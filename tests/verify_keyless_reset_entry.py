#!/usr/bin/env python3
"""Verify static reset/re-entry surfaces for the unauthenticated-execution audit."""
from __future__ import annotations
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
CF=(ROOT/'firmware/RH850_P1M-E_CodeFlash.bin').read_bytes()
CORPUS=ROOT/'data/generated/decompilations.jsonl'
passed=failed=0

def check(n,o,d=''):
 global passed,failed
 if o: passed+=1; print('[PASS]',n)
 else: failed+=1; print('[FAIL]',n,d)
funcs={}
with CORPUS.open() as f:
 for line in f:
  r=json.loads(line)
  if r.get('record')=='function' and r.get('entry_addr'): funcs[int(r['entry_addr'],16)]=r

def c(entry): return funcs[entry].get('decompiled_c','')

print('== triple-copy reset latch ==')
text=c(0x61AFA)
check('reset-latch setter writes raw/XOR55/XORAA triplet','Ramffc0a000 = param_1;' in text and '^ 0x55555555' in text and '^ 0xaaaaaaaa' in text)
for entry,val in [(0x62E0E,'0x3e3e3e3e'),(0x63960,'0x6d6d6d6d'),(0x64C44,'0xd6d6d6d6')]:
 check(f'known latch producer 0x{entry:X} supplies fixed sentinel {val}',f'FUN_00061afa({val});' in c(entry))
check('live application-to-boot handoff zeros all four latch words before 0x9F00',all(s in c(0x64EC8) for s in ['Ramffc0a000 = 0;','Ramffc0a004 = 0;','Ramffc0a008 = 0;','Ramffc0a00c = 0;','FUN_00009f00(&DAT_00031914);']))

print('\n== reset-mode translation has fixed callers ==')
tr=c(0x60870)
for src,dst in [("param_1 == -1","uVar1 = 0;"),("param_1 == '\\x01'","uVar1 = 0x50;"),("param_1 == '\\x02'","uVar1 = 0x3d;"),("param_1 != '\\0'","return 0x11;"),("uVar1 = 0x73;","FUN_000607de(uVar1);")]:
 check(f'reset translator pins {src}',src in tr and dst in tr)
# Canonical call graph: exactly system_hard_reset, FUN_62982, FUN_62AF2.
caller_entries=set()
for e,r in funcs.items():
 if e != 0x60870 and 'FUN_00060870(' in r.get('decompiled_c',''):
  caller_entries.add(e)
check('reset translator has only three canonical callers',caller_entries=={0x608AA,0x62982,0x62AF2},repr(sorted(caller_entries)))
check('62AF2 calls translator with fixed mode 1','FUN_00060870(1);' in c(0x62AF2))
check('system_hard_reset calls translator with fixed FF mode','FUN_00060870(0xff);' in c(0x608AA))

print('\n== startup coordinator is internal and fixed-policy ==')
coord_callers={e for e,r in funcs.items() if e != 0x62BC6 and 'FUN_00062bc6(' in r.get('decompiled_c','')}
check('reset/startup coordinator has one canonical caller',len(coord_callers)==1,repr(sorted(coord_callers)))
coord=c(0x62BC6)
for fixed in ('FUN_000628ee(0x11);','FUN_000628ee(0x22);','FUN_000628ee(0x33);','FUN_000628ee(0x44);'):
 check(f'coordinator uses fixed action {fixed}',fixed in coord)
check('coordinator does not reference application XCP window','febf7c' not in coord.lower() and 'febffb' not in coord.lower())

print('\n== power-on validation remains data/status selection, not PC selection ==')
# Reset-latch consumer copies the four words to ordinary FEBE status cells and replaces hardware words with sentinels.
restore=c(0x61B18)
check('reset-latch consumer copies all four words to FEBE status state',all(x in restore for x in ('DAT_febe39b4 = Ramffc0a000;','DAT_febe8d90 = Ramffc0a004;','DAT_febe8da4 = Ramffc0a008;','DAT_febe39b8 = Ramffc0a00c;')))
check('reset-latch consumer then overwrites hardware words with fixed sentinels',all(x in restore for x in ('Ramffc0a000 = 0xa5a5a5a5;','Ramffc0a004 = 0xf0f0f0f0;','Ramffc0a008 = 0xf0f0f0f;','Ramffc0a00c = 0;')))
check('live 9F00 handoff remains direct CodeFlash call, not latch-derived target',CF[0x64EEC:0x64EF0] == bytes.fromhex('baff1450') and 'FUN_00009f00' in c(0x64EC8))

print(f'\nResults: {passed} passed, {failed} failed')
raise SystemExit(1 if failed else 0)
