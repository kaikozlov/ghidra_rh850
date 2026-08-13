#!/usr/bin/env python3
"""Verify manifest-driven SecOC patcher host/runtime contracts."""

from __future__ import annotations

import copy
import json
import struct
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from exploit.patcher.patch_config import (
    CONFIG_SIZE,
    EXPECTED_RESIDUE,
    FLAG_APPLY,
    FLAG_VALIDATE_ONLY,
    MAGIC,
    PatchConfigError,
    PatchConfigV1,
    STRUCT,
    VERSION,
    config_from_manifest,
)

passed = failed = 0


def check(name: str, condition: object, detail: str = "") -> None:
    global passed, failed
    ok = bool(condition)
    passed += int(ok)
    failed += int(not ok)
    suffix = f" ({detail})" if detail else ""
    print(f"[{'PASS' if ok else 'FAIL'}] {name}{suffix}")


def rejects(name: str, manifest: dict, needle: str) -> None:
    try:
        config_from_manifest(manifest)
    except PatchConfigError as exc:
        check(name, needle.lower() in str(exc).lower(), str(exc))
    else:
        check(name, False, "unexpectedly accepted")


manifest_path = REPO / "data" / "generated" / "secoc_patch_manifest_4512000.json"
manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

print("== ABI shape ==")
check("runtime config ABI is exactly 96 bytes", CONFIG_SIZE == 96 and STRUCT.size == 96)
check("ABI magic encodes SPC1", struct.pack("<I", MAGIC) == b"SPC1")
check("ABI version is pinned", VERSION == 1)
header = (REPO / "exploit" / "common" / "patch_config.h").read_text(encoding="utf-8")
check("C and Python agree on config size", "#define PATCH_CONFIG_SIZE        96u" in header)
check("C header carries no Sienna patch VA", "8E6C8" not in header.upper())
check("C header carries no Sienna CRC geometry", "FFDEC" not in header.upper() and "18000" not in header.upper())

print("\n== Sienna manifest serialization ==")
validate = config_from_manifest(manifest, mode="validate-only")
raw = validate.to_bytes()
parsed = PatchConfigV1.from_bytes(raw)
check("validate-only mode is explicit", validate.flags == FLAG_VALIDATE_ONLY and parsed.flags == FLAG_VALIDATE_ONLY)
check("image SHA binding serializes exactly", parsed.image_sha256.hex() == manifest["image"]["sha256"])
check("image geometry serializes exactly", parsed.image_base == int(manifest["image"]["base"], 0) and parsed.image_size == manifest["image"]["size"])
check("patch VA serializes exactly", parsed.patch_va == int(manifest["patch"]["address"], 0))
check("patch preimage serializes exactly", parsed.original.hex() == manifest["patch"]["original"])
check("patch replacement serializes exactly", parsed.replacement.hex() == manifest["patch"]["replacement"])
check("patch block geometry serializes exactly", parsed.patch_block_base == int(manifest["patch"]["block_base"], 0) and parsed.flash_block_size == manifest["patch"]["block_size"])
check("CRC start/end serialize exactly", parsed.crc_start == int(manifest["boot_crc"]["start"], 0) and parsed.crc_end == int(manifest["boot_crc"]["end"], 0))
check("CRC fixup geometry serializes exactly", parsed.crc_fixup_va == int(manifest["boot_crc"]["fixup_va"], 0) and parsed.crc_fixup_block_base == int(manifest["boot_crc"]["fixup_block_base"], 0))
check("expected residue is backend invariant", parsed.expected_residue == EXPECTED_RESIDUE == 0xFFFFFFFF)
check("serialized config CRC validates", parsed.config_crc32 == validate.compute_crc32())

apply_cfg = config_from_manifest(manifest, mode="apply")
check("APPLY mode changes only explicit mode flag", apply_cfg.flags == FLAG_APPLY and apply_cfg.to_bytes()[8:] == validate.to_bytes()[8:92] + apply_cfg.to_bytes()[92:])
# The CRC necessarily changes with the flags. Compare semantic fields instead of raw tail.
check("APPLY preserves target identity", apply_cfg.image_sha256 == validate.image_sha256 and apply_cfg.patch_va == validate.patch_va and apply_cfg.original == validate.original and apply_cfg.replacement == validate.replacement)

print("\n== config corruption is rejected ==")
corrupt = bytearray(raw)
corrupt[0x30] ^= 0x01
try:
    PatchConfigV1.from_bytes(bytes(corrupt))
except PatchConfigError as exc:
    check("single-byte runtime corruption trips config CRC", "config_crc32" in str(exc), str(exc))
else:
    check("single-byte runtime corruption trips config CRC", False)

print("\n== fail-closed manifest validation ==")
bad = copy.deepcopy(manifest)
bad["semantic_resolution"]["candidate_count"] = 2
rejects("ambiguous semantic manifest is rejected", bad, "exactly one")

bad = copy.deepcopy(manifest)
bad["patch"]["preimage_verified"] = False
rejects("unverified preimage manifest is rejected", bad, "preimage")

bad = copy.deepcopy(manifest)
bad["patch"]["block_base"] = "0x88001"
rejects("unaligned patch block is rejected", bad, "unaligned")

bad = copy.deepcopy(manifest)
bad["patch"]["block_size"] = 0x4000
rejects("non-P1M-E FCU block size is rejected", bad, "requires 0x8000")

bad = copy.deepcopy(manifest)
bad["boot_crc"]["fixup_block_base"] = "0xF8001"
rejects("unaligned CRC block is rejected", bad, "unaligned")

bad = copy.deepcopy(manifest)
bad["boot_crc"]["fixup_va"] = "0xFFDE8"
rejects("non-terminal CRC fixup is rejected", bad, "terminal")

bad = copy.deepcopy(manifest)
bad["patch"]["address"] = "0x100000"
rejects("out-of-image patch is rejected", bad, "outside image")

bad = copy.deepcopy(manifest)
bad["safety"]["fail_closed"] = False
rejects("non-fail-closed manifest is rejected", bad, "fail-closed")

print("\n== synthetic foreign manifest has no calibration routing ==")
foreign = copy.deepcopy(manifest)
foreign["image"]["sha256"] = "42" * 32
foreign["patch"]["address"] = "0x42220"
foreign["patch"]["block_base"] = "0x40000"
foreign["patch"]["original"] = "3412"
foreign["patch"]["replacement"] = "3512"
foreign["boot_crc"]["start"] = "0x20000"
foreign["boot_crc"]["end"] = "0x7FFF0"
foreign["boot_crc"]["fixup_va"] = "0x7FFEC"
foreign["boot_crc"]["fixup_block_base"] = "0x78000"
foreign["semantic_resolution"]["patch"]["address"] = "0x00042220"
foreign["semantic_resolution"]["patch"]["original"] = "3412"
foreign["semantic_resolution"]["patch"]["replacement"] = "3512"
foreign_cfg = config_from_manifest(foreign)
check("synthetic foreign manifest serializes without special case", PatchConfigV1.from_bytes(foreign_cfg.to_bytes()).patch_va == 0x42220)
source = (REPO / "exploit" / "patcher" / "patch_config.py").read_text(encoding="utf-8").lower()
check("serializer has no software-ID routing table", "software_id" not in source and "8965" not in source)
check("serializer has no known Sienna target/CRC addresses", all(token not in source for token in ("8e6c8", "ffdec", "88000", "f8000")))

print("\n== zero-write preflight structure ==")
main_c = (REPO / "exploit" / "patcher" / "main.c").read_text(encoding="utf-8").lower()
preflight_c = (REPO / "exploit" / "patcher" / "preflight.c").read_text(encoding="utf-8").lower()
runtime_c = (REPO / "exploit" / "common" / "runtime.c").read_text(encoding="utf-8").lower()
zero_write_sources = "\n".join((main_c, preflight_c, runtime_c))
for forbidden, label in (
    ("faci_", "FACI helper"),
    ("flwl_reg", "flash write-lock register"),
    ("flwe_reg", "flash write-enable register"),
    ("flash_block_rmw", "flash block RMW"),
    ("program_page", "flash programming"),
    ("erase(", "flash erase"),
):
    check(f"validate-only implementation contains no {label}", forbidden not in zero_write_sources)
check("preflight validates config before live patch read", preflight_c.index("validate_patch_config_runtime") < preflight_c.index("verify_patch_preimage"))
check("preflight checks exact target preimage", "verify_patch_preimage" in preflight_c and "err_patch_preimage" in preflight_c)
check("preflight reports stored CRC fixup", "read_le_word(cfg->crc_fixup_va)" in preflight_c)
check("preflight computes live CRC prefix", "crc32_flash_range(cfg->crc_start, cfg->crc_fixup_va)" in preflight_c)
check("preflight computes current full residue", "crc32_flash_range(cfg->crc_start, cfg->crc_end)" in preflight_c)
check("validate-only returns to halt before APPLY dispatch", main_c.index("patch_config_validate_only") < main_c.index("run_apply(&g_patch_config)"))
check("payload source contains no reset call", "reset(" not in zero_write_sources and "0x157e" not in zero_write_sources)
check("runtime halt services watchdog indefinitely", "while (1)" in runtime_c and "feed_watchdog();" in runtime_c)
check("config slot is a separate fixed linker section", ".patch_config" in (REPO / "exploit" / "patcher" / "config_slot.c").read_text(encoding="utf-8"))

print("\n== fail-closed APPLY structure ==")
apply_c = (REPO / "exploit" / "patcher" / "apply.c").read_text(encoding="utf-8").lower()
flash_c = (REPO / "exploit" / "patcher" / "flash_backend.c").read_text(encoding="utf-8").lower()
rmw_positions = []
pos = 0
while True:
    pos = apply_c.find("flash_block_rmw(", pos)
    if pos < 0:
        break
    rmw_positions.append(pos)
    pos += 1
check("APPLY performs exactly target and fixup block RMW calls", len(rmw_positions) == 2, repr(rmw_positions))
if len(rmw_positions) == 2:
    preimage_pos = apply_c.index("verify_patch_preimage")
    target_readback_pos = apply_c.index("live_bytes_equal(cfg->patch_va", rmw_positions[0])
    live_prefix_pos = apply_c.index("crc32_flash_range(cfg->crc_start, cfg->crc_fixup_va)", rmw_positions[0])
    fixup_readback_pos = apply_c.index("readback = read_le_word(cfg->crc_fixup_va)", rmw_positions[1])
    final_crc_pos = apply_c.index("crc32_flash_range(cfg->crc_start, cfg->crc_end)", rmw_positions[1])
    check("APPLY verifies exact preimage before first persistent RMW", preimage_pos < rmw_positions[0])
    check("APPLY verifies target readback before CRC computation", rmw_positions[0] < target_readback_pos < live_prefix_pos)
    check("CRC prefix is computed from live flash after target RMW", rmw_positions[0] < live_prefix_pos < rmw_positions[1])
    check("fixup readback occurs after fixup RMW", rmw_positions[1] < fixup_readback_pos)
    check("final full-region CRC occurs after fixup readback", fixup_readback_pos < final_crc_pos)
check("APPLY derives fixup as prefix xor expected residue", "new_fixup = crc_prefix ^ 0xffffffffu" in apply_c)
check("APPLY rejects target RMW failure", "err_target_rmw" in apply_c)
check("APPLY rejects target readback mismatch", "err_target_readback" in apply_c)
check("APPLY rejects fixup RMW failure", "err_fixup_rmw" in apply_c)
check("APPLY rejects fixup readback mismatch", "err_fixup_readback" in apply_c)
check("APPLY rejects final residue mismatch", "err_final_residue" in apply_c)
apply_dispatch_pos = main_c.index("run_apply(&g_patch_config)")
apply_success_pos = main_c.index("telemetry_stage(stage_success)", apply_dispatch_pos)
check("success is emitted only after run_apply returns zero", apply_dispatch_pos < main_c.index("if (err == 0u)", apply_dispatch_pos) < apply_success_pos)
check("flash backend retains reviewed FACI primitive", all(token in flash_c for token in ("faci_erase", "faci_program_page", "faci_fentryr", "faci_fpckar")))
all_generic_c = "\n".join(
    p.read_text(encoding="utf-8").lower()
    for p in (REPO / "exploit").rglob("*.c")
)
check("generic payload C embeds no known Sienna patch/CRC addresses", all(token not in all_generic_c for token in ("8e6c8", "ffdec", "88000", "f8000")))
check("generic payload C contains no automatic reset target", "0x157e" not in all_generic_c and "reset(" not in all_generic_c)

print("\n== offline Sienna APPLY algorithm ==")
from tools.build_secoc_patch_manifest import crc32
blob = bytearray((REPO / "firmware" / "RH850_P1M-E_CodeFlash.bin").read_bytes())
image_off = validate.patch_va - validate.image_base
check("offline fixture starts at configured preimage", bytes(blob[image_off:image_off + validate.patch_len]) == validate.original)
blob[image_off:image_off + validate.patch_len] = validate.replacement
prefix = crc32(blob[validate.crc_start - validate.image_base:validate.crc_fixup_va - validate.image_base])
new_fixup = prefix ^ EXPECTED_RESIDUE
struct.pack_into("<I", blob, validate.crc_fixup_va - validate.image_base, new_fixup)
residue = crc32(blob[validate.crc_start - validate.image_base:validate.crc_end - validate.image_base])
check("offline live-order algorithm reproduces manifest fixup", new_fixup == int(manifest["boot_crc"]["patched_fixup_for_supplied_image"], 0))
check("offline live-order algorithm reaches expected final residue", residue == EXPECTED_RESIDUE)

print(f"\n== RESULT: {passed} passed, {failed} failed ==")
if failed:
    raise SystemExit(1)
