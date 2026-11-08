"""Synthetic table-contract regression tests; no proprietary fixture required."""
import struct
import unittest
from types import SimpleNamespace as NS

from tools.techstream.gts.p6_catalog import p6_catalog


def section(table, *rows):
    return NS(header=NS(table_type=table, record_count=len(rows)),
              decoded_record_size=len(rows[0]), decoded_data=b"".join(rows),
              iter_records=lambda: iter(NS(raw=bytes(row)) for row in rows))


def monitor(flags=3, did=0x1234):
    raw = bytearray(80)
    struct.pack_into("<I", raw, 0x28, 1)
    struct.pack_into("<I", raw, 0x30, flags)
    for off, val in ((0x34, 42), (0x3A, 7), (0x3E, 7), (0x46, did), (0x48, 0x9001)):
        struct.pack_into("<H", raw, off, val)
    raw[0x4A] = 2
    return raw


class P6CatalogTest(unittest.TestCase):
    def project(self, sections):
        return p6_catalog(NS(sections=sections), NS(get_string=lambda key: f"text{key}"),
                          "fixture", resolve_variable=lambda key: b"\x12\x34")

    def test_monitor_tables_are_not_union_and_flags_are_preserved(self):
        phy = bytearray(24)
        struct.pack_into("<iiiHH", phy, 0, 1, 1, 0, 7, 0)
        phy[20] = 2
        raw = monitor(0x103)
        result = self.project({62: section(62, raw, raw), 157: section(157, monitor()),
                               13: section(13, phy)})
        self.assertEqual(result["data_list"]["row_count"], 2)
        self.assertEqual(len(result["generic_ffd"]["signals"]), 2)
        signal = result["dids"]["0x1234"][0]
        self.assertEqual(signal["decoder"], "p6-native-msb0-u32-v1")
        self.assertEqual(signal["sign_mode"], 2)
        self.assertNotIn("signed", signal)
        self.assertEqual(signal["flags"], 0x103)

    def test_composite_stays_catalogued_but_not_wire_did(self):
        result = self.project({62: section(62, monitor(0x19))})
        self.assertEqual(result["dids"], {})
        self.assertEqual(result["generic_ffd"]["signals"], [])
        self.assertFalse(result["data_list"]["rows"][0]["wire_field"])

    def test_rob_uses_164_and_support_90_not_p5_or_151(self):
        raw = bytearray(48)
        struct.pack_into("<7H", raw, 20, 3, 0, 0, 8, 87, 1, 0)
        struct.pack_into("<H", raw, 36, 0xA802)
        support = bytearray(8)
        struct.pack_into("<HH", support, 2, 0xA802, 11)
        result = self.project({164: section(164, raw), 90: section(90, support),
                               151: section(151, bytes(8))})
        signal = result["rob"]["signals"][0]
        self.assertEqual(signal["bit_end"], 87)
        self.assertEqual(signal["did_support"]["fixed_length"], 11)
        self.assertEqual(signal["did_support"]["table"], 90)

    def test_all_rob_source_metadata_including_disabled_and_duplicates(self):
        code=bytearray(68)
        code[:6]="ABC".encode("utf-16le")
        struct.pack_into("<IIIIH",code,44,123,1,2,3,7)
        code[62:65]=bytes([0,2,5])
        signal=bytearray(48)
        struct.pack_into("<H",signal,34,9)
        signal[42]=6
        result=self.project({163:section(163,code,code),164:section(164,signal,signal)})["rob"]
        self.assertEqual(len(result["behavior_codes"]),2)
        self.assertEqual(len(result["signals"]),2)
        row=result["behavior_codes"][1]
        self.assertEqual((row["record"],row["enabled"],row["exception_handler_id"],row["exception_handler_flag"]),(1,0,7,5))
        self.assertEqual(row["comment_string_index"],3)
        self.assertEqual(row["raw"],code.hex())
        self.assertEqual(result["signals"][0]["exception_handler_id"],9)
        self.assertEqual(result["signals"][0]["exception_handler_flag"],6)
        self.assertEqual(result["signals"][0]["raw"],signal.hex())

    def test_condition_layouts_are_distinct(self):
        raw = monitor()
        struct.pack_into("<HH", raw, 0x36, 2, 3)
        live = bytearray(16)
        struct.pack_into("<HH", live, 0, 2, 1)
        struct.pack_into("<H", live, 10, 256)
        live[13:15] = bytes((4, 5))
        ffd = bytearray(12)
        struct.pack_into("<HH", ffd, 0, 3, 1)
        ffd[11] = 7
        result = self.project({62: section(62, raw), 63: section(63, live), 80: section(80, ffd)})
        self.assertEqual(result["data_list"]["rows"][0]["support_condition"]["condition_type"], 4)
        self.assertEqual(result["generic_ffd"]["signals"][0]["support_condition"]["condition_type"], 7)

    def test_duplicate_support_rows_are_preserved(self):
        first = bytearray(8)
        struct.pack_into("<HH", first, 2, 0x1234, 2)
        second = bytearray(first)
        struct.pack_into("<H", second, 4, 4)
        result = self.project({62: section(62, monitor()), 61: section(61, first, second)})
        support = result["data_list"]["rows"][0]["did_support"]
        self.assertEqual(support["fixed_length"], 2)
        self.assertEqual(support["additional_records"][0]["fixed_length"], 4)

    def test_short_monitor_fails_instead_of_silent_misdecode(self):
        with self.assertRaisesRegex(ValueError, "table 62"):
            self.project({62: section(62, bytes(64))})


if __name__ == "__main__":
    unittest.main()
