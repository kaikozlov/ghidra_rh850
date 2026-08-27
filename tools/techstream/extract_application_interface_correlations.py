#!/usr/bin/env python3
"""Generate bounded Techstream/DBC correlations for recovered EPS interfaces.

This artifact deliberately separates external vocabulary corroboration from
firmware proof.  It decodes only P5 fields whose offsets are independently
consumed by the pinned Techstream binaries and records accepted, ambiguous, and
rejected direct-name candidates explicitly.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path
import re
import struct
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from parse_ddb import DDBParser  # noqa: E402


REPO = Path(__file__).resolve().parents[2]
DEFAULT_ROOT = REPO / "software/Techstream/v18/unpacked/toyota/Toyota Diagnostics/Techstream"
DEFAULT_OUTPUT = REPO / "data/generated/techstream_v18/application_interface_correlations.json"
SIGNAL_INFO_DLL = DEFAULT_ROOT / "bin/GetDatMonSignalInfoP5_DT.dll"
KGP_DLL = DEFAULT_ROOT / "bin/KgpDataCtrl.dll"
DBC = REPO / "REFERENCE/opendbc/opendbc/dbc/generator/toyota/toyota_secoc_pt.dbc"
RX_MAP = REPO / "data/application_rx_map.csv"
TARGET_MONITORS = (60, 402, 403)
REGIONS = ("NA", "EU", "JP")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def section_records(db, table_type: int) -> list[bytes]:
    section = db.sections[table_type]
    size = section.record_size
    return [
        section.raw_data[i * size:(i + 1) * size]
        for i in range(section.header.record_count)
    ]


def find_u16_record(records: list[bytes], offset: int, key: int) -> tuple[int, bytes]:
    matches = [
        (index, raw)
        for index, raw in enumerate(records)
        if struct.unpack_from("<H", raw, offset)[0] == key
    ]
    if len(matches) != 1:
        raise ValueError(f"expected one key={key} at +0x{offset:x}, got {len(matches)}")
    return matches[0]


def decode_monitor(parser: DDBParser, root: Path, region: str, monitor_key: int) -> dict:
    db_path = root / region / "DB/EMPS_P5.ddb"
    db = parser.parse_ecu_db(db_path)
    strings = parser.load_string_db(root / region / "DB/M_English.ddb")

    monitor_index, monitor_raw = find_u16_record(section_records(db, 62), 0x24, monitor_key)
    name_index = struct.unpack_from("<I", monitor_raw, 0x18)[0]
    physical_key = struct.unpack_from("<H", monitor_raw, 0x2A)[0]
    bit_start = struct.unpack_from("<H", monitor_raw, 0x2C)[0]
    bit_end = struct.unpack_from("<H", monitor_raw, 0x2E)[0]
    sort_key = struct.unpack_from("<H", monitor_raw, 0x30)[0]
    pattern_key = struct.unpack_from("<H", monitor_raw, 0x32)[0]

    physical_index, physical_raw = find_u16_record(section_records(db, 13), 0x0C, physical_key)
    unit_key = struct.unpack_from("<H", physical_raw, 0x0E)[0]
    unit_index, unit_raw = find_u16_record(section_records(db, 15), 0x04, unit_key)
    unit_string_index = struct.unpack_from("<I", unit_raw, 0x00)[0]
    unit = strings.get_string(unit_string_index) if unit_string_index else None

    patterns = []
    if pattern_key:
        for index, raw in enumerate(section_records(db, 14)):
            if struct.unpack_from("<H", raw, 0x0C)[0] != pattern_key:
                continue
            patterns.append(
                {
                    "record_index": index,
                    "raw_hex": raw.hex(),
                    "raw_value_u32": struct.unpack_from("<I", raw, 0x04)[0],
                    "display_string_index": struct.unpack_from("<I", raw, 0x00)[0],
                    "display": strings.get_string(struct.unpack_from("<I", raw, 0x00)[0]),
                }
            )

    # Consumer-proven related-table keys only.  These are intentionally not a
    # scan of arbitrary u16 values inside unknown record layouts.
    related_specs = {
        61: ("data_id_u16", 0x02),
        63: ("data_id_bit_for_dm_key_u16", 0x00),
        80: ("data_id_bit_for_ffd_key_u16", 0x00),
        88: ("behavior_key_u16", 0x24),
        90: ("rob_data_id_u16", 0x02),
        91: ("behavior_signal_check_key_u16", 0x00),
    }
    related_hits = []
    for table_type, (field, offset) in related_specs.items():
        if table_type not in db.sections:
            continue
        for index, raw in enumerate(section_records(db, table_type)):
            if struct.unpack_from("<H", raw, offset)[0] != monitor_key:
                continue
            hit = {
                "table_type": table_type,
                "field": field,
                "record_index": index,
                "raw_hex": raw.hex(),
            }
            if table_type == 88:
                behavior_name_index = struct.unpack_from("<I", raw, 0x18)[0]
                hit["resolved_name"] = strings.get_string(behavior_name_index)
            related_hits.append(hit)

    active_test_exact_name_hits = []
    if 11 in db.sections:
        for index, raw in enumerate(section_records(db, 11)):
            name_idx = struct.unpack_from("<I", raw, 0x20)[0]
            name = strings.get_string(name_idx)
            if name and name == strings.get_string(name_index):
                active_test_exact_name_hits.append(index)

    return {
        "region": region,
        "database": "EMPS_P5.ddb",
        "database_sha256": sha256(db_path),
        "monitor": {
            "record_index": monitor_index,
            "raw_hex": monitor_raw.hex(),
            "key": monitor_key,
            "name_string_index": name_index,
            "name": strings.get_string(name_index),
            "physical_data_key": physical_key,
            "bit_start": bit_start,
            "bit_end": bit_end,
            "bit_width": bit_end - bit_start + 1,
            "sort_key": sort_key,
            "pattern_display_key": pattern_key,
        },
        "physical_data": {
            "record_index": physical_index,
            "raw_hex": physical_raw.hex(),
            "key": physical_key,
            "unit_key": unit_key,
        },
        "unit": {
            "record_index": unit_index,
            "raw_hex": unit_raw.hex(),
            "key": unit_key,
            "string_index": unit_string_index,
            "text": unit,
        },
        "pattern_display": patterns,
        "related_table_hits": related_hits,
        "active_test_exact_name_hits": active_test_exact_name_hits,
    }


def master_route(parser: DDBParser, root: Path, region: str) -> dict:
    master_path = root / region / "DB/Toyota.ddb"
    master = parser.parse_master_db(master_path)
    strings = parser.load_string_db(root / region / "DB/M_English.ddb")
    categories = parser.extract_master_ecu_categories(master.sections[16])
    matches = [(index, row) for index, row in enumerate(categories) if row.database_name == "EMPS_P5.ddb"]
    if len(matches) != 1:
        raise ValueError(f"{region}: expected one EMPS_P5 category, got {len(matches)}")
    record_index, category = matches[0]
    dlls = sorted(
        (
            {"dll_role_id": row.dll_role_id, "dll_name": row.dll_name}
            for row in parser.extract_master_dlls(master.sections[19])
            if row.category_id == category.category_id
        ),
        key=lambda row: (row["dll_role_id"], row["dll_name"]),
    )
    return {
        "region": region,
        "master_sha256": sha256(master_path),
        "record_index": record_index,
        "category_id": category.category_id,
        "generation": category.generation,
        "resolved_ecu_name": strings.get_string(category.ecu_name_string_index),
        "database_name": category.database_name,
        "dlls": dlls,
    }


def firmware_command_side() -> dict:
    with RX_MAP.open(newline="", encoding="utf-8") as stream:
        row = next(row for row in csv.DictReader(stream) if row.get("signal_id") == "61")
    dbc_text = DBC.read_text(encoding="utf-8")
    match = re.search(
        r"SG_\s+STEER_TORQUE_CMD\s*:\s*15\|16@0-\s*\(1,0\)",
        dbc_text,
    )
    if not match:
        raise ValueError("pinned Toyota DBC STEER_TORQUE_CMD geometry changed")
    return {
        "firmware_rx_signal": {
            "signal_id": 61,
            "can_id": row["can_id"],
            "wire_field": row["wire_field"],
            "bit_length": int(row["bit_length"]),
            "signed": row["signed"] == "1",
            "secoc_envelope": row["secoc_envelope"] == "yes",
            "destination": row["dest"],
            "command_chain": (
                "0xFEBE7F94 -> 0xFEBEF184 -> 0xFEBEAE20 -> "
                "steering command conditioning/status paths"
            ),
        },
        "public_dbc": {
            "relative_path": DBC.relative_to(REPO).as_posix(),
            "sha256": sha256(DBC),
            "message_can_id": "0x2E4",
            "message_name": "STEERING_LKA",
            "signal_name": "STEER_TORQUE_CMD",
            "bit_length": 16,
            "signed": True,
            "scale": 1,
            "offset": 0,
        },
    }


def build(root: Path) -> dict:
    parser = DDBParser()
    routes = [master_route(parser, root, region) for region in REGIONS]
    monitors = {
        str(key): [decode_monitor(parser, root, region, key) for region in REGIONS]
        for key in TARGET_MONITORS
    }

    # The targeted metadata is expected to be byte-identical across regions.
    for key, variants in monitors.items():
        semantic_projection = [
            {
                "monitor": item["monitor"],
                "physical_data": item["physical_data"],
                "unit": item["unit"],
                "pattern_display": item["pattern_display"],
                "related_table_hits": item["related_table_hits"],
                "active_test_exact_name_hits": item["active_test_exact_name_hits"],
            }
            for item in variants
        ]
        if not all(item == semantic_projection[0] for item in semantic_projection[1:]):
            raise ValueError(f"monitor {key} semantics diverge across NA/EU/JP")

    command = monitors["402"][0]
    cooperation = monitors["60"][0]
    control_state = monitors["403"][0]
    if command["monitor"]["name"] != "Command Value Torque":
        raise ValueError("monitor 402 name changed")
    if command["monitor"]["bit_width"] != 16 or command["unit"]["text"] != "Nm":
        raise ValueError("monitor 402 16-bit/Nm constraints changed")
    if cooperation["pattern_display"] != [
        {
            "record_index": 63,
            "raw_hex": "fc3902000000000000000000160001000000000000000100",
            "raw_value_u32": 0,
            "display_string_index": 145916,
            "display": "Cooperation Control",
        },
        {
            "record_index": 64,
            "raw_hex": "ca3c02000100000000000000160002000000000000000100",
            "raw_value_u32": 1,
            "display_string_index": 146634,
            "display": "Other than Cooperation Control",
        },
    ]:
        raise ValueError("monitor 60 display pattern changed")
    if control_state["monitor"]["bit_width"] != 16:
        raise ValueError("monitor 403 width changed")

    return {
        "schema_version": 1,
        "source": "Techstream V18.00.003 + pinned Toyota opendbc",
        "artifacts": {
            "kgp_data_ctrl": {
                "relative_path": KGP_DLL.relative_to(REPO).as_posix(),
                "sha256": sha256(KGP_DLL),
            },
            "p5_signal_info": {
                "relative_path": SIGNAL_INFO_DLL.relative_to(REPO).as_posix(),
                "sha256": sha256(SIGNAL_INFO_DLL),
            },
        },
        "master_routes": routes,
        "monitors": monitors,
        "firmware_command_side": firmware_command_side(),
        "correlations": [
            {
                "id": "APP-COR-001",
                "disposition": "accepted-corroboration",
                "firmware_concept": "authenticated CAN 0x2E4 signal 61 steering command domain",
                "techstream_monitor_key": 402,
                "techstream_name": "Command Value Torque",
                "matching_constraints": [
                    "EMPS_P5 category 405 / generation 20",
                    "P5 data-monitor routing includes GetDatMonListP5_DT.dll and GetDatMonSignalInfoP5_DT.dll",
                    "Techstream monitor width is 16 bits",
                    "Techstream physical-data/unit chain resolves to Nm",
                    "firmware signal 61 is authenticated signed 16-bit CAN 0x2E4 B1..B2",
                    "pinned public Toyota DBC independently calls the same 0x2E4 16-bit field STEER_TORQUE_CMD",
                    "firmware command-conditioning chain from signal 61 is independently recovered",
                ],
                "boundary": (
                    "Strong external vocabulary/shape/unit corroboration for the recovered steering-command "
                    "domain; no claim that Techstream monitor 402 reads the CAN 0x2E4 COM destination directly."
                ),
            },
            {
                "id": "APP-COR-002",
                "disposition": "ambiguous",
                "firmware_concept": "externally visible 0x262 LTA/LKA steering-state aggregates",
                "techstream_monitor_key": 60,
                "techstream_name": "Cooperation Control State",
                "matching_constraints": [
                    "EMPS_P5 steering category",
                    "8-bit diagnostic monitor",
                    "display pattern is binary Cooperation Control / Other than Cooperation Control",
                    "same key/name also appears in P5 behavior-data section 88",
                ],
                "blocking_difference": (
                    "No firmware-static diagnostic-monitor-to-CAN-status edge identifies which, if any, "
                    "0x262 LTA/LKA bit or aggregate carries this diagnostic state."
                ),
            },
            {
                "id": "APP-COR-003",
                "disposition": "rejected-direct-name",
                "firmware_concept": "specific 0x262 LTA_STATE/LKA_STATE field or bit",
                "techstream_monitor_key": 403,
                "techstream_name": "Control State Information",
                "matching_constraints": [
                    "EMPS_P5 steering category",
                    "16-bit unitless diagnostic monitor",
                ],
                "rejection_reason": (
                    "The generic 16-bit diagnostic state has no recovered route to one specific 0x262 "
                    "aggregate/bit, so using this name for a CAN field would be lexical projection."
                ),
            },
        ],
        "negative_search": {
            "consumer_proven_related_tables_checked": [61, 63, 80, 88, 90, 91],
            "monitor_402_related_hits": command["related_table_hits"],
            "monitor_403_related_hits": control_state["related_table_hits"],
            "monitor_60_related_hits": cooperation["related_table_hits"],
            "active_test_exact_name_hits": {
                key: monitors[str(key)][0]["active_test_exact_name_hits"]
                for key in TARGET_MONITORS
            },
            "boundary": (
                "No key 402/403 join was found in the consumer-proven P5 data-ID-bit/freeze-bit/behavior/"
                "RoB tables listed above. Type-65 DTC layout is not included because its key schema is not "
                "consumer-proven here. Absence is not a whole-diagnostic-system negative."
            ),
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    result = build(args.root.resolve())
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(
        "correlations",
        [(item["id"], item["disposition"]) for item in result["correlations"]],
    )
    print(f"Wrote {args.output}")


if __name__ == "__main__":
    main()
