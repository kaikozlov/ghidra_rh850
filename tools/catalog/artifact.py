#!/usr/bin/env python3
"""Discover, inspect, and regenerate tracked generated artifacts."""
from __future__ import annotations

import argparse
import json
import shlex
import subprocess
import sys
from pathlib import Path

from tools.catalog.artifact_catalog import (
    REPO, consumers, producer_args, producer_candidates, rows, tracked_artifacts,
)


def resolve_artifact(query: str) -> str:
    artifacts = tracked_artifacts()
    q = query.casefold()
    exact = [p for p in artifacts if p.casefold() == q or Path(p).name.casefold() == q]
    if len(exact) == 1:
        return exact[0]
    matches = [p for p in artifacts if q in p.casefold()]
    if len(matches) == 1:
        return matches[0]
    if not matches:
        raise SystemExit(f"no tracked generated artifact matches {query!r}")
    raise SystemExit("ambiguous artifact; matches:\n" + "\n".join(f"  {p}" for p in matches[:80]))


def print_rows(items: list[dict], as_json: bool) -> None:
    if as_json:
        print(json.dumps(items, indent=2, sort_keys=True))
        return
    for row in items:
        producers = ",".join(row["producers"]) or "no producer"
        print(f"{row['artifact']}\tproducer={producers}")


def describe(path: str) -> dict:
    return {
        "artifact": path,
        "size": (REPO / path).stat().st_size,
        "producers": producer_candidates(path),
        "consumers": consumers(path),
    }


def cmd_list(args: argparse.Namespace) -> int:
    print_rows(rows(args.query), args.json)
    return 0


def cmd_show(args: argparse.Namespace) -> int:
    row = describe(resolve_artifact(args.artifact))
    if args.json:
        print(json.dumps(row, indent=2, sort_keys=True))
    else:
        print(row["artifact"])
        print(f"size\t{row['size']}")
        print("producers\t" + (", ".join(row["producers"]) or "no producer"))
        print("consumers")
        for value in row["consumers"]:
            print(f"  {value}")
    return 0


def choose_producer(path: str, override: str | None) -> str:
    candidates = producer_candidates(path)
    if not candidates:
        raise SystemExit(f"no producer declared for {path}")
    if override:
        candidate = override if override.startswith("tools/") else f"tools/{override}"
        if candidate not in candidates:
            raise SystemExit(f"{candidate} does not own {path}; declared producers: {', '.join(candidates)}")
        return candidate
    if len(candidates) > 1:
        raise SystemExit(
            f"producer is ambiguous for {path}; pass --producer. Declared producers:\n" +
            "\n".join(f"  {p}" for p in candidates)
        )
    return candidates[0]


def producer_command(producer: str, passthrough: list[str]) -> list[str]:
    """Launch a producer through the locked project environment.

    Python producers run as modules so repository imports resolve through the
    installed package; non-Python producers keep direct execution.
    """
    if producer.endswith(".py"):
        module = producer[: -len(".py")].replace("/", ".")
        return ["uv", "run", "--project", str(REPO), "--locked", "python", "-m", module, *passthrough]
    return [str(REPO / producer), *passthrough]


def cmd_regen(args: argparse.Namespace) -> int:
    path = resolve_artifact(args.artifact)
    producer = choose_producer(path, args.producer)
    command = producer_command(producer, [*producer_args(path, producer), *args.generator_args])
    rendered = shlex.join(command)
    if args.dry_run:
        print(rendered)
        return 0
    print("+ " + rendered, file=sys.stderr)
    return subprocess.run(command, cwd=REPO, check=False).returncode


def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(prog="artifact", description=__doc__)
    sub = ap.add_subparsers(dest="command", required=True)
    p = sub.add_parser("list", help="list tracked generated artifacts")
    p.add_argument("query", nargs="?")
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=cmd_list)
    p = sub.add_parser("show", help="show producer and consumers")
    p.add_argument("artifact")
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=cmd_show)
    p = sub.add_parser(
        "regen", help="run the declared producer for one artifact",
        epilog="Pass generator arguments after --.",
    )
    p.add_argument("artifact")
    p.add_argument("--producer", help="select a producer when multiple candidates exist")
    p.add_argument("--dry-run", action="store_true", help="print the exact producer command without running it")
    p.set_defaults(func=cmd_regen)
    return ap


def main() -> int:
    tokens = sys.argv[1:]
    passthrough = []
    if tokens[:1] == ["regen"] and "--" in tokens:
        separator = tokens.index("--")
        tokens, passthrough = tokens[:separator], tokens[separator + 1:]
    args = build_parser().parse_args(tokens)
    args.generator_args = passthrough
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
