"""Decoded legacy operation definitions and safety policies, not vendor records."""

from __future__ import annotations

import json
from tools.techstream.diag_legacy_unknown_fields import (
    UnknownStore,
    validate as validate_unknown,
    restore as restore_unknown,
)

NUMBERS = (
    "active_test_pattern_key",
    "bit_end",
    "bit_start",
    "caution_id",
    "comment_id",
    "data_limits_mode",
    "data_max",
    "data_max_monitor_key",
    "data_min",
    "data_min_monitor_key",
    "help_id",
    "id",
    "info_id",
    "initial_value",
    "initial_value_mode",
    "initial_value_monitor_key",
    "name_string_index",
    "pattern_match_count",
    "physical_data_key",
    "presentation_pattern",
    "primary_key",
    "prohibition_id",
)
PATTERN = (
    "auto_continuation_time",
    "button_size",
    "key_invalid_flag",
    "key_operation_pattern",
    "lock_time",
    "maintenance_time",
    "pattern_display_key",
    "pattern_key",
    "repeat_enabled",
    "repeat_interval",
    "timeout_parameter",
)
PROGRAM = ("encoded", "request_identifier", "constant_or_mask")
POLICY_TEXT = ("generation_7", "nibble_order", "variant_boundary")
PARENT_KEYS = set(NUMBERS) | {
    "execution",
    "kind",
    "name",
    "pattern",
    "record",
    "request_program",
    "runtime_boundary",
    "signal_info",
    "source",
    "table",
}
PATTERN_KEYS = set(PATTERN) | {"source", "table", "record"}
PROGRAM_KEYS = (
    set(PROGRAM)
    | set(POLICY_TEXT)
    | {"operations", "support_required", "service_by_generation_low5"}
)
DDL = (
    """
CREATE TABLE IF NOT EXISTS text_values(id INTEGER PRIMARY KEY,value TEXT NOT NULL UNIQUE);
CREATE TABLE legacy_operation_policies(id INTEGER PRIMARY KEY,generation7_id INTEGER NOT NULL REFERENCES text_values(id),nibble_order_id INTEGER NOT NULL REFERENCES text_values(id),variant_boundary_id INTEGER NOT NULL REFERENCES text_values(id),service1 INTEGER NOT NULL,service2 INTEGER NOT NULL,service7 INTEGER NOT NULL,service_default INTEGER NOT NULL);
CREATE TABLE legacy_operation_programs(id INTEGER PRIMARY KEY,encoded INTEGER NOT NULL,request_identifier INTEGER NOT NULL,constant_or_mask INTEGER NOT NULL,support_required INTEGER NOT NULL CHECK(support_required IN(0,1)),policy_id INTEGER NOT NULL REFERENCES legacy_operation_policies(id),step_count INTEGER NOT NULL CHECK(step_count>=0));
CREATE TABLE legacy_operation_steps(program_id INTEGER NOT NULL REFERENCES legacy_operation_programs(id),position INTEGER NOT NULL,opcode INTEGER NOT NULL,operation_id INTEGER NOT NULL REFERENCES text_values(id),PRIMARY KEY(program_id,position)) WITHOUT ROWID;
CREATE TABLE legacy_operation_patterns(id INTEGER PRIMARY KEY,"""
    + ",".join(k + " INTEGER NOT NULL" for k in PATTERN)
    + """);
CREATE TABLE legacy_operation_pattern_entries(id INTEGER PRIMARY KEY,definition_id INTEGER NOT NULL REFERENCES legacy_operation_patterns(id),source_id INTEGER NOT NULL REFERENCES text_values(id),table_number INTEGER NOT NULL,record_number INTEGER NOT NULL,unknown_id INTEGER REFERENCES legacy_pattern_unknown_facts(id));
CREATE TABLE legacy_operation_defs(id INTEGER PRIMARY KEY,"""
    + ",".join(
        '"' + ("operation_id" if k == "id" else k) + '" INTEGER NOT NULL'
        for k in NUMBERS
    )
    + """,name_id INTEGER REFERENCES text_values(id),execution_id INTEGER NOT NULL REFERENCES text_values(id),boundary_id INTEGER NOT NULL REFERENCES text_values(id),program_id INTEGER NOT NULL REFERENCES legacy_operation_programs(id),pattern_id INTEGER NOT NULL REFERENCES legacy_operation_pattern_entries(id),signal_info_id INTEGER NOT NULL REFERENCES signal_infos(id));
CREATE TABLE legacy_operation_entries(id INTEGER PRIMARY KEY,definition_id INTEGER NOT NULL REFERENCES legacy_operation_defs(id),source_id INTEGER NOT NULL REFERENCES text_values(id),table_number INTEGER NOT NULL,record_number INTEGER NOT NULL,unknown_id INTEGER REFERENCES legacy_operation_unknown_facts(id));
"""
)


def integer(v):
    if type(v) is not int or not -(1 << 63) <= v < (1 << 63):
        raise ValueError("unsupported operation integer")
    return v


def text(v):
    if not isinstance(v, str):
        raise ValueError("unsupported operation text")
    return v


def same(a, b):
    return json.dumps(
        a, sort_keys=True, ensure_ascii=False, allow_nan=False
    ) == json.dumps(b, sort_keys=True, ensure_ascii=False, allow_nan=False)


class OperationStore:
    def __init__(self, db):
        self.db = db
        db.executescript(DDL)
        self.unknown = UnknownStore(db)
        self.memo = {}
        self.texts = {v: i for i, v in db.execute("SELECT id,value FROM text_values")}

    def string(self, v):
        v = text(v)
        if v not in self.texts:
            self.db.execute("INSERT OR IGNORE INTO text_values(value) VALUES(?)", (v,))
            self.texts[v] = self.db.execute(
                "SELECT id FROM text_values WHERE value=?", (v,)
            ).fetchone()[0]
        return self.texts[v]

    def intern(self, table, values, key=None):
        key = (table, values if key is None else key)
        if key not in self.memo:
            columns = [
                r[1] for r in self.db.execute("PRAGMA table_info(" + table + ")")
            ][1:]
            self.memo[key] = self.db.execute(
                "INSERT INTO "
                + table
                + "("
                + ",".join('"' + c + '"' for c in columns)
                + ") VALUES("
                + ",".join("?" for _ in values)
                + ")",
                values,
            ).lastrowid
        return self.memo[key]

    def pattern(self, r):
        if not isinstance(r, dict) or set(r) - {"uninterpreted_bytes"} != PATTERN_KEYS:
            raise ValueError("unknown pattern")
        if "uninterpreted_bytes" in r and r["uninterpreted_bytes"] is None:
            raise ValueError("invalid pattern unknown fields")
        validate_unknown("pattern", r.get("uninterpreted_bytes"))
        d = self.intern(
            "legacy_operation_patterns", tuple(integer(r[k]) for k in PATTERN)
        )
        return self.intern(
            "legacy_operation_pattern_entries",
            (
                d,
                self.string(r["source"]),
                integer(r["table"]),
                integer(r["record"]),
                self.unknown.intern("pattern", r.get("uninterpreted_bytes")),
            ),
        )

    def program(self, r):
        if not isinstance(r, dict) or set(r) != PROGRAM_KEYS:
            raise ValueError("unknown program")
        services = r["service_by_generation_low5"]
        if not isinstance(services, dict) or set(services) != {
            "1",
            "2",
            "7",
            "default",
        }:
            raise ValueError("unknown service policy")
        if type(r["support_required"]) is not bool or not isinstance(
            r["operations"], list
        ):
            raise ValueError("invalid program")
        steps = []
        for s in r["operations"]:
            if not isinstance(s, dict) or set(s) != {"opcode", "operation"}:
                raise ValueError("unknown operation step")
            steps.append((integer(s["opcode"]), self.string(s["operation"])))
        policy = self.intern(
            "legacy_operation_policies",
            tuple(self.string(r[k]) for k in POLICY_TEXT)
            + tuple(integer(services[k]) for k in ("1", "2", "7", "default")),
        )
        values = tuple(integer(r[k]) for k in PROGRAM) + (
            int(r["support_required"]),
            policy,
            len(steps),
        )
        key = (values, tuple(steps))
        exists = ("legacy_operation_programs", key) in self.memo
        identity = self.intern("legacy_operation_programs", values, key)
        if not exists:
            self.db.executemany(
                "INSERT INTO legacy_operation_steps VALUES(?,?,?,?)",
                [(identity, p, *s) for p, s in enumerate(steps)],
            )
        return identity

    def row(self, r):
        if (
            not isinstance(r, dict)
            or set(r) - {"uninterpreted_bytes"} != PARENT_KEYS
            or r["kind"] != "active_test"
        ):
            raise ValueError("unknown legacy operation")
        # Validate the complete shape before interning any fact. Future fields
        # must stay inline without leaving unused partial definitions behind.
        p = r["pattern"]
        q = r["request_program"]
        if not isinstance(p, dict) or set(p) - {"uninterpreted_bytes"} != PATTERN_KEYS:
            raise ValueError("unknown pattern")
        for domain, value in (("operation", r), ("pattern", p)):
            if "uninterpreted_bytes" in value and value["uninterpreted_bytes"] is None:
                raise ValueError("invalid unknown fields")
            validate_unknown(domain, value.get("uninterpreted_bytes"))
        if not isinstance(q, dict) or set(q) != PROGRAM_KEYS:
            raise ValueError("unknown program")
        for k in PATTERN + ("table", "record"):
            integer(p[k])
        text(p["source"])
        for k in NUMBERS + ("table", "record"):
            integer(r[k])
        for k in ("source", "execution", "runtime_boundary"):
            text(r[k])
        if r["name"] is not None:
            text(r["name"])
        for k in PROGRAM:
            integer(q[k])
        for k in POLICY_TEXT:
            text(q[k])
        services = q["service_by_generation_low5"]
        if not isinstance(services, dict) or set(services) != {
            "1",
            "2",
            "7",
            "default",
        }:
            raise ValueError("unknown service policy")
        for v in services.values():
            integer(v)
        if type(q["support_required"]) is not bool or not isinstance(
            q["operations"], list
        ):
            raise ValueError("invalid program")
        for step in q["operations"]:
            if not isinstance(step, dict) or set(step) != {"opcode", "operation"}:
                raise ValueError("unknown operation step")
            integer(step["opcode"])
            text(step["operation"])
        sig = r["signal_info"]
        if not isinstance(sig, dict) or set(sig) != {"$signal_info"}:
            raise ValueError("unknown signal definition")
        signal = integer(sig["$signal_info"])
        if not self.db.execute(
            "SELECT 1 FROM signal_infos WHERE id=?", (signal,)
        ).fetchone():
            raise ValueError("missing signal")
        numeric = tuple(integer(r[k]) for k in NUMBERS)
        name = None if r["name"] is None else self.string(r["name"])
        values = numeric + (
            name,
            self.string(r["execution"]),
            self.string(r["runtime_boundary"]),
            self.program(r["request_program"]),
            self.pattern(r["pattern"]),
            signal,
        )
        definition = self.intern("legacy_operation_defs", values)
        identity = self.intern(
            "legacy_operation_entries",
            (
                definition,
                self.string(r["source"]),
                integer(r["table"]),
                integer(r["record"]),
                self.unknown.intern("operation", r.get("uninterpreted_bytes")),
            ),
        )
        if not same(restore(self.db, identity), r):
            raise ValueError("operation roundtrip mismatch")
        return {"$legacy_operation": identity}

    def normalize(self, value):
        if isinstance(value, list):
            return [self.normalize(v) for v in value]
        if not isinstance(value, dict):
            return value
        if value.get("kind") == "active_test_pattern" and set(value) - {
            "uninterpreted_bytes"
        } == PATTERN_KEYS | {"kind"}:
            pattern = {k: v for k, v in value.items() if k != "kind"}
            try:
                for k in PATTERN + ("table", "record"):
                    integer(pattern[k])
                text(pattern["source"])
                return {"$legacy_operation_pattern": self.pattern(pattern)}
            except (ValueError, TypeError, KeyError, OverflowError):
                pass
        if value.get("kind") == "active_test" and "request_program" in value:
            try:
                return self.row(value)
            except (ValueError, TypeError, KeyError, OverflowError):
                pass
        return {k: self.normalize(v) for k, v in value.items()}


def one(db, table, identity):
    row = db.execute("SELECT * FROM " + table + " WHERE id=?", (identity,)).fetchone()
    if row is None:
        raise ValueError("missing " + table + " " + str(identity))
    return row[1:]


def string(db, identity):
    return one(db, "text_values", identity)[0]


def restore_pattern(db, identity, with_kind=True):
    definition, source, table, record, unknown = one(
        db, "legacy_operation_pattern_entries", identity
    )
    out = dict(zip(PATTERN, one(db, "legacy_operation_patterns", definition)))
    out.update(source=string(db, source), table=table, record=record)
    if unknown is not None:
        out["uninterpreted_bytes"] = restore_unknown(db, "pattern", unknown)
    if with_kind:
        out["kind"] = "active_test_pattern"
    return out


def restore(db, identity):
    definition, source, table, record, unknown = one(
        db, "legacy_operation_entries", identity
    )
    row = one(db, "legacy_operation_defs", definition)
    out = dict(zip(NUMBERS, row[: len(NUMBERS)]))
    name, execution, boundary, program, pattern, signal = row[len(NUMBERS) :]
    out.update(
        kind="active_test",
        name=None if name is None else string(db, name),
        execution=string(db, execution),
        runtime_boundary=string(db, boundary),
        signal_info={"$signal_info": signal},
        source=string(db, source),
        table=table,
        record=record,
    )
    if not db.execute("SELECT 1 FROM signal_infos WHERE id=?", (signal,)).fetchone():
        raise ValueError("missing operation signal")
    if unknown is not None:
        out["uninterpreted_bytes"] = restore_unknown(db, "operation", unknown)
    out["pattern"] = restore_pattern(db, pattern, with_kind=False)
    encoded, request, mask, support, policy, count = one(
        db, "legacy_operation_programs", program
    )
    if support not in (0, 1) or count < 0:
        raise ValueError("invalid operation policy")
    p = one(db, "legacy_operation_policies", policy)
    result = dict(zip(PROGRAM, (encoded, request, mask)))
    result.update(zip(POLICY_TEXT, (string(db, i) for i in p[:3])))
    result["service_by_generation_low5"] = dict(zip(("1", "2", "7", "default"), p[3:]))
    result["support_required"] = bool(support)
    steps = db.execute(
        "SELECT position,opcode,operation_id FROM legacy_operation_steps WHERE program_id=? ORDER BY position",
        (program,),
    ).fetchall()
    if len(steps) != count or [s[0] for s in steps] != list(range(count)):
        raise ValueError("incomplete operation steps")
    result["operations"] = [
        {"opcode": opcode, "operation": string(db, operation)}
        for _, opcode, operation in steps
    ]
    out["request_program"] = result
    return out
