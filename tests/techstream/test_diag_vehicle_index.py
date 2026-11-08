import json
import sqlite3
import unittest

from tools.techstream.diag_codec import compress, decompress
from tools.techstream.diag_vehicle_index import (
    ROUTE_INTS,
    ROUTE_NULLABLE_INTS,
    normalize,
    restore_vehicle_index,
)


def route():
    value = {k: 0 for k in ROUTE_INTS}
    value.update({k: None for k in ROUTE_NULLABLE_INTS})
    value.update(
        route_selector=17,
        controller=None,
        request_address_field_semantics="unrecovered",
        transport_kind="unknown",
    )
    return value


class VehicleIndexTests(unittest.TestCase):
    def fixture(self):
        db = sqlite3.connect(":memory:")
        self.addCleanup(db.close)
        db.executescript("""
          CREATE TABLE search_regions(id INTEGER PRIMARY KEY,name TEXT);
          INSERT INTO search_regions VALUES(1,'NA');
          CREATE TABLE source_documents(id INTEGER PRIMARY KEY,member TEXT,data BLOB);
          INSERT INTO source_documents VALUES(1,'index.json',NULL);
          CREATE TABLE source_pointers(id INTEGER PRIMARY KEY,pointer TEXT);
          CREATE TABLE source_document_parts(document_id INTEGER,pointer_id INTEGER,data BLOB,PRIMARY KEY(document_id,pointer_id)) WITHOUT ROWID;
        """)
        connection = dict(
            category_id=10,
            connection_comm_set_id=9,
            connection_frame_id=0,
            connection_route_selector=17,
            route_key="10:17",
        )
        other = dict(
            category_id=11,
            connection_comm_set_id=1,
            connection_frame_id=1,
            connection_route_selector=17,
            route_key=None,
        )
        values = {
            "vehicles": {
                "1": dict(name="", vehicle_type=1, install_set_ids=[10, 999, 10])
            },
            "install_sets": {"10": [connection, connection.copy(), other], "11": []},
            "routes": {"10:17": route()},
        }
        for identity, (kind, value) in enumerate(values.items(), 1):
            db.execute(
                "INSERT INTO source_pointers VALUES(?,?)",
                (identity, f"/regions/NA/{kind}"),
            )
            db.execute(
                "INSERT INTO source_document_parts VALUES(1,?,?)",
                (identity, compress(json.dumps(value).encode())),
            )
        return db, values

    def test_source_roundtrip_and_derived_projection(self):
        db, values = self.fixture()
        normalize(db)
        for kind, expected in values.items():
            packed = db.execute(
                """SELECT d.data FROM source_document_parts d
                 JOIN source_pointers p ON p.id=d.pointer_id WHERE p.pointer=?""",
                (f"/regions/NA/{kind}",),
            ).fetchone()[0]
            refs = json.loads(decompress(packed))
            actual = {}
            for key, ref in refs.items():
                marker, identity = next(iter(ref.items()))
                actual[key] = restore_vehicle_index(db, marker, identity)
            self.assertEqual(actual, expected)
        vehicle = db.execute("SELECT * FROM vehicles").fetchone()
        self.assertEqual(json.loads(vehicle[3]), [10, 999, 10])
        rows = db.execute(
            "SELECT category_id,route_key,request_address FROM vehicle_ecus ORDER BY category_id"
        ).fetchall()
        self.assertEqual(rows, [(10, "10:17", None), (11, None, None)])
        self.assertEqual(
            db.execute("SELECT count(*) FROM vehicle_connections").fetchone()[0], 2
        )

    def test_partial_index_preserves_absent_sections(self):
        db, values = self.fixture()
        db.execute("DELETE FROM source_document_parts WHERE pointer_id IN (2,3)")
        normalize(db)
        self.assertEqual(
            db.execute("SELECT count(*) FROM source_document_parts").fetchone()[0], 1
        )
        self.assertEqual(
            db.execute("SELECT count(*) FROM install_set_owners").fetchone()[0], 0
        )
        self.assertEqual(
            db.execute("SELECT count(*) FROM vehicle_ecus").fetchone()[0], 0
        )
        self.assertEqual(
            json.loads(
                db.execute("SELECT install_set_ids FROM vehicles").fetchone()[0]
            ),
            [10, 999, 10],
        )

    def test_reject_unknown_shape_before_creating_schema(self):
        db, values = self.fixture()
        values["vehicles"]["1"]["vehicle_type"] = True
        db.execute(
            "UPDATE source_document_parts SET data=? WHERE pointer_id=1",
            (compress(json.dumps(values["vehicles"]).encode()),),
        )
        with self.assertRaisesRegex(ValueError, "unsupported"):
            normalize(db)
        self.assertIsNone(
            db.execute(
                "SELECT 1 FROM sqlite_master WHERE name='vehicle_definitions'"
            ).fetchone()
        )

    def test_missing_and_corrupt_members(self):
        db, values = self.fixture()
        normalize(db)
        with self.assertRaisesRegex(ValueError, "invalid"):
            restore_vehicle_index(db, "$install_set", True)
        with self.assertRaisesRegex(ValueError, "missing"):
            restore_vehicle_index(db, "$install_set", 999)
        identity = db.execute(
            "SELECT definition_id FROM install_set_owners WHERE install_set_id=10"
        ).fetchone()[0]
        db.execute(
            "DELETE FROM install_set_members WHERE definition_id=? AND position=2",
            (identity,),
        )
        with self.assertRaisesRegex(ValueError, "missing"):
            restore_vehicle_index(db, "$install_set", identity)

    def test_old_projection_mismatch_refuses_replacement(self):
        db, values = self.fixture()
        db.execute(
            "CREATE TABLE vehicles(region TEXT,vehicle_type INTEGER,name TEXT,install_set_ids TEXT)"
        )
        db.execute("INSERT INTO vehicles VALUES('NA',1,'wrong','[]')")
        with self.assertRaisesRegex(ValueError, "changes vehicles"):
            normalize(db)
        self.assertEqual(db.execute("SELECT name FROM vehicles").fetchone()[0], "wrong")


if __name__ == "__main__":
    unittest.main()
