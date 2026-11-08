import sqlite3
import unittest
from tools.techstream.diag_product_legacy_conditions import (
    ConditionStore,
    dynamic_view,
    restore_dynamic,
)


class DynamicUnknownTests(unittest.TestCase):
    def test_optional_and_shared(self):
        db = sqlite3.connect(":memory:")
        store = ConditionStore(db)
        base = dynamic_view((1, 2, 3, 4, 5, 6), 0)
        old = store.row(base)
        self.assertEqual(restore_dynamic(db, old["$legacy_dynamic"]), base)
        for tail in ("", "010203"):
            value = dict(base, uninterpreted_bytes={"14_16": "abcdef", "18_end": tail})
            ref = store.row(value)
            self.assertIn("$legacy_dynamic", ref)
            self.assertEqual(restore_dynamic(db, ref["$legacy_dynamic"]), value)
        self.assertEqual(
            db.execute("SELECT count(*) FROM legacy_dynamic_defs").fetchone()[0], 1
        )
        for value in (
            dict(base, uninterpreted_bytes=None),
            dict(base, uninterpreted_bytes={"future": "aa"}),
        ):
            self.assertEqual(store.row(value), value)
        db.execute("DELETE FROM legacy_dynamic_unknown_facts")
        with self.assertRaises(ValueError):
            restore_dynamic(db, ref["$legacy_dynamic"])
