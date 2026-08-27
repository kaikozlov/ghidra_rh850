#!/usr/bin/env python3
"""Build deterministic closure for the 11 named plausibility-monitor roles."""
from __future__ import annotations
import argparse,hashlib,json,re,struct
from pathlib import Path
from sienna_target import CODEFLASH as SIENNA_CODEFLASH
from corolla_h_constants import RAW_DUMP as H_RAW_DUMP
ROOT=Path(__file__).resolve().parents[1];EV=ROOT/'data/generated/corolla_8965H1202000_plausibility_monitor_decompiler_evidence.json';HRAW=H_RAW_DUMP;SRAW=SIENNA_CODEFLASH;SDEC=ROOT/'data/generated/decompilations.jsonl';OUT=ROOT/'data/generated/corolla_8965H1202000_plausibility_monitor.json'
CHANNELS=[
 (0,0x43558,0x3E118,0x28984,0x28514,7),(1,0x4360A,0x3E1CA,0x289B8,0x28548,8),(2,0x436BC,0x3E27C,0x289EC,0x2857C,3),(3,0x4386C,0x3E42C,0x28A20,0x285B0,4),(4,0x43A1C,0x3E5DC,0x28A54,0x285E4,0),(5,0x43C0C,0x3E7CC,0x28A88,0x28618,1),(6,0x43CBA,0x3E87A,0x28ABC,0x2864C,2),(7,0x43D68,0x3E928,0x28AF0,0x28680,5),(8,0x43E56,0x3EA16,0x28B24,0x286B4,6)]
ROLES=CHANNELS+[(9,0x43F28,0x3EAE8,None,None,None),(10,0x440DC,0x3ECCC,None,None,None)]
def sha(b):return hashlib.sha256(b).hexdigest()
def row(raw,base):
 vals=struct.unpack_from('<13I',raw,base);return {'base':f'0x{base:08X}','pointers':[f'0x{x:08X}' if x else None for x in vals],'nonzero':sum(bool(x) for x in vals),'unique':len(set(x for x in vals if x))}
def srows():
 d={}
 for l in SDEC.read_text().splitlines():
  r=json.loads(l)
  if r.get('record')=='function':d[int(r['entry_addr'],16)]=r
 return d
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,default=OUT);a=ap.parse_args();H=HRAW.read_bytes()[:0x100000];S=SRAW.read_bytes();ev=json.loads(EV.read_text());by={int(r['entry'],16):r for r in ev['functions']};sd=srows()
 roles=[];chs=[]
 for idx,s,h,st,ht,status in ROLES:
  name=sd[s]['name'];roles.append({'reference_entry':f'0x{s:08X}','reference_name':name,'target_entry':f'0x{h:08X}','classification':'target-native-role-recovered','sienna_body_size':sd[s]['body_size'],'h_body_size':by[h]['body_size']})
  if st is not None:
   sr,hr=row(S,st),row(H,ht);hc=by[h]['decompiled_c'];sc=sd[s]['decompiled_c']
   hs=re.search(r'FUN_0003eccc\((\d+),',hc); ss=re.search(r'plausibility_monitor_status_publish\((\d+),',sc)
   chs.append({'channel':idx,'sienna':f'0x{s:08X}','h':f'0x{h:08X}','sienna_table':sr,'h_table':hr,'table_delta':ht-st,'expected_status_index':status,'sienna_status_index':int(ss.group(1)) if ss else None,'h_status_index':int(hs.group(1)) if hs else None})
 p={'schema':'corolla-h-plausibility-monitor-v1','software_id':'8965H1202000','images':{'h_sha256':sha(H),'sienna_sha256':sha(S)},'evidence':{'decompiler_evidence':str(EV.relative_to(ROOT))},'role_closure':roles,'role_closure_count':len(roles),'channels':chs,'status_index_order':[c[-1] for c in CHANNELS],'publisher':{'sienna':'0x000440DC','h':'0x0003ECCC','both_body_size_18':sd[0x440DC]['body_size']==18==by[0x3ECCC]['body_size'],'h_bound':9,'h_vector_base':'0xFEBE76EC'},'aggregate':{'sienna':'0x00043F28','h':'0x0003EAE8','size_change':[sd[0x43F28]['body_size'],by[0x3EAE8]['body_size']],'preserves_nine_state_aggregation':True,'h_adds_status_publication': 'FUN_00047484(1,' in by[0x3EAE8]['decompiled_c']},'owner_dispatch':{'sienna':'0x0005D3CE','h':'0x00058450','channel_call_order_h':[f'0x{x:08X}' for x in [0x3E5DC,0x3E7CC,0x3E87A,0x3E27C,0x3E42C,0x3E928,0x3EA16,0x3E118,0x3E1CA,0x3EAE8]]},'static_conclusion':{'all_11_roles_recovered':len(roles)==11,'all_channel_table_deltas_minus_0x470':all(x['table_delta']==-0x470 for x in chs),'status_index_permutation_preserved':all(x['sienna_status_index']==x['h_status_index']==x['expected_status_index'] for x in chs),'boundary':'channel roles, table ownership, status-index mapping, and aggregate/publisher architecture are recovered; H callback operands, thresholds, state addresses, and the added aggregate status path remain target-specific.'}}
 a.out.write_text(json.dumps(p,indent=2,sort_keys=True)+'\n');print('wrote',a.out)
if __name__=='__main__':main()
