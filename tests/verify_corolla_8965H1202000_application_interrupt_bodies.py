#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json,subprocess,sys,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];ART=ROOT/'data/generated/corolla_8965H1202000_application_interrupt_bodies.json';TOOL=ROOT/'tools/build_corolla_h_application_interrupt_bodies.py';EVID=ROOT/'data/generated/corolla_8965H1202000_application_interrupt_body_decompiler_evidence.json';HRAW=ROOT/'community/albinoelephant/raw-20260818/albinoelephant-corolla-2023.20260814-0023/dump_codeflash_00000000_00200000_20260814-025814.bin';p=f=0
def check(n,c):
 global p,f;ok=bool(c);p+=ok;f+=not ok;print(f"[{'PASS' if ok else 'FAIL'}][raw_bytes] {n}")
def sha(b):return hashlib.sha256(b).hexdigest()
with tempfile.TemporaryDirectory() as td:
 out=Path(td)/'x.json';subprocess.run([sys.executable,str(TOOL),'--out',str(out)],cwd=ROOT,check=True,stdout=subprocess.DEVNULL);check('report regenerates exactly',out.read_bytes()==ART.read_bytes())
d=json.loads(ART.read_text());e=json.loads(EVID.read_text());h=HRAW.read_bytes()[:0x100000]
check('seven evidence bodies raw-bound',len(e['functions'])==7 and all(sha(h[int(r['entry'],16):int(r['entry'],16)+r['body_size']])==r['body_sha256'] for r in e['functions']))
exp={'application_tauj0_ch0_body':'0x0005F258','application_tauj0_ch1_body':'0x0005F294','application_tauj0_ch2_body':'0x0005F2D0','application_can1_rx_interrupt_body':'0x0007D240','application_can1_tx_interrupt_body':'0x0007EB4E'}
check('five body roles exact',{x['reference_name']:x['target_entry'] for x in d['role_closure']}==exp)
chains={x['reference_name']:x['chain'] for x in d['rows']}
check('TAUJ bodies are direct wrapper children',chains['application_tauj0_ch0_body']==['0x0006A6C0','0x0005F258'] and chains['application_tauj0_ch1_body']==['0x0006A76A','0x0005F294'] and chains['application_tauj0_ch2_body']==['0x0006A816','0x0005F2D0'])
check('CAN1 bodies use one-hop thunks',chains['application_can1_rx_interrupt_body']==['0x0005F3AA','0x0005FB1E','0x0007D240'] and chains['application_can1_tx_interrupt_body']==['0x0005F368','0x0005FB12','0x0007EB4E'])
check('semantic boundary explicit','Deeper timer/ADC semantics are not transferred' in d['static_conclusion']['boundary'])
print(f'\nResults: {p} passed, {f} failed');raise SystemExit(1 if f else 0)
