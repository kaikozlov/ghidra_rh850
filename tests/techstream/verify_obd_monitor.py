#!/usr/bin/env python3
"""J1979 readiness, detail joins and regulated monitor result regression tests."""
from collections import Counter
from tools.techstream import techstream_paths
from tools.techstream.parse_ddb import DDBParser
from tools.techstream.gts.ddb import _english_strings
from tools.techstream.gts.obd_monitor import obd_monitor_catalog, decode_monitor_status, decode_monitor_result, resolve_monitor_result, match_iso_result, multi_pid_supported, decode_mode06_tid_responses

p = DDBParser()
root = techstream_paths.gts_db_root(techstream_paths.resolve_gts_root())
strings = _english_strings(p, root)
engine = obd_monitor_catalog(p.parse_ecu_db(root / "Engine_CM_P6.ddb"), strings, "Engine_CM_P6.ddb")
assert len(engine["statuses"]) == 10 and len(engine["detail_links"]) == 139
misfire = next(r for r in engine["statuses"] if r["name"] == "Misfire")
assert misfire["did"] == 0xF501 and misfire["status_bit_start"] == misfire["status_bit_end"] == 15
assert misfire["detail_links"][0]["dtc"] == 0x030000
assert decode_monitor_status(misfire, bytes.fromhex("62f5010001")) == {"visible": True, "condition": 65535, "status": 1}
assert decode_monitor_status(misfire, bytes.fromhex("62f5010000"))["status"] == 0
assert decode_monitor_status(misfire, bytes.fromhex("62f50100"))["visible"] is False
assert decode_monitor_status({**misfire, "visibility_policy": 2}, b"")["visible"] is False
try:
    decode_monitor_status({**misfire, "status_bit_start": 14}, bytes.fromhex("62f5010003"))
except ValueError:
    pass
else:
    raise AssertionError("nonboolean readiness accepted")
regulated = obd_monitor_catalog(p.parse_ecu_db(root / "RegulateECU.ddb"), strings, "RegulateECU.ddb")
assert len(regulated["results"]) == 94 and len(regulated["scalings"]) == 107
result = next(r for r in regulated["results"] if r["dtc"] == 0x1100)
assert result["name"] == "IN VVT STUCK (ADVANCED) B1"
assert result["scaling_id"] == 53 and result["scalings"][0]["unit_key"] == 258
value = decode_monitor_result(123, result["scalings"][0])
assert value["converted_integer"] == 123 and value["value"] == "1.23"
subaru = obd_monitor_catalog(p.parse_ecu_db(root / "RegulateSBRECU.ddb"), strings)
sub_result = subaru["results"][0]
resolved = resolve_monitor_result(subaru, sub_result["dtc"], 53, regulatory_catalog=regulated, subaru=True)
assert resolved["scaling_id"] == 0 and resolved["runtime_scaling_id"] == 53
assert resolved["scalings"][0]["scaling_id"] == 53
counts = Counter()
old_counts = Counter()
extra_counts = Counter()
source_counts = Counter()
for path in sorted(root.glob("*.ddb")):
    if path.name.startswith(("M_", "V_", "U_")) or path.name in {"Toyota.ddb", "Viewer.ddb"}:
        continue
    db = p.parse_ecu_db(path)
    if not any(t in db.sections for t in (*range(21, 32), 34, 143, 144, 160, 161, 162, 170)):
        continue
    catalog = obd_monitor_catalog(db, strings, path.name)
    extra_counts.update({key: len(catalog[key]) for key in ("iso_results", "oxygen_sensors", "multi_pid_dependencies", "mode05_tests", "mode06_tests", "mode06_mids", "test_monitors")})
    for key in ("legacy_results", "legacy_scalings", "test_monitors"):
        source_counts.update(row["table"] for row in catalog[key])
    counts.update({key: len(catalog[key]) for key in ("statuses", "results", "detail_links", "scalings")})
    old_counts.update({key: len(catalog[key]) for key in ("legacy_statuses", "legacy_results", "legacy_detail_links", "legacy_scalings")})
assert counts == {"statuses": 20, "results": 204, "detail_links": 249, "scalings": 107}
assert old_counts == {"legacy_statuses": 310, "legacy_results": 339, "legacy_detail_links": 510, "legacy_scalings": 108}
assert source_counts[143] == 10 and source_counts[144] == 2
assert source_counts[23] and source_counts[25]
predicate = {"test_id": 1, "component_id": 2, "condition_ignore_mask": 0,
             "conditions": [{"value": 3, "operator": 1}, {"value": 4, "operator": 2},
                            {"value": 5, "operator": 3}, {"value": 6, "operator": 4}]}
assert match_iso_result(predicate, 1, 2, bytes([3, 8, 7, 1]))
assert not match_iso_result(predicate, 1, 2, bytes([3, 4, 7, 1]))
assert match_iso_result({**predicate, "condition_ignore_mask": 2}, 1, 2, bytes([3, 4, 7, 1]))
assert not match_iso_result(predicate, 9, 2, bytes([3, 8, 7, 1]))
dependencies = [{"monitor_id": 8, "dependency_monitor_id": x} for x in (2, 3)]
assert multi_pid_supported(8, dependencies, {2, 3})
assert not multi_pid_supported(8, dependencies, {2})
assert not multi_pid_supported(9, dependencies, {2, 3})
# Native response aggregation merges minimum/maximum while retaining first value.
assert decode_mode06_tid_responses([
    bytes.fromhex("4601011234ffff"),
    bytes.fromhex("46018199990010"),
    bytes.fromhex("4601018888eeee"),
]) == [{"test_id": 1, "component_id": 1, "value": 0x1234,
        "minimum": 0x10, "maximum": 0xFFFF}]
assert decode_mode06_tid_responses([b"\x46"]) == []
for malformed in (b"", bytes.fromhex("4601011234ff")):
    try:
        decode_mode06_tid_responses([malformed])
    except ValueError:
        pass
    else:
        raise AssertionError("partial Mode06 result accepted")
# The remaining 120 source records are 20 templates copied into six catalogs.
# Keep every source identity; byte equality is not permission to drop copies.
templates = {}
for region in ("NA", "EU", "JP"):
    for filename in ("PowerTrain_CARB.ddb", "CAN_CARB.ddb"):
        path = root.parents[2] / region / "DB" / "Gen" / filename
        db = p.parse_ecu_db(path)
        cat = obd_monitor_catalog(db, strings, f"{region}/{filename}")
        for table, rows in ((24, cat["mode06_tests"]),
                            (25, [r for r in cat["test_monitors"] if r["table"] == 25])):
            raw = tuple(r.raw for r in db.sections[table].iter_records())
            assert len(rows) == len(raw) == (6 if table == 24 else 14)
            assert all(r["semantic_status"] == "indexes_only" for r in rows)
            assert tuple(bytes.fromhex(r["raw"]) for r in rows) == raw
            assert templates.setdefault(table, raw) == raw
print("[PASS] 120 Mode06 legacy source rows retained; 20 byte-distinct templates, semantics explicitly incomplete")
print("[PASS] additional OBD source coverage:", dict(extra_counts), dict(source_counts))
print("[PASS] older Mode06 coverage:", dict(old_counts))
print("[PASS] J1979-2 readiness bits, DTC details, result/scaling/unit joins and scalar conversion")
print("[PASS] NA modern OBD monitor coverage:", dict(counts))
