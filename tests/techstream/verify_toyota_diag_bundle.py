"""Verify the universal clean Toyota diagnostic bundle derived from current GTS+."""
from __future__ import annotations

import hashlib
import io
import json
import os
import sqlite3
import struct
import tempfile
import zipfile
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from tools import REPO_ROOT
REPO = REPO_ROOT

from tools.techstream import techstream_paths
from tools.techstream.diag_bundle import DEFAULT_BUNDLE, DiagnosticBundle, DiagnosticBundleWriter
from tools.techstream.diag_runtime_db import export_runtime_db
from tools.techstream.gts.bundle import _bundle_customize_catalog, _bundle_session_control, write_toyota_diag_bundle

ART = DEFAULT_BUNDLE

passed = failed = 0


def check(name: str, condition: object) -> None:
    global passed, failed
    ok = bool(condition)
    passed += int(ok)
    failed += int(not ok)
    print(f"[{'PASS' if ok else 'FAIL'}] {name}")


def verify_session_program_projection() -> None:
    context = SimpleNamespace(
        query=lambda *_: SimpleNamespace(status=0, records=(SimpleNamespace(generation=20),), as_dict=lambda: {"status": 0}),
        as_dict=lambda: {"history_known": True, "resolution": "initial"},
    )
    def program(_parser, _context, _category_id, selector, name):
        sends = {0xD1: ("1001", "1001"), 0xD2: ("1003", "1003"), 0xDD: ("22f186", "1003")}[selector]
        return {
            "name": name, "selector": f"0x{selector:X}", "resolved": True,
            "frames": [{"send": send, "comm_set": 7} for send in sends],
            "native": {"status": 0},
        }
    with patch("tools.techstream.gts.bundle._registry_request_row", side_effect=program):
        row = _bundle_session_control(None, context, [{"category_id": 372}])["per_category"]["372"]
    check("bundle sessions preserve multiframe D1/D2/DD programs and all keepalive steps",
          row["session_executor_supported"] is True
          and row["default_session_values"] == [1, 1]
          and row["extended_session_values"] == [3, 3]
          and len(row["default_session"]["frames"]) == len(row["extended_session"]["frames"]) == 2
          and [step["kind"] for step in row["keepalive"]["steps"]] == ["session_did_poll", "extended_session_refresh"])
    unknown = SimpleNamespace(
        query=lambda *_: SimpleNamespace(status=None, records=(), as_dict=lambda: {"status": None}),
        as_dict=lambda: {"history_known": False, "resolution": "unknown"},
    )
    unresolved = {"resolved": False, "frames": [], "native": {"status": None}}
    with patch("tools.techstream.gts.bundle._registry_request_row", return_value=unresolved):
        row = _bundle_session_control(None, unknown, [{"category_id": 372}])["per_category"]["372"]
    check("bundle sessions preserve unknown native context without manufactured session defaults",
          row["generation_low5"] is None
          and row["category_native_query"]["status"] is None
          and row["default_session_value"] is None
          and row["extended_session_value"] is None
          and row["session_executor_supported"] is False
          and row["default_session"]["native"]["status"] is None)


def verify_customize_context_projection() -> None:
    raw = bytearray(52)
    struct.pack_into("<HHH", raw, 8, 1, 200, 449)
    struct.pack_into("<H", raw, 0x2A, 0x225A)
    master = SimpleNamespace(sections={20: [], 21: [bytes(raw)], 22: [], 34: []})
    strings = SimpleNamespace(get_string=lambda _: "")
    targets = {449: {"name": "Context target", "generation": 22}}
    def context(status, resolution):
        return SimpleNamespace(
            query=lambda *_: SimpleNamespace(
                status=status, records=(object(),) if status == 0 else (),
                as_dict=lambda: {"status": status},
            ),
            as_dict=lambda: {"resolution": resolution, "history_known": status is not None},
        )
    with patch("tools.techstream.gts.bundle.ddb_records", side_effect=lambda rows: rows):
        selected = _bundle_customize_catalog(master, strings, targets, context(0, "event-history"))["items"][0]
        unknown = _bundle_customize_catalog(master, strings, targets, context(None, "unknown"))["items"][0]
        failed_target = _bundle_customize_catalog(master, strings, targets, context(0xA0030106, "event-history"))["items"][0]
    check("Customize metadata follows supplied event context, not last raw category",
          selected["target_generation"] == 22
          and selected["target_resolution"] == "event-history"
          and selected["modern_executor"]["family"] == "p6"
          and selected["source_ordinal"] == 0)
    check("Customize preserves unknown context and native target failures without default substitution",
          unknown["target_generation"] is None
          and unknown["target_category_name"] == ""
          and unknown["target_native_query"]["status"] is None
          and unknown["target_resolution"] == "unknown"
          and "modern_executor" not in unknown
          and failed_target["target_generation"] is None
          and failed_target["target_native_query"]["status"] == 0xA0030106
          and failed_target["target_resolution"] == "native-failure")


def verify_member_storage() -> None:
    members = [
        ("catalogs/NA/372.json", b'{"source":"NA","rows":[2,1,2]}\n'),
        ("catalogs/EU/372.json", b'{"source":"EU","rows":[2,1,2]}\n'),
        ("index.json", b'{"regions":["NA","EU"]}\n'),
    ]
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        first = root / "first"
        second = root / "second"
        for target in (first, second):
            writer = DiagnosticBundleWriter(target)
            for name, payload in members:
                writer.add(name, io.BytesIO(payload))
            writer.finish()
        bundle = DiagnosticBundle(first)
        bundle.verify()
        check("canonical members preserve source-qualified names, physical ordering and exact bytes",
              bundle.namelist() == [name for name, _ in members]
              and all(bundle.read(name) == payload for name, payload in members))
        check("canonical JSON inspection retains source-qualified payloads",
              bundle.json("catalogs/NA/372.json") == {"source": "NA", "rows": [2, 1, 2]}
              and bundle.json("catalogs/EU/372.json") == {"source": "EU", "rows": [2, 1, 2]})
        check("canonical gzip member regeneration is deterministic",
              all(path.read_bytes() == (second / path.relative_to(first)).read_bytes()
                  for path in first.rglob("*") if path.is_file()))
        export = root / "portable.zip"
        bundle.export_zip(export)
        bundle.compare_zip(export)
        with zipfile.ZipFile(export) as archive:
            check("portable export restores all member bytes and names in original order",
                  archive.namelist() == bundle.namelist()
                  and all(archive.read(name) == payload for name, payload in members)
                  and archive.testzip() is None)
        other_export = root / "other.zip"
        bundle.export_zip(other_export)
        check("portable ZIP export is byte-for-byte deterministic",
              export.read_bytes() == other_export.read_bytes())
        damaged = first / "catalogs/NA/372.json.gz"
        damaged.write_bytes((first / "catalogs/EU/372.json.gz").read_bytes())
        try:
            bundle.verify()
        except ValueError:
            check("canonical integrity detects valid-gzip member substitution", True)
        else:
            check("canonical integrity detects valid-gzip member substitution", False)


def verify_runtime_sqlite_projection() -> None:
    index = {
        "schema": "toyota-diagnostics-bundle-v4",
        "release": "test",
        "default_region": "NA",
        "regions": {
            "NA": {
                "vehicles": {"12704": {"vehicle_type": 12704, "name": "Camry HV", "install_set_ids": [12]}},
                "install_sets": {"12": [{
                    "category_id": 498, "connection_route_selector": 18,
                    "connection_frame_id": 0, "route_key": "498:18",
                }]},
                "routes": {"498:18": {
                    "physical_request_address": 0x792, "address_extension": 0,
                    "transport_kind": "iso15765-phase-family",
                }},
                "selected_categories": {"498": {
                    "name": "Front Recognition Camera 2", "short_name": "FRC_P5",
                    "database": "FRC_P5.ddb", "generation": 20,
                    "support_mode": "p5-standard",
                    "catalog_member": "catalogs/NA/498.json",
                }},
                "utilities": {"bindings": [{
                    "role": 0xD4, "semantic_kind": "single_routine_active_test",
                    "dll": "SingleRoutineActiveTest.dll",
                }]},
            },
        },
    }
    catalog = {
        "dids": {"0x1601": [{"name": "LTA Control Condition"}]},
        "dtcs": {}, "active_tests": [], "functions": [], "plugins": [], "utilities": [],
    }
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp) / "bundle"
        writer = DiagnosticBundleWriter(root)
        writer.add("catalogs/NA/498.json", io.BytesIO((json.dumps(catalog) + "\n").encode()))
        writer.add("index.json", io.BytesIO((json.dumps(index) + "\n").encode()))
        writer.finish()
        out = Path(tmp) / "runtime.sqlite"
        with patch("tools.techstream.diag_runtime_db._supplemental_rows", return_value=[]):
            result = export_runtime_db(root, out)
        with sqlite3.connect(out) as db:
            check("runtime SQLite records source schema and release",
                  db.execute("SELECT value FROM meta WHERE key='schema'").fetchone()[0] == "toyota-diagnostics-sqlite-v1"
                  and db.execute("SELECT value FROM meta WHERE key='release'").fetchone()[0] == "test")
            check("runtime SQLite indexes vehicle routes and OEM search terms",
                  db.execute("SELECT request_address FROM vehicle_ecus").fetchone()[0] == 0x792
                  and db.execute("SELECT count(*) FROM items_fts WHERE items_fts MATCH 'LTA'").fetchone()[0] == 1
                  and result["items"] == 4)


def main() -> int:
    verify_runtime_sqlite_projection()
    verify_session_program_projection()
    verify_customize_context_projection()
    verify_member_storage()
    gts = techstream_paths.resolve_gts_root(os.environ.get("GTSPLUS_ROOT"))
    source_hashes: dict[Path, str] = {}
    def source_matches(source: dict[str, object]) -> bool:
        path = Path(str(source["path"]))
        if not path.is_absolute():
            path = gts / path
        path = path.resolve()
        if not path.is_relative_to(gts.resolve()) or not path.is_file():
            return False
        if path not in source_hashes:
            source_hashes[path] = hashlib.sha256(path.read_bytes()).hexdigest()
        return source_hashes[path] == source["sha256"]
    archive = DiagnosticBundle(ART)
    archive.verify()
    check("bundle members match their exact-byte integrity manifest", True)
    with archive.open("index.json") as index_source:
        index = json.load(index_source)
        check("bundle declares the route-selector schema",
              index["schema"] == "toyota-diagnostics-bundle-v4")

        check("universal Toyota bundle does not project a Panda wiring default",
              "default_panda_bus" not in index)
        p5_contract = index["support_contracts"]["p5"]
        p6_contract = index["support_contracts"]["p6"]
        check("P5 and P6 support contracts are independent Toyota families",
              set(index["support_contracts"]) == {"p5", "p6"}
              and p5_contract["did_root"]["request"] == "220101"
              and p5_contract["routine_root"]["request"] == "31011001"
              and p5_contract["routine_root"]["root_request_rid"] == "0x1001"
              and p5_contract["routine_root"]["root_bitmap_base"] == "0x0000"
              and p5_contract["routine_root"]["selector_range"] == ["0x0200", "0xDF00"]
              and p5_contract["routine_root"]["implementation"]["CreateEnableRIdList"] == "0x10066160"
              and p6_contract["did_root"]["request"] == "22a100")
        check("ordinary Toyota P5 preserves root IDs and skips Toyota-reserved group queries",
              p5_contract["standard_did"]["root_ids_remain_supported"] is True
              and p5_contract["standard_did"]["selector_excluded"] == ["0xF300", "0xFD00"]
              and p5_contract["standard_did"]["member_offset"] == 1
              and p5_contract["standard_did"]["implementation"]["CreateEnableDataIdList"] == "0x10063890")
        check("P6 DID/RID support hierarchy is byte-exact and independently pinned",
              p6_contract["did_root"]["root_base"] == "0xA100"
              and p6_contract["did_root"]["root_shift"] == 0
              and p6_contract["did_root"]["selector_excluded"] == ["0xA1FD", "0xA1FE"]
              and p6_contract["did_root"]["selector_ids_remain_supported"] is True
              and p6_contract["routine_root"]["root_base"] == "0xD100"
              and p6_contract["implementation"]["AnalyzeFrameData"] == "0x100678D0"
              and p6_contract["implementation"]["CreateEnableDataIdList"] == "0x100679A0"
              and p6_contract["implementation"]["CreateEnableRIdList"] == "0x10067CF0")

        na_customize = json.loads(archive.read("customize/NA/0.json"))
        wireless = next(row for row in na_customize["groups"]
                        if row["body_type"] == 0 and row["group_id"] == 1)
        open_door = next(row for row in na_customize["items"]
                         if row["group_id"] == 1 and row["item_id"] == 23)
        check("NA Customize witness preserves OEM group/item/choice and target geometry",
              wireless["name"] == "Wireless Door Lock"
              and open_door["name"] == "Open Door Warn"
              and open_door["target_category_id"] == 26
              and open_door["target_category_name"] == "Theft Deterrent"
              and open_door["legacy_data_id"] == 1009
              and [row["name"] for row in open_door["choices"]] == ["OFF", "ON"]
              and [row["value"] for row in open_door["choices"]] == [0, 1]
              and open_door["current_bit_start"] == 7
              and open_door["current_bit_end"] == 7)
        p5_customize = next(row for row in na_customize["items"]
                            if row["group_id"] == 1 and row["item_id"] == 200
                            and row["target_category_id"] == 449)
        p6_customize = next(row for row in na_customize["items"]
                            if row["group_id"] == 1 and row["item_id"] == 210
                            and row["target_category_id"] == 6033)
        check("NA current P5/P6 Customize rows export exact write DID/phase/merge geometry",
              p5_customize["name"] == "Wireless Control Function"
              and p5_customize["write_did"] == 0x225A
              and p5_customize["target_route_selector"] == 0x22
              and [p5_customize["write_bit_start"], p5_customize["write_bit_end"]] == [0, 7]
              and p5_customize["merge_mode"] == 0
              and p5_customize["modern_executor"]["family"] == "p5"
              and p6_customize["name"] == "Wireless Remote Control Setting"
              and p6_customize["write_did"] == 0x225A
              and p6_customize["target_route_selector"] == 0x18
              and p6_customize["modern_executor"]["family"] == "p6")

        for region in ("NA", "EU", "JP"):
            regional = index["regions"][region]
            categories = regional["selected_categories"]
            raw_categories = [
                row for row in regional["raw_category_occurrences"]
                if row["source"]["family"] == "Gen"
            ]
            expected_raw_count = {"NA": 2171, "EU": 2180, "JP": 2165}[region]
            check(f"{region} preserves every physical Gen category occurrence",
                  len(regional["category_rows"]) == expected_raw_count
                  and len(raw_categories) == expected_raw_count
                  and [row["ordinal"] for row in raw_categories] == list(range(expected_raw_count))
                  and all(len(bytes.fromhex(row["raw"])) == 76 for row in raw_categories)
                  and regional["counts"]["raw_category_row_count"] == expected_raw_count)
            check(f"{region} labels raw catalogs and initial/selected snapshots separately",
                  "categories" not in regional
                  and regional["native_context"]["resolution"] == "initial"
                  and regional["native_context"]["history_known"] is True
                  and regional["initial_native_context"]["resolution"] == "initial"
                  and regional["initial_categories"] is not None
                  and "unproved" in regional["raw_catalog_boundary"]
                  and all(row["status"] == 0 for row in regional["category_resolution"].values()))
            check(f"{region} source paths and hashes name the actual selected Gen/Spe inputs",
                  regional["source_identity"]["master"]["path"] == f"{region}/DB/Gen/Toyota.ddb"
                  and regional["source_identity"]["strings"]["path"] == f"{region}/DB/Gen/M_English.ddb"
                  and all(source_matches(source) for source in regional["source_identity"].values())
                  and all(source_matches(row["source"]) for row in regional["native_context"]["files"]))
            check(f"{region} P6 Engine classification follows Toyota plugin dispatch",
                  categories["6000"]["database"] == "Engine_CM_P6.ddb"
                  and categories["6000"]["support_family"] == "p6"
                  and categories["6000"]["support_mode"] == "p6-standard"
                  and categories["6000"]["catalog_available"] is True
                  and categories["6000"]["catalog_member"] == f"catalogs/{region}/6000.json")
            check(f"{region} representative current TSS3 categories bind literal ordinary-Toyota P5 mode",
                  all(categories[str(cid)]["support_family"] == "p5"
                      and categories[str(cid)]["support_mode"] == "p5-standard"
                      and categories[str(cid)]["support_plugin_single"]["dll"] == "GetSupportP5_DT.dll"
                      for cid in (372, 397, 405, 435, 498)))
            check(f"{region} P5 shared-plugin partner/Hino modes are not collapsed into ordinary Toyota",
                  categories["722"]["support_mode"] == "p5-subaru"
                  and categories["8500"]["support_mode"] == "p5-suzuki"
                  and categories["851"]["support_mode"] == "p5-mazda"
                  and categories["5033"]["support_mode"] == "p5-hino")
            routes = regional["routes"]
            p5_route = routes["498:18"]
            p6_route = routes["6000:24"]
            check(f"{region} P5 route remains Toyota Phase5 ISO15765 CAN",
                  p5_route["transport_kind"] == "iso15765-phase-family"
                  and p5_route["controller"].startswith("CCommCtrlISO15765")
                  and p5_route["physical_request_address"] == 0x792)
            check(f"{region} P6 route selector 0x18 selects Toyota 29-bit ISO15765 normal-fixed",
                  p6_route["transport_kind"] == "iso15765-29bit-normal-fixed"
                  and p6_route["controller"] == "CCommCtrlISO15765_29BitCan"
                  and p6_route["request_address_field"] == 0x00
                  and p6_route["physical_request_address"] == 0x18DA00F1
                  and p6_route["physical_response_address"] == 0x18DAF100
                  and p6_route["functional_request_address"] == 0x18DB33F1)

            dispatch = regional["vehicle_resolver_dispatch"]
            check(f"{region} VIN10 generation dispatch is exact and 5..19 follow an unresolved alternate path",
                  dispatch["vin10_generation_low5"] == {
                      "3": "phase3", "4": "phase4", "20": "phase5", "21": "phase5", "22": "phase6",
                  }
                  and dispatch["vin10_rejected_generation_low5"] == list(range(5, 20))
                  and dispatch["roles"]["0x45"]["semantic"] == "legacy_select_vehicle"
                  and dispatch["roles"]["0x45"]["binary_present_in_current_gtsplus"] is False
                  and dispatch["roles"]["0x7D"]["binary_present_in_current_gtsplus"] is True)

            session = regional["session_control"]
            check(f"{region} session metadata has no generation/category permission allowlist",
                  session["kind"] == "toyota-per-category-selector-lifecycle"
                  and "eligible_generation_low5" not in session
                  and "wire_proven_categories" not in session)
            programs = [
                program
                for row in session["per_category"].values()
                for program in (row["default_session"], row["extended_session"], row["keepalive"]["program"])
            ]
            check(f"{region} session programs retain complete native selector rows and first-row CommSet",
                  all(
                      (
                          len(program["frames"]) == len(program["native"]["query"]["records"])
                          and all(
                              frame["comm_set"] == int.from_bytes(
                                  bytes.fromhex(program["native"]["query"]["records"][0]["raw"])[4:6], "little"
                              )
                              for frame in program["frames"]
                          )
                      ) if program["resolved"] else (
                          program["frames"] == [] and program["native"]["status"] is not None
                      )
                      for program in programs
                  ))
            check(f"{region} session values retain every emitted DSC step",
                  all(
                      row["default_session_values"] == [
                          bytes.fromhex(frame["send"])[1] for frame in row["default_session"]["frames"]
                      ]
                      and row["extended_session_values"] == [
                          bytes.fromhex(frame["send"])[1] for frame in row["extended_session"]["frames"]
                      ]
                      for row in session["per_category"].values() if row["session_executor_supported"]
                  ))
            for cid in (372, 397, 405, 435, 498):
                row = session["per_category"][str(cid)]
                if not (row["session_executor_supported"] is True
                        and row["default_session_value"] == 1
                        and row["extended_session_value"] == 3):
                    check(f"{region} TSS3 category-local D1/D2 session executor is recovered", False)
                    break
            else:
                check(f"{region} TSS3 category-local D1/D2 session executor is recovered", True)

        p6_engine_catalog = json.loads(archive.read("catalogs/NA/6000.json"))
        p6_mode6 = next(row for row in p6_engine_catalog["active_tests"]
                        if row["kind"] == "direct" and row["id"] == 1)
        check("P6 direct Active Test mode-6 geometry and live support gate are explicit",
              p6_mode6["name"] == "Activate the EVAP Purge VSV"
              and p6_mode6["did"] == 0x2801
              and p6_mode6["encoding_mode"] == 6
              and p6_mode6["control_enable_mask"]["start"] == "none"
              and p6_mode6["control_enable_mask"]["stop"] == "none"
              and p6_mode6["support_gate"] == {
                  "family": "p6", "mode": "p6-standard", "kind": "did", "identifier": 0x2801,
                  "inventory": "selector 0xC8: A100/A1nn enabled-DID list",
                  "length_probe": "selector 0xCA: 22 <DID>; N = received_length - 3",
              }
              and p6_mode6["signal_info"]["choices"] == [{"value": 0, "text": "OFF"}, {"value": 1, "text": "ON"}])
        p6_masked_routine = next(row for row in p6_engine_catalog["active_tests"]
                                  if row["kind"] == "routine" and row["id"] == 40000)
        check("P6 routine Active Test carries exact D100/D1nn RID support gate",
              p6_masked_routine["fixed_request"] is False
              and p6_masked_routine["output_mask_button"]["bytes"] == "ff"
              and p6_masked_routine["support_gate"] == {
                  "family": "p6", "mode": "p6-standard", "kind": "rid", "identifier": 0x1105,
                  "inventory": "selector 0xCC: D100/D1nn enabled-RID list",
              })

        p6_engine_catalog = json.loads(archive.read("catalogs/NA/6000.json"))
        p6_simple = next(row for row in p6_engine_catalog["utilities"] if row["id"] == 8001)
        check("universal P6 Engine catalog exports fixed Simple Operation Utility geometry",
              p6_simple["name"] == "Switch Specification Information"
              and p6_simple["routine_id"] == 0xDA03
              and [frame["materialized_static_request"] for frame in p6_simple["start_frames"]] == ["3101da03"]
              and [frame["materialized_static_request"] for frame in p6_simple["stop_frames"]] == ["3102da03"]
              and [frame["materialized_static_request"] for frame in p6_simple["result_frames"]] == ["3103da03"]
              and p6_simple["timer_ms"] == 8000
              and p6_simple["check_interval_ms"] == 200
              and p6_simple["support_gate"]["mode"] == "p6-standard")

        hybrid_catalog = json.loads(archive.read("catalogs/NA/397.json"))
        engine_catalog = json.loads(archive.read("catalogs/NA/372.json"))
        engine_groups = engine_catalog["active_test_groups"]
        group76 = next(row for row in engine_groups["groups"] if row["group_id"] == 76)
        group102 = next(row for row in engine_groups["groups"] if row["group_id"] == 102)
        check("universal Engine catalog exports four composable type-33 groups and one mixed-DID blocked group",
              engine_groups["materializable_group_count"] == 4
              and engine_groups["blocked_group_count"] == 1
              and group76["did"] == 0x284A
              and [row["input_slot"] for row in group76["member_inputs"]] == [1, 2]
              and group102["execution"] == "blocked")
        engine_shared_direct = next(row for row in engine_catalog["active_tests"] if row["id"] == 77)
        check("universal Engine catalog exports one-to-many type-67 geometry for shared-DID direct controls",
              engine_shared_direct["did"] == 0x284A
              and engine_shared_direct["encoding_mode"] == 0
              and len(engine_shared_direct["data_id_for_act_records"]) == 2
              and engine_shared_direct["control_enable_mask"]["start"] == "type67_rows_for_selected_byte_span"
              and engine_shared_direct["execution"] == "plan_only")
        engine_simple = next(row for row in engine_catalog["utilities"] if row["id"] == 8001)
        check("universal P5 Engine catalog exports fixed Simple Operation Utility geometry",
              engine_simple["name"] == "Reset Memory"
              and engine_simple["routine_id"] == 0x1187
              and [frame["materialized_static_request"] for frame in engine_simple["start_frames"]] == ["31011187"]
              and [frame["materialized_static_request"] for frame in engine_simple["stop_frames"]] == ["31021187"]
              and [frame["materialized_static_request"] for frame in engine_simple["result_frames"]] == ["31031187"]
              and engine_simple["timer_ms"] == 180000
              and engine_simple["check_interval_ms"] == 200
              and engine_simple["support_gate"]["mode"] == "p5-standard"
              and engine_simple["execution"] == "plan_only")
        engine_static_routine = next(row for row in engine_catalog["active_tests"] if row["id"] == 40402)
        check("universal Engine catalog grades static routine-command bytes as executable",
              [frame["materialized_static_request"] for frame in engine_static_routine["start_frames"]] == ["3101113600"]
              and [row["bytes"] for row in engine_static_routine["routine_commands"]] == ["00"]
              and engine_static_routine["fixed_request"] is True
              and engine_static_routine["execution"] == "executable")
        hybrid_engineering = next(row for row in hybrid_catalog["active_tests"] if row["id"] == 1)
        check("universal Hybrid direct Active Test carries clean role-0x70 engineering metadata",
              hybrid_engineering["signal_info"]["physical"]["decimal_point_count"] == 0
              and hybrid_engineering["signal_info"]["choices"] == [{"value": 1, "text": "ON"}]
              and hybrid_engineering["signal_info"]["engineering_to_raw"]["source"].endswith("CStartActTstSnd::SetValue"))
        hybrid_test = next(row for row in hybrid_catalog["active_tests"] if row["id"] == 1)
        check("bundle catalog retains raw bindings separately from context-selected role defaults",
              "plugins" in hybrid_catalog
              and "selected_plugins" in hybrid_catalog
              and all("occurrence" in row for row in hybrid_catalog["plugins"])
              and all("native" in row for row in hybrid_catalog["selected_plugins"])
              and source_matches(hybrid_catalog["source_identity"]["database"])
              and hybrid_catalog["category"]["catalog_context"]["source"]["sha256"]
                  == hybrid_catalog["source_identity"]["database"]["sha256"])
        hybrid_ffd = next(row for row in hybrid_catalog["commands"] if row["kind"] == "p5_dtc_snapshot")
        check("universal Hybrid catalog exports generic P5 DTC snapshot request",
              hybrid_ffd["role"] == 0xB5
              and hybrid_ffd["plugin_binding"]["binding_category_id"] == 0
              and hybrid_ffd["plugin_binding"]["dll"] == "GetEachFrzFrmDatP5_DT.dll"
              and [frame["send"] for frame in hybrid_ffd["requests"][0]["frames"]] == ["1904000000ff"]
              and [frame["check"] for frame in hybrid_ffd["requests"][0]["frames"]] == ["5904"])
        eps_catalog = json.loads(archive.read("catalogs/NA/405.json"))
        eps_ffd_meta = eps_catalog["generic_ffd"]
        eps_ffd_steering = next(row for row in eps_ffd_meta["signals"] if row["name"] == "Steering Angle")
        check("universal EPS catalog exports generic P5 FFD signal/condition semantics",
              eps_ffd_steering["snapshot_did"] == 0x3037
              and eps_ffd_steering["signal_info"]["unit"] == "deg"
              and eps_ffd_meta["condition_count"] == 2
              and eps_ffd_meta["dynamic_lsb_table_present"] is False)
        hybrid_rob_meta = hybrid_catalog["rob"]
        hybrid_behavior = next(row for row in hybrid_rob_meta["behavior_codes"] if row["behavior_code"] == 0x0450)
        check("universal Hybrid catalog exports current RoB behavior semantics",
              hybrid_behavior["signature"] == "X0450"
              and hybrid_behavior["name"] == "Hybrid/EV Battery Pack Sensor Module Mismatch"
              and hybrid_rob_meta["dynamic_lsb_table_present"] is False)
        eps_catalog = json.loads(archive.read("catalogs/NA/405.json"))
        eps_steering = next(row for row in eps_catalog["rob"]["signals"] if row["name"] == "Steering Angle")
        check("universal EPS catalog exports current RoB Steering Angle decoder metadata",
              eps_steering["did"] == 0x5037
              and eps_steering["bit_start"] == 0 and eps_steering["bit_end"] == 15
              and eps_steering["support_condition_key"] == 0
              and eps_steering["local_support_mode"] == 0
              and eps_steering["dynamic_lsb_possible"] is False
              and eps_steering["signal_info"]["mul"] == 15
              and eps_steering["signal_info"]["unit"] == "deg")
        hybrid_rob = next(row for row in hybrid_catalog["commands"] if row["kind"] == "p5_rob")
        check("universal Hybrid catalog preserves native P5 RoB triplet order and decode offsets",
              hybrid_rob["role"] == 0xA0
              and hybrid_rob["plugin_binding"]["binding_category_id"] == 397
              and hybrid_rob["plugin_binding"]["exact_category_binding"] is True
              and [
                  [frame["send"] for frame in hybrid_rob["requests"][phase]["frames"]]
                  for phase in ("inventory", "frames", "record")
              ] == [
                  ["ab11", "ab01"],
                  ["ab120000", "ab020000"],
                  ["ab1300000000", "ab0300000000"],
              ]
              and hybrid_rob["response_model"]["frames"]["payload_offset"] == 4
              and hybrid_rob["response_model"]["record"]["payload_offset"] == 6)
        check("universal Hybrid direct Active Test exports exact live runtime-length probe",
              hybrid_test["name"] == "Activate the Inverter Water Pump"
              and hybrid_test["runtime_length_probe"]["kind"] == "read_data_by_identifier_value_length"
              and hybrid_test["runtime_length_probe"]["selector"] == "0xCA"
              and [frame["materialized_request"] for frame in hybrid_test["runtime_length_probe"]["frames"]] == ["222801"]
              and [frame["positive_check"] for frame in hybrid_test["runtime_length_probe"]["frames"]] == ["62"]
              and hybrid_test["runtime_length_probe"]["response_prefix_length"] == 3)

        na = index["regions"]["NA"]
        camry = na["vehicles"]["12704"]
        check("Camry HV remains one Toyota DB vehicle",
              camry["name"] == "Camry HV"
              and camry["install_set_ids"] == [8119, 8120, 8121, 27706])
        four_runner = na["vehicles"]["12757"]
        check("non-Camry vehicle is represented by the same resolver",
              four_runner["name"] == "4Runner" and bool(four_runner["install_set_ids"]))

        def vehicle_candidates(vehicle: dict[str, object]) -> list[dict[str, object]]:
            rows: list[dict[str, object]] = []
            seen: set[tuple[int, int, str | None]] = set()
            for install_set_id in vehicle["install_set_ids"]:
                for row in na["install_sets"].get(str(install_set_id), []):
                    identity = (int(row["category_id"]), int(row["connection_route_selector"]), row.get("route_key"))
                    if identity not in seen:
                        seen.add(identity)
                        rows.append(row)
            return rows

        camry_candidates = vehicle_candidates(camry)
        four_runner_candidates = vehicle_candidates(four_runner)
        check("Camry resolver preserves all 34 logical candidates and routes",
              len(camry_candidates) == 34
              and all(row.get("route_key") is not None for row in camry_candidates))
        check("4Runner resolves independently to all 35 routes",
              len(four_runner_candidates) == 35
              and all(row.get("route_key") is not None for row in four_runner_candidates))

        p4 = na["vehicle_decision"]["probe_program"]["phase4"]
        p4_programs = list(p4["programs_by_k1"].values())
        check("P4 vehicle decision exports Toyota's complete 0x28..0x39 special-master program",
              bool(p4_programs)
              and all(sorted(step["selector"] for step in program["steps"]) == list(range(0x28, 0x3A))
                      for program in p4_programs))

    with tempfile.TemporaryDirectory() as tmp:
        regenerated_path = Path(tmp) / "toyota_diag_bundle_current"
        write_toyota_diag_bundle(gts, regenerated_path)
        tracked_files = {path.relative_to(ART) for path in ART.rglob("*") if path.is_file()}
        regenerated_files = {path.relative_to(regenerated_path) for path in regenerated_path.rglob("*") if path.is_file()}
        check("universal canonical bundle regenerates byte-for-byte deterministically",
              tracked_files == regenerated_files
              and all(hashlib.sha256((ART / path).read_bytes()).digest()
                      == hashlib.sha256((regenerated_path / path).read_bytes()).digest()
                      for path in tracked_files))
        portable = Path(tmp) / "toyota_diag_bundle_current.zip"
        archive.export_zip(portable)
        archive.compare_zip(portable)
        check("portable export restores every universal bundle member byte-for-byte", True)

    print(f"\n{passed} passed, {failed} failed")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
