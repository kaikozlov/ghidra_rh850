#!/usr/bin/env python3
"""Build an evidence-graded Sienna-vs-H steering-supervisor stage ledger.

The direct-call sequences are globally order-aligned with structural similarity.
This is a navigation/classification aid, not semantic identity proof. A matched
pair is promoted only when the separately generated whole-image artifact proves a
unique complete instruction-shape match. H-only/Sienna-only rows mean unpaired
in this ordered supervisor alignment, not globally absent from the other image.
"""
from __future__ import annotations
import argparse, difflib, hashlib, json, re
from pathlib import Path

REPO=Path(__file__).resolve().parents[1]
GAP=-0.22

H_ROLE={
0xC9466:("calibration_interpolation","two mode-selected interpolation lookups from ADE8-derived operating state"),
0xC5DEC:("calibration_interpolation","mode-indexed interpolation from ADE8-derived operating state"),
0xC803C:("supervisor_plausibility","absolute/threshold debounce over steering snapshot state"),
0xC80C4:("supervisor_plausibility","AE20/AE22 multi-window plausibility predicate; AE20 is not clamp input"),
0xC813A:("supervisor_validity","sentinel/validity aggregation over AE0A..AE10 and supervisor flags"),
0xC7E88:("supervisor_history_delta","history/delta comparison with mode-dependent limits"),
0xC7F40:("supervisor_mode_latch","mode fallback/latch update"),
0xC8526:("supervisor_consistency","paired scaled-state consistency/rate check"),
0xC8370:("supervisor_mode_scaling","mode-dependent scale initialization and state update"),
0xC87FC:("supervisor_rate_estimation","feedback delta/history/rate estimator"),
0xC88EE:("supervisor_delta_saturation","snapshot delta with signed saturation"),
0xC8926:("supervisor_rate_estimation","speed-normalized rate and bounded state update"),
0xC89D2:("b6_mode_table","B6-derived two-bit mode/table selection with debounce/ramp state"),
0xC8B02:("supervisor_correction","bounded error/offset correction from supervisor state"),
0xC7BE8:("supervisor_activation_fault","activation debounce with event/fault path"),
0xC7C70:("b6_validity_gate","B6 validity plus local validity gate"),
0xC7C94:("supervisor_fault_monitor","sign/plausibility monitor with event/fault path"),
0xC7D6A:("supervisor_fault_monitor","stability/debounce monitor with event/fault path"),
0xC7DEE:("supervisor_fault_monitor","delta monitor with event/fault path"),
0xC8652:("supervisor_mode_latch","mode-change/status latch update"),
0xC9ED0:("composite_wrapper","three-stage local postprocessing wrapper"),
0xC2296:("h_motion_state_estimator","multi-input H-only motion/state arbitration block"),
0xC265C:("h_motion_state_estimator","kinematic/feedback compensation and bounded interpolation block"),
0xC432E:("h_motion_state_estimator","paired state-update wrapper"),
0xC35BC:("h_dual_channel_plausibility","channel-A statistical/window plausibility estimator"),
0xC37AC:("h_dual_channel_plausibility","channel-B mirror statistical/window plausibility estimator"),
0xC399C:("h_dual_channel_plausibility","channel-A window/status classifier"),
0xC3A2E:("h_dual_channel_plausibility","channel-B window/status classifier"),
0xC3AC8:("h_dual_channel_plausibility","dual-channel consistency/debounce state"),
0xC3BD4:("h_dual_channel_plausibility","speed/state threshold fault latch"),
0xC3526:("composite_wrapper","five-stage H-only estimation subpipeline wrapper"),
0xC3C3C:("h_dual_channel_plausibility","combined channel-health/status arbitration"),
0xC3DC6:("h_dual_channel_plausibility","combined channel-health finalizer"),
0xC4536:("h_geometry_estimation","two-channel mean plus residual/offset construction"),
0xC4696:("h_geometry_estimation","bounded multi-channel residual/geometry computation"),
0xCDCFC:("composite_wrapper","two-stage late postprocessing wrapper"),
0xCCF58:("b6_status_export","B6-validity-gated mode/status propagation"),
0xCD01C:("status_postprocess","multi-source status/calibration postprocessing wrapper"),
0xC5FCC:("calibration_postprocess","ADE8-dependent calibrated postprocessing wrapper"),
0xCD15A:("calibration_interpolation","two mode-selected interpolation lookups from ADE8-derived operating state"),
}
S_REMOVED_ROLE={
0xC4CE0:("sienna_command_shaping","ADF6-indexed calibration lookup"),
0xC4E12:("sienna_command_shaping","ADF6-indexed calibration lookup"),
0xC4F62:("sienna_command_shaping","ADF6-indexed calibration lookup"),
0xC5100:("sienna_command_shaping","ADF6-indexed calibration lookup"),
0xC5050:("sienna_command_shaping","AE4A-indexed paired calibration lookup"),
0xC4E2C:("sienna_command_shaping","AE4A/BC9C gain and bounded scaling stage"),
0xC53A2:("sienna_command_shaping","ADF6/BE28 mode-gain/debounce stage"),
0xC8DE0:("sienna_lta_angle_command","authenticated 0x131 angle smoothing into BFF0"),
0xC5350:("sienna_state_postprocess","state snapshot/bounded helper wrapper"),
0xC4EC8:("sienna_command_shaping","command/state sign debounce/status stage"),
0xC4F7C:("sienna_command_shaping","AE4A-driven gain/integrator/output shaping stage"),
}

def sha(b:bytes)->str:return hashlib.sha256(b).hexdigest()
def loadj(p:Path):return json.loads(p.read_text())
def validate_struct(doc,image):
 if doc['image']['sha256']!=sha(image):raise ValueError('structural evidence image mismatch')
 out={}
 for r in doc['functions']:
  a=int(r['entry'],16);body=image[a:a+r['body_size']]
  if sha(body)!=r['body_sha256']:raise ValueError(f'body hash mismatch {a:#x}')
  out[a]=r
 return out

def calls(c,nmap):
 out=[]
 for line in c.splitlines():
  m=re.search(r'\b([A-Za-z_][A-Za-z0-9_]*)\(\);',line)
  if not m:continue
  n=m.group(1)
  if n.startswith('FUN_'):a=int(n[4:],16)
  else:a=nmap.get(n)
  if a is not None:out.append(a)
 return out

def align(S,H,Sf,Hf):
 M,N=len(S),len(H);sim={}
 for i,s in enumerate(S):
  for j,h in enumerate(H):
   a,b=Sf[s],Hf[h]
   r=difflib.SequenceMatcher(None,a['mnemonics'],b['mnemonics'],autojunk=False).ratio()
   sr=min(a['body_size'],b['body_size'])/max(a['body_size'],b['body_size'])
   sim[i,j]=.85*r+.15*sr
 dp=[[(-1e9,None)]*(N+1) for _ in range(M+1)];dp[0][0]=(0,None)
 for i in range(M+1):
  for j in range(N+1):
   cur=dp[i][j][0]
   if cur<-1e8:continue
   if i<M and j<N:
    r=sim[i,j];score=(r-.52)*1.8+(.18 if r>.97 else 0)
    if cur+score>dp[i+1][j+1][0]:dp[i+1][j+1]=(cur+score,('match',i,j,r))
   if i<M and cur+GAP>dp[i+1][j][0]:dp[i+1][j]=(cur+GAP,('sienna_only',i,j,None))
   if j<N and cur+GAP>dp[i][j+1][0]:dp[i][j+1]=(cur+GAP,('h_only',i,j,None))
 ops=[];i,j=M,N
 while i or j:
  op=dp[i][j][1];ops.append(op)
  if op[0]=='match':i-=1;j-=1
  elif op[0]=='sienna_only':i-=1
  else:j-=1
 return list(reversed(ops))

def main():
 ap=argparse.ArgumentParser(description=__doc__)
 ap.add_argument('--sienna-image',type=Path,default=REPO/'firmware/RH850_P1M-E_CodeFlash.bin')
 ap.add_argument('--h-image',type=Path,default=REPO/'community/albinoelephant/normalized/8965H1202000_CodeFlash.bin')
 ap.add_argument('--sienna-struct',type=Path,default=REPO/'data/generated/sienna_8965B4512000_steering_supervisor_structural_evidence.json')
 ap.add_argument('--h-struct',type=Path,default=REPO/'data/generated/corolla_8965H1202000_steering_supervisor_structural_evidence.json')
 ap.add_argument('--h-insertions',type=Path,default=REPO/'data/generated/corolla_8965H1202000_steering_supervisor_insertions_decompiler_evidence.json')
 ap.add_argument('--exact-transfer',type=Path,default=REPO/'data/generated/corolla_8965H1202000_structural_function_transfer.json')
 ap.add_argument('--out',type=Path,default=REPO/'data/generated/corolla_8965H1202000_steering_supervisor_stage_ledger.json')
 a=ap.parse_args();si=a.sienna_image.read_bytes();hi=a.h_image.read_bytes()
 Sf=validate_struct(loadj(a.sienna_struct),si);Hf=validate_struct(loadj(a.h_struct),hi)
 # canonical S root/name map
 decs=[]
 for line in (REPO/'data/generated/decompilations.jsonl').read_text().splitlines():
  r=json.loads(line)
  if 'entry_addr' in r:decs.append(r)
 nmap={r['name']:int(r['entry_addr'],16) for r in decs};sroot=next(r for r in decs if int(r['entry_addr'],16)==0xCB86E)
 hdoc=loadj(a.h_insertions); hroot=next(r for r in hdoc['functions'] if int(r['entry'],16)==0xCEDAE)
 S=calls(sroot['decompiled_c'],nmap);H=calls(hroot['decompiled_c'],{})
 if len(S)!=94 or len(H)!=123:raise ValueError(f'root call counts drifted S={len(S)} H={len(H)}')
 ops=align(S,H,Sf,Hf)
 exact=loadj(a.exact_transfer); exactpairs={(int(r['reference_entry'],16),int(r['target_entry'],16)) for r in exact['matches']}
 stages=[];honly=[];sonly=[];matched=[]
 for typ,i,j,score in ops:
  if typ=='match':
   s,h=S[i],H[j];evidence='unique-exact-instruction-shape' if (s,h) in exactpairs else ('order-aligned-high-similarity' if score>=.85 else 'order-aligned-candidate')
   row={'classification':'paired','sienna_index':i,'sienna_entry':f'0x{s:X}','h_index':j,'h_entry':f'0x{h:X}','structural_similarity':round(score,6),'pair_evidence':evidence}
   matched.append(row);stages.append(row)
  elif typ=='h_only':
   h=H[j]
   if h not in H_ROLE:raise ValueError(f'unclassified H insertion {h:#x}')
   role,desc=H_ROLE[h];row={'classification':'h-order-unpaired','h_index':j,'h_entry':f'0x{h:X}','role_class':role,'bounded_description':desc,'evidence_boundary':'target-native decompilation reviewed; unpaired in ordered supervisor alignment, not proof of global absence in Sienna'}
   honly.append(row);stages.append(row)
  else:
   s=S[i]
   if s not in S_REMOVED_ROLE:raise ValueError(f'unclassified Sienna removal {s:#x}')
   role,desc=S_REMOVED_ROLE[s];row={'classification':'sienna-order-unpaired','sienna_index':i,'sienna_entry':f'0x{s:X}','role_class':role,'bounded_description':desc,'evidence_boundary':'unpaired in ordered supervisor alignment; only explicit command-stage removals are promoted using independent CAN/config evidence'}
   sonly.append(row);stages.append(row)
 # key semantic pins for expansion/deletion claims
 Hdec={int(r['entry'],16):r['decompiled_c'] for r in hdoc['functions']}
 pins={0xC89D2:['cRamfebeadc2'],0xC7C70:['cRamfebeadb9'],0xCCF58:['-0xa47'],0xC80C4:['sRamfebeae20'],0xC35BC:['cRamfebebb9c'],0xC37AC:['cRamfebebb9f'],0xC4696:['uRamfebebbaa']}
 for addr,needles in pins.items():
  for needle in needles:
   if needle not in Hdec[addr]:raise ValueError(f'H insertion semantic pin missing {addr:#x} {needle}')
 lta=next(r for r in decs if int(r['entry_addr'],16)==0xC8DE0)['decompiled_c']
 if 'authenticated 0x131 STEERING_LTA_2' not in lta or 'DAT_febeae60' not in lta:raise ValueError('Sienna LTA command stage semantic pin missing')
 payload={'schema':'corolla-8965H1202000-steering-supervisor-stage-ledger-v1',
  'evidence_boundary':'Global order alignment is a navigation aid. Only unique complete instruction-shape pairs are semantic-transfer candidates; other pairs require target-native operand/dataflow review. H/S order-unpaired rows are not global absence proofs.',
  'roots':{'sienna':'0xCB86E','corolla_h':'0xCEDAE','sienna_body_size':sroot['body_size'],'corolla_h_body_size':hroot['body_size'],'sienna_direct_stage_count':len(S),'corolla_h_direct_stage_count':len(H)},
  'summary':{'paired':len(matched),'paired_unique_exact_shape':sum(r['pair_evidence']=='unique-exact-instruction-shape' for r in matched),'paired_high_similarity_nonexact':sum(r['pair_evidence']=='order-aligned-high-similarity' for r in matched),'paired_order_candidate':sum(r['pair_evidence']=='order-aligned-candidate' for r in matched),'h_order_unpaired':len(honly),'sienna_order_unpaired':len(sonly),'h_unpaired_role_counts':{}},
  'stages':stages,'h_order_unpaired':honly,'sienna_order_unpaired':sonly,
  'explicit_command_mode_boundary':{'classic_2e4':'normal Rx descriptor absent on H and retained clamp branch is independently proven zero-fed','classic_131':'normal Rx/SecOC descriptor absent on H and Sienna lta_angle_command_smoothing 0xC8DE0 is order-unpaired','replacement_command':'no direct replacement is assigned; H-only expansion is classified as supervisor/estimation/plausibility/status unless stronger ingress evidence exists'}}
 from collections import Counter
 payload['summary']['h_unpaired_role_counts']=dict(sorted(Counter(r['role_class'] for r in honly).items()))
 a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(payload,indent=2,sort_keys=True)+'\n')
 print(json.dumps(payload['summary'],indent=2))
if __name__=='__main__':main()
