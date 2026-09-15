#!/usr/bin/env python3
"""Verify the persisted T-0035 plaintext 8965F3401200 application image."""
from __future__ import annotations

import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IMAGE = ROOT / "firmware/tundra-8965F3401200/Application.bin"
LOAD_ADDRESS = 0x00018000
EXPECTED_SIZE = 0xE7DF0
EXPECTED_SHA256 = "c401af613cb44a70dad5ec3dba7218800bd32d94c4a47e12301b4e3a5ce33d94"

passed = failed = 0


def check(name: str, cond: object, detail: str = "") -> None:
    global passed, failed
    ok = bool(cond)
    passed += int(ok)
    failed += int(not ok)
    print(f"[{'PASS' if ok else 'FAIL'}] {name}" + (f" ({detail})" if detail else ""))


check("persisted Tundra application image exists", IMAGE.is_file())
if IMAGE.is_file():
    data = IMAGE.read_bytes()
    check("Tundra application image size exact", len(data) == EXPECTED_SIZE, hex(len(data)))
    check("Tundra application image hash exact", hashlib.sha256(data).hexdigest() == EXPECTED_SHA256)
    identity_off = 0x00020860 - LOAD_ADDRESS
    check("Tundra application identity at absolute 0x20860", data[identity_off:identity_off + 12] == b"8965F3401200")
    check("application region ends at absolute 0xFFDEF", LOAD_ADDRESS + len(data) - 1 == 0x000FFDEF)

print(f"\nResults: {passed} passed, {failed} failed")
raise SystemExit(1 if failed else 0)
