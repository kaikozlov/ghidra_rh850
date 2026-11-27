#!/usr/bin/env python3
"""Match cross-variant functions by instruction shape and matched call context.

Inputs are JSONL files emitted by ``ExportFunctionStructuralFingerprints.java``.
Initial matches require one function on each side with the same complete
mnemonic and instruction-length sequence. Repeated shapes resolve only when
already-final caller/callee pairs leave one reciprocal best candidate; all ties
fail closed.
"""

from __future__ import annotations

import argparse
import collections
import hashlib
import json
from collections.abc import Iterable
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


CONTEXT_SCORE_MARGIN = 1


def _call_graph(
    rows: list[dict[str, Any]],
) -> tuple[
    dict[int, collections.Counter[int]],
    dict[int, collections.Counter[int]],
]:
    entries = {row["entry_int"] for row in rows}
    outgoing = {entry: collections.Counter() for entry in entries}
    incoming = {entry: collections.Counter() for entry in entries}
    for row in rows:
        source = row["entry_int"]
        call_sites = row.get("direct_call_sites")
        if call_sites is None:
            call_sites = row.get("direct_call_targets", ())
        for raw_target in call_sites:
            target = int(raw_target, 16)
            if target not in entries:
                continue
            outgoing[source][target] += 1
            incoming[target][source] += 1
    return outgoing, incoming


def _context_score(
    reference_entry: int,
    target_entry: int,
    resolved: dict[int, int],
    reference_outgoing: dict[int, collections.Counter[int]],
    reference_incoming: dict[int, collections.Counter[int]],
    target_outgoing: dict[int, collections.Counter[int]],
    target_incoming: dict[int, collections.Counter[int]],
) -> int:
    score = 0
    for neighbor, multiplicity in reference_outgoing[reference_entry].items():
        matched_neighbor = resolved.get(neighbor)
        if matched_neighbor is not None:
            score += min(multiplicity, target_outgoing[target_entry][matched_neighbor])
    for neighbor, multiplicity in reference_incoming[reference_entry].items():
        matched_neighbor = resolved.get(neighbor)
        if matched_neighbor is not None:
            score += min(multiplicity, target_incoming[target_entry][matched_neighbor])
    return score


def _best_context(candidates: Iterable[tuple[int, int]]) -> tuple[int, int, int] | None:
    best_entry = best_score = second_score = 0
    for entry, score in candidates:
        if score > best_score:
            best_entry, best_score, second_score = entry, score, best_score
        elif score > second_score:
            second_score = score
    margin = best_score - second_score
    if margin < CONTEXT_SCORE_MARGIN:
        return None
    return best_entry, best_score, margin


def _match_row(
    reference: dict[str, Any],
    target: dict[str, Any],
    classification: str,
    *,
    context_round: int | None = None,
    context_score: int | None = None,
    context_margin: int | None = None,
) -> dict[str, Any]:
    delta = target["entry_int"] - reference["entry_int"]
    result = {
        "classification": classification,
        "reference_entry": reference["entry_addr"],
        "reference_name": reference.get("name"),
        "target_entry": target["entry_addr"],
        "target_name": target.get("name"),
        "delta": ("+" if delta >= 0 else "-") + f"0x{abs(delta):X}",
        "delta_decimal": delta,
        "body_size_reference": reference["body_size"],
        "body_size_target": target["body_size"],
        "instruction_count": reference["instruction_count"],
        "conditional_branch_count": reference["conditional_branch_count"],
        "unconditional_branch_count": reference["unconditional_branch_count"],
        "direct_call_target_count_reference": reference["direct_call_target_count"],
        "direct_call_target_count_target": target["direct_call_target_count"],
        "indirect_call_count_reference": reference["indirect_call_count"],
        "indirect_call_count_target": target["indirect_call_count"],
        "return_count_reference": reference["return_count"],
        "return_count_target": target["return_count"],
    }
    if context_round is not None:
        result.update(
            {
                "context_round": context_round,
                "context_score": context_score,
                "context_margin": context_margin,
            }
        )
    return result


def match(reference_path: Path, target_path: Path) -> dict[str, Any]:
    reference = _load(reference_path)
    target = _load(target_path)
    reference_by_sig: dict[tuple[Any, ...], list[dict[str, Any]]] = collections.defaultdict(list)
    target_by_sig: dict[tuple[Any, ...], list[dict[str, Any]]] = collections.defaultdict(list)
    reference_by_entry = {row["entry_int"]: row for row in reference}
    target_by_entry = {row["entry_int"]: row for row in target}
    for row in reference:
        reference_by_sig[_signature(row)].append(row)
    for row in target:
        target_by_sig[_signature(row)].append(row)

    unique_matches: list[dict[str, Any]] = []
    resolved: dict[int, int] = {}
    used_targets: set[int] = set()
    for signature, reference_rows in reference_by_sig.items():
        target_rows = target_by_sig.get(signature, [])
        if len(reference_rows) != 1 or len(target_rows) != 1:
            continue
        ref = reference_rows[0]
        tgt = target_rows[0]
        resolved[ref["entry_int"]] = tgt["entry_int"]
        used_targets.add(tgt["entry_int"])
        unique_matches.append(_match_row(ref, tgt, "unique-exact-shape"))

    ambiguous_signatures = [
        signature
        for signature, reference_rows in reference_by_sig.items()
        if target_by_sig.get(signature)
        and (len(reference_rows) != 1 or len(target_by_sig[signature]) != 1)
    ]
    ambiguous_reference_count = sum(
        len(reference_by_sig[signature]) for signature in ambiguous_signatures
    )
    reference_outgoing, reference_incoming = _call_graph(reference)
    target_outgoing, target_incoming = _call_graph(target)

    context_matches: list[dict[str, Any]] = []
    context_round = 0
    while True:
        context_round += 1
        accepted: list[tuple[int, int, int, int]] = []
        for signature in ambiguous_signatures:
            reference_entries = [
                row["entry_int"]
                for row in reference_by_sig[signature]
                if row["entry_int"] not in resolved
            ]
            target_entries = [
                row["entry_int"]
                for row in target_by_sig[signature]
                if row["entry_int"] not in used_targets
            ]
            if not reference_entries or not target_entries:
                continue

            scores = {
                (reference_entry, target_entry): _context_score(
                    reference_entry,
                    target_entry,
                    resolved,
                    reference_outgoing,
                    reference_incoming,
                    target_outgoing,
                    target_incoming,
                )
                for reference_entry in reference_entries
                for target_entry in target_entries
            }
            reference_best: dict[int, tuple[int, int, int]] = {}
            for reference_entry in reference_entries:
                best = _best_context(
                    (target_entry, scores[reference_entry, target_entry])
                    for target_entry in target_entries
                )
                if best is not None:
                    reference_best[reference_entry] = best

            target_best: dict[int, int] = {}
            for target_entry in target_entries:
                best = _best_context(
                    (reference_entry, scores[reference_entry, target_entry])
                    for reference_entry in reference_entries
                )
                if best is not None:
                    target_best[target_entry] = best[0]

            for reference_entry, (target_entry, score, margin) in reference_best.items():
                if target_best.get(target_entry) == reference_entry:
                    accepted.append((reference_entry, target_entry, score, margin))

        if not accepted:
            break
        for reference_entry, target_entry, score, margin in accepted:
            resolved[reference_entry] = target_entry
            used_targets.add(target_entry)
            context_matches.append(
                _match_row(
                    reference_by_entry[reference_entry],
                    target_by_entry[target_entry],
                    "context-exact-shape",
                    context_round=context_round,
                    context_score=score,
                    context_margin=margin,
                )
            )

    deltas: collections.Counter[int] = collections.Counter(
        row["delta_decimal"] for row in unique_matches if row["instruction_count"] >= 8
    )
    named = [row for row in unique_matches if _is_named(row.get("reference_name"))]
    named8 = [row for row in named if row["instruction_count"] >= 8]
    named_context = [
        row for row in context_matches if _is_named(row.get("reference_name"))
    ]
    return {
        "schema": SCHEMA,
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
            "unique_exact_shape_matches": len(unique_matches),
            "unique_exact_shape_matches_min_8_instructions": sum(
                row["instruction_count"] >= 8 for row in unique_matches
            ),
            "named_unique_exact_shape_matches": len(named),
            "named_unique_exact_shape_matches_min_8_instructions": len(named8),
            "ambiguous_reference_functions": ambiguous_reference_count,
            "context_resolved_matches": len(context_matches),
            "context_resolved_named_matches": len(named_context),
            "context_rounds": context_round - 1,
            "ambiguous_reference_functions_dropped": (
                ambiguous_reference_count - len(context_matches)
            ),
            "context_score_margin": CONTEXT_SCORE_MARGIN,
            "top_relocation_deltas_min_8_instructions": [
                {
                    "delta": ("+" if delta >= 0 else "-") + f"0x{abs(delta):X}",
                    "delta_decimal": delta,
                    "function_count": count,
                }
                for delta, count in deltas.most_common(32)
            ],
        },
        "matches": unique_matches,
        "context_matches": context_matches,
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
