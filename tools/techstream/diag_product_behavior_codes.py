"""Semantic ROB behavior codes, shared facts with concise origin bindings."""

NUMBERS = (
    "behavior_code",
    "comment_string_index",
    "division_string_index",
    "enabled",
    "exception_handler_flag",
    "exception_handler_id",
    "memory_override",
    "name_string_index",
)
TEXTS = ("name", "comment", "signature", "division", "kind")
COMMON = {"behavior_code", "comment", "name", "signature", "source", "table", "record"}
SHAPES = (COMMON | {"kind"}, COMMON | set(NUMBERS) | {"division"})
DDL = """
CREATE TABLE IF NOT EXISTS text_values(id INTEGER PRIMARY KEY,value TEXT NOT NULL UNIQUE);
CREATE TABLE behavior_code_defs(
 id INTEGER PRIMARY KEY,variant INTEGER NOT NULL CHECK(variant IN(0,1)),
 behavior_code INTEGER NOT NULL,comment_string_index INTEGER,division_string_index INTEGER,
 enabled INTEGER,exception_handler_flag INTEGER,exception_handler_id INTEGER,memory_override INTEGER,name_string_index INTEGER,
 name_id INTEGER REFERENCES text_values(id),comment_id INTEGER REFERENCES text_values(id),
 signature_id INTEGER NOT NULL REFERENCES text_values(id),division_id INTEGER REFERENCES text_values(id),kind_id INTEGER REFERENCES text_values(id),unknown_bytes BLOB);
CREATE TABLE behavior_code_entries(id INTEGER PRIMARY KEY,definition_id INTEGER NOT NULL REFERENCES behavior_code_defs(id),
 source_id INTEGER NOT NULL REFERENCES text_values(id),table_number INTEGER NOT NULL,record_number INTEGER NOT NULL);
"""


def integer(v):
    return type(v) is int and -(1 << 63) <= v < (1 << 63)


ROB_UNKNOWN_LAYOUTS = {163: (("65_67", 3),), 164: (("38_39", 2), ("43_47", 5))}


def rob_unknown_bytes(row):
    if "uninterpreted_bytes" not in row:
        return None
    layout = ROB_UNKNOWN_LAYOUTS.get(row.get("table"))
    value = row["uninterpreted_bytes"]
    if layout is None or type(value) is not dict or set(value) != {key for key, _ in layout}:
        raise ValueError("unsupported ROB unknown fields")
    result = b""
    for key, width in layout:
        if type(value[key]) is not str:
            raise ValueError("invalid ROB unknown bytes")
        raw = bytes.fromhex(value[key])
        if len(raw) != width or raw.hex() != value[key]:
            raise ValueError("invalid ROB unknown range")
        result += raw
    return result


def restore_rob_unknown(row, blob):
    if blob is None:
        return
    layout = ROB_UNKNOWN_LAYOUTS.get(row.get("table"))
    if layout is None or type(blob) is not bytes or len(blob) != sum(width for _, width in layout):
        raise ValueError("invalid ROB unknown storage")
    offset = 0
    value = {}
    for key, width in layout:
        value[key] = blob[offset:offset + width].hex()
        offset += width
    row["uninterpreted_bytes"] = value


class BehaviorCodeStore:
    def __init__(self, db):
        self.db = db
        db.executescript(DDL)
        self.strings = {}
        self.defs = {}
        self.entries = {}

    def text(self, v):
        if v is None:
            return None
        if v not in self.strings:
            self.db.execute("INSERT OR IGNORE INTO text_values(value) VALUES(?)", (v,))
            self.strings[v] = self.db.execute(
                "SELECT id FROM text_values WHERE value=?", (v,)
            ).fetchone()[0]
        return self.strings[v]

    def row(self, row):
        if not isinstance(row, dict):
            return row
        shape = set(row) - {"uninterpreted_bytes"}
        if shape not in SHAPES:
            return row
        variant = SHAPES.index(shape)
        try:
            unknown = rob_unknown_bytes(row)
            if unknown is not None and (variant != 1 or row["table"] != 163):
                return row
        except (ValueError, TypeError):
            return row
        if any(not integer(row[k]) for k in NUMBERS + ("table", "record") if k in row):
            return row
        if not isinstance(row["source"], str) or not isinstance(row["signature"], str):
            return row
        if any(
            row[k] is not None and not isinstance(row[k], str)
            for k in TEXTS
            if k in row
        ):
            return row
        if variant == 0 and not isinstance(row["kind"], str):
            return row
        values = (
            (variant,)
            + tuple(row.get(k) for k in NUMBERS)
            + tuple(self.text(row.get(k)) for k in TEXTS)
            + (unknown,)
        )
        if values not in self.defs:
            columns = ("variant",) + NUMBERS + tuple(k + "_id" for k in TEXTS) + ("unknown_bytes",)
            self.defs[values] = self.db.execute(
                "INSERT INTO behavior_code_defs("
                + ",".join(columns)
                + ") VALUES("
                + ",".join("?" for _ in columns)
                + ")",
                values,
            ).lastrowid
        entry = (
            self.defs[values],
            self.text(row["source"]),
            row["table"],
            row["record"],
        )
        if entry not in self.entries:
            self.entries[entry] = self.db.execute(
                "INSERT INTO behavior_code_entries(definition_id,source_id,table_number,record_number) VALUES(?,?,?,?)",
                entry,
            ).lastrowid
        return {"$behavior_code": self.entries[entry]}

    def normalize(self, value):
        if not isinstance(value, dict):
            return value
        result = dict(value)
        for field in ("rob", "p6_rob_source"):
            rows = value.get(field)
            if isinstance(rows, dict) and isinstance(rows.get("behavior_codes"), list):
                result[field] = dict(
                    rows, behavior_codes=[self.row(r) for r in rows["behavior_codes"]]
                )
        return result


def restore_behavior_code(db, identity):
    if not integer(identity) or identity <= 0:
        raise ValueError("invalid behavior code reference")
    columns = ("variant",) + NUMBERS + tuple(k + "_id" for k in TEXTS)
    row = db.execute(
        "SELECT "
        + ",".join("d." + c for c in columns)
        + ",e.source_id,e.table_number,e.record_number,d.unknown_bytes "
        "FROM behavior_code_entries e JOIN behavior_code_defs d ON d.id=e.definition_id WHERE e.id=?",
        (identity,),
    ).fetchone()
    if row is None:
        raise ValueError("missing behavior code definition")
    variant = row[0]
    if variant not in (0, 1):
        raise ValueError("invalid behavior code variant")
    result = {}
    for k, v in zip(NUMBERS, row[1:9]):
        if variant == 0 and k != "behavior_code":
            if v is not None:
                raise ValueError("unexpected P5 behavior field")
        else:
            if not integer(v):
                raise ValueError("missing behavior numeric field")
            result[k] = v
    for k, v in zip(TEXTS, row[9:14]):
        if (variant == 0 and k == "division") or (variant == 1 and k == "kind"):
            if v is not None:
                raise ValueError("unexpected behavior text field")
            continue
        if v is None:
            if k in ("signature", "kind"):
                raise ValueError("missing behavior required text")
            result[k] = None
        else:
            text = db.execute(
                "SELECT value FROM text_values WHERE id=?", (v,)
            ).fetchone()
            if text is None:
                raise ValueError("missing behavior text")
            result[k] = text[0]
    source = db.execute(
        "SELECT value FROM text_values WHERE id=?", (row[14],)
    ).fetchone()
    if source is None:
        raise ValueError("missing behavior source")
    result.update(source=source[0], table=row[15], record=row[16])
    if row[17] is not None and variant != 1:
        raise ValueError("unexpected P5 ROB unknown fields")
    restore_rob_unknown(result, row[17])
    return result
