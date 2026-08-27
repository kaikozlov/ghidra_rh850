#!/usr/bin/env python3
"""Verify the tracked/untracked boundary for external software corpora."""

from __future__ import annotations

import subprocess
import tomllib
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
RAW_PREFIXES = (
    "software/Techstream/v18/",
    "software/Techstream/gtsplus/",
    "software/Techstream/cuw/",
    "software/Renesas/",
)
EXPECTED_LOCKS = {
    "software/locks/techstream-v18.json",
    "software/locks/gtsplus.json",
    "software/locks/toyota-cuw-corpus.json",
    "software/locks/renesas-rfp.json",
}

passed = failed = 0


def check(name: str, condition: object, detail: str = "") -> None:
    global passed, failed
    ok = bool(condition)
    passed += int(ok)
    failed += int(not ok)
    print(
        f"[{'PASS' if ok else 'FAIL'}][documentation_lint] {name}"
        + (f" ({detail})" if detail else "")
    )


tracked = set(
    subprocess.check_output(["git", "ls-files"], cwd=REPO, text=True).splitlines()
)
raw_tracked = sorted(path for path in tracked if path.startswith(RAW_PREFIXES))
check(
    "no vendor/source corpus bytes are tracked", not raw_tracked, repr(raw_tracked[:20])
)
check("software policy is tracked", "software/README.md" in tracked)
check(
    "all source identity locks are tracked",
    EXPECTED_LOCKS <= tracked,
    repr(sorted(EXPECTED_LOCKS - tracked)),
)

ignore = (REPO / ".gitignore").read_text(encoding="utf-8")
for prefix in RAW_PREFIXES:
    check(f"raw corpus ignored: {prefix}", f"/{prefix}" in ignore)

manifest = tomllib.loads((REPO / "verification.toml").read_text(encoding="utf-8"))
external = manifest["external"]
check(
    "Techstream V18 external root canonical",
    external["techstream_v18"]["path"]
    == "software/Techstream/v18/unpacked/toyota/Toyota Diagnostics",
)
check(
    "GTS+ external root canonical",
    external["gtsplus"]["path"] == "software/Techstream/gtsplus",
)
check(
    "Toyota CUW external root canonical",
    external["cuw_reference_corpus"]["path"] == "software/Techstream/cuw",
)
check(
    "external software verification has no REFERENCE path",
    all(not item["path"].startswith("REFERENCE/") for item in external.values()),
)

print(f"\nResults: {passed} passed, {failed} failed")
raise SystemExit(1 if failed else 0)
