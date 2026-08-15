#!/usr/bin/env python3
"""Verify the hardware MPU permission of the XCP write window (COM-005 correction).

Raw CodeFlash bytes prove the P1M-E MPU configuration covering
`FEBF7C00..FEBFFBFC`:

  - MPU region-1 bounds live at CodeFlash `0x3181C`/`0x31820`
    (`FEBF7C00` / `FEBFFBFC`).
  - Context selectors: `0x3180F = 0x00` is the initial application context,
    `0x31810 = 0x01` is used by foreground/flash-end context entry, and
    `0x31811 = 0x00` is used by both CAN1 Tx/Rx ISR wrappers.
  - Context-0 `MPAT1 @ 0x31898 = 0xB8`, context-1 `MPAT1 @ 0x318D8 = 0xA8`.

With P1M-E MPAT semantics (Renesas R01UH0585EJ0120 Table 3.49: bit5 SX,
bit4 SW, bit3 SR, bits2/1/0 user X/W/R), context 0 grants **supervisor
R/W/execute** on the window; context 1 grants supervisor R/execute. Both
MPAT1 values use ASID 0 with G=0; reset startup explicitly loads ASID=0.
Neither context grants user-mode access.

Consequence: the earlier statement that the XCP write window is
"non-executable" was **Ghidra analysis metadata** (the LocalRAM memory block
carries `execute=false` in the Ghidra program database), not a hardware
security bound. The corrected impact statement is: the window is
attacker-writable **supervisor-executable** RAM with **no recovered
control-transfer consumer** (direct consumer/callback/function census remains
zero), so COM-005 stays a write primitive with bounded impact — this test does
not claim code execution.
"""
from __future__ import annotations

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


def u8(addr: int) -> int:
    return CF[addr]


def u32(addr: int) -> int:
    return struct.unpack_from("<I", CF, addr)[0]


def mpat_decode(value: int) -> dict[str, bool]:
    return {
        "SX": bool(value & 0x20),
        "SW": bool(value & 0x10),
        "SR": bool(value & 0x08),
        "UX": bool(value & 0x04),
        "UW": bool(value & 0x02),
        "UR": bool(value & 0x01),
    }


WINDOW_LO, WINDOW_HI = 0xFEBF7C00, 0xFEBFFBFC


def main() -> int:
    print("== MPU region-1 covers the XCP write window ==")
    check("region-1 lower bound @0x3181C == FEBF7C00", u32(0x3181C) == WINDOW_LO, hex(u32(0x3181C)))
    check("region-1 upper bound @0x31820 == FEBFFBFC", u32(0x31820) == WINDOW_HI, hex(u32(0x31820)))

    print("== context/ASID selectors ==")
    check("0x3180F == 0x00 (initial application MPU context)", u8(0x3180F) == 0x00, hex(u8(0x3180F)))
    check("0x31810 == 0x01 (foreground/flash-end MPU context selector)", u8(0x31810) == 0x01, hex(u8(0x31810)))
    check("0x31811 == 0x00 (CAN1 Tx/Rx ISR MPU context selector)", u8(0x31811) == 0x00, hex(u8(0x31811)))
    check("reset startup explicitly clears ASID to 0 at 0x27A", CF[0x27A:0x27E] == bytes.fromhex("e03f2010"), CF[0x27A:0x27E].hex())

    print("== MPAT1 attribute bytes ==")
    ctx0 = mpat_decode(u8(0x31898))
    ctx1 = mpat_decode(u8(0x318D8))
    check("ctx0 MPAT1 @0x31898 == 0x000000B8", u32(0x31898) == 0xB8, hex(u32(0x31898)))
    check("ctx1 MPAT1 @0x318D8 == 0x000000A8", u32(0x318D8) == 0xA8, hex(u32(0x318D8)))
    check("both MPAT1 values use ASID=0 and G=0",
          ((u32(0x31898) >> 16) & 0x3FF) == 0 and not (u32(0x31898) & 0x40)
          and ((u32(0x318D8) >> 16) & 0x3FF) == 0 and not (u32(0x318D8) & 0x40))
    check("application MPU init enables MPE+SVP (MPM=3)",
          CF[0x648BC:0x648C2] == bytes.fromhex("0352ea072028"), CF[0x648BC:0x648C2].hex())
    check("ctx0 grants supervisor R/W/execute", ctx0 == {"SX": True, "SW": True, "SR": True,
                                                         "UX": False, "UW": False, "UR": False})
    check("ctx1 grants supervisor R/execute (no write)", ctx1 == {"SX": True, "SW": False, "SR": True,
                                                                  "UX": False, "UW": False, "UR": False})
    check("neither context grants user-mode access",
          not any((ctx0[k], ctx1[k]) != (False, False) for k in ("UX", "UW", "UR")))

    print("== corrected impact statement boundary ==")
    check(
        "supervisor-executable window: this test asserts permission bits only, no consumer claim",
        ctx0["SX"] and ctx1["SX"],
    )
    print(
        "NOTE: Ghidra LocalRAM block execute=false is analysis metadata, not a hardware bound.\n"
        "      Direct consumer/callback/function census into the window remains zero, so COM-005\n"
        "      impact stays 'attacker-writable supervisor-executable RAM, no recovered\n"
        "      control-transfer consumer' — not an RCE claim."
    )

    print(f"\n{passed} passed, {failed} failed")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
