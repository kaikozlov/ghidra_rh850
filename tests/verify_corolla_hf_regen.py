#!/usr/bin/env python3
"""Regenerate committed Corolla H/F builder artifacts (full/local only)."""
from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from artifact_catalog import suite_builder_pairs  # noqa: E402
passed = failed = 0


def check(name, cond, detail=""):
    global passed, failed
    ok = bool(cond)
    passed += int(ok)
    failed += int(not ok)
    suffix = f" ({detail})" if detail else ""
    print(f"[{'PASS' if ok else 'FAIL'}] {name}{suffix}")


BUILDERS = [
    (Path(artifact).stem, builder, artifact)
    for builder, artifact in suite_builder_pairs("corolla_hf_regen")
]


for title, builder, artifact in BUILDERS:
    print(f"== {title} regen ==")
    tool = ROOT / builder
    art = ROOT / artifact
    with tempfile.TemporaryDirectory() as td:
        out = Path(td) / "out.json"
        proc = subprocess.run(
            [sys.executable, str(tool), "--out", str(out)],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        check(f"{title} builder exits cleanly", proc.returncode == 0, (proc.stderr or proc.stdout)[-300:] if proc.returncode else "")
        check(
            f"{title} artifact regenerates exactly",
            proc.returncode == 0 and out.exists() and out.read_bytes() == art.read_bytes(),
        )
    print()

print(f"\n== RESULT: {passed} passed, {failed} failed ==")
raise SystemExit(1 if failed else 0)
