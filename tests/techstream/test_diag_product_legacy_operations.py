import copy
import sqlite3
import unittest

from tools.techstream.diag_product_legacy_operations import (
    NUMBERS,
    PATTERN,
    OperationStore,
    restore,
    restore_pattern,
)


def example():
    row = dict.fromkeys(NUMBERS, 0)
    row.update(
        kind="active_test",
        name=None,
        execution="metadata_only",
        runtime_boundary="Needs live support reads; not executable.",
        source="Example.ddb",
        table=11,
        record=3,
        signal_info={"$signal_info": 1},
        pattern={
            **dict.fromkeys(PATTERN, 0),
            "source": "Example.ddb",
            "table": 12,
            "record": 5,
        },
        request_program={
            "encoded": 34,
            "request_identifier": 1,
            "constant_or_mask": 255,
            "generation_7": "identifier only",
            "nibble_order": "least_significant_first",
            "variant_boundary": "Live support required.",
            "support_required": True,
            "service_by_generation_low5": {"1": 109, "2": 109, "7": 61, "default": 48},
            "operations": [
                {"opcode": 2, "operation": "value_low_byte"},
                {"opcode": 2, "operation": "value_low_byte"},
            ],
        },
    )
    row["data_max"] = 2**53 + 1
    return row


class OperationTests(unittest.TestCase):
    def setUp(self):
        self.db = sqlite3.connect(":memory:")
        self.db.executescript(
            "PRAGMA foreign_keys=ON; CREATE TABLE signal_infos(id INTEGER PRIMARY KEY); INSERT INTO signal_infos VALUES(1);"
        )
        self.store = OperationStore(self.db)

    def test_exact_semantics_shared_program_and_null_name(self):
        original = example()
        marker = self.store.normalize(original)
        self.assertEqual(restore(self.db, marker["$legacy_operation"]), original)
        other = copy.deepcopy(original)
        other["record"] = 7
        other["name"] = "Control"
        self.store.normalize(other)
        self.assertEqual(
            self.db.execute(
                "SELECT count(*) FROM legacy_operation_programs"
            ).fetchone()[0],
            1,
        )
        self.assertEqual(
            self.db.execute("SELECT count(*) FROM legacy_operation_steps").fetchone()[
                0
            ],
            2,
        )
        self.assertEqual(original, example())

    def test_unknown_ranges_preserved_without_duplicate_base_facts(self):
        from tools.techstream.diag_legacy_unknown_fields import FIELDS, LENGTHS

        original = example()
        original["uninterpreted_bytes"] = {
            k: "ab" * n for k, n in zip(FIELDS["operation"], LENGTHS["operation"])
        }
        original["pattern"]["uninterpreted_bytes"] = {
            "14_17": "12345678",
            "22_23": "abcd",
        }
        first = self.store.normalize(original)
        self.assertEqual(restore(self.db, first["$legacy_operation"]), original)
        other = copy.deepcopy(original)
        other["uninterpreted_bytes"]["83"] = "12"
        second = self.store.normalize(other)
        self.assertNotEqual(first, second)
        self.assertEqual(restore(self.db, second["$legacy_operation"]), other)
        self.assertEqual(
            self.db.execute("SELECT count(*) FROM legacy_operation_defs").fetchone()[0],
            1,
        )
        bad = copy.deepcopy(original)
        bad["uninterpreted_bytes"]["future"] = "00"
        before = self.db.total_changes
        self.assertEqual(self.store.normalize(bad), bad)
        self.assertEqual(self.db.total_changes, before)

    def test_unknown_semantics_inline(self):
        original = example()
        original["new_safety_gate"] = "unknown"
        self.assertEqual(self.store.normalize(original), original)
        original = example()
        original["request_program"]["operations"][0]["condition"] = "unknown"
        self.assertEqual(self.store.normalize(original), original)

    def test_standalone_pattern_reuses_operation_definition_and_origin(self):
        operation = example()
        self.store.normalize(operation)
        row = dict(operation["pattern"], kind="active_test_pattern")
        marker = self.store.normalize(row)
        self.assertEqual(
            restore_pattern(self.db, marker["$legacy_operation_pattern"]), row
        )
        self.assertEqual(
            self.db.execute(
                "SELECT count(*) FROM legacy_operation_patterns"
            ).fetchone()[0],
            1,
        )
        self.assertEqual(
            self.db.execute(
                "SELECT count(*) FROM legacy_operation_pattern_entries"
            ).fetchone()[0],
            1,
        )
        row["future_field"] = True
        self.assertEqual(self.store.normalize(row), row)

    def test_missing_tail_rejected(self):
        identity = self.store.normalize(example())["$legacy_operation"]
        self.db.execute("DELETE FROM legacy_operation_steps WHERE position=1")
        with self.assertRaisesRegex(ValueError, "incomplete operation steps"):
            restore(self.db, identity)

    def test_missing_reference_rejected(self):
        identity = self.store.normalize(example())["$legacy_operation"]
        self.db.commit()
        self.db.execute("PRAGMA foreign_keys=OFF")
        self.db.execute("DELETE FROM legacy_operation_patterns")
        with self.assertRaisesRegex(ValueError, "missing legacy_operation_patterns"):
            restore(self.db, identity)


if __name__ == "__main__":
    unittest.main()
