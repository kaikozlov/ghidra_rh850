#!/usr/bin/env python3
"""Verify complete target-surface closure of Corolla-H deadline-monitor callbacks."""
from __future__ import annotations
import hashlib,json,subprocess,sys,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];ART=ROOT/'data/generated/corolla_8965H1202000_deadline_monitor_surface.json';EV=ROOT/'data/generated/corolla_8965H1202000_deadline_monitor_surface_decompiler_evidence.json';TOOL=ROOT/'tools/build_corolla_h_deadline_monitor_surface.py';RAW=ROOT/'community/albinoelephant/raw-20260818/albinoelephant-corolla-2023.20260814-0023/dump_codeflash_00000000_00200000_20260814-025814.bin'
p=f=0
def check(n,c):
 global p,f;ok=bool(c);p+=ok;f+=not ok;print(f"[{'PASS' if ok else 'FAIL'}][raw_bytes] {n}")
def sha(b):return hashlib.sha256(b).hexdigest()
with tempfile.TemporaryDirectory() as td:
 out=Path(td)/'x.json';subprocess.run([sys.executable,str(TOOL),'--out',str(out)],cwd=ROOT,check=True,stdout=subprocess.DEVNULL);check('report regenerates exactly',out.read_bytes()==ART.read_bytes())
d=json.loads(ART.read_text());e=json.loads(EV.read_text());raw=RAW.read_bytes()[:0x100000]
check('H image hash pinned',sha(raw)==e['image']['codeflash_sha256'])
check('91 H functions compacted: 88 callbacks + 3 support',e['function_count']==91 and e['callback_count']==88 and e['support_count']==3)
check('all raw H bodies validate',all(sha(raw[int(r['entry'],16):int(r['entry'],16)+r['body_size']])==r['body_sha256'] for r in e['functions']))
check('all decompiler hashes validate',all(sha(r['decompiled_c'].encode())==r['decompiled_c_sha256'] for r in e['functions']))
check('simple dispatcher maps 6962A->639CA at 138 bytes',d['dispatchers']['simple']=={'sienna':'0x0006962A','h':'0x000639CA','body_size':138,'unique_exact_instruction_shape':True})
check('variant-D dispatcher maps 6A28A->6462A at 1208 bytes',d['dispatchers']['variant_d']=={'sienna':'0x0006A28A','h':'0x0006462A','body_size':1208,'unique_exact_instruction_shape':True})
check('simple setup maps to H 387E4 and table 280E8',d['dispatchers']['simple_setup']['h']=='0x000387E4' and d['dispatchers']['simple_setup']['h_table']=='0x000280E8')
ht={x['name']:x for x in d['h_tables']};st={x['name']:x for x in d['sienna_tables']}
check('H variant-D A table base 280B4',ht['variant_d_a']['base']=='0x000280B4')
check('H simple table base 280E8',ht['simple']['base']=='0x000280E8')
check('H variant-D B table base 28260',ht['variant_d_b']['base']=='0x00028260')
check('S/H table row/stride shapes are identical',d['summary']['same_table_shapes'])
check('S/H per-table unique callback counts are 3/82/3',d['summary']['same_per_table_unique_counts'] and [ht[x]['unique_callbacks'] for x in ('variant_d_a','simple','variant_d_b')]==[3,82,3])
check('H simple table has 83 nonzero slots / 82 unique',ht['simple']['nonzero_slots']==83 and ht['simple']['unique_callbacks']==82)
check('H variant A has 3 nonzero / 3 unique',ht['variant_d_a']['nonzero_slots']==3 and ht['variant_d_a']['unique_callbacks']==3)
check('H variant B has 4 nonzero / 3 unique',ht['variant_d_b']['nonzero_slots']==4 and ht['variant_d_b']['unique_callbacks']==3)
check('both images have 88-callback union',d['summary']['sienna_unique_callback_union']==88==d['summary']['h_unique_callback_union'])
check('simple final row preserves duplicate-start/null-third shape',ht['simple']['rows'][-1][0]==ht['simple']['rows'][-1][1] and ht['simple']['rows'][-1][2] is None)
check('all 88 canonical deadline names are recensused',d['surface_recensus_count']==88 and d['summary']['all_88_named_deadline_residuals_closed'])
check('no one-to-one callback naming is claimed','not assigned Sienna callback names one-to-one' in d['summary']['boundary'])
print(f'\nResults: {p} passed, {f} failed');raise SystemExit(1 if f else 0)
