#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json,subprocess,sys,tempfile
from pathlib import Path
import pefile
REPO=Path(__file__).resolve().parents[1]; ROOT=REPO/'Techstream/unpacked/toyota/Toyota Diagnostics'; CUW=ROOT/'Calibration Update Wizard'; ART=REPO/'data/generated/techstream_v18/cuw_writer_protocol_grammar.json'; FW=(REPO/'firmware/RH850_P1M-E_CodeFlash.bin').read_bytes()
p=f=0; oracle='raw_bytes'
def check(n,c,d=''):
 global p,f
 ok=bool(c);p+=ok;f+=not ok;print(f"[{'PASS' if ok else 'FAIL'}][{oracle}] {n}"+(f' ({d})' if d else ''))
if not CUW.is_dir(): print('[SKIP] V18 unavailable'); raise SystemExit(77)
obj=json.loads(ART.read_text())
def raw(fn,rva,n):
 pe=pefile.PE(str(CUW/fn)); return pe.get_data(rva,n)
print('== decisive SecurityAccess request shapes ==')
# ReproStd stores request length = transport-prefix + 2 immediately before 27 01.
check('standard SA length is prefix+2',raw('TCUWCanReproStdPrepareWriter.dll',0x159f,3)==bytes.fromhex('8d5f02'))
check('standard SA request starts 27 01',raw('TCUWCanReproStdPrepareWriter.dll',0x15a2,16)==bytes.fromhex('c6843d7cd9ffff27c6843d7dd9ffff01'))
# Unified copies four dwords from ECUAuthKey and stores request length prefix+0x12.
check('unified SA request starts 27 01',raw('TCUWCanUnifiedPrepareWriter.dll',0x15a6,16)==bytes.fromhex('c6843d48c9ffff27c6843d49c9ffff01'))
check('unified copies first ECUAuthKey dword',raw('TCUWCanUnifiedPrepareWriter.dll',0x15c6,2)==bytes.fromhex('8b08'))
check('unified SA length is prefix+0x12',raw('TCUWCanUnifiedPrepareWriter.dll',0x15f1,3)==bytes.fromhex('8d4712'))

print('\n== target boot SecurityAccess contract ==')
# Corpus body is SHA-bound to raw firmware; semantic assertion is kept alongside raw identity.
rec=None
for line in (REPO/'data/generated/decompilations.jsonl').open():
 r=json.loads(line)
 if r.get('entry_addr')=='0x00005328': rec=r; break
check('request-seed function present',rec is not None)
if rec:
 size=rec['body_size']; check('request-seed raw body identity',hashlib.sha256(FW[0x5328:0x5328+size]).hexdigest()=='a99760a108a56907f1b4646d826a10d031415d107721909409af511ea575350c')
 check('target requires exact request length 0x12','param_1 == 0x12' in rec['decompiled_c'])
 check('wrong length returns NRC 0x13','uVar6 = 0x13' in rec['decompiled_c'])

print('\n== RoutineControl wire-byte correction ==')
# x86 imm16 is stored little-endian to the request buffer. These are the encoded bytes,
# so 0xF510 means wire bytes 10 F5, not F5 10.
check('standard RID immediate encodes wire 10 F5',raw('TCUWCanReproStdFlashWriter.dll',0x2698,9)==bytes.fromhex('66c78510c9ffff10f5'))
check('standard FF00 branch encodes ff 00',raw('TCUWCanReproStdFlashWriter.dll',0x2683,9)==bytes.fromhex('66c78510c9ffffff00'))
check('unified F0 routine encodes 10 F0',bytes.fromhex('10f0') in raw('TCUWCanUnifiedFlashWriter.dll',0x20e0,40))
check('unified FF00 branch encodes ff 00',bytes.fromhex('ff00') in raw('TCUWCanUnifiedFlashWriter.dll',0x2100,24))
check('unified F1 routine encodes 10 F1',raw('TCUWCanUnifiedFlashWriter.dll',0x2118,9)==bytes.fromhex('66c78524c9ffff10f1'))
check('unified F2 routine encodes 10 F2',raw('TCUWCanUnifiedFlashWriter.dll',0x212d,9)==bytes.fromhex('66c78524c9ffff10f2'))
import struct
routines=[struct.unpack_from('<I H B B I',FW,0x8F44+i*12)[1] for i in range(5)]
check('Sienna boot routine table exact',routines==[0x10F0,0x10F1,0x10F2,0x10F3,0xFF00],repr([hex(x) for x in routines]))

print('\n== route-family closure ==')
check('32 distinct prepare/flash families',len(obj['route_families'])==32)
check('196 rows classified',sum(x['factory_rows'] for x in obj['route_families'])==196)
check('verdict counts conservative exact',obj['verdict_counts']=={'bounded-rejected':30,'byte-compatible':1,'compatible-bounded':1,'rejected':162,'unresolved':2},repr(obj['verdict_counts']))
uni=next(x for x in obj['route_families'] if x['prepare_writer']=='TCUWCanUnifiedPrepareWriter.dll' and x['flash_writer']=='TCUWCanUnifiedFlashWriter.dll')
std=next(x for x in obj['route_families'] if x['prepare_writer']=='TCUWCanReproStdPrepareWriter.dll')
check('unified route is sole byte-compatible row',uni['factory_rows']==1 and uni['verdict_sienna_8965B4512000']=='byte-compatible')
check('standard route rejected by exact grammar',std['factory_rows']==2 and std['verdict_sienna_8965B4512000']=='rejected')
mmc=sum(x['factory_rows'] for x in obj['route_families'] if x['verdict_sienna_8965B4512000']=='unresolved')
check('only two MMC rows remain unresolved',mmc==2)

print('\n== raw-template scanner/regeneration ==')
# The scanner covers every referenced writer plus support DLLs and preserves encoded store bytes.
matrix=json.loads((REPO/'data/generated/techstream_v18/cuw_writer_family_matrix.json').read_text())
referenced={x['name'] for x in matrix['writers']}
check('all 47 referenced writers have scans',len(referenced)==47 and referenced <= set(obj['writer_scans']))
with tempfile.TemporaryDirectory() as td:
 out=Path(td)/'x.json'; r=subprocess.run([sys.executable,str(REPO/'tools/techstream/generate_cuw_writer_protocol_grammar.py'),'--root',str(ROOT),'--output',str(out)],check=False)
 check('generator exits',r.returncode==0);check('byte-identical regeneration',out.read_bytes()==ART.read_bytes())
print(f'\nResults: {p} passed, {f} failed');raise SystemExit(1 if f else 0)
