#!/usr/bin/env python3
"""Derived catalog for tracked generated artifacts, producers, and verification owners."""
from __future__ import annotations

import collections
import subprocess
import tomllib
from pathlib import Path
from typing import Iterable

from verification_deps import repository_paths, suite_dependency_map

REPO = Path(__file__).resolve().parents[1]
MANIFEST = REPO / "verification.toml"


def _git_files(*pathspecs: str) -> list[str]:
    proc = subprocess.run(
        ["git", "ls-files", "--", *pathspecs],
        cwd=REPO,
        text=True,
        capture_output=True,
        check=True,
    )
    return sorted(p for p in proc.stdout.splitlines() if p)


def tracked_artifacts() -> list[str]:
    return _git_files("data/generated")


def manifest() -> dict:
    return tomllib.loads(MANIFEST.read_text(encoding="utf-8"))


def suite_owners() -> dict[str, list[str]]:
    obj = manifest()
    deps = suite_dependency_map(REPO, obj, repository_paths(REPO))
    out: dict[str, list[str]] = collections.defaultdict(list)
    for suite, paths in deps.items():
        for path in paths:
            if path.startswith("data/generated/"):
                out[path].append(suite)
    # Keep explicit manifest paths as semantic/dynamic invalidators too.
    for suite, row in obj.get("suite", {}).items():
        for path in row.get("paths", []):
            if isinstance(path, str) and path.startswith("data/generated/") and "*" not in path:
                out[path].append(suite)
    return {path: list(dict.fromkeys(names)) for path, names in out.items()}


def _source_files() -> list[str]:
    return [
        p for p in _git_files("tools")
        if Path(p).suffix in {".py", ".sh"} or "/" not in Path(p).name
    ]


def _mentions(path: str, candidates: Iterable[str]) -> list[str]:
    found: list[str] = []
    needle = path.encode()
    for rel in candidates:
        p = REPO / rel
        try:
            if needle in p.read_bytes():
                found.append(rel)
        except (OSError, IsADirectoryError):
            continue
    return found


def producer_candidates(path: str) -> list[str]:
    """Return tracked tool files that name the exact artifact path.

    This is intentionally derived instead of manually registered. Helpers that only
    consume an artifact can appear here too, so callers should treat the result as
    candidates; exact producer selection is exposed to the user before execution.
    """
    ignore = {
        "tools/artifact_catalog.py",
        "tools/build_knowledge_index.py",
    }
    return [p for p in _mentions(path, _source_files()) if p not in ignore]


def consumers(path: str) -> list[str]:
    candidates = _git_files("tools", "tests")
    return [
        p for p in _mentions(path, candidates)
        if p not in {"tools/artifact_catalog.py", "tools/build_knowledge_index.py"}
    ]


def rows(query: str | None = None) -> list[dict]:
    owners = suite_owners()
    q = query.casefold() if query else None
    out = []
    for path in tracked_artifacts():
        if q and q not in path.casefold():
            continue
        out.append({
            "artifact": path,
            "producers": producer_candidates(path),
            "suites": owners.get(path, []),
        })
    return out
