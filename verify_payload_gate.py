#!/usr/bin/env python3
"""Verify the bootloader payload acceptance/execution findings without Ghidra.

Reads the committed CodeFlash image and public encrypted payloads directly.
Requires PyCryptodome. Exits nonzero on any mismatch.
"""
from pathlib import Path
import binascii
import hashlib
import struct
import sys

from Crypto.Cipher import AES
from Crypto.Hash import CMAC

HERE = Path(__file__).resolve().parent
REPOS = HERE.parent
CF = (HERE / "RH850_P1M-E_CodeFlash.bin").read_bytes()
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

# Exact RH850 sequence used twice by the flash engine:
#   movhi 0xFEBF,r0,r29; ld.w 0xFD0[r29],r29; ...; jarl r29,lp
check("flash callback load at 0x434C reads RAM 0xFEBF0FD0",
      CF[0x434C:0x4354] == bytes.fromhex("40eebffe3defd10f"), CF[0x434C:0x4354].hex())
check("flash callback indirect call at 0x435E",
      CF[0x435E:0x4362] == bytes.fromhex("fdc760f9"), CF[0x435E:0x4362].hex())
check("second callback load/call at 0x4402/0x440E",
      CF[0x4402:0x440E] == bytes.fromhex("40eebffe234e03003defd10f") and
      CF[0x440E:0x4412] == bytes.fromhex("fdc760f9"))

print("\n== Public encrypted payloads ==")
payload_paths = [
    REPOS / "secoc/payload.bin",
    REPOS / "calvinpark-openpilot/tsk/lib/payload.bin",
    REPOS / "calvinpark-openpilot/tsk/lib/payload_dataflash_ff200000_ff208000.bin",
    REPOS / "tsk_extraction_by_can_log/payload_dataflash_ff200000_ff208000.bin",
]
plaintexts = []
for path in payload_paths:
    ciphertext = path.read_bytes()
    plaintext = AES.new(DERIVED_KEY, AES.MODE_CBC, DID_202_IV).decrypt(ciphertext)
    plaintexts.append(plaintext)
    label = str(path.relative_to(REPOS))
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

check("Willem and Calvin RAM payload binaries are identical", plaintexts[0] == plaintexts[1])
check("thehui and Calvin DataFlash payload binaries are identical", plaintexts[2] == plaintexts[3])
check("derived zero-DID key",
      DERIVED_KEY.hex() == "80d221a05622b4f9d4f287922e6c78d1", DERIVED_KEY.hex())

print(f"\n== RESULT: {passed} passed, {failed} failed ==")
sys.exit(1 if failed else 0)
