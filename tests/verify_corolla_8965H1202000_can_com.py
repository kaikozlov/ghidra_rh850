#!/usr/bin/env python3
"""Verify Corolla H changed CAN/COM role recovery and configured routing."""
from __future__ import annotations
import hashlib,json,struct,subprocess,sys,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
ART=ROOT/'data/generated/corolla_8965H1202000_can_com.json';EV=ROOT/'data/generated/corolla_8965H1202000_can_com_decompiler_evidence.json';BUILD=ROOT/'tools/build_corolla_h_can_com.py'
HRAW=ROOT/'community/albinoelephant/raw-20260818/albinoelephant-corolla-2023.20260814-0023/dump_codeflash_00000000_00200000_20260814-025814.bin';SIMG=ROOT/'firmware/RH850_P1M-E_CodeFlash.bin'
p=f=0
def sha(b):return hashlib.sha256(b).hexdigest()
def ck(n,c,d=''):
 global p,f
 ok=bool(c);p+=ok;f+=not ok;print(f"[{'PASS' if ok else 'FAIL'}][raw_bytes] {n}"+(f' ({d})' if d else ''))
a=json.loads(ART.read_text());e=json.loads(EV.read_text());H=HRAW.read_bytes()[:0x100000];S=SIMG.read_bytes()
print('== deterministic artifact ==')
with tempfile.TemporaryDirectory() as td:
 out=Path(td)/'x.json';r=subprocess.run([sys.executable,str(BUILD),'--out',str(out)],cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
 ck('builder exits',r.returncode==0,r.stdout[-400:] if r.returncode else '');ck('report regenerates exactly',r.returncode==0 and out.read_bytes()==ART.read_bytes())
print('\n== compact evidence ==')
ck('H image hash pinned',sha(H)==e['image']['codeflash_sha256']==a['images']['h_sha256']);ck('19 H functions compacted',e['function_count']==19==len(e['functions']))
ck('all raw H bodies validate',all(sha(H[int(x['entry'],16):int(x['entry'],16)+x['body_size']])==x['body_sha256'] for x in e['functions']))
ck('all H decompiler hashes validate',all(sha(x['decompiled_c'].encode())==x['decompiled_c_sha256'] for x in e['functions']))
print('\n== nine role mappings ==')
exp={'0x0005D3CE':'0x00058450','0x0005DB6E':'0x00058BBC','0x00069DEC':'0x0006418C','0x0007C640':'0x00076A3C','0x0007E30C':'0x00078708','0x0007E5F2':'0x000789EE','0x0007F002':'0x000793FE','0x00080992':'0x0007AD8E','0x00084710':'0x0007EB10'}
ck('all nine changed can_com roles recovered',a['can_com_role_closure_count']==9 and {x['reference_entry']:x['target_entry'] for x in a['can_com_role_closure']}==exp)
g=a['rx_dispatch_groups'];ck('group B guard schedule is identical 29/29',g['group_b']['sienna_guard_count']==g['group_b']['h_guard_count']==29 and g['group_b']['guard_diff']==[])
ck('group A is 97->96 with one nested guard deletion',g['group_a']['sienna_guard_count']==97 and g['group_a']['h_guard_count']==96 and len(g['group_a']['guard_diff'])==1 and g['group_a']['guard_diff'][0]['sienna']==['if (uVar != 0) {'] and g['group_a']['guard_diff'][0]['h']==[])
d=a['deadline_monitor_c'];ck('deadline monitor body is exact at active H 6418C',d['exact_body_equal'] and H[0x6418C:0x6462A]==S[0x69DEC:0x6A28A])
ck('deadline body ambiguity is explicit',d['h_exact_body_occurrences']==['0x0006418C','0x000CF27E'])
ck('active H monitor caller disambiguates 6418C',d['active_h_caller']=='0x0003E118' and d['active_h_caller_invokes_6418c'])
print('\n== configured transport table proofs ==')
for row in a['configuration_pointer_proofs']:
 sa=int(row['sienna_pointer_at'],16);ha=int(row['h_pointer_at'],16)
 ck('table '+row['role'],struct.unpack_from('<I',S,sa)[0]==int(row['sienna_target'],16) and struct.unpack_from('<I',H,ha)[0]==int(row['h_target'],16))
by={int(x['entry'],16):x for x in e['functions']}
ck('H COM RxIndication retains full 212-byte copy/filter/timeout body',by[0x76A3C]['body_size']==212 and all(t in by[0x76A3C]['decompiled_c'] for t in ('& 0x10','& 8','& 4','*pbVar1 = *pbVar1 & 0xdc','FUN_00087a82(param_1)')))
ck('H PduR COM transmit wrapper remains 26 bytes',by[0x7AD8E]['body_size']==26 and 'PTR_LAB_00021c70' in by[0x7AD8E]['decompiled_c'])
ck('H CanIf Tx-ID class decoder retains six classes',all(t in by[0x789EE]['decompiled_c'] for t in ('0x6000','0x800','0xb800','0xc000','0xf800')))
ck('H CanIf Tx confirmation retains six class dispatch',all(t in by[0x793FE]['decompiled_c'] for t in ('0x6000','0x800','0xb800','0xc000','0xf800')))
ck('H RSCFD confirmation is called by Tx interrupt body', 'FUN_0007eb10' in by[0x7EB4E]['decompiled_c'])
ck('H normal Rx demux terminates at PduR route adapter', 'FUN_0007b026' in by[0x7A402]['decompiled_c'] and struct.unpack_from('<I',H,0x21C90)[0]==0x7B040)
ck('report keeps PDU membership in separate topology owner','individual PDU membership' in a['static_conclusion']['boundary'])
print(f'\nResults: {p} passed, {f} failed');raise SystemExit(1 if f else 0)
