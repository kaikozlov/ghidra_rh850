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
OPENPILOT_COMMIT = "ddc6e532ecb8640d5771234b0017d84839e28ae2"
OPENDBC_COMMIT = "fa1847d7ee66a221f2960ec5cf7a840e737ca521"
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
        capture_output=True, text=True, check=False,
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

    from opendbc.can import CANParser
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
    eps_parser = CANParser("toyota_tss3_pt_generated", [("TSS3_EPS_TELEMETRY", float("nan"))], 1)
    eps_fields = eps_parser.vl["TSS3_EPS_TELEMETRY"]
    ready_parser = CANParser("toyota_tss3_pt_generated", [("TSS3_READY_STATUS", float("nan"))], 1)

    cc = structs.CarControl()
    cc.enabled = True
    cc.latActive = True
    cc.longActive = True
    cc.actuators.torque = 1.0
    cc.actuators.steeringAngleDeg = 500.0
    cc.actuators.accel = 2.0
    _, can_sends = ci.apply(cc.as_reader(), 1_000_000_000)

    values = []
    ready_values = []
    for ev in LogReader(rlog, sort_by_time=True):
      if ev.which() != 'can':
        continue
      can = [CanData(int(c.address), bytes(c.dat), int(c.src)) for c in ev.can]
      t = int(ev.logMonoTime)
      ready_parser.update([(t, can)])
      if any(int(c.address) == 0x51E and int(c.src) == 1 for c in ev.can):
        ready_values.append(int(ready_parser.vl["TSS3_READY_STATUS"]["READY_STATUS"]))
      values.append(ci.update([(t, can)]))

    post = values[100:]
    fp = FINGERPRINTS[CAR.TOYOTA_COROLLA_TSS3][0]
    out = {
      'tss3': bool(cp1.flags & ToyotaFlags.TSS3),
      'secoc': bool(cp1.flags & ToyotaFlags.SECOC),
      'not_tss2': not bool(cp1.flags & ToyotaFlags.TSS2),
      'bus1_detected': bool(cp1.flags & ToyotaFlags.TSS3_PT_BUS1),
      'bus0_default': not bool(cp0.flags & ToyotaFlags.TSS3_PT_BUS1),
      'dbc': DBC[CAR.TOYOTA_COROLLA_TSS3][Bus.pt],
      'bounded_steering_status_name': 'STEERING_FAULT_INHIBIT_STATUS' in eps_fields and 'EPS_FAULT_INHIBIT' not in eps_fields,
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
      'ready_sample_count': len(ready_values),
      'ready_values': sorted(set(ready_values)),
      'min_driver_torque_nm': min(float(x.steeringTorque) for x in post),
      'max_driver_torque_nm': max(float(x.steeringTorque) for x in post),
      'driver_torque_unique_2dp': len(set(round(float(x.steeringTorque), 2) for x in post)),
      'steering_pressed_values': sorted(set(bool(x.steeringPressed) for x in post)),
      'steer_fault_temporary_values': sorted(set(bool(x.steerFaultTemporary) for x in post)),
      'steer_fault_permanent_values': sorted(set(bool(x.steerFaultPermanent) for x in post)),
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
    check=False,
)
check("read-only platform/rlog probe succeeds", proc.returncode == 0, proc.stderr.strip()[:240])
if proc.returncode == 0:
    # CANParser can emit a startup timeout diagnostic before the final JSON line.
    lines = [line for line in proc.stdout.splitlines() if line.strip()]
    result = json.loads(lines[-1])
    check("TSS3 and SecOC remain orthogonal flags", result["tss3"] and result["secoc"] and result["not_tss2"])
    check("observed bus1 and relay-correct bus0 parser modes are distinct", result["bus1_detected"] and result["bus0_default"])
    check("dedicated TSS3 DBC is selected", result["dbc"] == "toyota_tss3_pt_generated")
    check("steering status field name preserves the bounded semantics", result["bounded_steering_status_name"])
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
    check("read-only parser retains only the raw3-to-prior-art-drive decode", result["gear_values"] == ["drive"])
    check("cruise remains neutral without an engaged transition", result["cruise_enabled_values"] == [False])
    check("0x51E Ready Status is observable through the maintained DBC", result["ready_sample_count"] == 60 and result["ready_values"] == [1])
    check(
        "live physical driver torque is promoted from 0x030",
        result["min_driver_torque_nm"] < -8.0 and result["max_driver_torque_nm"] > 2.8
        and result["driver_torque_unique_2dp"] == 482,
        f"range={result['min_driver_torque_nm']:.2f}..{result['max_driver_torque_nm']:.2f} Nm unique={result['driver_torque_unique_2dp']}",
    )
    check("unvalidated driver override threshold remains disabled", result["steering_pressed_values"] == [False])
    check(
        "temporary/permanent steering fault classes remain deliberately neutral",
        result["steer_fault_temporary_values"] == [False] and result["steer_fault_permanent_values"] == [False],
    )

print(f"\n== RESULT: {passed} passed, {failed} failed ==")
raise SystemExit(1 if failed else 0)
