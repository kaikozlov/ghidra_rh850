#!/usr/bin/env python3
"""Verify Bus-1 camera/radar output decode over retained drives + GTS+ scales."""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

from tools import REPO_ROOT
REPO = REPO_ROOT
ART = REPO / "data/generated/camry_2026_bus1_camera_output.json"
BUILD = REPO / "tools/targets/camry/analysis/analyze_camry_2026_bus1_camera_output.py"

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

gts = art["gts_vocabulary"]
check("independently anchored CAN distance LSB is 0.005 m", gts["joined_distance_scale"]["lsb_m"] == 0.005)

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
    check(f"{drive}: occupied slots observed", slots["occupied_slots"] > 1000)
    dist = slots["longitudinal_m_u16be_lsb_0_005"]
    check(
        f"{drive}: occupied range uses independently anchored 0.005 m LSB",
        dist["min"] >= 0.5 and dist["max"] < 327.64 and 5.0 <= dist["median"] <= 30.0,
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
    integrity = d["object_cycle_integrity"]
    check(f"{drive}: every radar frame has a valid P05 checksum", integrity["crc_invalid_frames"] == 0 and integrity["crc_valid_frames"] > 120000)
    check(f"{drive}: every wrap keeps a new cycle occurrence", integrity["chronological_cycle_occurrences"] > 10000)
    joined = d["joined_object_family_0x180_0x18B"]
    check(f"{drive}: three banks join four 7-byte records per object", joined["bank_layout"] == {
        "bank0": ["0x180", "0x183", "0x186", "0x189"],
        "bank1": ["0x181", "0x184", "0x187", "0x18A"],
        "bank2": ["0x182", "0x185", "0x188", "0x18B"],
        "object_slots_per_bank": 8,
        "record_bytes_per_object": 28,
    })
    check(f"{drive}: thousands of complete synchronized object bursts", joined["complete_bursts"] > 30000)
    check(f"{drive}: recovered lateral field is signed12 * 0.04 m, left-positive", joined["wire_fields"]["record0_lateral"] == "B2:B3[7:4] signed12be * 0.04 m, left-positive")
    check(f"{drive}: recovered relative-speed field is signed14 * 0.025 m/s", joined["wire_fields"]["record1_relative_speed"] == "B1[5:0]||B2[7:0] signed14be * 0.025 m/s")
    kin = joined["kinematic_validation"]
    check(f"{drive}: >90k continuity-filtered relative-speed witnesses", kin["n"] > 90000, str(kin))
    check(f"{drive}: encoded relative speed tracks d(range)/dt at r>0.85", kin["pearson_r"] > 0.85, str(kin))
    check(f"{drive}: relative-speed fitted slope is ~1", 0.97 <= kin["fit_range_rate_from_encoded_vrel"]["slope"] <= 1.03, str(kin))
    check(f"{drive}: relative-speed fitted intercept is near zero", abs(kin["fit_range_rate_from_encoded_vrel"]["intercept_m_s"]) < 0.15, str(kin))
    check(f"{drive}: relative-speed median absolute kinematic error <1.3 m/s", kin["median_abs_error_m_s"] < 1.3, str(kin))
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

print(f"\nResults: {passed} passed, {failed} failed")
raise SystemExit(1 if failed else 0)
