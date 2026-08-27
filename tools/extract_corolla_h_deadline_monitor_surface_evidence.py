#!/usr/bin/env python3
"""Compact H-native evidence for the regenerated deadline-monitor callback surface."""
from __future__ import annotations
import hashlib,json,struct
from pathlib import Path
from corolla_h_constants import H_DEADLINE_TABLES, RAW_DUMP
ROOT=Path(__file__).resolve().parents[1]
RAW=RAW_DUMP
SRC=ROOT/'build/work/corpora/h_deadline_forced.jsonl'
OUT=ROOT/'data/generated/corolla_8965H1202000_deadline_monitor_surface_decompiler_evidence.json'
TABLES=tuple((base,count,stride,offs) for _name,base,count,stride,offs in H_DEADLINE_TABLES)
SUPPORT=(0x387E4,0x639CA,0x6462A)
def sha(b):return hashlib.sha256(b).hexdigest()
def callbacks(raw):
 vals=[]
 for base,count,stride,offs in TABLES:
  for i in range(count):
   for off in offs:
    x=struct.unpack_from('<I',raw,base+i*stride+off)[0]
    if x: vals.append(x)
 return sorted(set(vals))
def main():
 raw=RAW.read_bytes()[:0x100000]; by={}
 for line in SRC.read_text().splitlines():
  r=json.loads(line)
  if r.get('record')=='function':by[int(r['entry_addr'],16)]=r
 targets=callbacks(raw)+list(SUPPORT);out=[]
 for a in sorted(set(targets)):
  r=by.get(a)
  if not r or not r.get('decompile_completed') or not r.get('decompiled_c'):raise SystemExit(f'missing H function {a:#x}')
  n=int(r['body_size']);c=r['decompiled_c']
  out.append({'entry':f'0x{a:08X}','body_size':n,'body_sha256':sha(raw[a:a+n]),'decompiled_c_sha256':sha(c.encode()),'decompiled_c':c})
 p={'schema':'corolla-h-deadline-monitor-surface-evidence-v1','software_id':'8965H1202000','image':{'path':str(RAW.relative_to(ROOT)),'codeflash_size':len(raw),'codeflash_sha256':sha(raw)},'source_corpus':{'path':str(SRC.relative_to(ROOT)),'sha256':sha(SRC.read_bytes()),'boundary':'disposable H corpus with exactly the 88 callback-table targets forced as functions before decompilation'},'callback_count':len(callbacks(raw)),'support_count':len(SUPPORT),'functions':out,'function_count':len(out)}
 OUT.write_text(json.dumps(p,indent=2,sort_keys=True)+'\n');print(f'wrote {OUT}: {len(out)} functions ({len(callbacks(raw))} callbacks)')
if __name__=='__main__':main()
