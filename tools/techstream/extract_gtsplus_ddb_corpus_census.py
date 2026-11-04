#!/usr/bin/env python3
"""Build a reproducible census of the current GTS+ Toyota DDB corpus.

The goal is not to infer ECU behavior from strings.  It records exact corpus
geometry, exact host-factory table identities, resolved Active Test names, and
selected P5/P6 steering/control vocabulary with the ownership boundaries kept
explicit.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import struct
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import pefile
from tools.techstream.ddb_semantics import monitor_rows
from tools.techstream.ddb_strings import load_string_db
from tools.techstream.parse_ddb import DDBParser, ECU_TABLE_CLASS_NAMES
from tools.techstream.extract_gtsplus_factory_table_map import (
    FACTORIES, _supplemental_sources, extract_factory,
)
from tools.techstream.techstream_paths import resolve_gts_root
from tools import REPO_ROOT


DEFAULT_OUTPUT = REPO_ROOT / "data/generated/gtsplus_2026/ddb_corpus_census.json"
REGIONS = ("NA", "EU", "JP")
FAMILIES = ("Gen", "Spe")
ACTIVE_LAYOUTS = {
    11: {"record_size": 92, "name_offset": 0x20},
    68: {"record_size": 64, "name_offset": 0x0C},
    71: {"record_size": 72, "name_offset": 0x08},
}
CONTROL_NAME_RE = re.compile(
    r"steer|\beps\b|\blta\b|\blda\b|\blca\b|collision avoidance|safe exit",
    re.IGNORECASE,
)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def u16(raw: bytes, off: int) -> int:
    return struct.unpack_from("<H", raw, off)[0]


def u32(raw: bytes, off: int) -> int:
    return struct.unpack_from("<I", raw, off)[0]


def active_row(table: int, record: int, raw: bytes, strings: Any, source: str) -> dict[str, Any]:
    name = strings.get_string(u32(raw, ACTIVE_LAYOUTS[table]["name_offset"]))
    out: dict[str, Any] = {
        "source": source,
        "table": table,
        "record": record,
        "name": name,
    }
    if table == 11:
        out["legacy_primary_key"] = raw[0x52]
        out["legacy_secondary_key"] = u16(raw, 0x38)
    elif table == 68:
        out["active_test_id"] = u16(raw, 0x20)
    else:
        out["routine_id"] = u16(raw, 0x1C)
        out["active_test_id"] = u16(raw, 0x1E)
    return out


def selected_monitors(parser: DDBParser, root: Path) -> dict[str, Any]:
    db_root = root / "NA/DB/Gen"
    strings = load_string_db(parser, db_root / "M_English.ddb")
    targets = {
        "FRC_P5.ddb": re.compile(r"collision avoidance|steer", re.I),
        "PCS2_P5.ddb": re.compile(r"PCS Steering Request|Emergency Steering Assist|Collision Avoidance", re.I),
        "DRS_P5.ddb": re.compile(r"Active Steering Control Permission", re.I),
        "ADCU_P6.ddb": re.compile(r"Active Steering Status", re.I),
        "IPA_P5.ddb": re.compile(r"Advanced Park|Remote Park|Steer-By-Wire|Power Steering", re.I),
    }
    out: dict[str, Any] = {}
    for filename, pattern in targets.items():
        db = parser.parse_ecu_db(db_root / filename)
        rows = [
            {k: v for k, v in row.items() if k != "raw"}
            for row in monitor_rows(db, strings, filename, include_signal_info=True)
            if row.get("name") and pattern.search(row["name"])
        ]
        out[filename] = rows
    return out


def frc_collision_routine(parser: DDBParser, root: Path) -> dict[str, Any]:
    db_root = root / "NA/DB/Gen"
    strings = load_string_db(parser, db_root / "M_English.ddb")
    db = parser.parse_ecu_db(db_root / "FRC_P5.ddb")
    sec = db.sections[71]
    size = sec.decoded_record_size
    matches = []
    for index in range(sec.header.record_count):
        raw = sec.decoded_data[index * size:(index + 1) * size]
        row = active_row(71, index, raw, strings, "FRC_P5.ddb")
        if row["name"] == "PCS Collision Avoidance Assist":
            row.update({
                "start_request": f"3101{row['routine_id']:04X}",
                "stop_request": f"3102{row['routine_id']:04X}",
                "result_request": f"3103{row['routine_id']:04X}",
                "fixed_request": True,
                "raw": raw.hex(),
            })
            matches.append(row)
    if len(matches) != 1:
        raise ValueError(f"expected one FRC PCS Collision Avoidance Assist routine, got {len(matches)}")
    return matches[0]


def airbag_ddr_steering(parser: DDBParser, root: Path) -> list[dict[str, Any]]:
    """Extract exact named DDR monitor rows from the Camry-installed SRS DB.

    Current CDbDDRMonitorResRecords::SetRecString consumes raw+0x14 as the
    monitor-name string index; that host fact is independently pinned by the
    current factory/host audit.
    """
    db_root = root / "NA/DB/Gen"
    strings = load_string_db(parser, db_root / "M_English.ddb")
    db = parser.parse_ecu_db(db_root / "A_B_CAN_P5.ddb")
    wanted = re.compile(r"Emergency Steering Assist Request Flag|Collision Avoidance Assist(?: [123])?$", re.I)
    out = []
    for table in (110, 129, 138, 147):
        sec = db.sections[table]
        size = sec.decoded_record_size
        if size != 48:
            raise ValueError(f"A_B_CAN_P5 table {table}: expected 48-byte DDR monitor rows, got {size}")
        for index in range(sec.header.record_count):
            raw = sec.decoded_data[index * size:(index + 1) * size]
            name = strings.get_string(u32(raw, 0x14))
            if name and wanted.search(name):
                out.append({
                    "table": table,
                    "class_name": ECU_TABLE_CLASS_NAMES[table],
                    "record": index,
                    "name": name,
                    "name_string_index": u32(raw, 0x14),
                    "raw": raw.hex(),
                })
    return out


def psc_factor_data(parser: DDBParser, root: Path) -> dict[str, Any]:
    db_root = root / "NA/DB/Gen"
    strings = load_string_db(parser, db_root / "M_English.ddb")
    db = parser.parse_ecu_db(db_root / "PSC_P5.ddb")
    sec = db.sections[118]
    size = sec.decoded_record_size
    if size != 20:
        raise ValueError(f"PSC_P5 type 118 expected 20-byte rows, got {size}")
    wanted = {
        "History of no IG on in 49 Days",
        "Operated emergency start-up",
        "Started up vehicle by remote engine starter",
        "Stop Start-up (Steering Lock)",
        "Stop Start-up (Release Brake Pedal)",
    }
    rows = []
    groups = Counter()
    for index in range(sec.header.record_count):
        raw = sec.decoded_data[index * size:(index + 1) * size]
        short = strings.get_string(u32(raw, 0x00))
        help_text = strings.get_string(u32(raw, 0x04))
        key = u32(raw, 0x08)
        group = u16(raw, 0x0C)
        groups[group] += 1
        if short in wanted:
            rows.append({
                "record": index,
                "factor": short,
                "help": help_text,
                "key_u32": key,
                "group_u16": group,
                "raw": raw.hex(),
            })
    return {
        "class_name": ECU_TABLE_CLASS_NAMES[118],
        "record_count": sec.header.record_count,
        "record_size": size,
        "group_counts": {str(k): v for k, v in sorted(groups.items())},
        "selected_rows": rows,
        "host_consumer": "GetRoBP5_DT.dll imports CDbFactorDataResRecords::GetFactorData/GetFactorHelp",
    }


def req_limit_eps_boundary(parser: DDBParser, root: Path) -> dict[str, Any]:
    """Pin the shared-string/DID collision that caused a false P5 inference.

    The numeric namespace is *not* typed: a 16-bit DID/data-id may equal a
    string-table index.  CDbDataIdForDmResRecords::SetRecString is a no-op and
    FindDbItem1 consumes +0x02 as u16, so raw integer equality is not a string
    reference.  We keep concrete witnesses here because this exact trap is easy
    to reproduce when grepping the corpus.
    """
    db_root = root / "NA/DB/Gen"
    strings = load_string_db(parser, db_root / "M_English.ddb")
    wanted = {
        "Req Limit EPS 1 - Low Vol",
        "Req Limit EPS 2 - Low Vol",
        "Req Limit EPS 2 - Failure",
        "Req Limit EPS - Air Sus ON",
        "Req Limit EPS 3 - Low Vol",
    }
    entries = []
    by_text: dict[str, int] = {}
    for index in range(strings.entry_count):
        text = strings.get_string(index)
        if text in wanted:
            entries.append({"string_index": index, "text": text})
            by_text[text] = index

    witnesses = []
    for database, text in (
        ("EMPS_P5.ddb", "Req Limit EPS 2 - Low Vol"),
        ("HV_P5.ddb", "Req Limit EPS 1 - Low Vol"),
    ):
        data_id = by_text[text]
        db = parser.parse_ecu_db(db_root / database)
        sec = db.sections[61]
        size = sec.decoded_record_size
        matches = []
        for record in range(sec.header.record_count):
            raw = sec.decoded_data[record * size:(record + 1) * size]
            if u16(raw, 0x02) == data_id:
                matches.append({"record": record, "raw": raw.hex()})
        monitors = [
            {k: v for k, v in row.items() if k not in {"raw", "signal_info"}}
            for row in monitor_rows(db, strings, database, deduplicate=False)
            if row["alternate_did"] == data_id
        ]
        witnesses.append({
            "database": database,
            "numeric_value": data_id,
            "same_number_string": text,
            "type61_data_id_records": matches,
            "type62_monitors_with_same_alternate_did": monitors,
        })

    return {
        "global_string_entries": sorted(entries, key=lambda row: row["string_index"]),
        "collision_witnesses": witnesses,
        "host_boundary": {
            "table61_class": "CDbDataIdForDmTable",
            "record_size": 8,
            "lookup_field": "u16 +0x02",
            "set_rec_string": "no-op (returns zero without consuming CDbStringTable)",
            "meaning": (
                "numeric equality between a type-61 data-id/DID and an M_English "
                "string index is not a semantic string reference"
            ),
        },
    }




def _format_corpus(root: Path, ds4: bool) -> dict[str, Any]:
    """Decode every input; retain compact geometry and selection-contract rows."""
    parser = DDBParser()
    native = _supplemental_sources(root, ds4)
    factories = {
        f["format_version"]: (source["artifact"], f)
        for source in native.values() for f in source["factories"]
    }
    inputs: list[dict[str, Any]] = []
    formats: Counter[int] = Counter()
    groups: Counter[str] = Counter()
    section_count = fixed_rows = variable_sections = string_entries = metadata_entries = 0
    for product in (("DM", "OS") if ds4 else REGIONS):
        for family in FAMILIES:
            for path in sorted((root / product / "DB" / family).glob("*.ddb")):
                data = path.read_bytes()
                version = data[8]
                if not ds4 and version in (1, 2):
                    continue
                row = {
                    "id": path.relative_to(root).as_posix(),
                    "path": path.relative_to(REPO_ROOT).as_posix(),
                    "product": "DS-4" if ds4 else "GTSPlus", "region": product, "family": family,
                    "sha256": hashlib.sha256(data).hexdigest(), "size": len(data),
                    "header8": data[:8].hex(), "format_version": version,
                }
                formats[version] += 1
                groups[f"{product}/{family}"] += 1
                if version in (1, 2, 3):
                    parse = {1: parser.parse_master_db, 2: parser.parse_ecu_db,
                             3: parser.parse_viewer_db}[version]
                    db = parse(path)
                    source, factory = factories[version]
                    cases = {r["table_type"]: r for r in factory["records"]}
                    sections = []
                    for table, section in db.sections.items():
                        decoded = section.decoded_data
                        item = {
                            "table_type": table, "data_offset": section.data_offset,
                            "compression": section.header.compression,
                            "record_count": section.header.record_count,
                            "disk_payload_size": section.header.payload_size,
                            "decoded_size": len(decoded),
                            "decoded_sha256": hashlib.sha256(decoded).hexdigest(),
                            "native_source_sha256": source["sha256"],
                            "native_factory_va": factory["factory_va"],
                            "native_factory_case": cases[table],
                        }
                        if section.variable_layout:
                            section.variable_records()
                            variable_sections += 1
                            item.update({
                                "layout": "u32-pool-offset/u16-byte-length",
                                "pool_offset": section.header.record_count * 6,
                                "offset_directory_sha256": hashlib.sha256(
                                    decoded[:section.header.record_count * 6]
                                ).hexdigest(),
                            })
                        else:
                            size = section.decoded_record_size
                            fixed_rows += section.header.record_count
                            item.update({"record_size": size, "layout": "fixed"})
                            if version == 1 and table in (16, 19):
                                item["raw_rows"] = [
                                    decoded[i * size:(i + 1) * size].hex()
                                    for i in range(section.header.record_count)
                                ]
                        sections.append(item)
                    row["sections"] = sections
                    if version in (1, 2):
                        section_count += len(sections)
                elif version in (4, 5, 6):
                    db = parser.load_string_db(path)
                    source, factory = factories[version]
                    cases = {r["table_type"]: r for r in factory["records"]}
                    string_entries += db.entry_count
                    metadata_entries += len(db.metadata or ())
                    row["strings"] = {
                        "entry_count": db.entry_count, "pool_offset": db.pool_offset,
                        "metadata_count": len(db.metadata or ()),
                        "sections": [{
                            "table_type": table, "data_offset": section.data_offset,
                            "record_count": section.header.record_count,
                            "compression": section.header.compression,
                            "disk_payload_size": section.header.payload_size,
                            "layout": "u32-pool-offset/u16-byte-length" if table == 0 else "fixed",
                            "record_size": None if table == 0 else 164,
                            "decoded_size": len(section.decoded_data),
                            "decoded_sha256": hashlib.sha256(section.decoded_data).hexdigest(),
                            "native_source_sha256": source["sha256"],
                            "native_factory_va": factory["factory_va"],
                            "native_factory_case": cases[table],
                        } for table, section in db.sections.items()],
                        "layout": "u32-pool-offset/u16-byte-length; UTF-16LE byte pool",
                        "metadata_layout": "80-byte key;80-byte secondary key;u32 text index" if db.metadata is not None else None,
                    }
                else:
                    raise ValueError(f"unimplemented database format {version}: {path}")
                row["schema_family"] = db.schema_family
                inputs.append(row)
    return {
        "source_root": root.relative_to(REPO_ROOT).as_posix(),
        "native_sources": native,
        "counts": {
            "ddb_files": len(inputs),
            "formats": {str(k): v for k, v in sorted(formats.items())},
            "groups": dict(sorted(groups.items())),
            "sectioned_files": formats[1] + formats[2],
            "section_instances": section_count,
            "viewer_section_instances": sum(len(r["sections"]) for r in inputs if r["format_version"] == 3),
            "fixed_raw_rows_including_viewer": fixed_rows,
            "variable_sections": variable_sections,
            "string_entries": string_entries, "metadata_entries": metadata_entries,
        },
        "inputs": inputs,
    }

def _master_corpus(root: Path) -> dict[str, Any]:
    parser = DDBParser()
    native_path = root / "bin/KgpDataCtrl.dll"
    native_hash = sha256_file(native_path)
    native = pefile.PE(str(native_path))
    factory = extract_factory(native, FACTORIES[0])
    cases = {r["table_type"]: r for r in factory["records"]}
    inputs: list[dict[str, Any]] = []
    for region in REGIONS:
        for family in FAMILIES:
            path = root / region / "DB" / family / "Toyota.ddb"
            data = path.read_bytes()
            db = parser.parse_master_db(path)
            sections = []
            for table, section in db.sections.items():
                decoded = section.decoded_data
                if section.variable_layout:
                    section.variable_records()
                sections.append({
                    "table_type": table, "data_offset": section.data_offset,
                    "compression": section.header.compression,
                    "record_count": section.header.record_count,
                    "record_size": None if section.variable_layout else section.decoded_record_size,
                    "layout": "u32-pool-offset/u16-byte-length" if section.variable_layout else "fixed",
                    "disk_payload_size": section.header.payload_size,
                    "decoded_size": len(decoded),
                    "decoded_sha256": hashlib.sha256(decoded).hexdigest(),
                    "native_source_sha256": native_hash,
                    "native_factory_va": factory["factory_va"],
                    "native_factory_case": cases[table],
                })
                if table in (16, 19):
                    size = section.decoded_record_size
                    sections[-1]["raw_rows"] = [
                        decoded[i * size:(i + 1) * size].hex()
                        for i in range(section.header.record_count)
                    ]
            inputs.append({
                "id": path.relative_to(root).as_posix(),
                "path": path.relative_to(REPO_ROOT).as_posix(),
                "product": "GTSPlus", "region": region, "family": family,
                "sha256": hashlib.sha256(data).hexdigest(), "size": len(data),
                "header8": data[:8].hex(), "format_version": 1,
                "schema_family": db.schema_family, "sections": sections,
            })
    return {
        "counts": {
            "ddb_files": len(inputs),
            "section_instances": sum(len(r["sections"]) for r in inputs),
            "declared_records": sum(s["record_count"] for r in inputs for s in r["sections"]),
            "variable_sections": sum(s["record_size"] is None for r in inputs for s in r["sections"]),
        },
        "inputs": inputs,
    }



def build(root: Path | None = None) -> dict[str, Any]:
    root = (root or resolve_gts_root()).resolve()
    parser = DDBParser()
    total_files = 0
    ecu_count = 0
    regions: dict[str, Any] = {}
    table_files: Counter[int] = Counter()
    table_records: Counter[int] = Counter()
    table_sizes: dict[int, Counter[int]] = defaultdict(Counter)
    table_samples: dict[int, list[str]] = defaultdict(list)
    active_counts: Counter[int] = Counter()
    active_names: set[str] = set()
    control_rows: dict[tuple[Any, ...], dict[str, Any]] = {}

    for region in REGIONS:
        region_total = region_ecu = 0
        family_rows = {}
        for family in FAMILIES:
            db_root = root / region / "DB" / family
            paths = sorted(db_root.glob("*.ddb"))
            # Spe masters/ECU DBs share the region's Gen string database; Spe
            # does not carry its own M_English.ddb in the current release.
            string_path = db_root / "M_English.ddb"
            if not string_path.is_file():
                string_path = root / region / "DB/Gen/M_English.ddb"
            strings = load_string_db(parser, string_path)
            family_ecu = 0
            for path in paths:
                total_files += 1
                region_total += 1
                version = path.read_bytes()[8]
                if version != 2:
                    continue
                db = parser.parse_ecu_db(path)
                family_ecu += 1
                ecu_count += 1
                region_ecu += 1
                for table, sec in db.sections.items():
                    table_files[table] += 1
                    table_records[table] += sec.header.record_count
                    table_sizes[table][sec.decoded_record_size] += 1
                    if len(table_samples[table]) < 6:
                        table_samples[table].append(f"{region}/{family}/{path.name}")
                    layout = ACTIVE_LAYOUTS.get(table)
                    if layout is None:
                        continue
                    if sec.decoded_record_size != layout["record_size"]:
                        raise ValueError(
                            f"{region}/{family}/{path.name} table {table}: "
                            f"expected {layout['record_size']}, got {sec.decoded_record_size}"
                        )
                    size = sec.decoded_record_size
                    for record in range(sec.header.record_count):
                        raw = sec.decoded_data[record * size:(record + 1) * size]
                        row = active_row(table, record, raw, strings, f"{region}/{family}/{path.name}")
                        active_counts[table] += 1
                        if row["name"]:
                            active_names.add(row["name"])
                            if CONTROL_NAME_RE.search(row["name"]):
                                identity = (
                                    path.name,
                                    table,
                                    row.get("active_test_id"),
                                    row.get("routine_id"),
                                    row.get("legacy_primary_key"),
                                    row.get("legacy_secondary_key"),
                                    row["name"],
                                )
                                control_rows.setdefault(identity, row)
            family_rows[family] = {"ddb_files": len(paths), "ecu_databases": family_ecu}
        regions[region] = {
            "ddb_files": region_total,
            "ecu_databases": region_ecu,
            "families": family_rows,
        }

    type_rows = []
    for table in sorted(table_files):
        type_rows.append({
            "table_type": table,
            "class_name": ECU_TABLE_CLASS_NAMES.get(table),
            "file_occurrences": table_files[table],
            "record_count": table_records[table],
            "record_sizes": {str(k): v for k, v in sorted(table_sizes[table].items())},
            "sample_databases": table_samples[table],
        })

    bin_root = root / "bin"
    pe_count = 0
    for path in bin_root.iterdir():
        if not path.is_file():
            continue
        try:
            pefile.PE(str(path), fast_load=True)
            pe_count += 1
        except (pefile.PEFormatError, OSError):
            pass

    kgp = bin_root / "KgpDataCtrl.dll"
    result = {
        "schema": "gtsplus-current-ddb-corpus-census-v1",
        "release": "2026.03.002.02",
        "source": {
            "root": str(root.relative_to(REPO_ROOT)).replace("\\", "/"),
            "kgp_data_ctrl_sha256": sha256_file(kgp),
        },
        "corpus": {
            "ddb_files": total_files,
            "ecu_databases": ecu_count,
            "non_ecu_ddb_files": total_files - ecu_count,
            "regions": regions,
            "host_pe_files": pe_count,
        },
        "table_types": {
            "used_count": len(type_rows),
            "all_named_by_parser": all(row["class_name"] for row in type_rows),
            "rows": type_rows,
        },
        "active_tests": {
            "row_count": sum(active_counts.values()),
            "by_table": {str(k): v for k, v in sorted(active_counts.items())},
            "unique_resolved_name_count": len(active_names),
            "control_name_matches": sorted(
                control_rows.values(),
                key=lambda r: (r["name"].casefold(), r["source"], r["table"]),
            ),
        },
        "current_camry_relevant": {
            "frc_pcs_collision_avoidance_routine": frc_collision_routine(parser, root),
            "selected_monitors": selected_monitors(parser, root),
            "airbag_ddr_steering_control_names": airbag_ddr_steering(parser, root),
            "psc_factor_data": psc_factor_data(parser, root),
        },
        "req_limit_eps_boundary": req_limit_eps_boundary(parser, root),
        "ds4": _format_corpus(root.parent / "DS-4", True),
        "supplemental": _format_corpus(root, False),
        "main_masters": _master_corpus(root),
    }
    # Normalize tuples from shared signal-info helpers so an in-memory rebuild
    # compares byte-for-byte with JSON reloaded from disk.
    return json.loads(json.dumps(result))




def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", type=Path, default=None)
    ap.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = ap.parse_args()
    result = build(args.root)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(
        f"DDBs={result['corpus']['ddb_files']} ECU={result['corpus']['ecu_databases']} "
        f"types={result['table_types']['used_count']} active={result['active_tests']['row_count']}"
    )
    print(f"Wrote {args.output}")


if __name__ == "__main__":
    main()
