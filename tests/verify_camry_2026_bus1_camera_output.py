#!/usr/bin/env python3
"""Verify Bus-1 camera/radar output decode over retained drives + GTS+ scales."""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
ART = REPO / "data/generated/camry_2026_bus1_camera_output.json"
BUILD = REPO / "tools/analyze_camry_2026_bus1_camera_output.py"

passed = failed = 0


def check(name, condition, detail=""):
    global passed, failed
    ok = bool(condition)
    passed += int(ok)
    failed += int(not ok)
    print(f"[{'PASS' if ok else 'FAIL'}] {name}" + (f" ({detail})" if detail else ""))


art = json.loads(ART.read_text())

print("== deterministic regeneration ==")
with tempfile.TemporaryDirectory() as td:
    out = Path(td) / ART.name
    proc = subprocess.run(
        [sys.executable, str(BUILD), "--out", str(out)],
        cwd=REPO,
        capture_output=True,
        text=True,
        check=False,
    )
    check("offline analyzer succeeds", proc.returncode == 0, proc.stderr[-400:])
    check(
        "artifact regenerates byte-identically",
        proc.returncode == 0 and out.read_bytes() == ART.read_bytes(),
    )

check("schema is v2", art["schema"] == "camry-2026-bus1-camera-output-v2")
gts = art["gts_vocabulary"]
names = {row["name"] for row in gts["frc_p5_geometry_dids"]}
check("FRC 0x190A Forward Vehicle Distance is in vocabulary", "Forward Vehicle Distance" in names)
check("FRC 0x1804 Control Target Vehicle Distance is in vocabulary", "Control Target Vehicle Distance (DDR)" in names)
check("FFD 5A22 is unsigned 0.01 m", any(
    f["lsb"] == "0.01" and f["type"] == "u"
    for f in gts["operation_ffd_object_layouts"]["5A22"]["fields"]
))
check("joined distance LSB is 0.01 m", gts["joined_distance_scale"]["lsb_m"] == 0.01)

print("== both drives ==")
for drive in ("drive_a", "drive_b"):
    d = art["drives"][drive]
    check(f"{drive}: zero 0x00F on bus 1", d["0x00F_count"] == 0)
    ids = {(row["can_id"], row["dlc"]) for row in d["periodic_streams"]}
    check(f"{drive}: 22 periodic streams", len(d["periodic_streams"]) == 22)
    check(f"{drive}: 0x180/64 present", ("0x180", 64) in ids)
    check(f"{drive}: 0x18C/48 present", ("0x18C", 48) in ids)
    check(f"{drive}: 0x160/32 present", ("0x160", 32) in ids)
    check(f"{drive}: 0x180 last-4 is constant", d["0x180_unique_last4"] == 1)
    slots = d["object_slots_0x180_0x182"]
    check(f"{drive}: empty sentinel is 7-byte FFF8/FFFF", slots["empty_sentinel"] == "fff8000000ffff")
    check(f"{drive}: eight 7-byte slots", slots["slots_per_pdu"] == 8 and slots["slot_bytes"] == 7)
    check(f"{drive}: empty slots observed", slots["empty_slots"] > 0)
    check(f"{drive}: occupied slots observed", slots["occupied_slots"] > 1000)
    dist = slots["longitudinal_m_u16be_lsb_0_01"]
    check(
        f"{drive}: occupied range is metres-to-hundreds at 0.01 m LSB",
        dist["min"] >= 1.0 and dist["max"] <= 500.0 and 10.0 <= dist["median"] <= 60.0,
        str(dist),
    )
    check(
        f"{drive}: >=99% occupied distances in (0, 500] m",
        slots["occupied_distance_in_range_frac"] >= 0.99,
        str(slots["occupied_distance_in_range_frac"]),
    )
    rel = slots["rejected_direct_ffd_5A26_relspeed_s16_0_05"]["span_m_s"]
    check(
        f"{drive}: 5A26 overlay is physically impossible",
        abs(rel["max"]) > 100 or abs(rel["min"]) > 100,
        str(rel),
    )
    req = d["request_object_on_bus1"]
    check(f"{drive}: sampled ID11 |pinion|>=20", req["sampled"] >= 50, str(req["sampled"]))
    check(
        f"{drive}: 5282 ID||pinion||assist absent in ±25ms",
        req["layout_hits_in_window"] == 0,
        str(req["layout_hits_in_window"]),
    )
    check(
        f"{drive}: 5282 layout absent on all of Bus 1",
        req["layout_hits_global_bus1"] == 0,
        str(req["layout_hits_global_bus1"]),
    )

cl = art["classification"]
check("not a 1:1 0x08A copy", "absent" in cl["not_08A"])
check("middle hop: 5282 not on native Bus 1", "absent from sniffed Bus-1" in cl["middle_hop"])
check("0x160 standing SAS echo is explicitly rejected", "rejects the former standing" in cl["0x160"] and "CORR-138" in cl["0x160"])
check("old 8-byte radar DBC does not transfer", "does not transfer" in cl["not_tss2_8byte_radar_dbc"])
check("slot bytes 2-6 remain unmapped", "bytes 2-6" in cl["remainder"])

print(f"\nResults: {passed} passed, {failed} failed")
raise SystemExit(1 if failed else 0)
