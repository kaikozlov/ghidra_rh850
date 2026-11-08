import sqlite3
import unittest
from tools.techstream.diag_signal_observations import (
    ObservationStore,
    SHAPES,
    INTEGER_FIELDS,
    restore,
)


class SignalObservationTests(unittest.TestCase):
    def setUp(self):
        self.db = sqlite3.connect(":memory:")
        self.store = ObservationStore(self.db)

    def row(self, shape):
        r = {k: 0 for k in INTEGER_FIELDS if k in SHAPES[shape]}
        r.update(
            name="Signal",
            source="ECU.ddb",
            table=62,
            record=7,
            signal_info={"$signal_info": 1},
        )
        if "decoder" in SHAPES[shape]:
            r["decoder"] = "p6-native-msb0-u32-v1"
        if "did_support" in SHAPES[shape]:
            r["did_support"] = {"$did_support": 2}
        if "support_condition" in SHAPES[shape]:
            r["support_condition"] = None
        if "dynamic_lsb_possible" in SHAPES[shape]:
            r["dynamic_lsb_possible"] = False
        if "physical_range" in SHAPES[shape]:
            r["physical_range"] = [0.0, 79.998]
        if "graph_range" in SHAPES[shape]:
            r["graph_range"] = [0, 79997]
        if shape == 3:
            r["tables"] = [62, 157, 157]
        return r

    def test_unknown_bytes_exact_and_corruption(self):
        row = dict(self.row(2), table=164)
        absent = self.store.row(row)
        for fields in ({"38_39": "0000", "43_47": "0000000000"},
                       {"38_39": "abcd", "43_47": "0102030405"}):
            current = dict(row, uninterpreted_bytes=fields)
            ref = self.store.row(current)
            self.assertNotEqual(ref, absent)
            self.assertEqual(restore(self.db, ref["$signal_observation"]), current)
        self.db.execute("UPDATE signal_observations SET unknown_bytes=x'00'")
        with self.assertRaises(ValueError):
            restore(self.db, absent["$signal_observation"])

    def test_all_shapes_exact_and_origins_shared(self):
        for shape in SHAPES:
            row = self.row(shape)
            identity = self.store.row(row)["$signal_observation"]
            self.assertEqual(restore(self.db, identity), row)
            other = dict(row, source="Other.ddb", record=8)
            self.store.row(other)
        self.assertEqual(len(self.store.definitions), 5)
        self.assertEqual(len(self.store.entries), 10)

    def test_unknown_support_and_unknown_future(self):
        row = self.row(4)
        row["local_support_mode"] = None
        identity = self.store.row(row)["$signal_observation"]
        self.assertEqual(restore(self.db, identity), row)
        future = dict(row, new_semantics="preserve me")
        self.assertIs(self.store.row(future), future)
        negative_zero = self.row(5)
        negative_zero["physical_range"] = [-0.0, 1.0]
        self.assertIs(self.store.row(negative_zero), negative_zero)

    def test_source_root_shares_facts_and_preserves_source_only_and_unknown_rows(self):
        shared = self.row(4)
        source_only = dict(shared, record=99)
        future = dict(shared, unknown_semantics={"value": 7})
        document = {
            "rob": {"signals": [shared]},
            "p6_rob_source": {
                "signals": [shared, source_only, shared, future],
                "other": "retained",
            },
        }
        actual = self.store.normalize(document)
        self.assertEqual(
            actual["rob"]["signals"][0], actual["p6_rob_source"]["signals"][0]
        )
        rows = actual["p6_rob_source"]["signals"]
        self.assertEqual(len(rows), 4)
        self.assertEqual(rows[0], rows[2])
        self.assertEqual(restore(self.db, rows[1]["$signal_observation"]), source_only)
        self.assertIs(rows[3], future)
        self.assertEqual(actual["p6_rob_source"]["other"], "retained")
        self.assertEqual(len(self.store.entries), 2)

    def test_bad_reference_and_text(self):
        row = self.row(1)
        identity = self.store.row(row)["$signal_observation"]
        self.db.execute("UPDATE signal_observations SET info_id=0")
        with self.assertRaises(ValueError):
            restore(self.db, identity)
        self.db.execute("UPDATE signal_observations SET info_id=1")
        self.db.execute("DELETE FROM text_values WHERE value='Signal'")
        with self.assertRaises(ValueError):
            restore(self.db, identity)

    def test_reopen_and_list_order(self):
        row = self.row(3)
        identity = self.store.row(row)["$signal_observation"]
        self.assertEqual(
            ObservationStore(self.db).row(row), {"$signal_observation": identity}
        )
        self.db.execute("UPDATE signal_observations SET auxiliary_tables=1001")
        with self.assertRaises(ValueError):
            restore(self.db, identity)


if __name__ == "__main__":
    unittest.main()
