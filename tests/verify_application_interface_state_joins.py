#!/usr/bin/env python3
"""Independent raw-CodeFlash checks for cross-interface Rx->Tx state joins."""
from __future__ import annotations

import csv
from pathlib import Path
import sys

REPO = Path(__file__).resolve().parents[1]
CF = (REPO / "firmware" / "RH850_P1M-E_CodeFlash.bin").read_bytes()
RX = REPO / "data" / "application_rx_map.csv"
TX = REPO / "data" / "application_tx_map.csv"
JOINS = REPO / "data" / "application_interface_state_joins.csv"

passed = failed = 0


def check(name: str, condition: object, detail: str = "") -> None:
    global passed, failed
    ok = bool(condition)
    passed += int(ok)
    failed += int(not ok)
    suffix = f" ({detail})" if detail else ""
    print(f"[{'PASS' if ok else 'FAIL'}] {name}{suffix}")


def b(offset: int, hex_bytes: str) -> bool:
    expected = bytes.fromhex(hex_bytes)
    return CF[offset:offset + len(expected)] == expected


with RX.open(newline="", encoding="utf-8") as stream:
    rx = {int(r["signal_id"]): r for r in csv.DictReader(stream) if r["row_kind"] == "signal"}
with TX.open(newline="", encoding="utf-8") as stream:
    tx = {int(r["signal_id"]): r for r in csv.DictReader(stream)}
with JOINS.open(newline="", encoding="utf-8") as stream:
    joins = list(csv.DictReader(stream))

print("== curated join artifact ==")
check("exact three interface joins", [r["join_id"] for r in joins] == ["APP-JOIN-001", "APP-JOIN-002", "APP-JOIN-003"])
check("0x025 signal221 is signed12 -> FEBE801C", rx[221]["can_id"] == "0x25" and rx[221]["signed"] == "1" and rx[221]["bit_length"] == "12" and rx[221]["dest"] == "0xFEBE801C")
check("0x64F signal289 is signed12 -> FEBE807C", rx[289]["can_id"] == "0x64F" and rx[289]["signed"] == "1" and rx[289]["bit_length"] == "12" and rx[289]["dest"] == "0xFEBE807C")
check("0x2E4 signal61 is authenticated signed16 -> FEBE7F94", rx[61]["can_id"] == "0x2E4" and rx[61]["secoc_envelope"] == "yes" and rx[61]["signed"] == "1" and rx[61]["bit_length"] == "16" and rx[61]["dest"] == "0xFEBE7F94")
check("0x262 signal25 is LKA_STATE bit4", tx[25]["can_id"] == "0x262" and tx[25]["wire_field"] == "B3[5]" and tx[25]["static_role"].startswith("LKA_STATE bit4"))

print("\n== APP-JOIN-001/002: incoming steering fields -> CAN 0x4A3 ==")
check("difference helper loads 0x025 s221 and 0x64F s289", b(0x47046, "24371cc8") and b(0x4704A, "240f7cc8"))
check("difference helper subtracts and saturates", b(0x4706A, "a13182fffe24") and b(0x47070, "230f0200640fe6c4"))
check("0x4A3 producer directly reloads s221", b(0x4B7BE, "249f1cc8"))
check("0x4A3 emits s221 high nibble/low byte", b(0x4B7D8, "b19b") and b(0x4B7E0, "1308880ac10e0f00b00b"))
check("0x4A3 reloads and clamps the difference", b(0x4B7C8, "203eff07") and b(0x4B7D0, "204600f8") and b(0x4B7EA, "82ff9638"))
check("0x4A3 emits difference high nibble/low byte", b(0x4B7FC, "1308880ab39bc10e0f00b20b"))

print("\n== APP-JOIN-003: authenticated 0x2E4 torque -> LKA_STATE bit4 ==")
# application_rx_signal_consumer_56fc2 copies the signed command from the COM
# destination into the application mirror FEBEF184.
check("consumer loads 0x2E4 signal61 destination", b(0x57138, "240f94c7"))
check("consumer stores signal61 into FEBEF184", b(0x57148, "640f8439"))
# system-mode snapshot scales that mirror by 0x100/100 through CBB74 and stores
# the saturated result into FEBEAE20.
check("snapshot loads FEBEF184 and sets scale numerator/denominator", b(0xBA4B8, "24378439203e000120466400"))
check("snapshot calls signed saturating scaler CBB74", b(0xBA4C4, "234e380081ffac16"))
check("CBB74 performs multiply/divide and signed16 saturation", b(0xCBB84, "e7372002e837fc02") and b(0xCBB8C, "0606ff7f") and b(0xCBB9C, "200e0080") and b(0xCBBAE, "8034"))
check("snapshot stores scaled command into FEBEAE20", b(0xBA804, "230f3800640f20f6"))
# AE20 is consumed by both the torque clamp/gain path and the command-state
# discriminator C8072. C8072 eventually writes boolean BF74.
check("torque clamp/gain reads FEBEAE20", b(0xC8546, "249f20f6"))
check("command-state discriminator reads FEBEAE20", b(0xC8076, "24c720f6"))
check("command-state discriminator writes BF74", b(0xC81D6, "440f7407"))
# BF74 is ORed with a companion status into BF7B.
check("BF74/BF7A aggregate into BF7B", b(0xC8280, "840f7507610ae205840f7b07610ae20f0000440f7b07"))
# steering_command_export_scale moves BF7B into ACF6; application snapshot moves
# ACF6 into E844; Tx staging maps E844 to signal25 / B3[5].
check("BF7B is exported into ACF6", b(0xCB77C, "a40f7b07") and b(0xCB788, "ba0b"))
check("ACF6 is snapshotted into E844", b(0xBCE40, "840ff7f4c40b"))
check("E844 is staged into 0x262 signal25", b(0x4B948, "840f453024f694c897538f0b"))
check("0x262 packer consumes signal25 staging", b(0x4BE7E, "6f08") and b(0x4BE84, "440fe7d3"))

print("\n== MAC-result direct-export boundary ==")
# The live-project assertion pins the complete reference set for FEBE555C. Raw
# bytes here pin the only application-level branch that consumes the result.
check("SecOC Gate-2 reads MAC result at 0x8E69E", b(0x8E69E, "840f5d9d"))
check("MAC-result branch remains inside SecOC acceptance function", b(0x8E6A2, "e009e10f14d3"))

print(f"\nSummary: {passed} passed, {failed} failed")
sys.exit(1 if failed else 0)
