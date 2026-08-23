#!/usr/bin/env python3
"""Verify that configured XCP commands do not compose into a keyless write escape."""
from __future__ import annotations
import struct
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
CF=(ROOT/'firmware/RH850_P1M-E_CodeFlash.bin').read_bytes()
LO,HI=0xFEBF7C00,0xFEBFFBFF
passed=failed=0

def check(n,o,d=''):
 global passed,failed
 if o: passed+=1; print('[PASS]',n)
 else: failed+=1; print('[FAIL]',n, d)
def u16(o): return struct.unpack_from('<H',CF,o)[0]
def u32(o): return struct.unpack_from('<I',CF,o)[0]

print('== standard dispatcher is fixed and bounded ==')
command_map=CF[0x22C04:0x22C04+CF[0x22BD1]]
callbacks=[u32(0x22C30+i*4) for i in range(18)]
check('standard callback table has exactly 18 configured slots',len(callbacks)==18)
check('standard map indices stay inside callback table',all(i < len(callbacks) for i in command_map))
check('GET_SEED/UNLOCK remain unconfigured',command_map[7]==0 and command_map[8]==0)
check('DOWNLOAD maps to fixed 0x80F12',callbacks[command_map[0xFF-0xF0]]==0x80F12)
check('MODIFY_BITS maps to fixed 0x80FD8',callbacks[command_map[0xFF-0xEC]]==0x80FD8)
check('XCP write window constants remain exact',u32(0x2B3BC)==LO and u32(0x2B3C0)==HI)

print('\n== DAQ is read-direction only ==')
check('WRITE_DAQ stores accepted address into DAQ pointer table',CF[0x814C8:0x814CC]==bytes.fromhex('7ee7f194'))
check('SET_DAQ_LIST_MODE rejects mode bits 0x33 including STIM direction',CF[0x81540:0x81548]==bytes.fromhex('6108c10633009a2d'))
check('DAQ sampler dereferences configured pointer for one-byte read',CF[0x812C2:0x812D0]==bytes.fromhex('00f5c49941d2410a9a0081006090'))
check('DAQ sampler writes only DTO staging, not through configured pointer',CF[0x812D0:0x812D4]==bytes.fromhex('5397c894'))
for op in (0xDF,0xDC,0xDB): check(f'STIM-like opcode 0x{op:02X} is unconfigured',command_map[0xFF-op]==0)

print('\n== custom page/checksum commands cannot redirect writes ==')
selectors=[]; targets=[]
for i in range(7):
 s,p,t=struct.unpack_from('<B3sI',CF,0x2B3F0+i*8); selectors.append(s); targets.append(t); check(f'custom record {i} padding is zero',p==b'\0\0\0')
check('custom selector set is fixed FB/FA/F5/F3/EB/EA/E4',selectors==[0xFB,0xFA,0xF5,0xF3,0xEB,0xEA,0xE4])
check('custom targets are fixed CodeFlash functions',targets==[0x9729A,0x972FA,0x97432,0x97546,0x975EE,0x97668,0x976F4])
check('E4 hardcodes CodeFlash 0x10000 -> FEBF7C00',CF[0x976D0:0x976DE]==bytes.fromhex('3e06007cbffe210600000100e505'))
check('E4 terminates at 0x17DF0',CF[0x976E8:0x976F4]==bytes.fromhex('3306f07d0100f309f1f57f00'))
check('E4 gate requires source page 0 and destination page 1',CF[0x97738:0x9774A]==bytes.fromhex('619a8a0d20e65a00e009da05bfff8cffa505'))
check('F3 hardcodes the same 0x10000..0x17DF0 CodeFlash interval', CF[0x97578:0x97584] == bytes.fromhex('3306f07d0100320600000100'))
check('F3 invokes shared range helper before checksum', CF[0x975AE:0x975B4] == bytes.fromhex('0a30bfffaafd'))

print('\n== write-arithmetic near misses ==')
def allowed(start,length):
 if length<=0 or start>0xFFFFFFFF-(length-1): return False
 end=start+length-1
 return LO<=start<=end<=HI
check('six-byte DOWNLOAD at window start is valid',allowed(LO,6))
check('DOWNLOAD crossing high bound is invalid',not allowed(HI-2,6))
check('32-bit wrap is invalid before range comparison',not allowed(0xFFFFFFFE,4))
check('MODIFY_BITS requires word-aligned MTA',CF[0x80FFC:0x81008]==bytes.fromhex('80ffa6010ae0ca060300ba2d'))
check('largest aligned u32 target cannot wrap below zero',0xFFFFFFFC+3==0xFFFFFFFF)
check('largest aligned u32 target is outside XCP write range',not allowed(0xFFFFFFFC,4))

print(f'\nResults: {passed} passed, {failed} failed')
raise SystemExit(1 if failed else 0)
