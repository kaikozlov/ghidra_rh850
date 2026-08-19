#!/usr/bin/env python3
"""Compact target-native H evidence for the changed motor-control roles."""
from __future__ import annotations
import hashlib, json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
RAW=ROOT/'community/albinoelephant/raw-20260818/albinoelephant-corolla-2023.20260814-0023/dump_codeflash_00000000_00200000_20260814-025814.bin'
CORP=ROOT/'build/h_8965H1202000_rdbihelper2_decompilations.jsonl'
OUT=ROOT/'data/generated/corolla_8965H1202000_motor_control_decompiler_evidence.json'
FUNCS=[0x2E3E8,0x2E44C,0x2E780,0x2EDE6,0x324D4,0x32616,0x33C70,0x33D60,0x52DBA,0x57CEA,0x57EEE,0x57FC8,0x58226]
def sha(b):return hashlib.sha256(b).hexdigest()
def main():
 raw=RAW.read_bytes();img=raw[:0x100000];rows={}
 for l in CORP.read_text().splitlines():
  r=json.loads(l)
  if r.get('entry_addr'):rows[int(r['entry_addr'],16)]=r
 out=[]
 for a in FUNCS:
  r=rows.get(a)
  if not r or not r.get('decompile_completed') or not r.get('decompiled_c'):raise SystemExit(f'missing {a:#x}')
  n=int(r['body_size']);c=r['decompiled_c']
  out.append({'entry':f'0x{a:08X}','name':r.get('name',f'FUN_{a:08x}'),'body_size':n,'body_sha256':sha(img[a:a+n]),'decompiled_c_sha256':sha(c.encode()),'decompiled_c':c})
 payload={'schema':'corolla-h-motor-control-decompiler-evidence-v1','software_id':'8965H1202000','image':{'path':str(RAW.relative_to(ROOT)),'codeflash_size':len(img),'codeflash_sha256':sha(img)},'functions':out,'function_count':len(out),'source_corpus':{'path':str(CORP.relative_to(ROOT)),'sha256':sha(CORP.read_bytes()),'boundary':'clean disposable H application corpus; no motor entries were forced for this evidence set'}}
 OUT.write_text(json.dumps(payload,indent=2,sort_keys=True)+'\n');print(f'wrote {OUT}: {len(out)} functions')
if __name__=='__main__':main()
