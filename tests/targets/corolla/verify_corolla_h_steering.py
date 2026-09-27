#!/usr/bin/env python3
"""Portable Corolla H steering/control pins: FD control, nested and supervisor steering, LTA command provenance, motor control, direct-call surface, supervisor external ingress, and openpilot state bridge.

Domain split; assertions and helpers are carried over verbatim.
"""
from __future__ import annotations

import hashlib

from tools import REPO_ROOT
ROOT = REPO = REPO_ROOT
passed = failed = 0

def sha(data):
    return hashlib.sha256(data).hexdigest()

def check(name, cond, detail=''):
    global passed, failed
    ok = bool(cond)
    passed += int(ok)
    failed += int(not ok)
    suffix = f' ({detail})' if detail else ''
    print(f"[{'PASS' if ok else 'FAIL'}][raw_bytes] {name}{suffix}")


def _section_fd_control():
    print('== fd control ==')
    """Verify the 8965H1202000 FD/control-interface comparison."""

    import json

    REPO = REPO_ROOT
    ART = REPO / "data/generated/corolla_8965H1202000_fd_control_interface.json"
    EVIDENCE = REPO / "data/generated/corolla_8965H1202000_fd_control_decompiler_evidence.json"
    REFS = REPO / "data/generated/corolla_8965H1202000_fd_control_reference_census.json"
    STATE_EVIDENCE = REPO / "data/generated/corolla_8965H1202000_openpilot_state_bridge_decompiler_evidence.json"


    d = json.loads(ART.read_text())
    print("\n== FD receive generation ==")
    fd = d["fd_receive_generation"]
    check("Sienna FD Rx set is 025/090/D7", [x["can_id"] for x in fd["sienna_fd_rx"]] == ["0x025", "0x090", "0x0D7"])
    check("H FD Rx set adds only B6", [x["can_id"] for x in fd["corolla_h_fd_rx"]] == ["0x025", "0x090", "0x0D7", "0x0B6"])
    check("025 is explicitly classified as shared rather than H replacement",
          fd["shared_0x025_boundary"]["classification"] == "shared-preexisting-fd-interface-not-h-replacement")
    check("025 unpacker/producer/4A3 packer all have unique complete-shape transfers",
          len(fd["shared_0x025_boundary"]["unique_instruction_shape_pairs"]) == 3)
    check("H 025 signed12 field is still mirrored into 4A3 B1/B2",
          fd["shared_0x025_boundary"]["corolla_h_signed12_signal_184"]["directly_repacked_to_can_0x4A3_bytes"] == [1, 2])

    print("\n== secured FD B6 field roles ==")
    b6 = d["secured_fd_0x0b6"]
    check("B6 has 16 configured IDs but 12 scalar extracts",
          (len(b6["configured_signal_ids"]), len(b6["scalar_extracted_signal_ids"])) == (16, 12))
    check("B6 configured non-scalar IDs are 252/253/266/267",
          b6["configured_without_recovered_scalar_extract"] == [252, 253, 266, 267])
    by = {row["signal_id"]: row for row in b6["fields"]}
    check("B6 signal254 is 6-bit B3 mode/control ID", not by[254]["signed"] and by[254]["bit_length"] == 6 and by[254]["wire_byte"] == 3 and by[254]["snapshot_destination"] == "0xFEBEADB0" and by[254]["role"] == "target-lateral-control-id-mode-selector" and by[254]["direct_consumers"] == ["0xCBE6E"])
    check("B6 signal255 is signed16 at wire byte4", by[255]["signed"] and by[255]["bit_length"] == 16 and by[255]["wire_byte"] == 4)
    check("B6 signed16 field reaches AE82 target-angle snapshot",
          by[255]["role"] == "signed16-target-steering-angle-command" and by[255]["snapshot_destination"] == "0xFEBEAE82")
    check("B6 signed16 target-angle consumers are explicit", by[255]["direct_consumers"] == ["0xC86E8","0xC87FC","0xC9DB0","0xCB4F4"])
    check("B6 signed16 canonical result is target angle not torque", b6["signed16_target_angle_command"]["classification"] == "authenticated target-steering-angle command; not torque" and b6["signed16_target_angle_command"]["physical_scale_closed"] is True)
    check("B6 signed16 controller-equivalent scale is promoted", abs(b6["signed16_target_angle_command"]["controller_equivalent_deg_per_count"]-(1024/17870))<1e-15 and abs(b6["signed16_target_angle_command"]["controller_equivalent_mrad_per_count"]-1.0001215187701138)<1e-12 and b6["signed16_target_angle_command"]["oem_wire_unit_name_closed"] is False)
    check("B6 signal259 remains staging-only", by[259]["snapshot_destination"] is None)
    check("B6 signals256/257 reach snapshots but no recovered runtime consumer",
          all(by[x]["role"] == "snapshot-only-direct-xref-negative" for x in (256, 257)))
    check("B6 signal260 selects/ramp-controls mode tables", by[260]["role"] == "mode-table-selector" and "0xC89D2" in by[260]["direct_consumers"])
    check("B6 signal261 is a modulo/sequence delta input", by[261]["role"] == "modulo-sequence-delta" and by[261]["direct_consumers"] == ["0xCB246"])
    check("B6 8-bit signals262/263 are percentage-scaling inputs", by[262]["role"] == by[263]["role"] == "percentage-scaling")
    check("B6 signal264 is a validity/reset gate", by[264]["role"] == "validity-reset-gate")
    check("B6 signal265 is validity-gated mode/status", by[265]["role"] == "validity-gated-mode-status")
    check("active B6 consumers have target-native CEDAE paths where expected",
          all(by[x]["paths_from_0xCEDAE"][next(iter(by[x]["paths_from_0xCEDAE"]))] is not None for x in (258, 261, 262, 263, 264, 265)))
    check("B6 target-angle canonical proof linked", b6["signed16_target_angle_command"]["canonical_proof"] == "data/generated/corolla_8965H1202000_b6_target_angle_ingress.json" and b6["signed16_target_angle_command"]["physical_scale_closed"] is True)

    print("\n== Sienna-shaped steering-branch corrections ==")
    corr = d["sienna_shaped_branch_corrections"]
    check("AE20 is classified as internal-fed monitor/status branch", "monitor/status" in corr["old_2e4_monitor_branch"]["classification"])
    clamp = corr["retained_torque_clamp_branch"]
    check("retained H clamp input is AE12", clamp["input"] == "0xFEBEAE12")
    check("H clamp staging source is F166", clamp["upstream_staging"] == "0xFEBEF166")
    check("both recovered direct writers zero the clamp staging cell", len(clamp["direct_writer_census"]) == 2 and all("writes zero" in x for x in clamp["direct_writer_census"]))
    check("clamp branch is bounded as zero-source retained framework", "zero source" in clamp["classification"])

    print("\n== FD030 transmit generation ==")
    tx = d["fd_0x030_transmit"]
    check("H Tx replaces 260/262 with FD030", tx["sienna_tx_ids"][:2] == ["0x260", "0x262"] and tx["corolla_h_tx_ids"][0] == "0x030")
    check("FD030 is 32-byte cycle/tick 2", tx["pdu0_descriptor"] == {"cycle_or_timeout": 2, "flags": 3, "length": 32})
    check("FD030 owns configured signal IDs 0..36", tx["configured_signal_ids"] == list(range(37)))
    check("packer directly writes only signals 0..34", tx["direct_packer_signal_ids"] == list(range(35)))
    check("configured signals35/36 have no recovered direct pack call", tx["configured_without_recovered_direct_pack_call"] == [35, 36])
    check("signal9 is exact first-seven-byte additive field plus 0x38",
          tx["checksum_like_signal_9"]["formula"] == "sum(payload_bytes_0_through_6) + 0x38, low byte")
    classes = {row["writer_class"] for row in tx["fields"]}
    check("FD030 writer census distinguishes direct, GP-relative, constant-zero and computed fields",
          {"runtime-produced", "runtime-produced-gp-relative", "runtime-constant-zero-direct-writer-census", "computed-first-seven-byte-additive-field-plus-0x38"} <= classes)
    check("FD030 no longer has false default-init-only fields", "default-init-only-direct-writer-census" not in classes)
    gp = tx["gp_relative_writer_correction"]
    expected_gp = [0, 1, 10, 14, 16, 17, 18, 27, 28, 31, 34]
    check("FD030 GP-relative correction covers exact eleven signals", gp["affected_signal_ids"] == expected_gp)
    rows = {row["signal_id"]: row for row in tx["fields"]}
    check("all corrected signals have exact runtime GP-relative writers", all(rows[x]["writer_class"] == "runtime-produced-gp-relative" for x in expected_gp))
    check("signals 0/10/31 are the recovered driver-torque encoding family", all("driver-steering-torque" in rows[x]["recovered_semantic"] for x in (0, 10, 31)))
    check("signal34 is Q-current-derived", "Motor Actual Current (Q Axis)" in rows[34]["recovered_semantic"] and "calibration-dependent" in rows[34]["recovered_semantic"])
    print("\n== compact evidence binding ==")
    e = json.loads(EVIDENCE.read_text()); r = json.loads(REFS.read_text()); se = json.loads(STATE_EVIDENCE.read_text())
    check("FD/control evidence is exact H image-bound", e["software_id"] == "8965H1202000" and e["image"]["sha256"] == d["images"]["corolla_h_sha256"])
    check("direct-reference census records its computed-pointer boundary", "computed-pointer" in r["evidence_boundary"])
    check("reference census covers at least 70 explicit terms", len(r["terms"]) >= 70)


def _section_steering_nested():
    print('== steering nested ==')
    """Verify closure of the nine remaining named Corolla-H steering roles."""
    import json
    ROOT=REPO_ROOT
    ART=ROOT/'data/generated/corolla_8965H1202000_steering_nested.json'; EV=ROOT/'data/generated/corolla_8965H1202000_steering_nested_decompiler_evidence.json'; RAW=ROOT/'community/albinoelephant/raw-20260818/albinoelephant-corolla-2023.20260814-0023/dump_codeflash_00000000_00200000_20260814-025814.bin'
    d=json.loads(ART.read_text());e=json.loads(EV.read_text());raw=RAW.read_bytes()[:0x100000]
    check('H image hash pinned',sha(raw)==e['image']['codeflash_sha256'])
    check('all raw bodies validate',all(sha(raw[int(r['entry'],16):int(r['entry'],16)+r['body_size']])==r['body_sha256'] for r in e['functions']))
    by={int(r['entry'],16):r for r in e['functions']}
    check('six one-to-one steering roles recovered',d['steering_role_closure_count']==6)
    check('three classic command roles closed by recensus',d['classic_command_surface_recensus_count']==3)
    check('pipeline maps to H CEDAE',d['pipeline']['h']=='0x000CEDAE' and d['pipeline']['h_wrapper_calls_pipeline'])
    check('wrapper maps to H CF028',d['pipeline']['wrapper_h']=='0x000CF028')
    check('LTA limiter is terminal fourth call in paired wrapper',d['lta_rate_limit']['h_is_fourth_wrapper_call'] and d['lta_rate_limit']['h_wrapper_call_count']==4)
    check('H LTA limiter writes regenerated output bank',all(x.lower().replace('0x','') in by[0xC9C16]['decompiled_c'].lower().replace('0x','') for x in ['FEBEC1E0','FEBEC200','FEBEC20A']))
    pri=d['primary_command_conditioning']
    check('primary command wrapper keeps six stages',pri['wrapper_call_count_sienna']==6==pri['wrapper_call_count_h'])
    check('mode select and slew targets are ordered',pri['ordered_targets'][3:6]==['0x000CB8BA','0x000CB900','0x000CB9B6'])
    check('H mode select uses local supervisor mode and selected command',all(s in by[0xCB8BA]['decompiled_c'] for s in ['cRamfebec272','iRamfebec278','cRamfebec2a6']))
    check('H slew stage consumes selected command and emits conditioned output',all(s in by[0xCB9B6]['decompiled_c'] for s in ['iRamfebec278','sRamfebec2a8']))
    rep=d['classic_command_mode_replacement']
    check('classic 2E4/131 command inputs stay absent',not rep['classic_2e4_rx_present'] and not rep['classic_131_rx_present'])
    check('replacement decoder is H CBE6E behind CB68A',rep['h_decoder']=='0x000CBE6E' and rep['h_decoder_wrapper']=='0x000CB68A' and 'FUN_000cbe6e' in by[0xCB68A]['decompiled_c'])
    check('replacement decoder reads H-specific mode state',all(s in by[0xCBE6E]['decompiled_c'] for s in ['cRamfebeacbd','cRamfebec26d','cRamfebeadb0']))
    sec=d['secondary_command_conditioning']
    check('secondary parent chain maps BA3DA/CBA42/CB49C to B8E84/CEFF8/CE974',sec['h_parent_chain']==['0x000B8E84','0x000CEFF8','0x000CE974'])
    check('secondary select maps to H CD3CC',sec['select']['h']=='0x000CD3CC' and 'iRamfebec3b8' in by[0xCD3CC]['decompiled_c'])
    check('following gain clip remains H CD440 anchor',sec['following_gain_clip_anchor']['h']=='0x000CD440' and by[0xCD440]['body_size']==86)
    check('all nine named steering residuals closed',d['static_conclusion']['all_9_named_steering_residuals_closed'])


def _section_steering_supervisor():
    print('== steering supervisor ==')
    """Verify the 8965H1202000 steering-supervisor stage ledger."""
    import json
    REPO=REPO_ROOT
    ART=REPO/'data/generated/corolla_8965H1202000_steering_supervisor_stage_ledger.json'
    d=json.loads(ART.read_text());r=d['roots'];s=d['summary']
    print('\n== stage denominator ==')
    check('Sienna root is CB86E / 424 bytes',r['sienna']=='0xCB86E' and r['sienna_body_size']==424)
    check('H root is CEDAE / 534 bytes',r['corolla_h']=='0xCEDAE' and r['corolla_h_body_size']==534)
    check('direct stage counts are 94 -> 123',(r['sienna_direct_stage_count'],r['corolla_h_direct_stage_count'])==(94,123))
    check('83 stages are order-paired',s['paired']==83)
    check('33 pairs are unique exact instruction-shape transfers',s['paired_unique_exact_shape']==33)
    check('40 H stages are order-unpaired',s['h_order_unpaired']==40)
    check('11 Sienna stages are order-unpaired',s['sienna_order_unpaired']==11)
    check('every H-unpaired stage has a bounded role class',len(d['h_order_unpaired'])==40 and all(x['role_class'] and x['bounded_description'] for x in d['h_order_unpaired']))
    print('\n== command-specific transfer boundary ==')
    def pair(sa,ha):
     return next((x for x in d['stages'] if x.get('sienna_entry')==sa and x.get('h_entry')==ha),None)
    check('S clamp/gain -> H C91B6 is exact-shape',pair('0xC853A','0xC91B6')['pair_evidence']=='unique-exact-instruction-shape')
    check('S rate-limit -> H C9232 is exact-shape',pair('0xC85B6','0xC9232')['pair_evidence']=='unique-exact-instruction-shape')
    removed={x['sienna_entry']:x for x in d['sienna_order_unpaired']}
    check('authenticated 131 smoothing C8DE0 is order-unpaired',removed['0xC8DE0']['role_class']=='sienna_lta_angle_command')
    replacement=d['explicit_command_mode_boundary']['replacement_command']
    check('replacement command is protected B6 target angle','0x0B6 signal255' in replacement and 'signal254' in replacement)
    check('replacement command carries current closed B6 semantics','1024/17870 deg/count' in replacement and 'PCS/LDA/Hands Off LTA/LTA-LCA/PDA' in replacement and '7-foreground-tick' in replacement and 'modulo-64' in replacement)
    check('replacement command preserves remaining boundaries','literal OEM signal255 unit' in replacement and 'stock wall-clock sender cadence/template' in replacement and 'upstream producer/SecOC signing contract remain bounded' in replacement and 'exclusive replacement freshness progression is closed separately' in replacement and 'Physical scale and exact OEM mode names remain open' not in replacement)
    check('replacement command proof linked',d['explicit_command_mode_boundary']['canonical_proof']=='data/generated/corolla_8965H1202000_b6_target_angle_ingress.json')
    print('\n== H expansion classification ==')
    roles=s['h_unpaired_role_counts']
    check('H expansion includes B6 mode/validity/status stages',roles['b6_mode_table']==roles['b6_validity_gate']==roles['b6_status_export']==1)
    check('H expansion has eight dual-channel plausibility stages',roles['h_dual_channel_plausibility']==8)
    check('H expansion has three motion-state estimator stages',roles['h_motion_state_estimator']==3)
    check('H expansion has two geometry-estimator stages',roles['h_geometry_estimation']==2)
    check('H expansion has three supervisor fault monitors',roles['supervisor_fault_monitor']==3)
    check('all 40 H-unpaired roles are counted',sum(roles.values())==40)


def _section_lta_command_provenance():
    print('== lta command provenance ==')
    """Verify the exact-image Corolla H autonomous-lateral command provenance."""

    import hashlib
    import json

    REPO = REPO_ROOT
    ART = REPO / "data/generated/corolla_8965H1202000_lta_command_provenance.json"
    EVID = REPO / "data/generated/corolla_8965H1202000_lta_command_provenance_decompiler_evidence.json"
    IMAGE = REPO / "community/albinoelephant/normalized/8965H1202000_CodeFlash.bin"


    d = json.loads(ART.read_text())
    e = json.loads(EVID.read_text())
    image = IMAGE.read_bytes()

    print("\n== evidence identity ==")
    check("report is exact H image-bound", d["software_id"] == "8965H1202000" and d["images"]["corolla_h"]["sha256"] == hashlib.sha256(image).hexdigest())
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



def _section_motor_control():
    print('== motor control ==')
    """Verify target-native Corolla-H motor-control role recovery."""
    import json
    ROOT=REPO_ROOT
    ART=ROOT/'data/generated/corolla_8965H1202000_motor_control.json';EV=ROOT/'data/generated/corolla_8965H1202000_motor_control_decompiler_evidence.json';HRAW=ROOT/'community/albinoelephant/raw-20260818/albinoelephant-corolla-2023.20260814-0023/dump_codeflash_00000000_00200000_20260814-025814.bin'
    a=json.loads(ART.read_text());e=json.loads(EV.read_text());H=HRAW.read_bytes()[:0x100000];by={int(x['entry'],16):x for x in e['functions']}
    print('== deterministic artifact ==')
    print('\n== compact evidence ==')
    check('H image hash pinned',sha(H)==e['image']['codeflash_sha256']==a['images']['h_sha256']);check('all raw H bodies validate',all(sha(H[int(x['entry'],16):int(x['entry'],16)+x['body_size']])==x['body_sha256'] for x in e['functions']))
    print('\n== five changed motor roles ==')
    exp={'0x00032B80':'0x0002E780','0x00036A44':'0x00032616','0x00038464':'0x00033C70','0x00038554':'0x00033D60','0x0005D18C':'0x00058226'}
    check('all five unresolved motor roles recovered',a['motor_role_closure_count']==5 and {x['reference_entry']:x['target_entry'] for x in a['motor_role_closure']}==exp)
    print('\n== calibration state machine ==')
    c=a['calibration_state_machine'];check('S/H calibration state machines are both 1004 bytes',c['sienna_body_size']==c['h_body_size']==1004);check('state 0x33 calls recovered H main handler',c['sienna_has_state_33_call'] and c['h_has_state_33_call'] and c['h_state_0x33_handler']=='0x0002E780');check('H main calibration handler grows 1560->1638 bytes',c['sienna_handler_size']==1560 and c['h_handler_size']==1638);check('H calibration phases publish 0x22 then 0x44',c['h_completion_states']=={'preceding':0x22,'main':0x44} and '= 0x22' in by[0x2E44C]['decompiled_c'] and '= 0x44' in by[0x2E780]['decompiled_c']);check('0x512 and 0x600 domains still dispatch calibration machine',c['version_dispatch']['domains']==[0x512,0x600] and all(t in by[0x57CEA]['decompiled_c'] for t in ('param_2 == 0x512','param_2 == 0x600','FUN_0002ede6')) and all(t in by[0x57EEE]['decompiled_c'] for t in ('param_2 == 0x512','param_2 == 0x600','FUN_0002ede6')))
    print('\n== PI current loops ==')
    pi=a['current_pi_pair'];check('axis A remains exact-size 304-byte analogue',pi['axis_a_body_sizes']==[304,304]);check('axis B is simplified 404->280 bytes',pi['axis_b_body_sizes']==[404,280]);check('steady worker preserves B-before-A order',pi['order_preserved'] and pi['sienna_worker_indices']==[15,16] and pi['h_worker_indices']==[11,12]);check('H A/B share reset and saturation gates',pi['h_shared_reset_gate']);check('H axis B uses ref-feedback 6BBC-6BAC',all(t.lower().replace('0x','') in by[0x32616]['decompiled_c'].lower() for t in pi['h_axis_b_reference_feedback']));check('H axis A uses ref-feedback 6BBE-6BB0',all(t.lower().replace('0x','') in by[0x324D4]['decompiled_c'].lower() for t in pi['h_axis_a_reference_feedback']));check('H gain blocks split A/B at 2D5A4/2D5B4',all(t in by[0x324D4]['decompiled_c'] for t in ('DAT_0002d5a4','DAT_0002d5b0')) and all(t in by[0x32616]['decompiled_c'] for t in ('DAT_0002d5b4','PTR_LAB_0002d5bc')));check('axis-B internal-state transfer is explicitly bounded','do not transfer Sienna axis-B internal state semantics wholesale' in pi['axis_b_boundary'])
    print('\n== inverse rotating-frame pair ==')
    inv=a['inverse_rotating_frame'];check('H inverse transforms are twin 226-byte functions',inv['body_sizes']==[226,226]);check('inverse formula constants are preserved',inv['formula_tokens_present'] and inv['formula_tokens']==['0x6eda','0x6883','0x8000','0x2000','0x7fff','0x8001']);check('inverse-transform order is preserved',inv['order_preserved'] and inv['h_worker_indices']==[20,21]);check('motor0 H inputs/angle/output banks pinned',inv['h_inputs'][0]==['0xFEBE6A80','0xFEBE6A82'] and inv['h_angle_pairs'][0]==['0xFEBE7A54','0xFEBE7A56'] and inv['h_outputs'][0]==['0xFEBE6C78','0xFEBE6C7A','0xFEBE6C7C']);check('motor1 H inputs/angle/output banks pinned',inv['h_inputs'][1]==['0xFEBE6A84','0xFEBE6A86'] and inv['h_angle_pairs'][1]==['0xFEBE7A60','0xFEBE7A62'] and inv['h_outputs'][1]==['0xFEBE6C80','0xFEBE6C82','0xFEBE6C84'])
    print('\n== CH0 orchestration ==')
    w=a['ch0_worker'];check('CH0 worker maps 216->192 bytes',w['sienna_body_size']==216 and w['h_body_size']==192);check('CH0 wrappers are both 146 bytes',w['wrapper_body_sizes']==[146,146]);check('H wrapper directly invokes transition and steady workers',all(t in by[0x52DBA]['decompiled_c'] for t in ('FUN_00057fc8(2,uVar4,uVar1)','FUN_00058226(2,uVar2)')));check('H steady worker uses >0x1FF motor gate and >0x100 duty gate','0x1ff < param_2' in by[0x58226]['decompiled_c'] and '0x100 < param_2' in by[0x58226]['decompiled_c']);check('H anchor call order is PI-B, PI-A, inverse0, inverse1',all(by[0x58226]['decompiled_c'].index(x+'()') < by[0x58226]['decompiled_c'].index(y+'()') for x,y in zip(w['h_anchor_call_order'],w['h_anchor_call_order'][1:])));check('transition dispatcher contains same motor anchors',all(x+'()' in by[0x57FC8]['decompiled_c'] for x in w['h_anchor_call_order']))


def _section_direct_call_surface():
    print('== direct call surface ==')
    import csv,json
    ROOT=REPO_ROOT;EVID=ROOT/'data/generated/corolla_8965H1202000_direct_call_surface_evidence.json';ART=ROOT/'data/generated/corolla_8965H1202000_direct_call_surface.json';HRAW=ROOT/'community/albinoelephant/raw-20260818/albinoelephant-corolla-2023.20260814-0023/dump_codeflash_00000000_00200000_20260814-025814.bin';LEDGER=ROOT/'data/semantic_coverage_ledger.csv';p=f=0
    e=json.loads(EVID.read_text());d=json.loads(ART.read_text());h=HRAW.read_bytes()[:0x100000]
    check('evidence image hash pinned',e['image']['codeflash_sha256']==sha(h))
    check('all 5425 raw contiguous bodies validate',all(sha(h[int(r['entry'],16):int(r['entry'],16)+r['body_size']])==r['body_sha256'] for r in e['functions']))
    entries={int(r['entry'],16) for r in e['functions']};edges=[int(t,16) for r in e['functions'] for t in r['direct_call_targets']]
    check('literal-call edge/target counts pinned',len(edges)==9509 and len(set(edges))==5151)
    check('all in-image literal call targets resolve to clean H function entries',all(t>0xfffff or t in entries for t in edges) and e['summary']['missing_in_image_literal_call_targets']==[] and e['summary']['closed'])
    rows=list(csv.DictReader(LEDGER.open()));seeds=[r for r in rows if r['name'].startswith('direct_call_target_') and r['discovery_source']=='direct-call seed' and r['discovery_provenance']=='SeedDirectCallTargets.java']
    check('canonical direct-call-seed provenance cohort is exactly 153',len(seeds)==153 and d['canonical_direct_call_seed_count']==153)
    check('recensus covers exactly the canonical generic seed names',{x['reference_name'] for x in d['surface_recensus']}=={r['name'] for r in seeds})


def _section_supervisor_external_ingress():
    print('== supervisor external ingress ==')
    """Verify the H generated-COM -> steering-supervisor ingress census."""
    import json
    REPO=REPO_ROOT
    ART=REPO/'data/generated/corolla_8965H1202000_supervisor_external_ingress_census.json'
    HRAW=REPO/'community/albinoelephant/raw-20260818/albinoelephant-corolla-2023.20260814-0023/dump_codeflash_00000000_00200000_20260814-025814.bin'
    SIMG=REPO/'firmware/RH850_P1M-E_CodeFlash.bin'
    hsrc=HRAW.read_bytes();h=hsrc[:0x100000];s=SIMG.read_bytes();d=json.loads(ART.read_text())
    print('== image/corpus evidence boundary ==')
    check('H normalized image hash is pinned',sha(h)==d['images']['corolla_h_sha256'])
    check('Sienna image hash is pinned',sha(s)==d['images']['sienna_sha256'])
    check('census uses corrected fixed-map model','fixed-map-snapshot' in d['evidence_boundary'] and 'corrected-context' in d['evidence_boundary'])
    check('H COM data-offset table is recovered',d['summary']['h_offset_table']=='0x22788')
    check('S COM data-offset table is uniquely recovered in generated-data region',0x22000 <= int(d['summary']['s_offset_table'],16) < 0x23000)
    print('\n== exact consumer binding ==')
    check('census contains external supervisor references',len(d['external_refs'])>0)
    all_hash=True
    all_unpack=True
    for row in d['external_refs']:
     entry=row['consumer']; size=row['consumer_body_size']
     all_hash &= sha(h[entry:entry+size])==row['consumer_body_sha256']
     for u in row['source_unpackers']:
      all_unpack &= sha(h[u['entry']:u['entry']+u['body_size']])==u['body_sha256']
    check('every cited consumer raw-body hash validates',all_hash)
    check('every cited source-unpacker raw-body hash validates',all_unpack)
    print('\n== replacement-command closure ==')
    changed=[x for x in d['external_refs'] if x['wire_class']!='shared_wire_field']
    check('all H-only/wire-changed supervisor fields are from B6',bool(changed) and all(x['can']==0xB6 for x in changed))
    check('no non-B6 changed wire field reaches mapped supervisor cone',not [x for x in changed if x['can']!=0xB6])
    large=d['potential_changed_large_fields']
    check('only changed >=12-bit ingress is B6 signal255',bool(large) and {(x['can'],x['signal'],x['bits'],x['signed'],x['wire_byte']) for x in large}=={(0xB6,255,16,1,4)})
    positive=d['positive_changed_large_field']
    check('positive B6 signal255 fixed-map path exact',positive['raw']=='0xFEBE7D94' and positive['stage']=='0xFEBEF1CC' and positive['snapshot']=='0xFEBEAE82')
    check('positive B6 signal255 reaches steering cone',positive['consumer_entries']==['0x000C86E8','0x000C87FC','0x000C9DB0'])
    active_b6={x['signal'] for x in changed if x['can']==0xB6}
    check('exact fixed-map B6 supervisor field set is pinned',active_b6 == {254,255,258,260,261,262,263,264})
    check('all changed B6 fields except signal255 are sub-12-bit',all(x['bits']<12 for x in changed if x['signal']!=255))
    print('\n== shared-CAN boundary ==')
    shared_nonb6=[x for x in d['external_refs'] if x['can']!=0xB6]
    check('non-B6 external supervisor refs are same-wire fields on Sienna',bool(shared_nonb6) and all(x['wire_class']=='shared_wire_field' for x in shared_nonb6))
    check('shared FD025 cannot become an H-only wire-field source',all(x['wire_class']=='shared_wire_field' for x in d['external_refs'] if x['can']==0x25))
    check('census walks a nontrivial H supervisor call cone',d['summary']['h_cone_functions']>100)
    check('census tracks nontrivial generated COM staging/snapshot state',d['summary']['h_com_stage_cells']>20 and d['summary']['h_com_snapshot_cells']>20)


def _section_openpilot_state_bridge():
    print('== openpilot state bridge ==')
    """Verify the H/F Corolla openpilot state-interface bridge."""

    import json

    REPO = REPO_ROOT
    ART = REPO / "data/generated/corolla_8965H1202000_openpilot_state_bridge.json"
    EVID = REPO / "data/generated/corolla_8965H1202000_openpilot_state_bridge_decompiler_evidence.json"
    FD = REPO / "data/generated/corolla_8965H1202000_fd_control_interface.json"
    IMAGE = REPO / "community/albinoelephant/normalized/8965H1202000_CodeFlash.bin"


    art = json.loads(ART.read_text())
    evid = json.loads(EVID.read_text())
    fd = json.loads(FD.read_text())
    image = IMAGE.read_bytes()

    print("== deterministic artifacts ==")
    check("exact H image identity", len(image) == 0x100000 and sha(image) == art["images"]["corolla_h"]["sha256"] == evid["image"]["sha256"])
    check("H/F application identity carried forward", art["images"]["corolla_f"]["application_byte_identical_to_h"])
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

    print("\n== 0x351 mixed status bridge ==")
    s351 = art["state_bridge"]["0x351"]
    check("351 force7 topology is fully source-bounded", s351["force7_static_contract"]["condition"] == "(FEBE65E4 & 0x0003) != 0 AND FEBE7E13 != 0" and s351["force7_static_contract"]["record_aggregate_side"]["record_count"] == 24 and s351["force7_static_contract"]["record_aggregate_side"]["bit_used"] == 15)
    check("351 exact C159B49 diagnostic join", s351["diagnostic_join"]["techstream_code"] == "C159B49" and s351["diagnostic_join"]["h_dtc_index"] == 54 and s351["diagnostic_join"]["enabled_word"] == 1)
    check("351 exact seven-count transition state", any("seven-count transition state" in x and "0x2B930 = 7" in x for x in s351["producer_chain"]))
    check("351 force-7 override is separate and exact", "separately forces code 7" in s351["wire_fields"][0]["semantic"] and "exact force-7 indicator" in s351["wire_fields"][1]["semantic"] and "(FEBE65E4 & 3) != 0" in s351["wire_fields"][1]["semantic"] and "FEBE7E13 != 0" in s351["wire_fields"][1]["semantic"] and any("force-writes code 7 plus FEBE7DD1=1" in x for x in s351["producer_chain"]))

    print("\n== 0x394 classifier ==")
    s394 = art["state_bridge"]["0x394"]
    check("394 has exact 17-row classifier table", len(s394["state_table_rows"]) == 17 and s394["state_table_rows"][0] == [0, 0, 0, 0, 0])
    check("394 homolog table is byte-identical in Sienna", s394["sienna_table_byte_identical"] is True)
    check("394 state0 is deepest clear/normal path, not Ready", s394["classifier_states"]["0"]["role"] == "deepest clear/normal classifier path" and s394["openpilot_fault_mapping"]["classifier_deepest_clear_normal_state"] == 0 and "not sufficient to authorize actuation" in s394["openpilot_fault_mapping"]["conservative_clear_state_candidate"])
    cfg = s394["state0_final_branch_window"]
    check("394 state0 final gating is raw-instruction pinned", cfg["start"] == "0x0004BB16" and cfg["end_exclusive"] == "0x0004BB50" and cfg["sha256"] == "d3838fae94f6a5bdcf953ccabda64142bddeffd2470e4935af3c4a7374ba50c6" and "0x4BB48" in cfg["control_flow"])
    check("394 temp/permanent fault mapping is deliberately unresolved", s394["openpilot_fault_mapping"]["steerFaultTemporary"] == s394["openpilot_fault_mapping"]["steerFaultPermanent"] == "unresolved")
    check("394 complete DEM class partition is embedded", sum(s394["fault_state_contract"]["dem"]["class_counts"].values()) == 242 and s394["classifier_states"]["6"]["role"].startswith("class-0x02") and s394["classifier_states"]["10"]["role"].startswith("class-0x10") and s394["fault_state_contract"]["aging"]["class2_class4_secondary_age"] == 600)

    print("\n== live 0x030 state and torque ==")
    s030 = art["state_bridge"]["0x030"]
    check("030 configured signal set 0..36", s030["configured_signals"] == list(range(37)))
    check("030 direct packed signals 0..34", s030["direct_packed_signals"] == list(range(35)))
    check("030 additive byte7 exact formula", s030["additive_field"]["wire_byte"] == 7 and "sum(payload_bytes_0_through_6) + 0x38" in s030["additive_field"]["formula"])
    state_fields = {x["signal_id"]: x for x in s030["steering_state_fields"]}
    check("030 selected steering fault/inhibit status nominal polarity observed", state_fields[6]["wire"] == "B6[2]" and state_fields[6]["span_values"] == [0] and state_fields[6]["span_clear_frames"] == 6000)
    check("030 torque-validity gate nominal polarity observed", state_fields[8]["wire"] == "B6[0]" and state_fields[8]["span_values"] == [0] and state_fields[8]["span_clear_frames"] == 6000)
    check("030 neighboring status bit is live", state_fields[7]["span_values"] == [0, 1])
    check("030 B6[1] source/calibration is statically closed", "Q-axis actual-current-derived" in state_fields[7]["semantic"] and state_fields[7]["static_contract"]["calibration"]["feature_flag"] == 0x5A and "calibration-disabled" in state_fields[7]["static_contract"]["classification"])
    torque = s030["driver_torque_encoding_family"]
    check("030 torque exact physical reconstruction promoted", torque["signal_ids"] == [0, 10, 31] and torque["physical_reconstruction"].startswith("Steering Wheel Torque [N.m] = signal10_signed * 0.1"))
    check("030 torque live dynamic range observed", torque["span_torque_nm"]["count"] == 6000 and torque["span_torque_nm"]["min"] < -8.0 and torque["span_torque_nm"]["max"] > 2.8 and torque["span_torque_nm"]["unique_count"] > 500)
    check("030 coarse rounding behavior exact", torque["coarse_rounding_delta_values"] == [-1, 0, 1])
    check("030 eleven GP-relative false negatives corrected", [x["signal_id"] for x in s030["gp_relative_runtime_fields"]] == [0, 1, 10, 14, 16, 17, 18, 27, 28, 31, 34])
    check("030 Q-current derivative remains scale-bounded", s030["q_current_derived_field"]["signal_id"] == 34 and "calibration-dependent" in s030["q_current_derived_field"]["classification"])

    print("\n== Ready Status input wire join ==")
    ready = art["state_bridge"]["ready_status_input_0x51E"]
    check("Ready Status exact input wire and DID", ready["can_id"] == "0x51E" and ready["wire"] == "B0[7]" and ready["firmware_signal_id"] == 154 and ready["did"] == "0x1033" and ready["name"] == "Ready Status")
    check("Ready Status exact source chain", ready["source_chain"] == ["0x51E B0[7]", "0xFEBE7D1B", "0xFEBEF052", "0xFEBEB5A8", "0xFEBEE811", "DID 0x1033"] and ready["firmware_chain_verified"] is True)
    check("Ready Status operational value1 observed on Span", ready["span_operational_frames"] == 60 and ready["span_values"] == [1])
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
_section_fd_control()
_section_steering_nested()
_section_steering_supervisor()
_section_lta_command_provenance()
_section_motor_control()
_section_direct_call_surface()
_section_supervisor_external_ingress()
_section_openpilot_state_bridge()
print(f'\nResults: {passed} passed, {failed} failed')
raise SystemExit(1 if failed else 0)
