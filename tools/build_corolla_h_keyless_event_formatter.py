#!/usr/bin/env python3
"""Build deterministic Corolla-H event-formatter role/bounds evidence for the keyless re-audit."""
from __future__ import annotations
import argparse,hashlib,json,struct
from pathlib import Path
from sienna_target import CODEFLASH as SIENNA_CODEFLASH
from corolla_h_constants import RAW_DUMP as H_RAW_DUMP
ROOT=Path(__file__).resolve().parents[1]
EV_DEFAULT=ROOT/'data/generated/corolla_8965H1202000_keyless_event_formatter_decompiler_evidence.json'
S_DEFAULT=SIENNA_CODEFLASH
H_DEFAULT=H_RAW_DUMP
F_DEFAULT=ROOT/'community/spanconstant/raw-20260821/span-corolla-2025.20260821-1511/dump_codeflash_00000000_00200000_20260821-152033.bin'
OUT_DEFAULT=ROOT/'data/generated/corolla_8965H1202000_keyless_event_formatter.json'
ROLE_MAP=[
 (0x54910,'direct_call_target_00054910',0x50038,'unchecked-event-snapshot-formatter'),
 (0x549FA,'direct_call_target_000549fa',0x50122,'two-bank-event-snapshot-wrapper'),
 (0x54A7E,'direct_call_target_00054a7e',0x501A6,'bounded-event-detail-formatter-sibling'),
]
SUPPORT=[0x5031A,0x50D10,0x87384]
def sha(b:bytes)->str:return hashlib.sha256(b).hexdigest()
def u16(b:bytes,a:int)->int:return struct.unpack_from('<H',b,a)[0]
def bounds(img:bytes,desc_base:int,count:int,event_base:int)->dict:
 rows=[]
 for i in range(count):
  a=desc_base+i*0x18; rows.append({'index':i,'mask':u16(img,a+0x14),'length':img[a+0x16]})
 events=[]
 for i in range(0x40):
  a=event_base+i*8; eid=struct.unpack_from('<h',img,a)[0]; mask=u16(img,a+2)
  if not mask: continue
  selected=[r for r in rows if r['mask'] & mask]
  out=3+sum(3+r['length'] for r in selected)
  events.append({'slot':i,'event_id':eid,'mask':mask,'selected_count':len(selected),'payload_length_sum':sum(r['length'] for r in selected),'output_length':out})
 maxrow=max(events,key=lambda x:x['output_length'])
 return {'descriptor_base':f'0x{desc_base:08X}','descriptor_count':count,'event_map_base':f'0x{event_base:08X}','event_map_slots':0x40,'max_one_bank':maxrow['output_length'],'max_event_id':maxrow['event_id'],'max_event_mask':maxrow['mask'],'max_selected_count':maxrow['selected_count'],'conservative_two_bank_max':2*maxrow['output_length'],'staging_capacity':0x300,'headroom':0x300-2*maxrow['output_length']}
def main()->None:
 ap=argparse.ArgumentParser(description=__doc__); ap.add_argument('--evidence',type=Path,default=EV_DEFAULT); ap.add_argument('--sienna',type=Path,default=S_DEFAULT); ap.add_argument('--h',type=Path,default=H_DEFAULT); ap.add_argument('--f',type=Path,default=F_DEFAULT); ap.add_argument('--out',type=Path,default=OUT_DEFAULT); args=ap.parse_args()
 ev=json.loads(args.evidence.read_text()); S=args.sienna.read_bytes()[:0x100000]; H=args.h.read_bytes()[:0x100000]; F=args.f.read_bytes()[:0x100000]
 by={int(x['entry'],16):x for x in ev['functions']}; need={x[2] for x in ROLE_MAP}|set(SUPPORT)
 if not need <= set(by): raise SystemExit(f'missing H evidence: {sorted(need-set(by))}')
 roles=[]
 for ref,name,target,role in ROLE_MAP:
  roles.append({'reference_entry':f'0x{ref:08X}','reference_name':name,'target_entry':f'0x{target:08X}','role':role,'classification':'target-native-role-recovered'})
 sb=bounds(S,0x2A504,0x4B,0x2AD10); hb=bounds(H,0x29F1C,0x4E,0x2A770); fb=bounds(F,0x29F1C,0x4E,0x2A770)
 payload={
  'schema':'corolla-h-keyless-event-formatter-v1','software_id':'8965H1202000',
  'images':{'sienna_sha256':sha(S),'h_sha256':sha(H),'f_sha256':sha(F)},
  'evidence':{'decompiler_evidence':str(args.evidence.resolve().relative_to(ROOT)),'decompiler_evidence_sha256':sha(args.evidence.read_bytes())},
  'role_closure':roles,'role_closure_count':len(roles),'target_evidence_entries':[f'0x{x:08X}' for x in sorted(need)],
  'supporting_target_entries':[f'0x{x:08X}' for x in SUPPORT],
  'bounds':{'sienna':sb,'corolla_h':hb,'corolla_f':fb},
  'h_f_equivalence':{
   'formatter':H[0x50038:0x50038+234]==F[0x50038:0x50038+234],
   'wrapper':H[0x50122:0x50122+90]==F[0x50122:0x50122+90],
   'bounded_sibling':H[0x501A6:0x501A6+228]==F[0x501A6:0x501A6+228],
   'ab_worker':H[0x87384:0x87384+364]==F[0x87384:0x87384+364],
   'descriptor_table':H[0x29F1C:0x29F1C+0x4E*0x18]==F[0x29F1C:0x29F1C+0x4E*0x18],
   'event_map':H[0x2A770:0x2A970]==F[0x2A770:0x2A970],
  },
  'static_conclusion':{
   'tracked_images_overflow':False,
   'configuration_dependent_safety':True,
   'structural_in_loop_capacity_check':False,
   'boundary':'Current S/H/F event masks bound reachable output inside the 0x300 staging area. The inner formatter itself has no capacity check, so this is a portability-sensitive configuration bound, not a structural memory-safety proof and not a global static-attack absence claim.'
  }
 }
 args.out.parent.mkdir(parents=True,exist_ok=True); args.out.write_text(json.dumps(payload,indent=2,sort_keys=True)+'\n'); print(json.dumps({'role_closure_count':len(roles),'sienna':sb,'corolla_h':hb,'corolla_f':fb},indent=2))
if __name__=='__main__':main()
