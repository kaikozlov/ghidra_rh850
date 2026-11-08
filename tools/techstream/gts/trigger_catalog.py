"""Native GTS trigger setup, PSA DTC-group and predictive-FFD lookup tables.

GetTriggerItemList100010BA–10001116 copies table16 into CCmdTrigger.
DataMonitorPhase3 FUN10001E90 joins table19 to master function18/frame17.
GetFrzFrmDatPSA_DT10001095–10001106 joins table32 to signal-group0/check1.
CommandCommon GetPidIdFromPreAddInfo100A3B90 selects table171 by vehicle type.
"""
from __future__ import annotations

import struct
from typing import Any

from tools.techstream.ddb_semantics import records


def trigger_catalog(db: Any, strings: Any, source: str) -> dict[str, list[dict[str, Any]]]:
    def rows(table: int, size: int):
        if table not in db.sections:
            return []
        result = list(records(db.sections[table]))
        if any(len(raw) != size for raw in result):
            raise ValueError(f"{source}: table{table} expected {size}-byte records")
        return result

    def u16(raw: bytes, off: int) -> int:
        return struct.unpack_from("<H", raw, off)[0]

    def u32(raw: bytes, off: int) -> int:
        return struct.unpack_from("<I", raw, off)[0]

    def base(table: int, index: int, raw: bytes, exception_id: int, flag: int):
        return {"source": source, "table": table, "record": index, "raw": raw,
                "exception_handler_id": u16(raw, exception_id),
                "exception_handler_flag": raw[flag]}

    trigger_items = []
    for index, raw in enumerate(rows(16, 24)):
        trigger_items.append({
            **base(16, index, raw, 16, 20),
            "trigger_key": u16(raw, 12), "name_string_index": u32(raw, 8),
            "name": strings.get_string(u32(raw, 8)),
            # These are proved CCmdTrigger destination slots, not guessed UI labels.
            "command_trigger_fields": {
                "u16_at20": u16(raw, 14), "u32_at24": u32(raw, 4),
                "u8_at28": raw[19], "u32_at2c": u32(raw, 0), "u8_at30": raw[18],
            },
            "unassigned_tail": raw[21:24].hex(),
        })
    retrieval = []
    for index, raw in enumerate(rows(19, 8)):
        retrieval.append({
            **base(19, index, raw, 4, 7), "retrieval_key": u16(raw, 0),
            "function_selector": u16(raw, 2),
            "frame_lookup": {"master_table": 18, "selector": u16(raw, 2),
                             "next_master_table": 17},
            "assembler_mode": raw[6],
        })
    dtc_groups = []
    for index, raw in enumerate(rows(32, 10)):
        dtc_groups.append({
            **base(32, index, raw, 4, 6),
            "dtc_group_key": u16(raw, 0), "signal_group_key": raw[2],
            "signal_group_lookup": {"table": 0, "key": raw[2], "next_table": 1},
            "unassigned_byte3": raw[3], "unassigned_tail": raw[7:].hex(),
        })
    predictive = []
    monitor_by_did: dict[int, list[int]] = {}
    if 62 in db.sections:
        for index, raw in enumerate(records(db.sections[62])):
            if len(raw) >= 80:
                monitor_by_did.setdefault(u16(raw, 0x48), []).append(index)
    for index, raw in enumerate(rows(171, 8)):
        did = u16(raw, 2)
        predictive.append({
            **base(171, index, raw, 4, 7), "vehicle_type": raw[6], "did": did,
            "monitor_table": 62, "snapshot_monitor_records": monitor_by_did.get(did, []),
            "unassigned_word0": u16(raw, 0),
        })
    return {"trigger_items": trigger_items, "trigger_retrieval": retrieval,
            "dtc_group_retrieval": dtc_groups, "predictive_ffd_vehicle_dids": predictive}
