#!/usr/bin/env python3
"""Verify the RDBI producer emitted-write audit (MEM-SAFE-006 closure).

Pins, from firmware bytes and the tracked decompiler corpus:

  1. byte-identical regeneration of the artifact;
  2. the DID-table census: 242 configured rows, 196 unique producers, each
     producer serving exactly one declared length, all lengths 1..45;
  3. the count convention: 0x8A374 initializes the count slot from the
     DID-table record word (+2, via 0x8A31E -> 0x4C81A) BEFORE the producer
     runs, and the render loop 0x9429E advances by that slot — the emitted
     count is configuration-owned, never producer-returned;
  4. for all 196 producers: classified write extent never exceeds the declared
     length; class census is exact; every artifact body hash re-derives from
     firmware bytes and every corpus C hash re-derives from the corpus;
  5. the 46 zero-write producers are exactly the four-byte success stubs
     (raw `00 52 7f 00`), and the DID set that writes fewer bytes than
     declared is exactly the verified 48-DID stale census;
  6. exceptional classes pinned from raw bytes / hash-pinned corpus C:
     checkpoint magic 0xA55A5AA5 and the '?' (0x3f) fill constant in the
     checkpoint readers, loop-bound expressions, the F186 register delegate
     chain, and the three engines' internal declared_len guards.
"""
from __future__ import annotations

import hashlib
import json
import struct
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CF = (ROOT / "firmware" / "RH850_P1M-E_CodeFlash.bin").read_bytes()
ARTIFACT = ROOT / "data" / "generated" / "rdbi_emitted_write_audit.json"
CORPUS = ROOT / "data" / "generated" / "decompilations.jsonl"
GENERATOR = ROOT / "tools" / "generate_rdbi_emitted_write_audit.py"

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

passed = failed = 0


def check(name: str, condition: bool, detail: str = "") -> None:
    global passed, failed
    if condition:
        passed += 1
        print(f"[PASS] {name}")
    else:
        failed += 1
        print(f"[FAIL] {name}" + (f" ({detail})" if detail else ""))


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load_corpus() -> dict[str, dict]:
    functions: dict[str, dict] = {}
    with CORPUS.open(encoding="utf-8") as handle:
        for number, line in enumerate(handle, 1):
            if number == 1:
                continue
            record = json.loads(line)
            functions[record["entry_addr"]] = record
    return functions


def main() -> int:
    audit = json.loads(ARTIFACT.read_text())
    corpus = load_corpus()

    print("== regeneration is byte-identical ==")
    before = ARTIFACT.read_bytes()
    result = subprocess.run([sys.executable, str(GENERATOR)], capture_output=True, text=True)
    check("generator exit 0", result.returncode == 0, result.stderr[-300:])
    check("regenerated artifact matches tracked artifact", ARTIFACT.read_bytes() == before)
    check("generator reports zero exceedances", "exceeds=0" in result.stdout, result.stdout)

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
    c8a374 = corpus["0x0008a374"]["decompiled_c"]
    check("0x8A374 initializes the count slot before dispatching",
          c8a374.index("FUN_0008a31e(param_2)") < c8a374.index("FUN_0004cb8a(param_1,*param_2)"))
    check("0x4C81A reads the DID-record length word at record+2",
          "* 0x10 + iVar3 + 2);" in corpus["0x0004c81a"]["decompiled_c"])
    check("0x4CB8A invokes the configured producer with (dest, declared_len)",
          "((uint)*(ushort *)(puVar1 + -0xda4) * 0x10 + iVar2 + 4))(param_1,param_2)"
          in corpus["0x0004cb8a"]["decompiled_c"])
    check("render loop advances by the count slot, not a producer return",
          "(undefined *)(*(int *)(iVar4 + -0x5a98) + (uint)auStack_22[0]);"
          in corpus["0x0009429e"]["decompiled_c"])

    print("== emitted-write closure over all 196 producers ==")
    entries = audit["callbacks"]
    check("no producer write extent exceeds its declared length",
          all(entry["max_write_extent"] <= entry["declared_len"] for entry in entries))
    check("class census is exact", audit["summary"]["classes"] == {
        "direct_fixed": 134, "success_stub": 46, "engine_declared_bounded": 11,
        "fixed_extent_loop": 3, "declared_bounded_loop": 1, "register_delegate": 1,
    }, str(audit["summary"]["classes"]))
    check("150 exact-fit, 46 zero-write, no non-stub under-writer",
          audit["summary"]["exact_fit"] == 150 and audit["summary"]["zero_write"] == 46
          and audit["summary"]["under_nonzero"] == 0 and audit["under_writers_non_stub"] == [])
    check("artifact DID multiset matches the configured table",
          sorted(int(d["did"], 16) for e in entries for d in e["dids"])
          == sorted(row[0] for row in producers))

    ok_hash = ok_corpus = True
    for entry in entries:
        callback = int(entry["callback"], 16)
        record = corpus[entry["callback"]]
        if entry["body_sha256"] != sha256(CF[callback:callback + entry["body_size"]]):
            ok_hash = False
        if record["body_size"] != entry["body_size"]:
            ok_hash = False
        if entry["decompiled_c_sha256"] != sha256(record["decompiled_c"].encode()):
            ok_corpus = False
        if entry["declared_len"] not in {d["declared"] for d in entry["dids"]}:
            ok_corpus = False
    check("every producer body hash re-derives from firmware bytes", ok_hash)
    check("every corpus C hash re-derives from the tracked corpus", ok_corpus)

    print("== zero-write producers are the verified stale census ==")
    stubs = [entry for entry in entries if entry["class"] == "success_stub"]
    check("46 zero-write producers are exactly the four-byte success stubs",
          len(stubs) == 46 and all(CF[int(e["callback"], 16):int(e["callback"], 16) + 4] == SUCCESS_STUB
                                   for e in stubs))
    stub_dids = {int(d["did"], 16) for e in stubs for d in e["dids"]}
    under_dids = {int(d["did"], 16) for e in entries if e["write_relation"] != "exact_fit" for d in e["dids"]}
    check("DIDs writing fewer bytes than declared are exactly the verified 48",
          under_dids == VERIFIED_STUB_DIDS == stub_dids, str(under_dids ^ VERIFIED_STUB_DIDS))

    print("== exceptional classes pinned from raw bytes / corpus C ==")
    magic = bytes.fromhex("a55a5aa5")
    fill = bytes.fromhex("209e3f00")  # '?' fill constant materialization
    for entry in entries:
        callback = int(entry["callback"], 16)
        body = CF[callback:callback + entry["body_size"]]
        c = corpus[entry["callback"]]["decompiled_c"]
        if entry["class"] == "fixed_extent_loop" and entry["callback"] in ("0x0004ccc4", "0x0004cd74"):
            check(f"{entry['callback']} body carries the checkpoint magic", magic in body)
            if entry["callback"] == "0x0004ccc4":
                check("DID 0105 extent is exactly 12 (10-loop + fixed +10/+11)",
                      entry["max_write_extent"] == 12 and entry["declared_len"] == 12
                      and "iVar4 + -9" in c and c.count("iVar4 + -9") == 2
                      and "*(undefined1 *)(param_1 + 0xb) = 0;" in c)
                check("DID 0105 '?' fill constant pinned in raw bytes", fill in body)
            if entry["callback"] == "0x0004cd74":
                check("DID 010B extent is exactly 16 (16-iteration copy)",
                      entry["max_write_extent"] == 16 and entry["declared_len"] == 16
                      and "iVar4 + -0xf" in c and "0x3f" not in c and fill not in body)
            if entry["callback"] == "0x0004e8e4":
                check("application F181 extent is exactly 17 (1 + 16-byte software-ID record)",
                      entry["max_write_extent"] == 17 and entry["declared_len"] == 17
                      and "param_1[iVar3 + 1] = (&application_software_id_record_1)[iVar3];" in c)
        if entry["class"] == "declared_bounded_loop":
            check("F18C loops are bounded by the forwarded declared_len",
                  entry["callback"] == "0x0004e918" and "iVar3 - (param_2 & 0xffff)" in c
                  and c.count("iVar3 - (param_2 & 0xffff)") == 2 and magic in body and fill in body)
        if entry["class"] == "register_delegate":
            check("F186 declared length is 1 with a single-byte terminal writer",
                  entry["callback"] == "0x0004e90a" and entry["declared_len"] == 1
                  and entry["max_write_extent"] == 1)
            check("F186 delegate chain: 0x4E90A -> 0x8FDDE -> 0x907E6 single-byte store",
                  "FUN_0008fdde();" in c
                  and "FUN_000907e6();" in corpus["0x0008fdde"]["decompiled_c"]
                  and "*param_1 = *(undefined1 *)(puVar1 + -0x17b3);" in corpus["0x000907e6"]["decompiled_c"])
        if entry["class"] == "engine_declared_bounded":
            check(f"{entry['callback']} engine wrapper forwards (dest, declared_len) and declares 32",
                  entry["declared_len"] == 32 and ("(param_1,param_2)" in c or ",param_1,param_2)" in c)
                  and any(engine in entry["bound_source"] for engine in
                          ("0004c530", "0004c604", "000518f6")))

    print("== engine internals bound every write by the forwarded length ==")
    c530 = corpus["0x0004c530"]["decompiled_c"]
    c604 = corpus["0x0004c604"]["decompiled_c"]
    f6 = corpus["0x000518f6"]["decompiled_c"]
    check("0x4C530 clear loop and OR writes are length-guarded",
          "uVar4 < (param_2 & 0xffff)" in c530 and "uVar4 < (param_2 & 0xff)" in c530)
    check("0x4C604 clear loop and OR writes are length-guarded (dest param_2, len param_3)",
          "uVar3 < (param_3 & 0xffff)" in c604 and "uVar7 < (param_3 & 0xff)" in c604)
    check("0x518F6 clear loop and serial writes are length-guarded",
          "iVar4 - (param_2 & 0xffff)" in f6 and "(uVar5 + 3) - (param_2 & 0xffff)" in f6)
    check("engine wrapper bodies pinned", all(
        corpus[f"0x{addr:08x}"]["body_size"] == size
        for addr, size in ((0x4C530, 126), (0x4C604, 144), (0x518F6, 158))
    ))

    print("== closure summary ==")
    check("artifact records zero exceedances", audit["summary"]["exceeds_declared"] == 0)
    check("max non-stub write extent is 32 and every 45-byte DID is a zero-write stub",
          audit["summary"]["max_extent"] == 32
          and all(e["class"] == "success_stub" for e in entries if e["declared_len"] == 45))

    print(f"\nSummary: {passed} passed, {failed} failed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
