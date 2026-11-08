"""Decoded legacy live/freeze-frame monitors and their semantic relationships."""

from __future__ import annotations

import math

INTEGERS = (
    "begin_condition",
    "bit_end",
    "bit_start",
    "data_type",
    "exception_handler_flag",
    "exception_handler_id",
    "graph_max",
    "graph_min",
    "membership_flags",
    "monitor_key",
    "name_string_index",
    "pattern_display_key",
    "physical_data_key",
    "pid",
    "slope_condition",
    "slope_default",
    "sort_key",
    "support_condition_key",
    "support_policy",
    "trigger_condition",
)
BOOLEANS = ("freeze_member", "live_member", "support_condition_resolved")
UNKNOWN_RANGES = (("34_3f", 12), ("48_4b", 4), ("56_57", 2), ("5e_5f", 2))
FIELDS = (
    set(INTEGERS)
    | set(BOOLEANS)
    | {
        "data_max",
        "data_min",
        "kind",
        "layout",
        "name",
        "short_name",
        "source",
        "table",
        "record",
        "physical_records",
        "support_conditions",
        "dynamic_lsb_records",
    }
)
COLUMNS = (
    "name_id",
    "short_name_id",
    "layout_id",
    "physical_id",
    *INTEGERS,
    *BOOLEANS,
    "data_min",
    "data_max",
    "support_count",
    "dynamic_count",
)
DDL = (
    """
CREATE TABLE IF NOT EXISTS text_values(id INTEGER PRIMARY KEY,value TEXT NOT NULL UNIQUE);
CREATE TABLE IF NOT EXISTS legacy_freeze_definitions(
 id INTEGER PRIMARY KEY,name_id INTEGER REFERENCES text_values(id),
 short_name_id INTEGER NOT NULL REFERENCES text_values(id),layout_id INTEGER NOT NULL REFERENCES text_values(id),
 physical_id INTEGER NOT NULL REFERENCES freeze_physical_defs(id),
"""
    + ",\n".join(f"{field} INTEGER NOT NULL" for field in (*INTEGERS, *BOOLEANS))
    + """,
 data_min REAL NOT NULL,data_max REAL NOT NULL,support_count INTEGER NOT NULL,dynamic_count INTEGER NOT NULL);
CREATE TABLE IF NOT EXISTS legacy_freeze_unknown_facts(
 id INTEGER PRIMARY KEY,bytes_34_3f BLOB NOT NULL,bytes_48_4b BLOB NOT NULL,
 bytes_56_57 BLOB NOT NULL,bytes_5e_5f BLOB NOT NULL,byte_67 INTEGER NOT NULL);
CREATE TABLE IF NOT EXISTS legacy_freeze_entries(
 id INTEGER PRIMARY KEY,definition_id INTEGER NOT NULL REFERENCES legacy_freeze_definitions(id),
 source_id INTEGER NOT NULL REFERENCES text_values(id),table_number INTEGER NOT NULL,record_number INTEGER NOT NULL,
 unknown_id INTEGER REFERENCES legacy_freeze_unknown_facts(id));
CREATE TABLE IF NOT EXISTS legacy_freeze_support_members(
 definition_id INTEGER NOT NULL REFERENCES legacy_freeze_definitions(id),position INTEGER NOT NULL,
 condition_id INTEGER NOT NULL REFERENCES legacy_condition_entries(id),PRIMARY KEY(definition_id,position)) WITHOUT ROWID;
CREATE TABLE IF NOT EXISTS legacy_freeze_dynamic_members(
 definition_id INTEGER NOT NULL REFERENCES legacy_freeze_definitions(id),position INTEGER NOT NULL,
 dynamic_id INTEGER NOT NULL REFERENCES legacy_dynamic_entries(id),PRIMARY KEY(definition_id,position)) WITHOUT ROWID;
"""
)


def integer(value):
    return type(value) is int and -(1 << 63) <= value < (1 << 63)


def refs(rows, marker):
    if type(rows) is not list:
        raise ValueError("invalid freeze relationships")
    result = []
    for row in rows:
        if (
            type(row) is not dict
            or set(row) != {marker}
            or not integer(row[marker])
            or row[marker] <= 0
        ):
            raise ValueError("unknown freeze relationship")
        result.append(row[marker])
    return tuple(result)


class FreezeStore:
    def __init__(self, db):
        self.db = db
        db.executescript(DDL)
        self.texts = {}
        self.definitions = {}
        self.unknowns = {
            tuple(row[1:]): row[0]
            for row in db.execute("SELECT * FROM legacy_freeze_unknown_facts")
        }
        support = {}
        dynamic = {}
        for definition, position, child in db.execute(
            "SELECT * FROM legacy_freeze_support_members ORDER BY definition_id,position"
        ):
            support.setdefault(definition, []).append(child)
        for definition, position, child in db.execute(
            "SELECT * FROM legacy_freeze_dynamic_members ORDER BY definition_id,position"
        ):
            dynamic.setdefault(definition, []).append(child)
        for row in db.execute("SELECT * FROM legacy_freeze_definitions"):
            self.definitions[
                tuple(row[1:])
                + (tuple(support.get(row[0], [])), tuple(dynamic.get(row[0], [])))
            ] = row[0]
        self.entries = {
            tuple(row[1:]): row[0]
            for row in db.execute("SELECT * FROM legacy_freeze_entries")
        }

    def text(self, value):
        if value is None:
            return None
        if value not in self.texts:
            self.db.execute(
                "INSERT OR IGNORE INTO text_values(value) VALUES(?)", (value,)
            )
            self.texts[value] = self.db.execute(
                "SELECT id FROM text_values WHERE value=?", (value,)
            ).fetchone()[0]
        return self.texts[value]

    def row(self, row):
        if (
            type(row) is not dict
            or set(row) not in (FIELDS, FIELDS | {"unassigned_fields"})
            or row["kind"] != "freeze_frame"
        ):
            return row
        unknown = None
        try:
            if "unassigned_fields" in row:
                value = row["unassigned_fields"]
                if type(value) is not dict or set(value) != {
                    *(key for key, _ in UNKNOWN_RANGES),
                    "67",
                }:
                    raise ValueError("unknown freeze field layout")
                parts = []
                for key, size in UNKNOWN_RANGES:
                    if type(value[key]) is not str:
                        raise ValueError("invalid freeze unknown bytes")
                    data = bytes.fromhex(value[key])
                    if len(data) != size or data.hex() != value[key]:
                        raise ValueError("invalid freeze unknown bytes")
                    parts.append(data)
                if not integer(value["67"]) or not 0 <= value["67"] <= 255:
                    raise ValueError("invalid freeze unknown byte")
                unknown = (*parts, value["67"])
            if any(not integer(row[k]) for k in (*INTEGERS, "table", "record")):
                raise ValueError("invalid freeze integer")
            if row["table"] < 0 or row["record"] < 0:
                raise ValueError("invalid freeze origin")
            if any(type(row[k]) is not bool for k in BOOLEANS):
                raise ValueError("invalid freeze boolean")
            if any(
                type(row[k]) is not str for k in ("short_name", "layout", "source")
            ) or (row["name"] is not None and type(row["name"]) is not str):
                raise ValueError("invalid freeze label")
            if any(
                type(row[k]) is not float
                or not math.isfinite(row[k])
                or (row[k] == 0 and math.copysign(1, row[k]) < 0)
                for k in ("data_min", "data_max")
            ):
                raise ValueError("unsupported freeze range")
            physical = refs(row["physical_records"], "$freeze_physical")
            if len(physical) != 1:
                raise ValueError("unknown physical multiplicity")
            support = refs(row["support_conditions"], "$legacy_condition")
            dynamic = refs(row["dynamic_lsb_records"], "$legacy_dynamic")
        except (KeyError, TypeError, ValueError):
            return row
        key = (
            self.text(row["name"]),
            self.text(row["short_name"]),
            self.text(row["layout"]),
            physical[0],
            *(row[k] for k in INTEGERS),
            *(int(row[k]) for k in BOOLEANS),
            row["data_min"],
            row["data_max"],
            len(support),
            len(dynamic),
            support,
            dynamic,
        )
        if key not in self.definitions:
            identity = self.db.execute(
                f"INSERT INTO legacy_freeze_definitions({','.join(COLUMNS)}) VALUES({','.join('?' for _ in COLUMNS)})",
                key[:-2],
            ).lastrowid
            self.db.executemany(
                "INSERT INTO legacy_freeze_support_members VALUES(?,?,?)",
                [(identity, i, x) for i, x in enumerate(support)],
            )
            self.db.executemany(
                "INSERT INTO legacy_freeze_dynamic_members VALUES(?,?,?)",
                [(identity, i, x) for i, x in enumerate(dynamic)],
            )
            self.definitions[key] = identity
        unknown_id = None
        if unknown is not None:
            if unknown not in self.unknowns:
                self.unknowns[unknown] = self.db.execute(
                    "INSERT INTO legacy_freeze_unknown_facts(bytes_34_3f,bytes_48_4b,bytes_56_57,bytes_5e_5f,byte_67) VALUES(?,?,?,?,?)",
                    unknown,
                ).lastrowid
            unknown_id = self.unknowns[unknown]
        binding = (
            self.definitions[key],
            self.text(row["source"]),
            row["table"],
            row["record"],
            unknown_id,
        )
        if binding not in self.entries:
            self.entries[binding] = self.db.execute(
                "INSERT INTO legacy_freeze_entries(definition_id,source_id,table_number,record_number,unknown_id) VALUES(?,?,?,?,?)",
                binding,
            ).lastrowid
        return {"$legacy_freeze_signal": self.entries[binding]}

    def normalize(self, document):
        if (
            type(document) is not dict
            or type(document.get("legacy_records")) is not list
        ):
            return document
        return {
            **document,
            "legacy_records": [self.row(r) for r in document["legacy_records"]],
        }


def restore(db, identity):
    if not integer(identity) or identity <= 0:
        raise ValueError("invalid legacy freeze reference")
    row = db.execute(
        "SELECT d.*,s.value,e.table_number,e.record_number,e.unknown_id FROM legacy_freeze_entries e JOIN legacy_freeze_definitions d ON d.id=e.definition_id JOIN text_values s ON s.id=e.source_id WHERE e.id=?",
        (identity,),
    ).fetchone()
    if row is None:
        raise ValueError("missing legacy freeze signal")
    definition = row[0]
    values = dict(zip(COLUMNS, row[1 : 1 + len(COLUMNS)]))
    source, table, record, unknown_id = row[1 + len(COLUMNS) :]
    if not integer(table) or table < 0 or not integer(record) or record < 0:
        raise ValueError("invalid legacy freeze origin")

    def text(identity, nullable=False):
        if identity is None and nullable:
            return None
        r = db.execute(
            "SELECT value FROM text_values WHERE id=?", (identity,)
        ).fetchone()
        if r is None:
            raise ValueError("missing legacy freeze text")
        return r[0]

    out = {
        "kind": "freeze_frame",
        "name": text(values["name_id"], True),
        "short_name": text(values["short_name_id"]),
        "layout": text(values["layout_id"]),
        "source": source,
        "table": table,
        "record": record,
    }
    for key in INTEGERS:
        if not integer(values[key]):
            raise ValueError("missing legacy freeze integer")
        out[key] = values[key]
    for key in BOOLEANS:
        if values[key] not in (0, 1):
            raise ValueError("invalid legacy freeze boolean")
        out[key] = bool(values[key])
    for key in ("data_min", "data_max"):
        if type(values[key]) is not float or not math.isfinite(values[key]):
            raise ValueError("invalid legacy freeze range")
        out[key] = values[key]
    if not integer(values["physical_id"]) or values["physical_id"] <= 0:
        raise ValueError("invalid freeze physical reference")
    out["physical_records"] = [{"$freeze_physical": values["physical_id"]}]
    for field, table, column, count, marker in (
        (
            "support_conditions",
            "legacy_freeze_support_members",
            "condition_id",
            "support_count",
            "$legacy_condition",
        ),
        (
            "dynamic_lsb_records",
            "legacy_freeze_dynamic_members",
            "dynamic_id",
            "dynamic_count",
            "$legacy_dynamic",
        ),
    ):
        rows = db.execute(
            f"SELECT position,{column} FROM {table} WHERE definition_id=? ORDER BY position",
            (definition,),
        ).fetchall()
        if len(rows) != values[count] or any(
            p != i or not integer(v) or v <= 0 for i, (p, v) in enumerate(rows)
        ):
            raise ValueError("incomplete freeze relationships")
        out[field] = [{marker: v} for _, v in rows]
    if unknown_id is not None:
        if not integer(unknown_id) or unknown_id <= 0:
            raise ValueError("invalid freeze unknown reference")
        unknown = db.execute(
            "SELECT bytes_34_3f,bytes_48_4b,bytes_56_57,bytes_5e_5f,byte_67 FROM legacy_freeze_unknown_facts WHERE id=?",
            (unknown_id,),
        ).fetchone()
        if unknown is None:
            raise ValueError("missing freeze unknown facts")
        fields = {}
        for (key, size), data in zip(UNKNOWN_RANGES, unknown[:4]):
            if type(data) is not bytes or len(data) != size:
                raise ValueError("invalid freeze unknown bytes")
            fields[key] = data.hex()
        if not integer(unknown[4]) or not 0 <= unknown[4] <= 255:
            raise ValueError("invalid freeze unknown byte")
        fields["67"] = unknown[4]
        out["unassigned_fields"] = fields
    return out
