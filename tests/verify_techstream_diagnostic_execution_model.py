#!/usr/bin/env python3
"""Verify Techstream's DB -> plugin -> frame -> transport execution spine."""
from __future__ import annotations

import os
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
ART = REPO / "data/generated/techstream_v18/diagnostic_execution_model.json"
TOOL = REPO / "tools/techstream/extract_diagnostic_execution_model.py"


def resolve_v18() -> Path:
    base = Path(os.environ.get(
        "TECHSTREAM_UNPACKED_ROOT",
        REPO / "software/Techstream/v18/unpacked/toyota/Toyota Diagnostics",
    ))
    for candidate in (base, base / "Techstream"):
        if (candidate / "bin/CommandCommon.dll").is_file():
            return candidate
    return base


def resolve_gts() -> Path:
    base = Path(os.environ.get("GTSPLUS_ROOT", REPO / "software/Techstream/gtsplus"))
    for candidate in (
        base,
        base / "unpacked/gtsplus/Toyota Diagnostics/GTSPlus",
        base / "Toyota Diagnostics/GTSPlus",
    ):
        if (candidate / "bin/CommandCommon.dll").is_file():
            return candidate
    return base


V18 = resolve_v18()
GTS = resolve_gts()
if not (V18 / "NA/DB/Toyota.ddb").is_file() or not (GTS / "NA/DB/Gen/Toyota.ddb").is_file():
    print("[SKIP] pinned Techstream V18 + GTS+ trees are unavailable")
    raise SystemExit(77)

passed = failed = 0
oracle = "instruction_semantics"


def check(name: str, condition: object, detail: str = "") -> None:
    global passed, failed
    ok = bool(condition)
    passed += int(ok)
    failed += int(not ok)
    suffix = f" ({detail})" if detail else ""
    print(f"[{'PASS' if ok else 'FAIL'}][{oracle}] {name}{suffix}")


with tempfile.TemporaryDirectory() as td:
    out = Path(td) / "model.json"
    proc = subprocess.run(
        [
            sys.executable,
            str(TOOL),
            "--techstream-root",
            str(V18),
            "--gts-root",
            str(GTS),
            "--out",
            str(out),
        ],
        cwd=REPO,
        capture_output=True,
        text=True,
        check=False,
    )
    check("execution-model extractor succeeds", proc.returncode == 0, proc.stderr[-400:])
    check("execution-model artifact regenerates exactly", proc.returncode == 0 and out.read_bytes() == ART.read_bytes())

print(f"\n== RESULT: {passed} passed, {failed} failed ==")
raise SystemExit(1 if failed else 0)
