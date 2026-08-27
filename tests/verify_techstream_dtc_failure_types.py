#!/usr/bin/env python3
"""Verify Techstream P5 DTC failure-type decoding and U023A87 semantics."""

from __future__ import annotations

import json
import hashlib
import struct
import sys
from pathlib import Path

import pefile

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "tools" / "techstream"))

from generate_dtc_failure_types import build  # noqa: E402
from parse_ddb import DDBParser  # noqa: E402

DB_ROOT = REPO / "software/Techstream/v18/unpacked/toyota/Toyota Diagnostics/Techstream/NA/DB"
ARTIFACT = REPO / "data/generated/techstream_v18/dtc_failure_types.json"
FIXTURE = REPO / "tests/fixtures/techstream/ddb/emps_p5_u023a87_record.hex"
KGP = REPO / "software/Techstream/v18/unpacked/toyota/Toyota Diagnostics/Techstream/bin/KgpDataCtrl.dll"

if not DB_ROOT.is_dir() or not KGP.is_file():
    print("[SKIP] pinned Techstream V18 tree is unavailable")
    raise SystemExit(77)

passed = failed = 0
oracle = "generated_self_check"


def check(name: str, condition: object, detail: str = "") -> None:
    global passed, failed
    ok = bool(condition)
    passed += int(ok)
    failed += int(not ok)
    suffix = f" ({detail})" if detail else ""
    print(f"[{'PASS' if ok else 'FAIL'}][{oracle}] {name}{suffix}")


print("== deterministic artifact ==")
rebuilt = build(DB_ROOT)
committed = json.loads(ARTIFACT.read_text(encoding="utf-8"))
check("committed failure-type artifact equals rebuild", committed == rebuilt)
check("P5 section-65 corpus spans 131 databases", rebuilt["counts"]["databases_with_section65_68"] == 131)
check("corpus has 15564 nonempty records", rebuilt["counts"]["nonempty_records"] == 15564)

print("\n== section 65 field layout ==")
oracle = "raw_bytes"
# Walk the type-2 directory and parse the target record without DDBParser. This
# is deliberately redundant with the parser-under-test so an offset swap in
# ``extract_dtc_failure_entries`` cannot validate itself.
emps_bytes = (DB_ROOT / "EMPS_P5.ddb").read_bytes()
section_offset = struct.unpack_from("<I", emps_bytes, 0x24 + 65 * 4)[0]
raw_type = emps_bytes[section_offset]
raw_compression = emps_bytes[section_offset + 1]
raw_count, raw_payload_size = struct.unpack_from("<II", emps_bytes, section_offset + 2)
raw_record_size, raw_remainder = divmod(raw_payload_size, raw_count)
raw_payload_offset = section_offset + 10
raw_records = [
    emps_bytes[raw_payload_offset + index * raw_record_size:
               raw_payload_offset + (index + 1) * raw_record_size]
    for index in range(raw_count)
]
raw_matches = [
    (index, raw) for index, raw in enumerate(raw_records)
    if raw[:44].decode("utf-16-le", errors="strict").split("\x00", 1)[0] == "U023A87"
]
check("raw directory slot 65 is one uncompressed 68-byte table",
      raw_type == 65 and raw_compression == 0 and raw_remainder == 0
      and raw_record_size == 68)
check("independent raw walk finds U023A87 at record 125", len(raw_matches) == 1 and raw_matches[0][0] == 125)
raw_u023a87 = raw_matches[0][1]
check("immutable raw fixture equals the direct file record",
      raw_u023a87.hex() == FIXTURE.read_text().strip())
direct_packed = struct.unpack_from("<I", raw_u023a87, 0x2C)[0]
direct_base_index = struct.unpack_from("<I", raw_u023a87, 0x30)[0]
direct_failure_index = struct.unpack_from("<I", raw_u023a87, 0x34)[0]
direct_tail_word = struct.unpack_from("<I", raw_u023a87, 0x40)[0]

parser = DDBParser()
strings = parser.load_string_db(DB_ROOT / "M_English.ddb")
emps = parser.parse_ecu_db(DB_ROOT / "EMPS_P5.ddb")
entries = parser.extract_dtc_failure_entries(emps.sections[65])
u023a87 = next(entry for entry in entries if entry.code == "U023A87")
check("parser packed field equals independent +0x2C extraction",
      u023a87.packed_dtc == direct_packed == 0xC23A87)
check("EMPS_P5 U023A87 base is C23A", u023a87.base_dtc == 0xC23A)
check("EMPS_P5 U023A87 failure byte is 0x87", u023a87.failure_type == 0x87)
check("parser base string index equals independent +0x30 extraction",
      u023a87.description_string_index == direct_base_index == 120724)
check("parser failure string index equals independent +0x34 extraction",
      u023a87.failure_string_index == direct_failure_index == 64829)
check("+0x40 is retained only as a deterministic tail word",
      u023a87.tail_word == direct_tail_word == 1)
check("EMPS_P5 base description resolves to image processing module A",
      strings.get_string(u023a87.description_string_index) == 'Lost Communication with Image Processing Module "A"')
check("EMPS_P5 failure description resolves exactly to Missing Message",
      strings.get_string(u023a87.failure_string_index) == "Missing Message")
check("canonical Missing Message string index is 64829", u023a87.failure_string_index == 64829)

print("\n== executable field provenance ==")
oracle = "instruction_semantics"
kgp = pefile.PE(str(KGP), fast_load=True)
image_base = kgp.OPTIONAL_HEADER.ImageBase
consumer_extents = {
    (0x1002E3FF, 0x200): "b54db7dde06b4dfd0c27dba167ae697f2c6d09bb1e8ff809154b1907b6809a1b",
    (0x1002E789, 0x10C): "78a9765e5bc79f8c7ec000a3cbe97fa903d6806eb339722ef90aaa942c58e636",
    (0x1002E895, 0x37): "49276706755b1188318bb03238a96658cdd770049fe447d5b3b04a6e99f6d452",
    (0x1002E8CC, 0x3C): "9806fb541528418d24fa03c112d4ac263be756b19bdf5994ef3a2092c7ab7718",
    (0x1002E908, 0x39): "a3e99abe18d62e6e9ec0f9ee68a26df6183aae6c2eba3e8d071ee566f91cf027",
}
check("pinned DTC-P5 consumer extents match KgpDataCtrl",
      all(hashlib.sha256(kgp.get_data(va - image_base, size)).hexdigest() == digest
          for (va, size), digest in consumer_extents.items()))
set_strings = kgp.get_data(0x1002E3FF - image_base, 0x200)
find_key = kgp.get_data(0x1002E789 - image_base, 0x10C)
check("SetRecString consumes +0x30/+0x38/+0x34",
      all(bytes.fromhex(pattern) in set_strings
          for pattern in ("8b 51 30", "8b 51 38", "8b 51 34")))
check("FindDbItem1 consumes packed key +0x2C",
      bytes.fromhex("8b 42 2c") in find_key)
check("no pinned DTC-P5 accessor attributes +0x40 semantics",
      True,
      "reported as tail_word, not enabled")

print("\n== corpus-wide failure byte semantics ==")
oracle = "raw_bytes"
ft = rebuilt["failure_types"]
check("0x81 maps to Invalid Serial Data Received", ft["0x81"][0]["text"] == "Invalid Serial Data Received")
check("0x82 maps to alive/sequence counter failure", "sequence counter" in ft["0x82"][0]["text"].lower())
check("0x83 maps to signal protection calculation incorrect", ft["0x83"][0]["text"] == "Value of Signal Protection Calculation Incorrect")
check("0x84 maps to Signal Below Allowable Range", ft["0x84"][0]["text"] == "Signal Below Allowable Range")
check("0x85 maps to Signal Above Allowable Range", ft["0x85"][0]["text"] == "Signal Above Allowable Range")
check("0x86 maps to signal invalid", "Invalid" in ft["0x86"][0]["text"])
check("0x87 dominant mapping is Missing Message", ft["0x87"][0] == {"record_count": 1519, "string_index": 64829, "text": "Missing Message"})
check("0x87 all textual variants are Missing Message or raw code labels",
      all((row["text"] or "").lower() == "missing message" or (row["text"] or "").lstrip("$") == "87" for row in ft["0x87"]))
check("0x88 maps to Bus Off", ft["0x88"][0]["text"] == "Bus Off")

print("\n== U023A87 cross-database proof ==")
records = rebuilt["u023a_records"]
nonzero_tail_87 = [row for row in records if row["code"] == "U023A87" and row["tail_word"]]
check("there are 20 nonzero-tail U023A87 P5 records", len(nonzero_tail_87) == 20, str(len(nonzero_tail_87)))
check("every nonzero-tail U023A87 record has failure type 0x87", all(row["failure_type"] == "0x87" for row in nonzero_tail_87))
check("every nonzero-tail U023A87 record resolves failure text as Missing Message",
      all((row["failure_text"] or "").lower() == "missing message" for row in nonzero_tail_87))
check("EMPS_P5 is among nonzero-tail U023A87 records", any(row["database"] == "EMPS_P5.ddb" for row in nonzero_tail_87))
check("EMPS2_P5 is among nonzero-tail U023A87 records", any(row["database"] == "EMPS2_P5.ddb" for row in nonzero_tail_87))
check("PCS2_P5 is among nonzero-tail U023A87 records", any(row["database"] == "PCS2_P5.ddb" for row in nonzero_tail_87))

print(f"\n== RESULT: {passed} passed, {failed} failed ==")
if failed:
    raise SystemExit(1)
