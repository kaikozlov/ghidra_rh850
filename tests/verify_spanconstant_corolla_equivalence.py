#!/usr/bin/env python3
"""Verify the durable Span-vs-albino Corolla CodeFlash equivalence boundary."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
BASELINE = REPO / "community/albinoelephant/raw-20260818/albinoelephant-corolla-2023.20260814-0023/dump_codeflash_00000000_00200000_20260814-025814.bin"
TARGET = REPO / "community/spanconstant/raw-20260821/span-corolla-2025.20260821-1511/dump_codeflash_00000000_00200000_20260821-152033.bin"
ARTIFACT = REPO / "data/generated/corolla_8965F1208000_vs_8965H1202000_codeflash_equivalence.json"
TOOL = REPO / "tools/analyze_corolla_codeflash_equivalence.py"


def check(label: str, ok: bool) -> None:
    if not ok:
        raise AssertionError(label)
    print(f"[ok] {label}")


spec = importlib.util.spec_from_file_location("corolla_equiv", TOOL)
assert spec is not None and spec.loader is not None
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

tracked = json.loads(ARTIFACT.read_text(encoding="utf-8"))
fresh = mod.build_report(BASELINE, TARGET, "8965H1202000", "8965F1208000")
check("tracked equivalence report regenerates exactly from raw CodeFlash", tracked == fresh)

cmp = tracked["comparison"]
check("exactly 2190 normalized CodeFlash bytes differ", cmp["different_bytes"] == 2190)
check("first delta is 0xA004", cmp["first_difference"] == "0xA004")
check("last delta is 0x17DFF", cmp["last_difference"] == "0x17DFF")
check("886 exact changed runs are retained", cmp["exact_changed_run_count"] == 886)
check("18 coalesced calibration/identity regions are retained", cmp["coalesced_region_count"] == 18)

app = tracked["application_equivalence"]
check("entire 0x20000..0xFFFFF application image is byte-identical", app["identical"] and app["different_bytes"] == 0)
check("application region is 0xE0000 bytes", app["size"] == 0xE0000)
check("application hashes match", app["baseline_sha256"] == app["target_sha256"])

pins = tracked["pinned_ranges"]
for name in ("payload_build_secret", "boot_security_access_secret", "application_security_access_secret", "f181_primary_record"):
    check(f"{name} is byte-identical", pins[name]["identical"])
check("F181 primary record remains 8965F1208000", pins["f181_primary_record"]["target_ascii"] == "8965F1208000")
check("F181 secondary record advances to 8A3111213000", pins["f181_secondary_record"]["target_ascii"] == "8A3111213000")
check("separate one-record identity advances to 8965H1213000", pins["single_record_identity"]["target_ascii"] == "8965H1213000")
check("Span serial is present in the static image", pins["serial"]["target_ascii"] == "8965012N50E12H030731")

base_crc = tracked["crc_descriptors"]["baseline"]
target_crc = tracked["crc_descriptors"]["target"]
check("both Corolla images expose two valid self-describing CRC regions", len(base_crc) == len(target_crc) == 2 and all(r["terminal_fixup_valid"] for r in base_crc + target_crc))
check("lower calibration/identity CRC fixup changes", base_crc[0]["stored_fixup"] != target_crc[0]["stored_fixup"])
check("application CRC geometry and stock fixup are identical", base_crc[1] == target_crc[1])

check("semantic inheritance is explicitly limited to exact application bytes", tracked["interpretation_boundary"]["exact_application_byte_identity_allows_semantic_transfer"])
check("low-region differences remain an explicit independent-audit boundary", tracked["interpretation_boundary"]["low_region_differences_require_independent_data_calibration_identity_audit"])

print("\nSpan/albino Corolla CodeFlash equivalence verification passed.")
