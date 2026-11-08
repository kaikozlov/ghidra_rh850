"""Verify legacy Active Test metadata against every selected regional source."""
from collections import Counter
from tools.techstream import techstream_paths
from tools.techstream.diag_bundle import DiagnosticBundle, DEFAULT_BUNDLE
from tools.techstream.gts.ddb import _english_strings
from tools.techstream.gts.legacy_active import legacy_active_tests, legacy_active_patterns
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
        path = root / filename
        assert path.is_file(), path
        db = parser.parse_ecu_db(path)
        patterns = legacy_active_patterns(db, filename)
        counts["pattern_records"] += len(patterns)
        rows = legacy_active_tests(db, strings, filename)
        if 11 in db.sections:
            counts["catalogs"] += 1
            assert len(rows) == db.sections[11].header.record_count, filename
        for row in rows:
            counts["active_tests"] += 1
            counts["english_names"] += bool(row["name"])
            assert row["pattern"] is not None, (region, filename, row["id"])
            assert row["signal_info"] is not None, (region, filename, row["id"])
            assert row["signal_info"]["bit_width"] > 0, (region, filename, row["id"])
            counts["support_dependent_programs"] += row["request_program"]["support_required"]
    print(region, dict(counts))
