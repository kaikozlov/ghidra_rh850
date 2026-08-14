#!/usr/bin/env python3
"""Verify the application ICU-S initialization and authenticated key-update path."""
from __future__ import annotations

import struct
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
CF = (REPO / "firmware" / "RH850_P1M-E_CodeFlash.bin").read_bytes()
passed = failed = 0


def check(name: str, condition: bool, detail: str = "") -> None:
    global passed, failed
    if condition:
        passed += 1
        print(f"PASS: {name}")
    else:
        failed += 1
        suffix = f" ({detail})" if detail else ""
        print(f"FAIL: {name}{suffix}")


def u16(address: int) -> int:
    return struct.unpack_from("<H", CF, address)[0]


def u32(address: int) -> int:
    return struct.unpack_from("<I", CF, address)[0]


print("== ICU-S application initialization ==")
check(
    "application startup calls crypto/ICU initializer 0x88C4C",
    CF[0x6566A:0x6566E] == bytes.fromhex("82ffe235"),
    CF[0x6566A:0x6566E].hex(),
)
check(
    "crypto initializer calls ICU wrapper 0x86DB0",
    CF[0x88C50:0x88C54] == bytes.fromhex("bfff60e1"),
    CF[0x88C50:0x88C54].hex(),
)
check(
    "ICU wrapper calls initialized driver entry 0x8735E",
    CF[0x86DB4:0x86DB8] == bytes.fromhex("80ffaa05"),
    CF[0x86DB4:0x86DB8].hex(),
)
check(
    "driver initialization reaches hardware init 0x893DE",
    CF[0x87396:0x8739A] == bytes.fromhex("80ff4820"),
    CF[0x87396:0x8739A].hex(),
)
check(
    "ICU interrupt pair helper addresses EIINT 292/293",
    CF[0x89140:0x89144] == bytes.fromhex("e00f49b2")
    and CF[0x89150:0x89154] == bytes.fromhex("e00f4bb2"),
)

print("\n== RoutineControl RID 0x1010 reachability and policy ==")
ROUTINE_RID = struct.Struct("<HBBI")
write_rows = [
    ROUTINE_RID.unpack_from(CF, 0x26AEC + index * ROUTINE_RID.size)
    for index in range(0x13)
]
rid_1010 = write_rows[9]
check(
    "RoutineControl entry 9 is enabled RID 0x1010",
    rid_1010 == (0x1010, 0, 1, 0x26680),
    repr(rid_1010),
)
check(
    "RID 0x1010 selects policy index 1",
    u16(0x26690 + 9 * 2) == 1,
    hex(u16(0x26690 + 9 * 2)),
)
check(
    "policy 1 has no SecurityAccess-level requirement",
    CF[0x26420 + 1 * 2] == 0,
    hex(CF[0x26420 + 1 * 2]),
)
check(
    "policy 1 has one allowed diagnostic session",
    CF[0x26421 + 1 * 2] == 1,
    hex(CF[0x26421 + 1 * 2]),
)
session_list = u32(0x26680 + 4)
session_record = u32(session_list)
check("policy 1 session list is structurally valid", session_list == 0x263B4)
check("policy 1 resolves to session record 0x2630A", session_record == 0x2630A)
check(
    "RID 0x1010 requires extended session 0x03",
    CF[session_record + 1] == 3,
    hex(CF[session_record + 1]),
)
check(
    "RID 0x1010 callback fixes 64 input and 49 status/result bytes",
    CF[0x96360:0x96368] == bytes.fromhex("203e4000204e3100"),
    CF[0x96360:0x96368].hex(),
)
check(
    "runtime service object binds SID 0x31 to callback 0x95DCE",
    CF[0x25F10] == 0x31 and u32(0x25F00) == 0x95DCE,
)
rid_config = CF[0x26B8D + 9 * 15 : 0x26B8D + 10 * 15]
check(
    "RID 0x1010 enables control type 1 with one input and one output field",
    rid_config[4] == 1 and rid_config[6] == 1 and rid_config[8] == 1,
    rid_config.hex(),
)
check(
    "RID 0x1010 enables control type 3 with one output field",
    rid_config[1] == 1 and rid_config[3] == 1,
    rid_config.hex(),
)
check(
    "control-type-1 input descriptor is one 512-bit byte-array field",
    u32(0x2686C + 9 * 4) == 0x26790
    and CF[0x26791] == 7
    and u16(0x26792) == 512,
)
check(
    "control-type-1 output descriptor is one 392-bit byte-array field",
    u32(0x268BC + 9 * 4) == 0x267B4
    and CF[0x267B5] == 7
    and u16(0x267B6) == 392,
)
check(
    "control-type-3 output descriptor is the same 392-bit status/result shape",
    u32(0x267CC + 9 * 4) == 0x2670C
    and CF[0x2670D] == 7
    and u16(0x2670E) == 392,
)

print("\n== authenticated key-update envelope ==")
check(
    "lower prepare requires exactly 64 input bytes",
    CF[0x86E78:0x86E7E] == bytes.fromhex("0706c0ffb205"),
    CF[0x86E78:0x86E7E].hex(),
)
check(
    "lower prepare requires at least 48 output bytes",
    CF[0x86E86:0x86E90]
    == bytes.fromhex("000d0106d0ffe30712db"),
    CF[0x86E86:0x86E90].hex(),
)
check(
    "input is staged as 16 + 32 + 16 bytes",
    CF[0x86EB8:0x86EDE].count(bytes.fromhex("20461000")) == 2
    and CF[0x86EB8:0x86EDE].count(bytes.fromhex("20462000")) == 1,
)
check(
    "completion copies result as 32 + 16 bytes",
    CF[0x86F26:0x86F46].count(bytes.fromhex("20462000")) == 1
    and CF[0x86F26:0x86F46].count(bytes.fromhex("20461000")) == 1,
)
check(
    "diagnostic state machine submits 64 input / 48 output capacity",
    bytes.fromhex("200e3000") in CF[0x6823C:0x682A6]
    and bytes.fromhex("20464000") in CF[0x6823C:0x682A6],
)

print("\n== command-8 driver record and hardware trigger ==")
check("command-8 record ID is zero", u16(0x28024) == 0)
check("command-8 record sentinel is FFFF", u16(0x28026) == 0xFFFF)
check("command-8 completion callback is 0x6920A", u32(0x28028) == 0x6920A)
check("command-8 lower adapter is 0x870A8", u32(0x28038) == 0x870A8)
check("command-8 completion worker is 0x871A0", u32(0x2803C) == 0x871A0)
check("command-8 record state points to 0x28020", u32(0x28040) == 0x28020)
check(
    "hardware engine writes literal command 8 to ICUSCMD",
    CF[0x89A2A:0x89A32] == bytes.fromhex("080a80070f08a08b"),
    CF[0x89A2A:0x89A32].hex(),
)
check(
    "successful command-8 callback advances diagnostic state to 0x44",
    CF[0x6920A:0x69216]
    == bytes.fromhex("200e6600d832ba05200e4400"),
    CF[0x6920A:0x69216].hex(),
)
check(
    "post-update disabled KAT advances state 0x46 to complete 0x55",
    CF[0x6834E:0x6835C]
    == bytes.fromhex("0a06baffda05bfffc4fe20565500"),
    CF[0x6834E:0x6835C].hex(),
)
check(
    "complete state 0x55 maps to diagnostic status 0x02",
    CF[0x68C96:0x68C9E] == bytes.fromhex("1306abffe2970493"),
    CF[0x68C96:0x68C9E].hex(),
)
check(
    "failure state 0x66 maps to diagnostic status 0xFF",
    CF[0x68C9E:0x68CA6] == bytes.fromhex("13069afffa0d1f92"),
    CF[0x68C9E:0x68CA6].hex(),
)
check(
    "diagnostic start reports status 0x01 before arming state 0x22",
    bytes.fromhex("010a440f8598") in CF[0x68E40:0x68E5A]
    and bytes.fromhex("200e2200440f8698") in CF[0x68E40:0x68E5A],
    CF[0x68E40:0x68E5A].hex(),
)
check(
    "result read returns proof only for status 0x02",
    CF[0x68EC8:0x68ECE] == bytes.fromhex("629afa05b515"),
    CF[0x68EC8:0x68ECE].hex(),
)
check(
    "terminal status 0x02 or 0xFF clears the diagnostic bank after read",
    CF[0x68EF6:0x68F06]
    == bytes.fromhex("629ac205130601ffca050032bfff12f0"),
    CF[0x68EF6:0x68F06].hex(),
)
check(
    "completion scrubs 64-byte input and 48-byte result staging",
    CF[0x86F58:0x86F74]
    == bytes.fromhex(
        "24eef458203e40001d36080080ffe020"
        "1d364800203e300080ffd420"
    ),
    CF[0x86F58:0x86F74].hex(),
)

print(f"\n== RESULT: {passed} passed, {failed} failed ==")
if failed:
    sys.exit(1)
