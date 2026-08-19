#!/usr/bin/env python3
"""Verify the 2023 Corolla 8965H1202000 CodeFlash corpus and cross-image findings."""
from __future__ import annotations

import hashlib
import json
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from tools.build_ephemeral_runtime_manifest import load_codeflash  # noqa: E402
from tools.build_secoc_patch_manifest import build_manifest as build_patch_manifest  # noqa: E402

RAW_DIR = REPO / "community/albinoelephant/raw-20260818"
SESSION = RAW_DIR / "albinoelephant-corolla-2023.20260814-0023"
RANGE = SESSION / "dump_codeflash_00000000_00200000_20260814-025814.bin"
MANIFEST_TXT = RAW_DIR / "MANIFEST.txt"
SIENNA = (REPO / "firmware/RH850_P1M-E_CodeFlash.bin").read_bytes()
GATE = REPO / "data/generated/secoc_gate_resolution_8965H1202000_minimal.json"
RUNTIME = REPO / "data/generated/ephemeral_runtime_target_manifest_8965H1202000.json"

SOURCE_SHA = "97f9d42d936b97a99e7ab3d3ef20c6fb4c1fc3cc2ba199f6b158675a1709aee6"
CODEFLASH_SHA = "0b47bdc1217835c839e3543e52eab40eb793650a9c159e46f6a9b365ea41a67f"

passed = failed = 0


def check(name: str, condition: object, detail: str = "") -> None:
    global passed, failed
    ok = bool(condition)
    passed += int(ok)
    failed += int(not ok)
    suffix = f" ({detail})" if detail else ""
    print(f"[{'PASS' if ok else 'FAIL'}][raw_bytes] {name}{suffix}")


def occurrences(blob: bytes, needle: bytes) -> list[int]:
    out: list[int] = []
    pos = 0
    while True:
        pos = blob.find(needle, pos)
        if pos < 0:
            return out
        out.append(pos)
        pos += 1


print("== immutable acquisition and normalization ==")
raw = RANGE.read_bytes()
check("tracked range dump is exactly 2 MiB", len(raw) == 0x200000)
check("tracked range dump SHA-256 matches contributor manifest", hashlib.sha256(raw).hexdigest() == SOURCE_SHA)
codeflash, source = load_codeflash(RANGE)
check("upper 1 MiB is acquisition padding", raw[0x100000:] == b"\xFF" * 0x100000)
check("normalization returns exact first 1 MiB", codeflash == raw[:0x100000] and len(codeflash) == 0x100000)
check("normalized CodeFlash SHA-256 is pinned", hashlib.sha256(codeflash).hexdigest() == CODEFLASH_SHA)
check("normalization preserves source provenance", source["sha256"] == SOURCE_SHA and source["size"] == 0x200000)
manifest_text = MANIFEST_TXT.read_text(encoding="utf-8")
check("contributor manifest identifies no-glitch owner-side acquisition", "No glitching, no bench work, no module removal" in manifest_text)

print("\n== embedded ECU identity ==")
check("MCU boot-info string is exact", codeflash[0x180:0x180 + 40] == b"BOOT INFO AREA  R7F701383       72114350")
check("ECU serial is exact", codeflash[0xA4DC:0xA4DC + 20] == b"8965012N50A05G310920")
check("live primary software ID is exact", codeflash[0x17D80:0x17D80 + 12] == b"8965H1202000")
check("live secondary software ID is exact", codeflash[0x17DC0:0x17DC0 + 12] == b"8A3111202000")
check("8965F1208000 exists only as a distinct embedded table entry", codeflash[0x20860:0x20860 + 12] == b"8965F1208000")
check("H1202000 and F1208000 identities are not conflated", codeflash[0x17D80:0x17D8C] != codeflash[0x20860:0x2086C])

print("\n== cross-calibration crypto roots ==")
for address, label in (
    (0xBFD8, "payload-build secret"),
    (0xBFE8, "boot SecurityAccess secret"),
    (0x20840, "application SecurityAccess secret"),
):
    check(f"{label} is byte-identical to 4512000 at {address:#x}", codeflash[address:address + 16] == SIENNA[address:address + 16])
check("payload-build secret exact value", codeflash[0xBFD8:0xBFE8].hex() == "ba052435f8843f985fd1329d2b6117b0")
check("boot SA secret exact value", codeflash[0xBFE8:0xBFF8].hex() == "f05f36b7d78c03e24ab4faef2a57d044")
check("application SA secret exact value", codeflash[0x20840:0x20850].hex() == "893e08418c741ffa2a9c044bffa55813")
check("boot SA stage-1 routine transfers byte-for-byte", codeflash[0x6FD0:0x6FD0 + 50] == SIENNA[0x6FEC:0x6FEC + 50])
check("complete boot SA request/key/lockout/init state machine transfers at -0x1c",
      codeflash[0x530C:0x5612] == SIENNA[0x5328:0x562E])

print("\n== foreign Gate-2 and CRC-resigning manifest ==")
gate = json.loads(GATE.read_text(encoding="utf-8"))
check("foreign Gate-2 resolver is unique and SHA-bound", gate["resolution"] == "unique" and gate["candidate_count"] == 1 and gate["program_sha256"] == CODEFLASH_SHA)
check("foreign Gate-2 CMP neutralization is exact", gate["patch"] == {
    "address": "0x00088c62",
    "original": "e0d1",
    "replacement": "e001",
    "operation": "cmp-second-register-to-first-force-fallthrough",
})
check("foreign Gate-2 preserves BNE topology", gate["control_flow"]["bne"] == "0x00088c64" and gate["control_flow"]["bne_bytes"] == "9a0d" and gate["control_flow"]["verified_delivery_fallthrough"] == "0x00088c66")
with tempfile.TemporaryDirectory(prefix="corolla-codeflash-") as td:
    normalized = Path(td) / "8965H1202000_CodeFlash.bin"
    normalized.write_bytes(codeflash)
    patch_manifest = build_patch_manifest(gate, normalized, 0)
check("foreign stock region-1 CRC validates", patch_manifest["boot_crc"]["stock_region_valid"] is True and patch_manifest["boot_crc"]["stock_residue"] == "0xFFFFFFFF")
check("foreign region-1 geometry matches discovered P1M-E layout", patch_manifest["boot_crc"]["start"] == "0x18000" and patch_manifest["boot_crc"]["end"] == "0xFFDF0" and patch_manifest["boot_crc"]["fixup_va"] == "0xFFDEC")
check("foreign stock CRC fixup is exact", patch_manifest["boot_crc"]["stored_fixup"] == "0xAD59D70C")
check("foreign Gate patch resigns to exact fixup", patch_manifest["boot_crc"]["patched_fixup_for_supplied_image"] == "0xDD5F1477" and patch_manifest["boot_crc"]["patched_residue_for_supplied_image"] == "0xFFFFFFFF")

print("\n== Lochuan checkpoint-patch homolog ==")
# SECOC-050/CORR-066: use surrounding bytes, not the one-byte immediate alone.
sienna_lochuan_context = SIENNA[0x664E2:0x664EA]
hits = occurrences(codeflash, sienna_lochuan_context)
check("Sienna Lochuan-patch context has one foreign homolog", hits == [0x6081A], repr([hex(x) for x in hits]))
check("foreign homolog has the same 0x31 failure-status byte", codeflash[0x6081E] == 0x31)

print("\n== foreign ephemeral-runtime capability result ==")
runtime = json.loads(RUNTIME.read_text(encoding="utf-8"))
check("runtime manifest is bound to normalized and source hashes", runtime["image"]["sha256"] == CODEFLASH_SHA and runtime["image"]["source_sha256"] == SOURCE_SHA)
check("runtime manifest records only exact 12-character software IDs", runtime["image"]["software_ids"] == ["8965F1208000", "8965H1202000"])
records = runtime["secoc_records"]["records"]
check("Gate-2 queue has exactly three configured records", runtime["secoc_records"]["record_count"] == 3 and len(records) == 3)
check("foreign Gate-2 queue IDs are 00F/D7/B6", [r["can_id"] for r in records] == ["0xF", "0xD7", "0xB6"])
check("foreign Gate-2 queue omits steering 2E4/131", runtime["secoc_records"]["steering_bridge_missing_ids"] == ["0x2E4", "0x131"] and runtime["secoc_records"]["steering_bridge_profiles"] == [])
check("missing steering profiles are a successful fail-closed capability result", runtime["status"] == "semantic-resolved-steering-unsupported" and runtime["runtime_build_ready"] is False)

print(f"\nResults: {passed} passed, {failed} failed")
if failed:
    raise SystemExit(1)
