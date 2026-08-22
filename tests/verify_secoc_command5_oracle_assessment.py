#!/usr/bin/env python3
"""Verify the exact capability boundary of the Sienna command-5 crypto-test oracle."""
from __future__ import annotations

import hashlib
import struct
import sys
from pathlib import Path

from Crypto.Cipher import AES
from Crypto.Hash import CMAC

REPO = Path(__file__).resolve().parents[1]
CF = (REPO / "firmware" / "RH850_P1M-E_CodeFlash.bin").read_bytes()
REPORT = REPO / "docs" / "security" / "secoc" / "command5-oracle-assessment.md"
SLEIGH_ARITH = REPO / "ghidra" / "ghidra_v850" / "data" / "languages" / "v850_arithmetic.sinc"
passed = failed = 0


def check(name: str, condition: object, detail: str = "") -> None:
    global passed, failed
    ok = bool(condition)
    passed += int(ok)
    failed += int(not ok)
    suffix = f" ({detail})" if detail else ""
    print(f"[{'PASS' if ok else 'FAIL'}] {name}{suffix}")


def u16(a: int) -> int:
    return struct.unpack_from("<H", CF, a)[0]


def u32(a: int) -> int:
    return struct.unpack_from("<I", CF, a)[0]


def body_hash(a: int, n: int) -> str:
    return hashlib.sha256(CF[a:a+n]).hexdigest()


def dbl(block: bytes) -> bytes:
    x = int.from_bytes(block, "big")
    carry = (x >> 127) & 1
    x = ((x << 1) & ((1 << 128) - 1)) ^ (0x87 if carry else 0)
    return x.to_bytes(16, "big")


print("== stock no-SA bank is fixed to one 16-byte CMAC message ==")
check("bank-1 submit body pinned", body_hash(0x68B42, 128) == "2b7634bb6d42aa8173c53a5f43b8a88dcc12dedd89b9ceba35a728c8ad509b58")
check("mode-1 command-5 call uses literal 16-byte input/output length",
      CF[0x68B8A:0x68B92] == bytes.fromhex("204e1000644f6198"), CF[0x68B8A:0x68B92].hex())
check("mode-1 message pointer is FEBE517A and dispatch is 0x88350",
      CF[0x68B9A:0x68BB0] == bytes.fromhex("24467a99900b240eaa99010d240e6098030d81ffa4f7"))
check("full generated-result comparator body pinned", body_hash(0x69068, 38) == "9d34d1c1fff4dd34ac338c530e539f3663362db2c6ab4758065f7ac70c062173")

TP = 0x23EE4
BASE = TP + 0x1A8C
SIZE = 0x50
records = [BASE + i * SIZE for i in range(6)]
secured = [u32(a + 0x3C) for a in records]
trailers = [u16(a + 0x06) for a in records]
fv_bits = [CF[a + 0x14] for a in records]
payload = [n - t for n, t in zip(secured, trailers)]
auth_len = [2 + p + ((f + 7) // 8) for p, f in zip(payload, fv_bits)]
check("SecOC authenticated lengths are sync7/classic12/FD36",
      auth_len == [7, 12, 12, 12, 36, 36], repr(auth_len))
check("stock 16-byte bank length matches none of the Sienna SecOC profiles", 16 not in auth_len)

print("\n== CMAC length is cryptographically material ==")
key = bytes(range(16))
aes = AES.new(key, AES.MODE_ECB)
L = aes.encrypt(bytes(16))
k1 = dbl(L)
k2 = dbl(k1)
m12 = bytes(range(12))
padded12 = m12 + b"\x80" + bytes(3)
manual12 = aes.encrypt(bytes(a ^ b for a, b in zip(padded12, k2)))
c12 = CMAC.new(key, ciphermod=AES); c12.update(m12)
c16 = CMAC.new(key, ciphermod=AES); c16.update(m12 + bytes(4))
check("12-byte CMAC uses the incomplete-block K2 rule", manual12 == c12.digest())
check("same 12 bytes zero-extended to 16 produce a different CMAC", c12.digest() != c16.digest())
check("K1 and K2 are distinct secret-derived finalization masks", k1 != k2)

print("\n== generic command-5 API is variable-length and covers real SecOC domains ==")
check("generic command-5 prepare body pinned", body_hash(0x87A94, 178) == "db56dcbbc3be5852d9baa94784b80ddcd26cc9aa704aa4537fb58850a32bcb23")
check("generic prepare admits input lengths below 0x51",
      CF[0x87ABA:0x87AC0] == bytes.fromhex("0806afffa10d"), CF[0x87ABA:0x87AC0].hex())
check("generic prepare converts byte length to bit length",
      CF[0x87B1E:0x87B26] == bytes.fromhex("24f6085ac3ea1e0e"), CF[0x87B1E:0x87B26].hex())
check("12-byte classic and 36-byte FD inputs both fit generic command-5", 12 < 0x51 and 36 < 0x51)

print("\n== no stock tester-to-driver length-smuggling path ==")
# The wrapper materializes both driver ID 1 and length 16 as immediates.  Neither
# comes from the tester-controlled message/selector buffers.
check("mode-1 wrapper materializes literal length 16 in r9",
      CF[0x68B8A:0x68B8E] == bytes.fromhex("204e1000"))
check("mode-1 wrapper materializes literal driver record id 1",
      CF[0x68B92:0x68B94] == bytes.fromhex("0132"))
# All five CAN inputs are fixed DLC-8 PDU descriptors.
check("CAN 01B..01F receive descriptors are all fixed DLC 8",
      [CF[0x22088 + i*8:0x22088 + (i+1)*8] for i in range(5)] ==
      [bytes.fromhex(f"{cid:02x}00000008000000") for cid in range(0x1B, 0x20)])
# The four opaque/group reads load literal 8 into r8 directly before the helper.
for site in (0x6884E, 0x6888A, 0x688C6, 0x68902):
    check(f"collector group copy at 0x{site+2:X} uses literal length 8",
          CF[site:site+2] == bytes.fromhex("0842"), CF[site:site+2].hex())
# Prepare stages the bit length into the private descriptor; the start routine
# later references the fixed descriptor root rather than the wrapper stack.
check("prepare shifts byte length left by 3 before descriptor construction",
      CF[0x87B22:0x87B24] == bytes.fromhex("c3ea"), CF[0x87B22:0x87B24].hex())
check("command-5 start addresses prepared descriptor FEBF1208",
      CF[0x87C8A:0x87C8E] == bytes.fromhex("2436085a"), CF[0x87C8A:0x87C8E].hex())
# Primary application UDS service table contains 17 records and no SID 0x3D.
service_sids = [CF[0x25E28 + i*0x18 + 0x10] for i in range(17)]
check("primary application UDS service set is exact and has no WriteMemoryByAddress 0x3D",
      service_sids == [0x10,0x11,0x14,0x19,0x22,0x23,0x27,0x28,0x2E,0x31,0x34,0x36,0x37,0x3E,0x85,0xAB,0xBA],
      repr([hex(x) for x in service_sids]))
check("known XCP write window cannot reach command-5 prepared state",
      0xFEBFFBFF < 0xFEBF1208 or 0xFEBF7C00 > 0xFEBF1287)

check("generic output-copy body pinned", body_hash(0x87B46, 116) == "c62fc5e48366ad9f56eb73694bfa1481eaba9045f09d36dc751fc264e54f4be2")
check("output copy clamps only values above 16, so capacity 12 remains 12",
      CF[0x87B82:0x87B90] == bytes.fromhex("00450806efffb905204610000145"), CF[0x87B82:0x87B90].hex())

print("\n== bounded classic-12 adaptation ==")
stock_len_insn = CF[0x68B8A:0x68B8E]
classic_len_insn = bytes.fromhex("204e0c00")
check("stock length instruction is movea 0x10", stock_len_insn == bytes.fromhex("204e1000"), stock_len_insn.hex())
check("candidate classic rewrite changes only immediate 0x10 -> 0x0C",
      classic_len_insn[:2] == stock_len_insn[:2] and classic_len_insn[3:] == stock_len_insn[3:] and classic_len_insn != stock_len_insn)
sleigh = SLEIGH_ARITH.read_text(encoding="utf-8")
check("processor definition binds MOVEA immediate to signed s1631",
      ":movea s1631, R0004, r1115" in sleigh and "r1115 = R0004 + s1631" in sleigh)
check("12-byte output capacity still exposes more than transmitted MAC28", 12 * 8 > 28)

print("\n== neighboring raw-AES test is also fixed to one block ==")
check("command-1/3 test prepare body pinned", body_hash(0x8768E, 132) == "106d6cbad4051030f54b4c4cfeeee82bd7b835e8499c145da798d9a6e89b8a56")
check("command-1/3 test rejects any input length other than 16",
      CF[0x876B0:0x876B6] == bytes.fromhex("0806f0ffb205"), CF[0x876B0:0x876B6].hex())
check("low-level command-1/3 engine body pinned", body_hash(0x8954C, 228) == "e8577a1f8729e6ca4c261732427577f4b0ba3cce6388261993564682536429eb")
check("mode-0 AES result comparator body pinned", body_hash(0x69042, 38) == "10c5b80d77807fad9d88cc10e3eeb2b5c6d984e522a6a4a5c951a3d318dafa5f")
gp = 0xFEBEB800
mode0_disp = int.from_bytes(bytes.fromhex("9a99"), "little", signed=True)
mode1_disp = int.from_bytes(bytes.fromhex("aa99"), "little", signed=True)
check("mode-0 observation displacement 0x999A resolves to FEBE519A", gp + mode0_disp == 0xFEBE519A)
check("existing command-5 observer displacement 0x99AA resolves to FEBE51AA", gp + mode1_disp == 0xFEBE51AA)
check("mode-0 observer source instruction is 24 96 9A 99", bytes.fromhex("24969a99")[2:] == bytes.fromhex("9a99"))

print("\n== documentation boundary ==")
text = REPORT.read_text(encoding="utf-8") if REPORT.exists() else ""
for token in (
    "not a production secoc signing oracle",
    "exactly 16 bytes",
    "12 bytes",
    "36 bytes",
    "0x68b8a",
    "0x87a94",
    "cmac usage",
    "vendor extension",
    "freshness",
    "command 1/3",
    "length-smuggling",
    "writememorybyaddress",
):
    check(f"assessment records {token}", token in text.lower())

print(f"\nSummary: {passed} passed, {failed} failed")
sys.exit(1 if failed else 0)
