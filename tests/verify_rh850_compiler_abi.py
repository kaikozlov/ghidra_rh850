#!/usr/bin/env python3
"""Verify the firmware-observed volatile-EP RH850 ABI discriminator."""
from __future__ import annotations

import hashlib
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from exploit.common.payload_package import inspect_payload
from exploit.common.ram_exec import TOYOTA_P1ME_PAYLOAD_BUILD_SECRET

SIENNA = REPO / "firmware/RH850_P1M-E_CodeFlash.bin"
F33 = REPO / "firmware/camry-8965F3307000/CodeFlash.bin"
CSPEC = REPO / "ghidra/ghidra_v850/data/languages/v850.cspec"
WILLEM_PAYLOAD = REPO / "tests/fixtures/payloads/ram_dump_payload.bin"

SIENNA_SHA256 = "21140bbd65e530a9e518a3e84e20e5d85679675bc09cc724cb177bb7c76bafde"
F33_SHA256 = "42dce8efc42f6ae31718e7713fa2d26bb9191b4a82439778aee4d7afded9b0e7"
# Complete exact leaf body at VA 0x1478 in both images. It starts mov r6,ep,
# uses EP-relative short loads, loops, and returns jmp [lp] with no EP restore.
EP_CLOBBER_LEAF = bytes.fromhex(
    "06f0e041870d000d44f2670f0100443ae8060b007f00"
)
# Direct jarl 0x1478,lp at VA 0x1498 in both images.
CALL_1478 = bytes.fromhex("bfffe0ff")
WILLEM_PAYLOAD_SHA256 = "d972d4bf432685217591768600a9abd7820d35b04a72270edc87074365356be2"
WILLEM_SHELLCODE_SIZE = 438
WILLEM_SHELLCODE_SHA256 = "8b3f55e3950ca59e5175f6356df9ab96a34cb4515df11c6fd8c73f8f17bfc5eb"

passed = failed = 0

def check(name: str, cond: object) -> None:
    global passed, failed
    ok = bool(cond)
    passed += int(ok)
    failed += int(not ok)
    print(f"[{'PASS' if ok else 'FAIL'}] {name}")

for name, path, expected_sha in (
    ("Sienna", SIENNA, SIENNA_SHA256),
    ("F33", F33, F33_SHA256),
):
    blob = path.read_bytes()
    check(f"{name} exact image identity", hashlib.sha256(blob).hexdigest() == expected_sha)
    check(f"{name} reachable EP-clobber leaf bytes", blob[0x1478:0x148E] == EP_CLOBBER_LEAF)
    check(f"{name} direct caller bytes", blob[0x1498:0x149C] == CALL_1478)

payload = WILLEM_PAYLOAD.read_bytes()
check("Willem published working payload fixture identity", hashlib.sha256(payload).hexdigest() == WILLEM_PAYLOAD_SHA256)
inspection = inspect_payload(payload, secret=TOYOTA_P1ME_PAYLOAD_BUILD_SECRET)
working_shellcode = inspection.shellcode_region[:WILLEM_SHELLCODE_SIZE]
check("Willem payload authenticates and decrypts", inspection.cmac_valid and inspection.crc_residue == 0xFFFFFFFF and inspection.callback_address == 0xFEBF0000)
check("Willem working shellcode executable prefix identity", hashlib.sha256(working_shellcode).hexdigest() == WILLEM_SHELLCODE_SHA256)
check("Willem payload is zero-padded after the 438-byte shellcode", not any(inspection.shellcode_region[WILLEM_SHELLCODE_SIZE:]))

cspec = CSPEC.read_text(encoding="utf-8")
unaffected = cspec.split("<unaffected>", 1)[1].split("</unaffected>", 1)[0]
for reg in range(20, 30):
    check(f"cspec keeps r{reg} callee-saved", f'name="r{reg}"' in unaffected)
check("cspec models ep/r30 volatile", 'name="ep"' not in unaffected and 'name="r30"' not in unaffected)

print(f"\nSummary: {passed} passed, {failed} failed")
raise SystemExit(1 if failed else 0)
