#!/usr/bin/env python3
"""Verify the V18 SearchCal local-CUW search boundary from raw PE bytes.

This suite pins the legacy Techstream SearchCal helper as a local package-search
UI. It deliberately does not infer remote Toyota/TIS availability from local
corpus absence.
"""
from __future__ import annotations

import hashlib
import re
from pathlib import Path

import pefile

REPO = Path(__file__).resolve().parents[1]
ROOT = REPO / "software/Techstream/v18/unpacked/toyota/Toyota Diagnostics/Techstream"
SEARCHCAL = ROOT / "bin/SearchCal.dll"
TECHSTREAM = ROOT / "bin/Techstream.exe"

passed = failed = 0
oracle = "independent_external_artifact+raw_pe_bytes"


def check(name: str, cond: object, detail: str = "") -> None:
    global passed, failed
    ok = bool(cond)
    passed += int(ok)
    failed += int(not ok)
    print(f"[{'PASS' if ok else 'FAIL'}][{oracle}] {name}" + (f" ({detail})" if detail else ""))


def pe_load(path: Path) -> tuple[bytes, pefile.PE]:
    data = path.read_bytes()
    pe = pefile.PE(str(path))
    pe.parse_data_directories()
    return data, pe


def off(pe: pefile.PE, va: int) -> int:
    return pe.get_offset_from_rva(va - pe.OPTIONAL_HEADER.ImageBase)


def anchor(data: bytes, pe: pefile.PE, va: int, hex_bytes: str) -> bool:
    expected = bytes.fromhex(hex_bytes)
    start = off(pe, va)
    return data[start:start + len(expected)] == expected


def cstr(data: bytes, pe: pefile.PE, va: int, limit: int = 512) -> bytes:
    start = off(pe, va)
    return data[start:start + limit].split(b"\0", 1)[0]


def imports(pe: pefile.PE) -> dict[str, set[str]]:
    out: dict[str, set[str]] = {}
    for entry in pe.DIRECTORY_ENTRY_IMPORT:
        dll = entry.dll.decode(errors="replace")
        names = set()
        for imp in entry.imports:
            if imp.name:
                names.add(imp.name.decode(errors="replace"))
            else:
                names.add(f"ord:{imp.ordinal}")
        out[dll] = names
    return out


if not SEARCHCAL.is_file() or not TECHSTREAM.is_file():
    print("[SKIP] Techstream V18 unavailable")
    raise SystemExit(77)

sc_data, sc_pe = pe_load(SEARCHCAL)
ts_data, ts_pe = pe_load(TECHSTREAM)

check(
    "SearchCal.dll exact identity",
    len(sc_data) == 49152
    and hashlib.sha256(sc_data).hexdigest()
    == "a47d859f9730b9f3758c44c758063aa92f922ebc0a3b4189c30bb8317061f72b",
)
check(
    "Techstream.exe exact identity",
    len(ts_data) == 35852288
    and hashlib.sha256(ts_data).hexdigest()
    == "e6b7ab884c99a941d603251fb856a77a515639fdcd1d266e875cbd1abceb5e54",
)

exports = {
    s.name.decode(errors="replace"): sc_pe.OPTIONAL_HEADER.ImageBase + s.address
    for s in sc_pe.DIRECTORY_ENTRY_EXPORT.symbols if s.name
}
check("SearchCal exports only ShowSearchCalDialog", exports == {"ShowSearchCalDialog": 0x100014F0})

imps = imports(sc_pe)
check(
    "SearchCal import DLL set is local/UI/runtime only",
    set(imps) == {"MFC42.DLL", "MSVCRT.dll", "KERNEL32.dll", "USER32.dll", "SHELL32.dll"},
    repr(sorted(imps)),
)
flat = {name for names in imps.values() for name in names}
check(
    "SearchCal has no networking/database/XML imports",
    not any(
        re.search(r"socket|connect|recv|http|internet|wininet|winhttp|urlmon|xml|sql|odbc|database|ws2_32|winsock", name, re.I)
        for name in flat
    ),
)
check(
    "SearchCal imports exact local primitives",
    {"GetPrivateProfileStringA", "GetPrivateProfileIntA"} <= imps["KERNEL32.dll"]
    and "ShellExecuteA" in imps["SHELL32.dll"]
    and {"strncpy", "_mbscmp", "strncmp"} <= imps["MSVCRT.dll"],
)

expected_strings = {
    0x1000919C: b"\\*.cuw",
    0x100091A4: b"\\*",
    0x100091A8: b"CPU%1d%1d",
    0x100091B4: b"Node%02d",
    0x100091C0: b"NumberOfNode",
    0x100091D0: b"%02d_TargetCalibration",
    0x100091E8: b"NumberOfTargets",
    0x100091F8: b"NewCID",
    0x10009200: b"CPU%02d",
    0x10009208: b"NumberOfCalibration",
    0x1000921C: b"Ethernet",
    0x10009228: b"P5-Unified",
    0x10009234: b"ContactType",
    0x10009240: b"ModelYear",
    0x1000924C: b"System",
    0x10009258: b"Vehicle",
    0x10009260: b"EngineType",
    0x100094C0: b"open",
    0x100094D8: b"RequiredSpecReproVer",
    0x100094F0: b"xx_TargetCalibration",
}
for va, expected in expected_strings.items():
    check(f"SearchCal literal {expected.decode()} @ 0x{va:08X}", cstr(sc_data, sc_pe, va) == expected)

# ShowSearchCalDialog has one caller-supplied C string. It copies [ebp+8] into
# a local 255-byte path buffer using strncpy; no CID/vehicle object is passed.
check(
    "ShowSearchCalDialog copies sole input string into local path buffer",
    anchor(sc_data, sc_pe, 0x10001548, "8b4d088d95b8f9ffff66ab5152")
    and anchor(sc_data, sc_pe, 0x10001553, "5152c645fc01aaff15d0720010"),
)

# The search worker uses the supplied path to enumerate directory entries and
# then appends the literal \\*.cuw pattern for candidate packages.
check(
    "SearchCal local scanner appends \\*.cuw to enumerated directory",
    anchor(sc_data, sc_pe, 0x10002A32, "8d4424648d4c246c50e8c0300000689c910010")
    and anchor(sc_data, sc_pe, 0x10002A40, "689c9100108d4c241c5051"),
)

# CUW filtering/parser anchors: Vehicle-level fields plus CPU calibration data.
check(
    "SearchCal reads Vehicle NumberOfCalibration",
    anchor(sc_data, sc_pe, 0x10003016, "8b4c2410516a0068089200106858920010")
    and bytes.fromhex("6858920010") in sc_data,
)
check(
    "SearchCal reads CPU NewCID and NumberOfTargets",
    anchor(sc_data, sc_pe, 0x1000305F, "8d8c248401000050680501000051685492001068f8910010")
    and bytes.fromhex("68e8910010") in sc_data,
)
check(
    "SearchCal reads numbered TargetCalibration values and compares strings locally",
    bytes.fromhex("68d0910010") in sc_data
    and bytes.fromhex("ff15d4720010") in sc_data,
)
check(
    "SearchCal recognizes P5-Unified and Ethernet ContactType prefixes",
    bytes.fromhex("6828920010") in sc_data
    and bytes.fromhex("681c920010") in sc_data
    and bytes.fromhex("6834920010") in sc_data,
)

# The result action invokes ShellExecuteA with verb "open" on a path assembled
# from the selected local result; there is no downloader call in this module.
check(
    "SearchCal opens selected local result with ShellExecuteA",
    anchor(sc_data, sc_pe, 0x1000416A, "8b44240c8b4e206a016a006a005068c094001051")
    and anchor(sc_data, sc_pe, 0x1000417E, "ff1504730010"),
)

# Techstream loads SearchCal dynamically and invokes ShowSearchCalDialog with a
# CString initialized from the global empty-string byte at 0x01F0587C.
check("Techstream SearchCal initial string is empty", cstr(ts_data, ts_pe, 0x01F0587C) == b"")
check(
    "Techstream dynamically loads SearchCal and resolves ShowSearchCalDialog",
    cstr(ts_data, ts_pe, 0x01A3EE20) == b"SearchCal.dll"
    and cstr(ts_data, ts_pe, 0x01A3EE0C) == b"ShowSearchCalDialog"
    and anchor(ts_data, ts_pe, 0x00BA60F7, "6820eea301ff157019f500")
    and anchor(ts_data, ts_pe, 0x00BA6108, "680ceea30157ff157419f500"),
)
check(
    "Techstream calls SearchCal with one CString argument initialized from empty global",
    anchor(ts_data, ts_pe, 0x00BA60D4, "687c58f0018d4c2410")
    and anchor(ts_data, ts_pe, 0x00BA6118, "8b4c242051ffd0"),
)

print(f"\nResults: {passed} passed, {failed} failed")
raise SystemExit(1 if failed else 0)
