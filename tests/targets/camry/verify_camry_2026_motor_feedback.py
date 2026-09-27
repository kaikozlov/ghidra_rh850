#!/usr/bin/env python3
"""Tracked 2026 Camry 0x030 B22:B23 motor-feedback two-drive correlation.

Domain split; assertions and helpers are carried over verbatim.
"""
from __future__ import annotations


from tools import REPO_ROOT
ROOT = REPO = REPO_ROOT

passed = failed = 0


def check(name, cond, detail=""):
    global passed, failed
    ok = bool(cond)
    passed += int(ok)
    failed += int(not ok)
    suffix = f" ({detail})" if detail else ""
    print(f"[{'PASS' if ok else 'FAIL'}] {name}{suffix}")
print()

print("== camry 2026 0x030 B22:B23 motor-feedback two-drive correlation ==")
def _section_camry_2026_motor_feedback():
    import hashlib
    import json
    import subprocess
    import sys
    import tempfile
    from pathlib import Path

    ART = REPO / "data/generated/camry_2026_motor_feedback_correlation.json"
    TOOL = REPO / "tools/targets/camry/analysis/analyze_camry_2026_motor_feedback.py"
    PORT = REPO / "data/generated/camry_8965F3307000_tss3_opendbc_port.json"

    def sha(path):
        return hashlib.sha256(Path(path).read_bytes()).hexdigest()

    art = json.loads(ART.read_text())
    port = json.loads(PORT.read_text())

    check("sources pinned by sha256", art["sources"]["tss3_port"]["sha256"] == sha(PORT))
    check("decode binds exact-F33 B22:B23 mapping", port["status_carriers"]["0x030"]["mapped_motor_feedback"]["wire"] == "B22:B23")

    with tempfile.TemporaryDirectory(prefix="camry-mf-") as td:
        out = Path(td) / "mf.json"
        r = subprocess.run([sys.executable, str(TOOL), "--out", str(out)], cwd=REPO, capture_output=True, text=True)
        check("analyzer exits cleanly (Class-L and cruise census assertions hold)", r.returncode == 0)
        check("analyzer reproduces artifact byte-exact", out.exists() and out.read_bytes() == ART.read_bytes())

    a, b = art["drives"]["drive_a"], art["drives"]["drive_b"]
    check("B6 remains absent on all buses in both drives",
          art["combined"]["b6_observed_any"] is False and
          a["b6"]["total_all_buses"] == 0 and b["b6"]["total_all_buses"] == 0)
    check("Class-L strata populated", a["class_l"]["stats"]["n"] > 1000 and b["class_l"]["stats"]["n"] > 5000)
    check("speed-matched cruise control populated for drive B", b["control"]["n"] > 2500)

    core = b["hands_light_core"]
    check("drive B hands-light core floor is several-fold larger in Class-L",
          core["class_l"]["n"] > 4000 and core["control"]["n"] > 1000 and
          core["median_abs_current_floor_ratio"] >= 4 and
          core["rank_sum_z_class_l_larger"]["z"] >= 20 and
          core["rank_sum_z_class_l_larger"]["p_two_sided"] <= 1e-4)
    check("drive B core is smoother in Class-L", core["class_l"]["lag1_autocorr_abs_current"] > core["control"]["lag1_autocorr_abs_current"] > 0.4)
    check("control stratum is driver-proportional, Class-L is not (drive B)",
          art["combined"]["control_r_current_vs_torque"]["drive_b"] >= 0.7 and
          abs(art["combined"]["class_l_r_current_vs_torque"]["drive_b"]) <= 0.3)
    check("drive A control underpowered is recorded honestly",
          a["hands_light_core"]["control"]["n"] == 0 and art["combined"]["class_l_floor_ratios"]["drive_a"] is None)

    opp_a = a["opposing_driver_motion_runs"]["class_l"]
    opp_b = b["opposing_driver_motion_runs"]["class_l"]
    top = opp_a["top_runs"][0]
    check("drive A Class-L opposing runs reproduce (>=5 runs, longest >= 0.8 s)",
          opp_a["runs_ge_100ms"] >= 5 and opp_a["max_run_s"] >= 0.8 and opp_a["qualifying_samples"] >= 150)
    check("strongest drive A run opposes driver torque while steering moves",
          top["duration_s"] >= 0.9 and top["median_current"] < -400 and top["median_driver_torque_nm"] > 0.8 and
          top["median_rate_raw"] < -5 and top["median_speed_kph"] > 35)
    check("drive B Class-L opposing run reproduces (1 run >= 0.2 s)",
          opp_b["runs_ge_100ms"] == 1 and 0.2 <= opp_b["max_run_s"] <= 0.3 and opp_b["qualifying_samples"] >= 20)
    check("opposition control is weaker/absent outside Class-L",
          a["opposing_driver_motion_runs"]["control"]["max_run_s"] < 0.5 and
          b["opposing_driver_motion_runs"]["control"]["runs_ge_100ms"] == 0)

    sw = art["combined"]
    check("no sustained hands-light sweep inside Class-L",
          sw["class_l_hands_light_sweeps_ge_500ms"] == {"drive_a": 0, "drive_b": 0})
    check("speed-matched non-Class-L hands-light motion exists only there",
          a["hands_light_motion_sweeps"]["control_runs_ge_500ms"] >= 1 and
          b["hands_light_motion_sweeps"]["control_runs_ge_500ms"] == 0)
    rise_b = [e for e in b["class_l_edge_abs_current"]["edges"] if e["edge"] == "rise"][0]
    check("drive B Class-L rise shows no immediate current step",
          abs(rise_b["post_median_abs_current"] - rise_b["pre_median_abs_current"]) <= 30 and
          rise_b["pre_median_abs_current"] < 130 and rise_b["post_median_abs_current"] < 130)

_section_camry_2026_motor_feedback()
print()

print(f"\n== RESULT: {passed} passed, {failed} failed ==")
raise SystemExit(1 if failed else 0)
