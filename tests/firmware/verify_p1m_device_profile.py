#!/usr/bin/env python3
"""Validate the P1M-E SFR label CSV against mapped windows and known landmarks."""

from __future__ import annotations

import csv
import sys

from tools import REPO_ROOT

ROOT = REPO_ROOT
CSV_PATH = ROOT / "data" / "p1m_sfr_labels.csv"

WINDOWS = {
    "SFR_FACI_ID": (0xFFA08000, 0x20),
    "SFR_FACI": (0xFFA10000, 0x200),
    "SFR_FACI_COMMAND": (0xFFA20000, 0x4),
    "SFR_FACI_CONFIG": (0xFFC59000, 0x100),
    "SFR_EIC": (0xFFFFB000, 0x1000),
    # CPU-internal register page (PE guard, EI level interrupt controls
    # EIC8/EIC9/EIC16..); manual SFR list rows marked "CPU", e.g. FFFEEA10 H.
    "SFR_CPU_INTERNAL": (0xFFFEE000, 0x1000),
    "SFR_RSCFD": (0xFFD20000, 0x10000),
    "SFR_ICUS": (0xFFC5D000, 0x1000),
    "SFR_CODEFLASH_ECC": (0xFFC62000, 0x500),
    "SFR_STAC": (0xFFF81000, 0x1000),
    "SFR_CLKGEN": (0xFFF88000, 0x2000),
    "SFR_ECM_MASTER": (0xFFD60000, 0x100),
    "SFR_ECM_CHECKER": (0xFFD61000, 0x100),
    "SFR_ECM_COMMON": (0xFFD62000, 0x100),
    "SFR_ECM_PULSE": (0xFFD63000, 0x100),
    "SFR_TAUJ": (0xFFE50000, 0x3000),
    "SFR_ADCG0": (0xFFF91000, 0x1000),
    "SFR_ADCG1": (0xFFF92000, 0x1000),
    "SFR_DMAC_CM": (0xFFFF8100, 0x40),
    "SFR_TSG3": (0xFFE70000, 0x2000),
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
    0xFFC62008: ("UCFDERSTCLR", 4),
    0xFFC62030: ("UCFDERSTR", 4),
    0xFFF88818: ("CLKD3DIV", 4),
    0xFFF8881C: ("CLKD3STAT", 4),
    0xFFF890C0: ("CKSC3C", 4),
    0xFFF890C8: ("CKSC3S", 4),
    0xFFD60014: ("ECMMPCMD0", 4),
    0xFFD61014: ("ECMCPCMD0", 4),
    0xFFD62004: ("ECMMICFG0", 4),
    0xFFD62034: ("ECMESSTC0", 4),
    0xFFD62040: ("ECMPCMD1", 4),
    0xFFD62044: ("ECMPS", 1),
    0xFFD6207C: ("ECMPEM", 4),
    0xFFA10080: ("FSTATR", 4),
    0xFFA10084: ("FENTRYR", 2),
    0xFFA20000: ("FACI_COMMAND_AREA", 1),
    0xFFE5000C: ("TAUJ0CDR3", 4),
    0xFFE5001C: ("TAUJ0CNT3", 4),
    0xFFE5008C: ("TAUJ0CMOR3", 2),
    0xFFE50090: ("TAUJ0TPS", 2),
    0xFFF91200: ("ADCG0DIR00", 4),
    0xFFF92200: ("ADCG1DIR00", 4),
    0xFFFF8100: ("DM00CM", 4),
    0xFFFF8120: ("DM10CM", 4),
    0xFFE70180: ("TSG30CMPWE", 4),
    0xFFE70184: ("TSG30CMPVE", 4),
    0xFFE70188: ("TSG30CMPUE", 4),
    0xFFE71180: ("TSG31CMPWE", 4),
    0xFFE71184: ("TSG31CMPVE", 4),
    0xFFE71188: ("TSG31CMPUE", 4),
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

    print(f"\nSummary: {passed} passed, {failed} failed ({len(rows)} SFR labels)")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
