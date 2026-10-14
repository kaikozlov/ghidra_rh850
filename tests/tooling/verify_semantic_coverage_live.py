#!/usr/bin/env python3
"""Regenerate semantic coverage from a live working project and require parity."""
from __future__ import annotations

import argparse
import os
import subprocess
import tempfile
from pathlib import Path


from tools import REPO_ROOT
from tools.project.analysis_target import target
REPO = REPO_ROOT


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", default=os.environ.get("GHIDRA_ANALYSIS_TARGET"))
    parser.add_argument("--project-dir", type=Path)
    args = parser.parse_args()
    target_name, metadata = target(args.target)
    project_dir = args.project_dir or REPO / metadata["work_dir"]
    with tempfile.TemporaryDirectory(prefix="semantic-coverage-live-") as directory:
        temporary = Path(directory)
        csv_out = temporary / "semantic_coverage_ledger.csv"
        summary_out = temporary / "semantic_coverage_summary.json"
        environment = os.environ.copy()
        environment.update({
            "GHIDRA_ANALYSIS_TARGET": target_name,
            "PROJECT_DIR": str(project_dir.resolve()),
            "CSV_OUT": str(csv_out),
            "SUMMARY_OUT": str(summary_out),
        })
        subprocess.run(
            [str(REPO / "tools" / "project" / "export_ghidra_project.sh"), "semantic-coverage"],
            cwd=REPO, env=environment, check=True,
        )
        expected_csv = REPO / metadata["semantic_coverage_ledger"]
        expected_summary = REPO / metadata["semantic_coverage_summary"]
        if csv_out.read_bytes() != expected_csv.read_bytes():
            print("FAIL: live semantic coverage CSV differs from committed artifact")
            return 1
        if summary_out.read_bytes() != expected_summary.read_bytes():
            print("FAIL: live semantic coverage summary differs from committed artifact")
            return 1
    print("PASS: live semantic coverage exactly matches committed CSV and summary")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
