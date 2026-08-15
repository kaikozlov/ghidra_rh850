#!/usr/bin/env python3
"""Generate the RDBI producer emitted-write audit (MEM-SAFE-006 closure).

Question closed
---------------
For every configured RDBI producer callback (the 196 unique nonzero targets in
the application DID table at 0x2941C), can the callback ever write beyond the
response slot it is given?

The count the render loop advances by is *not* producer-returned: the producer
helper 0x8A374 first writes the configured per-DID length word (DID-table
record +2, read through 0x8A31E -> 0x4C81A) into the count slot and only then
invokes the configured producer through dispatcher 0x4CB8A as
``callback(dest, declared_len)``. The render loop 0x9429E afterwards advances
the write position by exactly that slot. The memory-safety question is
therefore purely: **does any producer write past ``dest[declared_len - 1]``?**

Method
------
Deterministic classification of each unique callback body from firmware bytes
plus the tracked, provenance-locked decompiler corpus
(``data/generated/decompilations.jsonl``; every corpus record's C is hashed and
every callback's raw body is re-hashed here, tying the two together):

  success_stub          body is exactly ``00 52 7f 00`` (mov 0,r10; jmp lp):
                        writes nothing (the verified 48-DID stale census).
  direct_fixed          corpus C shows only fixed-offset byte/word/dword
                        stores and the pinned 2/4-byte little-endian store
                        helpers (0x694CC/0x69504 = 4B, 0x694E4/0x6951C = 2B)
                        at constant offsets from ``dest``; extent is the max
                        offset+width.
  engine_declared_bounded
                        wrapper forwards ``(dest, declared_len)`` to one of the
                        three table/serial engines (0x4C530 DTC-mask-by-low,
                        0x4C604 DTC-mask-by-range, 0x518F6 serial-number
                        list); every engine write is guarded by the forwarded
                        declared_len.
  declared_bounded_loop corpus C shows the copy loop bound is
                        ``(declared_len & 0xffff)`` itself (F18C NvM serial).
  fixed_extent_loop     corpus C shows a constant trip count and/or fixed
                        post-loop stores (DID 0105 checkpoint 0x204 copy,
                        DID 010B checkpoint 0x20A copy, application F181
                        software-ID record copy).
  register_delegate     F186 forwards its argument registers to the session
                        API 0x8FDDE -> 0x907E6, whose only destination write
                        is a single byte at ``dest`` (declared length 1).

Any callback whose corpus C contains a ``param_1``-rooted write the classifier
does not fully account for is a hard error: classification is exhaustive or it
does not run. Exceptional callbacks are additionally pinned by raw-byte
substrings (checkpoint magic 0xA55A5AA5, the '?' = 0x3f fill constant) and by
their loop-bound expressions in the hash-pinned corpus C.

Output: data/generated/rdbi_emitted_write_audit.json
"""
from __future__ import annotations

import hashlib
import json
import re
import struct
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
CF = (REPO / "firmware" / "RH850_P1M-E_CodeFlash.bin").read_bytes()
CORPUS = REPO / "data" / "generated" / "decompilations.jsonl"
OUT = REPO / "data" / "generated" / "rdbi_emitted_write_audit.json"

DID_TABLE = 0x2941C
DID_ROWS = 0xF2
SUCCESS_STUB = bytes.fromhex("00527f00")
CHECKPOINT_MAGIC = bytes.fromhex("a55a5aa5")
FILL_3F = bytes.fromhex("209e3f00")  # materialization of the '?' fill constant

# Pinned little-endian store helpers: name -> bytes written at dest (+ offset).
STORE_HELPERS = {
    "FUN_000694cc": 4,
    "direct_call_target_00069504": 4,
    "FUN_000694e4": 2,
    "FUN_0006951c": 2,
}
# Pinned engines: name -> (bound argument, internal bound note).
ENGINES = {
    "direct_call_target_0004c530": (
        "param_2",
        "clear loop `uVar4 < (param_2 & 0xffff)`; every OR write guarded by `uVar4 < (param_2 & 0xff)`",
    ),
    "direct_call_target_0004c604": (
        "param_3",
        "writes at dest param_2; clear loop `uVar3 < (param_3 & 0xffff)`; every OR write guarded by `uVar7 < (param_3 & 0xff)`",
    ),
    "direct_call_target_000518f6": (
        "param_2",
        "clear loop `iVar4 < (param_2 & 0xffff)`; each 3-byte DTC triple and its 1-byte status store are behind `uVar5 + 3 - (param_2 & 0xffff) < 0`",
    ),
}

# Exceptional callbacks pinned from corpus C + raw bytes during this analysis.
PINNED_EXCEPTIONS: dict[int, dict] = {
    0x4CCC4: {
        "class": "fixed_extent_loop",
        "extent": 12,
        "dids": [0x0105],
        "note": "checkpoint_object 0x204 (magic 0xA55A5AA5): 10-iteration copy loop at dest[0..9] "
                "plus fixed zero stores at dest[10] and dest[11]; invalid-record branch fills "
                "dest[0..9] with '?' instead; both loops trip-count 10 (`iVar4 + -9`)",
        "c_bounds": ["iVar4 + -9", "*(undefined1 *)(param_1 + 10) = 0;", "*(undefined1 *)(param_1 + 0xb) = 0;"],
        "raw_pins": [CHECKPOINT_MAGIC, FILL_3F],
    },
    0x4CD74: {
        "class": "fixed_extent_loop",
        "extent": 16,
        "dids": [0x010B],
        "note": "checkpoint_object 0x20A (magic 0xA55A5AA5): single 16-iteration copy loop at "
                "dest[0..15]; invalid-record branch writes nothing (under-write only, error 5)",
        "c_bounds": ["iVar4 + -0xf"],
        "raw_pins": [CHECKPOINT_MAGIC],
    },
    0x4E8E4: {
        "class": "fixed_extent_loop",
        "extent": 17,
        "dids": [0xF181],
        "note": "application F181: `*dest = 1` then a 16-iteration copy of the software-ID record "
                "at dest[1..16] (declared 17)",
        "c_bounds": ["iVar3 + -0xf", "param_1[iVar3 + 1] = (&application_software_id_record_1)[iVar3];"],
        "raw_pins": [],
    },
    0x4E918: {
        "class": "declared_bounded_loop",
        "extent": None,  # bounded by declared_len itself
        "dids": [0xF18C],
        "note": "checkpoint_object 0x207 serial: both the copy loop and the '?'-fill loop are "
                "bounded by `(param_2 & 0xffff)`, i.e. the declared length forwarded by the caller",
        "c_bounds": ["iVar3 - (param_2 & 0xffff)", "= 0x3f;"],
        "raw_pins": [CHECKPOINT_MAGIC, FILL_3F],
    },
    0x4E90A: {
        "class": "register_delegate",
        "extent": 1,
        "dids": [0xF186],
        "note": "forwards its argument registers to the Dcm session API 0x8FDDE, which tail-calls "
                "0x907E6; the only destination write in that chain is the single-byte store "
                "`*param_1 = *(undefined1 *)(puVar1 + -0x17b3)` (declared length 1)",
        "c_bounds": ["FUN_0008fdde();"],
        "delegate_chain": [
            ("0x0008fdde", "if (param_1 == 0)", "FUN_000907e6();"),
            ("0x000907e6", "*param_1 = *(undefined1 *)(puVar1 + -0x17b3);", None),
        ],
        "raw_pins": [],
    },
}

DIRECT_WRITE_RES: list[tuple[re.Pattern, int | None, int]] = [
    (re.compile(r"^\s*\*param_1 = "), 0, 1),
    (re.compile(r"^\s*\*\(bool \*\)param_1 = "), 0, 1),
    (re.compile(r"^\s*\*\(ushort \*\)param_1 = "), 0, 2),
    (re.compile(r"^\s*param_1\[(\d+)\] = "), None, 1),
    (re.compile(r"^\s*\*\(undefined1 \*\)\(param_1 \+ (\d+)\) = "), None, 1),
    (re.compile(r"^\s*\*\(undefined2 \*\)\(param_1 \+ (\d+)\) = "), None, 2),
    (re.compile(r"^\s*\*\(undefined4 \*\)\(param_1 \+ (\d+)\) = "), None, 4),
]
CALL_RE = re.compile(r"^\s*(?:undefined\d? ?\*?|[a-z]+ )?([A-Za-z_][A-Za-z0-9_]*)\((.*)\);\s*$")
HELPER_AT_OFFSET_RE = re.compile(r"^\s*(?:undefined\d? ?)?([A-Za-z_][A-Za-z0-9_]*)\(.*,\s*param_1 \+ (\d+)\);\s*$")


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load_corpus() -> tuple[dict, dict[str, dict]]:
    metadata = None
    functions: dict[str, dict] = {}
    for number, line in enumerate(CORPUS.read_text(encoding="utf-8").splitlines(), 1):
        record = json.loads(line)
        if number == 1:
            metadata = record
        else:
            functions[record["entry_addr"]] = record
    return metadata, functions


def did_table_rows() -> list[dict]:
    rows = []
    for index in range(DID_ROWS):
        base = DID_TABLE + index * 16
        did, declared = struct.unpack_from("<HH", CF, base)
        callback, _aux, _tail = struct.unpack_from("<III", CF, base + 4)
        rows.append({"index": index, "did": did, "declared": declared, "callback": callback})
    return rows


def classify(callback: int, declared: int, record: dict) -> dict:
    """Classify one unique producer callback; exhaustive or it raises."""
    c = record["decompiled_c"]
    body = CF[callback : callback + record["body_size"]]
    entry: dict = {
        "callback": f"0x{callback:08x}",
        "body_size": record["body_size"],
        "body_sha256": sha256(body),
        "decompiled_c_sha256": record["decompiled_c_sha256"],
        "declared_len": declared,
        "class": None,
        "max_write_extent": None,
        "bound_source": None,
    }

    if body[:4] == SUCCESS_STUB and record["body_size"] == 4:
        entry.update({"class": "success_stub", "max_write_extent": 0,
                     "bound_source": "body is exactly `mov 0,r10; jmp lp` (00 52 7f 00): no destination write"})
        return entry

    pinned = PINNED_EXCEPTIONS.get(callback)
    if pinned is not None:
        for needle in pinned["c_bounds"]:
            if needle not in c:
                raise SystemExit(f"pinned bound {needle!r} missing from corpus C of {entry['callback']}")
        for raw in pinned["raw_pins"]:
            if raw not in body:
                raise SystemExit(f"raw pin {raw.hex()} missing from body of {entry['callback']}")
        extent = pinned["extent"] if pinned["extent"] is not None else declared
        entry.update({"class": pinned["class"], "max_write_extent": extent,
                     "bound_source": pinned["note"]})
        return entry

    max_off = 0
    engine = None
    leftover: list[str] = []
    lines = [line.rstrip() for line in c.splitlines()]
    signature = next((line for line in lines if line), "")
    for line in c.splitlines():
        if line == signature:
            continue
        hit = False
        for pattern, offset, width in DIRECT_WRITE_RES:
            match = pattern.match(line)
            if match:
                off = offset if offset is not None else int(match.group(1))
                max_off = max(max_off, off + width)
                hit = True
                break
        if hit:
            continue
        helper = HELPER_AT_OFFSET_RE.match(line)
        if helper and helper.group(1) in STORE_HELPERS:
            max_off = max(max_off, int(helper.group(2)) + STORE_HELPERS[helper.group(1)])
            continue
        match = CALL_RE.match(line)
        if match:
            name, args = match.groups()
            parts = [part.strip() for part in args.split(",")]
            if name in STORE_HELPERS and parts and parts[-1] == "param_1":
                max_off = max(max_off, STORE_HELPERS[name])
                continue
            if name in ENGINES and "param_1" in parts and parts[-1] in ("param_2",):
                engine = name
                continue
        if "param_1" in line:
            leftover.append(line.strip())

    if leftover:
        raise SystemExit(
            f"unclassified destination write in {entry['callback']} "
            f"(declared {declared}): {leftover!r}"
        )
    if engine is not None:
        bound_arg, internal = ENGINES[engine]
        entry.update({"class": "engine_declared_bounded", "max_write_extent": declared,
                     "bound_source": f"forwards (dest, declared_len) to {engine}; all writes bounded by "
                                  f"{bound_arg}: {internal}"})
        return entry
    if max_off == 0:
        raise SystemExit(f"{entry['callback']} has no recognized destination write at all")
    entry.update({"class": "direct_fixed", "max_write_extent": max_off,
                 "bound_source": "fixed-offset stores (incl. pinned 2/4-byte LE store helpers) only"})
    return entry


def main() -> int:
    metadata, functions = load_corpus()
    rows = did_table_rows()
    with_producer = [row for row in rows if row["callback"]]
    by_callback: dict[int, list[dict]] = {}
    for row in with_producer:
        by_callback.setdefault(row["callback"], []).append(row)

    if len(with_producer) != 242 or len(by_callback) != 196:
        raise SystemExit(f"DID-table census drifted: rows={len(with_producer)} unique={len(by_callback)}")

    entries = []
    for callback, uses in sorted(by_callback.items()):
        declared_lengths = {use["declared"] for use in uses}
        if len(declared_lengths) != 1:
            raise SystemExit(f"{callback:#x} serves multiple declared lengths {declared_lengths}")
        declared = declared_lengths.pop()
        record = functions.get(f"0x{callback:08x}")
        if record is None:
            raise SystemExit(f"callback {callback:#x} missing from decompiler corpus")
        if sha256(record["decompiled_c"].encode()) != record["decompiled_c_sha256"]:
            raise SystemExit(f"corpus C hash mismatch for {callback:#x}")
        entry = classify(callback, declared, record)
        entry["dids"] = [{"did": f"0x{use['did']:04X}", "declared": use["declared"]} for use in uses]
        entry["exceeds_declared"] = entry["max_write_extent"] > declared
        entry["write_relation"] = (
            "zero" if entry["max_write_extent"] == 0
            else ("exact_fit" if entry["max_write_extent"] == declared else "under")
        )
        entries.append(entry)

    exceeds = [entry for entry in entries if entry["exceeds_declared"]]
    classes: dict[str, int] = {}
    for entry in entries:
        classes[entry["class"]] = classes.get(entry["class"], 0) + 1
    under_nonzero = [
        entry for entry in entries
        if entry["write_relation"] == "under" and entry["class"] != "success_stub"
    ]

    payload = {
        "schema": "rdbi-emitted-write-audit/1",
        "scope": "Sienna EPS 8965B4512000 application image",
        "question": "can any configured RDBI producer callback write beyond the declared per-DID length it is handed?",
        "convention": {
            "dispatch": "0x4CB8A calls DID-table record+4 as callback(dest, declared_len)",
            "count_initialization": "0x8A374 writes the configured length word (DID record +2 via "
                                    "0x8A31E -> 0x4C81A) into the count slot BEFORE invoking the "
                                    "producer; the render loop 0x9429E advances by that slot, so the "
                                    "emitted count is configuration-owned, never producer-returned",
            "async_path": "pending path copies exactly the declared count bytes from a routine-owned "
                          "buffer through 0x8A32A (uStack_2e = count slot)",
            "pinned_bodies": {
                "0x0008a374": sha256(CF[0x8A374 : 0x8A374 + 270]),
                "0x0008a31e": sha256(CF[0x8A31E : 0x8A31E + 12]),
                "0x0004cb8a": sha256(CF[0x4CB8A : 0x4CB8A + 52]),
                "0x0004c81a": sha256(CF[0x4C81A : 0x4C81A + 42]),
                "0x0009429e": sha256(CF[0x9429E : 0x9429E + 392]),
            },
        },
        "did_table": {"base": "0x2941c", "rows": DID_ROWS, "rows_with_producer": len(with_producer),
                      "unique_producers": len(by_callback)},
        "summary": {
            "classified": len(entries),
            "exceeds_declared": len(exceeds),
            "classes": classes,
            "exact_fit": sum(1 for e in entries if e["write_relation"] == "exact_fit"),
            "under_nonzero": len(under_nonzero),
            "zero_write": sum(1 for e in entries if e["write_relation"] == "zero"),
            "max_declared": max(e["declared_len"] for e in entries),
            "max_extent": max(e["max_write_extent"] for e in entries),
        },
        "under_writers_non_stub": [
            {"callback": e["callback"], "extent": e["max_write_extent"], "declared": e["declared_len"],
             "dids": [d["did"] for d in e["dids"]]}
            for e in under_nonzero
        ],
        "exceptions": [
            {"callback": f"0x{callback:08x}", **spec, "raw_pins": [pin.hex() for pin in spec["raw_pins"]]}
            for callback, spec in sorted(PINNED_EXCEPTIONS.items())
        ],
        "callbacks": entries,
        "provenance": {
            "firmware": "firmware/RH850_P1M-E_CodeFlash.bin",
            "corpus": "data/generated/decompilations.jsonl",
            "corpus_function_count": metadata["function_count"],
            "corpus_executable_sha256": metadata["executable_sha256"],
            "corpus_inventory_sha256": metadata["project_inventory_sha256"],
        },
    }

    OUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(f"classified={len(entries)} exceeds={len(exceeds)} classes={classes}")
    print(f"exact_fit={payload['summary']['exact_fit']} under_nonzero={len(under_nonzero)} "
          f"zero={payload['summary']['zero_write']}")
    if under_nonzero:
        print("non-stub under-writers:", [e["callback"] for e in under_nonzero])
    print(f"wrote {OUT}")
    return 1 if exceeds else 0


if __name__ == "__main__":
    sys.exit(main())
