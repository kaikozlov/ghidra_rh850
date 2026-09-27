#!/usr/bin/env python3
"""Verify explicit suite, prefix, and group selection."""
from __future__ import annotations

import subprocess
import sys
import tempfile
import textwrap
import tomllib
from pathlib import Path

from tools import REPO_ROOT
REPO = REPO_ROOT
RUNNER = REPO / "tools/testing/fast_verify.py"
MANIFEST = REPO / "verification.toml"
passed = failed = 0


def check(name: str, cond: object, detail: str = "") -> None:
    global passed, failed
    ok = bool(cond)
    passed += int(ok)
    failed += int(not ok)
    print(f"[{'PASS' if ok else 'FAIL'}] {name}" + (f" ({detail})" if detail else ""))


manifest = tomllib.loads(MANIFEST.read_text(encoding="utf-8"))
suites = manifest.get("suite", {})
missing = [test for row in suites.values() for test in row.get("tests", []) if not (REPO / test).is_file()]
check("registered test files exist", not missing, repr(missing[:10]))

with tempfile.TemporaryDirectory(prefix="explicit-verify-") as td:
    root = Path(td)
    (root / "tools/testing").mkdir(parents=True)
    (root / "tests").mkdir()
    runner = root / "tools/testing/fast_verify.py"
    runner.write_text(RUNNER.read_text(encoding="utf-8"), encoding="utf-8")
    runner.chmod(0o755)
    (root / "tests/pass.py").write_text("print('[PASS] pass')\n", encoding="utf-8")
    (root / "tests/other.py").write_text("print('[PASS] other')\n", encoding="utf-8")
    (root / "verification.toml").write_text(textwrap.dedent('''\
        [verification]
        default_modes = ["full", "local"]
        core_suites = ["alpha"]
        [verification.groups]
        pair = ["alpha", "beta"]

        [suite.alpha]
        tests = ["tests/pass.py"]

        [suite.beta]
        tests = ["tests/other.py"]
    '''), encoding="utf-8")

    def run(*args: str):
        return subprocess.run([sys.executable, str(runner), *args, "--repo-root", str(root)], capture_output=True, text=True)

    none = run()
    check("no-argument invocation runs nothing", none.returncode == 0 and "No automatic verification plan" in none.stdout)
    one = run("alpha")
    check("explicit suite executes", one.returncode == 0 and "1 passed" in one.stdout)
    prefix = run("a")
    check("explicit prefix executes matching suite", prefix.returncode == 0 and "alpha" in prefix.stdout)
    group = run("@pair")
    check("explicit group executes", group.returncode == 0 and "2 passed" in group.stdout)
    core = run("core")
    check("core remains explicit", core.returncode == 0 and "1 passed" in core.stdout)
    auto = run("changed")
    check("changed-file auto-routing is refused", auto.returncode == 2 and "removed" in auto.stderr)

print(f"\nSummary: {passed} passed, {failed} failed")
raise SystemExit(1 if failed else 0)
