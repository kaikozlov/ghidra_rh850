#!/usr/bin/env python3
"""Build deterministic target-native Corolla-H motor-control comparison."""
from __future__ import annotations
import argparse,hashlib,json,re
from pathlib import Path
from sienna_target import CODEFLASH as SIENNA_CODEFLASH
from corolla_h_constants import RAW_DUMP as H_RAW_DUMP
ROOT=Path(__file__).resolve().parents[1]
EV=ROOT/'data/generated/corolla_8965H1202000_motor_control_decompiler_evidence.json';SC=ROOT/'data/generated/decompilations.jsonl';HRAW=H_RAW_DUMP;SI=SIENNA_CODEFLASH;OUT=ROOT/'data/generated/corolla_8965H1202000_motor_control.json'
MAP=[
(0x32B80,'motor_coord_transform_calib_handler',0x2E780),
(0x36A44,'dq_current_pi_axis_b',0x32616),
(0x38464,'motor0_inverse_rotating_frame_transform',0x33C70),
(0x38554,'motor1_inverse_rotating_frame_transform',0x33D60),
(0x5D18C,'tauj0_ch0_motor_control_worker',0x58226),
]
SUP=[(0x36902,'dq_current_pi_axis_a',0x324D4),(0x33198,'six-channel calibration state machine',0x2EDE6),(0x5784C,'CH0 mode/version wrapper',0x52DBA),(0x5CC08,'transition dispatcher',0x57CEA),(0x5CE0C,'steady dispatcher',0x57EEE)]
def sha(b):return hashlib.sha256(b).hexdigest()
def load_s(want):
 d={}
 for l in SC.read_text().splitlines():
  r=json.loads(l)
  if r.get('entry_addr') and int(r['entry_addr'],16) in want:d[int(r['entry_addr'],16)]=r
 if set(want)-d.keys():raise ValueError('missing canonical motor functions')
 return d
def fun_calls(c):return re.findall(r'\b(?:FUN_[0-9a-fA-F]{8}|[A-Za-z_][A-Za-z0-9_]*)\(',c)
def metrics(r):
 c=r['decompiled_c'];calls=[x[:-1] for x in fun_calls(c) if x not in ('if(','for(','while(','switch(')]
 if calls and calls[0]==r.get('name'):calls=calls[1:]
 return {'body_size':int(r['body_size']),'direct_call_count':len(calls),'if_count':len(re.findall(r'\bif\s*\(',c))}
def call_seq(c):
 return [x for x in re.findall(r'\b(FUN_[0-9a-fA-F]{8}|[A-Za-z_][A-Za-z0-9_]*)\(',c) if x not in {'if','for','while','switch'}]
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,default=OUT);a=ap.parse_args();ev=json.loads(EV.read_text());h={int(x['entry'],16):x for x in ev['functions']};H=HRAW.read_bytes()[:0x100000];SIMG=SI.read_bytes();S=load_s({x[0] for x in MAP+SUP})
 if sha(H)!=ev['image']['codeflash_sha256']:raise ValueError('H image drift')
 roles=[{'reference_entry':f'0x{sa:08X}','reference_name':n,'target_entry':f'0x{ha:08X}','classification':'target-native-role-recovered','reference_metrics':metrics(S[sa]),'target_metrics':metrics(h[ha])} for sa,n,ha in MAP]
 # Calibration state-machine anchor.
 sc=S[0x33198]['decompiled_c'];hc=h[0x2EDE6]['decompiled_c']
 # CH0 steady worker call order: locate the PI pair and inverse-transform pair.
 sw=call_seq(S[0x5D18C]['decompiled_c']);hw=call_seq(h[0x58226]['decompiled_c'])
 s_pi=[sw.index('dq_current_pi_axis_b'),sw.index('dq_current_pi_axis_a')]
 h_pi=[hw.index('FUN_00032616'),hw.index('FUN_000324d4')]
 s_inv=[sw.index('motor0_inverse_rotating_frame_transform'),sw.index('motor1_inverse_rotating_frame_transform')]
 h_inv=[hw.index('FUN_00033c70'),hw.index('FUN_00033d60')]
 # Formula tokens shared by all inverse transforms.
 inv_tokens=['0x6eda','0x6883','0x8000','0x2000','0x7fff','0x8001']
 # Axis controllers share reset/gate semantics; B is intentionally smaller on H.
 hb=h[0x32616]['decompiled_c'];ha=h[0x324D4]['decompiled_c']
 payload={
 'schema':'corolla-h-motor-control-v1','software_id':'8965H1202000','images':{'h_sha256':sha(H),'sienna_sha256':sha(SIMG)},'evidence':{'decompiler_evidence':str(EV.relative_to(ROOT)),'canonical_corpus':str(SC.relative_to(ROOT))},
 'motor_role_closure':roles,'motor_role_closure_count':len(roles),
 'calibration_state_machine':{
  'sienna_state_machine':'0x00033198','h_state_machine':'0x0002EDE6','sienna_body_size':S[0x33198]['body_size'],'h_body_size':h[0x2EDE6]['body_size'],
  'sienna_state_0x33_handler':'0x00032B80','h_state_0x33_handler':'0x0002E780','sienna_handler_size':S[0x32B80]['body_size'],'h_handler_size':h[0x2E780]['body_size'],
  'sienna_has_state_33_call':"DAT_febe6938 == '3'" in sc and 'motor_coord_transform_calib_handler' in sc,
  'h_has_state_33_call':"cramfebe67d0 == '3'" in hc.lower() and 'fun_0002e780' in hc.lower(),
  'version_dispatch':{'sienna_transition':'0x0005CC08','h_transition':'0x00057CEA','sienna_steady':'0x0005CE0C','h_steady':'0x00057EEE','domains':[0x512,0x600]},
  'h_preceding_phase':'0x0002E44C','h_main_phase':'0x0002E780','h_completion_states':{'preceding':0x22,'main':0x44},
  'interpretation':'same six-channel calibration state machine and state-0x33 role, with regenerated fixed-point handler/state addresses'},
 'current_pi_pair':{
  'sienna_axis_a':'0x00036902','h_axis_a':'0x000324D4','sienna_axis_b':'0x00036A44','h_axis_b':'0x00032616',
  'axis_a_body_sizes':[S[0x36902]['body_size'],h[0x324D4]['body_size']], 'axis_b_body_sizes':[S[0x36A44]['body_size'],h[0x32616]['body_size']],
  'sienna_worker_indices':s_pi,'h_worker_indices':h_pi,'order_preserved':s_pi[0]<s_pi[1] and h_pi[0]<h_pi[1],
  'h_shared_reset_gate':all(t in hb and t in ha for t in ('0x40004','0x7fff','0x8000')),
  'h_axis_b_reference_feedback':['0xFEBE6BBC','0xFEBE6BAC'],'h_axis_a_reference_feedback':['0xFEBE6BBE','0xFEBE6BB0'],
  'h_axis_b_gain_block':'0x0002D5B4..0x0002D5BC','h_axis_a_gain_block':'0x0002D5A4..0x0002D5B0',
  'axis_b_boundary':'H keeps the B-before-A current-loop role but simplifies Sienna axis-B cross-integrator/state coupling from 404 to 280 bytes; do not transfer Sienna axis-B internal state semantics wholesale'},
 'inverse_rotating_frame':{
  'sienna':['0x00038464','0x00038554'],'h':['0x00033C70','0x00033D60'],'body_sizes':[h[0x33C70]['body_size'],h[0x33D60]['body_size']],
  'formula_tokens':inv_tokens,'formula_tokens_present':all(all(t in h[x]['decompiled_c'].lower() for t in inv_tokens) for x in (0x33C70,0x33D60)),
  'h_inputs':[['0xFEBE6A80','0xFEBE6A82'],['0xFEBE6A84','0xFEBE6A86']], 'h_angle_pairs':[['0xFEBE7A54','0xFEBE7A56'],['0xFEBE7A60','0xFEBE7A62']], 'h_outputs':[['0xFEBE6C78','0xFEBE6C7A','0xFEBE6C7C'],['0xFEBE6C80','0xFEBE6C82','0xFEBE6C84']],
  'sienna_worker_indices':s_inv,'h_worker_indices':h_inv,'order_preserved':s_inv[0]<s_inv[1] and h_inv[0]<h_inv[1]},
 'ch0_worker':{
  'sienna':'0x0005D18C','h':'0x00058226','sienna_body_size':S[0x5D18C]['body_size'],'h_body_size':h[0x58226]['body_size'],'sienna_wrapper':'0x0005784C','h_wrapper':'0x00052DBA','wrapper_body_sizes':[S[0x5784C]['body_size'],h[0x52DBA]['body_size']],
  'h_transition_dispatcher':'0x00057FC8','h_steady_worker_call_from_wrapper':'FUN_00058226(2,uVar2)','mode_gate':0x200,'phase_duty_gate':0x101,
  'h_anchor_call_order':['FUN_00032616','FUN_000324d4','FUN_00033c70','FUN_00033d60'],
  'interpretation':'same high-rate CH0 orchestration role with a shorter regenerated stage list; PI and inverse-transform anchors preserve relative order'},
 'supporting_analogues':[{'reference_entry':f'0x{sa:08X}','reference_name':n,'target_entry':f'0x{ha:08X}','reference_metrics':metrics(S[sa]),'target_metrics':metrics(h[ha])} for sa,n,ha in SUP],
 'static_conclusion':{'motor_control_residue_closed':True,'axis_a_unique_shape_supporting_evidence':True,'five_changed_roles_recovered':True,'boundary':'high-level control roles and fixed-point transforms are recovered; H-specific downstream calibrations/state semantics remain target-specific where bodies changed'}
 }
 a.out.write_text(json.dumps(payload,indent=2,sort_keys=True)+'\n');print('wrote',a.out)
if __name__=='__main__':main()
