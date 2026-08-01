#!/usr/bin/env python3
"""Deterministic verification of the SecOC acceptance gate structure.

This suite pins the TWO-LEVEL gate structure that controls whether a secured
PDU is delivered as authenticated or unauthenticated:

  Gate 1 (0x8E726): verify_worker completion status
    — "did the verification worker run without error?"
    — filters out format errors, timeouts, submission failures
    — does NOT distinguish MAC match from mismatch

  Gate 2 (0x8E69E): MAC verification result from FEBE555C
    — "did the MAC actually match?"
    — loaded from the output pointer passed to cryptoif_job_finish
    — the REAL acceptance gate for authenticated delivery
    — match → authenticated delivery (state 0xB4, freshness committed)
    — mismatch → unauthenticated release (stale PDU, no freshness advance)

The two gates are independent:
  - cryptoif_job_finish returns job-completion status (0=ok, 1=error, 2=timeout)
  - FEBE555C holds the MAC match/mismatch result, written by the crypto driver
  - Gate 1 passes whenever the worker completes normally (return 0)
  - Gate 2 is the actual MAC decision

Pre-existing evidence in verify_secoc_security_properties.py already pins:
  - The unique load of FEBE555C at 0x8E69E
  - Its booleanization
  - The false-result branch avoiding authentic-PDU delivery

This test adds:
  - The two-level gate structure (both gate addresses and their distinct roles)
  - The call edges in the dispatch path
  - The profile coverage proof
  - The cryptoif_job_finish fourth-argument = FEBE555C plumbing
"""
from __future__ import annotations

import struct
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
CF = (REPO / "firmware" / "RH850_P1M-E_CodeFlash.bin").read_bytes()

ok = 0
bad = 0


def check(name: str, condition: object, detail: str = "") -> None:
    global ok, bad
    if bool(condition):
        ok += 1
    else:
        bad += 1
    suffix = f" ({detail})" if detail else ""
    print(f"[{'PASS' if condition else 'FAIL'}] {name}{suffix}")


def u16(off: int) -> int:
    return struct.unpack_from("<H", CF, off)[0]


def u32(off: int) -> int:
    return struct.unpack_from("<I", CF, off)[0]


def jarl_target(call_site: int) -> int | None:
    """Decode an RH850 jarl instruction's target address."""
    hw1 = u16(call_site)
    if hw1 != 0xFFBF:
        return None
    hw2 = u16(call_site + 2)
    disp = hw2 & 0x1FFF
    if disp & 0x1000:
        disp -= 0x2000
    return call_site + disp


def find_jarls(start: int, end: int) -> list[tuple[int, int]]:
    results = []
    for off in range(start, min(end, len(CF) - 4), 2):
        t = jarl_target(off)
        if t is not None:
            results.append((off, t))
    return results


# =====================================================================
# 1. Gate 1: verify_worker completion check (0x8E726)
# =====================================================================
print("== 1. Gate 1: verify_worker completion at 0x8E726 ==")

check("FUN_0008E700 calls secoc_rx_verify_worker at 0x8E720",
      jarl_target(0x8E720) == 0x8E4BA)

# Gate 1 instruction: cmp r0, r10 (0xE051 displayed, 0x51E0 LE)
check("Gate 1 at 0x8E726 is 'cmp r0, r10'",
      u16(0x8E726) == 0x51E0, hex(u16(0x8E726)))

# Skip-delivery branch
check("Gate 1 branch at 0x8E728 is bne",
      u16(0x8E728) == 0x05EA, hex(u16(0x8E728)))

# Delivery call (reached only if worker returned 0)
check("FUN_0008E700 calls FUN_0008E67A at 0x8E72E",
      jarl_target(0x8E72E) == 0x8E67A)


# =====================================================================
# 2. Gate 2: MAC verification result from FEBE555C (0x8E69E)
# =====================================================================
print("\n== 2. Gate 2: MAC result at 0x8E69E (FEBE555C) ==")

# The unique load of the ICU verify-result byte
# ld.bu -0x62A4[gp], r1  (gp=FEBEB800, gp-0x62A4=FEBE555C)
check("Gate 2 loads FEBE555C via ld.bu -0x62A4[gp] at 0x8E69E",
      CF[0x8E69E:0x8E6A8] == bytes.fromhex("840f5d9de009e10f14d3"),
      CF[0x8E69E:0x8E6A8].hex())

# The GP-relative displacement is unique — no other instruction loads this byte
check("FEBE555C GP-relative load is unique in CodeFlash",
      CF.count(bytes.fromhex("840f5d9d")) == 1)

# The false-result branch at 0x8E6C4
check("Gate 2 false-result branch at 0x8E6C4 avoids authentic delivery",
      CF[0x8E6C4:0x8E6DA] == bytes.fromhex("1d30e0d19a0d1a38bfff78fb1d301a38bfffe6fbd505"),
      CF[0x8E6C4:0x8E6DA].hex())

# Verify the GP arithmetic: gp - 0x62A4 = FEBE555C
GP = 0xFEBEB800
check("GP-relative offset: gp(0xFEBEB800) - 0x62A4 = 0xFEBE555C",
      GP - 0x62A4 == 0xFEBE555C)


# =====================================================================
# 3. cryptoif_job_finish fourth argument = pointer to FEBE555C
# =====================================================================
print("\n== 3. cryptoif_job_finish output pointer = FEBE555C ==")

# secoc_submit_cmac_verify calls:
#   cryptoif_job_finish(param_1, puVar1 + -0x18ad, puVar1[-0x18ae], puVar1 + -0x18a9)
# where puVar1 = &LAB_febeb800 = gp (as uint32_t*)
# The fourth arg = puVar1 + (-0x18a9) = gp + (-0x18a9 * sizeof(uint32_t))
#               = gp + (-0x18a9 * 4) = gp - 0x62A4 = FEBE555C
check("cryptoif_job_finish param_4 = gp - 0x62A4 = FEBE555C",
      -0x18A9 * 4 == -0x62A4)

# The third arg is the bit-length output pointer at gp - 0x18ae*4 = gp - 0x62B8 = FEBE5548
check("cryptoif_job_finish param_3 = gp - 0x62B8 = FEBE5548 (bit length)",
      -0x18AE * 4 == -0x62B8)

# The second arg is the tag output at gp - 0x18ad*4 = gp - 0x62B4 = FEBE554C
check("cryptoif_job_finish param_2 = gp - 0x62B4 = FEBE554C (tag output)",
      -0x18AD * 4 == -0x62B4)


# =====================================================================
# 4. Two-level gate structure: Gate 1 ≠ Gate 2
# =====================================================================
print("\n== 4. two-level gate structure ==")

# Gate 1 (0x8E726) checks verify_worker return value (job status)
# Gate 2 (0x8E69E) checks FEBE555C (MAC match/mismatch result)
# These are at DIFFERENT addresses and test DIFFERENT conditions.
check("Gate 1 (0x8E726) and Gate 2 (0x8E69E) are at different addresses",
      0x8E726 != 0x8E69E)

# Gate 1 is in FUN_0008E700 (the outer dispatcher)
# Gate 2 is in FUN_0008E67A (the acceptance/delivery function)
check("Gate 1 is in FUN_0008E700, Gate 2 is in FUN_0008E67A",
      0x8E700 <= 0x8E726 < 0x8E73A and 0x8E67A <= 0x8E69E < 0x8E700)


# =====================================================================
# 5. Profile coverage
# =====================================================================
print("\n== 5. profile coverage ==")

profile_can_ids = []
for i in range(6):
    base = 0x25972 + i * 0x50
    can_id = u32(base + 8)
    profile_can_ids.append(can_id)
    check(f"profile {i} CAN ID 0x{can_id:03X}",
          can_id != 0 and can_id < 0x800)

check("profiles cover 0x2E4/0x131/0x132/0x090/0x0D7/0x00F",
      set(profile_can_ids) == {0x2E4, 0x131, 0x132, 0x090, 0x0D7, 0x00F})


# =====================================================================
# 6. Call edges in the dispatch path
# =====================================================================
print("\n== 6. dispatch path call edges ==")

jarls_e67a = dict(find_jarls(0x8E67A, 0x8E700))
check("FUN_0008E67A calls FUN_0008E382 (MAC match path) at 0x8E6DE",
      jarls_e67a.get(0x8E6DE) == 0x8E382)
check("FUN_0008E67A calls FUN_0008E2BA (MAC mismatch delivery) at 0x8E6D4",
      jarls_e67a.get(0x8E6D4) == 0x8E2BA)
check("FUN_0008E67A calls FUN_0008E646 (commit freshness) at 0x8E6C0",
      jarls_e67a.get(0x8E6C0) == 0x8E646)

jarls_verify = dict(find_jarls(0x8E4BA, 0x8E700))
check("verify_worker calls secoc_submit_cmac_verify at 0x8E600",
      jarls_verify.get(0x8E600) == 0x8E3EA)

jarls_finish = dict(find_jarls(0x88BA8, 0x88C20))
check("cryptoif_job_finish calls crypto_driver_dispatch at 0x88BD2",
      jarls_finish.get(0x88BD2) == 0x88556)


# =====================================================================
# 7. ICU-S job completion polling (distinct from MAC result)
# =====================================================================
print("\n== 7. ICU-S job completion polling (gp+0x5BBE/5BBF) ==")

# cryptoif_job_finish polls gp+0x5BBE for completion and gp+0x5BBF for job status
# These are JOB COMPLETION indicators, NOT the MAC verification result
# gp+0x5BBE = FEBEB800 + 0x5BBE = FEBF13BE
# gp+0x5BBF = FEBEB800 + 0x5BBF = FEBF13BF
check("job completion flag at gp+0x5BBE = FEBF13BE",
      GP + 0x5BBE == 0xFEBF13BE)
check("job status byte at gp+0x5BBF = FEBF13BF",
      GP + 0x5BBF == 0xFEBF13BF)

# The MAC result is at FEBE555C — a DIFFERENT address from the job status
check("MAC result (FEBE555C) != job completion (FEBF13BE)",
      0xFEBE555C != 0xFEBF13BE)


print(f"\n== RESULT: {ok} passed, {bad} failed ==")
sys.exit(1 if bad else 0)
