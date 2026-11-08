import json
import struct
import unittest
from types import SimpleNamespace as NS
from tools.techstream.gts.active_test_support import (
    active_test_support_catalog, condition_supported, panel_supported, match_variable_pattern,
)


def section(table, *rows):
    return NS(header=NS(table_type=table,record_count=len(rows)),
              decoded_record_size=len(rows[0]),decoded_data=b"".join(rows),
              iter_records=lambda: iter(NS(raw=bytes(r)) for r in rows))


def variable(data, index=1):
    return {"index":index,"resolved":True,"bytes":data.hex(),"length":len(data)}


class ActiveSupportTests(unittest.TestCase):
    def test_source_rows_and_variable_namespaces(self):
        bit=bytearray(12)
        struct.pack_into("<HHHHHBB",bit,0,3,11,4,4,11,1,7)
        panel=bytearray(16)
        struct.pack_into("<HHHHHH",panel,0,5,0x1234,2,12,13,7)
        panel[13:15]=bytes([3,1])
        status=struct.pack("<6H",9,14,1,8,0,0)
        display=bytearray(20)
        struct.pack_into("<I7HBB",display,0,100,2,1,3,15,16,5,0,0,1)
        description=bytearray(20)
        struct.pack_into("<I5H",description,0,101,2,15,1,16,4)
        db=NS(sections={69:section(69,bit),142:section(142,bit),70:section(70,panel),
            72:section(72,status),73:section(73,display,display),
            79:section(79,display),78:section(78,description)})
        values={11:b"\x12\x34",12:b"\xff",13:b"\x02",14:b"\x05",15:b"\x01",16:b"\x00"}
        result=active_test_support_catalog(db,NS(get_string=lambda i:f"text{i}"),"ecu",
            resolve_variable=values.__getitem__,variable_namespace="master:NA")
        json.dumps(result)
        self.assertEqual(len(result["display_patterns"]),2)
        self.assertEqual(result["display_patterns"][1]["record"],1)
        self.assertEqual(result["support_conditions"][0]["did"],0x1234)
        self.assertEqual(result["routine_support_conditions"][0]["table"],142)
        self.assertEqual(result["description_patterns"][0]["description_id"],101)
        self.assertEqual(result["panel_support"][0]["mask"]["namespace"],"master:NA")
        self.assertEqual(result["routine_status"][0]["pattern"]["bytes"],"05")

    def test_msb0_cross_byte_condition(self):
        cond={"condition_type":7,"did_variable":variable(b"\x12\x34"),"bit_start":4,"bit_end":11}
        self.assertTrue(condition_supported(bytes.fromhex("0800"),cond))
        self.assertTrue(condition_supported(bytes.fromhex("0080"),cond))
        self.assertFalse(condition_supported(bytes.fromhex("f00f"),cond))
        with self.assertRaises(ValueError): condition_supported(b"",cond)
        cond["condition_type"]=1
        with self.assertRaises(ValueError): condition_supported(b"\xff\xff",cond)

    def test_panel_lexicographic_mask_and_modes(self):
        p={"mask":variable(bytes.fromhex("f00f")),"reference":variable(bytes.fromhex("8002")),
           "payload_byte_offset":1}
        for mode,expected in ((1,False),(2,True),(3,True),(4,False),(5,True),(6,False)):
            p["comparison_mode"]=mode
            self.assertEqual(panel_supported(bytes.fromhex("009001"),p),expected)
        for mode,expected in ((1,True),(2,False),(3,True),(4,True),(5,False),(6,False)):
            p["comparison_mode"]=mode
            self.assertEqual(panel_supported(bytes.fromhex("008ff2"),p),expected)
        self.assertFalse(panel_supported(b"",p))
        self.assertTrue(panel_supported(b"",None,panel_mode=1))
        self.assertFalse(panel_supported(b"",None,panel_mode=2))

    def test_exact_pattern_first_match(self):
        rows=[{"record":0,"pattern":variable(b"\x01")},{"record":1,"pattern":variable(b"\x01")}]
        self.assertEqual(match_variable_pattern(b"\x01",rows)["record"],0)
        self.assertIsNone(match_variable_pattern(b"\x01\x00",rows))

    def test_unresolved_stays_explicit_and_bad_stride_rejected(self):
        row=struct.pack("<6H",1,2,1,0,0,0)
        db=NS(sections={72:section(72,row)})
        result=active_test_support_catalog(db,None,"ecu")
        self.assertFalse(result["routine_status"][0]["pattern"]["resolved"])
        with self.assertRaises(ValueError):match_variable_pattern(b"",result["routine_status"])
        db.sections[72].decoded_record_size=10
        with self.assertRaises(ValueError):active_test_support_catalog(db,None,"ecu")
