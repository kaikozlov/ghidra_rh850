#!/usr/bin/env python3
"""Verify conservative cross-variant structural-function matching semantics."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

from tools import REPO_ROOT
REPO = REPO_ROOT

from tools.variants.match_variant_function_structure import match  # noqa: E402

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
    call_sites: list[int] | None = None,
    cond: int = 0,
) -> dict[str, object]:
    call_targets = sorted(set(call_sites or ()))
    return {
        "record": "function-structural-fingerprint",
        "entry_addr": f"0x{entry:08x}",
        "address_space": "ram",
        "name": name,
        "body_size": sum(int(x) for x in lengths),
        "instruction_count": len(mnemonics),
        "mnemonics": mnemonics,
        "instruction_lengths": lengths,
        "direct_call_targets": [
            f"0x{target:08x}" for target in call_targets
        ],
        "direct_call_sites": [f"0x{target:08x}" for target in call_sites or ()],
        "direct_call_target_count": len(call_targets),
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
            row(0x1000, "named_a", ["mov", "add", "cmp", "bnz", "jmp"], ["4", "2", "2", "2", "4"], cond=1),
            row(0x2000, "named_b", ["ld.w", "xor", "st.w", "jmp"], ["4", "2", "4", "4"]),
            row(0x3000, "named_c", ["mov", "shl", "jmp"], ["4", "2", "4"]),
            row(0x4000, "named_d1", ["mov", "satadd", "jmp"], ["4", "2", "4"]),
            row(0x4100, "named_d2", ["mov", "satadd", "jmp"], ["4", "2", "4"]),
        ],
    )
    write_jsonl(
        target,
        [
            row(0x1800, "FUN_00001800", ["mov", "add", "cmp", "bnz", "jmp"], ["4", "2", "2", "2", "4"], cond=1),
            row(0x2800, "FUN_00002800", ["ld.w", "xor", "st.w", "jmp"], ["4", "2", "4", "4"]),
            row(0x2900, "FUN_00002900", ["ld.w", "xor", "st.w", "jmp"], ["4", "2", "4", "4"]),
            row(0x3800, "FUN_00003800", ["mov", "shl", "jmp"], ["4", "4", "4"]),
            row(0x4800, "FUN_00004800", ["mov", "satadd", "jmp"], ["4", "2", "4"]),
        ],
    )

    report = match(reference, target)
    matches = report["matches"]

with tempfile.TemporaryDirectory() as tmp:
    root = Path(tmp)
    reference = root / "reference-context.jsonl"
    target = root / "target-context.jsonl"
    duplicate_shape = (["ld.w", "xor", "st.w", "jmp"], ["4", "2", "4", "4"])
    dependent_shape = (["mov", "add", "st.w", "jmp"], ["4", "2", "4", "4"])
    tied_shape = (["mov", "cmp", "setf", "jmp"], ["4", "2", "2", "4"])
    write_jsonl(
        reference,
        [
            row(0x1000, "anchor_a", ["mov", "jmp"], ["4", "4"]),
            row(0x1100, "anchor_b", ["mov", "add", "jmp"], ["4", "2", "4"]),
            row(0x2000, "context_a", *duplicate_shape, call_sites=[0x1000, 0x1000]),
            row(0x2100, "context_b", *duplicate_shape, call_sites=[0x1100]),
            row(0x3000, "dependent_a", *dependent_shape, call_sites=[0x2000]),
            row(0x3100, "dependent_b", *dependent_shape, call_sites=[0x2100]),
            row(0x4000, "tied_a", *tied_shape, call_sites=[0x1000]),
            row(0x4100, "tied_b", *tied_shape, call_sites=[0x1000]),
        ],
    )
    write_jsonl(
        target,
        [
            row(0x1800, "FUN_00001800", ["mov", "jmp"], ["4", "4"]),
            row(0x1900, "FUN_00001900", ["mov", "add", "jmp"], ["4", "2", "4"]),
            row(0x2800, "FUN_00002800", *duplicate_shape, call_sites=[0x1900]),
            row(0x2900, "FUN_00002900", *duplicate_shape, call_sites=[0x1800, 0x1800]),
            row(0x3800, "FUN_00003800", *dependent_shape, call_sites=[0x2800]),
            row(0x3900, "FUN_00003900", *dependent_shape, call_sites=[0x2900]),
            row(0x4800, "FUN_00004800", *tied_shape, call_sites=[0x1800]),
            row(0x4900, "FUN_00004900", *tied_shape, call_sites=[0x1800]),
        ],
    )
    context_report = match(reference, target)
    context_matches = {
        item["reference_entry"]: item
        for item in context_report["context_matches"]
    }

print("== iterative context ==")
check(
    "multiplicity resolves context_a",
    context_matches["0x00002000"]["target_entry"] == "0x00002900"
    and context_matches["0x00002000"]["context_score"] == 2,
)
check(
    "other duplicate resolves reciprocally",
    context_matches["0x00002100"]["target_entry"] == "0x00002800",
)
check(
    "new matches seed a later round",
    context_matches["0x00003000"]["target_entry"] == "0x00003900"
    and context_matches["0x00003000"]["context_round"] == 2,
)
check(
    "equally supported candidates remain unmatched",
    "0x00004000" not in context_matches and "0x00004100" not in context_matches,
)

print("== uniqueness and evidence boundary ==")
check("only one shape is unique on both sides", len(matches) == 1, repr(matches))
check("unique shape maps A 0x1000 -> 0x1800", matches[0]["reference_entry"] == "0x00001000" and matches[0]["target_entry"] == "0x00001800")
check("relocation is represented exactly", matches[0]["delta"] == "+0x800" and matches[0]["delta_decimal"] == 0x800)
check("target-duplicated B fails closed", all(item["reference_name"] != "named_b" for item in matches))
check("instruction-length-changed C does not match", all(item["reference_name"] != "named_c" for item in matches))
check("reference-duplicated D fails closed", all(not str(item["reference_name"]).startswith("named_d") for item in matches))

print(f"\nResults: {passed} passed, {failed} failed")
if failed:
    raise SystemExit(1)
