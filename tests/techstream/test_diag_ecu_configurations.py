import json
import sqlite3
import unittest
from tools.techstream.diag_codec import compress, decompress
from tools.techstream.diag_ecu_configurations import normalize, restore

class ConfigurationTests(unittest.TestCase):
    def fixture(self, values):
        db=sqlite3.connect(":memory:")
        db.execute("CREATE TABLE source_documents(id INTEGER PRIMARY KEY,member TEXT,data BLOB)")
        for i,value in enumerate(values,1):
            db.execute("INSERT INTO source_documents VALUES(?,?,?)",(i,f"catalogs/NA/{i}.json",compress(json.dumps(value).encode())))
        return db
    def test_owner_separate_exact_configuration_and_order(self):
        body={"signals":[{"$signal_definition":1},{"$signal_definition":1}],"unknown":{"null":None,"large":2**63}}
        values=[dict(body,category={"id":1}),dict(body,category={"id":2}),dict(body,category={"id":3},extra=False)]
        db=self.fixture(values);stats=normalize(db)
        self.assertEqual((stats["owners"],stats["definitions"]),(3,2))
        for i,want in enumerate(values,1):self.assertEqual(restore(db,i),want)
        self.assertEqual(db.execute("SELECT definition_id FROM ecu_catalog_bindings WHERE document_id IN(1,2)").fetchall(),[(1,),(1,)])
    def test_absent_null_and_unknown_category_shapes_stay_inline(self):
        values=[{"x":1},{"category":None},{"category":[]}]
        db=self.fixture(values);self.assertEqual(normalize(db)["owners"],0)
        actual=[json.loads(decompress(r[0])) for r in db.execute("SELECT data FROM source_documents ORDER BY id")]
        self.assertEqual(actual,values)
    def test_parts_are_not_reinterpreted(self):
        db=self.fixture([{"category":{},"signals":{"$part":1}}])
        db.execute("CREATE TABLE source_document_parts(document_id INTEGER)")
        db.execute("INSERT INTO source_document_parts VALUES(1)")
        self.assertEqual(normalize(db)["owners"],0)
    def test_corruption_and_missing_references_fail(self):
        db=self.fixture([{"category":{},"signals":[]}]);normalize(db)
        with self.assertRaises(ValueError):restore(db,0)
        with self.assertRaises(ValueError):restore(db,2)
        db.execute("UPDATE ecu_catalog_definitions SET data=?",(compress(b'{"category":{}}'),))
        with self.assertRaises(ValueError):restore(db,1)

if __name__=="__main__":unittest.main()
