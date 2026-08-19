#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json,struct,subprocess,sys,tempfile
from pathlib import Path
REPO=Path(__file__).resolve().parents[1]; FW=(REPO/'firmware/RH850_P1M-E_CodeFlash.bin').read_bytes(); OUT=REPO/'data/generated/sienna_8965B4512000_techstream_did_semantics.json'
p=f=0; oracle='raw_bytes'
def check(n,c,d=''):
 global p,f
 ok=bool(c);p+=ok;f+=not ok;print(f"[{'PASS' if ok else 'FAIL'}][{oracle}] {n}"+(f' ({d})' if d else ''))
obj=json.loads(OUT.read_text()); rows={int(x['did'],16):x for x in obj['dids']}
print('== exact Sienna DID table ==')
D=struct.Struct('<HHIII'); dids={}
for i in range(0xF2):
 d,l,cb,a1,a2=D.unpack_from(FW,0x2941c+i*16); dids[d]=(l,cb,a1,a2)
expect={0x1151:0x4d71c,0x1152:0x4d758,0x1153:0x4d794,0x1154:0x4d7d0,0x1155:0x4d80c,0x1156:0x4d856,0x1185:0x4d930,0x1c02:0x4db5e}
check('eight observer DIDs map to exact callbacks',{d:dids[d][1] for d in expect}==expect)
check('all eight are declared 2-byte RDBI values',all(dids[d][0]==2 for d in expect))
print('\n== callback/supporting body identities ==')
for x in obj['dids']:
 a=int(x['callback'],16); check(f"{x['did']} callback body identity",hashlib.sha256(FW[a:a+x['size']]).hexdigest()==x['callback_sha256'])
for x in obj['supporting_functions']:
 a=int(x['address'],16); check(f"{x['role']} body identity",hashlib.sha256(FW[a:a+x['size']]).hexdigest()==x['sha256'])
print('\n== exact Techstream Data-ID vocabulary ==')
h=json.loads((REPO/'data/generated/corolla_8965H1202000_techstream_correlations.json').read_text())
known={}
for family in ('emps_p5','emps2_p5'):
 for r in h['ddb_overlap'][family]['monitor_rows']:
  known.setdefault(r['primary_data_id'].lower(),set()).add(r['name'])
for x in obj['dids']:
 did=x['did'].lower(); check(f"{x['did']} Techstream primary Data ID/name exact",x['techstream_name'] in known.get(did,set()),repr(known.get(did)))
print('\n== target-native chain semantics ==')
# These are direct decompiler-corpus statements whose function bodies are independently SHA-pinned above.
code={}
for line in (REPO/'data/generated/decompilations.jsonl').open():
 r=json.loads(line)
 if r.get('entry_addr') and r.get('decompiled_c'):
  code[r['entry_addr'].lower()]=r['decompiled_c']
checks=[
('Q/D feedback combine','0x00037644','DAT_febe6d18 =','DAT_febe6d1a ='),
('Q/D command reference','0x00037712','DAT_febe6d2c = DAT_febe6d7e','DAT_febe6d2e = DAT_febe6d70'),
('RTE diagnostic staging','0x0005c0b6','DAT_febe66e6 = DAT_febe6d1a','DAT_febe66fc = DAT_febe6d2c','DAT_febe66e4 = DAT_febe6d18','DAT_febe66fe = DAT_febe6d2e'),
('command torque snapshot','0x000bcace','DAT_febee40a = DAT_febeac56'),
('command torque state','0x000cb454','DAT_febeac56 = DAT_febec1d2'),
('Q current limit snapshot','0x000bca88','DAT_febee608 = DAT_febeaf40'),
]
for name,a,*needles in checks: check(name,all(n in code.get(a,'') for n in needles))
check('1C02 remains general internal torque observer','general internal command-value torque' in obj['boundary'])
print('\n== regeneration ==')
with tempfile.TemporaryDirectory() as td:
 out=Path(td)/'x.json'; r=subprocess.run([sys.executable,str(REPO/'tools/techstream/generate_sienna_techstream_did_semantics.py'),'--output',str(out)],check=False)
 check('generator exits',r.returncode==0);check('byte-identical regeneration',out.read_bytes()==OUT.read_bytes())
print(f'\nResults: {p} passed, {f} failed');raise SystemExit(1 if f else 0)
