import unittest
from types import SimpleNamespace as NS
from tools.techstream.gts.active_test_source import active_test_source_catalog
from tests.techstream.verify_source_coverage import audit_catalog

class SourceCoverageTest(unittest.TestCase):
    def test_duplicate_active_ids_remain_source_rows(self):
        def section(n):
            return NS(iter_records=lambda: iter(NS(raw=bytes(n)) for _ in range(2)))
        rows = active_test_source_catalog(NS(sections={33:section(12),68:section(64),
            71:section(72),77:section(52)}), NS(get_string=lambda _:None),"fixture")
        self.assertEqual(len(rows),8)
        catalog = {"source_tables":[{"table":t,"record_count":2,"record_size":n}
                    for t,n in ((33,12),(68,64),(71,72),(77,52))],
                   "active_test_source":rows}
        self.assertEqual(audit_catalog(catalog),[])
        catalog["active_test_source"] = rows[:-1]
        self.assertIn("table 33: missing",audit_catalog(catalog)[0])

    def test_unknown_and_raw_only_fail(self):
        c={"source_tables":[{"table":999,"record_count":1,"record_size":2}],
           "monitor_source":[]}
        self.assertIn("no source decoder",audit_catalog(c)[0])
        c={"source_tables":[{"table":81,"record_count":1,"record_size":8}],
           "monitor_source":[{"table":81,"record":0,"raw":"00"*8}]}
        self.assertIn("raw-only",audit_catalog(c)[0])

    def test_duplicate_and_undeclared_projection_fail(self):
        row = {"table":81,"record":0,"raw":"00"*8,"did":1}
        c = {"source_tables":[{"table":81,"record_count":1,"record_size":8}],
             "monitor_source":[row,row]}
        self.assertTrue(any("duplicate source projection" in e for e in audit_catalog(c)))
        c["monitor_source"] = [{"table":68,"record":0,"raw":"00"*64,"active_test_id":1}]
        self.assertTrue(any("unexpected source table" in e for e in audit_catalog(c)))
        c = {"source_tables":[],"monitor_source":[row]}
        self.assertTrue(any("source table absent" in e for e in audit_catalog(c)))

    def test_actual_source_bytes_not_just_lengths(self):
        section = NS(header=NS(record_count=1), decoded_record_size=8,
                     iter_records=lambda: iter([NS(raw=bytes(8))]))
        db = NS(sections={81:section})
        c = {"source_tables":[{"table":81,"record_count":1,"record_size":8}],
             "monitor_source":[{"table":81,"record":0,"raw":"00"*8,"did":1}]}
        self.assertEqual(audit_catalog(c,db),[])
        c["monitor_source"][0]["raw"] = "01"+"00"*7
        self.assertTrue(any("bytes differ from actual" in e for e in audit_catalog(c,db)))
        del c["monitor_source"][0]["raw"]
        self.assertTrue(any("source bytes length -1" in e for e in audit_catalog(c,db)))

    def test_nested_lookup_cannot_mask_absent_source(self):
        c={"source_tables":[{"table":81,"record_count":2,"record_size":8}],
           "monitor_source":[{"table":81,"record":0,"raw":"00"*8,"did":1,
           "nested":{"table":81,"record":1,"raw":"00"*8,"did":2}}]}
        self.assertIn("missing [1]",audit_catalog(c)[0])

if __name__ == "__main__":
    unittest.main()
