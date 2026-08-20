#!/usr/bin/env python3
"""Generate CUW writer byte-template grammar and Sienna/H boot compatibility.

The byte scanner is intentionally conservative: it records immediate stores to
request/response buffers as raw x86 little-endian bytes. Semantic route verdicts
are promoted only for writer families whose decisive mismatch/match is separately
pinned by deterministic tests or existing firmware-static findings.
"""
from __future__ import annotations
import argparse, collections, hashlib, json, struct
from pathlib import Path
from typing import Any
import pefile
import sys

REPO=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(REPO))
from tools.techstream.generate_cuw_writer_inventory import factory_routes

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
 'TCUWP4CanSecurityChassisShrinkPrepareWriter.dll':('bounded-rejected','security-up short request class; no target-compatible 16-byte seed-request append recovered'),
 'TCUWP4CanPowerTrainPrepareWriter.dll':('rejected','short/common SecurityAccess class; flash pairings are independently incompatible'),
 'TCUWP5CanPowerTrainPrepareWriter.dll':('bounded-rejected','common prepare SecurityAccess builder unresolved at exact request shape; no positive 18-byte evidence'),
 'TCUWP4P5CanPowerTrainPrepareWriter.dll':('bounded-rejected','common prepare SecurityAccess class; no positive 18-byte evidence'),
 'TCUWP4CanCentralGWPrepareWriter.dll':('bounded-rejected','central-gateway prepare/routine family, no target boot grammar match'),
 'TCUWP5CanPowerTrainPrepareWriterForBodyMicon.dll':('bounded-rejected','common prepare SecurityAccess class; no positive 18-byte evidence'),
 'TCUWP5CanPowerTrainPrepareWriterForSolar.dll':('bounded-rejected','common prepare SecurityAccess class; no positive 18-byte evidence'),
 'TCUWCanSBRPrepareWriter.dll':('rejected','SecurityAccess 33/34 and vendor-session grammar unsupported by target'),
 'TCUWCanHINOPrepareWriter.dll':('rejected','SecurityAccess 03/04 HINO family unsupported by target'),
 'TCUWCanHINOPrepareWriterForVCS.dll':('rejected','SecurityAccess 03/04 HINO family unsupported by target'),
 'TCUWCanHINOPrepareWriterForDSS.dll':('rejected','SecurityAccess 03/04 HINO family unsupported by target'),
 'TCUWCanPSAPrepareWriter.dll':('rejected','legacy PSA authentication/SID family unsupported by target'),
 'TCUWP5CanSecurityPowerTrainPrepareWriter.dll':('candidate','18-byte 27 01 || ECUAuthKey shape matches, but paired flash/routine grammar decides route'),
 'TCUWCanMMCPrepareWriter.dll':('unresolved','legacy MMC grammar not sufficiently recovered for exact target disposition'),
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

def route_verdict(p:str,f:str)->tuple[str,str]:
 pc,why=PREP_CLASS.get(p,('unresolved','no exact decisive target grammar recovered'))
 if p=='TCUWCanUnifiedPrepareWriter.dll':
  if f=='TCUWCanUnifiedFlashWriter.dll': return 'byte-compatible','18-byte SA; exact 0203->0201->0202 WDBI; RIDs 10F0/FF00/10F1/10F2; 34 format 46; 36/37; 11 01 all match target boot grammar; exact calibration selection/values remain bounded'
  if f=='TCUWCanUnifiedFlashWriterEachArea.dll': return 'compatible-bounded','same target-compatible prepare/predownload/RID family; exact per-area RequestDownload layout remains bounded'
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
 names=sorted({x for pair in pairs for x in pair if x}|SUPPORT)
 scans={n:scan(a.root/'Calibration Update Wizard'/n) for n in names if (a.root/'Calibration Update Wizard'/n).is_file()}
 fam=[]; counts=collections.Counter()
 for (p,f),n in pairs.most_common():
  verdict,reason=route_verdict(p,f); counts[verdict]+=n; fam.append({'prepare_writer':p,'flash_writer':f,'factory_rows':n,'verdict_sienna_8965B4512000':verdict,'verdict_corolla_8965H1202000':verdict,'reason':reason})
 obj={'schema_version':1,'distribution':'Toyota Techstream V18.00.003','writer_scans':scans,'route_families':fam,'verdict_counts':dict(sorted(counts.items())),
 'target_boot_grammar':{'request_seed':'27 01 || 16 tester bytes; exact request length 0x12','send_key':'27 02 || 16-byte key','wdbi_order':'0203(5)->0201(16)->0202(16)','routine_ids':['10F0','10F1','10F2','10F3','FF00'],'note':'Corolla-H boot/UDS target grammar is independently transferred target-natively in tracked variant tests'},
 'evidence_boundary':'raw template scans preserve encoded x86 store bytes; semantic route verdicts use only decisive byte/decompilation-pinned writer/firmware facts. unresolved/bounded classes are not absence claims.'}
 a.output.parent.mkdir(parents=True,exist_ok=True); a.output.write_text(json.dumps(obj,indent=2,sort_keys=True)+'\n'); return 0
if __name__=='__main__': raise SystemExit(main())
