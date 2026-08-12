#!/usr/bin/env python3
"""Raw-CodeFlash proof for remaining normal application Tx semantics.

Covers CAN 0x351, 0x394, 0x4A3, and reasserts the already-bounded 0x4C8
constant/default behavior. Firmware-first structural roles only; no OEM names
are invented for packets absent from the pinned Toyota DBC corpus.
"""
from __future__ import annotations

import csv
import hashlib
from pathlib import Path
import sys

REPO = Path(__file__).resolve().parents[1]
CF = (REPO / "firmware" / "RH850_P1M-E_CodeFlash.bin").read_bytes()
MAP = REPO / "data" / "application_tx_map.csv"
RX_MAP = REPO / "data" / "application_rx_map.csv"

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


def sha(offset: int, size: int) -> str:
    return hashlib.sha256(CF[offset:offset + size]).hexdigest()


print("== exact remaining-Tx producer bodies ==")
expected_bodies = {
    (0x4B882, 34): "897ec99840a856831aaaed0e12cf2c9bbf23457701e7a833a5bec2ccf1ea9216",
    (0x4B8B6, 74): "2f6e1f487121e9daffe31c73f4b40013bed407e4660b8b62f04ed781a75ab22a",
    (0x4B7BA, 114): "dd046afdd6a747b9c6682b805a028642c163532a9cd97a6d3eba8156c1ba6195",
}
for (address, size), expected in expected_bodies.items():
    check(f"producer 0x{address:X} body identity", sha(address, size) == expected)

print("\n== CAN 0x351: plausibility-monitor status projection ==")
# The plausibility monitor writes its final boolean at FEBEB5F8; the application
# input snapshot copies that byte to FEBEE82B, and 0x4B82C filters/holds it.
check("plausibility monitor stores final status at FEBEB5F8", b(0xB9E8E, "840b"))
check("input snapshot copies FEBEB5F8 into FEBEE82B", b(0xBCD4A, "840ff9fdab0b"))
check("0x351 helper reads filtered previous status and FEBEE82B", b(0x4B82C, "8457b9c824f6e2c8a4972b30"))
check("0x351 helper uses seven-count hold threshold", CF[0x2FD84:0x2FD88] == bytes.fromhex("07000000"))
check("0x351 wrapper passes helper return directly to producer", b(0x4B8A8, "bfff84ff0a30bfffd4ff"))
# 0x4B882: gate = low two bits of FEBE673C nonzero AND FEBE80FB nonzero.
# When gated it forces status code 7 + flag 1; otherwise flag 0.
check("0x351 producer loads gate sources E673C/E80FB", b(0x4B882, "e49f3dafa40ffbc8"))
check("0x351 producer tests low-two-bit status", b(0x4B88A, "de9ae205"))
check("active gate forces status code 7 and flag 1", b(0x4B892, "0732010a"))
check("inactive gate clears override flag", b(0x4B898, "000a"))
check("0x351 producer stores code/flag into staging bytes", b(0x4B89A, "24f694c8a433a50b"))
# System input bit 0x8000 selects the 0x5A gate marker passed to 0x4BAE4.
check("system input bit 0x8000 controls gate marker", b(0x3BFC6, "dd360080b20520365a00") and b(0x3BFD0, "80ff14fb"))

print("\n== CAN 0x394: table-driven internal-state projection ==")
# FUN_50268 indexes a 5-byte tuple table with state * 5 and stores the tuple
# into FEBE8266/62/63/64/65 while storing the state itself at FEBE8258.
check("state lookup multiplies internal state by five", b(0x50406, "e1f60500"))
check("state lookup table base is exact 0x2A33C", b(0x5040A, "33063ca30200"))
check("tuple byte0 -> FEBE8266", b(0x50412, "6098449f66ca"))
check("tuple byte1 -> FEBE8262", b(0x50418, "6198449f62ca"))
check("tuple byte2 -> FEBE8263", b(0x5041E, "6298449f63ca"))
check("tuple byte3 -> FEBE8264", b(0x50424, "6398449f64ca"))
check("tuple byte4 -> FEBE8265", b(0x5042A, "6498") and b(0x50434, "8d9b"))
check("internal state -> FEBE8258", b(0x50430, "800b"))
expected_table = bytes.fromhex(
    "00 00 00 00 00 "
    "04 03 00 00 00 "
    "04 07 00 00 00 "
    "05 03 00 00 00 "
    "04 03 00 00 00 "
    "01 01 00 00 00 "
    "03 03 02 01 02 "
    "03 03 02 01 00 "
    "06 03 03 00 02 "
    "06 03 03 00 00 "
    "03 07 01 01 01 "
    "03 07 04 01 01 "
    "06 07 07 00 01 "
    "06 07 06 00 01 "
    "06 07 05 00 01 "
    "02 02 00 00 00 "
    "04 07 00 00 00"
)
check("17-entry five-byte state table is exact", CF[0x2A33C:0x2A33C + len(expected_table)] == expected_table)
# The 0x394 producer maps state into a coarse 2-bit class.
def state_class(state: int) -> int:
    u = (state - 1) & 0xFFFFFFFF
    if u > 3:
        if u == 4:
            return 1
        if u > 13:
            if u == 14:
                return 2
            if u != 15:
                return 0
    return 3

expected_classes = {0: 0, 5: 1, 15: 2, 17: 0}
expected_classes.update({state: 3 for state in range(1, 17) if state not in {5, 15}})
check("coarse state-class model matches exact valid/invalid partition",
      all(state_class(state) == expected for state, expected in expected_classes.items()))
check("producer contains 0/1/2/3 class constants", b(0x4B8CC, "000a") and b(0x4B8D0, "010a") and b(0x4B8D4, "020a") and b(0x4B8D8, "030a"))
check("tuple byte0 maps to signal40", b(0x4B8E0, "840f67caa60b"))
check("tuple byte4 maps to signal42", b(0x4B8E6, "a40f65caa90b"))
check("tuple bytes1/2/3 map to signals43/44/45", b(0x4B8EC, "840f63caaa0b") and b(0x4B8F2, "a40f63caab0b") and b(0x4B8F8, "840f65caad0b"))

print("\n== CAN 0x4A3: mixed steering telemetry and explicit Rx->Tx joins ==")
# Existing independently verified Rx map identifies E801C as CAN 0x025 signal
# 221 and E807C as CAN 0x64F signal 289. The new raw proof below pins their use
# and the exact Tx transformation; it does not use those OEM names as semantics.
with RX_MAP.open(newline="", encoding="utf-8") as stream:
    rx_rows = {int(row["signal_id"]): row for row in csv.DictReader(stream)}
check("Rx signal221 structural source is CAN 0x025 signed12 -> FEBE801C",
      rx_rows[221]["can_id"] == "0x25" and rx_rows[221]["bit_length"] == "12"
      and rx_rows[221]["signed"] == "1" and rx_rows[221]["dest"] == "0xFEBE801C")
check("Rx signal289 structural source is CAN 0x64F signed12 -> FEBE807C",
      rx_rows[289]["can_id"] == "0x64F" and rx_rows[289]["bit_length"] == "12"
      and rx_rows[289]["signed"] == "1" and rx_rows[289]["dest"] == "0xFEBE807C")
# 4703E computes E801C-E807C, saturates to signed16, stores E7CE6.
check("difference helper loads E801C and E807C", b(0x47046, "24371cc8") and b(0x4704A, "240f7cc8"))
check("difference helper subtracts and calls signed16 saturator", b(0x4706A, "a13182fffe24"))
check("difference helper stores result to FEBE7CE6", b(0x47070, "230f0200640fe6c4"))
# 4B7BA mirrors E801C in B1/B2.
check("0x4A3 producer loads signed E801C", b(0x4B7BE, "249f1cc8"))
check("0x4A3 B1 is E801C bits11:8", b(0x4B7E0, "1308880ac10e0f00b00b"))
check("0x4A3 B2 is E801C low byte", b(0x4B7D8, "b19b"))
# E7CE6 is clamped again to signed 12-bit [-2048,2047] and emitted in B3/B4.
check("delta is clamped with +2047/-2048 bounds", b(0x4B7C8, "203eff07") and b(0x4B7D0, "204600f8"))
check("0x4A3 producer invokes clamp helper 0x6F080", b(0x4B7EA, "82ff9638"))
check("0x4A3 B3/B4 store clamped delta high-nibble/low-byte", b(0x4B7FC, "1308880ab39bc10e0f00b20b"))
# B5 is a compact signed-byte conversion of existing 0x260 driver torque / 10.
check("0x4A3 B5 reads 0x260 driver-torque staging", b(0x4B7F6, "3b34"))
check("driver torque is divided by ten then sent through signed-byte saturator", b(0x4B808, "0a0ae137fc02e60081ff2cdd"))
check("converted driver torque stores to B5 staging", b(0x4B814, "030f010024f694c8") and b(0x4B81E, "b40b"))
# B6/B7 exactly mirror the 0x260 EPS torque staging word.
check("0x4A3 loads 0x260 EPS-torque staging", b(0x4B81C, "3e9c"))
check("0x4A3 B6/B7 split EPS torque high/low bytes", b(0x4B820, "1308880ab50bb69b"))
# B0 carries the 0x260 initialization/validity status plus fixed bit 5.
check("0x4A3 B0 ORs initialization/validity status with 0x20", b(0x4B7C6, "6208") and b(0x4B7DA, "810e2000") and b(0x4B7DE, "af0b"))

print("\n== CAN 0x4C8 remains constant/default-only ==")
check("0x4C8 packer writes constant 09 / zero / zero", b(0x4BC58, "090a440f0ad4") and b(0x4BC5E, "44070bd4") and b(0x4BC66, "6407d8d3"))
# Signal 57 remains absent from the packer and starts B4..B7 zero; the existing
# transmit verifier independently closes the pre/post-transform route.
check("0x4C8 initial B4..B7 are zero", CF[0x221DC + 31 + 4:0x221DC + 31 + 8] == bytes(4))

print("\n== curated remaining-Tx roles ==")
with MAP.open(newline="", encoding="utf-8") as stream:
    rows = {int(row["signal_id"]): row for row in csv.DictReader(stream)}
expected_roles = {
    38: "filtered plausibility-monitor status code; system-gated override=7",
    39: "system-gated plausibility-status override flag",
    40: "state-table tuple byte0",
    41: "coarse 1..16 internal-state class code",
    42: "state-table tuple byte4",
    43: "state-table tuple byte1",
    44: "state-table tuple byte2",
    45: "state-table tuple byte3",
    46: "initialization/validity flag OR 0x20",
    47: "CAN 0x025 signal221 signed12 mirror bits11:8",
    48: "CAN 0x025 signal221 signed12 mirror bits7:0",
    49: "clamped signed12 delta (CAN 0x025 s221 - CAN 0x64F s289) bits11:8",
    50: "clamped signed12 delta (CAN 0x025 s221 - CAN 0x64F s289) bits7:0",
    51: "signed-byte conversion of CAN 0x260 driver-torque staging / 10",
    52: "CAN 0x260 EPS-torque staging mirror high byte",
    53: "CAN 0x260 EPS-torque staging mirror low byte",
}
for sid, role in expected_roles.items():
    check(f"signal {sid} curated role is exact", rows[sid]["static_role"] == role, rows[sid]["static_role"])

print(f"\nSummary: {passed} passed, {failed} failed")
sys.exit(1 if failed else 0)
