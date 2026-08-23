#!/usr/bin/env python3
"""Raw-CodeFlash proof for CAN 0x262 / EPS_STATUS producer semantics."""
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
import sys

REPO = Path(__file__).resolve().parents[1]
CF = (REPO / "firmware" / "RH850_P1M-E_CodeFlash.bin").read_bytes()
MAP = REPO / "data" / "application_tx_map.csv"
DBC_FACTS = REPO / "data/external/opendbc/toyota_dbc_facts.json"

passed = failed = 0


def check(name: str, condition: object, detail: str = "") -> None:
    global passed, failed
    ok = bool(condition)
    passed += int(ok)
    failed += int(not ok)
    suffix = f" ({detail})" if detail else ""
    print(f"[{'PASS' if ok else 'FAIL'}] {name}{suffix}")


def sha(offset: int, size: int) -> str:
    return hashlib.sha256(CF[offset:offset + size]).hexdigest()


def b(offset: int, hex_bytes: str) -> bool:
    expected = bytes.fromhex(hex_bytes)
    return CF[offset:offset + len(expected)] == expected


print("== exact EPS_STATUS producer bodies ==")
expected_bodies = {
    (0x4B754, 90): "5ae6553eb3dc2de46a7e1471f28be9e5f7978766dd4d182b5af8efc9223e2b6e",
    (0x4B90A, 22): "d283d778d5d4d19ca5dded0e5df8de3acf04e6a3bc03ef6862e10157d42e68b7",
    (0x4B920, 12): "10fdaad0ab535a37e4254308d14c3781429d682c0d3795d6df8e8fdda12f722d",
    (0x4B93C, 46): "355bbe83a98b1d4487f93387c4fff5da82879f9a20446e0c6696f1e801bf90f9",
    (0x4B976, 86): "c6b3274f64a22ed3b223ccf5d47d3a66bf8648a84cba118d6b5da6b307f022bc",
}
for (address, size), expected in expected_bodies.items():
    check(f"producer 0x{address:X} body identity", sha(address, size) == expected)

print("\n== public DBC field geometry is only corroboration ==")
facts = json.loads(DBC_FACTS.read_text(encoding="utf-8"))
eps = facts["messages"]["EPS_STATUS"]
check("pinned DBC fact has EPS_STATUS CAN 0x262", eps["can_id_decimal"] == 610 and eps["length"] == 8)
check("DBC IPAS_STATE is B0 low nibble", eps["signals"]["IPAS_STATE"] == {"start_bit_motorola": 3, "bit_length": 4, "signed": False})
check("DBC LTA_STATE is B1[7:3]", eps["signals"]["LTA_STATE"] == {"start_bit_motorola": 15, "bit_length": 5, "signed": False})
check("DBC TYPE is B3[0]", eps["signals"]["TYPE"] == {"start_bit_motorola": 24, "bit_length": 1, "signed": False})
check("DBC LKA_STATE is B3[7:1]", eps["signals"]["LKA_STATE"] == {"start_bit_motorola": 31, "bit_length": 7, "signed": False})

print("\n== byte 0 / IPAS_STATE is runtime-zero in this calibration ==")
# 0x4B90A uses ep=FEBE8094 and clears offsets 8,9,0x20,0xA..0xE.
# Those are signals 10,12,11,14,15,16,23,24 respectively.
check(
    "0x4B90A clears all six RAM-backed B0 fields",
    b(0x4B90A, "24f694c888038903a0038a038b038c03"),
)
check("0x4B90A also clears the two high LKA bits", b(0x4B91A, "8d038e03"))

print("\n== LTA_STATE is a five-bit internal steering-status aggregate ==")
# 0x4B976 maps snapshot bytes E834,E833,E832,E835,E838 into B1[7:3].
check("LTA bit4 E834 -> B1[7]", b(0x4B97A, "840f3530") and b(0x4B986, "900b"))
check("LTA bit3 E833 -> B1[6]", b(0x4B988, "a40f3330") and b(0x4B98C, "920b"))
check("LTA bit2 E832 -> B1[5]", b(0x4B98E, "840f3330") and b(0x4B992, "940b"))
check("LTA bit1 E835 -> B1[4]", b(0x4B994, "a40f3530") and b(0x4B998, "960b"))
check("LTA bit0 E838 passes through marker gate helper", b(0x4B982, "84373930") and b(0x4B99A, "bfff92ff"))
check(
    "marker gate zeroes source when FEBE7426 equals 0x5A",
    b(0x4B92C, "8600840f27bc0106a6ffe03704537f00"),
)
# Upstream internal states exported into AD42..AD46: C12E,C0E2,C0E3,C12F,C130.
check("LTA bit4 is OR of two internal status flags", b(0xC9E90, "a40f2909a49f3109610ac205619ae20f0000440f2e09"))
check("LTA active-state bit is maintained by the C9A1E state machine", b(0xC9AA4, "449fe308") and b(0xC9AB0, "4497e208"))
check("C9A1E state transitions carry 0x11/0x44/0x22 markers", b(0xC9A70, "208e1100") and b(0xC9A7E, "208e4400") and b(0xC9A8A, "208e2200"))
check("LTA bit1 ORs three internal condition flags", b(0xC9EC4, "a4972b09a49f2d09840f2d09") and b(0xC9EDE, "440f2f09"))
check("LTA base bit requires source==1 and low nine status bits clear", b(0xC9EA8, "8497bff4e49ffdf5000a6192da05d306ff01e20f0000440f3009"))

print("\n== LKA_STATE is a seven-bit field with only five dynamic low bits ==")
# B3[7:6] are zeroed above. B3[5:1] come from E844/E841/E842/E82E/E843;
# B3[0] TYPE is independently zeroed by 0x4B754.
check("LKA bit4 E844 -> B3[5]", b(0x4B948, "840f4530") and b(0x4B952, "8f0b"))
check("LKA bit3 E841 -> B3[4]", b(0x4B954, "a40f4130") and b(0x4B958, "910b"))
check("LKA bit2 E842 -> B3[3]", b(0x4B95A, "840f4330") and b(0x4B95E, "930b"))
check("LKA bit1 E82E -> B3[2]", b(0x4B960, "840f2f30") and b(0x4B964, "950b"))
check("LKA bit0 E843 uses the same marker gate helper", b(0x4B940, "a4374330") and b(0x4B944, "bfffe8ff") and b(0x4B950, "9753"))
check("public TYPE bit B3[0] is zeroed by runtime producer", b(0x4B7A4, "9903"))
# Internal LKA-state source structure.
check("LKA bit4 upstream BF7B is OR of BF74/BF7A", b(0xC8280, "840f7507610ae205840f7b07610ae20f0000440f7b07"))
check("LKA bit1 BFA5 has explicit set and clear stores", b(0xC8380, "4407a507") and b(0xC8392, "440fa507"))
check("LKA active/recovery latches BFA6/BFA7 are separately updated", b(0xC846A, "449fa607") and b(0xC845A, "440fa707") and b(0xC8498, "4407a707"))
check("LKA base bit BFA9 uses same source/low-nine-bit predicate as LTA base", b(0xC8690, "8497bff4e49ffdf5000a6192da05d306ff01e20f0000440fa907"))

print("\n== proprietary B4 status + constant trailer bytes ==")
# B4 high fields are exported from C0D8,C0D9,C0FE,C0FF.
check("B4 threshold/limiter flags are written by C96D2", b(0xC9778, "44dfd808") and b(0xC977C, "4497d908"))
check("B4 transition latch/code are written by C9CA8", b(0xC9D5C, "44dffe08") and b(0xC9D60, "44e7ff08"))
check("B5/B6 runtime producer writes 0xFF", b(0x4B920, "1f0a24f694c89e0b9f0b7f00"))

print("\n== curated EPS_STATUS map roles ==")
with MAP.open(newline="", encoding="utf-8") as stream:
    rows = {int(row["signal_id"]): row for row in csv.DictReader(stream) if row["tx_pdu_id"] == "1"}
expected_roles = {
    10: "constant-zero EPS_STATUS prefix bit",
    11: "constant-zero EPS_STATUS prefix bit",
    12: "constant-zero EPS_STATUS prefix bit",
    13: "constant zero",
    14: "IPAS_STATE bit2; constant zero in runtime producer",
    15: "IPAS_STATE bit1; constant zero in runtime producer",
    16: "IPAS_STATE bit0; constant zero in runtime producer",
    17: "LTA_STATE bit4; internal status aggregate",
    18: "LTA_STATE bit3; timeout/recovery status",
    19: "LTA_STATE bit2; active-state latch",
    20: "LTA_STATE bit1; multi-condition status aggregate",
    21: "LTA_STATE bit0; gated base-eligibility status",
    22: "constant zero 11-bit field",
    23: "LKA_STATE bit6; constant zero in runtime producer",
    24: "LKA_STATE bit5; constant zero in runtime producer",
    25: "LKA_STATE bit4; internal status aggregate",
    26: "LKA_STATE bit3; transient recovery latch",
    27: "LKA_STATE bit2; active-state latch",
    28: "LKA_STATE bit1; timeout/availability status",
    29: "LKA_STATE bit0; gated base-eligibility status",
    30: "TYPE; constant zero in runtime producer",
    31: "steering-control threshold status",
    32: "steering-control limiter status",
    33: "steering-control transition latch",
    34: "steering-control transition code",
    35: "constant 0xFF byte in runtime producer",
    36: "constant 0xFF byte in runtime producer",
}
check("CAN 0x262 map contains all 28 signals", set(rows) == set(range(10, 38)))
for sid, role in expected_roles.items():
    check(f"signal {sid} curated role is exact", rows[sid]["static_role"] == role, rows[sid]["static_role"])

print(f"\nSummary: {passed} passed, {failed} failed")
sys.exit(1 if failed else 0)
