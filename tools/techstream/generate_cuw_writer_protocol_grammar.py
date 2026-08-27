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

from techstream_paths import V18_DIAGNOSTICS_ROOT
from typing import Any
import pefile
from pe_utils import imports as pe_imports
import sys

REPO=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(REPO))
from tools.techstream.cuw_parameter import decode_parameter_ini, factory_routes_from_ini_root

ROOT=V18_DIAGNOSTICS_ROOT
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
 imports=pe_imports(pe)
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

# Surviving-Unified closure pins.  Bodies are hashed from the raw PE; expected
# sha256 values are enforced at generation time so any binary or extent drift
# fails loudly instead of silently regenerating different semantics.
UNIFIED_SURVIVOR_PINS=[
 # normal Unified flash writer (TCUWCanUnifiedFlashWriter.dll)
 ('TCUWCanUnifiedFlashWriter.dll',0x10002510,1312,'unified_main_worker','e62369e56a5b3b0226f7bcfeebc024d7196877a70289ce79467cd4739917abec'),
 ('TCUWCanUnifiedFlashWriter.dll',0x10001d50,768,'unified_download_write_step','8ab8407ad57ca0aea5ac2a2ffd5ed10b8d65dcc6850e9dd2131e630faac24b3f'),
 ('TCUWCanUnifiedFlashWriter.dll',0x10001420,944,'unified_request_download','ab7e07d2c8d5602f34892c751329726f397bd07213fa3c641da5b211813f9cde'),
 ('TCUWCanUnifiedFlashWriter.dll',0x100017e0,324,'unified_transfer_data','9fbc28e4c9eaa5c54f4434ec8305bdc8a4331d9b884e107b32f74ccb680e0eee'),
 ('TCUWCanUnifiedFlashWriter.dll',0x10002080,1151,'unified_routine_control','35688924d8dc13d88d1c32acf009c129140878ed8850f1c2450629ad349f1862'),
 # EachArea Unified flash writer (TCUWCanUnifiedFlashWriterEachArea.dll);
 # predownload/request-download/reset/routine-control pins already live in DECISIVE_FUNCTIONS
 ('TCUWCanUnifiedFlashWriterEachArea.dll',0x10001cf0,596,'each_area_download_write_step','511f155fa5c6dac06606d34aa32e65a5b20d66a622d9b87bd01b8662ebaa7b80'),
 ('TCUWCanUnifiedFlashWriterEachArea.dll',0x100022d0,1326,'each_area_main_worker','43e89745fb42a09003996a45dd6bf03aff45501e86842f04364615a61a746e99'),
 # shared Unified support module (TCUWUnifiedUtils.dll)
 ('TCUWUnifiedUtils.dll',0x10002c40,108,'make_send_data','c2e0050b01d1cbd114ee0d63e49c7525766d6084dcc5030abbd1828c91bf8fbf'),
 ('TCUWUnifiedUtils.dll',0x10001000,48,'wrap_key_selector_resolver','6b62e4e114f856f932ebe339d3e35399fcaf76742e514c84d7b7ac8ea0e28c2c'),
 ('TCUWUnifiedUtils.dll',0x10002b50,234,'calc_seed_key','a360328e446abdd7aa3d8740bec0191f882c498c402e2b68090497f3e29acecd'),
]

# Import substrings that must not appear in either surviving Unified writer
# (negative evidence: no host-side digest/signature/repro-method consumption).
UNIFIED_FORBIDDEN_IMPORTS=(
 'GetReproMethod','GetDataFormat','GetCompressionAlgorithm','GetEraseBlock','GetALFID',
 'GetDownloadAddress','GetDownloadMemsize','GetRequiredSpecReproVer',
 'DigitalSignature','CMAC','CRC','CryptEncrypt','CryptDecrypt','CryptImportKey',
)

COMMON_FLASH_FUNCTIONS=[
 (0x10001070,503,'WriteBytes'),
 (0x10001270,155,'ReceiveAck'),
 (0x10001360,276,'CheckFinishReprogramming'),
 (0x100014c0,402,'SendNonce'),
 (0x10001670,402,'SendSeedKey'),
 (0x10001820,593,'SendNonceAndSeedKey'),
 (0x10001ac0,976,'CheckIDWithWaitOfSFs'),
 (0x10001ee0,716,'GetMemoryInfo'),
 (0x100021d0,317,'GetStatusOnce'),
 (0x10002310,143,'GetStatus'),
 (0x100023d0,255,'ChangeNextCpu'),
 (0x100024f0,299,'FinishReprogramming'),
 (0x100027d0,309,'DetectFalsify'),
 (0x10002920,431,'CheckBlock'),
 (0x10002af0,465,'EraseBlock'),
 (0x10002ce0,1415,'WriteBlock'),
 (0x100032c0,465,'InVerifyBlock'),
 (0x100034b0,944,'VerifyBlock'),
 (0x10003920,907,'VerifyBlock2'),
]

COMMON_FLASH_GRAMMAR={
 'framing':'proprietary CCanCommonFlashWriter commands follow the caller-supplied 4/5-byte CAN address prefix; command bytes below are not UDS SIDs',
 'ack':'ReceiveAck waits for an exact 5-byte response with command/status byte 0x3C after the address prefix',
 'commands':{
  'CheckFinishReprogramming':'0x3E',
  'SendNonce':'0x37 -> 0x38 -> 0x39, splitting a 16-byte nonce into 6/6/4-byte material chunks',
  'SendSeedKey':'0x3A -> 0x3B -> 0x3C, splitting a 16-byte seed-key blob into 6/6/4-byte material chunks',
  'SendNonceAndSeedKey':'0x37..0x39 nonce then 0x3A..0x3C seed-key',
  'CheckIDWithWaitOfSFs':'five-frame ID/password handshake followed by status traffic; final emitted command 0x3C',
  'GetMemoryInfo':'0x76 preferred, fallback 0x75; parses returned memory geometry then requires ack',
  'GetStatusOnce':'0x50, then status message and ack',
  'ChangeNextCpu':'0x65',
  'FinishReprogramming':'0x80',
  'DetectFalsify':'0x47 followed by status polling while status is 0x50',
  'CheckBlock':'0x35 short-range or 0x36 extended-range; polls with WaitTimeBeforeStatusCheckForBlankCheck',
  'EraseBlock':'0x25 short-range or 0x26 extended-range; polls with WaitTimeBeforeStatusCheckForEraseBlock',
  'WriteBlock':'0x41 starts a block; address + dynamic chunk-size selector follows; 0x45 continues; data chunk is selected by SendDataByteForWriteBlockType (0x100/0x80/0x20 byte classes)',
  'InVerifyBlock':'0x47 short-range or 0x48 extended-range; polls with WaitTimeBeforeStatusCheckForInVerify',
  'VerifyBlock':'0x15 short-range or 0x16 extended-range; sends 0x100-byte chunks and polls WaitTimeBeforeStatusCheckForVerify',
  'VerifyBlock2':'0x18 extended-range; sends 0x80-byte chunks and polls WaitTimeBeforeStatusCheckForVerify',
 },
 'target_boundary':'this shared proprietary common-flash grammar explains the body/chassis/powertrain/security families that import it; it is distinct from the tracked Sienna/H UDS boot grammar and cannot become target-compatible by parameter choice alone once the route-specific decisive mismatch is applied',
}

FAMILY_EVIDENCE={
 'MMC':{'security_access':'27 41 -> 67 41 (8-byte seed), then 27 42 || 8-byte derived key -> 67 42','download':'34 || dataFormat || 44 || address[4] || size[4]; 74 20 response; max block capped at 0x0FFF','transfer':'36/counter/data -> 76/counter; 37 -> 77','routines':['0301','FF00','0304'],'reset':'11 81 (suppressed hard reset)','target_disposition':'rejected: SA 41/42 -> NRC 0x12; RIDs 0301/0304 -> NRC 0x31'},
 'P5PowerTrain':{'security_access':'bare 27 01 -> 4-byte seed; 27 02 || 4-byte derived key','session':'10 02 -> 50 02','target_disposition':'rejected: exact target request-seed length is 18 bytes'},
 'P4P5PowerTrain':{'security_access':'bare 27 01 -> 4-byte seed; 27 02 || 4-byte derived key; parameter-driven WaitTimeAfterSeedData/Key','target_disposition':'rejected: exact target request-seed length is 18 bytes'},
 'P5BodyMicon':{'security_access':'bare 27 01 -> 6-byte seed; 27 02 || 6-byte derived key','target_disposition':'rejected: exact target request-seed length is 18 bytes'},
 'P5Solar':{'security_access':'bare 27 01 -> 4-byte seed; 27 02 || 4-byte derived key','session':'10 02 -> 50 02','target_disposition':'rejected: exact target request-seed length is 18 bytes'},
 'SecurityChassisShrink':{'security_access':'27 01 || dynamic selector[1] || ECUAuthKey[16]; 27 02 || CalcSeedKeyForSecurityUp[16]','target_disposition':'rejected: request-seed application payload is 19 bytes, one byte longer than target exact policy'},
 'CentralGW+BodyFlash':{'prepare':'CentralGW prepare invokes host callback and waits WaitTimeAfterReprogrammingMode','flash':'P4 BodyFlash delegates to legacy CCanCommonFlashWriter; FinishReprogramming writes raw command byte 0x80 after CAN address prefix','target_disposition':'rejected: legacy raw common-flash protocol is not target UDS boot grammar'},
 'UnifiedEachArea':{'predownload':'2E 0203||OffsetAddress[5] -> 2E 0201||SeedKey[16] -> 2E 0202||Nonce[16], re-sent for every area group','download':'34 || dataFormatIdentifier || 46 || addressSpaceByte || (OffsetAddress[5]+areaStart) || areaLength; parses 74 and caps block at 0x0FFF before subtracting two header bytes','routines':['10F0','FF00','10F1','10F2'],'reset':'11 01 -> 51 01','target_disposition':'byte-compatible with tracked target boot grammar; exact calibration selection/values remain runtime/package-bounded'},
}

UNIFIED_REQUEST_DOWNLOAD_GRAMMAR='34 || dataFormatIdentifier || 46 || addressSpaceByte || (OffsetAddress[5] + areaStart) || areaLength'

UNIFIED_SURVIVOR_SEQUENCING={
 'TCUWCanUnifiedFlashWriter.dll':{
  'scope':'per node CPU image; verified from pinned unified_main_worker/unified_download_write_step/unified_routine_control bodies',
  'predownload':'2E 02 03||OffsetAddress[5] -> 2E 02 01||SeedKey[16] -> 2E 02 02||Nonce[16] sent once per CPU image before the area loop (fcn 0x100010f0 called at VA 0x1000268a)',
  'routines_per_image':'one 10F0 pair (tag 0, whole image) before the area loop, then per area: FF00 (tag 1) always, 10F1 (tag 2) pair, 10F2 (tag 3) pair',
  'address_source':'per-area CFileHeaderInfo area objects (std::string StartAddress/Length, stride 0x38) summed across the three area tables for progress; RequestDownload uses OffsetAddress[5]+areaStart and the raw Length field bytes',
  'last_cpu_image_tail':'GetWakeUpTimeAfterReset stored, StopSyncPeriodicMsg, 11 01 reset (fcn 0x10001a20, 180 ms), then raw J2534 tail frames (fcn 0x10001b10)',
 },
 'TCUWCanUnifiedFlashWriterEachArea.dll':{
  'scope':'per node CPU image and per area group; verified from pinned each_area_main_worker/each_area_download_write_step bodies',
  'predownload':'2E 02 03||OffsetAddress[5] -> 2E 02 01||SeedKey[16] -> 2E 02 02||Nonce[16] re-sent inside the per-area loop (fcn 0x100010f0 called at VA 0x10002616) before every area group',
  'routines_per_area':'conditional 10F0 (tag 0) pair when the first area table is non-empty, FF00 (tag 1) always, conditional 10F1 (tag 2) pair when the second area table is non-empty, 10F2 (tag 3) pair always',
  'address_source':'three per-image area tables (CFileHeaderInfo-shaped +0x48/+0x90/+0xB4); area objects stride 0x38 = {std::string StartAddress@+0x00, std::string Length@+0x1C}; RequestDownload address = big-endian 40-bit GetOffsetAddress[5] combined with GetUnsignedLong(area StartAddress), Length bytes copied verbatim',
  'last_cpu_image_tail':'GetWakeUpTimeAfterReset stored, StopSyncPeriodicMsg, 11 01 reset (fcn 0x100019c0, 180 ms), 50 ms-step wake countdown with per-step host callback, then two raw J2534 WriteMsgs tail frames: CAN ID 0x777 data 10 81 (len 6) and CAN ID 0x7F7 data FE 10 81 (len 7, TxFlag 0x80)',
 },
}

def unified_survivor_closure(root:Path,scans:dict[str,Any])->dict[str,Any]:
 bodies=[]
 for name,va,size,role,expected in UNIFIED_SURVIVOR_PINS:
  path=root/'Calibration Update Wizard'/name; data=path.read_bytes(); pe=pefile.PE(data=data); base=pe.OPTIONAL_HEADER.ImageBase
  body=pe.get_data(va-base,size); digest=hashlib.sha256(body).hexdigest()
  if digest!=expected: raise SystemExit(f'unified survivor pin mismatch: {name} {va:#x}/{size} expected {expected} got {digest}')
  bodies.append({'binary':name,'binary_sha256':hashlib.sha256(data).hexdigest(),'va':va,'size':size,'role':role,'sha256':digest})
 # negative import evidence computed from the same scans the artifact publishes
 writers=['TCUWCanUnifiedPrepareWriter.dll','TCUWCanUnifiedFlashWriter.dll','TCUWCanUnifiedFlashWriterEachArea.dll']
 neg={}
 for w in writers:
  imports=[i['dll']+'!'+i['name'] for i in scans[w]['imports']]
  neg[w]={'forbidden_hits':[t for t in UNIFIED_FORBIDDEN_IMPORTS if any(t in s for s in imports)],
          'calibration_getters_consumed':sorted(s.split('!')[1] for s in imports if '@CalibrationFile' in s or '@CFileHeaderInfo' in s)}
 # 17-record wrap-key selector table in TCUWUnifiedUtils.dll
 uudata=(root/'Calibration Update Wizard'/'TCUWUnifiedUtils.dll').read_bytes(); uu=pefile.PE(data=uudata); ubase=uu.OPTIONAL_HEADER.ImageBase
 records=[]
 for idx in range(17):
  rec=uu.get_data(0x100051b0+idx*0x208-ubase,0x208)
  key=rec[:0x100].split(b'\x00')[0].decode('ascii')
  records.append({'index':idx,'selector':struct.unpack_from('<I',rec,0x204)[0],'key_string':key})
 return {
  'surviving_routes':['TCUWCanUnifiedPrepareWriter.dll+TCUWCanUnifiedFlashWriter.dll','TCUWCanUnifiedPrepareWriter.dll+TCUWCanUnifiedFlashWriterEachArea.dll'],
  'pinned_bodies':bodies,
  'decisive_pin_reference':'EachArea predownload/request-download/reset/routine-control bodies remain pinned in decisive_function_identities (0x100010f0/0x10001420/0x100019c0/0x10001f80)',
  'security_property2':{
   'source':'CalibrationFile::GetSecurityProperty2(node) returns the calibration string; the writer builds CBytes(const char*) from it',
   'decode':'CBytes(const char*) performs ordinary two-hex-digits-per-byte decoding (the same parser proven for the auth fields), so the public value "98" decodes to a first byte 0x98',
   'rule':'dataFormatIdentifier = (first decoded byte >> 3) & 1, i.e. bit 3 of the decoded byte; encoded in each_area_download_write_step by shr dl,3 / and dl,1 at VA 0x10001d33/0x10001d3b',
   'example':{'public_string':'98','decoded_first_byte':'0x98','dataFormatIdentifier':1},
   'boundary':'the decoded byte is key material semantics, not a character code; do not reinterpret the ASCII character value',
  },
  'request_download':{
   'grammar':UNIFIED_REQUEST_DOWNLOAD_GRAMMAR,
   'applies_to':['TCUWCanUnifiedFlashWriter.dll (0x10001420, 944 B)','TCUWCanUnifiedFlashWriterEachArea.dll (0x10001420, 855 B)'],
   'details':[
    'request bytes: 0x34, then dataFormatIdentifier from SecurityProperty2 decoded-byte bit 3, then 0x46, then addressSpaceByte derived from the area/routine tag (tags 0/1/2 -> 1, tag 3 -> 0), then the 5-byte big-endian address, then the area Length field bytes',
    'address = big-endian 40-bit combination of GetOffsetAddress[5] with GetUnsignedLong(area StartAddress string)',
    'areaLength is transmitted as the raw Length field bytes, not a parsed integer',
    'positive response 0x74 carries a big-endian maxBlockLength; the writer caps it at 0x0FFF and then subtracts two header bytes before use',
   ],
   'supersedes':'field provenance here is authoritative: route_families[].reason and the mirrored cuw_writer_family_matrix.json / cuw_calibration_schema.json dispositions carry the same corrected byte order (regenerated from this classifier) but only as one-line summaries; per-byte semantics, SecurityProperty2 decoding, and sequencing live in this closure',
  },
  'make_send_data':{
   'pin':next(b for b in bodies if b['role']=='make_send_data'),
   'semantics':'CUnifiedUtils::MakeSendData walks typSFormatRecord records {kind:u8, pad, offset:u32, ptr:u32, len:u32} (stride 0x10) and memcpy-copies the prebuilt payload bytes into the 36-block buffer; it performs no host encryption, compression, or hash transform',
  },
  'host_verification':{'claim':'neither surviving Unified flash writer performs any host-side CRC/CMAC/DigitalSignature/hash verification of the image it transfers','evidence':'import census of both flash writers contains no CRC/CMAC/DigitalSignature/crypto facility; recorded under negative_import_evidence'},
  'negative_import_evidence':{'forbidden_substrings':list(UNIFIED_FORBIDDEN_IMPORTS),'per_binary':neg,
   'interpretation':'the surviving writers consume only GetNodeIdx/GetNumCPUImages/GetOffsetAddress/GetSeedKey/GetNonce/GetP4ServerMaxTime/GetSecurityProperty2/GetWakeUpTimeAfterReset/GetNumCPUImageDataAreaInfo plus prepare-side GetECUAuthKey/GetServiceAuthKey; GetReproMethod/GetDataFormat and every digest/signature getter are provably absent, so those fields cannot alter either surviving route'},
  'wrap_key_selector_table':{
   'binary':'TCUWUnifiedUtils.dll','table_va':'0x100051b0','stride':0x208,'selector_offset':0x204,'record_count':17,
   'resolver':'wrap_key_selector_resolver (0x10001000, 48 B) linearly scans the selector dword at record+0x204 and returns record+0x00',
   'records':records,
   'reachability':{'surviving_path':'selector 0 is hardcoded: CUnifiedUtils::CalcSeedKey pushes imm8 0 at VA 0x10002b6e before calling the resolver, and TCUWCanCommonPrepareWriter!CalcSeedKeyForSecurityUp likewise uses selector 0; record 0 equals that selector-0 key B45B26D6344FD60E80BC01D63C7584A0',
                  'records_1_16':'present in the shipped binary but not proven reachable by any pinned V18 caller; no non-zero selector feed is recovered'},
  },
  'image_area_sequencing':UNIFIED_SURVIVOR_SEQUENCING,
 }

def decisive_function_identities(root:Path)->list[dict[str,Any]]:
 out=[]
 for name,funcs in DECISIVE_FUNCTIONS.items():
  path=root/'Calibration Update Wizard'/name; data=path.read_bytes(); pe=pefile.PE(data=data); base=pe.OPTIONAL_HEADER.ImageBase
  for va,size,role in funcs:
   body=pe.get_data(va-base,size)
   out.append({'binary':name,'binary_sha256':hashlib.sha256(data).hexdigest(),'va':va,'size':size,'role':role,'sha256':hashlib.sha256(body).hexdigest()})
 return out

def common_flash_function_identities(root:Path)->list[dict[str,Any]]:
 name='TCUWCanCommonFlashWriter.dll'; path=root/'Calibration Update Wizard'/name
 data=path.read_bytes(); pe=pefile.PE(data=data); base=pe.OPTIONAL_HEADER.ImageBase
 return [
  {'binary':name,'binary_sha256':hashlib.sha256(data).hexdigest(),'va':va,'size':size,'role':role,'sha256':hashlib.sha256(pe.get_data(va-base,size)).hexdigest()}
  for va,size,role in COMMON_FLASH_FUNCTIONS
 ]


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
  if f=='TCUWCanUnifiedFlashWriter.dll': return 'byte-compatible','18-byte SA; exact 0203->0201->0202 WDBI; RIDs 10F0/FF00/10F1/10F2; 34 || dataFormatIdentifier || 46 || addressSpaceByte || address || length; 36/37; 11 01 all match target boot grammar; exact calibration selection/values remain bounded'
  if f=='TCUWCanUnifiedFlashWriterEachArea.dll': return 'byte-compatible','same 18-byte SA and 0203->0201->0202 predownload re-sent per area; per-area RequestDownload is recovered as 34 || dataFormatIdentifier || 46 || addressSpaceByte || (OffsetAddress[5]+areaStart) || areaLength, with the same 10F0/FF00/10F1/10F2 and 11 01 family'
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
 routes,_=factory_routes_from_ini_root(a.root.resolve()/'Calibration Update Wizard'/'Ini'); pairs=collections.Counter((r['prepare_writer'],r['flash_writer']) for r in routes)
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
 common_users=sorted(n for n,rec in scans.items() if any(imp.get('dll')=='TCUWCanCommonFlashWriter.dll' for imp in rec.get('imports',[])))
 obj={'schema_version':4,'distribution':'Toyota Techstream V18.00.003','writer_scans':scans,'route_families':fam,'verdict_counts':dict(sorted(counts.items())),'decisive_function_identities':decisive_function_identities(a.root.resolve()),'common_flash_function_identities':common_flash_function_identities(a.root.resolve()),'common_flash_grammar':COMMON_FLASH_GRAMMAR,'common_flash_users':common_users,'family_evidence':FAMILY_EVIDENCE,'unified_survivor_closure':unified_survivor_closure(a.root.resolve(),scans),
 'target_boot_grammar':{'request_seed':'27 01 || 16 tester bytes; exact request length 0x12','send_key':'27 02 || 16-byte key','wdbi_order':'0203(5)->0201(16)->0202(16)','routine_ids':['10F0','10F1','10F2','10F3','FF00'],'note':'Corolla-H boot/UDS target grammar is independently transferred target-natively in tracked variant tests'},
 'evidence_boundary':'all 196 decoded factory rows now have an exact static target disposition: two Unified-family rows are byte-compatible with the tracked boot grammar and 194 rows have at least one byte/decompilation-pinned mismatch. Exact factory-row selection and calibration values still require the matching package/live session.'}
 a.output.parent.mkdir(parents=True,exist_ok=True); a.output.write_text(json.dumps(obj,indent=2,sort_keys=True)+'\n'); return 0
if __name__=='__main__': raise SystemExit(main())
