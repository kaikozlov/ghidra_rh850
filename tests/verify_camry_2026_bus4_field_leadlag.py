#!/usr/bin/env python3
"""Verify the exhaustive relay-correct Toyota-Bus-4 field lead/lag census.

The normal edit-loop pins the raw capture digests and the substantive
cross-drive negative. ``--regenerate`` opts into the ~6-minute byte-exact full replay.
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
RAW = REPO / "targets/camry-2026/raw-20260827"
ART = REPO / "data/generated/camry_2026_bus4_field_leadlag.json"
BUILD = REPO / "tools/targets/camry/analysis/analyze_camry_2026_bus4_field_leadlag.py"
REGENERATE = "--regenerate" in sys.argv[1:]
passed = failed = 0


def check(name: str, cond: object, detail: str = "") -> None:
    global passed, failed
    ok = bool(cond)
    passed += int(ok)
    failed += int(not ok)
    suffix = f" ({detail})" if detail else ""
    print(f"[{'PASS' if ok else 'FAIL'}] {name}{suffix}")


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


DRIVES = {
    "drive_a": (RAW / "camry_relay_route_can_20260827.ndjson.gz",
                "be0c02946818fafc48b7d3e2be5d2fde31d796e057ab29d8bf59a879c7553db5"),
    "drive_b": (RAW / "camry_relay_lta_confirm_route_can_20260827.ndjson.gz",
                "641eee57eaffc579002708185178ea08c189155527354712dd43a1f0e309bb3a"),
}

art = json.loads(ART.read_text())

print("== provenance ==")
for i, label in enumerate(("drive_a", "drive_b")):
    path, digest = DRIVES[label]
    check(f"{label} raw capture hash pinned", sha(path) == digest)
    check(f"{label} artifact source digest matches raw", art["sources"]["drives"][i]["sha256"] == digest)

if REGENERATE:
    print("== explicit byte-exact regeneration ==")
    with tempfile.TemporaryDirectory() as td:
        out = Path(td) / "bus4.json"
        p = subprocess.run([sys.executable, str(BUILD), "--out", str(out)], cwd=REPO,
                           capture_output=True, text=True, check=False)
        check("analyzer exits clean", p.returncode == 0, p.stderr[-300:])
        check("artifact regenerates byte-exact", p.returncode == 0 and out.read_bytes() == ART.read_bytes())
else:
    print("== deterministic regeneration ==")
    print("[SKIP] expensive full replay; use --regenerate")

print("== denominators ==")
expected_drv = {
    "drive_a": (200, 5021, 2221, 0),
    "drive_b": (153, 5448, 1803, 190),
}
for label, (streams, kept, refined, control) in expected_drv.items():
    d = art["drives"][label]
    check(f"{label} stream/kept/refined denominator exact",
          d["candidate_totals"]["streams"] == streams
          and d["candidate_totals"]["kept"] == kept
          and len(d["refined_candidates"]) == refined)
    check(f"{label} local-control denominator exact", d["window"]["control_grid_points"] == control)

print("== substantive matched negative ==")
c = art["combined"]
check("930 fields refined in both drives", c["refined_in_both_drives"] == 930)
check("69 fields reproduce strongly vs motor", c["reproduced_strong_motor_fields"] == 69)
check("zero reproduced motor leads >=50 ms", c["reproduced_motor_leads_ge_50ms"] == [])
check("zero reproduced rate leads >=50 ms", c["reproduced_rate_leads_ge_50ms"] == [])
check("all reproduced angle leads are EPS Tx 0x030",
      len(c["reproduced_angle_leads_ge_50ms"]) == 10
      and all(x.startswith("0x030") for x in c["reproduced_angle_leads_ge_50ms"])
      and c["angle_leads_outside_eps_tx_0x030"] == [])
check("all 25-ms motor near-leads are EPS Tx 0x030",
      len(c["reproduced_motor_near_leads_25_to_49ms"]) == 4
      and all(x.startswith("0x030") for x in c["reproduced_motor_near_leads_25_to_49ms"]))

sel = c["selected_fields"]
check("0x030 motor proxy is identity at zero lag",
      sel["0x030[22]s16be"]["drive_a"]["motor_r"] == 0.999
      and sel["0x030[22]s16be"]["drive_a"]["motor_peak_lag_ms"] == 0
      and sel["0x030[22]s16be"]["drive_b"]["motor_r"] == 0.9994
      and sel["0x030[22]s16be"]["drive_b"]["motor_peak_lag_ms"] == 0)
check("0x030 torque-family byte positively leads measured steering angle",
      sel["0x030[8]s8"]["drive_a"]["angle_peak_lag_ms"] == 350
      and sel["0x030[8]s8"]["drive_b"]["angle_peak_lag_ms"] == 250
      and sel["0x030[8]s8"]["drive_a"]["torque_r"] == 0.9991
      and sel["0x030[8]s8"]["drive_b"]["torque_r"] == 0.9983)
check("0x081/0x08A angle echoes lag motor in both drives",
      all(sel[f][d]["motor_peak_lag_ms"] <= -200 for f in ("0x081[16]s16be","0x08A[18]s16be")
          for d in ("drive_a","drive_b")))
check("0x090 retained composite remains lagging in both drives",
      sel["0x090[12]w12"]["drive_a"]["motor_peak_lag_ms"] == -325
      and sel["0x090[12]w12"]["drive_b"]["motor_peak_lag_ms"] == -500)

print(f"\n{passed} passed, {failed} failed")
sys.exit(1 if failed else 0)
