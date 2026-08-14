#!/usr/bin/env python3
"""Verify the 45-byte application RDBI stale-response disclosure chain."""
from __future__ import annotations

import hashlib
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CF = (ROOT / "firmware" / "RH850_P1M-E_CodeFlash.bin").read_bytes()
passed = failed = 0


def check(name: str, condition: bool, detail: str = "") -> None:
    global passed, failed
    if condition:
        passed += 1
        print(f"[PASS] {name}")
    else:
        failed += 1
        print(f"[FAIL] {name}" + (f" ({detail})" if detail else ""))


def u16(addr: int) -> int:
    return struct.unpack_from("<H", CF, addr)[0]


def u32(addr: int) -> int:
    return struct.unpack_from("<I", CF, addr)[0]


def sha(start: int, size: int) -> str:
    return hashlib.sha256(CF[start : start + size]).hexdigest()


def decode_long_branch(addr: int) -> tuple[str, int] | None:
    w0, w1 = struct.unpack_from("<HH", CF, addr)
    if ((w0 >> 6) & 0x1F) != 0x1E or (w1 & 1):
        return None
    reg2 = (w0 >> 11) & 0x1F
    high = w0 & 0x3F
    if high & 0x20:
        high -= 0x40
    return ("jarl" if reg2 else "jr"), addr + (high << 16) + w1


print("== configured 45-byte no-op DID family ==")
DID_TABLE = 0x2941C
expected_dids = tuple(range(0x1CF4, 0x1D00)) + (0x1D01, 0x1D02, 0x1D03)
rows = []
for index in range(242):
    off = DID_TABLE + index * 16
    did, size = struct.unpack_from("<HH", CF, off)
    callback, auxiliary, tail = struct.unpack_from("<III", CF, off + 4)
    if did in expected_dids:
        rows.append((index, did, size, callback, auxiliary, tail))
check("exactly 15 no-op DIDs are configured", len(rows) == 15, repr(rows))
check("no-op DID set is exactly 1CF4..1CFF plus 1D01..1D03", tuple(r[1] for r in rows) == expected_dids)
check("all no-op DIDs declare 45 response bytes", all(r[2] == 45 for r in rows))
check("callbacks are contiguous 4-byte stubs 0x4E40C..0x4E444", tuple(r[3] for r in rows) == tuple(range(0x4E40C, 0x4E448, 4)))
check("all 15 rows share auxiliary callback 0x4C816", all(r[4] == 0x4C816 for r in rows))
check("all 15 rows use direct record-operation selector 0", all(r[5] == 0 for r in rows))
check("1D00 is deliberately not part of the no-op family", u16(DID_TABLE + 206 * 16) == 0x1D00 and u16(DID_TABLE + 206 * 16 + 2) == 32 and u32(DID_TABLE + 206 * 16 + 4) == 0x4EA16)
check("15 producer stubs are exactly mov 0,r10; jmp lp", CF[0x4E40C:0x4E448] == bytes.fromhex("00527f00") * 15)

print("\n== DID class selects direct record operation 2 ==")
record = 0x26248
check("class record 2 callback slots are 934E6/93578/9361A", tuple(u32(record + o) for o in (0, 4, 8)) == (0x934E6, 0x93578, 0x9361A))
check("class record 2 policy pointer is 0x26164", u32(record + 0x10) == 0x26164)
check("class record 2 covers 0x1000..0x2000", (u16(record + 0x14), u16(record + 0x16)) == (0x1000, 0x2000))
check("class record 2 is enabled", CF[record + 0x18] == 1)
check("record-2 policy advertises only direct-read capability", u32(0x26164) == 0 and u32(0x26168) == 0x26134 and u32(0x2616C) == 0)
check("direct-mode selector body is pinned", sha(0x941C6, 156) == "3cfaae9de92f13797a2d42811d27fe113e7f536c5105017e3908d63e5a30839b")
check("direct RDBI worker body is pinned", sha(0x9429E, 392) == "e8d48150f644cfec8ae372f5688d3ccb9cc0f973266d178050a18c77f6deb022")
check("direct-mode worker calls record-operation dispatcher at 0x9434A", decode_long_branch(0x9434A) == ("jarl", 0x92810))
check("record-operation dispatcher body is pinned", sha(0x92810, 72) == "fbe313da88bafb3121ed279d07abb23a1802364dc77fa720294f044197f4ee31")
check("record-operation 2 wrapper is pinned", sha(0x9361A, 48) == "c41adb4c5f95502066735a1341d677ff774a38b56299d5ccb9911731b29d28af")
check("record-operation 2 calls direct DID producer helper", decode_long_branch(0x93632) == ("jarl", 0x8A374))

print("\n== immediate success preserves declared length ==")
check("DID size/producer helper body is pinned", sha(0x8A374, 270) == "0212497b4b74bf09682aeebdaabab5c5f60adb04bddd84e5f9094b276c9cd80f")
check("declared-size helper body is pinned", sha(0x8A31E, 12) == "a77a507740a47bac1347d4aa9b8c6e89bc36cd60a9b79ac2f1620a6af2c08b17")
check("configured producer dispatcher body is pinned", sha(0x4CB8A, 52) == "28856781365cd615d4f5bc16605af83efc7098321c21e290158bf4cf53b1c05f")
check("row-size helper body is pinned", sha(0x4C81A, 42) == "5169fcc5a9e6f4799c1714109bb13eed2d0710c32cb67103fbf664a60d4e9f9a")
check("8A374 obtains declared DID size", decode_long_branch(0x8A39A) == ("jarl", 0x8A31E))
check("8A374 invokes configured DID producer", decode_long_branch(0x8A3BE) == ("jarl", 0x4CB8A))
# On return==0, branch 0x8A3D0 skips the pending/error blocks at 0x8A3D4..0x8A42E,
# including every store that zeros the caller's output length.
check("immediate producer result is captured before pending/error handling", CF[0x8A3C2:0x8A3C8] == bytes.fromhex("0ae001daf52d"))
check("direct result helper does not clear producer output", sha(0x8A32A, 74) == "00e752508fd23bc38345c194b5a26bcf84be76e7e6f70057289380e5becba699")

print("\n== shared fixed Dcm response buffer is not cleared ==")
check("transport handoff body is pinned", sha(0x8FEF4, 120) == "cdfc41e7a404a075c0548570015c7b2e3c38dbaa97486a6568dc98b76adfc13e")
check("transport handoff obtains fixed response buffer", decode_long_branch(0x8FF56) == ("jarl", 0x91FD0))
check("transport handoff calls Dcm service dispatcher", decode_long_branch(0x8FF64) == ("jarl", 0x8F850))
check("Dcm service-dispatch body is pinned", sha(0x8F850, 248) == "ccd0d855b6c7d6e7335be257207421c7bd7f87898c04d36112f744e63aa5e27e")
check("Dcm dispatcher initializes context without clearing response data", decode_long_branch(0x8F868) == ("jarl", 0x8F6AC))
check("Dcm direct-service positive-response helper is pinned", sha(0x8F6FA, 86) == "5fc2d9ec072601f5ec0e2801476d4db4a75bc2770d402c902a44d5b0bc00dffa")
check("positive-response helper writes SID then advances response pointer by one", CF[0x8F704:0x8F716] == bytes.fromhex("939f0100939e4000419f0000000d410a010d"))
check("service-context constructor is pinned", sha(0x8F6AC, 40) == "e52dbb4f511e2245cbd37c8d9c9d77419c637b3753139b59e19428d514bebf26")
check("response-buffer provider is pinned", sha(0x91FD0, 72) == "78426256544bced0e16b7f96deabf056b3da14aaaea1e24738fd5c3732a6a498")
check("response-buffer provider constructs fixed GP-relative FEBE59F8 pointer", CF[0x91FEA:0x91FF2] == bytes.fromhex("240ef8a17d0f0100"))
check("response-buffer init helper is pinned", sha(0x91DA4, 94) == "a07f8a1c92b76a68c06383db2df5608f1a6eaed4a7ee962693586e8fa25db47e")
check("response-buffer reset helper is pinned", sha(0x91F84, 52) == "52ffd38a32962ee9b10ebec9ed585e1294c6ae3e77b0c4ee0e16acd84d97deb1")
# Both known reset sites use st.b r0 to the first byte only. No memset/loop exists
# in either pinned body; the live Ghidra verifier separately pins full xref topology.
check("startup clears only the first response-buffer byte", CF[0x91DAC:0x91DB0] == bytes.fromhex("4407f8a1"))
check("connection reset clears only first request/response bytes", CF[0x91F8A:0x91F8E] == bytes.fromhex("4407f8a1"))

print("\n== response geometry ==")
check("RDBI request-start body is pinned", sha(0x944C6, 104) == "213ea4e983a4cc1952747cc4610a9d73f049a02c8e0314a8f5b279ef83200f45")
check("45 stale bytes follow positive SID plus two-byte DID", 1 + 2 + 45 == 48)
check("a 47-byte seed response leaves exactly bytes 2..46 available for the next 45-byte leak", len(bytes(range(47))[2:47]) == 45)

print(f"\nSummary: {passed} passed, {failed} failed")
sys.exit(1 if failed else 0)
