#!/usr/bin/env python3
"""Extract every steering ECU database in the Techstream V18 corpus.

The Sienna correlation pipeline intentionally uses two NA EPS databases for
firmware annotation.  This companion artifact inventories and decodes every
EPS/EMPS database across NA, JP, and EU so variant evidence is not silently
lost.  Byte-identical semantic variants are grouped while preserving all source
paths.
"""

from __future__ import annotations

import hashlib
import json
import struct
from pathlib import Path

from parse_ddb import DDBParser, ECUDataBase, StringDataBase

REPO_ROOT = Path(__file__).resolve().parents[2]
TECHSTREAM_ROOT = (
    REPO_ROOT / "Techstream/unpacked/toyota/Toyota Diagnostics/Techstream"
)
OUTPUT_PATH = (
    REPO_ROOT
    / "data/generated/techstream_v18/steering_diagnostic_corpus.json"
)


def semantic_hash(db: ECUDataBase) -> str:
    """Hash parsed section metadata and payloads, ignoring regional file tags."""
    digest = hashlib.sha256()
    digest.update(bytes([db.format_version]))
    for section_type, section in sorted(db.sections.items()):
        header = section.header
        digest.update(
            struct.pack(
                "<BBII",
                section_type,
                header.compression,
                header.record_count,
                header.payload_size,
            )
        )
        digest.update(section.raw_data)
    return digest.hexdigest()


def extract_dtcs(db: ECUDataBase, strings: StringDataBase) -> list[dict]:
    section = db.sections.get(5)
    if section is None:
        return []
    if section.record_size != 28:
        raise ValueError(
            f"{db.path.name} DTC record size is {section.record_size}, expected 28"
        )
    entries = []
    for index in range(section.header.record_count):
        raw = section.raw_data[index * 28 : (index + 1) * 28]
        name_index = struct.unpack_from("<I", raw, 12)[0]
        entries.append(
            {
                "record_index": index,
                "code": raw[:12]
                .decode("utf-16-le", errors="replace")
                .rstrip("\x00"),
                "dtc_identifier": struct.unpack_from("<H", raw, 20)[0],
                "name_string_index": name_index,
                "resolved_name": strings.get_string(name_index),
            }
        )
    return entries


def extract_supported_pid_records(db: ECUDataBase) -> list[dict]:
    section = db.sections.get(3)
    if section is None:
        return []
    return [
        {
            "record_index": index,
            "raw_hex": raw.hex(),
            "support_key_hex": raw[4:6].hex(),
        }
        for index, raw in enumerate(DDBParser.extract_supported_pid_records(section))
    ]


def extract_dids(db: ECUDataBase) -> list[dict]:
    """Preserve real type-7 ``CDbDidTable`` rows with bounded key semantics."""
    section = db.sections.get(7)
    if section is None:
        return []
    records = [
        section.raw_data[index * 8 : (index + 1) * 8]
        for index in range(section.header.record_count)
    ]
    return [
        {
            "record_index": index,
            "identifier_u16_le": identifier,
            "identifier_bytes_hex": raw[4:6].hex(),
            "raw_hex": raw.hex(),
        }
        for index, (identifier, raw) in enumerate(
            zip(DDBParser.extract_dids(section), records)
        )
    ]


def extract_monitors(db: ECUDataBase, strings: StringDataBase) -> list[dict]:
    section = db.sections.get(10)
    if section is None:
        return []
    record_size = section.record_size
    if record_size < 60:
        raise ValueError(
            f"{db.path.name} monitor record size {record_size} is too short"
        )
    entries = []
    for index in range(section.header.record_count):
        raw = section.raw_data[
            index * record_size : (index + 1) * record_size
        ]
        name_index = struct.unpack_from("<I", raw, 48)[0]
        description_index = struct.unpack_from("<I", raw, 52)[0]
        entries.append(
            {
                "record_index": index,
                "record_size": record_size,
                "source_table_class": "CDbFreezeTable",
                "monitor_seq": struct.unpack_from("<I", raw, 56)[0],
                "name_string_index": name_index,
                "resolved_name": strings.get_string(name_index),
                "description_string_index": description_index,
                "resolved_description": strings.get_string(description_index),
            }
        )
    return entries


def build_steering_corpus() -> dict:
    parser = DDBParser()
    strings = parser.load_string_db(TECHSTREAM_ROOT / "NA/DB/M_English.ddb")
    source_paths = sorted(
        path
        for path in TECHSTREAM_ROOT.glob("*/DB/*.ddb")
        if path.stem.startswith(("EPS", "EMPS"))
    )

    groups: dict[str, dict] = {}
    for path in source_paths:
        db = parser.parse_ecu_db(path)
        digest = semantic_hash(db)
        relative_path = path.relative_to(TECHSTREAM_ROOT).as_posix()
        group = groups.get(digest)
        if group is None:
            group = {
                "semantic_sha256": digest,
                "representative_file": relative_path,
                "source_files": [],
                "format_version": db.format_version,
                "sections": {
                    str(section_type): {
                        "record_count": section.header.record_count,
                        "record_size": section.record_size,
                        "payload_size": section.header.payload_size,
                    }
                    for section_type, section in sorted(db.sections.items())
                },
                "dtcs": extract_dtcs(db, strings),
                "supported_pid_records": extract_supported_pid_records(db),
                "dids": extract_dids(db),
                "monitors": extract_monitors(db, strings),
            }
            groups[digest] = group
        group["source_files"].append(relative_path)

    variants = sorted(groups.values(), key=lambda item: item["representative_file"])
    dtc_ids = {
        entry["dtc_identifier"]
        for variant in variants
        for entry in variant["dtcs"]
        if entry["dtc_identifier"]
    }
    did_ids = {
        entry["identifier_bytes_hex"]
        for variant in variants
        for entry in variant["dids"]
    }
    supported_pid_keys = {
        entry["support_key_hex"]
        for variant in variants
        for entry in variant["supported_pid_records"]
    }
    return {
        "description": (
            "Complete regional Techstream V18 EPS/EMPS diagnostic corpus. "
            "Semantic duplicates are grouped; no firmware-calibration match is implied."
        ),
        "techstream_distribution": "V18.00.003",
        "string_database": {
            "file": "NA/DB/M_English.ddb",
            "entry_count": strings.entry_count,
            "decompressed_size": len(strings.decompressed),
        },
        "summary": {
            "source_files": len(source_paths),
            "semantic_variants": len(variants),
            "dtc_records": sum(len(variant["dtcs"]) for variant in variants),
            "unique_dtc_identifiers": len(dtc_ids),
            "did_records": sum(len(variant["dids"]) for variant in variants),
            "unique_did_record_keys": len(did_ids),
            "supported_pid_records": sum(
                len(variant["supported_pid_records"]) for variant in variants
            ),
            "unique_supported_pid_record_keys": len(supported_pid_keys),
            "monitor_records": sum(
                len(variant["monitors"]) for variant in variants
            ),
        },
        "source_files": [
            path.relative_to(TECHSTREAM_ROOT).as_posix() for path in source_paths
        ],
        "semantic_variants": variants,
    }


def main() -> None:
    corpus = build_steering_corpus()
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(corpus, indent=2, ensure_ascii=False))
    summary = corpus["summary"]
    print(f"Wrote {OUTPUT_PATH}")
    print(
        f"  {summary['source_files']} files, "
        f"{summary['semantic_variants']} semantic variants"
    )
    print(
        f"  {summary['unique_dtc_identifiers']} unique DTC IDs, "
        f"{summary['did_records']} CDbDidTable records, "
        f"{summary['unique_supported_pid_record_keys']} supported-PID keys, "
        f"{summary['monitor_records']} monitor records"
    )


if __name__ == "__main__":
    main()
