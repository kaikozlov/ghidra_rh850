#!/usr/bin/env python3
"""Rank exact-F33 memory-safety attack paths and homolog guard differences.

The inputs are read-only exports from the registered Camry and Crown Ghidra
snapshots.  Structural matches establish candidate homology; scalar operands
then expose changed bounds without treating decompiler spelling as evidence.
The report is a triage map, not a vulnerability verdict.
"""
from __future__ import annotations

import argparse
import bisect
import difflib
import hashlib
import json
import re
from pathlib import Path
from typing import Any

from tools import REPO_ROOT

CAMRY_SHA256 = "42dce8efc42f6ae31718e7713fa2d26bb9191b4a82439778aee4d7afded9b0e7"
CROWN_SHA256 = "5b89fdbc69edc2f66ef8a557f88b08c758e3146bd4e90067320d7966812b1273"
SCHEMA = "camry-8965f3307000-memory-attack-surface-v1"

DEFAULTS = {
    "camry_fingerprints": REPO_ROOT / "build/out/targets/camry-8965F3307000/function_structural_fingerprints.jsonl",
    "crown_fingerprints": REPO_ROOT / "build/out/targets/crown-8965F3012000/function_structural_fingerprints.jsonl",
    "matches": REPO_ROOT / "build/out/targets/camry-8965F3307000/crown_structural_function_transfer.json",
    "camry_scalars": REPO_ROOT / "build/out/targets/camry-8965F3307000/function_scalar_operands.jsonl",
    "crown_scalars": REPO_ROOT / "build/out/targets/crown-8965F3012000/function_scalar_operands.jsonl",
    "camry_decomp": REPO_ROOT / "data/generated/camry-8965F3307000/decompilations.jsonl",
    "crown_decomp": REPO_ROOT / "data/generated/crown-8965F3012000/decompilations.jsonl",
    "store_census": REPO_ROOT / "data/generated/camry_8965F3307000_computed_store_target_census.json",
    "output": REPO_ROOT / "data/generated/camry_8965F3307000_memory_attack_surface.json",
}

# Exact-image ingress and high-risk handler entries.  The raw CAN producer is
# separate from deferred consumers; table-driven edges are therefore represented
# as independent roots instead of invented direct calls.
ROOTS = {
    "raw_can_ring_producer": (0x80A4A, "RSCFD payload and retained DLC enter the software ring"),
    "deferred_can_dispatch": (0x80884, "software-ring records dispatch through configured callbacks"),
    "normal_com_ingress": (0x810F2, "normal/SecOC PDU callback path"),
    "cantp_ingress": (0x7A57A, "diagnostic CAN frame and ISO-TP PCI parser"),
    "dcm_scheduled_dispatch": (0x922AA, "completed application diagnostic request"),
    "dcm_write_did": (0x95978, "SID 0x2E request body"),
    "dcm_routine_control": (0x97AE4, "SID 0x31 request body and lifecycle operation"),
    "dcm_read_did": (0x962F2, "SID 0x22 DID list and response producer"),
    "dcm_read_memory": (0x965C0, "SID 0x23 address, size, memory ID, and response capacity"),
    "xcp_staging": (0x830D0, "extended-ID XCP-shaped frame staging; stock command gate is disabled"),
    "xcp_command_dispatch": (0x821D6, "post-staging command path behind fixed CodeFlash gate"),
    "boot_uds_dispatch": (0x5222, "boot diagnostic service dispatch after programming transition"),
}

MEMORY_NAME = re.compile(
    r"copy|memory|buffer|payload|request|response|receive|transmit|write|read|slot|ring|dispatch",
    re.IGNORECASE,
)
MEMORY_C = re.compile(
    r"\[[^\]]+\]\s*=|\*\s*\([^;]+\)\s*=|memcpy|copy|length|size|cursor|payload|buffer|request|response",
    re.IGNORECASE,
)
CONTROL = re.compile(r"\b(?:if|while|for|switch)\s*\(")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_jsonl(path: Path, record: str) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    metadata: dict[str, Any] | None = None
    rows: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as stream:
        for line in stream:
            row = json.loads(line)
            if row.get("record") == "metadata":
                metadata = row
            elif row.get("record") == record:
                rows.append(row)
    if metadata is None:
        raise ValueError(f"{path} has no metadata row")
    return metadata, rows


def keyed(rows: list[dict[str, Any]]) -> dict[int, dict[str, Any]]:
    return {int(row["entry_addr"], 16): row for row in rows}


def memory_score(row: dict[str, Any] | None) -> int:
    if row is None:
        return 0
    source = row.get("decompiled_c", "")
    return len(MEMORY_C.findall(source)) + 5 * bool(MEMORY_NAME.search(row.get("name", "")))


def closure(graph: dict[int, tuple[int, ...]], entry: int) -> set[int]:
    seen: set[int] = set()
    pending = [entry]
    while pending:
        address = pending.pop()
        if address in seen:
            continue
        seen.add(address)
        pending.extend(target for target in graph.get(address, ()) if target not in seen)
    return seen


def lis_anchors(
    camry: list[dict[str, Any]], crown: list[dict[str, Any]], matches: list[dict[str, Any]],
) -> list[tuple[int, int, int, int]]:
    camry_index = {int(row["entry_addr"], 16): index for index, row in enumerate(camry)}
    crown_index = {int(row["entry_addr"], 16): index for index, row in enumerate(crown)}
    pairs = sorted(
        (
            camry_index[int(row["reference_entry"], 16)],
            crown_index[int(row["target_entry"], 16)],
            int(row["reference_entry"], 16),
            int(row["target_entry"], 16),
        )
        for row in matches
        if row["instruction_count"] >= 8
    )
    ends: list[int] = []
    end_indices: list[int] = []
    previous = [-1] * len(pairs)
    for index, (_camry_index, target_index, _camry_addr, _target_addr) in enumerate(pairs):
        position = bisect.bisect_left(ends, target_index)
        if position == len(ends):
            ends.append(target_index)
            end_indices.append(index)
        else:
            ends[position] = target_index
            end_indices[position] = index
        if position:
            previous[index] = end_indices[position - 1]
    if not end_indices:
        return []
    index = end_indices[-1]
    result: list[tuple[int, int, int, int]] = []
    while index >= 0:
        result.append(pairs[index])
        index = previous[index]
    return list(reversed(result))


def fuzzy_missing_guard_candidates(
    camry: list[dict[str, Any]], crown: list[dict[str, Any]],
    decomp: dict[int, dict[str, Any]], anchors: list[tuple[int, int, int, int]],
) -> list[dict[str, Any]]:
    candidates: list[dict[str, Any]] = []
    previous = (-1, -1)
    sentinels = [*anchors, (len(camry), len(crown), -1, -1)]
    for current in sentinels:
        camry_indices = range(previous[0] + 1, current[0])
        crown_indices = range(previous[1] + 1, current[1])
        if len(camry_indices) != len(crown_indices) or len(camry_indices) > 64:
            previous = current[:2]
            continue
        for camry_index, crown_index in zip(camry_indices, crown_indices):
            reference = camry[camry_index]
            target = crown[crown_index]
            similarity = difflib.SequenceMatcher(
                None, reference["mnemonics"], target["mnemonics"], autojunk=False,
            ).ratio()
            delta = reference["conditional_branch_count"] - target["conditional_branch_count"]
            if similarity < 0.70 or delta >= 0:
                continue
            address = int(reference["entry_addr"], 16)
            row = decomp.get(address)
            candidates.append({
                "camry_entry": reference["entry_addr"],
                "camry_name": row.get("name") if row else reference.get("name"),
                "crown_entry": target["entry_addr"],
                "mnemonic_similarity": round(similarity, 6),
                "camry_conditional_branches": reference["conditional_branch_count"],
                "crown_conditional_branches": target["conditional_branch_count"],
                "memory_relevance_score": memory_score(row),
                "classification": "homolog-candidate-camry-has-fewer-conditional-branches",
            })
        previous = current[:2]
    return sorted(
        candidates,
        key=lambda row: (-row["memory_relevance_score"], row["camry_conditional_branches"] - row["crown_conditional_branches"], row["camry_entry"]),
    )


def scalar_vector(instruction: dict[str, Any]) -> list[tuple[int, int, int, int]]:
    result = []
    for operand in instruction["operands"]:
        for scalar in operand["scalars"]:
            result.append((
                operand["index"], scalar["bits"], int(scalar["unsigned"], 16), scalar["signed"],
            ))
    return result


def changed_bound_candidates(
    matches: list[dict[str, Any]], camry_scalars: dict[int, dict[str, Any]],
    crown_scalars: dict[int, dict[str, Any]], decomp: dict[int, dict[str, Any]],
) -> list[dict[str, Any]]:
    candidates: list[dict[str, Any]] = []
    for match in matches:
        camry_entry = int(match["reference_entry"], 16)
        crown_entry = int(match["target_entry"], 16)
        reference = camry_scalars.get(camry_entry)
        target = crown_scalars.get(crown_entry)
        if reference is None or target is None:
            continue
        reference_instructions = reference["instructions"]
        target_instructions = target["instructions"]
        if len(reference_instructions) != len(target_instructions):
            continue
        changes = []
        for index, (camry_instruction, crown_instruction) in enumerate(
            zip(reference_instructions, target_instructions)
        ):
            if camry_instruction["mnemonic"] != crown_instruction["mnemonic"]:
                continue
            if "CALL" in camry_instruction["flow"] or "JUMP" in camry_instruction["flow"]:
                continue
            camry_values = scalar_vector(camry_instruction)
            crown_values = scalar_vector(crown_instruction)
            if not camry_values or camry_values == crown_values:
                continue
            # Address materialization and GP/TP/EP-relative layout differences are
            # not bounds.  Retain direct comparisons and small immediates that feed
            # a conditional branch within the next three instructions.
            following = reference_instructions[index + 1:index + 4]
            feeds_branch = any("CONDITIONAL" in row["flow"] for row in following)
            small = all(0 <= value[3] <= 0x10000 for value in camry_values + crown_values)
            if camry_instruction["mnemonic"] not in {
                "cmp", "addi", "movea", "mov", "andi", "ori", "shl", "shr", "mul", "mulhi",
            }:
                continue
            is_compare = camry_instruction["mnemonic"] == "cmp"
            if not is_compare and not (feeds_branch and small):
                continue
            camry_text = [operand["text"] for operand in camry_instruction["operands"]]
            crown_text = [operand["text"] for operand in crown_instruction["operands"]]
            if not is_compare and any(
                register in " ".join(camry_text + crown_text)
                for register in ("gp", "tp", "ep")
            ):
                continue
            changes.append({
                "instruction": camry_instruction["address"],
                "mnemonic": camry_instruction["mnemonic"],
                "camry_operands": camry_text,
                "crown_operands": crown_text,
                "feeds_conditional_branch": feeds_branch,
            })
        if changes:
            row = decomp.get(camry_entry)
            candidates.append({
                "camry_entry": match["reference_entry"],
                "camry_name": row.get("name") if row else match.get("reference_name"),
                "crown_entry": match["target_entry"],
                "instruction_count": match["instruction_count"],
                "memory_relevance_score": memory_score(row),
                "changed_guard_operands": changes,
                "classification": "exact-instruction-shape-homolog-with-changed-guard-operand",
            })
    return sorted(
        candidates,
        key=lambda row: (-row["memory_relevance_score"], -len(row["changed_guard_operands"]), row["camry_entry"]),
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    for name, default in DEFAULTS.items():
        parser.add_argument("--" + name.replace("_", "-"), type=Path, default=default)
    args = parser.parse_args()

    camry_meta, camry_fingerprints = load_jsonl(args.camry_fingerprints, "function-structural-fingerprint")
    crown_meta, crown_fingerprints = load_jsonl(args.crown_fingerprints, "function-structural-fingerprint")
    camry_scalar_meta, camry_scalar_rows = load_jsonl(args.camry_scalars, "function-scalar-operands")
    crown_scalar_meta, crown_scalar_rows = load_jsonl(args.crown_scalars, "function-scalar-operands")
    _camry_decomp_meta, camry_decomp_rows = load_jsonl(args.camry_decomp, "function")
    _crown_decomp_meta, _crown_decomp_rows = load_jsonl(args.crown_decomp, "function")
    if camry_meta["executable_sha256"] != CAMRY_SHA256 or camry_scalar_meta["executable_sha256"] != CAMRY_SHA256:
        raise SystemExit("Camry exports do not bind to 8965F3307000")
    if crown_meta["executable_sha256"] != CROWN_SHA256 or crown_scalar_meta["executable_sha256"] != CROWN_SHA256:
        raise SystemExit("Crown exports do not bind to 8965F3012000")

    match_report = json.loads(args.matches.read_text(encoding="utf-8"))
    matches = match_report["matches"]
    store_report = json.loads(args.store_census.read_text(encoding="utf-8"))
    store_functions = {int(value, 16) for value in store_report["candidate_functions"]}
    decomp = keyed(camry_decomp_rows)
    fingerprints = keyed(camry_fingerprints)
    graph = {
        entry: tuple(int(target, 16) for target in row.get("direct_call_targets", ()))
        for entry, row in fingerprints.items()
    }

    source_map: dict[str, Any] = {}
    all_reachable: set[int] = set()
    for label, (entry, provenance) in ROOTS.items():
        reachable = closure(graph, entry)
        all_reachable.update(reachable)
        computed = sorted(reachable & store_functions)
        indirect = sorted(
            address for address in reachable
            if fingerprints.get(address, {}).get("indirect_call_count", 0)
        )
        ranked = sorted(
            reachable,
            key=lambda address: (
                -(10 * (address in store_functions)
                  + 8 * fingerprints.get(address, {}).get("indirect_call_count", 0)
                  + memory_score(decomp.get(address))),
                address,
            ),
        )
        source_map[label] = {
            "entry": f"0x{entry:08X}",
            "name": decomp.get(entry, {}).get("name", fingerprints.get(entry, {}).get("name")),
            "attacker_provenance": provenance,
            "direct_call_closure_count": len(reachable),
            "computed_store_functions": [f"0x{address:08X}" for address in computed],
            "indirect_call_functions": [f"0x{address:08X}" for address in indirect],
            "highest_risk_reachable_functions": [
                {
                    "entry": f"0x{address:08X}",
                    "name": decomp.get(address, {}).get("name", fingerprints.get(address, {}).get("name")),
                    "memory_relevance_score": memory_score(decomp.get(address)),
                    "computed_store_candidate": address in store_functions,
                    "indirect_call_count": fingerprints.get(address, {}).get("indirect_call_count", 0),
                }
                for address in ranked[:20]
            ],
        }

    anchors = lis_anchors(camry_fingerprints, crown_fingerprints, matches)
    missing_guards = fuzzy_missing_guard_candidates(
        camry_fingerprints, crown_fingerprints, decomp, anchors,
    )
    changed_bounds = changed_bound_candidates(
        matches, keyed(camry_scalar_rows), keyed(crown_scalar_rows), decomp,
    )

    whole_image_store_rows = [
        row for row in store_report["candidates"]
        if int(row["function"], 16) in all_reachable
    ]
    report = {
        "schema": SCHEMA,
        "target": {
            "name": "camry-8965F3307000",
            "codeflash_sha256": CAMRY_SHA256,
        },
        "comparison_target": {
            "name": "crown-8965F3012000",
            "codeflash_sha256": CROWN_SHA256,
            "role": "same-MCU Toyota/Denso family homolog comparator; differences are triage leads, not proof",
        },
        "inputs": {
            name: {"path": str(getattr(args, name).relative_to(REPO_ROOT)), "sha256": sha256(getattr(args, name))}
            for name in DEFAULTS if name != "output"
        },
        "summary": {
            "camry_functions": len(camry_fingerprints),
            "crown_functions": len(crown_fingerprints),
            "unique_exact_shape_homologs": len(matches),
            "monotonic_exact_anchors": len(anchors),
            "camry_fewer_branch_candidates": len(missing_guards),
            "changed_guard_operand_candidates": len(changed_bounds),
            "attacker_root_count": len(ROOTS),
            "directly_reachable_union_functions": len(all_reachable),
            "reachable_computed_store_rows": len(whole_image_store_rows),
        },
        "source_to_sink_map": source_map,
        "reachable_computed_store_rows": whole_image_store_rows,
        "homolog_missing_guard_candidates": missing_guards,
        "homolog_changed_guard_operand_candidates": changed_bounds,
        "interpretation": {
            "proof_boundary": "structural homology and operand differences rank review targets; exact Camry disassembly/dataflow and dynamic reproduction are required for a finding",
            "call_graph_boundary": "direct-call closure excludes unresolved table-driven callbacks, represented as separate exact roots above",
            "priority": "review request-derived loops, changed compare bounds, computed destinations, indirect callbacks, and lifecycle reuse before broad random mutation",
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(args.output), "summary": report["summary"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
