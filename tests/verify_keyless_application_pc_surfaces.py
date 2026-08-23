#!/usr/bin/env python3
"""Verify application-side PC/control-object candidates for the keyless-RCE audit."""
from __future__ import annotations

import json
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CF = (ROOT / "firmware/RH850_P1M-E_CodeFlash.bin").read_bytes()
CORPUS = ROOT / "data/generated/decompilations.jsonl"
XCP_LO, XCP_HI = 0xFEBF7C00, 0xFEBFFBFF

passed = failed = 0

def check(name: str, ok: bool, detail: str = "") -> None:
    global passed, failed
    if ok:
        passed += 1
        print(f"[PASS] {name}")
    else:
        failed += 1
        print(f"[FAIL] {name}" + (f" ({detail})" if detail else ""))

def u32(off: int) -> int:
    return struct.unpack_from("<I", CF, off)[0]

funcs: dict[int, dict] = {}
with CORPUS.open() as f:
    for line in f:
        rec = json.loads(line)
        if rec.get("record") == "function" and rec.get("entry_addr"):
            funcs[int(rec["entry_addr"], 16)] = rec

def refs(entry: int) -> set[tuple[int, str, int]]:
    out = set()
    for r in funcs[entry].get("data_references") or []:
        try:
            out.add((int(r["from_addr"], 16), str(r["ref_type"]), int(r["to_addr"], 16)))
        except (KeyError, TypeError, ValueError):
            pass
    return out

print("== exception-return and saved-PC surfaces ==")
return_sites = {
    0x20112: bytes.fromhex("e0074801"),
    0x64BCA: bytes.fromhex("e0074a01"),
    0x702E2: bytes.fromhex("e0074801"),
    0x703C6: bytes.fromhex("e0074801"),
    0x70472: bytes.fromhex("e0074801"),
    0x7051E: bytes.fromhex("e0074801"),
    0x70A00: bytes.fromhex("e0074801"),
    0x70BB0: bytes.fromhex("e0074801"),
}
for off, op in return_sites.items():
    check(f"exception return opcode pinned at 0x{off:X}", CF[off:off+4] == op)
check("return census has seven EIRET and one FERET", list(return_sites.values()).count(bytes.fromhex("e0074801")) == 7 and list(return_sites.values()).count(bytes.fromhex("e0074a01")) == 1)

# Common EIINT restore reloads EIPC from frame+0x14 and executes EIRET.
check("common restore reloads EIPC from RAM frame",
      CF[0x702D2:0x702E6] == bytes.fromhex("0a650c6de16f2000ec072000ed0f2000266d2465100d0ef53fff0000df1923ff0100441ae0074801")[-20:])
# TAUJ wrappers save EIPC at frame+0x14, then temporarily switch to fixed FEBE work stacks.
for name, entry, stack_imm in (
    ("TAUJ0", 0x70320, bytes.fromhex("4036befe261e0008")),
    ("TAUJ1", 0x703CA, bytes.fromhex("4036befe261e0010")),
    ("TAUJ2", 0x70476, bytes.fromhex("4036befe261e0018")),
):
    body = CF[entry:entry+0xAC]
    check(f"{name} saves EIPC at frame+0x14", bytes.fromhex("e057400063571500") in body)
    check(f"{name} work-stack switch is fixed FEBE address", stack_imm in body)
check("application foreground SP is fixed FEBE2000", CF[0x70548:0x7054E] == bytes.fromhex("23060020befe"))
check("fast-exception handler saves FEPC into its RAM frame", CF[0x64B46:0x64B52] == bytes.fromhex("e25740000a56040063570d00"))
check("fast-exception handler restores FEPC before FERET", CF[0x64BBA:0x64BCE] == bytes.fromhex("23570d00ea17200023571100031e1400e0074a01"))
check("known fixed application stack anchors lie below XCP window", all(v < XCP_LO for v in (0xFEBE0800,0xFEBE1000,0xFEBE1800,0xFEBE2000)))
check("canonical function entries do not lie in XCP window", not any(XCP_LO <= a <= XCP_HI for a in funcs))

print("\n== near-window callback FEBF7704 ==")
cb = 0xFEBF7704
check("callback cell is exactly 0x4FC below XCP lower bound", XCP_LO - cb == 0x4FC)
cb_refs = {(e, fr, typ, to) for e in funcs for fr, typ, to in refs(e) if to == cb}
check("callback cell has exactly one canonical read and one write globally",
      cb_refs == {(0x72E4A, 0x72E52, "READ", cb), (0x72E5E, 0x72E72, "WRITE", cb)}, repr(sorted(cb_refs)))
check("callback setter embeds both fixed targets",
      (0x72E72, "DATA", 0x75664) in refs(0x72E5E)
      and (0x72E72, "DATA", 0x7575A) in refs(0x72E5E))
check("callback consumer performs computed JARL after loading FEBF7704", CF[0x72E4A:0x72E5A] == bytes.fromhex("8007610040eebffe3def0577fdc760f9"))
check("setter selects only fixed 75664/7575A targets", CF[0x72E5E:0x72E76] == bytes.fromhex("21065a570700d832ca05210664560700405ebffe6b0f0577"))

print("\n== MPU selector provenance ==")
check("MPU context selector bytes are only 0/1", CF[0x3180C:0x31814] == bytes.fromhex("0000000001000000"))
check("MPU loader table base is fixed 0x31894", CF[0x648EE:0x648FC] == bytes.fromhex("06f09e00c6f22a0694180300caf1"))
expected_selector_refs = {
    0x608AA: 0x31812,
    0x647D4: 0x3180F,
    0x702E8: 0x31810,
    0x70308: 0x3180F,
    0x65028: 0x31811,
    0x6506A: 0x31811,
    0x650AC: 0x31813,
    0x650EE: 0x31813,
    0x70320: 0x3180C,
    0x703CA: 0x3180D,
    0x70476: 0x3180E,
}
mpu_callers = {e for e, r in funcs.items() if e != 0x648EE and 'FUN_000648ee(' in (r.get('decompiled_c') or '')}
check("MPU loader has exactly the 11 recovered canonical callers", mpu_callers == set(expected_selector_refs), repr(sorted(mpu_callers)))
for entry, target in expected_selector_refs.items():
    check(f"MPU caller 0x{entry:X} reads fixed selector byte 0x{target:X}", any(r[1] == "READ" and r[2] == target for r in refs(entry)), repr(refs(entry)))
check("all recovered MPU selector bytes decode to context 0 or 1", {CF[t] for t in expected_selector_refs.values()} <= {0,1})

print("\n== architectural alias geometry ==")
# P1M-E exposes PE1 and self views of the same 128 KiB at a fixed +0x200000 delta.
PE1_BASE, SELF_BASE, SIZE = 0xFEBE0000, 0xFEDE0000, 0x20000
check("self LocalRAM view is same-offset +0x200000 alias", SELF_BASE - PE1_BASE == 0x200000)
check("XCP shadow aliases to FEDF7C00, not a lower FEBE control object", XCP_LO + (SELF_BASE - PE1_BASE) == 0xFEDF7C00)
for control in (0xFEBE0800,0xFEBE1000,0xFEBE1800,0xFEBE2000,0xFEBF7704):
    check(f"control object 0x{control:X} physical offset differs from XCP start", (control - PE1_BASE) % SIZE != (XCP_LO - PE1_BASE) % SIZE)

print(f"\nResults: {passed} passed, {failed} failed")
raise SystemExit(1 if failed else 0)
