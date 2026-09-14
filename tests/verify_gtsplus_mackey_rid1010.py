#!/usr/bin/env python3
"""Verify current GTS+ MACKey support for the RID-0x1010 M1-M5 transport."""
from __future__ import annotations

import hashlib
import struct
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
DLL = REPO / "software/Techstream/gtsplus/unpacked/gtsplus/Toyota Diagnostics/GTSPlus/bin/UtilityExNK2.dll"
DLL_SHA = "d9868c8a9a69ffbab26ea7d4431e290372cd207e84e7b4aed27446aeb4c12ec1"
IMAGE_BASE = 0x10000000
TEXT_RVA = 0x1000
TEXT_RAW = 0x400

if not DLL.exists():
    print("[SKIP] GTS+ unpacked tree is not present")
    raise SystemExit(77)

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


def raw_to_va(raw: int) -> int:
    return IMAGE_BASE + TEXT_RVA + raw - TEXT_RAW


def rel32_target(data: bytes, raw: int) -> int:
    assert data[raw] == 0xE8
    return (raw_to_va(raw) + 5 + struct.unpack_from("<i", data, raw + 1)[0]) & 0xFFFFFFFF


gts = DLL.read_bytes()

print("== pinned current GTS+ UtilityExNK2 ==")
check("UtilityExNK2.dll size is exact", len(gts) == 0x1DD810)
check("UtilityExNK2.dll SHA-256 is exact", sha256(gts) == DLL_SHA)
check("official Ex2MAC_01_ComProcess export name is retained", b"Ex2MAC_01_ComProcess\x00" in gts)

print("\n== direct MAC_01 RID-0x1010 transport ==")
check("start helper embeds 31 01 10 10", gts[0xF944F:0xF9453] == bytes.fromhex("31 01 10 10"))
check("poll helper embeds 31 03 10 10", gts[0xF9323:0xF9327] == bytes.fromhex("31 03 10 10"))
check("Ex2MAC_01_ComProcess body is exact", sha256(gts[0x27990:0x27A48]) == "c10bbe074523b5e8d52a0b7276719ecf58c5151b1622805d5f3825eb6ddb9fac")
check("RID-0x1010 MACKey state worker is exact", sha256(gts[0xF8B40:0xF8CE3]) == "4cf9e7be8cf0e633726133807934ada756e1a2b4f84a65a38bdf5730bc6b47a1")
check("RID-0x1010 result helper is exact", sha256(gts[0xF92F0:0xF93D8]) == "65bb750e20a1fa79081c04538a1b31e118a52bdb05f25fb138e4d53b757bc30e")
check("RID-0x1010 start helper is exact", sha256(gts[0xF93E0:0xF9510]) == "eca43913dac73436b13fd7751450f01aa5811382084ba2228d843f4c0252e502")
check("MACKey worker calls RID-0x1010 start helper", rel32_target(gts, 0xF9E11) == 0x100F9FE0)
check("MACKey worker calls RID-0x1010 result helper", rel32_target(gts, 0xF9E57) == 0x100F9EF0)
check("MACKey worker polls RID-0x1010 result helper again", rel32_target(gts, 0xF9E9E) == 0x100F9EF0)
check("Ex2MAC_01_ComProcess references 0x100F9740 state machine", struct.pack("<I", 0x100F9740) in gts[0x27990:0x27A48])

print("\n== newer RID-0x3002 transport intentionally coexists ==")
check("newer start helper embeds 31 01 30 02", gts[0x12C58D:0x12C591] == bytes.fromhex("31 01 30 02"))
check("newer poll helper embeds 31 03 30 02", gts[0x12B04C:0x12B050] == bytes.fromhex("31 03 30 02"))
check("RID-0x3002 result helper is byte-pinned", sha256(gts[0x12B010:0x12B12C]) == "40ae4fc66a2a512a80ebbd72170a2df77a8949979ed4305b34d206e6bee41bf9")
check("RID-0x3002 start helper is byte-pinned", sha256(gts[0x12C570:0x12C664]) == "cc2903dda7ff92b583daf8544e69069d3bff9174534cde3fd671c87b4ad0fa63")

print(f"\nResults: {passed} passed, {failed} failed")
raise SystemExit(1 if failed else 0)
