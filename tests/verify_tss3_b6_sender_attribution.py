#!/usr/bin/env python3
"""Verify the bounded TSS3 Corolla B6 sender-attribution synthesis."""
from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
ARTIFACT = REPO / "data/generated/techstream_v18/tss3_b6_sender_attribution.json"
BUILDER = REPO / "tools/techstream/build_tss3_b6_sender_attribution.py"
H_CODE = REPO / "community/albinoelephant/normalized/8965H1202000_CodeFlash.bin"

passed = failed = 0
oracle = "generated_self_check+raw_bytes"


def check(name: str, condition: object, detail: str = "") -> None:
    global passed, failed
    ok = bool(condition)
    passed += int(ok)
    failed += int(not ok)
    print(f"[{'PASS' if ok else 'FAIL'}][{oracle}] {name}" + (f" ({detail})" if detail else ""))


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


spec = importlib.util.spec_from_file_location("b6_sender_attribution_builder", BUILDER)
assert spec and spec.loader
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

art = json.loads(ARTIFACT.read_text())
rebuilt = mod.build()
check("artifact regenerates exactly from pinned dependencies", art == rebuilt)
check("schema version", art["schema_version"] == 1)
check(
    "tracked H code identity pinned",
    sha256(H_CODE) == art["sources"]["community/albinoelephant/normalized/8965H1202000_CodeFlash.bin"]["sha256"]
    == "0b47bdc1217835c839e3543e52eab40eb793650a9c159e46f6a9b365ea41a67f",
)

corpus = art["corpus_boundary"]
check("six current FRC packages", corpus["frc_diag_id"] == "0792" and corpus["frc_package_count"] == 6)
check("all FRC packages are 0792 ReproMethod07", all(x["diag_id"] == "0792" and x["repro_method"] == "07" for x in corpus["frc_packages"]))
check("FRC stored images remain opaque/high entropy", all(x["decoded_image_entropy_bits_per_byte"] > 7.99 for x in corpus["frc_packages"]))
check("category-435 Brake package absent locally", corpus["category_435_brake_diag_id"] == "07B0" and corpus["category_435_brake_package_count"] == 0)
check("producer runtime code not searchable in current corpus", corpus["frc_runtime_code_searchable"] is False and corpus["brake_runtime_code_available"] is False)
check("literal producer-code search explicitly rejected", "unknown high-entropy representation" in corpus["consequence"])

sender = art["immediate_b6_sender_domain"]
check("immediate sender domain identified", sender["identified"] is True and sender["domain"] == "Brake System Control Module")
check("B6 endpoint identity exact", sender["eps_receive_can_id"] == "0x0B6" and sender["eps_receive_pdu_id"] == 42)
dtc = sender["techstream_dtc"]
check("B6 source-domain DTC exact", dtc["techstream_code"] == "U012987" and dtc["techstream_description"] == "Lost Communication with Brake System Control Module" and dtc["techstream_failure"] == "Missing Message")
check("Corolla brake family category/address exact", sender["corolla_p5_category"] == {"category_id": 435, "database": "ABS_P5.ddb", "display_name": "Brake/EPB", "diagnostic_request_address": "0x7B0", "functional_address": "0x7E5"})
check("originator/forwarder remains bounded", "does not distinguish originator from forwarder" in sender["boundary"])

family = art["authenticated_source_family"]
check("protected queue exact", family["h_protected_profiles"] == ["0x00F", "0x0D7", "0x0B6"])
check("one shared slot-4 config", family["shared_secoc_crypto_config_id"] == 0 and family["shared_icus_slot_selector"] == 4)
check("slot4 key remains hidden", family["slot4_key_value_cpu_visible"] is False)
check("D7/B6 brake-family interpretation bounded", "D7 and B6" in family["interpretation"] and "not proof" in family["boundary"])

up = art["upstream_origin_search"]
check("FRC->Brake and Brake->EPS dependencies identified", up["frc_to_brake_dependency_identified"] is True and up["brake_to_eps_dependency_identified"] is True)
check("direct FRC->EPS dependency also identified", up["frc_to_eps_dependency_also_identified"] is True)
check("payload transform remains open", up["payload_forwarding_or_transform_identified"] is False)
check("signing owner remains open", up["secoc_signing_owner_identified"] is False)

axes = art["requested_search_axes"]
check("32-byte Tx descriptor search correctly blocked", axes["fd32_transmit_descriptor"]["status"] == "blocked_by_corpus_representation")
check("SecOC generation-call search correctly blocked", axes["secoc_generation_calls"]["status"] == "blocked_by_corpus_representation")
req = axes["target_lateral_request_ids"]
check("accepted request IDs exact", req["accepted_h_request_ids"] == {"1": "PCS", "4": "LDA", "10": "Hands Off LTA", "11": "LTA/LCA", "19": "PDA"})
check("FRC/ABS named target producer monitor negative", req["abs_named_target_monitor_matches"] == [] and req["frc_named_target_steering_monitor_matches"] == [])
check("request dictionary remains observer-side", "observer DID 0x1CEE/0x1CEF" in req["dictionary_location"])

time = axes["timing_deadline_constants"]
check("receiver timeout remains seven scheduler ticks", time["receiver_primary_cutout_foreground_ticks"] == 7)
check("wall-clock sender cadence still open", time["wall_clock_timeout_identified"] is False and time["sender_wall_clock_cadence_identified"] is False)
check("flashing timing not transferred", "CUW flashing P4/retry timing is unrelated" in time["boundary"])

angle = axes["steering_angle_constants"]
check("H B6 controller-equivalent scale exact", abs(angle["h_b6_controller_equivalent_rad_per_count"] - 0.0010001215187701138) < 1e-15)
check("Brake 0x107E observer scale exact", angle["brake_ads_control_eps_pinion_angle2"] == {"did": "0x107E", "scale_rad_per_count": 0.00025, "signed_bits": 24, "role": "observer"})
check("observer/B6 scale ratio pinned but unjoined", abs(angle["b6_to_brake_observer_scale_ratio"] - 4.000486075080455) < 1e-12 and "not joined by a producer dataflow" in angle["boundary"])
for key, unit in (("ads_ddr_target_angle_order", "rad"), ("ads_ddr_target_angle_speed_order", "rad/s")):
    row = angle[key]
    conv = row["numeric_conversion"]
    check(f"{key} signed unity Techstream conversion", conv["mul"] == 1000 and conv["div"] == 1 and conv["offset"] == 0 and conv["signed"] is True and conv["decimal_point_count"] == 3 and row["unit"] == unit)
    check(f"{key} remains snapshot evidence", row["role"] == "Operation-FFD/DDR recorded snapshot")

recipe = art["sender_recipe_boundary"]
check("EPS verifier recipe itself known", recipe["eps_verifier_envelope_known"] is True and recipe["authenticated_input_bytes"] == 36 and recipe["freshness_id"] == 2 and recipe["normal_freshness_slot"] == 1 and recipe["icus_slot_selector"] == 4)
check("sender implementation/freshness/key still open", recipe["sender_freshness_state_owner_identified"] is False and recipe["sender_mac_implementation_identified"] is False and recipe["slot4_secret_value_identified"] is False)

c = art["static_conclusion"]
check("architectural sender family advanced", c["architectural_immediate_sender_domain_identified"] is True and c["authenticated_brake_source_family_supported"] is True)
check("no false code-level ownership claim", c["unique_upstream_originator_identified"] is False and c["byte_level_frc_to_brake_transform_identified"] is False and c["b6_secoc_signing_implementation_owner_identified"] is False and c["b6_sender_freshness_owner_identified"] is False)
check("current-corpus static search exhausted", c["producer_side_runtime_code_available_in_current_corpus"] is False and c["current_corpus_static_search_exhausted"] is True)
check("next target is matched 07B0 + 0792 or synchronized stock LTA", "07B0" in c["next_evidence"] and "0792" in c["next_evidence"] and "synchronized stock-LTA" in c["next_evidence"])

print(f"\nRESULT: {passed} passed, {failed} failed")
raise SystemExit(1 if failed else 0)
