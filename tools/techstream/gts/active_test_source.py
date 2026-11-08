"""Unfiltered type68/71/77 source projections, independent of runtime plans.

Field offsets are shared with active_tests selected-row decoders and bundle
_simple_utility_rows. Duplicate IDs remain distinct source records.
"""
from __future__ import annotations
import struct
from tools.techstream.ddb_semantics import records

DIRECT = {
    "name_string_index": (12,"I"), "active_test_id": (32,"H"),
    "physical_data_key": (36,"H"), "active_test_pattern_key": (38,"H"),
    "bit_start": (40,"H"), "bit_end": (42,"H"), "sort_key": (44,"H"),
    "exception_id": (46,"H"), "panel_key_0": (48,"H"), "panel_key_1": (50,"H"),
    "initial_read_did": (52,"H"), "direct_monitor_key": (54,"H"),
    "initial_read_mode": (57,"B"), "pattern": (58,"B"), "exception_flag": (59,"B"),
    "panel_check_mode": (60,"B"), "monitor_link_mode": (61,"B"),
}
ROUTINE = {
    "name_string_index": (8,"I"), "routine_id": (28,"H"), "active_test_id": (30,"H"),
    "active_test_pattern_key": (36,"H"), "routine_command_variable": (40,"H"),
    "routine_stop_command_variable": (42,"H"), "output_mask_value_variable": (44,"H"),
    "output_mask_button_variable": (46,"H"), "routine_status_key": (48,"H"),
    "pattern_display_variable_key": (60,"H"), "sort_key": (64,"H"),
}
UTILITY = {
    "name_string_index": (0,"I"), "timer_ms": (4,"I"), "start_help_id": (12,"I"),
    "routine_id": (20,"H"), "utility_id": (22,"H"), "sort_key": (24,"H"),
    "routine_command_variable": (26,"H"), "routine_stop_command_variable": (28,"H"),
    "check_interval_ms": (30,"H"), "p5_pattern_display": (32,"H"),
    "p6_pattern_display": (34,"H"), "p5_pattern_description": (36,"H"),
    "p6_pattern_description": (38,"H"), "status_1": (40,"H"), "status_2": (42,"H"),
    "p6_status_5": (44,"H"), "p6_status_6": (46,"H"),
}

def active_test_source_catalog(db, strings, source):
    result = []
    for table, size, fields in ((68,64,DIRECT),(71,72,ROUTINE),(77,52,UTILITY)):
        section = db.sections.get(table)
        if section is None:
            continue
        for index, raw in enumerate(records(section)):
            if len(raw) != size:
                raise ValueError(f"{source}: table{table} expected{size}, got{len(raw)}")
            row = {"source":source,"table":table,"record":index,"raw":raw.hex()}
            used = set()
            for name,(offset,fmt) in fields.items():
                row[name] = struct.unpack_from("<"+fmt,raw,offset)[0]
                used.update(range(offset,offset+struct.calcsize(fmt)))
            row["name"] = strings.get_string(row["name_string_index"])
            row["unassigned_bytes"] = {str(i):raw[i] for i in range(size) if i not in used}
            result.append(row)
    section = db.sections.get(33)
    if section is not None:
        for index, raw in enumerate(records(section)):
            if len(raw) != 12:
                raise ValueError(f"{source}: table33 expected12, got{len(raw)}")
            result.append({"source":source,"table":33,"record":index,"raw":raw.hex(),
                           "group_id":struct.unpack_from("<H",raw,0)[0],
                           "member_active_test_id":struct.unpack_from("<H",raw,2)[0],
                           "input_slot":struct.unpack_from("<H",raw,6)[0],
                           "unassigned_words":{str(i):struct.unpack_from("<H",raw,i)[0]
                                               for i in (4,8,10)}})
    return result
