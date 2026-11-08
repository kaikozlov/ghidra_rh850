import struct
import unittest
from types import SimpleNamespace

from tools.techstream.gts.work_factor import decode_dcm_item, viewer_help_index, work_factor_catalog


def section(size, rows):
    return SimpleNamespace(decoded_record_size=size,
                           iter_records=lambda: iter(SimpleNamespace(raw=row) for row in rows))


class Strings:
    def get_string(self, key):
        return {123: "Reason", 124: "Details", 125: "seconds"}.get(key)


class WorkFactorTests(unittest.TestCase):
    def fixture(self):
        signal = bytearray(28)
        struct.pack_into("<I7H", signal, 0, 123, 99, 7, 10, 11, 12, 13, 9)
        signal[26] = 2
        item = bytearray(40)
        struct.pack_into("<5I7H", item, 0, 3, 2, 4, 123, 125, 99, 3, 10, 0, 51, 61, 8)
        item[34:37] = bytes([2, 1, 1])
        pattern = struct.pack("<II4HB3s", 123, 124, 61, 6, 12, 7, 2, b"\0" * 3)
        standard = struct.pack("<IHHHBB", 0x12345678, 5, 6, 7, 8, 0)
        return SimpleNamespace(sections={
            18: section(12, [standard]), 35: section(28, [bytes(signal)]),
            36: section(40, [bytes(item), bytes(item)]),
            37: section(20, [pattern, pattern]),
        })

    def test_native_fields_and_variant_preserving_joins(self):
        catalog = work_factor_catalog(self.fixture(), Strings(), "fixture")
        signal = catalog["work_factor_signals"][0]
        self.assertEqual(signal["item_records"], [0, 1])
        self.assertEqual(signal["ram_frame_pid_ids"], [10, 11, 12])
        self.assertEqual(signal["ram_address_pid_id"], 13)
        self.assertEqual(signal["effective_mode"], 3)
        self.assertEqual(signal["effective_frame_length"], 4)
        item = catalog["work_factor_items"][0]
        self.assertEqual(item["pattern_records"], [0, 1])
        self.assertEqual(item["unit"], "seconds")
        self.assertEqual((item["bit_start"], item["bit_end"]), (3, 10))
        self.assertEqual(item["physical_data_id"], 51)
        self.assertEqual(item["exception_handler_id"], 8)
        self.assertEqual(item["role"], 2)
        self.assertTrue(item["new_dcm_available"])
        self.assertEqual(catalog["work_factor_patterns"][0]["help"], "Details")
        self.assertEqual(catalog["standard_info"][0]["signal_id"], 6)

    def test_dcm_msb_range_and_unsigned_arithmetic(self):
        item = work_factor_catalog(self.fixture(), Strings(), "fixture")["work_factor_items"][0]
        self.assertEqual(decode_dcm_item(item, bytes.fromhex("1234")), 221)
        item.update(bit_start=0, bit_end=31, scale_numerator=2, scale_denominator=0, addend_u32=3)
        self.assertEqual(decode_dcm_item(item, bytes.fromhex("ffffffff")), 1)
        item.update(bit_start=7, bit_end=7, scale_numerator=1, addend_u32=0)
        self.assertEqual(decode_dcm_item(item, b"\x01"), 1)
        for start, end in ((8, 7), (0, 32), (0, 8)):
            item.update(bit_start=start, bit_end=end)
            with self.assertRaises(ValueError):
                decode_dcm_item(item, b"\xff")

    def test_p5_and_rob_families_keep_native_keys(self):
        db = self.fixture()
        signal = bytearray(24)
        signal[:12] = "B1234\0".encode("utf-16-le")
        struct.pack_into("<IHHHB", signal, 12, 123, 0xF123, 7, 9, 2)
        item = struct.pack("<I6HHBB", 123, 0xF123, 0, 7, 51, 61, 9, 0, 1, 2)
        operation = struct.pack("<IIHHHBB", 123, 124, 0xF123, 0xABCD, 9, 2, 0)
        network = struct.pack("<I5HBB", 123, 0, 2, 61, 9, 0, 1, 2)
        factor = struct.pack("<IIIHHHBB", 123, 124, 0x12345678, 55, 9, 0, 2, 0)
        db.sections.update({
            114: section(24, [bytes(signal)]), 115: section(20, [item, item]),
            116: section(16, [operation]), 117: section(16, [network]),
            118: section(20, [factor]),
        })
        c = work_factor_catalog(db, Strings(), "fixture")
        p5 = c["work_factor_p5_signals"][0]
        self.assertEqual(p5["display_id"], "B1234")
        self.assertEqual(p5["identifier"], 0xF123)
        self.assertNotIn("item_records", p5)
        self.assertEqual(p5["identifier_roles"]["rob"], "behavior_code")
        self.assertEqual(p5["operation_code_records"], [0])
        self.assertEqual(c["work_factor_rob_items"][0]["pattern_records"], [0, 1])
        self.assertEqual(c["work_factor_operation_codes"][0]["operation_code"], 0xABCD)
        self.assertEqual(c["work_factor_operation_codes"][0]["content_name"], "Details")
        self.assertEqual(c["work_factor_network_status"][0]["pattern_records"], [0, 1])
        self.assertEqual(c["factor_data"][0]["value"], 0x12345678)
        self.assertEqual(c["factor_data"][0]["signal_id"], 55)

    def test_standard_info_joins_viewer_help_not_ecu_strings(self):
        db = self.fixture()
        help_id = 0x12345678
        viewer = SimpleNamespace(sections={2: section(12, [
            struct.pack("<IIHH", 123, help_id, 2, 0),
            struct.pack("<IIHH", 124, help_id, 3, 0),
            struct.pack("<IIHH", 125, help_id, 3, 0),
        ])})
        index = viewer_help_index(viewer, Strings(), "NA/Viewer.ddb", "NA/V_English.ddb")
        row = work_factor_catalog(db, Strings(), "fixture", viewer_help=index)["standard_info"][0]
        self.assertEqual(row["help_id"], help_id)
        self.assertNotIn("value_u32", row)
        self.assertEqual(row["standard_value"], "seconds")  # Last kind3 row, not first.
        self.assertEqual(row["standard_value_status"], "resolved")
        self.assertEqual([r["record"] for r in row["standard_value_help_records"]], [1, 2])
        self.assertEqual(row["standard_value_help_records"][-1]["namespace"], "viewer")
        self.assertEqual(row["standard_value_help_records"][-1]["string_source"], "NA/V_English.ddb")
        self.assertEqual(len(index[help_id]), 3)  # Other kinds remain in the source index.

    def test_standard_info_missing_help_and_translation_are_distinct(self):
        db = self.fixture()
        row = work_factor_catalog(db, Strings(), "fixture")["standard_info"][0]
        self.assertEqual(row["standard_value_status"], "viewer_help_not_loaded")
        row = work_factor_catalog(db, Strings(), "fixture", viewer_help={})["standard_info"][0]
        self.assertEqual(row["standard_value_status"], "help_not_found")
        viewer = SimpleNamespace(sections={2: section(12, [
            struct.pack("<IIHH", 999, 0x12345678, 3, 0),
        ])})
        index = viewer_help_index(viewer, Strings(), "Viewer.ddb")
        row = work_factor_catalog(db, Strings(), "fixture", viewer_help=index)["standard_info"][0]
        self.assertEqual(row["standard_value_status"], "translation_unavailable")
        self.assertIsNone(row["standard_value"])
        db.sections[18] = section(12, [bytes(12)])
        row = work_factor_catalog(db, Strings(), "fixture", viewer_help=index)["standard_info"][0]
        self.assertEqual(row["standard_value_status"], "not_specified")
        self.assertEqual(row["standard_value_help_records"], [])

    def test_absent_tables_and_wrong_stride(self):
        self.assertTrue(all(not rows for rows in work_factor_catalog(SimpleNamespace(sections={}), Strings(), "fixture").values()))
        for table in (18, 35, 36, 37, 114, 115, 116, 117, 118):
            with self.assertRaises(ValueError):
                work_factor_catalog(SimpleNamespace(sections={table: section(1, [b"\0"])}), Strings(), "fixture")


if __name__ == "__main__":
    unittest.main()
