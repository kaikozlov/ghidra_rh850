#!/usr/bin/env python3
"""Derived catalog for tracked generated artifacts and their producers."""
from __future__ import annotations

import ast
import subprocess
from collections.abc import Iterable
from functools import cache, lru_cache
from pathlib import Path

from tools.project import analysis_target

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


@cache
def _corpus_invocations() -> dict[str, tuple[str, tuple[str, ...]]]:
    """Use the registered work project and the generator used by Makefile."""
    invocations = {}
    for target, row in analysis_target.load()["targets"].items():
        path = row["decompiler_corpus"]
        project_args = ("--project-dir", str(REPO / row["work_dir"]))
        if target == "sienna-8965B4512000":
            invocations[path] = ("tools/project/generate_decompiler_corpus.py", project_args)
        else:
            invocations[path] = (
                "tools/project/generate_target_decompiler_corpus.py",
                ("--target", target, *project_args, "--output", str(REPO / path)),
            )
    return invocations


@lru_cache(maxsize=1)
def _tracked_artifacts() -> tuple[str, ...]:
    tracked = set(_git_files("data/generated"))
    tracked_files = set(_git_files())
    tracked.update(_corpus_invocations().keys() & tracked_files)
    for tool in _source_files_cached():
        tracked.update(path for path in _declared_outputs(tool) if path in tracked_files)
    return tuple(sorted(tracked))


def tracked_artifacts() -> list[str]:
    return list(_tracked_artifacts())


@lru_cache(maxsize=1)
def _source_files_cached() -> tuple[str, ...]:
    return tuple(p for p in _git_files("tools") if p.endswith(".py"))


def _mentions(path: str, candidates: Iterable[str]) -> list[str]:
    found: list[str] = []
    needles = [path.encode()]
    module_data = "ghidra/ghidra_v850/data/"
    if path.startswith(module_data):
        needles.append(path.removeprefix(module_data).encode())
    for rel in candidates:
        p = REPO / rel
        try:
            content = p.read_bytes()
            if any(needle in content for needle in needles):
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


def _artifact_path(node: ast.AST) -> str | None:
    path = _path_expr(node)
    if path is not None and not path.is_absolute() and ".." not in path.parts:
        rel = path.as_posix()
        if rel.startswith(("data/", "ghidra/ghidra_v850/data/")):
            return rel
    return None


@cache
def _declared_outputs(tool: str) -> tuple[str, ...]:
    """Recover output files and tracked members of explicit artifact directories."""
    path = REPO / tool
    if path.suffix != ".py":
        return ()
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except (OSError, SyntaxError, UnicodeDecodeError):
        return ()
    out: list[str] = []
    for node in tree.body:
        targets: list[ast.expr] = []
        value: ast.AST | None = None
        if isinstance(node, ast.Assign):
            targets = list(node.targets); value = node.value
        elif isinstance(node, ast.AnnAssign):
            targets = [node.target]; value = node.value
        if value is None:
            continue
        names = [t.id for t in targets if isinstance(t, ast.Name)]
        if not any({"OUT", "OUTPUT"}.intersection(name.split("_")) for name in names):
            continue
        if (rel := _artifact_path(value)) is not None:
            if "ARTIFACT_OUTPUT_DIR" in names:
                out.extend(_git_files(f":(literal){rel}/"))
            else:
                out.append(rel)
    # A CLI output default may be the only declaration, even with a short alias.
    for node in ast.walk(tree):
        if not (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and node.func.attr == "add_argument"
            and any(
                isinstance(arg, ast.Constant) and arg.value in ("--out", "--output")
                for arg in node.args
            )
        ):
            continue
        default = next((kw.value for kw in node.keywords if kw.arg == "default"), None)
        if default is not None and (rel := _artifact_path(default)) is not None:
            out.append(rel)
    return tuple(dict.fromkeys(out))


def declared_outputs(tool: str) -> list[str]:
    return list(_declared_outputs(tool))


def producer_args(path: str, producer: str) -> tuple[str, ...]:
    invocation = _corpus_invocations().get(path)
    return invocation[1] if invocation and invocation[0] == producer else ()


@cache
def _producer_candidates(path: str) -> tuple[str, ...]:
    """Return only producers with a declaration for this exact output."""
    invocation = _corpus_invocations().get(path)
    return tuple(
        tool for tool in _source_files_cached()
        if (invocation is not None and invocation[0] == tool and (REPO / tool).is_file())
        or path in _declared_outputs(tool)
    )


def producer_candidates(path: str) -> list[str]:
    return list(_producer_candidates(path))


def consumers(path: str) -> list[str]:
    candidates = _git_files("tools", "tests", "ghidra/scripts",
                            "ghidra/ghidra_v850/src", "Makefile", "verification.toml")
    producers = set(_producer_candidates(path))
    return [
        p for p in _mentions(path, candidates)
        if p != "tools/catalog/artifact_catalog.py" and p not in producers
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
