#!/usr/bin/env python3
"""Recover TAUJ0/CAN1 interrupt body roles from H wrapper call chains."""
from __future__ import annotations
import argparse,hashlib,json,struct
from pathlib import Path
from corolla_h_constants import RAW_DUMP as H_RAW_DUMP
ROOT=Path(__file__).resolve().parents[1]
HRAW=H_RAW_DUMP
HEV=ROOT/'data/generated/corolla_8965H1202000_application_interrupt_body_decompiler_evidence.json'
OUT=ROOT/'data/generated/corolla_8965H1202000_application_interrupt_bodies.json'
# ref, name, H wrapper, expected H body, optional thunk
ROLES=[
 (0x64F18,'application_tauj0_ch0_body',0x6A6C0,0x5F258,None),
 (0x64F54,'application_tauj0_ch1_body',0x6A76A,0x5F294,None),
 (0x64F90,'application_tauj0_ch2_body',0x6A816,0x5F2D0,None),
 (0x82E40,'application_can1_rx_interrupt_body',0x5F3AA,0x7D240,0x5FB1E),
 (0x8474E,'application_can1_tx_interrupt_body',0x5F368,0x7EB4E,0x5FB12),
]
def sha(b):return hashlib.sha256(b).hexdigest()
def branch(blob,a):
 w0,w1=struct.unpack_from('<HH',blob,a)
 if ((w0>>6)&0x1f)!=0x1e or (w1&1):return None
 reg=(w0>>11)&0x1f;hi=w0&0x3f
 if hi&0x20:hi-=0x40
 return ('jarl' if reg else 'jr',a+(hi<<16)+w1)
def calls(blob,a,n):
 out=[]
 for x in range(a,a+n-3,2):
  d=branch(blob,x)
  if d and d[0]=='jarl':out.append((x,d[1]))
 return out
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,default=OUT);a=ap.parse_args();h=HRAW.read_bytes()[:0x100000]
 ed=json.loads(HEV.read_text());ev={int(r['entry'],16):r for r in ed['functions']}
 if ed['image']['codeflash_sha256']!=sha(h):raise ValueError('evidence image mismatch')
 for x,r in ev.items():
  if sha(h[x:x+r['body_size']])!=r['body_sha256'] or sha(r['decompiled_c'].encode())!=r['decompiled_c_sha256']:raise ValueError(f'evidence drift {x:#x}')
 # Wrapper sizes are pinned from same-generation layout; call lists are raw instruction evidence.
 wrapper_sizes={0x6A6C0:170,0x6A76A:172,0x6A816:172,0x5F3AA:66,0x5F368:66}
 rows=[];closures=[]
 for ref,name,wrapper,body,thunk in ROLES:
  cs=calls(h,wrapper,wrapper_sizes[wrapper]);targets=[t for _,t in cs]
  if thunk is None:
   if body not in targets:raise ValueError(f'{name}: body not directly called by wrapper')
   chain=[f'0x{wrapper:08X}',f'0x{body:08X}']
  else:
   if thunk not in targets:raise ValueError(f'{name}: thunk not called by wrapper')
   tc=calls(h,thunk,ev[thunk]['body_size'])
   if [t for _,t in tc]!=[body]:raise ValueError(f'{name}: thunk target drift')
   chain=[f'0x{wrapper:08X}',f'0x{thunk:08X}',f'0x{body:08X}']
  rows.append({'reference_entry':f'0x{ref:08X}','reference_name':name,'h_wrapper':f'0x{wrapper:08X}','h_body':f'0x{body:08X}','chain':chain,'h_body_size':ev[body]['body_size']})
  closures.append({'reference_entry':f'0x{ref:08X}','reference_name':name,'target_entry':f'0x{body:08X}','role':name})
 # semantic-shape checks against the recovered H bodies
 for body in (0x5F258,0x5F294,0x5F2D0):
  c=ev[body]['decompiled_c']
  if "== 'Z'" not in c or "= 0x5a" not in c or "+ '\\x01'" not in c:raise ValueError(f'TAUJ body shape drift {body:#x}')
 if 'FUN_0007d202(1)' not in ev[0x7D240]['decompiled_c']:raise ValueError('CAN1 RX channel specialization drift')
 if 'FUN_0007eb10(1)' not in ev[0x7EB4E]['decompiled_c']:raise ValueError('CAN1 TX channel specialization drift')
 p={'schema':'corolla-h-application-interrupt-bodies-v1','software_id':'8965H1202000','image':{'h_sha256':sha(h)},'evidence':{'decompiler_evidence':str(HEV.relative_to(ROOT))},'rows':rows,'role_closure':closures,'role_closure_count':len(closures),'target_evidence_entries':[x['target_entry'] for x in closures],'static_conclusion':{'five_roles_recovered':True,'boundary':'TAUJ role identity is anchored by same EIINT-channel wrapper direct calls; CAN1 body identity is anchored by same EIINT channel plus one-hop thunk and literal channel-1 specialization. Deeper timer/ADC semantics are not transferred here.'}}
 a.out.write_text(json.dumps(p,indent=2,sort_keys=True)+'\n');print('wrote',a.out)
if __name__=='__main__':main()
