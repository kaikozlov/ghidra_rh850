import sqlite3
import unittest

from tools.techstream.diag_product_dtcs import DTCStore, restore


class ProductDTCTests(unittest.TestCase):
    def setUp(self):
        self.db = sqlite3.connect(":memory:")
        self.store = DTCStore(self.db)

    def test_decoded_facts_and_origin_sharing(self):
        fact = dict(
            kind="dtc",
            code="P1234",
            description="説明",
            failure=None,
            packed_dtc="0x123400",
        )
        first = dict(fact, source="ECU.ddb", table=65, record=7)
        second = dict(fact, source="Other.ddb", table=65, record=8)
        for row in (first, second, fact):
            identity = self.store.row(row)["$diagnostic_code"]
            self.assertEqual(restore(self.db, identity), row)
        self.assertEqual(len(self.store.codes), 1)
        self.assertEqual(len(self.store.entries), 3)
        self.assertEqual(
            self.db.execute(
                "SELECT count(*) FROM sqlite_master WHERE name='ecu_records'"
            ).fetchone()[0],
            0,
        )

    def test_null_absent_and_future_fields(self):
        rows = [
            {"code": "C0001"},
            {"code": "C0001", "description": None},
            {"code": "C0001", "description": ""},
            {"code": "C0001", "comment": None, "dtc_identifier": 9007199254740993},
            {"code": "C0001", "source": None, "table": None, "record": None},
        ]
        for row in rows:
            self.assertEqual(
                restore(self.db, self.store.row(row)["$diagnostic_code"]), row
            )
        self.assertEqual(len(self.store.codes), 4)
        for row in (
            {"code": "P0010", "future_semantics": {"a": 1}},
            {"code": "P0010", "dtc_identifier": True},
            {"code": "P0010", "packed_dtc": "0x001abc"},
        ):
            self.assertIs(self.store.row(row), row)

    def test_missing_text_and_corrupt_mask(self):
        row = dict(code="P0001", description="desc")
        identity = self.store.row(row)["$diagnostic_code"]
        self.db.execute("UPDATE diagnostic_codes SET field_mask=128")
        with self.assertRaises(ValueError):
            restore(self.db, identity)
        self.db.execute("UPDATE diagnostic_codes SET field_mask=2")
        self.db.execute("DELETE FROM text_values WHERE value='desc'")
        with self.assertRaises(ValueError):
            restore(self.db, identity)

    def test_reopen_reuses_facts_and_bindings(self):
        row = dict(code="P0001", description="text", source="E.ddb", table=5, record=0)
        first = self.store.row(row)
        second = DTCStore(self.db).row(row)
        self.assertEqual(first, second)
        self.assertEqual(
            self.db.execute("SELECT count(*) FROM diagnostic_codes").fetchone()[0], 1
        )
        self.assertEqual(
            self.db.execute("SELECT count(*) FROM dtc_entries").fetchone()[0], 1
        )

    def test_root_is_only_semantic_dtcs(self):
        document = {
            "dtcs": {"P0010": [{"code": "P0010", "description": "yes"}]},
            "unrelated": {"code": "P0010"},
        }
        normalized = self.store.normalize(document)
        self.assertEqual(normalized["unrelated"], document["unrelated"])
        self.assertEqual(
            restore(self.db, normalized["dtcs"]["P0010"][0]["$diagnostic_code"]),
            document["dtcs"]["P0010"][0],
        )


if __name__ == "__main__":
    unittest.main()
