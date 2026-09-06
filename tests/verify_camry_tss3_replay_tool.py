#!/usr/bin/env python3
"""Portable checks for the WP2 recorded-vs-proposed CarState replay tool."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.replay_camry_tss3_carstate_revisions import fixture_provenance, summarize

passed = failed = 0


def check(name: str, condition: bool) -> None:
    global passed, failed
    passed += int(condition)
    failed += int(not condition)
    print(f"[{'PASS' if condition else 'FAIL'}] {name}")


f3c = ROOT / "tests/fixtures/camry_20260904/3c-seg43.jsonl"
f3d = ROOT / "tests/fixtures/camry_20260904/3d-seg1-torque.jsonl"
p3c = fixture_provenance(f3c)
p3d = fixture_provenance(f3d)
check("3c replay fixture source pinned", p3c["source_sha256"] == "ab6b4fbe4d14227919a022dbc2c3091467446262d6896d26ea021ecc5d54c356")
check("3d torque replay fixture source pinned", p3d["source_sha256"] == "1437f8c6214274348c0be61e453d9c00626da43135b4872a0a1f76b74e54ddc3")
check("3d torque replay window pinned", p3d["window_s"] == [4.0, 14.0])

recorded = [
    {"t": 1, "steeringTorque": 0.4, "steeringPressed": False, "vehicleSensorsInvalid": False, "steeringAngleDeg": 2.0},
    {"t": 2, "steeringTorque": 1.3, "steeringPressed": False, "vehicleSensorsInvalid": False, "steeringAngleDeg": 2.1},
]
proposed = [
    {"t": 1, "steeringTorque": 0.4, "steeringPressed": False, "vehicleSensorsInvalid": False, "steeringAngleDeg": 2.0},
    {"t": 2, "steeringTorque": 1.3, "steeringPressed": True, "vehicleSensorsInvalid": False, "steeringAngleDeg": 2.1},
]
summary, rows = summarize(recorded, proposed, f3c)
check("replay keeps identical decode separate from driver semantic delta", summary["decode_equal_when_proposed_measurement_valid"] is True)
check("replay counts pressed transition", summary["steeringPressed_true_recorded"] == 0 and summary["steeringPressed_true_proposed"] == 1)
check("replay emits one diff row per timestamp", len(rows) == 2 and [r["t"] for r in rows] == [1, 2])

try:
    summarize(recorded, proposed[:1], f3c)
except RuntimeError:
    check("replay rejects length mismatch", True)
else:
    check("replay rejects length mismatch", False)

bad_time = [dict(proposed[0]), dict(proposed[1])]
bad_time[1]["t"] = 3
try:
    summarize(recorded, bad_time, f3c)
except RuntimeError:
    check("replay rejects timestamp mismatch", True)
else:
    check("replay rejects timestamp mismatch", False)

print(f"\n{passed} passed, {failed} failed")
raise SystemExit(1 if failed else 0)
