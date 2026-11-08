"""Decoded native recorder facts, not vendor-record reconstruction."""

from tools.techstream.diag_freeze_physical import integer

# Explicit domain fields and ordered relation tuple widths.
SPECS = {
    "addresses": (
        "address exception_flag exception_id monitor_key record_length section_kind trigger_id",
        "family record_class",
        "header_member",
        "",
        ("monitor_records", ("record", "table")),
    ),
    "invalid_conditions": (
        "combination_mode comparison_mode comparison_value condition_order exception_flag exception_id referenced_signal_key signal_key",
        "comparison family record_class",
        "",
        "",
        None,
    ),
    "monitors": (
        "bit_end bit_start data_max data_min exception_flag exception_id graph_max graph_min history_bit_end history_bit_start monitor_key name_string_index pattern_display_key physical_data_key presentation_mode sort_key",
        "family name record_class",
        "",
        "signal_info",
        ("invalid_condition_records", ("record", "table")),
    ),
    "triggers": (
        "dependent_data_0 dependent_data_1 exception_flag exception_id memo_string_index name_string_index trigger_id trigger_variant",
        "family memo name record_class",
        "",
        "",
        ("header_parameters", ()),
    ),
    "case_data_ids": (
        "case_did case_parameter case_selector exception_flag exception_id header_did",
        "family record_class",
        "",
        "",
        None,
    ),
    "header_data_ids": (
        "exception_flag exception_id header_did header_parameter",
        "family record_class",
        "",
        "",
        None,
    ),
}


UNINTERPRETED = {
    "addresses": ("13_15",),
    "invalid_conditions": ("15",),
    "monitors": ("8_11", "42_43", "46_47"),
    "triggers": ("33_35",),
    "case_data_ids": ("9", "11"),
    "header_data_ids": ("7",),
}


def ddl():
    out = []
    for kind, (ints, texts, bools, refs, relation) in SPECS.items():
        cols = (
            [k + " INTEGER NOT NULL" for k in (ints + " " + bools).split()]
            + [k + "_id INTEGER REFERENCES text_values(id)" for k in texts.split()]
            + [
                k + "_id INTEGER NOT NULL REFERENCES signal_infos(id)"
                for k in refs.split()
            ]
        )
        cols += [
            "uninterpreted_present INTEGER NOT NULL CHECK(uninterpreted_present IN(0,1))"
        ]
        cols += [
            "unknown_" + key + "_id INTEGER REFERENCES text_values(id)"
            for key in UNINTERPRETED[kind]
        ]
        if relation:
            cols += ["relation_count INTEGER NOT NULL CHECK(relation_count>=0)"]
        out.append(
            "CREATE TABLE IF NOT EXISTS native_recorder_"
            + kind
            + "_defs(id INTEGER PRIMARY KEY,"
            + ",".join(cols)
            + ");"
        )
        out.append(
            "CREATE TABLE IF NOT EXISTS native_recorder_"
            + kind
            + "_entries(id INTEGER PRIMARY KEY,definition_id INTEGER NOT NULL REFERENCES native_recorder_"
            + kind
            + "_defs(id),source_id INTEGER NOT NULL REFERENCES text_values(id),table_number INTEGER NOT NULL,record_number INTEGER NOT NULL);"
        )
        if relation:
            columns = relation[1] or ("value",)
            out.append(
                "CREATE TABLE IF NOT EXISTS native_recorder_"
                + kind
                + "_links(definition_id INTEGER NOT NULL REFERENCES native_recorder_"
                + kind
                + "_defs(id),position INTEGER NOT NULL,"
                + ",".join('"' + k + '" INTEGER NOT NULL' for k in columns)
                + ",PRIMARY KEY(definition_id,position)) WITHOUT ROWID;"
            )
    return "\n".join(out)


DDL = ddl()


class Store:
    def __init__(self, db):
        self.db = db
        db.executescript(DDL)
        self.texts = {}
        self.defs = {}
        self.entries = {}
        for kind, spec in SPECS.items():
            self.entries[kind] = {
                tuple(r[1:]): r[0]
                for r in db.execute(
                    "SELECT * FROM native_recorder_" + kind + "_entries"
                )
            }
            cache = self.defs[kind] = {}
            for r in db.execute("SELECT * FROM native_recorder_" + kind + "_defs"):
                links = (
                    tuple(
                        tuple(x[2:])
                        for x in db.execute(
                            "SELECT * FROM native_recorder_"
                            + kind
                            + "_links WHERE definition_id=? ORDER BY position",
                            (r[0],),
                        )
                    )
                    if spec[-1]
                    else ()
                )
                cache[tuple(r[1:]) + (links,)] = r[0]

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

    def validate(self, kind, row):
        ints, texts, bools, refs, relation = SPECS[kind]
        expected = set((ints + " " + texts + " " + bools + " " + refs).split()) | {
            "source",
            "record",
            "table",
        }
        if relation:
            expected.add(relation[0])
        if type(row) is dict and "uninterpreted_bytes" in row:
            expected.add("uninterpreted_bytes")
        if (
            type(row) is not dict
            or set(row) != expected
            or type(row["source"]) is not str
        ):
            return None
        try:
            nums = tuple(integer(row[k]) for k in ints.split())
            origin = (row["source"], integer(row["table"]), integer(row["record"]))
            if any(type(row[k]) is not bool for k in bools.split()):
                return None
            nums += tuple(int(row[k]) for k in bools.split())
            labels = tuple(row[k] for k in texts.split())
            if any(v is not None and type(v) is not str for v in labels):
                return None
            references = []
            for k in refs.split():
                v = row[k]
                if (
                    type(v) is not dict
                    or set(v) != {"$signal_info"}
                    or type(v["$signal_info"]) is not int
                    or v["$signal_info"] <= 0
                ):
                    return None
                references.append(integer(v["$signal_info"]))
            links = []
            if relation:
                values = row[relation[0]]
                if type(values) is not list:
                    return None
                for value in values:
                    if relation[1]:
                        if type(value) is not dict or set(value) != set(relation[1]):
                            return None
                        links.append(tuple(integer(value[k]) for k in relation[1]))
                    else:
                        links.append((integer(value),))
            unknown = row.get("uninterpreted_bytes")
            if "uninterpreted_bytes" in row:
                if (
                    type(unknown) is not dict
                    or set(unknown) != set(UNINTERPRETED[kind])
                    or any(type(v) is not str for v in unknown.values())
                ):
                    return None
            return nums, labels, tuple(references), tuple(links), origin, unknown
        except (ValueError, TypeError):
            return None

    def row(self, kind, row):
        valid = self.validate(kind, row)
        if valid is None:
            return row
        nums, labels, refs, links, origin, unknown = valid
        values = nums + tuple(self.text(v) for v in labels) + refs
        values += (int(unknown is not None),) + tuple(
            self.text(unknown[key]) if unknown is not None else None
            for key in UNINTERPRETED[kind]
        )
        if SPECS[kind][-1]:
            values += (len(links),)
        key = values + (links,)
        cache = self.defs[kind]
        if key not in cache:
            ident = self.db.execute(
                "INSERT INTO native_recorder_"
                + kind
                + "_defs VALUES("
                + ",".join("?" for _ in range(len(values) + 1))
                + ")",
                (None, *values),
            ).lastrowid
            if SPECS[kind][-1]:
                self.db.executemany(
                    "INSERT INTO native_recorder_"
                    + kind
                    + "_links VALUES("
                    + ",".join(
                        "?" for _ in range(2 + len(SPECS[kind][-1][1] or ("value",)))
                    )
                    + ")",
                    [(ident, i, *v) for i, v in enumerate(links)],
                )
            cache[key] = ident
        entry = (cache[key], self.text(origin[0]), origin[1], origin[2])
        cache = self.entries[kind]
        if entry not in cache:
            cache[entry] = self.db.execute(
                "INSERT INTO native_recorder_" + kind + "_entries VALUES(NULL,?,?,?,?)",
                entry,
            ).lastrowid
        return {"$native_recorder_" + kind: cache[entry]}

    def normalize(self, document):
        root = document.get("native_ddr")
        if isinstance(root, dict):
            for kind in SPECS:
                if isinstance(root.get(kind), list):
                    root[kind] = [self.row(kind, v) for v in root[kind]]
        return document


def restore(db, kind, ident):
    if kind not in SPECS or type(ident) is not int or ident <= 0:
        raise ValueError("invalid recorder source reference")
    entry = db.execute(
        "SELECT e.definition_id,t.value,e.table_number,e.record_number FROM native_recorder_"
        + kind
        + "_entries e JOIN text_values t ON t.id=e.source_id WHERE e.id=?",
        (ident,),
    ).fetchone()
    if entry is None:
        raise ValueError("missing native recorder origin")
    row = db.execute(
        "SELECT * FROM native_recorder_" + kind + "_defs WHERE id=?", (entry[0],)
    ).fetchone()
    if row is None:
        raise ValueError("missing native recorder definition")
    vals = iter(row[1:])
    ints, texts, bools, refs, relation = SPECS[kind]
    out = {}
    for k in ints.split():
        out[k] = next(vals)
    for k in bools.split():
        v = next(vals)
        if v not in (0, 1):
            raise ValueError("invalid native recorder boolean")
        out[k] = bool(v)
    for k in texts.split():
        i = next(vals)
        v = (
            None
            if i is None
            else db.execute("SELECT value FROM text_values WHERE id=?", (i,)).fetchone()
        )
        if i is not None and v is None:
            raise ValueError("missing native recorder text")
        out[k] = None if v is None else v[0]
    for k in refs.split():
        out[k] = {"$signal_info": next(vals)}
    present = next(vals)
    if present not in (0, 1):
        raise ValueError("invalid uninterpreted presence")
    unknown = {}
    for key in UNINTERPRETED[kind]:
        value_id = next(vals)
        if present:
            value = db.execute(
                "SELECT value FROM text_values WHERE id=?", (value_id,)
            ).fetchone()
            if value is None:
                raise ValueError("missing uninterpreted range")
            unknown[key] = value[0]
        elif value_id is not None:
            raise ValueError("unexpected uninterpreted range")
    if present:
        out["uninterpreted_bytes"] = unknown
    if relation:
        count = next(vals)
        out[relation[0]] = []
        for r in db.execute(
            "SELECT * FROM native_recorder_"
            + kind
            + "_links WHERE definition_id=? ORDER BY position",
            (entry[0],),
        ):
            if r[1] != len(out[relation[0]]):
                raise ValueError("invalid native recorder link order")
            out[relation[0]].append(
                dict(zip(relation[1], r[2:])) if relation[1] else r[2]
            )
        if len(out[relation[0]]) != count:
            raise ValueError("incomplete native recorder links")
    out.update(source=entry[1], table=entry[2], record=entry[3])
    return out
