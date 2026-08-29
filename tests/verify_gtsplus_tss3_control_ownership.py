#!/usr/bin/env python3
"""Verify current-GTS+ TSS3 recorder hosting and longitudinal ownership surface."""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "tools/techstream"))

from extract_gtsplus_tss3_control_ownership import build

ART = REPO / "data/generated/gtsplus_2026/tss3_control_ownership_surface.json"


def check(label: str, condition: bool) -> None:
    if not condition:
        raise AssertionError(label)
    print(f"[OK] {label}")


def did_rows(section: dict, did: str) -> list[dict]:
    return section["dids"][did]


def main() -> int:
    stored = json.loads(ART.read_text(encoding="utf-8"))
    current = build()
    check("artifact regenerates from pinned current GTS+", stored == current)
    check("schema", stored["schema"] == "gtsplus-tss3-control-ownership-surface-v2")

    host = stored["recorder_hosting"]
    check(
        "TSS3 recorder plugins are exclusively category-498 FRC bindings",
        host["host"]["category_id"] == 498
        and host["host"]["database"] == "FRC_P5.ddb"
        and host["host"]["name"] == "Front Recognition Camera 2"
        and host["host"]["bindings"] == [
            {"dll": "GetTSS3ImageFFDP5_DT.dll", "role": 233, "role_hex": "0xE9"},
            {"dll": "GetTSS3OperationFFDP5_DT.dll", "role": 234, "role_hex": "0xEA"},
        ],
    )
    check(
        "FRC TSS3 recorder diagnostic endpoint is 0x792 in every pinned region",
        host["diagnostic_request_address_by_region"] == {"NA": "792", "EU": "792", "JP": "792"},
    )

    lateral = stored["lateral_ownership_boundary"]
    check(
        "EPS receives/verifies B6 from the positively attributed Brake source domain",
        lateral["eps_receiver"]["can_id"] == "0x0B6"
        and lateral["eps_receiver"]["monitored_source_domain"] == "Brake System Control Module"
        and lateral["brake_domain"]["category"]["category_id"] == 435
        and lateral["eps_is_not_producer_evidence"]["verifier_envelope_known"] is True,
    )
    check(
        "unique lateral originator/signer/freshness ownership remains unassigned after static exhaustion",
        lateral["unique_originator_identified"] is False
        and lateral["signing_owner_identified"] is False
        and lateral["freshness_owner_identified"] is False
        and lateral["frc_to_brake_transform_identified"] is False
        and lateral["static_search_exhausted"] is True,
    )

    longi = stored["longitudinal_request_surface"]
    frc = longi["frc_output_vocabulary"]
    check("FRC request vocabulary is region invariant", frc["identical_across_regions"])
    check(
        "FRC upper-limit requester ID",
        did_rows(frc, "0x1B03")[0]["name"] == "ISA Requesting Vertical ID (Upper Limit)"
        and did_rows(frc, "0x1B03")[0]["bit_width"] == 8,
    )
    check(
        "FRC upper-limit acceleration is a signed 32-bit 0.001 m/s2 display",
        any(
            row["name"] == "ISA Request Acceleration (Upper Limit)"
            and row["bit_width"] == 32
            and row["signed"] is True
            and row["decimal_point_count"] == 3
            and row["unit"] == "m/s2"
            for row in did_rows(frc, "0x1B04")
        ),
    )
    check(
        "FRC allocation and brake/stop permission controls retained",
        any("Allocation Method Specification" in row["name"] for row in did_rows(frc, "0x1B06"))
        and any("Stop Control Permission" in row["name"] for row in did_rows(frc, "0x1B07")),
    )

    brake = longi["brake_receive_vocabulary"]
    check("ABS TSS request receive vocabulary is region invariant", brake["abs_identical_across_regions"])
    expected_brake = {
        "0x10A1": ("Request Acceleration of Upper Limit from Toyota Safety Sense", 16, True, 3),
        "0x10A2": ("Request Acceleration of Lower Limit from Toyota Safety Sense", 16, True, 3),
        "0x10A3": ("Request Acceleration and Deceleration ID of Upper Limit from Toyota Safety Sense", 6, False, 0),
        "0x10A4": ("Request Acceleration and Deceleration ID of Lower Limit from Toyota Safety Sense", 6, False, 0),
    }
    for did, (name, width, signed, point) in expected_brake.items():
        row = did_rows(brake, did)[0]
        check(
            f"brake TSS receive {did}",
            (row["name"], row["bit_width"], row["signed"], row["decimal_point_count"])
            == (name, width, signed, point),
        )
    check(
        "TSS receive DIDs exist in P5 skid/booster/EPB and P6 BSCM_A",
        set(brake["consumers"]) == {"435", "466", "485", "6004"},
    )

    recorder = longi["pcs_recorder_vocabulary"]
    check(
        "recorder contains lower and upper TSS longitudinal requests",
        recorder["5280"][0]["name"] == "TSS required longitudinal ID (lower limit)"
        and recorder["5281"][0]["name"] == "TSS request longitudinal ID (upper limit)",
    )
    check(
        "recorder contains longitudinal arbitration result ID and acceleration",
        recorder["5284"][0]["name"] == "Arbitration result_longitudinal ID"
        and recorder["57DB"][0]["name"] == "Arbitration result Acceleration"
        and recorder["57D3"][0]["name"] == "Arbitration result_Acceleration valid flag",
    )

    fleet = stored["fleet_brake_sink_census"]["regions"]
    check(
        "FRC fleet rows reproduce TMS-079 breadth",
        [fleet[r]["frc_install_row_count"] for r in ("NA", "EU", "JP")] == [256, 460, 213],
    )
    check(
        "all EU/JP and all production-looking NA FRC rows have a TSS-request-observable brake sink",
        [fleet[r]["rows_with_tss_request_observable_brake_sink"] for r in ("NA", "EU", "JP")] == [255, 460, 213]
        and len(fleet["NA"]["rows_without_sink"]) == 1
        and fleet["NA"]["rows_without_sink"][0]["vehicle_name"] == "TEST",
    )

    rob = stored["brake_rob_boundary"]
    check(
        "ordinary FRC/Brake RoB tables add no request/arbitration winner field",
        all(
            not rob["databases"][db]["request_or_arbitration_name_hits"]
            for db in ("FRC_P5.ddb", "ABS_P5.ddb", "Brk_Bst_P5.ddb")
        ),
    )
    check(
        "brake RoB retains only the named ADS pinion observer",
        rob["databases"]["ABS_P5.ddb"]["pinion_name_hits"]
        == [{"data_id": "0x507E", "record_name": "ADS Control EPS Pinion Angle2", "tables": [90, 151]}],
    )

    arbitration = stored["ordinary_arbitration_census"]
    check("no ordinary generation-20 control arbitration monitor exists", arbitration["generation20_hit_count"] == 0)
    check(
        "successor arbitration vocabulary is confined to ADCU_P6/P6F",
        {row["database"] for row in arbitration["control_related_hits"]} == {"ADCU_P6.ddb", "ADCU_P6F.ddb"}
        and {row["name"] for row in arbitration["control_related_hits"]} == {
            "Longitudinal Powertrain Arbitration ID",
            "Longitudinal Brake Arbitration ID",
            "Lateral Arbitration ID",
        },
    )

    camry = stored["exact_camry_blocker"]
    check(
        "exact Camry Brake identity and local producer-firmware absence are pinned",
        camry["identity"]["request"] == "0x7B0"
        and camry["identity"]["f181"] == "F152633K0000"
        and camry["identity"]["ecu_part_0105"] == "8954147040"
        and camry["producer_firmware"]["locally_available"] is False
        and camry["producer_firmware"]["diag_07b0_matches"] == [],
    )
    check(
        "Camry 0x107E is already disproved while 0x10A1..0x10A4 remain unmeasured live",
        camry["already_tested_observers"]["did_107e_default"]["status"] == "negative_or_timeout"
        and camry["already_tested_observers"]["did_107e_extended"]["status"] == "negative_or_timeout"
        and camry["new_longitudinal_observers_10a1_10a4_live_support"] == "not_measured",
    )

    srp = stored["current_utility_srp_census"]
    check(
        "current GTS+ UtilityNeo CONF scripts decode under the pinned V18 AES-256-ECB key",
        srp["srp_file_count"] == 18
        and srp["func_ids"] == [
            "ALM-01", "CSP-03", "CSP-05", "DCM-13", "DCM-33", "DSC-03", "ECD-43",
            "ECD-45", "ECD-46", "EFI-39", "FHV-03", "LAMP-02", "LAMP-03", "MG-01",
            "MM-37", "RCM-01", "SAS-01", "TVD-01",
        ],
    )
    check(
        "current utility frames carry no SecurityAccess/reflash service and no control/auth vocabulary",
        srp["forbidden_service_bytes_present"] == []
        and srp["control_security_vocabulary_hits"] == [],
    )

    graph = stored["labeled_observer_dtc_graph"]["databases"]
    check(
        "FRC carries no 'Toyota Safety Sense'-named ordinary monitor",
        graph["FRC_P5"]["safety_sense_named_monitors"] == [],
    )
    check(
        "brake domain carries no camera/recognition/radar-named monitor or DTC",
        all(
            graph[db]["camera_named_monitors"] == []
            and graph[db]["camera_radar_tss_named_dtcs"] == []
            for db in ("ABS_P5", "Brk_Bst_P5", "EPB_P5")
        ),
    )
    check(
        "brake request_or_arbitration_output monitors are exactly the four TSS request DIDs",
        all(
            len(graph[db]["request_or_arbitration_output_named_monitors"]) == 4
            for db in ("ABS_P5", "Brk_Bst_P5", "EPB_P5")
        ),
    )
    check(
        "the brake side's only ADAS-adjacent communication partner is the ADS Interface Module",
        stored["labeled_observer_dtc_graph"]["ads_interface_partner_on_brake"] is True
        and "Front Recognition Camera" not in " ".join(graph["ABS_P5"]["lost_communication_partners"]),
    )
    check(
        "EPS retains the Image Processing Module A/B communication naming",
        any("Image Processing Module" in name for name in graph["EMPS_P5"]["camera_radar_tss_named_dtcs"]),
    )

    specimens = stored["specimen_census"]
    check(
        "no bundled or tracked TSE/GTSE specimen exists",
        specimens["bundled_toyota_diagnostics_tse_gtse_count"] == 0
        and specimens["repository_reference_tse_gtse_count"] == 0,
    )
    check(
        "remaining boundary keeps wire/SecOC/arbitration ownership open",
        all(token in stored["remaining_boundary"] for token in ("vehicle-network command frame", "SecOC", "arbitration")),
    )

    print("GTS+ TSS3 control-ownership surface verification passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
