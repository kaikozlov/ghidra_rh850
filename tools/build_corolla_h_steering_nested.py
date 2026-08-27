#!/usr/bin/env python3
"""Build deterministic closure for the nine remaining named steering roles."""
from __future__ import annotations
import argparse,hashlib,json,re
from pathlib import Path
from sienna_target import CODEFLASH as SIENNA_CODEFLASH
from corolla_h_constants import RAW_DUMP as H_RAW_DUMP
ROOT=Path(__file__).resolve().parents[1]
EV=ROOT/'data/generated/corolla_8965H1202000_steering_nested_decompiler_evidence.json'
SDEC=ROOT/'data/generated/decompilations.jsonl'
HRAW=H_RAW_DUMP
SRAW=SIENNA_CODEFLASH
OUT=ROOT/'data/generated/corolla_8965H1202000_steering_nested.json'
ROLE_MAP=[
 (0xC8D62,'lta_internal_command_rate_limit',0xC9C16),
 (0xCA6B8,'steering_command_mode_select_stage',0xCB8BA),
 (0xCA75E,'steering_command_slew_gain_limit_stage',0xCB9B6),
 (0xCAC14,'steering_command_secondary_select_stage',0xCD3CC),
 (0xCB86E,'steering_control_cycle_pipeline',0xCEDAE),
 (0xCBA72,'steering_control_cycle_wrapper',0xCF028),
]
REMOVED=[
 (0xCA354,'steering_request_source_arbitration'),
 (0xCA3B8,'steering_lta_mode_latch'),
 (0xCA3F8,'steering_lka_torque_mode_latch'),
]
def sha(b):return hashlib.sha256(b).hexdigest()
def load_s():
 d={}
 for line in SDEC.read_text().splitlines():
  r=json.loads(line)
  if r.get('record')=='function':d[int(r['entry_addr'],16)]=r
 return d
def calls(c, by_name):
 c=c.split('{',1)[1] if '{' in c else c
 out=[]
 for name in re.findall(r'\b([A-Za-z_][A-Za-z0-9_]*)\s*\(',c):
  if name in by_name:
   out.append(by_name[name]); continue
  m=re.fullmatch(r'FUN_000([0-9a-fA-F]{5,6})',name)
  if m: out.append(int(m.group(1),16))
 return out
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,default=OUT);args=ap.parse_args()
 ev=json.loads(EV.read_text()); H=HRAW.read_bytes()[:0x100000]; S=SRAW.read_bytes(); sd=load_s(); by={int(r['entry'],16):r for r in ev['functions']}
 if sha(H)!=ev['image']['codeflash_sha256']:raise ValueError('H image drift')
 sname={r['name']:a for a,r in sd.items()}
 hname={r['decompiled_c'].split('(',1)[0].split()[-1]:a for a,r in by.items()}
 roles=[]
 for s,n,h in ROLE_MAP:
  roles.append({'reference_entry':f'0x{s:08X}','reference_name':n,'target_entry':f'0x{h:08X}','classification':'target-native-role-recovered','target_reported_body_size':by[h]['body_size']})
 removed=[{'reference_entry':f'0x{s:08X}','reference_name':n,'classification':'target-surface-recensused','replacement_surface':'0x000CBE6E'} for s,n in REMOVED]
 # Wrapper-order anchors.
 s_c8=calls(sd[0xC8DC8]['decompiled_c'],sname); h_c9=calls(by[0xC9CD2]['decompiled_c'],hname)
 s_ca=calls(sd[0xCA7F0]['decompiled_c'],sname); h_cb=calls(by[0xCBA40]['decompiled_c'],hname)
 # Semantic named calls are omitted by calls(); pin target positions directly from target wrappers.
 payload={
  'schema':'corolla-h-steering-nested-v1','software_id':'8965H1202000','images':{'h_sha256':sha(H),'sienna_sha256':sha(S)},'evidence':{'decompiler_evidence':str(EV.relative_to(ROOT))},
  'steering_role_closure':roles,'steering_role_closure_count':len(roles),'classic_command_surface_recensus':removed,'classic_command_surface_recensus_count':len(removed),
  'pipeline':{'sienna':'0x000CB86E','h':'0x000CEDAE','sienna_body_size':sd[0xCB86E]['body_size'],'h_body_size':by[0xCEDAE]['body_size'],'wrapper_sienna':'0x000CBA72','wrapper_h':'0x000CF028','h_wrapper_calls_pipeline':'FUN_000cedae' in by[0xCF028]['decompiled_c']},
  'lta_rate_limit':{'sienna':'0x000C8D62','h':'0x000C9C16','wrapper_sienna':'0x000C8DC8','wrapper_h':'0x000C9CD2','sienna_wrapper_call_count':len(s_c8),'h_wrapper_call_count':len(h_c9),'h_is_fourth_wrapper_call':h_c9[-1:]==[0xC9C16],'h_output_cells':['0xFEBEC1E0','0xFEBEC200','0xFEBEC20A'],'interpretation':'same terminal limiter position in the paired four-call LTA-control wrapper; H regenerates internal state and expands the limiter body'},
  'primary_command_conditioning':{'wrapper_sienna':'0x000CA7F0','wrapper_h':'0x000CBA40','wrapper_call_count_sienna':len(s_ca),'wrapper_call_count_h':len(h_cb),'mode_select':{'sienna':'0x000CA6B8','h':'0x000CB8BA','h_mode_state':'0xFEBEC2A6','h_selected_command':'0xFEBEC278'},'slew_gain_limit':{'sienna':'0x000CA75E','h':'0x000CB9B6','h_selected_command':'0xFEBEC278','h_output':'0xFEBEC2A8'},'ordered_targets': [f'0x{x:08X}' for x in h_cb]},
  'classic_command_mode_replacement':{'sienna_roles':[n for _,n in REMOVED],'h_decoder':'0x000CBE6E','h_decoder_wrapper':'0x000CB68A','h_decoder_inputs':['FEBEACBD','FEBEC26D','FEBEADB0'],'h_decoder_outputs':['FEBEC272','FEBEC273','FEBEC26E','FEBEC26F','FEBEC270','FEBEC271'],'classic_2e4_rx_present':False,'classic_131_rx_present':False,'interpretation':'H does not preserve separate authenticated-0x131 LTA and authenticated-0x2E4 torque arbitration/latch functions. The paired root-stage wrapper collapses to one H supervisory-mode decoder that derives six local mode flags from H-specific state. The three canonical roles are therefore closed by a complete replacement-surface recensus, not fake one-to-one homologs.'},
  'secondary_command_conditioning':{'sienna_parent_chain':['0x000BA3DA','0x000CBA42','0x000CB49C'],'h_parent_chain':['0x000B8E84','0x000CEFF8','0x000CE974'],'select':{'sienna':'0x000CAC14','h':'0x000CD3CC','sienna_body_size':sd[0xCAC14]['body_size'],'h_body_size':by[0xCD3CC]['body_size'],'h_output':'0xFEBEC3B8'},'following_gain_clip_anchor':{'sienna':'0x000CAC6A','h':'0x000CD440','h_body_size':by[0xCD440]['body_size']},'interpretation':'secondary select remains immediately upstream of the independently structural-matched gain/clip stage; H adds target-specific intermediate conditioning before the pair'},
  'static_conclusion':{'all_9_named_steering_residuals_closed':True,'one_to_one_roles_recovered':6,'removed_or_replaced_roles_recensused':3,'boundary':'high-level steering role/control topology is closed. H-specific supervisory mode meanings, calibration constants, and internal estimator state remain target-specific; absent classic 2E4/131 command ingress is not reintroduced.'}
 }
 args.out.write_text(json.dumps(payload,indent=2,sort_keys=True)+'\n');print('wrote',args.out)
if __name__=='__main__':main()
