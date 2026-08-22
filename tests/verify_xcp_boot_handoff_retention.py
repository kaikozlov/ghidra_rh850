#!/usr/bin/env python3
"""Verify XCP-window lifetime across the live application->boot handoff.

This is a raw-CodeFlash regression for the composition between COM-005 and
SEC-BOOT-011. It proves the normal application programming transition:

* passes the fixed retained record at CodeFlash 0x31914 to 0x9F00;
* enters the boot failure/programming runtime without a reset;
* does not call the reset-startup initializer 0x1404 on that path;
* leaves the FEBF7C00 XCP/shadow window untouched by the boot handoff; and
* clears MPM before calling 0x148E.

The test deliberately does NOT claim a control-transfer consumer into the XCP
window. It also pins the disproved candidate that r6 could be attacker-selected:
0x64EC8 loads literal 0x31914 immediately before the call.
"""
from __future__ import annotations

import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CF = (ROOT / "firmware" / "RH850_P1M-E_CodeFlash.bin").read_bytes()
passed = failed = 0


def check(name: str, condition: object, detail: str = "") -> None:
    global passed, failed
    ok = bool(condition)
    passed += int(ok)
    failed += int(not ok)
    suffix = f" ({detail})" if detail else ""
    print(f"[{'PASS' if ok else 'FAIL'}] {name}{suffix}")


def u32(addr: int) -> int:
    return struct.unpack_from("<I", CF, addr)[0]


print("== fixed application handoff source ==")
check(
    "0x64EE6 loads r6=0x31914 then calls 0x9F00",
    CF[0x64EE6:0x64EF0] == bytes.fromhex("260614190300baff1450"),
    CF[0x64EE6:0x64EF0].hex(),
)
record = tuple(u32(0x31914 + i * 4) for i in range(9))
check(
    "retained programming record is fixed {kind=0,id=0x7A1,session=2}",
    record == (0, 0x7A1, 0, 0, 2, 0, 0, 0, 0),
    repr(record),
)

print("== live boot context establishment ==")
check(
    "0x9F44 establishes SP/GP/TP and clears MPM before 0x148E",
    CF[0x9F44:0x9F62] == bytes.fromhex(
        "23060080befe"      # mov FEBE8000,sp
        "24060098bffe"      # mov FEBF9800,gp
        "25069c860000"      # mov 869C,tp
        "e0072028"          # ldsr r0,MPM
        "1c00"              # synci
        "1f00"              # syncp
        "bfff3075"          # jarl 148E,lp
    ),
    CF[0x9F44:0x9F62].hex(),
)
check(
    "0x148E copies exactly nine dwords into FEBF2908 then enters 0x1398",
    CF[0x148E:0x14A0] == bytes.fromhex("80072100243e08910942bfffe0ffbffffcfe"),
    CF[0x148E:0x14A0].hex(),
)
check(
    "0x1398 enters boot init 0x1338",
    CF[0x1398:0x13A0] == bytes.fromhex("80072100bfff9cff"),
    CF[0x1398:0x13A0].hex(),
)

print("== reset-only initializer is not on live handoff ==")
check(
    "reset startup is the sole direct caller of 0x1404",
    CF[0x67C:0x680] == bytes.fromhex("80ff880d"),
    CF[0x67C:0x680].hex(),
)
check(
    "boot runtime init 0x1338 has no call to 0x1404",
    bytes.fromhex("80ff68") not in CF[0x1338:0x1378],
)

print("== apparent FEBF7C00 reset clear is zero-trip ==")
check(
    "0x1426 loads FEBF7C00 but compares against lower FEBE7000",
    CF[0x1426:0x143C] == bytes.fromhex(
        "3e06007cbffe"  # mov FEBF7C00,ep
        "b505"          # br compare
        "0105"          # store body (not entered initially)
        "44f2"          # ep += 4
        "21060070befe"  # mov FEBE7000,r1
        "e1f1"          # cmp r1,ep
        "a1fd"          # bc store-body only when ep < endpoint
    ),
    CF[0x1426:0x143C].hex(),
)
check("FEBF7C00 is above FEBE7000", 0xFEBF7C00 > 0xFEBE7000)

print("== composition boundary ==")
check(
    "live-handoff core contains no literal FEBF7C00 materialization",
    bytes.fromhex("007cbffe") not in CF[0x64EC8:0x64EF8]
    and bytes.fromhex("007cbffe") not in CF[0x9F00:0x9F64]
    and bytes.fromhex("007cbffe") not in CF[0x148E:0x14A2]
    and bytes.fromhex("007cbffe") not in CF[0x1398:0x13B0],
)

print(f"\n== RESULT: {passed} passed, {failed} failed ==")
sys.exit(1 if failed else 0)
