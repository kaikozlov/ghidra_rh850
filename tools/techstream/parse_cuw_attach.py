#!/usr/bin/env python3
"""Parse an extracted CUW `attach.att` descriptor without interpretation drift."""
from __future__ import annotations
import argparse, json
from pathlib import Path

from cuw_attach import capture_shape


def parse_attach(path: Path) -> dict:
    """Compatibility API retaining the historical capture-oriented shape."""
    return capture_shape(path)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("attach", type=Path)
    ap.add_argument("--output", type=Path)
    args = ap.parse_args()
    result = parse_attach(args.attach)
    data = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(data, encoding="utf-8")
    else:
        print(data, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
