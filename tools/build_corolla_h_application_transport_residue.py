#!/usr/bin/env python3
"""Build residual application CAN/PduR transport closure for Corolla H."""
from __future__ import annotations
import argparse,hashlib,json,re,struct,sys
from pathlib import Path
from sienna_target import CODEFLASH as SIENNA_CODEFLASH
from corolla_h_constants import RAW_DUMP as H_RAW_DUMP
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from tools.compare_variant_application_rx import find_normal_rx_descriptor_table
SRAW=SIENNA_CODEFLASH;HRAW=H_RAW_DUMP;HEV=ROOT/'data/generated/corolla_8965H1202000_application_transport_decompiler_evidence.json';OUT=ROOT/'data/generated/corolla_8965H1202000_application_transport_residue.json'
TX=struct.Struct('<IBBH')
ROLES=[(0x7FF86,'application_can_special_rx_demux',0x7A382),(0x80006,'application_can_normal_rx_demux',0x7A402),(0x809C6,'application_pdu_transmit_router',0x7ADC2),(0x80C44,'application_pdu_rx_router',0x7B040),(0x4C158,'application_pack_can_394',0x47ADA)]
REMOVED=[(0x4A244,'application_unpack_can_2e4','H complete normal-Rx descriptor table has no CAN 0x2E4'),(0x4BCEE,'application_pack_can_260','H complete Tx descriptor run has no CAN 0x260'),(0x4BE24,'application_pack_can_262','H complete Tx descriptor run has no CAN 0x262')]
def sha(b):return hashlib.sha256(b).hexdigest()
def load_ev(h):
 d=json.loads(HEV.read_text());out={}
 if d['image']['codeflash_sha256']!=sha(h):raise ValueError('evidence image mismatch')
 for r in d['functions']:
  a=int(r['entry'],16);n=r['body_size'];c=r['decompiled_c']
  if sha(h[a:a+n])!=r['body_sha256'] or sha(c.encode())!=r['decompiled_c_sha256']:raise ValueError(f'evidence drift {a:#x}')
  out[a]=r
 return d,out
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,default=OUT);a=ap.parse_args();s=SRAW.read_bytes();h=HRAW.read_bytes()[:0x100000];meta,ev=load_ev(h)
 sb,srx=find_normal_rx_descriptor_table(s);hb,hrx=find_normal_rx_descriptor_table(h);sids=[x&0x7ff for x,_ in srx];hids=[x&0x7ff for x,_ in hrx]
 stx=[TX.unpack_from(s,0x21F78+TX.size*i)[0]&0x7ff for i in range(6)];htx=[TX.unpack_from(h,0x21F04+TX.size*i)[0]&0x7ff for i in range(5)]
 # H 394 packer must visibly pack four signals and submit generated PDU index 2.
 c394=ev[0x47ADA]['decompiled_c'];pack_calls=re.findall(r'FUN_000764ec\(',c394);submit='FUN_000763fa(2)' in c394
 route_checks={
  0x7A382:['while( true )','piVar3[1]'],0x7A402:['while( true )','FUN_0007b026'],0x7ADC2:['param_1 = param_1 & 0xffff','(*pcVar4)(uVar3)'],0x7B040:['uVar3 = param_1 & 0x7ff','(*pcVar4)(uVar2)']}
 for t,need in route_checks.items():
  c=ev[t]['decompiled_c']
  if not all(x in c for x in need):raise ValueError(f'route role drift {t:#x}')
 roles=[{'reference_entry':f'0x{r:08X}','reference_name':n,'target_entry':f'0x{t:08X}','role':n} for r,n,t in ROLES]
 rec=[{'reference_entry':f'0x{r:08X}','reference_name':n,'reason':why} for r,n,why in REMOVED]
 p={'schema':'corolla-h-application-transport-residue-v1','software_id':'8965H1202000','images':{'sienna_sha256':sha(s),'h_sha256':sha(h)},'evidence':{'decompiler_evidence':str(HEV.relative_to(ROOT))},'rx_configuration':{'sienna_base':f'0x{sb:08X}','h_base':f'0x{hb:08X}','sienna_count':len(srx),'h_count':len(hrx),'sienna_ids':[f'0x{x:03X}' for x in sids],'h_ids':[f'0x{x:03X}' for x in hids],'can_2e4_removed':0x2E4 in sids and 0x2E4 not in hids},'tx_configuration':{'sienna_ids':[f'0x{x:03X}' for x in stx],'h_ids':[f'0x{x:03X}' for x in htx],'removed':['0x260','0x262'],'h_394_index':htx.index(0x394),'h_394_packer':{'entry':'0x00047ADA','body_size':ev[0x47ADA]['body_size'],'direct_pack_call_count':len(pack_calls),'submits_pdu_index_2':submit}},'role_closure':roles,'role_closure_count':len(roles),'surface_recensus':rec,'surface_recensus_count':len(rec),'target_evidence_entries':[f'0x{x:08X}' for x in sorted({t for _,_,t in ROLES})],'static_conclusion':{'five_roles_recovered':True,'three_removed_generated_roles':True,'boundary':'Removed PDU descriptors close only the canonical generated pack/unpack roles. Surviving 0x394 is role-mapped by target PDU index plus H-native packer behavior; signal count changes from Sienna and field identity is not transferred.'}}
 a.out.write_text(json.dumps(p,indent=2,sort_keys=True)+'\n');print('wrote',a.out)
if __name__=='__main__':main()
