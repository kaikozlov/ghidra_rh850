#!/usr/bin/env python3
"""Tracked 2026 Camry TSK baseline and Techstream DTC-clear selector pins.

Domain split; assertions and helpers are carried over verbatim.
"""
from __future__ import annotations

from pathlib import Path

from tools import REPO_ROOT
ROOT = REPO = REPO_ROOT

passed = failed = 0


def check(name, cond, detail=""):
    global passed, failed
    ok = bool(cond)
    passed += int(ok)
    failed += int(not ok)
    suffix = f" ({detail})" if detail else ""
    print(f"[{'PASS' if ok else 'FAIL'}] {name}{suffix}")
print()

print("== camry 2026 tsk baseline ==")
def _section_camry_2026_tsk_baseline():
    import gzip
    import hashlib
    import json
    import subprocess
    import sys
    import tempfile
    from pathlib import Path
    REPO = REPO_ROOT
    RAW = REPO / 'targets/camry-2026/raw-20260826'
    ART = REPO / 'data/generated/camry_2026_tsk_baseline.json'
    BUILD = REPO / 'tools/targets/camry/analysis/analyze_camry_2026_baseline.py'

    def sha(path: Path) -> str:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    art = json.loads(ART.read_text())
    print('== source provenance ==')
    expected = {'can_oracle.ndjson.gz': (3265598, 'db47d483016c409b5c3a1ecdf58310f68ca8105a4c16eae54185016a6eaf3f41'), 'identity.json': (1559, '5feffa176a0a0293de53fee91486788c577d603ad72cc6e93064dd3710cad234'), 'programming_probe.json': (2135, 'c8dec4197585622a511a03a629e44b2b69369ce3b5b7978a584dfa5e4fa27817'), 'xcp_probe.json': (702, 'b8d96ae5cb97f18d1138196e2a0cb95de5938ec0ff7e512ee9f752f86645e273')}
    for name, (size, digest) in expected.items():
        p = RAW / name
        check(f'{name} exact tracked identity', p.stat().st_size == size and sha(p) == digest)
    raw = gzip.decompress((RAW / 'can_oracle.ndjson.gz').read_bytes())
    check('uncompressed CAN oracle exact identity', len(raw) == 37628790 and hashlib.sha256(raw).hexdigest() == '7c7b72b11a7a76f3059d63fba5b34f7a6177f8b9d51229e6209df7304b364147')
    print('\n== deterministic generated artifact ==')
    with tempfile.TemporaryDirectory() as td:
        out = Path(td) / 'camry.json'
        proc = subprocess.run([sys.executable, str(BUILD), '--out', str(out)], cwd=REPO, capture_output=True, text=True, check=False)
        check('baseline analyzer succeeds', proc.returncode == 0, proc.stderr[-300:])
        check('baseline artifact regenerates exactly', proc.returncode == 0 and out.read_bytes() == ART.read_bytes())
    print('\n== exact identity and route ==')
    ident = art['identity']
    check('exact two-record F181', ident['f181_records'] == ['8965F3307000', '8A3113303100'])
    check('exact ECU serial', ident['ecu_serial'] == '8965033K9011J2740743')
    check('normal-harness bus1 7A1/7A9 route', ident['route'] == {'elm327_param': 1, 'eps_bus': 1, 'eps_rx': '0x7a9', 'eps_rx_bus': 1, 'eps_tx': '0x7a1', 'semantic_path': 'normal-harness'})
    print('\n== programming and XCP boundary ==')
    prog = art['programming']
    check('PROGRAMMING handoff entered and route preserved', prog['status'] == 'entered' and prog['handoff_switched'] and prog['route_preserved'])
    check('boot F181 is two bang placeholders', bytes.fromhex(prog['bootloader_f181_hex']) == b'\x02' + b'!' * 32)
    xcp = art['xcp']
    check('tested XCP route is negative', xcp['status'] == 'unreachable' and xcp['request_id'] == '0x7f7' and (xcp['response_id'] == '0x7f8') and (xcp['connect_response'] == ''))
    print('\n== TSS3 CAN topology ==')
    can = art['can_capture']
    check('capture is approximately one minute', 59.98 < can['duration_s'] < 60.01)
    check('bus stream census is exact', can['stream_count_by_bus'] == {'0': 22, '1': 179, '2': 22})
    check('bus0/bus2 share exact 22-ID/DLC set', can['bus0_bus2_same_id_dlc_set'] and can['bus0_bus2_stream_count'] == 22)
    check('only 189 payload sequence differs across bus0/bus2', can['bus0_bus2_payload_sequence_unequal'] == ['0x189/64'])
    check('classic 131/2E4 steering is absent', can['legacy_steering_commands_absent'] and can['legacy_steering_counts'] == {'0x131/8': 0, '0x2E4/8': 0})
    check('early B6 absence in the stationary ready segment', can['b6_absent_in_stationary_ready_segment'])
    streams = can['selected_streams']
    for key, expected_count in (('0x00F/8', 619), ('0x025/32', 6188), ('0x030/32', 6188), ('0x090/32', 6187), ('0x0D7/32', 3094), ('0x0AA/8', 6187), ('0x101/8', 3095), ('0x116/8', 2627), ('0x127/8', 3777), ('0x176/8', 1949), ('0x51E/8', 61)):
        check(f'{key} retained count', streams[key]['count'] == expected_count and streams[key]['bus'] == 1)
    check('H/F auxiliary Tx set absent in this segment', all((streams[x]['count'] == 0 for x in ('0x351/4', '0x394/3', '0x4A3/8', '0x4C8/8'))))
    print('\n== H/F wire-format transfer ==')
    hf = art['hf_transfer_observations']
    f030 = hf['0x030']
    check('030 additive rule matches every frame', f030['frame_count'] == f030['additive_rule_matches'] == 6188)
    check('030 torque is dynamic/plausible', f030['steering_wheel_torque_nm'] == {'count': 6188, 'max': 1.8, 'min': -1.75, 'unique_count': 143})
    check('030 candidate fault/inhibit bit stays clear', f030['b6_status_values']['b6_bit2'] == [0])
    check('030 invalid candidate clears early', f030['b6_status_transitions']['b6_bit0'][:2] == [{'seconds': 0.01764, 'value': 1}, {'seconds': 0.201959, 'value': 0}])
    f025 = hf['0x025']
    check('025 steering layout decodes coherent dynamic values', f025['steering_angle_deg']['min'] == -12.0 and f025['steering_angle_deg']['max'] == 19.5 and (f025['steering_rate_raw_or_prior_art_deg_s']['min'] == -80) and (f025['steering_rate_raw_or_prior_art_deg_s']['max'] == 70))
    for addr, count in (('0x101', 3095), ('0x127', 3777), ('0x176', 1949)):
        c = hf['legacy_checksum_carriers'][addr]
        check(f'{addr} Toyota checksum all valid', c['frames'] == c['checksum_matches'] == count)
    check('127 raw0 P candidate is bounded', hf['0x127']['gear_raw_values'] == [0])
    ready = hf['0x51E']
    check('51E Ready wire exercises 0->1', ready['ready_values'] == [0, 1] and [x['value'] for x in ready['transition_timeline'][:2]] == [0, 1])
    check('51E Ready transition timing is exact', ready['transition_timeline'][0] == {'payload': '0000610000000000', 'seconds': 0.01764, 'value': 0} and ready['transition_timeline'][1] == {'payload': '8000610000000000', 'seconds': 0.994317, 'value': 1})
_section_camry_2026_tsk_baseline()
print()


print("== camry 2026 DTC clear ==")
def _section_camry_2026_dtc_clear():
    import hashlib
    import json
    import struct
    import subprocess
    import sys
    import tempfile
    from pathlib import Path

    from tools.techstream.parse_ddb import DDBParser
    from tools.techstream.techstream_paths import V18_TECHSTREAM_ROOT, gts_db_root, resolve_gts_root

    REPO = REPO_ROOT
    RAW = REPO / 'targets/camry-2026/raw-20260827/dtc-clear'
    ART = REPO / 'data/generated/camry_2026_dtc_clear.json'
    BUILD = REPO / 'tools/targets/camry/analysis/analyze_camry_2026_dtc_clear.py'

    def sha(path: Path) -> str:
        return hashlib.sha256(path.read_bytes()).hexdigest()

    expected = {
        'camry_dtc_clear_results.json': (2038, '5d428b050b351db858641f909de926bad0c269e7cbdfa04296378e6f594cf297'),
        'camry_dtc_final_sweep.json': (1657, 'b36d4b4e5788212168e83159c312f1202dcf82eccd36db50277615d58c9e307d'),
        'camry_dtc_sweep_after.json': (3486, '6dd5942e2e96e02bdfc229494e1f8700e15da4d5f121036e2c4fb0542e0f62d9'),
        'camry_dtc_sweep_before.json': (3536, 'ceb02436269d1c2332088f853d3acf80fdc3367905c0fc85142f311c94ac8b27'),
        'camry_functional_mode04_results.json': (742, '73721a17540a58779efd4b935c8d043dacfa8576dc151612e3d23c6e6110e916'),
        'camry_mode04_clear_results.json': (717, '235d6b7d7effff5512854e51cbb5d09f0b4e4825cb269654c88cef9c54325dd4'),
        'camry_obd_mode04_clear_20260827.json': (1494, '976957d9565c3d04c6ab2df658d6be5cd9525653acc5e4dcdbbc59d8848343b6'),
    }
    for name, (size, digest) in expected.items():
        path = RAW / name
        check(f'{name} exact tracked identity', path.stat().st_size == size and sha(path) == digest)

    with tempfile.TemporaryDirectory() as td:
        out = Path(td) / 'dtc-clear.json'
        proc = subprocess.run([sys.executable, str(BUILD), '--out', str(out)], cwd=REPO, capture_output=True, text=True, check=False)
        check('DTC-clear analyzer succeeds', proc.returncode == 0, proc.stderr[-300:])
        check('DTC-clear artifact regenerates exactly', proc.returncode == 0 and out.read_bytes() == ART.read_bytes())
    art = json.loads(ART.read_text())
    check('pre-clear U0131-87 status exact', art['dtc_status']['u0131_87_pre_clear_status'] == {'0x792': '0x28', '0x7b0': '0xAC', '0x7c4': '0x28', '0x7d2': '0x28'})
    check('Brake warning request bit was present', int(art['dtc_status']['u0131_87_pre_clear_status']['0x7b0'], 16) & 0x80)
    check('direct UDS 14 split exact', art['physical_uds14']['succeeded'] == ['0x792', '0x7a1', '0x7a2', '0x7b3', '0x7c4', '0x7d0'] and art['physical_uds14']['rejected_service_not_supported'] == ['0x700', '0x724', '0x747', '0x7b0', '0x7d2'])
    expected_obd = {'0x7E8', '0x7EA', '0x7EB', '0x7ED', '0x7EE'}
    check('functional OBD probe sees exact P5 legislated responders', set(art['legislated_obd']['mode01_responders']) == expected_obd)
    check('functional Mode 04 gets positive 44 from all legislated responders', art['legislated_obd']['request_id'] == '0x7DF' and art['legislated_obd']['mode04_clear_request_frame'] == '0104000000000000' and set(art['legislated_obd']['mode04_positive_responses']) == expected_obd and all(v.startswith('0144') for v in art['legislated_obd']['mode04_positive_responses'].values()))
    check('final 11-ECU sweep has no fault/pending/confirmed/warning records', art['final_sweep']['responding_ecus'] == 11 and art['final_sweep']['all_responding_ecus_clear_of_fault_bits'] is True and art['final_sweep']['remaining_fault_status_records'] == [])

    # Static host corroboration: current GTS+ binds the relevant P5 categories to
    # DelDiagCodeP4. V18 independently resolves the same selector grammar to
    # service 04 / positive 44, with Hybrid/Brake fallback 14FFFFFF / 54.
    parser = DDBParser()
    gts_root = resolve_gts_root()
    gts_master = parser.parse_master_db(gts_db_root(gts_root, 'NA', 'Gen') / 'Toyota.ddb')
    gts_dll = gts_root / 'bin/DelDiagCodeP4.dll'
    check('current GTS+ DelDiagCodeP4 exact identity', gts_dll.stat().st_size == 23568 and sha(gts_dll) == '8e52d52f860b5fbddcaf178bdbbfcf1e310c1a57e418cee840725f95d18d4e00')
    bound = {(r.category_id, r.dll_role_id, r.dll_name) for r in parser.extract_master_dlls(gts_master.sections[19])}
    for cat in (372, 395, 397, 398, 435):
        check(f'current GTS+ category {cat} binds DelDiagCodeP4 role 0x19', (cat, 25, 'DelDiagCodeP4.dll') in bound)

    def rows(section):
        size = section.decoded_record_size
        return [section.decoded_data[i:i + size] for i in range(0, len(section.decoded_data), size)]

    current_func = rows(gts_master.sections[18])
    for cat in (372, 395, 397, 398, 435):
        check(f'current GTS+ category {cat} clear selector 1 exists', any(struct.unpack_from('<HH', r, 0) == (cat, 1) for r in current_func))
    for cat in (397, 435):
        check(f'current GTS+ category {cat} clear fallback selector 0x102 exists', any(struct.unpack_from('<HH', r, 0) == (cat, 0x102) for r in current_func))

    v18_master = parser.parse_master_db(V18_TECHSTREAM_ROOT / 'NA/DB/Toyota.ddb')
    variable = v18_master.sections[0]
    pool = variable.header.record_count * 6
    def variable_blob(index: int) -> bytes:
        off, length = struct.unpack_from('<IH', variable.decoded_data, (index - 1) * 6)
        return variable.decoded_data[pool + off:pool + off + length]
    v18_func = rows(v18_master.sections[18])
    v18_comm = rows(v18_master.sections[17])
    def resolve_selector(cat: int, selector: int) -> tuple[bytes, bytes, bytes]:
        fr = next(r for r in v18_func if struct.unpack_from('<HH', r, 0) == (cat, selector))
        comm_id = struct.unpack_from('<H', fr, 6)[0]
        cr = next(r for r in v18_comm if struct.unpack_from('<H', r, 0)[0] == comm_id)
        refs = struct.unpack_from('<HHH', cr, 2)
        return tuple(variable_blob(x) if x else b'' for x in refs)
    check('V18 category 397 selector 1 resolves to 04 -> 44', resolve_selector(397, 1) == (b'\x04', b'', b'\x44'))
    check('V18 category 435 selector 1 resolves to 04 -> 44', resolve_selector(435, 1) == (b'\x04', b'', b'\x44'))
    check('V18 Hybrid/Brake fallback resolves to 14FFFFFF -> 54', resolve_selector(397, 0x102) == (bytes.fromhex('14ffffff'), b'', b'\x54') and resolve_selector(435, 0x102) == (bytes.fromhex('14ffffff'), b'', b'\x54'))

_section_camry_2026_dtc_clear()
print()

print(f"\n== RESULT: {passed} passed, {failed} failed ==")
raise SystemExit(1 if failed else 0)
