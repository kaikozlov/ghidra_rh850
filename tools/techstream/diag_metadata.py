"""Restore the diagnostic product's closed set of semantic references."""

from __future__ import annotations

import sqlite3
from typing import Any

from tools.techstream import (
    diag_customize_semantics,
    diag_decoded_monitors,
    diag_native_recorder,
    diag_ecu_configurations,
    diag_freeze_physical,
    diag_operation_plans,
    diag_product_active,
    diag_product_behavior_codes,
    diag_product_dtc_sources,
    diag_product_dtcs,
    diag_product_freeze_signals,
    diag_product_legacy_conditions,
    diag_product_legacy_operations,
    diag_product_legacy_rob,
    diag_product_memberships,
    diag_product_recorder,
    diag_signal_observations,
    diag_signal_records,
    diag_support_semantics,
    diag_topology,
    diag_vehicle_index,
    diag_work_semantics,
)

READERS = {
    "$behavior_code": diag_product_behavior_codes.restore_behavior_code,
    "$diagnostic_code": diag_product_dtcs.restore,
    "$dtc_source_definition": diag_product_dtc_sources.restore,
    "$legacy_rob_signal": diag_product_legacy_rob.restore,
    "$legacy_freeze_signal": diag_product_freeze_signals.restore,
    "$legacy_condition": diag_product_legacy_conditions.restore_condition,
    "$legacy_dynamic": diag_product_legacy_conditions.restore_dynamic,
    "$legacy_response_definition": diag_product_legacy_conditions.restore_response,
    "$signal_observation": diag_signal_observations.restore,
    "$signal_definition": diag_signal_records.restore_definition,
    "$data_list_row": diag_signal_records.restore_display,
    "$signal_info": diag_signal_records.restore_info,
    "$did_support": diag_signal_records.restore_support,
    "$support_condition": diag_signal_records.restore_condition,
    "$freeze_physical": diag_freeze_physical.restore_freeze_physical,
    "$can_topology": diag_topology.restore_topology,
    "$legacy_operation": diag_product_legacy_operations.restore,
    "$legacy_operation_pattern": diag_product_legacy_operations.restore_pattern,
    "$operation_plan": diag_operation_plans.restore,
    "$ecu_catalog": diag_ecu_configurations.restore,
}
for kind in (
    "ddr_signal",
    "ddr_behavior_signal",
    "ddr_condition",
    "ddr_behavior_condition",
    "ddr_data_id",
    "ddr_trigger",
    "ddr_behavior_code",
):
    READERS["$" + kind] = lambda db, identity, kind=kind: diag_product_recorder.restore(
        db, kind, identity
    )
for kind in diag_native_recorder.SPECS:
    READERS["$native_recorder_" + kind] = lambda db, identity, kind=kind: (
        diag_native_recorder.restore(db, kind, identity)
    )
for kind in diag_decoded_monitors.SPECS:
    READERS["$decoded_" + kind] = lambda db, identity, kind=kind: (
        diag_decoded_monitors.restore(db, kind, identity)
    )
for markers, reader in (
    (
        ("$customize_item", "$customize_group"),
        diag_customize_semantics.restore_customize,
    ),
    (
        ("$work_standard", "$work_pattern", "$work_factor_definition"),
        diag_work_semantics.restore_work_semantic,
    ),
    (
        ("$vehicle_definition", "$install_set", "$vehicle_route"),
        diag_vehicle_index.restore_vehicle_index,
    ),
    (diag_support_semantics.MARKERS, diag_support_semantics.restore),
    (diag_product_memberships.MARKERS, diag_product_memberships.restore),
    (
        (
            "$operation_base_frame",
            "$operation_frame",
            "$operation_encoding",
            "$operation_mask",
            "$operation_conversion",
        ),
        diag_product_active.restore,
    ),
):
    for marker in markers:
        READERS[marker] = lambda db, identity, marker=marker, reader=reader: reader(
            db, marker, identity
        )


def restore(db: sqlite3.Connection, value: Any) -> Any:
    """Expand product references with cycle checks and independent output trees."""
    objects: dict[tuple[str, int], Any] = {}
    active: set[tuple[str, int]] = set()

    def expand(node):
        if isinstance(node, list):
            return [expand(child) for child in node]
        if not isinstance(node, dict):
            return node
        markers = [key for key in node if key.startswith("$")]
        if not markers:
            return {key: expand(child) for key, child in node.items()}
        marker = markers[0]
        if marker not in READERS and marker != "$part":
            raise ValueError(f"unknown product reference {marker}")
        identity = node[marker]
        if len(node) != 1 or type(identity) is not int or identity <= 0:
            raise ValueError(f"invalid {marker} reference")
        # Document-part assembly belongs to the document reader. It validates
        # each pointer against its owner and loads the selected semantic part.
        if marker == "$part":
            return {marker: identity}
        key = (marker, identity)
        if key in active:
            raise ValueError(f"cyclic {marker} reference")
        if key not in objects:
            objects[key] = READERS[marker](db, identity)
        active.add(key)
        try:
            return expand(objects[key])
        finally:
            active.remove(key)

    return expand(value)
