"""camry-2026-f33 derived Toyota diagnostic registry: catalogs, session control, vehicle resolution, utilities, source identity."""

from __future__ import annotations

import json
import struct
from pathlib import Path
from typing import Any

from tools import REPO_ROOT
from tools.techstream.gts.active_tests import (
    _direct_active_test_executor_plan,
    _direct_active_test_selected_row,
    _direct_active_test_signal_info,
    _multi_active_test_category_plan,
    _routine_active_test_executor_plan,
    _routine_active_test_selected_row,
)
from tools.techstream.gts.ddb import _dtc_rows, _english_strings, _generic_ffd_rows, _monitor_rows, _rob_rows
from tools.techstream.ddb_semantics import extract_monitor_records
from tools.techstream.gts.execution_model import (
    EXECUTION_MODEL,
    GENERIC_UTILITY_ROLE_KINDS,
    P6_ACTIVE_TEST_PLUGIN_KINDS,
    VEHICLE_RESOLVER,
    _execution_model,
    _file_sha256,
    _semantic_kind_for_profile,
    _semantic_profile_for_plugin,
)
from tools.techstream.gts.master import (
    _master_canbus_topology_rows,
    _master_comm_set_rows,
    _master_frame_rows,
    _master_timer_rows,
    _master_variable,
    _resolve_master_category,
)
from tools.techstream.parse_ddb import DDBParser, StringDataBase
from tools.techstream.gts import support
from tools.techstream.techstream_paths import gts_db_root, resolve_gts_root


CAMRY_2026_DIAG_PROFILE = {
    "profile": "camry-2026-f33",
    "vehicle": "2026 Toyota Camry Hybrid",
    "panda_bus": 0,
    "fault_status_mask": 0xAF,
    "identity_guard": {
        "ecu": "eps",
        "did": 0xF181,
        "contains_ascii": "8965F3307000",
    },
    "ecus": [
        {"key": "engine", "name": "Engine", "address": 0x700, "category_id": 372, "functional_response": 0x7E8},
        {"key": "ect", "name": "ECT", "address": 0x701},
        {"key": "motor_generator", "name": "Motor Generator", "address": 0x724, "category_id": 395, "functional_response": 0x7EE},
        {"key": "hybrid", "name": "Hybrid Control", "address": 0x7D2, "category_id": 397, "functional_response": 0x7EA},
        {"key": "hv_battery", "name": "HV Battery", "address": 0x747, "category_id": 398, "functional_response": 0x7EB},
        {"key": "plug_in", "name": "Plug-in Control", "address": 0x745},
        {"key": "ecu_707", "name": "ECU 0x707", "address": 0x707},
        {"key": "ecu_703", "name": "ECU 0x703", "address": 0x703},
        {"key": "eps", "name": "Power Steering", "address": 0x7A1, "category_id": 405},
        {"key": "brake", "name": "Brake/EPB", "address": 0x7B0, "category_id": 435, "functional_response": 0x7ED},
        {"key": "ecu_750", "name": "ECU 0x750", "address": 0x750},
        {"key": "ecu_7b3", "name": "ECU 0x7B3", "address": 0x7B3},
        {"key": "air_conditioner", "name": "Air Conditioner", "address": 0x7C4, "category_id": 450},
        {"key": "ecu_7d1", "name": "ECU 0x7D1", "address": 0x7D1},
        {"key": "ecu_7d0", "name": "ECU 0x7D0", "address": 0x7D0},
        {"key": "frc", "name": "Front Recognition Camera", "address": 0x792, "category_id": 498},
        {"key": "ecu_7a2", "name": "ECU 0x7A2", "address": 0x7A2},
    ],
}


def _registry_signal_row(row: dict[str, Any]) -> dict[str, Any]:
    info = row.get("signal_info") or {}
    return {
        "decoder": "p5-linear-msb0-v1",
        "monitor_key": row.get("monitor_key"),
        "alternate_did": row.get("alternate_did"),
        "name": row.get("name") or "",
        "bit_start": row.get("bit_start"),
        "bit_end": row.get("bit_end"),
        "mul": info.get("mul", 1),
        "div": info.get("div", 1),
        "offset": info.get("offset", 0),
        "decimal_point_count": info.get("decimal_point_count", 0),
        "signed": bool(info.get("signed", False)),
        "unit": info.get("unit"),
        "data_range": info.get("data_range"),
        "graph_range": info.get("graph_range"),
        "patterns": {str(key): value for key, value in (info.get("pattern_display") or {}).items()},
    }


def _registry_did_catalog(rows: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        did = int(row["primary_did"])
        grouped.setdefault(f"0x{did:04X}", []).append(_registry_signal_row(row))
    return grouped


def _registry_eps_observed_identity(capture: dict[str, Any]) -> dict[str, Any]:
    route = capture["route"]
    if int(route["eps_tx"], 16) != 0x7A1:
        raise ValueError("Camry EPS identity TX drift")
    if route["eps_bus"] != 1 or route["elm327_param"] != 1:
        raise ValueError("Camry EPS pre-repin route drift")
    rows = {row["name"]: row for row in capture["identity"]}
    f181 = bytes.fromhex(rows["app_sw_id"]["hex"])
    if not f181 or f181[0] != 2 or len(f181) != 33:
        raise ValueError("Camry EPS F181 two-ID layout drift")
    software_ids = [f181[1 + 16 * index : 1 + 16 * (index + 1)].rstrip(b"\0").decode("ascii") for index in range(2)]
    serial = bytes.fromhex(rows["ecu_serial"]["hex"]).rstrip(b"\0").decode("ascii")
    return {
        "observation": "2026-08-26 pre-repin normal-harness NRTD",
        "panda_bus_at_observation": 1,
        "elm327_param": 1,
        "f181_software_ids": software_ids,
        "f18c_serial": serial,
        "route_note": "historical pre-repin Panda bus; current profile diagnostic route is post-repin Panda bus0",
    }


def _registry_nrtd_observed_identities(nrtd: dict[str, Any]) -> dict[str, dict[str, Any]]:
    modules = nrtd["module_identity"]
    if modules["elm327_param"] != 1:
        raise ValueError("Camry NRTD module identity ELM327 param drift")
    out: dict[str, dict[str, Any]] = {}
    for key, source_key in (("frc", "FRC_P5"), ("brake", "Brake_EPB_category_435")):
        row = modules[source_key]
        if row["bus"] != 1:
            raise ValueError(f"{source_key} pre-repin observation bus drift")
        out[key] = {
            "observation": "2026-08-26 pre-repin NRTD",
            "panda_bus_at_observation": 1,
            "elm327_param": 1,
            "f181_software_ids": [row["f181"]],
            "f18c_serial": row["f18c_serial"],
            "ecu_part_0105": row["ecu_part_0105"],
            "route_note": "historical pre-repin Panda bus; current profile diagnostic route is post-repin Panda bus0",
        }
    return out


def _registry_dtc_catalog(parser: DDBParser, db: Any, strings: StringDataBase, source: str) -> dict[str, list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = {}
    for row in _dtc_rows(parser, db, strings, source):
        packed = str(row.get("packed_dtc") or "").removeprefix("0x").upper()
        if not packed:
            continue
        grouped.setdefault(packed, []).append({
            "code": row.get("code") or "",
            "description": row.get("description") or "",
            "failure": row.get("failure") or "",
        })
    return grouped


def _compact_direct_active_test(
    selected: dict[str, Any],
    executor: dict[str, Any],
    monitor_rows: list[dict[str, Any]],
    init_frame: dict[str, Any] | None = None,
    signal_info: dict[str, Any] | None = None,
) -> dict[str, Any]:
    linked = [
        row for row in monitor_rows
        if row.get("primary_did") == selected["initial_read_did"]
        and row.get("bit_start") == selected["bit_start"]
        and row.get("bit_end") == selected["bit_end"]
    ]
    monitor = linked[0] if len(linked) == 1 else {}
    return {
        "id": selected["active_test_id"],
        "name": selected.get("name") or "",
        "kind": "direct",
        "service": 0x2F,
        "positive_response": 0x6F,
        "did": executor["data_id_for_act"]["did"],
        "encoding_mode": executor["data_id_for_act"]["encoding_mode"],
        "data_id_for_act_records": executor["data_id_for_act"]["records"],
        "control_enable_mask": executor["control_enable_mask"],
        "bit_start": executor["bit_range"]["start"],
        "bit_end": executor["bit_range"]["end"],
        "start_prefix": executor["start"]["materialized_prefix"],
        "stop_prefix": executor["stop"]["materialized_prefix"],
        "runtime_length_minimum": executor["runtime_data_length"]["minimum_from_bit_geometry"],
        "runtime_length_probe": {
            "kind": executor["runtime_data_length"]["probe"]["kind"],
            "selector": executor["runtime_data_length"]["probe"]["selector"],
            "request": executor["runtime_data_length"]["probe"]["materialized_request"],
            "check": executor["runtime_data_length"]["probe"]["positive_check"],
            "response_prefix_length": executor["runtime_data_length"]["probe"]["response_prefix_length"],
            "received_length_formula": executor["runtime_data_length"]["probe"]["received_length_formula"],
            "decoded_value_formula": executor["runtime_data_length"]["probe"]["decoded_value_formula"],
        },
        "minimum_examples": executor.get("minimum_length_examples"),
        "initial_read": _direct_initial_read_plan(selected, init_frame),
        "monitor_key": monitor.get("monitor_key"),
        "monitor_name": monitor.get("name") or "",
        "signal_info": signal_info,
        "session_requirement": _session_requirement(executor["start"]["materialized_prefix"]),
        "execution": "plan_only",
    }


def _direct_initial_read_plan(selected: dict[str, Any], init_frame: dict[str, Any] | None) -> dict[str, Any]:
    """Compact role-0x08 selector-0xCA initial-read request for one direct test."""
    plan: dict[str, Any] = {"mode": selected["initial_read_mode"]}
    if selected["initial_read_mode"] != 0 or init_frame is None:
        return plan
    did = int(selected["initial_read_did"])
    request = bytearray.fromhex(init_frame["send"]["bytes"])
    if len(request) < 3 or request[0] != 0x22:
        raise ValueError("selector 0xCA base request is no longer 22xxxx")
    request[1] = (did >> 8) & 0xFF
    request[2] = did & 0xFF
    plan.update({
        "selector": "0xCA",
        "request": request.hex(),
        "check": init_frame["receive_check"]["bytes"],
    })
    return plan


def _compact_routine_active_test(selected: dict[str, Any], executor: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": selected["active_test_id"],
        "name": selected.get("name") or "",
        "kind": "routine",
        "service": 0x31,
        "positive_response": 0x71,
        "routine_id": selected["routine_id"],
        "start_static": executor["start"]["materialized_static_request"],
        "stop_static": executor["stop"]["materialized_static_request"],
        "result_static": executor["result"]["materialized_static_request"],
        "fixed_request": executor["fixed_request"],
        "routine_command_variable": selected["routine_command_variable"],
        "routine_stop_command_variable": selected["routine_stop_command_variable"],
        "output_mask_value_variable": selected["output_mask_value_variable"],
        "output_mask_button_variable": selected["output_mask_button_variable"],
        "routine_command": executor["start"]["static_command_variable"],
        "routine_stop_command": executor["stop"]["static_command_variable"],
        "output_mask_value": executor["output_mask_value"],
        "output_mask_button": executor["output_mask_button"],
        "routine_status_key": selected["routine_status_key"],
        "session_requirement": _session_requirement(executor["start"]["materialized_static_request"]),
        "execution": "executable" if executor["fixed_request"] else "plan_only",
    }


def _registry_active_tests(
    parser: DDBParser,
    master: Any,
    category: dict[str, Any],
    db_root: Path,
    strings: StringDataBase,
    monitor_rows: list[dict[str, Any]],
    bindings: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    db_path = db_root / str(category["database"])
    db = parser.parse_ecu_db(db_path)
    init_frames = _master_frame_rows(parser, master, int(category["category_id"]), 0xCA)
    init_frame = init_frames[0] if len(init_frames) == 1 else None
    dll_rows = list(parser.extract_master_dlls(master.sections[19]))
    category_id = int(category["category_id"])
    support_family = support.support_family(
        support.support_plugin(dll_rows, category_id, 0x67),
        support.support_plugin(dll_rows, category_id, 0xD5),
    )
    support_mode = support.support_mode(category_id, int(category["generation"]), support_family)
    signal_info_enabled = any(
        int(binding.get("role", -1)) == 0x70
        and binding.get("semantic_kind") in {"p5_active_test_signal_info", "p6_active_test_signal_info"}
        and binding.get("semantic_status") == "exact_plugin_identity"
        for binding in bindings
    )
    rows: list[dict[str, Any]] = []
    direct = db.sections.get(68)
    if direct is not None:
        if direct.decoded_record_size != 64:
            raise ValueError(f"{db_path.name}: type-68 record size {direct.decoded_record_size}, expected 64")
        direct_ids = [
            struct.unpack_from("<H", direct.decoded_data, index * 64 + 0x20)[0]
            for index in range(direct.header.record_count)
        ]
        direct_counts = {value: direct_ids.count(value) for value in set(direct_ids)}
        for index, active_test_id in enumerate(direct_ids):
            raw = direct.decoded_data[index * 64 : (index + 1) * 64]
            name_index = struct.unpack_from("<I", raw, 0x0C)[0]
            name = strings.get_string(name_index) or ""
            if direct_counts[active_test_id] != 1:
                rows.append({
                    "id": active_test_id,
                    "record": index,
                    "name": name,
                    "kind": "direct",
                    "execution": "unresolved_static_plan",
                    "error": f"duplicate direct Active Test ID resolves {direct_counts[active_test_id]} rows",
                })
                continue
            try:
                db_obj, selected_db_path, selected = _direct_active_test_selected_row(
                    parser, category, db_root, active_test_id, strings
                )
                executor = _direct_active_test_executor_plan(
                    parser, master, category, db_obj, selected_db_path, selected
                )
                signal_info = None
                if signal_info_enabled:
                    resolved_info = _direct_active_test_signal_info(db_obj, selected_db_path, selected, strings)
                    signal_info = {
                        "physical": {
                            key: value for key, value in resolved_info["physical"].items()
                            if key not in {"record", "raw", "unit_record"}
                        },
                        "choices": [
                            {"value": row["value"], "text": row["text"]}
                            for row in resolved_info["display_info"]
                        ],
                        "pattern": {
                            key: value for key, value in resolved_info["active_test_pattern"].items()
                            if key not in {"record", "raw"}
                        },
                        "engineering_to_raw": {
                            "formula": "raw8 = trunc_toward_zero((value_integer - offset) * div / mul) & 0xFF",
                            "value_integer": "engineering display value scaled by 10^decimal_point_count",
                            "source": "CommandDataLib.dll CStartActTstSnd::SetValue",
                        },
                    }
                compact = _compact_direct_active_test(
                    selected, executor, monitor_rows, init_frame, signal_info=signal_info
                )
                if support_mode == "p6-standard":
                    compact["support_gate"] = {
                        "family": "p6",
                        "mode": "p6-standard",
                        "kind": "did",
                        "identifier": int(selected["initial_read_did"]),
                        "inventory": "selector 0xC8: A100/A1nn enabled-DID list",
                        "length_probe": "selector 0xCA: 22 <DID>; N = received_length - 3",
                    }
                multi_section = db_obj.sections.get(33)
                if multi_section is not None and multi_section.decoded_record_size == 12:
                    group_ids = {
                        struct.unpack_from("<H", multi_section.decoded_data, row_index * 12)[0]
                        for row_index in range(multi_section.header.record_count)
                    }
                    if int(selected["active_test_id"]) in group_ids:
                        compact["multi_control_group"] = True
                        compact["reason"] = (
                            "selected Active-Test ID is a type-33 group parent; current GTS enters the multi composer"
                        )
                rows.append(compact)
            except ValueError as exc:
                rows.append({
                    "id": active_test_id,
                    "record": index,
                    "name": name,
                    "kind": "direct",
                    "execution": "unresolved_static_plan",
                    "error": str(exc),
                })
    routine = db.sections.get(71)
    if routine is not None:
        if routine.decoded_record_size != 72:
            raise ValueError(f"{db_path.name}: type-71 record size {routine.decoded_record_size}, expected 72")
        routine_ids = [
            struct.unpack_from("<H", routine.decoded_data, index * 72 + 0x1E)[0]
            for index in range(routine.header.record_count)
        ]
        routine_counts = {value: routine_ids.count(value) for value in set(routine_ids)}
        for index, active_test_id in enumerate(routine_ids):
            raw = routine.decoded_data[index * 72 : (index + 1) * 72]
            name_index = struct.unpack_from("<I", raw, 0x08)[0]
            name = strings.get_string(name_index) or ""
            routine_id = struct.unpack_from("<H", raw, 0x1C)[0]
            if routine_counts[active_test_id] != 1:
                rows.append({
                    "id": active_test_id,
                    "record": index,
                    "name": name,
                    "kind": "routine",
                    "routine_id": routine_id,
                    "execution": "unresolved_static_plan",
                    "error": f"duplicate routine Active Test ID resolves {routine_counts[active_test_id]} rows",
                })
                continue
            _, _, selected = _routine_active_test_selected_row(parser, category, db_root, active_test_id, strings)
            try:
                executor = _routine_active_test_executor_plan(parser, master, category, selected)
                compact = _compact_routine_active_test(selected, executor)
                if support_mode == "p6-standard":
                    compact["support_gate"] = {
                        "family": "p6",
                        "mode": "p6-standard",
                        "kind": "rid",
                        "identifier": int(selected["routine_id"]),
                        "inventory": "selector 0xCC: D100/D1nn enabled-RID list",
                    }
                rows.append(compact)
            except ValueError as exc:
                rows.append({
                    "id": active_test_id,
                    "record": index,
                    "name": name,
                    "kind": "routine",
                    "routine_id": routine_id,
                    "execution": "unresolved_static_plan",
                    "error": str(exc),
                })
    return sorted(rows, key=lambda row: (int(row["id"]), row["kind"]))


def _registry_source_key(path: Path, gts_root: Path) -> str:
    """Return a checkout-independent logical identity for a registry source."""
    resolved = path.resolve()
    normalized_gts = gts_root.resolve()
    normalized_repo = REPO_ROOT.resolve()
    if resolved.is_relative_to(normalized_gts):
        return f"gtsplus/{resolved.relative_to(normalized_gts).as_posix()}"
    if resolved.is_relative_to(normalized_repo):
        return resolved.relative_to(normalized_repo).as_posix()
    raise ValueError(f"registry source is outside the repository/GTS+ roots: {resolved}")


REGISTRY_FUNCTION_NAME_BOUNDARY = (
    "current master type-26/type-27 rows for the Camry P5 categories carry string index 0: "
    "function/detail keys, ordering, and membership are recovered, OEM function names are not"
)


def _registry_role_bindings(
    parser: DDBParser,
    master: Any,
    category: dict[str, Any],
    bin_root: Path,
) -> list[dict[str, Any]]:
    """Category plugin bindings; semantic kind only where the exact plugin identity is recovered."""
    category_id = int(category["category_id"])
    bindings = []
    for entry in sorted(
        (row for row in parser.extract_master_dlls(master.sections[19]) if row.category_id == category_id),
        key=lambda row: (row.dll_role_id, row.dll_name.casefold()),
    ):
        plugin_path = bin_root / entry.dll_name
        profile_name, _, status = _semantic_profile_for_plugin(plugin_path, entry.dll_role_id)
        semantic_kind = _semantic_kind_for_profile(profile_name)
        if semantic_kind is None and plugin_path.is_file():
            p6_kind = P6_ACTIVE_TEST_PLUGIN_KINDS.get((entry.dll_role_id, _file_sha256(plugin_path)))
            if p6_kind is not None:
                semantic_kind = p6_kind
                status = "exact_plugin_identity"
        bindings.append({
            "role": entry.dll_role_id,
            "dll": entry.dll_name,
            "semantic_kind": semantic_kind,
            "semantic_status": status,
        })
    return bindings


def _registry_selector_rows(parser: DDBParser, master: Any, category_id: int) -> list[dict[str, Any]]:
    """Every resolved (selector -> CommSet/CommFrame/send/mask/check) row for one category."""
    rows = _master_frame_rows(parser, master, category_id)
    return [
        {
            "selector": row["selector"],
            "frame": row["comm_frame_id"],
            "comm_set": row["comm_set"],
            "send": row["send"]["bytes"],
            "mask": row["receive_mask"]["bytes"],
            "check": row["receive_check"]["bytes"],
        }
        for row in sorted(rows, key=lambda row: (int(row["selector"], 16), row["comm_frame_id"]))
    ]


def _registry_function_hierarchy(
    parser: DDBParser,
    master: Any,
    strings: StringDataBase,
    category_id: int,
) -> list[dict[str, Any]]:
    """Master type-26 function rows joined with type-27 detail keys per category."""
    detail_ids: dict[int, list[int]] = {}
    for entry in parser.extract_master_function_details(master.sections[27]):
        if entry.category_id == category_id:
            detail_ids.setdefault(entry.function_id, []).append(entry.detail_id)
    return [
        {
            "function_id": entry.function_id,
            "sort_key": entry.sort_key,
            "name": strings.get_string(entry.name_string_index),
            "description": strings.get_string(entry.description_string_index),
            "detail_ids": sorted(detail_ids.get(entry.function_id, [])),
        }
        for entry in sorted(
            (row for row in parser.extract_master_functions(master.sections[26]) if row.category_id == category_id),
            key=lambda row: (row.sort_key, row.function_id),
        )
    ]


def _registry_data_list(db: Any, strings: StringDataBase) -> dict[str, Any]:
    """Data List display order from the consumer-pinned monitor sort key."""
    records: list[Any] = []
    for table in (62, 157):
        section = db.sections.get(table)
        if section is not None:
            records.extend(extract_monitor_records(section))
    def identity(record: Any) -> tuple[Any, ...]:
        return (
            strings.get_string(record.name_string_index),
            record.primary_did,
            record.alternate_did,
            record.bit_start,
            record.bit_end,
        )

    by_identity: dict[tuple[Any, ...], Any] = {}
    for record in sorted(records, key=lambda record: (record.sort_key, record.table, record.index)):
        by_identity.setdefault(identity(record), record)
    ordered = sorted(by_identity.values(), key=lambda record: (record.sort_key, record.table, record.index))
    return {
        "tables": sorted({record.table for record in records}),
        "record_counts": {
            str(table): sum(1 for record in records if record.table == table)
            for table in sorted({record.table for record in records})
        },
        "row_count": len(ordered),
        "display_order": (
            "type-62/157 sort key (u16 record +0x30, +0x10 on 80-byte rows), then table/record; "
            "rows deduplicated by (name, did, alternate did, bit range), lowest ordering wins"
        ),
        "rows": [
            {
                "monitor_key": record.monitor_key,
                "sort_key": record.sort_key,
                "did": f"0x{record.primary_did:04X}",
                "bit_start": record.bit_start,
                "bit_end": record.bit_end,
                "name": strings.get_string(record.name_string_index) or "",
            }
            for record in ordered
        ],
    }


def _registry_active_test_groups(
    parser: DDBParser,
    category: dict[str, Any],
    db_root: Path,
    strings: StringDataBase,
) -> dict[str, Any]:
    """Compact current type-33 multi-control geometry plus composer executability."""
    plan = _multi_active_test_category_plan(parser, category, db_root)
    groups = []
    for group in plan["groups"]:
        parent = _direct_active_test_selected_row(
            parser, category, db_root, int(group["group_id"]), strings
        )[2]
        member_inputs = []
        member_dids = []
        input_slots = []
        for membership in group["members"]:
            selected = _direct_active_test_selected_row(
                parser, category, db_root, int(membership["member_active_test_id"]), strings
            )[2]
            did = int(selected["initial_read_did"])
            slot = int(membership["input_slot"])
            member_dids.append(did)
            input_slots.append(slot)
            member_inputs.append({
                "active_test_id": int(membership["member_active_test_id"]),
                "input_slot": slot,
                "did": did,
                "bit_start": int(selected["bit_start"]),
                "bit_end": int(selected["bit_end"]),
                "name": selected.get("name") or "",
            })
        same_did = len(set(member_dids)) == 1
        slots_valid = len(set(input_slots)) == len(input_slots) and all(slot in {1, 2} for slot in input_slots)
        composable = bool(member_inputs) and same_did and slots_valid
        reason = None
        if not same_did:
            reason = (
                "current DataMonitorPhase5 multi composer ORs member frames and rejects when DID bytes differ"
            )
        elif not slots_valid:
            reason = "current type-33 input slots are not a unique subset of {1,2}"
        groups.append({
            "group_id": int(group["group_id"]),
            "name": parent.get("name") or "",
            "members": [row["active_test_id"] for row in member_inputs],
            "member_inputs": member_inputs,
            "did": member_dids[0] if same_did and member_dids else None,
            "composer": "or_member_start_stop_frames",
            "execution": "materializable" if composable else "blocked",
            "reason": reason,
        })
    return {
        "group_count": plan["group_count"],
        "membership_count": plan["membership_count"],
        "materializable_group_count": sum(group["execution"] == "materializable" for group in groups),
        "blocked_group_count": sum(group["execution"] == "blocked" for group in groups),
        "groups": groups,
        "boundary": (
            "current DataMonitorPhase5 FUN_10014440 materializes each type-33 member through the ordinary "
            "direct executor, OR-composes complete start/stop frames, and requires all member DID bytes to match"
            if groups
            else "category has no type-33 multi-control membership rows"
        ),
    }


def _registry_request_from_frame(row: dict[str, Any], name: str) -> dict[str, Any]:
    comm_set = row["comm_set_metadata"]
    return {
        "name": name,
        "selector": row["selector"],
        "send": row["send"]["bytes"],
        "mask": row["receive_mask"]["bytes"],
        "check": row["receive_check"]["bytes"],
        "comm_set": row["comm_set"],
        "receive_timeout": comm_set["receive_timeout"],
        "retry_count": comm_set["retry_count"],
        "session_requirement": _session_requirement(row["send"]["bytes"]),
        "resolved": True,
    }


def _registry_request_row(
    parser: DDBParser,
    master: Any,
    category_id: int,
    selector: int,
    name: str,
) -> dict[str, Any]:
    matches = _master_frame_rows(parser, master, category_id, selector)
    if len(matches) != 1:
        return {"name": name, "selector": f"0x{selector:X}", "resolved": False}
    return _registry_request_from_frame(matches[0], name)


def _registry_command_rows(
    parser: DDBParser,
    master: Any,
    category: dict[str, Any],
    bin_root: Path,
    bindings: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Wire-request command plans for roles whose exact plugin semantics are recovered."""
    category_id = int(category["category_id"])
    rows: list[dict[str, Any]] = []
    for binding in bindings:
        kind = binding["semantic_kind"]
        if kind is None:
            continue
        _, profile, _ = _semantic_profile_for_plugin(bin_root / binding["dll"], binding["role"])
        if kind == "dtc_clear":
            control_flow = profile["control_flow"]
            timers = [row for row in _master_timer_rows(parser, master, category_id) if row["timer_id"] == 1]
            rows.append({
                "role": binding["role"],
                "kind": kind,
                "requests": [
                    _registry_request_row(parser, master, category_id, 0x1, "primary"),
                    _registry_request_row(parser, master, category_id, 0x102, "fallback"),
                ],
                "timer": {"timer_id": 1, "delay_ms": timers[0]["delay_ms"]} if len(timers) == 1 else None,
                "flow": {
                    "primary_selector": control_flow["primary_selector"],
                    "fallback_selector": control_flow["fallback_selector"],
                    "fallback_error_codes_when_function_gate_set": control_flow["fallback_error_codes_when_function_gate_set"],
                    "success": control_flow["success"],
                },
                "execution": "plan_only",
            })
        elif kind == "generic_cid":
            rows.append({
                "role": binding["role"],
                "kind": kind,
                "requests": [_registry_request_row(parser, master, category_id, 0xDC, "request")],
                "response_model": profile["response_model"],
                "execution": "plan_only",
            })
        elif kind == "p5_active_test_init":
            initial_read = profile["init_model"]["initial_read"]
            rows.append({
                "role": binding["role"],
                "kind": kind,
                "initial_read": {
                    "selector": initial_read["selector"],
                    "base_request": initial_read["base_request"],
                    "did_substitution": (
                        "request bytes 1/2 take the selected type-68 initial-read DID before send; "
                        "per-test requests are on each direct active-test row"
                    ),
                    "positive_check": initial_read["base_positive_check"],
                },
                "execution": "plan_only",
            })

    # Role 0xB5 is a generic/default P5 binding in the current master. CommandExecute's
    # CDbDllTable fallback selects the first role row (category 0) when a current P5
    # category has no exact 0xB5 row. Export only ordinary Toyota P5 here: partner/Hino
    # branches inside the same DLL have distinct orchestration and remain separate work.
    dll_rows = list(parser.extract_master_dlls(master.sections[19]))
    single = support.support_plugin(dll_rows, category_id, 0x67)
    multi = support.support_plugin(dll_rows, category_id, 0xD5)
    family = support.support_family(single, multi)
    mode = support.support_mode(category_id, int(category["generation"]), family)
    ffd_binding = support.support_plugin(dll_rows, category_id, 0xB5)
    if mode == "p5-standard" and ffd_binding is not None and ffd_binding["dll"] == "GetEachFrzFrmDatP5_DT.dll":
        request = _registry_request_row(parser, master, category_id, 0xCF, "all_snapshot_records")
        if request.get("resolved"):
            if request.get("send") != "1904000000ff" or request.get("check") != "5904":
                raise ValueError(
                    f"category {category_id}: selector 0xCF DTC snapshot frame drifted: "
                    f"{request.get('send')} -> {request.get('check')}"
                )
            rows.append({
                "role": 0xB5,
                "kind": "p5_dtc_snapshot",
                "plugin_binding": ffd_binding,
                "requests": [request],
                "request_model": {
                    "service": "0x19",
                    "subfunction": "0x04 reportDTCSnapshotRecordByDTCNumber",
                    "dtc_substitution": "request bytes 2/3/4 take the selected 24-bit DTC",
                    "snapshot_record_number": "0xFF (all snapshot records)",
                },
                "response_model": {
                    "positive_prefix": "5904",
                    "layout_after_prefix": "DTC[3] | status | repeated(snapshot_record:u8 | identifier_count:u8 | repeated(DID:be16 | length:u8 | data[length]))",
                    "dtc_echo_offset": 2,
                    "status_offset": 5,
                    "snapshot_records_offset": 6,
                    "identifier_length_source": "explicit u8 immediately after each DID",
                    "boundary": "raw snapshot DID blocks are exact; signal-level freeze-frame decoding is not projected from Data Monitor metadata",
                },
                "execution": "read_only",
            })

    rob_binding = support.support_plugin(dll_rows, category_id, 0xA0)
    if (mode == "p5-standard" and rob_binding is not None
            and rob_binding["exact_category_binding"] is True
            and rob_binding["dll"] == "GetRoBP5_DT.dll"):
        by_selector = {
            selector: _master_frame_rows(parser, master, category_id, selector)
            for selector in (0xF3, 0xF4, 0xF5)
        }

        def exact_frame(selector: int, send: str, check: str) -> dict[str, Any] | None:
            matches = [
                row for row in by_selector[selector]
                if row["send"]["bytes"] == send and row["receive_check"]["bytes"] == check
            ]
            return matches[0] if len(matches) == 1 else None

        protocols = []
        for base in (0x01, 0x11):
            inventory = exact_frame(0xF3, f"ab{base:02x}", f"eb{base:02x}")
            frames = exact_frame(0xF4, f"ab{base + 1:02x}0000", f"eb{base + 1:02x}")
            record = exact_frame(0xF5, f"ab{base + 2:02x}00000000", f"eb{base + 2:02x}")
            if inventory is None or frames is None or record is None:
                protocols = []
                break
            protocols.append({
                "inventory": _registry_request_from_frame(inventory, "behavior_codes"),
                "frames": {
                    **_registry_request_from_frame(frames, "behavior_frames"),
                    "behavior_substitution": "request bytes 2/3 take behavior_code as big-endian u16",
                },
                "record": {
                    **_registry_request_from_frame(record, "behavior_record"),
                    "behavior_substitution": "request bytes 2/3 take behavior_code as big-endian u16",
                    "frame_substitution": "request bytes 4/5 take frame_id as big-endian u16",
                },
            })
        if len(protocols) == 2:
            rows.append({
                "role": 0xA0,
                "kind": "p5_rob",
                "plugin_binding": rob_binding,
                "protocols": protocols,
                "response_model": {
                    "inventory": {
                        "layout": "EB | inventory_subfunction | repeated(behavior_code:be16)",
                        "payload_offset": 2,
                        "parser": "GetRoBP5_DT FUN_100010C0 computes (received_length-2)/2 and appends each BE16 word",
                    },
                    "frames": {
                        "layout": "EB | frame_subfunction | behavior_echo:be16 | repeated(frame_id:be16)",
                        "payload_offset": 4,
                        "parser": "FUN_100047A0 parses BE16 frame IDs from offset 4, sorts them, and removes duplicates",
                        "echo_validation": "current host does not validate behavior_echo before parsing",
                    },
                    "record": {
                        "layout": "EB | record_subfunction | behavior_echo:be16 | frame_echo:be16 | block_count:u8 | blocks",
                        "payload_offset": 6,
                        "block_count_offset": 6,
                        "count_zero_policy": "FUN_10002A60 derives block count by scanning valid blocks from offset 7 to response end",
                        "block_layout": "DID:be16 | length | data[length]",
                        "length_rule": "DID 0x6000..0x6FFF uses length:be32; every other DID uses length:u8",
                        "echo_validation": "current host does not validate behavior_echo/frame_echo before parsing",
                        "parser": "FUN_100016F0 parses unique DID blocks then passes them to behavior-data conversion",
                    },
                    "endianness": "big",
                    "boundary": "raw RoB inventory/frame/body transport is exact; behavior-record signal conversion/presentation remains separate",
                },
                "execution": "read_only",
            })
    return sorted(rows, key=lambda row: row["role"])


def _session_requirement(send_hex: str) -> str:
    """Classify a request against the recovered P5 first-byte session classifier.

    Request byte 0x01..0x0F is class 1 (default-session path); byte >= 0x10 is
    class 2, which the current-P5 host serves from extended session.
    """
    return "extended" if send_hex[:2].ljust(2, "0") >= "10" else "default"


def _registry_session_control(
    parser: DDBParser,
    master: Any,
    categories: list[dict[str, Any]],
) -> dict[str, Any]:
    """Current-P5 session lifecycle (TMS-077) with per-category resolved frames."""
    lifecycle = _execution_model()["gtsplus_continuity"]["dll_role_schema"]["execution_lifecycle"]
    transport = lifecycle["transport_and_session"]
    auto = transport["p5_automatic_session_judgment"]
    uds2 = auto["uds_class_2"]

    def frame_row(category_id: int, selector: int) -> dict[str, Any] | None:
        matches = _master_frame_rows(parser, master, category_id, selector)
        if len(matches) != 1:
            return None
        row = matches[0]
        return {
            "selector": row["selector"],
            "frame": row["comm_frame_id"],
            "send": row["send"]["bytes"],
            "mask": row["receive_mask"]["bytes"],
            "check": row["receive_check"]["bytes"],
            "comm_set": row["comm_set"],
        }

    per_category = {}
    for category in categories:
        category_id = int(category["category_id"])
        default = frame_row(category_id, 0xD1)
        extended = frame_row(category_id, 0xD2)
        keepalive = frame_row(category_id, 0xDD)
        for row, expected in ((default, "1001"), (extended, "1003"), (keepalive, "22f186")):
            if row is not None and row["send"] != expected:
                raise ValueError(
                    f"category {category_id} session frame {row['selector']} drift: {row['send']} != {expected}"
                )
        per_category[str(category_id)] = {
            "generation_low5": f"0x{int(category['generation']) & 0x1F:02X}",
            "default_session": default,
            "extended_session": extended,
            "keepalive": keepalive,
        }

    judgment = uds2["session_judgment_flag"]
    test_present = transport["test_present"]
    if uds2["phase5_session_sender"]["current_camry_wire_sequence"] != ["10 01", "10 03"]:
        raise ValueError("current-P5 session enter sequence drifted from the pinned wire proof")
    wire_sequence = ["1001", "1003"]
    return {
        "generation": "current-p5",
        "default_session": 1,
        "extended_session": 3,
        "enter_sequence": wire_sequence,
        "return_default": "1001",
        "keepalive": {
            "kind": "session_did_poll",
            "did": "0xF186",
            "request": "22f186",
            "positive_prefix": "62f186",
            "interval_s": round(test_present["cadence_ms"] / 1000, 3),
            "selector": "0xDD",
            "mask": "ff",
            "check": "62",
            "meaning": test_present["meaning"],
            "session_state": transport["session_state"],
        },
        "category_gate": auto["category_gate"],
        "request_classifier": auto["classifier"]["rule"],
        "class_1_default": auto["class_1_default"],
        "class_2_normal_path": uds2["normal_path"],
        "session_judgment_exception": {
            "role": "documentation",
            "runtime_default": False,
            "flag": judgment["field"],
            "setter": judgment["setter"],
            "clearer": judgment["clearer"],
            "behavior": judgment["phase5_alternate_behavior"],
            "external_importers": judgment["external_importers"],
        },
        "eligible_generation_low5": ["0x14", "0x15", "0x16"],
        "per_category": per_category,
        "boundary": (
            "frames are resolved per category from the current master; SendProc itself gates a shared automatic-session "
            "path by CDbEcuCategoryTable/class-0x110 byte +0x48 low5 in 0x14/0x15/0x16. This raw SendProc gate is "
            "not a diagnostic-family classifier: SelectCarTypeVin10 dispatches low5 0x16 to Phase6 and the universal "
            "P5 runtime instead follows GetSupportP5_DT bindings. The former local "
            "wire_proven_categories subset is intentionally absent: it was an independent-tooling policy, not "
            "Toyota resolver semantics. session_judgment_exception is documentation, not a runtime default"
        ),
    }


def _registry_vehicle_resolver(region: str) -> dict[str, Any]:
    """Portable clean subset of Toyota's independently verified current resolver artifact."""
    resolver = json.loads(VEHICLE_RESOLVER.read_text())
    if resolver.get("schema") != "gtsplus-current-vehicle-resolver-v1" or resolver.get("release") != "2026.03.002.02":
        raise ValueError("current vehicle resolver artifact identity drift")
    witness = resolver["regions"][region]["camry_hv_witness"]
    if witness.get("vehicle_type") != 12704 or witness.get("vehicle_name") != "Camry HV":
        raise ValueError(f"{region}: Camry-HV resolver witness unavailable")

    vin_rows = []
    for value in witness["vin_rows"]:
        raw = bytes.fromhex(value)
        vin_rows.append({
            "flags": struct.unpack_from("<I", raw, 0x00)[0],
            "vehicle_type": struct.unpack_from("<H", raw, 0x0E)[0],
            "category_id": struct.unpack_from("<H", raw, 0x10)[0],
            "phase_type": raw[0x12],
            "vin_prefix_hex": raw[0x13:0x1E].hex(),
        })

    candidates = [dict(row) for row in witness["mount_candidates"]]
    if len(candidates) != int(witness["mount_candidate_count"]) or any(not row.get("transport_route") for row in candidates):
        raise ValueError(f"{region}: Toyota transport route missing from Camry mount candidate")

    return {
        "generation": "current-gtsplus-vehicle-resolver-v2",
        "vehicle_type": witness["vehicle_type"],
        "vehicle_name": witness["vehicle_name"],
        "vin_decision": {
            "source_category_id": 372,
            "key": "category_id + phase_type + VIN[0:11], with flags bits 0..10 as per-position wildcards",
            "rows": vin_rows,
        },
        "install_set_ids": witness["install_set_ids"],
        "mount": {
            "algorithm": "GetMountEcuListNoCnfm/CEcuConnectCheck::CommConnectionNoBuffer",
            "candidate_count": witness["mount_candidate_count"],
            "candidates": candidates,
            "connection_profiles": witness["connection_profiles"],
            "frame_0": witness["connection_frame_witness"],
            "comm_set_9": witness["connection_comm_set_witness"],
            "transport_route": resolver["mounted_ecu"]["transport_route"],
            "route_boundary": (
                "transport_route is resolved exclusively from Toyota CDbProtInfoTable class 0x10D using the same "
                "category+phase key as CCommFrameCtrl::GetEcuAddr. Maintained-profile request addresses are not "
                "consulted. Shared request ID 0x750 remains category-specific through Toyota's address-extension field"
            ),
        },
        "p5_support": resolver["p5_support"],
        "boundary": resolver["boundary"],
    }


def _registry_utilities(parser: DDBParser, master: Any) -> dict[str, Any]:
    """Compact runtime utility surface over the already-recovered generic families."""
    generic_roles = _execution_model()["gtsplus_continuity"]["dll_role_schema"]["execution_lifecycle"][
        "transport_and_session"
    ]["generic_roles"]
    bindings = []
    by_role: dict[int, list[str]] = {}
    for entry in parser.extract_master_dlls(master.sections[19]):
        if entry.category_id == 0:
            by_role.setdefault(entry.dll_role_id, []).append(entry.dll_name)
    for role in sorted(GENERIC_UTILITY_ROLE_KINDS):
        dlls = sorted(set(by_role.get(role, [])))
        if len(dlls) != 1:
            raise ValueError(f"generic utility role 0x{role:X} resolved {len(dlls)} master bindings: {dlls}")
        pinned = generic_roles.get(f"0x{role:X}")
        if pinned is not None and pinned["plugin"] != dlls[0]:
            raise ValueError(
                f"generic utility role 0x{role:X} drift: master {dlls[0]} vs execution model {pinned['plugin']}"
            )
        bindings.append({"role": role, "dll": dlls[0], "semantic_kind": GENERIC_UTILITY_ROLE_KINDS[role]})
    return {
        "scope": (
            "recovered generic (category-0) command families only; every other generic role is "
            "intentionally absent rather than classified"
        ),
        "bindings": bindings,
        "routine_control": {
            "service": "0x31",
            "positive_response": "0x71",
            "start_selector": "0xD5",
            "stop_selector": "0xD6",
            "result_selector": "0xD7",
            "session_requirement": "extended",
            "request_template": (
                "31 <01 start|02 stop|03 result> FF FF; template bytes 2/3 are replaced by the "
                "selected type-71 routine ID; per-category frames are in catalogs.<id>.selectors"
            ),
        },
        "io_control": {
            "service": "0x2F",
            "positive_response": "0x6F",
            "start_selector": "0x9D",
            "stop_selector": "0x64",
            "session_requirement": "extended",
            "request_template": (
                "2F FF FF <03 shortTermAdjustment|00 returnControlToECU>; template bytes 1/2 are "
                "replaced by the control DID; the trailing value/control-enable payload length is "
                "runtime DataIdLengthList state"
            ),
        },
        "utility_list_source": (
            "per-ECU supported-function menu is catalogs.<id>.functions (master type-26/27 via "
            "GetEcuFuncList role 0x4); names are not recovered for these categories"
        ),
        "boundary": (
            "list/plan surface only; no execution authorization, SecurityAccess, session escalation, "
            "flash, or write workflow is included"
        ),
    }


def build_toyota_diag_registry(gts_root: Path, region: str = "NA", family: str = "Gen") -> dict[str, Any]:
    gts_root = resolve_gts_root(gts_root)
    db_root = gts_db_root(gts_root, region, family)
    parser = DDBParser()
    master_path = db_root / "Toyota.ddb"
    master = parser.parse_master_db(master_path)
    strings_path = db_root / "M_English.ddb"
    strings = _english_strings(parser, db_root)
    dtc_clear_path = REPO_ROOT / "data/generated/camry_2026_dtc_clear.json"
    dtc_clear = json.loads(dtc_clear_path.read_text())
    nrtd_p5_path = REPO_ROOT / "data/generated/camry_2026_nrtd_p5.json"
    nrtd_p5 = json.loads(nrtd_p5_path.read_text())
    eps_identity_path = REPO_ROOT / "targets/camry-2026/raw-20260826/identity.json"
    eps_identity = json.loads(eps_identity_path.read_text())

    profile = json.loads(json.dumps(CAMRY_2026_DIAG_PROFILE))
    known_categories = sorted({
        int(ecu["category_id"])
        for ecu in profile["ecus"]
        if "category_id" in ecu
    })
    catalogs: dict[str, Any] = {}
    source_files = [master_path, strings_path, dtc_clear_path, nrtd_p5_path, eps_identity_path, EXECUTION_MODEL, VEHICLE_RESOLVER]
    bin_root = gts_root / "bin"
    resolved_categories = []
    for category_id in known_categories:
        category = _resolve_master_category(parser, master, strings, str(category_id))
        resolved_categories.append(category)
        db_path = db_root / str(category["database"])
        db = parser.parse_ecu_db(db_path)
        source_files.append(db_path)
        monitor_rows = _monitor_rows(db, strings, db_path.name)
        bindings = _registry_role_bindings(parser, master, category, bin_root)
        catalogs[str(category_id)] = {
            "category": category,
            "dids": _registry_did_catalog(monitor_rows),
            "dtcs": _registry_dtc_catalog(parser, db, strings, db_path.name),
            "active_tests": _registry_active_tests(parser, master, category, db_root, strings, monitor_rows, bindings),
            "functions": _registry_function_hierarchy(parser, master, strings, category_id),
            "plugins": bindings,
            "commands": _registry_command_rows(parser, master, category, bin_root, bindings),
            "selectors": _registry_selector_rows(parser, master, category_id),
            "data_list": _registry_data_list(db, strings),
            "generic_ffd": _generic_ffd_rows(
            db, strings, db_path.name,
            resolve_variable=lambda variable_id: bytes.fromhex(_master_variable(master, variable_id)["bytes"]),
        ),
            "rob": _rob_rows(db, strings, db_path.name),
            "active_test_groups": _registry_active_test_groups(parser, category, db_root, strings),
        }
    profile["catalog_category_ids"] = known_categories
    profile["session_control"] = _registry_session_control(parser, master, resolved_categories)
    profile["vehicle_resolution"] = _registry_vehicle_resolver(region)

    referenced_comm_sets = {
        int(row["comm_set"])
        for catalog in catalogs.values()
        for row in catalog["selectors"]
    }
    for session_row in profile["session_control"]["per_category"].values():
        for frame_key in ("default_session", "extended_session", "keepalive"):
            frame = session_row[frame_key]
            if frame is not None:
                referenced_comm_sets.add(int(frame["comm_set"]))
    referenced_comm_sets.add(int(profile["vehicle_resolution"]["mount"]["comm_set_9"]["comm_set_id"]))
    referenced_comm_sets = sorted(referenced_comm_sets)
    commsets = {}
    for row in _master_comm_set_rows(parser, master):
        if row["comm_set_id"] not in referenced_comm_sets:
            continue
        commsets[str(row["comm_set_id"])] = {
            "send_parameter": row["send_parameter"],
            "receive_timeout": row["receive_timeout"],
            "retry_count": row["retry_count"],
            "exception_handler_id": row["exception_handler_id"],
            "exception_handler_flag": row["exception_handler_flag"],
        }
    if sorted(int(key) for key in commsets) != referenced_comm_sets:
        raise ValueError("referenced CommSet ids did not all resolve in the master table")

    mode04 = dtc_clear["legislated_obd"]
    profile["dtc_clear"] = {
        "physical_uds14": dtc_clear["physical_uds14"],
        "functional_obd": {
            "request_id": int(mode04["request_id"], 16),
            "mode04_request": mode04["mode04_clear_request_frame"],
            "positive_prefix": "0144",
            "expected_responders": sorted(int(value, 16) for value in mode04["mode04_positive_responses"]),
        },
        "boundary": dtc_clear["boundary"],
    }
    profile["catalog_category_ids"] = known_categories

    topology_rows = _master_canbus_topology_rows(parser, master, strings, "12704")
    if len(topology_rows) != 1:
        raise ValueError("Camry HV CAN topology cardinality drift")
    topology = topology_rows[0]
    if topology["vehicle_name"] != "Camry HV":
        raise ValueError("Camry HV CAN topology name drift")
    if topology["option_count"] != 18 or topology["placement_variant_count"] != 1:
        raise ValueError("Camry HV CAN topology option/variant drift")
    profile["gts_can_topology"] = {
        **topology,
        "namespace_boundary": "Toyota GTS Bus N names are vehicle-network domains, not Panda logical bus numbers; current post-repin diagnostics use Panda bus0",
    }

    observed_identities = _registry_nrtd_observed_identities(nrtd_p5)
    observed_identities["eps"] = _registry_eps_observed_identity(eps_identity)
    for ecu in profile["ecus"]:
        identity = observed_identities.get(ecu["key"])
        if identity is not None:
            ecu["observed_identity"] = identity

    return {
        "schema": "toyota-diagnostics-registry-v6",
        "profile": profile,
        "decoders": {
            "p5-linear-msb0-v1": {
                "payload_origin": "UDS DID value bytes (positive SID/DID echo excluded)",
                "bit_numbering": "msb0",
                "byte_order": "big-endian",
                "bit_range": "inclusive",
                "sign": "unsigned unless signal.signed; signed values use two's-complement at signal bit width",
                "integer_formula": "trunc_toward_zero(signed_raw * mul / div) + offset",
                "display_formula": "converted_integer / 10^decimal_point_count",
                "pattern_lookup": "match converted_integer before decimal rendering",
            }
        },
        "commsets": {
            "boundary": (
                "receive_timeout feeds CheckAndConvertRcvTimeOut before Receive; retry_count bounds "
                "retransmission attempts; send_parameter reaches SendInt argument 4, which the common "
                "CAN SendProc does not consume"
            ),
            "rows": commsets,
        },
        "utilities": _registry_utilities(parser, master),
        "function_names": REGISTRY_FUNCTION_NAME_BOUNDARY,
        "catalogs": catalogs,
        "source_identity": {
            key: {
                "bytes": path.stat().st_size,
                "sha256": _file_sha256(path),
            }
            for key, path in sorted(
                ((_registry_source_key(path, gts_root), path) for path in set(source_files)),
                key=lambda item: item[0],
            )
        },
        "boundary": (
            "Clean derived diagnostic metadata only: no Toyota binaries are embedded. Active Tests are static plans; "
            "execution=executable only means the fixed request geometry is complete, not that the registry authorizes "
            "execution: it intentionally contains no execution authorization, session escalation, SecurityAccess, "
            "flash, or write workflow."
        ),
    }
