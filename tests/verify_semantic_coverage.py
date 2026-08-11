#!/usr/bin/env python3
"""Validate the committed semantic ledger and its curated evidence boundary."""
from __future__ import annotations

import csv
import json
import subprocess
import sys
import tempfile
from collections import Counter
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]
LEDGER = REPO / "data" / "semantic_coverage_ledger.csv"
SUMMARY = REPO / "data" / "semantic_coverage_summary.json"
REVIEWS = REPO / "data" / "semantic_review_status.csv"
MERGER = REPO / "tools" / "apply_semantic_review_status.py"
HEADER = [
    "entry_addr", "body_bytes", "name", "discovery_source",
    "discovery_provenance", "name_source", "is_thunk", "calling_convention",
    "caller_count", "callee_count", "indirect_reference_count", "root_kind",
    "ram_ref_count", "ram_read_ref_count", "ram_write_ref_count",
    "mmio_ref_count", "codeflash_data_ref_count", "string_ref_count",
    "subsystem", "review_state", "evidence_grade", "verification_source",
    "oracle_class", "execution_status", "review_date", "review_result",
]
SEMANTIC_FIELDS = [
    "evidence_grade", "verification_source", "oracle_class", "execution_status",
    "review_date", "review_result",
]
DISCOVERY = {
    "auto-analysis", "direct-call seed", "callback-table seed", "vector seed",
    "manual/other",
}
REVIEW_STATES = {
    "unreviewed", "reviewed_unknown", "structurally_bounded",
    "semantically_identified",
}
GRADES = {"", "verified", "observed", "recovered", "bounded", "hypothesis", "disproved"}
ORACLES = {
    "", "raw_bytes", "instruction_semantics", "cfg_dataflow", "dynamic_trace",
    "independent_external_artifact", "generated_self_check", "identity_hash",
    "documentation_lint",
}
INDEPENDENT = {
    "raw_bytes", "instruction_semantics", "cfg_dataflow", "dynamic_trace",
    "independent_external_artifact",
}
EXECUTION = {"", "passed", "failed", "unavailable"}

passed = 0
failed = 0


def check(name: str, condition: bool, detail: str = "") -> None:
    global passed, failed
    passed += bool(condition)
    failed += not condition
    suffix = f" ({detail})" if detail else ""
    print(f"[{'PASS' if condition else 'FAIL'}] {name}{suffix}")


def counts(rows: list[dict[str, str]], field: str, *, include_blank: bool = True) -> dict[str, int]:
    result = Counter(row[field] for row in rows if include_blank or row[field])
    return dict(sorted(result.items()))


def merger_rejects(rows: list[dict[str, str]], reviews: list[dict[str, str]], expected: str) -> bool:
    with tempfile.TemporaryDirectory(prefix="semantic-review-negative-") as directory:
        root = Path(directory)
        ledger = root / "ledger.csv"
        review = root / "reviews.csv"
        with ledger.open("w", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=HEADER, lineterminator="\n")
            writer.writeheader()
            structural_rows = []
            for row in rows:
                structural = dict(row)
                for field in HEADER[19:]:
                    structural[field] = ""
                structural_rows.append(structural)
            writer.writerows(structural_rows)
        with review.open("w", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=["entry_addr", *HEADER[19:]], lineterminator="\n")
            writer.writeheader()
            writer.writerows(reviews)
        result = subprocess.run(
            [sys.executable, str(MERGER), "--ledger", str(ledger), "--reviews", str(review)],
            text=True, capture_output=True, check=False,
        )
        return result.returncode != 0 and expected in (result.stdout + result.stderr)


def main() -> int:
    print("== semantic coverage artifact ==")
    check("ledger exists", LEDGER.is_file(), str(LEDGER))
    check("summary exists", SUMMARY.is_file(), str(SUMMARY))
    check("curated reviews exist", REVIEWS.is_file(), str(REVIEWS))
    if not all(path.is_file() for path in (LEDGER, SUMMARY, REVIEWS)):
        return 1

    with LEDGER.open(newline="") as handle:
        reader = csv.DictReader(handle)
        check("ledger schema is exact", reader.fieldnames == HEADER, repr(reader.fieldnames))
        rows = list(reader)
    addresses: list[int] = []
    errors: list[str] = []
    for index, row in enumerate(rows):
        try:
            address = int(row["entry_addr"], 0)
            for field in (
                "body_bytes", "caller_count", "callee_count", "indirect_reference_count",
                "ram_ref_count", "ram_read_ref_count", "ram_write_ref_count",
                "mmio_ref_count", "codeflash_data_ref_count", "string_ref_count",
            ):
                if int(row[field]) < 0:
                    raise ValueError(f"negative {field}")
        except (KeyError, ValueError) as error:
            errors.append(f"row {index}: {error}")
            continue
        addresses.append(address)
        if row["discovery_source"] not in DISCOVERY:
            errors.append(f"0x{address:x}: discovery_source={row['discovery_source']}")
        if not row["discovery_provenance"]:
            errors.append(f"0x{address:x}: blank discovery provenance")
        if row["review_state"] not in REVIEW_STATES:
            errors.append(f"0x{address:x}: review_state={row['review_state']}")
        if row["evidence_grade"] not in GRADES or row["oracle_class"] not in ORACLES:
            errors.append(f"0x{address:x}: grade/oracle vocabulary")
        if row["execution_status"] not in EXECUTION:
            errors.append(f"0x{address:x}: execution_status={row['execution_status']}")
        if row["review_state"] == "unreviewed" and any(row[field] for field in SEMANTIC_FIELDS):
            errors.append(f"0x{address:x}: unreviewed row carries semantic evidence")
        if row["evidence_grade"] in {"verified", "observed", "recovered", "bounded", "disproved"}:
            if row["oracle_class"] not in INDEPENDENT or not row["verification_source"]:
                errors.append(f"0x{address:x}: grade exceeds oracle")
        if row["ram_read_ref_count"] and int(row["ram_read_ref_count"]) > int(row["ram_ref_count"]):
            errors.append(f"0x{address:x}: RAM read unique count exceeds total")
        if row["ram_write_ref_count"] and int(row["ram_write_ref_count"]) > int(row["ram_ref_count"]):
            errors.append(f"0x{address:x}: RAM write unique count exceeds total")

    check("all rows satisfy structural/semantic rules", not errors, repr(errors[:8]))
    check("addresses are sorted and unique", addresses == sorted(set(addresses)), str(len(addresses)))
    check("ledger is nonempty", bool(rows))
    check(
        "a user-defined name does not imply semantic review",
        any(row["name_source"] == "USER_DEFINED" and row["review_state"] == "unreviewed"
            and not row["evidence_grade"] for row in rows),
    )
    by_address = {int(row["entry_addr"], 0): row for row in rows}
    for address in (0x9729A, 0x972FA, 0x97432, 0x97546, 0x975EE, 0x97668, 0x976F4):
        row = by_address.get(address)
        check(f"callback 0x{address:08x} present", row is not None)
        if row:
            check(f"callback 0x{address:08x} discovery source", row["discovery_source"] == "callback-table seed")
            check(f"callback 0x{address:08x} reviewed semantics", row["review_state"] == "semantically_identified")
    check("direct-call seed represented", any(row["discovery_source"] == "direct-call seed" for row in rows))

    summary = json.loads(SUMMARY.read_text())
    reviewed = sum(row["review_state"] != "unreviewed" for row in rows)
    bounded = sum(row["review_state"] in {"structurally_bounded", "semantically_identified"} for row in rows)
    verified = sum(row["evidence_grade"] == "verified" and row["execution_status"] == "passed" for row in rows)
    check("summary schema version", summary.get("schema_version") == 2)
    check("summary discovered count", summary.get("discovered_function_count") == len(rows))
    check("summary reviewed count", summary.get("reviewed_function_count") == reviewed)
    check("summary bounded semantics count", summary.get("bounded_semantics_count") == bounded)
    check("summary deterministic verified count", summary.get("deterministically_verified_count") == verified)
    check("summary discovery counts", summary.get("discovery_source_counts") == counts(rows, "discovery_source"))
    check("summary review counts", summary.get("review_state_counts") == counts(rows, "review_state"))
    check("summary grade counts", summary.get("evidence_grade_counts") == counts(rows, "evidence_grade", include_blank=False))

    with REVIEWS.open(newline="") as handle:
        review_rows = list(csv.DictReader(handle))
    check("curated addresses are unique", len(review_rows) == len({row["entry_addr"] for row in review_rows}))
    unknown = dict(review_rows[0])
    unknown["entry_addr"] = "0x00ffffff"
    check("merger rejects unknown addresses", merger_rejects(rows, [unknown], "unknown function"))
    check("merger rejects duplicate entries", merger_rejects(rows, [review_rows[0], review_rows[0]], "duplicate semantic review"))

    print(f"\nSummary: {passed} passed, {failed} failed")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
