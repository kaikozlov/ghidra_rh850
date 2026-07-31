#!/usr/bin/env python3
"""Bound the ICU-S SFR footprint touched by firmware to the command/data block.

The ICU-S driver reaches keys only by slot SELECTOR (written to ``0xFFC5D004``),
never by value, and its register footprint is ``0xFFC5D000``-``0xFFC5D0FF``
(command/status/data). There is no key-RAM window: the only
``0xFFC5C000``-``0xFFC5FFFF`` 32-bit literals outside that block
(``0xFFC5C784``, ``0xFFC5DFA4``) are unused literal-pool entries in a diagnostic
function, never dereferenced. This guard fails if a new ICU-S-band SFR literal
appears (e.g. a key window), prompting review. See SECOC-027.
"""
from __future__ import annotations

import struct
import sys
from pathlib import Path

CF = (Path(__file__).resolve().parents[1] / "firmware" / "RH850_P1M-E_CodeFlash.bin").read_bytes()

passed = failed = 0


def check(name: str, condition: bool, detail: str = "") -> None:
    global passed, failed
    ok = bool(condition)
    passed += int(ok)
    failed += int(not ok)
    suffix = f" ({detail})" if detail else ""
    print(f"[{'PASS' if ok else 'FAIL'}] {name}{suffix}")


found: dict[int, int] = {}
for off in range(0, len(CF) - 3, 2):
    w = struct.unpack_from("<I", CF, off)[0]
    if 0xFFC5C000 <= w <= 0xFFC5FFFF:
        found.setdefault(w, off)

# Standalone ICU-S-band literals. The driver additionally indexes
# 0xFFC5D000-0xFFC5D0FF via base+offset (D000/D008/D010/D014/D018/D090-D0BC/
# D0E4/D0F0-D0FC), which do not appear as 32-bit literals; the literal scan
# captures the standalone-referenced subset plus two unused pool entries.
EXPECTED = {
    0xFFC5D004: "key-selector reg (icus_write_128 / cmd5 / cmd7)",
    0xFFC5D00C: "status/control",
    0xFFC5D01C: "control",
    0xFFC5D020: "status",
    0xFFC5D024: "control",
    0xFFC5D0A0: "data reg",
    0xFFC5D0E0: "control",
    0xFFC5C784: "unused pool entry (diagnostic FUN_000c090c); not dereferenced",
    0xFFC5DFA4: "unused pool entry (diagnostic FUN_000c090c); not dereferenced",
}
UNUSED_POOL = {0xFFC5C784, 0xFFC5DFA4}

check("every ICU-S-band literal is in the documented set",
      set(found) <= set(EXPECTED),
      f"unexpected: {sorted(hex(w) for w in set(found) - set(EXPECTED))}")
check("no key-RAM window outside the 0xFFC5D000-0xFFC5D0FF command/data block",
      all(0xFFC5D000 <= w < 0xFFC5D100 or w in UNUSED_POOL for w in found),
      f"out-of-band: {sorted(hex(w) for w in found if not (0xFFC5D000 <= w < 0xFFC5D100 or w in UNUSED_POOL))}")
check("key selector 0xFFC5D004 is referenced (selector-based, not key-value)",
      0xFFC5D004 in found)

print(f"\nSummary: {passed} passed, {failed} failed")
sys.exit(1 if failed else 0)
