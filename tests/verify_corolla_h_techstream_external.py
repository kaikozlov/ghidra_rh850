#!/usr/bin/env python3
"""Verify Corolla H Techstream joins against the external pinned DDB corpus."""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / "data/generated/corolla_8965H1202000_techstream_correlations.json"
BUILD = ROOT / "tools/build_corolla_h_techstream_correlations.py"
DIAG_ROOT = Path(
    os.environ.get(
        "TECHSTREAM_UNPACKED_ROOT",
        ROOT / "software/Techstream/v18/unpacked/toyota/Toyota Diagnostics",
    )
)
TECHROOT = DIAG_ROOT / "Techstream"
passed = failed = 0


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check(name: str, condition: bool, detail: str = "") -> None:
    global passed, failed
    ok = bool(condition)
    passed += int(ok)
    failed += int(not ok)
    suffix = f" ({detail})" if detail else ""
    print(f"[{'PASS' if ok else 'FAIL'}][independent_external_artifact] {name}{suffix}")


report = json.loads(ART.read_text())
for key, rel in (
    ("na_emps_p5", "NA/DB/EMPS_P5.ddb"),
    ("na_emps2_p5", "NA/DB/EMPS2_P5.ddb"),
):
    source = TECHROOT / rel
    check(f"{rel} exists", source.is_file(), str(source))
    if source.is_file():
        check(f"{rel} hash matches pinned report", sha(source) == report["sources"][key]["sha256"])

with tempfile.TemporaryDirectory(prefix="corolla-h-techstream-") as td:
    out = Path(td) / "report.json"
    proc = subprocess.run(
        [sys.executable, str(BUILD), "--out", str(out)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    check("Techstream correlation builder exits cleanly", proc.returncode == 0,
          (proc.stderr or proc.stdout)[-300:] if proc.returncode else "")
    check(
        "Techstream correlation artifact regenerates exactly",
        proc.returncode == 0 and out.is_file() and out.read_bytes() == ART.read_bytes(),
    )

print(f"\nResults: {passed} passed, {failed} failed")
raise SystemExit(1 if failed else 0)
