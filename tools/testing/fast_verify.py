#!/usr/bin/env python3
"""Small explicit verification runner.

Verification in this repository is intentionally opt-in.  The manifest is a
registry of named suites, not a changed-file ownership graph.  Documentation,
status ledgers, provenance metadata, and unrelated source files never select
verification automatically.

Examples:
    tools/test camry_f33_b6_stationary_probe
    tools/test camry_f33
    tools/test @exploit
    tools/test core
    tools/test full
    tools/test list [query]
    tools/test plan <suite-or-prefix|core|full|local>

Running ``tools/test`` with no selector performs no tests and exits successfully.
Choose the smallest suite that exercises the code/evidence you actually changed.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import threading
import time
import tomllib
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

DEFAULT_ROOT = Path(__file__).resolve().parents[2]
SKIP_EXIT_CODE = 77


def load_manifest(path: Path) -> dict:
    with path.open("rb") as stream:
        return tomllib.load(stream)


def core_suite_names(manifest: dict) -> set[str]:
    configured = manifest.get("verification", {}).get("core_suites", [])
    return set(configured) & set(manifest.get("suite", {}))


def suite_modes(manifest: dict, name: str, entry: dict) -> list[str]:
    modes = list(entry.get("modes", manifest.get("verification", {}).get("default_modes", ["full", "local"])))
    if name in core_suite_names(manifest) and "core" not in modes:
        modes.insert(0, "core")
    return modes


def selected_suites(manifest: dict, mode: str) -> list[str]:
    suites = manifest.get("suite", {})
    if mode == "required-external":
        return sorted(name for name, entry in suites.items() if entry.get("requires_external"))
    if mode == "core":
        return sorted(core_suite_names(manifest))
    default_modes = manifest.get("verification", {}).get("default_modes", ["full", "local"])
    return sorted(name for name, entry in suites.items() if mode in entry.get("modes", default_modes))


def _dedupe(values: list[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for value in values:
        if value not in seen:
            seen.add(value)
            out.append(value)
    return out


def resolve_query(manifest: dict, query: str) -> list[str]:
    suites = manifest.get("suite", {})
    if query.startswith("@"):
        members = manifest.get("verification", {}).get("groups", {}).get(query[1:])
        if not members:
            return []
        names: list[str] = []
        for member in members:
            names.extend(resolve_query(manifest, str(member)))
        return _dedupe(names)
    if query in suites:
        return [query]
    return sorted(name for name in suites if name.startswith(query))


def requirement_path(manifest: dict, root: Path, name: str, external_root: Path | None = None) -> Path:
    row = manifest.get("external", {}).get(name)
    if not row:
        raise ValueError(f"unknown external prerequisite {name!r}")
    if external_root is not None:
        return external_root
    env_name = row.get("env")
    if env_name and os.environ.get(env_name):
        return Path(os.environ[env_name]).expanduser()
    path = Path(row["path"])
    return path if path.is_absolute() else root / path


def missing_requirements(manifest: dict, root: Path, entry: dict, external_root: Path | None) -> list[tuple[str, str]]:
    missing: list[tuple[str, str]] = []
    for name in entry.get("requires_external", []):
        path = requirement_path(manifest, root, name, external_root)
        if not path.exists():
            missing.append((name, str(path)))
    return missing


def suite_is_serial(name: str, entry: dict) -> bool:
    if entry.get("serial") or entry.get("requires_external"):
        return True
    if "_live" in name:
        return True
    return any("_live" in Path(test).name for test in entry.get("tests", []))


def run_one(
    root: Path,
    manifest: dict,
    suite_name: str,
    entry: dict,
    test: str,
    *,
    require_external: bool,
    external_root: Path | None,
    allow_external: bool,
) -> dict:
    started = time.monotonic()
    missing = missing_requirements(manifest, root, entry, external_root)
    if missing:
        detail = "missing external prerequisite(s): " + ", ".join(f"{n}={p}" for n, p in missing)
        if require_external:
            return {"suite": suite_name, "test": test, "status": "fail", "detail": detail, "duration": 0.0}
        return {"suite": suite_name, "test": test, "status": "skip", "detail": detail, "duration": 0.0}

    path = root / test
    if not path.is_file():
        return {"suite": suite_name, "test": test, "status": "fail", "detail": "test file not found", "duration": 0.0}

    env = dict(os.environ)
    current_pythonpath = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = str(root) + (os.pathsep + current_pythonpath if current_pythonpath else "")
    env["RH850_VERIFY_EXTERNAL"] = "1" if allow_external else "0"
    timeout = entry.get("timeout", 300)
    try:
        proc = subprocess.run(
            [sys.executable, str(path), *entry.get("args", [])],
            cwd=root,
            env=env,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired as exc:
        return {
            "suite": suite_name,
            "test": test,
            "status": "fail",
            "detail": f"timed out after {timeout}s",
            "stdout": exc.stdout or "",
            "stderr": exc.stderr or "",
            "duration": round(time.monotonic() - started, 3),
        }

    if proc.returncode == SKIP_EXIT_CODE:
        status = "fail" if require_external else "skip"
        detail = "required external suite skipped" if require_external else "suite skipped"
    elif proc.returncode:
        status = "fail"
        detail = f"exit {proc.returncode}"
    else:
        status = "pass"
        detail = ""
    return {
        "suite": suite_name,
        "test": test,
        "status": status,
        "detail": detail,
        "stdout": proc.stdout,
        "stderr": proc.stderr,
        "duration": round(time.monotonic() - started, 3),
    }


def print_plan(manifest: dict, names: list[str], label: str) -> None:
    suites = manifest.get("suite", {})
    count = sum(len(suites[name].get("tests", [])) for name in names)
    print(f"Plan ({label}): {len(names)} suite(s), {count} test(s)")
    for name in names:
        entry = suites[name]
        modes = ",".join(suite_modes(manifest, name, entry))
        ext = ",".join(entry.get("requires_external", []))
        suffix = f" external={ext}" if ext else ""
        print(f"  {name}: {len(entry.get('tests', []))} test(s) modes={modes}{suffix}")


def execute(
    root: Path,
    manifest: dict,
    names: list[str],
    *,
    mode: str,
    require_external: bool,
    external_root: Path | None,
    allow_skips: bool,
    jobs: int,
    compact_json: bool,
) -> int:
    suites = manifest.get("suite", {})
    workers = jobs if jobs > 0 else (os.cpu_count() or 1)
    allow_external = mode in {"local", "required-external"} or require_external
    if allow_skips:
        allow_external = True

    work_parallel: list[tuple[str, dict, str]] = []
    work_serial: list[tuple[str, dict, str]] = []
    for name in names:
        entry = suites[name]
        bucket = work_serial if suite_is_serial(name, entry) or workers == 1 else work_parallel
        for test in entry.get("tests", []):
            bucket.append((name, entry, test))

    results: list[dict] = []
    lock = threading.Lock()

    def run(item: tuple[str, dict, str]) -> dict:
        name, entry, test = item
        result = run_one(
            root, manifest, name, entry, test,
            require_external=require_external and not allow_skips,
            external_root=external_root,
            allow_external=allow_external,
        )
        if not compact_json:
            with lock:
                print(f"[{result['status'].upper()}] {name}: {test}")
                if result.get("detail"):
                    print(f"  {result['detail']}")
        return result

    if work_parallel:
        with ThreadPoolExecutor(max_workers=workers) as pool:
            futures = [pool.submit(run, item) for item in work_parallel]
            for future in as_completed(futures):
                results.append(future.result())
    for item in work_serial:
        results.append(run(item))

    counts = Counter(row["status"] for row in results)
    failures = [row for row in results if row["status"] == "fail"]
    if compact_json:
        print(json.dumps({
            "mode": mode,
            "passed": counts["pass"],
            "failed": counts["fail"],
            "skipped": counts["skip"],
            "results": [
                {k: row[k] for k in ("suite", "test", "status", "duration", "detail") if k in row}
                for row in results
            ],
        }, indent=2))
    else:
        print(f"\nSummary: {counts['pass']} passed, {counts['fail']} failed, {counts['skip']} skipped")
        for row in failures:
            print(f"\n--- FAILED: {row['suite']} / {row['test']} ---", file=sys.stderr)
            if row.get("detail"):
                print(row["detail"], file=sys.stderr)
            if row.get("stdout"):
                print(row["stdout"], file=sys.stderr)
            if row.get("stderr"):
                print(row["stderr"], file=sys.stderr)
    return 1 if failures else 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Explicit repository verification runner")
    parser.add_argument("command", nargs="?", help="suite/prefix/@group, list, plan, core, full, local, required-external")
    parser.add_argument("query", nargs="*")
    parser.add_argument("--suite")
    parser.add_argument("--core", action="store_true")
    parser.add_argument("--full", action="store_true")
    parser.add_argument("--local", action="store_true")
    parser.add_argument("--required-external", action="store_true")
    parser.add_argument("--agent", action="store_true", help="core suite with compact JSON output")
    parser.add_argument("--allow-skips", action="store_true")
    parser.add_argument("--jobs", type=int, default=0)
    parser.add_argument("--manifest", type=Path)
    parser.add_argument("--repo-root", type=Path)
    parser.add_argument("--external-root", type=Path)
    args = parser.parse_args()

    root = (args.repo_root or DEFAULT_ROOT).resolve()
    manifest = load_manifest((args.manifest or root / "verification.toml").resolve())
    suites = manifest.get("suite", {})

    if args.command in {"changed", "branch"} or (args.command == "plan" and args.query and args.query[0] in {"changed", "branch"}):
        print("Automatic changed-file verification was removed. Select the relevant suite explicitly.", file=sys.stderr)
        return 2

    if args.command == "list":
        if len(args.query) > 1:
            parser.error("list takes at most one query")
        names = resolve_query(manifest, args.query[0]) if args.query else sorted(suites)
        if not names:
            return 2
        print_plan(manifest, names, args.query[0] if args.query else "all")
        return 0

    if args.command == "plan":
        if len(args.query) != 1:
            parser.error("plan requires one explicit suite/prefix/@group/core/full/local selector")
        selector = args.query[0]
        if selector in {"core", "full", "local"}:
            names = selected_suites(manifest, selector)
        else:
            names = resolve_query(manifest, selector)
        if not names:
            print(f"No suite, prefix, or @group matches: {selector}", file=sys.stderr)
            return 2
        print_plan(manifest, names, selector)
        return 0

    legacy = [args.suite, args.core, args.full, args.local, args.required_external, args.agent]
    if args.command and any(legacy):
        parser.error("positional selector cannot be combined with legacy mode flags")

    compact = False
    require_external = False
    mode = "suite"
    names: list[str] = []

    if args.command in {"core", "full", "local", "required-external"}:
        if args.query:
            parser.error(f"{args.command} does not take extra selectors")
        mode = args.command
        names = selected_suites(manifest, mode)
        require_external = mode == "required-external"
    elif args.command:
        selectors = [args.command, *args.query]
        for selector in selectors:
            resolved = resolve_query(manifest, selector)
            if not resolved:
                print(f"No suite, prefix, or @group matches: {selector}", file=sys.stderr)
                return 2
            names.extend(resolved)
        names = _dedupe(names)
        require_external = any(suites[name].get("requires_external") for name in names) and not args.allow_skips
    elif args.suite:
        names = resolve_query(manifest, args.suite)
        if not names:
            print(f"Unknown suite: {args.suite}", file=sys.stderr)
            return 2
    elif args.core or args.agent:
        mode = "core"
        names = selected_suites(manifest, mode)
        compact = args.agent
    elif args.full:
        mode = "full"
        names = selected_suites(manifest, mode)
    elif args.local:
        mode = "local"
        names = selected_suites(manifest, mode)
    elif args.required_external:
        mode = "required-external"
        names = selected_suites(manifest, mode)
        require_external = True
    else:
        print("No automatic verification plan. Run `tools/test <suite-or-prefix>` for the code/evidence you changed.")
        return 0

    return execute(
        root, manifest, names,
        mode=mode,
        require_external=require_external,
        external_root=args.external_root,
        allow_skips=args.allow_skips,
        jobs=args.jobs,
        compact_json=compact,
    )


if __name__ == "__main__":
    raise SystemExit(main())
