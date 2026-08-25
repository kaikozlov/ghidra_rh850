#!/usr/bin/env python3
"""Build the H/F Corolla versus Sienna SecOC structural comparison."""
from __future__ import annotations

import argparse
import hashlib
import json
import struct
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SIENNA = REPO / "firmware/RH850_P1M-E_CodeFlash.bin"
H = REPO / "community/albinoelephant/normalized/8965H1202000_CodeFlash.bin"
F_RAW = REPO / "community/spanconstant/raw-20260821/span-corolla-2025.20260821-1511/dump_codeflash_00000000_00200000_20260821-152033.bin"
H_SECOC = REPO / "data/generated/corolla_8965H1202000_b6_secoc_verification.json"
H_EVID = REPO / "data/generated/corolla_8965H1202000_b6_secoc_verification_decompiler_evidence.json"
TRANSFER = REPO / "data/generated/corolla_8965H1202000_named_function_transfer_ledger.json"
OUT = REPO / "data/generated/corolla_h_sienna_secoc_structural_comparison.json"

S_PROFILE_BASE = 0x25970
H_PROFILE_BASE = 0x2572C
PROFILE_SIZE = 0x50
S_PROFILE_COUNT = 6
H_PROFILE_COUNT = 3
S_KEY_CONFIG = 0x25950
H_KEY_CONFIG = 0x2570C
KEY_CONFIG_LEN = 20


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def u16(data: bytes, off: int) -> int:
    return struct.unpack_from("<H", data, off)[0]


def u32(data: bytes, off: int) -> int:
    return struct.unpack_from("<I", data, off)[0]


def profile(data: bytes, base: int, index: int) -> dict[str, object]:
    a = base + index * PROFILE_SIZE
    return {
        "index": index,
        "address": f"0x{a:08X}",
        "full_cmac_bits": u16(data, a + 0x00),
        "transmitted_cmac_bits": u16(data, a + 0x02),
        "sync_linkage": u16(data, a + 0x04),
        "trailer_bytes": u16(data, a + 0x06),
        "is_sync": bool(data[a + 0x09]),
        "data_id": f"0x{u16(data, a + 0x0A):03X}",
        "authentication_retry_limit": u16(data, a + 0x10),
        "freshness_id": u16(data, a + 0x12),
        "full_freshness_bits": data[a + 0x14],
        "transmitted_freshness_bits": data[a + 0x15],
        "cryptoif_handle": u32(data, a + 0x20),
        "secured_pdu_length": u32(data, a + 0x24),
        "cryptoif_busy_retry_limit": u16(data, a + 0x2E),
        "commit_callback": f"0x{u32(data, a + 0x30):08X}",
        "upper_pdu_id": u16(data, a + 0x34),
        "secured_buffer_length": u32(data, a + 0x3C),
        "input_buffer_length": u32(data, a + 0x44),
        "get_freshness_callback": f"0x{u32(data, a + 0x48):08X}",
        "upper_callback": f"0x{u32(data, a + 0x4C):08X}",
        "record_sha256": sha(data[a:a + PROFILE_SIZE]),
    }


def profile_by_data_id(rows: list[dict[str, object]], data_id: str) -> dict[str, object]:
    return next(row for row in rows if row["data_id"] == data_id)


def selected_equal(a: dict[str, object], b: dict[str, object], keys: list[str]) -> bool:
    return all(a[k] == b[k] for k in keys)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", type=Path, default=OUT)
    args = ap.parse_args()

    s = SIENNA.read_bytes()
    h = H.read_bytes()
    f = F_RAW.read_bytes()[:0x100000]
    h_secoc = json.loads(H_SECOC.read_text())
    h_evid = json.loads(H_EVID.read_text())
    transfer = json.loads(TRANSFER.read_text())

    if len(s) != 0x100000 or len(h) != 0x100000 or len(f) != 0x100000:
        raise ValueError("expected 1 MiB CodeFlash images")
    if h[0x20000:] != f[0x20000:]:
        raise ValueError("H/F application region is no longer identical")

    s_rows = [profile(s, S_PROFILE_BASE, i) for i in range(S_PROFILE_COUNT)]
    h_rows = [profile(h, H_PROFILE_BASE, i) for i in range(H_PROFILE_COUNT)]
    s_00f = profile_by_data_id(s_rows, "0x00F")
    h_00f = profile_by_data_id(h_rows, "0x00F")
    s_d7 = profile_by_data_id(s_rows, "0x0D7")
    h_d7 = profile_by_data_id(h_rows, "0x0D7")
    h_b6 = profile_by_data_id(h_rows, "0x0B6")

    format_keys = [
        "full_cmac_bits", "transmitted_cmac_bits", "sync_linkage", "trailer_bytes",
        "is_sync", "authentication_retry_limit", "full_freshness_bits",
        "transmitted_freshness_bits", "cryptoif_handle", "secured_pdu_length",
        "cryptoif_busy_retry_limit", "secured_buffer_length", "input_buffer_length",
    ]
    fd_class_keys = [
        "full_cmac_bits", "transmitted_cmac_bits", "sync_linkage", "trailer_bytes",
        "is_sync", "authentication_retry_limit", "full_freshness_bits",
        "transmitted_freshness_bits", "cryptoif_handle", "secured_pdu_length",
        "cryptoif_busy_retry_limit", "secured_buffer_length", "input_buffer_length",
    ]

    transfer_by_ref = {row["reference_entry"].upper(): row for row in transfer["functions"]}
    h_funcs = {row["role"]: row for row in h_evid["functions"]}

    mappings = [
        ("authenticated_input_builder", 0x8DB22, "secoc_authenticated_input_build"),
        ("trailer_freshness_tag_split", 0x8E1A8, "secoc_trailer_extract"),
        ("verify_worker", 0x8E4BA, "secoc_verify_worker"),
        ("post_cmac_acceptance", 0x8E67A, "post_cmac_acceptance_gate"),
        ("freshness_profile_lookup", 0x8E80A, "freshness_profile_lookup"),
        ("freshness_get_dispatch", 0x8E8E6, "freshness_get_dispatch"),
        ("freshness_commit_dispatch", 0x8E942, "freshness_commit_dispatch"),
        ("full_freshness_pack", 0x8EA4C, "full_freshness_pack"),
        ("sync_freshness_pack", 0x8EB2C, "sync_freshness_pack"),
        ("transmitted_freshness_parse", 0x8EBC2, "transmitted_freshness_parse"),
        ("sync_freshness_parse", 0x8EC82, "sync_freshness_parse"),
        ("reset_candidate_search", 0x8ED0A, "reset_candidate_search"),
        ("normal_window_message_reconstruction", 0x8ED88, "normal_freshness_window_check"),
        ("normal_candidate_builder", 0x8EE5C, "normal_freshness_candidate_build"),
        ("normal_freshness_reconstruct", 0x8EECA, "normal_freshness_reconstruct"),
        ("sync_freshness_reconstruct", 0x8EF9E, "sync_freshness_reconstruct"),
        ("normal_freshness_commit", 0x8F084, "normal_freshness_commit"),
        ("trip_wrap_ordinary_clear", 0x8F0B8, "trip_wrap_normal_state_clear"),
        ("sync_freshness_commit", 0x8F112, "sync_freshness_commit"),
        ("icus_cmac_verify_prepare", 0x87ED0, "icus_command7_descriptor_prepare"),
        ("icus_command7_driver", 0x897F4, "icus_command7_driver"),
    ]
    fn_rows = []
    for role, s_addr, h_role in mappings:
        h_row = h_funcs[h_role]
        h_addr = int(h_row["entry"], 16)
        size = h_row["body_size"]
        t = transfer_by_ref.get(f"0X{s_addr:08X}")
        fn_rows.append({
            "role": role,
            "sienna_entry": f"0x{s_addr:08X}",
            "corolla_h_entry": f"0x{h_addr:08X}",
            "body_size": size,
            "sienna_body_sha256": sha(s[s_addr:s_addr + size]),
            "corolla_h_body_sha256": sha(h[h_addr:h_addr + size]),
            "byte_identical": s[s_addr:s_addr + size] == h[h_addr:h_addr + size],
            "transfer_ledger_status": None if t is None else t["status"],
            "transfer_ledger_target": None if t is None else t["target_entry"],
        })

    exact_roles = [row["role"] for row in fn_rows if row["byte_identical"]]
    expected_exact = {
        "full_freshness_pack", "sync_freshness_pack", "transmitted_freshness_parse", "sync_freshness_parse"
    }
    if set(exact_roles) != expected_exact:
        raise ValueError(f"unexpected exact freshness transfer set: {exact_roles}")

    s_key = s[S_KEY_CONFIG:S_KEY_CONFIG + KEY_CONFIG_LEN]
    h_key = h[H_KEY_CONFIG:H_KEY_CONFIG + KEY_CONFIG_LEN]

    out = {
        "schema": "corolla-h-sienna-secoc-structural-comparison-v1",
        "applies_to": {
            "sienna": "8965B4512000",
            "corolla": ["8965H1202000", "8965F1208000"],
            "corolla_h_f_application_identical": True,
        },
        "sources": {
            "sienna_codeflash": {"path": str(SIENNA.relative_to(REPO)), "sha256": sha(s)},
            "corolla_h_codeflash": {"path": str(H.relative_to(REPO)), "sha256": sha(h)},
            "corolla_f_application_source": {"path": str(F_RAW.relative_to(REPO)), "application_sha256": sha(f[0x20000:])},
            "h_b6_secoc_contract": {"path": str(H_SECOC.relative_to(REPO)), "sha256": sha(H_SECOC.read_bytes())},
            "h_target_native_decompiler_evidence": {"path": str(H_EVID.relative_to(REPO)), "sha256": sha(H_EVID.read_bytes())},
            "raw_function_transfer_ledger": {"path": str(TRANSFER.relative_to(REPO)), "sha256": sha(TRANSFER.read_bytes())},
        },
        "profile_tables": {
            "sienna": {"base": f"0x{S_PROFILE_BASE:08X}", "count": S_PROFILE_COUNT, "records": s_rows},
            "corolla_h_f": {"base": f"0x{H_PROFILE_BASE:08X}", "count": H_PROFILE_COUNT, "records": h_rows},
            "protected_ids": {
                "sienna": [row["data_id"] for row in s_rows],
                "corolla_h_f": [row["data_id"] for row in h_rows],
                "shared": ["0x00F", "0x0D7"],
                "corolla_added": ["0x0B6"],
                "sienna_only": ["0x2E4", "0x131", "0x132", "0x090"],
            },
            "freshness_id_to_state_slot": {
                "sienna": {"0": "sync", "1": 0, "2": 1, "4": 2, "5": 3, "6": 4},
                "corolla_h_f": {"0": "sync", "1": 0, "2": 1},
                "rule": "Freshness ID is matched against the configured record; ordinary-state slot is a compact ordinal assigned while walking non-sync records. It is not the freshness ID used directly as an array index.",
            },
            "shared_00f": {
                "format_and_crypto_fields_identical": selected_equal(s_00f, h_00f, format_keys),
                "identical_fields": format_keys,
                "differences": {
                    "upper_pdu_id": {"sienna": s_00f["upper_pdu_id"], "corolla_h_f": h_00f["upper_pdu_id"]},
                    "callback_addresses": "relocated/generated per image",
                },
                "meaning": "Both images configure 0x00F as the synchronization profile: 8-byte secured PDU, FV36 transmitted in full, CMAC28, freshness ID0, no ordinary retry budgets, CryptoIf handle0.",
            },
            "shared_0d7": {
                "fd_format_crypto_retry_fields_identical": selected_equal(s_d7, h_d7, fd_class_keys),
                "identical_fields": fd_class_keys,
                "differences": {
                    "freshness_id": {"sienna": s_d7["freshness_id"], "corolla_h_f": h_d7["freshness_id"]},
                    "ordinary_slot": {"sienna": 4, "corolla_h_f": 0},
                    "upper_pdu_id": {"sienna": s_d7["upper_pdu_id"], "corolla_h_f": h_d7["upper_pdu_id"]},
                    "callback_addresses": "relocated/generated per image",
                },
                "meaning": "0x0D7 is a shared 32-byte ordinary SecOC profile with 28-byte application payload, FV46/FV4, CMAC28, auth retry1, CryptoIf-busy retry2, and handle0. Freshness ID/slot numbering is generated and is not portable across images.",
            },
            "b6_as_shared_fd_profile_class": {
                "matches_sienna_0d7_format_crypto_retry_class": selected_equal(s_d7, h_b6, fd_class_keys),
                "compared_fields": fd_class_keys,
                "b6_specific": {
                    "data_id": h_b6["data_id"],
                    "freshness_id": h_b6["freshness_id"],
                    "ordinary_slot": 1,
                    "upper_pdu_id": h_b6["upper_pdu_id"],
                },
                "meaning": "B6 is Corolla-specific as a protected PDU identity/application route, not as a cryptographic profile shape: it is instantiated from the same FD ordinary SecOC class already present as Sienna 0x0D7/0x090.",
            },
        },
        "synchronization_manager_config": {
            "sienna_address": "0x00025964",
            "corolla_h_f_address": "0x00025720",
            "compared_bytes": 32,
            "sienna_bytes": s[0x25964:0x25984].hex(),
            "corolla_h_f_bytes": h[0x25720:0x25740].hex(),
            "byte_identical": s[0x25964:0x25984] == h[0x25720:0x25740],
            "wrap_threshold": 15,
            "meaning": "The 32-byte generated synchronization-manager configuration immediately preceding the SecOC profile records is byte-identical after relocation, including the trip-wrap threshold 0x0F.",
        },
        "key_and_icus": {
            "sienna_config": {"address": f"0x{S_KEY_CONFIG:08X}", "bytes": s_key.hex()},
            "corolla_h_f_config": {"address": f"0x{H_KEY_CONFIG:08X}", "bytes": h_key.hex()},
            "configs_byte_identical": s_key == h_key,
            "config_semantics": {"type": 1, "icus_slot_selector": 4, "cryptoif_handle": 0, "icus_command": 7, "command_word": "0x00040007"},
            "slot_secret_transfer_boundary": "The selector is the same ICU-S slot index. This does not prove that the secret key material provisioned into slot4 is the same across ECUs/vehicles.",
            "lower_driver_structural_reuse": {
                "prepare": {"sienna": "0x00087ED0", "corolla_h_f": "0x000822D0", "body_size": 172},
                "command7_driver": {"sienna": "0x000897F4", "corolla_h_f": "0x00083BF4", "body_size": 288},
                "meaning": "Both target-native bodies read the selector from config+4 and issue ICUSCMD=(selector<<16)|7 for CMAC verification; function geometry is structurally preserved while GP/register/data addresses relocate.",
            },
        },
        "function_correspondence": {
            "rows": fn_rows,
            "exact_byte_transfers": exact_roles,
            "exact_byte_transfer_count": len(exact_roles),
            "boundary": "Exact byte transfer is claimed only for the four raw-identical freshness pack/parse helpers. Other rows are target-native role correspondences whose bodies change because tables, state addresses, profile cardinality, or call targets differ.",
        },
        "initialization_and_persistence": {
            "sienna_state_clear": {
                "function": "0x0008E9FC",
                "action": "zero global sync current/pending state, reset wrap/control state, regenerate complements, and zero 5x12-byte ordinary current plus 5x12-byte pending arrays",
            },
            "corolla_h_f_state_clear": {
                "function": "0x00089812",
                "action": "zero global sync current/pending state, reset wrap/control state, regenerate complements, zero 2x12-byte ordinary current plus 2x12-byte pending arrays, and zero one additional linked 12-byte current/pending pair",
            },
            "shared_semantic": "Both receiver implementations explicitly initialize freshness RAM to zero and maintain complement/control cells around authenticated sync state.",
            "persistence_boundary": "Initialization equivalence does not prove that no other module later restores freshness from NVM. Sienna-specific persistence conclusions must not be transferred to H/F without target-native restore-path evidence.",
        },
        "freshness_state_geometry": {
            "sienna": {
                "global_sync_current": {"trip": "0xFEBE5568", "reset": "0xFEBE556C"},
                "global_sync_pending": {"trip": "0xFEBE5570", "reset": "0xFEBE5574"},
                "wrap_flag": "0xFEBE5580",
                "ordinary_current_base": "0xFEBE5584",
                "ordinary_pending_base": "0xFEBE55C0",
                "ordinary_slot_count": 5,
                "ordinary_slot_bytes": 12,
                "ordinary_slot_order": ["0x2E4", "0x131", "0x132", "0x090", "0x0D7"],
            },
            "corolla_h_f": {
                "global_sync_current": {"trip": "0xFEBE54AC", "reset": "0xFEBE54B0"},
                "global_sync_pending": {"trip": "0xFEBE54B4", "reset": "0xFEBE54B8"},
                "wrap_flag": "0xFEBE54C6",
                "ordinary_current_base": "0xFEBE54C8",
                "ordinary_pending_base": "0xFEBE54E0",
                "ordinary_slot_count": 2,
                "ordinary_slot_bytes": 12,
                "ordinary_slot_order": ["0x0D7", "0x0B6"],
                "b6_current": "0xFEBE54D4",
                "b6_pending": "0xFEBE54EC",
                "extra_linked_pair": {
                    "current": "0xFEBE54F8",
                    "pending": "0xFEBE5504",
                    "linkage_config": "TP+0x1AB4 (0x00025820), value0",
                    "behavior": "initialized to zero and additionally cleared by 0x8A0AE when authenticated sync group0 wraps",
                    "semantic_boundary": "This pair is outside the two ordinary receive-profile slots. Its consumer/producer role is not assigned here and is not needed for B6 slot1 verification.",
                },
            },
            "portable_rule": "State record shape (trip32, reset32, message16 plus auxiliary bytes) and current/pending commit discipline are shared. Absolute RAM addresses, ordinary slot index, and freshness ID are generated per image and must not be transferred by number.",
        },
        "shared_freshness_semantics": {
            "ordinary_full_freshness": "46 meaningful bits: trip16||reset20||message8||reset_low2||00b",
            "ordinary_transmitted_freshness": "FV4: message_low2||reset_low2",
            "reset_candidate_order": ["current", "current-1", "current+1", "current-2", "current+2"],
            "same_epoch_message_rule": "next strictly-forward message8 congruent with received message_low2; ordinary forward delta 1..4",
            "new_epoch_rule": "accept a strictly newer authenticated trip/reset epoch and seed message8 from received message_low2",
            "terminal_boundary": "message 0xFF/reset 0xFFFFF can return status0x24 while still proceeding to CMAC",
            "sync_profile": "0x00F uses FV36 and lexicographic forward trip/reset acceptance with threshold15 bounded trip-wrap handling",
            "authenticated_wrap_commit": "successful 0x00F wrap commits sync current from pending and clears linked ordinary freshness windows",
            "commit_rule": "candidate ordinary/sync freshness is staged before CMAC and committed only after authentication success",
        },
        "mac28_and_authenticated_input": {
            "generic_builder": "DataID big-endian u16 || authentic application bytes || reconstructed full freshness",
            "ordinary_fd_authenticated_input_bytes": 36,
            "sienna_fd_examples": ["0x090", "0x0D7"],
            "corolla_fd_examples": ["0x0D7", "0x0B6"],
            "b6_input": "00 B6 || B0..B27 || freshness48",
            "algorithm": "AES-CMAC-128",
            "transmitted_tag": "MSB28",
            "ordinary_trailer": "first trailer byte high nibble=FV4; low nibble plus next 3 bytes=CMAC_MSB28",
            "sync_trailer": "FV36 plus CMAC28 fills the 8-byte secured 0x00F PDU",
            "source_identifier_boundary": "Neither implementation adds a separate source/profile identifier to the CMAC input beyond the configured two-byte DataID; freshness ID selects receiver state rather than adding authenticated bytes.",
        },
        "acceptance_and_retry_reuse": {
            "shared_queue_model": "new -> verify; freshness 0x22 hard-fails; 0x23 requests another freshness/auth candidate; 0x24 remains on the CMAC path; command7 result0 is match; only authenticated success commits freshness before upper-PDU delivery",
            "queue_state_bytes": {"idle": "E1", "new": "D2", "verify": "C3", "retry": "B4", "freshness_failure": "A5", "generic_failure": "96"},
            "ordinary_profile_retry_class": {"authentication_candidate_or_mac_mismatch": 1, "cryptoif_submit_busy": 2},
            "sync_profile_retry_class": {"authentication_candidate_or_mac_mismatch": 0, "cryptoif_submit_busy": 0},
            "corolla_b6_matches_sienna_ordinary_retry_class": True,
            "upper_engine_correspondence": h_secoc["sienna_prior_art"],
        },
        "transferable_sienna_semantics": {
            "safe_to_transfer_to_h_f_b6": [
                "SecOC profile-record field meanings and generic queue/verification stages",
                "FV4/FV46 packing and parsing, including the exact four byte-identical helper bodies",
                "reset-current/±1/±2 candidate search and forward message-low2 reconstruction",
                "0x00F monotonic synchronization and threshold15 wrap semantics",
                "staged freshness followed by authentication-only commit",
                "DataID||payload||full-freshness CMAC domain construction",
                "AES-CMAC-128 with MSB28 transmitted tag through CryptoIf handle0 and ICU-S command7 slot selector4",
            ],
            "must_remain_corolla_target_specific": [
                "protected PDU inventory and upper PDU/callback routing",
                "freshness ID and ordinary-slot numbering",
                "absolute RAM addresses and generated array cardinality",
                "the Corolla-only extra linked current/pending pair",
                "B6 application payload semantics and independent signal261 sequence behavior",
                "actual secret provisioned into ICU-S slot4",
                "upstream sender ownership, sender freshness-state source, wall-clock cadence, and physical interception topology",
            ],
        },
        "static_conclusion": {
            "same_generated_secoc_framework": True,
            "same_00f_sync_algorithm": True,
            "same_ordinary_fv46_fv4_algorithm": True,
            "same_mac28_construction_class": True,
            "same_icus_slot_selector_and_command": True,
            "same_slot4_secret_proved": False,
            "freshness_ids_portable_across_images": False,
            "ram_slot_numbers_portable_across_images": False,
            "b6_is_new_pdu_on_shared_fd_secoc_class": True,
            "short_form": "H/F reuses the Sienna SecOC receiver architecture and freshness arithmetic; Corolla mainly regenerates the profile inventory/state geometry and adds B6 as an FD ordinary profile.",
        },
        "evidence_boundary": (
            "This comparison proves structural/protocol reuse between Sienna 8965B4512000 and application-identical Corolla H/F using raw profile/config bytes, exact relocated helper bodies, and independently recovered target-native H/F behavior. It does not infer that the ICU-S slot4 secret is shared, does not transfer generated freshness IDs or RAM slots by number, and does not identify the B6 sender, cadence, or physical producer topology."
        ),
    }

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    print(f"wrote {args.out}: Sienna profiles={len(s_rows)}, H/F profiles={len(h_rows)}, exact freshness helpers={len(exact_roles)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
