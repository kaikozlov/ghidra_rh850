"""Legacy PID/DID response geometry and native support-bit predicates.

KgpDataCtrl.dll SHA256 19e709e12e53f485a84ccfbf6b226922b88502206c34b767db543c7f3df101f8:
FindDbItem1 PID/Did at 100C06D0/100AA0D0; exception getters
100C0820/100C0860, 100AA220/100AA260, 100C0320/100C0360,
100A9D20/100A9D60; variable resolution 100BFCB0/100A96B0.

Same-release recovered CommandCommon.dll SHA256
98e313d197eb7115d037a2d46e71343b4b44862356e9d772c8f2f03d96e638d3:
GetPidDataLength 1007E220, GetDidDataLength 1007D450,
CheckSupportPid 1006DCD0, CheckDidBitSupport 1006BC90,
CheckSupportBit 1006BDF0, CheckSupportBitOldBody 1006C8F0.
Their inclusive MSB-first extraction helper is 100BFF7C.
"""
from __future__ import annotations

import struct
from typing import Any, Callable

VariableResolver = Callable[[int], bytes]


def _records(db: Any, table: int, size: int):
    section = db.sections.get(table)
    if section is None:
        return
    for record in section.iter_records():
        if len(record.raw) != size:
            raise ValueError(f"legacy table {table} record {record.index}: expected {size} bytes, got {len(record.raw)}")
        yield record.index, record.raw


def response_definitions(db: Any, source: str = "") -> list[dict[str, Any]]:
    """Decode PID/DID keys, native response lengths and exception selection."""
    rows = []
    for table, key_offset, length_offset in ((6, 2, 3), (7, 4, 5)):
        for index, raw in _records(db, table, 8):
            length = raw[length_offset]
            row = {
                "table": table, "record": index, "source": source,
                "kind": "pid" if table == 6 else "did",
                "key": raw[key_offset], "data_length": length,
                "length_resolution": "runtime" if length == 0 else "fixed",
                "exception_id": struct.unpack_from("<H", raw)[0],
                "exception_flag": raw[6], "raw": raw.hex(),
            }
            # These bytes are retained independently: native length/key consumers
            # do not read them, so they must not be folded into an identifier.
            row["uninterpreted_fields"] = {
                "offset_4_5" if table == 6 else "offset_2_3":
                    raw[4:6].hex() if table == 6 else raw[2:4].hex(),
                "offset_7": raw[7],
            }
            rows.append(row)
    return rows


def support_conditions(
    db: Any, resolve_variable: VariableResolver | None = None, source: str = "",
) -> list[dict[str, Any]]:
    """Decode table-8/9 support queries and their response-bit predicates.

    Request selectors reference the native master function-frame table18.
    Request patches are relative to that frame, not guessed service bytes.
    Native exception filtering precedes key lookup; duplicate keys are retained.
    """
    rows = []
    modes = {
        2: {"request_selector": 0x10, "variable_length": 1, "request_offsets": [1], "response_offset": 2},
        3: {"request_selector": 0x69, "variable_length": 1, "request_offsets": [1], "response_offset": 2},
        4: {"request_selector": 0x6A, "variable_length": 2, "request_offsets": [2, 3], "response_offset": 4},
        6: {"cache": "did_support", "variable_min_length": 1, "response_offset": 0},
    }
    for table in (8, 9):
        for index, raw in _records(db, table, 12):
            key, variable_id, exception_id, start, end = struct.unpack_from("<5H", raw)
            mode = raw[11 if table == 8 else 10]
            row = {
                "table": table, "record": index, "source": source, "key": key,
                "variable_id": variable_id, "bit_start": start, "bit_end": end,
                "source_mode": mode, "exception_id": exception_id,
                "exception_flag": raw[10 if table == 8 else 11],
                "raw": raw.hex(), "predicate": "nonzero", "bit_order": "msb0",
                "native_consumers": ["CheckSupportBitP4"] if mode == 6 else
                    ["CheckSupportBit", "CheckSupportBitOldBody"],
            }
            query = modes.get(mode)
            row["query"] = dict(query) if query is not None else None
            if mode in (2, 6):
                row["p4_cache_query"] = {
                    "cache": "pid_support" if mode == 2 else "did_support",
                    "identifier_variable_offset": 0, "response_offset": 0,
                    "predicate": "nonzero",
                }
            row["native_status"] = "valid" if query is not None and end >= start else "invalid_geometry_or_mode"
            row["supported_identifier_gate"] = {
                "CheckSupportBit": {2: "pid", 3: "did"}.get(mode),
                "CheckSupportBitOldBody": None,
                "CheckSupportBitP4": "did" if mode == 6 else "pid" if mode == 2 else None,
            }
            if resolve_variable is not None:
                value = bytes(resolve_variable(variable_id))
                row["variable"] = value.hex()
                if query is not None:
                    if mode == 6:
                        if not value:
                            row["native_status"] = "invalid_variable_length"
                        else:
                            row["cache_identifier"] = value[0]
                    elif len(value) != query["variable_length"]:
                        row["native_status"] = "invalid_variable_length"
                    else:
                        row["request_patches"] = [
                            {"offset": offset, "value": byte}
                            for offset, byte in zip(query["request_offsets"], value)
                        ]
            rows.append(row)
    return rows


def evaluate_support_condition(condition: dict[str, Any], response: bytes) -> bool:
    """Evaluate a decoded condition on its native frame response bytes.

    Availability/exception selection and communication success are caller inputs.
    This function implements the native nonzero bit predicate after header removal.
    """
    query = condition.get("query")
    if query is None or condition.get("native_status") != "valid":
        raise ValueError("condition has no valid native query")
    start, end = int(condition["bit_start"]), int(condition["bit_end"])
    payload = response[int(query["response_offset"]):]
    if query.get("cache") and end >= len(payload) * 8:
        return False
    if start < 0 or end < start or end >= len(payload) * 8:
        raise ValueError("support predicate is outside response payload")
    # Native result is a 32-bit word; wider fields are not scalar predicates.
    width = end - start + 1
    if width > 32:
        raise ValueError("support predicate exceeds native 32-bit extraction")
    value = int.from_bytes(payload, "big") >> (len(payload) * 8 - end - 1)
    return bool(value & ((1 << width) - 1))
