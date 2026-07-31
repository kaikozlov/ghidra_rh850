#!/usr/bin/env python3
"""Validate the JSON emitted by ``ghidra stats`` after a full rebuild."""
from __future__ import annotations

import json
import sys

# Cardinality floors — device-profile mapping and vector recovery may increase
# totals relative to the pre-profile snapshot. Exact equality is enforced only
# for identity fields; numeric floors catch catastrophic analysis collapse.
#
# Memory blocks: CodeFlash + DataFlash + LocalRAM + verified SFR windows
# (SFR_EIC 0x1000 + SFR_RSCFD 0x10000 + SFR_ICUS 0x1000 + SFR_CLKGEN 0x2000
# + SFR_FCU 0x100 + SFR_TSG3 0x2000). The full peripheral range stays volatile in v850.pspec
# but is not mapped as one block (that made CodeFlash immediates look like
# valid SFR pointers and collapsed disassembly).
_MEMORY_SIZE = 0x100000 + 0x8000 + 0x20000 + 0x1000 + 0x10000 + 0x1000 + 0x2000 + 0x100 + 0x2000
_SECTIONS = 9  # CodeFlash, DataFlash, LocalRAM, EIC, RSCFD, ICUS, CLKGEN, FCU, TSG3

EXPECTED_MIN = {
    "functions": 5560,
    "instructions": 173000,
    "symbols": 27773,
    "memory_size": _MEMORY_SIZE,
    "sections": _SECTIONS,
}

EXPECTED_EXACT = {
    "memory_size": _MEMORY_SIZE,
    "sections": _SECTIONS,
}


def find_stats(text: str) -> dict[str, object]:
    decoder = json.JSONDecoder()
    for index, char in enumerate(text):
        if char not in "[{":
            continue
        try:
            value, _end = decoder.raw_decode(text[index:])
        except json.JSONDecodeError:
            continue
        rows = value if isinstance(value, list) else [value]
        for row in rows:
            if isinstance(row, dict) and isinstance(row.get("stats"), dict):
                return row["stats"]
    raise ValueError("could not find a stats object in ghidra output")


def main() -> int:
    try:
        stats = find_stats(sys.stdin.read())
    except ValueError as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1

    failures = []
    for field, minimum in EXPECTED_MIN.items():
        actual = stats.get(field)
        ok = isinstance(actual, int) and actual >= minimum
        status = "PASS" if ok else "FAIL"
        print(f"[{status}] {field} >= {minimum} (actual={actual})")
        if not ok:
            failures.append((field, f">={minimum}", actual))

    for field, expected in EXPECTED_EXACT.items():
        actual = stats.get(field)
        status = "PASS" if actual == expected else "FAIL"
        print(f"[{status}] {field} == {expected} (actual={actual})")
        if actual != expected:
            failures.append((field, expected, actual))

    if stats.get("program_name") != "RH850_P1M-E_CodeFlash.bin":
        failures.append(("program_name", "RH850_P1M-E_CodeFlash.bin", stats.get("program_name")))
    if stats.get("executable_format") != "Raw Binary":
        failures.append(("executable_format", "Raw Binary", stats.get("executable_format")))

    if failures:
        print(f"Ghidra statistics verification failed ({len(failures)} mismatches)", file=sys.stderr)
        return 1
    print("Ghidra statistics verification passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
