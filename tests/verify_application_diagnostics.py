#!/usr/bin/env python3
"""Independent raw-firmware checks for APPLICATION_DIAGNOSTICS.md."""
from pathlib import Path
import struct
import sys

REPO = Path(__file__).resolve().parents[1]
CF = (REPO / "firmware" / "RH850_P1M-E_CodeFlash.bin").read_bytes()

passed = 0
failed = 0


def check(name, cond, detail=""):
    global passed, failed
    if cond:
        passed += 1
        mark = "PASS"
    else:
        failed += 1
        mark = "FAIL"
    suffix = f" ({detail})" if detail else ""
    print(f"[{mark}] {name}{suffix}")


print("== application UDS service table ==")
APP_SERVICE = struct.Struct("<IIBBBBIII")
app_services = [APP_SERVICE.unpack_from(CF, 0x25E30 + i * APP_SERVICE.size) for i in range(17)]
app_sids = [row[2] for row in app_services]
expected_sids = [
    0x10, 0x11, 0x14, 0x19, 0x22, 0x23, 0x27, 0x28, 0x2E,
    0x31, 0x34, 0x36, 0x37, 0x3E, 0x85, 0xAB, 0xBA,
]
check("application service record size is 24 bytes", APP_SERVICE.size == 24)
check("application service table has 17 records", len(app_services) == 17)
check("application SID sequence matches", app_sids == expected_sids,
      " ".join(f"{sid:02x}" for sid in app_sids))
by_sid = {row[2]: row for row in app_services}
check("SID 0x10 points at application subfunction table 0x25BC0",
      by_sid[0x10][1] == 0x25BC0, hex(by_sid[0x10][1]))
check("SID 0x11 config references callback 0x8B1F0", by_sid[0x11][7] == 0x8B1F0)
check("SID 0x19 config references callback 0x945DC", by_sid[0x19][7] == 0x945DC)
check("SID 0x22 config references callback 0x948AA", by_sid[0x22][7] == 0x948AA)
check("SID 0x28 config references callback 0x93C62", by_sid[0x28][7] == 0x93C62)
check("SID 0x2E config references callback 0x95DCE", by_sid[0x2E][7] == 0x95DCE)
check("SID 0xAB config references callback 0x8D344", by_sid[0xAB][7] == 0x8D344)

print("\n== application identification DIDs ==")
APP_DID = struct.Struct("<HHIII")
app_dids = [APP_DID.unpack_from(CF, 0x2A30C + i * APP_DID.size) for i in range(3)]
expected_dids = [
    (0xF181, 0x0011, 0x4E8E4, 0, 0),
    (0xF186, 0x0001, 0x4E90A, 0, 0),
    (0xF18C, 0x0014, 0x4E918, 0, 0),
]
check("application DID record size is 16 bytes", APP_DID.size == 16)
check("F181/F186/F18C application records match", app_dids == expected_dids, repr(app_dids))
check("application software-ID slot 1 is 8965B4512000",
      CF[0x20860:0x20870] == b"8965B4512000\0\0\0\0")
check("application software-ID slot 2 begins with 8A311", CF[0x20870:0x20875] == b"8A311")
check("F181 callback has exact recovered 38-byte body",
      CF[0x4E8E4:0x4E90A] == bytes.fromhex(
          "06f0010a800b000a409602000198c191c69992976108410a0106f0ff53970100c6f500527f00"))
check("F186 callback delegates through its exact 14-byte wrapper",
      CF[0x4E90A:0x4E918] == bytes.fromhex("8007210084ffd014005240063f00"))
check("F18C callback embeds NvM record 0x0207",
      bytes.fromhex("20360702") in CF[0x4E918:0x4E98E])
check("F18C fallback contains literal '?'", bytes.fromhex("3f00") in CF[0x4E918:0x4E98E])

print("\n== application DiagnosticSessionControl callbacks ==")
SESSION_ROW = struct.Struct("<IIIHH")
session_rows = [SESSION_ROW.unpack_from(CF, 0x25BC0 + i * SESSION_ROW.size) for i in range(3)]
expected_sessions = [
    (0x93FF6, 0, 0x25BAB, 1, 3),
    (0x94006, 0, 0x25B64, 2, 2),
    (0x94016, 0, 0x25B66, 3, 2),
]
check("session row size is 16 bytes", SESSION_ROW.size == 16)
check("default/programming/extended rows match", session_rows == expected_sessions,
      repr(session_rows))
check("default wrapper passes requested session 1",
      CF[0x93FF6:0x94006] == bytes.fromhex("8007210086000142bfff3eff40063f00"))
check("programming wrapper passes requested session 2",
      CF[0x94006:0x94016] == bytes.fromhex("8007210086000242bfff2eff40063f00"))
check("extended wrapper passes requested session 3",
      CF[0x94016:0x94026] == bytes.fromhex("8007210086000342bfff1eff40063f00"))
check("application result mapper contains NRC 0x78",
      bytes.fromhex("7800") in CF[0x8D5FC:0x8D680])
check("application result mapper contains vendor NRC 0x88",
      bytes.fromhex("200e88ff") in CF[0x8D5FC:0x8D680])

print("\n== bootloader/application separation ==")
BOOT_SERVICE = struct.Struct("<BBHI")
boot_services = [BOOT_SERVICE.unpack_from(CF, 0x8E54 + i * BOOT_SERVICE.size) for i in range(20)]
boot_by_sid = {sid: (mask, handler) for sid, mask, _reserved, handler in boot_services}
check("bootloader SID 0x10 uses handler 0x614A and both addressing classes",
      boot_by_sid[0x10] == (3, 0x614A), repr(boot_by_sid[0x10]))
check("bootloader 0x28 and 0x85 are functional-only",
      boot_by_sid[0x28][0] == boot_by_sid[0x85][0] == 1)
check("bootloader 0x11 is physical-only", boot_by_sid[0x11][0] == 2)
check("bootloader 0x14/0x19/0x23/0xAB/0xBA share unsupported handler",
      all(boot_by_sid[sid][1] == 0x69B0 for sid in (0x14, 0x19, 0x23, 0xAB, 0xBA)))
BOOT_DID = struct.Struct("<IHHBBBB")
boot_dids = [BOOT_DID.unpack_from(CF, 0x8F14 + i * BOOT_DID.size) for i in range(4)]
check("bootloader DID set differs from application DID set",
      [row[2] for row in boot_dids] == [0xF181, 0x0201, 0x0202, 0x0203])

print("\n== corrected bootloader session task model ==")
check("session handler calls transient operation reserve at 0x61C2",
      CF[0x61C2:0x61C6] == bytes.fromhex("bfffb4e5"), CF[0x61C2:0x61C6].hex())
check("bootloader session worker contains eventual positive-response call path",
      bytes.fromhex("bfff0ae5e051ca25") in CF[0x6244:0x62D4])
check("main-loop task calls operation release at 0x138C",
      CF[0x138C:0x1390] == bytes.fromhex("80ff0e34"), CF[0x138C:0x1390].hex())
check("release helper clears both transient state bytes",
      CF[0x479A:0x47AA] == bytes.fromhex("a40fa392e009d2054407a2924407a392"),
      CF[0x479A:0x47AA].hex())
check("reserve helper tests busy state before setting it",
      CF[0x4776:0x478A] == bytes.fromhex("a40fa3920152e009fa054457a392020a440fa292"),
      CF[0x4776:0x478A].hex())

print(f"\n== RESULT: {passed} passed, {failed} failed ==")
sys.exit(1 if failed else 0)
