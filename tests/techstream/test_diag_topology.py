import copy
import sqlite3
import unittest
from tools.techstream.diag_topology import TopologyStore, restore_topology


def network():
    return dict(
        can_bus_car_id="0x00000001",
        option_count=2,
        placement_variant_count=1,
        vehicle_type=7,
        vehicle_name="Toyota",
        placement_variants=[
            dict(
                component_groups=["0x00000003"],
                placements=[
                    dict(
                        bus_index=23,
                        bus_name="Bus 1",
                        component_index=1,
                        component_hex="0x01",
                        ecu_domain="Radar",
                        junction_name="Junction",
                        gateway_names=["Gateway"],
                    )
                ],
            )
        ],
    )


class TopologyTests(unittest.TestCase):
    def store(self):
        db = sqlite3.connect(":memory:")
        self.addCleanup(db.close)
        db.executescript("""
          CREATE TABLE text_values(id INTEGER PRIMARY KEY,value TEXT UNIQUE);
          CREATE TABLE search_regions(id INTEGER PRIMARY KEY,name TEXT);
          CREATE TABLE vehicle_definitions(id INTEGER PRIMARY KEY,region_id INTEGER,vehicle_type INTEGER,name_id INTEGER);
          INSERT INTO search_regions VALUES(1,'NA');
          INSERT INTO text_values VALUES(1,'Toyota');
          INSERT INTO vehicle_definitions VALUES(1,1,7,1),(2,1,8,1);
        """)
        return db, TopologyStore(db)

    def test_roundtrip_and_shared_network(self):
        db, s = self.store()
        original = network()
        ref = s.normalize("NA", original)
        self.assertEqual(restore_topology(db, ref["$can_topology"]), original)
        second = copy.deepcopy(original)
        second["vehicle_type"] = 8
        ref2 = s.normalize("NA", second)
        self.assertEqual(restore_topology(db, ref2["$can_topology"]), second)
        self.assertEqual(
            db.execute("SELECT count(*) FROM topology_networks").fetchone()[0], 1
        )
        self.assertEqual(
            db.execute("SELECT count(*) FROM topology_placements").fetchone()[0], 1
        )

    def test_unknown_shape_preserved(self):
        db, s = self.store()
        for field, value in (
            ("option_count", True),
            ("can_bus_car_id", "0x1"),
            ("new_field", 7),
        ):
            original = network()
            original[field] = value
            self.assertEqual(s.normalize("NA", original), original)

    def test_missing_trailing_association(self):
        db, s = self.store()
        identity = s.normalize("NA", network())["$can_topology"]
        db.execute("DELETE FROM topology_gateways")
        with self.assertRaisesRegex(ValueError, "order/count"):
            restore_topology(db, identity)

    def test_conflicting_network(self):
        db, s = self.store()
        s.normalize("NA", network())
        altered = network()
        altered["option_count"] = 3
        with self.assertRaisesRegex(ValueError, "conflicting CAN network"):
            s.normalize("NA", altered)


if __name__ == "__main__":
    unittest.main()
