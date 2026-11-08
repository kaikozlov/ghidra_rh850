import struct
import unittest
from types import SimpleNamespace as NS

from tools.techstream.gts.monitor_source_catalog import monitor_source_catalog, TABLE_SIZES

def section(*rows):
    return NS(iter_records=lambda: iter(NS(raw=bytes(row)) for row in rows),
              decoded_record_size=len(rows[0]))

class MonitorSourceTest(unittest.TestCase):
    def catalog(self, tables, **kwargs):
        return monitor_source_catalog(NS(sections=tables),
            NS(get_string=lambda key: str(key)), "fixture", **kwargs)

    def test_all_aliases_and_duplicates_retained(self):
        tables = {t: section(bytes(size), bytes(size)) for t, size in TABLE_SIZES.items()}
        rows = self.catalog(tables)
        self.assertEqual(len(rows), 2 * len(TABLE_SIZES))
        self.assertEqual({(r["table"],r["record"]) for r in rows},
                         {(t,i) for t in TABLE_SIZES for i in range(2)})

    def test_conditions_use_distinct_layouts(self):
        a = struct.pack("<HHHHHHBBBB", 1,2,3,4,5,6,7,8,9,10)
        b = struct.pack("<HHHHHBB",1,2,3,4,5,6,7)
        rows = self.catalog({63:section(a),80:section(b),89:section(b)},
                            resolve_variable=lambda _: bytes.fromhex("1234"))
        self.assertEqual(rows[0]["comparison_value"],6)
        self.assertEqual(rows[0]["condition_type"],8)
        self.assertNotIn("referenced_did",rows[0])
        self.assertEqual(rows[1]["referenced_did"],0x1234)
        self.assertEqual(rows[2]["exception_handler_flag"],6)

    def test_status_and_dynamic_and_pcs(self):
        a = struct.pack("<IHHBBBB",0x80000000,4,5,6,7,8,9)
        b = struct.pack("<HHHBB",0xF301,1024,7,1,0)
        rows = self.catalog({66:section(a),81:section(b),86:section(bytes.fromhex("1100e101"))})
        self.assertEqual(rows[0]["key"],0x80000000)
        self.assertEqual(rows[0]["status_mask"],6)
        self.assertEqual(rows[1]["maximum_payload_length"],1024)
        self.assertEqual(rows[2]["pid"],0xE1)
        self.assertEqual(rows[2]["retrieval_group"],1)

    def test_physical_sign_mode_and_duplicate_candidates(self):
        p = bytearray(24)
        struct.pack_into("<iiiHH",p,0,2,3,4,5,6)
        p[20] = 3
        m = bytearray(80)
        struct.pack_into("<H",m,0x3A,5)
        rows = self.catalog({13:section(p,p),62:section(m)})
        self.assertEqual(len(rows[0]["physical_records"]),2)
        self.assertEqual(rows[0]["physical_records"][0]["sign_mode"],3)

    def test_indexed_joins_equal_reference_with_duplicate_units(self):
        from unittest.mock import patch
        libraries = {
            "physical":[{"key":5,"unit_key":9},{"key":5,"unit_key":7},
                        {"key":5,"unit_key":9},{"key":6,"unit_key":8}],
            "units":[{"key":7,"value":"first"},{"key":9,"value":"second"},
                     {"key":7,"value":"third"},{"key":8,"value":"excluded"}],
            "patterns":[{"key":3,"value":"first"},{"key":4,"value":"excluded"},
                        {"key":3,"value":"second"}]}
        monitor = bytearray(80)
        struct.pack_into("<H",monitor,0x3A,5)
        struct.pack_into("<H",monitor,0x42,3)
        with patch("tools.techstream.gts.monitor_source_catalog.physical_catalog",
                   return_value=libraries):
            rows = self.catalog({62:section(monitor,monitor)})
        physical = [p for p in libraries["physical"] if p["key"] == 5]
        reference = {
            "physical_records":physical,
            "unit_records":[u for u in libraries["units"]
                            if any(p["unit_key"] == u["key"] for p in physical)],
            "pattern_records":[p for p in libraries["patterns"] if p["key"] == 3]}
        for row in rows:
            self.assertEqual({key:row[key] for key in reference},reference)
        self.assertEqual([u["value"] for u in rows[0]["unit_records"]],
                         ["first","second","third"])

    def test_malformed_rows_fail(self):
        with self.assertRaisesRegex(ValueError,"table86"):
            self.catalog({86:section(bytes(8))})

if __name__ == "__main__":
    unittest.main()
