#!/usr/bin/env python3
"""Compact image-bound evidence from disposable variant corpora.

Subcommands here replace the former one-file-per-selection extractors. The four
modes share exactly one abstraction: read a disposable target-native JSONL
corpus, select function records, bind each selected record to raw CodeFlash
bytes with SHA-256, and write the mode's existing tracked JSON schema. They
differ only in *how* records are selected (explicit addresses, callback-table
resolution, or whole-corpus substring census). Modes that would need dynamic
target discovery or semantic joins stay in their own tools.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import struct
from pathlib import Path
from typing import Any, Iterator

DID = struct.Struct("<HHIII")
RID_CB = struct.Struct("<HHII")

MODES: dict[str, dict[str, Any]] = {
    "structural": {
        "summary": "raw-image-bound structural fingerprints for explicitly listed functions",
        "input": "disposable structural-fingerprint export (JSONL)",
        "selection": "explicit --address list",
    },
    "function": {
        "summary": "target-native decompilation evidence for explicitly listed functions",
        "input": "disposable target-native Ghidra corpus (JSONL)",
        "selection": "explicit --address list",
    },
    "application-diagnostics": {
        "summary": "decompilation evidence for application RDBI producers, RoutineControl callbacks, and helpers",
        "input": "disposable target-native Ghidra corpus (JSONL)",
        "selection": "DID/routine callback tables read from the image plus explicit --extra addresses",
    },
    "reference-census": {
        "summary": "complete exact-substring direct-reference census over a corpus",
        "input": "disposable target-native Ghidra corpus (JSONL)",
        "selection": "whole-corpus --term NAME=SUBSTRING census",
    },
}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def parse_int(value: str) -> int:
    return int(value, 0)


def display_path(path: Path, root: Path) -> str:
    try:
        return str(path.resolve().relative_to(root.resolve()))
    except ValueError:
        return str(path)


def load_codeflash(image: Path, *, description: str = "CodeFlash") -> bytes:
    data = image.read_bytes()
    if len(data) != 0x100000:
        raise SystemExit(f"expected 1 MiB {description}, got {len(data):#x}")
    return data


def iter_corpus(path: Path) -> Iterator[dict[str, Any]]:
    for line in path.read_text(encoding="utf-8").splitlines():
        # Preserve the retired extractors' strict JSONL contract: a blank line
        # is malformed input, not whitespace to silently ignore.
        yield json.loads(line)


def write_payload(out: Path, payload: dict[str, Any]) -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def run_structural(args: argparse.Namespace) -> None:
    root = Path(__file__).resolve().parents[1]
    image = load_codeflash(args.image, description="image")
    want = set(args.address)
    rows: dict[int, dict[str, Any]] = {}
    for record in iter_corpus(args.fingerprints):
        entry = int(record["entry_addr"], 16)
        if entry in want:
            rows[entry] = record
    missing = sorted(want - rows.keys())
    if missing:
        raise SystemExit("missing fingerprints: " + ", ".join(hex(x) for x in missing))
    out = []
    keep = ["body_size", "instruction_count", "mnemonics", "instruction_lengths", "conditional_branch_count", "unconditional_branch_count", "direct_call_target_count", "indirect_call_count", "return_count"]
    for entry in sorted(want):
        record = rows[entry]
        size = record["body_size"]
        body = image[entry:entry + size]
        if len(body) != size:
            raise SystemExit(f"body outside image {entry:#x}")
        row: dict[str, Any] = {"entry": f"0x{entry:08X}", "body_sha256": sha256(body)}
        for key in keep:
            row[key] = record[key]
        out.append(row)
    payload = {
        "schema": "rh850-variant-structural-evidence-v1",
        "software_id": args.software_id,
        "image": {"path": display_path(args.image, root), "size": len(image), "sha256": sha256(image)},
        "source_fingerprints": {
            "path": display_path(args.fingerprints, root),
            "sha256": sha256(args.fingerprints.read_bytes()),
            "note": "Disposable Ghidra export; provenance only.",
        },
        "function_count": len(out),
        "functions": out,
    }
    write_payload(args.out, payload)
    print(f"wrote {args.out}: {len(out)} functions")


def run_function(args: argparse.Namespace) -> None:
    root = Path(__file__).resolve().parents[1]
    image = load_codeflash(args.image)
    wanted = set(args.address)
    if not wanted:
        raise SystemExit("at least one --address is required")

    selected: dict[int, dict[str, Any]] = {}
    for record in iter_corpus(args.corpus):
        raw_entry = record.get("entry_addr")
        if raw_entry is None:
            continue
        entry = int(raw_entry, 16)
        if entry in wanted:
            selected[entry] = record

    missing = sorted(wanted - selected.keys())
    if missing:
        raise SystemExit("missing selected functions: " + ", ".join(f"0x{x:X}" for x in missing))

    functions = []
    for entry in sorted(wanted):
        record = selected[entry]
        size = int(record["body_size"])
        code = record.get("decompiled_c", "")
        if not record.get("decompile_completed", False) or not code:
            raise SystemExit(f"incomplete target-native decompilation at {entry:#x}")
        body = image[entry:entry + size]
        if len(body) != size:
            raise SystemExit(f"function outside CodeFlash: {entry:#x}+{size:#x}")
        functions.append({
            "entry": f"0x{entry:08X}",
            "body_size": size,
            "body_sha256": sha256(body),
            "decompiled_c_sha256": sha256(code.encode("utf-8")),
            "decompiled_c": code,
        })

    payload = {
        "schema": "rh850-variant-function-decompiler-evidence-v1",
        "software_id": args.software_id,
        "image": {
            "path": display_path(args.image, root),
            "size": len(image),
            "sha256": sha256(image),
        },
        "source_corpus": {
            "path": display_path(args.corpus, root),
            "sha256": sha256(args.corpus.read_bytes()),
            "note": "Disposable target-native Ghidra corpus; provenance only. Downstream checks use the compact image-bound records.",
        },
        "function_count": len(functions),
        "functions": functions,
    }
    write_payload(args.out, payload)
    print(f"wrote {args.out}: {len(functions)} functions")


def run_application_diagnostics(args: argparse.Namespace) -> None:
    image = load_codeflash(args.image)

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
    corpus_records: dict[int, dict[str, Any]] = {}
    for record in iter_corpus(args.corpus):
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
        body = image[address:address + size]
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
    write_payload(args.out, payload)
    print(
        f"wrote {args.out}: {len(functions)} functions "
        f"({len(did_callbacks)} RDBI, {len(routine_callbacks)} RoutineControl, "
        f"{len(set(args.extra))} extras)"
    )


def run_reference_census(args: argparse.Namespace) -> None:
    root = Path(__file__).resolve().parents[1]
    image = load_codeflash(args.image)
    terms: dict[str, str] = {}
    for item in args.term:
        if "=" not in item:
            raise SystemExit(f"bad --term {item!r}; expected NAME=SUBSTRING")
        name, value = item.split("=", 1)
        if not name or not value or name in terms:
            raise SystemExit(f"bad/duplicate --term {item!r}")
        terms[name] = value.lower()
    if not terms:
        raise SystemExit("at least one --term is required")

    matches: dict[str, list[dict[str, Any]]] = {name: [] for name in terms}
    for record in iter_corpus(args.corpus):
        entry_raw = record.get("entry_addr")
        code = record.get("decompiled_c", "")
        if entry_raw is None or not code:
            continue
        entry = int(entry_raw, 16)
        size = int(record["body_size"])
        body = image[entry:entry + size]
        if len(body) != size:
            raise SystemExit(f"function body outside image: {entry:#x}+{size:#x}")
        code_lines = code.splitlines()
        for name, needle in terms.items():
            hit_lines = [text.strip() for text in code_lines if needle in text.lower()]
            if hit_lines:
                matches[name].append({
                    "entry": f"0x{entry:08X}",
                    "body_size": size,
                    "body_sha256": sha256(body),
                    "matching_lines": hit_lines,
                })

    payload = {
        "schema": "rh850-variant-decompiler-direct-reference-census-v1",
        "evidence_boundary": "Complete exact-substring census over the supplied target-native decompiler corpus; bounded to direct textual references and does not exclude computed-pointer or alias-only accesses.",
        "software_id": args.software_id,
        "image": {
            "path": display_path(args.image, root),
            "size": len(image),
            "sha256": sha256(image),
        },
        "source_corpus": {
            "path": display_path(args.corpus, root),
            "sha256": sha256(args.corpus.read_bytes()),
        },
        "terms": {
            name: {"substring": value, "match_count": len(matches[name]), "matches": matches[name]}
            for name, value in terms.items()
        },
    }
    write_payload(args.out, payload)
    print(f"wrote {args.out}: {len(terms)} terms")
    for name in terms:
        print(f"  {name}: {len(matches[name])} functions")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="mode", required=True)

    subparsers.add_parser("list", help="list available evidence modes as JSON")

    structural = subparsers.add_parser(
        "structural", help=MODES["structural"]["summary"]
    )
    structural.add_argument("--image", type=Path, required=True)
    structural.add_argument("--fingerprints", type=Path, required=True)
    structural.add_argument("--software-id", required=True)
    structural.add_argument("--address", type=parse_int, action="append", default=[])
    structural.add_argument("--out", type=Path, required=True)
    structural.set_defaults(run=run_structural)

    function = subparsers.add_parser("function", help=MODES["function"]["summary"])
    function.add_argument("--image", type=Path, required=True)
    function.add_argument("--corpus", type=Path, required=True)
    function.add_argument("--software-id", required=True)
    function.add_argument("--address", type=parse_int, action="append", default=[])
    function.add_argument("--out", type=Path, required=True)
    function.set_defaults(run=run_function)

    diagnostics = subparsers.add_parser(
        "application-diagnostics", help=MODES["application-diagnostics"]["summary"]
    )
    diagnostics.add_argument("--image", type=Path, required=True)
    diagnostics.add_argument("--corpus", type=Path, required=True)
    diagnostics.add_argument("--did-table", type=parse_int, required=True)
    diagnostics.add_argument("--did-count", type=int, required=True)
    diagnostics.add_argument("--routine-callback-table", type=parse_int, required=True)
    diagnostics.add_argument("--routine-count", type=int, default=19)
    diagnostics.add_argument("--extra", type=parse_int, action="append", default=[])
    diagnostics.add_argument("--software-id", required=True)
    diagnostics.add_argument("--out", type=Path, required=True)
    diagnostics.set_defaults(run=run_application_diagnostics)

    census = subparsers.add_parser(
        "reference-census", help=MODES["reference-census"]["summary"]
    )
    census.add_argument("--image", type=Path, required=True)
    census.add_argument("--corpus", type=Path, required=True)
    census.add_argument("--software-id", required=True)
    census.add_argument("--term", action="append", default=[], metavar="NAME=SUBSTRING")
    census.add_argument("--out", type=Path, required=True)
    census.set_defaults(run=run_reference_census)

    return parser


def main() -> int:
    args = build_parser().parse_args()
    if args.mode == "list":
        print(json.dumps(MODES, indent=2, sort_keys=True))
        return 0
    args.run(args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
