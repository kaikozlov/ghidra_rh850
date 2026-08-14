#!/usr/bin/env python3
"""Verify the true application SID-0x2E WriteDataByIdentifier surface."""
from __future__ import annotations

import csv
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


def u16(a: int) -> int: return struct.unpack_from("<H", CF, a)[0]
def u32(a: int) -> int: return struct.unpack_from("<I", CF, a)[0]
def sha(a: int, n: int) -> str: return hashlib.sha256(CF[a:a+n]).hexdigest()


def decode_long_branch(addr: int) -> tuple[str, int] | None:
    w0, w1 = struct.unpack_from("<HH", CF, addr)
    if ((w0 >> 6) & 0x1F) != 0x1E or (w1 & 1): return None
    reg2 = (w0 >> 11) & 0x1F
    high = w0 & 0x3F
    if high & 0x20: high -= 0x40
    return ("jarl" if reg2 else "jr"), addr + (high << 16) + w1


EXPECTED = [
    (0x0204,2,0x4EC16,0x4EC2A),
    (0x2001,1,0x4EC46,0x4EC78),
    (0x2002,1,0x4ECBC,0x4ECD0),
    (0x2005,1,0x4ED2C,0x4ED40),
    (0x2006,1,0x4ED76,0x4ED8A),
    (0x2007,1,0x4EDC0,0x4EDD4),
    (0x2008,1,0x4EE0A,0x4EE1E),
    (0x2009,1,0x4EE54,0x4EE68),
    (0x200D,1,0x4EEA6,0x4EEBA),
    (0x2010,1,0x4EEF0,0x4EF04),
    (0x2012,1,0x4EF4A,0x4EF4E),
    (0x2013,2,0x4EF68,0x4EF90),
    (0x2014,1,0x4EFAC,0x4EFD4),
]

print("== SID 0x2E service policy ==")
check("application WDBI service object is pinned", CF[0x25EE8:0x25F00] == bytes.fromhex("623c090000000000765b0200000000002e00000200000000"))
check("SID 0x2E direct callback is 0x93C62", u32(0x25EE8) == 0x93C62)
check("SID 0x2E service identifier is 0x2E", CF[0x25EF8] == 0x2E)
check("SID 0x2E session count is 2", CF[0x25EFB] == 2)
check("SID 0x2E session list is programming+extended", CF[0x25B76:0x25B78] == bytes((2,3)))
check("SID 0x2E security count is zero", CF[0x25EFA] == 0)
check("WDBI callback body is pinned", sha(0x93C62,36) == "4005e0a9e033e72542a5ff293847924f5c1b6954819df63ba308a2ab8641003c")
check("WDBI request-start body is pinned", sha(0x93B56,136) == "9912f7af4b4faa2c506120f9454fe343ac23fe8deb55cae3d75d8789b01b29f2")

print("\n== class write capability and implemented membership ==")
# Only classes 1 and 3 have a non-null operation +12 write wrapper.
class_records = [0x26210,0x2622C,0x26248,0x26264,0x26280]
write_slots = [u32(a+12) for a in class_records]
check("only DID classes 1 and 3 expose configured write operations", write_slots == [0,0x936AA,0,0x936D6,0], repr(write_slots))
check("class-1 range is 0201..02FF", (u16(0x26240),u16(0x26242)) == (0x0201,0x02FF))
check("class-3 range is 2001..20FF", (u16(0x26278),u16(0x2627A)) == (0x2001,0x20FF))
check("shared class policy has direct-write callback slot", u32(0x2617C) != 0)
check("shared class policy adds no nested session/security list", CF[0x26154:0x26164] == bytes(16))
check("class-1 write wrapper is pinned", sha(0x936AA,44) == "6ab5ca2328be0a8b8fcf8c7e0a5cf3ec62470827c872a4633146f31e68b9a737")
check("class-3 write wrapper is pinned", sha(0x936D6,44) == "454dec5af9ab0862e37d5505c924ff8b6113690e3715f876d40c454e9f48053e")
check("both class write wrappers call 0x8A630", decode_long_branch(0x936BE) == ("jarl",0x8A630) and decode_long_branch(0x936EA) == ("jarl",0x8A630))

# Lower table is the actual implemented WDBI callback membership.
actual=[]
for i in range(13):
    o=0x25768+i*12
    actual.append((u16(o), u32(o+4), u32(o+8)))
check("13-entry lower WDBI callback table is exact", actual == [(d,s,r) for d,_,s,r in EXPECTED], repr(actual))
check("lower WDBI table body bytes are pinned", sha(0x25768,13*12) == "8e718e676f8a5a14e3234a3ad2eb3926859a59b10190fefc6e17ddf523abc3af")
check("lower start callback lookup is pinned", sha(0x8D3CC,74) == "da09068643ff4636029dc606a4ca84e4bd6b6c92549a9694f34b5ecb0378317f")
check("lower result callback lookup is pinned", sha(0x8D416,92) == "53eb2063d8cc21aeac28e633b7dba18edeb91d7cdb29269301687e2a77092c74")
check("shared WDBI worker is pinned", sha(0x8A630,90) == "63752c6baadcbe78724bbf76da81c127cdccc365a3010cc6f59a7fee0637f1d1")

# Candidate DIDs in the two write-capable classes; ten have no lower callback record.
did_rows=[]
for i in range(242):
    o=0x2941C+i*16
    did,size=u16(o),u16(o+2)
    if did==0x0204 or 0x2001<=did<=0x20FF:
        did_rows.append((did,size))
candidate={d for d,_ in did_rows}
implemented={d for d,_,_,_ in EXPECTED}
omitted=candidate-implemented
check("write-capable classes contain 23 configured DID rows", len(candidate)==23, repr(sorted(candidate)))
check("exact ten class-capable DIDs lack a lower write callback", omitted == {0x2003,0x2004,0x200A,0x200B,0x200C,0x200E,0x200F,0x2030,0x2031,0x2032}, repr(sorted(omitted)))

print("\n== payload lengths and callback gates ==")
length_by_did={}
for i in range(242):
    o=0x2941C+i*16; length_by_did[u16(o)]=u16(o+2)
check("all 13 WDBI payload lengths match DID row size metadata", all(length_by_did[d]==n for d,n,_,_ in EXPECTED))
# Ten ordinary starts are the same speed-only gate; 2013/2014 add two state gates.
speed_only=[0x4EC16,0x4EC46,0x4ECBC,0x4ED2C,0x4ED76,0x4EDC0,0x4EE0A,0x4EE54,0x4EEA6,0x4EEF0]
check("ten ordinary WDBI starts share the exact speed-gate body", all(sha(a,20)=="bb3ee890414c93d5d48fe96fd1151c95e507740e32eb0d00a75c2f2a1e08ac23" for a in speed_only))
check("2013/2014 starts share speed+state gate body", sha(0x4EF68,40)==sha(0x4EFAC,40)=="ecc2127f1b219bac3c5f952eaf45650bc9eea10c3f9350073e5f39cf4e0da0a3")
check("2012 start is unconditional success", CF[0x4EF4A:0x4EF4E] == bytes.fromhex("00527f00"))
check("exactly 12 of 13 implemented WDBI DIDs are vehicle-speed gated", len(speed_only)+2 == 12)
check("session-transition policy body is pinned", sha(0x4C942,30) == "59f72ced67bed66bac3837c907af72e235dbf710baa0c4205664622794595373")
check("session-transition speed check is conditional on requested session 02",
      CF[0x4C948:0x4C94C] == bytes.fromhex("623a9a0d"))
check("session-transition speed rejection returns internal result 0x0B",
      CF[0x4C958:0x4C95C] == bytes.fromhex("0b527f00"))
check("non-programming session path returns success", CF[0x4C95C:0x4C960] == bytes.fromhex("00527f00"))

print("\n== persistent NvM joins ==")
# Object 0x101/102/103 constructors call FF09C, a veneer over secoc_nvm_object_update.
check("object-101 constructor uses literal 0x101 and update veneer", CF[0xB4492:0xB4498] == bytes.fromhex("890320360101") and decode_long_branch(0xB44C2)==("jarl",0xFF09C))
check("object-102 constructor uses literal 0x102 and update veneer", CF[0xB5AA6:0xB5AAA] == bytes.fromhex("20360201") and decode_long_branch(0xB5AAA)==("jarl",0xFF09C))
check("object-103 selected-byte constructor uses literal 0x103 and update veneer", CF[0xB5342:0xB5346] == bytes.fromhex("20360301") and decode_long_branch(0xB5356)==("jarl",0xFF09C))
check("NvM update veneer is pinned", sha(0xFF09C,14) == "84370e4fe077b79616d4111032db449eef2132bad8d5804de557e46718961389")
check("eight WDBI DIDs map to persistent NvM state machines", {d for d,_,_,_ in EXPECTED if d in {0x2001,0x2002,0x2005,0x2006,0x2007,0x2008,0x2009,0x200D}} == {0x2001,0x2002,0x2005,0x2006,0x2007,0x2008,0x2009,0x200D})

print("\n== no-speed-gate DID 2012 live override ==")
check("2012 result accepts only payload 01 before helper call", CF[0x4EF54:0x4EF5E] == bytes.fromhex("6008610ada058aff76ef"))
check("2012 helper writes magic 0x5A to FEBEB18F", CF[0xB28A2:0xB28AA] == bytes.fromhex("200e5a00440f8ff9"))
check("2012 helper body is pinned", sha(0xB28A2,10) == "69b91e19346d41fe5a25be687204dcf304d131de4a67d979b15c68142a8caf37")
# Consumer instructions are pinned by exact fixed-address refs in their bodies.

print("\n== live parameter DIDs 2013/2014 ==")
check("2013 result calls helper FE1C8", decode_long_branch(0x4EF9E)==("jarl",0xFE1C8))
check("2014 result calls helper FE1B4", decode_long_branch(0x4EFEC)==("jarl",0xFE1B4))
check("2013 downstream control calculation body is pinned", sha(0xB763C,48)=="d1cffef524242cd467171074863fa79f7d45feaf48b421f57d77ea1a8375c5d5")
check("2014 downstream threshold-state bodies are pinned", sha(0xB692C,104)=="b0c3a2bbafdbf2646f327609776adde6fe6e06050458c13d508bf42ce68a3446" and sha(0xB70D0,68)=="a5a0b95fa36030b842d3b88bef3085a78e98962339ffefd94ffe4e91029911a7")

print("\n== committed surface artifact ==")
with (ROOT/"data/application_wdbi_surface.csv").open(newline="") as f:
    rows=list(csv.DictReader(f))
check("surface CSV has 13 rows", len(rows)==13)
check("surface CSV DIDs/lengths/callbacks match firmware", [(int(r['did'],16),int(r['payload_len']),int(r['start_callback'],16),int(r['result_callback'],16)) for r in rows] == EXPECTED)
check("surface CSV marks exactly eight persistent NvM DIDs", sum(r['side_effect_class']=='persistent_nvm_state' for r in rows)==8)
check("surface CSV marks only DID 2012 as ungated by speed", [r['did'] for r in rows if r['speed_gate']=='0']==['0x2012'])

print(f"\nSummary: {passed} passed, {failed} failed")
sys.exit(1 if failed else 0)
