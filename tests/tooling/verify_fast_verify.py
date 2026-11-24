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
    (root / "tests").mkdir()
    run_log = root / "run-order"
    for name in ("alpha", "alpine", "beta"):
        (root / f"tests/{name}.py").write_text(
            "with open('run-order', 'a', encoding='utf-8') as stream:\n"
            f"    stream.write('{name}\\n')\n",
            encoding="utf-8",
        )
    (root / "verification.toml").write_text(textwrap.dedent('''\
        [verification]
        default_modes = ["full", "local"]
        core_suites = ["alpha"]
        [verification.groups]
        pair = ["alpine", "beta"]

        [suite.alpha]
        tests = ["tests/alpha.py"]

        [suite.alpine]
        tests = ["tests/alpine.py"]

        [suite.beta]
        tests = ["tests/beta.py"]
    '''), encoding="utf-8")

    def run(*args: str):
        return subprocess.run([sys.executable, str(RUNNER), *args, "--repo-root", str(root)], capture_output=True, text=True)

    none = run()
    check("no-argument invocation runs nothing", none.returncode == 0 and "No automatic verification plan" in none.stdout)
    empty_plan = run("plan")
    check("plan requires explicit selectors", empty_plan.returncode == 2 and "requires at least one explicit" in empty_plan.stderr)
    core_plan = run("plan", "core")
    check("core plan retains its mode selection", core_plan.returncode == 0 and "Plan (core): 1 suite(s), 1 test(s)" in core_plan.stdout)
    mixed_mode = run("plan", "core", "beta")
    check("plan rejects extra selectors after a special mode", mixed_mode.returncode == 2 and "core does not take extra selectors" in mixed_mode.stderr)

    selectors = ("beta", "@pair", "al")
    plan = run("plan", *selectors)
    planned_suites = [line.strip().partition(":")[0] for line in plan.stdout.splitlines() if line.startswith("  ")]
    check(
        "mixed plan preserves first occurrence and deduplicates suites",
        plan.returncode == 0
        and "3 suite(s), 3 test(s)" in plan.stdout
        and planned_suites == ["beta", "alpine", "alpha"],
        plan.stdout or plan.stderr,
    )

    for missing_selector in ("absent", "@missing"):
        bad_selectors = (*selectors, missing_selector)
        bad_plan = run("plan", *bad_selectors)
        bad_run = run(*bad_selectors)
        check(
            f"plan and execution reject unmatched selector {missing_selector}",
            bad_plan.returncode == bad_run.returncode == 2
            and not bad_plan.stdout and not bad_run.stdout
            and bad_plan.stderr == bad_run.stderr == f"No suite, prefix, or @group matches: {missing_selector}\n",
        )

    for removed_selector in ("changed", "branch"):
        for args in ((removed_selector,), ("plan", removed_selector)):
            removed = run(*args)
            check(f"{' '.join(args)} refuses changed-file routing", removed.returncode == 2 and "removed" in removed.stderr)
    check("bare invocation, previews and invalid selectors execute nothing", not run_log.exists())

    execution = run(*selectors, "--jobs", "1")
    executed_suites = run_log.read_text(encoding="utf-8").splitlines() if run_log.exists() else []
    check(
        "execution runs the previewed union once in plan order",
        execution.returncode == 0 and executed_suites == planned_suites,
        repr(executed_suites) if execution.returncode == 0 else execution.stdout + execution.stderr,
    )

    one = run("alpha")
    check("explicit suite executes", one.returncode == 0 and "1 passed" in one.stdout)
    prefix = run("a")
    check("explicit prefix executes both matching suites", prefix.returncode == 0 and "2 passed" in prefix.stdout)
    group = run("@pair")
    check("explicit group executes", group.returncode == 0 and "2 passed" in group.stdout)
    core = run("core")
    check("core remains explicit", core.returncode == 0 and "1 passed" in core.stdout)

print(f"\nSummary: {passed} passed, {failed} failed")
raise SystemExit(1 if failed else 0)
