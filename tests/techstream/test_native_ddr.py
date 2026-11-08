import struct
import unittest
from types import SimpleNamespace
from tools.techstream.parse_ddb import Section, TableDataHead
from tools.techstream.gts.native_ddr import native_ddr_catalog


def section(table, rows):
    data = b"".join(rows)
    return Section(TableDataHead(table, 0, len(rows), len(data)), 0, data)


class NativeDDRTests(unittest.TestCase):
    def test_alias_keys_remain_family_scoped_and_duplicates_survive(self):
        monitor = bytearray(48)
        struct.pack_into("<I", monitor, 20, 123)
        struct.pack_into("<9H", monitor, 24, 7, 1, 0, 7, 0, 7, 10, 0, 0)
        address = struct.pack("<I3H6B", 0x1000, 7, 1, 0, 2, 1, 0, 0, 0, 0)
        condition = struct.pack("<I4H4B", 255, 7, 7, 1, 0, 0, 1, 0, 0)
        db = SimpleNamespace(sections={
            50: section(50,[monitor,monitor]),52:section(52,[address]),
            53: section(53,[condition]),82:section(82,[monitor]),84:section(84,[address]),
            108:section(108,[struct.pack("<3H2B",0x100,2,0,0,0)]),
            109:section(109,[struct.pack("<4H4B",0x100,0x101,4,0,2,0,0,0)]),
        })
        result = native_ddr_catalog(db,SimpleNamespace(get_string=lambda n:"Name"),"fixture")
        self.assertEqual(len(result["monitors"]),3)
        self.assertEqual(result["addresses"][0]["monitor_records"],[{"table":50,"record":0},{"table":50,"record":1}])
        self.assertEqual(result["addresses"][1]["monitor_records"],[{"table":82,"record":0}])
        self.assertEqual(result["monitors"][2]["invalid_condition_records"],[])
        self.assertEqual(result["monitors"][0]["invalid_condition_records"],[{"table":53,"record":0}])
        self.assertEqual(result["case_data_ids"][0]["case_did"],0x101)
        self.assertEqual(result["case_data_ids"][0]["family"],"native-ddr-110")

    def test_every_alias_covers_all_bytes_and_preserves_unknown_fields(self):
        from tools.techstream.gts.native_ddr import MONITOR_TABLES, HEADER_TABLES
        from tools.techstream.diag_product_projection import project_document
        layouts = [
            ("monitors", MONITOR_TABLES, 48, [(0, 8), (12, 42), (44, 46)],
             {"8_11": (8, 12), "42_43": (42, 44), "46_47": (46, 48)}),
            ("triggers", [t + 1 for t in MONITOR_TABLES], 36, [(0, 33)],
             {"33_35": (33, 36)}),
            ("addresses", [t + 2 for t in MONITOR_TABLES], 16, [(0, 13)],
             {"13_15": (13, 16)}),
            ("invalid_conditions", [t + 3 for t in MONITOR_TABLES], 16, [(0, 15)],
             {"15": (15, 16)}),
            ("header_data_ids", HEADER_TABLES, 8, [(0, 7)], {"7": (7, 8)}),
            ("case_data_ids", [t + 1 for t in HEADER_TABLES], 12, [(0, 9), (10, 11)],
             {"9": (9, 10), "11": (11, 12)}),
        ]
        for field, tables, size, known, unknown in layouts:
            occupied = [i for start, end in known + list(unknown.values()) for i in range(start, end)]
            self.assertEqual(sorted(occupied), list(range(size)))
            for table in tables:
                for nonzero in (False, True):
                    raw = bytearray(size)
                    for start, end in unknown.values():
                        raw[start:end] = bytes(range(start + 1, end + 1)) if nonzero else bytes(end - start)
                    db = SimpleNamespace(sections={table: section(table, [raw])})
                    result = native_ddr_catalog(db, SimpleNamespace(get_string=lambda _: None), "fixture")
                    expected = {k: raw[start:end].hex() for k, (start, end) in unknown.items()}
                    self.assertEqual(result[field][0]["uninterpreted_bytes"], expected)
                    product = project_document("catalogs/NA/1.json", {"native_ddr": result})
                    self.assertEqual(product["native_ddr"][field][0]["uninterpreted_bytes"], expected)

    def test_unknown_class_layout_rejected(self):
        with self.assertRaises(ValueError):
            native_ddr_catalog(SimpleNamespace(sections={50:section(50,[bytes(47)])}),None,"fixture")


if __name__=="__main__":
    unittest.main()
