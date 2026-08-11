#!/usr/bin/env python3
"""Verify Toyota.ddb steering routes from raw master-table bytes."""

from __future__ import annotations

import hashlib
import json
import struct
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "tools/techstream"))
from parse_ddb import lzss_decompress  # noqa: E402

ARTIFACT = REPO / "data/generated/techstream_v18/toyota_master_routes.json"

passed = failed = 0


def check(name: str, condition: object, detail: str = "") -> None:
    global passed, failed
    ok = bool(condition)
    passed += int(ok)
    failed += int(not ok)
    print(f"[{'PASS' if ok else 'FAIL'}] {name}" + (f" ({detail})" if detail else ""))


def raw_section(data: bytes, table_type: int) -> dict:
    directory_slot = 0x24 + table_type * 4
    section_offset = struct.unpack_from("<I", data, directory_slot)[0]
    if not section_offset:
        raise AssertionError(f"missing section {table_type}")
    actual_type, compression = struct.unpack_from("<BB", data, section_offset)
    count, payload_size = struct.unpack_from("<II", data, section_offset + 2)
    if actual_type != table_type:
        raise AssertionError((actual_type, table_type))
    on_disk = data[section_offset + 10:section_offset + 10 + payload_size]
    decoded = lzss_decompress(on_disk) if compression else on_disk
    record_size, remainder = divmod(len(decoded), count)
    if remainder:
        raise AssertionError((table_type, len(decoded), count))
    return {
        "section_offset": section_offset,
        "data_offset": section_offset + 10,
        "compression": compression,
        "count": count,
        "record_size": record_size,
        "records": [decoded[i * record_size:(i + 1) * record_size] for i in range(count)],
    }


def utf16_fixed(raw: bytes) -> str:
    return raw.decode("utf-16-le", errors="strict").split("\x00", 1)[0]


artifact = json.loads(ARTIFACT.read_text())

print("== direct NA category anchors ==")
na = next(item for item in artifact["regions"] if item["region"] == "NA")
na_data = (REPO / na["source"]["relative_path"]).read_bytes()
category = raw_section(na_data, 16)
check("NA category table is 2002 x 76 bytes",
      category["count"] == 2002 and category["record_size"] == 76)
for record_index, expected_name, expected_id in (
    (294, "EPS_P4DK3.ddb", 317),
    (496, "EPS_CAN_P4DK.ddb", 581),
):
    raw = category["records"][record_index]
    check(f"section-16 record {record_index} database name",
          utf16_fixed(raw[:40]) == expected_name)
    check(f"section-16 record {record_index} category id",
          struct.unpack_from("<H", raw, 68)[0] == expected_id)
    route = next(item for item in na["routes"] if item["database_name"] == expected_name)
    check(f"generated route {expected_name} retains exact category bytes",
          route["category"]["raw_hex"] == raw.hex())
    check(f"generated route {expected_name} retains exact file offset",
          route["category"]["on_disk_record_offset"]
          == category["data_offset"] + record_index * 76)

print("\n== every generated join points to exact source bytes ==")
for region in artifact["regions"]:
    source_path = REPO / region["source"]["relative_path"]
    data = source_path.read_bytes()
    check(f"{region['region']} source SHA-256",
          hashlib.sha256(data).hexdigest() == region["source"]["sha256"])
    tables = {table_type: raw_section(data, table_type) for table_type in (16, 19, 26, 27, 62, 88)}
    for route in region["routes"]:
        collections = (
            (16, [route["category"]]),
            (19, route["dlls"]),
            (26, route["functions"]),
            (27, route["function_details"]),
        )
        for table_type, records in collections:
            table = tables[table_type]
            for record in records:
                raw = table["records"][record["record_index"]]
                check(
                    f"{region['region']} {route['database_name']} type {table_type} "
                    f"record {record['record_index']}",
                    raw.hex() == record["raw_hex"]
                    and hashlib.sha256(raw).hexdigest() == record["raw_sha256"],
                )
        category_id = route["category"]["category_id"]
        check(f"{region['region']} {route['database_name']} DLL foreign keys",
              all(row["category_id"] == category_id for row in route["dlls"]))
        check(f"{region['region']} {route['database_name']} function foreign keys",
              all(row["category_id"] == category_id for row in route["functions"]))
        check(f"{region['region']} {route['database_name']} detail foreign keys",
              all(row["category_id"] == category_id for row in route["function_details"]))
        function_ids = {row["function_id"] for row in route["functions"]}
        check(f"{region['region']} {route['database_name']} detail function join",
              all(row["function_id"] in function_ids for row in route["function_details"]))
    for table_type, key in ((62, "communication_did_records"), (88, "communication_rid_records")):
        table = tables[table_type]
        check(f"{region['region']} complete type-{table_type} communication rows",
              len(region[key]) == table["count"]
              and all(table["records"][row["record_index"]].hex() == row["raw_hex"]
                      for row in region[key]))

print("\n== deterministic regeneration ==")
with tempfile.TemporaryDirectory() as temp_dir:
    rebuilt = Path(temp_dir) / "routes.json"
    proc = subprocess.run(
        [sys.executable, str(REPO / "tools/techstream/extract_toyota_master_routes.py"),
         "--output", str(rebuilt)], capture_output=True, text=True,
    )
    check("master-route generator succeeds", proc.returncode == 0, proc.stderr.strip())
    check("master-route regeneration is byte-identical",
          proc.returncode == 0 and rebuilt.read_bytes() == ARTIFACT.read_bytes())

check("communication tables remain an explicitly unresolved category join",
      any("no category-id field" in item for item in artifact["unresolved_joins"]))

print(f"\nResults: {passed} passed, {failed} failed")
raise SystemExit(1 if failed else 0)
