#!/usr/bin/env python3
"""Merge P1M-E drcov instruction traces into exact-target function coverage."""
from __future__ import annotations

import argparse
import bisect
import hashlib
import json
import re
import struct
from collections import Counter, defaultdict
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from itertools import pairwise
from pathlib import Path
from typing import Any

from tools import REPO_ROOT
from tools.emulation.p1me_machine import capture_many
from tools.project.analysis_target import target as resolve_target

TARGET = "camry-8965F3307000"
OUTPUT = Path("data/generated/camry_8965F3307000_execution_coverage.json")
TRACE_OUTPUT_DIR = REPO_ROOT / "build/out/targets/camry-8965F3307000/execution-coverage"
DEFAULT_SCENARIOS = (
    REPO_ROOT / "tests/fixtures/rh850/machine/camry-8965F3307000/camry_f33_scheduler_publication_native_ch1_single_request_returns.json",
    REPO_ROOT / "tests/fixtures/rh850/machine/camry-8965F3307000/camry_f33_scheduler_publication_native_ch0_preempts_ch1_full_return.json",
)
SCHEMA = "rh850-execution-coverage-v2"
INDIRECT_FLOW_OPS = frozenset(("CALLIND", "BRANCHIND"))


class CoverageError(RuntimeError):
    pass


@dataclass(frozen=True)
class Module:
    base: int
    end: int
    path: Path


@dataclass(frozen=True)
class Trace:
    scenario_id: str
    path: Path
    module: Module
    blocks: tuple[tuple[int, int], ...]
    instructions: tuple[tuple[int, int], ...] = ()

def _sha256(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def read_drcov(path: Path) -> Trace:
    path = path.resolve()
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except UnicodeDecodeError as exc:
        raise CoverageError(f"{path}: drcov log is not UTF-8 text") from exc
    if len(lines) < 7:
        raise CoverageError(f"{path}: truncated drcov log")
    expected = (
        "DRCOV VERSION: 3",
        "DRCOV FLAVOR: drcov",
        "Module Table: version 5, count 1",
        "Columns: id, containing_id, start, end, entry, offset, preferred_base, path",
    )
    if tuple(lines[:4]) != expected:
        raise CoverageError(f"{path}: unsupported drcov header")
    fields = [field.strip() for field in lines[4].split(", ", 7)]
    if len(fields) != 8 or fields[:2] != ["0", "0"]:
        raise CoverageError(f"{path}: invalid module row")
    try:
        module_path = Path(fields[7])
        if not module_path.is_absolute():
            module_path = REPO_ROOT / module_path
        module = Module(
            int(fields[2], 0),
            int(fields[3], 0),
            module_path.resolve(),
        )
        if int(fields[5], 0) != 0 or int(fields[6], 0) != module.base:
            raise CoverageError(f"{path}: unsupported module offset or preferred base")
    except ValueError as exc:
        raise CoverageError(f"{path}: invalid module bounds") from exc
    table_match = re.fullmatch(r"BB Table: ([0-9]+) bbs", lines[5])
    if table_match is None:
        raise CoverageError(f"{path}: missing basic-block table")
    count = int(table_match.group(1))
    if lines[6] != "module id, start, size:":
        raise CoverageError(f"{path}: invalid basic-block text heading")
    if len(lines) != 7 + count:
        raise CoverageError(f"{path}: basic-block table length does not match its count")
    blocks: list[tuple[int, int]] = []
    seen: set[int] = set()
    for index, line in enumerate(lines[7:]):
        match = re.fullmatch(
            r"module\[ *([0-9]+)\]:[ \t]*0x([0-9a-fA-F]+),[ \t]*([0-9]+)",
            line,
        )
        if match is None:
            raise CoverageError(f"{path}: invalid basic-block row at index {index}")
        module_id, offset, size = (
            int(match.group(1), 10), int(match.group(2), 16), int(match.group(3), 10),
        )
        pc = module.base + offset
        if module_id != 0 or size == 0 or pc + size > module.end:
            raise CoverageError(f"{path}: invalid basic-block row at index {index}")
        if pc in seen:
            raise CoverageError(f"{path}: duplicate basic block at 0x{pc:08X}")
        seen.add(pc)
        blocks.append((pc, size))
    return Trace(path.stem, path, module, tuple(blocks))


def _load_instruction_report(trace: Trace) -> Trace:
    report_path = trace.path.with_name(f"{trace.path.stem}.report.json")
    try:
        report = json.loads(report_path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise CoverageError(f"{trace.path}: matching machine report is required") from exc
    scenario_id = report.get("scenario")
    rows = report.get("instruction_trace")
    if not isinstance(scenario_id, str) or not isinstance(rows, list):
        raise CoverageError(f"{report_path}: missing scenario or instruction_trace")
    instructions: list[tuple[int, int]] = []
    unique: dict[int, int] = {}
    for index, row in enumerate(rows):
        try:
            pc = int(row["pc"], 0)
            size = int(row["size"])
        except (KeyError, TypeError, ValueError) as exc:
            raise CoverageError(
                f"{report_path}: invalid instruction_trace row {index}",
            ) from exc
        instructions.append((pc, size))
        prior = unique.setdefault(pc, size)
        if prior != size:
            raise CoverageError(f"{report_path}: conflicting size at 0x{pc:08X}")
    if tuple(unique.items()) != trace.blocks:
        raise CoverageError(
            f"{report_path}: first-execution instruction set differs from drcov",
        )
    return Trace(scenario_id, trace.path, trace.module, trace.blocks, tuple(instructions))


def _load_functions(
    corpus_path: Path,
    target_name: str,
) -> tuple[list[dict[str, Any]], list[tuple[int, int, int]], set[int], set[int]]:
    functions: list[dict[str, Any]] = []
    ranges: list[tuple[int, int, int]] = []
    indirect_flow_pcs: set[int] = set()
    indirect_branch_pcs: set[int] = set()
    with corpus_path.open(encoding="utf-8") as stream:
        header = json.loads(next(stream))
        if header.get("analysis_target") != target_name:
            raise CoverageError(f"{corpus_path}: target identity mismatch")
        for line in stream:
            row = json.loads(line)
            if row.get("record") != "function" or row.get("address_space") != "ram":
                continue
            entry = int(row["entry_addr"], 0)
            index = len(functions)
            functions.append({
                "address": entry,
                "name": row["name"],
                "body_size": row["body_size"],
            })
            for body_range in row["body_ranges"]:
                if body_range["space"] != "ram":
                    continue
                ranges.append((
                    int(body_range["min"], 0),
                    int(body_range["max"], 0),
                    index,
                ))
            for location in row.get("c_locations", ()):
                operation = location.get("op")
                pc = int(location["pc"], 0)
                if operation in INDIRECT_FLOW_OPS:
                    indirect_flow_pcs.add(pc)
                if operation == "BRANCHIND":
                    indirect_branch_pcs.add(pc)
    ranges.sort()
    for previous, current in pairwise(ranges):
        if current[0] <= previous[1] and current[2] != previous[2]:
            raise CoverageError(f"{corpus_path}: overlapping function body ranges")
    return functions, ranges, indirect_flow_pcs, indirect_branch_pcs


def _owners(
    pcs: Iterable[int],
    ranges: list[tuple[int, int, int]],
) -> dict[int, int | None]:
    starts = [row[0] for row in ranges]
    result: dict[int, int | None] = {}
    for pc in pcs:
        position = bisect.bisect_right(starts, pc) - 1
        result[pc] = (
            ranges[position][2]
            if position >= 0 and pc <= ranges[position][1]
            else None
        )
    return result


def _incision_rows(
    traces: Sequence[Trace],
    owners: dict[int, int | None],
    functions: Sequence[dict[str, Any]],
    function_starts: set[int],
    interrupt_targets: set[int],
    indirect_flow_pcs: set[int],
    indirect_branch_pcs: set[int],
) -> dict[str, list[dict[str, Any]]]:
    category_names = (
        "isr_entries",
        "isr_overlapping_function_entries",
        "task_switch_targets",
        "task_switch_overlapping_function_targets",
    )
    counts = {name: Counter() for name in category_names}
    scenarios = {name: defaultdict(set) for name in category_names}
    sources = {name: defaultdict(set) for name in category_names}

    def record(category: str, target: int, scenario_id: str, source: int | None) -> None:
        counts[category][target] += 1
        scenarios[category][target].add(scenario_id)
        if source is not None:
            sources[category][target].add(source)

    for trace in traces:
        first = trace.instructions[0][0] if trace.instructions else None
        if first in interrupt_targets and first not in function_starts:
            category = (
                "isr_overlapping_function_entries"
                if owners.get(first) is not None else "isr_entries"
            )
            record(category, first, trace.scenario_id, None)
        for (source, size), (target, _) in pairwise(trace.instructions):
            if target == source + size or target in function_starts:
                continue
            source_owner = owners.get(source)
            target_owner = owners.get(target)
            if source_owner is not None and source_owner == target_owner:
                continue
            if source in indirect_branch_pcs:
                category = (
                    "task_switch_overlapping_function_targets"
                    if target_owner is not None else "task_switch_targets"
                )
                record(category, target, trace.scenario_id, source)
            elif target in interrupt_targets and source not in indirect_flow_pcs:
                category = (
                    "isr_overlapping_function_entries"
                    if target_owner is not None else "isr_entries"
                )
                record(category, target, trace.scenario_id, source)

    def rows(category: str) -> list[dict[str, Any]]:
        result: list[dict[str, Any]] = []
        for address, count in sorted(counts[category].items()):
            if count < 2:
                continue
            row: dict[str, Any] = {
                "address": f"0x{address:08X}",
                "recurrence_count": count,
                "scenario_ids": sorted(scenarios[category][address]),
                "source_addresses": [
                    f"0x{source:08X}" for source in sorted(sources[category][address])
                ],
            }
            owner = owners.get(address)
            if owner is not None:
                row["overlapping_function"] = {
                    "address": f"0x{functions[owner]['address']:08X}",
                    "name": functions[owner]["name"],
                }
            result.append(row)
        return result

    return {category: rows(category) for category in category_names}


def _interrupt_entries(
    image_path: Path,
    module: Module,
    function_starts: set[int],
    trace_counts: Counter[int],
    scenarios_by_pc: dict[int, set[str]],
) -> list[dict[str, Any]]:
    image = image_path.read_bytes()
    intbp = 0x20200
    pointers = [
        struct.unpack_from("<I", image, intbp - module.base + channel * 4)[0]
        for channel in range(384)
    ]
    in_image = [pointer for pointer in pointers if module.base <= pointer < module.end]
    default = Counter(in_image).most_common(1)[0][0]
    channels_by_target: dict[int, list[int]] = defaultdict(list)
    for channel, pointer in enumerate(pointers):
        if module.base <= pointer < module.end and pointer != default:
            channels_by_target[pointer].append(channel)
    return [
        {
            "address": f"0x{address:08X}",
            "channels": channels,
            "is_function_start": address in function_starts,
            "execution_count": trace_counts[address],
            "scenario_ids": sorted(scenarios_by_pc.get(address, ())),
            "reached": trace_counts[address] != 0,
        }
        for address, channels in sorted(channels_by_target.items())
    ]


def merge_coverage(target_name: str, drcov_paths: Sequence[Path]) -> dict[str, Any]:
    if len(drcov_paths) < 2:
        raise CoverageError("at least two drcov runs are required")
    resolved_name, target = resolve_target(target_name)
    image_path = (REPO_ROOT / target["codeflash"]).resolve()
    base = int(target["codeflash_base"], 0)
    module = Module(base, base + target["codeflash_size"], image_path)
    if _sha256(image_path) != target["codeflash_sha256"]:
        raise CoverageError("registered CodeFlash identity mismatch")
    traces = [_load_instruction_report(read_drcov(path)) for path in drcov_paths]
    if len({trace.scenario_id for trace in traces}) != len(traces):
        raise CoverageError("drcov scenario IDs must be unique")
    for trace in traces:
        if trace.module != module:
            raise CoverageError(
                f"{trace.path}: module does not match the registered CodeFlash",
            )

    corpus_path = (REPO_ROOT / target["decompiler_corpus"]).resolve()
    functions, ranges, indirect_flow_pcs, indirect_branch_pcs = _load_functions(
        corpus_path, resolved_name,
    )
    function_starts = {row["address"] for row in functions}
    trace_counts: Counter[int] = Counter()
    sizes: dict[int, int] = {}
    scenarios_by_pc: dict[int, set[str]] = defaultdict(set)
    for trace in traces:
        for pc, size in trace.instructions:
            if sizes.setdefault(pc, size) != size:
                raise CoverageError(f"conflicting instruction sizes at 0x{pc:08X}")
            trace_counts[pc] += 1
            scenarios_by_pc[pc].add(trace.scenario_id)
    owners = _owners(sizes, ranges)

    function_counts: Counter[int] = Counter()
    function_unique: Counter[int] = Counter()
    function_scenarios: dict[int, set[str]] = defaultdict(set)
    for pc, count in trace_counts.items():
        owner = owners[pc]
        if owner is None:
            continue
        function_counts[owner] += count
        function_unique[owner] += 1
        function_scenarios[owner].update(scenarios_by_pc[pc])
    per_function = [
        {
            "address": f"0x{functions[index]['address']:08X}",
            "name": functions[index]["name"],
            "executed_instruction_count": function_unique[index],
            "execution_count": function_counts[index],
            "scenario_ids": sorted(function_scenarios[index]),
        }
        for index in sorted(
            function_counts,
            key=lambda item: functions[item]["address"],
        )
    ]
    interrupt_entries = _interrupt_entries(
        image_path,
        module,
        function_starts,
        trace_counts,
        scenarios_by_pc,
    )
    incision_rows = _incision_rows(
        traces,
        owners,
        functions,
        function_starts,
        {int(row["address"], 0) for row in interrupt_entries},
        indirect_flow_pcs,
        indirect_branch_pcs,
    )
    incision = {
        name: {
            "candidate_count": len(rows),
            "candidates": rows,
        }
        for name, rows in incision_rows.items()
    }
    return {
        "schema": SCHEMA,
        "target": resolved_name,
        "evidence": (
            "Instruction counts from the listed report traces, matched to the "
            "registered CodeFlash module"
        ),
        "module": {
            "id": 0,
            "base": f"0x{module.base:08X}",
            "length": module.end - module.base,
            "path": target["codeflash"],
            "sha256": target["codeflash_sha256"],
        },
        "scenario_ids": [trace.scenario_id for trace in traces],
        "runs": [
            {
                "scenario_id": trace.scenario_id,
                "drcov": (
                    str(trace.path.relative_to(REPO_ROOT))
                    if trace.path.is_relative_to(REPO_ROOT)
                    else str(trace.path)
                ),
                "sha256": _sha256(trace.path),
                "instruction_records": len(trace.instructions),
                "unique_basic_blocks": len(trace.blocks),
            }
            for trace in traces
        ],
        "instruction_records": sum(trace_counts.values()),
        "unique_instruction_count": len(trace_counts),
        "unattributed_instruction_count": sum(
            owner is None for owner in owners.values()
        ),
        "function_inventory_count": len(functions),
        "executed_function_count": len(per_function),
        "functions": per_function,
        "incision": incision,
        "intbp_entries": interrupt_entries,
        "seed_script": target["entry_seed_script"],
        "seed_candidates": [
            row["address"] for row in interrupt_entries
            if not row["is_function_start"]
        ],
    }


def _produce_traces(
    target_name: str,
    scenarios: Sequence[Path],
    output_dir: Path,
) -> list[Path]:
    reports = capture_many(
        target_name,
        [scenario.resolve() for scenario in scenarios],
        output_dir.resolve(),
        instruction_trace=True,
    )
    return [Path(report["drcov_path"]) for report in reports]


def _parse_object_range(value: str) -> tuple[int, int]:
    try:
        start_text, end_text = value.split(":", 1)
        start, end = int(start_text, 0), int(end_text, 0)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("range must be START:END") from exc
    if end <= start:
        raise argparse.ArgumentTypeError("range END must be greater than START")
    return start, end


def rank_object_references(
    result: dict[str, Any],
    target_name: str,
    object_name: str,
    object_range: tuple[int, int],
) -> dict[str, Any]:
    """Rank functions with static references to [start,end) by function coverage."""
    resolved_name, target = resolve_target(target_name)
    corpus_path = (REPO_ROOT / target["decompiler_corpus"]).resolve()
    start, end = object_range
    coverage = {
        int(row["address"], 0): row
        for row in result["functions"]
    }
    rows = []
    with corpus_path.open(encoding="utf-8") as stream:
        header = json.loads(next(stream))
        if header.get("analysis_target") != resolved_name:
            raise CoverageError(f"{corpus_path}: target identity mismatch")
        for line in stream:
            function = json.loads(line)
            if function.get("record") != "function":
                continue
            references = [
                reference
                for reference in function.get("data_references", ())
                if reference.get("to_space") == "ram"
                and start <= int(reference["to_addr"], 0) < end
            ]
            if not references:
                continue
            address = int(function["entry_addr"], 0)
            observed = coverage.get(address, {})
            rows.append({
                "address": f"0x{address:08X}",
                "name": function["name"],
                "executed_instruction_count": observed.get("executed_instruction_count", 0),
                "execution_count": observed.get("execution_count", 0),
                "scenario_ids": observed.get("scenario_ids", []),
                "reference_count": len(references),
                "references": sorted({
                    reference["to_addr"] for reference in references
                }),
            })
    rows.sort(key=lambda row: (
        -row["executed_instruction_count"],
        -row["execution_count"],
        row["address"],
    ))
    return {
        "name": object_name,
        "start": f"0x{start:08X}",
        "end_exclusive": f"0x{end:08X}",
        "referencing_function_count": len(rows),
        "functions": rows,
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "drcov",
        nargs="*",
        type=Path,
        help="two or more P1M-E drcov runs",
    )
    parser.add_argument("--target", default=TARGET)
    parser.add_argument(
        "--scenario",
        action="append",
        type=Path,
        default=[],
        help="machine scenario to execute when no drcov files are supplied",
    )
    parser.add_argument("--trace-output-dir", type=Path, default=TRACE_OUTPUT_DIR)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--object", help="name for an address-range object ranking")
    parser.add_argument(
        "--object-range",
        type=_parse_object_range,
        metavar="START:END",
        help="half-open address range referenced by ranked functions",
    )
    args = parser.parse_args(argv)
    if args.drcov and args.scenario:
        parser.error("--scenario cannot be combined with drcov inputs")
    try:
        paths = args.drcov or _produce_traces(
            args.target,
            args.scenario or DEFAULT_SCENARIOS,
            args.trace_output_dir,
        )
        result = merge_coverage(args.target, paths)
        if not args.drcov:
            result["evidence"] = (
                "Exact-image P1M-E simulation instruction traces from the listed scenarios"
            )
        if bool(args.object) != bool(args.object_range):
            parser.error("--object and --object-range must be supplied together")
        if args.object:
            result["object_ranking"] = rank_object_references(
                result, args.target, args.object, args.object_range,
            )
    except (CoverageError, OSError, ValueError, json.JSONDecodeError) as exc:
        parser.error(str(exc))
    output = args.output if args.output.is_absolute() else REPO_ROOT / args.output
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "output": str(output),
        "scenario_ids": result["scenario_ids"],
        "unique_instruction_count": result["unique_instruction_count"],
        "executed_function_count": result["executed_function_count"],
        "object_ranking": result.get("object_ranking"),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
