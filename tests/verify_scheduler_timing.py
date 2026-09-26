#!/usr/bin/env python3
"""Validate spec-backed scheduler timing and MMIO coverage.

Checks the recovered TAUJ0 periods and verifies that the SFR inventory uses
the exact P1M-E clock, ECM, FACI, and TAUJ register names.
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
    check("P-Bus clock source present", "P_BUS_clock_frequency" in sources)
    expected_periods = {
        "TAUJ0_CH0_isr": ("16000", "200"),
        "TAUJ0_CH1_isr": ("32000", "400"),
        "TAUJ0_CH2_isr": ("80000", "1000"),
        "TAUJ0_CH3_foreground_loop": ("400000", "5000"),
        "CAN_0x260_STEER_TORQUE": ("4", "20000"),
        "CAN_0x4C8": ("196", "980000"),
    }
    by_source = {r["source"]: r for r in rows}
    for source, (ticks, usec) in expected_periods.items():
        row = by_source.get(source, {})
        check(f"{source} exact period",
              (row.get("period_ticks"), row.get("period_us")) == (ticks, usec),
              repr(row))

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
               "not a period", "records a frequency"]
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

    sfr_by_addr = {int(r["address"], 0): r["name"] for r in sfr_rows}

    check("CLKD3DIV at 0xFFF88818", sfr_by_addr.get(0xFFF88818) == "CLKD3DIV")
    check("CLKD3STAT at 0xFFF8881C", sfr_by_addr.get(0xFFF8881C) == "CLKD3STAT")
    check("CKSC3C at 0xFFF890C0", sfr_by_addr.get(0xFFF890C0) == "CKSC3C")
    check("CKSC3S at 0xFFF890C8", sfr_by_addr.get(0xFFF890C8) == "CKSC3S")

    check("ECMMICFG0 at 0xFFD62004", sfr_by_addr.get(0xFFD62004) == "ECMMICFG0")
    check("ECMESSTC0 at 0xFFD62034", sfr_by_addr.get(0xFFD62034) == "ECMESSTC0")
    check("ECMPCMD1 at 0xFFD62040", sfr_by_addr.get(0xFFD62040) == "ECMPCMD1")
    check("ECMPS at 0xFFD62044", sfr_by_addr.get(0xFFD62044) == "ECMPS")

    check("FSTATR at 0xFFA10080", sfr_by_addr.get(0xFFA10080) == "FSTATR")
    check("FENTRYR at 0xFFA10084", sfr_by_addr.get(0xFFA10084) == "FENTRYR")
    check("FACI command area at 0xFFA20000",
          sfr_by_addr.get(0xFFA20000) == "FACI_COMMAND_AREA")

    check("TAUJ0CDR3 at 0xFFE5000C", sfr_by_addr.get(0xFFE5000C) == "TAUJ0CDR3")
    check("TAUJ0CMOR3 at 0xFFE50086", sfr_by_addr.get(0xFFE50086) == "TAUJ0CMOR3")
    check("TAUJ0TPS at 0xFFE50090", sfr_by_addr.get(0xFFE50090) == "TAUJ0TPS")

    print(f"\n== RESULT: {passed} passed, {failed} failed ==")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
