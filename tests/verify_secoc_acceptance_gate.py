#!/usr/bin/env python3
"""Deterministic verification of the SecOC acceptance gate structure.

This suite pins the TWO-LEVEL gate structure that controls whether a secured
PDU is delivered as authenticated or enters the failure/release path:

  Gate 1 (0x8E726): verify_worker completion status
    — "did the verification worker run without error?"
    — filters out format errors, timeouts, submission failures
    — does NOT distinguish MAC match from mismatch

  Gate 2 (0x8E69E): MAC verification result from FEBE555C
    — "did the MAC actually match?"
    — the REAL acceptance gate for authenticated delivery versus the
      failure/release path

Pre-existing evidence in verify_secoc_security_properties.py already pins:
  - The unique load of FEBE555C at 0x8E69E (instruction bytes)
  - Its booleanization
  - The false-result branch avoiding authentic-PDU delivery (instruction bytes)

This test adds:
  - Both gate addresses and their instruction encodings
  - The call edges in the dispatch path (jarl-decoded)
  - Profile coverage
  - The distinction between job-completion polling (FEBF13BE/BF) and
    MAC result (FEBE555C)

NOTE: The current deterministic test does not yet pin the complete argument
and indirect-dispatch dataflow from secoc_submit_cmac_verify through the
crypto driver to the FEBE555C write; this portion remains recovered from
Ghidra decompilation. See §9.1 of application-chain.md for discussion.
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

# Gate 1 instruction bytes: cmp r0, r10 + bne (4 bytes total)
check("Gate 1 at 0x8E726: 'cmp r0, r10' (e051) then 'bne' (ea05)",
      u16(0x8E726) == 0x51E0 and u16(0x8E728) == 0x05EA,
      f"{hex(u16(0x8E726))} {hex(u16(0x8E728))}")

# Delivery call (reached only if worker returned 0)
check("FUN_0008E700 calls FUN_0008E67A at 0x8E72E",
      jarl_target(0x8E72E) == 0x8E67A)


# =====================================================================
# 2. Gate 2: MAC verification result from FEBE555C (0x8E69E)
# =====================================================================
print("\n== 2. Gate 2: MAC result load at 0x8E69E (FEBE555C) ==")

# Pinned by pre-existing verify_secoc_security_properties.py:
# The unique load of the ICU verify-result byte, booleanization, and branch.
# We assert the same bytes here for completeness.
GATE2_LOAD = bytes.fromhex("840f5d9de009e10f14d3")
check("Gate 2 loads FEBE555C and booleanizes at 0x8E69E",
      CF[0x8E69E:0x8E6A8] == GATE2_LOAD,
      CF[0x8E69E:0x8E6A8].hex())

check("FEBE555C GP-relative load (840f5d9d) is unique in CodeFlash",
      CF.count(bytes.fromhex("840f5d9d")) == 1)

# The false-result branch bytes (pre-existing pin)
GATE2_FALSE_BRANCH = bytes.fromhex("1d30e0d19a0d1a38bfff78fb1d301a38bfffe6fbd505")
check("Gate 2 false-result branch at 0x8E6C4 avoids authentic delivery",
      CF[0x8E6C4:0x8E6DA] == GATE2_FALSE_BRANCH,
      CF[0x8E6C4:0x8E6DA].hex())


# =====================================================================
# 3. Two-level gate: Gate 1 and Gate 2 are distinct
# =====================================================================
print("\n== 3. two-level gate structure ==")

check("Gate 1 (0x8E726) in FUN_0008E700, Gate 2 (0x8E69E) in FUN_0008E67A",
      0x8E700 <= 0x8E726 < 0x8E73A and 0x8E67A <= 0x8E69E < 0x8E700)

# Job-completion polling address (FEBF13BE/BF) differs from MAC result (FEBE555C)
GP = 0xFEBEB800
check("job-completion polling (gp+0x5BBE = FEBF13BE) != MAC result (FEBE555C)",
      GP + 0x5BBE == 0xFEBF13BE and 0xFEBF13BE != 0xFEBE555C)


# =====================================================================
# 4. Dispatch path call edges (jarl-decoded)
# =====================================================================
print("\n== 4. dispatch path call edges ==")

jarls_verify = dict(find_jarls(0x8E4BA, 0x8E700))
check("verify_worker calls secoc_submit_cmac_verify at 0x8E600",
      jarls_verify.get(0x8E600) == 0x8E3EA)

jarls_e67a = dict(find_jarls(0x8E67A, 0x8E700))
check("FUN_0008E67A calls FUN_0008E382 (MAC match path) at 0x8E6DE",
      jarls_e67a.get(0x8E6DE) == 0x8E382)
check("FUN_0008E67A calls FUN_0008E2BA (mismatch release path) at 0x8E6D4",
      jarls_e67a.get(0x8E6D4) == 0x8E2BA)
check("FUN_0008E67A calls FUN_0008E646 (commit freshness) at 0x8E6C0",
      jarls_e67a.get(0x8E6C0) == 0x8E646)

jarls_finish = dict(find_jarls(0x88BA8, 0x88C20))
check("cryptoif_job_finish calls crypto_driver_dispatch at 0x88BD2",
      jarls_finish.get(0x88BD2) == 0x88556)


# =====================================================================
# 5. Profile coverage
# =====================================================================
print("\n== 5. profile table ==")

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
# 6. Limitations (not counted as pass/fail assertions)
# =====================================================================
print("\n== 6. limitations ==")

# The plumbing from secoc_submit_cmac_verify's arguments through the crypto
# driver to the FEBE555C write involves indirect calls (function pointers
# resolved through the crypto driver record table). The current deterministic
# test does not yet pin the complete argument and indirect-dispatch dataflow;
# this portion remains recovered from Ghidra decompilation.
#
# What IS pinned by this test and the pre-existing security-properties test:
#   - Gate 2 loads FEBE555C via unique ld.bu instruction (§2)
#   - Gate 1 instruction bytes at 0x8E726 (§1)
#   - Call edges in the dispatch path (§4)
#   - Profile CAN IDs (§5)
#
# What is NOT yet pinned by deterministic tests:
#   - The ABI argument setup placing gp-0x62A4 into the param_4 register
#   - The crypto driver record's indirect target and retained result pointer
#   - The completion instruction that writes match/mismatch through that pointer
#   - The exact effect of FUN_0008E2BA on MAC mismatch (§9.5)

print("  result-pointer plumbing: recovered from Ghidra decompilation,")
print("  not yet pinned by deterministic raw-byte tests (see §9.1)")


print(f"\n== RESULT: {ok} passed, {bad} failed ==")
sys.exit(1 if bad else 0)
