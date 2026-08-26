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
DOC = (REPO / "docs/architecture/toyota-openpilot-porting-contract.md").read_text()
FINDINGS = (REPO / "docs/status/FINDINGS.md").read_text()
PRIORITIES = (REPO / "docs/status/PRIORITIES.md").read_text()
QUESTIONS = (REPO / "docs/status/OPEN_QUESTIONS.md").read_text()

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
    proc = subprocess.run([sys.executable, str(REPO / "tools/build_corolla_tss3_opendbc_readiness.py"), "--output", str(out)], cwd=REPO, capture_output=True, text=True, check=False)
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

print("\n== role-level implementation readiness ==")
roles = {r["role"]: r for r in ART["role_readiness"]}
expected_status = {
    "SecOC synchronization": "reusable_security_plumbing",
    "vehicle speed / wheel validity": "strong_reuse_candidate",
    "brake pressed": "strong_reuse_candidate",
    "gas pressed": "strong_reuse_candidate",
    "cruise engaged": "wire_reuse_dynamic_semantics_open",
    "steering angle / rate": "reusable_signal_layout_new_fd_pdu",
    "driver steering torque / actuator response": "driver_torque_closed_actuator_response_static",
    "EPS readiness / steering faults": "generation_native_replacement_open_dynamic_join",
    "gear": "strong_reuse_candidate_partial_dynamic",
    "cruise availability / set speed / ACC faults / follow distance": "diagnostic_oracles_closed_wire_mapping_open",
    "radar / object state": "new_tss3_parser_required",
    "longitudinal command / stock ACC ownership": "open_separate_architecture",
}
for role, status in expected_status.items():
    check(f"{role} disposition", roles[role]["status"] == status)
check("old 0x260 fault/torque interface is not transplanted", "0x260 is absent" in roles["driver steering torque / actuator response"]["tss3_corolla_evidence"])
check("driver torque is physically closed on live 0x030", all(x in roles["driver steering torque / actuator response"]["tss3_corolla_evidence"] for x in ("signals10+31", "-8.23", "+2.85", "0.1 N.m/count", "-0.01 A/count")))
check("driver override is reclassified as Panda policy while Q-current response remains dynamic", all(x in roles["driver steering torque / actuator response"]["remaining_blocker"] for x in ("Panda/openpilot driver-override policy", "0x4A3 Q-current")))
check("fault readiness role carries exact new closures", all(x in roles["EPS readiness / steering faults"]["tss3_corolla_evidence"] for x in ("B6[2]", "6000/6000", "C159B49", "force-7 override", "17-state", "deepest recovered clear/normal classifier path", "0x51E B0[7]", "0x1033 Ready Status", "Ready=1")))
check("old 0x262 fault enums stay nonportable", "Old numeric fault enums" in roles["EPS readiness / steering faults"]["remaining_blocker"])
check("gear reuse is bounded to raw3 plus prior-art-D compatibility", all(x in roles["gear"]["tss3_corolla_evidence"] for x in ("3,662", "checksum", "raw value 3", "prior-art GEAR enum", "MOCK", "does not consume the legacy B5[3:0]")) and all(x in roles["gear"]["remaining_blocker"] for x in ("independent gear-state oracle", "P/R/N/B", "exact target")))
check("cruise role has exact P5 Data-ID oracles but no CAN join", all(x in roles["cruise availability / set speed / ACC faults / follow distance"]["tss3_corolla_evidence"] for x in ("0x1905", "0x1906", "0x1914", "0x1901", "0x1912", "not automatically direct UDS RDBI DIDs")) and "Techstream/GTS+" in roles["cruise availability / set speed / ACC faults / follow distance"]["remaining_blocker"])
check("lateral receiver/replacement freshness closed while signer/topology remain open", roles["lateral command"]["status"] == "eps_receiver_and_replacement_freshness_closed_signer_runtime_open" and all(x in roles["lateral command"]["tss3_corolla_evidence"] for x in ("35 ms", "minimal ID11", "replacement freshness")) and all(x in roles["lateral command"]["remaining_blocker"] for x in ("slot-4 signing", "command-5 runtime carrier", "stock sender cadence", "stock source")))

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
check("current Panda assumption is bus0", "logical bus 0" in bus["current_toyota_safety_assumption"])
check("route reusable state is observed on bus1", "logical bus 1" in bus["public_route_observation"])
check("Toyota-B relay topology is explicit", all(x in bus["toyota_b_harness_fact"] for x in ("CAN0/CAN2", "intercept-relay", "CAN1", "unsplit")))
span_bus = bus["span_moving_observation"]
check("Span rlog stayed direct normal-harness observation", span_bus["panda_state_samples"] == 599 and span_bus["all_samples_elm327_param1"] is True and span_bus["all_samples_harness_status_flipped"] is True)
check("Panda flipped is not physical repin", all(x in bus["toyota_b_harness_fact"] for x in ("CAN0/CAN2", "CAN1", "harnessStatus=flipped", "not a physical")))
check("direct observation is distinct from interception", all(x in bus["diagnostic_vs_interception"] for x in ("ELM327 param=1", "logical bus 1", "normal harness CAN1", "physical CAN0/CAN1 repin", "relay pair")))
check("missing physical repin limits suppression, not passive visibility", all(x in bus["consequence"] for x in ("missing physical repin", "suppression topology", "does not by itself", "B6", "bounded observation")))
impl = ART["implementation_readiness"]
check("TSS3 scaffold requires separate control-generation axis", any("TSS3 control-generation axis" in x and "SECOC" in x for x in impl["can_scaffold_now"]))
check("production lateral requires firmware identity plus relay-correct LTA transition", any(all(tok in x for tok in ("Firmware-identified", "physically relay-correct", "LTA", "off -> active -> off")) for x in impl["blocks_production_lateral"]))
check("production lateral now blocks on signer/runtime and policy validation, not receiver freshness/OEM torque recovery", any("slot-4 signing path" in x and "command-5 carrier" in x for x in impl["blocks_production_lateral"]) and any("No Toyota EPS physical-driver-torque comparator remains" in x for x in impl["blocks_production_lateral"]))
check("normal CarState blocker narrows gear to enum transitions", any("P/R/N/B" in x and "0x127" in x for x in impl["blocks_normal_carstate"]) and any("Cruise CAN-field mapping" in x and "FRC_P5 Data-ID" in x for x in impl["blocks_normal_carstate"]))
check("read-only scaffold can expose Ready without inventing policy", any("0x51E B0[7]" in x and "read-only observation" in x for x in impl["can_scaffold_now"]))
check("radar requires new FD semantics", any("0x123/16" in x for x in impl["blocks_radar"]))
check("longitudinal remains OQ-052", any("OQ-052" in x for x in impl["blocks_longitudinal"]))

print("\n== documentation integration ==")
for token in ("TSS generation", "SecOC/TSK", "corolla_tss3_opendbc_readiness.json", "0x123/16", "0x18A", "canValid=false", "0x127", "ELM327 param=1", "physical CAN0/CAN1"):
    check(f"canonical report records {token}", token in DOC)
check("COM-013 records readiness finding", "| COM-013 |" in FINDINGS and "corolla_tss3_opendbc_readiness.json" in FINDINGS)
check("priority queue consumes readiness artifact", "corolla_tss3_opendbc_readiness.json" in PRIORITIES)
check("OQ-030 consumes readiness artifact", "corolla_tss3_opendbc_readiness.json" in QUESTIONS)

print(f"\n== RESULT: {passed} passed, {failed} failed ==")
raise SystemExit(1 if failed else 0)
