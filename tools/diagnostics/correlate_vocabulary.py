#!/usr/bin/env python3
"""Correlate Techstream OEM vocabulary with firmware diagnostic tables.

Consumes:
    - Techstream catalog from ``tools/techstream/extract_catalog.py``
    - Firmware tables from ``tools/diagnostics/firmware_tables.py``

Produces:
    ``data/generated/<sha>/diagnostic_vocabulary.json`` — an enriched artifact
    that adds OEM names, match grades, and firmware addresses to the raw catalog.

Match grades (aligned with ``docs/status/FINDINGS.md``):

    exact       — identifier exists in both firmware and an EPS database.
                  The firmware proves existence; Techstream supplies the name.
    structural  — identifier + payload/session/service context both match.
    family      — identifier matches an EPS database for the same protocol
                  generation but is not proven calibration-specific.
    candidate   — identifier matches but multiple descriptions conflict.
    rejected    — Techstream constraints contradict firmware evidence.

Only ``exact`` and ``structural`` grades carry OEM names into auto-applied
symbol renames.  ``family`` grades add comment-only annotations.

Architecture::

    Techstream .ddb → extract_catalog.py → diagnostic_annotations.json
                                                        ↓
    firmware bytes  → firmware_tables.py → FirmwareTables
                                                        ↓
                                     correlate_vocabulary.py
                                                        ↓
                                       diagnostic_vocabulary.json
                                                        ↓
                                       ApplyDiagnosticVocabulary.java

Usage::

    uv run python tools/diagnostics/correlate_vocabulary.py
"""

from __future__ import annotations

import json
import hashlib
from pathlib import Path
from datetime import datetime, timezone

# These imports work because the script runs from the repo root and
# tools/techstream is on sys.path via the extract_catalog import chain.
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "techstream"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from firmware_tables import extract_all, FirmwareTables, DidEntry  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[2]
CATALOG_PATH = REPO_ROOT / "data" / "generated" / "21140bbd65e530a9" / "diagnostic_annotations.json"
CODEFLASH_PATH = REPO_ROOT / "firmware" / "RH850_P1M-E_CodeFlash.bin"

# RAM source mapping for monitor-bridged DIDs, recovered by decompiling each
# DID callback (via SeedDidCallbacks.java).  These identify the RAM variable or
# checkpoint object that each monitor reads — the semantic bridge from OEM
# vocabulary to firmware state.
MONITOR_RAM_SOURCES = {
    0x0102: "DAT_FEBEE90C (vehicle_speed_2B), DAT_FEBEE896 (speed_signal_2B), DAT_FEBEE815 (speed_flag_1B)",
    0x0103: "DAT_FEBEE910 (engine_rpm_ptr), DAT_FEBEE814 (rpm_flag_1B); returns 0 when rpm < 100000 (0xF4240)",
    0x0105: "checkpoint_object 0x204 (10B, magic 0xA55A5AA5), descriptor at CodeFlash 0x212F8",
    0x0109: "DAT_FEBEE867..FEBEE86C (6B steering_torque_raw); returns 0xFF fill when invalid (DAT_FEBEE813 != 'Z')",
    0x010B: "checkpoint_object 0x20A (16B, magic 0xA55A5AA5), descriptor at CodeFlash 0x21308",
    0x0110: "FUN_0006909A() result + GP[-0xB99] (FEBEE664); IG_switch_counter arithmetic",
    0x0111: "stub: returns 0 without reading any state",
    0x0112: "DAT_FEBE8AB0 + DAT_FEBE89A4 (diagnostic_code_count arithmetic)",
}


# ── Helpers ───────────────────────────────────────────────────────────────────

def slug(name: str) -> str:
    """Convert an OEM name to a valid symbol suffix (snake_case)."""
    out = []
    prev_under = True
    for ch in name.strip():
        if ch.isalnum():
            out.append(ch.lower())
            prev_under = False
        else:
            if not prev_under:
                out.append("_")
                prev_under = True
    result = "".join(out).strip("_")
    return result or "unnamed"


def firmware_sha256() -> str:
    return hashlib.sha256(CODEFLASH_PATH.read_bytes()).hexdigest()


# ── Correlators ───────────────────────────────────────────────────────────────

def correlate_dids(
    catalog: dict, tables: FirmwareTables
) -> list[dict]:
    """Correlate Techstream DIDs with firmware DID records.

    Only 12 Techstream DIDs exist (4 from EPS_P4DK3, 8 from EPS_CAN_P4DK).
    Each is checked for an exact match in the 242-entry firmware DID table.
    """
    matches = []
    fw_dids = tables.did_by_id
    techstream_dids = [e for e in catalog["entries"] if e["kind"] == "did"]

    for ts_did in techstream_dids:
        did_id = ts_did["identifier"]
        fw = fw_dids.get(did_id)

        if fw is None:
            # DID exists in Techstream but not in firmware — not unusual for
            # a cross-generation database.  Record as family candidate.
            matches.append({
                "kind": "did",
                "identifier": did_id,
                "oem_name": f"DID 0x{did_id:04X} (Techstream only)",
                "match_grade": "family",
                "firmware_table_index": None,
                "firmware_callback": None,
                "firmware_flags": None,
                "source_db": ts_did["source_db"],
                "annotation_action": "comment",
                "note": "DID exists in Techstream EPS database but not in "
                        "the firmware DID table — may be inactive or "
                        "cross-generation.",
            })
            continue

        matches.append({
            "kind": "did",
            "identifier": did_id,
            "oem_name": f"DID 0x{did_id:04X}",
            "match_grade": "exact",
            "firmware_table_index": fw.table_index,
            "firmware_callback": f"0x{fw.callback:05X}",
            "firmware_flags": f"0x{fw.flags:04X}",
            "firmware_table_base": "0x2941C",
            "source_db": ts_did["source_db"],
            "annotation_action": "name_callback" if fw.has_callback else "comment",
            "note": f"Exact DID match. Firmware callback 0x{fw.callback:05X} "
                    f"at table index {fw.table_index}.",
        })

    return matches


def correlate_dtcs(
    catalog: dict, cf: bytes
) -> list[dict]:
    """Correlate Techstream DTCs with firmware byte patterns.

    DTC identifiers are 2-byte values that appear at various offsets in the
    firmware.  We search for their little-endian representation and record
    the offsets as evidence — this is a content-match, not a table lookup.
    """
    import struct

    matches = []
    techstream_dtcs = [e for e in catalog["entries"] if e["kind"] == "dtc"]
    seen_ids: dict[int, list[dict]] = {}

    for ts_dtc in techstream_dtcs:
        dtc_id = ts_dtc["dtc_identifier"]
        if dtc_id == 0:
            continue
        pattern = struct.pack("<H", dtc_id)
        positions = []
        start = 0
        while len(positions) < 10:
            pos = cf.find(pattern, start)
            if pos < 0:
                break
            positions.append(f"0x{pos:05X}")
            start = pos + 1

        grade = "exact" if positions else "family"
        match = {
            "kind": "dtc",
            "code": ts_dtc["code"],
            "dtc_identifier": dtc_id,
            "oem_name": ts_dtc.get("resolved_name", "unknown"),
            "match_grade": grade,
            "firmware_offsets": positions,
            "source_db": ts_dtc["source_db"],
            "annotation_action": "comment",
            "note": (f"DTC {ts_dtc['code']} (0x{dtc_id:04X}) "
                     f"found at {len(positions)} location(s)" if positions else
                     f"DTC {ts_dtc['code']} (0x{dtc_id:04X}) not found in "
                     f"CodeFlash — may be diagnostic-only or cross-generation."),
        }
        seen_ids.setdefault(dtc_id, []).append(match)
        matches.append(match)

    # Detect conflicting descriptions for the same DTC ID
    for dtc_id, entries in seen_ids.items():
        names = {e["oem_name"] for e in entries if e["oem_name"] != "unknown"}
        if len(entries) > 1 and len(names) > 1:
            for e in entries:
                e["match_grade"] = "candidate"
                e["note"] += " Multiple conflicting descriptions across databases."

    return matches


def correlate_monitors(
    catalog: dict, tables: FirmwareTables
) -> list[dict]:
    """Correlate Techstream monitors with firmware DID records.

    The key discovery: monitor record field at offset 56 (the "seq" number)
    maps to firmware DIDs via ``DID = 0x0100 + seq``.  This is not in the
    .ddb section 0/1 lookup tables — those use proprietary PIDs (0x2711+).

    For monitors with seq < 100, DID = 0x0100 + seq hits the firmware DID
    table exactly, giving us OEM names like "Motor Actual Current",
    "Steering Torque", "Thermistor Temperature" for firmware callbacks.

    EPS_CAN_P4DK (the UDS/CAN variant) is authoritative for this firmware's
    DID semantics.  EPS_P4DK3 (the KWP variant) uses different naming — when
    they conflict, we grade as candidate.
    """
    # Build per-DID name sets from each DDB variant by re-reading the raw
    # section 10 records (the catalog doesn't carry the seq number).
    import struct
    from parse_ddb import DDBParser

    DB = REPO_ROOT / "Techstream/unpacked/toyota/Toyota Diagnostics/Techstream/NA/DB"
    parser = DDBParser()
    strings = parser.load_string_db(DB / "M_English.ddb")

    monitor_names_by_did: dict[int, dict[str, list[str]]] = {}
    for fname in ["EPS_CAN_P4DK.ddb", "EPS_P4DK3.ddb"]:
        db = parser.parse_ecu_db(DB / fname)
        if 10 not in db.sections:
            continue
        sec10 = db.sections[10]
        rec_sz = int(sec10.record_size)
        for i in range(sec10.header.record_count):
            raw = sec10.raw_data[i * rec_sz:(i + 1) * rec_sz]
            seq = struct.unpack_from("<I", raw, 56)[0]
            name_idx = struct.unpack_from("<I", raw, 48)[0]
            name = strings.get_string(name_idx)
            if not name or seq >= 100:
                continue
            did = 0x0100 + seq
            monitor_names_by_did.setdefault(did, {}).setdefault(fname, []).append(name)

    fw_dids = tables.did_by_id
    seen_dids: set[int] = set()
    matches: list[dict] = []

    # First: monitors that map to firmware DIDs (the high-value bridge)
    for did, names_by_db in sorted(monitor_names_by_did.items()):
        if did not in fw_dids:
            continue
        seen_dids.add(did)
        fw = fw_dids[did]
        can_names = sorted(set(names_by_db.get("EPS_CAN_P4DK.ddb", [])))
        kwp_names = sorted(set(names_by_db.get("EPS_P4DK3.ddb", [])))

        # CAN variant is authoritative for this UDS firmware
        oem_name = can_names[0] if can_names else (kwp_names[0] if kwp_names else "unnamed")

        # Grade: exact if CAN names agree, candidate if CAN/KWP conflict
        all_can_same = len(can_names) <= 1
        no_kwp_conflict = not kwp_names or set(can_names) == set(kwp_names)
        if all_can_same and no_kwp_conflict:
            grade = "exact"
        elif all_can_same:
            grade = "candidate"
        else:
            grade = "candidate"

        # Attach decompiled RAM source information for the bridged DIDs.
        # Recovered from SeedDidCallbacks.java decompilation of the callbacks.
        ram_source = MONITOR_RAM_SOURCES.get(did)

        match = {
            "kind": "monitor",
            "identifier": did,
            "oem_name": oem_name,
            "oem_symbol": slug(oem_name),
            "match_grade": grade,
            "firmware_table_index": fw.table_index,
            "firmware_callback": f"0x{fw.callback:05X}",
            "firmware_flags": f"0x{fw.flags:04X}",
            "source_db": "EPS_CAN_P4DK" if can_names else "EPS_P4DK3",
            "can_variant_name": can_names[0] if can_names else None,
            "kwp_variant_name": kwp_names[0] if kwp_names else None,
            "annotation_action": "name_callback" if grade == "exact" else "comment",
        }
        if ram_source:
            match["ram_source"] = ram_source
        match["note"] = (
            f"Monitor seq {did - 0x0100} → DID 0x{did:04X}, callback "
            f"0x{fw.callback:05X}. CAN name: '{can_names[0] if can_names else '?'}'"
            + ("'. KWP conflict: '" + kwp_names[0] + "'." if kwp_names and set(can_names) != set(kwp_names) else ".")
            + (" RAM: " + ram_source + "." if ram_source else "")
        )
        matches.append(match)

    # Remaining monitors that don't map to firmware DIDs stay as family vocabulary
    for mon in [e for e in catalog["entries"] if e["kind"] == "monitor"]:
        name = mon.get("resolved_name") or "unnamed"
        matches.append({
            "kind": "monitor",
            "oem_name": name,
            "oem_symbol": slug(name),
            "match_grade": "family",
            "source_db": mon["source_db"],
            "scaling_raw": mon.get("scaling_raw"),
            "annotation_action": "vocabulary",
            "note": (f"Techstream Data List monitor '{name}'. No firmware DID "
                     f"match (seq >= 100 or not in DID table)."),
        })

    return matches


def correlate_active_tests(
    catalog: dict, tables: FirmwareTables
) -> list[dict]:
    """Correlate Techstream active tests with firmware routine/DID tables.

    Active tests map to SID 0x2F InputOutputControlByIdentifier or
    SID 0x31 RoutineControl.  The subfunction field in active-test records
    may correspond to a DID or routine ID in the firmware.
    """
    matches = []
    tests = [e for e in catalog["entries"] if e["kind"] == "active_test"]
    fw_routines = tables.routine_by_id
    fw_dids = tables.did_by_id

    for test in tests:
        name = test.get("resolved_name") or "unnamed"
        subfunc = test.get("subfunction", 0)
        matched_routine = fw_routines.get(subfunc)
        matched_did = fw_dids.get(subfunc)

        if matched_routine:
            grade = "exact"
            action = "name_callback"
            note = (f"Active test '{name}' subfunction 0x{subfunc:04X} matches "
                    f"firmware routine table entry {matched_routine.table_index}.")
            firmware_ref = f"routine_table_index:{matched_routine.table_index}"
        elif matched_did:
            grade = "exact"
            action = "name_callback"
            note = (f"Active test '{name}' subfunction 0x{subfunc:04X} matches "
                    f"firmware DID table entry {matched_did.table_index}.")
            firmware_ref = f"did_table_index:{matched_did.table_index}"
        else:
            grade = "family"
            action = "vocabulary"
            note = (f"Active test '{name}' subfunction 0x{subfunc:04X} has no "
                    f"direct firmware table match.")
            firmware_ref = None

        matches.append({
            "kind": "active_test",
            "oem_name": name,
            "oem_symbol": slug(name),
            "subfunction": subfunc,
            "match_grade": grade,
            "source_db": test["source_db"],
            "firmware_ref": firmware_ref,
            "annotation_action": action,
            "note": note,
        })

    return matches


def correlate_services(
    catalog: dict, tables: FirmwareTables
) -> list[dict]:
    """Attach OEM UDS service names to firmware service records.

    UDS service names are standardized (ISO 14229-1), so this is a known
    vocabulary applied to the firmware's service table.  The value is
    having a single source mapping SID → standard name.
    """
    UDS_SERVICE_NAMES = {
        0x10: "DiagnosticSessionControl",
        0x11: "ECUReset",
        0x14: "ClearDiagnosticInformation",
        0x19: "ReadDTCInformation",
        0x22: "ReadDataByIdentifier",
        0x23: "ReadMemoryByAddress",
        0x27: "SecurityAccess",
        0x28: "CommunicationControl",
        0x2E: "WriteDataByIdentifier",
        0x31: "RoutineControl",
        0x34: "RequestDownload",
        0x36: "TransferData",
        0x37: "RequestTransferExit",
        0x3E: "TesterPresent",
        0x85: "ControlDTCSetting",
        0xAB: "ProprietaryEventRecord",
        0xBA: "ProprietaryService_BA",
    }

    matches = []
    seen_sids: set[int] = set()
    for svc in tables.services:
        # The primary service table (indices 0–16) is authoritative for
        # service-level callbacks.  Extra records (indices 17–22) are shared
        # entries used by functional/secondary groups — skip duplicates.
        if svc.sid in seen_sids:
            continue
        seen_sids.add(svc.sid)

        name = UDS_SERVICE_NAMES.get(svc.sid, f"UnknownService_0x{svc.sid:02X}")
        cb = f"0x{svc.callback:05X}" if svc.callback else None
        table_base = "0x25E30" if svc.table_index < 17 else "0x25FC8"
        matches.append({
            "kind": "service",
            "sid": svc.sid,
            "oem_name": name,
            "oem_symbol": f"uds_{slug(name)}",
            "match_grade": "exact",
            "firmware_table_index": svc.table_index,
            "firmware_callback": cb,
            "firmware_table_base": table_base,
            "annotation_action": "name_callback" if cb else "comment",
            "note": f"UDS SID 0x{svc.sid:02X} ({name}).",
        })

    return matches


# ── Main ──────────────────────────────────────────────────────────────────────

def build_vocabulary() -> dict:
    catalog = json.loads(CATALOG_PATH.read_text())
    cf = CODEFLASH_PATH.read_bytes()
    tables = extract_all(cf)

    sha = firmware_sha256()
    assert sha == catalog["firmware_sha256"], (
        f"Firmware SHA mismatch: catalog={catalog['firmware_sha256'][:16]}... "
        f"actual={sha[:16]}..."
    )

    all_matches = []
    all_matches.extend(correlate_dids(catalog, tables))
    all_matches.extend(correlate_dtcs(catalog, cf))
    all_matches.extend(correlate_monitors(catalog, tables))
    all_matches.extend(correlate_active_tests(catalog, tables))
    all_matches.extend(correlate_services(catalog, tables))

    # Summarize by grade
    by_grade: dict[str, int] = {}
    by_kind: dict[str, int] = {}
    for m in all_matches:
        by_grade[m["match_grade"]] = by_grade.get(m["match_grade"], 0) + 1
        by_kind[m["kind"]] = by_kind.get(m["kind"], 0) + 1

    return {
        "firmware_sha256": sha,
        "techstream_distribution": catalog["techstream_distribution"],
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "ecu": catalog["ecu"],
        "source_catalog": str(CATALOG_PATH.relative_to(REPO_ROOT)),
        "firmware_tables": {
            "did_table": {"base": "0x2941C", "count": len(tables.dids)},
            "service_table": {"base": "0x25E30", "count": len(tables.services)},
            "routine_table": {"base": "0x25768", "count": len(tables.routines)},
            "write_did_table": {"base": "0x26AEC", "count": len(tables.write_dids)},
        },
        "summary": {
            "total_mappings": len(all_matches),
            "by_kind": by_kind,
            "by_grade": by_grade,
            "auto_apply_count": sum(
                1 for m in all_matches
                if m["annotation_action"] in ("name_callback",)
            ),
            "comment_only_count": sum(
                1 for m in all_matches
                if m["annotation_action"] in ("comment", "vocabulary")
            ),
        },
        "mappings": all_matches,
    }


def main() -> None:
    vocab = build_vocabulary()

    out_dir = REPO_ROOT / "data" / "generated" / "21140bbd65e530a9"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "diagnostic_vocabulary.json"

    out_path.write_text(json.dumps(vocab, indent=2, ensure_ascii=False))
    print(f"Wrote {out_path}")
    print(f"  {vocab['summary']['total_mappings']} mappings")
    for kind, count in sorted(vocab["summary"]["by_kind"].items()):
        print(f"    {kind}: {count}")
    print("  by grade:")
    for grade, count in sorted(vocab["summary"]["by_grade"].items()):
        print(f"    {grade}: {count}")
    print(f"  auto-apply (symbol rename): {vocab['summary']['auto_apply_count']}")
    print(f"  comment-only: {vocab['summary']['comment_only_count']}")


if __name__ == "__main__":
    main()
