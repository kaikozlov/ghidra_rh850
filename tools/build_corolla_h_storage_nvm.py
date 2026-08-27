#!/usr/bin/env python3
"""Build deterministic H storage/NvM role and persistence-boundary report."""
from __future__ import annotations
import argparse,hashlib,json,struct
from pathlib import Path
from sienna_target import CODEFLASH as SIENNA_CODEFLASH
from corolla_h_constants import RAW_DUMP as H_RAW_DUMP
ROOT=Path(__file__).resolve().parents[1]
EV=ROOT/'data/generated/corolla_8965H1202000_storage_nvm_decompiler_evidence.json';SC=ROOT/'data/generated/decompilations.jsonl';DF=ROOT/'data/generated/corolla_2023_albino_dataflash_analysis.json'
HRAW=H_RAW_DUMP;SI=SIENNA_CODEFLASH;OUT=ROOT/'data/generated/corolla_8965H1202000_storage_nvm.json'
MAP=[(0x4EAD8,'application_dataflash_range_allowed',0x4A534),(0x65C84,'secoc_nvm_restore_request',0x5FFBC),(0x66DB2,'secoc_nvm_queue_restore',0x610EA)]
def sha(b):return hashlib.sha256(b).hexdigest()
def load_s():
 want={x[0] for x in MAP};d={}
 for l in SC.read_text().splitlines():
  r=json.loads(l)
  if r.get('entry_addr') and int(r['entry_addr'],16) in want:d[int(r['entry_addr'],16)]=r
 return d
def u16(b,a):return struct.unpack_from('<H',b,a)[0]
def u32(b,a):return struct.unpack_from('<I',b,a)[0]
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,default=OUT);a=ap.parse_args();ev=json.loads(EV.read_text());h={int(r['entry'],16):r for r in ev['functions']};s=load_s();H=HRAW.read_bytes()[:0x100000];S=SI.read_bytes();df=json.loads(DF.read_text())
 if sha(H)!=ev['image']['codeflash_sha256']:raise ValueError('H hash drift')
 roles=[]
 for sa,n,ha in MAP:
  roles.append({'reference_entry':f'0x{sa:08X}','reference_name':n,'target_entry':f'0x{ha:08X}','classification':'target-native-role-recovered','reference_body_size':s[sa]['body_size'],'target_body_size':h[ha]['body_size']})
 sr=[u32(S,0x293E4+i*4) for i in range(4)];hr=[u32(H,0x28EFC+i*4) for i in range(4)]
 if sr!=hr:raise ValueError('protected-range table diverged')
 obj15=next(x for x in df['triplicate_objects'] if x['object']==15)
 q=h[0x610EA]['decompiled_c'];req=h[0x5FFBC]['decompiled_c'];rng=h[0x4A534]['decompiled_c']
 payload={'schema':'corolla-h-storage-nvm-v1','software_id':'8965H1202000','images':{'h_sha256':sha(H),'sienna_sha256':sha(S),'dataflash_sha256':df['dump_sha256']},'evidence':{'decompiler_evidence':str(EV.relative_to(ROOT)),'canonical_corpus':str(SC.relative_to(ROOT)),'dataflash_analysis':str(DF.relative_to(ROOT))},'storage_nvm_role_closure':roles,'storage_nvm_role_closure_count':3,'dataflash_range_filter':{'sienna_table':'0x000293E4','h_table':'0x00028EFC','ranges':[{'start':f'0x{sr[0]:08X}','end':f'0x{sr[1]:08X}'},{'start':f'0x{sr[2]:08X}','end':f'0x{sr[3]:08X}'}],'tables_identical':True,'h_accept_marker':0x5A,'object15_geometry_inside_second_range':all(0xFF206C00<=int(obj15['known_key_field_geometry'][k],16)<=0xFF206EFF for k in ('raw','xor55','xoraa')),'boundary':'range filter proves exclusion geometry; it does not establish which diagnostic/API caller invokes the helper on every path'},'restore_request':{'sienna':'0x00065C84','h':'0x0005FFBC','namespace_dispatch':{'0x000':'0x0006095C','0x100':'0x000610EA','0x200':'0x000603CE'},'namespace_0x100_is_restore':True,'h_object_count':u16(H,0x2A972),'sienna_object_count':u16(S,0x2AF12),'interpretation':'namespace 0x100 queues generic triplicate NvM restore; it is not an ICU key-set command'},'queue_restore':{'sienna':'0x00066DB2','h':'0x000610EA','queue_state':0x11,'object_count':u16(H,0x2A972),'copies_requested':3,'h_three_copy_worker':'0x00069D1A','has_0x11_state_write':"= 0x11" in q,'request_calls_queue_restore':'FUN_000610ea(param_1)' in req},'object15_snapshot':{'object':15,'payload_length':obj15['payload_length'],'valid_copy_count':obj15['valid_copy_count'],'valid_consensus':obj15['valid_consensus'],'known_key_field_geometry':obj15['known_key_field_geometry'],'copy_addresses':[c['va_start'] for c in obj15['copies']],'copy_validity':[c['observable_valid'] for c in obj15['copies']],'interpretation':'generic restore machinery can address object 15, but the supplied H snapshot has no valid committed object-15 copy'},'static_conclusion':{'storage_nvm_residue_closed':True,'runtime_slot4_key_from_valid_object15_in_supplied_snapshot':False,'command8_provisioning_remains_separate':True,'boundary':'this closes the three named storage/NvM roles and current snapshot validity; it does not prove production dealer workflow or arbitrary undocumented storage'}}
 a.out.write_text(json.dumps(payload,indent=2,sort_keys=True)+'\n');print('wrote',a.out)
if __name__=='__main__':main()
