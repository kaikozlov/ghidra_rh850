#!/usr/bin/env python3
"""Verify semantics of Lochuan/3b1b's 0x664E6 0x31->0x10 patch.

The patch is intentionally compared with the real SecOC Gate-2 predicate but
is verified from the Sienna firmware independently of the external repository.
It changes only the ordinary checkpoint failure status exposed to consumers;
the lower storage-failure latch and Dem reporting path remain intact.
"""
from __future__ import annotations

import json
import struct
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
CF = (REPO / "firmware" / "RH850_P1M-E_CodeFlash.bin").read_bytes()
CORPUS = REPO / "data" / "generated" / "decompilations.jsonl"

ok = bad = 0


def check(name: str, condition: object, detail: str = "") -> None:
    global ok, bad
    passed = bool(condition)
    ok += int(passed)
    bad += int(not passed)
    suffix = f" ({detail})" if detail else ""
    print(f"[{'PASS' if passed else 'FAIL'}] {name}{suffix}")


def u16(off: int) -> int:
    return struct.unpack_from("<H", CF, off)[0]


def u32(off: int) -> int:
    return struct.unpack_from("<I", CF, off)[0]


print("== 1. Lochuan target is checkpoint failure-status immediate ==")
# The external patch identifies the single changed byte as VA 0x664E6. In stock
# CodeFlash this is byte 2 of `movea 0x31,r0,r28` at 0x664E4.
ORIGINAL_INSN = bytes.fromhex("20 e6 31 00")
PATCHED_INSN = bytes.fromhex("20 e6 10 00")
check("stock instruction at 0x664E4 is movea-immediate 0x31 form", CF[0x664E4:0x664E8] == ORIGINAL_INSN)
check("target byte 0x664E6 is 0x31", CF[0x664E6] == 0x31)
check("published edit changes only immediate byte 2", [i for i, (a, b) in enumerate(zip(ORIGINAL_INSN, PATCHED_INSN)) if a != b] == [2])
check("patched immediate becomes ordinary success status 0x10", PATCHED_INSN == bytes.fromhex("20e61000"))

print("\n== 2. stock completion logic already emits 0x10 on success ==")
# state 0x33 arm: r28=0x10; compare lower completion return against 0x5A;
# on equality branch around the failure block to the common publisher.
check(
    "state-0x33 arm initializes published status to 0x10",
    CF[0x664D6:0x664DA] == bytes.fromhex("20e61000"),
    CF[0x664D6:0x664DA].hex(),
)
check(
    "lower completion result is compared with 0x5A before failure block",
    CF[0x664DA:0x664E0] == bytes.fromhex("0a06a6fff205"),
    CF[0x664DA:0x664E0].hex(),
)

print("\n== 3. failure latch survives the 0x31->0x10 edit ==")
# Failure path sets r1=0x5A, r28=0x31, then stores r1 to gp+0x4E7C
# (FEBF067C). The external patch changes only byte 0x664E6, so this store is
# unaffected even though the public status in r28 becomes 0x10.
check("failure path materializes 0x5A latch value", CF[0x664E0:0x664E4] == bytes.fromhex("200e5a00"))
check("failure path stock public status instruction is 0x31", CF[0x664E4:0x664E8] == ORIGINAL_INSN)
check("failure path stores independent latch after patched byte", CF[0x664E8:0x664EC] == bytes.fromhex("440f7c4e"))
check(
    "common publisher stores object status through FEBF0308-relative slot",
    CF[0x664FA:0x66500] == bytes.fromhex("c4e95de7084b"),
    CF[0x664FA:0x66500].hex(),
)

print("\n== 4. public checkpoint status API reads the same status array ==")
check("ordinary status getter loads gp/object + 0x4B08", CF[0x668A4:0x668AA] == bytes.fromhex("c4318657094b"))
# 0x65D34 dispatches namespace 0 to 0x66896; callers use this API to observe
# the public status that 0x66446 publishes.
check("namespace-0 status dispatch calls 0x66896", CF[0x65D3C:0x65D46] == bytes.fromhex("8600ca0580ff560bf50d"))

print("\n== 5. lower failure latch is converted into Dem events ==")
check(
    "latch consumer reads FEBF067C/067D and clears both",
    CF[0x667E2:0x667FC] == bytes.fromhex("629863081306a6ffe25700000106a6ffba058a56020082038303"),
    CF[0x667E2:0x667FC].hex(),
)
check("Dem publisher uses event 0x94 for first latch", CF[0x556EA:0x556F2] == bytes.fromhex("20369400203e3200"))
check("Dem publisher uses event 0x93 for second latch", CF[0x556FA:0x55702] == bytes.fromhex("20369300203e3200"))

# Event table record byte +2 is DTC-table index. Both 0x93 and 0x94 map to 3.
EVENT_TABLE = 0x2FDDC
for event_id in (0x93, 0x94):
    record = CF[EVENT_TABLE + event_id * 8: EVENT_TABLE + (event_id + 1) * 8]
    check(f"Dem event 0x{event_id:02X} maps to DTC index 3", len(record) == 8 and record[2] == 3, record.hex())

# DTC table is [failure_type:u8][dtc_id:u16 LE][pad:u8][enabled:u32 LE].
DTC_RECORD = CF[0x309DC + 3 * 8: 0x309DC + 4 * 8]
failure_type, dtc_id, pad, enabled = struct.unpack("<BHBI", DTC_RECORD)
check("DTC index 3 failure type is 0x46", failure_type == 0x46, hex(failure_type))
check("DTC index 3 identifier is 0x45D6", dtc_id == 0x45D6, hex(dtc_id))
check("DTC index 3 is enabled", pad == 0 and enabled == 1, DTC_RECORD.hex())

print("\n== 6. checkpoint public status has no direct Gate-2 owner ==")
refs: list[tuple[int, str, str, str]] = []
with CORPUS.open(encoding="utf-8") as stream:
    for line in stream:
        row = json.loads(line)
        for ref in row.get("data_references", []):
            if ref.get("to_addr", "").lower() == "0xfebf0308":
                refs.append((int(row["entry_addr"], 16), row["name"], ref["from_addr"], ref["ref_type"]))
check("canonical graph contains direct references to FEBF0308", bool(refs), repr(refs))
check(
    "every direct FEBF0308 owner is confined to checkpoint cone 0x6622A..0x668EE",
    all(0x6622A <= entry <= 0x668EE for entry, _name, _site, _kind in refs),
    repr(refs),
)
check(
    "no direct FEBF0308 owner is in SecOC Gate-2 0x8E6xx region",
    all(not (0x8E600 <= entry < 0x8E800) for entry, _name, _site, _kind in refs),
)

print("\n== 7. real Gate-2 patch is independent ==")
check("real Gate-2 stock CMP remains e0d1 at 0x8E6C6", CF[0x8E6C6:0x8E6C8] == bytes.fromhex("e0d1"))
check("real Gate-2 following mismatch BNE remains 9a0d", CF[0x8E6C8:0x8E6CA] == bytes.fromhex("9a0d"))
check("Lochuan target and Gate-2 target are distinct", 0x664E6 != 0x8E6C6)

print(f"\n== RESULT: {ok} passed, {bad} failed ==")
sys.exit(1 if bad else 0)
