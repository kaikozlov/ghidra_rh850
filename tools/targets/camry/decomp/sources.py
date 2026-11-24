"""Retained source-bank organization and implementation precedence."""
from __future__ import annotations

import json
import re
from collections import defaultdict
from collections.abc import Iterable, Iterator
from dataclasses import dataclass
from pathlib import Path

from tools import REPO_ROOT
from tools.project import pseudo
from tools.project.analysis_target import target as resolve_target
from tools.targets.camry.decomp.c_text import _function_heads
from tools.targets.camry.decomp.syntax import _c_signature
from tools.targets.camry.decomp.tree import CANDIDATES, COMMON_HEADER, ROOT, TARGET, load_matched, load_symbols


def load_c_bodies(
    paths: list[Path], *, locations: dict[str, Path] | None = None,
) -> tuple[dict[str, str], set[str]]:
    bodies: dict[str, str] = {}
    duplicates: set[str] = set()
    for path in paths:
        lines = path.read_text(encoding="utf-8").splitlines()
        index = 0
        while index < len(lines):
            line = lines[index]
            if (
                not line.strip()
                or line.startswith("#")
                or line.startswith(" ")
                or line.startswith("\t")
                or line.startswith("/*")
                or line.startswith("//")
            ):
                index += 1
                continue
            start = index
            while index < len(lines) and "{" not in lines[index]:
                if ";" in lines[index]:
                    start = index + 1
                index += 1
            if index >= len(lines):
                break
            depth = 0
            while index < len(lines):
                depth += lines[index].count("{") - lines[index].count("}")
                index += 1
                if depth <= 0:
                    break
            chunk = "\n".join(lines[start:index]).strip() + "\n"
            match = re.search(r"\b([A-Za-z_][A-Za-z0-9_]*)\s*\(", _c_signature(chunk))
            if match is None:
                continue
            name = match.group(1)
            if name in bodies:
                duplicates.add(name)
            bodies[name] = chunk
            if locations is not None:
                locations[name] = path
    return bodies, duplicates


def _load_bodies(
    *, candidates: bool = False, locations: dict[str, Path] | None = None,
) -> tuple[dict[str, str], set[str]]:
    """Load canonical bodies, optionally selecting unchecked conversion candidates.

    Candidate output is never an implicit source tier. Only the conversion
    oracle opts into it; checked retained bodies and curated owners stay fixed.
    """
    bodies, duplicates = load_c_bodies(retained_paths(), locations=locations)
    if candidates:
        candidate_locations = {} if locations is not None else None
        generated, generated_dups = load_c_bodies(
            sorted(CANDIDATES.glob("*.c")), locations=candidate_locations,
        )
        checked = {
            row["name"] for row in load_matched()
            if row.get("status") in {"equivalent", "byte-matched"}
        }
        for name, chunk in generated.items():
            if name in bodies and name in checked:
                continue
            bodies[name] = chunk
            duplicates.discard(name)
            if name in generated_dups:
                duplicates.add(name)
            if locations is not None:
                locations[name] = candidate_locations[name]
    for path in _src_paths():
        curated, _curated_dups = load_c_bodies([path])
        for name in _function_heads(path.read_text(encoding="utf-8")):
            if name in curated:
                bodies[name] = curated[name]
                duplicates.discard(name)
                if locations is not None:
                    locations[name] = path
    return bodies, duplicates


@dataclass(frozen=True)
class SourceMatch:
    symbol: dict
    path: Path
    body: str
    pc: int | None


def _load_source_ranges() -> dict[str, list[tuple[int, int]]]:
    _, target = resolve_target(TARGET)
    corpus = REPO_ROOT / target["decompiler_corpus"]
    with corpus.open(encoding="utf-8") as handle:
        metadata = json.loads(handle.readline())
    if not isinstance(metadata, dict) or metadata.get("record") != "metadata":
        raise ValueError(f"invalid corpus metadata record in {corpus}")
    if (
        metadata.get("analysis_target") != TARGET
        or metadata.get("executable_sha256") != target["codeflash_sha256"]
    ):
        raise ValueError(f"pseudocode corpus does not match registered target {TARGET}: {corpus}")
    return pseudo.load_function_body_ranges(REPO_ROOT / target["inventory_baseline"], metadata)


def locate_sources(queries: Iterable[str]) -> Iterator[SourceMatch | str]:
    """Yield an effective C body or a diagnostic for each query, in input order."""
    by_name: dict[str, list[dict]] = defaultdict(list)
    by_entry: dict[int, list[dict]] = defaultdict(list)
    for symbol in load_symbols():
        by_name[symbol["name"]].append(symbol)
        by_entry[int(symbol["addr"], 16)].append(symbol)

    ranges: dict[str, list[tuple[int, int]]] | str | None = None
    bodies: dict[str, str] | None = None
    locations: dict[str, Path] = {}
    for query in queries:
        pc = None
        selected = by_name.get(query)
        if selected is None:
            try:
                address = int(query, 16)
            except ValueError:
                yield f"unknown reconstructed function: {query}"
                continue
            selected = by_entry.get(address)
            if selected is None:
                pc = address
                if ranges is None:
                    try:
                        ranges = _load_source_ranges()
                    except (OSError, ValueError, SystemExit) as exc:
                        ranges = str(exc)
                if isinstance(ranges, str):
                    yield f"cannot resolve PC {pc:#010x}: {ranges}"
                    continue
                owners = [
                    entry for entry, spans in ranges.items()
                    if any(start <= pc <= end for start, end in spans)
                ]
                if not owners:
                    yield f"no function owns PC {pc:#010x}"
                    continue
                if len(owners) > 1:
                    yield f"ambiguous function owner for PC {pc:#010x}: {', '.join(owners)}"
                    continue
                entry = owners[0]
                selected = by_entry.get(int(entry, 16))
                if selected is None:
                    yield f"no reconstructed C body for function at {entry} (PC {pc:#010x})"
                    continue

        if len(selected) != 1:
            hint = "; use its entry address" if query in by_name else ""
            yield f"ambiguous reconstructed function: {query}{hint}"
            continue
        symbol = selected[0]
        if bodies is None:
            bodies, _duplicates = _load_bodies(locations=locations)
        name = symbol["name"]
        if name not in bodies:
            context = f" (PC {pc:#010x})" if pc is not None else ""
            yield f"no reconstructed C body for {name} at {symbol['addr']}{context}"
            continue
        yield SourceMatch(symbol, locations[name], bodies[name], pc)


def _object_definitions(header: Path = COMMON_HEADER) -> list[tuple[str, str]]:
    """Definitions for extern objects declared in the selected common.h."""
    found: list[tuple[str, str]] = []
    if header.exists():
        pattern = re.compile(
            r"extern\s+((?:volatile\s+)?(?:u?int(?:8|16|32|64)_t|unsigned|int)\s+\*?\s*)"
            r"([A-Za-z_][A-Za-z0-9_]*)\s*;\s*$"
        )
        for line in header.read_text(encoding="utf-8").splitlines():
            match = pattern.match(line.strip())
            if match:
                found.append((match.group(2), f"{match.group(1)}{match.group(2)};"))
    return found


def _src_paths() -> list[Path]:
    return sorted((ROOT / "src").glob("*.c"))


def _src_definitions() -> set[str]:
    cached = getattr(_src_definitions, "cached", None)
    if cached is not None:
        return cached
    names: set[str] = set()
    for path in _src_paths():
        names.update(_function_heads(path.read_text(encoding="utf-8")))
    _src_definitions.cached = names
    return names



def retained_paths() -> list[Path]:
    """Return address-window definitions followed by non-addressed support."""
    return sorted(
        path for path in (ROOT / "src" / "retained").glob("*.c")
        if re.fullmatch(r"[0-9a-f]{8}\.c", path.name) or path.name == "support.c"
    )


def write_retained(bodies: dict[str, str]) -> None:
    """Replace the bank with 4-KiB windows keyed by symbol entry address.

    Body text is kept verbatim. Definitions without a firmware symbol belong
    to support.c, never an invented address window. Supporting extern-object
    definitions have one owner: the first translation unit referencing them.
    """
    addresses = {row["name"]: int(row["addr"], 16) for row in load_symbols()}
    windows: dict[int, list[str]] = defaultdict(list)
    addressed = bodies.keys() & addresses.keys()
    for name in sorted(addressed, key=lambda name: (addresses[name], name)):
        windows[addresses[name] & ~0xfff].append(name)
    groups = [(f"{address:08x}.c", names) for address, names in sorted(windows.items())]
    helpers = sorted(bodies.keys() - addresses.keys())
    if helpers:
        groups.append(("support.c", helpers))
    remaining = dict(_object_definitions(COMMON_HEADER))
    directory = ROOT / "src" / "retained"
    directory.mkdir(parents=True, exist_ok=True)
    wanted = set()
    for filename, names in groups:
        path = directory / filename
        wanted.add(path)
        text = "\n".join(bodies[name] for name in names)
        declarations = []
        for name, declaration in list(remaining.items()):
            if re.search(rf"\b{re.escape(name)}\b", text):
                declarations.append(declaration)
                del remaining[name]
        parts = ['#include "common.h"', "", *declarations]
        if declarations:
            parts.append("")
        rendered = "\n".join(parts) + "\n" + text
        if not rendered.endswith("\n"):
            rendered += "\n"
        if not path.exists() or path.read_text(encoding="utf-8") != rendered:
            path.write_text(rendered, encoding="utf-8")
    for path in retained_paths():
        if path not in wanted:
            path.unlink()
