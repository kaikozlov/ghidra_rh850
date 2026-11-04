#!/usr/bin/env python3
"""Validate the generated P1M-E SFR CSV's field boundaries and uniqueness."""

from __future__ import annotations

import csv
import json
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

    machine = json.loads((ROOT / "data/generated/p1me_machine.json").read_text())
    registers = {row["address"]: row for row in machine["manual"]["registers"]}
    csv_by_address = {int(row["address"], 0): row for row in rows}
    # Exact boot initialization windows; reserved holes remain unmapped.
    configuration = [
        0xFFD20010, 0xFFD20098, 0xFFD2009C, 0xFFD200A4,
        0xFFD20390, 0xFFD20394, 0xFFD20474, 0xFFD204FC,
        *(0xFFD200B8 + 4 * fifo for fifo in range(8)),
        *(0xFFD20118 + 4 * fifo for fifo in range(9)),
        *(0xFFD20500 + 0x20 * channel + offset
          for channel in range(3) for offset in (0, 4, 8, 12)),
        *(0xFFD21000 + 4 * word for word in range(64)),
        *(0xFFD24000 + 4 * word for word in range(48 * 8)),
    ]
    for address in configuration:
        register = registers.get(address, {})
        check(f"boot CAN register {address:#x} is declared manual RW word",
              register.get("size") == 4 and register.get("access") == "rw"
              and 4 in register.get("access_widths", [])
              and register.get("evidence") == "manual")
        check(f"boot CAN register {address:#x} CSV matches model",
              csv_by_address.get(address, {}).get("name") == register.get("name"))
    for channel in range(3):
        control = registers[0xFFD20508 + 0x20 * channel]
        status = registers[0xFFD2050C + 0x20 * channel]
        check(f"CAN{channel} FD clear/status reset and byte lanes",
              control["reset"] == status["reset"] == 0
              and control["access_widths"] == status["access_widths"] == [1, 2, 4])
        check(f"CAN{channel} FD clear/status semantics linked",
              control["trigger"] == "rscfd-fd-counter-clear"
              and control["status_register"] == status["name"]
              and status["trigger"] == "rscfd-fd-status"
              and status["writable_mask"] == 0x380)
    check("CAN register gaps remain unmapped",
          all(address not in registers for address in
              (0xFFD20514, 0xFFD20518, 0xFFD20554, 0xFFD21100, 0xFFD24600)))

    print(f"\nSummary: {passed} passed, {failed} failed ({len(rows)} SFR labels)")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
