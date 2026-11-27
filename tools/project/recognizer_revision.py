#!/usr/bin/env python3
"""Compute the repository-wide function recognizer revision."""
from __future__ import annotations

import argparse
import hashlib
from pathlib import Path

from tools import REPO_ROOT

DIGEST_DOMAIN = b"ghidra-rh850-recognizer-v1\0"
RECOGNIZER_INPUT_PATTERNS = (
    "ghidra/scripts/seed/*.java",
    "ghidra/scripts/annotate/*.java",
    "ghidra/scripts/verify/AssertFunctionDiscoveryFloor.java",
    "ghidra/scripts/verify/ExportOutsideFunctionCandidates.java",
    "ghidra/scripts/verify/ExportSemanticCoverageLedger.java",
    "data/analysis_targets.json",
    "data/targets/*/function_seeds.csv",
    "decomp/*/data.jsonl",
    "decomp/*/struct_layouts.json",
    "decomp/*/symbols.jsonl",
    "data/annotations/annotation_ledger.jsonl",
    "data/checkpoint_payload_map.csv",
    "data/p1m_sfr_labels.csv",
    "data/generated/*/diagnostic_vocabulary.json",
    "data/function_discovery_reviewed_clusters.csv",
    "data/semantic_review_status.csv",
    "tools/project/apply_function_discovery_adjudications.py",
    "tools/project/apply_semantic_review_status.py",
    "tools/project/rebuild_project.sh",
    "tools/project/rebuild_target_project.sh",
    "tools/project/export_ghidra_project.sh",
)


def recognizer_inputs(repo: Path = REPO_ROOT) -> tuple[Path, ...]:
    """Return the sorted, unique recognizer inputs and reject an incomplete tree."""
    relative_paths: set[Path] = set()
    for pattern in RECOGNIZER_INPUT_PATTERNS:
        matches = [path for path in repo.glob(pattern) if path.is_file()]
        if not matches:
            raise FileNotFoundError(f"recognizer input pattern matched no files: {pattern}")
        relative_paths.update(path.relative_to(repo) for path in matches)
    return tuple(sorted(relative_paths, key=lambda path: path.as_posix()))


def compute_recognizer_revision(repo: Path = REPO_ROOT) -> str:
    """Hash the domain plus each sorted relative path and its exact bytes."""
    digest = hashlib.sha256(DIGEST_DOMAIN)
    for relative_path in recognizer_inputs(repo):
        digest.update(relative_path.as_posix().encode("utf-8"))
        digest.update(b"\0")
        digest.update((repo / relative_path).read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--list", action="store_true", help="print the ordered input paths")
    args = parser.parse_args()
    if args.list:
        for path in recognizer_inputs():
            print(path.as_posix())
    else:
        print(compute_recognizer_revision())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
