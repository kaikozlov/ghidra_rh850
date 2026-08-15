#!/usr/bin/env python3
"""Self-contained internal-link check for Markdown documentation.

Walks the project-facing Markdown entry points plus docs/** and verifies
that every relative Markdown link target exists on disk. Catches the class of
regression where a moved/renamed document leaves dangling cross-references
(e.g. an untracked docs/reference/ directory).

Scope and limits (intentional):
- Only relative links ending in .md (optionally with a #anchor) are checked.
  http/https links, absolute paths, and non-Markdown assets are skipped.
- Anchor *targets* are not validated (that would require heading parsing);
  only the file the link points to must exist.
- Code spans/blocks are not parsed; a link-looking token inside inline code is
  still checked, which is conservative (fails safe, not silent).

Self-contained: reads only tracked Markdown files. No external dependencies.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]

# Human-facing repository entry points plus everything under docs/. Vendored
# component READMEs are intentionally excluded from this project-doc gate.
SCAN = [
    REPO / "README.md",
    REPO / "AGENTS.md",
    REPO / "exploit" / "README.md",
    REPO / "community" / "README.md",
    REPO / "data" / "README.md",
    REPO / "ghidra" / "README.md",
] + sorted((REPO / "docs").rglob("*.md"))

# A relative Markdown link target: [text](path/to/file.md) or
# [text](path/to/file.md#anchor). Excludes http(s):// and absolute paths.
LINK = re.compile(r"\[[^\]]*\]\(([^)]+)\)")

passed = 0
failed = 0


def check(name: str, cond: bool, detail: str = "") -> None:
    global passed, failed
    if cond:
        passed += 1
    else:
        failed += 1
        suffix = f" ({detail})" if detail else ""
        print(f"[FAIL] {name}{suffix}")


def is_checkable(target: str) -> bool:
    t = target.strip()
    if not t or t.startswith("#"):
        return False
    if "://" in t or t.startswith(("mailto:", "/", "~")):
        return False
    # strip anchor
    path_part = t.split("#", 1)[0]
    return path_part.endswith(".md")


def main() -> int:
    print("== documentation internal-link check ==")
    for md in SCAN:
        if not md.is_file():
            check(f"{md.relative_to(REPO)} exists", False, "missing scan target")
            continue
        text = md.read_text(encoding="utf-8")
        base = md.parent
        for m in LINK.finditer(text):
            target = m.group(1).strip()
            if not is_checkable(target):
                continue
            path_part = target.split("#", 1)[0]
            resolved = (base / path_part).resolve()
            ok = resolved.is_file()
            if not ok:
                check(
                    f"{md.relative_to(REPO)} -> {target}",
                    False,
                    "target does not exist",
                )
            else:
                globals()["passed"] += 1
    print(f"\n== RESULT: {passed} passed, {failed} failed ==")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
