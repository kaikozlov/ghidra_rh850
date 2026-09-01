#!/usr/bin/env python3
"""Verify the retained Camry request-coherent stock-steering witness."""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / "data/generated/camry_2026_stock_steering_witness.json"
TOOL = ROOT / "tools/analyze_camry_2026_stock_steering_witness.py"
D = json.loads(ART.read_text())
failures = []


def check(name, cond, detail=""):
    if cond:
        print(f"PASS {name}")
    else:
        print(f"FAIL {name}: {detail}")
        failures.append(name)


check("schema pinned", D["schema"] == "camry-2026-stock-steering-witness-v1")
a = D["drives"]["drive_a"]
b = D["drives"]["drive_b"]
check("B6 absent in both retained drives", a["b6_total_all_buses"] == b["b6_total_all_buses"] == 0)
check("drive A has five coherent opposing runs", a["runs_ge_100ms"] == 5 and a["max_run_s"] == 0.903264)
check("drive B reproduces one coherent opposing run", b["runs_ge_100ms"] == 1 and b["max_run_s"] == 0.223651)

top = a["top_runs"][0]
check("drive A top run starts 4.698966 s into ID11", top["start_from_id11_interval_s"] == 4.698966)
check("drive A top run carries 91 joined samples", top["sample_count"] == 91)
check("motor/motion point toward request throughout top run",
      top["motor_toward_target_fraction"] == 1.0 and top["motion_toward_target_fraction"] == 1.0)
check("driver torque opposes request throughout top run", top["driver_opposes_target_fraction"] == 1.0)
check("target error collapses across top run",
      top["target_error_first_deg"] == -8.971852 and top["target_error_last_deg"] == -0.417907
      and top["target_error_abs_reduction_deg"] == 8.553945)
check("wheel crosses toward negative Toyota target",
      top["angle_first_deg"] == 3.7 and top["angle_last_deg"] == -6.0
      and top["target_first_deg"] == -5.271852 and top["target_last_deg"] == -6.417907)
check("median motor opposes measured driver torque",
      top["median_motor_feedback"] == -447.0 and top["median_driver_torque_nm"] == 0.91)

btop = b["top_runs"][0]
check("opposite-sign drive B witness reproduces directionality",
      btop["median_motor_feedback"] == 333.0 and btop["median_driver_torque_nm"] == -0.73
      and btop["motor_toward_target_fraction"] == btop["driver_opposes_target_fraction"] == 1.0)

with tempfile.TemporaryDirectory() as td:
    regen = Path(td) / "witness.json"
    subprocess.run([sys.executable, str(TOOL), "--out", str(regen)], cwd=ROOT, check=True,
                   stdout=subprocess.DEVNULL)
    check("artifact regenerates byte-identically", regen.read_bytes() == ART.read_bytes())

if failures:
    raise SystemExit(f"{len(failures)} failed checks: {', '.join(failures)}")
print("all checks passed")
