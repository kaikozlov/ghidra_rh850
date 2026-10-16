"""Build the machine-derived semantic coverage summary for a registered target.

The summary is derived from evidence the repository already owns:
- the canonical project inventory baseline (names, signatures, comments, bodies)
- the target's RH850 machine fixtures (executed scenarios, by entry address)
- the target's registered recovered-function tables (bounded markers)

It contains no hand-maintained review state. Evidence scope conventions live in
the owning subsystem reports and docs/status/FINDINGS.md, not per function rows.
"""
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

from tools import REPO_ROOT
from tools.project import analysis_target

SCHEMA_VERSION = 3


def load_registry(target: str) -> tuple[str, dict]:
    return analysis_target.target(target)


def load_inventory(registry: dict) -> tuple[dict, dict]:
    """Return (functions by entry addr, function_comment texts by entry addr)."""
    path = REPO_ROOT / registry["inventory_baseline"]
    functions: dict[int, dict] = {}
    comments: dict[int, str] = {}
    with path.open() as handle:
        for line in handle:
            record = json.loads(line)
            kind = record.get("record")
            if kind == "function":
                functions[int(record["entry"]["offset"], 16)] = record
            elif kind == "function_comment":
                comments[int(record["entry"]["offset"], 16)] = record.get("text", "")
    return functions, comments


def load_fixture_coverage(target_name: str, functions: dict[int, dict]) -> Counter:
    """Map machine-fixture entry addresses onto containing functions."""
    fixture_root = REPO_ROOT / "tests" / "fixtures" / "rh850" / "machine" / target_name
    coverage: Counter = Counter()
    if not fixture_root.is_dir():
        return coverage
    ranges = sorted(
        (int(rec["body_ranges"][0]["min"]["offset"], 16),
         int(rec["body_ranges"][-1]["max"]["offset"], 16), addr)
        for addr, rec in functions.items() if rec.get("body_ranges"))
    for path in sorted(fixture_root.glob("*.json")):
        try:
            scenario = json.loads(path.read_text())
        except json.JSONDecodeError:
            continue
        address = scenario.get("entry", {}).get("address")
        if not address:
            continue
        entry = int(address, 16)
        for start, end, addr in ranges:
            if start <= entry <= end:
                coverage[addr] += 1
                break
    return coverage


def load_bounded(registry: dict) -> set[int]:
    bounded: set[int] = set()
    functions_path = registry.get("recovered_functions")
    if not functions_path:
        return bounded
    path = REPO_ROOT / functions_path
    if not path.is_file():
        return bounded
    with path.open() as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            row = json.loads(line)
            if row.get("bounded"):
                bounded.add(int(row["addr"], 16))
    return bounded


def build_summary(target_name: str, registry: dict) -> dict:
    functions, comments = load_inventory(registry)
    fixture_coverage = load_fixture_coverage(target_name, functions)
    bounded = load_bounded(registry)

    named = documented = fixture_executed = bounded_count = 0
    named_bytes = documented_bytes = 0
    total_bytes = 0
    for addr, record in functions.items():
        body = int(record.get("body_address_count", 0))
        total_bytes += body
        is_named = record.get("name_source") == "USER_DEFINED"
        is_documented = bool(comments.get(addr))
        if is_named:
            named += 1
            named_bytes += body
        if is_documented:
            documented += 1
            documented_bytes += body
        if addr in fixture_coverage:
            fixture_executed += 1
        if addr in bounded:
            bounded_count += 1

    return {
        "analysis_target": target_name,
        "schema_version": SCHEMA_VERSION,
        "discovered_function_count": len(functions),
        "named_function_count": named,
        "documented_function_count": documented,
        "fixture_executed_function_count": fixture_executed,
        "bounded_function_count": bounded_count,
        "function_body_bytes": total_bytes,
        "named_body_bytes": named_bytes,
        "documented_body_bytes": documented_bytes,
        "fixture_scenario_count": sum(fixture_coverage.values()),
        "evidence_class_note": (
            "named/documented derive from the canonical inventory; fixture_executed "
            "derives from target machine-fixture entry addresses; bounded derives "
            "from the registered recovered-function table. No hand-graded review "
            "state is included; scope conventions live in the owning reports."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", required=True)
    parser.add_argument("--output", help="output path (defaults to registry semantic_coverage_summary)")
    args = parser.parse_args()
    target_name, registry = load_registry(args.target)
    summary = build_summary(target_name, registry)
    output = Path(args.output) if args.output else REPO_ROOT / registry["semantic_coverage_summary"]
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    print(f"wrote {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
