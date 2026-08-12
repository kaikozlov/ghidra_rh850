#!/usr/bin/env python3
"""Independent checks for bounded Techstream/DBC application correlations."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
import re
import struct
import subprocess
import sys
import tempfile

import pefile

REPO = Path(__file__).resolve().parents[1]
ROOT = REPO / "Techstream/unpacked/toyota/Toyota Diagnostics/Techstream"
ARTIFACT = REPO / "data/generated/techstream_v18/application_interface_correlations.json"
GENERATOR = REPO / "tools/techstream/extract_application_interface_correlations.py"
RX_MAP = REPO / "data/application_rx_map.csv"
DBC = REPO / "REFERENCE/opendbc/opendbc/dbc/generator/toyota/toyota_secoc_pt.dbc"

if not ROOT.is_dir():
    print("[SKIP] pinned Techstream V18 tree is unavailable")
    raise SystemExit(77)

sys.path.insert(0, str(REPO / "tools/techstream"))
from parse_ddb import DDBParser  # noqa: E402

passed = failed = 0
oracle = "raw_bytes"


def check(name: str, condition: object, detail: str = "") -> None:
    global passed, failed
    ok = bool(condition)
    passed += int(ok)
    failed += int(not ok)
    suffix = f" ({detail})" if detail else ""
    print(f"[{'PASS' if ok else 'FAIL'}][{oracle}] {name}{suffix}")


def raw_section(data: bytes, table_type: int) -> tuple[int, list[bytes]]:
    offset = struct.unpack_from("<I", data, 0x24 + 4 * table_type)[0]
    actual_type, compression = struct.unpack_from("<BB", data, offset)
    count, payload_size = struct.unpack_from("<II", data, offset + 2)
    assert actual_type == table_type and compression == 0
    payload = data[offset + 10:offset + 10 + payload_size]
    size, remainder = divmod(payload_size, count)
    assert remainder == 0
    return size, [payload[i * size:(i + 1) * size] for i in range(count)]


def find_u16(records: list[bytes], offset: int, key: int) -> tuple[int, bytes]:
    hits = [(i, raw) for i, raw in enumerate(records) if struct.unpack_from("<H", raw, offset)[0] == key]
    assert len(hits) == 1, (offset, key, len(hits))
    return hits[0]


def pe_bytes(path: Path, va: int, size: int) -> bytes:
    pe = pefile.PE(str(path), fast_load=True)
    return pe.get_data(va - pe.OPTIONAL_HEADER.ImageBase, size)


artifact = json.loads(ARTIFACT.read_text())
parser = DDBParser()

print("== executable field consumers ==")
oracle = "instruction_semantics"
signal_info = ROOT / "bin/GetDatMonSignalInfoP5_DT.dll"
kgp = ROOT / "bin/KgpDataCtrl.dll"
for va, expected, label in (
    (0x10001852, "668b502a", "monitor +0x2A physical-data key"),
    (0x10001864, "680d020000", "physical-data kind 0x020D"),
    (0x1000189D, "668b510e", "physical-data +0x0E unit key"),
    (0x100018AF, "680f020000", "unit kind 0x020F"),
    (0x1000193A, "668b482c", "monitor +0x2C bit start"),
    (0x1000193E, "668b582e", "monitor +0x2E bit end"),
    (0x100019F8, "668b6a32", "monitor +0x32 pattern-display key"),
    (0x10001A0E, "680e020000", "pattern-display kind 0x020E"),
):
    actual = pe_bytes(signal_info, va, len(bytes.fromhex(expected)))
    check(label, actual == bytes.fromhex(expected), actual.hex())
for va, expected, label in (
    (0x10040F0B, "668b420c", "PhyData key is raw +0x0C"),
    (0x10040F7A, "6bc918", "PhyData record size is 24"),
    (0x1004F2FB, "668b4204", "Unit key is raw +0x04"),
    (0x1004F381, "6bc90c", "Unit record size is 12"),
    (0x1003FFDB, "668b420c", "PatDisp key is raw +0x0C"),
    (0x100400E8, "8b4204", "PatDisp secondary raw value is +0x04"),
    (0x1004016D, "6bc918", "PatDisp record size is 24"),
    (0x1003FE54, "8b02", "PatDisp display string index is raw +0x00"),
):
    actual = pe_bytes(kgp, va, len(bytes.fromhex(expected)))
    check(label, actual == bytes.fromhex(expected), actual.hex())

print("\n== source identities and EMPS_P5 monitor records ==")
oracle = "raw_bytes"
check("KgpDataCtrl identity", hashlib.sha256(kgp.read_bytes()).hexdigest() == artifact["artifacts"]["kgp_data_ctrl"]["sha256"])
check("P5 signal-info identity", hashlib.sha256(signal_info.read_bytes()).hexdigest() == artifact["artifacts"]["p5_signal_info"]["sha256"])
expected_names = {60: "Cooperation Control State", 402: "Command Value Torque", 403: "Control State Information"}
for region in ("NA", "EU", "JP"):
    ddb_path = ROOT / region / "DB/EMPS_P5.ddb"
    data = ddb_path.read_bytes()
    strings = parser.load_string_db(ROOT / region / "DB/M_English.ddb")
    generated_by_key = {
        item["monitor"]["key"]: item
        for key_rows in artifact["monitors"].values()
        for item in key_rows
        if item["region"] == region
    }
    check(f"{region} EMPS_P5 source identity", hashlib.sha256(data).hexdigest() == generated_by_key[402]["database_sha256"])
    size62, rec62 = raw_section(data, 62)
    size13, rec13 = raw_section(data, 13)
    size14, rec14 = raw_section(data, 14)
    size15, rec15 = raw_section(data, 15)
    check(f"{region} section 62 record size", size62 == 64)
    check(f"{region} section 13 record size", size13 == 24)
    check(f"{region} section 14 record size", size14 == 24)
    check(f"{region} section 15 record size", size15 == 12)
    for key, expected_name in expected_names.items():
        idx, raw = find_u16(rec62, 0x24, key)
        row = generated_by_key[key]
        check(f"{region} monitor {key} raw identity", raw.hex() == row["monitor"]["raw_hex"] and idx == row["monitor"]["record_index"])
        name_idx = struct.unpack_from("<I", raw, 0x18)[0]
        check(f"{region} monitor {key} name", strings.get_string(name_idx) == expected_name)
        check(f"{region} monitor {key} bit range", (struct.unpack_from("<H", raw, 0x2C)[0], struct.unpack_from("<H", raw, 0x2E)[0]) == (row["monitor"]["bit_start"], row["monitor"]["bit_end"]))
        phy_key = struct.unpack_from("<H", raw, 0x2A)[0]
        pidx, praw = find_u16(rec13, 0x0C, phy_key)
        unit_key = struct.unpack_from("<H", praw, 0x0E)[0]
        uidx, uraw = find_u16(rec15, 0x04, unit_key)
        unit_string_idx = struct.unpack_from("<I", uraw, 0)[0]
        unit = strings.get_string(unit_string_idx) if unit_string_idx else None
        check(f"{region} monitor {key} physical-data raw identity", pidx == row["physical_data"]["record_index"] and praw.hex() == row["physical_data"]["raw_hex"])
        check(f"{region} monitor {key} unit raw identity", uidx == row["unit"]["record_index"] and uraw.hex() == row["unit"]["raw_hex"])
        check(f"{region} monitor {key} unit resolution", unit == row["unit"]["text"])
    check(f"{region} Command Value Torque is exactly 16-bit", generated_by_key[402]["monitor"]["bit_width"] == 16)
    check(f"{region} Command Value Torque unit is Nm", generated_by_key[402]["unit"]["text"] == "Nm")
    check(f"{region} Control State Information is 16-bit unitless", generated_by_key[403]["monitor"]["bit_width"] == 16 and generated_by_key[403]["unit"]["text"] is None)

    # Pattern key 22 is consumer-proven at raw +0x0C, with the represented
    # value at raw +0x04 and display string index at raw +0x00.
    pattern_rows = []
    for i, raw in enumerate(rec14):
        if struct.unpack_from("<H", raw, 0x0C)[0] != 22:
            continue
        pattern_rows.append((i, struct.unpack_from("<I", raw, 0x04)[0], strings.get_string(struct.unpack_from("<I", raw, 0x00)[0])))
    check(
        f"{region} cooperation-control display pattern",
        pattern_rows == [(63, 0, "Cooperation Control"), (64, 1, "Other than Cooperation Control")],
        repr(pattern_rows),
    )

print("\n== master routing and firmware/DBC side ==")
for route in artifact["master_routes"]:
    check(f"{route['region']} EMPS category record", route["record_index"] == 374 and route["category_id"] == 405 and route["generation"] == 20)
    check(f"{route['region']} EMPS data-monitor DLL route", {d["dll_name"] for d in route["dlls"]} >= {"GetDatMonListP5_DT.dll", "GetDatMonSignalInfoP5_DT.dll"})
with RX_MAP.open(newline="", encoding="utf-8") as stream:
    signal61 = next(row for row in csv.DictReader(stream) if row.get("signal_id") == "61")
check("firmware signal61 is secured signed16 CAN 0x2E4", signal61["can_id"] == "0x2E4" and signal61["bit_length"] == "16" and signal61["signed"] == "1" and signal61["secoc_envelope"] == "yes")
dbc_text = DBC.read_text(encoding="utf-8")
check("public DBC independently has signed16 STEER_TORQUE_CMD", bool(re.search(r"SG_\s+STEER_TORQUE_CMD\s*:\s*15\|16@0-\s*\(1,0\)", dbc_text)))

print("\n== disposition and bounded negative ==")
cor = {row["id"]: row for row in artifact["correlations"]}
check("APP-COR-001 is accepted corroboration", cor["APP-COR-001"]["disposition"] == "accepted-corroboration")
check("APP-COR-002 remains ambiguous", cor["APP-COR-002"]["disposition"] == "ambiguous")
check("APP-COR-003 rejects direct CAN naming", cor["APP-COR-003"]["disposition"] == "rejected-direct-name")
neg = artifact["negative_search"]
check("monitor 402 has no consumer-proven related-table key hit", neg["monitor_402_related_hits"] == [])
check("monitor 403 has no consumer-proven related-table key hit", neg["monitor_403_related_hits"] == [])
check("monitor 60 has one behavior-data key hit", len(neg["monitor_60_related_hits"]) == 1 and neg["monitor_60_related_hits"][0]["table_type"] == 88 and neg["monitor_60_related_hits"][0]["resolved_name"] == "Cooperation Control State")
check("no target monitor has an exact-name active test", all(not hits for hits in neg["active_test_exact_name_hits"].values()))

print("\n== deterministic regeneration ==")
oracle = "generated_self_check"
with tempfile.TemporaryDirectory() as temp_dir:
    rebuilt = Path(temp_dir) / "correlations.json"
    proc = subprocess.run([sys.executable, str(GENERATOR), "--output", str(rebuilt)], capture_output=True, text=True)
    check("correlation generator succeeds", proc.returncode == 0, proc.stderr.strip())
    check("correlation regeneration is byte-identical", proc.returncode == 0 and rebuilt.read_bytes() == ARTIFACT.read_bytes())

print(f"\nResults: {passed} passed, {failed} failed")
raise SystemExit(1 if failed else 0)
