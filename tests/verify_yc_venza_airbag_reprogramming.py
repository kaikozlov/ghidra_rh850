#!/usr/bin/env python3
"""Verify the yc Venza airbag reprogramming/extended-user-area invariants."""
from __future__ import annotations

import hashlib
import struct
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
BOOT = REPO / "community/yc/venza/boot.bin"
CFLASH = REPO / "community/yc/venza/cflash.bin"

BOOT_SHA = "943934abc9a5c676eff46f51f008baa39e4f533e66650ffcce54d7bfb6e6e6e2"
CFLASH_SHA = "2dfaf7ce21cb04af1126192f574103f63802352f8717fa0f03986d5a11d067f9"
COPY = struct.Struct("<III")
SERVICE = struct.Struct("<IIIIBBBBB3x")
SUBFUNCTION = struct.Struct("<IIIHH")

passed = failed = 0


def check(name: str, condition: object, detail: str = "") -> None:
    global passed, failed
    ok = bool(condition)
    passed += int(ok)
    failed += int(not ok)
    suffix = f" ({detail})" if detail else ""
    print(f"[{'PASS' if ok else 'FAIL'}][raw_bytes] {name}{suffix}")


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


boot = BOOT.read_bytes()
cf = CFLASH.read_bytes()

print("== immutable contributor artifacts ==")
check("boot.bin is the exact 32-KiB artifact", len(boot) == 0x8000 and sha256(boot) == BOOT_SHA)
check("cflash.bin is the exact 3-MiB artifact", len(cf) == 0x300000 and sha256(cf) == CFLASH_SHA)
check("RPRG build tag is at the extended-user tail", boot[0x7FD0:0x7FE2] == b"AUBIST_RPRG_201902")
check("raw airbag identity 8917048E30 is retained", cf[0x17FFC6:0x17FFD0] == b"8917048E30")
check("raw airbag identity 8917F48692 is retained", cf[0x17FFD0:0x17FFDA] == b"8917F48692")

print("\n== extended-user image is a split RAM-loaded RPRG segment ==")
check("first relocation group header is exact", struct.unpack_from("<II", cf, 0x1914) == (3, 0x1954))
check("second relocation group header is exact", struct.unpack_from("<II", cf, 0x191C) == (3, 0x1978))
first_group = [COPY.unpack_from(cf, 0x1954 + i * COPY.size) for i in range(3)]
second_group = [COPY.unpack_from(cf, 0x1978 + i * COPY.size) for i in range(3)]
check("CodeFlash runtime segment ends at logical 0xA304", first_group[0] == (0xFEBEA7B0, 0x4190, 0xA304))
check("extended user 0x01000000..0x01007588 copies to FEBF0924", first_group[1] == (0xFEBF0924, 0x01000000, 0x01007588))
check("extended user 0x01007588..0x01007BD0 copies to FEBFBF90", second_group[1] == (0xFEBFBF90, 0x01007588, 0x01007BD0))
check("relocated CodeFlash seam is contiguous with RPRG destination", first_group[0][0] + (first_group[0][2] - first_group[0][1]) == first_group[1][0])
check("logical call at 0x83E0 retains the A304 split-image target encoding", cf[0x83E0:0x83E6] == bytes.fromhex("ff02241f0000"))

print("\n== DiagnosticSessionControl programming route ==")
svc10 = SERVICE.unpack_from(cf, 0x23C18)
check("service group has SID 0x10 with five subfunctions", svc10 == (0, 0, 0, 0x237D0, 0x10, 1, 0, 0, 5))
programming = SUBFUNCTION.unpack_from(cf, 0x237E0)
check("SID 0x10 subfunction 0x02 dispatches to C190C", programming == (0xC190C, 0, 0x2356A, 0x02, 3))
check("programming subfunction permits current sessions 1/3/2", cf[0x2356A:0x2356D] == bytes([1, 3, 2]))
check("C190C wrapper is exact", cf[0xC190C:0xC191C] == bytes.fromhex("800721008600024280ffc41940063f00"))

print("\n== retained programming handoff ==")
check(
    "handoff writer targets FEF0FFD0 and embeds 5AA5A55A",
    cf[0xC76C6:0xC7728]
    == bytes.fromhex(
        "3e06d0fff0fe020a800b81038203079a839b209e8000849b8503860387038803"
        "209e1000899b019a8a9b8b0b8c038d038e038f03900391039203930394039503"
        "96039703980399039a039b039c039d039e039f0321065aa5a55a405ef1fe6b0f"
        "f1ff"
    ),
)
check(
    "session event 6 performs the two 0x200 hardware writes then halt path",
    cf[0xC780E:0xC7838]
    == bytes.fromhex(
        "86006632ea0d200e000280078f0e0ef080078f0e10f0e0076001e00720018505"
        "00527f0000527f00405e"
    ),
)
check(
    "startup magic test is exact",
    cf[0x17BC:0x17D2] == bytes.fromhex("409ef1fe339ff1ff21065aa5a55ae199ea5700007f00"),
)
check("startup immediately has a dedicated magic-clear helper", cf[0x17D2:0x17DC] == bytes.fromhex("405ef1fe6b07f1ff7f00"))

print(f"\nResults: {passed} passed, {failed} failed")
raise SystemExit(1 if failed else 0)
