"""Variable-drive Active Tests (41) and communication ECU data (38).

Kgp: table41 stride1006f3b0, keys1006f190/1006f2a0,
exception1006f3f0/1006f430, strings1006e710. Table38 stride1007bab0,
key1007b9b0, exception1007baf0/1007bb30.
Consumers: GetMultiActInitPsaVrbl_DT10001390/10001cc0,
DM_ActVariable_DT1000ef50, CommandCommon1001a140/1001a440/1006d210.
These are descriptive records, never executable vehicle commands.
"""
from __future__ import annotations
import struct
from typing import Any
from tools.techstream.ddb_semantics import records, _physical_info
from tools.techstream.gts.legacy_active import legacy_active_patterns

def _u16(raw, off): return struct.unpack_from("<H", raw, off)[0]
def _u32(raw, off): return struct.unpack_from("<I", raw, off)[0]

def _rows(db, table, size):
    section = db.sections.get(table)
    if section is None:
        return
    if section.decoded_record_size != size:
        raise ValueError(f"Variable drive table {table}: expected {size}, got {section.decoded_record_size}")
    yield from enumerate(records(section))

def variable_drive_catalog(db: Any, strings: Any, source: str) -> dict[str, Any]:
    communication = []
    for index, raw in _rows(db, 38, 12):
        communication.append({
            "source":source, "table":38, "record":index, "raw":raw,
            "ecu_item_key":_u16(raw,0), "bit_start":_u16(raw,2), "bit_end":_u16(raw,4),
            "exception_id":_u16(raw,6), "pid":raw[8], "exception_flag":raw[9],
            "communication_frame_key":0x6b,
            "support_semantics":"PID availability followed by support-bit range check",
            "response_semantics":"ConvertPid then extract the inclusive bit range",
        })
    patterns = legacy_active_patterns(db, source)
    by_key = {}
    for row in patterns:
        by_key.setdefault(row["pattern_key"],[]).append(row)
    physical = {}
    if 13 in db.sections:
        for raw in records(db.sections[13]):
            physical.setdefault(_u16(raw,12),raw)
    active = []
    for index, raw in _rows(db,41,92):
        matches = by_key.get(_u16(raw,64),[])
        pattern = matches[0] if matches else None
        info = _physical_info(db, strings, physical_data_key=_u16(raw,62),
            bit_start=_u16(raw,66),bit_end=_u16(raw,68),
            pattern_display_key=pattern["pattern_display_key"] if pattern else 0)
        if info is not None:
            info.pop("signed",None)
            info["sign_mode"] = physical[_u16(raw,62)][20]
        active.append({
            "source":source,"table":41,"record":index,"raw":raw,
            "id":_u16(raw,56),"request_identifier":raw[80],
            "name_string_index":_u32(raw,32),"name":strings.get_string(_u32(raw,32)),
            "initial_value":_u32(raw,20),"data_max":_u32(raw,24),"data_min":_u32(raw,28),
            "comment_id":_u32(raw,36),"help_id":_u32(raw,40),"info_id":_u32(raw,44),
            "caution_id":_u32(raw,48),"prohibition_id":_u32(raw,52),
            "initial_value_monitor_key":_u16(raw,58),"did_support_key":_u16(raw,60),
            "physical_data_key":_u16(raw,62),"active_test_pattern_key":_u16(raw,64),
            "bit_start":_u16(raw,66),"bit_end":_u16(raw,68),
            "exception_id":_u16(raw,72),"communication_frame_key":_u16(raw,74),
            "data_max_monitor_key":_u16(raw,76),"data_min_monitor_key":_u16(raw,78),
            "support_mode":raw[81],"initial_value_mode":raw[82],"presentation_pattern":raw[83],
            "exception_flag":raw[85],"request_constant":raw[86],"data_limits_mode":raw[87],
            "request_constant_16":raw[88],"pattern":pattern,"pattern_match_count":len(matches),
            "signal_info":info,
            "support_semantics":{0:"PID length and optional table9 DID-bit predicate",
                                 1:"supported",2:"not_supported"}.get(raw[81],"unsupported_mode"),
            "request_encoding":{
                "program_source":"communication-frame send bytes, not packed nibbles",
                "communication_frame_key":_u16(raw,74),
                "service_by_generation_low5":{"1":0x6d,"2":0x6d,"7":0x3d,"default":0x30},
                "generation_7":"identifier-only; program bypassed",
                "maximum_program_length_exclusive":62,
                "operations":{"0":"end","1":"zero","2":"value_low","3":"value_shift_left_7_minus_bit_end_mod8",
                    "4":"request_constant","5":"request_constant","6":"request_constant_plus_value",
                    "7":"pattern_timeout_or_6","8":"command_parameter_28_low","10":"value_high",
                    "11":"unsupported_error","12":"unsupported_error","13":"unsupported_error",
                    "16":"request_constant_16","17":"pattern_timeout_literal"},
                "unlisted_opcode":"zero",
            },
            "execution":"metadata_only",
        })
    # Kgp55:100bf950/100bfa50/100bfa90/100bfad0; consumer
    # CommandCommon10068ff0 appends external frame send bytes to PID request.
    additions = []
    for index, raw in _rows(db,55,8):
        additions.append({
            "source":source,"table":55,"record":index,"raw":raw,
            "communication_frame_key":_u16(raw,0),"exception_id":_u16(raw,2),
            "pid":raw[4],"exception_flag":raw[5],
            "semantics":"Append the referenced communication-frame send bytes to the PID length request",
        })
    # Kgp60:1006c220/1006c330/1006c370/1006c3b0; DataMonitorPSA
    # 10005b20 and10006250 override service byte using table60+2.
    modes = []
    for index, raw in _rows(db,60,8):
        modes.append({
            "source":source,"table":60,"record":index,"raw":raw,
            "active_test_id":_u16(raw,0),"service_override":raw[2],
            "exception_id":_u16(raw,4),"exception_flag":raw[6],
            "semantics":"Override request service byte for the matching active-test ID",
        })
    return {"active_tests":active,"communication_data":communication,
        "pid_addition_frames":additions,"active_test_communication_modes":modes,
        "runtime_boundary":"Variable drive request program is in the external communication-frame DB; live support and initial/limit reads are not performed."}
