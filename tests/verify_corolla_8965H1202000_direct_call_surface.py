#!/usr/bin/env python3
from __future__ import annotations
import csv,hashlib,json,subprocess,sys,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];EVID=ROOT/'data/generated/corolla_8965H1202000_direct_call_surface_evidence.json';ART=ROOT/'data/generated/corolla_8965H1202000_direct_call_surface.json';TOOL=ROOT/'tools/build_corolla_h_direct_call_surface.py';HRAW=ROOT/'community/albinoelephant/raw-20260818/albinoelephant-corolla-2023.20260814-0023/dump_codeflash_00000000_00200000_20260814-025814.bin';LEDGER=ROOT/'data/semantic_coverage_ledger.csv';p=f=0
def check(n,c):
 global p,f;ok=bool(c);p+=ok;f+=not ok;print(f"[{'PASS' if ok else 'FAIL'}][raw_bytes] {n}")
def sha(b):return hashlib.sha256(b).hexdigest()
with tempfile.TemporaryDirectory() as td:
 out=Path(td)/'x.json';subprocess.run([sys.executable,str(TOOL),'--out',str(out)],cwd=ROOT,check=True,stdout=subprocess.DEVNULL);check('summary report regenerates exactly',out.read_bytes()==ART.read_bytes())
e=json.loads(EVID.read_text());d=json.loads(ART.read_text());h=HRAW.read_bytes()[:0x100000]
check('evidence image hash pinned',e['image']['codeflash_sha256']==sha(h))
check('clean H corpus cardinality pinned',e['summary']['function_count']==5425 and e['summary']['instruction_count']==159192)
check('all 5425 raw contiguous bodies validate',all(sha(h[int(r['entry'],16):int(r['entry'],16)+r['body_size']])==r['body_sha256'] for r in e['functions']))
entries={int(r['entry'],16) for r in e['functions']};edges=[int(t,16) for r in e['functions'] for t in r['direct_call_targets']]
check('literal-call edge/target counts pinned',len(edges)==9509 and len(set(edges))==5151)
check('all in-image literal call targets resolve to clean H function entries',all(t>0xfffff or t in entries for t in edges) and e['summary']['missing_in_image_literal_call_targets']==[] and e['summary']['closed'])
rows=list(csv.DictReader(LEDGER.open()));seeds=[r for r in rows if r['name'].startswith('direct_call_target_') and r['discovery_source']=='direct-call seed' and r['discovery_provenance']=='SeedDirectCallTargets.java']
check('canonical direct-call-seed provenance cohort is exactly 153',len(seeds)==153 and d['canonical_direct_call_seed_count']==153)
check('recensus covers exactly the canonical generic seed names',{x['reference_name'] for x in d['surface_recensus']}=={r['name'] for r in seeds})
check('provenance-only boundary explicit','not semantic identity' in d['static_conclusion']['boundary'] and 'no one-to-one behavior' in d['static_conclusion']['boundary'])
print(f'\nResults: {p} passed, {f} failed');raise SystemExit(1 if f else 0)
