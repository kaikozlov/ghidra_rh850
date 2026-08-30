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
from exploit.dumper.dump_codeflash import DumpRunError, LiveDumpCollector, load_audited_shellcode

passed = failed = 0


def check(name: str, condition: object, detail: str = "") -> None:
    global passed, failed
    ok = bool(condition)
    passed += int(ok)
    failed += int(not ok)
    suffix = f" ({detail})" if detail else ""
    print(f"[{'PASS' if ok else 'FAIL'}] {name}{suffix}")


print("== protocol namespace and framing ==")
hello, start, length, word_count = startup_frames()
check("HELLO decodes protocol version", decode_frame(hello).kind is FrameKind.HELLO and decode_frame(hello).value == PROTOCOL_VERSION)
check("range start decodes", decode_frame(start).kind is FrameKind.RANGE_START and decode_frame(start).value == CODEFLASH_BASE)
check("range length decodes", decode_frame(length).kind is FrameKind.RANGE_LENGTH and decode_frame(length).value == CODEFLASH_SIZE)
check("startup announces exact word count", decode_frame(word_count).kind is FrameKind.WORD_COUNT and decode_frame(word_count).value == WORD_COUNT)
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
r_full.feed(startup_frames()[3])
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

print("\n== live payload and wrapper structure ==")
dumper_c = (REPO / "exploit" / "dumper" / "main.c").read_text(encoding="utf-8").lower()
wrapper_py = (REPO / "exploit" / "dumper" / "dump_codeflash.py").read_text(encoding="utf-8").lower()
builder_py = (REPO / "exploit" / "dumper" / "build_shellcode.py").read_text(encoding="utf-8").lower()
check("read payload advertises exact CodeFlash range", all(token in dumper_c for token in ("0x00000000u", "0x00100000u", "codeflash_words")))
check("read payload emits addressed words, not sequential naked bytes", "send_frame(address, word)" in dumper_c)
check("read payload emits word-count and DONE controls", "ctrl_word_count" in dumper_c and "send_frame(ctrl_done, count)" in dumper_c)
check("read payload does not call unverified boot-RAM watchdog helpers", "0xfebf1188" not in dumper_c and "0xfebf11ac" not in dumper_c and "0xfebf11d2" not in dumper_c)
check("read payload contains no automatic reset", "reset(" not in dumper_c and "0x157e" not in dumper_c)
ready_wait = dumper_c.index("tx_ready_mask")
message_write = dumper_c.index("*(tmptr", ready_wait)
submit = dumper_c.index("*(tmc", message_write)
result_wait = dumper_c.index("tx_result_mask", submit)
status_clear = dumper_c.index("& 0xf9u", result_wait)
check("read payload waits for field-proven F33 callback idle mask before message RAM writes", ready_wait < message_write and "tx_ready_mask          0x06u" in dumper_c)
check("read payload waits for a completion result only after TMTR", submit < result_wait < status_clear)
check("read payload clears any nonzero callback completion without stock CanIf reclassification", "tx_result_success_mask" not in dumper_c and "status & 0xf9u" in dumper_c)
check("read payload bounds ready/completion waits", all(token in dumper_c for token in ("tx_spin_limit", "transport_fault_halt")))
check("read payload latches terminal Tx fault code/detail in RAM", "runtime_tx_fault" in dumper_c and "runtime_tx_detail" in dumper_c)
check("dumper compiler disables null-deref deletion", "-fno-delete-null-pointer-checks" in builder_py)
check("dumper links at authenticated callback VMA", "-ttext=0x{payload_load_addr:08x}" in builder_py and "payload_load_addr" in builder_py)
check("live wrapper authenticates shellcode before RAM upload", "package_shellcode" in wrapper_py and "cmac_valid" in wrapper_py and "crc_residue" in wrapper_py)
check("live wrapper requires the tracked audited executable identity", "load_audited_shellcode" in wrapper_py and "audited_build.json" in wrapper_py)
check("live wrapper keeps payload-build and SecurityAccess secrets separate", "load_payload_secret" in wrapper_py and "load_security_secret" in wrapper_py)
check("live wrapper persists partial acquisition on interrupt", "except keyboardinterrupt" in wrapper_py and "allow_partial=true" in wrapper_py)
check("complete live dump feeds semantic resolver by default", "resolve_secoc_patch_image.sh" in wrapper_py and "--no-resolve" in wrapper_py)
check("live wrapper never imports patcher write code", "exploit.patcher" not in wrapper_py)

print("\n== audited executable provenance ==")
tracked_audit_path = REPO / "exploit" / "dumper" / "audited_build.json"
tracked_audit = json.loads(tracked_audit_path.read_text(encoding="utf-8"))
source_bindings = {item["path"]: item["sha256"] for item in tracked_audit["sources"]}
check("tracked audit is explicitly reviewed read-only", tracked_audit["review_status"] == "audited-read-only")
check("tracked audit pins a full executable SHA and size", len(tracked_audit["shellcode"]["sha256"]) == 64 and tracked_audit["shellcode"]["size"] > 0)
check("tracked audit pins exact dumper source", source_bindings["exploit/dumper/main.c"] == hashlib.sha256((REPO / "exploit/dumper/main.c").read_bytes()).hexdigest())
check("tracked audit pins exact build script", source_bindings["exploit/dumper/build_shellcode.py"] == hashlib.sha256((REPO / "exploit/dumper/build_shellcode.py").read_bytes()).hexdigest())
check("tracked audit pins Docker image content ID", tracked_audit["toolchain"]["image_id"].startswith("sha256:") and len(tracked_audit["toolchain"]["image_id"]) == 71)

with tempfile.TemporaryDirectory() as td:
    temp = Path(td)
    shellcode_path = temp / "dumper.bin"
    shellcode_path.write_bytes(b"audited deterministic shellcode")
    binary_sha = hashlib.sha256(shellcode_path.read_bytes()).hexdigest()
    toolchain = {"backend": "test", "image_id": "sha256:" + "ab" * 32}
    audit = {
        "schema": "p1me-codeflash-dumper-audited-build-v1",
        "review_status": "audited-read-only",
        "sources": [
            {"path": "exploit/dumper/main.c", "sha256": hashlib.sha256((REPO / "exploit/dumper/main.c").read_bytes()).hexdigest()},
            {"path": "exploit/dumper/build_shellcode.py", "sha256": hashlib.sha256((REPO / "exploit/dumper/build_shellcode.py").read_bytes()).hexdigest()},
        ],
        "shellcode": {"sha256": binary_sha, "size": shellcode_path.stat().st_size, "entry_offset": 0},
        "toolchain": toolchain,
    }
    audit_path = temp / "audit.json"
    audit_path.write_text(json.dumps(audit), encoding="utf-8")
    metadata_path = shellcode_path.with_suffix(".bin.json")
    metadata = {
        "schema": "p1me-codeflash-dumper-shellcode-v1",
        "sha256": binary_sha,
        "size": shellcode_path.stat().st_size,
        "entry_offset": 0,
        "read_only": True,
        "source": "exploit/dumper/main.c",
        "source_sha256": audit["sources"][0]["sha256"],
        "toolchain": toolchain,
    }
    metadata_path.write_text(json.dumps(metadata), encoding="utf-8")
    loaded, _, _ = load_audited_shellcode(shellcode_path, audit_path=audit_path)
    check("exact audited executable and provenance are accepted", loaded == shellcode_path.read_bytes())
    shellcode_path.write_bytes(loaded + b"tamper")
    try:
        load_audited_shellcode(shellcode_path, audit_path=audit_path)
    except DumpRunError as exc:
        check("executable tampering is rejected before packaging", "executable hash/size" in str(exc), str(exc))
    else:
        check("executable tampering is rejected before packaging", False)
    shellcode_path.write_bytes(loaded)
    metadata["toolchain"] = {"backend": "different"}
    metadata_path.write_text(json.dumps(metadata), encoding="utf-8")
    try:
        load_audited_shellcode(shellcode_path, audit_path=audit_path)
    except DumpRunError as exc:
        check("toolchain provenance mismatch is rejected", "metadata disagrees" in str(exc), str(exc))
    else:
        check("toolchain provenance mismatch is rejected", False)

print("\n== live collector start/noise semantics ==")
with tempfile.TemporaryDirectory() as td:
    capture = Path(td) / "frames.ndjson"
    collector = LiveDumpCollector(capture)
    try:
        # UDS response chatter on 0x7A9 may precede payload HELLO and must not poison reconstruction.
        check("collector ignores pre-HELLO non-protocol frame", collector.feed(b"\x03\x7f\x31\x78\x00\x00\x00\x00") is False and collector.ignored_prehello == 1)
        check("collector starts only on HELLO", collector.feed(startup_frames()[0]) is False and collector.started)
        for frame in startup_frames()[1:]:
            collector.feed(frame)
        collector.feed(encode_data(0, 0x11223344))
        check("collector records addressed data after HELLO", collector.reassembler.unique_words == 1 and collector.accepted_frames == 5)
        check("collector stops on DONE even when host later detects incompleteness", collector.feed(encode_control(CTRL_DONE, WORD_COUNT)) is True and not collector.reassembler.complete)
    finally:
        collector.close()
    rows = [json.loads(line) for line in capture.read_text(encoding="utf-8").splitlines()]
    check("pre-HELLO noise is not persisted as dump data", len(rows) == 6 and rows[0]["data"] == startup_frames()[0].hex())

print(f"\n== RESULT: {passed} passed, {failed} failed ==")
if failed:
    raise SystemExit(1)
