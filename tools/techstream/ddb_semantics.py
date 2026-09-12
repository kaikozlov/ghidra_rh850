#!/usr/bin/env python3
"""Canonical semantic record grammar for Toyota P5/P6 DDB monitor/behavior rows."""
from __future__ import annotations

import struct
from collections.abc import Iterable
from dataclasses import dataclass
from typing import Any

from parse_ddb import DDBParser


def records(section: Any) -> Iterable[bytes]:
    size = section.decoded_record_size
    data = section.decoded_data
    for index in range(section.header.record_count):
        raw = data[index * size:(index + 1) * size]
        if len(raw) != size:
            raise ValueError(
                f"truncated DDB table {section.header.table_type} record {index}: "
                f"{len(raw)} != {size}"
            )
        yield raw


@dataclass(frozen=True)
class MonitorRecord:
    table: int
    index: int
    name_string_index: int
    monitor_key: int
    physical_data_key: int
    bit_start: int
    bit_end: int
    pattern_display_key: int
    primary_did: int
    alternate_did: int
    sort_key: int
    raw: bytes


@dataclass(frozen=True)
class BehaviorRecord:
    table: int
    index: int
    signature: str
    name_string_index: int
    comment_string_index: int
    behavior_code: int
    raw: bytes


@dataclass(frozen=True)
class RobSignalRecord:
    table: int
    index: int
    name_string_index: int
    record_key: int
    support_condition_key: int
    physical_data_key: int
    bit_start: int
    bit_end: int
    sort_key: int
    pattern_display_key: int
    exception_handler_id: int
    did: int
    extraction_mode: int
    presentation_mode: int
    exception_handler_flag: int
    raw: bytes


def extract_msb0(payload: bytes, bit_start: int, bit_end: int) -> int:
    """Extract a Toyota Data Monitor bit range (inclusive, MSB-first per byte)."""
    if bit_start < 0 or bit_end < bit_start:
        raise ValueError(f"invalid bit range {bit_start}..{bit_end}")
    if bit_end >= len(payload) * 8:
        raise ValueError(f"bit range {bit_start}..{bit_end} exceeds {len(payload)}-byte payload")
    start_byte = bit_start >> 3
    end_byte = bit_end >> 3
    assembled = int.from_bytes(payload[start_byte:end_byte + 1], "big")
    shift = 7 - (bit_end & 7)
    width = bit_end - bit_start + 1
    return (assembled >> shift) & ((1 << width) - 1)


def _trunc_div_toward_zero(numerator: int, denominator: int) -> int:
    if denominator == 0:
        raise ZeroDivisionError("Toyota physical conversion divisor is zero")
    quotient = abs(numerator) // abs(denominator)
    return -quotient if (numerator < 0) != (denominator < 0) else quotient


def convert_p5_physical(raw: int, *, bit_width: int, signed: bool, mul: int, div: int, offset: int) -> int:
    """Apply ordinary P5 CCmdConversionTbl/CComDataConvert integer semantics."""
    if bit_width <= 0:
        raise ValueError(f"invalid bit width {bit_width}")
    mask = (1 << bit_width) - 1
    value = raw & mask
    if signed and value & (1 << (bit_width - 1)):
        value -= 1 << bit_width
    numerator = value * mul
    converted = numerator if div <= 1 else _trunc_div_toward_zero(numerator, div)
    return converted + offset


def format_p5_decimal(converted_integer: int, decimal_point_count: int) -> str:
    """Render Techstream's integer graph value with its DDB decimal precision."""
    if decimal_point_count < 0:
        raise ValueError(f"invalid decimal point count {decimal_point_count}")
    if decimal_point_count == 0:
        return str(converted_integer)
    scale = 10 ** decimal_point_count
    magnitude = abs(converted_integer)
    whole, fraction = divmod(magnitude, scale)
    sign = "-" if converted_integer < 0 else ""
    return f"{sign}{whole}.{fraction:0{decimal_point_count}d}"


def decode_p5_signal(
    payload: bytes,
    *,
    bit_start: int,
    bit_end: int,
    mul: int,
    div: int,
    offset: int,
    signed: bool,
    decimal_point_count: int,
    patterns: dict[int, str | None] | None = None,
) -> dict[str, Any]:
    """Decode one ordinary current-P5 Data Monitor signal from its DID value payload."""
    raw = extract_msb0(payload, bit_start, bit_end)
    converted = convert_p5_physical(
        raw,
        bit_width=bit_end - bit_start + 1,
        signed=signed,
        mul=mul,
        div=div,
        offset=offset,
    )
    pattern = (patterns or {}).get(converted)
    return {
        "raw": raw,
        "converted_integer": converted,
        "value": format_p5_decimal(converted, decimal_point_count),
        "pattern": pattern,
    }


def extract_monitor_records(section: Any) -> list[MonitorRecord]:
    table = int(section.header.table_type)
    if table not in {62, 157}:
        raise ValueError(f"expected monitor table 62/157, got {table}")
    size = int(section.decoded_record_size)
    shift = 0x10 if size >= 0x50 else 0
    if size < 0x3A + shift:
        raise ValueError(f"monitor table {table} record size too small: 0x{size:X}")
    out = []
    for index, raw in enumerate(records(section)):
        u16 = lambda off: struct.unpack_from("<H", raw, off)[0]
        u32 = lambda off: struct.unpack_from("<I", raw, off)[0]
        out.append(MonitorRecord(
            table=table,
            index=index,
            name_string_index=u32(0x18 + shift),
            monitor_key=u16(0x24 + shift),
            physical_data_key=u16(0x2A + shift),
            bit_start=u16(0x2C + shift),
            bit_end=u16(0x2E + shift),
            pattern_display_key=u16(0x32 + shift),
            primary_did=u16(0x36 + shift),
            alternate_did=u16(0x38 + shift),
            sort_key=u16(0x30 + shift),
            raw=raw,
        ))
    return out


def extract_behavior_records(section: Any) -> list[BehaviorRecord]:
    table = int(section.header.table_type)
    if table != 87 or section.decoded_record_size < 20:
        raise ValueError(f"expected behavior table 87 with >=20-byte rows, got {table}/{section.decoded_record_size}")
    out = []
    for index, raw in enumerate(records(section)):
        out.append(BehaviorRecord(
            table=87,
            index=index,
            signature=raw[:12].decode("utf-16-le", errors="replace").split("\x00", 1)[0],
            name_string_index=struct.unpack_from("<I", raw, 0x0C)[0],
            comment_string_index=struct.unpack_from("<I", raw, 0x10)[0],
            behavior_code=struct.unpack_from("<H", raw, 0x14)[0],
            raw=raw,
        ))
    return out


def extract_rob_signal_records(section: Any) -> list[RobSignalRecord]:
    table = int(section.header.table_type)
    size = int(section.decoded_record_size)
    if table != 88 or size < 0x43:
        raise ValueError(f"expected current behavior-data table 88 with >=0x43-byte rows, got {table}/0x{size:X}")
    out = []
    for index, raw in enumerate(records(section)):
        u16 = lambda off: struct.unpack_from("<H", raw, off)[0]
        u32 = lambda off: struct.unpack_from("<I", raw, off)[0]
        out.append(RobSignalRecord(
            table=88,
            index=index,
            name_string_index=u32(0x20),
            record_key=u16(0x2C),
            support_condition_key=u16(0x2E),
            physical_data_key=u16(0x30),
            bit_start=u16(0x32),
            bit_end=u16(0x34),
            sort_key=u16(0x36),
            pattern_display_key=u16(0x38),
            exception_handler_id=u16(0x3A),
            did=u16(0x3C),
            extraction_mode=raw[0x3E],
            presentation_mode=raw[0x3F],
            exception_handler_flag=raw[0x42],
            raw=raw,
        ))
    return out


def _physical_info(
    db: Any, strings: Any, *, physical_data_key: int, bit_start: int, bit_end: int,
    pattern_display_key: int,
) -> dict[str, Any] | None:
    physical_section = db.sections.get(13)
    unit_section = db.sections.get(15)
    if physical_section is None or unit_section is None:
        return None
    physical = next((raw for raw in records(physical_section)
                     if len(raw) >= 0x16 and struct.unpack_from("<H", raw, 0x0C)[0] == physical_data_key), None)
    if physical is None:
        return None
    unit_key = struct.unpack_from("<H", physical, 0x0E)[0]
    unit = next((raw for raw in records(unit_section)
                 if len(raw) >= 8 and struct.unpack_from("<H", raw, 0x04)[0] == unit_key), None)
    unit_text = None if unit is None else strings.get_string(struct.unpack_from("<I", unit, 0x00)[0])
    patterns: dict[int, str | None] = {}
    pattern_section = db.sections.get(14)
    if pattern_section is not None and pattern_display_key:
        for raw in records(pattern_section):
            if len(raw) >= 0x0E and struct.unpack_from("<H", raw, 0x0C)[0] == pattern_display_key:
                patterns[struct.unpack_from("<I", raw, 0x04)[0]] = strings.get_string(struct.unpack_from("<I", raw, 0x00)[0])
    return {
        "physical_data_key": physical_data_key,
        "mul": struct.unpack_from("<i", physical, 0x00)[0],
        "div": struct.unpack_from("<i", physical, 0x04)[0],
        "offset": struct.unpack_from("<i", physical, 0x08)[0],
        "unit_key": unit_key,
        "unit": unit_text,
        "signed": bool(physical[0x14]),
        "decimal_point_count": physical[0x15],
        "bit_width": bit_end - bit_start + 1,
        "pattern_display": dict(sorted(patterns.items())),
    }


def _signal_info(db: Any, strings: Any, record: MonitorRecord) -> dict[str, Any] | None:
    info = _physical_info(
        db, strings,
        physical_data_key=record.physical_data_key,
        bit_start=record.bit_start,
        bit_end=record.bit_end,
        pattern_display_key=record.pattern_display_key,
    )
    if info is None:
        return None
    shift = 0x10 if len(record.raw) >= 0x50 else 0
    info.update({
        "data_range": [
            struct.unpack_from("<i", record.raw, 0x10 + shift)[0],
            struct.unpack_from("<i", record.raw, 0x0C + shift)[0],
        ],
        "graph_range": [
            struct.unpack_from("<i", record.raw, 0x08 + shift)[0],
            struct.unpack_from("<i", record.raw, 0x04 + shift)[0],
        ],
    })
    return info


def monitor_rows(
    db: Any,
    strings: Any,
    source: str,
    *,
    deduplicate: bool = True,
    include_signal_info: bool = False,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for table in (62, 157):
        section = db.sections.get(table)
        if section is None:
            continue
        for record in extract_monitor_records(section):
            row = {
                "kind": "did",
                "source": source,
                "table": table,
                "tables": [table],
                "record": record.index,
                "name": strings.get_string(record.name_string_index),
                "monitor_key": record.monitor_key,
                "physical_data_key": record.physical_data_key,
                "bit_start": record.bit_start,
                "bit_end": record.bit_end,
                "pattern_display_key": record.pattern_display_key,
                "primary_did": record.primary_did,
                "alternate_did": record.alternate_did,
                "sort_key": record.sort_key,
                "raw": record.raw,
            }
            if include_signal_info:
                row["signal_info"] = _signal_info(db, strings, record)
            rows.append(row)
    if not deduplicate:
        return rows
    by_identity: dict[tuple[Any, ...], dict[str, Any]] = {}
    for row in rows:
        identity = (row["name"], row["primary_did"], row["alternate_did"])
        existing = by_identity.get(identity)
        if existing is None:
            by_identity[identity] = row
        elif row["table"] not in existing["tables"]:
            existing["tables"].append(row["table"])
    return list(by_identity.values())


def dtc_rows(parser: DDBParser, db: Any, strings: Any, source: str) -> list[dict[str, Any]]:
    section = db.sections.get(65)
    if section is None:
        return []
    return [{
        "kind": "dtc",
        "source": source,
        "table": 65,
        "record": index,
        "code": entry.code,
        "packed_dtc": f"0x{entry.packed_dtc:06X}",
        "description": strings.get_string(entry.description_string_index),
        "failure": strings.get_string(entry.failure_string_index),
        "raw": entry.raw,
    } for index, entry in enumerate(parser.extract_dtc_failure_entries(section))]


def behavior_rows(db: Any, strings: Any, source: str) -> list[dict[str, Any]]:
    section = db.sections.get(87)
    if section is None:
        return []
    return [{
        "kind": "behavior",
        "source": source,
        "table": 87,
        "record": record.index,
        "signature": record.signature,
        "name": strings.get_string(record.name_string_index),
        "comment": strings.get_string(record.comment_string_index),
        "behavior_code": record.behavior_code,
        "raw": record.raw,
    } for record in extract_behavior_records(section)]



def rob_rows(db: Any, strings: Any, source: str, *, include_signal_info: bool = False) -> dict[str, Any]:
    """Decode current ordinary-P5 RoB behavior names and DID-scoped signal schemas.

    Type-88 rows are selected by returned DID at runtime. Type-90 supplies the local
    support mode; type-89 is represented as an explicit unresolved cross-DID key when
    present. Dynamic LSB table-64 membership is exported rather than silently applying
    V18-only behavior to current GTS+.
    """
    behavior = behavior_rows(db, strings, source)
    signal_section = db.sections.get(88)
    if signal_section is None:
        return {"behavior_codes": behavior, "signals": [], "dynamic_lsb_table_present": 64 in db.sections}

    did_modes: dict[int, int] = {}
    section90 = db.sections.get(90)
    if section90 is not None:
        for raw in records(section90):
            if len(raw) >= 7:
                did_modes[struct.unpack_from("<H", raw, 0x02)[0]] = raw[0x06]

    dynamic_keys: set[int] = set()
    section64 = db.sections.get(64)
    if section64 is not None:
        # Current table-64 key position is intentionally not named here until its
        # current consumer is independently pinned. Presence alone means the runtime
        # ChangeSignalLSB path may alter base physical coefficients.
        dynamic_keys = {-1}

    signals = []
    for record in extract_rob_signal_records(signal_section):
        row: dict[str, Any] = {
            "source": source,
            "table": 88,
            "record": record.index,
            "name": strings.get_string(record.name_string_index),
            "record_key": record.record_key,
            "support_condition_key": record.support_condition_key,
            "physical_data_key": record.physical_data_key,
            "bit_start": record.bit_start,
            "bit_end": record.bit_end,
            "sort_key": record.sort_key,
            "pattern_display_key": record.pattern_display_key,
            "exception_handler_id": record.exception_handler_id,
            "did": record.did,
            "extraction_mode": record.extraction_mode,
            "presentation_mode": record.presentation_mode,
            "exception_handler_flag": record.exception_handler_flag,
            "local_support_mode": did_modes.get(record.did),
            "dynamic_lsb_possible": bool(dynamic_keys),
            "raw": record.raw,
        }
        if include_signal_info:
            row["signal_info"] = _physical_info(
                db, strings,
                physical_data_key=record.physical_data_key,
                bit_start=record.bit_start,
                bit_end=record.bit_end,
                pattern_display_key=record.pattern_display_key,
            )
        signals.append(row)
    return {
        "behavior_codes": behavior,
        "signals": signals,
        "dynamic_lsb_table_present": 64 in db.sections,
        "cross_did_condition_rows": db.sections[89].header.record_count if 89 in db.sections else 0,
    }
