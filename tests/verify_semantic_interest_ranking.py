#!/usr/bin/env python3
"""Verify deterministic semantic interest ranking and selected cohorts."""
from __future__ import annotations

import csv
import subprocess
import sys
import tempfile
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]
ARTIFACT = REPO / "data" / "generated" / "semantic_interest_ranking.csv"
GENERATOR = REPO / "tools" / "project" / "generate_semantic_interest_ranking.py"
MANDATED = {
    0x17C8, 0x64414, 0xB603A, 0x32868, 0x35B86, 0x35D1E, 0x5E572,
    0x5CEE6, 0x5B740, 0x5BEA6, 0xBE8E6, 0x916E2, 0x8FFCC,
    0x9729A, 0x972FA, 0x97432, 0x97546, 0x975EE, 0x97668, 0x976F4,
}
REQUIRED_STRATA = {
    "boot", "application", "ram-heavy", "table-heavy", "high-fanout",
    "zero-caller", "indirect-callback", "isr-rooted", "largest-body",
    "cutoff-neighbor", "mandated-cutoff-stateful", "mandatory-graph-reaudit",
}

passed = 0
failed = 0


def check(name: str, condition: bool, detail: str = "") -> None:
    global passed, failed
    passed += bool(condition)
    failed += not condition
    print(f"[{'PASS' if condition else 'FAIL'}] {name}" + (f" ({detail})" if detail else ""))


def main() -> int:
    with ARTIFACT.open(newline="") as handle:
        rows = list(csv.DictReader(handle))
    addresses = [int(row["entry_addr"], 0) for row in rows]
    check("artifact sorted uniquely by address", addresses == sorted(set(addresses)))
    ranks = sorted(int(row["rank"]) for row in rows)
    check("ranks are a complete permutation", ranks == list(range(1, len(rows) + 1)))

    scalar = sorted(
        (row for row in rows if row["scalar_top_n"] == "true"),
        key=lambda row: int(row["rank"]),
    )
    check("scalar cohort has exactly 40 rows", len(scalar) == 40)
    metric_fields = [
        "function_bytes", "caller_count", "callee_count", "indirect_reference_count",
        "ram_ref_count", "ram_read_ref_count", "ram_write_ref_count", "mmio_ref_count",
        "codeflash_data_ref_count", "string_ref_count", "review_state",
    ]
    metric_groups: dict[tuple[str, ...], list[dict[str, str]]] = {}
    for row in rows:
        metric_groups.setdefault(tuple(row[field] for field in metric_fields), []).append(row)
    check(
        "exact score ties break by address",
        all(
            [int(row["entry_addr"], 0) for row in sorted(group, key=lambda item: int(item["rank"]))]
            == sorted(int(row["entry_addr"], 0) for row in group)
            for group in metric_groups.values()
        ),
    )
    observed_strata = {
        stratum for row in rows for stratum in row["strata"].split(";") if stratum
    }
    check("all required strata represented", REQUIRED_STRATA <= observed_strata, repr(sorted(observed_strata)))
    by_address = {int(row["entry_addr"], 0): row for row in rows}
    for address in sorted(MANDATED):
        row = by_address.get(address)
        check(f"mandated 0x{address:08x} present", row is not None)
        if row:
            check(f"mandated 0x{address:08x} selected", row["selected_for_sweep"] == "true")
    check(
        "indirect callbacks receive a positive score component",
        all(
            float(row["score_indirect_norm"]) > 0
            for row in rows if int(row["indirect_reference_count"]) > 0
        ),
    )

    with tempfile.TemporaryDirectory(prefix="semantic-ranking-") as directory:
        output = Path(directory) / "ranking.csv"
        subprocess.run(
            [sys.executable, str(GENERATOR), "--output", str(output)],
            cwd=REPO, check=True, stdout=subprocess.DEVNULL,
        )
        check("clean regeneration is byte-identical", output.read_bytes() == ARTIFACT.read_bytes())

    print(f"\nSummary: {passed} passed, {failed} failed")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
