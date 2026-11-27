#!/usr/bin/env python3
"""Verify compiler fingerprint census and CC-RH listing fixture identities."""

from __future__ import annotations

import subprocess
import sys

from tools import REPO_ROOT


def run(path: str, *args: str) -> None:
    subprocess.run(
        [sys.executable, str(REPO_ROOT / path), *args],
        cwd=REPO_ROOT,
        check=True,
    )


run("tools/testing/processor/build_ccrh_listing_fixture.py", "--check")
run("tools/testing/processor/census_compiler_fingerprints.py", "--check")
print("compiler fingerprint census verification passed")
