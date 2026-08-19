#!/usr/bin/env python3
"""Verify the H generated-COM -> steering-supervisor ingress census."""
from __future__ import annotations
import hashlib,json
from pathlib import Path
REPO=Path(__file__).resolve().parents[1]
ART=REPO/'data/generated/corolla_8965H1202000_supervisor_external_ingress_census.json'
HRAW=REPO/'community/albinoelephant/raw-20260818/albinoelephant-corolla-2023.20260814-0023/dump_codeflash_00000000_00200000_20260814-025814.bin'
SIMG=REPO/'firmware/RH850_P1M-E_CodeFlash.bin'
passed=failed=0
def sha(b):return hashlib.sha256(b).hexdigest()
def check(name,cond,detail=''):
 global passed,failed
 ok=bool(cond);passed+=int(ok);failed+=int(not ok);s=f' ({detail})' if detail else ''
 print(f"[{'PASS' if ok else 'FAIL'}][raw_bytes] {name}{s}")
hsrc=HRAW.read_bytes();h=hsrc[:0x100000];s=SIMG.read_bytes();d=json.loads(ART.read_text())
print('== image/corpus evidence boundary ==')
check('H normalized image hash is pinned',sha(h)==d['images']['corolla_h_sha256'])
check('Sienna image hash is pinned',sha(s)==d['images']['sienna_sha256'])
check('census explicitly bounds computed/opaque flows','computed-pointer' in d['evidence_boundary'] or 'opaque' in d['evidence_boundary'])
check('H COM data-offset table is recovered',d['summary']['h_offset_table']=='0x22788')
check('S COM data-offset table is uniquely recovered in generated-data region',0x22000 <= int(d['summary']['s_offset_table'],16) < 0x23000)
print('\n== exact consumer binding ==')
check('census contains external supervisor references',len(d['external_refs'])>0)
all_hash=True
all_unpack=True
for row in d['external_refs']:
 entry=row['consumer']; size=row['consumer_body_size']
 all_hash &= sha(h[entry:entry+size])==row['consumer_body_sha256']
 for u in row['source_unpackers']:
  all_unpack &= sha(h[u['entry']:u['entry']+u['body_size']])==u['body_sha256']
check('every cited consumer raw-body hash validates',all_hash)
check('every cited source-unpacker raw-body hash validates',all_unpack)
print('\n== replacement-command closure ==')
check('no H-only/wire-changed >=12-bit supervisor scalar remains',d['potential_changed_large_fields']==[])
changed=[x for x in d['external_refs'] if x['wire_class']!='shared_wire_field']
check('all H-only/wire-changed supervisor fields are from B6',bool(changed) and all(x['can']==0xB6 for x in changed))
check('no non-B6 changed wire field reaches mapped supervisor cone',not [x for x in changed if x['can']!=0xB6])
check('B6 signed16 signal255 never reaches mapped supervisor cone',not [x for x in d['external_refs'] if x['signal']==255])
active_b6={x['signal'] for x in changed if x['can']==0xB6}
check('exact directly referenced B6 supervisor field set is pinned',active_b6 == {258,260,261,262,263,264})
check('B6 changed fields are all sub-12-bit',all(x['bits']<12 for x in changed))
print('\n== shared-CAN boundary ==')
shared_nonb6=[x for x in d['external_refs'] if x['can']!=0xB6]
check('non-B6 external supervisor refs are same-wire fields on Sienna',bool(shared_nonb6) and all(x['wire_class']=='shared_wire_field' for x in shared_nonb6))
check('shared FD025 cannot become an H-only wire-field source',all(x['wire_class']=='shared_wire_field' for x in d['external_refs'] if x['can']==0x25))
check('census walks a nontrivial H supervisor call cone',d['summary']['h_cone_functions']>100)
check('census tracks nontrivial generated COM staging/snapshot state',d['summary']['h_com_stage_cells']>20 and d['summary']['h_com_snapshot_cells']>20)
print(f'\nResults: {passed} passed, {failed} failed')
raise SystemExit(1 if failed else 0)
