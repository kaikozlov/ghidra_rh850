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

    def test_known_layout_covers_all_bytes_and_unknown_values_survive(self):
        from tools.techstream.diag_product_projection import project_document
        layouts = {
            5: (28, [(0, 12), (12, 16), (16, 20), (20, 22), (22, 24), (26, 27), (27, 28)],
                {"24_25": (24, 26)}),
            65: (68, [(0, 44), (44, 48), (48, 52), (52, 56), (56, 60),
                      (60, 62), (62, 64), (64, 65), (65, 66), (66, 67)],
                 {"67": (67, 68)}),
        }
        for table, (size, decoded, unknown) in layouts.items():
            occupied = [position for start, end in decoded + list(unknown.values())
                        for position in range(start, end)]
            self.assertEqual(sorted(occupied), list(range(size)))
            for nonzero in (False, True):
                raw = bytearray(size)
                for start, end in unknown.values():
                    raw[start:end] = bytes(range(start + 1, end + 1)) if nonzero else bytes(end - start)
                rows = dtc_source_catalog(NS(sections={table: section(table, raw)}),
                                          NS(get_string=lambda _: None), "fixture")
                expected = {key: raw[start:end].hex() for key, (start, end) in unknown.items()}
                self.assertEqual(rows[0]["uninterpreted_bytes"], expected)
                actual = project_document("catalogs/NA/1.json", {"dtc_source": rows})
                self.assertEqual(actual["dtc_source"][0]["uninterpreted_bytes"], expected)

    def test_wrong_stride_rejected(self):
        with self.assertRaises(ValueError):
            dtc_source_catalog(NS(sections={5:section(5,bytes(27))}),None,"ecu")
