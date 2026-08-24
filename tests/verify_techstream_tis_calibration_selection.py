#!/usr/bin/env python3
"""Verify Toyota/TIS calibration-result parsing and candidate selection.

This suite independently pins the V18 Techstream host-side bridge between the
ECU-supply-change search response and the get-cal request.  It verifies the
response schema, the wired/update policy fields, the concrete selectSwInfo
software identifiers, normalization into 0x64-byte target records, local-file
filtering, and final swNo/fileName/swType serialization.  It does not infer
Toyota server-side matching rules or package availability.
"""
from __future__ import annotations

import hashlib
import sys
from pathlib import Path

import pefile

REPO = Path(__file__).resolve().parents[1]
ROOT = REPO / "Techstream/unpacked/toyota/Toyota Diagnostics/Techstream"
BIN = ROOT / "bin"
TECH = BIN / "Techstream.exe"

passed = failed = 0
oracle = "independent_external_artifact+raw_bytes"


def check(name: str, condition: object, detail: str = "") -> None:
    global passed, failed
    ok = bool(condition)
    passed += int(ok)
    failed += int(not ok)
    print(f"[{'PASS' if ok else 'FAIL'}][{oracle}] {name}" + (f" ({detail})" if detail else ""))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def off(pe: pefile.PE, va: int) -> int:
    return pe.get_offset_from_rva(va - pe.OPTIONAL_HEADER.ImageBase)


def anchor(data: bytes, pe: pefile.PE, va: int, hex_bytes: str) -> bool:
    want = bytes.fromhex(hex_bytes)
    start = off(pe, va)
    return data[start:start + len(want)] == want


def cstr(data: bytes, pe: pefile.PE, va: int, limit: int = 512) -> bytes:
    start = off(pe, va)
    return data[start:start + limit].split(b"\0", 1)[0]


if not TECH.is_file():
    print("[SKIP] Techstream V18 executable unavailable")
    raise SystemExit(77)

data = TECH.read_bytes()
pe = pefile.PE(str(TECH))

check(
    "Techstream.exe exact identity",
    (TECH.stat().st_size, sha(TECH))
    == (35852288, "e6b7ab884c99a941d603251fb856a77a515639fdcd1d266e875cbd1abceb5e54"),
)

print("\n== response XML schema ==")
strings = {
    0x011E97C4: b"systemAssyInfo",
    0x011E97D4: b"restoreInfo",
    0x011E97E0: b"improvementInfo",
    0x011E97F8: b"resData",
    0x011E981C: b"downloadFlg",
    0x011E9828: b"fileName",
    0x011E9834: b"comment",
    0x011E983C: b"swId",
    0x011E9844: b"selectSwInfo",
    0x011E985C: b"swComponentInfo",
    0x011E986C: b"supplyInfo",
    0x011EA898: b"updateFlg",
    0x011EA8A4: b"canWired",
    0x011EA8B0: b"canOTA",
    0x011EA8B8: b"numberingType",
    0x011EA8C8: b"displayVersion",
    0x011EA8D8: b"systemAssyNo",
    0x011E9D08: b"swType",
    0x011E9D98: b"swNo",
}
for va, value in strings.items():
    check(f"string {value.decode()} @ {va:#x}", cstr(data, pe, va) == value)

check(
    "resData/systemAssyInfo dispatch parses improvement then restore",
    anchor(
        data, pe, 0x005216E7,
        "8b55dc81c2dc00000052518bcc89650868e0971e01e83b7a8a00518d45d08bcc89650850e870110100e88be20000"
        "8b4ddc83c40c8b99e400000085db7e358bd168683b1d018b82e000000083c0108b0050ff157c26f50083c40885c0"
        "751583fb010f85280200008b45dc8b88e000000089591c8b4ddc81c1f000000051518bcc89650868d4971e01e8c8798a00"
        "518d55d08bcc89650852e8fd100100e818e20000",
    ),
)

check(
    "systemAssy record parser reads seven fields in declared order",
    anchor(
        data, pe, 0x0052FCDA,
        "8965ac68d8a81e01e855948900518d55ec8bcc8965ac52e88a2b00008d45d050e8013affff83c40c508d4d88c645fc10"
        "e87d9289008d4dd0c645fc0fe86b9289008b4d88687c58f00151ffd783c40885c07405be01000000518bcc8965ac68c8a81e01"
        "e8fa938900518d55ec8bcc8965ac52e82f2b00008d45cc50e8a639ffff83c40c508d4d8cc645fc11e8229289008d4dccc645fc0f"
        "e8109289008b4d8c687c58f00151ffd783c40885c07405be01000000518bcc8965ac68b8a81e01e89f938900518d55ec8bcc8965ac"
        "52e8d42a00008d45c850e84b39ffff83c40c508d4d90c645fc12e8c79189008d4dc8c645fc0fe8b59189008b4d90687c58f00151ffd7"
        "83c40885c07405be01000000518bcc8965ac68b0a81e01e844938900518d55ec8bcc8965ac52e8792a00008d45c450e8f038ffff83c40c"
        "508d4d94c645fc13e86c9189008d4dc4c645fc0fe85a9189008b4d94687c58f00151ffd783c40885c07405be01000000518bcc8965ac"
        "68a4a81e01e8e9928900518d55ec8bcc8965ac52e81e2a00008d45c050e89538ffff83c40c508d4d98c645fc14e8119189008d4dc0"
        "c645fc0fe8ff9089008b4d98687c58f00151ffd783c40885c07405be01000000518bcc8965ac6898a81e01",
    ),
)

print("\n== system-assy client policy ==")
check(
    "wired selector walks 0x20-byte improvement records and compares canWired to '1'",
    anchor(
        data, pe, 0x00521976,
        "8b55dcbf010000008bb2e000000083c6203bfb0f8dcbfdffff85f60f84c3fdffff8b461068683b1d0150ff157c26f500"
        "83c40885c0740f83ee20c7461c01000000e99efdffff8d43ff3bf87507c7461c0100000047ebb78b",
    ),
)
check(
    "later eligibility scan independently tests improvement updateFlg against '1'",
    anchor(
        data, pe, 0x0052F040,
        "8b83e40000008bb3e000000033ff8965f0897ddc897dfc8945e03b7de07d2a85f674268b461468683b1d0150ff157c26f500"
        "83c40885c0750abe010000008975dceb0b4783c620ebd1be010000006a",
    ),
)
check(
    "canOTA has no direct reference in the two pinned wired/update policy anchors",
    bytes.fromhex("b0a81e01") not in data[off(pe, 0x00521715):off(pe, 0x00521A00)]
    and bytes.fromhex("b0a81e01") not in data[off(pe, 0x0052F020):off(pe, 0x0052F090)],
)

print("\n== per-ECU candidate identity ==")
check(
    "supply parser selects selectSwInfo child records",
    anchor(
        data, pe, 0x00522872,
        "44981e01e805e6ffff8bf88b45e483c4083bc3897ddc74068b1050ff52088b45e0895de43bc3750d6803400080e8ce848a00"
        "8b45e08b088d55e4525750ff91900000003bc3",
    ),
)
# The four field-name immediates are in one parser block and are ordered
# swId -> comment -> fileName -> downloadFlg.  Pin their exact xrefs as a compact
# independent schema check.
for name, va, xref in (
    ("swId", 0x011E983C, 0x00522995),
    ("comment", 0x011E9834, 0x005229F9),
    ("fileName", 0x011E9828, 0x00522A40),
    ("downloadFlg", 0x011E981C, 0x00522A87),
):
    check(
        f"selectSwInfo parser field {name} xref",
        data[off(pe, xref - 1):off(pe, xref) + 4] == b"\x68" + va.to_bytes(4, "little"),
    )
check(
    "selection page copies selectSwInfo record fields 0/+8/+c into columns 12/13/14",
    anchor(
        data, pe, 0x00524C9C,
        "8bf08d8d54ffffffc645fc29e803d4ffff568d8d54ffffffe8d3428a008d46048d8d58ffffff50e8c4428a00"
        "8d4e08518d8d5cffffffe8b5428a008d560c8d8d60ffffff52e8a6428a00",
    )
    and anchor(
        data, pe, 0x00524E86,
        "6a0c8d4dbce8a07067008bf08d8d54ffffff518d4e30e8eb408a008b4e1c6a0123cf894e1c8bcee81e30ffff"
        "6a0d8d4dbce8747067008bf08d955cffffff8d4e3052e8bf408a008b4e1c6a0123cf894e1c8bcee8f22fffff"
        "6a0e8d4dbce8487067008bf08d8560ffffff508d4e30e893408a00",
    ),
)

print("\n== common target normalization ==")
check(
    "SetTargetCalFileInfo accepts only table rows whose column 11 parses to 1",
    anchor(
        data, pe, 0x0052615C,
        "e81f2e8a00687c58f0018d8d74ffffff89b570ffffffe8092e8a00687c58f0018d4d8089b578ffffff89b57cffffffe8f02d8a00"
        "6aff568d4d88897584e8f20801006aff568d4d9ce84f2e8a00578bcbe87f5d67006a0b8bc88945d4e8735d670083c0308d4de850e8c3",
    ),
)
check(
    "client derives swType and copies chosen columns 12/13 into target identity locals",
    anchor(
        data, pe, 0x0052625E,
        "8b8570ffffff83e800740c83e802741d68683b1d01eb228b4ddc688c8e1d0151ff157c26f50083c40885c07507688c8e1d01eb05"
        "68b89c1c018d8d6cffffffe8de2c8a008b8570ffffff85c07e0983f8037f046a0ceb1c8b55dc688c8e1d0152ff157c26f50083c408"
        "85c075046a0ceb026a038bcee8585c670083c0308d8d64ffffff50e8a52c8a006a0d8bcee8405c670083c0308d8d68ffffff50",
    ),
)
check(
    "common targets deduplicate on target +0x18 and +0x1c",
    anchor(
        data, pe, 0x0052636A,
        "8b55b48b8d64ffffff8d049b518d3480c1e6028b44161850ff157c26f50083c40885c0751c8b55b48b8568ffffff508b74161c56"
        "ff157c26f50083c40885c0740343ebb83bdf0f8c9f0100008b4dd46a",
    ),
)
check(
    "column 14 downloadFlg is parsed into common-target integer metadata",
    anchor(
        data, pe, 0x00526489,
        "6a0e8bcfe89e5a670083c0308d4de850e8ee2a8a008b4de88d45e46a0a5051c745e400000000ff158026f500898578ffff",
    ),
)
check(
    "common target arrays use 0x64-byte records",
    anchor(data, pe, 0x0052ED98, "8d4e04")
    and anchor(data, pe, 0x0052EDA3, "83c664"),
)

print("\n== local filtering and get-cal request ==")
check(
    "FindCalFile clears remote-needed list and walks selected 0x64-byte targets",
    anchor(
        data, pe, 0x0052734E,
        "8d8b44010000899314010000e831f700008b8b2401000033f6894de03b75e00f8dda0800008b93200100008d04b6687c58f001"
        "8d3c80c1e7028d443a348b443a3450ff157c26f50083c40885c00f85a30000008d45dc68403c1d018d4dd45051e8331c8a00"
        "8b9320010000c645fc188d4c3a1c8d5508515052e8e21d8a00508d4de8c645fc19e8b31b8a008d4d08c645fc18e8a11b8a00"
        "8d4dd4c645fc17e8951b8a008b4de88d8560fcffff5051ff154019f50083f8ff8945e4751b8b83200100008b934c0100008d8b"
        "4401000003c75052e80bf800008b55e452ff",
    ),
)
check("local scan carries *.cuw wildcard", b"*.cuw\0" in data)
check(
    "get-cal serializer loops remote-needed this+0x144/count+0x14c",
    anchor(
        data, pe, 0x00528A6C,
        "8b45c8897dd48b884c010000894db48b55b48b45d43bc20f8d7a0200008b55c88d8d9cfeffff50518d8a44010000e8f1b40000"
        "8bf08d8d38feffffc645fc1ae860f3ffff8d8d38feffffc645fc1be831e2ffff8d8d20ffffffe826e2ffff8b068d4e04518d8d24ffffff"
        "898520ffffffe815078a008d56188d8d38ffffff52e89c048a008d461c8d8d3cffffff50e88d048a008d4e20518d8d40ffffffe87e048a00"
        "8b56248d4628508d8d48ffffff899544ffffff",
    ),
)
check(
    "remote target +0x18/+0x1c become the serializer swNo/fileName value locals",
    anchor(
        data, pe, 0x00528AE1,
        "8d56188d8d38ffffff52e89c048a008d461c8d8d3cffffff50e88d048a008d4e20518d8d40ffffffe87e048a00",
    ),
)
for name, va, xref in (
    ("swNo", 0x011E9D98, 0x00528C42),
    ("fileName", 0x011E9828, 0x00528E60),
    ("swType", 0x011E9D08, 0x00528F70),
):
    # The xref addresses point at the imm32 portion of a PUSH imm32.
    check(
        f"get-cal XML emits {name}",
        data[off(pe, xref - 1):off(pe, xref) + 4] == b"\x68" + va.to_bytes(4, "little"),
    )
check(
    "get-cal request filename is SC_<id>_<timestamp>.xml",
    cstr(data, pe, 0x011E9D10) == b"SC_%s_%04d%02d%02d%02d%02d%02d.xml",
)

print("\n== downstream TIS handoff ==")
check(
    "ExecuteEcuSupplyChangeGetCalFile calls DownloadCalFiles after request construction",
    anchor(data, pe, 0x005284D3, "e8f8450000"),
)
# FUN_0052cad0 first calls the wrapper that decompiles to
# TisServiceDownloadCalFile, then (while its URL/result string is empty) calls
# the wrapper that decompiles to TisServiceGetCalFileURL.
check(
    "DownloadCalFiles invokes DownloadCalFile wrapper then GetCalFileURL poll wrapper",
    anchor(data, pe, 0x0052CBC0, "e8cbd56600")
    and anchor(data, pe, 0x0052CC03, "e878da6600"),
)

print(f"\nSummary: {passed} passed, {failed} failed")
raise SystemExit(1 if failed else 0)
