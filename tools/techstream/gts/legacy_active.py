"""Legacy Active Test parameter metadata recovered from current DS-4 consumers.

Evidence: GetATSignalInfo_DT.dll FUN_100014d0 (VA 100014d0), with
FUN_10001010 debug labels; GetActTstInitP4.dll FUN_100018f0/100010a0.
Same-release decompilations: build/out/active-meta-native/{19,5}.c.
These are parameter/display schemas, not permission to execute an actuator.
"""
from __future__ import annotations

import struct
from typing import Any

from tools.techstream.ddb_semantics import records, _physical_info


def _u16(raw: bytes, offset: int) -> int:
    return struct.unpack_from("<H", raw, offset)[0]


def _u32(raw: bytes, offset: int) -> int:
    return struct.unpack_from("<I", raw, offset)[0]


def _rows(db: Any, table: int, size: int):
    section = db.sections.get(table)
    if section is None:
        return
    if section.decoded_record_size != size:
        raise ValueError(f"legacy active table {table}: expected {size}-byte rows, got {section.decoded_record_size}")
    yield from enumerate(records(section))


def legacy_active_patterns(db: Any, source: str) -> list[dict[str, Any]]:
    """Decode the parameter panel/timing fields actually copied by native code."""
    return [{
        "source": source, "table": 12, "record": index, "raw": raw,
        "pattern_key": _u16(raw, 0),
        "repeat_interval": _u16(raw, 2),
        "timeout_parameter": _u16(raw, 8),
        "repeat_enabled": raw[20],
        "maintenance_time": _u16(raw, 4),
        "auto_continuation_time": _u16(raw, 6),
        "pattern_display_key": _u16(raw, 10),
        "lock_time": _u16(raw, 12),
        "key_invalid_flag": raw[18],
        "key_operation_pattern": raw[19],
        "button_size": raw[21],
        "uninterpreted_bytes": {"14_17": raw[14:18].hex(), "22_23": raw[22:24].hex()},
    } for index, raw in _rows(db, 12, 24)]


def legacy_request_program(raw: bytes) -> dict[str, Any]:
    """Symbolic request encoder, not guessed UDS frames.

    DataMonitorPhase3 VA100042a0 / Phase4 VA1000c9f0. Native walks at most
    four nibbles, low-first, stopping at zero. Support-dependent operations
    deliberately retain their runtime dependency.
    """
    operations = {
        1: "zero", 2: "value_low_byte", 3: "value_shifted_left_7_minus_bit_end_mod8",
        4: "constant", 5: "constant", 6: "constant_plus_value_low_byte",
        7: "timeout_parameter", 8: "command_parameter_28_low_byte",
        10: "value_high_byte", 11: "support_prefix_and_padding",
        12: "support_tail_padding", 13: "constant_and_support_mask",
        14: "p4_timeout_mask_and_padding",
    }
    encoded = _u16(raw, 74)
    decoded = []
    for ordinal in range(4):
        opcode = (encoded >> (4 * ordinal)) & 15
        if not opcode:
            break
        decoded.append({"opcode": opcode, "operation": operations.get(opcode, "zero")})
    return {
        "encoded": encoded, "nibble_order": "least_significant_first",
        "operations": decoded, "request_identifier": raw[82],
        "constant_or_mask": raw[88],
        "service_by_generation_low5": {"1": 0x6D, "2": 0x6D, "7": 0x3D, "default": 0x30},
        "generation_7": "identifier-only request; program is bypassed",
        "support_required": any(row["opcode"] in (11, 12, 13, 14) for row in decoded),
        "variant_boundary": "Base encoder substitutes timeout 6 when table12 +8 is zero; P4 override uses zero literally and implements opcode14. Support operations require generation low5=4 and live DID support bytes.",
    }


def legacy_active_tests(db: Any, strings: Any, source: str) -> list[dict[str, Any]]:
    patterns = legacy_active_patterns(db, source)
    by_key: dict[int, list[dict[str, Any]]] = {}
    for pattern in patterns:
        by_key.setdefault(pattern["pattern_key"], []).append(pattern)
    result = []
    for index, raw in _rows(db, 11, 92):
        pattern_key = _u16(raw, 64)
        matches = by_key.get(pattern_key, [])
        # Native GetDbRecord can return multiple records; consumer reads first.
        pattern = matches[0] if matches else None
        display_key = pattern["pattern_display_key"] if pattern else 0
        info = _physical_info(db, strings, physical_data_key=_u16(raw, 62),
                              bit_start=_u16(raw, 66), bit_end=_u16(raw, 68),
                              pattern_display_key=display_key)
        if info is not None:
            physical = db.sections.get(13)
            for physical_raw in records(physical):
                if _u16(physical_raw, 12) == _u16(raw, 62):
                    info["sign_mode"] = physical_raw[20]
                    # Native modes are not a boolean: preserve mode 3 as 3.
                    info.pop("signed", None)
                    break
        row = {
            "source": source, "table": 11, "record": index, "raw": raw,
            "id": _u16(raw, 56), "primary_key": raw[82],
            "name_string_index": _u32(raw, 32),
            "name": strings.get_string(_u32(raw, 32)),
            "initial_value": _u32(raw, 20),
            "data_max": _u32(raw, 24), "data_min": _u32(raw, 28),
            "comment_id": _u32(raw, 36), "help_id": _u32(raw, 40),
            "info_id": _u32(raw, 44), "caution_id": _u32(raw, 48),
            "prohibition_id": _u32(raw, 52),
            "initial_value_monitor_key": _u16(raw, 58),
            "physical_data_key": _u16(raw, 62),
            "active_test_pattern_key": pattern_key,
            "bit_start": _u16(raw, 66), "bit_end": _u16(raw, 68),
            "data_max_monitor_key": _u16(raw, 76),
            "data_min_monitor_key": _u16(raw, 78),
            "initial_value_mode": raw[84], "presentation_pattern": raw[85],
            "data_limits_mode": raw[89],
            "uninterpreted_bytes": {
                "0_19": raw[:20].hex(), "60_61": raw[60:62].hex(),
                "70_73": raw[70:74].hex(), "80_81": raw[80:82].hex(),
                "83": raw[83:84].hex(), "86_87": raw[86:88].hex(),
                "90_91": raw[90:92].hex(),
            },
            "pattern": pattern,
            "pattern_match_count": len(matches),
            "signal_info": info,
            "request_program": legacy_request_program(raw),
            "execution": "metadata_only",
            "runtime_boundary": "Initial value/limits and support-dependent request operations require live reads. Symbolic request encoding is decoded; stop scheduling, transport framing and active executor selection are not supplied by this metadata.",
        }
        result.append(row)
    return result
