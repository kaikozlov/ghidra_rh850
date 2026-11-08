import sqlite3
import unittest
from tools.techstream.diag_product_recorder import Store, SPECS, restore


def sample(kind):
    ints, texts, bools, floats, refs, lists = SPECS[kind]
    value = {k: 0 for k in ints}
    value.update({k: None for k in texts})
    value.update({k: False for k in bools})
    value.update({k: 0.0 for k in floats})
    value.update({k: {"$signal_info": 1} for k in refs})
    value.update({k: [2, 2, 0] for k in lists})
    if kind == "ddr_behavior_condition":
        value["comparison_bits64"] = (1 << 64) - 1
    value.update(source="ECU.ddb", table=167, record=3)
    return value


class RecorderTests(unittest.TestCase):
    def setUp(self):
        self.db = sqlite3.connect(":memory:")
        self.db.executescript(
            "CREATE TABLE text_values(id INTEGER PRIMARY KEY,value TEXT UNIQUE);CREATE TABLE signal_infos(id INTEGER PRIMARY KEY);INSERT INTO signal_infos VALUES(1);"
        )
        self.store = Store(self.db)

    def test_all_shapes_exact_and_reopen(self):
        for kind in SPECS:
            row = sample(kind)
            marker = self.store.row(kind, row)
            self.assertEqual(restore(self.db, kind, marker["$" + kind]), row)
            self.assertEqual(Store(self.db).row(kind, row), marker)

    def test_condition_unknown_byte_preserves_presence_and_reopens(self):
        base = sample("ddr_condition")
        markers = []
        for value in (None, "00", "a5", "ff"):
            row = dict(base)
            if value is not None:
                row["uninterpreted_bytes"] = {"15": value}
            marker = self.store.row("ddr_condition", row)
            self.assertIn("$ddr_condition", marker)
            self.assertEqual(restore(self.db, "ddr_condition", marker["$ddr_condition"]), row)
            self.assertEqual(Store(self.db).row("ddr_condition", row), marker)
            markers.append(marker["$ddr_condition"])
        self.assertEqual(len(set(markers)), 4)
        for value in (None, {}, {"15": ""}, {"15": "0"}, {"15": "GG"},
                      {"15": "FF"}, {"15": " 0"}, {"15": 0}, {"15": "00", "16": "00"}):
            row = dict(base, uninterpreted_bytes=value)
            self.assertEqual(self.store.row("ddr_condition", row), row)

    def test_unknown_fields_and_invalid_types_remain_inline(self):
        row = sample("ddr_signal")
        row["future"] = True
        self.assertEqual(self.store.row("ddr_signal", row), row)
        row = sample("ddr_signal")
        row["bit_start"] = True
        self.assertEqual(self.store.row("ddr_signal", row), row)
        row = sample("ddr_signal")
        row["data_min"] = -0.0
        self.assertEqual(self.store.row("ddr_signal", row), row)

    def test_relationship_order_and_completeness(self):
        ident = self.store.row("ddr_signal", sample("ddr_signal"))["$ddr_signal"]
        self.db.execute("DELETE FROM ddr_signal_data_id_records WHERE position=2")
        with self.assertRaisesRegex(ValueError, "incomplete"):
            restore(self.db, "ddr_signal", ident)

    def test_missing_text_and_boolean_corruption(self):
        ident = self.store.row("ddr_signal", sample("ddr_signal"))["$ddr_signal"]
        self.db.execute("UPDATE ddr_signal_defs SET list_member=2")
        with self.assertRaisesRegex(ValueError, "boolean"):
            restore(self.db, "ddr_signal", ident)

    def test_source_views_share_definition(self):
        row = sample("ddr_data_id")
        self.store.row("ddr_data_id", row)
        row["source"] = "other.ddb"
        self.store.row("ddr_data_id", row)
        self.assertEqual(
            self.db.execute("SELECT count(*) FROM ddr_data_id_defs").fetchone()[0], 1
        )
