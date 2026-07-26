#!/usr/bin/env python3
"""Generate the evidence-bounded checkpoint payload ownership map.

Descriptor geometry is read from the committed CodeFlash image. Semantic labels
and layouts summarize direct producer/consumer tracing; they are descriptive
analysis names, not recovered Toyota/Denso identifiers.
"""
from __future__ import annotations

import argparse
import csv
import struct
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
CF = (REPO / "firmware" / "RH850_P1M-E_CodeFlash.bin").read_bytes()
COUNT_ADDR = 0x2AF10
TABLE = 0x2AF2C

# index: (writers, evidence name, field-level layout, confidence/limit)
SEMANTICS = {
    0: ("0x5110A", "monitor_aggregate", "u8[8] group0; u8[8] group1; u32[12] group2; u32[12] group3; u32[12] group4", "direct field assembly"),
    1: ("0x51B70", "monitor_state_bank_0", "u8[240] whole-buffer snapshot", "direct whole-buffer copy; fields unresolved"),
    2: ("0x51B70", "monitor_state_bank_1", "u8[240] whole-buffer snapshot", "direct whole-buffer copy; fields unresolved"),
    3: ("0x51B70", "monitor_state_bank_2", "u8[240] whole-buffer snapshot", "direct whole-buffer copy; fields unresolved"),
    4: ("0x53492", "two_group_event_counters", "u16[18] counter_group0; u16[10] counter_group1", "direct field assembly"),
    5: ("0x477C8;0x47958", "two_channel_s16_sentinel_state", "s16 value0; s16 value1; u32 reserved_zero", "direct accesses; 32000 sentinel observed; physical quantity unresolved"),
    6: ("0x38CEC;0x38EAA", "multi_channel_u16_state", "u16[12] group0; u16[10] group1; u32 reserved_zero; u16[4] group2", "direct field assembly; OEM meaning unresolved"),
    7: ("0xB7E4A", "three_phase_mode_latch", "u8 phase; u8[7] reserved_zero", "phase values 0x00/0x11/0x22 observed"),
    8: ("0xBAF46", "u32_value_with_validity", "u32 value; u16 companion; u8 validity; u8 reserved", "direct field assembly; physical quantity unresolved"),
    9: ("0xBAFB2", "runtime_condition_snapshot", "u8[40] packed runtime-condition snapshot", "direct field assembly; individual OEM fields unresolved"),
    10: ("0x51176", "event_counter_pair", "u16 counter; u16 value; u32 reserved_zero", "direct field assembly"),
    11: ("0xBB286", "two_channel_u16_state", "u16 value0; u16 value1; u32 reserved_zero", "direct restore/reset; physical quantity unresolved"),
    12: ("0x4528C;0x453A2", "dual_incident_snapshot", "u16 counter0; u16 counter1; u32 reserved_zero; 2 * {u8 state; u8 pad; u16 value; u32 sample}", "direct field assembly"),
    13: ("0xBBCC4", "counter_and_accumulator", "u8[8] counter/accumulator state", "direct update; exact generated field types unresolved"),
    14: ("0x538D4", "three_entry_condition_history", "u8[12] trigger_counters; 3 * 12-byte condition entry", "direct field assembly"),
    15: ("0xBB482;0xBB508", "operating_state_snapshot", "u16 field00; u16 field02; u32 field04; u8[10] fields08_11; u16 field12; u32 field14", "direct field assembly; offset names retained"),
    17: ("0x53FC4", "event_log_control", "u8[16] event-log control state", "direct field assembly; individual OEM fields unresolved"),
    18: ("0x53FC4", "event_log_snapshot_bank_a", "u8[96] alternating event snapshot", "direct whole-buffer copy; fields unresolved"),
    19: ("0x53FC4", "event_log_snapshot_bank_b", "u8[96] alternating event snapshot", "direct whole-buffer copy; fields unresolved"),
    20: ("0x53F5E", "event_history_group_0", "u8[168] whole-buffer event-history snapshot", "direct whole-buffer copy; entry schema unresolved"),
    21: ("0x53F5E", "event_history_group_1", "u8[168] whole-buffer event-history snapshot", "direct whole-buffer copy; entry schema unresolved"),
    23: ("0x53F5E", "event_history_group_2", "u8[168] whole-buffer event-history snapshot", "direct whole-buffer copy; entry schema unresolved"),
    24: ("0x34FB6", "persistent_countdown", "u8 countdown; u8[7] reserved_zero", "direct decrement and zero test"),
    27: ("", "configured_orphan_slot", "u8[72] unresolved", "enabled descriptor; no static object-specific writer found"),
}


def build_rows() -> list[dict[str, object]]:
    count = struct.unpack_from("<H", CF, COUNT_ADDR)[0]
    rows = []
    for index in range(count):
        length, ring_blocks, first_block, reserved, ram = struct.unpack_from(
            "<HHHHI", CF, TABLE + index * 12
        )
        enabled = bool(ring_blocks and first_block != 0xFFFF)
        writers, name, layout, evidence = SEMANTICS.get(
            index, ("", "disabled", "", "descriptor disabled in this calibration")
        )
        rows.append({
            "object_index": index,
            "enabled": "yes" if enabled else "no",
            "data_length": length,
            "ring_blocks": ring_blocks,
            "first_nvm_block": "" if first_block == 0xFFFF else first_block,
            "ram_mirror": f"0x{ram:08X}",
            "writer_functions": writers,
            "evidence_name": name,
            "payload_layout": layout,
            "evidence_limit": evidence,
        })
    return rows


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-o", "--output", type=Path,
        default=REPO / "data" / "checkpoint_payload_map.csv",
    )
    args = parser.parse_args()
    rows = build_rows()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    print(f"wrote {len(rows)} checkpoint objects to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
