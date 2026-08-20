#!/usr/bin/env python3
from __future__ import annotations
import hashlib, json, struct, subprocess, sys, tempfile, zlib
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

print('\n== outer container framing: statically recovered constants ==')
oc=s['outer_container']
cpe=pefile.PE(str(ROOT/'Cuw.exe')); cbase=cpe.OPTIONAL_HEADER.ImageBase
check('schema magic equals Cuw.exe constant @0x5d453c',bytes.fromhex(oc['magic']['bytes_hex'])==cpe.get_data(0x5D453C-cbase,13)==bytes.fromhex('0043414c4942524154494f4e00') and oc['magic']['length']==13)
check('schema type table equals Cuw.exe table @0x5d5284 (count 11 @0x5d5290)',oc['format_type']['values']==list(cpe.get_data(0x5D5284-cbase,11))==[1,3,4,5,6,7,8,9,0x65,0x66,0x67] and oc['format_type']['table_count']==struct.unpack('<I',cpe.get_data(0x5D5290-cbase,4))[0]==11)
kal=pefile.PE(str(ROOT/'TCUWCalibrationFile.dll')); kb=kal.OPTIONAL_HEADER.ImageBase
check('known format versions equal gbytFORMAT_VERSIONS @0x100063a4',oc['format_type']['known_format_versions']==list(kal.get_data(0x100063A4-kb,3))==[1,3,4])
check('membership-only values not overclaimed',oc['format_type']['membership_only_values']==[5,6,7,8,9,0x65,0x66,0x67] and 'NOT claimed' in oc['format_type']['boundary'])
check('boundary status reflects recovered-framing + specimen-pending',s['outer_container_boundary']['status']=='framing-statically-recovered; specimen-validation-pending' and 'no real .cuw' in s['outer_container_boundary']['remaining'])
check('outer CRC region begins at total-size field',oc['outer_crc_check']['region']=='[18, declared_total)' and oc['outer_crc_check']['compare_va']==0x41405b)
check('tail is explicitly opaque', 'never interpreted' in oc['tail_policy'])

print('\n== outer container parser: synthetic fixture from recovered grammar ==')
# Fixture is assembled here independently of the parser module, straight from
# the documented grammar, so a parser bug cannot mask a grammar mismatch.
INI=(b'[Vehicle]\nVersion=102\nContactType=P5-Unified\nECUAuthKey=00112233445566778899AABBCCDDEEFF\n\n[01_TargetCalibration]\nStartAddress=00000000\nLength=00100000\n')
TAIL=bytes(range(64))+b'CPU-IMAGE-TAIL-OPAQUE'
def build(fmt=3,name=b'attach.att',payload=INI,tail=TAIL):
    total=22+2+len(name)+8+len(payload)+len(tail)
    b=bytearray(b'\x00CALIBRATION\x00'+bytes([fmt])+struct.pack('>I',0)+struct.pack('>I',total))
    b+=struct.pack('>H',len(name))+name+struct.pack('>I',len(payload))+struct.pack('>I',zlib.crc32(payload)&0xffffffff)+payload+tail
    b[14:18]=struct.pack('>I',zlib.crc32(bytes(b[18:total]))&0xffffffff)
    return bytes(b)
GOOD=build()
with tempfile.TemporaryDirectory() as td:
    td=Path(td); cuw=td/'synthetic.cuw'; out=td/'r.json'; pay=td/'attach.att'
    cuw.write_bytes(GOOD)
    r=subprocess.run([sys.executable,str(REPO/'tools/techstream/parse_cuw_container.py'),str(cuw),'--output',str(out),'--payload-out',str(pay)],check=False,capture_output=True,text=True)
    obj=json.loads(out.read_text()) if out.exists() else {}
    check('container parser exits successfully',r.returncode==0 and obj.get('ok') is True)
    check('magic/type/name extracted',obj.get('format_type')==3 and obj.get('name')=='attach.att' and obj.get('name_length')==10)
    check('payload round-trips byte-exact',pay.exists() and pay.read_bytes()==INI and obj.get('payload_length')==len(INI))
    check('outer CRC verified over [18,declared)',obj.get('computed_outer_crc32')==obj.get('stored_crc32') and obj.get('outer_crc_region')==[18,len(GOOD)] and obj.get('declared_total_size')==len(GOOD))
    check('opaque tail preserved verbatim',obj.get('tail_length')==len(TAIL) and hashlib.sha256(TAIL).hexdigest()==obj.get('tail_sha256'))
    def run_bad(label,data,needle):
        f=td/label; f.write_bytes(data); o=td/(label+'.json')
        rr=subprocess.run([sys.executable,str(REPO/'tools/techstream/parse_cuw_container.py'),str(f),'--output',str(o)],check=False,capture_output=True,text=True)
        jj=json.loads(o.read_text()) if o.exists() else {}
        check(label,rr.returncode==1 and any(needle in e for e in jj.get('errors',[])),(jj.get('errors') or ['?'])[0][:90])
    bad=bytearray(GOOD); bad[1]=0x58; run_bad('bad magic rejected',bytes(bad),'bad magic')
    run_bad('unknown format type rejected',build(fmt=0x02),'not in statically recovered membership table')
    badpay=bytearray(GOOD); badpay[22+2+10+4]^=0x01; run_bad('bad payload crc rejected',bytes(badpay),'payload CRC mismatch')
    corrupted=bytearray(GOOD); corrupted[len(GOOD)-5]^=0xff; run_bad('tail corruption caught by outer crc',bytes(corrupted),'outer CRC mismatch')
    flipcrc=bytearray(GOOD); flipcrc[14]^=0x01; run_bad('bad stored outer crc rejected',bytes(flipcrc),'outer CRC mismatch')
    over=bytearray(build(tail=b'')); struct.pack_into('>I',over,18,len(over)+10); run_bad('declared size beyond file rejected',bytes(over),'exceeds file size')
    short=bytearray(GOOD); struct.pack_into('>H',short,22,0x7ff); run_bad('truncated name rejected',bytes(short),'truncated inside first member name')
    # build_synthetic helper agrees with the independent fixture builder
    sys.path.insert(0,str(REPO/'tools/techstream'))
    import parse_cuw_container as pcc
    check('module build_synthetic matches independent grammar',pcc.build_synthetic(INI,tail=TAIL)==GOOD)
    check('module parse agrees on good fixture',not pcc.parse(GOOD)['errors'])

print('\n== deterministic regeneration ==')
with tempfile.TemporaryDirectory() as td:
 out=Path(td)/'schema.json'; r=subprocess.run([sys.executable,str(REPO/'tools/techstream/generate_cuw_calibration_schema.py'),'--root',str(ROOT),'--output',str(out)],check=False)
 check('schema generator exits successfully',r.returncode==0)
 check('schema regeneration byte-identical',out.read_bytes()==SCHEMA.read_bytes())
print(f'\nResults: {p} passed, {f} failed'); raise SystemExit(1 if f else 0)
