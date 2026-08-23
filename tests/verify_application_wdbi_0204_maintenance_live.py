#!/usr/bin/env python3
"""Run the WDBI DID 0x0204 maintenance topology assertion on the live project."""
from __future__ import annotations
import argparse
import subprocess
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
PROGRAM = "RH850_P1M-E_CodeFlash.bin"
EXPECTED = ("ASSERT application-wdbi-0204-maintenance: pending_states=2 object7_handshake=1 "
            "op6_initiator=1 op6_fanout=12 direct_actuation_refs=0 unexpected=0")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-dir", type=Path, default=REPO / "build/work/project")
    args = parser.parse_args()
    project = args.project_dir.resolve()
    if not (project / "rh850_p1me_mapped.rep").is_dir():
        print(f"[FAIL] live WDBI-0204 maintenance: missing project {project}")
        return 1
    with tempfile.TemporaryDirectory(prefix="wdbi-0204-") as directory:
        log = Path(directory) / "headless.log"
        result = subprocess.run([
            str(REPO / "tools/run_headless"), "--project-dir", str(project),
            "--project", "rh850_p1me_mapped", "--label", "application-wdbi-0204-maintenance",
            "--log", str(log), "--quiet", "--", "-process", PROGRAM, "-noanalysis", "-readOnly",
            "-postScript", "AssertApplicationWdbi0204Maintenance.java",
        ], cwd=REPO, text=True, capture_output=True)
        output = log.read_text(errors="replace") if log.exists() else ""
        if result.returncode or EXPECTED not in output:
            print("[FAIL] live WDBI-0204 maintenance assertion")
            print((result.stdout or "") + (result.stderr or "") + output[-6000:])
            return 1
    print("[PASS] live WDBI-0204: async mode/object7/op6 topology exact; no direct conditioned-command/dq join")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
