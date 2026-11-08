"""Shared decoded monitor facts and physical records.

Fixed semantic schemas retain every decoded field, including unresolved fields.
Unknown shapes stay inline. This module never decodes vendor bytes.
"""

from dataclasses import dataclass
import math
from tools.techstream.diag_freeze_physical import integer


@dataclass(frozen=True)
class Spec:
    integers: str
    texts: str
    ranges: str = ""
    kind: str = ""
    children: bool = False
    shared: str = ""


ORIGIN = "record table"
GATES = "exception_handler_flag exception_handler_id"
SPECS = {
    "pattern": Spec(
        GATES + " key",
        "source unassigned_fields.14_15 unassigned_fields.18_22 unassigned_fields.8_11",
        shared="pattern",
    ),
    "physical": Spec(
        "decimal_point_count div "
        + GATES
        + " key mul offset "
        + ORIGIN
        + " sign_mode unit_key unassigned_fields.23",
        "source unassigned_fields.18_19",
    ),
    "unit": Spec(GATES + " key unassigned_fields.11", "source", shared="unit"),
    "pcs_ffd": Spec(
        "pid "
        + ORIGIN
        + " request.function_selector request.pid_byte_offset retrieval_group unassigned_word0",
        "source",
        kind="pcs_operation_ffd_pid",
    ),
    "data_id": Spec(
        "did " + GATES + " fixed_length " + ORIGIN + " support_mode",
        "source",
        kind="data_id",
    ),
    "monitor": Spec(
        "bit_end bit_start data_range_max data_range_min extraction_mode ffd_support_condition_key flags graph_max graph_min live_support_condition_key monitor_key name_string_index pattern_display_key physical_data_key primary_did "
        + ORIGIN
        + " snapshot_did sort_key visibility_override",
        "name source unassigned_ranges.10_27 unassigned_ranges.2c_2f unassigned_ranges.44_45 unassigned_ranges.4c_4f",
        "physical_max physical_min",
        "monitor",
        True,
    ),
    "condition": Spec(
        "bit_end bit_start comparison_mode comparison_value condition_type "
        + GATES
        + " key "
        + ORIGIN
        + " referenced_did unassigned_tail variable_id",
        "source variable_bytes",
        kind="support_condition",
    ),
    "condition_compact": Spec(
        "bit_end bit_start condition_type "
        + GATES
        + " key "
        + ORIGIN
        + " referenced_did variable_id",
        "source variable_bytes",
        kind="support_condition",
    ),
    "dtc_status": Spec(
        "comparison_value "
        + GATES
        + " key "
        + ORIGIN
        + " status_mask unassigned_fields.byte11 unassigned_fields.word4",
        "source",
        kind="dtc_status",
    ),
    "dynamic_did": Spec(
        "did " + GATES + " maximum_payload_length " + ORIGIN + " unassigned_tail",
        "source",
        kind="dynamic_did",
    ),
    "behavior": Spec(
        "behavior_code comment_string_index name_string_index " + ORIGIN,
        "comment name signature source unassigned_tail",
        kind="behavior_code",
    ),
    "rob_signal": Spec(
        "bit_end bit_start did "
        + GATES
        + " extraction_mode name_string_index pattern_display_key physical_data_key presentation_mode "
        + ORIGIN
        + " record_key sort_key support_condition_key",
        "name source unassigned_ranges.0_1f unassigned_ranges.24_2b unassigned_ranges.40_41 unassigned_ranges.43_47",
        kind="rob_signal",
        children=True,
    ),
    "rob_special": Spec(
        GATES + " key " + ORIGIN + " signal_key unassigned_fields.word6",
        "source unassigned_fields.tail9",
        kind="rob_special_signal",
    ),
}
CHILDREN = (
    ("pattern_records", "pattern"),
    ("physical_records", "physical"),
    ("unit_records", "unit"),
)
SHARED = {
    "pattern": ("record name_string_index table value".split(), ["name"]),
    "unit": ("genre_id record name_string_index table".split(), ["name"]),
}


def fields(spec):
    ints = spec.integers.split()
    texts = spec.texts.split()
    if spec.shared:
        extra_ints, extra_texts = SHARED[spec.shared]
        ints += extra_ints
        texts += extra_texts
    return ints, texts, spec.ranges.split()


def tree(paths):
    result = {}
    for path in paths:
        cursor = result
        parts = path.split(".")
        for part in parts[:-1]:
            cursor = cursor.setdefault(part, {})
        cursor[parts[-1]] = None
    return result


def exact_shape(value, shape):
    if type(value) is not dict or set(value) != set(shape):
        return False
    return all(
        child is None or exact_shape(value[key], child) for key, child in shape.items()
    )


SHAPES = {
    name: tree(
        sum((list(x) for x in fields(spec)), [])
        + (["kind"] if spec.kind else [])
        + ([k for k, _ in CHILDREN] if spec.children else [])
    )
    for name, spec in SPECS.items()
}


def get(row, path):
    for part in path.split("."):
        row = row[part]
    return row


def put(row, path, value):
    parts = path.split(".")
    for part in parts[:-1]:
        row = row.setdefault(part, {})
    row[parts[-1]] = value


def column(path):
    return path.replace(".", "__")


def ddl():
    result = []
    for name, spec in SPECS.items():
        cols = ['"' + column(k) + '" INTEGER NOT NULL' for k in spec.integers.split()]
        cols += [
            column(k) + "_id INTEGER REFERENCES text_values(id)"
            for k in spec.texts.split()
        ]
        cols += [column(k) + " REAL NOT NULL" for k in spec.ranges.split()]
        if spec.shared:
            cols += [
                "value_id INTEGER NOT NULL REFERENCES freeze_"
                + ("patterns" if spec.shared == "pattern" else "units")
                + "(id)"
            ]
        if spec.children:
            cols += [
                k + "_count INTEGER NOT NULL CHECK(" + k + "_count>=0)"
                for k, _ in CHILDREN
            ]
        result.append(
            "CREATE TABLE IF NOT EXISTS decoded_"
            + name
            + "(id INTEGER PRIMARY KEY,"
            + ",".join(cols)
            + ");"
        )
        if spec.children:
            for key, child in CHILDREN:
                result.append(
                    "CREATE TABLE IF NOT EXISTS decoded_"
                    + name
                    + "_"
                    + key
                    + "(owner_id INTEGER NOT NULL REFERENCES decoded_"
                    + name
                    + "(id),position INTEGER NOT NULL,child_id INTEGER NOT NULL REFERENCES decoded_"
                    + child
                    + "(id),PRIMARY KEY(owner_id,position)) WITHOUT ROWID;"
                )
    return "\n".join(result)


DDL = ddl()


class Store:
    def __init__(self, db):
        self.db = db
        db.executescript(DDL)
        self.texts = {}
        self.cache = {}
        self.shared = {}
        for table in ("freeze_units", "freeze_patterns"):
            self.shared[table] = {
                tuple(r[1:]): r[0] for r in db.execute("SELECT * FROM " + table)
            }
        for name, spec in SPECS.items():
            cache = self.cache[name] = {}
            for row in db.execute("SELECT * FROM decoded_" + name):
                relations = (
                    tuple(
                        tuple(
                            x[0]
                            for x in db.execute(
                                "SELECT child_id FROM decoded_"
                                + name
                                + "_"
                                + key
                                + " WHERE owner_id=? ORDER BY position",
                                (row[0],),
                            )
                        )
                        for key, _ in CHILDREN
                    )
                    if spec.children
                    else ()
                )
                cache[tuple(row[1:]) + relations] = row[0]

    def valid(self, name, row):
        spec = SPECS[name]
        if not exact_shape(row, SHAPES[name]):
            return False
        if spec.kind and row["kind"] != spec.kind:
            return False
        if type(row["source"]) is not str:
            return False
        ints, texts, ranges = fields(spec)
        try:
            for k in ints:
                integer(get(row, k))
        except (TypeError, ValueError):
            return False
        if any(get(row, k) is not None and type(get(row, k)) is not str for k in texts):
            return False
        for k in ranges:
            v = get(row, k)
            if (
                type(v) is not float
                or not math.isfinite(v)
                or (v == 0 and math.copysign(1, v) < 0)
            ):
                return False
        if spec.children:
            for key, child in CHILDREN:
                if type(row[key]) is not list or not all(
                    self.valid(child, v) for v in row[key]
                ):
                    return False
        return True

    def text(self, value):
        if value is None:
            return None
        if value not in self.texts:
            self.db.execute(
                "INSERT OR IGNORE INTO text_values(value)VALUES(?)", (value,)
            )
            self.texts[value] = self.db.execute(
                "SELECT id FROM text_values WHERE value=?", (value,)
            ).fetchone()[0]
        return self.texts[value]

    def shared_value(self, kind, row):
        if kind == "pattern":
            table = "freeze_patterns"
            values = (
                row["record"],
                row["name_string_index"],
                row["table"],
                self.text(row["name"]),
                row["value"],
            )
        else:
            table = "freeze_units"
            values = (
                row["genre_id"],
                row["record"],
                row["name_string_index"],
                row["table"],
                self.text(row["name"]),
            )
        cache = self.shared[table]
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

    def intern(self, name, row):
        spec = SPECS[name]
        values = (
            tuple(get(row, k) for k in spec.integers.split())
            + tuple(self.text(get(row, k)) for k in spec.texts.split())
            + tuple(get(row, k) for k in spec.ranges.split())
        )
        if spec.shared:
            values += (self.shared_value(spec.shared, row),)
        relations = (
            tuple(
                tuple(self.intern(child, v) for v in row[key])
                for key, child in CHILDREN
            )
            if spec.children
            else ()
        )
        values += tuple(len(v) for v in relations)
        key = values + relations
        cache = self.cache[name]
        if key not in cache:
            ident = self.db.execute(
                "INSERT INTO decoded_"
                + name
                + " VALUES("
                + ",".join("?" for _ in range(len(values) + 1))
                + ")",
                (None, *values),
            ).lastrowid
            for (field, _), relation in zip(CHILDREN, relations):
                self.db.executemany(
                    "INSERT INTO decoded_" + name + "_" + field + " VALUES(?,?,?)",
                    [(ident, i, v) for i, v in enumerate(relation)],
                )
            cache[key] = ident
        return cache[key]

    def row(self, name, row):
        # Validate the entire nested definition before writing any rows. A future
        # shape must remain inline without orphan child/text records.
        if not self.valid(name, row):
            return row
        return {"$decoded_" + name: self.intern(name, row)}

    def normalize(self, document):
        physical = document.get("physical_catalog")
        if isinstance(physical, dict):
            for key, name in (
                ("patterns", "pattern"),
                ("physical", "physical"),
                ("units", "unit"),
            ):
                if isinstance(physical.get(key), list):
                    physical[key] = [self.row(name, v) for v in physical[key]]
        rows = document.get("monitor_source")
        if isinstance(rows, list):
            result = []
            for row in rows:
                if type(row) is not dict:
                    result.append(row)
                    continue
                names = [
                    name
                    for name, spec in SPECS.items()
                    if spec.kind and row.get("kind") == spec.kind
                ]
                value = row
                for name in names:
                    if self.valid(name, row):
                        value = {"$decoded_" + name: self.intern(name, row)}
                        break
                result.append(value)
            document["monitor_source"] = result
        return document


def restore(db, name, ident):
    if name not in SPECS or type(ident) is not int or ident <= 0:
        raise ValueError("invalid decoded monitor reference")
    spec = SPECS[name]
    row = db.execute(
        "SELECT * FROM decoded_" + name + " WHERE id=?", (ident,)
    ).fetchone()
    if row is None:
        raise ValueError("missing decoded monitor definition")
    values = iter(row[1:])
    out = {}
    for key in spec.integers.split():
        put(out, key, next(values))
    for key in spec.texts.split():
        i = next(values)
        text = (
            None
            if i is None
            else db.execute("SELECT value FROM text_values WHERE id=?", (i,)).fetchone()
        )
        if i is not None and text is None:
            raise ValueError("missing decoded monitor text")
        put(out, key, None if text is None else text[0])
    for key in spec.ranges.split():
        put(out, key, next(values))
    if spec.shared:
        i = next(values)
        if spec.shared == "pattern":
            data = db.execute(
                "SELECT p.record,p.string_index,p.table_type,t.value,p.value FROM freeze_patterns p LEFT JOIN text_values t ON t.id=p.text_id WHERE p.id=?",
                (i,),
            ).fetchone()
            keys = ("record", "name_string_index", "table", "name", "value")
        else:
            data = db.execute(
                "SELECT u.genre_id,u.record,u.string_index,u.table_type,t.value FROM freeze_units u LEFT JOIN text_values t ON t.id=u.text_id WHERE u.id=?",
                (i,),
            ).fetchone()
            keys = ("genre_id", "record", "name_string_index", "table", "name")
        if data is None:
            raise ValueError("missing decoded physical semantic value")
        out.update(zip(keys, data))
    if spec.kind:
        out["kind"] = spec.kind
    if spec.children:
        for key, child in CHILDREN:
            count = next(values)
            out[key] = []
            for position, child_id in db.execute(
                "SELECT position,child_id FROM decoded_"
                + name
                + "_"
                + key
                + " WHERE owner_id=? ORDER BY position",
                (ident,),
            ):
                if position != len(out[key]):
                    raise ValueError("invalid decoded child order")
                out[key].append({"$decoded_" + child: child_id})
            if len(out[key]) != count:
                raise ValueError("incomplete decoded child relationship")
    return out
