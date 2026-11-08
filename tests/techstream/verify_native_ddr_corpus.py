"""Check exact DDR class-alias row accounting and family-scoped joins."""
from collections import Counter
from tools.techstream import techstream_paths
from tools.techstream.diag_bundle import DiagnosticBundle, DEFAULT_BUNDLE
from tools.techstream.gts.ddb import _english_strings
from tools.techstream.gts.native_ddr import native_ddr_catalog, MONITOR_TABLES, HEADER_TABLES
from tools.techstream.parse_ddb import DDBParser

parser = DDBParser()
base = techstream_paths.gts_db_root(techstream_paths.resolve_gts_root())
index = DiagnosticBundle(DEFAULT_BUNDLE).json("index.json")
tables = {t+i for t in MONITOR_TABLES for i in range(4)} | {t+i for t in HEADER_TABLES for i in range(2)}
for region, regional in sorted(index["regions"].items()):
    root = base.parents[2] / region / "DB" / "Gen"
    strings = _english_strings(parser, root)
    counts = Counter()
    for category in regional["selected_categories"].values():
        filename = category.get("database")
        if not filename:
            continue
        db = parser.parse_ecu_db(root / filename)
        if not tables.intersection(db.sections):
            continue
        out = native_ddr_catalog(db, strings, filename)
        counts["catalogs"] += 1
        actual = Counter()
        for field, rows in out.items():
            if not isinstance(rows, list):
                continue
            counts[field] += len(rows)
            for row in rows:
                actual[row["table"]] += 1
        expected = {table: sec.header.record_count for table,sec in db.sections.items() if table in tables}
        assert actual == expected, (region,filename,actual,expected)
        for row in out["monitors"]:
            counts["named_monitors"] += bool(row["name"])
            counts["physical_joins"] += row["signal_info"] is not None
        for row in out["addresses"]:
            counts["address_monitor_joins"] += bool(row["monitor_records"])
    print(region,dict(counts),flush=True)
