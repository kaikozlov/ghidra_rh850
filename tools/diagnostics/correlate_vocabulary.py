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
import struct
import hashlib
from pathlib import Path

# These imports work because the script runs from the repo root and
# tools/techstream is on sys.path via the extract_catalog import chain.
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "techstream"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from firmware_tables import extract_all, FirmwareTables, DidEntry  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[2]
CODEFLASH_PATH = REPO_ROOT / "firmware" / "RH850_P1M-E_CodeFlash.bin"

# Firmware DTC table used by FUN_0005159e/FUN_000517b4. The callbacks walk 0xA0
# records with an 8-byte stride: identifiers are based at 0x309DC and enabled
# dwords at 0x309E0. Each record is:
# [u8:failure_type] [u16:dtc_id_LE] [u8:0x00] [u32:enabled]
# The DTC identifier is at byte offset 1 within the record. Byte 0 is the UDS
# failure-type/subtype byte: e.g. U023A has both 0x00 and 0x87 records in this
# image, producing full DTCs U023A and U023A87 respectively.
# Only matches within this table are "exact"; blind byte searches elsewhere
# in CodeFlash are false positives (immediate values, instruction bytes).
DTC_TABLE_START = 0x309DC
DTC_TABLE_COUNT = 0xA0
DTC_RECORD_SIZE = 8
DTC_TABLE_END = DTC_TABLE_START + DTC_TABLE_COUNT * DTC_RECORD_SIZE

# Generated diagnostic-event table consumed by FUN_00050f56/FUN_00051268.
# Byte 2 of each 8-byte record is the DTC-table index. This provides the durable
# link between a concrete Dem event and a full DTC record, including subtype.
DTC_EVENT_TABLE_START = 0x2FDDC
DTC_EVENT_TABLE_COUNT = 0x180
DTC_EVENT_RECORD_SIZE = 8

# RAM source mapping for seq-derived candidate firmware DIDs, recovered by
# decompiling each DID callback (via SeedDidCallbacks.java).  These identify
# the RAM variable or checkpoint object that each monitor reads and provide the
# independent evidence needed to promote the candidate semantic bridge.
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


def scan_firmware_dtc_event_links(cf: bytes) -> dict[int, list[int]]:
    """Return ``{dtc_table_index: [event_id, ...]}`` from the Dem event table."""
    links: dict[int, list[int]] = {}
    for event_id in range(DTC_EVENT_TABLE_COUNT):
        off = DTC_EVENT_TABLE_START + event_id * DTC_EVENT_RECORD_SIZE
        if off + DTC_EVENT_RECORD_SIZE > len(cf):
            break
        dtc_index = cf[off + 2]
        if dtc_index < DTC_TABLE_COUNT:
            links.setdefault(dtc_index, []).append(event_id)
    return links


def scan_firmware_dtc_table(cf: bytes) -> dict[int, list[dict]]:
    """Scan the firmware DTC table structurally without losing failure type.

    Returns ``{dtc_id: [{index, offset, failure_type, event_ids}, ...]}``.
    Only enabled records matching the known 8-byte layout are accepted.  The
    event IDs are resolved through the generated 0x180-entry Dem event table.
    """
    entries: dict[int, list[dict]] = {}
    event_links = scan_firmware_dtc_event_links(cf)
    end = min(DTC_TABLE_END, len(cf))
    for index, off in enumerate(range(DTC_TABLE_START, end, DTC_RECORD_SIZE)):
        failure_type, dtc_id, pad, enabled = struct.unpack_from("<BHBI", cf, off)
        if enabled != 1 or pad != 0 or dtc_id == 0:
            continue
        entries.setdefault(dtc_id, []).append({
            "index": index,
            "offset": off,
            "failure_type": failure_type,
            "event_ids": event_links.get(index, []),
        })
    return entries


def catalog_path() -> Path:
    """Resolve the catalog path from the firmware SHA (no hardcoded prefix)."""
    sha = firmware_sha256()
    return REPO_ROOT / "data" / "generated" / sha[:16] / "diagnostic_annotations.json"


# ── Correlators ───────────────────────────────────────────────────────────────

def correlate_dids(
    catalog: dict, tables: FirmwareTables
) -> list[dict]:
    """Correlate Techstream DIDs with firmware DID records.

    The catalog already deduplicates DIDs by identifier (regardless of source
    DDB variant), so each DID appears once.  Each is checked for an exact
    match in the 242-entry firmware DID table.
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
                "firmware_response_size_or_attribute": None,
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
            "firmware_response_size_or_attribute": (
                f"0x{fw.response_size_or_attribute:04X}"
            ),
            "firmware_table_base": "0x2941C",
            "source_db": ts_did["source_db"],
            # The DDB record supplies only the numeric identifier here; it
            # does not recover a semantic OEM name for the callback.
            "annotation_action": "comment",
            "note": f"Exact DID match. Firmware callback 0x{fw.callback:05X} "
                    f"at table index {fw.table_index}.",
        })

    return matches


def correlate_dtcs(
    catalog: dict, cf: bytes
) -> list[dict]:
    """Correlate Techstream DTCs with the firmware DTC table.

    Uses a structural scan of the firmware DTC table (0xA0 8-byte records at
    0x309DC-0x30EDC) rather than a blind byte search.  Only DTC IDs found
    within this table are "exact"; others are "family" (diagnostic-only or
    cross-generation).

    DTC descriptions are resolved against M_English.  If the same DTC ID has
    different descriptions across the KWP (EPS_P4DK3) and CAN (EPS_CAN_P4DK)
    databases, the grade is "candidate" with a conflict note — but only when
    both variants describe the same DID differently, not when the variants
    simply use different generic names (which is expected for different
    protocol generations).
    """
    fw_dtcs = scan_firmware_dtc_table(cf)
    matches = []
    techstream_dtcs = [e for e in catalog["entries"] if e["kind"] == "dtc"]
    seen_ids: dict[int, list[dict]] = {}

    for ts_dtc in techstream_dtcs:
        dtc_id = ts_dtc["dtc_identifier"]
        if dtc_id == 0:
            continue

        fw_entries = fw_dtcs.get(dtc_id)
        if fw_entries:
            offsets = [f"0x{entry['offset']:05X}" for entry in fw_entries]
            variants = []
            for entry in fw_entries:
                failure_type = entry["failure_type"]
                full_code = ts_dtc["code"] if failure_type == 0 else f"{ts_dtc['code']}{failure_type:02X}"
                variants.append({
                    "table_index": entry["index"],
                    "offset": f"0x{entry['offset']:05X}",
                    "failure_type": failure_type,
                    "full_code": full_code,
                    "event_ids": [f"0x{event_id:X}" for event_id in entry["event_ids"]],
                })
            grade = "exact"
            variant_text = ", ".join(
                f"{variant['full_code']}@{variant['offset']}"
                + (f" events={variant['event_ids']}" if variant["event_ids"] else "")
                for variant in variants[:3]
            )
            note = (f"DTC {ts_dtc['code']} (0x{dtc_id:04X}) found in firmware "
                    f"DTC table with {len(variants)} enabled subtype record(s): {variant_text}")
        else:
            offsets = []
            variants = []
            grade = "family"
            note = (f"DTC {ts_dtc['code']} (0x{dtc_id:04X}) not in firmware DTC "
                    f"table — may be diagnostic-only or cross-generation.")

        match = {
            "kind": "dtc",
            "code": ts_dtc["code"],
            "dtc_identifier": dtc_id,
            "oem_name": ts_dtc.get("resolved_name", "unknown"),
            "match_grade": grade,
            "firmware_offsets": offsets,
            "firmware_variants": variants,
            "source_db": ts_dtc["source_db"],
            "annotation_action": "comment",
            "note": note,
        }
        seen_ids.setdefault(dtc_id, []).append(match)
        matches.append(match)

    # Resolve conflicts across DDB variants.  CAN (EPS_CAN_P4DK) is authoritative
    # for this UDS firmware, just as for monitors.  KWP (EPS_P4DK3) differences
    # are expected (different protocol generation) and do NOT downgrade the grade.
    # Only flag as "candidate" when multiple different names exist WITHIN the same
    # variant for the same DTC ID.
    for dtc_id, entries in seen_ids.items():
        # Group by source DB variant
        by_db: dict[str, set[str]] = {}
        for e in entries:
            name = e["oem_name"]
            if name != "unknown":
                by_db.setdefault(e["source_db"], set()).add(name)

        has_intra_variant_conflict = any(len(names) > 1 for names in by_db.values())
        if has_intra_variant_conflict:
            for e in entries:
                e["match_grade"] = "candidate"
                e["note"] += " Multiple descriptions within the same database variant."

    return matches


def correlate_monitors(
    catalog: dict, tables: FirmwareTables
) -> list[dict]:
    """Correlate Techstream monitors with firmware DID records.

    Monitor record field 56 (the "seq" number) supplies a structural candidate
    via ``DID = 0x0100 + seq``. This is not a DDB DID-table relationship;
    promotion requires independent firmware callback/data-source evidence.

    For some monitors with seq < 100, the candidate exists in the firmware DID
    table. OEM names such as "Motor Instruction Current" and "Steering Torque"
    become structural only where callback decompilation independently agrees.

    EPS_CAN_P4DK (the UDS/CAN variant) is authoritative for this firmware's
    monitor vocabulary. EPS_P4DK3 (the KWP variant) uses different naming because
    it is a different protocol generation — KWP/CAN differences are EXPECTED
    and do not indicate a conflict.  Only disagreements WITHIN the CAN variant
    itself would trigger a candidate grade.
    """
    import struct
    from parse_ddb import DDBParser

    DB = REPO_ROOT / "Techstream/unpacked/toyota/Toyota Diagnostics/Techstream/NA/DB"
    parser = DDBParser()
    strings = parser.load_string_db(DB / "M_English.ddb")

    # Build per-DID name sets from each DDB variant by re-reading the raw
    # section 10 records (the catalog doesn't carry the seq number).
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

    # First: seq-derived monitor candidates that coincide with firmware DIDs.
    for did, names_by_db in sorted(monitor_names_by_did.items()):
        if did not in fw_dids:
            continue
        seen_dids.add(did)
        fw = fw_dids[did]
        can_names = sorted(set(names_by_db.get("EPS_CAN_P4DK.ddb", [])))
        kwp_names = sorted(set(names_by_db.get("EPS_P4DK3.ddb", [])))

        # Prefer the CAN-family label over the KWP-family label. This chooses
        # vocabulary; it does not prove calibration-specific semantics.
        oem_name = can_names[0] if can_names else (kwp_names[0] if kwp_names else "unnamed")

        # Attach independent decompiled RAM evidence for candidate DIDs.
        ram_source = MONITOR_RAM_SOURCES.get(did)

        # The seq bridge and firmware membership establish structure, not OEM
        # semantics by themselves. Auto-name only when callback decompilation
        # independently recovers a meaningful RAM source. DID 0x0111 is a stub
        # and 0x0101 has no recovered source, so both remain family vocabulary.
        if len(can_names) > 1:
            grade = "candidate"
        elif ram_source and not ram_source.startswith("stub:"):
            grade = "structural"
        else:
            grade = "family"

        match = {
            "kind": "monitor",
            "identifier": did,
            "oem_name": oem_name,
            "oem_symbol": slug(oem_name),
            "match_grade": grade,
            "firmware_table_index": fw.table_index,
            "firmware_callback": f"0x{fw.callback:05X}",
            "firmware_response_size_or_attribute": (
                f"0x{fw.response_size_or_attribute:04X}"
            ),
            "source_db": "EPS_CAN_P4DK" if can_names else "EPS_P4DK3",
            "can_variant_name": can_names[0] if can_names else None,
            "kwp_variant_name": kwp_names[0] if kwp_names else None,
            "annotation_action": "name_callback" if grade == "structural" else "comment",
        }
        if ram_source:
            match["ram_source"] = ram_source

        parts = [
            f"Monitor seq {did - 0x0100} → DID 0x{did:04X}, callback "
            f"0x{fw.callback:05X}.",
            f"CAN name: '{can_names[0]}'." if can_names else "No CAN name.",
        ]
        if kwp_names:
            parts.append(f"KWP name: '{kwp_names[0]}' (different protocol, expected).")
        if ram_source:
            parts.append(f"RAM: {ram_source}.")
        match["note"] = " ".join(parts)
        matches.append(match)

    # Remaining monitors without a matching firmware candidate stay as family
    # vocabulary. Do not append source records for a bridge already emitted
    # above; the old logic duplicated every bridged monitor as exact and family.
    for mon in [e for e in catalog["entries"] if e["kind"] == "monitor"]:
        seq = mon.get("monitor_seq")
        if seq is not None and 0x0100 + seq in seen_dids:
            continue
        name = mon.get("resolved_name") or "unnamed"
        matches.append({
            "kind": "monitor",
            "oem_name": name,
            "oem_symbol": slug(name),
            "match_grade": "family",
            "source_db": mon["source_db"],
            "monitor_seq": seq,
            "scaling_raw": mon.get("scaling_raw"),
            "annotation_action": "vocabulary",
            "note": (f"Techstream Data List monitor '{name}'. No firmware DID "
                     f"match (seq >= 100 or not in DID table)."),
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


def correlate_utility_strings(
    catalog: dict, tables: FirmwareTables
) -> list[dict]:
    """Carry steering-anchored U_English strings as family-only evidence.

    U_English provides resource identifiers but not ECU ownership or a firmware
    procedure relationship. The extractor uses explicit steering anchors only;
    no firmware routine mapping is attempted.
    """
    procedures = [e for e in catalog["entries"] if e["kind"] == "utility_string"]

    matches = []
    for proc in procedures:
        text = proc.get("text", "")
        name = text.strip().split("\r\n")[0][:120] if text else "unnamed"
        matches.append({
            "kind": "utility_string",
            "oem_name": name,
            "text": text,
            "oem_symbol": slug(name),
            "match_grade": "family",
            "string_index": proc.get("string_index"),
            "matched_patterns": proc.get("matched_patterns", []),
            "resource_identifier": proc.get("resource_identifier"),
            "resource_auxiliary_value": proc.get("resource_auxiliary_value"),
            "source_db": "U_English",
            "annotation_action": "vocabulary",
            "note": "Steering-anchored text from U_English.ddb. Resource IDs "
                    "group UI text but do not establish ECU/procedure linkage; family-level "
                    "vocabulary only, with no firmware routine mapping.",
        })

    return matches


def build_vocabulary() -> dict:
    cat_path = catalog_path()
    catalog = json.loads(cat_path.read_text())
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
    all_matches.extend(correlate_services(catalog, tables))
    all_matches.extend(correlate_utility_strings(catalog, tables))

    # Summarize by grade
    by_grade: dict[str, int] = {}
    by_kind: dict[str, int] = {}
    for m in all_matches:
        by_grade[m["match_grade"]] = by_grade.get(m["match_grade"], 0) + 1
        by_kind[m["kind"]] = by_kind.get(m["kind"], 0) + 1

    return {
        "firmware_sha256": sha,
        "techstream_distribution": catalog["techstream_distribution"],
        "ecu": catalog["ecu"],
        "source_catalog": str(cat_path.relative_to(REPO_ROOT)),
        "firmware_tables": {
            "did_table": {"base": "0x2941C", "count": len(tables.dids)},
            "service_table": {"base": "0x25E30", "count": len(tables.services)},
            "routine_table": {"base": "0x25768", "count": len(tables.routines)},
            "write_did_table": {"base": "0x26AEC", "count": len(tables.write_dids)},
            "dtc_table": {
                "base": f"0x{DTC_TABLE_START:X}",
                "end": f"0x{DTC_TABLE_END:X}",
                "count": DTC_TABLE_COUNT,
                "record_size": DTC_RECORD_SIZE,
                "failure_type_offset": 0,
                "dtc_identifier_offset": 1,
            },
            "dtc_event_table": {
                "base": f"0x{DTC_EVENT_TABLE_START:X}",
                "count": DTC_EVENT_TABLE_COUNT,
                "record_size": DTC_EVENT_RECORD_SIZE,
                "dtc_table_index_offset": 2,
            },
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

    sha = firmware_sha256()
    out_dir = REPO_ROOT / "data" / "generated" / sha[:16]
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
