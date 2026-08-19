#!/usr/bin/env python3
"""Build deterministic Sienna↔Corolla-H CAN/COM role and table comparison."""
from __future__ import annotations
import argparse,difflib,hashlib,json,re,struct
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
EVP=ROOT/'data/generated/corolla_8965H1202000_can_com_decompiler_evidence.json'
SCORP=ROOT/'data/generated/decompilations.jsonl'
HRAW=ROOT/'community/albinoelephant/raw-20260818/albinoelephant-corolla-2023.20260814-0023/dump_codeflash_00000000_00200000_20260814-025814.bin'
SIMG=ROOT/'firmware/RH850_P1M-E_CodeFlash.bin'
OUT=ROOT/'data/generated/corolla_8965H1202000_can_com.json'
MAP=[
(0x5D3CE,'autosar_com_rx_dispatch_group_b',0x58450),(0x5DB6E,'autosar_com_rx_dispatch_group_a',0x58BBC),(0x69DEC,'com_signal_deadline_monitor_c',0x6418C),(0x7C640,'application_com_rx_indication',0x76A3C),(0x7E30C,'application_pdur_tx_confirmation_router',0x78708),(0x7E5F2,'application_canif_get_tx_can_id',0x789EE),(0x7F002,'application_canif_tx_confirmation',0x793FE),(0x80992,'application_pdur_com_transmit',0x7AD8E),(0x84710,'application_rscfd_tx_confirmation_dispatch',0x7EB10)]
SUP=[0x809C6,0x80C44,0x7FF86,0x80006]
def sha(b):return hashlib.sha256(b).hexdigest()
def load_s(addrs):
 d={}
 for l in SCORP.read_text().splitlines():
  r=json.loads(l)
  if r.get('entry_addr') and int(r['entry_addr'],16) in addrs:d[int(r['entry_addr'],16)]=r
 if set(addrs)-d.keys():raise ValueError('missing canonical funcs')
 return d
def calls(c):return re.findall(r'\bFUN_[0-9a-fA-F]{8}\(',c)
def metrics(r):
 c=r['decompiled_c'];return {'body_size':int(r['body_size']),'fun_call_count':len(calls(c)),'if_count':len(re.findall(r'\bif\s*\(',c)),'loop_count':len(re.findall(r'\b(?:for|while|do)\b',c))}
def guards(c):
 o=[]
 for x in c.splitlines():
  x=x.strip()
  if x.startswith('if (') or x.startswith('else if ('):
   x=x.removeprefix('else ');x=re.sub(r'uVar\d+','uVar',x);x=re.sub(r'LAB_[0-9a-fA-F]+','LAB',x);o.append(x)
 return o
def gd(a,b):
 out=[]
 for op,i1,i2,j1,j2 in difflib.SequenceMatcher(a=a,b=b,autojunk=False).get_opcodes():
  if op!='equal':out.append({'opcode':op,'sienna':a[i1:i2],'h':b[j1:j2],'sienna_range':[i1,i2],'h_range':[j1,j2]})
 return out
def u32(b,a):return struct.unpack_from('<I',b,a)[0]
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,default=OUT);a=ap.parse_args()
 ev=json.loads(EVP.read_text());h={int(r['entry'],16):r for r in ev['functions']};S=load_s({x[0] for x in MAP}|set(SUP));H=HRAW.read_bytes()[:0x100000];SI=SIMG.read_bytes()
 if sha(H)!=ev['image']['codeflash_sha256']:raise ValueError('H hash drift')
 roles=[]
 for sa,n,ha in MAP:roles.append({'reference_entry':f'0x{sa:08X}','reference_name':n,'target_entry':f'0x{ha:08X}','classification':'target-native-role-recovered','reference_metrics':metrics(S[sa]),'target_metrics':metrics(h[ha])})
 gbS,gbH=guards(S[0x5D3CE]['decompiled_c']),guards(h[0x58450]['decompiled_c']);gaS,gaH=guards(S[0x5DB6E]['decompiled_c']),guards(h[0x58BBC]['decompiled_c'])
 # Table-slot proofs bind function role independently of address similarity.
 table=[
 {'role':'pdur_tx_confirmation','sienna_pointer_at':'0x00021980','sienna_target':'0x0007E30C','h_pointer_at':'0x0002192C','h_target':'0x00078708'},
 {'role':'canif_get_tx_can_id','sienna_pointer_at':'0x00021EDC','sienna_target':'0x0007E5F2','h_pointer_at':'0x00021E68','h_target':'0x000789EE'},
 {'role':'canif_tx_confirmation','sienna_pointer_at':'0x00021ED0','sienna_target':'0x0007F002','h_pointer_at':'0x00021E5C','h_target':'0x000793FE'},
 {'role':'com_rx_indication','sienna_pointer_at':'0x00021E28','sienna_target':'0x0007C640','h_pointer_at':'0x00021DB4','h_target':'0x00076A3C'},
 {'role':'pdu_transmit_router','sienna_pointer_at':'0x00021CE4','sienna_target':'0x000809C6','h_pointer_at':'0x00021C70','h_target':'0x0007ADC2'},
 {'role':'pdu_rx_router','sienna_pointer_at':'0x00021D04','sienna_target':'0x00080C44','h_pointer_at':'0x00021C90','h_target':'0x0007B040'},
 ]
 for r in table:
  if u32(SI,int(r['sienna_pointer_at'],16))!=int(r['sienna_target'],16) or u32(H,int(r['h_pointer_at'],16))!=int(r['h_target'],16):raise ValueError('table pointer drift '+r['role'])
 exact_deadline=SI[0x69DEC:0x69DEC+1182]==H[0x6418C:0x6418C+1182]
 payload={'schema':'corolla-h-can-com-v1','software_id':'8965H1202000','images':{'h_sha256':sha(H),'sienna_sha256':sha(SI)},'evidence':{'decompiler_evidence':str(EVP.relative_to(ROOT)),'canonical_corpus':str(SCORP.relative_to(ROOT))},'can_com_role_closure':roles,'can_com_role_closure_count':len(roles),'rx_dispatch_groups':{'group_b':{'sienna':'0x0005D3CE','h':'0x00058450','sienna_guard_count':len(gbS),'h_guard_count':len(gbH),'guard_diff':gd(gbS,gbH)},'group_a':{'sienna':'0x0005DB6E','h':'0x00058BBC','sienna_guard_count':len(gaS),'h_guard_count':len(gaH),'guard_diff':gd(gaS,gaH)},'boundary':'same generated mode-dispatch roles; changed PDU/unpacker populations remain target-specific'},'deadline_monitor_c':{'sienna':'0x00069DEC','h':'0x0006418C','exact_body_equal':exact_deadline,'h_exact_body_occurrences':['0x0006418C','0x000CF27E'],'active_h_caller':'0x0003E118','active_h_caller_invokes_6418c':'FUN_0006418c(' in h[0x3E118]['decompiled_c'],'boundary':'body identity alone is ambiguous; active role is bound by target-native caller census'},'configuration_pointer_proofs':table,'supporting_route_chain':{'normal_rx_demux':{'sienna':'0x00080006','h':'0x0007A402'},'special_rx_demux':{'sienna':'0x0007FF86','h':'0x0007A382'},'pdu_rx_router':{'sienna':'0x00080C44','h':'0x0007B040'},'pdu_transmit_router':{'sienna':'0x000809C6','h':'0x0007ADC2'},'h_normal_rx_terminal_call':'FUN_0007b026 -> pointer 0x21C90 -> 0x7B040','h_com_rx_config_target':'0x21DB4 -> 0x76A3C'},'static_conclusion':{'can_com_residue_closed':True,'role_count':9,'transport_configuration_regenerated':True,'boundary':'roles/configured callbacks are recovered; individual PDU membership remains owned by the separate exact H COM topology report'}}
 a.out.write_text(json.dumps(payload,indent=2,sort_keys=True)+'\n');print('wrote',a.out)
if __name__=='__main__':main()
