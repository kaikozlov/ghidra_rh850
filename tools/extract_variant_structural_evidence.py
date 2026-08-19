#!/usr/bin/env python3
"""Extract compact raw-image-bound structural fingerprints for selected functions."""
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path

def sha256(b: bytes) -> str: return hashlib.sha256(b).hexdigest()
def pi(s: str) -> int: return int(s, 0)
def disp(p: Path, root: Path) -> str:
    try: return str(p.resolve().relative_to(root.resolve()))
    except ValueError: return str(p)

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--image',type=Path,required=True);ap.add_argument('--fingerprints',type=Path,required=True)
    ap.add_argument('--software-id',required=True);ap.add_argument('--address',type=pi,action='append',default=[]);ap.add_argument('--out',type=Path,required=True)
    a=ap.parse_args(); root=Path(__file__).resolve().parents[1]; image=a.image.read_bytes()
    if len(image)!=0x100000: raise SystemExit(f'expected 1 MiB image, got {len(image):#x}')
    want=set(a.address); rows={}
    for line in a.fingerprints.read_text().splitlines():
        r=json.loads(line); entry=int(r['entry_addr'],16)
        if entry in want: rows[entry]=r
    missing=sorted(want-rows.keys())
    if missing: raise SystemExit('missing fingerprints: '+', '.join(hex(x) for x in missing))
    out=[]
    keep=['body_size','instruction_count','mnemonics','instruction_lengths','conditional_branch_count','unconditional_branch_count','direct_call_target_count','indirect_call_count','return_count']
    for entry in sorted(want):
        r=rows[entry]; size=r['body_size']; body=image[entry:entry+size]
        if len(body)!=size: raise SystemExit(f'body outside image {entry:#x}')
        q={'entry':f'0x{entry:08X}','body_sha256':sha256(body)}
        for k in keep:q[k]=r[k]
        out.append(q)
    payload={'schema':'rh850-variant-structural-evidence-v1','software_id':a.software_id,
             'image':{'path':disp(a.image,root),'size':len(image),'sha256':sha256(image)},
             'source_fingerprints':{'path':disp(a.fingerprints,root),'sha256':sha256(a.fingerprints.read_bytes()),'note':'Disposable Ghidra export; provenance only.'},
             'function_count':len(out),'functions':out}
    a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(payload,indent=2,sort_keys=True)+'\n')
    print(f'wrote {a.out}: {len(out)} functions')
if __name__=='__main__':main()
