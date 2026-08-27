"""Shared exact-F33 canonical-corpus helpers."""
from __future__ import annotations
from pathlib import Path
REPO=Path(__file__).resolve().parents[1]
CORPUS=REPO/'data/generated/camry-8965F3307000/decompilations.jsonl'
def body_bytes(image:bytes,row:dict)->bytes:
    ranges=row.get('body_ranges')
    if not ranges:
        key='entry_addr' if 'entry_addr' in row else 'entry'; e=int(row[key],16); n=int(row['body_size']); return image[e:e+n]
    chunks=[]
    for r in ranges:
        if r.get('space')!='ram': raise ValueError(f"unsupported function body space {r.get('space')}")
        lo=int(r['min'],16); hi=int(r['max'],16)
        if lo<0 or hi<lo or hi>=len(image): raise ValueError(f'body range outside CodeFlash: {lo:#x}..{hi:#x}')
        chunks.append(image[lo:hi+1])
    out=b''.join(chunks)
    if len(out)!=int(row['body_size']): raise ValueError(f"body-range size mismatch {row.get('entry_addr', row.get('entry'))}: {len(out)} != {row['body_size']}")
    return out
def display_path(path:Path)->str:
    r=path.resolve(); rr=REPO.resolve(); return str(r.relative_to(rr)) if r.is_relative_to(rr) else str(path)
