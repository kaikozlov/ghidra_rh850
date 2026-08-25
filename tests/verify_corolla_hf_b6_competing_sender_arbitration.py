#!/usr/bin/env python3
"""Verify H/F protected-B6 competing-sender receiver arbitration."""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / "data/generated/corolla_hf_b6_competing_sender_arbitration.json"
EVID = ROOT / "data/generated/corolla_8965H1202000_b6_competing_sender_decompiler_evidence.json"
EXTRACTOR = ROOT / "tools/extract_corolla_h_b6_competing_sender_evidence.py"
BUILDER = ROOT / "tools/build_corolla_hf_b6_competing_sender_arbitration.py"
H = ROOT / "community/albinoelephant/normalized/8965H1202000_CodeFlash.bin"
DOC = ROOT / "docs/variants/corolla-h-f-openpilot-state-bridge.md"
FINDINGS = ROOT / "docs/status/FINDINGS.md"
CORRECTIONS = ROOT / "docs/status/CORRECTIONS.md"

passed = 0
failed = 0


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def check(name: str, cond: bool) -> None:
    global passed, failed
    if cond:
        passed += 1
        print(f"PASS: {name}")
    else:
        failed += 1
        print(f"FAIL: {name}")


a = json.loads(ART.read_text())
ev = json.loads(EVID.read_text())
h = H.read_bytes()

check("schema", a["schema"] == "corolla-hf-b6-competing-sender-arbitration-v1")
check("exact H/F scope", a["applies_to"] == ["8965H1202000", "8965F1208000"] and a["cross_variant"]["h_f_application_byte_identical"])
check("non-enabling boundary", not a["suppression_conclusion"]["parallel_injection_safe"] and not a["suppression_conclusion"]["freshness_preemption_is_safe_coexistence"])

print("\n== promoted target-native evidence ==")
check("evidence schema/count", ev["schema"] == "corolla-h-b6-competing-sender-decompiler-evidence-v1" and ev["function_count"] == 12)
check("extractor hash pinned", ev["generator"]["sha256"] == sha(EXTRACTOR.read_bytes()))
check("H image hash pinned", ev["image"]["sha256"] == sha(h))
body_ok = True
for row in ev["functions"]:
    entry = int(row["entry"], 16)
    size = row["body_size"]
    body_ok &= sha(h[entry:entry + size]) == row["body_sha256"]
check("all promoted raw H bodies pinned", body_ok)
roles = {r["role"] for r in ev["functions"]}
check("queue/delivery/sequence/request roles all promoted", {
    "secoc_secured_pdu_ingress", "secoc_queue_first_insert", "secoc_queue_existing_slot_update",
    "secoc_pending_or_retry_to_verify", "com_rx_indication_single_shadow_copy",
    "b6_application_sequence_delta", "b6_sequence_scaled_target_plausibility",
    "b6_target_lateral_id_decoder",
}.issubset(roles))

print("\n== receiver/source identity ==")
r = a["receiver_identity"]
check("one B6 identity", r["can_id"] == "0x0B6" and r["application_pdu_id"] == 42 and r["authenticated_data_id"] == "0x00B6")
check("one ordinary freshness identity", r["freshness_id"] == 2 and r["normal_freshness_slot"] == 1)
check("slot4 shared crypto selection", r["crypto_slot"] == 4)
check("no source ID in recovered authenticated input", not r["separate_source_identifier_in_authenticated_input"])
check("no source-specific acceptance recovered", not r["source_specific_acceptance_recovered"])

print("\n== one-slot SecOC queue arbitration ==")
q = a["single_profile_queue"]
check("single B6 queue multiplicity", q["queue_multiplicity"] == 1 and q["not_a_source_priority_queue"])
check("idle first arrival inserts", "E1->D2" in q["idle_E1"] and "0x87CD6" in q["idle_E1"])
check("pending arrival coalesces into existing slot", "0x87DB0" in q["pending_D2"] and "does not create a second" in q["pending_D2"])
check("pending stage is last-arrival-wins", "last B6 arrival" in q["pending_arbitration"])
check("inflight C3/B4 arrivals not admitted", "ignored" in q["inflight_arbitration"] and "C3" in q["verify_C3_or_retry_B4"] and "B4" in q["verify_C3_or_retry_B4"])

print("\n== freshness arbitration ==")
fresh = a["freshness_arbitration"]
check("single shared committed B6 freshness", fresh["committed_state_is_shared_per_b6_profile"])
check("freshness commits before normal verified COM delivery", fresh["commit_before_normal_verified_application_delivery"])
check("same low2 after committed10 reconstructs 14", fresh["same_low2_reference_examples"]["committed10_received_low2_2"] == 14)
check("next low2 after committed10 reconstructs 11", fresh["same_low2_reference_examples"]["committed10_received_low2_3"] == 11)
check("same-full-freshness replay cannot reuse committed freshness", "next congruent" in fresh["same_full_freshness_replay_after_commit"] and "fails verification" in fresh["same_full_freshness_replay_after_commit"])
check("same-freshness verification failure has bounded delivery exception", "failure forwarding grace/global-override" in fresh["same_full_freshness_replay_after_commit"] and "without committing freshness" in fresh["same_full_freshness_replay_after_commit"])
ffd = fresh["verification_failure_forwarding_exception"]
check("failure-forward grace geometry joined", ffd["grace_limit"] == 204 and ffd["b6_profile_plus_0x09"] == 0)
check("failure-forward never authenticates/commits", "never commits freshness" in ffd["behavior"] and "does not turn" in ffd["arbitration_effect"])
check("future valid freshness has no source lock", "no source lock" in fresh["future_freshness_from_another_capable_sender"])
check("capable senders race shared freshness", "race one shared freshness" in fresh["consequence"])

print("\n== application sequence is not sender arbitration ==")
s = a["application_sequence_arbitration"]
check("signal261 modulo64/gap8", s["signal_id"] == 261 and s["modulus"] == 64 and "min(delta,8)" in s["effective_gap"])
check("strict +1 not required by EPS", not s["strict_plus_one_required_by_eps"])
check("duplicate app sequence not rejected", not s["duplicate_sequence_rejected"] and s["examples"]["same_application_sequence"] == {"raw_delta": 0, "effective_gap": 1})
check("strict +1 and gap4 examples", s["examples"]["strict_plus_one"] == {"raw_delta": 1, "effective_gap": 1} and s["examples"]["gap_four"] == {"raw_delta": 4, "effective_gap": 4})
check("large app gap capped8", s["examples"]["large_gap_capped"] == {"raw_delta": 19, "effective_gap": 8})
check("sequence feeds target plausibility", "0xCB4F4" in s["plausibility_use"] and "78 raw" in s["plausibility_use"])

print("\n== request ID and application shadow ==")
req = a["request_id_arbitration"]
check("accepted request dictionary exact", req["accepted_active_ids"] == {"1":"PCS", "4":"LDA", "10":"Hands Off LTA", "11":"LTA/LCA", "19":"PDA"})
check("no request priority order recovered", req["priority_order_recovered"] is None and "no competing-request history" in req["behavior"])
check("later delivered request can replace profile", "later successfully delivered B6" in req["conclusion"])
d = a["application_delivery"]
check("single PDU42 shadow", d["shared_shadow_pdu"] == 42 and d["entry"] == "0x00076A3C")
check("sequential accepted B6 overwrites current shadow", "overwrites" in d["sequential_valid_frames"])
check("last successful delivery is current command", "last successfully delivered" in d["effective_policy"])

print("\n== hypothesis resolution / suppression policy ==")
hyp = a["hypothesis_resolution"]
check("newest application sequence winner disproved", hyp["newest_application_sequence_wins"].startswith("disproved"))
check("source-specific arbitration not recovered", hyp["source_specific_acceptance"].startswith("not recovered"))
check("frame winner is stage-dependent", hyp["first_or_last_frame_wins"].startswith("stage-dependent"))
check("request priority disproved", hyp["request_id_priority"].startswith("disproved"))
check("freshness is source-agnostic", "not source-specific" in hyp["freshness_rejects_competing_sender"])
policy = a["suppression_conclusion"]
check("EPS does not require named stock identity", not policy["eps_protocol_requires_named_stock_source"])
check("deterministic lateral requires exclusive B6 authority", policy["deterministic_lateral_authority_requires_exclusive_b6_control"])
check("production policy requires stock suppression or proved quiescence", "Suppress/isolate" in policy["production_policy"] and "quiescent" in policy["production_policy"])
check("freshness racing explicitly forbidden as coexistence", "Do not use freshness racing" in policy["production_policy"])
check("physical relay-side identity remains dynamic", "Static receiver logic cannot identify" in policy["physical_topology_boundary"])

print("\n== canonical documentation ==")
doc = DOC.read_text()
findings = FINDINGS.read_text()
corrections = CORRECTIONS.read_text()
check("canonical report records competing-sender arbitration", "Competing valid B6 senders: receiver arbitration and suppression requirement" in doc)
check("canonical report forbids freshness racing", "Freshness racing or" in doc and "not a safe coexistence/fallback mechanism" in doc)
check("canonical report keeps physical suppression point dynamic", "Static receiver logic cannot identify which physical relay side" in doc)
check("COM-016 finding registered", "| COM-016 |" in findings and "competing-sender arbitration is source-agnostic" in findings)
check("CORR-111 failure-forward correction registered", "### CORR-111" in corrections and "not universally non-delivering" in corrections)

print("\n== builder reproducibility ==")
with tempfile.TemporaryDirectory() as td:
    tmp = Path(td) / "arb.json"
    subprocess.run([sys.executable, str(BUILDER), "--out", str(tmp)], cwd=ROOT, check=True, capture_output=True, text=True)
    check("builder reproduces committed arbitration artifact", tmp.read_bytes() == ART.read_bytes())

print(f"\n{passed} passed, {failed} failed")
raise SystemExit(1 if failed else 0)
