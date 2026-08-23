#!/usr/bin/env python3
"""Inspect, migrate, and safely clean the canonical ignored build workspace."""
from __future__ import annotations
import argparse, json, shutil, subprocess, sys
from pathlib import Path
REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))
from tools.build_paths import for_repo
CATEGORIES = ("cache", "work", "out", "logs", "tmp")
LEGACY_MIGRATIONS = {
    "ghidra-cli": ("cache", "ghidra-cli"),
    "ghidra-home": ("cache", "ghidra-home"),
    "toolchains": ("cache", "toolchains"),
    "processor-extension-src": ("cache", "processor-extension-src"),
    "ghidra-cli.env": ("cache", "ghidra-cli.env"),
    "ghidra-processor.env": ("cache", "ghidra-processor.env"),
    "project": ("work", "project"),
    "pe-project": ("work", "pe-project"),
    "secoc-targets": ("work", "secoc-targets"),
    "ephemeral-runtime-targets": ("work", "ephemeral-runtime-targets"),
    "processor-fixture-project": ("work", "processor-fixture-project"),
    "sleigh-resolution-project": ("work", "sleigh-resolution-project"),
    "parity-project": ("work", "parity-project"),
    "pseudocode": ("out", "pseudocode"),
    "ephemeral-runtime": ("out", "ephemeral-runtime"),
    "target-evidence": ("out", "target-evidence"),
    "processor_manifest.json": ("out", "processor_manifest.json"),
    "decompiler-signatures.txt": ("out", "decompiler-signatures.txt"),
    "ghidra_project_inventory.jsonl": ("out", "ghidra_project_inventory.jsonl"),
    "application_tx_producer_refs.csv": ("out", "application_tx_producer_refs.csv"),
    "sleigh-logs": ("logs", "sleigh"),
}

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


def legacy_entries(paths) -> list[Path]:
    known = {getattr(paths, name).resolve() for name in CATEGORIES}
    if not paths.root.is_dir():
        return []
    return sorted((p for p in paths.root.iterdir() if p.resolve() not in known), key=lambda p: p.name)

def status(paths):
    root=paths.root
    legacy=[{"name":p.name,"bytes":size_bytes(p)} for p in legacy_entries(paths)]
    return {
        "schema":"ghidra-rh850-build-layout-v1",
        "root":str(root),
        "categories":{n:{"path":str(getattr(paths,n)),"bytes":size_bytes(getattr(paths,n))} for n in CATEGORIES},
        "legacy_top_level":sorted(legacy,key=lambda x:x['name']),
    }

def main()->int:
    ap=argparse.ArgumentParser()
    sub=ap.add_subparsers(dest='cmd',required=True)
    sub.add_parser('init')
    st=sub.add_parser('status'); st.add_argument('--json',action='store_true'); st.add_argument('--all',action='store_true',help='show every legacy top-level entry')
    cl=sub.add_parser('clean'); cl.add_argument('scopes',nargs='*',choices=CATEGORIES); cl.add_argument('--force',action='store_true')
    mg=sub.add_parser('migrate-known', help='move known pre-layout reusable state into canonical namespaces'); mg.add_argument('--apply',action='store_true',help='perform moves; default is dry-run')
    ml=sub.add_parser('migrate-legacy', help='quarantine all remaining pre-layout top-level state under build/work/legacy-root'); ml.add_argument('--apply',action='store_true',help='perform moves; default is dry-run')
    a=ap.parse_args(); paths=for_repo(REPO)
    if a.cmd=='init': paths.ensure(); print(paths.root); return 0
    if a.cmd=='status':
        d=status(paths)
        if a.json: print(json.dumps(d,indent=2)); return 0
        print(f"build root: {d['root']}")
        for n,row in d['categories'].items(): print(f"  {n:5s} {row['bytes']:12d}  {row['path']}")
        if d['legacy_top_level']:
            rows = sorted(d['legacy_top_level'], key=lambda row: row['bytes'], reverse=True)
            total = sum(row['bytes'] for row in rows)
            print(f"legacy pre-layout entries: {len(rows)} totaling {total} bytes (not used by canonical defaults)")
            shown = rows if a.all else rows[:20]
            for row in shown: print(f"  {row['bytes']:12d}  {row['name']}")
            if len(shown) < len(rows):
                print(f"  ... {len(rows) - len(shown)} more; use status --all or --json")
        return 0
    if a.cmd == 'migrate-known':
        require_canonical_root(paths)
        if daemon_running():
            raise SystemExit("refusing legacy migration while an RH850 Ghidra daemon is running")
        moves = []
        for name, (category, child) in LEGACY_MIGRATIONS.items():
            src = paths.root / name
            dst = getattr(paths, category) / child
            if not src.exists():
                continue
            if dst.exists():
                print(f"CONFLICT {src} -> {dst} (destination exists)")
                continue
            moves.append((src, dst))
        # Promotion corpora are explicitly workspace state; migrate known top-level
        # H corpus exports without touching arbitrary one-off analysis directories.
        if paths.root.is_dir():
            corpus_dir = paths.work / 'corpora'
            for src in sorted(paths.root.glob('h_*.jsonl')):
                dst = corpus_dir / src.name
                if dst.exists():
                    print(f"CONFLICT {src} -> {dst} (destination exists)")
                else:
                    moves.append((src, dst))
        if not moves:
            print("no known legacy entries to migrate")
            return 0
        for src, dst in moves:
            print(f"{'MOVE' if a.apply else 'WOULD MOVE'} {src} -> {dst}")
            if a.apply:
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(src), str(dst))
        if not a.apply:
            print("dry-run only; re-run with --apply")
        return 0
    if a.cmd == 'migrate-legacy':
        require_canonical_root(paths)
        if daemon_running():
            raise SystemExit("refusing legacy migration while an RH850 Ghidra daemon is running")
        entries = legacy_entries(paths)
        if not entries:
            print("no legacy top-level entries to migrate")
            return 0
        destination_root = paths.work / "legacy-root"
        conflicts = []
        moves = []
        for src in entries:
            dst = destination_root / src.name
            if dst.exists():
                conflicts.append((src, dst))
            else:
                moves.append((src, dst))
        for src, dst in conflicts:
            print(f"CONFLICT {src} -> {dst} (destination exists)")
        for src, dst in moves:
            print(f"{'MOVE' if a.apply else 'WOULD MOVE'} {src} -> {dst}")
            if a.apply:
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(src), str(dst))
        if conflicts:
            raise SystemExit(f"refusing incomplete legacy migration: {len(conflicts)} conflict(s)")
        if not a.apply:
            print("dry-run only; re-run with --apply")
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
