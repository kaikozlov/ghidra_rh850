#!/usr/bin/env python3
"""Verify the Techstream ↔ Corolla 8965H1202000 steering correlation."""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
ART = REPO / "data/generated/corolla_8965H1202000_techstream_correlations.json"
EVID = REPO / "data/generated/corolla_8965H1202000_techstream_steering_decompiler_evidence.json"
TOOL = REPO / "tools/build_corolla_h_techstream_correlations.py"
RAW = REPO / "community/albinoelephant/raw-20260818/albinoelephant-corolla-2023.20260814-0023/dump_codeflash_00000000_00200000_20260814-025814.bin"
TECHROOT = REPO / "Techstream/unpacked/toyota/Toyota Diagnostics/Techstream"
passed = failed = 0


def check(name: str, cond: object, detail: str = "") -> None:
    global passed, failed
    ok = bool(cond)
    passed += int(ok); failed += int(not ok)
    suffix = f" ({detail})" if detail else ""
    print(f"[{'PASS' if ok else 'FAIL'}][raw_bytes] {name}{suffix}")


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


with tempfile.TemporaryDirectory() as td:
    out = Path(td) / "corolla-techstream.json"
    subprocess.run([sys.executable, str(TOOL), "--out", str(out)], cwd=REPO, check=True,
                   stdout=subprocess.DEVNULL)
    check("tracked Corolla Techstream report regenerates exactly", out.read_bytes() == ART.read_bytes())

d = json.loads(ART.read_text())
e = json.loads(EVID.read_text())
raw = RAW.read_bytes()

print("\n== source identity ==")
check("tracked raw Corolla dump is 2 MiB", len(raw) == 0x200000)
check("report binds raw Corolla dump", sha(raw) == d["sources"]["corolla_codeflash"]["sha256"])
for key, rel in (("na_emps_p5", "NA/DB/EMPS_P5.ddb"), ("na_emps2_p5", "NA/DB/EMPS2_P5.ddb")):
    src = TECHROOT / rel
    check(f"{rel} hash matches pinned semantics", sha(src.read_bytes()) == d["sources"][key]["sha256"])

print("\n== compact target-native evidence ==")
check("40 H functions support the Techstream steering/current/DTC joins", e["function_count"] == 40)
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

print("\n== protected brake-profile field semantics ==")
pb = d["protected_brake_profile_semantics"]
check("D7 configured/scalar split is 240..247 versus 240/243/246", pb["d7"]["configured_signal_ids"] == list(range(240,248)) and [x["signal_id"] for x in pb["d7"]["scalar_calls"]] == [240,243,246])
check("D7 only 16-bit scalar is signal243", [x for x in pb["d7"]["scalar_calls"] if x["bit_length"] == 16] == [{"bit_length":16,"bit_offset_in_byte":0,"packed_bit_offset":384,"signal_id":243}])
check("D7 signal243 is exact DID1185 CAN Vehicle Speed SP1", pb["d7"]["sp1_vehicle_speed"]["signal_id"] == 243 and pb["d7"]["sp1_vehicle_speed"]["primary_data_id"] == "0x1185" and pb["d7"]["sp1_vehicle_speed"]["name"] == "CAN Vehicle Speed (SP1)" and pb["d7"]["sp1_vehicle_speed"]["callback_recovered"])
check("B6 sole 16-bit scalar remains staged-only", pb["b6"]["largest_scalar_signal_id"] == 255 and pb["b6"]["largest_scalar_role"] == "signed16-staged-only-direct-xref-negative")

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
check("protected brake profiles have no recovered steering magnitude", c["protected_brake_profiles_have_no_recovered_steering_magnitude"])
check("camera/IPM-A DTC is asserted disabled", c["camera_ipm_a_dtc_disabled"])
check("Sienna active IPM-A monitor rows are asserted removed", c["sienna_ipm_a_monitor_rows_removed_in_h"])
check("external CAN-field equivalence remains false", c["external_can_field_equivalence"] is False)

print(f"\nResults: {passed} passed, {failed} failed")
raise SystemExit(1 if failed else 0)
