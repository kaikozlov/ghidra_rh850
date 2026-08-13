#!/usr/bin/env python3
"""Verify the read-only addressed-word CodeFlash dump protocol/reassembler."""

from __future__ import annotations

import hashlib
import json
import random
import struct
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from exploit.dumper.protocol import (
    CODEFLASH_BASE,
    CODEFLASH_SIZE,
    CTRL_DONE,
    CTRL_ERROR,
    CTRL_PROGRESS,
    PROTOCOL_VERSION,
    WORD_COUNT,
    DumpProtocolError,
    FrameKind,
    decode_frame,
    encode_control,
    encode_data,
    startup_frames,
)
from exploit.dumper.reassemble import CodeFlashReassembler, DumpReassemblyError, boot_crc_sanity

passed = failed = 0


def check(name: str, condition: object, detail: str = "") -> None:
    global passed, failed
    ok = bool(condition)
    passed += int(ok)
    failed += int(not ok)
    suffix = f" ({detail})" if detail else ""
    print(f"[{'PASS' if ok else 'FAIL'}] {name}{suffix}")


print("== protocol namespace and framing ==")
hello, start, length = startup_frames()
check("HELLO decodes protocol version", decode_frame(hello).kind is FrameKind.HELLO and decode_frame(hello).value == PROTOCOL_VERSION)
check("range start decodes", decode_frame(start).kind is FrameKind.RANGE_START and decode_frame(start).value == CODEFLASH_BASE)
check("range length decodes", decode_frame(length).kind is FrameKind.RANGE_LENGTH and decode_frame(length).value == CODEFLASH_SIZE)
example = encode_data(0x1234, 0xAABBCCDD)
decoded = decode_frame(example)
check("data frame round-trips address/value", decoded.kind is FrameKind.DATA and decoded.value == 0x1234 and decoded.data == 0xAABBCCDD)
check("control namespace cannot collide with CodeFlash", 0xD00D0000 > CODEFLASH_BASE + CODEFLASH_SIZE - 1)
try:
    encode_data(1, 0)
except DumpProtocolError as exc:
    check("misaligned data address is rejected by encoder", "aligned" in str(exc), str(exc))
else:
    check("misaligned data address is rejected by encoder", False)
try:
    encode_data(CODEFLASH_SIZE, 0)
except DumpProtocolError as exc:
    check("out-of-range data address is rejected by encoder", "outside" in str(exc), str(exc))
else:
    check("out-of-range data address is rejected by encoder", False)

print("\n== duplicate/conflict/completeness semantics ==")
r = CodeFlashReassembler()
for frame in startup_frames():
    r.feed(frame)
r.feed(encode_data(0, 0x11223344))
r.feed(encode_data(0, 0x11223344))
check("identical duplicate is tolerated and counted", r.unique_words == 1 and r.duplicate_words == 1)
try:
    r.feed(encode_data(0, 0x55667788))
except DumpReassemblyError as exc:
    check("conflicting duplicate is fatal", "conflicting duplicate" in str(exc), str(exc))
else:
    check("conflicting duplicate is fatal", False)
r.feed(encode_control(CTRL_DONE, WORD_COUNT))
check("DONE does not make an incomplete acquisition complete", not r.complete and r.report(include_sanity=False)["missing_word_count"] == WORD_COUNT - 1)

r_error = CodeFlashReassembler()
for frame in startup_frames():
    r_error.feed(frame)
r_error.feed(encode_control(CTRL_ERROR, 7))
check("payload error marker invalidates protocol", any("payload error" in item for item in r_error.protocol_errors()))

print("\n== out-of-order complete reconstruction from firmware truth ==")
firmware_path = REPO / "firmware" / "RH850_P1M-E_CodeFlash.bin"
firmware = firmware_path.read_bytes()
check("committed fixture is exactly 1 MiB", len(firmware) == CODEFLASH_SIZE)
indices = list(range(WORD_COUNT))
random.Random(0x4512000).shuffle(indices)
r_full = CodeFlashReassembler()
# Controls can arrive around data; only their values, not sequential placement, matter.
r_full.feed(startup_frames()[0])
r_full.feed(startup_frames()[2])
for sequence, index in enumerate(indices):
    offset = index * 4
    word = struct.unpack_from("<I", firmware, offset)[0]
    r_full.feed(encode_data(offset, word))
    if sequence in (32768, 131072, 220000):
        r_full.feed(encode_control(CTRL_PROGRESS, offset))
# Exercise an identical duplicate after the full shuffled stream.
r_full.feed(encode_data(0x100, struct.unpack_from("<I", firmware, 0x100)[0]))
r_full.feed(startup_frames()[1])
r_full.feed(encode_control(CTRL_DONE, WORD_COUNT))
report = r_full.report()
check("all addressed words reconstruct a complete image", r_full.complete and report["complete"])
check("reconstruction is byte-identical to committed firmware", bytes(r_full.image) == firmware)
check("reconstructed SHA-256 equals source truth", report["sha256"] == hashlib.sha256(firmware).hexdigest())
check("full reconstruction retains duplicate count", report["observed"]["duplicate_words"] == 1)
check("progress is telemetry only", len(report["observed"]["progress_markers"]) == 3)

sanity = report["boot_crc_sanity"]
check("boot sanity dynamically rediscovers two descriptors", sanity["descriptor_count"] == 2)
check("public Sienna artifact retains exactly one directly valid descriptor", sanity["valid_descriptor_count"] == 1)
high = next(item for item in sanity["descriptors"] if item["start"] == "0x18000")
check("high-region acquisition anomaly is observed, not repaired", high["terminal_fixup_valid"] is False and high["full_crc"] == "0x5AA2313A")

print("\n== partial persistence is explicit ==")
with tempfile.TemporaryDirectory() as td:
    temp = Path(td)
    partial = CodeFlashReassembler()
    for frame in startup_frames():
        partial.feed(frame)
    for address in (0, 4, 0x100, CODEFLASH_SIZE - 4):
        partial.feed(encode_data(address, struct.unpack_from("<I", firmware, address)[0]))
    partial.feed(encode_control(CTRL_DONE, WORD_COUNT))
    out = temp / "partial.bin"
    partial_report = partial.write_outputs(out, allow_partial=True)
    check("partial output preserves full address space with explicit gaps", len(out.read_bytes()) == CODEFLASH_SIZE and partial_report["complete"] is False)
    check("partial report never assigns a SHA to incomplete bytes", partial_report["sha256"] is None)
    check("partial report compresses missing words into ranges", partial_report["missing_word_count"] == WORD_COUNT - 4 and len(partial_report["missing_ranges"]) >= 2)
    saved_report = json.loads((temp / "partial.bin.json").read_text(encoding="utf-8"))
    check("partial missing-range report is persisted beside image", saved_report["missing_word_count"] == WORD_COUNT - 4)
    try:
        partial.write_outputs(temp / "must-not-write.bin", allow_partial=False)
    except DumpReassemblyError as exc:
        check("require-complete refuses incomplete output", "incomplete" in str(exc), str(exc))
        check("require-complete refusal creates no image", not (temp / "must-not-write.bin").exists())
    else:
        check("require-complete refuses incomplete output", False)

print("\n== physical source separation contract ==")
dumper_sources = "\n".join(
    path.read_text(encoding="utf-8").lower()
    for path in (REPO / "exploit" / "dumper").rglob("*")
    if path.is_file() and path.suffix in {".py", ".c", ".h", ".md"}
)
check("dumper workstream contains no FACI symbol", "faci_" not in dumper_sources)
check("dumper workstream does not import flash backend", "flash_backend" not in dumper_sources)
check("dumper workstream contains no flash erase/program primitive", "flash_block_rmw" not in dumper_sources and "faci_program_page" not in dumper_sources)

print(f"\n== RESULT: {passed} passed, {failed} failed ==")
if failed:
    raise SystemExit(1)
