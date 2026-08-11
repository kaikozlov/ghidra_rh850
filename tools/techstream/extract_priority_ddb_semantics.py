#!/usr/bin/env python3
"""Generate consumer-proven schemas for priority steering DDB sections."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import pefile

from parse_ddb import DDBParser, ECU_TABLE_CLASS_NAMES


REPO = Path(__file__).resolve().parents[2]
DEFAULT_ROOT = REPO / "Techstream/unpacked/toyota/Toyota Diagnostics/Techstream"
DEFAULT_PE = DEFAULT_ROOT / "bin/KgpDataCtrl.dll"
DEFAULT_OUTPUT = REPO / "data/generated/techstream_v18/priority_steering_ddb_semantics.json"
PRIORITY_TYPES = (6, 11, 12, 61, 62, 63, 80, 87, 88, 90, 91)

SCHEMAS = {
    6: {
        "record_size": 8,
        "fields": {"pid_key_u8": {"offset": 2, "width": 1}},
        "consumers": [("CDbPidTable::FindDbItem1", 0x10041D29, "+0x02 byte lookup")],
    },
    11: {
        "record_size": 92,
        "fields": {
            "active_test_name_string_index": {"offset": 32, "width": 4},
            "secondary_key_u16": {"offset": 56, "width": 2},
            "primary_key_u8": {"offset": 82, "width": 1},
        },
        "consumers": [
            ("CDbActTestResRecords::SetRecString", 0x10005E4A, "+0x20 string index"),
            ("CDbActTestTable::FindDbItem2", 0x100062FD, "+0x38 u16 lookup"),
            ("CDbActTestTable::FindDbItem1", 0x100061EF, "+0x52 byte lookup"),
        ],
    },
    12: {
        "record_size": 24,
        "fields": {"pattern_key_u16": {"offset": 0, "width": 2}},
        "consumers": [("CDbActTestPatternTable::FindDbItem1", 0x100056F9, "+0x00 u16 lookup")],
    },
    61: {
        "record_size": 8,
        "fields": {"data_id_u16": {"offset": 2, "width": 2}},
        "consumers": [("CDbDataIdForDmTable::FindDbItem1", 0x10027329, "+0x02 u16 lookup")],
    },
    62: {
        "record_size": 64,
        "fields": {
            "name_string_index": {"offset": 24, "width": 4},
            "monitor_key_u16": {"offset": 36, "width": 2},
            "sort_key_u16": {"offset": 48, "width": 2},
        },
        "consumers": [
            ("CDbDatamonitorP5ResRecords::SetRecString", 0x1002857A, "+0x18 string index"),
            ("CDbDatamonitorP5Table::FindDbItem1", 0x10028719, "+0x24 u16 lookup"),
            ("CDbDatamonitorP5ResRecords::SortInOrder", 0x10028492, "+0x30 u16 sort")
        ],
    },
    63: {
        "record_size": 16,
        "fields": {
            "lookup_key_u16": {"offset": 0, "width": 2},
            "variable_index_u16": {"offset": 2, "width": 2},
        },
        "consumers": [
            ("CDbDataIdBitForDmTable::FindDbItem1", 0x10025749, "+0x00 u16 lookup"),
            ("CDbDataIdBitForDmResRecords::SetRecVariableData", 0x1002556A, "+0x02 variable index"),
        ],
    },
    80: {
        "record_size": 12,
        "fields": {
            "lookup_key_u16": {"offset": 0, "width": 2},
            "variable_index_u16": {"offset": 2, "width": 2},
        },
        "consumers": [
            ("CDbDataIdBitForFfdTable::FindDbItem1", 0x10025D79, "+0x00 u16 lookup"),
            ("CDbDataIdBitForFfdResRecords::SetRecVariableData", 0x10025B9A, "+0x02 variable index"),
        ],
    },
    87: {
        "record_size": 28,
        "fields": {
            "behavior_signature": {"offset": 0, "width": 12, "encoding": "UTF-16LE"},
            "name_string_index": {"offset": 12, "width": 4},
            "comment_string_index": {"offset": 16, "width": 4},
        },
        "consumers": [
            ("CDbBehaviorCodeResRecords::GetBehaviorCodeSig", 0x10007DB5, "+0x00 inline signature"),
            ("CDbBehaviorCodeResRecords::SetRecString", 0x10007B8D, "+0x0C/+0x10 string indices"),
        ],
    },
    88: {
        "record_size": 60,
        "fields": {
            "name_string_index": {"offset": 24, "width": 4},
            "behavior_key_u16": {"offset": 36, "width": 2},
            "sort_key_u16": {"offset": 46, "width": 2},
        },
        "consumers": [
            ("CDbBehaviorDataRecordP5ResRecords::SetRecString", 0x1000862A, "+0x18 string index"),
            ("CDbBehaviorDataRecordP5Table::FindDbItem1", 0x100087C9, "+0x24 u16 lookup"),
            ("CDbBehaviorDataRecordP5ResRecords::SortInOrder", 0x10008542, "+0x2E u16 sort"),
        ],
    },
    90: {
        "record_size": 8,
        "fields": {"data_id_u16": {"offset": 2, "width": 2}},
        "consumers": [("CDbDataIdForRobTable::FindDbItem1", 0x10027789, "+0x02 u16 lookup")],
    },
    91: {
        "record_size": 12,
        "fields": {"behavior_key_u16": {"offset": 0, "width": 2}},
        "consumers": [("CDbBehaviorSignalCheckTable::FindDbItem1", 0x10009A09, "+0x00 u16 lookup")],
    },
}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def schemas_with_identity(pe: pefile.PE) -> dict[str, dict]:
    image_base = pe.OPTIONAL_HEADER.ImageBase
    output = {}
    for table_type, schema in SCHEMAS.items():
        consumers = []
        for name, va, evidence in schema["consumers"]:
            prefix = pe.get_data(va - image_base, 64)
            consumers.append(
                {
                    "method": name,
                    "va": f"0x{va:08X}",
                    "evidence": evidence,
                    "identity_kind": "64-byte method prefix",
                    "prefix_sha256": sha256(prefix),
                }
            )
        output[str(table_type)] = {
            "class_name": ECU_TABLE_CLASS_NAMES[table_type],
            "record_size": schema["record_size"],
            "fields": schema["fields"],
            "consumers": consumers,
            "unknown_bytes_policy": "complete raw_hex retained per record",
        }
    return output


def build(root: Path, pe_path: Path) -> dict:
    parser = DDBParser()
    pe_bytes = pe_path.read_bytes()
    pe = pefile.PE(data=pe_bytes, fast_load=False)
    sources = []
    steering_files = sorted(
        path
        for path in root.glob("*/DB/*.ddb")
        if path.name.upper().startswith(("EPS", "EMPS"))
    )
    for path in steering_files:
        db = parser.parse_ecu_db(path)
        selected = sorted(set(db.sections) & set(PRIORITY_TYPES))
        if not selected:
            continue
        region = path.relative_to(root).parts[0]
        strings = parser.load_string_db(root / region / "DB/M_English.ddb")
        sections = {}
        for table_type in selected:
            section = db.sections[table_type]
            decoded = parser.extract_priority_records(section)
            records = []
            for index, record in enumerate(decoded):
                fields = dict(record.fields)
                if "name_string_index" in fields:
                    fields["resolved_name"] = strings.get_string(fields["name_string_index"])
                if "comment_string_index" in fields:
                    fields["resolved_comment"] = strings.get_string(
                        fields["comment_string_index"]
                    )
                if "active_test_name_string_index" in fields:
                    fields["resolved_active_test_name"] = strings.get_string(
                        fields["active_test_name_string_index"]
                    )
                records.append({"record_index": index, "fields": fields, "raw_hex": record.raw.hex()})
            sections[str(table_type)] = {
                "record_count": section.header.record_count,
                "record_size": section.record_size,
                "payload_sha256": sha256(section.raw_data),
                "records": records,
            }
        source_bytes = path.read_bytes()
        sources.append(
            {
                "relative_path": path.relative_to(root).as_posix(),
                "size": len(source_bytes),
                "sha256": sha256(source_bytes),
                "sections": sections,
            }
        )
    return {
        "schema_version": 1,
        "source": "Techstream V18.00.003",
        "artifact": {
            "relative_path": pe_path.relative_to(REPO).as_posix(),
            "size": len(pe_bytes),
            "sha256": sha256(pe_bytes),
        },
        "schemas": schemas_with_identity(pe),
        "sources": sources,
        "summary": {
            "steering_files_with_priority_sections": len(sources),
            "section_instances": sum(len(item["sections"]) for item in sources),
            "decoded_records": sum(
                section["record_count"]
                for item in sources
                for section in item["sections"].values()
            ),
        },
        "interpretation_boundary": (
            "Only fields directly consumed by the pinned exported methods are named; "
            "all other bytes remain available solely as raw_hex. Numeric joins to "
            "Sienna firmware are not asserted by this artifact."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--pe", type=Path, default=DEFAULT_PE)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    result = build(args.root.resolve(), args.pe.resolve())
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(result["summary"])
    print(f"Wrote {args.output}")


if __name__ == "__main__":
    main()
