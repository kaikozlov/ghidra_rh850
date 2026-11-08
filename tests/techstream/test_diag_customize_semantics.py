import sqlite3
import unittest

from tools.techstream.diag_customize_semantics import (
    CHOICE,
    EXECUTOR,
    ITEM,
    SCHEMA,
    TEXT,
    Reader,
    Writer,
)


class CustomizeSemanticsTests(unittest.TestCase):
    def setUp(self):
        self.db = sqlite3.connect(":memory:")
        self.db.execute(
            "CREATE TABLE text_values(id INTEGER PRIMARY KEY,value TEXT UNIQUE)"
        )
        self.db.executescript(SCHEMA)
        self.writer = Writer(self.db)
        self.reader = Reader(self.db)

    def item(self):
        row = {k: ("" if k in TEXT else 0) for k in ITEM}
        row["raw_u32_24"] = 4294967295
        choice = {k: (None if k in TEXT else 0) for k in CHOICE}
        row["choices"] = [choice, dict(choice)]
        return row

    def test_exact_order_optional_and_missing(self):
        row = self.item()
        id = self.writer.item(row)
        self.assertEqual(row, self.reader.read("$customize_item", id))
        row["modern_executor"] = {k: k for k in EXECUTOR}
        self.assertEqual(
            row, self.reader.read("$customize_item", self.writer.item(row))
        )
        self.db.execute("DELETE FROM customize_choice_members WHERE position=1")
        with self.assertRaisesRegex(ValueError, "incomplete"):
            self.reader.read("$customize_item", id)

    def test_future_and_invalid_preserved(self):
        for key, value in [
            ("target_resolution_status", 3),
            ("raw_u32_24", False),
            ("raw_u32_24", 1.2),
        ]:
            row = self.item()
            row[key] = value
            self.assertEqual({"items": [row]}, self.writer.transform({"items": [row]}))

    def test_empty_choices_and_missing_definition(self):
        row = self.item()
        row["choices"] = []
        self.assertEqual(
            row, self.reader.read("$customize_item", self.writer.item(row))
        )
        with self.assertRaises(ValueError):
            self.reader.read("$customize_item", 999)


if __name__ == "__main__":
    unittest.main()
