#!/usr/bin/env python3
"""Extract field-proven Toyota.ddb routes for the priority steering families."""

from __future__ import annotations

import argparse
import hashlib
import json
import struct
from pathlib import Path

from parse_ddb import DDBParser


REPO = Path(__file__).resolve().parents[2]
DEFAULT_ROOT = REPO / "Techstream/unpacked/toyota/Toyota Diagnostics/Techstream"
DEFAULT_OUTPUT = REPO / "data/generated/techstream_v18/toyota_master_routes.json"
TARGET_DATABASES = ("EPS_P4DK3.ddb", "EPS_CAN_P4DK.ddb", "EMPS_P5.ddb")


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def record_source(section, index: int, raw: bytes) -> dict:
    return {
        "record_index": index,
        "logical_payload_offset": index * len(raw),
        "on_disk_section_data_offset": section.data_offset,
        "on_disk_record_offset": (
            section.data_offset + index * len(raw)
            if section.header.compression == 0
            else None
        ),
        "compression": section.header.compression,
        "raw_hex": raw.hex(),
        "raw_sha256": sha256(raw),
    }


def comm_records(parser: DDBParser, master, strings) -> dict:
    did_section = master.sections[62]
    did_raw = did_section.decoded_data
    did_size = did_section.decoded_record_size
    dids = []
    for index in range(did_section.header.record_count):
        raw = did_raw[index * did_size : (index + 1) * did_size]
        dids.append(
            {
                **record_source(did_section, index, raw),
                "primary_key_u16": struct.unpack_from("<H", raw, 0)[0],
                "secondary_key_u16": struct.unpack_from("<H", raw, 16)[0],
            }
        )

    rid_section = master.sections[88]
    rid_raw = rid_section.decoded_data
    rid_size = rid_section.decoded_record_size
    rids = []
    for index in range(rid_section.header.record_count):
        raw = rid_raw[index * rid_size : (index + 1) * rid_size]
        string_index = struct.unpack_from("<I", raw, 12)[0]
        rids.append(
            {
                **record_source(rid_section, index, raw),
                "unit_name_string_index": string_index,
                "resolved_unit_name": strings.get_string(string_index),
                "primary_key_u16": struct.unpack_from("<H", raw, 16)[0],
                "secondary_key_u16": struct.unpack_from("<H", raw, 26)[0],
            }
        )
    return {"communication_did_records": dids, "communication_rid_records": rids}


def region_routes(root: Path, region: str) -> dict:
    parser = DDBParser()
    db_path = root / region / "DB/Toyota.ddb"
    string_path = root / region / "DB/M_English.ddb"
    master = parser.parse_master_db(db_path)
    strings = parser.load_string_db(string_path)
    categories = parser.extract_master_ecu_categories(master.sections[16])
    dlls = parser.extract_master_dlls(master.sections[19])
    functions = parser.extract_master_functions(master.sections[26])
    details = parser.extract_master_function_details(master.sections[27])

    routes = []
    for database_name in TARGET_DATABASES:
        matches = [
            (index, entry)
            for index, entry in enumerate(categories)
            if entry.database_name == database_name
        ]
        if not matches:
            continue
        if len(matches) != 1:
            raise ValueError(
                f"{region} expected one {database_name} category, got {len(matches)}"
            )
        category_index, category = matches[0]
        category_functions = [
            (index, entry)
            for index, entry in enumerate(functions)
            if entry.category_id == category.category_id
        ]
        category_details = [
            (index, entry)
            for index, entry in enumerate(details)
            if entry.category_id == category.category_id
        ]
        category_dlls = [
            (index, entry)
            for index, entry in enumerate(dlls)
            if entry.category_id == category.category_id
        ]
        routes.append(
            {
                "database_name": database_name,
                "category": {
                    **record_source(master.sections[16], category_index, category.raw),
                    "category_id": category.category_id,
                    "generation": category.generation,
                    "ecu_short_name": category.ecu_short_name,
                    "ecu_name_string_index": category.ecu_name_string_index,
                    "resolved_ecu_name": strings.get_string(category.ecu_name_string_index),
                },
                "functions": [
                    {
                        **record_source(master.sections[26], index, entry.raw),
                        "category_id": entry.category_id,
                        "function_id": entry.function_id,
                        "sort_key": entry.sort_key,
                        "name_string_index": entry.name_string_index,
                        "resolved_name": strings.get_string(entry.name_string_index),
                        "description_string_index": entry.description_string_index,
                        "resolved_description": strings.get_string(
                            entry.description_string_index
                        ),
                    }
                    for index, entry in category_functions
                ],
                "function_details": [
                    {
                        **record_source(master.sections[27], index, entry.raw),
                        "category_id": entry.category_id,
                        "function_id": entry.function_id,
                        "detail_id": entry.detail_id,
                        "name_string_index": entry.name_string_index,
                        "resolved_name": strings.get_string(entry.name_string_index),
                    }
                    for index, entry in category_details
                ],
                "dlls": [
                    {
                        **record_source(master.sections[19], index, entry.raw),
                        "category_id": entry.category_id,
                        "dll_role_id": entry.dll_role_id,
                        "dll_name": entry.dll_name,
                    }
                    for index, entry in category_dlls
                ],
            }
        )

    db_bytes = db_path.read_bytes()
    return {
        "region": region,
        "source": {
            "relative_path": db_path.relative_to(REPO).as_posix(),
            "size": len(db_bytes),
            "sha256": sha256(db_bytes),
        },
        "routes": routes,
        **comm_records(parser, master, strings),
    }


def build(root: Path) -> dict:
    result = {
        "schema_version": 1,
        "source": "Techstream V18.00.003",
        "targets": list(TARGET_DATABASES),
        "field_provenance": {
            "type_16": {
                "class": "CDbEcuCategoryTable",
                "record_size": 76,
                "fields": {
                    "database_name": "GetEcuFileName returns +0x00",
                    "ecu_short_name": "GetEcuShortName returns +0x28",
                    "ecu_name_string_index": "SetRecString consumes +0x3C",
                    "category_id": "FindDbItem1 and ComparativeKey consume +0x44",
                },
            },
            "type_19": {
                "class": "CDbDllTable",
                "record_size": 88,
                "fields": {
                    "category_id": "FindDbItem2 consumes +0x50",
                    "dll_role_id": "FindDbItem1 consumes +0x56",
                },
            },
            "type_26": {
                "class": "CDbEcuFuncInfoTable",
                "record_size": 24,
                "fields": {
                    "name/description_string_index": "SetRecString consumes +0x00/+0x04",
                    "category_id": "FindDbItem1 consumes +0x08",
                    "function_id": "FindDbItem2 consumes +0x0A",
                    "sort_key": "ComparativeKey consumes +0x14",
                },
            },
            "type_27": {
                "class": "CDbEcuFuncDetailsTable",
                "record_size": 24,
                "fields": {
                    "name_string_index": "SetRecString consumes +0x00",
                    "category/function/detail": "ComparativeKey consumes +0x04/+0x06/+0x08",
                },
            },
            "type_62": {
                "class": "CDbCommDidDataTable",
                "record_size": 24,
                "fields": {
                    "primary_key": "FindDbItem1 consumes +0x00",
                    "secondary_key": "ComparativeKey consumes +0x10",
                },
            },
            "type_88": {
                "class": "CDbCommRidDataTable",
                "record_size": 36,
                "fields": {
                    "unit_name_string_index": "SetRecString consumes +0x0C",
                    "primary/secondary_key": "Find/ComparativeKey consume +0x10/+0x1A",
                },
            },
        },
        "regions": [region_routes(root, region) for region in ("NA", "EU", "JP")],
        "unresolved_joins": [
            "type-19 dll_role_id names are not assigned without a consuming enum",
            "type-62/88 communication records expose no category-id field in their table consumers",
            "no literal 8965B4512000 calibration identifier occurs in the master databases",
        ],
    }
    na_routes = {
        route["database_name"]: route["category"]["record_index"]
        for route in result["regions"][0]["routes"]
    }
    if na_routes != {
        "EPS_P4DK3.ddb": 294,
        "EPS_CAN_P4DK.ddb": 496,
        "EMPS_P5.ddb": 374,
    }:
        raise ValueError(f"NA priority anchors diverged: {na_routes}")
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    result = build(args.root.resolve())
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    for region in result["regions"]:
        print(
            region["region"],
            [(route["database_name"], route["category"]["record_index"])
             for route in region["routes"]],
        )
    print(f"Wrote {args.output}")


if __name__ == "__main__":
    main()
