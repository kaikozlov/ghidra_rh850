#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json,subprocess,sys,tempfile
from pathlib import Path
import pefile
from tools import REPO_ROOT
REPO=REPO_ROOT; ROOT=REPO/'software/Techstream/v18/unpacked/toyota/Toyota Diagnostics'; CUW=ROOT/'Calibration Update Wizard'; ART=REPO/'data/generated/techstream_v18/cuw_writer_protocol_grammar.json'; FW=(REPO/'firmware/RH850_P1M-E_CodeFlash.bin').read_bytes()
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


print('\n== formerly bounded SecurityAccess families ==')
sec_body=raw('TCUWP4CanSecurityChassisShrinkPrepareWriter.dll',0x1420,840)
check('security chassis body imports ECUAuthKey in SA builder',bytes.fromhex('b8300010') in sec_body)
check('security chassis body imports security-up key transform',bytes.fromhex('c0300010') in sec_body)

print('\n== MMC exact legacy grammar ==')
mmc_r0301=raw('TCUWCanMMCFlashWriter.dll',0x1830,390)
mmc_r0304=raw('TCUWCanMMCFlashWriter.dll',0x12f0,212)
mmc_rff00=raw('TCUWCanMMCFlashWriter.dll',0x19c0,540)
check('MMC routine 0301 encoded on wire',bytes.fromhex('31010301') in mmc_r0301 and bytes.fromhex('71010301') in mmc_r0301)
check('MMC routine 0304 encoded on wire',bytes.fromhex('31010304') in mmc_r0304 and bytes.fromhex('71010304') in mmc_r0304)
check('MMC routine FF00 encoded on wire',bytes.fromhex('3101ff00') in mmc_rff00 and bytes.fromhex('7101ff00') in mmc_rff00)

print('\n== Unified EachArea exact request-download closure ==')
each=raw('TCUWCanUnifiedFlashWriterEachArea.dll',0x1420,855)
check('EachArea RequestDownload sets SID 34',b'\x34' in each)
check('EachArea RequestDownload contains address/length format 46',b'\x46' in each)
check('EachArea parses positive SID 74',b'\x74' in each)
check('EachArea caps negotiated block at 0x0FFF',bytes.fromhex('ff0f0000') in each)

print('\n== decisive body pins for formerly bounded families ==')
for x in obj['decisive_function_identities']:
 body=raw(x['binary'],x['va']-0x10000000,x['size'])
 check(x['role']+' raw body identity',hashlib.sha256(body).hexdigest()==x['sha256'])

print('\n== surviving Unified closure (normal + EachArea + UnifiedUtils) ==')
import struct
clo=obj['unified_survivor_closure']
for x in clo['pinned_bodies']:
 body=raw(x['binary'],x['va']-0x10000000,x['size'])
 check('survivor pin '+x['role']+' raw body identity',hashlib.sha256(body).hexdigest()==x['sha256'])
step=raw('TCUWCanUnifiedFlashWriterEachArea.dll',0x1cf0,596)
check('EachArea step encodes the bit-3 rule as shr dl,3 / and dl,1',bytes.fromhex('c0ea03') in step and bytes.fromhex('80e201') in step)
uu=pefile.PE(str(CUW/'TCUWUnifiedUtils.dll'))
recs=[{'index':i,'selector':struct.unpack_from('<I',r,0x204)[0],'key_string':r.split(b'\x00')[0].decode('ascii')} for i in range(17) for r in [uu.get_data(0x51b0+i*0x208,0x208)]]
check('wrap-key selector table re-parse matches artifact',recs==clo['wrap_key_selector_table']['records'] and len(recs)==17)
check('wrap-key record 0 is the selector-0 CommonPrepareWriter key',recs[0]=={'index':0,'selector':0,'key_string':'B45B26D6344FD60E80BC01D63C7584A0'})
check('wrap-key records 7 and 8 are identical',recs[7]['key_string']==recs[8]['key_string'])
check('CalcSeedKey hardcodes selector 0 before resolver call',raw('TCUWUnifiedUtils.dll',0x2b6e,2)==bytes.fromhex('6a00'))
for w in ['TCUWCanUnifiedPrepareWriter.dll','TCUWCanUnifiedFlashWriter.dll','TCUWCanUnifiedFlashWriterEachArea.dll']:
 pe=pefile.PE(str(CUW/w)); names=' '.join((s.name.decode('latin1') if s.name else '')+' '+lib.dll.decode('latin1') for lib in pe.DIRECTORY_ENTRY_IMPORT for s in lib.imports)
 check(w+' imports no repro-method/data-format/digest facility',not any(t in names for t in clo['negative_import_evidence']['forbidden_substrings']))
print('\n== shared legacy common-flash grammar ==')
for x in obj['common_flash_function_identities']:
 body=raw(x['binary'],x['va']-0x10000000,x['size'])
 check('common flash '+x['role']+' body identity',hashlib.sha256(body).hexdigest()==x['sha256'])

print('\n== target boot SecurityAccess contract ==')
# Corpus body is SHA-bound to raw firmware; semantic assertion is kept alongside raw identity.
rec=None
for line in (REPO/'data/generated/decompilations.jsonl').open():
 r=json.loads(line)
 if r.get('entry_addr')=='0x00005328': rec=r; break
check('request-seed function present',rec is not None)
if rec:
 size=rec['body_size']; check('request-seed raw body identity',hashlib.sha256(FW[0x5328:0x5328+size]).hexdigest()=='a99760a108a56907f1b4646d826a10d031415d107721909409af511ea575350c')

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

print('\n== raw-template scanner/regeneration ==')
# The scanner covers every referenced writer plus support DLLs and preserves encoded store bytes.
with tempfile.TemporaryDirectory() as td:
 out=Path(td)/'x.json'; r=subprocess.run([sys.executable,str(REPO/'tools/techstream/generate_cuw_writer_protocol_grammar.py'),'--root',str(ROOT),'--output',str(out)],check=False)
 check('generator exits',r.returncode==0);check('byte-identical regeneration',out.read_bytes()==ART.read_bytes())
print(f'\nResults: {p} passed, {f} failed');raise SystemExit(1 if f else 0)
