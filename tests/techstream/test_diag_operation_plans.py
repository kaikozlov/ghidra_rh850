import copy
import sqlite3
import unittest

from tools.techstream.diag_operation_plans import (
    EXTERNAL,
    OPTIONAL,
    SCHEMAS,
    PlanStore,
    restore,
)


def example(name):
    out = {}
    optional = OPTIONAL[name][0]
    for field, typ in SCHEMAS[name].items():
        if field in optional:
            continue
        if typ.startswith("~"):
            value = None
        elif typ.startswith("[]"):
            value = []
        elif typ.startswith("@"):
            value = example(typ[1:])
        elif typ.startswith("$"):
            value = {typ: 1}
        elif typ == "b":
            value = False
        elif typ == "i":
            value = 0
        elif typ == "x":
            value = ""
        else:
            value = "text"
        out[field] = value
    if name in ("direct", "routine", "refused"):
        out["kind"] = "direct" if name == "refused" else name
    return out


class PlanTests(unittest.TestCase):
    def setUp(self):
        self.db = sqlite3.connect(":memory:")
        self.db.execute("PRAGMA foreign_keys=ON")
        for t in EXTERNAL.values():
            self.db.execute("CREATE TABLE " + t + "(id INTEGER PRIMARY KEY)")
            self.db.execute("INSERT INTO " + t + " VALUES(1)")
        self.store = PlanStore(self.db)

    def test_direct_null_absent_and_duplicate_ordered_frames(self):
        row = example("direct")
        row["id"] = 2**53 + 1
        frame = example("formula_frame")
        frame["materialized_prefix"] = "2f1234"
        row["start_frames"] = [frame, copy.deepcopy(frame)]
        original = copy.deepcopy(row)
        marker = self.store.normalize_plan(row)
        self.assertEqual(restore(self.db, marker["$operation_plan"]), row)
        self.assertEqual(original, row)
        self.assertEqual(
            self.db.execute("SELECT count(*) FROM plan_formula_frame").fetchone()[0], 1
        )
        self.assertIsNone(row["minimum_examples"])
        self.assertNotIn("support_gate", row)

    def test_routine_and_refusal_exact(self):
        for name in ("routine", "refused"):
            row = example(name)
            if name == "refused":
                row.update(error="No safe executor", execution="unsupported")
            marker = self.store.normalize_plan(row)
            self.assertEqual(restore(self.db, marker["$operation_plan"]), row)

    def test_unknown_field_and_shape_inline(self):
        row = example("direct")
        row["future_safety_gate"] = True
        self.assertEqual(self.store.normalize_plan(row), row)
        row = example("direct")
        row["initial_read"]["new_mode_semantics"] = 7
        self.assertEqual(self.store.normalize_plan(row), row)
        self.assertEqual(
            self.db.execute("SELECT count(*) FROM operation_plan_entries").fetchone()[
                0
            ],
            0,
        )

    def test_missing_ordered_tail_rejected(self):
        row = example("direct")
        row["start_frames"] = [example("formula_frame")] * 2
        marker = self.store.normalize_plan(row)
        self.db.execute("DELETE FROM plan_direct_start_frames WHERE position=1")
        with self.assertRaisesRegex(ValueError, "incomplete plan children"):
            restore(self.db, marker["$operation_plan"])

    def test_missing_reference_is_corruption(self):
        row = example("direct")
        row["control_enable_mask"] = {"$operation_mask": 99}
        with self.assertRaisesRegex(ValueError, "missing plan external"):
            self.store.normalize_plan(row)

    def test_presence_and_required_bool_are_checked(self):
        row = example("routine")
        marker = self.store.normalize_plan(row)
        self.db.execute("UPDATE plan_routine SET f_fixed_request=9")
        with self.assertRaisesRegex(ValueError, "invalid plan boolean"):
            restore(self.db, marker["$operation_plan"])


if __name__ == "__main__":
    unittest.main()
