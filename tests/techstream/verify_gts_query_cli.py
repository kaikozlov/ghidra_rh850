#!/usr/bin/env python3
"""Verify the unified GTS+ query/recovery CLI against pinned external artifacts."""
from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
from pathlib import Path
from unittest.mock import patch

from tools import REPO_ROOT

import tools.techstream.ddb_strings as ddb_strings
import tools.techstream.pe_utils as pe_utils
from tools.techstream import techstream_paths
from tools.techstream.gts import active_tests, commands, cuw, ddb, query
from tools.techstream.gts import master as gts_master
from tools.techstream.parse_ddb import DDBParser, ECU_TABLE_CLASS_NAMES

ROOT = REPO_ROOT


def check(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)
    print(f"[PASS] {message}")


gts = techstream_paths.resolve_gts_root()
db_root = techstream_paths.gts_db_root(gts)
cuwplus = techstream_paths.resolve_cuwplus_root(gts)
corpus = techstream_paths.resolve_cuw_corpus()

check((db_root / "EMPS_P5.ddb").is_file(), "current GTS+ EMPS_P5 database is available")
check((db_root / "M_English.ddb").is_file(), "current GTS+ English OEM string database is available")
check((cuwplus / "Ini/P5-Unified04.ini").is_file(), "current CUWPlus P5-Unified04 route is available")
check((corpus / "T-0051-26.cuw").is_file(), "pinned Camry CUW is available")

with tempfile.TemporaryDirectory(prefix="gts-cli-cwd-") as td:
    result = subprocess.run(
        [str(ROOT / "tools/gts"), "category", "HV_P5", "--json", "--limit", "1"],
        cwd=td, capture_output=True, text=True, check=True,
    )
    category_response = json.loads(result.stdout)
    check(
        category_response["category"]["category_id"] == 397
        and category_response["category"]["name"] == "Hybrid Control",
        "public category query emits one JSON document without text-renderer fallthrough",
    )

with tempfile.TemporaryDirectory(prefix="gts-recorder-schema-") as td:
    fixture = Path(td)
    generated = fixture / "data/generated/gtsplus_2026"
    generated.mkdir(parents=True)
    tss3_fields = [
        {"DataID": "5A08", "DataName": "Brake permission"},
        {"DataID": "6A08", "DataName": "Reference to 5A08"},
        {"DataID": "-", "DataName": "Viewer metadata"},
    ]
    adu_fields = [{"DataID": "5A08", "DataName": "Different ADU field"}]
    (generated / "pcs_data_viewer_tss3_managed_semantics.json").write_text(json.dumps({
        "schema": "gtsplus-pcs-data-viewer-tss3-managed-semantics-v1",
        "sources": {}, "operation_ffd": {"detail_rows": tss3_fields},
    }))
    (generated / "pcs_data_viewer_adu_semantics.json").write_text(json.dumps({
        "schema": "gtsplus-pcs-data-viewer-adu-semantics-v1",
        "sources": {}, "adu": {"rows": adu_fields},
    }))
    with patch.object(query, "REPO_ROOT", fixture):
        prefixed = query.recorder_payload("tss3", "0x5a08")["fields"]
        bare = query.recorder_payload("tss3", "5A08")["fields"]
        check(
            [row["DataName"] for row in prefixed] == [row["DataName"] for row in bare] == ["Brake permission"],
            "recorder IDs match exactly, not names containing the same hex token",
        )
        check(
            [row["DataID"] for row in query.recorder_payload("tss3", "brAKE")["fields"]] == ["5A08"],
            "recorder field-name matching is case-insensitive",
        )
        check(
            [row["DataID"] for row in query.recorder_payload("tss3")["fields"]] == ["5A08", "6A08"],
            "recorder discovery excludes non-record viewer metadata",
        )
        check(
            query.recorder_payload("adu", "0x6A08")["fields"] == []
            and [row["DataName"] for row in query.recorder_payload("adu", "0x5A08")["fields"]] == ["Different ADU field"],
            "recorder schemas neither mix same-ID meanings nor fall back to another schema",
        )

with tempfile.TemporaryDirectory(prefix="gts-cache-prune-") as td:
    cache_root = Path(td)
    current_cache = cache_root / "M_English-current.bin"
    current_cache.write_bytes(b"current")
    for index in range(6):
        (cache_root / f"M_English-old{index}.bin").write_bytes(bytes([index]))
    ddb_strings._prune(current_cache)
    remaining = list(cache_root.glob("M_English-*.bin"))
    check(current_cache in remaining, "string-cache pruning always preserves the current decode")
    check(
        len(remaining) == ddb_strings.CACHE_GENERATIONS_TO_KEEP,
        "string-cache pruning keeps a bounded multi-release working set",
    )

with tempfile.TemporaryDirectory(prefix="gts-root-routing-") as td:
    fixture = Path(td)
    selected_gts = fixture / "release/unpacked/gtsplus/Toyota Diagnostics/GTSPlus"
    adjacent_cuwplus = fixture / "release/cuwplus/CUWPlus"
    explicit_cuwplus = fixture / "explicit/CUWPlus"
    selected_gts.mkdir(parents=True)
    adjacent_cuwplus.mkdir(parents=True)
    explicit_cuwplus.mkdir(parents=True)
    check(
        techstream_paths.resolve_cuwplus_root(selected_gts) == adjacent_cuwplus.resolve(),
        "selected GTS+ tree prefers its adjacent CUWPlus routes over repository defaults",
    )
    check(
        techstream_paths.resolve_cuwplus_root(selected_gts, explicit_cuwplus) == explicit_cuwplus.resolve(),
        "explicit CUWPlus root overrides adjacent/default route trees",
    )
    adjacent_cuwplus.rmdir()
    unresolved = techstream_paths.resolve_cuwplus_root(selected_gts)
    check(
        not unresolved.exists() and unresolved != cuwplus,
        "alternate GTS+ tree without CUWPlus never borrows repository-default writer routes",
    )

parser = DDBParser()
strings = ddb._english_strings(parser, db_root)
master = parser.parse_master_db(db_root / "Toyota.ddb")
camry_bus = gts_master._master_canbus_topology_rows(parser, master, strings, "12704")
check(len(camry_bus) == 1 and camry_bus[0]["vehicle_name"] == "Camry HV" and camry_bus[0]["can_bus_car_id"] == "0x00A7D910" and camry_bus[0]["option_count"] == 18 and camry_bus[0]["placement_variant_count"] == 1, "CAN Bus Check resolver joins current Camry-HV type 12704 to one 18-option topology")
camry_placements = {row["component_hex"]: row for row in camry_bus[0]["placement_variants"][0]["placements"]}
check(camry_placements["0x6D"]["ecu_domain"] == "Front Camera Module" and camry_placements["0x6D"]["bus_name"] == "Bus 1" and camry_placements["0x29"]["ecu_domain"] == "Skid Control (ABS/VSC/TRAC)" and camry_placements["0x29"]["bus_name"] == "Bus 4" and camry_placements["0x32"]["ecu_domain"] == "Power Steering (EPS)" and camry_placements["0x32"]["bus_name"] == "Bus 4", "CAN Bus Check resolver exposes camera Bus1 versus Brake/EPS Bus4 split")
hybrid = gts_master._resolve_master_category(parser, master, strings, "HV_P5")
check(hybrid["category_id"] == 397 and hybrid["name"] == "Hybrid Control", "master category resolver joins HV_P5 to category 397 Hybrid Control")
plugins = gts_master._master_plugins(parser, master, hybrid["category_id"])
check(any(row == {"role": 25, "role_hex": "0x19", "dll": "DelDiagCodeP4.dll"} for row in plugins), "current master plugin resolver decodes DelDiagCodeP4 role 0x19")
commsets = gts_master._master_comm_set_rows(parser, master)
commset1 = next(row for row in commsets if row["comm_set_id"] == 1)
check(len(commsets) == 13 and commset1["raw"] == "e8030000fc0300000000010000000100", "current master exposes 13 stable 16-byte CommSet rows")
check(commset1["receive_timeout"] == 1020 and commset1["retry_count"] == 1, "current CommSet 1 resolves receive timeout 1020 and one retry")
check(
    ECU_TABLE_CLASS_NAMES[33] == "CDbMultiDidIdTable"
    and ECU_TABLE_CLASS_NAMES[67] == "CDbDataIdForActTable"
    and ECU_TABLE_CLASS_NAMES[68] == "CDbActTestP5Table"
    and ECU_TABLE_CLASS_NAMES[71] == "CDbRoutineActTestP5Table",
    "current parser names the consumer-proven Active Test, DataIdForAct, and MultiDID tables",
)
timers = gts_master._master_timer_rows(parser, master, hybrid["category_id"])
check(
    timers == [{"category_id": 397, "timer_id": 1, "delay_ms": 0, "unknown_dword_08": 0, "raw": "000000008d01010000000000"}],
    "current Hybrid timer 1 resolves to zero-millisecond post-command delay",
)

role_catalog = gts_master._master_role_catalog(parser, master, gts / "bin")
role19 = next(row for row in role_catalog if row["role"] == 25)
check(len(role_catalog) == 191 and role19["binding_count"] == 536 and role19["category_count"] == 536 and role19["binding_surface_counts"] == {"direct_transport": 536} and role19["plugins"][0]["dll"] == "DelDiagCodeP4.dll" and role19["plugins"][0]["binding_count"] == 424, "current master role census resolves operation surfaces as well as 6194 -> 191 role compression")
role5 = next(row for row in role_catalog if row["role"] == 5)
check(role5["plugins"][0]["surface"] == "support_cache_v18_proven" and role5["plugins"][1]["surface"] == "delegated_transport_v18_proven", "role query distinguishes P4 cached support from P5 delegated support probing")
engine_category = gts_master._resolve_master_category(parser, master, strings, "Engine_P5")
emps_category = gts_master._resolve_master_category(parser, master, strings, "EMPS_P5")
hybrid_active_plan = commands._master_command_plan(parser, master, hybrid, 0x06, gts / "bin", db_root)
check(
    hybrid_active_plan["plugin"] == "GetActTstListP5_DT.dll"
    and hybrid_active_plan["semantic_status"] == "exact_plugin_identity_and_category_active_test_partition"
    and hybrid_active_plan["operation_surface"] == "delegated_transport_v18_proven"
    and hybrid_active_plan["active_test_model"]["category_plan"]["direct_candidate_count"] == 29
    and hybrid_active_plan["active_test_model"]["category_plan"]["routine_candidate_count"] == 10,
    "command plan partitions Hybrid role 0x06 into 29 DID-backed direct and 10 RID-backed routine candidates",
)
engine_multi_plan = commands._master_command_plan(
    parser, master, engine_category, 0x63, gts / "bin", db_root, 0x4C, strings
)
engine_multi = engine_multi_plan["multi_active_test_init_model"]
engine_group = engine_multi["selected_plan"]
check(
    engine_multi_plan["plugin"] == "GetMultiActInitP5_DT.dll"
    and engine_multi_plan["operation_surface"] == "direct_transport"
    and engine_multi_plan["semantic_status"] == "exact_plugin_identity_and_selected_multi_active_test_plan"
    and engine_multi["category_plan"]["group_count"] == 5
    and engine_multi["category_plan"]["membership_count"] == 10
    and engine_group["group"]["name"] == "Pilot Injection Volume"
    and engine_group["group"]["member_count"] == 2
    and [(m["sort_order"], m["input_slot"], m["selected_test"]["active_test_id"], m["selected_test"]["name"]) for m in engine_group["members"]] == [
        (1, 1, 0x4D, "Pilot Injection Volume Select Cylinder"),
        (2, 2, 0x4E, "Pilot Injection Volume Value"),
    ]
    and [(m["selected_test"]["initial_read_did"], m["selected_test"]["bit_start"], m["selected_test"]["bit_end"], m["initial_transaction"]["materialized_send"]) for m in engine_group["members"]] == [
        (0x284A, 0, 7, "22284a"),
        (0x284A, 8, 15, "22284a"),
    ],
    "command plan expands Engine role 0x63 group 0x4C into two ordered type-68 controls sharing DID 0x284A",
)
hybrid_multi_plan = commands._master_command_plan(parser, master, hybrid, 0x63, gts / "bin", db_root)
check(
    hybrid_multi_plan["multi_active_test_init_model"]["category_plan"]["group_count"] == 0
    and hybrid_multi_plan["multi_active_test_init_model"]["category_plan"]["membership_count"] == 0,
    "command plan keeps Hybrid role 0x63 binding but reports no static type-33 multi-control groups",
)

hybrid_init_plan = commands._master_command_plan(
    parser, master, hybrid, 0x08, gts / "bin", db_root, 0x01, strings
)
hybrid_init_selected = hybrid_init_plan["active_test_init_model"]["selected_plan"]
check(
    hybrid_init_plan["plugin"] == "GetActTstInitP5_DT.dll"
    and hybrid_init_plan["operation_surface"] == "direct_transport"
    and hybrid_init_plan["semantic_status"] == "exact_plugin_identity_and_selected_active_test_plan"
    and hybrid_init_selected["selected_test"]["name"] == "Activate the Inverter Water Pump"
    and hybrid_init_selected["selected_test"]["initial_read_did"] == 0x2801
    and hybrid_init_selected["selected_test"]["bit_start"] == 15
    and hybrid_init_selected["selected_test"]["bit_end"] == 15
    and hybrid_init_selected["initial_transaction"]["selector"] == "0xCA"
    and hybrid_init_selected["initial_transaction"]["base_frame"]["send"]["bytes"] == "22ffff"
    and hybrid_init_selected["initial_transaction"]["materialized_send"] == "222801"
    and hybrid_init_selected["initial_transaction"]["receive_check"] == "62"
    and hybrid_init_selected["linked_monitor"]["monitor_key"] == 30
    and hybrid_init_selected["linked_monitor"]["monitor"]["name"] == "Inverter Water Pump"
    and hybrid_init_selected["linked_monitor"]["monitor"]["signal_info"]["pattern_display"] == {0: "OFF", 1: "ON"}
    and hybrid_init_selected["executor"]["service"] == "0x2F"
    and hybrid_init_selected["executor"]["positive_response"] == "0x6F"
    and hybrid_init_selected["executor"]["data_id_for_act"]["table"] == 67
    and hybrid_init_selected["executor"]["data_id_for_act"]["table_class"] == "CDbDataIdForActTable"
    and hybrid_init_selected["executor"]["data_id_for_act"]["encoding_mode"] == 1
    and hybrid_init_selected["executor"]["start"]["materialized_prefix"] == "2f280103"
    and hybrid_init_selected["executor"]["stop"]["materialized_prefix"] == "2f280100"
    and hybrid_init_selected["executor"]["runtime_data_length"]["minimum_from_bit_geometry"] == 2
    and hybrid_init_selected["executor"]["runtime_data_length"]["probe"]["kind"] == "read_data_by_identifier_value_length"
    and hybrid_init_selected["executor"]["runtime_data_length"]["probe"]["selector"] == "0xCA"
    and hybrid_init_selected["executor"]["runtime_data_length"]["probe"]["materialized_request"] == "222801"
    and hybrid_init_selected["executor"]["runtime_data_length"]["probe"]["positive_check"] == "62"
    and hybrid_init_selected["executor"]["runtime_data_length"]["probe"]["response_prefix_length"] == 3
    and hybrid_init_selected["executor"]["minimum_length_examples"] == {
        "raw_0": "2f2801030000",
        "raw_1": "2f2801030001",
        "return_control": "2f2801000001",
        "qualification": "uses N=2, the static minimum required by bit 15; not proof that the runtime DataIdLengthList entry has that length",
    },
    "command plan materializes Hybrid role 0x08 Active Test 1 through init/read and bounded 0x2F runtime execution",
)
hybrid_active_monitor_plan = commands._master_command_plan(
    parser, master, hybrid, 0xAD, gts / "bin", db_root
)
hybrid_active_monitor = hybrid_active_monitor_plan["active_test_monitor_model"]["category_plan"]
check(
    hybrid_active_monitor_plan["plugin"] == "GetDatMonListP5ForActTest_DT.dll"
    and hybrid_active_monitor_plan["operation_surface"] == "delegated_transport_v18_proven"
    and hybrid_active_monitor_plan["semantic_status"] == "exact_plugin_identity_and_category_active_test_monitor_partition"
    and hybrid_active_monitor["candidate_table"] == 62
    and hybrid_active_monitor["candidate_count"] == 1464
    and hybrid_active_monitor["active_test_membership_bit"] == "0x40"
    and hybrid_active_monitor["active_test_candidate_count"] == 1411
    and hybrid_active_monitor["nonmember_count"] == 53
    and hybrid_active_monitor["candidate_partition"] == {
        "active_direct_include": 0,
        "active_runtime_check_support_pid": 1411,
        "nonmember_direct_exclude": 0,
        "nonmember_runtime_probe_then_filter": 53,
    }
    and hybrid_active_monitor["support_list_builder"] == "CreateEnableDataIdList",
    "command plan closes Hybrid role 0xAD as 1411 bit-0x40 Active-Test monitors plus 53 runtime-probed nonmembers",
)

hybrid_signal_plan = commands._master_command_plan(
    parser, master, hybrid, 0x70, gts / "bin", db_root, 0x01, strings
)
hybrid_signal_selected = hybrid_signal_plan["active_test_signal_info_model"]["selected_plan"]
check(
    hybrid_signal_plan["plugin"] == "GetATSignalInfoP5_DT.dll"
    and hybrid_signal_plan["operation_surface"] == "no_recovered_shared_transport_edge"
    and hybrid_signal_plan["semantic_status"] == "exact_plugin_identity_and_selected_active_test_signal_info"
    and hybrid_signal_selected["selected_test"]["name"] == "Activate the Inverter Water Pump"
    and hybrid_signal_selected["active_test_pattern"]["key"] == 10
    and hybrid_signal_selected["active_test_pattern"]["pattern_display_key"] == 102
    and hybrid_signal_selected["active_test_pattern"]["key_operation_pattern"] == 101
    and hybrid_signal_selected["physical"]["key"] == 6
    and hybrid_signal_selected["physical"]["mul"] == 1
    and hybrid_signal_selected["physical"]["div"] == 1
    and hybrid_signal_selected["physical"]["offset"] == 0
    and hybrid_signal_selected["physical"]["signed"] is False
    and hybrid_signal_selected["display_info"] == [{
        "record": 690,
        "value": 1,
        "text": "ON",
        "raw": "ae6300000100000000000000660001000000000000000100",
    }],
    "command plan joins Hybrid role 0x70 Active Test 1 to exact pattern/physical/display metadata without transport",
)

frc_category = gts_master._resolve_master_category(parser, master, strings, "FRC_P5")
_, _, routine_selected = active_tests._routine_active_test_selected_row(
    parser, frc_category, db_root, 0xA429, strings
)
routine_executor = active_tests._routine_active_test_executor_plan(
    parser, master, frc_category, routine_selected
)
check(
    routine_selected["name"] == "LTA Steering Vibration"
    and routine_selected["routine_id"] == 0x1588
    and routine_selected["routine_command_variable"] == 0
    and routine_selected["routine_stop_command_variable"] == 0
    and routine_selected["output_mask_value_variable"] == 0
    and routine_selected["output_mask_button_variable"] == 0
    and routine_selected["routine_status_key"] == 2
    and routine_selected["sort_key"] == 542
    and routine_executor["service"] == "0x31"
    and routine_executor["positive_response"] == "0x71"
    and routine_executor["fixed_request"] is True
    and routine_executor["start"]["materialized_static_request"] == "31011588"
    and routine_executor["stop"]["materialized_static_request"] == "31021588"
    and routine_executor["result"]["materialized_static_request"] == "31031588",
    "unified Active-Test planner resolves FRC A429 as fixed UDS RoutineControl RID 0x1588",
)

try:
    active_tests._routine_active_test_selected_row(parser, frc_category, db_root, 0xFFFF, strings)
except ValueError as exc:
    check("resolved 0 type-71 rows" in str(exc), "routine Active-Test planner fails closed for an unknown type-71 key")
else:
    raise AssertionError("routine Active-Test planner accepted an unknown type-71 key")

try:
    commands._master_command_plan(parser, master, hybrid, 0x08, gts / "bin", db_root, 0xFFFF, strings)
except ValueError as exc:
    check("resolved 0 type-68 rows" in str(exc), "role 0x08 selected-test planner fails closed for an unknown direct Active Test ID")
else:
    raise AssertionError("role 0x08 selected-test planner accepted an unknown Active Test ID")

emps_monitor_plan = commands._master_command_plan(parser, master, emps_category, 0x05, gts / "bin", db_root)
check(
    emps_monitor_plan["plugin"] == "GetDatMonListP5_DT.dll"
    and emps_monitor_plan["semantic_status"] == "exact_plugin_identity_and_category_candidate_partition"
    and emps_monitor_plan["operation_surface"] == "delegated_transport_v18_proven"
    and emps_monitor_plan["list_model"]["category_plan"]["candidate_partition"] == {
        "direct_include": 0,
        "direct_exclude": 0,
        "runtime_check_support_pid": 230,
    },
    "command plan partitions EMPS role 0x05 into 230 runtime support-probed Data Monitor candidates",
)
hybrid_plan = commands._master_command_plan(parser, master, hybrid, 0x19, gts / "bin")
check(
    hybrid_plan["plugin"] == "DelDiagCodeP4.dll"
    and hybrid_plan["semantic_status"] == "exact_plugin_identity_and_primary_frame"
    and hybrid_plan["frames"]["primary"]["send"]["bytes"] == "04"
    and hybrid_plan["frames"]["fallback"]["send"]["bytes"] == "14ffffff"
    and hybrid_plan["timers"] == [{"category_id": 397, "timer_id": 1, "delay_ms": 0, "unknown_dword_08": 0, "raw": "000000008d01010000000000"}]
    and len(hybrid_plan["control_flow"]["fallback_error_codes_when_function_gate_set"]) == 10,
    "command plan joins Hybrid role 0x19 plugin, category-local frames, timer, and exact state machine",
)
emps_cid_plan = commands._master_command_plan(parser, master, emps_category, 0x52, gts / "bin")
check(
    emps_cid_plan["plugin"] == "GetCID_SID22_DT.dll"
    and emps_cid_plan["semantic_status"] == "exact_plugin_identity_and_category_frame"
    and emps_cid_plan["frames"]["request"]["send"]["bytes"] == "22f181"
    and emps_cid_plan["response_model"]["payload_offset"] == 4
    and emps_cid_plan["response_model"]["record_size"] == 16,
    "command plan joins EMPS role 0x52 F181 wire contract to exact current response parser",
)
emps_signal_plan = commands._master_command_plan(parser, master, emps_category, 0x41, gts / "bin")
check(
    emps_signal_plan["semantic_status"] == "exact_plugin_identity_metadata_only"
    and emps_signal_plan["frames"] == {}
    and emps_signal_plan["metadata_model"]["physical_data_table"] == 13
    and emps_signal_plan["metadata_model"]["unit_table"] == 15
    and emps_signal_plan["metadata_model"]["pattern_display_table"] == 14,
    "command plan joins EMPS role 0x41 to exact current signal-info metadata semantics without inventing transport",
)
with tempfile.TemporaryDirectory(prefix="gts-command-hash-mismatch-") as td:
    fake_bin = Path(td)
    source = gts / "bin/GetCID_SID22_DT.dll"
    altered = fake_bin / source.name
    shutil.copyfile(source, altered)
    altered.write_bytes(altered.read_bytes() + b"\x00")
    mismatched = commands._master_command_plan(parser, master, emps_category, 0x52, fake_bin)
    check(
        mismatched["semantic_status"] == "plugin_semantics_unrecovered_for_identity"
        and mismatched["response_model"] is None
        and mismatched["frames"] == {},
        "command plan fails closed when a known plugin filename has a different SHA-256",
    )
primary = gts_master._master_frame_rows(parser, master, hybrid["category_id"], 0x01)
check(len(primary) == 1 and primary[0]["comm_set_metadata"]["receive_timeout"] == 1020 and primary[0]["comm_set_metadata"]["retry_count"] == 1 and primary[0]["send"] == {"id": "0x2743", "normalized_id": "0x33", "bytes": "04"} and primary[0]["receive_check"] == {"id": "0x28F7", "normalized_id": "0x1E7", "bytes": "44"}, "current master selector 1 resolves namespaced variables to 04 -> 44")
fallback = gts_master._master_frame_rows(parser, master, hybrid["category_id"], 0x102)
check(len(fallback) == 1 and fallback[0]["send"] == {"id": "0x2D28", "normalized_id": "0x618", "bytes": "14ffffff"} and fallback[0]["receive_check"] == {"id": "0x28E4", "normalized_id": "0x1D4", "bytes": "54"}, "current master selector 0x102 resolves namespaced variables to 14FFFFFF -> 54")
emps = parser.parse_ecu_db(db_root / "EMPS_P5.ddb")
rows = ddb._monitor_rows(emps, strings, "EMPS_P5.ddb")
rows_1cee = [row for row in rows if row["primary_did"] == 0x1CEE]
names_1cee = {row["name"] for row in rows_1cee}
check("Advanced Drive Target Steering Angle" in names_1cee, "DID 0x1CEE resolves Advanced Drive Target Steering Angle")
check("Target Steering Angle After Output Compensation" in names_1cee, "DID 0x1CEE retains the second Toyota interpretation")
ffd = ddb._generic_ffd_rows(
    emps,
    strings,
    "EMPS_P5.ddb",
    resolve_variable=lambda variable_id: bytes.fromhex(gts_master._master_variable(master, variable_id)["bytes"]),
)
ffd_steering = next(row for row in ffd["signals"] if row["name"] == "Steering Angle")
check(
    ffd_steering["snapshot_did"] == 0x3037
    and ffd_steering["primary_did"] == 0x1037
    and [ffd_steering["bit_start"], ffd_steering["bit_end"]] == [0, 15]
    and ffd_steering["local_support_mode"] == 0
    and ffd_steering["support_condition"] is None
    and ffd_steering["signal_info"]["mul"] == 15
    and ffd_steering["signal_info"]["signed"] is True
    and ffd_steering["signal_info"]["unit"] == "deg",
    "current EPS generic FFD maps SSR DID 0x3037 to the exact Steering Angle signal schema",
)
ffd_odo_km = next(row for row in ffd["signals"] if row["monitor_key"] == 9905)
check(
    ffd_odo_km["snapshot_did"] == 0x0403
    and ffd_odo_km["support_condition"] == {
        "key": 10001, "variable_id": 11290, "referenced_did": 0x0403,
        "bit_start": 7, "bit_end": 7, "condition_type": 7,
    }
    and ffd_odo_km["signal_info"]["unit"] == "km",
    "current EPS generic FFD resolves type-80 variable 0x2C1A to DID 0x0403 bit7 condition",
)
check(
    len(ffd["signals"]) == 163 and ffd["condition_count"] == 2
    and ffd["dynamic_lsb_table_present"] is False,
    "current EPS generic FFD aliases collapse to 163 unique signals with two exact support conditions",
)

rob = ddb._rob_rows(emps, strings, "EMPS_P5.ddb")
rob_steering = next(row for row in rob["signals"] if row["name"] == "Steering Angle")
check(
    rob_steering["did"] == 0x5037
    and [rob_steering["bit_start"], rob_steering["bit_end"]] == [0, 15]
    and rob_steering["local_support_mode"] == 0
    and rob_steering["support_condition_key"] == 0
    and rob_steering["dynamic_lsb_possible"] is False
    and rob_steering["signal_info"]["unit"] == "deg"
    and rob_steering["signal_info"]["mul"] == 15
    and rob_steering["signal_info"]["signed"] is True,
    "current EPS RoB signal grammar joins type-88 DID/bit geometry to physical/unit metadata",
)
rob_behavior = next(row for row in rob["behavior_codes"] if row["behavior_code"] == 0x0455)
check(
    rob_behavior["signature"] == "X0455"
    and rob_behavior["name"] == "Steering Angle Sensor Incorrect Installation",
    "current EPS RoB behavior-code grammar recovers OEM code/name identity",
)

steering = next(row for row in rows if row["monitor_key"] == 17)
check(
    steering["name"] == "Steering Angle"
    and steering["primary_did"] == 0x1037
    and steering["signal_info"] == {
        "physical_data_key": 3,
        "mul": 15,
        "div": 1,
        "offset": 0,
        "unit_key": 46,
        "unit": "deg",
        "signed": True,
        "decimal_point_count": 1,
        "bit_width": 16,
        "data_range": [-2048, 2047],
        "graph_range": [-30720, 30705],
        "pattern_display": {},
    },
    "current DID rows join role-0x41 physical/unit semantics for Steering Angle",
)
frc = parser.parse_ecu_db(db_root / "FRC_P5.ddb")
frc_rows = ddb._monitor_rows(frc, strings, "FRC_P5.ddb")
frc_1601 = {row["name"]: row for row in frc_rows if row["primary_did"] == 0x1601}
check(
    frc_1601["LTA Switch Condition Flag"]["signal_info"]["pattern_display"] == {0: "OFF", 1: "ON"}
    and frc_1601["LTA Control Condition"]["signal_info"]["pattern_display"] == {0: "LTA Enabled", 1: "LTA Disabled"}
    and frc_1601["Hands-Off Customize Condition Flag"]["signal_info"]["pattern_display"] == {0: "OFF", 1: "ON"}
    and frc_1601["Hands-Off Control Condition"]["signal_info"]["pattern_display"] == {0: "Hands-Off Enabled", 1: "Hands-off Disabled"},
    "current FRC DID 0x1601 exposes exact LTA/Hands-Off value dictionaries",
)
frc_1914 = next(row for row in frc_rows if row["primary_did"] == 0x1914 and row["name"] == "ACC Control in Operation Flag")
check(
    [frc_1914["bit_start"], frc_1914["bit_end"]] == [8, 8]
    and frc_1914["signal_info"]["pattern_display"] == {
        0: "Cruise Control Not in Operation",
        1: "Cruise Control in Operation",
    },
    "current FRC DID 0x1914 exposes exact ACC-in-operation dictionary",
)
cooperation = next(row for row in rows if row["monitor_key"] == 60)
check(
    cooperation["signal_info"]["pattern_display"] == {
        0: "Cooperation Control",
        1: "Other than Cooperation Control",
    }
    and cooperation["signal_info"]["bit_width"] == 8,
    "current DID rows join type-14 display dictionary for Cooperation Control State",
)
check(
    len({(row["name"], row["primary_did"], row["alternate_did"]) for row in rows}) == len(rows),
    "overlapping current Data List table aliases are deduplicated",
)

routes = query._route_rows(cuwplus)
route04 = [row for row in routes if row["contact_type"] == "P5-Unified04"]
check(len(route04) == 1, "P5-Unified04 resolves one current CUWPlus route")
check(route04[0]["cid_getter"] == "TCUWCanUnifiedCIDGetter.dll", "P5-Unified04 resolves Unified CID getter")
check(route04[0]["prepare_writer"] == "TCUWCanReproStdPrepareWriter.dll", "P5-Unified04 resolves ReproStd prepare writer")
check(route04[0]["flash_writer"] == "TCUWCanReproStdFlashWriter.dll", "P5-Unified04 resolves ReproStd flash writer")
check(query._route_match("P5-Unified04", route04[0]), "route matcher searches semantic route values")
check(
    not query._route_match("DLLFileNameForPrepareWrite", route04[0]),
    "route matcher does not leak raw CSV header names into search results",
)

fast_outer, fast_descriptor = cuw._cuw_descriptor_fast(corpus / "T-0051-26.cuw")
check(fast_outer["format_type"] == 0x67, "fast CUW header path resolves format 0x67 without reading flash members")
check(fast_outer["validation"] == "header-and-first-member-only", "fast CUW path labels its bounded validation level")
check(fast_descriptor["Vehicle"]["ContactType"] == "P5-Unified", "fast CUW descriptor path resolves contact type")

outer, descriptor = cuw._cuw_descriptor(corpus / "T-0051-26.cuw")
check(outer["format_type"] == 0x67, "fully validated Camry CUW outer format remains 0x67")
check(outer["validation"] == "full-container", "full CUW path labels full-container validation")
check(descriptor["Vehicle"]["VehicleName"] == "CAMRY", "Camry CUW OEM vehicle name resolves")
check(descriptor["Vehicle"]["ContactType"] == "P5-Unified", "Camry CUW contact type resolves")
check(descriptor["Node01"]["DiagID"] == "0724", "Camry CUW diagnostic ID resolves")
check(
    cuw._new_cids(descriptor) == ["8A2810602100", "8A2910601100", "8A2A10602100"],
    "Camry CUW logical-block NewCIDs resolve",
)
check(
    cuw._target_calibrations(descriptor) == ["8A2810602000", "8A2910601000", "8A2A10602000"],
    "Camry CUW target calibrations resolve",
)

p5_route = [row for row in routes if row["contact_type"] == "P5-Unified"]
check(len(p5_route) == 1, "Camry P5-Unified contact type resolves one current route")
check(p5_route[0]["prepare_writer"] == "TCUWCanUnifiedPrepareWriter.dll", "Camry CUW resolves current Unified prepare writer")
check(p5_route[0]["flash_writer"] == "TCUWCanUnifiedFlashWriter.dll", "Camry CUW resolves current Unified flash writer")

kgp = query._resolve_pe(gts, cuwplus, "KgpDataCtrl.dll")
check(kgp.is_file(), "PE resolver finds current KgpDataCtrl.dll")
strings_in_kgp = pe_utils.binary_strings(kgp.read_bytes())
check(any("CDbDatamonitorP5Table" in value for value in strings_in_kgp), "PE string surface exposes current Data Monitor implementation class")

print("verified unified GTS+ DDB/CUW/PE query surface")
