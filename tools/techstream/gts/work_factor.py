"""Source work-factor catalogs, including duplicate exception variants.

Native evidence (current GTSPlus): KgpDataCtrl GetRecordAddress and
GetExceptahand* at 100cb7a0..100cb820, 100daa60..100daae0,
100dc8a0..100dc920, 100ddbc0..100ddc40 fix table strides and exceptions.
FindDbItem at 100cb5a0/100cb6a0, 100da960, 100dc6a0/100dc7a0
fix the lookup keys. SetRecString at 100da070/100dc040/100dd540 fixes strings.
CommandCommon 10026e10/10026fe0/10029f70/1002c990 consumes item ranges,
scaling, physical-data and pattern references. GetBitRangeData 10028930
uses inclusive MSB-first bit positions. GetAnlzWrkFctP3_DT 100015a0 and
GetAnlzWrkFctP4_DT 10001d00 consume the signal-list PID references.
CommandCommon SetWorkFactorInfo 10027d00 passes signal-list +4 (through
WORK_FACTOR_PID_DATA +32) as the item-group key; +6 is the displayed ID.

GetStandardValueInfo Execute 10001010 and its disassembly prove table18
key1 is the selected standard-value ID and key2 is the signal ID; +0 is
Viewer help ID, not a numeric value or an ECU M_English string index.
The complete downstream chain is v18 CommandAPI 100a96e0 (CmdInfo+12
-> ApiRcv+8), Techstream 00c88420 (ApiRcv+8 -> 00c41480), and 00c41480
(GetParameterHelp: Viewer 0x302, key=help ID, select kind3, last row wins).
Current ViewerDb 100117d0/100115d0/10011590/10011860 establishes the same
12-byte help layout: string index+0, help ID+4, kind+8. Resolve against
V_English, never M_English; identical numeric indices have unrelated text.
P5/RoB native consumers: CommandCommon 1002b090/1002b8c0/1002bb50/
1002bda0; GetRoBP5_AnlzWkFct_DT 10001430/100019b0/10002af0;
GetRoBP5_DT 10003a30 and GetRoBP6_DT 10003a60. KgpDataCtrl
GetWorkFactorDispId 100dce00 returns the inline wchar_t field at +0.
Table114 identifiers are DIDs in the DCM path but behavior codes in the
RoB path. They are not a static join to table115 DIDs (the RoB response
supplies its data-record IDs).

These are unfiltered source definitions, not live ECU support. Unconsumed
bytes are explicitly retained rather than given invented meanings.
"""
from __future__ import annotations

import struct
from typing import Any

from tools.techstream.ddb_semantics import records


def _rows(db: Any, table: int, size: int):
    section = db.sections.get(table)
    if section is None:
        return
    if section.decoded_record_size != size:
        raise ValueError(f"table {table}: expected {size}-byte records, got {section.decoded_record_size}")
    yield from enumerate(records(section))


def _u16(raw: bytes, offset: int) -> int:
    return struct.unpack_from("<H", raw, offset)[0]


def _u32(raw: bytes, offset: int) -> int:
    return struct.unpack_from("<I", raw, offset)[0]


def viewer_help_index(
    db: Any, strings: Any, source: str, string_source: str = "V_English.ddb",
) -> dict[int, list[dict[str, Any]]]:
    """Index Viewer table2 once per region, preserving row order and every kind.

    The caller owns the language choice. No fallback to ECU/master strings is
    valid: the native Viewer resolver loads a different string namespace.
    """
    index: dict[int, list[dict[str, Any]]] = {}
    for ordinal, raw in _rows(db, 2, 12):
        help_id, string_index = _u32(raw, 4), _u32(raw, 0)
        text = strings.get_string(string_index)
        index.setdefault(help_id, []).append({
            "source": source, "namespace": "viewer", "table": 2,
            "record": ordinal, "raw": raw.hex(), "help_id": help_id,
            "kind": _u16(raw, 8), "string_index": string_index,
            "string_source": string_source, "text": text,
            "translation_available": text is not None,
            "uninterpreted_bytes": {"10": raw[10:].hex()},
        })
    return index


def work_factor_catalog(
    db: Any, strings: Any, source: str, *,
    viewer_help: dict[int, list[dict[str, Any]]] | None = None,
) -> dict[str, list[dict[str, Any]]]:
    """Decode all nine tables; record-number joins retain every source variant."""
    catalog: dict[str, list[dict[str, Any]]] = {
        "standard_info": [], "work_factor_signals": [],
        "work_factor_items": [], "work_factor_patterns": [],
        "work_factor_p5_signals": [], "work_factor_rob_items": [],
        "work_factor_operation_codes": [], "work_factor_network_status": [],
        "factor_data": [],
    }

    def base(table: int, ordinal: int, raw: bytes) -> dict[str, Any]:
        return {"source": source, "table": table, "record": ordinal, "raw": raw.hex()}

    def name(row: dict[str, Any], field: str, raw: bytes, offset: int) -> None:
        index = _u32(raw, offset)
        row[field + "_string_index"] = index
        row[field] = strings.get_string(index) or ""

    for ordinal, raw in _rows(db, 18, 12):
        row = base(18, ordinal, raw)
        help_id = _u32(raw, 0)
        help_rows = [] if viewer_help is None or help_id == 0 else [
            help_row for help_row in viewer_help.get(help_id, []) if help_row["kind"] == 3
        ]
        selected = help_rows[-1] if help_rows else None
        if help_id == 0:
            status = "not_specified"
        elif viewer_help is None:
            status = "viewer_help_not_loaded"
        elif selected is None:
            status = "help_not_found"
        elif not selected["translation_available"]:
            status = "translation_unavailable"
        else:
            status = "resolved"
        row.update({
            "standard_value_id": _u16(raw, 4), "signal_id": _u16(raw, 6),
            "help_id": help_id,
            "standard_value": selected["text"] if selected is not None else None,
            "standard_value_status": status,
            "standard_value_help_records": help_rows,
            "exception_handler_id": _u16(raw, 8), "exception_handler_flag": raw[10],
            "uninterpreted_bytes": {"11": raw[11:].hex()},
        })
        catalog["standard_info"].append(row)

    for ordinal, raw in _rows(db, 37, 20):
        row = base(37, ordinal, raw)
        name(row, "name", raw, 0)
        name(row, "help", raw, 4)
        row.update({
            "pattern_id": _u16(raw, 8), "value": _u16(raw, 10),
            "display_code": _u16(raw, 12),
            "exception_handler_id": _u16(raw, 14), "exception_handler_flag": raw[16],
            "uninterpreted_bytes": {"17": raw[17:].hex()},
        })
        catalog["work_factor_patterns"].append(row)

    for ordinal, raw in _rows(db, 36, 40):
        row = base(36, ordinal, raw)
        name(row, "name", raw, 12)
        name(row, "unit", raw, 16)
        pattern_id = _u16(raw, 30)
        row.update({
            "item_group_id": _u16(raw, 20),
            "bit_start": _u16(raw, 22), "bit_end": _u16(raw, 24),
            "scale_numerator": _u32(raw, 0), "scale_denominator": _u32(raw, 4),
            "addend_u32": _u32(raw, 8),
            "physical_data_id": _u16(raw, 28), "pattern_id": pattern_id,
            "exception_handler_id": _u16(raw, 32), "role": raw[34],
            "exception_handler_flag": raw[35],
            "new_dcm_available": raw[36] != 0,
            "new_dcm_availability_byte": raw[36],
            "pattern_records": [p["record"] for p in catalog["work_factor_patterns"]
                                if p["pattern_id"] == pattern_id],
            "uninterpreted_bytes": {"26": raw[26:28].hex(), "37": raw[37:].hex()},
        })
        catalog["work_factor_items"].append(row)

    for ordinal, raw in _rows(db, 35, 28):
        row = base(35, ordinal, raw)
        name(row, "name", raw, 0)
        group_id = _u16(raw, 4)
        row.update({
            "id": _u16(raw, 6), "item_group_id": group_id,
            "ram_frame_pid_ids": [_u16(raw, offset) for offset in (8, 10, 12)],
            "ram_address_pid_id": _u16(raw, 14),
            "freeze_frame_number": 0x100,
            "exception_handler_id": _u16(raw, 16),
            "mode": _u16(raw, 22), "effective_mode": _u16(raw, 22) or 3,
            "frame_length": raw[25], "effective_frame_length": raw[25] or 4,
            "exception_handler_flag": raw[26],
            "item_records": [item["record"] for item in catalog["work_factor_items"]
                             if item["item_group_id"] == group_id],
            "uninterpreted_bytes": {"18": raw[18:22].hex(), "24": raw[24:25].hex(),
                                    "27": raw[27:].hex()},
        })
        catalog["work_factor_signals"].append(row)
    for ordinal, raw in _rows(db, 115, 20):
        row = base(115, ordinal, raw)
        name(row, "name", raw, 0)
        pattern_id = _u16(raw, 12)
        row.update({
            "data_id": _u16(raw, 4), "bit_start": _u16(raw, 6), "bit_end": _u16(raw, 8),
            "physical_data_id": _u16(raw, 10), "pattern_id": pattern_id,
            "role": raw[18], "exception_handler_id": _u16(raw, 14),
            "exception_handler_flag": raw[19],
            "pattern_records": [p["record"] for p in catalog["work_factor_patterns"]
                                if p["pattern_id"] == pattern_id],
            "uninterpreted_bytes": {"16": raw[16:18].hex()},
        })
        catalog["work_factor_rob_items"].append(row)

    for ordinal, raw in _rows(db, 116, 16):
        row = base(116, ordinal, raw)
        name(row, "function_name", raw, 0)
        name(row, "content_name", raw, 4)
        row.update({
            "data_id": _u16(raw, 8), "operation_code": _u16(raw, 10),
            "exception_handler_id": _u16(raw, 12), "exception_handler_flag": raw[14],
            "uninterpreted_bytes": {"15": raw[15:].hex()},
        })
        catalog["work_factor_operation_codes"].append(row)

    for ordinal, raw in _rows(db, 117, 16):
        row = base(117, ordinal, raw)
        name(row, "name", raw, 0)
        pattern_id = _u16(raw, 8)
        row.update({
            "status_id": raw[14], "bit_start": _u16(raw, 4), "bit_end": _u16(raw, 6),
            "pattern_id": pattern_id,
            "exception_handler_id": _u16(raw, 10), "exception_handler_flag": raw[15],
            "pattern_records": [p["record"] for p in catalog["work_factor_patterns"]
                                if p["pattern_id"] == pattern_id],
            "uninterpreted_bytes": {"12": raw[12:14].hex()},
        })
        catalog["work_factor_network_status"].append(row)

    for ordinal, raw in _rows(db, 118, 20):
        row = base(118, ordinal, raw)
        name(row, "name", raw, 0)
        name(row, "help", raw, 4)
        row.update({
            "signal_id": _u16(raw, 12), "value": _u32(raw, 8),
            "exception_handler_id": _u16(raw, 14), "exception_handler_flag": raw[18],
            "uninterpreted_bytes": {"16": raw[16:18].hex(), "19": raw[19:].hex()},
        })
        catalog["factor_data"].append(row)

    for ordinal, raw in _rows(db, 114, 24):
        row = base(114, ordinal, raw)
        name(row, "name", raw, 12)
        data_id = _u16(raw, 16)
        row.update({
            "identifier": data_id, "id": _u16(raw, 18),
            "identifier_roles": {"dcm": "data_id", "rob": "behavior_code"},
            "exception_handler_id": _u16(raw, 20), "exception_handler_flag": raw[22],
            "operation_code_records": [op["record"] for op in catalog["work_factor_operation_codes"]
                                       if op["data_id"] == data_id],
            "display_id": raw[:12].decode("utf-16-le").split(chr(0), 1)[0],
            "uninterpreted_bytes": {"23": raw[23:].hex()},
        })
        catalog["work_factor_p5_signals"].append(row)
    return catalog


def decode_dcm_item(item: dict[str, Any], payload: bytes) -> int:
    """Offline DCM item value, not the distinct P3/P4 physical-data conversion.

    CommandCommon 10028930 extracts an inclusive MSB-first range; 10029f70
    applies unsigned 32-bit multiply, optional divide, then wraparound add.
    Caller supplies response data after its protocol header.
    """
    start, end = item["bit_start"], item["bit_end"]
    width = end - start + 1
    if start < 0 or width < 1 or width > 32 or end >= len(payload) * 8:
        raise ValueError("work-factor bit range is invalid or outside response payload")
    value = (int.from_bytes(payload, "big") >> (len(payload) * 8 - end - 1)) & ((1 << width) - 1)
    value = (value * item["scale_numerator"]) & 0xFFFFFFFF
    if item["scale_denominator"]:
        value //= item["scale_denominator"]
    return (value + item["addend_u32"]) & 0xFFFFFFFF
