"""Lossless semantic source rows independent of selected runtime P5/P6 plugins.

Alias tables are retained separately, without union/dedup or support filtering.
Consumer evidence: extract_gtsplus_p6_{data_list,freeze_frame,rob}; current
KgpDataCtrl native class factory and exception getters; DataMonitorPhase6
FUN100074E0 (dynamic DID/capacity); CommandCommon1008AE30 (DTC status masks).
"""
from __future__ import annotations

import struct
from typing import Any, Callable

from tools.techstream.ddb_semantics import records
from tools.techstream.gts.physical_catalog import physical_catalog

TABLE_SIZES = {61: 8, 156: 8, 62: 80, 157: 80, 63: 16, 66: 12,
               80: 12, 81: 8, 86: 4, 87: 28, 88: 72, 153: 72, 89: 12,
               90: 8, 151: 8, 91: 12, 152: 12}


def monitor_source_catalog(
    db: Any, strings: Any, source: str, *,
    resolve_variable: Callable[[int], bytes] | None = None,
) -> list[dict[str, Any]]:
    """Every row in source order; lookup references retain duplicate candidates."""
    libraries = physical_catalog(db, strings, source)
    # Preserve source ordering and duplicate candidates without rescanning whole
    # libraries for every signal. A unit occurs once per source row, even when
    # several candidate physical rows refer to that same unit key.
    physical_by_key: dict[int, list[dict[str, Any]]] = {}
    patterns_by_key: dict[int, list[dict[str, Any]]] = {}
    units_by_key: dict[int, list[tuple[int, dict[str, Any]]]] = {}
    for physical in libraries["physical"]:
        physical_by_key.setdefault(physical["key"], []).append(physical)
    for pattern in libraries["patterns"]:
        patterns_by_key.setdefault(pattern["key"], []).append(pattern)
    for ordinal, unit in enumerate(libraries["units"]):
        units_by_key.setdefault(unit["key"], []).append((ordinal, unit))
    physical_units = {}
    for key, physical in physical_by_key.items():
        unit_keys = {p["unit_key"] for p in physical}
        candidates = [item for unit_key in unit_keys for item in units_by_key.get(unit_key, ())]
        physical_units[key] = [unit for _, unit in sorted(candidates, key=lambda item: item[0])]
    result: list[dict[str, Any]] = []
    for table, size in TABLE_SIZES.items():
        section = db.sections.get(table)
        if section is None:
            continue
        for index, raw in enumerate(records(section)):
            if len(raw) != size:
                raise ValueError(f"{source}: table{table} expected{size}, got{len(raw)}")
            u16 = lambda off: struct.unpack_from("<H", raw, off)[0]
            u32 = lambda off: struct.unpack_from("<I", raw, off)[0]
            row: dict[str, Any] = {"source": source, "table": table, "record": index,
                                   "raw": raw.hex()}
            if table in (61, 156, 90, 151):
                row.update(kind="data_id", did=u16(2), fixed_length=u16(4),
                           support_mode=raw[6], exception_handler_id=u16(0),
                           exception_handler_flag=raw[7])
            elif table in (63, 80, 89):
                row.update(kind="support_condition", key=u16(0), variable_id=u16(2),
                           exception_handler_id=u16(4), bit_start=u16(6), bit_end=u16(8))
                if table == 63:
                    row.update(comparison_value=u16(10), exception_handler_flag=raw[12],
                               condition_type=raw[13], comparison_mode=raw[14],
                               unassigned_tail=raw[15])
                else:
                    row.update(exception_handler_flag=raw[10], condition_type=raw[11])
                if resolve_variable is not None:
                    variable = resolve_variable(row["variable_id"])
                    row["variable_bytes"] = variable.hex()
                    if row["condition_type"] == 7 and len(variable) == 2:
                        row["referenced_did"] = int.from_bytes(variable, "big")
            elif table == 66:
                row.update(kind="dtc_status", key=u32(0), status_mask=raw[8],
                           comparison_value=raw[9], exception_handler_id=u16(6),
                           exception_handler_flag=raw[10],
                           unassigned_fields={"word4": u16(4), "byte11": raw[11]})
            elif table == 81:
                row.update(kind="dynamic_did", did=u16(0), maximum_payload_length=u16(2),
                           exception_handler_id=u16(4), exception_handler_flag=raw[6],
                           unassigned_tail=raw[7])
            elif table == 86:
                # KgpDataCtrl100CF333 selects byte3; PCS Operation10001000
                # patches byte2 into command frame0x11 at request offset3.
                row.update(kind="pcs_operation_ffd_pid", retrieval_group=raw[3],
                           pid=raw[2], unassigned_word0=u16(0),
                           request={"function_selector": 0x11, "pid_byte_offset": 3})
            elif table in (91, 152):
                row.update(kind="rob_special_signal", key=u16(0), signal_key=u16(2),
                           exception_handler_id=u16(4), exception_handler_flag=raw[8],
                           unassigned_fields={"word6": u16(6), "tail9": raw[9:].hex()})
            elif table == 87:
                row.update(kind="behavior_code",
                           signature=raw[:12].decode("utf-16le").split("\x00", 1)[0],
                           name_string_index=u32(12), comment_string_index=u32(16),
                           behavior_code=u16(20))
                row["name"] = strings.get_string(row["name_string_index"])
                row["comment"] = strings.get_string(row["comment_string_index"])
                row["unassigned_tail"] = raw[22:].hex()
            elif table in (62, 157):
                row.update(kind="monitor", name_string_index=u32(0x28),
                           monitor_key=u16(0x34), flags=u32(0x30),
                           live_support_condition_key=u16(0x36),
                           ffd_support_condition_key=u16(0x38),
                           physical_data_key=u16(0x3A), bit_start=u16(0x3C),
                           bit_end=u16(0x3E), sort_key=u16(0x40),
                           pattern_display_key=u16(0x42),
                           primary_did=u16(0x46), snapshot_did=u16(0x48),
                           extraction_mode=raw[0x4A], visibility_override=raw[0x4B],
                           graph_max=struct.unpack_from("<i", raw, 0x14)[0],
                           graph_min=struct.unpack_from("<i", raw, 0x18)[0],
                           data_range_max=struct.unpack_from("<i", raw, 0x1C)[0],
                           data_range_min=struct.unpack_from("<i", raw, 0x20)[0],
                           physical_max=struct.unpack_from("<d", raw, 0)[0],
                           physical_min=struct.unpack_from("<d", raw, 8)[0])
                row["name"] = strings.get_string(row["name_string_index"])
                row["unassigned_ranges"] = {"10_27": raw[16:40].hex(),
                                            "2c_2f": raw[44:48].hex(),
                                            "44_45": raw[68:70].hex(),
                                            "4c_4f": raw[76:80].hex()}
            elif table in (88, 153):
                row.update(kind="rob_signal", name_string_index=u32(0x20),
                           record_key=u16(0x2C), support_condition_key=u16(0x2E),
                           physical_data_key=u16(0x30), bit_start=u16(0x32),
                           bit_end=u16(0x34), sort_key=u16(0x36),
                           pattern_display_key=u16(0x38), exception_handler_id=u16(0x3A),
                           did=u16(0x3C), extraction_mode=raw[0x3E],
                           presentation_mode=raw[0x3F], exception_handler_flag=raw[0x42])
                row["name"] = strings.get_string(row["name_string_index"])
                row["unassigned_ranges"] = {"0_1f": raw[:32].hex(),
                                            "24_2b": raw[36:44].hex(),
                                            "40_41": raw[64:66].hex(),
                                            "43_47": raw[67:72].hex()}
            if "physical_data_key" in row:
                key = row["physical_data_key"]
                row["physical_records"] = physical_by_key.get(key, [])
                row["unit_records"] = physical_units.get(key, [])
                row["pattern_records"] = patterns_by_key.get(row["pattern_display_key"], [])
            result.append(row)
    return result
