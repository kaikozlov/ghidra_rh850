#!/usr/bin/env python3
"""Image-bound variant evidence and BSim family queries.

The compact evidence modes bind records from target-native exports to CodeFlash
bytes. ``bsim`` queries a registered target against named database scopes and
records one best match or miss per function and scope.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import struct
import subprocess
import tempfile
from collections.abc import Iterator
from pathlib import Path
from typing import Any

from tools import REPO_ROOT
from tools.project.analysis_target import load as load_targets
from tools.project.project_layout import materialize

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
    "bsim": {
        "summary": "best BSim match per function and target/reference scope",
        "input": "registered target working project plus regenerable H2 BSim database",
        "selection": "all BSim-signable functions; server-side MD5/path scopes",
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
        # Preserve the retired extractors' strict JSONL contract:
        # treat every blank line as malformed input.
        yield json.loads(line)


def write_payload(out: Path, payload: dict[str, Any]) -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def run_structural(args: argparse.Namespace) -> None:
    root = REPO_ROOT
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
    root = REPO_ROOT
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
    root = REPO_ROOT
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

EPS_TARGETS = (
    "camry-8965F3307000",
    "sienna-8965B4512000",
    "crown-8965F3012000",
    "corolla-8965F1208000",
    "corolla-8965H1202000",
)


def _md5(path: Path) -> str:
    digest = hashlib.md5(usedforsecurity=False)
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _bsim_url(path: Path) -> str:
    resolved = path.resolve()
    if resolved.name.endswith(".mv.db"):
        resolved = resolved.with_name(resolved.name.removesuffix(".mv.db"))
    database_file = resolved.with_name(resolved.name + ".mv.db")
    if not database_file.is_file():
        raise SystemExit(f"BSim database not found: {database_file}")
    return f"file:{resolved}"


def _iter_bsim_rows(path: Path) -> Iterator[dict[str, Any]]:
    with path.open(encoding="utf-8") as stream:
        for line in stream:
            if line.strip():
                yield json.loads(line)


def _apply_bsim_matches(
    args: argparse.Namespace, output: Path, targets: dict[str, dict[str, Any]]
) -> int:
    if args.target != "sienna-8965B4512000":
        raise SystemExit("calibrated BSim application is available only for the Sienna query")
    artifact = REPO_ROOT / "data/generated/sienna_8965B4512000_bsim_calibrated_transfer.json"
    evidence = json.loads(artifact.read_text())
    minimum_similarity = evidence["similarity_threshold"]
    minimum_instructions = evidence["minimum_instruction_count"]
    if args.similarity < minimum_similarity or args.instruction_floor < minimum_instructions:
        raise SystemExit(
            "cannot apply below the calibrated operating point "
            f"(similarity {minimum_similarity}, at least {minimum_instructions} instructions)"
        )
    approved: dict[tuple[str, str, str], str] = {}
    for target, target_evidence in evidence["targets"].items():
        for match in target_evidence["applied_names"]:
            approved[
                (target, match["source_address"], match["target_address"])
            ] = match["source_name"]

    grouped: dict[Path, dict[int, str]] = {}
    for row in _iter_bsim_rows(output):
        key = (row.get("scope"), row.get("source_address"), row.get("target_address"))
        if (
            row.get("record") == "match"
            and row.get("matched")
            and row["similarity"] >= args.similarity
            and row.get("source_instruction_count", 0) >= args.instruction_floor
            and key in approved
        ):
            seed_path = REPO_ROOT / targets[row["scope"]]["function_seeds"]
            grouped.setdefault(seed_path, {})[int(row["target_address"], 16)] = approved[key]

    provenance = artifact.relative_to(REPO_ROOT).as_posix()
    additions = 0
    for path, names in grouped.items():
        with path.open(newline="", encoding="utf-8") as stream:
            records = list(csv.reader(stream))
        existing = {int(record[0], 16) for record in records[1:]}
        with path.open("a", newline="", encoding="utf-8") as stream:
            writer = csv.writer(stream, lineterminator="\n")
            for address in sorted(names.keys() - existing):
                writer.writerow(
                    (
                        f"0x{address:08X}",
                        provenance,
                        f"name={names[address]}; exact mnemonic and instruction-length "
                        "sequence at calibrated BSim operating point",
                    )
                )
                additions += 1
    return additions


def run_bsim(args: argparse.Namespace) -> None:
    registry = load_targets()
    targets = registry["targets"]
    if args.target not in EPS_TARGETS:
        raise SystemExit(f"BSim target must be one of: {', '.join(EPS_TARGETS)}")
    if args.references_only:
        if args.against or not args.reference_set:
            raise SystemExit("--references-only requires --reference-set and no --against")
        against: list[str] = []
    else:
        against = args.against or [name for name in EPS_TARGETS if name != args.target]
    unknown = sorted(set(against) - set(EPS_TARGETS))
    if unknown:
        raise SystemExit(f"unknown EPS comparison target(s): {', '.join(unknown)}")
    if args.target in against:
        raise SystemExit("the query target cannot also be an --against target")

    scopes: list[str] = []
    for name in against:
        image = REPO_ROOT / targets[name]["codeflash"]
        scopes.append(f"{name}=md5:{_md5(image)}")
    for reference_set in args.reference_set or ("ccrh", "gcc"):
        scopes.append(f"{reference_set}=path:{reference_set}")

    output = (
        args.out
        or REPO_ROOT / "build/out/variants/bsim" / f"{args.target}.jsonl"
    ).resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.unlink(missing_ok=True)
    log = REPO_ROOT / "build/logs/bsim" / f"{args.target}-query.log"
    log.parent.mkdir(parents=True, exist_ok=True)
    row = targets[args.target]
    work_root = REPO_ROOT / "build/work"
    work_root.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(
        prefix=f"bsim-query-{args.target}-", dir=work_root
    ) as temporary:
        project_dir = Path(temporary)
        materialize(
            REPO_ROOT / row["snapshot_dir"], project_dir, row["project_name"]
        )
        command = [
            str(REPO_ROOT / "tools/project/run_headless"),
            "--project-dir",
            str(project_dir),
            "--project",
            row["project_name"],
            "--log",
            str(log),
            "--quiet",
            "--",
            "-process",
            row["program_name"],
            "-noanalysis",
            "-readOnly",
            "-postScript",
            "QueryBSimMatches.java",
            _bsim_url(args.database),
            str(output),
            str(args.similarity),
            str(args.confidence),
            str(args.max_matches),
            *scopes,
        ]
        completed = subprocess.run(command, cwd=REPO_ROOT, text=True, check=False)
        if completed.returncode:
            raise SystemExit(completed.returncode)
    if not output.is_file():
        raise SystemExit(f"BSim query did not produce function rows: {output}")

    counts = {scope.split("=", 1)[0]: 0 for scope in scopes}
    has_function_rows = False
    for row in _iter_bsim_rows(output):
        if row.get("record") != "match":
            continue
        has_function_rows = True
        if not row["matched"]:
            continue
        counts[row["scope"]] += 1
        print(
            "\t".join(
                (
                    row["source_address"],
                    row["source_name"],
                    str(row.get("source_instruction_count", 0)),
                    row["scope"],
                    row["target_name"],
                    row["target_address"],
                    f"{row['similarity']:.6f}",
                    f"{row['confidence']:.6f}",
                )
            )
        )
    if not has_function_rows:
        raise SystemExit(f"BSim query did not produce function rows: {output}")
    print(f"wrote {output}")
    print("matches: " + ", ".join(f"{scope}={count}" for scope, count in counts.items()))
    if args.apply:
        additions = _apply_bsim_matches(args, output, targets)
        print(f"seed application: added {additions} function entries")
    else:
        print("query only; use --apply to add reviewed matches to the seed CSVs")


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

    bsim = subparsers.add_parser("bsim", help=MODES["bsim"]["summary"])
    bsim.add_argument("target", choices=EPS_TARGETS)
    bsim.add_argument(
        "--database",
        type=Path,
        default=REPO_ROOT / "build/cache/bsim-family/toyota-eps-family",
    )
    bsim.add_argument(
        "--against",
        action="append",
        default=[],
        metavar="TARGET",
        help="comparison target (repeatable; default: every other EPS target)",
    )
    bsim.add_argument(
        "--references-only",
        action="store_true",
        help="query only explicit --reference-set scopes",
    )
    bsim.add_argument(
        "--reference-set",
        action="append",
        choices=("ccrh", "gcc"),
        default=[],
        help="compiler-runtime project path to query (repeatable)",
    )
    bsim.add_argument("--similarity", type=float, default=1.0)
    bsim.add_argument("--confidence", type=float, default=0.0)
    bsim.add_argument("--instruction-floor", type=int, default=101)
    bsim.add_argument("--max-matches", type=int, default=1)
    bsim.add_argument("--out", type=Path)
    bsim.add_argument(
        "--apply",
        action="store_true",
        help="apply reviewed candidates at the calibrated operating point",
    )
    bsim.set_defaults(run=run_bsim)

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
