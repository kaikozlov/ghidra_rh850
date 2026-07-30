#!/usr/bin/env python3
"""Validate the control/safety cyclic partition and steering-command ingress.

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
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CSV_PATH = ROOT / "data" / "control_partition.csv"
REPORT_PATH = ROOT / "docs" / "architecture" / "control-partition.md"
TX_MAP_PATH = ROOT / "data" / "application_tx_map.csv"
RX_MAP_PATH = ROOT / "data" / "application_rx_map.csv"
CODEFLASH_PATH = ROOT / "firmware" / "RH850_P1M-E_CodeFlash.bin"

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


def decode_branch(addr: int, codeflash: bytes) -> tuple[str, int] | None:
    """Decode the RH850 jarl/jr forms used by the bounded call graph."""
    if addr + 4 > len(codeflash):
        return None
    w0 = struct.unpack_from("<H", codeflash, addr)[0]
    if (w0 >> 6) & 0x1F != 0x1E:
        return None
    w1 = struct.unpack_from("<H", codeflash, addr + 2)[0]
    if w1 & 1:  # SLEIGH constraint: op1616=0
        return None
    reg2 = (w0 >> 11) & 0x1F
    high = w0 & 0x3F
    if high & 0x20:
        high -= 0x40
    target = addr + (high << 16) + w1
    return ("jarl" if reg2 else "jr"), target


def branch_targets(codeflash: bytes, start: int, end: int) -> set[int]:
    targets: set[int] = set()
    for addr in range(start, end, 2):
        decoded = decode_branch(addr, codeflash)
        if decoded is not None:
            targets.add(decoded[1])
    return targets


def branch_target_at(codeflash: bytes, addr: int) -> int:
    decoded = decode_branch(addr, codeflash)
    return -1 if decoded is None else decoded[1]


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

    print("\n== periodic-domain call graph ==")
    codeflash = CODEFLASH_PATH.read_bytes()
    check("TAUJ0 CH0 body calls timing + CH0 cyclic group",
          {0x6424C, 0x656F0}.issubset(branch_targets(codeflash, 0x64F18, 0x64F90)))
    check("TAUJ0 CH2 body calls timing + CH2 cyclic group",
          {0x64376, 0x65720}.issubset(branch_targets(codeflash, 0x64F90, 0x64FCC)))
    check("foreground loop is CH3-polled and calls application group 0x65750",
          0x65750 in branch_targets(codeflash, 0x64FCC, 0x650AC))
    foreground_group = {
        branch_target_at(codeflash, addr)
        for addr in (0x65754, 0x65758, 0x6575C, 0x65760, 0x65764, 0x65768)
    }
    check("foreground application group has exact six callees",
          foreground_group == {int(addr, 16) for addr in CYCLIC_CALLEES},
          str(sorted(hex(addr) for addr in foreground_group)))
    check("0x68C0C dispatches dormant crypto-test state step",
          0x68BC2 in branch_targets(codeflash, 0x68C0C, 0x68DE6))
    check("0x68DE6 dispatches dormant crypto-test finalizer",
          0x68D0E in branch_targets(codeflash, 0x68DE6, 0x68E24))

    print("\n== protected 0x2E4 steering-command ingress ==")
    with RX_MAP_PATH.open(newline="", encoding="utf-8") as fh:
        rx_rows = list(csv.DictReader(fh))
    signal61 = next((row for row in rx_rows if row["row_kind"] == "signal"
                     and row["signal_id"] == "61"), None)
    check("signal 61 exists in RX map", signal61 is not None)
    if signal61 is not None:
        check("signal 61 is protected CAN 0x2E4 PDU 6",
              signal61["can_id"].lower() == "0x2e4"
              and signal61["rx_pdu_id"] == "6"
              and signal61["secoc_envelope"] == "yes")
        check("signal 61 is signed big-endian 16-bit B1..B2",
              signal61["wire_field"] == "B1..B2 BE16"
              and signal61["endianness"] == "big"
              and signal61["bit_length"] == "16"
              and signal61["signed"] == "1")
        check("signal 61 unpacker and first staging consumer are pinned",
              signal61["unpacker"].lower() == "0x4a244"
              and signal61["dest"].lower() == "0xfebe7f94"
              and signal61["first_consumer"].lower() == "0x56fc2")

    # COM destination -> RTE-like staging copy.
    check("0x56FC2 loads signal state FEBE7F94",
          codeflash[0x57138:0x5713C] == bytes.fromhex("240f94c7"))
    check("0x56FC2 stores signal state FEBEF184",
          codeflash[0x57148:0x5714C] == bytes.fromhex("640f8439"))

    # Per-tick snapshot scales FEBEF184 by 0x100/100 into FEBEAE20.
    check("snapshot loads FEBEF184 and calls signed scaling helper",
          codeflash[0xBA4B8:0xBA4CC] == bytes.fromhex(
              "24378439203e000120466400234e380081ffac16"))
    check("snapshot commits scaled command to FEBEAE20",
          codeflash[0xBA804:0xBA80C] == bytes.fromhex("230f3800640f20f6"))

    # Structural scheduling path to the two command conditioners.
    check("0x57AC2 version dispatch reaches full/reduced system-mode wrappers",
          {0xFDD40, 0xFDD54}.issubset(branch_targets(codeflash, 0x57AC2, 0x57BEA)))
    check("full system-mode wrapper reaches dispatcher 0xBEC4C",
          0xBEC4C in branch_targets(codeflash, 0xFDD40, 0xFDD54))
    check("system-mode dispatcher reaches snapshot 0xBA43A",
          0xBA43A in branch_targets(codeflash, 0xBEC4C, 0xBF17E))
    check("snapshot reaches control-cycle wrapper 0xCBA72",
          0xCBA72 in branch_targets(codeflash, 0xBA43A, 0xBAEEE))
    check("control-cycle wrapper reaches pipeline 0xCB86E",
          0xCB86E in branch_targets(codeflash, 0xCBA72, 0xCBA7E))
    pipeline_targets = branch_targets(codeflash, 0xCB86E, 0xCBA66)
    check("control pipeline calls clamp/gain and rate-limit stages",
          {0xC853A, 0xC85B6}.issubset(pipeline_targets))

    # FEBEAE20 -> bounded/gain-adjusted BF80 -> saturated/rate-limited BF9A/BF84.
    check("0xC853A reads FEBEAE20",
          codeflash[0xC8546:0xC854A] == bytes.fromhex("249f20f6"))
    check("0xC853A writes bounded command FEBEBF94",
          codeflash[0xC8566:0xC856A] == bytes.fromhex("64379407"))
    check("0xC853A writes gain-adjusted command FEBEBF80",
          codeflash[0xC85AE:0xC85B2] == bytes.fromhex("640f8107"))
    check("0xC85B6 reads gain-adjusted command FEBEBF80",
          codeflash[0xC85CA:0xC85CE] == bytes.fromhex("240f8107"))
    check("0xC85B6 writes rate-limited command FEBEBF9A",
          codeflash[0xC8628:0xC862C] == bytes.fromhex("649f9a07"))
    check("0xC85B6 writes conditioned command FEBEBF84",
          codeflash[0xC8678:0xC867C] == bytes.fromhex("640f8507"))

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
