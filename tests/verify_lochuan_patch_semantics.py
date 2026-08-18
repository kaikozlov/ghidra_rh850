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

print("\n== 6. patched instruction is dormant unless a write completion fails ==")
# Queue states 0x22 (changed data) and 0x33 (same-data/retry candidate) both
# converge on the physical-write path. The scheduler then records global
# completion state 0x33 before waiting for the NvM callback. The separate
# completion-state 0x22 arm in FUN_00066446 is the read/restore path.
check(
    "queue recognizes both 0x22 and 0x33 write candidates",
    CF[0x663E8:0x663F4] == bytes.fromhex("1d06deffc2051d06cdffda15"),
    CF[0x663E8:0x663F4].hex(),
)
check(
    "write path records completion state 0x33",
    CF[0x6640C:0x66414] == bytes.fromhex("20ee210020de3300"),
    CF[0x6640C:0x66414].hex(),
)
check(
    "completion worker dispatches state 0x33 to the patched arm",
    CF[0x66464:0x66472] == bytes.fromhex("1c06deffa20d1c06cdff9a4d8535"),
    CF[0x66464:0x66472].hex(),
)
# In the state-0x33 arm, successful callback state leaves r28=0x10 and branches
# around the patched instruction. Only lower-result != 0x5A reaches 0x664E4.
check(
    "successful write callback branches around 0x664E4",
    CF[0x664D6:0x664E0] == bytes.fromhex("20e610000a06a6fff205"),
    CF[0x664D6:0x664E0].hex(),
)

print("\n== 7. object 6 foreground restore trusts only public status 0x10 ==")
# FUN_B9054 builds a default object-6 buffer, asks the generated checkpoint
# restore API for object 6, then accepts payload +0x30 only when returned status
# is exactly 0x10 and the adjacent marker is valid. Otherwise it publishes the
# 0x7F80 sentinel and validity=0. Because the generated restore API copies the
# current RAM mirror before returning FEBF0308[6], a Lochuan-patched failed write
# can make the unpersisted RAM value look valid within the same boot.
check("object-6 restore passes literal object index 6", CF[0xB9070:0xB9078] == bytes.fromhex("0338063284ff3c60"))
check("object-6 restore requires returned status 0x10", CF[0xB9078:0xB9084] == bytes.fromhex("23f630000a06f0ff7198000c"))
check("object-6 restore failure path materializes 0x7F80 sentinel", CF[0xB909E:0xB90A4] == bytes.fromhex("209e807f000a"))
check("object-6 accepted/fallback value publishes to FEBEB592", CF[0xB90A4:0xB90AC] == bytes.fromhex("24f664fd979c860b"))
check(
    "namespace-0 restore copies RAM mirror before returning public status",
    CF[0x668C8:0x668E4] == bytes.fromhex("0730ecf7400221062caf0200c1f1043d7040bfffbef4c4e99d57094b"),
    CF[0x668C8:0x668E4].hex(),
)

print("\n== 8. object 6 persists the same learned baseline that it later restores ==")
# checkpoint_multi_channel_u16_state_persist loads FEBEE8AC into payload +0x30,
# then invokes secoc_nvm_object_update(6,...). application_input_snapshot_update
# is the sole normal writer of FEBEE8AC and copies FEBEB592 into it.
check("object-6 payload +0x30 is loaded from FEBEE8AC", CF[0x38D82:0x38D88] == bytes.fromhex("240fac30980c"))
check("object-6 persistence invokes update for literal object 6", CF[0x38DA4:0x38DC0] == bytes.fromhex("0338249fa8b60632240faab69a9c9b0c24f68cb6819c820c82ff1ccf"))

print("\n== 9. object-6 learned outputs enter the steering-command model ==")
# FUN_B9552 publishes two derived learned values at FEBEB594/596. The broad
# foreground snapshot copies them to FEBEAC6E/6C. Those are consumed by C4D9C
# and C4C8E respectively; C4C8E writes FEBEBC88, which is read by the named
# steering_command_secondary_select_stage. This proves a conditional path into
# the steering-command/plausibility model without claiming a direct d/q-current
# or PWM edge.
check("learned-state updater writes FEBEB594/596", CF[0xB9650:0xB965A] == bytes.fromhex("640f94fd020c640f96fd"))
check("C4C8E reads FEBEAC6C and writes FEBEBC88", CF[0xC4C96:0xC4CB8] == bytes.fromhex("e4976df4c199240fbe04d309640f6d041298f209df058099f309f30f2e9364978804"))
check("C4D9C reads FEBEAC6E", CF[0xC4DA4:0xC4DB0] == bytes.fromhex("24f628f424df8a0423e463e8"))

print("\n== 10. object-6 reload is reachable on the >=0x200 mode transition ==")
check(
    "mode dispatcher tests new and previous mode against 0x200 plus flag 0x10",
    CF[0xBEFD2:0xBEFE6] == bytes.fromhex("1c0600fe994ddade10001d0600fe891de0d9b205"),
    CF[0xBEFD2:0xBEFE6].hex(),
)
check(
    "mode-entry path resets object-6 init then conditionally calls B9662",
    CF[0xBF010:0xBF01C] == bytes.fromhex("bfff26a0e0d9b205bfff4aa6"),
    CF[0xBF010:0xBF01C].hex(),
)

print("\n== 11. checkpoint public status has no direct Gate-2 owner ==")
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

print("\n== 12. real Gate-2 patch is independent ==")
check("real Gate-2 stock CMP remains e0d1 at 0x8E6C6", CF[0x8E6C6:0x8E6C8] == bytes.fromhex("e0d1"))
check("real Gate-2 following mismatch BNE remains 9a0d", CF[0x8E6C8:0x8E6CA] == bytes.fromhex("9a0d"))
check("Lochuan target and Gate-2 target are distinct", 0x664E6 != 0x8E6C6)

print(f"\n== RESULT: {ok} passed, {bad} failed ==")
sys.exit(1 if bad else 0)
