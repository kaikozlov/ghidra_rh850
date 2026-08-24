#!/usr/bin/env python3
"""Regenerate the public-route opendbc evidence from the exact external rlog."""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
RLOG = REPO / "REFERENCE/public_route_corolla_2023_segment0_rlog.zst"
OPENPILOT = (REPO / "../kai-openpilot").resolve()
PYTHON = OPENPILOT / ".venv/bin/python"
TRACKED = REPO / "data/generated/corolla_2023_public_route_opendbc_evidence.json"

passed = failed = 0

def check(name: str, condition: object, detail: str = "") -> None:
    global passed, failed
    ok = bool(condition); passed += int(ok); failed += int(not ok)
    suffix = f" ({detail})" if detail else ""
    print(f"[{'PASS' if ok else 'FAIL'}][independent_external_artifact] {name}{suffix}")

if not RLOG.is_file() or not PYTHON.is_file():
    print(f"[SKIP] external route/logreader unavailable: rlog={RLOG.is_file()} python={PYTHON.is_file()}")
    raise SystemExit(77)

check("external raw rlog exists", RLOG.is_file())
check("external openpilot logreader environment exists", PYTHON.is_file())

with tempfile.TemporaryDirectory(prefix="corolla-route-opendbc-") as td:
    out = Path(td) / "evidence.json"
    proc = subprocess.run([
        str(PYTHON), str(REPO / "tools/extract_corolla_2023_public_route_opendbc_evidence.py"),
        "--rlog", str(RLOG), "--openpilot-root", str(OPENPILOT), "--output", str(out),
    ], cwd=REPO, capture_output=True, text=True, timeout=120)
    check("raw-route extraction succeeds", proc.returncode == 0, proc.stderr.strip()[:200])
    if out.exists():
        check("tracked extraction matches exact raw route", json.loads(out.read_text()) == json.loads(TRACKED.read_text()))

print(f"\n== RESULT: {passed} passed, {failed} failed ==")
raise SystemExit(1 if failed else 0)
