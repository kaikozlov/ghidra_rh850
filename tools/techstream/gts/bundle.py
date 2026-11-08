"""Toyota-current regional diagnostic catalogs in canonical gzip-member storage."""

from __future__ import annotations

import io
import json
import shutil
import struct
import tempfile
import zipfile
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
from typing import Any

from tools import REPO_ROOT
from tools.techstream.diag_bundle import DiagnosticBundleWriter
from tools.techstream.gts.ddb import _english_strings, _generic_ffd_rows, _monitor_rows, _rob_rows
from tools.techstream.ddb_semantics import (
    NativeSelectionError,
    UnresolvedNativeContext,
    records as ddb_records,
    select_for_consumer,
)
from tools.techstream.gts.execution_model import EXECUTION_MODEL, VEHICLE_RESOLVER, _execution_model, _file_sha256, _resolve_plugin_path
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
    _registry_request_row,
    _registry_selector_rows,
    _registry_selected_role_bindings,
    _registry_utilities,
)
from tools.techstream.gts.master import (
    _master_category_rows,
    _resolve_master_category,
    _master_variable,
)
from tools.techstream.parse_ddb import DDBParser, StringDataBase
from tools.techstream.gts.p6_catalog import p6_catalog
from tools.techstream.gts.legacy_catalog import legacy_catalog_rows
from tools.techstream.gts.legacy_support import support_catalog
from tools.techstream.gts.legacy_freeze import dynamic_lsb_rows
from tools.techstream.gts.legacy_catalog import _json_value
from tools.techstream.gts.physical_catalog import physical_catalog
from tools.techstream.legacy_rob import legacy_rob_catalog
from tools.techstream.gts.p6_ddr import p6_ddr_catalog
from tools.techstream.gts.work_factor import work_factor_catalog, viewer_help_index
from tools.techstream.gts.native_ddr import native_ddr_catalog
from tools.techstream.gts.ddr_behavior import ddr_behavior_catalog
from tools.techstream.gts.trigger_catalog import trigger_catalog
from tools.techstream.gts.active_test_support import active_test_support_catalog
from tools.techstream.gts.variable_drive import variable_drive_catalog
from tools.techstream.gts.monitor_source_catalog import monitor_source_catalog
from tools.techstream.gts.obd_monitor import obd_monitor_catalog
from tools.techstream.gts.diagnostic_metadata import diagnostic_metadata
from tools.techstream.gts.dtc_source_catalog import dtc_source_catalog
from tools.techstream.gts.active_test_source import active_test_source_catalog
from tools.techstream.gts.rob_source_catalog import rob_source_catalog
from tools.techstream.gts import support
from tools.techstream.gts.query import native_ecu_catalog_category, native_selection_context
from tools.techstream.techstream_paths import gts_db_root


TOYOTA_DIAG_BUNDLE_SCHEMA = "toyota-diagnostics-bundle-v4"
TOYOTA_DIAG_BUNDLE_PROFILE = "toyota-current"
TOYOTA_DIAG_BUNDLE_REGIONS = ("NA", "EU", "JP")

_PHASE3_SELECTORS = ((0x1B, 9), (0x1C, 5), (0x1D, 4), (0x1E, 3), (0x1F, 2), (0x20, 2),
                     (0x21, 2), (0x22, 8), (0x23, 1), (0x24, 1), (0x25, 1), (0x26, 6), (0x27, 7))
_PHASE4_SELECTORS = ((0x28, 1), (0x29, 1), (0x2A, 1), (0x2B, 1), (0x2C, 1), (0x2D, 1),
                     (0x2E, 1), (0x2F, 2), (0x30, 2), (0x31, 2), (0x32, 2), (0x33, 2),
                     (0x34, 2), (0x36, 3), (0x37, 4), (0x38, 5), (0x35, 6), (0x39, 10))


def _bundle_transport_semantics(route_selector: int, request_address: int, functional_address: int) -> dict[str, Any]:
    """Recover the transport controller selected by CCommFrameCtrl::ChangeCommIF.

    ChangeCommIF switches on the low nibble of the encoded route selector.
    Values ending in 2 use the ISO15765 family; 0x18/0x38 select CCommCtrlISO15765_29BitCan;
    0x78/0x88 select the CAN-FD ISO15765 PS controller; low-nibble 4 selects
    CCommCtrlISO13400_NDIS. Keep unrecovered cases explicit rather than projecting
    the transport implemented by our consumer onto Toyota's route.
    """
    low = route_selector & 0x0F
    out: dict[str, Any] = {
        "change_comm_if_case": low,
        "request_address_field": request_address,
        "functional_address_field": functional_address,
    }
    if route_selector in {0x18, 0x38}:
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
    elif route_selector in {0x78, 0x88}:
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


def _bundle_protocol_route(master: Any, category_id: int, route_selector: int) -> dict[str, Any]:
    """Materialize Toyota's class-0x10D route and recovered transport interpretation."""
    matches = [
        raw for raw in ddb_records(master.sections[13])
        if struct.unpack_from("<H", raw, 0x00)[0] == category_id and raw[0x18] == route_selector
    ]
    if len(matches) != 1:
        raise ValueError(
            f"CDbProtInfo category {category_id} route selector 0x{route_selector:02X} resolved {len(matches)} rows"
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
        "route_selector": raw[0x18],
        **_bundle_transport_semantics(raw[0x18], request_address, functional_address),
    }


def _bundle_connection_frame(master: Any, frame_id: int) -> dict[str, Any]:
    result = master.query(17, frame_id)
    try:
        selected = select_for_consumer(result, "frame")
    except (NativeSelectionError, UnresolvedNativeContext) as exc:
        return {"frame_id": frame_id, "resolved": False, "native": result.as_dict(), "status": getattr(exc, "status", None)}
    send_var, mask_var, check_var = struct.unpack_from("<HHH", selected.raw, 2)
    source = master.database_for(selected)
    return {
        "frame_id": frame_id,
        "resolved": True,
        "send": _master_variable(source, send_var)["bytes"],
        "mask": _master_variable(source, mask_var)["bytes"],
        "check": _master_variable(source, check_var)["bytes"],
        "native": result.as_dict(),
        "source": selected.as_dict(),
    }


def _bundle_comm_set(master: Any, comm_set_id: int) -> dict[str, Any]:
    result = master.query(29, comm_set_id)
    try:
        selected = select_for_consumer(result, "commset")
    except (NativeSelectionError, UnresolvedNativeContext) as exc:
        return {"resolved": False, "native": result.as_dict(), "status": getattr(exc, "status", None)}
    raw = selected.raw
    return {
        "resolved": True,
        "comm_set_id": comm_set_id,
        "send_parameter": struct.unpack_from("<I", raw, 0)[0],
        "receive_timeout": struct.unpack_from("<I", raw, 4)[0],
        "retry_count": raw[14],
        "native": result.as_dict(),
        "source": selected.as_dict(),
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
            "route_selector": raw[0x02],
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


def _bundle_special_vehicle_program(gts_root: Path, region: str, parser: DDBParser, master: Any) -> dict[str, Any]:
    """Export native Gen+Spe selector programs for the P3/P4 vehicle probes."""
    raw_keys = {
        struct.unpack_from("<HH", row.raw, 0)
        for row in master.raw_records(18)
    }

    def programs(selector_map: tuple[tuple[int, int], ...]) -> dict[str, Any]:
        selectors = {selector for selector, _ in selector_map}
        k1s = sorted({k1 for k1, selector in raw_keys if selector in selectors})
        out = {}
        for k1 in k1s:
            steps = []
            for selector, parser_kind in selector_map:
                if (k1, selector) not in raw_keys:
                    continue
                program = _registry_request_row(parser, master, k1, selector, f"vehicle_probe_{selector:02x}")
                steps.append({**program, "selector": selector, "parser_kind": parser_kind})
            if steps:
                out[str(k1)] = {"k1": k1, "steps": steps}
        return out

    phase3 = programs(_PHASE3_SELECTORS)
    phase4 = programs(_PHASE4_SELECTORS)
    commset_ids = sorted({
        frame["comm_set"]
        for by_k1 in (phase3, phase4)
        for program in by_k1.values()
        for step in program["steps"]
        for frame in step["frames"]
    })
    commsets = {key: _bundle_comm_set(master, key) for key in commset_ids}
    spe_path = gts_db_root(gts_root, region, "Spe") / "Toyota.ddb"
    return {
        "phase3": {
            "type41_mode": "DecisionKey/DecisionKeyEU according to Toyota region selector",
            "programs_by_k1": phase3,
        },
        "phase4": {
            "type41_mode": "DecisionKey/DecisionKeyEU according to Toyota region selector",
            "programs_by_k1": phase4,
        },
        "commsets": {str(key): commsets[key] for key in commset_ids},
        "native_context": master.as_dict(),
        "source_identity": {
            "special_master": {
                "path": str(spe_path.relative_to(gts_root)),
                "bytes": spe_path.stat().st_size,
                "sha256": _file_sha256(spe_path),
            },
        },
        "boundary": (
            "Selector/frame/CommSet selection uses the shared native Gen+Spe context and first-selector CommSet. "
            "K1 is Toyota shared-data slot 14; type-41 metadata remains raw/unproved live selection."
        ),
    }


def _bundle_session_control(parser: DDBParser, master: Any, categories: list[dict[str, Any]]) -> dict[str, Any]:
    """Export complete native D1/D2/DD programs, not single-frame projections."""
    lifecycle = _execution_model()["gtsplus_continuity"]["dll_role_schema"]["execution_lifecycle"]
    transport = lifecycle["transport_and_session"]
    auto = transport["p5_automatic_session_judgment"]
    cadence_s = round(transport["test_present"]["cadence_ms"] / 1000, 3)

    def program(category_id: int, selector: int, name: str) -> dict[str, Any]:
        return _registry_request_row(parser, master, category_id, selector, name)

    def session_values(value: dict[str, Any]) -> list[int]:
        if not value["resolved"] or not value["frames"]:
            return []
        values = []
        for frame in value["frames"]:
            send = bytes.fromhex(frame["send"])
            if len(send) != 2 or send[0] != 0x10:
                return []
            values.append(send[1])
        return values

    per_category = {}
    for category in categories:
        category_id = int(category["category_id"])
        category_query = master.query(16, category_id)
        selected_category = category_query.records[0] if category_query.status == 0 and category_query.records else None
        d1 = program(category_id, 0xD1, "default_session")
        d2 = program(category_id, 0xD2, "extended_session")
        dd = program(category_id, 0xDD, "keepalive")
        default_values = session_values(d1)
        extended_values = session_values(d2)
        default_session = default_values[-1] if default_values else None
        extended_session = extended_values[-1] if extended_values else None
        session_executor_supported = bool(default_values and extended_values)
        keepalive_steps = []
        for frame in dd["frames"] if dd["resolved"] else []:
            send = bytes.fromhex(frame["send"])
            step = {"request": frame["send"], "frame": frame}
            if len(send) == 3 and send[0] == 0x22:
                did = int.from_bytes(send[1:3], "big")
                step.update({
                    "kind": "session_did_poll" if did == 0xF186 else "did_poll",
                    "did": f"0x{did:04X}",
                    "positive_prefix": (bytes([0x62]) + send[1:3]).hex(),
                })
            elif send == b"\x10\x03":
                step["kind"] = "extended_session_refresh"
            else:
                step["kind"] = "unsupported_raw"
            keepalive_steps.append(step)
        keepalive = {
            "program": dd,
            "steps": keepalive_steps,
            "interval_s": cadence_s,
        }
        per_category[str(category_id)] = {
            "generation_low5": (selected_category.generation & 0x1F) if selected_category is not None else None,
            "category_native_query": category_query.as_dict(),
            "session_executor_supported": session_executor_supported,
            "session_executor_boundary": (
                None if session_executor_supported else
                "D1/D2 are present only as a request shape not implemented by the generic DiagnosticSession executor"
            ),
            "default_session": d1,
            "default_session_value": default_session,
            "default_session_values": default_values,
            "extended_session": d2,
            "extended_session_value": extended_session,
            "extended_session_values": extended_values,
            "keepalive": keepalive,
        }

    return {
        "kind": "toyota-per-category-selector-lifecycle",
        "native_context": master.as_dict(),
        "execution_order": "Execute all frames in each selected program in emitted order; the scalar session value is the final DSC step, not a substitute request.",
        "category_gate": auto["category_gate"],
        "per_category": per_category,
        "boundary": (
            "D1/D2/DD are context-qualified ordered native programs for every initial Toyota category. Execute every frame, "
            "with the first selector row's CommSet applied to the whole program. Session values record every DSC step; "
            "generation-low5 and category membership are metadata, never an allowlist."
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
    raw_master: Any,
) -> list[dict[str, Any]]:
    section = db.sections.get(77)
    if section is None:
        return []
    if section.decoded_record_size != 52:
        raise ValueError(
            f"{category.get('database')}: type-77 record size {section.decoded_record_size}, expected 52"
        )
    category_id = int(category["category_id"])

    phases = {
        selector: _registry_request_row(parser, master, category_id, selector, name)
        for selector, name in ((0xD8, "start"), (0xD9, "stop"), (0xDA, "result"))
    }
    geometry_valid = all(
        phases[selector]["resolved"]
        and bool(phases[selector]["frames"])
        and all(
            frame["send"] == bytes((0x31, subfunction, 0xFF, 0xFF)).hex()
            and frame["check"] == bytes((0x71, subfunction)).hex()
            for frame in phases[selector]["frames"]
        )
        for selector, subfunction in ((0xD8, 1), (0xD9, 2), (0xDA, 3))
    )

    result = []
    for index, raw in enumerate(ddb_records(section)):
        name_index = struct.unpack_from("<I", raw, 0x00)[0]
        rid = struct.unpack_from("<H", raw, 0x14)[0]
        utility_id = struct.unpack_from("<H", raw, 0x16)[0]
        command_variable = struct.unpack_from("<H", raw, 0x1A)[0]
        stop_variable = struct.unpack_from("<H", raw, 0x1C)[0]
        command = _master_variable(raw_master, command_variable)
        stop_command = _master_variable(raw_master, stop_variable)
        geometry_ok = geometry_valid and rid not in {0, 0xFFFF}
        def materialize(selector: int, subfunction: int, suffix: str = "") -> list[dict[str, Any]]:
            if not geometry_ok:
                return []
            request = (bytes((0x31, subfunction)) + rid.to_bytes(2, "big")).hex() + suffix
            return [
                {"base_frame": frame, "materialized_static_request": request}
                for frame in phases[selector]["frames"]
            ]
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
            "selector_programs": {f"0x{key:X}": value for key, value in phases.items()},
            "start_frames": materialize(0xD8, 1, command["bytes"]),
            "stop_frames": materialize(0xD9, 2),
            "result_frames": materialize(0xDA, 3),
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
    *,
    raw_master: Any,
    gts_root: Path,
    context_identity: dict[str, Any],
    viewer_help: Any,
    viewer_identity: dict[str, Any],
) -> dict[str, Any]:
    db_path = Path(category["catalog_database_path"])
    db = parser.parse_ecu_db(db_path)
    monitor_rows = _monitor_rows(db, strings, db_path.name)
    bindings = _registry_role_bindings(parser, master, category, bin_root)
    selected_bindings = _registry_selected_role_bindings(parser, master, category, bin_root)
    category_id = int(category["category_id"])
    support_family = support.support_family(
        support.support_plugin(master, category_id, 0x67),
        support.support_plugin(master, category_id, 0xD5),
    )
    support_mode = support.support_mode(category_id, int(category["generation"]), support_family)
    def resolve_variable(key: int) -> bytes:
        return bytes.fromhex(_master_variable(raw_master if key > 10000 else db, key)["bytes"])

    rob_source = rob_source_catalog(db, strings, db_path.name, resolve_variable=resolve_variable)
    common = {
        "category": category,
        "p6_rob_source": _json_value({key: rob_source[key] for key in ("behavior_codes", "signals")}),
        "legacy_records": legacy_catalog_rows(
            db, strings, db_path.name,
            lambda key: bytes.fromhex(_master_variable(raw_master if key > 10000 else db, key)["bytes"]),
        ),
        "support_catalog": support_catalog(db, strings, db_path.name),
        "physical_catalog": physical_catalog(db, strings, db_path.name),
        "dynamic_lsb": _json_value(dynamic_lsb_rows(db)),
        "legacy_rob": _json_value(legacy_rob_catalog(db, strings, db_path.name)),
        "ddr": _json_value(p6_ddr_catalog(db, strings, db_path.name)),
        "work_factor": _json_value(work_factor_catalog(db, strings, db_path.name, viewer_help=viewer_help)),
        "native_ddr": _json_value(native_ddr_catalog(db, strings, db_path.name)),
        "ddr_behavior": _json_value(ddr_behavior_catalog(db, strings, db_path.name)),
        "trigger_catalog": _json_value(trigger_catalog(db, strings, db_path.name)),
        "active_test_support": _json_value(active_test_support_catalog(
            db, strings, db_path.name, resolve_variable=resolve_variable,
            variable_namespace=lambda key: "master" if key > 10000 else "ecu",
        )),
        "variable_drive": _json_value(variable_drive_catalog(db, strings, db_path.name)),
        "monitor_source": _json_value(monitor_source_catalog(
            db, strings, db_path.name, resolve_variable=resolve_variable,
        )),
        "obd_monitor": _json_value(obd_monitor_catalog(db, strings, db_path.name)),
        "diagnostic_metadata": _json_value(diagnostic_metadata(db, strings, db_path.name)),
        "dtc_source": _json_value(dtc_source_catalog(db, strings, db_path.name)),
        "active_test_source": _json_value(active_test_source_catalog(db, strings, db_path.name)),
        "source_tables": [
            {"table": table, "record_count": section.header.record_count,
             "record_size": section.decoded_record_size}
            for table, section in sorted(db.sections.items())
        ],
        "active_tests": _registry_active_tests(parser, master, category, db_root, strings, monitor_rows, selected_bindings),
        "functions": _registry_function_hierarchy(parser, raw_master, strings, category_id),
        "plugins": bindings,
        "selected_plugins": selected_bindings,
        "native_context": context_identity,
        "selection_boundary": "Initial category/DLL/frame selection is native-qualified; ECU catalog tables remain raw and unproved for live selection.",
        "commands": _registry_command_rows(parser, master, category, bin_root, selected_bindings),
        "selectors": _registry_selector_rows(parser, master, category_id),
        "active_test_groups": _registry_active_test_groups(parser, category, db_root, strings),
        "utilities": _simple_utility_rows(
            parser, master, category, db, strings, support_mode=support_mode, raw_master=raw_master,
        ),
        "source_identity": {
            "database": {
                "path": str(db_path.relative_to(gts_root)),
                "bytes": db_path.stat().st_size,
                "sha256": _file_sha256(db_path),
            },
            **({"viewer_help": viewer_identity} if db.sections.get(18) is not None else {}),
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
            resolve_variable=lambda variable_id: bytes.fromhex(_master_variable(raw_master, variable_id)["bytes"]),
        ),
            "rob": _rob_rows(db, strings, db_path.name),
        }
    if support_mode == "p6-standard":
        return {
            **common,
            **p6_catalog(
                db, strings, db_path.name,
                resolve_variable=lambda variable_id: bytes.fromhex(_master_variable(raw_master, variable_id)["bytes"]),
            ),
            "dtcs": _registry_dtc_catalog(parser, db, strings, db_path.name),
        }
    raise AssertionError(f"unreachable catalog support mode for category {category_id}: {support_mode!r}")


def _bundle_json_bytes(payload: Any) -> bytes:
    # Native query identities and plugin metadata may carry absolute source
    # paths internally. Persist portable repository-relative identities only.
    serialized = json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False)
    serialized = serialized.replace(str(REPO_ROOT) + "/", "")
    return (serialized + "\n").encode()


def _bundle_write_json(archive: zipfile.ZipFile, member: str, payload: Any) -> None:
    info = zipfile.ZipInfo(member, date_time=(1980, 1, 1, 0, 0, 0))
    info.compress_type = zipfile.ZIP_DEFLATED
    info.external_attr = 0o644 << 16
    archive.writestr(info, _bundle_json_bytes(payload))


def _bundle_customize_catalog(
    master: Any,
    strings: Any,
    category_by_id: dict[int, dict[str, Any]],
    context: Any,
) -> dict[str, Any]:
    """Recover current regional Toyota Customize catalog from master tables 20/21/22/34.

    These are master tables. GetCustomSupportList selects a
    body type and then table-20 groups. GetCustomItemList resolves table-21 by
    group id and table-22 by choice-list id; each item names the live target ECU.
    """
    def u16(raw: bytes, off: int) -> int:
        return struct.unpack_from("<H", raw, off)[0]

    def u32(raw: bytes, off: int) -> int:
        return struct.unpack_from("<I", raw, off)[0]

    choice_rows: dict[int, list[dict[str, Any]]] = {}
    for source_ordinal, raw in enumerate(ddb_records(master.sections[22])):
        key = u16(raw, 0x04)
        choice_rows.setdefault(key, []).append({
            "source_ordinal": source_ordinal,
            "raw": raw.hex(),
            "value": u16(raw, 0x06),
            "name": strings.get_string(u32(raw, 0x00)) or "",
            "name_string_index": u32(raw, 0x00),
            "exception_flag": raw[0x08],
            "exception_id": u16(raw, 0x0A),
        })
    for rows in choice_rows.values():
        rows.sort(key=lambda row: int(row["value"]))

    groups = []
    for source_ordinal, raw in enumerate(ddb_records(master.sections[20])):
        groups.append({
            "source_ordinal": source_ordinal,
            "raw": raw.hex(),
            "body_type": raw[0x08],
            "group_id": u16(raw, 0x04),
            "name": strings.get_string(u32(raw, 0x00)) or "",
            "name_string_index": u32(raw, 0x00),
            "exception_flag": raw[0x09],
            "exception_id": u16(raw, 0x0A),
        })
    groups.sort(key=lambda row: (int(row["body_type"]), int(row["group_id"])))

    items: list[dict[str, Any]] = []
    for source_ordinal, raw in enumerate(ddb_records(master.sections[21])):
        group_id = u16(raw, 0x08)
        item_id = u16(raw, 0x0A)
        target_category_id = u16(raw, 0x0C)
        choice_key = u16(raw, 0x20)
        all_default_gate = u16(raw, 0x22)
        target_query = context.query(16, target_category_id)
        target = category_by_id.get(target_category_id) if target_query.status == 0 and target_query.records else None
        items.append({
            "source_ordinal": source_ordinal,
            "raw": raw.hex(),
            "group_id": group_id,
            "item_id": item_id,
            "name": strings.get_string(u32(raw, 0x00)) or "",
            "name_string_index": u32(raw, 0x00),
            "metadata_dword_04": u32(raw, 0x04),
            "target_category_id": target_category_id,
            "target_category_name": str(target.get("name") or "") if target else "",
            "target_generation": int(target["generation"]) if target and target.get("generation") is not None else None,
            "target_native_query": target_query.as_dict(),
            "target_resolution": (
                context.as_dict()["resolution"] if target else
                "unknown" if target_query.status is None else
                "native-failure" if target_query.status != 0 else "missing"
            ),
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
            "target_route_selector": raw[0x2C],
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
    for source_ordinal, raw in enumerate(ddb_records(master.sections[34])):
        probes.append({
            "source_ordinal": source_ordinal,
            "raw": raw.hex(),
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
        "schema": "toyota-customize-catalog-v3",
        "native_context": context.as_dict(),
        "selection_boundary": "Groups/items/choices/probes are raw catalog occurrences, not proved live selection. Target category metadata is qualified by the supplied initial/event/unknown native context.",
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
    native_history: Path | None,
    history_known: bool,
) -> dict[str, Any]:
    """Build one Toyota-native regional resolver index plus decoded catalog shards."""
    db_root = gts_db_root(gts_root, region, family)
    parser = DDBParser()
    master_path = db_root / "Toyota.ddb"
    strings_path = db_root / "M_English.ddb"
    master = parser.parse_master_db(master_path)
    strings = _english_strings(parser, db_root)
    viewer_path = db_root / "Viewer.ddb"
    viewer_strings_path = db_root / "V_English.ddb"
    viewer_help = viewer_help_index(
        parser.parse_viewer_db(viewer_path), parser.load_string_db(viewer_strings_path), viewer_path.name,
    )
    viewer_identity = {
        key: {"path": str(path.relative_to(gts_root)), "bytes": path.stat().st_size,
              "sha256": _file_sha256(path)}
        for key, path in (("database", viewer_path), ("strings", viewer_strings_path))
    }
    context = native_selection_context(gts_root, region, history=native_history, history_known=history_known)
    initial_context = (
        context if native_history is None and history_known else
        native_selection_context(gts_root, region) if history_known else None
    )
    category_rows = _master_category_rows(parser, master, strings)
    initial_categories = [] if initial_context is None else [
        _resolve_master_category(parser, initial_context, strings, str(category_id))
        for category_id in dict.fromkeys(row.category_id for row in initial_context.active_records(16))
    ]
    initial_context_identity = initial_context.as_dict() if initial_context is not None else None
    category_ids = dict.fromkeys(row.category_id for row in context.raw_records(16, family="Gen"))
    category_resolution = {str(key): context.query(16, key) for key in category_ids}
    selected_categories = [
        _resolve_master_category(parser, context, strings, key)
        for key, result in category_resolution.items()
        if result.status == 0 and result.records
    ]

    # Catalog availability follows the selected source database, independently
    # of which support plugin a live diagnostic session uses.
    catalog_categories = []
    for row in selected_categories:
        category_id = int(row["category_id"])
        cached = context.file(ecu_id=category_id, family=family)
        source_path = Path(cached.source.path) if cached is not None else db_root / str(row["database"])
        if not row.get("database") or not source_path.is_file():
            continue
        catalog_categories.append(native_ecu_catalog_category(context, row, db_root, parser))
    catalog_ids = {int(row["category_id"]) for row in catalog_categories}
    catalog_by_id = {int(row["category_id"]): row for row in catalog_categories}
    context_identity = context.as_dict()

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
    category_by_id = {
        int(row["category_id"]): catalog_by_id.get(int(row["category_id"]), row)
        for row in selected_categories
    }
    for row in selected_categories:
        category_id = int(row["category_id"])
        item = dict(category_by_id[category_id])
        item["generation_low5"] = int(row["generation"]) & 0x1F
        single = support.support_plugin(context, category_id, 0x67)
        multi = support.support_plugin(context, category_id, 0xD5)
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
        route_selector = raw[0x13]
        route_key = f"{category_id}:{route_selector}"
        if route_key not in routes:
            try:
                routes[route_key] = _bundle_protocol_route(master, category_id, route_selector)
            except ValueError:
                route_key = None
        install_sets.setdefault(str(install_set_id), []).append({
            "category_id": category_id,
            "connection_frame_id": frame_id,
            "connection_comm_set_id": comm_set_id,
            "connection_route_selector": route_selector,
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
        "route_selector": raw[0x12],
        "vin_prefix_hex": raw[0x13:0x1E].hex(),
    } for raw in ddb_records(master.sections[59])]
    type41_rows = _bundle_vehicle_decision_rows(master)
    vehicle_program = _bundle_special_vehicle_program(gts_root, region, parser, context)
    bin_root = gts_root / "bin"
    vehicle_roles = {}
    for role, semantic in ((0x45, "legacy_select_vehicle"), (0x4A, "legacy_select_vehicle_vin"), (0x7D, "vin10_select_vehicle")):
        query = context.query(19, role, 0)
        if query.status is None or query.status != 0:
            vehicle_roles[f"0x{role:02X}"] = {"semantic": semantic, "native": query.as_dict()}
            continue
        selected = support.support_plugin(context, 0, role)
        if selected is None:
            continue
        dll = str(selected["dll"])
        vehicle_roles[f"0x{role:02X}"] = {
            **selected,
            "semantic": semantic,
            "binary_present_in_current_gtsplus": _resolve_plugin_path(bin_root, dll).is_file(),
        }

    session_categories = [{"category_id": category_id} for category_id in category_ids]
    region_index = {
        "region": region,
        "vehicles": vehicles,
        "vin_decision": {
            "path": "P5/P6 final resolver; P3/P4 candidate/source stage before type-41",
            "key": "category_id + route_selector + VIN[0:11], with flags bits 0..10 as per-position wildcards",
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
        "category_rows": category_rows,
        "raw_category_occurrences": [row.as_dict() for row in context.raw_records(16)],
        "initial_categories": (
            {str(row["category_id"]): row for row in initial_categories} if initial_context is not None else None
        ),
        "initial_native_context": initial_context_identity,
        "selected_categories": category_index,
        "category_resolution": {key: value.as_dict() for key, value in category_resolution.items()},
        "raw_role_bindings": [row.as_dict() for row in context.raw_records(19)],
        "native_context": context_identity,
        "raw_catalog_boundary": "Install sets, routes, vehicle decisions, Customize tables and ECU catalogs are raw/unproved live selection; native proof covers only category/DLL/selector/frame/CommSet/timer tables.",
        "install_sets": install_sets,
        "routes": routes,
        "connection_frames": {
            str(frame_id): _bundle_connection_frame(context, frame_id)
            for frame_id in sorted(connection_frame_ids)
        },
        "commsets": {
            str(key): _bundle_comm_set(context, key)
            for key in dict.fromkeys(struct.unpack_from("<H", row.raw, 10)[0] for row in context.raw_records(29))
        },
        "session_control": _bundle_session_control(parser, context, session_categories),
        "utilities": _registry_utilities(parser, context),
        "customize_member": f"customize/{region}/0.json",
        "can_topology": _bundle_can_topologies(parser, master, strings, vehicle_types_with_routes),
        "counts": {
            "vehicle_count": len(vehicles),
            "install_set_count": len(install_sets),
            "raw_category_row_count": len(category_rows),
            "initial_category_count": len(initial_categories) if initial_context is not None else None,
            "selected_category_count": len(category_index),
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
                "path": str(master_path.relative_to(gts_root)),
                "bytes": master_path.stat().st_size,
                "sha256": _file_sha256(master_path),
            },
            "strings": {
                "path": str(strings_path.relative_to(gts_root)),
                "bytes": strings_path.stat().st_size,
                "sha256": _file_sha256(strings_path),
            },
            "special_master": vehicle_program["source_identity"]["special_master"],
        },
    }

    with zipfile.ZipFile(part_path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6) as archive:
        customize = _bundle_customize_catalog(master, strings, category_by_id, context)
        customize["source_identity"] = region_index["source_identity"]
        _bundle_write_json(archive, f"customize/{region}/0.json", customize)
        for category in sorted(catalog_categories, key=lambda row: int(row["category_id"])):
            category_id = int(category["category_id"])
            payload = _bundle_category_catalog(
                parser, context, strings, db_root, bin_root, category,
                raw_master=master, gts_root=gts_root, context_identity=context_identity,
                viewer_help=viewer_help, viewer_identity=viewer_identity,
            )
            _bundle_write_json(archive, f"catalogs/{region}/{category_id}.json", payload)
    return region_index



def write_toyota_diag_bundle(
    gts_root: Path,
    out: Path,
    *,
    family: str = "Gen",
    regions: tuple[str, ...] = TOYOTA_DIAG_BUNDLE_REGIONS,
    native_history: Path | None = None,
    history_known: bool = True,
) -> dict[str, Any]:
    """Write canonical diagnostic members consumed directly by offline tooling.

    Each regional master is derived in an independent worker. Temporary regional
    ZIPs stay in the build workspace; only deterministic gzip members and their
    ordered integrity manifest are retained in the output directory.
    """
    resolver_artifact = json.loads(VEHICLE_RESOLVER.read_text())
    if resolver_artifact.get("release") != "2026.03.002.02":
        raise ValueError("current vehicle resolver release drift")
    index: dict[str, Any] = {
        "schema": TOYOTA_DIAG_BUNDLE_SCHEMA,
        "profile": TOYOTA_DIAG_BUNDLE_PROFILE,
        "release": resolver_artifact["release"],
        "default_region": regions[0],
        "native_context_request": {"history_known": history_known, "history_supplied": native_history is not None},
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
                    "selector_excluded": [f"0x{selector:04X}" for selector in range(0xD1F0, 0xD1FF)],
                    "member_base": "(selector & 0x00FF) << 8",
                    "member_shift": 0,
                    "selector_ids_remain_supported": True,
                    "hierarchy": "D100-root bitmap -> D1nn selector IDs; query D1nn except inclusive D1F0..D1FE -> nn00..nnFF RID bitmap",
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
            "Raw category and role occurrences remain separate from initial and supplied-context native snapshots. "
            "Native proof covers tables 16/17/18/19/25/29 only; other catalogs and vehicle/install/route tables are raw/unproved live selection. "
            "Catalog availability is not an ECU-support gate. Exact raw row bytes and source hashes are retained; executable Toyota binaries are not embedded."
        ),
    }
    if native_history is not None:
        index["source_identity"]["native_history"] = {
            "path": str(native_history.resolve().relative_to(REPO_ROOT)),
            "bytes": native_history.stat().st_size,
            "sha256": _file_sha256(native_history),
        }

    out.parent.mkdir(parents=True, exist_ok=True)
    if out.exists() and not (out / "manifest.json").is_file():
        raise ValueError(f"refusing to replace a non-bundle directory: {out}")
    with tempfile.TemporaryDirectory(prefix="toyota-diag-bundle-", dir=out.parent) as workspace_text:
        workspace = Path(workspace_text)
        part_paths = {region: workspace / f"{region}.zip" for region in regions}
        workers = min(len(regions), 3)
        with ProcessPoolExecutor(max_workers=workers) as executor:
            futures = {
                executor.submit(
                    _build_toyota_diag_region, gts_root, family, region, part_paths[region],
                    native_history, history_known,
                ): region
                for region in regions
            }
            for future in as_completed(futures):
                region = futures[future]
                index["regions"][region] = future.result()

        canonical = workspace / "bundle"
        writer = DiagnosticBundleWriter(canonical)
        for region in regions:
            with zipfile.ZipFile(part_paths[region]) as part:
                names = sorted(part.namelist(), key=lambda name: int(Path(name).stem))
                for name in names:
                    with part.open(name) as source:
                        writer.add(name, source)
        writer.add("index.json", io.BytesIO(_bundle_json_bytes(index)))
        writer.finish()
        if out.exists():
            shutil.rmtree(out)
        canonical.replace(out)
    return index
