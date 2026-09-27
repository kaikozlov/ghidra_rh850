"""Verify the universal clean Toyota diagnostic bundle derived from current GTS+."""
from __future__ import annotations

import hashlib
import json
import os
import tempfile
import zipfile
from pathlib import Path

from tools import REPO_ROOT
REPO = REPO_ROOT

from tools.techstream import techstream_paths
from tools.techstream.gts.bundle import write_toyota_diag_bundle

ART = REPO / "data/generated/gtsplus_2026/toyota_diag_bundle_current.zip"

passed = failed = 0


def check(name: str, condition: object) -> None:
    global passed, failed
    ok = bool(condition)
    passed += int(ok)
    failed += int(not ok)
    print(f"[{'PASS' if ok else 'FAIL'}] {name}")


def main() -> int:
    with zipfile.ZipFile(ART) as archive:
        check("bundle ZIP has no corrupt members", archive.testzip() is None)
        index = json.loads(archive.read("index.json"))

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
              and p6_contract["routine_root"]["selector_excluded"] == ["0xD1F0", "0xD1FE"]
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
              and p5_customize["target_phase_type"] == 0x22
              and [p5_customize["write_bit_start"], p5_customize["write_bit_end"]] == [0, 7]
              and p5_customize["merge_mode"] == 0
              and p5_customize["modern_executor"]["family"] == "p5"
              and p6_customize["name"] == "Wireless Remote Control Setting"
              and p6_customize["write_did"] == 0x225A
              and p6_customize["target_phase_type"] == 0x18
              and p6_customize["modern_executor"]["family"] == "p6")

        for region in ("NA", "EU", "JP"):
            regional = index["regions"][region]
            categories = regional["categories"]
            check(f"{region} P6 Engine is classified by Toyota plugin dispatch, not projected into P5",
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
            check(f"{region} P6 phase 0x18 selects Toyota 29-bit ISO15765 normal-fixed",
                  p6_route["transport_kind"] == "iso15765-29bit-normal-fixed"
                  and p6_route["controller"] == "CCommCtrlISO15765_29BitCan"
                  and p6_route["request_address_field"] == 0x00
                  and p6_route["physical_request_address"] == 0x18DA00F1
                  and p6_route["physical_response_address"] == 0x18DAF100
                  and p6_route["functional_request_address"] == 0x18DB33F1)

            dispatch = regional["vehicle_resolver_dispatch"]
            check(f"{region} VIN10 generation dispatch is exact and 5..19 are an unresolved alternate path, not unsupported",
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
              and p6_simple["start_static"] == "3101da03"
              and p6_simple["stop_static"] == "3102da03"
              and p6_simple["result_static"] == "3103da03"
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
              and engine_simple["start_static"] == "31011187"
              and engine_simple["stop_static"] == "31021187"
              and engine_simple["result_static"] == "31031187"
              and engine_simple["timer_ms"] == 180000
              and engine_simple["check_interval_ms"] == 200
              and engine_simple["support_gate"]["mode"] == "p5-standard"
              and engine_simple["execution"] == "plan_only")
        engine_static_routine = next(row for row in engine_catalog["active_tests"] if row["id"] == 40402)
        check("universal Engine catalog grades static routine-command bytes as executable",
              engine_static_routine["start_static"] == "3101113600"
              and engine_static_routine["routine_command"]["bytes"] == "00"
              and engine_static_routine["fixed_request"] is True
              and engine_static_routine["execution"] == "executable")
        hybrid_engineering = next(row for row in hybrid_catalog["active_tests"] if row["id"] == 1)
        check("universal Hybrid direct Active Test carries clean role-0x70 engineering metadata",
              hybrid_engineering["signal_info"]["physical"]["decimal_point_count"] == 0
              and hybrid_engineering["signal_info"]["choices"] == [{"value": 1, "text": "ON"}]
              and hybrid_engineering["signal_info"]["engineering_to_raw"]["source"].endswith("CStartActTstSnd::SetValue"))
        hybrid_test = next(row for row in hybrid_catalog["active_tests"] if row["id"] == 1)
        hybrid_ffd = next(row for row in hybrid_catalog["commands"] if row["kind"] == "p5_dtc_snapshot")
        check("universal Hybrid catalog exports generic P5 DTC snapshot request",
              hybrid_ffd["role"] == 0xB5
              and hybrid_ffd["plugin_binding"]["binding_category_id"] == 0
              and hybrid_ffd["plugin_binding"]["dll"] == "GetEachFrzFrmDatP5_DT.dll"
              and hybrid_ffd["requests"][0]["send"] == "1904000000ff"
              and hybrid_ffd["requests"][0]["check"] == "5904")
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
        check("universal Hybrid catalog exports exact P5 RoB inventory/frame/record triplets",
              hybrid_rob["role"] == 0xA0
              and hybrid_rob["plugin_binding"]["binding_category_id"] == 397
              and hybrid_rob["plugin_binding"]["exact_category_binding"] is True
              and [[phase["send"] for phase in (protocol["inventory"], protocol["frames"], protocol["record"])]
                   for protocol in hybrid_rob["protocols"]] == [
                      ["ab01", "ab020000", "ab0300000000"],
                      ["ab11", "ab120000", "ab1300000000"],
                   ]
              and hybrid_rob["response_model"]["frames"]["payload_offset"] == 4
              and hybrid_rob["response_model"]["record"]["payload_offset"] == 6)
        check("universal Hybrid direct Active Test exports exact live runtime-length probe",
              hybrid_test["name"] == "Activate the Inverter Water Pump"
              and hybrid_test["runtime_length_probe"]["kind"] == "read_data_by_identifier_value_length"
              and hybrid_test["runtime_length_probe"]["selector"] == "0xCA"
              and hybrid_test["runtime_length_probe"]["request"] == "222801"
              and hybrid_test["runtime_length_probe"]["check"] == "62"
              and hybrid_test["runtime_length_probe"]["response_prefix_length"] == 3)

        na = index["regions"]["NA"]
        camry = na["vehicles"]["12704"]
        check("Camry HV remains one Toyota DB vehicle, not the bundle profile",
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
                    identity = (int(row["category_id"]), int(row["connection_phase_type"]), row.get("route_key"))
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

    actual_sha = hashlib.sha256(ART.read_bytes()).hexdigest()
    with tempfile.TemporaryDirectory() as tmp:
        regenerated_path = Path(tmp) / "toyota_diag_bundle_current.zip"
        gts = techstream_paths.resolve_gts_root(os.environ.get("GTSPLUS_ROOT"))
        write_toyota_diag_bundle(gts, regenerated_path)
        regenerated_sha = hashlib.sha256(regenerated_path.read_bytes()).hexdigest()
        check("universal bundle regenerates byte-for-byte deterministically", actual_sha == regenerated_sha)

    print(f"\n{passed} passed, {failed} failed")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
