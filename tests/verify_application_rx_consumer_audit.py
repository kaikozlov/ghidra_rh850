#!/usr/bin/env python3
"""Repository-side checks for the live-Ghidra unresolved Rx consumer audit.

The audit artifact is structural Ghidra evidence. This test independently pins
the decisive local-postprocess control flow to raw CodeFlash and checks that the
stored-only rows retain the exact bounded reference/alias disposition emitted by
the live exporter.
"""
from __future__ import annotations

from collections import Counter
import csv
from pathlib import Path
import sys

REPO = Path(__file__).resolve().parents[1]
CF = (REPO / "firmware" / "RH850_P1M-E_CodeFlash.bin").read_bytes()
AUDIT = REPO / "data" / "application_rx_consumer_audit.csv"

passed = failed = 0


def check(name: str, condition: object, detail: str = "") -> None:
    global passed, failed
    ok = bool(condition)
    passed += int(ok)
    failed += int(not ok)
    suffix = f" ({detail})" if detail else ""
    print(f"[{'PASS' if ok else 'FAIL'}] {name}{suffix}")


def b(offset: int, hex_bytes: str) -> bool:
    expected = bytes.fromhex(hex_bytes)
    return CF[offset:offset + len(expected)] == expected


with AUDIT.open(newline="", encoding="utf-8") as stream:
    rows = list(csv.DictReader(stream))
by_sid = {int(row["signal_id"]): row for row in rows}

LOCAL = {231, 233, 235, 237, 270, 273, 276}
STORED = {
    62, 70, 107, 115, 144, 173, 177, 194, 197,
    256, 257, 261, 262, 263, 278, 286, 291, 292,
}
SECOC = {62, 115, 194, 197, 270, 273, 276, 278, 286}
LOCAL_SITES = {
    231: "0x4AEEE",
    233: "0x4AF1A",
    235: "0x4AF46",
    237: "0x4AF72",
    270: "0x4B2A6",
    273: "0x4B306",
    276: "0x4B366",
}

print("== exact unresolved denominator and dispositions ==")
check("audit has exactly 25 rows", len(rows) == 25, str(len(rows)))
check("audit signal IDs are exact", set(by_sid) == LOCAL | STORED)
check(
    "disposition totals are 7 local-postprocess + 18 stored-only",
    Counter(row["disposition"] for row in rows)
    == Counter({"local-postprocess": 7, "stored-no-direct-consumer": 18}),
)
check("exact local-postprocess signal set", {sid for sid, row in by_sid.items() if row["disposition"] == "local-postprocess"} == LOCAL)
check("exact stored-no-direct-consumer signal set", {sid for sid, row in by_sid.items() if row["disposition"] == "stored-no-direct-consumer"} == STORED)
check("exact SecOC unresolved set is nine signals", {sid for sid, row in by_sid.items() if row["secoc_envelope"] == "yes"} == SECOC)
check("SecOC split is 3 local + 6 store-only", len(LOCAL & SECOC) == 3 and len(STORED & SECOC) == 6)
check(
    "no PARAM/plain-DATA pointer into the complete Rx scalar bank originates outside generated unpackers",
    all(row["outside_unpacker_bank_pointer_sites"] == "" for row in rows),
)

print("\n== live-audit direct-reference shape ==")
for sid in sorted(LOCAL):
    row = by_sid[sid]
    check(f"signal {sid} has three direct refs", row["direct_ref_count"] == "3")
    check(f"signal {sid} local read site is exact", row["unpacker_read_sites"] == LOCAL_SITES[sid], row["unpacker_read_sites"])
    check(f"signal {sid} has no outside direct read", row["outside_read_sites"] == "")
    check(f"signal {sid} has no outside PARAM alias in same-unpacker range", row["outside_param_alias_sites"] == "")
for sid in sorted(STORED):
    row = by_sid[sid]
    check(f"signal {sid} has exactly two direct refs", row["direct_ref_count"] == "2")
    check(f"signal {sid} has no local direct read", row["unpacker_read_sites"] == "")
    check(f"signal {sid} has no outside direct read", row["outside_read_sites"] == "")
    check(f"signal {sid} has no extra direct refs", row["other_direct_refs"] == "")
    check(f"signal {sid} has no outside PARAM alias in same-unpacker range", row["outside_param_alias_sites"] == "")
check(
    "16/18 stored-only rows are selective omissions beside consumed siblings",
    sum(int(by_sid[sid]["consumed_siblings_same_unpacker"]) > 0 for sid in STORED) == 16,
)
check(
    "CAN 0x020 is the sole whole-unpacker no-direct-consumer pair",
    {sid for sid in STORED if by_sid[sid]["consumed_siblings_same_unpacker"] == "0"} == {291, 292},
)

print("\n== raw local-postprocess control flow ==")
# CAN 0x0AA: four unsigned 15-bit raw values are immediately loaded as
# halfwords and normalized with helper 0x4A49C using offset 0x1A6F.
for sid, call, read, out_ptr in [
    (231, 0x4AEEA, 0x4AEEE, 0x4AEF8),
    (233, 0x4AF16, 0x4AF1A, 0x4AF24),
    (235, 0x4AF42, 0x4AF46, 0x4AF50),
    (237, 0x4AF6E, 0x4AF72, 0x4AF7C),
]:
    check(f"signal {sid} receive_signal call is pinned", b(call, "83ff"))
    check(f"signal {sid} local raw read is halfword", CF[read:read + 2] == bytes.fromhex("e447"))
    check(f"signal {sid} normalization offset is 0x1A6F", b(read + 6, "203e6f1a"))
    check(f"signal {sid} derived output pointer is explicit", CF[out_ptr:out_ptr + 2] == bytes.fromhex("244e"))
    check(f"signal {sid} calls postprocess helper 0x4A49C", CF[out_ptr + 4:out_ptr + 6] == bytes.fromhex("bfff"))

# CAN 0x090: three unsigned 10-bit raw values are immediately loaded and
# normalized with offset 0x0200 to derived halfwords 8060/8062/8064.
for sid, call, read, out_ptr in [
    (270, 0x4B2A2, 0x4B2A6, 0x4B2B0),
    (273, 0x4B302, 0x4B306, 0x4B310),
    (276, 0x4B362, 0x4B366, 0x4B370),
]:
    check(f"signal {sid} receive_signal call is pinned", b(call, "83ff"))
    check(f"signal {sid} local raw read is halfword", CF[read:read + 2] == bytes.fromhex("e447"))
    check(f"signal {sid} normalization offset is 0x0200", b(read + 6, "203e0002"))
    check(f"signal {sid} derived output pointer is explicit", CF[out_ptr:out_ptr + 2] == bytes.fromhex("244e"))
    check(f"signal {sid} calls postprocess helper 0x4A49C", CF[out_ptr + 4:out_ptr + 6] == bytes.fromhex("bfff"))

# Downstream generated consumer loads all seven derived halfwords.
derived_reads = {
    0x5735E: "249f32c8",  # 0x0AA s231 -> 0xFEBE8032
    0x57340: "249f34c8",  # s233 -> 0x8034
    0x57382: "249f36c8",  # s235 -> 0x8036
    0x57374: "249f38c8",  # s237 -> 0x8038
    0x573E8: "248760c8",  # 0x090 s270 -> 0x8060
    0x573FA: "248762c8",  # s273 -> 0x8062
    0x5745A: "249f64c8",  # s276 -> 0x8064
}
for address, raw in derived_reads.items():
    check(f"derived postprocess output is consumed at 0x{address:X}", b(address, raw))

print(f"\nSummary: {passed} passed, {failed} failed")
sys.exit(1 if failed else 0)
