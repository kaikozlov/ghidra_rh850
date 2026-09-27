#!/usr/bin/env python3
"""Portable Corolla H SecOC pins: B6 SecOC verification, key provenance, and receive surface.

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


def _section_b6_secoc_verification():
    print('== b6 secoc verification ==')
    """Verify the complete H/F protected-0x0B6 receiver SecOC state machine."""

    import json
    import struct

    REPO = REPO_ROOT
    ART = REPO / "data/generated/corolla_8965H1202000_b6_secoc_verification.json"
    EVID = REPO / "data/generated/corolla_8965H1202000_b6_secoc_verification_decompiler_evidence.json"
    H = REPO / "community/albinoelephant/normalized/8965H1202000_CodeFlash.bin"
    F_RAW = REPO / "community/spanconstant/raw-20260821/span-corolla-2025.20260821-1511/dump_codeflash_00000000_00200000_20260821-152033.bin"
    FULL = REPO / "data/generated/corolla_8965H1202000_b6_full_receiver_contract.json"
    BASE = REPO / "data/generated/corolla_8965H1202000_b6_receiver_contract.json"
    KEYS = REPO / "data/generated/corolla_8965H1202000_secoc_key_provenance.json"


    def reset_trials(current: int) -> list[tuple[int, int]]:
        rows = [(0, current)]
        if current > 0:
            rows.append((1, current - 1))
        if current < 0xFFFFF:
            rows.append((2, current + 1))
        if current > 1:
            rows.append((3, current - 2))
        if current < 0xFFFFE:
            rows.append((4, current + 2))
        return rows


    def reset_candidate(current: int, rx_low2: int, attempt: int) -> tuple[int, int] | None:
        rows = [(trial, value) for trial, value in reset_trials(current) if value & 3 == rx_low2]
        return rows[attempt] if attempt < len(rows) else None


    def next_message(committed: int, rx_low2: int) -> tuple[int, bool]:
        candidate = (committed & ~3) | rx_low2
        if rx_low2 <= (committed & 3):
            candidate += 4
        if candidate <= 0xFF:
            return candidate, False
        return 0xFF, True


    art = json.loads(ART.read_text())
    ev = json.loads(EVID.read_text())
    h = H.read_bytes()
    f = F_RAW.read_bytes()
    full = json.loads(FULL.read_text())
    base = json.loads(BASE.read_text())
    keys = json.loads(KEYS.read_text())
    funcs = {int(row["entry"], 16): row for row in ev["functions"]}

    print("\n== exact source and cross-variant binding ==")
    check("H image exact", len(h) == 0x100000 and sha(h) == "0b47bdc1217835c839e3543e52eab40eb793650a9c159e46f6a9b365ea41a67f")
    check("all promoted H bodies raw-bound",
          all(sha(h[a:a + row["body_size"]]) == row["body_sha256"] for a, row in funcs.items()))
    check("H/F application bytes are identical", h[0x20000:0x100000] == f[0x20000:0x100000])
    check("verification contract explicitly shared with F", art["applies_to"] == ["8965H1202000", "8965F1208000"] and art["cross_variant"]["b6_secoc_verification_contract_byte_identical"] is True)
    check("cross-variant caveat retained", "low-region calibration" in art["cross_variant"]["boundary"])

    print("\n== exact B6 profile / identifiers ==")
    r = h[0x257CC:0x2581C]
    check("B6 profile record exact location/size", len(r) == 0x50 and art["identifiers"]["secoc_record_address"] == "0x000257CC")
    check("B6 DataID and PDU42 exact", struct.unpack_from("<H", r, 0xA)[0] == 0xB6 and struct.unpack_from("<H", r, 0x34)[0] == 42)
    check("B6 freshness ID2 normal slot1", r[9] == 0 and struct.unpack_from("<H", r, 0x12)[0] == 2 and art["identifiers"]["normal_freshness_slot"] == 1)
    check("B6 FV46/FV4 exact", r[0x14] == 46 and r[0x15] == 4)
    check("B6 get/commit callbacks exact", struct.unpack_from("<I", r, 0x48)[0] == 0x896B0 and struct.unpack_from("<I", r, 0x30)[0] == 0x89758)
    check("B6 two retry budgets exact", struct.unpack_from("<H", r, 0x10)[0] == 1 and struct.unpack_from("<H", r, 0x2E)[0] == 2)
    check("B6 internal linkage field +0x04 is zero", struct.unpack_from("<H", r, 4)[0] == 0 and art["identifiers"]["normal_linkage_field_plus_0x04"] == 0)
    check("no invented extra source identifier", art["identifiers"]["separate_source_identifier_in_cmac_input"] is False)

    print("\n== exact RAM state geometry ==")
    ram = art["ram_state"]
    check("retry/result cells exact", ram["crypto_submit_retry_counter"] == "0xFEBE5404" and ram["authentication_candidate_retry_counter"] == "0xFEBE5406" and ram["cmac_verify_result_byte"] == "0xFEBE5450")
    check("authenticated sync current cells exact", ram["global_sync_current_trip"] == "0xFEBE54AC" and ram["global_sync_current_reset"] == "0xFEBE54B0")
    check("authenticated sync pending cells exact", ram["global_sync_pending_trip"] == "0xFEBE54B4" and ram["global_sync_pending_reset"] == "0xFEBE54B8")
    check("B6 committed/pending slots exact", ram["b6_committed_slot"]["address"] == "0xFEBE54D4" and ram["b6_pending_slot"]["address"] == "0xFEBE54EC")
    check("B6 freshness slot shape exact", ram["b6_committed_slot"]["fields"] == {"trip_u32": 0, "reset_u32": 4, "message_u16": 8} and ram["b6_committed_slot"]["bytes"] == 12)
    check("init boundary does not overclaim persistence", "does not by itself claim" in ram["initialization"]["persistence_boundary"])

    print("\n== transmitted freshness and reference candidate arithmetic ==")
    tf = art["transmitted_freshness"]
    check("FV4 split exact", tf["wire"] == "B28[7:4]" and tf["decode"] == {"message_low2": "B28[7:6]", "reset_low2": "B28[5:4]"})
    check("full freshness format exact", tf["full_bits"] == 46 and tf["full_freshness"] == "trip16 || reset20 || message8 || reset_low2 || 00b")
    fa = art["freshness_acceptance"]
    rc = fa["reset_candidate_search"]
    check("reset candidate order exact", rc["ordered_trials"] == ["current", "current-1", "current+1", "current-2", "current+2"])
    check("reset domain exact", rc["domain"] == [0, 0xFFFFF])
    check("reset search is anchored to authenticated global reset", "uVar1 = *(uint *)(unaff_gp + -0x6350);" in funcs[0x89CDA]["decompiled_c"])
    check("reset low2 filter exact", rc["filter"] == "candidate_reset & 3 == transmitted reset_low2" and "*(byte *)(param_2 + 10)" in funcs[0x89CDA]["decompiled_c"])
    check("independent reset model nominal", reset_candidate(100, 0, 0) == (0, 100) and reset_candidate(100, 3, 0) == (1, 99) and reset_candidate(100, 1, 0) == (2, 101))
    check("independent reset model ±2 ambiguity", reset_candidate(100, 2, 0) == (3, 98) and reset_candidate(100, 2, 1) == (4, 102))
    check("B6 retry1 exactly resolves ±2 ambiguity", rc["ordinary_b6_retry_limit"] == 1 and "-2" in rc["important_ambiguity"] and "+2" in rc["important_ambiguity"])
    mc = fa["message_reconstruction_same_epoch"]
    check("same-epoch formula exact", mc["formula"] == "candidate=(committed_message & ~3)|received_message_low2; if received_low2 <= (committed_message & 3), candidate += 4")
    check("message truncation width is exactly two bits", "uStack_24 = 2" in funcs[0x89E2C]["decompiled_c"] and "uVar6 = *param_3;" in funcs[0x89D58]["decompiled_c"] and "uVar7 = 1 << uVar6;" in funcs[0x89D58]["decompiled_c"])
    check("message low2 comes from B28[7:6] and committed slot +8", "*(ushort *)(param_2 + 8) <=" in funcs[0x89E2C]["decompiled_c"] and "unaff_gp + -0x6330" in funcs[0x89E2C]["decompiled_c"] and (0xFEBEB800 - 0x6330 + 0xC) == 0xFEBE54DC)
    check("message reconstruction masks then advances by four", "uVar4 = *(ushort *)(param_2 + 8) | ~((short)uVar7 - 1U) & uVar2;" in funcs[0x89D58]["decompiled_c"] and "uVar6 = uVar5 + uVar2;" in funcs[0x89D58]["decompiled_c"])
    check("independent message model forward 1..4", next_message(10, 3) == (11, False) and next_message(10, 2) == (14, False) and mc["ordinary_forward_delta"] == [1, 4])
    check("message boundary model exact", next_message(254, 3) == (255, False) and next_message(253, 0) == (255, True))
    check("new epoch forward rule exact", fa["epoch_transition"]["strictly_newer_rule"] == "global_trip > committed_trip OR (global_trip == committed_trip AND candidate_reset > committed_reset)")
    check("new epoch starts message from received low2", fa["epoch_transition"]["new_epoch_message"] == "received_message_low2 (0..3)")
    check("staging happens before CMAC", "pending slot" in fa["epoch_transition"]["staging"] and "before CMAC" in fa["epoch_transition"]["staging"])

    print("\n== special boundary and authenticated sync wrap ==")
    s24 = fa["special_status_0x24"]
    check("0x24 is not hard freshness reject", s24["hard_reject"] is False)
    check("0x24 still executes CMAC", s24["cmac_still_runs"] is True and "common C3 path" in s24["reason"])
    wrap = fa["trip_wrap"]
    check("sync trip-wrap threshold raw exact", h[0x25728] == 0x0F and wrap["sync_threshold"] == 15)
    check("sync wrap window exact", "0xFFFF-15" in wrap["wrap_acceptance"] and "<=16" in wrap["wrap_acceptance"])
    check("authenticated trip wrap clears B6 freshness slots", wrap["b6_state_cleared_on_authenticated_trip_wrap"] is True and "0x8A0AE(0)" in wrap["post_verified_sync_action"] and "B6" in wrap["post_verified_sync_action"])
    check("global sync only commits after auth success", fa["global_epoch_source"]["commit_only_after_authentication_success"] is True)

    print("\n== CMAC construction, command7, key selector ==")
    env = art["authenticated_envelope"]
    check("CMAC input exact 36-byte shape", env["authenticated_input_bytes"] == 36 and env["cmac_input"] == "00 B6 || B0..B27 || reconstructed_freshness[6]")
    check("CMAC/tag exact", env["cmac_algorithm"] == "AES-CMAC-128" and env["received_tag_bits"] == 28 and env["transmitted_tag"] == "MSB28")
    check("command7 path exact", "0x88A56" in env["submit_path"] and "0x822D0" in env["submit_path"] and "0x83BF4" in env["submit_path"])
    check("config0/job0/slot4 exact", art["identifiers"]["secoc_crypto_config_id"] == 0 and art["identifiers"]["cryptoif_job_handle"] == 0 and art["identifiers"]["icus_slot_selector"] == 4)
    check("ICU-S command word exact", env["icus_command_word"].endswith("0x00040007"))
    check("raw config type1/selector4 exact", h[0x2570C:0x25720].hex() == "0100000004000000000000000000000000000000")
    check("slot4 key remains opaque", env["key_value_cpu_visible"] is False and keys["static_storage_derivation_conclusion"]["cpu_visible_raw_slot4_key"] is False)
    check("result zero means CMAC match", "0 means verified/match" in env["result_polarity"] and "disabled" in env["result_evidence"])

    print("\n== queue / retry / acceptance state machine ==")
    sm = art["acceptance_state_machine"]
    check("queue states exact", sm["queue_states"] == {"idle": "E1", "new": "D2", "verify": "C3", "retry": "B4", "freshness_failure": "A5", "generic_failure": "96"})
    check("fresh PDU resets both retry counters", "D2->C3" in sm["new_pdu_transition"] and "resets" in sm["new_pdu_transition"])
    check("B4 re-entry itself adds no counter reset", "B4->C3" in sm["same_pdu_retry_transition"] and "without an additional reset" in sm["same_pdu_retry_transition"])
    rb = sm["retry_budgets"]
    check("auth candidate/MAC retry budget1 exact", rb["authentication_candidate_or_mac_mismatch"]["limit"] == 1 and rb["authentication_candidate_or_mac_mismatch"]["record_offset"] == "0x10" and rb["authentication_candidate_or_mac_mismatch"]["scope"] == "current queued PDU")
    check("auth retry resets CryptoIf busy counter", "unaff_gp + -0x63fc) = 0;" in funcs[0x8891E]["decompiled_c"] and "resets the CryptoIf-submit counter" in rb["authentication_candidate_or_mac_mismatch"]["interaction"])
    check("CryptoIf busy retry budget2 is per auth attempt", rb["cryptoif_submit_busy"]["limit"] == 2 and rb["cryptoif_submit_busy"]["record_offset"] == "0x2E" and "current authentication candidate" in rb["cryptoif_submit_busy"]["scope"])
    check("CryptoIf result2 increments busy counter without clearing auth counter", "unaff_gp + -0x63fc" in funcs[0x889C2]["decompiled_c"] and "unaff_gp + -0x63fa" not in funcs[0x889C2]["decompiled_c"])
    fr = sm["freshness_results"]
    check("freshness 0x22 hard fails before command7", "hard freshness failure" in fr["0x22"] and "no command7" in fr["0x22"])
    check("freshness 0x22 records conditional failure-forwarding", "0x888A6" in fr["0x22"] and "grace counter" in fr["0x22"])
    check("freshness 0x23 retries candidate", "candidate retry" in fr["0x23"] and "C3->B4" in fr["0x23"])
    check("freshness 0x24 stays verify and continues command7", "state remains C3" in fr["0x24"] and "command7 still executes" in fr["0x24"])
    check("Gate1 requires verify-worker zero", "only when 0x88A56 returns 0" in sm["gate1"])
    g2 = sm["gate2"]
    check("Gate2 result cell exact", g2["result_cell"] == "0xFEBE5450")
    check("success commits before delivery", g2["commit_before_delivery"] is True and "pending slot commits" in g2["success"] and "then PDU42 routes" in g2["success"])
    check("mismatch never commits freshness", "does not commit" in g2["mismatch"])
    check("exhausted mismatch records conditional failure-forwarding", "retry budget is exhausted" in g2["mismatch"] and "0x888A6" in g2["mismatch"])
    fc = sm["freshness_commit"]
    check("normal commit copies pending only on success", "copy pending" in fc["success_action"] and "no copy" in fc["failure_action"] and "unchanged" in fc["failure_action"])
    fd = sm["verification_failure_delivery_policy"]
    check("B6 failure-forward grace policy exact", fd["b6_profile_plus_0x09"] == 0 and fd["grace_limit_raw"] == 204 and fd["grace_counter"] == "0xFEBE5408")
    check("failure grace raw config exact", struct.unpack_from("<H", h, 0x25726)[0] == 204)
    check("failure grace lifecycle promoted", all(a in funcs for a in (0x88288, 0x88308, 0x8857C, 0x886DA, 0x886FC)))
    check("failure delivery handler promoted", all(a in funcs for a in (0x88512, 0x88856, 0x888A6)))
    check("hard freshness fail can conditionally reach COM", "0x88A56 sets A5" in fd["freshness_0x22_path"] and "still reach COM" in fd["freshness_0x22_path"])
    check("exhausted CMAC mismatch can conditionally reach COM", "retry is exhausted" in fd["cmac_mismatch_path"] and "0x888A6" in fd["cmac_mismatch_path"])
    check("failure forwarding never commits freshness", "not authenticated successes" in fd["authentication_boundary"] and "do not commit" in fd["authentication_boundary"])
    check("post-grace normal failure route closed", "grace_counter >= 204" in fd["steady_state_boundary"] and "does not route" in fd["steady_state_boundary"])
    check("verified upper route remains COM PDU42", sm["verified_delivery"]["route_id"] == 42 and sm["verified_delivery"]["resolved_upper_callback"] == "0x00076A3C")

    print("\n== application signal261 is independent from SecOC freshness ==")
    seq = art["application_sequence_relation"]
    check("signal261 wire geometry exact", seq["signal_id"] == 261 and seq["wire"] == "B7[5:0]" and seq["application_counter_bits"] == 6)
    check("signal261 modulo64/gap8 exact", seq["application_modulus"] == 64 and seq["application_gap_cap"] == 8 and seq["application_consumer"]["modulus"] == 64)
    check("SecOC message counter distinct 8-bit state", seq["secoc_message_counter_bits"] == 8 and seq["secoc_transmitted_message_bits"] == 2)
    check("two counters explicitly independent", seq["independent_counters"] is True and "does not select the SecOC freshness candidate" in seq["relationship"])
    check("sender must maintain both counters", "Maintain both counters" in seq["sender_requirement"])

    print("\n== Sienna prior art and remaining sender boundary ==")
    prior = art["sienna_prior_art"]
    check("seven Sienna upper-engine role anchors", len(prior["rows"]) == 7)
    check("Sienna comparison uses consistent +0x5A64 role relocation", all(row["entry_delta"] == "0x5A64" for row in prior["rows"]))
    recipe = art["sender_recipe"]
    check("receiver-required sender envelope enumerated", len(recipe["receiver_required_steps"]) == 7 and "AES-CMAC-128" in recipe["receiver_required_steps"][4] and "authenticated/committed 0x00F" in recipe["receiver_required_steps"][0])
    check("slot4 secret remains true cryptographic blocker", "slot-4 secret value remains opaque" in recipe["cryptographic_blocker"])
    replacement = recipe["replacement_sender_state_machine"]
    check("replacement sender re-anchors on authenticated newer 0x00F epoch", "strictly newer authenticated 0x00F" in replacement["startup"] and "seeds full message8" in replacement["new_epoch"])
    check("same-epoch replacement progression matches receiver +1..+4 window", "+1 is simplest" in replacement["same_epoch"] and "+1..+4" in replacement["same_epoch"])
    check("sender restart waits for next epoch instead of guessing message8", "do not guess/replay" in replacement["sender_restart_mid_epoch"] and "next authenticated reset/trip advance" in replacement["sender_restart_mid_epoch"])
    check("replacement sender needs no cross-power message8 persistence", "No sender-side message8 persistence is required" in replacement["power_cycle_persistence"])
    check("replacement sender keeps signal261 separate", "separately modulo 64" in replacement["application_sequence261"] and replacement["state_to_persist_while_running"] == ["trip16", "reset20", "message8", "signal261"])
    check("replacement re-anchor delay stays outside acyclic receiver artifact", "separate freshness-bridge artifact" in replacement["reanchor_delay_boundary"] and "remains acyclic" in replacement["reanchor_delay_boundary"])
    check("replacement freshness no longer requires stock counter discovery", replacement["requires_stock_sender_counter_discovery"] is False and replacement["requires_exclusive_b6_authority"] is True and "no longer required" in recipe["runtime_state_blocker"])
    con = art["static_conclusion"]
    check("all receiver verification dimensions closed", all(con[k] is True for k in (
        "b6_freshness_extraction_closed", "b6_freshness_window_closed", "b6_mac_input_closed",
        "b6_key_slot_selection_closed", "b6_profile_identifiers_closed", "b6_sequence_relation_closed",
        "b6_accept_reject_state_machine_closed", "b6_commit_timing_closed", "b6_verification_failure_delivery_policy_closed", "b6_h_f_receiver_verification_identical")))
    check("replacement sender freshness state machine is closed", con["replacement_sender_freshness_state_machine_closed"] is True and con["replacement_sender_requires_stock_counter_discovery"] is False)
    check("true stock sender/key boundaries remain open", con["slot4_secret_value_closed"] is False and con["stock_sender_freshness_state_ownership_closed"] is False and con["sender_wall_clock_cadence_closed"] is False and con["upstream_producer_closed"] is False)
    check("evidence boundary rejects stock sender/key overclaim but closes replacement re-anchor", "does not recover the protected slot-4 secret" in art["evidence_boundary"] and "upstream FRC/Brake" in art["evidence_boundary"] and "exclusive replacement sender" in art["evidence_boundary"])




def _section_secoc_key_provenance():
    print('== secoc key provenance ==')
    """Verify Corolla 8965H1202000 SecOC key-selector/provisioning provenance."""

    import json

    REPO = REPO_ROOT
    ART = REPO / "data/generated/corolla_8965H1202000_secoc_key_provenance.json"
    EVIDENCE = REPO / "data/generated/corolla_8965H1202000_secoc_key_provenance_decompiler_evidence.json"
    HRAW = REPO / "community/albinoelephant/raw-20260818/albinoelephant-corolla-2023.20260814-0023/dump_codeflash_00000000_00200000_20260814-025814.bin"
    SIMG = REPO / "firmware/RH850_P1M-E_CodeFlash.bin"
    DF = REPO / "data/generated/corolla_2023_albino_dataflash_analysis.json"


    hraw = HRAW.read_bytes()
    h = hraw[:0x100000]
    s = SIMG.read_bytes()
    d = json.loads(ART.read_text())
    ev = json.loads(EVIDENCE.read_text())
    df = json.loads(DF.read_text())

    print("== deterministic generator ==")
    print("\n== image/evidence binding ==")
    check("H image hash is pinned", sha(h) == d["images"]["corolla_h_sha256"] == ev["image"]["sha256"])
    check("Sienna image hash is pinned", sha(s) == d["images"]["sienna_sha256"])
    all_bodies = True
    for row in ev["functions"]:
        entry = int(row["entry"], 16)
        all_bodies &= sha(h[entry:entry + row["body_size"]]) == row["body_sha256"]
    check("all cited H raw function bodies validate", all_bodies)

    print("\n== queue records and shared selector ==")
    check("exact H protected queue IDs", [r["can_id"] for r in d["secoc_records"]] == ["0x00F", "0x0D7", "0x0B6"])
    check("all queue records use SecOC config ID 0", all(r["secoc_crypto_config_id"] == 0 for r in d["secoc_records"]))
    check("all queue records use CryptoIf job handle 0", all(r["cryptoif_job_handle"] == 0 for r in d["secoc_records"]))
    check("config object is exact type1/slot4", d["shared_crypto_selection"]["config_bytes"] == "0100000004000000000000000000000000000000")
    check("config object selects ICU-S slot 4", d["shared_crypto_selection"]["config_type"] == 1 and d["shared_crypto_selection"]["icus_slot_selector"] == 4)
    check("H and Sienna use the same slot-4 config bytes", d["shared_crypto_selection"]["same_bytes_as_sienna"])
    check("raw H config bytes agree", h[0x2570C:0x25720].hex() == d["shared_crypto_selection"]["config_bytes"])
    check("raw Sienna config bytes agree", s[0x25950:0x25964].hex() == d["shared_crypto_selection"]["config_bytes"])

    print("\n== command-7 CPU/ICU boundary ==")
    path = d["command7_cpu_to_icus_path"]
    check("command-7 path retains no raw key bytes", path["raw_key_bytes_in_cpu_command_descriptor"] is False)
    check("command-7 prepare is pinned", path["icus_command7_prepare"] == "0x822D0")
    check("command-7 driver is pinned", path["icus_command7"] == "0x83BF4")
    check("disabled H KAT uses same config", d["slot4_kat"]["config_bytes"] == d["shared_crypto_selection"]["config_bytes"])
    check("disabled H KAT gate is zero", d["slot4_kat"]["compile_gate_address"] == "0x2CA9F" and h[0x2CA9F] == 0 and not d["slot4_kat"]["enabled"])

    print("\n== authenticated key update boundary ==")
    ku = d["command8_key_update"]
    check("key update accepts exact 64-byte package", ku["request_length"] == 64 and ku["staging_shape"] == [16, 32, 16])
    check("key update returns 48-byte proof/result", ku["success_output_length"] == 48)
    check("key update submits literal ICU command 8", ku["icus_command"] == 8 and ku["driver"] == "0x83D7A")
    check("CPU descriptor has no fixed target slot", ku["fixed_cpu_side_target_slot_selector"] is None)

    print("\n== DataFlash evidence boundary ==")
    neg = d["dataflash_raw_key_negative"]
    check("tracked DataFlash hash is pinned", neg["snapshot_sha256"] == df["dump_sha256"])
    check("raw-window scan denominator is 23,277", neg["candidates_tested"] == df["key_domain_scan"]["candidates_tested"] == 23277)
    check("raw-window scan found no candidate match", neg["matches"] == df["key_domain_scan"]["matches"] == [])

    print("\n== final static model ==")
    model = d["static_storage_derivation_conclusion"]
    check("slot selector is CPU-visible", model["cpu_visible_slot4_selector"] is True)
    check("raw slot-4 key is not CPU-visible on mapped verify path", model["cpu_visible_raw_slot4_key"] is False)
    check("mapped SecOC init has no recovered raw-key load", model["mapped_secoc_init_raw_key_load_found"] is False)
    check("mapped SecOC init has no recovered key derivation", model["mapped_secoc_init_key_derivation_found"] is False)
    check("authenticated provisioning interface is recovered", model["provisioning_interface_found"] is True)


def _section_secoc_surface():
    print('== secoc surface ==')
    """Verify target-native Corolla H SecOC/ICU-S residual role recovery."""
    import json
    ROOT=REPO_ROOT
    ART=ROOT/'data/generated/corolla_8965H1202000_secoc_surface.json';EV=ROOT/'data/generated/corolla_8965H1202000_secoc_surface_decompiler_evidence.json';HRAW=ROOT/'community/albinoelephant/raw-20260818/albinoelephant-corolla-2023.20260814-0023/dump_codeflash_00000000_00200000_20260814-025814.bin'
    a=json.loads(ART.read_text());e=json.loads(EV.read_text());H=HRAW.read_bytes()[:0x100000];byh={int(x['target_entry'],16):x for x in e['functions']}
    print('== deterministic artifact ==')
    print('\n== compact evidence ==')
    check('H image hash pinned',sha(H)==e['image']['codeflash_sha256']==a['images']['h_sha256']);check('all raw canonical-size target windows validate',all(sha(H[int(x['target_entry'],16):int(x['target_entry'],16)+x['raw_window_size']])==x['raw_window_sha256'] for x in e['functions']))
    print('\n== ICU-S / CryptoIf core ==')
    c=a['icus_cryptoif_core'];check('25 lower core roles recover at one -0x5C00 island',c['role_count']==25 and c['all_at_single_delta'] and c['delta']==-0x5c00);check('all 25 core reported body sizes match canonical roles',c['all_reported_body_sizes_match']);check('command8 adapter calls command8 prepare','FUN_00081262' in byh[0x814a8]['decompiled_c']);check('command5 adapter calls MAC-generation prepare','FUN_00081e94' in byh[0x820cc]['decompiled_c']);check('command7 verify adapter calls CMAC-verify prepare','FUN_000822d0' in byh[0x824dc]['decompiled_c']);check('CryptoIf begin/update preserve generic job chain',byh[0x82f6a]['target_reported_body_size']==50 and byh[0x82f9c]['target_reported_body_size']==12);check('FIFO/finalizer trio is exact-size relocated family',[byh[x]['target_reported_body_size'] for x in (0x83848,0x838be,0x83910)]==[82,82,60])
    print('\n== RX front-end and profile population ==')
    r=a['rx_frontend'];check('H init and ingress roles recovered',r['init']['h']=='0x00088024' and r['indication']['h']=='0x0008818C');check('H init installs generated slot-4 crypto config',r['init']['installs_slot4_config']);check('H ingress calls record lookup then secured queue',r['indication']['calls_record_lookup'] and r['indication']['calls_secured_queue'] and r['indication']['body_size']==62);check('H has exactly three SecOC RX profiles',r['profile_count']==3 and [x['can_id'] for x in r['profiles']]==[0x00f,0x0d7,0x0b6]);check('H profile PDU IDs are 9/40/42',[x['pdu_id'] for x in r['profiles']]==[9,40,42]);check('all H profiles share crypto config/job 0',all(x['crypto_config_id']==0 and x['cryptoif_handle']==0 for x in r['profiles']))
    print('\n== freshness architecture ==')
    fr=a['freshness'];check('configured get callback is H 896B0',fr['configured_get_callback_set']==[0x896b0]);check('configured commit callback is H 89758',fr['configured_commit_callback_set']==[0x89758]);check('get callback dispatches profile lookup + normal/sync reconstruction',fr['get_dispatches_normal_sync']);check('commit callback dispatches profile lookup + normal/sync commit',fr['commit_dispatches_normal_sync']);check('normal freshness reconstruct maps to H 89E9A',fr['reconstruct_normal']['h']=='0x00089E9A' and byh[0x89e9a]['target_reported_body_size']==212);check('sync freshness reconstruct maps to H 89F6E',fr['reconstruct_sync']['h']=='0x00089F6E' and byh[0x89f6e]['target_reported_body_size']==228);check('normal/sync commits retain 52/78-byte roles',[byh[x]['target_reported_body_size'] for x in (0x8a07a,0x8a130)]==[52,78])
    print('\n== application ICU interrupts and test callbacks ==')
    i=a['application_icus_isrs'];check('ICU ISR pair remains 66-byte wrappers',i['same_reported_size']);check('CH292 ISR calls H interrupt dispatcher','FUN_00081a10' in byh[0x5f3ec]['decompiled_c']);check('CH293 ISR calls H interrupt dispatcher','FUN_00081a36' in byh[0x5f42e]['decompiled_c']);tc=a['crypto_test_callbacks'];cmpc=byh[0x633a0]['decompiled_c'];check('command5 result comparator still compares 16 bytes and returns 44/33',tc['result_compare']['compare_length']==16 and '0x10' in cmpc and '0x44' in cmpc and '0x33' in cmpc);check('key-update completion retains 44/66 terminal states','0x66' in byh[0x63542]['decompiled_c'] and '0x44' in byh[0x63542]['decompiled_c']);check('command5 completion calls result comparator on success','000633a0' in byh[0x635a2]['decompiled_c'].lower());check('fragmented callback boundary caveat is explicit','fragmented' in tc['boundary'])
    print('\n== protected D7 generated unpacker ==')
    d=a['d7_unpacker'];check('H D7 SecOC record routes to PDU 40',d['h_secoc_record_pdu_id']==40);check('PDU 40 owns configured signals 240..247',d['h_pdu40_signal_ids']==list(range(240,248)));check('H D7 scalar unpacker is 468FA and reads 240/243/246',d['h']=='0x000468FA' and sorted(d['h_scalar_receive_signal_ids'])==[240,243,246]);check('H D7 unpacker is regenerated 194->140 bytes',d['sienna_body_size']==194 and d['h_reported_body_size']==140);check('D7 role transfer does not transfer Sienna signal IDs','regenerates the signal population' in d['interpretation'])
    print('\n== conclusion boundary ==')
    sc=a['static_conclusion'];check('all 42 SecOC/ICU-S residual roles are closed',sc['all_42_secoc_icus_residual_roles_recovered']);check('profile population difference remains explicit',sc['h_profile_population_changed']);
_section_b6_secoc_verification()
_section_secoc_key_provenance()
_section_secoc_surface()
print(f'\nResults: {passed} passed, {failed} failed')
raise SystemExit(1 if failed else 0)
