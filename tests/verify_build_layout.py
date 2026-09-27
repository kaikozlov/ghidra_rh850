#!/usr/bin/env python3
"""Verify safe cleanup and side-effect-free Ghidra status queries."""
from __future__ import annotations

import os
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
passed = failed = 0


def check(name: str, condition: object, detail: str = "") -> None:
    global passed, failed
    ok = bool(condition)
    passed += int(ok); failed += int(not ok)
    print(f"[{'PASS' if ok else 'FAIL'}] {name}" + (f" ({detail})" if detail else ""))


print("\n== destructive-operation safety ==")
with tempfile.TemporaryDirectory(prefix="rh850-build-layout-clean-") as td:
    external_root = Path(td) / "build"
    sentinel = external_root / "tmp" / "keep-me"
    sentinel.parent.mkdir(parents=True)
    sentinel.write_text("preserve")
    env = dict(os.environ, BUILD_ROOT=str(external_root))
    cp = subprocess.run([sys.executable, str(REPO / "tools/project/build_layout.py"), "clean", "tmp"], cwd=REPO, env=env, capture_output=True, text=True, timeout=15)
    check("destructive layout operations reject BUILD_ROOT overrides", cp.returncode != 0 and sentinel.read_text() == "preserve", cp.stderr)

print("\n== side-effect-free status path ==")
with tempfile.TemporaryDirectory(prefix="rh850-build-layout-") as td:
    root = Path(td) / "build"
    env = dict(os.environ, BUILD_ROOT=str(root), GHIDRA_NO_BOOTSTRAP="1", GHIDRA_AGENT="1")
    cp = subprocess.run(["bash", str(REPO / "tools/g"), "session-status"], cwd=REPO, env=env, capture_output=True, text=True, timeout=15)
    check("tools/g session-status works with empty build root", cp.returncode == 0, cp.stderr)
    check("session-status does not create cache/work/output state", not root.exists() or not any(root.iterdir()))

print(f"\nResults: {passed} passed, {failed} failed")
raise SystemExit(1 if failed else 0)
