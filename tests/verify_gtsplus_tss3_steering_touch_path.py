#!/usr/bin/env python3
"""Verify the current-GTS+ TSS3 steering-touch / hands-on sensing path."""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "tools/techstream"))

from extract_gtsplus_tss3_steering_touch_path import build

ART = REPO / "data/generated/gtsplus_2026/tss3_steering_touch_path.json"


def check(label: str, condition: bool) -> None:
    if not condition:
        raise AssertionError(label)
    print(f"[OK] {label}")


def main() -> int:
    stored = json.loads(ART.read_text(encoding="utf-8"))
    current = build()
    check("artifact regenerates from pinned current GTS+ and tracked firmware", stored == current)
    check("schema", stored["schema"] == "gtsplus-tss3-steering-touch-path-v1")

    operation = stored["tss3_operation_surface"]
    check(
        "TSS3 Operation-FFD exposes touch sensor presence as DataID 5222",
        operation["touch_sensor_presence"] == {
            "data_id": "5222",
            "name": "Touch sensor presence",
            "byte_position": 1,
            "bit_position": 7,
            "bit_length": 8,
            "data_size": 1,
            "support_did": 0,
        },
    )
    check(
        "TSS3 recorder namespace independently uses 5501/5505 for LDA state",
        {row["data_id"] for row in operation["recorder_local_id_collision_examples"]}
        == {"5501", "5505"},
    )

    diag = stored["diagnostic_semantics"]
    check(
        "FRC diagnoses steering touch sensor failure",
        diag["frc_p5"]["touch_sensor_dtc"]
        == {"code": "C1A7796", "description": "Steering Touch Sensor", "failure": "Component Internal Failure"},
    )
    behavior = {row["signature"]: row["name"] for row in diag["frc_p5"]["wheel_meter_cxpi_behaviors"]}
    check(
        "FRC exposes steering-switch/meter and CXPI communication behaviors",
        behavior == {
            "X20B9": "Communication Error from Steering Switch Control Module to Instrument Panel Cluster Control Module",
            "X20BF": "CXPI Communication Error (Ais)",
            "X2501": "CXPI Communication Error (CMB)",
        },
    )

    p5 = diag["p5_predecessor_oracles"]
    check(
        "P5 LDA keeps torque and touch not-holding judgments separate",
        p5["lda_torque_judgment"]["primary_did"] == "0x1044"
        and p5["lda_touch_judgment"]["primary_did"] == "0x1045"
        and p5["fr_camera_grip_presence"]["patterns"] == {"0": "Absence", "1": "Presence"},
    )
    p6 = diag["p6_successor_oracles"]["steering_wheel_hold_detection"]
    check(
        "P6 explicitly models release/touch/torque/touch+torque hold detection",
        p6["patterns"] == {
            "0": "Release Detection",
            "1": "Hold Detection (Steering Touch Sensor)",
            "2": "Hold Detection (Torque Sensor)",
            "3": "Hold Detection (Steering Touch Sensor and Torque Sensor)",
        },
    )

    zone_grip = diag["p6_successor_oracles"]["zone_ecu_left_right_grip"]
    check(
        "P6 zone ECU exposes independent left/right steering grip operation bits",
        [(row["name"], row["bit_start"], row["patterns"]) for row in zone_grip] == [
            ("Steering Switch (Left Steering Grip Operation Information)", 56, {"0": "OFF", "1": "ON"}),
            ("Steering Switch (Right Steering Grip Operation Information)", 57, {"0": "OFF", "1": "ON"}),
        ],
    )

    ddr = stored["airbag_ddr_grip_surface"]
    check("A_B_CAN_P5 grip surface is table 147 / 0x30-byte rows", ddr["table"] == 147 and ddr["record_size"] == 0x30)
    check(
        "SRS DDR has left/right grip values and validity as local keys 5500..5505",
        [(row["primary_key"], row["name"]) for row in ddr["rows"]] == [
            (5500, "Grip Sensor Value (Left)"),
            (5501, "Grip Sensor Value (Left)"),
            (5502, "Grip Sensor Value (Right)"),
            (5503, "Grip Sensor Value (Right)"),
            (5504, "Grip Sensor Value Invalid Flag"),
            (5505, "Grip Sensor Value Invalid Flag"),
        ],
    )
    check(
        "host field access proves +0x18 is the DDR monitor key, not a CAN ID",
        all(ddr["host_layout_proof"]["monitor_field_witnesses"].values()),
    )
    address = ddr["address_table"]
    check(
        "DDR address table has nine grip-key mappings across recorder selector contexts",
        [(row["record"], row["monitor_key"], row["field_6_u16"], row["selector_0"], row["selector_1"]) for row in address["rows"]] == [
            (2137, 5501, 0x24, 0x16, 0x02),
            (2138, 5502, 0x24, 0x16, 0x02),
            (2139, 5504, 0x24, 0x16, 0x02),
            (2699, 5500, 0x60, 0x19, 0x02),
            (2700, 5503, 0x60, 0x19, 0x02),
            (2701, 5505, 0x60, 0x19, 0x02),
            (3095, 5500, 0x60, 0x1B, 0x02),
            (3096, 5503, 0x60, 0x1B, 0x02),
            (3097, 5505, 0x60, 0x1B, 0x02),
        ],
    )
    check(
        "DDR address host lookup is selector+selector+local-key rather than CAN routing",
        all(ddr["host_layout_proof"]["address_field_witnesses"].values()),
    )
    check(
        "DDR invalid-condition table pairs left/right grip values with local validity keys",
        {row["monitor_key"]: row["invalid_key"] for row in address["invalid_condition_table"]["rows"]}
        == {5500: 5505, 5501: 5504, 5502: 5504, 5503: 5505, 5504: 5504, 5505: 5505},
    )

    cats = stored["standalone_wheel_category_boundary"]
    check(
        "no steering-pad/combination-switch/under-wheel diagnostic category co-occurs with FRC_P5 in any region",
        all(
            row["category_498_cooccurrence_count"] == 0
            for region in cats["regions"].values()
            for row in region["candidate_categories"]
        ),
    )

    topology = stored["representative_canbus_topology"]["vehicles"]
    expected = {
        (109, "Front Camera Module", "Bus 1"),
        (98, "Combination Meter", "Bus 3"),
        (50, "Power Steering (EPS)", "Bus 4"),
        (240, "Spiral cable (Steering Angle Sensor)", "Bus 4"),
    }
    check("representative TSS3 topology census includes Camry/Prius/Grand Highlander/RX", set(topology) == {"camry_hv", "prius", "grand_highlander", "rx350h"})
    check(
        "all representative TSS3 cars share camera/meter/EPS/SAS placement and no touch/grip CAN node",
        all(
            {(p["component_index"], p["ecu_domain"], p["bus_name"]) for p in vehicle["placements"]} == expected
            and vehicle["explicit_touch_or_grip_topology_nodes"] == []
            for vehicle in topology.values()
        ),
    )

    venza = stored["venza_srs_024_boundary"]["candidate_0x024"]
    check(
        "tracked Venza SRS independently joins SecOC profile/PDU/acceptance to physical CAN 0x024",
        venza["application_rx_pdu"] == 14
        and venza["secoc_data_id"] == "0x024"
        and venza["normal_rx_can_id"] == "0x024"
        and venza["hardware_acceptance_can_id"] == "0x024"
        and venza["physical_can_id_proved"] is True,
    )
    check("Venza 0x024 is not promoted to a grip carrier", venza["grip_semantic_join_proved"] is False)

    recovered = stored["recovered_path"]
    check(
        "remaining boundary is the post-meter CAN carrier/parser",
        "exact post-meter CAN arbitration ID" in recovered["still_open"]
        and "touch-equipped vehicle capture" in recovered["still_open"],
    )

    print("GTS+ TSS3 steering-touch path verification passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
