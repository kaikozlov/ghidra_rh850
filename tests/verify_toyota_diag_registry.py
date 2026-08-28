"""Verify the clean derived Toyota diagnostics registry for the maintainer Camry."""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "tools/techstream"))

import gts_cli
from ddb_semantics import decode_p5_signal, extract_msb0, format_p5_decimal, convert_p5_physical

ART = REPO / "data/generated/gtsplus_2026/toyota_diag_registry_camry_2026.json"

passed = failed = 0


def check(name: str, condition: object) -> None:
    global passed, failed
    ok = bool(condition)
    passed += int(ok)
    failed += int(not ok)
    print(f"[{'PASS' if ok else 'FAIL'}][generated_self_check] {name}")


def main() -> int:
    check("registry artifact exists", ART.is_file())
    actual = json.loads(ART.read_text())
    gts = gts_cli._resolve_gts_root(os.environ.get("GTSPLUS_ROOT"))
    regenerated = gts_cli.build_toyota_diag_registry(gts)
    check("registry regenerates exactly from current GTS+ and pinned live evidence", actual == regenerated)

    profile = actual["profile"]
    check("schema and exact Camry profile are pinned",
          actual["schema"] == "toyota-diagnostics-registry-v4"
          and profile["profile"] == "camry-2026-f33"
          and profile["panda_bus"] == 0)
    decoder = actual["decoders"]["p5-linear-msb0-v1"]
    check("registry carries the closed current-P5 value decoder contract",
          decoder["payload_origin"] == "UDS DID value bytes (positive SID/DID echo excluded)"
          and decoder["bit_numbering"] == "msb0"
          and decoder["byte_order"] == "big-endian"
          and decoder["integer_formula"] == "trunc_toward_zero(signed_raw * mul / div) + offset"
          and decoder["pattern_lookup"] == "match converted_integer before decimal rendering")
    check("exact F33 EPS identity guard is pinned",
          profile["identity_guard"] == {
              "ecu": "eps", "did": 0xF181, "contains_ascii": "8965F3307000",
          })
    check("post-repin DTC sweep retains the exact 17 validated addresses",
          [row["address"] for row in profile["ecus"]] == [
              0x700, 0x701, 0x724, 0x7D2, 0x747, 0x745, 0x707, 0x703, 0x7A1,
              0x7B0, 0x750, 0x7B3, 0x7C4, 0x7D1, 0x7D0, 0x792, 0x7A2,
          ])
    functional = profile["dtc_clear"]["functional_obd"]
    check("functional OBD Mode 04 route matches the live-validated Camry clear",
          functional == {
              "request_id": 0x7DF,
              "mode04_request": "0104000000000000",
              "positive_prefix": "0144",
              "expected_responders": [0x7E8, 0x7EA, 0x7EB, 0x7ED, 0x7EE],
          })
    check("core current P5 catalogs are present",
          profile["catalog_category_ids"] == [372, 395, 397, 398, 405, 435, 450, 498])
    source_keys = set(actual["source_identity"])
    check("registry source identities are checkout-independent logical paths",
          "gtsplus/NA/DB/Gen/Toyota.ddb" in source_keys
          and "gtsplus/NA/DB/Gen/M_English.ddb" in source_keys
          and all(not key.startswith("software/Techstream/") for key in source_keys)
          and all("/Users/" not in key for key in source_keys))

    topology = profile["gts_can_topology"]
    placements = topology["placement_variants"][0]["placements"]
    placement_by_domain = {row["ecu_domain"]: row for row in placements}
    check("current GTS Camry-HV CAN topology is a single invariant 18-option placement",
          topology["vehicle_type"] == 12704
          and topology["vehicle_name"] == "Camry HV"
          and topology["can_bus_car_id"] == "0x00A7D910"
          and topology["option_count"] == 18
          and topology["placement_variant_count"] == 1
          and len(topology["placement_variants"][0]["component_groups"]) == 18)
    check("GTS Bus 1 is the Front Camera domain behind Central Gateway",
          placement_by_domain["Front Camera Module"]["bus_name"] == "Bus 1"
          and placement_by_domain["Front Camera Module"]["gateway_names"] == ["Central Gateway"])
    check("GTS Bus 4 carries both EPS and Skid Control behind Central Gateway",
          placement_by_domain["Power Steering (EPS)"]["bus_name"] == "Bus 4"
          and placement_by_domain["Power Steering (EPS)"]["gateway_names"] == ["Central Gateway"]
          and placement_by_domain["Skid Control (ABS/VSC/TRAC)"]["bus_name"] == "Bus 4"
          and placement_by_domain["Skid Control (ABS/VSC/TRAC)"]["gateway_names"] == ["Central Gateway"])
    check("GTS vehicle-bus names remain explicitly separate from Panda logical buses",
          "not Panda logical bus numbers" in topology["namespace_boundary"]
          and "post-repin diagnostics use Panda bus0" in topology["namespace_boundary"])

    ecu_by_key = {row["key"]: row for row in profile["ecus"]}
    eps_identity = ecu_by_key["eps"]["observed_identity"]
    frc_identity = ecu_by_key["frc"]["observed_identity"]
    brake_identity = ecu_by_key["brake"]["observed_identity"]
    check("historical EPS identity is exact without rewriting its pre-repin Panda route",
          eps_identity["f181_software_ids"] == ["8965F3307000", "8A3113303100"]
          and eps_identity["f18c_serial"] == "8965033K9011J2740743"
          and eps_identity["panda_bus_at_observation"] == 1
          and eps_identity["elm327_param"] == 1
          and "current profile diagnostic route is post-repin Panda bus0" in eps_identity["route_note"])
    check("historical FRC identity is exact without rewriting its pre-repin Panda route",
          frc_identity["f181_software_ids"] == ["8646F3315000"]
          and frc_identity["ecu_part_0105"] == "8646C06091"
          and frc_identity["f18c_serial"] == "TN69400026030404235J"
          and frc_identity["panda_bus_at_observation"] == 1
          and "current profile diagnostic route is post-repin Panda bus0" in frc_identity["route_note"])
    check("historical Brake identity is exact without rewriting its pre-repin Panda route",
          brake_identity["f181_software_ids"] == ["F152633K0000"]
          and brake_identity["ecu_part_0105"] == "8954147040"
          and brake_identity["f18c_serial"] == "8954147040CFC1800985"
          and brake_identity["panda_bus_at_observation"] == 1
          and "current profile diagnostic route is post-repin Panda bus0" in brake_identity["route_note"])

    eps_angle = actual["catalogs"]["405"]["dids"]["0x1037"]
    check("EPS steering-angle DID retains exact current scaling",
          len(eps_angle) == 1
          and eps_angle[0]["decoder"] == "p5-linear-msb0-v1"
          and eps_angle[0]["name"] == "Steering Angle"
          and (eps_angle[0]["bit_start"], eps_angle[0]["bit_end"]) == (0, 15)
          and eps_angle[0]["mul"] == 15
          and eps_angle[0]["signed"] is True
          and eps_angle[0]["unit"] == "deg")
    signal_rows = [
        signal
        for catalog in actual["catalogs"].values()
        for signals in catalog["dids"].values()
        for signal in signals
    ]
    check("every shipped current-P5 DID signal explicitly selects the closed decoder",
          signal_rows and all(row["decoder"] == "p5-linear-msb0-v1" for row in signal_rows))
    check("MSB0 extraction crosses bytes exactly",
          extract_msb0(bytes.fromhex("a53c"), 4, 11) == 0x53)
    check("signed conversion truncates division toward zero rather than Python floor",
          convert_p5_physical(0xFF, bit_width=8, signed=True, mul=5, div=2, offset=0) == -2)
    check("decimal presentation retains exact DDB precision",
          format_p5_decimal(-15, 1) == "-1.5" and format_p5_decimal(15, 3) == "0.015")
    eps_decoded = decode_p5_signal(
        bytes.fromhex("0001"),
        bit_start=eps_angle[0]["bit_start"], bit_end=eps_angle[0]["bit_end"],
        mul=eps_angle[0]["mul"], div=eps_angle[0]["div"], offset=eps_angle[0]["offset"],
        signed=eps_angle[0]["signed"], decimal_point_count=eps_angle[0]["decimal_point_count"],
    )
    check("Steering Angle raw 1 deterministically renders as 1.5 deg",
          eps_decoded == {"raw": 1, "converted_integer": 15, "value": "1.5", "pattern": None})

    frc_lta = actual["catalogs"]["498"]["dids"]["0x1601"]
    check("FRC 0x1601 carries the current LTA and Hands-Off state vocabulary",
          [row["name"] for row in frc_lta] == [
              "LTA Switch Condition Flag", "LTA Control Condition",
              "Hands-Off Customize Condition Flag", "Hands-Off Control Condition",
          ]
          and frc_lta[1]["patterns"] == {"0": "LTA Enabled", "1": "LTA Disabled"})
    frc_condition = frc_lta[1]
    frc_decoded = decode_p5_signal(
        bytes.fromhex("00010000"),
        bit_start=frc_condition["bit_start"], bit_end=frc_condition["bit_end"],
        mul=frc_condition["mul"], div=frc_condition["div"], offset=frc_condition["offset"],
        signed=frc_condition["signed"], decimal_point_count=frc_condition["decimal_point_count"],
        patterns={int(key): value for key, value in frc_condition["patterns"].items()},
    )
    check("FRC 0x1601 pattern display matches the converted integer",
          frc_decoded["raw"] == 1 and frc_decoded["converted_integer"] == 1
          and frc_decoded["pattern"] == "LTA Disabled")

    for category in (397, 435, 450, 498):
        dtc = actual["catalogs"][str(category)]["dtcs"].get("C13187", [])
        check(f"category {category} resolves live U0131-87 as missing EPS message",
              len(dtc) == 1 and dtc[0]["code"] == "U013187" and dtc[0]["failure"] == "Missing Message")

    hv_test = next(row for row in actual["catalogs"]["397"]["active_tests"] if row["id"] == 1)
    check("Hybrid Active Test 1 is a closed plan-only 0x2F executor",
          hv_test["name"] == "Activate the Inverter Water Pump"
          and hv_test["service"] == 0x2F
          and hv_test["did"] == 0x2801
          and hv_test["start_prefix"] == "2f280103"
          and hv_test["stop_prefix"] == "2f280100"
          and hv_test["execution"] == "plan_only")

    frc_test = next(row for row in actual["catalogs"]["498"]["active_tests"] if row["id"] == 0xA429)
    check("FRC LTA Steering Vibration is exact fixed RID 0x1588 executable RoutineControl geometry",
          frc_test["name"] == "LTA Steering Vibration"
          and frc_test["routine_id"] == 0x1588
          and frc_test["fixed_request"] is True
          and frc_test["start_static"] == "31011588"
          and frc_test["stop_static"] == "31021588"
          and frc_test["result_static"] == "31031588"
          and frc_test["session_requirement"] == "extended"
          and frc_test["execution"] == "executable")

    active = [row for catalog in actual["catalogs"].values() for row in catalog["active_tests"]]
    check("Active Tests are graded by fixed-geometry sufficiency without guessing",
          sum(row["execution"] == "executable" for row in active) == 41
          and sum(row["execution"] == "plan_only" for row in active) == 361
          and sum(row["execution"] == "unresolved_static_plan" for row in active) == 26
          and all(row["execution"] != "executable" for row in active if row["kind"] == "direct"))
    check("registry contains derived metadata only and forbids execution authorization",
          "no Toyota binaries" in actual["boundary"]
          and "no execution authorization" in actual["boundary"]
          and "no execution authorization" in actual["utilities"]["boundary"])

    # ---- schema v4: execution model, function hierarchy, utilities ----
    hv = actual["catalogs"]["397"]
    check("v3 loader surface is preserved behind the v4 additions",
          all(key in hv for key in ("category", "dids", "dtcs", "active_tests"))
          and hv_test["execution"] == "plan_only"
          and hv_test["start_prefix"] == "2f280103")
    check("initial-read request is materialized per direct Active Test",
          hv_test["initial_read"] == {"mode": 0, "selector": "0xCA", "request": "222801", "check": "62"}
          and hv_test["session_requirement"] == "extended")

    session = profile["session_control"]
    check("session_control carries the runtime current-P5 contract",
          session["generation"] == "current-p5"
          and session["default_session"] == 1
          and session["extended_session"] == 3
          and session["enter_sequence"] == ["1001", "1003"]
          and session["return_default"] == "1001"
          and session["keepalive"] == {
              "kind": "session_did_poll", "did": "0xF186", "request": "22f186",
              "positive_prefix": "62f186", "interval_s": 2.0,
          } | {key: session["keepalive"][key] for key in ("selector", "mask", "check", "meaning", "session_state")})
    check("session-judgment exception stays documentation, not runtime default",
          session["session_judgment_exception"]["runtime_default"] is False
          and session["session_judgment_exception"]["flag"] == "CCommFrameCtrl +0x398"
          and session["wire_proven_categories"] == [397, 435, 498])
    check("every catalog category resolves identical D1/D2/0xDD session frames",
          set(session["per_category"]) == {str(cid) for cid in profile["catalog_category_ids"]}
          and all(row["generation_low5"] == "0x14"
                  and row["default_session"]["send"] == "1001"
                  and row["extended_session"]["send"] == "1003"
                  and row["keepalive"]["send"] == "22f186"
                  and row["keepalive"]["check"] == "62"
                  for row in session["per_category"].values()))

    check("referenced CommSet timeout/retry rows are carried exactly",
          actual["commsets"]["rows"] == {
              "1": {
                  "send_parameter": 1000, "receive_timeout": 1020, "retry_count": 1,
                  "exception_handler_id": 0, "exception_handler_flag": 0,
              }
          }
          and "CheckAndConvertRcvTimeOut" in actual["commsets"]["boundary"])

    hv_selectors = {row["selector"]: row for row in hv["selectors"]}
    check("resolved selector frames include the recovered executor templates",
          len(hv["selectors"]) == 42
          and hv_selectors["0xDD"] == {"selector": "0xDD", "frame": "0x2B55", "comm_set": 1,
                                       "send": "22f186", "mask": "ff", "check": "62"}
          and hv_selectors["0x9D"]["send"] == "2fffff03" and hv_selectors["0x9D"]["check"] == "6f"
          and hv_selectors["0x64"]["send"] == "2fffff00"
          and hv_selectors["0xD5"]["send"] == "3101ffff" and hv_selectors["0xD7"]["check"] == "7103")

    hv_plugins = {row["role"]: row for row in hv["plugins"]}
    check("role bindings carry recovered kinds and fail closed elsewhere",
          hv_plugins[0x19]["dll"] == "DelDiagCodeP4.dll"
          and hv_plugins[0x19]["semantic_kind"] == "dtc_clear"
          and hv_plugins[0x41]["semantic_kind"] == "p5_signal_info"
          and hv_plugins[0x29]["semantic_kind"] is None
          and hv_plugins[0x29]["semantic_status"] == "plugin_semantics_unrecovered_for_identity")
    emps_plugins = {row["role"]: row for row in actual["catalogs"]["405"]["plugins"]}
    check("EMPS binds the exactly-recovered 0x52 CID plugin",
          emps_plugins[0x52]["dll"] == "GetCID_SID22_DT.dll"
          and emps_plugins[0x52]["semantic_kind"] == "generic_cid")

    hv_commands = {row["role"]: row for row in hv["commands"]}
    check("DTC-clear command carries both selector paths with per-request session class",
          hv_commands[0x19]["kind"] == "dtc_clear"
          and hv_commands[0x19]["requests"][0] == {
              "name": "primary", "selector": "0x1", "send": "04", "mask": "", "check": "44",
              "comm_set": 1, "receive_timeout": 1020, "retry_count": 1,
              "session_requirement": "default", "resolved": True,
          }
          and hv_commands[0x19]["requests"][1]["send"] == "14ffffff"
          and hv_commands[0x19]["requests"][1]["session_requirement"] == "extended"
          and hv_commands[0x19]["timer"] == {"timer_id": 1, "delay_ms": 0}
          and len(hv_commands[0x19]["flow"]["fallback_error_codes_when_function_gate_set"]) == 10)
    emps_cid = {row["role"]: row for row in actual["catalogs"]["405"]["commands"]}[0x52]
    check("CID response model is carried where the exact plugin identity is recovered",
          emps_cid["requests"][0]["selector"] == "0xDC"
          and emps_cid["requests"][0]["check"] == "62f181"
          and emps_cid["response_model"]["payload_offset"] == 4
          and emps_cid["response_model"]["record_size"] == 16)

    hv_functions = {row["function_id"]: row for row in hv["functions"]}
    check("supported-function hierarchy joins type-26 functions to type-27 details",
          len(hv["functions"]) == 9
          and sum(len(row["detail_ids"]) for row in hv["functions"]) == 18
          and sorted(hv_functions) == [2, 3, 4, 10, 28, 29, 30, 32, 37]
          and all(row["name"] is None and row["description"] is None for row in hv["functions"])
          and "OEM function names are not" in actual["function_names"])

    hv_data_list = hv["data_list"]
    check("Data List display order is the consumer-pinned monitor sort key",
          hv_data_list["record_counts"] == {"157": 1448, "62": 1464}
          and hv_data_list["row_count"] == 1457
          and hv_data_list["rows"][0] == {"monitor_key": 662, "sort_key": 0, "did": "0x0103",
                                          "bit_start": 8, "bit_end": 31,
                                          "name": "Total Distance Traveled"}
          and [row["sort_key"] for row in hv_data_list["rows"]]
          == sorted(row["sort_key"] for row in hv_data_list["rows"]))

    engine_groups = actual["catalogs"]["372"]["active_test_groups"]
    check("multi-control Active-Test group geometry is carried without manufacturing groups",
          engine_groups["group_count"] == 5 and engine_groups["membership_count"] == 10
          and engine_groups["groups"][0] == {"group_id": 76, "members": [77, 78]}
          and actual["catalogs"]["397"]["active_test_groups"]["group_count"] == 0)

    utilities = actual["utilities"]
    check("utility surface is the recovered generic families only, others absent",
          len(utilities["bindings"]) == 10
          and {row["semantic_kind"] for row in utilities["bindings"]} == {
              "test_present_start", "test_present_stop", "check_mode_frame_get",
              "check_mode_frame_confirm", "active_test_start", "routine_active_test_init",
              "routine_active_test_signal_info", "set_default_session", "move_session_cgwd",
              "single_routine_active_test",
          }
          and {row["role"] for row in utilities["bindings"]}
          == {0x3A, 0x3B, 0x61, 0x62, 0xB0, 0xAE, 0xAF, 0xBF, 0xCA, 0xD4}
          and utilities["routine_control"]["session_requirement"] == "extended"
          and utilities["io_control"]["session_requirement"] == "extended")

    print(f"\n== RESULT: {passed} passed, {failed} failed ==")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
