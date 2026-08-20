#!/usr/bin/env python3
"""Generate CUW writer byte-template grammar and Sienna/H boot compatibility.

The byte scanner is intentionally conservative: it records immediate stores to
request/response buffers as raw x86 little-endian bytes. Semantic route verdicts
are promoted only for writer families whose decisive mismatch/match is separately
pinned by deterministic tests or existing firmware-static findings.
"""
from __future__ import annotations
import argparse, collections, csv, hashlib, io, json, struct
from pathlib import Path
from typing import Any
import pefile
import sys

REPO=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(REPO))
from tools.techstream.generate_cuw_writer_inventory import decode_parameter_ini, factory_routes

ROOT=REPO/'Techstream/unpacked/toyota/Toyota Diagnostics'
CUW=ROOT/'Calibration Update Wizard'
OUT=REPO/'data/generated/techstream_v18/cuw_writer_protocol_grammar.json'

SUPPORT={'TCUWCanCommonPrepareWriter.dll','TCUWCanCommonFlashWriter.dll','TCUWUnifiedUtils.dll','TCUWHINOUtils.dll','TCUWSBRUtils.dll','TCUWPSAUtils.dll','TCUWCanDiagCommUtils.dll'}
UDS={0x10,0x11,0x22,0x27,0x28,0x2e,0x31,0x34,0x36,0x37,0x3e,0x85}
POS={0x50,0x51,0x62,0x67,0x68,0x6e,0x71,0x74,0x76,0x77,0x7e,0xc5}

# Decisive, evidence-bounded compatibility classes. Wildcards are prefix matches.
PREP_CLASS={
 'TCUWCanUnifiedPrepareWriter.dll':('candidate','18-byte 27 01 || ECUAuthKey and 18-byte 27 02 || derived key'),
 'TCUWCanReproStdPrepareWriter.dll':('rejected','bare 2-byte 27 01 conflicts with target exact 18-byte request-seed policy'),
 'TCUWEthernetReprostdPrepareWriter.dll':('rejected','ReproStd family plus Ethernet transport'),
 'TCUWP4CanBodyPrepareWriter.dll':('rejected','SecurityAccess 61/62 subfunctions are unsupported by target bootloader'),
 'TCUWP4CanAirbagPrepareWriter.dll':('rejected','SecurityAccess 03/04 subfunctions are unsupported by target bootloader'),
 'TCUWP4CanClearanceSonarPrepareWriter.dll':('rejected','SecurityAccess 03/04 subfunctions are unsupported by target bootloader'),
 'TCUWP4CanSecurityAirbagPrepareWriter.dll':('rejected','SecurityAccess 03/04 subfunctions are unsupported by target bootloader'),
 'TCUWP4CanChassisShrinkPrepareWriter.dll':('rejected','3-byte 27 01 request conflicts with target exact 18-byte request-seed policy'),
 'TCUWP4CanSecurityChassisShrinkPrepareWriter.dll':('rejected','27 01 || dynamic selector byte || ECUAuthKey[16] is 19-byte application payload, conflicting with target exact 18-byte request-seed policy'),
 'TCUWP4CanPowerTrainPrepareWriter.dll':('rejected','short/common SecurityAccess class; flash pairings are independently incompatible'),
 'TCUWP5CanPowerTrainPrepareWriter.dll':('rejected','exact builder sends bare 27 01 then derives a 4-byte response key; target requires 27 01 || 16 tester bytes'),
 'TCUWP4P5CanPowerTrainPrepareWriter.dll':('rejected','exact builder sends bare 27 01, receives a 4-byte seed, and sends a 4-byte derived key; target requires 27 01 || 16 tester bytes'),
 'TCUWP4CanCentralGWPrepareWriter.dll':('rejected','prepare delegates a gateway callback; paired P4 body flash uses legacy raw common-flash framing rather than target UDS boot grammar'),
 'TCUWP5CanPowerTrainPrepareWriterForBodyMicon.dll':('rejected','exact builder sends bare 27 01 before a 6-byte seed/key exchange; target requires 16 tester bytes in request-seed'),
 'TCUWP5CanPowerTrainPrepareWriterForSolar.dll':('rejected','exact builder sends bare 27 01 then derives a 4-byte response key; target requires 27 01 || 16 tester bytes'),
 'TCUWCanSBRPrepareWriter.dll':('rejected','SecurityAccess 33/34 and vendor-session grammar unsupported by target'),
 'TCUWCanHINOPrepareWriter.dll':('rejected','SecurityAccess 03/04 HINO family unsupported by target'),
 'TCUWCanHINOPrepareWriterForVCS.dll':('rejected','SecurityAccess 03/04 HINO family unsupported by target'),
 'TCUWCanHINOPrepareWriterForDSS.dll':('rejected','SecurityAccess 03/04 HINO family unsupported by target'),
 'TCUWCanPSAPrepareWriter.dll':('rejected','legacy PSA authentication/SID family unsupported by target'),
 'TCUWP5CanSecurityPowerTrainPrepareWriter.dll':('candidate','18-byte 27 01 || ECUAuthKey shape matches, but paired flash/routine grammar decides route'),
 'TCUWCanMMCPrepareWriter.dll':('rejected','exact MMC SecurityAccess uses subfunctions 41/42; flash additionally uses unsupported RIDs 0301/0304'),
}


def events(pe:pefile.PE):
 out=[]
 for sec in pe.sections:
  if not (sec.Characteristics & 0x20000000): continue
  b=sec.get_data(); base=sec.VirtualAddress; i=0
  while i<len(b)-4:
   # mov byte ptr [mem], imm8
   if b[i]==0xc6 and (b[i+1]&0xc0)!=0xc0:
    modrm=b[i+1]; mod,rm=modrm>>6,modrm&7; j=i+2; disp=None
    if rm==4:
     sib=b[j]; j+=1
     if (sib&7)==5 and mod==0: disp=struct.unpack_from('<I',b,j)[0]; j+=4
    elif rm==5 and mod==0: disp=struct.unpack_from('<I',b,j)[0]; j+=4
    if mod==1: j+=1; disp=None
    elif mod==2: disp=struct.unpack_from('<I',b,j)[0]; j+=4
    if j<len(b): out.append((base+i,disp,bytes([b[j]]))); i=j+1; continue
   # mov word ptr [mem], imm16 -- preserve encoded little-endian bytes (wire order on x86 store)
   if b[i:i+2]==b'\x66\xc7' and (b[i+2]&0xc0)!=0xc0:
    modrm=b[i+2]; mod,rm=modrm>>6,modrm&7; j=i+3; disp=None
    if rm==4:
     sib=b[j]; j+=1
     if (sib&7)==5 and mod==0: disp=struct.unpack_from('<I',b,j)[0]; j+=4
    elif rm==5 and mod==0: disp=struct.unpack_from('<I',b,j)[0]; j+=4
    if mod==1: j+=1; disp=None
    elif mod==2: disp=struct.unpack_from('<I',b,j)[0]; j+=4
    if j+2<=len(b): out.append((base+i,disp,b[j:j+2])); i=j+2; continue
   i+=1
 return out

def chains(evs,max_gap=48):
 out=[]; cur=None
 for rva,disp,bs in evs:
  if disp is None: continue
  if cur and disp==cur[0]+len(cur[1]) and rva-cur[2][-1]<=max_gap:
   cur[1]+=bs; cur[2].append(rva); continue
  if cur and len(cur[1])>=2: out.append(cur)
  cur=[disp,bytearray(bs),[rva]]
 if cur and len(cur[1])>=2: out.append(cur)
 return out

def scan(path:Path)->dict[str,Any]:
 data=path.read_bytes(); pe=pefile.PE(data=data)
 ts=[]
 for disp,bb,rvas in chains(events(pe)):
  raw=bytes(bb); k='uds-request' if raw[0] in UDS else 'uds-positive-response' if raw[0] in POS else 'other'
  if k!='other' or len(raw)>=3: ts.append({'rva':rvas[0],'bytes':raw.hex(' '),'length':len(raw),'kind':k})
 imports=[]
 for lib in getattr(pe,'DIRECTORY_ENTRY_IMPORT',[]):
  dll=lib.dll.decode('latin1')
  for s in lib.imports:
   imports.append({'dll':dll,'name':s.name.decode('latin1') if s.name else f'ordinal:{s.ordinal}'})
 return {'name':path.name,'sha256':hashlib.sha256(data).hexdigest(),'templates':ts,'imports':imports}

# Ghidra-derived function extents for decisive formerly-bounded families.  The
# artifact hashes the raw PE bodies; tests re-derive those hashes without a live
# Ghidra project.  Semantic descriptions below come from those pinned bodies.
DECISIVE_FUNCTIONS={
 'TCUWCanMMCPrepareWriter.dll':[(0x100010c0,259,'mmc_session_10_02'),(0x10001250,519,'mmc_seed_key_transform'),(0x100016a0,703,'mmc_security_access_41_42')],
 'TCUWCanMMCFlashWriter.dll':[(0x100010d0,284,'mmc_transfer_data'),(0x100011f0,249,'mmc_transfer_exit'),(0x100012f0,212,'mmc_routine_0304'),(0x100013d0,169,'mmc_suppressed_reset'),(0x10001550,736,'mmc_request_download'),(0x10001830,390,'mmc_routine_0301'),(0x100019c0,540,'mmc_routine_ff00')],
 'TCUWP5CanPowerTrainPrepareWriter.dll':[(0x10001130,1064,'p5_powertrain_security_access')],
 'TCUWP4P5CanPowerTrainPrepareWriter.dll':[(0x100016a0,1150,'p4p5_powertrain_security_access')],
 'TCUWP5CanPowerTrainPrepareWriterForBodyMicon.dll':[(0x10001130,596,'p5_body_micon_security_access')],
 'TCUWP5CanPowerTrainPrepareWriterForSolar.dll':[(0x10001140,1064,'p5_solar_security_access')],
 'TCUWP4CanSecurityChassisShrinkPrepareWriter.dll':[(0x10001420,840,'security_chassis_security_access')],
 'TCUWP4CanCentralGWPrepareWriter.dll':[(0x10001000,156,'central_gateway_prepare_callback')],
 'TCUWCanCommonFlashWriter.dll':[(0x10001ac0,976,'legacy_common_check_id'),(0x100024f0,299,'legacy_common_finish_reprogramming')],
 'TCUWCanUnifiedFlashWriterEachArea.dll':[(0x100010f0,816,'each_area_predownload'),(0x10001420,855,'each_area_request_download'),(0x100019c0,239,'each_area_reset'),(0x10001f80,832,'each_area_routine_control')],
}

FAMILY_EVIDENCE={
 'MMC':{'security_access':'27 41 -> 67 41 (8-byte seed), then 27 42 || 8-byte derived key -> 67 42','download':'34 || dataFormat || 44 || address[4] || size[4]; 74 20 response; max block capped at 0x0FFF','transfer':'36/counter/data -> 76/counter; 37 -> 77','routines':['0301','FF00','0304'],'reset':'11 81 (suppressed hard reset)','target_disposition':'rejected: SA 41/42 -> NRC 0x12; RIDs 0301/0304 -> NRC 0x31'},
 'P5PowerTrain':{'security_access':'bare 27 01 -> 4-byte seed; 27 02 || 4-byte derived key','session':'10 02 -> 50 02','target_disposition':'rejected: exact target request-seed length is 18 bytes'},
 'P4P5PowerTrain':{'security_access':'bare 27 01 -> 4-byte seed; 27 02 || 4-byte derived key; parameter-driven WaitTimeAfterSeedData/Key','target_disposition':'rejected: exact target request-seed length is 18 bytes'},
 'P5BodyMicon':{'security_access':'bare 27 01 -> 6-byte seed; 27 02 || 6-byte derived key','target_disposition':'rejected: exact target request-seed length is 18 bytes'},
 'P5Solar':{'security_access':'bare 27 01 -> 4-byte seed; 27 02 || 4-byte derived key','session':'10 02 -> 50 02','target_disposition':'rejected: exact target request-seed length is 18 bytes'},
 'SecurityChassisShrink':{'security_access':'27 01 || dynamic selector[1] || ECUAuthKey[16]; 27 02 || CalcSeedKeyForSecurityUp[16]','target_disposition':'rejected: request-seed application payload is 19 bytes, one byte longer than target exact policy'},
 'CentralGW+BodyFlash':{'prepare':'CentralGW prepare invokes host callback and waits WaitTimeAfterReprogrammingMode','flash':'P4 BodyFlash delegates to legacy CCanCommonFlashWriter; FinishReprogramming writes raw command byte 0x80 after CAN address prefix','target_disposition':'rejected: legacy raw common-flash protocol is not target UDS boot grammar'},
 'UnifiedEachArea':{'predownload':'2E 0203||OffsetAddress[5] -> 2E 0201||SeedKey[16] -> 2E 0202||Nonce[16]','download':'34 || compressionFlag || areaFlag || 46 || (OffsetAddress[5]+areaStart) || areaSize; parses 74 and caps block at 0x0FFF','routines':['10F0','FF00','10F1','10F2'],'reset':'11 01 -> 51 01','target_disposition':'byte-compatible with tracked target boot grammar; exact calibration selection/values remain runtime/package-bounded'},
}

def decisive_function_identities(root:Path)->list[dict[str,Any]]:
 out=[]
 for name,funcs in DECISIVE_FUNCTIONS.items():
  path=root/'Calibration Update Wizard'/name; data=path.read_bytes(); pe=pefile.PE(data=data); base=pe.OPTIONAL_HEADER.ImageBase
  for va,size,role in funcs:
   body=pe.get_data(va-base,size)
   out.append({'binary':name,'binary_sha256':hashlib.sha256(data).hexdigest(),'va':va,'size':size,'role':role,'sha256':hashlib.sha256(body).hexdigest()})
 return out


ROUTE_TIMING_KEYS=(
 'WaitTimeAfterSeedData','WaitTimeAfterSeedKey','WaitTimeAfterReprogrammingMode',
 'WaitTimeAfterFlashWrite','WaitTimeAfterEndOfFlashing','ReceiveTimeoutBeforeFlashWrite',
 'ReceiveTimeoutBeforeInitialCommand','ReceiveTimeoutBeforePrepareRetry','WaitTimeBetweenSF',
 'PrepareRetryFlag','IGOffRetriableFlag','WaitTimeAfterIGOnAtRetry',
)

def factory_parameter_rows(root:Path)->list[dict[str,str]]:
 out=[]
 for path in sorted((root/'Calibration Update Wizard/Ini').glob('*.ini'),key=lambda p:p.name.lower()):
  try:
   rows=list(csv.reader(io.StringIO(decode_parameter_ini(path.read_bytes()).decode('latin1'))))
  except Exception:
   continue
  if len(rows)<2 or 'DLLFileNameForPrepareWrite' not in rows[0]: continue
  header=rows[0]
  for row in rows[1:]:
   row=row+['']*(len(header)-len(row)); out.append(dict(zip(header,row)))
 return out

def route_parameter_profile(rows:list[dict[str,str]])->dict[str,list[str]]:
 return {key:sorted({r.get(key,'') for r in rows}) for key in ROUTE_TIMING_KEYS}

def route_verdict(p:str,f:str)->tuple[str,str]:
 pc,why=PREP_CLASS.get(p,('unresolved','no exact decisive target grammar recovered'))
 if p=='TCUWCanUnifiedPrepareWriter.dll':
  if f=='TCUWCanUnifiedFlashWriter.dll': return 'byte-compatible','18-byte SA; exact 0203->0201->0202 WDBI; RIDs 10F0/FF00/10F1/10F2; 34 format 46; 36/37; 11 01 all match target boot grammar; exact calibration selection/values remain bounded'
  if f=='TCUWCanUnifiedFlashWriterEachArea.dll': return 'byte-compatible','same 18-byte SA and 0203->0201->0202 predownload; per-area RequestDownload is now recovered as 34 || flags || 46 || (OffsetAddress[5]+areaStart) || areaSize, with the same 10F0/FF00/10F1/10F2 and 11 01 family'
 if p=='TCUWCanReproStdPrepareWriter.dll': return 'rejected','2-byte 27 01 -> target NRC 0x13; standard RIDs 10F5/10F6 absent -> NRC 0x31'
 if p=='TCUWP5CanSecurityPowerTrainPrepareWriter.dll':
  return 'rejected','18-byte SA shape matches but RID 0x1003 and paired VFOREST/M16C flash grammar are target-incompatible'
 # An independently incompatible flash family is enough to reject the full route.
 if 'VFOREST' in f: return 'rejected','proprietary VFOREST nonce/seed framing has no target boot handler'
 if 'M16C' in f: return 'rejected','legacy M16C password/material-transfer grammar has no target boot handler'
 if pc=='candidate': return 'compatible-bounded',why
 return pc,why

def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--root',type=Path,default=ROOT); ap.add_argument('--output',type=Path,default=OUT); a=ap.parse_args()
 routes,_=factory_routes(a.root.resolve()); pairs=collections.Counter((r['prepare_writer'],r['flash_writer']) for r in routes)
 parameter_rows=factory_parameter_rows(a.root.resolve())
 by_pair=collections.defaultdict(list)
 for row in parameter_rows:
  by_pair[(row.get('DLLFileNameForPrepareWrite',''),row.get('DLLFileNameForFlashWrite',''))].append(row)
 names=sorted({x for pair in pairs for x in pair if x}|SUPPORT)
 scans={n:scan(a.root/'Calibration Update Wizard'/n) for n in names if (a.root/'Calibration Update Wizard'/n).is_file()}
 fam=[]; counts=collections.Counter()
 for (p,f),n in pairs.most_common():
  verdict,reason=route_verdict(p,f); counts[verdict]+=n
  reset_templates=sorted({t['bytes'] for t in scans.get(f,{}).get('templates',[]) if t['bytes'].startswith('11 ')})
  fam.append({'prepare_writer':p,'flash_writer':f,'factory_rows':n,'verdict_sienna_8965B4512000':verdict,'verdict_corolla_8965H1202000':verdict,'reason':reason,'timing_retry_profile':route_parameter_profile(by_pair[(p,f)]),'reset_templates':reset_templates})
 obj={'schema_version':2,'distribution':'Toyota Techstream V18.00.003','writer_scans':scans,'route_families':fam,'verdict_counts':dict(sorted(counts.items())),'decisive_function_identities':decisive_function_identities(a.root.resolve()),'family_evidence':FAMILY_EVIDENCE,
 'target_boot_grammar':{'request_seed':'27 01 || 16 tester bytes; exact request length 0x12','send_key':'27 02 || 16-byte key','wdbi_order':'0203(5)->0201(16)->0202(16)','routine_ids':['10F0','10F1','10F2','10F3','FF00'],'note':'Corolla-H boot/UDS target grammar is independently transferred target-natively in tracked variant tests'},
 'evidence_boundary':'all 196 decoded factory rows now have an exact static target disposition: two Unified-family rows are byte-compatible with the tracked boot grammar and 194 rows have at least one byte/decompilation-pinned mismatch. Exact factory-row selection and calibration values still require the matching package/live session.'}
 a.output.parent.mkdir(parents=True,exist_ok=True); a.output.write_text(json.dumps(obj,indent=2,sort_keys=True)+'\n'); return 0
if __name__=='__main__': raise SystemExit(main())
