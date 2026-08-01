#!/usr/bin/env python3
"""Extract an OEM diagnostic catalog from Techstream .ddb files.

Produces ``diagnostic_annotations.json`` — a generated artifact that
correlates Techstream diagnostic vocabulary with firmware identifiers.

The catalog resolves every string index against ALL three OEM string
databases (M_English, V_English, U_English) and records all resolutions.
The Techstream runtime selects which DB to use per-context; we record all
three so the correlation engine can pick the right one without hardcoding.

Usage::

    uv run python tools/techstream/extract_catalog.py

Output: ``data/generated/<firmware-sha>/diagnostic_annotations.json``
"""

from __future__ import annotations

import json
import re
import struct
import hashlib
from pathlib import Path

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

# All three OEM string databases.  Techstream loads these separately and
# selects per-context at runtime (the DLL is agnostic — it resolves against
# whatever CDbStringTable pointer it's given).  We load all three and resolve
# every index against each, recording all results.
STRING_DBS = ["M_English.ddb", "V_English.ddb", "U_English.ddb"]

# U_English has no structural ECU/procedure linkage. Keep only strings with
# explicit steering anchors. Broad terms such as "initial setting" and the old
# substring search for "eps" pulled unrelated text (including "steps").
EPS_UTILITY_PATTERNS = [
    re.compile(pattern, re.IGNORECASE)
    for pattern in (
        r"\btorque sensor\b",
        r"\bpower steering\b",
        r"\belectric power steering\b",
        r"\bsteering torque\b",
        r"\bsteering angle sensor\b",
        r"\bassist map\b",
        r"\bEPS\b",
    )
]


# ── Helpers ───────────────────────────────────────────────────────────────────

def resolve_all(
    index: int, dbs: dict[str, StringDataBase]
) -> dict[str, str | None]:
    """Resolve a string index against all loaded DBs."""
    return {name: db.get_string(index) for name, db in dbs.items()}


# ── Extractors ────────────────────────────────────────────────────────────────

def extract_dtcs(
    db: ECUDataBase, dbs: dict[str, StringDataBase]
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
        resolutions = resolve_all(name_idx, dbs)
        entries.append(
            {
                "kind": "dtc",
                "code": code,
                "dtc_identifier": dtc_id,
                "name_string_index": name_idx,
                "resolved_name": resolutions.get("M_English"),
                "resolutions": resolutions,
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
        entries.append(
            {
                "kind": "did",
                "identifier": did,
                "source_db": db.name,
            }
        )
    return entries


def extract_monitors(
    db: ECUDataBase, dbs: dict[str, StringDataBase]
) -> list[dict]:
    """Extract data monitor records from section type 10 (84-byte records).

    String indices at offsets 48 and 52 are u32 (not u16 — indices above
    65535 are valid and appear in this data).
    """
    entries = []
    if 10 not in db.sections:
        return entries
    sec = db.sections[10]
    rec_size = int(sec.record_size)
    for i in range(sec.header.record_count):
        raw = sec.raw_data[i * rec_size : (i + 1) * rec_size]
        name_idx = struct.unpack_from("<I", raw, 48)[0]
        desc_idx = struct.unpack_from("<I", raw, 52)[0]
        monitor_seq = struct.unpack_from("<I", raw, 56)[0]
        name_res = resolve_all(name_idx, dbs)
        desc_res = resolve_all(desc_idx, dbs)
        scaling = [struct.unpack_from("<H", raw, j)[0] for j in range(0, 24, 2)]
        entries.append(
            {
                "kind": "monitor",
                "record_index": i,
                "name_string_index": name_idx,
                "resolved_name": name_res.get("M_English"),
                "name_resolutions": name_res,
                "desc_string_index": desc_idx,
                "resolved_desc": desc_res.get("M_English"),
                "desc_resolutions": desc_res,
                "monitor_seq": monitor_seq,
                "scaling_raw": scaling,
                "source_db": db.name,
            }
        )
    return entries


def extract_utility_strings(
    u_db: StringDataBase,
) -> list[dict]:
    """Extract steering-anchored strings from U_English.

    U_English (format 0x06) contains wizard/dialog text for dealer service
    procedures. Its parallel type-1 section supplies stable resource
    identifiers, but still does not establish ECU ownership or a firmware
    routine binding. These are family-level candidates, not procedure records.
    """
    entries: list[dict] = []
    for idx in range(1, u_db.entry_count + 1):
        text = u_db.get_string(idx)
        if not text:
            continue
        matched = [
            pattern.pattern for pattern in EPS_UTILITY_PATTERNS
            if pattern.search(text)
        ]
        if matched:
            metadata = u_db.get_metadata(idx)
            entries.append({
                "kind": "utility_string",
                "string_index": idx,
                "text": text,
                "matched_patterns": matched,
                "resource_identifier": (
                    metadata.identifier if metadata is not None else None
                ),
                "resource_auxiliary_value": (
                    metadata.auxiliary_value if metadata is not None else None
                ),
            })
    return entries


# ── Main ──────────────────────────────────────────────────────────────────────

def build_catalog() -> dict:
    parser = DDBParser()
    required = [TECHSTREAM_DB / name for name in (*STRING_DBS, *EPS_DDB_FILES)]
    missing = [path for path in required if not path.is_file()]
    if missing:
        names = ", ".join(str(path) for path in missing)
        raise FileNotFoundError(f"required Techstream catalog sources missing: {names}")

    # Load all three string databases
    dbs: dict[str, StringDataBase] = {}
    for fname in STRING_DBS:
        path = TECHSTREAM_DB / fname
        name = fname.replace(".ddb", "")
        dbs[name] = parser.load_string_db(path)

    # Load all EPS databases
    eps_dbs = []
    for fname in EPS_DDB_FILES:
        path = TECHSTREAM_DB / fname
        eps_dbs.append(parser.parse_ecu_db(path))

    entries = []
    for db in eps_dbs:
        entries.extend(extract_dtcs(db, dbs))
        entries.extend(extract_dids(db))
        entries.extend(extract_monitors(db, dbs))

    # Load steering-anchored U_English strings. Resource identifiers group UI
    # strings but do not bind them to this ECU or a firmware routine, so these
    # remain family-level vocabulary only.
    entries.extend(extract_utility_strings(dbs["U_English"]))

    # Deduplicate. DIDs are keyed by identifier alone (same DID across DDB
    # variants is the same diagnostic concept). DTCs and monitors keep
    # source_db in the key since KWP and CAN use different names.
    seen = set()
    deduped = []
    for e in entries:
        if e["kind"] == "did":
            key = (e["kind"], e.get("identifier"))
        else:
            key = (
                e["kind"],
                e.get("code"),
                e.get("identifier"),
                e.get("record_index"),
                e.get("source_db"),
                e.get("string_index"),
            )
        if key not in seen:
            seen.add(key)
            deduped.append(e)

    # Summarize
    by_kind: dict[str, int] = {}
    for e in deduped:
        by_kind[e["kind"]] = by_kind.get(e["kind"], 0) + 1

    catalog = {
        "firmware_sha256": CODEFLASH_SHA256,
        "techstream_distribution": "V18.00.003",
        "ecu": {
            "family": "EPS",
            "software_id": "8965B4512000",
            "protocol": "P4CAN",
        },
        "source_files": {
            "ecu_databases": [f"NA/DB/{f}" for f in EPS_DDB_FILES],
            "string_databases": [f"NA/DB/{f}" for f in STRING_DBS],
        },
        "firmware_did_table": {
            "base": f"0x{FW_DID_TABLE_BASE:X}",
            "count": FW_DID_TABLE_COUNT,
            "range": [f"0x{FW_DID_RANGE_START:04X}", f"0x{FW_DID_RANGE_END:04X}"],
        },
        "summary": {
            "total_entries": len(deduped),
            "by_kind": by_kind,
        },
        "string_databases": {
            name: {
                "file": f"{name}.ddb",
                "entry_count": db.entry_count,
                "pool_offset": db.pool_offset,
                "decompressed_size": len(db.decompressed),
                "metadata_entry_count": (
                    len(db.metadata) if db.metadata is not None else 0
                ),
            }
            for name, db in dbs.items()
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
    print(f"  String DBs loaded: {', '.join(catalog['string_databases'].keys())}")


if __name__ == "__main__":
    main()
