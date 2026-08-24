#!/usr/bin/env python3
"""Build the H/F Corolla state-interface bridge to pre-TSS3 openpilot roles."""
from __future__ import annotations

import argparse
import hashlib
import json
import struct
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
IMAGE = REPO / "community/albinoelephant/normalized/8965H1202000_CodeFlash.bin"
EVID = REPO / "data/generated/corolla_8965H1202000_openpilot_state_bridge_decompiler_evidence.json"
TECH = REPO / "data/generated/corolla_8965H1202000_techstream_correlations.json"
FD = REPO / "data/generated/corolla_8965H1202000_fd_control_interface.json"
INGRESS = REPO / "data/generated/corolla_8965H1202000_supervisor_external_ingress_census.json"
LTA = REPO / "data/generated/corolla_8965H1202000_lta_command_provenance.json"
TARGET = REPO / "data/generated/corolla_8965H1202000_b6_target_angle_ingress.json"
STRUCT = REPO / "data/generated/corolla_8965H1202000_structural_function_transfer.json"
EQ = REPO / "data/generated/corolla_8965F1208000_vs_8965H1202000_codeflash_equivalence.json"
OLD = REPO / "data/external/opendbc/toyota_corolla_pre_tss3_contract.json"
OUT = REPO / "data/generated/corolla_8965H1202000_openpilot_state_bridge.json"
PDU = struct.Struct("<HBBHBB")


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def fnmap(e: dict) -> dict[int, dict]:
    return {int(x["entry"], 16): x for x in e["functions"]}


def need(text: str, *tokens: str) -> None:
    for token in tokens:
        if token not in text:
            raise ValueError(f"missing recovered token: {token}")


def monitor(tech: dict, key: int) -> dict:
    rows = tech["ddb_overlap"]["emps_p5"]["monitor_rows"]
    found = [r for r in rows if r["monitor_key"] == key]
    if len(found) != 1:
        raise ValueError(f"monitor {key} count {len(found)}")
    return found[0]


def build() -> dict:
    image = IMAGE.read_bytes()
    evid = json.loads(EVID.read_text())
    tech = json.loads(TECH.read_text())
    fd = json.loads(FD.read_text())
    ingress = json.loads(INGRESS.read_text())
    lta = json.loads(LTA.read_text())
    target = json.loads(TARGET.read_text())
    struct = json.loads(STRUCT.read_text())
    eq = json.loads(EQ.read_text())
    old = json.loads(OLD.read_text())
    if len(image) != 0x100000 or sha(image) != evid["image"]["sha256"]:
        raise ValueError("H image/evidence identity drift")
    if evid["source_corpus"]["sha256"] != "c3411eec57b9d55c004b0b0f328394bb152577c3398084dccc729dab5da54656":
        raise ValueError("H corrected-context corpus identity drift")
    if evid["source_corpus"]["function_count"] != 5478:
        raise ValueError("H corpus function count drift")
    if eq["application_equivalence"]["different_bytes"] != 0:
        raise ValueError("H/F application equivalence drift")

    f = fnmap(evid)
    for row in evid["functions"]:
        start = int(row["entry"], 16); size = row["body_size"]
        if sha(image[start:start+size]) != row["body_sha256"]:
            raise ValueError(f"raw body drift {row['entry']}")

    c46c4c=f[0x46C4C]["decompiled_c"]; c46d9a=f[0x46D9A]["decompiled_c"]; c4749a=f[0x4749A]["decompiled_c"]
    c46e0c=f[0x46E0C]["decompiled_c"]; c46e62=f[0x46E62]["decompiled_c"]; c47ba2=f[0x47BA2]["decompiled_c"]
    c46e96=f[0x46E96]["decompiled_c"]; c47ada=f[0x47ADA]["decompiled_c"]; c6387c=f[0x6387C]["decompiled_c"]
    need(c46c4c, "sRamfebe7e22 = (short)((sRamfebe6554 * 100) / 0x100);", "uRamfebe7e28 = (undefined2)((sRamfebe6592 * -100) / 0x80);")
    need(c46d9a, "uRamfebe7ddd = (undefined1)uRamfebe7d34;", "FUN_00069420((int)sRamfebe7a46", "FUN_0006387c((int)(*(short *)(iVar1 + -0x39de) / 10)")
    need(c4749a, "uRamfebe88f6 = uRamfebe7ddb;", "FUN_0007662e(0x2b,0x27,8,0", "FUN_0007662e(0x32,0x2e,8,0")
    need(c46e0c, "bRamfebe7dfb = bRamfebe7dfb + 1;", "DAT_0002b930")
    need(c46e62, "param_1 = 7;", "uRamfebe7dd1 = 1;", "uRamfebe7dd0 = param_1;")
    need(c47ba2, "FUN_000764ec(0x25,0x22,3,5", "FUN_000764ec(0x26,0x22,1,4")
    need(c46e96, "uVar1 = bRamfebe7f58 - 1;", "uRamfebe7dd5 = uRamfebe7f65;", "uRamfebe7dda = 3;")
    need(c47ada, "FUN_000764ec(0x27,0x25,2,6", "FUN_000764ec(0x28,0x25,3,3", "FUN_000764ec(0x29,0x26,3,1", "FUN_000764ec(0x2a,0x26,1,0")
    need(c6387c, "uVar1 = 0x7f;", "iVar2 = -0x80;", "uVar1 = 0x81;")

    pdu = [PDU.unpack_from(image, 0x22620 + i*PDU.size) for i in range(5)]
    if pdu != [(2,0,0,32,0,3),(200,0,0,4,0,3),(60,0,0,3,0,3),(100,0,0,8,0,3),(196,0,0,8,0,3)]:
        raise ValueError(f"Tx PDU descriptor drift: {pdu}")

    m15=monitor(tech,15); m17=monitor(tech,17); q=tech["motor_current_bridge"]["techstream_monitors"]["251"]
    if (m15["name"],m15["primary_data_id"],m15["h_callback"]) != ("Steering Wheel Torque","0x1035","0x48820"):
        raise ValueError("Steering Wheel Torque Techstream join drift")
    if (m17["name"],m17["primary_data_id"],m17["h_callback"]) != ("Steering Angle","0x1037","0x488A8"):
        raise ValueError("Steering Angle Techstream join drift")
    if (q["name"],q["primary_data_id"],q["unit"]) != ("Motor Actual Current (Q Axis)","0x1151","A"):
        raise ValueError("Q-current Techstream join drift")

    matches={int(x["target_entry"],16):x for x in struct["matches"]}
    structural={}
    for target_entry, role in ((0x46C4C,"0x4A3 source preparation"),(0x46D9A,"0x4A3 staging"),(0x4749A,"0x4A3 packer"),(0x46E0C,"0x351 debounce"),(0x46E62,"0x351 producer"),(0x47BA2,"0x351 packer"),(0x46E96,"0x394 state projection")):
        row=matches.get(target_entry)
        if not row or row["classification"] != "unique-exact-shape":
            raise ValueError(f"structural transfer drift {target_entry:#x}")
        structural[f"0x{target_entry:08X}"]={"role":role,"reference_entry":row["reference_entry"],"classification":row["classification"],"boundary":row["evidence_boundary"]}

    old260=next(x for x in old["state_messages"] if x["id"]=="0x260")
    old262=next(x for x in old["state_messages"] if x["id"]=="0x262")
    if old260["roles"] != ["driver steering torque","EPS steering torque","accurate steering angle","angle initialization"]:
        raise ValueError("old 0x260 state contract drift")

    large_refs=[x for x in ingress["external_refs"] if x["bits"] >= 12]
    large_signals=sorted({(x["can"],x["signal"],x["bits"]) for x in large_refs})
    if large_signals != [(0x25,184,12),(0x25,186,12),(0xB6,255,16)]:
        raise ValueError(f"supervisor-reaching >=12-bit ingress drift: {large_signals}")
    changed_large={(x['can'],x['signal'],x['bits'],x['signed'],x['wire_byte']) for x in ingress['potential_changed_large_fields']}
    if ingress["summary"]["h_scalar_rx_calls"] != 101 or changed_large != {(0xB6,255,16,1,4)}:
        raise ValueError("complete fixed-map generated-COM ingress census drift")

    pb=tech["protected_brake_profile_semantics"]
    ipm=tech["camera_ipm_a_residue"]
    if lta["schema"] != "corolla-8965H1202000-lta-command-provenance-v8":
        raise ValueError("corrected LTA provenance schema drift")
    lta_static = lta["static_conclusion"]
    if not (lta_static["named_retained_branch_computed_alias_audit_closed"] and lta_static["b6_percentage_modulates_retained_branch"]):
        raise ValueError("computed retained-branch audit not closed")
    return {
      "schema":"corolla-8965H1202000-openpilot-state-bridge-v6",
      "evidence_boundary": (
        "Exact H bytes and target-native decompiler/Techstream joins define the newer EPS state carriers. "
        "Sienna/openpilot structures are used only to identify which roles a port needs, not to transplant field scales or fault codes. "
        "The command side is additionally audited for GP-relative/computed writers: protected B6 signal255 is recovered through a hidden RTE snapshot as a signed16 target-steering-angle command, then compared against independently reconstructed 0x025 measured angle before entering the steering controller. "
        "Physical B6 scaling and OEM mode/request semantics are closed, as are the seven-tick receiver-loss cutoff and modulo-64 sequence handling; wall-clock cadence, exact secondary B6 field names, and the upstream producer/authentication route remain bounded; no second command-sized generated scalar or recovered literal block/group/full-PDU route is identified, while arbitrary computed aliases and DMA/peripheral mutation remain outside this proof."
      ),
      "images": {
        "corolla_h":{"software_id":"8965H1202000","sha256":sha(image)},
        "corolla_f":{"software_id":"8965F1208000","application_byte_identical_to_h":True,"application_sha256":eq["application_equivalence"]["baseline_sha256"]},
      },
      "pre_tss3_openpilot_requirements": {
        "steer_torque_sensor_0x260_roles":old260["roles"],
        "eps_status_0x262_roles":old262["roles"],
        "panda_safety_inputs":old["safety_inputs"],
        "old_fault_states_are_not_portable":old["steering_fault_states"],
      },
      "h_tx_pdu_descriptors": [
        {"pdu":i,"can_id":cid,"descriptor":list(pdu[i]),"length":pdu[i][3],"cycle_or_timeout_raw":pdu[i][0]}
        for i,cid in enumerate(["0x030","0x351","0x394","0x4A3","0x4C8"])
      ],
      "state_bridge": {
        "0x4A3": {
          "classification":"high-confidence newer Corolla openpilot state bridge",
          "length":8,
          "pdu":3,
          "fields":[
            {"wire":"B0","source":"FEBE7DAE | 0x20","semantic":"status/validity family; exact OEM bit meaning unresolved","confidence":"recovered"},
            {"wire":"B1:B2","source":"FEBE7D34 from FD 0x025 signal184","semantic":"mirror of the target-native signed-12 steering-angle sensor field","confidence":"verified dataflow"},
            {"wire":"B3:B4","source":"FEBE7A46","semantic":"same target-native signed-12 quantity exposed by Techstream DID 0x1037 Steering Angle","confidence":"verified dataflow + official name"},
            {"wire":"B5","source":"FEBE6554 -> *100/0x100 -> /10 -> signed-byte saturation","semantic":"same native source as Techstream DID 0x1035 Steering Wheel Torque; exact physical B5 scaling not yet promoted","confidence":"verified dataflow + official name"},
            {"wire":"B6:B7","source":"FEBE6592 * -100 / 0x80, big-endian signed16","semantic":"exact sign-inverted raw quantity used by DID 0x1151 Motor Actual Current (Q Axis), unit A; motor-current response, not assumed old STEER_TORQUE_EPS","confidence":"verified dataflow + official name"},
          ],
          "openpilot_consequence":"0x4A3 can supply generation-native angle, driver-torque-source, and motor-response observables before 0x030 is fully decoded; Panda limits/scales must be derived for this generation.",
        },
        "0x351": {
          "classification":"structural continuity of EPS plausibility/debounce status carrier",
          "length":4,"pdu":1,
          "wire":"B2[7:5] = FEBE7DD0; B2[4] = FEBE7DD1",
          "producer":"0x46E62 forces status code 7 and flag 1 under its active gate; 0x46E0C retains the old seven-count hold/debounce architecture",
          "boundary":"The H upstream boolean/state source is not given an old OEM semantic name solely from structural similarity.",
          "openpilot_consequence":"Useful readiness/inhibit candidate and dynamic correlation target; do not hard-code it as LKA_STATE yet.",
        },
        "0x394": {
          "classification":"strong EPS internal status/fault-family carrier",
          "length":3,"pdu":2,
          "producer":"0x46E96 projects internal FEBE7F58 class plus FEBE7F65/62/63/64 staging state",
          "wire":"B1[7:6]=7DD5; B1[5:3]=7DD6; B2[3:1]=7DD7; B2[0]=7DD9",
          "boundary":"Exact H code meanings and old 0x262 LKA_STATE numeric values are unresolved/non-portable.",
          "openpilot_consequence":"Primary candidate for generation-native steering readiness/fault state; correlate against Techstream DTCs and stock-LTA transitions.",
        },
        "0x030": {
          "classification":"mixed 32-byte FD EPS telemetry/status/validity carrier; still requires field recovery",
          "length":32,"pdu":0,
          "configured_signals":fd["fd_0x030_transmit"]["configured_signal_ids"],
          "direct_packed_signals":fd["fd_0x030_transmit"]["direct_packer_signal_ids"],
          "additive_field":fd["fd_0x030_transmit"]["checksum_like_signal_9"],
          "openpilot_consequence":"Decode remaining validity/control-state fields after exploiting the clearer 0x4A3/0x351/0x394 bridges; do not assume it is a monolithic 0x260+0x262 replacement.",
        },
      },
      "command_ingress_closure": {
        "generated_scalar_rx_calls":ingress["summary"]["h_scalar_rx_calls"],
        "supervisor_external_signals":ingress["summary"]["external_signals"],
        "supervisor_reaching_ge12bit_fields":[{"can_id":"0x025","signal_id":184,"bits":12},{"can_id":"0x025","signal_id":186,"bits":12},{"can_id":"0x0B6","signal_id":255,"bits":16}],
        "fixed_map_correction_recovered_b6_target": True,
        "protected_0x0D7":pb["d7"]["interpretation"],
        "protected_0x0B6_techstream_boundary":pb["b6"]["interpretation"],
        "b6_target_angle": {
          "mode_signal_id": target["mode_ingress"]["signal_id"],
          "mode_wire_byte": target["mode_ingress"]["wire_byte"],
          "decoded_mode_values": target["mode_ingress"]["decoded_values"],
          "can_id": target["wire_ingress"]["can_id"],
          "signal_id": target["wire_ingress"]["signal_id"],
          "wire_byte": target["wire_ingress"]["wire_byte"],
          "bit_length": target["wire_ingress"]["bit_length"],
          "signed": target["wire_ingress"]["signed"],
          "snapshot": target["wire_ingress"]["snapshot_destination"],
          "classification": target["wire_ingress"]["classification"],
          "target_vs_measured_loop": target["measured_angle_feedback"]["classification"],
          "physical_scale_closed": target["scaling"]["physical_degree_scale_closed"],
          "controller_equivalent_deg_per_count": target["scaling"]["controller_equivalent_deg_per_b6_count"],
          "controller_equivalent_mrad_per_count": target["scaling"]["controller_equivalent_mrad_per_b6_count"],
          "oem_wire_unit_name_closed": target["scaling"]["oem_wire_unit_name_closed"],
          "mode_profile_semantics": target["mode_ingress"]["profile_semantics"],
          "immediate_sender_relationship": target["static_conclusion"]["immediate_sender_relationship"],
          "request_selection_closed": lta_static["request_selection_identified"],
          "receiver_loss_cutout_ticks": lta_static["receiver_loss_cutout_ticks"],
          "wall_clock_timeout_closed": lta_static["wall_clock_timeout_identified"],
          "sequence_modulus": lta_static["sequence_modulus"],
          "sequence_gap_cap": lta_static["sequence_gap_cap"],
        },
        "brake_domain_conclusion":pb["conclusion"],
        "old_camera_interface_removed":ipm["interpretation"],
        "computed_retained_branch": {
          "classification": lta["retained_lta_branch"]["classification"],
          "mode_enable_writer": lta["retained_lta_branch"]["computed_writer_correction"]["mode_enable_0xFEBEC26D"]["writer"],
          "magnitude_writer": lta["retained_lta_branch"]["computed_writer_correction"]["replicated_magnitude_0xFEBEC17C_17E_184"]["writer"],
          "b6_modulator_signal_ids": [x["signal_id"] for x in lta["retained_lta_branch"]["computed_writer_correction"]["b6_modulators"]],
          "statically_dead": lta_static["retained_sienna_lta_branch_statically_dead"],
          "command_sized_wire_scalar_recovered": lta_static["h_only_or_wire_changed_command_sized_scalar_recovered"],
        },
        "static_conclusion":"Protected CAN-FD 0x0B6 signal255 is the recovered H/F external target-steering-angle ingress. The direct-reference-only supervisor census missed it because FEBEF1CC is copied to FEBEAE82 through GP-relative RTE code. FD 0x025 feedback is exactly 1.5 deg/coarse count plus a signed 0.1-deg fractional nibble, and the matched controller closes signal255 at 1024/17870 deg/count (~1.000121519 mrad/count) controller-equivalent scale. Signal254 selects five accepted cooperative-control profiles with distinct calibration banks; Techstream Target Lateral ID closes them as 1=PCS, 4=LDA, 10=Hands Off LTA, 11=LTA/LCA, and 19=PDA. Techstream identifies the immediate monitored sender relationship as Brake System Control Module. Signal254 request selection, a seven-foreground-tick primary receiver-loss cutoff, and modulo-64 sequence handling with gap cap 8 are also closed. The OEM signal255 unit label, wall-clock sender cadence, exact secondary B6 field names, and upstream FRC_P5 -> Brake/EPB producer/authentication route remain open.",
      },
      "structural_corroboration":structural,
      "next_discriminators":[
        "Treat signal254 request selection, the 7-tick receiver deadline, and modulo-64 sequence rules as closed receiver requirements; recover wall-clock sender cadence and exact secondary-field names only if needed for safety validation.",
        "Acquire/analyze true-TSS3 FRC_P5 and Brake/EPB producer/Tx descriptors or synchronized captures to close the upstream FRC -> chassis -> EPS route and authentication contract.",
        "Derive H-native driver override, motor-response, readiness/fault, rate and message-loss limits before defining Panda safety; do not reuse old 0x260/0x262 scales or fault codes.",
      ],
    }


def main() -> int:
    ap=argparse.ArgumentParser()
    ap.add_argument('--out',type=Path,default=OUT)
    args=ap.parse_args()
    report=build(); args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
    print(json.dumps({'out':str(args.out),'schema':report['schema']},indent=2))
    return 0

if __name__=='__main__': raise SystemExit(main())
