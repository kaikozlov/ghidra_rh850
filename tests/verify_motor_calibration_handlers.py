#!/usr/bin/env python3
"""Verify Stage-6 calibration/version-domain handler boundaries."""
from __future__ import annotations
import csv, hashlib, struct, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
CF=(ROOT/'firmware/RH850_P1M-E_CodeFlash.bin').read_bytes()
CSV=ROOT/'data/motor_calibration_handlers.csv'
REPORT=ROOT/'docs/architecture/control-partition.md'
passed=failed=0

def check(name,cond,detail=''):
    global passed,failed
    ok=bool(cond); passed+=ok; failed+=not ok
    print(f"[{'PASS' if ok else 'FAIL'}] {name}"+(f" ({detail})" if detail else ''))

def sha(a,n): return hashlib.sha256(CF[a:a+n]).hexdigest()
def branch_target(a):
    if a+4>len(CF): return None
    w0,w1=struct.unpack_from('<HH',CF,a)
    if ((w0>>6)&0x1f)!=0x1e or (w1&1): return None
    hi=w0&0x3f
    if hi&0x20: hi-=0x40
    return a+(hi<<16)+w1

def targets(lo,hi): return {t for a in range(lo,hi,2) if (t:=branch_target(a)) is not None}

with CSV.open(newline='',encoding='utf-8') as f: rows=list(csv.DictReader(f))
check('artifact has two calibration handlers',len(rows)==2)
by={int(r['handler'],0):r for r in rows}
for a in (0x32B80,0xB98BC):
    r=by[a]
    check(f'{a:#x} body hash',sha(a,int(r['handler_size']))==r['handler_sha256'])

print('\n== coordinate-transform calibration domain ==')
check('CH0 transition dispatcher reaches inner 0x33198',0x33198 in targets(0x5CC08,0x5CE0C))
check('CH0 steady dispatcher reaches inner 0x33198',0x33198 in targets(0x5CE0C,0x5CEA8))
check('inner state machine reaches handler 0x32B80',0x32B80 in targets(0x33198,0x33584))
check('outer CH0 version dispatcher reaches transition and steady dispatchers',
      {0x5CC08,0x5CE0C}.issubset(targets(0x5784C,0x57902)))
check('transition dispatcher body pinned',sha(0x5CC08,388)=='915c1411f46958b7fc78cf1d6bb70982f0aac897d8bfecc9a55e268d8e53fec1')
check('steady dispatcher body pinned',sha(0x5CE0C,156)=='7cd649bf259e42be56e022e4944b8ae24276c6aaab9ae107a1c51e202170fd7e')
check('inner 0x33198 body pinned',sha(0x33198,1004)=='40e63928fedc7317056602ff80c8a217e5cdb64c5f73fdfd46f04c62f0b6ad5b')

print('\n== rotor-observer calibration domain ==')
check('transition wrapper BEB44 reaches B98BC',0xB98BC in targets(0xBEB44,0xBEBF6))
check('steady wrapper BEBF6 reaches B98BC',0xB98BC in targets(0xBEBF6,0xBEC4C))
check('outer CH2 version dispatcher reaches transition wrapper through FDD18',0xFDD18 in targets(0x579B4,0x57A3C))
check('outer CH2 version dispatcher reaches steady wrapper through FDD2C',0xFDD2C in targets(0x579B4,0x57A3C))
check('outer CH2 dispatcher body pinned',sha(0x579B4,136)=='91b364232b930841c0ae6a1d9ce750f4dc2ac25ddf456499b91e65a012db5c7f')
check('transition wrapper body pinned',sha(0xBEB44,178)=='d57a00df7543e90c9cbddaeec02ed78b52412706ce50f6c451697a10370f0de6')
check('steady wrapper body pinned',sha(0xBEBF6,86)=='ac38a1b4315e205b4dbb98d1e865d72adad5629e577682fc693db94e6c0e6faf')

text=REPORT.read_text(encoding='utf-8') if REPORT.exists() else ''
for token in ('0x32B80','0x33198','0x512','0x600','0xB98BC','0xBEB44','0xBEBF6','0x200..0x522','data/motor_calibration_handlers.csv'):
    check(f'report contains {token}',token.lower() in text.lower())
print(f'\nSummary: {passed} passed, {failed} failed')
sys.exit(1 if failed else 0)
