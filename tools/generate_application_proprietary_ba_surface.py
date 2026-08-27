#!/usr/bin/env python3
"""Generate the bounded application SID-0xBA proprietary operation surface."""
from __future__ import annotations
import argparse,csv,struct
from pathlib import Path
from sienna_target import CODEFLASH as SIENNA_CODEFLASH
ROOT=Path(__file__).resolve().parents[1]
CF=(SIENNA_CODEFLASH).read_bytes()
TABLE=0x28098
COUNT_ADDR=0x28094
# Semantics are bounded by deterministic firmware verifiers. Raw table fields are always derived.
SEM={
0xF1: dict(request_shape='F1 JTEKM', effect_class='service_lifecycle_mode3_request', local_gate='persistent_BA_authorization', persistence='none', downstream='FEBEB112=5A; FEBEB113=11'),
0xF3: dict(request_shape='F3 TMPCL', effect_class='persistent_object5_6_maintenance', local_gate='persistent_BA_authorization + local status', persistence='ordinary objects 5,6', downstream='runtime groups + object5/6 maintenance'),
0xF4: dict(request_shape='F4 JTRM1', effect_class='service_lifecycle_mode5_request', local_gate='persistent_BA_authorization', persistence='none', downstream='FEBEB112=5A; FEBEB113=22'),
0xF5: dict(request_shape='F5 JTRM2', effect_class='service_lifecycle_mode6_request', local_gate='persistent_BA_authorization', persistence='none', downstream='FEBEB112=5A; FEBEB113=44'),
0xF6: dict(request_shape='F6 BADIS', effect_class='persistent_BA_authorization_disable', local_gate='persistent_BA_authorization', persistence='ordinary object 24 + redundant object 5', downstream='FEBE5F27/28 -> 0/0'),
0xF7: dict(request_shape='F7 BAENA', effect_class='SA2_persistent_BA_authorization_enable', local_gate='application SecurityAccess level 2', persistence='ordinary object 24 + redundant object 5', downstream='FEBE5F27=5A; FEBE5F28=30'),
0xF8: dict(request_shape='F8 TZCLR', effect_class='speed_state_gated_shared_persistent_workflow', local_gate='persistent_BA_authorization + speed<=0x04B0 + transition/state gates', persistence='shared B7D26 namespace-0x100 workflow', downstream='B7D26(22,2) completion family'),
0xF9: dict(request_shape='F9 JTRM3', effect_class='service_lifecycle_mode7_request', local_gate='persistent_BA_authorization', persistence='none', downstream='FEBEB112=5A; FEBEB113=88'),
0xFA: dict(request_shape='FA <value> VSPD', effect_class='alternate_speed_like_snapshot_override', local_gate='persistent_BA_authorization + feature flag', persistence='none', downstream='FEBEB116=5A; FEBEB117=value -> FEBEB6F6 -> FEBEE894'),
0xFB: dict(request_shape='FB ASINC', effect_class='filtered_operational_inhibit_flag', local_gate='persistent_BA_authorization', persistence='none', downstream='FEBEB118=5A -> B80EE filtered branch'),
}
EXPECTED_START={0xF1:0x34B74,0xF3:0x34BA8,0xF4:0x34C50,0xF5:0x34C84,0xF6:0x34CB8,0xF7:0x34DAE,0xF8:0x34EC0,0xF9:0x34F1A,0xFA:0x34F4E,0xFB:0x34F90}
EXPECTED_DONE={0xF1:0x34B9A,0xF3:0x34BF4,0xF4:0x34C76,0xF5:0x34CAA,0xF6:0x34D4E,0xF7:0x34E6C,0xF8:0x34F08,0xF9:0x34F40,0xFA:0x34F80,0xFB:0x34FAA}
def rows():
 count=CF[COUNT_ADDR]
 if count!=10: raise SystemExit(f'unexpected BA operation count {count}')
 out=[]
 for i in range(count):
  a=TABLE+i*16
  sel,length,result,*_=CF[a:a+8]
  start,done=struct.unpack_from('<II',CF,a+8)
  if sel not in SEM: raise SystemExit(f'unexpected selector {sel:02X}')
  if length!=6 or start!=EXPECTED_START[sel] or done!=EXPECTED_DONE[sel]:
   raise SystemExit(f'BA row {sel:02X} drift')
  s=SEM[sel]
  out.append({
   'selector':f'0x{sel:02X}','descriptor_addr':f'0x{a:X}','request_data_length':str(length),
   'request_shape':s['request_shape'],'start_callback':f'0x{start:X}','completion_callback':f'0x{done:X}',
   'effective_session':'3','configured_service_security_count':'0','effective_local_gate':s['local_gate'],
   'effect_class':s['effect_class'],'persistence':s['persistence'],'downstream_state':s['downstream'],
   'direct_actuation_boundary':'no direct conditioned-command/dq/PWM reference in recovered cone',
  })
 return out
def main():
 p=argparse.ArgumentParser(); p.add_argument('-o','--output',type=Path,default=ROOT/'data/application_proprietary_ba_surface.csv'); a=p.parse_args()
 rs=rows(); a.output.parent.mkdir(parents=True,exist_ok=True)
 with a.output.open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rs[0]),lineterminator='\n');w.writeheader();w.writerows(rs)
 print(f'Wrote {len(rs)} BA operation rows to {a.output}')
if __name__=='__main__': main()
