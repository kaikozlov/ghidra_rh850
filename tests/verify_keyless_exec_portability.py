#!/usr/bin/env python3
"""Verify the authenticated RAM-exec baseline across all three tracked EPS dumps."""
from __future__ import annotations
import json, struct
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
S=(ROOT/'firmware/RH850_P1M-E_CodeFlash.bin').read_bytes()
H=(ROOT/'community/albinoelephant/raw-20260818/albinoelephant-corolla-2023.20260814-0023/dump_codeflash_00000000_00200000_20260814-025814.bin').read_bytes()
F=(ROOT/'community/spanconstant/raw-20260821/span-corolla-2025.20260821-1511/dump_codeflash_00000000_00200000_20260821-152033.bin').read_bytes()
passed=failed=0

def check(n,o,d=''):
 global passed,failed
 if o: passed+=1; print('[PASS]',n)
 else: failed+=1; print('[FAIL]',n, d)

def exact_shift(image,off,size): return S[off:off+size]==image[off-0x1C:off-0x1C+size]

print('== shared roots and boot implementation ==')
for name,img in [('H',H),('F',F)]:
 check(f'{name} payload-build root matches Sienna',img[0xBFD8:0xBFE8]==S[0xBFD8:0xBFE8])
 check(f'{name} boot-SA root matches Sienna',img[0xBFE8:0xBFF8]==S[0xBFE8:0xBFF8])
 check(f'{name} app-SA root matches Sienna',img[0x20840:0x20850]==S[0x20840:0x20850])
for name,img in [('H',H),('F',F)]:
 for label,off,size in [
  ('SecurityAccess',0x5516,110),('RequestDownload',0x5D68,468),('TransferData',0x4DBA,56),
  ('TransferExit',0x5C92,152),('RoutineControl',0x567E,696),('request-seed',0x5328,202),
  ('send-key',0x53F2,12),('payload-decrypt task',0x6BDE,116)]:
  check(f'{name} {label} body transfers at -0x1C',exact_shift(img,off,size))
check('H/F boot domain is byte-identical through 0xA003',H[:0xA004]==F[:0xA004])
check('H/F live handoff stays at absolute 0x9F00 with same fixed-state prefix',H[0x9F00:0x9F22]==F[0x9F00:0x9F22]==S[0x9F00:0x9F22])

print('\n== field-acquisition provenance ==')
h_manifest=(ROOT/'community/albinoelephant/raw-20260818/MANIFEST.txt').read_text()
check('Albino manifest says dump used public payload-build secret','public payload-build secret' in h_manifest)
check('Albino manifest rules out glitch/bench/module removal for this acquisition','No glitching, no bench work, no module removal.' in h_manifest)
span_log=json.loads((ROOT/'community/spanconstant/raw-20260821/span-corolla-2025.20260821-1511/security_access_log.json').read_text())
attempts=next(iter(span_log['ecus'].values()))['attempts']
accepted={a['caller'] for a in attempts if a['outcome']=='accepted' and a['call']=='send_key'}
for caller in ('dump_range:codeflash','dump_range:local_ram_pe1','dump_range:local_ram_self','dump_range:dataflash'):
 check(f'Span log records accepted SecurityAccess for {caller}',caller in accepted)
profiles=json.loads((ROOT/'data/variant_bootstrap_profiles.json').read_text())['profiles']
check('exactly one tracked authenticated-RAM bootstrap profile', len(profiles)==1)
profile=profiles[0]
check('bootstrap profile pins FEBF0000/0x1000 staging', profile['authenticated_download_base']=='0xFEBF0000' and profile['authenticated_download_size']=='0x1000')
check('bootstrap profile pins 10F0 verify and FF00 execute', profile['verify_routine']=='0x10F0' and profile['execute_routine']=='0xFF00')
evidence={e['software_id']:e for e in profile['evidence']}
for sw,manifest in [('8965H1202000','community/albinoelephant/raw-20260818/MANIFEST.txt'),('8965F1208000','community/spanconstant/raw-20260821/MANIFEST.txt')]:
 e=evidence[sw]
 check(f'{sw} profile records target-built range-payload execution', e['fixture_transfer']=='target-built-range-payloads-observed' and e['grade']=='observed')
 check(f'{sw} profile provenance names retained manifest', manifest in e['source'])

print(f'\nResults: {passed} passed, {failed} failed')
raise SystemExit(1 if failed else 0)
