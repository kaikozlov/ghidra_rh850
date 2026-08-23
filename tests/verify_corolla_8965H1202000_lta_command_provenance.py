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
check("36 target-native functions support provenance closure", e["function_count"] == 36)
check("LTA report consumes tracked compact whole-corpus census", d["schema"] == "corolla-8965H1202000-lta-command-provenance-v3" and d["whole_corpus_census"]["path"] == "data/generated/corolla_8965H1202000_lta_command_provenance_census.json" and d["whole_corpus_census"]["source_function_count"] > 5000)
for row in e["functions"]:
    start = int(row["entry"], 16); size = row["body_size"]
    check(f"raw body hash {row['entry']}", hashlib.sha256(image[start:start+size]).hexdigest() == row["body_sha256"])

print("\n== retained Sienna-homolog LTA magnitude branch ==")
r = d["retained_lta_branch"]
for addr, init, consumer in [
    ("0xFEBEC17C", "0X000C97A8", "0X000C9C16"),
    ("0xFEBEC17E", "0X000C97A8", "0X000C9C16"),
    ("0xFEBEC184", "0X000C97A8", "0X000C9C16"),
]:
    cell = r["magnitude_inputs"][addr]
    check(f"{addr} has exactly init plus rate-limit consumer", [x["entry"] for x in cell["occurrences"]] == [init, consumer])
    check(f"{addr} only direct writer is zero init", len(cell["direct_lhs_writes"]) == 1 and "= 0;" in cell["direct_lhs_writes"][0]["lines"][0])
    check(f"{addr} has no raw absolute pointer literal", cell["raw_u32_literal_pointer_hits"] == [])
check("C9C16 recovers three-word magnitude vote/rate-limit", r["magnitude_vote_and_rate_limit"]["recovered"])

print("\n== retained LTA mode activation ==")
c26d = r["magnitude_inputs"]["0xFEBEC26D"]
check("C26D occurrence set is two readers plus one zero init", [x["entry"] for x in c26d["occurrences"]] == ["0X000CB07C", "0X000CB1C8", "0X000CBE6E"])
check("C26D only direct writer is zero", len(c26d["direct_lhs_writes"]) == 1 and "= 0;" in c26d["direct_lhs_writes"][0]["lines"][0])
check("C26D has no raw absolute pointer literal", c26d["raw_u32_literal_pointer_hits"] == [])
check("cyclic decoder explicitly requires C26D==1", r["mode_enable"]["decoder_requires_one"])
check("decoder initializes all mode outputs to zero before gate", r["mode_enable"]["decoder_zeroes_all_outputs_when_gate_false"])
check("retained command conditioning chain is recovered", all(x["recovered"] for x in r["command_conditioning"]))
check("C2A6 writers are init/reset plus CB8BA state machine", [x["entry"] for x in r["command_state_writes"]["0xFEBEC2A6"]] == ["0X000CB696", "0X000CB6CA", "0X000CB8BA"])
check("C2A8 writers are init/reset plus CB9B6 conditioner", [x["entry"] for x in r["command_state_writes"]["0xFEBEC2A8"]] == ["0X000CB696", "0X000CB6CA", "0X000CB9B6"])

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
for addr in ["0xFEBEBE04","0xFEBEBD90","0xFEBEB678","0xFEBEBEC6","0xFEBEC39C","0xFEBEABB0","0xFEBEBCF8"]:
    writes = f["direct_zero_writer_census"][addr]
    check(f"{addr} direct writers are zero-only", writes and all("= 0;" in line for x in writes for line in x["lines"]))

print("\n== bounded static conclusion ==")
s = d["static_conclusion"]
check("retained LTA magnitudes are direct-write zero", s["retained_sienna_lta_magnitude_direct_write_zero"])
check("retained LTA enable is direct-write zero", s["retained_sienna_lta_enable_direct_write_zero"])
check("retained LTA branch is not active under recovered direct writes", s["retained_sienna_lta_branch_active_under_recovered_direct_writes"] is False)
check("no hidden D7 group/full-PDU command is recovered", s["hidden_d7_group_or_full_pdu_command_recovered"] is False)
check("no hidden B6 group/full-PDU command is recovered", s["hidden_b6_group_or_full_pdu_command_recovered"] is False)
check("all shared command-sized ingress is sensor state", s["shared_command_sized_ingress_classified_as_sensor_state"])
check("Command Value Torque is not classified LTA-only", s["command_value_torque_is_lta_only"] is False)
check("external autonomous lateral ingress remains unidentified", s["external_autonomous_lateral_ingress_identified"] is False)
check("broad static search is closed", s["broad_static_search_closed"] is True)

print(f"\nResults: {passed} passed, {failed} failed")
raise SystemExit(1 if failed else 0)
