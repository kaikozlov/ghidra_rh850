#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
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
from inspect_cuw_legacy import (
    decode_legacy_target_data, legacy_check_id_payloads, legacy_seed_key,
    summarize_repeated_word, summarize_srec,
)
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
repeat = sr['repeated_word_summary']
check('encoded-looking fill word census pinned', repeat['word_hex'] == 'A1DFE103' and repeat['aligned_word_count'] == 70726)
check('two full A1DFE103 64K regions pinned', repeat['full_64k_regions'] == [
    {'start':'0x050000','end_exclusive':'0x060000','length':65536},
    {'start':'0x1E0000','end_exclusive':'0x1F0000','length':65536},
])
check('repeated-word helper reproduces synthetic whole-region detection', summarize_repeated_word(bytes.fromhex('a1dfe103') * 0x4000)['full_regions'] == [{'start':0,'end_exclusive':0x10000,'length':0x10000}])
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
def calib_at(va,n): return cal.get_data(va-base,n)
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
fallback = ev['legacy_security']['calibration_password']['fallback_selector_evidence']
check('GetNewPassword fallback body pinned', fallback['get_new_password']['va'] == '0x10003090' and fallback['get_new_password']['size'] == '0x3C' and hashlib.sha256(calib_at(0x10003090,0x3C)).hexdigest() == fallback['get_new_password']['sha256'] == 'efe7a275c16909454cfe40418c22da35e5cf7a2ba5d2cb134ed7c6cae08c46fc' and calib_at(0x100030A2,8) == bytes.fromhex('807a44005e74078b'))
check('CalibArchivedFile GetPassword body pinned', fallback['get_password']['va'] == '0x10002EF0' and fallback['get_password']['size'] == '0x15F' and hashlib.sha256(calib_at(0x10002EF0,0x15F)).hexdigest() == fallback['get_password']['sha256'] == '13cd12218291ebbe2d147d2ea9c2cdecd020bf73d4c9f1505c6cdbbeae799164')
check('specimen password equals image bytes at selected address', ev['legacy_security']['calibration_password']['value'] == sr['security_trailer']['password_bytes'] == '79EF38FF' and ev['legacy_security']['calibration_password']['source_address'] == '0x1FFF00')
cpw = ev['legacy_security']['calibration_password']
check('NewPassword parser source slots are pinned', cpw['new_password_override_parser']['parser_site_va'] == '0x00408CE8' and cpw['new_password_override_parser']['source_record_value_offset'] == '0x1C' and cpw['new_password_override_parser']['source_record_present_offset'] == '0x20' and at(0x408CE0, 0x20) == bytes.fromhex('ffff0f8df2fdffff8b0da4045d00898d18edffff8b0da8045d00898d1cedffff'))
check('SelectRetryPassword body is pinned with old/new/toggle semantics', cpw['retry_selector']['va'] == '0x0046CAB0' and hashlib.sha256(at(0x46CAB0, 0x6C)).hexdigest() == cpw['retry_selector']['sha256_0x6c'] == 'c653fcca83bc5b43d5b710bcc93d8240950ea4980a941f1c7ebe87910bf7e48a' and 'explicit true selects new (1)' in cpw['retry_selector']['semantics'] and 'object+0x78 == 7 toggles' in cpw['retry_selector']['semantics'])
selector_consumer = cpw['retry_selector']['consumer_branch']
check('Execute maps selector zero to old and nonzero to new source', selector_consumer['selector_test_va'] == '0x0045F4BC' and at(0x45F4BC,12) == bytes.fromhex('8b808c0000008038000f8426') and selector_consumer['zero_old_path_va'] == '0x0045F7F1' and at(0x45F7F1,10) == bytes.fromhex('698df8fbffff1a030000') and selector_consumer['nonzero_new_path_helper_call_va'] == '0x0045F7CF' and at(0x45F7CF,5) == bytes.fromhex('e80440fbff'))

print('\n== legacy TargetData/check-ID software-password path ==')
targets = ev['legacy_security']['target_data_passwords']
decoder = targets['decoder']
check('TargetData decoder body pinned', decoder['escaped_string_decoder_va'] == '0x004B3880' and decoder['escaped_string_decoder_size'] == '0x170' and hashlib.sha256(at(0x4B3880, 0x170)).hexdigest() == decoder['escaped_string_decoder_sha256'] == 'a62f3f89276881a88b6cff421772fd4ee43e2fa273a8c39f9ca0bc4737cf20fa')
check('TargetData uint-reader body pinned', decoder['uint_reader_va'] == '0x004B3F34' and decoder['uint_reader_size'] == '0x122' and hashlib.sha256(at(0x4B3F34, 0x122)).hexdigest() == decoder['uint_reader_sha256'] == '5c21c78aea493daf5d2c817aeef7bb5f615c63381c7e8c246eebd681f88bb042')
expected_targets = [
    ('302U1000','41364547383B483A','A5CD46B3','B346CDA5'),
    ('302U1100','41443A46384B364B','AC8C4F0D','0D4F8CAC'),
    ('302U1200','37333947373C373A','727D3713','13377D72'),
]
location = bytes.fromhex(ev['descriptor']['CPU01']['LocationID'])
for record, expected in zip(targets['targets'], expected_targets):
    calibration, target_data, password_hex, wire_hex = expected
    password = decode_legacy_target_data(target_data)
    frames = legacy_check_id_payloads(location, password)
    check(f'{calibration} TargetData decodes exactly', record['calibration'] == calibration and record['target_data'] == target_data and password == int(password_hex,16) and record['password'] == password_hex)
    check(f'{calibration} old-password wire bytes exact', frames == [b'\x00',b'\x00',bytes.fromhex('200701000200'),bytes.fromhex('0300'),bytes.fromhex(wire_hex)] and record['wire_password'] == wire_hex)
try:
    decode_legacy_target_data('0000000000000000')
except ValueError:
    malformed_rejected = True
else:
    malformed_rejected = False
check('TargetData decoder rejects non-ASCII-hex decode', malformed_rejected)

consumer = cpw['wire_consumer']
check('CheckIDWithWaitOfSFs body pinned', consumer['va'] == '0x0045C86C' and consumer['size'] == '0x570' and hashlib.sha256(at(0x45C86C, 0x570)).hexdigest() == consumer['sha256'] == '302c53c53cd78441ce2c989def17ba5f1f910053f3d1d59c61c9ba772d653c9e')
check('CheckID frame-3 LocationID permutation instruction anchors', [at(a,6) for a in (0x45CA89,0x45CA95,0x45CAA1,0x45CAAD,0x45CAB9,0x45CAC5)] == [bytes.fromhex(x) for x in ('8a95fbfeffff','8a8dfafeffff','8a85f7feffff','8a95f6feffff','8a8df5feffff','8a85f4feffff')])
check('CheckID frame-4 LocationID permutation instruction anchors', at(0x45CB19,6) == bytes.fromhex('8a95f9feffff') and at(0x45CB25,6) == bytes.fromhex('8a8df8feffff'))
check('CheckID password byte-reversal loop pinned', at(0x45CB82,0x1F) == bytes.fromhex('33c08d9580ecffffb9030000002bc88a8c0de8fdffff880a404283f8047ce9'))
check('CheckID sends exactly five constructed frames', at(0x45CBB4,7) == bytes.fromhex('be0500000033db'))
new_frames = legacy_check_id_payloads(location, int(cpw['value'],16))
check('new-image password role and exact wire encoding closed', cpw['role'].startswith('new-image software password') and cpw['wire_password'] == 'FF38EF79' and [x.hex().upper() for x in new_frames] == cpw['check_id_payloads_after_can_id'] == ['00','00','200701000200','0300','FF38EF79'])
check('CheckID is separate raw handshake, not SecurityAccess', 'separate from UDS SecurityAccess' in consumer['classification'] and consumer['location_id_permutation'] == 'frame3 = LocationID[7,6,3,2,1,0]; frame4 = LocationID[5,4]')

print('\n== legacy S-record host transmission path ==')
img = ev['modern_transfer_boundary']['legacy_image_transmission_evidence']
check('S-record parser body pinned', hashlib.sha256(at(0x4A9A9C,0x61F)).hexdigest() == img['srecord_parser']['sha256'] == 'f2f19629ec980462b042bd7abed3c7f73fda6ec894593037159b2d23282a17ba')
check('S-record materializer body pinned', hashlib.sha256(at(0x4AB2D4,0x1D3)).hexdigest() == img['srecord_materializer']['sha256'] == 'abe8a1e2a26ed78326ebfed08f551256edc2fa66394115b0de34fc0d0e6f6e31')
check('legacy data sender body pinned', hashlib.sha256(at(0x45C700,0x165)).hexdigest() == img['data_sender']['sha256'] == 'cf272798d1980d6ab166fc661ddd100bbd323079dc4ded957be124149d063261')
check('legacy data sender uses direct memory-copy helper at TX construction', at(0x45C787,5) == bytes.fromhex('e8b4dd1400'))
check('host-side body coding boundary is closed without ECU-side overclaim', 'copies materialized S-record image bytes unchanged' in img['conclusion'] and 'no host-side coding transform' in img['conclusion'] and 'ECU-side interpretation' in ev['modern_transfer_boundary']['body_coding_boundary'])

check('modern credential fields absent from real legacy descriptor', set(ev['modern_transfer_boundary']['descriptor_fields_absent']) == {'ECUAuthKey','ServiceAuthKey','SeedKey','Nonce','OffsetAddress','SecurityProperty2'} and not any(x in ev['descriptor']['CPU01'] or x in ev['descriptor']['Vehicle'] for x in ev['modern_transfer_boundary']['descriptor_fields_absent']))

print(f'\nResults: {p} passed, {f} failed')
raise SystemExit(1 if f else 0)
