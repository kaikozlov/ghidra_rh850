#!/usr/bin/env python3
"""Verify the application SID-0xBA proprietary operation and authorization surface."""
from __future__ import annotations
import csv,hashlib,struct,subprocess,sys,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
CF=(ROOT/'firmware/RH850_P1M-E_CodeFlash.bin').read_bytes()
CSV=ROOT/'data/application_proprietary_ba_surface.csv'
GEN=ROOT/'tools/generate_application_proprietary_ba_surface.py'
passed=failed=0
def check(name,cond,detail=''):
 global passed,failed
 if cond: passed+=1
 else: failed+=1
 print(f"[{'PASS' if cond else 'FAIL'}] {name}"+(f' ({detail})' if detail else ''))
def u32(a): return struct.unpack_from('<I',CF,a)[0]
def sha(a,n): return hashlib.sha256(CF[a:a+n]).hexdigest()
def branch(a):
 w0,w1=struct.unpack_from('<HH',CF,a)
 if ((w0>>6)&0x1f)!=0x1e or w1&1:return None
 reg=(w0>>11)&0x1f; hi=w0&0x3f
 if hi&0x20:hi-=0x40
 return ('jarl' if reg else 'jr',a+(hi<<16)+w1)
print('== SID BA service and operation descriptors ==')
S=struct.Struct('<IIIIBBBBB3x'); services=[S.unpack_from(CF,0x25E28+i*24) for i in range(17)]; ba=next(r for r in services if r[4]==0xBA)
check('BA direct callback is 0x8D344',ba[0]==0x8D344,hex(ba[0]))
check('BA service is extended-session only',list(CF[ba[2]:ba[2]+ba[7]])==[3])
check('BA configured Dcm security count is zero',ba[6]==0)
check('BA operation count is 10',CF[0x28094]==10,str(CF[0x28094]))
expected=[
(0xF1,0x34B74,0x34B9A),(0xF3,0x34BA8,0x34BF4),(0xF4,0x34C50,0x34C76),(0xF5,0x34C84,0x34CAA),(0xF6,0x34CB8,0x34D4E),
(0xF7,0x34DAE,0x34E6C),(0xF8,0x34EC0,0x34F08),(0xF9,0x34F1A,0x34F40),(0xFA,0x34F4E,0x34F80),(0xFB,0x34F90,0x34FAA)]
for i,(sel,start,done) in enumerate(expected):
 a=0x28098+i*16
 check(f'BA descriptor {sel:02X} exact',CF[a]==sel and CF[a+1]==6 and u32(a+8)==start and u32(a+12)==done)
print('\n== request tokens and gateway authorization ==')
for addr,token in [(0x2109D,b'JTEKM'),(0x210A2,b'TMPCL'),(0x210A7,b'JTRM1'),(0x210AC,b'JTRM2'),(0x210B1,b'BADIS'),(0x210B6,b'BAENA'),(0x210BB,b'TZCLR'),(0x210C0,b'JTRM3'),(0x210C5,b'VSPD'),(0x210C9,b'ASINC')]:
 check(f'token at 0x{addr:X} is {token.decode()}',CF[addr:addr+len(token)]==token)
check('gateway BAENA token is separately pinned',CF[0x21098:0x2109D]==b'BAENA')
check('gateway helper body pinned',sha(0x34882,50)=='285279c2e2c1ee816f5e4a9fc84d75045cf5341cac098a546ed0e910885516fe')
check('gateway accepts only selector F7 / length 6 / BAENA when marker is absent',CF[0x3489C:0x348AC]==bytes.fromhex('1c0609fffa0566dada056152ba0520ee'))
check('dispatcher body pinned',sha(0x348B4,146)=='c1996f216a6a083f6272a54510891811a383f8e70ac634d00151de4543b63fe3')
check('dispatcher calls gateway then loads persistent marker',branch(0x348D2)==('jarl',0x34882) and CF[0x348D6:0x348DA]==bytes.fromhex('a40f27a7'))
print('\n== F7 BAENA local SecurityAccess-2 gate ==')
check('F7 local gate helper pinned',sha(0x34D96,24)=='13f0312fd51578c9d417d7f862d597eea0cba5c55df258b69fe8fe8a7dfae5b3')
check('F7 gate calls Dcm security reader wrapper',branch(0x34D9A)==('jarl',0x8C8C6))
check('F7 gate tests mask bit 0x02',CF[0x34DA2:0x34DA6]==bytes.fromhex('ca9e0200'))
check('security wrapper calls application security-state reader',branch(0x8C8CE)==('jarl',0x8FDCA))
check('security mask setter body pinned',sha(0x9075A,120)=='567dfaaec84a0a62838119415f96899d593b8b5fe9191e5753d616350b465b1e')
check('mask setter computes bit from level-1',CF[0x90788:0x907A2]==bytes.fromhex('1d9effff930013f0a5f2d30e1f00c2f2019ac3f1e19fc208030d'))
print('\n== persistent authorization objects and restore/countdown ==')
check('F7 start body pinned',sha(0x34DAE,190)=='a49e3ee734fda7f3659cef6f2eef88f9a1c47ba6f9b0852495e16d74c585d4c2')
check('F7 writes ordinary object 24 / wire ID 0x18',bytes.fromhex('20361800') in CF[0x34DAE:0x34E6C])
check('F7 writes redundant namespace object 5 / wire ID 0x105',bytes.fromhex('20360501') in CF[0x34DAE:0x34E6C])
check('F7 embeds redundant marker magic A55A5AA5',bytes.fromhex('2106a55a5aa5') in CF[0x34DAE:0x34E6C])
check('F7 terminalizes marker/count to 5A and DAT_310A9',CF[0x34E38:0x34E4A]==bytes.fromhex('9c0f010000ea24f624a7840b200e5a00830b'))
check('F6 disable body pinned',sha(0x34CB8,150)=='b82660142c8ece335d7a87a26450dadb2e14ff508a7fc9d061c053e9d2447f28')
check('F6 touches same two persistent object IDs',bytes.fromhex('20361800') in CF[0x34CB8:0x34D4E] and bytes.fromhex('20360501') in CF[0x34CB8:0x34D4E])
check('restore body pinned',sha(0x347B0,92)=='f351bf243a0d85bd8c8939761438fe11ef4727627b2417a853ac890302774078')
check('restore reads 0x105 then validates A55A5AA5',CF[0x347B8:0x347D4].startswith(bytes.fromhex('20360501')) and bytes.fromhex('2106a55a5aa5') in CF[0x347B0:0x3480C])
check('restore reads object 0x18 and bounds countdown by DAT_310A9',bytes.fromhex('20361800') in CF[0x347B0:0x3480C] and bytes.fromhex('b39fa910') in CF[0x347B0:0x3480C])
check('countdown body pinned',sha(0x34FB6,84)=='02a6900937a3c2d7798af9897f49c256bbdbd480b199d5eb0932dc244fa97573')
check('countdown persists 0x18 and clears 0x105 on expiry',bytes.fromhex('20361800') in CF[0x34FB6:0x3500A] and bytes.fromhex('20360501') in CF[0x34FB6:0x3500A])
# Storage descriptors: ordinary 24 is separately mapped; redundant 5 and key-bearing 15 must remain distinct.
red5=struct.unpack_from('<HHI',CF,0x2B0AC+5*8); red15=struct.unpack_from('<HHI',CF,0x2B0AC+15*8)
check('redundant object 5 is 8 bytes / base block 15 / RAM FEBEF418',red5==(8,15,0xFEBEF418),repr(red5))
check('key-bearing redundant object 15 is separate 32-byte object / RAM FEBF02E8',red15==(32,41,0xFEBF02E8),repr(red15))
with (ROOT/'data/checkpoint_payload_map.csv').open(newline='') as f: cps={int(r['object_index']):r for r in csv.DictReader(f)}
check('ordinary object 24 is persistent_countdown',cps[24]['evidence_name']=='persistent_countdown' and cps[24]['data_length']=='8')
print('\n== operation families and bounded effects ==')
for start,mode in [(0x34B74,3),(0x34C50,5),(0x34C84,6),(0x34F1A,7)]:
 check(f'JTRM/JTEKM start {start:06X} reaches common mode-request thunk',0xFE024 in [branch(a)[1] for a in range(start,start+40,2) if branch(a) and branch(a)[0]=='jarl'])
check('TMPCL completion reaches persistent object-5/6 helpers',branch(0x34C00)==('jarl',0x3B252) and branch(0x34C04)==('jarl',0x38DCA) and branch(0x34C08)==('jarl',0x47958))
check('TZCLR is gated by actual application vehicle-speed snapshot',CF[0x34ED4:0x34ED6]==bytes.fromhex('77d0') and branch(0x34EDA)==('jarl',0x3485A))
check('TZCLR completion joins B7D26 shared workflow',branch(0x34F12)==('jarl',0xFDE30))
check('VSPDA shape is value + four-byte VSPD token',CF[0x34F58:0x34F62]==bytes.fromhex('07360100253ee1d10442'))
check('VSPDA completion calls B20CC thunk',branch(0x34F88)==('jarl',0xFE1A0))
check('ASINC compares five bytes starting at overlapping A',CF[0x34F94:0x34FA0]==bytes.fromhex('07300542253ee5d1bfffbef8'))
check('ASINC completion calls B20DC thunk',branch(0x34FAE)==('jarl',0xFE1DC))
check('ASINC lower flag setter body pinned',sha(0xB20DC,12)=='4c8d9f3c9cee9f6e1fe0813c9c4ab30968888bb9ebb0cc8e075866bb4198b99b')
check('ASINC filtered consumer body pinned',sha(0xB80EE,192)=='efdfb22c1fb61de153991835c98ccca28725de8bdaa5745f6089b94439f0ab59')
check('VSPDA worker body pinned',sha(0xBC5BC,228)=='ae1be39d16576ecb4d529a88940e02315a875e5188c1e5052bc455be79a0f519')
print('\n== generated BA artifact ==')
with CSV.open(newline='') as f: rows=list(csv.DictReader(f))
check('BA CSV has ten rows',len(rows)==10)
check('BA CSV selectors exact',[r['selector'] for r in rows]==[f'0x{x:02X}' for x,_,_ in expected])
check('F7 CSV records local SA2 gate',next(r for r in rows if r['selector']=='0xF7')['effective_local_gate']=='application SecurityAccess level 2')
check('FA CSV records alternate snapshot, not protected speed gate','FEBEE894' in next(r for r in rows if r['selector']=='0xFA')['downstream_state'])
with tempfile.TemporaryDirectory() as d:
 out=Path(d)/'ba.csv'; p=subprocess.run([sys.executable,str(GEN),'-o',str(out)],cwd=ROOT,capture_output=True,text=True)
 check('BA generator rerun succeeds',p.returncode==0,p.stderr)
 check('BA CSV matches deterministic regeneration',out.read_bytes()==CSV.read_bytes())
print(f'\nSummary: {passed} passed, {failed} failed')
raise SystemExit(1 if failed else 0)
