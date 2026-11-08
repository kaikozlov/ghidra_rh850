"""P6 catalog projections from the consumer-pinned 2026 GTS table layouts.

These are static catalogs, not vehicle-supported lists. Runtime admission still
requires support replies, field bounds and the exported cross-DID conditions.
See docs/tooling/gtsplus-p5-adas-p6-migration.md sections 9–11.
"""
from __future__ import annotations

import struct
from typing import Any, Callable

from tools.techstream.ddb_semantics import extract_monitor_records, records


def _rows(db: Any, table: int, minimum: int) -> list[bytes]:
    section = db.sections.get(table)
    if section is None:
        return []
    result = list(records(section))
    if any(len(raw) < minimum for raw in result):
        raise ValueError(f"P6 table {table}: record shorter than {minimum} bytes")
    return result


def _u16(raw: bytes, offset: int) -> int:
    return struct.unpack_from("<H", raw, offset)[0]


def _u32(raw: bytes, offset: int) -> int:
    return struct.unpack_from("<I", raw, offset)[0]


def p6_catalog(
    db: Any, strings: Any, source: str, *,
    resolve_variable: Callable[[int], bytes],
) -> dict[str, Any]:
    """Project all P6 monitor/FFD/ROB records without P5 duplicate-table unions."""
    physical_rows = {_u16(r, 12): r for r in _rows(db, 13, 22)}

    units = {_u16(r, 4): strings.get_string(_u32(r, 0)) for r in _rows(db, 15, 8)}
    patterns: dict[int, dict[str, Any]] = {}
    for raw in _rows(db, 14, 14):
        patterns.setdefault(_u16(raw, 12), {})[str(struct.unpack_from("<i", raw, 4)[0])] = strings.get_string(_u32(raw, 0))

    def physical(key: int, start: int, end: int, pattern: int) -> dict[str, Any] | None:
        raw = physical_rows.get(key)
        if raw is None:
            return None
        mul, div, offset = struct.unpack_from("<iii", raw)
        return {"physical_data_key": key, "mul": mul, "div": div, "offset": offset,
                "unit_key": _u16(raw, 14), "unit": units.get(_u16(raw, 14)),
                "sign_mode": raw[20], "decimal_point_count": raw[21],
                "bit_width": end - start + 1, "pattern_display": patterns.get(pattern, {})}

    def supports(table: int) -> dict[int, dict[str, Any]]:
        result = {}
        for index, raw in enumerate(_rows(db, table, 7)):
            did = _u16(raw, 2)
            fixed = _u16(raw, 4)
            row = {"table": table, "record": index, "did": did,
                   "fixed_length": fixed, "support_mode": raw[6],
                   "snapshot_length_encoding": "fixed" if fixed else
                   "inline_be16" if did >= 0x9000 else "inline_u8"}
            if did in result:
                result[did].setdefault("additional_records", []).append(row)
            else:
                result[did] = row
        return result

    def conditions(table: int) -> dict[int, dict[str, Any]]:
        result = {}
        for index, raw in enumerate(_rows(db, table, 15 if table == 63 else 12)):
            key, variable_id = _u16(raw, 0), _u16(raw, 2)
            value = resolve_variable(variable_id)
            if len(value) < 2:
                raise ValueError(f"P6 table {table} condition {key}: variable has no DID")
            if key in result:
                raise ValueError(f"P6 table {table}: duplicate condition {key}")
            row = {"table": table, "record": index, "key": key,
                   "variable_id": variable_id, "variable_bytes": value.hex(),
                   "referenced_did": int.from_bytes(value[:2], "big"),
                   "bit_start": _u16(raw, 6), "bit_end": _u16(raw, 8),
                   "condition_type": raw[13] if table == 63 else raw[11]}
            if table == 63:
                row.update(comparison_value=_u16(raw, 10), comparison_mode=raw[14])
            result[key] = row
        return result

    def condition(table: dict[int, Any], key: int) -> Any:
        if not key:
            return None
        if key not in table:
            raise ValueError(f"P6 missing condition {key}")
        return table[key]

    live_support, rob_support = supports(61), supports(90)
    live_conditions, ffd_conditions, rob_conditions = conditions(63), conditions(80), conditions(89)
    composites: dict[int, list[str]] = {}
    for raw in _rows(db, 26, 2):
        composites.setdefault(_u16(raw, 0), []).append(raw.hex())
    monitors = []
    _rows(db, 62, 80)
    if 62 in db.sections:
        monitors = extract_monitor_records(db.sections[62])
    dids: dict[str, list[Any]] = {}
    live, snapshots = [], []
    for record in monitors:
        raw = record.raw
        info = physical(record.physical_data_key, record.bit_start, record.bit_end,
                        record.pattern_display_key)
        flags = _u32(raw, 0x30)
        base = {"source": source, "table": 62, "record": record.index,
                "monitor_key": record.monitor_key,
                "name": strings.get_string(record.name_string_index) or "",
                "primary_did": record.primary_did, "alternate_did": record.alternate_did,
                "flags": flags, "bit_start": record.bit_start, "bit_end": record.bit_end,
                "sort_key": record.sort_key, "physical_data_key": record.physical_data_key,
                "pattern_display_key": record.pattern_display_key,
                "extraction_mode": raw[0x4A], "visibility_override": raw[0x4B],
                "signal_info": info,
                "physical_range": list(reversed(struct.unpack_from("<dd", raw, 0))),
                "graph_range": [struct.unpack_from("<i", raw, 0x18)[0],
                                struct.unpack_from("<i", raw, 0x14)[0]]}
        # No deduplication: independent records may have distinct admission rules.
        row = {**base, "did": f"0x{record.primary_did:04X}",
               "list_member": bool(flags & 1),
               "wire_field": not bool(flags & 0x18) and record.primary_did != 0,
               "support_condition": condition(live_conditions, _u16(raw, 0x36)),
               "did_support": live_support.get(record.primary_did),
               "composite_records": composites.get(record.monitor_key, [])}
        live.append(row)
        if row["wire_field"]:
            dids.setdefault(row["did"], []).append({
                **base, **(info or {}), "decoder": "p6-native-msb0-u32-v1",
                "support_condition": row["support_condition"],
                "did_support": row["did_support"], "list_member": row["list_member"],
            })
        if flags & 2:
            support = live_support.get(record.alternate_did)
            snapshots.append({**base, "snapshot_did": record.alternate_did,
                              "support_condition": condition(ffd_conditions, record.ffd_support_condition_key),
                              "did_support": support,
                              "local_support_mode": None if support is None else support["support_mode"],
                              "decoder": "p6-native-msb0-u32-v1"})
    behaviors = []
    # KgpDataCtrl100C4BE0 stride68;100C4C20 flag+64,100C4C60 id+60.
    for index, raw in enumerate(_rows(db, 163, 68)):
        if len(raw) != 68:
            raise ValueError(f"{source}: ROB table163 requires exact68-byte layout, got{len(raw)}")
        terminator = next((offset for offset in range(0, 44, 2) if raw[offset:offset + 2] == b"\0\0"), 44)
        if terminator < 44 and any(raw[terminator + 2:44]):
            raise ValueError(f"{source}: ROB table163 has nonzero signature suffix after terminator")
        behaviors.append({"source": source, "table": 163, "record": index, "raw": raw.hex(),
                          "name_string_index": _u32(raw,48),
                          "division_string_index": _u32(raw,52),
                          "comment_string_index": _u32(raw,56),
                          "exception_handler_id": _u16(raw,60),
                          "exception_handler_flag": raw[64],
                          "signature": raw[:44].decode("utf-16le").split("\x00", 1)[0],
                          "behavior_code": _u32(raw, 44),
                          "name": strings.get_string(_u32(raw, 48)),
                          "division": strings.get_string(_u32(raw, 52)),
                          "comment": strings.get_string(_u32(raw, 56)),
                          "enabled": raw[62], "memory_override": raw[63],
                          "uninterpreted_bytes": {"65_67": raw[65:68].hex()}})
    rob = []
    for index, raw in enumerate(_rows(db, 164, 48)):
        if len(raw) != 48:
            raise ValueError(f"{source}: ROB table164 requires exact48-byte layout, got{len(raw)}")
        key, cond, phy, start, end, order, pattern = struct.unpack_from("<7H", raw, 20)
        did = _u16(raw, 36)
        support = rob_support.get(did)
        # KgpDataCtrl100C5630 flag+42 and100C5670 id+34.
        rob.append({"source": source, "table": 164, "record": index, "raw": raw.hex(),
                    "name_string_index": _u32(raw,16),
                    "exception_handler_id": _u16(raw,34),
                    "exception_handler_flag": raw[42],
                    "record_key": key, "name": strings.get_string(_u32(raw, 16)),
                    "did": did, "support_condition_key": cond,
                    "support_condition": condition(rob_conditions, cond),
                    "physical_data_key": phy, "bit_start": start, "bit_end": end,
                    "sort_key": order, "pattern_display_key": pattern,
                    "extraction_mode": raw[40], "presentation_mode": raw[41],
                    "physical_range": list(reversed(struct.unpack_from("<dd", raw))),
                    "did_support": support,
                    "local_support_mode": None if support is None else support["support_mode"],
                    "signal_info": physical(phy, start, end, pattern),
                    "decoder": "p6-native-msb0-u32-v1",
                    "uninterpreted_bytes": {"38_39": raw[38:40].hex(), "43_47": raw[43:48].hex()}})
    return {
        "dids": dids,
        "data_list": {"tables": [62] if 62 in db.sections else [],
                      "record_counts": {"62": len(monitors)}, "row_count": len(live),
                      "display_order": "native type-62 record order; runtime admission is not evaluated",
                      "rows": live},
        "generic_ffd": {"signals": snapshots, "conditions": list(ffd_conditions.values()),
                        "condition_count": len(ffd_conditions), "did_support": list(live_support.values()),
                        "dynamic_lsb_table_present": 64 in db.sections},
        "rob": {"behavior_codes": behaviors, "signals": rob,
                "conditions": list(rob_conditions.values()), "did_support": list(rob_support.values()),
                "dynamic_lsb_table_present": False},
    }
