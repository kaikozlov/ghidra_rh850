"""Canonical ECU configurations with separate regional/category ownership.

Only complete catalog bodies excluding the root category are shared. Equality
includes every semantic value, ordered membership and duplicate occurrence.
This is a domain boundary, not arbitrary JSON-subtree interning.
"""

import hashlib
import json

from tools.techstream.diag_codec import compress, decompress

DDL = """
CREATE TABLE ecu_catalog_definitions(id INTEGER PRIMARY KEY,data BLOB NOT NULL);
CREATE TABLE ecu_catalog_bindings(
 document_id INTEGER PRIMARY KEY REFERENCES source_documents(id),
 definition_id INTEGER NOT NULL REFERENCES ecu_catalog_definitions(id),
 category BLOB NOT NULL);
"""


def encoded(value):
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode()


def restore(db, identity):
    if type(identity) is not int or identity <= 0:
        raise ValueError("invalid ECU catalog reference")
    row = db.execute(
        "SELECT d.data,b.category FROM ecu_catalog_bindings b JOIN ecu_catalog_definitions d ON d.id=b.definition_id WHERE b.document_id=?",
        (identity,),
    ).fetchone()
    if row is None:
        raise ValueError("missing ECU catalog binding")
    body, category = (json.loads(decompress(blob)) for blob in row)
    if (
        not isinstance(body, dict)
        or "category" in body
        or not isinstance(category, dict)
    ):
        raise ValueError("invalid ECU catalog definition")
    return dict(body, category=category)


def normalize(db):
    db.executescript(DDL)
    # Hashes narrow candidates only. Actual canonical body bytes decide equality.
    candidates = {}
    counts = {
        "owners": 0,
        "definitions": 0,
        "body_bytes_before": 0,
        "body_bytes_unique": 0,
        "skipped": 0,
    }
    has_parts = db.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name='source_document_parts'"
    ).fetchone()
    for identity, member, packed in db.execute(
        "SELECT id,member,data FROM source_documents WHERE member LIKE 'catalogs/%' ORDER BY id"
    ):
        original = json.loads(decompress(packed))
        if not isinstance(original, dict) or not isinstance(
            original.get("category"), dict
        ):
            counts["skipped"] += 1
            continue
        # Future catalog-specific parts require an explicit domain migration.
        if (
            has_parts
            and db.execute(
                "SELECT 1 FROM source_document_parts WHERE document_id=? LIMIT 1",
                (identity,),
            ).fetchone()
        ):
            counts["skipped"] += 1
            continue
        body = {k: v for k, v in original.items() if k != "category"}
        raw = encoded(body)
        digest = hashlib.sha256(raw).digest()
        definition = None
        for candidate in candidates.get(digest, []):
            prior = db.execute(
                "SELECT data FROM ecu_catalog_definitions WHERE id=?", (candidate,)
            ).fetchone()[0]
            if decompress(prior) == raw:
                definition = candidate
                break
        if definition is None:
            definition = db.execute(
                "INSERT INTO ecu_catalog_definitions(data) VALUES(?)", (compress(raw),)
            ).lastrowid
            candidates.setdefault(digest, []).append(definition)
            counts["definitions"] += 1
            counts["body_bytes_unique"] += len(raw)
        db.execute(
            "INSERT INTO ecu_catalog_bindings VALUES(?,?,?)",
            (identity, definition, compress(encoded(original["category"]))),
        )
        db.execute(
            "UPDATE source_documents SET data=? WHERE id=?",
            (compress(encoded({"$ecu_catalog": identity})), identity),
        )
        counts["owners"] += 1
        counts["body_bytes_before"] += len(raw)
    return counts
