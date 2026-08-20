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


print('\n== formerly bounded SecurityAccess families ==')
def templates(name): return {x['bytes'] for x in obj['writer_scans'][name]['templates']}
for name in ['TCUWP5CanPowerTrainPrepareWriter.dll','TCUWP4P5CanPowerTrainPrepareWriter.dll','TCUWP5CanPowerTrainPrepareWriterForBodyMicon.dll','TCUWP5CanPowerTrainPrepareWriterForSolar.dll']:
 check(name+' exposes bare 27 01 / 27 02 templates',{'27 01','27 02','67 01','67 02'} <= templates(name))
check('security chassis has 27 01/02 family',{'27 01','27 02','67 01','67 02'} <= templates('TCUWP4CanSecurityChassisShrinkPrepareWriter.dll'))
# The security-chassis body calls both GetECUAuthKey and CalcSeedKeyForSecurityUp;
# Ghidra shows a dynamic selector byte inserted between 27 01 and the 16-byte ECUAuthKey.
sec_body=raw('TCUWP4CanSecurityChassisShrinkPrepareWriter.dll',0x1420,840)
check('security chassis body imports ECUAuthKey in SA builder',bytes.fromhex('b8300010') in sec_body)
check('security chassis body imports security-up key transform',bytes.fromhex('c0300010') in sec_body)

print('\n== MMC exact legacy grammar ==')
check('MMC prepare exposes SA 41/42',{'27 41','67 41','27 42','67 42'} <= templates('TCUWCanMMCPrepareWriter.dll'))
mmc_r0301=raw('TCUWCanMMCFlashWriter.dll',0x1830,390)
mmc_r0304=raw('TCUWCanMMCFlashWriter.dll',0x12f0,212)
mmc_rff00=raw('TCUWCanMMCFlashWriter.dll',0x19c0,540)
check('MMC routine 0301 encoded on wire',bytes.fromhex('31010301') in mmc_r0301 and bytes.fromhex('71010301') in mmc_r0301)
check('MMC routine 0304 encoded on wire',bytes.fromhex('31010304') in mmc_r0304 and bytes.fromhex('71010304') in mmc_r0304)
check('MMC routine FF00 encoded on wire',bytes.fromhex('3101ff00') in mmc_rff00 and bytes.fromhex('7101ff00') in mmc_rff00)
check('MMC reset is suppressed 11 81', '11 81' in templates('TCUWCanMMCFlashWriter.dll'))

print('\n== Unified EachArea exact request-download closure ==')
each=raw('TCUWCanUnifiedFlashWriterEachArea.dll',0x1420,855)
check('EachArea RequestDownload sets SID 34',b'\x34' in each)
check('EachArea RequestDownload contains address/length format 46',b'\x46' in each)
check('EachArea parses positive SID 74',b'\x74' in each)
check('EachArea caps negotiated block at 0x0FFF',bytes.fromhex('ff0f0000') in each)
check('EachArea exact predownload order', [x['bytes'] for x in obj['writer_scans']['TCUWCanUnifiedFlashWriterEachArea.dll']['templates'][:6]] == ['2e 02 03','6e 02 03','2e 02 01','6e 02 01','2e 02 02','6e 02 02'])

print('\n== decisive body pins for formerly bounded families ==')
for x in obj['decisive_function_identities']:
 body=raw(x['binary'],x['va']-0x10000000,x['size'])
 check(x['role']+' raw body identity',hashlib.sha256(body).hexdigest()==x['sha256'])

print('\n== shared legacy common-flash grammar ==')
check('15 referenced flash writers import CCanCommonFlashWriter',len(obj['common_flash_users'])==15)
check('shared common-flash grammar is explicitly proprietary','not UDS SIDs' in obj['common_flash_grammar']['framing'])
expected_common={'CheckFinishReprogramming':'0x3E','ChangeNextCpu':'0x65','FinishReprogramming':'0x80','GetStatusOnce':'0x50'}
check('fixed common-flash command bytes exact',all(obj['common_flash_grammar']['commands'][k].startswith(v) for k,v in expected_common.items()))
check('nonce/seed common-flash sequences exact','0x37 -> 0x38 -> 0x39' in obj['common_flash_grammar']['commands']['SendNonce'] and '0x3A -> 0x3B -> 0x3C' in obj['common_flash_grammar']['commands']['SendSeedKey'])
check('erase/verify variants exact','0x25' in obj['common_flash_grammar']['commands']['EraseBlock'] and '0x26' in obj['common_flash_grammar']['commands']['EraseBlock'] and '0x15' in obj['common_flash_grammar']['commands']['VerifyBlock'] and '0x16' in obj['common_flash_grammar']['commands']['VerifyBlock'])
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
check('verdict counts fully closed',obj['verdict_counts']=={'byte-compatible':2,'rejected':194},repr(obj['verdict_counts']))
uni=[x for x in obj['route_families'] if x['prepare_writer']=='TCUWCanUnifiedPrepareWriter.dll']
std=next(x for x in obj['route_families'] if x['prepare_writer']=='TCUWCanReproStdPrepareWriter.dll')
check('both Unified route rows are byte-compatible',sum(x['factory_rows'] for x in uni)==2 and all(x['verdict_sienna_8965B4512000']=='byte-compatible' for x in uni))
check('standard route rejected by exact grammar',std['factory_rows']==2 and std['verdict_sienna_8965B4512000']=='rejected')
check('no unresolved/bounded route rows remain',all(x['verdict_sienna_8965B4512000'] in {'byte-compatible','rejected'} for x in obj['route_families']))

print('\n== per-route timing/retry/reset profiles ==')
timing_keys={'WaitTimeAfterSeedData','WaitTimeAfterSeedKey','WaitTimeAfterReprogrammingMode','WaitTimeAfterFlashWrite','WaitTimeAfterEndOfFlashing','ReceiveTimeoutBeforeFlashWrite','ReceiveTimeoutBeforeInitialCommand','ReceiveTimeoutBeforePrepareRetry','WaitTimeBetweenSF','PrepareRetryFlag','IGOffRetriableFlag','WaitTimeAfterIGOnAtRetry'}
check('all 32 routes carry complete timing/retry key set',len(obj['route_families'])==32 and all(set(x['timing_retry_profile'])==timing_keys for x in obj['route_families']))
unified_routes=[x for x in obj['route_families'] if x['prepare_writer']=='TCUWCanUnifiedPrepareWriter.dll']
check('both compatible Unified rows have modern blank seed timing and IG-off retry enabled',all(x['timing_retry_profile']['WaitTimeAfterSeedData']==[''] and x['timing_retry_profile']['WaitTimeAfterSeedKey']==[''] and x['timing_retry_profile']['IGOffRetriableFlag']==['1'] for x in unified_routes))
check('both compatible Unified flash variants expose 11 01 reset template',all(x['reset_templates']==['11 01'] for x in unified_routes))
mmc_route=next(x for x in obj['route_families'] if x['prepare_writer']=='TCUWCanMMCPrepareWriter.dll')
check('MMC profile pins 400ms end wait and suppressed 11 81 reset',mmc_route['timing_retry_profile']['WaitTimeAfterEndOfFlashing']==['400'] and mmc_route['reset_templates']==['11 81'])

print('\n== raw-template scanner/regeneration ==')
# The scanner covers every referenced writer plus support DLLs and preserves encoded store bytes.
matrix=json.loads((REPO/'data/generated/techstream_v18/cuw_writer_family_matrix.json').read_text())
referenced={x['name'] for x in matrix['writers']}
check('all 47 referenced writers have scans',len(referenced)==47 and referenced <= set(obj['writer_scans']))
with tempfile.TemporaryDirectory() as td:
 out=Path(td)/'x.json'; r=subprocess.run([sys.executable,str(REPO/'tools/techstream/generate_cuw_writer_protocol_grammar.py'),'--root',str(ROOT),'--output',str(out)],check=False)
 check('generator exits',r.returncode==0);check('byte-identical regeneration',out.read_bytes()==ART.read_bytes())
print(f'\nResults: {p} passed, {f} failed');raise SystemExit(1 if f else 0)
