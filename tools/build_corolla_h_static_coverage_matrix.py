#!/usr/bin/env python3
"""Build an evidence-graded static-analysis coverage matrix for 8965H1202000.

This is a navigation/denominator artifact. It never upgrades a raw transfer
candidate merely because the canonical Sienna function has a useful name.
Coverage is promoted only by one of:
  * exact complete-body transfer;
  * a unique complete-instruction-shape target that is present in a tracked
    target-native evidence artifact;
  * an explicitly complete generated-surface recensus (currently application
    RDBI/RoutineControl and the complete steering-supervisor direct-stage set).
Everything else remains structural-only or unresolved.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import struct
from collections import Counter, defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
DID = struct.Struct("<HHIII")
RID_CB = struct.Struct("<HHII")


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def load_codeflash(path: Path) -> bytes:
    data = path.read_bytes()
    if len(data) != 0x100000:
        raise ValueError(f"expected 1 MiB CodeFlash: {path} got {len(data):#x}")
    return data


def canonical_supervisor_calls() -> set[int]:
    records = []
    for line in (REPO / "data/generated/decompilations.jsonl").read_text().splitlines():
        r = json.loads(line)
        if "entry_addr" in r:
            records.append(r)
    by_name = {r["name"]: int(r["entry_addr"], 16) for r in records}
    root = next(r for r in records if int(r["entry_addr"], 16) == 0xCB86E)
    out = set()
    for line in root["decompiled_c"].splitlines():
        match = re.search(r"\b([A-Za-z_][A-Za-z0-9_]*)\(\);", line)
        if not match:
            continue
        name = match.group(1)
        if name.startswith("FUN_"):
            out.add(int(name[4:], 16))
        elif name in by_name:
            out.add(by_name[name])
    if len(out) != 94:
        raise ValueError(f"canonical supervisor direct-stage denominator drifted: {len(out)}")
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--ledger",
        type=Path,
        default=REPO / "data/generated/corolla_8965H1202000_named_function_transfer_ledger.json",
    )
    ap.add_argument(
        "--structural",
        type=Path,
        default=REPO / "data/generated/corolla_8965H1202000_structural_function_transfer.json",
    )
    ap.add_argument(
        "--sienna-image",
        type=Path,
        default=REPO / "firmware/RH850_P1M-E_CodeFlash.bin",
    )
    ap.add_argument(
        "--out",
        type=Path,
        default=REPO / "data/generated/corolla_8965H1202000_static_coverage_matrix.json",
    )
    args = ap.parse_args()

    ledger = load_json(args.ledger)
    rows = ledger["functions"]
    structural = load_json(args.structural)
    sienna = load_codeflash(args.sienna_image)

    # Unique target->reference map from the independent structural artifact.
    target_to_reference = {
        int(r["target_entry"], 16): int(r["reference_entry"], 16)
        for r in structural["matches"]
    }

    # Every H function explicitly carried in a compact target-native evidence set.
    evidence_files = sorted((REPO / "data/generated").glob("corolla_8965H1202000_*decompiler_evidence.json"))
    evidence_target_entries: dict[int, set[str]] = defaultdict(set)
    evidence_file_hashes = {}
    for path in evidence_files:
        doc = load_json(path)
        if doc.get("software_id") != "8965H1202000":
            continue
        evidence_file_hashes[str(path.relative_to(REPO))] = sha256(path.read_bytes())
        for record in doc.get("functions", []):
            raw = record.get("entry") or record.get("entry_addr")
            if raw is None:
                continue
            evidence_target_entries[int(raw, 16)].add(str(path.relative_to(REPO)))

    evidence_reference_entries: dict[int, set[str]] = defaultdict(set)
    h_native_unpaired_count = 0
    for target, owners in evidence_target_entries.items():
        reference = target_to_reference.get(target)
        if reference is None:
            h_native_unpaired_count += 1
            continue
        evidence_reference_entries[reference].update(owners)

    # Explicit generated-surface recensuses. These are not function homology:
    # they prove the foreign generated surface was exhaustively re-enumerated.
    recensus: dict[int, set[str]] = defaultdict(set)

    # Sienna application RDBI producers: complete foreign RDBI producer recensus exists.
    for i in range(242):
        _did, _length, callback, _aux, _tail = DID.unpack_from(sienna, 0x2941C + i * DID.size)
        if callback:
            recensus[callback].add("application-rdbi-complete-producer-recensus")

    # Sienna RoutineControl precondition/action callbacks: complete 19-RID H recensus exists.
    for i in range(19):
        _rid, _pad, precondition, action = RID_CB.unpack_from(sienna, 0x25804 + i * RID_CB.size)
        if precondition:
            recensus[precondition].add("application-routinecontrol-complete-callback-recensus")
        if action:
            recensus[action].add("application-routinecontrol-complete-callback-recensus")

    # Every canonical direct steering-supervisor stage has an explicit row in the 94->123 ledger.
    for entry in canonical_supervisor_calls():
        recensus[entry].add("steering-supervisor-complete-direct-stage-ledger")

    # Classify each canonical named function conservatively.
    classified = []
    for row in rows:
        ref = int(row["reference_entry"], 16)
        status = row["status"]
        target = row.get("target_entry")
        target_int = int(target, 16) if target else None
        owners = sorted(evidence_reference_entries.get(ref, set()))
        census = sorted(recensus.get(ref, set()))

        if status == "exact-byte-transfer":
            coverage = "verified-exact-body-transfer"
            basis = ["complete canonical body is byte-identical at resolved H target"]
        elif status == "unique-instruction-shape-candidate" and owners:
            coverage = "target-native-inspected-unique-shape"
            basis = ["unique complete instruction-shape target"] + [f"target-native:{x}" for x in owners]
        elif census:
            coverage = "target-surface-recensused"
            basis = census
        elif status == "unique-instruction-shape-candidate":
            coverage = "structural-candidate-only"
            basis = ["unique complete instruction-shape match exists; target-native operand/dataflow not yet recorded"]
        else:
            coverage = "genuinely-unresolved"
            basis = ["no exact transfer, no inspected unique structural target, and no complete generated-surface recensus"]

        classified.append(
            {
                "reference_entry": row["reference_entry"],
                "reference_name": row["reference_name"],
                "body_size": row["body_size"],
                "semantic_tags": row["semantic_tags"],
                "transfer_status": status,
                "target_entry": target,
                "coverage": coverage,
                "coverage_basis": basis,
                "target_native_evidence_files": owners,
                "surface_recensus": census,
            }
        )

    counts = Counter(row["coverage"] for row in classified)
    tag_counts: dict[str, Counter] = defaultdict(Counter)
    for row in classified:
        tags = row["semantic_tags"] or ["untagged"]
        for tag in tags:
            tag_counts[tag][row["coverage"]] += 1

    unresolved = [row for row in classified if row["coverage"] == "genuinely-unresolved"]
    structural_only = [row for row in classified if row["coverage"] == "structural-candidate-only"]

    payload = {
        "schema": "corolla-8965H1202000-static-coverage-matrix-v1",
        "evidence_boundary": (
            "Navigation/denominator artifact. Surface recensus means the foreign generated surface was exhaustively re-enumerated; it is not function homology. Structural-candidate-only is not semantic transfer. Genuinely-unresolved means only that none of the tracked promotion conditions apply."
        ),
        "source": {
            "named_transfer_ledger": str(args.ledger.relative_to(REPO)),
            "named_transfer_ledger_sha256": sha256(args.ledger.read_bytes()),
            "structural_transfer": str(args.structural.relative_to(REPO)),
            "structural_transfer_sha256": sha256(args.structural.read_bytes()),
            "sienna_codeflash_sha256": sha256(sienna),
            "target_native_evidence_files": evidence_file_hashes,
        },
        "summary": {
            "named_function_count": len(classified),
            "coverage_counts": dict(sorted(counts.items())),
            "genuinely_unresolved_count": len(unresolved),
            "structural_candidate_only_count": len(structural_only),
            "h_native_evidence_functions_without_unique_sienna_pair": h_native_unpaired_count,
            "surface_recensus_reference_function_count": sum(bool(v) for v in recensus.values()),
            "target_native_inspected_reference_function_count": len(evidence_reference_entries),
            "tag_coverage_counts": {tag: dict(sorted(counter.items())) for tag, counter in sorted(tag_counts.items())},
        },
        "functions": classified,
        "genuinely_unresolved": unresolved,
        "structural_candidate_only": structural_only,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps(payload["summary"], indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
