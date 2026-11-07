#!/usr/bin/env python3
"""Verify the minimal persistent write+exec patch design across registered EPS CodeFlash images.

For Camry F33 and both Corollas: pin every firmware fact the design in
docs/security/minimal-write-exec-patch.md relies on, reconstruct the patched
image deterministically, and assert the boot-validity invariants (CRC
residues, markers, change set). For Crown: pin the census result that the XCP
command family is absent, so the design's non-transfer is machine-checked too.
"""
from __future__ import annotations

import hashlib
import zlib
import struct
from typing import NamedTuple

from tools import REPO_ROOT

STUB = bytes.fromhex("1fa040aebffe35b7017c96bf01001f001c00f6c760f92056 5a007400".replace(" ", ""))
GATE_STOCK = 0x5A
GATE_PATCHED = 0x00
REGION0_RANGE = (0x10000, 0x17DF0)
REGION1_RANGE = (0x18000, 0xFFDF0)
REGION1_FIXUP_VA = 0xFFDEC
MARKER0_VA, MARKER1_VA = 0x17E00, 0xFFE00
MARKER_WORD = 0x5AA5A55A

class Target(NamedTuple):
    name: str
    sha_expect: str | None
    gate_va: int
    table: int
    f3: int
    f3_end: int
    window: tuple[int, int]
    mpu: tuple[int, int]
    fixup_expect: bytes


# name, image, sha256, gate VA, custom-table base, F3 handler, F3 end (EB row),
# window cells, MPU bounds, patched region-1 fixup
TRANSFER_TARGETS = [
    Target(
        "camry-8965F3307000",
        "42dce8efc42f6ae31718e7713fa2d26bb9191b4a82439778aee4d7afded9b0e7",
        0x30D68, 0x2B250, 0x99266, 0x9930E,
        (0x2B21C, 0x2B220), (0x31690, 0x31694),
        bytes.fromhex("f06e82d1"),
    ),
    Target(
        "corolla-8965H1202000",
        None,
        0x2CAA0, 0x2AE38, 0x92576, 0x9261E,
        (0x2AE04, 0x2AE08), (0x2D1EC, 0x2D1F0),
        bytes.fromhex("aa618db6"),
    ),
    Target(
        "corolla-8965F1208000",
        None,
        0x2CAA0, 0x2AE38, 0x92576, 0x9261E,
        (0x2AE04, 0x2AE08), (0x2D1EC, 0x2D1F0),
        bytes.fromhex("aa618db6"),
    ),
]

CROWN_IMAGE = "firmware/crown-8965F3012000/CodeFlash.bin"
CROWN_FEBF7C00_SITES = [0x1428, 0x31338, 0x62AD6]
CROWN_MPU_BOUNDS = (0x31338, 0x3133C)

passed = failed = 0


def check(name: str, cond: object, detail: str = "") -> None:
    global passed, failed
    ok = bool(cond)
    passed += ok
    failed += not ok
    print(f"[{'PASS' if ok else 'FAIL'}][patch_design] {name}" + (f" ({detail})" if detail else ""))


def u32(buf: bytes, va: int) -> int:
    return struct.unpack_from("<I", buf, va)[0]


def solve_fixup(prefix: bytes, target: int = 0xFFFFFFFF) -> bytes:
    """Four file-order bytes X with crc32(prefix + X) == target (affine GF(2) solve)."""
    f0 = zlib.crc32(prefix + b"\0\0\0\0")
    basis: dict[int, tuple[int, int]] = {}
    for i in range(32):
        cur, pat = zlib.crc32(prefix + (1 << i).to_bytes(4, "little")) ^ f0, 1 << i
        for pivot in sorted(basis, reverse=True):
            if (cur >> pivot) & 1:
                cc, pp = basis[pivot]
                cur ^= cc
                pat ^= pp
        if cur:
            basis[cur.bit_length() - 1] = (cur, pat)
    cur, pat = target ^ f0, 0
    for pivot in sorted(basis, reverse=True):
        if (cur >> pivot) & 1:
            cc, pp = basis[pivot]
            cur ^= cc
            pat ^= pp
    if cur:
        raise AssertionError("crc fixup system not solvable")
    return pat.to_bytes(4, "little")


def verify_transfer_target(name: str, sha_expect: str | None, gate_va: int, table: int,
                           f3: int, f3_end: int, window: tuple[int, int],
                           mpu: tuple[int, int], fixup_expect: bytes) -> None:
    stock = (REPO_ROOT / f"firmware/{name}/CodeFlash.bin").read_bytes()
    f3_row = table + 3 * 8
    print(f"== {name}: stock facts ==")
    check(f"{name}: 1 MiB image", len(stock) == 0x100000)
    if sha_expect:
        check(f"{name}: exact stock identity", hashlib.sha256(stock).hexdigest() == sha_expect)
    check(f"{name}: XCP ingress gate byte is 0x5A at {gate_va:#x}", stock[gate_va] == GATE_STOCK)
    check(f"{name}: F3 table row selects the sacrificial handler",
          stock[f3_row] == 0xF3 and u32(stock, f3_row + 4) == f3)
    check(f"{name}: sacrificial body extent reaches the EB selector row",
          f3 + len(STUB) < f3_end and stock[f3_row + 8] == 0xEB and u32(stock, f3_row + 12) == f3_end)
    check(f"{name}: write window cells are FEBF7C00/FEBFFBFF",
          u32(stock, window[0]) == 0xFEBF7C00 and u32(stock, window[1]) == 0xFEBFFBFF)
    check(f"{name}: MPU region bounds the window FEBF7C00..FEBFFBFC",
          u32(stock, mpu[0]) == 0xFEBF7C00 and u32(stock, mpu[1]) == 0xFEBFFBFC)
    check(f"{name}: region CRC residues are FFFFFFFF",
          zlib.crc32(stock[slice(*REGION0_RANGE)]) == 0xFFFFFFFF
          and zlib.crc32(stock[slice(*REGION1_RANGE)]) == 0xFFFFFFFF)
    check(f"{name}: validity markers present",
          u32(stock, MARKER0_VA) == MARKER_WORD and u32(stock, MARKER1_VA) == MARKER_WORD)
    check(f"{name}: solver reproduces the stock region-1 fixup",
          solve_fixup(stock[REGION1_RANGE[0]:REGION1_FIXUP_VA]) == stock[REGION1_FIXUP_VA:REGION1_FIXUP_VA + 4])

    print(f"== {name}: patched image ==")
    patched = bytearray(stock)
    patched[gate_va] = GATE_PATCHED
    patched[f3:f3 + len(STUB)] = STUB
    fixup = solve_fixup(bytes(patched[REGION1_RANGE[0]:REGION1_FIXUP_VA]))
    patched[REGION1_FIXUP_VA:REGION1_FIXUP_VA + 4] = fixup
    check(f"{name}: patched region-1 fixup matches the documented value",
          fixup == fixup_expect, fixup.hex())
    check(f"{name}: patched region CRC residues are FFFFFFFF",
          zlib.crc32(bytes(patched[slice(*REGION0_RANGE)])) == 0xFFFFFFFF
          and zlib.crc32(bytes(patched[slice(*REGION1_RANGE)])) == 0xFFFFFFFF)
    check(f"{name}: validity markers unchanged",
          u32(patched, MARKER0_VA) == MARKER_WORD and u32(patched, MARKER1_VA) == MARKER_WORD)
    diffs = [i for i in range(len(stock)) if patched[i] != stock[i]]
    in_gate = [i for i in diffs if i == gate_va]
    in_stub = [i for i in diffs if f3 <= i < f3 + len(STUB)]
    in_fixup = [i for i in diffs if REGION1_FIXUP_VA <= i < REGION1_FIXUP_VA + 4]
    check(f"{name}: change set is exactly gate + stub + fixup",
          len(diffs) == len(in_gate) + len(in_stub) + len(in_fixup) and len(in_gate) == 1
          and 0 < len(in_stub) <= len(STUB) and len(in_fixup) == 4,
          f"{len(diffs)} bytes")
    check(f"{name}: boot region and region 0 untouched", all(i >= REGION1_RANGE[0] for i in diffs))


def verify_sienna_gate_facts() -> None:
    """Sienna is the glitch-dumped image: stock byte facts only, no patched-image construction."""
    img = (REPO_ROOT / "firmware/RH850_P1M-E_CodeFlash.bin").read_bytes()
    print("== sienna-8965B4512000: family gate facts ==")
    check("sienna: XCP ingress gate byte is 0x5A at 0x30EF4", img[0x30EF4] == GATE_STOCK)
    check("sienna: F3 table row selects the sacrificial handler",
          img[0x2B3F0 + 24] == 0xF3 and u32(img, 0x2B3F0 + 28) == 0x97546)
    check("sienna: sacrificial body extent reaches the EB selector row",
          0x97546 + len(STUB) < 0x975EE and img[0x2B3F0 + 32] == 0xEB
          and u32(img, 0x2B3F0 + 36) == 0x975EE)
    check("sienna: write window cells are FEBF7C00/FEBFFBFF",
          u32(img, 0x2B3BC) == 0xFEBF7C00 and u32(img, 0x2B3C0) == 0xFEBFFBFF)
    check("sienna: MPU region bounds the window FEBF7C00..FEBFFBFC",
          u32(img, 0x3181C) == 0xFEBF7C00 and u32(img, 0x31820) == 0xFEBFFBFC)



def verify_tundra_census() -> None:
    """Both committed Tundra EPS application images lack the XCP module, matching Crown."""
    for part in ("tundra-8965F3401200", "tundra-8965F3402200"):
        img = (REPO_ROOT / f"firmware/{part}/Application.bin").read_bytes()
        has_table = any(
            img[k] == 0xFB and img[k + 8] == 0xFA and img[k + 16] == 0xF5 and img[k + 24] == 0xF3
            and img[k + 32] == 0xEB and img[k + 40] == 0xEA and img[k + 48] == 0xE4
            for k in range(0x800, len(img) - 56)
        )
        cells = sum(u32(img, a) == 0xFEBFFBFF for a in range(0, len(img) - 4, 4))
        sites = sum(u32(img, a) == 0xFEBF7C00 for a in range(0, len(img) - 4, 4))
        check(f"{part}: no custom XCP selector table", not has_table)
        check(f"{part}: no write-window upper cell", cells == 0)
        check(f"{part}: only shadow/MPU FEBF7C00 occurrences", 0 < sites <= 2, str(sites))

def verify_crown_census() -> None:
    img = (REPO_ROOT / CROWN_IMAGE).read_bytes()
    print("== crown-8965F3012000: XCP-absent census ==")
    sites, i = [], 0
    pat = struct.pack("<I", 0xFEBF7C00)
    while True:
        j = img.find(pat, i)
        if j < 0:
            break
        sites.append(j)
        i = j + 1
    check("crown: FEBF7C00 occurs only at startup clear, MPU bounds, shadow copy",
          sites == CROWN_FEBF7C00_SITES, ", ".join(hex(s) for s in sites))
    check("crown: no write-window pointer cell pair (FEBF7C00,FEBFFBFF)",
          all(u32(img, a + 4) != 0xFEBFFBFF for a in sites))
    check("crown: MPU window bounds present", u32(img, CROWN_MPU_BOUNDS[0]) == 0xFEBF7C00
          and u32(img, CROWN_MPU_BOUNDS[1]) == 0xFEBFFBFC)
    has_table = any(
        img[k] == 0xFB and img[k + 8] == 0xFA and img[k + 16] == 0xF5 and img[k + 24] == 0xF3
        and img[k + 32] == 0xEB and img[k + 40] == 0xEA and img[k + 48] == 0xE4
        for k in range(0x10000, len(img) - 56)
    )
    check("crown: no custom XCP selector table anywhere", not has_table)
    check("crown: boot region table and markers transfer",
          u32(img, 0x8E00) == 0x10000 and u32(img, 0x8E00 + 28) == 0x18000
          and u32(img, 0x8E00 + 56) == 0xFEBF0000
          and u32(img, MARKER0_VA) == MARKER_WORD and u32(img, MARKER1_VA) == MARKER_WORD
          and zlib.crc32(img[slice(*REGION0_RANGE)]) == 0xFFFFFFFF
          and zlib.crc32(img[slice(*REGION1_RANGE)]) == 0xFFFFFFFF)


def main() -> int:
    for cfg in TRANSFER_TARGETS:
        verify_transfer_target(*cfg)
    verify_crown_census()
    verify_tundra_census()
    verify_sienna_gate_facts()
    print(f"\n{passed} passed, {failed} failed")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
