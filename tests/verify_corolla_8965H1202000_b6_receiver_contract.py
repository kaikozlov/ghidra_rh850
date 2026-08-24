#!/usr/bin/env python3
"""Verify the H protected-B6 request/validity/loss receiver contract."""
from __future__ import annotations
import hashlib, json, struct, subprocess, sys, tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
ART = REPO / "data/generated/corolla_8965H1202000_b6_receiver_contract.json"
EVID = REPO / "data/generated/corolla_8965H1202000_b6_receiver_contract_decompiler_evidence.json"
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
can_ev = json.loads(CAN_EVID.read_text())
raw = RAW.read_bytes()

print("\n== exact source binding ==")
check("schema v1", art["schema"] == "corolla-8965H1202000-b6-receiver-contract-v1")
check("H image exact", len(raw) == 0x100000 and art["sources"]["codeflash"]["sha256"] == sha(raw) == "0b47bdc1217835c839e3543e52eab40eb793650a9c159e46f6a9b365ea41a67f")
check("33 compact receiver functions", ev["function_count"] == art["sources"]["decompiler_evidence"]["function_count"] == 33)
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
check("wall-clock timeout explicitly unsupported", loss["absolute_time_supported"] is False and "do not convert" in loss["absolute_time_boundary"] and "milliseconds" in loss["absolute_time_boundary"])

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

print("\n== scheduler domain ==")
sched = com["scheduler"]
check("foreground tick source exact", sched["foreground_loop"] == "0x0005F30C" and "TAUJ0 CH3" in sched["tick_source"] and "0xFFFFB111" in sched["tick_source"])
check("deadline and status run in same tick domain", sched["same_tick_domain"] is True and sched["lower_deadline_chain"] == "5F30C -> 5FAF2 -> 73564 -> 7683C" and "58BBC transition | 59574 steady" in sched["status_chain"])
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
check("signal258 profile-dependent contribution gate bounded", cf["258"]["wire"] == "B6 bit2" and cf["258"]["snapshot"] == "0xFEBEADBB" and cf["258"]["consumer"] == "0x000CBEEE" and "value 1 is required" in cf["258"]["semantics"] and cf["258"]["oem_name_identified"] is False)
check("signal258 OEM name is not overclaimed", cf["258"]["family_vocabulary_candidate"] == "Cooperative Control in Progress Flag" and "does not prove" in cf["258"]["boundary"])
check("signal260 four-state controller selector bounded", cf["260"]["wire"] == "B7 bits7:6" and cf["260"]["snapshot"] == "0xFEBEADC2" and cf["260"]["consumers"] == ["0x000C89D2","0x000C8D42"] and cf["260"]["oem_name_identified"] is False)
seq = cf["261"]
check("signal261 is exact six-bit rolling sequence counter", seq["wire"] == "B7 bits5:0" and seq["snapshot"] == "0xFEBEADBC" and seq["classification"] == "rolling-sequence-counter" and seq["counter_bits"] == 6 and seq["wrap_max"] == 63 and seq["modulus"] == 64)
check("sequence constants raw exact", struct.unpack_from("<H", raw, 0xAFCE8)[0] == 63 and struct.unpack_from("<H", raw, 0xAFCEA)[0] == 8 and seq["gap_cap"] == 8)
check("sequence gap behavior exact", seq["delta_formula"] == "delta = (current - previous) mod 64" and seq["effective_gap_formula"] == "effective_gap = 1 when delta <= 1, otherwise min(delta, 8)" and seq["strict_plus_one_required"] is False)
check("sequence gap reaches plausibility supervision", "CB4F4" in seq["downstream"] and "GP+0xA4C" in seq["downstream"])
check("signal264 special validity/inhibit remains scoped", cf["264"]["wire"] == "B10 bit7" and cf["264"]["snapshot"] == "0xFEBEADC1" and "zero is required" in cf["264"]["semantics"] and "AP/Remote Parking" in cf["264"]["scope_boundary"])
check("signal265 is valid-gated status", cf["265"]["wire"] == "B10 bits2:0" and cf["265"]["snapshot"] == "0xFEBEADD9" and cf["265"]["consumer"] == "0x000CCF58" and "healthy" in cf["265"]["semantics"])

print("\n== static conclusion ==")
c = art["static_conclusion"]
check("receiver request selection closed", c["request_selection_closed"] is True)
check("loss cutout closed only in ticks", c["primary_loss_cutout_closed_in_ticks"] is True and c["primary_loss_cutout_ticks"] == 7 and c["wall_clock_timeout_closed"] is False)
check("rolling sequence contract closed", c["sequence_counter_closed"] is True and c["sequence_modulus"] == 64 and c["sequence_gap_cap"] == 8)
check("secondary names and upstream producer remain bounded", c["secondary_field_names_closed"] is False and c["upstream_producer_closed"] is False and "FRC_P5/Brake producer" in c["next_static_target"])
check("evidence boundary rejects sender/ms overclaim", "does not infer milliseconds" in art["evidence_boundary"] and "sender implementation" in art["evidence_boundary"])

print(f"\nResults: {passed} passed, {failed} failed")
raise SystemExit(1 if failed else 0)
