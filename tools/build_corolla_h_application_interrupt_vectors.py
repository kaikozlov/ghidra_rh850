#!/usr/bin/env python3
"""Build raw application EIINT vector-role transfer for unresolved Corolla H wrappers."""
from __future__ import annotations
import argparse,hashlib,json,struct
from pathlib import Path
from sienna_target import CODEFLASH as SIENNA_CODEFLASH
from corolla_h_constants import RAW_DUMP as H_RAW_DUMP
ROOT=Path(__file__).resolve().parents[1];SRAW=SIENNA_CODEFLASH;HRAW=H_RAW_DUMP;OUT=ROOT/'data/generated/corolla_8965H1202000_application_interrupt_vectors.json';BASE=0x20200;COUNT=384
ROLES={8:(0x70A54,'application_ecm_maskable_isr'),133:(0x70320,'application_tauj0_ch0_isr'),134:(0x703CA,'application_tauj0_ch1_isr'),135:(0x70476,'application_tauj0_ch2_isr'),187:(0x6506A,'application_can1_rx_isr'),188:(0x65028,'application_can1_tx_isr'),379:(0x65130,'application_flash_end_isr')}
def sha(b):return hashlib.sha256(b).hexdigest()
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,default=OUT);a=ap.parse_args();s=SRAW.read_bytes();h=HRAW.read_bytes()[:0x100000]
 sv=list(struct.unpack_from('<384I',s,BASE));hv=list(struct.unpack_from('<384I',h,BASE));roles=[];rows=[]
 for ch,(expected,name) in ROLES.items():
  if sv[ch]!=expected:raise ValueError(f'S vector drift ch{ch}: {sv[ch]:#x}')
  rows.append({'channel':ch,'sienna_target':f'0x{sv[ch]:08X}','h_target':f'0x{hv[ch]:08X}','reference_name':name})
  roles.append({'reference_entry':f'0x{expected:08X}','reference_name':name,'target_entry':f'0x{hv[ch]:08X}','role':f'application EIINT channel {ch} wrapper'})
 p={'schema':'corolla-h-application-interrupt-vectors-v1','software_id':'8965H1202000','images':{'sienna_sha256':sha(s),'h_sha256':sha(h)},'table':{'base':f'0x{BASE:08X}','count':COUNT,'sienna_sha256':sha(s[BASE:BASE+COUNT*4]),'h_sha256':sha(h[BASE:BASE+COUNT*4])},'rows':rows,'role_closure':roles,'role_closure_count':len(roles),'target_evidence_entries':[x['target_entry'] for x in roles],'static_conclusion':{'seven_unresolved_wrappers_recovered':True,'boundary':'Role transfer is limited to wrapper identity at the same hardware EIINT channel. Handler internals and downstream callback targets remain H-specific unless separately recovered.'}}
 a.out.write_text(json.dumps(p,indent=2,sort_keys=True)+'\n');print('wrote',a.out)
if __name__=='__main__':main()
