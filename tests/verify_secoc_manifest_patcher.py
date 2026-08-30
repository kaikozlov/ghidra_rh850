#!/usr/bin/env python3
"""Verify manifest-driven SecOC patcher host/runtime contracts."""

from __future__ import annotations

import copy
import hashlib
import json
import os
import struct
import subprocess
import sys
import tempfile
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
from exploit.common.payload_package import PAYLOAD_LOAD_ADDR, PAYLOAD_SIZE, inspect_payload, package_shellcode
from exploit.common.ram_exec import bootstrap_protocol_values, explicit_ram_exec_geometry, explicit_route
from exploit.patcher.build_payload import (
    CONFIG_OFFSET,
    TEMPLATE_SIZE,
    PayloadBuildError,
    build_configured_payload,
    inject_config,
    validate_restore_artifact,
)
from exploit.patcher.deploy import (
    DeployError,
    TelemetryCollector,
    expected_preflight,
    preflight_record,
    validate_preflight_for_apply,
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

print("== boot bootstrap grammar ==")
old0 = explicit_route(bus=0, elm327_param=1, uds_variant="old", cpu_index=0)
new0 = explicit_route(bus=0, elm327_param=1, uds_variant="new", cpu_index=0)
old1 = explicit_route(bus=0, elm327_param=1, uds_variant="old", cpu_index=1)
new1 = explicit_route(bus=0, elm327_param=1, uds_variant="new", cpu_index=1)
check("old-stack CPU0 keeps DID 0203 all-zero while RequestDownload uses memory ID 1", bootstrap_protocol_values(old0) == (bytes(5), b"\x01", b"\x45\x00"))
check("new-stack CPU0 alone uses DID 0203 offset selector 01", bootstrap_protocol_values(new0) == (b"\x01" + bytes(4), b"\x01", b"\x45\x01"))
check("old-stack CPU1 keeps zero DID 0203 and memory ID 0", bootstrap_protocol_values(old1) == (bytes(5), b"\x00", b"\x45\x00"))
check("new-stack CPU1 keeps zero DID 0203 and uses new routine magic", bootstrap_protocol_values(new1) == (bytes(5), b"\x00", b"\x45\x01"))

print("== ABI shape ==")
check("runtime config ABI is exactly 96 bytes", CONFIG_SIZE == 96 and STRUCT.size == 96)
check("ABI magic encodes SPC1", struct.pack("<I", MAGIC) == b"SPC1")
check("ABI version is pinned", VERSION == 1)
header = (REPO / "exploit" / "common" / "patch_config.h").read_text(encoding="utf-8")
check("C and Python agree on config size", "#define PATCH_CONFIG_SIZE        96u" in header)
check("C header carries no Sienna patch VA", "8E6C6" not in header.upper() and "8E6C8" not in header.upper())
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
bad["image"]["base"] = "0x8000"
rejects("nonzero image base is outside the P1M-E backend allowlist", bad, "requires codeflash")

bad = copy.deepcopy(manifest)
bad["image"]["size"] = 0x200000
rejects("oversized image is outside the P1M-E backend allowlist", bad, "requires codeflash")

bad = copy.deepcopy(manifest)
bad["boot_crc"]["fixup_block_base"] = "0xF8001"
rejects("unaligned CRC block is rejected", bad, "unaligned")

bad = copy.deepcopy(manifest)
bad["boot_crc"]["fixup_va"] = "0xFFDE8"
rejects("non-terminal CRC fixup is rejected", bad, "terminal")

bad = copy.deepcopy(manifest)
bad["patch"]["address"] = "0x100000"
bad["semantic_resolution"]["patch"]["address"] = "0x00100000"
rejects("out-of-image patch is rejected", bad, "outside image")

bad = copy.deepcopy(manifest)
bad["safety"]["fail_closed"] = False
rejects("non-fail-closed manifest is rejected", bad, "fail-closed")

bad = copy.deepcopy(manifest)
bad["semantic_resolution"]["program_sha256"] = "00" * 32
rejects("semantic/image SHA disagreement is rejected", bad, "does not match image.sha256")

bad = copy.deepcopy(manifest)
bad["semantic_resolution"]["patch"]["address"] = "0x1234"
rejects("semantic/top-level patch disagreement is rejected", bad, "does not match patch.address")

print("\n== synthetic foreign manifest has no calibration routing ==")
foreign = copy.deepcopy(manifest)
foreign["image"]["sha256"] = "42" * 32
foreign["semantic_resolution"]["program_sha256"] = "42" * 32
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
check("serializer has no known Sienna target/CRC addresses", all(token not in source for token in ("8e6c6", "8e6c8", "ffdec", "88000", "f8000")))

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
check("validate-only returns to halt before APPLY dispatch", main_c.index("patch_config_validate_only") < main_c.index("run_apply(cfg)"))
check("runtime is initialized before first telemetry send", main_c.index("runtime_init();") < main_c.index("telemetry_stage(stage_boot);"))
check("generic runtime does not call unverified F33 boot-RAM helpers", "0xfebf1188" not in runtime_c and "0xfebf11ac" not in runtime_c and "0xfebf11d2" not in runtime_c)
check("generic watchdog hook is intentionally inert until target-native recovery", "deliberate no-op until a target-native callable watchdog contract is proven" in runtime_c)
check("generic runtime does not write community scratch RAM before first witness", "0xfebf1f00" not in runtime_c and "0xfebf1f04" not in runtime_c)
check("payload source contains no reset call", "reset(" not in zero_write_sources and "0x157e" not in zero_write_sources)
check("runtime halt services watchdog indefinitely", "while (1)" in runtime_c and "feed_watchdog();" in runtime_c)
check("runtime enforces absolute P1M-E CodeFlash base/size", "patch_backend_flash_base" in runtime_c and "patch_backend_flash_size" in runtime_c)
ready_wait = runtime_c.index("tx_ready_mask")
message_write = runtime_c.index("*(tmptr", ready_wait)
submit = runtime_c.index("*(tmc", message_write)
result_wait = runtime_c.index("tx_result_mask", submit)
status_clear = runtime_c.index("& 0xf9u", result_wait)
check("telemetry waits for the field-proven callback idle mask before message RAM writes", ready_wait < message_write)
check("telemetry polls completion only after setting TMTR", submit < result_wait)
check("telemetry callback transport uses field-proven F33 0x06 idle/completion mask", "tx_ready_mask            0x06u" in runtime_c and "tx_result_mask           0x06u" in runtime_c)
check("telemetry callback clears completion without stock CanIf result reclassification", "tx_result_success_mask" not in runtime_c and "status & 0xf9u" in runtime_c)
check("telemetry status clear uses the firmware's sync barrier", 'asm("syncp")' in runtime_c)
header_lower = (REPO / "exploit" / "common" / "patch_config.h").read_text(encoding="utf-8").lower()
check("runtime config uses fixed plaintext-shellcode offset", "patch_config_offset      0x0f70u" in header_lower and "patch_config_runtime_addr" in header_lower)
check("runtime config slot remains below bootloader callback boundary", CONFIG_OFFSET + CONFIG_SIZE <= 0xFD0)
from exploit.patcher.build_shellcode_template import _compile_args as shellcode_compile_args
link_args = shellcode_compile_args("v850-elf-gcc", "shellcode.c", "shellcode.elf")
check("patcher shellcode links at authenticated callback VMA", f"-Wl,-Ttext=0x{PAYLOAD_LOAD_ADDR:08X}" in link_args and "-Wl,-Ttext=0" not in link_args)
ram_exec_source = (REPO / "exploit" / "common" / "ram_exec.py").read_text(encoding="utf-8")
check("payload telemetry accepts relay-mate Panda bus visibility", "bus != route.bus" not in ram_exec_source and "can_addr != RX_ADDR" in ram_exec_source)

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
apply_dispatch_pos = main_c.index("run_apply(cfg)")
apply_success_pos = main_c.index("telemetry_stage(stage_success)", apply_dispatch_pos)
check("success is emitted only after run_apply returns zero", apply_dispatch_pos < main_c.index("if (err == 0u)", apply_dispatch_pos) < apply_success_pos)
check("flash backend uses corrected P1M-E FACI register identities", all(token in flash_c for token in (
    "faci_fstatr", "0xffa10080", "faci_fastat", "0xffa10010",
    "faci_fentryr", "0xffa10084", "faci_fprotr", "0xffa10088",
    "faci_fareaselc", "0xffa10020", "fhve15_reg", "0xfff8a430",
    "fhve3_reg", "0xfff82410",
)))
check("FCU command completion checks timeout, status-mask, and command-lock state",
      "static int faci_result" in flash_c
      and "faci_err_timeout" in flash_c
      and "faci_err_status" in flash_c
      and "fastat_cmdlk_mask" in flash_c
      and "fstatr_error_mask         0x00007040u" in flash_c)
check("program data pacing uses manufacturer-proven post-write FSTATR DBFULL bit-10 poll",
      "fstatr_dbfull_mask" in flash_c and "0x00000400u" in flash_c
      and "while ((faci_fstatr & fstatr_dbfull_mask) != 0u)" in flash_c
      and flash_c.index("faci_fdata = word") < flash_c.index("while ((faci_fstatr & fstatr_dbfull_mask) != 0u)")
      and "unsigned short timeout = 0xffffu" in flash_c
      and "fstatr_program_pace_mask" not in flash_c
      and "0x00000800u" not in flash_c
      and "1u << 21" not in flash_c
      and "0x00200000" not in flash_c)
check("FCU cleanup has both Forced Stop and Status Clear",
      "faci_fcmd8 = 0xb3u" in flash_c and "faci_fcmd8 = 0x50u" in flash_c)
check("FCU failure cleanup propagates Status Clear result", "static int faci_failure_cleanup" in flash_c and flash_c.count("return faci_result();") >= 3)
check("FCU enter and exit transitions return checked status", "static int faci_enter_pe_mode" in flash_c and "static int faci_exit_pe_mode" in flash_c)
check("erase and program completion use full FACI result", flash_c.count("return faci_result();") >= 3)
check("all P/E-attempt failures converge on cleanup and exit", flash_c.count("goto cleanup;") >= 3 and "cleanup:" in flash_c and "err = faci_exit_pe_mode();" in flash_c)
check("FCU errors preserve failing phase in return code", all(token in flash_c for token in ("flash_err_unlock", "flash_err_enter", "flash_err_erase", "flash_err_program", "flash_err_exit", "flash_err_cleanup")))
all_generic_c = "\n".join(
    p.read_text(encoding="utf-8").lower()
    for p in (REPO / "exploit").rglob("*.c")
)
check("generic payload C embeds no known Sienna patch/CRC addresses", all(token not in all_generic_c for token in ("8e6c6", "8e6c8", "ffdec", "88000", "f8000")))
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

print("\n== authenticated RAM payload packaging ==")
firmware_bytes = (REPO / "firmware" / "RH850_P1M-E_CodeFlash.bin").read_bytes()
payload_build_secret = firmware_bytes[0xBFD8:0xBFE8]
security_access_secret = firmware_bytes[0xBFE8:0xBFF8]
community_payload = (REPO / "tests" / "fixtures" / "payloads" / "dataflash_dump_payload.bin").read_bytes()
community_inspection = inspect_payload(community_payload, secret=payload_build_secret)
check("community payload decrypts with separate payload-build secret", community_inspection.cmac_valid and community_inspection.crc_residue == 0xFFFFFFFF)
check("community payload callback is RAM base", community_inspection.callback_address == 0xFEBF0000)
check("community payload descriptor covers 0xFF0 bytes", community_inspection.descriptor_address == 0xFEBF0000 and community_inspection.descriptor_length == 0xFF0)
check("packager reproduces committed community ciphertext byte-for-byte", package_shellcode(community_inspection.shellcode_region[:0x18A], secret=payload_build_secret) == community_payload)
check("payload-build and SecurityAccess secrets are distinct in source firmware", payload_build_secret != security_access_secret)

print("\n== host payload injection and RESTORE artifact ==")
with tempfile.TemporaryDirectory() as td:
    temp = Path(td)
    template_path = temp / "generic_shellcode_template.bin"
    template_path.write_bytes(b"\x00" * TEMPLATE_SIZE)
    validate_out = temp / "validate.bin"
    validate_meta = build_configured_payload(
        image_path=REPO / "firmware" / "RH850_P1M-E_CodeFlash.bin",
        manifest_path=manifest_path,
        template_path=template_path,
        mode="validate-only",
        output_path=validate_out,
        payload_secret=payload_build_secret,
    )
    built = validate_out.read_bytes()
    configured_shellcode = Path(validate_meta["configured_shellcode"]["path"]).read_bytes()
    injected = PatchConfigV1.from_bytes(configured_shellcode[CONFIG_OFFSET:CONFIG_OFFSET + CONFIG_SIZE])
    packaged = inspect_payload(built, secret=payload_build_secret)
    check("configured shellcode template stays below callback boundary", len(configured_shellcode) == TEMPLATE_SIZE and TEMPLATE_SIZE <= 0xFD0)
    check("final authenticated upload remains exactly 4 KiB", len(built) == PAYLOAD_SIZE)
    check("fixed config slot contains serialized validate config", injected.flags == FLAG_VALIDATE_ONLY and injected.patch_va == validate.patch_va)
    check("ciphertext decrypts to configured shellcode", packaged.shellcode_region[:TEMPLATE_SIZE] == configured_shellcode and packaged.cmac_valid and packaged.crc_residue == 0xFFFFFFFF)
    check("build metadata pins image/manifest/template/payload hashes", all(validate_meta[key].get("sha256") for key in ("image", "manifest", "template", "payload")))

    bad_template = bytearray(b"\x00" * TEMPLATE_SIZE)
    bad_template[CONFIG_OFFSET] = 1
    try:
        inject_config(bytes(bad_template), validate)
    except PayloadBuildError as exc:
        check("non-placeholder template config slot is rejected", "all-zero" in str(exc), str(exc))
    else:
        check("non-placeholder template config slot is rejected", False)

    missing_restore_out = temp / "unsafe-apply.bin"
    try:
        build_configured_payload(
            image_path=REPO / "firmware" / "RH850_P1M-E_CodeFlash.bin",
            manifest_path=manifest_path,
            template_path=template_path,
            mode="apply",
            output_path=missing_restore_out,
            payload_secret=payload_build_secret,
        )
    except PayloadBuildError as exc:
        check("APPLY payload generation refuses missing RESTORE directory", "restore-dir" in str(exc).lower(), str(exc))
        check("refused APPLY leaves no configured payload behind", not missing_restore_out.exists())
    else:
        check("APPLY payload generation refuses missing RESTORE directory", False)

    restore_dir = temp / "restore"
    apply_out = temp / "apply.bin"
    apply_meta = build_configured_payload(
        image_path=REPO / "firmware" / "RH850_P1M-E_CodeFlash.bin",
        manifest_path=manifest_path,
        template_path=template_path,
        mode="apply",
        output_path=apply_out,
        payload_secret=payload_build_secret,
        restore_dir=restore_dir,
    )
    artifact_path = Path(apply_meta["restore_artifact"]["path"])
    artifact = validate_restore_artifact(
        artifact_path,
        image_path=REPO / "firmware" / "RH850_P1M-E_CodeFlash.bin",
        manifest_path=manifest_path,
        template_path=template_path,
        payload_secret=payload_build_secret,
    )
    restore_cfg = PatchConfigV1.from_bytes((restore_dir / "restore_config.bin").read_bytes())
    check("RESTORE config expects patched bytes", restore_cfg.original == apply_cfg.replacement)
    check("RESTORE config restores preserved preimage", restore_cfg.replacement == apply_cfg.original)
    check("RESTORE simulation restores target and valid CRC", artifact["validation"]["target_bytes_restored"] is True and int(artifact["validation"]["restore_simulated_residue"], 0) == EXPECTED_RESIDUE)
    check("RESTORE payload is independently hash-pinned", hashlib.sha256((restore_dir / "restore_payload.bin").read_bytes()).hexdigest() == artifact["restore_payload"]["sha256"])
    try:
        validate_restore_artifact(
            artifact_path,
            image_path=REPO / "firmware" / "RH850_P1M-E_CodeFlash.bin",
            manifest_path=manifest_path,
            template_path=template_path,
            expected_ram_load_addr=0xFEBE0000,
        )
    except PayloadBuildError as exc:
        check("RESTORE artifact is bound to its RAM-exec load address", "different RAM-exec load address" in str(exc), str(exc))
    else:
        check("RESTORE artifact is bound to its RAM-exec load address", False)

    wrong_image = temp / "wrong.bin"
    wrong_blob = bytearray((REPO / "firmware" / "RH850_P1M-E_CodeFlash.bin").read_bytes())
    wrong_blob[0] ^= 1
    wrong_image.write_bytes(wrong_blob)
    try:
        validate_restore_artifact(
            artifact_path,
            image_path=wrong_image,
            manifest_path=manifest_path,
            template_path=template_path,
        )
    except PayloadBuildError as exc:
        check("RESTORE artifact rejects different firmware image", "different pre-write" in str(exc), str(exc))
    else:
        check("RESTORE artifact rejects different firmware image", False)

    restore_payload_path = restore_dir / "restore_payload.bin"
    pristine_restore_payload = restore_payload_path.read_bytes()
    tampered_restore_payload = bytearray(pristine_restore_payload)
    tampered_restore_payload[0x20] ^= 1
    restore_payload_path.write_bytes(tampered_restore_payload)
    try:
        validate_restore_artifact(
            artifact_path,
            image_path=REPO / "firmware" / "RH850_P1M-E_CodeFlash.bin",
            manifest_path=manifest_path,
            template_path=template_path,
        )
    except PayloadBuildError as exc:
        check("RESTORE artifact rejects tampered recovery payload", "payload hash mismatch" in str(exc).lower(), str(exc))
    else:
        check("RESTORE artifact rejects tampered recovery payload", False)
    restore_payload_path.write_bytes(pristine_restore_payload)

    wrong_template = temp / "different-template.bin"
    wrong_template_blob = bytearray(b"\x00" * TEMPLATE_SIZE)
    wrong_template_blob[0x20] = 1
    wrong_template.write_bytes(wrong_template_blob)
    try:
        validate_restore_artifact(
            artifact_path,
            image_path=REPO / "firmware" / "RH850_P1M-E_CodeFlash.bin",
            manifest_path=manifest_path,
            template_path=wrong_template,
        )
    except PayloadBuildError as exc:
        check("RESTORE artifact rejects different generic template", "different generic shellcode template" in str(exc).lower(), str(exc))
    else:
        check("RESTORE artifact rejects different generic template", False)

print("\n== live-preflight APPLY gate model ==")
with tempfile.TemporaryDirectory() as td:
    temp = Path(td)
    live_blob = bytearray((REPO / "firmware" / "RH850_P1M-E_CodeFlash.bin").read_bytes())
    crc_start = int(manifest["boot_crc"]["start"], 0)
    crc_fixup = int(manifest["boot_crc"]["fixup_va"], 0)
    crc_end = int(manifest["boot_crc"]["end"], 0)
    live_prefix = crc32(live_blob[crc_start:crc_fixup])
    struct.pack_into("<I", live_blob, crc_fixup, live_prefix ^ EXPECTED_RESIDUE)
    live_image = temp / "live-valid.bin"
    live_image.write_bytes(live_blob)
    live_manifest = copy.deepcopy(manifest)
    live_manifest["image"]["path"] = str(live_image)
    live_manifest["image"]["sha256"] = hashlib.sha256(live_blob).hexdigest()
    live_manifest["semantic_resolution"]["program_sha256"] = live_manifest["image"]["sha256"]
    live_manifest_path = temp / "manifest.json"
    live_manifest_path.write_text(json.dumps(live_manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    template_path = temp / "generic_shellcode_template.bin"
    template_path.write_bytes(b"\x00" * TEMPLATE_SIZE)

    live_validate = config_from_manifest(live_manifest, mode="validate-only")
    expected = expected_preflight(bytes(live_blob), live_validate)
    check("synthetic live pre-write fixture has valid boot CRC", expected["crc_residue"] == EXPECTED_RESIDUE)

    def tstage(stage: int) -> bytes:
        return struct.pack("<II", 0xDEAD0000 | stage, 0xCAFEBABE)

    def tvalue(tag: int, field: int, value: int) -> bytes:
        return struct.pack("<II", (field << 8) | tag, value)

    collector = TelemetryCollector()
    config_values = {
        0x0001: live_validate.flags,
        0x0002: live_validate.patch_va,
        0x0003: live_validate.patch_block_base,
        0x0004: live_validate.flash_block_size,
        0x0005: live_validate.crc_start,
        0x0006: live_validate.crc_end,
        0x0007: live_validate.crc_fixup_va,
        0x0008: live_validate.crc_fixup_block_base,
        0x0009: PatchConfigV1.from_bytes(live_validate.to_bytes()).config_crc32,
    }
    preflight_fields = {0x0100: "patch_observed", 0x0101: "fixup_stored", 0x0102: "crc_prefix", 0x0103: "crc_residue"}
    collector.feed(tstage(0x10))
    collector.feed(tstage(0x11))
    for field, value in config_values.items():
        collector.feed(tvalue(0xB1, field, value))
    collector.feed(tstage(0x12))
    for field, name in preflight_fields.items():
        collector.feed(tvalue(0xB2, field, expected[name]))
    collector.feed(tstage(0x7F))
    collector.feed(tstage(0xFF))
    check("synthetic live preflight telemetry completes cleanly", collector.payload_success)

    pf = preflight_record(
        collector=collector,
        config=live_validate,
        image=bytes(live_blob),
        image_path=live_image,
        manifest_path=live_manifest_path,
        template_path=template_path,
        execution={"f181_hex": "018965B451200000000000", "f181_ascii": None, "boot_f181_hex": "02" + "21" * 32, "boot_f181_ascii": None, "route": {"bus": 1, "elm327_param": 1, "uds_variant": "old", "cpu_index": 0}},
        telemetry_sha256="ab" * 32,
    )
    check("matching valid live preflight is APPLY-ready", pf["apply_ready"] is True)
    pf_path = temp / "preflight.json"
    pf_path.write_text(json.dumps(pf, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    live_apply = config_from_manifest(live_manifest, mode="apply")
    accepted_pf = validate_preflight_for_apply(
        pf_path,
        config=live_apply,
        image=bytes(live_blob),
        manifest_path=live_manifest_path,
        template_path=template_path,
    )
    check("APPLY accepts only matching preflight identity/observations", accepted_pf["f181_hex"] == pf["f181_hex"])
    external_geometry = explicit_ram_exec_geometry(
        load_addr=0xFEBE0000,
        evidence="external-source:test-nondefault-geometry",
    )
    try:
        validate_preflight_for_apply(
            pf_path,
            config=live_apply,
            image=bytes(live_blob),
            manifest_path=live_manifest_path,
            template_path=template_path,
            ram_exec_geometry=external_geometry,
        )
    except DeployError as exc:
        check("APPLY rejects a preflight from different RAM-exec geometry", "RAM-exec geometry" in str(exc), str(exc))
    else:
        check("APPLY rejects a preflight from different RAM-exec geometry", False)

    bad_pf = copy.deepcopy(pf)
    bad_pf["observed"]["crc_prefix"] ^= 1
    bad_pf_path = temp / "bad-preflight.json"
    bad_pf_path.write_text(json.dumps(bad_pf, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    try:
        validate_preflight_for_apply(
            bad_pf_path,
            config=live_apply,
            image=bytes(live_blob),
            manifest_path=live_manifest_path,
            template_path=template_path,
        )
    except DeployError as exc:
        check("APPLY rejects preflight observations that do not match dump", "observations" in str(exc), str(exc))
    else:
        check("APPLY rejects preflight observations that do not match dump", False)

print("\n== bootstrap/deployer secret and routing discipline ==")
ram_exec_source = (REPO / "exploit" / "common" / "ram_exec.py").read_text(encoding="utf-8").lower()
deploy_source = (REPO / "exploit" / "patcher" / "deploy.py").read_text(encoding="utf-8").lower()
check("shared bootstrap contains no embedded SecurityAccess secret", "f05f36b7d78c03e24ab4faef2a57d044" not in ram_exec_source)
check("shared bootstrap contains no embedded payload-build secret", payload_build_secret.hex() not in ram_exec_source)
check("bootstrap takes SecurityAccess secret from environment/file", "toyota_eps_boot_secret_hex" in ram_exec_source and "security-secret-file" in deploy_source)
check("bootstrap takes separate payload-build secret from environment/file", "toyota_eps_payload_secret_hex" in ram_exec_source and "payload-secret-file" in deploy_source)
check("bootstrap requires explicit UDS variant", "uds variant must be explicitly 'old' or 'new'" in ram_exec_source)
check("bootstrap requires bootloader reappearance before SecurityAccess", "_enter_programming_bootloader" in ram_exec_source and "expected_boot_f181_hex" in ram_exec_source and "bootloader did not reappear" in ram_exec_source.lower())
check("bootstrap uses one clean boot DEFAULT-EXTENDED-PROGRAMMING ladder", "boot.diagnostic_session_control(session.default)" in ram_exec_source and "boot.diagnostic_session_control(session.extended_diagnostic)" in ram_exec_source and "boot.diagnostic_session_control(session.programming)" in ram_exec_source)
check("bootstrap clears host RX backlog immediately before FF00 trigger", "panda.can_clear(0xffff)" in ram_exec_source and ram_exec_source.index("panda.can_clear(0xffff)") < ram_exec_source.index("isotp_send = _import_isotp_send()"))
check("deployer requires explicit route or recorded session", "--session-dir or explicit --bus and --elm327-param" in deploy_source)
check("deployer binds APPLY to prior F181 before RAM upload", "expected_f181_hex = preflight.get(\"f181_hex\")" in deploy_source and "expected_f181_hex=expected_f181_hex" in deploy_source)
check("deployer requires explicit F181 on first live preflight", "first live validate-only execution requires --expected-f181-hex" in deploy_source and "expected_f181_hex=expected_f181_hex" in deploy_source)
check("deployer requires explicit boot F181 on first live preflight", "first live validate-only execution requires --expected-boot-f181-hex" in deploy_source and "expected_boot_f181_hex=expected_boot_f181_hex" in deploy_source)
check("deployer does not equate payload completion with SecOC proof", "it is not evidence that secoc authentication is bypassed" in deploy_source)

print("\n== deploy CLI fail-closed APPLY gate ==")
with tempfile.TemporaryDirectory() as td:
    temp = Path(td)
    template_path = temp / "generic_shellcode_template.bin"
    template_path.write_bytes(b"\x00" * TEMPLATE_SIZE)
    run_dir = temp / "run"
    result = subprocess.run(
        [
            sys.executable,
            str(REPO / "exploit" / "patcher" / "deploy.py"),
            str(REPO / "firmware" / "RH850_P1M-E_CodeFlash.bin"),
            "--manifest", str(manifest_path),
            "--template", str(template_path),
            "--run-dir", str(run_dir),
            "--apply",
        ],
        cwd=REPO,
        env={**os.environ, "TOYOTA_EPS_PAYLOAD_SECRET_HEX": payload_build_secret.hex()},
        capture_output=True,
        text=True,
        check=False,
    )
    check("deploy CLI refuses APPLY without RESTORE artifact", result.returncode == 2 and "without --restore-artifact" in result.stderr, result.stderr.strip())
    check("refused deploy CLI APPLY never emits payload", not (run_dir / "payload-apply.bin").exists())

print(f"\n== RESULT: {passed} passed, {failed} failed ==")
if failed:
    raise SystemExit(1)
