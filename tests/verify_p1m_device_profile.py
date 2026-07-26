#!/usr/bin/env python3
"""Validate the P1M-E SFR label CSV against mapped windows and known landmarks."""
from __future__ import annotations

import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CSV_PATH = ROOT / "data" / "p1m_sfr_labels.csv"

WINDOWS = {
    "SFR_EIC": (0xFFFFB000, 0x1000),
    "SFR_RSCFD": (0xFFD20000, 0x10000),
    "SFR_ICUS": (0xFFC5D000, 0x1000),
    "SFR_CLKGEN": (0xFFF88000, 0x2000),
    "SFR_FCU": (0xFFD62000, 0x100),
}

# Landmarks that must remain labeled for day-to-day analysis.
REQUIRED = {
    0xFFFFB110: ("EIC136", 2),
    0xFFFFB248: ("EIC292", 2),
    0xFFFFB24A: ("EIC293", 2),
    0xFFFFB10A: ("EIC133", 2),
    0xFFFFB176: ("EIC187", 2),
    0xFFD20178: ("CFSTS", 4),
    0xFFD20184: ("CFSTS_CH1", 4),
    0xFFD201D8: ("CFPCTR", 4),
    0xFFD20250: ("CFDTMC", 4),
    0xFFD20260: ("CFDTMC16", 1),
    0xFFD202D0: ("CFDTMSTS", 4),
    0xFFD23400: ("CFID", 4),
    0xFFD24200: ("CFDTMID16", 4),
    0xFFC5D000: ("ICUSCMD", 4),
    0xFFC5D00C: ("ICUSSTS", 4),
}

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


def window_for(addr: int, size: int) -> str | None:
    end = addr + size - 1
    for name, (base, win_size) in WINDOWS.items():
        if base <= addr and end < base + win_size:
            return name
    return None


def main() -> int:
    print("== P1M-E SFR label CSV ==")
    check("CSV exists", CSV_PATH.is_file(), str(CSV_PATH))
    if not CSV_PATH.is_file():
        print(f"\nSummary: {passed} passed, {failed} failed")
        return 1

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

    check("CSV has at least 20 named SFRs", len(rows) >= 20, str(len(rows)))
    check("CSV grew past the original 7-row inventory", len(rows) > 7, str(len(rows)))

    addresses: set[int] = set()
    names: set[str] = set()
    by_addr: dict[int, tuple[str, int]] = {}
    for row in rows:
        addr = int(row["address"], 0)
        size = int(row["size"], 0)
        name = row["name"]
        access = row["access"]
        check(f"{name} access is r/w/rw", access in {"r", "w", "rw"})
        check(f"{name} size is 1/2/4/8", size in {1, 2, 4, 8}, str(size))
        check(f"{name} address unique", addr not in addresses, hex(addr))
        check(f"{name} name unique", name not in names, name)
        win = window_for(addr, size)
        check(f"{name} sits in a mapped volatile window", win is not None,
              f"{addr:#x}+{size}")
        addresses.add(addr)
        names.add(name)
        by_addr[addr] = (name, size)

    for addr, (name, size) in REQUIRED.items():
        actual = by_addr.get(addr)
        check(f"required {name} at {addr:#x}",
              actual == (name, size),
              repr(actual))

    # EIC channel formula used by the architecture docs.
    for channel, addr in [(136, 0xFFFFB110), (292, 0xFFFFB248), (187, 0xFFFFB176)]:
        check(f"EIC{channel} follows 0xFFFFB000+2*n",
              addr == 0xFFFFB000 + 2 * channel)

    print(f"\nSummary: {passed} passed, {failed} failed ({len(rows)} SFR labels)")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
