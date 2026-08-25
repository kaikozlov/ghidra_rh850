#!/usr/bin/env python3
"""Verify the H/F 0x00F -> ordinary SecOC freshness bridge artifact."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
ART = json.loads((REPO / "data/generated/corolla_hf_secoc_00f_freshness_bridge.json").read_text())
H = json.loads((REPO / "data/generated/corolla_8965H1202000_b6_secoc_verification.json").read_text())
DECOMP = json.loads((REPO / "data/generated/corolla_8965H1202000_b6_secoc_verification_decompiler_evidence.json").read_text())
COMP = json.loads((REPO / "data/generated/corolla_h_sienna_secoc_structural_comparison.json").read_text())
ALBINO = REPO / "community/albinoelephant/can_oracle.ndjson"

passed = failed = 0


def check(name: str, condition: object, detail: str = "") -> None:
    global passed, failed
    ok = bool(condition)
    passed += int(ok)
    failed += int(not ok)
    suffix = f" ({detail})" if detail else ""
    print(f"[{'PASS' if ok else 'FAIL'}] {name}{suffix}")


print("== exact H/F synchronization profile and wire layout ==")
prof = COMP["profile_tables"]["corolla_h_f"]["records"][0]
static = ART["static_h_f_receiver"]
wire = static["wire_layout"]
check("artifact schema/title pinned", ART["schema"] == 1 and "0x00F" in ART["title"])
check("H/F application identity applies", static["applies_to"]["corolla_h_f_application_identical"] is True)
check("H/F sync profile is DataID 0x00F freshness ID0", prof["data_id"] == "0x00F" and prof["freshness_id"] == 0)
check("H/F sync profile record address exact", prof["address"] == "0x0002572C")
check("sync PDU is exactly eight bytes", prof["secured_pdu_length"] == prof["input_buffer_length"] == 8)
check("sync freshness is full/transmitted FV36", prof["full_freshness_bits"] == prof["transmitted_freshness_bits"] == 36)
check("sync CMAC is 128 -> MSB28", prof["full_cmac_bits"] == 128 and prof["transmitted_cmac_bits"] == 28)
check("sync has no auth or CryptoIf-busy retry", prof["authentication_retry_limit"] == prof["cryptoif_busy_retry_limit"] == 0)
check("artifact profile is independently pinned to raw profile", static["profile_record"]["record_sha256"] == prof["record_sha256"])
check("sync has no application payload", wire["application_payload_bytes"] == 0)
check("sync trip occupies B0:B1", wire["B0_B1"] == "trip16, big-endian")
check("sync reset occupies B2:B4 high nibble", wire["B2_B3_B4_7_4"] == "reset20, big-endian")
check("sync MAC28 occupies B4 low nibble through B7", wire["B4_3_0_B5_B6_B7"] == "CMAC_MSB28")
check("sync FV36 is trip16||reset20", wire["freshness36"] == "trip16 || reset20")
check("sync CMAC input is seven bytes", wire["authenticated_input"] == "00 0F || trip16 || reset20 || 0000b" and wire["authenticated_input_bytes"] == 7)

print("\n== target-native H receiver functions ==")
funcs = {f["entry"]: f for f in DECOMP["functions"]}
bind = static["decompiler_bindings"]
for role, entry in {
    "authenticated_input_build": "0x00087FC2",
    "sync_pack": "0x000899B4",
    "sync_parse": "0x00089B46",
    "sync_reconstruct": "0x00089F6E",
    "sync_commit": "0x0008A130",
    "normal_reset_search": "0x00089CDA",
    "normal_window": "0x00089D58",
}.items():
    check(f"{role} entry/hash bound to target-native decompiler", bind[role]["entry"] == entry and bind[role]["body_sha256"] == funcs[entry]["body_sha256"])
check("sync parser decodes B0:B1 trip", "CONCAT11(*param_1,param_1[1])" in funcs["0x00089B46"]["decompiled_c"])
check("sync parser decodes B2:B4 reset", "param_1[4] >> 4" in funcs["0x00089B46"]["decompiled_c"])
check("sync packer writes five freshness bytes", "param_2[4] = (char)(param_1[1] << 4)" in funcs["0x000899B4"]["decompiled_c"])
check("global 00F state addresses remain exact", static["ram_state"]["current_state"] == ["0xFEBE54AC", "0xFEBE54B0"])
check("sync commit is authentication-gated", static["ram_state"]["commit_only_after_authentication_success"] is True)
check("trip wrap threshold remains 15", static["sync_acceptance"]["trip_wrap_threshold"] == 15)
check("authenticated trip wrap clears B6/D7 state", static["sync_acceptance"]["trip_wrap_clears_b6_and_d7"] is True)

print("\n== ordinary D7/B6 freshness relationship ==")
ordf = static["ordinary_freshness"]
check("D7 and B6 have distinct ordinary freshness IDs", ordf["d7_freshness_id"] == 1 and ordf["b6_freshness_id"] == 2)
check("ordinary D7/B6 slots are independent", ordf["independent_ordinary_slots"] is True)
check("FV4 split is message-low2 then reset-low2", ordf["wire_fv4"]["decode"] == {"message_low2": "B28[7:6]", "reset_low2": "B28[5:4]"})
check("ordinary full freshness is exact", ordf["full_freshness"] == "trip16 || reset20 || message8 || reset_low2 || 00b")
check("reset search exact order", ordf["reset_candidate_search"]["ordered_trials"] == ["current", "current-1", "current+1", "current-2", "current+2"])
check("same-epoch window is strict-forward +1..+4", ordf["same_epoch_message_rule"]["strictly_forward"] is True and ordf["same_epoch_message_rule"]["ordinary_forward_delta"] == [1, 4])
check("new epoch seeds message from received low2", ordf["new_epoch_message_rule"] == "received_message_low2 (0..3)")

print("\n== Albino same-investigation sync oracle ==")
alb = ART["captures"]["albino_2023_tskm_sync_oracle"]
check("Albino raw oracle SHA pinned", hashlib.sha256(ALBINO.read_bytes()).hexdigest() == alb["source"]["sha256"] == "8863398a98875a853e722a6ba83fc10563d5764cea33719c8af34225efa189a3")
check("Albino oracle has 1232 sync rows split 616/616", alb["rows"] == 1232 and alb["rows_per_bus"] == {"0": 616, "2": 616})
check("Albino bus0/bus2 sync payload sequences identical", alb["bus0_bus2_payload_sequences_identical"] is True)
check("Albino trip is exactly 0x0D0D", alb["trip_values_hex"] == ["0x0D0D"])
check("Albino has 206 unique sync states", alb["unique_states"] == 206)
check("Albino reset states mostly advance +1", alb["reset_transition_deltas"] == {"1": 204, "115": 1})
check("Albino state copies are byte-identical", alb["all_repeated_state_payloads_byte_identical"] is True)
check("Albino normal reset cadence median is ~300ms", 295_000_000 <= alb["state_transition_period_ns_median"] <= 305_000_000)
check("Albino collection gap remains explicitly bounded", alb["initial_collection_gap"]["observed_reset_delta"] == 115 and "collection artifact" in alb["initial_collection_gap"]["interpretation"])

print("\n== Span moving-rlog dynamic replay ==")
span = ART["captures"]["span_2025_discord"]
ss = span["sync_00f"]
sd = span["d7_receiver_model_replay"]
st = span["transition_ordering"]
check("Span has 600 00F and 3000 D7 frames", span["wire_counts"]["0x00F"] == 600 and span["wire_counts"]["0x0D7"] == 3000)
check("Span trip is 0x162D and constant", ss["trip_values_hex"] == ["0x162D"])
check("Span reset advances 1037->1237", ss["reset_first"] == 1037 and ss["reset_last"] == 1237)
check("Span 00F wire cadence ~100ms", 99_000_000 <= ss["frame_period_ns_median"] <= 101_000_000)
check("Span reset epoch cadence ~300ms", 299_000_000 <= ss["state_transition_period_ns_median"] <= 301_000_000)
check("Span all 199 inter-transition intervals near 300ms", ss["state_transition_intervals_280_to_320ms"] == ss["state_transition_interval_count"] == 199)
check("Span reset transition is +1 exactly 200 times", ss["reset_transition_deltas_same_trip"] == {"1": 200})
check("Span duplicate sync states are byte/MAC identical", ss["all_repeated_state_payloads_byte_identical"] is True and ss["all_repeated_state_mac28_identical"] is True)
check("Span has one unique MAC28 per sync state", ss["unique_mac28_count"] == ss["unique_states"] == 201)
check("H reset search maps every post-sync Span D7", sd["unmapped_after_first_sync"] == 0 and span["wire_counts"]["mapped_0x0D7_after_first_00F"] == 2997)
check("Span live reset candidates are current/current-1 only", sd["candidate_delta_counts"] == {"-1": 200, "0": 2797})
check("Span same-epoch reconstructed message8 always +1", sd["same_epoch_message8_delta_counts"] == {"1": 2796})
check("Span has 199 complete 15-frame D7 epochs", sd["complete_15_frame_epochs"] == 199)
check("every complete Span epoch is message8 1..15", sd["complete_epochs_exact_message8_1_through_15"] == 199)
check("all non-initial Span epochs begin message-low2=1", sd["non_initial_epoch_first_message_low2"] == {"1": 200})
check("all Span sync transitions record one same-timestamp old-reset D7 after the new 00F", st["d7_same_timestamp_after_sync_using_previous_reset_low2"] == st["sync_state_transitions"] == 200)
check("no same-timestamp old-reset Span D7 precedes the new 00F in logged array order", st["d7_same_timestamp_before_sync_using_previous_reset_low2"] == 0)
check("all after-sync old-reset D7 frames end at message-low2=3", st["those_after_sync_previous_reset_frames_with_message_low2_3"] == 200)
check("new-reset D7 follows ~20ms later", 19_000_000 <= st["first_d7_new_reset_delay_ns_min"] <= st["first_d7_new_reset_delay_ns_median"] <= st["first_d7_new_reset_delay_ns_max"] <= 21_000_000)
check("all first new-reset Span D7 frames start low2=1", st["first_d7_new_reset_message_low2"] == {"1": 200})
check("cross-capture conclusion binds Span current-1 overlap to logged order", ART["cross_capture_conclusions"]["span_logged_order_exercises_current_minus_1_overlap"] is True)

print("\n== independent public-route replay ==")
pub = ART["captures"]["public_2023"]
ps = pub["sync_00f"]
pd = pub["d7_receiver_model_replay"]
check("public route has 588 00F and 2943 D7 frames", pub["wire_counts"]["0x00F"] == 588 and pub["wire_counts"]["0x0D7"] == 2943)
check("public trip is 0x0CE9 and constant", ps["trip_values_hex"] == ["0x0CE9"])
check("public reset states 224->428", ps["reset_first"] == 224 and ps["reset_last"] == 428)
check("public sync cadence ~100ms", 99_000_000 <= ps["frame_period_ns_median"] <= 101_000_000)
check("public reset cadence median ~300ms", 295_000_000 <= ps["state_transition_period_ns_median"] <= 305_000_000)
check("public capture has 194/196 near-300ms transition intervals", ps["state_transition_intervals_280_to_320ms"] == 194 and ps["state_transition_interval_count"] == 196)
check("H reset search maps every post-sync public D7", pd["unmapped_after_first_sync"] == 0 and pub["wire_counts"]["mapped_0x0D7_after_first_00F"] == 2940)
check("public live reset candidates are current/current-1 only", pd["candidate_delta_counts"] == {"-1": 196, "0": 2744})
check("public same-epoch reconstructed message8 always +1", pd["same_epoch_message8_delta_counts"] == {"1": 2742})
check("all 194 complete public epochs are message8 1..15", pd["complete_15_frame_epochs"] == pd["complete_epochs_exact_message8_1_through_15"] == 194)

print("\n== B6 sender consequence and boundary ==")
imp = ART["b6_sender_implication"]
check("00F exposes 36/46 meaningful B6 freshness bits", imp["what_00f_reveals"].startswith("36/46"))
check("B6 message8 explicitly remains local", "B6-local" in imp["what_remains_per_b6"] and "must not be copied" in imp["what_remains_per_b6"])
check("new authenticated epoch removes dependence on old B6 message8", "does not require knowledge of the previous B6 message8" in imp["new_epoch_reanchor"])
check("same-epoch sender still needs full message state", "still needs the reconstructed full message8" in imp["same_epoch_boundary"])
check("transition overlap is explicitly handled", "current-1" in imp["transition_race"] and "new 0x00F" in imp["transition_race"])
check("slot4 secret remains unresolved", any("slot-4 secret" in x for x in imp["still_blocking"]))
check("live B6 sender policy remains unresolved", any("live B6" in x for x in imp["still_blocking"]))
check("capture identity boundary remains explicit", "not exact H/F firmware-identity joins" in ART["evidence_boundary"])
check("D7 message counter is not transferred to B6", "No D7 message counter is transferred to B6" in ART["evidence_boundary"])

print(f"\n== RESULT: {passed} passed, {failed} failed ==")
raise SystemExit(1 if failed else 0)
