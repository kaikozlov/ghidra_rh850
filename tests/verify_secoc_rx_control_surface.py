#!/usr/bin/env python3
"""Verify the six-profile SecOC downstream-role ledger from committed evidence."""
from __future__ import annotations

import csv
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CF = (ROOT / "firmware" / "RH850_P1M-E_CodeFlash.bin").read_bytes()
SURFACE = ROOT / "data" / "secoc_rx_control_surface.csv"
RXMAP = ROOT / "data" / "application_rx_map.csv"
passed = failed = 0


def check(name: str, condition: bool, detail: str = "") -> None:
    global passed, failed
    if condition:
        passed += 1
        print(f"[PASS] {name}")
    else:
        failed += 1
        print(f"[FAIL] {name}" + (f" ({detail})" if detail else ""))


def u16(off: int) -> int:
    return struct.unpack_from("<H", CF, off)[0]


def u32(off: int) -> int:
    return struct.unpack_from("<I", CF, off)[0]


with SURFACE.open(newline="", encoding="utf-8") as f:
    rows = list(csv.DictReader(f))
by_id = {int(r["can_id"], 0): r for r in rows}
expected_ids = [0x00F, 0x2E4, 0x131, 0x132, 0x090, 0x0D7]
expected_pdu = [11, 6, 26, 35, 46, 47]
expected_len = [8, 8, 8, 8, 32, 32]

print("== profile census ==")
check("surface has exactly six rows", len(rows) == 6)
check("surface CAN IDs are exact", list(by_id) == expected_ids, repr(list(by_id)))
check("exact role classes",
      [by_id[i]["role_class"] for i in expected_ids] == [
          "synchronization", "steering_command", "steering_command",
          "protected_snapshot", "steering_measurement_validity", "vehicle_speed_validity",
      ])
check("only 0x2E4 and 0x131 select command modes",
      {i for i, r in by_id.items() if r["command_mode"] != "none"} == {0x2E4, 0x131})
check("0x132 remains bounded snapshot negative", by_id[0x132]["evidence_grade"] == "bounded")

print("\n== firmware SecOC records ==")
records = [0x25970 + i * 0x50 for i in range(6)]
check("record IDs match ledger", [u16(a + 0x0A) for a in records] == expected_ids)
check("record PDU IDs match ledger", [u16(a + 0x34) for a in records] == expected_pdu)
check("record secured lengths match ledger", [u32(a + 0x3C) for a in records] == expected_len)
check("ledger PDU IDs match firmware", [int(by_id[i]["rx_pdu_id"]) for i in expected_ids] == expected_pdu)
check("ledger formats match firmware lengths",
      [by_id[i]["can_format"] for i in expected_ids] == ["classic"] * 4 + ["fd", "fd"])
check("all profiles transmit 28 CMAC bits", all(u16(a + 2) == 28 for a in records))

with RXMAP.open(newline="", encoding="utf-8") as f:
    rx_rows = list(csv.DictReader(f))
by_signal = {int(r["signal_id"]): r for r in rx_rows}
with (ROOT / "data" / "application_rx_signal_evidence.csv").open(newline="", encoding="utf-8") as f:
    evidence_rows = list(csv.DictReader(f))
by_evidence_signal = {int(r["signal_id"]): r for r in evidence_rows}

print("\n== protected steering commands ==")
check("0x2E4 request destination is FEBE7F98", int(by_signal[60]["dest"], 0) == 0xFEBE7F98)
check("0x2E4 torque destination is FEBE7F94", int(by_signal[61]["dest"], 0) == 0xFEBE7F94)
check("0x131 request2 destination is FEBE7FC5", int(by_signal[112]["dest"], 0) == 0xFEBE7FC5)
check("0x131 signed angle destination is FEBE7FBE", int(by_signal[114]["dest"], 0) == 0xFEBE7FBE)
check("0x131 angle ledger reaches C0D6/C144",
      "C0D6" in by_id[0x131]["derived_control_state"] and "FEBEC144" in by_id[0x131]["derived_control_state"])

print("\n== protected 0x090 measurement/validity domain ==")
check("0x090 three 10-bit raw signals are exact",
      [(int(by_signal[s]["dest"], 0), int(by_signal[s]["bit_length"])) for s in (270, 273, 276)] ==
      [(0xFEBE805A, 10), (0xFEBE805C, 10), (0xFEBE805E, 10)])
check("0x090 ledger pins normalized steering-cycle states",
      all(t in by_id[0x090]["derived_control_state"] for t in ("FEBEB6AA", "FEBEB714", "FEBEAE02", "FEBEAF00")))
check("0x090 ledger distinguishes prerequisite from command selection",
      "never selects C13A/C13D" in by_id[0x090]["downstream_effect"])

print("\n== protected 0x0D7 speed/status domain ==")
check("signal 283 is unsigned16 at FEBE8070",
      int(by_signal[283]["dest"], 0) == 0xFEBE8070
      and int(by_signal[283]["bit_length"]) == 16
      and int(by_signal[283]["signed"]) == 0)
check("signal 280 corrected destination is FEBE8076", int(by_signal[280]["dest"], 0) == 0xFEBE8076)
check("signal 284 independently owns FEBE8072", int(by_signal[284]["dest"], 0) == 0xFEBE8072)
check("signal 280 evidence marks generated stack persistence",
      "stack temporary" in by_evidence_signal[280]["classification_basis"])
check("signal 280 stack destination setup bytes",
      CF[0x4B402:0x4B40A] == bytes.fromhex("03f0230e0b000105"))
check("signal 280 persists stack byte to FEBE8076",
      CF[0x4B450:0x4B460] == bytes.fromhex("a30f0b0020361c0044ef7ac8440f76c8"))
check("0x0D7 ledger reaches named vehicle-speed state",
      "application_vehicle_speed_raw" in by_id[0x0D7]["derived_control_state"])
check("0x0D7 ledger records status/fault path", "B6396" in by_id[0x0D7]["derived_control_state"])

print(f"\nSummary: {passed} passed, {failed} failed")
raise SystemExit(1 if failed else 0)
