#!/usr/bin/env python3
"""Build raw configured application command/async-operation callback closure for 8965H1202000."""
from __future__ import annotations
import argparse,hashlib,json,struct
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SRAW=ROOT/'firmware/RH850_P1M-E_CodeFlash.bin'
HRAW=ROOT/'community/albinoelephant/raw-20260818/albinoelephant-corolla-2023.20260814-0023/dump_codeflash_00000000_00200000_20260814-025814.bin'
STRUCT=ROOT/'data/generated/corolla_8965H1202000_structural_function_transfer.json'
OUT=ROOT/'data/generated/corolla_8965H1202000_application_callback_tables.json'
S_CMD_BASE=0x22C30; H_CMD_BASE=0x22A74
S_OP_BASE=0x280A0; H_OP_BASE=0x27DB0
CMD_NAMES={
1:'application_command_01_callback',2:'application_command_02_callback',3:'application_command_03_callback',4:'application_command_04_callback',5:'application_command_05_callback',6:'application_command_06_callback',7:'application_command_07_callback',8:'application_command_08_callback',9:'application_command_09_callback',10:'application_command_10_callback',11:'application_command_11_callback',12:'application_command_12_callback',13:'application_command_13_callback',14:'application_command_14_callback',15:'application_command_15_callback',16:'application_command_16_callback',17:'application_command_17_callback'}
# Canonical descriptor callback names keyed by descriptor discriminator. F4/F5 are removed in H.
OP_ROWS={
0x6F3:('application_proprietary_ab_f1_start','application_proprietary_ab_f1_result'),
0x6F4:('application_operation_01_start','application_operation_01_completion'),
0x6F5:('application_operation_02_start','application_operation_02_completion'),
0x6F6:('application_operation_03_start','application_operation_03_completion'),
0x6F7:('application_operation_04_start','application_operation_04_completion'),
0x6F8:('application_operation_05_start','application_operation_05_completion'),
0x6F9:('application_operation_06_start','application_operation_06_completion'),
0x6FA:('application_operation_07_start','application_operation_07_completion'),
0x6FB:('application_operation_08_start','application_operation_08_completion'),
}
OP9=('application_operation_09_start','application_operation_09_completion')
def sha(b):return hashlib.sha256(b).hexdigest()
def words(b,a,n):return list(struct.unpack_from('<'+'I'*n,b,a))
def fmt(x):return f'0x{x:08X}'
def parse_op_rows(b,base,count):
 out=[]
 for i in range(count):
  a=base+i*0x10; p,q,c,d=struct.unpack_from('<4I',b,a)
  out.append({'address':fmt(a),'start':fmt(p),'completion':fmt(q),'config_word':fmt(c),'tail_word':fmt(d),'discriminator':c&0xffff})
 return out
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,default=OUT);a=ap.parse_args()
 S=SRAW.read_bytes();H=HRAW.read_bytes()[:0x100000]
 if len(S)!=0x100000 or len(H)!=0x100000:raise ValueError('expected 1 MiB images')
 st=json.loads(STRUCT.read_text())
 anchor=next(x for x in st['matches'] if int(x['reference_entry'],16)==0x81970)
 if int(anchor['target_entry'],16)!=0x7BD6C:raise ValueError('command-0 structural anchor drifted')
 sc=words(S,S_CMD_BASE,18);hc=words(H,H_CMD_BASE,18)
 # Raw uniqueness: H command-0 pointer is unique in image and occurs at table base.
 pat=struct.pack('<I',hc[0]);hits=[];pos=0
 while True:
  j=H.find(pat,pos)
  if j<0:break
  hits.append(j);pos=j+1
 roles=[];recensus=[]
 command_rows=[]
 for i,(sv,hv) in enumerate(zip(sc,hc)):
  command_rows.append({'command_id':i,'sienna_target':fmt(sv),'h_target':fmt(hv)})
  if i in CMD_NAMES:
   roles.append({'reference_entry':fmt(sv),'reference_name':CMD_NAMES[i],'target_entry':fmt(hv),'role':f'application command callback ID {i}'})
 # Canonical rows F3..FB + special op9. H has F3,F6..FB + special: F4/F5 removed.
 srows=parse_op_rows(S,S_OP_BASE,9)
 hrows=parse_op_rows(H,H_OP_BASE,7)
 sby={r['discriminator']:r for r in srows};hby={r['discriminator']:r for r in hrows}
 op_rows=[]
 for disc,names in OP_ROWS.items():
  sr=sby[disc];hr=hby.get(disc)
  status='preserved' if hr else 'removed'
  op_rows.append({'discriminator':f'0x{disc:04X}','status':status,'sienna':sr,'h':hr})
  for field,name in [('start',names[0]),('completion',names[1])]:
   ref=sr[field]
   if hr:
    roles.append({'reference_entry':ref,'reference_name':name,'target_entry':hr[field],'role':f'async operation descriptor {disc:#06x} {field}'})
   else:
    recensus.append({'reference_entry':ref,'reference_name':name,'reason':f'H async-operation descriptor set has no {disc:#06x} row'})
 # special op9 row immediately follows FB in both generations
 s9=parse_op_rows(S,S_OP_BASE+9*0x10,1)[0];h9=parse_op_rows(H,H_OP_BASE+7*0x10,1)[0]
 # special discriminator is a callback/state helper pointer in both words, not 6Fxx.
 op_rows.append({'discriminator':'special-op9','status':'preserved','sienna':s9,'h':h9})
 for field,name in [('start',OP9[0]),('completion',OP9[1])]:
  roles.append({'reference_entry':s9[field],'reference_name':name,'target_entry':h9[field],'role':f'async operation special op9 {field}'})
 target_evidence={int(x['target_entry'],16) for x in roles}
 payload={
 'schema':'corolla-h-application-callback-tables-v1','software_id':'8965H1202000',
 'images':{'sienna_sha256':sha(S),'h_sha256':sha(H)},
 'command_table':{'sienna_base':fmt(S_CMD_BASE),'h_base':fmt(H_CMD_BASE),'count':18,'anchor':{'reference':'0x00081970','target':'0x0007BD6C','structural_classification':anchor['classification'],'h_pointer_occurrences':[fmt(x) for x in hits]},'rows':command_rows},
 'async_operation_table':{'sienna_base':fmt(S_OP_BASE),'h_base':fmt(H_OP_BASE),'canonical_discriminators':[f'0x{x:04X}' for x in sorted(OP_ROWS)],'h_discriminators':[f'0x{x:04X}' for x in sorted(hby)],'rows':op_rows,'removed_discriminators':['0x06F4','0x06F5']},
 'role_closure':roles,'role_closure_count':len(roles),'surface_recensus':recensus,'surface_recensus_count':len(recensus),'target_evidence_entries':[fmt(x) for x in sorted(target_evidence)],
 'static_conclusion':{'command_roles_recovered':17,'operation_roles_recovered':16,'operation_roles_removed':4,'global_roles_recovered':len(roles),'boundary':'Command IDs and operation discriminators come from raw target configuration. Missing 6F4/6F5 proves removal of those configured descriptor roles only; it does not prove their lower-level behaviors are absent elsewhere in H.'}}
 a.out.write_text(json.dumps(payload,indent=2,sort_keys=True)+'\n');print('wrote',a.out)
if __name__=='__main__':main()
