#!/usr/bin/env python3
"""Verify bounded application WDBI DID 0x2013/0x2014 control cones."""
from __future__ import annotations

import csv, hashlib, json, struct, sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
CF=(ROOT/'firmware/RH850_P1M-E_CodeFlash.bin').read_bytes()
CORPUS=ROOT/'data/generated/decompilations.jsonl'
passed=failed=0

def check(name, cond, detail=''):
 global passed,failed
 if cond: passed+=1; print('[PASS]',name)
 else: failed+=1; print('[FAIL]',name, f'({detail})' if detail else '')

def sha(a,n): return hashlib.sha256(CF[a:a+n]).hexdigest()
def corpus(a):
 for line in CORPUS.open():
  r=json.loads(line)
  if r.get('record')=='function' and int(r['entry_addr'],16)==a: return r
 raise KeyError(hex(a))
def refs(a,target,kind=None):
 return [x for x in corpus(a).get('data_references',[]) if x.get('to_addr')==target and (kind is None or x.get('ref_type')==kind)]
def veneer_target(addr):
 if CF[addr:addr+2] != bytes.fromhex('2c06') or CF[addr+6:addr+8] != bytes.fromhex('6c00'):
  return None
 return struct.unpack_from('<I', CF, addr+2)[0]

def branch(addr):
 w0,w1=struct.unpack_from('<HH',CF,addr)
 if ((w0>>6)&0x1f)!=0x1e or (w1&1): return None
 reg2=(w0>>11)&0x1f; hi=w0&0x3f
 if hi&0x20: hi-=0x40
 return ('jarl' if reg2 else 'jr', addr+(hi<<16)+w1)

print('== WDBI 2013 entry and numeric-control chain ==')
check('2013 start gate body is pinned', sha(0x4EF68,40)=='ecc2127f1b219bac3c5f952eaf45650bc9eea10c3f9350073e5f39cf4e0da0a3')
check('2013 result body is pinned', sha(0x4EF90,28)=='b53a42023a915f18aa810e47b1c0822ff7aa244ae39e0f46af4dcf7edd0bbdae')
check('2013 result reaches helper FE1C8', branch(0x4EF9E)==('jarl',0xFE1C8))
check('2013 helper veneer targets B76A8', veneer_target(0xFE1C8)==0xB76A8)
check('B76A8 writes FEBEB434', bool(refs(0xB76A8,'0xfebeb434','WRITE')))
check('B763C reads 434 and writes 448', refs(0xB763C,'0xfebeb434','READ') and refs(0xB763C,'0xfebeb448','WRITE'))
check('B76C0 reads 448 and writes 452', refs(0xB76C0,'0xfebeb448','READ') and refs(0xB76C0,'0xfebeb452','WRITE'))
check('B72EC reads 452', refs(0xB72EC,'0xfebeb452','READ'))
check('B73D0 writes selected value to 41A', refs(0xB73D0,'0xfebeb41a','WRITE'))
check('BCACE copies 41A into E416', refs(0xBCACE,'0xfebeb41a','READ') and refs(0xBCACE,'0xfebee416','WRITE'))
check('3572C mode-selects E416 into 6ACE', refs(0x3572C,'0xfebee416','READ') and refs(0x3572C,'0xfebe6ace','WRITE'))
check('37FB6 reads 6ACE and writes motor-worker 6DCA/6DCC', refs(0x37FB6,'0xfebe6ace','READ') and refs(0x37FB6,'0xfebe6dca','WRITE') and refs(0x37FB6,'0xfebe6dcc','WRITE'))
check('motor control worker directly calls 37FB6', branch(0x5D1A2)==('jarl',0x37FB6))

print('\n== 2013 motor-worker state dead-ends in staging mirrors ==')
# Use full corpus to pin reader-function membership rather than instruction spellings.
def reader_funcs(target):
 out=set()
 for line in CORPUS.open():
  r=json.loads(line)
  if r.get('record')!='function': continue
  if any(x.get('to_addr')==target and x.get('ref_type') in ('READ','PARAM') for x in r.get('data_references',[])):
   out.add(int(r['entry_addr'],16))
 return out
check('6DCA readers are exactly task/RTE staging', reader_funcs('0xfebe6dca')=={0x58404,0x5B9C4,0x5C0B6}, repr(reader_funcs('0xfebe6dca')))
check('6DCC readers are exactly task/RTE staging', reader_funcs('0xfebe6dcc')=={0x58404,0x5B9C4,0x5C0B6}, repr(reader_funcs('0xfebe6dcc')))
for target in ('0xfebe66ce','0xfebe66d0','0xfebe63ce','0xfebe63d0'):
 check(f'{target} staging mirror has no runtime readers', reader_funcs(target)==set(), repr(reader_funcs(target)))

print('\n== WDBI 2014 threshold/mode-selection chain ==')
check('2014 start gate matches 2013 speed+state gate', sha(0x4EFAC,40)=='ecc2127f1b219bac3c5f952eaf45650bc9eea10c3f9350073e5f39cf4e0da0a3')
check('2014 result body is pinned', sha(0x4EFD4,42)=='1b1bb16aa65b140b38ce9882b52e0d92dd33491998a83b4e827319de37961eb9')
check('2014 helper veneer targets B71FE', veneer_target(0xFE1B4)==0xB71FE)
check('B71FE writes FEBEB3EE', bool(refs(0xB71FE,'0xfebeb3ee','WRITE')))
check('B692C reads 3EE and writes threshold decision 3EC', refs(0xB692C,'0xfebeb3ee','READ') and refs(0xB692C,'0xfebeb3ec','WRITE'))
check('B6994 reads 3EC and writes state 3E7', refs(0xB6994,'0xfebeb3ec','READ') and refs(0xB6994,'0xfebeb3e7','WRITE'))
check('B70D0 reads 3EE for independent threshold return', refs(0xB70D0,'0xfebeb3ee','READ'))
check('B7114 selector tail is pinned', CF[0xB71B0:0xB71BA]==bytes.fromhex('5fd261d2eb05bfff1aff'))
check('B7114 directly calls B70D0 only after selector-1 threshold test', branch(0xB71B6)==('jarl',0xB70D0))
check('B65BC side state is local mode/calibration state', refs(0xB65BC,'0xfebeb3a4','WRITE') and refs(0xB65BC,'0xfebeb3a6','WRITE'))

print('\n== 2014 cross-service RoutineControl gate ==')
rows=list(csv.DictReader((ROOT/'data/application_routine_control_surface.csv').open()))
expected={15:'0x110A',17:'0x110C',18:'0x110D'}
check('RoutineControl indices 15/17/18 are RIDs 110A/110C/110D', {i:rows[i]['rid'] for i in expected}==expected)
for i,addr in ((15,0x4F5C4),(17,0x4F6A2),(18,0x4F74A)):
 check(f'RID {rows[i]["rid"]} precondition is expected callback', int(rows[i]['precondition_callback'],16)==addr)
 callsite={0x4F5C4:0x4F5DE,0x4F6A2:0x4F6BA,0x4F74A:0x4F766}[addr]
 check(f'RID {rows[i]["rid"]} precondition calls FE164', branch(callsite)==('jarl',0xFE164))

check('shared precondition veneer FE164 targets B7114', veneer_target(0xFE164)==0xB7114)
check('RID 110A type-1 path preserves selector 1 into FE164', CF[0x4F5DA:0x4F5E2]==bytes.fromhex('6132aa1d8aff86eb'))
check('RID 110C type-1 path forces selector 2 into FE164', CF[0x4F6B8:0x4F6BE]==bytes.fromhex('02328affaaea'))
check('RID 110D type-1 path forces selector 3 into FE164', CF[0x4F764:0x4F76A]==bytes.fromhex('03328afffee9'))
check('B7114 selector 3 skips B70D0 while selectors 1/2 reach it', CF[0xB71B0:0xB71BA]==bytes.fromhex('5fd261d2eb05bfff1aff'))
print('\n== bounded separation from independent actuation path ==')
act_states={'0xfebe6d18','0xfebe6d1c','0xfebe6d28','0xfebe6d2a'}
for addr in (0xB763C,0xB76C0,0xB72EC,0xB73D0,0xBCACE,0x3572C,0x37FB6,0xB692C,0xB6994,0xB70D0,0xB7114):
 direct={x.get('to_addr') for x in corpus(addr).get('data_references',[])}
 check(f'{addr:06X} has no direct d/q ref/feedback references', direct.isdisjoint(act_states), repr(sorted(direct & act_states)))
check('independent motor actuation oracle is present', (ROOT/'tests/verify_motor_actuation_boundary.py').is_file())

print(f'\nSummary: {passed} passed, {failed} failed')
sys.exit(1 if failed else 0)
