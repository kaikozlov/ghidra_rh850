import struct
import unittest
from types import SimpleNamespace

from tools.techstream.gts.legacy_support import decode_support_bitmap, support_catalog


def section(table, size, rows):
    return SimpleNamespace(header=SimpleNamespace(table_type=table, record_count=len(rows)),
                           decoded_record_size=size, decoded_data=b"".join(rows),
                           iter_records=lambda: iter(SimpleNamespace(raw=row) for row in rows))


class Strings:
    def get_string(self, key):
        return {123: "Snapshot group"}.get(key)


class LegacySupportTests(unittest.TestCase):
    def test_group_join_stays_with_its_native_table_family(self):
        group = struct.pack("<IHHBBH", 123, 99, 7, 4, 1, 0)
        check = struct.pack("<HHHBB", 99, 0x1234, 8, 2, 0)
        other = struct.pack("<HHHBB", 99, 0x5678, 0, 0, 0)
        db = SimpleNamespace(sections={
            0: section(0, 12, [group]), 1: section(1, 8, [check, check]),
            154: section(154, 12, [group]), 155: section(155, 8, [other]),
        })
        catalog = support_catalog(db, Strings(), "fixture")
        self.assertEqual(catalog["signal_groups"][0]["members"], [0x1234, 0x1234])
        self.assertEqual(catalog["signal_groups"][1]["members"], [0x5678])
        self.assertEqual(catalog["signal_groups"][0]["name"], "Snapshot group")
        self.assertEqual(catalog["signal_memberships"][0]["exception_handler_id"], 8)

    def test_query_policy_and_frame_number_are_not_dids(self):
        db = SimpleNamespace(sections={
            3: section(3, 8, [bytes.fromhex("0700000020020100")]),
            2: section(2, 4, [bytes.fromhex("08000f02")]),
        })
        catalog = support_catalog(db, Strings(), "fixture")
        self.assertEqual(catalog["support_queries"][0]["query_id"], 0x20)
        self.assertTrue(catalog["support_queries"][0]["requires_previously_supported_query_id_in_p4"])
        self.assertEqual(catalog["freeze_frame_queries"][0]["freeze_frame_number"], 15)
        self.assertNotIn("did", catalog["freeze_frame_queries"][0])

    def test_native_bitmap_order_and_byte_id_boundary(self):
        self.assertEqual(decode_support_bitmap(0x20, bytes.fromhex("8101")), [0x20, 0x21, 0x28, 0x30])
        self.assertEqual(decode_support_bitmap(0xFE, b"\xff\xff"), [0xFE, 0xFF])
        self.assertEqual(decode_support_bitmap(0x20, b""), [0x20])
        with self.assertRaises(ValueError):
            decode_support_bitmap(256, b"")

    def test_wrong_layout_is_not_silently_decoded(self):
        db = SimpleNamespace(sections={3: section(3, 4, [b"\0" * 4])})
        with self.assertRaises(ValueError):
            support_catalog(db, Strings(), "fixture")


if __name__ == "__main__":
    unittest.main()
