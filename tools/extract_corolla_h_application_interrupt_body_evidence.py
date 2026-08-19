#!/usr/bin/env python3
"""Compact H-native evidence for application timer/CAN interrupt bodies."""
from __future__ import annotations
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
RAW=ROOT/'community/albinoelephant/raw-20260818/albinoelephant-corolla-2023.20260814-0023/dump_codeflash_00000000_00200000_20260814-025814.bin'
SRC=ROOT/'build/h_small_adapters_forced.jsonl'
OUT=ROOT/'data/generated/corolla_8965H1202000_application_interrupt_body_decompiler_evidence.json'
TARGETS=[0x5F258,0x5F294,0x5F2D0,0x5FB12,0x5FB1E,0x7D240,0x7EB4E]
def sha(b):return hashlib.sha256(b).hexdigest()
def main():
 raw=RAW.read_bytes()[:0x100000];by={}
 for l in SRC.read_text().splitlines():
  r=json.loads(l)
  if r.get('record')=='function':by[int(r['entry_addr'],16)]=r
 out=[]
 for a in TARGETS:
  r=by.get(a)
  if not r or not r.get('decompile_completed') or not r.get('decompiled_c'):raise SystemExit(f'missing {a:#x}')
  n=int(r['body_size']);c=r['decompiled_c'];out.append({'entry':f'0x{a:08X}','body_size':n,'body_sha256':sha(raw[a:a+n]),'decompiled_c_sha256':sha(c.encode()),'decompiled_c':c})
 p={'schema':'corolla-h-application-interrupt-body-evidence-v1','software_id':'8965H1202000','image':{'path':str(RAW.relative_to(ROOT)),'codeflash_size':len(raw),'codeflash_sha256':sha(raw)},'source_corpus':{'path':str(SRC.relative_to(ROOT)),'sha256':sha(SRC.read_bytes())},'functions':out,'function_count':len(out)}
 OUT.write_text(json.dumps(p,indent=2,sort_keys=True)+'\n');print(f'wrote {OUT}: {len(out)} functions')
if __name__=='__main__':main()
