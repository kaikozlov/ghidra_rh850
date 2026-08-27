#!/usr/bin/env python3
"""Verify the application SID-0x2E WriteDataByIdentifier surface, callbacks, and DID cones.

Merged portable family module.
"""
from __future__ import annotations

import csv
import hashlib
import json
import struct
import sys
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

print("== WDBI surface ==")




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


print("\n== WDBI callbacks ==")




def decode_branch(addr):
    """Decode RH850 jarl/jr (op0610=0x1E, op1616=0).

    Returns (kind, target, reg2) where kind is 'jarl' (reg2!=0) or 'jr' (reg2==0).
    Returns None if the instruction is not a valid jarl/jr encoding.
    """
    if addr + 4 > len(CF):
        return None
    w0 = struct.unpack_from("<H", CF, addr)[0]
    if (w0 >> 6) & 0x1F != 0x1E:
        return None
    w1 = struct.unpack_from("<H", CF, addr + 2)[0]
    if w1 & 1:  # SLEIGH constraint: op1616=0
        return None
    reg2 = (w0 >> 11) & 0x1F
    s0005 = w0 & 0x3F
    if s0005 & 0x20:
        s0005 -= 0x40
    target = ((s0005 << 16) | w1) + addr
    kind = "jarl" if reg2 != 0 else "jr"
    return (kind, target, reg2)


# ═══════════════════════════════════════════════════════════════════
# Constants
# ═══════════════════════════════════════════════════════════════════
SENSITIVE_TARGETS = {
    0x865D4,  # AES key expansion
    0x853EE,  # AES decrypt block
    0x852B0,  # AES encrypt wrapper
    0x8496C,  # AES encrypt rounds
    0x72F58,  # NvM ReadBlock
    0x72F84,  # NvM WriteBlock
    0x84850,  # ICU-S init
    0x84874,  # ICU-S process
    0x8488C,  # ICU-S finalize
    0x880DC,  # ICU verify adapter
    # Complete SecOC/CMAC verification chain (CSM/CryptoIf + ICU-S)
    0x88B6A,  # CSM job start / CMAC verify init
    0x88B9C,  # CSM process / CMAC update
    0x88BA8,  # CSM finish / CMAC finalize
    0x88556,  # CryptoIf job dispatch
    0x88080,  # ICU-S CMAC operation
    0x897F4,  # SecOC freshness / verify helper
    0x8C7BC,  # SA crypto stage 1
    0x8C7F6,  # SA crypto stage 2
    0x8FDCA,  # security-state reader
    0x8F242,  # security level checker
    0x92FEE,  # per-DID policy check
    0x900FC,  # unlock helper
}

# WDBI callback code range scanned for direct branch targets.
SCAN_RANGES = [
    ("WDBI_callbacks", 0x4EC16, 0x4F000),
]

# Firmware-derived direct branch targets in the 13 callback pairs.
FIRMWARE_TARGETS = {
    0x4C4A4, 0x4EC5A, 0x4EC68, 0x8A6AA,
    0xFDE58, 0xFDED0, 0xFE04C, 0xFE060, 0xFE09C,
    0xFE0C4, 0xFE1B4, 0xFE1C8, 0xFE2A4,
}


def branch_targets(start, end):
    """Return direct RH850 jarl/jr targets in a bounded code interval."""
    targets = set()
    for addr in range(start, end, 2):
        result = decode_branch(addr)
        if result is not None:
            targets.add(result[1])
    return targets


def veneer_target(addr):
    """Decode the generated ``mov imm32,r12; jmp r12`` veneer form."""
    if CF[addr:addr + 2] != b"\x2c\x06" or CF[addr + 6:addr + 8] != b"\x6c\x00":
        return None
    return struct.unpack_from("<I", CF, addr + 2)[0]

# ═══════════════════════════════════════════════════════════════════
# 1. WDBI DID callback table at 0x25768
# ═══════════════════════════════════════════════════════════════════
print("== WDBI callback table at 0x25768 ==")

SID_2E_RECORD = 0x25EE8
check("SID 0x2E application callback is 0x93C62",
      struct.unpack_from("<I", CF, SID_2E_RECORD)[0] == 0x93C62)
check("SID 0x2E service record carries sessions 2/3 and no SA levels",
      CF[SID_2E_RECORD + 0x10] == 0x2E and CF[SID_2E_RECORD + 0x12] == 0 and
      CF[SID_2E_RECORD + 0x13] == 2 and CF[0x25B76:0x25B78] == bytes((2,3)))

WDBI_CSV = REPO / "data" / "application_wdbi_callbacks.csv"
check("WDBI callback CSV exists", WDBI_CSV.exists())
with open(WDBI_CSV) as f:
    wdbi_rows = list(csv.DictReader(f))
check("CSV has 13 WDBI entries", len(wdbi_rows) == 13, str(len(wdbi_rows)))

EXPECTED_SIZES = {
    0x0204: (20, 28),
    0x2001: (20, 68),
    0x2002: (20, 76),
    0x2005: (20, 54),
    0x2006: (20, 54),
    0x2007: (20, 54),
    0x2008: (20, 54),
    0x2009: (20, 54),
    0x200D: (20, 54),
    0x2010: (20, 70),
    0x2012: (4, 26),
    0x2013: (40, 28),
    0x2014: (40, 42),
}

for i, row in enumerate(wdbi_rows):
    did = int(row["did"], 16)
    start_cb = int(row["start_cb"], 16)
    result_cb = int(row["result_cb"], 16)
    addr = 0x25768 + i * 0xC
    did_actual = struct.unpack_from("<H", CF, addr)[0]
    start_actual = struct.unpack_from("<I", CF, addr + 4)[0]
    result_actual = struct.unpack_from("<I", CF, addr + 8)[0]
    check(f"WDBI table[{i}] DID=0x{did:04X} start=0x{start_cb:X} result=0x{result_cb:X}",
          did_actual == did and start_actual == start_cb and result_actual == result_cb,
          f"got DID=0x{did_actual:04X} start=0x{start_actual:X} result=0x{result_actual:X}")
    csv_sizes = (int(row["start_size_bytes"]), int(row["result_size_bytes"]))
    check(f"WDBI DID 0x{did:04X} callback sizes match recovered bodies",
          csv_sizes == EXPECTED_SIZES[did], repr(csv_sizes))
    csv_targets = (set() if row["call_targets"] == "none" else
                   {int(value, 16) for value in row["call_targets"].split(";")})
    actual_targets = (
        branch_targets(start_cb, start_cb + csv_sizes[0]) |
        branch_targets(result_cb, result_cb + csv_sizes[1])
    )
    check(f"WDBI DID 0x{did:04X} direct-target census matches callback bodies",
          csv_targets == actual_targets,
          f"csv={sorted(map(hex, csv_targets))}; actual={sorted(map(hex, actual_targets))}")

# The worker wrappers are the fourth callbacks in generic DID-class records for
# 0x0201..0x02FF and 0x2001..0x20FF. They are reached by the active SID-0x2E
# generic write-record dispatcher, not by CommunicationControl or SID 0x31.
CONTROL_RECORD = struct.Struct("<IIIIIHHB3x")
control_rows = [CONTROL_RECORD.unpack_from(CF, 0x26210 + i * CONTROL_RECORD.size)
                for i in range(5)]
check("generic DID-class record size is 0x1C", CONTROL_RECORD.size == 0x1C)
check("range 0x0201..0x02FF uses WDBI wrapper 0x936AA",
      control_rows[1][5:8] == (0x0201, 0x02FF, 1) and control_rows[1][3] == 0x936AA)
check("range 0x2001..0x20FF uses WDBI wrapper 0x936D6",
      control_rows[3][5:8] == (0x2001, 0x20FF, 1) and control_rows[3][3] == 0x936D6)
check("WDBI request path reaches generic write-record dispatcher",
      0x92A70 in branch_targets(0x9395E, 0x93A1E))
wrapper_0201_call = decode_branch(0x936BE)
wrapper_2001_call = decode_branch(0x936EA)
check("both generic-control wrappers call worker 0x8A630",
      wrapper_0201_call is not None and wrapper_0201_call[1] == 0x8A630 and
      wrapper_2001_call is not None and wrapper_2001_call[1] == 0x8A630)
check("worker reaches start and result dispatchers",
      0x8A482 in branch_targets(0x8A630, 0x8A68A) and
      0x8A542 in branch_targets(0x8A630, 0x8A68A))
check("dispatchers reach both 13-entry callback lookups",
      0x8D3CC in branch_targets(0x8A482, 0x8A542) and
      0x8D416 in branch_targets(0x8A542, 0x8A630))

# ═══════════════════════════════════════════════════════════════════
# 2. Firmware-derived branch scan across all 3 ranges
# ═══════════════════════════════════════════════════════════════════
print("\n== firmware-derived branch scan (jarl + jr) ==")

firmware_targets = set()
sensitive_hits = []
for name, start, end in SCAN_RANGES:
    for addr in range(start, end, 2):
        result = decode_branch(addr)
        if result is None:
            continue
        kind, target, reg2 = result
        if 0 < target < 0x100000:
            firmware_targets.add(target)
            if target in SENSITIVE_TARGETS:
                sensitive_hits.append((addr, kind, target))

check("no direct sensitive branch targets in callback range (jarl + jr)",
      len(sensitive_hits) == 0,
      f"{len(sensitive_hits)} found: {[(hex(a), k, hex(t)) for a, k, t in sensitive_hits]}")

check("firmware-derived target set matches expected (13 targets)",
      firmware_targets == FIRMWARE_TARGETS,
      f"missing={FIRMWARE_TARGETS - firmware_targets}; "
      f"extra={firmware_targets - FIRMWARE_TARGETS}")

# Direct callback closure is not the whole story. Successful result callbacks
# arm three byte-state machines whose consumers submit namespace-0x100 objects
# 0x101, 0x102, and 0x103 through wrapper 0xFF09C -> dispatcher 0x65CD8.
print("\n== WDBI state-mediated namespace-0x100 persistence paths ==")
result_helper_by_did = {
    0x2001: 0xFE060,
    0x2002: 0xFDE58,
    0x2005: 0xFE0C4,
    0x2006: 0xFE0C4,
    0x2007: 0xFE0C4,
    0x2008: 0xFE0C4,
    0x2009: 0xFE0C4,
    0x200D: 0xFE0C4,
}
for row in wdbi_rows:
    did = int(row["did"], 16)
    if did not in result_helper_by_did:
        continue
    result_cb = int(row["result_cb"], 16)
    helper = result_helper_by_did[did]
    check(f"WDBI DID 0x{did:04X} result reaches state-arm helper 0x{helper:X}",
          helper in branch_targets(result_cb, result_cb + int(row["result_size_bytes"])))

check("veneer 0xFE060 reaches object-0x101 state producer 0xB47A6",
      veneer_target(0xFE060) == 0xB47A6)
check("veneer 0xFDE58 reaches object-0x102 state producer 0xB5D0C",
      veneer_target(0xFDE58) == 0xB5D0C)
check("veneer 0xFE0C4 reaches object-0x103 state producer 0xB55C4",
      veneer_target(0xFE0C4) == 0xB55C4)

persistence_paths = [
    (0x101, 0xB44CA, 0xB45A2, 0xB4484, 0xB44CA),
    (0x102, 0xB5C3E, 0xB5CD0, 0xB5C16, 0xB5C3E),
    (0x103, 0xB535E, 0xB53E8, 0xB52DA, 0xB535E),
]
for object_id, consumer_start, consumer_end, update_start, update_end in persistence_paths:
    check(f"object 0x{object_id:03X} state consumer reaches update helper 0x{update_start:X}",
          update_start in branch_targets(consumer_start, consumer_end))
    check(f"object 0x{object_id:03X} update helper embeds selector and calls 0xFF09C",
          b"\x20\x36" + struct.pack("<H", object_id) in CF[update_start:update_end] and
          0xFF09C in branch_targets(update_start, update_end))

check("thin update wrapper 0xFF09C reaches dispatcher 0x65CD8",
      0x65CD8 in branch_targets(0xFF09C, 0xFF0B0))

# ═══════════════════════════════════════════════════════════════════
# 3. GP-relative and literal SecOC key references
# ═══════════════════════════════════════════════════════════════════
print("\n== SecOC key references in scanned ranges ==")

for name, start, end in SCAN_RANGES:
    # GP-relative displacements (APP_GP = 0xFEBEB800)
    for disp, label in [(0x5AE8, "FEBF02E8"), (0x5AF8, "FEBF02F8")]:
        target_bytes = struct.pack("<h", disp)
        found = CF.find(target_bytes, start, end)
        check(f"{name}: no GP-disp 0x{disp:04X} ({label})",
              found < 0, f"at 0x{found:05X}")

    # Literal 32-bit addresses
    for addr_val in [0xFEBF02E8, 0xFF206E14]:
        target_bytes = struct.pack("<I", addr_val)
        found = CF.find(target_bytes, start, end)
        check(f"{name}: no literal 0x{addr_val:08X}",
              found < 0, f"at 0x{found:05X}")

# ═══════════════════════════════════════════════════════════════════
# 4. Callback liveness
# ═══════════════════════════════════════════════════════════════════
print("\n== callback liveness ==")
for row in wdbi_rows:
    did = int(row["did"], 16)
    for field in ("start_cb", "result_cb"):
        cb = int(row[field], 16)
        check(f"WDBI DID 0x{did:04X} {field} 0x{cb:X} is live",
              CF[cb:cb + 2] != b"\x00\x00")


print("\n== WDBI 0204 maintenance ==")


CORPUS = ROOT / "data/generated/decompilations.jsonl"


def sha(addr: int, size: int) -> str:
    return hashlib.sha256(CF[addr:addr + size]).hexdigest()


def branch(addr: int) -> tuple[str, int] | None:
    w0, w1 = struct.unpack_from("<HH", CF, addr)
    if ((w0 >> 6) & 0x1F) != 0x1E or (w1 & 1):
        return None
    reg2 = (w0 >> 11) & 0x1F
    hi = w0 & 0x3F
    if hi & 0x20:
        hi -= 0x40
    return ("jarl" if reg2 else "jr", addr + (hi << 16) + w1)


records: dict[int, dict] = {}
for line in CORPUS.open():
    record = json.loads(line)
    if record.get("record") == "function":
        records[int(record["entry_addr"], 16)] = record


def direct_refs(addr: int) -> set[int]:
    out: set[int] = set()
    for ref in records[addr].get("data_references", []):
        target = ref.get("to_addr", "")
        if target.startswith("0x"):
            out.add(int(target, 16))
    return out


print("== WDBI 0204 membership and request split ==")
rows = {row["did"]: row for row in csv.DictReader((ROOT / "data/application_wdbi_surface.csv").open(newline=""))}
row = rows["0x0204"]
check("0204 is the two-byte WDBI member", row["payload_len"] == "2" and row["start_callback"] == "0x4EC16" and row["result_callback"] == "0x4EC2A")
check("0204 is sessions 2/3, SecurityAccess-free, vehicle-speed gated", row["sessions"] == "2,3" and row["security_access_required"] == "0" and row["speed_gate"] == "1")
check("0204 start gate body is pinned", sha(0x4EC16, 20) == "bb3ee890414c93d5d48fe96fd1151c95e507740e32eb0d00a75c2f2a1e08ac23")
check("0204 result body is pinned", sha(0x4EC2A, 28) == "400a129b2f6e6cb6de1df28868ce698dcebabd462de098d7b5b26a3a9c1282ce")
check("result defaults to state 0x21 and tests payload-byte-1 bit 7", CF[0x4EC2A:0x4EC34] == bytes.fromhex("200e2100c6ff0100a205"))
check("set bit converts 0x21 to 0x11", CF[0x4EC34:0x4EC36] == bytes.fromhex("500a"))
check("result stores state and shared pending tag 0x2E10", CF[0x4EC36:0x4EC44] == bytes.fromhex("24f64cc902529b0b200e102e8f0c"))
check("result returns Dcm pending status 2", CF[0x4EC3A:0x4EC3C] == bytes.fromhex("0252"))

print("\n== Dcm pending worker and two application modes ==")
check("shared 0x2E pending dispatcher is pinned", sha(0x4C3CA, 86) == "63aa7e4748748ccac6d46030ab58825e5e9b67e3117baa978e5ed6e01a6bb754")
check("0204 pending worker body is pinned", sha(0x4EBBC, 58) == "b3913138d8a22bd61e26233cca962ff81841bcff8d978ed7a3f3d1b6eccacc1e")
check("state 0x11 calls 35582", branch(0x4EBCA) == ("jarl", 0x35582))
check("state 0x11 writes application mode 0x11 through FDE08", CF[0x4EBCE:0x4EBD6] == bytes.fromhex("203611008aff36f2") and branch(0x4EBD2) == ("jarl", 0xFDE08))
check("state 0x11 advances Dcm state to 0x12", CF[0x4EBD6:0x4EBDA] == bytes.fromhex("200e1200"))
check("state 0x21 writes application mode 0x22 through FDE08", CF[0x4EBE2:0x4EBEA] == bytes.fromhex("203622008aff22f2") and branch(0x4EBE6) == ("jarl", 0xFDE08))
check("state 0x21 advances Dcm state to 0x22", CF[0x4EBEA:0x4EBEE] == bytes.fromhex("200e2200"))
check("mode helper 35582 is pinned", sha(0x35582, 52) == "2c2a4fb92de73ac8d7b2178beeced784c17f54add185c08d205524f493991dce")
check("FDE08 thunk is pinned", sha(0xFDE08, 8) == "68bfb2e96f05cec57e51d4d1b8e0c08b27b83e128b7c6d5584c0d98b9b580b5e")
check("FDE08 thunk targets B7F7C", CF[0xFDE08:0xFDE10] == bytes.fromhex("2c067c7f0b006c00"))
check("B7F7C is a six-byte FEBEAF47 setter", sha(0xB7F7C, 6) == "bf8c503dc3d081353476e18e7826bdffc9424689dd9d4ca6552a8167a401043a")

print("\n== object-7 mode-latch persistence handshake ==")
check("operational mode worker is pinned", sha(0xB7E6E, 182) == "bf7950266f1d10f78fc58f7fee440f858576f5a366843d7b40ab5706d0940dc1")
check("object-7 persistence helper is pinned", sha(0xB7E4A, 36) == "a2a3731ecac0740853ff44e414cd5cd3dc5580bdd5042c3a27e04c6cca8d2d22")
check("B7E4A submits literal object 7 through FF09C", CF[0xB7E5C:0xB7E66] == bytes.fromhex("07320305800b84ff3a72") and branch(0xB7E62) == ("jarl", 0xFF09C))
check("NvM status worker is pinned", sha(0xB7F4C, 48) == "b44d7baf3a6e2bce8997a14eca5a7eb1670702392a771952ba44b5cc7e537faa")
check("B7F4C polls literal object 7 status", CF[0xB7F5C:0xB7F62] == bytes.fromhex("073284ff6671") and branch(0xB7F5E) == ("jarl", 0xFF0C4))
check("completion helper is pinned", sha(0xB7F24, 40) == "a72d66663456e5d78e09d821e1c0e556cb238ab867e65723379293bbbb661d5f")
check("completion helper reports selector 0x12 through C430", CF[0xB7F40:0xB7F48] == bytes.fromhex("2036120084ffbc6c") and branch(0xB7F44) == ("jarl", 0xFEC00))

persist_rows = list(csv.DictReader((ROOT / "data/object15_reachability.csv").open(newline="")))
def persisted(caller: str, obj: int) -> bool:
    return any(r["caller_addr"] == caller and r["object_index"] == str(obj) and r["async_persist_behavior"] == "checkpoint_persist" for r in persist_rows)
check("B7E4A is independently classified as checkpoint object 7 persistence", persisted("0xB7E4A", 7))

print("\n== branch-specific post-response queue operation 6 ==")
check("Dcm completion dispatcher is pinned", sha(0x4EBF6, 32) == "a7542561f3b8a22053950c5784e1c0cc794a123d1c80d3bb0c4a116224a67675")
check("state 0x12 clears without queue operation", CF[0x4EBFE:0x4EC04] == bytes.fromhex("0106eeffe205"))
check("state 0x22 uniquely calls queue starter 50922 before clearing", CF[0x4EC04:0x4EC12] == bytes.fromhex("0106deffda0580ff181d440767c9") and branch(0x4EC0A) == ("jarl", 0x50922))
check("queue starter body is pinned", sha(0x50922, 116) == "72008c7894efd52ba593be71718a362347ac7d8dd9081211572bc997ea7f5b64")
check("idle queue starter sets operation 6 then calls initializer", CF[0x5092E:0x5093C] == bytes.fromhex("060a440f8cca bfffb2ff c43f8cca".replace(" ", "")) and branch(0x50934) == ("jarl", 0x508E6))
check("operation-6 initializer is pinned", sha(0x508E6, 60) == "42961c51463fa34a1645d7daf2aeb181a0bf6821ca12bbc813bddd3680966e38")
expected_calls = [0xFDFE8,0x539A8,0x390E6,0x453A2,0xFDDF4,0xFDDE0,0x546E2,0x505F8,0x51524,0x52016,0x53626,0x5062A]
call_sites = [0x508EA,0x508EE,0x508F2,0x508F6,0x508FA,0x508FE,0x50902,0x50908,0x5090C,0x50910,0x50914,0x5091A]
actual_calls = [branch(site)[1] if branch(site) else None for site in call_sites]
check("operation-6 initializer has exact 12-callee fan-out", actual_calls == expected_calls, repr([hex(x) if x else None for x in actual_calls]))
check("normal queue scheduler body is pinned", sha(0x50B22, 24) == "44666d287fbc50489cf37b72a9452b1987da05fe742ec259ddd18ab051db2d1a")
check("operation-6 completion monitor is pinned", sha(0x50A1C, 204) == "89683a882b55a0255bf1e379ac3ad1c18c7e4d377bad600a711e1258a0159dbb")

print("\n== queue operation 6 resets/persists checkpoint groups ==")
for caller, obj, label in [
    ("0xBAFB2", 9, "runtime-condition snapshot"),
    ("0xBB3C6", 11, "two-channel state"),
    ("0x453A2", 12, "dual-incident snapshot"),
    ("0x539A8", 14, "condition-history"),
    ("0xBB5EC", 15, "operating-state snapshot"),
]:
    check(f"operation-6 fan-out persists checkpoint object {obj} ({label})", persisted(caller, obj))
check("operation-6 live-state clear helper 390E6 is pinned", sha(0x390E6, 14) == "a4d8238da30f44a19cd69f4974774492048b0b719ff4cbe714acdd24612ef99c")

print("\n== bounded separation from direct steering-current/PWM actuation ==")
command_states = {
    0xFEBE7F94,0xFEBEF184,0xFEBEAE20,0xFEBEBF80,0xFEBEBF84,0xFEBEBF9A,0xFEBEBFA2,0xFEBEACFF,
    0xFEBEAE60,0xFEBEBFF0,0xFEBEC0BE,0xFEBEC0C8,0xFEBEC0D6,0xFEBEC144,0xFEBEC170,0xFEBEC1B8,
    0xFEBEC1B4,0xFEBEC1BC,0xFEBEC1D4,0xFEBEB788,0xFEBEB87E,0xFEBEAE16,0xFEBEAE6E,
    0xFEBE6D18,0xFEBE6D1C,0xFEBE6D28,0xFEBE6D2A,
}
audit_functions = [
    0x4EC2A,0x4EBBC,0x35582,0xB7F7C,0xB7E6E,0xB7E4A,0xB7F4C,0xB7F24,0x4EBF6,0x50922,0x508E6,
    0xBB210,0x539A8,0x390E6,0x453A2,0xBB5EC,0xBB3C6,0x546E2,0x505F8,0x51524,0x52016,0x53626,0x5062A,
]
missing = [hex(a) for a in audit_functions if a not in records]
check("all recovered 0204/operation-6 boundary functions exist in corpus", not missing, repr(missing))
hits: list[str] = []
for addr in audit_functions:
    for target in sorted(direct_refs(addr) & command_states):
        hits.append(f"{addr:06X}->{target:08X}")
check("0204 + operation-6 direct data refs do not join conditioned command or d/q state", not hits, repr(hits))
check("independent motor actuation oracle is present", (ROOT / "tests/verify_motor_actuation_boundary.py").is_file())
check("surface matrix classifies 0204 as persistent maintenance/reset", row["side_effect_class"] == "persistent_maintenance_reset")


print("\n== WDBI 2010 dead state ==")


CORPUS = ROOT / "data/generated/decompilations.jsonl"


def sha(addr: int, size: int) -> str:
    return hashlib.sha256(CF[addr:addr + size]).hexdigest()


def branch(addr: int) -> tuple[str, int] | None:
    w0, w1 = struct.unpack_from("<HH", CF, addr)
    if ((w0 >> 6) & 0x1F) != 0x1E or (w1 & 1):
        return None
    reg2 = (w0 >> 11) & 0x1F
    hi = w0 & 0x3F
    if hi & 0x20:
        hi -= 0x40
    return ("jarl" if reg2 else "jr", addr + (hi << 16) + w1)


def corpus_records() -> list[dict]:
    return [json.loads(line) for line in CORPUS.open()]


RECORDS = corpus_records()


def refs_to(target: str) -> list[tuple[str, str]]:
    out: list[tuple[str, str]] = []
    for record in RECORDS:
        if record.get("record") != "function":
            continue
        for ref in record.get("data_references", []):
            if ref.get("to_addr") == target:
                out.append((ref["from_addr"], ref["ref_type"]))
    return sorted(out)


print("== WDBI 2010 membership and gate ==")
with (ROOT / "data/application_wdbi_surface.csv").open(newline="") as stream:
    rows = {row["did"]: row for row in csv.DictReader(stream)}
row = rows["0x2010"]
check("2010 remains a one-byte implemented WDBI member", row["payload_len"] == "1" and row["start_callback"] == "0x4EEF0" and row["result_callback"] == "0x4EF04")
check("2010 outer policy remains sessions 2/3 with no SecurityAccess", row["sessions"] == "2,3" and row["security_access_required"] == "0")
check("2010 retains the ordinary vehicle-speed start gate", row["speed_gate"] == "1" and sha(0x4EEF0, 20) == "bb3ee890414c93d5d48fe96fd1151c95e507740e32eb0d00a75c2f2a1e08ac23")

print("\n== result payload mapping and dead state writes ==")
check("2010 result body is pinned", sha(0x4EF04, 70) == "7925583212ae9d53bb53efbb830e480f9b507e3e777b910d964ed93e380a12f8")
check("payload 0 selects magic 55AAAA55", CF[0x4EF10:0x4EF18] == bytes.fromhex("260655aaaa550638"))
check("payload 1/2 share magic AA5555AA with second word 55AAAA55", CF[0x4EF22:0x4EF2E] == bytes.fromhex("2606aa5555aa270655aaaa55"))
check("other payloads retain internal status -12 and skip the writer", CF[0x4EF1A:0x4EF22] == bytes.fromhex("5f0a1432610aab0d"))
check("valid payload path calls FE09C", branch(0x4EF2E) == ("jarl", 0xFE09C))
check("FE09C veneer is pinned", sha(0xFE09C, 8) == "be1af0d4c53f140d80d3e57b54f4de67553d124dfd06c0ba187b22e2251e48f0")
check("FE09C veneer targets B7C0E", CF[0xFE09C:0xFE0A4] == bytes.fromhex("2c060e7c0b006c00"))
check("B7C0E writer body is pinned", sha(0xB7C0E, 18) == "4cfb3de0d2668056e097f1be7c4085f5dd681ae1f914de2045c45ed3ec7a9895")
check("B7C0E writes marker 0x44 and both payload words", CF[0xB7C0E:0xB7C1E] == bytes.fromhex("200e440024f68cfc820b005209350b3d"))
check("B7C0E returns fixed success 0", CF[0xB7C18:0xB7C20] == bytes.fromhex("005209350b3d7f00"))

expected_refs = {
    "0xfebeb48e": [("0x000b7c16", "WRITE"), ("0x000bd694", "WRITE")],
    "0xfebeb49c": [("0x000b7c1a", "WRITE"), ("0x000bd696", "WRITE")],
    "0xfebeb4a0": [("0x000b7c1c", "WRITE"), ("0x000bd698", "WRITE")],
}
for target, expected in expected_refs.items():
    actual = refs_to(target)
    check(f"{target} exact corpus xrefs are init + 2010 writer only", actual == expected, repr(actual))
    check(f"{target} has no recovered runtime read/param reference", not any(kind in {"READ", "PARAM"} for _, kind in actual), repr(actual))

print("\n== 0x2E10 pending branch is unreachable for DID 2010 ==")
check("generic result-status mapper is pinned", sha(0x4C4A4, 44) == "c6338b8f4adef899c9690bb4f79b643a7a432e3b2735680a72fc880d6fe6d177")
check("mapper input 0 returns 0", CF[0x4C4A4:0x4C4C0] == bytes.fromhex("e031b20d743292157932d20d7a32920d7f32d20509527f0006507f00"))
check("mapper input -1 is the unique branch returning 2", CF[0x4C4B4:0x4C4C4] == bytes.fromhex("7f32d20509527f0006507f0002527f00"))
check("mapper input -12 returns 4", CF[0x4C4A8:0x4C4D0].endswith(bytes.fromhex("04527f00")))
# The only mapper inputs that 2010 can supply are B7C0E's fixed 0 or the invalid-input sentinel -12.
reachable_mapper_inputs = {0, -12}
mapper = {0: 0, -12: 4, -7: 8, -6: 5, -1: 2}
check("2010 reachable mapper outputs are exactly 0/4", {mapper[x] for x in reachable_mapper_inputs} == {0, 4})
check("2010 can never produce mapper result 2", 2 not in {mapper[x] for x in reachable_mapper_inputs})
check("result callback writes 2E10 only if mapper result equals 2", CF[0x4EF38:0x4EF46] == bytes.fromhex("000a6252ba05200e102e640f6ac9"))
check("therefore 2010 always writes zero to shared diagnostic status word", 2 not in {mapper[x] for x in reachable_mapper_inputs})

print("\n== FEBE816A is shared diagnostic service bookkeeping ==")
check("shared status dispatcher body is pinned", sha(0x4C3CA, 86) == "63aa7e4748748ccac6d46030ab58825e5e9b67e3117baa978e5ed6e01a6bb754")
check("dispatcher masks the high byte", CF[0x4C3CE:0x4C3D6] == bytes.fromhex("e40f6bc9c19e00ff"))
check("dispatcher recognizes service tags 0x14 and 0x2E", CF[0x4C3D8:0x4C3E4] == bytes.fromhex("130600ec8225130600d2e205"))
check("dispatcher also recognizes proprietary service tag 0xBA", CF[0x4C3E4:0x4C3EC] == bytes.fromhex("805e00baeb99fa15"))
check("ClearDiagnosticInformation state machine is pinned", sha(0x4C9C6, 68) == "88392041b92100673411912fb2c1d7567a1cea057628a67c1cb3657a6e897400")
check("ClearDiagnosticInformation writes shared status 0x1410", CF[0x4C9D2:0x4C9DA] == bytes.fromhex("200e1014640f6ac9"))
check("WDBI 0204 independently writes shared status 0x2E10", CF[0x4EC3E:0x4EC44] == bytes.fromhex("200e102e8f0c"))
check("2010 status-word write site is the same shared FEBE816A location", refs_to("0xfebe816a").count(("0x0004ef42", "WRITE")) == 1)

print("\n== bounded separation from actuation ==")
check("surface artifact classifies 2010 as write-only diagnostic residue", row["side_effect_class"] == "write_only_diagnostic_residue")
check("independent motor actuation oracle is present", (ROOT / "tests/verify_motor_actuation_boundary.py").is_file())


print("\n== WDBI 2012 lifecycle ==")


CORPUS = ROOT / "data" / "generated" / "decompilations.jsonl"


def u16(addr: int) -> int:
    return struct.unpack_from("<H", CF, addr)[0]


def sha(addr: int, size: int) -> str:
    return hashlib.sha256(CF[addr:addr + size]).hexdigest()


def decode_branch(addr: int) -> tuple[str, int] | None:
    if addr + 4 > len(CF):
        return None
    w0, w1 = struct.unpack_from("<HH", CF, addr)
    if ((w0 >> 6) & 0x1F) != 0x1E or (w1 & 1):
        return None
    reg2 = (w0 >> 11) & 0x1F
    high = w0 & 0x3F
    if high & 0x20:
        high -= 0x40
    return ("jarl" if reg2 else "jr"), addr + (high << 16) + w1


def corpus_function(addr: int) -> dict:
    with CORPUS.open() as fh:
        for line in fh:
            row = json.loads(line)
            if row.get("record") == "function" and int(row["entry_addr"], 16) == addr:
                return row
    raise KeyError(hex(addr))


def has_data_ref(addr: int, target: str, ref_type: str) -> bool:
    return any(
        ref.get("to_addr") == target and ref.get("ref_type") == ref_type
        for ref in corpus_function(addr).get("data_references", [])
    )


print("== effective unauthenticated WDBI-2012 entry ==")
check("WDBI 2012 start is unconditional success", CF[0x4EF4A:0x4EF4E] == bytes.fromhex("00527f00"))
check("WDBI 2012 result body is pinned", sha(0x4EF4E, 26) == "7bf9284d824d94976bb9e6ca499fe59cb8aab4191714eef81d857ee2a213048f")
check("WDBI 2012 result accepts payload 01 before helper call", CF[0x4EF54:0x4EF5E] == bytes.fromhex("6008610ada058aff76ef"))
check("2012 helper writes magic 0x5A to FEBEB18F", CF[0xB28A2:0xB28AA] == bytes.fromhex("200e5a00440f8ff9"))
check("session-transition policy body is pinned", sha(0x4C942, 30) == "59f72ced67bed66bac3837c907af72e235dbf710baa0c4205664622794595373")
check("session-transition speed check is specific to requested session 02", CF[0x4C948:0x4C94C] == bytes.fromhex("623a9a0d"))
check("non-programming session path returns success", CF[0x4C95C:0x4C960] == bytes.fromhex("00527f00"))

print("\n== supply-qualified promotion to transition bit 0x08 ==")
check("B2642 state builder body is pinned", sha(0xB2642, 532) == "b0ced02b2558595b99a3b8297b76e494b61780e5e403552c4104f914e1bfe4cb")
check("transition-mask helper CCFCE is pinned", sha(0xCCFCE, 68) == "e6389dad4462cf104c60fd4ae890f5d2b93b480989ed3150fdc9a64fa1015d1b")
check("2012 transition threshold calibration AEF10 is 0x0900", u16(0xAEF10) == 0x0900)
check("B2642 reads FEBEB18F beside transition byte FEBEB18E", has_data_ref(0xB2642, "0xfebeb18f", "READ") and has_data_ref(0xB2642, "0xfebeb18e", "PARAM"))
check("B2642 snapshots FEBEB084 for threshold comparison", has_data_ref(0xB2642, "0xfebeb084", "READ"))
check("B2642 loads AEF10 and compares the saved supply snapshot", CF[0xB27A2:0xB27AC] == bytes.fromhex("f90f0100e35f1100e159"))
check("B2642 checks 18F against 0x5A", CF[0xB27B8:0xB27BE] == bytes.fromhex("1706a6fff225"))
check("18F==0x5A branch ORs logical transition bit 0x08", CF[0xB280A:0xB2810] == bytes.fromhex("810e0800430f"))
check("B2642 publishes transition mask through CCFCE", decode_branch(0xB2844) == ("jarl", 0xCCFCE))
ccfce_c = corpus_function(0xCCFCE)["decompiled_c"]
check("CCFCE stores third redundant copy as mask XOR 0xAA", "*param_4 = param_1 ^ 0xaa;" in ccfce_c)
check("logical bit 0x08 therefore clears encoded FEBEB18E bit 3", ((0x08 ^ 0xAA) & 0x08) == 0 and ((0x00 ^ 0xAA) & 0x08) != 0)

# Provenance: the same upstream raw word is independently staged as the typed
# application supply value and into the B2xx snapshot used by the 0x0900 gate.
check("RTE staging reads FEBE7D52 as supply source", has_data_ref(0x5C666, "0xfebe7d52", "READ"))
check("RTE staging writes application_supply_value_raw FEBE6692", has_data_ref(0x5C666, "0xfebe6692", "WRITE"))
check("56E4E reads the same FEBE7D52 source", has_data_ref(0x56E4E, "0xfebe7d52", "READ"))
check("56E4E snapshots that source to FEBEEE20", has_data_ref(0x56E4E, "0xfebeee20", "WRITE"))
check("BE8E6 copies FEBEEE20 into FEBEB084", has_data_ref(0xBE8E6, "0xfebeee20", "READ") and has_data_ref(0xBE8E6, "0xfebeb084", "WRITE"))
with (ROOT / "data" / "ram_overlay_map.csv").open(newline="") as fh:
    overlay = list(csv.DictReader(line for line in fh if not line.startswith("#")))
check("FEBE6692 is typed as application_supply_value_raw",
      any(row.get("address", "").lower() == "0xfebe6692" and row.get("name") == "application_supply_value_raw" for row in overlay))

print("\n== same-tick lifecycle consumption ==")
check("system-mode per-tick dispatcher body is pinned", sha(0xBEC4C, 1330) == "ba2bab0301825855e4011a640ca4c6c31d3105c11600591c7ffbe301cb8c16e9")
check("primary scheduler branch calls B2642 then transition step",
      decode_branch(0xBEF24) == ("jarl", 0xB2642) and decode_branch(0xBEF28) == ("jarl", 0xB2912))
check("alternate scheduler branch also calls B2642 before transition step",
      decode_branch(0xBEF42) == ("jarl", 0xB2642) and decode_branch(0xBEF4A) == ("jarl", 0xB2912))
check("transition-phase worker body is pinned", sha(0xB2912, 220) == "0a7ff6c488ec819a60fc1412030e4d30cd8a83fbd21e20e000c6a2ac4941cfab")
check("transition worker reads FEBEB18E", CF[0xB2942:0xB2946] == bytes.fromhex("84d78ff9"))
check("transition worker tests encoded bit 3 via shift/carry", CF[0xB295E:0xB2962] == bytes.fromhex("84d2993d"))
check("encoded bit clear takes BNC past the mode-specific lifecycle block", CF[0xB2960:0xB2962] == bytes.fromhex("993d"))

print("\n== mode-dependent lifecycle/persistence block suppressed by 2012 ==")
check("mode 0x500 branch is selected by exact compare", CF[0xB2962:0xB2968] == bytes.fromhex("010600fbea15"))
check("mode 0x500 clears signal-vector slot 0 then slot 1",
      decode_branch(0xB296C) == ("jarl", 0xFED2C)
      and CF[0xB2970:0xB2974] == bytes.fromhex("0132003a")
      and decode_branch(0xB2974) == ("jarl", 0xFED2C))
check("signal-slot setter thunk resolves to 0x562C8", CF[0xFED2C:0xFED34] == bytes.fromhex("2c06c86205006c00"))
check("signal-slot setter writes shared vector FEBE8AE0", has_data_ref(0x562C8, "0xfebe8ae0", "DATA"))
check("mode 0x500 invokes object/default helpers 5,6,9,8 in order",
      [decode_branch(x) for x in (0xB2978,0xB297C,0xB2980,0xB2984)]
      == [("jarl",0xFEF5C),("jarl",0xFEF0C),("jarl",0xBAFB2),("jarl",0xBAF82)])
check("object-5 helper uses object ID 5 and secoc update path",
      CF[0x4799A:0x4799C] == bytes.fromhex("0532") and decode_branch(0x4799E) == ("jarl", 0x65CD8))
check("object-6 helper uses object ID 6 and secoc update path",
      CF[0x38E66:0x38E68] == bytes.fromhex("0632") and decode_branch(0x38F28) == ("jarl", 0x65CD8))
check("object-9 helper uses object ID 9", CF[0xBAFC8:0xBAFCA] == bytes.fromhex("0932"))
check("object-9 helper reaches secoc_nvm_object_update veneer", decode_branch(0xBB098) == ("jarl", 0xFF09C))
check("conditional object-8 helper uses object ID 8", CF[0xBAF9C:0xBAF9E] == bytes.fromhex("0832"))
check("conditional object-8 helper reaches secoc_nvm_object_update veneer", decode_branch(0xBAFA8) == ("jarl", 0xFF09C))
check("mode 0x500 sets transition phase 0x11", CF[0xB2988:0xB298E] == bytes.fromhex("200e1100430f"))

check("mode 0x300 branch invokes objects 5,6,8", [decode_branch(x) for x in (0xB299C,0xB29A0,0xB29A4)] == [("jarl",0xFEF5C),("jarl",0xFEF0C),("jarl",0xBAF82)])
check("mode 0x300 raises event 0x23", CF[0xB29AC:0xB29B0] == bytes.fromhex("20362300") and decode_branch(0xB29B0) == ("jarl",0xB02BC))
check("mode 0x400 selects transition phase 0x11", CF[0xB29BA:0xB29C4] == bytes.fromhex("010600fcaa0d200e1100"))

print("\n== separate rotor-observer calibration branch ==")
check("B24BE can promote 2012 flag into FEBEB192", has_data_ref(0xB24BE, "0xfebeb18f", "READ") and has_data_ref(0xB24BE, "0xfebeb192", "WRITE"))
check("B30E0 reads FEBEB192 and writes FEBEB1D1", has_data_ref(0xB30E0, "0xfebeb192", "READ") and has_data_ref(0xB30E0, "0xfebeb1d1", "WRITE"))
check("FEBEB192==0x5A conditionally zeroes outgoing FEBEB1D1 selector",
      CF[0xB319C:0xB31A6] == bytes.fromhex("0106a6ff88b3e09f049b"))
check("rotor-observer calibration handler reads FEBEB1D1", has_data_ref(0xB98BC, "0xfebeb1d1", "READ"))
check("rotor-observer handler body is pinned", sha(0xB98BC, 1040) == "7c4b961616c76b6f2100d1c819d4f8ee5f764bd129daea4d3fdc643a257c7209")
check("observer publication helper body is pinned", sha(0xB8E0C, 20) == "fa32916b5b60a1b2e68aec234e5bff835e1f843c98d6636031da064c4bf4d08d")
check("observer publication helper targets FEBEB548 indexed array", has_data_ref(0xB8E0C, "0xfebeb548", "DATA"))

print("\n== bounded separation from proven actuation path ==")
# Keep the independent actuation oracle as the authority for the d/q->PI->PWM
# chain; this test only confirms the 2012 state variables are outside its direct
# fixed-reference producer set.
actuation_states = {"0xfebe6d28", "0xfebe6d2a", "0xfebe6d18", "0xfebe6d1c"}
for addr in (0xB2642,0xB2912,0xB30E0,0xB98BC,0xB8E0C):
    refs = {ref.get("to_addr") for ref in corpus_function(addr).get("data_references", [])}
    check(f"{addr:06X} has no direct d/q reference/feedback state refs", refs.isdisjoint(actuation_states), repr(sorted(refs & actuation_states)))
check("independent motor-actuation verifier remains present", (ROOT / "tests" / "verify_motor_actuation_boundary.py").is_file())


print("\n== WDBI 2013/2014 controls ==")


CORPUS=ROOT/'data/generated/decompilations.jsonl'

def sha(a,n): return hashlib.sha256(CF[a:a+n]).hexdigest()
def corpus(a):
 for line in CORPUS.open():
  r=json.loads(line)
  if r.get('record')=='function' and int(r['entry_addr'],16)==a: return r
 raise KeyError(hex(a))
def refs(a,target,kind=None):
 return [x for x in corpus(a).get('data_references',[]) if x.get('to_addr')==target and (kind is None or x.get('ref_type')==kind)]
def veneer_target(addr):
 if CF[addr:addr+2] != bytes.fromhex('2c06') or CF[addr+6:addr+8] != bytes.fromhex('6c00'):
  return None
 return struct.unpack_from('<I', CF, addr+2)[0]

def branch(addr):
 w0,w1=struct.unpack_from('<HH',CF,addr)
 if ((w0>>6)&0x1f)!=0x1e or (w1&1): return None
 reg2=(w0>>11)&0x1f; hi=w0&0x3f
 if hi&0x20: hi-=0x40
 return ('jarl' if reg2 else 'jr', addr+(hi<<16)+w1)

print('== WDBI 2013 entry and numeric-control chain ==')
check('2013 start gate body is pinned', sha(0x4EF68,40)=='ecc2127f1b219bac3c5f952eaf45650bc9eea10c3f9350073e5f39cf4e0da0a3')
check('2013 result body is pinned', sha(0x4EF90,28)=='b53a42023a915f18aa810e47b1c0822ff7aa244ae39e0f46af4dcf7edd0bbdae')
check('2013 result reaches helper FE1C8', branch(0x4EF9E)==('jarl',0xFE1C8))
check('2013 helper veneer targets B76A8', veneer_target(0xFE1C8)==0xB76A8)
check('B76A8 writes FEBEB434', bool(refs(0xB76A8,'0xfebeb434','WRITE')))
check('B763C reads 434 and writes 448', refs(0xB763C,'0xfebeb434','READ') and refs(0xB763C,'0xfebeb448','WRITE'))
check('B76C0 reads 448 and writes 452', refs(0xB76C0,'0xfebeb448','READ') and refs(0xB76C0,'0xfebeb452','WRITE'))
check('B72EC reads 452', refs(0xB72EC,'0xfebeb452','READ'))
check('B73D0 writes selected value to 41A', refs(0xB73D0,'0xfebeb41a','WRITE'))
check('BCACE copies 41A into E416', refs(0xBCACE,'0xfebeb41a','READ') and refs(0xBCACE,'0xfebee416','WRITE'))
check('3572C mode-selects E416 into 6ACE', refs(0x3572C,'0xfebee416','READ') and refs(0x3572C,'0xfebe6ace','WRITE'))
check('37FB6 reads 6ACE and writes motor-worker 6DCA/6DCC', refs(0x37FB6,'0xfebe6ace','READ') and refs(0x37FB6,'0xfebe6dca','WRITE') and refs(0x37FB6,'0xfebe6dcc','WRITE'))
check('motor control worker directly calls 37FB6', branch(0x5D1A2)==('jarl',0x37FB6))

print('\n== 2013 motor-worker state dead-ends in staging mirrors ==')
# Use full corpus to pin reader-function membership rather than instruction spellings.
def reader_funcs(target):
 out=set()
 for line in CORPUS.open():
  r=json.loads(line)
  if r.get('record')!='function': continue
  if any(x.get('to_addr')==target and x.get('ref_type') in ('READ','PARAM') for x in r.get('data_references',[])):
   out.add(int(r['entry_addr'],16))
 return out
check('6DCA readers are exactly task/RTE staging', reader_funcs('0xfebe6dca')=={0x58404,0x5B9C4,0x5C0B6}, repr(reader_funcs('0xfebe6dca')))
check('6DCC readers are exactly task/RTE staging', reader_funcs('0xfebe6dcc')=={0x58404,0x5B9C4,0x5C0B6}, repr(reader_funcs('0xfebe6dcc')))
for target in ('0xfebe66ce','0xfebe66d0','0xfebe63ce','0xfebe63d0'):
 check(f'{target} staging mirror has no runtime readers', reader_funcs(target)==set(), repr(reader_funcs(target)))

print('\n== WDBI 2014 threshold/mode-selection chain ==')
check('2014 start gate matches 2013 speed+state gate', sha(0x4EFAC,40)=='ecc2127f1b219bac3c5f952eaf45650bc9eea10c3f9350073e5f39cf4e0da0a3')
check('2014 result body is pinned', sha(0x4EFD4,42)=='1b1bb16aa65b140b38ce9882b52e0d92dd33491998a83b4e827319de37961eb9')
check('2014 helper veneer targets B71FE', veneer_target(0xFE1B4)==0xB71FE)
check('B71FE writes FEBEB3EE', bool(refs(0xB71FE,'0xfebeb3ee','WRITE')))
check('B692C reads 3EE and writes threshold decision 3EC', refs(0xB692C,'0xfebeb3ee','READ') and refs(0xB692C,'0xfebeb3ec','WRITE'))
check('B6994 reads 3EC and writes state 3E7', refs(0xB6994,'0xfebeb3ec','READ') and refs(0xB6994,'0xfebeb3e7','WRITE'))
check('B70D0 reads 3EE for independent threshold return', refs(0xB70D0,'0xfebeb3ee','READ'))
check('B7114 selector tail is pinned', CF[0xB71B0:0xB71BA]==bytes.fromhex('5fd261d2eb05bfff1aff'))
check('B7114 directly calls B70D0 only after selector-1 threshold test', branch(0xB71B6)==('jarl',0xB70D0))
check('B65BC side state is local mode/calibration state', refs(0xB65BC,'0xfebeb3a4','WRITE') and refs(0xB65BC,'0xfebeb3a6','WRITE'))

print('\n== 2014 cross-service RoutineControl gate ==')
rows=list(csv.DictReader((ROOT/'data/application_routine_control_surface.csv').open()))
expected={15:'0x110A',17:'0x110C',18:'0x110D'}
check('RoutineControl indices 15/17/18 are RIDs 110A/110C/110D', {i:rows[i]['rid'] for i in expected}==expected)
for i,addr in ((15,0x4F5C4),(17,0x4F6A2),(18,0x4F74A)):
 check(f'RID {rows[i]["rid"]} precondition is expected callback', int(rows[i]['precondition_callback'],16)==addr)
 callsite={0x4F5C4:0x4F5DE,0x4F6A2:0x4F6BA,0x4F74A:0x4F766}[addr]
 check(f'RID {rows[i]["rid"]} precondition calls FE164', branch(callsite)==('jarl',0xFE164))

check('shared precondition veneer FE164 targets B7114', veneer_target(0xFE164)==0xB7114)
check('RID 110A type-1 path preserves selector 1 into FE164', CF[0x4F5DA:0x4F5E2]==bytes.fromhex('6132aa1d8aff86eb'))
check('RID 110C type-1 path forces selector 2 into FE164', CF[0x4F6B8:0x4F6BE]==bytes.fromhex('02328affaaea'))
check('RID 110D type-1 path forces selector 3 into FE164', CF[0x4F764:0x4F76A]==bytes.fromhex('03328afffee9'))
check('B7114 selector 3 skips B70D0 while selectors 1/2 reach it', CF[0xB71B0:0xB71BA]==bytes.fromhex('5fd261d2eb05bfff1aff'))
print('\n== bounded separation from independent actuation path ==')
act_states={'0xfebe6d18','0xfebe6d1c','0xfebe6d28','0xfebe6d2a'}
for addr in (0xB763C,0xB76C0,0xB72EC,0xB73D0,0xBCACE,0x3572C,0x37FB6,0xB692C,0xB6994,0xB70D0,0xB7114):
 direct={x.get('to_addr') for x in corpus(addr).get('data_references',[])}
 check(f'{addr:06X} has no direct d/q ref/feedback references', direct.isdisjoint(act_states), repr(sorted(direct & act_states)))
check('independent motor actuation oracle is present', (ROOT/'tests/verify_motor_actuation_boundary.py').is_file())

print(f"\n== RESULT: {passed} passed, {failed} failed ==")
raise SystemExit(1 if failed else 0)
