"""Native signal-group and legacy support-query catalogs.

KgpDataCtrl current getters pin layouts and exception fields:
SignalGroup 100c9b00/100c9c10/100c9c50/100c9c90/100c9650;
SignalCheck 100c9300/100c9410/100c9450/100c9490;
SupPid 100cfb40/100cfc50/100cfc90/100cfcd0;
SupDid 100ce480/100ce5d0/100ce610; SupFreeze 100ce990/100ce9d0/100cea10.
CommandCommon GetPidIdFromSignalId 100935c0 proves group+4 -> check+0,
then check+2 identifiers. GetSupport{Pid,Did}List 1007e6e0/1007e5f0
and GetEnableList 1007d6e0 prove query ID+4, policy+5. GetFrzSupport
10088330 uses SupFreeze+2 as the freeze-frame number.
These catalogs describe native selection, not a live support result.
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


def support_catalog(db: Any, strings: Any, source: str) -> dict[str, list[dict[str, Any]]]:
    """Decode each source row, preserving duplicate variants and family identity."""
    groups, checks, queries, freezes = [], [], [], []
    for group_table, check_table in ((0, 1), (154, 155)):
        family_checks = []
        for ordinal, raw in _rows(db, check_table, 8):
            row = {
                "source": source, "table": check_table, "record": ordinal, "raw": raw.hex(),
                "list_key": _u16(raw, 0), "identifier": _u16(raw, 2),
                "exception_handler_id": _u16(raw, 4), "exception_handler_flag": raw[6],
            }
            checks.append(row)
            family_checks.append(row)
        for ordinal, raw in _rows(db, group_table, 12):
            string_id = struct.unpack_from("<I", raw)[0]
            key = _u16(raw, 4)
            groups.append({
                "source": source, "table": group_table, "record": ordinal, "raw": raw.hex(),
                "group_id": raw[8], "name_string_index": string_id,
                "name": strings.get_string(string_id) or "", "list_key": key,
                "exception_handler_id": _u16(raw, 6), "exception_handler_flag": raw[9],
                "member_table": check_table,
                "members": [row["identifier"] for row in family_checks if row["list_key"] == key],
                "member_records": [row["record"] for row in family_checks if row["list_key"] == key],
            })
    for table, kind in ((3, "pid"), (4, "did")):
        for ordinal, raw in _rows(db, table, 8):
            queries.append({
                "source": source, "table": table, "record": ordinal, "raw": raw.hex(),
                "kind": kind, "query_id": raw[4], "policy": raw[5],
                "requires_previously_supported_query_id_in_p4": raw[5] == 2,
                "exception_handler_id": _u16(raw, 0), "exception_handler_flag": raw[6],
            })
    for ordinal, raw in _rows(db, 2, 4):
        freezes.append({
            "source": source, "table": 2, "record": ordinal, "raw": raw.hex(),
            "freeze_frame_number": raw[2],
            "exception_handler_id": _u16(raw, 0), "exception_handler_flag": raw[3],
            "request_variable_byte_by_frame_length": {"3": 2, "4": 1},
        })
    return {"signal_groups": groups, "signal_memberships": checks,
            "support_queries": queries, "freeze_frame_queries": freezes}


def decode_support_bitmap(query_id: int, payload: bytes) -> list[int]:
    """CommandCommon AnalyzeFrameData 1007c760: base ID plus MSB-first bits.

    Input is response data after the native protocol-specific header removal.
    This is a pure offline decoder; it does not send or authorize a request.
    """
    if not 0 <= query_id <= 255:
        raise ValueError("legacy support query ID must fit one byte")
    result = [query_id]
    for byte_index, value in enumerate(payload):
        for bit in range(8):
            identifier = query_id + 1 + byte_index * 8 + bit
            if identifier > 255:
                break
            if value & (0x80 >> bit):
                result.append(identifier)
    return result
