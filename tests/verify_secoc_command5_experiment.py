#!/usr/bin/env python3
"""Verify the bounded application-context selector-4 command-5 experiment."""

from __future__ import annotations

import copy
import hashlib
import json
import struct
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from exploit.command5.build_experiment import (
    EXPECTED_RESIDUE,
    FCU_BLOCK_SIZE,
    MUTATIONS,
    TARGET_BLOCK_BASE,
    ExperimentBuildError,
    build_plan,
)
from exploit.command5.stimulus import (
    COMMAND5_MODE,
    COMMAND5_SELECTOR,
    DEFAULT_ROUNDS,
    StimulusError,
    build_input_frames,
    build_stimulus_plan,
    parse_selector3_response,
)
from tools.build_secoc_patch_manifest import crc32, discover_crc_descriptors

passed = failed = 0


def check(name: str, condition: object, detail: str = "") -> None:
    global passed, failed
    ok = bool(condition)
    passed += int(ok)
    failed += int(not ok)
    suffix = f" ({detail})" if detail else ""
    print(f"[{'PASS' if ok else 'FAIL'}] {name}{suffix}")


firmware_path = REPO / "firmware" / "RH850_P1M-E_CodeFlash.bin"
firmware = firmware_path.read_bytes()

print("== bounded instruction mutations ==")
check("experiment uses four bounded instruction mutations", len(MUTATIONS) == 4)
check("all experiment mutations fit one 32 KiB FCU block", all(TARGET_BLOCK_BASE <= m.address and m.address + len(m.original) <= TARGET_BLOCK_BASE + FCU_BLOCK_SIZE for m in MUTATIONS))
check("total changed instruction bytes is 14", sum(len(m.original) for m in MUTATIONS) == 14)
for mutation in MUTATIONS:
    observed = firmware[mutation.address:mutation.address + len(mutation.original)]
    check(f"{mutation.name} preimage matches committed firmware", observed == mutation.original, observed.hex())

by_name = {m.name: m for m in MUTATIONS}
check("activation patch is exact 4-byte tail branch", by_name["activate-bank1-after-init"].original.hex() == "40063f00" and by_name["activate-bank1-after-init"].replacement.hex() == "8007660f")
check("diagnostic copy gate patch is two-byte NOP", by_name["did1010-force-copy"].replacement == b"\x00\x00")
check("diagnostic result source patch points at generated-result buffer encoding", by_name["did1010-result-source"].replacement.hex() == "2496aa99")
check("diagnostic status source is independent from key-update source encoding", by_name["did1010-status-source"].replacement != by_name["did1010-status-source"].original)

print("\n== static dormant-harness contract ==")
check("stable-input threshold is three observations", firmware[0x30FBB] == 3, str(firmware[0x30FBB]))
# The stock finalizer must not erase the generated-result buffer before the
# diagnostic shim can observe it.
finalizer = None
for line in (REPO / "data" / "generated" / "decompilations.jsonl").open(encoding="utf-8"):
    row = json.loads(line)
    if row.get("record") == "function" and row.get("entry_addr") == "0x00068de6":
        finalizer = row
        break
check("crypto_test_bank1_finalize is present in decompiler corpus", finalizer is not None)
if finalizer is not None:
    result_writes = [
        ref
        for ref in finalizer.get("data_references", [])
        if ref.get("ref_type") == "WRITE"
        and isinstance(ref.get("to_addr"), str)
        and 0xFEBE51AA <= int(ref["to_addr"], 16) < 0xFEBE51BA
    ]
    check("stock finalizer does not clear generated-result buffer", not result_writes, repr(result_writes))
# Signal metadata table used by crypto_test_read_input_properties:
# signal 95 -> COM byte offset 0x97, 8 bits; signal 96 -> offset 0x98, 8 bits.
check("selector signal id is 95", struct.unpack_from("<H", firmware, 0x25912)[0] == 0x5F)
check("mode signal id is 96", struct.unpack_from("<H", firmware, 0x25914)[0] == 0x60)
check("selector/mode COM offsets are consecutive bytes 0x97/0x98", struct.unpack_from("<H", firmware, 0x2592E)[0] == 0x97 and struct.unpack_from("<H", firmware, 0x25930)[0] == 0x98)
check("selector/mode widths are eight bits", firmware[0x2593A] == 8 and firmware[0x2593B] == 8)
# Message/expected-result signal groups map to offsets 0x9F,0xA7,0xAF,0xB7.
check("message/result group COM offsets match 0x01C..0x01F payloads", [struct.unpack_from("<H", firmware, off)[0] for off in (0x25932, 0x25934, 0x25936, 0x25938)] == [0x9F, 0xA7, 0xAF, 0xB7])

print("\n== deterministic patch/restore builder ==")
with tempfile.TemporaryDirectory() as td:
    temp = Path(td)
    try:
        build_plan(firmware_path, temp / "refuse")
    except ExperimentBuildError as exc:
        check("live preparation rejects invalid source boot CRC", "source boot-crc descriptor is invalid" in str(exc).lower(), str(exc))
    else:
        check("live preparation rejects invalid source boot CRC", False)

    fixture_plan = build_plan(firmware_path, temp / "fixture", allow_invalid_source_crc=True)
    check("offline fixture plan records invalid source CRC rather than hiding it", fixture_plan["source_image"]["boot_crc_valid_before"] is False)
    check("fixture patched image reaches expected CRC residue", int(fixture_plan["boot_crc"]["patched_residue"], 0) == EXPECTED_RESIDUE)
    check("fixture RESTORE preserves original target-block bytes", fixture_plan["restore"]["restored_target_block_matches_source"] is True)
    check("fixture RESTORE may differ only because invalid source CRC is normalized", fixture_plan["restore"]["restored_image_matches_source"] is False)
    restore = json.loads((temp / "fixture" / "RESTORE.json").read_text(encoding="utf-8"))
    check("RESTORE artifact is explicitly validated", restore["validated"] is True and int(restore["boot_crc"]["validated_restore_residue"], 0) == EXPECTED_RESIDUE)

    repaired = bytearray(firmware)
    # Existing CRC reconstruction evidence shows the public acquisition anomaly is
    # exactly 0xBB1C4: 0x80 -> 0x82. This produces a valid source for the generic
    # safety property test without changing any command-5 mutation preimage.
    repaired[0xBB1C4] = 0x82
    descriptors = discover_crc_descriptors(bytes(repaired), 0)
    high = next(item for item in descriptors if item.start == 0x18000)
    check("synthetic repaired source has valid high boot CRC", high.terminal_fixup_valid)
    repaired_path = temp / "repaired.bin"
    repaired_path.write_bytes(repaired)
    repaired_plan = build_plan(repaired_path, temp / "repaired")
    check("valid-source plan succeeds without unsafe override", repaired_plan["source_image"]["boot_crc_valid_before"] is True)
    check("valid-source RESTORE reconstructs exact source image", repaired_plan["restore"]["restored_image_matches_source"] is True)
    patched = (temp / "repaired" / "command5_experiment_patched.bin").read_bytes()
    for mutation in MUTATIONS:
        check(f"patched image contains {mutation.name} replacement", patched[mutation.address:mutation.address + len(mutation.replacement)] == mutation.replacement)
    patched_crc = next(item for item in discover_crc_descriptors(patched, 0) if item.start == 0x18000)
    check("patched image dynamically validates boot CRC", patched_crc.terminal_fixup_valid and patched_crc.full_crc == EXPECTED_RESIDUE)

print("\n== exact CAN stimulus mapping ==")
message = bytes(range(16))
expected = bytes(range(0x80, 0x90))
frames = build_input_frames(message, expected=expected)
check("selector-4/mode-1 frame is 0x01B bytes 04 01 ...", frames[0].address == 0x01B and frames[0].data == b"\x04\x01" + b"\x00" * 6)
check("0x01C/0x01D carry the exact 16-byte command-5 message", frames[1].address == 0x01C and frames[1].data == message[:8] and frames[2].address == 0x01D and frames[2].data == message[8:])
check("0x01E/0x01F carry the exact 16-byte expected value", frames[3].address == 0x01E and frames[3].data == expected[:8] and frames[4].address == 0x01F and frames[4].data == expected[8:])
plan = build_stimulus_plan(message, expected=expected)
check("default plan uses five spaced rounds", plan["rounds"] == DEFAULT_ROUNDS == 5 and plan["round_interval_seconds"] == 0.10)
check("plan records three required stable observations", plan["stability"]["required_unchanged_observations"] == 3)
try:
    build_stimulus_plan(message, rounds=3)
except StimulusError as exc:
    check("too-few update rounds are rejected", "at least four" in str(exc), str(exc))
else:
    check("too-few update rounds are rejected", False)

print("\n== DID 0x1010 selector-3 observation parser ==")
response = b"\x6e\x03\x10\x10" + b"\x10" + bytes(range(16)) + bytes(range(32))
parsed = parse_selector3_response(response)
check("selector-3 parser exposes patched status byte", parsed["status"] == 0x10)
check("selector-3 parser extracts exactly first 16 generated-result bytes", parsed["generated_cmac"] == bytes(range(16)))
check("selector-3 parser quarantines adjacent 32 bytes", parsed["extra"] == bytes(range(32)))
try:
    parse_selector3_response(b"\x6e\x03\x10\x11" + b"\x00" * 49)
except StimulusError as exc:
    check("wrong DID/selector response prefix is rejected", "unexpected" in str(exc), str(exc))
else:
    check("wrong DID/selector response prefix is rejected", False)

print("\n== scope and interpretation discipline ==")
source = (REPO / "exploit" / "command5" / "build_experiment.py").read_text(encoding="utf-8").lower()
stimulus_source = (REPO / "exploit" / "command5" / "stimulus.py").read_text(encoding="utf-8").lower()
check("experiment patch does not contain SecOC Gate-2 target address", "8e6c8" not in source)
check("experiment patch does not import production flash backend", "flash_backend" not in source)
check("stimulus labels result as application-context evidence only", "does not prove production secoc transmit integration" in stimulus_source)
check("live stimulus keeps pre-stimulus diagnostic baseline", "result_changed_from_pre_stimulus_baseline" in stimulus_source)

print(f"\n== RESULT: {passed} passed, {failed} failed ==")
if failed:
    raise SystemExit(1)
