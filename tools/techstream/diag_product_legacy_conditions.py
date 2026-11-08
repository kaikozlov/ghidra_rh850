"""Semantic legacy response lengths, support predicates and dynamic scaling.

Facts are decoded protocol parameters, not vendor record bytes. Query layouts
and patches are the explicit semantics of those parameters. Unknown projections
remain inline and are never silently reduced to a known subset.
"""

from __future__ import annotations

import json

from .diag_legacy_unknown_fields import (
    UnknownStore,
    validate as validate_unknown,
    restore as restore_unknown,
)

DDL = """
CREATE TABLE IF NOT EXISTS text_values(id INTEGER PRIMARY KEY,value TEXT NOT NULL UNIQUE);
CREATE TABLE IF NOT EXISTS legacy_condition_defs(
 id INTEGER PRIMARY KEY,condition_key INTEGER NOT NULL,variable_id INTEGER NOT NULL,
 bit_start INTEGER NOT NULL,bit_end INTEGER NOT NULL,source_mode INTEGER NOT NULL,
 exception_id INTEGER NOT NULL,exception_flag INTEGER NOT NULL,variable BLOB);
CREATE TABLE IF NOT EXISTS legacy_condition_entries(
 id INTEGER PRIMARY KEY,definition_id INTEGER NOT NULL REFERENCES legacy_condition_defs(id),
 source_id INTEGER NOT NULL REFERENCES text_values(id),table_number INTEGER NOT NULL,
 record_number INTEGER NOT NULL,has_kind INTEGER NOT NULL CHECK(has_kind IN(0,1)));
CREATE TABLE IF NOT EXISTS legacy_response_defs(
 id INTEGER PRIMARY KEY,response_key INTEGER NOT NULL,data_length INTEGER NOT NULL,
 exception_id INTEGER NOT NULL,exception_flag INTEGER NOT NULL);
CREATE TABLE IF NOT EXISTS legacy_response_entries(
 id INTEGER PRIMARY KEY,definition_id INTEGER NOT NULL REFERENCES legacy_response_defs(id),
 source_id INTEGER NOT NULL REFERENCES text_values(id),table_number INTEGER NOT NULL,record_number INTEGER NOT NULL);
CREATE TABLE IF NOT EXISTS legacy_dynamic_defs(
 id INTEGER PRIMARY KEY,monitor_key INTEGER NOT NULL,mul INTEGER NOT NULL,div INTEGER NOT NULL,
 bit_start INTEGER NOT NULL,bit_end INTEGER NOT NULL,pid INTEGER NOT NULL);
CREATE TABLE IF NOT EXISTS legacy_dynamic_entries(
 id INTEGER PRIMARY KEY,definition_id INTEGER NOT NULL REFERENCES legacy_dynamic_defs(id),
 record_number INTEGER NOT NULL,unknown_id INTEGER REFERENCES legacy_dynamic_unknown_facts(id));
"""
CONDITION_FIELDS = (
    "key",
    "variable_id",
    "bit_start",
    "bit_end",
    "source_mode",
    "exception_id",
    "exception_flag",
)
RESPONSE_FIELDS = ("key", "data_length", "exception_id", "exception_flag")
DYNAMIC_FIELDS = ("monitor_key", "mul", "div", "bit_start", "bit_end", "pid")


def integer(v):
    if type(v) is not int or not -(1 << 63) <= v < (1 << 63):
        raise ValueError("unsupported legacy integer")
    return v


def same(a, b):
    return json.dumps(
        a, sort_keys=True, ensure_ascii=False, allow_nan=False
    ) == json.dumps(b, sort_keys=True, ensure_ascii=False, allow_nan=False)


def condition_view(values, variable, source, table, record, has_kind):
    if table not in (8, 9) or record < 0 or has_kind not in (0, 1):
        raise ValueError("invalid legacy condition origin")
    key, var_id, start, end, mode, exception_id, exception_flag = values
    queries = {
        2: {
            "request_selector": 16,
            "variable_length": 1,
            "request_offsets": [1],
            "response_offset": 2,
        },
        3: {
            "request_selector": 105,
            "variable_length": 1,
            "request_offsets": [1],
            "response_offset": 2,
        },
        4: {
            "request_selector": 106,
            "variable_length": 2,
            "request_offsets": [2, 3],
            "response_offset": 4,
        },
        6: {"cache": "did_support", "variable_min_length": 1, "response_offset": 0},
    }
    query = queries.get(mode)
    out = dict(zip(CONDITION_FIELDS, values))
    out.update(
        source=source,
        table=table,
        record=record,
        predicate="nonzero",
        bit_order="msb0",
        query=query,
        native_status="valid"
        if query is not None and end >= start
        else "invalid_geometry_or_mode",
        supported_identifier_gate={
            "CheckSupportBit": {2: "pid", 3: "did"}.get(mode),
            "CheckSupportBitOldBody": None,
            "CheckSupportBitP4": "did" if mode == 6 else "pid" if mode == 2 else None,
        },
    )
    if has_kind:
        out["kind"] = "pid_bit" if table == 8 else "did_bit"
    if mode in (2, 6):
        out["p4_cache_query"] = {
            "cache": "pid_support" if mode == 2 else "did_support",
            "identifier_variable_offset": 0,
            "response_offset": 0,
            "predicate": "nonzero",
        }
    if variable is not None:
        out["variable"] = variable.hex()
        if query is not None:
            if mode == 6:
                if variable:
                    out["cache_identifier"] = variable[0]
                else:
                    out["native_status"] = "invalid_variable_length"
            elif len(variable) != query["variable_length"]:
                out["native_status"] = "invalid_variable_length"
            else:
                out["request_patches"] = [
                    {"offset": offset, "value": byte}
                    for offset, byte in zip(query["request_offsets"], variable)
                ]
    return out


def response_view(values, source, table, record):
    if table not in (6, 7) or record < 0:
        raise ValueError("invalid legacy response origin")
    out = dict(zip(RESPONSE_FIELDS, values))
    out.update(
        source=source,
        table=table,
        record=record,
        kind="pid" if table == 6 else "did",
        length_resolution="runtime" if out["data_length"] == 0 else "fixed",
    )
    return out


def dynamic_view(values, record):
    if record < 0:
        raise ValueError("invalid dynamic LSB origin")
    return {**dict(zip(DYNAMIC_FIELDS, values)), "table": 39, "record": record}


class ConditionStore:
    def __init__(self, db):
        self.db = db
        db.executescript(DDL)
        self.unknown = UnknownStore(db)
        self.texts = {}
        self.maps = {}
        for table in (
            "legacy_condition_defs",
            "legacy_condition_entries",
            "legacy_response_defs",
            "legacy_response_entries",
            "legacy_dynamic_defs",
            "legacy_dynamic_entries",
        ):
            self.maps[table] = {
                tuple(r[1:]): r[0] for r in db.execute(f"SELECT * FROM {table}")
            }

    def text(self, value):
        if value not in self.texts:
            self.db.execute(
                "INSERT OR IGNORE INTO text_values(value) VALUES(?)", (value,)
            )
            self.texts[value] = self.db.execute(
                "SELECT id FROM text_values WHERE value=?", (value,)
            ).fetchone()[0]
        return self.texts[value]

    def intern(self, table, values):
        cache = self.maps[table]
        if values not in cache:
            cache[values] = self.db.execute(
                f"INSERT INTO {table} VALUES(NULL,{','.join('?' for _ in values)})",
                values,
            ).lastrowid
        return cache[values]

    def row(self, row):
        if type(row) is not dict:
            return row
        table = row.get("table")
        if type(table) is not int or table not in (6, 7, 8, 9, 39):
            return row
        try:
            record = integer(row["record"])
            if record < 0:
                raise ValueError("negative origin")
            if table != 39:
                source = row["source"]
                if type(source) is not str:
                    raise ValueError("invalid source")
            if table in (8, 9):
                values = tuple(integer(row[k]) for k in CONDITION_FIELDS)
                variable = bytes.fromhex(row["variable"]) if "variable" in row else None
                has_kind = int("kind" in row)
                if not same(
                    condition_view(values, variable, source, table, record, has_kind),
                    row,
                ):
                    return row
                definition = self.intern("legacy_condition_defs", values + (variable,))
                identity = self.intern(
                    "legacy_condition_entries",
                    (definition, self.text(source), table, record, has_kind),
                )
                return {"$legacy_condition": identity}
            if table in (6, 7):
                values = tuple(integer(row[k]) for k in RESPONSE_FIELDS)
                if not same(response_view(values, source, table, record), row):
                    return row
                definition = self.intern("legacy_response_defs", values)
                identity = self.intern(
                    "legacy_response_entries",
                    (definition, self.text(source), table, record),
                )
                return {"$legacy_response_definition": identity}
            values = tuple(integer(row[k]) for k in DYNAMIC_FIELDS)
            unknown = row.get("uninterpreted_bytes")
            if "uninterpreted_bytes" in row and unknown is None:
                return row
            validate_unknown("dynamic", unknown)
            projected = dynamic_view(values, record)
            if unknown is not None:
                projected["uninterpreted_bytes"] = unknown
            if not same(projected, row):
                return row
            unknown_id = self.unknown.intern("dynamic", unknown)
            definition = self.intern("legacy_dynamic_defs", values)
            identity = self.intern(
                "legacy_dynamic_entries", (definition, record, unknown_id)
            )
            return {"$legacy_dynamic": identity}
        except (KeyError, ValueError, TypeError, OverflowError):
            return row

    def normalize(self, value):
        if isinstance(value, list):
            return [self.normalize(v) for v in value]
        if not isinstance(value, dict):
            return value
        converted = self.row(value)
        if converted is not value:
            return converted
        return {k: self.normalize(v) for k, v in value.items()}


def restore_condition(db, identity):
    row = db.execute(
        """SELECT d.condition_key,d.variable_id,d.bit_start,d.bit_end,d.source_mode,d.exception_id,d.exception_flag,d.variable,
 s.value,e.table_number,e.record_number,e.has_kind FROM legacy_condition_entries e
 JOIN legacy_condition_defs d ON d.id=e.definition_id JOIN text_values s ON s.id=e.source_id WHERE e.id=?""",
        (identity,),
    ).fetchone()
    if row is None:
        raise ValueError("missing legacy condition")
    values = tuple(integer(v) for v in row[:7])
    return condition_view(
        values, row[7], row[8], integer(row[9]), integer(row[10]), integer(row[11])
    )


def restore_response(db, identity):
    row = db.execute(
        """SELECT d.response_key,d.data_length,d.exception_id,d.exception_flag,s.value,e.table_number,e.record_number
 FROM legacy_response_entries e JOIN legacy_response_defs d ON d.id=e.definition_id JOIN text_values s ON s.id=e.source_id WHERE e.id=?""",
        (identity,),
    ).fetchone()
    if row is None:
        raise ValueError("missing legacy response")
    return response_view(
        tuple(integer(v) for v in row[:4]), row[4], integer(row[5]), integer(row[6])
    )


def restore_dynamic(db, identity):
    row = db.execute(
        """SELECT d.monitor_key,d.mul,d.div,d.bit_start,d.bit_end,d.pid,e.record_number,e.unknown_id
 FROM legacy_dynamic_entries e JOIN legacy_dynamic_defs d ON d.id=e.definition_id WHERE e.id=?""",
        (identity,),
    ).fetchone()
    if row is None:
        raise ValueError("missing legacy dynamic LSB")
    result = dynamic_view(tuple(integer(v) for v in row[:6]), integer(row[6]))
    if row[7] is not None:
        result["uninterpreted_bytes"] = restore_unknown(db, "dynamic", row[7])
    return result
