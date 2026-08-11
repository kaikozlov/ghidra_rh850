#!/usr/bin/env python3
"""Extract P4DK4 diagnostic vocabulary for cross-variant EPS analysis.

``EPS_P4DK4.ddb`` (JP region only) is the richest EPS database in the
Techstream V18 corpus: 26 unique DTCs (45 records with dual naming),
89 monitors, and 85 raw ``CDbPidTable`` records. It is a JP-market diagnostic
variant with 85 raw ``CDbPidTable`` rows, not a later release — the
Techstream V18.00.003 distribution
(December 2022) predates both the 2023 Sienna and the 2025 Corolla.

This script produces a standalone vocabulary artifact for cross-variant
use — its 13 extra seq-derived candidate firmware-DID bridges (relative to the
NA database) cover EPS state variables that give the correlation engine more
matches to test when new firmware arrives. They are not ``CDbDidTable`` rows.

The artifact is NOT Sienna-specific (no firmware DID-table correlation).
It is a pure OEM vocabulary extraction, analogous to what
``extract_catalog.py`` produces before the firmware correlation step.

Usage::

    uv run python tools/techstream/extract_p4dk4_catalog.py

Output: ``data/generated/p4dk4_template/p4dk4_vocabulary.json``
"""

from __future__ import annotations

import json
import struct
from pathlib import Path

from parse_ddb import DDBParser

# ── Constants ─────────────────────────────────────────────────────────────────

REPO_ROOT = Path(__file__).resolve().parents[2]
TECHSTREAM_DB = REPO_ROOT / "Techstream/unpacked/toyota/Toyota Diagnostics/Techstream"

# P4DK4 is JP-only. String DBs are region-independent (same OEM tables).
P4DK4_PATH = "JP/DB/EPS_P4DK4.ddb"
STRING_DBS = ["NA/DB/M_English.ddb", "NA/DB/V_English.ddb"]

# Structural monitor→firmware-DID candidate used by correlate_vocabulary.py:
# monitor field offset 56 ("seq") yields candidate DID = 0x0100 + seq.  This
# is not a CDbDidTable identity and requires independent firmware evidence.
MONITOR_SEQ_OFFSET = 56
MONITOR_BRIDGE_BASE = 0x0100


# ── Extraction ────────────────────────────────────────────────────────────────

def extract_dtcs(db, strings_m, strings_v):
    entries = []
    sec = db.sections[5]
    rec_size = 28
    for i in range(sec.header.record_count):
        raw = sec.raw_data[i * rec_size:(i + 1) * rec_size]
        code = raw[0:12].decode("utf-16-le", errors="replace").rstrip("\x00")
        name_idx = struct.unpack_from("<I", raw, 12)[0]
        dtc_id = struct.unpack_from("<H", raw, 20)[0]
        entries.append({
            "kind": "dtc",
            "code": code,
            "dtc_identifier": dtc_id,
            "name_string_index": name_idx,
            "resolved_name": strings_m.get_string(name_idx),
        })
    return entries


def extract_supported_pid_records(db):
    """Preserve section-3 CDbSupPidTable rows as bounded raw records."""
    entries = []
    sec = db.sections[3]
    for i, raw in enumerate(DDBParser.extract_supported_pid_records(sec)):
        entries.append({
            "kind": "supported_pid_record",
            "record_index": i,
            "raw_hex": raw.hex(),
            "support_key_hex": raw[4:6].hex(),
        })
    return entries


def extract_monitors(db, strings_m):
    entries = []
    sec = db.sections[10]
    rec_sz = int(sec.record_size)
    for i in range(sec.header.record_count):
        raw = sec.raw_data[i * rec_sz:(i + 1) * rec_sz]
        seq = struct.unpack_from("<I", raw, MONITOR_SEQ_OFFSET)[0]
        name_idx = struct.unpack_from("<I", raw, 48)[0]
        desc_idx = struct.unpack_from("<I", raw, 52)[0]
        name = strings_m.get_string(name_idx) or ""
        desc = strings_m.get_string(desc_idx) or ""

        candidate_did = MONITOR_BRIDGE_BASE + seq if seq < 100 else None

        entries.append({
            "kind": "monitor",
            "source_table_class": "CDbFreezeTable",
            "record_index": i,
            "seq": seq,
            "candidate_firmware_did": (
                f"0x{candidate_did:04X}" if candidate_did else None
            ),
            "name_string_index": name_idx,
            "resolved_name": name or None,
            "resolved_desc": desc or None,
            "scaling_raw": [struct.unpack_from("<H", raw, j)[0] for j in range(0, 24, 2)],
        })
    return entries


def extract_pid_records(db):
    """Extract raw section-6 ``CDbPidTable`` records.

    The structure is not fully decoded; preserve raw bytes for structural
    comparison without the former unsupported "subfunction" interpretation.
    """
    entries = []
    sec = db.sections[6]
    rec_size = 8
    for i in range(sec.header.record_count):
        raw = sec.raw_data[i * rec_size:(i + 1) * rec_size]
        entries.append({
            "kind": "pid_record",
            "record_index": i,
            "raw_hex": raw.hex(),
        })
    return entries


def build_p4dk4_catalog() -> dict:
    parser = DDBParser()

    # Load string databases
    dbs = {}
    for sdb_path in STRING_DBS:
        name = Path(sdb_path).stem
        dbs[name] = parser.load_string_db(TECHSTREAM_DB / sdb_path)

    # Parse P4DK4
    db = parser.parse_ecu_db(TECHSTREAM_DB / P4DK4_PATH)

    # Extract all record types
    dtcs = extract_dtcs(db, dbs["M_English"], dbs.get("V_English"))
    supported_pid_records = extract_supported_pid_records(db)
    monitors = extract_monitors(db, dbs["M_English"])
    pid_records = extract_pid_records(db)

    # Build the structural candidate summary (seq < 100 → firmware DID label).
    bridged = [
        {
            "seq": m["seq"],
            "candidate_firmware_did": m["candidate_firmware_did"],
            "name": m["resolved_name"],
        }
        for m in monitors
        if m["candidate_firmware_did"]
    ]

    candidate_dids = sorted({
        int(m["candidate_firmware_did"], 16)
        for m in monitors
        if m["candidate_firmware_did"]
    })

    # Deduplicate DTCs by (code, identifier), merging alternate name strings.
    # P4DK4 carries dual naming for most DTCs: a formal name and a short/
    # alternate name, sharing the same (code, identifier). Both are kept.
    dtc_groups: dict[tuple[str, int], list[dict]] = {}
    for d in dtcs:
        key = (d["code"], d["dtc_identifier"])
        dtc_groups.setdefault(key, []).append(d)

    dtcs_deduped = []
    for key in sorted(dtc_groups):
        group = dtc_groups[key]
        merged = dict(group[0])
        names = [g["resolved_name"] for g in group if g.get("resolved_name")]
        if len(names) > 1:
            merged["resolved_name"] = names[0]
            merged["alternate_names"] = names[1:]
        dtcs_deduped.append(merged)

    catalog = {
        "description": (
            "P4DK4 EPS diagnostic vocabulary from a co-shipped Techstream V18 "
            "database. Not firmware-correlated and not evidence that the "
            "database targets a newer EPS generation. Seq-derived candidate "
            "firmware-DID labels are structural and are not CDbDidTable rows."
        ),
        "techstream_distribution": "V18.00.003",
        "source_file": P4DK4_PATH,
        "summary": {
            "dtcs": len(dtcs_deduped),
            "unique_dtc_identifiers": len({d["dtc_identifier"] for d in dtcs_deduped}),
            "supported_pid_records": len(supported_pid_records),
            "monitors": len(monitors),
            "structural_monitor_bridges": len(bridged),
            "candidate_firmware_did_count": len(candidate_dids),
            "pid_records": len(pid_records),
        },
        "string_databases": {
            name: {
                "entry_count": db_sdb.entry_count,
                "decompressed_size": len(db_sdb.decompressed),
            }
            for name, db_sdb in dbs.items()
        },
        "structural_monitor_bridges": bridged,
        "dtcs": dtcs_deduped,
        "supported_pid_records": supported_pid_records,
        "monitors": monitors,
        "pid_records": pid_records,
    }
    return catalog


def main() -> None:
    catalog = build_p4dk4_catalog()

    out_dir = REPO_ROOT / "data" / "generated" / "p4dk4_template"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "p4dk4_vocabulary.json"

    out_path.write_text(json.dumps(catalog, indent=2, ensure_ascii=False))
    print(f"Wrote {out_path}")
    print(f"  DTCs: {catalog['summary']['dtcs']} ({catalog['summary']['unique_dtc_identifiers']} unique IDs)")
    print(f"  Supported-PID records: {catalog['summary']['supported_pid_records']}")
    print(
        f"  Monitors: {catalog['summary']['monitors']} "
        f"({catalog['summary']['structural_monitor_bridges']} structural "
        "firmware-DID candidates)"
    )
    print(f"  PID records: {catalog['summary']['pid_records']}")


if __name__ == "__main__":
    main()
