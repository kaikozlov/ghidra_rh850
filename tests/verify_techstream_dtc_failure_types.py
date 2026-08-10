#!/usr/bin/env python3
"""Verify Techstream P5 DTC failure-type decoding and U023A87 semantics."""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "tools" / "techstream"))

from generate_dtc_failure_types import build  # noqa: E402
from parse_ddb import DDBParser  # noqa: E402

DB_ROOT = REPO / "Techstream/unpacked/toyota/Toyota Diagnostics/Techstream/NA/DB"
ARTIFACT = REPO / "data/generated/techstream_v18/dtc_failure_types.json"

passed = failed = 0


def check(name: str, condition: object, detail: str = "") -> None:
    global passed, failed
    ok = bool(condition)
    passed += int(ok)
    failed += int(not ok)
    suffix = f" ({detail})" if detail else ""
    print(f"[{'PASS' if ok else 'FAIL'}] {name}{suffix}")


print("== deterministic artifact ==")
rebuilt = build(DB_ROOT)
committed = json.loads(ARTIFACT.read_text(encoding="utf-8"))
check("committed failure-type artifact equals rebuild", committed == rebuilt)
check("P5 section-65 corpus spans 131 databases", rebuilt["counts"]["databases_with_section65_68"] == 131)
check("corpus has 15564 nonempty records", rebuilt["counts"]["nonempty_records"] == 15564)

print("\n== section 65 field layout ==")
parser = DDBParser()
strings = parser.load_string_db(DB_ROOT / "M_English.ddb")
emps = parser.parse_ecu_db(DB_ROOT / "EMPS_P5.ddb")
entries = parser.extract_dtc_failure_entries(emps.sections[65])
u023a87 = next(entry for entry in entries if entry.code == "U023A87")
check("EMPS_P5 U023A87 packed value is C23A87", u023a87.packed_dtc == 0xC23A87)
check("EMPS_P5 U023A87 base is C23A", u023a87.base_dtc == 0xC23A)
check("EMPS_P5 U023A87 failure byte is 0x87", u023a87.failure_type == 0x87)
check("EMPS_P5 U023A87 is enabled", u023a87.enabled == 1)
check("EMPS_P5 base description resolves to image processing module A",
      strings.get_string(u023a87.description_string_index) == 'Lost Communication with Image Processing Module "A"')
check("EMPS_P5 failure description resolves exactly to Missing Message",
      strings.get_string(u023a87.failure_string_index) == "Missing Message")
check("canonical Missing Message string index is 64829", u023a87.failure_string_index == 64829)

print("\n== corpus-wide failure byte semantics ==")
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
enabled_87 = [row for row in records if row["code"] == "U023A87" and row["enabled"]]
check("there are 20 enabled U023A87 P5 records", len(enabled_87) == 20, str(len(enabled_87)))
check("every enabled U023A87 record has failure type 0x87", all(row["failure_type"] == "0x87" for row in enabled_87))
check("every enabled U023A87 record resolves failure text as Missing Message",
      all((row["failure_text"] or "").lower() == "missing message" for row in enabled_87))
check("EMPS_P5 is among enabled U023A87 records", any(row["database"] == "EMPS_P5.ddb" for row in enabled_87))
check("EMPS2_P5 is among enabled U023A87 records", any(row["database"] == "EMPS2_P5.ddb" for row in enabled_87))
check("PCS2_P5 is among enabled U023A87 records", any(row["database"] == "PCS2_P5.ddb" for row in enabled_87))

print(f"\n== RESULT: {passed} passed, {failed} failed ==")
if failed:
    raise SystemExit(1)
