import copy
import sqlite3
import unittest
from tools.techstream.diag_freeze_physical import SCHEMA
from tools.techstream.diag_product_legacy_rob import Store, restore, INTS


def sample():
    row = {k: 0 for k in INTS}
    row.update(
        name=None,
        short_name="",
        decoder="legacy-rob-msb0-u32-v1",
        support_rule="excluded",
        source="unit.ddb",
        table=45,
        record=1,
        data_min=0.0,
        data_max=3.0,
    )
    unit = {"genre_id": 0, "name": None, "name_string_index": 70, "record": 61}
    physical = dict(
        decimal_point_count=0,
        div=1,
        mul=1,
        offset=0,
        physical_data_key=12,
        record=4,
        sign_mode=0,
        table=13,
        unit_key=5,
        units=[unit],
    )
    pattern = dict(name="ready", name_string_index=6, record=2, table=14, value=0)
    row.update(
        physical_variants=[physical, copy.deepcopy(physical)],
        pattern_display=[pattern, copy.deepcopy(pattern)],
    )
    return row


class LegacyROBTests(unittest.TestCase):
    def setUp(self):
        self.db = sqlite3.connect(":memory:")
        self.db.executescript(
            "CREATE TABLE text_values(id INTEGER PRIMARY KEY,value TEXT UNIQUE);"
            + SCHEMA
        )
        self.store = Store(self.db)

    def test_roundtrip_and_shared_definitions(self):
        row = sample()
        marker = self.store.row(row)
        ident = marker["$legacy_rob_signal"]
        self.assertEqual(restore(self.db, ident), row)
        other = copy.deepcopy(row)
        other["source"] = "other.ddb"
        self.assertEqual(
            restore(self.db, self.store.row(other)["$legacy_rob_signal"]), other
        )
        self.assertEqual(
            self.db.execute("SELECT count(*) FROM legacy_rob_definitions").fetchone()[
                0
            ],
            1,
        )
        self.assertEqual(Store(self.db).row(row), marker)

    def test_unknown_negative_zero_and_bool_stay_inline(self):
        for change in ({"future": 1}, {"data_min": -0.0}, {"bit_start": True}):
            row = sample()
            row.update(change)
            self.assertEqual(self.store.row(row), row)

    def test_missing_ordered_relationship_fails(self):
        ident = self.store.row(sample())["$legacy_rob_signal"]
        self.db.execute("DELETE FROM legacy_rob_variants WHERE position=1")
        with self.assertRaisesRegex(ValueError, "incomplete"):
            restore(self.db, ident)

    def test_missing_pattern_fails(self):
        ident = self.store.row(sample())["$legacy_rob_signal"]
        self.db.execute("DELETE FROM freeze_pattern_members WHERE position=0")
        with self.assertRaisesRegex(ValueError, "order"):
            restore(self.db, ident)
