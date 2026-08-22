#!/usr/bin/env python3
"""Pin the critical raw-byte boundaries behind SEC-BOOT-013.

This is not a proof of global exploit absence. It protects the specific negative
claims used by docs/security/bootloader-noauth-pc-pivot-assessment.md: fixed
handoff source, bounded DCM transport, state-2 anti-concurrency ordering, exact
SecurityAccess lengths, and immutable-size service table.
"""
from __future__ import annotations

import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CF = (ROOT / "firmware/RH850_P1M-E_CodeFlash.bin").read_bytes()
passed = failed = 0


def check(name: str, condition: object, detail: str = "") -> None:
    global passed, failed
    ok = bool(condition)
    passed += int(ok); failed += int(not ok)
    print(f"[{'PASS' if ok else 'FAIL'}] {name}" + (f" ({detail})" if detail else ""))


print("== fixed live-handoff source ==")
check("application handoff loads fixed r6=0x31914 before 0x9F00",
      CF[0x64EE6:0x64EF0] == bytes.fromhex("260614190300baff1450"),
      CF[0x64EE6:0x64EF0].hex())
check("fixed record is kind0 / 7A1 / session2",
      tuple(struct.unpack_from("<9I", CF, 0x31914)) == (0,0x7A1,0,0,2,0,0,0,0))

print("\n== immutable bounded service dispatch ==")
records=[struct.unpack_from("<BBHI",CF,0x8E54+i*8) for i in range(20)]
check("boot UDS table has 20 distinct SID records", len(records)==20 and len({r[0] for r in records})==20)
check("SID 27 is fixed handler 5516", next(r for r in records if r[0]==0x27)==(0x27,0x02,0,0x5516))
check("mutating transfer handlers are fixed table targets",
      {r[0]:r[3] for r in records if r[0] in (0x2E,0x31,0x34,0x36,0x37)} ==
      {0x2E:0x4948,0x31:0x567E,0x34:0x5D68,0x36:0x4DBA,0x37:0x5C92})

print("\n== DCM receive bounds and anti-race ordering ==")
check("StartOfReception rejects total length above 0x1000",
      CF[0x638C:0x63A2] == bytes.fromhex("0806ffef64c8f105200e001000ea690f0000a50503ea"),
      CF[0x638C:0x63A2].hex())
check("StartOfReception rejects immediately when DCM receive state is 2",
      CF[0x63A2:0x63AA] == bytes.fromhex("840fbb93620aa21d"),
      CF[0x63A2:0x63AA].hex())
check("successful TpRxIndication stores state 2 before service dispatch",
      CF[0x64E6:0x6500] == bytes.fromhex("020ae43fb9986457ad936457b193440fba934407bb93bfff26ed"),
      CF[0x64E6:0x6500].hex())
check("CopyRxData computes 0x1000-current and rejects oversized fragment before copy",
      CF[0x6474:0x6490] == bytes.fromhex("e49fb998200e0010b309e1e98f151d08d309640fb8981d38bfff96ff"),
      CF[0x6474:0x6490].hex())
check("underlying byte copier clamps cursor at 0x1000",
      CF[0x6426:0x6444] == bytes.fromhex("e40fb9930798c199130600f0960d003a010600f0d105203e0010a139c700"),
      CF[0x6426:0x6444].hex())

print("\n== SecurityAccess parser widths ==")
check("request-seed requires exact total length 0x12",
      CF[0x5340:0x534A] == bytes.fromhex("0606eeffe20520361300"))
check("send-key gates state then requires exact total length 0x12",
      CF[0x53F6:0x5412] == bytes.fromhex("c600a4ef559361eae1070f01e207050163eaeb070501d97d0606eeff"))
check("send-key expected-key compute receives fixed length 0x10",
      CF[0x5464:0x546C] == bytes.fromhex("0736100080ffe41b"))

print("\n== known authenticated callback remains distinct ==")
check("FF00 callback load remains FEBF0FD0",
      CF[0x434C:0x4354] == bytes.fromhex("40eebffe3defd10f"),
      CF[0x434C:0x4354].hex())
check("callback call is indirect only after that load",
      CF[0x435E:0x4362] == bytes.fromhex("fdc760f9"))

print(f"\n== RESULT: {passed} passed, {failed} failed ==")
raise SystemExit(1 if failed else 0)
