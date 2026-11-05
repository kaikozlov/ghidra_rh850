#!/usr/bin/env python3
"""Verify the unified GTS+ query/recovery CLI against pinned external artifacts."""
from __future__ import annotations

import hashlib
import csv
import io
import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path
from unittest.mock import patch

from tools import REPO_ROOT

import tools.techstream.ddb_strings as ddb_strings
import tools.techstream.pe_utils as pe_utils
from tools.techstream import techstream_paths
from tools.techstream.cuw_attach import parse_attach_bytes, current_profile_int
from tools.techstream.cuw_parameter import decode_parameter_ini, factory_routes_from_ini_root, select_factory_routes_for_descriptor
from tools.techstream.gts import active_tests, commands, cuw, ddb, query
from tools.techstream.gts import master as gts_master
from tools.techstream.gts import execution_model, registry
from tools.techstream.parse_ddb import DDBParser, ECU_TABLE_CLASS_NAMES
from tools.techstream.ddb_semantics import UnresolvedNativeContext

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

with patch.dict(os.environ, {"GTSPLUS_CUW_ROOT": ""}):
    installed_cuwplus = techstream_paths.resolve_cuwplus_root(gts)
check(
    installed_cuwplus == (gts.parent / "CUWPlus").resolve()
    and (installed_cuwplus / "Ini/P5-Unified04.ini").is_file()
    and (installed_cuwplus / "CUW.dll").is_file(),
    "default CUWPlus selection returns the installed product root, retaining INIs and DLLs",
)
check(
    query.status_payload(gts, installed_cuwplus, corpus, db_root)["route_ini_files"] == 505,
    "default current status counts the complete 505-file installed INI corpus",
)
check(
    (installed_cuwplus / "TCUWEthernetCIDGetter.dll").resolve()
    in set(query._iter_pe_candidates(gts, installed_cuwplus)),
    "default native discovery retains installed CUWPlus modules outside the partial oracle corpus",
)

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
    current_env = {**os.environ, "GTSPLUS_CUW_ROOT": ""}
    status_result = subprocess.run(
        [str(ROOT / "tools/gts"), "status", "--gtsplus-root", str(gts), "--json"],
        cwd=td, env=current_env, capture_output=True, text=True, check=True,
    )
    status_response = json.loads(status_result.stdout)
    check(
        status_response["cuwplus_root"] == str(installed_cuwplus)
        and status_response["route_ini_files"] == 505,
        "public status returns the complete installed CUWPlus product from an unrelated working directory",
    )
    pe_result = subprocess.run(
        [str(ROOT / "tools/gts"), "pe", "TCUWEthernetCIDGetter.dll",
         "--gtsplus-root", str(gts), "--json", "--limit", "1"],
        cwd=td, env=current_env, capture_output=True, text=True, check=True,
    )
    check(
        json.loads(pe_result.stdout)["path"] == str(installed_cuwplus / "TCUWEthernetCIDGetter.dll"),
        "public native discovery reports installed protected source rather than a recovered-body fallback",
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
            "recorder IDs match exactly",
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

with tempfile.TemporaryDirectory(prefix="gts-root-routing-") as td, patch.dict(
    os.environ, {"GTSPLUS_CUW_ROOT": ""}
):
    fixture = Path(td)
    release = fixture / "release"
    selected_gts = release / "unpacked/gtsplus/Toyota Diagnostics/GTSPlus"
    installed = selected_gts.parent / "CUWPlus"
    partial = release / "cuwplus/CUWPlus"
    explicit = fixture / "explicit/CUWPlus"
    flat = fixture / "explicit-flat"
    (selected_gts / "NA/DB/Gen").mkdir(parents=True)
    (installed / "Ini").mkdir(parents=True)
    (partial / "Ini").mkdir(parents=True)
    explicit.mkdir(parents=True)
    flat.mkdir()
    source_ini = installed_cuwplus / "Ini/P5-Unified04.ini"
    shutil.copyfile(source_ini, installed / "Ini/P5-Unified04.ini")
    shutil.copyfile(source_ini, flat / "P5-Unified04.ini")
    (installed / "FixtureWriter.dll").write_bytes(b"installed source")
    (flat / "FixtureWriter.dll").write_bytes(b"explicit source")
    check(
        techstream_paths.resolve_gts_root(release) == selected_gts.resolve()
        and techstream_paths.resolve_gts_root(release / "unpacked/gtsplus") == selected_gts.resolve()
        and techstream_paths.resolve_gts_root(selected_gts) == selected_gts.resolve(),
        "external, unpacked, and direct GTS root layouts normalize to one selected release",
    )
    check(
        techstream_paths.resolve_cuwplus_root(selected_gts) == installed.resolve(),
        "selected GTS+ release uses its installed product sibling rather than an ancestor sample",
    )
    selected_alias = fixture / "selected-gts-alias"
    selected_alias.symlink_to(selected_gts, target_is_directory=True)
    check(
        techstream_paths.resolve_cuwplus_root(selected_alias) == installed.resolve(),
        "GTS symlink selection follows the canonical installed source rather than its alias parent",
    )
    with patch.dict(os.environ, {"GTSPLUS_ROOT": str(release)}):
        check(
            techstream_paths.resolve_cuwplus_root(techstream_paths.resolve_gts_root()) == installed.resolve(),
            "GTSPLUS_ROOT selects that release's installed CUWPlus sibling",
        )
    with patch.dict(os.environ, {"GTSPLUS_CUW_ROOT": str(flat)}):
        check(
            techstream_paths.resolve_cuwplus_root(selected_gts) == flat.resolve()
            and techstream_paths.resolve_cuwplus_root(selected_gts, explicit) == explicit.resolve(),
            "explicit argument wins over environment, and environment wins over installed source",
        )
    check(
        techstream_paths.resolve_cuwplus_root(selected_gts, partial) == partial.resolve()
        and techstream_paths.resolve_cuwplus_root(selected_gts, fixture / "absent") == (fixture / "absent").resolve(),
        "explicit partial and nonexistent source paths are never silently replaced",
    )
    check(
        techstream_paths.resolve_cuwplus_root(selected_gts, Path(os.path.relpath(explicit)))
        == explicit.resolve(),
        "explicit relative CUWPlus roots retain canonical resolution",
    )
    with patch.dict(os.environ, {"HOME": str(fixture)}):
        check(
            techstream_paths.resolve_cuwplus_root(selected_gts, "~/explicit/CUWPlus") == explicit.resolve(),
            "explicit home-relative CUWPlus roots retain expansion",
        )
    normalized = fixture / "recovered"
    normalized.mkdir()
    (normalized / "FixtureWriter.dll").write_bytes(b"normalized analysis body")
    check(
        techstream_paths.resolve_cuwplus_root(selected_gts, normalized) == normalized.resolve()
        and query._resolve_pe(selected_gts, normalized, "FixtureWriter.dll")
        == (normalized / "FixtureWriter.dll").resolve(),
        "explicit normalized-body selection is independent of installed-source discovery",
    )
    selected_routes = query._route_rows(installed)
    flat_routes = query._route_rows(flat)
    check(
        selected_routes == flat_routes and len(selected_routes) == 1
        and selected_routes[0]["selector"] == "P5-Unified04"
        and selected_routes[0]["encoded_sha256"] == hashlib.sha256(source_ini.read_bytes()).hexdigest(),
        "installed and explicit flat INI layouts preserve the same complete route identity",
    )
    check(
        query.status_payload(selected_gts, installed, corpus, selected_gts / "NA/DB/Gen")["route_ini_files"] == 1
        and query.status_payload(selected_gts, flat, corpus, selected_gts / "NA/DB/Gen")["route_ini_files"] == 1
        and query._resolve_pe(selected_gts, installed, "FixtureWriter.dll") == (installed / "FixtureWriter.dll").resolve()
        and query._resolve_pe(selected_gts, flat, "FixtureWriter.dll") == (flat / "FixtureWriter.dll").resolve(),
        "status and native discovery consume the selected product or flat corpus without changing roots",
    )
    for layout in (installed, flat):
        route_result = subprocess.run(
            [str(ROOT / "tools/gts"), "route", "--gtsplus-root", str(selected_gts),
             "--cuwplus-root", str(layout), "--json", "--limit", "1000"],
            capture_output=True, text=True, check=True,
        )
        status_result = subprocess.run(
            [str(ROOT / "tools/gts"), "status", "--gtsplus-root", str(selected_gts),
             "--cuwplus-root", str(layout), "--json"],
            capture_output=True, text=True, check=True,
        )
        selected_status = json.loads(status_result.stdout)
        check(
            json.loads(route_result.stdout) == selected_routes
            and selected_status["cuwplus_root"] == str(layout.resolve())
            and selected_status["route_ini_files"] == 1,
            "public route/status consumers preserve explicit installed and flat root selection",
        )
    matching_ini = installed_cuwplus / "Ini/P5-Unified.ini"
    shutil.copyfile(matching_ini, flat / "selected-route.ini")
    shutil.copyfile(matching_ini, flat / "P5-Unified.ini")
    cuw_result = subprocess.run(
        [str(ROOT / "tools/gts"), "cuw", "T-0058-23.cuw", "--cuw-root", str(corpus),
         "--gtsplus-root", str(selected_gts), "--cuwplus-root", str(flat), "--json"],
        capture_output=True, text=True, check=True,
    )
    descriptor_payload = json.loads(cuw_result.stdout)
    descriptor_routes = descriptor_payload["gtsplus_routes"]
    cid_binding = next(binding for binding in descriptor_payload["gtsplus_selection"]["roles"] if binding["role"] == "cid")
    check(
        descriptor_payload["gtsplus_selection"]["engine"]["name"] == "phase"
        and cid_binding["dll"] == "TCUWCanUnifiedCIDGetter.dll"
        and descriptor_routes
        and all(row["parameter_file"] == row["selector"] + ".ini" for row in descriptor_routes)
        and all(row["parameter_file"] != "selected-route.ini" for row in descriptor_routes),
        "public CUW join derives exact native selector filenames rather than treating ContactType or an alias file as a route",
    )
    # Product-level Ini wins; do not merge stray product-level CSVs into it.
    shutil.copyfile(source_ini, installed / "stray.ini")
    check(
        query._route_rows(installed) == selected_routes,
        "installed route discovery reads only Ini rather than merging another layout",
    )
    unresolved_gts = selected_gts.parent / "Unrelated"
    unresolved_gts.mkdir()
    for missing_or_unrelated in (selected_gts.parent / "Absent", unresolved_gts):
        check(
            techstream_paths.resolve_cuwplus_root(missing_or_unrelated)
            == missing_or_unrelated.resolve() / "__missing_cuwplus__",
            "missing or unrelated GTS roots do not borrow a present CUWPlus sibling",
        )
    shutil.rmtree(installed / "Ini")
    check(
        techstream_paths.resolve_cuwplus_root(selected_gts)
        == selected_gts.resolve() / "__missing_cuwplus__",
        "missing installed INIs never fall back to a partial ancestor or repository release",
    )
    shutil.rmtree(installed)
    check(
        techstream_paths.resolve_cuwplus_root(selected_gts)
        == selected_gts.resolve() / "__missing_cuwplus__",
        "missing installed CUWPlus never falls back to an ancestor sample or repository release",
    )
    check(
        query._route_rows(techstream_paths.resolve_cuwplus_root(selected_gts)) == [],
        "missing-release sentinel contributes no routes",
    )
    with patch.dict(os.environ, {"GTSPLUS_CUW_ROOT": str(flat)}):
        check(
            techstream_paths.resolve_cuwplus_root(selected_gts.parent / "Absent") == flat.resolve(),
            "explicit environment remains authoritative even when GTS source is missing",
        )
check(
    techstream_paths.v18_diagnostics_root() == techstream_paths.V18_DIAGNOSTICS_ROOT
    and techstream_paths.v18_techstream_root() == techstream_paths.V18_TECHSTREAM_ROOT
    and techstream_paths.v18_db_root() == techstream_paths.V18_DB_ROOT
    and techstream_paths.v18_cuw_root() == techstream_paths.V18_CUW_ROOT,
    "current root cutover preserves every historical V18 source-root API",
)

parser = DDBParser()
strings = ddb._english_strings(parser, db_root)
master = query.native_selection_context(gts, "NA")
raw_category_catalog = gts_master._master_category_rows(parser, master, strings)
spe_category_catalog = [row for row in raw_category_catalog if row["source"]["family"] == "Spe"]
check(
    len(spe_category_catalog) == 2004
    and all(row["name"] is None and row["string_resolution"]["status"] == "unresolved-source" for row in spe_category_catalog),
    "Spe raw category occurrences retain unresolved string provenance rather than borrowing Gen names",
)
main_default_count = 0
for region in ("NA", "EU", "JP"):
    regional_db = techstream_paths.gts_db_root(gts, region)
    regional_master = query.native_selection_context(gts, region)
    raw_categories = regional_master.raw_records(16, family="Gen")
    check(
        len(raw_categories) == {"NA": 2171, "EU": 2180, "JP": 2165}[region]
        and len({row.identity for row in raw_categories}) == len(raw_categories),
        f"{region} native context retains every source-qualified physical Gen category occurrence",
    )
    role_heads = {}
    for occurrence in regional_master.active_records(19, family="Gen"):
        role_heads.setdefault(occurrence.dll_role_id, occurrence)
    for role, expected in role_heads.items():
        selected = regional_master.query(19, role, 0x10000).require_success()
        check(
            selected.records[0].identity == expected.identity,
            f"{region} role {role:#x} native default preserves its actual active role head",
        )
    main_default_count += len(role_heads)
    generic = {"category_id": 0}
    generic_bindings = registry._registry_role_bindings(parser, regional_master, generic, gts / "bin")
    for role, requested, actual, expected_sha in (
        (0xDA, "GetCurAbsTimeInfo_DT.Dll", "GetCurAbsTimeInfo_DT.dll",
         "f31e0aafe7a61a9295bcc2b966d5b528483e4c25e9777fc848433726d6cdf20f"),
        (0xCB, "GetOpeFrzFrmDatP4_ICS02_DT.Dll", "GetOpeFrzFrmDatP4_ICS02_DT.dll",
         "fc9668bc2ed1d3a7bdb044a0f93b7ceaa7838fe30cf863fa39fe62e9a82cf13d"),
    ):
        path = execution_model._resolve_plugin_path(gts / "bin", requested)
        identity = execution_model._plugin_identity(path)
        command = commands._master_command_plan(parser, regional_master, generic, role, gts / "bin")
        binding = next(row for row in generic_bindings if row["role"] == role)
        check(
            path == gts / "bin" / actual and identity["path"] == actual
            and identity["source_path"] == str(path)
            and identity["size"] == path.stat().st_size
            and identity["sha256"] == expected_sha
            and command["plugin_identity"] == binding["plugin_identity"] == identity,
            f"{region} Gen role {role:#x} command and registry resolve the selected-folder case alias",
        )
    for role, name in ((0x72, "GetCurTimeInfo_DT.dll"), (0xAB, "SelectCarId_DT.dll")):
        command = commands._master_command_plan(parser, regional_master, generic, role, gts / "bin")
        binding = next(row for row in generic_bindings if row["role"] == role)
        check(
            command["semantic_status"] == binding["semantic_status"] == "plugin_file_missing"
            and command["plugin_identity"] == binding["plugin_identity"]
            and command["plugin_identity"]["source_path"] == str(gts / "bin" / name)
            and command["plugin_identity"]["sha256"] is None,
            f"{region} Gen role {role:#x} stays missing in GTSPlus/bin despite other supplied folders",
        )
check(main_default_count == 575, "all575 supplied main Gen first-role defaults are exercised")
ds4_default_count = 0
for domain in ("DM", "OS"):
    ds4_context = query.native_selection_context(gts.parent / "DS-4", domain)
    role_heads = {}
    for occurrence in ds4_context.active_records(19, family="Gen"):
        role_heads.setdefault(occurrence.dll_role_id, occurrence)
    for role, expected in role_heads.items():
        selected = ds4_context.query(19, role, 0x10000).require_success()
        check(
            selected.records[0].identity == expected.identity,
            f"DS4 {domain} role {role:#x} native default preserves its source-qualified role head",
        )
    ds4_default_count += len(role_heads)
check(ds4_default_count == 359, "all359 supplied DS4 Gen first-role defaults are exercised")


with tempfile.TemporaryDirectory(prefix="gts-plugin-path-") as td:
    fixture = Path(td)
    selected_bin = fixture / "selected/bin"
    selected_bin.mkdir(parents=True)
    for outside in (fixture / "selected/DS-4/bin", fixture / "older/bin", selected_bin / "nested"):
        outside.mkdir(parents=True)
        (outside / "Missing.DLL").write_bytes(b"outside selected folder")
    missing = execution_model._resolve_plugin_path(selected_bin, "Missing.dll")
    check(
        missing == selected_bin / "Missing.dll"
        and execution_model._plugin_identity(missing) == {
            "path": "Missing.dll", "source_path": str(missing), "size": None, "sha256": None,
        },
        "plugin lookup never searches sibling, old-release, or nested folders",
    )
    collision = selected_bin / "Collision.dll"
    collision_alias = selected_bin / "collision.DLL"
    collision.write_bytes(b"first source")
    collision_alias.write_bytes(b"second source")
    # Model both directory entries on case-insensitive development filesystems too.
    with patch.object(Path, "iterdir", return_value=[collision, collision_alias]):
        for requested in (collision.name, collision_alias.name, "COLLISION.DLL"):
            try:
                execution_model._resolve_plugin_path(selected_bin, requested)
            except ValueError as exc:
                check(
                    "ambiguous plugin filename" in str(exc),
                    "case-equivalent plugin entries fail closed even for an exact spelling",
                )
            else:
                raise AssertionError("plugin resolver accepted case-equivalent source entries")

camry_bus = gts_master._master_canbus_topology_rows(parser, master, strings, "12704")
check(len(camry_bus) == 1 and camry_bus[0]["vehicle_name"] == "Camry HV" and camry_bus[0]["can_bus_car_id"] == "0x00A7D910" and camry_bus[0]["option_count"] == 18 and camry_bus[0]["placement_variant_count"] == 1, "CAN Bus Check resolver joins current Camry-HV type 12704 to one 18-option topology")
camry_placements = {row["component_hex"]: row for row in camry_bus[0]["placement_variants"][0]["placements"]}
check(camry_placements["0x6D"]["ecu_domain"] == "Front Camera Module" and camry_placements["0x6D"]["bus_name"] == "Bus 1" and camry_placements["0x29"]["ecu_domain"] == "Skid Control (ABS/VSC/TRAC)" and camry_placements["0x29"]["bus_name"] == "Bus 4" and camry_placements["0x32"]["ecu_domain"] == "Power Steering (EPS)" and camry_placements["0x32"]["bus_name"] == "Bus 4", "CAN Bus Check resolver exposes camera Bus1 versus Brake/EPS Bus4 split")
hybrid = gts_master._resolve_master_category(parser, master, strings, "HV_P5")
check(hybrid["category_id"] == 397 and hybrid["name"] == "Hybrid Control", "master category resolver joins HV_P5 to category 397 Hybrid Control")
plugins = gts_master._master_plugins(parser, master, hybrid["category_id"])
check(any(row["role"] == 25 and row["dll"] == "DelDiagCodeP4.dll" for row in plugins), "current master plugin resolver decodes selected DelDiagCodeP4 role 0x19 with native provenance")
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
    [(row["category_id"], row["timer_id"], row["delay_ms"], row["unknown_dword_08"], row["raw"]) for row in timers]
    == [(397, 1, 0, 0, "000000008d01010000000000")],
    "current Hybrid timer 1 resolves to zero-millisecond post-command delay",
)

role_catalog = gts_master._master_role_catalog(parser, master, gts / "bin")
role19 = next(row for row in role_catalog if row["role"] == 25)
check(len(role_catalog) == 191 and role19["binding_count"] == 536 and role19["category_count"] == 536 and role19["binding_surface_counts"] == {"direct_transport": 536} and role19["plugins"][0]["dll"] == "DelDiagCodeP4.dll" and role19["plugins"][0]["binding_count"] == 424, "current master role census resolves operation surfaces as well as 6194 -> 191 role compression")
role5 = next(row for row in role_catalog if row["role"] == 5)
check(role5["plugins"][0]["surface"] == "support_cache_v18_proven" and role5["plugins"][1]["surface"] == "delegated_transport_v18_proven", "role query distinguishes P4 cached support from P5 delegated support probing")
engine_category = gts_master._resolve_master_category(parser, master, strings, "Engine_P5")
emps_category = gts_master._resolve_master_category(parser, master, strings, "EMPS_P5")
catalog_context_before = master.as_dict()
qualified_emps = query.native_ecu_catalog_category(master, emps_category, db_root, parser)
check(
    master.as_dict() == catalog_context_before
    and qualified_emps["catalog_context"]["load_id"] is None
    and qualified_emps["catalog_context"]["cache_action"] == "not-mutated-offline-catalog",
    "offline metadata enumeration retains the caller's native history instead of inventing cached ECU loads",
)
explicit_cache = query.native_selection_context(gts, "NA")
explicit_cache.load(parser.parse_ecu_db(db_root / "EMPS_P5.ddb"), ecu_id=405, family="Gen", load_id="explicit-emps-cache")
retained_emps = query.native_ecu_catalog_category(explicit_cache, emps_category, db_root, parser)
check(
    retained_emps["catalog_context"]["load_id"] == "explicit-emps-cache"
    and retained_emps["catalog_context"]["cached_file_reused"]
    and retained_emps["catalog_context"]["cache_action"] == "retained-explicit-load",
    "explicit native ECU cache identity survives raw metadata qualification",
)
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
    and [(m["selected_test"]["initial_read_did"], m["selected_test"]["bit_start"], m["selected_test"]["bit_end"], [frame["materialized_send"] for frame in m["initial_transaction"]["frames"]]) for m in engine_group["members"]] == [
        (0x284A, 0, 7, ["22284a"]),
        (0x284A, 8, 15, ["22284a"]),
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
    and [frame["base_frame"]["send"]["bytes"] for frame in hybrid_init_selected["initial_transaction"]["frames"]] == ["22ffff"]
    and [frame["materialized_send"] for frame in hybrid_init_selected["initial_transaction"]["frames"]] == ["222801"]
    and [frame["receive_check"] for frame in hybrid_init_selected["initial_transaction"]["frames"]] == ["62"]
    and hybrid_init_selected["linked_monitor"]["monitor_key"] == 30
    and hybrid_init_selected["linked_monitor"]["monitor"]["name"] == "Inverter Water Pump"
    and hybrid_init_selected["linked_monitor"]["monitor"]["signal_info"]["pattern_display"] == {0: "OFF", 1: "ON"}
    and hybrid_init_selected["executor"]["service"] == "0x2F"
    and hybrid_init_selected["executor"]["positive_response"] == "0x6F"
    and hybrid_init_selected["executor"]["data_id_for_act"]["table"] == 67
    and hybrid_init_selected["executor"]["data_id_for_act"]["table_class"] == "CDbDataIdForActTable"
    and hybrid_init_selected["executor"]["data_id_for_act"]["encoding_mode"] == 1
    and [frame["materialized_prefix"] for frame in hybrid_init_selected["executor"]["start"]["frames"]] == ["2f280103"]
    and [frame["materialized_prefix"] for frame in hybrid_init_selected["executor"]["stop"]["frames"]] == ["2f280100"]
    and hybrid_init_selected["executor"]["runtime_data_length"]["minimum_from_bit_geometry"] == 2
    and hybrid_init_selected["executor"]["runtime_data_length"]["probe"]["kind"] == "read_data_by_identifier_value_length"
    and hybrid_init_selected["executor"]["runtime_data_length"]["probe"]["selector"] == "0xCA"
    and [frame["materialized_request"] for frame in hybrid_init_selected["executor"]["runtime_data_length"]["probe"]["frames"]] == ["222801"]
    and [frame["positive_check"] for frame in hybrid_init_selected["executor"]["runtime_data_length"]["probe"]["frames"]] == ["62"]
    and hybrid_init_selected["executor"]["runtime_data_length"]["probe"]["response_prefix_length"] == 3
    and hybrid_init_selected["executor"]["minimum_length_examples"]["start"] == [
        {"raw_0": "2f28010300000001", "raw_1": "2f28010300010001"}
    ]
    and hybrid_init_selected["executor"]["minimum_length_examples"]["stop"] == [
        {"return_control": "2f2801000001"}
    ],
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
    and [frame["materialized_static_request"] for frame in routine_executor["start"]["frames"]] == ["31011588"]
    and [frame["materialized_static_request"] for frame in routine_executor["stop"]["frames"]] == ["31021588"]
    and [frame["materialized_static_request"] for frame in routine_executor["result"]["frames"]] == ["31031588"],
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
    and [frame["send"]["bytes"] for frame in hybrid_plan["frames"]["primary"]] == ["04"]
    and [frame["send"]["bytes"] for frame in hybrid_plan["frames"]["fallback"]] == ["14ffffff"]
    and [(row["category_id"], row["timer_id"], row["delay_ms"], row["raw"]) for row in hybrid_plan["timers"]]
    == [(397, 1, 0, "000000008d01010000000000")]
    and hybrid_plan["timer_selection"]["query"]["status"] == 0
    and len(hybrid_plan["control_flow"]["fallback_error_codes_when_function_gate_set"]) == 10,
    "command plan joins Hybrid role 0x19 plugin, category-local frames, timer, and exact state machine",
)
emps_cid_plan = commands._master_command_plan(parser, master, emps_category, 0x52, gts / "bin")
check(
    emps_cid_plan["plugin"] == "GetCID_SID22_DT.dll"
    and emps_cid_plan["semantic_status"] == "exact_plugin_identity_and_category_frame"
    and [frame["send"]["bytes"] for frame in emps_cid_plan["frames"]["request"]] == ["22f181"]
    and emps_cid_plan["response_model"]["payload_offset"] == 4
    and emps_cid_plan["response_model"]["record_size"] == 16,
    "command plan joins EMPS role 0x52 F181 wire contract to exact current response parser",
)
with tempfile.TemporaryDirectory(prefix="gts-command-case-alias-") as td:
    selected_bin = Path(td) / "selected"
    selected_bin.mkdir()
    aliased = selected_bin / "getcid_sid22_dt.DLL"
    shutil.copyfile(gts / "bin/GetCID_SID22_DT.dll", aliased)
    alias_plan = commands._master_command_plan(parser, master, emps_category, 0x52, selected_bin)
    alias_binding = next(
        row for row in registry._registry_role_bindings(parser, master, emps_category, selected_bin)
        if row["role"] == 0x52
    )
    check(
        alias_plan["plugin_identity"] == alias_binding["plugin_identity"]
        == execution_model._plugin_identity(aliased)
        and alias_plan["plugin_identity"]["path"] == aliased.name
        and alias_plan["plugin_identity"]["sha256"] == emps_cid_plan["plugin_identity"]["sha256"]
        and alias_plan["semantic_profile"] == emps_cid_plan["semantic_profile"]
        and alias_plan["semantic_status"] == "exact_plugin_identity_and_category_frame"
        and alias_plan["frames"] == emps_cid_plan["frames"],
        "copied plugin case alias retains exact role/SHA semantics and consistent command/registry provenance",
    )
    check(
        execution_model._semantic_profile_for_plugin(aliased, 0x41)[2]
        == "plugin_semantics_unrecovered_for_identity",
        "exact plugin bytes cannot acquire the semantic profile of a different role",
    )
    altered_bin = Path(td) / "altered"
    altered_bin.mkdir()
    altered_alias = altered_bin / aliased.name
    altered_alias.write_bytes(aliased.read_bytes() + b"\x00")
    altered_alias_plan = commands._master_command_plan(parser, master, emps_category, 0x52, altered_bin)
    altered_alias_binding = next(
        row for row in registry._registry_role_bindings(parser, master, emps_category, altered_bin)
        if row["role"] == 0x52
    )
    check(
        altered_alias_plan["semantic_status"] == altered_alias_binding["semantic_status"]
        == "plugin_semantics_unrecovered_for_identity"
        and altered_alias_plan["plugin_identity"] == altered_alias_binding["plugin_identity"]
        and altered_alias_plan["frames"] == {} and altered_alias_plan["response_model"] is None,
        "case alias lookup does not admit altered bytes or reuse a previously cached identity",
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
check(len(primary) == 1 and primary[0]["comm_set_metadata"]["receive_timeout"] == 1020 and primary[0]["comm_set_metadata"]["retry_count"] == 1 and primary[0]["send"]["id"] == "0x2743" and primary[0]["send"]["normalized_id"] == "0x33" and primary[0]["send"]["bytes"] == "04" and primary[0]["receive_check"]["bytes"] == "44" and primary[0]["selection"]["context"]["resolution"] == "initial", "current native selector 1 resolves source-qualified namespaced variables to 04 -> 44")
fallback = gts_master._master_frame_rows(parser, master, hybrid["category_id"], 0x102)
check(len(fallback) == 1 and fallback[0]["send"]["id"] == "0x2D28" and fallback[0]["send"]["normalized_id"] == "0x618" and fallback[0]["send"]["bytes"] == "14ffffff" and fallback[0]["receive_check"]["id"] == "0x28E4" and fallback[0]["receive_check"]["normalized_id"] == "0x1D4" and fallback[0]["receive_check"]["bytes"] == "54", "current native selector 0x102 resolves source-qualified namespaced variables to 14FFFFFF -> 54")
emps_default = commands._master_command_plan(parser, master, emps_category, 0xDA, gts / "bin")
check(
    emps_default["plugin"] == "GetCurAbsTimeInfo_DT.Dll"
    and emps_default["selected_binding"]["ordinal"] == 6135
    and emps_default["binding_query"]["mode"] == "first-role"
    and emps_default["plugin_identity"]["path"] == "GetCurAbsTimeInfo_DT.dll",
    "EMPS roleDA resolves the actual first-role fallback and selected-folder case alias",
)
initial_selector = gts_master._master_frame_rows(parser, master, 1, 0x66)
history_context = query.native_selection_context(gts, "NA")
history_context.correspondence_reflection(0, 136)
after_selector = gts_master._master_frame_rows(parser, history_context, 1, 0x66)
check(
    [row["send"]["bytes"] for row in initial_selector] == ["0100"]
    and [row["send"]["bytes"] for row in after_selector] == ["2100"]
    and history_context.as_dict()["resolution"] == "event-history",
    "explicit handler136 history changes selector66 without claiming that a vehicle emitted the event",
)
unknown_context = query.native_selection_context(gts, "NA", history_known=False)
unknown = unknown_context.query(19, 0xDA, 405)
check(
    unknown.status is None and not unknown.records and bool(unknown.raw_variants),
    "unknown native context exposes raw role variants and never substitutes initial defaults",
)
try:
    commands._master_command_plan(parser, unknown_context, emps_category, 0xDA, gts / "bin")
except UnresolvedNativeContext as exc:
    check(exc.result is not None and exc.result.status is None, "command unknown-context failure retains native query evidence")
else:
    raise AssertionError("command invented a DLL selection for unknown native history")
with tempfile.TemporaryDirectory(prefix="gts-native-history-") as td:
    event_file = Path(td) / "events.json"
    event_file.write_text(json.dumps([{"kind": "reflection", "ecu_id": 0, "handling_id": 136}]))
    replay = query.native_selection_context(gts, "NA", history=event_file)
    check(
        [row["send"]["bytes"] for row in gts_master._master_frame_rows(parser, replay, 1, 0x66)] == ["2100"],
        "public native context loader replays ordered JSON events without synthesizing live state",
    )
    result = subprocess.run(
        [str(ROOT / "tools/gts"), "frame", "1", "0x66", "--native-history", str(event_file), "--json"],
        capture_output=True, text=True, check=True,
    )
    check(
        [row["send"]["bytes"] for row in json.loads(result.stdout)] == ["2100"],
        "frame CLI exposes reproducible event-qualified native programs",
    )
    result = subprocess.run(
        [str(ROOT / "tools/gts"), "command", "EMPS_P5", "0xDA", "--native-context", "unknown", "--json"],
        capture_output=True, text=True,
    )
    failure = json.loads(result.stdout)
    check(
        result.returncode == 2 and failure["error"] == "UnresolvedNativeContext"
        and failure["status"] is None and failure["native_context"]["resolution"] == "unknown",
        "CLI unknown context returns one structured unresolved document rather than a fabricated plan",
    )
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

native_profile = parse_attach_bytes(
    b"pre=carry\r\n[S]\r\na=1\r\nb=2\r\n[S]\r\na=3\r\n;comment=literal\r\n[Last]\r\n x = y \r\n\0[Ignored]\nx=1",
    native_current=True,
)
check(
    native_profile == {"S": {"a": "3", ";comment": "literal"}, "Last": {" x ": " y "}}
    and current_profile_int("  -12suffix", 7) == -12
    and current_profile_int("garbage", 7) == 7
    and current_profile_int("2147483648", 7) == 7,
    "current profile preserves literal lexical rules, replaces repeated sections and catches decimal errors to caller defaults",
)
check(
    parse_attach_bytes(b"[S]\na=1\n[S]\nb=2\n") == {"S": {"a": "1", "b": "2"}}
    and parse_attach_bytes(b"[S]\na=1\n[Unused]", native_current=True) == {"S": {"a": "1"}},
    "historical inventory parser stays separate and final current headers do not create empty sections",
)

with tempfile.TemporaryDirectory(prefix="gts-current-cuw-selection-") as td:
    ini = Path(td)
    key_column = "ParamFileKeySystemProtocolMicon"
    flag_column = "FlagToUseCIDGetterAndFlashWriterDLL"

    def parameter_file(filename, header, rows):
        text = io.StringIO(newline="")
        writer = csv.writer(text, lineterminator="\r\n")
        writer.writerow(header)
        writer.writerows(rows)
        decoded = text.getvalue().encode("latin1")
        encoded = bytes(component for value in decoded for component in
                        ((((value >> 4) + 8) << 2), (((value & 15) + 8) << 2)))
        (ini / filename).write_bytes(encoded)

    def factory(selector, prepare="Prepare.dll", flash="Flash.dll", filename=None):
        parameter_file(filename or selector + ".ini", [
            key_column, "DLLFileNameForGetCID", "DLLFileNameForPrepareWrite",
            "DLLFileNameForFlashWrite", "EnableDLLVersionInformation",
        ], [[selector, "Getter.dll", prepare, flash, "1\n2\n3\n4"]])

    def classic(kind="13", contact="CAN", cpu="56"):
        return {"Format": {"Version": "4"}, "Vehicle": {
            "KindOfECU": kind, "ContactType": contact, "NumberOfCalibration": "1",
        }, "CPU01": {"CPUType": cpu}}

    parameter_file("Parameter.ini", [key_column, flag_column], [
        ["13CAN56", "0"], ["13CAN56", "1"], ["14CAN57", "1"], ["15CAN58", "bad"],
    ])
    selected = select_factory_routes_for_descriptor(ini, classic())
    check(
        selected["engine"]["name"] == "legacy"
        and len(selected["engine"]["master_occurrences"]) == 2,
        "ordinary missing own INI uses first exact master row, preserving duplicate occurrences",
    )
    factory("13CAN56", filename="alias.ini")
    check(
        select_factory_routes_for_descriptor(ini, classic())["engine"]["name"] == "legacy",
        "differently named INI with matching header cannot override native own-file probe",
    )
    factory("13CAN56")
    selected = select_factory_routes_for_descriptor(ini, classic())
    check(
        selected["engine"]["name"] == "phase"
        and next(binding for binding in selected["roles"] if binding["role"] == "flash")["dll"] == "Flash.dll",
        "readable ordinary own INI overrides master flag zero and selects exact phase row",
    )
    check(
        select_factory_routes_for_descriptor(ini, classic("14", cpu="57"))["engine"]["reason"] == "CPassThruException:9999"
        and select_factory_routes_for_descriptor(ini, classic("15", cpu="58"))["engine"]["reason"] == "throw-int:2"
        and select_factory_routes_for_descriptor(ini, classic("16", cpu="59"))["engine"]["reason"] == "throw-int:2",
        "failed open with true, invalid and absent master values preserves distinct native failure paths",
    )
    special = select_factory_routes_for_descriptor(ini, classic("", "P5-Unified", ""))
    check(
        special["engine"]["name"] == "phase"
        and all(binding["parameter"].get("error", {}).get("native_error") == 9999 for binding in special["roles"])
        and special["role_preconditions"][0]["stage"] == "native-node-access",
        "exact special ContactType bypasses master and own-file probe but never synthesizes missing role parameters",
    )
    raw_rows, raw_stats = factory_routes_from_ini_root(ini)
    current_rows, current_stats = factory_routes_from_ini_root(ini, current=True)
    check(
        len(raw_rows) == raw_stats["factory_rows"] == 2
        and len(current_rows) == current_stats["selector_rows"] == 4
        and current_stats["master_rows"] == 4
        and len(next(row for row in current_rows if row["selector"] == "14CAN57")["master_occurrences"]) == 1,
        "current union retains master-only selectors without changing historical factory inventory semantics",
    )

    factory("KCAN1", "FirstPrepare.dll", "FirstFlash.dll")
    factory("KCAN2", "SecondPrepare.dll", "SecondFlash.dll")
    two_cpu = classic("K", cpu="1")
    two_cpu["Vehicle"]["NumberOfCalibration"] = "2"
    two_cpu["CPU02"] = {"CPUType": "2"}
    selected = select_factory_routes_for_descriptor(ini, two_cpu)
    prepares = [binding for binding in selected["roles"] if binding["role"] == "prepare"]
    flashes = [binding for binding in selected["roles"] if binding["role"] == "flash"]
    check(
        [binding["dll"] for binding in prepares] == ["FirstPrepare.dll", "FirstPrepare.dll"]
        and prepares[1]["address_parameter"]["selector"] == "KCAN2"
        and [binding["dll"] for binding in flashes] == ["FirstFlash.dll", "SecondFlash.dll"],
        "classic prepare DLL comes from CPU0, addresses from current CPU, and flash DLL from each CPU",
    )
    modern = {"Format": {"Version": "107"}, "Vehicle": {
        "KindOfECU": "K", "ContactType": "P5-Unified", "NumberOfNode": "2",
    }, "Node01": {"RequiredSpecReproVer": "02", "Protocol": "P", "NumberOfCalibration": "2"},
       "Node02": {"RequiredSpecReproVer": "04", "Protocol": "Q", "NumberOfCalibration": "1",
                  "NumberOfLogicalBlock": "1"}, "LogicalBlock201": {"NewCID": "node2"}}
    factory("KP5-UnifiedP")
    factory("KP5-Unified")
    factory("KP5-Unified04")
    selected = select_factory_routes_for_descriptor(ini, modern)
    check(
        [cpu["cpu_index"] for cpu in selected["model"]["cpus"]] == [0, 1, 2]
        and all(cpu["cpu_type"] == "" for cpu in selected["model"]["cpus"])
        and selected["roles"][0]["parameter"]["selector"] == "KP5-UnifiedP"
        and [binding["parameter"]["selector"] for binding in selected["roles"] if binding["role"] == "prepare"]
        == ["KP5-Unified", "KP5-Unified", "KP5-Unified04"],
        "modern CPUType stays empty, getter appends first-node protocol, and node preparation uses exact required-spec rule",
    )
    modern["Vehicle"]["ContactType"] = "Phase6"
    modern["Vehicle"]["NumberOfNode"] = "1"
    modern["Node01"].update(RequiredSpecReproVer="04", Protocol="02")
    modern["Node01"]["NumberOfLogicalBlock"] = "2"
    modern["LogicalBlock101"] = {"NewCID": "first"}
    modern["LogicalBlock102"] = {"NewCID": "second"}
    factory("KPhase602")
    selected = select_factory_routes_for_descriptor(ini, modern)
    check(
        all(binding["parameter"]["selector"] == "KPhase602" for binding in selected["roles"]),
        "Phase6 node role discriminator is Protocol, not required-spec or a protocol guessed from selector text",
    )
    ten_nodes = {"Format": {"Version": "107"}, "Vehicle": {
        "KindOfECU": "K", "ContactType": "P5-Unified", "NumberOfNode": "10",
    }, "Node00": {"NumberOfCalibration": "1", "Protocol": "WRAPPED", "RequiredSpecReproVer": "02"},
       "Node10": {"NumberOfCalibration": "1", "Protocol": "MAIN", "RequiredSpecReproVer": "05"}}
    factory("KP5-Unified05")
    selected = select_factory_routes_for_descriptor(ini, ten_nodes)
    check(
        selected["model"]["cpus"] == [{"cpu_index": 0, "cpu_type": "", "node_index": 9}]
        and selected["model"]["nodes"][9]["Protocol"] == "MAIN"
        and next(binding for binding in selected["roles"] if binding["role"] == "prepare")
            ["parameter"]["selector"] == "KP5-Unified05",
        "node10 CPU allocation prepass wraps to Node00 while main Protocol/spec fields come from Node10",
    )
    ten_nodes["Node00"]["NumberOfCalibration"] = "2"
    unsafe = select_factory_routes_for_descriptor(ini, ten_nodes)
    check(
        unsafe["model"]["error"]["allocation_prepass_cpus"] == 2
        and unsafe["model"]["error"]["materialized_cpus"] == 1
        and unsafe["model"]["error"]["native_unsafe"] is True
        and unsafe["roles"] == [],
        "allocation/materialization divergence is a native unsafe boundary, not a sanitized selector",
    )
    ten_nodes["Node00"]["NumberOfCalibration"] = "-1"
    unsafe = select_factory_routes_for_descriptor(ini, ten_nodes)
    check(
        unsafe["model"]["error"]["declared_cpus"] == -1
        and "native_exception" not in unsafe["model"]["error"],
        "negative prepass CPU counts are not clamped or assigned an invented native exception",
    )
    zero_logical = {"Format": {"Version": "107"}, "Vehicle": {
        "KindOfECU": "K", "ContactType": "P5-Unified", "NumberOfNode": "1",
    }, "Node01": {"NumberOfCalibration": "0", "NumberOfLogicalBlock": "0",
                  "RequiredSpecReproVer": "02"},
       "LogicalBlock101": {"NewCID": "first"}, "LogicalBlock132": {"NewCID": "last"}}
    unsafe = select_factory_routes_for_descriptor(ini, zero_logical)
    check(
        unsafe["model"]["error"]["allocation_prepass_cpus"] == 2
        and unsafe["model"]["error"]["materialized_cpus"] == 0,
        "zero declared logical count does not stop the prepass before nonempty CID admission through ID32",
    )
    zero_logical["Node01"]["RequiredSpecReproVer"] = "04"
    unsafe = select_factory_routes_for_descriptor(ini, zero_logical)
    check(
        unsafe["model"]["error"]["admitted_logical_blocks"] == 2
        and unsafe["model"]["error"]["native_unsafe"] is True,
        "logical main parser with zero allocation still scans and can write admitted records out of bounds",
    )
    zero_logical["Node01"]["NumberOfLogicalBlock"] = "-1"
    check(
        select_factory_routes_for_descriptor(ini, zero_logical)["model"]["error"]
            ["declared_logical_blocks"] == -1,
        "negative main logical count remains an unsigned-allocation boundary",
    )
    zero_logical["Vehicle"]["NumberOfNode"] = "0"
    check(
        select_factory_routes_for_descriptor(ini, zero_logical)["model"]["error"]["declared_nodes"] == 0,
        "zero nodes expose native allocation/last-node indexing rather than a fake empty model",
    )

    old = classic("ENG & ECT", "SIL")
    old["Format"]["Version"] = "3"
    old["CPU01"] = {"ECUType": "MPC565"}
    check(
        select_factory_routes_for_descriptor(ini, old)["engine"]["selector"] == "0SIL9",
        "Version3 maps old names and normalizes MPC565 to CPU9 only for exact SIL",
    )
    old["Vehicle"]["KindOfECU"] = "unknown"
    check(
        select_factory_routes_for_descriptor(ini, old)["model"]["error"]["native_exception"] == "std::out_of_range",
        "unknown historical native Kind mapping fails rather than becoming empty or synthetic zero",
    )

expected_factory_rows = []
expected_master_occurrences = {}
for ini_path in (installed_cuwplus / "Ini").glob("*.ini"):
    decoded = decode_parameter_ini(ini_path.read_bytes()).decode("latin1")
    csv_rows = list(csv.reader(io.StringIO(decoded)))
    if not csv_rows or "ParamFileKeySystemProtocolMicon" not in csv_rows[0]:
        continue
    column = csv_rows[0].index("ParamFileKeySystemProtocolMicon")
    if "DLLFileNameForPrepareWrite" in csv_rows[0]:
        expected_factory_rows.extend((cells[column], ini_path.name, index)
                                     for index, cells in enumerate(csv_rows[1:], 1))
    if ini_path.name == "Parameter.ini":
        for index, cells in enumerate(csv_rows[1:], 1):
            expected_master_occurrences.setdefault(cells[column].split("\n", 1)[0], []).append(index)
declared_selectors = {row[0] for row in expected_factory_rows}
expected_union = expected_factory_rows + [(selector, None, None) for selector in expected_master_occurrences
                                         if selector not in declared_selectors]
installed_routes = query._route_rows(installed_cuwplus)
check(
    sorted((row["selector"], row["parameter_file"], row["row_index"]) for row in installed_routes)
    == sorted(expected_union)
    and all([occurrence["row_index"] for occurrence in row["master_occurrences"]]
            == expected_master_occurrences.get(row["selector"], []) for row in installed_routes),
    "installed current selection rows equal exact factory occurrences plus master-only selectors and ordered master joins",
)
routes = query._route_rows(cuwplus)
route04 = [row for row in routes if row["selector"] == "P5-Unified04"]
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

p5_route = [row for row in routes if row["selector"] == "P5-Unified"]
check(len(p5_route) == 1, "P5-Unified is an exact current selector, not a parsed ContactType")
check(p5_route[0]["prepare_writer"] == "TCUWCanUnifiedPrepareWriter.dll", "Camry CUW resolves current Unified prepare writer")
check(p5_route[0]["flash_writer"] == "TCUWCanUnifiedFlashWriter.dll", "Camry CUW resolves current Unified flash writer")

kgp = query._resolve_pe(gts, cuwplus, "KgpDataCtrl.dll")
check(kgp.is_file(), "PE resolver finds current KgpDataCtrl.dll")
strings_in_kgp = pe_utils.binary_strings(kgp.read_bytes())
check(any("CDbDatamonitorP5Table" in value for value in strings_in_kgp), "PE string surface exposes current Data Monitor implementation class")

print("verified unified GTS+ DDB/CUW/PE query surface")
