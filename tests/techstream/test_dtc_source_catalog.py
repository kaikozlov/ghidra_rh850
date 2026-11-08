import struct
import unittest
from types import SimpleNamespace as NS
from tools.techstream.gts.dtc_source_catalog import dtc_source_catalog


def section(table,*rows):
    return NS(header=NS(table_type=table,record_count=len(rows)),
              decoded_record_size=len(rows[0]),decoded_data=b"".join(rows),
              iter_records=lambda:iter(NS(raw=bytes(r)) for r in rows))


class DtcSourceTests(unittest.TestCase):
    def test_legacy_detail_lookup_enable_and_exception(self):
        raw=bytearray(28);raw[:10]="P0123".encode("utf-16le")
        struct.pack_into("<IIHH",raw,12,100,101,0x123,17)
        raw[26:28]=bytes([2,3])
        rows=dtc_source_catalog(NS(sections={5:section(5,raw)}),NS(get_string=lambda x:f"s{x}"),"ecu")
        self.assertEqual(rows[0]["detail_lookup_key"],0x123)
        self.assertEqual(rows[0]["comment"],"s101")
        self.assertEqual(rows[0]["exception_handler_id"],17)
        self.assertTrue(rows[0]["enabled"])
        self.assertEqual(rows[0]["enabled_value"],2)

    def test_p5_enabled_is_byte_not_old_tail_word(self):
        raw=bytearray(68);raw[:14]="P012345".encode("utf-16le")
        struct.pack_into("<IIIIHH",raw,44,0x12345,100,101,102,17,19)
        raw[64:67]=bytes([0,8,9])
        rows=dtc_source_catalog(NS(sections={65:section(65,raw,raw)}),NS(get_string=lambda x:f"s{x}"),"ecu")
        self.assertEqual(len(rows),2)
        r=rows[1];self.assertEqual(r["record"],1);self.assertFalse(r["enabled"])
        self.assertEqual((r["base_dtc"],r["failure_type"]),(0x123,0x45))
        self.assertEqual((r["failure_description"],r["comment"]),("s101","s102"))
        self.assertEqual(r["exception_handler_flag"],9)
        self.assertEqual([f["value"] for f in r["diag_code_info_fields"]],[8,19])

    def test_wrong_stride_rejected(self):
        with self.assertRaises(ValueError):
            dtc_source_catalog(NS(sections={5:section(5,bytes(27))}),None,"ecu")
