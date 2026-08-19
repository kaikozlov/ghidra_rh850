#!/usr/bin/env python3
"""Parse an extracted CUW `attach.att` descriptor without interpretation drift.

The descriptor grammar is Windows-profile/INI-like.  This tool intentionally
preserves unknown sections/keys and raw values: it is capture-ready before a
matching Toyota calibration becomes available.
"""
from __future__ import annotations
import argparse, configparser, json
from pathlib import Path


def parse_attach(path: Path) -> dict:
    raw = path.read_bytes()
    # Toyota's V18 client is native ANSI.  latin-1 gives a reversible byte->text
    # mapping for unknown regional bytes instead of silently replacing them.
    text = raw.decode("latin1")
    cp = configparser.RawConfigParser(interpolation=None, strict=False, delimiters=("=",))
    cp.optionxform = str
    cp.read_string(text)
    return {
        "source": str(path),
        "size": len(raw),
        "sections": [
            {"name": section, "fields": [{"name": k, "value": v} for k, v in cp.items(section, raw=True)]}
            for section in cp.sections()
        ],
    }


def main() -> int:
    ap=argparse.ArgumentParser(); ap.add_argument("attach", type=Path); ap.add_argument("--output", type=Path)
    a=ap.parse_args(); result=parse_attach(a.attach)
    data=json.dumps(result, indent=2, sort_keys=True)+"\n"
    if a.output: a.output.write_text(data, encoding="utf-8")
    else: print(data, end="")
    return 0

if __name__ == "__main__": raise SystemExit(main())
