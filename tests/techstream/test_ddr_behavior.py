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

    def test_original_identifier_and_unknown_bytes_survive_product_projection(self):
        from tools.techstream.diag_product_projection import project_document

        invalid = bytes.fromhex("00d8") + bytes(10)
        embedded = ("D" + chr(0) + "TAIL").encode("utf-16-le")
        cases = [
            (("D2815" + chr(0)).encode("utf-16-le"), {"identifier": "D2815"}),
            ("D2815X".encode("utf-16-le"), {"identifier": "D2815X"}),
            (bytes(12), {"identifier": ""}),
            (invalid, {"uninterpreted_identifier_bytes": invalid.hex()}),
            (embedded, {"uninterpreted_identifier_bytes": embedded.hex()}),
        ]
        for prefix, expected in cases:
            with self.subTest(prefix=prefix):
                raw = prefix + bytes(32)
                db = SimpleNamespace(sections={133: section(133, [raw])})
                decoded = ddr_behavior_catalog(
                    db, SimpleNamespace(get_string=lambda _: None), "fixture"
                )
                product = project_document("catalogs/NA/1.json", {"ddr_behavior": decoded})
                for key, value in expected.items():
                    self.assertEqual(decoded["codes"][0][key], value)
                    self.assertEqual(product["ddr_behavior"]["codes"][0][key], value)
                self.assertNotIn("raw", product["ddr_behavior"]["codes"][0])

    def test_all_uninterpreted_ranges_preserved_without_overlap(self):
        from tools.techstream.diag_product_projection import project_document

        # Exclusive-end ranges, independently enumerated against the decoder.
        layouts = {
            133: (44, "codes", [(0, 36), (40, 42), (43, 44)],
                  {"36_39": (36, 40), "42": (42, 43)}),
            134: (72, "signals", [(0, 16), (20, 28), (32, 36), (44, 64), (66, 68)],
                  {"16_19": (16, 20), "28_31": (28, 32), "36_43": (36, 44),
                   "64_65": (64, 66), "68_71": (68, 72)}),
            135: (24, "invalid_conditions", [(0, 19)], {"19_23": (19, 24)}),
        }
        for table, (size, collection, decoded, unknown) in layouts.items():
            occupied = []
            for start, end in decoded + list(unknown.values()):
                occupied.extend(range(start, end))
            self.assertEqual(sorted(occupied), list(range(size)), table)
            for nonzero in (False, True):
                raw = bytearray(size)
                for start, end in unknown.values():
                    raw[start:end] = bytes(range(start + 1, end + 1)) if nonzero else bytes(end - start)
                db = SimpleNamespace(sections={table: section(table, [raw])})
                result = ddr_behavior_catalog(db, SimpleNamespace(get_string=lambda _: None), "fixture")
                product = project_document("catalogs/NA/1.json", {"ddr_behavior": result})
                fields = product["ddr_behavior"][collection][0]["uninterpreted_bytes"]
                self.assertEqual(fields, {key: raw[start:end].hex() for key, (start, end) in unknown.items()})

    def test_unknown_layout_rejected(self):
        with self.assertRaises(ValueError):
            ddr_behavior_catalog(SimpleNamespace(sections={135:section(135,[bytes(23)])}),None,"fixture")


if __name__=="__main__":
    unittest.main()
