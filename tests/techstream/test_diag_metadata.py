import sqlite3
import unittest
from unittest.mock import patch

from tools.techstream.diag_metadata import READERS, restore


class ProductReferenceTests(unittest.TestCase):
    def setUp(self):
        self.db = sqlite3.connect(":memory:")

    def test_rejects_unknown_and_removed_research_markers(self):
        for marker in (
            "$metadata",
            "$native_record",
            "$physical",
            "$plugin_query",
            "$future",
        ):
            with (
                self.subTest(marker=marker),
                self.assertRaisesRegex(ValueError, "unknown product reference"),
            ):
                restore(self.db, {marker: 1})

    def test_independent_outputs_and_single_lookup(self):
        calls = []

        def reader(db, identity):
            calls.append(identity)
            return {"rows": [{"value": 7}]}

        with patch.dict(READERS, {"$signal_info": reader}):
            out = restore(self.db, [{"$signal_info": 1}, {"$signal_info": 1}])
        self.assertEqual(calls, [1])
        out[0]["rows"][0]["value"] = 99
        self.assertEqual(out[1]["rows"][0]["value"], 7)

    def test_cycles_and_marker_validation(self):
        with patch.dict(
            READERS, {"$signal_info": lambda db, identity: {"$signal_info": identity}}
        ):
            with self.assertRaisesRegex(ValueError, "cyclic"):
                restore(self.db, {"$signal_info": 1})
        for value in (
            {"$signal_info": True},
            {"$signal_info": 0},
            {"$signal_info": 1, "other": 2},
        ):
            with self.assertRaisesRegex(ValueError, "invalid"):
                restore(self.db, value)

    def test_part_owned_by_document_reader(self):
        self.assertEqual(
            restore(self.db, {"part": {"$part": 2}}), {"part": {"$part": 2}}
        )
        with self.assertRaisesRegex(ValueError, "invalid"):
            restore(self.db, {"$part": -1})


if __name__ == "__main__":
    unittest.main()
