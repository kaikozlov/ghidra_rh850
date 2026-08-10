#!/usr/bin/env python3
"""Generate the recovered Sienna U023A87 communication-monitor map.

Four of the five Dem events mapped to U023A87 are members of the 11-entry
communication-monitor table at CodeFlash 0x28278. Its u16 at +2 is the Dem
event ID and byte +5 is the receive-state selector consumed by FUN_00048e4c.
Ghidra recovery independently ties selectors 0/6/7/8 to the listed COM
unpackers. Event 0xB3 is not present in this table and remains unresolved.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
CF_PATH = REPO / "firmware/RH850_P1M-E_CodeFlash.bin"
RX_MAP_PATH = REPO / "data/application_rx_map.csv"
OUTPUT = REPO / "data/generated/u023a87_monitor_map.json"

DTC_TABLE_BASE = 0x309DC
DTC_RECORD_SIZE = 8
U023A87_DTC_INDEX = 93
DTC_EVENT_TABLE_BASE = 0x2FDDC
DTC_EVENT_RECORD_SIZE = 8
TARGET_EVENTS = (0xB0, 0xB3, 0x138, 0x13C, 0x13D)
COMM_MONITOR_TABLE_BASE = 0x28278
COMM_MONITOR_RECORD_SIZE = 8
COMM_MONITOR_COUNT = 11

# Recovered from instruction-aware Ghidra data flow: each listed unpacker calls
# FUN_00048e4c(selector), and application_rx_map.csv independently binds that
# unpacker address to its accepted CAN ID.
RX_STATE_UNPACKER = {
    0: 0x4A244,
    6: 0x4A4BC,
    7: 0x4A5A2,
    8: 0x4A68A,
}


def load_unpacker_can_map() -> dict[int, set[int]]:
    result: dict[int, set[int]] = {}
    with RX_MAP_PATH.open(newline="", encoding="utf-8") as stream:
        for row in csv.DictReader(stream):
            try:
                unpacker = int(row["unpacker"], 0)
                can_id = int(row["can_id"], 0)
            except (ValueError, TypeError):
                continue
            result.setdefault(unpacker, set()).add(can_id)
    return result


def build() -> dict:
    cf = CF_PATH.read_bytes()
    unpacker_can = load_unpacker_can_map()

    dtc_off = DTC_TABLE_BASE + U023A87_DTC_INDEX * DTC_RECORD_SIZE
    dtc_raw = cf[dtc_off : dtc_off + DTC_RECORD_SIZE]
    if len(dtc_raw) != 8:
        raise ValueError("U023A87 DTC record outside CodeFlash")
    failure_type = dtc_raw[0]
    base_dtc = int.from_bytes(dtc_raw[1:3], "little")

    event_rows = {}
    for event_id in TARGET_EVENTS:
        off = DTC_EVENT_TABLE_BASE + event_id * DTC_EVENT_RECORD_SIZE
        raw = cf[off : off + DTC_EVENT_RECORD_SIZE]
        event_rows[event_id] = {
            "event_id": f"0x{event_id:X}",
            "event_record_address": f"0x{off:X}",
            "raw": raw.hex(),
            "dtc_table_index": raw[2],
        }

    monitor_rows = []
    event_to_monitor = {}
    for index in range(COMM_MONITOR_COUNT):
        off = COMM_MONITOR_TABLE_BASE + index * COMM_MONITOR_RECORD_SIZE
        raw = cf[off : off + COMM_MONITOR_RECORD_SIZE]
        event_id = int.from_bytes(raw[2:4], "little")
        rx_state = raw[5]
        row = {
            "monitor_index": index,
            "address": f"0x{off:X}",
            "raw": raw.hex(),
            "event_id": f"0x{event_id:X}",
            "dispatch_index": raw[4],
            "rx_state_selector": rx_state,
            "mode": f"0x{raw[6]:02X}",
            "peer": raw[7],
        }
        unpacker = RX_STATE_UNPACKER.get(rx_state)
        if unpacker is not None:
            ids = sorted(unpacker_can.get(unpacker, set()))
            row["unpacker"] = f"0x{unpacker:X}"
            row["can_ids"] = [f"0x{can_id:X}" for can_id in ids]
        monitor_rows.append(row)
        event_to_monitor[event_id] = row

    mappings = []
    for event_id in TARGET_EVENTS:
        event = event_rows[event_id]
        monitor = event_to_monitor.get(event_id)
        if monitor and monitor.get("can_ids"):
            mappings.append({
                "event_id": event["event_id"],
                "dtc_table_index": event["dtc_table_index"],
                "monitor_index": monitor["monitor_index"],
                "rx_state_selector": monitor["rx_state_selector"],
                "unpacker": monitor["unpacker"],
                "can_ids": monitor["can_ids"],
                "status": "recovered",
            })
        else:
            mappings.append({
                "event_id": event["event_id"],
                "dtc_table_index": event["dtc_table_index"],
                "status": "configured-unresolved",
                "note": "event is not present in the recovered 11-entry communication-monitor table",
            })

    return {
        "schema_version": 1,
        "firmware_sha256": __import__("hashlib").sha256(cf).hexdigest(),
        "u023a87": {
            "dtc_table_index": U023A87_DTC_INDEX,
            "record_address": f"0x{dtc_off:X}",
            "failure_type": f"0x{failure_type:02X}",
            "base_dtc": f"0x{base_dtc:04X}",
            "full_code": "U023A87",
            "event_ids": [f"0x{x:X}" for x in TARGET_EVENTS],
        },
        "communication_monitor_table": {
            "address": f"0x{COMM_MONITOR_TABLE_BASE:X}",
            "record_size": COMM_MONITOR_RECORD_SIZE,
            "count": COMM_MONITOR_COUNT,
            "event_id_offset": 2,
            "dispatch_index_offset": 4,
            "rx_state_selector_offset": 5,
            "rows": monitor_rows,
        },
        "event_mappings": mappings,
        "boundary": (
            "The four recovered mappings are comparative 8965B4512000 receive monitors. "
            "Event 0xB3 is configured for U023A87 but is not present in this monitor table; "
            "its specific reporter/PDU remains unresolved."
        ),
    }


def main() -> int:
    result = build()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(OUTPUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
