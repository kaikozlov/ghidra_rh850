"""Validate native DDR source accounting and joins for all selected regions."""
from collections import Counter
from tools.techstream import techstream_paths
from tools.techstream.diag_bundle import DiagnosticBundle, DEFAULT_BUNDLE
from tools.techstream.gts.ddb import _english_strings
from tools.techstream.gts.p6_ddr import p6_ddr_catalog
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
        if not any(table in db.sections for table in (165,166,167,168)):
            continue
        out = p6_ddr_catalog(db, strings, filename)
        counts["catalogs"] += 1
        for table, field in ((165,"triggers"),(166,"data_ids"),(167,"signals"),(168,"invalid_conditions")):
            expected = db.sections[table].header.record_count if table in db.sections else 0
            assert len(out[field]) == expected, (region, filename, table)
            counts[field] += len(out[field])
        for row in out["signals"]:
            assert row["signal_info"] is not None, (region, filename, row["signal_key"])
            assert row["data_id_records"], (region, filename, row["did"])
            assert row["signal_info"]["bit_width"] > 0
            counts["named_signals"] += bool(row["name"])
            counts["conditioned_signals"] += bool(row["invalid_condition_records"])
            for ordinal in row["data_id_records"]:
                assert out["data_ids"][ordinal]["did"] == row["did"]
            for ordinal in row["invalid_condition_records"]:
                assert out["invalid_conditions"][ordinal]["signal_key"] == row["signal_key"]
    print(region, dict(counts))
