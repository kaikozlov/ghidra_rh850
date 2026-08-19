#!/usr/bin/env python3
"""Verify generated bounded-API, packet-selector, and record-operation adapter mappings."""
from __future__ import annotations
import hashlib,json,subprocess,sys,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];ART=ROOT/'data/generated/corolla_8965H1202000_small_adapters.json';EV=ROOT/'data/generated/corolla_8965H1202000_small_adapter_decompiler_evidence.json';TOOL=ROOT/'tools/build_corolla_h_small_adapters.py';RAW=ROOT/'community/albinoelephant/raw-20260818/albinoelephant-corolla-2023.20260814-0023/dump_codeflash_00000000_00200000_20260814-025814.bin'
p=f=0
def check(n,c):
 global p,f;ok=bool(c);p+=ok;f+=not ok;print(f"[{'PASS' if ok else 'FAIL'}][raw_bytes] {n}")
def sha(b):return hashlib.sha256(b).hexdigest()
with tempfile.TemporaryDirectory() as td:
 out=Path(td)/'x.json';subprocess.run([sys.executable,str(TOOL),'--out',str(out)],cwd=ROOT,check=True,stdout=subprocess.DEVNULL);check('report regenerates exactly',out.read_bytes()==ART.read_bytes())
d=json.loads(ART.read_text());e=json.loads(EV.read_text());raw=RAW.read_bytes()[:0x100000];by={int(r['entry'],16):r for r in e['functions']}
check('H image hash pinned',sha(raw)==e['image']['codeflash_sha256'])
check('18 H adapter functions compacted',e['function_count']==18)
check('all raw H bodies validate',all(sha(raw[int(r['entry'],16):int(r['entry'],16)+r['body_size']])==r['body_sha256'] for r in e['functions']))
check('all H decompiler hashes validate',all(sha(r['decompiled_c'].encode())==r['decompiled_c_sha256'] for r in e['functions']))
check('all 18 roles recovered',d['role_closure_count']==18 and d['static_conclusion']['all_18_roles_recovered'])
b=d['bounded_api'];check('six bounded wrappers relocate by -0x5C60',b['delta']==-0x5C60 and b['same_wrapper_sizes'])
check('H bounded pointer table is 21838',b['h_pointer_table']['base']=='0x00021838' and len(b['h_pointer_table']['values'])==6)
check('all six bounded target slots preserve -0x4FDA relocation',all(int(h,16)-int(s,16)==-0x4FDA for s,h in zip(b['sienna_pointer_table']['values'],b['h_pointer_table']['values'])))
pkt=d['packet_selector'];check('packet table has same 21 configured selector indices',pkt['configured_selectors_h']==pkt['configured_selectors_sienna'] and len(pkt['configured_selectors_h'])==21)
check('packet table maps to H 269FC',pkt['h_table_base']=='0x000269FC' and pkt['table_count']==44)
check('seven residual packet selector targets exact',pkt['mapped_target_checks'] and sorted(pkt['mapped_selectors'])==[6,15,16,22,38,39,43])
rec=d['record_operation'];check('record table maps 5x0x1C at H 25F28',rec['h_table_base']=='0x00025F28' and rec['record_count']==5 and rec['stride']==28)
check('five record callback words exact',rec['mapped_target_checks'] and rec['all_h_callbacks_48_bytes'])
check('target-specific payload boundary explicit','remain H-specific' in d['static_conclusion']['boundary'])
print(f'\nResults: {p} passed, {f} failed');raise SystemExit(1 if f else 0)
