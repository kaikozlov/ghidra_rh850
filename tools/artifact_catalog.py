#!/usr/bin/env python3
"""Derived catalog for tracked generated artifacts, producers, and verification owners."""
from __future__ import annotations

import ast
import collections
import subprocess
import tomllib
from functools import lru_cache
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


@lru_cache(maxsize=1)
def _tracked_artifacts() -> tuple[str, ...]:
    return tuple(_git_files("data/generated"))


def tracked_artifacts() -> list[str]:
    return list(_tracked_artifacts())


@lru_cache(maxsize=1)
def manifest() -> dict:
    return tomllib.loads(MANIFEST.read_text(encoding="utf-8"))


@lru_cache(maxsize=1)
def _suite_owners() -> dict[str, list[str]]:
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


def suite_owners() -> dict[str, list[str]]:
    return {path: list(names) for path, names in _suite_owners().items()}


@lru_cache(maxsize=1)
def _source_files_cached() -> tuple[str, ...]:
    return tuple([
        p for p in _git_files("tools")
        if Path(p).suffix in {".py", ".sh"} or "/" not in Path(p).name
    ])


def _source_files() -> list[str]:
    return list(_source_files_cached())


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


def _path_expr(node: ast.AST) -> Path | None:
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return Path(node.value)
    if isinstance(node, ast.Name) and node.id in {"REPO", "ROOT", "REPO_ROOT"}:
        return Path()
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Div):
        left = _path_expr(node.left)
        right = _path_expr(node.right)
        if left is not None and right is not None:
            return left / right
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "Path" and len(node.args) == 1:
        return _path_expr(node.args[0])
    return None


@lru_cache(maxsize=None)
def _declared_outputs(tool: str) -> tuple[str, ...]:
    """Recover conventional OUT/OUTPUT constants from a Python producer."""
    path = REPO / tool
    if path.suffix != ".py":
        return []
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except (OSError, SyntaxError, UnicodeDecodeError):
        return []
    out: list[str] = []
    for node in tree.body:
        targets: list[ast.expr] = []
        value: ast.AST | None = None
        if isinstance(node, ast.Assign):
            targets = list(node.targets); value = node.value
        elif isinstance(node, ast.AnnAssign):
            targets = [node.target]; value = node.value
        if value is not None:
            names = [t.id for t in targets if isinstance(t, ast.Name)]
            if any("OUT" in name.upper() or "OUTPUT" in name.upper() for name in names):
                resolved = _path_expr(value)
                if resolved is not None:
                    rel = resolved.as_posix().lstrip("./")
                    if rel.startswith("data/"):
                        out.append(rel)
    # Generic tools often declare their artifact only as argparse --out/--output
    # defaults rather than module constants. Recover those defaults as local
    # producer metadata too.
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call) or not node.args:
            continue
        first = node.args[0]
        if not isinstance(first, ast.Constant) or first.value not in {"--out", "--output"}:
            continue
        default = next((kw.value for kw in node.keywords if kw.arg == "default"), None)
        if default is None:
            continue
        resolved = _path_expr(default)
        if resolved is not None:
            rel = resolved.as_posix().lstrip("./")
            if rel.startswith("data/"):
                out.append(rel)
    return tuple(dict.fromkeys(out))


def declared_outputs(tool: str) -> list[str]:
    return list(_declared_outputs(tool))


def _naming_producer(path: str) -> str | None:
    name = Path(path).name
    if name.startswith("corolla_8965H1202000_") and name.endswith(".json"):
        suffix = Path(name).stem.removeprefix("corolla_8965H1202000_")
        candidate = f"tools/build_corolla_h_{suffix}.py"
        if (REPO / candidate).is_file():
            return candidate
    if name.startswith("corolla_hf_") and name.endswith(".json"):
        suffix = Path(name).stem.removeprefix("corolla_hf_")
        candidate = f"tools/build_corolla_hf_{suffix}.py"
        if (REPO / candidate).is_file():
            return candidate
    return None


@lru_cache(maxsize=None)
def _producer_candidates(path: str) -> tuple[str, ...]:
    """Return likely producers, preferring declared output ownership.

    A source file merely mentioning an artifact is a consumer, not a producer. We
    therefore first recover conventional OUT/OUTPUT constants, then the established
    Corolla semantic-builder naming contract, and only then fall back to source
    mentions for older tools that have not adopted declarative output metadata yet.
    """
    declared = [tool for tool in _source_files() if path in declared_outputs(tool)]
    if declared:
        return tuple(declared)
    named = _naming_producer(path)
    if named:
        return (named,)
    ignore = {"tools/artifact_catalog.py", "tools/build_knowledge_index.py"}
    mentioned = [p for p in _mentions(path, _source_files()) if p not in ignore]
    ranked = [
        p for p in mentioned
        if Path(p).name.startswith(("build_", "generate_", "extract_", "analyze_", "inspect_", "compare_"))
    ]
    return tuple(ranked or mentioned)


def producer_candidates(path: str) -> list[str]:
    return list(_producer_candidates(path))


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


def family_primary_builders(family: str) -> list[tuple[str, str]]:
    """Derive semantic builder -> primary artifact pairs for regen gates.

    The family builder filename is the local contract; the primary artifact follows
    the corresponding tracked basename. Builders with a deliberately cross-family
    output fall back to their single declared generated output. H also includes the
    generic application-diagnostics comparator because it declares an H-family output.
    """
    if family == "corolla_h":
        tool_prefix = "build_corolla_h_"
        artifact_prefix = "corolla_8965H1202000_"
        extras = {"tools/compare_variant_application_diagnostics.py"}
    elif family == "corolla_hf":
        tool_prefix = "build_corolla_hf_"
        artifact_prefix = "corolla_hf_"
        extras: set[str] = set()
    else:
        raise ValueError(f"unknown builder family: {family}")

    pairs: list[tuple[str, str]] = []
    for tool_path in sorted((REPO / "tools").glob(f"{tool_prefix}*.py")):
        tool = tool_path.relative_to(REPO).as_posix()
        suffix = tool_path.stem.removeprefix(tool_prefix)
        primary = f"data/generated/{artifact_prefix}{suffix}.json"
        if (REPO / primary).is_file():
            pairs.append((tool, primary))
            continue
        declared = [p for p in declared_outputs(tool) if p.startswith("data/generated/")]
        if len(declared) != 1:
            raise ValueError(f"cannot derive one primary artifact for {tool}: {declared}")
        pairs.append((tool, declared[0]))
    for tool in sorted(extras):
        declared = [p for p in declared_outputs(tool) if Path(p).name.startswith(artifact_prefix)]
        if len(declared) != 1:
            raise ValueError(f"cannot derive one {family} artifact for {tool}: {declared}")
        pairs.append((tool, declared[0]))
    return pairs


def primary_output_for_tool(tool: str) -> str:
    """Resolve one tool's canonical tracked primary artifact."""
    stem = Path(tool).stem
    if stem.startswith("build_corolla_h_"):
        suffix = stem.removeprefix("build_corolla_h_")
        candidate = f"data/generated/corolla_8965H1202000_{suffix}.json"
        if (REPO / candidate).is_file():
            return candidate
    if stem.startswith("build_corolla_hf_"):
        suffix = stem.removeprefix("build_corolla_hf_")
        candidate = f"data/generated/corolla_hf_{suffix}.json"
        if (REPO / candidate).is_file():
            return candidate
    declared = [p for p in declared_outputs(tool) if p.startswith("data/generated/") and (REPO / p).is_file()]
    if len(declared) != 1:
        raise ValueError(f"cannot derive one tracked primary output for {tool}: {declared}")
    return declared[0]


def suite_builder_pairs(suite: str) -> list[tuple[str, str]]:
    """Derive dynamic builder invocations from a verification suite's path contract."""
    row = manifest().get("suite", {}).get(suite)
    if row is None:
        raise ValueError(f"unknown verification suite: {suite}")
    pairs: list[tuple[str, str]] = []
    for value in row.get("paths", []):
        if not isinstance(value, str) or not value.startswith("tools/") or not value.endswith(".py"):
            continue
        name = Path(value).name
        if not name.startswith(("build_", "generate_", "extract_", "analyze_", "inspect_", "compare_")):
            continue
        try:
            artifact = primary_output_for_tool(value)
        except ValueError:
            continue
        pairs.append((value, artifact))
    return pairs
