#!/usr/bin/env python3
"""Verify registry-owned analyzer choices reach deterministic headless rebuilds."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from tools import REPO_ROOT

ROOT = REPO_ROOT
RESOLVER = ROOT / "tools/project/analysis_target.py"
TARGET_REBUILD = ROOT / "tools/project/rebuild_target_project.sh"
SIENNA_REBUILD = ROOT / "tools/project/rebuild_project.sh"

passed = failed = 0


def check(name: str, condition: object, detail: str = "") -> None:
    global passed, failed
    ok = bool(condition)
    passed += int(ok)
    failed += int(not ok)
    print(f"[{'PASS' if ok else 'FAIL'}] {name}" + (f" ({detail})" if detail else ""))


def resolve(target: str, phase: str) -> list[str]:
    result = subprocess.run(
        [sys.executable, str(RESOLVER), target, "--analyzer-headless-args", phase],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    check(f"resolve {target} {phase}", result.returncode == 0, result.stderr.strip())
    return result.stdout.splitlines()


camry_pre = resolve("camry-8965F3307000", "pre")
check(
    "Camry analysis invocation disables Address Tables",
    camry_pre
    == [
        "-preScript",
        "ApplyAnalysisOptions.java",
        "Create Address Tables=false",
        "Non-Returning Functions - Discovered=true",
    ],
    repr(camry_pre),
)
check(
    "Camry import invocation persists the same choices",
    resolve("camry-8965F3307000", "post")
    == ["-postScript", "ApplyAnalysisOptions.java", *camry_pre[2:]],
)

sienna_pre = resolve("sienna-8965B4512000", "pre")
check(
    "Sienna analysis invocation preserves both measured settings",
    sienna_pre
    == [
        "-preScript",
        "ApplyAnalysisOptions.java",
        "Create Address Tables=true",
        "Non-Returning Functions - Discovered=true",
    ],
    repr(sienna_pre),
)
check(
    "unrecorded target forces no analyzer choice",
    resolve("crown-8965F3012000", "pre") == [],
)

for path, expected_analysis_passes in ((TARGET_REBUILD, 3), (SIENNA_REBUILD, 3)):
    source = path.read_text()
    check(
        f"{path.name} resolves registry analyzer arguments",
        "--analyzer-headless-args post" in source
        and "--analyzer-headless-args pre" in source,
    )
    check(
        f"{path.name} applies options to import and every analysis pass",
        source.count('"${ANALYZER_IMPORT_ARGS[@]}"') == 1
        and source.count('"${ANALYZER_ANALYSIS_ARGS[@]}"') == expected_analysis_passes,
    )
    check(
        f"{path.name} has no target-specific analyzer policy",
        "Create Address Tables" not in source
        and "Non-Returning Functions - Discovered" not in source,
    )

print(f"\nResults: {passed} passed, {failed} failed")
raise SystemExit(1 if failed else 0)
