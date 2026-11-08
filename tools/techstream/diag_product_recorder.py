"""Semantic recorder schemas: signals, admission comparisons and trigger events.

Each domain has fixed typed columns. Source occurrences bind shared definitions;
ordered record links are relations, not serialized JSON. No vendor bytes are used.
"""

import math
from tools.techstream.diag_freeze_physical import integer

COMMON_SIGNAL = "bit_end bit_start did exception_flag exception_id name_string_index pattern_display_key physical_data_key presentation_mode signal_key signal_role sort_key"
# (integer fields, nullable text fields, boolean fields, range fields, child refs, ordered integer lists)
SPECS = {
    "ddr_signal": (
        COMMON_SIGNAL + " visibility",
        "name",
        "list_member",
        "data_min data_max",
        "signal_info",
        "data_id_records invalid_condition_records",
    ),
    "ddr_behavior_signal": (
        COMMON_SIGNAL + " extraction_mode graph_max graph_min support_condition_key",
        "name family",
        "live_list_member",
        "data_min data_max",
        "signal_info",
        "invalid_condition_records",
    ),
    "ddr_condition": (
        "combination_mode comparison_mode comparison_value condition_order exception_flag exception_id referenced_signal_key signal_key",
        "comparison",
        "",
        "",
        "",
        "",
    ),
    "ddr_behavior_condition": (
        "combination_mode comparison_mode condition_order exception_flag exception_id referenced_signal_key signal_key",
        "comparison family",
        "",
        "",
        "",
        "",
    ),
    "ddr_data_id": (
        "did exception_flag exception_id payload_length validity_mode",
        "",
        "",
        "",
        "",
        "",
    ),
    "ddr_trigger": (
        "dtc_identifier exception_flag exception_id name_string_index trigger_memo_string_index trigger_point_enabled trigger_selector_0 trigger_selector_1 unresolved_u16_0e",
        "name trigger_memo",
        "",
        "",
        "",
        "",
    ),
    "ddr_behavior_code": (
        "additional_string_index behavior_key dependent_data_0 dependent_data_1 exception_flag exception_id name_string_index trigger_memo_string_index trigger_selector_0 trigger_selector_1",
        "additional_text family name trigger_memo",
        "",
        "",
        "",
        "",
    ),
}
SPECS = {k: tuple(v.split() for v in spec) for k, spec in SPECS.items()}
PATHS = {
    "ddr": {
        "signals": "ddr_signal",
        "invalid_conditions": "ddr_condition",
        "data_ids": "ddr_data_id",
        "triggers": "ddr_trigger",
    },
    "ddr_behavior": {
        "signals": "ddr_behavior_signal",
        "invalid_conditions": "ddr_behavior_condition",
        "codes": "ddr_behavior_code",
    },
}
ORIGIN = {"source", "table", "record"}


def ddl():
    out = []
    for kind, (ints, texts, bools, floats, refs, lists) in SPECS.items():
        cols = [k + " INTEGER NOT NULL" for k in ints + bools] + [
            k + "_id INTEGER REFERENCES text_values(id)" for k in texts
        ]
        cols += [k + " REAL NOT NULL" for k in floats] + [
            k + "_id INTEGER NOT NULL REFERENCES signal_infos(id)" for k in refs
        ]
        if kind == "ddr_behavior_condition":
            cols += ["comparison_bits64 TEXT NOT NULL"]
        cols += [k + "_count INTEGER NOT NULL" for k in lists]
        if kind == "ddr_condition":
            cols += ["unknown_byte15 TEXT CHECK(unknown_byte15 IS NULL OR (length(unknown_byte15)=2 AND unknown_byte15 NOT GLOB '*[^0-9a-f]*'))"]
        out.append(
            "CREATE TABLE IF NOT EXISTS "
            + kind
            + "_defs(id INTEGER PRIMARY KEY,"
            + ",".join(cols)
            + ");"
        )
        out.append(
            "CREATE TABLE IF NOT EXISTS "
            + kind
            + "_entries(id INTEGER PRIMARY KEY,definition_id INTEGER NOT NULL REFERENCES "
            + kind
            + "_defs(id),source_id INTEGER NOT NULL REFERENCES text_values(id),table_number INTEGER NOT NULL,record_number INTEGER NOT NULL);"
        )
        for k in lists:
            out.append(
                "CREATE TABLE IF NOT EXISTS "
                + kind
                + "_"
                + k
                + "(definition_id INTEGER NOT NULL REFERENCES "
                + kind
                + "_defs(id),position INTEGER NOT NULL,value INTEGER NOT NULL,PRIMARY KEY(definition_id,position)) WITHOUT ROWID;"
            )
    return "\n".join(out)


DDL = ddl()


class Store:
    def __init__(self, db):
        self.db = db
        db.executescript(DDL)
        self.texts = {}
        self.entries = {}
        self.defs = {}
        for kind, spec in SPECS.items():
            self.entries[kind] = {
                tuple(r[1:]): r[0]
                for r in db.execute("SELECT * FROM " + kind + "_entries")
            }
            self.defs[kind] = {}
            for r in db.execute("SELECT * FROM " + kind + "_defs"):
                relations = tuple(
                    tuple(
                        v[0]
                        for v in db.execute(
                            "SELECT value FROM "
                            + kind
                            + "_"
                            + k
                            + " WHERE definition_id=? ORDER BY position",
                            (r[0],),
                        )
                    )
                    for k in spec[-1]
                )
                self.defs[kind][tuple(r[1:]) + relations] = r[0]

    def text(self, value):
        if value is None:
            return None
        if type(value) is not str:
            raise ValueError("unsupported recorder label")
        if value not in self.texts:
            self.db.execute(
                "INSERT OR IGNORE INTO text_values(value) VALUES(?)", (value,)
            )
            self.texts[value] = self.db.execute(
                "SELECT id FROM text_values WHERE value=?", (value,)
            ).fetchone()[0]
        return self.texts[value]

    def row(self, kind, row):
        ints, texts, bools, floats, refs, lists = SPECS[kind]
        shape = set(ints + texts + bools + floats + refs + lists) | ORIGIN
        if kind == "ddr_behavior_condition":
            shape.add("comparison_bits64")
        if type(row) is not dict:
            return row
        unknown_byte15 = None
        if kind == "ddr_condition" and "uninterpreted_bytes" in row:
            unknown = row["uninterpreted_bytes"]
            if type(unknown) is not dict or set(unknown) != {"15"}:
                return row
            unknown_byte15 = unknown["15"]
            if type(unknown_byte15) is not str or len(unknown_byte15) != 2 or any(c not in "0123456789abcdef" for c in unknown_byte15):
                return row
            shape.add("uninterpreted_bytes")
        if set(row) != shape:
            return row
        try:
            values = tuple(integer(row[k]) for k in ints)
            if any(type(row[k]) is not bool for k in bools):
                return row
            values += tuple(int(row[k]) for k in bools) + tuple(
                self.text(row[k]) for k in texts
            )
            if any(
                type(row[k]) is not float
                or not math.isfinite(row[k])
                or (row[k] == 0 and math.copysign(1, row[k]) < 0)
                for k in floats
            ):
                return row
            values += tuple(row[k] for k in floats)
            for k in refs:
                v = row[k]
                if (
                    type(v) is not dict
                    or set(v) != {"$signal_info"}
                    or type(v["$signal_info"]) is not int
                    or v["$signal_info"] <= 0
                ):
                    return row
                values += (v["$signal_info"],)
            if kind == "ddr_behavior_condition":
                v = row["comparison_bits64"]
                if type(v) is not int or not 0 <= v < 1 << 64:
                    return row
                values += (str(v),)
            relations = []
            for k in lists:
                if type(row[k]) is not list:
                    return row
                relations.append(tuple(integer(v) for v in row[k]))
            values += tuple(len(x) for x in relations)
            if kind == "ddr_condition":
                values += (unknown_byte15,)
            if type(row["source"]) is not str:
                return row
            origin = (
                self.text(row["source"]),
                integer(row["table"]),
                integer(row["record"]),
            )
            key = values + tuple(relations)
            cache = self.defs[kind]
            if key not in cache:
                ident = self.db.execute(
                    "INSERT INTO "
                    + kind
                    + "_defs VALUES("
                    + ",".join("?" for _ in range(len(values) + 1))
                    + ")",
                    (None, *values),
                ).lastrowid
                for k, relation in zip(lists, relations):
                    self.db.executemany(
                        "INSERT INTO " + kind + "_" + k + " VALUES(?,?,?)",
                        [(ident, i, v) for i, v in enumerate(relation)],
                    )
                cache[key] = ident
            entry = (cache[key], *origin)
            cache = self.entries[kind]
            if entry not in cache:
                cache[entry] = self.db.execute(
                    "INSERT INTO " + kind + "_entries VALUES(NULL,?,?,?,?)", entry
                ).lastrowid
            return {"$" + kind: cache[entry]}
        except (ValueError, TypeError):
            return row

    def normalize(self, document):
        for root, fields in PATHS.items():
            value = document.get(root)
            if isinstance(value, dict):
                for field, kind in fields.items():
                    if isinstance(value.get(field), list):
                        value[field] = [self.row(kind, v) for v in value[field]]
        return document


def restore(db, kind, ident):
    if kind not in SPECS or type(ident) is not int or ident <= 0:
        raise ValueError("invalid recorder reference")
    entry = db.execute(
        "SELECT e.definition_id,t.value,e.table_number,e.record_number FROM "
        + kind
        + "_entries e JOIN text_values t ON t.id=e.source_id WHERE e.id=?",
        (ident,),
    ).fetchone()
    if entry is None:
        raise ValueError("missing recorder origin")
    row = db.execute(
        "SELECT * FROM " + kind + "_defs WHERE id=?", (entry[0],)
    ).fetchone()
    if row is None:
        raise ValueError("missing recorder definition")
    ints, texts, bools, floats, refs, lists = SPECS[kind]
    vals = iter(row[1:])
    out = {}
    for k in ints:
        out[k] = next(vals)
    for k in bools:
        v = next(vals)
        if v not in (0, 1):
            raise ValueError("invalid recorder boolean")
        out[k] = bool(v)
    for k in texts:
        i = next(vals)
        v = (
            None
            if i is None
            else db.execute("SELECT value FROM text_values WHERE id=?", (i,)).fetchone()
        )
        if i is not None and v is None:
            raise ValueError("missing recorder text")
        out[k] = None if v is None else v[0]
    for k in floats:
        out[k] = next(vals)
    for k in refs:
        out[k] = {"$signal_info": next(vals)}
    if kind == "ddr_behavior_condition":
        out["comparison_bits64"] = int(next(vals))
    for k in lists:
        count = next(vals)
        out[k] = []
        for position, v in db.execute(
            "SELECT position,value FROM "
            + kind
            + "_"
            + k
            + " WHERE definition_id=? ORDER BY position",
            (entry[0],),
        ):
            if position != len(out[k]):
                raise ValueError("invalid recorder relationship order")
            out[k].append(v)
        if len(out[k]) != count:
            raise ValueError("incomplete recorder relationship")
    if kind == "ddr_condition":
        unknown_byte15 = next(vals, None)
        if unknown_byte15 is not None:
            if type(unknown_byte15) is not str or len(unknown_byte15) != 2 or any(c not in "0123456789abcdef" for c in unknown_byte15):
                raise ValueError("invalid recorder unknown byte")
            out["uninterpreted_bytes"] = {"15": unknown_byte15}
    out.update(source=entry[1], table=entry[2], record=entry[3])
    return out
