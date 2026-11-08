"""Semantic work-factor values and localized help, without vendor record bodies."""

import json

from tools.techstream.diag_codec import compress, decompress

HELP = (
    "help_id",
    "kind",
    "namespace",
    "record",
    "source",
    "string_index",
    "string_source",
    "table",
    "text",
    "translation_available",
)
STANDARD = (
    "exception_handler_flag",
    "exception_handler_id",
    "help_id",
    "record",
    "signal_id",
    "source",
    "standard_value",
    "standard_value_id",
    "standard_value_status",
    "table",
)
PATTERN = (
    "display_code",
    "exception_handler_flag",
    "exception_handler_id",
    "help",
    "help_string_index",
    "name",
    "name_string_index",
    "pattern_id",
    "record",
    "source",
    "table",
    "value",
)
FACTOR = (
    "exception_handler_flag",
    "exception_handler_id",
    "help",
    "help_string_index",
    "name",
    "name_string_index",
    "record",
    "signal_id",
    "source",
    "table",
    "value",
)
TEXT = frozenset(
    (
        "namespace",
        "source",
        "string_source",
        "text",
        "standard_value",
        "standard_value_status",
        "help",
        "name",
    )
)
# Fixed domain schemas. These are columns, not property/value records.
SCHEMA = """
CREATE TABLE work_help_definitions(id INTEGER PRIMARY KEY,help_id INTEGER NOT NULL,kind INTEGER NOT NULL,namespace_id INTEGER REFERENCES text_values(id),record INTEGER NOT NULL,source_id INTEGER REFERENCES text_values(id),string_index INTEGER NOT NULL,string_source_id INTEGER REFERENCES text_values(id),table_type INTEGER NOT NULL,text_id INTEGER REFERENCES text_values(id),translation_available INTEGER NOT NULL CHECK(translation_available IN(0,1)),unknown_bytes BLOB);
CREATE TABLE work_standard_definitions(id INTEGER PRIMARY KEY,exception_handler_flag INTEGER NOT NULL,exception_handler_id INTEGER NOT NULL,help_id INTEGER NOT NULL,record INTEGER NOT NULL,signal_id INTEGER NOT NULL,source_id INTEGER REFERENCES text_values(id),standard_value_id_text INTEGER REFERENCES text_values(id),standard_value_id INTEGER NOT NULL,standard_value_status_id INTEGER REFERENCES text_values(id),table_type INTEGER NOT NULL,help_definition_id INTEGER REFERENCES work_help_definitions(id),unknown_bytes BLOB);
CREATE TABLE work_pattern_definitions(id INTEGER PRIMARY KEY,display_code INTEGER NOT NULL,exception_handler_flag INTEGER NOT NULL,exception_handler_id INTEGER NOT NULL,help_id_text INTEGER REFERENCES text_values(id),help_string_index INTEGER NOT NULL,name_id INTEGER REFERENCES text_values(id),name_string_index INTEGER NOT NULL,pattern_id INTEGER NOT NULL,record INTEGER NOT NULL,source_id INTEGER REFERENCES text_values(id),table_type INTEGER NOT NULL,value INTEGER NOT NULL,unknown_bytes BLOB);
CREATE TABLE work_factor_definitions(id INTEGER PRIMARY KEY,exception_handler_flag INTEGER NOT NULL,exception_handler_id INTEGER NOT NULL,help_id_text INTEGER REFERENCES text_values(id),help_string_index INTEGER NOT NULL,name_id INTEGER REFERENCES text_values(id),name_string_index INTEGER NOT NULL,record INTEGER NOT NULL,signal_id INTEGER NOT NULL,source_id INTEGER REFERENCES text_values(id),table_type INTEGER NOT NULL,value INTEGER NOT NULL,unknown_bytes BLOB);
"""
SPECS = {
    "$work_standard": ("work_standard_definitions", STANDARD),
    "$work_pattern": ("work_pattern_definitions", PATTERN),
    "$work_factor_definition": ("work_factor_definitions", FACTOR),
}
COLLECTIONS = {
    "standard_info": "$work_standard",
    "work_factor_patterns": "$work_pattern",
    "factor_data": "$work_factor_definition",
}


def integer(v):
    if type(v) is not int or not -(1 << 63) <= v < (1 << 63):
        raise ValueError("unsupported work-factor integer")
    return v


UNKNOWN = {
    "$work_standard": (("11", 1),),
    "$work_pattern": (("17", 3),),
    "$work_factor_definition": (("16", 2), ("19", 1)),
    "help": (("10", 2),),
}


def unknown_bytes(value, kind):
    if "uninterpreted_bytes" not in value:
        return None
    fields = value["uninterpreted_bytes"]
    if type(fields) is not dict or set(fields) != {key for key, _ in UNKNOWN[kind]}:
        raise ValueError("unsupported work-factor unknown fields")
    result = b""
    for key, width in UNKNOWN[kind]:
        if type(fields[key]) is not str:
            raise ValueError("invalid work-factor unknown text")
        data = bytes.fromhex(fields[key])
        if len(data) != width or data.hex() != fields[key]:
            raise ValueError("invalid work-factor unknown bytes")
        result += data
    return result


def restore_unknown(value, blob, kind):
    if blob is None:
        return
    if type(blob) is not bytes or len(blob) != sum(width for _, width in UNKNOWN[kind]):
        raise ValueError("invalid work-factor unknown storage")
    fields = {}
    offset = 0
    for key, width in UNKNOWN[kind]:
        fields[key] = blob[offset : offset + width].hex()
        offset += width
    value["uninterpreted_bytes"] = fields


class Writer:
    def __init__(self, db):
        self.db = db
        self.cache = {}
        self.text = {}

    def string(self, v):
        if v is None:
            return None
        if type(v) is not str:
            raise ValueError("unsupported work-factor text")
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

    def values(self, v, fields):
        result = []
        for k in fields:
            x = v[k]
            if k in TEXT:
                result.append(self.string(x))
            elif k == "translation_available":
                if type(x) is not bool:
                    raise ValueError("unsupported translation state")
                result.append(int(x))
            else:
                result.append(integer(x))
        return tuple(result)

    def definition(self, v, marker):
        table, fields = SPECS[marker]
        expected = set(fields) | (
            {"standard_value_help_records"} if marker == "$work_standard" else set()
        )
        if type(v) is not dict or set(v) not in (
            expected,
            expected | {"uninterpreted_bytes"},
        ):
            raise ValueError("unsupported work-factor shape")
        values = self.values(v, fields)
        if marker == "$work_standard":
            rows = v["standard_value_help_records"]
            if type(rows) is not list or len(rows) > 1:
                raise ValueError("unsupported multi-help definition")
            help_id = None
            if rows:
                if type(rows[0]) is not dict or set(rows[0]) not in (
                    set(HELP),
                    set(HELP) | {"uninterpreted_bytes"},
                ):
                    raise ValueError("unsupported help definition")
                help_id = self.row(
                    "work_help_definitions",
                    self.values(rows[0], HELP) + (unknown_bytes(rows[0], "help"),),
                )
            values += (help_id,)
        return self.row(table, values + (unknown_bytes(v, marker),))

    def transform(self, value):
        if type(value) is not dict:
            return value
        group = value.get("work_factor")
        if type(group) is not dict:
            return value
        output = dict(group)
        for collection, marker in COLLECTIONS.items():
            if type(group.get(collection)) is not list:
                continue
            rows = []
            for row in group[collection]:
                try:
                    rows.append({marker: self.definition(row, marker)})
                except (ValueError, TypeError, KeyError):
                    rows.append(row)
            output[collection] = rows
        return {**value, "work_factor": output}


class Reader:
    def __init__(self, db):
        self.db = db

    def text(self, id):
        if id is None:
            return None
        row = self.db.execute(
            "SELECT value FROM text_values WHERE id=?", (id,)
        ).fetchone()
        if row is None:
            raise ValueError("missing work-factor text")
        return row[0]

    def fields(self, fields, values):
        result = {}
        for k, v in zip(fields, values):
            if k in TEXT:
                result[k] = self.text(v)
            elif k == "translation_available":
                if v not in (0, 1):
                    raise ValueError("invalid translation state")
                result[k] = bool(v)
            else:
                result[k] = v
        return result

    def read(self, marker, id):
        if marker not in SPECS or type(id) is not int or id <= 0:
            raise ValueError("invalid work-factor reference")
        table, fields = SPECS[marker]
        row = self.db.execute(
            "SELECT * FROM " + table + " WHERE id=?", (id,)
        ).fetchone()
        if row is None:
            raise ValueError("missing work-factor definition")
        result = self.fields(fields, row[1 : len(fields) + 1])
        if marker == "$work_standard":
            result["standard_value_help_records"] = []
            if row[len(fields) + 1] is not None:
                help = self.db.execute(
                    "SELECT * FROM work_help_definitions WHERE id=?",
                    (row[len(fields) + 1],),
                ).fetchone()
                if help is None:
                    raise ValueError("missing work-factor help")
                decoded_help = self.fields(HELP, help[1:])
                restore_unknown(decoded_help, help[-1], "help")
                result["standard_value_help_records"].append(decoded_help)
        restore_unknown(result, row[-1], marker)
        return result


def restore_work_semantic(db, marker, id):
    return Reader(db).read(marker, id)


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
            packed = compress(
                json.dumps(
                    result, ensure_ascii=False, separators=(",", ":"), sort_keys=True
                ).encode()
            )
            db.execute(
                "UPDATE "
                + table
                + " SET data=? WHERE "
                + " AND ".join(k + "=?" for k in keys),
                (packed, *row[:-1]),
            )
            changed += 1
    return changed
