#!/usr/bin/env python3
"""Verify that application WDBI DID 0x2010 only writes dead diagnostic residue."""
from __future__ import annotations

import csv
import hashlib
import json
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CF = (ROOT / "firmware/RH850_P1M-E_CodeFlash.bin").read_bytes()
CORPUS = ROOT / "data/generated/decompilations.jsonl"
passed = failed = 0


def check(name: str, condition: object, detail: str = "") -> None:
    global passed, failed
    ok = bool(condition)
    passed += int(ok)
    failed += int(not ok)
    print(f"[{'PASS' if ok else 'FAIL'}] {name}" + (f" ({detail})" if detail else ""))


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

print(f"\nSummary: {passed} passed, {failed} failed")
raise SystemExit(1 if failed else 0)
