#!/usr/bin/env python3
"""Compact target-native H evidence for the changed storage/NvM roles."""
from __future__ import annotations
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
RAW=ROOT/'community/albinoelephant/raw-20260818/albinoelephant-corolla-2023.20260814-0023/dump_codeflash_00000000_00200000_20260814-025814.bin'
CORP=ROOT/'build/h_8965H1202000_storage_nvm_decompilations.jsonl'
OUT=ROOT/'data/generated/corolla_8965H1202000_storage_nvm_decompiler_evidence.json'
FUNCS=[0x4A534,0x5FFBC,0x610EA]
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
  n=int(r['body_size']);code=r['decompiled_c']
  out.append({'entry':f'0x{a:08X}','name':r.get('name',f'FUN_{a:08x}'),'body_size':n,'body_sha256':sha(img[a:a+n]),'decompiled_c_sha256':sha(code.encode()),'decompiled_c':code})
 payload={'schema':'corolla-h-storage-nvm-decompiler-evidence-v1','software_id':'8965H1202000','image':{'path':str(RAW.relative_to(ROOT)),'codeflash_sha256':sha(img),'codeflash_size':len(img)},'functions':out,'function_count':len(out),'source_corpus':{'path':str(CORP.relative_to(ROOT)),'sha256':sha(CORP.read_bytes()),'boundary':'disposable H corpus with only the three missing storage/NvM entry points forced'}}
 OUT.write_text(json.dumps(payload,indent=2,sort_keys=True)+'\n');print(f'wrote {OUT}: {len(out)} functions')
if __name__=='__main__':main()
