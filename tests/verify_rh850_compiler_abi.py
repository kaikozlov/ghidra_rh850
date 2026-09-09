#!/usr/bin/env python3
"""Verify the firmware-observed volatile-EP RH850 ABI discriminator."""
from __future__ import annotations

import hashlib
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SIENNA = REPO / "firmware/RH850_P1M-E_CodeFlash.bin"
F33 = REPO / "firmware/camry-8965F3307000/CodeFlash.bin"
CSPEC = REPO / "ghidra/ghidra_v850/data/languages/v850.cspec"
PROCESSOR_DOC = REPO / "docs/tooling/processor-module-audit.md"
FINDINGS = REPO / "docs/status/FINDINGS.md"
CORRECTIONS = REPO / "docs/status/CORRECTIONS.md"
SWITCH_INSPECTOR = REPO / "ghidra/scripts/investigate/InspectSwitchSites.java"

SIENNA_SHA256 = "21140bbd65e530a9e518a3e84e20e5d85679675bc09cc724cb177bb7c76bafde"
F33_SHA256 = "42dce8efc42f6ae31718e7713fa2d26bb9191b4a82439778aee4d7afded9b0e7"
# Complete exact leaf body at VA 0x1478 in both images. It starts mov r6,ep,
# uses EP-relative short loads, loops, and returns jmp [lp] with no EP restore.
EP_CLOBBER_LEAF = bytes.fromhex(
    "06f0e041870d000d44f2670f0100443ae8060b007f00"
)
# Direct jarl 0x1478,lp at VA 0x1498 in both images.
CALL_1478 = bytes.fromhex("bfffe0ff")

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

cspec = CSPEC.read_text(encoding="utf-8")
check("cspec models ep volatile", "ep (r30)  element pointer (volatile)" in cspec)
check("cspec no longer claims shared CC-RH ABI",
      "ABI shared by the Renesas" not in cspec and "standard Renesas CC-RH ABI" in cspec)

processor = PROCESSOR_DOC.read_text(encoding="utf-8")
check("canonical processor audit records ABI discriminator",
      "Compiler / ABI fingerprint: `ep` is volatile, not CC-RH callee-save" in processor
      and "CC-RH V2.08.00" in processor
      and "Toyota compiler vendor/version remains **bounded**" in processor)

findings = FINDINGS.read_text(encoding="utf-8")
check("ARCH-017 records volatile-ep finding",
      "| ARCH-017 |" in findings and "standard CC-RH ep-preservation rule" in findings)
corrections = CORRECTIONS.read_text(encoding="utf-8")
check("CORR-187 records superseded ABI claim", "### CORR-187 —" in corrections)

inspector = SWITCH_INSPECTOR.read_text(encoding="utf-8")
check("switch investigator avoids unsupported vendor assertion",
      "real GHS switch" not in inspector and "real compiler switch" in inspector)

print(f"\nSummary: {passed} passed, {failed} failed")
raise SystemExit(1 if failed else 0)
