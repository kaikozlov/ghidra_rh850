#!/usr/bin/env python3
"""Merge curated semantic review evidence into a structural Ghidra ledger."""
from __future__ import annotations

import argparse
import csv
from pathlib import Path


SEMANTIC_FIELDS = [
    "review_state",
    "evidence_grade",
    "verification_source",
    "oracle_class",
    "execution_status",
    "review_date",
    "review_result",
]
REVIEW_STATES = {
    "unreviewed",
    "reviewed_unknown",
    "structurally_bounded",
    "semantically_identified",
}
GRADES = {"", "verified", "observed", "recovered", "bounded", "hypothesis", "disproved"}
ORACLES = {
    "",
    "raw_bytes",
    "instruction_semantics",
    "cfg_dataflow",
    "dynamic_trace",
    "independent_external_artifact",
    "generated_self_check",
    "identity_hash",
    "documentation_lint",
}
EXECUTION = {"", "passed", "failed", "unavailable"}
INDEPENDENT_ORACLES = {
    "raw_bytes",
    "instruction_semantics",
    "cfg_dataflow",
    "dynamic_trace",
    "independent_external_artifact",
}


def validate(review: dict[str, str], address: int) -> None:
    state = review["review_state"]
    grade = review["evidence_grade"]
    oracle = review["oracle_class"]
    execution = review["execution_status"]
    if state not in REVIEW_STATES:
        raise SystemExit(f"0x{address:x}: invalid review_state {state!r}")
    if grade not in GRADES:
        raise SystemExit(f"0x{address:x}: invalid evidence_grade {grade!r}")
    if oracle not in ORACLES:
        raise SystemExit(f"0x{address:x}: invalid oracle_class {oracle!r}")
    if execution not in EXECUTION:
        raise SystemExit(f"0x{address:x}: invalid execution_status {execution!r}")
    if state == "unreviewed" and any(review[field] for field in SEMANTIC_FIELDS[1:]):
        raise SystemExit(f"0x{address:x}: unreviewed row carries semantic evidence")
    if state == "reviewed_unknown" and grade not in {"", "hypothesis"}:
        raise SystemExit(f"0x{address:x}: reviewed_unknown grade is too strong: {grade}")
    if state == "structurally_bounded" and grade not in {"bounded", "hypothesis"}:
        raise SystemExit(f"0x{address:x}: structurally_bounded requires bounded/hypothesis")
    if state == "semantically_identified" and grade not in {
        "verified", "observed", "recovered", "disproved"
    }:
        raise SystemExit(f"0x{address:x}: semantically_identified requires a supported grade")
    if grade in {"verified", "observed", "recovered", "bounded", "disproved"}:
        if oracle not in INDEPENDENT_ORACLES:
            raise SystemExit(
                f"0x{address:x}: grade {grade} exceeds non-independent oracle {oracle!r}"
            )
        if not review["verification_source"]:
            raise SystemExit(f"0x{address:x}: graded row lacks verification_source")
    if execution and not oracle:
        raise SystemExit(f"0x{address:x}: execution status without oracle")
    if not review["review_date"] or not review["review_result"]:
        raise SystemExit(f"0x{address:x}: curated review lacks date/result")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ledger", type=Path, required=True)
    parser.add_argument("--reviews", type=Path, required=True)
    args = parser.parse_args()

    with args.ledger.open(newline="") as handle:
        reader = csv.DictReader(handle)
        fields = reader.fieldnames
        rows = list(reader)
    if not fields or any(field not in fields for field in SEMANTIC_FIELDS):
        raise SystemExit("structural ledger lacks semantic merge fields")
    by_address = {int(row["entry_addr"], 0): row for row in rows}
    if len(by_address) != len(rows):
        raise SystemExit("structural ledger has duplicate addresses")
    if any(any(row[field] for field in SEMANTIC_FIELDS) for row in rows):
        raise SystemExit("structural exporter populated semantic fields")
    for row in rows:
        row["review_state"] = "unreviewed"

    with args.reviews.open(newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames != ["entry_addr", *SEMANTIC_FIELDS]:
            raise SystemExit(f"unexpected semantic review header: {reader.fieldnames}")
        reviews = list(reader)
    seen: set[int] = set()
    for review in reviews:
        address = int(review["entry_addr"], 0)
        if address in seen:
            raise SystemExit(f"duplicate semantic review address 0x{address:x}")
        seen.add(address)
        if address not in by_address:
            raise SystemExit(f"semantic review references unknown function 0x{address:x}")
        validate(review, address)
        for field in SEMANTIC_FIELDS:
            by_address[address][field] = review[field]

    temporary = args.ledger.with_suffix(args.ledger.suffix + ".tmp")
    with temporary.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    temporary.replace(args.ledger)
    print(f"Applied {len(reviews)} semantic reviews to {len(rows)} structural rows")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
