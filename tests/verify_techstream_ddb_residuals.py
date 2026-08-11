#!/usr/bin/env python3
"""Verify the bounded high-value residual audit of Techstream DDB schemas."""

from __future__ import annotations

import hashlib
import struct
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "tools/techstream"))
from parse_ddb import DDBParser  # noqa: E402

ROOT = REPO / "Techstream/unpacked/toyota/Toyota Diagnostics/Techstream"

passed = 0
failed = 0


def check(name: str, condition: bool, detail: str = "") -> None:
    global passed, failed
    if condition:
        passed += 1
        print(f"[PASS] {name}" + (f" ({detail})" if detail else ""))
    else:
        failed += 1
        print(f"[FAIL] {name}" + (f" ({detail})" if detail else ""))


if not ROOT.exists():
    print("SKIP: ignored Techstream tree is not present")
    raise SystemExit(0)

parser = DDBParser()
security = ROOT / "NA/DB/Security_P4.ddb"
toyota = ROOT / "NA/DB/Toyota.ddb"
m_strings = parser.load_string_db(ROOT / "NA/DB/M_English.ddb")

print("== pinned residual-audit sources ==")
check(
    "Security_P4 hash",
    hashlib.sha256(security.read_bytes()).hexdigest()
    == "d642840c0899252b4404650aa4dd96da11bdacd4a48dc8c63e366979d681037e",
)
check(
    "Toyota.ddb hash",
    hashlib.sha256(toyota.read_bytes()).hexdigest()
    == "63ee18391421a7b02996eef282bc8ea3251889981d9cf9e1722e89f4952cb19e",
)

print("\n== Security_P4 structural audit ==")
sec = parser.parse_ecu_db(security)
expected_types = {
    0, 1, 3, 4, 5, 6, 7, 10, 11, 12, 13, 14, 15, 16,
    35, 36, 37, 43, 44, 45, 46, 57, 58, 59,
}
check("Security_P4 complete section-type set", set(sec.sections) == expected_types)
check("Security_P4 type 35 is one 28-byte record",
      sec.sections[35].header.record_count == 1 and sec.sections[35].record_size == 28)
check("Security_P4 type 37 is fifty 20-byte records",
      sec.sections[37].header.record_count == 50 and sec.sections[37].record_size == 20)

rec35 = sec.sections[35].raw_data[:28]
idx35 = struct.unpack_from("<I", rec35, 0)[0]
check("type 35 resolves to Security Alarm Operation",
      m_strings.get_string(idx35) == "Security Alarm Operation")

sec37 = sec.sections[37]
labels: list[str] = []
details: list[str] = []
for i in range(sec37.header.record_count):
    rec = sec37.raw_data[i * sec37.record_size:(i + 1) * sec37.record_size]
    name_idx, detail_idx = struct.unpack_from("<II", rec, 0)
    labels.append(m_strings.get_string(name_idx))
    details.append(m_strings.get_string(detail_idx))
check("type 37 begins with alarm-condition vocabulary",
      labels[:5] == [
          "Battery Desorption", "Hood Open", "Luggage Open",
          "Luggage Open, Hood Open", "Door Open",
      ])
check("type 37 details describe alarm conditions",
      any("alarm" in text.lower() for text in details if text))
resolved_security_text = "\n".join(text for text in labels + details if text).lower()
check("type 35/37 targeted vocabulary is not key-provisioning vocabulary",
      not any(token in resolved_security_text
              for token in ("safekey", "keypair", "seedvalue", "mcu id", "mack4", "macm1")))

print("\n== steering EPS/EMPS corpus residual inventory ==")
steering_files = sorted(
    p for p in ROOT.glob("*/DB/*.ddb")
    if p.name.upper().startswith(("EPS", "EMPS"))
)
union: set[int] = set()
parsed_count = 0
for path in steering_files:
    try:
        db = parser.parse_ecu_db(path)
    except ValueError:
        continue
    parsed_count += 1
    union.update(db.sections)
check("all 35 steering EPS/EMPS type-2 databases are parsed", parsed_count == 35)
check(
    "steering section-type union is explicit through type 91",
    sorted(union) == [
        0, 1, 2, 3, 5, 6, 7, 10, 11, 12, 13, 14, 15, 16, 18, 19,
        32, 38, 43, 44, 45, 46, 55, 57, 58, 59, 61, 62, 63, 65, 66,
        80, 87, 88, 90, 91,
    ],
)

print("\n== Toyota master database boundary ==")
toyota_bytes = toyota.read_bytes()
check("Toyota.ddb is distinct format type 1", toyota_bytes[8] == 0x01)
try:
    parser.parse_ecu_db(toyota)
except ValueError as exc:
    check("type-2 ECU parser rejects Toyota master schema", "expected ECU database" in str(exc))
else:
    check("type-2 ECU parser rejects Toyota master schema", False)
check("Toyota master database remains large separate schema", len(toyota_bytes) > 10_000_000)

print(f"\n{passed} passed, {failed} failed")
raise SystemExit(1 if failed else 0)
