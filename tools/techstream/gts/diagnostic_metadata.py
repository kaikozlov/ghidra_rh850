"""Native detail/highlight, expanded-DTC and snapshot-selection records.

GetDiagCodeInfo_DT100013c0/10001df0 prove table5 DTC ->47 detail ->48
highlight joins and command-field copies. KgpDataCtrl getters pin row
sizes20/8/36/8/8 and exception gates. CommandCommon1008eea0 consumes49
expanded24-bit codes;10090190 consumes40 freeze-frame numbers.
GetOperationFrzFrmDatP4_DT10001000 consumes54 group selector and frame byte.
Opaque command fields retain their exact typed destination rather than
inventing a label from a coincidental string-table match.
"""
from __future__ import annotations

import struct
from typing import Any
from tools.techstream.ddb_semantics import records


def diagnostic_metadata(db: Any, strings: Any, source: str) -> dict[str, list[dict[str, Any]]]:
    result = {"details": [], "highlights": [], "expanded_dtcs": [],
              "pending_freeze": [], "operation_freeze": []}
    def rows(table, size):
        s = db.sections.get(table)
        if s is None:
            return []
        r = list(records(s))
        if any(len(raw) != size for raw in r):
            raise ValueError(f"{source}: table{table} expects{size}-byte records")
        return r
    def u16(raw, offset):
        return struct.unpack_from("<H", raw, offset)[0]
    def u32(raw, offset):
        return struct.unpack_from("<I", raw, offset)[0]
    def base(table, index, raw):
        return {"source": source, "table": table, "record": index, "raw": raw.hex()}
    for index, raw in enumerate(rows(48, 8)):
        result["highlights"].append({**base(48, index, raw),
            "list_key": u16(raw, 0), "monitor_key": u16(raw, 2),
            "highlight_mode": raw[4], "unassigned_bytes": raw[5:].hex()})
    for index, raw in enumerate(rows(47, 20)):
        highlight_key = u16(raw, 12)
        result["details"].append({**base(47, index, raw),
            "dtc_identifier": u16(raw, 8), "detail_value": u32(raw, 0),
            "highlight_list_key": highlight_key,
            "highlight_records": [r["record"] for r in result["highlights"] if r["list_key"] == highlight_key],
            "command_fields": {"u32_30": u32(raw, 0), "u32_3c": u32(raw, 4),
                               "u16_3a": u16(raw, 10), "u8_2c": raw[16], "u8_38": raw[17]},
            "exception_handler_id": u16(raw, 14), "exception_handler_flag": raw[18]})
    for index, raw in enumerate(rows(49, 36)):
        description, comment = u32(raw, 24), u32(raw, 28)
        result["expanded_dtcs"].append({**base(49, index, raw),
            "code": raw[:20].decode("utf-16le").split("\0", 1)[0],
            "packed_dtc": u32(raw, 20), "description_string_index": description,
            "description": strings.get_string(description), "comment_string_index": comment,
            "comment": strings.get_string(comment), "enabled": raw[34],
            "exception_handler_id": u16(raw, 32), "exception_handler_flag": raw[35]})
    for index, raw in enumerate(rows(40, 8)):
        result["pending_freeze"].append({**base(40, index, raw),
            "freeze_frame_number": raw[6], "exception_handler_id": u16(raw, 0),
            "exception_handler_flag": raw[7],
            "request_byte_by_frame_length": {"3": 2, "4": 1},
            "unassigned_bytes_2_5": raw[2:6].hex()})
    for index, raw in enumerate(rows(54, 8)):
        result["operation_freeze"].append({**base(54, index, raw),
            "group_selector": raw[7], "freeze_frame_number": raw[5],
            "exception_handler_id": u16(raw, 0), "exception_handler_flag": raw[6],
            "unassigned_bytes_2_4": raw[2:5].hex()})
    return result
