#!/usr/bin/env python3
"""Raw-CodeFlash proof for application Tx producer semantics (0x260, 0x262, and remaining PDUs).

Merged portable family module.
"""
from __future__ import annotations

import csv
import hashlib
import json
import struct
import sys
from pathlib import Path

ROOT = REPO = Path(__file__).resolve().parents[1]
CF = (ROOT / "firmware" / "RH850_P1M-E_CodeFlash.bin").read_bytes()
passed = failed = 0


def check(name, cond, detail=""):
    global passed, failed
    ok = bool(cond)
    passed += int(ok)
    failed += int(not ok)
    suffix = f" ({detail})" if detail else ""
    print(f"[{'PASS' if ok else 'FAIL'}] {name}{suffix}")

print("== TX 260 semantics ==")


MAP = REPO / "data" / "application_tx_map.csv"



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


print("\n== TX 262 semantics ==")


MAP = REPO / "data" / "application_tx_map.csv"
DBC_FACTS = REPO / "data/external/opendbc/toyota_dbc_facts.json"



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


print("\n== TX remaining semantics ==")


MAP = REPO / "data" / "application_tx_map.csv"
RX_MAP = REPO / "data" / "application_rx_map.csv"



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

print(f"\n== RESULT: {passed} passed, {failed} failed ==")
raise SystemExit(1 if failed else 0)
