#!/usr/bin/env python3
"""Verify conservative cross-variant structural-function matching semantics."""

from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from tools.match_variant_function_structure import match  # noqa: E402

passed = failed = 0


def check(name: str, condition: object, detail: str = "") -> None:
    global passed, failed
    ok = bool(condition)
    passed += int(ok)
    failed += int(not ok)
    suffix = f" ({detail})" if detail else ""
    print(f"[{'PASS' if ok else 'FAIL'}] {name}{suffix}")


def row(
    entry: int,
    name: str,
    mnemonics: list[str],
    lengths: list[str],
    *,
    calls: int = 0,
    cond: int = 0,
) -> dict[str, object]:
    return {
        "record": "function-structural-fingerprint",
        "entry_addr": f"0x{entry:08x}",
        "address_space": "ram",
        "name": name,
        "body_size": sum(int(x) for x in lengths),
        "instruction_count": len(mnemonics),
        "mnemonics": mnemonics,
        "instruction_lengths": lengths,
        "direct_call_targets": [],
        "direct_call_target_count": calls,
        "indirect_call_count": 0,
        "conditional_branch_count": cond,
        "unconditional_branch_count": 0,
        "return_count": 1,
    }


def write_jsonl(path: Path, rows: list[dict[str, object]]) -> None:
    path.write_text("".join(json.dumps(item, sort_keys=True) + "\n" for item in rows), encoding="utf-8")


with tempfile.TemporaryDirectory() as tmp:
    root = Path(tmp)
    reference = root / "reference.jsonl"
    target = root / "target.jsonl"

    # A is the one legitimate unique shape. B is duplicated on the target and
    # must fail closed. C differs only in instruction lengths and therefore must
    # not match despite identical mnemonics. D is duplicated on the reference
    # and must also fail closed.
    write_jsonl(
        reference,
        [
            row(0x1000, "named_a", ["mov", "add", "cmp", "bnz", "jmp"], ["4", "2", "2", "2", "4"], calls=1, cond=1),
            row(0x2000, "named_b", ["ld.w", "xor", "st.w", "jmp"], ["4", "2", "4", "4"]),
            row(0x3000, "named_c", ["mov", "shl", "jmp"], ["4", "2", "4"]),
            row(0x4000, "named_d1", ["mov", "satadd", "jmp"], ["4", "2", "4"]),
            row(0x4100, "named_d2", ["mov", "satadd", "jmp"], ["4", "2", "4"]),
        ],
    )
    write_jsonl(
        target,
        [
            row(0x1800, "FUN_00001800", ["mov", "add", "cmp", "bnz", "jmp"], ["4", "2", "2", "2", "4"], calls=1, cond=1),
            row(0x2800, "FUN_00002800", ["ld.w", "xor", "st.w", "jmp"], ["4", "2", "4", "4"]),
            row(0x2900, "FUN_00002900", ["ld.w", "xor", "st.w", "jmp"], ["4", "2", "4", "4"]),
            row(0x3800, "FUN_00003800", ["mov", "shl", "jmp"], ["4", "4", "4"]),
            row(0x4800, "FUN_00004800", ["mov", "satadd", "jmp"], ["4", "2", "4"]),
        ],
    )

    report = match(reference, target)
    matches = report["matches"]

print("== uniqueness and evidence boundary ==")
check("schema is pinned", report["schema"] == "rh850-cross-image-structural-function-match-v1")
check("report explicitly excludes operand semantics", "operands" in report["evidence_boundary"].lower())
check("only one shape is unique on both sides", len(matches) == 1, repr(matches))
check("unique shape maps A 0x1000 -> 0x1800", matches[0]["reference_entry"] == "0x00001000" and matches[0]["target_entry"] == "0x00001800")
check("relocation is represented exactly", matches[0]["delta"] == "+0x800" and matches[0]["delta_decimal"] == 0x800)
check("target-duplicated B fails closed", all(item["reference_name"] != "named_b" for item in matches))
check("instruction-length-changed C does not match", all(item["reference_name"] != "named_c" for item in matches))
check("reference-duplicated D fails closed", all(not str(item["reference_name"]).startswith("named_d") for item in matches))

print("\n== summary accounting ==")
check("summary counts the unique pair", report["summary"]["unique_exact_shape_matches"] == 1)
check("five-instruction fixture does not enter >=8 bucket", report["summary"]["unique_exact_shape_matches_min_8_instructions"] == 0)
check("named-reference accounting includes A", report["summary"]["named_unique_exact_shape_matches"] == 1)

print(f"\nResults: {passed} passed, {failed} failed")
if failed:
    raise SystemExit(1)
