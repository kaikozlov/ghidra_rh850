#!/usr/bin/env python3
"""Compact whole-corpus facts needed by Corolla-H LTA provenance verification.

This is a promotion tool, not a core verifier.  The source corpus is a disposable
Ghidra workspace export and must be supplied explicitly; the tracked compact
result is what repository verification consumes.
"""
from __future__ import annotations
import argparse, hashlib, json, struct, sys
from pathlib import Path
from corolla_h_constants import CODEFLASH as H_CODEFLASH

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))
IMAGE = H_CODEFLASH
DEFAULT_OUT = REPO / "data/generated/corolla_8965H1202000_lta_command_provenance_census.json"

# Import the exact extraction helpers used by the report builder.
from tools.build_corolla_h_lta_command_provenance import (  # noqa: E402
    flatten_args, lhs_writes, load_corpus, resolved_call_first_args, term_occurrences,
)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--corpus", type=Path, required=True,
                    help="disposable whole-image H decompiler corpus JSONL")
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT)
    a = ap.parse_args()
    corpus = a.corpus.resolve()
    if not corpus.is_file():
        raise SystemExit(f"missing corpus: {corpus}")
    image = IMAGE.read_bytes()
    hf = load_corpus(corpus)

    def first_args(entry: int, callee: str) -> list[int]:
        row = next(r for r in hf if int(r["entry_addr"], 16) == entry)
        return sorted(set(flatten_args(resolved_call_first_args([row], callee, image))))

    group_calls = resolved_call_first_args(hf, "FUN_00077a3a", image)
    full_pdu_calls = resolved_call_first_args(hf, "FUN_0007636c", image)
    group_ids = sorted(set(flatten_args(group_calls)))
    full_pdu_ids = sorted(set(flatten_args(full_pdu_calls)))
    cells = {}
    for addr in (0xFEBEC17C, 0xFEBEC17E, 0xFEBEC184, 0xFEBEC26D):
        suffix = f"{addr:08x}"
        cells[f"0x{addr:08X}"] = {
            "occurrences": term_occurrences(hf, suffix),
            "direct_lhs_writes": lhs_writes(hf, suffix),
        }
    writes = {}
    for addr in (
        0xFEBEC2A6, 0xFEBEC2A8, 0xFEBEBE04, 0xFEBEBD90, 0xFEBEB678,
        0xFEBEBEC6, 0xFEBEC39C, 0xFEBEABB0, 0xFEBEBCF8, 0xFEBEC2D4,
    ):
        writes[f"0x{addr:08X}"] = lhs_writes(hf, f"{addr:08x}")

    out = {
        "schema": "corolla-8965H1202000-lta-whole-corpus-census-v1",
        "software_id": "8965H1202000",
        "image": {"path": str(IMAGE.relative_to(REPO)), "sha256": sha(IMAGE)},
        "source_corpus": {
            "kind": "disposable-ghidra-workspace-export",
            "sha256": sha(corpus),
            "function_count": len(hf),
            "boundary": "Source workspace corpus is intentionally untracked; this compact promoted census is the repository input.",
        },
        "scalar_receive_ids": {
            "d7": first_args(0x468FA, "FUN_0007643a"),
            "b6": first_args(0x46A10, "FUN_0007643a"),
        },
        "all_literal_block_group_receive_ids": group_ids,
        "block_group_calls": group_calls,
        "all_literal_full_pdu_ids": full_pdu_ids,
        "full_pdu_calls": full_pdu_calls,
        "cells": cells,
        "direct_lhs_writes": writes,
    }
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    print(a.out)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
