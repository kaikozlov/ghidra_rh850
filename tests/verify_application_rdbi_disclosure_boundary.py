#!/usr/bin/env python3
"""Execute the bounded application-RDBI disclosure audit on the live project."""
from __future__ import annotations

import argparse
import subprocess
import tempfile
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]
PROGRAM = "RH850_P1M-E_CodeFlash.bin"
EXPECTED = (
    "ASSERT application-rdbi-disclosure-boundary: "
    "dids=242 unique_callbacks=196 max_depth=4 sensitive_hits=4 unexpected=0"
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-dir", type=Path, default=REPO / "build" / "project")
    args = parser.parse_args()
    project_dir = args.project_dir.resolve()
    if not (project_dir / "rh850_p1me_mapped.rep").is_dir():
        print(f"[FAIL] live RDBI disclosure boundary: missing project {project_dir}")
        return 1

    with tempfile.TemporaryDirectory(prefix="rdbi-disclosure-") as directory:
        log = Path(directory) / "headless.log"
        result = subprocess.run(
            [
                str(REPO / "tools" / "run_headless"),
                "--project-dir", str(project_dir),
                "--project", "rh850_p1me_mapped",
                "--label", "application-rdbi-disclosure-boundary",
                "--log", str(log),
                "--quiet",
                "--",
                "-process", PROGRAM,
                "-noanalysis",
                "-readOnly",
                "-postScript", "AssertApplicationRdbiDisclosureBoundary.java",
            ],
            cwd=REPO,
            text=True,
            capture_output=True,
        )
        output = log.read_text(encoding="utf-8", errors="replace") if log.exists() else ""
        if result.returncode != 0:
            print("[FAIL] live RDBI disclosure boundary: headless verifier failed")
            if result.stdout:
                print(result.stdout)
            if result.stderr:
                print(result.stderr)
            if output:
                print(output[-4000:])
            return 1
        if EXPECTED not in output:
            print("[FAIL] live RDBI disclosure boundary: expected assertion summary missing")
            print(output[-4000:])
            return 1

    print("[PASS] live RDBI disclosure boundary: 242 DIDs / 196 callbacks / 4-hop bounded negative")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
