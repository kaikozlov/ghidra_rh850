"""Canonical vehicle, installation and route entities for the source index.

Ordered source memberships remain lossless. Browse views deliberately collapse
identical installed connections, as the previous CLI projection did.
"""

from __future__ import annotations

import json

from tools.techstream.diag_codec import compress, decompress

MARKERS = ("$vehicle_definition", "$install_set", "$vehicle_route")
ROUTE_INTS = (
    "address_extension",
    "change_comm_if_case",
    "functional_address",
    "functional_address_field",
    "legislated_request_address",
    "protocol_info_id",
    "request_address",
    "request_address_field",
    "request_mask",
    "response_mask",
    "route_selector",
)
ROUTE_NULLABLE_INTS = (
    "functional_request_address",
    "physical_request_address",
    "physical_response_address",
)
ROUTE_TEXT = ("controller", "request_address_field_semantics", "transport_kind")
ROUTE_FIELDS = ROUTE_INTS + ROUTE_NULLABLE_INTS + ROUTE_TEXT
CONNECTION_FIELDS = frozenset(
    {
        "category_id",
        "connection_comm_set_id",
        "connection_frame_id",
        "connection_route_selector",
        "route_key",
    }
)
DDL = (
    """
CREATE TABLE IF NOT EXISTS text_values(id INTEGER PRIMARY KEY,value TEXT NOT NULL UNIQUE);
CREATE TABLE vehicle_definitions(
 id INTEGER PRIMARY KEY,region_id INTEGER NOT NULL REFERENCES search_regions(id),
 vehicle_type INTEGER NOT NULL,name_id INTEGER NOT NULL REFERENCES text_values(id),
 install_count INTEGER NOT NULL,UNIQUE(region_id,vehicle_type));
CREATE TABLE vehicle_install_references(
 vehicle_id INTEGER NOT NULL REFERENCES vehicle_definitions(id),position INTEGER NOT NULL,
 install_set_id INTEGER NOT NULL,PRIMARY KEY(vehicle_id,position)) WITHOUT ROWID;
CREATE TABLE vehicle_connections(
 id INTEGER PRIMARY KEY,category_id INTEGER NOT NULL,comm_set_id INTEGER NOT NULL,
 frame_id INTEGER NOT NULL,route_selector INTEGER NOT NULL,has_route INTEGER NOT NULL);
CREATE TABLE install_set_definitions(id INTEGER PRIMARY KEY,member_count INTEGER NOT NULL);
CREATE TABLE install_set_members(
 definition_id INTEGER NOT NULL REFERENCES install_set_definitions(id),position INTEGER NOT NULL,
 connection_id INTEGER NOT NULL REFERENCES vehicle_connections(id),PRIMARY KEY(definition_id,position)) WITHOUT ROWID;
CREATE TABLE install_set_owners(
 region_id INTEGER NOT NULL REFERENCES search_regions(id),install_set_id INTEGER NOT NULL,
 definition_id INTEGER NOT NULL REFERENCES install_set_definitions(id),PRIMARY KEY(region_id,install_set_id)) WITHOUT ROWID;
CREATE TABLE vehicle_route_owners(
 region_id INTEGER NOT NULL REFERENCES search_regions(id),category_id INTEGER NOT NULL,route_selector INTEGER NOT NULL,
 definition_id INTEGER NOT NULL REFERENCES vehicle_route_definitions(id),
 PRIMARY KEY(region_id,category_id,route_selector)) WITHOUT ROWID;
"""
    + "CREATE TABLE vehicle_route_definitions(id INTEGER PRIMARY KEY,"
    + ",".join(
        [f"{k} INTEGER NOT NULL" for k in ROUTE_INTS]
        + [f"{k} INTEGER" for k in ROUTE_NULLABLE_INTS]
        + [f"{k}_id INTEGER REFERENCES text_values(id)" for k in ROUTE_TEXT]
    )
    + ");"
)

VEHICLES_SQL = """
SELECT g.name AS region,v.vehicle_type,t.value AS name,
 (SELECT json_group_array(install_set_id)
  FROM (SELECT install_set_id FROM vehicle_install_references r
        WHERE r.vehicle_id=v.id ORDER BY position)) AS install_set_ids
FROM search_regions g JOIN vehicle_definitions v ON v.region_id=g.id
JOIN text_values t ON t.id=v.name_id
"""
VEHICLE_ECUS_SQL = """
SELECT DISTINCT g.name AS region,v.vehicle_type,s.install_set_id,
 c.category_id,c.route_selector,c.frame_id AS connection_frame_id,
 CASE WHEN c.has_route=1 THEN CAST(c.category_id AS TEXT)||':'||CAST(c.route_selector AS TEXT) ELSE NULL END AS route_key,
 d.physical_request_address AS request_address,d.address_extension,k.value AS transport_kind
FROM search_regions g
JOIN vehicle_definitions v ON v.region_id=g.id
JOIN vehicle_install_references r ON r.vehicle_id=v.id
JOIN install_set_owners s ON s.region_id=v.region_id AND s.install_set_id=r.install_set_id
JOIN install_set_members m ON m.definition_id=s.definition_id
JOIN vehicle_connections c ON c.id=m.connection_id
LEFT JOIN vehicle_route_owners o ON c.has_route=1 AND o.region_id=v.region_id
 AND o.category_id=c.category_id AND o.route_selector=c.route_selector
LEFT JOIN vehicle_route_definitions d ON d.id=o.definition_id
LEFT JOIN text_values k ON k.id=d.transport_kind_id
"""


VEHICLE_COUNTS_SQL = """
SELECT g.name AS region,v.vehicle_type,count(DISTINCT c.category_id) AS ecu_count
FROM search_regions g JOIN vehicle_definitions v ON v.region_id=g.id
JOIN vehicle_install_references r ON r.vehicle_id=v.id
JOIN install_set_owners s ON s.region_id=v.region_id AND s.install_set_id=r.install_set_id
JOIN install_set_members m ON m.definition_id=s.definition_id
JOIN vehicle_connections c ON c.id=m.connection_id
GROUP BY g.name,v.vehicle_type
"""


def integer(value):
    return type(value) is int and -(1 << 63) <= value < (1 << 63)


def _valid_part(kind, values):
    if not isinstance(values, dict):
        return False
    for key, value in values.items():
        if not isinstance(key, str):
            return False
        if kind == "vehicles":
            if not isinstance(value, dict) or set(value) != {
                "vehicle_type",
                "name",
                "install_set_ids",
            }:
                return False
            if (
                not integer(value["vehicle_type"])
                or key != str(value["vehicle_type"])
                or not isinstance(value["name"], str)
            ):
                return False
            if not isinstance(value["install_set_ids"], list) or not all(
                integer(x) for x in value["install_set_ids"]
            ):
                return False
        elif kind == "install_sets":
            try:
                number = int(key)
            except ValueError:
                return False
            if not integer(number) or str(number) != key or not isinstance(value, list):
                return False
            for row in value:
                if not isinstance(row, dict) or set(row) != CONNECTION_FIELDS:
                    return False
                if not all(integer(row[k]) for k in CONNECTION_FIELDS - {"route_key"}):
                    return False
                expected = f"{row['category_id']}:{row['connection_route_selector']}"
                if row["route_key"] is not None and row["route_key"] != expected:
                    return False
        elif kind == "routes":
            if not isinstance(value, dict) or set(value) != set(ROUTE_FIELDS):
                return False
            try:
                category, selector = map(int, key.split(":"))
            except ValueError:
                return False
            if (
                not integer(category)
                or not integer(selector)
                or key != f"{category}:{selector}"
                or selector != value["route_selector"]
            ):
                return False
            if not all(integer(value[k]) for k in ROUTE_INTS):
                return False
            if not all(
                value[k] is None or integer(value[k]) for k in ROUTE_NULLABLE_INTS
            ):
                return False
            if not isinstance(
                value["request_address_field_semantics"], str
            ) or not isinstance(value["transport_kind"], str):
                return False
            if value["controller"] is not None and not isinstance(
                value["controller"], str
            ):
                return False
        else:
            return False
    return True


class VehicleIndexStore:
    def __init__(self, db):
        self.db = db
        self.strings = {}
        self.connections = {}
        self.install_sets = {}
        self.routes = {}

    def text(self, value):
        if value is None:
            return None
        if value not in self.strings:
            self.db.execute(
                "INSERT OR IGNORE INTO text_values(value) VALUES (?)", (value,)
            )
            self.strings[value] = self.db.execute(
                "SELECT id FROM text_values WHERE value=?", (value,)
            ).fetchone()[0]
        return self.strings[value]

    def route(self, value):
        key = tuple(value[k] for k in ROUTE_INTS + ROUTE_NULLABLE_INTS) + tuple(
            self.text(value[k]) for k in ROUTE_TEXT
        )
        if key not in self.routes:
            columns = (
                ROUTE_INTS + ROUTE_NULLABLE_INTS + tuple(k + "_id" for k in ROUTE_TEXT)
            )
            self.routes[key] = self.db.execute(
                f"INSERT INTO vehicle_route_definitions({','.join(columns)}) VALUES ({','.join('?' for _ in key)})",
                key,
            ).lastrowid
        return self.routes[key]

    def install_set(self, rows):
        members = []
        for row in rows:
            key = (
                row["category_id"],
                row["connection_comm_set_id"],
                row["connection_frame_id"],
                row["connection_route_selector"],
                int(row["route_key"] is not None),
            )
            if key not in self.connections:
                self.connections[key] = self.db.execute(
                    "INSERT INTO vehicle_connections(category_id,comm_set_id,frame_id,route_selector,has_route) VALUES (?,?,?,?,?)",
                    key,
                ).lastrowid
            members.append(self.connections[key])
        key = tuple(members)
        if key not in self.install_sets:
            identity = self.db.execute(
                "INSERT INTO install_set_definitions(member_count) VALUES (?)",
                (len(members),),
            ).lastrowid
            self.db.executemany(
                "INSERT INTO install_set_members VALUES (?,?,?)",
                ((identity, pos, connection) for pos, connection in enumerate(members)),
            )
            self.install_sets[key] = identity
        return self.install_sets[key]

    def part(self, region, kind, values):
        result = {}
        for key, value in values.items():
            if kind == "vehicles":
                identity = self.db.execute(
                    "INSERT INTO vehicle_definitions(region_id,vehicle_type,name_id,install_count) VALUES (?,?,?,?)",
                    (
                        region,
                        value["vehicle_type"],
                        self.text(value["name"]),
                        len(value["install_set_ids"]),
                    ),
                ).lastrowid
                self.db.executemany(
                    "INSERT INTO vehicle_install_references VALUES (?,?,?)",
                    (
                        (identity, pos, set_id)
                        for pos, set_id in enumerate(value["install_set_ids"])
                    ),
                )
                result[key] = {"$vehicle_definition": identity}
            elif kind == "install_sets":
                identity = self.install_set(value)
                self.db.execute(
                    "INSERT INTO install_set_owners VALUES (?,?,?)",
                    (region, int(key), identity),
                )
                result[key] = {"$install_set": identity}
            else:
                identity = self.route(value)
                category, selector = map(int, key.split(":"))
                self.db.execute(
                    "INSERT INTO vehicle_route_owners VALUES (?,?,?,?)",
                    (region, category, selector, identity),
                )
                result[key] = {"$vehicle_route": identity}
        return result


def restore_vehicle_index(db, marker, identity):
    if marker not in MARKERS or not integer(identity) or identity <= 0:
        raise ValueError("invalid vehicle index reference")
    if marker == "$vehicle_definition":
        row = db.execute(
            "SELECT v.vehicle_type,t.value,v.install_count FROM vehicle_definitions v JOIN text_values t ON t.id=v.name_id WHERE v.id=?",
            (identity,),
        ).fetchone()
        if row is None:
            raise ValueError("missing vehicle definition")
        vehicle_type, name, count = row
        refs = []
        for position, install_set in db.execute(
            "SELECT position,install_set_id FROM vehicle_install_references WHERE vehicle_id=? ORDER BY position",
            (identity,),
        ):
            if position != len(refs):
                raise ValueError("invalid vehicle install order")
            refs.append(install_set)
        if len(refs) != count:
            raise ValueError("missing vehicle install references")
        return dict(vehicle_type=vehicle_type, name=name, install_set_ids=refs)
    if marker == "$install_set":
        count = db.execute(
            "SELECT member_count FROM install_set_definitions WHERE id=?", (identity,)
        ).fetchone()
        if count is None:
            raise ValueError("missing install set definition")
        result = []
        for position, category, comm, frame, selector, has_route in db.execute(
            """
          SELECT m.position,c.category_id,c.comm_set_id,c.frame_id,c.route_selector,c.has_route
          FROM install_set_members m JOIN vehicle_connections c ON c.id=m.connection_id
          WHERE m.definition_id=? ORDER BY m.position""",
            (identity,),
        ):
            if position != len(result) or has_route not in (0, 1):
                raise ValueError("invalid install set member")
            result.append(
                dict(
                    category_id=category,
                    connection_comm_set_id=comm,
                    connection_frame_id=frame,
                    connection_route_selector=selector,
                    route_key=f"{category}:{selector}" if has_route else None,
                )
            )
        if len(result) != count[0]:
            raise ValueError("missing install set members")
        return result
    columns = ROUTE_INTS + ROUTE_NULLABLE_INTS + tuple(k + "_id" for k in ROUTE_TEXT)
    row = db.execute(
        f"SELECT {','.join(columns)} FROM vehicle_route_definitions WHERE id=?",
        (identity,),
    ).fetchone()
    if row is None:
        raise ValueError("missing vehicle route definition")
    result = dict(zip(ROUTE_INTS + ROUTE_NULLABLE_INTS, row[:14]))
    for key, text_id in zip(ROUTE_TEXT, row[14:]):
        if text_id is None:
            if key != "controller":
                raise ValueError("missing route description")
            result[key] = None
        else:
            text = db.execute(
                "SELECT value FROM text_values WHERE id=?", (text_id,)
            ).fetchone()
            if text is None:
                raise ValueError("missing route text")
            result[key] = text[0]
    return result


def normalize(db):
    parts = []
    for document, pointer, path, packed in db.execute("""
      SELECT p.document_id,p.pointer_id,s.pointer,p.data FROM source_document_parts p
      JOIN source_pointers s ON s.id=p.pointer_id
      JOIN source_documents d ON d.id=p.document_id WHERE d.member='index.json'"""):
        components = path.split("/")
        if (
            len(components) != 4
            or components[1] != "regions"
            or components[3] not in ("vehicles", "install_sets", "routes")
        ):
            continue
        region, kind = components[2], components[3]
        values = json.loads(decompress(packed))
        if not _valid_part(kind, values):
            raise ValueError(
                f"unsupported vehicle index shape at {path}; no data omitted"
            )
        region_id = db.execute(
            "SELECT id FROM search_regions WHERE name=?", (region,)
        ).fetchone()
        if region_id is None:
            raise ValueError(f"unknown vehicle region {region}")
        parts.append((document, pointer, region_id[0], kind, packed))
    if not parts:
        return
    for statement in DDL.split(";"):
        if statement.strip():
            db.execute(statement)
    store = VehicleIndexStore(db)
    for document, pointer, region, kind, packed in parts:
        values = json.loads(decompress(packed))
        result = store.part(region, kind, values)
        data = json.dumps(
            result, ensure_ascii=False, sort_keys=True, separators=(",", ":")
        ).encode()
        db.execute(
            "UPDATE source_document_parts SET data=? WHERE document_id=? AND pointer_id=?",
            (compress(data), document, pointer),
        )
    # New relation cardinalities must be visible before the validation joins.
    # Otherwise SQLite may choose an expensive scan order for the fresh schema.
    for table in (
        "vehicle_definitions",
        "vehicle_install_references",
        "vehicle_connections",
        "install_set_definitions",
        "install_set_members",
        "install_set_owners",
        "vehicle_route_owners",
        "vehicle_route_definitions",
    ):
        db.execute(f"ANALYZE {table}")
    # Verify the public projection before replacing it; source data remains
    # richer (ordered duplicate members and unresolved installation references).
    for old, query in (("vehicles", VEHICLES_SQL), ("vehicle_ecus", VEHICLE_ECUS_SQL)):
        if (
            db.execute("SELECT 1 FROM sqlite_master WHERE name=?", (old,)).fetchone()
            is None
        ):
            continue
        for left, right in (
            (f"SELECT * FROM {old}", query),
            (query, f"SELECT * FROM {old}"),
        ):
            if db.execute(f"SELECT 1 FROM ({left} EXCEPT {right}) LIMIT 1").fetchone():
                raise ValueError(f"canonical vehicle model changes {old} output")
    for name in (
        "vehicle_ecus",
        "installed_ecus",
        "vehicle_install_sets",
        "transport_routes",
        "vehicles",
    ):
        row = db.execute(
            "SELECT type FROM sqlite_master WHERE name=?", (name,)
        ).fetchone()
        if row:
            db.execute(f"DROP {row[0].upper()} {name}")
    db.execute("CREATE VIEW vehicles AS " + VEHICLES_SQL)
    db.execute("CREATE VIEW vehicle_ecus AS " + VEHICLE_ECUS_SQL)
    db.execute("CREATE VIEW vehicle_ecu_counts AS " + VEHICLE_COUNTS_SQL)
