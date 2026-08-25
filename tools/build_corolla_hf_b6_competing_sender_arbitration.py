#!/usr/bin/env python3
"""Build the H/F protected-B6 competing-sender receiver-arbitration contract."""
from __future__ import annotations

import argparse
import hashlib
import json
import struct
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
H_IMAGE = REPO / "community/albinoelephant/normalized/8965H1202000_CodeFlash.bin"
F_IMAGE = REPO / "community/spanconstant/raw-20260821/span-corolla-2025.20260821-1511/dump_codeflash_00000000_00200000_20260821-152033.bin"
EVIDENCE = REPO / "data/generated/corolla_8965H1202000_b6_competing_sender_decompiler_evidence.json"
SECOC = REPO / "data/generated/corolla_8965H1202000_b6_secoc_verification.json"
FULL = REPO / "data/generated/corolla_8965H1202000_b6_full_receiver_contract.json"
RECEIVER = REPO / "data/generated/corolla_8965H1202000_b6_receiver_contract.json"
LIMITS = REPO / "data/generated/corolla_hf_steering_limits.json"
EQUIV = REPO / "data/generated/corolla_8965F1208000_vs_8965H1202000_codeflash_equivalence.json"
OUT = REPO / "data/generated/corolla_hf_b6_competing_sender_arbitration.json"


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def need(text: str, *tokens: str) -> None:
    missing = [token for token in tokens if token not in text]
    if missing:
        raise ValueError("missing target-native decompiler token(s): " + ", ".join(missing))


def app_sequence(prev: int, current: int) -> tuple[int, int]:
    """Exact signal261 application delta/effective-gap model."""
    if not 0 <= prev < 64 or not 0 <= current < 64:
        raise ValueError("signal261 outside modulo-64 domain")
    delta = (current - prev) % 64
    effective = 1 if delta <= 1 else min(delta, 8)
    return delta, effective


def next_same_epoch_message(committed: int, received_low2: int) -> int:
    """Exact same-epoch next-congruent message8 reconstruction before boundary handling."""
    if not 0 <= committed <= 0xFF or not 0 <= received_low2 < 4:
        raise ValueError("freshness input outside domain")
    candidate = (committed & ~3) | received_low2
    if received_low2 <= (committed & 3):
        candidate += 4
    return min(candidate, 0xFF)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", type=Path, default=OUT)
    args = ap.parse_args()

    h = H_IMAGE.read_bytes()
    f = F_IMAGE.read_bytes()[:0x100000]
    ev = json.loads(EVIDENCE.read_text())
    secoc = json.loads(SECOC.read_text())
    full = json.loads(FULL.read_text())
    receiver = json.loads(RECEIVER.read_text())
    limits = json.loads(LIMITS.read_text())
    equiv = json.loads(EQUIV.read_text())

    if len(h) != 0x100000 or len(f) != 0x100000:
        raise ValueError("H/F CodeFlash size drift")
    if ev["schema"] != "corolla-h-b6-competing-sender-decompiler-evidence-v1" or ev["function_count"] != 12:
        raise ValueError("competing-sender evidence drift")
    if ev["image"]["sha256"] != sha(h):
        raise ValueError("H evidence/image identity drift")
    if not (h[0x20000:] == f[0x20000:] and equiv["application_equivalence"]["identical"] and equiv["application_equivalence"]["different_bytes"] == 0):
        raise ValueError("H/F application identity drift")

    funcs = {int(row["entry"], 16): row["decompiled_c"] for row in ev["functions"]}
    need(funcs[0x8865A], "cVar1 == -0x1f", "*puVar5 = 0xd2", "FUN_00087cd6", "cVar1 == -0x2e", "FUN_00087db0")
    need(funcs[0x87CD6], "FUN_0008323e(local_34 + iStack_20,*param_3)", "*puVar1 = *(undefined2 *)(param_3 + 1)", "FUN_00087cb0")
    need(funcs[0x87DB0], "FUN_0008323e(local_34 + (param_3 & 0xffff) + iStack_24,*param_4)", "*(undefined2 *)((param_2 & 0xffff) * 8 + aiStack_2c[0]) = uVar5")
    need(funcs[0x88702], "cVar2 == -0x2e", "cVar2 == -0x4c", "cVar3 = -0x3d", "if (cVar2 == -0x2e)")
    need(funcs[0x87E8E], "FUN_00083444(local_30 + iStack_1c,uStack_2c)", "*puVar1 = 0", "puVar1[1] = 0xffff")
    need(funcs[0x76A3C], "for (uVar5 = 0; uVar5 < uVar4", "FUN_000769f6(param_1,1)", "FUN_00087a82(param_1)")
    need(funcs[0xCB246], "bRamfebeadbc - uRamfebec248", "uRamfebec248 = (ushort)bRamfebeadbc", "DAT_000afce8", "DAT_000afcea")
    need(funcs[0xCB4F4], "*(short *)(iVar13 + 0xa4c)", "iVar2 = (int)sVar3 * (uint)uVar11")
    need(funcs[0xCBE6E], "cRamfebeadb0 == '\\x01'", "cRamfebeadb0 == '\\x04'", "cRamfebeadb0 == '\\n'", "cRamfebeadb0 == '\\v'", "cRamfebeadb0 == '\\x13'")

    record = h[0x257CC:0x2581C]
    if not (len(record) == 0x50 and struct.unpack_from("<H", record, 0x0A)[0] == 0xB6 and struct.unpack_from("<H", record, 0x12)[0] == 2 and struct.unpack_from("<H", record, 0x34)[0] == 42):
        raise ValueError("B6 generated profile identity drift")
    wrap, gap = struct.unpack_from("<HH", h, 0xAFCE8)
    if (wrap, gap) != (63, 8):
        raise ValueError("B6 application sequence constants drift")

    ids = secoc["identifiers"]
    accept = secoc["acceptance_state_machine"]
    failure_delivery = accept["verification_failure_delivery_policy"]
    delivery = full["verified_delivery"]
    request = receiver["request_contract"]
    seq = receiver["companion_fields"]["261"]
    if not (
        ids["data_id_authenticated_be16"] == "0x00B6"
        and ids["freshness_id"] == 2
        and ids["normal_freshness_slot"] == 1
        and ids["separate_source_identifier_in_cmac_input"] is False
        and ids["icus_slot_selector"] == 4
        and accept["gate2"]["commit_before_delivery"] is True
        and failure_delivery["grace_limit_raw"] == 204
        and failure_delivery["b6_profile_plus_0x09"] == 0
        and delivery["route_id"] == 42
        and seq["modulus"] == 64 and seq["gap_cap"] == 8 and seq["strict_plus_one_required"] is False
        and limits["command_limits"]["b6_lta_delta"]["raw_per_effective_sequence_gap"] == 78
    ):
        raise ValueError("joined B6 receiver contract drift")

    seq_examples = {
        "same_application_sequence": app_sequence(10, 10),
        "strict_plus_one": app_sequence(10, 11),
        "gap_four": app_sequence(10, 14),
        "wrap_gap_three": app_sequence(62, 1),
        "large_gap_capped": app_sequence(1, 20),
    }
    if seq_examples != {
        "same_application_sequence": (0, 1),
        "strict_plus_one": (1, 1),
        "gap_four": (4, 4),
        "wrap_gap_three": (3, 3),
        "large_gap_capped": (19, 8),
    }:
        raise ValueError("application sequence reference model drift")

    freshness_examples = {
        "committed10_received_low2_2": next_same_epoch_message(10, 2),
        "committed10_received_low2_3": next_same_epoch_message(10, 3),
        "committed11_received_low2_3": next_same_epoch_message(11, 3),
    }
    if freshness_examples != {
        "committed10_received_low2_2": 14,
        "committed10_received_low2_3": 11,
        "committed11_received_low2_3": 15,
    }:
        raise ValueError("freshness replay reference model drift")

    out = {
        "schema": "corolla-hf-b6-competing-sender-arbitration-v1",
        "applies_to": ["8965H1202000", "8965F1208000"],
        "sources": {
            "h_codeflash": {"path": str(H_IMAGE.relative_to(REPO)), "sha256": sha(h)},
            "f_codeflash": {"path": str(F_IMAGE.relative_to(REPO)), "application_sha256": sha(f[0x20000:])},
            "decompiler_evidence": {"path": str(EVIDENCE.relative_to(REPO)), "sha256": sha(EVIDENCE.read_bytes())},
            "secoc_verification": {"path": str(SECOC.relative_to(REPO)), "sha256": sha(SECOC.read_bytes())},
            "full_receiver": {"path": str(FULL.relative_to(REPO)), "sha256": sha(FULL.read_bytes())},
            "receiver_contract": {"path": str(RECEIVER.relative_to(REPO)), "sha256": sha(RECEIVER.read_bytes())},
            "steering_limits": {"path": str(LIMITS.relative_to(REPO)), "sha256": sha(LIMITS.read_bytes())},
            "hf_equivalence": {"path": str(EQUIV.relative_to(REPO)), "sha256": sha(EQUIV.read_bytes())},
        },
        "receiver_identity": {
            "can_id": "0x0B6",
            "application_pdu_id": 42,
            "authenticated_data_id": "0x00B6",
            "freshness_id": 2,
            "normal_freshness_slot": 1,
            "crypto_slot": 4,
            "separate_source_identifier_in_authenticated_input": False,
            "source_specific_acceptance_recovered": False,
            "boundary": "The receiver authenticates one generated B6/DataID/freshness profile. No sender/source identity is concatenated into the recovered CMAC input or used after verification. This is a receiver-side negative, not proof that upstream network topology has only one producer."
        },
        "single_profile_queue": {
            "ingress": "0x0008865A",
            "idle_E1": "first arrival changes E1->D2 and inserts the B6 profile once via 0x87CD6",
            "pending_D2": "another arrival while still D2 updates the existing B6 profile storage via 0x87DB0; it does not create a second queued B6 profile",
            "verify_C3_or_retry_B4": "0x8865A has no update/insert branch for C3 or B4, so newly arriving B6 PDUs during verification/retry are not admitted into the profile queue",
            "pending_arbitration": "last B6 arrival that updates the D2 pending slot before D2->C3 is the payload presented to verification",
            "inflight_arbitration": "once the worker transitions that profile to C3 (or B4 retry), later arrivals are ignored until cleanup returns the profile to E1",
            "queue_multiplicity": 1,
            "not_a_source_priority_queue": True,
        },
        "freshness_arbitration": {
            "committed_state_is_shared_per_b6_profile": True,
            "commit_before_normal_verified_application_delivery": True,
            "same_full_freshness_replay_after_commit": "does not authenticate as the same freshness: same-epoch reconstruction chooses the next congruent message8 value; the old CMAC therefore authenticates different freshness and fails verification absent a CMAC collision. During the separately recovered verification-failure forwarding grace/global-override modes, that failed queued payload can nevertheless be delivered to COM without committing freshness; outside those modes the failure handler does not route it.",
            "same_low2_reference_examples": {k: v for k, v in freshness_examples.items()},
            "future_freshness_from_another_capable_sender": "receiver has no source lock; a PDU that reconstructs to an acceptable future B6 freshness and carries a valid slot-4 CMAC can be accepted and then advances the single shared committed B6 freshness state",
            "verification_failure_forwarding_exception": {
                "grace_limit": 204,
                "b6_profile_plus_0x09": 0,
                "behavior": "0x888A6 can route a freshness-hard-failed or retry-exhausted CMAC-failed queued B6 to COM while the global grace counter is below 204 or the separate global D2 override mode is active; failure forwarding never commits freshness",
                "arbitration_effect": "the failure-forwarding window weakens freshness as an application-level duplicate barrier during that bounded mode; it does not turn the failed PDU into an authenticated success",
            },
            "consequence": "two independently transmitting slot-4-capable senders race one shared freshness state rather than coexist as independently tracked sources",
        },
        "application_sequence_arbitration": {
            "signal_id": 261,
            "modulus": 64,
            "raw_delta": "(current - previous) mod 64",
            "effective_gap": "1 for delta<=1, otherwise min(delta,8)",
            "strict_plus_one_required_by_eps": False,
            "duplicate_sequence_rejected": False,
            "examples": {k: {"raw_delta": v[0], "effective_gap": v[1]} for k, v in seq_examples.items()},
            "plausibility_use": "0xCB4F4 consumes effective_gap; H/F target-jump allowance is 78 raw per effective gap",
            "conclusion": "signal261 is a steering plausibility/time-gap input, not a duplicate-sender winner selector",
        },
        "request_id_arbitration": {
            "signal_id": 254,
            "accepted_active_ids": request["accepted_active_requests"],
            "decoder": "0x000CBE6E",
            "priority_order_recovered": None,
            "behavior": "the decoder clears all profile flags each call and selects at most the one profile encoded by the current B6 snapshot; it retains no competing-request history or priority ranking",
            "conclusion": "a later successfully delivered B6 can replace the active request/profile simply by carrying a different supported Target Lateral ID",
        },
        "application_delivery": {
            "entry": "0x00076A3C",
            "shared_shadow_pdu": 42,
            "behavior": "each successfully verified delivery copies the received PDU into the same COM PDU42 shadow, reloads the same deadline, and clears the same activity state",
            "sequential_valid_frames": "later successfully delivered B6 overwrites the current COM/application snapshot; there is no per-sender merge or priority state",
            "effective_policy": "last successfully delivered PDU is the current application command/profile, subject to task sampling",
        },
        "hypothesis_resolution": {
            "newest_application_sequence_wins": "disproved: signal261 does not select a winner and delta0 is tolerated as effective gap1",
            "source_specific_acceptance": "not recovered: one source-agnostic B6 SecOC profile/freshness/COM state is used",
            "first_or_last_frame_wins": "stage-dependent: D2 pending coalescing is last-arrival-wins; C3/B4 inflight arrivals are ignored; first successful commit consumes a given full freshness; across sequential accepted future freshness values the last COM delivery becomes current",
            "request_id_priority": "disproved: CBE6E decodes only the current value and has no cross-frame priority ranking",
            "freshness_rejects_competing_sender": "only indirectly: stale/replayed freshness fails authentication and freshness is not source-specific; additionally, the bounded verification-failure forwarding mode can still deliver a failed queued B6 without committing freshness. A valid future freshness from another capable sender can advance the same shared state normally.",
        },
        "suppression_conclusion": {
            "eps_protocol_requires_named_stock_source": False,
            "parallel_injection_safe": False,
            "freshness_preemption_is_safe_coexistence": False,
            "deterministic_lateral_authority_requires_exclusive_b6_control": True,
            "production_policy": "Suppress/isolate the stock B6 producer on the relay-correct path before openpilot emits B6, unless future capture proves the stock sender is quiescent for every state in which openpilot transmits. Do not use freshness racing/preemption as the coexistence mechanism.",
            "why": "The EPS has no source preference or request priority. Competing senders race a single pending queue slot and a single freshness state; whichever future-valid PDU is successfully delivered most recently becomes the one application command, while the bounded failure-forwarding mode can even expose a verification-failed queued PDU to COM without advancing freshness. That timing-dependent behavior is incompatible with deterministic openpilot authority and transparent fallback.",
            "physical_topology_boundary": "Static receiver logic cannot identify the relay side of the stock producer. The physical repin/capture is still required to locate and validate the actual suppression boundary.",
        },
        "cross_variant": {
            "h_f_application_byte_identical": True,
            "boundary": "Every function/table used by this contract lies in the H/F byte-identical application region 0x20000..0x100000, so the receiver arbitration transfers exactly between 8965H1202000 and 8965F1208000.",
        },
        "static_conclusion": {
            "source_specific_arbitration_absent": True,
            "single_pending_profile_queue_closed": True,
            "pending_last_arrival_coalescing_closed": True,
            "inflight_arrival_drop_closed": True,
            "same_freshness_replay_fails_authentication_by_forward_freshness_model": True,
            "verification_failure_forwarding_exception_closed": True,
            "application_sequence_not_duplicate_filter": True,
            "request_id_priority_absent": True,
            "sequential_delivery_last_snapshot_wins": True,
            "production_stock_suppression_still_required": True,
            "parallel_injection_authorized": False,
        },
        "evidence_boundary": "Receiver-side static result only. It does not authorize parallel injection, identify the physical stock producer side, recover sender cadence, reveal the ICU-S slot-4 secret, or prove stock B6 activity during any vehicle feature state."
    }

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
