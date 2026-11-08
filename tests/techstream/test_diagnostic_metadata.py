import struct
import unittest
from types import SimpleNamespace
from tools.techstream.gts.diagnostic_metadata import diagnostic_metadata
from tools.techstream.parse_ddb import Section, TableDataHead


class DiagnosticMetadataTests(unittest.TestCase):
    def test_detail_highlight_and_expanded_names(self):
        def section(table, rows):
            b = b"".join(rows)
            return Section(TableDataHead(table, 0, len(rows), len(b)), 0, b)
        detail = struct.pack("<IIHHHHBBBB", 277, 0, 0x69, 200, 3, 12, 1, 1, 0, 0)
        highlight = struct.pack("<HHBBBB", 3, 511, 1, 0, 0, 0)
        expanded = bytearray(36)
        expanded[:20] = "THC_D001".encode("utf-16le").ljust(20, b"\0")
        struct.pack_into("<IIIHBB", expanded, 20, 0xA4001, 100, 101, 13, 1, 2)
        db = SimpleNamespace(sections={47: section(47, [detail]),
                                      48: section(48, [highlight, highlight]),
                                      49: section(49, [expanded]),
                                      40: section(40, [bytes.fromhex("0100000000000f02")])})
        c = diagnostic_metadata(db, SimpleNamespace(get_string=lambda key: str(key)), "fixture")
        self.assertEqual(c["details"][0]["highlight_records"], [0, 1])
        self.assertEqual(c["details"][0]["dtc_identifier"], 0x69)
        self.assertEqual(c["highlights"][0]["monitor_key"], 511)
        self.assertEqual(c["expanded_dtcs"][0]["packed_dtc"], 0xA4001)
        self.assertEqual(c["expanded_dtcs"][0]["description"], "100")
        self.assertEqual(c["pending_freeze"][0]["freeze_frame_number"], 15)


if __name__ == "__main__":
    unittest.main()
