"""P5/P6 Active-Test planning: type-68/71 selected rows, direct/routine executor plans, type-33 multi-control groups, monitor partitions, role-0x70 signal info."""

from __future__ import annotations

import struct
from pathlib import Path
from typing import Any

from tools.techstream.gts.ddb import _monitor_rows
from tools.techstream.ddb_semantics import native_context
from tools.techstream.gts.query import _raw_catalog_source, native_ecu_catalog_category
from tools.techstream.gts.master import _master_frame_rows, _master_variable
from tools.techstream.parse_ddb import ECU_TABLE_CLASS_NAMES, DDBParser, StringDataBase


def _active_test_list_category_plan(parser: DDBParser, category: dict[str, Any], db_root: Path) -> dict[str, Any]:
    mode = int(category["generation"]) & 0xE0
    db_path = Path(category.get("catalog_database_path") or db_root / str(category["database"]))
    db = parser.parse_ecu_db(db_path)
    direct = db.sections.get(68)
    routine = db.sections.get(71)
    multi = db.sections.get(33)
    if direct is not None and direct.decoded_record_size != 64:
        raise ValueError(f"{db_path.name}: type-68 record size {direct.decoded_record_size}, expected 64")
    if routine is not None and routine.decoded_record_size != 72:
        raise ValueError(f"{db_path.name}: type-71 record size {routine.decoded_record_size}, expected 72")
    direct_count = 0 if direct is None else direct.header.record_count
    routine_count = 0 if routine is None else routine.header.record_count
    return {
        "catalog_context": {**_raw_catalog_source(db_path), "category": category},
        "generation": int(category["generation"]),
        "generation_mode": f"0x{mode:X}",
        "direct_table": 68,
        "direct_table_class": ECU_TABLE_CLASS_NAMES[68],
        "direct_candidate_count": direct_count,
        "routine_table": 71,
        "routine_table_class": ECU_TABLE_CLASS_NAMES[71],
        "routine_candidate_count": routine_count,
        "multi_did_table_present": multi is not None,
        "multi_did_count": 0 if multi is None else multi.header.record_count,
        "support_builders": (
            ["CreateEnableDataIdListForSubaruCheckDID", "CreateEnableRIdListforSUBARU"]
            if mode == 0x20
            else ["CreateEnableDataIdList", "CreateEnableRIdList"]
        ),
        "direct_support_helper": (
            "CheckSupportDidForSUBARU" if mode == 0x20 else "CheckSupportDid"
        ),
        "routine_support_helper": (
            "CheckSupportRidForSUBARU" if mode == 0x20 else "CheckSupportRid"
        ),
        "runtime_support_required": direct_count > 0 or routine_count > 0,
        "runtime_boundary": (
            "candidate counts are static; direct tests require DID support evaluation and routine tests require "
            "RID support evaluation before Techstream's final Active Test list is known"
        ),
    }


def _direct_active_test_selected_row(
    parser: DDBParser,
    category: dict[str, Any],
    db_root: Path,
    active_test_id: int,
    strings: StringDataBase | None = None,
) -> tuple[Any, Path, dict[str, Any]]:
    db_path = Path(category.get("catalog_database_path") or db_root / str(category["database"]))
    db = parser.parse_ecu_db(db_path)
    section = db.sections.get(68)
    if section is None:
        raise ValueError(f"{db_path.name}: selected direct Active Test table 68 is absent")
    if section.decoded_record_size != 64:
        raise ValueError(f"{db_path.name}: type-68 record size {section.decoded_record_size}, expected 64")
    matches = []
    for index in range(section.header.record_count):
        raw = section.decoded_data[index * 64 : (index + 1) * 64]
        if struct.unpack_from("<H", raw, 0x20)[0] == active_test_id:
            matches.append((index, raw))
    if len(matches) != 1:
        raise ValueError(
            f"{db_path.name}: direct Active Test ID 0x{active_test_id:X} resolved {len(matches)} type-68 rows"
        )
    index, raw = matches[0]
    name_index = struct.unpack_from("<I", raw, 0x0C)[0]
    selected = {
        "catalog_context": {**_raw_catalog_source(db_path), "category": category},
        "record": index,
        "active_test_id": active_test_id,
        "active_test_id_hex": f"0x{active_test_id:X}",
        "name_string_index": name_index,
        "name": (strings.get_string(name_index) or "") if strings is not None else None,
        "physical_data_key": struct.unpack_from("<H", raw, 0x24)[0],
        "active_test_pattern_key": struct.unpack_from("<H", raw, 0x26)[0],
        "bit_start": struct.unpack_from("<H", raw, 0x28)[0],
        "bit_end": struct.unpack_from("<H", raw, 0x2A)[0],
        "sort_key": struct.unpack_from("<H", raw, 0x2C)[0],
        "exception_id": struct.unpack_from("<H", raw, 0x2E)[0],
        "panel_key_0": struct.unpack_from("<H", raw, 0x30)[0],
        "panel_key_1": struct.unpack_from("<H", raw, 0x32)[0],
        "initial_read_did": struct.unpack_from("<H", raw, 0x34)[0],
        "direct_monitor_key": struct.unpack_from("<H", raw, 0x36)[0],
        "initial_read_mode": raw[0x39],
        "pattern": raw[0x3A],
        "exception_flag": raw[0x3B],
        "panel_check_mode": raw[0x3C],
        "monitor_link_mode": raw[0x3D],
        "raw": raw.hex(),
    }
    return db, db_path, selected


def _routine_active_test_selected_row(
    parser: DDBParser,
    category: dict[str, Any],
    db_root: Path,
    active_test_id: int,
    strings: StringDataBase | None = None,
) -> tuple[Any, Path, dict[str, Any]]:
    """Resolve one current 72-byte type-71 P5 routine Active-Test row."""
    db_path = Path(category.get("catalog_database_path") or db_root / str(category["database"]))
    db = parser.parse_ecu_db(db_path)
    section = db.sections.get(71)
    if section is None:
        raise ValueError(f"{db_path.name}: selected routine Active Test table 71 is absent")
    if section.decoded_record_size != 72:
        raise ValueError(
            f"{db_path.name}: current type-71 record size {section.decoded_record_size}, expected 72"
        )
    matches = []
    for index in range(section.header.record_count):
        raw = section.decoded_data[index * 72 : (index + 1) * 72]
        if struct.unpack_from("<H", raw, 0x1E)[0] == active_test_id:
            matches.append((index, raw))
    if len(matches) != 1:
        raise ValueError(
            f"{db_path.name}: routine Active Test ID 0x{active_test_id:X} resolved {len(matches)} type-71 rows"
        )
    index, raw = matches[0]
    name_index = struct.unpack_from("<I", raw, 0x08)[0]
    selected = {
        "catalog_context": {**_raw_catalog_source(db_path), "category": category},
        "record": index,
        "active_test_id": active_test_id,
        "active_test_id_hex": f"0x{active_test_id:X}",
        "name_string_index": name_index,
        "name": (strings.get_string(name_index) or "") if strings is not None else None,
        "routine_id": struct.unpack_from("<H", raw, 0x1C)[0],
        "routine_id_hex": f"0x{struct.unpack_from('<H', raw, 0x1C)[0]:04X}",
        "active_test_pattern_key": struct.unpack_from("<H", raw, 0x24)[0],
        "routine_command_variable": struct.unpack_from("<H", raw, 0x28)[0],
        "routine_stop_command_variable": struct.unpack_from("<H", raw, 0x2A)[0],
        "output_mask_value_variable": struct.unpack_from("<H", raw, 0x2C)[0],
        "output_mask_button_variable": struct.unpack_from("<H", raw, 0x2E)[0],
        "routine_status_key": struct.unpack_from("<H", raw, 0x30)[0],
        "pattern_display_variable_key": struct.unpack_from("<H", raw, 0x3C)[0],
        "sort_key": struct.unpack_from("<H", raw, 0x40)[0],
        "raw": raw.hex(),
    }
    return db, db_path, selected


def _routine_active_test_executor_plan(
    parser: DDBParser,
    master: Any,
    category: dict[str, Any],
    selected: dict[str, Any],
) -> dict[str, Any]:
    """Materialize the current GTS+ P5 UDS RoutineControl contract."""
    master = native_context(master)
    category_id = int(category["category_id"])
    rid = int(selected["routine_id"])

    def phase(selector: int, subfunction: int, variable_field: str | None) -> dict[str, Any]:
        rows = _master_frame_rows(parser, master, category_id, selector)
        materialized = []
        for frame in rows:
            expected = bytes((0x31, subfunction, 0xFF, 0xFF))
            send = bytes.fromhex(frame["send"]["bytes"])
            if send != expected:
                raise ValueError(
                    f"category {category_id}: selector 0x{selector:X} base request {send.hex()} != {expected.hex()}"
                )
            expected_reply = bytes((0x71, subfunction)).hex()
            if frame["receive_check"]["bytes"] != expected_reply:
                raise ValueError(
                    f"category {category_id}: selector 0x{selector:X} positive check "
                    f"{frame['receive_check']['bytes']} != {expected_reply}"
                )
            request = bytearray(send)
            request[2] = (rid >> 8) & 0xFF
            request[3] = rid & 0xFF
            variable = None
            if variable_field is not None:
                variable_id = int(selected[variable_field])
                variable = _master_variable(master, variable_id)
                if variable_id:
                    request.extend(bytes.fromhex(variable["bytes"]))
            materialized.append({
                "base_frame": frame,
                "static_command_variable": variable,
                "materialized_static_request": request.hex(),
            })
        return {
            "selector": f"0x{selector:X}",
            "subfunction": f"0x{subfunction:02X}",
            "frames": materialized,
        }

    start = phase(0xD5, 0x01, "routine_command_variable")
    stop = phase(0xD6, 0x02, "routine_stop_command_variable")
    result = phase(0xD7, 0x03, None)
    value_mask = _master_variable(master, int(selected["output_mask_value_variable"]))
    button_mask = _master_variable(master, int(selected["output_mask_button_variable"]))
    # Routine command/stop variables are static bytes copied directly into the
    # request by DataMonitorPhase5. Only output masks admit runtime UI/value bytes.
    fixed = not (
        int(selected["output_mask_value_variable"])
        or int(selected["output_mask_button_variable"])
    )
    return {
        "native_context": master.as_dict(),
        "service": "0x31",
        "service_name": "RoutineControl",
        "positive_response": "0x71",
        "routine_id": rid,
        "routine_id_hex": f"0x{rid:04X}",
        "start": start,
        "stop": stop,
        "result": result,
        "output_mask_value": value_mask,
        "output_mask_button": button_mask,
        "fixed_request": fixed,
        "parameterization": (
            "fixed: all command/stop bytes are static and no runtime value/button mask is referenced"
            if fixed
            else "parameterized: static command bytes are merged with runtime value/button bytes through explicit type-71 masks"
        ),
        "transport": (
            "DataMonitorPhase5 passes buffer+1/length-1 to the shared active_test_start interface with "
            "ActiveTestType=1; DataListIF re-prepends 0x31 and appends a new active node. Only the STOP "
            "chain deduplicates by SID+RID, retaining its existing bytes. The event accepts 0x71, "
            "and the common P5 J2534 worker sends the queued frame via SendIntExt"
        ),
        "boundary": "static plan only; does not execute RoutineControl or prove outer session/authentication requirements",
    }


def _direct_active_test_executor_plan(
    parser: DDBParser,
    master: Any,
    category: dict[str, Any],
    db: Any,
    db_path: Path,
    selected: dict[str, Any],
) -> dict[str, Any]:
    """Describe current-main P5/P6 direct packing with runtime DID length N."""
    master = native_context(master)
    section = db.sections.get(67)
    if section is None:
        raise ValueError(f"{db_path.name}: direct Active-Test table 67 is absent")
    if section.decoded_record_size != 18:
        raise ValueError(f"{db_path.name}: type-67 record size {section.decoded_record_size}, expected 18")
    did = selected["initial_read_did"]
    matches = []
    for index in range(section.header.record_count):
        raw = section.decoded_data[index * 18 : (index + 1) * 18]
        if struct.unpack_from("<H", raw, 0x02)[0] == did:
            matches.append((index, raw))
    if not matches:
        raise ValueError(f"{db_path.name}: DID 0x{did:04X} resolved no type-67 rows")
    encoding_mode = matches[0][1][0x0A]
    type67_records = [
        {
            "record": index,
            "did": did,
            "control_enable_bit_1based": struct.unpack_from("<H", raw, 0x04)[0],
            "data_byte_offset": struct.unpack_from("<H", raw, 0x06)[0],
            "data_byte_length": struct.unpack_from("<H", raw, 0x08)[0],
            "encoding_mode": raw[0x0A],
            "mode5_bit_start_match": struct.unpack_from("<H", raw, 0x0C)[0],
            "mode5_bit_end_match": struct.unpack_from("<H", raw, 0x0E)[0],
            "raw": raw.hex(),
        }
        for index, raw in matches
    ]

    def frames(selector: int, expected: bytes, positive: str) -> list[dict[str, Any]]:
        rows = _master_frame_rows(parser, master, int(category["category_id"]), selector)
        materialized = []
        for row in rows:
            send = bytearray.fromhex(row["send"]["bytes"])
            if send != expected:
                raise ValueError(
                    f"category {category['category_id']}: selector 0x{selector:X} base request {send.hex()} != {expected.hex()}"
                )
            if row["receive_check"]["bytes"] != positive:
                raise ValueError(
                    f"category {category['category_id']}: selector 0x{selector:X} positive response != {positive}"
                )
            send[1] = (did >> 8) & 0xFF
            send[2] = did & 0xFF
            materialized.append({"base_frame": row, "request": send.hex(), "positive_check": positive})
        return materialized

    starts = frames(0x9D, bytes.fromhex("2fffff03"), "6f")
    stops = frames(0x64, bytes.fromhex("2fffff00"), "6f")
    lengths = frames(0xCA, bytes.fromhex("22ffff"), "62")
    bit_start = selected["bit_start"]
    bit_end = selected["bit_end"]
    minimum_length = bit_end // 8 + 1
    payloads = {
        0: ("N-byte value payload || L-byte type-67 enable mask", "L-byte type-67 enable mask"),
        1: ("N-byte value payload || N-byte control-enable mask", "N-byte control-enable mask"),
        3: ("N-byte value payload", "empty"),
        4: ("N-byte shifted value payload || N-byte control-enable mask", "N-byte control-enable mask"),
        5: ("N-byte shifted value payload || L-byte exact-match type-67 enable mask", "FF"),
        6: ("N-byte value payload", "empty"),
    }
    start_payload, stop_payload = payloads.get(encoding_mode, ("unsupported", "unsupported"))
    plan: dict[str, Any] = {
        "native_context": master.as_dict(),
        "service": "0x2F",
        "service_name": "InputOutputControlByIdentifier",
        "positive_response": "0x6F",
        "data_id_for_act": {
            "table": 67,
            "table_class": ECU_TABLE_CLASS_NAMES[67],
            "did": did,
            "did_hex": f"0x{did:04X}",
            "encoding_mode": encoding_mode,
            "encoding_mode_source_record": matches[0][0],
            "records": type67_records,
        },
        "start": {
            "selector": "0x9D",
            "control_parameter": "0x03",
            "control_name": "shortTermAdjustment",
            "frames": [{
                "base_frame": row["base_frame"],
                "materialized_prefix": row["request"],
                "formula": f"{row['request']} || {start_payload}",
            } for row in starts],
        },
        "stop": {
            "selector": "0x64",
            "control_parameter": "0x00",
            "control_name": "returnControlToECU",
            "frames": [{
                "base_frame": row["base_frame"],
                "materialized_prefix": row["request"],
                "formula": f"{row['request']} || {stop_payload}",
            } for row in stops],
        },
        "runtime_data_length": {
            "symbol": "N",
            "source": "CCmdDataIdLengthList runtime support cache",
            "minimum_from_bit_geometry": minimum_length,
            "probe": {
                "kind": "read_data_by_identifier_value_length",
                "selector": "0xCA",
                "frames": [{
                    "base_frame": row["base_frame"],
                    "materialized_request": row["request"],
                    "positive_check": row["positive_check"],
                } for row in lengths],
                "response_prefix_length": 3,
                "received_length_formula": "N = received UDS payload length - 3 (positive SID 0x62 + echoed DID)",
                "decoded_value_formula": "N = len(ReadDataByIdentifier value bytes after stripping 0x62 || DID)",
                "cache_population": (
                    "CCommCachePlusP5::CheckSupportDid reads selector 0xCA, then appends DID and "
                    "received_length-3 to the per-ECU CCmdDataIdLengthList cache"
                ),
            },
            "boundary": "static DDB geometry gives only a minimum; the exact length is materialized from the live 0x22 response",
        },
        "bit_range": {"start": bit_start, "end": bit_end},
        "encoding_requirements": {
            "source_scope": "current main GTSPlus DataMonitorPhase5_DT.dll and DataMonitorPhase6_DT.dll",
            "p5_supported": encoding_mode in {0, 1, 3, 4, 5},
            "p6_supported": encoding_mode in {0, 1, 3, 4, 6},
            "unsupported_status": "0xC0040102",
            "value_input": "CStartActTstSnd raw u32 +0x24 and alternate u32 +0x28",
            "adapter": "DiagAdaptation logical-value conversion writes these fields directly; SetValue is a separate native-caller path",
            "engine_selection": (
                "ordinary category generation low5bits 0x14/0x15 selects P5 and 0x16 selects P6; "
                "controller mode, multi-ECU flags and populated connection state can instead select Dual/Fuel. "
                "The category alone does not establish the loaded executor."
            ),
        },
        "control_enable_mask": {
            "start": (
                "type67_rows_for_selected_byte_span" if encoding_mode == 0
                else "selected_bit_range_or_alternate" if encoding_mode == 1
                else "selected_bit_range" if encoding_mode == 4
                else "first_exact_type67_row" if encoding_mode == 5
                else "none"
            ),
            "stop": (
                "type67_rows_for_selected_byte_span" if encoding_mode == 0
                else "selected_bit_range_or_alternate" if encoding_mode == 1
                else "selected_bit_range" if encoding_mode == 4
                else "single_FF_byte" if encoding_mode == 5
                else "none"
            ),
            "type67_rule": (
                "mode 0 includes fully contained type-67 byte spans and sets MSB0 bit "
                "control_enable_bit_1based-1; L is the highest selected mask-byte index plus one. "
                "P5 mode 5 uses the first row with start_byte <= data_byte_offset < start_byte+width, "
                "data_byte_offset+data_byte_length <= start_byte+width and exact +0x0C/+0x0E bit bounds. "
                "A matched zero enable key returns C0040102; no matching mode-5 row yields L=0."
            ),
        },
        "encoding": (
            "mode 0/3 zero-fill N bytes and write raw32 big-endian across "
            "u16(trunc_toward_zero((bit_end-bit_start)/8)+1) bytes, restricted to widths 1..4; "
            "mode 0 appends its type-67 mask to START and STOP, while mode 3 appends no mask"
            if encoding_mode in {0, 3}
            else "mode 1 alternate=0 writes low8(raw)<<[7-(bit_end&7)] at bit_end>>3 and appends an "
                 "N-byte inclusive range mask to START and STOP; u8(bit_end-bit_start)>7 returns C0040102. "
                 "Nonzero alternate requires a one-byte span and uses unshifted raw8 and low8(alternate)"
            if encoding_mode == 1
            else "mode 4 writes u32(raw32<<[7-(bit_end&7)]) big-endian over the 1..4-byte span and "
                 "appends an N-byte inclusive range mask to START and STOP"
            if encoding_mode == 4
            else "P5 mode 5 uses the same shifted raw32 placement, appends its first exact type-67 "
                 "row's L-byte enable mask to START and one FF byte to STOP; P6 rejects mode 5"
            if encoding_mode == 5
            else "P6 mode 6 writes low8(raw)<<[7-(bit_end&7)] at bit_end>>3; START carries N data bytes "
                 "and STOP has no payload; P5 rejects mode 6"
            if encoding_mode == 6
            else f"encoding mode {encoding_mode} returns native status C0040102"
        ),
        "transport": (
            "DataMonitor strips the existing SID; the matching P5/P6 DataListIF active event re-prepends "
            "0x2F. START always appends a new active node. Only the STOP chain deduplicates by SID+DID, "
            "retaining its existing bytes. GetSndFrame copies queued bytes unchanged to SendIntExt."
        ),
    }
    if encoding_mode == 1 and bit_start == bit_end:
        byte_index = bit_end // 8
        shift = 7 - (bit_end & 7)
        off = bytearray(minimum_length)
        on = bytearray(minimum_length)
        mask = bytearray(minimum_length)
        on[byte_index] = 1 << shift
        mask[byte_index] = 1 << shift
        plan["minimum_length_examples"] = {
            "start": [{
                "raw_0": (bytes.fromhex(row["request"]) + off + mask).hex(),
                "raw_1": (bytes.fromhex(row["request"]) + on + mask).hex(),
            } for row in starts],
            "stop": [{
                "return_control": (bytes.fromhex(row["request"]) + mask).hex(),
            } for row in stops],
            "qualification": (
                f"uses N={minimum_length}, the static minimum required by bit {bit_end}; "
                "not proof that the runtime DataIdLengthList entry has that length"
            ),
        }
    return plan


def _initial_read_program(
    frames: list[dict[str, Any]], category_id: int, did: int
) -> list[dict[str, Any]]:
    materialized = []
    for frame in frames:
        request = bytearray.fromhex(frame["send"]["bytes"])
        if len(request) < 3 or request[0] != 0x22:
            raise ValueError(
                f"category {category_id}: selector 0xCA base request is not 22xxxx: {request.hex()}"
            )
        request[1] = (did >> 8) & 0xFF
        request[2] = did & 0xFF
        materialized.append({
            "base_frame": frame,
            "materialized_send": request.hex(),
            "receive_check": frame["receive_check"]["bytes"],
        })
    return materialized


def _active_test_init_selected_plan(
    parser: DDBParser,
    master: Any,
    category: dict[str, Any],
    db_root: Path,
    active_test_id: int,
    strings: StringDataBase | None = None,
) -> dict[str, Any]:
    db, db_path, selected = _direct_active_test_selected_row(
        parser, category, db_root, active_test_id, strings
    )

    mode = selected["initial_read_mode"]
    transaction: dict[str, Any] = {"mode": mode, "performed": False}
    if mode == 0:
        frames = _master_frame_rows(parser, master, int(category["category_id"]), 0xCA)
        program = _initial_read_program(frames, int(category["category_id"]), selected["initial_read_did"])
        transaction = {
            "mode": mode,
            "performed": True,
            "selector": "0xCA",
            "frames": program,
            "bit_start": selected["bit_start"],
            "bit_end": selected["bit_end"],
        }
    elif mode == 1:
        transaction["reason"] = "type-68 initial_read_mode == 1"
    else:
        transaction["reason"] = "plugin rejects modes other than 0/1 as C0040102"

    mode_generation = int(category["generation"]) & 0xE0
    monitor_table = 157 if mode_generation == 0x60 else 62
    linked: dict[str, Any] = {
        "mode": selected["monitor_link_mode"],
        "table": monitor_table,
        "monitor_key": None,
        "resolution": None,
    }
    if selected["monitor_link_mode"] == 1:
        linked["monitor_key"] = selected["direct_monitor_key"]
        linked["resolution"] = "direct type-68 +0x36"
    else:
        monitor = db.sections.get(monitor_table)
        if monitor is None:
            linked["resolution"] = "generation-selected monitor table absent"
        elif monitor.decoded_record_size < 0x48:
            raise ValueError(
                f"{db_path.name}: monitor table {monitor_table} record size 0x{monitor.decoded_record_size:X} too small"
            )
        else:
            candidates = []
            size = monitor.decoded_record_size
            for monitor_index in range(monitor.header.record_count):
                mon = monitor.decoded_data[monitor_index * size : (monitor_index + 1) * size]
                if not (struct.unpack_from("<I", mon, 0x30)[0] & 0x40):
                    continue
                if struct.unpack_from("<H", mon, 0x46)[0] != selected["initial_read_did"]:
                    continue
                if struct.unpack_from("<H", mon, 0x3C)[0] != selected["bit_start"]:
                    continue
                if struct.unpack_from("<H", mon, 0x3E)[0] != selected["bit_end"]:
                    continue
                candidates.append({
                    "record": monitor_index,
                    "monitor_key": struct.unpack_from("<H", mon, 0x34)[0],
                })
            linked["candidates"] = candidates
            if len(candidates) == 1:
                linked["monitor_key"] = candidates[0]["monitor_key"]
                linked["resolution"] = "unique DID/bit-range match from plugin scan"
            else:
                linked["resolution"] = f"plugin scan produced {len(candidates)} matches"

    if strings is not None and linked["monitor_key"] is not None:
        semantic = [
            row for row in _monitor_rows(db, strings, db_path.name)
            if row.get("monitor_key") == linked["monitor_key"]
        ]
        if len(semantic) == 1:
            linked["monitor"] = semantic[0]

    executor = _direct_active_test_executor_plan(parser, master, category, db, db_path, selected)

    return {
        "selected_test": selected,
        "initial_transaction": transaction,
        "linked_monitor": linked,
        "executor": executor,
        "runtime_boundary": (
            "selected-row and initial-request materialization are offline deterministic; whether the test is offered "
            "and panel entries are supported still depends on role-0x06/live support state"
        ),
    }


def _direct_active_test_signal_info(
    db: Any,
    db_path: Path,
    selected: dict[str, Any],
    strings: StringDataBase,
) -> dict[str, Any]:
    """Resolve current role-0x70 signal metadata for one selected type-68 row."""
    def unique_record(table: int, key_offset: int, key: int) -> tuple[int, bytes]:
        section = db.sections.get(table)
        if section is None:
            raise ValueError(f"{db_path.name}: required role-0x70 table {table} is absent")
        size = section.decoded_record_size
        matches = []
        for index in range(section.header.record_count):
            raw = section.decoded_data[index * size : (index + 1) * size]
            if len(raw) >= key_offset + 2 and struct.unpack_from("<H", raw, key_offset)[0] == key:
                matches.append((index, raw))
        if len(matches) != 1:
            raise ValueError(
                f"{db_path.name}: table {table} key 0x{key:X} resolved {len(matches)} rows"
            )
        return matches[0]

    pattern_index, pattern = unique_record(12, 0x00, selected["active_test_pattern_key"])
    physical_index, physical = unique_record(13, 0x0C, selected["physical_data_key"])
    unit_key = struct.unpack_from("<H", physical, 0x0E)[0]
    unit_index, unit = unique_record(15, 0x04, unit_key)
    pattern_display_key = struct.unpack_from("<H", pattern, 0x0A)[0]
    display = []
    section14 = db.sections.get(14)
    if section14 is None:
        raise ValueError(f"{db_path.name}: required role-0x70 table 14 is absent")
    for index in range(section14.header.record_count):
        size = section14.decoded_record_size
        raw = section14.decoded_data[index * size : (index + 1) * size]
        if len(raw) >= 0x0E and struct.unpack_from("<H", raw, 0x0C)[0] == pattern_display_key:
            display.append({
                "record": index,
                "value": struct.unpack_from("<I", raw, 0x04)[0],
                "text": strings.get_string(struct.unpack_from("<I", raw, 0x00)[0]),
                "raw": raw.hex(),
            })

    return {
        "active_test_pattern": {
            "record": pattern_index,
            "key": selected["active_test_pattern_key"],
            "button_size": pattern[0x15],
            "key_operation_pattern": pattern[0x13],
            "key_invalid_flag": pattern[0x12],
            "maintenance_time": struct.unpack_from("<H", pattern, 0x04)[0],
            "auto_continue_time": struct.unpack_from("<H", pattern, 0x06)[0],
            "lock_time": struct.unpack_from("<H", pattern, 0x0C)[0],
            "pattern_display_key": pattern_display_key,
            "raw": pattern.hex(),
        },
        "physical": {
            "record": physical_index,
            "key": selected["physical_data_key"],
            "mul": struct.unpack_from("<i", physical, 0x00)[0],
            "div": struct.unpack_from("<i", physical, 0x04)[0],
            "offset": struct.unpack_from("<i", physical, 0x08)[0],
            "signed": bool(physical[0x14]),
            "decimal_point_count": physical[0x15],
            "unit_key": unit_key,
            "unit_record": unit_index,
            "unit": strings.get_string(struct.unpack_from("<I", unit, 0x00)[0]),
            "unit_genre_id": struct.unpack_from("<H", unit, 0x06)[0],
            "raw": physical.hex(),
        },
        "display_info": display,
    }


def _active_test_signal_info_selected_plan(
    parser: DDBParser,
    category: dict[str, Any],
    db_root: Path,
    active_test_id: int,
    strings: StringDataBase,
) -> dict[str, Any]:
    db, db_path, selected = _direct_active_test_selected_row(
        parser, category, db_root, active_test_id, strings
    )
    resolved = _direct_active_test_signal_info(db, db_path, selected, strings)
    return {
        "selected_test": selected,
        **resolved,
        "runtime_boundary": (
            "role-0x70 is metadata-only for the exact plugin identity; this selected-item plan does not execute "
            "transport or prove role-0x06 live availability"
        ),
    }


def _multi_active_test_category_plan(
    parser: DDBParser, category: dict[str, Any], db_root: Path
) -> dict[str, Any]:
    db_path = Path(category.get("catalog_database_path") or db_root / str(category["database"]))
    db = parser.parse_ecu_db(db_path)
    section = db.sections.get(33)
    if section is None:
        return {
            "catalog_context": {**_raw_catalog_source(db_path), "category": category},
            "group_table": 33,
            "group_table_class": ECU_TABLE_CLASS_NAMES.get(33, "unknown"),
            "group_count": 0,
            "membership_count": 0,
            "groups": [],
            "boundary": "category binds role 0x63 but has no type-33 multi-control membership table",
        }
    if section.decoded_record_size != 12:
        raise ValueError(f"{db_path.name}: type-33 record size {section.decoded_record_size}, expected 12")
    groups: dict[int, list[dict[str, Any]]] = {}
    for index in range(section.header.record_count):
        raw = section.decoded_data[index * 12 : (index + 1) * 12]
        group_id = struct.unpack_from("<H", raw, 0x00)[0]
        groups.setdefault(group_id, []).append({
            "record": index,
            "member_active_test_id": struct.unpack_from("<H", raw, 0x02)[0],
            "unknown_word_04": struct.unpack_from("<H", raw, 0x04)[0],
            "input_slot": struct.unpack_from("<H", raw, 0x06)[0],
            "sort_order": struct.unpack_from("<I", raw, 0x06)[0],
            "unknown_word_08": struct.unpack_from("<H", raw, 0x08)[0],
            "unknown_word_0A": struct.unpack_from("<H", raw, 0x0A)[0],
            "raw": raw.hex(),
        })
    rows = [
        {
            "group_id": group_id,
            "group_id_hex": f"0x{group_id:X}",
            "members": sorted(members, key=lambda row: (row["input_slot"], row["member_active_test_id"])),
        }
        for group_id, members in sorted(groups.items())
    ]
    return {
        "catalog_context": {**_raw_catalog_source(db_path), "category": category},
        "group_table": 33,
        "group_table_class": ECU_TABLE_CLASS_NAMES.get(33, "unknown"),
        "record_size": 12,
        "group_count": len(rows),
        "membership_count": section.header.record_count,
        "groups": rows,
        "boundary": (
            "type-33 +0x00 is group ID, +0x02 member Active-Test ID, and +0x06 is the current "
            "runtime input-slot selector (1 -> CStartActTstSnd +0x24, 2 -> +0x28); each member "
            "then follows the ordinary type-68 direct materializer"
        ),
    }


def _multi_active_test_group_plan(
    parser: DDBParser,
    master: Any,
    category: dict[str, Any],
    db_root: Path,
    group_id: int,
    strings: StringDataBase,
) -> dict[str, Any]:
    census = _multi_active_test_category_plan(parser, category, db_root)
    matches = [group for group in census["groups"] if group["group_id"] == group_id]
    if len(matches) != 1:
        raise ValueError(
            f"{category['database']}: multi Active Test group 0x{group_id:X} resolved {len(matches)} type-33 groups"
        )
    group = matches[0]
    _, _, parent = _direct_active_test_selected_row(parser, category, db_root, group_id, strings)
    frames = _master_frame_rows(parser, master, int(category["category_id"]), 0xCA)
    members = []
    for membership in group["members"]:
        _, _, selected = _direct_active_test_selected_row(
            parser, category, db_root, membership["member_active_test_id"], strings
        )
        mode = selected["initial_read_mode"]
        transaction: dict[str, Any] = {"mode": mode, "performed": False}
        if mode == 0:
            program = _initial_read_program(frames, int(category["category_id"]), selected["initial_read_did"])
            transaction = {
                "mode": 0,
                "performed": True,
                "selector": "0xCA",
                "frames": program,
                "bit_start": selected["bit_start"],
                "bit_end": selected["bit_end"],
            }
        elif mode == 1:
            transaction["reason"] = "type-68 initial_read_mode == 1"
        else:
            transaction["reason"] = "plugin rejects modes other than 0/1 as C0040102"
        members.append({
            **membership,
            "selected_test": selected,
            "initial_transaction": transaction,
        })
    return {
        "group": {
            "group_id": group_id,
            "group_id_hex": f"0x{group_id:X}",
            "name": parent["name"],
            "selected_test": parent,
            "member_count": len(members),
        },
        "base_frames": frames,
        "members": members,
        "runtime_boundary": (
            "group expansion, ordering, type-68 member fields, and initial request materialization are static; "
            "the role does not imply that every category binding has type-33 groups"
        ),
    }


def _active_test_monitor_category_plan(
    parser: DDBParser, category: dict[str, Any], db_root: Path
) -> dict[str, Any]:
    mode = int(category["generation"]) & 0xE0
    table = 157 if mode == 0x60 else 62
    db_path = Path(category.get("catalog_database_path") or db_root / str(category["database"]))
    db = parser.parse_ecu_db(db_path)
    section = db.sections.get(table)
    if section is None:
        raise ValueError(f"{db_path.name}: role-0xAD selected monitor table {table}, but it is absent")
    size = section.decoded_record_size
    if size < 0x36:
        raise ValueError(f"{db_path.name}: monitor table {table} record size 0x{size:X} too small")
    counts = {
        "active_direct_include": 0,
        "active_runtime_check_support_pid": 0,
        "nonmember_direct_exclude": 0,
        "nonmember_runtime_probe_then_filter": 0,
    }
    for index in range(section.header.record_count):
        raw = section.decoded_data[index * size : (index + 1) * size]
        flag = raw[0x30]
        active_member = bool(flag & 0x40)
        direct_decision = bool(flag & 0x10)
        if active_member and direct_decision:
            counts["active_direct_include"] += 1
        elif active_member:
            counts["active_runtime_check_support_pid"] += 1
        elif direct_decision:
            counts["nonmember_direct_exclude"] += 1
        else:
            counts["nonmember_runtime_probe_then_filter"] += 1
    active_count = counts["active_direct_include"] + counts["active_runtime_check_support_pid"]
    nonmember_count = counts["nonmember_direct_exclude"] + counts["nonmember_runtime_probe_then_filter"]
    return {
        "catalog_context": {**_raw_catalog_source(db_path), "category": category},
        "generation": int(category["generation"]),
        "generation_mode": f"0x{mode:X}",
        "candidate_table": table,
        "candidate_table_class": ECU_TABLE_CLASS_NAMES.get(table, "unknown"),
        "candidate_count": section.header.record_count,
        "record_size": size,
        "active_test_membership_bit": "0x40",
        "active_test_candidate_count": active_count,
        "nonmember_count": nonmember_count,
        "support_list_builder": (
            "CreateEnableDataIdListForSubaruCheckDID" if mode == 0x20 else "CreateEnableDataIdList"
        ),
        "candidate_partition": counts,
        "runtime_support_required": (
            counts["active_runtime_check_support_pid"] > 0
            or counts["nonmember_runtime_probe_then_filter"] > 0
        ),
        "runtime_boundary": (
            "bit-0x40 membership is static, but CheckSupportPid outcomes remain runtime/cache dependent; "
            "nonmember rows with bit4 clear are still support-probed by the plugin before the final 0x40 filter"
        ),
    }


def _monitor_list_category_plan(parser: DDBParser, category: dict[str, Any], db_root: Path) -> dict[str, Any]:
    mode = int(category["generation"]) & 0xE0
    table = 157 if mode == 0x60 else 62
    db_path = Path(category.get("catalog_database_path") or db_root / str(category["database"]))
    db = parser.parse_ecu_db(db_path)
    section = db.sections.get(table)
    if section is None:
        raise ValueError(f"{db_path.name}: role-0x05 selected monitor table {table}, but it is absent")
    counts = {"direct_include": 0, "direct_exclude": 0, "runtime_check_support_pid": 0}
    size = section.decoded_record_size
    if size < 0x36:
        raise ValueError(f"{db_path.name}: monitor table {table} record size 0x{size:X} too small")
    for index in range(section.header.record_count):
        raw = section.decoded_data[index * size : (index + 1) * size]
        flag = raw[0x30]
        if flag & 0x10:
            counts["direct_include" if flag & 0x01 else "direct_exclude"] += 1
        else:
            counts["runtime_check_support_pid"] += 1
    return {
        "catalog_context": {**_raw_catalog_source(db_path), "category": category},
        "generation": int(category["generation"]),
        "generation_mode": f"0x{mode:X}",
        "candidate_table": table,
        "candidate_table_class": ECU_TABLE_CLASS_NAMES.get(table, "unknown"),
        "candidate_count": section.header.record_count,
        "record_size": size,
        "support_list_builder": (
            "CreateEnableDataIdListForSubaruCheckDID" if mode == 0x20 else "CreateEnableDataIdList"
        ),
        "candidate_partition": counts,
        "runtime_support_required": counts["runtime_check_support_pid"] > 0,
        "runtime_boundary": (
            "candidate partition is static; records in runtime_check_support_pid require support-cache/live ECU "
            "CheckSupportPid results before Techstream's final presented list is known"
        ),
    }


def resolve_active_test(
    parser: DDBParser,
    master: Any,
    category: dict[str, Any],
    db_root: Path,
    strings: StringDataBase | None,
    active_test_id: int,
    kind: str | None,
) -> tuple[str, dict[str, Any]]:
    """Resolve one direct or routine P5 Active Test into its static wire plan."""
    master = native_context(master)
    category = native_ecu_catalog_category(master, category, db_root, parser)
    db = parser.parse_ecu_db(Path(category["catalog_database_path"]))
    kinds = []
    if 68 in db.sections and db.sections[68].decoded_record_size == 64:
        size = db.sections[68].decoded_record_size
        if any(
            struct.unpack_from("<H", db.sections[68].decoded_data, index * size + 0x20)[0] == active_test_id
            for index in range(db.sections[68].header.record_count)
        ):
            kinds.append("direct")
    if 71 in db.sections and db.sections[71].decoded_record_size == 72:
        size = db.sections[71].decoded_record_size
        if any(
            struct.unpack_from("<H", db.sections[71].decoded_data, index * size + 0x1E)[0] == active_test_id
            for index in range(db.sections[71].header.record_count)
        ):
            kinds.append("routine")

    if kind is not None:
        if kind not in kinds:
            raise SystemExit(
                f"{category['database']}: Active Test 0x{active_test_id:X} is not a {kind} candidate"
            )
    elif len(kinds) == 1:
        kind = kinds[0]
    elif not kinds:
        raise SystemExit(
            f"{category['database']}: Active Test 0x{active_test_id:X} was not found in current type-68/type-71 tables"
        )
    else:
        raise SystemExit(
            f"{category['database']}: Active Test 0x{active_test_id:X} exists as both {', '.join(kinds)}; use --kind"
        )

    if kind == "direct":
        _, _, selected = _direct_active_test_selected_row(
            parser, category, db_root, active_test_id, strings
        )
        selected_plan = _active_test_init_selected_plan(
            parser, master, category, db_root, active_test_id, strings
        )
        payload = {
            "native_context": native_context(master).as_dict(),
            "category": category,
            "kind": kind,
            "selected_test": selected,
            "executor": selected_plan["executor"],
            "initial_transaction": selected_plan["initial_transaction"],
            "linked_monitor": selected_plan["linked_monitor"],
            "boundary": "read-only static planning; no Active Test request is sent",
        }
    else:
        _, _, selected = _routine_active_test_selected_row(
            parser, category, db_root, active_test_id, strings
        )
        payload = {
            "native_context": native_context(master).as_dict(),
            "category": category,
            "kind": kind,
            "selected_test": selected,
            "executor": _routine_active_test_executor_plan(parser, master, category, selected),
            "boundary": "read-only static planning; no RoutineControl request is sent",
        }
    return kind, payload
