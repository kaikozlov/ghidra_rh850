"""CAN topology definitions shared by vehicle associations, not cloned JSON graphs."""

from __future__ import annotations
import json
from tools.techstream.diag_codec import compress, decompress

DDL = """
CREATE TABLE topology_buses(bus_index INTEGER PRIMARY KEY,name_id INTEGER NOT NULL REFERENCES text_values(id));
CREATE TABLE topology_placements(id INTEGER PRIMARY KEY,bus_index INTEGER NOT NULL REFERENCES topology_buses(bus_index),component_index INTEGER NOT NULL,domain_id INTEGER NOT NULL REFERENCES text_values(id),junction_id INTEGER NOT NULL REFERENCES text_values(id),gateway_count INTEGER NOT NULL);
CREATE TABLE topology_gateways(placement_id INTEGER NOT NULL REFERENCES topology_placements(id),position INTEGER NOT NULL,name_id INTEGER NOT NULL REFERENCES text_values(id),PRIMARY KEY(placement_id,position)) WITHOUT ROWID;
CREATE TABLE topology_variants(id INTEGER PRIMARY KEY,group_count INTEGER NOT NULL,placement_count INTEGER NOT NULL);
CREATE TABLE topology_variant_groups(variant_id INTEGER NOT NULL REFERENCES topology_variants(id),position INTEGER NOT NULL,group_id INTEGER NOT NULL,PRIMARY KEY(variant_id,position)) WITHOUT ROWID;
CREATE TABLE topology_variant_placements(variant_id INTEGER NOT NULL REFERENCES topology_variants(id),position INTEGER NOT NULL,placement_id INTEGER NOT NULL REFERENCES topology_placements(id),PRIMARY KEY(variant_id,position)) WITHOUT ROWID;
CREATE TABLE topology_networks(id INTEGER PRIMARY KEY,can_car_id INTEGER NOT NULL UNIQUE,option_count INTEGER NOT NULL,variant_count INTEGER NOT NULL);
CREATE TABLE topology_network_variants(network_id INTEGER NOT NULL REFERENCES topology_networks(id),position INTEGER NOT NULL,variant_id INTEGER NOT NULL REFERENCES topology_variants(id),PRIMARY KEY(network_id,position)) WITHOUT ROWID;
CREATE TABLE topology_vehicle_views(id INTEGER PRIMARY KEY,vehicle_id INTEGER NOT NULL REFERENCES vehicle_definitions(id),network_id INTEGER NOT NULL REFERENCES topology_networks(id),UNIQUE(vehicle_id,network_id));
"""
NETWORK = {
    "can_bus_car_id",
    "option_count",
    "placement_variant_count",
    "placement_variants",
    "vehicle_name",
    "vehicle_type",
}
PLACEMENT = {
    "bus_index",
    "bus_name",
    "component_hex",
    "component_index",
    "ecu_domain",
    "gateway_names",
    "junction_name",
}


def integer(value):
    return type(value) is int and 0 <= value <= 2**63 - 1


def hex_id(value, width):
    if not isinstance(value, str):
        return False
    try:
        return value == f"0x{int(value, 16):0{width}X}" and 0 <= int(value, 16) < 1 << (
            width * 4
        )
    except ValueError:
        return False


def recognized(value):
    if not isinstance(value, dict) or set(value) != NETWORK:
        return False
    if (
        not hex_id(value["can_bus_car_id"], 8)
        or not integer(value["option_count"])
        or not integer(value["vehicle_type"])
        or not isinstance(value["vehicle_name"], str)
    ):
        return False
    variants = value["placement_variants"]
    if (
        not isinstance(variants, list)
        or type(value["placement_variant_count"]) is not int
        or value["placement_variant_count"] != len(variants)
    ):
        return False
    for variant in variants:
        if (
            not isinstance(variant, dict)
            or set(variant) != {"component_groups", "placements"}
            or not isinstance(variant["component_groups"], list)
            or not all(hex_id(x, 8) for x in variant["component_groups"])
            or not isinstance(variant["placements"], list)
        ):
            return False
        for p in variant["placements"]:
            if (
                not isinstance(p, dict)
                or set(p) != PLACEMENT
                or not integer(p["bus_index"])
                or not integer(p["component_index"])
            ):
                return False
            if (
                not hex_id(p["component_hex"], 2)
                or int(p["component_hex"], 16) != p["component_index"]
            ):
                return False
            if (
                not all(
                    isinstance(p[k], str)
                    for k in ("bus_name", "ecu_domain", "junction_name")
                )
                or not isinstance(p["gateway_names"], list)
                or not all(isinstance(x, str) for x in p["gateway_names"])
            ):
                return False
    return True


class TopologyStore:
    def __init__(self, db):
        self.db = db
        for statement in DDL.split(";"):
            if statement.strip():
                db.execute(statement)
        self.texts = {}
        self.placements = {}
        self.variants = {}
        self.networks = {}

    def text(self, value):
        if value not in self.texts:
            self.db.execute(
                "INSERT OR IGNORE INTO text_values(value) VALUES (?)", (value,)
            )
            self.texts[value] = self.db.execute(
                "SELECT id FROM text_values WHERE value=?", (value,)
            ).fetchone()[0]
        return self.texts[value]

    def placement(self, p):
        key = (
            p["bus_index"],
            p["component_index"],
            p["bus_name"],
            p["ecu_domain"],
            p["junction_name"],
            tuple(p["gateway_names"]),
        )
        if key in self.placements:
            return self.placements[key]
        bus = self.db.execute(
            "SELECT t.value FROM topology_buses b JOIN text_values t ON t.id=b.name_id WHERE b.bus_index=?",
            (p["bus_index"],),
        ).fetchone()
        if bus is None:
            self.db.execute(
                "INSERT INTO topology_buses VALUES (?,?)",
                (p["bus_index"], self.text(p["bus_name"])),
            )
        elif bus[0] != p["bus_name"]:
            raise ValueError("conflicting CAN bus identity")
        identity = self.db.execute(
            "INSERT INTO topology_placements(bus_index,component_index,domain_id,junction_id,gateway_count) VALUES (?,?,?,?,?)",
            (
                p["bus_index"],
                p["component_index"],
                self.text(p["ecu_domain"]),
                self.text(p["junction_name"]),
                len(p["gateway_names"]),
            ),
        ).lastrowid
        self.db.executemany(
            "INSERT INTO topology_gateways VALUES (?,?,?)",
            (
                (identity, i, self.text(name))
                for i, name in enumerate(p["gateway_names"])
            ),
        )
        self.placements[key] = identity
        return identity

    def variant(self, v):
        groups = tuple(int(x, 16) for x in v["component_groups"])
        placements = tuple(self.placement(p) for p in v["placements"])
        previous = self.variants.get(groups)
        if previous:
            if previous[1] != placements:
                raise ValueError("conflicting CAN component-group definition")
            return previous[0]
        identity = self.db.execute(
            "INSERT INTO topology_variants(group_count,placement_count) VALUES (?,?)",
            (len(groups), len(placements)),
        ).lastrowid
        self.db.executemany(
            "INSERT INTO topology_variant_groups VALUES (?,?,?)",
            ((identity, i, value) for i, value in enumerate(groups)),
        )
        self.db.executemany(
            "INSERT INTO topology_variant_placements VALUES (?,?,?)",
            ((identity, i, value) for i, value in enumerate(placements)),
        )
        self.variants[groups] = (identity, placements)
        return identity

    def normalize(self, region, value):
        if not recognized(value):
            return value
        owner = self.db.execute(
            "SELECT v.id,t.value FROM vehicle_definitions v JOIN search_regions r ON r.id=v.region_id JOIN text_values t ON t.id=v.name_id WHERE r.name=? AND v.vehicle_type=?",
            (region, value["vehicle_type"]),
        ).fetchone()
        if owner is None or owner[1] != value["vehicle_name"]:
            return value
        car = int(value["can_bus_car_id"], 16)
        variants = tuple(self.variant(v) for v in value["placement_variants"])
        previous = self.networks.get(car)
        if previous:
            if previous[1:] != (value["option_count"], variants):
                raise ValueError("conflicting CAN network identity")
            network = previous[0]
        else:
            network = self.db.execute(
                "INSERT INTO topology_networks(can_car_id,option_count,variant_count) VALUES (?,?,?)",
                (car, value["option_count"], len(variants)),
            ).lastrowid
            self.db.executemany(
                "INSERT INTO topology_network_variants VALUES (?,?,?)",
                ((network, i, v) for i, v in enumerate(variants)),
            )
            self.networks[car] = (network, value["option_count"], variants)
        self.db.execute(
            "INSERT OR IGNORE INTO topology_vehicle_views(vehicle_id,network_id) VALUES (?,?)",
            (owner[0], network),
        )
        identity = self.db.execute(
            "SELECT id FROM topology_vehicle_views WHERE vehicle_id=? AND network_id=?",
            (owner[0], network),
        ).fetchone()[0]
        return {"$can_topology": identity}


def ordered(db, sql, args, count, label):
    rows = db.execute(sql, args).fetchall()
    if len(rows) != count or any(row[0] != i for i, row in enumerate(rows)):
        raise ValueError(f"invalid {label} order/count")
    return [row[1:] for row in rows]


def restore_topology(db, identity):
    row = db.execute(
        """SELECT n.id,n.can_car_id,n.option_count,n.variant_count,v.vehicle_type,t.value
      FROM topology_vehicle_views o JOIN topology_networks n ON n.id=o.network_id
      JOIN vehicle_definitions v ON v.id=o.vehicle_id JOIN text_values t ON t.id=v.name_id WHERE o.id=?""",
        (identity,),
    ).fetchone()
    if row is None:
        raise ValueError(f"missing CAN topology {identity}")
    network, car, options, count, vehicle, name = row
    variants = []
    for (variant,) in ordered(
        db,
        "SELECT position,variant_id FROM topology_network_variants WHERE network_id=? ORDER BY position",
        (network,),
        count,
        "topology variants",
    ):
        counts = db.execute(
            "SELECT group_count,placement_count FROM topology_variants WHERE id=?",
            (variant,),
        ).fetchone()
        groups = ordered(
            db,
            "SELECT position,group_id FROM topology_variant_groups WHERE variant_id=? ORDER BY position",
            (variant,),
            counts[0],
            "topology groups",
        )
        placements = []
        for (place,) in ordered(
            db,
            "SELECT position,placement_id FROM topology_variant_placements WHERE variant_id=? ORDER BY position",
            (variant,),
            counts[1],
            "topology placements",
        ):
            p = db.execute(
                """SELECT p.bus_index,b.value,p.component_index,d.value,j.value,p.gateway_count
              FROM topology_placements p JOIN topology_buses a ON a.bus_index=p.bus_index
              JOIN text_values b ON b.id=a.name_id JOIN text_values d ON d.id=p.domain_id JOIN text_values j ON j.id=p.junction_id WHERE p.id=?""",
                (place,),
            ).fetchone()
            gateways = ordered(
                db,
                "SELECT g.position,t.value FROM topology_gateways g JOIN text_values t ON t.id=g.name_id WHERE g.placement_id=? ORDER BY g.position",
                (place,),
                p[5],
                "topology gateways",
            )
            placements.append(
                dict(
                    bus_index=p[0],
                    bus_name=p[1],
                    component_index=p[2],
                    component_hex=f"0x{p[2]:02X}",
                    ecu_domain=p[3],
                    junction_name=p[4],
                    gateway_names=[x[0] for x in gateways],
                )
            )
        variants.append(
            dict(
                component_groups=[f"0x{x[0]:08X}" for x in groups],
                placements=placements,
            )
        )
    return dict(
        can_bus_car_id=f"0x{car:08X}",
        option_count=options,
        placement_variant_count=count,
        placement_variants=variants,
        vehicle_type=vehicle,
        vehicle_name=name,
    )


def normalize(db):
    store = TopologyStore(db)
    for doc, pointer, packed, path in db.execute(
        """SELECT d.document_id,d.pointer_id,d.data,p.pointer FROM source_document_parts d JOIN source_pointers p ON p.id=d.pointer_id WHERE p.pointer LIKE '/regions/%/can_topology'"""
    ):
        region = path.split("/")[2]
        value = json.loads(decompress(packed))
        if not isinstance(value, dict):
            continue
        result = {}
        for key, networks in value.items():
            if not isinstance(networks, list):
                result[key] = networks
                continue
            result[key] = [
                store.normalize(region, n)
                if isinstance(n, dict) and str(n.get("vehicle_type")) == key
                else n
                for n in networks
            ]
        data = compress(
            json.dumps(
                result, sort_keys=True, ensure_ascii=False, separators=(",", ":")
            ).encode()
        )
        db.execute(
            "UPDATE source_document_parts SET data=? WHERE document_id=? AND pointer_id=?",
            (data, doc, pointer),
        )
