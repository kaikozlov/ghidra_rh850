#!/usr/bin/env python3
"""Verify semantics of Lochuan/3b1b's 0x664E6 0x31->0x10 patch.

The patch is intentionally compared with the real SecOC Gate-2 predicate but
is verified from the Sienna firmware independently of the external repository.
It changes only the ordinary checkpoint failure status exposed to consumers;
the lower storage-failure latch and Dem reporting path remain intact.
"""
from __future__ import annotations

import csv
import hashlib
import json
import struct
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
CF = (REPO / "firmware" / "RH850_P1M-E_CodeFlash.bin").read_bytes()
CORPUS = REPO / "data" / "generated" / "decompilations.jsonl"
CHECKPOINT_MAP = REPO / "data" / "checkpoint_payload_map.csv"
NVM_RECORDS = REPO / "data" / "dataflash_nvm_records.csv"

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

print("\n== 11. objects 5/6/8 are one persisted adaptation family ==")
with CHECKPOINT_MAP.open(newline="", encoding="utf-8") as stream:
    checkpoint_rows = {int(row["object_index"]): row for row in csv.DictReader(stream)}
for obj, expected in {
    5: (8, 6, 64, "0xFEBEF430"),
    6: (56, 6, 70, "0xFEBEF4D0"),
    8: (8, 2, 76, "0xFEBEF438"),
}.items():
    row = checkpoint_rows[obj]
    actual = (int(row["data_length"]), int(row["ring_blocks"]), int(row["first_nvm_block"]), row["ram_mirror"])
    check(f"object {obj} checkpoint geometry", actual == expected, repr(actual))
check(
    "B19D2 grouped commit calls object5, object6, then object8 writers",
    CF[0xB19D6:0xB19E2] == bytes.fromhex("84ff72d584ff1ed580ff6895"),
    CF[0xB19D6:0xB19E2].hex(),
)
check(
    "0x701 lifecycle substate invokes grouped 5/6/8 commit then advances to 0x702",
    CF[0xB1A52:0xB1A5E] == bytes.fromhex("bfff80ff20360207bfffd6e8"),
    CF[0xB1A52:0xB1A5E].hex(),
)
check("transition persistence first dwell threshold is 0 ticks", u16(0xAEF28) == 0, str(u16(0xAEF28)))
check("transition persistence alternate dwell threshold is 100 ticks", u16(0xAEF2E) == 100, str(u16(0xAEF2E)))
check(
    "transition-dwell commit calls object5, object6, and object13 writers",
    CF[0xB2D34:0xB2D42] == bytes.fromhex("01d884ff12c284ffbec180ff868f"),
    CF[0xB2D34:0xB2D42].hex(),
)

print("\n== 12. captured 5/6/8 DataFlash rings are healthy ==")
with NVM_RECORDS.open(newline="", encoding="utf-8") as stream:
    nvm_rows = list(csv.DictReader(stream))
for obj, expected_count in ((5, 6), (6, 6), (8, 2)):
    rows = [r for r in nvm_rows if r["owner_class"] == "checkpoint" and r["owner_index"] == str(obj)]
    check(f"object {obj} has expected captured ring count", len(rows) == expected_count, str(len(rows)))
    check(f"object {obj} captured records all validate", all(r["record_valid"] == "yes" for r in rows))
    check(f"object {obj} generation/complement pairs all validate", all(r["checkpoint_counter_valid"] == "yes" for r in rows))

print("\n== 13. object5 status controls object6 validation baseline ==")
check("object5 restore requires exact public status 0x10", CF[0x477E6:0x477EC] == bytes.fromhex("0a06f0ff7980"))
check("object5 restore failure substitutes signed sentinel 0x7D00", CF[0x47808:0x47810] == bytes.fromhex("200e007d01980092"))
# The object-6 validators compare the restored object-5 baselines against their
# current paired samples before accepting slices of the object-6 bank.
validator_refs: dict[int, set[str]] = {}
with CORPUS.open(encoding="utf-8") as stream:
    for line in stream:
        row = json.loads(line)
        if row.get("record") != "function":
            continue
        entry = int(row["entry_addr"], 16)
        if entry in {0x38848, 0x3910A, 0x393EC, 0x39D48, 0x3A4E6, 0x3AD34}:
            validator_refs[entry] = {ref.get("to_addr", "").lower() for ref in row.get("data_references", [])}
needed_baselines = {"0xfebe7d6e", "0xfebe7d70", "0xfebe7d76", "0xfebe7d78"}
check(
    "object6 validators read object5 current/restored reference pair",
    any(needed_baselines <= refs for refs in validator_refs.values()),
    repr({hex(k): sorted(v & needed_baselines) for k, v in validator_refs.items()}),
)

print("\n== 14. object8 is another exact-0x10 adaptation restore ==")
check("object8 restore requires exact public status 0x10", CF[0xBAF00:0xBAF06] == bytes.fromhex("0a06f0ffca0d"))
check(
    "object8 success publishes persisted u32/u16/validity tuple",
    CF[0xBAF08:0xBAF18] == bytes.fromhex("000d640f05f77208640f0ef66608440f"),
    CF[0xBAF08:0xBAF18].hex(),
)

print("\n== 15. object7 is a separate protected-status phase workflow ==")
check("object7 restore requires exact public status 0x10 for persisted phase", CF[0xB7E0C:0xB7E1C] == bytes.fromhex("0a06f0ff8a15830f01000106efffba0d"))
# Firmware corpus proves object7 phase byte FEBEAF44 is read by the protected
# 0x0D7 fault monitor, which raises event 0x2D; mode substate 0x522 consumes it.
obj7_phase_read = event_2d_set = event_2d_consume = False
with CORPUS.open(encoding="utf-8") as stream:
    for line in stream:
        row = json.loads(line)
        if row.get("record") != "function":
            continue
        entry = int(row["entry_addr"], 16)
        code = row.get("decompiled_c", "").lower()
        refs_here = {ref.get("to_addr", "").lower() for ref in row.get("data_references", [])}
        if entry == 0xB6396:
            obj7_phase_read = "0xfebeaf44" in refs_here
            event_2d_set = "system_mode_event_set(0x2d)" in code
        if entry == 0xB1DAC:
            event_2d_consume = "fun_000b03cc(0x2d)" in code and "0x522" in code
check("0x0D7 fault monitor reads object7 phase byte", obj7_phase_read)
check("0x0D7 fault monitor raises system event 0x2D", event_2d_set)
check("mode-0x522 workflow consumes event 0x2D", event_2d_consume)

print("\n== 16. object6-sensitive learner has no direct 0x262/0x351 status edge ==")
sensitive = {"0xfebeb87e", "0xfebebc88", "0xfebebc9a", "0xfebeb754", "0xfebec1b8", "0xfebec1d4"}
lka_producers = {0xC8072, 0xC8224, 0xC8280, 0xC8306, 0xC8690}
lka_refs: dict[int, set[str]] = {}
with CORPUS.open(encoding="utf-8") as stream:
    for line in stream:
        row = json.loads(line)
        if row.get("record") != "function":
            continue
        entry = int(row["entry_addr"], 16)
        if entry in lka_producers:
            lka_refs[entry] = {ref.get("to_addr", "").lower() for ref in row.get("data_references", [])}
check("all five dynamic 0x262 LKA producers are present", set(lka_refs) == lka_producers, repr(sorted(hex(x) for x in lka_refs)))
check(
    "none of the dynamic 0x262 LKA producers directly reads object6-sensitive model state",
    all(not (refs & sensitive) for refs in lka_refs.values()),
    repr({hex(k): sorted(v & sensitive) for k, v in lka_refs.items()}),
)

print("\n== 17. ordinary WriteBlock completion is binary success/failure at checkpoint boundary ==")
# NvM service 0x07 builds lower operation class 2. The lower selector map at
# 0x27760 maps class 2 to adapter index 1, whose callback pointer is 0x72DFA.
# 0x72DFA is currently outside the canonical function graph, so pin its bytes
# directly: it samples the write-device state, writes FEBF7700 only for state
# 0 or 1, and leaves all other states nonterminal.
check(
    "service-7 write path materializes lower operation class 2",
    CF[0x715DC:0x715E6] == bytes.fromhex("0755050582ec01e5405e"),
    CF[0x715DC:0x715E6].hex(),
)
check(
    "lower operation selector maps class 2 to adapter index 1",
    u32(0x27760) == 2 and u32(0x27764) == 0x27770
    and u32(0x27778) == 2 and u32(0x2777C) == 1,
)
check("adapter index 1 callback is 0x72DFA", u32(0x2776C) == 0x72DFA, hex(u32(0x2776C)))
check(
    "write completion adapter only commits request result 0 or 1",
    CF[0x72E1A:0x72E3A] == bytes.fromhex("e051a20d6152aa150032bfff54e20432bfff4ee20152405ebffe1f0a4b570077"),
    CF[0x72E1A:0x72E3A].hex(),
)

print("\n== 18. write report mode has one success key, one special nonterminal key, and failure keys ==")
# FUN_75482 puts this device into report mode 2. In FUN_76CD6 that selects the
# second result byte in the eight-row table at 0x27E0C. The resulting raw code
# reaches FUN_75692: raw 0 -> state 0; raw 0x83 -> state 4; every other nonzero
# code -> state 1. Because 0x72DFA only commits terminal state 0/1, raw 0x83 is
# explicitly not a completed WriteBlock failure yet.
check(
    "write device setup selects report mode 2",
    CF[0x754AE:0x754B4] == bytes.fromhex("023280ff1a17"),
    CF[0x754AE:0x754B4].hex(),
)
expected_write_map = [
    (0x00000001, 0x00),
    (0x0000FFFF, 0xFD),
    (0x0000FFFE, 0x7F),
    (0x0000FFFD, 0xFD),
    (0x0000FFFC, 0x83),
    (0x0000FFFB, 0xFD),
    (0x0000FFFA, 0xFF),
    (0xFFFF0000, 0x7F),
]
actual_write_map = []
for i in range(8):
    row = CF[0x27E0C + i * 8:0x27E14 + i * 8]
    actual_write_map.append((int.from_bytes(row[0:4], "little"), row[5]))
check("mode-2 lower report map matches eight pinned rows", actual_write_map == expected_write_map, repr(actual_write_map))
check(
    "raw result mapper sends zero to state0, 0x83 to state4, other nonzero to state1",
    CF[0x75692:0x756C6] == bytes.fromhex(
        "80076100c6eeff00fa051d30bfff26fe80ff9c03e50d1d067dffba050432a505"
        "0132bfff10fe1d3080ff760380ff8c0340067f00"
    ),
    CF[0x75692:0x756C6].hex(),
)

print("\n== 19. checkpoint public status has no direct Gate-2 owner ==")
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

print("\n== 20. published target-sector pins are derivable from this offline image ==")
target_sector = CF[0x60000:0x68000]
patched_target_sector = bytearray(target_sector)
patched_target_sector[0x664E6 - 0x60000] = 0x10
check(
    "published original target-sector SHA is the canonical offline sector",
    hashlib.sha256(target_sector).hexdigest() == "f0e76a887c2b85609cee4cd44620db068d414edfb44bbafe551ec440b2a0e9d0",
    hashlib.sha256(target_sector).hexdigest(),
)
check(
    "published candidate SHA is exactly the one-byte offline mutation",
    hashlib.sha256(patched_target_sector).hexdigest() == "c67d992a8413d020fb16464d58654ab3fbd84139809b6b544c6142d6dcfeeb7b",
    hashlib.sha256(patched_target_sector).hexdigest(),
)
check("published original CRC fixup is literal source-image word", u32(0xFFDEC) == 0x0962887F, hex(u32(0xFFDEC)))

print("\n== 21. real Gate-2 patch is independent ==")
check("real Gate-2 stock CMP remains e0d1 at 0x8E6C6", CF[0x8E6C6:0x8E6C8] == bytes.fromhex("e0d1"))
check("real Gate-2 following mismatch BNE remains 9a0d", CF[0x8E6C8:0x8E6CA] == bytes.fromhex("9a0d"))
check("Lochuan target and Gate-2 target are distinct", 0x664E6 != 0x8E6C6)

print(f"\n== RESULT: {ok} passed, {bad} failed ==")
sys.exit(1 if bad else 0)
