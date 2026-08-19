#!/usr/bin/env python3
"""Compare canonical RH850 function bodies against a foreign CodeFlash image.

This is a firmware-byte comparison, not a semantic matcher.  It uses the
canonical Sienna Ghidra function inventory only to define reference function
body ranges, then proves exact transfer from raw bytes wherever possible.

For each reference function:

* ``exact-same-va`` means every reference body range is byte-identical at the
  same target virtual address.
* ``exact-unique-relocated`` means all body ranges are byte-identical after one
  unique constant address shift.  The longest body range is used only as a
  search anchor; every range is verified at that same shift.
* ``exact-ambiguous`` means multiple shifts reproduce the complete body and no
  unique target address can be assigned.
* ``changed-or-absent`` means no exact complete-body transfer was found.
* bodies whose longest range is shorter than the configured exact-search floor
  are not searched globally because tiny instruction sequences are frequently
  duplicated.

For non-exact bodies, the report may include a *candidate* target address inferred
from neighboring exact functions.  Candidate byte-similarity is useful triage,
but it is deliberately not promoted to semantic homology.  Decompile/disassemble
and prove any material transferred behavior against the foreign firmware before
recording it as a finding.

The target may be a bare 1 MiB CodeFlash image or the repository-supported 2 MiB
range-dumper shape whose upper 1 MiB is all 0xFF.
"""

from __future__ import annotations

import argparse
import bisect
import collections
import hashlib
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from tools.build_ephemeral_runtime_manifest import load_codeflash  # noqa: E402

SCHEMA = "rh850-cross-image-function-body-transfer-v1"
MIN_GLOBAL_EXACT_BYTES = 8
ANCHOR_MIN_BODY_BYTES = 16
BRACKET_MAX_DISTANCE = 0x10000
NEAREST_MAX_DISTANCE = 0x4000
MAX_EXACT_MATCHES_RECORDED = 32


@dataclass(frozen=True)
class BodyRange:
    start: int
    end: int  # exclusive

    @property
    def size(self) -> int:
        return self.end - self.start


@dataclass(frozen=True)
class ReferenceFunction:
    entry: int
    name: str | None
    ranges: tuple[BodyRange, ...]
    body_size: int


@dataclass(frozen=True)
class ExactAnchor:
    reference_entry: int
    target_entry: int
    delta: int
    body_size: int
    name: str | None


def sha256(blob: bytes) -> str:
    return hashlib.sha256(blob).hexdigest()


def _address(value: int | None) -> str | None:
    return None if value is None else f"0x{value:08X}"


def _signed_hex(value: int) -> str:
    return ("+" if value >= 0 else "-") + f"0x{abs(value):X}"


def load_reference_functions(path: Path, image_size: int) -> list[ReferenceFunction]:
    functions: list[ReferenceFunction] = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            record = json.loads(line)
            if record.get("record") != "function":
                continue
            entry_obj = record.get("entry") or {}
            if entry_obj.get("space") != "ram":
                continue
            entry = int(entry_obj["offset"], 16)
            ranges: list[BodyRange] = []
            outside = False
            for item in record.get("body_ranges", []):
                lo = item["min"]
                hi = item["max"]
                if lo.get("space") != "ram" or hi.get("space") != "ram":
                    outside = True
                    break
                start = int(lo["offset"], 16)
                end = int(hi["offset"], 16) + 1
                if start < 0 or end > image_size:
                    outside = True
                    break
                ranges.append(BodyRange(start, end))
            if outside or not ranges or entry >= image_size:
                continue
            functions.append(
                ReferenceFunction(
                    entry=entry,
                    name=record.get("user_name"),
                    ranges=tuple(ranges),
                    body_size=sum(r.size for r in ranges),
                )
            )
    functions.sort(key=lambda row: row.entry)
    return functions


def body_matches_at_delta(
    reference: bytes,
    target: bytes,
    function: ReferenceFunction,
    delta: int,
) -> bool:
    for body_range in function.ranges:
        target_start = body_range.start + delta
        target_end = body_range.end + delta
        if target_start < 0 or target_end > len(target):
            return False
        if reference[body_range.start : body_range.end] != target[target_start:target_end]:
            return False
    return True


def occurrence_offsets(blob: bytes, needle: bytes, limit: int) -> list[int]:
    out: list[int] = []
    pos = 0
    while len(out) < limit:
        hit = blob.find(needle, pos)
        if hit < 0:
            break
        out.append(hit)
        pos = hit + 1
    return out


def exact_transfer(
    reference: bytes,
    target: bytes,
    function: ReferenceFunction,
) -> dict[str, Any]:
    if body_matches_at_delta(reference, target, function, 0):
        return {
            "classification": (
                "same-va-small-exact"
                if max(r.size for r in function.ranges) < MIN_GLOBAL_EXACT_BYTES
                else "exact-same-va"
            ),
            "target_entry": function.entry,
            "delta": 0,
            "exact_shift_count": 1,
            "search_anchor_size": max(r.size for r in function.ranges),
        }

    longest = max(function.ranges, key=lambda r: (r.size, -r.start))
    if longest.size < MIN_GLOBAL_EXACT_BYTES:
        return {
            "classification": "too-small-for-global-exact-search",
            "target_entry": None,
            "delta": None,
            "exact_shift_count": None,
            "search_anchor_size": longest.size,
        }

    needle = reference[longest.start : longest.end]
    hits = occurrence_offsets(target, needle, MAX_EXACT_MATCHES_RECORDED + 1)
    candidate_deltas: set[int] = set()
    for hit in hits:
        delta = hit - longest.start
        if body_matches_at_delta(reference, target, function, delta):
            candidate_deltas.add(delta)

    if len(candidate_deltas) == 1:
        delta = next(iter(candidate_deltas))
        return {
            "classification": "exact-unique-relocated",
            "target_entry": function.entry + delta,
            "delta": delta,
            "exact_shift_count": 1,
            "search_anchor_size": longest.size,
        }
    if len(candidate_deltas) > 1:
        shifts = sorted(candidate_deltas)
        return {
            "classification": "exact-ambiguous",
            "target_entry": None,
            "delta": None,
            "exact_shift_count": len(shifts),
            "exact_candidate_deltas": shifts[:MAX_EXACT_MATCHES_RECORDED],
            "search_anchor_size": longest.size,
        }
    return {
        "classification": "changed-or-absent",
        "target_entry": None,
        "delta": None,
        "exact_shift_count": 0,
        "search_anchor_size": longest.size,
    }


def neighboring_alignment(
    entry: int,
    anchors: list[ExactAnchor],
    anchor_entries: list[int],
) -> tuple[int, str, int] | None:
    if not anchors:
        return None
    index = bisect.bisect_left(anchor_entries, entry)
    previous = anchors[index - 1] if index else None
    following = anchors[index] if index < len(anchors) else None

    if previous and following and previous.delta == following.delta:
        left_distance = entry - previous.reference_entry
        right_distance = following.reference_entry - entry
        if left_distance <= BRACKET_MAX_DISTANCE and right_distance <= BRACKET_MAX_DISTANCE:
            return previous.delta, "bracketed-by-exact-same-delta", max(left_distance, right_distance)

    nearest: list[tuple[int, ExactAnchor]] = []
    if previous:
        nearest.append((abs(entry - previous.reference_entry), previous))
    if following:
        nearest.append((abs(following.reference_entry - entry), following))
    if not nearest:
        return None
    distance, anchor = min(nearest, key=lambda row: (row[0], row[1].reference_entry))
    if distance <= NEAREST_MAX_DISTANCE:
        return anchor.delta, "nearest-exact-anchor", distance
    return None


def alignment_candidate(
    reference: bytes,
    target: bytes,
    function: ReferenceFunction,
    anchors: list[ExactAnchor],
    anchor_entries: list[int],
) -> dict[str, Any] | None:
    inferred = neighboring_alignment(function.entry, anchors, anchor_entries)
    if inferred is None:
        return None
    delta, basis, distance = inferred
    target_entry = function.entry + delta
    changed_bytes = 0
    compared_bytes = 0
    changed_halfwords = 0
    compared_halfwords = 0

    for body_range in function.ranges:
        target_start = body_range.start + delta
        target_end = body_range.end + delta
        if target_start < 0 or target_end > len(target):
            return None
        ref_bytes = reference[body_range.start : body_range.end]
        target_bytes = target[target_start:target_end]
        changed_bytes += sum(a != b for a, b in zip(ref_bytes, target_bytes))
        compared_bytes += len(ref_bytes)
        halfword_length = len(ref_bytes) - (len(ref_bytes) % 2)
        for off in range(0, halfword_length, 2):
            compared_halfwords += 1
            if ref_bytes[off : off + 2] != target_bytes[off : off + 2]:
                changed_halfwords += 1

    byte_equal_ratio = 1.0 - changed_bytes / compared_bytes if compared_bytes else 0.0
    halfword_equal_ratio = (
        1.0 - changed_halfwords / compared_halfwords if compared_halfwords else None
    )
    if byte_equal_ratio >= 0.95:
        quality = "very-high-byte-similarity"
    elif byte_equal_ratio >= 0.85:
        quality = "high-byte-similarity"
    elif byte_equal_ratio >= 0.60:
        quality = "moderate-byte-similarity"
    else:
        quality = "low-byte-similarity"

    return {
        "target_entry": target_entry,
        "delta": delta,
        "basis": basis,
        "max_reference_anchor_distance": distance,
        "compared_bytes": compared_bytes,
        "changed_bytes": changed_bytes,
        "byte_equal_ratio": round(byte_equal_ratio, 6),
        "compared_halfwords": compared_halfwords,
        "changed_halfwords": changed_halfwords,
        "halfword_equal_ratio": (
            None if halfword_equal_ratio is None else round(halfword_equal_ratio, 6)
        ),
        "quality": quality,
        "evidence_boundary": (
            "triage candidate only; neighboring exact relocation plus byte similarity does "
            "not prove function boundaries, control flow, or semantic homology"
        ),
    }


def relocation_clusters(rows: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    buckets: dict[int, list[dict[str, Any]]] = collections.defaultdict(list)
    for row in rows:
        if row["classification"] not in {"exact-same-va", "exact-unique-relocated"}:
            continue
        if row["body_size"] < ANCHOR_MIN_BODY_BYTES:
            continue
        delta = row.get("delta_decimal")
        if delta is None:
            continue
        buckets[int(delta)].append(row)

    clusters: list[dict[str, Any]] = []
    for delta, items in buckets.items():
        reference_entries = [int(row["reference_entry"], 16) for row in items]
        target_entries = [int(row["target_entry"], 16) for row in items]
        named = [row for row in items if row.get("name")]
        clusters.append(
            {
                "delta": _signed_hex(delta),
                "delta_decimal": delta,
                "function_count": len(items),
                "named_function_count": len(named),
                "exact_body_bytes": sum(row["body_size"] for row in items),
                "reference_min_entry": _address(min(reference_entries)),
                "reference_max_entry": _address(max(reference_entries)),
                "target_min_entry": _address(min(target_entries)),
                "target_max_entry": _address(max(target_entries)),
                "named_examples": [
                    {
                        "name": row["name"],
                        "reference_entry": row["reference_entry"],
                        "target_entry": row["target_entry"],
                    }
                    for row in named[:12]
                ],
            }
        )
    clusters.sort(key=lambda row: (-row["function_count"], row["delta_decimal"]))
    return clusters


def summarize_classes(rows: Iterable[dict[str, Any]]) -> dict[str, int]:
    counts: collections.Counter[str] = collections.Counter()
    for row in rows:
        counts[row["classification"]] += 1
    return dict(sorted(counts.items()))


def summarize_candidate_quality(rows: Iterable[dict[str, Any]]) -> dict[str, int]:
    counts: collections.Counter[str] = collections.Counter()
    for row in rows:
        candidate = row.get("alignment_candidate")
        if candidate:
            counts[candidate["quality"]] += 1
    return dict(sorted(counts.items()))


def compare(
    reference_image: bytes,
    reference_inventory: Path,
    target_image: bytes,
    *,
    target_source: dict[str, Any],
    reference_id: str,
    target_id: str,
) -> dict[str, Any]:
    functions = load_reference_functions(reference_inventory, len(reference_image))
    rows: list[dict[str, Any]] = []

    for function in functions:
        exact = exact_transfer(reference_image, target_image, function)
        row: dict[str, Any] = {
            "reference_entry": _address(function.entry),
            "name": function.name,
            "body_size": function.body_size,
            "body_range_count": len(function.ranges),
            "body_ranges": [
                {"start": _address(r.start), "end_exclusive": _address(r.end), "size": r.size}
                for r in function.ranges
            ],
            "classification": exact["classification"],
            "target_entry": _address(exact.get("target_entry")),
            "delta": (
                None if exact.get("delta") is None else _signed_hex(int(exact["delta"]))
            ),
            "delta_decimal": exact.get("delta"),
            "exact_shift_count": exact.get("exact_shift_count"),
            "search_anchor_size": exact.get("search_anchor_size"),
        }
        if "exact_candidate_deltas" in exact:
            row["exact_candidate_deltas"] = [
                _signed_hex(int(delta)) for delta in exact["exact_candidate_deltas"]
            ]
        rows.append(row)

    anchors = [
        ExactAnchor(
            reference_entry=int(row["reference_entry"], 16),
            target_entry=int(row["target_entry"], 16),
            delta=int(row["delta_decimal"]),
            body_size=int(row["body_size"]),
            name=row.get("name"),
        )
        for row in rows
        if row["classification"] in {"exact-same-va", "exact-unique-relocated"}
        and row["body_size"] >= ANCHOR_MIN_BODY_BYTES
        and row.get("target_entry") is not None
        and row.get("delta_decimal") is not None
    ]
    anchors.sort(key=lambda row: row.reference_entry)
    anchor_entries = [row.reference_entry for row in anchors]

    by_entry = {function.entry: function for function in functions}
    for row in rows:
        if row["classification"] in {"exact-same-va", "exact-unique-relocated"}:
            continue
        function = by_entry[int(row["reference_entry"], 16)]
        candidate = alignment_candidate(
            reference_image,
            target_image,
            function,
            anchors,
            anchor_entries,
        )
        if candidate is not None:
            candidate = dict(candidate)
            candidate["target_entry"] = _address(int(candidate["target_entry"]))
            candidate["delta"] = _signed_hex(int(candidate["delta"]))
            del candidate["max_reference_anchor_distance"]
            # Reinsert the distance after converting to an explicit integer name;
            # keeping the machine field integer makes thresholds easy to audit.
            inferred = neighboring_alignment(function.entry, anchors, anchor_entries)
            assert inferred is not None
            candidate["max_reference_anchor_distance_bytes"] = inferred[2]
            row["alignment_candidate"] = candidate

    named_rows = [row for row in rows if row.get("name")]
    exact_proven = sum(
        1
        for row in rows
        if row["classification"] in {"exact-same-va", "exact-unique-relocated"}
    )
    named_exact_proven = sum(
        1
        for row in named_rows
        if row["classification"] in {"exact-same-va", "exact-unique-relocated"}
    )
    return {
        "schema": SCHEMA,
        "evidence_boundary": (
            "Exact classes are raw-byte transfer proofs for the reference Ghidra-defined "
            "body ranges only. They do not by themselves prove callers, data tables, runtime "
            "reachability, or unchanged semantics outside those bytes. Alignment candidates "
            "are triage only and require foreign-image disassembly/decompilation before use."
        ),
        "reference": {
            "id": reference_id,
            "codeflash_sha256": sha256(reference_image),
            "codeflash_size": len(reference_image),
            "inventory": reference_inventory.name,
        },
        "target": {
            "id": target_id,
            "normalized_codeflash_sha256": sha256(target_image),
            "normalized_codeflash_size": len(target_image),
            "source_sha256": target_source.get("sha256"),
            "source_size": target_source.get("size"),
            "normalization": target_source.get("normalization"),
        },
        "method": {
            "minimum_global_exact_search_bytes": MIN_GLOBAL_EXACT_BYTES,
            "exact_relocation_anchor_minimum_body_bytes": ANCHOR_MIN_BODY_BYTES,
            "bracket_alignment_max_distance_bytes": BRACKET_MAX_DISTANCE,
            "nearest_alignment_max_distance_bytes": NEAREST_MAX_DISTANCE,
            "candidate_similarity_is_semantic_proof": False,
        },
        "summary": {
            "reference_codeflash_functions": len(rows),
            "named_reference_functions": len(named_rows),
            "exact_body_transfer_proven_functions": exact_proven,
            "exact_body_transfer_proven_fraction": round(exact_proven / len(rows), 6),
            "named_exact_body_transfer_proven_functions": named_exact_proven,
            "named_exact_body_transfer_proven_fraction": round(
                named_exact_proven / len(named_rows), 6
            ),
            "classification_counts": summarize_classes(rows),
            "named_classification_counts": summarize_classes(named_rows),
            "alignment_candidate_quality_counts": summarize_candidate_quality(rows),
            "named_alignment_candidate_quality_counts": summarize_candidate_quality(named_rows),
            "exact_relocation_anchor_count": len(anchors),
        },
        "relocation_clusters": relocation_clusters(rows),
        "functions": rows,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reference-image", type=Path, required=True)
    parser.add_argument("--reference-inventory", type=Path, required=True)
    parser.add_argument("--target-image", type=Path, required=True)
    parser.add_argument("--reference-id", default="reference")
    parser.add_argument("--target-id", default="target")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    reference_image = args.reference_image.read_bytes()
    target_image, target_source = load_codeflash(args.target_image)
    report = compare(
        reference_image,
        args.reference_inventory,
        target_image,
        target_source=target_source,
        reference_id=args.reference_id,
        target_id=args.target_id,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "output": str(args.output),
                "summary": report["summary"],
                "top_relocation_clusters": report["relocation_clusters"][:10],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
