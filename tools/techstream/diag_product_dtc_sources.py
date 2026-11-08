"""Source DTC admission fields extend the same canonical diagnostic definitions."""

from __future__ import annotations

from tools.techstream.diag_product_dtcs import DTCStore
from tools.techstream.diag_product_dtcs import restore as restore_code

DDL = """
CREATE TABLE IF NOT EXISTS dtc_source_extensions(
 id INTEGER PRIMARY KEY,entry_id INTEGER NOT NULL REFERENCES dtc_entries(id),
 enabled_value INTEGER NOT NULL,description_string_index INTEGER NOT NULL,
 comment_string_index INTEGER NOT NULL,exception_handler_id INTEGER NOT NULL,
 exception_handler_flag INTEGER NOT NULL,detail_table INTEGER,detail_lookup_key INTEGER,
 failure_string_index INTEGER,info_byte INTEGER,info_word INTEGER,unknown_bytes BLOB NOT NULL);
"""
BASE = frozenset(
    {
        "code",
        "description",
        "description_string_index",
        "comment",
        "comment_string_index",
        "enabled",
        "enabled_value",
        "exception_handler_id",
        "exception_handler_flag",
        "source",
        "table",
        "record",
        "uninterpreted_bytes",
    }
)
SHAPES = {
    5: BASE
    | {
        "dtc_identifier",
        "detail_table",
        "detail_lookup_key",
        "unconsumed_descriptor_offsets",
    },
    65: BASE
    | {
        "packed_dtc",
        "base_dtc",
        "failure_type",
        "failure_string_index",
        "failure_description",
        "diag_code_info_fields",
    },
}


def uint(value, bits):
    if type(value) is not int or not 0 <= value < 1 << bits:
        raise ValueError("invalid source DTC integer")
    return value


def source_values(row):
    table = row.get("table")
    if type(table) is not int or table not in SHAPES or set(row) != SHAPES[table]:
        raise ValueError("unrecognized source DTC fields")
    uint(row["record"], 63)
    if type(row["source"]) is not str or type(row["code"]) is not str:
        raise ValueError("invalid source DTC identity")
    enabled = uint(row["enabled_value"], 8)
    if type(row["enabled"]) is not bool or row["enabled"] != (enabled != 0):
        raise ValueError("inconsistent source DTC enabled state")
    common = (
        enabled,
        uint(row["description_string_index"], 32),
        uint(row["comment_string_index"], 32),
        uint(row["exception_handler_id"], 16),
        uint(row["exception_handler_flag"], 8),
    )
    if table == 5:
        if row["unconsumed_descriptor_offsets"] != [24, 25] or any(
            type(x) is not int for x in row["unconsumed_descriptor_offsets"]
        ):
            raise ValueError("unrecognized DTC descriptor offsets")
        detail = uint(row["detail_table"], 16)
        lookup = uint(row["detail_lookup_key"], 16)
        failure = byte = word = None
        key, width = "24_25", 2
    else:
        packed = uint(row["packed_dtc"], 32)
        if (
            type(row["base_dtc"]) is not int
            or row["base_dtc"] != (packed >> 8) & 65535
            or type(row["failure_type"]) is not int
            or row["failure_type"] != packed & 255
        ):
            raise ValueError("inconsistent packed DTC fields")
        info = row["diag_code_info_fields"]
        if type(info) is not list or len(info) != 2:
            raise ValueError("unrecognized DTC info fields")
        byte = uint(info[0]["value"], 8)
        word = uint(info[1]["value"], 16)
        expected = [
            {"source_offset": 65, "output_offset": 52, "width": 1, "value": byte},
            {"source_offset": 62, "output_offset": 54, "width": 2, "value": word},
        ]
        if info != expected or any(
            type(v) is not int for part in info for v in part.values()
        ):
            raise ValueError("unrecognized DTC info geometry")
        detail = lookup = None
        failure = uint(row["failure_string_index"], 32)
        key, width = "67", 1
    unknown = row["uninterpreted_bytes"]
    if (
        type(unknown) is not dict
        or set(unknown) != {key}
        or type(unknown[key]) is not str
    ):
        raise ValueError("unrecognized DTC unknown bytes")
    blob = bytes.fromhex(unknown[key])
    if len(blob) != width or blob.hex() != unknown[key]:
        raise ValueError("invalid source DTC unknown bytes")
    return common + (detail, lookup, failure, byte, word, blob)


class SourceDTCStore:
    def __init__(self, db, codes=None):
        self.db = db
        self.codes = codes if codes is not None else DTCStore(db)
        db.executescript(DDL)
        self.entries = {
            tuple(row[1:]): row[0]
            for row in db.execute("SELECT * FROM dtc_source_extensions")
        }

    def row(self, row):
        if type(row) is not dict:
            return row
        try:
            values = source_values(row)
            semantic = {
                key: row[key]
                for key in (
                    "source",
                    "table",
                    "record",
                    "code",
                    "description",
                    "comment",
                )
            }
            semantic["kind"] = "dtc"
            if row["table"] == 5:
                semantic["dtc_identifier"] = uint(row["dtc_identifier"], 16)
            else:
                semantic["packed_dtc"] = f"0x{row['packed_dtc']:06X}"
                semantic["failure"] = row["failure_description"]
                if semantic["comment"] is None:
                    semantic.pop(
                        "comment"
                    )  # Existing P6 diagnostic definition has no comment field.
            ref = self.codes.row(semantic)
            if set(ref) != {"$diagnostic_code"}:
                return row
        except (KeyError, ValueError, TypeError, IndexError):
            return row
        key = (ref["$diagnostic_code"], *values)
        if key not in self.entries:
            self.entries[key] = self.db.execute(
                "INSERT INTO dtc_source_extensions VALUES("
                + ",".join("?" for _ in range(13))
                + ")",
                (None, *key),
            ).lastrowid
        return {"$dtc_source_definition": self.entries[key]}

    def normalize(self, value):
        if type(value) is not dict or type(value.get("dtc_source")) is not list:
            return value
        return {**value, "dtc_source": [self.row(row) for row in value["dtc_source"]]}


def restore(db, identity):
    if type(identity) is not int or identity <= 0:
        raise ValueError("invalid source DTC reference")
    row = db.execute(
        "SELECT * FROM dtc_source_extensions WHERE id=?", (identity,)
    ).fetchone()
    if row is None:
        raise ValueError("missing source DTC definition")
    _, entry, enabled, di, ci, ehid, ehflag, detail, lookup, fi, ib, iw, unknown = row
    semantic = restore_code(db, entry)
    table = semantic.get("table")
    out = {
        key: semantic[key]
        for key in ("source", "table", "record", "code", "description")
    }
    out["comment"] = semantic.get("comment")
    out.update(
        enabled_value=enabled,
        enabled=enabled != 0,
        description_string_index=di,
        comment_string_index=ci,
        exception_handler_id=ehid,
        exception_handler_flag=ehflag,
    )
    if type(unknown) is not bytes:
        raise ValueError("invalid source DTC byte storage")
    if table == 5:
        if any(v is not None for v in (fi, ib, iw)):
            raise ValueError("unexpected source DTC extension fields")
        out.update(
            dtc_identifier=semantic["dtc_identifier"],
            detail_table=detail,
            detail_lookup_key=lookup,
            unconsumed_descriptor_offsets=[24, 25],
            uninterpreted_bytes={"24_25": unknown.hex()},
        )
    elif table == 65:
        if detail is not None or lookup is not None:
            raise ValueError("unexpected source DTC detail fields")
        packed = int(semantic["packed_dtc"], 16)
        out.update(
            packed_dtc=packed,
            base_dtc=(packed >> 8) & 65535,
            failure_type=packed & 255,
            failure_string_index=fi,
            failure_description=semantic["failure"],
            uninterpreted_bytes={"67": unknown.hex()},
            diag_code_info_fields=[
                {"source_offset": 65, "output_offset": 52, "width": 1, "value": ib},
                {"source_offset": 62, "output_offset": 54, "width": 2, "value": iw},
            ],
        )
    else:
        raise ValueError("invalid source DTC table")
    source_values(out)
    return out
