#!/usr/bin/env python3
"""Promote exact-F33 decompiler evidence needed by the static lateral contract."""
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path
REPO=Path(__file__).resolve().parents[1]
IMAGE=REPO/'community/kai/camry-2026/normalized/8965F3307000_CodeFlash.bin'
OUT=REPO/'data/generated/camry_8965F3307000_lateral_decompiler_evidence.json'
ENTRIES=[
  0x34C56,0x35A06,0x46994,0x47AE0,0x484D2,0x48684,0x4B59E,0x4BD46,0x4DB70,0x4DBBC,0x4E394,0x54244,0x564CE,0x58074,
  0x66062,0x6639C,0x66512,0xBCD66,0xCDA20,0xCCF0E,0xCCFB6,0xCDFF8,0xCE3AA,
  0xCEC8A,0xCED28,0xCEDA4,0xCEE20,0xCEE46,0xCEE80,0xCEF26,0xCEFFC,
]
IMAGE_SHA='42dce8efc42f6ae31718e7713fa2d26bb9191b4a82439778aee4d7afded9b0e7'

def sha(b:bytes)->str:return hashlib.sha256(b).hexdigest()
def main()->int:
 ap=argparse.ArgumentParser(description=__doc__); ap.add_argument('--corpus',type=Path,required=True); ap.add_argument('--out',type=Path,default=OUT); a=ap.parse_args()
 image=IMAGE.read_bytes()
 if len(image)!=0x100000 or sha(image)!=IMAGE_SHA: raise SystemExit('exact F33 image identity drift')
 rows={}; total=0
 for line in a.corpus.open(encoding='utf-8'):
  r=json.loads(line)
  if r.get('record')=='function':
   total+=1; rows[int(r['entry_addr'],16)]=r
 funcs=[]
 for entry in ENTRIES:
  r=rows.get(entry)
  if not r or not r.get('decompile_completed') or not r.get('decompiled_c'): raise SystemExit(f'missing complete decompile 0x{entry:X}')
  n=int(r['body_size']); body=image[entry:entry+n]; text=r['decompiled_c']
  funcs.append({'entry':f'0x{entry:08X}','body_size':n,'body_sha256':sha(body),'decompiled_c_sha256':sha(text.encode()),'decompiled_c':text})
 def refs(token:str):
  out=[]
  for entry,r in rows.items():
   text=r.get('decompiled_c','')
   if token in text:
    n=int(r['body_size']); out.append({'entry':f'0x{entry:08X}','body_size':n,'body_sha256':sha(image[entry:entry+n])})
  return sorted(out,key=lambda x:x['entry'])
 torque=refs('-0x5158'); qcur=refs('-0x50f2')
 obj={
  'schema':'camry-8965f3307000-lateral-decompiler-evidence-v1',
  'software_id':'8965F3307000',
  'image':{'path':str(IMAGE.relative_to(REPO)),'size':len(image),'sha256':IMAGE_SHA},
  'source_corpus':{'path':str(a.corpus),'sha256':sha(a.corpus.read_bytes()),'function_count':total,'boundary':'Disposable Ghidra corpus used to recover direct/fixed-GP references; every promoted function/reference row is independently body-hash-bound to the exact normalized image.'},
  'function_count':len(funcs),'functions':funcs,
  'fixed_gp_census':{
    'driver_torque_source':{'token':'gp-0x5158','entries':torque,'cooperative_c8_d1_intersection':[]},
    'q_current_source':{'token':'gp-0x50F2','entries':qcur,'cooperative_c8_d1_intersection':[]},
    'boundary':'Whole recovered-function-corpus textual census of direct/fixed-GP references. Computed aliases, value-set pointer recovery, and DMA/peripheral mutation are outside this negative proof.'
  },
 }
 a.out.parent.mkdir(parents=True,exist_ok=True); a.out.write_text(json.dumps(obj,indent=2,sort_keys=True)+'\n'); print(f'wrote {a.out}: {len(funcs)} functions, corpus={total}')
 return 0
if __name__=='__main__': raise SystemExit(main())
