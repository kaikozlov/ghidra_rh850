"""Ordered diagnostic relationships over canonical signals, codes and display rows."""

from __future__ import annotations

import json
import sqlite3

from tools.techstream import diag_codec

GROUPS = {
    "$did_membership": (
        "did",
        "$signal_definition",
        "definition_id",
        "signal_definitions",
    ),
    "$dtc_membership": ("dtc", "$diagnostic_code", "entry_id", "dtc_entries"),
}
MARKERS = (*GROUPS, "$display_membership")
DDL = (
    "\n".join(
        f"""
CREATE TABLE IF NOT EXISTS {kind}_membership_sets(
 id INTEGER PRIMARY KEY,group_count INTEGER NOT NULL CHECK(group_count>=0));
CREATE TABLE IF NOT EXISTS {kind}_membership_groups(
 set_id INTEGER NOT NULL REFERENCES {kind}_membership_sets(id),
 position INTEGER NOT NULL CHECK(position>=0),key TEXT NOT NULL,
 member_count INTEGER NOT NULL CHECK(member_count>=0),
 PRIMARY KEY(set_id,position),UNIQUE(set_id,key)) WITHOUT ROWID;
CREATE TABLE IF NOT EXISTS {kind}_membership_rows(
 set_id INTEGER NOT NULL,group_position INTEGER NOT NULL,position INTEGER NOT NULL CHECK(position>=0),
 {column} INTEGER NOT NULL REFERENCES {target}(id),
 PRIMARY KEY(set_id,group_position,position),
 FOREIGN KEY(set_id,group_position) REFERENCES {kind}_membership_groups(set_id,position)) WITHOUT ROWID;
"""
        for kind, _, column, target in GROUPS.values()
    )
    + """
CREATE TABLE IF NOT EXISTS display_membership_sets(
 id INTEGER PRIMARY KEY,row_count INTEGER NOT NULL CHECK(row_count>=0));
CREATE TABLE IF NOT EXISTS display_membership_rows(
 set_id INTEGER NOT NULL REFERENCES display_membership_sets(id),
 position INTEGER NOT NULL CHECK(position>=0),
 row_id INTEGER NOT NULL REFERENCES data_list_rows(id),
 PRIMARY KEY(set_id,position)) WITHOUT ROWID;
"""
)


def encoded(value):
    # Dictionary order is an explicit group order, not an incidental hash key.
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"), allow_nan=False)


def references(value, marker):
    if type(value) is not list:
        return None
    ids = []
    for row in value:
        if type(row) is not dict or set(row) != {marker}:
            return None
        identity = row[marker]
        if type(identity) is not int or identity <= 0:
            raise ValueError(f"invalid diagnostic membership {marker}")
        ids.append(identity)
    return ids


class Store:
    def __init__(self, db: sqlite3.Connection):
        self.db = db
        db.executescript(DDL)
        self.cache = {marker: {} for marker in MARKERS}
        self.targets = {}
        for marker, (kind, _, _, target) in GROUPS.items():
            self.targets[marker] = {
                r[0] for r in db.execute(f"SELECT id FROM {target}")
            }
            for (identity,) in db.execute(f"SELECT id FROM {kind}_membership_sets"):
                self.cache[marker][encoded(restore(db, marker, identity))] = identity
        marker = "$display_membership"
        self.targets[marker] = {
            r[0] for r in db.execute("SELECT id FROM data_list_rows")
        }
        for (identity,) in db.execute("SELECT id FROM display_membership_sets"):
            self.cache[marker][encoded(restore(db, marker, identity))] = identity

    def grouped(self, marker, value):
        if type(value) is not dict:
            return value
        kind, reference, column, _ = GROUPS[marker]
        groups = []
        for key, rows in value.items():
            if type(key) is not str:
                return value
            ids = references(rows, reference)
            if ids is None:
                return value
            groups.append((key, ids))
        for _, ids in groups:
            if any(identity not in self.targets[marker] for identity in ids):
                raise ValueError(f"missing diagnostic target in {marker}")
        key = encoded(value)
        identity = self.cache[marker].get(key)
        if identity is None:
            identity = self.db.execute(
                f"INSERT INTO {kind}_membership_sets(group_count) VALUES(?)",
                (len(groups),),
            ).lastrowid
            for position, (name, ids) in enumerate(groups):
                self.db.execute(
                    f"INSERT INTO {kind}_membership_groups VALUES(?,?,?,?)",
                    (identity, position, name, len(ids)),
                )
                self.db.executemany(
                    f"INSERT INTO {kind}_membership_rows VALUES(?,?,?,?)",
                    ((identity, position, n, child) for n, child in enumerate(ids)),
                )
            self.cache[marker][key] = identity
        return {marker: identity}

    def display(self, value):
        marker = "$display_membership"
        ids = references(value, "$data_list_row")
        if ids is None:
            return value
        if any(identity not in self.targets[marker] for identity in ids):
            raise ValueError("missing diagnostic display target")
        key = encoded(value)
        identity = self.cache[marker].get(key)
        if identity is None:
            identity = self.db.execute(
                "INSERT INTO display_membership_sets(row_count) VALUES(?)", (len(ids),)
            ).lastrowid
            self.db.executemany(
                "INSERT INTO display_membership_rows VALUES(?,?,?)",
                ((identity, n, child) for n, child in enumerate(ids)),
            )
            self.cache[marker][key] = identity
        return {marker: identity}

    def normalize(self, document):
        if type(document) is not dict:
            return document
        result = dict(document)
        for field, marker in (("dids", "$did_membership"), ("dtcs", "$dtc_membership")):
            if field in document:
                result[field] = self.grouped(marker, document[field])
        display = document.get("data_list")
        if type(display) is dict and "rows" in display:
            result["data_list"] = {**display, "rows": self.display(display["rows"])}
        return result


def restore(db, marker, identity):
    if type(identity) is not int or identity <= 0:
        raise ValueError("invalid diagnostic membership identity")
    if marker == "$display_membership":
        count = db.execute(
            "SELECT row_count FROM display_membership_sets WHERE id=?", (identity,)
        ).fetchone()
        if count is None:
            raise ValueError("missing display membership")
        rows = db.execute(
            """SELECT m.position,m.row_id,d.id FROM display_membership_rows m
               LEFT JOIN data_list_rows d ON d.id=m.row_id WHERE m.set_id=? ORDER BY m.position""",
            (identity,),
        ).fetchall()
        if len(rows) != count[0] or any(
            row[0] != n or row[2] is None for n, row in enumerate(rows)
        ):
            raise ValueError("incomplete display membership")
        return [{"$data_list_row": row[1]} for row in rows]
    if marker not in GROUPS:
        raise ValueError("unknown diagnostic membership")
    kind, reference, column, target = GROUPS[marker]
    count = db.execute(
        f"SELECT group_count FROM {kind}_membership_sets WHERE id=?", (identity,)
    ).fetchone()
    if count is None:
        raise ValueError(f"missing {kind} membership")
    groups = db.execute(
        f"SELECT position,key,member_count FROM {kind}_membership_groups WHERE set_id=? ORDER BY position",
        (identity,),
    ).fetchall()
    if len(groups) != count[0] or any(row[0] != n for n, row in enumerate(groups)):
        raise ValueError(f"incomplete {kind} membership groups")
    members = db.execute(
        f"""SELECT m.group_position,m.position,m.{column},d.id FROM {kind}_membership_rows m
            LEFT JOIN {target} d ON d.id=m.{column}
            WHERE m.set_id=? ORDER BY m.group_position,m.position""",
        (identity,),
    ).fetchall()
    values = [[] for _ in groups]
    for group, position, child, found in members:
        if (
            group < 0
            or group >= len(groups)
            or position != len(values[group])
            or found is None
        ):
            raise ValueError(f"invalid {kind} membership row")
        values[group].append({reference: child})
    if any(len(values[n]) != row[2] for n, row in enumerate(groups)):
        raise ValueError(f"incomplete {kind} membership rows")
    return {row[1]: values[n] for n, row in enumerate(groups)}


def normalize(db):
    store = Store(db)
    for identity, packed in db.execute(
        "SELECT id,data FROM source_documents WHERE member LIKE 'catalogs/%'"
    ):
        value = json.loads(diag_codec.decompress(packed))
        result = store.normalize(value)
        if result != value:
            db.execute(
                "UPDATE source_documents SET data=? WHERE id=?",
                (diag_codec.compress(encoded(result).encode()), identity),
            )
