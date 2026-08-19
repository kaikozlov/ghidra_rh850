#!/usr/bin/env python3
"""Build deterministic Corolla-H comparison for the final seven crypto roles."""
from __future__ import annotations
import argparse,hashlib,json,struct
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
EV=ROOT/'data/generated/corolla_8965H1202000_crypto_residue_decompiler_evidence.json';SC=ROOT/'data/generated/decompilations.jsonl';HRAW=ROOT/'community/albinoelephant/raw-20260818/albinoelephant-corolla-2023.20260814-0023/dump_codeflash_00000000_00200000_20260814-025814.bin';SI=ROOT/'firmware/RH850_P1M-E_CodeFlash.bin';OUT=ROOT/'data/generated/corolla_8965H1202000_crypto_residue.json'
ROLES=[
 (0x70fc,'payload_crypto_finalize',0x70e0,'exact-ambiguous-body-role-recovered'),
 (0x68f0c,'crypto_test_bank0_update_counter_snapshot',0x63244,'target-native-role-recovered'),
 (0x68f92,'crypto_test_bank0_activate',0x632ca,'target-native-role-recovered'),
 (0x68fc2,'crypto_test_bank1_update_counter_snapshot',0x632fa,'target-native-role-recovered'),
 (0x69018,'crypto_test_bank1_activate',0x63350,'target-native-role-recovered'),
 (0x88302,'crypto_generate_driver_record_lookup',0x82702,'target-native-role-recovered'),
 (0x88508,'crypto_driver_record_lookup',0x82908,'target-native-role-recovered'),
]
def sha(b):return hashlib.sha256(b).hexdigest()
def u16s(b,a,n):return [struct.unpack_from('<H',b,a+2*i)[0] for i in range(n)]
def load_s():
 d={}
 want={x[0] for x in ROLES}|{0x70e4}
 for l in SC.read_text().splitlines():
  r=json.loads(l)
  if r.get('entry_addr') and int(r['entry_addr'],16) in want:d[int(r['entry_addr'],16)]=r
 return d
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,default=OUT);args=ap.parse_args();ev=json.loads(EV.read_text());byh={int(x['target_entry'],16):x for x in ev['functions']};H=HRAW.read_bytes()[:0x100000];S=SI.read_bytes();sd=load_s()
 if sha(H)!=ev['image']['codeflash_sha256']:raise ValueError('H image drift')
 roles=[]
 for s,n,h,c in ROLES:
  roles.append({'reference_entry':f'0x{s:08X}','reference_name':n,'target_entry':f'0x{h:08X}','classification':'target-native-role-recovered','target_reported_body_size':byh[h]['target_reported_body_size'],'mapping_note':c})
 b0s=u16s(S,0x258e8,8);b0h=u16s(H,0x256a4,8);b1s=u16s(S,0x258f8,5);b1h=u16s(H,0x256b4,5)
 exact=S[0x70fc:0x7108]==H[0x70e0:0x70ec]
 payload={
  'schema':'corolla-h-crypto-residue-v1','software_id':'8965H1202000','images':{'h_sha256':sha(H),'sienna_sha256':sha(S)},'evidence':{'decompiler_evidence':str(EV.relative_to(ROOT))},'crypto_role_closure':roles,'crypto_role_closure_count':7,
  'payload_crypto_finalize':{'sienna':'0x000070FC','h':'0x000070E0','body_size':12,'exact_body_equal':exact,'h_calls_clear':'FUN_000070c8' in byh[0x70e0]['decompiled_c'],'sienna_clear':'0x000070E4','h_clear':'0x000070C8','clear_delta':-0x1c,'interpretation':'same boot payload crypto cleanup wrapper; raw body is non-unique globally, so role is bound by the adjacent clear-function call chain rather than exact bytes alone'},
  'crypto_test_banks':{
   'bank0':{'snapshot':{'sienna':'0x00068F0C','h':'0x00063244','sienna_counter_indices':b0s,'h_counter_indices':b0h},'activate':{'sienna':'0x00068F92','h':'0x000632CA','h_active_cell':'0xFEBE4F82','h_state_cell':'0xFEBE4F83','initial_state':0x11},'index_shift':[h-s for s,h in zip(b0s,b0h)]},
   'bank1':{'snapshot':{'sienna':'0x00068FC2','h':'0x000632FA','sienna_counter_indices':b1s,'h_counter_indices':b1h},'activate':{'sienna':'0x00069018','h':'0x00063350','h_active_cell':'0xFEBE4F87','h_state_cell':'0xFEBE4F88','initial_state':0x11},'index_shift':[h-s for s,h in zip(b1s,b1h)]},
   'interpretation':'both crypto-test banks preserve activation/state/snapshot architecture, while generated COM update-counter indices shift by -2, consistent with the H changed preceding Rx topology; do not transfer Sienna counter numbers'},
  'driver_record_lookup':{
   'generate':{'sienna':'0x00088302','h':'0x00082702','record_base':'0x00027C88','record_count':2,'record_stride':0x20},
   'verify_generic':{'sienna':'0x00088508','h':'0x00082908','record_base':'0x00027CCC','record_count':2,'record_stride':0x20},
   'delta':-0x5c00,'interpretation':'two-record lower-driver lookup roles preserve ID/stride/count with relocated generated tables'},
  'static_conclusion':{'all_7_crypto_residual_roles_recovered':True,'crypto_named_residue_closed':True,'test_bank_counter_population_changed':True,'boundary':'role/control semantics are recovered; generated H COM counter indices and RAM addresses remain target-specific'}
 }
 args.out.write_text(json.dumps(payload,indent=2,sort_keys=True)+'\n');print('wrote',args.out)
if __name__=='__main__':main()
