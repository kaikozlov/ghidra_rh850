import struct
import unittest
from types import SimpleNamespace

from tools.techstream.parse_ddb import Section, TableDataHead
from tools.techstream.gts.legacy_active import legacy_active_tests, legacy_active_patterns


def section(table, rows):
    data = b"".join(rows)
    return Section(TableDataHead(table, 0, len(rows), len(data)), 0, data)


class LegacyActiveTests(unittest.TestCase):
    def test_parameter_joins_and_native_field_offsets(self):
        active = bytearray(92)
        for offset, value in [(20, 7), (24, 255), (28, 0), (32, 123), (36, 1),
                              (40, 2), (44, 3), (48, 4), (52, 5)]:
            struct.pack_into("<I", active, offset, value)
        for offset, value in [(56, 99), (58, 77), (62, 9), (64, 10), (66, 8), (68, 15), (76, 78), (78, 79)]:
            struct.pack_into("<H", active, offset, value)
        active[82], active[84], active[85], active[89] = 3, 1, 4, 3
        pattern = bytearray(24)
        for offset, value in [(0, 10), (4, 100), (6, 200), (10, 11), (12, 300)]:
            struct.pack_into("<H", pattern, offset, value)
        pattern[18], pattern[19], pattern[21] = 1, 2, 3
        physical = bytearray(24)
        struct.pack_into("<iiiHH", physical, 0, 2, 3, -4, 9, 12)
        physical[20], physical[21] = 3, 2
        unit = struct.pack("<IHH", 124, 12, 0)
        display = bytearray(24)
        struct.pack_into("<II", display, 0, 125, 42)
        struct.pack_into("<H", display, 12, 11)
        db = SimpleNamespace(sections={11: section(11, [active]), 12: section(12, [pattern]),
             13: section(13, [physical]), 14: section(14, [display]), 15: section(15, [unit])})
        strings = SimpleNamespace(get_string=lambda key: {123: "Actuator", 124: "V", 125: "On"}.get(key))
        row = legacy_active_tests(db, strings, "fixture")[0]
        self.assertEqual((row["id"], row["name"], row["initial_value"], row["data_max"]), (99, "Actuator", 7, 255))
        self.assertEqual(row["pattern"]["lock_time"], 300)
        self.assertEqual(row["pattern"]["button_size"], 3)
        self.assertEqual(row["signal_info"]["pattern_display"], {42: "On"})
        self.assertEqual(row["signal_info"]["bit_width"], 8)
        self.assertEqual(row["signal_info"]["offset"], -4)
        self.assertEqual(row["signal_info"]["sign_mode"], 3)
        self.assertNotIn("signed", row["signal_info"])
        self.assertEqual(row["execution"], "metadata_only")
        self.assertEqual(row["raw"], active)
        db.sections.pop(12)
        row = legacy_active_tests(db, strings, "fixture")[0]
        self.assertIsNone(row["pattern"])
        self.assertEqual(row["pattern_match_count"], 0)

    def test_request_program_order_termination_and_dependencies(self):
        from tools.techstream.gts.legacy_active import legacy_request_program
        raw = bytearray(92)
        struct.pack_into("<H", raw, 74, 0xC32B)
        raw[82], raw[88] = 0x42, 0x80
        program = legacy_request_program(raw)
        self.assertEqual([row["opcode"] for row in program["operations"]], [11, 2, 3, 12])
        self.assertTrue(program["support_required"])
        self.assertEqual(program["request_identifier"], 0x42)
        struct.pack_into("<H", raw, 74, 0xA002)
        self.assertEqual(len(legacy_request_program(raw)["operations"]), 1)

    def test_rejects_unknown_layout(self):
        db = SimpleNamespace(sections={12: section(12, [bytes(23)])})
        with self.assertRaises(ValueError):
            legacy_active_patterns(db, "fixture")


if __name__ == "__main__":
    unittest.main()
