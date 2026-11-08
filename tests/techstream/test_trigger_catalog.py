import struct
import unittest
from types import SimpleNamespace as NS

from tools.techstream.gts.trigger_catalog import trigger_catalog


def section(*rows):
    return NS(iter_records=lambda: iter(NS(raw=bytes(row)) for row in rows))


class TriggerCatalogTest(unittest.TestCase):
    def test_trigger_command_layout(self):
        raw = struct.pack("<IIIHHHBBB3s", 11, 12, 13, 14, 15, 16, 17, 18, 19, b"abc")
        result = trigger_catalog(NS(sections={16: section(raw)}),
                                 NS(get_string=lambda key: str(key)), "fixture")
        row = result["trigger_items"][0]
        self.assertEqual(row["name"], "13")
        self.assertEqual(row["trigger_key"], 14)
        self.assertEqual(row["command_trigger_fields"],
                         {"u16_at20": 15, "u32_at24": 12, "u8_at28": 18,
                          "u32_at2c": 11, "u8_at30": 17})
        self.assertEqual(row["exception_handler_id"], 16)

    def test_retrieval_and_predictive_relationships(self):
        monitor = bytearray(80)
        struct.pack_into("<H", monitor, 0x48, 0x2AF8)
        result = trigger_catalog(NS(sections={
            19: section(struct.pack("<HHHBB", 0x1FA4, 0xCD, 0, 1, 0)),
            32: section(struct.pack("<HBBHB3s", 9, 99, 0, 0, 0, bytes(3))),
            171: section(struct.pack("<HHHBB", 0, 0x2AF8, 0, 40, 0)),
            62: section(monitor)}), None, "fixture")
        self.assertEqual(result["trigger_retrieval"][0]["function_selector"], 0xCD)
        self.assertEqual(result["dtc_group_retrieval"][0]["signal_group_key"], 99)
        row = result["predictive_ffd_vehicle_dids"][0]
        self.assertEqual(row["vehicle_type"], 40)
        self.assertEqual(row["snapshot_monitor_records"], [0])

    def test_layout_mismatch_is_not_silently_decoded(self):
        with self.assertRaisesRegex(ValueError, "table171"):
            trigger_catalog(NS(sections={171: section(bytes(6))}), None, "fixture")


if __name__ == "__main__":
    unittest.main()
