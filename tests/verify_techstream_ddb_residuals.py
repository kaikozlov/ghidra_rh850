#!/usr/bin/env python3
"""Verify the bounded high-value residual audit of Techstream DDB schemas."""

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
sys.path.insert(0, str(REPO / "tools/techstream"))
from parse_ddb import (  # noqa: E402
    DDBParser,
    ECU_TABLE_CLASS_NAMES,
    MASTER_TABLE_CLASS_NAMES,
)

ROOT = REPO / "Techstream/unpacked/toyota/Toyota Diagnostics/Techstream"
BIN = ROOT / "bin"
FACTORY_ARTIFACT = REPO / "data/generated/techstream_v18/ddb_factory_table_map.json"

passed = 0
failed = 0
oracle = "identity_hash"


def check(name: str, condition: bool, detail: str = "") -> None:
    global passed, failed
    if condition:
        passed += 1
        print(f"[PASS][{oracle}] {name}" + (f" ({detail})" if detail else ""))
    else:
        failed += 1
        print(f"[FAIL][{oracle}] {name}" + (f" ({detail})" if detail else ""))


if not ROOT.exists():
    print("SKIP: ignored Techstream tree is not present")
    raise SystemExit(77)

parser = DDBParser()
security = ROOT / "NA/DB/Security_P4.ddb"
toyota = ROOT / "NA/DB/Toyota.ddb"
kgp = BIN / "KgpDataCtrl.dll"
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
check(
    "KgpDataCtrl.dll hash",
    hashlib.sha256(kgp.read_bytes()).hexdigest()
    == "e5235bc0c241c6a450fe461031eed0915675032b1db994bd54d98818fac88aa9",
)

kgp_pe = pefile.PE(str(kgp), fast_load=True)
kgp_pe.parse_data_directories(
    directories=[pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_EXPORT"]]
)
image_base = kgp_pe.OPTIONAL_HEADER.ImageBase
factory_body = kgp_pe.get_data(0x1001ECCB - image_base, 14551)
check(
    "format-2 table factory body pin",
    hashlib.sha256(factory_body).hexdigest()
    == "bc2b0b27e6e81abbea2b94ebc021ac9882466497e5b4c6c5bd5511557a45b996",
)
check("factory maps section 3 to CDbSupPidTable",
      ECU_TABLE_CLASS_NAMES[3] == "CDbSupPidTable")
check("factory maps section 7 to CDbDidTable",
      ECU_TABLE_CLASS_NAMES[7] == "CDbDidTable")
check("factory maps section 6 to CDbPidTable",
      ECU_TABLE_CLASS_NAMES[6] == "CDbPidTable")
check("factory maps section 10 to CDbFreezeTable",
      ECU_TABLE_CLASS_NAMES[10] == "CDbFreezeTable")

print("\n== independently derived factory maps ==")
oracle = "instruction_semantics"
factory_artifact = json.loads(FACTORY_ARTIFACT.read_text())
exports = {}
for symbol in kgp_pe.DIRECTORY_ENTRY_EXPORT.symbols:
    if not symbol.name:
        continue
    decorated = symbol.name.decode("ascii")
    if decorated.startswith("??0") and "@@QAE@EE@Z" in decorated:
        exports[image_base + symbol.address] = decorated[3:].split("@@", 1)[0]

def independent_factory_map(jump_table_va: int, maximum_type: int) -> dict[int, str]:
    raw_table = kgp_pe.get_data(jump_table_va - image_base, (maximum_type + 1) * 4)
    cases = struct.unpack("<" + "I" * (maximum_type + 1), raw_table)
    result = {}
    for table_type, case_va in enumerate(cases):
        body = kgp_pe.get_data(case_va - image_base, 0x80)
        targets = []
        for offset, opcode in enumerate(body[:-4]):
            if opcode != 0xE8:
                continue
            target = case_va + offset + 5 + struct.unpack_from("<i", body, offset + 1)[0]
            if target in exports:
                targets.append(exports[target])
        if targets:
            result[table_type] = targets[0]
    return result

raw_master_map = independent_factory_map(0x1001EB67, 0x58)
raw_ecu_map = independent_factory_map(0x100225A2, 0x96)
check("raw factories resolve all 89 format-1 and 151 format-2 cases",
      len(raw_master_map) == 89 and len(raw_ecu_map) == 151)
check("parser master names are a strict match to executable constructors",
      all(raw_master_map[key] == value for key, value in MASTER_TABLE_CLASS_NAMES.items()))
check("parser ECU names are a strict match to executable constructors",
      all(raw_ecu_map[key] == value for key, value in ECU_TABLE_CLASS_NAMES.items()))
artifact_maps = {
    factory["format_version"]: {
        row["table_type"]: row["class_name"]
        for row in factory["records"] if row["status"] == "constructed"
    }
    for factory in factory_artifact["factories"]
}
check("generated format-1 map equals independent executable walk",
      artifact_maps[1] == raw_master_map)
check("generated format-2 map equals independent executable walk",
      artifact_maps[2] == raw_ecu_map)
oracle = "generated_self_check"
with tempfile.TemporaryDirectory() as temp_dir:
    rebuilt_path = Path(temp_dir) / "factory.json"
    proc = subprocess.run(
        [sys.executable, str(REPO / "tools/techstream/extract_factory_table_map.py"),
         "--output", str(rebuilt_path)], capture_output=True, text=True,
    )
    check("factory-map generator succeeds", proc.returncode == 0, proc.stderr.strip())
    check("factory-map regeneration is byte-identical",
          proc.returncode == 0 and rebuilt_path.read_bytes() == FACTORY_ARTIFACT.read_bytes())

print("\n== Security_P4 structural audit ==")
oracle = "raw_bytes"
sec = parser.parse_ecu_db(security)
expected_types = {
    0, 1, 3, 4, 5, 6, 7, 10, 11, 12, 13, 14, 15, 16,
    35, 36, 37, 43, 44, 45, 46, 57, 58, 59,
}
check("Security_P4 complete section-type set", set(sec.sections) == expected_types)
check("Security_P4 section 3 is supported-PID metadata, not a DID table",
      ECU_TABLE_CLASS_NAMES[sec.sections[3].header.table_type]
      == "CDbSupPidTable")
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
master = parser.parse_master_db(toyota)
expected_master_types = {
    0, 2, 4, 5, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24,
    25, 26, 27, 28, 29, 32, 33, 34, 35, 36, 41, 42, 43, 44, 46, 47,
    48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 62, 63, 64,
    65, 68, 69, 72, 73, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85,
    86, 87, 88,
}
check("Toyota master structural parser covers all 67 NA sections",
      set(master.sections) == expected_master_types)
regional_masters = {
    region: parser.parse_master_db(ROOT / region / "DB/Toyota.ddb")
    for region in ("NA", "EU", "JP")
}
check("all three regional Toyota masters parse structurally",
      {region: len(db.sections) for region, db in regional_masters.items()}
      == {"NA": 67, "EU": 67, "JP": 76})
eu_section4 = regional_masters["EU"].sections[4]
try:
    _ = eu_section4.record_size
except ValueError as exc:
    check("compressed master payloads cannot masquerade as decoded records",
          "compressed" in str(exc))
else:
    check("compressed master payloads cannot masquerade as decoded records", False)
check("master factory identifies CAN, ECU, DLL, DID, and RID tables",
      {key: MASTER_TABLE_CLASS_NAMES[key] for key in (14, 16, 19, 26, 56, 62, 88)}
      == {
          14: "CDbCommInfoCanTable",
          16: "CDbEcuCategoryTable",
          19: "CDbDllTable",
          26: "CDbEcuFuncInfoTable",
          56: "CDbEcuDescriptionTable",
          62: "CDbCommDidDataTable",
          88: "CDbCommRidDataTable",
      })
check("Toyota master contains no exact Sienna calibration identifier",
      b"8965B4512000" not in toyota_bytes
      and "8965B4512000".encode("utf-16-le") not in toyota_bytes)
try:
    parser.parse_ecu_db(toyota)
except ValueError as exc:
    check("type-2 ECU API still rejects Toyota master schema",
          "expected ECU database" in str(exc))
else:
    check("type-2 ECU API still rejects Toyota master schema", False)

print(f"\n{passed} passed, {failed} failed")
raise SystemExit(1 if failed else 0)
