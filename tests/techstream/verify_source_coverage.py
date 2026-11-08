"""Audit every selected catalog, including variant/non-Gen database selections.

This is source-row coverage, not proof that every field or live path is understood.
Only explicit source collections count. Nested lookup copies cannot mask missing
top-level rows, unknown source tables fail, and raw-only records do not count.
Run: python -m tests.techstream.verify_source_coverage BUNDLE_DIRECTORY
"""
from __future__ import annotations
import argparse
from collections import Counter
import json
from pathlib import Path
from tools.techstream.diag_bundle import DiagnosticBundle

COLLECTION_TABLES = {
    "legacy_records": set(range(6,13)),
    "support_catalog": {0,1,2,3,4,154,155},
    "physical_catalog": {13,14,15},
    "dynamic_lsb": {39},
    "legacy_rob": {42,43,44,45,46,56,57,58,59},
    "ddr": {165,166,167,168},
    "work_factor": {18,35,36,37,114,115,116,117,118},
    "native_ddr": {t for base in (50,82,92,96,100,104,110,119,123,129,138,147)
                   for t in range(base,base+4)} | {108,109,127,128,136,137,145,146},
    "ddr_behavior": {133,134,135},
    "trigger_catalog": {16,19,32,171},
    "active_test_support": {67,69,70,72,73,78,79,142},
    "active_test_source": {33,68,71,77},
    "variable_drive": {38,41,55,60},
    "monitor_source": {61,156,62,157,63,66,80,81,86,87,88,153,89,90,151,91,152},
    "obd_monitor": {21,22,23,24,25,26,27,28,29,30,31,34,143,144,160,161,162,170},
    "diagnostic_metadata": {40,47,48,49,54},
    "dtc_source": {5,65},
    "p6_rob_source.behavior_codes": {163},
    "p6_rob_source.signals": {164},
}
TABLE_COLLECTION = {}
for collection, tables in COLLECTION_TABLES.items():
    for table in tables:
        if table in TABLE_COLLECTION:
            raise AssertionError(f"duplicate decoder registry table {table}")
        TABLE_COLLECTION[table] = collection

def source_rows(value):
    if isinstance(value, list):
        for item in value:
            yield from source_rows(item)
    elif isinstance(value, dict):
        if "table" in value and "record" in value:
            yield value
        else:
            for item in value.values():
                yield from source_rows(item)

def audit_catalog(catalog, source_db=None):
    errors = []
    sources = {int(s["table"]):s for s in catalog["source_tables"]}
    found = {}
    for collection, allowed in COLLECTION_TABLES.items():
        value = catalog
        for part in collection.split("."):
            value = value.get(part, {}) if isinstance(value, dict) else {}
        for row in source_rows(value):
            table, ordinal = int(row["table"]), int(row["record"])
            if table not in allowed:
                errors.append(f"{collection}: unexpected source table {table}")
                continue
            key = table, ordinal
            if key in found:
                errors.append(f"table {table} record {ordinal}: duplicate source projection")
            found[key] = row
            fields = set(row) - {"source","table","record","raw","family","kind","layout",
                                 "unassigned_bytes","unassigned_ranges","unassigned_fields","unassigned_tail"}
            if not fields:
                errors.append(f"table {table} record {ordinal}: raw-only projection")
    for table, source in sources.items():
        count, size = int(source["record_count"]), int(source["record_size"])
        if count and table not in TABLE_COLLECTION:
            errors.append(f"table {table}: no source decoder registered ({count} rows)")
            continue
        actual = {i for t,i in found if t == table}
        expected = set(range(count))
        if actual != expected:
            errors.append(f"table {table}: missing {sorted(expected-actual)[:12]}, extra {sorted(actual-expected)[:12]}")
        for ordinal in actual:
            raw = found[table,ordinal].get("raw")
            try:
                length = len(bytes.fromhex(raw)) if isinstance(raw,str) else len(raw)
            except (TypeError,ValueError):
                length = -1
            if length != size:
                errors.append(f"table {table} record {ordinal}: source bytes length {length}, expected {size}")
    if source_db is not None:
        from tools.techstream.ddb_semantics import records
        actual_headers = {t: (s.header.record_count, s.decoded_record_size)
                          for t,s in source_db.sections.items()}
        saved_headers = {t:(int(s["record_count"]),int(s["record_size"])) for t,s in sources.items()}
        if actual_headers != saved_headers:
            errors.append("source_tables inventory differs from actual selected database")
        for table,section in source_db.sections.items():
            for ordinal,raw in enumerate(records(section)):
                row = found.get((table,ordinal))
                if row is None:
                    continue
                encoded = row.get("raw")
                try:
                    decoded = bytes.fromhex(encoded) if isinstance(encoded,str) else bytes(encoded)
                except (TypeError,ValueError):
                    decoded = None
                if decoded != raw:
                    errors.append(f"table {table} record {ordinal}: bytes differ from actual selected source")
    for table,ordinal in found:
        if table not in sources:
            errors.append(f"table {table} record {ordinal}: source table absent")
    return errors

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("bundle", type=Path)
    parser.add_argument("--gts-root", type=Path, help="Also compare headers and every decoded source byte against selected databases")
    args = parser.parse_args()
    if args.gts_root:
        from tools.techstream.parse_ddb import DDBParser
        source_parser = DDBParser()
        from tests.techstream.viewer_source_audit import ViewerSourceAuditor
        viewer_auditor = ViewerSourceAuditor(args.gts_root)
    bundle = DiagnosticBundle(args.bundle)
    summary, failures, table_totals = Counter(), [], Counter()
    for name in bundle.namelist():
        if not name.startswith("catalogs/"):
            continue
        catalog = bundle.json(name)
        region = name.split("/")[1]
        summary[region] += 1
        for table in catalog["source_tables"]:
            table_totals[int(table["table"])] += int(table["record_count"])
        source_db = None
        if args.gts_root:
            source_path = args.gts_root / catalog["source_identity"]["database"]["path"]
            source_db = source_parser.parse_ecu_db(source_path)
        errors = audit_catalog(catalog, source_db)
        if args.gts_root:
            errors.extend(viewer_auditor.audit(catalog, region))
        if errors:
            failures.append({"catalog":name,"errors":errors})
    print(json.dumps({"selected_catalogs":dict(summary),"source_rows_by_table":dict(sorted(table_totals.items())),
                      "failed_catalogs":len(failures),"failures":failures},indent=2))
    return bool(failures)

if __name__ == "__main__":
    raise SystemExit(main())
