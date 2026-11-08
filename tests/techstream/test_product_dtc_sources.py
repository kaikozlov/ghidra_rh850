import sqlite3
import unittest

from tools.techstream.diag_product_dtc_sources import SourceDTCStore, restore


class SourceDTCTests(unittest.TestCase):
    def setUp(self):
        self.db = sqlite3.connect(":memory:")
        self.store = SourceDTCStore(self.db)

    def row(self):
        return {
            "source": "ABS.ddb",
            "table": 5,
            "record": 0,
            "code": "P0001",
            "description": None,
            "comment": "",
            "description_string_index": 0,
            "comment_string_index": 4,
            "enabled_value": 0,
            "enabled": False,
            "exception_handler_id": 65535,
            "exception_handler_flag": 255,
            "dtc_identifier": 1,
            "detail_table": 47,
            "detail_lookup_key": 2,
            "unconsumed_descriptor_offsets": [24, 25],
            "uninterpreted_bytes": {"24_25": "12ff"},
        }

    def test_disabled_and_variants_and_unknown(self):
        row = self.row()
        a = self.store.row(row)["$dtc_source_definition"]
        other = {**row, "enabled_value": 2, "enabled": True}
        b = self.store.row(other)["$dtc_source_definition"]
        self.assertNotEqual(a, b)
        self.assertEqual(restore(self.db, a), row)
        self.assertEqual(restore(self.db, b), other)
        self.assertEqual(
            self.db.execute("SELECT count(*) FROM diagnostic_codes").fetchone()[0], 1
        )

    def test_unknown_shape_and_noncanonical_values_stay_inline(self):
        for field, value in [
            ("future", 2),
            ("enabled", 1),
            ("enabled_value", 256),
            ("uninterpreted_bytes", {"24_25": "FFFF"}),
        ]:
            row = self.row()
            row[field] = value
            self.assertEqual(self.store.row(row), row)

    def test_corrupt_and_missing(self):
        id = self.store.row(self.row())["$dtc_source_definition"]
        self.db.execute(
            "UPDATE dtc_source_extensions SET enabled_value=256 WHERE id=?", (id,)
        )
        with self.assertRaises(ValueError):
            restore(self.db, id)
        with self.assertRaises(ValueError):
            restore(self.db, 999)

    def test_table65_exact(self):
        row = self.row()
        for k in (
            "dtc_identifier",
            "detail_table",
            "detail_lookup_key",
            "unconsumed_descriptor_offsets",
        ):
            del row[k]
        row.update(
            table=65,
            packed_dtc=0x123456,
            base_dtc=0x1234,
            failure_type=0x56,
            failure_string_index=0,
            failure_description=None,
            uninterpreted_bytes={"67": "ff"},
            diag_code_info_fields=[
                {"source_offset": 65, "output_offset": 52, "width": 1, "value": 255},
                {"source_offset": 62, "output_offset": 54, "width": 2, "value": 65535},
            ],
        )
        id = self.store.row(row)["$dtc_source_definition"]
        self.assertEqual(restore(self.db, id), row)


if __name__ == "__main__":
    unittest.main()
