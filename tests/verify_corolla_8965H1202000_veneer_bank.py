#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json,subprocess,sys,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; ART=ROOT/'data/generated/corolla_8965H1202000_veneer_bank.json'; TOOL=ROOT/'tools/build_corolla_h_veneer_bank.py'; SRAW=ROOT/'firmware/RH850_P1M-E_CodeFlash.bin'; HRAW=ROOT/'community/albinoelephant/raw-20260818/albinoelephant-corolla-2023.20260814-0023/dump_codeflash_00000000_00200000_20260814-025814.bin'
p=f=0
def check(n,c):
 global p,f;ok=bool(c);p+=ok;f+=not ok;print(f"[{'PASS' if ok else 'FAIL'}][raw_bytes] {n}")
def sha(b): return hashlib.sha256(b).hexdigest()
with tempfile.TemporaryDirectory() as td:
 out=Path(td)/'x.json';subprocess.run([sys.executable,str(TOOL),'--out',str(out)],cwd=ROOT,check=True,stdout=subprocess.DEVNULL);check('report regenerates exactly',out.read_bytes()==ART.read_bytes())
d=json.loads(ART.read_text());S=SRAW.read_bytes();H=HRAW.read_bytes()[:0x100000]
check('image hashes pinned',d['images']['sienna_sha256']==sha(S) and d['images']['h_sha256']==sha(H))
b=d['bank'];check('fixed bank is 60 slots at 0x14 stride',b['slot_count']==60 and b['stride']==0x14 and b['start']=='0x000FDE08' and b['end']=='0x000FE2A4')
check('veneer cardinality is 44 S / 38 H / 36 common',b['sienna_veneer_count']==44 and b['h_veneer_count']==38 and b['common_veneer_slots']==36)
check('full-bank removal set pinned',b['removed_slots']==['0x000FE164','0x000FE1B4','0x000FE1C8','0x000FE1F0','0x000FE204','0x000FE218','0x000FE22C','0x000FE2A4'])
check('full-bank addition set pinned',b['added_slots']==['0x000FE178','0x000FE18C'])
check('all recorded veneer raw bytes have call/return signature',all((x[side]['kind']!='veneer' or (bytes.fromhex(x[side]['raw8'])[:2]==b'\x2c\x06' and bytes.fromhex(x[side]['raw8'])[6:8]==b'\x6c\x00')) for x in b['slots'] for side in ('sienna','h')))
pairs=d['unresolved_pair_census'];check('11 canonical unresolved veneer pairs censused',len(pairs)==11)
check('six preserved and five removed unresolved pairs',d['static_conclusion']['preserved_unresolved_pairs']==6 and d['static_conclusion']['removed_unresolved_pairs']==5)
check('preserved H target set pinned',[(x['slot'],x['h_target']) for x in pairs if x['status']=='preserved-slot']==[('0x000FDEA8','0x000B6556'),('0x000FE074','0x000B4882'),('0x000FE088','0x000B4886'),('0x000FE0B0','0x000B5364'),('0x000FE1A0','0x000B1F4A'),('0x000FE1DC','0x000B1F5A')])
check('removed unresolved slots are literal fill',all(bytes.fromhex(x['h_raw8'])==bytes.fromhex('4000400040004000') for x in pairs if x['status']=='removed-slot'))
check('12 direct roles + 10 recensus rows close 22 names',d['role_closure_count']==12 and d['surface_recensus_count']==10 and d['role_closure_count']+d['surface_recensus_count']==22)
check('role targets are represented by raw veneer evidence',set(x['target_entry'] for x in d['role_closure']) <= set(d['target_evidence_entries']))
check('removed low-role boundary is explicit','does not prove' in d['static_conclusion']['boundary'])
print(f'\nResults: {p} passed, {f} failed');raise SystemExit(1 if f else 0)
