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
import threading
import time
import tomllib
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
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
FINDING_ID_RE = re.compile(r"\b[A-Z][A-Z0-9]*(?:-[A-Z][A-Z0-9]*)*-\d{3}\b")
TEST_REFERENCE_RE = re.compile(r"(?:tests/)?(verify_[A-Za-z0-9_]+\.py)\b")
AGGREGATE_LEDGERS = {
    "docs/status/FINDINGS.md": "findings",
    "docs/status/OPEN_QUESTIONS.md": "stable_ids",
    "docs/status/CORRECTIONS.md": "stable_ids",
    "docs/status/PRIORITIES.md": "stable_ids",
}
PORTABLE_BROAD_INVALIDATORS = (
    "firmware/",
)


@dataclass(frozen=True)
class ChangeSet:
    paths: set[str]
    base: str
    base_description: str
    untracked: set[str]


@dataclass(frozen=True)
class LedgerDiff:
    changed_lines: list[str]
    old_lines: list[str]
    new_lines: list[str]
    old_numbers: set[int]
    new_numbers: set[int]


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


def suite_modes(manifest: dict, entry: dict) -> list[str]:
    return entry.get(
        "modes",
        manifest.get("verification", {}).get("default_modes", ["core", "full", "local"]),
    )


def resolve_query(manifest: dict, query: str) -> list[str]:
    suites = manifest.get("suite", {})
    if query in suites:
        return [query]
    return sorted(name for name in suites if name.startswith(query))


def print_suite_listing(manifest: dict, query: str | None = None) -> int:
    names = resolve_query(manifest, query) if query else sorted(manifest.get("suite", {}))
    if not names:
        print(f"No suite or suite-prefix matches: {query}", file=sys.stderr)
        return 2
    suites = manifest["suite"]
    test_count = sum(len(suites[name].get("tests", [])) for name in names)
    label = f"Prefix {query!r}" if query and query not in suites else (
        f"Suite {query!r}" if query else "All suites"
    )
    print(f"{label}: {len(names)} suite(s), {test_count} test(s)")
    print("Any leading suite-name prefix can be used as a family query.")
    for name in names:
        entry = suites[name]
        modes = ",".join(suite_modes(manifest, entry)) or "explicit-only"
        external = ",".join(entry.get("requires_external", []))
        suffix = f" external={external}" if external else ""
        print(f"  {name}: {len(entry.get('tests', []))} test(s) modes={modes}{suffix}")
    return 0


def path_matches_pattern(path: str, pattern: str) -> bool:
    """Match exact files exactly and explicit directory patterns by prefix."""
    return path.startswith(pattern) if pattern.endswith("/") else path == pattern


def suites_matching_paths(manifest: dict, changed: set[str]) -> set[str]:
    return {
        name
        for name, entry in manifest.get("suite", {}).items()
        if any(
            path_matches_pattern(path, pattern)
            for pattern in (*entry.get("paths", []), *entry.get("tests", []))
            for path in changed
        )
    }


def _run_git(root: Path, args: list[str]) -> tuple[str | None, str | None]:
    command = ["git", *args]
    try:
        proc = subprocess.run(command, cwd=root, capture_output=True, text=True, timeout=30)
    except subprocess.TimeoutExpired:
        return None, f"{' '.join(command)} timed out"
    if proc.returncode:
        return None, f"{' '.join(command)} failed: {proc.stderr.strip()}"
    return proc.stdout.strip(), None


def resolve_change_base(
    root: Path, override: str | None, *, branch: bool = False
) -> tuple[str | None, str | None, str | None]:
    if override:
        resolved, error = _run_git(root, ["rev-parse", "--verify", override])
        if error:
            return None, None, error
        return override, f"explicit base {override} ({resolved[:12]})", None

    if not branch:
        head, error = _run_git(root, ["rev-parse", "--verify", "HEAD"])
        if error:
            return None, None, error
        return "HEAD", f"working tree against HEAD ({head[:12]})", None

    branch_name, error = _run_git(root, ["rev-parse", "--abbrev-ref", "HEAD"])
    if error:
        return None, None, error
    if branch_name == "HEAD":
        return None, None, (
            "Cannot infer committed change base from detached HEAD; "
            "pass --base <ref> explicitly."
        )

    upstream, error = _run_git(
        root, ["rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{upstream}"]
    )
    if error or not upstream:
        return None, None, (
            f"Cannot infer committed change base: branch {branch_name!r} has no configured "
            "upstream; pass --base <ref> explicitly."
        )
    ahead_text, error = _run_git(root, ["rev-list", "--count", f"{upstream}..HEAD"])
    if error:
        return None, None, error
    if ahead_text and int(ahead_text) > 0:
        merge_base, error = _run_git(root, ["merge-base", "HEAD", upstream])
        if error:
            return None, None, error
        return merge_base, f"merge-base with {upstream} ({merge_base[:12]})", None
    head, error = _run_git(root, ["rev-parse", "--verify", "HEAD"])
    if error:
        return None, None, error
    return "HEAD", f"working tree against HEAD ({head[:12]})", None


def changed_paths(
    root: Path, base_override: str | None, *, branch: bool = False
) -> tuple[ChangeSet | None, str | None]:
    base, description, error = resolve_change_base(root, base_override, branch=branch)
    if error:
        return None, error
    diff, error = _run_git(root, ["diff", "--name-only", "--no-renames", base, "--"])
    if error:
        return None, error
    untracked_text, error = _run_git(root, ["ls-files", "--others", "--exclude-standard"])
    if error:
        return None, error
    tracked_changes = set(diff.splitlines()) if diff else set()
    untracked = set(untracked_text.splitlines()) if untracked_text else set()
    return ChangeSet(tracked_changes | untracked, base, description, untracked), None


def _parse_ledger_diff(diff: str) -> tuple[list[str], set[int], set[int]]:
    changed: list[str] = []
    old_numbers: set[int] = set()
    new_numbers: set[int] = set()
    old_line = new_line = 0
    in_hunk = False
    hunk_re = re.compile(r"^@@ -(\d+)(?:,\d+)? \+(\d+)(?:,\d+)? @@")
    for line in diff.splitlines():
        match = hunk_re.match(line)
        if match:
            old_line, new_line = map(int, match.groups())
            in_hunk = True
            continue
        if not in_hunk or line.startswith(("+++", "---")):
            continue
        if line.startswith("-"):
            changed.append(line[1:])
            old_numbers.add(old_line)
            old_line += 1
        elif line.startswith("+"):
            changed.append(line[1:])
            new_numbers.add(new_line)
            new_line += 1
        elif line.startswith(" "):
            old_line += 1
            new_line += 1
    return changed, old_numbers, new_numbers


def _git_file_lines(root: Path, revision: str, path: str) -> list[str]:
    proc = subprocess.run(
        ["git", "show", f"{revision}:{path}"],
        cwd=root, capture_output=True, text=True, timeout=30,
    )
    return proc.stdout.splitlines() if proc.returncode == 0 else []


def changed_ledger(
    root: Path, changes: ChangeSet, path: str
) -> tuple[LedgerDiff | None, str | None]:
    if path in changes.untracked:
        try:
            new_lines = (root / path).read_text(encoding="utf-8").splitlines()
            return LedgerDiff(
                new_lines, [], new_lines, set(), set(range(1, len(new_lines) + 1))
            ), None
        except (OSError, UnicodeError) as error:
            return None, f"cannot read changed aggregate ledger {path}: {error}"
    diff, error = _run_git(
        root, ["diff", "--unified=0", "--no-ext-diff", changes.base, "--", path]
    )
    if error:
        return None, error
    changed, old_numbers, new_numbers = _parse_ledger_diff(diff)
    old_lines = _git_file_lines(root, changes.base, path)
    try:
        new_lines = (root / path).read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeError):
        new_lines = []
    return LedgerDiff(changed, old_lines, new_lines, old_numbers, new_numbers), None


def aggregate_infrastructure_suites(manifest: dict) -> set[str]:
    configured = manifest.get("verification", {}).get(
        "aggregate_infrastructure_suites",
        ["analysis_status", "doc_links", "knowledge_index"],
    )
    return set(configured) & set(manifest.get("suite", {}))


def _owned_text_paths(root: Path, entry: dict) -> set[Path]:
    root = root.resolve()
    excluded = {(root / value).resolve() for value in AGGREGATE_LEDGERS}
    result: set[Path] = set()
    candidates = (*entry.get("tests", []), *entry.get("paths", []))
    for value in candidates:
        if not value.startswith(("tests/", "docs/")):
            continue
        path = (root / value.rstrip("/")).resolve()
        try:
            path.relative_to(root)
        except ValueError:
            continue
        if path in excluded:
            continue
        if value.endswith("/"):
            if path.is_dir():
                for item in path.rglob("*"):
                    if not item.is_file():
                        continue
                    resolved = item.resolve()
                    try:
                        resolved.relative_to(root)
                    except ValueError:
                        continue
                    if resolved not in excluded:
                        result.add(resolved)
        elif path.is_file():
            result.add(path)
    return result


def suites_mentioning_ids(root: Path, manifest: dict, ids: set[str]) -> set[str]:
    if not ids:
        return set()
    cache: dict[Path, str] = {}
    matches: set[str] = set()
    for name, entry in manifest.get("suite", {}).items():
        for path in _owned_text_paths(root, entry):
            if path not in cache:
                try:
                    cache[path] = path.read_text(encoding="utf-8")
                except (OSError, UnicodeError):
                    cache[path] = ""
            if any(stable_id in cache[path] for stable_id in ids):
                matches.add(name)
                break
    return matches


def suites_for_test_references(manifest: dict, lines: list[str]) -> set[str]:
    owners: dict[str, set[str]] = {}
    for name, entry in manifest.get("suite", {}).items():
        for test in entry.get("tests", []):
            owners.setdefault(Path(test).name, set()).add(name)
    referenced = {match for line in lines for match in TEST_REFERENCE_RE.findall(line)}
    return {owner for test in referenced for owner in owners.get(test, set())}


def _enclosing_ids(path: str, lines: list[str], line_number: int) -> set[str]:
    if not lines or line_number < 1 or line_number > len(lines):
        return set()
    index = line_number - 1
    line = lines[index]
    direct = set(FINDING_ID_RE.findall(line))
    if line.startswith("#"):
        return direct

    if path == "docs/status/OPEN_QUESTIONS.md":
        enclosing: set[str] = set()
        if not line.startswith(("  ", "\t")):
            return direct
        for candidate in reversed(lines[:index]):
            if candidate.startswith("#"):
                break
            match = re.match(r"^-\s+\*\*(OQ-\d{3})\b", candidate)
            if match:
                enclosing.add(match.group(1))
                break
            if candidate.startswith("-") and candidate.strip():
                break
        return direct | enclosing

    if path == "docs/status/CORRECTIONS.md":
        enclosing: set[str] = set()
        for candidate in reversed(lines[:index]):
            match = re.match(r"^###\s+(CORR-\d{3})\b", candidate)
            if match:
                enclosing.add(match.group(1))
                break
            if candidate.startswith("#"):
                break
        return direct | enclosing

    if path == "docs/status/PRIORITIES.md":
        start = index
        while start > 0 and lines[start - 1].strip():
            start -= 1
        end = index + 1
        while end < len(lines) and lines[end].strip():
            end += 1
        enclosing = {
            stable_id
            for candidate in lines[start:end]
            for stable_id in FINDING_ID_RE.findall(candidate)
        }
        return direct | enclosing
    return direct


def enclosing_changed_ids(path: str, diff: LedgerDiff) -> set[str]:
    ids = {
        stable_id
        for number in diff.old_numbers
        for stable_id in _enclosing_ids(path, diff.old_lines, number)
    }
    ids.update(
        stable_id
        for number in diff.new_numbers
        for stable_id in _enclosing_ids(path, diff.new_lines, number)
    )
    return ids


def has_unresolved_structural_line(path: str, diff: LedgerDiff) -> bool:
    for lines, numbers in (
        (diff.old_lines, diff.old_numbers),
        (diff.new_lines, diff.new_numbers),
    ):
        for number in numbers:
            if number < 1 or number > len(lines):
                continue
            line = lines[number - 1]
            if not line.strip():
                continue
            if FINDING_ID_RE.search(line) or TEST_REFERENCE_RE.search(line):
                continue
            if not _enclosing_ids(path, lines, number):
                return True
    return False


def route_aggregate_ledger(
    root: Path, manifest: dict, changes: ChangeSet, path: str
) -> tuple[set[str], str, str | None]:
    infrastructure = aggregate_infrastructure_suites(manifest)
    broad = suites_matching_paths(manifest, {path})
    ledger_diff, error = changed_ledger(root, changes, path)
    if error:
        return broad | infrastructure, "broad fallback (diff unavailable)", error
    assert ledger_diff is not None
    diff_lines = ledger_diff.changed_lines
    ids = enclosing_changed_ids(path, ledger_diff)
    if has_unresolved_structural_line(path, ledger_diff):
        return broad | infrastructure, "broad fallback (structural change)", None
    routed = suites_mentioning_ids(root, manifest, ids)
    if AGGREGATE_LEDGERS[path] == "findings":
        routed |= suites_for_test_references(manifest, diff_lines)
    if not ids and not routed:
        return broad | infrastructure, "broad fallback (structural change)", None
    if not routed:
        return broad | infrastructure, "broad fallback (unowned stable IDs)", None
    return routed | infrastructure, "content-aware stable-ID/test routing", None


def plan_changed_suites(
    root: Path, manifest: dict, changes: ChangeSet
) -> tuple[list[str], list[str], list[str], list[str]]:
    notes: list[str] = []
    warnings: list[str] = []
    aggregate_paths = set(AGGREGATE_LEDGERS) & changes.paths
    ordinary_paths = changes.paths - aggregate_paths
    names: set[str] = set()
    matched_paths: set[str] = set()
    for path in ordinary_paths:
        owners = suites_matching_paths(manifest, {path})
        if owners:
            matched_paths.add(path)
            names |= owners

    invalidators = {
        path
        for path in ordinary_paths
        if any(path_matches_pattern(path, pattern) for pattern in PORTABLE_BROAD_INVALIDATORS)
    }
    if invalidators:
        names |= set(selected_suites(manifest, "full"))
        notes.append(
            "portable full invalidator(s): " + ", ".join(sorted(invalidators))
        )
    unmatched = sorted(ordinary_paths - matched_paths - invalidators)
    retired = [
        path
        for path in unmatched
        if path.startswith("tests/verify_")
        and path.endswith(".py")
        and not (root / path).exists()
    ]
    if retired:
        retired_set = set(retired)
        unmatched = [path for path in unmatched if path not in retired_set]
        notes.append("retired test file(s): " + ", ".join(retired))

    for path in sorted(aggregate_paths):
        routed, note, warning = route_aggregate_ledger(root, manifest, changes, path)
        names |= routed
        notes.append(f"{path}: {note} ({len(routed)} suite(s))")
        if warning:
            warnings.append(warning)
    return sorted(names), notes, warnings, unmatched


def print_plan(
    manifest: dict, names: list[str], *, label: str, notes: list[str] | None = None
) -> None:
    suites = manifest.get("suite", {})
    test_count = sum(len(suites[name].get("tests", [])) for name in names)
    print(f"Plan ({label}): {len(names)} suite(s), {test_count} test(s)")
    for note in notes or []:
        print(f"  note: {note}")
    for name in names:
        entry = suites[name]
        modes = ",".join(suite_modes(manifest, entry)) or "explicit-only"
        external = ",".join(entry.get("requires_external", []))
        suffix = f" external={external}" if external else ""
        print(f"  {name}: {len(entry.get('tests', []))} test(s) modes={modes}{suffix}")


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


def suite_is_serial(name: str, entry: dict) -> bool:
    """Live Ghidra, external-corpus, and explicitly serial suites stay off the pool."""
    if entry.get("serial") or entry.get("requires_external"):
        return True
    if "_live" in name:
        return True
    return any("_live" in Path(test).name for test in entry.get("tests", []))


def _report_result(result: dict, *, compact: bool, root: Path,
                   out_dir: Path | None, print_lock: threading.Lock) -> None:
    with print_lock:
        if not compact:
            print(f"[{result['status'].upper()}] {result['suite']}: {result['test']}")
            if result.get("detail"):
                print(f"  {result['detail']}")
        if result["status"] == "fail":
            write_failure_log(root, result, out_dir)


def execute_suites(root: Path, manifest: dict, suite_names: list[str], *,
                   mode: str, require_external: bool = False,
                   external_root: Path | None = None,
                   out_dir: Path | None = None, compact: bool = False,
                   allow_optional_external: bool = False,
                   jobs: int = 0) -> int:
    started = time.monotonic()
    results: list[dict] = []
    suites = manifest.get("suite", {})
    print_lock = threading.Lock()
    workers = jobs if jobs > 0 else (os.cpu_count() or 1)

    def run_one(suite_name: str, test: str, entry: dict) -> dict:
        suite_allows_external = allow_optional_external
        if mode in {"changed", "suite", "branch"} and not entry.get("requires_external"):
            suite_allows_external = False
        result = run_test(
            root, test, entry, manifest,
            require_external=require_external,
            external_root=external_root,
            allow_optional_external=suite_allows_external,
        )
        result["suite"] = suite_name
        _report_result(
            result, compact=compact, root=root, out_dir=out_dir, print_lock=print_lock
        )
        return result

    parallel: list[tuple[str, str, dict]] = []
    serial: list[tuple[str, str, dict]] = []
    for suite_name in suite_names:
        entry = suites[suite_name]
        bucket = serial if suite_is_serial(suite_name, entry) or workers == 1 else parallel
        for test in entry.get("tests", []):
            bucket.append((suite_name, test, entry))

    if parallel:
        with ThreadPoolExecutor(max_workers=workers) as pool:
            futures = [
                pool.submit(run_one, suite_name, test, entry)
                for suite_name, test, entry in parallel
            ]
            for future in as_completed(futures):
                results.append(future.result())
    for suite_name, test, entry in serial:
        results.append(run_one(suite_name, test, entry))

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


def _dedupe_names(names: list[str]) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for name in names:
        if name in seen:
            continue
        seen.add(name)
        ordered.append(name)
    return ordered


def main() -> int:
    parser = argparse.ArgumentParser(description="Authoritative verification runner")
    parser.add_argument(
        "command", nargs="?",
        help="suite/prefix, list [query], plan [changed|branch|query], "
        "core/full/local/branch, or additional suite names",
    )
    parser.add_argument(
        "query", nargs="*",
        help="list/plan argument, or extra suite/prefix names",
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--suite")
    group.add_argument("--changed", action="store_true")
    group.add_argument("--branch", action="store_true")
    group.add_argument("--core", action="store_true")
    group.add_argument("--full", action="store_true")
    group.add_argument("--local", action="store_true")
    group.add_argument("--required-external", action="store_true")
    group.add_argument("--agent", action="store_true")
    parser.add_argument("--base")
    parser.add_argument(
        "--jobs", type=int, default=0,
        help="portable worker count (0 = CPU count; 1 = serial)",
    )
    parser.add_argument(
        "--allow-skips", action="store_true",
        help="allow explicitly requested external suites to skip missing prerequisites",
    )
    parser.add_argument("--manifest", type=Path)
    parser.add_argument("--repo-root", type=Path)
    parser.add_argument("--external-root", type=Path)
    parser.add_argument("--out-dir", type=Path)
    args = parser.parse_args()

    root = (args.repo_root or DEFAULT_ROOT).resolve()
    manifest_path = (args.manifest or root / "verification.toml").resolve()
    manifest = load_manifest(manifest_path)
    suites = manifest.get("suite", {})

    legacy_selected = any((
        args.suite, args.changed, args.branch, args.core, args.full, args.local,
        args.required_external, args.agent,
    ))
    if args.command and legacy_selected:
        parser.error("positional commands cannot be combined with legacy mode flags")

    command = args.command
    extra = list(args.query)
    if command == "list":
        if len(extra) > 1:
            parser.error("list takes at most one query")
        return print_suite_listing(manifest, extra[0] if extra else None)

    plan_only = command == "plan"
    plan_query = (extra[0] if extra else "changed") if plan_only else None
    if plan_only and len(extra) > 1:
        parser.error("plan takes at most one query")
    explicit_queries: list[str] = []
    explicit_suite_selected = False
    changed_request = False
    branch_mode = False
    names: list[str] = []
    mode = "changed"
    required = False
    compact = False

    if plan_only:
        if plan_query == "changed":
            changed_request = True
        elif plan_query == "branch":
            changed_request = True
            branch_mode = True
        elif plan_query in {"core", "full", "local"}:
            names = selected_suites(manifest, plan_query)
            print_plan(manifest, names, label=plan_query)
            return 0
        else:
            explicit_queries = [plan_query]
    elif command in {"core", "full", "local"}:
        if extra:
            parser.error(f"{command} does not take extra suite names")
        mode = command
        names = selected_suites(manifest, mode)
    elif command == "branch" or args.branch:
        changed_request = True
        branch_mode = True
    elif command:
        explicit_queries = [command, *extra]
    elif args.suite:
        if args.suite not in suites:
            print(f"Unknown suite: {args.suite}", file=sys.stderr)
            return 2
        names = [args.suite]
        explicit_suite_selected = True
        mode = "suite"
        required = bool(suites[args.suite].get("requires_external")) and not args.allow_skips
    elif args.changed or not legacy_selected:
        changed_request = True
    elif args.required_external:
        names, mode, required = (
            selected_suites(manifest, "required-external"), "required-external", True
        )
    elif args.agent:
        names, mode, compact = selected_suites(manifest, "core"), "core", True
    else:
        mode = "core" if args.core else "full" if args.full else "local"
        names = selected_suites(manifest, mode)

    if explicit_queries:
        names = []
        for query in explicit_queries:
            resolved = resolve_query(manifest, query)
            if not resolved:
                print(f"No suite or suite-prefix matches: {query}", file=sys.stderr)
                return 2
            names.extend(resolved)
        names = _dedupe_names(names)
        if plan_only:
            print_plan(manifest, names, label=f"query {explicit_queries[0]!r}")
            return 0
        explicit_external = any(suites[name].get("requires_external") for name in names)
        mode, required = "suite", explicit_external and not args.allow_skips

    if changed_request:
        changes, error = changed_paths(root, args.base, branch=branch_mode)
        if error:
            print(error, file=sys.stderr)
            return 1
        assert changes is not None
        if not changes.paths:
            print(
                f"No changes detected ({changes.base_description}) — "
                "0 suites / 0 tests selected."
            )
            return 0
        names, notes, warnings, unmatched = plan_changed_suites(root, manifest, changes)
        for warning in warnings:
            print(f"warning: {warning}", file=sys.stderr)
        if unmatched:
            print(
                "Changed path(s) have no verification owner: " + ", ".join(unmatched),
                file=sys.stderr,
            )
            return 2
        if not names:
            print(
                "No suites matched changed files: " + ", ".join(sorted(changes.paths)),
                file=sys.stderr,
            )
            return 2
        if plan_only:
            print_plan(
                manifest, names,
                label=f"{'branch' if branch_mode else 'changed'}; {changes.base_description}",
                notes=notes,
            )
            return 0
        for note in notes:
            print(f"Selection: {note}")
        mode = "branch" if branch_mode else "changed"
        required = (
            any(suites[name].get("requires_external") for name in names)
            and not args.allow_skips
        )

    if required:
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

    allow_optional_external = mode in {"local", "required-external"} or required
    if (explicit_queries or explicit_suite_selected) and args.allow_skips:
        allow_optional_external = True
    if mode in {"changed", "branch"} and any(
        suites[name].get("requires_external") for name in names
    ):
        allow_optional_external = True
    return execute_suites(
        root, manifest, names, mode=mode, require_external=required,
        external_root=args.external_root, out_dir=args.out_dir, compact=compact,
        allow_optional_external=allow_optional_external, jobs=args.jobs,
    )


if __name__ == "__main__":
    raise SystemExit(main())
