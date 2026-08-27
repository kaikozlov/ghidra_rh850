#!/usr/bin/env python3
"""Join exact Techstream EMPS_P5 Data IDs to Sienna 8965B4512000 control state.

The generated artifact is intentionally capture-oriented: exact Sienna RDBI
callbacks, exact EMPS_P5 primary/alternate Data-ID vocabulary, byte-pinned
producer/control functions, emitted engineering-unit transforms, and explicit
interpretation boundaries for later GTS+/bench correlation.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "tools"))
from sienna_target import CODEFLASH as FW  # noqa: E402
H_JOIN = REPO / "data/generated/corolla_8965H1202000_techstream_correlations.json"
OUT = REPO / "data/generated/sienna_8965B4512000_techstream_did_semantics.json"

DIDS = {
    0x1151: {
        "callback": 0x4D71C, "size": 60, "observer_cell": "0xFEBE66E6",
        "source_chain": ["0xFEBE66E6", "0xFEBE6D1A"],
        "semantic": "Motor Actual Current (Q Axis)", "unit": "A", "monitor_key": 251,
        "role": "actual_q_current",
        "emitted_encoding": "signed16; raw observer * 100 / 0x80; clamp [-32768,32767]; 0.01 A/LSB",
        "control_role": "dual-motor sum-frame Q-axis actual-current observer",
    },
    0x1152: {
        "callback": 0x4D758, "size": 60, "observer_cell": "0xFEBE66FC",
        "source_chain": ["0xFEBE66FC", "0xFEBE6D2C", "0xFEBE6D7E", "0xFEBE6DB2", "0xFEBE6ACC", "0xFEBEE40C"],
        "semantic": "Command Value Current (Q Axis)", "unit": "A", "monitor_key": 252,
        "role": "command_q_current",
        "emitted_encoding": "signed16; raw observer * 100 / 0x80; clamp [-32768,32767]; 0.01 A/LSB",
        "control_role": "base Q-current command observer; compensated PI reference is FEBE6D24, not the DID-visible base cell",
        "capture_expectation": "normal path maps command magnitude monotonically and negates FEBEE40C before the Q-current reference path; compare sign against 0x1C02 rather than assuming equality",
    },
    0x1153: {
        "callback": 0x4D794, "size": 60, "observer_cell": "0xFEBE66E4",
        "source_chain": ["0xFEBE66E4", "0xFEBE6D18"],
        "semantic": "Motor Actual Current 2 (D Axis)", "unit": "A", "monitor_key": 253,
        "role": "actual_d_current",
        "emitted_encoding": "signed16; raw observer * 100 / 0x80; clamp [-32768,32767]; 0.01 A/LSB",
        "control_role": "dual-motor sum-frame D-axis actual-current observer; FEBE6D18 feeds the D-current PI error",
    },
    0x1154: {
        "callback": 0x4D7D0, "size": 60, "observer_cell": "0xFEBE66FE",
        "source_chain": ["0xFEBE66FE", "0xFEBE6D2E", "0xFEBE6D70"],
        "semantic": "Command Value Current 2 (D Axis)", "unit": "A", "monitor_key": 254,
        "role": "command_d_current",
        "emitted_encoding": "signed16; raw observer * 100 / 0x80; clamp [-32768,32767]; 0.01 A/LSB",
        "control_role": "base D-current command observer; compensated PI reference is FEBE6D28",
        "capture_expectation": "the recovered magnitude-indexed map becomes negative at high command magnitude, consistent with field-weakening behavior; exact calibration-table semantics remain bounded",
    },
    0x1155: {
        "callback": 0x4D80C, "size": 74, "observer_cell": "0xFEBE665C",
        "source_chain": ["0xFEBE665C", "0xFEBE7D14", "0xFEBE7D34"],
        "semantic": "Motor Rotation Angle", "unit": "deg", "monitor_key": 255,
        "role": "motor_rotation_angle",
        "emitted_encoding": "unsigned16; observer * 0x465 >> 11; clamp to 36000; 0.01 deg/LSB; 0xFFFF when Dem event 0x52 is set",
        "control_role": "resolver/motor-angle observer with explicit internal-Dem validity gate",
    },
    0x1156: {
        "callback": 0x4D856, "size": 58, "observer_cell": "0xFEBE6764",
        "source_chain": ["0xFEBE6764", "0xFEBEE608", "0xFEBEAF40"],
        "semantic": "Final Motor Current Limited (Q Axis)", "unit": "A", "monitor_key": 256,
        "role": "final_q_current_limit",
        "emitted_encoding": "unsigned/non-negative signed16 transport; observer * 100 / 0x80; clamp [0,32767]; 0.01 A/LSB",
        "control_role": "selected minimum current-limit magnitude used by the command clamp; individual limit-candidate meanings remain bounded",
        "companion_did": "0x1065",
    },
    0x1185: {
        "callback": 0x4D930, "size": 42, "observer_cell": "0xFEBE8070",
        "source_chain": ["0xFEBE8070", "SecOC CAN-FD 0x0D7 signal 0x11B/283"],
        "semantic": "CAN Vehicle Speed (SP1)", "unit": "km/h", "monitor_key": 305,
        "role": "vehicle_speed_sp1",
        "emitted_encoding": "unsigned16; clamp to 30000; 0.01 km/h/LSB; 300.00 km/h cap",
        "control_role": "protected 0x0D7 PDU speed observer; distinct from DID 0x0102 vehicle-speed acquisition",
    },
    0x1C02: {
        "callback": 0x4DB5E, "size": 72, "observer_cell": "0xFEBE674A",
        "source_chain": ["0xFEBE674A", "0xFEBEE40A", "0xFEBEAC56", "0xFEBEC1D2", "0xFEBEC1C0"],
        "semantic": "Command Value Torque", "unit": "Nm", "monitor_key": 402,
        "role": "internal_command_value_torque",
        "emitted_encoding": "signed16; (((observer * FEBEE8A6)/0x2000)*100)/0x100; clamp [-20000,20000]; 0.01 Nm/LSB",
        "control_role": "general internal command-value-torque observer upstream of the limited sibling that reaches the motor Q/D current-reference path; not intrinsically one external CAN command",
    },
}

COMPANION_DIDS = {
    0x1065: {
        "callback": 0x4D084,
        "size": 44,
        "semantic": "Q-current-limit-positive flag",
        "unit": "boolean",
        "source_chain": ["0xFEBE6764"],
        "emitted_encoding": "1 byte; bool(FEBE6764 > 0)",
        "boundary": "structural companion observer; no independent EMPS_P5 OEM name is assigned here",
    },
}

# Function extents come from the pinned Sienna Ghidra inventory.  Their bodies
# are hashed from raw CodeFlash so generated semantics cannot drift from bytes.
FUNCTIONS = {
    0x3572C: (156, "motor_command_sign_junction"),
    0x35960: (338, "dual_motor_clarke_park_feedback"),
    0x36902: (304, "dq_current_pi_axis_a"),
    0x36A44: (404, "dq_current_pi_axis_b"),
    0x36DDE: (36, "q_current_error_clamp"),
    0x36F9A: (96, "q_current_pi_frontend"),
    0x37644: (202, "dual_motor_dq_feedback_combine"),
    0x37712: (120, "dual_motor_dq_current_reference"),
    0x37B5A: (52, "d_current_base_select"),
    0x37B92: (322, "q_current_magnitude_map"),
    0x37CD4: (38, "q_current_sign_and_map"),
    0x37FA2: (16, "q_current_command_input_latch"),
    0x472A6: (38, "motor_rotation_wrap"),
    0x4B3AA: (194, "application_unpack_can_0d7_secoc_fd"),
    0x51708: (82, "dem_event_state_query"),
    0x5B662: (222, "rte_snapshot_copy"),
    0x5C0B6: (1204, "rte_input_staging_copy_b"),
    0x5C56A: (252, "rte_snapshot_copy_2"),
    0x5C666: (1442, "rte_input_staging_copy_a"),
    0x5D18C: (216, "tauj0_ch0_motor_control_worker"),
    0xB8E5C: (60, "q_limit_candidate_select_a"),
    0xB8E98: (52, "q_limit_candidate_select_b"),
    0xB8ED0: (128, "q_limit_publish"),
    0xBCA88: (66, "q_limit_rte_publish"),
    0xBCACE: (104, "command_torque_rte_publish"),
    0xCAC14: (86, "steering_command_secondary_select_stage"),
    0xCAC6A: (86, "steering_command_secondary_gain_clip"),
    0xCACC0: (168, "steering_command_secondary_limit_stage"),
    0xCAD68: (28, "steering_command_primary_limit_publish"),
    0xCAD84: (82, "steering_command_primary_select"),
    0xCADD6: (80, "steering_command_torque_scale_and_limit"),
    0xCAE26: (48, "steering_command_limited_sibling"),
    0xCAE56: (68, "steering_command_delayed_variant"),
    0xCB454: (72, "command_torque_state_publish"),
    0xFCC00: (78, "command_limit_table_state_publish"),
}


def digest(fw: bytes, address: int, size: int) -> str:
    return hashlib.sha256(fw[address:address + size]).hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", type=Path, default=OUT)
    args = ap.parse_args()

    fw = FW.read_bytes()
    h = json.loads(H_JOIN.read_text())
    monitor_rows = h["ddb_overlap"]["emps_p5"]["monitor_rows"]
    by_primary = {int(row["primary_data_id"], 16): row for row in monitor_rows}

    did_rows = []
    for did, row in DIDS.items():
        src = by_primary[did]
        entry = dict(row)
        entry.update({
            "did": f"0x{did:04X}",
            "callback": f"0x{row['callback']:08X}",
            "callback_sha256": digest(fw, row["callback"], row["size"]),
            "techstream_record_index": src["ddb_record_index"],
            "techstream_record_sha256": src["ddb_record_sha256"],
            "techstream_name": src["name"],
            "techstream_primary_data_id": src["primary_data_id"],
            "techstream_alternate_data_id": src["alternate_data_id"],
            "confidence": "exact DID vocabulary + target-native callback/dataflow",
        })
        did_rows.append(entry)

    companions = []
    for did, row in COMPANION_DIDS.items():
        entry = dict(row)
        entry.update({
            "did": f"0x{did:04X}",
            "callback": f"0x{row['callback']:08X}",
            "callback_sha256": digest(fw, row["callback"], row["size"]),
        })
        companions.append(entry)

    functions = [
        {
            "address": f"0x{address:08X}",
            "size": size,
            "role": role,
            "sha256": digest(fw, address, size),
        }
        for address, (size, role) in FUNCTIONS.items()
    ]

    obj = {
        "schema_version": 2,
        "software_id": "8965B4512000",
        "image_sha256": hashlib.sha256(fw).hexdigest(),
        "dids": did_rows,
        "companion_dids": companions,
        "supporting_functions": functions,
        "control_model": {
            "feedback": "dual_motor_dq_feedback_combine publishes D/Q sum-frame actual state; 0x1151/0x1153 observe the staged Q/D sums",
            "base_references": "dual_motor_dq_current_reference publishes base 0x1152/0x1154 sources while separate compensated cells FEBE6D24/FEBE6D28 feed the PI loops",
            "q_command_bridge": "limited sibling FEBEC1D4 is published through FEBEAC54/FEBEE40C; motor setup negates that value into FEBE6ACC -> FEBE6DB2 -> Q-current magnitude/sign mapping -> FEBE6D7E -> 0x1152",
            "torque_observer": "0x1C02 observes sibling command state FEBEC1D2 through FEBEAC56/FEBEE40A; it is upstream/general and does not identify one external command provenance",
            "q_limit": "0x1156 observes FEBEAF40 through FEBEE608/FEBE6764; FEBEAF40 is a selected current-limit magnitude and also constrains the command clamp",
            "speed": "0x1185 observes the 16-bit SP1 field decoded from protected CAN-FD 0x0D7 and is intentionally distinct from DID 0x0102's other vehicle-speed acquisition",
        },
        "motor_angle_validity": {
            "dem_event": "0x52",
            "event_record_address": "0x0003006C",
            "event_record_raw": fw[0x3006C:0x30074].hex(),
            "dtc_table_index": fw[0x3006E],
            "interpretation": "event is used as an internal motor-angle validity gate; its event record carries DTC-table index 0, while the event producer/physical fault meaning remains unresolved",
        },
        "observer_priority": ["0x1C02", "0x1152", "0x1151", "0x1156", "0x1065", "0x1154", "0x1153", "0x1185", "0x1155"],
        "capture_card": [
            {"did": "0x1C02", "request": "22 1C 02", "signed": True, "scale": "0.01 Nm/LSB", "purpose": "general internal command torque"},
            {"did": "0x1152", "request": "22 11 52", "signed": True, "scale": "0.01 A/LSB", "purpose": "base Q-current command; compare sign/magnitude with 1C02"},
            {"did": "0x1151", "request": "22 11 51", "signed": True, "scale": "0.01 A/LSB", "purpose": "Q-current actual/follower"},
            {"did": "0x1156", "request": "22 11 56", "signed": False, "scale": "0.01 A/LSB", "purpose": "selected Q-current limit"},
            {"did": "0x1065", "request": "22 10 65", "signed": False, "scale": "boolean", "purpose": "limit-positive companion"},
            {"did": "0x1154", "request": "22 11 54", "signed": True, "scale": "0.01 A/LSB", "purpose": "base D-current command / field-axis behavior"},
            {"did": "0x1153", "request": "22 11 53", "signed": True, "scale": "0.01 A/LSB", "purpose": "D-current actual"},
            {"did": "0x1185", "request": "22 11 85", "signed": False, "scale": "0.01 km/h/LSB", "purpose": "protected-0D7 SP1 speed; compare with 0x0102"},
            {"did": "0x1155", "request": "22 11 55", "signed": False, "scale": "0.01 deg/LSB; 0xFFFF invalid", "purpose": "motor-angle validity canary"},
        ],
        "xcp_read_only_candidates": [
            "0xFEBE6D18", "0xFEBE6D1A", "0xFEBE6D2C", "0xFEBE6D2E",
            "0xFEBE6D24", "0xFEBE6D28", "0xFEBE6D20", "0xFEBE665C",
            "0xFEBE7D14", "0xFEBE6764", "0xFEBEAF40", "0xFEBEB548",
            "0xFEBE8070", "0xFEBEE40A", "0xFEBEE40C", "0xFEBE674A",
            "0xFEBEE8A6", "0xFEBE719A", "0xFEBEC1B8", "0xFEBEC1D2",
            "0xFEBEC1D4", "0xFEBEC1D6", "0xFEBEC1D8",
        ],
        "bounded_residues": [
            "producer/meaning of internal Dem event 0x52 that invalidates 0x1155",
            "individual semantic ownership of the steering_command_secondary_select_stage contributors and exact external 0x2E4 -> general-command contribution",
            "direct sin/cos table labeling behind the cross-consistent D/Q Park-axis interpretation",
            "semantic meaning of every q-limit candidate feeding FEBEAF40",
            "DDB range-word representation details for 0x1155 beyond the firmware-emitted 36000 cap",
        ],
        "boundary": "Techstream names are carried by exact primary Data-ID identity plus Sienna target-native callback/dataflow. 0x1C02 is a general internal command-value-torque observer; the recovered downstream current-control bridge does not make it intrinsically a specific external steering-CAN field or LTA source.",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
