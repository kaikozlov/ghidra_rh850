#!/usr/bin/env python3
"""Validate the generated P1M-E SFR CSV's field boundaries and uniqueness."""

from __future__ import annotations

import csv
import sys

from tools import REPO_ROOT

ROOT = REPO_ROOT
CSV_PATH = ROOT / "data" / "p1m_sfr_labels.csv"


passed = 0
failed = 0


def check(name: str, cond: bool, detail: str = "") -> None:
    global passed, failed
    if cond:
        passed += 1
        print(f"  PASS {name}")
    else:
        failed += 1
        suffix = f" ({detail})" if detail else ""
        print(f"  FAIL {name}{suffix}")


def main() -> int:
    print("== P1M-E SFR label CSV ==")

    rows: list[dict[str, str]] = []
    with CSV_PATH.open(newline="") as fh:
        reader = csv.reader(fh)
        header = next(reader)
        check("header is address,name,size,access,comment",
              header == ["address", "name", "size", "access", "comment"],
              repr(header))
        for line_no, parts in enumerate(reader, start=2):
            if not parts or parts[0].lstrip().startswith("#"):
                continue
            if len(parts) != 5:
                check(f"line {line_no} has five columns", False, repr(parts))
                continue
            rows.append({
                "address": parts[0].strip(),
                "name": parts[1].strip(),
                "size": parts[2].strip(),
                "access": parts[3].strip(),
                "comment": parts[4].strip(),
            })

    addresses: set[int] = set()
    names: set[str] = set()
    for row in rows:
        addr = int(row["address"], 0)
        size = int(row["size"], 0)
        name = row["name"]
        access = row["access"]
        check(f"{name} access is r/w/rw", access in {"r", "w", "rw"})
        check(f"{name} size is 1/2/4/8", size in {1, 2, 4, 8}, str(size))
        check(f"{name} address unique", addr not in addresses, hex(addr))
        check(f"{name} name unique", name not in names, name)
        addresses.add(addr)
        names.add(name)

    print(f"\nSummary: {passed} passed, {failed} failed ({len(rows)} SFR labels)")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
