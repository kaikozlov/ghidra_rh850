#!/usr/bin/env python3
"""Verify the exact 2026 Camry 8965F3307000 SecOC Gate-2 patch contract."""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from exploit.patcher.build_payload import make_restore_config, simulate_apply  # noqa: E402
from exploit.patcher.patch_config import config_from_manifest  # noqa: E402
from tools.build_secoc_patch_manifest import build_manifest, crc32  # noqa: E402

IMAGE = REPO / "community/kai/camry-2026/normalized/8965F3307000_CodeFlash.bin"
SIENNA = REPO / "firmware/RH850_P1M-E_CodeFlash.bin"
GATE = REPO / "data/generated/secoc_gate_resolution_8965F3307000_minimal.json"
MANIFEST = REPO / "data/generated/secoc_patch_manifest_8965F3307000.json"
IMAGE_SHA = "42dce8efc42f6ae31718e7713fa2d26bb9191b4a82439778aee4d7afded9b0e7"

passed = failed = 0


def check(name: str, condition: object, detail: str = "") -> None:
    global passed, failed
    ok = bool(condition)
    passed += int(ok)
    failed += int(not ok)
    print(f"[{'PASS' if ok else 'FAIL'}][raw_bytes] {name}" + (f" ({detail})" if detail else ""))


def occurrences(blob: bytes, needle: bytes) -> list[int]:
    out: list[int] = []
    pos = 0
    while True:
        pos = blob.find(needle, pos)
        if pos < 0:
            return out
        out.append(pos)
        pos += 1


image = IMAGE.read_bytes()
sienna = SIENNA.read_bytes()
gate = json.loads(GATE.read_text(encoding="utf-8"))
manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))

print("== exact F33 image and crypto-root provenance ==")
check("normalized F33 CodeFlash is exactly 1 MiB", len(image) == 0x100000)
check("normalized F33 SHA-256 is pinned", hashlib.sha256(image).hexdigest() == IMAGE_SHA)
for start, label in ((0xBFD8, "payload-build root"), (0xBFE8, "boot-SA root"), (0x20840, "application-SA root")):
    f33 = image[start:start + 16]
    check(f"F33 {label} is 16 bytes and byte-identical to canonical Sienna", len(f33) == 16 and f33 == sienna[start:start + 16])

print("\n== target-native Gate-2 semantic result ==")
check("fresh bare-import semantic resolver is unique and SHA-bound",
      gate["candidate_count"] == 1 and gate["resolution"] == "unique" and gate["program_sha256"] == IMAGE_SHA)
check("F33 Gate-2 owner and CMP are exact",
      gate["function"]["entry"] == "0x0008f906" and gate["patch"]["address"] == "0x0008f952")
check("F33 patch is CMP neutralization",
      gate["patch"]["original"] == "e0d1" and gate["patch"]["replacement"] == "e001"
      and gate["patch"]["operation"] == "cmp-second-register-to-first-force-fallthrough")
check("verify-result polarity is zero-success", gate["verify_result_polarity"] == "zero-is-verified-ok-nonzero-is-not-verified")
flow = gate["control_flow"]
check("F33 BNE topology is exact",
      flow["bne"] == "0x0008f954" and flow["bne_bytes"] == "9a0d"
      and flow["verified_delivery_fallthrough"] == "0x0008f956"
      and flow["mismatch_branch_target"] == "0x0008f966" and flow["join"] == "0x0008f96e")
check("both stock arms retain calls", flow["verified_fallthrough_calls"] == 2 and flow["mismatch_branch_calls"] == 1)
egg = bytes.fromhex("e0d19a0d1a38bfff")
check("full Gate-2 machine anchor is unique in exact F33", occurrences(image, egg) == [0x8F952])
check("raw patch preimage is exact", image[0x8F952:0x8F954] == bytes.fromhex("e0d1"))

print("\n== deterministic F33 manifest and CRC resign ==")
rebuilt = build_manifest(gate, IMAGE, 0)
check("committed F33 patch manifest is deterministic", rebuilt == manifest)
check("manifest is exact-image/preimage bound",
      manifest["image"]["sha256"] == IMAGE_SHA and manifest["patch"] == {
          "address": "0x8F952", "block_base": "0x88000", "block_size": 32768,
          "original": "e0d1", "preimage_verified": True, "replacement": "e001",
      })
crc = manifest["boot_crc"]
check("F33 high boot CRC is stock-valid",
      crc["start"] == "0x18000" and crc["end"] == "0xFFDF0"
      and crc["fixup_va"] == "0xFFDEC" and crc["stock_region_valid"] is True
      and crc["stock_residue"] == "0xFFFFFFFF")
check("F33 patch has deterministic repaired fixup/residue",
      crc["patched_prefix_crc_for_supplied_image"] == "0x2650CC50"
      and crc["patched_fixup_for_supplied_image"] == "0xD9AF33AF"
      and crc["patched_residue_for_supplied_image"] == "0xFFFFFFFF")
check("both self-describing F33 CRC regions validate",
      manifest["discovery"]["crc_descriptor_count"] == 2
      and all(row["terminal_fixup_valid"] for row in manifest["discovery"]["crc_descriptors"]))

print("\n== generic patcher apply/restore simulation ==")
apply_cfg = config_from_manifest(manifest, mode="apply")
patched, patched_fixup, patched_residue = simulate_apply(image, apply_cfg)
check("generic patcher simulation applies only the target predicate plus CRC fixup",
      patched[0x8F952:0x8F954] == bytes.fromhex("e001")
      and patched_fixup == 0xD9AF33AF and patched_residue == 0xFFFFFFFF)
restore_cfg = make_restore_config(apply_cfg)
restored, restore_fixup, restore_residue = simulate_apply(patched, restore_cfg)
check("generic restore simulation recovers original Gate-2 bytes", restored[0x8F952:0x8F954] == bytes.fromhex("e0d1"))
check("generic restore simulation returns the exact stock image",
      restored == image and restore_fixup == int(crc["stored_fixup"], 0) and restore_residue == 0xFFFFFFFF)
check("direct CRC of simulated patched high region is valid",
      crc32(patched[int(crc["start"], 0):int(crc["end"], 0)]) == 0xFFFFFFFF)

print(f"\n{passed} passed, {failed} failed")
raise SystemExit(1 if failed else 0)
