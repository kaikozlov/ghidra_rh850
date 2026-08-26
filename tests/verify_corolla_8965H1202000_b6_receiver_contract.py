#!/usr/bin/env python3
"""Verify the H protected-B6 request/validity/loss receiver contract."""
from __future__ import annotations
import hashlib, json, struct, subprocess, sys, tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
ART = REPO / "data/generated/corolla_8965H1202000_b6_receiver_contract.json"
EVID = REPO / "data/generated/corolla_8965H1202000_b6_receiver_contract_decompiler_evidence.json"
FOLLOWUP = REPO / "data/generated/corolla_8965H1202000_tms053_followup_decompiler_evidence.json"
CAN_EVID = REPO / "data/generated/corolla_8965H1202000_can_com_decompiler_evidence.json"
RAW = REPO / "community/albinoelephant/normalized/8965H1202000_CodeFlash.bin"
TOOL = REPO / "tools/build_corolla_h_b6_receiver_contract.py"
passed = failed = 0

def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def check(name: str, cond: object, detail: str = "") -> None:
    global passed, failed
    ok = bool(cond); passed += int(ok); failed += int(not ok)
    print(f"[{'PASS' if ok else 'FAIL'}][raw_bytes] {name}" + (f" ({detail})" if detail else ""))

with tempfile.TemporaryDirectory() as td:
    out = Path(td) / "receiver.json"
    r = subprocess.run([sys.executable, str(TOOL), "--out", str(out)], cwd=REPO, capture_output=True, text=True)
    check("receiver builder exits", r.returncode == 0, (r.stdout + r.stderr)[-500:] if r.returncode else "")
    check("receiver artifact regenerates exactly", r.returncode == 0 and out.read_bytes() == ART.read_bytes())

art = json.loads(ART.read_text())
ev = json.loads(EVID.read_text())
followup = json.loads(FOLLOWUP.read_text())
can_ev = json.loads(CAN_EVID.read_text())
raw = RAW.read_bytes()

print("\n== exact source binding ==")
check("schema v1", art["schema"] == "corolla-8965H1202000-b6-receiver-contract-v1")
check("H image exact", len(raw) == 0x100000 and art["sources"]["codeflash"]["sha256"] == sha(raw) == "0b47bdc1217835c839e3543e52eab40eb793650a9c159e46f6a9b365ea41a67f")
check("33 historical compact receiver functions preserved", ev["function_count"] == art["sources"]["decompiler_evidence"]["function_count"] == 33)
check("29 TMS-053 follow-up functions are raw-bound", followup["function_count"] == art["sources"]["tms053_followup_decompiler_evidence"]["function_count"] == 29 and all(sha(raw[int(x["entry"], 16):int(x["entry"], 16) + x["body_size"]]) == x["body_sha256"] for x in followup["functions"]))
check("all compact receiver bodies raw-bound", all(sha(raw[int(x["entry"], 16):int(x["entry"], 16) + x["body_size"]]) == x["body_sha256"] for x in ev["functions"]))
rx = next(x for x in can_ev["functions"] if x["entry"] == "0x00076A3C")
check("CAN COM receive indication raw-bound", sha(raw[0x76A3C:0x76A3C + rx["body_size"]]) == rx["body_sha256"])

print("\n== request selection ==")
req = art["request_contract"]
check("signal254 request geometry", req["signal_id"] == 254 and req["wire_byte"] == 3 and req["bit_length"] == 6 and req["snapshot"] == "0xFEBEADB0")
check("OEM request dictionary exact", req["oem_dictionary"] == "Target Lateral ID" and req["no_request"] == {"value": 0, "label": "No Request (Manual Operation)"})
check("five H active request IDs exact", req["accepted_active_requests"] == {"1":"PCS","4":"LDA","10":"Hands Off LTA","11":"LTA/LCA","19":"PDA"})
check("request decoder/gates exact", req["decoder"] == "0x000CBE6E" and req["common_active_flag"] == "0xFEBEC272" and req["receiver_gates"] == ["0xFEBEACBD == 0", "0xFEBEC26D == 1"])
check("signal254 classified as request ID", req["classification"] == "supported-target-lateral-request-id" and "unsupported/No-Request" in req["boundary"])

print("\n== lower COM deadline and loss cutout ==")
com = art["communication_supervision"]
pdu_raw = raw[0x22770:0x22778]
check("PDU42 raw descriptor exact", pdu_raw.hex() == "060000002000000c" and struct.unpack("<HBBHBB", pdu_raw) == (6,0,0,32,0,12))
pdu = com["pdu_descriptor"]
check("PDU42 contract decodes deadline/length/flags", pdu == {"address":"0x00022770","raw_hex":"060000002000000c","deadline_value_ticks":6,"successful_rx_reload_ticks":7,"length":32,"flags":12,"activity_tracking_enabled":True})
check("successful Rx reload and activity clear", com["successful_receive"]["entry"] == "0x00076A3C" and any("769F6" in x for x in com["successful_receive"]["actions"]) and any("87A82" in x for x in com["successful_receive"]["actions"]))
loss = com["deadline_expiry"]
check("primary cutout is seven foreground ticks", loss["primary_cutout_after_foreground_ticks"] == 7 and loss["countdown"] == "0x0007683C" and "87AA0" in loss["expiry_action"])
check("wall-clock timeout closed at nominal 35 ms", loss["absolute_time_supported"] is True and loss["nominal_primary_cutout_ms"] == 35.0 and "5.1 ms" in loss["absolute_time_boundary"])

print("\n== receive-status propagation ==")
status_raw = raw[0x28D8C:0x28D94]
check("slot18 status config exact", status_raw.hex() == "2a00000bb8010200" and status_raw[0] == 42 and struct.unpack_from("<H", status_raw, 4)[0] == 440)
qual = com["status_qualifier"]
check("extended qualifier records 440 threshold", qual["config_address"] == "0x00028D8C" and qual["configured_extended_threshold_ticks"] == 440 and qual["primary_cutout_precedes_extended_state"] is True)
flow = com["status_dataflow"]
check("status slot18 chain exact", flow["slot_accessor"] == "0x44744(0x18)" and flow["raw"] == "0xFEBE7DA0" and flow["staging"] == "0xFEBEF132" and flow["snapshot"] == "0xFEBEADB9")
check("receive status convention exact", flow["initial_value"] == 1 and flow["healthy_value"] == 0 and "nonzero immediately" in flow["loss_value"])
gate = com["steering_enable_gate"]
check("C26D steering-health gate exact", gate["entry"] == "0x000CC7F8" and gate["output"] == "0xFEBEC26D" and gate["health_slots"] == ["0x10 (CAN 0x025)", "0x18 (CAN 0x0B6)"] and "0xFEBEADB9 == 0" in gate["condition"])
check("loss disables cooperative profile selection", "cannot assert any cooperative profile" in gate["effect"])
mode_gate = com["cooperative_system_mode_gate"]
check("FEBEACBD normalization exact", mode_gate["source_state"] == "0xFEBEF000" and mode_gate["normalized_output"] == "0xFEBEACBD" and mode_gate["normalization"] == {"0": 0, "2": 2, "3": 4, "other_nonzero": 1})
check("cooperative acceptance requires ACBD0 and C26D1", "FEBEACBD == 0 AND FEBEC26D == 1" in mode_gate["cooperative_acceptance"])
check("ACBD is distinct from B6 communication loss", "not a synonym" in mode_gate["classification"] and "FEBEADB9 -> FEBEC26D" in mode_gate["b6_loss_path_is_separate"])
check("no direct H Tx packer reads ACBD under promoted census", mode_gate["direct_reference_count"] == 21 and mode_gate["direct_tx_packer_refs"] == [] and "no native wire-visible" in mode_gate["wire_feedback_boundary"])

print("\n== scheduler domain ==")
sched = com["scheduler"]
check("foreground tick source exact", sched["foreground_loop"] == "0x0005F30C" and "TAUJ0 CH3" in sched["tick_source"] and "0xFFFFB111" in sched["tick_source"])
check("deadline and status run in same tick domain", sched["same_tick_domain"] is True and sched["lower_deadline_chain"] == "5F30C -> 5FAF2 -> 73564 -> 7683C" and "58BBC transition | 59574 steady" in sched["status_chain"])
timing = sched["tauj0_config"]
check("TAUJ0 CH3 startup/steady count geometry exact", timing["init_entry"] == "0x0005F660" and timing["steady_reload_entry"] == "0x0005F812" and timing["tps"] == timing["brs"] == timing["cmor3"] == 0 and timing["ch3_initial_cdr"] == 407999 and timing["ch3_steady_cdr"] == 399999 and timing["ch3_initial_counts"] == 408000 and timing["ch3_steady_counts"] == 400000)
check("steady foreground tick is nominal 5 ms with one 5.1 ms startup interval", timing["nominal_steady_tick_ms"] == 5.0 and abs(timing["nominal_initial_interval_ms"] - 5.1) < 1e-12)
dyn = sched["dynamic_corroboration"]
check("Span 0x030 dynamically corroborates two ticks at ~10 ms", dyn["frames"] == 6000 and dyn["descriptor_cycle_ticks"] == 2 and abs(dyn["mean_interval_ms"] - 10.00001211468578) < 1e-9 and abs(dyn["derived_foreground_tick_ms"] - 5.00000605734289) < 1e-9)
check("Techstream missing-message join exact", com["techstream"] == {"dtc":"U012987","description":"Lost Communication with Brake System Control Module","failure":"Missing Message","dem_event":"0x0143"})

print("\n== companion control fields ==")
cf = art["companion_fields"]
unpacker = next(x["decompiled_c"] for x in ev["functions"] if x["entry"] == "0x00046A10")
check("signals258/260/261/264/265 exact unpacker geometries", all(token in unpacker for token in (
    "FUN_0007643a(0x102,0x1ad,1,2,0,unaff_gp + -0x3a68);",
    "FUN_0007643a(0x104,0x1ae,2,6,0,unaff_gp + -0x3a66);",
    "FUN_0007643a(0x105,0x1ae,6,0,0,unaff_gp + -0x3a65);",
    "FUN_0007643a(0x108,0x1b1,1,7,0,unaff_gp + -0x3a62);",
    "FUN_0007643a(0x109,0x1b1,3,0,0,unaff_gp + -0x3a5f);",
)))
check("signal258 corrected as additive-term suppressor", cf["258"]["wire"] == "B6 bit2" and cf["258"]["snapshot"] == "0xFEBEADBB" and cf["258"]["consumer"] == "0x000CBEEE" and "signal258 == 1 suppresses" in cf["258"]["semantics"] and cf["258"]["candidate_id11_value"] == 1 and cf["258"]["oem_name_identified"] is False)
check("signal258 OEM name is not overclaimed", cf["258"]["family_vocabulary_candidate"] == "Cooperative Control in Progress Flag" and "does not prove" in cf["258"]["boundary"])
check("signal260 0/3 recovered-equivalence is bounded", cf["260"]["wire"] == "B7 bits7:6" and cf["260"]["snapshot"] == "0xFEBEADC2" and cf["260"]["consumers"] == ["0x000C89D2","0x000C8D42"] and "values 0 and 3" in cf["260"]["semantics"] and cf["260"]["candidate_id11_value"] == 0 and "not asserted globally equivalent" in cf["260"]["candidate_boundary"])
seq = cf["261"]
check("signal261 is exact six-bit rolling sequence counter", seq["wire"] == "B7 bits5:0" and seq["snapshot"] == "0xFEBEADBC" and seq["classification"] == "rolling-sequence-counter" and seq["counter_bits"] == 6 and seq["wrap_max"] == 63 and seq["modulus"] == 64)
check("sequence constants raw exact", struct.unpack_from("<H", raw, 0xAFCE8)[0] == 63 and struct.unpack_from("<H", raw, 0xAFCEA)[0] == 8 and seq["gap_cap"] == 8)
check("sequence gap behavior exact", seq["delta_formula"] == "delta = (current - previous) mod 64" and seq["effective_gap_formula"] == "effective_gap = 1 when delta <= 1, otherwise min(delta, 8)" and seq["strict_plus_one_required"] is False)
check("sequence gap reaches plausibility supervision", "CB4F4" in seq["downstream"] and "GP+0xA4C" in seq["downstream"])
check("signals262/263 zero remove recovered percentage contributions", cf["262"]["wire"] == "B8" and cf["262"]["snapshot"] == "0xFEBEADBD" and cf["262"]["consumer"] == "0x000CC442" and cf["262"]["candidate_id11_value"] == 0 and cf["263"]["wire"] == "B9" and cf["263"]["snapshot"] == "0xFEBEADBE" and cf["263"]["consumer"] == "0x000CBFCE" and cf["263"]["candidate_id11_value"] == 0)
check("signal264 special validity/inhibit remains scoped", cf["264"]["wire"] == "B10 bit7" and cf["264"]["snapshot"] == "0xFEBEADC1" and "zero is required" in cf["264"]["semantics"] and cf["264"]["candidate_id11_value"] == 0 and "AP/Remote Parking" in cf["264"]["scope_boundary"])
check("signal265 is valid-gated status with zero default", cf["265"]["wire"] == "B10 bits2:0" and cf["265"]["snapshot"] == "0xFEBEADD9" and cf["265"]["consumer"] == "0x000CCF58" and cf["265"]["downstream_consumer"] == "0x000CCF8C" and cf["265"]["initial_default_value"] == cf["265"]["candidate_id11_value"] == 0 and "healthy" in cf["265"]["semantics"])

print("\n== static conclusion ==")
c = art["static_conclusion"]
check("receiver request selection closed", c["request_selection_closed"] is True)
check("loss cutout closed in ticks and nominal wall clock", c["primary_loss_cutout_closed_in_ticks"] is True and c["primary_loss_cutout_ticks"] == 7 and c["wall_clock_timeout_closed"] is True and c["foreground_tick_nominal_ms"] == 5.0 and c["primary_loss_cutout_nominal_ms"] == 35.0)
check("rolling sequence contract closed", c["sequence_counter_closed"] is True and c["sequence_modulus"] == 64 and c["sequence_gap_cap"] == 8)
check("secondary names and upstream producer remain bounded", c["secondary_field_names_closed"] is False and c["upstream_producer_closed"] is False and c["minimal_id11_companion_candidate_closed_for_eps_consumers"] is True and "FRC_P5/Brake stock template" in c["next_static_target"])
check("evidence boundary keeps stock cadence/cross-ECU neutrality bounded", "35.0 ms" in art["evidence_boundary"] and "stock B6 transmit cadence" in art["evidence_boundary"] and "cross-ECU neutrality" in art["evidence_boundary"])

print(f"\nResults: {passed} passed, {failed} failed")
raise SystemExit(1 if failed else 0)
