"""Category+role command planning: binds master plugin rows to recovered plugin semantic profiles and category DB plans."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pefile

from tools.techstream.gts.active_tests import (
    _active_test_init_selected_plan,
    _active_test_list_category_plan,
    _active_test_monitor_category_plan,
    _active_test_signal_info_selected_plan,
    _monitor_list_category_plan,
    _multi_active_test_category_plan,
    _multi_active_test_group_plan,
)
from tools.techstream.diagnostic_role_model import plugin_operation_signature
from tools.techstream.gts.execution_model import _file_sha256, _semantic_profile_for_plugin
from tools.techstream.gts.master import _master_command_binding, _master_frame_rows, _master_timer_rows
from tools.techstream.parse_ddb import DDBParser, StringDataBase


def _master_command_plan(
    parser: DDBParser,
    master: Any,
    category: dict[str, Any],
    role: int,
    bin_root: Path,
    db_root: Path | None = None,
    selected_item: int | None = None,
    strings: StringDataBase | None = None,
) -> dict[str, Any]:
    category_id = int(category["category_id"])
    binding = _master_command_binding(parser, master, category_id, role)
    plugin_path = bin_root / binding.dll_name
    if plugin_path.is_file():
        try:
            operation = plugin_operation_signature(plugin_path)
        except pefile.PEFormatError:
            operation = {"surface": "plugin_pe_unparseable"}
        identity = {
            "path": plugin_path.name,
            "size": plugin_path.stat().st_size,
            "sha256": _file_sha256(plugin_path),
        }
    else:
        operation = {"surface": "plugin_file_missing"}
        identity = {"path": plugin_path.name, "size": None, "sha256": None}

    profile_name, profile, semantic_status = _semantic_profile_for_plugin(plugin_path, role)
    result: dict[str, Any] = {
        "category": category,
        "role": role,
        "role_hex": f"0x{role:X}",
        "plugin": binding.dll_name,
        "plugin_identity": identity,
        "operation_surface": operation["surface"],
        "semantic_status": semantic_status,
        "semantic_profile": profile_name,
        "frames": {},
        "timers": [],
        "response_model": None,
        "control_flow": None,
        "metadata_model": None,
        "list_model": None,
        "active_test_model": None,
        "active_test_init_model": None,
        "active_test_signal_info_model": None,
        "active_test_monitor_model": None,
        "multi_active_test_init_model": None,
        "boundary": (
            "Frames/timers are resolved from the selected category. Executable semantics are attached only "
            "when the selected plugin SHA-256 exactly matches a recovered profile."
        ),
    }
    if selected_item is not None and role not in {0x08, 0x63, 0x70}:
        raise ValueError("--item is currently supported only for Active Test roles 0x08, 0x63, and 0x70")
    if profile is None:
        return result

    if profile_name == "role_0x63_p5_multi_active_test_init":
        result["multi_active_test_init_model"] = dict(profile["init_model"])
        if db_root is not None:
            result["multi_active_test_init_model"]["category_plan"] = _multi_active_test_category_plan(
                parser, category, db_root
            )
            result["semantic_status"] = "exact_plugin_identity_and_category_multi_active_test_census"
        if selected_item is not None:
            if db_root is None or strings is None:
                raise ValueError("role-0x63 selected-group planning requires the category ECU database and strings")
            result["multi_active_test_init_model"]["selected_plan"] = _multi_active_test_group_plan(
                parser, master, category, db_root, selected_item, strings
            )
            result["semantic_status"] = "exact_plugin_identity_and_selected_multi_active_test_plan"
    elif profile_name == "role_0xad_p5_monitor_list_for_active_test":
        result["active_test_monitor_model"] = dict(profile["list_model"])
        if db_root is not None:
            result["active_test_monitor_model"]["category_plan"] = _active_test_monitor_category_plan(
                parser, category, db_root
            )
            result["semantic_status"] = "exact_plugin_identity_and_category_active_test_monitor_partition"
        else:
            result["semantic_status"] = "exact_plugin_identity_active_test_monitor_semantics"
    elif profile_name == "role_0x70_p5_active_test_signal_info":
        result["active_test_signal_info_model"] = dict(profile["metadata_model"])
        if selected_item is not None:
            if db_root is None or strings is None:
                raise ValueError("role-0x70 selected-item planning requires the category ECU database and strings")
            result["active_test_signal_info_model"]["selected_plan"] = _active_test_signal_info_selected_plan(
                parser, category, db_root, selected_item, strings
            )
            result["semantic_status"] = "exact_plugin_identity_and_selected_active_test_signal_info"
        else:
            result["semantic_status"] = "exact_plugin_identity_requires_selected_active_test"
    elif profile_name == "role_0x08_p5_active_test_init":
        result["active_test_init_model"] = dict(profile["init_model"])
        if selected_item is not None:
            if db_root is None:
                raise ValueError("role-0x08 selected-item planning requires the category ECU database")
            result["active_test_init_model"]["selected_plan"] = _active_test_init_selected_plan(
                parser, master, category, db_root, selected_item, strings
            )
            result["semantic_status"] = "exact_plugin_identity_and_selected_active_test_plan"
        else:
            result["semantic_status"] = "exact_plugin_identity_requires_selected_active_test"
    elif profile_name == "role_0x06_p5_active_test_list":
        result["active_test_model"] = dict(profile["list_model"])
        if db_root is not None:
            result["active_test_model"]["category_plan"] = _active_test_list_category_plan(parser, category, db_root)
            result["semantic_status"] = "exact_plugin_identity_and_category_active_test_partition"
        else:
            result["semantic_status"] = "exact_plugin_identity_active_test_list_semantics"
    elif profile_name == "role_0x05_p5_monitor_list":
        result["list_model"] = dict(profile["list_model"])
        if db_root is not None:
            result["list_model"]["category_plan"] = _monitor_list_category_plan(parser, category, db_root)
            result["semantic_status"] = "exact_plugin_identity_and_category_candidate_partition"
        else:
            result["semantic_status"] = "exact_plugin_identity_monitor_list_semantics"
    elif profile_name == "role_0x41_p5_signal_info":
        result["metadata_model"] = profile["metadata_model"]
        result["semantic_status"] = "exact_plugin_identity_metadata_only"
    elif profile_name == "role_0x52_generic_cid":
        rows = _master_frame_rows(parser, master, category_id, 0xDC)
        result["frames"]["request"] = rows[0] if len(rows) == 1 else None
        result["response_model"] = profile["response_model"]
        result["semantic_status"] = (
            "exact_plugin_identity_and_category_frame"
            if len(rows) == 1
            else "exact_plugin_identity_but_category_selector_0xDC_missing"
        )
    elif profile_name == "role_0x19_dtc_clear":
        primary = _master_frame_rows(parser, master, category_id, 0x01)
        fallback = _master_frame_rows(parser, master, category_id, 0x102)
        result["frames"]["primary"] = primary[0] if len(primary) == 1 else None
        result["frames"]["fallback"] = fallback[0] if len(fallback) == 1 else None
        result["timers"] = [row for row in _master_timer_rows(parser, master, category_id) if row["timer_id"] == 1]
        result["control_flow"] = profile["control_flow"]
        result["semantic_status"] = (
            "exact_plugin_identity_and_primary_frame"
            if len(primary) == 1
            else "exact_plugin_identity_but_primary_selector_0x1_missing"
        )
    return result
