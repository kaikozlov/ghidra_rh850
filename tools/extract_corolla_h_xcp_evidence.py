#!/usr/bin/env python3
"""Compact target-native H evidence for XCP command-table residuals."""
from __future__ import annotations
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
RAW=ROOT/'community/albinoelephant/raw-20260818/albinoelephant-corolla-2023.20260814-0023/dump_codeflash_00000000_00200000_20260814-025814.bin'
C1=ROOT/'build/work/corpora/h_8965H1202000_xcp_decompilations.jsonl';C2=ROOT/'build/work/corpora/h_8965H1202000_xcp_helpers_decompilations.jsonl';OUT=ROOT/'data/generated/corolla_8965H1202000_xcp_decompiler_evidence.json'
FUNCS=[0x9232A,0x92462,0x9261E,0x92698,0x9227E,0x92314,0x9238A,0x92436,0x7C390,0x7C39C,0x92724]
def sha(b):return hashlib.sha256(b).hexdigest()
def load(p):
 d={}
 for l in p.read_text().splitlines():
  r=json.loads(l)
  if r.get('entry_addr'):d[int(r['entry_addr'],16)]=r
 return d
def main():
 raw=RAW.read_bytes();img=raw[:0x100000];rows=load(C1);rows.update(load(C2));out=[]
 for a in FUNCS:
  r=rows.get(a)
  if not r or not r.get('decompile_completed') or not r.get('decompiled_c'):raise SystemExit(f'missing {a:#x}')
  n=int(r['body_size']);c=r['decompiled_c'];out.append({'entry':f'0x{a:08X}','name':r.get('name',f'FUN_{a:08x}'),'body_size':n,'body_sha256':sha(img[a:a+n]),'decompiled_c_sha256':sha(c.encode()),'decompiled_c':c})
 payload={'schema':'corolla-h-xcp-decompiler-evidence-v1','software_id':'8965H1202000','image':{'path':str(RAW.relative_to(ROOT)),'codeflash_sha256':sha(img),'codeflash_size':len(img)},'functions':out,'function_count':len(out),'source_corpora':[{'path':str(C1.relative_to(ROOT)),'sha256':sha(C1.read_bytes())},{'path':str(C2.relative_to(ROOT)),'sha256':sha(C2.read_bytes())}],'boundary':'only forced XCP command/helper boundaries are promoted; unrelated disposable-project partitioning is ignored'}
 OUT.write_text(json.dumps(payload,indent=2,sort_keys=True)+'\n');print(f'wrote {OUT}: {len(out)} functions')
if __name__=='__main__':main()
