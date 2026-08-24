#!/usr/bin/env python3
"""Verify complete, reproducible disposition of the selected semantic sweep."""
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
RANKING = REPO / "data/generated/semantic_interest_ranking.csv"
INVENTORY = REPO / "data/ghidra_project_inventory.baseline.jsonl"
ARTIFACT = REPO / "data/generated/semantic_sweep_decompilations.jsonl"
GENERATOR = REPO / "tools/generate_semantic_sweep.py"
REVIEWS = REPO / "data/semantic_review_status.csv"
passed = failed = 0


def check(name: str, condition: object, detail: str = "") -> None:
    global passed, failed
    ok = bool(condition)
    passed += int(ok)
    failed += int(not ok)
    print(f"[{'PASS' if ok else 'FAIL'}] {name}" + (f" ({detail})" if detail else ""))


with RANKING.open(newline="") as stream:
    selected = {row["entry_addr"]: row for row in csv.DictReader(stream)
                if row["selected_for_sweep"] == "true"}
with REVIEWS.open(newline="") as stream:
    review_rows = list(csv.DictReader(stream))
reviews = {row["entry_addr"]: row for row in review_rows}
records = [json.loads(line) for line in ARTIFACT.read_text(encoding="utf-8").splitlines()]
metadata, functions = records[0], records[1:]

print("== semantic sweep provenance ==")
generator_source = GENERATOR.read_text(encoding="utf-8")
check("generator exports and compares the selected live project inventory",
      "export_ghidra_project.sh" in generator_source and "project-inventory" in generator_source
      and '"compare"' in generator_source
      and "live project does not match" in generator_source)
check("metadata schema", metadata == {
    "record": "metadata",
    "schema_version": 1,
    "selected_count": len(selected),
    "ranking_path": "data/generated/semantic_interest_ranking.csv",
    "ranking_sha256": hashlib.sha256(RANKING.read_bytes()).hexdigest(),
    "project_inventory_path": "data/ghidra_project_inventory.baseline.jsonl",
    "project_inventory_sha256": hashlib.sha256(INVENTORY.read_bytes()).hexdigest(),
})
check("artifact has exactly one function per selected address",
      {row["entry_addr"] for row in functions} == set(selected)
      and len(functions) == len(selected) == 100)
check("artifact is address-unique", len(functions) == len({row["entry_addr"] for row in functions}))

print("\n== decompiler identities and selection reasons ==")
errors = []
for row in functions:
    expected = selected[row["entry_addr"]]
    code = row["decompiled_c"]
    if row["record"] != "function":
        errors.append(f"{row['entry_addr']}: record kind")
    if row["rank"] != int(expected["rank"]):
        errors.append(f"{row['entry_addr']}: rank")
    if row["scalar_top_n"] != (expected["scalar_top_n"] == "true"):
        errors.append(f"{row['entry_addr']}: scalar selection")
    if row["strata"] != (expected["strata"].split(";") if expected["strata"] else []):
        errors.append(f"{row['entry_addr']}: strata")
    if hashlib.sha256(code.encode()).hexdigest() != row["normalized_c_sha256"]:
        errors.append(f"{row['entry_addr']}: decompiler hash")
    if not code.strip() or not row["name"]:
        errors.append(f"{row['entry_addr']}: empty output")
check("all decompilations retain exact identities and selection provenance", not errors, repr(errors[:8]))

print("\n== curated dispositions ==")
check("semantic review table addresses are unique", len(reviews) == len(review_rows))
missing = sorted(set(selected) - set(reviews))
check("every selected function has a curated review row", not missing, repr(missing))
check("every selected function records a nonempty disposition",
      all(reviews[address]["review_state"] != "unreviewed"
          and reviews[address]["review_result"] for address in selected))
check("review-unknown rows claim no semantic grade",
      all(not row["evidence_grade"] for row in reviews.values()
          if row["review_state"] == "reviewed_unknown"))

print(f"\nResults: {passed} passed, {failed} failed")
raise SystemExit(1 if failed else 0)
