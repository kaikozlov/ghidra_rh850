#!/usr/bin/env python3
"""Generate a provenance-locked whole-project Ghidra decompiler corpus."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[1]
BUILD_ROOT = Path(os.environ.get("BUILD_ROOT", REPO / "build")).expanduser().resolve()
BUILD_WORK = Path(os.environ.get("BUILD_WORK", BUILD_ROOT / "work")).expanduser().resolve()
BUILD_OUT = Path(os.environ.get("BUILD_OUT", BUILD_ROOT / "out")).expanduser().resolve()
BUILD_LOGS = Path(os.environ.get("BUILD_LOGS", BUILD_ROOT / "logs")).expanduser().resolve()
BUILD_TMP = Path(os.environ.get("BUILD_TMP", BUILD_ROOT / "tmp")).expanduser().resolve()
COMMITTED_PROJECT = REPO / "project"
PROJECT_NAME = "rh850_p1me_mapped"
PROGRAM_NAME = "RH850_P1M-E_CodeFlash.bin"
INVENTORY = REPO / "data/ghidra_project_inventory.baseline.jsonl"
DEFAULT_OUTPUT = REPO / "data/generated/decompilations.jsonl"
DEFAULT_VIEW = BUILD_OUT / "pseudocode"
EXPORTER = REPO / "ghidra/scripts/verify/ExportDecompilerCorpus.java"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def is_within(path: Path, parent: Path) -> bool:
    path = path.resolve()
    parent = parent.resolve()
    return path == parent or parent in path.parents


def normalize_c(code: str) -> str:
    return code.replace("\r\n", "\n").replace("\r", "\n")


def run_checked(command: list[str], *, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    completed = subprocess.run(
        command,
        cwd=REPO,
        env=env,
        capture_output=True,
        text=True,
    )
    if completed.returncode:
        rendered = " ".join(command)
        raise SystemExit(
            f"command failed ({completed.returncode}): {rendered}\n"
            f"--- stdout ---\n{completed.stdout}\n--- stderr ---\n{completed.stderr}"
        )
    return completed


def load_inventory(path: Path) -> tuple[dict[str, Any], dict[str, dict[str, Any]], dict[str, Any]]:
    metadata: dict[str, Any] | None = None
    functions: dict[str, dict[str, Any]] = {}
    totals: dict[str, Any] | None = None
    for line in path.read_text(encoding="utf-8").splitlines():
        record = json.loads(line)
        kind = record["record"]
        if kind == "meta":
            metadata = record
        elif kind == "function":
            offset = int(record["entry"]["offset"], 16)
            entry = f"0x{offset:08x}"
            if entry in functions:
                raise SystemExit(f"duplicate inventory function address: {entry}")
            functions[entry] = record
        elif kind == "totals":
            totals = record
    if metadata is None or totals is None:
        raise SystemExit(f"inventory is missing meta/totals records: {path}")
    if totals["functions"] != len(functions):
        raise SystemExit(
            f"inventory function count mismatch: totals={totals['functions']} parsed={len(functions)}"
        )
    return metadata, functions, totals


def validate_project(project_dir: Path) -> Path:
    project_dir = project_dir.expanduser().resolve()
    committed = COMMITTED_PROJECT.resolve()
    if project_dir == committed or committed in project_dir.parents:
        raise SystemExit(f"refusing committed project: {project_dir}")
    if not (project_dir / f"{PROJECT_NAME}.rep").is_dir():
        raise SystemExit(
            f"missing working project: {project_dir / (PROJECT_NAME + '.rep')}\n"
            "run 'make work-project' or build a disposable project first"
        )
    return project_dir


def verify_live_inventory(project_dir: Path, environment: dict[str, str], temp_dir: Path) -> None:
    live_inventory = temp_dir / "live-project.jsonl"
    inventory_env = environment.copy()
    inventory_env["PROJECT_DIR"] = str(project_dir)
    run_checked([str(REPO / "tools/generate_project_inventory.sh"), str(live_inventory)], env=inventory_env)
    run_checked([
        sys.executable,
        str(REPO / "tools/project_inventory.py"),
        "compare",
        str(INVENTORY),
        str(live_inventory),
    ])


def export_raw_corpus(
    project_dir: Path,
    raw_output: Path,
    timeout_seconds: int,
    environment: dict[str, str],
) -> None:
    log = BUILD_LOGS / "generate-decompiler-corpus.log"
    log.parent.mkdir(parents=True, exist_ok=True)
    run_checked([
        str(REPO / "tools/run_headless"),
        "--project-dir", str(project_dir),
        "--project", PROJECT_NAME,
        "--label", "decompiler-corpus",
        "--log", str(log),
        "--quiet",
        "--",
        "-process", PROGRAM_NAME,
        "-noanalysis",
        "-readOnly",
        "-postScript", EXPORTER.name, str(raw_output), str(timeout_seconds),
    ], env=environment)
    if not raw_output.is_file():
        raise SystemExit(f"decompiler exporter produced no output: {raw_output}")
    log_text = log.read_text(encoding="utf-8", errors="replace")
    if "ExportDecompilerCorpus: wrote " not in log_text:
        raise SystemExit(f"decompiler exporter did not report success; see {log}")


def canonicalize_records(
    raw_output: Path,
    inventory_functions: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    seen: set[str] = set()
    failures: list[str] = []
    identity_errors: list[str] = []

    for line_number, line in enumerate(raw_output.read_text(encoding="utf-8").splitlines(), 1):
        raw = json.loads(line)
        entry = raw.get("entry_addr")
        if not isinstance(entry, str) or entry not in inventory_functions:
            identity_errors.append(f"line {line_number}: unexpected entry {entry!r}")
            continue
        if entry in seen:
            identity_errors.append(f"line {line_number}: duplicate entry {entry}")
            continue
        seen.add(entry)

        expected = inventory_functions[entry]
        if raw.get("record") != "function":
            identity_errors.append(f"{entry}: record kind {raw.get('record')!r}")
        if raw.get("address_space") != expected["entry"]["space"]:
            identity_errors.append(
                f"{entry}: address space {raw.get('address_space')!r} != {expected['entry']['space']!r}"
            )
        if raw.get("body_size") != expected["body_address_count"]:
            identity_errors.append(
                f"{entry}: body size {raw.get('body_size')!r} != {expected['body_address_count']}"
            )
        if raw.get("is_thunk") != expected["is_thunk"]:
            identity_errors.append(f"{entry}: thunk identity changed")
        if raw.get("calling_convention") != expected["calling_convention"]:
            identity_errors.append(
                f"{entry}: calling convention {raw.get('calling_convention')!r} "
                f"!= {expected['calling_convention']!r}"
            )
        if expected["user_name"] is not None and raw.get("name") != expected["user_name"]:
            identity_errors.append(
                f"{entry}: user name {raw.get('name')!r} != {expected['user_name']!r}"
            )

        completed = raw.get("decompile_completed") is True
        code = normalize_c(str(raw.get("decompiled_c", "")))
        error = str(raw.get("decompile_error", ""))
        if not completed or not code.strip():
            failures.append(f"{entry} {raw.get('name', '')}: {error or 'empty decompilation'}")

        raw_refs = raw.get("data_references", [])
        if not isinstance(raw_refs, list):
            identity_errors.append(f"{entry}: data_references is not a list")
            raw_refs = []
        data_references: list[dict[str, Any]] = []
        for ref_index, ref in enumerate(raw_refs):
            if not isinstance(ref, dict):
                identity_errors.append(f"{entry}: data reference {ref_index} is not an object")
                continue
            try:
                from_addr = f"0x{int(str(ref['from_addr']), 16):08x}"
                to_addr = f"0x{int(str(ref['to_addr']), 16):08x}"
                operand_index = int(ref["operand_index"])
                to_space = str(ref["to_space"])
                ref_type = str(ref["ref_type"])
            except (KeyError, TypeError, ValueError) as exc:
                identity_errors.append(f"{entry}: invalid data reference {ref_index}: {exc}")
                continue
            if not to_space or not ref_type:
                identity_errors.append(f"{entry}: empty data-reference identity at {ref_index}")
                continue
            data_references.append({
                "from_addr": from_addr,
                "to_addr": to_addr,
                "to_space": to_space,
                "ref_type": ref_type,
                "operand_index": operand_index,
            })
        data_references.sort(key=lambda ref: (
            int(ref["from_addr"], 16), int(ref["to_addr"], 16),
            ref["to_space"], ref["ref_type"], ref["operand_index"],
        ))

        records.append({
            "record": "function",
            "entry_addr": entry,
            "address_space": raw.get("address_space", ""),
            "name": raw.get("name", ""),
            "signature": raw.get("signature"),
            "calling_convention": raw.get("calling_convention", ""),
            "body_size": raw.get("body_size"),
            "is_thunk": raw.get("is_thunk"),
            "decompile_completed": completed,
            "decompile_error": error,
            "data_references": data_references,
            "decompiled_c_sha256": hashlib.sha256(code.encode()).hexdigest(),
            "decompiled_c": code,
        })

    missing = sorted(set(inventory_functions) - seen)
    if missing:
        identity_errors.append(f"missing {len(missing)} inventory functions: {missing[:8]!r}")
    if identity_errors:
        raise SystemExit("decompiler corpus identity validation failed:\n  " + "\n  ".join(identity_errors[:20]))
    if failures:
        raise SystemExit(
            f"{len(failures)} functions failed to decompile; corpus was not updated:\n  "
            + "\n  ".join(failures[:20])
        )
    records.sort(key=lambda record: int(record["entry_addr"], 16))
    return records


def write_corpus(
    output: Path,
    records: list[dict[str, Any]],
    inventory_meta: dict[str, Any],
    inventory_totals: dict[str, Any],
    timeout_seconds: int,
) -> dict[str, Any]:
    metadata = {
        "record": "metadata",
        "schema_version": 2,
        "function_count": len(records),
        "decompiled_count": sum(record["decompile_completed"] for record in records),
        "failed_count": sum(not record["decompile_completed"] for record in records),
        "decompiler_timeout_seconds": timeout_seconds,
        "project_inventory_path": INVENTORY.relative_to(REPO).as_posix(),
        "project_inventory_sha256": sha256(INVENTORY),
        "generator_path": Path(__file__).resolve().relative_to(REPO).as_posix(),
        "generator_sha256": sha256(Path(__file__).resolve()),
        "exporter_path": EXPORTER.relative_to(REPO).as_posix(),
        "exporter_sha256": sha256(EXPORTER),
        "ghidra_version": inventory_meta["ghidra_version"],
        "program_name": inventory_meta["program_name"],
        "executable_sha256": inventory_meta["executable_sha256"],
        "language_id": inventory_meta["language_id"],
        "compiler_spec_id": inventory_meta["compiler_spec_id"],
        "inventory_function_count": inventory_totals["functions"],
    }
    output = output.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        mode="w",
        encoding="utf-8",
        newline="\n",
        dir=output.parent,
        prefix=f".{output.name}.",
        delete=False,
    ) as stream:
        temporary = Path(stream.name)
        for record in (metadata, *records):
            stream.write(json.dumps(record, sort_keys=True, separators=(",", ":")) + "\n")
    temporary.replace(output)
    output.chmod(0o644)
    return metadata


def safe_name(name: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9_.-]+", "_", name).strip("._")
    return (slug or "function")[:96]


def materialize_view(view_dir: Path, records: list[dict[str, Any]], metadata: dict[str, Any]) -> None:
    view_dir = view_dir.expanduser().resolve()
    if not is_within(view_dir, BUILD_OUT) or view_dir == BUILD_OUT.resolve():
        raise SystemExit(f"refusing pseudocode view outside build/out/: {view_dir}")

    parent = view_dir.parent
    parent.mkdir(parents=True, exist_ok=True)
    temporary = Path(tempfile.mkdtemp(prefix=f".{view_dir.name}.", dir=parent))
    try:
        index_lines = ["entry_addr\tname\tsignature\tpath\tdecompiled_c_sha256"]
        for record in records:
            entry_hex = record["entry_addr"][2:]
            filename = f"{entry_hex}_{safe_name(str(record['name']))}.c"
            path = temporary / filename
            header = (
                "/* Generated decompiler view; do not edit.\n"
                f" * entry: {record['entry_addr']}\n"
                f" * name: {record['name']}\n"
                f" * signature: {record['signature'] or ''}\n"
                f" * calling_convention: {record['calling_convention']}\n"
                f" * project_inventory_sha256: {metadata['project_inventory_sha256']}\n"
                f" * data_reference_count: {len(record.get('data_references', []))}\n"
                f" * decompiled_c_sha256: {record['decompiled_c_sha256']}\n"
                " */\n\n"
            )
            code = record["decompiled_c"]
            path.write_text(header + code + ("" if code.endswith("\n") else "\n"), encoding="utf-8")
            index_lines.append(
                "\t".join([
                    record["entry_addr"],
                    str(record["name"]),
                    str(record["signature"] or ""),
                    filename,
                    record["decompiled_c_sha256"],
                ])
            )
        (temporary / "index.tsv").write_text("\n".join(index_lines) + "\n", encoding="utf-8")
        if view_dir.exists():
            shutil.rmtree(view_dir)
        temporary.replace(view_dir)
    except BaseException:
        shutil.rmtree(temporary, ignore_errors=True)
        raise


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-dir", type=Path, default=BUILD_WORK / "project")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--view-dir", type=Path, default=DEFAULT_VIEW)
    parser.add_argument("--no-view", action="store_true")
    parser.add_argument(
        "--timeout-seconds",
        type=int,
        default=60,
        help="per-function Ghidra decompiler timeout; 0 means no timeout (default: 60)",
    )
    args = parser.parse_args()
    if args.timeout_seconds < 0:
        parser.error("--timeout-seconds must be >= 0")

    project_dir = validate_project(args.project_dir)
    environment = os.environ.copy()
    environment["GHIDRA_PROJECT"] = str(project_dir)

    # A daemon cannot safely share the project with a read-only headless export.
    # Stop only the selected working project's daemon, then prove that this live
    # project is exactly the committed canonical inventory before attribution.
    run_checked([str(REPO / "tools/g"), "stop"], env=environment)

    inventory_meta, inventory_functions, inventory_totals = load_inventory(INVENTORY)
    BUILD_TMP.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="decompiler-corpus-", dir=BUILD_TMP) as temp_name:
        temp_dir = Path(temp_name)
        verify_live_inventory(project_dir, environment, temp_dir)
        raw_output = temp_dir / "raw-decompilations.jsonl"
        export_raw_corpus(project_dir, raw_output, args.timeout_seconds, environment)
        records = canonicalize_records(raw_output, inventory_functions)

    metadata = write_corpus(
        args.output,
        records,
        inventory_meta,
        inventory_totals,
        args.timeout_seconds,
    )
    if not args.no_view:
        materialize_view(args.view_dir, records, metadata)

    print(
        f"Wrote {len(records)} decompilations to {args.output.resolve()} "
        f"(inventory {metadata['project_inventory_sha256'][:12]}...)"
    )
    if not args.no_view:
        print(f"Materialized searchable pseudocode view: {args.view_dir.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
