#!/usr/bin/env python3
"""Verify the target-native nine-channel plausibility-monitor mapping."""
from __future__ import annotations
import hashlib,json,subprocess,sys,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];ART=ROOT/'data/generated/corolla_8965H1202000_plausibility_monitor.json';EV=ROOT/'data/generated/corolla_8965H1202000_plausibility_monitor_decompiler_evidence.json';TOOL=ROOT/'tools/build_corolla_h_plausibility_monitor.py';RAW=ROOT/'community/albinoelephant/raw-20260818/albinoelephant-corolla-2023.20260814-0023/dump_codeflash_00000000_00200000_20260814-025814.bin'
p=f=0
def check(n,c):
 global p,f;ok=bool(c);p+=ok;f+=not ok;print(f"[{'PASS' if ok else 'FAIL'}][raw_bytes] {n}")
def sha(b):return hashlib.sha256(b).hexdigest()
with tempfile.TemporaryDirectory() as td:
 out=Path(td)/'x.json';subprocess.run([sys.executable,str(TOOL),'--out',str(out)],cwd=ROOT,check=True,stdout=subprocess.DEVNULL);check('report regenerates exactly',out.read_bytes()==ART.read_bytes())
d=json.loads(ART.read_text());e=json.loads(EV.read_text());raw=RAW.read_bytes()[:0x100000];by={int(r['entry'],16):r for r in e['functions']}
check('H image hash pinned',sha(raw)==e['image']['codeflash_sha256'])
check('12 H functions compacted',e['function_count']==12)
check('all raw H bodies validate',all(sha(raw[int(r['entry'],16):int(r['entry'],16)+r['body_size']])==r['body_sha256'] for r in e['functions']))
check('all H decompiler hashes validate',all(sha(r['decompiled_c'].encode())==r['decompiled_c_sha256'] for r in e['functions']))
check('all 11 named roles recovered',d['role_closure_count']==11 and d['static_conclusion']['all_11_roles_recovered'])
check('nine channels mapped',len(d['channels'])==9)
check('all channel tables shift by -0x470',d['static_conclusion']['all_channel_table_deltas_minus_0x470'] and all(c['table_delta']==-0x470 for c in d['channels']))
check('status permutation preserved',d['status_index_order']==[7,8,3,4,0,1,2,5,6] and d['static_conclusion']['status_index_permutation_preserved'])
check('each H channel calls common status publisher',all('FUN_0003eccc' in by[int(c['h'],16)]['decompiled_c'] for c in d['channels']))
check('publisher maps to H 3ECCC',d['publisher']['h']=='0x0003ECCC' and d['publisher']['both_body_size_18'] and d['publisher']['h_bound']==9)
check('H publisher vector base is FEBE76EC','febe76ec' in by[0x3ECCC]['decompiled_c'].lower())
check('aggregate maps 436->484',d['aggregate']['size_change']==[436,484] and d['aggregate']['h']=='0x0003EAE8')
check('H aggregate adds status publication',d['aggregate']['h_adds_status_publication'] and 'FUN_00047484(1,' in by[0x3EAE8]['decompiled_c'])
check('owner group-B ordering preserved',d['owner_dispatch']['h']=='0x00058450' and d['owner_dispatch']['channel_call_order_h']==['0x0003E5DC','0x0003E7CC','0x0003E87A','0x0003E27C','0x0003E42C','0x0003E928','0x0003EA16','0x0003E118','0x0003E1CA','0x0003EAE8'])
check('target-specific boundary explicit','remain target-specific' in d['static_conclusion']['boundary'])
print(f'\nResults: {p} passed, {f} failed');raise SystemExit(1 if f else 0)
