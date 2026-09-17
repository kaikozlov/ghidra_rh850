#!/usr/bin/env python3
"""Recover the current Toyota TSS3 steering-touch / hands-on sensing path.

This extractor joins current GTS+ diagnostic vocabulary, PCS Data Viewer TSS3
Operation-FFD semantics, master install/topology tables, one current SRS DDR
schema, and the tracked Venza SRS firmware used elsewhere in this repository.

The goal is deliberately bounded: prove Toyota's touch/torque sensing model and
where the steering-touch subnode sits in the diagnostic/network architecture,
without inventing the still-unrecovered meter/gateway CAN signal that carries
raw grip state to TSS3 consumers.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import struct
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

import pefile

sys.path.insert(0, str(Path(__file__).resolve().parent))

from ddb_semantics import behavior_rows, dtc_rows, monitor_rows, records
from ddb_strings import load_string_db
from parse_ddb import DDBParser
from techstream_paths import gts_db_root, resolve_gts_root

REPO = Path(__file__).resolve().parents[2]
DEFAULT_OUT = REPO / "data/generated/gtsplus_2026/tss3_steering_touch_path.json"
PCS_SEMANTICS = REPO / "data/generated/gtsplus_2026/pcs_data_viewer_tss3_managed_semantics.json"
VENZA_SRS = REPO / "community/yc/venza/cflash.bin"
REGIONS = ("NA", "EU", "JP")
REPRESENTATIVE_VEHICLES = {
    "camry_hv": 12984,
    "prius": 12933,
    "grand_highlander": 12970,
    "rx350h": 12968,
}
RELEVANT_TOPOLOGY_COMPONENTS = {
    109: "Front Camera Module",
    98: "Combination Meter",
    50: "Power Steering (EPS)",
    240: "Spiral cable (Steering Angle Sensor)",
}
WHEEL_CATEGORY_NAME_RE = re.compile(
    r"steering pad|combination switch|switch module under the steering wheel|steering switch",
    re.IGNORECASE,
)


def u16(raw: bytes, off: int) -> int:
    return struct.unpack_from("<H", raw, off)[0]


def u32(raw: bytes, off: int) -> int:
    return struct.unpack_from("<I", raw, off)[0]


def sha256_bytes(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def compact_monitor(row: dict[str, Any]) -> dict[str, Any]:
    info = row.get("signal_info") or {}
    return {
        "name": row["name"],
        "primary_did": f"0x{int(row['primary_did']):04X}",
        "alternate_did": f"0x{int(row['alternate_did']):04X}" if row["alternate_did"] else None,
        "bit_start": int(row["bit_start"]),
        "bit_end": int(row["bit_end"]),
        "bit_width": int(row["bit_end"] - row["bit_start"] + 1),
        "patterns": {str(k): v for k, v in info.get("pattern_display", {}).items()},
        "unit": info.get("unit"),
    }


def db_semantics(parser: DDBParser, root: Path, database: str) -> tuple[list[dict], list[dict], list[dict]]:
    db_root = gts_db_root(root, "NA", "Gen")
    db = parser.parse_ecu_db(db_root / f"{database}.ddb")
    strings = load_string_db(parser, db_root / "M_English.ddb")
    monitors = monitor_rows(db, strings, f"{database}.ddb", include_signal_info=True)
    return monitors, dtc_rows(parser, db, strings, f"{database}.ddb"), behavior_rows(db, strings, f"{database}.ddb")


def selected_monitor(rows: list[dict], did: int, name: str) -> dict[str, Any]:
    matches = [row for row in rows if int(row["primary_did"]) == did and row["name"] == name]
    if len(matches) != 1:
        raise ValueError(f"expected one {name!r} row at 0x{did:04X}, found {len(matches)}")
    return compact_monitor(matches[0])


def tss3_operation_surface() -> dict[str, Any]:
    payload = json.loads(PCS_SEMANTICS.read_text(encoding="utf-8"))
    rows = payload["operation_ffd"]["detail_rows"]

    touch = [row for row in rows if row.get("DataID") == "5222" and row.get("DataName") == "Touch sensor presence"]
    if len(touch) != 1:
        raise ValueError(f"TSS3 Touch sensor presence row changed: {touch!r}")

    collision_ids = {"5501", "5505"}
    collisions = [
        {
            "data_id": row["DataID"],
            "name": row["DataName"],
            "byte_position": int(row["BytePosition"]),
            "bit_position": int(row["BitPosition"]),
            "bit_length": int(row["BitLength"]),
        }
        for row in rows
        if row.get("DataID") in collision_ids
    ]
    collisions.sort(key=lambda row: (row["data_id"], row["byte_position"], row["name"]))
    if not collisions:
        raise ValueError("expected TSS3 recorder-local 5501/5505 rows")

    row = touch[0]
    return {
        "touch_sensor_presence": {
            "data_id": row["DataID"],
            "name": row["DataName"],
            "byte_position": int(row["BytePosition"]),
            "bit_position": int(row["BitPosition"]),
            "bit_length": int(row["BitLength"]),
            "data_size": int(row["DataSize"]),
            "support_did": int(row["SupportDID"]),
        },
        "recorder_local_id_collision_examples": collisions,
        "namespace_boundary": (
            "TSS3 Operation-FFD DataIDs are recorder-local identifiers. Numeric equality with a DataID in another "
            "ECU/recorder schema does not imply a shared wire signal or shared semantic meaning."
        ),
    }


def diagnostic_semantics(parser: DDBParser, root: Path) -> dict[str, Any]:
    frc_mon, frc_dtcs, frc_beh = db_semantics(parser, root, "FRC_P5")
    lda_mon, _, _ = db_semantics(parser, root, "LDA_P5")
    camera_mon, _, _ = db_semantics(parser, root, "Fr_Camera_P5")
    p6_mon, p6_dtcs, _ = db_semantics(parser, root, "ADCU_P6")
    zone_mon, _, _ = db_semantics(parser, root, "Zone_ECU_A_P6")

    frc_touch_dtcs = [
        {"code": row["code"], "description": row["description"], "failure": row["failure"]}
        for row in frc_dtcs
        if row["description"] == "Steering Touch Sensor"
    ]
    if frc_touch_dtcs != [{"code": "C1A7796", "description": "Steering Touch Sensor", "failure": "Component Internal Failure"}]:
        raise ValueError(f"FRC touch DTC changed: {frc_touch_dtcs!r}")

    wanted_behaviors = {
        "X20B9": "Communication Error from Steering Switch Control Module to Instrument Panel Cluster Control Module",
        "X20BF": "CXPI Communication Error (Ais)",
        "X2501": "CXPI Communication Error (CMB)",
    }
    got_behaviors = {
        row["signature"]: row["name"]
        for row in frc_beh
        if row["signature"] in wanted_behaviors
    }
    if got_behaviors != wanted_behaviors:
        raise ValueError(f"FRC steering/CXPI behaviors changed: {got_behaviors!r}")

    p6_hold = selected_monitor(p6_mon, 0x1B10, "Steering Wheel Hold Detection")
    expected_hold = {
        "0": "Release Detection",
        "1": "Hold Detection (Steering Touch Sensor)",
        "2": "Hold Detection (Torque Sensor)",
        "3": "Hold Detection (Steering Touch Sensor and Torque Sensor)",
    }
    if p6_hold["patterns"] != expected_hold:
        raise ValueError(f"P6 steering hold enum changed: {p6_hold['patterns']!r}")

    zone_grip = [
        compact_monitor(row)
        for row in zone_mon
        if int(row["primary_did"]) == 0x1C01 and "Steering Grip Operation Information" in row["name"]
    ]
    zone_grip.sort(key=lambda row: row["name"])

    return {
        "frc_p5": {
            "touch_sensor_dtc": frc_touch_dtcs[0],
            "wheel_meter_cxpi_behaviors": [
                {"signature": sig, "name": wanted_behaviors[sig]}
                for sig in sorted(wanted_behaviors)
            ],
        },
        "p5_predecessor_oracles": {
            "fr_camera_grip_presence": selected_monitor(camera_mon, 0x1023, "Grip Detection Sensor Information"),
            "lda_torque_judgment": selected_monitor(
                lda_mon, 0x1044, "Not Holding Steering Wheel Judgment Status (Torque Sensor)"
            ),
            "lda_touch_judgment": selected_monitor(
                lda_mon, 0x1045, "Not Holding Steering Wheel Judgment Status (Touch Sensor)"
            ),
        },
        "p6_successor_oracles": {
            "steering_wheel_hold_detection": p6_hold,
            "steering_touch_sensor_dtc": [
                {"code": row["code"], "description": row["description"], "failure": row["failure"]}
                for row in p6_dtcs
                if row["description"] == "Steering Touch Sensor"
            ],
            "zone_ecu_left_right_grip": zone_grip,
        },
        "transfer_boundary": (
            "P5 predecessor and P6 successor rows prove Toyota treats torque and steering-touch as distinct, "
            "combinable hands-on inputs. They are semantic oracles only; their DIDs/bit positions are not "
            "transferred onto FRC_P5 vehicle-network frames."
        ),
    }


def airbag_ddr_grip_surface(parser: DDBParser, root: Path) -> dict[str, Any]:
    db_root = gts_db_root(root, "NA", "Gen")
    db = parser.parse_ecu_db(db_root / "A_B_CAN_P5.ddb")
    strings = load_string_db(parser, db_root / "M_English.ddb")
    section = db.sections[147]
    if section.decoded_record_size != 0x30:
        raise ValueError(f"unexpected CDbDDRMonitorTable record size {section.decoded_record_size}")

    matched = []
    for index, raw in enumerate(records(section)):
        name = strings.get_string(u32(raw, 0x14)) or ""
        if not name.startswith("Grip Sensor"):
            continue
        matched.append({
            "record": index,
            "name": name,
            "primary_key": u16(raw, 0x18),
            "primary_key_hex": f"0x{u16(raw, 0x18):04X}",
            "exception_handler_id": u16(raw, 0x28),
            "exception_handler_flag": raw[0x2D],
        })
    matched.sort(key=lambda row: row["primary_key"])

    expected = [
        (5500, "Grip Sensor Value (Left)"),
        (5501, "Grip Sensor Value (Left)"),
        (5502, "Grip Sensor Value (Right)"),
        (5503, "Grip Sensor Value (Right)"),
        (5504, "Grip Sensor Value Invalid Flag"),
        (5505, "Grip Sensor Value Invalid Flag"),
    ]
    if [(row["primary_key"], row["name"]) for row in matched] != expected:
        raise ValueError(f"A_B_CAN_P5 grip DDR rows changed: {matched!r}")

    address_section = db.sections[149]
    if address_section.decoded_record_size != 0x10:
        raise ValueError(f"unexpected CDbDDRAddressTable record size {address_section.decoded_record_size}")
    grip_keys = {key for key, _ in expected}
    address_rows = []
    for index, raw in enumerate(records(address_section)):
        monitor_key = u16(raw, 0x04)
        if monitor_key not in grip_keys:
            continue
        address_rows.append({
            "record": index,
            "monitor_key": monitor_key,
            "field_0_u32": u32(raw, 0x00),
            "field_6_u16": u16(raw, 0x06),
            "exception_handler_id": u16(raw, 0x08),
            "selector_0": raw[0x0A],
            "selector_1": raw[0x0B],
            "exception_handler_flag": raw[0x0C],
            "raw": raw.hex(),
        })
    address_rows.sort(key=lambda row: row["record"])
    expected_address = [
        (2137, 5501, 0x24, 0x16, 0x02),
        (2138, 5502, 0x24, 0x16, 0x02),
        (2139, 5504, 0x24, 0x16, 0x02),
        (2699, 5500, 0x60, 0x19, 0x02),
        (2700, 5503, 0x60, 0x19, 0x02),
        (2701, 5505, 0x60, 0x19, 0x02),
        (3095, 5500, 0x60, 0x1B, 0x02),
        (3096, 5503, 0x60, 0x1B, 0x02),
        (3097, 5505, 0x60, 0x1B, 0x02),
    ]
    observed_address = [
        (row["record"], row["monitor_key"], row["field_6_u16"], row["selector_0"], row["selector_1"])
        for row in address_rows
    ]
    if observed_address != expected_address:
        raise ValueError(f"A_B_CAN_P5 grip DDR address rows changed: {observed_address!r}")

    invalid_section = db.sections[150]
    if invalid_section.decoded_record_size != 0x10:
        raise ValueError(f"unexpected CDbDDRInvalidConditionTable record size {invalid_section.decoded_record_size}")
    invalid_rows = []
    for index, raw in enumerate(records(invalid_section)):
        monitor_key = u16(raw, 0x04)
        if monitor_key not in grip_keys:
            continue
        invalid_rows.append({
            "record": index,
            "monitor_key": monitor_key,
            "invalid_key": u16(raw, 0x06),
            "raw": raw.hex(),
        })
    invalid_rows.sort(key=lambda row: row["monitor_key"])
    expected_invalid = {5500: 5505, 5501: 5504, 5502: 5504, 5503: 5505, 5504: 5504, 5505: 5505}
    if {row["monitor_key"]: row["invalid_key"] for row in invalid_rows} != expected_invalid:
        raise ValueError(f"A_B_CAN_P5 grip invalid-condition map changed: {invalid_rows!r}")

    pe_path = root / "Bin/KgpDataCtrl.dll"
    pe = pefile.PE(str(pe_path), fast_load=False)
    exports = {
        (sym.name or b"").decode(errors="replace"): int(sym.address)
        for sym in pe.DIRECTORY_ENTRY_EXPORT.symbols
    }
    monitor_exports = {
        "find": "?FindDbItem1@CDbDDRMonitorTable@@MAEKKPAXKPAPAXPAK@Z",
        "compare": "?ComparativeKey@CDbDDRMonitorTable@@MAEFPAXPAPAXKK@Z",
        "exception_id": "?GetExceptahandId@CDbDDRMonitorTable@@MAEGPAXK@Z",
        "exception_flag": "?GetExceptahandFlag@CDbDDRMonitorTable@@MAEEPAXK@Z",
    }
    monitor_rvas = {name: exports[export] for name, export in monitor_exports.items()}
    if monitor_rvas != {"find": 0xA4130, "compare": 0xA42F0, "exception_id": 0xA42B0, "exception_flag": 0xA4270}:
        raise ValueError(f"CDbDDRMonitorTable host RVAs changed: {monitor_rvas!r}")

    address_exports = {
        "find_selector_0": "?FindDbItem1@CDbDDRAddressTable@@MAEKKPAXKPAPAXPAK@Z",
        "find_selector_1": "?FindDbItem2@CDbDDRAddressTable@@MAEKKPAXKPAPAXPAK@Z",
        "compare": "?ComparativeKey@CDbDDRAddressTable@@MAEFPAXPAPAXKK@Z",
        "exception_id": "?GetExceptahandId@CDbDDRAddressTable@@MAEGPAXK@Z",
        "exception_flag": "?GetExceptahandFlag@CDbDDRAddressTable@@MAEEPAXK@Z",
    }
    address_rvas = {name: exports[export] for name, export in address_exports.items()}
    if address_rvas != {
        "find_selector_0": 0x9ED00,
        "find_selector_1": 0x9EE00,
        "compare": 0x9EFC0,
        "exception_id": 0x9EF80,
        "exception_flag": 0x9EF40,
    }:
        raise ValueError(f"CDbDDRAddressTable host RVAs changed: {address_rvas!r}")

    def body(rva: int, size: int) -> bytes:
        off = pe.get_offset_from_rva(rva)
        return pe.__data__[off:off + size]

    # Machine-code witnesses, avoiding a disassembler dependency.
    monitor_find_body = body(monitor_rvas["find"], 0x100)
    monitor_compare_body = body(monitor_rvas["compare"], 0xC0)
    monitor_exception_id_body = body(monitor_rvas["exception_id"], 0x40)
    monitor_exception_flag_body = body(monitor_rvas["exception_flag"], 0x40)
    monitor_witnesses = {
        "primary_key_plus_0x18_in_find": bytes.fromhex("0fb74218") in monitor_find_body,
        "primary_key_plus_0x18_in_compare": bytes.fromhex("0fb74218") in monitor_compare_body and bytes.fromhex("0fb75118") in monitor_compare_body,
        "exception_id_plus_0x28": bytes.fromhex("668b440a28") in monitor_exception_id_body,
        "exception_flag_plus_0x2d": bytes.fromhex("8a440a2d") in monitor_exception_flag_body,
    }
    if not all(monitor_witnesses.values()):
        raise ValueError(f"CDbDDRMonitorTable host field witnesses changed: {monitor_witnesses!r}")

    address_find0_body = body(address_rvas["find_selector_0"], 0x100)
    address_find1_body = body(address_rvas["find_selector_1"], 0x100)
    address_compare_body = body(address_rvas["compare"], 0x150)
    address_exception_id_body = body(address_rvas["exception_id"], 0x40)
    address_exception_flag_body = body(address_rvas["exception_flag"], 0x40)
    address_witnesses = {
        "selector_0_plus_0x0a": bytes.fromhex("0fb6420a") in address_find0_body,
        "selector_1_plus_0x0b": bytes.fromhex("0fb6420b") in address_find1_body,
        "compare_selector_0_plus_0x0a": bytes.fromhex("0fb6420a") in address_compare_body and bytes.fromhex("0fb6510a") in address_compare_body,
        "compare_selector_1_plus_0x0b": bytes.fromhex("0fb6480b") in address_compare_body and bytes.fromhex("0fb6420b") in address_compare_body,
        "compare_monitor_key_plus_0x04": bytes.fromhex("0fb75104") in address_compare_body and bytes.fromhex("0fb74804") in address_compare_body,
        "exception_id_plus_0x08": bytes.fromhex("668b440a08") in address_exception_id_body,
        "exception_flag_plus_0x0c": bytes.fromhex("8a440a0c") in address_exception_flag_body,
    }
    if not all(address_witnesses.values()):
        raise ValueError(f"CDbDDRAddressTable host field witnesses changed: {address_witnesses!r}")

    return {
        "database": "A_B_CAN_P5.ddb",
        "table": 147,
        "record_size": section.decoded_record_size,
        "rows": matched,
        "address_table": {
            "table": 149,
            "record_size": address_section.decoded_record_size,
            "rows": address_rows,
            "invalid_condition_table": {
                "table": 150,
                "record_size": invalid_section.decoded_record_size,
                "rows": invalid_rows,
            },
            "conclusion": (
                "Grip monitor keys 5500..5505 are reused in multiple CDbDDRAddressTable selector contexts. "
                "The current host looks the table up by byte +0x0A, byte +0x0B, then local monitor key +0x04. "
                "The same grip key therefore maps to different recorder-layout rows across selectors; this table "
                "is DDR payload-address metadata, not a CAN arbitration-ID or vehicle-PDU routing table."
            ),
        },
        "host_layout_proof": {
            "kgp_data_ctrl": {
                "path": str(pe_path.relative_to(root)).replace("\\", "/"),
                "sha256": sha256_file(pe_path),
            },
            "monitor_export_rvas": {key: f"0x{value:08X}" for key, value in monitor_rvas.items()},
            "monitor_field_witnesses": monitor_witnesses,
            "address_export_rvas": {key: f"0x{value:08X}" for key, value in address_rvas.items()},
            "address_field_witnesses": address_witnesses,
            "conclusion": (
                "CDbDDRMonitorTable uses the u16 at +0x18 as its local monitor key. CDbDDRAddressTable is "
                "independently keyed by selector bytes +0x0A/+0x0B and local monitor key +0x04. Therefore "
                "5500..5505 and their address rows describe the SRS DDR recorder schema, not CAN IDs."
            ),
        },
    }

def steering_category_boundary(parser: DDBParser, root: Path) -> dict[str, Any]:
    per_region = {}
    all_candidate_ids: set[int] = set()
    for region in REGIONS:
        db_root = gts_db_root(root, region, "Gen")
        master = parser.parse_master_db(db_root / "Toyota.ddb")
        strings = load_string_db(parser, db_root / "M_English.ddb")
        categories = {
            row.category_id: {
                "category_id": row.category_id,
                "generation": row.generation,
                "database": row.database_name,
                "name": strings.get_string(row.ecu_name_string_index) or "",
            }
            for row in parser.extract_master_ecu_categories(master.sections[16])
        }
        candidates = {
            cid: row for cid, row in categories.items()
            if WHEEL_CATEGORY_NAME_RE.search(row["name"])
        }
        all_candidate_ids.update(candidates)

        vehicle_sets: dict[int, set[int]] = defaultdict(set)
        for raw in records(master.sections[5]):
            vehicle_sets[u16(raw, 0x04)].add(u16(raw, 0x06))
        set_categories: dict[int, set[int]] = defaultdict(set)
        for raw in records(master.sections[44]):
            set_categories[u16(raw, 0x04)].add(u16(raw, 0x06))

        frc_sets = [
            install_set
            for install_sets in vehicle_sets.values()
            for install_set in install_sets
            if 498 in set_categories.get(install_set, set())
        ]
        rows = []
        for cid in sorted(candidates):
            rows.append({
                **candidates[cid],
                "install_row_count": sum(cid in set_categories[sid] for sids in vehicle_sets.values() for sid in sids),
                "category_498_cooccurrence_count": sum(cid in set_categories[sid] for sid in frc_sets),
            })
        per_region[region] = {
            "frc_p5_install_row_count": len(frc_sets),
            "candidate_categories": rows,
        }

    cooccurrence = [
        (region, row)
        for region, payload in per_region.items()
        for row in payload["candidate_categories"]
        if row["category_498_cooccurrence_count"]
    ]
    if cooccurrence:
        raise ValueError(f"standalone steering switch/touch category now co-occurs with FRC_P5: {cooccurrence!r}")

    return {
        "candidate_category_ids": sorted(all_candidate_ids),
        "regions": per_region,
        "conclusion": (
            "Current NA/EU/JP install sets contain no steering-pad/combination-switch/under-wheel-switch diagnostic "
            "category alongside category 498 FRC_P5. The steering-touch wheel is therefore not represented as a "
            "standalone TSS3 GTS ECU category."
        ),
    }


def relevant_topology(parser: DDBParser, root: Path, vehicle_type: int) -> dict[str, Any]:
    db_root = gts_db_root(root, "NA", "Gen")
    master = parser.parse_master_db(db_root / "Toyota.ddb")
    strings = load_string_db(parser, db_root / "M_English.ddb")

    vehicle_names = {
        u32(raw, 0x04): strings.get_string(u32(raw, 0x00)) or ""
        for raw in records(master.sections[43])
    }
    car_rows = [raw for raw in records(master.sections[75]) if u32(raw, 0x04) == vehicle_type]
    if not car_rows:
        raise ValueError(f"missing CAN Bus Check row for vehicle type {vehicle_type}")
    option_rows = list(records(master.sections[77]))
    component_rows = list(records(master.sections[78]))
    subbus_names = {
        u32(raw, 0x00): strings.get_string(u32(raw, 0x04)) or ""
        for raw in records(master.sections[76])
    }
    bus_names = {
        u32(raw, 0x08): strings.get_string(u32(raw, 0x04)) or ""
        for raw in records(master.sections[79])
    }

    placements: set[tuple[int, str, int, str]] = set()
    all_domains: set[str] = set()
    for car_raw in car_rows:
        car_id = u32(car_raw, 0x00)
        for option in [raw for raw in option_rows if u32(raw, 0x00) == car_id]:
            group = u32(option, 44)
            for raw in component_rows:
                if u32(raw, 0x00) != group:
                    continue
                component_index = raw[14]
                domain = subbus_names.get(component_index + 1, "")
                all_domains.add(domain)
                if component_index in RELEVANT_TOPOLOGY_COMPONENTS:
                    bus_index = u16(raw, 0x08)
                    placements.add((component_index, domain, bus_index, bus_names.get(bus_index, "")))

    result = [
        {
            "component_index": component,
            "component_hex": f"0x{component:02X}",
            "ecu_domain": domain,
            "bus_index": bus_index,
            "bus_name": bus_name,
        }
        for component, domain, bus_index, bus_name in sorted(placements)
    ]
    expected = {
        (109, "Front Camera Module", 29, "Bus 1"),
        (98, "Combination Meter", 31, "Bus 3"),
        (50, "Power Steering (EPS)", 32, "Bus 4"),
        (240, "Spiral cable (Steering Angle Sensor)", 32, "Bus 4"),
    }
    if placements != expected:
        raise ValueError(f"vehicle type {vehicle_type} relevant topology changed: {placements!r}")
    touch_domains = sorted(domain for domain in all_domains if re.search(r"touch|grip", domain, re.IGNORECASE))
    if touch_domains:
        raise ValueError(f"vehicle type {vehicle_type} gained explicit touch/grip CAN topology nodes: {touch_domains!r}")
    return {
        "vehicle_type": vehicle_type,
        "vehicle_name": vehicle_names[vehicle_type],
        "placements": result,
        "explicit_touch_or_grip_topology_nodes": touch_domains,
    }


def representative_topology(parser: DDBParser, root: Path) -> dict[str, Any]:
    vehicles = {
        label: relevant_topology(parser, root, vehicle_type)
        for label, vehicle_type in REPRESENTATIVE_VEHICLES.items()
    }
    return {
        "region": "NA",
        "vehicles": vehicles,
        "shared_shape": (
            "Front Camera Module=Bus 1; Combination Meter=Bus 3; Power Steering and Spiral cable/SAS=Bus 4; "
            "no explicit touch/grip ECU appears in CAN Bus Check."
        ),
    }


def venza_srs_024_boundary() -> dict[str, Any]:
    cf = VENZA_SRS.read_bytes()
    profiles = [
        (0x1D6C8, 0),
        (0x1D718, 16),
        (0x1D768, 18),
        (0x1D7B8, 14),
    ]
    rows = []
    for off, expected_pdu in profiles:
        raw = cf[off:off + 0x50]
        app_pdu = u16(raw, 0x34)
        data_id = u16(raw, 0x0A)
        length = u32(raw, 0x24)
        normal_can_id = u32(cf, 0x1DA50 + app_pdu * 8) & 0x7FF
        acceptance_can_id = u32(cf, 0x20D8C + app_pdu * 16) & 0x7FF
        if app_pdu != expected_pdu or normal_can_id != data_id or acceptance_can_id != data_id:
            raise ValueError(
                f"Venza SRS SecOC/route join changed at {off:#x}: pdu={app_pdu} data={data_id:#x} "
                f"normal={normal_can_id:#x} acceptance={acceptance_can_id:#x}"
            )
        rows.append({
            "profile_offset": f"0x{off:05X}",
            "application_rx_pdu": app_pdu,
            "secoc_data_id": f"0x{data_id:03X}",
            "configured_length": length,
            "normal_rx_can_id": f"0x{normal_can_id:03X}",
            "hardware_acceptance_can_id": f"0x{acceptance_can_id:03X}",
        })

    target = next(row for row in rows if row["secoc_data_id"] == "0x024")
    return {
        "source": {
            "path": str(VENZA_SRS.relative_to(REPO)),
            "sha256": sha256_bytes(cf),
        },
        "profiles": rows,
        "candidate_0x024": {
            **target,
            "physical_can_id_proved": True,
            "grip_semantic_join_proved": False,
        },
        "boundary": (
            "The tracked 2021 Venza SRS firmware proves 0x024 is a real authenticated CAN-FD receive PDU: its "
            "SecOC row maps to application Rx PDU 14, and both the normal Rx descriptor and hardware acceptance "
            "table map PDU 14 to CAN 0x024. Nothing in this firmware statically identifies 0x024 as steering grip; "
            "it must not be promoted to a touch-sensor carrier without an independent semantic join."
        ),
    }


def build() -> dict[str, Any]:
    root = resolve_gts_root()
    parser = DDBParser()
    return {
        "schema": "gtsplus-tss3-steering-touch-path-v1",
        "title": "Toyota TSS3 steering-touch, torque hands-on, and wheel-subnode architecture",
        "tss3_operation_surface": tss3_operation_surface(),
        "diagnostic_semantics": diagnostic_semantics(parser, root),
        "airbag_ddr_grip_surface": airbag_ddr_grip_surface(parser, root),
        "standalone_wheel_category_boundary": steering_category_boundary(parser, root),
        "representative_canbus_topology": representative_topology(parser, root),
        "venza_srs_024_boundary": venza_srs_024_boundary(),
        "recovered_path": {
            "known": [
                "steering touch sensing is an explicit TSS3 configuration dimension (Operation-FFD 5222)",
                "Toyota models touch and torque as distinct and combinable hands-on inputs",
                "FRC_P5 diagnoses the Steering Touch Sensor and wheel/meter CXPI communication path",
                "current TSS3 CAN Bus Check exposes the Combination Meter as a CAN node but no standalone touch/grip ECU",
                "current SRS DDR consumes left/right grip values and receive-validity state as first-class recorder inputs",
            ],
            "bounded_network_model": "steering-wheel touch subnode -> meter-side subnetwork -> Combination Meter -> vehicle CAN/gateway -> FRC/SRS consumers",
            "still_open": (
                "The exact post-meter CAN arbitration ID, payload bits, gateway transform, and FRC parser for left/right "
                "grip remain unresolved. Closing them requires a touch-equipped vehicle capture or plaintext meter/FRC "
                "firmware; current encrypted FRC CUWs do not expose the application parser."
            ),
        },
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--output", type=Path, default=DEFAULT_OUT)
    args = ap.parse_args()
    payload = build()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"wrote {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
