#!/usr/bin/env python3
"""Search maintained target/subsystem reports, artifacts, and verification suites."""
from __future__ import annotations

import argparse
import json
import tomllib
from pathlib import Path

from tools import REPO_ROOT
from tools.catalog.artifact_catalog import rows as artifact_rows

ROOT = REPO_ROOT

MANIFEST = ROOT / "verification.toml"


def matches(query: str, *values: object) -> bool:
    q = query.casefold()
    return any(q in str(v).casefold() for v in values if v is not None)


def artifacts(query: str) -> list[dict]:
    return [{"kind": "artifact", **row} for row in artifact_rows(query)]


def suites(query: str) -> list[dict]:
    out = []
    with MANIFEST.open("rb") as handle:
        suite_rows = tomllib.load(handle).get("suite", {})
    for name, row in suite_rows.items():
        tests = row.get("tests", [])
        paths = row.get("paths", [])
        if matches(query, name, *tests, *paths):
            out.append({
                "kind": "suite",
                "name": name,
                "tests": tests,
                "modes": row.get("modes", ["full", "local"]),
                "oracle": row.get("oracle"),
                "requires_external": row.get("requires_external", []),
            })
    return out


def docs(query: str) -> list[dict]:
    out = []
    q = query.casefold()
    for path in sorted((ROOT / "docs").rglob("*.md")):
        rel = path.relative_to(ROOT).as_posix()
        text = path.read_text(encoding="utf-8", errors="replace")
        heading = next((line[2:].strip() for line in text.splitlines() if line.startswith("# ")), Path(rel).stem)
        if q not in rel.casefold() and q not in heading.casefold() and q not in text.casefold():
            continue
        # Show the first matching non-generated line as context rather than dumping prose.
        context = ""
        for line in text.splitlines():
            clean = line.strip()
            if q in clean.casefold() and clean and not clean.startswith("<!--"):
                context = clean[:240]
                break
        out.append({"kind": "doc", "path": rel, "title": heading, "match": context})
    return out


def format_result(row: dict) -> str:
    kind = row["kind"]
    if kind == "artifact":
        return f"artifact\t{row['artifact']}\tproducer={','.join(row['producers']) or '—'}"
    if kind == "suite":
        return f"suite\t{row['name']}\ttests={','.join(row['tests'])}\tmodes={','.join(row['modes'])}"
    if kind == "doc":
        return f"doc\t{row['path']}\t{row['title']}\t{row['match']}"
    return json.dumps(row, sort_keys=True)


def main() -> int:
    ap = argparse.ArgumentParser(prog="know", description=__doc__)
    ap.add_argument("query", help="Subsystem, filename, suite, or free-text fragment")
    ap.add_argument("--kind", action="append", choices=("doc", "artifact", "suite"))
    ap.add_argument("--limit", type=int, default=60)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    kinds = set(args.kind or ("doc", "artifact", "suite"))
    loaders = {
        "artifact": artifacts,
        "suite": suites,
        "doc": docs,
    }
    result = []
    for kind in ("doc", "artifact", "suite"):
        if kind in kinds:
            result.extend(loaders[kind](args.query))
    result = result[: max(0, args.limit)]
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        for row in result:
            print(format_result(row))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
