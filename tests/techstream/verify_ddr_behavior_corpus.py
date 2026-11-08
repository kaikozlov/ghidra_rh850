"""Verify ADS DDR source row accounting and physical joins in every region."""
from collections import Counter
from tools.techstream import techstream_paths
from tools.techstream.diag_bundle import DiagnosticBundle, DEFAULT_BUNDLE
from tools.techstream.gts.ddb import _english_strings
from tools.techstream.gts.ddr_behavior import ddr_behavior_catalog
from tools.techstream.parse_ddb import DDBParser

parser = DDBParser()
base = techstream_paths.gts_db_root(techstream_paths.resolve_gts_root())
index = DiagnosticBundle(DEFAULT_BUNDLE).json("index.json")
for region, regional in sorted(index["regions"].items()):
    root = base.parents[2] / region / "DB" / "Gen"
    strings = _english_strings(parser, root)
    counts = Counter()
    for category in regional["selected_categories"].values():
        filename = category.get("database")
        if not filename:
            continue
        db = parser.parse_ecu_db(root / filename)
        if not any(table in db.sections for table in (133,134,135)):
            continue
        out = ddr_behavior_catalog(db, strings, filename)
        counts["catalogs"] += 1
        for table, field in ((133,"codes"),(134,"signals"),(135,"invalid_conditions")):
            expected = db.sections[table].header.record_count if table in db.sections else 0
            assert len(out[field]) == expected, (region, filename, table)
            counts[field] += len(out[field])
        for row in out["signals"]:
            assert row["signal_info"] is not None, (region, filename, row["signal_key"])
            assert row["signal_info"]["bit_width"] > 0
            counts["named_signals"] += bool(row["name"])
            for ordinal in row["invalid_condition_records"]:
                assert out["invalid_conditions"][ordinal]["signal_key"] == row["signal_key"]
    print(region, dict(counts), flush=True)
