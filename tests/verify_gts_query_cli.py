#!/usr/bin/env python3
"""Verify the unified read-only GTS+ query surface against pinned external artifacts."""
from __future__ import annotations

import shutil
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools" / "techstream"))

import ddb_strings
import gts_cli
from parse_ddb import DDBParser


def check(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)
    print(f"[PASS] {message}")


gts = gts_cli._resolve_gts_root()
db_root = gts_cli._db_root(gts)
cuwplus = gts_cli._resolve_cuwplus_root(gts)
corpus = gts_cli._resolve_cuw_corpus()

check((db_root / "EMPS_P5.ddb").is_file(), "current GTS+ EMPS_P5 database is available")
check((db_root / "M_English.ddb").is_file(), "current GTS+ English OEM string database is available")
check((cuwplus / "Ini/P5-Unified04.ini").is_file(), "current CUWPlus P5-Unified04 route is available")
check((corpus / "T-0051-26.cuw").is_file(), "pinned Camry CUW is available")

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
        gts_cli._resolve_cuwplus_root(selected_gts) == adjacent_cuwplus.resolve(),
        "selected GTS+ tree prefers its adjacent CUWPlus routes over repository defaults",
    )
    check(
        gts_cli._resolve_cuwplus_root(selected_gts, explicit_cuwplus) == explicit_cuwplus.resolve(),
        "explicit CUWPlus root overrides adjacent/default route trees",
    )
    adjacent_cuwplus.rmdir()
    unresolved = gts_cli._resolve_cuwplus_root(selected_gts)
    check(
        not unresolved.exists() and unresolved != cuwplus,
        "alternate GTS+ tree without CUWPlus never borrows repository-default writer routes",
    )

parser = DDBParser()
strings = gts_cli._english_strings(parser, db_root)
master = parser.parse_master_db(db_root / "Toyota.ddb")
camry_bus = gts_cli._master_canbus_topology_rows(parser, master, strings, "12704")
check(len(camry_bus) == 1 and camry_bus[0]["vehicle_name"] == "Camry HV" and camry_bus[0]["can_bus_car_id"] == "0x00A7D910" and camry_bus[0]["option_count"] == 18 and camry_bus[0]["placement_variant_count"] == 1, "CAN Bus Check resolver joins current Camry-HV type 12704 to one 18-option topology")
camry_placements = {row["component_hex"]: row for row in camry_bus[0]["placement_variants"][0]["placements"]}
check(camry_placements["0x6D"]["ecu_domain"] == "Front Camera Module" and camry_placements["0x6D"]["bus_name"] == "Bus 1" and camry_placements["0x29"]["ecu_domain"] == "Skid Control (ABS/VSC/TRAC)" and camry_placements["0x29"]["bus_name"] == "Bus 4" and camry_placements["0x32"]["ecu_domain"] == "Power Steering (EPS)" and camry_placements["0x32"]["bus_name"] == "Bus 4", "CAN Bus Check resolver exposes camera Bus1 versus Brake/EPS Bus4 split")
check(gts_cli.build_parser().parse_args(["canbus", "12704"]).func is gts_cli.cmd_canbus, "gts canbus command is registered in the unified CLI")
hybrid = gts_cli._resolve_master_category(parser, master, strings, "HV_P5")
check(hybrid["category_id"] == 397 and hybrid["name"] == "Hybrid Control", "master category resolver joins HV_P5 to category 397 Hybrid Control")
plugins = gts_cli._master_plugins(parser, master, hybrid["category_id"])
check(any(row == {"role": 25, "role_hex": "0x19", "dll": "DelDiagCodeP4.dll"} for row in plugins), "current master plugin resolver decodes DelDiagCodeP4 role 0x19")
commsets = gts_cli._master_comm_set_rows(parser, master)
commset1 = next(row for row in commsets if row["comm_set_id"] == 1)
check(len(commsets) == 13 and commset1["raw"] == "e8030000fc0300000000010000000100", "current master exposes 13 stable 16-byte CommSet rows")
check(commset1["receive_timeout"] == 1020 and commset1["retry_count"] == 1, "current CommSet 1 resolves receive timeout 1020 and one retry")
timers = gts_cli._master_timer_rows(parser, master, hybrid["category_id"])
check(
    timers == [{"category_id": 397, "timer_id": 1, "delay_ms": 0, "unknown_dword_08": 0, "raw": "000000008d01010000000000"}],
    "current Hybrid timer 1 resolves to zero-millisecond post-command delay",
)

role_catalog = gts_cli._master_role_catalog(parser, master, gts / "bin")
role19 = next(row for row in role_catalog if row["role"] == 25)
check(len(role_catalog) == 191 and role19["binding_count"] == 536 and role19["category_count"] == 536 and role19["binding_surface_counts"] == {"direct_transport": 536} and role19["plugins"][0]["dll"] == "DelDiagCodeP4.dll" and role19["plugins"][0]["binding_count"] == 424, "current master role census resolves operation surfaces as well as 6194 -> 191 role compression")
role5 = next(row for row in role_catalog if row["role"] == 5)
check(role5["plugins"][0]["surface"] == "support_cache_v18_proven" and role5["plugins"][1]["surface"] == "delegated_transport_v18_proven", "role query distinguishes P4 cached support from P5 delegated support probing")
emps_category = gts_cli._resolve_master_category(parser, master, strings, "EMPS_P5")
emps_monitor_plan = gts_cli._master_command_plan(parser, master, emps_category, 0x05, gts / "bin", db_root)
check(
    emps_monitor_plan["plugin"] == "GetDatMonListP5_DT.dll"
    and emps_monitor_plan["semantic_status"] == "exact_plugin_identity_and_category_candidate_partition"
    and emps_monitor_plan["operation_surface"] == "delegated_transport_v18_proven"
    and emps_monitor_plan["list_model"]["category_plan"] == {
        "generation": 20,
        "generation_mode": "0x0",
        "candidate_table": 62,
        "candidate_table_class": "CDbDatamonitorP5Table",
        "candidate_count": 230,
        "record_size": 80,
        "support_list_builder": "CreateEnableDataIdList",
        "candidate_partition": {
            "direct_include": 0,
            "direct_exclude": 0,
            "runtime_check_support_pid": 230,
        },
        "runtime_support_required": True,
        "runtime_boundary": (
            "candidate partition is static; records in runtime_check_support_pid require support-cache/live ECU "
            "CheckSupportPid results before Techstream's final presented list is known"
        ),
    },
    "command plan partitions EMPS role 0x05 into 230 runtime support-probed Data Monitor candidates",
)
hybrid_plan = gts_cli._master_command_plan(parser, master, hybrid, 0x19, gts / "bin")
check(
    hybrid_plan["plugin"] == "DelDiagCodeP4.dll"
    and hybrid_plan["semantic_status"] == "exact_plugin_identity_and_primary_frame"
    and hybrid_plan["frames"]["primary"]["send"]["bytes"] == "04"
    and hybrid_plan["frames"]["fallback"]["send"]["bytes"] == "14ffffff"
    and hybrid_plan["timers"] == [{"category_id": 397, "timer_id": 1, "delay_ms": 0, "unknown_dword_08": 0, "raw": "000000008d01010000000000"}]
    and len(hybrid_plan["control_flow"]["fallback_error_codes_when_function_gate_set"]) == 10,
    "command plan joins Hybrid role 0x19 plugin, category-local frames, timer, and exact state machine",
)
emps_cid_plan = gts_cli._master_command_plan(parser, master, emps_category, 0x52, gts / "bin")
check(
    emps_cid_plan["plugin"] == "GetCID_SID22_DT.dll"
    and emps_cid_plan["semantic_status"] == "exact_plugin_identity_and_category_frame"
    and emps_cid_plan["frames"]["request"]["send"]["bytes"] == "22f181"
    and emps_cid_plan["response_model"]["payload_offset"] == 4
    and emps_cid_plan["response_model"]["record_size"] == 16,
    "command plan joins EMPS role 0x52 F181 wire contract to exact current response parser",
)
emps_signal_plan = gts_cli._master_command_plan(parser, master, emps_category, 0x41, gts / "bin")
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
    mismatched = gts_cli._master_command_plan(parser, master, emps_category, 0x52, fake_bin)
    check(
        mismatched["semantic_status"] == "plugin_semantics_unrecovered_for_identity"
        and mismatched["response_model"] is None
        and mismatched["frames"] == {},
        "command plan fails closed when a known plugin filename has a different SHA-256",
    )
primary = gts_cli._master_frame_rows(parser, master, hybrid["category_id"], 0x01)
check(len(primary) == 1 and primary[0]["comm_set_metadata"]["receive_timeout"] == 1020 and primary[0]["comm_set_metadata"]["retry_count"] == 1 and primary[0]["send"] == {"id": "0x2743", "normalized_id": "0x33", "bytes": "04"} and primary[0]["receive_check"] == {"id": "0x28F7", "normalized_id": "0x1E7", "bytes": "44"}, "current master selector 1 resolves namespaced variables to 04 -> 44")
fallback = gts_cli._master_frame_rows(parser, master, hybrid["category_id"], 0x102)
check(len(fallback) == 1 and fallback[0]["send"] == {"id": "0x2D28", "normalized_id": "0x618", "bytes": "14ffffff"} and fallback[0]["receive_check"] == {"id": "0x28E4", "normalized_id": "0x1D4", "bytes": "54"}, "current master selector 0x102 resolves namespaced variables to 14FFFFFF -> 54")
emps = parser.parse_ecu_db(db_root / "EMPS_P5.ddb")
rows = gts_cli._monitor_rows(emps, strings, "EMPS_P5.ddb")
rows_1cee = [row for row in rows if row["primary_did"] == 0x1CEE]
names_1cee = {row["name"] for row in rows_1cee}
check("Advanced Drive Target Steering Angle" in names_1cee, "DID 0x1CEE resolves Advanced Drive Target Steering Angle")
check("Target Steering Angle After Output Compensation" in names_1cee, "DID 0x1CEE retains the second Toyota interpretation")
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
frc_rows = gts_cli._monitor_rows(frc, strings, "FRC_P5.ddb")
frc_1601 = {row["name"]: row for row in frc_rows if row["primary_did"] == 0x1601}
check(
    frc_1601["LTA Switch Condition Flag"]["signal_info"]["pattern_display"] == {0: "OFF", 1: "ON"}
    and frc_1601["LTA Control Condition"]["signal_info"]["pattern_display"] == {0: "LTA Enabled", 1: "LTA Disabled"}
    and frc_1601["Hands-Off Customize Condition Flag"]["signal_info"]["pattern_display"] == {0: "OFF", 1: "ON"}
    and frc_1601["Hands-Off Control Condition"]["signal_info"]["pattern_display"] == {0: "Hands-Off Enabled", 1: "Hands-off Disabled"},
    "current FRC DID 0x1601 exposes exact LTA/Hands-Off value dictionaries",
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

routes = gts_cli._route_rows(cuwplus)
route04 = [row for row in routes if row["contact_type"] == "P5-Unified04"]
check(len(route04) == 1, "P5-Unified04 resolves one current CUWPlus route")
check(route04[0]["cid_getter"] == "TCUWCanUnifiedCIDGetter.dll", "P5-Unified04 resolves Unified CID getter")
check(route04[0]["prepare_writer"] == "TCUWCanReproStdPrepareWriter.dll", "P5-Unified04 resolves ReproStd prepare writer")
check(route04[0]["flash_writer"] == "TCUWCanReproStdFlashWriter.dll", "P5-Unified04 resolves ReproStd flash writer")
check(gts_cli._route_match("P5-Unified04", route04[0]), "route matcher searches semantic route values")
check(
    not gts_cli._route_match("DLLFileNameForPrepareWrite", route04[0]),
    "route matcher does not leak raw CSV header names into search results",
)

fast_outer, fast_descriptor = gts_cli._cuw_descriptor_fast(corpus / "T-0051-26.cuw")
check(fast_outer["format_type"] == 0x67, "fast CUW header path resolves format 0x67 without reading flash members")
check(fast_outer["validation"] == "header-and-first-member-only", "fast CUW path labels its bounded validation level")
check(fast_descriptor["Vehicle"]["ContactType"] == "P5-Unified", "fast CUW descriptor path resolves contact type")

outer, descriptor = gts_cli._cuw_descriptor(corpus / "T-0051-26.cuw")
check(outer["format_type"] == 0x67, "fully validated Camry CUW outer format remains 0x67")
check(outer["validation"] == "full-container", "full CUW path labels full-container validation")
check(descriptor["Vehicle"]["VehicleName"] == "CAMRY", "Camry CUW OEM vehicle name resolves")
check(descriptor["Vehicle"]["ContactType"] == "P5-Unified", "Camry CUW contact type resolves")
check(descriptor["Node01"]["DiagID"] == "0724", "Camry CUW diagnostic ID resolves")
check(
    gts_cli._new_cids(descriptor) == ["8A2810602100", "8A2910601100", "8A2A10602100"],
    "Camry CUW logical-block NewCIDs resolve",
)
check(
    gts_cli._target_calibrations(descriptor) == ["8A2810602000", "8A2910601000", "8A2A10602000"],
    "Camry CUW target calibrations resolve",
)

p5_route = [row for row in routes if row["contact_type"] == "P5-Unified"]
check(len(p5_route) == 1, "Camry P5-Unified contact type resolves one current route")
check(p5_route[0]["prepare_writer"] == "TCUWCanUnifiedPrepareWriter.dll", "Camry CUW resolves current Unified prepare writer")
check(p5_route[0]["flash_writer"] == "TCUWCanUnifiedFlashWriter.dll", "Camry CUW resolves current Unified flash writer")

kgp = gts_cli._resolve_pe(gts, cuwplus, "KgpDataCtrl.dll")
check(kgp.is_file(), "PE resolver finds current KgpDataCtrl.dll")
strings_in_kgp = gts_cli._binary_strings(kgp.read_bytes())
check(any("CDbDatamonitorP5Table" in value for value in strings_in_kgp), "PE string surface exposes current Data Monitor implementation class")

print("verified unified GTS+ DDB/CUW/PE query surface")
