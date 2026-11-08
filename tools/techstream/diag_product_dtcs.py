"""Decoded diagnostic trouble-code facts for the product catalog.

No raw firmware records or research reconstruction are required. Unknown semantic
fields remain inline rather than being discarded or encoded in opaque sidecars.
"""

from __future__ import annotations

DDL = """
CREATE TABLE IF NOT EXISTS text_values(id INTEGER PRIMARY KEY,value TEXT NOT NULL UNIQUE);
CREATE TABLE IF NOT EXISTS diagnostic_codes(
 id INTEGER PRIMARY KEY,code_id INTEGER NOT NULL REFERENCES text_values(id),
 description_id INTEGER REFERENCES text_values(id),comment_id INTEGER REFERENCES text_values(id),
 failure_id INTEGER REFERENCES text_values(id),identifier INTEGER,packed_code INTEGER,
 field_mask INTEGER NOT NULL);
CREATE TABLE IF NOT EXISTS dtc_entries(
 id INTEGER PRIMARY KEY,code_id INTEGER NOT NULL REFERENCES diagnostic_codes(id),
 source_id INTEGER REFERENCES text_values(id),table_number INTEGER,record_number INTEGER,
 origin_mask INTEGER NOT NULL);
"""
FIELDS = {
    "kind": 1,
    "description": 2,
    "comment": 4,
    "failure": 8,
    "dtc_identifier": 16,
    "packed_dtc": 32,
}
ORIGIN = {"source": 1, "table": 2, "record": 4}
ALLOWED = {"code", *FIELDS, *ORIGIN}
MAX_INT = (1 << 63) - 1


class DTCStore:
    def __init__(self, db):
        self.db = db
        db.executescript(DDL)
        self.texts = {}
        self.codes = {
            tuple(r[1:]): r[0] for r in db.execute("SELECT * FROM diagnostic_codes")
        }
        self.entries = {
            tuple(r[1:]): r[0] for r in db.execute("SELECT * FROM dtc_entries")
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
        if type(row) is not dict or "code" not in row or not set(row) <= ALLOWED:
            return row
        if type(row["code"]) is not str or ("kind" in row and row["kind"] != "dtc"):
            return row
        for field in ("description", "comment", "failure", "source"):
            if field in row and row[field] is not None and type(row[field]) is not str:
                return row
        for field in ("dtc_identifier", "table", "record"):
            if (
                field in row
                and row[field] is not None
                and (type(row[field]) is not int or not 0 <= row[field] <= MAX_INT)
            ):
                return row
        packed = row.get("packed_dtc")
        if packed is not None:
            try:
                decoded = int(packed, 16)
            except (ValueError, TypeError):
                return row
            if not 0 <= decoded <= 0xFFFFFFFF or packed != f"0x{decoded:06X}":
                return row
            packed = decoded
        mask = sum(bit for field, bit in FIELDS.items() if field in row)
        key = (
            self.text(row["code"]),
            self.text(row.get("description")),
            self.text(row.get("comment")),
            self.text(row.get("failure")),
            row.get("dtc_identifier"),
            packed,
            mask,
        )
        if key not in self.codes:
            self.codes[key] = self.db.execute(
                "INSERT INTO diagnostic_codes(code_id,description_id,comment_id,failure_id,identifier,packed_code,field_mask) VALUES(?,?,?,?,?,?,?)",
                key,
            ).lastrowid
        origin_mask = sum(bit for field, bit in ORIGIN.items() if field in row)
        binding = (
            self.codes[key],
            self.text(row.get("source")),
            row.get("table"),
            row.get("record"),
            origin_mask,
        )
        if binding not in self.entries:
            self.entries[binding] = self.db.execute(
                "INSERT INTO dtc_entries(code_id,source_id,table_number,record_number,origin_mask) VALUES(?,?,?,?,?)",
                binding,
            ).lastrowid
        return {"$diagnostic_code": self.entries[binding]}

    def normalize(self, document):
        if type(document) is not dict or type(document.get("dtcs")) is not dict:
            return document
        result = dict(document)
        result["dtcs"] = {
            code: [self.row(row) for row in rows] if type(rows) is list else rows
            for code, rows in document["dtcs"].items()
        }
        return result


def restore(db, identity):
    if type(identity) is not int or identity <= 0:
        raise ValueError("invalid diagnostic code reference")
    row = db.execute(
        """
      SELECT c.value,d.value,m.value,f.value,v.identifier,v.packed_code,v.field_mask,
             s.value,e.table_number,e.record_number,e.origin_mask,
             v.description_id,v.comment_id,v.failure_id,e.source_id
      FROM dtc_entries e JOIN diagnostic_codes v ON v.id=e.code_id
      JOIN text_values c ON c.id=v.code_id LEFT JOIN text_values d ON d.id=v.description_id
      LEFT JOIN text_values m ON m.id=v.comment_id LEFT JOIN text_values f ON f.id=v.failure_id
      LEFT JOIN text_values s ON s.id=e.source_id WHERE e.id=?""",
        (identity,),
    ).fetchone()
    if row is None:
        raise ValueError(f"missing diagnostic code {identity}")
    (
        code,
        description,
        comment,
        failure,
        identifier,
        packed,
        mask,
        source,
        table,
        record,
        origin_mask,
        *refs,
    ) = row
    if mask < 0 or mask & ~63 or origin_mask < 0 or origin_mask & ~7:
        raise ValueError("invalid diagnostic code field mask")
    for value, ref in zip((description, comment, failure, source), refs):
        if (ref is None) != (value is None):
            raise ValueError("missing diagnostic code text")
    values = {
        "kind": "dtc",
        "description": description,
        "comment": comment,
        "failure": failure,
        "dtc_identifier": identifier,
        "packed_dtc": None if packed is None else f"0x{packed:06X}",
    }
    for field, value in (("dtc_identifier", identifier), ("packed_dtc", packed)):
        if value is not None and (
            type(value) is not int
            or value < 0
            or value > (0xFFFFFFFF if field == "packed_dtc" else MAX_INT)
        ):
            raise ValueError("invalid diagnostic code integer")
    result = {"code": code}
    result.update({field: values[field] for field, bit in FIELDS.items() if mask & bit})
    for field, value in (
        ("description", description),
        ("comment", comment),
        ("failure", failure),
        ("dtc_identifier", identifier),
        ("packed_dtc", packed),
    ):
        if not mask & FIELDS[field] and value is not None:
            raise ValueError("unexpected diagnostic code value")
    for field, value in (("source", source), ("table", table), ("record", record)):
        if origin_mask & ORIGIN[field]:
            if (
                field != "source"
                and value is not None
                and (type(value) is not int or not 0 <= value <= MAX_INT)
            ):
                raise ValueError("invalid diagnostic code origin")
            result[field] = value
        elif value is not None:
            raise ValueError("unexpected diagnostic code origin")
    return result
