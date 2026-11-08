"""Typed signal definitions and data-list views shared by their source uses."""

from __future__ import annotations

import json
import math
from tools.techstream.diag_codec import compress, decompress

SCHEMA = """
CREATE TABLE IF NOT EXISTS text_values(id INTEGER PRIMARY KEY,value TEXT NOT NULL UNIQUE);
CREATE TABLE IF NOT EXISTS signal_labels(id INTEGER PRIMARY KEY,monitor_key INTEGER NOT NULL,name_id INTEGER NOT NULL REFERENCES text_values(id),bit_start INTEGER NOT NULL,bit_end INTEGER NOT NULL);
CREATE TABLE IF NOT EXISTS signal_pattern_sets(id INTEGER PRIMARY KEY,entry_count INTEGER NOT NULL);
CREATE TABLE IF NOT EXISTS signal_pattern_entries(set_id INTEGER NOT NULL REFERENCES signal_pattern_sets(id),key_id INTEGER NOT NULL REFERENCES text_values(id),value_id INTEGER REFERENCES text_values(id),PRIMARY KEY(set_id,key_id)) WITHOUT ROWID;
CREATE TABLE IF NOT EXISTS signal_infos(id INTEGER PRIMARY KEY,bit_width INTEGER NOT NULL,decimal_point_count INTEGER NOT NULL,div INTEGER NOT NULL,mul INTEGER NOT NULL,offset INTEGER NOT NULL,physical_data_key INTEGER NOT NULL,sign_mode INTEGER NOT NULL,unit_id INTEGER REFERENCES text_values(id),unit_key INTEGER NOT NULL,pattern_id INTEGER NOT NULL REFERENCES signal_pattern_sets(id),signed_view INTEGER NOT NULL CHECK(signed_view IN(0,1)));
CREATE TABLE IF NOT EXISTS signal_did_support(id INTEGER PRIMARY KEY,did INTEGER NOT NULL,fixed_length INTEGER NOT NULL,record INTEGER NOT NULL,encoding_id INTEGER NOT NULL REFERENCES text_values(id),support_mode INTEGER NOT NULL,table_type INTEGER NOT NULL,has_additional INTEGER NOT NULL,additional_count INTEGER NOT NULL);
CREATE TABLE IF NOT EXISTS signal_support_additional(parent_id INTEGER NOT NULL REFERENCES signal_did_support(id),position INTEGER NOT NULL,child_id INTEGER NOT NULL REFERENCES signal_did_support(id),PRIMARY KEY(parent_id,position)) WITHOUT ROWID;
CREATE TABLE IF NOT EXISTS signal_conditions(id INTEGER PRIMARY KEY,bit_end INTEGER NOT NULL,bit_start INTEGER NOT NULL,comparison_mode INTEGER NOT NULL,comparison_value INTEGER NOT NULL,condition_type INTEGER NOT NULL,condition_key INTEGER NOT NULL,record INTEGER NOT NULL,referenced_did INTEGER NOT NULL,table_type INTEGER NOT NULL,variable_bytes BLOB NOT NULL,variable_id INTEGER NOT NULL,condition_view INTEGER NOT NULL CHECK(condition_view IN(0,1,2)));
CREATE TABLE IF NOT EXISTS signal_monitors(id INTEGER PRIMARY KEY,label_id INTEGER NOT NULL REFERENCES signal_labels(id),alternate_did INTEGER NOT NULL,info_id INTEGER NOT NULL REFERENCES signal_infos(id),support_id INTEGER REFERENCES signal_did_support(id),condition_id INTEGER REFERENCES signal_conditions(id),extraction_mode INTEGER NOT NULL,flags INTEGER NOT NULL,graph_low INTEGER NOT NULL,graph_high INTEGER NOT NULL,list_member INTEGER NOT NULL,pattern_display_key INTEGER NOT NULL,physical_data_key INTEGER NOT NULL,physical_low REAL NOT NULL,physical_high REAL NOT NULL,primary_did INTEGER NOT NULL,record INTEGER NOT NULL,sort_key INTEGER NOT NULL,source_id INTEGER NOT NULL REFERENCES text_values(id),table_type INTEGER NOT NULL,visibility_override INTEGER NOT NULL);
CREATE TABLE IF NOT EXISTS signal_definitions(id INTEGER PRIMARY KEY,generation INTEGER NOT NULL CHECK(generation IN(5,6)),label_id INTEGER REFERENCES signal_labels(id),alternate_did INTEGER,decimal_point_count INTEGER,decoder_id INTEGER NOT NULL REFERENCES text_values(id),div INTEGER,mul INTEGER,offset INTEGER,unit_id INTEGER REFERENCES text_values(id),graph_low INTEGER,graph_high INTEGER,data_low INTEGER,data_high INTEGER,pattern_id INTEGER REFERENCES signal_pattern_sets(id),signed INTEGER,monitor_id INTEGER REFERENCES signal_monitors(id));
CREATE TABLE IF NOT EXISTS data_list_rows(id INTEGER PRIMARY KEY,generation INTEGER NOT NULL CHECK(generation IN(5,6)),label_id INTEGER REFERENCES signal_labels(id),sort_key INTEGER,monitor_id INTEGER REFERENCES signal_monitors(id),did_id INTEGER NOT NULL REFERENCES text_values(id),wire_field INTEGER);
"""
LABEL = ("monitor_key", "name", "bit_start", "bit_end")
P5 = frozenset(
    (
        "alternate_did",
        "bit_end",
        "bit_start",
        "data_range",
        "decimal_point_count",
        "decoder",
        "div",
        "graph_range",
        "monitor_key",
        "mul",
        "name",
        "offset",
        "patterns",
        "signed",
        "unit",
    )
)
INFO = (
    "bit_width",
    "decimal_point_count",
    "div",
    "mul",
    "offset",
    "physical_data_key",
    "sign_mode",
    "unit",
    "unit_key",
    "pattern_display",
)
LEGACY_INFO = frozenset(INFO) - {"sign_mode"} | {"signed"}
CORE = frozenset(
    (
        "alternate_did",
        "bit_end",
        "bit_start",
        "did_support",
        "extraction_mode",
        "flags",
        "graph_range",
        "list_member",
        "monitor_key",
        "name",
        "pattern_display_key",
        "physical_data_key",
        "physical_range",
        "primary_did",
        "record",
        "signal_info",
        "sort_key",
        "source",
        "support_condition",
        "table",
        "visibility_override",
    )
)
P6 = CORE | frozenset(
    (
        "decoder",
        "bit_width",
        "decimal_point_count",
        "div",
        "mul",
        "offset",
        "pattern_display",
        "sign_mode",
        "unit",
        "unit_key",
    )
)
D5 = frozenset((*LABEL, "did", "sort_key"))
D6 = CORE | frozenset(("did", "wire_field", "composite_records"))
SUPPORT = (
    "did",
    "fixed_length",
    "record",
    "snapshot_length_encoding",
    "support_mode",
    "table",
)
CONDITION = (
    "bit_end",
    "bit_start",
    "comparison_mode",
    "comparison_value",
    "condition_type",
    "key",
    "record",
    "referenced_did",
    "table",
    "variable_bytes",
    "variable_id",
)
SHORT_CONDITION = frozenset(CONDITION) - {"comparison_mode", "comparison_value"}
COMPACT_CONDITION = frozenset(
    ("bit_end", "bit_start", "condition_type", "key", "referenced_did", "variable_id")
)


def integer(v):
    if type(v) is not int or not -(1 << 63) <= v < (1 << 63):
        raise ValueError("unsupported signal integer")
    return v


def boolean(v):
    if type(v) is not bool:
        raise ValueError("unsupported signal boolean")
    return int(v)


def int_range(v):
    if type(v) is not list or len(v) != 2:
        raise ValueError("unsupported signal range")
    return tuple(integer(x) for x in v)


def real_range(v):
    if (
        type(v) is not list
        or len(v) != 2
        or any(type(x) is not float or not math.isfinite(x) for x in v)
    ):
        raise ValueError("unsupported physical range")
    if any(x == 0 and math.copysign(1, x) < 0 for x in v):
        raise ValueError("negative zero requires inline preservation")
    return tuple(v)


class Writer:
    def __init__(self, db):
        self.db = db
        self.cache = {}
        self.text = dict(db.execute("SELECT value,id FROM text_values"))
        self.next_ids = {}
        for table in (
            "signal_labels",
            "signal_infos",
            "signal_conditions",
            "signal_monitors",
            "signal_definitions",
            "data_list_rows",
        ):
            rows = db.execute(f"SELECT * FROM {table}").fetchall()
            self.cache[table] = {tuple(row[1:]): row[0] for row in rows}
            self.next_ids[table] = max((row[0] for row in rows), default=0) + 1
        patterns = self.cache.setdefault("signal_pattern_sets", {})
        for identity, expected in db.execute(
            "SELECT id,entry_count FROM signal_pattern_sets"
        ):
            key = tuple(
                db.execute(
                    """SELECT k.value,v.value FROM signal_pattern_entries p
                JOIN text_values k ON k.id=p.key_id LEFT JOIN text_values v ON v.id=p.value_id
                WHERE p.set_id=? ORDER BY k.value""",
                    (identity,),
                )
            )
            if len(key) != expected:
                raise ValueError("missing signal pattern entries")
            patterns[key] = identity
        self.next_ids["signal_pattern_sets"] = max(patterns.values(), default=0) + 1
        supports = self.cache.setdefault("support_objects", {})
        for row in db.execute("SELECT * FROM signal_did_support"):
            children = tuple(
                v[0]
                for v in db.execute(
                    "SELECT child_id FROM signal_support_additional WHERE parent_id=? ORDER BY position",
                    (row[0],),
                )
            )
            if len(children) != row[-1]:
                raise ValueError("missing additional DID support")
            supports[tuple(row[1:-1]) + (children,)] = row[0]
        self.next_ids["support_objects"] = max(supports.values(), default=0) + 1

    def string(self, value, nullable=False):
        if value is None and nullable:
            return None
        if type(value) is not str:
            raise ValueError("unsupported signal string")
        if value not in self.text:
            self.db.execute(
                "INSERT OR IGNORE INTO text_values(value) VALUES (?)", (value,)
            )
            self.text[value] = self.db.execute(
                "SELECT id FROM text_values WHERE value=?", (value,)
            ).fetchone()[0]
        return self.text[value]

    def row(self, table, values):
        cache = self.cache.setdefault(table, {})
        if values not in cache:
            identity = self.next_ids.get(table, 1)
            self.next_ids[table] = identity + 1
            self.db.execute(
                f"INSERT INTO {table} VALUES ({','.join('?' for _ in range(len(values) + 1))})",
                (identity, *values),
            )
            cache[values] = identity
        return cache[values]

    def label(self, value):
        return self.row(
            "signal_labels",
            (
                integer(value["monitor_key"]),
                self.string(value["name"]),
                integer(value["bit_start"]),
                integer(value["bit_end"]),
            ),
        )

    def patterns(self, value):
        if type(value) is not dict or any(
            type(k) is not str or (v is not None and type(v) is not str)
            for k, v in value.items()
        ):
            raise ValueError("unsupported pattern set")
        key = tuple(sorted(value.items()))
        cache = self.cache.setdefault("signal_pattern_sets", {})
        if key not in cache:
            identity = self.next_ids["signal_pattern_sets"]
            self.next_ids["signal_pattern_sets"] = identity + 1
            cache[key] = identity
            self.db.execute(
                "INSERT INTO signal_pattern_sets VALUES (?,?)", (identity, len(key))
            )
            self.db.executemany(
                "INSERT INTO signal_pattern_entries VALUES (?,?,?)",
                ((identity, self.string(k), self.string(v, True)) for k, v in key),
            )
        return cache[key]

    def info(self, value):
        if type(value) is not dict or set(value) not in (set(INFO), LEGACY_INFO):
            raise ValueError("unsupported signal info")
        legacy = set(value) == LEGACY_INFO
        sign = boolean(value["signed"]) if legacy else integer(value["sign_mode"])
        return self.row(
            "signal_infos",
            tuple(integer(value[k]) for k in INFO[:6])
            + (
                sign,
                self.string(value["unit"], True),
                integer(value["unit_key"]),
                self.patterns(value["pattern_display"]),
                int(legacy),
            ),
        )

    def support(self, value):
        if value is None:
            return None
        if type(value) is not dict or set(value) not in (
            set(SUPPORT),
            set(SUPPORT) | {"additional_records"},
        ):
            raise ValueError("unsupported DID support")
        additional = value.get("additional_records", [])
        if type(additional) is not list:
            raise ValueError("unsupported additional support")
        children = tuple(self.support(v) for v in additional)
        if any(x is None for x in children):
            raise ValueError("null additional support")
        key = (
            integer(value["did"]),
            integer(value["fixed_length"]),
            integer(value["record"]),
            self.string(value["snapshot_length_encoding"]),
            integer(value["support_mode"]),
            integer(value["table"]),
            int("additional_records" in value),
            children,
        )
        cache = self.cache.setdefault("support_objects", {})
        if key not in cache:
            identity = self.next_ids["support_objects"]
            cache[key] = identity
            self.next_ids["support_objects"] = identity + 1
            self.db.execute(
                "INSERT INTO signal_did_support VALUES (?,?,?,?,?,?,?,?,?)",
                (identity, *key[:-1], len(children)),
            )
            self.db.executemany(
                "INSERT INTO signal_support_additional VALUES (?,?,?)",
                ((identity, i, child) for i, child in enumerate(children)),
            )
        return cache[key]

    def condition(self, value):
        if value is None:
            return None
        if type(value) is not dict or set(value) not in (
            set(CONDITION),
            SHORT_CONDITION,
            COMPACT_CONDITION,
        ):
            raise ValueError("unsupported support condition")
        raw = value.get("variable_bytes", "")
        if type(raw) is not str:
            raise ValueError("unsupported variable bytes")
        data = bytes.fromhex(raw)
        if data.hex() != raw:
            raise ValueError("noncanonical variable bytes")
        return self.row(
            "signal_conditions",
            tuple(integer(value.get(k, 0)) for k in CONDITION[:9])
            + (
                data,
                integer(value["variable_id"]),
                (
                    0
                    if set(value) == set(CONDITION)
                    else 1
                    if set(value) == SHORT_CONDITION
                    else 2
                ),
            ),
        )

    def monitor(self, value):
        return self.row(
            "signal_monitors",
            (
                self.label(value),
                integer(value["alternate_did"]),
                self.info(value["signal_info"]),
                self.support(value["did_support"]),
                self.condition(value["support_condition"]),
                integer(value["extraction_mode"]),
                integer(value["flags"]),
                *int_range(value["graph_range"]),
                boolean(value["list_member"]),
                integer(value["pattern_display_key"]),
                integer(value["physical_data_key"]),
                *real_range(value["physical_range"]),
                integer(value["primary_did"]),
                integer(value["record"]),
                integer(value["sort_key"]),
                self.string(value["source"]),
                integer(value["table"]),
                integer(value["visibility_override"]),
            ),
        )

    def definition(self, value):
        if set(value) == P5:
            values = (
                5,
                self.label(value),
                integer(value["alternate_did"]),
                integer(value["decimal_point_count"]),
                self.string(value["decoder"]),
                integer(value["div"]),
                integer(value["mul"]),
                integer(value["offset"]),
                self.string(value["unit"], True),
                *int_range(value["graph_range"]),
                *int_range(value["data_range"]),
                self.patterns(value["patterns"]),
                boolean(value["signed"]),
                None,
            )
        elif set(value) == P6:
            info = value["signal_info"]
            if any(
                type(value[k]) is not type(info[k]) or value[k] != info[k]
                for k in INFO
                if k != "physical_data_key"
            ):
                raise ValueError("signal projection differs from info")
            values = (
                6,
                None,
                None,
                None,
                self.string(value["decoder"]),
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                self.monitor(value),
            )
        else:
            raise ValueError("unsupported definition shape")
        return {"$signal_definition": self.row("signal_definitions", values)}

    def display(self, value):
        if set(value) == D5:
            values = (
                5,
                self.label(value),
                integer(value["sort_key"]),
                None,
                self.string(value["did"]),
                None,
            )
        elif set(value) == D6:
            if (
                value["composite_records"] != []
                or type(value["composite_records"]) is not list
            ):
                raise ValueError("nonempty composite records")
            values = (
                6,
                None,
                None,
                self.monitor(value),
                self.string(value["did"]),
                boolean(value["wire_field"]),
            )
        else:
            raise ValueError("unsupported display shape")
        return {"$data_list_row": self.row("data_list_rows", values)}

    def transform(self, value):
        if isinstance(value, list):
            return [self.transform(x) for x in value]
        if not isinstance(value, dict):
            return value
        if set(value) in (P5, P6, D5, D6):
            definition = set(value) in (P5, P6)
            try:
                validator = Validator()
                validator.definition(value) if definition else validator.display(value)
            except (ValueError, KeyError, TypeError):
                # Validate before interning anything: unsupported future values
                # remain inline without leaving orphan typed entities.
                return value
            else:
                return self.definition(value) if definition else self.display(value)
        domain = None
        if set(value) in (set(INFO), LEGACY_INFO):
            domain = ("info", "$signal_info")
        elif set(value) in (set(SUPPORT), set(SUPPORT) | {"additional_records"}):
            domain = ("support", "$did_support")
        elif set(value) in (set(CONDITION), SHORT_CONDITION, COMPACT_CONDITION):
            domain = ("condition", "$support_condition")
        if domain is not None:
            method, marker = domain
            try:
                getattr(Validator(), method)(value)
            except (ValueError, KeyError, TypeError):
                return value
            return {marker: getattr(self, method)(value)}
        return {k: self.transform(v) for k, v in value.items()}


class Validator(Writer):
    def __init__(self):
        pass

    def string(self, value, nullable=False):
        if value is None and nullable:
            return None
        if type(value) is not str:
            raise ValueError("unsupported signal string")
        return 0

    def row(self, table, values):
        return 0

    def patterns(self, value):
        if type(value) is not dict or any(
            type(k) is not str or (v is not None and type(v) is not str)
            for k, v in value.items()
        ):
            raise ValueError("unsupported pattern set")
        return 0

    def support(self, value):
        if value is None:
            return None
        if type(value) is not dict or set(value) not in (
            set(SUPPORT),
            set(SUPPORT) | {"additional_records"},
        ):
            raise ValueError("unsupported DID support")
        for key in SUPPORT:
            self.string(value[key]) if key == "snapshot_length_encoding" else integer(
                value[key]
            )
        additional = value.get("additional_records", [])
        if type(additional) is not list:
            raise ValueError("unsupported additional support")
        for child in additional:
            if child is None:
                raise ValueError("null additional support")
            self.support(child)
        return 0


def normalize(db):
    db.executescript(SCHEMA)
    writer = Writer(db)
    for table, keys in (
        ("source_documents", ("id",)),
        ("source_document_parts", ("document_id", "pointer_id")),
    ):
        for row in db.execute(f"SELECT {','.join(keys)},data FROM {table}"):
            raw = decompress(row[-1])
            value = json.loads(raw)
            changed = writer.transform(value)
            if changed != value:
                packed = compress(
                    json.dumps(
                        changed,
                        ensure_ascii=False,
                        sort_keys=True,
                        separators=(",", ":"),
                    ).encode()
                )
                db.execute(
                    f"UPDATE {table} SET data=? WHERE {' AND '.join(k + '=?' for k in keys)}",
                    (packed, *row[:-1]),
                )
    return {
        table: db.execute(f"SELECT count(*) FROM {table}").fetchone()[0]
        for table in (
            "signal_definitions",
            "data_list_rows",
            "signal_monitors",
            "signal_infos",
        )
    }


class Reader:
    def __init__(self, db):
        self.db = db
        self.cache = {}
        self.active = set()

    def one(self, table, identity):
        row = self.db.execute(
            f"SELECT * FROM {table} WHERE id=?", (identity,)
        ).fetchone()
        if row is None:
            raise ValueError(f"missing {table} record {identity}")
        return row[1:]

    def text(self, identity):
        if identity is None:
            return None
        return self.one("text_values", identity)[0]

    def label(self, identity):
        key, name, start, end = self.one("signal_labels", identity)
        return dict(monitor_key=key, name=self.text(name), bit_start=start, bit_end=end)

    def patterns(self, identity):
        expected = self.one("signal_pattern_sets", identity)[0]
        out = {}
        for key, value_id, value in self.db.execute(
            """
            SELECT k.value,p.value_id,v.value FROM signal_pattern_entries p
            LEFT JOIN text_values k ON k.id=p.key_id LEFT JOIN text_values v ON v.id=p.value_id
            WHERE p.set_id=? ORDER BY k.value""",
            (identity,),
        ):
            if type(key) is not str or (
                value_id is not None and type(value) is not str
            ):
                raise ValueError("missing signal pattern text")
            out[key] = value
        if len(out) != expected:
            raise ValueError("missing signal pattern entries")
        return out

    def info(self, identity):
        row = self.one("signal_infos", identity)
        out = dict(zip(INFO[:7], row[:7]))
        if row[10] not in (0, 1):
            raise ValueError("invalid signal-info representation")
        if row[10]:
            if row[6] not in (0, 1):
                raise ValueError("invalid legacy signal signed flag")
            out["signed"] = bool(out.pop("sign_mode"))
        out.update(
            unit=self.text(row[7]),
            unit_key=row[8],
            pattern_display=self.patterns(row[9]),
        )
        return out

    def support(self, identity):
        if identity is None:
            return None
        if identity in self.active:
            raise ValueError("cyclic DID support")
        row = self.one("signal_did_support", identity)
        out = dict(zip(SUPPORT, row[:6]))
        out["snapshot_length_encoding"] = self.text(row[3])
        children = self.db.execute(
            "SELECT position,child_id FROM signal_support_additional WHERE parent_id=? ORDER BY position",
            (identity,),
        ).fetchall()
        if len(children) != row[7]:
            raise ValueError("missing additional DID support")
        if not row[6] and children:
            raise ValueError("unexpected additional DID support")
        if row[6]:
            self.active.add(identity)
            try:
                out["additional_records"] = []
                for expected, (position, child) in enumerate(children):
                    if position != expected:
                        raise ValueError("noncontiguous additional DID support")
                    out["additional_records"].append(self.support(child))
            finally:
                self.active.remove(identity)
        return out

    def condition(self, identity):
        if identity is None:
            return None
        row = self.one("signal_conditions", identity)
        out = dict(zip(CONDITION, row))
        out["variable_bytes"] = row[9].hex()
        if row[11] not in (0, 1, 2):
            raise ValueError("invalid support-condition representation")
        if row[11] != 0:
            del out["comparison_mode"], out["comparison_value"]
        if row[11] == 2:
            del out["record"], out["table"], out["variable_bytes"]
        return out

    def monitor(self, identity):
        row = self.one("signal_monitors", identity)
        out = self.label(row[0])
        out.update(
            alternate_did=row[1],
            signal_info=self.info(row[2]),
            did_support=self.support(row[3]),
            support_condition=self.condition(row[4]),
            extraction_mode=row[5],
            flags=row[6],
            graph_range=[row[7], row[8]],
            list_member=bool(row[9]),
            pattern_display_key=row[10],
            physical_data_key=row[11],
            physical_range=[row[12], row[13]],
            primary_did=row[14],
            record=row[15],
            sort_key=row[16],
            source=self.text(row[17]),
            table=row[18],
            visibility_override=row[19],
        )
        return out

    def definition(self, identity):
        row = self.one("signal_definitions", identity)
        generation = row[0]
        if generation == 5:
            out = self.label(row[1])
            out.update(
                alternate_did=row[2],
                decimal_point_count=row[3],
                decoder=self.text(row[4]),
                div=row[5],
                mul=row[6],
                offset=row[7],
                unit=self.text(row[8]),
                graph_range=[row[9], row[10]],
                data_range=[row[11], row[12]],
                patterns=self.patterns(row[13]),
                signed=bool(row[14]),
            )
            return out
        if generation == 6:
            out = self.monitor(row[15])
            info = out["signal_info"]
            out.update({k: info[k] for k in INFO if k != "physical_data_key"})
            out["decoder"] = self.text(row[4])
            return out
        raise ValueError("unsupported signal definition generation")

    def display(self, identity):
        row = self.one("data_list_rows", identity)
        if row[0] == 5:
            out = self.label(row[1])
            out.update(sort_key=row[2], did=self.text(row[4]))
            return out
        if row[0] == 6:
            out = self.monitor(row[3])
            out.update(
                did=self.text(row[4]), wire_field=bool(row[5]), composite_records=[]
            )
            return out
        raise ValueError("unsupported data-list generation")


def restore_definition(db, identity):
    return Reader(db).definition(identity)


def restore_display(db, identity):
    return Reader(db).display(identity)


def restore_info(db, identity):
    return Reader(db).info(identity)


def restore_support(db, identity):
    return Reader(db).support(identity)


def restore_condition(db, identity):
    return Reader(db).condition(identity)
