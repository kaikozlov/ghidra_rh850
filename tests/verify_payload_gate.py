#!/usr/bin/env python3
"""Verify the bootloader payload acceptance/execution findings without Ghidra.

Reads the committed CodeFlash and pinned public-payload fixtures directly. The
fixtures' upstream provenance is checked separately by verify_external_corroboration.py.
"""
from pathlib import Path
import binascii
import hashlib
import struct
import sys

from Crypto.Cipher import AES
from Crypto.Hash import CMAC

REPO = Path(__file__).resolve().parents[1]
CF = (REPO / "firmware" / "RH850_P1M-E_CodeFlash.bin").read_bytes()
PAYLOAD_BUILD_SECRET = bytes.fromhex("ba052435f8843f985fd1329d2b6117b0")
DID_201_KEY = bytes(16)
DID_202_IV = bytes(16)
DERIVED_KEY = AES.new(PAYLOAD_BUILD_SECRET, AES.MODE_ECB).encrypt(DID_201_KEY)

passed = failed = 0

def check(name, condition, detail=""):
    global passed, failed
    if condition:
        passed += 1
        print(f"[PASS] {name}" + (f" ({detail})" if detail else ""))
    else:
        failed += 1
        print(f"[FAIL] {name}" + (f" ({detail})" if detail else ""))

def words(addr, count):
    return struct.unpack_from("<" + "I" * count, CF, addr)

print("== CodeFlash and bootloader tables ==")
check("CodeFlash SHA-256",
      hashlib.sha256(CF).hexdigest() ==
      "21140bbd65e530a9e518a3e84e20e5d85679675bc09cc724cb177bb7c76bafde")

# Memory-access table used by RequestDownload/RoutineControl (3 x 16 bytes).
access = [words(0x8DA0 + i * 16, 4) for i in range(3)]
check("downloadable RAM range is 0xFEBF0000..0xFEBF0FFF",
      access[2][:3] == (0xFEBF0000, 0xFEBF0FFF, 0x33), str(tuple(hex(x) for x in access[2])))

# Region table (3 x 28 bytes). RAM row contains the CMAC-tag and CRC descriptor metadata.
regions = [words(0x8E00 + i * 28, 7) for i in range(3)]
ram_region = regions[2]
check("RAM region CMAC tag address is 0xFEBF0FF0",
      ram_region[:3] == (0xFEBF0000, 0xFEBF0FFF, 0xFEBF0FF0),
      str(tuple(hex(x) for x in ram_region)))
check("RAM region has one CRC descriptor at 0x8DF0",
      ram_region[5:] == (1, 0x8DF0))

# CRC descriptor: data address, length, pointer to embedded address, pointer to embedded length.
crc_desc = words(0x8DF0, 4)
check("RAM CRC descriptor matches builder trailer",
      crc_desc == (0xFEBF0000, 0xFF0, 0xFEBF0FE0, 0xFEBF0FE4),
      str(tuple(hex(x) for x in crc_desc)))

# Five RoutineControl entries: default result, RID, allowed subfunction, option length, state.
routines = []
for i in range(5):
    routines.append(struct.unpack_from("<I H B B I", CF, 0x8F44 + i * 12))
check("RoutineControl IDs",
      [r[1] for r in routines] == [0x10F0, 0x10F1, 0x10F2, 0x10F3, 0xFF00])
check("0x10F0 and 0xFF00 require START + 10 option bytes",
      routines[0][2:4] == (1, 10) and routines[4][2:4] == (1, 10))

print("\n== Download / decrypt / erase control flow ==")
services = {
    sid: handler
    for sid, _mask, _rsv, handler in (
        struct.unpack_from("<BBHI", CF, 0x8E54 + i * 8) for i in range(20)
    )
}
check("SID 0x34 RequestDownload handler is 0x5D68", services[0x34] == 0x5D68)
check("SID 0x36 TransferData handler is 0x4DBA", services[0x36] == 0x4DBA)
check("SID 0x37 TransferExit handler is 0x5C92", services[0x37] == 0x5C92)
check("SID 0x31 RoutineControl handler is 0x567E", services[0x31] == 0x567E)

check("RequestDownload calls payload crypto init wrapper",
      CF[0x5F1A:0x5F1E] == bytes.fromhex("80ff8e0c"), CF[0x5F1A:0x5F1E].hex())
check("crypto init wrapper calls payload_crypto_initialize",
      CF[0x6BA8:0x6BB0] == bytes.fromhex("8007210080ff2805"),
      CF[0x6BA8:0x6BB0].hex())
check("payload_crypto_initialize calls derive then CBC/CMAC init",
      CF[0x70D4:0x70E0] == bytes.fromhex("80072100bfff90ffbfffbeff"),
      CF[0x70D4:0x70E0].hex())

check("TransferData dispatches active download path to 0x4B7C",
      CF[0x4DD6:0x4DDE] == bytes.fromhex("620aca05bfffa2fd"),
      CF[0x4DD6:0x4DDE].hex())
check("TransferData enqueue calls payload_decrypt_enqueue",
      CF[0x4C72:0x4C76] == bytes.fromhex("80ff421f"), CF[0x4C72:0x4C76].hex())
check("TransferData path rejects bad chunk length with NRC 0x31",
      bytes.fromhex("20363100") in CF[0x4B7C:0x4DBA])
check("TransferData enqueue-failure path emits NRC 0x72",
      CF[0x4C7A:0x4C7E] == bytes.fromhex("20367200"))

check("decrypt task calls CBC wrapper 0x7108",
      CF[0x6C06:0x6C0A] == bytes.fromhex("80ff0205"), CF[0x6C06:0x6C0A].hex())
check("decrypt task advances pointers by one AES block",
      CF[0x6C10:0x6C14] == bytes.fromhex("010e1000"), CF[0x6C10:0x6C14].hex())

check("TransferExit finalizes payload crypto through 0x6BD2",
      CF[0x5CE6:0x5CEA] == bytes.fromhex("80ffec0e"), CF[0x5CE6:0x5CEA].hex())
check("payload_crypto_finalize wrapper sits at 0x6BD2",
      CF[0x6BD2:0x6BDA] == bytes.fromhex("8007210080ff2605"),
      CF[0x6BD2:0x6BDA].hex())

check("RoutineControl CRC path calls queue helper 0x47BA",
      CF[0x57C4:0x57C8] == bytes.fromhex("bffff6ef"), CF[0x57C4:0x57C8].hex())
check("RoutineControl erase path calls flash_erase_start",
      CF[0x58B4:0x58B8] == bytes.fromhex("bfff2ce9"), CF[0x58B4:0x58B8].hex())
check("CMAC verify path calls payload_cmac_verify_enqueue",
      CF[0x5978:0x597C] == bytes.fromhex("80ff4215"), CF[0x5978:0x597C].hex())
check("RAM verifier/erase workers contain NRC 0x72 failure sites",
      CF[0x5936:0x5C00].count(bytes.fromhex("20367200")) >= 2)

check("main loop invokes flash_operation_task",
      CF[0x1388:0x138C] == bytes.fromhex("80ffa030"), CF[0x1388:0x138C].hex())
check("flash task reaches driver call-block at 0x4332",
      CF[0x44A8:0x44AC] == bytes.fromhex("bfff8afe"), CF[0x44A8:0x44AC].hex())
check("flash_erase_start prologue is at 0x41E0",
      CF[0x41E0:0x41E4] == bytes.fromhex("8807e110"), CF[0x41E0:0x41E4].hex())
check("flash_operation_task prologue is at 0x4428",
      CF[0x4428:0x442C] == bytes.fromhex("8207e130"), CF[0x4428:0x442C].hex())
check("erase engine function prologue is at 0x4332",
      CF[0x4332:0x4336] == bytes.fromhex("8207e110"), CF[0x4332:0x4336].hex())

# Exact RH850 sequence used twice by the flash engine:
#   movhi 0xFEBF,r0,r29; ld.w 0xFD0[r29],r29; ...; jarl r29,lp
check("flash callback load at 0x434C reads RAM 0xFEBF0FD0",
      CF[0x434C:0x4354] == bytes.fromhex("40eebffe3defd10f"), CF[0x434C:0x4354].hex())
check("flash callback indirect call at 0x435E",
      CF[0x435E:0x4362] == bytes.fromhex("fdc760f9"), CF[0x435E:0x4362].hex())
check("second callback load/call at 0x4402/0x440E",
      CF[0x4402:0x440E] == bytes.fromhex("40eebffe234e03003defd10f") and
      CF[0x440E:0x4412] == bytes.fromhex("fdc760f9"))

print("\n== Pinned public encrypted-payload fixtures ==")
payloads = [
    (
        "RAM-dump payload",
        REPO / "tests/fixtures/payloads/ram_dump_payload.bin",
        "d972d4bf432685217591768600a9abd7820d35b04a72270edc87074365356be2",
    ),
    (
        "DataFlash-dump payload",
        REPO / "tests/fixtures/payloads/dataflash_dump_payload.bin",
        "d48988366b5e6d2ddd7438caca5e6f6f02daba9b650263c323a2ffd770a06e34",
    ),
]
for label, path, expected_sha256 in payloads:
    ciphertext = path.read_bytes()
    plaintext = AES.new(DERIVED_KEY, AES.MODE_CBC, DID_202_IV).decrypt(ciphertext)
    check(f"{label}: pinned SHA-256", hashlib.sha256(ciphertext).hexdigest() == expected_sha256)
    check(f"{label}: encrypted size is 0x1000", len(ciphertext) == 0x1000)
    check(f"{label}: callback slot points to payload base",
          struct.unpack_from("<I", plaintext, 0xFD0)[0] == 0xFEBF0000)
    check(f"{label}: embedded CRC address/length",
          struct.unpack_from("<II", plaintext, 0xFE0) == (0xFEBF0000, 0xFF0))
    check(f"{label}: CRC32 residue over 0xFF0 bytes",
          (binascii.crc32(plaintext[:0xFF0]) & 0xFFFFFFFF) == 0xFFFFFFFF)
    cmac = CMAC.new(DERIVED_KEY, ciphermod=AES)
    cmac.update(DID_202_IV + plaintext[:0xFF0])
    check(f"{label}: CMAC(IV || plaintext[0:0xFF0])",
          cmac.digest() == plaintext[0xFF0:0x1000])
    check(f"{label}: AES-CBC round trip",
          AES.new(DERIVED_KEY, AES.MODE_CBC, DID_202_IV).encrypt(plaintext) == ciphertext)

check("derived zero-DID key",
      DERIVED_KEY.hex() == "80d221a05622b4f9d4f287922e6c78d1", DERIVED_KEY.hex())

print(f"\n== RESULT: {passed} passed, {failed} failed ==")
sys.exit(1 if failed else 0)
