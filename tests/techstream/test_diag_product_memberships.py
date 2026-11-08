import sqlite3
import unittest

from tools.techstream.diag_product_memberships import Store, restore


class MembershipTests(unittest.TestCase):
    def fixture(self):
        db = sqlite3.connect(":memory:")
        db.executescript("""
            PRAGMA foreign_keys=ON;
            CREATE TABLE signal_definitions(id INTEGER PRIMARY KEY);
            CREATE TABLE dtc_entries(id INTEGER PRIMARY KEY);
            CREATE TABLE data_list_rows(id INTEGER PRIMARY KEY);
            INSERT INTO signal_definitions VALUES(1),(9007199254740993);
            INSERT INTO dtc_entries VALUES(2);
            INSERT INTO data_list_rows VALUES(3);
        """)
        self.addCleanup(db.close)
        return db, Store(db)

    def test_order_empty_groups_duplicates_and_exact_ids(self):
        db, store = self.fixture()
        document = {
            "dids": {
                "odd/~": [
                    {"$signal_definition": 9007199254740993},
                    {"$signal_definition": 1},
                    {"$signal_definition": 1},
                ],
                "empty": [],
            },
            "dtcs": {"P": [{"$diagnostic_code": 2}, {"$diagnostic_code": 2}]},
            "data_list": {"label": "display order", "rows": [{"$data_list_row": 3}]},
        }
        result = store.normalize(document)
        for field in ("dids", "dtcs"):
            marker, identity = next(iter(result[field].items()))
            restored = restore(db, marker, identity)
            self.assertEqual(restored, document[field])
            self.assertEqual(list(restored), list(document[field]))
        marker, identity = next(iter(result["data_list"]["rows"].items()))
        self.assertEqual(restore(db, marker, identity), document["data_list"]["rows"])
        self.assertEqual(store.normalize(document), result)
        self.assertEqual(Store(db).normalize(document), result)
        self.assertEqual(db.execute("PRAGMA foreign_key_check").fetchall(), [])

    def test_absence_null_empty_and_future_rows(self):
        db, store = self.fixture()
        for value in (
            {},
            {"dids": None},
            {"dids": {"x": [{"future": 1}]}},
            {"data_list": {"rows": None}},
        ):
            self.assertEqual(store.normalize(value), value)
        result = store.normalize(
            {"dids": {}, "dtcs": {"x": []}, "data_list": {"rows": []}}
        )
        for field in ("dids", "dtcs"):
            marker, identity = next(iter(result[field].items()))
            self.assertEqual(
                restore(db, marker, identity), {} if field == "dids" else {"x": []}
            )
        self.assertEqual(
            restore(
                db,
                "$display_membership",
                result["data_list"]["rows"]["$display_membership"],
            ),
            [],
        )

    def test_missing_or_invalid_target_is_not_silently_retained(self):
        db, store = self.fixture()
        for identity in (True, -1, 100):
            with self.assertRaises(ValueError):
                store.normalize({"dids": {"x": [{"$signal_definition": identity}]}})
        self.assertEqual(
            db.execute("SELECT count(*) FROM did_membership_sets").fetchone()[0], 0
        )

    def test_missing_tail_group_or_member_detected(self):
        db, store = self.fixture()
        result = store.normalize({"dids": {"a": [{"$signal_definition": 1}], "b": []}})
        identity = result["dids"]["$did_membership"]
        db.execute("DELETE FROM did_membership_rows WHERE set_id=?", (identity,))
        with self.assertRaisesRegex(ValueError, "incomplete"):
            restore(db, "$did_membership", identity)
        db.execute(
            "DELETE FROM did_membership_groups WHERE set_id=? AND position=1",
            (identity,),
        )
        with self.assertRaisesRegex(ValueError, "incomplete"):
            restore(db, "$did_membership", identity)

    def test_dangling_child_and_duplicate_mutation(self):
        db, store = self.fixture()
        result = store.normalize(
            {"data_list": {"rows": [{"$data_list_row": 3}, {"$data_list_row": 3}]}}
        )
        identity = result["data_list"]["rows"]["$display_membership"]
        rows = restore(db, "$display_membership", identity)
        rows[0]["$data_list_row"] = 99
        self.assertEqual(rows[1], {"$data_list_row": 3})
        db.commit()
        db.execute("PRAGMA foreign_keys=OFF")
        db.execute("DELETE FROM data_list_rows")
        with self.assertRaisesRegex(ValueError, "incomplete"):
            restore(db, "$display_membership", identity)


if __name__ == "__main__":
    unittest.main()
