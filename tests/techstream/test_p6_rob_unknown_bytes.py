import unittest
from types import SimpleNamespace

from tests.techstream.verify_p6_rob_byte_coverage import reconstruct
from tools.techstream.gts.rob_source_catalog import rob_source_catalog


class ROBUnknownTests(unittest.TestCase):
    def decode(self, table, raw):
        section = SimpleNamespace(
            iter_records=lambda: iter([SimpleNamespace(raw=bytes(raw), index=0)])
        )
        db = SimpleNamespace(sections={table: section})
        return rob_source_catalog(
            db,
            SimpleNamespace(get_string=lambda key: None),
            "fixture.ddb",
            resolve_variable=lambda key: b"\0\0",
        )

    def test_every_unknown_offset_roundtrips_nonzero(self):
        for table, width, offsets, key in (
            (163, 68, range(65, 68), "behavior_codes"),
            (164, 48, [38, 39, 43, 44, 45, 46, 47], "signals"),
        ):
            for offset in offsets:
                raw = bytearray(width)
                raw[offset] = 0xA5
                with self.subTest(table=table, offset=offset):
                    row = self.decode(table, raw)[key][0]
                    self.assertEqual(reconstruct(row), raw)

    def test_signature_suffix_and_full_width(self):
        raw = bytearray(68)
        raw[:6] = b"A\x00\x00\x00B\x00"
        with self.assertRaisesRegex(ValueError, "signature suffix"):
            self.decode(163, raw)
        raw[:44] = ("A" * 22).encode("utf-16le")
        self.assertEqual(reconstruct(self.decode(163, raw)["behavior_codes"][0]), raw)

    def test_future_larger_layout_not_truncated(self):
        for table, width in ((163, 68), (164, 48)):
            with self.subTest(table=table), self.assertRaises(ValueError):
                self.decode(table, bytearray(width + 1))


if __name__ == "__main__":
    unittest.main()
