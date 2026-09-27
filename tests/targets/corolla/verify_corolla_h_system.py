#!/usr/bin/env python3
"""Portable Corolla H system pins: orchestration surface and Techstream correlations.

Domain split; assertions and helpers are carried over verbatim.
"""
from __future__ import annotations

import hashlib

from tools import REPO_ROOT
ROOT = REPO = REPO_ROOT
passed = failed = 0

def sha(data):
    return hashlib.sha256(data).hexdigest()

def check(name, cond, detail=''):
    global passed, failed
    ok = bool(cond)
    passed += int(ok)
    failed += int(not ok)
    suffix = f' ({detail})' if detail else ''
    print(f"[{'PASS' if ok else 'FAIL'}][raw_bytes] {name}{suffix}")


def _section_system_orchestration():
    print('== system orchestration ==')
    """Verify target-native Corolla 8965H1202000 system/orchestration recovery."""

    import json

    ROOT = REPO_ROOT
    ART = ROOT / "data/generated/corolla_8965H1202000_system_orchestration.json"
    EVIDENCE = ROOT / "data/generated/corolla_8965H1202000_system_orchestration_decompiler_evidence.json"
    HRAW = ROOT / "community/albinoelephant/raw-20260818/albinoelephant-corolla-2023.20260814-0023/dump_codeflash_00000000_00200000_20260814-025814.bin"


    art = json.loads(ART.read_text())
    ev = json.loads(EVIDENCE.read_text())
    h = HRAW.read_bytes()[:0x100000]

    print("== deterministic artifact ==")
    print("\n== evidence binding ==")
    check("H image hash is pinned", sha(h) == ev["image"]["codeflash_sha256"] == art["images"]["corolla_h_sha256"])
    check("all contiguous H body hashes validate",
          all(sha(h[int(r["entry"],16):int(r["entry"],16)+r["body_size"]]) == r["body_sha256"] for r in ev["functions"]))
    reset = ev["reset_0x1f2"]
    check("reset 0x1F2 is explicitly non-contiguous", reset["entry"] == "0x000001F2" and "non-contiguous" in reset["body_boundary"])
    check("all reset raw windows validate",
          all(sha(h[int(w["start"],16):int(w["start"],16)+w["size"]]) == w["sha256"] for w in reset["raw_windows"]))

    print("\n== scheduler/system closure ==")
    closure = art["scheduler_system_closure"]
    expected = {
        "0x000001F2":"0x000001F2", "0x00058404":"0x0005389C", "0x00062758":"0x0005CAAC",
        "0x000B0518":"0x000B05D0", "0x000B28AC":"0x000B2692", "0x000BA43A":"0x000B8EE4",
        "0x000BD10E":"0x000BBFE6", "0x000BEC4C":"0x000BD954",
    }
    check("all eight scheduler/system residual roles are mapped", art["scheduler_system_closure_count"] == 8 and
          {r["reference_entry"]:r["target_entry"] for r in closure} == expected)
    by_ref = {r["reference_entry"]:r for r in closure}
    check("H periodic generated task remains flat/no-branch", by_ref["0x00058404"]["target_metrics"]["if_count"] == 0 and
          by_ref["0x00058404"]["target_metrics"]["switch_count"] == 0 and
          by_ref["0x00058404"]["target_metrics"]["unique_direct_call_count"] == 333)
    check("H one-shot subsystem init remains no-branch", by_ref["0x000BD10E"]["target_metrics"]["if_count"] == 0 and
          by_ref["0x000BD10E"]["target_metrics"]["unique_direct_call_count"] == 94)
    check("H telemetry snapshot body is target-native 2654 bytes", by_ref["0x000BA43A"]["target_metrics"]["body_size"] == 2654)
    check("H transition phase initializer retains 26-byte/one-call shape", by_ref["0x000B28AC"]["target_metrics"] == {
        "body_size":26,"direct_call_count":1,"unique_direct_call_count":1,"if_count":0,"switch_count":0,"loop_count":0})
    markers = by_ref["0x000001F2"]["target_evidence"]["static_markers"]
    check("H reset decision retains FCU/marker constants and terminal loop", all(markers.values()))

    print("\n== mode coordinator ==")
    mode = art["mode_coordinator"]
    expected_query = [0,9,5,0,1,9,3,0,1,9,6,12,0,1,9,6,11,7,0,1,9,4,7,2,0,9,10,7,14,15,9,2,7,0,13,8,1,9]
    expected_clear = [0,0,1,9,0,1,9,12,0,1,9,6,0,1,9,2,0,9,7,2,15,0,8,1]
    check("mode event-query sequence is exactly preserved", mode["query_sequences_identical"] and mode["event_query_sequence"] == expected_query)
    check("mode event-clear sequence is exactly preserved", mode["clear_sequences_identical"] and mode["event_clear_sequence"] == expected_clear)
    check("mode coordinator keeps 47 branch tests", mode["sienna_metrics"]["if_count"] == mode["h_metrics"]["if_count"] == 47)
    check("mode coordinator body size remains near-identical", mode["sienna_metrics"]["body_size"] == 1014 and mode["h_metrics"]["body_size"] == 1016)

    print("\n== per-tick wiring delta ==")
    tick = art["per_tick_dispatch"]
    check("guard denominator is 74 -> 64", tick["sienna_guard_count"] == 74 and tick["h_guard_count"] == 64)
    check("guard diff is one contiguous 10-guard deletion", len(tick["guard_diff"]) == 1 and
          tick["guard_diff"][0]["opcode"] == "delete" and len(tick["guard_diff"][0]["sienna_guards"]) == 10 and
          tick["guard_diff"][0]["h_guards"] == [])
    check("deleted guard region includes both Sienna 0x520 branches",
          tick["guard_diff"][0]["sienna_guards"].count("if (param_2 == 0x520) {") == 2)
    check("H full dispatcher has no 0x520 guard", tick["sienna_has_0x520_guard"] and not tick["h_has_0x520_guard"])
    check("deleted block includes known Sienna B763C helper", "FUN_000b763c" in tick["sienna_only_post_coordinator_calls"])
    check("H full dispatcher preserves telemetry -> coordinator -> snapshot order",
          tick["h_major_call_order"] == ["FUN_000b8ee4","FUN_000b05d0","FUN_000bba48"] and
          tick["h_major_call_positions"]["FUN_000b8ee4"] <
          tick["h_major_call_positions"]["FUN_000b05d0"] <
          tick["h_major_call_positions"]["FUN_000bba48"])
    reduced = art["reduced_per_tick_companion"]
    check("H reduced/current-mode dispatcher keeps same major trio", reduced["h_calls"] == ["FUN_000b8ee4","FUN_000b05d0","FUN_000bba48"])
    check("reduced dispatcher shrinks 504 -> 460 bytes", reduced["sienna_metrics"]["body_size"] == 504 and reduced["h_metrics"]["body_size"] == 460)

    print("\n== startup / wrappers / regenerated copy surface ==")
    start = art["startup_and_wrappers"]
    check("H startup coordinator enables IRQ", start["startup"]["enables_irq"])
    check("H startup coordinator tail is foreground loop call", start["startup"]["last_explicit_fun_call"] == "FUN_0005f30c")
    check("subsystem-init veneer targets BBFE6", "FUN_000bbfe6();" in start["subsystem_init_wrapper"]["wrapper_code"])
    check("per-tick veneer forwards three args to BD954", "FUN_000bd954(param_1,param_2,param_3);" in start["per_tick_wrapper"]["wrapper_code"])
    check("transition phase init writes shifted FEBEB160-162 state", all(x in start["transition_phase_init"]["code"] for x in ("0xfebeb162","0xfebeb160","0xfebeb161")))
    rte = art["regenerated_com_rte_surface"]
    check("H shared Rx consumer fragment has five recovered generated callers", rte["consumer_fragment_callers_within_evidence"] ==
          ["0x0005389C","0x00058450","0x0005886A","0x000589A8","0x00058B3C"])
    check("H RTE copy banks are split across three pinned wrappers", rte["rte_copy_banks"] == [
        {"target":"0x00056970","wrapper":"0x00052E4C"},
        {"target":"0x0005701E","wrapper":"0x00052EEE"},
        {"target":"0x0005722E","wrapper":"0x00052FEC"},
    ])
    check("static conclusion closes scheduler residue without claiming all COM helpers", art["static_conclusion"]["scheduler_system_residue_closed"] and
          "not every generated COM helper" in art["static_conclusion"]["remaining_boundary"])


def _section_techstream_correlations():
    print('== techstream correlations ==')
    """Verify the Techstream ↔ Corolla 8965H1202000 steering correlation."""

    import json

    REPO = REPO_ROOT
    ART = REPO / "data/generated/corolla_8965H1202000_techstream_correlations.json"
    EVID = REPO / "data/generated/corolla_8965H1202000_techstream_steering_decompiler_evidence.json"
    RAW = REPO / "community/albinoelephant/raw-20260818/albinoelephant-corolla-2023.20260814-0023/dump_codeflash_00000000_00200000_20260814-025814.bin"


    d = json.loads(ART.read_text())
    e = json.loads(EVID.read_text())
    raw = RAW.read_bytes()

    print("\n== source identity ==")
    check("tracked raw Corolla dump is 2 MiB", len(raw) == 0x200000)
    check("report binds raw Corolla dump", sha(raw) == d["sources"]["corolla_codeflash"]["sha256"])
    check(
        "report pins EMPS_P5 external source identity",
        d["sources"]["na_emps_p5"] == {
            "relative_path": "NA/DB/EMPS_P5.ddb",
            "sha256": "1e5ffc4f998570458fa86dd0d563949006f9e0781f15d118d01e80656fadd199",
        },
    )
    check(
        "report pins EMPS2_P5 external source identity",
        d["sources"]["na_emps2_p5"] == {
            "relative_path": "NA/DB/EMPS2_P5.ddb",
            "sha256": "e80d722f3b80077e3f7bdc4b815c2035b21a51cefb6cd26dc6de3ada20939312",
        },
    )

    print("\n== compact target-native evidence ==")
    for row in e["functions"]:
        start = int(row["entry"], 16); size = row["body_size"]
        check(f"raw body hash {row['entry']}", sha(raw[start:start+size]) == row["body_sha256"])

    print("\n== recovered P5 data-ID layout ==")
    for name in ("emps_p5", "emps2_p5"):
        x = d["data_id_layout_recovery"][name]
        check(f"{name} primary data-ID words resolve except sentinel",
              x["primary_nonzero_count"] == x["primary_resolves_in_type61_or_fffe"])
        check(f"{name} alternate data-ID words all resolve",
              x["alternate_nonzero_count"] == x["alternate_resolves_in_type61"])
    check("P5 list host uses support-ID filtering", "CheckSupportPid" in d["data_id_layout_recovery"]["host_consumer"])

    print("\n== Corolla vocabulary fit ==")
    ov = d["ddb_overlap"]
    check("H has 226 readable RDBI DIDs", ov["h_readable_did_count"] == 226)
    check("EMPS_P5 overlaps 124 H DIDs", ov["emps_p5"]["h_type61_overlap_count"] == 124)
    check("EMPS_P5 yields 137 H-supported named monitor rows", ov["emps_p5"]["h_supported_monitor_rows"] == 137)
    check("EMPS2_P5 overlap is smaller", ov["emps2_p5"]["h_type61_overlap_count"] == 112)

    print("\n== Command Value Torque exact join ==")
    t = d["command_value_torque"]
    check("monitor 402 is Command Value Torque in Nm",
          t["techstream"]["monitor_key"] == 402 and t["techstream"]["name"] == "Command Value Torque" and t["techstream"]["unit"] == "Nm")
    check("monitor 402 primary/alternate IDs are 1C02/3C02",
          t["techstream"]["primary_data_id"] == "0x1C02" and t["techstream"]["alternate_data_id"] == "0x3C02")
    check("H DID 1C02 is a live 2-byte callback", t["corolla_h_rdbi"]["callback"] == "0x000495A0" and t["corolla_h_rdbi"]["callback_classification"] == "direct_fixed" and t["corolla_h_rdbi"]["declared_length"] == 2)
    check("H DID 1C02 formula is recovered", t["corolla_h_rdbi"]["formula_recovered"])
    check("all target-native producer-chain relations are recovered", all(x["recovered"] for x in t["target_native_producer_chain"]))
    check("active pipeline order is CD55A -> CD5DC -> CE928",
          t["target_native_producer_chain"][-1]["relation"].endswith("CD55A -> CD5DC -> CE928 in order"))

    print("\n== motor-current bridge ==")
    b = d["motor_current_bridge"]
    mon = b["techstream_monitors"]
    check("Q actual/command and D actual/command monitors are 16-bit amperes",
          all(mon[str(k)]["bit_width"] == 16 and mon[str(k)]["unit"] == "A" for k in (251, 252, 253, 254)))
    check("Q current command is DID 1152", mon["252"]["primary_data_id"] == "0x1152" and mon["252"]["name"] == "Command Value Current (Q Axis)")
    check("D current command is DID 1154", mon["254"]["primary_data_id"] == "0x1154" and mon["254"]["name"] == "Command Value Current 2 (D Axis)")
    check("final Q current limit is DID 1156", mon["256"]["primary_data_id"] == "0x1156" and mon["256"]["name"] == "Final Motor Current Limited (Q Axis)" and mon["256"]["unit"] == "A")
    check("internal command torque has complete static Q-current bridge", all(x["recovered"] for x in b["q_axis_command_chain"]))
    check("Q-current bridge reaches compensated-command minus raw-feedback error stage",
          any(x["entry"] == "0x00032934" and "FEBE6BB8" in x["relation"] and "FEBE6BB4" in x["relation"] for x in b["q_axis_command_chain"]))
    check("Q-current bridge reaches dedicated PI stage",
          any(x["entry"] == "0x000329A0" and "PI" in x["relation"] for x in b["q_axis_command_chain"]))
    check("actual q/d current observers have complete target-native chain", all(x["recovered"] for x in b["q_axis_actual_chain"]))
    check("D-axis current command is recovered as separate motor-internal path", all(x["recovered"] for x in b["d_axis_command_chain"]))
    check("Q-axis current-limit observer chain is complete", all(x["recovered"] for x in b["q_axis_limit_chain"]))
    check("Q command chain explicitly passes through C3D2 -> C3D6 -> C3D4",
          b["q_axis_command_chain"][0]["entry"] == "0x000CD5DC" and b["q_axis_command_chain"][1]["entry"] == "0x000CD644")

    print("\n== steering-state diagnostic bridge ==")
    sb = d["steering_state_bridge_diagnostics"]
    tq = sb["steering_wheel_torque"]
    check("Steering Wheel Torque DID 1035 is signed Nm/3 decimals", tq["primary_data_id"] == "0x1035" and tq["name"] == "Steering Wheel Torque" and tq["signed"] and tq["unit"] == "Nm" and tq["decimal_point_count"] == 3 and tq["mul"] == tq["div"] == 1)
    ready = sb["ready_status_oracle"]
    check("Ready Status DID 1033 is exact boolean diagnostic oracle", ready["primary_data_id"] == "0x1033" and ready["name"] == "Ready Status" and ready["source_chain"] == ["0xFEBE7D1B", "0xFEBEF052", "0xFEBEB5A8", "0xFEBEE811", "DID 0x1033"] and ready["conversion"]["data_range"] == [0, 1])
    elec = sb["0x351_motor_b_terminal_voltage_monitor"]
    check("0x351 electrical monitor joins exact enabled C159B49", elec["dem_event"] == 4 and elec["dtc"]["h_dtc_index"] == 54 and elec["dtc"]["enabled_word"] == 1 and elec["dtc"]["techstream_code"] == "C159B49")
    check("C159B49 carries exact Toyota description/failure", elec["dtc"]["techstream_description"] == 'Power Steering Motor "B" Terminal Voltage Detect Circuit' and elec["dtc"]["techstream_failure"] == "Internal Electronic Failure")
    qactual = b["techstream_monitors"]["251"]
    check("Q actual current conversion is signed A/2 decimals", qactual["primary_data_id"] == "0x1151" and qactual["signed"] and qactual["unit"] == "A" and qactual["decimal_point_count"] == 2 and qactual["mul"] == qactual["div"] == 1)

    print("\n== Techstream surface selection ==")
    ts = d["techstream_surface"]
    check("EMPS_P5 master route is category405 generation20", ts["na_master_category_id"] == 405 and ts["na_master_generation"] == 20)
    check("EMPS_P5 is master-routed in NA/EU/JP while EMPS2_P5 is not", ts["emps_p5_master_routed_regions"] == ["NA","EU","JP"] and ts["emps2_p5_master_route_count"] == 0)
    check("EMPS_P5 parsed section set is P5 monitor/behavior only", ts["section_types"] == [61,62,63,80,87,88,90,91])
    check("no classic type11/12 Active Test table is present", ts["classic_active_test_section_types_present"] == [])
    check("category405 routes no Active Test or Routine-named DLL", ts["active_test_named_dlls"] == [] and ts["routine_named_dlls"] == [])
    check("Cooperation Control State DID106A is a success stub", ts["cooperation_control_state"]["primary_data_id"] == "0x106A" and ts["cooperation_control_state"]["h_callback_classification"] == "success_stub")

    print("\n== communication-monitor DTC join ==")
    cm = d["communication_monitor_dtc"]
    check("communication monitor is a six-row target-native family", cm["row_count"] == 6 and all(cm["target_native_checks"].values()))
    check("six monitor rows resolve to 025/D7/D0/3B0/D5/B6", [x["can_id"] for x in cm["rows"]] == ["0x025","0x0D7","0x0D0","0x3B0","0x0D5","0x0B6"])
    check("D7/D5/B6 share Brake System Control Module missing-message DTC", cm["brake_missing_message_can_ids"] == ["0x0D7","0x0D5","0x0B6"])
    b6 = next(x for x in cm["rows"] if x["can_id"] == "0x0B6")
    check("B6 monitor is row5 slot18 PDU42", b6["row_index"] == 5 and b6["status_slot"] == "0x18" and b6["pdu_id"] == 42)
    check("B6 maps event0143 to H DTC index82 C12987", b6["dem_event"] == "0x0143" and b6["dtc"]["h_dtc_index"] == 82 and b6["dtc"]["packed_dtc"] == "0xC12987")
    check("Techstream names B6 source as brake-system missing message", b6["dtc"]["techstream_code"] == "U012987" and b6["dtc"]["techstream_description"] == "Lost Communication with Brake System Control Module" and b6["dtc"]["techstream_failure"] == "Missing Message")

    print("\n== complete H DEM event-class/DTC catalog ==")
    fc = d["fault_event_class_catalog"]
    check("242 populated-class DEM events are exhaustively classified", sum(fc["class_counts"].values()) == 242 and fc["event_count_scanned"] == 0x180)
    check("exact class histogram is pinned", fc["class_counts"] == {"0x01":8,"0x02":34,"0x04":1,"0x08":1,"0x0F":1,"0x10":173,"0x20":16,"0x40":1,"0x80":7})
    check("class 0x02 mostly carries named DTCs", fc["classes"]["0x02"]["dtc_indexed_count"] == 32)
    check("class 0x10 is the dominant named fault family", fc["classes"]["0x10"]["dtc_indexed_count"] == 169)
    check("class 0x20 has six named DTC events", fc["classes"]["0x20"]["dtc_indexed_count"] == 6)
    check("internal-only classes retain zero-DTC boundary", all(fc["classes"][x]["dtc_indexed_count"] == 0 for x in ("0x04","0x08","0x0F","0x40","0x80")))

    print("\n== protected brake-profile field semantics ==")
    pb = d["protected_brake_profile_semantics"]
    check("D7 configured/scalar split is 240..247 versus 240/243/246", pb["d7"]["configured_signal_ids"] == list(range(240,248)) and [x["signal_id"] for x in pb["d7"]["scalar_calls"]] == [240,243,246])
    check("D7 only 16-bit scalar is signal243", [x for x in pb["d7"]["scalar_calls"] if x["bit_length"] == 16] == [{"bit_length":16,"bit_offset_in_byte":0,"packed_bit_offset":384,"signal_id":243}])
    check("D7 signal243 is exact DID1185 CAN Vehicle Speed SP1", pb["d7"]["sp1_vehicle_speed"]["signal_id"] == 243 and pb["d7"]["sp1_vehicle_speed"]["primary_data_id"] == "0x1185" and pb["d7"]["sp1_vehicle_speed"]["name"] == "CAN Vehicle Speed (SP1)" and pb["d7"]["sp1_vehicle_speed"]["callback_recovered"])
    check("B6 signal255 role is deferred beyond direct-xref Techstream join", pb["b6"]["largest_scalar_signal_id"] == 255 and pb["b6"]["largest_scalar_role"] == "target-native-role-deferred-to-computed-ingress-provenance")

    print("\n== disabled camera/IPM-A diagnostic residue ==")
    ipm = d["camera_ipm_a_residue"]
    check("H retains U023A87 IPM-A DTC at index93 but disables it", ipm["h_dtc_index"] == 93 and ipm["packed_dtc"] == "0xC23A87" and ipm["techstream_code"] == "U023A87" and ipm["h_enabled_word"] == 0)
    check("Techstream names disabled H residue as Image Processing Module A missing message", ipm["techstream_description"] == 'Lost Communication with Image Processing Module "A"' and ipm["techstream_failure"] == "Missing Message")
    check("removed Sienna IPM monitor set is 2E4/131/191/2FD", ipm["removed_sienna_can_ids"] == ["0x131","0x191","0x2E4","0x2FD"])
    check("all four Sienna IPM rows are absent from H active monitor table", len(ipm["sienna_active_ipm_rows"]) == 4 and all(x["sienna_row_event_matches"] and x["corolla_h_event_dtc_index"] == 93 and not x["corolla_h_active_monitor_row_present"] for x in ipm["sienna_active_ipm_rows"]))
    check("legacy B3 event is disconnected from DTC93 in H", ipm["h_event_b3"]["dtc_index"] == 0)

    print("\n== angle-domain negative ==")
    a = d["modern_angle_domain"]
    check("target-angle monitor family is grouped under 1CEE/1CEF", a["primary_data_ids"] == ["0x1CEE", "0x1CEF"])
    check("H supports none of the 2069..2076 target-angle family", not a["corolla_h_supports_any"] and all(not x["corolla_h_rdbi_supported"] for x in a["rows"]))

    print("\n== interpretation boundary ==")
    c = d["static_conclusion"]
    check("exact H Command Value Torque DID join is asserted", c["command_value_torque_exact_did_join"])
    check("live internal H producer pipeline is asserted", c["command_value_torque_live_internal_pipeline"])
    check("command-torque to Q-current static bridge is asserted", c["command_torque_to_q_current_static_bridge"])
    check("q/d actual current observer closure is asserted", c["q_d_actual_current_observers_recovered"])
    check("D-axis command path is asserted separate", c["d_axis_command_path_separate"])
    check("Q-axis limit observer closure is asserted", c["q_axis_limit_observer_recovered"])
    check("classic Active Test surface remains absent", c["classic_active_test_surface_present"] is False)
    check("live Cooperation Control State monitor remains absent", c["live_cooperation_control_state_monitor"] is False)
    check("B6 brake-system DTC join is asserted", c["b6_brake_system_missing_message_dtc_join"])
    check("D7 command-sized scalar is exact vehicle speed", c["d7_command_sized_scalar_is_vehicle_speed"])
    check("B6 signal255 semantics are deferred to target-native provenance", c["b6_signal255_semantics_deferred_to_target_native_provenance"])
    check("camera/IPM-A DTC is asserted disabled", c["camera_ipm_a_dtc_disabled"])
    check("Sienna active IPM-A monitor rows are asserted removed", c["sienna_ipm_a_monitor_rows_removed_in_h"])
    check("external CAN-field equivalence remains false", c["external_can_field_equivalence"] is False)
_section_system_orchestration()
_section_techstream_correlations()
print(f'\nResults: {passed} passed, {failed} failed')
raise SystemExit(1 if failed else 0)
