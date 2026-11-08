import struct
import unittest
from types import SimpleNamespace

from tools.techstream.gts.physical_catalog import physical_catalog
from tools.techstream.parse_ddb import Section, TableDataHead


class PhysicalCatalogTests(unittest.TestCase):
    def test_unreferenced_and_duplicate_definitions_are_retained(self):
        phy = struct.pack("<iiiHHHHBBBB", 2, 3, -4, 7, 9, 11, 0, 3, 2, 1, 0)
        pattern = bytearray(24)
        struct.pack_into("<Ii", pattern, 0, 44, -1)
        struct.pack_into("<HH", pattern, 12, 17, 0)
        struct.pack_into("<H", pattern, 16, 12)
        pattern[23] = 2
        unit = struct.pack("<IHHHBB", 45, 9, 5, 13, 1, 0)
        def section(table, rows):
            raw = b"".join(rows)
            return Section(TableDataHead(table, 0, len(rows), len(raw)), 0, raw)
        db = SimpleNamespace(sections={13: section(13, [phy, phy]),
                                      14: section(14, [pattern]),
                                      15: section(15, [unit])})
        result = physical_catalog(db, SimpleNamespace(get_string=lambda key: str(key)), "fixture")
        self.assertEqual(len(result["physical"]), 2)
        self.assertEqual(result["physical"][0]["sign_mode"], 3)
        self.assertEqual(result["physical"][1]["record"], 1)
        self.assertEqual(result["patterns"][0]["value"], -1)
        self.assertEqual(result["patterns"][0]["exception_handler_flag"], 2)
        self.assertEqual(result["units"][0]["genre_id"], 5)
        self.assertEqual(result["units"][0]["name"], "45")


if __name__ == "__main__":
    unittest.main()
