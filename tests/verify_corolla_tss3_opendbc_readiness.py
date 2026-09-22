#!/usr/bin/env python3
"""Verify the generated Corolla TSS3/opendbc implementation-readiness model."""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
ART_PATH = REPO / "data/generated/corolla_tss3_opendbc_readiness.json"
ART = json.loads(ART_PATH.read_text())

passed = failed = 0

def check(name: str, condition: object, detail: str = "") -> None:
    global passed, failed
    ok = bool(condition); passed += int(ok); failed += int(not ok)
    suffix = f" ({detail})" if detail else ""
    print(f"[{'PASS' if ok else 'FAIL'}][generated_self_check] {name}{suffix}")

print("== reproducibility ==")
check("schema is v1", ART["schema"] == "corolla-tss3-opendbc-readiness-v1")
with tempfile.TemporaryDirectory(prefix="tss3-opendbc-") as td:
    out = Path(td) / "readiness.json"
    proc = subprocess.run([sys.executable, str(REPO / "tools/targets/corolla/builders/build_corolla_tss3_opendbc_readiness.py"), "--output", str(out)], cwd=REPO, capture_output=True, text=True, check=False)
    check("builder succeeds", proc.returncode == 0, proc.stderr.strip()[:200])
    if out.exists():
        check("tracked artifact is generator-drift free", json.loads(out.read_text()) == ART)

print("\n== orthogonal architecture axes ==")
axes = ART["axes"]
check("TSS axis is ADAS/control", "ADAS/control" in axes["adas_control_generation"])
check("SecOC/TSK axis is security/authentication", "security/authentication" in axes["security_architecture"])
check("SecOC does not imply TSS generation", all(x in axes["orthogonality"] for x in ("independent", "SecOC/TSK", "does not establish")))
check("current upstream Toyota prior art was checked", ART["upstream_prior_art"]["current_upstream_checked_commit"] == "7343a66d46213d5f73528afc6c6db713ebd88a9d")

print("\n== specimen discipline ==")
spec = ART["specimen_boundaries"]
check("H/F application identity is exact", spec["h_f_application_contract_same"] is True)
check("exact H Tx set is pinned", spec["exact_h_tx_pdus"] == [["0x030", 32], ["0x351", 4], ["0x394", 3], ["0x4A3", 8], ["0x4C8", 8]])
check("exact H SecOC Rx set is pinned", spec["exact_h_secoc_rx_pdus"] == [["0x00F", 8], ["0x0D7", 32], ["0x0B6", 32]])
vis = spec["public_route_vs_exact_h_f_visibility"]
check("route sees sync/D7 but not B6", vis["secoc_rx_observed_counts"] == {"0x00F/8": 588, "0x0B6/32": 0, "0x0D7/32": 2943})
check("route sees only 0x030 of H/F exact Tx set", vis["tx_observed_counts"] == {"0x030/32": 5888, "0x351/4": 0, "0x394/3": 0, "0x4A3/8": 0, "0x4C8/8": 0})
join30 = spec["public_route_0x030_exact_h_f_rule_join"]
check("route 0x030 matches exact H/F additive rule on all frames", join30["frame_count"] == join30["rule_matches"] == 5888 and join30["exact_h_f_additive_rule"]["wire_byte"] == 7)
check("0x030 rule join does not promote route identity", "not an exact firmware/vehicle identity" in join30["boundary"])
check("public route is not merged with H/F", all(x in spec["critical_warning"] for x in ("Do not attribute", "no carFw", "not evidence of a complete")))
span_spec = spec["span_moving_rlog"]
check("Span moving rlog is contributor-attributed, not exact F identity", span_spec["identity_boundary"]["rlog_has_no_usable_f181_join"] is True and span_spec["identity_boundary"]["same_dongle"] is False)
check("Span moving rlog encodes unswapped observation boundary", span_spec["harness_observation_boundary"]["all_samples_elm327_param1"] is True and "had not physically swapped" in span_spec["harness_observation_boundary"]["field_context"])
native_acc = span_spec["native_acc_gate"]
check("Span retained rlog closes native 0x08A ACC gate", native_acc["acc_engaged_frames"] == 37 and native_acc["acc_disengaged_frames"] == 2363 and native_acc["state_when_engaged"] == [93] and native_acc["state_when_disengaged"] == [18])
public_gear = spec["public_route_gear"]
check("public route closes 0x3BF P/R/D transitions", public_gear["0x3BF"]["direct_observed_labels"] == {"0x10": "D", "0x40": "R", "0x80": "P"} and [x["raw"] for x in public_gear["0x3BF"]["transitions"]] == [128, 64, 16])
check("public 0x2A1 independently corroborates P/R/D", public_gear["0x2A1"]["direct_observed_labels"] == {"0x01": "P", "0x02": "R", "0x04": "D"} and [x["raw"] for x in public_gear["0x2A1"]["transitions"]] == [1, 2, 4])
check("GTS+ P5 hybrid preserves P/R/N/D/B ordering", spec["gts_p5_hybrid_shift_position"] == {"source": "HV_P5.ddb", "name": "Shift Position", "pattern_display": {"0": "P", "2": "R", "4": "N", "6": "D", "8": "B"}})
check("retained Albino evidence is longitudinal-only bounded", spec["retained_albino_longitudinal"]["validated_status"].endswith("VALIDATED on car") and all(x in spec["retained_albino_longitudinal"]["boundary"] for x in ("longitudinal", "lateral remained IN PROGRESS", "not evidence")))

print("\n== role-level implementation readiness ==")
roles = {r["role"]: r for r in ART["role_readiness"]}
expected_status = {
    "SecOC synchronization": "reusable_security_plumbing",
    "vehicle speed / wheel validity": "strong_reuse_candidate",
    "brake pressed": "strong_reuse_candidate",
    "gas pressed": "strong_reuse_candidate",
    "cruise engaged": "generation_native_can_closed",
    "steering angle / rate": "reusable_signal_layout_new_fd_pdu",
    "driver steering torque / actuator response": "driver_torque_closed_actuator_response_static",
    "EPS readiness / steering faults": "generation_native_replacement_open_dynamic_join",
    "gear": "generation_native_carstate_closed",
    "cruise availability / set speed / ACC faults / follow distance": "core_carstate_closed_optional_acc_ui_open",
    "radar / object state": "optional_parser_not_required_for_base_port",
    "longitudinal command / stock ACC ownership": "stock_owned_shared_08a_request_plane_source_ownership_open",
}
for role, status in expected_status.items():
    check(f"{role} disposition", roles[role]["status"] == status)
check("old 0x260 fault/torque interface is not transplanted", "0x260 is absent" in roles["driver steering torque / actuator response"]["tss3_corolla_evidence"])
check("driver torque is physically closed on live 0x030", all(x in roles["driver steering torque / actuator response"]["tss3_corolla_evidence"] for x in ("signals10+31", "-8.23", "+2.85", "0.1 N.m/count", "-0.01 A/count")))
check("driver override is reclassified as Panda policy while Q-current response remains dynamic", all(x in roles["driver steering torque / actuator response"]["remaining_blocker"] for x in ("Panda/openpilot driver-override policy", "0x4A3 Q-current")))
check("fault readiness role carries exact new closures", all(x in roles["EPS readiness / steering faults"]["tss3_corolla_evidence"] for x in ("B6[2]", "6000/6000", "Q Axis", "calibration-disabled", "C159B49", "24-record aggregate", "242 populated-class DEM events", "class 0x02 -> states 6/7", "200/600-count", "0x51E B0[7]", "0x1033 Ready Status", "Ready=1", "power-supply receive-validity/freeze gate", "distinct from B6 loss", "B6[3]/B10[3]/B13[4]", "cannot represent exact cooperative authority")))
check("old 0x262 fault enums stay nonportable", "Old numeric fault enums" in roles["EPS readiness / steering faults"]["remaining_blocker"])
check("gear core state is closed from direct transitions plus GTS ordering", all(x in roles["gear"]["tss3_corolla_evidence"] for x in ("0x3BF", "0x80=P", "0x40=R", "0x10=D", "0x2A1", "0x127", "GTS+ HV_P5")) and "No core gear-state blocker" in roles["gear"]["remaining_blocker"])
check("native ACC engagement is closed on 0x08A", all(x in roles["cruise engaged"]["tss3_corolla_evidence"] for x in ("0x08A", "B22 bit 0x10", "2,363", "37", "0x12", "0x5D")) and "No core CarState engagement-field blocker" in roles["cruise engaged"]["remaining_blocker"])
check("core cruise state is closed while optional UI fields remain open", all(x in roles["cruise availability / set speed / ACC faults / follow distance"]["tss3_corolla_evidence"] for x in ("ACC_STATE", "B22 bit0x10", "0x67", "0x251", "19-mph", "0x1901", "0x1905", "0x1906", "0x1912", "0x1914")) and all(x in roles["cruise availability / set speed / ACC faults / follow distance"]["remaining_blocker"] for x in ("Optional follow-distance", "not required")))
check("longitudinal stays stock-owned on the shared 0x08A request plane",
      all(x in roles["longitudinal command / stock ACC ownership"]["tss3_corolla_evidence"] for x in ("0x08A", "ID17/allocation3", "ID23/allocation1", "-0.387", "+0.082", "0x160", "not qualified")) and
      all(x in roles["longitudinal command / stock ACC ownership"]["remaining_blocker"] for x in ("stock longitudinal", "0x08A", "source-suppression", "PCS/AEB", "Do not revive")))
check("native radar parser is optional for base port", roles["radar / object state"]["status"] == "optional_parser_not_required_for_base_port" and "radarUnavailable/model-lead" in roles["radar / object state"]["remaining_blocker"])
check("lateral receiver/replacement freshness closed while signer/topology remain open", roles["lateral command"]["status"] == "eps_receiver_replacement_freshness_and_static_carrier_closed_live_signer_open" and all(x in roles["lateral command"]["tss3_corolla_evidence"] for x in ("35 ms", "minimal ID11", "replacement freshness")) and all(x in roles["lateral command"]["remaining_blocker"] for x in ("slot-4 signing", "live-validate", "inert canary", "stock sender cadence", "stock source")))

print("\n== cross-year TSS3 FD network ==")
fd = ART["tss3_fd_network"]
span = fd["span_2025_static"]
span_move = fd["span_2025_moving_discord_rlog"]
check("Span source ZIP is exact tracked archive", span["source_zip"]["sha256"] == "a5744b4c4627d3e5c20d590bb882d25b9b40c0679cbc3e9660140c7f2ef5262b")
check("Span capture member identity is pinned", span["member"] == {"line_count": 75192, "path": "tsk/uds-sweep/ready_capture.ndjson", "sha256": "182ae388d292d38edea892ce02565f51ac1c36453aae5c302d8e32c1abcd0ae9", "size": 11981966})
check("Span mode label is not trusted", all(x in span["capture_mode_boundary"] for x in ("probably", "Not Ready to Drive", "not active-LTA")))
check("Span static bus0/bus2 ID/DLC sets are equal", span["bus0_bus2_same_id_dlc_set"] is True)
check("Span static bus0/bus2 payload sequences are byte-identical", span["bus0_bus2_payload_sequences_equal"] is True and all(x["payload_sequence_equal"] for x in span["bus0_bus2_equality_by_id"]))
check("2023 and static Span share exact 22-ID/DLC baseline", fd["cross_year_same_bus0_id_dlc_set"] is True and fd["cross_year_public_bus0_equals_span_bus2_id_dlc_set"] is True and len(fd["cross_year_id_dlc_set"]) == 22)
check("moving Span independently preserves exact 22-ID/DLC baseline", fd["moving_span_matches_public_bus0_id_dlc_set"] is True and fd["moving_span_bus0_bus2_same_id_dlc_set"] is True and span_move["bus0_bus2_same_id_dlc_set"] is True and span_move["bus0_bus2_payload_sequences_equal"] is True)
check("moving evidence upgrades geometry, not semantics", all(x in fd["interpretation"] for x in ("moving/driving", "does not assign field semantics", "producer ownership")))
overlap = fd["tss2_radar_track_namespace_overlap"]
check("13 TSS3 FD PDUs overlap older TSS2 radar-track namespace", overlap["upstream_ranges"] == ["0x180..0x18F", "0x190..0x19F"] and overlap["matching_count"] == 13 and [x["can_id"] for x in overlap["matching_tss3_bus0_pdus"]] == [f"0x{x:03X}" for x in range(0x180, 0x18D)])
check("radar namespace overlap remains a search prior only", all(x in overlap["boundary"] for x in ("generation-broken", "search prior", "not a semantic assignment")))
check("0x18A has competing radar/object and lateral hypotheses", all(x in fd["0x18A_disposition"] for x in ("one 64-byte", "radar-track namespace", "competing", "neither interpretation")))

print("\n== Panda/harness and implementation boundaries ==")
bus = ART["bus_and_suppression_boundary"]
topo = bus["canonical_deployment_topology"]
check("canonical TSS3 topology is repinned 0/2 with aux bus1", topo["chassis_state_bus"] == 0 and topo["source_frc_bus"] == 2 and topo["aux_radar_bus"] == 1 and "CAN0/CAN2" in topo["description"])
check("runtime topology has no stock-harness fallback", all(x in bus["runtime_topology_policy"] for x in ("provenance only", "does not auto-detect", "parallel logical-bus-1", "repinned 0/2")))
check("current Panda assumption is canonical bus0", "canonical repinned chassis bus 0" in bus["current_toyota_safety_assumption"])
check("raw route provenance remains bus1", all(x in bus["public_route_observation"] for x in ("Historical raw evidence", "logical bus 1", "does not define runtime placement")))
check("Toyota-B relay topology is explicit", all(x in bus["toyota_b_harness_fact"] for x in ("CAN0/CAN2", "intercept-relay", "CAN1", "unsplit")))
span_bus = bus["span_moving_observation"]
check("Span rlog stayed direct normal-harness observation", span_bus["panda_state_samples"] == 599 and span_bus["all_samples_elm327_param1"] is True and span_bus["all_samples_harness_status_flipped"] is True)
check("Panda flipped is not physical repin", all(x in bus["toyota_b_harness_fact"] for x in ("CAN0/CAN2", "CAN1", "harnessStatus=flipped", "not a physical")))
check("historical bus1 observation is distinct from maintained interception", all(x in bus["diagnostic_vs_interception"] for x in ("ELM327 param=1", "logical bus 1", "physical CAN0/CAN1 repin", "CAN0/CAN2 relay pair")))
check("unrepinned Span route is evidence, not supported topology", all(x in bus["consequence"] for x in ("unrepinned bus-1 rlog", "not a supported topology", "canonical repinned 0/2", "bounded historical observation")))
impl = ART["implementation_readiness"]
implemented = impl["implemented_from_retained_evidence"]
check("base state plumbing is implemented from retained evidence", any(all(tok in x for tok in ("0x025/32", "0x030", "0x127", "0x3BF")) for x in implemented))
check("native Corolla cruise state is implemented", any(all(tok in x for tok in ("0x08A", "0x251", "19-mph")) for x in implemented))
check("shared 0x08A longitudinal request plane is implemented stock-owned", any(all(tok in x for tok in ("0x08A", "0x160", "stock longitudinal", "does not synthesize")) for x in implemented))
check("B6 signer host architecture is implemented", any(all(tok in x for tok in ("B6", "target-angle", "Panda angle safety")) for x in implemented))
check("production lateral now blocks on live signer and stock-source proof", any(all(tok in x for tok in ("resident signer/helper", "native B6", "steering response")) for x in impl["blocks_production_lateral"]) and any(all(tok in x for tok in ("stock-LTA", "suppression point")) for x in impl["blocks_production_lateral"]))
check("normal CarState no longer blocks on gear/cruise discovery", all("gear" not in x.lower() and "set speed" not in x.lower() for x in impl["blocks_normal_carstate"]) and any("Ready=0" in x and "temporary/permanent" in x for x in impl["blocks_normal_carstate"]))
check("radar is optional for base model-lead port", any("radarUnavailable/model leads" in x for x in impl["blocks_radar"]))
check("longitudinal remaining blocker is 0x08A source ownership before AEB validation", len(impl["blocks_longitudinal"]) == 1 and all(tok in impl["blocks_longitudinal"][0] for tok in ("0x08A", "source-ownership", "sole emitter", "PCS/AEB", "0x160")))

check("readiness carries power-supply cooperative gate", ART["specimen_boundaries"]["power_supply_cooperative_gate"]["classification"]["distinct_from_b6_loss"].endswith("FEBEADB9 -> FEBEC26D path."))
check("readiness rejects coarse 0x030 authority substitution", ART["specimen_boundaries"]["cooperative_authority_wire_visibility"]["exact_authority_negative"]["exact_wire_visible_cooperative_authority_bit_recovered"] is False)
check("readiness carries 242-event 0x394 fault contract", sum(ART["specimen_boundaries"]["fault_state_contract"]["class_counts"].values()) == 242 and ART["specimen_boundaries"]["fault_state_contract"]["class_to_state"]["0x02"]["states"] == [6,7] and ART["specimen_boundaries"]["fault_state_contract"]["aging"]["class2_class4_secondary_age"] == 600)
check("readiness carries Q-current B6[1] and force7 source contracts", "Q-axis actual-current-derived" in ART["specimen_boundaries"]["remaining_status_contract"]["can_0x030_b6_bit1"]["classification"] and ART["specimen_boundaries"]["remaining_status_contract"]["can_0x351_force7"]["condition"] == "(FEBE65E4 & 0x0003) != 0 AND FEBE7E13 != 0")
check("readiness carries static H/F carrier candidate without live overclaim", ART["specimen_boundaries"]["command5_runtime_carrier"]["static_candidate"]["size"] == 464 and ART["specimen_boundaries"]["command5_runtime_carrier"]["proxy"]["size"] == 462 and ART["specimen_boundaries"]["command5_runtime_carrier"]["canary"]["size"] == 332 and not ART["specimen_boundaries"]["command5_runtime_carrier"]["boundary"]["live_retention_closed"])
direct = ART["specimen_boundaries"]["command5_runtime_carrier"]["direct_canary"]
check("readiness operationalizes exact same-car direct canary", direct["tool"] == "exploit/ephemeral_runtime/corolla_hf_direct_canary.py" and direct["package"]["payload_sha256"] == "313d1bb70fe6147c179e4b5a35e4556e536f062a80d53d85af3d4292b0b29d84" and direct["field_proven_bootstrap"]["did_0203"] == "0000000000" and direct["field_proven_bootstrap"]["post_10f0_ram_substitution_required"] is False and direct["success_gate"]["heartbeat_address"] == "0xFEBFFB80" and direct["success_gate"]["command5_proxy_authorized_by_this_plan"] is False)
direct_cmd5 = ART["specimen_boundaries"]["command5_runtime_carrier"]["direct_command5"]
check("readiness operationalizes guarded exact-H/F command5 second stage", direct_cmd5["tool"] == "exploit/ephemeral_runtime/corolla_hf_direct_command5.py" and direct_cmd5["package"]["payload_sha256"] == "a94979704010758dd09acc0e137977c8eed5003822eababa39eb8a7e5e9d5a58" and direct_cmd5["probe"]["command5"]["input_length"] == 36 and direct_cmd5["live_guards"]["successful_canary_result_required"] and direct_cmd5["live_guards"]["reset_to_stock_confirmation_required"] and direct_cmd5["live_guards"]["steering_can_transmit_used"] is False)
check("highest-value evidence starts with guarded signer validation", "corolla_hf_direct_canary.py" in ART["highest_value_next_evidence"][0] and "selector-4" in ART["highest_value_next_evidence"][0])
check("highest-value evidence includes live B6 and 0x08A ownership closure", any("native authenticated B6" in x and "EPS response" in x for x in ART["highest_value_next_evidence"]) and any("0x08A" in x and "sole qualified request source" in x and "PCS/AEB" in x for x in ART["highest_value_next_evidence"]))
check("radar remains optional future work", any("0x123/0x180-family" in x and "model-lead" in x for x in ART["highest_value_next_evidence"]))

print(f"\n== RESULT: {passed} passed, {failed} failed ==")
raise SystemExit(1 if failed else 0)
