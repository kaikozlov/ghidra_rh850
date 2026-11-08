"""Shared semantic operation frames and encoding policies; no OEM record archive."""

from __future__ import annotations

import json

DDL = """
CREATE TABLE IF NOT EXISTS text_values(id INTEGER PRIMARY KEY,value TEXT NOT NULL UNIQUE);
CREATE TABLE operation_wire_frames(id INTEGER PRIMARY KEY,selector_id INTEGER NOT NULL REFERENCES text_values(id),comm_set INTEGER NOT NULL,send BLOB NOT NULL,mask BLOB NOT NULL,check_bytes BLOB NOT NULL,receive_timeout INTEGER NOT NULL,retry_count INTEGER NOT NULL);
CREATE TABLE operation_base_frames(id INTEGER PRIMARY KEY,wire_id INTEGER NOT NULL REFERENCES operation_wire_frames(id),category_id INTEGER NOT NULL,frame_id INTEGER NOT NULL REFERENCES text_values(id),send_id INTEGER NOT NULL REFERENCES text_values(id),send_normalized_id INTEGER NOT NULL REFERENCES text_values(id),mask_id INTEGER NOT NULL REFERENCES text_values(id),mask_normalized_id INTEGER NOT NULL REFERENCES text_values(id),check_id INTEGER NOT NULL REFERENCES text_values(id),check_normalized_id INTEGER NOT NULL REFERENCES text_values(id),send_parameter INTEGER NOT NULL,unknown_word INTEGER NOT NULL,exception_id INTEGER NOT NULL,exception_flag INTEGER NOT NULL);
CREATE TABLE operation_frames(id INTEGER PRIMARY KEY,wire_id INTEGER NOT NULL REFERENCES operation_wire_frames(id),frame_id INTEGER NOT NULL REFERENCES text_values(id),name_id INTEGER NOT NULL REFERENCES text_values(id),session_id INTEGER NOT NULL REFERENCES text_values(id));
CREATE TABLE operation_encoding_policies(id INTEGER PRIMARY KEY,p5_supported INTEGER NOT NULL,p6_supported INTEGER NOT NULL,unsupported_status_id INTEGER NOT NULL REFERENCES text_values(id),source_scope_id INTEGER NOT NULL REFERENCES text_values(id),value_input_id INTEGER NOT NULL REFERENCES text_values(id),adapter_id INTEGER NOT NULL REFERENCES text_values(id),engine_selection_id INTEGER NOT NULL REFERENCES text_values(id));
CREATE TABLE operation_mask_policies(id INTEGER PRIMARY KEY,start_id INTEGER NOT NULL REFERENCES text_values(id),stop_id INTEGER NOT NULL REFERENCES text_values(id),rule_id INTEGER NOT NULL REFERENCES text_values(id));
CREATE TABLE operation_conversions(id INTEGER PRIMARY KEY,formula_id INTEGER NOT NULL REFERENCES text_values(id),source_id INTEGER NOT NULL REFERENCES text_values(id),value_integer_id INTEGER NOT NULL REFERENCES text_values(id));
"""
BASE = frozenset(
    {
        "category_id",
        "comm_frame_id",
        "comm_set",
        "comm_set_metadata",
        "kind",
        "receive_check",
        "receive_mask",
        "selector",
        "send",
    }
)
FRAME = frozenset(
    {
        "check",
        "comm_set",
        "frame",
        "mask",
        "name",
        "receive_timeout",
        "retry_count",
        "selector",
        "send",
        "session_requirement",
    }
)
META = frozenset(
    {
        "comm_set_id",
        "exception_handler_flag",
        "exception_handler_id",
        "receive_timeout",
        "retry_count",
        "send_parameter",
        "unknown_word_0c",
    }
)
ENCODING = (
    "p5_supported",
    "p6_supported",
    "unsupported_status",
    "source_scope",
    "value_input",
    "adapter",
    "engine_selection",
)
MASK = ("start", "stop", "type67_rule")
CONVERSION = ("formula", "source", "value_integer")
TABLES = {
    "$operation_base_frame": "operation_base_frames",
    "$operation_frame": "operation_frames",
    "$operation_encoding": "operation_encoding_policies",
    "$operation_mask": "operation_mask_policies",
    "$operation_conversion": "operation_conversions",
}


def encoded(v):
    return json.dumps(
        v, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False
    )


def integer(v):
    if type(v) is not int or not -(1 << 63) <= v < (1 << 63):
        raise ValueError("invalid operation integer")
    return v


def wire_bytes(v):
    if type(v) is not str:
        raise ValueError("invalid operation bytes")
    raw = bytes.fromhex(v)
    if raw.hex() != v:
        raise ValueError("noncanonical operation bytes")
    return raw


class OperationStore:
    def __init__(self, db):
        self.db = db
        self.text = {}
        self.cache = {}

    def text_id(self, value):
        if type(value) is not str:
            raise ValueError("invalid operation text")
        if value not in self.text:
            self.db.execute(
                "INSERT OR IGNORE INTO text_values(value) VALUES(?)", (value,)
            )
            self.text[value] = self.db.execute(
                "SELECT id FROM text_values WHERE value=?", (value,)
            ).fetchone()[0]
        return self.text[value]

    def row(self, table, values):
        cache = self.cache.setdefault(table, {})
        if values not in cache:
            cache[values] = self.db.execute(
                f"INSERT INTO {table} VALUES(NULL,{','.join('?' for _ in values)})",
                values,
            ).lastrowid
        return cache[values]

    def wire(self, selector, comm_set, send, mask, check, timeout, retry):
        return self.row(
            "operation_wire_frames",
            (
                self.text_id(selector),
                integer(comm_set),
                wire_bytes(send),
                wire_bytes(mask),
                wire_bytes(check),
                integer(timeout),
                integer(retry),
            ),
        )

    def frame(self, v):
        if set(v) == FRAME:
            wire = self.wire(
                v["selector"],
                v["comm_set"],
                v["send"],
                v["mask"],
                v["check"],
                v["receive_timeout"],
                v["retry_count"],
            )
            return {
                "$operation_frame": self.row(
                    "operation_frames",
                    (
                        wire,
                        self.text_id(v["frame"]),
                        self.text_id(v["name"]),
                        self.text_id(v["session_requirement"]),
                    ),
                )
            }
        if set(v) != BASE or v["kind"] != "frame":
            return None
        meta = v["comm_set_metadata"]
        if (
            not isinstance(meta, dict)
            or set(meta) != META
            or meta["comm_set_id"] != v["comm_set"]
            or type(meta["comm_set_id"]) is not int
        ):
            return None
        variables = [v[k] for k in ("send", "receive_mask", "receive_check")]
        if any(
            not isinstance(z, dict) or set(z) != {"id", "normalized_id", "bytes"}
            for z in variables
        ):
            return None
        wire = self.wire(
            v["selector"],
            v["comm_set"],
            *(z["bytes"] for z in variables),
            meta["receive_timeout"],
            meta["retry_count"],
        )
        ids = tuple(
            self.text_id(z[k]) for z in variables for k in ("id", "normalized_id")
        )
        extra = tuple(
            integer(meta[k])
            for k in (
                "send_parameter",
                "unknown_word_0c",
                "exception_handler_id",
                "exception_handler_flag",
            )
        )
        return {
            "$operation_base_frame": self.row(
                "operation_base_frames",
                (
                    wire,
                    integer(v["category_id"]),
                    self.text_id(v["comm_frame_id"]),
                    *ids,
                    *extra,
                ),
            )
        }

    def policy(self, v, field):
        if field == "encoding_requirements" and set(v) == set(ENCODING):
            if (
                type(v["p5_supported"]) is not bool
                or type(v["p6_supported"]) is not bool
            ):
                return None
            values = (
                int(v["p5_supported"]),
                int(v["p6_supported"]),
                *(self.text_id(v[k]) for k in ENCODING[2:]),
            )
            return {
                "$operation_encoding": self.row("operation_encoding_policies", values)
            }
        if field == "control_enable_mask" and set(v) == set(MASK):
            return {
                "$operation_mask": self.row(
                    "operation_mask_policies", tuple(self.text_id(v[k]) for k in MASK)
                )
            }
        if field == "engineering_to_raw" and set(v) == set(CONVERSION):
            return {
                "$operation_conversion": self.row(
                    "operation_conversions",
                    tuple(self.text_id(v[k]) for k in CONVERSION),
                )
            }
        return None

    def normalize(self, value, field=""):
        if isinstance(value, list):
            return [self.normalize(v, field) for v in value]
        if not isinstance(value, dict):
            return value
        try:
            ref = self.frame(value) or self.policy(value, field)
        except (KeyError, TypeError, ValueError):
            ref = None
        if ref is not None:
            return ref
        return {k: self.normalize(v, k) for k, v in value.items()}


def _text(db, identity):
    row = db.execute("SELECT value FROM text_values WHERE id=?", (identity,)).fetchone()
    if row is None:
        raise ValueError("missing operation text")
    return row[0]


def _wire(db, identity):
    row = db.execute(
        "SELECT selector_id,comm_set,send,mask,check_bytes,receive_timeout,retry_count FROM operation_wire_frames WHERE id=?",
        (identity,),
    ).fetchone()
    if row is None or any(type(v) is not bytes for v in row[2:5]):
        raise ValueError("missing or invalid operation wire frame")
    return (_text(db, row[0]), *row[1:])


def restore(db, marker, identity):
    if marker not in TABLES or type(identity) is not int or identity <= 0:
        raise ValueError("invalid operation reference")
    row = db.execute(
        f"SELECT * FROM {TABLES[marker]} WHERE id=?", (identity,)
    ).fetchone()
    if row is None:
        raise ValueError("missing operation definition")
    row = row[1:]
    if marker == "$operation_encoding":
        if row[0] not in (0, 1) or row[1] not in (0, 1):
            raise ValueError("invalid operation support flags")
        return dict(
            zip(
                ENCODING, (bool(row[0]), bool(row[1]), *(_text(db, x) for x in row[2:]))
            )
        )
    if marker in ("$operation_mask", "$operation_conversion"):
        return dict(
            zip(
                MASK if marker == "$operation_mask" else CONVERSION,
                (_text(db, x) for x in row),
            )
        )
    selector, comm, send, mask, check, timeout, retry = _wire(db, row[0])
    if marker == "$operation_frame":
        return dict(
            selector=selector,
            comm_set=comm,
            send=send.hex(),
            mask=mask.hex(),
            check=check.hex(),
            receive_timeout=timeout,
            retry_count=retry,
            frame=_text(db, row[1]),
            name=_text(db, row[2]),
            session_requirement=_text(db, row[3]),
        )
    variables = [
        dict(
            id=_text(db, row[3 + i * 2]),
            normalized_id=_text(db, row[4 + i * 2]),
            bytes=data.hex(),
        )
        for i, data in enumerate((send, mask, check))
    ]
    meta = dict(
        comm_set_id=comm,
        receive_timeout=timeout,
        retry_count=retry,
        send_parameter=row[9],
        unknown_word_0c=row[10],
        exception_handler_id=row[11],
        exception_handler_flag=row[12],
    )
    return dict(
        category_id=row[1],
        comm_frame_id=_text(db, row[2]),
        comm_set=comm,
        comm_set_metadata=meta,
        kind="frame",
        send=variables[0],
        receive_mask=variables[1],
        receive_check=variables[2],
        selector=selector,
    )


def normalize(db):
    from tools.techstream.diag_codec import compress, decompress

    db.executescript(DDL)
    store = OperationStore(db)
    for table, keys in (
        ("source_documents", ("id",)),
        ("source_document_parts", ("document_id", "pointer_id")),
    ):
        for row in db.execute(f"SELECT {','.join(keys)},data FROM {table}"):
            value = json.loads(decompress(row[-1]))
            changed = store.normalize(value)
            if changed != value:
                db.execute(
                    f"UPDATE {table} SET data=? WHERE "
                    + " AND ".join(k + "=?" for k in keys),
                    (compress(encoded(changed).encode()), *row[:-1]),
                )
    return {
        table: db.execute("SELECT count(*) FROM " + table).fetchone()[0]
        for table in ("operation_wire_frames", *TABLES.values())
    }
