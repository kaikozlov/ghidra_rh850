#!/usr/bin/env python3
from __future__ import annotations
import hashlib, json, subprocess, sys, tempfile
from pathlib import Path
import pefile

REPO=Path(__file__).resolve().parents[1]
ROOT=REPO/'Techstream/unpacked/toyota/Toyota Diagnostics/Calibration Update Wizard'
SCHEMA=REPO/'data/generated/techstream_v18/cuw_calibration_schema.json'
p=f=fails=0
oracle='raw_bytes'
def check(name,cond,detail=''):
 global p,f
 ok=bool(cond); p+=ok; f+=not ok
 print(f"[{'PASS' if ok else 'FAIL'}][{oracle}] {name}"+(f" ({detail})" if detail else ''))

if not ROOT.is_dir(): print('[SKIP] V18 unavailable'); raise SystemExit(77)
s=json.loads(SCHEMA.read_text())
print('== byte-pinned parser identities ==')
for row in s['function_identities']:
 pe=pefile.PE(str(ROOT/row['artifact'])); body=pe.get_data(row['va']-pe.OPTIONAL_HEADER.ImageBase,row['size'])
 digest=hashlib.sha256(body).hexdigest()
 check(f"{row['artifact']}:{row['role']} identity",digest==row['expected_sha256']==row['sha256'])

print('\n== target/object geometry ==')
area=s['objects']['CLogicalBlockAreaInfo']
check('area object is exactly five 0x1c string objects',area['size']==0x8c and [x['object_offset'] for x in area['fields']]==[0,0x1c,0x38,0x54,0x70])
check('integrity field names/order exact',[x['name'] for x in area['fields']]==['StartAddress','Length','CRC','CMAC','DigitalSignature'])
check('source target record is five pointers / 0x14',s['target_integrity']['record_size']==0x14 and [x['source_offset'] for x in s['target_integrity']['fields']]==[0,4,8,12,16])
lb=s['objects']['CLogicalBlockInfo']
check('logical block size/area offsets exact',lb['size']==0x39c and [x['logical_block_object_offset'] for x in lb['area_records']]==[0x8,0x94,0x120,0x1ac,0x238,0x2c4])
check('six parser calls exact',[x['call_va'] for x in s['target_integrity']['families']]==[0x40bfea,0x40c03e,0x40c092,0x40c0e6,0x40c13a,0x40c18e])
check('attach.att and critical key vocabulary captured',s['descriptor']['embedded_name']=='attach.att' and {'ECUAuthKey','ServiceAuthKey','SeedKey','Nonce','OffsetAddress','SecurityProperty2','DigitalSignature'} <= set(s['descriptor']['key_vocabulary']))
consumer=s['target_integrity']['standard_writer_consumer']
check('standard writer consumes exact five object offsets',consumer['field_offsets']=={'StartAddress':0,'Length':0x1c,'CRC':0x38,'CMAC':0x54,'DigitalSignature':0x70})
check('standard writer wire routine IDs are 10F5/FF00/10F6',consumer['routine_ids']=={'0':'10F5','1':'FF00','2':'10F6'})
check('standard writer carries all six target families',set(sum(consumer['target_family_callers'].values(),[]))=={'ReproData','EraseAndReproRoutine','DeltaReproData','DeltaEraseAndReproRoutine','CompressionReproData','CompressionEraseAndReproRoutine'})
check('unified routes are explicitly kept separate','CFileHeaderInfo' in s['target_integrity']['unified_writer_boundary'] and 'do not consume' in s['target_integrity']['unified_writer_boundary'])
route_rel=s['target_integrity']['route_relevance']
check('all 32 route pairs have integrity relevance',len(route_rel)==32 and sum(x['factory_rows'] for x in route_rel)==196)
check('integrity relevance matches 194 rejected / 2 compatible',sum(x['factory_rows'] for x in route_rel if x['target_verdict']=='rejected')==194 and sum(x['factory_rows'] for x in route_rel if x['target_verdict']=='byte-compatible')==2)
standard_rel=next(x for x in route_rel if x['integrity_path']=='standard-CLogicalBlockAreaInfo')
check('signature-bearing standard integrity path is target-rejected',standard_rel['target_verdict']=='rejected' and standard_rel['factory_rows']==2 and 'DigitalSignature' in standard_rel['field_flow'])
unified_rel=[x for x in route_rel if x['integrity_path']=='unified-CFileHeaderInfo-area']
check('both compatible routes use unified area path',len(unified_rel)==2 and all(x['target_verdict']=='byte-compatible' for x in unified_rel))
check('compatible routes do not promote standard signature fields',all('not consumed through the standard' in x['field_flow']['DigitalSignature'] for x in unified_rel))

print('\n== extracted attach.att parser fixture ==')
fixture='''[Vehicle]\nVersion=102\nECUAuthKey=00112233445566778899AABBCCDDEEFF\nServiceAuthKey=FFEEDDCCBBAA99887766554433221100\n\n[LogicalBlock101]\nReproMethod=Whole\nNumberOfTargets=1\n\n[01_TargetCalibration]\nStartAddress=00000000\nLength=00100000\nCRC=12345678\nCMAC=00112233445566778899AABBCCDDEEFF\nDigitalSignature=ABCDEF\nUnknownFutureField=preserve-me\n'''
with tempfile.TemporaryDirectory() as td:
 inp=Path(td)/'attach.att'; out=Path(td)/'out.json'; inp.write_bytes(fixture.encode('latin1'))
 r=subprocess.run([sys.executable,str(REPO/'tools/techstream/parse_cuw_attach.py'),str(inp),'--output',str(out)],check=False)
 obj=json.loads(out.read_text()) if out.exists() else {}
 check('attach parser exits successfully',r.returncode==0)
 sections={x['name']:{y['name']:y['value'] for y in x['fields']} for x in obj.get('sections',[])}
 check('unknown fields are losslessly retained',sections.get('01_TargetCalibration',{}).get('UnknownFutureField')=='preserve-me')
 check('case/value preservation',sections.get('Vehicle',{}).get('ECUAuthKey')=='00112233445566778899AABBCCDDEEFF')

print('\n== deterministic regeneration ==')
with tempfile.TemporaryDirectory() as td:
 out=Path(td)/'schema.json'; r=subprocess.run([sys.executable,str(REPO/'tools/techstream/generate_cuw_calibration_schema.py'),'--root',str(ROOT),'--output',str(out)],check=False)
 check('schema generator exits successfully',r.returncode==0)
 check('schema regeneration byte-identical',out.read_bytes()==SCHEMA.read_bytes())
print(f'\nResults: {p} passed, {f} failed'); raise SystemExit(1 if f else 0)
