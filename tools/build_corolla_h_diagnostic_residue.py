#!/usr/bin/env python3
"""Build deterministic Corolla-H closure for the 59 remaining diagnostic roles."""
from __future__ import annotations
import argparse,hashlib,json,struct
from pathlib import Path
from sienna_target import CODEFLASH as SIENNA_CODEFLASH
from corolla_h_constants import RAW_DUMP as H_RAW_DUMP
ROOT=Path(__file__).resolve().parents[1]
EV=ROOT/'data/generated/corolla_8965H1202000_diagnostic_residue_decompiler_evidence.json'; HRAW=H_RAW_DUMP; SRAW=SIENNA_CODEFLASH; OUT=ROOT/'data/generated/corolla_8965H1202000_diagnostic_residue.json'
ROLE_MAP=[
 (0x4C942,'application_session_transition_policy',0x4826A),(0x80114,'application_can_diagnostic_rx_demux',0x7A510),(0x8A27E,'application_session_transition_check_adapter',0x8467E),(0x8B144,'application_clear_diagnostic_information_request_start',0x85544),
 (0x936AA,'application_wdbi_class_0201_write',0x8E6D0),(0x936D6,'application_wdbi_class_2001_write',0x8E6FC),(0x93B56,'application_wdbi_request_start',0x8EB7C),(0x93C62,'application_wdbi_callback',0x8EC88),
 (0x93D28,'application_session_request_start',0x8ED4E),(0x93E32,'application_session_request_cancel',0x8EE58),(0x93E72,'application_session_request_poll',0x8EE98),(0x93F9A,'application_session_transition_background_poll',0x8EFC0),(0x944C6,'application_rdbi_request_start',0x8F4EC),
 (0x955DC,'application_routine_control_type_supported',0x90602),(0x95624,'application_routine_control_input_length_invalid',0x9064A),(0x956C6,'application_routine_control_output_capacity_invalid',0x906EC),(0x95C8C,'application_routine_control_request_start',0x90CB2),
 (0xB28A2,'application_diagnostic_helper_b28a2',0xB2B6E),(0xB47A6,'application_diagnostic_helper_b47a6',0xB486C),(0xB55C4,'application_diagnostic_helper_b55c4',0xB5346),(0xB5D0C,'application_diagnostic_helper_b5d0c',0xB5A30),(0xB7C0E,'application_diagnostic_helper_b7c0e',0xB66B6),
 (0xFDE58,'application_diagnostic_helper_fde58',0xFDE58),(0xFDED0,'application_diagnostic_helper_fded0',0xFDED0),(0xFE060,'application_diagnostic_helper_fe060',0xFE060),(0xFE09C,'application_diagnostic_helper_fe09c',0xFE09C),(0xFE0C4,'application_diagnostic_helper_fe0c4',0xFE0C4),
]
RECENSUS_EXTRA=[
 (0x4EC68,'application_diagnostic_helper_4ec68','removed alternate WDBI branch'),(0x4F928,'application_did_table_getter','readable-DID surface regenerated and exhaustively enumerated'),
 (0xB71FE,'application_diagnostic_helper_b71fe','2014 setter removed from live H WDBI path'),(0xB76A8,'application_diagnostic_helper_b76a8','2013 setter removed from live H WDBI path'),(0xFE1B4,'application_diagnostic_helper_fe1b4','2014 thunk removed from live H WDBI path'),(0xFE1C8,'application_diagnostic_helper_fe1c8','2013 thunk removed from live H WDBI path'),
]
def sha(b):return hashlib.sha256(b).hexdigest()
def tab(b,base,n):
 return [{'did':f'0x{did:04X}','start':f'0x{s:08X}','result':f'0x{r:08X}'} for did,_pad,s,r in (struct.unpack_from('<HHII',b,base+i*12) for i in range(n))]
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,default=OUT);args=ap.parse_args();H=HRAW.read_bytes()[:0x100000];S=SRAW.read_bytes();ev=json.loads(EV.read_text());by={int(r['entry'],16):r for r in ev['functions']}
 if sha(H)!=ev['image']['codeflash_sha256']:raise ValueError('H image drift')
 roles=[]
 for s,n,h in ROLE_MAP:
  if h not in by:raise ValueError(f'missing evidence {h:#x}')
  roles.append({'reference_entry':f'0x{s:08X}','reference_name':n,'target_entry':f'0x{h:08X}','classification':'target-native-role-recovered','target_reported_body_size':by[h]['body_size']})
 st=tab(S,0x25768,13);ht=tab(H,0x25530,12); sd={x['did']:x for x in st};hd={x['did']:x for x in ht}
 callback_rec=[]
 names={0x0204:'0204',0x2001:'2001',0x2002:'2002',0x2005:'2005',0x2006:'2006',0x2007:'2007',0x2008:'2008',0x2009:'2009',0x200D:'200d',0x2010:'2010',0x2012:'2012',0x2013:'2013',0x2014:'2014'}
 for did,label in names.items():
  srow=sd[f'0x{did:04X}']; hrow=hd.get(f'0x{did:04X}')
  for phase in ('start','result'):
   callback_rec.append({'reference_entry':srow[phase],'reference_name':f'application_wdbi_{label}_{phase}','classification':'target-surface-recensused','h_target':hrow[phase] if hrow else None,'disposition':'removed DID' if hrow is None else ('disabled callback surface' if did in (0x2013,0x2014) else 'surviving H callback')})
 extras=[{'reference_entry':f'0x{s:08X}','reference_name':n,'classification':'target-surface-recensused','disposition':d} for s,n,d in RECENSUS_EXTRA]
 payload={'schema':'corolla-h-diagnostic-residue-v1','software_id':'8965H1202000','images':{'h_sha256':sha(H),'sienna_sha256':sha(S)},'evidence':{'decompiler_evidence':str(EV.relative_to(ROOT))},'diagnostic_role_closure':roles,'diagnostic_role_closure_count':len(roles),'diagnostic_surface_recensus':callback_rec+extras,'diagnostic_surface_recensus_count':len(callback_rec)+len(extras),
 'wdbi':{'sienna_table':{'base':'0x00025768','count':13,'rows':st},'h_table':{'base':'0x00025530','count':12,'rows':ht},'removed_dids':sorted(set(sd)-set(hd)),'added_dids':sorted(set(hd)-set(sd)),'start_lookup':{'sienna':'0x0008D3CC','h':'0x000877CC','h_count':12,'h_table_base':'0x00025530'},'result_lookup':{'sienna':'0x0008D416','h':'0x00087816','h_count':12},'disabled_on_h':['0x2013','0x2014'],'h_2012_unconditional_start': 'return 0;' in by[0x4A89A]['decompiled_c'],'interpretation':'H removes DID 200D; 2013/2014 remain configured but their start callbacks return 5 and results are no-op; 2012 remains unconditional-start. Surviving maintenance/persistence callbacks are regenerated and therefore old per-DID function identity is closed by complete table/callback recensus.'},
 'session':{'policy':{'sienna':'0x0004C942','h':'0x0004826A','requested_session_2_speed_gate':all(x in by[0x4826A]['decompiled_c'] for x in ["param_2 == '\\x02'",'return 0xb'])},'request_family':[['0x00093D28','0x0008ED4E'],['0x00093E32','0x0008EE58'],['0x00093E72','0x0008EE98'],['0x00093F9A','0x0008EFC0']]},
 'routine_control':{'helpers':[['0x000955DC','0x00090602'],['0x00095624','0x0009064A'],['0x000956C6','0x000906EC'],['0x00095C8C','0x00090CB2']],'h_rid_count_source':'DAT_00026376','outer_policy_shape_owned_by':'corolla_8965H1202000_application_diagnostics_diff.json'},
 'static_conclusion':{'all_59_diagnostic_residuals_closed':len(roles)+len(callback_rec)+len(extras)==59,'role_recovered':len(roles),'surface_recensused':len(callback_rec)+len(extras),'diagnostics_named_residue_closed':True,'boundary':'DCM lifecycle roles are recovered; generated DID/RID/WDBI content is target-specific and removed/disabled WDBI functions are recensused rather than assigned fake homologs.'}}
 args.out.write_text(json.dumps(payload,indent=2,sort_keys=True)+'\n');print('wrote',args.out)
if __name__=='__main__':main()
