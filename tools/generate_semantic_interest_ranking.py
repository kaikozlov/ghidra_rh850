#!/usr/bin/env python3
"""Generate a deterministic semantic-review interest ranking.

The scalar score is a weighted sum of log-normalized structural components:
body bytes .18, callers .10, callees .10, indirect references .14, unique RAM
references .14, RAM read/write density .12, MMIO .08, CodeFlash data .06,
strings .03, and an unreviewed bonus .05. No zero-caller penalty exists;
indirect/table callbacks receive their own positive component.
"""
from __future__ import annotations

import argparse
import csv
import math
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]
TOP_N = 40
SELECTION_DATE = "2026-08-11"
MANDATED = {0x35B86, 0x35D1E, 0x5BEA6, 0xBE8E6, 0x916E2}
WEIGHTS = {
    "size": 0.18,
    "callers": 0.10,
    "callees": 0.10,
    "indirect": 0.14,
    "ram": 0.14,
    "ram_rw_density": 0.12,
    "mmio": 0.08,
    "codeflash_data": 0.06,
    "strings": 0.03,
    "unreviewed": 0.05,
}
HEADER = [
    "entry_addr", "function_bytes", "caller_count", "callee_count",
    "indirect_reference_count", "ram_ref_count", "ram_read_ref_count",
    "ram_write_ref_count", "mmio_ref_count", "codeflash_data_ref_count",
    "string_ref_count", "root_kind", "review_state", "score_size_norm",
    "score_callers_norm", "score_callees_norm", "score_indirect_norm",
    "score_ram_norm", "score_ram_rw_density_norm", "score_mmio_norm",
    "score_codeflash_data_norm", "score_strings_norm", "score_unreviewed_norm",
    "final_score", "rank", "scalar_top_n", "strata", "selected_for_sweep",
    "selection_date", "review_date", "review_result",
]


def log_normalize(values: list[float]) -> list[float]:
    transformed = [math.log1p(value) for value in values]
    maximum = max(transformed, default=0.0)
    return [value / maximum if maximum else 0.0 for value in transformed]


def top(rows: list[dict[str, object]], key, count: int = 5) -> set[int]:
    ordered = sorted(rows, key=lambda row: (-key(row), -float(row["final_score"]), int(row["address"])))
    return {int(row["address"]) for row in ordered[:count]}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ledger", type=Path, default=REPO / "data" / "semantic_coverage_ledger.csv")
    parser.add_argument("--output", type=Path, default=REPO / "data" / "generated" / "semantic_interest_ranking.csv")
    args = parser.parse_args()

    with args.ledger.open(newline="") as handle:
        source = list(csv.DictReader(handle))
    rows: list[dict[str, object]] = []
    for row in source:
        body = int(row["body_bytes"])
        reads = int(row["ram_read_ref_count"])
        writes = int(row["ram_write_ref_count"])
        rows.append({
            "address": int(row["entry_addr"], 0),
            "function_bytes": body,
            "caller_count": int(row["caller_count"]),
            "callee_count": int(row["callee_count"]),
            "indirect_reference_count": int(row["indirect_reference_count"]),
            "ram_ref_count": int(row["ram_ref_count"]),
            "ram_read_ref_count": reads,
            "ram_write_ref_count": writes,
            "ram_rw_density": (reads + writes) / max(body, 1),
            "mmio_ref_count": int(row["mmio_ref_count"]),
            "codeflash_data_ref_count": int(row["codeflash_data_ref_count"]),
            "string_ref_count": int(row["string_ref_count"]),
            "root_kind": row["root_kind"],
            "review_state": row["review_state"],
            "review_date": row["review_date"],
            "review_result": row["review_result"],
        })

    component_values = {
        "size": [float(row["function_bytes"]) for row in rows],
        "callers": [float(row["caller_count"]) for row in rows],
        "callees": [float(row["callee_count"]) for row in rows],
        "indirect": [float(row["indirect_reference_count"]) for row in rows],
        "ram": [float(row["ram_ref_count"]) for row in rows],
        "ram_rw_density": [float(row["ram_rw_density"]) for row in rows],
        "mmio": [float(row["mmio_ref_count"]) for row in rows],
        "codeflash_data": [float(row["codeflash_data_ref_count"]) for row in rows],
        "strings": [float(row["string_ref_count"]) for row in rows],
        "unreviewed": [1.0 if row["review_state"] == "unreviewed" else 0.0 for row in rows],
    }
    normalized = {name: log_normalize(values) for name, values in component_values.items()}
    for index, row in enumerate(rows):
        for name in WEIGHTS:
            row[f"score_{name}_norm"] = normalized[name][index]
        row["final_score"] = sum(
            WEIGHTS[name] * float(row[f"score_{name}_norm"]) for name in WEIGHTS
        )
    ranked = sorted(rows, key=lambda row: (-float(row["final_score"]), int(row["address"])))
    for rank, row in enumerate(ranked, 1):
        row["rank"] = rank

    strata: dict[int, set[str]] = {int(row["address"]): set() for row in rows}
    def mark(addresses: set[int], name: str) -> None:
        for address in addresses:
            strata[address].add(name)

    mark(top([row for row in rows if int(row["address"]) < 0x20000], lambda row: float(row["final_score"]), 3), "boot")
    mark(top([row for row in rows if 0x20000 <= int(row["address"]) < 0x100000], lambda row: float(row["final_score"]), 3), "application")
    mark(top(rows, lambda row: int(row["ram_ref_count"])), "ram-heavy")
    mark(top(rows, lambda row: int(row["codeflash_data_ref_count"]) + int(row["indirect_reference_count"])), "table-heavy")
    mark(top(rows, lambda row: int(row["callee_count"])), "high-fanout")
    mark(top([row for row in rows if int(row["caller_count"]) == 0], lambda row: float(row["final_score"])), "zero-caller")
    mark(top(rows, lambda row: int(row["indirect_reference_count"])), "indirect-callback")
    mark({int(row["address"]) for row in rows if row["root_kind"] == "interrupt"}, "isr-rooted")
    mark(top(rows, lambda row: int(row["function_bytes"])), "largest-body")
    mark({int(row["address"]) for row in ranked if 38 <= int(row["rank"]) <= 42}, "cutoff-neighbor")
    mark(MANDATED, "mandated-cutoff-stateful")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=HEADER, lineterminator="\n")
        writer.writeheader()
        for row in sorted(rows, key=lambda item: int(item["address"])):
            address = int(row["address"])
            scalar = int(row["rank"]) <= TOP_N
            selected = scalar or bool(strata[address])
            output = {
                "entry_addr": f"0x{address:08x}",
                "function_bytes": row["function_bytes"],
                "caller_count": row["caller_count"],
                "callee_count": row["callee_count"],
                "indirect_reference_count": row["indirect_reference_count"],
                "ram_ref_count": row["ram_ref_count"],
                "ram_read_ref_count": row["ram_read_ref_count"],
                "ram_write_ref_count": row["ram_write_ref_count"],
                "mmio_ref_count": row["mmio_ref_count"],
                "codeflash_data_ref_count": row["codeflash_data_ref_count"],
                "string_ref_count": row["string_ref_count"],
                "root_kind": row["root_kind"],
                "review_state": row["review_state"],
                **{f"score_{name}_norm": f"{float(row[f'score_{name}_norm']):.6f}" for name in WEIGHTS},
                "final_score": f"{float(row['final_score']):.6f}",
                "rank": row["rank"],
                "scalar_top_n": str(scalar).lower(),
                "strata": ";".join(sorted(strata[address])),
                "selected_for_sweep": str(selected).lower(),
                "selection_date": SELECTION_DATE if selected else "",
                "review_date": row["review_date"],
                "review_result": row["review_result"],
            }
            writer.writerow(output)
    print(f"Wrote {len(rows)} ranked functions; scalar top {TOP_N}; selected {sum(int(r['rank']) <= TOP_N or bool(strata[int(r['address'])]) for r in rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
