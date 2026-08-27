#!/usr/bin/env python3
"""Derive mechanical verifier dependencies from Python source.

``verification.toml`` should describe *non-obvious* invalidation edges.  Python
verifiers already encode ordinary file dependencies in executable code; this module
extracts the small, auditable subset of those expressions that can be resolved
statically:

* repository-relative ``pathlib.Path`` expressions passed to calls or file methods;
* literal ``glob``/``rglob``/``iterdir`` roots;
* repository-local Python imports; and
* repository Python scripts executed through ``subprocess`` (recursively).

Only tracked or pending repository paths are returned.  Ignored external corpora,
build outputs, arbitrary string mentions, and unresolved dynamic paths are never
invented as dependencies.
"""
from __future__ import annotations

import ast
import os
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

# These have specialized change-routing policies and must not be flattened into
# ordinary mechanical ownership.
SPECIAL_ROUTING_PATHS = {
    "docs/status/FINDINGS.md",
    "docs/status/OPEN_QUESTIONS.md",
    "docs/status/CORRECTIONS.md",
    "docs/status/PRIORITIES.md",
}

# Firmware changes intentionally invalidate the complete portable tier.  Recording
# hundreds of exact per-test firmware reads adds no information to the route graph.
CENTRALIZED_PREFIXES = ("firmware/",)

_FILE_METHODS = {
    "read_text",
    "read_bytes",
    "open",
    "exists",
    "is_file",
    "is_dir",
    "stat",
    "write_text",
    "write_bytes",
    "touch",
    "unlink",
}
_GLOB_METHODS = {"glob", "rglob", "iterdir"}
_SUBPROCESS_METHODS = {
    "run",
    "check_call",
    "check_output",
    "call",
    "Popen",
}


def repository_paths(root: Path) -> set[str]:
    """Return tracked plus pending additions, excluding ignored external state."""
    tracked = set(subprocess.check_output(
        ["git", "ls-files"], cwd=root, text=True
    ).splitlines())
    deleted = set(subprocess.check_output(
        ["git", "ls-files", "--deleted"], cwd=root, text=True
    ).splitlines())
    pending = set(subprocess.check_output(
        ["git", "ls-files", "--others", "--exclude-standard"],
        cwd=root,
        text=True,
    ).splitlines())
    return {path for path in ((tracked - deleted) | pending) if path}


def path_matches_pattern(path: str, pattern: str) -> bool:
    return path.startswith(pattern) if pattern.endswith("/") else path == pattern


def _static_glob_prefix(pattern: str) -> str:
    """Return the literal directory prefix before the first glob metacharacter."""
    parts: list[str] = []
    for part in Path(pattern).parts:
        if any(char in part for char in "*?["):
            break
        parts.append(part)
    return Path(*parts).as_posix() if parts else ""


@dataclass(frozen=True)
class SourceDependencies:
    paths: frozenset[str]
    python_sources: frozenset[str]


class _SourceScanner(ast.NodeVisitor):
    def __init__(
        self,
        root: Path,
        source: Path,
        repo_paths: set[str],
        *,
        include_globs: bool,
    ) -> None:
        self.root = root.resolve()
        self.source = source.resolve()
        self.repo_paths = repo_paths
        self.include_globs = include_globs
        self.env_stack: list[dict[str, Path]] = [{}]
        self.alias_stack: list[dict[str, set[Path]]] = [{}]
        self.container_stack: list[dict[str, dict[int, set[Path]]]] = [{}]
        self.paths: set[str] = set()
        self.python_sources: set[str] = set()
        self.imports: list[str] = []
        self.search_dirs: list[Path] = [self.source.parent, self.root]

    @property
    def env(self) -> dict[str, Path]:
        return self.env_stack[-1]

    @property
    def aliases(self) -> dict[str, set[Path]]:
        return self.alias_stack[-1]

    @property
    def containers(self) -> dict[str, dict[int, set[Path]]]:
        return self.container_stack[-1]

    @staticmethod
    def _normalize(value: Path) -> Path:
        # All statically evaluable paths are already absolute (repo root, __file__,
        # or an absolute Path literal). Lexical normalization avoids thousands of
        # filesystem lstat calls from Path.resolve() during every edit-loop plan.
        return Path(os.path.normpath(str(value)))

    def _relative(self, value: Path) -> str | None:
        if not value.is_absolute():
            return None
        try:
            rel = self._normalize(value).relative_to(self.root).as_posix()
        except ValueError:
            return None
        return rel

    def _known_file(self, value: Path) -> str | None:
        rel = self._relative(value)
        if rel is None or rel not in self.repo_paths:
            return None
        if rel in SPECIAL_ROUTING_PATHS or rel.startswith(CENTRALIZED_PREFIXES):
            return None
        return rel

    def _known_directory(self, value: Path, pattern: str | None = None) -> str | None:
        base = self._relative(value)
        if base is None:
            return None
        prefix = _static_glob_prefix(pattern) if pattern else ""
        rel = (Path(base) / prefix).as_posix() if base and prefix else (prefix or base)
        rel = rel.strip("/")
        if not rel:
            return None
        directory = rel + "/"
        if directory.startswith(CENTRALIZED_PREFIXES):
            return None
        if any(path.startswith(directory) for path in self.repo_paths):
            return directory
        return None

    def _eval_path(self, node: ast.AST | None) -> Path | None:
        if node is None:
            return None
        if isinstance(node, ast.Name):
            if node.id == "__file__":
                return self.source
            return self.env.get(node.id)
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            # A bare string is not repository-relative by itself.
            return None
        if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Div):
            left = self._eval_path(node.left)
            if left is None:
                return None
            if isinstance(node.right, ast.Constant) and isinstance(node.right.value, str):
                return left / node.right.value
            return None
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name) and node.func.id == "Path" and node.args:
                arg = node.args[0]
                if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                    candidate = Path(arg.value)
                    return candidate if candidate.is_absolute() else None
                return self._eval_path(arg)
            if isinstance(node.func, ast.Name) and node.func.id == "str" and node.args:
                return self._eval_path(node.args[0])
            if isinstance(node.func, ast.Attribute):
                if node.func.attr in {"resolve", "absolute"}:
                    return self._eval_path(node.func.value)
                # Path.cwd() is the repository root for verifier execution.
                if (
                    node.func.attr == "cwd"
                    and isinstance(node.func.value, ast.Name)
                    and node.func.value.id == "Path"
                ):
                    return self.root
                # Environment-backed external roots often provide a repository
                # fallback as the final argument.  Resolve only that fallback.
                if (
                    node.func.attr == "get"
                    and isinstance(node.func.value, ast.Attribute)
                    and node.func.value.attr == "environ"
                    and len(node.args) >= 2
                ):
                    return self._eval_path(node.args[-1])
        if isinstance(node, ast.Attribute) and node.attr == "parent":
            value = self._eval_path(node.value)
            return value.parent if value is not None else None
        if isinstance(node, ast.Subscript) and isinstance(node.value, ast.Attribute):
            if node.value.attr == "parents":
                value = self._eval_path(node.value.value)
                if value is None:
                    return None
                index: int | None = None
                if isinstance(node.slice, ast.Constant) and isinstance(node.slice.value, int):
                    index = node.slice.value
                if index is not None and index >= 0:
                    try:
                        return value.parents[index]
                    except IndexError:
                        return None
        return None

    def _bind(self, target: ast.AST, value: Path | None) -> None:
        if value is not None and isinstance(target, ast.Name):
            self.env[target.id] = value

    def _known_files_for_expr(self, node: ast.AST) -> set[str]:
        found: set[str] = set()
        if isinstance(node, ast.Name):
            for value in self.aliases.get(node.id, set()):
                rel = self._known_file(value)
                if rel:
                    found.add(rel)
        value = self._eval_path(node)
        if value is not None:
            rel = self._known_file(value)
            if rel:
                found.add(rel)
        return found

    def _add_file_expr(self, node: ast.AST) -> str | None:
        found = self._known_files_for_expr(node)
        self.paths.update(found)
        return next(iter(found), None)

    def _walk_call_paths(self, node: ast.AST) -> set[str]:
        found: set[str] = set()
        for child in ast.walk(node):
            found.update(self._known_files_for_expr(child))
        self.paths.update(found)
        return found

    def _container_columns(self, node: ast.AST) -> dict[int, set[Path]]:
        """Resolve Path-valued columns in a literal list/tuple table."""
        if not isinstance(node, (ast.List, ast.Tuple)) or not node.elts:
            return {}
        rows = node.elts
        if all(isinstance(row, (ast.List, ast.Tuple)) for row in rows):
            columns: dict[int, set[Path]] = {}
            for row in rows:
                assert isinstance(row, (ast.List, ast.Tuple))
                for index, cell in enumerate(row.elts):
                    value = self._eval_path(cell)
                    if value is not None and self._known_file(value):
                        columns.setdefault(index, set()).add(value)
            return columns
        values = {
            value
            for cell in rows
            if (value := self._eval_path(cell)) is not None and self._known_file(value)
        }
        return {-1: values} if values else {}

    def visit_Assign(self, node: ast.Assign) -> None:
        value = self._eval_path(node.value)
        columns = self._container_columns(node.value)
        for target in node.targets:
            self._bind(target, value)
            if columns and isinstance(target, ast.Name):
                self.containers[target.id] = columns
        self.generic_visit(node)

    def visit_AnnAssign(self, node: ast.AnnAssign) -> None:
        self._bind(node.target, self._eval_path(node.value))
        self.generic_visit(node)

    def _visit_scoped_body(self, body: list[ast.stmt]) -> None:
        self.env_stack.append(dict(self.env))
        self.alias_stack.append({name: set(values) for name, values in self.aliases.items()})
        self.container_stack.append({
            name: {index: set(values) for index, values in columns.items()}
            for name, columns in self.containers.items()
        })
        try:
            for item in body:
                self.visit(item)
        finally:
            self.container_stack.pop()
            self.alias_stack.pop()
            self.env_stack.pop()

    def visit_For(self, node: ast.For) -> None:
        columns = self.containers.get(node.iter.id, {}) if isinstance(node.iter, ast.Name) else {}
        self.visit(node.iter)
        self.env_stack.append(dict(self.env))
        self.alias_stack.append({name: set(values) for name, values in self.aliases.items()})
        self.container_stack.append({
            name: {index: set(values) for index, values in table.items()}
            for name, table in self.containers.items()
        })
        try:
            if isinstance(node.target, (ast.Tuple, ast.List)):
                for index, target in enumerate(node.target.elts):
                    if isinstance(target, ast.Name) and columns.get(index):
                        self.aliases[target.id] = set(columns[index])
            elif isinstance(node.target, ast.Name) and columns.get(-1):
                self.aliases[node.target.id] = set(columns[-1])
            for item in node.body:
                self.visit(item)
            for item in node.orelse:
                self.visit(item)
        finally:
            self.container_stack.pop()
            self.alias_stack.pop()
            self.env_stack.pop()

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self._visit_scoped_body(node.body)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self._visit_scoped_body(node.body)

    def visit_Call(self, node: ast.Call) -> None:
        if isinstance(node.func, ast.Attribute):
            method = node.func.attr
            if method in _FILE_METHODS:
                self._add_file_expr(node.func.value)
            elif method in _GLOB_METHODS and self.include_globs:
                base = self._eval_path(node.func.value)
                pattern = None
                if node.args and isinstance(node.args[0], ast.Constant):
                    if isinstance(node.args[0].value, str):
                        pattern = node.args[0].value
                if base is not None:
                    rel = self._known_directory(base, pattern)
                    if rel:
                        self.paths.add(rel)

            # Resolve local module search roots without turning the entire
            # directory into an invalidation edge.
            if (
                isinstance(node.func.value, ast.Attribute)
                and isinstance(node.func.value.value, ast.Name)
                and node.func.value.value.id == "sys"
                and node.func.value.attr == "path"
                and method in {"insert", "append"}
            ):
                index = 1 if method == "insert" and len(node.args) > 1 else 0
                if len(node.args) > index:
                    value = self._eval_path(node.args[index])
                    if value is not None:
                        self.search_dirs.append(value)

            if (
                isinstance(node.func.value, ast.Name)
                and node.func.value.id == "subprocess"
                and method in _SUBPROCESS_METHODS
            ):
                executed: set[str] = set()
                for arg in node.args:
                    executed.update(self._walk_call_paths(arg))
                for rel in executed:
                    if rel.endswith(".py"):
                        self.python_sources.add(rel)
        elif isinstance(node.func, ast.Name) and node.func.id == "open" and node.args:
            self._add_file_expr(node.args[0])

        # A repository file nested anywhere in a helper argument is a mechanical
        # input even when the helper/generator expression performs the actual read.
        for arg in node.args:
            self._walk_call_paths(arg)
        for keyword in node.keywords:
            self._walk_call_paths(keyword.value)
        self.generic_visit(node)

    def visit_Import(self, node: ast.Import) -> None:
        self.imports.extend(alias.name for alias in node.names)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        if node.module:
            self.imports.append(node.module)

    def _resolve_imports(self) -> None:
        seen_dirs: set[Path] = set()
        search_dirs = []
        for directory in self.search_dirs:
            resolved = self._normalize(directory)
            if resolved not in seen_dirs:
                seen_dirs.add(resolved)
                search_dirs.append(resolved)
        for module in self.imports:
            rel_module = Path(*module.split("."))
            for directory in search_dirs:
                candidates = (
                    directory / rel_module.with_suffix(".py"),
                    directory / rel_module / "__init__.py",
                )
                matched = False
                for candidate in candidates:
                    rel = self._known_file(candidate)
                    if not rel:
                        continue
                    self.paths.add(rel)
                    if rel.endswith(".py"):
                        self.python_sources.add(rel)
                    matched = True
                if matched:
                    break

    def result(self) -> SourceDependencies:
        self._resolve_imports()
        return SourceDependencies(frozenset(self.paths), frozenset(self.python_sources))


def scan_python_source(
    root: Path,
    source: str,
    repo_paths: set[str],
    *,
    include_globs: bool = True,
    function_name: str | None = None,
) -> SourceDependencies:
    path = root / source
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=source)
    except (OSError, UnicodeError, SyntaxError):
        return SourceDependencies(frozenset(), frozenset())
    scanner = _SourceScanner(root, path, repo_paths, include_globs=include_globs)
    if function_name is None:
        scanner.visit(tree)
    else:
        matches = [
            node
            for node in tree.body
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == function_name
        ]
        # Section-specific dependency routing is an optimization, never a
        # correctness boundary. If the requested entry point is missing or
        # ambiguous, scan the whole verifier rather than silently under-route.
        scanner.visit(matches[0] if len(matches) == 1 else tree)
    return scanner.result()


def transitive_python_dependencies(
    root: Path,
    sources: Iterable[str],
    repo_paths: set[str] | None = None,
    *,
    root_functions: dict[str, str] | None = None,
    cache: dict[tuple[str, bool, str | None], SourceDependencies] | None = None,
) -> set[str]:
    """Return mechanical repository dependencies for Python verifier sources."""
    known = repo_paths if repo_paths is not None else repository_paths(root)
    roots = set(dict.fromkeys(sources))
    pending = list(roots)
    visited: set[str] = set()
    dependencies: set[str] = set()
    source_cache = cache if cache is not None else {}
    while pending:
        source = pending.pop()
        if source in visited or source not in known or not source.endswith(".py"):
            continue
        visited.add(source)
        # Broad globs in a verifier are direct mechanical dependencies.  In a
        # transitive helper they are deliberately not auto-promoted: many generators
        # glob only to inventory file names, and treating those as content ownership
        # recreates the broad false-fanout problem.  A helper whose globbed contents
        # are semantically relevant must declare that directory in suite.paths.
        include_globs = source in roots
        function_name = (root_functions or {}).get(source) if source in roots else None
        cache_key = (source, include_globs, function_name)
        result = source_cache.get(cache_key)
        if result is None:
            result = scan_python_source(
                root, source, known, include_globs=include_globs, function_name=function_name
            )
            source_cache[cache_key] = result
        dependencies.update(result.paths)
        pending.extend(sorted(result.python_sources - visited))
    # The starting verifier files are already owned through suite.tests. Imported
    # and subprocess-executed Python helpers must remain dependencies themselves:
    # changing helper code must rerun every caller in addition to its own inputs.
    dependencies.difference_update(roots)
    return dependencies


def _section_function(entry: dict) -> str | None:
    """Resolve the conventional ``--section NAME`` verifier entry point."""
    args = [str(value) for value in entry.get("args", [])]
    section: str | None = None
    for index, value in enumerate(args):
        if value == "--section" and index + 1 < len(args):
            section = args[index + 1]
            break
        if value.startswith("--section="):
            section = value.split("=", 1)[1]
            break
    if not section:
        return None
    normalized = section.replace("-", "_")
    return f"section_{normalized}"


def suite_dependency_map(
    root: Path,
    manifest: dict,
    repo_paths: set[str] | None = None,
) -> dict[str, set[str]]:
    """Derive mechanical dependencies for every manifest suite."""
    known = repo_paths if repo_paths is not None else repository_paths(root)
    result: dict[str, set[str]] = {}
    cache: dict[tuple[str, bool, str | None], SourceDependencies] = {}
    for name, entry in manifest.get("suite", {}).items():
        tests = [str(path) for path in entry.get("tests", [])]
        function_name = _section_function(entry)
        root_functions = {test: function_name for test in tests} if function_name else None
        deps = transitive_python_dependencies(
            root, tests, known, root_functions=root_functions, cache=cache
        )
        deps.difference_update(tests)
        result[name] = deps
    return result
