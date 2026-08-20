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

print('\n== surviving Unified closure (normal + EachArea + UnifiedUtils) ==')
import struct
clo=obj['unified_survivor_closure']
for x in clo['pinned_bodies']:
 body=raw(x['binary'],x['va']-0x10000000,x['size'])
 check('survivor pin '+x['role']+' raw body identity',hashlib.sha256(body).hexdigest()==x['sha256'])
PARENT_VERIFIED={'unified_main_worker':'e62369e56a5b3b0226f7bcfeebc024d7196877a70289ce79467cd4739917abec','unified_download_write_step':'8ab8407ad57ca0aea5ac2a2ffd5ed10b8d65dcc6850e9dd2131e630faac24b3f','unified_request_download':'ab7e07d2c8d5602f34892c751329726f397bd07213fa3c641da5b211813f9cde','unified_transfer_data':'9fbc28e4c9eaa5c54f4434ec8305bdc8a4331d9b884e107b32f74ccb680e0eee','unified_routine_control':'35688924d8dc13d88d1c32acf009c129140878ed8850f1c2450629ad349f1862','each_area_download_write_step':'511f155fa5c6dac06606d34aa32e65a5b20d66a622d9b87bd01b8662ebaa7b80','each_area_main_worker':'43e89745fb42a09003996a45dd6bf03aff45501e86842f04364615a61a746e99','make_send_data':'c2e0050b01d1cbd114ee0d63e49c7525766d6084dcc5030abbd1828c91bf8fbf'}
for x in clo['pinned_bodies']:
 if x['role'] in PARENT_VERIFIED: check(x['role']+' matches parent-verified hash',x['sha256']==PARENT_VERIFIED[x['role']])
check('RequestDownload grammar exact byte order',clo['request_download']['grammar']=='34 || dataFormatIdentifier || 46 || addressSpaceByte || (OffsetAddress[5] + areaStart) || areaLength')
sp2=clo['security_property2']
check('SecurityProperty2 is hex-decoded (98 -> 0x98 -> 1)',sp2['example']=={'public_string':'98','decoded_first_byte':'0x98','dataFormatIdentifier':1} and 'not a character code' in sp2['boundary'])
step=raw('TCUWCanUnifiedFlashWriterEachArea.dll',0x1cf0,596)
check('EachArea step encodes the bit-3 rule as shr dl,3 / and dl,1',bytes.fromhex('c0ea03') in step and bytes.fromhex('80e201') in step)
uu=pefile.PE(str(CUW/'TCUWUnifiedUtils.dll'))
recs=[{'index':i,'selector':struct.unpack_from('<I',r,0x204)[0],'key_string':r.split(b'\x00')[0].decode('ascii')} for i in range(17) for r in [uu.get_data(0x51b0+i*0x208,0x208)]]
check('wrap-key selector table re-parse matches artifact',recs==clo['wrap_key_selector_table']['records'] and len(recs)==17)
check('wrap-key record 0 is the selector-0 CommonPrepareWriter key',recs[0]=={'index':0,'selector':0,'key_string':'B45B26D6344FD60E80BC01D63C7584A0'})
check('wrap-key records 7 and 8 are identical',recs[7]['key_string']==recs[8]['key_string'])
check('records 1-16 stated present but not proven reachable','not proven reachable' in clo['wrap_key_selector_table']['reachability']['records_1_16'])
check('CalcSeedKey hardcodes selector 0 before resolver call',raw('TCUWUnifiedUtils.dll',0x2b6e,2)==bytes.fromhex('6a00'))
for w in ['TCUWCanUnifiedPrepareWriter.dll','TCUWCanUnifiedFlashWriter.dll','TCUWCanUnifiedFlashWriterEachArea.dll']:
 pe=pefile.PE(str(CUW/w)); names=' '.join((s.name.decode('latin1') if s.name else '')+' '+lib.dll.decode('latin1') for lib in pe.DIRECTORY_ENTRY_IMPORT for s in lib.imports)
 check(w+' imports no repro-method/data-format/digest facility',not any(t in names for t in clo['negative_import_evidence']['forbidden_substrings']))
check('artifact records zero forbidden-import hits',all(not v['forbidden_hits'] for v in clo['negative_import_evidence']['per_binary'].values()))
check('host verification claim excludes host-side digests','performs any host-side CRC/CMAC/DigitalSignature/hash verification' in clo['host_verification']['claim'] and 'neither surviving Unified flash writer' in clo['host_verification']['claim'])
check('MakeSendData documented as copy-only with no host transform','no host encryption, compression, or hash transform' in clo['make_send_data']['semantics'])
ea=clo['image_area_sequencing']['TCUWCanUnifiedFlashWriterEachArea.dll']; nw=clo['image_area_sequencing']['TCUWCanUnifiedFlashWriter.dll']
check('EachArea re-sends 0203/0201/0202 predownload per area group','re-sent' in ea['predownload'])
check('EachArea routine order 10F0/FF00/10F1/10F2 with exact conditionals','conditional 10F0' in ea['routines_per_area'] and 'FF00 (tag 1) always' in ea['routines_per_area'] and 'conditional 10F1' in ea['routines_per_area'])
check('normal writer sends predownload once per CPU image before the area loop','once per CPU image' in nw['predownload'] and 'before the area loop' in nw['predownload'])
check('both surviving routes end with 11 01 plus raw J2534 tail frames',all('11 01' in x['last_cpu_image_tail'] and 'raw J2534' in x['last_cpu_image_tail'] for x in (ea,nw)))
check('family evidence EachArea download uses corrected byte order',obj['family_evidence']['UnifiedEachArea']['download'].startswith('34 || dataFormatIdentifier || 46 || addressSpaceByte'))
check('route reasons and mirrored artifacts carry the corrected order',all('dataFormatIdentifier' in x['reason'] for x in obj['route_families'] if x['prepare_writer']=='TCUWCanUnifiedPrepareWriter.dll'))
check('closure marks field provenance authoritative over one-line mirrors','cuw_writer_family_matrix.json' in clo['request_download']['supersedes'] and 'authoritative' in clo['request_download']['supersedes'])

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
