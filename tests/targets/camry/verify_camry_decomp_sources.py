#!/usr/bin/env python3
"""Protect retained-bank boundaries and rollback after promotion changes windows."""
from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path
from unittest.mock import patch

from tools.targets.camry.decomp import promotion, sources, tree
from tools.targets.camry.decomp.c_text import (
    _c_contains, _direct_calls, _function_heads, _match_delimiter, _split_args,
)
from tools.targets.camry.decomp.execution import link


def check_source_lookup() -> None:
    symbol = {"name": "subject", "addr": "0x1000"}
    missing = {"name": "missing", "addr": "0x2000"}
    with tempfile.TemporaryDirectory(prefix="camry-source-") as directory:
        root = Path(directory)
        candidates = root / "build/candidates"
        candidate = candidates / "000.c"
        retained = root / "src/retained/00001000.c"
        curated = root / "src/recovered.c"
        candidate.parent.mkdir(parents=True)
        retained.parent.mkdir(parents=True)
        candidate.write_text("int subject(void)\n{\n  return 1;\n}\n", encoding="utf-8")
        retained.write_text("int subject(void)\n{\n  return 2;\n}\n", encoding="utf-8")
        matched = [{"name": "subject", "status": "converted"}]
        with (
            patch.object(sources, "ROOT", root),
            patch.object(sources, "CANDIDATES", candidates),
            patch.object(sources, "load_symbols", return_value=[symbol, missing]),
            patch.object(sources, "load_matched", return_value=matched),
        ):
            # Source lookup never opts into a stale candidate cache, regardless
            # of the status assigned to the canonical retained implementation.
            for status in ("converted", "equivalent", "byte-matched"):
                matched[0]["status"] = status
                assert sources.locate_source("0x1000") == (
                    symbol, retained, retained.read_text(encoding="utf-8"),
                )
                bodies, duplicates = sources._load_bodies(candidates=True)
                expected = candidate if status == "converted" else retained
                assert bodies["subject"] == expected.read_text(encoding="utf-8")
                assert not duplicates
            curated.write_text("int subject(void)\n{\n  return 3;\n}\n", encoding="utf-8")
            assert sources.locate_source("1000") == (
                symbol, curated, curated.read_text(encoding="utf-8"),
            )
            locations = {}
            bodies, duplicates = sources._load_bodies(candidates=True, locations=locations)
            assert bodies["subject"] == curated.read_text(encoding="utf-8")
            assert locations["subject"] == curated and not duplicates
            # Retained-only implementations remain discoverable without candidates.
            curated.unlink()
            candidate.unlink()
            matched[0]["status"] = "converted"
            assert sources.locate_source("subject") == (
                symbol, retained, retained.read_text(encoding="utf-8"),
            )
            for query, message in (
                ("unknown", "unknown reconstructed function"),
                ("0x3000", "unknown reconstructed function"),
                ("missing", "no reconstructed C body"),
            ):
                try:
                    sources.locate_source(query)
                except ValueError as exc:
                    assert message in str(exc)
                else:
                    raise AssertionError(f"{query}: expected lookup failure")
    print("PASS source lookup: cache-independent canonical bodies and explicit unchecked candidates")


def check_c_token_matching() -> None:
    assert _c_contains("emit_value\n (1,\n 2);", "emit_value(1,2);")
    assert _c_contains("emit_value(/* source */ 1, 2);", "emit_value(1,2);")
    assert not _c_contains("other_emit_value(1,2);", "emit_value(1,2);")
    assert not _c_contains('emit_value("a b");', 'emit_value("ab");')
    assert not _c_contains("value + +increment;", "value++increment;")
    assert not _c_contains("// emit_value(1,2);\nother();", "emit_value(1,2);")
    assert _split_args('f(1,2), "a,b", (int[]){1,2}') == [
        "f(1,2)", ' "a,b"', " (int[]){1,2}",
    ]
    code = '(f(")"), g())'
    assert _match_delimiter(code, 0) == len(code) - 1
    assert _match_delimiter(code, len(code) - 1, step=-1) == 0
    assert _match_delimiter("(", 0, required=False) is None
    try:
        _match_delimiter("(", 0)
    except ValueError:
        pass
    else:
        raise AssertionError("incomplete delimiter must fail")
    assert _match_delimiter('(")")', 0) == 4
    assert _match_delimiter('(")")', 0, quoted=False) == 2
    assert [name for name, _open, _close in _direct_calls("f(g(), h())", set())] == ["g", "h", "f"]
    assert [name for name, _open, _close in _direct_calls("f(g(), h())", {"h"})] == ["g", "f"]
    heads = _function_heads(
        "static unsigned internal(void);\n"
        "unsigned internal(void) { return 0; }\n"
        "unsigned visible(void) { return 2; }\n"
        "void\n"
        "*wrapped(\n"
        "  unsigned value)\n"
        "{ return 0; }\n"
        "unsigned declaration(void);\n"
    )
    assert set(heads) == {"visible", "wrapped"}
    print("PASS C-token matching: wrapped calls, identifiers, literals, operators, comments")


def check_promotion_declarations() -> None:
    original, _duplicates = sources._load_bodies()
    probe = "int cleanup_probe(void)\n{\n  return 37;\n}\n"
    with tempfile.TemporaryDirectory(prefix="camry-promotion-") as directory:
        root = Path(directory) / "canonical"
        shutil.copytree(tree.ROOT, root)
        header = root / "include" / "common.h"
        with (
            patch.object(tree, "ROOT", root),
            patch.object(sources, "ROOT", root),
            patch.object(sources, "COMMON_HEADER", header),
            patch.object(promotion, "ROOT", root),
            patch.object(promotion, "COMMON_HEADER", header),
        ):
            paths = [header, *sources.retained_paths()]
            snapshots = {path: path.read_text(encoding="utf-8") for path in paths}
            with (root / "src" / "retained" / "support.c").open("a", encoding="utf-8") as handle:
                handle.write("\n" + probe)
            with header.open("a", encoding="utf-8") as handle:
                handle.write("\nint cleanup_probe(int argument);\n")
            promotion._promote([], [], {})
            assert link._prototypes(header)["cleanup_probe"] == "int cleanup_probe(void)"
            actual, duplicates = sources._load_bodies()
            assert actual == {**original, "cleanup_probe": probe} and not duplicates
            result = subprocess.run(
                [
                    "cc", "-std=c11", "-Werror", "-DCAMRY_HOST",
                    "-I", str(header.parent), "-fsyntax-only", "-x", "c", "-",
                ],
                input='#include "common.h"\nint caller(void) { return cleanup_probe(); }\n',
                text=True, capture_output=True,
            )
            assert result.returncode == 0, result.stderr
            promotion._restore(snapshots)
            assert {path: path.read_text(encoding="utf-8") for path in paths} == snapshots
            restored, duplicates = sources._load_bodies()
            assert restored == original and not duplicates
    print("PASS promotion declarations: retained ABI compiles and header/source rollback is exact")


def main() -> int:
    check_source_lookup()
    check_c_token_matching()
    check_promotion_declarations()
    symbols = [
        {"name": "lower", "addr": "0xfff"},
        {"name": "upper", "addr": "0x1000"},
        {"name": "later", "addr": "0x2000"},
    ]
    bodies = {
        "lower": "int lower(void)\n{\n  return 1;\n}\n",
        "upper": "int upper(void)\n{\n  return 2;\n}\n",
        "helper": "int helper(void)\n{\n  __builtin_trap();\n}\n",
    }
    with tempfile.TemporaryDirectory(prefix="camry-retained-") as directory:
        root = Path(directory)
        header = root / "include" / "common.h"
        header.parent.mkdir()
        header.write_text("int lower(void);\nint upper(void);\n", encoding="utf-8")
        with (
            patch.object(sources, "ROOT", root),
            patch.object(sources, "load_symbols", return_value=symbols),
            patch.object(sources, "_object_definitions", return_value=[]),
        ):
            sources.write_retained(bodies)
            paths = sources.retained_paths()
            assert [path.name for path in paths] == [
                "00000000.c", "00001000.c", "support.c",
            ]
            recovered, duplicates = sources.load_c_bodies(paths)
            assert recovered == bodies and not duplicates
            snapshots = {path: path.read_text(encoding="utf-8") for path in [*paths, header]}

            # A failed promotion can remove windows and helper stubs, change
            # bodies and declarations, and introduce a previously absent window.
            sources.write_retained({
                "lower": "int lower(void)\n{\n  return 99;\n}\n",
                "later": "int later(void)\n{\n  return 3;\n}\n",
            })
            header.write_text("int lower(int argument);\nint later(void);\n", encoding="utf-8")
            assert not (root / "src/retained/00001000.c").exists()
            assert not (root / "src/retained/support.c").exists()
            assert (root / "src/retained/00002000.c").exists()
            promotion._restore(snapshots)
            restored = {
                path: path.read_text(encoding="utf-8")
                for path in [*sources.retained_paths(), header]
            }
            assert restored == snapshots
    print("PASS retained boundaries, helper definitions, and whole-bank/header rollback")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
