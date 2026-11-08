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

    def test_unknown_class_layout_rejected(self):
        with self.assertRaises(ValueError):
            native_ddr_catalog(SimpleNamespace(sections={50:section(50,[bytes(47)])}),None,"fixture")


if __name__=="__main__":
    unittest.main()
