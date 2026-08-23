#!/usr/bin/env python3
"""Verify application CanTp/PduR/DCM receive bounds reopened after the keyless audit."""
from __future__ import annotations
import json,struct
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
FW=(ROOT/'firmware/RH850_P1M-E_CodeFlash.bin').read_bytes()
CORP=ROOT/'data/generated/decompilations.jsonl'
WANTED={0x79DE6,0x79FDA,0x903A8,0x9043C,0x90916,0x909BC,0x920D2,0x92398}
by={}
for line in CORP.read_text().splitlines():
 r=json.loads(line)
 if r.get('entry_addr'):
  a=int(r['entry_addr'],16)
  if a in WANTED: by[a]=r
p=f=0
def ck(n,c,d=''):
 global p,f
 ok=bool(c); p+=ok; f+=not ok; print(f"[{'PASS' if ok else 'FAIL'}][cfg_dataflow] {n}"+(f' ({d})' if d else ''))
def u16(a):return struct.unpack_from('<H',FW,a)[0]
def u32(a):return struct.unpack_from('<I',FW,a)[0]
print('== CanTp framing and PduR routing ==')
ck('all required canonical functions are in the decompiler corpus',set(by)==WANTED,str(sorted(WANTED-set(by))))
ck('CanTp first-frame protocol ceiling is 0xFFF',u16(0x22D20)==0x0FFF,hex(u16(0x22D20)))
# Three 0x20-byte CanTp connection records carry the upper-layer Rx PDU IDs at +8.
tp_ids=[u16(0x22CBE+i*0x20+8) for i in range(3)]
ck('three diagnostic CanTp connections route PDU IDs 0x802/803/804',tp_ids==[0x802,0x803,0x804],str([hex(x) for x in tp_ids]))
callbacks=[u32(0x2188C+4*i) for i in range(6)]
ck('PduR callback vector is exact',callbacks==[0x903A8,0x9043C,0x909BC,0x904BC,0x90B20,0x90C30],str([hex(x) for x in callbacks]))
ck('generic 0x90916 copy belongs to CopyTxData, not receive reassembly','FUN_00090916' in by[0x909BC]['decompiled_c'] and callbacks[2]==0x909BC)
print('\n== DCM receive allocation ==')
slots=[(u16(0x26064+i*8),u32(0x26064+i*8+4)) for i in range(3)]
ck('DCM has three fixed 256-byte request buffers',slots==[(0x100,0xFEBE5629),(0x100,0xFEBE5729),(0x100,0xFEBE5829)],str([(hex(a),hex(b)) for a,b in slots]))
ck('DCM local PDU IDs are exactly 2/3/4',[u16(0x260C6+i*12) for i in range(3)]==[2,3,4])
sor=by[0x903A8]['decompiled_c']
ck('StartOfReception rejects total length above configured slot capacity','(param_3 & 0xffff) <=' in sor and 'return 3;' in sor)
ck('StartOfReception recognizes exactly three slots','if (2 < uVar4)' in sor)
print('\n== segmented-copy bounds ==')
copyrx=by[0x9043C]['decompiled_c']; copy=by[0x920D2]['decompiled_c']; rem=by[0x92398]['decompiled_c']; cf=by[0x79FDA]['decompiled_c']; ff=by[0x79DE6]['decompiled_c']
ck('CopyRxData obtains remaining capacity before copying','FUN_00092398' in copyrx and 'FUN_000920d2' in copyrx and copyrx.index('FUN_00092398') < copyrx.index('FUN_000920d2'))
ck('CopyRxData requires chunk length <= remaining capacity','*(ushort *)(param_2 + 4) <= uVar4' in copyrx)
ck('remaining-capacity getter reads the per-slot remaining field','DAT_febe59d0' in rem)
ck('copy helper advances destination pointer one byte per copied byte','*(undefined1 *)*piVar1 = uVar3;' in copy and '*piVar1 = *piVar1 + 1;' in copy)
ck('copy helper decrements remaining capacity by copied length','DAT_febe59d0' in copy and '= sVar2 - sVar4;' in copy)
ck('CanTp CF path clips payload chunk to remaining TP length','if (uVar6 < uVar9)' in cf and 'uStack_24 = uVar6;' in cf and 'uVar9 = uVar9 - uStack_24;' in cf)
ck('CanTp FF parser enforces 0x22D20 configured ceiling','DAT_00022d20 < uVar2' in ff)
ck('protocol max is larger than each DCM allocation, making DCM check material',0xFFF>0x100)
print(f'\nResults: {p} passed, {f} failed'); raise SystemExit(1 if f else 0)
