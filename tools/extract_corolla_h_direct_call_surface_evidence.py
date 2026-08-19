#!/usr/bin/env python3
"""Compact the clean H structural corpus into raw-bound direct-call closure evidence."""
from __future__ import annotations
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
RAW=ROOT/'community/albinoelephant/raw-20260818/albinoelephant-corolla-2023.20260814-0023/dump_codeflash_00000000_00200000_20260814-025814.bin'
SRC=ROOT/'build/h_clean_function_structural_fingerprints.jsonl'
OUT=ROOT/'data/generated/corolla_8965H1202000_direct_call_surface_evidence.json'
def sha(b):return hashlib.sha256(b).hexdigest()
def main():
 raw=RAW.read_bytes()[:0x100000];rows=[]
 for l in SRC.read_text().splitlines():
  r=json.loads(l)
  if r.get('record')!='function-structural-fingerprint':continue
  a=int(r['entry_addr'],16);n=int(r['body_size']);lens=[int(x) for x in r['instruction_lengths']]
  if sum(lens)!=n:raise SystemExit(f'non-contiguous fingerprint body at {a:#x}')
  rows.append({'entry':f'0x{a:08X}','body_size':n,'body_sha256':sha(raw[a:a+n]),'instruction_count':int(r['instruction_count']),'direct_call_targets':r.get('direct_call_targets',[])})
 entries={int(r['entry'],16) for r in rows};edges=[(int(t,16),int(r['entry'],16)) for r in rows for t in r['direct_call_targets']];missing=sorted({t for t,_ in edges if t<=0xfffff and t not in entries})
 if missing:raise SystemExit(f'clean H literal-call graph is not closed: {[hex(x) for x in missing]}')
 p={'schema':'corolla-h-direct-call-surface-evidence-v1','software_id':'8965H1202000','image':{'path':str(RAW.relative_to(ROOT)),'codeflash_size':len(raw),'codeflash_sha256':sha(raw)},'source':{'path':str(SRC.relative_to(ROOT)),'sha256':sha(SRC.read_bytes()),'provenance':'fresh clean H CodeFlash import; ExportFunctionStructuralFingerprints.java before semantic seeding'},'functions':rows,'summary':{'function_count':len(rows),'instruction_count':sum(r['instruction_count'] for r in rows),'literal_call_edge_count':len(edges),'unique_literal_call_target_count':len({t for t,_ in edges}),'missing_in_image_literal_call_targets':[],'closed':True}}
 OUT.write_text(json.dumps(p,indent=2,sort_keys=True)+'\n');print(f'wrote {OUT}: {len(rows)} functions, {len(edges)} literal calls')
if __name__=='__main__':main()
