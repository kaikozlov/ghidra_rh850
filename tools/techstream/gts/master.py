"""Toyota master DDB domain: ECU categories, DLL roles/plugins, functions, variables, timers, CommSets, FuncCommFrames, CAN Bus Check topology."""

from __future__ import annotations

import struct
from pathlib import Path
from typing import Any

from tools.techstream.gts.ddb import _fold_match
from tools.techstream.ddb_semantics import records as ddb_records
from tools.techstream.diagnostic_role_model import role_operation_catalog
from tools.techstream.parse_ddb import DDBParser, StringDataBase


def _parse_master_key(value: str) -> int | None:
    try:
        return int(value, 0)
    except ValueError:
        return None


def _master_category_rows(parser: DDBParser, master: Any, strings: StringDataBase) -> list[dict[str, Any]]:
    return [
        {
            "category_id": entry.category_id,
            "generation": entry.generation,
            "database": entry.database_name,
            "short_name": entry.ecu_short_name,
            "name": strings.get_string(entry.ecu_name_string_index) or "",
        }
        for entry in parser.extract_master_ecu_categories(master.sections[16])
    ]


def _resolve_master_category(parser: DDBParser, master: Any, strings: StringDataBase, query: str) -> dict[str, Any]:
    rows = _master_category_rows(parser, master, strings)
    numeric = _parse_master_key(query)
    if numeric is not None:
        matches = [row for row in rows if row["category_id"] == numeric]
    else:
        exact = [
            row for row in rows
            if query.casefold() in {
                row["database"].casefold(),
                Path(row["database"]).stem.casefold(),
                row["short_name"].casefold(),
                row["name"].casefold(),
            }
        ]
        matches = exact or [
            row for row in rows
            if _fold_match(query, row["database"], row["short_name"], row["name"])
        ]
    if not matches:
        raise SystemExit(f"no Toyota master ECU category matches {query!r}")
    category_ids = {row["category_id"] for row in matches}
    if len(category_ids) != 1:
        summary = "\n".join(
            f"  {row['category_id']}\t{row['database']}\t{row['name']}"
            for row in matches[:40]
        )
        raise SystemExit(f"ambiguous Toyota master ECU category {query!r}; matches:\n{summary}")
    return matches[0]


def _master_role_catalog(parser: DDBParser, master: Any, bin_root: Path | None = None) -> list[dict[str, Any]]:
    if bin_root is not None:
        return role_operation_catalog(parser, master, bin_root)["roles"]
    by_role: dict[int, list[Any]] = {}
    for entry in parser.extract_master_dlls(master.sections[19]):
        by_role.setdefault(entry.dll_role_id, []).append(entry)
    rows = []
    for role, entries in by_role.items():
        plugin_counts: dict[str, int] = {}
        for entry in entries:
            plugin_counts[entry.dll_name] = plugin_counts.get(entry.dll_name, 0) + 1
        plugins = [
            {"dll": dll, "binding_count": count}
            for dll, count in sorted(plugin_counts.items(), key=lambda item: (-item[1], item[0].casefold()))
        ]
        rows.append({
            "role": role,
            "role_hex": f"0x{role:X}",
            "binding_count": len(entries),
            "category_count": len({entry.category_id for entry in entries}),
            "plugins": plugins,
        })
    return sorted(rows, key=lambda row: (-row["binding_count"], row["role"]))


def _master_plugins(parser: DDBParser, master: Any, category_id: int) -> list[dict[str, Any]]:
    return [
        {"role": entry.dll_role_id, "role_hex": f"0x{entry.dll_role_id:X}", "dll": entry.dll_name}
        for entry in sorted(
            (row for row in parser.extract_master_dlls(master.sections[19]) if row.category_id == category_id),
            key=lambda row: (row.dll_role_id, row.dll_name.casefold()),
        )
    ]


def _master_functions(parser: DDBParser, master: Any, strings: StringDataBase, category_id: int) -> list[dict[str, Any]]:
    return [
        {
            "function_id": entry.function_id,
            "function_hex": f"0x{entry.function_id:X}",
            "sort_key": entry.sort_key,
            "name": strings.get_string(entry.name_string_index) or "",
            "description": strings.get_string(entry.description_string_index) or "",
        }
        for entry in parser.extract_master_functions(master.sections[26])
        if entry.category_id == category_id
    ]


def _master_variable(master: Any, variable_id: int) -> dict[str, Any]:
    if variable_id == 0:
        return {"id": "0x0", "normalized_id": "0x0", "bytes": ""}
    # Current GTS+ CDbVariableTable::GetVariable namespaces references above
    # decimal 10000 (0x2710); subtract before the unchanged 1-based table lookup.
    normalized = variable_id - 0x2710 if variable_id > 0x2710 else variable_id
    section = master.sections[0]
    count = section.header.record_count
    if not 1 <= normalized <= count:
        raise ValueError(
            f"variable 0x{variable_id:X} normalizes to 0x{normalized:X}, outside 1..{count}"
        )
    data = section.decoded_data
    table_end = count * 6
    rel, length = struct.unpack_from("<IH", data, (normalized - 1) * 6)
    start = table_end + rel
    end = start + length
    if end > len(data):
        raise ValueError(f"variable 0x{variable_id:X} overruns variable pool")
    return {
        "id": f"0x{variable_id:X}",
        "normalized_id": f"0x{normalized:X}",
        "bytes": data[start:end].hex(),
    }


def _master_timer_rows(parser: DDBParser, master: Any, category_id: int | None = None) -> list[dict[str, Any]]:
    rows = [
        {
            "category_id": entry.category_id,
            "timer_id": entry.timer_id,
            "delay_ms": entry.delay_ms,
            "unknown_dword_08": entry.unknown_dword_08,
            "raw": entry.raw.hex(),
        }
        for entry in parser.extract_master_timers(master.sections[25])
        if category_id is None or entry.category_id == category_id
    ]
    return sorted(rows, key=lambda row: (row["category_id"], row["timer_id"]))


def _master_command_binding(parser: DDBParser, master: Any, category_id: int, role: int) -> Any:
    matches = [
        entry for entry in parser.extract_master_dlls(master.sections[19])
        if entry.category_id == category_id and entry.dll_role_id == role
    ]
    if len(matches) != 1:
        raise ValueError(f"category {category_id} role 0x{role:X} resolved {len(matches)} plugin bindings")
    return matches[0]


def _master_comm_set_rows(parser: DDBParser, master: Any) -> list[dict[str, Any]]:
    return [
        {
            "comm_set_id": entry.comm_set_id,
            "send_parameter": entry.send_parameter,
            "receive_timeout": entry.receive_timeout,
            "exception_handler_id": entry.exception_handler_id,
            "unknown_word_0c": entry.unknown_word_0c,
            "retry_count": entry.retry_count,
            "exception_handler_flag": entry.exception_handler_flag,
            "raw": entry.raw.hex(),
        }
        for entry in parser.extract_master_comm_sets(master.sections[29])
    ]


def _master_frame_rows(parser: DDBParser, master: Any, category_id: int, selector: int | None = None) -> list[dict[str, Any]]:
    """Resolve CDbFuncCommFrame rows using one index per parsed Toyota master."""
    cache = getattr(master, "_gts_frame_index", None)
    if cache is None:
        func = master.sections[18]
        frame_table = master.sections[17]
        func_size = func.decoded_record_size
        frame_size = frame_table.decoded_record_size
        frames = {
            struct.unpack_from("<H", raw, 0)[0]: raw
            for raw in (
                frame_table.decoded_data[i * frame_size : (i + 1) * frame_size]
                for i in range(frame_table.header.record_count)
            )
        }
        functions: dict[int, list[tuple[int, int, int, bytes]]] = {}
        for i in range(func.header.record_count):
            raw = func.decoded_data[i * func_size : (i + 1) * func_size]
            category, row_selector, comm_set, frame_id = struct.unpack_from("<HHHH", raw, 0)
            functions.setdefault(category, []).append((row_selector, comm_set, frame_id, raw))
        commsets = {row["comm_set_id"]: row for row in _master_comm_set_rows(parser, master)}
        cache = {"frames": frames, "functions": functions, "commsets": commsets}
        master._gts_frame_index = cache

    rows = []
    for row_selector, comm_set, frame_id, raw in cache["functions"].get(category_id, []):
        if selector is not None and row_selector != selector:
            continue
        frame = cache["frames"].get(frame_id)
        if frame is None:
            raise ValueError(f"category {category_id} selector 0x{row_selector:X}: missing frame 0x{frame_id:X}")
        comm_set_metadata = cache["commsets"].get(comm_set)
        if comm_set_metadata is None:
            raise ValueError(f"category {category_id} selector 0x{row_selector:X}: missing CommSet {comm_set}")
        send_var, mask_var, check_var = struct.unpack_from("<HHH", frame, 2)
        rows.append({
            "kind": "frame",
            "category_id": category_id,
            "selector": f"0x{row_selector:X}",
            "comm_set": comm_set,
            "comm_set_metadata": comm_set_metadata,
            "comm_frame_id": f"0x{frame_id:X}",
            "send": _master_variable(master, send_var),
            "receive_mask": _master_variable(master, mask_var),
            "receive_check": _master_variable(master, check_var),
            "func_comm_frame_raw": raw.hex(),
            "comm_frame_raw": frame.hex(),
        })
    return rows


def _master_canbus_topology_rows(parser: DDBParser, master: Any, strings: Any, query: str) -> list[dict[str, Any]]:
    """Resolve Toyota master CAN Bus Check topology for a vehicle type/name."""
    required = (55, 75, 76, 77, 78, 79)
    missing = [table_id for table_id in required if table_id not in master.sections]
    if missing:
        raise SystemExit(f"master database lacks CAN Bus Check tables: {missing}")

    vehicle_names = {
        struct.unpack_from("<I", raw, 4)[0]: strings.get_string(struct.unpack_from("<I", raw, 0)[0])
        for raw in ddb_records(master.sections[43])
    }
    try:
        vehicle_type = int(query, 0)
    except ValueError:
        vehicle_type = None
    if vehicle_type is not None:
        matches = [vehicle_type] if vehicle_type in vehicle_names else []
    else:
        matches = sorted(
            vehicle_type for vehicle_type, name in vehicle_names.items()
            if name and query.casefold() in name.casefold()
        )
    if not matches:
        raise SystemExit(f"no Toyota master vehicle type/name matches {query!r}")

    car_rows = list(ddb_records(master.sections[75]))
    option_rows = list(ddb_records(master.sections[77]))
    component_rows = list(ddb_records(master.sections[78]))
    subbus_names = {
        struct.unpack_from("<I", raw, 0)[0]: strings.get_string(struct.unpack_from("<I", raw, 4)[0])
        for raw in ddb_records(master.sections[76])
    }
    bus_names = {
        struct.unpack_from("<I", raw, 8)[0]: strings.get_string(struct.unpack_from("<I", raw, 4)[0])
        for raw in ddb_records(master.sections[79])
    }
    gateway_names: dict[int, set[str]] = {}
    for raw in ddb_records(master.sections[55]):
        bus_index = struct.unpack_from("<H", raw, 8)[0]
        gateway_names.setdefault(bus_index, set()).add(strings.get_string(struct.unpack_from("<I", raw, 4)[0]))

    out = []
    for vehicle_type in matches:
        vehicle_car_rows = [raw for raw in car_rows if struct.unpack_from("<I", raw, 4)[0] == vehicle_type]
        for car_raw in vehicle_car_rows:
            car_id = struct.unpack_from("<I", car_raw, 0)[0]
            options = [raw for raw in option_rows if struct.unpack_from("<I", raw, 0)[0] == car_id]
            placement_variants: dict[tuple, dict[str, Any]] = {}
            for option in options:
                group = struct.unpack_from("<I", option, 44)[0]
                rows = [raw for raw in component_rows if struct.unpack_from("<I", raw, 0)[0] == group]
                placements = []
                shape = []
                for raw in sorted(rows, key=lambda item: (struct.unpack_from("<H", item, 8)[0], item[14])):
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
                        "junction_name": strings.get_string(struct.unpack_from("<I", raw, 4)[0]),
                    }
                    placements.append(row)
                    shape.append((component_index, domain, bus_index, row["bus_name"]))
                shape_key = tuple(shape)
                existing = placement_variants.get(shape_key)
                if existing is None:
                    placement_variants[shape_key] = {
                        "component_groups": [f"0x{group:08X}"],
                        "placements": placements,
                    }
                else:
                    existing["component_groups"].append(f"0x{group:08X}")
            out.append({
                "vehicle_type": vehicle_type,
                "vehicle_name": vehicle_names[vehicle_type],
                "can_bus_car_id": f"0x{car_id:08X}",
                "option_count": len(options),
                "placement_variant_count": len(placement_variants),
                "placement_variants": list(placement_variants.values()),
            })
    if not out:
        raise SystemExit(f"vehicle match {query!r} has no CAN Bus Check topology row")
    return out
