#!/usr/bin/env python3
"""Verify boot CodeFlash CRC resigning and the region-1 dump anomaly.

The committed 8965B4512000 CodeFlash artifact is preserved byte-for-byte as
published. Its high CodeFlash boot-CRC region does not validate as-is, but the
syndrome has exactly one single-bit correction: VA 0xBB1C4 bit 5, A2 -> 82.
That same bit change repairs an obviously anomalous RH850 `sst.b` displacement
from 0x22 to 0x02, turning the surrounding six destination offsets into an exact
permutation of 0..5.

The boot CRC scheme itself is not in doubt: region 0 is a stock known-good
fixture for the same CRC-32/Ethernet + terminal complement-word construction
used by the community flash patcher. Reconstructing the single bad bit makes
region 1's existing fixup word validate exactly, and the verified Gate-2 patch
then re-signs with fixup 0x91698386.
"""
from __future__ import annotations

import hashlib
import struct
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
CF = (REPO / "firmware" / "RH850_P1M-E_CodeFlash.bin").read_bytes()
POLY = 0xEDB88320

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


def u32(off: int) -> int:
    return struct.unpack_from("<I", CF, off)[0]


def crc32_ethernet(data: bytes | bytearray) -> int:
    """CRC-32/Ethernet exactly as implemented by community main.c."""
    crc = 0xFFFFFFFF
    for byte in data:
        crc ^= byte
        for _ in range(8):
            crc = (crc >> 1) ^ POLY if crc & 1 else crc >> 1
    return (crc ^ 0xFFFFFFFF) & 0xFFFFFFFF


def single_bit_fixes(data: bytes, current_crc: int, target_crc: int) -> list[tuple[int, int]]:
    """Return (byte_offset, bit_index) flips that change current_crc to target_crc.

    CRC differences are linear. For a reflected CRC, a flipped final input bit
    contributes POLY to the raw state; repeatedly applying the zero-input state
    transition walks that influence backward across every earlier stream bit.
    Final XOR cancels in the CRC difference.
    """
    delta = current_crc ^ target_crc
    total_bits = len(data) * 8
    effect = POLY
    fixes: list[tuple[int, int]] = []
    for distance_from_end in range(total_bits):
        if effect == delta:
            stream_bit = total_bits - 1 - distance_from_end
            fixes.append((stream_bit // 8, stream_bit % 8))
        effect = ((effect >> 1) ^ (POLY if effect & 1 else 0)) & 0xFFFFFFFF
    return fixes


print("== 0. canonical published artifact ==")
check(
    "published CodeFlash hash remains pinned",
    hashlib.sha256(CF).hexdigest()
    == "21140bbd65e530a9e518a3e84e20e5d85679675bc09cc724cb177bb7c76bafde",
)

print("\n== 1. boot CRC descriptors and DCRA feed shape ==")
check("region 0 descriptor", (u32(0x8DD0), u32(0x8DD4)) == (0x10000, 0x7DF0))
check("region 1 descriptor", (u32(0x8DE0), u32(0x8DE4)) == (0x18000, 0xE7DF0))
# crc32_hardware_compute @ 0x47EA: EP=FFD51004, clears EP+0x1C control,
# seeds EP+0 with r8, writes each loaded 32-bit word to FFD51000, reads COUT,
# and returns NOT(COUT). Pin the decisive raw instructions.
check("DCRA control is cleared before feed", CF[0x47F0:0x47F2] == bytes.fromhex("9c03"))
check("caller seed is written to DCRA COUT", CF[0x47F4:0x47F6] == bytes.fromhex("0145"))
check("32-bit words are fed to DCRA CIN", CF[0x4802:0x4808] == bytes.fromhex("80070f9820aa"))
check("DCRA COUT is read then complemented", CF[0x4810:0x4818] == bytes.fromhex("8007490820aa2150"))

print("\n== 2. region 0 is an in-image CRC resigning fixture ==")
r0_start = 0x10000
r0_fixup = 0x17DEC
r0_end = 0x17DF0
r0_pre = crc32_ethernet(CF[r0_start:r0_fixup])
r0_stored = u32(r0_fixup)
r0_full = crc32_ethernet(CF[r0_start:r0_end])
check("region 0 prefix CRC", r0_pre == 0xEC0CD6CF, f"0x{r0_pre:08X}")
check("region 0 stores complement of prefix CRC", r0_stored == (r0_pre ^ 0xFFFFFFFF) == 0x13F32930)
check("region 0 final residue is 0xFFFFFFFF", r0_full == 0xFFFFFFFF, f"0x{r0_full:08X}")

print("\n== 3. published region-1 anomaly has one unique single-bit repair ==")
r1_start = 0x18000
r1_fixup = 0xFFDEC
r1_end = 0xFFDF0
r1_published = crc32_ethernet(CF[r1_start:r1_end])
check("published region 1 has observed non-final residue", r1_published == 0x5AA2313A, f"0x{r1_published:08X}")
fixes = single_bit_fixes(CF[r1_start:r1_end], r1_published, 0xFFFFFFFF)
expected_relative = 0xBB1C4 - r1_start
check(
    "exactly one single-bit correction reaches the expected residue",
    fixes == [(expected_relative, 5)],
    repr([(hex(r1_start + off), bit) for off, bit in fixes]),
)
check("published candidate byte is 0xA2", CF[0xBB1C4] == 0xA2)

print("\n== 4. the same bit repairs the local instruction semantics ==")
# Six sst.b instructions in FUN_000BB0A2 copy consecutive source bytes into a
# six-byte destination. For these short stores, the low seven bits encode the
# EP-relative byte displacement. The published A2 encodes 0x22; clearing bit 5
# gives 82 -> displacement 2.
store_vas = [0xBB1BE, 0xBB1C4, 0xBB1CA, 0xBB1D0, 0xBB1D6, 0xBB1DC]
published_offsets = [CF[va] & 0x7F for va in store_vas]
corrected_offsets = published_offsets.copy()
corrected_offsets[1] = 0x82 & 0x7F
check("published six store offsets contain anomalous 0x22", published_offsets == [1, 0x22, 0, 4, 5, 3], repr(published_offsets))
check("A2 -> 82 is exactly bit-5 clear", (0xA2 ^ 0x82) == 0x20)
check("corrected store offsets are a permutation of 0..5", corrected_offsets == [1, 2, 0, 4, 5, 3] and sorted(corrected_offsets) == list(range(6)), repr(corrected_offsets))

print("\n== 5. reconstructed stock region 1 validates its existing fixup ==")
corrected = bytearray(CF)
corrected[0xBB1C4] = 0x82
corrected_pre = crc32_ethernet(corrected[r1_start:r1_fixup])
stock_fixup = struct.unpack_from("<I", corrected, r1_fixup)[0]
corrected_full = crc32_ethernet(corrected[r1_start:r1_end])
check("corrected region-1 prefix CRC", corrected_pre == 0xF69D7780, f"0x{corrected_pre:08X}")
check("existing stock fixup is exactly complement of corrected prefix", stock_fixup == (corrected_pre ^ 0xFFFFFFFF) == 0x0962887F, f"0x{stock_fixup:08X}")
check("corrected stock region-1 residue is 0xFFFFFFFF", corrected_full == 0xFFFFFFFF, f"0x{corrected_full:08X}")
check(
    "reconstructed CodeFlash hash is stable",
    hashlib.sha256(corrected).hexdigest() == "b6f510662c324261dac6fc1504ec77c217d2055dc099096375a91f3fcf7e9916",
)

print("\n== 6. Gate-2 patch re-signs on reconstructed stock image ==")
patched = bytearray(corrected)
patched[0x8E6C8] = 0x95
patched_pre = crc32_ethernet(patched[r1_start:r1_fixup])
patched_fixup = patched_pre ^ 0xFFFFFFFF
struct.pack_into("<I", patched, r1_fixup, patched_fixup)
patched_full = crc32_ethernet(patched[r1_start:r1_end])
check("Gate-2 patched prefix CRC", patched_pre == 0x6E967C79, f"0x{patched_pre:08X}")
check("Gate-2 patched fixup is 0x91698386", patched_fixup == 0x91698386, f"0x{patched_fixup:08X}")
check("Gate-2 patched region residue is 0xFFFFFFFF", patched_full == 0xFFFFFFFF, f"0x{patched_full:08X}")

print(f"\n== RESULT: {ok} passed, {bad} failed ==")
sys.exit(1 if bad else 0)
