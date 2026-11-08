#!/usr/bin/env python3
"""Check native legacy support predicates and exact response field boundaries."""
from collections import Counter
from types import SimpleNamespace
import struct

from tools.techstream import techstream_paths
from tools.techstream.parse_ddb import DDBParser, Section, TableDataHead
from tools.techstream.gts.legacy_signals import response_definitions, support_conditions, evaluate_support_condition
from tools.techstream.gts.master import _master_variable


def section(table, rows):
    raw = b"".join(rows)
    return Section(TableDataHead(table, 0, len(rows), len(raw)), 0, raw)


pid = bytes.fromhex("3412120001020300")
did = bytes.fromhex("7856000012040500")
db = SimpleNamespace(sections={6: section(6, [pid]), 7: section(7, [did])})
rows = response_definitions(db)
assert rows[0]["key"] == 0x12 and rows[0]["data_length"] == 0
assert rows[0]["length_resolution"] == "runtime"
assert rows[0]["exception_id"] == 0x1234 and rows[0]["exception_flag"] == 3
assert rows[1]["key"] == 0x12 and rows[1]["data_length"] == 4
assert rows[1]["exception_id"] == 0x5678 and rows[1]["exception_flag"] == 5
assert DDBParser.extract_dids(db.sections[7]) == [0x12]
from tools.techstream.extract_steering_corpus import extract_dids
projected = extract_dids(db)
assert projected[0]["identifier_u8"] == 0x12
assert projected[0]["response_data_length"] == 4
assert projected[0]["identifier_bytes_hex"] == "12"
assert "identifier_u16_le" not in projected[0]
try:
    DDBParser.extract_dids(section(7, [b"x" * 7]))
except ValueError:
    pass
else:
    raise AssertionError("truncated legacy DID silently dropped")


def condition(table, mode, start, end, flag=0):
    return struct.pack("<5H", 1, 10001, 8, start, end) + bytes((flag, mode) if table == 8 else (mode, flag))


db = SimpleNamespace(sections={
    8: section(8, [condition(8, 4, 7, 8, 3), condition(8, 2, 0, 0)]),
    9: section(9, [condition(9, 6, 0, 7, 9)]),
})
rows = support_conditions(db)
assert rows[0]["exception_flag"] == 3 and rows[2]["exception_flag"] == 9
assert rows[0]["query"]["request_selector"] == 0x6A
assert rows[0]["query"]["response_offset"] == 4
assert evaluate_support_condition(rows[0], bytes.fromhex("000000000180"))
assert not evaluate_support_condition(rows[0], bytes.fromhex("00000000fe7f"))
assert evaluate_support_condition(rows[1], bytes.fromhex("000080"))
assert not evaluate_support_condition(rows[1], bytes.fromhex("000001"))
assert rows[2]["query"]["cache"] == "did_support"
assert evaluate_support_condition(rows[2], b"\x01")
assert not evaluate_support_condition(rows[2], b"")
resolved = support_conditions(db, lambda _: b"\x12\x34")
assert resolved[0]["request_patches"] == [{"offset": 2, "value": 0x12}, {"offset": 3, "value": 0x34}]
assert resolved[1]["native_status"] == "invalid_variable_length"
assert resolved[2]["cache_identifier"] == 0x12
assert rows[1]["supported_identifier_gate"]["CheckSupportBit"] == "pid"
assert rows[1]["supported_identifier_gate"]["CheckSupportBitOldBody"] is None
for malformed in (b"x" * 11, b"x" * 13):
    try:
        support_conditions(SimpleNamespace(sections={8: section(8, [malformed])}))
    except ValueError:
        pass
    else:
        raise AssertionError("incorrect native record stride accepted")

parser = DDBParser()
root = techstream_paths.gts_db_root(techstream_paths.resolve_gts_root())
master = parser.parse_master_db(root / "Toyota.ddb")
counts = Counter()
for path in sorted(root.glob("*.ddb")):
    if path.name.startswith(("M_", "V_", "U_")) or path.name in {"Toyota.ddb", "Viewer.ddb"}:
        continue
    db = parser.parse_ecu_db(path)
    response_definitions(db, path.name)
    rows = support_conditions(db, lambda key: bytes.fromhex(
        _master_variable(master if key > 10000 else db, key)["bytes"]), path.name)
    assert all(row["native_status"] == "valid" for row in rows), path.name
    counts.update((row["table"], row["source_mode"]) for row in rows)
assert counts == {(8, 2): 3374, (8, 4): 196, (9, 2): 983, (9, 3): 142, (9, 4): 112, (9, 6): 947}
print("[PASS] legacy response lengths, exception offsets, MSB-first predicates, request patches and cache mode")
print("[PASS] all 5754 NA support conditions resolve variables and native modes:", dict(counts))
