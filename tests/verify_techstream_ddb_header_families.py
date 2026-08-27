#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "tools/techstream"))
from parse_ddb import DDBParser  # noqa: E402

p = f = 0
oracle = "raw_bytes"


def check(name: str, condition: bool, detail: str = "") -> None:
    global p, f
    ok = bool(condition)
    p += ok
    f += not ok
    print(f"[{'PASS' if ok else 'FAIL'}][{oracle}] {name}" + (f" ({detail})" if detail else ""))


def header(prefix8: bytes, fmt: int, *, terminated: bool = True) -> bytes:
    data = bytearray(0x40)
    data[:8] = prefix8
    data[8] = fmt
    data[9] = 0xAC
    sig = b"DiagTool DataCtrl" + (b"\x00" if terminated else b"X")
    data[0x0A : 0x0A + len(sig)] = sig
    if not terminated:
        data[0x0A + len(sig) :] = b"Y" * (len(data) - (0x0A + len(sig)))
    return bytes(data)


def accepted(name: str, data: bytes) -> None:
    try:
        DDBParser._validate_header(data)
    except Exception as exc:
        check(name, False, repr(exc))
    else:
        check(name, True)


def rejected(name: str, data: bytes, needle: str) -> None:
    try:
        DDBParser._validate_header(data)
    except ValueError as exc:
        check(name, needle in str(exc), str(exc))
    else:
        check(name, False, "unexpectedly accepted")


print("== accepted pinned header families ==")
accepted("Techstream V18 NA type-2", header(bytes.fromhex("40000c160c080039"), 0x02))
accepted("GTS+ Gen NA type-2", header(bytes.fromhex("40000c1a06100b0e"), 0x02))
accepted("GTS+ Spe NA type-1", header(bytes.fromhex("49000c1a03111438"), 0x01))
accepted("GTS+ Gen NA P6/P6F type-2", header(bytes.fromhex("01020a1a06100b0e"), 0x02))
accepted("Techstream V18 U English", header(bytes.fromhex("39000c160b150f16"), 0x06))
accepted("GTS+ U English", header(bytes.fromhex("48000c1a05120b09"), 0x06))
accepted("GTS+ U PortugueseBR", header(bytes.fromhex("48000c1a05120b0d"), 0x06))

print("\n== fail-closed boundaries ==")
rejected("unknown standard generation rejected", header(bytes.fromhex("40000c1b06100b0e"), 0x02), "bad magic prefix")
rejected("legacy type-4 family remains rejected", header(bytes.fromhex("0e070c0a011b0e19"), 0x04), "bad magic prefix")
rejected("GTS+ U unknown language tag rejected", header(bytes.fromhex("48000c1a05120b0e"), 0x06), "bad magic prefix")
rejected("unterminated signature rejected", header(bytes.fromhex("40000c1a06100b0e"), 0x02, terminated=False), "unterminated")
short = b"\x00" * 0x20
rejected("short header rejected", short, "file too short")

print(f"\nResults: {p} passed, {f} failed")
raise SystemExit(1 if f else 0)
