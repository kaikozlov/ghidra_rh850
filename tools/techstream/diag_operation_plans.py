"""Typed semantic operation plans. Closed domain schemas; no vendor record decoder.

Each schema below is a named diagnostic concept with explicit SQL columns and
foreign keys. Optional fields have presence bits, lists have checked counts.
There is no arbitrary key/value or JSON-node table.
"""

from __future__ import annotations

# i integer; b bool; s shared text; x command hex bytes; @name typed child;
# $name existing semantic marker; [] ordered child list; ~ nullable; ? absent.
SCHEMAS = {}
OPTIONAL = {}


def schema(name, fields, optional=(), combinations=None):
    SCHEMAS[name] = dict(fields)
    OPTIONAL[name] = (
        tuple(optional),
        tuple(tuple(c) for c in combinations) if combinations is not None else ((),),
    )


def fields(kind, names):
    return [(n, kind) for n in names.split()]


schema("variable", [("bytes", "x"), ("id", "s"), ("normalized_id", "s")])
schema(
    "formula_frame",
    [
        ("base_frame", "$operation_base_frame"),
        ("formula", "s"),
        ("materialized_prefix", "x"),
    ],
)
schema(
    "static_frame",
    [
        ("base_frame", "$operation_base_frame"),
        ("materialized_static_request", "x"),
        ("static_command_variable", "~@variable"),
    ],
)
schema(
    "probe_frame",
    [
        ("base_frame", "$operation_base_frame"),
        ("materialized_request", "x"),
        ("positive_check", "x"),
    ],
)
schema(
    "length_probe",
    fields("s", "decoded_value_formula kind received_length_formula selector")
    + [("response_prefix_length", "i"), ("frames", "[]@probe_frame")],
)
schema(
    "initial_read",
    [
        ("mode", "i"),
        ("frames", "[]$operation_frame"),
        ("name", "s"),
        ("resolved", "b"),
        ("selector", "s"),
    ],
    ("frames", "name", "resolved", "selector"),
    ((), ("frames", "name", "resolved", "selector")),
)
schema("example_start", [("raw_0", "x"), ("raw_1", "x")])
schema("example_stop", [("return_control", "x")])
schema(
    "examples",
    [
        ("qualification", "s"),
        ("start", "[]@example_start"),
        ("stop", "[]@example_stop"),
    ],
)
schema(
    "data_binding",
    fields(
        "i",
        "control_enable_bit_1based data_byte_length data_byte_offset did encoding_mode mode5_bit_end_match mode5_bit_start_match record",
    ),
)
schema("choice", [("text", "s"), ("value", "i")])
schema(
    "presentation_pattern",
    fields(
        "i",
        "auto_continue_time button_size key key_invalid_flag key_operation_pattern lock_time maintenance_time pattern_display_key",
    ),
)
schema(
    "scaling",
    fields("i", "decimal_point_count div key mul offset unit_genre_id unit_key")
    + [("signed", "b"), ("unit", "~s")],
)
schema(
    "signal",
    [
        ("choices", "[]@choice"),
        ("engineering_to_raw", "$operation_conversion"),
        ("pattern", "@presentation_pattern"),
        ("physical", "@scaling"),
    ],
)
schema(
    "support_gate",
    fields("s", "family inventory kind mode")
    + [("identifier", "i"), ("length_probe", "s")],
    ("length_probe",),
    ((), ("length_probe",)),
)
COMMON = fields("s", "execution kind name") + fields("i", "id")
schema(
    "direct",
    COMMON
    + fields(
        "i",
        "bit_end bit_start did encoding_mode positive_response runtime_length_minimum service",
    )
    + fields("s", "monitor_name session_requirement")
    + [
        ("monitor_key", "~i"),
        ("control_enable_mask", "$operation_mask"),
        ("encoding_requirements", "$operation_encoding"),
        ("data_id_for_act_records", "[]@data_binding"),
        ("initial_read", "@initial_read"),
        ("minimum_examples", "~@examples"),
        ("runtime_length_probe", "@length_probe"),
        ("signal_info", "@signal"),
        ("start_frames", "[]@formula_frame"),
        ("stop_frames", "[]@formula_frame"),
        ("support_gate", "@support_gate"),
        ("multi_control_group", "b"),
        ("reason", "s"),
    ],
    ("support_gate", "multi_control_group", "reason"),
    ((), ("support_gate",), ("multi_control_group", "reason")),
)
schema(
    "routine",
    COMMON
    + fields(
        "i",
        "output_mask_button_variable output_mask_value_variable positive_response routine_command_variable routine_id routine_status_key routine_stop_command_variable service",
    )
    + [
        ("fixed_request", "b"),
        ("session_requirement", "s"),
        ("output_mask_button", "@variable"),
        ("output_mask_value", "@variable"),
        ("routine_commands", "[]@variable"),
        ("routine_stop_commands", "[]@variable"),
        ("start_frames", "[]@static_frame"),
        ("stop_frames", "[]@static_frame"),
        ("result_frames", "[]@static_frame"),
        ("support_gate", "@support_gate"),
    ],
    ("support_gate",),
    ((), ("support_gate",)),
)
schema(
    "refused",
    COMMON + fields("i", "record routine_id") + [("error", "s")],
    ("routine_id",),
    ((), ("routine_id",)),
)

EXTERNAL = {
    "operation_base_frame": "operation_base_frames",
    "operation_frame": "operation_frames",
    "operation_conversion": "operation_conversions",
    "operation_mask": "operation_mask_policies",
    "operation_encoding": "operation_encoding_policies",
}
ROOTS = ("direct", "routine", "refused")


def table(name):
    return "plan_" + name


def column(name):
    return "f_" + name


def base_type(typ):
    return typ.removeprefix("~")


def sqltype(typ):
    typ = base_type(typ)
    if typ == "x":
        return "BLOB"
    if typ == "s":
        return "INTEGER REFERENCES text_values(id)"
    if typ.startswith("@"):
        return "INTEGER REFERENCES " + table(typ[1:]) + "(id)"
    if typ.startswith("$"):
        return "INTEGER REFERENCES " + EXTERNAL[typ[1:]] + "(id)"
    return "INTEGER"


def ddl():
    parts = [
        "CREATE TABLE IF NOT EXISTS text_values(id INTEGER PRIMARY KEY,value TEXT NOT NULL UNIQUE);"
    ]
    for name, fs in SCHEMAS.items():
        cols = ["id INTEGER PRIMARY KEY", "present INTEGER NOT NULL"]
        opts = OPTIONAL[name][0]
        for f, t in fs.items():
            if t.startswith("[]"):
                cols.append(
                    column(f)
                    + " INTEGER"
                    + ("" if f in opts else " NOT NULL")
                    + " CHECK("
                    + column(f)
                    + ">=0)"
                )
            else:
                cols.append(
                    column(f)
                    + " "
                    + sqltype(t)
                    + ("" if f in opts or t.startswith("~") else " NOT NULL")
                )
        parts.append("CREATE TABLE " + table(name) + "(" + ",".join(cols) + ");")
        for f, t in fs.items():
            if t.startswith("[]"):
                parts.append(
                    "CREATE TABLE "
                    + table(name)
                    + "_"
                    + f
                    + "(parent_id INTEGER NOT NULL REFERENCES "
                    + table(name)
                    + "(id),position INTEGER NOT NULL,value "
                    + sqltype(t[2:])
                    + " NOT NULL,PRIMARY KEY(parent_id,position)) WITHOUT ROWID;"
                )
    parts.append(
        "CREATE TABLE operation_plan_entries(id INTEGER PRIMARY KEY,direct_id INTEGER REFERENCES plan_direct(id),routine_id INTEGER REFERENCES plan_routine(id),refused_id INTEGER REFERENCES plan_refused(id),CHECK((direct_id IS NOT NULL)+(routine_id IS NOT NULL)+(refused_id IS NOT NULL)=1));"
    )
    return "\n".join(parts)


DDL = ddl()


def integer(v):
    if type(v) is not int or not -(1 << 63) <= v < (1 << 63):
        raise ValueError("invalid plan integer")
    return v


def valid(name, row):
    if not isinstance(row, dict):
        raise ValueError("invalid plan object")
    opts, allowed = OPTIONAL[name]
    fs = SCHEMAS[name]
    if (
        set(row) - set(fs)
        or set(fs) - set(opts) - set(row)
        or tuple(k for k in opts if k in row) not in allowed
    ):
        raise ValueError("unknown plan shape")
    for k, v in row.items():
        validate_value(fs[k], v)


def validate_value(typ, v):
    if typ.startswith("~"):
        if v is None:
            return
        typ = typ[1:]
    if typ.startswith("[]"):
        if not isinstance(v, list):
            raise ValueError("invalid plan list")
        for c in v:
            validate_value(typ[2:], c)
    elif typ.startswith("@"):
        valid(typ[1:], v)
    elif typ.startswith("$"):
        if not isinstance(v, dict) or set(v) != {typ}:
            raise ValueError("invalid semantic plan ref")
        if integer(v[typ]) <= 0:
            raise ValueError("invalid semantic plan id")
    elif typ == "i":
        integer(v)
    elif typ == "b":
        if type(v) is not bool:
            raise ValueError("invalid plan boolean")
    elif typ in ("s", "x"):
        if not isinstance(v, str):
            raise ValueError("invalid plan text")
        if typ == "x" and bytes.fromhex(v).hex() != v:
            raise ValueError("noncanonical plan command")
    else:
        raise ValueError("unknown plan field type")


class PlanStore:
    def __init__(self, db):
        self.db = db
        db.executescript(DDL)
        self.memo = {}
        self.strings = {v: i for i, v in db.execute("SELECT id,value FROM text_values")}

    def string(self, v):
        if v not in self.strings:
            self.db.execute("INSERT OR IGNORE INTO text_values(value) VALUES(?)", (v,))
            self.strings[v] = self.db.execute(
                "SELECT id FROM text_values WHERE value=?", (v,)
            ).fetchone()[0]
        return self.strings[v]

    def encode(self, typ, v):
        if typ.startswith("~"):
            if v is None:
                return None
            typ = typ[1:]
        if typ.startswith("@"):
            return self.intern(typ[1:], v)
        if typ.startswith("$"):
            identity = v[typ]
            if (
                self.db.execute(
                    "SELECT 1 FROM " + EXTERNAL[typ[1:]] + " WHERE id=?", (identity,)
                ).fetchone()
                is None
            ):
                raise ValueError("missing plan external definition")
            return identity
        if typ == "s":
            return self.string(v)
        if typ == "x":
            return bytes.fromhex(v)
        if typ == "b":
            return int(v)
        return v

    def intern(self, name, row):
        fs = SCHEMAS[name]
        opts = OPTIONAL[name][0]
        present = sum(1 << i for i, k in enumerate(opts) if k in row)
        values = [present]
        children = {}
        for f, t in fs.items():
            if f not in row:
                values.append(None)
            elif t.startswith("[]"):
                items = tuple(self.encode(t[2:], v) for v in row[f])
                children[f] = items
                values.append(len(items))
            else:
                values.append(self.encode(t, row[f]))
        key = (name, tuple(values), tuple(children.items()))
        if key in self.memo:
            return self.memo[key]
        cols = ["present"] + [column(f) for f in fs]
        identity = self.db.execute(
            "INSERT INTO "
            + table(name)
            + "("
            + ",".join(cols)
            + ") VALUES("
            + ",".join("?" for _ in values)
            + ")",
            values,
        ).lastrowid
        for f, items in children.items():
            self.db.executemany(
                "INSERT INTO " + table(name) + "_" + f + " VALUES(?,?,?)",
                [(identity, p, v) for p, v in enumerate(items)],
            )
        self.memo[key] = identity
        return identity

    def normalize_plan(self, row):
        if not isinstance(row, dict):
            return row
        name = "refused" if "error" in row else row.get("kind")
        if name not in ROOTS:
            return row
        try:
            valid(name, row)
        except (ValueError, TypeError, KeyError, OverflowError):
            return row
        # Invalid references are corruption, not a new semantic shape.
        definition = self.intern(name, row)
        refs = tuple(definition if k == name else None for k in ROOTS)
        key = ("root", refs)
        if key not in self.memo:
            self.memo[key] = self.db.execute(
                "INSERT INTO operation_plan_entries(direct_id,routine_id,refused_id) VALUES(?,?,?)",
                refs,
            ).lastrowid
        return {"$operation_plan": self.memo[key]}

    def normalize(self, value):
        if not isinstance(value, dict):
            return value
        out = dict(value)
        if isinstance(out.get("active_tests"), list):
            out["active_tests"] = [self.normalize_plan(r) for r in out["active_tests"]]
        return out


def restore(db, identity):
    row = db.execute(
        "SELECT direct_id,routine_id,refused_id FROM operation_plan_entries WHERE id=?",
        (identity,),
    ).fetchone()
    if row is None or sum(v is not None for v in row) != 1:
        raise ValueError("invalid operation plan reference")
    name = ROOTS[next(i for i, v in enumerate(row) if v is not None)]
    return restore_object(db, name, next(v for v in row if v is not None))


def restore_object(db, name, identity):
    fs = SCHEMAS[name]
    opts, allowed = OPTIONAL[name]
    row = db.execute(
        "SELECT present,"
        + ",".join(column(f) for f in fs)
        + " FROM "
        + table(name)
        + " WHERE id=?",
        (identity,),
    ).fetchone()
    if row is None:
        raise ValueError("missing " + table(name))
    present = row[0]
    if type(present) is not int or present < 0 or present >= (1 << len(opts)):
        raise ValueError("invalid plan presence")
    included = tuple(k for i, k in enumerate(opts) if present & (1 << i))
    if included not in allowed:
        raise ValueError("invalid plan optional combination")
    out = {}
    for (f, t), v in zip(fs.items(), row[1:]):
        if f in opts and f not in included:
            if v is not None:
                raise ValueError("unexpected absent plan value")
            continue
        if t.startswith("[]"):
            if type(v) is not int or v < 0:
                raise ValueError("invalid plan child count")
            children = db.execute(
                "SELECT position,value FROM "
                + table(name)
                + "_"
                + f
                + " WHERE parent_id=? ORDER BY position",
                (identity,),
            ).fetchall()
            if len(children) != v or [p for p, _ in children] != list(range(v)):
                raise ValueError("incomplete plan children")
            out[f] = [decode(db, t[2:], c) for _, c in children]
        else:
            out[f] = decode(db, t, v)
    return out


def decode(db, typ, v):
    if typ.startswith("~"):
        if v is None:
            return None
        typ = typ[1:]
    if v is None:
        raise ValueError("missing required plan value")
    if typ.startswith("@"):
        return restore_object(db, typ[1:], v)
    if typ.startswith("$"):
        if (
            db.execute(
                "SELECT 1 FROM " + EXTERNAL[typ[1:]] + " WHERE id=?", (v,)
            ).fetchone()
            is None
        ):
            raise ValueError("missing plan external definition")
        return {typ: v}
    if typ == "s":
        r = db.execute("SELECT value FROM text_values WHERE id=?", (v,)).fetchone()
        if r is None:
            raise ValueError("missing plan text")
        return r[0]
    if typ == "x":
        if not isinstance(v, bytes):
            raise ValueError("invalid plan command bytes")
        return v.hex()
    if typ == "b":
        if v not in (0, 1):
            raise ValueError("invalid plan boolean")
        return bool(v)
    return integer(v)
