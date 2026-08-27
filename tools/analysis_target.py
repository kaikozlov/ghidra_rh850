#!/usr/bin/env python3
"""Resolve first-class analysis-target metadata from data/analysis_targets.json."""
from __future__ import annotations
import argparse, json, shlex
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
REGISTRY = REPO / "data/analysis_targets.json"

def load() -> dict:
    obj = json.loads(REGISTRY.read_text())
    if obj.get("schema") != "ghidra-rh850-analysis-targets-v1":
        raise SystemExit("analysis target registry schema drift")
    return obj

def target(name: str | None) -> tuple[str, dict]:
    obj = load(); name = name or obj["default_target"]
    try: row = obj["targets"][name]
    except KeyError: raise SystemExit(f"unknown analysis target: {name}")
    return name, row

def main() -> int:
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("target", nargs="?")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--shell", action="store_true", help="emit shell exports for tools/g")
    ap.add_argument("--field")
    args=ap.parse_args()
    name,row=target(args.target)
    if args.field:
        value=row.get(args.field)
        if value is None: raise SystemExit(f"target {name} has no field {args.field}")
        print(value); return 0
    if args.shell:
        vals={
            "GHIDRA_ANALYSIS_TARGET": name,
            "GHIDRA_PROJECT": str(REPO / row["work_dir"]),
        }
        for k,v in vals.items(): print(f"export {k}={shlex.quote(v)}")
        return 0
    out={"name":name, **row}
    if args.json or True: print(json.dumps(out,indent=2,sort_keys=True))
    return 0
if __name__ == "__main__": raise SystemExit(main())
