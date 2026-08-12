#!/usr/bin/env python3
"""Raw-CodeFlash proof for CAN 0x260 application Tx producer semantics.

This deliberately does not consume the Ghidra reference exporter as its oracle.
It pins the decisive RH850 instruction bytes, calibration constants, and the
curated role strings emitted by generate_application_tx_map.py.
"""
from __future__ import annotations

import csv
import hashlib
from pathlib import Path
import struct
import sys

REPO = Path(__file__).resolve().parents[1]
CF = (REPO / "firmware" / "RH850_P1M-E_CodeFlash.bin").read_bytes()
MAP = REPO / "data" / "application_tx_map.csv"

passed = failed = 0


def check(name: str, condition: object, detail: str = "") -> None:
    global passed, failed
    ok = bool(condition)
    passed += int(ok)
    failed += int(not ok)
    suffix = f" ({detail})" if detail else ""
    print(f"[{'PASS' if ok else 'FAIL'}] {name}{suffix}")


def u16(offset: int) -> int:
    return struct.unpack_from("<H", CF, offset)[0]


def sha(offset: int, size: int) -> str:
    return hashlib.sha256(CF[offset:offset + size]).hexdigest()


def b(offset: int, hex_bytes: str) -> bool:
    expected = bytes.fromhex(hex_bytes)
    return CF[offset:offset + len(expected)] == expected


print("== exact CAN 0x260 producer bodies ==")
expected_bodies = {
    (0x4B66C, 232): "2dbb743c6900c4894670aea1121cd4e192d6812ca5a69709c397d00f83395fec",
    (0x4B900, 10): "038db5b3d9f613a864878e90a8ac87ae58fb9d683dc5d7ea1f16233b47500e97",
    (0x4B976, 86): "c6b3274f64a22ed3b223ccf5d47d3a66bf8648a84cba118d6b5da6b307f022bc",
    (0x4B9CC, 10): "c8b13ae5a0c69ed6e511e070a27f3b58cad82103c0b9ada9416f993d13a929ff",
}
for (address, size), expected in expected_bodies.items():
    check(f"producer 0x{address:X} body identity", sha(address, size) == expected)

print("\n== signal 0: legacy STEER_OVERRIDE location is constant-clear ==")
check("init writes zero to upstream export byte FEBEAD33", b(0xBE02E, "f703"))
check("runtime command-export path writes zero to FEBEAD33", b(0xCB792, "f703"))
check(
    "snapshot copies FEBEAD33 into FEBEE830",
    b(0xBCD92, "a40f33f5b00b"),
)
check(
    "Tx producer copies FEBEE830 into FEBE8094",
    b(0x4B9CC, "840f3130440f94c87f00"),
)

print("\n== signals 3/4: operational-mode inhibit predicates ==")
check("0x4B66C masks system mode with 0xFF00", b(0x4B67E, "c10e00ff"))
check("signal-3 path tests mode 0x400", b(0x4B686, "010600fc"))
check("signal-3 path tests mode 0x500", b(0x4B6A0, "010600fb"))
check("signal-3 mode-0x500 path tests transition phase 0x11", b(0x4B6A6, "1306efff"))
check("signal-3 path masks shared status word to low nine bits", b(0x4B6AC, "ce96ff01"))
check("signal-3 predicate stores to FEBE8099", b(0x4B6B4, "449799c8"))
check("signal-4 path independently tests mode 0x400", b(0x4B6B8, "010600fc"))
check("signal-4 path tests mode 0x500 and transition phase", b(0x4B6BE, "010600fb") and b(0x4B6C4, "1306efff"))
check("signal-4 path additionally gates the byte at FEBE6738", b(0x4B6CA, "e069"))
check("signal-4 path masks the same low-nine-bit status word", b(0x4B6CE, "ce0eff01"))
check("signal-4 predicate stores to FEBE809A", b(0x4B6D6, "440f9ac8"))

print("\n== signal 1: composite initialization/validity flag ==")
check("three local validity fields are zero-tested", b(0x4B6DA, "e0618a15e059ea0de051ca0d"))
check("two snapshot statuses are compared against 0x22", b(0x4B6E6, "1106deff") and b(0x4B6EC, "1006deff"))
check("third status comparison feeds setfe", b(0x4B6F2, "0f06deffe29f0000"))
check("composite flag stores to FEBE8096", b(0x4B6FE, "449f96c8"))

print("\n== signal 6: selected sensor channel, scaled/clamped to +/-700 ==")
check("signal-6 source loads signed FEBE6680", b(0x4B70A, "240f80ae"))
check("signal-6 scales by 100/256", b(0x4B70E, "209e0001e10e6400f30ffc02"))
check("signal-6 clamp constants are +/-700", b(0x4B71C, "010644fd") and b(0x4B728, "0106bc02"))
check("signal-6 stores to FEBE810A", b(0x4B732, "640f0ac9"))
check(
    "sensor selector chooses between two signed channels when enable marker is 0x5A",
    b(0x47BF0, "840fd5d10106a6ffda0d240f8ac524f644b0609802941306a6fff20f240b640facc5"),
)

print("\n== signal 7: saturated signed steering-control difference/estimate ==")
check("C9CA8 subtracts reference/state inputs", b(0xC9CE8, "b609"))
check("C9CA8 applies +0x7FFF/-0x8000 saturation boundaries", b(0xC9CEA, "01060180") and b(0xC9CF6, "208e0080"))
check("C9CA8 stores saturated result at C0FC", b(0xC9D00, "649ffc08"))
check("command-export path copies C0FC into AE5C", b(0xCB84A, "240ffc08") and b(0xCB858, "640f5cf6"))

print("\n== signal 2: debounced steering-control consistency state ==")
check("C9B98 initializes C100 asserted", b(0xC9B9C, "010a") and b(0xC9BC6, "440f0009"))
check("C9D7C reads C100 and its debounce counter", b(0xC9D8C, "84e70109") and b(0xC9D90, "e4eff508"))
check("C9D7C computes an absolute difference through CB31A", b(0xC9DC2, "b03180ff5615"))
check("C9D7C stores updated C100/counter", b(0xC9DF2, "44e7000964eff408"))
check("consistency magnitude threshold is 524", u16(0x1BD1C) == 524, str(u16(0x1BD1C)))
check("debounce count threshold is 40", u16(0x1BD22) == 40, str(u16(0x1BD22)))

print("\n== signal 5: thresholded motor-feedback magnitude status ==")
check("status producer loads FEBEAFE0 and calls signed-absolute helper", b(0xBC9E0, "2437e0f7") and b(0xBC9F6, "80ffc4f0"))
check("threshold table base is literal 0xAEEF0", b(0xBC9E8, "3b06f0ee0a00"))
check("threshold enable marker is 0x5A", CF[0xAEEF0] == 0x5A)
check("upper/lower thresholds are 5120/2560", (u16(0xAEEF2), u16(0xAEEF4)) == (5120, 2560))
check("debounce threshold is zero in this calibration", u16(0xAEEF6) == 0)
check("BCA28 stores resulting state byte at B724", b(0xBCA6C, "8093"))
check("motor feedback helper reads 6D20/6D18 and calls lookup/interpolator", b(0x37F8E, "0435003cbfffcefe"))
check("motor feedback helper stores the resulting 16-bit estimate at 6DA8", b(0x37F96, "6457a8b5"))

print("\n== signal 8: motor-control-derived signed torque estimate ==")
check("signal-8 producer loads signed FEBE66F0", b(0x4B73C, "240ff0ae"))
check("signal-8 negates source then scales by 100/128", b(0x4B740, "209e80008009e40f4c02f30ffc02"))
check("signal-8 stores to FEBE8110", b(0x4B74E, "640f10c9"))

print("\n== curated map roles ==")
with MAP.open(newline="", encoding="utf-8") as stream:
    rows = {int(row["signal_id"]): row for row in csv.DictReader(stream) if row["tx_pdu_id"] == "0"}
expected_roles = {
    0: "constant-clear in recovered producer graph; public DBC location STEER_OVERRIDE",
    1: "composite initialization/validity flag; public DBC STEER_ANGLE_INITIALIZING",
    2: "debounced steering-control consistency status",
    3: "operational-mode/status inhibit A",
    4: "operational-mode/status inhibit B",
    5: "thresholded motor-feedback magnitude status",
    6: "scaled/clamped sensor torque; public DBC STEER_TORQUE_DRIVER",
    7: "saturated signed steering-control estimate; public DBC STEER_ANGLE",
    8: "scaled motor-feedback torque estimate; public DBC STEER_TORQUE_EPS",
}
check("CAN 0x260 map contains all ten signals", set(rows) == set(range(10)))
for sid, role in expected_roles.items():
    check(f"signal {sid} curated role is exact", rows[sid]["static_role"] == role, rows[sid]["static_role"])

print(f"\nSummary: {passed} passed, {failed} failed")
sys.exit(1 if failed else 0)
