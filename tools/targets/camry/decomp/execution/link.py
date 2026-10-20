"""Build converted C closures and diagnose native linkage."""
from __future__ import annotations

from tools.targets.camry.decomp.execution.build import C_FLAGS, HOST_CPU, HOST_MEM
from pathlib import Path
from tools.targets.camry.decomp.tree import COMMON_HEADER, ROOT
import ctypes
import os
import re
import subprocess
import tempfile
from tools.targets.camry.decomp.bindings import write_gap_thunks
from tools.targets.camry.decomp.bindings import write_indirect_table
from tools.targets.camry.decomp.c_text import _c_calls
from tools.targets.camry.decomp.sources import _object_definitions, _src_definitions, _src_paths


def _diagnostic(log: str) -> str:
    for line in log.splitlines():
        text = line.strip()
        if (
            "error:" in text
            or "duplicate symbol" in text
            or "Undefined symbols" in text
            or "undefined reference" in text
        ):
            return text[:220]
    lines = [line.strip() for line in log.splitlines() if line.strip()]
    return (lines[0][:220] if lines else "unknown")


def _compile(
    directory: Path,
    names: list[str],
    bodies: dict[str, str],
    stubs: dict[str, str] | None = None,
    provided: set[str] | None = None,
    *,
    header: Path = COMMON_HEADER,
) -> tuple[ctypes.CDLL | None, str]:
    source = directory / "candidates.c"
    stub_path = directory / "stubs.c"
    # dlopen caches by path; a retry must not reload a previous slice.
    descriptor, library_path = tempfile.mkstemp(prefix="liboracle-", suffix=".dylib", dir=directory)
    os.close(descriptor)
    library = Path(library_path)
    defined = _src_definitions() | (provided or set())
    parts = ['#include "common.h"', "int camry_note_call(uint32_t caller, uint32_t address);", ""]
    emitted = set()
    for name in names:
        if name in defined or name in emitted or name not in bodies:
            continue
        emitted.add(name)
        parts.append(bodies[name])
    source.write_text("\n".join(parts) + "\n", encoding="utf-8")
    stub_text = ['#include <stdlib.h>', '#include "common.h"', ""]
    for name, signature in sorted((stubs or {}).items()):
        if name in defined or name in emitted:
            continue
        stub_text.append(signature.rstrip())
        stub_text.append("{")
        stub_text.append("  abort();")
        stub_text.append("}")
        stub_text.append("")
    for _name, decl in _object_definitions(header):
        stub_text.append(decl)
    stub_path.write_text("\n".join(stub_text) + "\n", encoding="utf-8")
    table = directory / "indirect_table.c"
    gaps = directory / "gap_thunks.c"
    linked = [source, *(_src_paths())]
    write_indirect_table(table, linked)
    write_gap_thunks(gaps)
    command = [
        "cc", "-O2", *C_FLAGS,
        "-I", str(header.parent),
        "-I", str(ROOT / "include"),
        "-I", str(HOST_CPU.parent),
        "-dynamiclib", "-o", str(library),
        str(source), str(stub_path), str(table), str(gaps), str(HOST_MEM), str(HOST_CPU),
        *[str(path) for path in _src_paths()],
    ]
    result = subprocess.run(command, text=True, capture_output=True, check=False)
    if result.returncode == 0:
        return ctypes.CDLL(library), ""
    return None, result.stderr or result.stdout


def _drop_unlinked(names: list[str], bodies: dict[str, str], log: str) -> list[str]:
    missing = re.findall(r'"_([^"]+)", referenced from:', log)
    if not missing:
        missing = re.findall(r"undefined reference to [`']([^']+)'", log)
    if not missing:
        return []
    dropped = []
    for name in names:
        text = bodies[name]
        if any(re.search(rf"\b{re.escape(symbol)}\b", text) for symbol in missing):
            dropped.append(name)
    return dropped


def _body_closure(roots: list[str], bodies: dict[str, str]) -> list[str]:
    """Functions the host must link, including calls the scenario did not take."""
    needed: list[str] = []
    seen: set[str] = set()
    pending = list(roots)
    while pending:
        name = pending.pop()
        if name in seen or name not in bodies:
            continue
        seen.add(name)
        needed.append(name)
        pending.extend(callee for callee in _c_calls(bodies[name]) if callee not in seen)
    return needed


def _prototypes(header: Path = COMMON_HEADER) -> dict[str, str]:
    """Declarator text from the selected common.h, without the trailing semicolon."""
    if not header.exists():
        return {}
    found: dict[str, str] = {}
    buf = ""
    for line in header.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not buf and (
            not stripped
            or stripped.startswith(("#", "//", "/*", "*"))
            or stripped.startswith(("typedef", "struct", "enum", "union"))
        ):
            continue
        buf = f"{buf} {stripped}".strip()
        if not buf.endswith(";"):
            if len(buf) > 800:
                buf = ""
            continue
        match = re.search(r"\b([A-Za-z_][A-Za-z0-9_]*)\s*\([^;]*\)\s*;$", buf)
        if match:
            found[match.group(1)] = buf[:-1].rstrip()
        buf = ""
    return found


def _undefined_symbols(log: str) -> list[str]:
    missing = re.findall(r'"_([^"]+)", referenced from:', log)
    if not missing:
        missing = re.findall(r"undefined reference to [`']_?([^']+)'", log)
    seen: list[str] = []
    for name in missing:
        if name not in seen:
            seen.append(name)
    return seen


def _macro_names(header: Path = COMMON_HEADER) -> set[str]:
    if not header.exists():
        return set()
    return set(re.findall(
        r"^#define\s+([A-Za-z_][A-Za-z0-9_]*)\s*\(",
        header.read_text(encoding="utf-8"),
        re.M,
    ))


def _linkable(
    roots: list[str],
    bodies: dict[str, str],
    defined: set[str],
    symbols: set[str],
    macros: set[str],
) -> tuple[set[str], list[str]]:
    memo: dict[str, bool] = {}

    def ok(name: str) -> bool:
        if name in memo:
            return memo[name]
        if name in defined or name in macros:
            memo[name] = True
            return True
        if name not in bodies:
            memo[name] = name not in symbols
            return memo[name]
        memo[name] = True
        good = all(callee == name or ok(callee) for callee in _c_calls(bodies[name]))
        memo[name] = good
        return good

    kept = {name for name in roots if ok(name)}
    support: list[str] = []
    seen = set(kept) | defined | macros
    pending = list(kept)
    while pending:
        name = pending.pop()
        body = bodies.get(name)
        if body is None:
            continue
        for callee in _c_calls(body) | (
            set(re.findall(r"\b([A-Za-z_][A-Za-z0-9_]*)\b", body)) & bodies.keys()
        ):
            if callee in seen or callee not in bodies:
                continue
            seen.add(callee)
            support.append(callee)
            pending.append(callee)
    return kept, support


def _error_names(
    log: str,
    names: list[str],
    bodies: dict[str, str],
    skip: set[str] | None = None,
) -> list[str]:
    lines = [int(number) for number in re.findall(r"candidates\.c:(\d+):\d+: (?:fatal )?error:", log)]
    if not lines:
        return []
    defined = _src_definitions() | (skip or set())
    cursor = 4
    spans = []
    emitted: set[str] = set()
    for name in names:
        if name in defined or name in emitted or name not in bodies:
            continue
        emitted.add(name)
        spans.append((cursor, name))
        cursor += bodies[name].count("\n") + 1
    found = []
    for line in lines:
        owner = None
        for start, name in spans:
            if start <= line:
                owner = name
            else:
                break
        if owner and owner not in found:
            found.append(owner)
    return found

