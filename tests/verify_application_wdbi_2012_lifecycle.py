#!/usr/bin/env python3
"""Verify the bounded lifecycle/persistence consequence of application WDBI DID 0x2012."""
from __future__ import annotations

import csv
import hashlib
import json
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CF = (ROOT / "firmware" / "RH850_P1M-E_CodeFlash.bin").read_bytes()
CORPUS = ROOT / "data" / "generated" / "decompilations.jsonl"
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

print(f"\nSummary: {passed} passed, {failed} failed")
sys.exit(1 if failed else 0)
