#!/usr/bin/env python3
"""Compact target-native evidence for Corolla-H diagnostic residue closure."""
from __future__ import annotations
import hashlib,json,struct
from pathlib import Path
from corolla_h_constants import RAW_DUMP as H_RAW_DUMP
ROOT=Path(__file__).resolve().parents[1]
RAW=H_RAW_DUMP
SRC=ROOT/'build/work/corpora/h_diag_wdbi_exact.jsonl'
OUT=ROOT/'data/generated/corolla_8965H1202000_diagnostic_residue_decompiler_evidence.json'
ROLE_TARGETS=[
 0x4826A,0x7A510,0x8467E,0x85544,0x8E6D0,0x8E6FC,0x8EB7C,0x8EC88,
 0x8ED4E,0x8EE58,0x8EE98,0x8EFC0,0x8F4EC,0x90602,0x9064A,0x906EC,0x90CB2,
 0xB2B6E,0xB486C,0xB5346,0xB5A30,0xB66B6,0xFDE58,0xFDED0,0xFE060,0xFE09C,0xFE0C4,
]
def sha(b):return hashlib.sha256(b).hexdigest()
def load():
 d={}
 for l in SRC.read_text().splitlines():
  r=json.loads(l)
  if r.get('record')=='function' and r.get('entry_addr'):d[int(r['entry_addr'],16)]=r
 return d
def main():
 raw=RAW.read_bytes()[:0x100000]; d=load(); targets=set(ROLE_TARGETS)
 for i in range(12):
  _did,_pad,s,r=struct.unpack_from('<HHII',raw,0x25530+i*12);targets|={s,r}
 targets|={0x877CC,0x87816}
 out=[]
 for a in sorted(targets):
  r=d.get(a)
  if not r or not r.get('decompile_completed') or not r.get('decompiled_c'):raise SystemExit(f'missing {a:#x}')
  n=int(r['body_size']);c=r['decompiled_c']
  out.append({'entry':f'0x{a:08X}','body_size':n,'body_sha256':sha(raw[a:a+n]),'decompiled_c_sha256':sha(c.encode()),'decompiled_c':c})
 p={'schema':'corolla-h-diagnostic-residue-evidence-v1','software_id':'8965H1202000','image':{'path':str(RAW.relative_to(ROOT)),'codeflash_size':len(raw),'codeflash_sha256':sha(raw)},'source_corpus':{'path':str(SRC.relative_to(ROOT)),'sha256':sha(SRC.read_bytes()),'boundary':'disposable H project seeded at diagnostic triage plus exact H WDBI table callback entries; only functions explicitly compacted here are promoted'},'functions':out,'function_count':len(out)}
 OUT.write_text(json.dumps(p,indent=2,sort_keys=True)+'\n');print(f'wrote {OUT}: {len(out)} functions')
if __name__=='__main__':main()
