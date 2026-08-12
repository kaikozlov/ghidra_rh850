#!/usr/bin/env python3
"""Independent checks for generated application Tx producer evidence.

The checked-in CSV is Ghidra-derived structure. This verifier ties every owning
function/body hash back to raw CodeFlash bytes and independently checks the Tx
signal/source mapping already pinned by verify_application_transmit.py.
"""
from __future__ import annotations

from collections import Counter, defaultdict
import csv
import hashlib
from pathlib import Path
import sys

REPO = Path(__file__).resolve().parents[1]
CF = (REPO / "firmware" / "RH850_P1M-E_CodeFlash.bin").read_bytes()
TX_MAP = REPO / "data" / "application_tx_map.csv"
EVIDENCE = REPO / "data" / "application_tx_producer_evidence.csv"

passed = failed = 0


def check(name: str, condition: object, detail: str = "") -> None:
    global passed, failed
    ok = bool(condition)
    passed += int(ok)
    failed += int(not ok)
    suffix = f" ({detail})" if detail else ""
    print(f"[{'PASS' if ok else 'FAIL'}] {name}{suffix}")


def num(value: str) -> int:
    return int(value, 0)


with TX_MAP.open(newline="", encoding="utf-8") as stream:
    tx_rows = list(csv.DictReader(stream))
with EVIDENCE.open(newline="", encoding="utf-8") as stream:
    rows = list(csv.DictReader(stream))

ram_signals = {int(row["signal_id"]): row for row in tx_rows if row["source_kind"] == "ram"}
by_signal: dict[int, list[dict[str, str]]] = defaultdict(list)
for row in rows:
    by_signal[int(row["signal_id"])].append(row)

print("== complete RAM-backed Tx source census ==")
check("Tx map contains 50 RAM-backed signals", len(ram_signals) == 50, str(len(ram_signals)))
check("producer evidence covers exactly those 50 signals", set(by_signal) == set(ram_signals))
check(
    "producer evidence source address matches Tx map for every signal",
    all(
        {num(r["source_ram"]) for r in by_signal[sid]} == {num(signal["source"])}
        for sid, signal in ram_signals.items()
    ),
)
check("evidence has 158 signal-reference rows", len(rows) == 158, str(len(rows)))
check(
    "reference-role totals are exact",
    Counter(row["ref_role"] for row in rows)
    == Counter({
        "producer-write": 50,
        "packer-read": 50,
        "default-init-write": 50,
        "other-read": 8,
    }),
    repr(Counter(row["ref_role"] for row in rows)),
)

print("\n== one producer per RAM-backed signal ==")
for sid, signal in sorted(ram_signals.items()):
    signal_rows = by_signal[sid]
    producers = [r for r in signal_rows if r["ref_role"] == "producer-write"]
    packer_reads = [r for r in signal_rows if r["ref_role"] == "packer-read"]
    defaults = [r for r in signal_rows if r["ref_role"] == "default-init-write"]
    check(f"signal {sid} has exactly one non-default producer", len(producers) == 1)
    check(
        f"signal {sid} packer read belongs to configured packer",
        len(packer_reads) == 1
        and num(packer_reads[0]["owner_entry"]) == num(signal["packer"]),
    )
    check(
        f"signal {sid} has exactly one application default-init write",
        len(defaults) == 1
        and num(defaults[0]["owner_entry"]) == 0x57BFE
        and defaults[0]["owner_name"] == "application_ram_default_init",
    )

expected_producers = {
    0x4B66C: {1, 3, 4, 6, 8},
    0x4B754: {30},
    0x4B7BA: set(range(46, 54)),
    0x4B882: {38, 39},
    0x4B8B6: set(range(40, 46)),
    0x4B900: {5},
    0x4B90A: {10, 11, 12, 14, 15, 16, 23, 24},
    0x4B920: {35, 36},
    0x4B93C: {25, 26, 27, 28, 29},
    0x4B976: {2, 7, 17, 18, 19, 20, 21, 31, 32, 33, 34},
    0x4B9CC: {0},
}
actual_producers: dict[int, set[int]] = defaultdict(set)
for row in rows:
    if row["ref_role"] == "producer-write":
        actual_producers[num(row["owner_entry"])].add(int(row["signal_id"]))
check("50 Tx staging writes collapse to 11 exact producer functions", actual_producers == expected_producers)

print("\n== Ghidra body identity is independently raw-byte backed ==")
owner_records = {
    (num(row["owner_entry"]), int(row["owner_body_size"]), row["owner_body_sha256"])
    for row in rows
}
check("all evidence references are function-owned", all(entry != 0 for entry, _, _ in owner_records))
for entry, size, expected_sha in sorted(owner_records):
    raw_sha = hashlib.sha256(CF[entry:entry + size]).hexdigest()
    check(
        f"owner body 0x{entry:X} hash matches raw CodeFlash",
        raw_sha == expected_sha,
        f"size={size}",
    )

print("\n== bounded extra-reader census ==")
extra = [row for row in rows if row["ref_role"] == "other-read"]
check(
    "only five Tx signals have non-packer readers",
    {int(row["signal_id"]) for row in extra} == {1, 6, 8, 10, 38},
)
check(
    "extra-reader count per signal is exact",
    Counter(int(row["signal_id"]) for row in extra) == Counter({1: 2, 6: 3, 8: 1, 10: 1, 38: 1}),
)

print(f"\nSummary: {passed} passed, {failed} failed")
sys.exit(1 if failed else 0)
