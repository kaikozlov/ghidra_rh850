"""Source-complete active-test support catalogs and offline native predicates.

Native evidence: KgpDataCtrl SetRecVariableData 10099790/1009B0E0
(69/142), 1009D650 (70), 100C6E40 (72), 100BE6F0 (73/79),
100BCEE0 (78); CommandCommon CheckSupportBit 10070AC0 and
CheckSupportPanel 10071DF0; GetSimpleOperationUtilityResult_DT 100014E0.
Variable references are resolved by the caller's native-selected namespace,
never guessed from the ECU file. These functions perform no vehicle I/O.
"""
from __future__ import annotations

import operator
import struct
from collections.abc import Callable
from typing import Any

from tools.techstream.ddb_semantics import records


def _u16(raw: bytes, offset: int) -> int:
    return struct.unpack_from("<H", raw, offset)[0]


def _u32(raw: bytes, offset: int) -> int:
    return struct.unpack_from("<I", raw, offset)[0]


def active_test_support_catalog(
    db: Any, strings: Any, source: str, *,
    resolve_variable: Callable[[int], bytes] | None = None,
    variable_namespace: str | Callable[[int], str] = "native-selected",
) -> dict[str, list[dict[str, Any]]]:
    """Retain every source row, including definitions not selected by an action.

    Descriptor fields not consumed by the traced runtime paths remain in raw;
    their offsets are explicitly identified rather than assigned invented names.
    """
    def variable(index: int) -> dict[str, Any]:
        namespace = variable_namespace(index) if callable(variable_namespace) else variable_namespace
        result: dict[str, Any] = {"index": index, "namespace": namespace}
        if index == 0:
            result.update(bytes="", length=0, resolved=True)
        elif resolve_variable is not None:
            data = bytes(resolve_variable(index))
            result.update(bytes=data.hex(), length=len(data), resolved=True)
        else:
            result["resolved"] = False
        return result

    specs = ((67,18,"data_id_definitions"),(69,12,"support_conditions"),
             (70,16,"panel_support"),(72,12,"routine_status"),
             (73,20,"display_patterns"),(78,20,"description_patterns"),
             (79,20,"result_patterns"),(142,12,"routine_support_conditions"))
    result = {name: [] for _,_,name in specs}
    for table, stride, name in specs:
        section = db.sections.get(table)
        if section is None:
            continue
        if section.header.record_count and section.decoded_record_size != stride:
            raise ValueError(f"active support table {table}: expected stride {stride}, got {section.decoded_record_size}")
        for index, raw in enumerate(records(section)):
            row: dict[str, Any] = {"source": source, "table": table, "record": index, "raw": raw.hex()}
            if table == 67:
                row.update(did=_u16(raw,2), control_enable_bit_1based=_u16(raw,4),
                           data_byte_offset=_u16(raw,6),data_byte_length=_u16(raw,8),
                           encoding_mode=raw[10],mode5_bit_start_match=_u16(raw,12),
                           mode5_bit_end_match=_u16(raw,14),
                           exception_handler_id=_u16(raw,0),exception_handler_flag=raw[16])
            elif table in (69,142):
                row.update(key=_u16(raw,0),did_variable=variable(_u16(raw,2)),
                           exception_handler_id=_u16(raw,4),bit_start=_u16(raw,6),
                           bit_end=_u16(raw,8),exception_handler_flag=raw[10],
                           condition_type=raw[11],frame_selector=0xC9,
                           response_header_length=3)
                data = row["did_variable"].get("bytes")
                if data is not None and len(data) == 4:
                    row["did"] = int(data,16)
            elif table == 70:
                row.update(key=_u16(raw,0),did=_u16(raw,2),payload_byte_offset=_u16(raw,4),
                           mask=variable(_u16(raw,6)),reference=variable(_u16(raw,8)),
                           exception_handler_id=_u16(raw,10),comparison_mode=raw[13],
                           exception_handler_flag=raw[14],frame_selector=0xCA,
                           response_header_length=3,unconsumed_descriptor_offsets=[12])
            elif table == 72:
                row.update(key=_u16(raw,0),pattern=variable(_u16(raw,2)),
                           exception_handler_id=_u16(raw,6),exception_handler_flag=raw[8],
                           match="exact-full-payload",unconsumed_descriptor_offsets=[4,5])
            elif table in (73,79):
                string_index=_u32(raw,0)
                row.update(key=_u16(raw,4),name_string_index=string_index,
                           name=strings.get_string(string_index),
                           exception_handler_id=_u16(raw,8),press=variable(_u16(raw,10)),
                           pull=variable(_u16(raw,12)),panel_key=_u16(raw,14),
                           panel_mode=raw[18],exception_handler_flag=raw[19],
                           unconsumed_descriptor_offsets=[6,7,16,17])
            else:
                row.update(key=_u16(raw,4),description_id=_u32(raw,0),
                           press=variable(_u16(raw,6)),pull=variable(_u16(raw,10)),
                           exception_handler_id=_u16(raw,12),exception_handler_flag=raw[16],
                           match="exact-full-payload",
                           unconsumed_descriptor_offsets=[8,9,14,15,17])
            result[name].append(row)
    return result


def condition_supported(payload: bytes, condition: dict[str, Any]) -> bool:
    """Check already-received DID data (three-byte response header removed)."""
    if condition["condition_type"] != 7:
        raise ValueError("native CheckSupportBit requires condition type 7")
    did = condition["did_variable"]
    if not did.get("resolved") or did.get("length") != 2:
        raise ValueError("native CheckSupportBit requires a two-byte DID variable")
    start, end = condition["bit_start"], condition["bit_end"]
    if start < 0 or end < start or end >= len(payload)*8:
        raise ValueError("support bit range exceeds response payload")
    value = int.from_bytes(payload,"big") >> (len(payload)*8-end-1)
    return bool(value & ((1 << (end-start+1))-1))


def panel_supported(payload: bytes, panel: dict[str, Any] | None, *, panel_mode: int = 0) -> bool:
    """Apply native panel override or masked lexicographic comparison."""
    if panel_mode == 1:
        return True
    if panel_mode == 2:
        return False
    if panel_mode != 0 or panel is None:
        raise ValueError("invalid panel mode or missing panel definition")
    mode = panel["comparison_mode"]
    if mode == 0:
        return True
    operations = {1:operator.eq,2:operator.ne,3:operator.ge,4:operator.le,5:operator.gt,6:operator.lt}
    if mode not in operations:
        raise ValueError("invalid native panel comparison mode")
    for field in ("mask","reference"):
        if not panel[field].get("resolved"):
            raise ValueError(f"unresolved panel {field} variable")
    mask=bytes.fromhex(panel["mask"]["bytes"])
    reference=bytes.fromhex(panel["reference"]["bytes"])
    if len(reference) < len(mask):
        raise ValueError("native panel reference is shorter than mask")
    offset=panel["payload_byte_offset"]
    if offset < 0 or offset+len(mask) > len(payload):
        return False
    actual=bytes(a&m for a,m in zip(payload[offset:],mask))
    expected=bytes(a&m for a,m in zip(reference,mask))
    return operations[mode](actual,expected)


def match_variable_pattern(payload: bytes, rows: list[dict[str, Any]], *, field: str = "pattern") -> dict[str, Any] | None:
    """Native first exact byte-and-length match; duplicate rows retain order."""
    for row in rows:
        pattern=row[field]
        if not pattern.get("resolved"):
            raise ValueError("unresolved pattern variable")
        if pattern["index"] == 0:
            raise ValueError("native result matcher rejects zero pattern variable")
        if bytes.fromhex(pattern["bytes"]) == payload:
            return row
    return None
