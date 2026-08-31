#!/usr/bin/env python3
"""Inspect and safely clean the canonical ignored build workspace."""
from __future__ import annotations
import argparse, json, shutil, subprocess, sys
from pathlib import Path
REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))
from tools.build_paths import for_repo
CATEGORIES = ("cache", "work", "out", "logs", "tmp")

def size_bytes(path: Path) -> int:
    if not path.exists(): return 0
    if path.is_file(): return path.stat().st_size
    total=0
    for p in path.rglob('*'):
        try:
            if p.is_file() and not p.is_symlink(): total += p.stat().st_size
        except FileNotFoundError: pass
    return total

def daemon_running() -> bool:
    return subprocess.run(["pgrep","-f","AnalyzeHeadless.*rh850"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode == 0


def require_canonical_root(paths) -> None:
    canonical = (REPO / "build").resolve()
    if paths.root != canonical:
        raise SystemExit(
            f"refusing destructive build-layout operation with BUILD_ROOT override: {paths.root}\n"
            f"expected repository build root: {canonical}"
        )

def status(paths):
    root=paths.root
    return {
        "schema":"ghidra-rh850-build-layout-v1",
        "root":str(root),
        "categories":{n:{"path":str(getattr(paths,n)),"bytes":size_bytes(getattr(paths,n))} for n in CATEGORIES},
    }

def main()->int:
    ap=argparse.ArgumentParser()
    sub=ap.add_subparsers(dest='cmd',required=True)
    sub.add_parser('init')
    st=sub.add_parser('status'); st.add_argument('--json',action='store_true')
    cl=sub.add_parser('clean'); cl.add_argument('scopes',nargs='*',choices=CATEGORIES); cl.add_argument('--force',action='store_true')
    a=ap.parse_args(); paths=for_repo(REPO)
    if a.cmd=='init': paths.ensure(); print(paths.root); return 0
    if a.cmd=='status':
        d=status(paths)
        if a.json: print(json.dumps(d,indent=2)); return 0
        print(f"build root: {d['root']}")
        for n,row in d['categories'].items(): print(f"  {n:5s} {row['bytes']:12d}  {row['path']}")
        return 0
    require_canonical_root(paths)
    scopes=a.scopes or ['tmp','logs']
    if any(s in {'work','cache'} for s in scopes) and not a.force:
        raise SystemExit("refusing to remove work/cache without --force")
    if any(s in {'work','cache'} for s in scopes) and daemon_running():
        raise SystemExit("refusing to remove build/work or build/cache while an RH850 Ghidra daemon is running")
    for scope in scopes:
        p=getattr(paths,scope)
        if p.exists(): shutil.rmtree(p)
        p.mkdir(parents=True,exist_ok=True)
        print(f"cleaned {p}")
    return 0
if __name__=='__main__': raise SystemExit(main())
