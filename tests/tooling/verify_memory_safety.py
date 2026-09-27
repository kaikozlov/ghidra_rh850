#!/usr/bin/env python3
"""Verify every proposition in the memory-safety proof matrix."""
from __future__ import annotations


from tools import REPO_ROOT
REPO = REPO_ROOT

from tools.security.memory_safety_semantics import analyze  # noqa: E402


image = (REPO / "firmware" / "RH850_P1M-E_CodeFlash.bin").read_bytes()
result = analyze(image)
passed = failed = 0

for claim, propositions in result["propositions"].items():
    print(f"== {claim} ==")
    for proposition, ok in propositions.items():
        passed += bool(ok)
        failed += not ok
        print(f"[{'PASS' if ok else 'FAIL'}] {proposition}")

print(f"\nResults: {passed} passed, {failed} failed")
raise SystemExit(1 if failed else 0)
