"""Native P6 DDR schemas, not the unrelated managed PCS viewer schema.

Evidence (2026 GTS+):
KgpDataCtrl FindDbItem1 VA100a2280/1009c8d0/100a2d10/100a3700,
DDRDiagCode DecisionKey100a21f0, DDRInvalid ComparativeKey100a38c0,
DDRFreezeFrame SortInOrder100a2a60 and each table's exception accessors.
CommandCommon CCmdGetDDRInfoP6Base: GetSSR10040cb0, GetSSRData10041300,
SetSignalInfo10044790, SetTriggerName10044b60, GetCalcInfo1003fe30,
GetInvalidInfo10040970, CheckInvalidDBValue1003f140.
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
        raise ValueError(f"native DDR table {table}: expected {size}-byte rows, got {section.decoded_record_size}")
    yield from enumerate(records(section))


def ddr_invalid_condition(raw: bytes, *, source: str, table: int, record: int) -> dict[str, Any]:
    """Shared CDbDDRInvalidConditionTable record, including all factory aliases."""
    if len(raw) != 16:
        raise ValueError(f"DDR invalid condition expected 16 bytes, got {len(raw)}")
    return {
        "source": source, "table": table, "record": record, "raw": raw,
        "signal_key": _u16(raw, 4), "referenced_signal_key": _u16(raw, 6),
        "comparison_value": _u32(raw, 0), "condition_order": _u16(raw, 8),
        "exception_id": _u16(raw, 10), "exception_flag": raw[14],
        "combination_mode": raw[12], "comparison_mode": raw[13],
        "comparison": {1: "equal", 2: "not_equal"}.get(raw[13], "unsupported"),
    }


def p6_ddr_catalog(db: Any, strings: Any, source: str) -> dict[str, Any]:
    """Decode every source row, keeping duplicate keys and exception gates.

    Source ordinals remain stable. Linked record ordinals, rather than copied
    payloads, preserve the one-to-many admission/condition relationships.
    """
    triggers = []
    for index, raw in _rows(db, 165, 20):
        triggers.append({
            "source": source, "table": 165, "record": index, "raw": raw,
            "dtc_identifier": _u32(raw, 0),
            "name_string_index": _u32(raw, 4), "name": strings.get_string(_u32(raw, 4)),
            "trigger_memo_string_index": _u32(raw, 8), "trigger_memo": strings.get_string(_u32(raw, 8)),
            "exception_id": _u16(raw, 12), "exception_flag": raw[19],
            "trigger_selector_0": raw[16], "trigger_selector_1": raw[17],
            "trigger_point_enabled": raw[18],
            "unresolved_u16_0e": _u16(raw, 14),
        })
    data_ids = []
    by_did: dict[int, list[int]] = {}
    for index, raw in _rows(db, 166, 8):
        did = _u16(raw, 0)
        data_ids.append({
            "source": source, "table": 166, "record": index, "raw": raw,
            "did": did, "payload_length": _u16(raw, 2),
            "exception_id": _u16(raw, 4), "validity_mode": raw[6], "exception_flag": raw[7],
        })
        by_did.setdefault(did, []).append(index)
    invalid = []
    by_signal: dict[int, list[int]] = {}
    for index, raw in _rows(db, 168, 16):
        key = _u16(raw, 4)
        invalid.append(ddr_invalid_condition(raw, source=source, table=168, record=index))
        by_signal.setdefault(key, []).append(index)
    for indices in by_signal.values():
        indices.sort(key=lambda index: invalid[index]["condition_order"])
    signals = []
    physical = db.sections.get(13)
    physical_rows: dict[int, list[bytes]] = {}
    if physical is not None:
        for raw in records(physical):
            if len(raw) < 22:
                raise ValueError("native DDR physical record shorter than 22 bytes")
            physical_rows.setdefault(_u16(raw, 12), []).append(raw)
    for index, raw in _rows(db, 167, 40):
        did, key, start, end, order, phy, pattern = struct.unpack_from("<7H", raw, 20)
        info = _physical_info(db, strings, physical_data_key=phy,
                              bit_start=start, bit_end=end, pattern_display_key=pattern)
        if info is not None:
            info.pop("signed", None)
            info["sign_mode"] = physical_rows[phy][0][20]
        signals.append({
            "source": source, "table": 167, "record": index, "raw": raw,
            "name_string_index": _u32(raw, 16), "name": strings.get_string(_u32(raw, 16)),
            "did": did, "signal_key": key, "bit_start": start, "bit_end": end,
            "sort_key": order, "physical_data_key": phy, "pattern_display_key": pattern,
            "signal_info": info,
            "data_id_records": by_did.get(did, []),
            "invalid_condition_records": by_signal.get(key, []),
            "exception_id": _u16(raw, 34), "exception_flag": raw[39],
            "list_member": bool(raw[36]) and raw[37] != 2,
            "visibility": raw[36], "signal_role": raw[37], "presentation_mode": raw[38],
            # CCmdFrzFrmDat +0x90/+0x88 are DataMin/DataMax, pinned by
            # GetDatMonSignalInfo debug labels via the shared table10 copies.
            "data_min": struct.unpack_from("<d", raw, 0)[0],
            "data_max": struct.unpack_from("<d", raw, 8)[0],
        })
    return {
        "triggers": triggers, "data_ids": data_ids, "signals": signals,
        "invalid_conditions": invalid,
        "semantics": {
            "validity_modes": {"0": "valid", "1": "single-bit field on odd byte; previous-byte corresponding bit admits value", "2": "valid"},
            "comparison_modes": {"1": "equal", "2": "not_equal"},
            "combination_modes": {"0": "single", "1": "and-group", "2": "or-group"},
            "condition_order": "native owner-key then condition-order; duplicate records preserved",
            "runtime_boundary": "Static schema and exception gates only; DDR replies and native exception context determine admitted records and values.",
        },
    }
