#!/usr/bin/env python3
"""Verify target-native recovery of the final seven H crypto roles."""
from __future__ import annotations
import hashlib,json,subprocess,sys,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
ART=ROOT/'data/generated/corolla_8965H1202000_crypto_residue.json';EV=ROOT/'data/generated/corolla_8965H1202000_crypto_residue_decompiler_evidence.json';BUILD=ROOT/'tools/build_corolla_h_crypto_residue.py';HRAW=ROOT/'community/albinoelephant/raw-20260818/albinoelephant-corolla-2023.20260814-0023/dump_codeflash_00000000_00200000_20260814-025814.bin'
p=f=0
def sha(b):return hashlib.sha256(b).hexdigest()
def ck(n,c,d=''):
 global p,f
 ok=bool(c);p+=ok;f+=not ok;print(f"[{'PASS' if ok else 'FAIL'}][raw_bytes] {n}"+(f' ({d})' if d else ''))
a=json.loads(ART.read_text());e=json.loads(EV.read_text());H=HRAW.read_bytes()[:0x100000];by={int(x['target_entry'],16):x for x in e['functions']}
with tempfile.TemporaryDirectory() as td:
 out=Path(td)/'x.json';r=subprocess.run([sys.executable,str(BUILD),'--out',str(out)],cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True);ck('builder exits',r.returncode==0,r.stdout[-300:] if r.returncode else '');ck('report regenerates exactly',r.returncode==0 and out.read_bytes()==ART.read_bytes())
ck('H image hash pinned',sha(H)==e['image']['codeflash_sha256']==a['images']['h_sha256']);ck('seven crypto roles compacted',e['function_count']==7==len(e['functions'])==a['crypto_role_closure_count']);ck('all raw H bodies validate',all(sha(H[int(x['target_entry'],16):int(x['target_entry'],16)+x['target_reported_body_size']])==x['body_sha256'] for x in e['functions']));ck('all decompiler hashes validate',all(sha(x['decompiled_c'].encode())==x['decompiled_c_sha256'] for x in e['functions']))
exp={'0x000070FC':'0x000070E0','0x00068F0C':'0x00063244','0x00068F92':'0x000632CA','0x00068FC2':'0x000632FA','0x00069018':'0x00063350','0x00088302':'0x00082702','0x00088508':'0x00082908'};ck('all seven role mappings exact', {x['reference_entry']:x['target_entry'] for x in a['crypto_role_closure']}==exp)
pf=a['payload_crypto_finalize'];ck('payload finalize is exact 12-byte relocated wrapper',pf['exact_body_equal'] and pf['body_size']==12 and pf['h']=='0x000070E0');ck('payload finalize is role-bound by relocated clear call',pf['h_calls_clear'] and pf['clear_delta']==-0x1c and 'FUN_000070c8' in by[0x70e0]['decompiled_c'])
b=a['crypto_test_banks'];ck('bank0 preserves eight-counter snapshot',b['bank0']['snapshot']['h_counter_indices']==list(range(10,18)) and b['bank0']['snapshot']['sienna_counter_indices']==list(range(12,20)));ck('bank1 preserves five-counter snapshot',b['bank1']['snapshot']['h_counter_indices']==list(range(18,23)) and b['bank1']['snapshot']['sienna_counter_indices']==list(range(20,25)));ck('both H counter cohorts shift by -2',b['bank0']['index_shift']==[-2]*8 and b['bank1']['index_shift']==[-2]*5);ck('bank0 activation keeps active/state 0x11 lifecycle',all(t in by[0x632ca]['decompiled_c'] for t in ('cRamfebe4f82','uRamfebe4f83 = 0x11','FUN_00062214','FUN_0006224c(1)','direct_call_target_00063244')));ck('bank1 activation keeps active/state 0x11 lifecycle',all(t in by[0x63350]['decompiled_c'] for t in ('cRamfebe4f87','uRamfebe4f88 = 0x11','FUN_00062282','direct_call_target_000632fa')));ck('counter-number transfer is explicitly rejected','do not transfer Sienna counter numbers' in b['interpretation'])
dr=a['driver_record_lookup'];ck('generate driver lookup is two records stride 0x20',dr['generate']['h']=='0x00082702' and dr['generate']['record_count']==2 and dr['generate']['record_stride']==0x20 and '0x27c88' in by[0x82702]['decompiled_c']);ck('generic driver lookup is two records stride 0x20',dr['verify_generic']['h']=='0x00082908' and dr['verify_generic']['record_count']==2 and dr['verify_generic']['record_stride']==0x20 and '0x27ccc' in by[0x82908]['decompiled_c']);ck('driver lookup pair remains -0x5C00',dr['delta']==-0x5c00)
sc=a['static_conclusion'];ck('all seven crypto residual roles closed',sc['all_7_crypto_residual_roles_recovered'] and sc['crypto_named_residue_closed']);ck('target-specific generated-state boundary remains explicit','target-specific' in sc['boundary'])
print(f'\nResults: {p} passed, {f} failed');raise SystemExit(1 if f else 0)
