#!/usr/bin/env python3
"""Verify the deterministic CUW cross-ECU SecurityAccess derivation artifact."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools/techstream"))

from analyze_cuw_cross_ecu_security_derivations import build

ART = ROOT / "data/generated/techstream_v18/cuw_cross_ecu_security_derivations.json"
expected = json.loads(ART.read_text())
actual = build()
assert actual == expected, "cross-ECU CUW derivation artifact drift"

control = actual["eps_control_specimen"]
assert control["eps_root_reproduces_actual_ecu_auth_key"] is True
assert control["actual_ecu_auth_key"] == "38adeef5ccae3f96d598d6fe9db14585"

pred = actual["high_value_non_eps_predictions"]
assert pred == {
    "0792": "5f1ca3df28378c808de34318288b056b",
    "07D2": "5693eea973333cf7a408bc86b1c98914",
    "0724": "192b8e45370251dff3b77f6bb069bf27",
}

groups = {(row["diag_id"], row["working_key"]): row for row in actual["credential_groups"]}
assert groups[("0792", "9318e0bfa4be96b787365ea2b5e26f3f")]["package_count"] == 6
assert groups[("07D2", "da4158ee9dd381cf7f9fc66da74682f3")]["package_count"] == 2
assert groups[("0724", "c178ed94d8dd00a65e520a536b7fa30c")]["package_count"] == 1
assert actual["simple_public_id_kdf_negative"]["matching_packages"] == []

payload = actual["eps_payload_root_cuw_trials"]
assert payload["packages_with_seedkey_nonce_grammar"] == [
    "T-0015-20.cuw",
    "T-0035-22.cuw",
    "T-0036-22.cuw",
]
assert payload["verified_shared_root_packages"] == ["T-0035-22.cuw", "T-0036-22.cuw"]
assert payload["rejected_same_root_packages"] == ["T-0015-20.cuw"]
trial_by_name = {trial["filename"]: trial for trial in payload["trials"]}
assert all(
    cpu["all_regions_cmac_valid"]
    for name in ("T-0035-22.cuw", "T-0036-22.cuw")
    for cpu in trial_by_name[name]["cpus"]
)
assert all(
    not region["cmac_valid"]
    for cpu in trial_by_name["T-0015-20.cuw"]["cpus"]
    for region in cpu["regions"]
)
assert all(trial["best_candidate"]["byte_identity_after_32"] < 0.01 for trial in actual["reprostd_image_key_trials"])

frc_kdf = actual["frc_reprostd_cbc_kdf_search"]
assert frc_kdf["sample_bytes_per_image"] == 0x10000
assert frc_kdf["sparse_block_count"] == 128
assert frc_kdf["base_atom_count"] == 112
assert frc_kdf["candidate_value_count"] == 43845
assert frc_kdf["full_score_top_n"] == 16
assert frc_kdf["interesting_identity_threshold"] == 0.01
assert [row["name"] for row in frc_kdf["pairs"]] == [
    "frc_f420_62_to_149",
    "frc_f160_61_to_150",
]
assert all(row["encoded_byte_identity_after_32"] < 0.01 for row in frc_kdf["pairs"])
assert frc_kdf["candidates_at_or_above_threshold"] == []
assert frc_kdf["best_full_min_identity"] < 0.005
assert all(row["full_min_identity"] < 0.005 for row in frc_kdf["top_full_results"])
assert "not an exhaustive KDF search" in frc_kdf["boundary"]

extended = actual["frc_reprostd_extended_kdf_audit"]
assert extended["shared_secret_variant_count"] == 32
assert extended["stable_context_variant_count"] == 28
assert extended["shared_stage1_value_count"] == 2688
assert extended["shared_candidate_value_count"] == 67157
assert extended["per_image_context_count"] == 75
assert extended["per_image_candidate_value_tuple_count"] == 49725
assert extended["total_candidate_key_hypothesis_count"] == 116882
assert extended["sample_bytes_per_image"] == 0x10000
assert extended["sparse_block_count"] == 64
assert extended["full_rescore_top_n"] == 32
assert extended["best_sparse_min_identity"] < 0.011
assert extended["candidates_at_or_above_threshold"] == []
assert all(row["full_min_identity"] < 0.005 for row in extended["top_full_results"])
assert any("Kimage=AES-128-ECB-ENC" in row for row in extended["known_toyota_constructions_covered"])
assert "only the top 32 sparse results" in extended["boundary"]

a32 = extended["routine_a32_baselines"]
assert a32["bottlenose_r4_first_1376_bytes"]["shape_score"] > 0.6
assert a32["encrypted_routine_as_little_endian_words"]["shape_score"] < 0.02
assert max(row["shape_score"] for row in extended["routine_a32_top_candidates"]) < 0.1
assert all(row["push_pop_count"] == 0 and row["return_count"] == 0
           for row in extended["routine_a32_top_candidates"])
assert "sibling A32 compiler-output baseline only" in a32["bottlenose_scope"]

print("CUW cross-ECU SecurityAccess derivations: PASS")
