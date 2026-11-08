"""Semantic support catalogs: query rules and ordered signal memberships.

Groups reference the already-canonical membership facts. The two legacy output
arrays are views of those links, not independently stored copies.
"""

from __future__ import annotations

FIELDS = {
    "member": (
        "identifier",
        "list_key",
        "exception_handler_flag",
        "exception_handler_id",
    ),
    "query": ("query_id", "policy", "exception_handler_flag", "exception_handler_id"),
    "freeze": ("freeze_frame_number", "exception_handler_flag", "exception_handler_id"),
    "group": (
        "group_id",
        "list_key",
        "member_table",
        "name_string_index",
        "exception_handler_flag",
        "exception_handler_id",
    ),
}
MARKERS = {
    "$support_member_facts": "member",
    "$support_query_facts": "query",
    "$freeze_query_facts": "freeze",
    "$support_group_facts": "group",
}
TABLES = {kind: "support_" + kind + "_facts" for kind in FIELDS}


def ddl():
    p = [
        "CREATE TABLE IF NOT EXISTS text_values(id INTEGER PRIMARY KEY,value TEXT NOT NULL UNIQUE);",
        "CREATE TABLE freeze_query_policies(id INTEGER PRIMARY KEY,length3_offset INTEGER NOT NULL,length4_offset INTEGER NOT NULL);",
    ]
    for kind, fields in FIELDS.items():
        cols = ["id INTEGER PRIMARY KEY"] + [f + " INTEGER NOT NULL" for f in fields]
        if kind == "query":
            cols += [
                "kind_id INTEGER NOT NULL REFERENCES text_values(id)",
                "requires_previous INTEGER NOT NULL CHECK(requires_previous IN(0,1))",
            ]
        if kind == "freeze":
            cols += ["policy_id INTEGER NOT NULL REFERENCES freeze_query_policies(id)"]
        if kind == "group":
            cols += [
                "name_id INTEGER NOT NULL REFERENCES text_values(id)",
                "member_count INTEGER NOT NULL CHECK(member_count>=0)",
            ]
        p.append("CREATE TABLE " + TABLES[kind] + "(" + ",".join(cols) + ");")
        p.append(
            "CREATE TABLE support_"
            + kind
            + "_origins(id INTEGER PRIMARY KEY,definition_id INTEGER NOT NULL REFERENCES "
            + TABLES[kind]
            + "(id),source_id INTEGER NOT NULL REFERENCES text_values(id),table_number INTEGER NOT NULL,record_number INTEGER NOT NULL);"
        )
    p.append(
        "CREATE TABLE support_group_links(definition_id INTEGER NOT NULL REFERENCES support_group_facts(id),position INTEGER NOT NULL,member_id INTEGER NOT NULL REFERENCES support_member_origins(id),PRIMARY KEY(definition_id,position)) WITHOUT ROWID;"
    )
    return "\n".join(p)


DDL = ddl()
ORIGIN = {"source", "table", "record"}
EXTRA = {
    "member": set(),
    "query": {"kind", "requires_previously_supported_query_id_in_p4"},
    "freeze": {"request_variable_byte_by_frame_length"},
    "group": {"name", "member_records", "members"},
}


def integer(v):
    if type(v) is not int or not -(1 << 63) <= v < (1 << 63):
        raise ValueError("invalid support integer")
    return v


def validate(kind, row):
    if (
        not isinstance(row, dict)
        or set(row) != set(FIELDS[kind]) | ORIGIN | EXTRA[kind]
    ):
        raise ValueError("unknown support shape")
    for k in FIELDS[kind] + ("table", "record"):
        integer(row[k])
    if not isinstance(row["source"], str):
        raise ValueError("invalid support source")
    if kind == "query":
        if (
            not isinstance(row["kind"], str)
            or type(row["requires_previously_supported_query_id_in_p4"]) is not bool
        ):
            raise ValueError("invalid support query")
    if kind == "freeze":
        p = row["request_variable_byte_by_frame_length"]
        if not isinstance(p, dict) or set(p) != {"3", "4"}:
            raise ValueError("unknown freeze query policy")
        integer(p["3"])
        integer(p["4"])
    if kind == "group":
        if not isinstance(row["name"], str):
            raise ValueError("invalid group name")
        for k in ("member_records", "members"):
            if not isinstance(row[k], list):
                raise ValueError("invalid group members")
            for v in row[k]:
                integer(v)
        if len(row["member_records"]) != len(row["members"]):
            raise ValueError("inconsistent group members")


class SupportStore:
    def __init__(self, db):
        self.db = db
        db.executescript(DDL)
        self.memo = {}
        self.texts = {v: i for i, v in db.execute("SELECT id,value FROM text_values")}

    def text(self, v):
        if v not in self.texts:
            self.db.execute("INSERT OR IGNORE INTO text_values(value) VALUES(?)", (v,))
            self.texts[v] = self.db.execute(
                "SELECT id FROM text_values WHERE value=?", (v,)
            ).fetchone()[0]
        return self.texts[v]

    def intern(self, table, values, extra=()):
        key = (table, values, extra)
        if key not in self.memo:
            self.memo[key] = self.db.execute(
                "INSERT INTO "
                + table
                + " VALUES(NULL,"
                + ",".join("?" for _ in values)
                + ")",
                values,
            ).lastrowid
        return self.memo[key]

    def row(self, kind, row, links=()):
        values = tuple(row[f] for f in FIELDS[kind])
        if kind == "query":
            values += (
                self.text(row["kind"]),
                int(row["requires_previously_supported_query_id_in_p4"]),
            )
        if kind == "freeze":
            p = row["request_variable_byte_by_frame_length"]
            values += (self.intern("freeze_query_policies", (p["3"], p["4"])),)
        if kind == "group":
            values += (self.text(row["name"]), len(links))
        key = (TABLES[kind], values, links if kind == "group" else ())
        existed = key in self.memo
        definition = self.intern(TABLES[kind], values, links if kind == "group" else ())
        if kind == "group" and not existed:
            self.db.executemany(
                "INSERT INTO support_group_links VALUES(?,?,?)",
                [(definition, p, v) for p, v in enumerate(links)],
            )
        identity = self.intern(
            "support_" + kind + "_origins",
            (definition, self.text(row["source"]), row["table"], row["record"]),
        )
        marker = next(m for m, k in MARKERS.items() if k == kind)
        return {marker: identity}

    def normalize(self, value):
        if not isinstance(value, dict) or not isinstance(
            value.get("support_catalog"), dict
        ):
            return value
        original = value["support_catalog"]
        out = dict(original)
        lookup = {}
        source_rows = original.get("signal_memberships")
        if isinstance(source_rows, list):
            members = []
            for row in source_rows:
                try:
                    validate("member", row)
                except (ValueError, TypeError):
                    members.append(row)
                    continue
                marker = self.row("member", row)
                members.append(marker)
                key = (row["source"], row["table"], row["record"])
                lookup.setdefault(key, []).append(
                    (row, marker["$support_member_facts"])
                )
            out["signal_memberships"] = members
        for field, kind in (
            ("signal_groups", "group"),
            ("support_queries", "query"),
            ("freeze_frame_queries", "freeze"),
        ):
            if not isinstance(original.get(field), list):
                continue
            result = []
            for row in original[field]:
                try:
                    validate(kind, row)
                    links = []
                    if kind == "group":
                        for record, identifier in zip(
                            row["member_records"], row["members"]
                        ):
                            matches = lookup.get(
                                (row["source"], row["member_table"], record), []
                            )
                            if (
                                len(matches) != 1
                                or matches[0][0]["identifier"] != identifier
                                or matches[0][0]["list_key"] != row["list_key"]
                            ):
                                raise ValueError("unresolved group member")
                            links.append(matches[0][1])
                    result.append(self.row(kind, row, tuple(links)))
                except (ValueError, TypeError):
                    result.append(row)
            out[field] = result
        return dict(value, support_catalog=out)


def one(db, table, identity):
    row = db.execute("SELECT * FROM " + table + " WHERE id=?", (identity,)).fetchone()
    if row is None:
        raise ValueError("missing " + table)
    return row[1:]


def text(db, identity):
    return one(db, "text_values", identity)[0]


def restore(db, marker, identity):
    kind = MARKERS[marker]
    definition, source, table, record = one(
        db, "support_" + kind + "_origins", identity
    )
    values = one(db, TABLES[kind], definition)
    n = len(FIELDS[kind])
    out = dict(zip(FIELDS[kind], values[:n]))
    out.update(source=text(db, source), table=table, record=record)
    if kind == "query":
        name, required = values[n:]
        if required not in (0, 1):
            raise ValueError("invalid support flag")
        out.update(
            kind=text(db, name),
            requires_previously_supported_query_id_in_p4=bool(required),
        )
    if kind == "freeze":
        policy = one(db, "freeze_query_policies", values[n])
        out["request_variable_byte_by_frame_length"] = dict(zip(("3", "4"), policy))
    if kind == "group":
        name, count = values[n:]
        rows = db.execute(
            "SELECT position,member_id FROM support_group_links WHERE definition_id=? ORDER BY position",
            (definition,),
        ).fetchall()
        if (
            count < 0
            or len(rows) != count
            or [r[0] for r in rows] != list(range(count))
        ):
            raise ValueError("incomplete support group")
        members = []
        records = []
        for _, identity in rows:
            member = restore(db, "$support_member_facts", identity)
            if (
                member["source"] != out["source"]
                or member["table"] != out["member_table"]
                or member["list_key"] != out["list_key"]
            ):
                raise ValueError("inconsistent support group origin")
            members.append(member["identifier"])
            records.append(member["record"])
        out.update(name=text(db, name), members=members, member_records=records)
    return out
