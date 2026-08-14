#!/usr/bin/env python3
"""Execute the fixed-response-buffer xref assertion on the live project."""
from __future__ import annotations

import argparse
import subprocess
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
PROGRAM = "RH850_P1M-E_CodeFlash.bin"
EXPECTED = (
    "ASSERT application-rdbi-stale-response: "
    "fixed_buffer=febe59f8 direct_xrefs=3 clears=2 pointer_refs=1 unexpected=0"
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-dir", type=Path, default=REPO / "build" / "project")
    args = parser.parse_args()
    project_dir = args.project_dir.resolve()
    if not (project_dir / "rh850_p1me_mapped.rep").is_dir():
        print(f"[FAIL] live RDBI stale-response xrefs: missing project {project_dir}")
        return 1
    with tempfile.TemporaryDirectory(prefix="rdbi-stale-live-") as directory:
        log = Path(directory) / "headless.log"
        result = subprocess.run(
            [
                str(REPO / "tools" / "run_headless"),
                "--project-dir", str(project_dir),
                "--project", "rh850_p1me_mapped",
                "--label", "application-rdbi-stale-response",
                "--log", str(log),
                "--quiet",
                "--",
                "-process", PROGRAM,
                "-noanalysis",
                "-readOnly",
                "-postScript", "AssertApplicationRdbiStaleResponse.java",
            ],
            cwd=REPO,
            text=True,
            capture_output=True,
        )
        output = log.read_text(encoding="utf-8", errors="replace") if log.exists() else ""
        if result.returncode != 0 or EXPECTED not in output:
            print("[FAIL] live RDBI stale-response xrefs")
            print((result.stdout or "")[-2000:])
            print((result.stderr or "")[-2000:])
            print(output[-4000:])
            return 1
    print("[PASS] live RDBI stale-response xrefs: fixed buffer has only two byte-clears plus pointer construction")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
