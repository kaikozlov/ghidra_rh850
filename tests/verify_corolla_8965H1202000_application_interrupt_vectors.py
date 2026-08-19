#!/usr/bin/env python3
from __future__ import annotations
import json,subprocess,sys,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];ART=ROOT/'data/generated/corolla_8965H1202000_application_interrupt_vectors.json';TOOL=ROOT/'tools/build_corolla_h_application_interrupt_vectors.py';p=f=0
def check(n,c):
 global p,f;ok=bool(c);p+=ok;f+=not ok;print(f"[{'PASS' if ok else 'FAIL'}][raw_bytes] {n}")
with tempfile.TemporaryDirectory() as td:
 out=Path(td)/'x.json';subprocess.run([sys.executable,str(TOOL),'--out',str(out)],cwd=ROOT,check=True,stdout=subprocess.DEVNULL);check('report regenerates exactly',out.read_bytes()==ART.read_bytes())
d=json.loads(ART.read_text());check('EIINT table is 384 entries at 20200',d['table']['base']=='0x00020200' and d['table']['count']==384)
exp={8:'0x0006ADF4',133:'0x0006A6C0',134:'0x0006A76A',135:'0x0006A816',187:'0x0005F3AA',188:'0x0005F368',379:'0x0005F470'}
check('seven channel targets exact',{x['channel']:x['h_target'] for x in d['rows']}==exp)
check('all seven roles recovered',d['role_closure_count']==7 and d['static_conclusion']['seven_unresolved_wrappers_recovered'])
check('target evidence is exactly vector entries',set(d['target_evidence_entries'])==set(exp.values()))
check('internal semantic boundary explicit','internals' in d['static_conclusion']['boundary'])
print(f'\nResults: {p} passed, {f} failed');raise SystemExit(1 if f else 0)
