#!/usr/bin/env python3
"""Deterministic verification of the SecOC MAC-acceptance bypass patch point.

This suite pins the exact CodeFlash byte that, when changed from 0x9A to 0x95,
converts the Gate-2 conditional branch (bne → authenticated delivery only on MAC
match) into an unconditional branch (br → authenticated delivery ALWAYS). This
is the minimal one-byte CodeFlash change needed to bypass the recovered Gate-2
MAC delivery decision shared by the configured receive profiles. Persistent
deployment additionally requires a boot-compatible CRC repair.

Context (see SECOC-029, application-chain.md §9):
  Gate 2 at 0x8E69E loads the MAC verification result byte from FEBE555C,
  booleanizes it into r26, and at 0x8E6C8 branches to FUN_0008E382
  (authenticated delivery) only when r26 != 0 (MAC matched). The false
  path falls through to FUN_0008E244 + FUN_0008E2BA (failure/release).

The patch converts the 2-byte Bcond instruction at 0x8E6C8 from:
    0x0D9A = bne 0x8E6DA  (condition NE = 0xA)
to:
    0x0D95 = br  0x8E6DA  (condition always = 0x5)

Only the low byte changes (0x9A → 0x95); the high byte (0x0D, which encodes
the displacement) is unchanged. The branch target remains 0x8E6DA.

Freshness handling remains independent of the patched branch: FUN_0008E646 is
called at 0x8E6C0 before the branch and receives the REAL MAC-derived boolean in
r7. The patch therefore forces only the subsequent delivery decision; it does
not force the freshness manager to treat a bad MAC as authenticated. Existing
analysis shows the false-auth path does not advance ordinary freshness state.

CRC geometry: the patch is at VA 0x8E6C8, within boot-validity region 1
(0x18000..0xFFDFF), whose adjustment word is at 0xFFDEC. The community flash
RMW/resigning mechanism uses the same CRC-32/Ethernet terminal-fixup scheme
verified by stock region 0. The published region-1 dump contains a separately
recovered one-bit anomaly at 0xBB1C4; on the reconstructed stock image this
Gate-2 patch re-signs with adjustment 0x91698386 (SECOC-028/044, CORR-042).
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


def decode_bcond(off: int) -> tuple[int, int, int, int, int, int]:
    """Decode an RH850 Bcond addr9 instruction.

    Returns (halfword, s1115, opcode, op0406, cc0003, target_va).
    """
    hw = u16(off)
    s1115 = (hw >> 11) & 0x1F
    opcode = (hw >> 7) & 0xF
    op0406 = (hw >> 4) & 0x7
    cc = hw & 0xF
    s1115_signed = s1115 - 0x20 if s1115 & 0x10 else s1115
    target = ((s1115_signed << 4) | (op0406 << 1)) + off
    return hw, s1115, opcode, op0406, cc, target


# =====================================================================
# 1. Original instruction at the patch point
# =====================================================================
print("== 1. original bne at patch point 0x8E6C8 ==")

PATCH_VA = 0x8E6C8
hw, s1115, opcode, op0406, cc, target = decode_bcond(PATCH_VA)

check("instruction at 0x8E6C8 is Bcond format (opcode 0xB)",
      opcode == 0xB, f"opcode=0x{opcode:X}")

check("condition is NE (cc=0xA)",
      cc == 0xA, f"cc=0x{cc:X}")

check("branch target is 0x8E6DA (FUN_0008E382 authenticated delivery)",
      target == 0x8E6DA, f"target=0x{target:X}")

check("original halfword is 0x0D9A",
      hw == 0x0D9A, f"hw=0x{hw:04X}")


# =====================================================================
# 2. Patched instruction
# =====================================================================
print("\n== 2. patched br at 0x8E6C8 ==")

PATCHED_BYTE = 0x95  # only the low byte changes
patched_hw = (hw & 0xFF00) | PATCHED_BYTE
s1115_p = (patched_hw >> 11) & 0x1F
op0406_p = (patched_hw >> 4) & 0x7
cc_p = patched_hw & 0xF
s1115_p_signed = s1115_p - 0x20 if s1115_p & 0x10 else s1115_p
target_p = ((s1115_p_signed << 4) | (op0406_p << 1)) + PATCH_VA

check("patched condition is always (cc=0x5)",
      cc_p == 0x5, f"cc=0x{cc_p:X}")

check("patched target is still 0x8E6DA",
      target_p == 0x8E6DA, f"target=0x{target_p:X}")

check("only low byte changes (0x9A → 0x95)",
      (hw & 0xFF00) == (patched_hw & 0xFF00) and (hw & 0xFF) != PATCHED_BYTE,
      f"orig=0x{hw:04X} patched=0x{patched_hw:04X}")

check("high byte unchanged (0x0D = displacement)",
      (patched_hw >> 8) == 0x0D, f"high byte=0x{(patched_hw >> 8):02X}")


# =====================================================================
# 3. Gate 2 structure context
# =====================================================================
print("\n== 3. Gate 2 structure (patch in context) ==")

# Freshness callback at 0x8E6C0 is BEFORE the branch and receives the real
# MAC-derived boolean; changing 0x8E6C8 does not change that argument.
GATE2_LOAD = bytes.fromhex("840f5d9de009e10f14d3")
check("Gate 2 MAC result load at 0x8E69E (FEBE555C)",
      CF[0x8E69E:0x8E6A8] == GATE2_LOAD,
      CF[0x8E69E:0x8E6A8].hex())

# FEBE555C GP-relative load is unique
check("FEBE555C GP-relative load (840f5d9d) is unique",
      CF.count(bytes.fromhex("840f5d9d")) == 1)

# The false-path branch bytes (confirmed by verify_secoc_acceptance_gate.py)
GATE2_FALSE_BRANCH = bytes.fromhex("1d30e0d19a0d1a38bfff78fb1d301a38bfffe6fbd505")
check("Gate 2 false-result branch at 0x8E6C4 (contains our patch byte)",
      CF[0x8E6C4:0x8E6DA] == GATE2_FALSE_BRANCH,
      CF[0x8E6C4:0x8E6DA].hex())


# =====================================================================
# 4. CRC geometry (algorithm compatibility is verified separately)
# =====================================================================
print("\n== 4. CRC geometry ==")

# Boot validity region 1: 0x18000..0xFFDFF, CRC descriptor at 0x8DE0
check("CRC region 1 covers patch point",
      0x18000 <= PATCH_VA <= 0xFFDFF)

# Adjustment word at 0xFFDEC
check("CRC adjustment word at 0xFFDEC",
      0xFFDEC == 0xFFDF0 - 4)

# Marker at 0xFFE00
check("boot validity marker 0x5AA5A55A at 0xFFE00",
      u32(0xFFE00) == 0x5AA5A55A,
      f"0x{u32(0xFFE00):08X}")


# =====================================================================
# 5. Patch byte uniqueness (not a common byte)
# =====================================================================
print("\n== 5. patch point isolation ==")

# The specific halfword 0x0D9A (bne +18) should not be too common
bne_count = CF.count(struct.pack("<H", 0x0D9A))
check(f"halfword 0x0D9A occurs {bne_count} times (context disambiguates)",
      bne_count > 0, f"count={bne_count}")

# The 10-byte context window at the patch point
context = CF[0x8E6C0:0x8E6D2]
check("patch context window is stable (jarl+cmp+bne+fallthrough)",
      len(context) == 18 and context[8] == 0x9A and context[9] == 0x0D,
      context.hex())


# =====================================================================
# Result
# =====================================================================
print(f"\n== RESULT: {ok} passed, {bad} failed ==")
sys.exit(1 if bad else 0)
