"""Shared native DDR class families selected by the exact GTS factory map.

KgpDataCtrl: monitor Find100a4130/stride100a4230/sort100a3e80,
trigger Find100a4b00/100a4c00, address Find1009ed00/1009ee00,
header Find100a3210, case Find100a1410, plus exception accessors.
CommandCommon: SetDdrFrzFrmDatParam1003b8d0, GetHeaderDdrIdList10039cb0,
GetDdrHeaderInfoDID10039800, CheckDdrCaseInfoDIDSupport10034580,
SetDdrTriggerDependData1003d540, SetDdrTrigerName1003d140.
GetDDRInfo_DT: native address/monitor reads10005770 and10003b00.
"""
from __future__ import annotations
import struct
from typing import Any

from tools.techstream.ddb_semantics import records, _physical_info
from tools.techstream.parse_ddb import ECU_TABLE_CLASS_NAMES
from tools.techstream.gts.p6_ddr import ddr_invalid_condition

MONITOR_TABLES = (50, 82, 92, 96, 100, 104, 110, 119, 123, 129, 138, 147)
HEADER_TABLES = (108, 127, 136, 145)


def _u16(raw, offset):
    return struct.unpack_from("<H", raw, offset)[0]


def _u32(raw, offset):
    return struct.unpack_from("<I", raw, offset)[0]


def _rows(db, table, size, expected_class):
    assert ECU_TABLE_CLASS_NAMES[table] == expected_class
    section = db.sections.get(table)
    if section is None:
        return
    if section.decoded_record_size != size:
        raise ValueError(f"native DDR table {table} ({expected_class}): expected {size}, got {section.decoded_record_size}")
    yield from enumerate(records(section))


def native_ddr_catalog(db: Any, strings: Any, source: str) -> dict[str, Any]:
    result = {key: [] for key in ("monitors", "triggers", "addresses", "invalid_conditions", "header_data_ids", "case_data_ids")}
    physical_rows = {}
    if 13 in db.sections:
        for raw in records(db.sections[13]):
            physical_rows.setdefault(_u16(raw, 12), raw)

    def identity(table, ordinal, raw, family):
        return {"source": source, "table": table, "record": ordinal, "raw": raw,
                "family": f"native-ddr-{family}", "record_class": ECU_TABLE_CLASS_NAMES[table]}

    for base in MONITOR_TABLES:
        for ordinal, raw in _rows(db, base, 48, "CDbDDRMonitorTable"):
            key, phy, start, end, history_start, history_end, order, pattern, exception = struct.unpack_from("<9H", raw, 24)
            info = _physical_info(db, strings, physical_data_key=phy, bit_start=start, bit_end=end, pattern_display_key=pattern)
            if info is not None:
                info.pop("signed", None)
                info["sign_mode"] = physical_rows[phy][20]
            result["monitors"].append({
                **identity(base, ordinal, raw, base), "monitor_key": key,
                "name_string_index": _u32(raw, 20), "name": strings.get_string(_u32(raw, 20)),
                "physical_data_key": phy, "bit_start": start, "bit_end": end,
                "history_bit_start": history_start, "history_bit_end": history_end,
                "sort_key": order, "pattern_display_key": pattern,
                "exception_id": exception, "exception_flag": raw[45],
                "presentation_mode": raw[44], "signal_info": info,
                "graph_max": struct.unpack_from("<i", raw, 0)[0],
                "graph_min": struct.unpack_from("<i", raw, 4)[0],
                "data_max": _u32(raw, 12), "data_min": _u32(raw, 16),
            })
        for ordinal, raw in _rows(db, base+1, 36, "CDbDDRTriggerTable"):
            result["triggers"].append({
                **identity(base+1, ordinal, raw, base),
                "trigger_id": raw[30], "trigger_variant": raw[31],
                "name_string_index": _u32(raw, 8), "name": strings.get_string(_u32(raw, 8)),
                "memo_string_index": _u32(raw, 12), "memo": strings.get_string(_u32(raw, 12)),
                "dependent_data_0": _u32(raw, 0), "dependent_data_1": _u32(raw, 4),
                "header_parameters": list(struct.unpack_from("<6H", raw, 16)),
                "exception_id": _u16(raw, 28), "exception_flag": raw[32],
            })
        for ordinal, raw in _rows(db, base+2, 16, "CDbDDRAddressTable"):
            result["addresses"].append({
                **identity(base+2, ordinal, raw, base),
                "address": _u32(raw, 0), "monitor_key": _u16(raw, 4),
                "record_length": _u16(raw, 6), "exception_id": _u16(raw, 8),
                "trigger_id": raw[10], "section_kind": raw[11], "exception_flag": raw[12],
                "header_member": raw[11] == 1,
            })
        # All aliases have the same factory class, not merely similar bytes.
        for ordinal, raw in _rows(db, base+3, 16, "CDbDDRInvalidConditionTable"):
            result["invalid_conditions"].append({
                **ddr_invalid_condition(raw, source=source, table=base+3, record=ordinal),
                "family": f"native-ddr-{base}", "record_class": "CDbDDRInvalidConditionTable",
            })

    for table in HEADER_TABLES:
        family = table+2
        for ordinal, raw in _rows(db, table, 8, "CDbDDRHeaderInfoDataIdTable"):
            result["header_data_ids"].append({
                **identity(table, ordinal, raw, family), "header_did": _u16(raw, 0),
                "header_parameter": _u16(raw, 2),
                "exception_id": _u16(raw, 4), "exception_flag": raw[6],
            })
        for ordinal, raw in _rows(db, table+1, 12, "CDbDDRCaseInfoDataIdTable"):
            result["case_data_ids"].append({
                **identity(table+1, ordinal, raw, family), "header_did": _u16(raw, 0),
                "case_did": _u16(raw, 2), "case_parameter": _u16(raw, 4),
                "exception_id": _u16(raw, 6), "case_selector": raw[8], "exception_flag": raw[10],
            })
    # References are family-scoped: equal keys across aliases must never merge.
    monitor_refs = {}
    for row in result["monitors"]:
        monitor_refs.setdefault((row["family"], row["monitor_key"]), []).append({"table": row["table"], "record": row["record"]})
    for row in result["addresses"]:
        row["monitor_records"] = monitor_refs.get((row["family"], row["monitor_key"]), [])
    conditions = {}
    for row in result["invalid_conditions"]:
        conditions.setdefault((row["family"], row["signal_key"]), []).append(row)
    for row in result["monitors"]:
        row["invalid_condition_records"] = [{"table": condition["table"], "record": condition["record"]}
            for condition in sorted(conditions.get((row["family"], row["monitor_key"]), []),
                                    key=lambda condition: condition["condition_order"])]
    result["runtime_boundary"] = "All factory-equivalent static rows retained. Native exception selection and acquired recorder data remain necessary; table presence alone is not vehicle support."
    return result
