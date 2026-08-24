#!/usr/bin/env python3
"""Regenerate semantic coverage from a live working project and require parity."""
from __future__ import annotations

import argparse
import os
import subprocess
import tempfile
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-dir", type=Path, default=REPO / "build" / "work" / "project")
    args = parser.parse_args()
    with tempfile.TemporaryDirectory(prefix="semantic-coverage-live-") as directory:
        temporary = Path(directory)
        csv_out = temporary / "semantic_coverage_ledger.csv"
        summary_out = temporary / "semantic_coverage_summary.json"
        environment = os.environ.copy()
        environment.update({
            "PROJECT_DIR": str(args.project_dir.resolve()),
            "CSV_OUT": str(csv_out),
            "SUMMARY_OUT": str(summary_out),
        })
        subprocess.run(
            [str(REPO / "tools" / "export_ghidra_project.sh"), "semantic-coverage"],
            cwd=REPO, env=environment, check=True,
        )
        expected_csv = REPO / "data" / "semantic_coverage_ledger.csv"
        expected_summary = REPO / "data" / "semantic_coverage_summary.json"
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
