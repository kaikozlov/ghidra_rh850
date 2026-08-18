#!/usr/bin/env python3
"""Pin the static evidence boundary for the RAM-only SecOC bypass investigation.

This deliberately proves only firmware-static properties.  It does not claim a
bench-validated post-initialization control-transfer hook.
"""
from __future__ import annotations

import json
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CF = (ROOT / "firmware" / "RH850_P1M-E_CodeFlash.bin").read_bytes()
CORPUS = ROOT / "data" / "generated" / "decompilations.jsonl"
passed = failed = 0


def check(name: str, condition: bool, detail: str = "") -> None:
    global passed, failed
    if condition:
        passed += 1
        print(f"[PASS] {name}")
    else:
        failed += 1
        print(f"[FAIL] {name}" + (f" ({detail})" if detail else ""))


def u32(addr: int) -> int:
    return struct.unpack_from("<I", CF, addr)[0]


def functions() -> list[dict]:
    out = []
    with CORPUS.open() as f:
        for line in f:
            row = json.loads(line)
            if row.get("record") == "function":
                out.append(row)
    return out


FUNCS = functions()
FUN_BY_ADDR = {int(row["entry_addr"], 16): row for row in FUNCS}


def refs_to(addr: int) -> list[tuple[int, str, int, str]]:
    hits = []
    for row in FUNCS:
        fn = int(row["entry_addr"], 16)
        for ref in row["data_references"]:
            if int(ref["to_addr"], 16) == addr:
                hits.append((fn, row["name"], int(ref["from_addr"], 16), ref["ref_type"]))
    return sorted(hits)


def main() -> int:
    print("== reset / boot-to-application RAM lifetime ==")
    check(
        "reset startup clears FEBE7000..FEBE7FFC",
        CF[0x660:0x67C] == bytes.fromhex(
            "2b060080befe2c060070befeec59f3056c0701000c660400ec59bbfd"
        ),
        CF[0x660:0x67C].hex(),
    )
    check(
        "reset wrapper clears FEBE8000 upward to FEC00000 boundary",
        CF[0x143C:0x1452] == bytes.fromhex(
            "3e060080befeb505010544f221060000c0fee1f1a1fd"
        ),
        CF[0x143C:0x1452].hex(),
    )
    check(
        "0x1426 apparent XCP-window clear is zero-trip under decoded bc comparison",
        CF[0x1426:0x143C] == bytes.fromhex(
            "3e06007cbffeb505010544f221060070befee1f1a1fd"
        )
        and not (0xFEBF7C00 < 0xFEBE7000),
        CF[0x1426:0x143C].hex(),
    )
    check("application entry pointer @0xFFDB8 == 0x20880", u32(0xFFDB8) == 0x20880, hex(u32(0xFFDB8)))
    check(
        "boot_application_handoff loads entry pointer and computed-calls it",
        CF[0x13F2:0x1402] == bytes.fromhex("8007890bfb1f630f010001e8fdc760f9"),
        CF[0x13F2:0x1402].hex(),
    )
    check(
        "application startup overwrites XCP shadow from CodeFlash 0x10000..0x17DEF",
        CF[0x6263E:0x62660] == bytes.fromhex(
            "3e06007cbffe210600000100e505219f0100440a019d44f23306f07d0100f309f1f5"
        ),
        CF[0x6263E:0x62660].hex(),
    )

    print("== retained authenticated-download pocket / MPU ==")
    check("MPU region 5 lower == FEBEF400", u32(0x3183C) == 0xFEBEF400, hex(u32(0x3183C)))
    check("MPU region 5 upper == FEBF33FC", u32(0x31840) == 0xFEBF33FC, hex(u32(0x31840)))
    check("MPU context 0 region 5 is supervisor RWX (0xB8)", u32(0x318A8) == 0xB8, hex(u32(0x318A8)))
    check("MPU context 1 region 5 is supervisor RWX (0xB8)", u32(0x318E8) == 0xB8, hex(u32(0x318E8)))

    app_refs = []
    for row in FUNCS:
        fn = int(row["entry_addr"], 16)
        if not (0x20000 <= fn < 0x100000):
            continue
        for ref in row["data_references"]:
            target = int(ref["to_addr"], 16)
            if 0xFEBF0000 <= target <= 0xFEBF0FFF:
                app_refs.append((target, fn, int(ref["from_addr"], 16), ref["ref_type"]))
    app_refs.sort()
    check(
        "no recovered application direct reference enters FEBF0000..FEBF0307",
        all(target >= 0xFEBF0308 for target, *_ in app_refs),
        repr(app_refs[:5]),
    )
    check(
        "first recovered application direct reference in payload window is FEBF0308",
        bool(app_refs) and app_refs[0][0] == 0xFEBF0308,
        repr(app_refs[:3]),
    )

    print("== SecOC result-consumption path ==")
    result_refs = refs_to(0xFEBE555C)
    compact = [(fn, site, typ) for fn, _, site, typ in result_refs]
    check(
        "FEBE555C has exactly producer PARAM + Gate-2 READ direct refs",
        compact == [
            (0x8E3EA, 0x8E41A, "PARAM"),
            (0x8E67A, 0x8E69E, "READ"),
        ],
        repr(compact),
    )
    check(
        "stock Gate-2 predicate is cmp r0,r26; bne at 8E6C6/8E6C8",
        CF[0x8E6C6:0x8E6CA] == bytes.fromhex("e0d19a0d"),
        CF[0x8E6C6:0x8E6CA].hex(),
    )
    check(
        "correct persistent neutralization changes cmp only (E0D1 -> E001)",
        bytes.fromhex("e001") + CF[0x8E6C8:0x8E6CA] == bytes.fromhex("e0019a0d"),
    )

    print("== recovered RAM callback cells are active subsystem state, not dormant hook slots ==")
    cb_refs = [(fn, site, typ) for fn, _, site, typ in refs_to(0xFEBE5600)]
    check(
        "FEBE5600 callback cell has explicit clear/config writers and runtime readers",
        cb_refs == [
            (0x8F688, 0x8F690, "WRITE"),
            (0x8F6FA, 0x8F73E, "WRITE"),
            (0x8F750, 0x8F814, "WRITE"),
            (0x8F948, 0x8F94C, "READ"),
            (0x8F948, 0x8F958, "READ"),
            (0x8F984, 0x8F984, "READ"),
            (0x8F996, 0x8F99A, "READ"),
        ],
        repr(cb_refs),
    )
    icus_cb = refs_to(0xFEBF1194)
    check(
        "ICU-S interrupt callback FEBF1194 is actively rewritten/cleared",
        sum(1 for *_, typ in icus_cb if typ == "WRITE") >= 10
        and sum(1 for *_, typ in icus_cb if typ == "READ") == 2,
        f"refs={len(icus_cb)}",
    )
    startup = FUN_BY_ADDR[0x65626]["decompiled_c"]
    check(
        "application startup initializes ICU-S then resets the FEBE5600 callback subsystem",
        "crypto_icus_initialize();" in startup and "FUN_0008a030();" in startup,
    )
    callback_reset_chain = [
        (0x8A030, "FUN_00096b82"),
        (0x96B82, "FUN_00096b66"),
        (0x96B66, "FUN_0008f1d0"),
        (0x8F1D0, "FUN_0008f6a0"),
        (0x8F6A0, "FUN_0008f688"),
    ]
    check(
        "startup callback reset chain reaches the function that zeros FEBE5600",
        all(name in FUN_BY_ADDR[addr]["decompiled_c"] for addr, name in callback_reset_chain),
    )
    check(
        "ICU-S startup initialization zeros FEBF1194 before normal SecOC traffic",
        "puVar1[0x1665] = 0;" in FUN_BY_ADDR[0x8735E]["decompiled_c"]
        and "crypto_icus_initialize();" in startup,
    )

    print("== conclusion boundary ==")
    check(
        "retained pocket is inside both authenticated-download and application-RWX bounds",
        0xFEBF0000 >= 0xFEBF0000
        and 0xFEBF0307 <= 0xFEBF0FFF
        and 0xFEBEF400 <= 0xFEBF0000 <= 0xFEBF0307 <= 0xFEBF33FC,
    )
    print(
        "NOTE: this proves a reset-cleared, direct-handoff-retainable, application-RWX storage pocket.\n"
        "      It does not prove a post-init stock control-transfer consumer into that pocket."
    )

    print(f"\n{passed} passed, {failed} failed")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
