#!/usr/bin/env python3
from __future__ import annotations

import csv
import io
import json
import struct
import sys
import zlib
from pathlib import Path

import pefile

REPO = Path(__file__).resolve().parents[1]
ROOT = REPO / 'Techstream/unpacked/toyota/Toyota Diagnostics/Calibration Update Wizard'
EVIDENCE = REPO / 'data/generated/techstream_v18/cuw_t0087_17_specimen.json'
sys.path.insert(0, str(REPO / 'tools/techstream'))
from generate_cuw_writer_inventory import decode_parameter_ini
from inspect_cuw_legacy import legacy_seed_key, summarize_srec
from parse_cuw_container import MAGIC, parse

p = f = 0
oracle = 'raw_bytes+independent_external_artifact'

def check(name, cond, detail=''):
    global p, f
    ok = bool(cond); p += ok; f += not ok
    print(f"[{'PASS' if ok else 'FAIL'}][{oracle}] {name}" + (f" ({detail})" if detail else ''))

if not ROOT.is_dir():
    print('[SKIP] V18 unavailable')
    raise SystemExit(77)

ev = json.loads(EVIDENCE.read_text())

print('== T-0087-17 immutable specimen summary ==')
check('external specimen identity pinned', ev['source'] == {
    'filename': 'T-0087-17.cuw',
    'availability': 'external user-supplied specimen; raw package intentionally not committed',
    'size': 5112447,
    'sha256': 'd40cc0988f7310ce0417fba17e512ae915719b40fed9a98f829ca1c5639c3cbd',
})
check('real package validates both recorded CRC layers', ev['outer_container']['stored_crc32'] == ev['outer_container']['computed_crc32'] == 'D9AD63D2' and ev['outer_container']['first_member']['payload_crc32'] == '057704E2')
check('real package is Format Version 4', ev['outer_container']['format_type'] == 4 and ev['descriptor']['Format']['Version'] == '4')
check('descriptor identifies 2015-16 Corolla engine package', ev['descriptor']['Vehicle']['VehicleName'] == 'Corolla' and ev['descriptor']['Vehicle']['ModelYear'] == '15-16' and ev['descriptor']['Vehicle']['EngineType'] == '2ZR-FAE' and ev['descriptor']['CPU01']['CPUImageName'] == '89663-02U13.xx')
check('calibration transition exact', [ev['descriptor']['CPU01'][f'{i:02d}_TargetCalibration'] for i in range(1,4)] == ['302U1000','302U1100','302U1200'] and ev['descriptor']['CPU01']['NewCID'] == '302U1300')
arch = ev['format4_archive']
check('format4 archive consumes tail exactly', arch['count'] == 1 and 1 + 2 + arch['name_length'] + 8 + arch['payload_length'] == ev['outer_container']['tail_length'] and arch['record_consumes_tail_exactly'])
check('archive payload CRC validates', arch['payload_crc32'] == arch['computed_payload_crc32'] == '5CACED62')
sr = ev['srecord']
check('S-record shape exact', sr['record_counts'] == {'S0':1,'S2':65536,'S8':1} and sr['data_length'] == 0x200000 and sr['data_record_bytes'] == 32 and sr['entry_address'] == '0x014B00')
check('reconstructed image identity pinned', sr['reconstructed_image_sha256'] == '2b2db1d9766405d74706e56fc1baea544e2a00bbaf09ee36f5994f1617852735')
check('security trailer binds password/name/location', sr['security_trailer']['bytes_at_1fff00_1fff20'] == '79ef38ff2d75eb3138393636332d303255313320202020200002000100030720' and sr['security_trailer']['cpu_image_name_ascii_at_1fff08'].rstrip() == '89663-02U13' and sr['security_trailer']['location_id_bytes_at_1fff18'] == ev['descriptor']['CPU01']['LocationID'])

print('\n== independent Format-Version-4 parser fixture ==')
def member(name: bytes, payload: bytes) -> bytes:
    return struct.pack('>H', len(name)) + name + struct.pack('>II', len(payload), zlib.crc32(payload) & 0xffffffff) + payload
attach = b'[Format]\nVersion=4\n\n[Vehicle]\nNumberOfCalibration=1\n'
archive_payload = b'S0030000FC\r\n'
tail = bytes([1]) + member(b'302U1300.txt', archive_payload)
total = 22 + len(member(b'attach.att', attach)) + len(tail)
raw = bytearray(MAGIC + bytes([4]) + b'\0\0\0\0' + struct.pack('>I', total) + member(b'attach.att', attach) + tail)
raw[14:18] = struct.pack('>I', zlib.crc32(raw[18:]) & 0xffffffff)
obj = parse(bytes(raw))
check('format4 synthetic package accepted', not obj['errors'])
check('format4 count/member recovered', obj['format4_archive_count'] == 1 and obj['format4_archives'][0]['name'] == '302U1300.txt' and obj['format4_archives'][0]['payload_length'] == len(archive_payload))
check('format4 parser consumes declared end', obj['format4_archive_bytes_consumed'] == len(tail) and obj['format4_archives'][0]['record_end'] == total)
bad = bytearray(raw)
# Corrupt archive payload, then repair the outer CRC so the inner member CRC is the sole failure.
bad[-3] ^= 1
bad[14:18] = struct.pack('>I', zlib.crc32(bad[18:]) & 0xffffffff)
badobj = parse(bytes(bad))
check('format4 archive CRC enforced independently', any('format-4 archive[0] payload CRC mismatch' in x for x in badobj['errors']))

print('\n== S-record parser fixture ==')
def srec(kind: str, addr: int, payload: bytes=b'') -> bytes:
    alen = {'0':2,'2':3,'8':3}[kind]
    body = addr.to_bytes(alen,'big') + payload
    count = len(body) + 1
    csum = (~(count + sum(body))) & 0xff
    return f'S{kind}{count:02X}'.encode() + (body + bytes([csum])).hex().upper().encode()
sbuf = b'\r\n'.join([srec('0',0,b'TEST'), srec('2',0x100,b'\x01\x02\x03\x04'), srec('8',0x123456)]) + b'\r\n'
ss, mem = summarize_srec(sbuf)
check('S-record fixture checksum/type/address parser exact', ss['record_counts'] == {'0':1,'2':1,'8':1} and ss['entry_address'] == 0x123456 and bytes(mem[x] for x in range(0x100,0x104)) == b'\x01\x02\x03\x04')

print('\n== V18 selector join ==')
cal = pefile.PE(str(ROOT/'TCUWCalibrationFile.dll')); base = cal.OPTIONAL_HEADER.ImageBase; rawcal = (ROOT/'TCUWCalibrationFile.dll').read_bytes()
def export_pointed_value(marker: str):
    vals = {}
    for sym in cal.DIRECTORY_ENTRY_EXPORT.symbols:
        name = (sym.name or b'').decode('latin1')
        if marker not in name: continue
        off = cal.get_offset_from_rva(sym.address); ptr = struct.unpack_from('<I',rawcal,off)[0]
        po = cal.get_offset_from_rva(ptr-base); end = rawcal.index(0,po)
        vals[rawcal[po:end].decode('latin1')] = name
    return vals
cpuvals = export_pointed_value('glptrCPUType_'); kindvals = export_pointed_value('glptrKindOfECU_')
check('CPUType 70 is SH72544R 2560K', cpuvals.get('70') == '?glptrCPUType_SH72544R_2560K@@3PBDB')
check('KindOfECU 0 is ENG&ECT', kindvals.get('0') == '?glptrKindOfECU_ENGAndECT@@3PBDB')
rows = list(csv.reader(io.StringIO(decode_parameter_ini((ROOT/'Ini/Parameter.ini').read_bytes()).decode('latin1'))))
hdr = rows[0]; matches=[]
for row in rows[1:]:
    row += ['']*(len(hdr)-len(row)); d=dict(zip(hdr,row))
    if d.get('ParamFileKeySystemProtocolMicon') == '0CAN70': matches.append(d)
check('exactly one 0CAN70 system row', len(matches) == 1)
r = matches[0]
check('0CAN70 selects package password address and legacy route', r.get('PasswordAddress') == '001FFF00' and r.get('ByteOrder') == '1' and r.get('FlagToUseCIDGetterAndFlashWriterDLL') == '0' and r.get('FORESTTypeFlag') == '0')
check('specimen route summary matches decoded row', ev['techstream_v18_route']['selection_key'] == '0CAN70' and all(r.get(k) == v for k,v in ev['techstream_v18_route']['parameter_row'].items()))

print('\n== legacy CCanFlashWriter SecurityAccess ==')
cuw = pefile.PE(str(ROOT/'Cuw.exe')); cbase=cuw.OPTIONAL_HEADER.ImageBase
def at(va,n): return cuw.get_data(va-cbase,n)
check('round A441 initializer bytes exact', at(0x47F0C4,10) == bytes.fromhex('6841a4000068e86e5f00'))
check('round 2172 initializer bytes exact', at(0x47F0D9,10) == bytes.fromhex('687221000068f46f5f00'))
check('round A421 initializer bytes exact', at(0x47F0EE,10) == bytes.fromhex('6821a400006800715f00'))
check('round 4172 initializer bytes exact', at(0x47F103,10) == bytes.fromhex('6872410000680c725f00'))
for seedhex in ('00000000','12345678','ffffffff','a5a55a5a'):
    seed=bytes.fromhex(seedhex)
    check(f'legacy SA algebra {seedhex}', legacy_seed_key(seed) == bytes(x^y for x,y in zip(seed,bytes.fromhex('00606000'))))
check('specimen records same exact SA simplification', ev['legacy_security']['security_access']['simplified'] == 'key = seed XOR 00 60 60 00')

print('\n== archived password extraction contract ==')
exports={(s.name or b'').decode('latin1'): cal.OPTIONAL_HEADER.ImageBase+s.address for s in cal.DIRECTORY_ENTRY_EXPORT.symbols}
check('GetPassword export VA exact', exports.get('?GetPassword@CalibArchivedFile@@QAEHAAVCParameter@@@Z') == 0x10002EF0)
check('GetNewPassword export VA exact', exports.get('?GetNewPassword@CalibrationFile@@QAEHHAAVCParameter@@@Z') == 0x10003090)
check('specimen password equals image bytes at selected address', ev['legacy_security']['calibration_password']['value'] == sr['security_trailer']['password_bytes'] == '79EF38FF' and ev['legacy_security']['calibration_password']['source_address'] == '0x1FFF00')
check('modern credential fields absent from real legacy descriptor', set(ev['modern_transfer_boundary']['descriptor_fields_absent']) == {'ECUAuthKey','ServiceAuthKey','SeedKey','Nonce','OffsetAddress','SecurityProperty2'} and not any(x in ev['descriptor']['CPU01'] or x in ev['descriptor']['Vehicle'] for x in ev['modern_transfer_boundary']['descriptor_fields_absent']))

print(f'\nResults: {p} passed, {f} failed')
raise SystemExit(1 if f else 0)
