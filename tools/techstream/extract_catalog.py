#!/usr/bin/env python3
"""Extract an OEM diagnostic catalog from Techstream .ddb files.

Produces ``diagnostic_annotations.json`` — a generated artifact that
correlates Techstream diagnostic vocabulary with firmware identifiers.

The catalog is the first layer of the annotation pipeline described in
``docs/tooling/techstream-ddb-pipeline.md``::

    Techstream .ddb → extract_catalog.py → diagnostic_annotations.json
                                                        ↓
                                       ApplyDiagnosticVocabulary.java
                                                        ↓
                                           annotated Ghidra project

Usage::

    uv run python tools/techstream/extract_catalog.py

Output: ``data/generated/<firmware-sha>/diagnostic_annotations.json``
"""

from __future__ import annotations

import json
import struct
import hashlib
from pathlib import Path
from datetime import datetime, timezone

from parse_ddb import DDBParser, ECUDataBase, StringDataBase

# ── Constants ─────────────────────────────────────────────────────────────────

REPO_ROOT = Path(__file__).resolve().parents[2]
TECHSTREAM_DB = REPO_ROOT / "Techstream/unpacked/toyota/Toyota Diagnostics/Techstream/NA/DB"

CODEFLASH_SHA256 = (
    "21140bbd65e530a9e518a3e84e20e5d85679675bc09cc724cb177bb7c76bafde"
)

# Firmware DID table (from AnnotateApplicationDiagnostics.java)
FW_DID_TABLE_BASE = 0x2941C
FW_DID_TABLE_COUNT = 242  # 0xF2
FW_DID_RANGE_START = 0x0100
FW_DID_RANGE_END = 0xF18C

# EPS .ddb files to process (DS2/KWP and UDS/CAN variants)
EPS_DDB_FILES = ["EPS_P4DK3.ddb", "EPS_CAN_P4DK.ddb"]

# M_English.ddb is the OEM description string database (DTC names, monitor
# names, etc.).  V_English.ddb is the UI/active-test description database.
# String indices in DTC records resolve to M_English, not V_English.
STRING_DB_FILE = "M_English.ddb"


# ── Extractors ────────────────────────────────────────────────────────────────

def extract_dtcs(
    db: ECUDataBase, veng: StringDataBase
) -> list[dict]:
    """Extract DTC records from section type 5.

    Each 28-byte record: [12B UTF-16LE code][u32 name_idx][u32 0][u16 dtc_id]
    """
    entries = []
    if 5 not in db.sections:
        return entries
    sec = db.sections[5]
    rec_size = 28
    for i in range(sec.header.record_count):
        raw = sec.raw_data[i * rec_size : (i + 1) * rec_size]
        code = raw[0:12].decode("utf-16-le", errors="replace").rstrip("\x00")
        name_idx = struct.unpack_from("<I", raw, 12)[0]
        dtc_id = struct.unpack_from("<H", raw, 20)[0]
        name = veng.get_string(name_idx)
        entries.append(
            {
                "kind": "dtc",
                "code": code,
                "dtc_identifier": dtc_id,
                "name_string_index": name_idx,
                "resolved_name": name,
                "source_db": db.name,
            }
        )
    return entries


def extract_dids(db: ECUDataBase) -> list[dict]:
    """Extract DID identifiers from section type 3 (8-byte records)."""
    entries = []
    if 3 not in db.sections:
        return entries
    sec = db.sections[3]
    rec_size = 8
    for i in range(sec.header.record_count):
        raw = sec.raw_data[i * rec_size : (i + 1) * rec_size]
        did = struct.unpack_from("<H", raw, 4)[0]
        in_firmware = FW_DID_RANGE_START <= did <= FW_DID_RANGE_END
        entries.append(
            {
                "kind": "did",
                "identifier": did,
                "in_firmware_table": in_firmware,
                "source_db": db.name,
            }
        )
    return entries


def extract_monitors(
    db: ECUDataBase, veng: StringDataBase
) -> list[dict]:
    """Extract data monitor records from section type 10 (84-byte records).

    Each record has name/description string indices at offsets 48 and 52.
    """
    entries = []
    if 10 not in db.sections:
        return entries
    sec = db.sections[10]
    rec_size = int(sec.record_size)
    for i in range(sec.header.record_count):
        raw = sec.raw_data[i * rec_size : (i + 1) * rec_size]
        name_idx = struct.unpack_from("<H", raw, 48)[0]
        desc_idx = struct.unpack_from("<H", raw, 52)[0]
        name = veng.get_string(name_idx)
        desc = veng.get_string(desc_idx)
        # Scaling/min/max fields from the first 24 bytes
        scaling = [struct.unpack_from("<H", raw, j)[0] for j in range(0, 24, 2)]
        entries.append(
            {
                "kind": "monitor",
                "record_index": i,
                "name_string_index": name_idx,
                "resolved_name": name,
                "desc_string_index": desc_idx,
                "resolved_desc": desc,
                "scaling_raw": scaling,
                "source_db": db.name,
            }
        )
    return entries


def extract_active_tests(
    db: ECUDataBase, veng: StringDataBase
) -> list[dict]:
    """Extract active test/routine records from section type 14 (24-byte records)."""
    entries = []
    if 14 not in db.sections:
        return entries
    sec = db.sections[14]
    rec_size = 24
    for i in range(sec.header.record_count):
        raw = sec.raw_data[i * rec_size : (i + 1) * rec_size]
        name_idx = struct.unpack_from("<H", raw, 0)[0]
        subfunc = struct.unpack_from("<H", raw, 4)[0]
        name = veng.get_string(name_idx)
        entries.append(
            {
                "kind": "active_test",
                "record_index": i,
                "name_string_index": name_idx,
                "resolved_name": name,
                "subfunction": subfunc,
                "source_db": db.name,
            }
        )
    return entries


# ── Main ──────────────────────────────────────────────────────────────────────

def build_catalog() -> dict:
    parser = DDBParser()

    # Load OEM description string database (M_English)
    strings = parser.load_string_db(TECHSTREAM_DB / STRING_DB_FILE)

    # Load all EPS databases
    eps_dbs = []
    for fname in EPS_DDB_FILES:
        path = TECHSTREAM_DB / fname
        if path.exists():
            eps_dbs.append(parser.parse_ecu_db(path))

    entries = []
    for db in eps_dbs:
        entries.extend(extract_dtcs(db, strings))
        entries.extend(extract_dids(db))
        entries.extend(extract_monitors(db, strings))
        entries.extend(extract_active_tests(db, strings))

    # Deduplicate
    seen = set()
    deduped = []
    for e in entries:
        key = (
            e["kind"],
            e.get("code"),
            e.get("identifier"),
            e.get("record_index"),
            e.get("source_db"),
        )
        if key not in seen:
            seen.add(key)
            deduped.append(e)

    # Summarize
    by_kind: dict[str, int] = {}
    for e in deduped:
        by_kind[e["kind"]] = by_kind.get(e["kind"], 0) + 1

    # DIDs that appear in both Techstream and firmware
    firmware_dids = [
        e for e in deduped if e["kind"] == "did" and e.get("in_firmware_table")
    ]

    catalog = {
        "firmware_sha256": CODEFLASH_SHA256,
        "techstream_distribution": "V18.00.008",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "ecu": {
            "family": "EPS",
            "software_id": "8965B4512000",
            "protocol": "P4CAN",
        },
        "source_files": {
            "ecu_databases": [f"NA/DB/{f}" for f in EPS_DDB_FILES],
            "string_database": f"NA/DB/{STRING_DB_FILE}",
        },
        "firmware_did_table": {
            "base": f"0x{FW_DID_TABLE_BASE:X}",
            "count": FW_DID_TABLE_COUNT,
            "range": [f"0x{FW_DID_RANGE_START:04X}", f"0x{FW_DID_RANGE_END:04X}"],
        },
        "summary": {
            "total_entries": len(deduped),
            "by_kind": by_kind,
            "dids_in_firmware": len(firmware_dids),
        },
        "string_database": {
            "file": STRING_DB_FILE,
            "entry_count": strings.entry_count,
            "pool_offset": strings.pool_offset,
            "decompressed_size": len(strings.decompressed),
        },
        "entries": deduped,
    }
    return catalog


def main() -> None:
    catalog = build_catalog()

    out_dir = REPO_ROOT / "data" / "generated" / CODEFLASH_SHA256[:16]
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "diagnostic_annotations.json"

    out_path.write_text(json.dumps(catalog, indent=2, ensure_ascii=False))
    print(f"Wrote {out_path}")
    print(f"  {catalog['summary']['total_entries']} entries")
    for kind, count in sorted(catalog["summary"]["by_kind"].items()):
        print(f"    {kind}: {count}")
    print(f"  DIDs in firmware table: {catalog['summary']['dids_in_firmware']}")


if __name__ == "__main__":
    main()
