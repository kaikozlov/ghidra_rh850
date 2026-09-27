#!/usr/bin/env python3
"""Verify the current GTS+ DDB corpus census and steering-control witnesses."""
from __future__ import annotations

import json

from tools import REPO_ROOT
REPO = REPO_ROOT

from tools.techstream.extract_gtsplus_ddb_corpus_census import build
from tools.techstream.techstream_paths import resolve_gts_root

ARTIFACT = REPO / "data/generated/gtsplus_2026/ddb_corpus_census.json"

passed = failed = 0


def check(name: str, condition: bool, detail: str = "") -> None:
    global passed, failed
    ok = bool(condition)
    passed += int(ok)
    failed += int(not ok)
    print(f"[{'PASS' if ok else 'FAIL'}] {name}" + (f" ({detail})" if detail else ""))


a = json.loads(ARTIFACT.read_text())

fresh = build(resolve_gts_root())
check("artifact regenerates exactly", fresh == a)

print(f"\nResults: {passed} passed, {failed} failed")
raise SystemExit(1 if failed else 0)
