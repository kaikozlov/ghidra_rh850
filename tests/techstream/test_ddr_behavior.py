import struct
import unittest
from types import SimpleNamespace
from tools.techstream.parse_ddb import Section, TableDataHead
from tools.techstream.gts.ddr_behavior import ddr_behavior_catalog


def section(table,rows):
    data=b"".join(rows)
    return Section(TableDataHead(table,0,len(rows),len(data)),0,data)


class DDRBehaviorTests(unittest.TestCase):
    def test_native_keys_fields_and_64bit_condition_are_preserved(self):
        code=bytearray(44)
        struct.pack_into("<II",code,12,1,2)
        struct.pack_into("<H",code,32,100)
        code[40:44]=bytes([3,4,0,1])
        signal=bytearray(72)
        struct.pack_into("<dd",signal,0,255.0,-1.0)
        struct.pack_into("<I",signal,32,3)
        struct.pack_into("<9H",signal,44,7,0,1,0,15,5,0,0,0x1234)
        signal[67]=1
        condition=bytearray(24)
        struct.pack_into("<Q4H",condition,0,0xFEDCBA9876543210,7,8,1,0)
        condition[17]=2
        physical=bytearray(24)
        struct.pack_into("<iiiHH",physical,0,1,1,0,1,0)
        physical[20]=3
        db=SimpleNamespace(sections={133:section(133,[code]),134:section(134,[signal,signal]),
            135:section(135,[condition]),13:section(13,[physical]),15:section(15,[bytes(8)])})
        out=ddr_behavior_catalog(db,SimpleNamespace(get_string=lambda n:{1:"Code",2:"Memo",3:"Signal"}.get(n)),"fixture")
        self.assertEqual(out["codes"][0]["trigger_selector_1"],4)
        self.assertEqual(len(out["signals"]),2)
        self.assertEqual(out["signals"][0]["invalid_condition_records"],[0])
        self.assertEqual(out["signals"][0]["did"],0x1234)
        self.assertEqual(out["signals"][0]["signal_info"]["sign_mode"],3)
        self.assertEqual(out["signals"][0]["data_min"],-1.0)
        self.assertTrue(out["signals"][0]["live_list_member"])
        self.assertEqual(out["invalid_conditions"][0]["comparison_bits64"],0xFEDCBA9876543210)
        self.assertEqual(out["invalid_conditions"][0]["comparison"],"not_equal_bits64")

    def test_unknown_layout_rejected(self):
        with self.assertRaises(ValueError):
            ddr_behavior_catalog(SimpleNamespace(sections={135:section(135,[bytes(23)])}),None,"fixture")


if __name__=="__main__":
    unittest.main()
