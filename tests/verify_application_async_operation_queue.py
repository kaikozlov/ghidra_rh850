#!/usr/bin/env python3
"""Verify the five-operation application async queue and its service ownership."""
from __future__ import annotations
import hashlib, json, struct
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
CF=(ROOT/'firmware/RH850_P1M-E_CodeFlash.bin').read_bytes()
CORPUS=ROOT/'data/generated/decompilations.jsonl'
passed=failed=0

def check(name, cond, detail=''):
 global passed,failed
 ok=bool(cond); passed+=int(ok); failed+=int(not ok)
 print(f"[{'PASS' if ok else 'FAIL'}] {name}" + (f" ({detail})" if detail else ''))

def sha(a,n): return hashlib.sha256(CF[a:a+n]).hexdigest()
def branch(addr):
 w0,w1=struct.unpack_from('<HH',CF,addr)
 if ((w0>>6)&0x1f)!=0x1e or (w1&1): return None
 reg2=(w0>>11)&0x1f; hi=w0&0x3f
 if hi&0x20: hi-=0x40
 return ('jarl' if reg2 else 'jr',addr+(hi<<16)+w1)

records={}
for line in CORPUS.open():
 r=json.loads(line)
 if r.get('record')=='function': records[int(r['entry_addr'],16)]=r

def refs(a): return {(x.get('to_addr'),x.get('ref_type')) for x in records[a].get('data_references',[])}
print('\n== queue core bodies ==')
expected_hashes={
 0x50596:(32,'2191cf542bfd8076d4c3f059c99f157ddd4959b90f82402fea55a365664c34cc'),
 0x50660:(56,'f85d9c7e028e19c53886d2f31b5447e9d6bc15934e2d167ac1bb3d2b20cd37db'),
 0x50698:(116,'4a6dde2acd26024bb9c97bcb9fe628b150aeabb92e5d4a8c1b8d9dd96f56cfe5'),
 0x50760:(138,'a25cabafa8560267791181e7444f2b8e420553a6a26a321c63e73242cbde9d9d'),
 0x507EA:(110,'782e3ad62cea114bded3abd421a942e176f9d336d1e0276c9dde9c1031c27122'),
 0x50864:(130,'8d3a5182469e6ca6eef870cc3589cd82470b0494826ae8b7e09373d4b73f06f0'),
 0x50922:(116,'72008c7894efd52ba593be71718a362347ac7d8dd9081211572bc997ea7f5b64'),
 0x50996:(134,'8d379447351da965245bb09190b912571cc751ce6cc34e8420e50d5b1864e6df'),
 0x50A1C:(204,'89683a882b55a0255bf1e379ac3ad1c18c7e4d377bad600a711e1258a0159dbb'),
 0x4C430:(68,'2d869b6cbc19d6eecddd5c1d1fe408f88646282e908848ff39f79b9a22975024'),
 0x4C474:(48,'cd13e47fa59cfbd55ef3faee25d846ed3621904496b552a98d881d70954bcb50'),
 0x4C9C6:(68,'88392041b92100673411912fb2c1d7567a1cea057628a67c1cb3657a6e897400'),
 0x35658:(136,'1dee8942ea79edb1a9476877e492ea6f0f1f10b16c945a66688c206d38c625b2'),
}
for a,(n,h) in expected_hashes.items(): check(f'{a:06X} body pinned',sha(a,n)==h)

print('\n== starter state numbers prove no operation 3 ==')
# Each starter writes its operation number while idle and then ORs the active bit.
starters=[
 (1,0x50698,0x506A4,0x506A6,0x506AE),
 (2,0x50760,0x5076C,0x5076E,0x50776),
 (4,0x507EA,0x507F6,0x507F8,0x50800),
 (5,0x50864,0x50870,0x50872,0x5087A),
 (6,0x50922,0x5092E,0x50930,0x50938),
]
for op,entry,mov_site,store_site,active_site in starters:
 check(f'op{op} starter entry is present',entry in records)
 check(f'op{op} idle starter loads literal state {op}',CF[mov_site:mov_site+2]==bytes([op,0x0a]),CF[mov_site:mov_site+2].hex())
 check(f'op{op} idle starter stores state to FEBE828C',CF[store_site:store_site+4]==bytes.fromhex('440f8cca'),CF[store_site:store_site+4].hex())
 check(f'op{op} starter sets active bit 7 after initializer',CF[active_site:active_site+4]==bytes.fromhex('c43f8cca'),CF[active_site:active_site+4].hex())

print('\n== exact external ownership ==')
# Pin the non-replay callsites directly from firmware.
check('op1 external owner is ClearDiagnosticInformation worker',branch(0x4C9DA)==('jarl',0x50698))
check('op2 external owner is RoutineControl 1108 action',branch(0x4F4CA)==('jarl',0x50760))
check('op4 external owner is internal helper 35658',branch(0x3568C)==('jarl',0x507EA))
check('op5 external owner is RoutineControl 1004 action',branch(0x4F17E)==('jarl',0x50864))
check('op6 external owner is WDBI 0204 completion branch',branch(0x4EC0A)==('jarl',0x50922))
check('35658 has no diagnostic-state references',not ({'0xfebe8154','0xfebe8155','0xfebe8156','0xfebe815d','0xfebe816a'} & {x for x,_ in refs(0x35658)}))
check('35658 is called only from recovered CAN/RTE-side sites',all(branch(a)==('jarl',0x35658) for a in (0x5E1B8,0x5E1DE,0x5E7D0)))

print('\n== completion ownership and the SID14 bridge ==')
check('op4 therefore uses selector-less fallthrough replay',branch(0x50AE0)==('jarl',0x50996))
check('op1 success/failure selector is literal 0x11',CF[0x50A76:0x50A82]==bytes.fromhex('203611001238853520361100'))
check('op1 completion calls shared selector bridge C430',branch(0x50ADC)==('jarl',0x4C430))
check('ClearDI start writes pending tag 0x1410',CF[0x4C9D2:0x4C9DA]==bytes.fromhex('200e1014640f6ac9'))
check('op6 uses coalescing completion helper',branch(0x50AA2)==('jarl',0x4C474))

print('\n== op4 is internal finite selector-less maintenance ==')
check('op4 shares maintenance initializer with op1',branch(0x507FC)==('jarl',0x50660) and branch(0x506AA)==('jarl',0x50660))
check('monitor always falls through to replay once shared statuses are nonpending',branch(0x50AE0)==('jarl',0x50996))
check('replay clears active byte before trying queued work',CF[0x509A6:0x509A8]==bytes.fromhex('8003'))

print(f'\nSummary: {passed} passed, {failed} failed')
raise SystemExit(1 if failed else 0)
