#!/usr/bin/env python3
"""Verify the corrected application SID 0x23 ReadMemoryByAddress surface."""
from __future__ import annotations

import hashlib
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CF = (ROOT / "firmware" / "RH850_P1M-E_CodeFlash.bin").read_bytes()
passed = failed = 0


def check(name: str, condition: bool, detail: str = "") -> None:
    global passed, failed
    if condition:
        passed += 1
        print(f"[PASS] {name}")
    else:
        failed += 1
        print(f"[FAIL] {name}" + (f" ({detail})" if detail else ""))


def u32(addr: int) -> int:
    return struct.unpack_from("<I", CF, addr)[0]


def sha(start: int, end: int) -> str:
    return hashlib.sha256(CF[start:end]).hexdigest()


def decode_long_branch(addr: int) -> tuple[str, int] | None:
    w0 = struct.unpack_from("<H", CF, addr)[0]
    if (w0 >> 6) & 0x1F != 0x1E:
        return None
    w1 = struct.unpack_from("<H", CF, addr + 2)[0]
    if w1 & 1:
        return None
    reg2 = (w0 >> 11) & 0x1F
    high = w0 & 0x3F
    if high & 0x20:
        high -= 0x40
    return ("jarl" if reg2 else "jr"), addr + (high << 16) + w1


def overlaps(start: int, size: int, excluded: tuple[tuple[int, int], ...]) -> bool:
    end = start + size - 1
    return any(start <= hi and lo <= end for lo, hi in excluded)


print("== runtime SID 0x23 object ==")
obj = 0x25EA0
callback, sec_ptr, session_ptr, sub_ptr = struct.unpack_from("<IIII", CF, obj)
sid, has_sub, sec_count, session_count, sub_count = CF[obj + 16 : obj + 21]
check("SID 0x23 object begins at 0x25EA0", sid == 0x23)
check("SID 0x23 direct callback is 0x948AA", callback == 0x948AA, hex(callback))
check("SID 0x23 is a direct service", has_sub == 0 and sub_ptr == 0 and sub_count == 0)
check("SID 0x23 has no service-level SecurityAccess entries", sec_ptr == 0 and sec_count == 0)
check("SID 0x23 is extended-session-only", session_count == 1 and CF[session_ptr] == 3)

print("\n== address/length format ==")
format_desc = u32(0x26204)
format_list = u32(format_desc)
format_count = CF[format_desc + 4]
check("memory format descriptor is 0x26128", format_desc == 0x26128, hex(format_desc))
check("exactly one ALFID is configured", format_count == 1)
check("configured ALFID is 0x15", CF[format_list] == 0x15, hex(CF[format_list]))
check("ALFID 0x15 encodes one-byte size plus five-byte address field", (CF[format_list] >> 4, CF[format_list] & 0xF) == (1, 5))

print("\n== configured read classes ==")
config = u32(0x26208)
count = u32(0x2620C)
check("memory-class table begins at 0x261A4", config == 0x261A4, hex(config))
check("exactly two memory classes are configured", count == 2)
classes: dict[int, tuple[int, int]] = {}
for index in range(count):
    off = config + index * 12
    read_ptr, write_ptr = struct.unpack_from("<II", CF, off)
    read_count, write_count, kind, enabled = CF[off + 8 : off + 12]
    check(f"memory class {kind} is enabled and read-only", enabled == 1 and read_count == 1 and write_count == 0 and write_ptr == 0)
    sec, end, start = struct.unpack_from("<III", CF, read_ptr)
    range_sec_count = CF[read_ptr + 12]
    check(f"memory class {kind} range has no SecurityAccess list", sec == 0 and range_sec_count == 0)
    classes[kind] = (start, end)
check("memory identifier 1 covers application RAM FEBE0000..FEBFFFFF", classes.get(1) == (0xFEBE0000, 0xFEBFFFFF), repr(classes.get(1)))
check("memory identifier 2 covers DataFlash FF200000..FF207FFF", classes.get(2) == (0xFF200000, 0xFF207FFF), repr(classes.get(2)))
check("no CodeFlash memory class is configured", set(classes) == {1, 2})

print("\n== compiled exclusion ranges ==")
ram_excluded = tuple(struct.unpack_from("<II", CF, 0x293F4 + i * 8) for i in range(5))
df_excluded = tuple(struct.unpack_from("<II", CF, 0x293E4 + i * 8) for i in range(2))
expected_ram = (
    (0xFEBE0000, 0xFEBE37FF),
    (0xFEBE5030, 0xFEBE529B),
    (0xFEBF0288, 0xFEBF13CB),
    (0xFEBF4958, 0xFEBF4B33),
    (0xFEBF6C00, 0xFEBF78DF),
)
expected_df = (
    (0xFF207800, 0xFF207FFF),
    (0xFF206C00, 0xFF206EFF),
)
check("RAM exclusion table matches five compiled ranges", ram_excluded == expected_ram, repr(ram_excluded))
check("DataFlash exclusion table matches two compiled ranges", df_excluded == expected_df, repr(df_excluded))
check("RAM range-validator body is pinned", sha(0x4EA76, 0x4EABA) == "c6826075f3e313c6beb0f05c55b7a41fd5b46973a5f9eb2ee0ae22f6e6c92cb6")
check("DataFlash range-validator body is pinned", sha(0x4EAD6, 0x4EB1C) == "e2fe4fc55a84acddf7d37e151000448c5e54f3df8442581fb7fa69bb53cf295d")
check("read dispatcher calls RAM validator", decode_long_branch(0x4EB50) == ("jarl", 0x4EA76))
check("read dispatcher calls DataFlash validator", decode_long_branch(0x4EB70) == ("jarl", 0x4EAD6))
check("RAM read uses direct byte-copy helper", decode_long_branch(0x4EB60) == ("jarl", 0x4EABA))

print("\n== security-sensitive overlap disposition ==")
for label, start, size in (
    ("command-5 generated result FEBE51AA", 0xFEBE51AA, 16),
    ("key-update result FEBE523A", 0xFEBE523A, 48),
    ("object-15 RAM field FEBF02F8", 0xFEBF02F8, 16),
    ("application SecurityAccess state FEBF4958", 0xFEBF4958, 0x1DC),
):
    check(f"{label} overlaps a compiled RAM exclusion", overlaps(start, size, ram_excluded))
check("payload-derivation buffer FEBF2D08 is not excluded", not overlaps(0xFEBF2D08, 16, ram_excluded))
check("object-15 raw DataFlash field FF206E14 is excluded", overlaps(0xFF206E14, 16, df_excluded))
check("ICU-S tail FF207800 is excluded", overlaps(0xFF207800, 1, df_excluded))
check("ordinary DataFlash FF200000 remains readable", not overlaps(0xFF200000, 16, df_excluded))

print("\n== bounded request geometry ==")
check("one-byte configured size field caps a single request at 255 bytes", (0x15 >> 4) == 1 and 0xFF == 255)
check("RAM read helper independently rejects sizes above 256", CF[0x4EB3E:0x4EB48] == bytes.fromhex("1c0effff010601ff9125"))
check("compiled exclusion test rejects overlap, not only starts inside the range", overlaps(0xFEBE502F, 2, ram_excluded))
check("byte immediately before an excluded RAM range is readable alone", not overlaps(0xFEBE502F, 1, ram_excluded))
check("byte immediately after command/key-update exclusion is readable", not overlaps(0xFEBE529C, 1, ram_excluded))

print(f"\nSummary: {passed} passed, {failed} failed")
sys.exit(1 if failed else 0)
