#!/usr/bin/env python3
"""Portable exact-F33 verifier family with per-surface section dispatch.

Each section is the former standalone verifier body, mechanically wrapped so
verification.toml can keep precise path invalidation while the family lives in
one module. External GTS+ and dynamic Camry suites remain separate.
"""
from __future__ import annotations

import argparse


def section_codeflash() -> int:
    """Verify exact 8965F3307000 Camry CodeFlash acquisition and target-native static closure."""
    import hashlib, json, subprocess, sys, tempfile
    from pathlib import Path

    REPO = Path(__file__).resolve().parents[1]
    RAW_DIR = REPO / 'targets/camry-2026/raw-20260826/codeflash'
    RAW = RAW_DIR / 'camry_8965F3307000_codeflash_20260826T213719Z.bin'
    COV = RAW_DIR / 'camry_8965F3307000_codeflash_20260826T213719Z.coverage.bin'
    RUN = RAW_DIR / 'camry_8965F3307000_codeflash_20260826T213719Z.run.json'
    NORM = REPO / 'firmware/camry-8965F3307000/CodeFlash.bin'
    PAYLOAD = REPO / 'targets/camry-2026/raw-20260826/calvin_payload_codeflash_00000000_00200000.bin'
    EVID = REPO / 'data/generated/camry_8965F3307000_decompiler_evidence.json'
    ART = REPO / 'data/generated/camry_8965F3307000_codeflash.json'
    BUILD = REPO / 'tools/analyze_camry_8965F3307000_codeflash.py'
    passed = failed = 0

    def check(name: str, condition: object, detail: str = '') -> None:
        nonlocal passed, failed
        ok = bool(condition); passed += int(ok); failed += int(not ok)
        suffix = f' ({detail})' if detail else ''
        print(f"[{'PASS' if ok else 'FAIL'}][raw_bytes] {name}{suffix}")

    def sha(path: Path) -> str:
        return hashlib.sha256(path.read_bytes()).hexdigest()

    def fnmap(e):
        return {int(row['entry'], 16): row for row in e['functions']}

    def body_bytes(image: bytes, row: dict) -> bytes:
        ranges = row.get("body_ranges") or []
        if not ranges:
            entry = int(row["entry"], 16)
            return image[entry:entry + int(row["body_size"])]
        out = bytearray()
        for r in ranges:
            lo = int(r["min"], 16); hi = int(r["max"], 16)
            out.extend(image[lo:hi + 1])
        return bytes(out)

    art = json.loads(ART.read_text()); evid = json.loads(EVID.read_text()); run = json.loads(RUN.read_text())
    print('== exact acquisition ==')
    check('raw 2 MiB dump exact identity', RAW.stat().st_size == 0x200000 and sha(RAW) == 'b588c7258699beee77669d1f5f09bb17ef8b189b941b46f344a07378c3aaa727')
    check('normalized 1 MiB exact identity', NORM.stat().st_size == 0x100000 and sha(NORM) == '42dce8efc42f6ae31718e7713fa2d26bb9191b4a82439778aee4d7afded9b0e7')
    raw = RAW.read_bytes(); norm = NORM.read_bytes()
    check('normalization is exact lower half', raw[:0x100000] == norm)
    check('upper transport half is erased', raw[0x100000:] == b'\xff' * 0x100000)
    check('coverage bitmap is complete', COV.stat().st_size == 0x80000 and COV.read_bytes() == b'\x01' * 0x80000)
    check('Calvin payload exact identity', PAYLOAD.stat().st_size == 0x1000 and sha(PAYLOAD) == '860f8a3418d23ccfd0861a97efdb9e1d23a8854c3a629b8d7b6821eb93d0b588')
    check('embedded primary F181 at exact offset', norm[0x20860:0x20860+12] == b'8965F3307000')
    check('embedded secondary identity at exact offset', norm[0x17DC0:0x17DC0+12] == b'8A3113303100')
    res = run['result']
    check('live range acquisition complete', res['status'] == 'complete' and res['coverage_percent'] == 100.0 and res['unique_words'] == res['expected_words'] == 524288)
    check('live range acquisition conflict-free', res['conflicts'] == 0 and res['duplicate_words'] == 0 and res['spi_errors'] == 0)
    check('live run hash binds raw dump', res['sha256'] == sha(RAW))
    check('live run exact target route', run['target']['bus'] == 1 and run['target']['elm327_param'] == 1 and run['target']['tx'] == '0x7a1' and run['target']['rx'] == '0x7a9')
    stages = {x['name']: x for x in run['stages']}
    check('live run guarded NRTD', stages['NRTD Ready-status guard']['status'] == 'accepted' and stages['NRTD Ready-status guard']['ready_values'] == [0])
    check('boot placeholder exact', stages['boot identity']['observed_hex'] == '02' + '21' * 32)
    check('stock boot RMBA rejected', stages['boot SID 0x23 codeflash probe']['status'] == 'rejected')
    check('old-stack DID0203 accepted', run['uds_variant'] == 'old' and stages['UDS variant / DID 0x0203']['value'] == '0000000000')
    check('zero 0201/0202 accepted', stages['DID 0x0201/0x0202']['value'] == 'zero16')
    check('authenticated geometry exact', stages['RequestDownload']['data_hex'] == '01460100febf000000001000' and stages['RoutineControl 0x10F0']['data_hex'] == '4500febf000000001000')
    check('callback trigger exact', stages['RoutineControl 0xFF00 callback trigger']['data_hex'] == '3101ff004500000e000000008000')

    print('\n== deterministic static artifact ==')
    with tempfile.TemporaryDirectory() as td:
        out = Path(td) / 'camry.json'
        proc = subprocess.run([sys.executable, str(BUILD), '--out', str(out)], cwd=REPO, capture_output=True, text=True, check=False)
        check('static analyzer succeeds', proc.returncode == 0, proc.stderr[-300:])
        check('static artifact regenerates exactly', proc.returncode == 0 and out.read_bytes() == ART.read_bytes())
    check('static schema exact', art['schema'] == 'camry-8965f3307000-codeflash-static-v1')
    check('decompiler evidence schema exact', evid['schema'] == 'camry-8965f3307000-decompiler-evidence-v1' and evid['function_count'] == 27)
    funcs = fnmap(evid)
    for entry, row in funcs.items():
        check(f'0x{entry:05X} body hash binds exact image', hashlib.sha256(body_bytes(norm, row)).hexdigest() == row['body_sha256'])

    print('\n== normal application Rx configuration ==')
    rx = art['application_rx']
    check('Camry Rx table exact start/count', rx['camry_table_start'] == '0x00021FE8' and rx['camry_descriptor_count'] == 43)
    check('all 40 H descriptors survive', rx['vs_corolla_h']['shared_descriptor_count'] == 40 and rx['vs_corolla_h']['removed_descriptor_count'] == 0)
    check('Camry adds exactly 116/D8/1DA versus H', [(x['can_id'], x['length']) for x in rx['vs_corolla_h']['added']] == [('0x116',8),('0x0D8',8),('0x1DA',8)])
    check('Camry drops old Sienna steering set', {x['can_id'] for x in rx['vs_sienna_b4512000']['removed']} == {'0x2E4','0x191','0x131','0x2FD','0x132','0x423','0x020'})
    check('Camry adds protected B6 versus Sienna', any(x['can_id'] == '0x0B6' and x['can_fd'] and x['length'] == 32 for x in rx['vs_sienna_b4512000']['added']))

    print('\n== target-native SecOC ==')
    sec = art['secoc_receive']
    check('three protected profiles exact', [x['data_id'] for x in sec['profiles']] == ['0x00F','0x0D7','0x0B6'])
    check('slot selector config exact', sec['key_config_address'] == '0x00025828' and sec['key_config_raw_hex'] == '0100000004000000000000000000000000000000' and sec['selector_type'] == 1 and sec['selector'] == 4)
    b6 = sec['profiles'][2]
    check('B6 profile is PDU44', b6['application_pdu_id'] == b6['upper_route_id'] == 44)
    check('B6 profile is 32-byte FV4/MAC28', b6['secured_pdu_length'] == 32 and b6['application_bytes'] == 28 and b6['transmitted_freshness_bits'] == 4 and b6['transmitted_cmac_bits'] == 28)
    check('B6 full freshness/CMAC domains exact', b6['full_freshness_bits'] == 46 and b6['full_cmac_bits'] == 128)
    check('B6 crypto handle is zero', b6['cryptoif_handle'] == 0)
    check('target ICU code programs command 7', 'DAT_ffc5d000 = puVar2[4] << 0x10 | 7;' in funcs[0x8A8E4]['decompiled_c'])
    check('RxIndication enters 3-profile secured queue', 'FUN_0008f2b0' in funcs[0x8EE7C]['decompiled_c'] and 'FUN_0008f34a' in funcs[0x8EE7C]['decompiled_c'])
    check('SecOC lookup has exactly three records', '(&DAT_0002587c)[(short)uVar1 * 0x28]' in funcs[0x8F2B0]['decompiled_c'] and 'if (2 < uVar1)' in funcs[0x8F2B0]['decompiled_c'])
    check('verify worker composes 36-byte auth input', '*(undefined4 *)(puVar1 + -0x62d8) = 0x24;' in funcs[0x8F746]['decompiled_c'] and all(x in funcs[0x8F746]['decompiled_c'] for x in ('FUN_0008f434','FUN_0008ecb2','FUN_0008f676')))

    print('\n== B6 COM and steering-target ingress ==')
    com = art['b6_com']
    check('target TP/COM table geometry exact', com['tp'] == '0x00023DFC' and com['signal_to_pdu_table'] == '0x00022488' and com['pdu_table'] == '0x000226C0' and com['pdu_count'] == 48 and com['signal_count'] == 284)
    check('PDU44 signal ownership exact', com['pdu44_signal_ids'] == list(range(259,276)))
    check('PDU44 scalar/non-scalar split exact', com['scalar_signal_ids'] == list(range(261,274)) and com['non_scalar_bookends'] == [259,260,274,275])
    check('PDU44 buffer/descriptor exact', com['pdu44_buffer_offset'] == '0x1B7' and com['pdu44_descriptor_hex'] == '060000002000000c')
    check('Camry deadline is seven foreground ticks only', com['deadline_descriptor'] == {'configured_value':6,'successful_receive_reload_ticks':7,'tick_period_ms':None})
    fields = {x['signal_id']: x for x in com['wire_fields']}
    check('signal261 is B3 low6', fields[261]['byte_offset'] == 3 and fields[261]['bit_length'] == 6 and fields[261]['bit_start'] == 0 and not fields[261]['signed'])
    check('signal262 is signed B4:B5', fields[262]['byte_offset'] == 4 and fields[262]['bit_length'] == 16 and fields[262]['bit_start'] == 0 and fields[262]['signed'])
    check('B6 unpacker target-native calls exact selector extraction', 'FUN_0007d12a(0x105,0x1ba,6,0,0,&DAT_febe80bc);' in funcs[0x4BD46]['decompiled_c'])
    check('B6 unpacker target-native calls exact signed16 extraction', 'FUN_0007d12a(0x106,0x1bb,0x10,0,1,puVar2 + -0x3748);' in funcs[0x4BD46]['decompiled_c'])
    check('signed16 raw -> staging', 'DAT_febef1fa = DAT_febe80b8;' in funcs[0x58074]['decompiled_c'])
    check('signed16 staging -> snapshot', '*(undefined2 *)(puVar15 + -0x970) = *(undefined2 *)(puVar15 + 0x39fa);' in funcs[0xBCD66]['decompiled_c'])
    check('selector raw -> staging -> snapshot', 'DAT_febef130 = DAT_febe80bc;' in funcs[0x58074]['decompiled_c'] and 'puVar15[-0xa50] = puVar15[0x3930];' in funcs[0xBCD66]['decompiled_c'])
    check('signed target doubles in target conditioner', 'iVar1 = DAT_febeae90 * 2;' in funcs[0xCCF0E]['decompiled_c'])
    check('target conditioner saturates symmetric int16 domain', '0x7fff' in funcs[0xCCF0E]['decompiled_c'] and '-0x7fff' in funcs[0xCCF0E]['decompiled_c'])
    check('independent plausibility path consumes same snapshot', 'sVar3 = *(short *)(puVar11 + -0x970);' in funcs[0xCEE80]['decompiled_c'] and 'FUN_000d0970((int)sVar3)' in funcs[0xCEE80]['decompiled_c'])
    cmd = art['b6_steering_command']
    check('B3 closes as Toyota Target Lateral ID', cmd['selector_signal']['oem_name'] == 'Target Lateral ID' and cmd['selector_signal']['accepted_controller_values'] == {'1':'PCS','4':'LDA','10':'Hands Off LTA','11':'LTA/LCA','18':'SDG','19':'PDA'} and cmd['selector_signal']['additional_target_native_value'] == {'49':'Self-Propelled Transport'})
    check('target-native selector decoder consumes B3 snapshot', all(tok in funcs[0xCEFFC]['decompiled_c'] for tok in ("DAT_febeadb0", "DAT_febeadb0 == '\\x01'", "DAT_febeadb0 == '\\x04'", "DAT_febeadb0 == '\\n'", "DAT_febeadb0 == '\\v'", "DAT_febeadb0 == '\\x12'", "DAT_febeadb0 == '\\x13'")))
    check('auxiliary selector consumer recognizes value49', "DAT_febeadb0 == '1'" in funcs[0xCB73A]['decompiled_c'])

    print('\n== Camry-native measured steering angle / target comparator ==')
    feedback = cmd['measured_steering_angle_feedback']
    check('025 is target-native PDU35 at buffer 0x127', feedback['can_id'] == '0x025' and feedback['pdu_id'] == 35 and feedback['buffer_offset'] == '0x127')
    check('025 coarse field is signed12 signal187', feedback['coarse_signal']['signal_id'] == 187 and feedback['coarse_signal']['wire'] == 'B0..B1 signed12' and feedback['coarse_signal']['techstream_did'] == '0x1037' and feedback['coarse_signal']['techstream_name'] == 'Steering Angle' and feedback['coarse_signal']['scale_deg_per_count'] == 1.5)
    check('025 fractional field is signed4 signal188', feedback['fraction_signal']['signal_id'] == 188 and feedback['fraction_signal']['wire'] == 'B4[7:4] signed4' and feedback['fraction_signal']['scale_deg_per_count'] == 0.1)
    check('025 unpacker extracts exact coarse/fraction fields', all(tok in funcs[0x4B59E]['decompiled_c'] for tok in ('FUN_0007d12a(0xbb,0x127,0xc,0,1,&DAT_febe8048);','FUN_0007d12a(0xbc,299,4,4,1,puVar2 + -0x37b1);')))
    check('Camry DID1037 row binds callback 4DBF8', feedback['did1037_row'] == {'address':'0x000293AC','callback':'0x0004DBF8','raw_hex':'37100200f8db04000000000000000000'} and 'DAT_febe7d46' in funcs[0x4DBF8]['decompiled_c'])
    check('measured angle reconstruction is target native', '* 0xf' in funcs[0xB3B06]['decompiled_c'] and '* 0x6fb' in funcs[0xCE9EA]['decompiled_c'] and '0x200' in funcs[0xCE9EA]['decompiled_c'] and all(tok in funcs[0xCEADA]['decompiled_c'] for tok in ('DAT_febecad2','DAT_febecad4','DAT_febecad6')))
    cmp = cmd['target_minus_measured_comparator']
    check('clean comparator is 0xCD128', cmp['entry'] == '0x000CD128' and funcs[0xCD128]['body_size'] == 376)
    check('same gain is applied before target-minus-measured subtraction', all(tok in funcs[0xCD128]['decompiled_c'] for tok in ('iVar1 = (iVar1 * 0xb76) / 0x400;','DAT_febec8dc = (iVar2 * 0xb76) / 0x400;','DAT_febec8e0 = iVar1 - DAT_febec8dc;')))
    check('B6 signal262 is target steering angle', cmd['signed_target_signal']['classification'] == 'target steering angle command' and 'target steering angle' in cmd['classification'])
    scale = cmd['controller_equivalent_scale']
    check('controller-equivalent B6 scale exact fraction', scale['fraction_deg_per_b6_count'] == {'numerator':1024,'denominator':17870})
    check('controller-equivalent scale is ~1.00012 mrad/count', abs(scale['mrad_per_b6_count'] - 1.000121519) < 1e-9 and 'does not literally name' in scale['boundary'])
    check('Corolla wall-clock timing not transferred', 'does not transfer Corolla H' in art['b6_com']['boundary'])

    print('\n== documentation ==')
    doc = (REPO / 'docs/variants/camry-2026-live-baseline.md').read_text()
    for tok in ('b588c7258699beee', '42dce8efc42f6ae3', '0x25848', 'PDU44', 'signal 262', 'B4:B5', '0xCCF0E'):
        check(f'variant report contains {tok}', tok in doc)
    findings = (REPO / 'docs/status/FINDINGS.md').read_text()
    check('VAR-054 retained', '| VAR-054 |' in findings and '8965F3307000' in findings)

    print(f'\nResults: {passed} passed, {failed} failed')
    return 1 if failed else 0


def section_flash_backend() -> int:
    """Verify exact-F33 plus Toyota T-0035 FACI behavior used by the patch backend."""
    import hashlib, json
    from pathlib import Path

    ROOT = Path(__file__).resolve().parents[1]
    IMAGE = ROOT / 'firmware/camry-8965F3307000/CodeFlash.bin'
    F33 = ROOT / 'data/generated/camry_8965F3307000_flash_backend_evidence.json'
    T0035 = ROOT / 'data/generated/techstream_v18/t0035_faci_backend_evidence.json'
    FLASH = ROOT / 'exploit/patcher/flash_backend.c'
    LOCK = ROOT / 'software/locks/toyota-cuw-corpus.json'

    passed=failed=0
    def check(name, cond, detail=''):
        nonlocal passed, failed
        ok=bool(cond); passed+=ok; failed+=not ok
        print(f"[{'PASS' if ok else 'FAIL'}][raw_bytes] {name}" + (f' ({detail})' if detail else ''))

    def funcs(obj):
        return {int(x['entry'],16):x for x in obj['functions']}

    image=IMAGE.read_bytes(); f33=json.loads(F33.read_text()); t=json.loads(T0035.read_text()); flash=FLASH.read_text().lower()
    lock=json.loads(LOCK.read_text())

    print('== exact F33 boot flash-control evidence ==')
    check('F33 flash evidence is exact-image bound', f33['software_id']=='8965F3307000' and f33['image']['sha256']==hashlib.sha256(image).hexdigest())
    F=funcs(f33)
    for entry,row in F.items():
        size=row['body_size']; check(f'F33 function 0x{entry:X} raw body hash', hashlib.sha256(image[entry:entry+size]).hexdigest()==row['body_sha256'])
    check('F33 ready helper uses FSTATR bit15', '& 0x8000' in F[0x78BFA]['decompiled_c'])
    status=F[0x78C30]['decompiled_c']
    check('F33 status-clear helper uses FSTATR error bit and FASTAT command-lock family', all(x in status for x in ('& 0x4000','0xffa10010','0x10','0xffa20000,0x50')))
    forced=F[0x78CE6]['decompiled_c']
    check('F33 forced-stop helper emits B3 and waits on ready', '0xffa20000,0xb3' in forced and '0x8000,0x8000' in forced)
    program=F[0x78E2A]['decompiled_c']
    write='FUN_00078aec(0xffa20000,local_20[uVar5]);'; dbfull='if ((uVar2 & 0x400) != 0)'
    check('F33 native program routine checks DBFULL bit10 after each halfword write', write in program and dbfull in program and program.index(write)<program.index(dbfull))
    check('F33 native program routine uses E8 and terminal D0', '0xffa20000,0xe8' in program and '0xffa20000,0xd0' in program)
    check('F33 native final status mask remains 0x24068', '& 0x24068' in F[0x79026]['decompiled_c'])

    print('\n== exact Toyota T-0035 manufacturer evidence ==')
    check('T-0035 artifact source is pinned corpus member', t['source']=={'filename':'T-0035-22.cuw','sha256':'9882b1b6dd6acda2d142a2825eda396b0a425e41c13f822b9a18e022d4c43e81','size':5725237})
    locked=next(x for x in lock['artifacts'] if x['filename']=='T-0035-22.cuw')
    check('T-0035 generated evidence agrees with corpus lock', locked['sha256']==t['source']['sha256'] and locked['size']==t['source']['size'])
    check('T-0035 is exact P5-Unified EPS/Tundra 07A1 package', t['package']['contact_type']=='P5-Unified' and t['package']['diag_id']=='07A1' and t['package']['vehicle']=='TUNDRA')
    check('both manufacturer CPU erase payloads are 4KiB at FEBF0000 and CMAC-valid', len(t['cpus'])==2 and all(x['erase']['load_address']=='0xFEBF0000' and x['erase']['size']==0x1000 and x['erase']['cmac_valid'] for x in t['cpus']))
    check('manufacturer program semantics use post-write DBFULL bit10, not SUSRDY bit11', '0x00000400 (DBFULL)' in t['recovered_faci_semantics']['program_sequence'] and 'bit10/0x400' in t['recovered_faci_semantics']['program_pacing_boundary'] and 'do not use bit11/0x800' in t['recovered_faci_semantics']['program_pacing_boundary'])
    check('manufacturer error/command-lock families are exact', t['recovered_faci_semantics']['fstatr_error_mask']=='0x00007040' and t['recovered_faci_semantics']['command_lock_mask']=='FASTAT 0x10')
    check('manufacturer erase and P/E entry sequences are recovered', t['recovered_faci_semantics']['erase_sequence']=='FPSADDR=1; FSADDR; 0x20; D0' and 'FENTRYR=AA01' in t['recovered_faci_semantics']['pe_entry'] and 'FPROTR=5501' in t['recovered_faci_semantics']['pe_entry'])
    check('manufacturer scope stays Tundra/F3 bounded', 'not an exact 8965F3307000 Camry calibration package' in t['scope_boundary'])

    print('\n== patcher convergence ==')
    check('patcher now uses DBFULL 0x400', 'fstatr_dbfull_mask' in flash and '0x00000400u' in flash)
    check('patcher waits after each programmed halfword', flash.index('faci_fdata = word') < flash.index('while ((faci_fstatr & fstatr_dbfull_mask) != 0u)'))
    check('patcher no longer uses 0x800 pacing interpretation', 'fstatr_program_pace_mask' not in flash and '0x00000800u' not in flash)
    check('patcher retains F33/Toyota error and recovery families', all(x in flash for x in ('fstatr_error_mask         0x00007040u','fastat_cmdlk_mask         0x10u','faci_fcmd8 = 0xb3u','faci_fcmd8 = 0x50u')))

    print(f'\n{passed} passed, {failed} failed')
    return 1 if failed else 0


def section_secoc_patch() -> int:
    """Verify the exact 2026 Camry 8965F3307000 SecOC Gate-2 patch contract."""

    import hashlib
    import json
    import sys
    from pathlib import Path

    REPO = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(REPO))

    from exploit.patcher.build_payload import make_restore_config, simulate_apply  # noqa: E402
    from exploit.patcher.patch_config import config_from_manifest  # noqa: E402
    from tools.build_secoc_patch_manifest import build_manifest, crc32  # noqa: E402

    IMAGE = REPO / "firmware/camry-8965F3307000/CodeFlash.bin"
    SIENNA = REPO / "firmware/RH850_P1M-E_CodeFlash.bin"
    GATE = REPO / "data/generated/secoc_gate_resolution_8965F3307000_minimal.json"
    MANIFEST = REPO / "data/generated/secoc_patch_manifest_8965F3307000.json"
    IMAGE_SHA = "42dce8efc42f6ae31718e7713fa2d26bb9191b4a82439778aee4d7afded9b0e7"

    passed = failed = 0


    def check(name: str, condition: object, detail: str = "") -> None:
        nonlocal passed, failed
        ok = bool(condition)
        passed += int(ok)
        failed += int(not ok)
        print(f"[{'PASS' if ok else 'FAIL'}][raw_bytes] {name}" + (f" ({detail})" if detail else ""))


    def occurrences(blob: bytes, needle: bytes) -> list[int]:
        out: list[int] = []
        pos = 0
        while True:
            pos = blob.find(needle, pos)
            if pos < 0:
                return out
            out.append(pos)
            pos += 1


    image = IMAGE.read_bytes()
    sienna = SIENNA.read_bytes()
    gate = json.loads(GATE.read_text(encoding="utf-8"))
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))

    print("== exact F33 image and crypto-root provenance ==")
    check("normalized F33 CodeFlash is exactly 1 MiB", len(image) == 0x100000)
    check("normalized F33 SHA-256 is pinned", hashlib.sha256(image).hexdigest() == IMAGE_SHA)
    for start, label in ((0xBFD8, "payload-build root"), (0xBFE8, "boot-SA root"), (0x20840, "application-SA root")):
        f33 = image[start:start + 16]
        check(f"F33 {label} is 16 bytes and byte-identical to canonical Sienna", len(f33) == 16 and f33 == sienna[start:start + 16])

    print("\n== target-native Gate-2 semantic result ==")
    check("fresh bare-import semantic resolver is unique and SHA-bound",
          gate["candidate_count"] == 1 and gate["resolution"] == "unique" and gate["program_sha256"] == IMAGE_SHA)
    check("F33 Gate-2 owner and CMP are exact",
          gate["function"]["entry"] == "0x0008f906" and gate["patch"]["address"] == "0x0008f952")
    check("F33 patch is CMP neutralization",
          gate["patch"]["original"] == "e0d1" and gate["patch"]["replacement"] == "e001"
          and gate["patch"]["operation"] == "cmp-second-register-to-first-force-fallthrough")
    check("verify-result polarity is zero-success", gate["verify_result_polarity"] == "zero-is-verified-ok-nonzero-is-not-verified")
    flow = gate["control_flow"]
    check("F33 BNE topology is exact",
          flow["bne"] == "0x0008f954" and flow["bne_bytes"] == "9a0d"
          and flow["verified_delivery_fallthrough"] == "0x0008f956"
          and flow["mismatch_branch_target"] == "0x0008f966" and flow["join"] == "0x0008f96e")
    check("both stock arms retain calls", flow["verified_fallthrough_calls"] == 2 and flow["mismatch_branch_calls"] == 1)
    egg = bytes.fromhex("e0d19a0d1a38bfff")
    check("full Gate-2 machine anchor is unique in exact F33", occurrences(image, egg) == [0x8F952])
    check("raw patch preimage is exact", image[0x8F952:0x8F954] == bytes.fromhex("e0d1"))

    print("\n== deterministic F33 manifest and CRC resign ==")
    rebuilt = build_manifest(gate, IMAGE, 0)
    check("committed F33 patch manifest is deterministic", rebuilt == manifest)
    check("manifest is exact-image/preimage bound",
          manifest["image"]["sha256"] == IMAGE_SHA and manifest["patch"] == {
              "address": "0x8F952", "block_base": "0x88000", "block_size": 32768,
              "original": "e0d1", "preimage_verified": True, "replacement": "e001",
          })
    crc = manifest["boot_crc"]
    check("F33 high boot CRC is stock-valid",
          crc["start"] == "0x18000" and crc["end"] == "0xFFDF0"
          and crc["fixup_va"] == "0xFFDEC" and crc["stock_region_valid"] is True
          and crc["stock_residue"] == "0xFFFFFFFF")
    check("F33 patch has deterministic repaired fixup/residue",
          crc["patched_prefix_crc_for_supplied_image"] == "0x2650CC50"
          and crc["patched_fixup_for_supplied_image"] == "0xD9AF33AF"
          and crc["patched_residue_for_supplied_image"] == "0xFFFFFFFF")
    check("both self-describing F33 CRC regions validate",
          manifest["discovery"]["crc_descriptor_count"] == 2
          and all(row["terminal_fixup_valid"] for row in manifest["discovery"]["crc_descriptors"]))

    print("\n== generic patcher apply/restore simulation ==")
    apply_cfg = config_from_manifest(manifest, mode="apply")
    patched, patched_fixup, patched_residue = simulate_apply(image, apply_cfg)
    check("generic patcher simulation applies only the target predicate plus CRC fixup",
          patched[0x8F952:0x8F954] == bytes.fromhex("e001")
          and patched_fixup == 0xD9AF33AF and patched_residue == 0xFFFFFFFF)
    restore_cfg = make_restore_config(apply_cfg)
    restored, restore_fixup, restore_residue = simulate_apply(patched, restore_cfg)
    check("generic restore simulation recovers original Gate-2 bytes", restored[0x8F952:0x8F954] == bytes.fromhex("e0d1"))
    check("generic restore simulation returns the exact stock image",
          restored == image and restore_fixup == int(crc["stored_fixup"], 0) and restore_residue == 0xFFFFFFFF)
    check("direct CRC of simulated patched high region is valid",
          crc32(patched[int(crc["start"], 0):int(crc["end"], 0)]) == 0xFFFFFFFF)

    print(f"\n{passed} passed, {failed} failed")
    return 1 if failed else 0


def section_lateral_static() -> int:
    """Verify exact-F33 target-native lateral/static closure from tracked bytes/evidence."""

    import hashlib
    import json
    import subprocess
    import sys
    import tempfile
    from pathlib import Path

    ROOT = Path(__file__).resolve().parents[1]
    IMAGE = ROOT / "firmware/camry-8965F3307000/CodeFlash.bin"
    EVID = ROOT / "data/generated/camry_8965F3307000_lateral_decompiler_evidence.json"
    ART = ROOT / "data/generated/camry_8965F3307000_lateral_static.json"
    BUILD = ROOT / "tools/build_camry_8965F3307000_lateral_static.py"
    CODEFLASH = ROOT / "data/generated/camry_8965F3307000_codeflash.json"
    PRODUCT = ROOT / "data/p1me_product_memory.json"
    RUNTIME = ROOT / "data/generated/camry_8965F3307000_command5_runtime_carrier.json"
    BASELINE = ROOT / "docs/variants/camry-2026-live-baseline.md"
    FINDINGS = ROOT / "docs/status/FINDINGS.md"

    p = f = 0


    def sha(data: bytes) -> str:
        return hashlib.sha256(data).hexdigest()


    def body_bytes(image: bytes, row: dict) -> bytes:
        ranges = row.get("body_ranges") or []
        if not ranges:
            entry = int(row["entry"], 16); return image[entry:entry + int(row["body_size"])]
        out = bytearray()
        for r in ranges:
            lo = int(r["min"], 16); hi = int(r["max"], 16); out.extend(image[lo:hi + 1])
        return bytes(out)


    def check(name: str, ok: object) -> None:
        nonlocal p, f
        yes = bool(ok)
        p += int(yes)
        f += int(not yes)
        print(f"[{'PASS' if yes else 'FAIL'}] {name}")


    img = IMAGE.read_bytes()
    evid = json.loads(EVID.read_text(encoding="utf-8"))
    art = json.loads(ART.read_text(encoding="utf-8"))
    codeflash = json.loads(CODEFLASH.read_text(encoding="utf-8"))
    product = json.loads(PRODUCT.read_text(encoding="utf-8"))
    runtime = json.loads(RUNTIME.read_text(encoding="utf-8"))
    funcs = {int(row["entry"], 16): row for row in evid["functions"]}

    print("== deterministic target evidence ==")
    check("artifact schema/target exact", art["schema"] == "camry-8965f3307000-lateral-static-v1" and art["target"]["software_id"] == "8965F3307000" and art["target"]["mcu"] == "R7F701381")
    check("decompiler evidence exact schema/image", evid["schema"] == "camry-8965f3307000-lateral-decompiler-evidence-v1" and evid["function_count"] == len(funcs) == 31 and evid["image"]["sha256"] == sha(img) == art["target"]["codeflash_sha256"])
    for entry, row in sorted(funcs.items()):
        check(f"0x{entry:08X} body hash", sha(body_bytes(img, row)) == row["body_sha256"])
    with tempfile.TemporaryDirectory(prefix="camry-f33-lateral-") as td:
        out = Path(td) / "lateral.json"
        r = subprocess.run([sys.executable, str(BUILD), "--out", str(out)], cwd=ROOT, capture_output=True, text=True)
        check("builder exits cleanly", r.returncode == 0)
        check("builder reproduces artifact byte-exact", out.exists() and out.read_bytes() == ART.read_bytes())

    print("\n== exact timer / B6 deadline ==")
    t = art["foreground_timing"]
    check("R7F701381 exact 1MiB product pinned", product["products"]["R7F701381"]["codeflash_bytes"] == 0x100000 and product["products"]["R7F701381"]["regulator"] == "DPS")
    check("TAUJ official 80MHz P-Bus source pinned", product["timer"]["p_bus_hz"] == 80_000_000 and any("TAUJ" in x and "80 MHz" in x for x in product["sources"]["datasheet"]["references"]))
    check("target timer entries exact", t["loop"] == "0x00066062" and t["timer_init"] == "0x0006639C" and t["timer_reload"] == "0x00066512")
    check("target timer config no prescale", t["tps"] == t["brs"] == t["cmor_ch3"] == 0 and "Ramffe50090 = 0;" in funcs[0x6639C]["decompiled_c"] and "Ramffe50080 = 0;" in funcs[0x6639C]["decompiled_c"])
    terms = [int.from_bytes(img[0x30DF0 + 4*i:0x30DF4 + 4*i], "little") for i in range(8)]
    check("target timer raw terms exact", terms == [16000, 800, 32000, 9200, 80000, 9600, 400000, 10000])
    check("first interval 410000 / 5.125ms", t["initial_counts"] == 410000 and t["initial_period_ms"] == 5.125)
    check("steady interval 400000 / 5ms", t["steady_counts"] == 400000 and t["steady_period_ms"] == 5.0)
    check("foreground polls/clears channel3 flag", t["tick_flag"] == "FFFFB111 bit4" and "(bVar1 & 0x10) == 0" in funcs[0x66062]["decompiled_c"] and "DAT_ffffb110._1_1_ = bVar1 & 0xef;" in funcs[0x66062]["decompiled_c"])
    check("B6 deadline seven ticks / 35ms", t["b6_successful_receive_reload_ticks"] == codeflash["b6_com"]["deadline_descriptor"]["successful_receive_reload_ticks"] == 7 and t["b6_nominal_steady_timeout_ms"] == 35.0)

    print("\n== mode2 command envelope / sequence ==")
    e = art["lta_lca_mode2_envelope"]
    check("Target Lateral ID11 selects mode2", e["target_lateral_id"] == 11 and e["oem_name"] == "LTA/LCA" and e["internal_mode"] == 2 and "DAT_febeadb0 == '\\v'" in funcs[0xCEFFC]["decompiled_c"])
    check("mode2 absolute 1745 exact", e["absolute_target_raw"] == 1745 and int.from_bytes(img[0x12978:0x1297A], "little") == int.from_bytes(img[0x1A978:0x1A97A], "little") == 1745)
    check("mode2 per-gap 78 exact", e["per_effective_sequence_gap_raw"] == 78 and int.from_bytes(img[0x1297A:0x1297C], "little") == int.from_bytes(img[0x1A97A:0x1A97C], "little") == 78)
    check("absolute controller-equivalent about 100deg", 99.98 < e["absolute_target_deg_controller_equivalent"] < 100.01)
    check("per-gap controller-equivalent about 4.47deg", 4.46 < e["per_effective_sequence_gap_deg_controller_equivalent"] < 4.48)
    check("sequence modulus/gap cap exact", e["sequence_modulus"] == 64 and e["sequence_gap_cap"] == 8 and int.from_bytes(img[0xB0620:0xB0622], "little") == 63 and int.from_bytes(img[0xB0622:0xB0624], "little") == 8)
    check("maximum ECU relaxed gap exact", e["max_relaxed_gap_delta_raw"] == 624)
    check("conditioned internal limits exact", e["conditioned_absolute_doubled_domain"] == int.from_bytes(img[0xB0666:0xB0668], "little") == 3490 and e["conditioned_per_call_doubled_domain"] == int.from_bytes(img[0x1299A:0x1299C], "little") == int.from_bytes(img[0x1A99A:0x1A99C], "little") == 7)
    check("target delta deadband exact", e["delta_deadband_raw"] == int.from_bytes(img[0xB061C:0xB061E], "little") == 87)
    scale = e["b6_scale"]
    check("B6 physical scale exact fraction", scale["fraction_deg_per_b6_count"] == {"numerator": 1024, "denominator": 17870} and abs(scale["mrad_per_b6_count"] - 1.0001215187701138) < 1e-15)
    check("Panda boundary rejects ECU gap relaxation", "exact modulo-64 +1" in e["panda_boundary"] and "should not use the ECU gap relaxation" in e["panda_boundary"])

    print("\n== companion B6 fields ==")
    s = art["secondary_b6_fields"]
    check("signal265 suppressor exact role", s["signal265"]["wire"] == "B6[2]" and s["signal265"]["exact_oem_name"] is None and "suppress" in s["signal265"]["role"] and "DAT_febeadbb" in funcs[0xCDA20]["decompiled_c"])
    check("signal268 application sequence exact role", s["signal268"]["wire"] == "B7[5:0]" and s["signal268"]["exact_oem_name"] is None and "modulo-64 sequence" in s["signal268"]["role"] and "DAT_febeadbc" in funcs[0xCEC8A]["decompiled_c"])
    check("signal269 percentage contribution exact role", s["signal269"]["wire"] == "B8" and "/100" not in s["signal269"]["role"] and "divided by 100" in s["signal269"]["role"] and "DAT_febeadbd" in funcs[0xCE3AA]["decompiled_c"] and ") / 100" in funcs[0xCE3AA]["decompiled_c"])
    check("signal270 percentage contribution exact role", s["signal270"]["wire"] == "B9" and "divided by 100" in s["signal270"]["role"] and "DAT_febeadbe" in funcs[0xCDFF8]["decompiled_c"] and ") / 100" in funcs[0xCDFF8]["decompiled_c"])
    check("unnamed-field boundary preserved", all(s[k]["exact_oem_name"] is None for k in ("signal265", "signal268", "signal269", "signal270")) and "stay unnamed" in s["boundary"])

    print("\n== steering-rate monitor ==")
    r = art["steering_rate_monitor"]
    check("025 signal189 is Steering Angle Velocity", r["can_id"] == "0x025" and r["signal_id"] == 189 and r["techstream_name"] == "Steering Angle Velocity" and r["did"] == "0x1036")
    check("rate callback exact", r["callback"] == "0x0004DBBC" and int.from_bytes(img[0x2939C:0x2939E], "little") == 0x1036 and int.from_bytes(img[0x293A0:0x293A4], "little") == 0x4DBBC)
    check("rate raw extraction exact", r["raw_destination"] == "gp-0x37B6" and "FUN_0007d12a(0xbd,299,0xc,0,1,puVar2 + -0x37b6)" in funcs[0x4B59E]["decompiled_c"])
    check("rate diagnostic conversion exact", "DAT_febe66a4" in funcs[0x4DBBC]["decompiled_c"] and "* 0x168) / 0x400" in funcs[0x4DBBC]["decompiled_c"])
    check("rate monitor raw threshold exact", r["mode2_abs_raw_threshold"] == int.from_bytes(img[0xB066E:0xB0670], "little") == 100 and r["monitor_entry"] == "0x000CED28")
    check("rate monitor persistence exact", r["mode2_persistence_cycles"] == int.from_bytes(img[0x12968:0x1296A], "little") == int.from_bytes(img[0x1A968:0x1A96A], "little") == 79)
    check("rate persistence is 395ms at steady tick", r["steady_persistence_time_ms_if_continuously_violating"] == 395.0)
    check("rate threshold policy boundary explicit", "not" not in r["boundary"].lower() or "production Panda policy" in r["boundary"])

    print("\n== driver torque / Q-current boundaries ==")
    d = art["driver_torque"]
    check("DID1035 exact Toyota identity/source", d["did"] == "0x1035" and d["techstream_name"] == "Steering Wheel Torque" and d["callback"] == "0x0004DB70" and d["raw_source"] == "gp-0x5158")
    check("DID1035 physical formula and display clamp", d["physical_formula"] == "N.m = raw / 256" and d["diagnostic_display_clamp_nm"] == 25.0 and "* 1000) / 0x100" in funcs[0x4DB70]["decompiled_c"] and "&LAB_000061a8" in funcs[0x4DB70]["decompiled_c"])
    check("DID1035 validity magic exact", d["validity_magic"] == "0xA5AA5AA5" and "-0x5aa5a55b" in funcs[0x4DB70]["decompiled_c"])
    check("correct normalized torque acquisition clamp is 2109", d["sensor_acquisition_saturation_raw"] == int.from_bytes(img[0x30E52:0x30E54], "little") == 2109 and d["sensor_acquisition_saturation_calibration"] == "normalized CodeFlash 0x00030E52")
    check("2109 raw is about 8.238Nm representation limit", abs(d["sensor_acquisition_saturation_nm"] - 8.23828125) < 1e-12 and d["override_threshold_recovered"] is False and "not a driver-override threshold" in d["boundary"])
    check("torque whole-corpus direct/fixed-GP census exact", d["direct_fixed_gp_reference_entries"] == ["0x00035A06", "0x0004C000", "0x0004C490", "0x0004DB70", "0x00052CA0", "0x00054244", "0x000564CE", "0x00059448", "0x0005D5E0"] and d["read_reference_entries"] == d["direct_fixed_gp_reference_entries"][:7] and d["write_reference_entries"] == d["direct_fixed_gp_reference_entries"][7:] and evid["fixed_gp_census"]["driver_torque_source"]["resolved_address"] == "0xFEBE66A8")
    check("torque cooperative cone direct/fixed-GP intersection empty", d["cooperative_c8_d1_direct_fixed_gp_intersection"] == [])
    q = art["q_current"]
    check("DID1151 exact Toyota identity/source", q["did"] == "0x1151" and q["techstream_name"] == "Motor Actual Current (Q Axis)" and q["callback"] == "0x0004E394" and q["raw_source"] == "gp-0x50F2")
    check("DID1151 formula exact", q["physical_formula"] == "A = raw / 128" and q["diagnostic_formula"] == "displayed centi-A = (raw * 100) / 0x80" and "* 100) / 0x80" in funcs[0x4E394]["decompiled_c"])
    check("Q-current whole-corpus direct/fixed-GP census exact", q["direct_fixed_gp_reference_entries"] == ["0x0004E394", "0x00052CA0", "0x00054244", "0x000564CE", "0x00059448", "0x0005D12C"] and q["read_reference_entries"] == q["direct_fixed_gp_reference_entries"][:4] and q["write_reference_entries"] == q["direct_fixed_gp_reference_entries"][4:] and evid["fixed_gp_census"]["q_current_source"]["resolved_address"] == "0xFEBE670E")
    check("Q-current cooperative cone direct/fixed-GP intersection empty", q["cooperative_c8_d1_direct_fixed_gp_intersection"] == [] and q["response_threshold_recovered"] is False)
    check("negative census boundary explicit", "computed aliases" in evid["fixed_gp_census"]["boundary"].lower() and "dma" in evid["fixed_gp_census"]["boundary"].lower())

    print("\n== runtime/static-live boundary ==")
    rr = art["runtime_readiness"]
    check("runtime anchors exact", rr["application_context_init"] == "0x000715B4" and rr["startup_coordinator"] == "0x000637EE" and rr["startup_final_init"] == "0x000701EA" and rr["foreground_loop"] == "0x00066062")
    check("runtime low carrier construction is retained only as disproved history", rr["static_low_carrier_constructed"] is True and rr["low_carrier_disproved"] is True and rr["static_command5_carrier_artifact"] == "data/generated/camry_8965F3307000_command5_runtime_carrier.json" and runtime["boundary"]["static_low_carrier_candidate_closed"] is True)
    check("verified high-tail retention is joined exactly", rr["high_tail_live_retention_closed"] is True and rr["high_tail_base"] == "0xFEBFF9F0" and rr["high_tail_end_exclusive"] == "0xFEBFFBFC" and runtime["boundary"]["verified_high_tail_live_retention_closed"] is True)
    check("signer permission/latency/application pivot remain open", rr["live_slot4_permission_closed"] is False and rr["command5_latency_closed"] is False and rr["application_mode_execution_pivot_closed"] is False)
    b = art["boundary"]
    check("static envelope/timing/rate closed", b["target_native_mode2_envelope_closed"] and b["target_native_rate_monitor_closed"] and b["target_native_timing_closed"])
    check("override/current response not invented", not b["driver_override_numeric_threshold_closed"] and not b["motor_current_response_threshold_closed"])
    check("stock sender/relay/production remain open", not b["stock_b6_cadence_template_freshness_closed"] and not b["relay_suppression_live_closed"] and not b["production_lateral_output_authorized"])
    check("runtime carrier itself forbids actuation", runtime["boundary"]["vehicle_actuation_authorized"] is False and runtime["boundary"]["steering_can_transmit_used"] is False)

    print("\n== canonical docs ==")
    doc = BASELINE.read_text(encoding="utf-8")
    for token in ("5.000-ms", "35 ms", "±1745", "78 counts", "signal 265", "Steering Angle Velocity", "±2109", "0x637EE", "FEBF0307"):
        check(f"Camry §12 contains {token}", token in doc)
    findings = FINDINGS.read_text(encoding="utf-8")
    check("VAR-056 registered", "| VAR-056 |" in findings and "8965F3307000" in findings)
    check("VAR-056 verifier family named", "verify_camry_8965F3307000.py" in findings)

    print(f"\nResults: {p} passed, {f} failed")
    return 1 if f else 0


def section_tss3_opendbc_port() -> int:
    """Verify exact-F33 Tx/status evidence for the passive Camry TSS3 opendbc port."""

    import hashlib
    import json
    import subprocess
    import sys
    import tempfile
    from pathlib import Path

    ROOT = Path(__file__).resolve().parents[1]
    IMAGE = ROOT / "firmware/camry-8965F3307000/CodeFlash.bin"
    EVID = ROOT / "data/generated/camry_8965F3307000_tss3_tx_decompiler_evidence.json"
    ART = ROOT / "data/generated/camry_8965F3307000_tss3_opendbc_port.json"
    BUILD = ROOT / "tools/build_camry_8965F3307000_tss3_opendbc_port.py"
    REPORT = ROOT / "docs/variants/camry-2026-tss3-opendbc-port.md"
    FINDINGS = ROOT / "docs/status/FINDINGS.md"
    CORRECTIONS = ROOT / "docs/status/CORRECTIONS.md"
    PRIORITIES = ROOT / "docs/status/PRIORITIES.md"

    p = f = 0


    def sha(data: bytes) -> str:
        return hashlib.sha256(data).hexdigest()


    def body_bytes(image: bytes, row: dict) -> bytes:
        ranges=row.get("body_ranges") or []
        if not ranges:
            e=int(row["entry"],16); return image[e:e+int(row["body_size"])]
        out=bytearray()
        for r in ranges:
            lo=int(r["min"],16); hi=int(r["max"],16); out.extend(image[lo:hi+1])
        return bytes(out)


    def check(name: str, ok: object) -> None:
        nonlocal p, f
        yes = bool(ok)
        p += int(yes)
        f += int(not yes)
        print(f"[{'PASS' if yes else 'FAIL'}] {name}")


    img = IMAGE.read_bytes()
    evid = json.loads(EVID.read_text(encoding="utf-8"))
    art = json.loads(ART.read_text(encoding="utf-8"))
    funcs = {int(row["entry"], 16): row for row in evid["functions"]}

    print("== target/evidence identity ==")
    check("artifact schema/target", art["schema"] == "camry-8965f3307000-tss3-opendbc-port-v1" and art["target"]["software_id"] == "8965F3307000")
    check("exact image hash", sha(img) == evid["image"]["sha256"] == art["target"]["codeflash_sha256"] == "42dce8efc42f6ae31718e7713fa2d26bb9191b4a82439778aee4d7afded9b0e7")
    check("compact evidence exact", evid["schema"] == "camry-8965f3307000-tss3-tx-decompiler-evidence-v1" and evid["function_count"] == len(funcs) == 11)
    for entry, row in sorted(funcs.items()):
        check(f"0x{entry:08X} body hash", sha(body_bytes(img,row)) == row["body_sha256"])
    with tempfile.TemporaryDirectory(prefix="camry-f33-tss3-port-") as td:
        out = Path(td) / "port.json"
        r = subprocess.run([sys.executable, str(BUILD), "--out", str(out)], cwd=ROOT, capture_output=True, text=True)
        check("builder exits cleanly", r.returncode == 0)
        check("builder reproduces artifact byte-exact", out.exists() and out.read_bytes() == ART.read_bytes())

    print("\n== exact F33 generated-COM Tx geometry ==")
    tx = art["generated_com_tx"]
    check("Tx table exact address", tx["tx_table"] == "0x00021F58")
    check("first five Tx IDs exact", [(x["can_id"], x["can_fd"]) for x in tx["first_five"]] == [("0x030", True), ("0x351", False), ("0x394", False), ("0x4A3", False), ("0x4C8", False)])
    check("signal/PDU tables exact", tx["signal_to_pdu_table"] == "0x00022488" and tx["pdu_table"] == "0x000226C0" and tx["signal_count"] == 284)
    check("PDU descriptors exact", tx["pdu_descriptors"] == {
        "0": [2, 0, 0, 32, 0, 3], "1": [200, 0, 0, 4, 0, 3], "2": [60, 0, 0, 3, 0, 3],
        "3": [100, 0, 0, 8, 0, 3], "4": [196, 0, 0, 8, 0, 3],
    })
    check("0x351 signal allocation exact", tx["signal_allocations"]["1"] == [38, 39])
    check("0x394 signal allocation exact", tx["signal_allocations"]["2"] == [40, 41, 42, 43])
    check("0x4A3 signal allocation exact", tx["signal_allocations"]["3"] == list(range(44, 52)))
    check("generic scalar packer target-native", "&DAT_00022488 + (param_1 & 0xffff) * 2" in funcs[0x7D1DC]["decompiled_c"])

    print("\n== exact F33 status carrier packers ==")
    s = art["status_carriers"]
    check("351 exact functions", s["0x351"]["producer"] == "0x0004C216" and s["0x351"]["debounce"] == "0x0004C1C0" and s["0x351"]["packer"] == "0x0004CED0")
    check("351 exact packing", "FUN_0007d1dc(0x26,0x22,3,5" in funcs[0x4CED0]["decompiled_c"] and "FUN_0007d1dc(0x27,0x22,1,4" in funcs[0x4CED0]["decompiled_c"])
    check("351 policy remains bounded", "no openpilot temporary/permanent fault mapping" in s["0x351"]["policy_boundary"])
    check("394 exact functions", s["0x394"]["projection"] == "0x0004C24A" and s["0x394"]["packer"] == "0x0004CE08")
    check("394 exact packing", all(tok in funcs[0x4CE08]["decompiled_c"] for tok in (
        "FUN_0007d1dc(0x28,0x25,2,6", "FUN_0007d1dc(0x29,0x25,3,3", "FUN_0007d1dc(0x2a,0x26,3,1", "FUN_0007d1dc(0x2b,0x26,1,0")))
    check("394 policy remains bounded", "not promoted to Ready" in s["0x394"]["policy_boundary"])
    check("4A3 exact functions", s["0x4A3"]["source_preparation"] == "0x0004C000" and s["0x4A3"]["staging"] == "0x0004C14E" and s["0x4A3"]["packer"] == "0x0004C7AA")
    check("4A3 packs signals44..51", "FUN_0007d31e(0x2c,0x27,8,0" in funcs[0x4C7AA]["decompiled_c"] and "FUN_0007d31e(0x33,0x2e,8,0" in funcs[0x4C7AA]["decompiled_c"])
    check("4A3 signed12 angle staging exact", all(tok in funcs[0x4C14E]["decompiled_c"] for tok in ("DAT_febe8048", ">> 8) & 0xf", "DAT_febe7d46", "0x7ff", "0xfffff800")))
    check("4A3 torque staging exact", "DAT_febe66a8" in funcs[0x4C000]["decompiled_c"] and "* 100) / 0x100" in funcs[0x4C000]["decompiled_c"] and "puVar1 + -0x36ae" in funcs[0x4C14E]["decompiled_c"])
    check("4A3 alternate current source exact", "DAT_febe6718" in funcs[0x4C000]["decompiled_c"] and "* -100) / 0x80" in funcs[0x4C000]["decompiled_c"])
    check("4A3 current is not mislabeled DID1151", "GP-0x50E8" in s["0x4A3"]["current_semantic_boundary"] and "GP-0x50F2" in s["0x4A3"]["current_semantic_boundary"])

    print("\n== VAR-056 bounded-census correction ==")
    c = art["census_correction"]
    check("canonical torque census supersedes scratch 4->5 count", c["old_recovered_count"] == 5 and c["new_recovered_count"] == 9 and c["new_read_count"] == 7 and c["new_write_count"] == 2 and c["new_entry"] == "0x0004C490")
    check("updated torque entries exact", c["driver_torque_direct_fixed_gp_entries"] == ["0x00035A06", "0x0004C000", "0x0004C490", "0x0004DB70", "0x00052CA0", "0x00054244", "0x000564CE", "0x00059448", "0x0005D5E0"])
    check("control-cone conclusion unchanged", c["control_cone_conclusion_changed"] is False and "zero direct references inside the cooperative C8xxx-D1xxx" in c["reason"])
    check("alternate-current census distinct", [x["entry"] for x in evid["fixed_gp_census"]["alternate_4a3_current_source_gp_minus_0x50e8"]] == ["0x0004C000", "0x0004C490", "0x00059448", "0x0005D12C"])
    check("DID1151 source census remains distinct", [x["entry"] for x in evid["fixed_gp_census"]["did1151_q_current_source_gp_minus_0x50f2"]] == ["0x0004E394", "0x00052CA0", "0x00054244", "0x000564CE", "0x00059448", "0x0005D12C"])
    check("negative census boundary retained", "computed aliases" in evid["fixed_gp_census"]["boundary"].lower() and "dma" in evid["fixed_gp_census"]["boundary"].lower())

    print("\n== passive opendbc integration boundary ==")
    o = art["passive_opendbc_integration"]
    check("implementation commits pinned", o["nested_opendbc_commit"] == "ab60fd95d8a7b566e10ed1cf59738292f3498932" and o["parent_kai_openpilot_commit"] == "d7d7dfd7e49961e9d35eb7a7681e8756ceee8d04")
    check("exact platform/F181 binding recorded", o["exact_platform"] == "TOYOTA_CAMRY_TSS3" and "byte-exact EPS F181" in o["identity_binding"])
    check("ambiguous legacy fingerprint avoided", "179-ID" in o["can_census"] and "147-ID Corolla" in o["can_census"] and "strict subset" in o["can_census"])
    check("same-car replay coverage recorded", o["carstate_replay"] == ["0x025", "0x030", "0x127 P/R/N/D/B", "0x51E Ready 0/1"])
    check("shadow controller sends zero CAN", "returns zero CAN" in o["controller_boundary"])
    check("Panda production path remains disabled", "ALLOW_DEBUG-only" in o["panda_boundary"] and "0x0B6 is absent" in o["panda_boundary"] and "SafetyModel.noOutput" in o["panda_boundary"])
    check("production output remains unauthorized", o["production_output_authorized"] is False and "steering CAN transmission" in art["boundary"])

    print("\n== exact-F33 default-off development integration ==")
    d = art["gate2_development_integration"]
    check("development implementation commits pinned",
          d["nested_opendbc_commit"] == "dde0fcf0fbaf875750c54a072b0dcb3857f8829b" and
          d["parent_kai_openpilot_commit"] == "15f3550365e2eee54ca5645ae9c24d9d41ae4f31")
    check("development path defaults off and rejects release branches", d["default_enabled"] is False and d["release_branch_allowed"] is False)
    check("development target/topology binding exact", "8965F3307000" in d["target_binding"] and "bus0" in d["target_binding"])
    required = d["runtime_config"]["required_live_fields"]
    check("development config refuses guessed live facts",
          d["runtime_config"]["master_enable"] == "ToyotaTSS3DevLateral" and
          d["runtime_config"]["json"] == "ToyotaTSS3DevLateralConfig" and
          any("b6_template_hex" in x for x in required) and any("cadence_frames" in x for x in required) and
          any("gate2_bypass_validated=true" in x for x in required) and any("exclusive_b6_authority_validated=true" in x for x in required))
    check("development sender keeps exact F33 static bounds", all(tok in d["sender"] for tok in ("ID11", "+/-1745", "+78", "newer stock 0x00F", "zero MAC28")))
    check("development Panda is debug-only B6-only fail-closed", all(tok in d["panda"] for tok in ("ALLOW_DEBUG-only", "0x0B6-only", "0x025", "0x00F", "strict +1", "35-ms")))
    check("development inactive path invents no OEM packet", "no invented inactive B6 frame" in d["inactive_behavior"] and "newer sync epoch" in d["inactive_behavior"])
    check("development does not authorize production", d["production_output_authorized"] is False and "production output remains unsupported" in art["boundary"])

    print("\n== canonical documentation ==")
    report = REPORT.read_text(encoding="utf-8")
    findings = FINDINGS.read_text(encoding="utf-8")
    corrections = CORRECTIONS.read_text(encoding="utf-8")
    priorities = PRIORITIES.read_text(encoding="utf-8")
    for token in ("ab60fd95", "d7d7dfd7e", "dde0fcf0", "15f355036", "0x4C000", "0x4C7AA", "0x4CED0", "0x4CE08", "SafetyModel.noOutput", "179-ID", "147-ID", "ToyotaTSS3DevLateral"):
        check(f"dedicated port report contains {token}", token in report)
    check("VAR-058 registered", "| VAR-058 |" in findings and "8965F3307000" in findings and "ab60fd95" in findings)
    check("VAR-062 development staging registered", "| VAR-062 |" in findings and "dde0fcf0" in findings and "15f355036" in findings)
    check("CORR-120 historical step retained", "### CORR-120" in corrections and "0x4C000" in corrections and "VAR-056" in corrections and "five" in corrections.lower())
    check("CORR-122 canonical census registered", "### CORR-122" in corrections and "6,065" in corrections and "FEBE66A8" in corrections and "FEBE670E" in corrections and "9" in corrections)
    check("priorities record passive baseline plus gated development port", "ab60fd95" in priorities and "dde0fcf0" in priorities and "production output remains disabled" in priorities.lower())

    print(f"\nResults: {p} passed, {f} failed")
    return 1 if f else 0


def section_fault_status() -> int:
    """Verify exact-F33 0x394 DEM/classifier fault-status recovery."""

    import hashlib
    import json
    import subprocess
    import sys
    import tempfile
    from pathlib import Path

    ROOT = Path(__file__).resolve().parents[1]
    IMAGE = ROOT / "firmware/camry-8965F3307000/CodeFlash.bin"
    EVID = ROOT / "data/generated/camry_8965F3307000_fault_status_decompiler_evidence.json"
    ART = ROOT / "data/generated/camry_8965F3307000_fault_status.json"
    BUILD = ROOT / "tools/build_camry_8965F3307000_fault_status.py"
    REPORT = ROOT / "docs/variants/camry-2026-tss3-fault-status.md"
    FINDINGS = ROOT / "docs/status/FINDINGS.md"
    PRIORITIES = ROOT / "docs/status/PRIORITIES.md"

    passed = failed = 0


    def sha(data: bytes) -> str:
        return hashlib.sha256(data).hexdigest()


    def check(name: str, condition: object) -> None:
        nonlocal passed, failed
        ok = bool(condition)
        passed += int(ok)
        failed += int(not ok)
        print(f"[{'PASS' if ok else 'FAIL'}][raw_bytes] {name}")


    img = IMAGE.read_bytes()
    evid = json.loads(EVID.read_text(encoding="utf-8"))
    art = json.loads(ART.read_text(encoding="utf-8"))
    funcs = {int(row["entry"], 16): row for row in evid["functions"]}

    print("== exact target/evidence identity ==")
    check("artifact schema", art["schema"] == "camry-8965f3307000-fault-status-v1")
    check("exact target", art["target"]["software_id"] == "8965F3307000")
    check("image hash", sha(img) == evid["image"]["sha256"] == art["target"]["codeflash_sha256"] == "42dce8efc42f6ae31718e7713fa2d26bb9191b4a82439778aee4d7afded9b0e7")
    check("evidence schema/count", evid["schema"] == "camry-8965f3307000-fault-status-decompiler-evidence-v1" and evid["function_count"] == len(funcs) == 10)
    for entry, row in sorted(funcs.items()):
        check(f"0x{entry:08X} body hash", sha(img[entry:entry + row["body_size"]]) == row["body_sha256"])
    with tempfile.TemporaryDirectory(prefix="camry-f33-fault-status-") as td:
        out = Path(td) / "fault-status.json"
        proc = subprocess.run([sys.executable, str(BUILD), "--out", str(out)], cwd=ROOT, capture_output=True, text=True)
        check("builder exits cleanly", proc.returncode == 0)
        check("builder reproduces artifact byte-exact", out.exists() and out.read_bytes() == ART.read_bytes())

    print("\n== target-native 0x394 classifier ==")
    c = art["classifier"]
    check("classifier entry exact", c["entry"] == "0x000512E4" and c["class_accumulator"] == "0x00050FC8")
    check("state table exact address", c["state_table"] == "0x0002A19C")
    check("state table has 17 rows", len(c["state_table_rows"]) == 17)
    check("state table exact bytes", img[0x2A19C:0x2A19C + 85].hex() == "00000000000403000000040700000005030000000403000000010100000003030201020303020100060303000206030300000307010101030704010106070700010607060001060705000102020000000407000000")
    check("state0 role bounded", "clear/normal" in c["state_roles"]["0"] and "Ready" not in c["state_roles"]["0"])
    check("class states exact", c["state_roles"]["6"].startswith("class-0x02") and c["state_roles"]["10"].startswith("class-0x10") and c["state_roles"]["12"].startswith("class-0x40"))
    check("state16 remains operational inhibit", "inhibit" in c["state_roles"]["16"])

    print("\n== exact wire projection ==")
    w = art["wire"]
    proj = {tuple(row["wire"]): tuple(row["states"]) for row in w["projection_to_state_candidates"]}
    check("0x394 exact carrier", w["can_id"] == "0x394" and w["length"] == 3)
    check("unique state0 projection", proj[(0, 0, 0, 0)] == (0,))
    check("class02 unique projection", proj[(2, 3, 2, 1)] == (6,))
    check("class10 unique projection", proj[(1, 7, 1, 1)] == (10,))
    check("first lossy projection exact", proj[(0, 3, 0, 0)] == (1, 3, 4))
    check("second lossy projection exact", proj[(0, 7, 0, 0)] == (2, 16))
    check("wire boundary is candidate-only", "lossy" in w["boundary"] and "fabricate" in w["boundary"])

    print("\n== target-native aging/calibration ==")
    a = art["aging"]
    check("calibration address exact", a["calibration_address"] == "0x00030E40")
    check("raw calibration words exact", a["raw_u16"] == [200, 200, 600, 22170, 200, 200, 1000])
    check("primary/aggregate/secondary ages exact", (a["primary_latch_bank_355d_age"], a["aggregate_latch_bank_355c_age"], a["class2_class4_secondary_latch_age"]) == (200, 200, 600))
    check("F33 clear-enable age is target-specific", a["primary_clear_enable_age"] == 22170 and a["comparison_to_h"] == {"h_primary_clear_enable_age": 17736, "f33_primary_clear_enable_age": 22170})
    check("aging is not promoted to wall-clock policy", "No wall-clock" in a["boundary"] and "temporary/permanent" in a["boundary"])

    print("\n== target-native DEM/DTC census ==")
    d = art["dem"]
    check("event table geometry exact", d["event_table"] == "0x0002FC50" and d["event_count"] == 0x180 and d["record_size"] == 8)
    check("class histogram exact", d["class_counts"] == {"0x01":8,"0x02":34,"0x04":1,"0x08":1,"0x0F":1,"0x10":171,"0x20":16,"0x40":1,"0x80":7})
    check("240 classified events", sum(d["class_counts"].values()) == 240)
    comp = d["comparison_to_h"]
    check("31 H/F event records differ", comp["changed_record_count"] == 31 and len(comp["changed_records"]) == 31)
    check("only thermal events leave class10", comp["class_removed_events"] == ["0x0085", "0x0088"])
    check("only event0AC loses DTC index", comp["dtc_index_removed_events"] == ["0x00AC"])
    thermal = comp["thermal_dtcs_removed_from_class_0x10"]
    check("thermal A/B DTC names exact", [(x["event"], x["dtc"]["techstream_code"], x["dtc"]["techstream_description"]) for x in thermal] == [
        ("0x0085", "C10051C", 'Control Module Internal Temperature Sensor "B"'),
        ("0x0088", "C10001C", 'Control Module Internal Temperature Sensor "A"'),
    ])
    check("DTC table exact relocation", art["dtc"]["table"] == "0x00030850")
    check("80 referenced DTC rows remain byte-identical", art["dtc"]["referenced_index_count"] == 80 and art["dtc"]["referenced_rows_identical_to_h"] is True)
    check("DTC index120 exact disable", art["dtc"]["index_120_disabled"] == {"h_raw":"8710d10001000000", "f33_raw":"8710d10000000000"})
    check("Techstream join is raw-record based", "identical packed-DTC bytes" in art["dtc"]["vocabulary_join"])

    print("\n== openpilot policy boundary ==")
    op = art["openpilot_policy"]
    check("internal state exposure only", "candidate set" in op["internal_state_exposure"])
    check("state0 is not Ready authorization", "not independently a Ready" in op["state0"])
    check("temporary fault policy unresolved", op["steerFaultTemporary"] == "unresolved policy mapping")
    check("permanent fault policy unresolved", op["steerFaultPermanent"] == "unresolved policy mapping")
    check("production output remains unauthorized", op["production_output_authorized"] is False)
    integ = art["passive_opendbc_integration"]
    check("passive implementation hashes pinned", integ["nested_opendbc_commit"] == "0d5773bd393bbf3d4109728171d2390b60fcde16" and integ["parent_kai_openpilot_commit"] == "191aeb43df3fb72f3264209be1aad57b9ca42e2d")
    check("public fault flags remain unchanged", integ["public_fault_flags_changed"] is False)
    check("full nested gate recorded", "4077 passed / 719 skipped" in integ["full_gate"] and "MISRA" in integ["full_gate"])

    print("\n== documentation integration ==")
    report = REPORT.read_text(encoding="utf-8")
    findings = FINDINGS.read_text(encoding="utf-8")
    priorities = PRIORITIES.read_text(encoding="utf-8")
    for tok in ("0x512E4", "0x2A19C", "0x2FC50", "0x30850", "22,170", "240", "C10051C", "C10001C", "steerFaultTemporary", "steerFaultPermanent"):
        check(f"report contains {tok}", tok in report)
    check("VAR-059 registered", "| VAR-059 |" in findings and "0x512E4" in findings and "240" in findings)
    check("priorities consume F33 fault-status closure", "VAR-059" in priorities and "0x394" in priorities and "asserted/recovery" in priorities)

    print(f"\nResults: {passed} passed, {failed} failed")
    return 1 if failed else 0


def section_secoc_recovery() -> int:
    """Verify retained 8965F3307000 DataFlash/RAM SecOC recovery evidence."""

    import gzip
    import hashlib
    import json
    import subprocess
    import sys
    import tempfile
    from pathlib import Path

    REPO = Path(__file__).resolve().parents[1]
    ROOT = REPO / "targets/camry-2026/raw-20260826/secoc-recovery"
    ART = REPO / "data/generated/camry_8965F3307000_secoc_recovery.json"
    BUILD = REPO / "tools/analyze_camry_8965F3307000_secoc_recovery.py"

    passed = failed = 0


    def check(name: str, condition: object, detail: str = "") -> None:
        nonlocal passed, failed
        ok = bool(condition)
        passed += int(ok)
        failed += int(not ok)
        suffix = f" ({detail})" if detail else ""
        print(f"[{'PASS' if ok else 'FAIL'}][raw_bytes] {name}{suffix}")


    def sha(path: Path) -> str:
        return hashlib.sha256(path.read_bytes()).hexdigest()


    print("== retained source identities ==")
    expected = {
        "dataflash/dump_ff200000_ff208000.bin": (0x8000, "231fbdde4ef317931d8f1ff20ff131650f7d773c124a179b0ae3dc98bf8e4432"),
        "ram/local_ram_pe1.bin": (0x20000, "0ddef478b15bcf3241c56573463eda25ba018081629daf0042fcae1204c435a7"),
        "ram/global_ram.bin": (0x10000, "53c8370237c681d4105c513be5096461ac735ffcb9577995c7203216165006a4"),
        "ram/local_ram_pe1.coverage.bin": (0x8000, "bfa5a24faa8ddf576edcc46f4f05e2459ee4a383b8dc14ff7dba0056b9c59ed0"),
        "ram/global_ram.coverage.bin": (0x4000, "111ce3c2a38d83a2e4706bde4abddd509d7f8248116c6832b06745bdc349e09f"),
        "ram/local_ram_pe1.run.json": (None, "ccd6335b2d6f02dcb4dbd76dcb7f436493e34204dbcea7beec509efa3e326d57"),
        "ram/global_ram.run.json": (None, "0474343a39270fa6dfebd267cbc391ce9b6075c8343beafbf7fb1e6ceed52961"),
        "payloads/payload_dataflash_ff200000_ff208000.bin": (0x1000, "d48988366b5e6d2ddd7438caca5e6f6f02daba9b650263c323a2ffd770a06e34"),
        "payloads/payload_local_ram_pe1_febe0000_fec00000.bin": (0x1000, "fbb1f5bd352c3f0bf416d6b1ef6a7696f97cad2b9f49570ca859207f3269e44f"),
        "payloads/payload_global_ram_feef8000_fef08000.bin": (0x1000, "43d00fdaf790c6deb230d3a4e7b8f8bd17e077a100fa53ebb194532f55c510fd"),
        "camry_ram_dump.py": (None, "ac40975761b1a13ca17cdf85131f69fb968934a75de9a3cfe313a231df87cbfe"),
    }
    for rel, (size, digest) in expected.items():
        path = ROOT / rel
        check(f"{rel} hash", path.is_file() and sha(path) == digest)
        if size is not None:
            check(f"{rel} size", path.stat().st_size == size)

    oracle = ROOT / "can_oracle.ndjson.gz"
    check("oracle compressed identity", sha(oracle) == "e977f5f0dc3d86786af8ae576d785af46c8facc8e186c4598f692a38ecb95b73")
    with gzip.open(oracle, "rb") as stream:
        raw_oracle = stream.read()
    check("oracle uncompressed identity", len(raw_oracle) == 37552829 and hashlib.sha256(raw_oracle).hexdigest() == "823622ed360ee1b2c2c156c6196a17d001c845f4d53fbc56922a338a4a46e33c")

    print("\n== deterministic artifact regeneration ==")
    with tempfile.TemporaryDirectory() as td:
        out = Path(td) / "camry_secoc.json"
        proc = subprocess.run([sys.executable, str(BUILD), "--out", str(out)], cwd=REPO, capture_output=True, text=True, check=False)
        check("recovery analyzer succeeds", proc.returncode == 0, proc.stderr[-300:])
        check("recovery artifact regenerates exactly", proc.returncode == 0 and out.read_bytes() == ART.read_bytes())

    art = json.loads(ART.read_text())
    check("artifact schema exact", art["schema"] == "camry-8965f3307000-secoc-recovery-v1")
    check("artifact exact F33 route", art["target"]["f181"] == "8965F3307000" and art["target"]["secondary_identity"] == "8A3113303100" and art["target"]["diagnostic_route"] == {"bus": 1, "elm327_param": 1, "rx": "0x7A9", "tx": "0x7A1"})

    print("\n== DataFlash object-15 disposition ==")
    obj15 = art["dataflash"]["object15"]
    check("object15 has zero valid copies", obj15["valid_copy_count"] == 0 and not obj15["valid_consensus"])
    check("object15 triplicate geometry exact", obj15["copy_addresses"] == ["0xFF206E00", "0xFF206D00", "0xFF206C00"])
    check("object15 key-field geometry exact", obj15["key_field_addresses"] == ["0xFF206E14", "0xFF206D14", "0xFF206C14"])
    check("all object15 key fields are raw zero", obj15["key_fields_zero"] == [True, True, True])

    df = (ROOT / "dataflash/dump_ff200000_ff208000.bin").read_bytes()
    for off in (0x6E14, 0x6D14, 0x6C14):
        check(f"DataFlash +0x{off:04X} raw zero16", df[off:off + 16] == bytes(16))

    print("\n== RAM acquisition and legacy-table rejection ==")
    local = art["local_ram_pe1"]
    global_ram = art["global_ram"]
    for name, node, expected_words in (("local", local, 32768), ("global", global_ram, 16384)):
        acq = node["acquisition"]
        check(f"{name} RAM acquisition complete", acq["status"] == "complete" and acq["coverage_percent"] == 100.0 and acq["unique_words"] == acq["expected_words"] == expected_words)
        check(f"{name} RAM acquisition clean", acq["duplicate_words"] == 0 and acq["conflicts"] == 0 and acq["spi_errors"] == 0 and acq["coverage"]["all_words_covered"])
        check(f"{name} RAM exact target guard", acq["application_f181_exact"] and acq["boot_f181_exact"] and acq["nrt_ready_values"] == [0])
        check(f"{name} RAM exact old-stack bootstrap", acq["old_stack_zero_dids"] and acq["verify_10f0_accepted"] and acq["ff00_sent"])
    check("PE1 acquisition clobber is explicit", local["clobber_range"] == ["0xFEBF0000", "0xFEBF1000"] and local["acquisition"]["clobber_range"] == ["0xfebf0000", "0xfebf1000"])
    check("application-SA root mirrors once at FEBF7B80", local["app_sa_root_hits"] == ["0xFEBF7B80"])
    check("payload/boot roots are not raw LocalRAM values", local["payload_build_root_hits"] == [] and local["boot_sa_root_hits"] == [])
    check("payload/boot/application roots absent from GlobalRAM", global_ram["app_sa_root_hits"] == [] and global_ram["payload_build_root_hits"] == [] and global_ram["boot_sa_root_hits"] == [])
    legacy = local["legacy_key_table"]
    check("legacy FEBE6E34 layout has 14 records and zero valid checksums", legacy["record_count"] == 14 and legacy["valid_checksum_count"] == 0 and all(not row["checksum_valid"] for row in legacy["records"]))
    check("legacy would-be KEY_1 field is zero", legacy["old_extractor_key_1"]["key_field_address"] == "0xFEBE6E60" and legacy["old_extractor_key_1"]["key_field_zero"])
    check("legacy would-be KEY_4 record is checksum-invalid", legacy["old_extractor_key_4"]["key_field_address"] == "0xFEBE6EC0" and not legacy["old_extractor_key_4"]["checksum_valid"])
    check("legacy FEBF42E0 factory record is zero", legacy["old_factory_record_0xFEBF42E0_zero"])

    print("\n== CAN oracle and retained exhaustive matcher result ==")
    oracle_art = art["oracle"]
    focus = oracle_art["focus_bus1_streams"]
    check("oracle is about 60 s", 59000 < oracle_art["duration_ms"] < 61000)
    check("native sync 0x00F retained", focus["0x00F"] == {"count": 618, "length_counts": {"8": 618}})
    check("native FD 0x0D7 retained", focus["0x0D7"] == {"count": 3095, "length_counts": {"32": 3095}})
    check("native FD 0x090 retained", focus["0x090"] == {"count": 6190, "length_counts": {"32": 6190}})
    check("B6 absent only in this stationary oracle", focus["0x0B6"]["count"] == 0)
    scan = art["offline_key_scan"]
    check("matcher provenance exact", scan["matcher"]["repository"] == "kai-openpilot" and scan["matcher"]["commit"] == "2bfbef37fddbdf4e499a4adc55005474f3c5ffcf")
    check("matcher oracle sample set exact", scan["oracle"]["sync_samples"] == 208 and scan["oracle"]["protected_samples"] == 813 and scan["oracle"]["malformed"] == 0)
    expected_scans = {
        "dataflash": (32753, 32753),
        "local_ram_pe1": (131057, 126946),
        "global_ram": (65521, 65521),
    }
    for name, (windows, eligible) in expected_scans.items():
        row = scan["scans"][name]
        check(f"{name} scan exhausted every eligible window", row["status"] == "not_found" and row["windows_scanned"] == windows and row["windows_eligible"] == eligible and row["survivors"] == 0 and row["matches"] == 0)
        check(f"{name} scan saw the full capped oracle", row["sync"] == "0/208" and row["protected"] == "0/813")
    check("LocalRAM matcher excluded the payload span", scan["scans"]["local_ram_pe1"]["excluded_clobber"] == ["0xFEBF0000", "0xFEBF1000"] and scan["scans"]["local_ram_pe1"]["coverage_known"])

    print("\n== documentation ==")
    doc = (REPO / "docs/variants/camry-2026-live-baseline.md").read_text()
    findings = (REPO / "docs/status/FINDINGS.md").read_text()
    readme = (REPO / "targets/camry-2026/README.md").read_text()
    for token in ("231fbdde4ef31793", "0xFF206E14", "0xFEBF7B80", "126,946", "65,521"):
        check(f"canonical report contains {token}", token in doc)
    check("VAR-055 retained", "| VAR-055 |" in findings and "8965F3307000" in findings)
    check("community README points to SecOC recovery evidence", "secoc-recovery" in readme and "LocalRAM" in readme and "GlobalRAM" in readme)

    print(f"\nResults: {passed} passed, {failed} failed")
    return 1 if failed else 0


def section_command5_runtime_carrier() -> int:
    """Verify the exact-F33 static command-5 runtime carrier and audited candidates."""
    import hashlib, json, struct, subprocess, sys, tempfile
    from pathlib import Path
    ROOT=Path(__file__).resolve().parents[1]
    ART=ROOT/'data/generated/camry_8965F3307000_command5_runtime_carrier.json'
    BUILD=ROOT/'tools/build_camry_8965F3307000_command5_runtime_carrier.py'
    IMAGE=ROOT/'firmware/camry-8965F3307000/CodeFlash.bin'
    RUNTIME_BUILDER=ROOT/'exploit/ephemeral_runtime/build_camry_f33_command5_carrier.py'
    PROXY_AUDIT=ROOT/'exploit/ephemeral_runtime/audited_camry_f33_command5_proxy_build.json'
    CANARY_AUDIT=ROOT/'exploit/ephemeral_runtime/audited_camry_f33_runtime_canary_build.json'
    PROXY_BIN=ROOT/'exploit/ephemeral_runtime/audited/camry_f33_command5_proxy.bin'
    CANARY_BIN=ROOT/'exploit/ephemeral_runtime/audited/camry_f33_runtime_canary.bin'
    PROXY_SOURCE=ROOT/'exploit/ephemeral_runtime/corolla_hf_command5_proxy.c'
    CANARY_SOURCE=ROOT/'exploit/ephemeral_runtime/corolla_hf_canary.c'
    RAMREQ=ROOT/'data/variant_ram_exec_requirements.json'
    p=f=0
    def sha(b:bytes)->str:return hashlib.sha256(b).hexdigest()
    def check(name:str,cond:object)->None:
     nonlocal p, f; ok=bool(cond); p+=int(ok); f+=int(not ok); print(f"[{'PASS' if ok else 'FAIL'}] {name}")
    a=json.loads(ART.read_text()); img=IMAGE.read_bytes(); pa=json.loads(PROXY_AUDIT.read_text()); ca=json.loads(CANARY_AUDIT.read_text())
    print('== deterministic target binding ==')
    check('schema/scope exact',a['schema']=='camry-8965f3307000-command5-runtime-carrier-v1' and a['applies_to']==['8965F3307000'])
    check('exact image pinned',a['sources']['codeflash']['sha256']==sha(img)=='42dce8efc42f6ae31718e7713fa2d26bb9191b4a82439778aee4d7afded9b0e7')
    check('identity/route exact',a['identity']['application_records']==['8965F3307000','8A3113303100'] and a['identity']['route']=={'tx':'0x7A1','rx':'0x7A9','bus':1,'elm327_param':1,'uds_variant':'old','cpu_index':0})
    with tempfile.TemporaryDirectory(prefix='f33-runtime-') as td:
     out=Path(td)/'a.json'; r=subprocess.run([sys.executable,str(BUILD),'--out',str(out)],cwd=ROOT,capture_output=True,text=True)
     check('builder exits cleanly',r.returncode==0)
     check('builder reproduces artifact byte-exact',out.exists() and out.read_bytes()==ART.read_bytes())
    for name,row in a['sources']['raw_function_ranges'].items():
     off=int(row['address'],16); n=row['size']; check(f'{name} raw range hash',sha(img[off:off+n])==row['sha256'])
    print('\n== bootstrap / startup / scheduler ==')
    b=a['bootstrap_contract']; s=a['scheduler_transfer']
    check('bootstrap stays RAM-only old-stack',b['download_base']==b['callback_base']=='0xFEBF0000' and b['download_size']==0x1000 and b['verify_routine']=='0x10F0' and b['callback_routine']=='0xFF00' and b['did_0203']=='0000000000' and b['did_0201']==b['did_0202']=='00'*16)
    check('artifact does not expose secret values',b['secret_values_recorded_in_artifact'] is False)
    check('boot transition exact',s['boot_transition_calls']==['0x00000C9A','0x00000E54','0x00000F80','0x000010C6'] and s['boot_validity_check']=='0x0000119E')
    check('context/startup exact',s['application_context_init']=='0x000715B4' and s['startup_jarl_first']=='0x000637F6' and s['startup_jarl_after']=='0x0006384A' and s['startup_jarl_count']==21 and s['startup_final_init']=='0x000701EA')
    check('foreground exact',s['foreground_loop']=='0x00066062' and s['tick_poll']=={'address':'0xFFFFB111','bit':4,'clear_mask':'0xEF'} and s['foreground_tick_counter']=='0xFEBE39DB')
    check('foreground context wrappers exact',s['foreground_calls']==['0x00065442','0x00071378','0x00066FF2','0x00071398','0x000667E6','0x00071378','0x00066CF6','0x00071398'])
    print('\n== static-low versus verified-high carrier geometry ==')
    g=a['static_low_carrier_geometry']; h=a['verified_high_tail_carrier']; m=a['mailbox_geometry']
    check('historical low pocket stays exact but is explicitly disproved live',g['base']=='0xFEBF0000' and g['end_inclusive']=='0xFEBF0307' and g['end_exclusive']=='0xFEBF0308' and g['size']==776 and g['first_recovered_normalized_direct_or_simple_gp_reference']=='0xFEBF0308' and 'not a retained production carrier' in g['static_boundary'])
    check('low pocket region5 static MPU geometry remains exact',g['mpu_region_index']==5 and g['mpu_bounds']==['0xFEBEF400','0xFEBF33FC'] and g['ctx0_mpat']==g['ctx1_mpat']=='0x000000B8')
    check('high tail is live retained/executable exact 524-byte carrier',h['base']=='0xFEBFF9F0' and h['end_inclusive']=='0xFEBFFBFB' and h['end_exclusive']=='0xFEBFFBFC' and h['size']==524 and h['retained_sha256']=='89ffed31c24e746a57171e6f3e22f99d1e78d57b63bccb8778c7fe715d18800c' and h['live_exact_after_stock_startup'] and h['live_execution_proven'] and h['stock_application_reappeared'] and h['safety_tx_blocked_delta']==0)
    check('high tail region1 MPU geometry exact',h['mpu_region_index']==1 and h['mpu_bounds']==['0xFEBF7C00','0xFEBFFBFC'] and h['ctx0_mpat']=='0x000000B8' and h['ctx1_mpat']=='0x000000A8')
    check('historical mailbox exact 60-byte span',m['base']=='0xFEBFFB80' and m['end_inclusive']=='0xFEBFFBBB' and m['end_exclusive']=='0xFEBFFBBC' and m['size']==60 and m['normalized_direct_or_simple_gp_reference_count']==0 and m['historical_only'] is True)
    check('mailbox region1 ctx0 writable / ctx1 nonwrite',m['mpu_region_index']==1 and m['mpu_bounds']==['0xFEBF7C00','0xFEBFFBFC'] and m['ctx0_mpat']=='0x000000B8' and m['ctx1_mpat']=='0x000000A8' and 'ctx0' in m['intended_write_context'] and '0x71398' in m['intended_write_context'])
    words=struct.unpack_from('<64I',img,0x31688)
    check('raw MPU table exact region1/5', (words[2],words[3],words[10],words[11])==(0xFEBF7C00,0xFEBFFBFC,0xFEBEF400,0xFEBF33FC) and words[33]==0xB8 and words[49]==0xA8 and words[37]==words[53]==0xB8)
    print('\n== command5 route ==')
    c=a['command5_contract']
    check('record0 adapter/worker/callback exact',c['driver_record_table']=='0x00027DA4' and c['driver_record']==0 and c['adapter']=='0x00088DBC' and c['worker']=='0x00088EC0' and c['completion_callback']=='0x00089C4C')
    check('dispatcher/lower exact',c['dispatcher']=='0x00089440' and c['lower_engine']=='0x0008A720' and c['key_selector']==4 and c['fixed_input_length']==36 and c['output_length']==16)
    check('completion cells exact',c['done_flag']=='0xFEBF13BC' and c['status_flag']=='0xFEBF13BD' and c['serialized_with_command7'] is True)
    check('raw driver record exact',struct.unpack_from('<8I',img,0x27DA4)==(0xFFFF0000,0x89C4C,0,0,0,0x88DBC,0x88EC0,0x27DA0))
    print('\n== audited executable candidates ==')
    can=a['runtime_candidates']['inert_canary']; prox=a['runtime_candidates']['fixed_36_command5_proxy']
    check('canary exact audited build',can['size']==CANARY_BIN.stat().st_size==334 and can['headroom']==442 and can['sha256']==sha(CANARY_BIN.read_bytes())=='facd4f590581f7422dab0fc4fcea21f6d73e4c361b1f4d54960d7001e89bdbb0' and can['entry_offset']==can['relocations']==0 and can['command5_calls'] is False and can['production_poststartup_usable'] is False)
    check('proxy exact audited build',prox['size']==PROXY_BIN.stat().st_size==464 and prox['headroom']==312 and prox['sha256']==sha(PROXY_BIN.read_bytes())=='0ea9b9d460c3678ad4341817ae606d720bb2a13f4d14ec7dc1e0c8f569db94d3' and prox['entry_offset']==prox['relocations']==0 and prox['input_length']==36 and prox['key_selector']==4 and prox['production_poststartup_usable'] is False)
    for label,audit,source,binary in [('proxy',pa,PROXY_SOURCE,PROXY_BIN),('canary',ca,CANARY_SOURCE,CANARY_BIN)]:
     check(f'{label} audit source bound',audit['source']['sha256']==sha(source.read_bytes()))
     check(f'{label} audit builder bound',audit['builder']['sha256']==sha(RUNTIME_BUILDER.read_bytes()))
     check(f'{label} compiler equivalence',audit['toolchain']['reproduced_byte_exact'] is True and audit['toolchain']['reference_sha256']=='273202dc591810b2f587ab8fac044599b57b4e07a24ff61d36b7131b97c00660')
     check(f'{label} audit binary bound',audit['shellcode']['sha256']==sha(binary.read_bytes()) and audit['compile_contract']['entry_offset']==0 and audit['compile_contract']['relocations']==0)
    check('proxy source is fixed-36 and busy-retry', '36u' in PROXY_SOURCE.read_text() and 'else if (rc != 2)' in PROXY_SOURCE.read_text())
    check('canary source has no command5 dispatch', 'TARGET_COMMAND5_DISPATCH' not in CANARY_SOURCE.read_text() and 'TARGET_CANARY_HEARTBEAT' in CANARY_SOURCE.read_text())
    print('\n== dynamic boundary ==')
    z=a['boundary']; variants={str(x.get('id','')).lower() for x in json.loads(RAMREQ.read_text())['variants']}
    check('low static carrier is superseded by verified high tail',z['static_low_carrier_candidate_closed'] and z['low_carrier_disproved'] and not z['low_carrier_live_retention_closed'] and z['verified_high_tail_live_retention_closed'])
    check('Camry high-tail geometry is promoted',z['verified_variant_ram_exec_requirement_promoted'] and 'camry-2026-8965f3307000-high-tail' in variants)
    check('slot4/latency/application pivot remain open',not z['live_slot4_command5_permission_closed'] and not z['command5_latency_jitter_closed'] and not z['application_mode_execution_pivot_closed'])
    check('no flash write/steering tx/actuation authorized',not z['flash_write_used'] and not z['steering_can_transmit_used'] and not z['production_b6_signer_closed'] and not z['vehicle_actuation_authorized'])
    check('historical sequence records low-pocket failure then high-tail closure',[x['stage'] for x in a['historical_low_carrier_live_sequence']]==[1,2] and 'disproved' in a['historical_low_carrier_live_sequence'][0]['result'] and 'closed' in a['historical_low_carrier_live_sequence'][1]['result'])
    print(f'\nResults: {p} passed, {f} failed')
    return 1 if f else 0


def section_application_ram_loader() -> int:
    """Verify the exact-F33 non-persistent application-mode RAM-loader assessment."""

    import hashlib
    import json
    import struct
    import subprocess
    import sys
    import tempfile
    from pathlib import Path

    ROOT = Path(__file__).resolve().parents[1]
    ART = ROOT / "data/generated/camry_8965F3307000_application_ram_loader_assessment.json"
    BUILD = ROOT / "tools/build_camry_8965F3307000_application_ram_loader_assessment.py"
    IMAGE = ROOT / "firmware/camry-8965F3307000/CodeFlash.bin"
    RAW = ROOT / "targets/camry-2026/raw-20260826"
    RAMREQ = ROOT / "data/variant_ram_exec_requirements.json"

    passed = failed = 0


    def sha(data: bytes) -> str:
        return hashlib.sha256(data).hexdigest()


    def check(name: str, condition: object, detail: str = "") -> None:
        nonlocal passed, failed
        ok = bool(condition)
        passed += int(ok)
        failed += int(not ok)
        suffix = f" ({detail})" if detail else ""
        print(f"[{'PASS' if ok else 'FAIL'}] {name}{suffix}")


    def find_ldsr_writers(image: bytes, system_register: int, selector: int) -> list[tuple[int,int,bytes]]:
        out=[]
        for off in range(0,len(image)-3,2):
            word=struct.unpack_from("<I",image,off)[0]
            if (((word >> 5) & 0x3F) == 0x3F and
                ((word >> 11) & 0x1F) == system_register and
                ((word >> 16) & 0x7FF) == 0x20 and
                ((word >> 27) & 0x1F) == selector):
                out.append((off,word & 0x1F,image[off:off+4]))
        return out


    a = json.loads(ART.read_text())
    img = IMAGE.read_bytes()
    print("== deterministic target/evidence binding ==")
    check("assessment schema exact", a["schema"] == "camry-8965f3307000-application-ram-loader-assessment-v1")
    check("exact F33 image pinned", len(img) == 0x100000 and sha(img) == a["target"]["codeflash_sha256"] == "42dce8efc42f6ae31718e7713fa2d26bb9191b4a82439778aee4d7afded9b0e7")
    with tempfile.TemporaryDirectory(prefix="f33-app-loader-") as td:
        out = Path(td) / "assessment.json"
        r = subprocess.run([sys.executable, str(BUILD), "--out", str(out)], cwd=ROOT, capture_output=True, text=True)
        check("builder exits cleanly", r.returncode == 0, r.stderr.strip())
        check("builder reproduces tracked artifact byte-exact", out.exists() and out.read_bytes() == ART.read_bytes())
    for name, digest in a["live_runtime_carrier"]["source_files"].items():
        check(f"live evidence hash pinned: {name}", sha((RAW / name).read_bytes()) == digest)

    print("\n== live carrier correction ==")
    h = a["live_runtime_carrier"]
    check("high tail is exact 524-byte retained executable carrier", h["base"] == "0xFEBFF9F0" and h["end_inclusive"] == "0xFEBFFBFB" and h["size"] == 524 and h["retained_sha256"] == "89ffed31c24e746a57171e6f3e22f99d1e78d57b63bccb8778c7fe715d18800c" and h["exact_after_stock_startup"] and h["executed_live"])
    check("stock application returned with no Panda TX block delta", h["stock_application_reappeared"] and h["safety_tx_blocked_delta"] == 0)
    check("low FEBF0000 carrier is rejected", h["low_febf0000_carrier_rejected"] is True)
    check("failed poststartup canary is preserved as a negative probe", "negative/no application reappearance" in h["poststartup_direct_canary_result"])

    print("\n== application XCP arbitrary writer ==")
    x = a["application_xcp"]
    check("packed request descriptors are exact", x["request_can_id"] == "0x7F7" and x["packed_descriptor_hits"]["request"] == ["0x021F50", "0x023398"] and struct.unpack_from("<I", img, 0x21F50)[0] == 0x9FDC0002 and struct.unpack_from("<I", img, 0x23398)[0] == 0x9FDC0002)
    check("packed response descriptor is exact", x["response_can_id"] == "0x7F8" and x["packed_descriptor_hits"]["response"] == ["0x021F48"] and struct.unpack_from("<I", img, 0x21F48)[0] == 0x9FE00002)
    opmap = img[0x22B24:0x22B24 + 41]
    callbacks = [struct.unpack_from("<I", img, 0x22B50 + 4*i)[0] for i in range(18)]
    check("GET_SEED/UNLOCK are unconfigured", x["get_seed_configured"] is False and x["unlock_configured"] is False and opmap[0xFF-0xF8] == 0 and opmap[0xFF-0xF7] == 0)
    check("SET_MTA maps to exact F33 callback", x["set_mta"] == "0x00082C62" and callbacks[opmap[0xFF-0xF6]] == 0x82C62)
    check("DOWNLOAD maps to exact F33 callback", x["download"] == "0x00081FFE" and callbacks[opmap[0xFF-0xF0]] == 0x81FFE)
    check("MODIFY_BITS/SHORT_UPLOAD remain configured", x["modify_bits"] == "0x000820C4" and x["short_upload"] == "0x00082B1A" and callbacks[opmap[0xFF-0xEC]] == 0x820C4 and callbacks[opmap[0xFF-0xF4]] == 0x82B1A)
    expected_daq={"0xE3":"0x00082880","0xE2":"0x000824B8","0xE1":"0x00082510","0xE0":"0x00082616","0xDE":"0x000826D6","0xDD":"0x000827B4","0xDA":"0x0008295C","0xD9":"0x0008299A","0xD8":"0x00082910","0xD7":"0x000829CE"}
    check("full configured XCP DAQ bank is exact", x["configured_daq_commands"] == expected_daq and all(callbacks[opmap[0xFF-int(cmd,16)]] == int(target,16) for cmd,target in expected_daq.items()))
    check("XCP DAQ is measurement-only, not a PC/write pivot", x["daq_boundary"]["write_daq"] == "0x00082510" and x["daq_boundary"]["odt_reader"] == "0x00082368" and x["daq_boundary"]["odt_state_inside_xcp_write_window"] is False and x["daq_boundary"]["tester_selected_address_use"] == "read one measurement byte into DTO staging" and x["daq_boundary"]["stim_or_direction_mode_recovered"] is False)
    for cmd in (0xF9,0xF5,0xF3,0xF2,0xF1,0xEF,0xEE,0xED,0xDC,0xDB):
        check(f"standard XCP command 0x{cmd:02X} remains unmapped", opmap[0xFF-cmd] == 0)
    check("software write window exactly covers high tail", x["software_write_window"] == ["0xFEBF7C00", "0xFEBFFBFF"] and struct.unpack_from("<II", img, 0x2B21C) == (0xFEBF7C00, 0xFEBFFBFF) and x["high_tail_fully_inside_write_window"])
    route=x["physical_route"]
    check("XCP RX rule is exact RSCFD controller-1 rule 46", route["rscfd_controller"] == 1 and route["rx"]["rule_index"] == 46 and route["rx"]["controller_span"] == {"start_index":0,"count":47} and route["rx"]["rule"] == "0x00023398" and struct.unpack_from("<I",img,0x23398)[0] == 0x9FDC0002)
    check("XCP TX handle 0x37 independently maps to controller1/resource8", route["tx"]["family"] == 5 and route["tx"]["software_route_index"] == 4 and route["tx"]["hardware_tx_handle"] == "0x0037" and route["tx"]["resource"] == 8 and struct.unpack_from("<I",img,0x22E38)[0] == 0x22DB8 and img[0x22E26:0x22E28] == bytes((1,8)))
    check("XCP wire contract is classic standard CAN DLC8", route["can_format"] == "classic standard CAN" and route["frame_size"] == 8 and (struct.unpack_from("<I",img,0x23398)[0] & 0x40000000) == 0 and img[0x22ABD] == 8)
    act=x["transport_activation"]
    check("XCP activation uses exact owner/transport state cells", act["transport_state"] == "0xFEBE4EE6" and act["disabled_value"] == "0x69" and act["enabled_value"] == "0x5A" and act["owner_active_state"] == "0xFEBE491B" and act["owner_online_event_state"] == "0xFEBE4919" and act["configured_source_mask"] == "0x10")
    check("XCP owner delay is three exact 5ms foreground ticks", act["configured_delay_foreground_ticks"] == 3 and act["foreground_tick_ms"] == 5.0 and act["configured_delay_ms"] == 15.0 and struct.unpack_from("<H",img,0x21B8C)[0] == 3)
    check("normal bus1/ELM1 timeout is reclassified on the proven correct route", x["normal_route_live_result"]["status"] == "correct_route_no_response_timeout" and x["normal_route_live_result"]["tested_bus"] == 1 and x["normal_route_live_result"]["elm327_param"] == 1 and x["normal_route_live_result"]["panda_tx_block_counter_recorded"] is False and "statically proven correct" in x["reachability_boundary"])
    check("read-only state preflight is the next XCP discriminator", act["read_only_preflight"] == "exploit/followups/xcp_runtime_state_probe.py" and any("SID 0x23" in row for row in a["minimum_next_observations"]))

    print("\n== calibration-page shadow is not an execution overlay ==")
    cx = a["custom_xcp"]
    raw = a["raw_range_evidence"]
    check("custom paging selectors carry standard calibration-page roles", cx["semantic_roles"] == {"0xE4":"COPY_CAL_PAGE","0xEA":"GET_CAL_PAGE","0xEB":"SET_CAL_PAGE","0xF3":"BUILD_CHECKSUM"} and cx["calibration_page_state"] == ["0xFEBE5EC4","0xFEBE5EC5"] and cx["page_translator"] == "0x000991D2")
    check("startup and XCP copy loops are byte-identical", cx["startup_copy"]["callsite"] == "0x00063822" and cx["startup_copy"]["same_copy_loop_as_xcp"] is True and img[0x636D4:0x636F8] == img[0x993F0:0x99414] and img[0x63822:0x63826] == bytes.fromhex("bfffb2fe"))
    check("calibration source/shadow geometry is exact", cx["e4_copy"]["source"] == ["0x00010000","0x00017DEF"] and cx["e4_copy"]["destination"] == ["0xFEBF7C00","0xFEBFF9EF"] and sha(img[0x10000:0x17DF0]) == cx["calibration_shadow_classification"]["source_sha256"] == "675e9f5f360277c6eb27ef73bb021e40861a88d99dd283adb2d7062506d246b6" and cx["residual_tail_starts_exactly_after_e4_copy"])
    check("recovered calibration shadow has no code-flow consumer", cx["calibration_shadow_classification"]["recovered_function_entries_in_source_range"] == 0 and cx["calibration_shadow_classification"]["recovered_function_owned_flow_edges_into_source_range"] == 0 and cx["calibration_shadow_classification"]["recovered_flow_edges_into_ram_shadow"] == 0 and cx["calibration_shadow_classification"]["page_state_application_consumers_recovered"] == 0 and cx["calibration_shadow_classification"]["instruction_fetch_or_branch_remap_recovered"] is False)
    for name,row in raw.items():
        base=int(row["address"],16); size=row["size"]
        check(f"raw evidence range pinned: {name}", sha(img[base:base+size]) == row["sha256"])

    print("\n== ordinary application UDS negatives ==")
    u = a["application_uds"]
    check("SID 0x3D WriteMemoryByAddress is absent", u["write_memory_by_address_0x3d_configured"] is False and "0x3D" not in u["configured_sids"])
    check("SID 0x23 is read-only application RMBA surface", u["read_memory_by_address"] == {"sid":"0x23","callback":"0x000965C0","sessions":[3]})
    check("SID 0x2E is DID-bounded rather than arbitrary memory writer", u["write_data_by_identifier"]["callback"] == "0x00095978" and u["write_data_by_identifier"]["arbitrary_memory_writer"] is False)
    for sid, key in [(0x34,"request_download"),(0x36,"transfer_data"),(0x37,"request_transfer_exit")]:
        row = u[key]
        check(f"SID 0x{sid:02X} has no application transfer callback and requires session 2", row["callback"] is None and row["sessions"] == [2] and row[[k for k in row if k.endswith("context_recovered")][0]] is False)
    check("programming session remains the disruptive handoff", u["programming_session_is_disruptive_handoff"] is True)
    reset=u["ecu_reset"]
    check("application ECUReset has no worker or subfunction path", reset == {"sid":"0x11","callback":None,"sessions":[2],"has_subfunctions":False,"subfunction_count":0,"application_reset_action_recovered":False,"verdict":"no application ECUReset worker exists to compose with the retained tail"} and img[0x25C6C:0x25C84] == bytes.fromhex("0000000000000000bc590200000000001100000100000000"))

    print("\n== application diagnostic pivot exhaustion ==")
    dp=a["application_diagnostic_pivot_audit"]
    ab=dp["sid_ab"]
    raw_ab=[]
    for i in range(3):
        off=0x25AFC+i*0x10
        raw_ab.append((img[off+0xC],struct.unpack_from("<I",img,off)[0],struct.unpack_from("<I",img,off+8)[0]))
    check("SID AB has three fixed selector callbacks", raw_ab == [(1,0x9874A,0x259A4),(2,0x9876C,0x259A6),(3,0x9878E,0x259A8)] and [(r["selector"],r["callback"],r["policy"]) for r in ab["selectors"]] == [("0x01","0x0009874A","0x000259A4"),("0x02","0x0009876C","0x000259A6"),("0x03","0x0009878E","0x000259A8")])
    ab_events=[(struct.unpack_from("<I",img,0x2AB70+i*8)[0],img[0x2AB70+i*8+4],img[0x2AB70+i*8+5]) for i in range(64)]
    pop=[(i,row) for i,row in enumerate(ab_events) if row[0]]
    check("SID AB event catalogue is IDs/types, not an address table", len(pop) == 51 and [i for i,_ in pop] == list(range(1,52)) and {row[1] for _,row in pop} == {0x11,0x22,0x33,0x44,0x55} and ab["request_derived_indirect_pc_target_recovered"] is False and ab["request_state_inside_xcp_write_window"] is False)
    ba=dp["sid_ba"]
    raw_ba=[]
    for i in range(struct.unpack_from("<I",img,0x27EC0)[0]):
        off=0x27EC4+i*0x10
        raw_ba.append((img[off],img[off+1],struct.unpack_from("<I",img,off+8)[0],struct.unpack_from("<I",img,off+12)[0]))
    check("SID BA ten-operation table is fixed CodeFlash dispatch", len(raw_ba) == ba["operation_count"] == 10 and all(0 < x < len(img) for row in raw_ba for x in row[2:]) and ba["all_callbacks_fixed_codeflash"] and ba["request_derived_indirect_pc_target_recovered"] is False and ba["request_copy_cap_bytes"] == 64)
    rc=dp["routine_control"]
    raw_routines=[struct.unpack_from("<III",img,0x256DC+i*12) for i in range(19)]
    check("all 19 RoutineControl rows use fixed CodeFlash callbacks", len(raw_routines) == rc["row_count"] == 19 and raw_routines[8] == (0x100F,0x8B858,0x8B872) and raw_routines[9] == (0x1010,0,0) and all((pre==0 or pre < len(img)) and (act==0 or act < len(img)) for _,pre,act in raw_routines) and rc["request_derived_indirect_pc_target_recovered"] is False)
    w=dp["wdbi"]
    raw_wdbi=[]
    for i in range(13):
        off=0x25640+i*12
        did,flags=struct.unpack_from("<HH",img,off); raw_wdbi.append((did,flags,struct.unpack_from("<I",img,off+4)[0],struct.unpack_from("<I",img,off+8)[0]))
    check("WDBI exact DID set is fixed-callback maintenance only", [r[0] for r in raw_wdbi] == [0x0204,0x2001,0x2002,0x2005,0x2006,0x2007,0x2008,0x2009,0x200D,0x2010,0x2012,0x2013,0x2014] and all(r[1] == 0 and 0 < r[2] < len(img) and 0 < r[3] < len(img) for r in raw_wdbi) and w["all_callbacks_fixed_codeflash"] and w["payload_interpreted_as_address"] is False and w["request_derived_indirect_pc_target_recovered"] is False and w["internal_payload_stage_cap_bytes"] == 8)
    check("diagnostic pivot audit closes recovered write/proprietary/reset classes", all(dp[k]["request_derived_indirect_pc_target_recovered"] is False for k in ("sid_ab","sid_ba","routine_control","wdbi")) and dp["ecu_reset"]["application_reset_action_recovered"] is False)

    print("\n== stock command-5 routine ==")
    c = a["stock_command5_routine"]
    check("RID 0x100F exact table/callback chain", c["rid"] == "0x100F" and c["routine_table"] == "0x00026918" and c["callback_table"] == "0x000256DC" and c["precondition"] == "0x0008B858" and c["action"] == "0x0008B872" and c["chain"] == ["0x0008B872","0x0006A0AE","0x00069C58","0x00069BD8","0x00089440"])
    check("RID 0x100F is fixed-16/private-result not direct SecOC signing API", c["input_length"] == 16 and c["input"] == "0xFEBE5186" and c["output"] == "0xFEBE51B6" and c["output_exposed_to_tester"] is False and c["xcp_can_rewrite_input_or_output"] is False)

    print("\n== control-transfer boundary ==")
    ct = a["control_transfer_audit"]
    raw_indirect = ct["raw_indirect_control_transfer_census"]
    check("current first-class indirect-transfer census is 496 total / 487 application",
          raw_indirect["total"] == 496 and raw_indirect["application"] == 487 and
          raw_indirect["mnemonics_total"] == {"jarl":403,"jmp":93} and
          raw_indirect["mnemonics_application"] == {"jarl":395,"jmp":92} and
          raw_indirect["reset_thunk_outside_function_classifier"] == "0x00000032")
    check("current computed-call classifier covers 495 total / all 487 application transfers",
          ct["computed_call_sites_reviewed_total"] == 495 and ct["computed_call_sites_reviewed_application"] == 487)
    cp = ct["computed_call_classifier_provenance"]
    check("direct classifier provenance has zero XCP-window source cells",
          cp["direct_referenced_definition_sites"] == 161 and cp["direct_referenced_non_ram_sites"] == 152 and
          cp["direct_referenced_lower_ram_sites"] == 9 and cp["direct_referenced_xcp_window_sites"] == 0 and
          cp["locally_resolved_without_operand_reference_sites"] == 330 and cp["no_definition_within_24_instruction_backtracker_sites"] == 4 and
          cp["all_direct_lower_ram_cells_below_xcp_write_window"])
    ram_cells = {row["cell"]: row for row in cp["direct_lower_ram_cells"]}
    check("direct RAM call-source cells are concrete and below the XCP floor",
          set(ram_cells) == {"0xFEBF0FD0","0xFEBF6B04","0xFEBF117C","0xFEBF1194","0xFEBE5628"} and
          ram_cells["0xFEBF6B04"]["writer"] == "0x00073EEE" and ram_cells["0xFEBF6B04"]["fixed_targets"] == ["0x000766F4","0x000767EA"] and
          all(int(cell,16) < 0xFEBF7C00 for cell in ram_cells))
    check("no raw CodeFlash u32 pointer lands in high tail", ct["raw_codeflash_u32_pointers_into_high_tail"] == [])
    dma = ct["fixed_dmac_descriptor_audit"]
    check("F33 fixed DMAC descriptor families are target-natively enumerated", dma["fixed_descriptor_paths_closed"] is True and dma["descriptor_apply"] == "0x00060A6A" and dma["recovered_fixed_table_callers"] == ["0x00060462","0x00060C20","0x00061B90","0x000628B2"] and len(dma["tables"]) == 7)
    raw_dma_endpoints=[]
    for table in dma["tables"]:
        base=int(table["base"],16); count=table["count"]
        check(f"DMAC table {table['base']} raw hash/pointer provenance", sha(img[base:base+count*0x28]) == table["sha256"] and [f"0x{x:06X}" for x in [i for i in range(len(img)-3) if img[i:i+4] == struct.pack('<I',base)]] == table["raw_pointer_hits"])
        for i in range(count):
            off=base+i*0x28
            raw_dma_endpoints.extend(struct.unpack_from("<IIII", img, off+8)[:2])
            raw_dma_endpoints.extend(struct.unpack_from("<II", img, off+0x18))
    check("fixed DMAC endpoint census is 88 fields with zero XCP-window hits", len(raw_dma_endpoints) == dma["endpoint_count"] == 88 and dma["endpoints_in_xcp_window"] == [] and all(not (0xFEBF7C00 <= x <= 0xFEBFFBFF) for x in raw_dma_endpoints))
    residual=ct["residual_computed_calls"]
    check("four residual computed calls resolve below the XCP window", residual["sites"] == ["0x0008863E","0x0008AF7A","0x0008AF88","0x0008AFAA"] and all(int(x,16) < 0xFEBF7C00 for x in residual["callback_cells"]) and residual["all_cells_below_xcp_write_window"] and residual["writers_install_fixed_codeflash_targets"] and residual["bitwise_complement_guards"])
    exc=ct["exception_saved_pc_audit"]
    check("exception/saved-PC route is confined to lower stacks",
          exc["exception_return_sites"] == ["0x00020102","0x00065C60","0x00071372","0x00071456","0x00071502","0x000715AE","0x00071A90","0x00071C40"] and
          exc["exception_return_count"] == 8 and exc["application_initial_sp"] == "0xFEBE2000" and
          exc["temporary_isr_stacks"] == ["0xFEBE0800","0xFEBE1000","0xFEBE1800","0xFEBE2800"] and
          exc["eipc_saved_on_interrupted_stack"] and exc["all_recovered_saved_pc_stacks_below_xcp_write_window"] and
          exc["direct_flow_edges_into_xcp_write_window"] == 0)
    check("only one recovered application DMAC channel programmer remains", dma["recovered_channel_programmers"] == ["0x00060A6A"] and dma["fixed_global_setup"] == "0x00060A10" and dma["recovered_channel_register_accessors"] == ["0x0006091E","0x00060934","0x00060940","0x000609B0","0x00060A6A"])
    ctbp=ct["ctbp_writer_census"]
    raw_ctbp=find_ldsr_writers(img,20,0)
    check("whole-image CTBP writer census closes CALLT-base retargeting", raw_ctbp == [(0x25E,0,bytes.fromhex("e0a72000"))] and ctbp["writers"] == [{"address":"0x0000025E","bytes":"e0a72000","source_register":"r0"}] and ctbp["all_ctbp_writers_census_closed"] and ctbp["only_writer_sets_zero"])
    vec=ct["fixed_vector_base_setup"]
    check("application INTBP/EBASE setup uses fixed CodeFlash bases", img[0x715B4:0x715E4] == bytes.fromhex("2b06000202000000eb2720082b06000002000000eb1f2008240600b8befe2506fc3d020023060020befe7f002c0682e9") and vec["intbp"] == "0x00020200" and vec["ebase"] == "0x00020000" and vec["values_are_fixed_immediates"] and vec["tester_controlled_vector_base_recovered"] is False)
    check("negative is explicitly bounded after static-pivot exhaustion", all(word in ct["bounded_negative"].lower() for word in ("computed", "dma", "memory-safety", "undiscovered")) and "xcp daq" in ct["bounded_negative"].lower() and "diagnostics" in ct["bounded_negative"].lower())
    check("no complete non-disruptive loader+exec path claimed", a["implementation_readiness"]["complete_non_disruptive_loader_and_execution_path"] is False and a["implementation_readiness"]["safe_inert_vehicle_poc_built"] is False)
    arch = a["architectures"]
    check("ranked architecture disposition is complete", [row["rank"] for row in arch] == [1,2,3] and "0x00081FFE" in arch[0]["exact_surface"].values() and arch[0]["lifetime"].startswith("volatile") and "PROGRAMMING" in arch[2]["network_visibility"] and arch[2]["remaining_unknowns"] == [])

    print("\n== verified geometry promotion ==")
    rows = {row["id"]: row for row in json.loads(RAMREQ.read_text())["variants"]}
    camry = rows["camry-2026-8965f3307000-high-tail"]
    check("variant table promotes only verified high tail", camry["evidence"] == "dynamic-probe-verified" and camry["retained_application_rwx_base"] == "0xFEBFF9F0" and camry["retained_application_rwx_end_exclusive"] == "0xFEBFFBFC" and camry["retained_application_rwx_size"] == "0x20C")
    check("production command5 mailbox remains unassigned", camry["command5_mailbox_address"] is None and camry["command5_mailbox_size"] is None)

    print(f"\nResults: {passed} passed, {failed} failed")
    return 1 if failed else 0


SECTIONS = {
    "codeflash": section_codeflash,
    "flash_backend": section_flash_backend,
    "secoc_patch": section_secoc_patch,
    "lateral_static": section_lateral_static,
    "tss3_opendbc_port": section_tss3_opendbc_port,
    "fault_status": section_fault_status,
    "secoc_recovery": section_secoc_recovery,
    "command5_runtime_carrier": section_command5_runtime_carrier,
    "application_ram_loader": section_application_ram_loader,
}

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--section", choices=tuple(SECTIONS), help="run one F33 proof surface; omitted runs all portable sections")
    args = ap.parse_args()
    names = [args.section] if args.section else list(SECTIONS)
    failures = 0
    for name in names:
        if len(names) > 1:
            print(f"\n===== F33 {name} =====")
        failures += int(SECTIONS[name]() != 0)
    return 1 if failures else 0

if __name__ == "__main__":
    raise SystemExit(main())
