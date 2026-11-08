"""Phase-4 Record-of-Behavior catalogs and scalar decoding.

Pinned to GTS+ 2026 GetRoBP4_DT.dll: 100026E0 selects supported BDIDs,
10001D90 extracts inclusive MSB0 fields, and 10002B80 resolves physical,
unit and display metadata. KgpDataCtrl 10072110 fixes table45/59 stride96;
1006FA80/100CE080 fix table43/44/57/58 stride8. Table46 is shared by modes.
"""
from __future__ import annotations

import struct
from typing import Any

from tools.techstream.ddb_semantics import records
from tools.techstream.native_conversion import convert_scalar


def _u16(raw: bytes, offset: int) -> int:
    return struct.unpack_from("<H", raw, offset)[0]


def _u32(raw: bytes, offset: int) -> int:
    return struct.unpack_from("<I", raw, offset)[0]


def _rows(db: Any, table: int, size: int) -> list[bytes]:
    section = db.sections.get(table)
    if section is None:
        return []
    if section.decoded_record_size != size and section.header.record_count:
        raise ValueError(f"legacy ROB table {table}: expected {size}-byte records, got {section.decoded_record_size}")
    return list(records(section))


def decode_rob_scalar(payload: bytes, signal: dict[str, Any], *, physical_variant: int = 0) -> int:
    """Decode a selector-BD response data payload, after its echoed request bytes."""
    start, end = signal["bit_start"], signal["bit_end"]
    if start < 0 or end < start or end >= len(payload) * 8 or end - start >= 32:
        raise ValueError("legacy ROB scalar range is outside the supplied payload or u32 width")
    value = (int.from_bytes(payload, "big") >> (len(payload) * 8 - end - 1)) & ((1 << (end - start + 1)) - 1)
    info = signal["physical_variants"][physical_variant]
    return convert_scalar(value, end - start + 1, info["mul"], info["div"], info["offset"], info["sign_mode"])


def legacy_rob_catalog(db: Any, strings: Any, source: str) -> dict[str, Any]:
    """Decode both OEM recorder modes without collapsing their namespaces."""
    physical = _rows(db, 13, 24)
    units = _rows(db, 15, 12)
    # Current GTS+ display rows have a 24-byte native record.
    patterns = _rows(db, 14, 24)
    checks = []
    for index, raw in enumerate(_rows(db, 46, 12)):
        checks.append({"source": source, "table": 46, "record": index, "raw": raw.hex(),
                       "role": _u16(raw, 0), "signal_key": _u16(raw, 2),
                       "exception_handler_id": _u16(raw, 4), "exception_handler_flag": raw[8]})
    families = []
    for mode, code_table, bdid_table, support_table, signal_table in ((1,42,43,44,45),(2,56,57,58,59)):
        if not any(t in db.sections for t in (code_table, bdid_table, support_table, signal_table)):
            continue
        support = [{"source": source, "table": support_table, "record": index, "raw": raw.hex(),
                    "group": raw[4], "query_mode": raw[5],
                    "requires_prior_support": raw[5] == 2,
                    "exception_handler_id": _u16(raw, 0), "exception_handler_flag": raw[6]}
                   for index, raw in enumerate(_rows(db, support_table, 8))]
        identifiers = [{"source": source, "table": bdid_table, "record": index, "raw": raw.hex(),
                        "bdid": raw[2], "exception_handler_id": _u16(raw, 0),
                        "exception_handler_flag": raw[6]}
                       for index, raw in enumerate(_rows(db, bdid_table, 8))]
        codes = []
        for index, raw in enumerate(_rows(db, code_table, 28)):
            codes.append({"source": source, "table": code_table, "record": index, "raw": raw.hex(),
                          "behavior_code": _u16(raw,20),
                          "signature": raw[:12].decode("utf-16le").split("\0",1)[0],
                          "name": strings.get_string(_u32(raw,12)),
                          "comment": strings.get_string(_u32(raw,16)),
                          "enabled": raw[26],
                          "exception_handler_id": _u16(raw,22), "exception_handler_flag": raw[27]})
        signals = []
        for index, raw in enumerate(_rows(db, signal_table, 96)):
            key, phy_key, pattern_key = _u16(raw,64), _u16(raw,68), _u16(raw,78)
            variants = []
            for phy_index, phy in enumerate(physical):
                if _u16(phy,12) != phy_key:
                    continue
                unit_key = _u16(phy,14)
                unit_rows = [{"record": unit_index, "name_string_index": _u32(unit,0),
                              "name": strings.get_string(_u32(unit,0)), "genre_id": _u16(unit,6)}
                             for unit_index, unit in enumerate(units) if _u16(unit,4) == unit_key]
                variants.append({"table": 13, "record": phy_index, "physical_data_key": phy_key,
                                 "mul": struct.unpack_from("<i",phy,0)[0],
                                 "div": struct.unpack_from("<i",phy,4)[0],
                                 "offset": struct.unpack_from("<i",phy,8)[0],
                                 "sign_mode": phy[20], "decimal_point_count": phy[21],
                                 "unit_key": unit_key, "units": unit_rows})
            displays = [{"table": 14, "record": p_index, "value": struct.unpack_from("<i",p,4)[0],
                         "name_string_index": _u32(p,0), "name": strings.get_string(_u32(p,0))}
                        for p_index,p in enumerate(patterns) if _u16(p,12) == pattern_key]
            signals.append({"source": source, "table": signal_table, "record": index, "raw": raw.hex(),
                            "signal_key": key, "name_string_index": _u32(raw,56),
                            "name": strings.get_string(_u32(raw,56)),
                            "short_name": raw[16:40].decode("utf-16le").split("\0",1)[0],
                            "bdid": raw[87], "bit_start": _u16(raw,70), "bit_end": _u16(raw,72),
                            "sort_key": _u16(raw,76), "presentation_mode": raw[84],
                            "support_mode": raw[85],
                            "support_rule": {0:"query_supported_bdid",1:"unconditional",2:"excluded"}.get(raw[85], "native_error"),
                            "physical_data_key": phy_key, "physical_variants": variants,
                            "pattern_display_key": pattern_key, "pattern_display": displays,
                            "data_max": struct.unpack_from("<d",raw,0)[0],
                            "data_min": struct.unpack_from("<d",raw,8)[0],
                            "graph_max": struct.unpack_from("<i",raw,40)[0],
                            "graph_min": struct.unpack_from("<i",raw,44)[0],
                            "exception_handler_id": _u16(raw,80), "exception_handler_flag": raw[90],
                            "decoder": "legacy-rob-msb0-u32-v1"})
        families.append({"mode": mode, "behavior_codes": codes, "identifiers": identifiers,
                         "support_queries": support, "signals": signals,
                         "transport": {"support_selector":188,"read_selector":189,
                                       "request_behavior_code_offsets":[2,3],
                                       "request_frame_offset":4,"request_bdid_offset":5,
                                       "payload_offset":"send_frame_length"}})
    return {"families": families, "signal_checks": checks}
