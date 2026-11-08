"""Decoded legacy ROB signals, scaling and ordered display choices.

Origins remain small views of shared semantic definitions. No raw OEM records
or inference about execution support is needed to reconstruct these facts.
"""

import math
from tools.techstream.diag_freeze_physical import Writer as PhysicalWriter, integer

INTS = (
    "bdid",
    "bit_end",
    "bit_start",
    "exception_handler_flag",
    "exception_handler_id",
    "graph_max",
    "graph_min",
    "name_string_index",
    "pattern_display_key",
    "physical_data_key",
    "presentation_mode",
    "signal_key",
    "sort_key",
    "support_mode",
)
TEXTS = ("name", "short_name", "decoder", "support_rule")
PHYSICAL = (
    "decimal_point_count",
    "div",
    "mul",
    "offset",
    "physical_data_key",
    "record",
    "sign_mode",
    "table",
    "unit_key",
)
SHAPE = (
    set(INTS)
    | set(TEXTS)
    | {
        "data_min",
        "data_max",
        "source",
        "table",
        "record",
        "physical_variants",
        "pattern_display",
    }
)
DDL = (
    """
CREATE TABLE IF NOT EXISTS legacy_rob_physical(id INTEGER PRIMARY KEY,
decimal_point_count INTEGER NOT NULL,div INTEGER NOT NULL,mul INTEGER NOT NULL,offset INTEGER NOT NULL,physical_data_key INTEGER NOT NULL,record INTEGER NOT NULL,sign_mode INTEGER NOT NULL,table_number INTEGER NOT NULL,unit_key INTEGER NOT NULL,unit_id INTEGER NOT NULL REFERENCES freeze_units(id));
CREATE TABLE IF NOT EXISTS legacy_rob_definitions(id INTEGER PRIMARY KEY,
"""
    + ",".join(k + " INTEGER NOT NULL" for k in INTS)
    + ","
    + ",".join(k + "_id INTEGER REFERENCES text_values(id)" for k in TEXTS)
    + """
,data_min REAL NOT NULL,data_max REAL NOT NULL,pattern_list_id INTEGER NOT NULL REFERENCES freeze_pattern_lists(id),physical_count INTEGER NOT NULL);
CREATE TABLE IF NOT EXISTS legacy_rob_variants(definition_id INTEGER NOT NULL REFERENCES legacy_rob_definitions(id),position INTEGER NOT NULL,physical_id INTEGER NOT NULL REFERENCES legacy_rob_physical(id),PRIMARY KEY(definition_id,position)) WITHOUT ROWID;
CREATE TABLE IF NOT EXISTS legacy_rob_entries(id INTEGER PRIMARY KEY,definition_id INTEGER NOT NULL REFERENCES legacy_rob_definitions(id),source_id INTEGER NOT NULL REFERENCES text_values(id),table_number INTEGER NOT NULL,record_number INTEGER NOT NULL);
"""
)


class Store:
    def __init__(self, db):
        self.db = db
        db.executescript(DDL)
        self.physical = PhysicalWriter(db)
        # Share existing semantic unit/choice entities, including those produced
        # earlier in this export. Do not allocate duplicate cross-domain values.
        for table in ("freeze_units", "freeze_patterns"):
            self.physical.cache[table] = {
                tuple(r[1:]): r[0] for r in db.execute("SELECT * FROM " + table)
            }
        self.physical.cache["pattern_lists"] = {
            tuple(
                x[0]
                for x in db.execute(
                    "SELECT pattern_id FROM freeze_pattern_members WHERE list_id=? ORDER BY position",
                    (i,),
                )
            ): i
            for (i,) in db.execute("SELECT id FROM freeze_pattern_lists")
        }
        self.cache = {}
        for table in ("legacy_rob_physical", "legacy_rob_entries"):
            self.cache[table] = {
                tuple(r[1:]): r[0] for r in db.execute("SELECT * FROM " + table)
            }
        self.definitions = {}
        for row in db.execute("SELECT * FROM legacy_rob_definitions"):
            variants = tuple(
                x[0]
                for x in db.execute(
                    "SELECT physical_id FROM legacy_rob_variants WHERE definition_id=? ORDER BY position",
                    (row[0],),
                )
            )
            self.definitions[tuple(row[1:]) + variants] = row[0]

    def intern(self, table, values):
        cache = self.cache.setdefault(table, {})
        if values not in cache:
            cache[values] = self.db.execute(
                "INSERT INTO "
                + table
                + " VALUES("
                + ",".join("?" for _ in range(len(values) + 1))
                + ")",
                (None, *values),
            ).lastrowid
        return cache[values]

    def variant(self, row):
        if (
            not isinstance(row, dict)
            or set(row) != set(PHYSICAL) | {"units"}
            or not isinstance(row["units"], list)
            or len(row["units"]) != 1
        ):
            raise ValueError("unsupported ROB physical shape")
        u = row["units"][0]
        if not isinstance(u, dict) or set(u) != {
            "genre_id",
            "name",
            "name_string_index",
            "record",
        }:
            raise ValueError("unsupported ROB unit")
        unit = self.physical.unit(
            {
                "genre_id": u["genre_id"],
                "record": u["record"],
                "string_index": u["name_string_index"],
                "table": 15,
                "text": u["name"],
            }
        )
        return self.intern(
            "legacy_rob_physical", tuple(integer(row[k]) for k in PHYSICAL) + (unit,)
        )

    def row(self, row):
        if type(row) is not dict or set(row) != SHAPE:
            return row
        try:
            ints = tuple(integer(row[k]) for k in INTS)
            texts = tuple(self.physical.string(row[k]) for k in TEXTS)
            ranges = tuple(row[k] for k in ("data_min", "data_max"))
            if any(
                type(x) is not float
                or not math.isfinite(x)
                or (x == 0 and math.copysign(1, x) < 0)
                for x in ranges
            ):
                return row
            if type(row["source"]) is not str:
                return row
            origin = (
                self.physical.string(row["source"]),
                integer(row["table"]),
                integer(row["record"]),
            )
            if (
                type(row["physical_variants"]) is not list
                or type(row["pattern_display"]) is not list
            ):
                return row
            variants = tuple(self.variant(v) for v in row["physical_variants"])
            patterns = []
            for p in row["pattern_display"]:
                if type(p) is not dict or set(p) != {
                    "name",
                    "name_string_index",
                    "record",
                    "table",
                    "value",
                }:
                    return row
                patterns.append(
                    {
                        "text": p["name"],
                        "string_index": p["name_string_index"],
                        "record": p["record"],
                        "table": p["table"],
                        "value": p["value"],
                    }
                )
            values = (
                ints
                + texts
                + ranges
                + (self.physical.patterns(patterns), len(variants))
            )
            key = values + variants
            if key not in self.definitions:
                ident = self.db.execute(
                    "INSERT INTO legacy_rob_definitions VALUES("
                    + ",".join("?" for _ in range(len(values) + 1))
                    + ")",
                    (None, *values),
                ).lastrowid
                self.db.executemany(
                    "INSERT INTO legacy_rob_variants VALUES(?,?,?)",
                    [(ident, i, v) for i, v in enumerate(variants)],
                )
                self.definitions[key] = ident
            return {
                "$legacy_rob_signal": self.intern(
                    "legacy_rob_entries", (self.definitions[key], *origin)
                )
            }
        except (TypeError, ValueError):
            return row

    def normalize(self, document):
        value = document.get("legacy_rob")
        if isinstance(value, dict):
            for family in value.get("families", []):
                if isinstance(family, dict) and isinstance(family.get("signals"), list):
                    family["signals"] = [self.row(v) for v in family["signals"]]
        return document


def restore(db, ident):
    if type(ident) is not int or ident <= 0:
        raise ValueError("invalid legacy ROB reference")
    entry = db.execute(
        "SELECT e.definition_id,t.value,e.table_number,e.record_number FROM legacy_rob_entries e JOIN text_values t ON t.id=e.source_id WHERE e.id=?",
        (ident,),
    ).fetchone()
    if entry is None:
        raise ValueError("missing legacy ROB origin")
    row = db.execute(
        "SELECT * FROM legacy_rob_definitions WHERE id=?", (entry[0],)
    ).fetchone()
    if row is None:
        raise ValueError("missing legacy ROB definition")
    vals = list(row[1:])
    out = dict(zip(INTS, vals[: len(INTS)]))
    pos = len(INTS)
    for k in TEXTS:
        text_id = vals[pos]
        pos += 1
        text = (
            None
            if text_id is None
            else db.execute(
                "SELECT value FROM text_values WHERE id=?", (text_id,)
            ).fetchone()
        )
        if text_id is not None and text is None:
            raise ValueError("missing legacy ROB text")
        out[k] = None if text is None else text[0]
    out["data_min"], out["data_max"], pattern_list, count = vals[pos:]
    out.update(
        source=entry[1],
        table=entry[2],
        record=entry[3],
        physical_variants=[],
        pattern_display=[],
    )
    for position, *v in db.execute(
        "SELECT m.position,p.* FROM legacy_rob_variants m JOIN legacy_rob_physical p ON p.id=m.physical_id WHERE m.definition_id=? ORDER BY m.position",
        (entry[0],),
    ):
        if position != len(out["physical_variants"]):
            raise ValueError("invalid ROB physical order")
        variant = dict(zip(PHYSICAL, v[1:-1]))
        u = db.execute(
            "SELECT u.genre_id,t.value,u.string_index,u.record,u.table_type FROM freeze_units u LEFT JOIN text_values t ON t.id=u.text_id WHERE u.id=?",
            (v[-1],),
        ).fetchone()
        if u is None or u[4] != 15:
            raise ValueError("invalid ROB unit")
        variant["units"] = [
            dict(zip(("genre_id", "name", "name_string_index", "record"), u[:4]))
        ]
        out["physical_variants"].append(variant)
    if len(out["physical_variants"]) != count:
        raise ValueError("incomplete ROB physical variants")
    expected = db.execute(
        "SELECT entry_count FROM freeze_pattern_lists WHERE id=?", (pattern_list,)
    ).fetchone()
    if expected is None:
        raise ValueError("missing ROB pattern list")
    for position, *p in db.execute(
        "SELECT m.position,t.value,p.string_index,p.record,p.table_type,p.value FROM freeze_pattern_members m JOIN freeze_patterns p ON p.id=m.pattern_id LEFT JOIN text_values t ON t.id=p.text_id WHERE m.list_id=? ORDER BY m.position",
        (pattern_list,),
    ):
        if position != len(out["pattern_display"]):
            raise ValueError("invalid ROB pattern order")
        out["pattern_display"].append(
            dict(zip(("name", "name_string_index", "record", "table", "value"), p))
        )
    if len(out["pattern_display"]) != expected[0]:
        raise ValueError("incomplete ROB patterns")
    return out
