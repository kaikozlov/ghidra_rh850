#!/usr/bin/env python3
"""Verify the exact-image Corolla H autonomous-lateral command provenance."""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
ART = REPO / "data/generated/corolla_8965H1202000_lta_command_provenance.json"
EVID = REPO / "data/generated/corolla_8965H1202000_lta_command_provenance_decompiler_evidence.json"
TOOL = REPO / "tools/build_corolla_h_lta_command_provenance.py"
IMAGE = REPO / "community/albinoelephant/normalized/8965H1202000_CodeFlash.bin"
passed = failed = 0


def check(name: str, cond: object, detail: str = "") -> None:
    global passed, failed
    ok = bool(cond)
    passed += int(ok); failed += int(not ok)
    suffix = f" ({detail})" if detail else ""
    print(f"[{'PASS' if ok else 'FAIL'}][raw_bytes] {name}{suffix}")


with tempfile.TemporaryDirectory() as td:
    out = Path(td) / "lta.json"
    subprocess.run([sys.executable, str(TOOL), "--out", str(out)], cwd=REPO, check=True,
                   stdout=subprocess.DEVNULL)
    check("tracked LTA provenance report regenerates exactly", out.read_bytes() == ART.read_bytes())

d = json.loads(ART.read_text())
e = json.loads(EVID.read_text())
image = IMAGE.read_bytes()

print("\n== evidence identity ==")
check("report is exact H image-bound", d["software_id"] == "8965H1202000" and d["images"]["corolla_h"]["sha256"] == hashlib.sha256(image).hexdigest())
check("50 target-native functions support direct+computed provenance closure", e["function_count"] == 50)
check("LTA report consumes tracked compact whole-corpus census", d["schema"] == "corolla-8965H1202000-lta-command-provenance-v8" and d["whole_corpus_census"]["path"] == "data/generated/corolla_8965H1202000_lta_command_provenance_census.json" and d["whole_corpus_census"]["source_function_count"] > 5000)
for row in e["functions"]:
    start = int(row["entry"], 16); size = row["body_size"]
    check(f"raw body hash {row['entry']}", hashlib.sha256(image[start:start+size]).hexdigest() == row["body_sha256"])

print("\n== retained Sienna-homolog branch: computed-writer correction ==")
r = d["retained_lta_branch"]
for addr in ("0xFEBEC17C", "0xFEBEC17E", "0xFEBEC184", "0xFEBEC26D"):
    cell = r["direct_symbol_observations"][addr]
    check(f"{addr} direct-symbol census retained as bounded observation", cell["direct_symbol_lhs_writes"] and cell["raw_u32_literal_pointer_hits"] == [])

corr = r["computed_writer_correction"]
check("direct-symbol-only census is explicitly marked incomplete", corr["direct_symbol_census_was_incomplete"] is True)
mode = corr["mode_enable_0xFEBEC26D"]
check("CC7F8 recovers GP-relative C26D writer", mode["writer"] == "0x000CC7F8" and mode["recovered"] and mode["selector_recovered"] and mode["health_aggregate_recovered"])
check("health selectors 0x10/0x18 both use class2", mode["selector_slots"]["0x10"]["health_class"] == 2 and mode["selector_slots"]["0x18"]["health_class"] == 2)
check("raw selector rows pinned", mode["selector_slots"]["0x10"]["raw_hex"] == "025a2300000bb801" and mode["selector_slots"]["0x18"]["raw_hex"] == "02002b00000bffff")
mag = corr["replicated_magnitude_0xFEBEC17C_17E_184"]
check("CC2EC->CAD62 recovers GP-relative magnitude triplet writers", mag["writer"] == "0x000CAD62" and mag["upstream_conditioner"] == "0x000CC2EC" and mag["recovered"])
mods = {x["signal_id"]: x for x in corr["b6_modulators"]}
check("B6 signal262 is 8-bit byte8 ADBD modifier", mods[262]["wire_byte"] == 8 and mods[262]["bit_length"] == 8 and mods[262]["snapshot"] == "0xFEBEADBD" and mods[262]["consumer"] == "0x000CC442" and mods[262]["recovered"])
check("B6 signal263 is 8-bit byte9 ADBE modifier", mods[263]["wire_byte"] == 9 and mods[263]["bit_length"] == 8 and mods[263]["snapshot"] == "0xFEBEADBE" and mods[263]["consumer"] == "0x000CBFCE" and mods[263]["recovered"])
check("base magnitude synthesis is target-native local state", corr["local_base_synthesis"]["entry"] == "0x000CC18E" and corr["local_base_synthesis"]["recovered"])
check("C9C16 still recovers three-word magnitude vote/rate-limit", r["magnitude_vote_and_rate_limit"]["recovered"])
check("mode decoder explicitly requires C26D==1", r["mode_enable"]["decoder_requires_one"])
check("mode decoder initializes all outputs zero before gate", r["mode_enable"]["decoder_zeroes_all_outputs_when_gate_false"])
check("retained command conditioning chain is recovered", all(x["recovered"] for x in r["command_conditioning"]))
check("retained branch classification records live local B6-modulated path", r["classification"] == "retained-sienna-homolog-conditioner-live-b6-target-angle-driven-and-b6-modulated")

print("\n== D7 hidden-payload census ==")
d7 = d["d7_hidden_payload_census"]
check("D7 SecOC profile is 32 bytes with 28-bit MAC and 4-bit transmitted freshness", d7["secured_length"] == 32 and d7["profile"]["authenticator_bits"] == 28 and d7["profile"]["transmitted_freshness_bits"] == 4)
check("D7 carries 28 authenticated application bytes", d7["profile"]["security_trailer_bytes"] == 4 and d7["profile"]["authenticated_application_bytes"] == 28)
check("D7 configured signal IDs are exactly 240..247", d7["com"]["configured_signal_ids"] == list(range(240,248)))
check("D7 scalar receive IDs are exactly 240/243/246", d7["com"]["scalar_receive_ids"] == [240,243,246])
check("D7 configured nonscalar IDs are 241/242/244/245/247", d7["com"]["configured_without_scalar_receive"] == [241,242,244,245,247])
check("no D7 nonscalar ID is consumed by block/group API", d7["com"]["non_scalar_ids_used_by_block_group_api"] == [])
check("full-PDU copy does not use D7/PDU40", d7["com"]["all_literal_full_pdu_ids"] == [0] and d7["com"]["d7_full_pdu_copy_present"] is False)
check("D7 COM buffer has no raw absolute pointer literal", d7["com"]["buffer_address"] == "0xFEBE4ACC" and d7["com"]["raw_u32_buffer_pointer_hits"] == [])

print("\n== B6 hidden-payload census ==")
b = d["b6_hidden_payload_census"]
check("B6 SecOC profile is 32 bytes with 28-bit MAC and 4-bit transmitted freshness", b["secured_length"] == 32 and b["profile"]["authenticator_bits"] == 28 and b["profile"]["transmitted_freshness_bits"] == 4)
check("B6 therefore carries 28 authenticated application bytes", b["profile"]["security_trailer_bytes"] == 4 and b["profile"]["authenticated_application_bytes"] == 28)
check("B6 configured signal IDs are exactly 252..267", b["com"]["configured_signal_ids"] == list(range(252,268)))
check("B6 scalar receive IDs are exactly 254..265", b["com"]["scalar_receive_ids"] == list(range(254,266)))
check("B6 configured nonscalar IDs are 252/253/266/267", b["com"]["configured_without_scalar_receive"] == [252,253,266,267])
check("block/group receive calls resolve only unrelated IDs", b["com"]["all_literal_block_group_receive_ids"] == list(range(89,97)) + list(range(99,103)))
check("no B6 nonscalar ID is consumed by block/group API", b["com"]["non_scalar_ids_used_by_block_group_api"] == [])
check("full-PDU copy surface only uses PDU0", b["com"]["all_literal_full_pdu_ids"] == [0] and b["com"]["b6_full_pdu_copy_present"] is False)
check("B6 COM buffer has no raw absolute pointer literal", b["com"]["buffer_address"] == "0xFEBE4AF4" and b["com"]["raw_u32_buffer_pointer_hits"] == [])
check("Sienna 2E4 control also has nonscalar configured rows", b["sienna_2e4_control"]["configured_signal_ids"] == list(range(58,66)) and b["sienna_2e4_control"]["configured_without_scalar_receive"] == [64,65])

print("\n== adversarial shared-large-field closure ==")
sh = d["shared_can025_sensor_ingress"]
support = d["supporting_inputs"]
sup_path = REPO / support["supervisor_external_ingress_census"]["path"]
check("supervisor external-ingress census identity is bound", hashlib.sha256(sup_path.read_bytes()).hexdigest() == support["supervisor_external_ingress_census"]["sha256"])
dbc_path = REPO / sh["dbc"]["path"]
check("pinned Toyota DBC identity is bound", hashlib.sha256(dbc_path.read_bytes()).hexdigest() == sh["dbc"]["sha256"])
check("CAN025 is pinned as STEER_ANGLE_SENSOR", sh["can_id"] == "0x025" and sh["dbc"]["message"] == "STEER_ANGLE_SENSOR" and sh["dbc"]["message_id_decimal"] == 37)
check("DBC coarse steering angle is signed12", sh["dbc"]["signals"]["STEER_ANGLE"] == {"start_bit_motorola":3,"bit_length":12,"signed":True})
check("DBC steering fraction is signed4", sh["dbc"]["signals"]["STEER_FRACTION"] == {"start_bit_motorola":39,"bit_length":4,"signed":True})
check("DBC steering rate is signed12", sh["dbc"]["signals"]["STEER_RATE"] == {"start_bit_motorola":35,"bit_length":12,"signed":True})
for sig, bits, byte, bitoff, addr, sref in [
    (184,12,0,0,"0xFEBEADF0",221),
    (185,4,4,4,"0xFEBEACC5",222),
    (186,12,4,0,"0xFEBEAE14",223),
]:
    row = sh["h_signals"][str(sig)]
    check(f"H signal{sig} has exact shared CAN025 shape", row["can_id"] == "0x025" and row["bit_length"] == bits and row["signed"] and row["wire_byte"] == byte and row["bit_offset_in_byte"] == bitoff and row["snapshot_address"] == addr and row["source_unpackers"] == ["0x0004636A"] and row["sienna_same_shape_signals"] == [sref])
check("CAN025 unpacker recovers all three field shapes", all(sh["unpacker"][k] for k in ("signal184_shape_recovered","signal185_shape_recovered","signal186_shape_recovered")))
check("H reconstructs angle from coarse+fraction", sh["target_native_semantics"]["angle_plus_fraction"]["recovered"])
check("H treats signal186 snapshot as rate magnitude", sh["target_native_semantics"]["steering_rate_magnitude"]["recovered"])
check("H jointly plausibility-checks angle and rate", sh["target_native_semantics"]["joint_plausibility"]["recovered"])
check("shared command-sized ingress is classified sensor state", sh["classification"] == "shared-command-sized-ingress-is-steering-angle-sensor-state")

print("\n== final internal torque-command composition ==")
f = d["final_command_composition"]
check("BD0E is recovered from local ABB0+BCF8 chain", f["bd0e_local_chain"]["recovered"])
check("C358 is recovered from local C392+C2D4 chain", f["c358_local_chain"]["recovered"] and f["c358_local_chain"]["c392_recovered_local_state"])
writers = f["computed_writer_audit"]
expected = {
    "0xFEBEBE04":"0x000C68F4", "0xFEBEBD90":"0x000C6146", "0xFEBEB678":"0x000BE25A",
    "0xFEBEBEC6":"0x000C76FA", "0xFEBEC39C":"0x000CD31A",
}
check("all promoted GP-relative final-command writers recover", f["all_promoted_computed_writers_recovered"] and all(writers[a]["writer"] == e and writers[a]["recovered"] for a,e in expected.items()))

print("\n== B6 signed16 target-angle ingress ==")
ta=d["b6_signed16_target_angle_ingress"]
check("B6 signed16 snapshot is AE82", ta["wire_ingress"]["signal_id"] == 255 and ta["wire_ingress"]["snapshot_destination"] == "0xFEBEAE82")
check("B6 signed16 domain is target angle", ta["wire_ingress"]["classification"] == "authenticated-signed16-target-steering-angle-command")
check("target-vs-measured loop is independently recovered", ta["measured_angle_feedback"]["classification"] == "independent-target-versus-measured-steering-angle-control-loop")
check("physical B6 controller-equivalent scale is closed", ta["scaling"]["physical_degree_scale_closed"] is True and ta["scaling"]["controller_equivalent_fraction_deg_per_b6_count"] == {"numerator":1024,"denominator":17870} and abs(ta["scaling"]["controller_equivalent_mrad_per_b6_count"]-1.0001215187701138)<1e-12)
check("B6 OEM wire-unit label remains open", ta["scaling"]["oem_wire_unit_name_closed"] is False)
check("Techstream identifies B6 immediate sender as brake", ta["techstream"]["immediate_sender_monitor"]["description"] == "Lost Communication with Brake System Control Module")

print("\n== corrected bounded static conclusion ==")
s = d["static_conclusion"]
check("earlier direct-write inactive conclusion is superseded", s["earlier_direct_write_inactive_conclusion_superseded"] is True)
check("retained magnitude computed writer is recovered", s["retained_sienna_lta_magnitude_computed_writer_recovered"] is True)
check("retained enable computed writer is recovered", s["retained_sienna_lta_enable_computed_writer_recovered"] is True)
check("retained branch is not statically dead", s["retained_sienna_lta_branch_statically_dead"] is False)
check("B6 percentage modifiers reach retained branch", s["b6_percentage_modulates_retained_branch"] is True)
check("B6 signed16 target-angle command is recovered", s["b6_signed16_target_angle_command_recovered"] is True)
check("no hidden D7 group/full-PDU command is recovered", s["hidden_d7_group_or_full_pdu_command_recovered"] is False)
check("no hidden B6 group/full-PDU command is recovered", s["hidden_b6_group_or_full_pdu_command_recovered"] is False)
check("all shared command-sized ingress is sensor state", s["shared_command_sized_ingress_classified_as_sensor_state"])
check("H-only command-sized scalar is now recovered", s["h_only_or_wire_changed_command_sized_scalar_recovered"] is True)
check("named retained-branch computed alias audit is closed", s["named_retained_branch_computed_alias_audit_closed"] is True)
check("Command Value Torque is not classified LTA-only", s["command_value_torque_is_lta_only"] is False)
check("external autonomous lateral ingress is identified", s["external_autonomous_lateral_ingress_identified"] is True and "0x0B6 signal255" in s["external_autonomous_lateral_ingress"])
check("immediate sender relationship is Brake System Control Module", s["immediate_sender_relationship"] == "Brake System Control Module")
check("upstream feature producer remains open", s["upstream_feature_producer_identified"] is False)
check("physical B6 scale is promoted", s["physical_scale_identified"] is True and abs(s["controller_equivalent_deg_per_count"]-(1024/17870))<1e-15)
check("OEM B6 wire-unit label remains open", s["oem_wire_unit_name_identified"] is False)
check("signal254 accepted profiles and OEM labels recovered", s["signal254_profile_values_recovered"] == [1,4,10,11,19] and s["signal254_exact_feature_labels_identified"] is True and s["signal254_profile_labels"] == {'1':'PCS','4':'LDA','10':'Hands Off LTA','11':'LTA/LCA','19':'PDA'})
check("B6 receiver request/loss/sequence contract promoted", s["request_selection_identified"] is True and s["receiver_loss_cutout_ticks"] == 7 and s["wall_clock_timeout_identified"] is True and s["sequence_counter_identified"] is True and s["sequence_modulus"] == 64 and s["sequence_gap_cap"] == 8)
check("broad static search remains closed", s["broad_static_search_closed"] is True)

print("\n== correction/documentation integration ==")
corrections=(REPO / "docs/status/CORRECTIONS.md").read_text()
findings=(REPO / "docs/status/FINDINGS.md").read_text()
variant=(REPO / "docs/variants/corolla-2023-us-public-route.md").read_text()
priorities=(REPO / "docs/status/PRIORITIES.md").read_text()
check("CORR-107 records GP-relative target-angle correction", "### CORR-107" in corrections and "CC7F8" in corrections and "CAD62" in corrections and "signal255" in corrections and "signals262/263" in corrections and "FEBEAE82" in corrections)
check("CORR-078 is explicitly superseded", "**Superseded:** CORR-107" in corrections)
check("VAR-036 current finding is corrected", "| VAR-036 | **Correction" in findings and "CC2EC -> CAD62" in findings)
check("canonical Corolla report carries corrected B6 target-angle branch", "protected B6 carries target steering angle" in variant and "FEBEF1CC -> FEBEAE82" in variant and "CA138" in variant and "CAD62" in variant)
check("priority promotes recovered B6 target-angle command", "B6 signal255" in priorities and "target-minus-measured" in priorities and "1024/17870" in priorities and "signed16 scalar is staged-only" not in priorities)

print(f"\nResults: {passed} passed, {failed} failed")
raise SystemExit(1 if failed else 0)
