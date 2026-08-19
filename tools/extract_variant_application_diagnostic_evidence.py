#!/usr/bin/env python3
"""Extract a compact, image-bound decompiler evidence set for variant diagnostics.

This does not perform semantic classification itself. It selects only the
configured application RDBI producers, RoutineControl callbacks, and explicitly
requested helper/downstream functions from a target-native Ghidra decompiler
corpus. Every selected record is tied back to the raw CodeFlash bytes by body
SHA-256 so later deterministic analyses can reject stale/mismatched evidence.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import struct
from pathlib import Path

DID = struct.Struct("<HHIII")
RID_CB = struct.Struct("<HHII")


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def parse_int(value: str) -> int:
    return int(value, 0)


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--image", type=Path, required=True)
    p.add_argument("--corpus", type=Path, required=True)
    p.add_argument("--did-table", type=parse_int, required=True)
    p.add_argument("--did-count", type=int, required=True)
    p.add_argument("--routine-callback-table", type=parse_int, required=True)
    p.add_argument("--routine-count", type=int, default=19)
    p.add_argument("--extra", type=parse_int, action="append", default=[])
    p.add_argument("--software-id", required=True)
    p.add_argument("--out", type=Path, required=True)
    args = p.parse_args()

    image = args.image.read_bytes()
    if len(image) != 0x100000:
        raise SystemExit(f"expected 1 MiB CodeFlash, got {len(image):#x}")

    did_callbacks: set[int] = set()
    for i in range(args.did_count):
        _did, _length, callback, _aux, _tail = DID.unpack_from(
            image, args.did_table + i * DID.size
        )
        if callback:
            did_callbacks.add(callback)

    routine_callbacks: set[int] = set()
    for i in range(args.routine_count):
        _rid, _pad, precondition, action = RID_CB.unpack_from(
            image, args.routine_callback_table + i * RID_CB.size
        )
        if precondition:
            routine_callbacks.add(precondition)
        if action:
            routine_callbacks.add(action)

    selected = did_callbacks | routine_callbacks | set(args.extra)
    corpus_records: dict[int, dict] = {}
    for line in args.corpus.read_text(encoding="utf-8").splitlines():
        record = json.loads(line)
        entry = record.get("entry_addr")
        if entry is None:
            continue
        address = int(entry, 16)
        if address in selected:
            corpus_records[address] = record

    missing = sorted(selected - corpus_records.keys())
    if missing:
        raise SystemExit(
            "selected functions missing from decompiler corpus: "
            + ", ".join(f"0x{x:X}" for x in missing)
        )

    functions = []
    for address in sorted(selected):
        record = corpus_records[address]
        size = int(record["body_size"])
        body = image[address : address + size]
        if len(body) != size:
            raise SystemExit(f"function body outside CodeFlash: {address:#x}+{size:#x}")
        code = record.get("decompiled_c", "")
        if not record.get("decompile_completed", False) or not code:
            raise SystemExit(f"decompilation incomplete for {address:#x}")
        functions.append(
            {
                "entry": f"0x{address:08X}",
                "body_size": size,
                "body_sha256": sha256(body),
                "decompiled_c_sha256": sha256(code.encode("utf-8")),
                "decompiled_c": code,
                "selection_roles": sorted(
                    role
                    for role, members in (
                        ("rdbi_producer", did_callbacks),
                        ("routine_control_callback", routine_callbacks),
                        ("extra_helper_or_downstream", set(args.extra)),
                    )
                    if address in members
                ),
            }
        )

    payload = {
        "schema": "rh850-variant-application-diagnostic-decompiler-evidence-v1",
        "software_id": args.software_id,
        "image": {
            "path": str(args.image),
            "size": len(image),
            "sha256": sha256(image),
        },
        "source_corpus": {
            "path": str(args.corpus),
            "sha256": sha256(args.corpus.read_bytes()),
            "note": "Disposable target-native Ghidra corpus; path is provenance only and is not required by downstream deterministic checks.",
        },
        "tables": {
            "did_table": f"0x{args.did_table:X}",
            "did_count": args.did_count,
            "routine_callback_table": f"0x{args.routine_callback_table:X}",
            "routine_count": args.routine_count,
        },
        "selection": {
            "rdbi_producer_count": len(did_callbacks),
            "routine_control_callback_count": len(routine_callbacks),
            "extra_count": len(set(args.extra)),
            "function_count": len(functions),
        },
        "functions": functions,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        f"wrote {args.out}: {len(functions)} functions "
        f"({len(did_callbacks)} RDBI, {len(routine_callbacks)} RoutineControl, "
        f"{len(set(args.extra))} extras)"
    )


if __name__ == "__main__":
    main()
