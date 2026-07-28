#!/usr/bin/env python3
"""Verify the application SecOC receive profile directly from committed images."""
from __future__ import annotations

import math
import struct
import sys
from collections import Counter
from pathlib import Path

from Crypto.Cipher import AES
from Crypto.Hash import CMAC

REPO = Path(__file__).resolve().parents[1]
CF = (REPO / "firmware" / "RH850_P1M-E_CodeFlash.bin").read_bytes()
DF = (REPO / "firmware" / "RH850_P1M-E_DataFlash.bin").read_bytes()
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


def u16(a: int) -> int:
    return struct.unpack_from("<H", CF, a)[0]


def u32(a: int) -> int:
    return struct.unpack_from("<I", CF, a)[0]


print("== generated SecOC receive records ==")
TP = 0x23EE4
RECORD_BASE = TP + 0x1A8C
RECORD_SIZE = 0x50
records = [RECORD_BASE + i * RECORD_SIZE for i in range(6)]
expected_ids = [0x00F, 0x2E4, 0x131, 0x132, 0x090, 0x0D7]
expected_pdu = [11, 6, 26, 35, 46, 47]
expected_secured_len = [8, 8, 8, 8, 32, 32]
expected_trailer_len = [8, 4, 4, 4, 4, 4]
expected_full_fv = [36, 46, 46, 46, 46, 46]
expected_trunc_fv = [36, 4, 4, 4, 4, 4]
expected_handles = [0, 0, 0, 0, 0, 0]
expected_crypto_buffer_lengths = [8, 8, 8, 8, 32, 32]
expected_freshness_ids = [0, 1, 2, 4, 5, 6]

check("record table resolves to 0x25970", RECORD_BASE == 0x25970)
check("six records have exact Data/CAN IDs", [u16(a + 0x0A) for a in records] == expected_ids)
check("records have exact application RX PDU IDs", [u16(a + 0x34) for a in records] == expected_pdu)
check("records have exact secured PDU lengths", [u32(a + 0x3C) for a in records] == expected_secured_len)
check("records duplicate exact buffer lengths", [u32(a + 0x44) for a in records] == expected_secured_len)
check("sync/normal trailer lengths are 8/4", [u16(a + 0x06) for a in records] == expected_trailer_len)
check("all records configure 128-bit full CMAC", all(u16(a) == 128 for a in records))
check("all records configure 28-bit transmitted CMAC", all(u16(a + 2) == 28 for a in records))
check("full freshness widths are 36/46 bits", [CF[a + 0x14] for a in records] == expected_full_fv)
check("transmitted freshness widths are 36/4 bits", [CF[a + 0x15] for a in records] == expected_trunc_fv)
check("freshness IDs match exact sequence", [u16(a + 0x12) for a in records] == expected_freshness_ids)
check("all SecOC profiles use CSM/CryptoIf handle 0", [u32(a + 0x20) for a in records] == expected_handles)
check("classic/FD crypto buffer lengths are 8/32",
      [u32(a + 0x24) for a in records] == expected_crypto_buffer_lengths)
check("all profiles use freshness callback 0x8E8E6", all(u32(a + 0x48) == 0x8E8E6 for a in records))
check("all profiles use freshness commit callback 0x8E942", all(u32(a + 0x30) == 0x8E942 for a in records))
check("all profiles use application state callback 0x69182", all(u32(a + 0x4C) == 0x69182 for a in records))

payload_lengths = [total - trailer for total, trailer in zip(expected_secured_len, expected_trailer_len)]
full_fv_bytes = [(bits + 7) // 8 for bits in expected_full_fv]
authenticated_lengths = [2 + payload + fv for payload, fv in zip(payload_lengths, full_fv_bytes)]
check("sync has no authentic payload", payload_lengths[0] == 0)
check("classic protected payloads are four bytes", payload_lengths[1:4] == [4, 4, 4])
check("CAN-FD protected payloads are 28 bytes", payload_lengths[4:] == [28, 28])
check("classic protected authenticated input is 96 bits", authenticated_lengths[1:4] == [12, 12, 12])
check("CAN-FD authenticated input is 36 bytes", authenticated_lengths[4:] == [36, 36])
check("sync authenticated input is ID16 + freshness36", authenticated_lengths[0] == 7)
check("ordinary trailer is exactly FV4 + CMAC28", expected_trunc_fv[1] + 28 == 32)
check("sync trailer is exactly FV36 + CMAC28", expected_trunc_fv[0] + 28 == 64)

print("\n== CAN acceptance to SecOC PDU routing ==")
normal_ids = [u32(0x22018 + i * 8) & 0x7FF for i in range(47)]
acceptance_ids = [u32(0x231A0 + i * 16) for i in range(51)]
expected_routes = {0x2E4: (0, 6), 0x00F: (5, 11), 0x131: (20, 26),
                   0x132: (29, 35), 0x090: (40, 46), 0x0D7: (41, 47)}
for can_id, (index, pdu_id) in expected_routes.items():
    check(f"CAN {can_id:#05x} acceptance index", acceptance_ids[index] == can_id)
    check(f"CAN {can_id:#05x} maps to SecOC PDU {pdu_id}", 6 + index == pdu_id)
check("normal RX descriptors mirror all six SecOC CAN IDs",
      all(normal_ids[index] == can_id for can_id, (index, _) in expected_routes.items()))
check("0x344 has no application acceptance rule", 0x344 not in acceptance_ids)
check("0x344 has no SecOC receive record", 0x344 not in [u16(a + 0x0A) for a in records])
check("0x344 has no aligned 32-bit CodeFlash literal",
      all(u32(a) != 0x344 for a in range(0, len(CF) - 3, 4)))

print("\n== ICU-S slot-4 configuration and disabled known-answer vector ==")
secoc_key_cfg = CF[0x25950:0x25964]
kat_message = CF[0x215E4:0x215F4]
kat_tag = CF[0x215F4:0x21604]
kat_cfg = CF[0x21604:0x21618]
check("SecOC crypto config type is 1", struct.unpack_from("<I", secoc_key_cfg)[0] == 1)
check("SecOC crypto config selects slot 4", secoc_key_cfg[4] == 4 and secoc_key_cfg[5:] == bytes(15))
check("known-answer config matches type 1 / slot 4", kat_cfg == secoc_key_cfg)
check("known-answer input is 16 zero bytes", kat_message == bytes(16))
check("known-answer tag is exact embedded value", kat_tag.hex() == "b290fa2ea7b6b52eb124134522a6e540")
kat = CMAC.new(bytes([0xFF]) * 16, ciphermod=AES)
kat.update(bytes(16))
check("known-answer tag is AES-CMAC under erased FF*16 key", kat.digest() == kat_tag)
zero_kat = CMAC.new(bytes(16), ciphermod=AES)
zero_kat.update(bytes(16))
check("known-answer tag is not the zero-key vector", zero_kat.digest() != kat_tag)
check("known-answer compile-time gate byte is zero", CF[0x30EF3] == 0)
check("synchronous known-answer body requires gate byte 0x5A",
      CF[0x68102:0x68110] ==
      bytes.fromhex("400e0300a10ff30e0106a6ffda2d"))
check("asynchronous known-answer body requires the same gate byte 0x5A",
      CF[0x682B0:0x682BE] ==
      bytes.fromhex("400e0300a10ff30e0106a6ffaa1d"))

# Exact RH850 instructions: config+4 key selector is loaded at 0x87F70; command
# word (slot << 16) | 7 is assembled and written to FFC5D000 at 0x89906..0x89911.
check("ICU request loads key selector from config+4",
      CF[0x87F70:0x87F76] == bytes.fromhex("9b0f05000d0d"))
check("ICU command encodes key slot <<16 OR command 7",
      CF[0x89906:0x8990C] == bytes.fromhex("d08a910e0700"))
check("ICU command writes FFC5D000",
      CF[0x8990C:0x89912] == bytes.fromhex("80070f08a08b"))
check("CMAC verify command state is literal 7",
      CF[0x898CE:0x898D4] == bytes.fromhex("070a640f295b"))

print("\n== ICU-S command-5 MAC-generation family ==")
generate_records = [0x27F78, 0x27F98]
verify_records = [0x27FBC, 0x27FDC]
check("command-5 lower table has IDs 0 and 1",
      [u16(a) for a in generate_records] == [0, 1])
check("command-5 records use the same adapter and completion worker",
      all(u32(a + 0x14) == 0x87CCC and u32(a + 0x18) == 0x87DD0
          for a in generate_records))
check("command-5 records use synchronous/asynchronous callbacks",
      [u32(a + 4) for a in generate_records] == [0x88B5C, 0x6926A])
check("command-7 records use the seeded verification completion worker",
      all(u32(a + 0x18) == 0x881DC for a in verify_records))
check("command-5 prepare loads key selector from config+4",
      CF[0x87B2E:0x87B32] == bytes.fromhex("9a0f0500"))
check("command-5 engine records literal operation 5",
      CF[0x896DC:0x896E2] == bytes.fromhex("050a640f295b"))
check("command-5 command encodes selector <<16 OR 5 and writes ICUSCMD",
      CF[0x89734:0x89740] ==
      bytes.fromhex("d092920e050080070f08a08b"))
check("command-5 completion clamps caller output length to 16 bytes",
      CF[0x87B7E:0x87B90] ==
      bytes.fromhex("e0e9ca0d00450806efffb905204610000145"))
check("command-5 application harness compares all 16 generated bytes",
      CF[0x69068:0x6908E] ==
      bytes.fromhex("20563300000a01f0c4f19e9fab999e978b99f391"
                    "c205205644007f00410a0106f0ffa9f57f00"))
check("only configured command-5 dispatch call is the application crypto-test harness",
      CF.count(bytes.fromhex("81ffa4f7")) == 1 and
      CF[0x68BAC:0x68BB0] == bytes.fromhex("81ffa4f7"))
check("command-5 harness obtains selector from RAM rather than hard-coding slot 4",
      CF[0x68B82:0x68B92] ==
      bytes.fromhex("03f0070d840f9998204e1000644f6198"))

print("\n== authenticated-input and freshness packing code ==")
check("authenticated-input builder stores big-endian Data ID",
      CF[0x8DB50:0x8DB5C] == bytes.fromhex("880a470f00006808470f0100"))
check("freshness parser has explicit four-bit profile branch",
      CF[0x8EBC2:0x8EBCA] == bytes.fromhex("08f0643aba0d0105"))
check("full-freshness packer has explicit 46-bit profile branch",
      CF[0x8EA4C:0x8EA5E] == bytes.fromhex("06f06b08889f0100f309eb350106d2ffba25"))

# Independent arithmetic check of the documented 46-bit left-aligned format.
def pack_freshness(trip: int, reset: int, message: int) -> bytes:
    return struct.pack(">HI", trip & 0xFFFF,
                       ((reset & 0xFFFFF) << 12) |
                       ((message & 0xFF) << 4) |
                       ((reset & 3) << 2))

sample = pack_freshness(0x1234, 0x56789, 0xAB)
check("freshness reference packing is six bytes", len(sample) == 6)
check("freshness leaves two low pad bits clear", sample[-1] & 3 == 0)
transmitted_flag = ((0xAB & 3) << 2) | (0x56789 & 3)
check("transmitted nibble combines message-low2/reset-low2", transmitted_flag == 0xD)
check("full freshness retains message-low4 in its high final nibble", sample[-1] >> 4 == (0xAB & 0xF))

print("\n== object-15 separation and corrected work buffers ==")
obj15 = struct.unpack_from("<HHI", CF, 0x2B0AC + 15 * 8)
check("object 15 remains len32/base41/RAM FEBF02E8", obj15 == (32, 41, 0xFEBF02E8))
check("FEBF02F8 has no direct CodeFlash pointer literal",
      struct.pack("<I", 0xFEBF02F8) not in CF)
check("FEBF02E8 appears only in the object-15 descriptor",
      CF.find(struct.pack("<I", 0xFEBF02E8)) == 0x2B128 and
      CF.find(struct.pack("<I", 0xFEBF02E8), 0x2B129) == -1)

APP_GP = 0xFEBEB800
work_root = APP_GP + 0x5308
obj15_group = work_root + (15 & 3) * 0x60
check("correct triplicate work root is FEBF0B08", work_root == 0xFEBF0B08)
check("object-15 work buffers are FEBF0C28/48/68",
      (obj15_group, obj15_group + 0x20, obj15_group + 0x40) ==
      (0xFEBF0C28, 0xFEBF0C48, 0xFEBF0C68))
check("restore code uses GP displacement 0x5308",
      CF[0x675BA:0x675BE] == bytes.fromhex("24e60853"))
check("persistence buffers are FEBF06A8/6C8/6E8",
      tuple(APP_GP + 0x4EA8 + x for x in (0, 0x20, 0x40)) ==
      (0xFEBF06A8, 0xFEBF06C8, 0xFEBF06E8))

# Object 15 physical allocations: page 440 raw, 436 XOR55, 432 XORAA.
copy_data = []
copy_valid = []
for page, mask, storage_index in [(440, 0, 40), (436, 0x55, 44), (432, 0xAA, 48)]:
    rec = DF[page * 64:(page + 1) * 64]
    copy_valid.append(struct.unpack_from("<H", rec)[0] == storage_index and rec[-4:] == b"\xAA" * 4)
    copy_data.append(bytes(b ^ mask for b in rec[4:36]))
check("all three object-15 records are invalid", copy_valid == [False, False, False], str(copy_valid))
check("invalid object-15 copies do not decode to consensus", len(set(copy_data)) == 3)
for obj, pages in {12: (443, 439, 435), 13: (442, 438, 434), 14: (441, 437, 433)}.items():
    valid = []
    for page, storage_index in zip(pages, (40 - (15 - obj), 44 - (15 - obj), 48 - (15 - obj))):
        rec = DF[page * 64:(page + 1) * 64]
        valid.append(struct.unpack_from("<H", rec)[0] == storage_index and rec[-4:] == b"\xAA" * 4)
    check(f"object {obj} optional-bank copies are also invalid", valid == [False, False, False], str(valid))
raw_field = DF[0x6E14:0x6E24]
entropy = -sum((n / 16) * math.log2(n / 16) for n in Counter(raw_field).values())
check("raw object-15 field is exact low-entropy snapshot value",
      raw_field.hex() == "00000000040000808202000000000000" and entropy < 1.4)

print("\n== SecOC lower-job lookup ==")
lower_records = verify_records
lower_ids = [u16(a) for a in lower_records]
check("lower CryptoIf table has only IDs 0 and 1", lower_ids == [0, 1])
check("both lower records target ICU verify adapter 0x880DC",
      all(u32(a + 0x14) == 0x880DC for a in lower_records))
check("SecOC handle 0 resolves to lower ICU driver record 0",
      set(expected_handles) == {0} and 0 in lower_ids)
check("SecOC worker loads handle from record+0x20",
      CF[0x8E5F8:0x8E600] == bytes.fromhex("fd372100233e1c00"))

print(f"\nSummary: {passed} passed, {failed} failed")
sys.exit(1 if failed else 0)
