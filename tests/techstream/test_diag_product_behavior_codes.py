import sqlite3
import unittest
from tools.techstream.diag_product_behavior_codes import (
    BehaviorCodeStore,
    restore_behavior_code,
)


class BehaviorTests(unittest.TestCase):
    def setUp(self):
        self.db = sqlite3.connect(":memory:")
        self.store = BehaviorCodeStore(self.db)

    def sample(self, modern=False):
        row = dict(
            behavior_code=1280,
            comment=None,
            name="Condition",
            signature="X0500",
            source="Engine.ddb",
            table=87,
            record=0,
        )
        if modern:
            row.update(
                comment_string_index=0,
                division_string_index=2,
                enabled=0,
                exception_handler_flag=1,
                exception_handler_id=5,
                memory_override=0,
                name_string_index=9,
                division="",
            )
        else:
            row["kind"] = "behavior"
        return row

    def test_unknown_bytes_exact_and_corruption(self):
        row = dict(self.sample(True), table=163)
        absent = self.store.row(row)
        for encoded in ("000000", "abcdef"):
            current = dict(row, uninterpreted_bytes={"65_67": encoded})
            ref = self.store.row(current)
            self.assertNotEqual(ref, absent)
            self.assertEqual(restore_behavior_code(self.db, ref["$behavior_code"]), current)
        self.db.execute("UPDATE behavior_code_defs SET unknown_bytes=x'00'")
        with self.assertRaises(ValueError):
            restore_behavior_code(self.db, absent["$behavior_code"])

    def test_variants_and_sharing(self):
        for modern in (False, True):
            row = self.sample(modern)
            ref = self.store.row(row)
            self.assertEqual(restore_behavior_code(self.db, ref["$behavior_code"]), row)
            self.assertEqual(self.store.row(row), ref)
            other = dict(row, record=4)
            self.assertNotEqual(self.store.row(other), ref)
        self.assertEqual(
            self.db.execute("SELECT count(*) FROM behavior_code_defs").fetchone()[0], 2
        )

    def test_future_and_boolean_stay_inline(self):
        for row in (
            dict(self.sample(), future=1),
            dict(self.sample(), behavior_code=True),
        ):
            self.assertEqual(self.store.row(row), row)

    def test_source_root_shares_full_facts_and_keeps_unknowns(self):
        row = self.sample(True)
        future = dict(row, uninterpreted_bytes={"67": "01"})
        actual = self.store.normalize(
            {
                "rob": {"behavior_codes": [row]},
                "p6_rob_source": {"behavior_codes": [row, row, future], "other": 1},
            }
        )
        self.assertEqual(
            actual["rob"]["behavior_codes"][0],
            actual["p6_rob_source"]["behavior_codes"][0],
        )
        rows = actual["p6_rob_source"]["behavior_codes"]
        self.assertEqual(len(rows), 3)
        self.assertEqual(rows[0], rows[1])
        self.assertIs(rows[2], future)
        self.assertEqual(actual["p6_rob_source"]["other"], 1)
        self.assertEqual(restore_behavior_code(self.db, rows[0]["$behavior_code"]), row)
        self.assertEqual(
            self.db.execute("SELECT count(*) FROM behavior_code_entries").fetchone()[0],
            1,
        )

    def test_missing_and_null_text(self):
        row = self.sample(True)
        row["name"] = None
        row["comment"] = ""
        ref = self.store.row(row)
        self.assertEqual(restore_behavior_code(self.db, ref["$behavior_code"]), row)
        self.db.execute("DELETE FROM text_values WHERE value=''")
        with self.assertRaises(ValueError):
            restore_behavior_code(self.db, ref["$behavior_code"])

    def test_scope_and_disabled(self):
        row = self.sample(True)
        doc = {"rob": {"behavior_codes": [row]}, "other": row}
        got = self.store.normalize(doc)
        self.assertEqual(got["other"], row)
        self.assertEqual(
            restore_behavior_code(
                self.db, got["rob"]["behavior_codes"][0]["$behavior_code"]
            )["enabled"],
            0,
        )
