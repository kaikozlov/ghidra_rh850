#!/usr/bin/env python3
"""Compact target-native evidence for the remaining Corolla-H steering roles."""
from __future__ import annotations
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
RAW=ROOT/'community/albinoelephant/raw-20260818/albinoelephant-corolla-2023.20260814-0023/dump_codeflash_00000000_00200000_20260814-025814.bin'
SRC=ROOT/'build/h_8965H1202000_decompilations.corrected-context.raw.jsonl'
OUT=ROOT/'data/generated/corolla_8965H1202000_steering_nested_decompiler_evidence.json'
TARGETS=[
 0xC9C16,0xC9CD2,
 0xCB68A,0xCBE6E,
 0xCB8BA,0xCB9B6,0xCBA40,
 0xCD3CC,0xCD440,0xCE974,0xCEFF8,0xB8E84,
 0xCEDAE,0xCF028,
]
def sha(b): return hashlib.sha256(b).hexdigest()
def load():
 d={}
 for line in SRC.read_text().splitlines():
  try:r=json.loads(line)
  except json.JSONDecodeError:continue
  if r.get('record')=='function' and r.get('entry_addr'):d[int(r['entry_addr'],16)]=r
 return d
def main():
 raw=RAW.read_bytes()[:0x100000]; src=load(); out=[]
 for a in TARGETS:
  r=src.get(a)
  if not r or not r.get('decompile_completed') or not r.get('decompiled_c'): raise SystemExit(f'missing H function {a:#x}')
  n=int(r['body_size']); c=r['decompiled_c']
  out.append({'entry':f'0x{a:08X}','body_size':n,'body_sha256':sha(raw[a:a+n]),'decompiled_c_sha256':sha(c.encode()),'decompiled_c':c})
 p={'schema':'corolla-h-steering-nested-evidence-v1','software_id':'8965H1202000','image':{'path':str(RAW.relative_to(ROOT)),'codeflash_size':len(raw),'codeflash_sha256':sha(raw)},'source_corpus':{'path':str(SRC.relative_to(ROOT)),'sha256':sha(SRC.read_bytes())},'functions':out,'function_count':len(out),'boundary':'remaining steering-role evidence only; target-native roles are bound by caller/callee topology and dataflow, not local byte alignment'}
 OUT.write_text(json.dumps(p,indent=2,sort_keys=True)+'\n'); print(f'wrote {OUT}: {len(out)} functions')
if __name__=='__main__':main()
