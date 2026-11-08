import copy
import sqlite3
import unittest

from tools.techstream.diag_freeze_physical import (
    SCHEMA,
    Writer,
    restore_freeze_physical,
)


class FreezePhysicalTest(unittest.TestCase):
    def setUp(self):
        self.db = sqlite3.connect(":memory:")
        self.db.execute("PRAGMA foreign_keys=ON")
        self.db.executescript(
            "CREATE TABLE text_values(id INTEGER PRIMARY KEY,value TEXT UNIQUE);"
            + SCHEMA
        )
        self.writer = Writer(self.db)

    def row(self):
        return dict(
            bit_width=8,
            decimal_point_count=2,
            div=0,
            mul=9007199254740993,
            offset=-3,
            physical_data_key=4,
            record=5,
            sign_mode=2,
            table=13,
            unit_key=6,
            units=[dict(genre_id=0, record=7, string_index=8, table=15, text=None)],
            patterns=[
                dict(record=9, string_index=10, table=14, text="", value=-1),
                dict(record=9, string_index=10, table=14, text="", value=-1),
            ],
        )

    def test_exact_dedup_order_nullable_and_zero_divisor(self):
        row = self.row()
        ref = self.writer.transform(row)
        self.assertEqual(ref, self.writer.transform(copy.deepcopy(row)))
        self.assertEqual(restore_freeze_physical(self.db, ref["$freeze_physical"]), row)
        self.assertEqual(
            self.db.execute("select count(*) from freeze_physical_defs").fetchone()[0],
            1,
        )
        self.assertEqual(
            self.db.execute("select count(*) from freeze_patterns").fetchone()[0], 1
        )
        self.assertEqual(
            self.db.execute("select count(*) from freeze_pattern_members").fetchone()[
                0
            ],
            2,
        )

    def test_unknown_states_preserved_inline(self):
        for row in [
            dict(self.row(), future_state="unsupported"),
            dict(self.row(), offset=-0.0),
            dict(self.row(), sign_mode=False),
            dict(self.row(), units=[]),
        ]:
            self.assertEqual(self.writer.transform(row), row)

    def test_missing_tail_and_missing_reference(self):
        ref = self.writer.transform(self.row())["$freeze_physical"]
        self.db.execute("delete from freeze_pattern_members where position=1")
        with self.assertRaisesRegex(ValueError, "incomplete"):
            restore_freeze_physical(self.db, ref)
        with self.assertRaisesRegex(ValueError, "missing"):
            restore_freeze_physical(self.db, 999)
