#!/usr/bin/env python3
"""Verify the recovered 8965B4512000 U023A87 communication-monitor mapping."""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from tools.generate_u023a87_monitor_map import build  # noqa: E402

ARTIFACT = REPO / "data/generated/u023a87_monitor_map.json"

passed = failed = 0


def check(name: str, condition: object, detail: str = "") -> None:
    global passed, failed
    ok = bool(condition)
    passed += int(ok)
    failed += int(not ok)
    suffix = f" ({detail})" if detail else ""
    print(f"[{'PASS' if ok else 'FAIL'}] {name}{suffix}")


rebuilt = build()
committed = json.loads(ARTIFACT.read_text(encoding="utf-8"))

print("== deterministic artifact ==")
check("committed monitor map equals rebuild", committed == rebuilt)
check("U023A87 is DTC index 93", rebuilt["u023a87"]["dtc_table_index"] == 93)
check("U023A87 failure byte is 0x87", rebuilt["u023a87"]["failure_type"] == "0x87")
check("U023A87 has exactly five configured Dem events",
      rebuilt["u023a87"]["event_ids"] == ["0xB0", "0xB3", "0x138", "0x13C", "0x13D"])

print("\n== communication-monitor table ==")
table = rebuilt["communication_monitor_table"]
check("monitor table is at 0x28278", table["address"] == "0x28278")
check("monitor table has 11 eight-byte records", table["count"] == 11 and table["record_size"] == 8)
check("event ID is u16 at record offset +2", table["event_id_offset"] == 2)
check("RX-state selector is byte +5", table["rx_state_selector_offset"] == 5)

mappings = {row["event_id"]: row for row in rebuilt["event_mappings"]}
expected = {
    "0xB0": (0, "0x4A244", ["0x2E4"]),
    "0x13C": (6, "0x4A4BC", ["0x191"]),
    "0x138": (7, "0x4A5A2", ["0x131"]),
    "0x13D": (8, "0x4A68A", ["0x2FD"]),
}
for event_id, (selector, unpacker, can_ids) in expected.items():
    row = mappings[event_id]
    check(f"{event_id} mapping is recovered", row["status"] == "recovered")
    check(f"{event_id} RX selector", row["rx_state_selector"] == selector)
    check(f"{event_id} unpacker", row["unpacker"] == unpacker)
    check(f"{event_id} CAN ID", row["can_ids"] == can_ids)

print("\n== bounded residual ==")
check("event 0xB3 remains configured-unresolved", mappings["0xB3"]["status"] == "configured-unresolved")
check("event 0xB3 is absent from the 11-entry monitor table",
      all(row["event_id"] != "0xB3" for row in table["rows"]))
check("boundary does not invent a PDU for 0xB3", "remains unresolved" in rebuilt["boundary"])

print(f"\n== RESULT: {passed} passed, {failed} failed ==")
if failed:
    raise SystemExit(1)
