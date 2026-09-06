#!/usr/bin/env python3
"""Replay identical Camry TSS3 CAN fixtures through two opendbc revisions.

Work package 2 companion for REFERENCE/CAMRY_OPENPILOT_COMPLETION_PLAN.md.
The recorded September revision and a caller-selected proposed revision receive
exactly the same source-derived CAN rows. The output separates stable decoded
CarState fields from the intentionally changed driver-interaction semantics.

This is an offline review tool. It does not transmit CAN or touch a vehicle.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import tempfile
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[1]
DEFAULT_OPENPILOT = Path("/Users/kai/dev/inspect/repos/kai-openpilot")
RECORDED_REVISION = "c7a62eaf"
DEFAULT_FIXTURES = (
    REPO / "tests/fixtures/camry_20260904/3c-seg43.jsonl",
    REPO / "tests/fixtures/camry_20260904/3d-seg1-torque.jsonl",
)

# Keep this child self-contained so each subprocess imports the requested
# opendbc worktree rather than whichever revision happens to be on sys.path.
CHILD = r'''
import json, sys
from pathlib import Path
sys.path.insert(0, sys.argv[1])
from opendbc.car import CanData
from opendbc.car.toyota.interface import CarInterface
from opendbc.car.toyota.values import CAR

fingerprint = {i: {} for i in range(8)}
fingerprint[0] = {0x025: 32, 0x0AA: 8, 0x3F6: 8}
CP = CarInterface.get_params(CAR.TOYOTA_CAMRY_TSS3, fingerprint, [], False, False, False)
ci = CarInterface(CP)
replay_ids = {0x025, 0x0AA, 0x030, 0x08A, 0x251, 0x101, 0x116, 0x51E, 0x00F, 0x0FE, 0x127}
rows = []
for line in Path(sys.argv[2]).read_text().splitlines():
  if not line.strip():
    continue
  rec = json.loads(line)
  if rec.get("type") != "can" or int(rec.get("src", 999)) > 3:
    continue
  addr = int(rec["addr"])
  if addr not in replay_ids:
    continue
  bus = 2 if addr in (0x08A, 0x251) else 0
  cs = ci.update([(int(rec["t"]), [CanData(addr, bytes.fromhex(rec["dat"]), bus)])])
  if cs is not None and addr == 0x030:
    rows.append({
      "t": int(rec["t"]),
      "steeringTorque": cs.steeringTorque,
      "steeringPressed": cs.steeringPressed,
      "vehicleSensorsInvalid": cs.vehicleSensorsInvalid,
      "steeringAngleDeg": cs.steeringAngleDeg,
    })
print(json.dumps(rows, separators=(",", ":")))
'''

# Execute the *actual current openpilot* DesireHelper rather than duplicating
# its transition rule in this repository. This proves the CarState semantic
# delta has the downstream consequence described in the WP2 audit while still
# keeping the physical Camry torque sign/threshold explicitly unvalidated.
DESIRE_CHILD = r'''
import json, sys
from types import SimpleNamespace
sys.path.insert(0, sys.argv[1])
from openpilot.cereal import log
from openpilot.selfdrive.controls.lib.desire_helper import DesireHelper

def cs(pressed, torque, left):
  return SimpleNamespace(vEgo=25.0, leftBlinker=left, rightBlinker=False,
                         steeringPressed=pressed, steeringTorque=torque,
                         leftBlindspot=False, rightBlindspot=False)

def run(pressed):
  d = DesireHelper()
  d.update(cs(pressed, 2.0, False), True, 1.0)
  d.update(cs(pressed, 2.0, True), True, 1.0)  # rising blinker -> preLaneChange
  before = d.lane_change_state == log.LaneChangeState.preLaneChange
  d.update(cs(pressed, 2.0, True), True, 1.0)
  return {
    "entered_pre_lane_change": before,
    "entered_lane_change_starting": d.lane_change_state == log.LaneChangeState.laneChangeStarting,
    "desire_lane_change_left": d.desire == log.Desire.laneChangeLeft,
  }

print(json.dumps({"pressed_false": run(False), "pressed_true": run(True)}, separators=(",", ":")))
'''


def git(root: Path, *args: str) -> str:
    return subprocess.check_output(["git", "-C", str(root), *args], text=True).strip()


def fixture_provenance(path: Path) -> dict[str, Any]:
    first = json.loads(path.read_text().splitlines()[0])
    if first.get("type") != "provenance":
        raise ValueError(f"{path}: first row is not provenance")
    return first


def run_child(python: Path, script: Path, opendbc_root: Path, fixture: Path) -> list[dict[str, Any]]:
    proc = subprocess.run(
        [str(python), str(script), str(opendbc_root), str(fixture)],
        capture_output=True, text=True, check=False, timeout=600,
    )
    if proc.returncode != 0:
        raise RuntimeError(f"replay failed for {opendbc_root}: {proc.stderr[-4000:]}")
    return json.loads(proc.stdout)


def run_desire_helper(python: Path, script: Path, openpilot_root: Path) -> dict[str, Any]:
    proc = subprocess.run(
        [str(python), str(script), str(openpilot_root)],
        capture_output=True, text=True, check=False, timeout=60,
    )
    if proc.returncode != 0:
        raise RuntimeError(f"DesireHelper check failed: {proc.stderr[-4000:]}")
    result = json.loads(proc.stdout)
    if (result["pressed_false"] != {
            "entered_pre_lane_change": True,
            "entered_lane_change_starting": False,
            "desire_lane_change_left": False,
        } or result["pressed_true"] != {
            "entered_pre_lane_change": True,
            "entered_lane_change_starting": True,
            "desire_lane_change_left": True,
        }):
        raise RuntimeError(f"unexpected current DesireHelper semantics: {result}")
    return result


def summarize(recorded: list[dict[str, Any]], proposed: list[dict[str, Any]], fixture: Path) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    if len(recorded) != len(proposed):
        raise RuntimeError(f"{fixture}: replay lengths differ: {len(recorded)} != {len(proposed)}")
    if [r["t"] for r in recorded] != [r["t"] for r in proposed]:
        raise RuntimeError(f"{fixture}: replay timestamps differ between revisions")

    diff_rows = []
    for a, b in zip(recorded, proposed):
        diff_rows.append({
            "t": a["t"],
            "torque_recorded": a["steeringTorque"],
            "torque_proposed": b["steeringTorque"],
            "angle_recorded": a["steeringAngleDeg"],
            "angle_proposed": b["steeringAngleDeg"],
            "pressed_recorded": a["steeringPressed"],
            "pressed_proposed": b["steeringPressed"],
            "invalid_recorded": a["vehicleSensorsInvalid"],
            "invalid_proposed": b["vehicleSensorsInvalid"],
        })

    valid_pairs = [(a, b) for a, b in zip(recorded, proposed) if not b["vehicleSensorsInvalid"]]
    decode_equal = all(
        abs(float(a["steeringTorque"]) - float(b["steeringTorque"])) < 1e-6
        and abs(float(a["steeringAngleDeg"]) - float(b["steeringAngleDeg"])) < 1e-6
        for a, b in valid_pairs
    )
    prov = fixture_provenance(fixture)
    summary = {
        "fixture": str(fixture.relative_to(REPO) if fixture.is_relative_to(REPO) else fixture),
        "source_route": prov["route"],
        "source_segment": prov["segment"],
        "source_sha256": prov["source_sha256"],
        "window_s": prov["window_s"],
        "frames_compared": len(diff_rows),
        "steeringPressed_true_recorded": sum(bool(r["pressed_recorded"]) for r in diff_rows),
        "steeringPressed_true_proposed": sum(bool(r["pressed_proposed"]) for r in diff_rows),
        "vehicleSensorsInvalid_true_recorded": sum(bool(r["invalid_recorded"]) for r in diff_rows),
        "vehicleSensorsInvalid_true_proposed": sum(bool(r["invalid_proposed"]) for r in diff_rows),
        "decode_equal_when_proposed_measurement_valid": decode_equal,
        "semantic_delta": (
            "The recorded revision hardcodes steeringPressed=False. The proposed revision derives "
            "the ordinary upstream driver-interaction state from physical torque at the provisional "
            "TSS3 threshold and propagates DRIVER_TORQUE_INVALID; sign/threshold remain physical-"
            "validation items, not replay-established facts."
        ),
    }
    return summary, diff_rows


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--openpilot-root", type=Path, default=DEFAULT_OPENPILOT)
    ap.add_argument("--recorded-revision", default=RECORDED_REVISION)
    ap.add_argument("--proposed-revision", help="expected proposed opendbc HEAD; defaults to current HEAD")
    ap.add_argument("--python", type=Path, help="Python with opendbc runtime dependencies")
    ap.add_argument("--fixture", action="append", type=Path, dest="fixtures")
    ap.add_argument("--out-root", type=Path, default=REPO / "build/out/camry-replay-audit-20260905")
    args = ap.parse_args()

    opendbc = args.openpilot_root / "opendbc_repo"
    python = args.python or (opendbc / ".venv/bin/python")
    proposed_revision = git(opendbc, "rev-parse", "HEAD")
    if args.proposed_revision and not proposed_revision.startswith(args.proposed_revision):
        raise SystemExit(f"proposed revision mismatch: expected {args.proposed_revision}, got {proposed_revision}")
    recorded_revision = git(opendbc, "rev-parse", args.recorded_revision)
    fixtures = [p.resolve() for p in (args.fixtures or DEFAULT_FIXTURES)]
    for fixture in fixtures:
        if not fixture.is_file():
            raise SystemExit(f"missing fixture: {fixture}")

    args.out_root.mkdir(parents=True, exist_ok=True)
    child = args.out_root / "_replay_carstate_child.py"
    child.write_text(CHILD)
    desire_child = args.out_root / "_replay_desire_helper_child.py"
    desire_child.write_text(DESIRE_CHILD)
    desire_semantics = run_desire_helper(python, desire_child, args.openpilot_root)

    with tempfile.TemporaryDirectory(prefix="camry-opendbc-replay-") as td:
        recorded_root = Path(td) / "recorded"
        subprocess.run(
            ["git", "-C", str(opendbc), "worktree", "add", "--detach", str(recorded_root), recorded_revision],
            check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
        )
        try:
            summaries: dict[str, Any] = {}
            for fixture in fixtures:
                rec = run_child(python, child, recorded_root, fixture)
                prop = run_child(python, child, opendbc, fixture)
                summary, diff_rows = summarize(rec, prop, fixture)
                summaries[fixture.stem] = summary
                (args.out_root / f"replay_carstate_diff_{fixture.stem}.json").write_text(
                    json.dumps(diff_rows, indent=2, sort_keys=True) + "\n")
            output = {
                "schema": "camry-tss3-carstate-revision-replay-v2",
                "recorded_revision": recorded_revision,
                "proposed_revision": proposed_revision,
                "upstream_desire_helper": desire_semantics,
                "fixtures": summaries,
            }
            (args.out_root / "replay_summary.json").write_text(json.dumps(output, indent=2, sort_keys=True) + "\n")
            print(json.dumps(output, indent=2, sort_keys=True))
        finally:
            subprocess.run(["git", "-C", str(opendbc), "worktree", "remove", "--force", str(recorded_root)],
                           check=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
