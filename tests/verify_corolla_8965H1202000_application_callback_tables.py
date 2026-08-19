#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json,subprocess,sys,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];ART=ROOT/'data/generated/corolla_8965H1202000_application_callback_tables.json';TOOL=ROOT/'tools/build_corolla_h_application_callback_tables.py';SRAW=ROOT/'firmware/RH850_P1M-E_CodeFlash.bin';HRAW=ROOT/'community/albinoelephant/raw-20260818/albinoelephant-corolla-2023.20260814-0023/dump_codeflash_00000000_00200000_20260814-025814.bin'
p=f=0
def check(n,c):
 global p,f;ok=bool(c);p+=ok;f+=not ok;print(f"[{'PASS' if ok else 'FAIL'}][raw_bytes] {n}")
def sha(b):return hashlib.sha256(b).hexdigest()
with tempfile.TemporaryDirectory() as td:
 out=Path(td)/'x.json';subprocess.run([sys.executable,str(TOOL),'--out',str(out)],cwd=ROOT,check=True,stdout=subprocess.DEVNULL);check('report regenerates exactly',out.read_bytes()==ART.read_bytes())
d=json.loads(ART.read_text());S=SRAW.read_bytes();H=HRAW.read_bytes()[:0x100000]
check('image hashes pinned',d['images']['sienna_sha256']==sha(S) and d['images']['h_sha256']==sha(H))
c=d['command_table'];check('command tables are 18 entries',c['count']==18 and len(c['rows'])==18)
check('command-0 target anchor is unique raw pointer at H table base',c['anchor']['target']=='0x0007BD6C' and c['anchor']['h_pointer_occurrences']==['0x00022A74'])
check('H command table exact targets pinned',[r['h_target'] for r in c['rows']]==['0x0007BD6C','0x0007BD7E','0x0007BDDE','0x0007BDB2','0x0007BF72','0x0007BE2A','0x0007B30E','0x0007B3D4','0x0007BB90','0x0007B7C8','0x0007B820','0x0007B926','0x0007B9E6','0x0007BAC4','0x0007BC6C','0x0007BCAA','0x0007BC20','0x0007BCDE'])
check('17 named command IDs recovered',d['static_conclusion']['command_roles_recovered']==17 and sum('application_command_' in x['reference_name'] for x in d['role_closure'])==17)
o=d['async_operation_table'];check('canonical operation discriminators F3..FB',o['canonical_discriminators']==[f'0x{x:04X}' for x in range(0x6F3,0x6FC)])
check('H removes exactly F4/F5',o['removed_discriminators']==['0x06F4','0x06F5'] and o['h_discriminators']==['0x06F3','0x06F6','0x06F7','0x06F8','0x06F9','0x06FA','0x06FB'])
check('operation H callback pairs pinned',[(x['discriminator'],x['h']['start'],x['h']['completion']) for x in o['rows'] if x['status']=='preserved']==[('0x06F3','0x000307C2','0x000307E8'),('0x06F6','0x000307F6','0x00030842'),('0x06F7','0x0003089E','0x00030934'),('0x06F8','0x00030994','0x00030A52'),('0x06F9','0x00030AA6','0x00030ADC'),('0x06FA','0x00030AEE','0x00030B14'),('0x06FB','0x00030B22','0x00030B54'),('special-op9','0x00030B64','0x00030B7E')])
check('16 operation roles recovered and four removed',d['static_conclusion']['operation_roles_recovered']==16 and d['surface_recensus_count']==4)
check('33 direct roles + 4 recensuses close 37 names',d['role_closure_count']==33 and d['surface_recensus_count']==4)
check('all direct role targets are raw-config evidence',set(x['target_entry'] for x in d['role_closure'])<=set(d['target_evidence_entries']))
check('missing-row boundary explicit','does not prove' in d['static_conclusion']['boundary'])
print(f'\nResults: {p} passed, {f} failed');raise SystemExit(1 if f else 0)
