#!/usr/bin/env python3
"""Validate the JSON emitted by ``ghidra stats`` after a full rebuild."""
from __future__ import annotations

import json
import sys

EXPECTED = {
    "functions": 5560,
    "instructions": 173000,
    "symbols": 27768,
    "memory_size": 1081344,
    "sections": 2,
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
    for field, expected in EXPECTED.items():
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
