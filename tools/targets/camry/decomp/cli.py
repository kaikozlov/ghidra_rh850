"""Inspect the Camry reconstruction and run conversion and oracle workflows."""
from __future__ import annotations

import argparse
from tools import REPO_ROOT
import json

from . import corpus, sources, tree



def cmd_status(_args: argparse.Namespace) -> int:
    symbols = tree.load_symbols()
    report = tree.image_summary(symbols)
    rows = tree.load_matched()
    named = sum(1 for row in symbols if not row["name"].startswith("FUN_"))
    report["named_functions"] = named
    report["equivalent_functions"] = sum(1 for row in rows if row["status"] == "equivalent")
    report["byte_matched_functions"] = sum(1 for row in rows if row["status"] == "byte-matched")
    report["converted_functions"] = sum(1 for row in rows if row["status"] == "converted")
    report["unconvertible_functions"] = sum(1 for row in rows if row["status"] == "unconvertible")
    print(json.dumps(report, indent=2))
    return 0


def cmd_oracle(_args: argparse.Namespace) -> int:
    from .oracle import run_oracles

    return run_oracles()


def cmd_lift(args: argparse.Namespace) -> int:
    from .lifting.workflow import run

    return run(args.operation)


def cmd_source(args: argparse.Namespace) -> int:
    try:
        symbol, path, body = sources.locate_source(args.query)
    except ValueError as exc:
        raise SystemExit(str(exc)) from None
    print(f"/* {tree.TARGET}: {symbol['name']} @ {symbol['addr']}")
    print(f" * {path.relative_to(REPO_ROOT)} */")
    print(body, end="")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="toyota decomp", description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    status = sub.add_parser("status", help="print image and matched-function counts")
    status.set_defaults(func=cmd_status)
    source = sub.add_parser("source", help="show the effective reconstructed C and its source path")
    source.add_argument("query", help="canonical function name or hexadecimal entry address")
    source.set_defaults(func=cmd_source)
    corpus_parser = sub.add_parser("corpus", help="compile every decompiler body and rank the failures")
    corpus_parser.set_defaults(func=corpus.cmd_corpus)
    oracle = sub.add_parser(
        "oracle",
        help="compare converted leaves with original bytes and mark only agreements",
    )
    oracle.set_defaults(func=cmd_oracle)
    lift = sub.add_parser("lift", help="report, emit, or oracle-check instruction lifts")
    lift.add_argument("operation", choices=("report", "emit", "check"))
    lift.set_defaults(func=cmd_lift)
    args = parser.parse_args(argv)
    return args.func(args)
