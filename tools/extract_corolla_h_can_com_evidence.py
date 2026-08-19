#!/usr/bin/env python3
"""Compact H-native evidence for the changed CAN/COM transport surface."""
from __future__ import annotations
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
RAW=ROOT/'community/albinoelephant/raw-20260818/albinoelephant-corolla-2023.20260814-0023/dump_codeflash_00000000_00200000_20260814-025814.bin'
CLEAN=ROOT/'build/h_8965H1202000_rdbihelper2_decompilations.jsonl'
FORCED=ROOT/'build/h_8965H1202000_can_com_rx_decompilations.jsonl'
OUT=ROOT/'data/generated/corolla_8965H1202000_can_com_decompiler_evidence.json'
CLEAN_FUNCS=[0x3E118,0x524B8,0x52F22,0x53030,0x58450,0x58BBC,0x6418C,0x77224,0x7AD8E,0x7EB10,0x7EB4E]
FORCED_FUNCS=[0x76A3C,0x78708,0x789EE,0x793FE,0x7A382,0x7A402,0x7ADC2,0x7B040]
def sha(b):return hashlib.sha256(b).hexdigest()
def load(p):
 d={}
 for l in p.read_text().splitlines():
  r=json.loads(l)
  if r.get('entry_addr'):d[int(r['entry_addr'],16)]=r
 return d
def main():
 raw=RAW.read_bytes();img=raw[:0x100000];clean=load(CLEAN);forced=load(FORCED);out=[]
 for src,addrs,label in [(clean,CLEAN_FUNCS,'clean'),(forced,FORCED_FUNCS,'forced')]:
  for a in addrs:
   r=src.get(a)
   if not r or not r.get('decompile_completed') or not r.get('decompiled_c'):raise SystemExit(f'missing {label} {a:#x}')
   n=int(r['body_size']);code=r['decompiled_c'];body=img[a:a+n]
   out.append({'entry':f'0x{a:08X}','name':r.get('name',f'FUN_{a:08x}'),'body_size':n,'body_sha256':sha(body),'decompiled_c_sha256':sha(code.encode()),'decompiled_c':code,'source_corpus':label})
 payload={'schema':'corolla-h-can-com-decompiler-evidence-v1','software_id':'8965H1202000','image':{'path':str(RAW.relative_to(ROOT)),'codeflash_size':len(img),'codeflash_sha256':sha(img)},'functions':sorted(out,key=lambda r:int(r['entry'],16)),'function_count':len(out),'source_corpora':{'clean':{'path':str(CLEAN.relative_to(ROOT)),'sha256':sha(CLEAN.read_bytes())},'forced':{'path':str(FORCED.relative_to(ROOT)),'sha256':sha(FORCED.read_bytes()),'boundary':'used only for transport entry points missing from the clean partition; no unrelated forced boundaries are promoted'}}}
 OUT.write_text(json.dumps(payload,indent=2,sort_keys=True)+'\n');print(f'wrote {OUT}: {len(out)} functions')
if __name__=='__main__':main()
