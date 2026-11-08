import sqlite3
import unittest

from tools.techstream.diag_work_semantics import (
    FACTOR,
    HELP,
    PATTERN,
    SCHEMA,
    STANDARD,
    TEXT,
    Reader,
    Writer,
)


class WorkSemanticsTest(unittest.TestCase):
    def setUp(self):
        self.db = sqlite3.connect(":memory:")
        self.db.execute("PRAGMA foreign_keys=ON")
        self.db.executescript(
            "CREATE TABLE text_values(id INTEGER PRIMARY KEY,value TEXT UNIQUE);"
            + SCHEMA
        )
        self.w = Writer(self.db)
        self.r = Reader(self.db)

    def fields(self, keys):
        return {
            k: None if k in TEXT else False if k == "translation_available" else 0
            for k in keys
        }

    def test_all_shapes_shared_help_and_null_labels(self):
        help = self.fields(HELP)
        help["text"] = "not available"
        standard = self.fields(STANDARD)
        standard["standard_value_status"] = "unresolved"
        standard["standard_value_help_records"] = [help]
        a = self.w.definition(standard, "$work_standard")
        second = dict(standard, record=1)
        b = self.w.definition(second, "$work_standard")
        self.assertEqual(self.r.read("$work_standard", a), standard)
        self.assertEqual(self.r.read("$work_standard", b), second)
        self.assertEqual(
            self.db.execute("SELECT count(*) FROM work_help_definitions").fetchone()[0],
            1,
        )
        for marker, fields in (
            ("$work_pattern", PATTERN),
            ("$work_factor_definition", FACTOR),
        ):
            row = self.fields(fields)
            row["value"] = 9007199254740993
            row["name"] = ""
            id = self.w.definition(row, marker)
            self.assertEqual(self.r.read(marker, id), row)

    def test_unknown_or_multi_help_preserved(self):
        standard = self.fields(STANDARD)
        standard["standard_value_help_records"] = []
        for row in (
            dict(standard, future_state="unknown"),
            dict(standard, signal_id=False),
            dict(standard, standard_value_help_records=[self.fields(HELP)] * 2),
        ):
            root = {"work_factor": {"standard_info": [row]}}
            self.assertEqual(self.w.transform(root), root)

    def test_unknown_bytes_presence_nonzero_and_variants(self):
        from tools.techstream.diag_work_semantics import UNKNOWN

        for marker, fields in (
            ("$work_standard", STANDARD),
            ("$work_pattern", PATTERN),
            ("$work_factor_definition", FACTOR),
        ):
            row = self.fields(fields)
            if marker == "$work_standard":
                help = self.fields(HELP)
                help["uninterpreted_bytes"] = {"10": "ff12"}
                row["standard_value_help_records"] = [help]
            absent = self.w.definition(row, marker)
            row["uninterpreted_bytes"] = {
                key: "ff" * width for key, width in UNKNOWN[marker]
            }
            present = self.w.definition(row, marker)
            self.assertNotEqual(absent, present)
            self.assertEqual(self.r.read(marker, present), row)
            self.assertNotIn("uninterpreted_bytes", self.r.read(marker, absent))

    def test_malformed_unknown_preserved_and_corrupt_rejected(self):
        row = self.fields(STANDARD)
        row["standard_value_help_records"] = []
        for unknown in ({"11": "ffff"}, {"11": "FF"}, {"future": "00"}, None):
            value = dict(row, uninterpreted_bytes=unknown)
            with self.assertRaises(ValueError):
                self.w.definition(value, "$work_standard")
        row["uninterpreted_bytes"] = {"11": "ff"}
        id = self.w.definition(row, "$work_standard")
        self.db.execute(
            "UPDATE work_standard_definitions SET unknown_bytes=x'ffff' WHERE id=?",
            (id,),
        )
        with self.assertRaises(ValueError):
            self.r.read("$work_standard", id)

    def test_empty_help_and_missing_reference(self):
        row = self.fields(STANDARD)
        row["standard_value_help_records"] = []
        id = self.w.definition(row, "$work_standard")
        self.assertEqual(self.r.read("$work_standard", id), row)
        with self.assertRaisesRegex(ValueError, "missing"):
            self.r.read("$work_pattern", 999)
