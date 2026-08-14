#!/usr/bin/env python3
"""Run the application WDBI-2012 lifecycle boundary assertion on the live project."""
from __future__ import annotations
import argparse, subprocess, tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
PROGRAM = "RH850_P1M-E_CodeFlash.bin"
EXPECTED = (
    "ASSERT application-wdbi-2012-lifecycle: refs_18f=7 refs_18e=11 refs_192=4 "
    "refs_1d1=8 refs_54c=3 refs_signal=3 direct_actuation_refs=0 "
    "direct_actuation_calls=0 unexpected=0"
)

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-dir", type=Path, default=REPO / "build/project")
    args = parser.parse_args()
    project = args.project_dir.resolve()
    if not (project / "rh850_p1me_mapped.rep").is_dir():
        print(f"[FAIL] live WDBI-2012 lifecycle: missing project {project}")
        return 1
    with tempfile.TemporaryDirectory(prefix="wdbi-2012-lifecycle-") as directory:
        log = Path(directory) / "headless.log"
        result = subprocess.run([
            str(REPO / "tools/run_headless"), "--project-dir", str(project),
            "--project", "rh850_p1me_mapped", "--label", "application-wdbi-2012-lifecycle",
            "--log", str(log), "--quiet", "--", "-process", PROGRAM,
            "-noanalysis", "-readOnly", "-postScript", "AssertApplicationWdbi2012Lifecycle.java",
        ], cwd=REPO, text=True, capture_output=True)
        output = log.read_text(errors="replace") if log.exists() else ""
        if result.returncode != 0 or EXPECTED not in output:
            print("[FAIL] live WDBI-2012 lifecycle assertion")
            print((result.stdout or "") + (result.stderr or "") + output[-5000:])
            return 1
    print("[PASS] live WDBI-2012 lifecycle: exact state topology; no direct d/q/PWM join")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
