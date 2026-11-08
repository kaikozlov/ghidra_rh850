"""Current GTS+ legacy monitor/FFD table10, decoded from native consumers.

Despite its CDbFreezeTable name, this table also supplies live Data List rows.
Offsets refer to 104-byte current GTS+ records, not the 84-byte V18 layout.
GetDatMonSignalInfo.dll 100012B4–100014CA proves signal/physical joins;
its debug strings identify the copied presentation fields. KgpDataCtrl
100B34C0/100B35D0 proves PID/monitor indices, 100B2FC9 proves display order.
CommandCommon CheckSupportPid 1006DCD0 proves type8 admission conditions.
"""
from __future__ import annotations

import struct
from collections import defaultdict
from typing import Any, Iterable

from tools.techstream.ddb_semantics import format_p5_decimal, records
from tools.techstream.native_conversion import convert_scalar


def extract_legacy_scalar(payload: bytes, start: int, end: int) -> int:
    """CommandCommon FUN_100BFF7C inclusive MSB0 with native u32 folding.

    Input is the PID payload after protocol framing and, for P4, ConvertPid.
    Never apply the bit offsets directly to a complete diagnostic response.
    """
    if start < 0 or end < start or end >= len(payload) * 8:
        raise ValueError("legacy signal bit range outside PID payload")
    first, last = start >> 3, end >> 3
    shift = -(~end & 7)
    value = payload[last] >> (~end & 7)
    if first == last:
        return value & ((1 << (end - start + 1)) - 1)
    for index in range(last - 1, first, -1):
        shift += 8
        value |= (payload[index] << (shift & 31)) & 0xFFFFFFFF
    head = (payload[first] << (start & 7)) & 0xFF
    width_minus_one = end - start
    if width_minus_one < 7:
        head >>= (7 - width_minus_one) & 31
    else:
        head <<= (width_minus_one - 7) & 31
    return (value | head) & 0xFFFFFFFF


def decode_legacy_scalar(
    row: dict[str, Any], payload: bytes, *, live: bool = False,
    dynamic_lsb: int | None = None,
) -> dict[str, Any]:
    """Native freeze numeric/enum value, or live special-format numeric value.

    CCmdFrzFrmDat::GetValue10034D60 uses the basic overload for every format.
    DatMonCommon10003680 instead dispatches special formats via10022B60.
    Neither path is the separate GetValueEx GUI text-formatting interface.
    """
    if len(row["physical_records"]) != 1:
        raise ValueError("legacy scalar needs one unambiguous physical record")
    phy = row["physical_records"][0]
    dynamic = row.get("dynamic_lsb_records", [])
    if dynamic:
        if dynamic_lsb is None:
            raise ValueError("runtime PID slope required for table39 dynamic LSB")
        if len(dynamic) != 1:
            raise ValueError("ambiguous dynamic LSB rows")
        if dynamic_lsb:
            import math
            numerator = _i32(dynamic_lsb * dynamic[0]["mul"] * 10 ** phy["decimal_point_count"])
            denominator = dynamic[0]["div"]
            divisor = math.gcd(numerator, denominator)
            if not divisor:
                raise ValueError("zero dynamic LSB ratio")
            phy = {**phy, "mul": numerator // divisor, "div": denominator // divisor}
    value = extract_legacy_scalar(payload, row["bit_start"], row["bit_end"])
    raw = value
    converted = convert_scalar(value, phy["bit_width"], phy["mul"], phy["div"],
                               phy["offset"], phy["sign_mode"])
    if live:
        converted = _live_value(raw, row["data_type"], phy, converted)
    return {"raw": raw, "converted_integer": converted,
            "value": format_p5_decimal(converted, phy["decimal_point_count"]),
            "patterns": [item["text"] for item in phy["patterns"] if item["value"] == converted]}



def _i32(value: int) -> int:
    value &= 0xFFFFFFFF
    return value - (1 << 32) if value & 0x80000000 else value


def _trunc_div(value: int, divisor: int) -> int:
    quotient = abs(value) // abs(divisor)
    return -quotient if (value < 0) != (divisor < 0) else quotient


def _live_value(raw: int, data_type: int, phy: dict[str, Any], basic: int) -> int:
    """CComDataConvert10022B60 special overload; not GetValueEx."""
    if data_type == 6:
        if raw == 0:
            return 0
        first = 30000 // raw
        return max(0, first - 50 if first < 623 else 240000 // raw - 4400)
    if data_type == 19:
        value = convert_scalar(raw, 32, phy["mul"], phy["div"], phy["offset"], 0)
        hours = _trunc_div(value, 60)
        return _i32((value - hours * 60) | (hours * 256))
    if data_type == 24:
        return raw >> 1 if raw < 3001 else _i32(raw * 8 - 22500)
    if data_type in (7, 8, 9, 10, 11):
        width = {7: 10, 8: 12, 9: 10, 10: 8, 11: 16}[data_type]
        signed = data_type in (7, 8, 10)
        value = 0
        negative = False
        for bit in range(width):
            source_byte = (raw >> ((bit // 8) * 8)) & 255
            source_bit = (source_byte >> (7 - bit % 8)) & 1
            if signed and bit == width - 1:
                negative = bool(source_bit)
            else:
                value |= source_bit << bit
        value = -value if negative else value
        numerator = _i32(value * phy["mul"])
        if phy["div"] != 0:
            numerator = _trunc_div(numerator, phy["div"])
        return _i32(numerator + phy["offset"])
    return basic


def dynamic_lsb_rows(db: Any) -> list[dict[str, Any]]:
    """All table39 rows, including rows not referenced by a monitor."""
    if 39 not in db.sections:
        return []
    result = []
    for index, raw in enumerate(records(db.sections[39])):
        if len(raw) < 18:
            raise ValueError("legacy dynamic LSB table39 record shorter than18")
        result.append({
            "table": 39, "record": index, "monitor_key": struct.unpack_from("<H", raw, 8)[0],
            "mul": struct.unpack_from("<i", raw, 0)[0],
            "div": struct.unpack_from("<i", raw, 4)[0],
            "bit_start": struct.unpack_from("<H", raw, 10)[0],
            "bit_end": struct.unpack_from("<H", raw, 12)[0], "pid": raw[17],
            "uninterpreted_bytes": {"14_16": raw[14:17].hex(), "18_end": raw[18:].hex()},
            "raw": raw,
        })
    return result


def legacy_freeze_rows(
    db: Any, strings: Any, source: str, *, conditions: Iterable[dict[str, Any]] = (),
) -> list[dict[str, Any]]:
    """Decode signal schemas; keep vehicle support separate from static metadata."""
    def rows(table: int):
        return list(records(db.sections[table])) if table in db.sections else []

    def u16(raw: bytes, off: int) -> int:
        return struct.unpack_from("<H", raw, off)[0]

    def u32(raw: bytes, off: int) -> int:
        return struct.unpack_from("<I", raw, off)[0]

    physical = defaultdict(list)
    for index, raw in enumerate(rows(13)):
        if len(raw) < 22:
            raise ValueError("legacy physical table13 record shorter than22")
        physical[u16(raw, 12)].append((index, raw))
    units = defaultdict(list)
    for index, raw in enumerate(rows(15)):
        if len(raw) < 8:
            raise ValueError("legacy unit table15 record shorter than8")
        units[u16(raw, 4)].append({"table": 15, "record": index,
                                  "string_index": u32(raw, 0),
                                  "text": strings.get_string(u32(raw, 0)),
                                  "genre_id": u16(raw, 6)})
    patterns = defaultdict(list)
    for index, raw in enumerate(rows(14)):
        if len(raw) < 14:
            raise ValueError("legacy pattern table14 record shorter than14")
        patterns[u16(raw, 12)].append({"table": 14, "record": index,
                                     "value": struct.unpack_from("<i", raw, 4)[0],
                                     "string_index": u32(raw, 0),
                                     "text": strings.get_string(u32(raw, 0))})
    dynamic_lsb = defaultdict(list)
    for dynamic in dynamic_lsb_rows(db):
        dynamic_lsb[dynamic["monitor_key"]].append(dynamic)
    condition_index = defaultdict(list)
    for condition in conditions:
        if condition["table"] == 8:
            condition_index[condition["key"]].append(condition)
    result = []
    for index, raw in enumerate(rows(10)):
        if len(raw) != 104:
            raise ValueError(f"{source}: table10 record{index} length{len(raw)}; expected104")
        phy_key, pattern_key = u16(raw, 0x50), u16(raw, 0x5A)
        start, end = u16(raw, 0x52), u16(raw, 0x54)
        signal_info = []
        for phy_index, phy in physical[phy_key]:
            mul, div, offset = struct.unpack_from("<iii", phy)
            signal_info.append({"table": 13, "record": phy_index,
                                "physical_data_key": phy_key,
                                "mul": mul, "div": div, "offset": offset,
                                "sign_mode": phy[20], "decimal_point_count": phy[21],
                                "bit_width": end - start + 1,
                                "unit_key": u16(phy, 14), "units": units[u16(phy, 14)],
                                "patterns": patterns[pattern_key]})
        condition_key = u16(raw, 0x4E)
        result.append({
            "kind": "freeze_frame", "source": source, "table": 10, "record": index,
            "raw": raw, "layout": "gtsplus-104",
            "monitor_key": u16(raw, 0x4C),
            "name_string_index": u32(raw, 0x44),
            "name": strings.get_string(u32(raw, 0x44)),
            "short_name": raw[:24].decode("utf-16le").split("\x00", 1)[0],
            "pid": raw[0x63], "bit_start": start, "bit_end": end,
            "physical_data_key": phy_key, "pattern_display_key": pattern_key,
            "physical_records": signal_info,
            "dynamic_lsb_records": dynamic_lsb[u16(raw, 0x4C)],
            "data_max": struct.unpack_from("<d", raw, 0x18)[0],
            "data_min": struct.unpack_from("<d", raw, 0x20)[0],
            "graph_max": struct.unpack_from("<i", raw, 0x2C)[0],
            "graph_min": struct.unpack_from("<i", raw, 0x30)[0],
            "begin_condition": u32(raw, 0x28), "trigger_condition": u32(raw, 0x40),
            "slope_condition": raw[0x64], "slope_default": raw[0x65],
            "data_type": raw[0x60], "support_policy": raw[0x61],
            "membership_flags": raw[0x62], "live_member": bool(raw[0x62] & 1),
            "freeze_member": bool(raw[0x62] & 2),
            "sort_key": u16(raw, 0x58),
            "exception_handler_id": u16(raw, 0x5C),
            "exception_handler_flag": raw[0x66],
            "support_condition_key": condition_key,
            "support_conditions": condition_index[condition_key] if condition_key else [],
            "support_condition_resolved": not condition_key or bool(condition_index[condition_key]),
            # Bytes without a demonstrated consumer name remain explicitly bounded.
            "unassigned_fields": {"34_3f": raw[0x34:0x40].hex(),
                                  "48_4b": raw[0x48:0x4C].hex(),
                                  "56_57": raw[0x56:0x58].hex(),
                                  "5e_5f": raw[0x5E:0x60].hex(), "67": raw[0x67]},
        })
    return result
