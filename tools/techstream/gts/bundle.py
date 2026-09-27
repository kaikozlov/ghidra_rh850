"""toyota-current universal regional diagnostic bundle: regional resolver index, catalog shards, deterministic ZIP assembly (ProcessPool over regions)."""

from __future__ import annotations

import json
import struct
import tempfile
import zipfile
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
from typing import Any

from tools import REPO_ROOT
from tools.techstream.gts.ddb import _english_strings, _generic_ffd_rows, _monitor_rows, _rob_rows
from tools.techstream.ddb_semantics import records as ddb_records
from tools.techstream.gts.execution_model import EXECUTION_MODEL, VEHICLE_RESOLVER, _execution_model, _file_sha256
from tools.techstream.gts.registry import (
    REGISTRY_FUNCTION_NAME_BOUNDARY,
    _registry_active_test_groups,
    _registry_active_tests,
    _registry_command_rows,
    _registry_data_list,
    _registry_did_catalog,
    _registry_dtc_catalog,
    _registry_function_hierarchy,
    _registry_role_bindings,
    _registry_selector_rows,
    _registry_utilities,
)
from tools.techstream.gts.master import (
    _master_category_rows,
    _master_comm_set_rows,
    _master_frame_rows,
    _master_variable,
)
from tools.techstream.parse_ddb import DDBParser, StringDataBase
from tools.techstream.gts import support
from tools.techstream.techstream_paths import gts_db_root


TOYOTA_DIAG_BUNDLE_SCHEMA = "toyota-diagnostics-bundle-v2"
TOYOTA_DIAG_BUNDLE_PROFILE = "toyota-current"
TOYOTA_DIAG_BUNDLE_REGIONS = ("NA", "EU", "JP")

_PHASE3_SELECTORS = ((0x1B, 9), (0x1C, 5), (0x1D, 4), (0x1E, 3), (0x1F, 2), (0x20, 2),
                     (0x21, 2), (0x22, 8), (0x23, 1), (0x24, 1), (0x25, 1), (0x26, 6), (0x27, 7))
_PHASE4_SELECTORS = ((0x28, 1), (0x29, 1), (0x2A, 1), (0x2B, 1), (0x2C, 1), (0x2D, 1),
                     (0x2E, 1), (0x2F, 2), (0x30, 2), (0x31, 2), (0x32, 2), (0x33, 2),
                     (0x34, 2), (0x36, 3), (0x37, 4), (0x38, 5), (0x35, 6), (0x39, 10))


def _bundle_transport_semantics(phase_type: int, request_address: int, functional_address: int) -> dict[str, Any]:
    """Recover the transport controller selected by CCommFrameCtrl::ChangeCommIF.

    ChangeCommIF switches on the low nibble of phase type. Current P5 phases ending
    in 2 use the ISO15765 family; 0x18/0x38 select CCommCtrlISO15765_29BitCan;
    0x78/0x88 select the CAN-FD ISO15765 PS controller; low-nibble 4 selects
    CCommCtrlISO13400_NDIS. Keep unrecovered cases explicit rather than projecting
    the transport implemented by our consumer onto Toyota's route.
    """
    low = phase_type & 0x0F
    out: dict[str, Any] = {
        "change_comm_if_case": low,
        "request_address_field": request_address,
        "functional_address_field": functional_address,
    }
    if phase_type in {0x18, 0x38}:
        tx = 0x18DA0000 | ((request_address & 0xFF) << 8) | 0xF1
        out.update({
            "transport_kind": "iso15765-29bit-normal-fixed",
            "controller": "CCommCtrlISO15765_29BitCan",
            "physical_request_address": tx,
            "physical_response_address": (tx & 0xFFFF0000) | ((tx << 8) & 0xFF00) | ((tx >> 8) & 0xFF),
            "functional_request_address": (0x18DB0000 | ((functional_address & 0xFF) << 8) | 0xF1)
            if functional_address else None,
            "request_address_field_semantics": "target-address byte (TA); physical normal-fixed request is 0x18DA<ta>F1",
        })
    elif phase_type in {0x78, 0x88}:
        out.update({
            "transport_kind": "canfd-iso15765-ps",
            "controller": "CCommCtrl_FD_ISO15765_PS",
            "physical_request_address": None,
            "physical_response_address": None,
            "functional_request_address": None,
            "request_address_field_semantics": "controller-specific; full wire address not projected by this extractor",
        })
    elif low == 0x02:
        out.update({
            "transport_kind": "iso15765-phase-family",
            "controller": "CCommCtrlISO15765 family (generation/mode subdispatch)",
            "physical_request_address": request_address,
            "physical_response_address": request_address + 8 if request_address < 0xFFF8 else None,
            "functional_request_address": None,
            "request_address_field_semantics": "CAN request ID for the current Toyota P5 routes",
        })
    elif low == 0x04:
        out.update({
            "transport_kind": "iso13400-ndis",
            "controller": "CCommCtrlISO13400_NDIS",
            "physical_request_address": None,
            "physical_response_address": None,
            "functional_request_address": None,
            "request_address_field_semantics": "ISO13400 logical route; not a CAN arbitration ID",
        })
    elif low == 0x03:
        out.update({
            "transport_kind": "direct-can",
            "controller": "CCommCtrlDirectCan",
            "physical_request_address": request_address,
            "physical_response_address": None,
            "functional_request_address": None,
            "request_address_field_semantics": "direct CAN route",
        })
    else:
        out.update({
            "transport_kind": f"change-comm-if-case-{low}-unrecovered",
            "controller": None,
            "physical_request_address": None,
            "physical_response_address": None,
            "functional_request_address": None,
            "request_address_field_semantics": "transport controller semantics not yet recovered",
        })
    return out


def _bundle_protocol_route(master: Any, category_id: int, phase_type: int) -> dict[str, Any]:
    """Materialize Toyota's class-0x10D route and recovered transport interpretation."""
    matches = [
        raw for raw in ddb_records(master.sections[13])
        if struct.unpack_from("<H", raw, 0x00)[0] == category_id and raw[0x18] == phase_type
    ]
    if len(matches) != 1:
        raise ValueError(
            f"CDbProtInfo category {category_id} phase 0x{phase_type:02X} resolved {len(matches)} rows"
        )
    raw = matches[0]
    if len(raw) != 28:
        raise ValueError(f"CDbProtInfo row size drift: {len(raw)}")
    request_address = struct.unpack_from("<H", raw, 0x08)[0]
    functional_address = struct.unpack_from("<H", raw, 0x06)[0]
    return {
        "protocol_info_id": struct.unpack_from("<H", raw, 0x02)[0],
        "functional_address": functional_address,
        "request_address": request_address,
        "address_extension": raw[0x0A],
        "request_mask": struct.unpack_from("<H", raw, 0x0E)[0],
        "response_mask": struct.unpack_from("<H", raw, 0x10)[0],
        "legislated_request_address": struct.unpack_from("<H", raw, 0x14)[0],
        "phase_type": raw[0x18],
        **_bundle_transport_semantics(raw[0x18], request_address, functional_address),
    }


def _bundle_connection_frame(master: Any, frame_id: int) -> dict[str, Any]:
    matches = [raw for raw in ddb_records(master.sections[17]) if struct.unpack_from("<H", raw, 0)[0] == frame_id]
    if len(matches) != 1:
        raise ValueError(f"CDbCommFrame {frame_id} resolved {len(matches)} rows")
    raw = matches[0]
    send_var, mask_var, check_var = struct.unpack_from("<HHH", raw, 2)
    return {
        "frame_id": frame_id,
        "send": _master_variable(master, send_var)["bytes"],
        "mask": _master_variable(master, mask_var)["bytes"],
        "check": _master_variable(master, check_var)["bytes"],
    }


def _bundle_can_topologies(parser: DDBParser, master: Any, strings: Any, vehicle_types: set[int]) -> dict[str, list[dict[str, Any]]]:
    """Batch the existing CAN Bus Check join so the runtime never needs Toyota DDB files."""
    required = (55, 75, 76, 77, 78, 79)
    if any(table_id not in master.sections for table_id in required):
        return {}

    vehicle_names = {
        struct.unpack_from("<I", raw, 4)[0]: strings.get_string(struct.unpack_from("<I", raw, 0)[0]) or ""
        for raw in ddb_records(master.sections[43])
    }
    car_by_vehicle: dict[int, list[bytes]] = {}
    for raw in ddb_records(master.sections[75]):
        car_by_vehicle.setdefault(struct.unpack_from("<I", raw, 4)[0], []).append(raw)
    options_by_car: dict[int, list[bytes]] = {}
    for raw in ddb_records(master.sections[77]):
        options_by_car.setdefault(struct.unpack_from("<I", raw, 0)[0], []).append(raw)
    components_by_group: dict[int, list[bytes]] = {}
    for raw in ddb_records(master.sections[78]):
        components_by_group.setdefault(struct.unpack_from("<I", raw, 0)[0], []).append(raw)
    subbus_names = {
        struct.unpack_from("<I", raw, 0)[0]: strings.get_string(struct.unpack_from("<I", raw, 4)[0]) or ""
        for raw in ddb_records(master.sections[76])
    }
    bus_names = {
        struct.unpack_from("<I", raw, 8)[0]: strings.get_string(struct.unpack_from("<I", raw, 4)[0]) or ""
        for raw in ddb_records(master.sections[79])
    }
    gateway_names: dict[int, set[str]] = {}
    for raw in ddb_records(master.sections[55]):
        bus_index = struct.unpack_from("<H", raw, 8)[0]
        gateway_names.setdefault(bus_index, set()).add(strings.get_string(struct.unpack_from("<I", raw, 4)[0]) or "")

    out: dict[str, list[dict[str, Any]]] = {}
    for vehicle_type in sorted(vehicle_types):
        rows = []
        for car_raw in car_by_vehicle.get(vehicle_type, []):
            car_id = struct.unpack_from("<I", car_raw, 0)[0]
            options = options_by_car.get(car_id, [])
            placement_variants: dict[tuple[Any, ...], dict[str, Any]] = {}
            for option in options:
                group = struct.unpack_from("<I", option, 44)[0]
                placements = []
                shape = []
                for raw in sorted(components_by_group.get(group, []), key=lambda item: (struct.unpack_from("<H", item, 8)[0], item[14])):
                    bus_index = struct.unpack_from("<H", raw, 8)[0]
                    component_index = raw[14]
                    domain = subbus_names.get(component_index + 1, "")
                    row = {
                        "component_index": component_index,
                        "component_hex": f"0x{component_index:02X}",
                        "ecu_domain": domain,
                        "bus_index": bus_index,
                        "bus_name": bus_names.get(bus_index, f"BusIndex {bus_index}"),
                        "gateway_names": sorted(x for x in gateway_names.get(bus_index, set()) if x),
                        "junction_name": strings.get_string(struct.unpack_from("<I", raw, 4)[0]) or "",
                    }
                    placements.append(row)
                    shape.append((component_index, domain, bus_index, row["bus_name"]))
                shape_key = tuple(shape)
                if shape_key not in placement_variants:
                    placement_variants[shape_key] = {
                        "component_groups": [f"0x{group:08X}"],
                        "placements": placements,
                    }
                else:
                    placement_variants[shape_key]["component_groups"].append(f"0x{group:08X}")
            rows.append({
                "vehicle_type": vehicle_type,
                "vehicle_name": vehicle_names.get(vehicle_type, ""),
                "can_bus_car_id": f"0x{car_id:08X}",
                "option_count": len(options),
                "placement_variant_count": len(placement_variants),
                "placement_variants": list(placement_variants.values()),
            })
        if rows:
            out[str(vehicle_type)] = rows
    return out


def _bundle_vehicle_decision_rows(master: Any) -> list[dict[str, Any]]:
    """Serialize type-41 semantics as clean criteria instead of opaque DDB records."""
    out = []
    for raw in ddb_records(master.sections[41]):
        if len(raw) != 52:
            raise ValueError(f"type-41 row size drift: {len(raw)}")
        flags = struct.unpack_from("<I", raw, 0x24)[0]
        out.append({
            "category_id": struct.unpack_from("<H", raw, 0x00)[0],
            "phase_type": raw[0x02],
            "flags": flags,
            "text_criteria": [
                {"value_hex": raw[0x03:0x0A].hex(), "length": raw[0x0A], "operator": raw[0x0B]},
                {"value_hex": raw[0x0C:0x12].hex(), "length": raw[0x12], "operator": raw[0x13]},
            ],
            "scalar_criteria": [
                {"value": raw[0x14], "operator": raw[0x15]},
                {"value": raw[0x16], "operator": raw[0x17]},
                {"value": raw[0x18], "operator": raw[0x19]},
                {"value": raw[0x1A], "operator": raw[0x1B]},
                {"value": raw[0x1C], "operator": raw[0x1D]},
                # Current DecisionKey uses the same operator byte at +0x1D for the +0x1E criterion.
                {"value": raw[0x1E], "operator": raw[0x1D]},
                {"value": raw[0x20], "operator": raw[0x21]},
                {"value": raw[0x22], "operator": raw[0x23]},
            ],
            "new_fields": [struct.unpack_from("<H", raw, off)[0] for off in (0x28, 0x2A, 0x2C, 0x2E)],
            "field_30": struct.unpack_from("<H", raw, 0x30)[0],
            "vehicle_type": struct.unpack_from("<H", raw, 0x32)[0],
        })
    return out


def _bundle_special_vehicle_program(gts_root: Path, region: str, parser: DDBParser, gen_master: Any) -> dict[str, Any]:
    """Resolve P3/P4 SelectCarTypeVin10 probes from Spe FuncCommFrame + Gen CommSet."""
    spe_root = gts_db_root(gts_root, region, "Spe")
    spe_path = spe_root / "Toyota.ddb"
    spe = parser.parse_master_db(spe_path)
    func = spe.sections[18]
    frame = spe.sections[17]
    frame_rows = {
        struct.unpack_from("<H", raw, 0)[0]: raw
        for raw in ddb_records(frame)
    }
    by_key: dict[tuple[int, int], list[bytes]] = {}
    for raw in ddb_records(func):
        k1, selector = struct.unpack_from("<HH", raw, 0)
        by_key.setdefault((k1, selector), []).append(raw)

    def programs(selector_map: tuple[tuple[int, int], ...]) -> dict[str, Any]:
        selectors = {selector for selector, _ in selector_map}
        k1s = sorted({k1 for k1, selector in by_key if selector in selectors})
        out: dict[str, Any] = {}
        for k1 in k1s:
            steps = []
            for selector, parser_kind in selector_map:
                matches = by_key.get((k1, selector), [])
                if not matches:
                    continue
                frames = []
                for raw in matches:
                    comm_set_id, frame_id = struct.unpack_from("<HH", raw, 4)
                    comm_frame = frame_rows.get(frame_id)
                    if comm_frame is None:
                        raise ValueError(f"{region} Spe CommFrame {frame_id} is missing")
                    send_id, mask_id, check_id = struct.unpack_from("<HHH", comm_frame, 2)
                    frames.append({
                        "comm_set_id": comm_set_id,
                        "comm_frame_id": frame_id,
                        "send": _master_variable(spe, send_id)["bytes"],
                        "mask": _master_variable(spe, mask_id)["bytes"],
                        "check": _master_variable(spe, check_id)["bytes"],
                    })
                steps.append({
                    "selector": selector,
                    "parser_kind": parser_kind,
                    "frames": frames,
                })
            if steps:
                out[str(k1)] = {"k1": k1, "steps": steps}
        return out

    phase3 = programs(_PHASE3_SELECTORS)
    phase4 = programs(_PHASE4_SELECTORS)
    commset_ids = sorted({
        frame["comm_set_id"]
        for programs_by_k1 in (phase3, phase4)
        for program in programs_by_k1.values()
        for step in program["steps"]
        for frame in step["frames"]
    })
    gen_commsets = {row["comm_set_id"]: row for row in _master_comm_set_rows(parser, gen_master)}
    missing = [comm_set_id for comm_set_id in commset_ids if comm_set_id not in gen_commsets]
    if missing:
        raise ValueError(f"{region} Spe vehicle program references missing Gen CommSets {missing}")
    return {
        "phase3": {
            "type41_mode": "DecisionKey/DecisionKeyEU according to Toyota region selector",
            "programs_by_k1": phase3,
        },
        "phase4": {
            "type41_mode": "DecisionKey/DecisionKeyEU according to Toyota region selector",
            "programs_by_k1": phase4,
        },
        "commsets": {str(key): gen_commsets[key] for key in commset_ids},
        "source_identity": {
            "special_master": {
                "path": f"{region}/DB/Spe/Toyota.ddb",
                "bytes": spe_path.stat().st_size,
                "sha256": _file_sha256(spe_path),
            },
        },
        "boundary": (
            "SelectCarTypeVin10 P3/P4 resolves FuncCommFrame/CommFrame/variable records from the Spe master while "
            "the referenced CommSet is resolved from the Gen master. K1 is Toyota shared-data slot 14; no category heuristic is substituted."
        ),
    }


def _bundle_session_control(parser: DDBParser, master: Any, categories: list[dict[str, Any]]) -> dict[str, Any]:
    """Per-category lifecycle derived from each category's actual D1/D2/DD selector frames."""
    lifecycle = _execution_model()["gtsplus_continuity"]["dll_role_schema"]["execution_lifecycle"]
    transport = lifecycle["transport_and_session"]
    auto = transport["p5_automatic_session_judgment"]
    cadence_s = round(transport["test_present"]["cadence_ms"] / 1000, 3)

    def frame(category_id: int, selector: int) -> dict[str, Any] | None:
        rows = _master_frame_rows(parser, master, category_id, selector)
        if not rows:
            return None
        if len(rows) != 1:
            raise ValueError(f"category {category_id} selector 0x{selector:X} resolved {len(rows)} rows")
        row = rows[0]
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
        d1 = frame(category_id, 0xD1)
        d2 = frame(category_id, 0xD2)
        dd = frame(category_id, 0xDD)
        def dsc_session(value: dict[str, Any] | None) -> int | None:
            if value is None:
                return None
            send = bytes.fromhex(value["send"])
            return send[1] if len(send) == 2 and send[0] == 0x10 else None

        default_session = dsc_session(d1)
        extended_session = dsc_session(d2)
        session_executor_supported = default_session is not None and extended_session is not None
        keepalive = None
        if dd is not None:
            send = bytes.fromhex(dd["send"])
            if len(send) == 3 and send[0] == 0x22:
                did = int.from_bytes(send[1:3], "big")
                keepalive = {
                    "kind": "session_did_poll" if did == 0xF186 else "did_poll",
                    "did": f"0x{did:04X}",
                    "request": dd["send"],
                    "positive_prefix": (bytes([0x62]) + send[1:3]).hex(),
                    "interval_s": cadence_s,
                }
            elif send == b"\x10\x03":
                keepalive = {
                    "kind": "extended_session_refresh",
                    "request": dd["send"],
                    "interval_s": cadence_s,
                }
            else:
                keepalive = {
                    "kind": "unsupported_raw",
                    "request": dd["send"],
                    "interval_s": cadence_s,
                }
        per_category[str(category_id)] = {
            "generation_low5": int(category["generation"]) & 0x1F,
            "session_executor_supported": session_executor_supported,
            "session_executor_boundary": (
                None if session_executor_supported else
                "D1/D2 are present only as a request shape not implemented by the generic DiagnosticSession executor"
            ),
            "default_session": d1,
            "default_session_value": default_session,
            "extended_session": d2,
            "extended_session_value": extended_session,
            "keepalive_frame": dd,
            "keepalive": keepalive,
        }

    return {
        "kind": "toyota-per-category-selector-lifecycle",
        "category_gate": auto["category_gate"],
        "per_category": per_category,
        "boundary": (
            "D1/D2/DD are resolved independently for every Toyota category. The runtime follows the selected category's actual "
            "DiagnosticSessionControl bytes when D1/D2 have that wire shape; generation-low5 and category membership are evidence "
            "metadata, never an allowlist."
        ),
    }


def _simple_utility_rows(
    parser: DDBParser,
    master: Any,
    category: dict[str, Any],
    db: Any,
    strings: Any,
    *,
    support_mode: str | None,
) -> list[dict[str, Any]]:
    section = db.sections.get(77)
    if section is None:
        return []
    if section.decoded_record_size != 52:
        raise ValueError(
            f"{category.get('database')}: type-77 record size {section.decoded_record_size}, expected 52"
        )
    category_id = int(category["category_id"])

    phases: dict[int, dict[str, Any] | None] = {}
    for selector, subfunction in ((0xD8, 1), (0xD9, 2), (0xDA, 3)):
        rows = _master_frame_rows(parser, master, category_id, selector)
        if len(rows) != 1:
            phases[selector] = None
            continue
        frame = rows[0]
        expected = bytes((0x31, subfunction, 0xFF, 0xFF))
        send = bytes.fromhex(frame["send"]["bytes"])
        expected_reply = bytes((0x71, subfunction)).hex()
        phases[selector] = frame if send == expected and frame["receive_check"]["bytes"] == expected_reply else None

    result = []
    for index, raw in enumerate(ddb_records(section)):
        name_index = struct.unpack_from("<I", raw, 0x00)[0]
        rid = struct.unpack_from("<H", raw, 0x14)[0]
        utility_id = struct.unpack_from("<H", raw, 0x16)[0]
        command_variable = struct.unpack_from("<H", raw, 0x1A)[0]
        stop_variable = struct.unpack_from("<H", raw, 0x1C)[0]
        command = _master_variable(master, command_variable)
        stop_command = _master_variable(master, stop_variable)
        geometry_ok = all(phases.values()) and rid not in {0, 0xFFFF}
        row = {
            "id": utility_id,
            "kind": "simple_operation",
            "record": index,
            "name": strings.get_string(name_index) or "",
            "name_string_index": name_index,
            "routine_id": rid,
            "timer_ms": struct.unpack_from("<I", raw, 0x04)[0],
            "start_help_id": struct.unpack_from("<I", raw, 0x0C)[0],
            "sort_key": struct.unpack_from("<H", raw, 0x18)[0],
            "routine_command_variable": command_variable,
            "routine_command": command,
            "routine_stop_command_variable": stop_variable,
            "routine_stop_command": stop_command,
            "check_interval_ms": struct.unpack_from("<H", raw, 0x1E)[0],
            "result_keys": {
                "p5_pattern_display": struct.unpack_from("<H", raw, 0x20)[0],
                "p6_pattern_display": struct.unpack_from("<H", raw, 0x22)[0],
                "p5_pattern_description": struct.unpack_from("<H", raw, 0x24)[0],
                "p6_pattern_description": struct.unpack_from("<H", raw, 0x26)[0],
                "status_1": struct.unpack_from("<H", raw, 0x28)[0],
                "status_2": struct.unpack_from("<H", raw, 0x2A)[0],
                "p6_status_5": struct.unpack_from("<H", raw, 0x2C)[0],
                "p6_status_6": struct.unpack_from("<H", raw, 0x2E)[0],
                "raw_u16_30": struct.unpack_from("<H", raw, 0x30)[0],
                "raw_u16_32": struct.unpack_from("<H", raw, 0x32)[0],
            },
            "start_static": (
                bytes((0x31, 0x01)) + rid.to_bytes(2, "big") + bytes.fromhex(command["bytes"])
            ).hex() if geometry_ok else None,
            "stop_static": (bytes((0x31, 0x02)) + rid.to_bytes(2, "big")).hex() if geometry_ok else None,
            "result_static": (bytes((0x31, 0x03)) + rid.to_bytes(2, "big")).hex() if geometry_ok else None,
            "positive_response": 0x71,
            "session_requirement": "extended",
            "support_gate": {
                "mode": support_mode,
                "kind": "rid",
                "identifier": rid,
            },
            "execution": "plan_only" if geometry_ok and support_mode in {"p5-standard", "p6-standard"} else "unresolved_static_plan",
            "boundary": (
                "D8/D9/DA request geometry, fixed command bytes, timer/check interval, and result keys are exact. "
                "Runtime must apply Toyota RID support before mutation; result-key semantic rendering is separate."
            ),
        }
        if not geometry_ok:
            row["error"] = "D8/D9/DA simple-operation RoutineControl geometry is missing or malformed"
        elif support_mode not in {"p5-standard", "p6-standard"}:
            row["error"] = f"support mode {support_mode or 'unresolved'} has no standalone Simple Utility executor"
        result.append(row)
    return sorted(result, key=lambda row: (int(row["sort_key"]), int(row["id"])))


def _bundle_category_catalog(
    parser: DDBParser,
    master: Any,
    strings: StringDataBase,
    db_root: Path,
    bin_root: Path,
    category: dict[str, Any],
) -> dict[str, Any]:
    db_path = db_root / str(category["database"])
    db = parser.parse_ecu_db(db_path)
    monitor_rows = _monitor_rows(db, strings, db_path.name)
    bindings = _registry_role_bindings(parser, master, category, bin_root)
    dll_rows = list(parser.extract_master_dlls(master.sections[19]))
    category_id = int(category["category_id"])
    support_family = support.support_family(
        support.support_plugin(dll_rows, category_id, 0x67),
        support.support_plugin(dll_rows, category_id, 0xD5),
    )
    support_mode = support.support_mode(category_id, int(category["generation"]), support_family)
    common = {
        "category": category,
        "active_tests": _registry_active_tests(parser, master, category, db_root, strings, monitor_rows, bindings),
        "functions": _registry_function_hierarchy(parser, master, strings, category_id),
        "plugins": bindings,
        "commands": _registry_command_rows(parser, master, category, bin_root, bindings),
        "selectors": _registry_selector_rows(parser, master, category_id),
        "active_test_groups": _registry_active_test_groups(parser, category, db_root, strings),
        "utilities": _simple_utility_rows(parser, master, category, db, strings, support_mode=support_mode),
        "source_identity": {
            "database": {
                "path": f"{db_root.parent.parent.name}/DB/{db_root.name}/{db_path.name}",
                "bytes": db_path.stat().st_size,
                "sha256": _file_sha256(db_path),
            },
        },
    }
    if support_mode != "p6-standard":
        return {
            **common,
            "dids": _registry_did_catalog(monitor_rows),
            "dtcs": _registry_dtc_catalog(parser, db, strings, db_path.name),
            "data_list": _registry_data_list(db, strings),
            "generic_ffd": _generic_ffd_rows(
            db, strings, db_path.name,
            resolve_variable=lambda variable_id: bytes.fromhex(_master_variable(master, variable_id)["bytes"]),
        ),
            "rob": _rob_rows(db, strings, db_path.name),
        }
    if support_mode == "p6-standard":
        return {
            **common,
            "dids": {},
            "dtcs": {},
            "data_list": {
                "tables": [], "record_counts": {}, "row_count": 0,
                "display_order": "P6 Data List presentation semantics are not exported by this catalog yet",
                "rows": [],
            },
            "generic_ffd": {
                "signals": [], "boundary": "P6 generic freeze-frame semantics are not projected from P5",
            },
            "rob": {
                "behavior_codes": [], "signals": [],
                "boundary": "P6 Record-of-Behavior semantics are not projected from P5",
            },
        }
    raise AssertionError(f"unreachable catalog support mode for category {category_id}: {support_mode!r}")


def _bundle_json_bytes(payload: Any) -> bytes:
    return (json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n").encode()


def _bundle_write_json(archive: zipfile.ZipFile, member: str, payload: Any) -> None:
    info = zipfile.ZipInfo(member, date_time=(1980, 1, 1, 0, 0, 0))
    info.compress_type = zipfile.ZIP_DEFLATED
    info.external_attr = 0o644 << 16
    archive.writestr(info, _bundle_json_bytes(payload))


def _bundle_customize_catalog(
    master: Any,
    strings: Any,
    category_by_id: dict[int, dict[str, Any]],
) -> dict[str, Any]:
    """Recover current regional Toyota Customize catalog from master tables 20/21/22/34.

    These are master tables, not ECU-DDB tables. GetCustomSupportList selects a
    body type and then table-20 groups. GetCustomItemList resolves table-21 by
    group id and table-22 by choice-list id; each item names the live target ECU.
    """
    def u16(raw: bytes, off: int) -> int:
        return struct.unpack_from("<H", raw, off)[0]

    def u32(raw: bytes, off: int) -> int:
        return struct.unpack_from("<I", raw, off)[0]

    choice_rows: dict[int, list[dict[str, Any]]] = {}
    for raw in ddb_records(master.sections[22]):
        key = u16(raw, 0x04)
        choice_rows.setdefault(key, []).append({
            "value": u16(raw, 0x06),
            "name": strings.get_string(u32(raw, 0x00)) or "",
            "name_string_index": u32(raw, 0x00),
            "exception_flag": raw[0x08],
            "exception_id": u16(raw, 0x0A),
        })
    for rows in choice_rows.values():
        rows.sort(key=lambda row: int(row["value"]))

    groups = []
    for raw in ddb_records(master.sections[20]):
        groups.append({
            "body_type": raw[0x08],
            "group_id": u16(raw, 0x04),
            "name": strings.get_string(u32(raw, 0x00)) or "",
            "name_string_index": u32(raw, 0x00),
            "exception_flag": raw[0x09],
            "exception_id": u16(raw, 0x0A),
        })
    groups.sort(key=lambda row: (int(row["body_type"]), int(row["group_id"])))

    items = []
    for raw in ddb_records(master.sections[21]):
        group_id = u16(raw, 0x08)
        item_id = u16(raw, 0x0A)
        target_category_id = u16(raw, 0x0C)
        choice_key = u16(raw, 0x20)
        all_default_gate = u16(raw, 0x22)
        target = category_by_id.get(target_category_id)
        items.append({
            "group_id": group_id,
            "item_id": item_id,
            "name": strings.get_string(u32(raw, 0x00)) or "",
            "name_string_index": u32(raw, 0x00),
            "metadata_dword_04": u32(raw, 0x04),
            "target_category_id": target_category_id,
            "target_category_name": str(target.get("name") or "") if target else "",
            "target_generation": int(target["generation"]) if target and target.get("generation") is not None else None,
            "item_aux_u16_0e": u16(raw, 0x0E),
            "support_bit_start": u16(raw, 0x10),
            "support_bit_end": u16(raw, 0x12),
            "current_bit_start": u16(raw, 0x14),
            "current_bit_end": u16(raw, 0x16),
            "write_bit_start": u16(raw, 0x18),
            "write_bit_end": u16(raw, 0x1A),
            "legacy_data_id": u16(raw, 0x1C),
            "raw_u16_1e": u16(raw, 0x1E),
            "choice_list_key": choice_key,
            "choices": choice_rows.get(choice_key, []),
            "all_default_gate_u16_22": all_default_gate,
            "raw_u32_24": u32(raw, 0x24),
            "raw_u16_28": u16(raw, 0x28),
            "write_did": u16(raw, 0x2A),
            "target_phase_type": raw[0x2C],
            "merge_mode": raw[0x2D],
            "support_selector": raw[0x2E],
            "read_current": raw[0x2F],
            "current_data_mode": raw[0x30],
            "write_variant": raw[0x31],
            "support_mode": raw[0x32],
            "raw_u8_33": raw[0x33],
        })
    for item in items:
        generation_low5 = (int(item["target_generation"]) & 0x1F) if item["target_generation"] is not None else None
        if generation_low5 in {0x14, 0x15, 0x16} and int(item["write_did"]) != 0:
            family = "p6" if generation_low5 == 0x16 else "p5"
            item["modern_executor"] = {
                "family": family,
                "support_gate": f"{family}-standard DID support inventory must advertise write_did",
                "read_current": "22 <write_did> -> 62 <write_did> || current bytes",
                "merge": "clear MSB0 write_bit_start..write_bit_end then OR selected raw value; merge_mode 1 additionally requires the preceding-byte support bit(s)",
                "write": "2E <write_did> || merged current bytes -> 6E <write_did>",
                "verify": "re-read write_did and require the merged bytes/value",
                "session_requirement": "extended",
            }
    items.sort(key=lambda row: (int(row["group_id"]), int(row["item_id"]), int(row["target_category_id"])))

    probes = []
    for raw in ddb_records(master.sections[34]):
        probes.append({
            "target_category_id": u16(raw, 0x00),
            "second_connect_argument": u16(raw, 0x02),
            "connect_frame_id": u16(raw, 0x04),
            "raw_u16_06": u16(raw, 0x06),
            "lookup_key": u16(raw, 0x08),
            "raw_u16_0a": u16(raw, 0x0A),
            "connect_argument_0c": raw[0x0C],
            "body_type": raw[0x0D],
            "raw_u16_0e": u16(raw, 0x0E),
        })

    return {
        "schema": "toyota-customize-catalog-v1",
        "groups": groups,
        "items": items,
        "body_type_probes": probes,
        "counts": {
            "group_rows": len(groups),
            "item_rows": len(items),
            "choice_rows": sum(len(rows) for rows in choice_rows.values()),
            "body_type_probe_rows": len(probes),
        },
        "semantics": {
            "group_key": "body_type:u8 + group_id:u16 (CDbCustSignListTable)",
            "item_key": "group_id:u16 + item_id:u16 (CDbCustItemTable)",
            "choice_key": "choice_list_key:u16 + value:u16 (CDbPossibleToSetTable)",
            "all_default_gate": (
                "SetCustomizeAllDefault checks CustItem +0x22 before its per-row default path; this field is zero in every "
                "current NA/EU/JP CustItem row, so no OEM default value is inferred from the current master"
            ),
            "target": "CustItem +0x0C is the live target ECU/category id; +0x2C is the target phase type",
            "modern_write": (
                "For generation-low5 0x14/0x15/0x16, +0x2A is the write/current DID. SetCustom reads it through selector 0xCA, "
                "merges the selected value into +0x18/+0x1A MSB0 write bits, then selector 0x74 sends 2E <DID> || merged bytes and verifies 6E <DID>."
            ),
        },
        "boundary": (
            "Static OEM Customize catalog and item geometry only. Body-type selection still requires the recovered live "
            "GetCustomSupportList connection checks; current-value acquisition and SetCustom write execution are separate runtime stages."
        ),
    }


def _build_toyota_diag_region(
    gts_root: Path,
    family: str,
    region: str,
    part_path: Path,
) -> dict[str, Any]:
    """Build one Toyota-native regional resolver index plus decoded catalog shards."""
    db_root = gts_db_root(gts_root, region, family)
    parser = DDBParser()
    master_path = db_root / "Toyota.ddb"
    strings_path = db_root / "M_English.ddb"
    master = parser.parse_master_db(master_path)
    strings = _english_strings(parser, db_root)
    category_rows = _master_category_rows(parser, master, strings)
    dll_rows = list(parser.extract_master_dlls(master.sections[19]))

    # Preserve the exact P5 catalog set that shipped before P6 catalog support, then
    # add current p6-standard categories. Do not broaden or shrink legacy partner P5 shards here.
    p5_catalog_ids = {
        int(entry.category_id)
        for entry in dll_rows
        if entry.dll_name == "GetSupportP5_DT.dll"
    }
    catalog_categories = []
    for row in category_rows:
        category_id = int(row["category_id"])
        if not row.get("database") or not (db_root / str(row["database"])).is_file():
            continue
        family = support.support_family(
            support.support_plugin(dll_rows, category_id, 0x67),
            support.support_plugin(dll_rows, category_id, 0xD5),
        )
        mode = support.support_mode(category_id, int(row["generation"]), family)
        if category_id in p5_catalog_ids or mode == "p6-standard":
            catalog_categories.append(row)
    catalog_ids = {int(row["category_id"]) for row in catalog_categories}

    vehicles: dict[str, dict[str, Any]] = {}
    vehicle_names = {
        struct.unpack_from("<I", raw, 4)[0]: strings.get_string(struct.unpack_from("<I", raw, 0)[0]) or ""
        for raw in ddb_records(master.sections[43])
    }
    vehicle_sets: dict[int, set[int]] = {}
    for raw in ddb_records(master.sections[5]):
        vehicle_type, install_set_id = struct.unpack_from("<HH", raw, 4)
        vehicle_sets.setdefault(vehicle_type, set()).add(install_set_id)
    for vehicle_type, install_set_ids in sorted(vehicle_sets.items()):
        vehicles[str(vehicle_type)] = {
            "vehicle_type": vehicle_type,
            "name": vehicle_names.get(vehicle_type, ""),
            "install_set_ids": sorted(install_set_ids),
        }

    category_index: dict[str, dict[str, Any]] = {}
    category_by_id = {int(row["category_id"]): row for row in category_rows}
    for row in category_rows:
        category_id = int(row["category_id"])
        item = dict(row)
        item["generation_low5"] = int(row["generation"]) & 0x1F
        single = support.support_plugin(dll_rows, category_id, 0x67)
        multi = support.support_plugin(dll_rows, category_id, 0xD5)
        item["support_plugin_single"] = single
        item["support_plugin_multi"] = multi
        item["support_family"] = support.support_family(single, multi)
        item["support_mode"] = support.support_mode(category_id, int(row["generation"]), item["support_family"])
        item["catalog_available"] = category_id in catalog_ids
        if category_id in catalog_ids:
            item["catalog_member"] = f"catalogs/{region}/{category_id}.json"
        category_index[str(category_id)] = item

    install_sets: dict[str, list[dict[str, Any]]] = {}
    routes: dict[str, dict[str, Any]] = {}
    connection_frame_ids: set[int] = set()
    vehicle_types_with_routes: set[int] = set()
    install_row_count = 0
    for raw in ddb_records(master.sections[44]):
        install_set_id, category_id, frame_id, comm_set_id = struct.unpack_from("<HHHH", raw, 4)
        phase_type = raw[0x13]
        route_key = f"{category_id}:{phase_type}"
        if route_key not in routes:
            try:
                routes[route_key] = _bundle_protocol_route(master, category_id, phase_type)
            except ValueError:
                route_key = None
        install_sets.setdefault(str(install_set_id), []).append({
            "category_id": category_id,
            "connection_frame_id": frame_id,
            "connection_comm_set_id": comm_set_id,
            "connection_phase_type": phase_type,
            "route_key": route_key,
        })
        install_row_count += 1
        connection_frame_ids.add(frame_id)

    set_has_route = {
        int(set_id): any(row.get("route_key") is not None for row in rows)
        for set_id, rows in install_sets.items()
    }
    for vehicle_type, row in vehicles.items():
        if any(set_has_route.get(int(set_id), False) for set_id in row["install_set_ids"]):
            vehicle_types_with_routes.add(int(vehicle_type))

    vin_rows = [{
        "flags": struct.unpack_from("<I", raw, 0x00)[0],
        "vehicle_type": struct.unpack_from("<H", raw, 0x0E)[0],
        "category_id": struct.unpack_from("<H", raw, 0x10)[0],
        "phase_type": raw[0x12],
        "vin_prefix_hex": raw[0x13:0x1E].hex(),
    } for raw in ddb_records(master.sections[59])]
    type41_rows = _bundle_vehicle_decision_rows(master)
    vehicle_program = _bundle_special_vehicle_program(gts_root, region, parser, master)
    bin_root = gts_root / "bin"
    vehicle_roles = {}
    for role, semantic in ((0x45, "legacy_select_vehicle"), (0x4A, "legacy_select_vehicle_vin"), (0x7D, "vin10_select_vehicle")):
        selected = support.support_plugin(dll_rows, 0, role)
        if selected is None:
            continue
        dll = str(selected["dll"])
        vehicle_roles[f"0x{role:02X}"] = {
            **selected,
            "semantic": semantic,
            "binary_present_in_current_gtsplus": (bin_root / dll).is_file(),
        }

    session_categories = [category_by_id[key] for key in sorted(category_by_id)]
    region_index = {
        "region": region,
        "vehicles": vehicles,
        "vin_decision": {
            "path": "P5/P6 final resolver; P3/P4 candidate/source stage before type-41",
            "key": "category_id + phase_type + VIN[0:11], with flags bits 0..10 as per-position wildcards",
            "rows": vin_rows,
        },
        "vehicle_decision": {
            "path": "P3/P4 live SelectCarTypeVin10 probes followed by CDbVehicleDecisionTable",
            "rows": type41_rows,
            "probe_program": vehicle_program,
        },
        "vehicle_resolver_dispatch": {
            "roles": vehicle_roles,
            "vin10_generation_low5": {
                "3": "phase3",
                "4": "phase4",
                "20": "phase5",
                "21": "phase5",
                "22": "phase6",
            },
            "vin10_rejected_generation_low5": list(range(5, 20)),
            "boundary": (
                "SelectCarTypeVin10 itself rejects low5 5..19 with 0xA0040403. Toyota's master separately binds legacy "
                "SelectCarType.dll/SelectCarTypeVin.dll roles; those binaries are not present in the current GTS+ payload, so "
                "their semantics are unresolved here rather than declaring those Toyota generations unsupported."
            ),
        },
        "categories": category_index,
        "install_sets": install_sets,
        "routes": routes,
        "connection_frames": {
            str(frame_id): _bundle_connection_frame(master, frame_id)
            for frame_id in sorted(connection_frame_ids)
        },
        "commsets": {str(row["comm_set_id"]): row for row in _master_comm_set_rows(parser, master)},
        "session_control": _bundle_session_control(parser, master, session_categories),
        "utilities": _registry_utilities(parser, master),
        "customize_member": f"customize/{region}/0.json",
        "can_topology": _bundle_can_topologies(parser, master, strings, vehicle_types_with_routes),
        "counts": {
            "vehicle_count": len(vehicles),
            "install_set_count": len(install_sets),
            "category_count": len(category_index),
            "catalog_count": len(catalog_ids),
            "install_row_count": install_row_count,
            "vin_decision_row_count": len(vin_rows),
            "vehicle_decision_row_count": len(type41_rows),
            "route_count": len(routes),
            "support_family_counts": {
                family_name: sum(row.get("support_family") == family_name for row in category_index.values())
                for family_name in ("p3", "p4", "p5", "p6")
            },
            "support_mode_counts": {
                mode: sum(row.get("support_mode") == mode for row in category_index.values())
                for mode in sorted({str(row.get("support_mode")) for row in category_index.values() if row.get("support_mode")})
            },
        },
        "source_identity": {
            "master": {
                "path": f"{region}/DB/{family}/Toyota.ddb",
                "bytes": master_path.stat().st_size,
                "sha256": _file_sha256(master_path),
            },
            "strings": {
                "path": f"{region}/DB/{family}/M_English.ddb",
                "bytes": strings_path.stat().st_size,
                "sha256": _file_sha256(strings_path),
            },
            "special_master": vehicle_program["source_identity"]["special_master"],
        },
    }

    with zipfile.ZipFile(part_path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6) as archive:
        _bundle_write_json(
            archive,
            f"customize/{region}/0.json",
            _bundle_customize_catalog(master, strings, category_by_id),
        )
        for category in sorted(catalog_categories, key=lambda row: int(row["category_id"])):
            category_id = int(category["category_id"])
            payload = _bundle_category_catalog(parser, master, strings, db_root, bin_root, category)
            _bundle_write_json(archive, f"catalogs/{region}/{category_id}.json", payload)
    return region_index


def _bundle_write_bytes(archive: zipfile.ZipFile, member: str, data: bytes) -> None:
    info = zipfile.ZipInfo(member, date_time=(1980, 1, 1, 0, 0, 0))
    info.compress_type = zipfile.ZIP_DEFLATED
    info.external_attr = 0o644 << 16
    archive.writestr(info, data)


def write_toyota_diag_bundle(
    gts_root: Path,
    out: Path,
    *,
    family: str = "Gen",
    regions: tuple[str, ...] = TOYOTA_DIAG_BUNDLE_REGIONS,
) -> dict[str, Any]:
    """Write the universal clean Toyota diagnostic bundle used by `tools/toyota`.

    Regional extraction is CPU-heavy, so each regional master is derived in an
    independent worker. The final archive is then merged in fixed region/category
    order with fixed ZIP timestamps, keeping the artifact deterministic regardless
    of worker completion order.
    """
    resolver_artifact = json.loads(VEHICLE_RESOLVER.read_text())
    if resolver_artifact.get("release") != "2026.03.002.02":
        raise ValueError("current vehicle resolver release drift")
    index: dict[str, Any] = {
        "schema": TOYOTA_DIAG_BUNDLE_SCHEMA,
        "profile": TOYOTA_DIAG_BUNDLE_PROFILE,
        "release": resolver_artifact["release"],
        "default_region": "NA",
        "fault_status_mask": 0xAF,
        "mode04_request": "0104000000000000",
        "support_contracts": {
            "p5": {
                **resolver_artifact["p5_support"],
                "did_mode_dispatch": {
                    "p5-standard": "generic C8 two-level DID bitmap",
                    "p5-subaru": "CreateEnableDataIdListForSubaruCheckDID path",
                    "p5-suzuki": "CreateEnableDataIdListForSuzuki path",
                    "p5-mazda": "CreateEnableDataIdListForMazda path",
                    "p5-hino": "CreateEnableDataIdListForHino path for category 0x13A9/0x13B9/0x13BA",
                },
                "routine_root": {
                    "request": "31011001",
                    "positive_sid": "0x71",
                    "bitmap_bytes_max": 32,
                    "bit_numbering": "msb0",
                    "root_request_rid": "0x1001",
                    "root_bitmap_base": "0x0000",
                    "root_shift": 8,
                    "member_offset": 1,
                    "terminal_alias_bit_skipped": True,
                    "selector_range": ["0x0200", "0xDF00"],
                    "selector_request": "3101NNNN",
                    "group_ids_remain_supported": True,
                    "routine_info_capability": "function 3 / detail 0x56; if present, strip first returned option byte before bitmap decoding",
                    "generation_21_policy": "generation-low5 0x15 uses static type-71/type-77 RIDs rather than selector 0xCC",
                    "hierarchy": "RID 0x1001 root bitmap -> xx00 group RIDs; query 0x0200..0xDF00 groups -> xx01..xxFF member RID bitmap",
                    "implementation": {
                        "command_common_sha256": "98e313d197eb7115d037a2d46e71343b4b44862356e9d772c8f2f03d96e638d3",
                        "AnalyzeFrameData": "0x10063660",
                        "CreateEnableRIdList": "0x10066160",
                        "ConvertToNoRoutineInfo": "0x100738F0",
                        "CheckIncludingRoutineInfo": "0x10070910"
                    }
                },
                "standard_did": {
                    "root_ids_remain_supported": True,
                    "selector_excluded": ["0xF300", "0xFD00"],
                    "member_offset": 1,
                    "terminal_alias_bit_skipped": True,
                    "implementation": {
                        "command_common_sha256": "98e313d197eb7115d037a2d46e71343b4b44862356e9d772c8f2f03d96e638d3",
                        "AnalyzeFrameData": "0x10063660",
                        "CreateEnableDataIdList": "0x10063890",
                    },
                },
            },
            "p6": {
                "options": {"1": "PID", "2": "DID", "3": "RID"},
                "did_root": {
                    "request": "22a100",
                    "positive_sid": "0x62",
                    "bitmap_bytes_max": 32,
                    "bit_numbering": "msb0",
                    "root_base": "0xA100",
                    "root_shift": 0,
                    "selector_request": "22a1NN",
                    "selector_excluded": ["0xA1FD", "0xA1FE"],
                    "member_base": "(selector & 0x00FF) << 8",
                    "member_shift": 0,
                    "selector_ids_remain_supported": True,
                    "hierarchy": "A100-root bitmap -> A1nn selector IDs; query A1nn except A1FD/A1FE -> nn00..nnFF DID bitmap",
                },
                "routine_root": {
                    "request": "3101d100",
                    "positive_sid": "0x71",
                    "bitmap_bytes_max": 32,
                    "bit_numbering": "msb0",
                    "root_base": "0xD100",
                    "root_shift": 0,
                    "selector_request": "3101d1NN",
                    "selector_excluded": ["0xD1F0", "0xD1FE"],
                    "member_base": "(selector & 0x00FF) << 8",
                    "member_shift": 0,
                    "selector_ids_remain_supported": True,
                    "hierarchy": "D100-root bitmap -> D1nn selector IDs; query D1nn except D1F0/D1FE -> nn00..nnFF RID bitmap",
                },
                "plugin": "GetSupportMultiP6_DT.dll",
                "implementation": {
                    "command_common_sha256": "98e313d197eb7115d037a2d46e71343b4b44862356e9d772c8f2f03d96e638d3",
                    "AnalyzeFrameData": "0x100678D0",
                    "CreateEnableDataIdList": "0x100679A0",
                    "CreateEnableRIdList": "0x10067CF0",
                },
            },
        },
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
        "function_names": REGISTRY_FUNCTION_NAME_BOUNDARY,
        "regions": {},
        "source_identity": {
            "vehicle_resolver": {
                "path": str(VEHICLE_RESOLVER.relative_to(REPO_ROOT)),
                "bytes": VEHICLE_RESOLVER.stat().st_size,
                "sha256": _file_sha256(VEHICLE_RESOLVER),
            },
            "execution_model": {
                "path": str(EXECUTION_MODEL.relative_to(REPO_ROOT)),
                "bytes": EXECUTION_MODEL.stat().st_size,
                "sha256": _file_sha256(EXECUTION_MODEL),
            },
        },
        "boundary": (
            "Clean derived metadata only. Vehicle/install/category/route/session/support-family selection comes from Toyota Gen/Spe "
            "masters and role fallback. Catalog availability is an independent tooling capability and is never an ECU-support gate. "
            "Live family-specific support filtering remains the per-ECU capability criterion. No Toyota binary or opaque DDB payload is embedded."
        ),
    }

    out.parent.mkdir(parents=True, exist_ok=True)
    temporary = out.with_name(f".{out.name}.tmp")
    temporary.unlink(missing_ok=True)
    try:
        with tempfile.TemporaryDirectory(prefix="toyota-diag-bundle-", dir=out.parent) as workspace_text:
            workspace = Path(workspace_text)
            part_paths = {region: workspace / f"{region}.zip" for region in regions}
            workers = min(len(regions), 3)
            with ProcessPoolExecutor(max_workers=workers) as executor:
                futures = {
                    executor.submit(_build_toyota_diag_region, gts_root, family, region, part_paths[region]): region
                    for region in regions
                }
                for future in as_completed(futures):
                    region = futures[future]
                    index["regions"][region] = future.result()

            with zipfile.ZipFile(temporary, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6) as archive:
                for region in regions:
                    with zipfile.ZipFile(part_paths[region]) as part:
                        names = sorted(part.namelist(), key=lambda name: int(Path(name).stem))
                        for name in names:
                            _bundle_write_bytes(archive, name, part.read(name))
                _bundle_write_json(archive, "index.json", index)
        temporary.replace(out)
    except BaseException:
        temporary.unlink(missing_ok=True)
        raise
    return index
