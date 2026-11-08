"""Shared decoded ROB and freeze-frame signal observations.

The observation is semantic: decoded geometry, identifiers, presentation and
support flags bind existing signal/condition definitions. Origins are separate
small bindings. No OEM raw rows or inferred source decoding is involved.
"""

from __future__ import annotations

import math

COMMON = {
    "bit_end",
    "bit_start",
    "local_support_mode",
    "name",
    "pattern_display_key",
    "physical_data_key",
    "record",
    "signal_info",
    "sort_key",
    "source",
    "table",
}
SHAPES = {
    1: COMMON
    | {
        "did",
        "dynamic_lsb_possible",
        "exception_handler_flag",
        "exception_handler_id",
        "extraction_mode",
        "presentation_mode",
        "record_key",
        "support_condition_key",
    },
    2: COMMON
    | {
        "decoder",
        "did",
        "did_support",
        "exception_handler_flag",
        "exception_handler_id",
        "extraction_mode",
        "name_string_index",
        "physical_range",
        "presentation_mode",
        "record_key",
        "support_condition",
        "support_condition_key",
    },
    3: COMMON
    | {
        "dynamic_lsb_possible",
        "flags",
        "monitor_key",
        "primary_did",
        "snapshot_did",
        "support_condition",
        "tables",
    },
    4: COMMON
    | {
        "dynamic_lsb_possible",
        "flags",
        "monitor_key",
        "primary_did",
        "snapshot_did",
        "support_condition",
    },
    5: COMMON
    | {
        "alternate_did",
        "decoder",
        "did_support",
        "extraction_mode",
        "flags",
        "graph_range",
        "monitor_key",
        "physical_range",
        "primary_did",
        "snapshot_did",
        "support_condition",
        "visibility_override",
    },
}
INTEGER_FIELDS = (
    "bit_end",
    "bit_start",
    "local_support_mode",
    "pattern_display_key",
    "physical_data_key",
    "sort_key",
    "did",
    "exception_handler_flag",
    "exception_handler_id",
    "extraction_mode",
    "presentation_mode",
    "record_key",
    "support_condition_key",
    "name_string_index",
    "flags",
    "monitor_key",
    "primary_did",
    "snapshot_did",
    "alternate_did",
    "visibility_override",
)
COLUMNS = (
    "shape",
    "name_id",
    "decoder_id",
    "info_id",
    "support_id",
    "condition_id",
    "dynamic_lsb",
    *INTEGER_FIELDS,
    "physical_low",
    "physical_high",
    "graph_low",
    "graph_high",
    "auxiliary_tables",
    "unknown_bytes",
)
DDL = (
    """
CREATE TABLE IF NOT EXISTS text_values(id INTEGER PRIMARY KEY,value TEXT NOT NULL UNIQUE);
CREATE TABLE IF NOT EXISTS signal_observations(
 id INTEGER PRIMARY KEY,shape INTEGER NOT NULL,
 name_id INTEGER REFERENCES text_values(id),decoder_id INTEGER REFERENCES text_values(id),
 info_id INTEGER NOT NULL REFERENCES signal_infos(id),support_id INTEGER REFERENCES signal_did_support(id),
 condition_id INTEGER REFERENCES signal_conditions(id),dynamic_lsb INTEGER,
"""
    + ",\n".join(f"{name} INTEGER" for name in INTEGER_FIELDS)
    + """,
 physical_low REAL,physical_high REAL,graph_low INTEGER,graph_high INTEGER,auxiliary_tables INTEGER,unknown_bytes BLOB);
CREATE TABLE IF NOT EXISTS signal_observation_entries(
 id INTEGER PRIMARY KEY,definition_id INTEGER NOT NULL REFERENCES signal_observations(id),
 source_id INTEGER REFERENCES text_values(id),table_number INTEGER NOT NULL,record_number INTEGER NOT NULL);
"""
)


def _integer(value):
    return type(value) is int and -(1 << 63) <= value < (1 << 63)


def _reference(value, marker, nullable=False):
    if nullable and value is None:
        return None
    if (
        type(value) is not dict
        or set(value) != {marker}
        or not _integer(value[marker])
        or value[marker] <= 0
    ):
        raise ValueError("invalid semantic signal reference")
    return value[marker]


class ObservationStore:
    def __init__(self, db):
        self.db = db
        db.executescript(DDL)
        self.texts = {}
        self.definitions = {
            tuple(r[1:]): r[0] for r in db.execute("SELECT * FROM signal_observations")
        }
        self.entries = {
            tuple(r[1:]): r[0]
            for r in db.execute("SELECT * FROM signal_observation_entries")
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
        if type(row) is not dict:
            return row
        shape = next(
            (
                n
                for n, fields in SHAPES.items()
                if set(row) - {"uninterpreted_bytes"} == fields
            ),
            None,
        )
        if shape is None:
            return row
        try:
            from tools.techstream.diag_product_behavior_codes import rob_unknown_bytes

            unknown = rob_unknown_bytes(row)
            if unknown is not None and (shape != 2 or row["table"] != 164):
                return row
            for field in ("name", "source", "decoder"):
                if (
                    field in row
                    and row[field] is not None
                    and type(row[field]) is not str
                ):
                    raise ValueError("invalid text")
            if any(
                not _integer(row[f])
                and not (f == "local_support_mode" and row[f] is None)
                for f in (*INTEGER_FIELDS, "table", "record")
                if f in row
            ):
                raise ValueError("invalid integer")
            if row["record"] < 0 or row["table"] < 0:
                raise ValueError("invalid origin")
            if (
                "dynamic_lsb_possible" in row
                and type(row["dynamic_lsb_possible"]) is not bool
            ):
                raise ValueError("invalid boolean")
            if shape == 3 and (
                type(row["tables"]) is not list
                or not 2 <= len(row["tables"]) <= 1001
                or row["tables"][0] != 62
                or any(type(x) is not int or x != 157 for x in row["tables"][1:])
            ):
                raise ValueError("unknown table alternatives")
            info = _reference(row["signal_info"], "$signal_info")
            support = (
                _reference(row["did_support"], "$did_support", True)
                if "did_support" in row
                else None
            )
            condition = (
                _reference(row["support_condition"], "$support_condition", True)
                if "support_condition" in row
                else None
            )
            physical = row.get("physical_range", [None, None])
            graph = row.get("graph_range", [None, None])
            if "physical_range" in row and (
                type(physical) is not list
                or len(physical) != 2
                or any(
                    type(x) is not float
                    or not math.isfinite(x)
                    or (x == 0 and math.copysign(1, x) < 0)
                    for x in physical
                )
            ):
                raise ValueError("unsupported real range")
            if "graph_range" in row and (
                type(graph) is not list
                or len(graph) != 2
                or not all(_integer(x) for x in graph)
            ):
                raise ValueError("invalid graph range")
        except (KeyError, ValueError, TypeError):
            return row
        key = (
            shape,
            self.text(row["name"]),
            self.text(row.get("decoder")),
            info,
            support,
            condition,
            int(row["dynamic_lsb_possible"]) if "dynamic_lsb_possible" in row else None,
            *(row.get(f) for f in INTEGER_FIELDS),
            *physical,
            *graph,
            len(row["tables"]) - 1 if shape == 3 else None,
            unknown,
        )
        if key not in self.definitions:
            self.definitions[key] = self.db.execute(
                f"INSERT INTO signal_observations({','.join(COLUMNS)}) VALUES({','.join('?' for _ in COLUMNS)})",
                key,
            ).lastrowid
        binding = (
            self.definitions[key],
            self.text(row["source"]),
            row["table"],
            row["record"],
        )
        if binding not in self.entries:
            self.entries[binding] = self.db.execute(
                "INSERT INTO signal_observation_entries(definition_id,source_id,table_number,record_number) VALUES(?,?,?,?)",
                binding,
            ).lastrowid
        return {"$signal_observation": self.entries[binding]}

    def normalize(self, document):
        if type(document) is not dict:
            return document
        result = dict(document)
        for field in ("rob", "generic_ffd", "p6_rob_source"):
            value = document.get(field)
            if type(value) is dict and type(value.get("signals")) is list:
                result[field] = {
                    **value,
                    "signals": [self.row(r) for r in value["signals"]],
                }
        return result


def restore(db, identity):
    if type(identity) is not int or identity <= 0:
        raise ValueError("invalid signal observation")
    row = db.execute(
        "SELECT d.*,s.value,e.table_number,e.record_number,e.source_id FROM signal_observation_entries e JOIN signal_observations d ON d.id=e.definition_id LEFT JOIN text_values s ON s.id=e.source_id WHERE e.id=?",
        (identity,),
    ).fetchone()
    if row is None:
        raise ValueError("missing signal observation")
    values = dict(zip(COLUMNS, row[1 : 1 + len(COLUMNS)]))
    source, table, record, source_id = row[1 + len(COLUMNS) :]
    shape = values["shape"]
    if (
        shape not in SHAPES
        or (source_id is None) != (source is None)
        or not _integer(table)
        or not _integer(record)
        or table < 0
        or record < 0
    ):
        raise ValueError("invalid observation shape/origin")

    def text(identity):
        if identity is None:
            return None
        r = db.execute(
            "SELECT value FROM text_values WHERE id=?", (identity,)
        ).fetchone()
        if r is None:
            raise ValueError("missing observation text")
        return r[0]

    fields = SHAPES[shape]
    result = {
        "source": source,
        "table": table,
        "record": record,
        "name": text(values["name_id"]),
    }
    for key in INTEGER_FIELDS:
        value = values[key]
        if key in fields:
            if not _integer(value) and not (
                key == "local_support_mode" and value is None
            ):
                raise ValueError("missing observation integer")
            result[key] = value
        elif value is not None:
            raise ValueError("unexpected observation integer")
    if "decoder" in fields:
        result["decoder"] = text(values["decoder_id"])
    elif values["decoder_id"] is not None:
        raise ValueError("unexpected observation decoder")
    for field, column, marker in (
        ("signal_info", "info_id", "$signal_info"),
        ("did_support", "support_id", "$did_support"),
        ("support_condition", "condition_id", "$support_condition"),
    ):
        value = values[column]
        if field in fields:
            if value is not None and (not _integer(value) or value <= 0):
                raise ValueError("invalid observation reference")
            if field == "signal_info" and value is None:
                raise ValueError("missing signal info")
            result[field] = None if value is None else {marker: value}
        elif value is not None:
            raise ValueError("unexpected observation reference")
    if "dynamic_lsb_possible" in fields:
        if values["dynamic_lsb"] not in (0, 1):
            raise ValueError("invalid dynamic LSB flag")
        result["dynamic_lsb_possible"] = bool(values["dynamic_lsb"])
    elif values["dynamic_lsb"] is not None:
        raise ValueError("unexpected dynamic LSB flag")
    for field, low, high in (
        ("physical_range", "physical_low", "physical_high"),
        ("graph_range", "graph_low", "graph_high"),
    ):
        pair = [values[low], values[high]]
        if field in fields:
            valid = (
                all(type(x) is float and math.isfinite(x) for x in pair)
                if field == "physical_range"
                else all(_integer(x) for x in pair)
            )
            if not valid:
                raise ValueError("invalid observation range")
            result[field] = pair
        elif any(x is not None for x in pair):
            raise ValueError("unexpected observation range")
    if shape == 3:
        count = values["auxiliary_tables"]
        if not _integer(count) or not 1 <= count <= 1000:
            raise ValueError("invalid auxiliary table count")
        result["tables"] = [62] + [157] * count
    elif values["auxiliary_tables"] is not None:
        raise ValueError("unexpected auxiliary tables")
    from tools.techstream.diag_product_behavior_codes import restore_rob_unknown

    if values["unknown_bytes"] is not None and shape != 2:
        raise ValueError("unexpected observation unknown fields")
    restore_rob_unknown(result, values["unknown_bytes"])
    return result
