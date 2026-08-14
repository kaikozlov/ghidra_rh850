#!/usr/bin/env python3
"""Verify the multidimensional status page against committed artifacts."""
from __future__ import annotations

import csv
import hashlib
import json
import struct
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
STATUS = REPO / "docs/status/ANALYSIS_STATUS.md"
passed = failed = 0


def check(name: str, condition: object, detail: str = "") -> None:
    global passed, failed
    ok = bool(condition)
    passed += int(ok)
    failed += int(not ok)
    print(f"[{'PASS' if ok else 'FAIL'}] {name}" + (f" ({detail})" if detail else ""))


text = STATUS.read_text(encoding="utf-8")
code = REPO / "firmware/RH850_P1M-E_CodeFlash.bin"
data = REPO / "firmware/RH850_P1M-E_DataFlash.bin"
check("firmware sizes", code.stat().st_size == 0x100000 and data.stat().st_size == 0x8000)
check("firmware sizes published", "CodeFlash 1,048,576 B; DataFlash 32,768 B" in text)

inventory = REPO / "data/ghidra_project_inventory.baseline.jsonl"
records = [json.loads(line) for line in inventory.read_text(encoding="utf-8").splitlines()]
totals = records[-1]
inventory_sha = hashlib.sha256(inventory.read_bytes()).hexdigest()
check("project totals", totals["record"] == "totals" and totals["functions"] == 6376
      and totals["instructions"] == 183240 and totals["memory_blocks"] == 14)
check("inventory hash published", inventory_sha in text, inventory_sha)

outside = json.loads((REPO / "data/outside_function_summary.json").read_text())
check("outside-function totals", outside["candidate_count"] == 1665
      and outside["decoded_instruction_count"] == 17147
      and outside["decoded_byte_count"] == 48164)
check("outside-function classes", outside["candidate_class_counts"]
      == {"orphan-decoded-run": 703, "pointer-referenced-code-run": 962})
check("outside-function adjudication", outside["adjudication_state_counts"]
      == {"unresolved": 1605, "unresolved-reviewed": 60})

table_specs = [
    (0x2B3F0, 7, 8, (4,)), (0x22C30, 18, 4, (0,)),
    (0x25804, 19, 12, (4, 8)),
    (0x2941C, 242, 16, (4,)),
    (0x28098, 10, 16, (8, 12)), (0x26CCC, 8, 4, (0,)),
    (0x26CEC, 45, 4, (0,)), (0x26DA0, 9, 4, (0,)),
    (0x26218, 6, 28, (0,)),
    (0x28524, 1, 52, tuple(range(0, 52, 4))),
    (0x28558, 28, 12, (0, 4, 8)),
    (0x286D0, 1, 52, tuple(range(0, 52, 4))),
]
blob = code.read_bytes()
pointer_count = sum(
    struct.unpack_from("<I", blob, base + index * stride + offset)[0] != 0
    for base, count, stride, offsets in table_specs
    for index in range(count) for offset in offsets
)
check("dispatch-proven table denominator", len(table_specs) == 12 and pointer_count == 456)
check("dispatch denominator published", "12 tables / 456 nonzero target pointers" in text)

summary = json.loads((REPO / "data/semantic_coverage_summary.json").read_text())
check("semantic review totals", summary["function_count"] == 6376
      and summary["reviewed_function_count"] == 110
      and summary["bounded_semantics_count"] == 22)
check("semantic state totals", summary["review_state_counts"] == {
    "reviewed_unknown": 88, "semantically_identified": 19,
    "structurally_bounded": 3, "unreviewed": 6266,
})
check("semantic grade totals", summary["evidence_grade_counts"]
      == {"bounded": 3, "recovered": 11, "verified": 8})
check("execution totals explicit", summary["execution_status_counts"]
      == {"passed": 105, "unavailable": 5})

with (REPO / "data/generated/semantic_interest_ranking.csv").open(newline="") as stream:
    selected = [row for row in csv.DictReader(stream) if row["selected_for_sweep"] == "true"]
check("selected sweep denominator", len(selected) == 100)

priority = json.loads((REPO / "data/generated/techstream_v18/priority_steering_ddb_semantics.json").read_text())
check("priority semantic denominator", len(priority["schemas"]) == 11
      and priority["summary"] == {
          "steering_files_with_priority_sections": 32,
          "section_instances": 76, "decoded_records": 6521,
      })
lock = json.loads((REPO / "techstream.lock.json").read_text())
check("Techstream locked denominator", len(lock["artifacts"]) == 45)

verified_findings = []
observed_findings = []
grade_index = None
for line in (REPO / "docs/status/FINDINGS.md").read_text(encoding="utf-8").splitlines():
    if line.startswith("| ID |"):
        header = [cell.strip() for cell in line.strip("|").split("|")]
        grade_index = header.index("Grade")
    elif grade_index is not None and line.startswith("| ") and not line.startswith("|---"):
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if len(cells) > grade_index:
            grade = cells[grade_index]
            if grade == "verified":
                verified_findings.append(cells[0])
            if grade.startswith("observed"):
                observed_findings.append(cells[0])
check("exact verified finding denominator", len(verified_findings) == 57)
check("dynamic observation denominator", observed_findings == ["SECOC-030", "VAR-001"])

required_tokens = [
    "105 `passed`, 5 `unavailable`, 0 `failed`",
    "Live official Techstream↔`8965B4512000` flows captured | 0",
    "Exact cross-variant/target-generation transfers verified | 0",
]
check("blocked and execution dimensions published", all(token in text for token in required_tokens))

print(f"\nSummary: {passed} passed, {failed} failed")
raise SystemExit(1 if failed else 0)
