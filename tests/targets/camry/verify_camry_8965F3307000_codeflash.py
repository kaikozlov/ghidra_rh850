#!/usr/bin/env python3
"""Verify exact 8965F3307000 Camry CodeFlash acquisition and target-native static closure.

Standalone section of the exact-F33 portable family; assertions are carried over verbatim.
"""
from __future__ import annotations

from tools import REPO_ROOT
def section_codeflash() -> int:
    """Verify exact 8965F3307000 Camry CodeFlash acquisition and target-native static closure."""
    import hashlib, json, subprocess, sys, tempfile
    from pathlib import Path

    REPO = REPO_ROOT
    RAW_DIR = REPO / 'targets/camry-2026/raw-20260826/codeflash'
    RAW = RAW_DIR / 'camry_8965F3307000_codeflash_20260826T213719Z.bin'
    COV = RAW_DIR / 'camry_8965F3307000_codeflash_20260826T213719Z.coverage.bin'
    RUN = RAW_DIR / 'camry_8965F3307000_codeflash_20260826T213719Z.run.json'
    NORM = REPO / 'firmware/camry-8965F3307000/CodeFlash.bin'
    PAYLOAD = REPO / 'targets/camry-2026/raw-20260826/calvin_payload_codeflash_00000000_00200000.bin'
    EVID = REPO / 'data/generated/camry_8965F3307000_decompiler_evidence.json'
    ART = REPO / 'data/generated/camry_8965F3307000_codeflash.json'
    BUILD = REPO / 'tools/targets/camry/analysis/analyze_camry_8965F3307000_codeflash.py'
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

    print('\n== 2026-08-30 collector-fixed zero-write preflight ==')
    live_pf_dir = REPO / 'targets/camry-2026/raw-20260830/secoc-patch-preflight-f33-collector-fixed'
    live_run = json.loads((live_pf_dir / 'run.json').read_text())
    live_pf = json.loads((live_pf_dir / 'preflight.json').read_text())
    live_events = [json.loads(line) for line in (live_pf_dir / 'telemetry.ndjson').read_text().splitlines() if line.strip()]
    check('collector-fixed preflight completed with telemetry', live_run['status'] == 'payload-complete' and live_run['telemetry']['payload_success'] and live_run['execution']['handler_done'] and live_run['execution']['telemetry_frames'] == live_run['telemetry']['event_count'] == 35)
    check('collector-fixed preflight is exact-target and APPLY-ready', live_pf['apply_ready'] and live_pf['boot_crc_valid'] and live_pf['f181_hex'] == '023839363546333330373030300000000038413331313333303331303000000000' and live_pf['boot_f181_hex'] == '02' + '21' * 32 and live_pf['route'] == {'bus': 0, 'cpu_index': 0, 'elm327_param': 1, 'uds_variant': 'old'})
    check('collector-fixed live observations exactly match offline image', live_pf['config_mismatches'] == [] and live_pf['observation_mismatches'] == [] and live_pf['observed'] == live_pf['expected'] == {'crc_prefix': 0x273C8914, 'crc_residue': 0xFFFFFFFF, 'fixup_stored': 0xD8C376EB, 'patch_observed': 0xD1E0})
    check('collector-fixed telemetry reaches SUCCESS and DONE', any(e.get('name') == 'SUCCESS' for e in live_events) and any(e.get('name') == 'DONE' for e in live_events))

    print('\n== 2026-08-30 persistent Gate-2 APPLY ==')
    apply_dir = REPO / 'targets/camry-2026/raw-20260830/secoc-patch-apply-f33-final'
    apply_run = json.loads((apply_dir / 'run.json').read_text())
    apply_events = [json.loads(line) for line in (apply_dir / 'telemetry.ndjson').read_text().splitlines() if line.strip()]
    check('persistent APPLY completed with no telemetry errors', apply_run['status'] == 'payload-complete' and apply_run['telemetry']['payload_success'] and apply_run['telemetry']['errors'] == [] and apply_run['execution']['handler_done'] and apply_run['execution']['telemetry_frames'] == apply_run['telemetry']['event_count'] == 65)
    check('persistent APPLY exact target and payload identity', apply_run['execution']['f181_hex'] == '023839363546333330373030300000000038413331313333303331303000000000' and apply_run['execution']['boot_f181_hex'] == '02' + '21' * 32 and apply_run['payload']['sha256'] == '5cd8ed3bbdf0c5afeb9af675548ecad836cc3ef4494e8c87528e5c0683188d73')
    values = {(e.get('tag'), e.get('field')): e.get('value') for e in apply_events if e.get('type') == 'value'}
    check('persistent APPLY target readback is patched E001', values.get((0xC0, 0x0203)) == 0x000001E0)
    check('persistent APPLY CRC repair/readback/final residue exact', values.get((0xC1, 0x0300)) == 0x2650CC50 and values.get((0xC1, 0x0302)) == 0xD9AF33AF and values.get((0xC1, 0x0304)) == 0xD9AF33AF and values.get((0xC1, 0x0305)) == 0xFFFFFFFF)
    check('persistent APPLY reaches SUCCESS and DONE while keeping SecOC proof separate', apply_run['apply']['write_crc_sequence_complete'] and apply_run['apply']['secoc_bypass_proven'] is False and any(e.get('name') == 'SUCCESS' for e in apply_events) and any(e.get('name') == 'DONE' for e in apply_events))

    print('\n== 2026-08-30 post-reboot persistence verification ==')
    persist_dir = REPO / 'targets/camry-2026/raw-20260830/secoc-patch-post-reboot-verify'
    persist_run = json.loads((persist_dir / 'run.json').read_text())
    persist_events = [json.loads(line) for line in (persist_dir / 'telemetry.ndjson').read_text().splitlines() if line.strip()]
    check('post-reboot patch persistence verifier succeeds', persist_run['verified'] is True and persist_run['config_mismatches'] == [] and persist_run['observation_mismatches'] == [] and persist_run['telemetry']['payload_success'] and persist_run['telemetry']['event_count'] == 35)
    check('post-reboot exact F33 identities survive power cycle', persist_run['execution']['f181_hex'] == '023839363546333330373030300000000038413331313333303331303000000000' and persist_run['execution']['boot_f181_hex'] == '02' + '21' * 32 and persist_run['execution']['direct_bootloader'] is False)
    check('post-reboot live patch/fixup/CRC exactly match patched image', persist_run['observed'] == persist_run['expected'] == {'crc_prefix': 0x2650CC50, 'crc_residue': 0xFFFFFFFF, 'fixup_stored': 0xD9AF33AF, 'patch_observed': 0x01E0})
    check('post-reboot verifier remains zero-write and SecOC consequence separate', persist_run['verify_config']['original'] == 'e001' and persist_run['verify_config']['replacement'] == 'e0d1' and any(e.get('name') == 'SUCCESS' for e in persist_events) and any(e.get('name') == 'DONE' for e in persist_events))

    print('\n== deterministic static artifact ==')
    with tempfile.TemporaryDirectory() as td:
        out = Path(td) / 'camry.json'
        proc = subprocess.run([sys.executable, str(BUILD), '--out', str(out)], cwd=REPO, capture_output=True, text=True, check=False)
        check('static analyzer succeeds', proc.returncode == 0, proc.stderr[-300:])
        check('static artifact regenerates exactly', proc.returncode == 0 and out.read_bytes() == ART.read_bytes())
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
    check('signed16 staging -> snapshot', '*(undefined2 *)(puVar38 + -0x970) = *(undefined2 *)(puVar38 + 0x39fa);' in funcs[0xBCD62]['decompiled_c'])
    check('selector raw -> staging -> snapshot', 'DAT_febef130 = DAT_febe80bc;' in funcs[0x58074]['decompiled_c'] and 'puVar38[-0xa50] = puVar38[0x3930];' in funcs[0xBCD62]['decompiled_c'])
    check('signed target doubles in target conditioner', 'iVar1 = DAT_febeae90 * 2;' in funcs[0xCCF0E]['decompiled_c'])
    check('target conditioner saturates symmetric int16 domain', '0x7fff' in funcs[0xCCF0E]['decompiled_c'] and '-0x7fff' in funcs[0xCCF0E]['decompiled_c'])
    check('independent plausibility path consumes same snapshot', 'sVar4 = *(short *)(puVar12 + -0x970);' in funcs[0xCEE7C]['decompiled_c'] and 'FUN_000d0970((int)sVar4)' in funcs[0xCEE7C]['decompiled_c'])
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
    scale = cmd['controller_equivalent_scale']
    check('controller-equivalent B6 scale exact fraction', scale['fraction_deg_per_b6_count'] == {'numerator':1024,'denominator':17870})
    check('controller-equivalent scale is ~1.00012 mrad/count', abs(scale['mrad_per_b6_count'] - 1.000121519) < 1e-9)
    print(f'\nResults: {passed} passed, {failed} failed')
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(section_codeflash())
