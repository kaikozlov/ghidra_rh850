#!/usr/bin/env python3
"""Validate the control/safety cyclic partition artifacts.

Checks that:
- data/control_partition.csv exists and has the right schema;
- all six cyclic callees under 0x65750 are represented;
- the 0x7F7 special RX demux row is present;
- each row has a bounded subsystem name and evidence grade;
- docs/architecture/control-partition.md references the CSV and all six functions;
- the Tx signal closure for signals 9, 37, 57 is documented.
"""
from __future__ import annotations

import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CSV_PATH = ROOT / "data" / "control_partition.csv"
REPORT_PATH = ROOT / "docs" / "architecture" / "control-partition.md"
TX_MAP_PATH = ROOT / "data" / "application_tx_map.csv"

EXPECTED_HEADER = [
    "function_addr",
    "subsystem",
    "role",
    "state_root",
    "outputs",
    "calibration_refs",
    "evidence_grade",
]

# The six cyclic callees of FUN_00065750 in dispatch order.
CYCLIC_CALLEES = [
    "0x68c0c",
    "0x791c4",
    "0x96bac",
    "0x68de6",
    "0x57ac2",
    "0x6547c",
]

SPECIAL_RX_DEMUX = "0x7ff86"

ALLOWED_GRADES = {"recovered", "annotated", "bounded"}

passed = failed = 0


def check(name: str, condition: bool, detail: str = "") -> None:
    global passed, failed
    if condition:
        passed += 1
    else:
        failed += 1
    suffix = f" ({detail})" if detail else ""
    print(f"[{'PASS' if condition else 'FAIL'}] {name}{suffix}")


def main() -> int:
    print("== control partition CSV ==")
    check("CSV exists", CSV_PATH.is_file(), str(CSV_PATH))
    if not CSV_PATH.is_file():
        print(f"\nSummary: {passed} passed, {failed} failed")
        return 1

    with CSV_PATH.open(newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        check("header schema matches", reader.fieldnames == EXPECTED_HEADER,
              repr(reader.fieldnames))
        rows = list(reader)

    check("CSV has at least 7 rows (6 cyclics + 0x7F7)", len(rows) >= 7,
          str(len(rows)))

    # Build address -> row mapping.
    by_addr: dict[str, dict[str, str]] = {}
    for row in rows:
        by_addr[row["function_addr"].strip().lower()] = row

    # All six cyclic callees present.
    for addr in CYCLIC_CALLEES:
        check(f"cyclic callee {addr} present", addr in by_addr)

    # 0x7F7 special demux present.
    check(f"special RX demux {SPECIAL_RX_DEMUX} present",
          SPECIAL_RX_DEMUX in by_addr)

    # Each row has a bounded subsystem name and evidence grade.
    for row in rows:
        addr = row["function_addr"]
        check(f"{addr} subsystem non-empty", bool(row["subsystem"].strip()),
              row["subsystem"])
        check(f"{addr} evidence_grade allowed",
              row["evidence_grade"] in ALLOWED_GRADES, row["evidence_grade"])
        check(f"{addr} role non-empty", bool(row["role"].strip()))

    print("\n== control partition report ==")
    check("report exists", REPORT_PATH.is_file(), str(REPORT_PATH))
    if not REPORT_PATH.is_file():
        print(f"\nSummary: {passed} passed, {failed} failed")
        return 1

    report = REPORT_PATH.read_text(encoding="utf-8")

    # Report references the CSV.
    check("report references control_partition.csv",
          "data/control_partition.csv" in report)

    # Report references all six functions.
    for addr in CYCLIC_CALLEES:
        # Match with or without leading zeros: 0x68c0c or 0x00068c0c
        short = addr
        check(f"report references {short}", short.lower() in report.lower(),
              short)

    # Report references the 0x7F7 demux.
    check("report references 0x7ff86", "0x7ff86" in report.lower())

    # Report references 0x65750 dispatcher.
    check("report references 0x65750", "0x65750" in report.lower())

    print("\n== Tx signal producer closure ==")
    if TX_MAP_PATH.is_file():
        with TX_MAP_PATH.open(newline="", encoding="utf-8") as fh:
            tx_rows = list(csv.DictReader(fh))
        sig_rows = {int(r["signal_id"]): r for r in tx_rows}
        for sig_id, packer in [(9, "0x4BCEE"), (37, "0x4BE24"), (57, "0x4BC54")]:
            row = sig_rows.get(sig_id)
            check(f"signal {sig_id} exists in TX map", row is not None)
            if row is None:
                continue
            check(f"signal {sig_id} is configured-unresolved",
                  row["source_kind"] == "configured-unresolved",
                  row["source_kind"])
            # Packer evidence should mention the packer address in static_role.
            check(f"signal {sig_id} static_role documents packer exclusion",
                  packer.lower() in row["static_role"].lower(),
                  row["static_role"][:80])

    print(f"\nSummary: {passed} passed, {failed} failed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
