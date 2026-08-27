#!/usr/bin/env python3
"""Resolve first-class analysis-target metadata from data/analysis_targets.json."""
from __future__ import annotations
import argparse, json
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

def path(name: str | None, field: str) -> Path:
    resolved, row = target(name)
    value = row.get(field)
    if not isinstance(value, str):
        raise KeyError(f"target {resolved} has no path field {field}")
    return (REPO / value).resolve()

def verified_file(name: str | None, field: str) -> Path:
    """Resolve a registered file and enforce sibling size/hash metadata when present."""
    import hashlib
    resolved, row = target(name)
    value = row.get(field)
    if not isinstance(value, str):
        raise KeyError(f"target {resolved} has no field {field}")
    p = (REPO / value).resolve()
    if not p.is_file():
        raise FileNotFoundError(p)
    size = row.get(f"{field}_size")
    digest = row.get(f"{field}_sha256")
    if size is not None and p.stat().st_size != int(size):
        raise ValueError(f"target {resolved} {field} size drift: {p.stat().st_size} != {size}")
    if digest is not None and hashlib.sha256(p.read_bytes()).hexdigest() != digest:
        raise ValueError(f"target {resolved} {field} identity drift")
    return p

def main() -> int:
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("target", nargs="?")
    ap.add_argument("--list", action="store_true", help="list configured analysis targets")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--field")
    args=ap.parse_args()
    if args.list:
        obj=load()
        rows=[{"name":name, **row} for name,row in obj["targets"].items()]
        if args.json: print(json.dumps(rows,indent=2,sort_keys=True))
        else:
            for row in rows:
                print(f"{row['name']}\t{row['status']}\t{row['vehicle']}\t{row['software_id']}")
        return 0
    name,row=target(args.target)
    if args.field:
        value=row.get(args.field)
        if value is None: raise SystemExit(f"target {name} has no field {args.field}")
        print(value); return 0
    print(json.dumps({"name":name, **row},indent=2,sort_keys=True))
    return 0
if __name__ == "__main__": raise SystemExit(main())
