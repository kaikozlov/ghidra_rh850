#!/usr/bin/env python3
"""Independently verify priority steering DDB fields and raw preservation."""

from __future__ import annotations

import hashlib
import json
import struct
import subprocess
import sys
import tempfile
from pathlib import Path

import pefile

REPO = Path(__file__).resolve().parents[1]
ROOT = REPO / "software/Techstream/v18/unpacked/toyota/Toyota Diagnostics/Techstream"
ARTIFACT = REPO / "data/generated/techstream_v18/priority_steering_ddb_semantics.json"

if not ROOT.is_dir():
    print("[SKIP] pinned Techstream V18 tree is unavailable")
    raise SystemExit(77)

passed = failed = 0
oracle = "identity_hash"


def check(name: str, condition: object, detail: str = "") -> None:
    global passed, failed
    ok = bool(condition)
    passed += int(ok)
    failed += int(not ok)
    print(f"[{'PASS' if ok else 'FAIL'}][{oracle}] {name}" + (f" ({detail})" if detail else ""))


def raw_section(data: bytes, table_type: int) -> tuple[int, list[bytes]]:
    section_offset = struct.unpack_from("<I", data, 0x24 + table_type * 4)[0]
    actual_type, compression = struct.unpack_from("<BB", data, section_offset)
    count, payload_size = struct.unpack_from("<II", data, section_offset + 2)
    assert actual_type == table_type and compression == 0
    payload = data[section_offset + 10:section_offset + 10 + payload_size]
    record_size, remainder = divmod(payload_size, count)
    assert remainder == 0
    return record_size, [payload[i * record_size:(i + 1) * record_size] for i in range(count)]


def decode_field(raw: bytes, spec: dict) -> int | str:
    offset, width = spec["offset"], spec["width"]
    value = raw[offset:offset + width]
    if spec.get("encoding") == "UTF-16LE":
        return value.decode("utf-16-le", errors="strict").split("\x00", 1)[0]
    return int.from_bytes(value, "little")


artifact = json.loads(ARTIFACT.read_text())

print("== executable consumer identities ==")
pe_path = REPO / artifact["artifact"]["relative_path"]
pe_bytes = pe_path.read_bytes()
check("KgpDataCtrl artifact identity",
      hashlib.sha256(pe_bytes).hexdigest() == artifact["artifact"]["sha256"])
pe = pefile.PE(data=pe_bytes, fast_load=True)
image_base = pe.OPTIONAL_HEADER.ImageBase
for table_type, schema in artifact["schemas"].items():
    for consumer in schema["consumers"]:
        va = int(consumer["va"], 16)
        prefix = pe.get_data(va - image_base, 64)
        check(f"type {table_type} consumer {consumer['method']}",
              hashlib.sha256(prefix).hexdigest() == consumer["prefix_sha256"])

# Prefix identities only pin which methods were inspected.  These exact x86
# operand bytes independently pin the load-bearing record offsets used by the
# priority monitor/behavior field claims.
oracle = "instruction_semantics"
field_loads = {
    0x10041DDB: bytes.fromhex("8a4202"),       # type 6: byte +0x02
    0x100287CB: bytes.fromhex("668b4224"),     # type 62: word +0x24
    0x1002851D: bytes.fromhex("668b5130"),     # type 62: word +0x30 lhs
    0x1002852C: bytes.fromhex("668b4830"),     # type 62: word +0x30 rhs
    0x100085CD: bytes.fromhex("668b512e"),     # type 88: word +0x2e lhs
    0x100085DC: bytes.fromhex("668b482e"),     # type 88: word +0x2e rhs
    0x10028643: bytes.fromhex("8b4218"),       # type 62: dword +0x18
    0x10025642: bytes.fromhex("668b4802"),     # type 63: word +0x02
}
for va, expected in field_loads.items():
    actual = pe.get_data(va - image_base, len(expected))
    check(f"field consumer operand at {va:#x}", actual == expected, actual.hex())

print("\n== raw records and field offsets ==")
oracle = "raw_bytes"
section_instances = decoded_records = 0
for source in artifact["sources"]:
    path = ROOT / source["relative_path"]
    data = path.read_bytes()
    check(f"{source['relative_path']} source identity",
          hashlib.sha256(data).hexdigest() == source["sha256"])
    for table_type_text, generated in source["sections"].items():
        table_type = int(table_type_text)
        schema = artifact["schemas"][table_type_text]
        record_size, records = raw_section(data, table_type)
        section_instances += 1
        decoded_records += len(records)
        check(f"{source['relative_path']} type {table_type} shape",
              record_size == schema["record_size"] == generated["record_size"]
              and len(records) == generated["record_count"] == len(generated["records"]))
        check(f"{source['relative_path']} type {table_type} payload identity",
              hashlib.sha256(b"".join(records)).hexdigest() == generated["payload_sha256"])
        for record, expected in zip(records, generated["records"]):
            if record.hex() != expected["raw_hex"]:
                check(f"{source['relative_path']} type {table_type} raw records", False)
                break
            for field_name, field_spec in schema["fields"].items():
                if decode_field(record, field_spec) != expected["fields"][field_name]:
                    check(
                        f"{source['relative_path']} type {table_type} field {field_name}",
                        False,
                        f"record={expected['record_index']}",
                    )
                    break
        else:
            check(f"{source['relative_path']} type {table_type} raw fields", True)

check("summary section-instance count is independently reproduced",
      section_instances == artifact["summary"]["section_instances"] == 76)
check("summary decoded-record count is independently reproduced",
      decoded_records == artifact["summary"]["decoded_records"] == 6521)
check("32 steering files carry at least one priority section",
      len(artifact["sources"]) == artifact["summary"]["steering_files_with_priority_sections"] == 32)
check("every schema explicitly preserves unknown bytes",
      all(schema["unknown_bytes_policy"] == "complete raw_hex retained per record"
          for schema in artifact["schemas"].values()))

print("\n== deterministic regeneration ==")
oracle = "generated_self_check"
with tempfile.TemporaryDirectory() as temp_dir:
    rebuilt = Path(temp_dir) / "priority.json"
    proc = subprocess.run(
        [sys.executable, str(REPO / "tools/techstream/extract_priority_ddb_semantics.py"),
         "--output", str(rebuilt)], capture_output=True, text=True,
    )
    check("priority semantics generator succeeds", proc.returncode == 0, proc.stderr.strip())
    check("priority semantics regeneration is byte-identical",
          proc.returncode == 0 and rebuilt.read_bytes() == ARTIFACT.read_bytes())

print(f"\nResults: {passed} passed, {failed} failed")
raise SystemExit(1 if failed else 0)
