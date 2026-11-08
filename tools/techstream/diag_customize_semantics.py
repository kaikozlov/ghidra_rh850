"""Customize items, ordered choice sets and executable semantic profiles."""

import json

from tools.techstream.diag_codec import compress, decompress

ITEM = (
    "all_default_gate_u16_22",
    "choice_list_key",
    "current_bit_end",
    "current_bit_start",
    "current_data_mode",
    "group_id",
    "item_aux_u16_0e",
    "item_id",
    "legacy_data_id",
    "merge_mode",
    "metadata_dword_04",
    "name",
    "name_string_index",
    "raw_u16_1e",
    "raw_u16_28",
    "raw_u32_24",
    "raw_u8_33",
    "read_current",
    "source_ordinal",
    "support_bit_end",
    "support_bit_start",
    "support_mode",
    "support_selector",
    "target_category_id",
    "target_category_name",
    "target_generation",
    "target_resolution",
    "target_route_selector",
    "write_bit_end",
    "write_bit_start",
    "write_did",
    "write_variant",
)
CHOICE = (
    "exception_flag",
    "exception_id",
    "name",
    "name_string_index",
    "source_ordinal",
    "value",
)
GROUP = (
    "body_type",
    "exception_flag",
    "exception_id",
    "group_id",
    "name",
    "name_string_index",
    "source_ordinal",
)
EXECUTOR = (
    "family",
    "merge",
    "read_current",
    "session_requirement",
    "support_gate",
    "verify",
    "write",
)
TEXT = frozenset(("name", "target_category_name", "target_resolution"))


def columns(fields, texts=TEXT):
    return ",".join(
        k + "_id INTEGER REFERENCES text_values(id)"
        if k in texts
        else k + " INTEGER NOT NULL"
        for k in fields
    )


SCHEMA = (
    """
CREATE TABLE customize_choice_definitions(id INTEGER PRIMARY KEY,"""
    + columns(CHOICE)
    + """);
CREATE TABLE customize_choice_lists(id INTEGER PRIMARY KEY,entry_count INTEGER NOT NULL CHECK(entry_count>=0));
CREATE TABLE customize_choice_members(list_id INTEGER NOT NULL REFERENCES customize_choice_lists(id),position INTEGER NOT NULL,choice_id INTEGER NOT NULL REFERENCES customize_choice_definitions(id),PRIMARY KEY(list_id,position)) WITHOUT ROWID;
CREATE TABLE customize_executor_profiles(id INTEGER PRIMARY KEY,"""
    + columns(EXECUTOR, frozenset(EXECUTOR))
    + """);
CREATE TABLE customize_group_definitions(id INTEGER PRIMARY KEY,"""
    + columns(GROUP)
    + """);
CREATE TABLE customize_item_definitions(id INTEGER PRIMARY KEY,"""
    + columns(ITEM)
    + """,choice_list_id INTEGER NOT NULL REFERENCES customize_choice_lists(id),executor_id INTEGER REFERENCES customize_executor_profiles(id));
"""
)


def integer(v):
    if type(v) is not int or not -(1 << 63) <= v < (1 << 63):
        raise ValueError("unsupported customize integer")
    return v


class Writer:
    def __init__(self, db):
        self.db = db
        self.cache = {}
        self.text = {}

    def text_id(self, v):
        if v is None:
            return None
        if type(v) is not str:
            raise ValueError("unsupported customize label")
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

    def values(self, row, fields, texts=TEXT):
        if type(row) is not dict or set(row) != set(fields):
            raise ValueError("unsupported customize shape")
        return tuple(
            self.text_id(row[k]) if k in texts else integer(row[k]) for k in fields
        )

    def choices(self, rows):
        if type(rows) is not list:
            raise ValueError("unsupported customize choices")
        ids = tuple(
            self.row("customize_choice_definitions", self.values(row, CHOICE))
            for row in rows
        )
        cache = self.cache.setdefault("lists", {})
        if ids not in cache:
            id = self.db.execute(
                "INSERT INTO customize_choice_lists(entry_count) VALUES(?)", (len(ids),)
            ).lastrowid
            self.db.executemany(
                "INSERT INTO customize_choice_members VALUES(?,?,?)",
                [(id, i, v) for i, v in enumerate(ids)],
            )
            cache[ids] = id
        return cache[ids]

    def item(self, row):
        if type(row) is not dict or set(row) not in (
            set(ITEM) | {"choices"},
            set(ITEM) | {"choices", "modern_executor"},
        ):
            raise ValueError("unsupported customize item")
        values = self.values({k: row[k] for k in ITEM}, ITEM)
        executor = None
        if "modern_executor" in row:
            executor = self.row(
                "customize_executor_profiles",
                self.values(row["modern_executor"], EXECUTOR, frozenset(EXECUTOR)),
            )
        return self.row(
            "customize_item_definitions",
            values + (self.choices(row["choices"]), executor),
        )

    def transform(self, value):
        if type(value) is not dict:
            return value
        result = dict(value)
        for key, marker in (
            ("items", "$customize_item"),
            ("groups", "$customize_group"),
        ):
            if type(value.get(key)) is not list:
                continue
            rows = []
            for row in value[key]:
                try:
                    id = (
                        self.item(row)
                        if key == "items"
                        else self.row(
                            "customize_group_definitions", self.values(row, GROUP)
                        )
                    )
                    rows.append({marker: id})
                except (ValueError, TypeError, KeyError):
                    rows.append(row)
            result[key] = rows
        return result


class Reader:
    def __init__(self, db):
        self.db = db

    def fields(self, fields, values, texts=TEXT):
        out = {}
        for k, v in zip(fields, values):
            if k in texts:
                if v is None:
                    out[k] = None
                else:
                    text = self.db.execute(
                        "SELECT value FROM text_values WHERE id=?", (v,)
                    ).fetchone()
                    if text is None:
                        raise ValueError("missing customize text")
                    out[k] = text[0]
            else:
                out[k] = v
        return out

    def read(self, marker, id):
        if (
            marker not in ("$customize_item", "$customize_group")
            or type(id) is not int
            or id <= 0
        ):
            raise ValueError("invalid customize reference")
        table, fields = (
            ("customize_item_definitions", ITEM)
            if marker == "$customize_item"
            else ("customize_group_definitions", GROUP)
        )
        row = self.db.execute(
            "SELECT * FROM " + table + " WHERE id=?", (id,)
        ).fetchone()
        if row is None:
            raise ValueError("missing customize definition")
        out = self.fields(fields, row[1 : len(fields) + 1])
        if marker == "$customize_group":
            return out
        list_id, executor = row[-2:]
        count = self.db.execute(
            "SELECT entry_count FROM customize_choice_lists WHERE id=?", (list_id,)
        ).fetchone()
        if count is None:
            raise ValueError("missing customize choice list")
        choices = []
        for position, *values in self.db.execute(
            "SELECT m.position,c.exception_flag,c.exception_id,c.name_id,c.name_string_index,c.source_ordinal,c.value FROM customize_choice_members m JOIN customize_choice_definitions c ON c.id=m.choice_id WHERE m.list_id=? ORDER BY m.position",
            (list_id,),
        ):
            if position != len(choices):
                raise ValueError("invalid customize choice order")
            choices.append(self.fields(CHOICE, values))
        if len(choices) != count[0]:
            raise ValueError("incomplete customize choices")
        out["choices"] = choices
        if executor is not None:
            value = self.db.execute(
                "SELECT * FROM customize_executor_profiles WHERE id=?", (executor,)
            ).fetchone()
            if value is None:
                raise ValueError("missing customize executor")
            out["modern_executor"] = self.fields(
                EXECUTOR, value[1:], frozenset(EXECUTOR)
            )
        return out


def restore_customize(db, marker, id):
    return Reader(db).read(marker, id)


def normalize(db):
    db.executescript(SCHEMA)
    writer = Writer(db)
    changed = 0
    for id, packed in db.execute(
        "SELECT id,data FROM source_documents WHERE member LIKE 'customize/%'"
    ):
        value = json.loads(decompress(packed))
        result = writer.transform(value)
        if result == value:
            continue
        db.execute(
            "UPDATE source_documents SET data=? WHERE id=?",
            (
                compress(
                    json.dumps(
                        result,
                        ensure_ascii=False,
                        separators=(",", ":"),
                        sort_keys=True,
                    ).encode()
                ),
                id,
            ),
        )
        changed += 1
    return changed
