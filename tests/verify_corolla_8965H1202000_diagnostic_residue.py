#!/usr/bin/env python3
"""Verify closure of the remaining Corolla-H named diagnostic residue."""
from __future__ import annotations
import hashlib,json,subprocess,sys,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];ART=ROOT/'data/generated/corolla_8965H1202000_diagnostic_residue.json';EV=ROOT/'data/generated/corolla_8965H1202000_diagnostic_residue_decompiler_evidence.json';TOOL=ROOT/'tools/build_corolla_h_diagnostic_residue.py';RAW=ROOT/'community/albinoelephant/raw-20260818/albinoelephant-corolla-2023.20260814-0023/dump_codeflash_00000000_00200000_20260814-025814.bin'
p=f=0
def check(n,c):
 global p,f;ok=bool(c);p+=ok;f+=not ok;print(f"[{'PASS' if ok else 'FAIL'}][raw_bytes] {n}")
def sha(b):return hashlib.sha256(b).hexdigest()
with tempfile.TemporaryDirectory() as td:
 out=Path(td)/'x.json';subprocess.run([sys.executable,str(TOOL),'--out',str(out)],cwd=ROOT,check=True,stdout=subprocess.DEVNULL);check('report regenerates exactly',out.read_bytes()==ART.read_bytes())
d=json.loads(ART.read_text());e=json.loads(EV.read_text());raw=RAW.read_bytes()[:0x100000];by={int(r['entry'],16):r for r in e['functions']}
check('H image hash pinned',sha(raw)==e['image']['codeflash_sha256'])
check('53 target-native functions compacted',e['function_count']==53==len(e['functions']))
check('all raw H bodies validate',all(sha(raw[int(r['entry'],16):int(r['entry'],16)+r['body_size']])==r['body_sha256'] for r in e['functions']))
check('all decompiler hashes validate',all(sha(r['decompiled_c'].encode())==r['decompiled_c_sha256'] for r in e['functions']))
check('27 diagnostic roles recovered',d['diagnostic_role_closure_count']==27)
check('32 canonical rows closed by complete recensus',d['diagnostic_surface_recensus_count']==32)
check('all 59 residual names accounted once',d['diagnostic_role_closure_count']+d['diagnostic_surface_recensus_count']==59)
w=d['wdbi'];check('S WDBI has 13 entries',w['sienna_table']['count']==13);check('H WDBI has 12 entries',w['h_table']['count']==12)
check('H removes only DID 200D',w['removed_dids']==['0x200D'] and not w['added_dids'])
check('H WDBI table base is 25530',w['h_table']['base']=='0x00025530' and w['start_lookup']['h_table_base']=='0x00025530')
check('H lookup bound is 12 in both phases',w['start_lookup']['h_count']==12==w['result_lookup']['h_count'])
check('2013 and 2014 are disabled on H',w['disabled_on_h']==['0x2013','0x2014'])
for did,start,result in [('0x2013',0x4A8B8,0x4A8BC),('0x2014',0x4A8C0,0x4A8C4)]:
 check(f'{did} start returns 5', 'return 5;' in by[start]['decompiled_c'])
 check(f'{did} result is no-op success', 'return 0;' in by[result]['decompiled_c'] and by[result]['body_size']==4)
check('2012 remains unconditional-start',w['h_2012_unconditional_start'] and by[0x4A89A]['body_size']==4)
check('2012 result still reaches target lifecycle helper','thunk_FUN_000b2b6e' in by[0x4A89E]['decompiled_c'])
check('0204 maintains pending 2E10 behavior','0x2e10' in by[0x4A686]['decompiled_c'])
check('WDBI request start maps to exact-size H 8EB7C',by[0x8EB7C]['body_size']==136)
check('WDBI callback maps to exact-size H 8EC88',by[0x8EC88]['body_size']==36)
check('session policy preserves session-2 speed gate',d['session']['policy']['requested_session_2_speed_gate'])
check('session request family maps all four lifecycle roles',len(d['session']['request_family'])==4)
check('RoutineControl generic helpers map all four roles',len(d['routine_control']['helpers'])==4)
check('request-start retains H RID count source',d['routine_control']['h_rid_count_source']=='DAT_00026376')
check('all 59 diagnostic residuals closed',d['static_conclusion']['all_59_diagnostic_residuals_closed'])
check('fake WDBI homologs explicitly rejected','fake homologs' in d['static_conclusion']['boundary'])
print(f'\nResults: {p} passed, {f} failed');raise SystemExit(1 if f else 0)
