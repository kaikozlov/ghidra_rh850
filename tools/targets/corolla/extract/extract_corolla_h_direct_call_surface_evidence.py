#!/usr/bin/env python3
"""Bind the canonical H literal-call graph to its CodeFlash function ranges."""
from __future__ import annotations
from tools import REPO_ROOT
import hashlib,json
from tools.targets.corolla.support.corolla_h_constants import RAW_DUMP as H_RAW_DUMP
ROOT=REPO_ROOT
RAW=H_RAW_DUMP
SRC=ROOT/'data/targets/corolla-8965H1202000/function_structural_fingerprints.jsonl'
OUT=ROOT/'data/generated/corolla_8965H1202000_direct_call_surface_evidence.json'
def sha(b):return hashlib.sha256(b).hexdigest()
def main():
 raw=RAW.read_bytes()[:0x100000];rows=[];metadata=None
 for l in SRC.read_text().splitlines():
  r=json.loads(l)
  if r.get('record')=='metadata':
   metadata=r
   continue
  if r.get('record')!='function-structural-fingerprint':continue
  a=int(r['entry_addr'],16)
  if r['address_space']!='ram' or a>=len(raw):continue
  parts=[]
  for span in r['body_ranges']:
   lo=int(span['min'],16);hi=int(span['max'],16)+1
   if span['space']!='ram' or not 0<=lo<hi<=len(raw):
    raise SystemExit(f'function range outside H CodeFlash at {a:#x}')
   parts.append(raw[lo:hi])
  body=b''.join(parts)
  if len(body)!=r['body_size']:raise SystemExit(f'function range size mismatch at {a:#x}')
  rows.append({'entry':f'0x{a:08X}','body_size':len(body),'body_ranges':r['body_ranges'],'body_sha256':sha(body),'instruction_count':int(r['instruction_count']),'direct_call_targets':r['direct_call_targets']})
 if metadata is None or metadata['executable_sha256']!=sha(raw):
  raise SystemExit('H fingerprint/image identity mismatch')
 entries={int(r['entry'],16) for r in rows};edges=[(int(t,16),int(r['entry'],16)) for r in rows for t in r['direct_call_targets']];missing=sorted({t for t,_ in edges if t<len(raw) and t not in entries})
 if missing:raise SystemExit(f'canonical H literal-call graph is not closed: {[hex(x) for x in missing]}')
 p={'schema':'corolla-h-direct-call-surface-evidence-v2','software_id':'8965H1202000','image':{'path':str(RAW.relative_to(ROOT)),'codeflash_size':len(raw),'codeflash_sha256':sha(raw)},'source':{'path':str(SRC.relative_to(ROOT)),'sha256':sha(SRC.read_bytes()),'project':metadata},'functions':rows,'summary':{'function_count':len(rows),'instruction_count':sum(r['instruction_count'] for r in rows),'literal_call_edge_count':len(edges),'unique_literal_call_target_count':len({t for t,_ in edges}),'missing_in_image_literal_call_targets':[],'closed':True}}
 OUT.write_text(json.dumps(p,indent=2,sort_keys=True)+'\n');print(f'wrote {OUT}: {len(rows)} functions, {len(edges)} literal calls')
if __name__=='__main__':main()
