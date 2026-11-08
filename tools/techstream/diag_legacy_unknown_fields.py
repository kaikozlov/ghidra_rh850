"""Fixed unresolved ranges retained alongside decoded legacy facts."""

FIELDS = {
    "operation": ("0_19", "60_61", "70_73", "80_81", "83", "86_87", "90_91"),
    "pattern": ("14_17", "22_23"),
    "dynamic": ("14_16", "18_end"),
}
LENGTHS = {"operation": (20, 2, 4, 2, 1, 2, 2), "pattern": (4, 2), "dynamic": (3, None)}
DDL = "\n".join(
    "CREATE TABLE IF NOT EXISTS legacy_"
    + kind
    + "_unknown_facts(id INTEGER PRIMARY KEY,"
    + ",".join(
        "range_" + key + "_id INTEGER NOT NULL REFERENCES text_values(id)"
        for key in keys
    )
    + ");"
    for kind, keys in FIELDS.items()
)


def validate(domain, value):
    if value is None:
        return
    if (
        type(value) is not dict
        or set(value) != set(FIELDS[domain])
        or any(type(v) is not str for v in value.values())
    ):
        raise ValueError("unsupported legacy uninterpreted fields")
    for key, size in zip(FIELDS[domain], LENGTHS[domain]):
        raw = bytes.fromhex(value[key])
        if raw.hex() != value[key] or (size is not None and len(raw) != size):
            raise ValueError("unsupported legacy uninterpreted range")


class UnknownStore:
    def __init__(self, db):
        self.db = db
        db.executescript(DDL)
        self.text = {}
        self.cache = {}
        for domain in FIELDS:
            self.cache[domain] = {
                tuple(r[1:]): r[0]
                for r in db.execute("SELECT * FROM legacy_" + domain + "_unknown_facts")
            }

    def intern(self, domain, value):
        validate(domain, value)
        if value is None:
            return None
        ids = []
        for key in FIELDS[domain]:
            text = value[key]
            if text not in self.text:
                self.db.execute(
                    "INSERT OR IGNORE INTO text_values(value)VALUES(?)", (text,)
                )
                self.text[text] = self.db.execute(
                    "SELECT id FROM text_values WHERE value=?", (text,)
                ).fetchone()[0]
            ids.append(self.text[text])
        key = tuple(ids)
        cache = self.cache[domain]
        if key not in cache:
            cache[key] = self.db.execute(
                "INSERT INTO legacy_"
                + domain
                + "_unknown_facts VALUES(NULL,"
                + ",".join("?" for _ in ids)
                + ")",
                ids,
            ).lastrowid
        return cache[key]


def restore(db, domain, identity):
    if identity is None:
        return None
    if domain not in FIELDS or type(identity) is not int or identity <= 0:
        raise ValueError("invalid legacy unknown reference")
    row = db.execute(
        "SELECT * FROM legacy_" + domain + "_unknown_facts WHERE id=?", (identity,)
    ).fetchone()
    if row is None:
        raise ValueError("missing legacy unknown facts")
    result = {}
    for key, text_id in zip(FIELDS[domain], row[1:]):
        text = db.execute(
            "SELECT value FROM text_values WHERE id=?", (text_id,)
        ).fetchone()
        if text is None:
            raise ValueError("missing legacy unknown range")
        result[key] = text[0]
    validate(domain, result)
    return result
