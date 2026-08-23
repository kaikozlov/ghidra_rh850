#!/usr/bin/env python3
"""Authoritative repository verification runner.

``verification.toml`` owns every gate, its change paths, external inputs, and
its default evidence-oracle class.  Exit code 77 is the machine-readable skip
contract for optional prerequisites.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import time
import tomllib
from collections import Counter
from pathlib import Path

DEFAULT_ROOT = Path(__file__).resolve().parent.parent
SKIP_EXIT_CODE = 77
ORACLE_CLASSES = {
    "identity_hash",
    "documentation_lint",
    "generated_self_check",
    "raw_bytes",
    "instruction_semantics",
    "cfg_dataflow",
    "dynamic_trace",
    "independent_external_artifact",
}
SEMANTIC_ORACLES = {
    "raw_bytes",
    "instruction_semantics",
    "cfg_dataflow",
    "dynamic_trace",
    "independent_external_artifact",
}
ASSERTION_RE = re.compile(
    r"^(?:\[(PASS|FAIL)\](?:\[([a-z_]+)\])?|(PASS|FAIL):)",
    re.MULTILINE,
)


def load_manifest(path: Path) -> dict:
    with path.open("rb") as stream:
        return tomllib.load(stream)


def requirement_path(manifest: dict, root: Path, name: str,
                     external_root: Path | None = None) -> Path:
    item = manifest.get("external", {}).get(name)
    if not item:
        raise ValueError(f"suite references unknown external requirement {name!r}")
    if external_root is not None:
        return external_root
    env_name = item.get("env")
    if env_name and os.environ.get(env_name):
        return Path(os.environ[env_name]).expanduser()
    path = Path(item["path"])
    return path if path.is_absolute() else root / path


def missing_requirements(manifest: dict, root: Path, entry: dict,
                         external_root: Path | None = None) -> list[dict]:
    missing = []
    for name in entry.get("requires_external", []):
        path = requirement_path(manifest, root, name, external_root)
        if not path.exists():
            missing.append({"name": name, "path": str(path)})
    return missing


def assertion_counts(output: str, default_oracle: str) -> tuple[dict, dict]:
    passed: Counter[str] = Counter()
    failed: Counter[str] = Counter()
    for bracket_status, tagged_oracle, legacy_status in ASSERTION_RE.findall(output):
        status = bracket_status or legacy_status
        oracle = tagged_oracle or default_oracle
        if oracle not in ORACLE_CLASSES:
            oracle = default_oracle
        (passed if status == "PASS" else failed)[oracle] += 1
    return dict(sorted(passed.items())), dict(sorted(failed.items()))


def run_test(root: Path, test_path: str, entry: dict, manifest: dict,
             *, require_external: bool = False,
             external_root: Path | None = None,
             allow_optional_external: bool = False) -> dict:
    started = time.monotonic()
    full = root / test_path
    default_oracle = entry.get(
        "oracle", manifest.get("verification", {}).get("default_oracle", "raw_bytes")
    )
    missing = missing_requirements(manifest, root, entry, external_root)
    if missing:
        status = "fail" if require_external else "skip"
        detail = "missing external prerequisite(s): " + ", ".join(
            f"{item['name']}={item['path']}" for item in missing
        )
        return {
            "test": test_path,
            "status": status,
            "exit_code": 1 if require_external else SKIP_EXIT_CODE,
            "detail": detail,
            "oracle": default_oracle,
            "assertions": {"passed": {}, "failed": {}},
            "semantic_status": "not_executed",
            "duration_seconds": round(time.monotonic() - started, 3),
        }
    if not full.is_file():
        return {
            "test": test_path,
            "status": "fail",
            "exit_code": 1,
            "detail": "test file not found",
            "oracle": default_oracle,
            "assertions": {"passed": {}, "failed": {}},
            "semantic_status": "not_executed",
            "duration_seconds": round(time.monotonic() - started, 3),
        }

    child_env = dict(os.environ)
    child_env["RH850_VERIFY_EXTERNAL"] = "1" if allow_optional_external else "0"
    try:
        proc = subprocess.run(
            [sys.executable, str(full), *entry.get("args", [])],
            capture_output=True,
            text=True,
            cwd=root,
            env=child_env,
            timeout=entry.get("timeout", 300),
        )
        exit_code = proc.returncode
        passed, failed = assertion_counts(proc.stdout + "\n" + proc.stderr, default_oracle)
        failed_assertions = sum(failed.values())
        if exit_code == SKIP_EXIT_CODE:
            status = "fail" if require_external else "skip"
            detail = (
                "required external suite reported skip (exit 77)"
                if require_external else "suite reported skip (exit 77)"
            )
        elif exit_code != 0 or failed_assertions:
            status = "fail"
            detail = (
                f"suite printed {failed_assertions} failed assertion(s) with exit 0"
                if exit_code == 0 else f"suite exited with status {exit_code}"
            )
        else:
            status = "pass"
            detail = ""
        semantic_count = sum(passed.get(name, 0) for name in SEMANTIC_ORACLES)
        semantic_status = (
            "verified" if status == "pass" and semantic_count
            else "not_semantic" if status == "pass"
            else "not_executed"
        )
        return {
            "test": test_path,
            "status": status,
            "exit_code": exit_code,
            "stdout": proc.stdout,
            "stderr": proc.stderr,
            **({"detail": detail} if detail else {}),
            "oracle": default_oracle,
            "assertions": {"passed": passed, "failed": failed},
            "semantic_status": semantic_status,
            "duration_seconds": round(time.monotonic() - started, 3),
        }
    except subprocess.TimeoutExpired as error:
        return {
            "test": test_path,
            "status": "fail",
            "exit_code": 1,
            "detail": f"timed out after {entry.get('timeout', 300)} seconds",
            "oracle": default_oracle,
            "stdout": error.stdout or "",
            "stderr": error.stderr or "",
            "assertions": {"passed": {}, "failed": {}},
            "semantic_status": "not_executed",
            "duration_seconds": round(time.monotonic() - started, 3),
        }


def print_failure(result: dict) -> None:
    print(f"\n--- FAILED: {result['suite']} / {result['test']} ---", file=sys.stderr)
    if result.get("detail"):
        print(result["detail"], file=sys.stderr)
    if result.get("stdout"):
        print("--- stdout ---", file=sys.stderr)
        print(result["stdout"], file=sys.stderr)
    if result.get("stderr"):
        print("--- stderr ---", file=sys.stderr)
        print(result["stderr"], file=sys.stderr)


def write_failure_log(root: Path, result: dict, out_dir: Path | None = None) -> None:
    directory = out_dir or Path(os.environ.get("BUILD_LOGS", root / "build" / "logs")) / "verify"
    directory.mkdir(parents=True, exist_ok=True)
    (directory / f"{result['suite']}.log").write_text(
        f"=== DETAIL ===\n{result.get('detail', '')}\n"
        f"=== STDOUT ===\n{result.get('stdout', '')}\n"
        f"=== STDERR ===\n{result.get('stderr', '')}\n",
        encoding="utf-8",
    )


def selected_suites(manifest: dict, mode: str) -> list[str]:
    suites = manifest.get("suite", {})
    if mode == "required-external":
        return sorted(name for name, entry in suites.items() if entry.get("requires_external"))
    default_modes = manifest.get("verification", {}).get(
        "default_modes", ["core", "full", "local"]
    )
    return sorted(
        name for name, entry in suites.items()
        if mode in entry.get("modes", default_modes)
    )


def summarize(results: list[dict], mode: str) -> dict:
    statuses = Counter(item["status"] for item in results)
    oracle_passed: Counter[str] = Counter()
    oracle_failed: Counter[str] = Counter()
    for item in results:
        oracle_passed.update(item["assertions"]["passed"])
        oracle_failed.update(item["assertions"]["failed"])
    return {
        "mode": mode,
        "total": len(results),
        "passed": statuses["pass"],
        "failed": statuses["fail"],
        "skipped": statuses["skip"],
        "test_duration_seconds": round(sum(item.get("duration_seconds", 0.0) for item in results), 3),
        "assertions": {
            "passed_by_oracle": {name: oracle_passed[name] for name in sorted(ORACLE_CLASSES)},
            "failed_by_oracle": {name: oracle_failed[name] for name in sorted(ORACLE_CLASSES)},
        },
        "results": [
            {
                "suite": item["suite"],
                "test": item["test"],
                "status": item["status"],
                "oracle": item["oracle"],
                "semantic_status": item["semantic_status"],
                "duration_seconds": item.get("duration_seconds", 0.0),
                "assertions": item["assertions"],
                **({"detail": item["detail"]} if item.get("detail") else {}),
            }
            for item in results
        ],
    }


def execute_suites(root: Path, manifest: dict, suite_names: list[str], *,
                   mode: str, require_external: bool = False,
                   external_root: Path | None = None,
                   out_dir: Path | None = None, compact: bool = False,
                   allow_optional_external: bool = False) -> int:
    started = time.monotonic()
    results = []
    suites = manifest.get("suite", {})
    for suite_name in suite_names:
        entry = suites[suite_name]
        for test in entry.get("tests", []):
            result = run_test(
                root, test, entry, manifest,
                require_external=require_external,
                external_root=external_root,
                allow_optional_external=allow_optional_external,
            )
            result["suite"] = suite_name
            results.append(result)
            if not compact:
                print(f"[{result['status'].upper()}] {suite_name}: {test}")
                if result.get("detail"):
                    print(f"  {result['detail']}")
            if result["status"] == "fail":
                write_failure_log(root, result, out_dir)

    summary = summarize(results, mode)
    if compact:
        print(json.dumps(summary, indent=2))
    else:
        wall_seconds = time.monotonic() - started
        print(
            f"\nSummary: {summary['passed']} passed, {summary['failed']} failed, "
            f"{summary['skipped']} skipped in {wall_seconds:.2f}s"
        )
        print("Assertion passes by oracle: " + json.dumps(
            summary["assertions"]["passed_by_oracle"], sort_keys=True
        ))
        slow = sorted(results, key=lambda item: item.get("duration_seconds", 0.0), reverse=True)
        slow = [item for item in slow[:5] if item.get("duration_seconds", 0.0) >= 1.0]
        if slow:
            print("Slowest tests:")
            for item in slow:
                print(
                    f"  {item['duration_seconds']:.2f}s  {item['suite']}: {item['test']}"
                )
    for result in results:
        if result["status"] == "fail":
            print_failure(result)
    return 1 if summary["failed"] else 0


def changed_paths(root: Path, base: str) -> tuple[set[str] | None, str | None]:
    commands = (
        ["git", "diff", "--name-only", base],
        ["git", "ls-files", "--others", "--exclude-standard"],
    )
    changed: set[str] = set()
    for command in commands:
        try:
            proc = subprocess.run(command, cwd=root, capture_output=True, text=True, timeout=30)
        except subprocess.TimeoutExpired:
            return None, f"{' '.join(command)} timed out"
        if proc.returncode:
            return None, f"{' '.join(command)} failed: {proc.stderr.strip()}"
        changed.update(line for line in proc.stdout.splitlines() if line)
    return changed, None


def main() -> int:
    parser = argparse.ArgumentParser(description="Authoritative verification runner")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--suite")
    group.add_argument("--changed", action="store_true")
    group.add_argument("--core", action="store_true")
    group.add_argument("--full", action="store_true")
    group.add_argument("--local", action="store_true")
    group.add_argument("--required-external", action="store_true")
    group.add_argument("--agent", action="store_true")
    parser.add_argument("--base", default="HEAD")
    parser.add_argument("--manifest", type=Path)
    parser.add_argument("--repo-root", type=Path)
    parser.add_argument("--external-root", type=Path)
    parser.add_argument("--out-dir", type=Path)
    args = parser.parse_args()

    root = (args.repo_root or DEFAULT_ROOT).resolve()
    manifest_path = (args.manifest or root / "verification.toml").resolve()
    manifest = load_manifest(manifest_path)
    suites = manifest.get("suite", {})

    if args.suite:
        if args.suite not in suites:
            print(f"Unknown suite: {args.suite}", file=sys.stderr)
            return 2
        names, mode, required, compact = [args.suite], "suite", False, False
    elif args.changed:
        changed, error = changed_paths(root, args.base)
        if error:
            print(error, file=sys.stderr)
            return 1
        if not changed:
            print("No changes detected — nothing to verify.")
            return 0
        names = sorted({
            name for name, entry in suites.items()
            if any(path.startswith(pattern.rstrip("/"))
                   for pattern in (*entry.get("paths", []), *entry.get("tests", []))
                   for path in changed)
        })
        if not names:
            print("No suites matched changed files: " + ", ".join(sorted(changed)), file=sys.stderr)
            return 2
        mode, required, compact = "changed", False, False
    elif args.required_external:
        names, mode, required, compact = (
            selected_suites(manifest, "required-external"), "required-external", True, False
        )
        missing = {
            (item["name"], item["path"])
            for name in names
            for item in missing_requirements(
                manifest, root, suites[name], args.external_root
            )
        }
        if missing:
            detail = ", ".join(f"{name}={path}" for name, path in sorted(missing))
            print(f"Required external prerequisite missing: {detail}", file=sys.stderr)
            return 1
    elif args.agent:
        names, mode, required, compact = selected_suites(manifest, "core"), "core", False, True
    else:
        mode = "core" if args.core else "full" if args.full else "local"
        names, required, compact = selected_suites(manifest, mode), False, False

    allow_optional_external = mode in {"local", "required-external"}
    return execute_suites(
        root, manifest, names, mode=mode, require_external=required,
        external_root=args.external_root, out_dir=args.out_dir, compact=compact,
        allow_optional_external=allow_optional_external,
    )


if __name__ == "__main__":
    raise SystemExit(main())
