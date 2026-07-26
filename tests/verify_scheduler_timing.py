#!/usr/bin/env python3
"""Validate scheduler timing and observed MMIO coverage.

Checks data/scheduler_periods.csv schema, bounded-negative language for
unresolved timing, and verifies the SFR CSV covers PLL/clock and flash
sequencer windows now mapped in the device profile.
"""
from __future__ import annotations

import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PERIODS_CSV = ROOT / "data" / "scheduler_periods.csv"
SFR_CSV = ROOT / "data" / "p1m_sfr_labels.csv"

passed = failed = 0


def check(name: str, condition: bool, detail: str = "") -> None:
    global passed, failed
    if condition:
        passed += 1
    else:
        failed += 1
    suffix = f" ({detail})" if detail else ""
    status = "PASS" if condition else "FAIL"
    print(f"[{status}] {name}{suffix}")


def main() -> int:
    print("== scheduler timing ==")
    check("scheduler_periods.csv exists", PERIODS_CSV.is_file())

    rows: list[dict[str, str]] = []
    with PERIODS_CSV.open(newline="") as fh:
        reader = csv.DictReader(fh)
        check("CSV header schema",
              reader.fieldnames == ["source", "period_ticks", "period_us",
                                    "derivation", "evidence"],
              repr(reader.fieldnames))
        for row in reader:
            rows.append(row)

    check("CSV has at least 10 sources", len(rows) >= 10, str(len(rows)))

    sources = {r["source"] for r in rows}
    check("foreground loop tick present",
          "TAUJ0_CH3_foreground_loop" in sources)
    check("PLL clock source present", "PLL_clock_frequency" in sources)

    # Every period_us must be either a number or "unsupported".
    for r in rows:
        pu = r["period_us"].strip()
        pt = r["period_ticks"].strip()
        check(f"{r['source']} period_ticks is numeric or unsupported",
              pt.isdigit() or pt == "unsupported", pt)
        check(f"{r['source']} period_us is numeric or unsupported",
              pu.isdigit() or pu == "unsupported", pu)

    # Bounded-negative: unresolved rows must use bounded language.
    BOUNDED = ["not statically", "unsupported", "cannot", "not recoverable",
               "not referenced", "requires pll", "not statically recoverable",
               "not a period"]
    for r in rows:
        if r["period_us"] == "unsupported":
            deriv = r["derivation"].lower()
            check(f"{r['source']} derivation explains why unsupported",
                  any(w in deriv for w in BOUNDED),
                  r["derivation"][:80])

    # No row may invent a microsecond period without evidence.
    for r in rows:
        if r["period_us"].strip().isdigit():
            check(f"{r['source']} has derivation for resolved period",
                  len(r["derivation"]) > 10,
                  r["derivation"][:80])

    print("\n== observed MMIO coverage ==")
    sfr_rows: list[dict[str, str]] = []
    with SFR_CSV.open(newline="") as fh:
        reader = csv.reader(fh)
        next(reader)  # skip header
        for parts in reader:
            if not parts or parts[0].lstrip().startswith("#"):
                continue
            sfr_rows.append({"address": parts[0].strip(),
                             "name": parts[1].strip()})

    sfr_addrs = {int(r["address"], 0) for r in sfr_rows}
    sfr_names = {r["name"] for r in sfr_rows}

    # PLL/clock registers must be labeled.
    check("PLLCFG at 0xFFF88818 labeled", 0xFFF88818 in sfr_addrs)
    check("PLLCTL at 0xFFF890C0 labeled", 0xFFF890C0 in sfr_addrs)
    check("PLLSTS at 0xFFF890C8 labeled", 0xFFF890C8 in sfr_addrs)

    # FCU registers must be labeled.
    check("FKEY at 0xFFD62040 labeled", 0xFFD62040 in sfr_addrs)
    check("FSTS at 0xFFD62044 labeled", 0xFFD62044 in sfr_addrs)
    check("FCU command window at 0xFFD62004 labeled",
          0xFFD62004 in sfr_addrs)

    print(f"\n== RESULT: {passed} passed, {failed} failed ==")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
