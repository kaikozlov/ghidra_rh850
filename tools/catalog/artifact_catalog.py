#!/usr/bin/env python3
"""Derived catalog for tracked generated artifacts and their producers."""
from __future__ import annotations

import ast
import subprocess
from functools import lru_cache
from pathlib import Path
from typing import Iterable

REPO = Path(__file__).resolve().parents[2]

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
        candidate = f"tools/targets/corolla/builders/build_corolla_h_{suffix}.py"
        if (REPO / candidate).is_file():
            return candidate
    if name.startswith("corolla_hf_") and name.endswith(".json"):
        suffix = Path(name).stem.removeprefix("corolla_hf_")
        candidate = f"tools/targets/corolla/builders/build_corolla_hf_{suffix}.py"
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
    ignore = {"tools/catalog/artifact_catalog.py"}
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
        if p not in {"tools/catalog/artifact_catalog.py"}
    ]


def rows(query: str | None = None) -> list[dict]:
    q = query.casefold() if query else None
    out = []
    for path in tracked_artifacts():
        if q and q not in path.casefold():
            continue
        out.append({
            "artifact": path,
            "producers": producer_candidates(path),
        })
    return out
