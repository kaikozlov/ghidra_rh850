import copy
import struct
import unittest
from types import SimpleNamespace as NS
from tests.techstream.viewer_source_audit import expected_viewer_rows, audit_viewer_rows

class ViewerAuditTest(unittest.TestCase):
    def fixture(self):
        rows = [struct.pack("<IIHH",s,h,k,0) for s,h,k in ((10,7,3),(20,7,2),(30,7,3),(40,8,3))]
        db = NS(sections={2:NS(iter_records=lambda:iter(NS(raw=r) for r in rows))})
        expected = expected_viewer_rows(db,NS(get_string=lambda i:{10:"old",20:"wrong kind",30:"last"}.get(i)))
        identity = {"database":{"path":"NA/DB/Gen/Viewer.ddb","sha256":"actual","bytes":1},
                    "strings":{"path":"NA/DB/Gen/V_English.ddb","sha256":"actual-text","bytes":2}}
        def standard(key,index):
            matches = copy.deepcopy(expected.get(key,[])) if key else []
            return {"record":index,"raw":struct.pack("<III",key,0,0).hex(),
                    "help_id":key,"standard_value_help_records":matches,
                    "standard_value":matches[-1]["text"] if matches else None,
                    "standard_value_status": {0:"not_specified",7:"resolved",8:"translation_unavailable",9:"help_not_found"}[key]}
        catalog = {"source_identity":{"viewer_help":copy.deepcopy(identity)},
                   "work_factor":{"standard_info":[standard(k,i) for i,k in enumerate((0,7,8,9))]}}
        return catalog,expected,identity

    def test_last_match_missing_translation_and_zero(self):
        c,e,i = self.fixture()
        self.assertEqual(audit_viewer_rows(c,e,i),[])
        self.assertEqual([r["record"] for r in e[7]],[0,2])

    def test_wrong_namespace_text_and_selection(self):
        for field,value in (("namespace","master"),("string_source","M_English.ddb"),
                            ("text","wrong"),("record",99),("raw","00"*12)):
            c,e,i = self.fixture()
            c["work_factor"]["standard_info"][1]["standard_value_help_records"][-1][field] = value
            self.assertTrue(audit_viewer_rows(c,e,i),field)
        c,e,i = self.fixture()
        c["work_factor"]["standard_info"][1]["standard_value"] = "old"
        self.assertTrue(any("last matching" in s for s in audit_viewer_rows(c,e,i)))

    def test_wrong_hash_and_status(self):
        c,e,i = self.fixture()
        c["source_identity"]["viewer_help"]["strings"]["sha256"] = "wrong"
        self.assertTrue(any("identity" in s for s in audit_viewer_rows(c,e,i)))
        c,e,i = self.fixture()
        c["work_factor"]["standard_info"][0]["standard_value_status"] = "help_not_found"
        self.assertTrue(any("status" in s for s in audit_viewer_rows(c,e,i)))

if __name__ == "__main__":
    unittest.main()
