#!/usr/bin/env python3
"""Verify exact-F33 incident branch and recovery-epilogue byte geometry."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools.targets.camry.analysis import analyze_f33_recovery_structure as recovery

passed = failed = 0


def check(name: str, condition: object) -> None:
    global passed, failed
    ok = bool(condition)
    passed += int(ok)
    failed += int(not ok)
    print(f"[{'PASS' if ok else 'FAIL'}] {name}")


image = recovery.IMAGE.read_bytes()
report = recovery.analyze(image)
incident = report["incident"]
geometry = incident["clear_bits_encoding_geometry"]

check("exact stock image identity", report["source"]["sha256"] == recovery.IMAGE_SHA256)
check(
    "recorded malformed JARL32 stream is exact",
    incident["instruction_with_stock_successor"] == "ff02925b2436",
)
check("malformed target is reconstructed", incident["decoded_bad_target"] == "0x362BFE04")
check(
    "candidate clears bits only",
    geometry["candidate_instruction"] == "ff0212010000"
    and geometry["cleared_bit_mask"] == "0000805a2436",
)
check(
    "candidate reaches matching one-LP epilogue",
    geometry["candidate_target"] == "0x0007A384"
    and geometry["candidate_target_bytes"] == "40063f00"
    and geometry["matching_entry_prologue"]["bytes"] == "80072100",
)
check("displacement-subset census is exact", geometry["subset_displacement_count"] == 16384)
check("no clear-bits displacement reaches resident signer", geometry["resident_subset_targets"] == [])

# Boot/reset/safety outputs relevant to post-incident recovery.
clear = report["boot_cold_flash_error_clear"]
check(
    "cold startup clears CodeFlash ECC status before validity",
    clear["address"] == "0x00000802"
    and clear["bytes"].startswith("3e060420c6ff0f0a010d010a030d"),
)
retained = report["boot_retained_reset_record"]
check(
    "retained reset record is read before ordinary validity call",
    retained["reader_call"]["target"] == "0x00000E54"
    and retained["validity_call_after_reader"]["target"] == "0x0000119E"
    and int(retained["reader_call"]["address"], 16) < int(retained["validity_call_after_reader"]["address"], 16),
)
errout = report["application_errorout_mask_init"]
check(
    "application programs bounded ECM ERROROUT masks",
    errout["startup_call"]["target"] == "0x00063338"
    and errout["ecmemk0"]["value"] == "0xFFFFFFE1"
    and errout["ecmemk1"]["value"] == "0xFFFFFFFF"
    and errout["ecmemk2"]["value"] == "0x3FFFFFFF",
)

print(f"Results: {passed} passed, {failed} failed")
raise SystemExit(1 if failed else 0)
