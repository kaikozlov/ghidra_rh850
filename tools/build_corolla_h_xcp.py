#!/usr/bin/env python3
"""Build deterministic Sienna↔Corolla-H XCP residual comparison."""
from __future__ import annotations
import argparse,hashlib,json,struct
from pathlib import Path
from sienna_target import CODEFLASH as SIENNA_CODEFLASH
from corolla_h_constants import RAW_DUMP, XCP_ROLE_MAP
ROOT=Path(__file__).resolve().parents[1];EV=ROOT/'data/generated/corolla_8965H1202000_xcp_decompiler_evidence.json';SC=ROOT/'data/generated/decompilations.jsonl';HRAW=RAW_DUMP;SI=SIENNA_CODEFLASH;OUT=ROOT/'data/generated/corolla_8965H1202000_xcp.json'
MAP=XCP_ROLE_MAP
def sha(b):return hashlib.sha256(b).hexdigest()
def u32(b,a):return struct.unpack_from('<I',b,a)[0]
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,default=OUT);a=ap.parse_args();ev=json.loads(EV.read_text());h={int(x['entry'],16):x for x in ev['functions']};H=HRAW.read_bytes()[:0x100000];S=SI.read_bytes()
 if sha(H)!=ev['image']['codeflash_sha256']:raise ValueError('H hash drift')
 roles=[{'reference_entry':f'0x{sa:08X}','reference_name':n,'target_entry':f'0x{ha:08X}','selector':op,'classification':'target-native-role-recovered','target_body_size':h[ha]['body_size']} for sa,n,ha,op in MAP]
 s_table=[(u32(S,0x2B3F0+i*8),u32(S,0x2B3F4+i*8)) for i in range(7)];h_table=[(u32(H,0x2AE38+i*8),u32(H,0x2AE3C+i*8)) for i in range(7)]
 selectors=[0xFB,0xFA,0xF5,0xF3,0xEB,0xEA,0xE4]
 if [x[0] for x in s_table]!=selectors or [x[0] for x in h_table]!=selectors:raise ValueError('XCP selector table drift')
 excl=[(u32(H,0x28F0C+i*8),u32(H,0x28F10+i*8)) for i in range(u32(H,0x2AE00))]
 payload={'schema':'corolla-h-xcp-v1','software_id':'8965H1202000','images':{'h_sha256':sha(H),'sienna_sha256':sha(S)},'evidence':{'decompiler_evidence':str(EV.relative_to(ROOT)),'canonical_corpus':str(SC.relative_to(ROOT))},'xcp_role_closure':roles,'xcp_role_closure_count':4,'custom_command_table':{'selectors':selectors,'sienna_base':'0x0002B3F0','h_base':'0x0002AE38','sienna_handlers':[f'0x{x[1]:08X}' for x in s_table],'h_handlers':[f'0x{x[1]:08X}' for x in h_table]},'fa_indexed_identifier':{'h':'0x0009232A','index_limit':5,'pointer_table':'0x0002AE10','metadata_table':'0x0002AE14','response_helper':'0x0009227E'},'f5_upload':{'h':'0x00092462','request_length':8,'byte_count_min':1,'byte_count_max':7,'range_helper':'0x0009238A','copy_helper':'0x00092436','localram_outer_range':['0xFEBE0000','0xFEBFFFFF'],'exclusion_count':u32(H,0x2AE00),'h_exclusion_ranges':[[f'0x{x:08X}',f'0x{y:08X}'] for x,y in excl],'special_codeflash_copy_check':{'length':0x7DEC,'start_min':'0x00010000','end_exclusive':'0x00017DF0'},'interpretation':'bounded upload/read policy survives with H-specific relocated exclusion windows'},'page_state':{'writer_h':'0x0009261E','reader_h':'0x00092698','state_cells':['0xFEBE5DB0','0xFEBE5DB1'],'writer_accepts_values':[0,1],'writer_flag_mask':3,'reader_selectors':[1,2],'response_helper':'0x0009227E'},'e4_support':{'selector':0xE4,'h_handler':'0x00092724','remains_in_same_custom_table':True},'static_conclusion':{'xcp_residue_closed':True,'custom_selector_set_preserved':True,'application_side_f5_read_primitive_preserved':True,'boundary':'this transfers application-side command semantics; external gateway reachability remains a separate dynamic/topology question'}}
 a.out.write_text(json.dumps(payload,indent=2,sort_keys=True)+'\n');print('wrote',a.out)
if __name__=='__main__':main()
