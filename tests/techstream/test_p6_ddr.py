import struct
import unittest
from types import SimpleNamespace
from tools.techstream.parse_ddb import Section, TableDataHead
from tools.techstream.gts.p6_ddr import p6_ddr_catalog


def section(table, rows):
    payload = b"".join(rows)
    return Section(TableDataHead(table, 0, len(rows), len(payload)), 0, payload)


class P6DDRTests(unittest.TestCase):
    def test_native_fields_and_one_to_many_joins(self):
        trigger = bytearray(20)
        struct.pack_into("<IIIHH", trigger, 0, 0x6E0000, 1, 2, 3, 4)
        trigger[16:] = bytes([5, 6, 1, 7])
        did = struct.pack("<HHHBB", 0x1402, 12, 8, 1, 9)
        signal = bytearray(40)
        struct.pack_into("<ddI7HH4B", signal, 0, 2.0, 3.0, 3, 0x1402, 10, 8, 15, 20, 4, 0, 11, 1, 0, 2, 12)
        condition = struct.pack("<I4H4B", 0xFFFF, 10, 11, 2, 13, 1, 2, 14, 0)
        earlier = bytearray(condition)
        struct.pack_into("<H", earlier, 8, 1)
        physical = bytearray(24)
        struct.pack_into("<iiiHH", physical, 0, 2, 3, -4, 4, 5)
        physical[20:22] = bytes([3, 1])
        unit = struct.pack("<IHH", 4, 5, 0)
        db = SimpleNamespace(sections={
            165: section(165, [trigger]), 166: section(166, [did, did]),
            167: section(167, [signal]), 168: section(168, [condition, earlier]),
            13: section(13, [physical]), 15: section(15, [unit]),
        })
        strings = SimpleNamespace(get_string=lambda n: {1:"Trigger",2:"Memo",3:"Signal",4:"km/h"}.get(n))
        out = p6_ddr_catalog(db, strings, "fixture")
        row = out["signals"][0]
        self.assertEqual(row["name"], "Signal")
        self.assertEqual(row["data_id_records"], [0, 1])
        self.assertEqual(row["invalid_condition_records"], [1, 0])
        self.assertEqual(row["signal_info"]["sign_mode"], 3)
        self.assertNotIn("signed", row["signal_info"])
        self.assertEqual(row["signal_info"]["unit"], "km/h")
        self.assertEqual(row["signal_info"]["bit_width"], 8)
        self.assertEqual(out["triggers"][0]["dtc_identifier"], 0x6E0000)
        self.assertEqual(out["triggers"][0]["trigger_memo"], "Memo")
        self.assertEqual(out["invalid_conditions"][0]["comparison"], "not_equal")
        self.assertEqual(row["raw"], signal)
        self.assertEqual(out["data_ids"][0]["validity_mode"], 1)

    def test_missing_join_is_not_fabricated(self):
        raw = bytearray(40)
        struct.pack_into("<7H", raw, 20, 0x1410, 1, 0, 7, 1, 99, 0)
        result = p6_ddr_catalog(SimpleNamespace(sections={167: section(167, [raw])}),
                                SimpleNamespace(get_string=lambda n: None), "fixture")
        row = result["signals"][0]
        self.assertIsNone(row["signal_info"])
        self.assertEqual(row["data_id_records"], [])
        self.assertEqual(row["invalid_condition_records"], [])

    def test_invalid_condition_retains_last_byte(self):
        for value in (0, 0xa5):
            raw = bytes(15) + bytes([value])
            db = SimpleNamespace(sections={168:section(168,[raw])})
            row = p6_ddr_catalog(db, None, "fixture")["invalid_conditions"][0]
            self.assertEqual(row["uninterpreted_bytes"], {"15":raw[15:].hex()})
            from tools.techstream.diag_product_projection import project_document
            product = project_document("catalogs/NA/1.json", {"ddr":{"invalid_conditions":[row]}})
            self.assertEqual(product["ddr"]["invalid_conditions"][0]["uninterpreted_bytes"],
                             row["uninterpreted_bytes"])

    def test_unknown_layout_rejected(self):
        with self.assertRaises(ValueError):
            p6_ddr_catalog(SimpleNamespace(sections={165:section(165,[bytes(19)])}), None, "fixture")


if __name__ == "__main__":
    unittest.main()
