import struct
import unittest
from types import SimpleNamespace as NS

from tools.techstream.gts.legacy_freeze import decode_legacy_scalar, extract_legacy_scalar, legacy_freeze_rows


def section(*rows):
    return NS(iter_records=lambda: iter(NS(raw=bytes(row)) for row in rows))


class LegacyFreezeTest(unittest.TestCase):
    def test_physical_and_condition_joins(self):
        row = bytearray(104)
        row[:4] = "RPM".encode("utf-16le")[:4]
        struct.pack_into("<dd", row, 24, 9000.0, 0.0)
        struct.pack_into("<I", row, 0x44, 11)
        for off, val in ((0x4C, 42), (0x4E, 9), (0x50, 7), (0x52, 8),
                         (0x54, 23), (0x58, 3), (0x5A, 12), (0x5C, 55)):
            struct.pack_into("<H", row, off, val)
        row[0x60:0x67] = bytes((2, 1, 3, 0x21, 4, 5, 1))
        phy = bytearray(24)
        struct.pack_into("<iiiHH", phy, 0, 5, 2, -40, 7, 8)
        phy[20:22] = bytes((2, 1))
        unit = struct.pack("<IHH", 33, 8, 4)
        pattern = bytearray(24)
        struct.pack_into("<Ii", pattern, 0, 44, -1)
        struct.pack_into("<H", pattern, 12, 12)
        db = NS(sections={10: section(row), 13: section(phy), 15: section(unit), 14: section(pattern)})
        cond = {"table": 8, "key": 9, "source_mode": 3}
        result = legacy_freeze_rows(db, NS(get_string=lambda key: str(key)), "fixture", conditions=[cond])[0]
        self.assertEqual(result["pid"], 0x21)
        self.assertEqual(result["bit_end"], 23)
        self.assertEqual(result["support_conditions"], [cond])
        self.assertTrue(result["support_condition_resolved"])
        self.assertEqual(result["physical_records"][0]["offset"], -40)
        self.assertEqual(result["physical_records"][0]["sign_mode"], 2)
        self.assertEqual(result["physical_records"][0]["patterns"][0]["value"], -1)
        self.assertEqual(result["physical_records"][0]["units"][0]["text"], "33")
        self.assertEqual(result["data_max"], 9000)
        self.assertTrue(result["live_member"])

    def test_payload_extraction_and_signed_scaling(self):
        phy = {"bit_width": 8, "sign_mode": 1, "mul": 3, "div": 2, "offset": 10,
               "decimal_point_count": 1, "patterns": [{"value": 7, "text": "seven"}]}
        row = {"data_type": 2, "physical_records": [phy], "bit_start": 8, "bit_end": 15}
        self.assertEqual(decode_legacy_scalar(row, bytes((0, 254))),
                         {"raw": 254, "converted_integer": 7, "value": "0.7", "patterns": ["seven"]})
        phy["sign_mode"] = 3
        self.assertEqual(decode_legacy_scalar(row, bytes((0, 130)))["converted_integer"], 7)
        self.assertEqual(extract_legacy_scalar(bytes(range(11)), 8, 87), 0x070C0D0E)
        with self.assertRaises(ValueError):
            decode_legacy_scalar(row, bytes((0,)))
        row["data_type"] = 13
        self.assertEqual(decode_legacy_scalar(row, bytes((0, 1)))["converted_integer"], 11)

    def test_native_live_format_routes_differ_from_freeze(self):
        phy = {"bit_width": 16, "sign_mode": 0, "mul": 1, "div": 1, "offset": 0,
               "decimal_point_count": 0, "patterns": []}
        row = {"data_type": 6, "physical_records": [phy], "bit_start": 0, "bit_end": 15}
        self.assertEqual(decode_legacy_scalar(row, (100).to_bytes(2, "big"))["converted_integer"], 100)
        self.assertEqual(decode_legacy_scalar(row, (100).to_bytes(2, "big"), live=True)["converted_integer"], 250)
        row["data_type"] = 19
        self.assertEqual(decode_legacy_scalar(row, (125).to_bytes(2, "big"), live=True)["converted_integer"], 0x205)
        row["data_type"] = 24
        self.assertEqual(decode_legacy_scalar(row, (3000).to_bytes(2, "big"), live=True)["converted_integer"], 1500)
        self.assertEqual(decode_legacy_scalar(row, (3001).to_bytes(2, "big"), live=True)["converted_integer"], 1508)
        row["data_type"] = 10
        self.assertEqual(decode_legacy_scalar(row, bytes((0, 0x81)), live=True)["converted_integer"], -1)

    def test_all_observed_freeze_formats_use_basic_conversion(self):
        phy = {"bit_width": 16, "sign_mode": 0, "mul": 3, "div": 2, "offset": -1,
               "decimal_point_count": 1, "patterns": [{"value": 8, "text": "match"}]}
        row = {"physical_records": [phy], "bit_start": 0, "bit_end": 15}
        for kind in (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 13, 19, 24, 25):
            row["data_type"] = kind
            value = decode_legacy_scalar(row, bytes((0, 6)))
            self.assertEqual(value["value"], "0.8")
            self.assertEqual(value["patterns"], ["match"])
        for kind in (7, 8, 9, 10, 11):
            row["data_type"] = kind
            # low byte0x80 reverses into magnitude1 in every chassis format
            self.assertEqual(decode_legacy_scalar(row, bytes((0, 128)), live=True)["converted_integer"], 0)

    def test_runtime_dynamic_lsb_not_replaced_by_static_scale(self):
        row = {"data_type": 2, "bit_start": 0, "bit_end": 7,
               "physical_records": [{"bit_width": 8, "sign_mode": 0, "mul": 1,
                                     "div": 1, "offset": 0, "decimal_point_count": 1,
                                     "patterns": []}],
               "dynamic_lsb_records": [{"mul": 3, "div": 4}]}
        with self.assertRaisesRegex(ValueError, "runtime PID slope"):
            decode_legacy_scalar(row, bytes((10,)))
        self.assertEqual(decode_legacy_scalar(row, bytes((10,)), dynamic_lsb=2)["value"], "15.0")

    def test_native_field_operands_when_corpus_available(self):
        import pefile
        from tools.techstream.techstream_paths import resolve_gts_root
        try:
            root = resolve_gts_root(None)
        except (FileNotFoundError, SystemExit):
            self.skipTest("GTS corpus unavailable")
        path = root / "bin/GetDatMonSignalInfo.dll"
        if not path.is_file():
            self.skipTest("GTS corpus unavailable")
        pe = pefile.PE(str(path))
        for rva, expected in {
            0x12B7: "668b404c", 0x12C5: "8b4044", 0x1302: "0fb64060",
            0x1341: "0fb74050", 0x13E8: "0fb77052", 0x13EC: "0fb77854",
            0x14B0: "0fb7405a",
        }.items():
            self.assertEqual(pe.get_data(rva, len(bytes.fromhex(expected))).hex(), expected)
        kgp = pefile.PE(str(root / "bin/KgpDataCtrl.dll"))
        self.assertEqual(kgp.get_data(0xB34C0, 4).hex(), "0fb64263")
        self.assertEqual(kgp.get_data(0xB3656, 4).hex(), "6b450c68")

    def test_not_v18_layout(self):
        with self.assertRaisesRegex(ValueError, "expected104"):
            legacy_freeze_rows(NS(sections={10: section(bytes(84))}), None, "fixture")

    def test_missing_condition_not_silently_supported(self):
        row = bytearray(104)
        struct.pack_into("<H", row, 0x4E, 999)
        result = legacy_freeze_rows(NS(sections={10: section(row)}),
                                   NS(get_string=lambda key: ""), "fixture")[0]
        self.assertFalse(result["support_condition_resolved"])
        self.assertEqual(result["support_condition_key"], 999)


if __name__ == "__main__":
    unittest.main()
