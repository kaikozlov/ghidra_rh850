#!/usr/bin/env python3
"""Match cross-variant functions by address-independent instruction shape.

Inputs are JSONL files emitted by ``ExportFunctionStructuralFingerprints.java``.
The strongest class emitted here, ``unique-exact-shape``, requires one and only
one function on *both* sides to have the same complete mnemonic sequence and
instruction-length sequence.  Operands, constants, data addresses, call targets,
and semantics are intentionally excluded from the signature, so a structural
match is a homolog *candidate*, not proof that configuration or behavior is
identical.  Material roles still require target-native disassembly/decompilation.
"""

from __future__ import annotations

import argparse
import collections
import hashlib
import json
from pathlib import Path
from typing import Any

SCHEMA = "rh850-cross-image-structural-function-match-v1"


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _load(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            row = json.loads(line)
            if row.get("record") != "function-structural-fingerprint":
                continue
            row = dict(row)
            row["entry_int"] = int(row["entry_addr"], 16)
            rows.append(row)
    rows.sort(key=lambda row: row["entry_int"])
    return rows


def _signature(row: dict[str, Any]) -> tuple[tuple[str, ...], tuple[str, ...]]:
    return tuple(row["mnemonics"]), tuple(row["instruction_lengths"])


def _is_named(name: str | None) -> bool:
    return bool(name) and not name.startswith("FUN_") and not name.startswith("thunk_FUN_")


def match(reference_path: Path, target_path: Path) -> dict[str, Any]:
    reference = _load(reference_path)
    target = _load(target_path)
    reference_by_sig: dict[tuple[Any, ...], list[dict[str, Any]]] = collections.defaultdict(list)
    target_by_sig: dict[tuple[Any, ...], list[dict[str, Any]]] = collections.defaultdict(list)
    for row in reference:
        reference_by_sig[_signature(row)].append(row)
    for row in target:
        target_by_sig[_signature(row)].append(row)

    matches: list[dict[str, Any]] = []
    for signature, reference_rows in reference_by_sig.items():
        target_rows = target_by_sig.get(signature, [])
        if len(reference_rows) != 1 or len(target_rows) != 1:
            continue
        ref = reference_rows[0]
        tgt = target_rows[0]
        delta = tgt["entry_int"] - ref["entry_int"]
        matches.append(
            {
                "classification": "unique-exact-shape",
                "reference_entry": ref["entry_addr"],
                "reference_name": ref.get("name"),
                "target_entry": tgt["entry_addr"],
                "target_name": tgt.get("name"),
                "delta": ("+" if delta >= 0 else "-") + f"0x{abs(delta):X}",
                "delta_decimal": delta,
                "body_size_reference": ref["body_size"],
                "body_size_target": tgt["body_size"],
                "instruction_count": ref["instruction_count"],
                "conditional_branch_count": ref["conditional_branch_count"],
                "unconditional_branch_count": ref["unconditional_branch_count"],
                "direct_call_target_count_reference": ref["direct_call_target_count"],
                "direct_call_target_count_target": tgt["direct_call_target_count"],
                "indirect_call_count_reference": ref["indirect_call_count"],
                "indirect_call_count_target": tgt["indirect_call_count"],
                "return_count_reference": ref["return_count"],
                "return_count_target": tgt["return_count"],
                "evidence_boundary": (
                    "complete mnemonic+instruction-length shape is unique on both sides; "
                    "operands/constants/data addresses/call targets are not part of the "
                    "signature and must be checked before semantic transfer"
                ),
            }
        )
    matches.sort(key=lambda row: int(row["reference_entry"], 16))

    deltas: collections.Counter[int] = collections.Counter(
        row["delta_decimal"] for row in matches if row["instruction_count"] >= 8
    )
    named = [row for row in matches if _is_named(row.get("reference_name"))]
    named8 = [row for row in named if row["instruction_count"] >= 8]
    return {
        "schema": SCHEMA,
        "evidence_boundary": (
            "Structural matching ignores operands by design. It is stronger than local "
            "address/byte-similarity triage for recovering function identity across relocation "
            "and data-layout changes, but it is not a proof of identical semantics or configuration."
        ),
        "reference": {
            "fingerprints": str(reference_path),
            "sha256": _sha256(reference_path),
            "function_count": len(reference),
        },
        "target": {
            "fingerprints": str(target_path),
            "sha256": _sha256(target_path),
            "function_count": len(target),
        },
        "summary": {
            "unique_exact_shape_matches": len(matches),
            "unique_exact_shape_matches_min_8_instructions": sum(
                row["instruction_count"] >= 8 for row in matches
            ),
            "named_unique_exact_shape_matches": len(named),
            "named_unique_exact_shape_matches_min_8_instructions": len(named8),
            "top_relocation_deltas_min_8_instructions": [
                {
                    "delta": ("+" if delta >= 0 else "-") + f"0x{abs(delta):X}",
                    "delta_decimal": delta,
                    "function_count": count,
                }
                for delta, count in deltas.most_common(32)
            ],
        },
        "matches": matches,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reference", type=Path, required=True)
    parser.add_argument("--target", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    report = match(args.reference, args.target)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(args.output), "summary": report["summary"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
