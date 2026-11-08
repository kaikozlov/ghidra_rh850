"""Product physical definitions: semantic scaling, unit and ordered value labels."""

import json

from tools.techstream.diag_codec import compress, decompress

SCHEMA = """
CREATE TABLE freeze_units(id INTEGER PRIMARY KEY,genre_id INTEGER NOT NULL,record INTEGER NOT NULL,string_index INTEGER NOT NULL,table_type INTEGER NOT NULL,text_id INTEGER REFERENCES text_values(id));
CREATE TABLE freeze_patterns(id INTEGER PRIMARY KEY,record INTEGER NOT NULL,string_index INTEGER NOT NULL,table_type INTEGER NOT NULL,text_id INTEGER REFERENCES text_values(id),value INTEGER NOT NULL);
CREATE TABLE freeze_pattern_lists(id INTEGER PRIMARY KEY,entry_count INTEGER NOT NULL CHECK(entry_count>=0));
CREATE TABLE freeze_pattern_members(list_id INTEGER NOT NULL REFERENCES freeze_pattern_lists(id),position INTEGER NOT NULL,pattern_id INTEGER NOT NULL REFERENCES freeze_patterns(id),PRIMARY KEY(list_id,position)) WITHOUT ROWID;
CREATE TABLE freeze_physical_defs(id INTEGER PRIMARY KEY,bit_width INTEGER NOT NULL,decimal_point_count INTEGER NOT NULL,div INTEGER NOT NULL,mul INTEGER NOT NULL,offset INTEGER NOT NULL,physical_data_key INTEGER NOT NULL,record INTEGER NOT NULL,sign_mode INTEGER NOT NULL,table_type INTEGER NOT NULL,unit_key INTEGER NOT NULL,unit_id INTEGER NOT NULL REFERENCES freeze_units(id),pattern_list_id INTEGER NOT NULL REFERENCES freeze_pattern_lists(id));
"""
FIELDS = (
    "bit_width",
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
UNIT = ("genre_id", "record", "string_index", "table", "text")
PATTERN = ("record", "string_index", "table", "text", "value")


def integer(v):
    if type(v) is not int or not -(1 << 63) <= v < (1 << 63):
        raise ValueError("unsupported physical integer")
    return v


class Writer:
    def __init__(self, db):
        self.db = db
        self.cache = {}
        self.text = {}

    def string(self, v):
        if v is None:
            return None
        if type(v) is not str:
            raise ValueError("unsupported physical label")
        if v not in self.text:
            self.db.execute("INSERT OR IGNORE INTO text_values(value) VALUES(?)", (v,))
            self.text[v] = self.db.execute(
                "SELECT id FROM text_values WHERE value=?", (v,)
            ).fetchone()[0]
        return self.text[v]

    def row(self, table, values):
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

    def unit(self, v):
        if type(v) is not dict or set(v) != set(UNIT):
            raise ValueError("unsupported physical unit")
        return self.row(
            "freeze_units",
            tuple(integer(v[k]) for k in UNIT[:4]) + (self.string(v["text"]),),
        )

    def pattern(self, v):
        if type(v) is not dict or set(v) != set(PATTERN):
            raise ValueError("unsupported physical pattern")
        return self.row(
            "freeze_patterns",
            tuple(integer(v[k]) for k in PATTERN[:3])
            + (self.string(v["text"]), integer(v["value"])),
        )

    def patterns(self, rows):
        if type(rows) is not list:
            raise ValueError("unsupported physical pattern list")
        ids = tuple(self.pattern(v) for v in rows)
        cache = self.cache.setdefault("pattern_lists", {})
        if ids not in cache:
            id = self.db.execute(
                "INSERT INTO freeze_pattern_lists(entry_count) VALUES(?)", (len(ids),)
            ).lastrowid
            self.db.executemany(
                "INSERT INTO freeze_pattern_members VALUES(?,?,?)",
                [(id, i, p) for i, p in enumerate(ids)],
            )
            cache[ids] = id
        return cache[ids]

    def definition(self, v):
        if type(v) is not dict or set(v) != set(FIELDS) | {"units", "patterns"}:
            raise ValueError("unsupported physical definition")
        if type(v["units"]) is not list or len(v["units"]) != 1:
            raise ValueError("physical definition requires explicit single-unit shape")
        values = tuple(integer(v[k]) for k in FIELDS) + (
            self.unit(v["units"][0]),
            self.patterns(v["patterns"]),
        )
        return self.row("freeze_physical_defs", values)

    def transform(self, v):
        if type(v) is dict:
            if set(v) == set(FIELDS) | {"units", "patterns"}:
                try:
                    return {"$freeze_physical": self.definition(v)}
                except (ValueError, TypeError):
                    pass
            return {k: self.transform(x) for k, x in v.items()}
        if type(v) is list:
            return [self.transform(x) for x in v]
        return v


def restore_freeze_physical(db, id):
    if type(id) is not int or id <= 0:
        raise ValueError("invalid freeze physical reference")
    row = db.execute(
        "SELECT bit_width,decimal_point_count,div,mul,offset,physical_data_key,record,sign_mode,table_type,unit_key,unit_id,pattern_list_id FROM freeze_physical_defs WHERE id=?",
        (id,),
    ).fetchone()
    if row is None:
        raise ValueError("missing freeze physical definition")
    result = dict(zip(FIELDS, row[:10]))
    unit = db.execute(
        "SELECT u.genre_id,u.record,u.string_index,u.table_type,t.value FROM freeze_units u LEFT JOIN text_values t ON t.id=u.text_id WHERE u.id=?",
        (row[10],),
    ).fetchone()
    if unit is None:
        raise ValueError("missing physical unit")
    result["units"] = [dict(zip(UNIT, unit))]
    size = db.execute(
        "SELECT entry_count FROM freeze_pattern_lists WHERE id=?", (row[11],)
    ).fetchone()
    if size is None:
        raise ValueError("missing physical pattern list")
    patterns = []
    for position, *values in db.execute(
        """SELECT m.position,p.record,p.string_index,p.table_type,t.value,p.value
 FROM freeze_pattern_members m JOIN freeze_patterns p ON p.id=m.pattern_id LEFT JOIN text_values t ON t.id=p.text_id
 WHERE m.list_id=? ORDER BY m.position""",
        (row[11],),
    ):
        if position != len(patterns):
            raise ValueError("invalid physical pattern order")
        patterns.append(dict(zip(PATTERN, values)))
    if len(patterns) != size[0]:
        raise ValueError("incomplete physical pattern list")
    result["patterns"] = patterns
    return result


def normalize(db):
    db.executescript(SCHEMA)
    writer = Writer(db)
    changed = 0
    for table, keys in (
        ("source_documents", ("id",)),
        ("source_document_parts", ("document_id", "pointer_id")),
    ):
        for row in db.execute("SELECT " + ",".join(keys) + ",data FROM " + table):
            value = json.loads(decompress(row[-1]))
            result = writer.transform(value)
            if result == value:
                continue
            raw = json.dumps(
                result, ensure_ascii=False, separators=(",", ":"), sort_keys=True
            ).encode()
            db.execute(
                "UPDATE "
                + table
                + " SET data=? WHERE "
                + " AND ".join(k + "=?" for k in keys),
                (compress(raw), *row[:-1]),
            )
            changed += 1
    return changed
