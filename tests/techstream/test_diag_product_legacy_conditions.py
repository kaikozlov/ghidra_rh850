import sqlite3
import unittest
from tools.techstream.diag_product_legacy_conditions import (
    ConditionStore,
    condition_view,
    response_view,
    dynamic_view,
    restore_condition,
    restore_response,
    restore_dynamic,
)


class LegacyConditionTests(unittest.TestCase):
    def setUp(self):
        self.db = sqlite3.connect(":memory:")
        self.store = ConditionStore(self.db)

    def test_central_reader_semantic_marker_registry(self):
        from tools.techstream.diag_metadata import READERS, restore
        from unittest.mock import Mock, patch

        rows = [
            condition_view((1, 10001, 0, 7, 2, 0, 0), b"\\x04", "ECU.ddb", 8, 0, 1),
            response_view((2, 4, 0, 0), "ECU.ddb", 6, 9),
            dynamic_view((314, -10, 255, 24, 31, 79), 5),
        ]
        for row in rows:
            marker = self.store.row(row)
            self.assertNotIn("$legacy_response", marker)
            self.assertEqual(restore(self.db, marker), row)
        reader = Mock(return_value={"kind": "freeze_frame"})
        with patch.dict(READERS, {"$legacy_freeze_signal": reader}):
            self.assertEqual(
                restore(self.db, {"$legacy_freeze_signal": 1}), {"kind": "freeze_frame"}
            )
            reader.assert_called_once_with(self.db, 1)

    def test_modes_and_variable_states(self):
        for mode in (2, 3, 4, 6, 99):
            for variable in (None, b"", b"\x01", b"\xff\xbe"):
                for end in (3, 7):
                    values = (1, 10001, 7, end, mode, 0, 0)
                    row = condition_view(values, variable, "ECU.ddb", 8, 0, 1)
                    identity = self.store.row(row)["$legacy_condition"]
                    self.assertEqual(restore_condition(self.db, identity), row)

    def test_shared_facts_and_kind_binding(self):
        values = (1, 10001, 0, 7, 2, 0, 0)
        a = condition_view(values, b"\x04", "ECU.ddb", 8, 0, 1)
        b = condition_view(values, b"\x04", "ECU.ddb", 8, 0, 0)
        self.store.row(a)
        self.store.row(b)
        self.assertEqual(len(self.store.maps["legacy_condition_defs"]), 1)
        self.assertEqual(len(self.store.maps["legacy_condition_entries"]), 2)
        self.assertEqual(ConditionStore(self.db).row(a), self.store.row(a))

    def test_response_dynamic_and_future(self):
        for length in (0, 4):
            row = response_view((2, length, 0, 0), "ECU.ddb", 6, 9)
            identity = self.store.row(row)["$legacy_response_definition"]
            self.assertEqual(restore_response(self.db, identity), row)
        row = dynamic_view((314, -10, 255, 24, 31, 79), 5)
        identity = self.store.row(row)["$legacy_dynamic"]
        self.assertEqual(restore_dynamic(self.db, identity), row)
        future = dict(row, new_policy="unknown")
        self.assertIs(self.store.row(future), future)
        invalid = dict(row, mul=True)
        self.assertIs(self.store.row(invalid), invalid)

    def test_offline_predicate_behavior_preserved(self):
        from tools.techstream.gts.legacy_signals import evaluate_support_condition

        for mode in (2, 3, 4, 6, 99):
            variable = b"\\x01\\x02" if mode == 4 else b"\\x01"
            row = condition_view((1, 1, 0, 7, mode, 0, 0), variable, "E.ddb", 8, 0, 0)
            restored = restore_condition(
                self.db, self.store.row(row)["$legacy_condition"]
            )
            for payload in (b"", bytes(8), bytes([255]) * 8):

                def result(value):
                    try:
                        return evaluate_support_condition(value, payload)
                    except ValueError as error:
                        return str(error)

                self.assertEqual(result(row), result(restored))

    def test_empty_variable_not_absent_and_missing_reference(self):
        values = (1, 1, 0, 7, 6, 0, 0)
        row = condition_view(values, b"", "ECU.ddb", 9, 0, 0)
        identity = self.store.row(row)["$legacy_condition"]
        restored = restore_condition(self.db, identity)
        self.assertEqual(restored["variable"], "")
        self.assertEqual(restored["native_status"], "invalid_variable_length")
        self.db.execute("DELETE FROM legacy_condition_defs")
        with self.assertRaises(ValueError):
            restore_condition(self.db, identity)


if __name__ == "__main__":
    unittest.main()
