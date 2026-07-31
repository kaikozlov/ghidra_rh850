#!/usr/bin/env python3
"""Fast verification helper.

Reads verification.toml and supports three modes:
  verify-one SUITE=<name>      Run a single suite's test(s)
  verify-changed               Map git-changed paths to suites, run matching tests
  verify-agent                 Run all suites, capture output, emit compact JSON

Usage:
  uv run --locked python tools/fast_verify.py --suite control_partition
  uv run --locked python tools/fast_verify.py --changed
  uv run --locked python tools/fast_verify.py --changed --base main
  uv run --locked python tools/fast_verify.py --agent [--out-dir build/verify]
"""
from __future__ import annotations

import json
import subprocess
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PYTHON = sys.executable

# Directory for full failure logs (verify-one / verify-changed).
VERIFY_LOG_DIR = ROOT / "build" / "verify"


def load_ownership() -> dict:
    with open(ROOT / "verification.toml", "rb") as f:
        data = tomllib.load(f)
    return data.get("suite", {})


def run_suite(test_path: str) -> dict:
    """Run a single test file, returning structured result."""
    full = ROOT / test_path
    if not full.exists():
        return {"test": test_path, "status": "missing", "detail": "file not found"}

    proc = subprocess.run(
        [PYTHON, str(full)],
        capture_output=True,
        text=True,
        timeout=300,
    )
    return {
        "test": test_path,
        "status": "pass" if proc.returncode == 0 else "fail",
        "exit_code": proc.returncode,
        "stdout": proc.stdout,
        "stderr": proc.stderr,
    }


def write_full_log(result: dict) -> Path | None:
    """Write the complete stdout+stderr to build/verify/<suite>.log on failure."""
    if result["status"] != "fail":
        return None
    VERIFY_LOG_DIR.mkdir(parents=True, exist_ok=True)
    suite = result.get("suite", Path(result["test"]).stem)
    log_file = VERIFY_LOG_DIR / f"{suite}.log"
    log_file.write_text(
        f"=== STDOUT ===\n{result.get('stdout', '')}"
        f"\n=== STDERR ===\n{result.get('stderr', '')}\n"
    )
    return log_file


def print_failure(result: dict, suite: str | None = None) -> None:
    """Print both stdout and stderr for a failed test."""
    label = f"{suite} / {result['test']}" if suite else result["test"]
    print(f"\n--- FAILED: {label} ---", file=sys.stderr)
    if result.get("stdout"):
        print("--- stdout ---", file=sys.stderr)
        print(result["stdout"], file=sys.stderr)
    if result.get("stderr"):
        print("--- stderr ---", file=sys.stderr)
        print(result["stderr"], file=sys.stderr)


def verify_one(suite_name: str) -> int:
    ownership = load_ownership()
    if suite_name not in ownership:
        print(f"Unknown suite: {suite_name}", file=sys.stderr)
        print(f"Available: {', '.join(sorted(ownership))}", file=sys.stderr)
        return 2

    entry = ownership[suite_name]
    tests = entry.get("tests", [])
    if not tests:
        print(f"Suite '{suite_name}' has no tests", file=sys.stderr)
        return 1

    print(f"==> {suite_name} ({len(tests)} test file(s))")
    failed = 0
    for test in tests:
        result = run_suite(test)
        status = result["status"]
        if status == "pass":
            print(f"  [PASS] {test}")
        else:
            print(f"  [FAIL] {test}")
            result["suite"] = suite_name
            log_path = write_full_log(result)
            if log_path:
                print(f"  Full log: {log_path}", file=sys.stderr)
            print_failure(result, suite=suite_name)
            failed += 1

    return 1 if failed else 0


def verify_changed(base: str = "HEAD") -> int:
    # Get changed files (staged + unstaged vs the base ref).
    proc = subprocess.run(
        ["git", "diff", "--name-only", base],
        capture_output=True,
        text=True,
        cwd=ROOT,
    )
    changed = set(proc.stdout.strip().split("\n")) if proc.stdout.strip() else set()
    # Also include untracked files.
    proc = subprocess.run(
        ["git", "ls-files", "--others", "--exclude-standard"],
        capture_output=True,
        text=True,
        cwd=ROOT,
    )
    if proc.stdout.strip():
        changed.update(proc.stdout.strip().split("\n"))

    if not changed:
        print("No changes detected — nothing to verify.")
        return 0

    ownership = load_ownership()
    matched_suites = set()
    for suite_name, entry in ownership.items():
        for pattern in entry.get("paths", []):
            for changed_file in changed:
                if changed_file.startswith(pattern.rstrip("/")):
                    matched_suites.add(suite_name)
                    break

    if not matched_suites:
        print(f"No suites matched changed files: {', '.join(sorted(changed))}", file=sys.stderr)
        print(
            "(If you changed tools/scripts without a suite mapping, "
            "run 'make verify' for the full gate.)",
            file=sys.stderr,
        )
        return 2

    print(f"Changed files: {len(changed)}")
    print(f"Matched suites: {', '.join(sorted(matched_suites))}")
    print()

    failed = 0
    for suite_name in sorted(matched_suites):
        entry = ownership[suite_name]
        for test in entry.get("tests", []):
            result = run_suite(test)
            status = result["status"]
            if status == "pass":
                print(f"  [PASS] {suite_name}: {test}")
            else:
                print(f"  [FAIL] {suite_name}: {test}")
                result["suite"] = suite_name
                log_path = write_full_log(result)
                if log_path:
                    print(f"  Full log: {log_path}", file=sys.stderr)
                print_failure(result, suite=suite_name)
                failed += 1

    return 1 if failed else 0


def verify_agent(out_dir: str | None = None) -> int:
    resolved_out = Path(out_dir) if out_dir else (ROOT / "build" / "verify")
    resolved_out.mkdir(parents=True, exist_ok=True)

    ownership = load_ownership()
    results = []
    total = 0
    passed = 0
    failed = 0

    for suite_name in sorted(ownership):
        entry = ownership[suite_name]
        for test in entry.get("tests", []):
            total += 1
            result = run_suite(test)
            result["suite"] = suite_name
            results.append(result)
            if result["status"] == "pass":
                passed += 1
            else:
                failed += 1
                # Write full log for failures.
                log_file = resolved_out / f"{suite_name}.log"
                log_file.write_text(
                    f"=== STDOUT ===\n{result.get('stdout', '')}"
                    f"\n=== STDERR ===\n{result.get('stderr', '')}\n"
                )

    summary = {
        "total": total,
        "passed": passed,
        "failed": failed,
        "results": [
            {"suite": r["suite"], "test": r["test"], "status": r["status"]}
            for r in results
        ],
    }

    # Print compact JSON summary to stdout.
    print(json.dumps(summary, indent=2))

    # Print full output (both streams) for failures.
    for r in results:
        if r["status"] == "fail":
            print_failure(r, suite=r["suite"])

    return 1 if failed else 0


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Fast verification helper")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--suite", help="Run a single suite by name")
    group.add_argument("--changed", action="store_true", help="Run suites matching git changes")
    group.add_argument("--agent", action="store_true", help="Run all suites with compact JSON output")
    parser.add_argument("--base", default="HEAD", help="Git ref to compare against for --changed (default: HEAD)")
    parser.add_argument("--out-dir", help="Directory for verify-agent logs (default: build/verify)")
    args = parser.parse_args()

    if args.suite:
        return verify_one(args.suite)
    elif args.changed:
        return verify_changed(base=args.base)
    elif args.agent:
        return verify_agent(args.out_dir)
    return 0


if __name__ == "__main__":
    sys.exit(main())
