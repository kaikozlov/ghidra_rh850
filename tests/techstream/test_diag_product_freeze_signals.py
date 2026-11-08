import sqlite3
import unittest
from tools.techstream.diag_product_freeze_signals import (
    FreezeStore,
    INTEGERS,
    BOOLEANS,
    restore,
)


class ProductFreezeSignalTests(unittest.TestCase):
    def setUp(self):
        self.db = sqlite3.connect(":memory:")
        self.store = FreezeStore(self.db)

    def row(self):
        value = {k: 0 for k in INTEGERS}
        value.update({k: False for k in BOOLEANS})
        value.update(
            kind="freeze_frame",
            layout="gtsplus-104",
            name=None,
            short_name="",
            source="ECU.ddb",
            table=10,
            record=2,
            data_min=0.0,
            data_max=127.0,
            physical_records=[{"$freeze_physical": 1}],
            support_conditions=[{"$legacy_condition": 2}, {"$legacy_condition": 2}],
            dynamic_lsb_records=[{"$legacy_dynamic": 3}],
        )
        return value

    def test_definition_origin_and_order(self):
        row = self.row()
        identity = self.store.row(row)["$legacy_freeze_signal"]
        self.assertEqual(restore(self.db, identity), row)
        other = dict(row, source="Another.ddb", record=5)
        second = self.store.row(other)["$legacy_freeze_signal"]
        self.assertEqual(restore(self.db, second), other)
        self.assertEqual(len(self.store.definitions), 1)
        self.assertEqual(len(self.store.entries), 2)
        self.assertEqual(
            FreezeStore(self.db).row(row), {"$legacy_freeze_signal": identity}
        )

    def test_missing_children_and_corrupt_integer(self):
        identity = self.store.row(self.row())["$legacy_freeze_signal"]
        self.db.execute("DELETE FROM legacy_freeze_support_members WHERE position=1")
        with self.assertRaises(ValueError):
            restore(self.db, identity)

    def test_unknown_semantics_stay_inline(self):
        for row in (
            dict(self.row(), future="preserve"),
            dict(self.row(), physical_records=[]),
            dict(self.row(), data_min=-0.0),
            dict(self.row(), support_conditions=[{"key": 1}]),
        ):
            self.assertIs(self.store.row(row), row)
        self.assertEqual(len(self.store.definitions), 0)

    def unknown(self):
        return {
            "34_3f": "01" * 12,
            "48_4b": "ff" * 4,
            "56_57": "0000",
            "5e_5f": "abcd",
            "67": 255,
        }

    def test_unknown_facts_share_without_duplicate_base_and_preserve_absence(self):
        absent = self.row()
        present = dict(absent, unassigned_fields=self.unknown())
        ids = [
            self.store.row(row)["$legacy_freeze_signal"] for row in (absent, present)
        ]
        self.assertNotEqual(*ids)
        self.assertEqual(restore(self.db, ids[0]), absent)
        self.assertEqual(restore(self.db, ids[1]), present)
        self.assertEqual(len(self.store.definitions), 1)
        self.assertEqual(len(self.store.unknowns), 1)
        self.assertEqual(
            FreezeStore(self.db).row(present), {"$legacy_freeze_signal": ids[1]}
        )
        changed = dict(present, unassigned_fields=dict(self.unknown(), **{"67": 0}))
        third = self.store.row(changed)["$legacy_freeze_signal"]
        self.assertEqual(restore(self.db, third), changed)
        self.assertEqual(len(self.store.definitions), 1)
        self.assertEqual(len(self.store.unknowns), 2)

    def test_unknown_future_shape_and_invalid_values_stay_inline(self):
        for unknown in (
            None,
            {},
            dict(self.unknown(), future=0),
            dict(self.unknown(), **{"67": True}),
            dict(self.unknown(), **{"67": 256}),
            dict(self.unknown(), **{"34_3f": "00"}),
            dict(self.unknown(), **{"5e_5f": "ABCD"}),
        ):
            row = dict(self.row(), unassigned_fields=unknown)
            self.assertIs(self.store.row(row), row)
        self.assertFalse(self.store.definitions)
        self.assertFalse(self.store.unknowns)

    def test_unknown_corruption_rejected(self):
        row = dict(self.row(), unassigned_fields=self.unknown())
        identity = self.store.row(row)["$legacy_freeze_signal"]
        for sql in (
            "UPDATE legacy_freeze_unknown_facts SET byte_67=256",
            "UPDATE legacy_freeze_unknown_facts SET bytes_34_3f=X'00'",
            "DELETE FROM legacy_freeze_unknown_facts",
        ):
            self.db.execute("SAVEPOINT corrupt")
            self.db.execute(sql)
            with self.assertRaises(ValueError):
                restore(self.db, identity)
            self.db.execute("ROLLBACK TO corrupt")
            self.db.execute("RELEASE corrupt")

    def test_nullable_label_and_positive_zero(self):
        row = self.row()
        row["support_conditions"] = []
        row["dynamic_lsb_records"] = []
        identity = self.store.row(row)["$legacy_freeze_signal"]
        restored = restore(self.db, identity)
        self.assertIsNone(restored["name"])
        self.assertIs(type(restored["data_min"]), float)


if __name__ == "__main__":
    unittest.main()
