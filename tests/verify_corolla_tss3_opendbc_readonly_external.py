#!/usr/bin/env python3
"""Verify the sibling kai-openpilot/opendbc read-only Corolla TSS3 checkpoint.

This local/external gate intentionally checks the implementation against the tracked
Span rlog without treating that vehicle-level capture as an exact F181 firmware join.
"""
from __future__ import annotations

import json
import os
import subprocess
import textwrap
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
OPENPILOT = (REPO / "../kai-openpilot").resolve()
OPENPILOT_PYTHON = OPENPILOT / ".venv/bin/python"
OPENPILOT_COMMIT = "bb786e2c29f1ad433b1e3d08c0129a0f769a6d91"
OPENDBC_COMMIT = "200dfa78bbda4228f5e9bb1f7281659f5b6df8a6"
RLOG = REPO / "community/spanconstant/span_67fd5b833889fedf_00000010--17084916da--3--rlog.zst"

passed = failed = 0


def check(name: str, condition: object, detail: str = "") -> None:
    global passed, failed
    ok = bool(condition)
    passed += int(ok)
    failed += int(not ok)
    suffix = f" ({detail})" if detail else ""
    print(f"[{'PASS' if ok else 'FAIL'}][independent_external_artifact] {name}{suffix}")


def is_ancestor(repo: Path, commit: str) -> bool:
    proc = subprocess.run(
        ["git", "-C", str(repo), "merge-base", "--is-ancestor", commit, "HEAD"],
        capture_output=True, text=True,
    )
    return proc.returncode == 0


if not OPENPILOT_PYTHON.is_file() or not RLOG.is_file() or not (OPENPILOT / ".git").exists():
    print(
        "[SKIP] sibling kai-openpilot/runtime evidence unavailable: "
        f"openpilot={OPENPILOT.exists()} python={OPENPILOT_PYTHON.is_file()} rlog={RLOG.is_file()}"
    )
    raise SystemExit(77)

OPENDBC = OPENPILOT / "opendbc_repo"
check("kai-openpilot contains the read-only integration commit", is_ancestor(OPENPILOT, OPENPILOT_COMMIT))
check("checked-out opendbc contains the TSS3 implementation commit", is_ancestor(OPENDBC, OPENDBC_COMMIT))

probe = textwrap.dedent(
    """
    import json
    import sys

    from opendbc.car import Bus, CanData, structs
    from opendbc.car.toyota.fingerprints import FINGERPRINTS
    from opendbc.car.toyota.interface import CarInterface
    from opendbc.car.toyota.values import CAR, DBC, ToyotaFlags
    from openpilot.tools.lib.logreader import LogReader

    rlog = sys.argv[1]

    def fingerprint_on(bus):
      fp = {i: {} for i in range(8)}
      fp[bus] = {0x025: 32, 0x0AA: 8}
      return fp

    cp1 = CarInterface.get_params(CAR.TOYOTA_COROLLA_TSS3, fingerprint_on(1), [], False, False, False)
    cp0 = CarInterface.get_params(CAR.TOYOTA_COROLLA_TSS3, fingerprint_on(0), [], False, False, False)
    ci = CarInterface(cp1)

    cc = structs.CarControl()
    cc.enabled = True
    cc.latActive = True
    cc.longActive = True
    cc.actuators.torque = 1.0
    cc.actuators.steeringAngleDeg = 500.0
    cc.actuators.accel = 2.0
    _, can_sends = ci.apply(cc.as_reader(), 1_000_000_000)

    values = []
    for ev in LogReader(rlog, sort_by_time=True):
      if ev.which() != 'can':
        continue
      can = [CanData(int(c.address), bytes(c.dat), int(c.src)) for c in ev.can]
      values.append(ci.update([(int(ev.logMonoTime), can)]))

    post = values[100:]
    fp = FINGERPRINTS[CAR.TOYOTA_COROLLA_TSS3][0]
    out = {
      'tss3': bool(cp1.flags & ToyotaFlags.TSS3),
      'secoc': bool(cp1.flags & ToyotaFlags.SECOC),
      'not_tss2': not bool(cp1.flags & ToyotaFlags.TSS2),
      'bus1_detected': bool(cp1.flags & ToyotaFlags.TSS3_PT_BUS1),
      'bus0_default': not bool(cp0.flags & ToyotaFlags.TSS3_PT_BUS1),
      'dbc': DBC[CAR.TOYOTA_COROLLA_TSS3][Bus.pt],
      'dashcam_only': bool(cp1.dashcamOnly),
      'no_output': cp1.safetyConfigs[0].safetyModel == structs.CarParams.SafetyModel.noOutput,
      'radar_unavailable': bool(cp1.radarUnavailable),
      'longitudinal_disabled': not bool(cp1.openpilotLongitudinalControl),
      'controller_send_count': len(can_sends),
      'fingerprint_count': len(fp),
      'fingerprint_shapes': {hex(k): fp[k] for k in (0x025, 0x0AA, 0x0D7)},
      'samples': len(values),
      'post_samples': len(post),
      'post_can_valid': sum(bool(x.canValid) for x in post),
      'max_speed_mps': max(float(x.vEgoRaw) for x in post),
      'min_angle_deg': min(float(x.steeringAngleDeg) for x in post),
      'max_angle_deg': max(float(x.steeringAngleDeg) for x in post),
      'min_rate_deg_s': min(float(x.steeringRateDeg) for x in post),
      'max_rate_deg_s': max(float(x.steeringRateDeg) for x in post),
      'brake_values': sorted(set(bool(x.brakePressed) for x in post)),
      'gas_values': sorted(set(bool(x.gasPressed) for x in post)),
      'gear_values': sorted(set(str(x.gearShifter) for x in post)),
      'cruise_enabled_values': sorted(set(bool(x.cruiseState.enabled) for x in post)),
    }
    print(json.dumps(out, sort_keys=True))
    """
)
env = os.environ.copy()
env["PYTHONPATH"] = os.pathsep.join([str(OPENPILOT / "opendbc_repo"), str(OPENPILOT)])
env["PWD"] = str(OPENPILOT)
proc = subprocess.run(
    [str(OPENPILOT_PYTHON), "-c", probe, str(RLOG)],
    cwd=OPENPILOT,
    env=env,
    capture_output=True,
    text=True,
    timeout=180,
)
check("read-only platform/rlog probe succeeds", proc.returncode == 0, proc.stderr.strip()[:240])
if proc.returncode == 0:
    # CANParser can emit a startup timeout diagnostic before the final JSON line.
    lines = [line for line in proc.stdout.splitlines() if line.strip()]
    result = json.loads(lines[-1])
    check("TSS3 and SecOC remain orthogonal flags", result["tss3"] and result["secoc"] and result["not_tss2"])
    check("observed bus1 and relay-correct bus0 parser modes are distinct", result["bus1_detected"] and result["bus0_default"])
    check("dedicated TSS3 DBC is selected", result["dbc"] == "toyota_tss3_pt_generated")
    check(
        "platform is passive at both CarParams and controller boundaries",
        result["dashcam_only"] and result["no_output"] and result["radar_unavailable"]
        and result["longitudinal_disabled"] and result["controller_send_count"] == 0,
    )
    check(
        "Span topology fingerprint is the tracked 147-message shape",
        result["fingerprint_count"] == 147
        and result["fingerprint_shapes"] == {"0x25": 32, "0xaa": 8, "0xd7": 32},
    )
    check("full Span rlog has 6000 CAN samples", result["samples"] == 6000)
    check("all 5900 post-startup samples are CAN-valid", result["post_samples"] == 5900 and result["post_can_valid"] == 5900)
    check("replayed speed reaches moving range", result["max_speed_mps"] > 6.0, f"max={result['max_speed_mps']:.3f} m/s")
    check("replayed steering range matches dynamic evidence", result["min_angle_deg"] < -500 and result["max_angle_deg"] > 100)
    check("replayed steering-rate range matches dynamic evidence", result["min_rate_deg_s"] <= -700 and result["max_rate_deg_s"] >= 800)
    check("brake and gas both transition", result["brake_values"] == [False, True] and result["gas_values"] == [False, True])
    check("only dynamically proven D gear is promoted", result["gear_values"] == ["drive"])
    check("cruise remains neutral without an engaged transition", result["cruise_enabled_values"] == [False])

print(f"\n== RESULT: {passed} passed, {failed} failed ==")
raise SystemExit(1 if failed else 0)
