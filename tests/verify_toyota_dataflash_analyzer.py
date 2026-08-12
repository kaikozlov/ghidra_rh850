#!/usr/bin/env python3
"""Verify the generic Toyota DataFlash structural/key-domain analyzer."""

from __future__ import annotations

import csv
import json
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from tools.analyze_toyota_dataflash import (  # noqa: E402
    DEFAULT_BASE,
    REFERENCE_DUMP,
    REFERENCE_OUTPUT,
    analyze,
    analyze_triplicate_objects,
    entropy_ranked_windows,
    scan_key_domains,
    sha256,
    short_block_additive_checksum,
)
from tools.toyota_secoc_oracle import load_capture  # noqa: E402
from tools.toyota_secoc_signer import sign_classic_frame, sign_sync_frame  # noqa: E402

passed = failed = 0


def check(name: str, condition: object, detail: str = "") -> None:
    global passed, failed
    ok = bool(condition)
    passed += int(ok)
    failed += int(not ok)
    suffix = f" ({detail})" if detail else ""
    print(f"[{'PASS' if ok else 'FAIL'}] {name}{suffix}")


print("== committed 4512000 structural reference ==")
rebuilt = analyze(REFERENCE_DUMP, rank_limit=24)
committed = json.loads(REFERENCE_OUTPUT.read_text(encoding="utf-8"))
check("committed structural artifact equals rebuild", committed == rebuilt)
check("reference dump is 32 KiB", rebuilt["size"] == 0x8000)
check("all 32753 sliding windows are considered", rebuilt["entropy_windows"]["sliding_window_count"] == 32753)
check("entropy ranking is descending", all(
    a["entropy"] >= b["entropy"]
    for a,b in zip(rebuilt["entropy_windows"]["ranked"], rebuilt["entropy_windows"]["ranked"][1:])
))
objects = {row["object"]: row for row in rebuilt["triplicate_objects"]}
for object_id in (0,1,2,3,5,6):
    check(f"reference object {object_id} has three valid consensus copies",
          objects[object_id]["valid_copy_count"] == 3 and objects[object_id]["valid_consensus"])
for object_id in (4,12,13,14,15):
    check(f"reference object {object_id} has no valid copy", objects[object_id]["valid_copy_count"] == 0)
obj15 = objects[15]
check("object15 raw key field geometry is FF206E14", obj15["known_key_field_geometry"]["raw"] == "0xFF206E14")
check("object15 XOR55 key field geometry is FF206D14", obj15["known_key_field_geometry"]["xor55"] == "0xFF206D14")
check("object15 XORAA key field geometry is FF206C14", obj15["known_key_field_geometry"]["xoraa"] == "0xFF206C14")
check("object15 geometry aligns with related 4514000 observation", obj15["known_key_field_geometry"]["geometry_alignment"] is True)
check("object15 runtime key equivalence is not invented", obj15["known_key_field_geometry"]["runtime_key_equivalence"] == "unproven")
check(
    "short-block additive checksum is reader-enforced",
    "0x7668A" in rebuilt["physical_validity_model"]["short_block_integrity"]
    and rebuilt["physical_validity_model"]["short_block_mismatch_result"] == "0xFFFC",
)
check(
    "long blocks remain outside the short-block checksum rule",
    "skips the short-block checksum" in rebuilt["physical_validity_model"]["long_block_header"],
)

print("\n== synthetic valid object15 triplicate ==")
layout = list(csv.DictReader((REPO / "data/dataflash_nvm_records.csv").open()))
reference = bytearray(REFERENCE_DUMP.read_bytes())
key = bytes.fromhex("00112233445566778899aabbccddeeff")
payload = bytes.fromhex("a55a5aa5000000001122334455667788") + key
masks = {"raw":0x00,"xor55":0x55,"xoraa":0xAA}
for row in layout:
    if row["secoc_object"] != "15":
        continue
    start = int(row["va_start"],0) - DEFAULT_BASE
    alloc = int(row["allocation_bytes"])
    storage = int(row["storage_index"])
    reference[start:start+2] = storage.to_bytes(2,"little")
    mask = masks[row["copy_encoding"]]
    encoded_payload = bytes(value ^ mask for value in payload)
    reference[start+4:start+36] = encoded_payload
    reference[start+2:start+4] = short_block_additive_checksum(storage, encoded_payload).to_bytes(2,"little")
    reference[start+36:start+alloc-4] = bytes([mask]) * (alloc-40)
    reference[start+alloc-4:start+alloc] = b"\xaa"*4
synthetic_objects = {row["object"]: row for row in analyze_triplicate_objects(bytes(reference))}
s15 = synthetic_objects[15]
check("synthetic object15 recognizes all three physical copies as valid", s15["valid_copy_count"] == 3)
check("synthetic object15 decodes raw/XOR55/XORAA to one payload", s15["all_decoded_copies_equal"] and s15["valid_consensus"])
check("synthetic object15 consensus hash matches decoded payload", s15["consensus_payload_sha256"] == sha256(payload))
check("all three decoded object15 second fields hash to the same key", len({copy["second_field_sha256"] for copy in s15["copies"]}) == 1 and s15["copies"][0]["second_field_sha256"] == sha256(key))
check("synthetic object15 short checksums validate", all(copy["header_word1_matches_expected"] for copy in s15["copies"]))
check("synthetic object15 marks the short checksum as reader-enforced", all(copy["header_word1_reader_enforced"] for copy in s15["copies"]))

print("\n== key-domain classification ==")
TRIP, RESET = 0x1234, 0x56789
SYNC_KEY = bytes.fromhex("100102030405060708090a0b0c0d0e0f")
K116 = bytes.fromhex("201112131415161718191a1b1c1d1e1f")
K24D = bytes.fromhex("302122232425262728292a2b2c2d2e2f")
COMMON = bytes.fromhex("403132333435363738393a3b3c3d3e3f")
ALL = bytes.fromhex("504142434445464748494a4b4c4d4e4f")


def capture_for(path: Path, sync_key: bytes, k116: bytes, k24d: bytes) -> tuple[list, list]:
    rows = [
        {"addr":0x0F,"bus":1,"data":sign_sync_frame(sync_key,TRIP,RESET).hex()},
        {"addr":0x116,"bus":1,"data":sign_classic_frame(k116,0x116,b"\x01\x02\x03\x04",TRIP,RESET,0x25).hex()},
        {"addr":0x116,"bus":1,"data":sign_classic_frame(k116,0x116,b"\x05\x06\x07\x08",TRIP,RESET,0x29).hex()},
        {"addr":0x24D,"bus":1,"data":sign_classic_frame(k24d,0x24D,b"\x10\x20\x30\x40",TRIP,RESET,0x32).hex()},
        {"addr":0x24D,"bus":1,"data":sign_classic_frame(k24d,0x24D,b"\x11\x21\x31\x41",TRIP,RESET,0x36).hex()},
    ]
    path.write_text("\n".join(json.dumps(row) for row in rows)+"\n")
    sync, protected, _ = load_capture(path)
    return sync, protected


def tiny_dump(keys: list[tuple[int,bytes]]) -> bytes:
    blob = bytearray((i*73+19)&0xff for i in range(320))
    for offset,k in keys: blob[offset:offset+16]=k
    return bytes(blob)

with tempfile.TemporaryDirectory() as td:
    root=Path(td)
    # Three independent domains.
    sync, protected = capture_for(root/'independent.ndjson', SYNC_KEY, K116, K24D)
    scan = scan_key_domains(tiny_dump([(17,SYNC_KEY),(83,K116),(149,K24D)]), sync, protected, min_entropy=0.0)
    found={row["offset"]:row for row in scan["matches"]}
    check("domain scan finds sync-only key", found[17]["classification"] == "sync only")
    check("domain scan finds 0x116-only key", found[83]["classification"] == "0x116 only")
    check("domain scan finds 0x24D-only key", found[149]["classification"] == "0x24D only")

    # One protected key across two IDs, separate sync key.
    sync, protected = capture_for(root/'protected_common.ndjson', SYNC_KEY, COMMON, COMMON)
    scan = scan_key_domains(tiny_dump([(31,SYNC_KEY),(121,COMMON)]), sync, protected, min_entropy=0.0)
    found={row["offset"]:row for row in scan["matches"]}
    check("domain scan classifies common 0x116+0x24D key", found[121]["classification"] == "common 0x116+0x24D")
    check("common protected key records both IDs", found[121]["protected_ids_passing"] == ["0x116","0x24D"])

    # One key for synchronization and protected traffic.
    sync, protected = capture_for(root/'all_common.ndjson', ALL, ALL, ALL)
    scan = scan_key_domains(tiny_dump([(57,ALL)]), sync, protected, min_entropy=0.0)
    found={row["offset"]:row for row in scan["matches"]}
    check("domain scan classifies common sync+protected key", found[57]["classification"] == "common sync+protected")
    check("common sync key records both protected IDs", found[57]["protected_ids_passing"] == ["0x116","0x24D"])

print("\n== no raw key disclosure ==")
serialized=json.dumps(committed)
check("reference structural artifact does not expose the synthetic key", key.hex() not in serialized)
check("candidate ranking exposes hashes rather than raw bytes", all("sha256" in row and "key" not in row for row in committed["entropy_windows"]["ranked"]))

print(f"\n== RESULT: {passed} passed, {failed} failed ==")
if failed:
    raise SystemExit(1)
