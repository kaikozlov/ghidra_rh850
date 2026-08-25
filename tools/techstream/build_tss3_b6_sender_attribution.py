#!/usr/bin/env python3
"""Build the bounded TSS3 Corolla B6 sender-attribution artifact.

This intentionally joins already-generated, independently verified evidence:
- exact-H receiver/Techstream attribution and B6 control dataflow,
- exact-H SecOC key/profile provenance,
- raw-Techstream-derived P5 module/diagnostic semantics, and
- the externally verified local FRC CUW corpus.

The goal is to answer what the current corpus can prove about the *sender side*
without pretending that opaque FRC repro images or a missing category-435 CUW
contain decoded producer code.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[2]
DEFAULT_OUT = REPO / "data/generated/techstream_v18/tss3_b6_sender_attribution.json"
P5 = REPO / "data/generated/techstream_v18/p5_lateral_control_semantics.json"
CUW = REPO / "data/generated/techstream_v18/cuw_frc_corpus.json"
H_CORR = REPO / "data/generated/corolla_8965H1202000_techstream_correlations.json"
H_KEY = REPO / "data/generated/corolla_8965H1202000_secoc_key_provenance.json"
H_B6 = REPO / "data/generated/corolla_8965H1202000_b6_secoc_verification.json"
H_PROV = REPO / "data/generated/corolla_8965H1202000_lta_command_provenance.json"
H_CODE = REPO / "community/albinoelephant/normalized/8965H1202000_CodeFlash.bin"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def build() -> dict[str, Any]:
    p5 = load(P5)
    cuw = load(CUW)
    corr = load(H_CORR)
    key = load(H_KEY)
    b6 = load(H_B6)
    prov = load(H_PROV)

    topology = p5["upstream_lateral_route"]["topology_conclusion"]
    brake_angle = p5["upstream_lateral_route"]["brake_family_angle_observer"]
    frc = p5["front_recognition_camera_2"]
    abs_na = p5["upstream_lateral_route"]["regions"]["NA"]
    target_id = p5["power_steering"]["target_lateral_id_semantics"]
    ads_rows = {
        row["record_index"]: row
        for row in p5["advanced_drive_control"]["ddr_behavior_data_rows"]["rows"]
    }
    sender_dtc = corr["protected_brake_profile_semantics"]["b6"]["techstream_source_dtc"]
    shared_key = key["shared_crypto_selection"]
    b6_scale = prov["b6_signed16_target_angle_ingress"]["scaling"]
    b6_static = prov["b6_signed16_target_angle_ingress"]["static_conclusion"]

    frc_packages = [
        {
            "filename": row["filename"],
            "diag_id": row["descriptor"]["diag_id"],
            "source_cid": row["descriptor"]["source_target_calibration_1"],
            "new_cid": row["descriptor"]["new_cid"],
            "repro_method": row["descriptor"]["repro_method"],
            "contact_type": row["descriptor"]["contact_type"],
            "decoded_image_length": row["whole_repro"]["decoded_image_length"],
            "decoded_image_entropy_bits_per_byte": row["whole_repro"]["decoded_image_entropy_bits"],
        }
        for row in cuw["packages"]
    ]
    diag_counts = cuw["reference_inventory"]["diag_id_counts"]
    if len(frc_packages) != 6 or {row["diag_id"] for row in frc_packages} != {"0792"}:
        raise ValueError("FRC corpus no longer consists of six 0792 packages")
    if diag_counts.get("07B0", 0) != 0:
        raise ValueError("local CUW corpus now contains a 07B0 package; rerun producer analysis")
    if not all(row["decoded_image_entropy_bits_per_byte"] > 7.99 for row in frc_packages):
        raise ValueError("FRC image representation no longer satisfies the pinned opacity boundary")

    if not (
        sender_dtc["techstream_code"] == "U012987"
        and sender_dtc["techstream_description"] == "Lost Communication with Brake System Control Module"
        and sender_dtc["techstream_failure"] == "Missing Message"
    ):
        raise ValueError("exact-H B6 immediate sender-domain DTC drift")
    if not (
        topology["frc_to_brake_dependency_identified"]
        and topology["brake_to_eps_dependency_identified"]
        and topology["frc_to_eps_dependency_also_identified"]
        and not topology["payload_forwarding_or_transform_identified"]
        and not topology["secoc_sender_ownership_identified"]
    ):
        raise ValueError("P5 topology boundary drift")
    if not (
        shared_key["secoc_crypto_config_id"] == 0
        and shared_key["icus_slot_selector"] == 4
        and [r["can_id"] for r in key["secoc_records"]] == ["0x00F", "0x0D7", "0x0B6"]
    ):
        raise ValueError("H protected-profile shared slot-4 selection drift")

    expected_requests = {"1": "PCS", "4": "LDA", "10": "Hands Off LTA", "11": "LTA/LCA", "19": "PDA"}
    if b6_static["signal254_profile_labels"] != expected_requests:
        raise ValueError("H B6 accepted Target Lateral ID profile labels drift")
    if abs_na["abs_target_lateral_name_negative"]["matches"]:
        raise ValueError("ABS_P5 now exposes a named target-lateral/steering monitor")
    if "no named Target Steering Angle" not in frc["target_steering_angle_negative_note"]:
        raise ValueError("FRC target-steering negative drift")

    for idx, unit in ((406, "rad/s"), (407, "rad")):
        row = ads_rows[idx]
        conv = row["numeric_conversion"]
        if not (
            conv["mul"] == 1000
            and conv["div"] == 1
            and conv["offset"] == 0
            and conv["signed"]
            and conv["decimal_point_count"] == 3
            and row["resolved_unit"] == unit
        ):
            raise ValueError(f"ADS DDR target-order conversion drift at row {idx}")

    if not (
        brake_angle["name"] == "ADS Control EPS Pinion Angle2"
        and brake_angle["primary_data_id"] == "0x107E"
        and brake_angle["display_scale_per_raw_count"] == 0.00025
        and brake_angle["unit"] == "rad"
    ):
        raise ValueError("Brake-family angle observer drift")

    b6_rad_per_count = b6_scale["controller_equivalent_mrad_per_b6_count"] / 1000.0
    angle_ratio = b6_rad_per_count / brake_angle["display_scale_per_raw_count"]

    return {
        "schema_version": 1,
        "title": "Toyota TSS3 Corolla protected-B6 sender attribution from current Techstream/CUW corpus",
        "sources": {
            str(path.relative_to(REPO)): {"sha256": sha256_file(path)}
            for path in (P5, CUW, H_CORR, H_KEY, H_B6, H_PROV, H_CODE)
        },
        "corpus_boundary": {
            "frc_diag_id": "0792",
            "frc_package_count": len(frc_packages),
            "frc_packages": frc_packages,
            "category_435_brake_diag_id": "07B0",
            "category_435_brake_package_count": diag_counts.get("07B0", 0),
            "all_reference_diag_id_counts": diag_counts,
            "frc_runtime_code_searchable": False,
            "brake_runtime_code_available": False,
            "why_frc_not_searchable": cuw["transform_boundary"]["xx_members"],
            "why_brake_not_searchable": "No current REFERENCE/cuw package has Node01/DiagID=07B0. This is a local-corpus absence only.",
            "consequence": "The requested 32-byte Tx-descriptor and SecOC-generation-call searches cannot be performed honestly against decoded producer code in the current corpus. Re-scanning the six 0792 stored images for literals would treat an unknown high-entropy representation as executable plaintext.",
        },
        "immediate_b6_sender_domain": {
            "identified": True,
            "domain": "Brake System Control Module",
            "eps_receive_can_id": "0x0B6",
            "eps_receive_pdu_id": 42,
            "techstream_dtc": sender_dtc,
            "supporting_brake_profile": {
                "can_id": "0x0D7",
                "relationship": "Exact H maps protected 0x0D7 and 0x0B6 to the same Brake System Control Module missing-message DTC; classic 0x0D5 is a third control.",
            },
            "corolla_p5_category": {
                "category_id": 435,
                "database": "ABS_P5.ddb",
                "display_name": "Brake/EPB",
                "diagnostic_request_address": "0x7B0",
                "functional_address": "0x7E5",
            },
            "boundary": "This identifies the immediate monitored source domain at the EPS endpoint. It does not distinguish originator from forwarder or prove which ECU executes CMAC/freshness generation.",
        },
        "authenticated_source_family": {
            "identified": True,
            "h_protected_profiles": [r["can_id"] for r in key["secoc_records"]],
            "shared_secoc_crypto_config_id": shared_key["secoc_crypto_config_id"],
            "shared_icus_slot_selector": shared_key["icus_slot_selector"],
            "slot4_key_value_cpu_visible": False,
            "interpretation": "H's sync 0x00F plus ordinary 0x0D7/0x0B6 all select the same protected ICU-S slot-4 key. D7 and B6 independently carry the Brake System Control Module loss label. This supports one authenticated brake-system source family rather than unrelated per-PDU key selection.",
            "boundary": "Shared key selection is not proof that the category-435 application owns the secret; the slot-4 value is hardware-protected and no producer application is decoded in the current corpus.",
        },
        "upstream_origin_search": {
            "frc_to_brake_dependency_identified": topology["frc_to_brake_dependency_identified"],
            "brake_to_eps_dependency_identified": topology["brake_to_eps_dependency_identified"],
            "frc_to_eps_dependency_also_identified": topology["frc_to_eps_dependency_also_identified"],
            "payload_forwarding_or_transform_identified": topology["payload_forwarding_or_transform_identified"],
            "secoc_signing_owner_identified": topology["secoc_sender_ownership_identified"],
            "strongest_static_model": topology["strongest_static_model"],
            "conclusion": "A brake-mediated FRC/ADS target route remains the strongest static architecture, but direct FRC->EPS dependency and ADS-interface references prevent assigning FRC as the unique originator or ABS as a pure forwarder.",
        },
        "requested_search_axes": {
            "fd32_transmit_descriptor": {
                "status": "blocked_by_corpus_representation",
                "result": "No decoded FRC or Brake producer application is available. The exact H receiver proves B6 is a 32-byte secured PDU; it cannot identify the sender Tx descriptor.",
            },
            "secoc_generation_calls": {
                "status": "blocked_by_corpus_representation",
                "result": "No producer-side CMAC/freshness generation call is recoverable from the current FRC CUWs, and no category-435 Brake image is present. H proves the verification envelope and shared slot selection only.",
            },
            "target_lateral_request_ids": {
                "status": "observer_dictionary_identified_producer_field_not_identified",
                "accepted_h_request_ids": expected_requests,
                "p5_oem_dictionary": target_id["value_dictionary"],
                "dictionary_location": "EMPS_P5/EMPS2_P5 Target Lateral ID observer DID 0x1CEE/0x1CEF",
                "abs_named_target_monitor_matches": abs_na["abs_target_lateral_name_negative"]["matches"],
                "frc_named_target_steering_monitor_matches": [],
                "boundary": "The numeric request vocabulary is exact, but no FRC/ABS P5 data-monitor row exposes the producer-side field carrying it.",
            },
            "timing_deadline_constants": {
                "status": "receiver_deadline_only",
                "receiver_primary_cutout_foreground_ticks": b6_static["receiver_loss_cutout_ticks"],
                "wall_clock_timeout_identified": b6_static["wall_clock_timeout_identified"],
                "sender_wall_clock_cadence_identified": False,
                "boundary": "The TAUJ0-CH3 foreground tick source is known but its period is not; CUW flashing P4/retry timing is unrelated to runtime B6 cadence and is not transferred.",
            },
            "steering_angle_constants": {
                "h_b6_controller_equivalent_rad_per_count": b6_rad_per_count,
                "h_b6_oem_wire_unit_name_identified": b6_scale["oem_wire_unit_name_closed"],
                "brake_ads_control_eps_pinion_angle2": {
                    "did": brake_angle["primary_data_id"],
                    "scale_rad_per_count": brake_angle["display_scale_per_raw_count"],
                    "signed_bits": 24,
                    "role": "observer",
                },
                "b6_to_brake_observer_scale_ratio": angle_ratio,
                "ads_ddr_target_angle_order": {
                    "record_index": 407,
                    "name": ads_rows[407]["name"],
                    "bit_range": ads_rows[407]["bit_range"],
                    "unit": ads_rows[407]["resolved_unit"],
                    "numeric_conversion": ads_rows[407]["numeric_conversion"],
                    "role": "Operation-FFD/DDR recorded snapshot",
                },
                "ads_ddr_target_angle_speed_order": {
                    "record_index": 406,
                    "name": ads_rows[406]["name"],
                    "bit_range": ads_rows[406]["bit_range"],
                    "unit": ads_rows[406]["resolved_unit"],
                    "numeric_conversion": ads_rows[406]["numeric_conversion"],
                    "role": "Operation-FFD/DDR recorded snapshot",
                },
                "boundary": "These three numeric domains are not joined by a producer dataflow. In particular, 0x107E is an actual/pinion observer and does not reveal B6 packing merely because its scale is approximately one quarter of the B6 controller-equivalent scale.",
            },
        },
        "sender_recipe_boundary": {
            "eps_verifier_envelope_known": True,
            "authenticated_input_bytes": b6["authenticated_envelope"]["authenticated_input_bytes"],
            "authenticated_input": b6["authenticated_envelope"]["cmac_input"],
            "freshness_id": b6["identifiers"]["freshness_id"],
            "normal_freshness_slot": b6["identifiers"]["normal_freshness_slot"],
            "icus_slot_selector": b6["identifiers"]["icus_slot_selector"],
            "sender_freshness_state_owner_identified": False,
            "sender_mac_implementation_identified": False,
            "slot4_secret_value_identified": False,
        },
        "static_conclusion": {
            "architectural_immediate_sender_domain_identified": True,
            "architectural_immediate_sender_domain": "Brake System Control Module / Corolla category-435 Brake/EPB family",
            "authenticated_brake_source_family_supported": True,
            "unique_upstream_originator_identified": False,
            "byte_level_frc_to_brake_transform_identified": False,
            "b6_secoc_signing_implementation_owner_identified": False,
            "b6_sender_freshness_owner_identified": False,
            "producer_side_runtime_code_available_in_current_corpus": False,
            "current_corpus_static_search_exhausted": True,
            "next_evidence": "Acquire the category-435 07B0 Brake/EPB CUW matched to the target vehicle and decode its application representation; pair it with the matched 0792 FRC image or a synchronized stock-LTA capture. Then search the decoded producer images for the 32-byte B6 Tx descriptor, request-ID state, angle conversion, cadence, freshness state and CMAC submission path.",
        },
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", type=Path, default=DEFAULT_OUT)
    args = ap.parse_args()
    obj = build()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n")
    print(f"Wrote {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
