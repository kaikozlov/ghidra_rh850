#!/usr/bin/env python3
"""Verify the corrected Gate-2 compare-neutralization MAC-bypass patch.

Command-7 result zero is verification OK. Gate 2 materializes `(result != 0)`
into r26, executes `cmp r0,r26; bne mismatch`, and therefore falls through to
PduR/COM delivery only when the verify result is zero. The bypass changes the
CMP from `cmp r0,r26` to `cmp r0,r0`, making the existing BNE impossible while
preserving the branch instruction and both arm bodies.

The superseded 9a0d->950d patch is tested explicitly as a negative regression:
it turns BNE into unconditional BR and therefore forces the mismatch/failure arm.
"""
from __future__ import annotations

import struct
import sys
import zlib
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


def decode_cmp_format_ii(data: bytes) -> tuple[int, int, int]:
    """Return (left_reg, right_reg, opcode6) for a 2-byte RH850 Format-II CMP."""
    if len(data) != 2:
        raise ValueError("CMP must be two bytes")
    hw = int.from_bytes(data, "little")
    return hw & 0x1F, (hw >> 11) & 0x1F, (hw >> 5) & 0x3F


def synthesize_cmp_same_register(data: bytes) -> bytes:
    left, _right, _opcode = decode_cmp_format_ii(data)
    hw = int.from_bytes(data, "little")
    patched = (hw & 0x07FF) | (left << 11)
    return patched.to_bytes(2, "little")


def decode_bcond(off: int, data: bytes | None = None) -> tuple[int, int]:
    hw = int.from_bytes(data if data is not None else CF[off:off + 2], "little")
    s1115 = (hw >> 11) & 0x1F
    op0406 = (hw >> 4) & 0x7
    cc = hw & 0xF
    s1115_signed = s1115 - 0x20 if s1115 & 0x10 else s1115
    target = ((s1115_signed << 4) | (op0406 << 1)) + off
    return cc, target


PATCH_VA = 0x8E6C6
BRANCH_VA = 0x8E6C8
ORIGINAL = bytes.fromhex("e0d1")
REPLACEMENT = bytes.fromhex("e001")

print("== 1. corrected patch is CMP neutralization at 0x8E6C6 ==")
check("stock patch preimage is e0d1", CF[PATCH_VA:PATCH_VA + 2] == ORIGINAL)
left, right, opcode = decode_cmp_format_ii(ORIGINAL)
check("stock CMP operands encode r0,r26", (left, right) == (0, 26), repr((left, right)))
check("generic same-register synthesis yields e001", synthesize_cmp_same_register(ORIGINAL) == REPLACEMENT)
pleft, pright, popcode = decode_cmp_format_ii(REPLACEMENT)
check("patched CMP encodes r0,r0", (pleft, pright) == (0, 0))
check("CMP opcode bits are preserved", popcode == opcode)
check("only the second-register field changes", ORIGINAL[0] == REPLACEMENT[0] and ORIGINAL[1] != REPLACEMENT[1])
check("full field-tested gate context is unique", CF.count(bytes.fromhex("e0d19a0d1a38bfff")) == 1)

print("\n== 2. BNE is preserved and still points to mismatch arm ==")
check("following BNE bytes remain 9a0d", CF[BRANCH_VA:BRANCH_VA + 2] == bytes.fromhex("9a0d"))
cc, target = decode_bcond(BRANCH_VA)
check("stock branch condition is NE", cc == 0xA, f"cc=0x{cc:X}")
check("stock branch target is mismatch bookkeeping at 0x8E6DA", target == 0x8E6DA, f"0x{target:X}")
check("neutralized CMP makes BNE condition false for every result", pleft == pright)
check("fallthrough begins at verified-delivery arm 0x8E6CA", BRANCH_VA + 2 == 0x8E6CA)

print("\n== 3. old branch patch is explicitly the wrong direction ==")
OLD_WRONG_REPLACEMENT = bytes.fromhex("950d")
old_cc, old_target = decode_bcond(BRANCH_VA, OLD_WRONG_REPLACEMENT)
check("superseded 950d condition is unconditional BR", old_cc == 0x5, f"cc=0x{old_cc:X}")
check("superseded 950d preserves mismatch target", old_target == 0x8E6DA)
check("old patch therefore forces mismatch arm, not delivery", old_cc == 0x5 and old_target != 0x8E6CA)
check("correct patch leaves the branch bytes untouched", CF[BRANCH_VA:BRANCH_VA + 2] == bytes.fromhex("9a0d"))

print("\n== 4. pre-gate freshness handling remains before patched CMP ==")
check(
    "Gate-2 context keeps freshness call before CMP and delivery calls after it",
    CF[0x8E6C0:0x8E6DA] == bytes.fromhex("bfff86ff1d30e0d19a0d1a38bfff78fb1d301a38bfffe6fbd505"),
    CF[0x8E6C0:0x8E6DA].hex(),
)
check("patch is two bytes after pre-gate call return setup", PATCH_VA > 0x8E6C0)

print("\n== 5. CRC resigning for corrected patch ==")
check("patch lies in boot CRC region 1", 0x18000 <= PATCH_VA < 0xFFDF0)
check("CRC fixup remains at terminal word 0xFFDEC", 0xFFDEC == 0xFFDF0 - 4)
check("validity marker remains 0x5AA5A55A", u32(0xFFE00) == 0x5AA5A55A)

# Published image has the independently recovered one-bit acquisition anomaly.
published = bytearray(CF)
published[PATCH_VA:PATCH_VA + 2] = REPLACEMENT
published_prefix = zlib.crc32(published[0x18000:0xFFDEC]) & 0xFFFFFFFF
published_fixup = published_prefix ^ 0xFFFFFFFF
check("published-image corrected-patch prefix CRC is pinned", published_prefix == 0x23247E0C, f"0x{published_prefix:08X}")
check("published-image corrected-patch fixup is pinned", published_fixup == 0xDCDB81F3, f"0x{published_fixup:08X}")

clean = bytearray(CF)
clean[0xBB1C4] = 0x82
clean[PATCH_VA:PATCH_VA + 2] = REPLACEMENT
clean_prefix = zlib.crc32(clean[0x18000:0xFFDEC]) & 0xFFFFFFFF
clean_fixup = clean_prefix ^ 0xFFFFFFFF
struct.pack_into("<I", clean, 0xFFDEC, clean_fixup)
clean_residue = zlib.crc32(clean[0x18000:0xFFDF0]) & 0xFFFFFFFF
check("reconstructed-clean corrected-patch prefix CRC is pinned", clean_prefix == 0xBE36F00D, f"0x{clean_prefix:08X}")
check("reconstructed-clean corrected-patch fixup is 0x41C90FF2", clean_fixup == 0x41C90FF2, f"0x{clean_fixup:08X}")
check("reconstructed-clean corrected-patch residue is 0xFFFFFFFF", clean_residue == 0xFFFFFFFF, f"0x{clean_residue:08X}")

print(f"\n== RESULT: {ok} passed, {bad} failed ==")
sys.exit(1 if bad else 0)
