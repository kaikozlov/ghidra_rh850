#!/usr/bin/env python3
"""Extract a P4DK4 diagnostic vocabulary template for newer-generation EPS.

``EPS_P4DK4.ddb`` (JP region only) is the richest EPS database in the
Techstream V18 corpus: 45 DTCs, 89 monitors, 85 subfunction definitions.
It represents a newer EPS generation than the NA databases (EPS_CAN_P4DK,
EPS_P4DK3) currently used as the Sienna diagnostic template.

This script produces a standalone vocabulary artifact intended for
**cross-variant** use — specifically as a search template for the Corolla
``8965F1208000`` and other newer-generation Denso RH850 EPS calibrations
where the P4DK4 generation may be a closer match than the NA databases.

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
from datetime import datetime, timezone

from parse_ddb import DDBParser

# ── Constants ─────────────────────────────────────────────────────────────────

REPO_ROOT = Path(__file__).resolve().parents[2]
TECHSTREAM_DB = REPO_ROOT / "Techstream/unpacked/toyota/Toyota Diagnostics/Techstream"

# P4DK4 is JP-only. String DBs are region-independent (same OEM tables).
P4DK4_PATH = "JP/DB/EPS_P4DK4.ddb"
STRING_DBS = ["NA/DB/M_English.ddb", "NA/DB/V_English.ddb"]

# The monitor→DID bridge: monitor record field at offset 56 ("seq") maps to
# UDS DIDs via DID = 0x0100 + seq (recovered from correlate_vocabulary.py).
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


def extract_dids(db):
    entries = []
    sec = db.sections[3]
    rec_size = 8
    for i in range(sec.header.record_count):
        raw = sec.raw_data[i * rec_size:(i + 1) * rec_size]
        did = struct.unpack_from("<H", raw, 4)[0]
        entries.append({"kind": "did", "identifier": did, "record_index": i})
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

        bridged_did = MONITOR_BRIDGE_BASE + seq if seq < 100 else None

        entries.append({
            "kind": "monitor",
            "record_index": i,
            "seq": seq,
            "bridged_did": f"0x{bridged_did:04X}" if bridged_did else None,
            "name_string_index": name_idx,
            "resolved_name": name or None,
            "resolved_desc": desc or None,
            "scaling_raw": [struct.unpack_from("<H", raw, j)[0] for j in range(0, 24, 2)],
        })
    return entries


def extract_subfunctions(db):
    """Extract section 6 subfunction definitions.

    Each 8-byte record appears to encode a subfunction ID (byte 2) and
    a count/type field (byte 3). The structure is not fully decoded;
    we record raw bytes for structural comparison.
    """
    entries = []
    sec = db.sections[6]
    rec_size = 8
    for i in range(sec.header.record_count):
        raw = sec.raw_data[i * rec_size:(i + 1) * rec_size]
        entries.append({
            "kind": "subfunction",
            "record_index": i,
            "raw_hex": raw.hex(),
        })
    return entries


def main() -> None:
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
    dids = extract_dids(db)
    monitors = extract_monitors(db, dbs["M_English"])
    subfns = extract_subfunctions(db)

    # Build the bridged monitor summary (seq < 100 → DID)
    bridged = [
        {"seq": m["seq"], "did": m["bridged_did"], "name": m["resolved_name"]}
        for m in monitors
        if m["bridged_did"]
    ]

    # Unique DIDs from bridged monitors
    bridged_dids = sorted({int(m["bridged_did"], 16) for m in monitors if m["bridged_did"]})

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
            "P4DK4 EPS diagnostic vocabulary template for newer-generation "
            "Denso RH850 EPS calibrations (e.g. Corolla 8965F1208000). "
            "Not firmware-correlated; pure OEM vocabulary extraction."
        ),
        "techstream_distribution": "V18.00.008",
        "source_file": P4DK4_PATH,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "summary": {
            "dtcs": len(dtcs_deduped),
            "unique_dtc_identifiers": len({d["dtc_identifier"] for d in dtcs_deduped}),
            "dids": len({d["identifier"] for d in dids}),
            "monitors": len(monitors),
            "bridged_monitors": len(bridged),
            "bridged_did_count": len(bridged_dids),
            "subfunctions": len(subfns),
        },
        "string_databases": {
            name: {
                "entry_count": db_sdb.entry_count,
                "decompressed_size": len(db_sdb.decompressed),
            }
            for name, db_sdb in dbs.items()
        },
        "bridged_monitors": bridged,
        "dtcs": dtcs_deduped,
        "dids": sorted({d["identifier"] for d in dids}),
        "monitors": monitors,
        "subfunctions": subfns,
    }

    out_dir = REPO_ROOT / "data" / "generated" / "p4dk4_template"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "p4dk4_vocabulary.json"

    out_path.write_text(json.dumps(catalog, indent=2, ensure_ascii=False))
    print(f"Wrote {out_path}")
    print(f"  DTCs: {catalog['summary']['dtcs']} ({catalog['summary']['unique_dtc_identifiers']} unique IDs)")
    print(f"  DIDs: {catalog['summary']['dids']}")
    print(f"  Monitors: {catalog['summary']['monitors']} ({catalog['summary']['bridged_monitors']} bridged to DIDs)")
    print(f"  Subfunctions: {catalog['summary']['subfunctions']}")


if __name__ == "__main__":
    main()
