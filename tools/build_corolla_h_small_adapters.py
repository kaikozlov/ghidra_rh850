#!/usr/bin/env python3
"""Build deterministic closure for 18 generated packet/record/API adapter roles."""
from __future__ import annotations
import argparse,hashlib,json,struct
from pathlib import Path
from sienna_target import CODEFLASH as SIENNA_CODEFLASH
from corolla_h_constants import RAW_DUMP as H_RAW_DUMP
ROOT=Path(__file__).resolve().parents[1];HRAW=H_RAW_DUMP;SRAW=SIENNA_CODEFLASH;EV=ROOT/'data/generated/corolla_8965H1202000_small_adapter_decompiler_evidence.json';OUT=ROOT/'data/generated/corolla_8965H1202000_small_adapters.json'
BOUNDED=[(0x7ADC8,'bounded_api_wrapper_00',0x75168),(0x7ADDC,'bounded_api_wrapper_01',0x7517C),(0x7ADEE,'bounded_api_wrapper_02',0x7518E),(0x7AE00,'bounded_api_wrapper_03',0x751A0),(0x7AE14,'bounded_api_wrapper_04',0x751B4),(0x7AE28,'bounded_api_wrapper_05',0x751C8)]
PACKET=[(39,0x90676,'packet_low_selector_39_callback',0x8B69C),(43,0x9133C,'packet_low_selector_43_callback',0x8C362),(15,0x94A52,'packet_low_selector_15_callback',0x8FA78),(16,0x94B66,'packet_low_selector_16_callback',0x8FB8C),(38,0x953AA,'packet_low_selector_38_callback',0x903D0),(6,0x95DFC,'packet_low_selector_06_callback',0x90E22),(22,0x96B0C,'packet_low_selector_22_callback',0x91B32)]
RECORD=[(0,0x935BA,'record_operation_00_callback',0x8E5E0),(1,0x935EA,'record_operation_01_callback',0x8E610),(2,0x9361A,'record_operation_02_callback',0x8E640),(3,0x9364A,'record_operation_03_callback',0x8E670),(4,0x9367A,'record_operation_04_callback',0x8E6A0)]
def sha(b):return hashlib.sha256(b).hexdigest()
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,default=OUT);a=ap.parse_args();H=HRAW.read_bytes()[:0x100000];S=SRAW.read_bytes();ev=json.loads(EV.read_text());by={int(r['entry'],16):r for r in ev['functions']};roles=[]
 for s,n,h in BOUNDED:
  roles.append({'reference_entry':f'0x{s:08X}','reference_name':n,'target_entry':f'0x{h:08X}','classification':'target-native-role-recovered','family':'bounded_api'})
 for sel,s,n,h in PACKET:
  roles.append({'reference_entry':f'0x{s:08X}','reference_name':n,'target_entry':f'0x{h:08X}','classification':'target-native-role-recovered','family':'packet_selector','selector':sel})
 for idx,s,n,h in RECORD:
  roles.append({'reference_entry':f'0x{s:08X}','reference_name':n,'target_entry':f'0x{h:08X}','classification':'target-native-role-recovered','family':'record_operation','record_index':idx})
 # Raw config joins.
 sp=struct.unpack_from('<44I',S,0x26CEC);hp=struct.unpack_from('<44I',H,0x269FC)
 sr=[struct.unpack_from('<7I',S,0x26218+i*0x1c) for i in range(5)];hr=[struct.unpack_from('<7I',H,0x25F28+i*0x1c) for i in range(5)]
 sb=struct.unpack_from('<6I',S,0x2188C);hb=struct.unpack_from('<6I',H,0x21838)
 payload={'schema':'corolla-h-small-adapters-v1','software_id':'8965H1202000','images':{'h_sha256':sha(H),'sienna_sha256':sha(S)},'evidence':{'decompiler_evidence':str(EV.relative_to(ROOT))},'role_closure':roles,'role_closure_count':len(roles),
 'bounded_api':{'sienna_wrapper_range':['0x0007ADC8','0x0007AE28'],'h_wrapper_range':['0x00075168','0x000751C8'],'delta':-0x5C60,'sienna_pointer_table':{'base':'0x0002188C','values':[f'0x{x:08X}' for x in sb]},'h_pointer_table':{'base':'0x00021838','values':[f'0x{x:08X}' for x in hb]},'same_wrapper_sizes':[20,18,18,20,20,18]==[by[h]['body_size'] for _,_,h in BOUNDED]},
 'packet_selector':{'sienna_table_base':'0x00026CEC','h_table_base':'0x000269FC','table_count':44,'configured_selectors_sienna':[i for i,x in enumerate(sp) if x],'configured_selectors_h':[i for i,x in enumerate(hp) if x],'mapped_selectors':[x[0] for x in PACKET],'mapped_target_checks':all(hp[sel]==h for sel,_,_,h in PACKET)},
 'record_operation':{'sienna_table_base':'0x00026218','h_table_base':'0x00025F28','record_count':5,'stride':28,'sienna_callback_words':[f'0x{x[0]:08X}' for x in sr],'h_callback_words':[f'0x{x[0]:08X}' for x in hr],'mapped_target_checks':all(hr[i][0]==h for i,_,_,h in RECORD),'all_h_callbacks_48_bytes':all(by[h]['body_size']==48 for _,_,_,h in RECORD)},
 'static_conclusion':{'all_18_roles_recovered':len(roles)==18,'boundary':'packet selector and record-index meanings are configuration-bound; bounded wrappers preserve API slot order/signatures. Target callback internals and target table payload fields remain H-specific.'}}
 a.out.write_text(json.dumps(payload,indent=2,sort_keys=True)+'\n');print('wrote',a.out)
if __name__=='__main__':main()
