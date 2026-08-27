#!/usr/bin/env python3
"""Build the fixed high-page call-veneer bank diff for Corolla 8965H1202000."""
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path
from sienna_target import CODEFLASH as SIENNA_CODEFLASH
from corolla_h_constants import RAW_DUMP as H_RAW_DUMP

ROOT=Path(__file__).resolve().parents[1]
SRAW=SIENNA_CODEFLASH
HRAW=H_RAW_DUMP
OUT=ROOT/'data/generated/corolla_8965H1202000_veneer_bank.json'
START=0xFDE08; END=0xFE2A4; STRIDE=0x14
FILL=bytes.fromhex('4000400040004000')
# Canonical unresolved veneer-derived pairs. Names came from the canonical Sienna project;
# classification below is determined only from the raw fixed-slot bank.
PAIRS=[
 (0xFDEA8,0xB7AAE,'constant_veneer_target_000b7aae'),
 (0xFE074,0xB47F6,'constant_veneer_target_000b47f6'),
 (0xFE088,0xB482E,'constant_veneer_target_000b482e'),
 (0xFE0B0,0xB55E2,'constant_veneer_target_000b55e2'),
 (0xFE164,0xB7114,'constant_veneer_target_000b7114'),
 (0xFE1A0,0xB20CC,'constant_veneer_target_000b20cc'),
 (0xFE1DC,0xB20DC,'constant_veneer_target_000b20dc'),
 (0xFE1F0,0xB720A,'constant_veneer_target_000b720a'),
 (0xFE204,0xB7218,'constant_veneer_target_000b7218'),
 (0xFE218,0xB7226,'constant_veneer_target_000b7226'),
 (0xFE22C,0xB722C,'constant_veneer_target_000b722c'),
]
def sha(b): return hashlib.sha256(b).hexdigest()
def is_veneer(b,a):
 x=b[a:a+8]; return len(x)==8 and x[:2]==b'\x2c\x06' and x[6:8]==b'\x6c\x00'
def classify(b,a):
 x=b[a:a+8]
 if is_veneer(b,a): return {'kind':'veneer','target':f'0x{int.from_bytes(x[2:6],"little"):08X}','raw8':x.hex()}
 if x==FILL: return {'kind':'fill','target':None,'raw8':x.hex()}
 return {'kind':'other','target':None,'raw8':x.hex()}
def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--out',type=Path,default=OUT); a=ap.parse_args()
 S=SRAW.read_bytes(); H=HRAW.read_bytes()[:0x100000]
 if len(S)!=0x100000 or len(H)!=0x100000: raise ValueError('expected 1 MiB CodeFlash images')
 slots=[]; sv=set(); hv=set()
 for i,addr in enumerate(range(START,END+1,STRIDE)):
  s=classify(S,addr); h=classify(H,addr)
  if s['kind']=='veneer': sv.add(addr)
  if h['kind']=='veneer': hv.add(addr)
  slots.append({'slot_index':i,'address':f'0x{addr:08X}','sienna':s,'h':h})
 roles=[]; recens=[]; pairs=[]; target_evidence=set()
 for slot,slow,name in PAIRS:
  s=classify(S,slot); h=classify(H,slot)
  if s['kind']!='veneer' or int(s['target'],16)!=slow: raise ValueError(f'canonical pair drift at {slot:#x}')
  high_name=f'direct_call_target_{slot:08x}'
  if h['kind']=='veneer':
   ht=int(h['target'],16); status='preserved-slot'
   roles += [
    {'reference_entry':f'0x{slot:08X}','reference_name':high_name,'target_entry':f'0x{slot:08X}','role':f'fixed high-page veneer slot {slot:#x}'},
    {'reference_entry':f'0x{slow:08X}','reference_name':name,'target_entry':f'0x{ht:08X}','role':f'target selected by preserved veneer slot {slot:#x}'},
   ]
   target_evidence.update((slot,ht))
  else:
   ht=None; status='removed-slot'
   recens += [
    {'reference_entry':f'0x{slot:08X}','reference_name':high_name,'reason':f'H slot {slot:#x} is fill, not a veneer'},
    {'reference_entry':f'0x{slow:08X}','reference_name':name,'reason':f'canonical low target was named from removed veneer slot {slot:#x}; no one-to-one H role assigned'},
   ]
  pairs.append({'slot':f'0x{slot:08X}','sienna_target':f'0x{slow:08X}','h_target':None if ht is None else f'0x{ht:08X}','status':status,'h_raw8':h['raw8']})
 payload={
  'schema':'corolla-h-veneer-bank-v1','software_id':'8965H1202000',
  'images':{'sienna_sha256':sha(S),'h_sha256':sha(H)},
  'bank':{'start':f'0x{START:08X}','end':f'0x{END:08X}','stride':STRIDE,'slot_count':len(slots),'slots':slots,
          'sienna_veneer_count':len(sv),'h_veneer_count':len(hv),'common_veneer_slots':len(sv&hv),
          'removed_slots':[f'0x{x:08X}' for x in sorted(sv-hv)],'added_slots':[f'0x{x:08X}' for x in sorted(hv-sv)]},
  'unresolved_pair_census':pairs,
  'role_closure':roles,'role_closure_count':len(roles),
  'surface_recensus':recens,'surface_recensus_count':len(recens),
  'target_evidence_entries':[f'0x{x:08X}' for x in sorted(target_evidence)],
  'static_conclusion':{
   'preserved_unresolved_pairs':sum(p['status']=='preserved-slot' for p in pairs),
   'removed_unresolved_pairs':sum(p['status']=='removed-slot' for p in pairs),
   'boundary':'A preserved fixed veneer slot proves the H call-slot role and its H low target. A removed slot proves only removal of that canonical veneer-derived role; it does not prove the old low-level operation is absent elsewhere in H.'
  }
 }
 a.out.write_text(json.dumps(payload,indent=2,sort_keys=True)+'\n'); print('wrote',a.out)
if __name__=='__main__': main()
