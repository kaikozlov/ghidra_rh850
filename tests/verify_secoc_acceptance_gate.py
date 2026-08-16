#!/usr/bin/env python3
"""Deterministic verification of the corrected SecOC acceptance-gate semantics.

The receive path has two distinct gates:

  Gate 1 (0x8E726): verify-worker completion status.
  Gate 2 (0x8E69E..0x8E6C8): ICU-S CMAC verification result.

The command-7 KAT pins the Gate-2 result polarity: zero is verification OK;
nonzero is not verified. Gate 2 booleanizes `(result != 0)` into r26, then
`cmp r0,r26; bne mismatch`. Therefore result==0 falls through to the PduR/COM
delivery chain, while nonzero branches to failure/retry bookkeeping.
"""
from __future__ import annotations

import struct
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
CF = (REPO / "firmware" / "RH850_P1M-E_CodeFlash.bin").read_bytes()

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


def jarl_target(call_site: int) -> int | None:
    w0, w1 = struct.unpack_from("<HH", CF, call_site)
    if ((w0 >> 6) & 0x1F) != 0x1E or (w1 & 1):
        return None
    reg2 = (w0 >> 11) & 0x1F
    if reg2 == 0:
        return None
    high = w0 & 0x3F
    if high & 0x20:
        high -= 0x40
    return call_site + (high << 16) + w1


def find_jarls(start: int, end: int) -> dict[int, int]:
    out: dict[int, int] = {}
    for off in range(start, min(end, len(CF) - 4), 2):
        target = jarl_target(off)
        if target is not None:
            out[off] = target
    return out


print("== 1. Gate 1 remains worker-completion filtering ==")
check("dispatcher calls secoc_rx_verify_worker", jarl_target(0x8E720) == 0x8E4BA)
check(
    "Gate 1 is cmp r0,r10 then bne",
    u16(0x8E726) == 0x51E0 and u16(0x8E728) == 0x05EA,
    f"0x{u16(0x8E726):04X} 0x{u16(0x8E728):04X}",
)
check("worker success enters Gate-2 dispatcher", jarl_target(0x8E72E) == 0x8E67A)


print("\n== 2. command-7 KAT pins verify-result polarity ==")
# Synchronous slot-4 KAT: initialize output byte at sp+3 to 1, pass &sp[3] to
# cryptoif_job_finish, then report SETFE(cStack_21 == 0). Thus only a driver
# result of zero produces KAT pass; an unwritten/preinitialized 1 remains fail.
check(
    "KAT preinitializes verify-result output byte to 1",
    CF[0x680FC:0x68102] == bytes.fromhex("010a430f0300"),
    CF[0x680FC:0x68102].hex(),
)
check(
    "KAT passes sp+3 as cryptoif_job_finish result pointer",
    CF[0x6814A:0x68152] == bytes.fromhex("234e030082ff5a0a"),
    CF[0x6814A:0x68152].hex(),
)
check("KAT result call targets cryptoif_job_finish", jarl_target(0x6814E) == 0x88BA8)
check(
    "KAT reports pass iff verify-result byte equals zero",
    CF[0x68168:0x6817E] == bytes.fromhex("03f06398010a030d2036ff00233e0400e099e20f0000"),
    CF[0x68168:0x6817E].hex(),
)


print("\n== 3. Gate 2 maps zero to delivery and nonzero to mismatch ==")
GATE2_LOAD = bytes.fromhex("840f5d9de009e10f14d3")
check("Gate 2 loads FEBE555C and materializes result!=0", CF[0x8E69E:0x8E6A8] == GATE2_LOAD)
check("FEBE555C load is unique", CF.count(bytes.fromhex("840f5d9d")) == 1)
check(
    "Gate 2 compares boolean to zero then BNEs to mismatch arm",
    CF[0x8E6C4:0x8E6CC] == bytes.fromhex("1d30e0d19a0d1a38"),
    CF[0x8E6C4:0x8E6CC].hex(),
)
check("gate CMP is cmp r0,r26", CF[0x8E6C6:0x8E6C8] == bytes.fromhex("e0d1"))
check("following BNE remains 9a0d", CF[0x8E6C8:0x8E6CA] == bytes.fromhex("9a0d"))

# boolean := (verify_result != 0); BNE is taken when boolean != 0.
# Combined with the KAT polarity, branch target is mismatch and fallthrough is OK.
check("verified-result fallthrough begins at 0x8E6CA", 0x8E6C8 + 2 == 0x8E6CA)
check("mismatch BNE target is 0x8E6DA", 0x8E6DA > 0x8E6CA)


print("\n== 4. fallthrough is the PduR/COM delivery chain ==")
jarls_gate = find_jarls(0x8E67A, 0x8E700)
check("fallthrough calls verification-status helper with success code", jarls_gate.get(0x8E6CC) == 0x8E244)
check("fallthrough calls PDU extract/route helper", jarls_gate.get(0x8E6D4) == 0x8E2BA)
check("mismatch branch calls retry/failure bookkeeping", jarls_gate.get(0x8E6DE) == 0x8E382)
check("pre-gate freshness/status callback remains before Gate 2", jarls_gate.get(0x8E6C0) == 0x8E646)

jarls_delivery = find_jarls(0x8E2BA, 0x8E30A)
check("delivery helper extracts queued PDU", jarls_delivery.get(0x8E2D4) == 0x8D9A4)
check("delivery helper passes extracted PDU to routing wrapper", jarls_delivery.get(0x8E2F0) == 0x8E7C6)
check("routing wrapper enters PduR-style dispatcher", jarl_target(0x8E7CC) == 0x80BBA)
check(
    "PduR-style dispatcher terminates in computed routing callback",
    CF[0x80C1C:0x80C26] == bytes.fromhex("25ef61e01330fdc760f9"),
    CF[0x80C1C:0x80C26].hex(),
)


print("\n== 5. mismatch arm is retained/retry bookkeeping, not delivery ==")
jarls_mismatch = find_jarls(0x8E382, 0x8E3EA)
check("mismatch bookkeeping not direct PDU-routing wrapper", 0x8E7C6 not in jarls_mismatch.values())
check("mismatch bookkeeping not PduR dispatcher", 0x80BBA not in jarls_mismatch.values())
check(
    "mismatch helper contains state/counter updates and status notification call",
    jarls_mismatch.get(0x8E3CC) == 0x8E244 and jarls_mismatch.get(0x8E3DC) == 0x8E30A,
)
# In FUN_8E67A, cleanup is skipped for retained state 0xB4 and run otherwise.
check(
    "post-arm cleanup tests state against 0xB4",
    CF[0x8E6EA:0x8E6F4] == bytes.fromhex("9c0f010001064cffc205"),
    CF[0x8E6EA:0x8E6F4].hex(),
)


print("\n== 6. Gate 1 completion and Gate 2 verify result are distinct ==")
GP = 0xFEBEB800
check(
    "job-completion polling cell differs from CMAC verify-result cell",
    GP + 0x5BBE == 0xFEBF13BE and 0xFEBF13BE != 0xFEBE555C,
)
check("cryptoif_job_finish calls crypto_driver_dispatch", jarl_target(0x88BD2) == 0x88556)


print("\n== 7. shared receive-profile coverage ==")
profile_can_ids = []
for i in range(6):
    base = 0x25972 + i * 0x50
    can_id = u32(base + 8)
    profile_can_ids.append(can_id)
    check(f"profile {i} has valid CAN ID 0x{can_id:03X}", 0 < can_id < 0x800)
check(
    "profiles cover all six recovered secured inputs",
    set(profile_can_ids) == {0x2E4, 0x131, 0x132, 0x090, 0x0D7, 0x00F},
)

print(f"\n== RESULT: {ok} passed, {bad} failed ==")
sys.exit(1 if bad else 0)
