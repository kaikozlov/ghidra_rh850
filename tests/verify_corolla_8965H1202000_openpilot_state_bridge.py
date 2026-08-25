#!/usr/bin/env python3
"""Verify the H/F Corolla openpilot state-interface bridge."""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
ART = REPO / "data/generated/corolla_8965H1202000_openpilot_state_bridge.json"
EVID = REPO / "data/generated/corolla_8965H1202000_openpilot_state_bridge_decompiler_evidence.json"
FD = REPO / "data/generated/corolla_8965H1202000_fd_control_interface.json"
BUILD = REPO / "tools/build_corolla_h_openpilot_state_bridge.py"
IMAGE = REPO / "community/albinoelephant/normalized/8965H1202000_CodeFlash.bin"
DOC = REPO / "docs/variants/corolla-h-f-openpilot-state-bridge.md"
passed = failed = 0


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def check(name: str, condition: object, detail: str = "") -> None:
    global passed, failed
    ok = bool(condition)
    passed += int(ok)
    failed += int(not ok)
    suffix = f" ({detail})" if detail else ""
    print(f"[{'PASS' if ok else 'FAIL'}][raw_bytes] {name}{suffix}")


art = json.loads(ART.read_text())
evid = json.loads(EVID.read_text())
fd = json.loads(FD.read_text())
image = IMAGE.read_bytes()

print("== deterministic artifacts ==")
with tempfile.TemporaryDirectory() as td:
    out = Path(td) / "bridge.json"
    proc = subprocess.run([sys.executable, str(BUILD), "--out", str(out)], cwd=REPO, capture_output=True, text=True, check=False)
    check("bridge builder succeeds", proc.returncode == 0, proc.stderr[-300:])
    check("bridge artifact regenerates exactly", proc.returncode == 0 and out.read_bytes() == ART.read_bytes())
check("bridge schema v8", art["schema"] == "corolla-8965H1202000-openpilot-state-bridge-v8")
check("compact evidence schema v2", evid["schema"] == "corolla-h-openpilot-state-bridge-decompiler-evidence-v2")
check("exact H image identity", len(image) == 0x100000 and sha(image) == art["images"]["corolla_h"]["sha256"] == evid["image"]["sha256"])
check("H/F application identity carried forward", art["images"]["corolla_f"]["application_byte_identical_to_h"])
check("promoted corpus identity exact", evid["source_corpus"]["sha256"] == "c3411eec57b9d55c004b0b0f328394bb152577c3398084dccc729dab5da54656" and evid["source_corpus"]["function_count"] == 5478)
check("26 compact state functions promoted", evid["function_count"] == 26)
for row in evid["functions"]:
    start = int(row["entry"], 16)
    check(f"raw body {row['entry']}", sha(image[start:start + row["body_size"]]) == row["body_sha256"])

print("\n== exact H Tx carriers ==")
pdus = {x["can_id"]: x for x in art["h_tx_pdu_descriptors"]}
check("new H Tx family exact", list(pdus) == ["0x030", "0x351", "0x394", "0x4A3", "0x4C8"])
check("0x030 is 32-byte PDU0", pdus["0x030"]["pdu"] == 0 and pdus["0x030"]["length"] == 32)
check("0x351 is 4-byte PDU1", pdus["0x351"]["pdu"] == 1 and pdus["0x351"]["length"] == 4)
check("0x394 is 3-byte PDU2", pdus["0x394"]["pdu"] == 2 and pdus["0x394"]["length"] == 3)
check("0x4A3 is 8-byte PDU3", pdus["0x4A3"]["pdu"] == 3 and pdus["0x4A3"]["length"] == 8)

print("\n== 0x4A3 physical state bridge ==")
b = art["state_bridge"]["0x4A3"]
fields = {x["wire"]: x for x in b["fields"]}
check("4A3 driver torque has official physical scale", fields["B5"]["semantic"] == "Steering Wheel Torque" and fields["B5"]["techstream_did"] == "0x1035" and fields["B5"]["unit"] == "Nm" and fields["B5"]["packet_scale"] == 0.1)
check("4A3 Q-current is sign-inverted physical feedback", fields["B6:B7"]["semantic"] == "Motor Actual Current (Q Axis)" and fields["B6:B7"]["techstream_did"] == "0x1151" and fields["B6:B7"]["packet_scale"] == -0.01)
check("4A3 carries selected steering fault/inhibit duplicate", fields["B0[0]"]["semantic"].startswith("selected steering fault/inhibit status") and "not an exhaustive EPS-fault state" in fields["B0[0]"]["semantic"])
check("4A3 remains route-availability bounded", "zero 0x4A3 frames" in b["dynamic_boundary"])

print("\n== 0x351 mixed status bridge ==")
s351 = art["state_bridge"]["0x351"]
check("351 is mixed status, not generic readiness", "mixed EPS status" in s351["classification"] and "C159B49-linked" in s351["classification"] and "does not name the whole packet" in s351["boundary"])
check("351 exact C159B49 diagnostic join", s351["diagnostic_join"]["techstream_code"] == "C159B49" and s351["diagnostic_join"]["h_dtc_index"] == 54 and s351["diagnostic_join"]["enabled_word"] == 1)
check("351 exact seven-count transition state", any("seven-count transition state" in x and "0x2B930 = 7" in x for x in s351["producer_chain"]))
check("351 force-7 override is separate and exact", "separately forces code 7" in s351["wire_fields"][0]["semantic"] and "exact force-7 indicator" in s351["wire_fields"][1]["semantic"] and "(FEBE65E4 & 3) != 0" in s351["wire_fields"][1]["semantic"] and "FEBE7E13 != 0" in s351["wire_fields"][1]["semantic"] and any("force-writes code 7 plus FEBE7DD1=1" in x for x in s351["producer_chain"]))
check("351 packet availability remains bounded", "zero 0x351 frames" in s351["dynamic_boundary"])

print("\n== 0x394 classifier ==")
s394 = art["state_bridge"]["0x394"]
check("394 has exact 17-row classifier table", len(s394["state_table_rows"]) == 17 and s394["state_table_rows"][0] == [0, 0, 0, 0, 0])
check("394 homolog table is byte-identical in Sienna", s394["sienna_table_byte_identical"] is True)
check("394 state0 is deepest clear/normal path, not Ready", s394["classifier_states"]["0"]["role"] == "deepest clear/normal classifier path" and s394["openpilot_fault_mapping"]["classifier_deepest_clear_normal_state"] == 0 and "not sufficient to authorize actuation" in s394["openpilot_fault_mapping"]["conservative_clear_state_candidate"])
cfg = s394["state0_final_branch_window"]
check("394 state0 final gating is raw-instruction pinned", cfg["start"] == "0x0004BB16" and cfg["end_exclusive"] == "0x0004BB50" and cfg["sha256"] == "d3838fae94f6a5bdcf953ccabda64142bddeffd2470e4935af3c4a7374ba50c6" and "0x4BB48" in cfg["control_flow"] and "state 16" in cfg["control_flow"] and "not assign OEM names" in cfg["boundary"])
check("394 special state15 remains bounded", s394["classifier_states"]["15"]["role"] == "special operating state" and "not safely nameable" in s394["classifier_states"]["15"]["boundary"])
check("394 temp/permanent fault mapping is deliberately unresolved", s394["openpilot_fault_mapping"]["steerFaultTemporary"] == s394["openpilot_fault_mapping"]["steerFaultPermanent"] == "unresolved")
check("394 packet availability remains bounded", "zero 0x394 frames" in s394["dynamic_boundary"])

print("\n== live 0x030 state and torque ==")
s030 = art["state_bridge"]["0x030"]
check("030 configured signal set 0..36", s030["configured_signals"] == list(range(37)))
check("030 direct packed signals 0..34", s030["direct_packed_signals"] == list(range(35)))
check("030 additive byte7 exact formula", s030["additive_field"]["wire_byte"] == 7 and "sum(payload_bytes_0_through_6) + 0x38" in s030["additive_field"]["formula"])
state_fields = {x["signal_id"]: x for x in s030["steering_state_fields"]}
check("030 selected steering fault/inhibit status nominal polarity observed", state_fields[6]["wire"] == "B6[2]" and state_fields[6]["span_values"] == [0] and state_fields[6]["span_clear_frames"] == 6000)
check("030 torque-validity gate nominal polarity observed", state_fields[8]["wire"] == "B6[0]" and state_fields[8]["span_values"] == [0] and state_fields[8]["span_clear_frames"] == 6000)
check("030 neighboring status bit is live", state_fields[7]["span_values"] == [0, 1])
torque = s030["driver_torque_encoding_family"]
check("030 torque exact physical reconstruction promoted", torque["signal_ids"] == [0, 10, 31] and torque["physical_reconstruction"].startswith("Steering Wheel Torque [N.m] = signal10_signed * 0.1"))
check("030 torque live dynamic range observed", torque["span_torque_nm"]["count"] == 6000 and torque["span_torque_nm"]["min"] < -8.0 and torque["span_torque_nm"]["max"] > 2.8 and torque["span_torque_nm"]["unique_count"] > 500)
check("030 coarse rounding behavior exact", torque["coarse_rounding_delta_values"] == [-1, 0, 1])
check("030 eleven GP-relative false negatives corrected", [x["signal_id"] for x in s030["gp_relative_runtime_fields"]] == [0, 1, 10, 14, 16, 17, 18, 27, 28, 31, 34])
check("underlying FD artifact carries the GP correction", fd["schema"] == "corolla-8965H1202000-fd-control-interface-v2" and fd["fd_0x030_transmit"]["gp_relative_writer_correction"]["affected_signal_ids"] == [0, 1, 10, 14, 16, 17, 18, 27, 28, 31, 34])
check("030 Q-current derivative remains scale-bounded", s030["q_current_derived_field"]["signal_id"] == 34 and "calibration-dependent" in s030["q_current_derived_field"]["classification"])

print("\n== Ready Status input wire join ==")
ready = art["state_bridge"]["ready_status_input_0x51E"]
check("Ready Status exact input wire and DID", ready["can_id"] == "0x51E" and ready["wire"] == "B0[7]" and ready["firmware_signal_id"] == 154 and ready["did"] == "0x1033" and ready["name"] == "Ready Status")
check("Ready Status exact source chain", ready["source_chain"] == ["0x51E B0[7]", "0xFEBE7D1B", "0xFEBEF052", "0xFEBEB5A8", "0xFEBEE811", "DID 0x1033"] and ready["firmware_chain_verified"] is True)
check("Ready Status operational value1 is observed but value0 remains bounded", ready["span_operational_frames"] == 60 and ready["span_values"] == [1] and "value 0" in ready["boundary"] and "does not imply" in ready["boundary"])
check("Ready Status is explicitly an input, not invented as EPS Tx field", "can be parsed as the target-native Ready Status input" in ready["openpilot_consequence"] and "distinct from 0x030/0x351/0x394" in ready["openpilot_consequence"])

print("\n== CarState/Panda closure ==")
closure = art["carstate_and_panda_input_closure"]
check("driver torque is now live on 030", "closed and live on 0x030" in closure["driver_steering_torque"])
check("motor response remains static 4A3", "0x4A3 B6:B7" in closure["motor_actuator_response"] and "current routes do not carry 0x4A3" in closure["motor_actuator_response"])
check("fault gates are live but temp/permanent remains open", "live 0x030 B6[2]" in closure["steering_fault_inhibit_status"] and closure["temporary_vs_permanent_fault"].startswith("not closed"))
check("production safety remains blocked", "do not authorize actuation" in closure["production_safety_boundary"])

print("\n== command ingress continuity ==")
c = art["command_ingress_closure"]
check("large ingress includes B6 target plus 025 sensors", c["supervisor_reaching_ge12bit_fields"] == [{"can_id": "0x025", "signal_id": 184, "bits": 12}, {"can_id": "0x025", "signal_id": 186, "bits": 12}, {"can_id": "0x0B6", "signal_id": 255, "bits": 16}])
check("B6 target-angle command remains exact", c["b6_target_angle"]["signal_id"] == 255 and c["b6_target_angle"]["wire_byte"] == 4 and c["b6_target_angle"]["signed"] and c["b6_target_angle"]["snapshot"] == "0xFEBEAE82")
check("B6 receiver contract retained", c["b6_target_angle"]["request_selection_closed"] is True and c["b6_target_angle"]["receiver_loss_cutout_ticks"] == 7 and c["b6_target_angle"]["sequence_modulus"] == 64 and c["b6_target_angle"]["sequence_gap_cap"] == 8)

print("\n== documentation integration ==")
doc = DOC.read_text() if DOC.exists() else ""
for token in ("0x4A3", "0x351", "0x394", "0x030", "0x1035", "0x1037", "0x1151", "0x0B6", "Target Steering Angle", "FRC_P5"):
    check(f"doc preserves {token}", token in doc)
findings = (REPO / "docs/status/FINDINGS.md").read_text()
priorities = (REPO / "docs/status/PRIORITIES.md").read_text()
check("COM-009 integrated", "| COM-009 |" in findings and "corolla-h-f-openpilot-state-bridge.md" in findings)
check("priority consumes state bridge", "corolla-h-f-openpilot-state-bridge.md" in priorities)

print(f"\nResults: {passed} passed, {failed} failed")
raise SystemExit(1 if failed else 0)
