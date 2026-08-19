#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
ART=ROOT/'data/generated/corolla_8965H1202000_structural_residue_decompiler_evidence.json'
STRUCT=ROOT/'data/generated/corolla_8965H1202000_structural_function_transfer.json'
HRAW=ROOT/'community/albinoelephant/raw-20260818/albinoelephant-corolla-2023.20260814-0023/dump_codeflash_00000000_00200000_20260814-025814.bin'
p=f=0
def check(n,c):
 global p,f;ok=bool(c);p+=ok;f+=not ok;print(f"[{'PASS' if ok else 'FAIL'}][raw_bytes] {n}")
def sha(b):return hashlib.sha256(b).hexdigest()
d=json.loads(ART.read_text());st=json.loads(STRUCT.read_text());h=HRAW.read_bytes()[:0x100000]
check('software/image identity pinned',d['software_id']=='8965H1202000' and d['image']['codeflash_sha256']==sha(h))
check('exactly 96 inspected candidates',d['function_count']==96 and len(d['functions'])==96)
check('reference and target entries are each unique',len({x['reference_entry'] for x in d['functions']})==96 and len({x['entry'] for x in d['functions']})==96)
check('all H bodies raw-bound',all(sha(h[int(x['entry'],16):int(x['entry'],16)+x['body_size']])==x['body_sha256'] for x in d['functions']))
check('all decompiler payloads hash-bind',all(sha(x['decompiled_c'].encode())==x['decompiled_c_sha256'] and x['decompiled_c'] for x in d['functions']))
sm={int(x['reference_entry'],16):x for x in st['matches']}
check('every inspected pair is the structural artifact target',all(int(x['reference_entry'],16) in sm and int(x['entry'],16)==int(sm[int(x['reference_entry'],16)]['target_entry'],16) for x in d['functions']))
check('every inspected pair is unique-exact-shape',all(sm[int(x['reference_entry'],16)]['classification']=='unique-exact-shape' for x in d['functions']))
check('all structural body sizes agree with target evidence',all(int(sm[int(x['reference_entry'],16)]['body_size_target'])==x['body_size'] for x in d['functions']))
check('inspection boundary explicitly avoids semantic homology','does not assert semantic-role' in d['static_conclusion']['boundary'])
print(f'\nResults: {p} passed, {f} failed');raise SystemExit(1 if f else 0)
