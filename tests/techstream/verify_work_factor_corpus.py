"""Check all selected regional source rows, without depending on the export."""
from collections import Counter
from tools.techstream import techstream_paths
from tools.techstream.diag_bundle import DiagnosticBundle, DEFAULT_BUNDLE
from tools.techstream.gts.ddb import _english_strings
from tools.techstream.gts.work_factor import viewer_help_index, work_factor_catalog
from tools.techstream.parse_ddb import DDBParser

parser = DDBParser()
base = techstream_paths.gts_db_root(techstream_paths.resolve_gts_root())
index = DiagnosticBundle(DEFAULT_BUNDLE).json("index.json")
tables = {18: "standard_info", 35: "work_factor_signals",
          36: "work_factor_items", 37: "work_factor_patterns",
          114: "work_factor_p5_signals", 115: "work_factor_rob_items",
          116: "work_factor_operation_codes", 117: "work_factor_network_status",
          118: "factor_data"}
for region, regional in sorted(index["regions"].items()):
    root = base.parents[2] / region / "DB" / "Gen"
    strings = _english_strings(parser, root)
    counts = Counter()
    help_index = viewer_help_index(parser.parse_viewer_db(root / "Viewer.ddb"),
                                   parser.load_string_db(root / "V_English.ddb"),
                                   f"{region}/Viewer.ddb", f"{region}/V_English.ddb")
    for filename in sorted({c["database"] for c in regional["selected_categories"].values()
                            if c.get("database")}):
        db = parser.parse_ecu_db(root / filename)
        catalog = work_factor_catalog(db, strings, filename, viewer_help=help_index)
        for table, key in tables.items():
            expected = db.sections[table].header.record_count if table in db.sections else 0
            assert len(catalog[key]) == expected, (region, filename, table)
            counts[key] += expected
        for row in catalog["standard_info"]:
            counts["standard_value_" + row["standard_value_status"]] += 1
            assert row["standard_value_status"] in ("resolved", "not_specified"), (region, filename, row)
            if row["help_id"]:
                assert row["standard_value"], (region, filename, row)
        for row in catalog["work_factor_items"]:
            counts["items_with_names"] += bool(row["name"])
            counts["items_without_pattern_match"] += bool(row["pattern_id"] and not row["pattern_records"])
            counts["items_with_invalid_bit_range"] += row["bit_end"] < row["bit_start"]
        for row in catalog["work_factor_signals"]:
            counts["signals_without_item_match"] += not bool(row["item_records"])
    print(region, dict(counts), flush=True)
