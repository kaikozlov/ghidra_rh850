#!/usr/bin/env python3
"""Compact target-native evidence for the seven remaining named crypto roles."""
from __future__ import annotations
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
RAW=ROOT/'community/albinoelephant/raw-20260818/albinoelephant-corolla-2023.20260814-0023/dump_codeflash_00000000_00200000_20260814-025814.bin'
SOURCES={
 'clean':ROOT/'build/h_8965H1202000_rdbihelper2_decompilations.jsonl',
 'secoc_app':ROOT/'build/h_8965H1202000_secoc_app_decompilations.jsonl',
}
OUT=ROOT/'data/generated/corolla_8965H1202000_crypto_residue_decompiler_evidence.json'
PAIRS=[
 (0x70fc,0x70e0,'clean'),
 (0x68f0c,0x63244,'secoc_app'),(0x68f92,0x632ca,'secoc_app'),
 (0x68fc2,0x632fa,'secoc_app'),(0x69018,0x63350,'secoc_app'),
 (0x88302,0x82702,'secoc_app'),(0x88508,0x82908,'secoc_app'),
]
def sha(b):return hashlib.sha256(b).hexdigest()
def load(p):
 d={}
 for l in p.read_text().splitlines():
  r=json.loads(l)
  if r.get('entry_addr'):d[int(r['entry_addr'],16)]=r
 return d
def main():
 raw=RAW.read_bytes();img=raw[:0x100000];src={k:load(v) for k,v in SOURCES.items()};out=[]
 for s,h,sk in PAIRS:
  r=src[sk].get(h)
  if not r or not r.get('decompile_completed') or not r.get('decompiled_c'):raise SystemExit(f'missing {h:#x}')
  n=int(r['body_size']);c=r['decompiled_c']
  out.append({'reference_entry':f'0x{s:08X}','target_entry':f'0x{h:08X}','target_reported_body_size':n,'body_sha256':sha(img[h:h+n]),'decompiled_c_sha256':sha(c.encode()),'decompiled_c':c,'source_corpus':sk})
 payload={'schema':'corolla-h-crypto-residue-decompiler-evidence-v1','software_id':'8965H1202000','image':{'path':str(RAW.relative_to(ROOT)),'codeflash_size':len(img),'codeflash_sha256':sha(img)},'functions':out,'function_count':len(out),'source_corpora':{k:{'path':str(v.relative_to(ROOT)),'sha256':sha(v.read_bytes())} for k,v in SOURCES.items()},'boundary':'seven residual canonical crypto roles only; no neighboring disposable-project boundaries are promoted'}
 OUT.write_text(json.dumps(payload,indent=2,sort_keys=True)+'\n');print(f'wrote {OUT}: {len(out)} functions')
if __name__=='__main__':main()
