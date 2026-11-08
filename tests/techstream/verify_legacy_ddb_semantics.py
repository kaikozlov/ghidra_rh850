#!/usr/bin/env python3
"""Verify legacy source records are retained without fabricated UDS/P5 semantics."""
from collections import Counter
from types import SimpleNamespace
import struct

from tools.techstream import techstream_paths
from tools.techstream.ddb_semantics import dtc_rows
from tools.techstream.gts.legacy_catalog import legacy_catalog_rows
from tools.techstream.gts.master import _master_variable
from tools.techstream.gts.ddb import _english_strings
from tools.techstream.parse_ddb import DDBParser, Section, TableDataHead


def section(table, rows):
    payload = b"".join(rows)
    return Section(TableDataHead(table, 0, len(rows), len(payload)), 0, payload)


strings = SimpleNamespace(get_string=lambda key: {1: "Description", 2: "Comment", 3: "Name"}.get(key))
old = bytearray(28)
old[:12] = "P0001\0".encode("utf-16-le")
struct.pack_into("<IIH", old, 12, 1, 2, 0x1234)
modern = bytearray(68)
modern[:44] = "P000100".encode("utf-16-le").ljust(44, b"\0")
struct.pack_into("<III", modern, 44, 0x000100, 1, 2)
parser = DDBParser()
rows = dtc_rows(parser, SimpleNamespace(sections={5: section(5, [old]), 65: section(65, [modern])}), strings, "fixture")
assert len(rows) == 2 and rows[0]["code"] == "P0001"
assert rows[0]["dtc_identifier"] == 0x1234
assert rows[0]["description"] == "Description" and rows[0]["comment"] == "Comment"
assert "packed_dtc" not in rows[0] and "failure" not in rows[0]
assert rows[1]["packed_dtc"] == "0x000100"
assert rows[0]["raw"] == old
try:
    dtc_rows(parser, SimpleNamespace(sections={5: section(5, [b"x" * 27])}), strings, "bad")
except ValueError:
    pass
else:
    raise AssertionError("malformed DTC record accepted")

root = techstream_paths.gts_db_root(techstream_paths.resolve_gts_root())
strings = _english_strings(parser, root)
db = parser.parse_ecu_db(root / "Engine_P3.ddb")
dtcs = dtc_rows(parser, db, strings, "Engine_P3.ddb")
master = parser.parse_master_db(root / "Toyota.ddb")
rows = legacy_catalog_rows(db, strings, "Engine_P3.ddb", lambda key: bytes.fromhex(
    _master_variable(master if key > 10000 else db, key)["bytes"]))
counts = Counter(row["kind"] for row in rows)
assert len(dtcs) == 2344
assert counts == {"pid": 138, "did": 18, "pid_bit": 104, "did_bit": 66,
                  "freeze_frame": 407, "active_test": 66, "active_test_pattern": 30}
assert next(x for x in rows if x["kind"] == "freeze_frame")["name"] == "Number of Emission DTC"
assert all(x.get("name") for x in rows if x["kind"] in {"freeze_frame", "active_test"})
print("[PASS] legacy DTC identity, mixed-generation retention, layout validation, decoded legacy catalog")
print("[PASS] Engine_P3: 2344 DTCs and", dict(counts))
