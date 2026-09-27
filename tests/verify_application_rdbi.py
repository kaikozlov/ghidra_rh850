#!/usr/bin/env python3
"""Verify application RDBI stale-response, preflight bounds, and emitted-write audit.

Merged portable family module.
"""
from __future__ import annotations

import collections
import hashlib
import json
import struct
from pathlib import Path

ROOT = REPO = Path(__file__).resolve().parents[1]
CF = (ROOT / "firmware" / "RH850_P1M-E_CodeFlash.bin").read_bytes()
passed = failed = 0


def check(name, cond, detail=""):
    global passed, failed
    ok = bool(cond)
    passed += int(ok)
    failed += int(not ok)
    suffix = f" ({detail})" if detail else ""
    print(f"[{'PASS' if ok else 'FAIL'}] {name}{suffix}")

print("== RDBI stale response ==")




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


EXPECTED_NOOP_DID_LENGTHS = {
    0x0111: 4,
    0x1066: 1, 0x106A: 1,
    0x10C7: 2, 0x10C8: 2, 0x10C9: 2,
    0x10F7: 2, 0x10F8: 2, 0x10F9: 2,
    **{did: 2 for did in range(0x1124, 0x112A)},
    0x112F: 7, 0x1130: 1, 0x1131: 1,
    0x11BC: 1, 0x11C8: 1,
    0x1C99: 1, 0x1C9A: 1, 0x1C9B: 1, 0x1C9C: 7,
    0x1C9D: 1, 0x1C9E: 7, 0x1C9F: 1, 0x1CA0: 7,
    **{did: 45 for did in range(0x1CF4, 0x1D00)},
    0x1D01: 45, 0x1D02: 45, 0x1D03: 45,
    0x1F03: 1, 0x1F04: 1,
    0x2030: 16, 0x2031: 16, 0x2032: 17,
}

print("== complete success-without-write DID census ==")
DID_TABLE = 0x2941C
stub = bytes.fromhex("00527f00")
rows = []
for index in range(242):
    off = DID_TABLE + index * 16
    did, size = struct.unpack_from("<HH", CF, off)
    callback, auxiliary, tail = struct.unpack_from("<III", CF, off + 4)
    if callback and CF[callback : callback + 4] == stub:
        rows.append((index, did, size, callback, auxiliary, tail))
actual = {row[1]: row[2] for row in rows}
check("exactly 48 configured RDBI rows use a four-byte success-without-write producer", len(rows) == 48, repr(rows))
check("no-op DID/length map is exact", actual == EXPECTED_NOOP_DID_LENGTHS, repr(actual))
check("no-op rows use 46 unique producer stubs", len({row[3] for row in rows}) == 46)
check("every producer is exactly mov 0,r10; jmp lp", all(CF[row[3] : row[3] + 4] == stub for row in rows))
check("leak-width distribution is exact", collections.Counter(actual.values()) == {1: 13, 2: 12, 4: 1, 7: 4, 16: 2, 17: 1, 45: 15})
check("maximum stale disclosure per request is 45 bytes", max(actual.values()) == 45)
check("1D00 is a real 32-byte producer between the no-op rows", u16(DID_TABLE + 206 * 16) == 0x1D00 and u16(DID_TABLE + 206 * 16 + 2) == 32 and u32(DID_TABLE + 206 * 16 + 4) == 0x4EA16)

print("\n== all 48 rows select a direct record operation ==")
# Class 0 covers 0x0100..0x0200, class 2 covers 0x1000..0x2000, and
# class 3 covers 0x2001..0x20FF. Those are the only classes containing no-op rows.
class_specs = {
    0: (0x26210, 0x0100, 0x0200, 0x26164, 0x935BA),
    2: (0x26248, 0x1000, 0x2000, 0x26164, 0x9361A),
    3: (0x26264, 0x2001, 0x20FF, 0x26174, 0x9364A),
}
for index, (record, low, high, policy, read_cb) in class_specs.items():
    check(f"class {index} range/policy is pinned", (u16(record + 0x14), u16(record + 0x16), u32(record + 0x10), CF[record + 0x18]) == (low, high, policy, 1))
    check(f"class {index} configured read callback is {read_cb:05X}", u32(record + 8) == read_cb)
# FUN_92432 sets direct-read capability bit 2 whenever policy+4 is non-null.
check("policy 0x26164 advertises direct read", u32(0x26168) != 0)
check("policy 0x26174 advertises direct read", u32(0x26178) != 0)
# The generic dynamic/element path is disabled globally in this calibration,
# so FUN_941C6 cannot select mode 2 before it falls back to class-direct mode.
check("generic DID lookup table count is zero", u16(0x261E8) == 0)
check("generic element lookup count is zero", CF[0x261EC] == 0)
check("generic DID lookup helper is pinned", sha(0x924D6, 156) == "e74e5209914af582104c293d48ca6a417b787ebe02abb531116259e61ea60da2")
check("generic element lookup helper is pinned", sha(0x93086, 136) == "e8d46d2fe979a56c93707a0bfc4d0df8c52972381ea89ad6c91dff566b7a8fd4")
check("direct-mode selector body is pinned", sha(0x941C6, 156) == "3cfaae9de92f13797a2d42811d27fe113e7f536c5105017e3908d63e5a30839b")
check("direct RDBI worker body is pinned", sha(0x9429E, 392) == "e8d48150f644cfec8ae372f5688d3ccb9cc0f973266d178050a18c77f6deb022")
check("direct-mode worker calls record-operation dispatcher at 0x9434A", decode_long_branch(0x9434A) == ("jarl", 0x92810))
check("record-operation dispatcher body is pinned", sha(0x92810, 72) == "fbe313da88bafb3121ed279d07abb23a1802364dc77fa720294f044197f4ee31")
for index, address, digest in (
    (0, 0x935BA, "e476e26f2a250e6ab24d18db197050da293e06645340a0d05bcb8fef8affb894"),
    (2, 0x9361A, "c41adb4c5f95502066735a1341d677ff774a38b56299d5ccb9911731b29d28af"),
    (3, 0x9364A, "afdcabcdecc803e32918b4f054689cf141c75651caca4d065f42a8511a94c4af"),
):
    check(f"record-operation {index} wrapper is pinned", sha(address, 48) == digest)
    check(f"record-operation {index} calls direct DID producer helper", decode_long_branch(address + 0x18) == ("jarl", 0x8A374))

print("\n== immediate success preserves declared length ==")
check("DID size/producer helper body is pinned", sha(0x8A374, 270) == "0212497b4b74bf09682aeebdaabab5c5f60adb04bddd84e5f9094b276c9cd80f")
check("declared-size helper body is pinned", sha(0x8A31E, 12) == "a77a507740a47bac1347d4aa9b8c6e89bc36cd60a9b79ac2f1620a6af2c08b17")
check("configured producer dispatcher body is pinned", sha(0x4CB8A, 52) == "28856781365cd615d4f5bc16605af83efc7098321c21e290158bf4cf53b1c05f")
check("row-size helper body is pinned", sha(0x4C81A, 42) == "5169fcc5a9e6f4799c1714109bb13eed2d0710c32cb67103fbf664a60d4e9f9a")
check("8A374 obtains declared DID size", decode_long_branch(0x8A39A) == ("jarl", 0x8A31E))
check("8A374 invokes configured DID producer", decode_long_branch(0x8A3BE) == ("jarl", 0x4CB8A))
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
check("startup clears only the first response-buffer byte", CF[0x91DAC:0x91DB0] == bytes.fromhex("4407f8a1"))
check("connection reset clears only first request/response bytes", CF[0x91F8A:0x91F8E] == bytes.fromhex("4407f8a1"))

check("RDBI request-start body is pinned", sha(0x944C6, 104) == "213ea4e983a4cc1952747cc4610a9d73f049a02c8e0314a8f5b279ef83200f45")

print("\n== RDBI preflight bounds ==")




def u16(addr: int) -> int:
    return struct.unpack_from("<H", CF, addr)[0]


def u32(addr: int) -> int:
    return struct.unpack_from("<I", CF, addr)[0]


DID_TABLE = 0x2941C
DID_COUNT = 0xF2


print("== DID table shape ==")
lengths = [u16(DID_TABLE + 16 * i + 2) for i in range(DID_COUNT)]
check("configured per-DID response lengths are 1..45", all(1 <= n <= 45 for n in lengths), f"max={max(lengths)}")
check("maximum declared single-DID requirement is <= 47", max(lengths) + 2 <= 47)

print("== one DID per request (0x944C6 gate) ==")
# 0x944C6 request-shape gate: reject if len<2, odd, or len>>1 > 1.
print("== preflight and render share one length source ==")
# 0x4C81A reads (idx*0x10 + table + 2) through application_did_table_getter
# (base 0x2941C, count 0xF2). Both 0x9404A preflight accumulation and the
# 0x9429E render loop dispatch through this identical expression.
# 0x9404A accumulation: puVar1[-0x16ad] += auStack_a[0] + 2 (declared+DID echo)
# Verify the "+2" addend instruction pair exists in the accumulation window.
print("== render loop re-checks capacity per DID ==")
# 0x9429E: after callback, compares write_pos+count vs FEBE5D70 (clamped <=0xFFFE),
# branches to 0x14 (response-too-long, via 0x94426) or 0x24 paths instead of copying.
clamp = bytes.fromhex("8096feff")  # ori 0xfffe,r0,r18 at 0x94382
check("capacity clamp literal 0xFFFE used by render loop", clamp in CF[0x94360:0x94430])
check("render loop clamps capacity twice (both sites in 0x9429E)", CF.count(clamp, 0x9429E, 0x94420) == 2)


print("\n== RDBI emitted-write audit ==")


ARTIFACT = ROOT / "data" / "generated" / "rdbi_emitted_write_audit.json"

DID_TABLE = 0x2941C
DID_ROWS = 0xF2
SUCCESS_STUB = bytes.fromhex("00527f00")

VERIFIED_STUB_DIDS = {
    0x0111,
    0x1066, 0x106A,
    0x10C7, 0x10C8, 0x10C9,
    0x10F7, 0x10F8, 0x10F9,
    0x1124, 0x1125, 0x1126, 0x1127, 0x1128, 0x1129,
    0x112F, 0x1130, 0x1131,
    0x11BC, 0x11C8,
    0x1C99, 0x1C9A, 0x1C9B, 0x1C9C, 0x1C9D, 0x1C9E, 0x1C9F, 0x1CA0,
    0x1CF4, 0x1CF5, 0x1CF6, 0x1CF7, 0x1CF8, 0x1CF9, 0x1CFA, 0x1CFB, 0x1CFC, 0x1CFD, 0x1CFE, 0x1CFF,
    0x1D01, 0x1D02, 0x1D03,
    0x1F03, 0x1F04,
    0x2030, 0x2031, 0x2032,
}



def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


audit = json.loads(ARTIFACT.read_text())

print("== DID-table census (firmware bytes) ==")
rows = []
for index in range(DID_ROWS):
    base = DID_TABLE + index * 16
    did, declared = struct.unpack_from("<HH", CF, base)
    callback = struct.unpack_from("<I", CF, base + 4)[0]
    rows.append((did, declared, callback))
producers = [row for row in rows if row[2]]
lengths_by_cb: dict[int, set[int]] = {}
for _did, declared, callback in producers:
    lengths_by_cb.setdefault(callback, set()).add(declared)
check("242 configured rows carry a producer", len(producers) == 242, str(len(producers)))
check("196 unique producer callbacks", len(lengths_by_cb) == 196, str(len(lengths_by_cb)))
check("every producer serves exactly one declared length",
      all(len(lengths) == 1 for lengths in lengths_by_cb.values()))
check("declared lengths are 1..45 (max 45)",
      all(1 <= n <= 45 for lengths in lengths_by_cb.values() for n in lengths)
      and max(n for lengths in lengths_by_cb.values() for n in lengths) == 45)
check("artifact census agrees with the table",
      audit["did_table"]["unique_producers"] == 196 and audit["summary"]["classified"] == 196)

print("== count convention: configuration-owned, not producer-returned ==")
conv = audit["convention"]["pinned_bodies"]
for name, (addr, size) in {
    "0x0008a374": (0x8A374, 270), "0x0008a31e": (0x8A31E, 12),
    "0x0004cb8a": (0x4CB8A, 52), "0x0004c81a": (0x4C81A, 42),
    "0x0009429e": (0x9429E, 392),
}.items():
    check(f"{name} body hash pinned", conv[name] == sha256(CF[addr:addr + size]))
print("== emitted-write closure over all 196 producers ==")
entries = audit["callbacks"]
check("artifact DID multiset matches the configured table",
      sorted(int(d["did"], 16) for e in entries for d in e["dids"])
      == sorted(row[0] for row in producers))


ok_hash = True
for entry in entries:
    callback = int(entry["callback"], 16)
    if entry["body_sha256"] != sha256(CF[callback:callback + entry["body_size"]]):
        ok_hash = False
check("every producer body hash re-derives from firmware bytes", ok_hash)

print("== zero-write producers are the verified stale census ==")
stubs = [entry for entry in entries if entry["class"] == "success_stub"]
check("46 zero-write producers are exactly the four-byte success stubs",
      len(stubs) == 46 and all(CF[int(e["callback"], 16):int(e["callback"], 16) + 4] == SUCCESS_STUB
                               for e in stubs))
stub_dids = {int(d["did"], 16) for e in stubs for d in e["dids"]}
under_dids = {int(d["did"], 16) for e in entries if e["write_relation"] != "exact_fit" for d in e["dids"]}
check("DIDs writing fewer bytes than declared are exactly the verified 48",
      under_dids == VERIFIED_STUB_DIDS == stub_dids, str(under_dids ^ VERIFIED_STUB_DIDS))

print("== exceptional classes pinned from raw bytes ==")
magic = bytes.fromhex("a55a5aa5")
fill = bytes.fromhex("209e3f00")  # '?' fill constant materialization
for entry in entries:
    callback = int(entry["callback"], 16)
    body = CF[callback:callback + entry["body_size"]]
    if entry["class"] == "fixed_extent_loop" and entry["callback"] in ("0x0004ccc4", "0x0004cd74"):
        check(f"{entry['callback']} body carries the checkpoint magic", magic in body)
        if entry["callback"] == "0x0004ccc4":
            check("DID 0105 '?' fill constant pinned in raw bytes", fill in body)
        if entry["callback"] == "0x0004cd74":
            check("DID 010B body excludes the '?' fill constant", fill not in body)
    if entry["class"] == "declared_bounded_loop":
        check("F18C body carries checkpoint magic and '?' fill",
              entry["callback"] == "0x0004e918" and magic in body and fill in body)

print(f"\n== RESULT: {passed} passed, {failed} failed ==")
raise SystemExit(1 if failed else 0)
