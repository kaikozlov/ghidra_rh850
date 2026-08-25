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
ENG_EVID = REPO / "data/generated/corolla_8965H1202000_nonsteering_engagement_decompiler_evidence.json"
TECH = REPO / "data/generated/corolla_8965H1202000_techstream_correlations.json"
FD = REPO / "data/generated/corolla_8965H1202000_fd_control_interface.json"
DIAG_EVID = REPO / "data/generated/corolla_8965H1202000_application_diagnostic_decompiler_evidence.json"
SPAN = REPO / "data/generated/corolla_2025_span_discord_rlog_opendbc_evidence.json"
SIENNA = REPO / "firmware/RH850_P1M-E_CodeFlash.bin"
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
    eng_evid = json.loads(ENG_EVID.read_text())
    tech = json.loads(TECH.read_text())
    fd = json.loads(FD.read_text())
    diag_evid = json.loads(DIAG_EVID.read_text())
    span = json.loads(SPAN.read_text())
    sienna = SIENNA.read_bytes()
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
    if evid["schema"] != "corolla-h-openpilot-state-bridge-decompiler-evidence-v2" or evid["function_count"] != 26:
        raise ValueError("H steering-state compact evidence schema/count drift")
    if eq["application_equivalence"]["different_bytes"] != 0:
        raise ValueError("H/F application equivalence drift")
    if eng_evid["schema"] != "corolla-h-nonsteering-engagement-decompiler-evidence-v1" or eng_evid["function_count"] != 6:
        raise ValueError("H non-steering engagement compact evidence schema/count drift")
    if eng_evid["image"]["sha256"] != sha(image):
        raise ValueError("H non-steering engagement evidence image drift")

    f = fnmap(evid)
    ef = fnmap(eng_evid)
    for row in [*evid["functions"], *eng_evid["functions"]]:
        start = int(row["entry"], 16); size = row["body_size"]
        if sha(image[start:start+size]) != row["body_sha256"]:
            raise ValueError(f"raw body drift {row['entry']}")

    cgear = ef[0x45EDE]["decompiled_c"]
    cready = ef[0x46144]["decompiled_c"]
    cready_stage = ef[0x5262C]["decompiled_c"]
    cready_copy_secondary = ef[0xBAB58]["decompiled_c"]
    cready_copy_primary = ef[0xBAC16]["decompiled_c"]
    cready_publish = ef[0xBBA48]["decompiled_c"]
    need(cgear,
         "FUN_0007643a(0x7b,0xd7,6,2,0,",
         "FUN_0007643a(0x7d,0xd8,1,3,0,",
         "FUN_0007643a(0x81,0xda,0xb,0,1,0xfebe7cfc);")
    need(cready, "FUN_0007643a(0x9a,0xf7,1,7,0,0xfebe7d1b);")
    need(cready_stage, "uRamfebef052 = uRamfebe7d1b;")
    need(cready_copy_secondary, "uVar1 = uRamfebef052;", "*(undefined1 *)(iVar3 + -600) = uVar1;")
    need(cready_copy_primary, "cRamfebeb5a8 = cRamfebef052;")
    need(cready_publish, "uRamfebee811 = uRamfebeb5a8;")

    c3738c=f[0x3738C]["decompiled_c"]
    c46c4c=f[0x46C4C]["decompiled_c"]; c46d9a=f[0x46D9A]["decompiled_c"]; c4749a=f[0x4749A]["decompiled_c"]
    c46e0c=f[0x46E0C]["decompiled_c"]; c46e62=f[0x46E62]["decompiled_c"]; c47ba2=f[0x47BA2]["decompiled_c"]
    c46e96=f[0x46E96]["decompiled_c"]; c47ada=f[0x47ADA]["decompiled_c"]; c472e0=f[0x472E0]["decompiled_c"]
    c4b692=f[0x4B692]["decompiled_c"]; c4b9ae=f[0x4B9AE]["decompiled_c"]
    cb87e8=f[0xB87E8]["decompiled_c"]; cbba48=f[0xBBA48]["decompiled_c"]
    c5262c=f[0x5262C]["decompiled_c"]; cbac16=f[0xBAC16]["decompiled_c"]; c6387c=f[0x6387C]["decompiled_c"]
    need(c46c4c, "sRamfebe7e22 = (short)((sRamfebe6554 * 100) / 0x100);", "uRamfebe7e28 = (undefined2)((sRamfebe6592 * -100) / 0x80);", "uRamfebe7db2 = (char)uVar1;", "cRamfebee886 != '\\0'", "if (uVar1 == 1)", "sRamfebe7e22 = 0;")
    need(c46d9a, "uRamfebe7ddd = (undefined1)uRamfebe7d34;", "FUN_00069420((int)sRamfebe7a46", "FUN_0006387c((int)(*(short *)(iVar1 + -0x39de) / 10)")
    need(c4749a, "uRamfebe88f6 = uRamfebe7ddb;", "FUN_0007662e(0x2b,0x27,8,0", "FUN_0007662e(0x32,0x2e,8,0")
    need(c46e0c, "bRamfebe7dfb = bRamfebe7dfb + 1;", "DAT_0002b930", "cRamfebee82b")
    need(cb87e8, "thunk_FUN_0004c3c8(4,0x32);", "bVar2 = cVar11 == 'Z';", "*(bool *)(iVar3 + -0x2ec) = bVar2;")
    need(cbba48, "uRamfebee82b = uRamfebeb514;", "uRamfebee811 = uRamfebeb5a8;")
    need(c46e62, "param_1 = 7;", "uRamfebe7dd1 = 1;", "uRamfebe7dd0 = param_1;")
    need(c47ba2, "FUN_000764ec(0x25,0x22,3,5", "FUN_000764ec(0x26,0x22,1,4")
    need(c46e96, "uVar1 = bRamfebe7f58 - 1;", "uRamfebe7dd5 = uRamfebe7f65;", "uRamfebe7dda = 3;")
    need(c4b692, "param_1 == '\\x02'", "param_1 == '\\x0f'", "param_1 == '\\x10'", "param_1 == '@'")
    need(c4b9ae, "uVar18 = 1;", "uVar18 = 2;", "uVar18 = 3;", "uVar18 = 0xf;", "uVar18 = 0x10;", "(&DAT_00029d54)[iVar21]")
    need(c3738c, "FUN_000472e0(uVar6);", "param_1 & 0x8000")
    need(c472e0, "uRamfebe7e13 = param_1;")
    need(c5262c, "uRamfebef052 = uRamfebe7d1b;")
    need(cbac16, "cRamfebeb5a8 = cRamfebef052;")
    need(c47ada, "FUN_000764ec(0x27,0x25,2,6", "FUN_000764ec(0x28,0x25,3,3", "FUN_000764ec(0x29,0x26,3,1", "FUN_000764ec(0x2a,0x26,1,0")
    need(c6387c, "uVar1 = 0x7f;", "iVar2 = -0x80;", "uVar1 = 0x81;")

    # DID 0x1035's callback lives in the independently tracked application-
    # diagnostic evidence rather than the corrected-context state corpus. Keep
    # those provenance buckets separate while pinning the exact native scaling.
    if diag_evid["schema"] != "rh850-variant-application-diagnostic-decompiler-evidence-v1" or diag_evid["image"]["sha256"] != sha(image):
        raise ValueError("H diagnostic callback evidence identity drift")
    did1035_rows = [row for row in diag_evid["functions"] if row["entry"] == "0x00048820"]
    if len(did1035_rows) != 1:
        raise ValueError(f"DID 0x1035 callback evidence count drift: {len(did1035_rows)}")
    did1035 = did1035_rows[0]
    did1035_start = int(did1035["entry"], 16)
    if sha(image[did1035_start:did1035_start + did1035["body_size"]]) != did1035["body_sha256"] or sha(did1035["decompiled_c"].encode()) != did1035["decompiled_c_sha256"]:
        raise ValueError("DID 0x1035 callback evidence drift")
    need(did1035["decompiled_c"], "aiStack_c[0] = (sRamfebe6554 * 1000) / 0x100;", "FUN_0006943a(aiStack_c[0],25000,0xffff9e58,aiStack_c);", "FUN_0006385c(iVar1,param_1);")

    # H's actual 0x394 classifier indexes a 17x5-byte state projection table.
    # The homologous Sienna table is byte-identical, but state meanings below are
    # taken from the H classifier itself rather than transplanted DBC labels.
    expected_state_table = [
        [0,0,0,0,0], [4,3,0,0,0], [4,7,0,0,0], [5,3,0,0,0],
        [4,3,0,0,0], [1,1,0,0,0], [3,3,2,1,2], [3,3,2,1,0],
        [6,3,3,0,2], [6,3,3,0,0], [3,7,1,1,1], [3,7,4,1,1],
        [6,7,7,0,1], [6,7,6,0,1], [6,7,5,0,1], [2,2,0,0,0],
        [4,7,0,0,0],
    ]
    h_state_table = [list(image[0x29D54+i*5:0x29D54+(i+1)*5]) for i in range(17)]
    s_state_table = [list(sienna[0x2A33C+i*5:0x2A33C+(i+1)*5]) for i in range(17)]
    if h_state_table != expected_state_table or s_state_table != expected_state_table:
        raise ValueError("0x394 classifier state-table drift")
    # Raw H branch window for the final state-15/state-0/state-16 decision. The
    # exact RH850 instructions prove failed operational predicates branch to
    # 0x4BB48 (MOV 0x10,r1), while only the fully passing path reaches 0x4BB4C
    # with r1 still zero from the preceding ANDI. Pin this independently of
    # decompiler nesting so state 0 cannot be promoted from an ambiguous goto.
    state0_cfg_start, state0_cfg_end = 0x4BB16, 0x4BB50
    state0_cfg = image[state0_cfg_start:state0_cfg_end]
    expected_state0_cfg_hex = "a35f0300615aea051806a6ffb2050f0ab5151906a6ffea0d1706a6ffb20d1406a6ff820da35f01000b06a6ffb205e0a9b205200e1000e1f60500"
    if state0_cfg.hex() != expected_state0_cfg_hex:
        raise ValueError("0x394 state-0 final branch window drift")
    if image[0x2B930] != 7:
        raise ValueError("0x351 seven-count hold calibration drift")

    pdu = [PDU.unpack_from(image, 0x22620 + i*PDU.size) for i in range(5)]
    if pdu != [(2,0,0,32,0,3),(200,0,0,4,0,3),(60,0,0,3,0,3),(100,0,0,8,0,3),(196,0,0,8,0,3)]:
        raise ValueError(f"Tx PDU descriptor drift: {pdu}")

    m15=monitor(tech,15); m17=monitor(tech,17); q=tech["motor_current_bridge"]["techstream_monitors"]["251"]
    bridge_diag=tech["steering_state_bridge_diagnostics"]
    torque_sem=bridge_diag["steering_wheel_torque"]
    ready_sem=bridge_diag["ready_status_oracle"]
    d351=bridge_diag["0x351_motor_b_terminal_voltage_monitor"]["dtc"]
    span030=span["direct_reuse_evidence"]["0x030"]
    span030_bridge=span030["steering_state_bridge"]
    span_torque=span030_bridge["steering_wheel_torque"]
    span_ready=span["direct_reuse_evidence"]["0x51E"]
    if (m15["name"],m15["primary_data_id"],m15["h_callback"]) != ("Steering Wheel Torque","0x1035","0x48820"):
        raise ValueError("Steering Wheel Torque Techstream join drift")
    if (m17["name"],m17["primary_data_id"],m17["h_callback"]) != ("Steering Angle","0x1037","0x488A8"):
        raise ValueError("Steering Angle Techstream join drift")
    if (q["name"],q["primary_data_id"],q["unit"]) != ("Motor Actual Current (Q Axis)","0x1151","A"):
        raise ValueError("Q-current Techstream join drift")
    if not (q["signed"] and q["mul"] == q["div"] == 1 and q["offset"] == 0 and q["decimal_point_count"] == 2):
        raise ValueError("Q-current physical conversion drift")
    if not (torque_sem["name"] == "Steering Wheel Torque" and torque_sem["unit"] == "Nm" and torque_sem["signed"] and torque_sem["decimal_point_count"] == 3 and torque_sem["mul"] == torque_sem["div"] == 1):
        raise ValueError("steering-wheel-torque physical conversion drift")
    if not (d351["dem_event"] == "0x0004" and d351["h_dtc_index"] == 54 and d351["techstream_code"] == "C159B49" and d351["enabled_word"] == 1):
        raise ValueError("0x351 event/DTC semantic join drift")
    if not (ready_sem["name"] == "Ready Status" and ready_sem["primary_data_id"] == "0x1033" and ready_sem["source_chain"][:4] == ["0xFEBE7D1B","0xFEBEF052","0xFEBEB5A8","0xFEBEE811"]):
        raise ValueError("Ready Status diagnostic oracle drift")
    if not (span_ready["frame_count"] == 60 and span_ready["ready_status_values"] == [1]):
        raise ValueError("Span 0x51E Ready Status operational-state evidence drift")
    if not (span030["frame_count"] == span030["rule_matches"] == 6000 and span030_bridge["steering_fault_inhibit_status"]["values"] == [0] and span030_bridge["driver_torque_invalid"]["values"] == [0]):
        raise ValueError("Span 0x030 nominal steering-state bridge drift")
    if not (span_torque["torque_nm"]["count"] == 6000 and span_torque["fine_values"] == [-5,-4,-3,-2,-1,0,1,2,3,4,5] and span_torque["coarse_rounding_delta_values"] == [-1,0,1]):
        raise ValueError("Span 0x030 driver-torque decode drift")
    if fd["schema"] != "corolla-8965H1202000-fd-control-interface-v2":
        raise ValueError("H FD/control interface schema drift")
    fd030_rows = {row["signal_id"]: row for row in fd["fd_0x030_transmit"]["fields"]}
    gp030 = fd["fd_0x030_transmit"]["gp_relative_writer_correction"]
    if gp030["affected_signal_ids"] != [0,1,10,14,16,17,18,27,28,31,34]:
        raise ValueError("H 0x030 GP-relative writer correction drift")
    if any(fd030_rows[x]["writer_class"] != "runtime-produced-gp-relative" for x in gp030["affected_signal_ids"]):
        raise ValueError("H 0x030 corrected writer classification drift")

    matches={int(x["target_entry"],16):x for x in struct["matches"]}
    structural={}
    for target_entry, role in ((0x46C4C,"0x030/0x4A3 state and telemetry source preparation"),(0x46D9A,"0x4A3 staging"),(0x4749A,"0x4A3 packer"),(0x46E0C,"0x351 debounce"),(0x46E62,"0x351 producer"),(0x47BA2,"0x351 packer"),(0x46E96,"0x394 state projection"),(0x4B9AE,"0x394 17-state classifier")):
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
      "schema":"corolla-8965H1202000-openpilot-state-bridge-v8",
      "evidence_boundary": (
        "Exact H bytes and target-native decompiler/Techstream joins define the newer EPS state carriers. "
        "Sienna/openpilot structures are used only to identify which roles a port needs, not to transplant field scales or fault codes. "
        "The command side is additionally audited for GP-relative/computed writers: protected B6 signal255 is recovered through a hidden RTE snapshot as a signed16 target-steering-angle command, then compared against independently reconstructed 0x025 measured angle before entering the steering controller. "
        "Physical B6 scaling and OEM mode/request semantics are closed, as are the seven-tick receiver-loss cutoff and modulo-64 sequence handling; wall-clock cadence, exact secondary B6 field names, and the upstream producer/authentication route remain bounded; no second command-sized generated scalar or recovered literal block/group/full-PDU route is identified, while arbitrary computed aliases and DMA/peripheral mutation remain outside this proof."
      ),
      "evidence_sources": {
        "state_corpus": {"path": str(EVID.relative_to(REPO)), "sha256": sha(EVID.read_bytes())},
        "did_0x1035_callback": {"path": str(DIAG_EVID.relative_to(REPO)), "sha256": sha(DIAG_EVID.read_bytes()), "entry": "0x00048820"},
      },
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
          "classification":"generation-native steering telemetry bridge; driver torque and actuator response closed statically",
          "length":8,
          "pdu":3,
          "fields":[
            {"wire":"B0[5]","source":"constant 1 from FEBE7DAE | 0x20","semantic":"constant marker bit","confidence":"verified dataflow"},
            {"wire":"B0[0]","source":"FEBE7DAE","semantic":"selected steering fault/inhibit status aggregate; same source is 0x030 B6[2]; not an exhaustive EPS-fault state","confidence":"verified dataflow + Span nominal polarity through duplicate 0x030 carrier"},
            {"wire":"B1:B2","source":"FEBE7D34 from FD 0x025 signal184","semantic":"mirror of the target-native signed-12 steering-angle sensor field","physical_scale":"1.5 deg/count","confidence":"verified dataflow + Techstream angle conversion"},
            {"wire":"B3:B4","source":"FEBE7A46","semantic":"same target-native signed-12 quantity exposed by Techstream DID 0x1037 Steering Angle","physical_scale":"1.5 deg/count","confidence":"verified dataflow + official name/conversion"},
            {"wire":"B5","source":"FEBE6554 -> trunc(*100/0x100) -> trunc(/10) -> signed-byte saturation","semantic":"Steering Wheel Torque","techstream_did":"0x1035","unit":"Nm","packet_scale":0.1,"packet_scale_unit":"Nm/count","quantization":"two-stage truncation before signed-byte saturation; packet is the native torque source quantized to intended 0.1 N.m/count","confidence":"verified dataflow + official name/conversion"},
            {"wire":"B6:B7","source":"FEBE6592 * -100 / 0x80, big-endian signed16","semantic":"Motor Actual Current (Q Axis)","techstream_did":"0x1151","unit":"A","packet_scale":-0.01,"packet_scale_unit":"A/count","sign_note":"packet signed integer is the sign-inverted Techstream raw integer; Techstream uses two displayed decimals","confidence":"verified dataflow + official name/conversion"},
          ],
          "dynamic_boundary":"Span's moving route contains zero 0x4A3 frames, so the packet fields are firmware/Techstream-static rather than route-validated. The duplicated FEBE7DAE selected steering fault/inhibit status bit is dynamically nominal-clear through 0x030.",
          "openpilot_consequence":"Generation-native driver torque and actuator-response observables are closed without old 0x260 semantics. They can feed a future Panda safety model once relay-correct routing/availability is captured; absence from the current route prevents using them as required CarState inputs today.",
        },
        "0x351": {
          "classification":"mixed EPS status carrier with a C159B49-linked motor-B electrical-monitor path plus a separate force-7 override",
          "length":4,"pdu":1,
          "wire_fields":[
            {"wire":"B2[7:5]","source":"FEBE7DD0","semantic":"mixed status code: normally propagates the FEBEB514/FEBEE82B monitor boolean through 0x46E0C; 0x46E62 separately forces code 7 when (FEBE65E4 & 3) != 0 and FEBE7E13 != 0"},
            {"wire":"B2[4]","source":"FEBE7DD1","semantic":"exact force-7 indicator: 1 iff (FEBE65E4 & 3) != 0 and FEBE7E13 != 0; otherwise 0"},
          ],
          "producer_chain":[
            "0xB87E8 computes the C159B49-linked electrical-monitor predicate, reports Dem event 4 on assertion, and stores its boolean at GP-0x2EC = FEBEB514",
            "0xBBA48 copies FEBEB514 -> FEBEE82B; 0x46E0C propagates that monitor boolean while maintaining the exact seven-count transition state using calibration byte 0x2B930 = 7",
            "independently, 0x3738C -> 0x472E0 supplies FEBE7E13 from its param_1 bit15 path",
            "0x46E62 stages the mixed result: normally param_1 into FEBE7DD0, but force-writes code 7 plus FEBE7DD1=1 when (FEBE65E4 & 3) != 0 and FEBE7E13 != 0; 0x47BA2 packs B2[7:5]/B2[4]",
          ],
          "diagnostic_join":d351,
          "boundary":"C159B49 names one upstream electrical-monitor path feeding 0x351; it does not name the whole packet or the separate force-7 condition. 0x351 is not a generic LKA/EPS-ready state, and its numeric status codes must not be transplanted into old 0x262 LKA_STATE meanings.",
          "dynamic_boundary":"Span and the public TSS3 route contain zero 0x351 frames, so packet availability and asserted-state transitions remain uncaptured.",
          "openpilot_consequence":"Treat 0x351 as mixed generation-native status. Its C159B49-linked path and force-7 override must be correlated separately before either is used for safety; remove it from the generic readiness-candidate bucket.",
        },
        "0x394": {
          "classification":"generation-native 17-state EPS fault/status classifier with a recovered deepest clear/normal state",
          "length":3,"pdu":2,
          "classifier_entry":"0x0004B9AE",
          "projection_entry":"0x00046E96",
          "state_table_address":"0x00029D54",
          "state_table_rows":h_state_table,
          "sienna_homolog_table_address":"0x0002A33C",
          "sienna_table_byte_identical":h_state_table == s_state_table,
          "state0_final_branch_window":{
            "start":"0x0004BB16",
            "end_exclusive":"0x0004BB50",
            "raw_hex":state0_cfg.hex(),
            "sha256":sha(state0_cfg),
            "control_flow":"state 15 branches directly to 0x4BB4C; each failed final state-0 operational predicate branches to 0x4BB48 where MOV 0x10,r1 selects state 16; only the fully passing path branches from 0x4BB46 to 0x4BB4C with r1 still 0",
            "boundary":"instruction-level proof of the state-0 gating only; it does not assign OEM names to the individual predicates or equate state 0 with Techstream Ready Status",
          },
          "wire_projection":{
            "B1[7:6]":"table column 4 via FEBE7F65 -> FEBE7DD5",
            "B1[5:3]":"table column 1 via FEBE7F62 -> FEBE7DD6",
            "B2[3:1]":"table column 2 via FEBE7F63 -> FEBE7DD7",
            "B2[0]":"table column 3 via FEBE7F64 -> FEBE7DD9",
            "not_on_0x394":"table column 0 is staged through FEBE7F66/FEBE7DD2; the separate coarse class FEBE7DDA is not packed by 0x47ADA",
          },
          "classifier_states":{
            "0":{"role":"deepest clear/normal classifier path","evidence":"deepest H classifier path leaves uVar18=0 only after the preceding aggregated fault-class branches are clear and additional operational predicates pass; this is not equivalent to a proved EPS Ready boolean"},
            "1":{"role":"startup/settling hold A"},
            "2":{"role":"startup/settling hold B"},
            "3":{"role":"internal input invalid/unavailable branch"},
            "4":{"role":"retained table row; not directly selected by the recovered H classifier body"},
            "5":{"role":"retained table row; not directly selected by the recovered H classifier body"},
            "6-14":{"role":"active fault/inhibit classifier branches sourced from the Dem event-class aggregate/latches"},
            "15":{"role":"special operating state","boundary":"selected by a distinct operational predicate, not safely nameable as ready or fault from static evidence alone"},
            "16":{"role":"fallback/not-normal operational inhibit branch"},
          },
          "dem_class_aggregator":"0x4B692 accumulates event classes/counters consumed by 0x4B9AE; the branches cover real EPS processor, power, motor, sensor, communication, and compatibility fault families",
          "openpilot_fault_mapping":{
            "classifier_deepest_clear_normal_state":0,
            "conservative_clear_state_candidate":"state 0 only, pending packet routing plus Ready/LTA dynamic correlation; state 0 alone is not sufficient to authorize actuation",
            "steerFaultTemporary":"unresolved",
            "steerFaultPermanent":"unresolved",
            "reason":"Firmware distinguishes startup, live/latched/aged fault classes and a special state 15, but no evidence maps those distinctions to openpilot's temporary/permanent fault contract. Guessing would be unsafe.",
          },
          "dynamic_boundary":"Span and the public route contain zero 0x394 frames; the state-0 clear/normal path and fault branches are statically recovered but not observed on-vehicle in the available captures.",
          "openpilot_consequence":"This recovers a native deepest-clear/normal versus fault-family discriminator candidate, but not a Ready authorization bit or temporary/permanent CarState fault labels. A future relay-correct capture should correlate raw 0x394 states against EPS Ready Status, DTC transitions and stock LTA enable/disable.",
        },
        "0x030": {
          "classification":"live generation-native EPS telemetry/status/validity carrier with driver torque and two safety-relevant gates closed",
          "length":32,"pdu":0,
          "configured_signals":fd["fd_0x030_transmit"]["configured_signal_ids"],
          "direct_packed_signals":fd["fd_0x030_transmit"]["direct_packer_signal_ids"],
          "additive_field":fd["fd_0x030_transmit"]["checksum_like_signal_9"],
          "steering_state_fields":[
            {"signal_id":6,"wire":"B6[2]","source":"FEBE7DAE","semantic":"selected steering fault/inhibit status aggregate; duplicated as 0x4A3 B0[0]; not an exhaustive EPS-fault state","span_values":span030_bridge["steering_fault_inhibit_status"]["values"],"span_clear_frames":span030_bridge["steering_fault_inhibit_status"]["clear_frames"]},
            {"signal_id":8,"wire":"B6[0]","source":"FEBE7DB2","semantic":"driver-torque invalid/inhibit gate; the same producer condition forces FEBE7E22 driver torque to zero","span_values":span030_bridge["driver_torque_invalid"]["values"],"span_clear_frames":span030_bridge["driver_torque_invalid"]["clear_frames"]},
            {"signal_id":7,"wire":"B6[1]","source":"FEBE7DB3 <- FEBEE848","semantic":"live status bit; exact steering meaning unresolved","span_values":span030_bridge["b6_bit1"]["values"]},
            {"signal_id":5,"wire":"B6[3]","source":"FEBE7E09","semantic":"runtime status bit; exact steering meaning unresolved","span_values":span030_bridge["b6_bit3"]["values"]},
          ],
          "gp_relative_runtime_fields":[
            {"signal_id":x,"wire":f"B{fd030_rows[x]['wire_byte']} bit{fd030_rows[x]['bit_offset']} len{fd030_rows[x]['bit_length']}","source":fd030_rows[x]["source"],"writer":fd030_rows[x]["nondefault_writer_functions"][0],"semantic":fd030_rows[x]["recovered_semantic"]}
            for x in gp030["affected_signal_ids"]
          ],
          "driver_torque_encoding_family":{
            "signal_ids":[0,10,31],
            "native_source":"FEBE6554 through the same transformed/saturated torque intermediate used by 0x4A3 B5 and Techstream DID 0x1035",
            "physical_reconstruction":"Steering Wheel Torque [N.m] = signal10_signed * 0.1 + signal31_signed4 * 0.01; signal0_signed is a separate truncation-toward-zero 0.1 N.m view",
            "coarse_rounding_delta_values":span_torque["coarse_rounding_delta_values"],
            "span_torque_nm":span_torque["torque_nm"],
            "classification":"exact firmware/Techstream physical decode of live 0x030 Steering Wheel Torque; signals10+31 reconstruct the native intermediate exactly and signal0 is a bounded coarse view",
          },
          "q_current_derived_field":{
            "signal_id":34,
            "source":"FEBE6592 Motor Actual Current (Q Axis)",
            "classification":"runtime signed16 calibrated derivative with sign inversion; source semantics are closed but exact packet engineering scale remains calibration-dependent",
          },
          "span_dynamic":{"frame_count":span030["frame_count"],"additive_rule_matches":span030["rule_matches"],"byte16_values":span030_bridge["byte16_values"]},
          "boundary":"The available moving log proves 0x030 is live and both safety-relevant gates are clear in all 6,000 nominal frames. The prior direct-reference writer census was incomplete: eleven additional fields have exact GP-relative runtime writers, including a redundant driver-torque representation and a Q-current-derived field. It contains no induced fault or stock-LTA transition, so asserted-state operational consequences remain firmware-static and temporary/permanent fault semantics remain unresolved.",
          "openpilot_consequence":"0x030 can immediately supply physical driver steering torque, nominal selected steering fault/inhibit status, and driver-torque-validity state to the read-only measurement harness without making unseen 0x4A3/0x394/0x351 mandatory for CAN validity.",
        },
        "ready_status_input_0x51E":{
          "can_id":"0x51E",
          "length":8,
          "firmware_signal_id":154,
          "wire":"B0[7]",
          "raw_destination":"0xFEBE7D1B",
          "did":"0x1033",
          "name":"Ready Status",
          "source_chain":["0x51E B0[7]", *ready_sem["source_chain"]],
          "firmware_chain_verified":True,
          "span_operational_frames":span_ready["frame_count"],
          "span_values":span_ready["ready_status_values"],
          "boundary":"Exact H proves the incoming CAN field that feeds Techstream Ready Status. Neither retained route exercises value 0, and this does not imply that any EPS Tx PDU republishes the same boolean.",
          "openpilot_consequence":"0x51E B0[7] can be parsed as the target-native Ready Status input. Keep it distinct from 0x030/0x351/0x394 steering-fault state, and validate a Ready 1->0 transition before using it as an engagement/fault classifier.",
        },
      },
      "carstate_and_panda_input_closure": {
        "driver_steering_torque":"closed and live on 0x030 signals10+31 with exact N.m reconstruction; 0x4A3 B5 is a statically closed 0.1 N.m/count alternate carrier not present on current routes",
        "motor_actuator_response":"closed statically at 0x4A3 B6:B7 as sign-inverted DID 0x1151 Motor Actual Current (Q Axis), -0.01 A/count, but current routes do not carry 0x4A3",
        "steering_fault_inhibit_status":"selected steering fault/inhibit status closed on live 0x030 B6[2] and duplicated in 0x4A3 B0[0]; Span nominal-clear 6000/6000; not an exhaustive EPS-fault state",
        "driver_torque_validity":"closed on live 0x030 B6[0]; Span nominal-clear 6000/6000 and asserted firmware state zeroes driver-torque telemetry",
        "electrical_motor_fault":"the 0x351 base-status path is statically joined through FEBEB514/FEBEE82B to Dem event 4 -> C159B49, but 0x351 also has a separate force-7 override from FEBE65E4/FEBE7E13; route availability/asserted transitions are not captured",
        "eps_classifier_clear_normal_path":"0x394 state 0 is the deepest recovered clear/normal classifier path; it is not a proved Ready boolean, and route availability/transitions are not captured",
        "eps_ready":"closed as incoming 0x51E B0[7] -> FEBE7D1B -> FEBEF052 -> FEBEB5A8 -> FEBEE811 -> Techstream DID 0x1033 Ready Status; Span moving route carries value 1 on 60/60 frames, but Ready=0 transition remains uncaptured",
        "temporary_vs_permanent_fault":"not closed; no safe static mapping from 0x394 classes to openpilot steerFaultTemporary/steerFaultPermanent",
        "production_safety_boundary":"These results close most semantic input roles but do not authorize actuation. Panda safety still requires relay-correct message availability/side attribution, stock-LTA transitions, asserted fault captures, and validated control limits/suppression.",
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
        "Treat live 0x030 driver torque plus selected steering fault/inhibit/validity status, 0x4A3 Q-current response/alternate torque, the 0x351 C159B49-linked base path plus separate force-7 override, and the 0x394 state-0 deepest clear/normal classifier path as closed at their stated evidence grades; do not redo their basic producer recovery.",
        "Acquire a firmware-identified relay-correct H/F-family capture that actually carries 0x4A3/0x351/0x394 and exercises stock LTA off->active->off plus 0x51E Ready Status 1->0 and DTC transitions. This is required to close packet availability, state-15 meaning, and temporary/permanent CarState mapping; the Ready Status wire field itself is already closed.",
        "Acquire/analyze true-TSS3 FRC_P5 and Brake/EPB producer/Tx descriptors or synchronized captures to close the upstream FRC -> chassis -> EPS route, SecOC sender/freshness contract, suppression ownership, and production control limits.",
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
