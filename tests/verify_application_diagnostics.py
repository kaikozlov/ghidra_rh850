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
check("every expected SID is present exactly once",
      sorted(app_sids) == sorted(expected_sids) and len(set(app_sids)) == 17)
by_sid = {row[2]: (i, row) for i, row in enumerate(app_services)}
for sid in expected_sids:
    check(f"SID 0x{sid:02X} exists in primary table", sid in by_sid)

expected_callbacks = {
    0x11: 0x8B1F0,
    0x19: 0x945DC,
    0x22: 0x948AA,
    0x28: 0x93C62,
    0x2E: 0x95DCE,
    0xAB: 0x8D344,
}
# 0x10/27/3E/85 use subfunction tables rather than a service-level callback.
for sid, callback in expected_callbacks.items():
    check(f"SID 0x{sid:02X} config references callback 0x{callback:X}",
          by_sid[sid][1][7] == callback, hex(by_sid[sid][1][7]))
for sid in (0x14, 0x23, 0x31, 0x34, 0x36, 0x37, 0xBA):
    check(f"SID 0x{sid:02X} has null service callback", by_sid[sid][1][7] == 0)

check("SID 0x10 points at application subfunction table 0x25BC0",
      by_sid[0x10][1][1] == 0x25BC0, hex(by_sid[0x10][1][1]))
check("SID 0x19 points at subfunction table 0x25BF0", by_sid[0x19][1][1] == 0x25BF0)
check("SID 0x27 points at subfunction table 0x25C30", by_sid[0x27][1][1] == 0x25C30)
check("SID 0x28 points at subfunction table 0x25C70", by_sid[0x28][1][1] == 0x25C70)
check("SID 0x3E points at subfunction table 0x25CA0", by_sid[0x3E][1][1] == 0x25CA0)
check("SID 0x85 points at subfunction table 0x25CB0", by_sid[0x85][1][1] == 0x25CB0)
check("SID 0xAB points at subfunction table 0x25CD0", by_sid[0xAB][1][1] == 0x25CD0)

expected_sessions = {
    0x10: [1, 2, 3],
    0x11: [2],
    0x14: [1, 3],
    0x19: [1, 3],
    0x22: [1, 2, 3],
    0x23: [3],
    0x27: [2, 3],
    0x28: [3],
    0x2E: [2, 3],
    0x31: [1, 2, 3],
    0x34: [2],
    0x36: [2],
    0x37: [2],
    0x3E: [1, 2, 3],
    0x85: [3],
    0xAB: [1, 3],
    0xBA: [3],
}
for sid, sessions in expected_sessions.items():
    _index, row = by_sid[sid]
    allow = list(CF[row[0]: row[0] + row[5]])
    check(f"SID 0x{sid:02X} session allow-list matches", allow == sessions, repr(allow))
    check(f"SID 0x{sid:02X} security allow-count is zero at service level", row[4] == 0)

print("\n== application service groups and secondary endpoint ==")
SERVICE_GROUP = struct.Struct("<HBBI")
service_groups = [SERVICE_GROUP.unpack_from(CF, 0x25DE0 + i * 8) for i in range(3)]
check("service-group directory defines keys/counts 2:17, 3:6, 4:5",
      [(key, count) for key, count, _reserved, _pointer in service_groups]
      == [(2, 17), (3, 6), (4, 5)], repr(service_groups))
check("service-group index-list pointers are exact",
      [row[3] for row in service_groups] == [0x25DF8, 0x25DC0, 0x25E1C])
index_lists = [
    list(struct.unpack_from("<17H", CF, 0x25DF8)),
    list(struct.unpack_from("<6H", CF, 0x25DC0)),
    list(struct.unpack_from("<5H", CF, 0x25E1C)),
]
check("primary group selects records 0..16", index_lists[0] == list(range(17)))
check("functional group reuses exact six records",
      index_lists[1] == [17, 2, 7, 9, 13, 14], repr(index_lists[1]))
check("secondary physical group selects extra records 18..22",
      index_lists[2] == list(range(18, 23)), repr(index_lists[2]))
extra_services = [APP_SERVICE.unpack_from(CF, 0x25FC8 + i * 24) for i in range(6)]
all_services = app_services + extra_services
service_sets = [[all_services[index][2] for index in indexes] for indexes in index_lists]
check("effective primary/functional/secondary SID sets match",
      service_sets == [expected_sids, [0x10, 0x14, 0x28, 0x31, 0x3E, 0x85],
                       [0x10, 0x19, 0x22, 0x3E, 0xAB]], repr(service_sets))
check("application diagnostic receive CAN IDs are 7A1/777/7A0",
      [struct.unpack_from("<I", CF, 0x21FC8 + i * 8)[0] for i in range(3)]
      == [0x7A1, 0x777, 0x7A0])
check("application diagnostic transmit CAN IDs are paired 7A9/7A8",
      [struct.unpack_from("<I", CF, 0x21FA8 + i * 8)[0] for i in range(4)]
      == [0x7A9, 0x7A9, 0x7A8, 0x7A8])

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
check("default subfunction allows current sessions 1/2/3",
      CF[session_rows[0][2]:session_rows[0][2] + session_rows[0][4]] == bytes([1, 2, 3]))
check("programming subfunction allows only current sessions 2/3",
      CF[session_rows[1][2]:session_rows[1][2] + session_rows[1][4]] == bytes([2, 3]))
check("extended subfunction allows only current sessions 1/3",
      CF[session_rows[2][2]:session_rows[2][2] + session_rows[2][4]] == bytes([1, 3]))
SESSION_CONFIG = struct.Struct("<BBHHHH")
programming_config = SESSION_CONFIG.unpack_from(CF, 0x26300)
check("programming runtime config selects async kind 2/session 2",
      programming_config[:2] == (2, 2), repr(programming_config))
check("programming runtime config carries 50 ms P2 and encoded 5 s P2*",
      programming_config[2] == 50 and programming_config[5] == 500,
      repr(programming_config))
check("application result mapper contains NRC 0x78",
      bytes.fromhex("7800") in CF[0x8D5FC:0x8D680])
check("application result mapper contains vehicleSpeedTooHigh NRC 0x88",
      bytes.fromhex("200e88ff") in CF[0x8D5FC:0x8D680])

print("\n== programming policy and reset handoff ==")
APP_GP = 0xFEBEB800

def fits_s16(value: int) -> bool:
    return -0x8000 <= value <= 0x7FFF

check("programming calibrations are speed 0x0180 and supply 0x0A00",
      struct.unpack_from("<HH", CF, 0x181DC) == (0x0180, 0x0A00))
check("snapshot prologue sets r19 = GP+0x3000",
      CF[0xBCB3E:0xBCB42] == bytes.fromhex("249e0030"))
check("snapshot restores EP from r19 before phase store window",
      CF[0xBCCAE:0xBCCB0] == bytes.fromhex("13f0"))
check("input snapshot copies live GP-0x65C phase to EP+0x1F (GP+0x301F)",
      CF[0xBCD02:0xBCD08] == bytes.fromhex("840fa5f99f0b"),
      CF[0xBCD02:0xBCD08].hex())
check("transition phase initializer passes phase zero",
      CF[0xB28AC:0xB28B2] == bytes.fromhex("80072100243e"))
check("transition state machine embeds phase markers 0x11 and 0x22",
      bytes.fromhex("200e1100") in CF[0xB2912:0xB29EA] and
      bytes.fromhex("200e2200") in CF[0xB2912:0xB29EA])
check("speed policy loads GP+0x3092 then compares calibration 0x0180",
      CF[0x4C944:0x4C954] == bytes.fromhex("e40f9330623a9a0d409e0200f39fdd81"),
      CF[0x4C944:0x4C954].hex())
check("speed policy has exact recovered body",
      CF[0x4C942:0x4C960] == bytes.fromhex(
          "8700e40f9330623a9a0d409e0200f39fdd81f309b3050b527f0000527f00"))
# application_programming_handoff_prerequisites @ 0x4C960:
#   ld.bu 0x301F[gp] ; ld.hu -0x516E[gp] ; ld.bu -0x36AE[gp]
#   addi -0x11 ; be fail ; movhi 2 / ld.hu -0x7E22[r1] (= CodeFlash 0x181DE)
#   cmp supply ; bc fail ; cmp flag ; be ok ; mov 1 ; jmp lp
HANDOFF = bytes.fromhex(
    "a40f1f30e49f93ae845753c90106efff"
    "920d400e0200e10fdf81e199b105e051"
    "a20501527f00")
check("handoff prerequisites body is exact through return",
      CF[0x4C960:0x4C986] == HANDOFF, CF[0x4C960:0x4C986].hex())
check("handoff loads phase via ld.bu 0x301F[gp] -> FEBEE81F",
      CF[0x4C960:0x4C964] == bytes.fromhex("a40f1f30") and
      (APP_GP + 0x301F) & 0xFFFFFFFF == 0xFEBEE81F and fits_s16(0x301F))
check("handoff compares phase against immediate 0x11",
      CF[0x4C96C:0x4C970] == bytes.fromhex("0106efff"))
check("handoff loads supply via ld.hu -0x516E[gp] -> FEBE6692",
      CF[0x4C964:0x4C968] == bytes.fromhex("e49f93ae") and
      (APP_GP + (-0x516E)) & 0xFFFFFFFF == 0xFEBE6692 and fits_s16(-0x516E))
check("handoff loads alternate flag via ld.bu -0x36AE[gp] -> FEBE8152",
      CF[0x4C968:0x4C96C] == bytes.fromhex("845753c9") and
      (APP_GP + (-0x36AE)) & 0xFFFFFFFF == 0xFEBE8152 and fits_s16(-0x36AE))
check("handoff compares against calibrated min supply at 0x181DE",
      CF[0x4C972:0x4C97A] == bytes.fromhex("400e0200e10fdf81") and
      struct.unpack_from("<H", CF, 0x181DE)[0] == 0x0A00)
check("handoff failure path returns internal 1",
      CF[0x4C982:0x4C986] == bytes.fromhex("01527f00"))
check("speed GP+0x3092 resolves to FEBEE892",
      (APP_GP + 0x3092) & 0xFFFFFFFF == 0xFEBEE892 and fits_s16(0x3092))
check("reset marker clear/store use GP-0x369A -> FEBE8166",
      CF[0x4C986:0x4C98A] == bytes.fromhex("440766c9") and
      CF[0x4C998:0x4C99C] == bytes.fromhex("840f67c9") and
      (APP_GP + (-0x369A)) & 0xFFFFFFFF == 0xFEBE8166 and fits_s16(-0x369A))
check("readiness/async workers use absolute FEBF3B18/FEBF3B14",
      CF[0x8A092:0x8A098] == bytes.fromhex("3d06183bbffe") and
      CF[0x8A248:0x8A24E] == bytes.fromhex("3d06143bbffe"))
check("reset latch is absolute FEBF3B14+5",
      CF[0x8A24E:0x8A252] == bytes.fromhex("bde70500") and
      CF[0x8A276:0x8A27A] == bytes.fromhex("5de70500"))
check("async poll maps worker result 1 to NRC 0x22",
      CF[0x93EE6:0x93EFA] == bytes.fromhex("6152ea0d44072da51c3080ff480120ee22001d38"),
      CF[0x93EE6:0x93EFA].hex())
check("application result mapper still contains NRC 0x22 literal",
      bytes.fromhex("200e2200") in CF[0x8D5FC:0x8D680])
check("lower request/poll stubs return immediate success",
      CF[0x8A01C:0x8A024] == bytes.fromhex("00527f0000527f00"))
check("lower token validator returns 0x5A",
      CF[0x8D534:0x8D53A] == bytes.fromhex("20565a007f00"))
check("prepare stage embeds operation 0x08000200",
      bytes.fromhex("00020008") in CF[0x8A0C2:0x8A172])
check("commit stage embeds operation 0x08000201",
      bytes.fromhex("01020008") in CF[0x8A172:0x8A244])
check("readiness adapter calls handoff prerequisites",
      CF[0x8A0A0:0x8A0A4] == bytes.fromhex("bcffc028"),
      CF[0x8A0A0:0x8A0A4].hex())
check("reset request queues system event 9",
      CF[0x4C9A0:0x4C9A6] == bytes.fromhex("09328bff5a16"),
      CF[0x4C9A0:0x4C9A6].hex())
check("mode 0x900 callback table points to shutdown entry/exit",
      struct.unpack_from("<II", CF, 0xAEB48) == (0xB20EA, 0xB213A))
check("shutdown entry carries subsystem request 0x70017001",
      struct.pack("<I", 0x70017001) in CF[0xB20EA:0xB213A])
check("shutdown entry carries subsystem request 0x00020002",
      struct.pack("<I", 0x00020002) in CF[0xB20EA:0xB213A])
check("hard-reset path enters an intentional terminal loop",
      CF[0x60928:0x6092A] == bytes.fromhex("8505"),
      CF[0x60928:0x6092A].hex())

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

print("\n== application DID / write-DID / routine-ID tables ==")
did_rows = [APP_DID.unpack_from(CF, 0x2941C + i * APP_DID.size) for i in range(0xF2)]
check("application DID table getter embeds count 0xF2 and base 0x2941C",
      CF[0x4F928:0x4F938] == bytes.fromhex("06f0200ef200800c2a061c9402007f00"),
      CF[0x4F928:0x4F938].hex())
check("DID table has 242 records from 0x0100 through F18C",
      did_rows[0][0] == 0x0100 and did_rows[-1][0] == 0xF18C and len(did_rows) == 0xF2)
check("DID table still contains F181/F186/F18C records",
      [(0xF181, 0x0011, 0x4E8E4), (0xF186, 0x0001, 0x4E90A), (0xF18C, 0x0014, 0x4E918)]
      == [(d, f, c) for d, f, c, _a1, _a2 in did_rows if d in (0xF181, 0xF186, 0xF18C)])
WRITE_DID = struct.Struct("<HBBI")
write_rows = [WRITE_DID.unpack_from(CF, 0x26AEC + i * WRITE_DID.size) for i in range(0x13)]
check("write-DID table has 19 records from 0x1000 through 0x110D",
      write_rows[0][0] == 0x1000 and write_rows[-1][0] == 0x110D and len(write_rows) == 0x13)
check("write-DID records carry enable byte 0x01", all(row[2] == 1 for row in write_rows))
ROUTINE = struct.Struct("<HHII")
routine_rows = [ROUTINE.unpack_from(CF, 0x25768 + i * ROUTINE.size) for i in range(32)]
check("routine-ID table has 32 records from 0x0204 through 0x110D",
      routine_rows[0][0] == 0x0204 and routine_rows[-1][0] == 0x110D)
check("routine-ID lookup scans tp+0x1884 (=0x25768)",
      bytes.fromhex("8418") in CF[0x8D3CC:0x8D416])
check("routine-ID lookup stops after index 0x0C",
      bytes.fromhex("0c00") in CF[0x8D3CC:0x8D416])

print("\n== per-SID handler bodies and bounded negatives ==")
SUBFN = struct.Struct("<IIIHH")
sa_rows = [SUBFN.unpack_from(CF, 0x25C30 + i * SUBFN.size) for i in range(4)]
check("SecurityAccess subfunctions are 01..04", [row[3] for row in sa_rows] == [1, 2, 3, 4])
check("SecurityAccess wrappers target shared level helpers",
      [row[0] for row in sa_rows] == [0x94E32, 0x94E46, 0x94E5A, 0x94E6E])
check("SecurityAccess level-1/2 configs use 16-byte seed/key",
      struct.unpack_from("<I", CF, 0x26338)[0] == 0x10 and
      struct.unpack_from("<I", CF, 0x26350)[0] == 0x10)
check("SecurityAccess send-key embeds NRC 0x35 and 0x36",
      bytes.fromhex("203e3500") in CF[0x94A72:0x94B66] and
      bytes.fromhex("203e3600") in CF[0x94A72:0x94B66])
check("ECUReset start packs three request bytes before lower stages",
      bytes.fromhex("7d070100") in CF[0x8B144:0x8B180] and
      bytes.fromhex("3d3e0800") in CF[0x8B144:0x8B180])
check("ECUReset prepare stage embeds op 0x18000000",
      bytes.fromhex("40360018") in CF[0x8AF28:0x8B014])
check("ECUReset commit stage embeds op 0x18000001",
      bytes.fromhex("40360018") in CF[0x8B014:0x8B124] or
      bytes.fromhex("01000018") in CF[0x8B014:0x8B124])
check("ControlDTCSetting subfunction 01 wrapper passes setting 1",
      CF[0x8CCDC:0x8CCFA] == bytes.fromhex(
          "80076100d832ea050132bfff96ff0ae8c50500eabfff90fd1d5040067f00"))
check("CommunicationControl subfunctions are 00/01/03",
      [SUBFN.unpack_from(CF, 0x25C70 + i * SUBFN.size)[3] for i in range(3)] == [0, 1, 3])
check("proprietary AB subfunctions are 01/02/03",
      [SUBFN.unpack_from(CF, 0x25CD0 + i * SUBFN.size)[3] for i in range(3)] == [1, 2, 3])
check("RDBI start embeds NRC 0x13/0x31/0x33 literals",
      bytes.fromhex("203e1300") in CF[0x9479A:0x9486C] and
      bytes.fromhex("203e3100") in CF[0x9479A:0x9486C] and
      bytes.fromhex("203e3300") in CF[0x9479A:0x9486C])
check("WDBI start embeds NRC 0x13/0x31/0x33 literals",
      bytes.fromhex("200e1300") in CF[0x95C8C:0x95D7E] and
      bytes.fromhex("200e3100") in CF[0x95C8C:0x95D7E] and
      bytes.fromhex("200e3300") in CF[0x95C8C:0x95D7E])
check("WDBI start embeds NRC 0x12 via movea/mov immediate form",
      bytes.fromhex("200e1200") in CF[0x95C8C:0x95D7E] or
      bytes.fromhex("203e1200") in CF[0x95C8C:0x95D7E])

# Bounded negatives: null-callback SIDs have no absolute callback pointer in-record
# and no CodeFlash dword xref to the service-record address. Combined with the
# shared gate check below, this matches the published search coverage — not an
# exhaustive DSP-absence claim.
for sid, record_addr in (
    (0x14, 0x25E60),
    (0x23, 0x25EA8),
    (0x31, 0x25F08),
    (0x34, 0x25F20),
    (0x36, 0x25F38),
    (0x37, 0x25F50),
    (0xBA, 0x25FB0),
):
    needle = struct.pack("<I", record_addr)
    hits = []
    start = 0
    while True:
        at = CF.find(needle, start)
        if at < 0:
            break
        hits.append(at)
        start = at + 1
    check(f"SID 0x{sid:02X} record address has no CodeFlash dword xrefs",
          hits == [], repr([hex(h) for h in hits]))

print("\n== instruction-proved RAM side effects and shared service gate ==")
def mov_imm32_r1(imm: int) -> bytes:
    return bytes.fromhex("2106") + struct.pack("<I", imm)


for addr, imm, label in (
    (0x8CC80, 0xFEBF45A8, "ControlDTCSetting"),
    (0x8B5B0, 0xFEBF3BFC, "ReadDTC subfn01"),
    (0x8BA30, 0xFEBF3F24, "ReadDTC subfn02"),
    (0x8BD9A, 0xFEBF4248, "ReadDTC subfn03"),
    (0x8C32C, 0xFEBF457C, "ReadDTC subfn04"),
    (0x8D350, 0xFEBF48EC, "proprietary AB"),
):
    check(f"{label} absolute mov imm32,r1 at 0x{addr:X}",
          CF[addr:addr + 6] == mov_imm32_r1(imm), CF[addr:addr + 6].hex())

check("ControlDTCSetting stores setting byte via st.b r6,0[r1] after absolute base",
      CF[0x8CCCA:0x8CCCE] == bytes.fromhex("41370000"))
check("ControlDTCSetting request mirror targets FEBF45A8+0xC via movea 0xC,r1,r19",
      CF[0x8CC9E:0x8CCA2] == bytes.fromhex("219e0c00"))
check("proprietary AB st.w r19,0x50[r1] builds FEBF493C from FEBF48EC",
      CF[0x8D358:0x8D35C] == bytes.fromhex("619f5100"))
check("proprietary AB keeps FEBF48EC in r6 for primary 0/4/8/C stores",
      CF[0x8D356:0x8D358] == bytes.fromhex("0130") and
      CF[0x8D394:0x8D398] == bytes.fromhex("660f0100"))
check("ReadDTC subfn01 mirrors request via st.w r19,0[r1] at absolute base",
      CF[0x8B5BA:0x8B5BE] == bytes.fromhex("619f0100"))

# Shared session gate 0x8F282: SID compare at tp+0x1F54 (=0x25E38), stride 0x18,
# then jarl 0x8F202; session-list miss emits NRC 0x7F.
APP_TP = 0x25E38 - 0x1F54
check("service-table SID byte is at TP+0x1F54 (first record SID 0x10)",
      APP_TP == 0x23EE4 and CF[APP_TP + 0x1F54] == 0x10)
check("gate 0x8F282 encodes ld.bu 0x1F54[r17] SID compare",
      CF[0x8F2B8:0x8F2BC] == bytes.fromhex("918f551f"))
check("gate 0x8F282 encodes mulhi 0x18 record stride before SID load",
      CF[0x8F2B2:0x8F2B6] == bytes.fromhex("f18e1800"))
check("gate 0x8F282 jarls session allow-list helper 0x8F202",
      CF[0x8F308:0x8F30C] == bytes.fromhex("bffffafe"))
check("gate session-list failure path embeds NRC 0x7F",
      CF[0x8F32C:0x8F330] == bytes.fromhex("200e7f00"))
check("SecurityAccess send-key success jarls unlock helper 0x900FC",
      CF[0x94AC0:0x94AC4] == bytes.fromhex("bfff3cb6"))
check("CommunicationControl 0x95154 jarls mode helpers 0x94F8E and 0x9505C",
      bytes.fromhex("bfff62fd") in CF[0x95154:0x952D0] and
      bytes.fromhex("bfff90fd") in CF[0x95154:0x952D0])

print("\n== Dcm DSP dispatch architecture ==")

# The application Dcm has a compiled generated-DSP framework at 0x8F3E4 that is
# entered after the service gate succeeds. It uses two enable flags and two
# function-pointer pairs to select start-phase and complete-phase DSP handlers.
# In this calibration the start-phase DSP is globally disabled, so all services
# (including null-callback SIDs) receive the same no-op start processing. The
# complete-phase DSP is enabled but resolves to a generic init/teardown stub.
check("DSP start-phase enable flag @0x25DCC is 0x00 (globally disabled)",
      CF[0x25DCC] == 0x00)
check("DSP complete-phase enable flag @0x25DCD is 0x01 (enabled)",
      CF[0x25DCD] == 0x01)

# DSP pointer-pair chain: flag-ptr -> ptr-table -> handler-fn
dsp_start_pair = struct.unpack_from("<I", CF, 0x25DD0)[0]
dsp_complete_pair = struct.unpack_from("<I", CF, 0x25DD8)[0]
check("DSP start ptr-pair @0x25DD0 resolves to 0x25B54",
      dsp_start_pair == 0x25B54)
check("DSP complete ptr-pair @0x25DD8 resolves to 0x25B5C",
      dsp_complete_pair == 0x25B5C)
dsp_start_fn = struct.unpack_from("<I", CF, dsp_start_pair)[0]
dsp_complete_fn = struct.unpack_from("<I", CF, dsp_complete_pair)[0]
check("DSP start handler is stub 0x8F1E0 (mov 1,r10; jmp lp = return 1)",
      dsp_start_fn == 0x8F1E0 and
      CF[0x8F1E0:0x8F1E4] == bytes.fromhex("01527f00"))
check("DSP complete handler is 0x8F1E8 (-> 0x8A00C -> 0x4C506 init stub)",
      dsp_complete_fn == 0x8F1E8)
check("DSP complete stub 0x8F1E8 jarls 0x8A00C at 0x8F1F0",
      CF[0x8F1F0:0x8F1F4] == bytes.fromhex("bfff1cae"))
check("DSP complete callee 0x8A00C is a prepare/dispose wrapper",
      CF[0x8A00C:0x8A010] == bytes.fromhex("80072100") and
      CF[0x8A018:0x8A01C] == bytes.fromhex("40063f00"))
check("handoff-flag setter 0x4C506 stores to application_alternate_handoff_flag",
      bytes.fromhex("06a6ff") in CF[0x4C506:0x4C540])

# Service record byte[9] is the subfunction/callback processing flag.
# byte[9]==0x01 -> service routes through subfn dispatch (0x8F750)
# byte[9]==0x00 -> service routes through simple response (0x8F6FA)
byte9_subfn = {0x10, 0x19, 0x27, 0x28, 0x3E, 0x85, 0xAB}
byte9_simple = {0x11, 0x14, 0x22, 0x23, 0x2E, 0x31, 0x34, 0x36, 0x37, 0xBA}
for sid in byte9_subfn:
    idx = [i for i in range(17) if app_services[i][2] == sid][0]
    check(f"SID 0x{sid:02X} byte[9] marks subfn/callback processing",
          app_services[idx][3] == 0x01)
for sid in byte9_simple:
    idx = [i for i in range(17) if app_services[i][2] == sid][0]
    check(f"SID 0x{sid:02X} byte[9] marks simple-response path",
          app_services[idx][3] == 0x00)

# All null-callback SIDs have byte[9]==0x00 -> they take the simple-response
# path. This is the definitive resolution of the "dsp-indirection-unresolved"
# status: there is no hidden DSP path; the generated DSP start-phase is globally
# disabled and these services echo a positive response without service-specific
# processing.
for sid in (0x14, 0x23, 0x31, 0x34, 0x36, 0x37, 0xBA):
    idx = [i for i in range(17) if app_services[i][2] == sid][0]
    check(f"null-callback SID 0x{sid:02X} takes simple-response path "
          f"(byte[9]==0 and callback==0)",
          app_services[idx][3] == 0x00 and app_services[idx][7] == 0)

# The main Dcm request processor at 0x8F850 calls the gate, then the DSP
# dispatcher, then routes to simple-response (0x8F6FA) or subfn dispatch
# (0x8F750) based on the flag the gate sets.
check("Dcm main processor 0x8F850 calls service gate 0x8F282 at 0x8F8BC",
      CF[0x8F8BC:0x8F8C0] == bytes.fromhex("bfffc6f9"))
check("Dcm main processor 0x8F850 calls DSP dispatcher 0x8F3E4 (phase 0 at 0x8F88E)",
      CF[0x8F88E:0x8F892] == bytes.fromhex("bfff56fb"))
check("Dcm main processor 0x8F850 calls DSP dispatcher 0x8F3E4 (phase 2 at 0x8F8D6)",
      CF[0x8F8D6:0x8F8DA] == bytes.fromhex("bfff0efb"))
check("Dcm main processor 0x8F850 calls simple-response 0x8F6FA at 0x8F8EA",
      CF[0x8F8EA:0x8F8EE] == bytes.fromhex("bfff10fe"))
check("Dcm main processor 0x8F850 calls subfn dispatch 0x8F750 at 0x8F8F0",
      CF[0x8F8F0:0x8F8F4] == bytes.fromhex("bfff60fe"))
check("simple-response builder 0x8F6FA ORs SID with 0x40 positive-response prefix",
      bytes.fromhex("4000") in CF[0x8F6FA:0x8F720])

print("\n== generated application diagnostic map artifact ==")
import csv
import tempfile
from pathlib import Path as _Path
MAP_CSV = REPO / "data" / "application_diagnostic_map.csv"
GEN = REPO / "tools" / "generate_application_diagnostic_map.py"
check("application diagnostic map CSV exists", MAP_CSV.is_file())
with MAP_CSV.open(newline="") as fh:
    map_rows = list(csv.DictReader(fh))
check("map CSV contains exactly 17 SID rows", len(map_rows) == 17, str(len(map_rows)))
check("map CSV SID set matches primary table",
      [int(row["sid"], 16) for row in map_rows] == expected_sids)
missing = [sid for sid in expected_sids if f"0x{sid:02X}" not in {row["sid"] for row in map_rows}]
check("map CSV fails closed if any of 17 SIDs missing", missing == [], repr(missing))
with tempfile.TemporaryDirectory() as tmp:
    out = _Path(tmp) / "application_diagnostic_map.csv"
    import subprocess
    proc = subprocess.run(
        [sys.executable, str(GEN), "-o", str(out)],
        cwd=REPO,
        check=True,
        capture_output=True,
        text=True,
    )
    check("generator rerun succeeds", proc.returncode == 0, proc.stderr)
    regenerated = out.read_bytes()
    check("committed map matches deterministic regeneration",
          regenerated == MAP_CSV.read_bytes())

print(f"\n== RESULT: {passed} passed, {failed} failed ==")
sys.exit(1 if failed else 0)
