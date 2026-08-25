#!/usr/bin/env python3
"""Build the complete H/F protected-0x0B6 SecOC receiver verification contract."""
from __future__ import annotations

import argparse
import hashlib
import json
import struct
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
IMAGE = REPO / "community/albinoelephant/normalized/8965H1202000_CodeFlash.bin"
F_RAW = REPO / "community/spanconstant/raw-20260821/span-corolla-2025.20260821-1511/dump_codeflash_00000000_00200000_20260821-152033.bin"
EVID = REPO / "data/generated/corolla_8965H1202000_b6_secoc_verification_decompiler_evidence.json"
FULL = REPO / "data/generated/corolla_8965H1202000_b6_full_receiver_contract.json"
BASE = REPO / "data/generated/corolla_8965H1202000_b6_receiver_contract.json"
KEYS = REPO / "data/generated/corolla_8965H1202000_secoc_key_provenance.json"
EQUIV = REPO / "data/generated/corolla_8965F1208000_vs_8965H1202000_codeflash_equivalence.json"
OUT = REPO / "data/generated/corolla_8965H1202000_b6_secoc_verification.json"

TP = 0x23D6C
GP = 0xFEBEB800
B6_RECORD = 0x257CC
B6_PROFILE_INDEX = 2
MAX_RESET = 0xFFFFF
MAX_MESSAGE = 0xFF


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def need(text: str, *tokens: str) -> None:
    missing = [token for token in tokens if token not in text]
    if missing:
        raise ValueError("missing target-native decompiler token(s): " + ", ".join(missing))


def reset_trials(current_reset: int) -> list[tuple[int, int]]:
    """Exact 0x89CDA trial order as (trial_index, candidate_reset)."""
    if not 0 <= current_reset <= MAX_RESET:
        raise ValueError("reset outside 20-bit domain")
    out = [(0, current_reset)]
    if current_reset > 0:
        out.append((1, current_reset - 1))
    if current_reset < MAX_RESET:
        out.append((2, current_reset + 1))
    if current_reset > 1:
        out.append((3, current_reset - 2))
    if current_reset < MAX_RESET - 1:
        out.append((4, current_reset + 2))
    return out


def select_reset_candidate(current_reset: int, received_low2: int, attempt: int) -> tuple[int, int] | None:
    """Select attempt-th reset candidate whose low two bits match received FV4."""
    matches = [(trial, value) for trial, value in reset_trials(current_reset) if (value & 3) == received_low2]
    return matches[attempt] if 0 <= attempt < len(matches) else None


def next_message_candidate(committed: int, received_low2: int) -> tuple[int, bool]:
    """Same-epoch 0x89D58 message reconstruction for reset<0xFFFFF.

    Returns (candidate, boundary_0x24).  The special boundary maps an otherwise
    overflowing next congruent value to 0xFF; the outer wrapper reports 0x24 but
    the generic worker still proceeds to CMAC verification.
    """
    if not 0 <= committed <= MAX_MESSAGE or not 0 <= received_low2 < 4:
        raise ValueError("message counter outside domain")
    candidate = (committed & ~3) | received_low2
    if received_low2 <= (committed & 3):
        candidate += 4
    if candidate <= MAX_MESSAGE:
        return candidate, False
    return MAX_MESSAGE, True


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--image", type=Path, default=IMAGE)
    ap.add_argument("--evidence", type=Path, default=EVID)
    ap.add_argument("--out", type=Path, default=OUT)
    args = ap.parse_args()

    h = args.image.read_bytes()
    f = F_RAW.read_bytes()[:0x100000]
    ev = json.loads(args.evidence.read_text())
    full = json.loads(FULL.read_text())
    base = json.loads(BASE.read_text())
    keys = json.loads(KEYS.read_text())
    equiv = json.loads(EQUIV.read_text())
    if len(h) != 0x100000 or sha(h) != ev["image"]["sha256"]:
        raise ValueError("H image/evidence identity drift")
    if ev["function_count"] != 36:
        raise ValueError("H B6 SecOC verification evidence count drift")
    funcs = {int(row["entry"], 16): row["decompiled_c"] for row in ev["functions"]}

    # Exact B6 profile and normal-profile slot mapping.  H has one sync profile
    # (00F) followed by two ordinary profiles (D7, B6), so freshness ID2 maps to
    # ordinary slot1 even though the queue/SecOC record index is 2.
    records = [h[0x2572C + i * 0x50:0x2572C + (i + 1) * 0x50] for i in range(3)]
    if any(len(r) != 0x50 for r in records):
        raise ValueError("SecOC record table truncated")
    record = records[B6_PROFILE_INDEX]
    normal_slot = -1
    normal_count = 0
    for i, row in enumerate(records):
        is_sync = row[9] == 1
        if i == B6_PROFILE_INDEX:
            normal_slot = 0 if is_sync else normal_count
        if not is_sync:
            normal_count += 1
    if not (
        normal_slot == 1 and normal_count == 2
        and struct.unpack_from("<H", record, 0x0A)[0] == 0x00B6
        and struct.unpack_from("<H", record, 0x10)[0] == 1
        and struct.unpack_from("<H", record, 0x12)[0] == 2
        and record[0x14] == 46 and record[0x15] == 4
        and struct.unpack_from("<H", record, 0x2E)[0] == 2
        and struct.unpack_from("<I", record, 0x30)[0] == 0x89758
        and struct.unpack_from("<H", record, 0x34)[0] == 42
        and struct.unpack_from("<I", record, 0x48)[0] == 0x896B0
        and struct.unpack_from("<H", record, 0x04)[0] == 0
    ):
        raise ValueError("B6 profile/retry/slot geometry drift")

    # Target-native function semantics.  These intentionally cover the details
    # that the earlier byte-complete receiver artifact left open.
    need(funcs[0x8857C], "FUN_00083444(unaff_gp + -0x63fc,4);", "*(undefined1 *)(iVar1 + -0x63f0) = 0xe1;", "uVar2 < 3")
    need(funcs[0x88702], "cVar2 == -0x2e", "cVar2 == -0x4c", "cVar3 = -0x3d", "unaff_gp + -0x63fa) = 0;")
    need(funcs[0x8891E], "unaff_gp + -0x63fa", "unaff_tp + 0x19d0", "*pcVar1 = -0x4c", "uVar2 + 1", "unaff_gp + -0x63fc) = 0;", "uVar4 = 2", "uVar4 = 1")
    need(funcs[0x889C2], "unaff_gp + -0x63fc", "LAB_000019ee", "*pcVar1 = -0x4c", "uVar2 + 1")
    need(funcs[0x88A56], "FUN_00088702", "FUN_00088744", "unaff_gp + -0x63fa", "iVar7 == 0x22", "iVar7 == 0x24", "FUN_00088908", "iVar7 == 0x23", "FUN_0008891e", "unaff_gp + -0x63ec) = 0x24", "FUN_00087fc2", "FUN_00088986", "FUN_000889c2")
    need(funcs[0x88C9C], "FUN_00088a56", "iVar2 == 0", "FUN_00088c16")
    need(funcs[0x88C16], "unaff_gp + -0x63b0", "FUN_00088be2", "FUN_0008891e(uVar5,0x200)", "FUN_00088856(uVar5,0)")
    need(funcs[0x88BE2], "| 0x10000", "if (param_2 == '\\0')", "iVar1 + 0x19f0")
    need(funcs[0x89558], "sVar6 = sVar6 + 1", "iVar4 = 1", "iVar4 = 3", "2 < uVar5")
    need(funcs[0x89758], "param_1 >> 0x10 == 0", "FUN_0008a07a", "FUN_0008a130")
    need(funcs[0x89812], "unaff_gp + -0x6354,8", "unaff_gp + -0x634c,8", "unaff_gp + -0x6338,0x18", "unaff_gp + -0x6320,0x18")
    need(funcs[0x89A46], "if (param_2 == 4)", "*param_1 >> 6", "bVar1 = *param_1 >> 4", "bVar1 & 3")
    need(funcs[0x89CDA], "uVar1 = *(uint *)(unaff_gp + -0x6350);", "*(byte *)(param_2 + 10)", "if (4 < uVar3)", "uVar1 = uVar1 - 1", "uVar1 = uVar1 + 1", "uVar1 = uVar1 - 2", "uVar1 = uVar1 + 2", "sVar2 = sVar2 + -1")
    need(funcs[0x89D58], "uVar6 = *(uint *)(unaff_gp + -0x6354);", "unaff_gp + -0x6338", "uVar6 = *param_3;", "uVar7 = 1 << uVar6;", "uVar4 = *(ushort *)(param_2 + 8) | ~((short)uVar7 - 1U) & uVar2;", "uVar5 = param_3[4];", "uVar6 = uVar5 + uVar2", "0xfffff", "return 0x23", "return 0x22", "*(undefined2 *)(param_4 + 2) = 0xff")
    need(funcs[0x89E2C], "uStack_24 - 2", "uStack_24 = 2", "*(ushort *)(param_2 + 8) <=", "unaff_gp + -0x6330", "FUN_00089cda", "FUN_00089d58")
    need(funcs[0x89E9A], "FUN_00089a46", "FUN_00089e2c", "sStack_24 == 0xff", "iVar3 = 0x24", "unaff_gp + -0x6320", "FUN_00089876")
    need(funcs[0x8A07A], "param_1 < 2", "param_2 == '\\x01'", "unaff_gp + -0x6338", "unaff_gp + -0x6320", "0xc")
    need(funcs[0x89F6E], "0xffff - *(byte *)(unaff_tp + 0x19bc)", "bVar1", "unaff_gp + -0x634c", "unaff_gp + -0x6348", "return 0x22")
    need(funcs[0x8A130], "unaff_gp + -0x6354", "unaff_gp + -0x634c", "FUN_0008a0ae(0)")
    need(funcs[0x8A0AE], "unaff_gp + -0x6338", "unaff_gp + -0x6320", "sVar4 * 0xc", "iVar1 + 9")
    need(funcs[0x62430], "cStack_21 = '\\x01'", "FUN_00082fa8", "uStack_1c = cStack_21 == '\\0'")
    need(funcs[0x822D0], "*param_1 != 1", "*(uint *)(unaff_gp + 0x5974) = (uint)*(byte *)(param_1 + 1)")
    need(funcs[0x83BF4], "uVar9 = puVar2[4]", "uVar9 < 0xf", "Ramffc5d000 = uVar9 << 0x10 | 7")

    # Pure reference arithmetic independently reproduces the H candidate order
    # and the useful FV4 ambiguity.  These are emitted as executable examples
    # and rechecked again by the verifier.
    examples = {
        "reset_current_100_rx0_attempt0": select_reset_candidate(100, 0, 0),
        "reset_current_100_rx3_attempt0": select_reset_candidate(100, 3, 0),
        "reset_current_100_rx1_attempt0": select_reset_candidate(100, 1, 0),
        "reset_current_100_rx2_attempt0": select_reset_candidate(100, 2, 0),
        "reset_current_100_rx2_attempt1": select_reset_candidate(100, 2, 1),
        "message_10_rx3": next_message_candidate(10, 3),
        "message_10_rx2": next_message_candidate(10, 2),
        "message_254_rx3": next_message_candidate(254, 3),
        "message_253_rx0": next_message_candidate(253, 0),
    }
    expected = {
        "reset_current_100_rx0_attempt0": (0, 100),
        "reset_current_100_rx3_attempt0": (1, 99),
        "reset_current_100_rx1_attempt0": (2, 101),
        "reset_current_100_rx2_attempt0": (3, 98),
        "reset_current_100_rx2_attempt1": (4, 102),
        "message_10_rx3": (11, False),
        "message_10_rx2": (14, False),
        "message_254_rx3": (255, False),
        "message_253_rx0": (255, True),
    }
    if examples != expected:
        raise ValueError(f"reference freshness model drift: {examples!r}")

    # Key selection and authenticated-envelope facts are joined from separately
    # verified artifacts, then rechecked against the exact H profile/config bytes.
    envelope = full["wire_envelope"]
    selection = keys["shared_crypto_selection"]
    if not (
        envelope["authenticated_input"]["packing"] == "DataID_be16(0x00B6) || B0..B27 || reconstructed_freshness48"
        and envelope["authenticated_input"]["bytes"] == 36
        and envelope["profile"]["transmitted_authenticator_bits"] == 28
        and selection["secoc_crypto_config_id"] == 0
        and selection["cryptoif_job_handle"] == 0
        and selection["config_type"] == 1
        and selection["icus_slot_selector"] == 4
        and h[0x2570C:0x25720].hex() == selection["config_bytes"]
    ):
        raise ValueError("B6 authenticated envelope/key selector drift")

    # H/F transfer is exact for every address used here: the applications are
    # byte-identical from 0x20000 through the end of CodeFlash.
    app_eq = equiv["application_equivalence"]
    all_h_entries = [int(row["entry"], 16) for row in ev["functions"]] + [B6_RECORD, 0x2570C]
    if not (
        h[0x20000:0x100000] == f[0x20000:0x100000]
        and app_eq["identical"] is True and app_eq["different_bytes"] == 0
        and all(0x20000 <= entry < 0x100000 for entry in all_h_entries)
    ):
        raise ValueError("H/F SecOC verification-path identity drift")

    current_slot = GP - 0x6338 + normal_slot * 0x0C
    pending_slot = GP - 0x6320 + normal_slot * 0x0C
    sync_threshold = h[TP + 0x19BC]
    if sync_threshold != 0x0F:
        raise ValueError("sync trip-wrap threshold drift")

    out = {
        "schema": "corolla-8965H1202000-b6-secoc-verification-v1",
        "software_id": "8965H1202000",
        "applies_to": ["8965H1202000", "8965F1208000"],
        "sources": {
            "codeflash": {"path": str(args.image.relative_to(REPO)), "sha256": sha(h)},
            "decompiler_evidence": {"path": str(args.evidence.relative_to(REPO)), "sha256": sha(args.evidence.read_bytes()), "function_count": ev["function_count"]},
            "full_receiver_contract": {"path": str(FULL.relative_to(REPO)), "sha256": sha(FULL.read_bytes())},
            "base_receiver_contract": {"path": str(BASE.relative_to(REPO)), "sha256": sha(BASE.read_bytes())},
            "key_provenance": {"path": str(KEYS.relative_to(REPO)), "sha256": sha(KEYS.read_bytes())},
            "hf_equivalence": {"path": str(EQUIV.relative_to(REPO)), "sha256": sha(EQUIV.read_bytes())},
        },
        "identifiers": {
            "can_id": "0x0B6",
            "secoc_record_index": B6_PROFILE_INDEX,
            "secoc_record_address": f"0x{B6_RECORD:08X}",
            "application_pdu_id": 42,
            "upper_route_id": 42,
            "data_id_authenticated_be16": "0x00B6",
            "freshness_id": 2,
            "freshness_kind": "normal",
            "normal_freshness_slot": normal_slot,
            "normal_linkage_field_plus_0x04": 0,
            "secoc_crypto_config_id": 0,
            "cryptoif_job_handle": 0,
            "icus_command": 7,
            "icus_slot_selector": 4,
            "separate_source_identifier_in_cmac_input": False,
            "boundary": "The authenticated prefix is the 16-bit DataID 0x00B6. Freshness ID2 selects receiver state but is not separately concatenated into the 36-byte CMAC input. No additional source/profile identifier was recovered in that input."
        },
        "ram_state": {
            "gp": f"0x{GP:08X}",
            "b6_queue_state": f"0x{GP - 0x63F0 + B6_PROFILE_INDEX:08X}",
            "crypto_submit_retry_counter": f"0x{GP - 0x63FC:08X}",
            "authentication_candidate_retry_counter": f"0x{GP - 0x63FA:08X}",
            "cmac_verify_result_byte": f"0x{GP - 0x63B0:08X}",
            "global_sync_current_trip": f"0x{GP - 0x6354:08X}",
            "global_sync_current_reset": f"0x{GP - 0x6350:08X}",
            "global_sync_pending_trip": f"0x{GP - 0x634C:08X}",
            "global_sync_pending_reset": f"0x{GP - 0x6348:08X}",
            "b6_committed_slot": {"address": f"0x{current_slot:08X}", "bytes": 12, "fields": {"trip_u32": 0, "reset_u32": 4, "message_u16": 8}},
            "b6_pending_slot": {"address": f"0x{pending_slot:08X}", "bytes": 12, "fields": {"trip_u32": 0, "reset_u32": 4, "message_u16": 8}},
            "initialization": {
                "verify_engine": "0x0008857C clears both retry counters and initializes all three queue states to E1",
                "freshness": "0x00089812 zeros current/pending global sync state and both 12-byte ordinary current/pending slots",
                "persistence_boundary": "This proves application initialization writes these RAM cells; it does not by itself claim a whole-program negative for every possible external/NvM restoration path."
            },
        },
        "transmitted_freshness": {
            "bits": 4,
            "wire": "B28[7:4]",
            "decode": {"message_low2": "B28[7:6]", "reset_low2": "B28[5:4]"},
            "full_freshness": "trip16 || reset20 || message8 || reset_low2 || 00b",
            "full_bits": 46,
            "parser": "0x00089A46",
            "packer": "0x00089876",
        },
        "freshness_acceptance": {
            "global_epoch_source": {
                "secured_sync_can_id": "0x00F",
                "sync_freshness_id": 0,
                "sync_full_and_transmitted_bits": 36,
                "current_state": [f"0x{GP - 0x6354:08X}", f"0x{GP - 0x6350:08X}"],
                "reconstruct": "0x00089F6E",
                "commit": "0x0008A130",
                "commit_only_after_authentication_success": True,
            },
            "reset_candidate_search": {
                "function": "0x00089CDA",
                "base": "current authenticated 0x00F reset counter",
                "ordered_trials": ["current", "current-1", "current+1", "current-2", "current+2"],
                "domain": [0, MAX_RESET],
                "filter": "candidate_reset & 3 == transmitted reset_low2",
                "selection": "authentication_candidate_retry_counter selects the Nth matching trial",
                "ordinary_b6_retry_limit": 1,
                "important_ambiguity": "Only current-2 and current+2 collide in the two-bit transmitted reset domain; attempt0 chooses -2 (trial3) and the one allowed same-PDU retry can choose +2 (trial4).",
                "examples": {k: list(v) if isinstance(v, tuple) else v for k, v in examples.items() if k.startswith("reset_")},
            },
            "message_reconstruction_same_epoch": {
                "function": "0x00089D58",
                "condition": "global_trip == committed_trip and candidate_reset == committed_reset",
                "formula": "candidate=(committed_message & ~3)|received_message_low2; if received_low2 <= (committed_message & 3), candidate += 4",
                "ordinary_forward_delta": [1, 4],
                "strictly_forward": True,
                "overflow_behavior": "If the next congruent value would exceed 0xFF, the candidate message is forced to 0xFF and outer 0x89E9A returns status 0x24. The same 0xFF/status0x24 boundary is also reached when the selected reset is already 0xFFFFF.",
                "examples": {k: [v[0], v[1]] for k, v in examples.items() if k.startswith("message_")},
            },
            "epoch_transition": {
                "strictly_newer_rule": "global_trip > committed_trip OR (global_trip == committed_trip AND candidate_reset > committed_reset)",
                "new_epoch_message": "received_message_low2 (0..3)",
                "not_newer_rule": "older/equal candidate returns 0x23 while reset trial index <=3, otherwise 0x22",
                "staging": f"accepted/reconstructed candidate is copied to B6 pending slot {pending_slot:#010x} before CMAC",
            },
            "special_status_0x24": {
                "meaning": "message-0xFF or reset-0xFFFFF boundary candidate notification",
                "callback_dispatch": "0x00088908",
                "hard_reject": False,
                "cmac_still_runs": True,
                "reason": "0x88A56 calls 0x88908 then reaches the common C3 path that builds/submits command 7; unlike 0x23 it does not transition C3->B4.",
            },
            "trip_wrap": {
                "sync_threshold": sync_threshold,
                "wrap_acceptance": "when current trip >= 0xFFFF-15, a nonzero new trip <=16 is treated as forward wrap by 0x89F6E",
                "post_verified_sync_action": "0x8A130 commits pending global trip/reset; on wrap it calls 0x8A0AE(0), which clears current+pending ordinary freshness slots whose internal record+0x04 linkage field equals 0, including D7 and B6",
                "b6_state_cleared_on_authenticated_trip_wrap": True,
            },
        },
        "authenticated_envelope": {
            "application_bytes": 28,
            "authenticated_input_bytes": 36,
            "cmac_input": "00 B6 || B0..B27 || reconstructed_freshness[6]",
            "cmac_algorithm": "AES-CMAC-128",
            "transmitted_tag": "MSB28",
            "received_tag_bits": 28,
            "trailer": "B28[3:0] || B29 || B30 || B31 after FV4 removal/top-alignment",
            "submit_path": "0x88A56 -> 0x88986 -> CryptoIf job0 -> driver dispatch -> command7 prepare 0x822D0 -> ICU-S command7 0x83BF4",
            "icus_command_word": "(slot_selector << 16) | 7 = 0x00040007",
            "key_selection": "config0 type1 -> protected ICU-S slot4",
            "key_value_cpu_visible": False,
            "result_polarity": "command7 result byte 0 means verified/match; nonzero means mismatch",
            "result_evidence": "live 0x88C16 tests result!=0 as mismatch; disabled 0x62430 command7 KAT initializes result=1 and reports pass only when result becomes 0",
        },
        "acceptance_state_machine": {
            "queue_states": {"idle": "E1", "new": "D2", "verify": "C3", "retry": "B4", "freshness_failure": "A5", "generic_failure": "96"},
            "new_pdu_transition": "0x88702: D2->C3 and resets auth-candidate + CryptoIf-submit retry counters to zero",
            "same_pdu_retry_transition": "0x88702 itself performs B4->C3 without an additional reset; the caller that schedules an authentication retry (0x8891E) has already incremented the auth counter and reset the CryptoIf-submit counter to zero",
            "freshness_results": {
                "0x00": "candidate staged; continue to command7",
                "0x22": "hard freshness failure -> A5 -> cleanup; no command7 and no delivery",
                "0x23": "0x8891E(...,0x201) candidate retry; if below B6 limit1, C3->B4 and auth-candidate counter increments",
                "0x24": "call freshness-boundary callback through 0x88908; state remains C3 and command7 still executes",
            },
            "crypto_submit_result_2": "0x889C2(...,0x202) uses B6 record +0x2E limit2 for CryptoIf submit/busy retries of the current authentication candidate; B4->C3 preserves that counter across busy retries, while 0x8891E resets it when advancing to a new auth/freshness attempt",
            "gate1": "0x88C9C reaches post-CMAC gate only when 0x88A56 returns 0",
            "gate2": {
                "function": "0x00088C16",
                "result_cell": f"0x{GP - 0x63B0:08X}",
                "success": "result==0: freshness commit callback receives freshness ID2 with high16 clear, pending slot commits, then PDU42 routes to COM",
                "mismatch": "result!=0: freshness commit callback receives 0x00010002 so pending state does not commit; 0x8891E(...,0x200) may retry the same queued PDU; no PDU42 delivery on mismatch",
                "commit_before_delivery": True,
            },
            "retry_budgets": {
                "authentication_candidate_or_mac_mismatch": {"record_offset": "0x10", "limit": 1, "counter": f"0x{GP - 0x63FA:08X}", "scope": "current queued PDU", "interaction": "0x8891E increments this counter and resets the CryptoIf-submit counter before B4 retry"},
                "cryptoif_submit_busy": {"record_offset": "0x2E", "limit": 2, "counter": f"0x{GP - 0x63FC:08X}", "scope": "current authentication candidate/verification attempt within the queued PDU", "interaction": "0x889C2 increments it on driver result2; 0x8891E clears it when an auth/freshness retry is scheduled"},
            },
            "freshness_commit": {
                "dispatcher": "0x00089758",
                "normal_commit": "0x0008A07A",
                "success_action": f"copy pending 12-byte B6 slot {pending_slot:#010x} -> committed slot {current_slot:#010x}",
                "failure_action": "no copy; committed B6 freshness is unchanged",
            },
            "verified_delivery": full["verified_delivery"],
        },
        "application_sequence_relation": {
            "signal_id": 261,
            "wire": "B7[5:0]",
            "application_counter_bits": 6,
            "application_modulus": 64,
            "application_gap_cap": 8,
            "secoc_message_counter_bits": 8,
            "secoc_transmitted_message_bits": 2,
            "independent_counters": True,
            "relationship": "signal261 is ordinary authenticated application data inside B0..B27. SecOC freshness is reconstructed from B28[7:4] plus SecOC RAM state. Signal261 is unpacked/consumed only on the post-verification COM/application side and does not select the SecOC freshness candidate.",
            "sender_requirement": "Maintain both counters: a SecOC message8/reset/trip state for CMAC/FV4 and the independent application signal261 modulo-64 sequence for steering plausibility.",
            "application_consumer": base["companion_fields"]["261"],
        },
        "sienna_prior_art": ev["sienna_upper_engine_comparison"],
        "cross_variant": {
            "h_f_application_identical": True,
            "identical_range": ["0x20000", "0x100000"],
            "all_verification_functions_and_tables_inside_identical_range": True,
            "b6_secoc_verification_contract_byte_identical": True,
            "boundary": "H and F application bytes are identical for every record/config/function used by this proof. This does not transfer low-region calibration values or identify the upstream sender."
        },
        "sender_recipe": {
            "receiver_required_steps": [
                "Maintain a full freshness tuple consistent with the receiver's authenticated 0x00F trip/reset epoch and B6 message8 progression.",
                "Encode FV4 in B28[7:4] as message_low2||reset_low2.",
                "Build freshness48 as trip16||reset20||message8||reset_low2||00b.",
                "Compute AES-CMAC-128 over 00 B6 || B0..B27 || freshness48 using the key selected by protected ICU-S slot4.",
                "Transmit CMAC_MSB28 in B28[3:0],B29,B30,B31.",
                "Independently maintain application signal261 in B7[5:0] for steering sequence/plausibility semantics."
            ],
            "cryptographic_blocker": "The exact receiver selector is closed, but the slot-4 secret value remains opaque to mapped CPU/application code. A sender still needs that secret or an approved/available ICU-S operation that can produce the required tag.",
            "runtime_state_blocker": "The receiver algorithm is closed, but sender ownership/source of the live trip/reset/message state and stock wall-clock cadence remain outside this EPS receiver image.",
        },
        "static_conclusion": {
            "b6_freshness_extraction_closed": True,
            "b6_freshness_window_closed": True,
            "b6_mac_input_closed": True,
            "b6_key_slot_selection_closed": True,
            "b6_profile_identifiers_closed": True,
            "b6_sequence_relation_closed": True,
            "b6_accept_reject_state_machine_closed": True,
            "b6_commit_timing_closed": True,
            "b6_h_f_receiver_verification_identical": True,
            "slot4_secret_value_closed": False,
            "sender_freshness_state_ownership_closed": False,
            "sender_wall_clock_cadence_closed": False,
            "upstream_producer_closed": False,
            "short_form": "FV4 reconstructs against authenticated 00F state; candidate is staged, command7 verifies CMAC28 with slot4, and only result0 commits freshness then delivers PDU42."
        },
        "evidence_boundary": (
            "This closes the H/F EPS receiver-side SecOC verification algorithm for protected 0x0B6, including exact freshness state, "
            "candidate/window rules, retry scopes, CMAC input/slot selection, commit timing, and application-sequence separation. It "
            "does not recover the protected slot-4 secret, sender-side ownership of live freshness state, stock sender cadence, or the "
            "upstream FRC/Brake payload/signing producer."
        ),
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    print(f"wrote {args.out}: B6 slot={normal_slot}, auth_retry={struct.unpack_from('<H', record, 0x10)[0]}, submit_retry={struct.unpack_from('<H', record, 0x2E)[0]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
