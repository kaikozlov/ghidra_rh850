"""Read reconstructed product semantics from the exported SQLite database."""

import json

from tools.techstream.diag_codec import decompress
from tools.techstream.diag_metadata import restore


def at_pointer(value, pointer):
    if not pointer:
        return value
    if not pointer.startswith("/"):
        raise ValueError(f"invalid JSON pointer: {pointer}")
    for token in pointer.split("/")[1:]:
        token = token.replace("~1", "/").replace("~0", "~")
        value = value[int(token)] if isinstance(value, list) else value[token]
    return value


def _decode(db, packed):
    return restore(db, json.loads(decompress(packed)))


def read_document(db, member):
    row = db.execute(
        "SELECT id,data FROM source_documents WHERE member=?", (member,)
    ).fetchone()
    if row is None:
        raise ValueError(f"missing product document: {member}")
    document_id, packed = row
    document = _decode(db, packed)
    for pointer, data in db.execute(
        """SELECT p.pointer,s.data
            FROM source_document_parts s JOIN source_pointers p ON p.id=s.pointer_id
            WHERE s.document_id=?""",
        (document_id,),
    ):
        tokens = pointer.split("/")
        parent = at_pointer(document, "/".join(tokens[:-1]))
        key = tokens[-1].replace("~1", "/").replace("~0", "~")
        parent[int(key) if isinstance(parent, list) else key] = _decode(db, data)
    return document


def read_item(db, item_id):
    row = db.execute(
        """SELECT r.member_id,p.pointer
        FROM item_source_refs r JOIN source_pointers p ON p.id=r.pointer_id
        WHERE r.item_id=?""",
        (item_id,),
    ).fetchone()
    if row is None:
        raise ValueError(f"missing product item: {item_id}")
    member_id, pointer = row
    # Index entities are separate semantic parts. Reading one item must not
    # materialize the full vehicle/route index.
    for part_pointer, packed in db.execute(
        """SELECT p.pointer,s.data
            FROM source_document_parts s JOIN source_pointers p ON p.id=s.pointer_id
            WHERE s.document_id=?""",
        (member_id,),
    ):
        if pointer == part_pointer or pointer.startswith(part_pointer + "/"):
            return at_pointer(_decode(db, packed), pointer[len(part_pointer) :])
    packed = db.execute(
        "SELECT data FROM source_documents WHERE id=?", (member_id,)
    ).fetchone()[0]
    return at_pointer(_decode(db, packed), pointer)
