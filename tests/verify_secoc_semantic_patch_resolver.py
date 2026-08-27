#!/usr/bin/env python3
"""Verify the calibration-independent SecOC semantic patch resolver workflow."""

from __future__ import annotations

import copy
import json
import struct
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from tools.build_secoc_patch_manifest import (
    CONCATENATED_DUMP_SIZE,
    EXPECTED_CRC_RESIDUE,
    P1M_E_CODEFLASH_SIZE,
    VALIDITY_MARKER,
    build_manifest,
    crc32,
    discover_crc_descriptors,
    validate_codeflash_geometry,
)

passed = failed = 0


def check(name: str, condition: object, detail: str = "") -> None:
    global passed, failed
    ok = bool(condition)
    passed += int(ok)
    failed += int(not ok)
    suffix = f" ({detail})" if detail else ""
    print(f"[{'PASS' if ok else 'FAIL'}] {name}{suffix}")


cf_path = REPO / "firmware" / "RH850_P1M-E_CodeFlash.bin"
resolution_path = REPO / "data" / "generated" / "secoc_gate_resolution_4512000.json"
minimal_resolution_path = REPO / "data" / "generated" / "secoc_gate_resolution_4512000_minimal.json"
manifest_path = REPO / "data" / "generated" / "secoc_patch_manifest_4512000.json"
resolution = json.loads(resolution_path.read_text(encoding="utf-8"))
minimal_resolution = json.loads(minimal_resolution_path.read_text(encoding="utf-8"))
committed_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

print("== semantic resolver has no Sienna target constants ==")
java_path = REPO / "ghidra" / "scripts" / "investigate" / "ResolveSecocAcceptanceGate.java"
java = java_path.read_text(encoding="utf-8").lower()
for forbidden, label in (
    ("8e6c6", "known Gate-2 CMP patch VA"),
    ("8e6c8", "known adjacent Gate-2 BNE VA"),
    ("febe555c", "known MAC-result global"),
    ("8e67a", "known acceptance-function entry"),
    ("ffdec", "known CRC fixup VA"),
    ("18000", "known high CRC start"),
    ("ffe00", "known high validity-marker VA"),
):
    check(f"resolver source does not embed {label}", forbidden not in java)
for token, label in (
    ("getfunctions(true)", "whole-function census"),
    ("hasparamreference(sourceglobal)", "result output passed-by-address invariant"),
    ("cmovne", "boolean materialization"),
    ("findfallthroughjoin", "verified/mismatch convergence"),
    ("candidates.size() != 1", "fail-closed uniqueness"),
    ("neutralizecmp", "local CMP neutralization synthesis"),
):
    check(f"resolver implements {label}", token in java)
check("resolver is read-only", "saveprogram" not in java and "setname(" not in java and "createfunction(" not in java)

seeder_path = REPO / "ghidra" / "scripts" / "investigate" / "SeedSecocAcceptanceGateCandidates.java"
seeder = seeder_path.read_text(encoding="utf-8").lower()
for forbidden, label in (("8e6c6", "Sienna Gate-2 VA"), ("88c62", "H/F Gate-2 VA"), ("8f952", "F33 Gate-2 VA")):
    check(f"candidate seeder does not embed {label}", forbidden not in seeder)
check("candidate seeder uses a machine anchor only to recover function ownership",
      "gate_anchor" in seeder and "gate_offset_from_owner" in seeder and "createfunction(" in seeder)
check("candidate seeder fails closed on ambiguous anchors", "hits.size() != 1" in seeder and "fail_closed" in seeder)

anchor = bytes.fromhex("e0d19a0d1a38bfff")
anchor_fixtures = (
    (cf_path, 0x8E6C6, "Sienna 8965B4512000"),
    (REPO / "community/albinoelephant/normalized/8965H1202000_CodeFlash.bin", 0x88C62, "Corolla H"),
    (REPO / "community/spanconstant/raw-20260821/span-corolla-2025.20260821-1511/dump_codeflash_00000000_00200000_20260821-152033.bin", 0x88C62, "Corolla F"),
    (REPO / "community/kai/camry-2026/normalized/8965F3307000_CodeFlash.bin", 0x8F952, "Camry F33"),
)
for path, expected, label in anchor_fixtures:
    blob = path.read_bytes()[:P1M_E_CODEFLASH_SIZE]
    hits = [off for off in range(len(blob)) if blob.startswith(anchor, off)]
    check(f"Gate-2 machine anchor is unique on retained {label}", hits == [expected])

print("\n== committed semantic result ==")
check("semantic scan resolved exactly one candidate", resolution["candidate_count"] == 1 and resolution["resolution"] == "unique")
check("fixture independently rediscovered known Gate-2 VA", int(resolution["patch"]["address"], 0) == 0x8E6C6)
check("fixture independently rediscovered MAC-result global", int(resolution["mac_result_source"]["address"], 0) == 0xFEBE555C)
check("fixture synthesizes corrected CMP neutralization", resolution["patch"]["original"] == "e0d1" and resolution["patch"]["replacement"] == "e001" and resolution["patch"]["operation"] == "cmp-second-register-to-first-force-fallthrough")
check("fixture proves pre-gate state call precedes patch", int(resolution["pre_gate_state_call"], 0) < int(resolution["patch"]["address"], 0))
check("fixture pins zero-is-verified result polarity", resolution["verify_result_polarity"] == "zero-is-verified-ok-nonzero-is-not-verified")
check("fixture preserves the BNE and names both corrected arms", resolution["control_flow"]["bne"] == "0x0008e6c8" and resolution["control_flow"]["bne_bytes"] == "9a0d" and resolution["control_flow"]["verified_delivery_fallthrough"] == "0x0008e6ca" and resolution["control_flow"]["mismatch_branch_target"] == "0x0008e6da")
check("fixture has calls on both verified and mismatch arms", resolution["control_flow"]["verified_fallthrough_calls"] >= 1 and resolution["control_flow"]["mismatch_branch_calls"] >= 1)
check("semantic result is bound to exact CodeFlash SHA", resolution["program_sha256"] == committed_manifest["image"]["sha256"])

print("\n== bare CodeFlash-only import portability fixture ==")
check("minimal unannotated import still resolves uniquely", minimal_resolution["candidate_count"] == 1 and minimal_resolution["resolution"] == "unique")
check("minimal import resolves the same patch address", minimal_resolution["patch"]["address"] == resolution["patch"]["address"])
check("minimal import synthesizes the same replacement", minimal_resolution["patch"]["replacement"] == resolution["patch"]["replacement"])
check("minimal import is bound to the same input image SHA", minimal_resolution["program_sha256"] == resolution["program_sha256"])
check("minimal import explicitly reports unmapped RAM provenance", minimal_resolution["mac_result_source"]["address"] is None and minimal_resolution["mac_result_source"]["resolution"] == "unmapped-on-current-import")
check("annotated import upgrades result provenance", resolution["mac_result_source"]["passed_by_address_elsewhere"] is True)

print("\n== arbitrary-image workflow contract ==")
image_wrapper = (REPO / "tools" / "resolve_secoc_patch_image.sh").read_text(encoding="utf-8")
check("arbitrary-image workflow uses a disposable build workspace", "build/work/secoc-targets" in image_wrapper)
check("arbitrary-image workflow performs a raw RH850/P1M-E import", "-import \"$IMAGE\"" in image_wrapper and "v850e3:LE:32:default" in image_wrapper)
check("arbitrary-image workflow seeds undiscovered Gate-2 owners before semantic resolution",
      "SeedSecocAcceptanceGateCandidates.java" in image_wrapper
      and image_wrapper.index("SeedSecocAcceptanceGateCandidates.java") < image_wrapper.index("ResolveSecocAcceptanceGate.java"))
check("arbitrary-image workflow runs the semantic resolver", "ResolveSecocAcceptanceGate.java" in image_wrapper)
check("arbitrary-image workflow opts into investigate scripts explicitly", "--with-investigate" in image_wrapper)
check("arbitrary-image workflow contains no input-image write primitive", "dd " not in image_wrapper and "ghidra patch" not in image_wrapper.lower() and '> "$IMAGE"' not in image_wrapper)

print("\n== manifest rebuild and dynamic CRC discovery ==")
rebuilt = build_manifest(resolution, cf_path, 0)
check("committed manifest equals deterministic rebuild", committed_manifest == rebuilt)
check("manifest verifies patch preimage", rebuilt["patch"]["preimage_verified"] is True)
check("CRC descriptor scan finds exactly two self-describing records", rebuilt["discovery"]["crc_descriptor_count"] == 2)
check("exactly one discovered CRC region covers the semantic patch", int(rebuilt["boot_crc"]["start"], 0) <= int(rebuilt["patch"]["address"], 0) < int(rebuilt["boot_crc"]["end"], 0))
check("CRC fixup is derived as final word of discovered region", int(rebuilt["boot_crc"]["fixup_va"], 0) == int(rebuilt["boot_crc"]["end"], 0) - 4)
check("public-dump anomaly is surfaced, not silently accepted", rebuilt["boot_crc"]["stock_region_valid"] is False)
check("valid sibling descriptor proves terminal-fixup scheme", rebuilt["boot_crc"]["validated_sibling_descriptor_count"] >= 1)
check("live policy explicitly recomputes from live CodeFlash", "live CodeFlash" in rebuilt["boot_crc"]["live_policy"])
check("offline supplied-image resigning self-checks", rebuilt["boot_crc"]["patched_residue_for_supplied_image"] == "0xFFFFFFFF")

print("\n== reconstructed clean Sienna image is handled without resolver changes ==")
with tempfile.TemporaryDirectory() as td:
    repaired_path = Path(td) / "repaired.bin"
    repaired = bytearray(cf_path.read_bytes())
    repaired[0xBB1C4] = 0x82  # SECOC-044 artifact reconstruction; resolver is unchanged.
    repaired_path.write_bytes(repaired)
    repaired_resolution = copy.deepcopy(resolution)
    import hashlib
    repaired_resolution["program_sha256"] = hashlib.sha256(repaired).hexdigest()
    clean = build_manifest(repaired_resolution, repaired_path, 0)
    check("reconstructed stock target CRC region validates", clean["boot_crc"]["stock_region_valid"] is True)
    check("clean-image Gate-2 fixup is recovered dynamically", clean["boot_crc"]["patched_fixup_for_supplied_image"] == "0x41C90FF2")
    check("clean-image patched residue is 0xFFFFFFFF", clean["boot_crc"]["patched_residue_for_supplied_image"] == "0xFFFFFFFF")

print("\n== generic synthetic CRC descriptor fixture ==")
blob = bytearray(b"\xA5" * 0x400)
region_start = 0x100
region_len = 0x80
region_end = region_start + region_len
fixup = region_end - 4
embedded_start = 0x300
embedded_len = 0x304
struct.pack_into("<II", blob, 0x20, region_start, region_len)
struct.pack_into("<II", blob, 0x28, embedded_start, embedded_len)
struct.pack_into("<I", blob, embedded_start, region_start)
struct.pack_into("<I", blob, embedded_len, region_len)
for i in range(region_start, fixup):
    blob[i] = ((i * 37) ^ (i >> 2)) & 0xFF
synthetic_prefix = crc32(blob[region_start:fixup])
struct.pack_into("<I", blob, fixup, synthetic_prefix ^ 0xFFFFFFFF)
struct.pack_into("<I", blob, region_end + 0x0C, VALIDITY_MARKER)
descs = discover_crc_descriptors(bytes(blob), 0)
check("generic descriptor recognizer finds synthetic record without Sienna geometry", len(descs) == 1)
if descs:
    d = descs[0]
    check("synthetic descriptor validates terminal CRC construction", d.terminal_fixup_valid and d.full_crc == EXPECTED_CRC_RESIDUE)
    check("synthetic validity marker location is discovered by trailer scan", d.validity_marker_va == region_end + 0x0C)

print("\n== fail-closed image geometry and provenance ==")
cf_bytes = cf_path.read_bytes()
dataflash_path = REPO / "firmware" / "RH850_P1M-E_DataFlash.bin"
check("committed CodeFlash image has the expected 1 MiB geometry", len(cf_bytes) == P1M_E_CODEFLASH_SIZE == 0x100000)
check("DataFlash prefix fixture is the 0x8000 concatenation prefix", dataflash_path.stat().st_size == 0x8000)
try:
    validate_codeflash_geometry(len(cf_bytes))
    check("exact 1 MiB CodeFlash geometry is accepted", True)
except ValueError as exc:
    check("exact 1 MiB CodeFlash geometry is accepted", False, str(exc))
for size, label in (
    (0, "empty image"),
    (0x8000, "DataFlash-only image"),
    (0x80000, "half-size truncated image"),
    (0xFFFFF, "one-byte-truncated image"),
    (0x100008, "oversized image"),
):
    try:
        validate_codeflash_geometry(size)
    except ValueError as exc:
        check(f"{label} geometry is rejected", "expected exactly" in str(exc), str(exc))
    else:
        check(f"{label} geometry is rejected", False)
try:
    validate_codeflash_geometry(CONCATENATED_DUMP_SIZE)
except ValueError as exc:
    check(
        "0x108000 DataFlash+CodeFlash concatenation is rejected with explicit diagnosis",
        "DataFlash" in str(exc) and "0x8000" in str(exc) and "strip" in str(exc),
        str(exc),
    )
else:
    check("0x108000 DataFlash+CodeFlash concatenation is rejected with explicit diagnosis", False)
with tempfile.TemporaryDirectory() as td:
    concat_path = Path(td) / "concat.bin"
    concat_path.write_bytes(dataflash_path.read_bytes() + cf_bytes)
    check("concatenated fixture is exactly 0x108000 bytes", concat_path.stat().st_size == CONCATENATED_DUMP_SIZE == 0x108000)
    try:
        build_manifest(resolution, concat_path, 0)
    except ValueError as exc:
        check("manifest builder rejects concatenated dump before any resolution logic", "DataFlash+CodeFlash concatenated" in str(exc), str(exc))
    else:
        check("manifest builder rejects concatenated dump before any resolution logic", False)
    truncated_path = Path(td) / "truncated.bin"
    truncated_path.write_bytes(cf_bytes[:-0x100])
    try:
        build_manifest(resolution, truncated_path, 0)
    except ValueError as exc:
        check("manifest builder rejects truncated image on geometry", "unexpected CodeFlash image geometry" in str(exc), str(exc))
    else:
        check("manifest builder rejects truncated image on geometry", False)
    check("valid manifest rebuild still succeeds after geometry gate", build_manifest(resolution, cf_path, 0) == committed_manifest)
wrapper = (REPO / "tools" / "resolve_secoc_patch_image.sh").read_text(encoding="utf-8")
check("arbitrary-image wrapper gates geometry before the Ghidra import", "validate_codeflash_geometry" in wrapper and wrapper.index("validate_codeflash_geometry") < wrapper.index('-import "$IMAGE"'))
check("arbitrary-image wrapper diagnoses the concatenated dump by name", "DataFlash+CodeFlash concatenated" in wrapper or "validate_codeflash_geometry" in wrapper)

print("\n== fail-closed image/preimage behavior ==")
sha_mismatch = copy.deepcopy(resolution)
sha_mismatch["program_sha256"] = "00" * 32
try:
    build_manifest(sha_mismatch, cf_path, 0)
except ValueError as exc:
    check("resolver/image SHA mismatch is rejected", "SHA-256 mismatch" in str(exc), str(exc))
else:
    check("resolver/image SHA mismatch is rejected", False)

bad_resolution = copy.deepcopy(resolution)
bad_resolution["patch"]["original"] = "0000"
try:
    build_manifest(bad_resolution, cf_path, 0)
except ValueError as exc:
    check("wrong semantic patch bytes are rejected before deployment", "same-register RH850 CMP" in str(exc), str(exc))
else:
    check("wrong semantic patch bytes are rejected before deployment", False)

old_direction = copy.deepcopy(resolution)
old_direction["patch"] = {
    "address": "0x0008e6c8",
    "original": "9a0d",
    "replacement": "950d",
    "operation": "bne-to-unconditional-br-preserve-target",
}
try:
    build_manifest(old_direction, cf_path, 0)
except ValueError as exc:
    check("superseded branch-to-mismatch patch is rejected semantically", "operation" in str(exc), str(exc))
else:
    check("superseded branch-to-mismatch patch is rejected semantically", False)

masqueraded_old_direction = copy.deepcopy(old_direction)
masqueraded_old_direction["patch"]["operation"] = "cmp-second-register-to-first-force-fallthrough"
masqueraded_old_direction["control_flow"]["gate_cmp"] = "0x0008e6c8"
try:
    build_manifest(masqueraded_old_direction, cf_path, 0)
except ValueError as exc:
    check("old branch bytes cannot masquerade as CMP neutralization", "same-register RH850 CMP" in str(exc), str(exc))
else:
    check("old branch bytes cannot masquerade as CMP neutralization", False)

wrong_bne_target = copy.deepcopy(resolution)
wrong_bne_target["control_flow"]["mismatch_branch_target"] = "0x0008e6dc"
try:
    build_manifest(wrong_bne_target, cf_path, 0)
except ValueError as exc:
    check("tampered mismatch target is rejected against encoded BNE", "encoded BNE target" in str(exc), str(exc))
else:
    check("tampered mismatch target is rejected against encoded BNE", False)

wrong_fallthrough = copy.deepcopy(resolution)
wrong_fallthrough["control_flow"]["verified_delivery_fallthrough"] = "0x0008e6cc"
try:
    build_manifest(wrong_fallthrough, cf_path, 0)
except ValueError as exc:
    check("tampered verified fallthrough is rejected", "BNE fallthrough" in str(exc), str(exc))
else:
    check("tampered verified fallthrough is rejected", False)

print(f"\n== RESULT: {passed} passed, {failed} failed ==")
if failed:
    raise SystemExit(1)
