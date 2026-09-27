#!/usr/bin/env python3
"""Portable Corolla H protected-0x0B6 receiver pins: byte/bit-complete receiver contract, compact receiver contract, and target-angle ingress.

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


def _section_b6_full_receiver_contract():
    print('== b6 full receiver contract ==')
    """Verify the byte/bit-complete H/F protected-0x0B6 receiver contract."""

    import json
    import struct

    REPO = REPO_ROOT
    ART = REPO / "data/generated/corolla_8965H1202000_b6_full_receiver_contract.json"
    EVID = REPO / "data/generated/corolla_8965H1202000_b6_full_receiver_decompiler_evidence.json"
    H = REPO / "community/albinoelephant/normalized/8965H1202000_CodeFlash.bin"
    F_RAW = REPO / "community/spanconstant/raw-20260821/span-corolla-2025.20260821-1511/dump_codeflash_00000000_00200000_20260821-152033.bin"
    LTA = REPO / "data/generated/corolla_8965H1202000_lta_command_provenance.json"
    KEYS = REPO / "data/generated/corolla_8965H1202000_secoc_key_provenance.json"


    art = json.loads(ART.read_text())
    ev = json.loads(EVID.read_text())
    h = H.read_bytes()
    f = F_RAW.read_bytes()
    lta = json.loads(LTA.read_text())
    keys = json.loads(KEYS.read_text())
    funcs = {int(row["entry"], 16): row for row in ev["functions"]}

    print("\n== exact source and H/F binding ==")
    check("H image pinned", len(h) == 0x100000 and sha(h) == "0b47bdc1217835c839e3543e52eab40eb793650a9c159e46f6a9b365ea41a67f")
    check("all promoted functions raw-bound",
          all(sha(h[a:a + row["body_size"]]) == row["body_sha256"] for a, row in funcs.items()))
    check("H/F application bytes identical", h[0x20000:0x100000] == f[0x20000:0x100000])
    check("H/F contract explicitly shared", art["applies_to"] == ["8965H1202000", "8965F1208000"] and art["cross_variant"]["receiver_contract_byte_identical"] is True)

    print("\n== raw B6 SecOC profile ==")
    record = h[0x257CC:0x2581C]
    check("B6 record raw exact", len(record) == 0x50 and art["wire_envelope"]["profile_record"]["raw_hex"] == record.hex())
    check("CMAC width is 128/full and 28/transmitted", struct.unpack_from("<H", record, 0)[0] == 128 and struct.unpack_from("<H", record, 2)[0] == 28)
    check("trailer is four bytes", struct.unpack_from("<H", record, 6)[0] == 4)
    check("normal profile and Data ID B6 exact", record[9] == 0 and struct.unpack_from("<H", record, 0xA)[0] == 0xB6)
    check("freshness profile id2, FV46/FV4 exact", struct.unpack_from("<H", record, 0x12)[0] == 2 and record[0x14] == 46 and record[0x15] == 4)
    check("secured lengths all 32", struct.unpack_from("<I", record, 0x24)[0] == struct.unpack_from("<I", record, 0x3C)[0] == struct.unpack_from("<I", record, 0x44)[0] == 32)
    check("application and route PDU both 42", struct.unpack_from("<H", record, 0x34)[0] == struct.unpack_from("<H", record, 0x36)[0] == 42)
    check("freshness callbacks exact", struct.unpack_from("<I", record, 0x30)[0] == 0x89758 and struct.unpack_from("<I", record, 0x48)[0] == 0x896B0)
    check("profile partitions frame 28+4", art["wire_envelope"]["authenticated_application_region"] == {"first_byte": 0, "last_byte": 27, "bytes": 28} and art["wire_envelope"]["security_trailer_region"] == {"first_byte": 28, "last_byte": 31, "bytes": 4})

    print("\n== trailer and freshness arithmetic ==")
    # Synthetic trailer: high B28 nibble is FV4; remaining 28 wire bits are CMAC_MSB28.
    b28, b29, b30, b31 = 0xDA, 0x12, 0x34, 0x56
    fv4 = b28 >> 4
    cmac28 = ((b28 & 0xF) << 24) | (b29 << 16) | (b30 << 8) | b31
    shifted = bytes([((b28 << 4) | (b29 >> 4)) & 0xFF,
                     ((b29 << 4) | (b30 >> 4)) & 0xFF,
                     ((b30 << 4) | (b31 >> 4)) & 0xFF,
                     (b31 << 4) & 0xFF])
    check("B28 high nibble is FV4", fv4 == 0xD)
    check("B28 low nibble plus B29..31 is CMAC28", cmac28 == 0x0A123456)
    check("receiver left-shift reconstructs top-aligned CMAC28", shifted.hex() == "a1234560")
    # Independent reference pack for trip16/reset20/message8/reset-low2/00.
    trip, reset, message = 0x1234, 0x56789, 0xAB
    freshness = struct.pack(">HI", trip, ((reset & 0xFFFFF) << 12) | (message << 4) | ((reset & 3) << 2))
    check("full freshness is six bytes", len(freshness) == 6 and freshness.hex() == "123456789ab4")
    check("46-bit full freshness leaves low two pad bits zero", freshness[-1] & 3 == 0)
    check("transmitted FV4 is message-low2 then reset-low2", ((message & 3) << 2 | (reset & 3)) == 0xD)
    check("artifact pins exact full-freshness packing", art["wire_envelope"]["full_freshness"]["packing"] == "trip16 || reset20 || message8 || reset_low2 || 00b")

    print("\n== authenticated input and slot selection ==")
    auth = art["wire_envelope"]["authenticated_input"]
    check("authenticated input is exactly 36 bytes", auth["bytes"] == 36 and auth["application_bytes"] == 28 and auth["freshness_storage_bytes"] == 6)
    check("authenticated input exact shape", auth["packing"] == "DataID_be16(0x00B6) || B0..B27 || reconstructed_freshness48" and auth["data_id_bytes"] == "00b6")
    check("CMAC compare is MSB28", "MSB28" in auth["algorithm"])
    sel = keys["shared_crypto_selection"]
    check("B6 selects generated config0/job0/ICU-S slot4", sel["secoc_crypto_config_id"] == 0 and sel["cryptoif_job_handle"] == 0 and sel["icus_slot_selector"] == 4)
    check("slot4 key value remains CPU-opaque", art["wire_envelope"]["profile"]["key_value_cpu_visible"] is False and art["static_conclusion"]["receiver_key_value_closed"] is False)

    print("\n== verified upper delivery ==")
    delivery = art["verified_delivery"]
    check("verified route resolves to COM PDU42", delivery["route_id"] == 42 and delivery["resolved_upper_callback"] == "0x00076A3C" and "COM RxIndication" in delivery["upper_callback_role"])
    check("delivery chain exact", delivery["queue_ingress"] == "0x0008865A" and delivery["verify_worker"] == "0x00088A56" and delivery["upper_wrapper"] == "0x00088856 -> 0x00089514 -> 0x0007AFB6")
    check("no trailer-stripping overclaim", "does not prove" in delivery["length_boundary"] and "application-consumer census" in delivery["length_boundary"])

    print("\n== application-consumer closure ==")
    app = art["application_consumption"]
    check("configured B6 IDs are exactly 252..267", app["configured_signal_ids"] == list(range(252, 268)))
    check("scalar B6 IDs are exactly 254..265", app["scalar_extracted_signal_ids"] == list(range(254, 266)))
    check("nonscalar configured IDs exact", app["configured_without_scalar_receive"] == [252, 253, 266, 267])
    check("semantic scalar IDs exact", app["application_semantic_signal_ids"] == [254, 255, 258, 260, 261, 262, 263, 264, 265])
    check("extracted/no-downstream IDs exact", app["extracted_no_recovered_downstream_consumer_signal_ids"] == [256, 257, 259])
    escape = app["generic_escape_census"]
    check("no B6 nonscalar block/group consumer", escape["non_scalar_ids_used_by_block_group_api"] == [])
    check("no B6 full-PDU copy", escape["b6_full_pdu_copy_present"] is False and 42 not in escape["all_literal_full_pdu_ids"])
    check("no raw absolute B6 COM-buffer pointer", escape["raw_u32_buffer_pointer_hits"] == [])
    direct_region = escape["direct_com_region_reference_census"]
    check("no direct named/simple-GP-alias B6 COM-window reference in application corpus",
          direct_region["hit_count"] == 0 and direct_region["direct_hits"] == []
          and direct_region["first_byte"] == "0xFEBE4AF4" and direct_region["last_byte"] == "0xFEBE4B13"
          and direct_region["application_first"] == "0x00020000"
          and direct_region["application_end_exclusive"] == "0x00100000")

    print("\n== complete 256-bit partition ==")
    counts = app["bit_category_counts"]
    check("all 256 wire bits partitioned once", sum(counts.values()) == 256)
    check("51 bits have recovered application semantics", counts["application_semantic"] == 51)
    check("6 bits extracted but have no recovered downstream consumer", counts["extracted_no_recovered_downstream_consumer"] == 6)
    check("167 authenticated app bits have no recovered app consumer", counts["authenticated_application_no_recovered_consumer"] == 167)
    check("security trailer partitions 4 FV + 28 MAC bits", counts["secoc_transmitted_freshness"] == 4 and counts["secoc_transmitted_authenticator"] == 28)
    byte_map = app["byte_map"]
    check("byte map covers B0..B31", [row["byte"] for row in byte_map] == list(range(32)))
    check("B0..B2 are authenticated/no-consumer", all(set(byte_map[i]["bit_categories_lsb_to_msb"]) == {"authenticated_application_no_recovered_consumer"} for i in range(3)))
    check("B3 includes Target Lateral ID and two no-consumer bits", {f["signal_id"] for f in byte_map[3]["scalar_fields"]} == {254} and byte_map[3]["bit_categories_lsb_to_msb"].count("application_semantic") == 6)
    check("B4/B5 are entirely target-angle semantics", all(set(byte_map[i]["bit_categories_lsb_to_msb"]) == {"application_semantic"} for i in (4, 5)))
    check("B6 partitions snapshot/gate/staged and one unconsumed bit", byte_map[6]["bit_categories_lsb_to_msb"].count("application_semantic") == 1 and byte_map[6]["bit_categories_lsb_to_msb"].count("extracted_no_recovered_downstream_consumer") == 6 and byte_map[6]["bit_categories_lsb_to_msb"].count("authenticated_application_no_recovered_consumer") == 1)
    check("B7/B8/B9 are entirely recovered application semantics", all(set(byte_map[i]["bit_categories_lsb_to_msb"]) == {"application_semantic"} for i in (7, 8, 9)))
    check("B10 has four semantic and four no-consumer bits", byte_map[10]["bit_categories_lsb_to_msb"].count("application_semantic") == 4 and byte_map[10]["bit_categories_lsb_to_msb"].count("authenticated_application_no_recovered_consumer") == 4)
    check("B11..B27 are authenticated/no-consumer", all(set(byte_map[i]["bit_categories_lsb_to_msb"]) == {"authenticated_application_no_recovered_consumer"} for i in range(11, 28)))
    check("B28 splits CMAC/FV nibble", byte_map[28]["bit_categories_lsb_to_msb"] == ["secoc_transmitted_authenticator"] * 4 + ["secoc_transmitted_freshness"] * 4)
    check("B29..B31 are all transmitted authenticator", all(set(byte_map[i]["bit_categories_lsb_to_msb"]) == {"secoc_transmitted_authenticator"} for i in range(29, 32)))

    print("\n== sender/application boundary ==")
    check("receiver semantics explicitly concentrated B3..B10", "B3..B10" in app["receiver_semantic_concentration"])
    check("unconsumed application bytes still authenticated", "all B0..B27 are inside the CMAC input" in app["sender_boundary"])
    conclusion = art["static_conclusion"]
    check("full receiver partition and SecOC envelope closed", conclusion["full_32_byte_receiver_partition_closed"] is True and conclusion["receiver_secoc_envelope_closed"] is True and conclusion["receiver_authenticated_input_closed"] is True)
    check("receiver freshness/trailer closed", conclusion["receiver_freshness_layout_closed"] is True and conclusion["receiver_transmitted_trailer_layout_closed"] is True)
    check("receiver app generic consumption closed", conclusion["receiver_application_generic_consumption_closed"] is True)
    check("sender cadence/ownership still open", conclusion["sender_wall_clock_cadence_closed"] is False and conclusion["sender_freshness_state_ownership_closed"] is False and conclusion["upstream_producer_closed"] is False)
    check("evidence boundary rejects sender/key overclaim", "does not recover the ICU-S slot-4 secret value" in art["evidence_boundary"] and "sender cadence" in art["evidence_boundary"])


def _section_b6_receiver_contract():
    print('== b6 receiver contract ==')
    """Verify the H protected-B6 request/validity/loss receiver contract."""
    import json, struct

    REPO = REPO_ROOT
    ART = REPO / "data/generated/corolla_8965H1202000_b6_receiver_contract.json"
    EVID = REPO / "data/generated/corolla_8965H1202000_b6_receiver_contract_decompiler_evidence.json"
    FOLLOWUP = REPO / "data/generated/corolla_8965H1202000_tms053_followup_decompiler_evidence.json"
    CAN_EVID = REPO / "data/generated/corolla_8965H1202000_can_com_decompiler_evidence.json"
    RAW = REPO / "community/albinoelephant/normalized/8965H1202000_CodeFlash.bin"

    art = json.loads(ART.read_text())
    ev = json.loads(EVID.read_text())
    followup = json.loads(FOLLOWUP.read_text())
    can_ev = json.loads(CAN_EVID.read_text())
    raw = RAW.read_bytes()

    print("\n== exact source binding ==")
    check("H image exact", len(raw) == 0x100000 and art["sources"]["codeflash"]["sha256"] == sha(raw) == "0b47bdc1217835c839e3543e52eab40eb793650a9c159e46f6a9b365ea41a67f")
    check("TMS-053 follow-up functions are raw-bound", all(sha(raw[int(x["entry"], 16):int(x["entry"], 16) + x["body_size"]]) == x["body_sha256"] for x in followup["functions"]))
    check("all compact receiver bodies raw-bound", all(sha(raw[int(x["entry"], 16):int(x["entry"], 16) + x["body_size"]]) == x["body_sha256"] for x in ev["functions"]))
    rx = next(x for x in can_ev["functions"] if x["entry"] == "0x00076A3C")
    check("CAN COM receive indication raw-bound", sha(raw[0x76A3C:0x76A3C + rx["body_size"]]) == rx["body_sha256"])

    print("\n== request selection ==")
    req = art["request_contract"]
    check("signal254 request geometry", req["signal_id"] == 254 and req["wire_byte"] == 3 and req["bit_length"] == 6 and req["snapshot"] == "0xFEBEADB0")
    check("OEM request dictionary exact", req["oem_dictionary"] == "Target Lateral ID" and req["no_request"] == {"value": 0, "label": "No Request (Manual Operation)"})
    check("five H active request IDs exact", req["accepted_active_requests"] == {"1":"PCS","4":"LDA","10":"Hands Off LTA","11":"LTA/LCA","19":"PDA"})
    check("request decoder/gates exact", req["decoder"] == "0x000CBE6E" and req["common_active_flag"] == "0xFEBEC272" and req["receiver_gates"] == ["0xFEBEACBD == 0", "0xFEBEC26D == 1"])
    check("signal254 classified as request ID", req["classification"] == "supported-target-lateral-request-id")

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
    check("no direct H Tx packer reads ACBD under promoted census", mode_gate["direct_tx_packer_refs"] == [] and "no native wire-visible" in mode_gate["wire_feedback_boundary"])

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
    check("signal258 joins Cooperative Control in Progress vocabulary", cf["258"]["family_vocabulary_candidate"] == "Cooperative Control in Progress Flag")
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


def _section_b6_target_angle_ingress():
    print('== b6 target angle ingress ==')
    """Verify the H protected-B6 target-angle ingress proof."""
    import json
    REPO=REPO_ROOT
    ART=REPO/'data/generated/corolla_8965H1202000_b6_target_angle_ingress.json'
    EVID=REPO/'data/generated/corolla_8965H1202000_b6_target_angle_decompiler_evidence.json'
    RAW=REPO/'community/albinoelephant/normalized/8965H1202000_CodeFlash.bin'
    d=json.loads(ART.read_text()); e=json.loads(EVID.read_text()); raw=RAW.read_bytes()
    print('\n== source identity ==')
    check('H hash exact',d['sources']['codeflash']['sha256']==sha(raw)=='0b47bdc1217835c839e3543e52eab40eb793650a9c159e46f6a9b365ea41a67f')
    check('all compact raw bodies validate',all(sha(raw[int(x['entry'],16):int(x['entry'],16)+x['body_size']])==x['body_sha256'] for x in e['functions']))
    print('\n== exact protected B6 ingress ==')
    mode=d['mode_ingress']; w=d['wire_ingress']
    check('signal254 is 6-bit B3 mode ID',mode['signal_id']==254 and mode['wire_byte']==3 and mode['bit_length']==6 and not mode['signed'])
    check('signal254 fixed-map snapshot exact',mode['raw_destination']=='0xFEBE7D96' and mode['staging_destination']=='0xFEBEF127' and mode['snapshot_destination']=='0xFEBEADB0')
    check('signal254 decoder exact values',mode['decoded_values']=={'1':['C272','C273'],'4':['C272','C26E'],'10':['C272','C270'],'11':['C272','C26F'],'19':['C272','C271']})
    profiles=mode['profile_semantics']
    check('signal254 accepted profiles share common active flag',profiles['common_active_flag']=='C272 is asserted for every accepted value')
    check('signal254 profile flags are mutually exclusive',profiles['mutually_exclusive_profile_flags']=={'1':'C273','4':'C26E','10':'C270','11':'C26F','19':'C271'})
    check('signal254 profiles select separate calibration banks','distinct calibration banks' in profiles['calibration_selection'])
    check('signal254 exact OEM feature labels close',profiles['oem_dictionary_name']=='Target Lateral ID' and profiles['oem_feature_labels']=={'1':'PCS','4':'LDA','10':'Hands Off LTA','11':'LTA/LCA','19':'PDA'})
    check('raw 25/27 special pair gets OEM labels','raw IDs 25 (0x19) and 27 (0x1B)' in profiles['additional_raw_id_use'] and 'AP and Remote Parking' in profiles['additional_raw_id_use'] and 'Only 25/AP' in profiles['additional_raw_id_use'])
    check('signal254 OEM join proof exact','1 PCS, 4 LDA, 10 Hands Off LTA, 11 LTA/LCA, 19 PDA, 25 AP, 27 Remote Parking' in profiles['join_proof'] and 'NA/EU/JP' in profiles['join_proof'])
    check('B6 is protected FD PDU42',w['can_id']=='0x0B6' and w['can_fd'] and w['secured'] and w['pdu_id']==42 and w['pdu_buffer_offset']=='0x01A7')
    check('signal255 is signed16 B4:B5',w['signal_id']==255 and w['wire_byte']==4 and w['bit_length']==16 and w['signed'])
    check('wire->raw->stage->snapshot exact',w['raw_destination']=='0xFEBE7D94' and w['staging_destination']=='0xFEBEF1CC' and w['snapshot_destination']=='0xFEBEAE82')
    check('three ingress functions exact',w['unpacker']=='0x00046A10' and w['staging_copy']=='0x0005262C' and w['gp_relative_snapshot_copy']=='0x000B8EEC')
    check('wire classification is target steering angle',w['classification']=='authenticated-signed16-target-steering-angle-command')
    print('\n== target vs measured control proof ==')
    t=d['target_angle_pipeline']; m=d['measured_angle_feedback']
    check('target starts at C9DB0',t[0]['entry']=='0x000C9DB0' and 'AE82 * 2' in t[0]['relation'])
    check('target replication/rate-limit at C9E54',t[1]['entry']=='0x000C9E54' and 'C098/C100/C120' in t[1]['relation'])
    check('matched target-vs-measured comparator at CA138',t[2]['entry']=='0x000CA138' and 'scaled_target - scaled_measured' in t[2]['relation'])
    check('actual feedback is FD025 184/185/186',m['source_can_id']=='0x025' and m['source_signals']==[184,185,186])
    check('actual snapshots exact',m['snapshots']=={'184':'0xFEBEADF0','185':'0xFEBEACC5','186':'0xFEBEAE14'})
    check('actual reconstruction exact constants', '0x6FB / 0x200' in m['reconstruction'] and 'fraction + coarse*15' in m['reconstruction'])
    wr=m['wire_representation']
    check('FD025 signal184 exact coarse-angle scale',wr['signal184']=={'bits':12,'signed':True,'role':'coarse steering angle','techstream_did':'0x1037','techstream_name':'Steering Angle','physical_scale_deg_per_count':1.5})
    check('FD025 signal185 exact signed fraction scale',wr['signal185']=={'bits':4,'signed':True,'role':'signed fractional steering angle','physical_scale_deg_per_count':0.1})
    check('FD025 combined angle is tenths of degree',wr['combined']=='15 * signal184 + signal185' and wr['combined_unit']=='0.1 deg' and wr['full_turn_counts']==3600 and 'divides that combined count by 3600' in wr['proof'])
    check('same comparator gain recorded', 'same 0xB76/0x400 gain' in m['comparison'])
    check('independent target-vs-measured loop asserted',m['classification']=='independent-target-versus-measured-steering-angle-control-loop')
    check('active controller follows comparator',t[3]['entry']=='0x000CAC24/0x000CA940')
    check('decoded cooperative mode gates controller',t[4]['entry']=='0x000CAD1C' and 'C272' in t[4]['relation'])
    check('controller reaches replicated magnitude',t[5]['entry']=='0x000CC18E -> 0x000CC2EC -> 0x000CAD62')
    check('replicated magnitude reaches C2A8',t[6]['entry']=='0x000C9C16 -> 0x000CB8BA -> 0x000CB9B6' and 'C2A8' in t[6]['relation'])
    check('C2A8 reaches general torque composition',t[7]['entry']=='0x000CD3CC' and 'C3B8' in t[7]['relation'])
    fb=d['final_command_bridge']
    check('target contribution reaches 1C02 bridge','C2A8' in fb['local_chain'] and 'C3D2' in fb['local_chain'] and fb['recovered'])
    check('final observer is Command Value Torque',fb['techstream_command_torque']=={'did':'0x1C02','name':'Command Value Torque','unit':'Nm'})
    check('final q-current observer is 1152',fb['q_axis_command']=={'did':'0x1152','name':'Command Value Current (Q Axis)','unit':'A'})
    check('independent AE82 safety/plausibility consumer',d['independent_safety_consumer']['entry']=='0x000CB4F4' and d['independent_safety_consumer']['source']=='0xFEBEAE82')
    print('\n== scaling boundary ==')
    s=d['scaling']
    check('internal target x2 relation exact','2 * signed16(B6 B4:B5)' in s['exact_internal_relation'])
    check('internal measured relation exact','15*FD025_coarse' in s['exact_internal_relation'] and '1787 / 512' in s['exact_internal_relation'])
    check('physical degree scale closed',s['physical_degree_scale_closed'] is True and s['controller_equivalent_fraction_deg_per_b6_count']=={'numerator':1024,'denominator':17870})
    check('controller-equivalent degree value exact enough',abs(s['controller_equivalent_deg_per_b6_count']-(1024/17870))<1e-15)
    check('controller-equivalent scale is ~1 mrad/count',abs(s['controller_equivalent_mrad_per_b6_count']-1.0001215187701138)<1e-12 and abs(s['difference_from_exact_1_mrad_percent']-0.01215187701137932)<1e-12)
    check('scale keeps integer quantization boundary','integer truncation' in s['quantization_boundary'] and 'exact linearized conversion' in s['quantization_boundary'])
    print('\n== independent Techstream context ==')
    ts=d['techstream']
    check('B6 sender DTC is U012987',ts['immediate_sender_monitor']['dtc']=='U012987')
    check('B6 sender is Brake System Control Module',ts['immediate_sender_monitor']['description']=='Lost Communication with Brake System Control Module' and ts['immediate_sender_monitor']['failure']=='Missing Message')
    check('Corolla P5 topology includes EMPS Brake/EPB FRC',ts['corolla_p5_topology']['required_categories']==[405,435,498] and ts['corolla_p5_topology']['names']=={'405':'EMPS','435':'Brake/EPB','498':'Front Recognition Camera 2'})
    check('P5 target-angle names corroborate domain',[x['name'] for x in ts['family_angle_vocabulary']]==['Target Steering Angle After Output Compensation','Advanced Drive Target Steering Angle'])
    check('P5 target-angle family uses 1CEE',all(x['primary_data_id']=='0x1CEE' for x in ts['family_angle_vocabulary']))
    check('Target Lateral ID dictionary joins H signal254',ts['target_lateral_id_dictionary']=={'name':'Target Lateral ID','accepted_h_profile_labels':{'1':'PCS','4':'LDA','10':'Hands Off LTA','11':'LTA/LCA','19':'PDA'},'special_h_ids':{'25':'AP','27':'Remote Parking'},'pattern_display_key':39})
    check('DID1037 conversion joins H measured angle',ts['steering_angle_conversion']=={'did':'0x1037','name':'Steering Angle','h_callback':'0x488A8','raw_scale':'1.5 deg/count','physical_data_key':3,'conversion_plugin':'GetDatMonSignalInfoP5_DT.dll'})
    check('exact H target observer name not overclaimed','exact H lacks DID 0x1CEE' in ts['vocabulary_boundary'] and 'OEM engineering-unit name' in ts['vocabulary_boundary'])
    print('\n== generation migration ==')
    mig=d['migration']
    check('older Corolla was torque command','0x2E4' in mig['pre_tss3_corolla'] and 'torque' in mig['pre_tss3_corolla'])
    check('Sienna angle prior art kept separate','0x131' in mig['sienna_secoc_prior_art'] and 'different wire' in mig['sienna_secoc_prior_art'])
    check('H/F migration is B6 target angle','0x0B6' in mig['corolla_h_f'] and 'target-angle' in mig['corolla_h_f'])
    check('no wire compatibility overclaim','none claimed' in mig['wire_compatibility'])
    print('\n== static conclusion ==')
    c=d['static_conclusion']
    check('external lateral ingress identified',c['external_autonomous_lateral_ingress_identified'] is True)
    check('ingress exact B6 signal255',c['ingress']=='protected CAN-FD 0x0B6 signal255 signed16 B4:B5')
    check('command domain angle not torque',c['command_domain']=='target steering angle' and c['torque_command'] is False)
    check('mode ingress exact B6 signal254',c['mode_ingress']=='protected CAN-FD 0x0B6 signal254 6-bit B3')
    check('wire target reaches torque/current chain',c['reaches_command_value_torque_and_q_current'] is True)
    check('immediate sender relationship brake',c['immediate_sender_relationship']=='Brake System Control Module')
    check('upstream feature producer still open',c['upstream_feature_producer_identified'] is False)
    check('physical controller-equivalent scale identified',c['physical_scale_identified'] is True and abs(c['controller_equivalent_deg_per_count']-(1024/17870))<1e-15)
    check('OEM wire unit name remains open',c['oem_wire_unit_name_identified'] is False)
    check('signal254 feature labels are identified',c['signal254_feature_labels_identified'] is True and c['signal254_profile_labels']=={'1':'PCS','4':'LDA','10':'Hands Off LTA','11':'LTA/LCA','19':'PDA'})
    check('receiver request/loss/sequence contract promoted',c['request_selection_identified'] is True and c['receiver_loss_cutout_ticks']==7 and c['wall_clock_timeout_identified'] is True and c['sequence_counter_identified'] is True and c['sequence_modulus']==64 and c['sequence_gap_cap']==8)
    check('next target is upstream producer, stock template and signing path','FRC_P5 -> Brake/EPB' in c['next_static_target'] and 'stock B6 cadence' in c['next_static_target'] and 'production signing/suppression path' in c['next_static_target'] and 'replacement freshness' in c['next_static_target'])
_section_b6_full_receiver_contract()
_section_b6_receiver_contract()
_section_b6_target_angle_ingress()
print(f'\nResults: {passed} passed, {failed} failed')
raise SystemExit(1 if failed else 0)
