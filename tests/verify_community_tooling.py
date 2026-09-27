#!/usr/bin/env python3
"""Verify firmware-content invariants behind the community patcher artifacts.

The community-contributed exploit tooling in ``community/`` targets the
published ``8965B4512000`` CodeFlash dump. These checks pin the firmware facts
this repository has independently verified and that the tooling depends on:

  - the egg-hunter signature occurs exactly once, at VA 0x3485A (the shared
    SID-0xBA token comparator), and is a false positive for SecOC (SECOC-028);
  - the CRC geometry of the published dump, its unique one-bit anomaly at
    0xBB1C4 (SECOC-044), and the deterministic Gate-2 patch adjustment
    (SECOC-043).

These are firmware-content checks; they do not claim the tools work on
hardware.
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


def community_crc32(data: bytes) -> int:
    """Mirror crc32_flash_range() from the committed community main.c."""
    crc = 0xFFFFFFFF
    for byte in data:
        crc ^= byte
        for _ in range(8):
            crc = (crc >> 1) ^ 0xEDB88320 if crc & 1 else crc >> 1
    return crc ^ 0xFFFFFFFF


# ---- 6. Egg signature is a FALSE POSITIVE on 8965B4512000 (SECOC-028 erratum) ----
print("== 6. egg signature false-positive on Sienna 8965B4512000 ==")

# The egg (88 00 01 52 00 0a e5 0d) is the first 8 bytes of FUN_0003485A,
# the shared 5-byte token comparator for the SID-0xBA proprietary operation
# table — NOT the SecOC MAC verification function. Patching it forces BA token
# matches; F7's independent SA2 gate remains elsewhere. The actual SecOC verify
# worker is at 0x8E4BA.
EGG = bytes([0x88, 0x00, 0x01, 0x52, 0x00, 0x0A, 0xE5, 0x0D])

egg_matches = []
start = 0
while True:
    pos = CF.find(EGG, start)
    if pos == -1:
        break
    egg_matches.append(pos)
    start = pos + 1

check("egg appears exactly once in CodeFlash", len(egg_matches) == 1, f"{len(egg_matches)} matches")

if egg_matches:
    egg_va = egg_matches[0]

    # PIN: exact address is 0x3485A
    check("egg address is VA 0x3485A", egg_va == 0x3485A, hex(egg_va))

    check("egg encodes known memcmp prologue", CF[egg_va:egg_va + 8] == EGG)

    # PIN: the two direct callers of the SID-0xBA shared token comparator
    # FUN_00034882 at 0x34882 calls 0x3485A from 0x34898 (jarl)
    # historical symbol application_proprietary_ab_f1_start is BA F1/JTEKM and calls 0x3485A at 0x34B80

    def jarl_target(call_site):
        """Decode an RH850 jarl instruction's target address.

        jarl is a 32-bit (2-halfword) instruction. The 13-bit signed
        displacement is in bits 12:0 of the second halfword (no shift —
        RH850 instructions are 16-bit aligned but the displacement is in
        raw bytes here)."""
        hw1 = struct.unpack_from("<H", CF, call_site)[0]
        if hw1 != 0xFFBF:
            return None
        hw2 = struct.unpack_from("<H", CF, call_site + 2)[0]
        disp = hw2 & 0x1FFF
        if disp & 0x1000:
            disp -= 0x2000
        return call_site + disp

    t1 = jarl_target(0x34898)
    check("FUN_00034882 calls egg at 0x34898",
          t1 == 0x3485A,
          hex(t1) if t1 is not None else "not a jarl")

    t2 = jarl_target(0x34B80)
    check("BA F1/JTEKM callback calls shared comparator at 0x34B80",
          t2 == 0x3485A,
          hex(t2) if t2 is not None else "not a jarl")

    # The patch would overwrite +0..3 with 01 52 7f 00:
    #   +0: 0152   mov 1, r10    (return = 1)
    #   +2: 7f00   jmp [lp]      (return immediately)
    # This makes the function always return "match" for BA token comparisons,
    # not SecOC; F7's independent SA2 gate remains elsewhere. The effect is
    # documented but not asserted here as a firmware
    # fact (it's an analysis of the hypothetical patch, not a byte check).

    # The actual SecOC MAC verification function is secoc_rx_verify_worker at 0x8E4BA.
    # Its prologue bytes are completely different.
    secoc_prologue = CF[0x8E4BA:0x8E4BA + 8]
    check(
        "SecOC verify worker 0x8E4BA prologue != egg",
        secoc_prologue != EGG,
        f"0x8E4BA: {secoc_prologue.hex()} vs egg: {EGG.hex()}",
    )

    # Distance confirms they are unrelated functions
    distance = 0x8E4BA - egg_va
    check(
        "egg and SecOC worker are ~0x59C60 bytes apart (unrelated)",
        distance > 0x10000,
        f"distance: 0x{distance:X}",
    )


# ---- 7. CRC geometry and resigning are valid; public region 1 has a one-bit anomaly ----
print("\n== 7. CRC geometry, resigning, and published-dump anomaly ==")

r1_crc_addr = struct.unpack_from("<I", CF, 0xFFDE0)[0]
r1_crc_len = struct.unpack_from("<I", CF, 0xFFDE4)[0]
crc_range_end = r1_crc_addr + r1_crc_len

check("CRC range starts at 0x18000 (shellcode CRC_RANGE_START)", r1_crc_addr == 0x18000)
check("CRC range ends at 0xFFDF0", crc_range_end == 0xFFDF0)
check("CRC adjustment word at 0xFFDEC is 4 bytes before range end", 0xFFDF0 - 0xFFDEC == 4)
check("CRC adjustment block is 0xF8000 (last 32KB block)", 0xFFDEC >= 0xF8000 and 0xFFDEC < 0xF8000 + 0x8000)
check("region 1 marker at 0xFFE00 (shellcode SCAN_END)", struct.unpack_from("<I", CF, 0xFFE00)[0] == 0x5AA5A55A)

# Region 0 is a stock in-image fixture for the exact community formula:
# CRC(prefix) ^ 0xFFFFFFFF is stored as the terminal little-endian word, and
# the complete region then has residue 0xFFFFFFFF.
r0_pre = community_crc32(CF[0x10000:0x17DEC])
r0_adj = struct.unpack_from("<I", CF, 0x17DEC)[0]
check("region 0 prefix CRC is 0xEC0CD6CF", r0_pre == 0xEC0CD6CF)
check("region 0 stock adjustment equals complemented prefix CRC",
      r0_adj == (r0_pre ^ 0xFFFFFFFF) == 0x13F32930)
check("region 0 complete CRC residue is 0xFFFFFFFF",
      community_crc32(CF[0x10000:0x17DF0]) == 0xFFFFFFFF)

# The public 4512000 high region is anomalous as published, but the mismatch is
# explained exactly by one bit at 0xBB1C4. Clearing bit 5 (A2 -> 82) makes the
# existing stock word at 0xFFDEC valid without changing the CRC algorithm.
check("published region 1 residue is the known anomalous 0x5AA2313A",
      community_crc32(CF[r1_crc_addr:crc_range_end]) == 0x5AA2313A)
corrected = bytearray(CF)
check("published byte at 0xBB1C4 is 0xA2", corrected[0xBB1C4] == 0xA2)
corrected[0xBB1C4] = 0x82
corrected_pre = community_crc32(corrected[r1_crc_addr:0xFFDEC])
stock_adj = struct.unpack_from("<I", corrected, 0xFFDEC)[0]
check("one-bit reconstruction makes stock fixup exact",
      corrected_pre == 0xF69D7780
      and stock_adj == (corrected_pre ^ 0xFFFFFFFF) == 0x0962887F)
check("one-bit reconstructed region 1 residue is 0xFFFFFFFF",
      community_crc32(corrected[r1_crc_addr:crc_range_end]) == 0xFFFFFFFF)

# On the reconstructed stock image, our calibration-specific Gate-2 patch has a
# deterministic replacement adjustment. The live patcher would derive this from
# the real ECU contents rather than needing the number hardcoded.
patched = bytearray(corrected)
patched[0x8E6C6:0x8E6C8] = bytes.fromhex("e001")
patched_pre_adj = community_crc32(patched[r1_crc_addr:0xFFDEC])
patched_adj = patched_pre_adj ^ 0xFFFFFFFF
struct.pack_into("<I", patched, 0xFFDEC, patched_adj)
check("reconstructed corrected Gate-2 patch adjustment is 0x41C90FF2",
      patched_pre_adj == 0xBE36F00D and patched_adj == 0x41C90FF2,
      f"pre=0x{patched_pre_adj:08X} adjustment=0x{patched_adj:08X}")
check("reconstructed Gate-2 patched region validates to 0xFFFFFFFF",
      community_crc32(patched[r1_crc_addr:crc_range_end]) == 0xFFFFFFFF)


print(f"\n== RESULT: {ok} passed, {bad} failed ==")
sys.exit(1 if bad else 0)
