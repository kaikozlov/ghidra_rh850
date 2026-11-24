#!/usr/bin/env python3
"""Browse the persistent whole-image Ghidra pseudocode corpus."""
from __future__ import annotations

import argparse
from bisect import bisect_right
from collections import defaultdict
from functools import cached_property
import hashlib
import json
import re
import shlex
import sys
from pathlib import Path
from typing import Any

from tools import REPO_ROOT
from tools.project import analysis_target
from tools.project.generate_decompiler_corpus import (
    DEFAULT_VIEW,
    VIEW_INDEX_HEADER,
    materialize_view,
    render_view_file,
)

ROOT = REPO_ROOT


def load_corpus(path: Path) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    try:
        stream = path.open(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"missing pseudocode corpus: {path}") from exc
    except OSError as exc:
        raise SystemExit(f"cannot open pseudocode corpus {path}: {exc.strerror}") from exc
    metadata: dict[str, Any] | None = None
    functions: list[dict[str, Any]] = []
    with stream:
        for line_number, line in enumerate(stream, 1):
            try:
                record = json.loads(line)
            except ValueError as exc:
                raise SystemExit(f"invalid JSON in pseudocode corpus {path}:{line_number}: {exc}") from exc
            if not isinstance(record, dict):
                raise SystemExit(f"invalid corpus record at {path}:{line_number}")
            if line_number == 1:
                if record.get("record") != "metadata":
                    raise SystemExit(f"invalid corpus metadata record in {path}")
                metadata = record
            else:
                if record.get("record") != "function":
                    raise SystemExit(f"invalid function record at {path}:{line_number}")
                functions.append(record)
    if metadata is None:
        raise SystemExit(f"empty pseudocode corpus: {path}")
    return metadata, functions


def normalize_address(query: str) -> str | None:
    value = query.strip().lower()
    try:
        if value.startswith("0x"):
            return f"0x{int(value, 16):08x}"
        if value and all(ch in "0123456789abcdef" for ch in value) and any(ch.isdigit() for ch in value):
            return f"0x{int(value, 16):08x}"
    except ValueError:
        pass
    return None


def load_function_body_ranges(
    inventory_path: Path, corpus_metadata: dict[str, Any]
) -> dict[str, list[tuple[int, int]]]:
    try:
        contents = inventory_path.read_bytes()
    except FileNotFoundError as exc:
        raise SystemExit(
            f"missing project inventory: {inventory_path}\n"
            "the pinned inventory is required to resolve interior function addresses"
        ) from exc
    except OSError as exc:
        raise SystemExit(
            f"cannot read project inventory {inventory_path}: {exc.strerror}\n"
            "the pinned inventory is required to resolve interior function addresses"
        ) from exc
    expected_sha = corpus_metadata.get("project_inventory_sha256")
    if not isinstance(expected_sha, str) or not expected_sha:
        raise SystemExit(
            "pseudocode corpus lacks project_inventory_sha256 provenance; "
            "cannot resolve interior function addresses safely"
        )
    actual_sha = hashlib.sha256(contents).hexdigest()
    if actual_sha != expected_sha:
        raise SystemExit(
            f"project inventory does not match pseudocode corpus: {inventory_path}\n"
            f"expected sha256 {expected_sha}, got {actual_sha}"
        )

    ranges: dict[str, list[tuple[int, int]]] = {}
    for line in contents.decode("utf-8").splitlines():
        record = json.loads(line)
        if record.get("record") != "function":
            continue
        entry = record.get("entry", {})
        if entry.get("space") != "ram":
            continue
        entry_addr = f"0x{int(entry['offset'], 16):08x}"
        body_ranges: list[tuple[int, int]] = []
        for body_range in record.get("body_ranges", []):
            minimum = body_range.get("min", {})
            maximum = body_range.get("max", {})
            if minimum.get("space") != "ram" or maximum.get("space") != "ram":
                continue
            body_ranges.append((int(minimum["offset"], 16), int(maximum["offset"], 16)))
        ranges[entry_addr] = body_ranges
    return ranges


class _Lookup:
    def __init__(
        self, functions: list[dict[str, Any]], metadata: dict[str, Any],
        inventory: Path | None, inventory_hint: str,
    ) -> None:
        self.functions = functions
        self.metadata = metadata
        self.inventory = inventory
        self.inventory_hint = inventory_hint

    @cached_property
    def by_entry(self) -> dict[str, list[dict[str, Any]]]:
        entries: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for record in self.functions:
            entries[record["entry_addr"]].append(record)
        return entries

    @cached_property
    def by_reference(self) -> dict[str, list[tuple[dict[str, Any], dict[str, Any]]]]:
        references: dict[str, list[tuple[dict[str, Any], dict[str, Any]]]] = defaultdict(list)
        for function in self.functions:
            for reference in function.get("data_references", []):
                references[reference["to_addr"]].append((function, reference))
        return references

    @cached_property
    def range_index(self) -> tuple[list[tuple[int, int, int]], list[int]] | str:
        if self.inventory is None:
            return f"pseudocode corpus does not identify a project inventory; {self.inventory_hint}"
        try:
            ranges = load_function_body_ranges(self.inventory, self.metadata)
        except SystemExit as exc:
            return f"{exc}\n{self.inventory_hint}"
        intervals = sorted(
            (start, end, position)
            for position, record in enumerate(self.functions)
            for start, end in ranges.get(record["entry_addr"], ())
        )
        # Prefix maxima retain overlapping ranges and let the scan stop at gaps.
        max_ends: list[int] = []
        for _, end, _ in intervals:
            max_ends.append(max(max_ends[-1], end) if max_ends else end)
        return intervals, max_ends

    def find_functions(self, query: str) -> tuple[list[dict[str, Any]], bool]:
        address = normalize_address(query)
        if address is not None:
            exact = self.by_entry.get(address)
            if exact:
                return exact, True

            range_index = self.range_index
            if isinstance(range_index, str):
                raise ValueError(range_index)
            target = int(address, 16)
            intervals, max_ends = range_index
            position = bisect_right(intervals, target, key=lambda interval: interval[0]) - 1
            positions: set[int] = set()
            while position >= 0 and max_ends[position] >= target:
                _, end, function_position = intervals[position]
                if end >= target:
                    positions.add(function_position)
                position -= 1
            containing = [self.functions[position] for position in sorted(positions)]
            if len(containing) > 1:
                names = ", ".join(f"{r['entry_addr']} {r['name']}" for r in containing)
                raise ValueError(f"address {address} belongs to multiple functions: {names}")
            if containing:
                return containing, True

        folded = query.casefold()
        exact_names = [record for record in self.functions if str(record["name"]).casefold() == folded]
        if exact_names:
            return exact_names, True
        return [record for record in self.functions if folded in str(record["name"]).casefold()], False

    def find_references(self, query: str) -> list[tuple[dict[str, Any], dict[str, Any]]]:
        address = normalize_address(query)
        if address is None:
            raise ValueError(f"invalid data-reference address: {query!r}")
        return self.by_reference.get(address, [])


class _View:
    def __init__(self, directory: Path, lookup: _Lookup, materialize_command: str) -> None:
        self.directory = directory.resolve()
        self.lookup = lookup
        self.materialize_command = materialize_command

    @cached_property
    def index(self) -> dict[str, str] | str:
        path = self.directory / "index.tsv"
        try:
            with path.open(encoding="utf-8") as stream:
                if stream.readline().rstrip("\n") != VIEW_INDEX_HEADER:
                    return f"invalid pseudocode view index: {path}"
                entries: dict[str, str] = {}
                for line in stream:
                    fields = line.rstrip("\n").split("\t")
                    if len(fields) != 5:
                        return f"invalid pseudocode view index row: {path}"
                    entry, name, signature, filename, digest = fields
                    records = self.lookup.by_entry.get(entry, ())
                    if entry in entries or len(records) != 1:
                        return f"pseudocode view index does not match the selected corpus: {path}"
                    record = records[0]
                    if (name, signature, digest) != (
                        str(record["name"]), str(record.get("signature") or ""), record["decompiled_c_sha256"],
                    ):
                        return f"pseudocode view index does not match the selected corpus at {entry}: {path}"
                    entries[entry] = filename
                if len(entries) != len(self.lookup.by_entry):
                    return f"pseudocode view index does not cover the selected corpus: {path}"
                return entries
        except FileNotFoundError:
            return f"missing pseudocode view index: {path}"
        except (OSError, UnicodeError) as exc:
            return f"cannot read pseudocode view index {path}: {exc}"

    def path(self, record: dict[str, Any]) -> Path:
        try:
            return self._path(record)
        except ValueError as exc:
            raise ValueError(f"{exc}\nmaterialize the selected corpus with: {self.materialize_command}") from exc

    def _path(self, record: dict[str, Any]) -> Path:
        index = self.index
        if isinstance(index, str):
            raise ValueError(index)
        inventory_sha256 = self.lookup.metadata.get("project_inventory_sha256")
        if not isinstance(inventory_sha256, str) or not inventory_sha256:
            raise ValueError("pseudocode corpus lacks project_inventory_sha256 view provenance")
        relative = Path(index[record["entry_addr"]])
        if relative.is_absolute() or ".." in relative.parts or relative.suffix != ".c":
            raise ValueError(f"invalid pseudocode view path: {relative}")
        try:
            path = (self.directory / relative).resolve()
            if not path.is_relative_to(self.directory):
                raise ValueError(f"pseudocode view path escapes {self.directory}: {relative}")
            if not path.is_file():
                raise ValueError(f"missing pseudocode view file: {path}")
            if path.read_bytes() != render_view_file(record, inventory_sha256).encode("utf-8"):
                raise ValueError(f"pseudocode view file does not match the selected corpus or inventory: {path}")
        except (OSError, RuntimeError) as exc:
            raise ValueError(f"cannot read pseudocode view file {relative}: {exc}") from exc
        return path


def print_listing(records: list[dict[str, Any]]) -> None:
    for record in records:
        signature = record.get("signature") or ""
        print(f"{record['entry_addr']}\t{record['name']}\t{signature}")


def print_data_references(matches: list[tuple[dict[str, Any], dict[str, Any]]]) -> None:
    for function, reference in matches:
        print(
            f"{reference['from_addr']}\t{reference['ref_type']}\t{reference['to_addr']}\t"
            f"{function['entry_addr']}\t{function['name']}\top={reference['operand_index']}"
        )


def unique_functions(matches: list[tuple[dict[str, Any], dict[str, Any]]]) -> list[dict[str, Any]]:
    by_entry: dict[str, dict[str, Any]] = {}
    for function, _ in matches:
        by_entry[function["entry_addr"]] = function
    return [by_entry[entry] for entry in sorted(by_entry, key=lambda value: int(value, 16))]


def print_code(records: list[dict[str, Any]], *, separators: bool) -> None:
    for index, record in enumerate(records):
        if separators:
            if index:
                print()
            print(f"/* ==== {record['entry_addr']} {record['name']} ==== */")
        code = record["decompiled_c"]
        sys.stdout.write(code)
        if not code.endswith("\n"):
            sys.stdout.write("\n")


def _run_queries(
    args: argparse.Namespace, lookup: _Lookup, view: _View | None, target: str | None, corpus: Path,
) -> int:
    results = []
    missed = False
    queries = args.data_ref or args.queries
    for query in queries:
        try:
            if args.data_ref:
                reference_matches = lookup.find_references(query)
                if not reference_matches:
                    raise ValueError(f"no canonical data references target {query!r}")
                matches = unique_functions(reference_matches)
                show_code = args.all
            else:
                matches, exact = lookup.find_functions(query)
                if not matches:
                    raise ValueError(f"no pseudocode function matches {query!r}")
                show_code = not args.list and (exact or len(matches) == 1 or args.all)
            paths = [str(view.path(record)) for record in matches] if view is not None else None
        except ValueError as exc:
            missed = True
            if args.json:
                results.append({"query": query, "matches": [], "error": str(exc)})
            else:
                print(f"{query!r}: {exc}" if len(queries) > 1 else str(exc), file=sys.stderr)
            continue

        if args.json:
            references_by_entry: dict[str, list[dict[str, Any]]] = defaultdict(list)
            if args.data_ref:
                for record, reference in reference_matches:
                    references_by_entry[record["entry_addr"]].append(reference)
            rows = []
            for index, record in enumerate(matches):
                entry = record["entry_addr"]
                row = {
                    "entry": entry,
                    "name": record["name"],
                    "signature": record.get("signature"),
                    "references": references_by_entry[entry] if args.data_ref else record.get("data_references", []),
                }
                if paths is not None:
                    row["path"] = paths[index]
                elif show_code:
                    row["decompiled_c"] = record["decompiled_c"]
                rows.append(row)
            results.append({"query": query, "matches": rows, "error": None})
        elif paths is not None:
            print("\n".join(paths))
        elif show_code:
            print_code(matches, separators=bool(args.data_ref) or len(matches) > 1)
        elif args.list:
            print_listing(matches)
        elif args.data_ref:
            print_data_references(reference_matches)
        else:
            print(f"{len(matches)} functions match {query!r}; refine the query or pass --all:")
            print_listing(matches)

    if args.json:
        print(json.dumps({
            "target": target,
            "corpus": str(corpus),
            "mode": "data-ref" if args.data_ref else "function",
            "results": results,
        }))
    return int(missed)


def main() -> int:
    parser = argparse.ArgumentParser(prog="pseudo", description=__doc__)
    parser.add_argument("queries", nargs="*", metavar="QUERY", help="function addresses, names, or name substrings")
    parser.add_argument("--target", help="registered analysis target; defaults to data/analysis_targets.json primary")
    parser.add_argument(
        "--data-ref", metavar="ADDRESS", action="append", default=[],
        help="find canonical references to ADDRESS (repeat to query multiple addresses)",
    )
    parser.add_argument("--corpus", type=Path, help="read an explicit corpus instead of the registered target's annotated view")
    parser.add_argument(
        "--inventory", type=Path,
        help="project inventory used for exact interior-address containment",
    )
    parser.add_argument("--all", action="store_true", help="print pseudocode for every substring match")
    parser.add_argument("--list", action="store_true", help="list matching functions instead of pseudocode")
    parser.add_argument("--path", action="store_true", help="show paths from the matching materialized view's index.tsv")
    parser.add_argument("--json", action="store_true", help="emit ordered query results and per-query errors as JSON")
    parser.add_argument("--stats", action="store_true", help="show corpus provenance and counts")
    parser.add_argument(
        "--materialize",
        action="store_true",
        help="rebuild build/out/pseudocode from the tracked corpus without running Ghidra",
    )
    parser.add_argument("--view-dir", type=Path, default=DEFAULT_VIEW)
    args = parser.parse_intermixed_args()
    queries = args.queries or args.data_ref
    if args.queries and args.data_ref:
        parser.error("positional queries and --data-ref are mutually exclusive")
    if not queries and not (args.stats or args.materialize):
        parser.error("query is required unless --data-ref, --stats, or --materialize is used")
    if args.json and (args.stats or args.materialize):
        parser.error("use --stats and --materialize separately from --json queries")
    if args.path and (not queries or args.stats or args.list):
        parser.error("--path requires queries and cannot be combined with --stats or --list")

    try:
        target_name, target_row = analysis_target.target(args.target)
    except SystemExit as exc:
        if "tools/gtarget list" in str(exc):
            raise
        raise SystemExit(f"{exc}\nList registered targets with: tools/gtarget list") from exc
    target_hint = f"Inspect registered inputs with: tools/gtarget show {target_name}"
    artifact_hint = f"{target_hint}\nDiscover tracked corpora with: tools/artifact list decompilations.jsonl"
    custom_corpus = args.corpus is not None
    corpus = (args.corpus or (ROOT / target_row["decompiler_corpus"])).expanduser().resolve()
    try:
        metadata, functions = load_corpus(corpus)
    except SystemExit as exc:
        raise SystemExit(f"{exc}\n{artifact_hint}") from exc

    declared_target = metadata.get("analysis_target")
    digest = metadata.get("executable_sha256")
    if not custom_corpus or args.target is not None:
        if (
            (declared_target is not None and declared_target != target_name)
            or (digest is not None and digest != target_row["codeflash_sha256"])
            or (not custom_corpus and (
                digest is None or metadata.get("project_inventory_path") != target_row["inventory_baseline"]
            ))
        ):
            raise SystemExit(f"pseudocode corpus does not match target {target_name}: {corpus}\n{artifact_hint}")
    output_target = target_name if not custom_corpus or args.target is not None else None
    if output_target is None and isinstance(declared_target, str):
        output_target = declared_target
    if args.corpus is None and "decomp_root" in target_row:
        symbols = ROOT / target_row["decomp_root"] / "symbols.jsonl"
        try:
            names = {int(row["addr"], 16): row["name"]
                     for row in map(json.loads, symbols.read_text(encoding="utf-8").splitlines())}
        except OSError as exc:
            raise SystemExit(f"cannot read target symbol annotations {symbols}: {exc}\n{artifact_hint}") from exc
        try:
            renames = {row["name"]: names[int(row["entry_addr"], 16)]
                       for row in functions
                       if row["name"] != names[int(row["entry_addr"], 16)]}
        except KeyError as exc:
            raise SystemExit(f"target symbol annotations do not cover the corpus; missing entry {exc}\n{artifact_hint}") from exc
        if renames:
            tokens = re.compile(r"\b(?:" + "|".join(map(re.escape, renames)) + r")\b")
            for row in functions:
                for key in ("name", "signature", "decompiled_c"):
                    if row[key] is not None:
                        row[key] = tokens.sub(lambda match: renames[match.group()], row[key])
                row["decompiled_c_sha256"] = hashlib.sha256(row["decompiled_c"].encode()).hexdigest()
                # This is an annotated view; recorded PC spans belong to the raw corpus.
                row.pop("c_locations", None)
    inventory = args.inventory
    if inventory is None and isinstance(metadata.get("project_inventory_path"), str):
        inventory = ROOT / metadata["project_inventory_path"]
    if inventory is not None:
        inventory = inventory.expanduser()

    if args.materialize:
        materialize_view(args.view_dir, functions, metadata)
        print(
            f"Materialized {len(functions)} pseudocode files at {args.view_dir.expanduser().resolve()}",
            file=sys.stderr if args.path else sys.stdout,
        )

    if args.stats:
        print(json.dumps(metadata, indent=2, sort_keys=True))
    if not queries:
        return 0

    lookup = _Lookup(functions, metadata, inventory, f"Pass --inventory with the matching inventory.\n{target_hint}")
    view = None
    if args.path:
        materialize = ["tools/pseudo"]
        if not custom_corpus or args.target is not None:
            materialize.extend(["--target", target_name])
        if custom_corpus:
            materialize.extend(["--corpus", str(corpus)])
        view_dir = args.view_dir.expanduser().resolve()
        if view_dir != DEFAULT_VIEW:
            materialize.extend(["--view-dir", str(view_dir)])
        materialize.append("--materialize")
        view = _View(view_dir, lookup, shlex.join(materialize))
    return _run_queries(args, lookup, view, output_target, corpus)


if __name__ == "__main__":
    raise SystemExit(main())
