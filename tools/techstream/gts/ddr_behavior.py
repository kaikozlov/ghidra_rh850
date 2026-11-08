"""ADS DDR P5 tables133–135, pinned to native Kgp/GetADSDDRInfoP5 consumers.

Kgp keys:133+20/u16 with secondarybytes28/29 (VA1009fde0);
134+2c/u16 (100a0f10);135+8/u16 (100a04c0).
GetADSDDRInfoP5_DT: field extraction10002720, support10002ae0,
metadata100066d0/100089e0, invalid comparison100051b0.
"""
from __future__ import annotations
import struct
from typing import Any
from tools.techstream.ddb_semantics import records, _physical_info


def _u16(raw, off): return struct.unpack_from("<H", raw, off)[0]
def _u32(raw, off): return struct.unpack_from("<I", raw, off)[0]


def _rows(db, table, size):
    section = db.sections.get(table)
    if section is None:
        return
    if section.decoded_record_size != size:
        raise ValueError(f"DDR behavior table{table}: expected {size}, got {section.decoded_record_size}")
    yield from enumerate(records(section))


def _identifier_fields(raw: bytes) -> dict[str, str]:
    """Preserve the fixed-width original identifier, never infer it from a key."""
    field = raw[:12]
    try:
        decoded = field.decode("utf-16-le")
    except UnicodeDecodeError:
        return {"uninterpreted_identifier_bytes": field.hex()}
    identifier = decoded.rstrip("\u0000")
    if "\u0000" in identifier:
        return {"uninterpreted_identifier_bytes": field.hex()}
    return {"identifier": identifier}


def ddr_behavior_catalog(db: Any, strings: Any, source: str) -> dict[str, Any]:
    def identity(table, index, raw):
        return {"source":source, "table":table, "record":index, "raw":raw, "family":"ads-ddr-p5"}

    codes = []
    for index, raw in _rows(db,133,44):
        codes.append({
            **identity(133,index,raw), **_identifier_fields(raw), "behavior_key":_u16(raw,32),
            "name_string_index":_u32(raw,12), "name":strings.get_string(_u32(raw,12)),
            "trigger_memo_string_index":_u32(raw,16), "trigger_memo":strings.get_string(_u32(raw,16)),
            "additional_string_index":_u32(raw,28), "additional_text":strings.get_string(_u32(raw,28)),
            "dependent_data_0":_u32(raw,20), "dependent_data_1":_u32(raw,24),
            "trigger_selector_0":raw[40], "trigger_selector_1":raw[41],
            "exception_id":_u16(raw,34), "exception_flag":raw[43],
            "uninterpreted_bytes": {"36_39": raw[36:40].hex(), "42": raw[42:43].hex()},
        })
    invalid = []
    by_signal = {}
    for index, raw in _rows(db,135,24):
        key = _u16(raw,8)
        invalid.append({
            **identity(135,index,raw), "signal_key":key, "referenced_signal_key":_u16(raw,10),
            "comparison_bits64":struct.unpack_from("<Q",raw,0)[0], "condition_order":_u16(raw,12),
            "exception_id":_u16(raw,14), "exception_flag":raw[18],
            "combination_mode":raw[16], "comparison_mode":raw[17],
            "comparison":{1:"equal_bits64",2:"not_equal_bits64"}.get(raw[17],"unsupported"),
            "uninterpreted_bytes": {"19_23": raw[19:24].hex()},
        })
        by_signal.setdefault(key,[]).append(index)
    for indices in by_signal.values():
        indices.sort(key=lambda index:invalid[index]["condition_order"])
    physical = {}
    if 13 in db.sections:
        for raw in records(db.sections[13]):
            physical.setdefault(_u16(raw,12),raw)
    signals = []
    for index, raw in _rows(db,134,72):
        key, condition, phy, start, end, order, pattern, exception, did = struct.unpack_from("<9H",raw,44)
        info = _physical_info(db,strings,physical_data_key=phy,bit_start=start,bit_end=end,pattern_display_key=pattern)
        if info is not None:
            info.pop("signed",None)
            info["sign_mode"] = physical[phy][20]
        signals.append({
            **identity(134,index,raw), "signal_key":key, "support_condition_key":condition,
            "physical_data_key":phy, "bit_start":start, "bit_end":end, "sort_key":order,
            "pattern_display_key":pattern, "exception_id":exception, "exception_flag":raw[66],
            "did":did, "name_string_index":_u32(raw,32), "name":strings.get_string(_u32(raw,32)),
            "signal_info":info, "presentation_mode":raw[62], "signal_role":raw[63],
            "extraction_mode":raw[67], "live_list_member":raw[67]==1,
            "data_max":struct.unpack_from("<d",raw,0)[0], "data_min":struct.unpack_from("<d",raw,8)[0],
            "graph_max":struct.unpack_from("<i",raw,20)[0], "graph_min":struct.unpack_from("<i",raw,24)[0],
            "invalid_condition_records":by_signal.get(key,[]),
            "uninterpreted_bytes": {
                "16_19": raw[16:20].hex(), "28_31": raw[28:32].hex(),
                "36_43": raw[36:44].hex(), "64_65": raw[64:66].hex(),
                "68_71": raw[68:72].hex(),
            },
        })
    return {"codes":codes,"signals":signals,"invalid_conditions":invalid,
            "runtime_boundary":"Physical metadata and recorder geometry decoded; DID support, exception context and captured DDR data determine runtime values."}
