#!/usr/bin/env python3
"""Verify the software-first ICU-S investigation boundaries from raw firmware.

This suite intentionally separates four claims:
- obvious application transport/memory-service overwrite paths are bounded;
- an accepted bootloader payload is a constructible arbitrary-code callback;
- the dormant command-5 harness is not stock-remotely activated; and
- existing command-5 / DID-1010 paths provide concrete command-control and
  output-transport templates, without claiming that command 13 exports a key.
"""
from __future__ import annotations

import binascii
import hashlib
import struct
import sys
from pathlib import Path

from Crypto.Cipher import AES
from Crypto.Hash import CMAC

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
        print(f"FAIL: {name}" + (f" ({detail})" if detail else ""))


def u16(address: int) -> int:
    return struct.unpack_from("<H", CF, address)[0]


def u32(address: int) -> int:
    return struct.unpack_from("<I", CF, address)[0]


def body_hash(address: int, size: int) -> str:
    return hashlib.sha256(CF[address : address + size]).hexdigest()


check(
    "pinned CodeFlash",
    hashlib.sha256(CF).hexdigest()
    == "21140bbd65e530a9e518a3e84e20e5d85679675bc09cc724cb177bb7c76bafde",
)

print("\n== application transport and null memory services ==")
# Three application Dcm route records: capacity then buffer pointer.
check(
    "three diagnostic routes have 256-byte buffers",
    [u32(0x26064 + index * 8) for index in range(3)] == [0x100, 0x100, 0x100],
)
check(
    "application start-of-reception body is pinned",
    body_hash(0x903A8, 148)
    == "62a1f8d1faae310e1943896951270fd2db6c7f5f7518c5ff678e64b40b8e2281",
)
check(
    "application CopyRxData body is pinned",
    body_hash(0x9043C, 128)
    == "5170b1cd9071763145f139f11d39bfa0e43cea164fba3010705aac083e404484",
)
check(
    "bounded byte-copy body is pinned",
    body_hash(0x920D2, 74)
    == "c085acef78b04cf4cca08528e58736eb02eb82b833e4bc8f3399ffd4d8294092",
)

APP_SERVICE = struct.Struct("<IIBBBBIII")
services = [APP_SERVICE.unpack_from(CF, 0x25E30 + index * APP_SERVICE.size) for index in range(17)]
by_sid = {row[2]: row for row in services}
for sid in (0x23, 0x34, 0x36, 0x37):
    row = by_sid[sid]
    check(
        f"application SID 0x{sid:02X} has no subfunction or service callback",
        row[3] == 0 and row[7] == 0,
        repr(row),
    )
check("application DSP start hook is compiled off", CF[0x25DCC] == 0)
check(
    "generic positive-response body is pinned",
    body_hash(0x8F6FA, 86)
    == "5fc2d9ec072601f5ec0e2801476d4db4a75bc2770d402c902a44d5b0bc00dffa",
)

print("\n== WDBI exact sizing ==")
check("write-DID count is 19", CF[0x26666] == 19)
check(
    "WDBI exact-input validator is pinned",
    body_hash(0x95624, 162)
    == "8c1b46acc28801e3e5ad7dcb257a9bb439351b0f355ea67bf35bc2bb43150e1a",
)
check(
    "WDBI output-capacity validator is pinned",
    body_hash(0x956C6, 212)
    == "57a242d13a31e9c4ecc21e3e5b69a1e44fcfaee0d693754e76a38a06b46aae3c",
)

write_rows = [
    struct.unpack_from("<HBBI", CF, 0x26AEC + index * 8)
    for index in range(CF[0x26666])
]
size_bits = CF[0x263AC : 0x263AC + 32]


def descriptor_width(pointer_table: int, count_table: int, index: int) -> int:
    count = CF[count_table + index * 15]
    if count == 0:
        return 0
    descriptor = u32(pointer_table + index * 4) + (count - 1) * 6
    field_type = CF[descriptor + 1]
    # Firmware-generated type 7 is the variable-width byte-array descriptor;
    # its bit width is held directly at +2. Other field types use 0x263AC.
    base_bits = u16(descriptor + 2) if field_type == 7 else size_bits[field_type]
    bit_offset = u16(descriptor + 4)
    return (base_bits + bit_offset + 7) // 8


selector1_inputs = [descriptor_width(0x2686C, 0x26B93, i) for i in range(19)]
selector1_outputs = [descriptor_width(0x268BC, 0x26B95, i) for i in range(19)]
selector3_outputs = [descriptor_width(0x267CC, 0x26B90, i) for i in range(19)]
check("maximum configured WDBI input is 64 bytes", max(selector1_inputs) == 64)
check(
    "DID 0x1010 is the 64-byte input / 49-byte output record",
    write_rows[9][0] == 0x1010
    and selector1_inputs[9] == 64
    and selector1_outputs[9] == 49
    and selector3_outputs[9] == 49,
)
check("largest WDBI request including selector/DID is 67 bytes", max(selector1_inputs) + 3 == 67)

print("\n== constructible authenticated bootloader callback ==")
PAYLOAD_BUILD_SECRET = bytes.fromhex("ba052435f8843f985fd1329d2b6117b0")
check("payload-build secret is pinned at CodeFlash 0xBFD8", CF[0xBFD8:0xBFE8] == PAYLOAD_BUILD_SECRET)
access_row = struct.unpack_from("<IIII", CF, 0x8DA0 + 2 * 16)
check(
    "bootloader accepts the 4 KiB RAM payload window",
    access_row[:3] == (0xFEBF0000, 0xFEBF0FFF, 0x33),
)
check(
    "flash engine loads and calls payload-controlled callback",
    CF[0x434C:0x4354] == bytes.fromhex("40eebffe3defd10f")
    and CF[0x435E:0x4362] == bytes.fromhex("fdc760f9"),
)

payload_secrets = {
    "candidate_f05_dataflash_payload.bin": CF[0xBFE8:0xBFF8],
    "dataflash_dump_payload.bin": PAYLOAD_BUILD_SECRET,
    "ram_dump_payload.bin": PAYLOAD_BUILD_SECRET,
}
for path in sorted((REPO / "tests" / "fixtures" / "payloads").glob("*.bin")):
    ciphertext = path.read_bytes()
    secret = payload_secrets.get(path.name)
    check(f"{path.name}: build-secret mapping exists", secret is not None)
    if secret is None:
        continue
    fixture_derived_key = AES.new(secret, AES.MODE_ECB).encrypt(bytes(16))
    plaintext = AES.new(fixture_derived_key, AES.MODE_CBC, bytes(16)).decrypt(ciphertext)
    cmac = CMAC.new(fixture_derived_key, ciphermod=AES)
    cmac.update(bytes(16) + plaintext[:0xFF0])
    nonzero_code = [index for index, value in enumerate(plaintext[:0xFD0]) if value]
    check(f"{path.name}: accepted payload size", len(ciphertext) == 0x1000)
    check(
        f"{path.name}: callback starts at payload base",
        struct.unpack_from("<I", plaintext, 0xFD0)[0] == 0xFEBF0000,
    )
    check(
        f"{path.name}: CRC and CMAC are reproducible",
        (binascii.crc32(plaintext[:0xFF0]) & 0xFFFFFFFF) == 0xFFFFFFFF
        and cmac.digest() == plaintext[0xFF0:0x1000],
    )
    check(
        f"{path.name}: more than 0xE00 bytes remain before callback trailer",
        bool(nonzero_code) and 0xFD0 - 1 - nonzero_code[-1] >= 0xE00,
        hex(nonzero_code[-1] if nonzero_code else 0),
    )

print("\n== dormant harness and reusable command paths ==")
check(
    "bank-1 activator has no literal CodeFlash function-pointer entry",
    struct.pack("<I", 0x69018) not in CF,
)
check(
    "bank-1 activator body is pinned",
    CF[0x69018:0x69042]
    == bytes.fromhex(
        "80072100a40f8f98e009ea0d010a440f8f986407"
        "7a98200e1100440f9098bfff14efbfff88ff40063f00"
    ),
)
check("command-5 tracks ID 5 at 0x896DC", CF[0x896DC:0x896DE] == bytes.fromhex("050a"))
check(
    "command-5 submits selector-shifted ID 5 at 0x89734",
    CF[0x89734:0x8973A] == bytes.fromhex("d092920e0500"),
)
check(
    "completion compares ICUSCMD low ID with tracked ID",
    body_hash(0x89DE6, 58)
    == "814595c10b759f6dc32d1f9d36ed81bcd9c65b82048babfaea8857e77194c775",
)
check(
    "DID-1010 command-8 engine fixes four input and three output blocks",
    CF[0x899C2:0x899CC] == bytes.fromhex("040a640f2d5b030a640f"),
)
check("command-8 tracks ID 8 at 0x899E4", CF[0x899E4:0x899E6] == bytes.fromhex("080a"))
check("command-8 submits literal ID 8 at 0x89A2A", CF[0x89A2A:0x89A2C] == bytes.fromhex("080a"))
check(
    "command-11 has no input/output callback setup",
    CF[0x89A36:0x89A92].count(struct.pack("<I", 0x89448)) == 0
    and CF[0x89A36:0x89A92].count(struct.pack("<I", 0x894BE)) == 0,
)
check(
    "command-0x22 configures one input and two output blocks",
    CF[0x89B36:0x89B3C] == bytes.fromhex("010a640f2d5b")
    and CF[0x89B10:0x89B12] == bytes.fromhex("0252")
    and CF[0x89B5E:0x89B62] == bytes.fromhex("6457355b"),
)

print(f"\nSummary: {passed} passed, {failed} failed")
sys.exit(1 if failed else 0)
