#!/usr/bin/env python3
"""Tracked 2026 Camry live-baseline, NRTD P5, and READY/gear captures.

Merged portable family module.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

passed = failed = 0


def check(name, cond, detail=""):
    global passed, failed
    ok = bool(cond)
    passed += int(ok)
    failed += int(not ok)
    suffix = f" ({detail})" if detail else ""
    print(f"[{'PASS' if ok else 'FAIL'}] {name}{suffix}")

print("== camry 2026 nrtd p5 ==")
def _section_camry_2026_nrtd_p5():
    import hashlib
    import json
    import subprocess
    import sys
    import tempfile
    from pathlib import Path
    REPO = Path(__file__).resolve().parents[1]
    RAW = REPO / 'targets/camry-2026/raw-20260826'
    ART = REPO / 'data/generated/camry_2026_nrtd_p5.json'
    BUILD = REPO / 'tools/analyze_camry_2026_nrtd_p5.py'

    def sha(path: Path) -> str:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    art = json.loads(ART.read_text())
    print('== source provenance ==')
    expected = {'camry_nrtd_module_identity_20260826.json': (5398, '0ed09e5abec3a555d9e8b26c03a740747f04675859de8d12f49c8afb0eb53bdd'), 'camry_nrtd_p5_oracles_20260826.json': (1179, '17d9870cc65f71c9890389a22fa3f0f9561ec3d4f2679cc9e61076ed6977bcba'), 'camry_nrtd_p5_oracles_extra_20260826.json': (586, '4a59d82a2f027b5d6413bf6608905503975afa40ce87dfa350b36e8459da62f6'), 'camry_nrtd_brake_107e_extended_20260826.json': (281, '3475f1df52cf69fc56fea51cdaa85cc00797cd720e3583e29d0aaa7b1b80af2c'), 'camry_nrtd_cruise_buttons_20260826.json': (72108, '1977d05439f632017369d761641726536b635cc95b66cd5d5079af8096f4877e'), 'camry_nrtd_cruise_MAIN_20260826.json': (35980, 'ca7c3911e402a763f23af00c92f449c75afa8c8b0e94b10293b710aad95d337b'), 'camry_nrtd_cruise_RESPLUS_20260826.json': (35882, '1d176f20e9c2b11e46ebe6d069c1d653dd3026a3f4895dde85730f9742e1ce07'), 'camry_nrtd_cruise_SETMINUS_20260826.json': (35881, 'f9ea74fd5846222d38884183c12eb19ec20fd80c6730f21dc1bcd5a377efa9aa'), 'camry_nrtd_cruise_CANCEL_20260826.json': (35884, '432fc309de02bfdd4f5927af6928382cf0f0617f68258484eabac05f3fb06111'), 'camry_nrtd_cruise_DISTANCE_20260826.json': (35862, '024f1df8b783da1b4d1485b824bf3092ea412c112efb2f12ad2ebdbf4cfddcdb'), 'camry_nrtd_cruise_can_sync_20260826.json.gz': (1103765, '083435105745d928ceea5dea2a614b7a1fbd32341ba4c94987c73ef6287e87fa')}
    for name, (size, digest) in expected.items():
        p = RAW / name
        check(f'{name} exact tracked identity', p.stat().st_size == size and sha(p) == digest)
    manifest = (RAW / 'NRTD_MANIFEST.txt').read_text()
    check('NRTD manifest pins every raw source', all((name in manifest and digest in manifest for name, (_, digest) in expected.items())))
    check('NRTD manifest preserves read-only boundary', all((x in manifest for x in ('Not Ready to Drive', 'No SecurityAccess key, RoutineControl start, write, reset, download', 'vehicle-control transmission', 'separate from MANIFEST.txt'))))
    print('\n== deterministic generated artifact ==')
    with tempfile.TemporaryDirectory() as td:
        out = Path(td) / 'camry_nrtd.json'
        proc = subprocess.run([sys.executable, str(BUILD), '--out', str(out)], cwd=REPO, capture_output=True, text=True, check=False)
        check('NRTD analyzer succeeds', proc.returncode == 0, proc.stderr[-300:])
        check('NRTD artifact regenerates exactly', proc.returncode == 0 and out.read_bytes() == ART.read_bytes())
    check('schema is v1', art['schema'] == 'camry-2026-nrtd-p5-v1')
    check('vehicle state is explicitly NRTD/stationary', 'Not Ready to Drive' in art['vehicle_state'] and 'stationary' in art['vehicle_state'])
    print('\n== exact P5 module identities ==')
    mods = art['module_identity']
    frc = mods['FRC_P5']
    brake = mods['Brake_EPB_category_435']
    check('normal-harness ELM param1 retained', mods['elm327_param'] == 1)
    check('FRC route and exact F181', frc['bus'] == 1 and frc['tx'] == '0x792' and (frc['rx'] == '0x79A') and (frc['f181'] == '8646F3315000'))
    check('FRC exact supporting identities', frc['f18c_serial'] == 'TN69400026030404235J' and frc['ecu_part_0105'] == '8646C06091' and (frc['swin_1fff'] == '06000000000000000000'))
    check('FRC direct route is bus1-only in bounded sweep', frc['bus0_bus2_f181_timeout'] is True)
    check('Brake/EPB route and exact F181', brake['bus'] == 1 and brake['tx'] == '0x7B0' and (brake['rx'] == '0x7B8') and (brake['f181'] == 'F152633K0000'))
    check('Brake exact supporting identities', brake['f18c_serial'] == '8954147040CFC1800985' and brake['ecu_part_0105'] == '8954147040')
    check('Brake direct route is bus1-only in bounded sweep', brake['bus0_bus2_f181_timeout'] is True)
    print('\n== read-only Techstream-oracle transfer ==')
    fo = art['frc_read_only_oracles']
    expected_oracles = {'0X1202': ('febcf6d2', 4), '0X1901': ('0000000000000000', 8), '0X1905': ('8080', 2), '0X1906': ('e080e0008000', 6), '0X1912': ('02', 1), '0X1914': ('8000', 2), '0X1918': ('8000', 2), '0X1928': ('c0c0', 2)}
    check('all selected FRC P5 oracles answer', all((fo[k]['status'] == 'positive' and (fo[k]['hex'], fo[k]['length']) == v for k, v in expected_oracles.items())))
    bo = art['brake_read_only_oracles']
    check('Brake 0x102F answers', bo['0x102F'] == {'hex': 'f700fd007c00a9000000', 'length': 10, 'status': 'positive'})
    check('Brake 0x107E rejected in default', bo['0x107E_default']['status'] == 'negative_or_timeout' and 'request out of range' in bo['0x107E_default']['error'])
    check('Brake 0x107E rejected in extended and ECU returned default', bo['0x107E_extended']['extended_session'] == 'positive' and bo['0x107E_extended']['status'] == 'negative_or_timeout' and ('request out of range' in bo['0x107E_extended']['error']) and (bo['0x107E_extended']['returned_default'] is True))
    check('0x107E Corolla live-oracle transfer is explicitly rejected', 'Do not transfer' in bo['boundary'])
    print('\n== isolated cruise controls ==')
    iso = art['isolated_cruise_controls']

    def values(label: str, field: str) -> list[str]:
        return [x[field] for x in iso[label]['transitions']]
    check('MAIN isolated 1906 event', iso['MAIN']['sample_count'] == 373 and values('MAIN', '1906') == ['e080e0008000', 'e0c0e0008000', 'e080e0008000'])
    check('RES+ isolated two-phase 1906 event', iso['RES+']['sample_count'] == 372 and values('RES+', '1906') == ['e080e0008000', 'e080e0808000', 'e0a0e0808000', 'e080e0008000'])
    check('SET- isolated 1906 event', values('SET-', '1906') == ['e080e0008000', 'e080e0408000', 'e080e0008000'])
    check('CANCEL isolated 1906 event', values('CANCEL', '1906') == ['e080e0008000', 'e080e0208000', 'e080e0008000'])
    check('distance isolated persistent 1912 change', values('DISTANCE', '1912') == ['03', '04'])
    print('\n== synchronized diagnostic/CAN join ==')
    sync = art['synchronized_capture']
    check('synchronized capture exact sample/frame counts', sync['oracle_sample_count'] == 1742 and sync['can_frame_count'] == 90932)
    check('exact synchronized event times', sync['event_times_s'] == {'CANCEL': 15.285071, 'DISTANCE': 16.874632, 'MAIN': 9.884382, 'RES+': 11.7243, 'SET-': 13.624379})
    carrier = sync['0x0FE_momentary_switch_carrier']
    check('0x0FE/32 bus1 momentary carrier cadence', carrier['bus'] == 1 and carrier['address'] == '0x0FE' and (carrier['dlc'] == 32) and (33.0 < carrier['rate_hz'] < 33.4))
    check('0x0FE baseline tuple exact', carrier['baseline_B3_B4_B6_B7'] == {'B3': 63, 'B4': 0, 'B6': 195, 'B7': 98})
    expected_events = {'MAIN': ({'B3': 63, 'B4': 0, 'B6': 195, 'B7': 102}, {'B3': 0, 'B4': 0, 'B6': 0, 'B7': 4}), 'RES+': ({'B3': 191, 'B4': 0, 'B6': 67, 'B7': 98}, {'B3': 128, 'B4': 0, 'B6': 128, 'B7': 0}), 'SET-': ({'B3': 63, 'B4': 128, 'B6': 195, 'B7': 34}, {'B3': 0, 'B4': 128, 'B6': 0, 'B7': 64}), 'CANCEL': ({'B3': 63, 'B4': 64, 'B6': 195, 'B7': 66}, {'B3': 0, 'B4': 64, 'B6': 0, 'B7': 32})}
    for label, (event_tuple, xor) in expected_events.items():
        e = carrier['events'][label]
        check(f'0x0FE {label} event tuple exact', e['event_B3_B4_B6_B7'] == event_tuple and e['xor'] == xor)
    check('0x0FE interpretation is dynamic join, not producer claim', 'direct dynamic join' in carrier['interpretation'] and 'Counter/integrity' in carrier['interpretation'])
    dist = sync['distance_state']
    check('distance DID 1912 validated twice', dist['isolated_transition'] == '03->04' and dist['synchronized_transition'] == '04->01' and (dist['frc_did'] == '0x1912'))
    c251 = dist['candidate_can_carriers']['0x251/8']
    c5af = dist['candidate_can_carriers']['0x5AF/32']
    check('0x251 distance candidate exact', c251['bus'] == 1 and c251['byte_index'] == 5 and (c251['before'] == 136) and (c251['after'] == 40) and (c251['payload_before'] == 'a00000488088a080') and (c251['payload_after'] == 'a00000488028a080') and (0 < c251['latency_from_1912_change_ms'] < 20))
    check('0x5AF distance candidate exact', c5af['bus'] == 1 and c5af['byte_index'] == 24 and (c5af['before'] == 240) and (c5af['after'] == 228) and (c5af['xor'] == 20) and (0 < c5af['latency_from_1912_change_ms'] < 20))
    check('distance ordinary-CAN semantics remain bounded', all(('candidate only' in x['boundary'] for x in (c251, c5af))) and 'pending an independent repeat/enum sweep' in dist['interpretation'])
    check('production boundary remains observation-only', all((x in art['production_boundary'] for x in ('identities and observation carriers only', 'does not establish Camry B6', 'production safety policy'))))
    print('\n== documentation ==')
    doc = (REPO / 'docs/variants/camry-2026-live-baseline.md').read_text()
    for token in ('8646F3315000', 'F152633K0000', '0x0FE', '0x1906', '0x1912', '0x251', '0x5AF', '0x107E'):
        check(f'Camry report preserves {token}', token in doc)
_section_camry_2026_nrtd_p5()
print()

print("== camry 2026 ready gear ==")
def _section_camry_2026_ready_gear():
    import gzip
    import hashlib
    import json
    import subprocess
    import sys
    import tempfile
    from pathlib import Path
    REPO = Path(__file__).resolve().parents[1]
    RAW = REPO / 'targets/camry-2026/raw-20260826'
    ART = REPO / 'data/generated/camry_2026_ready_gear.json'
    BUILD = REPO / 'tools/analyze_camry_2026_ready_gear.py'

    def sha(path: Path) -> str:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    art = json.loads(ART.read_text())
    print('== source provenance ==')
    expected = {'camry_ready_gear_capture.py': (774, 'b79857ffa38f7ad94030313a5c5609cbd3e35178c31f8d72fa72a912c20740fb'), 'camry_ready_gear_20260826.json.gz': (1660906, '379ec28fba65191d2898ebb156fe83e2e8e59c38bbf5fcfb7166ec9ff32c3889'), 'camry_b_capture.py': (755, '2d72ec4ace3ab01ecae440d8d4f8324e3d7166a15f9bdd868d6a5c2d2a2ae153'), 'camry_ready_b_20260826.json.gz': (715102, '7bae994dea1caff06d8f31f58558f67d646da38bd9531557875858eb33fa4db3')}
    for name, (size, digest) in expected.items():
        p = RAW / name
        check(f'{name} exact tracked identity', p.stat().st_size == size and sha(p) == digest)
    check('READY gear manifest pins missed-B first run and B repeat', 'B had been missed' in (RAW / 'READY_GEAR_MANIFEST.txt').read_text() and 'D/B/D' in (RAW / 'READY_GEAR_MANIFEST.txt').read_text())
    for name, raw_size, raw_sha in (('camry_ready_gear_20260826.json.gz', 16814179, 'c03524036e531c22d60646be65c57b85fb1e9fb0c8b5d2c50e4b3055dbecef52'), ('camry_ready_b_20260826.json.gz', 7278095, '733b7a6fe9aa2f12401077489d662657a5abd20588c1d53a600ffbeec41b40f2')):
        raw = gzip.decompress((RAW / name).read_bytes())
        check(f'{name} uncompressed identity', len(raw) == raw_size and hashlib.sha256(raw).hexdigest() == raw_sha)
    print('\n== passive capture boundary ==')
    for name in ('camry_ready_gear_capture.py', 'camry_b_capture.py'):
        src = (RAW / name).read_text()
        check(f'{name} uses can_recv', 'can_recv' in src)
        check(f'{name} has no CAN transmit', 'can_send' not in src and 'can_send_many' not in src)
        check(f'{name} has no UDS/security path', all((x not in src for x in ('UdsClient', 'SecurityAccess', 'RoutineControl', 'request_download', '0x27'))))
    check('artifact preserves observation-only boundary', art['capture_boundary']['no_vehicle_control_transmission'] is True and 'passive' in art['capture_boundary']['operation'])
    print('\n== deterministic artifact ==')
    with tempfile.TemporaryDirectory() as td:
        out = Path(td) / 'camry-ready-gear.json'
        proc = subprocess.run([sys.executable, str(BUILD), '--out', str(out)], cwd=REPO, capture_output=True, text=True, check=False)
        check('READY/gear analyzer succeeds', proc.returncode == 0, proc.stderr[-300:])
        check('READY/gear artifact regenerates exactly', proc.returncode == 0 and out.read_bytes() == ART.read_bytes())
    check('schema is v1', art['schema'] == 'camry-2026-ready-gear-v1')
    print('\n== controlled Ready transition ==')
    ready = art['ready_status']
    check('51E Ready sequence is 0->1', ready['first_run_sequence'] == [0, 1])
    check('51E transition bytes/timing exact', ready['transition'] == [{'payload': '0000640000000000', 'seconds': 0.070314, 'value': 0}, {'payload': '80006e0000000000', 'seconds': 5.213083, 'value': 1}])
    check('Ready causality strengthened but latency bounded', 'logger was already running in NRTD' in ready['interpretation'] and 'not machine-timestamped' in ready['interpretation'])
    print('\n== full 0x127 gear enum ==')
    gear = art['gear']
    check('first sequence P-R-N-D-N-R-P exact', gear['first_run_sequence'] == [0, 1, 2, 3, 2, 1, 0])
    check('B repeat sequence exact', gear['second_run_sequence'] == [0, 3, 4, 3])
    check('complete enum exact', gear['validated_enum'] == {'0': 'P', '1': 'R', '2': 'N', '3': 'D', '4': 'B'})
    check('first 0x127 checksum all valid', gear['checksum']['first_run'] == {'frames': 3777, 'matches': 3777})
    check('B-run 0x127 checksum all valid', gear['checksum']['b_run'] == {'frames': 1634, 'matches': 1634})
    p1 = gear['evidence']['P_R_N_D_roundtrip']
    check('P/R/N/D transition times exact', [(x['seconds'], x['value']) for x in p1] == [(0.016697, 0), (12.560082, 1), (14.443866, 2), (17.525321, 3), (21.129039, 2), (23.014504, 1), (25.192386, 0)])
    b = gear['evidence']['B_roundtrip']
    check('D/B/D transition times exact', [(x['seconds'], x['value']) for x in b] == [(0.020694, 0), (5.107709, 3), (9.480908, 4), (13.626834, 3)])
    check('B exact stable payload', b[2]['payload'] == '00100000004e8d1b')
    check('gear interpretation closes Camry measurement only', 'complete prior-art enum' in gear['interpretation'] and 'cross-model' in gear['interpretation'])
    print('\n== stationary corroboration ==')
    for name, count in (('nrtd_to_ready_gear', 6187), ('ready_b', 2677)):
        wheels = art['captures'][name]['0x0AA_stationary_corroboration']
        check(f'{name} stationary wheel carrier exact', wheels['frame_count'] == count and wheels['unique_payloads'] == ['1a6f1a6f1a6f1a6f'])
    print('\n== documentation ==')
    doc = (REPO / 'docs/variants/camry-2026-live-baseline.md').read_text()
    for token in ('VAR-053', 'P=0', 'R=1', 'N=2', 'D=3', 'B=4', '5.213083', '9.480908'):
        check(f'Camry report preserves {token}', token in doc)
    check('production boundary remains read-only', 'Production output remains disabled' in doc and 'does not authorize' in doc)
_section_camry_2026_ready_gear()
print()

print("== camry 2026 relay-correct capture ==")
def _section_camry_2026_relay_correct_capture():
    import hashlib
    import json
    import subprocess
    import sys
    import tempfile
    from pathlib import Path
    REPO = Path(__file__).resolve().parents[1]
    RAW = REPO / 'targets/camry-2026/raw-20260827'
    ART = REPO / 'data/generated/camry_2026_relay_correct_capture.json'
    BUILD = REPO / 'tools/analyze_camry_2026_relay_capture.py'

    def sha(path: Path) -> str:
        return hashlib.sha256(path.read_bytes()).hexdigest()

    print('== source provenance ==')
    expected = {
        'camry_post_repin_nrtd_20260827.json.gz': (252884, '4e061d5ec06b0dee0b208e7bc34d5f8050af565978ef3254ce221ad329b4f74d'),
        'camry_post_repin_ready_20260827.json.gz': (298123, '32e9ac52c53ac05248b45c2f0eb6a6d50c59c11a9db4fafb31e145919078a58d'),
        'camry_relay_route_can_20260827.ndjson.gz': (14639570, 'be0c02946818fafc48b7d3e2be5d2fde31d796e057ab29d8bf59a879c7553db5'),
        'camry_relay_lta_confirm_route_can_20260827.ndjson.gz': (24952076, '641eee57eaffc579002708185178ea08c189155527354712dd43a1f0e309bb3a'),
        'extract_route_can.py': (None, 'ed4d5a69c8485296287aeda09735e5724c87270b610b264491dc3070a637a926'),
    }
    for name, (size, digest) in expected.items():
        path = RAW / name
        check(f'{name} exact tracked identity', (size is None or path.stat().st_size == size) and sha(path) == digest)
    manifest = (RAW / 'MANIFEST.txt').read_text()
    check('relay manifest pins privacy/passive boundary', all(x in manifest for x in ('passive incoming CAN only', 'No GPS', 'CHECKSUM_ERROR', 'machine-prove')))

    print('\n== deterministic artifact ==')
    with tempfile.TemporaryDirectory() as td:
        out = Path(td) / 'relay.json'
        proc = subprocess.run([sys.executable, str(BUILD), '--out', str(out)], cwd=REPO, capture_output=True, text=True, check=False)
        check('relay analyzer succeeds', proc.returncode == 0, proc.stderr[-300:])
        check('relay artifact regenerates exactly', proc.returncode == 0 and out.read_bytes() == ART.read_bytes())
    art = json.loads(ART.read_text())
    check('relay artifact schema v2', art['schema'] == 'camry-2026-relay-correct-capture-v2')
    check('production output stays disabled', art['conclusion']['production_output_authorized'] is False and 'passive incoming CAN only' in art['capture_boundary']['operation'])

    print('\n== physical repin topology ==')
    nrtd = art['post_repin_nrtd']
    check('NRTD bus0/bus2 exact duplicated sequence', nrtd['bus0_bus2_sequence_identical'] is True and nrtd['frames_by_bus'] == {'0': 13910, '1': 3938, '2': 13910})
    check('NRTD repin census is 153/22/153', nrtd['id_dlc_count_by_bus'] == {'0': 153, '1': 22, '2': 153})
    for addr, expected_count in (('0x00F/8', 100), ('0x025/32', 1000), ('0x030/32', 1000), ('0x0D7/32', 500)):
        check(f'{addr} moved to relay pair', nrtd['selected_counts'][addr] == {'0': expected_count, '1': 0, '2': expected_count})
    ready = art['post_repin_ready']
    check('READY keeps same 0/2-vs-1 topology', ready['id_dlc_count_by_bus'] == {'0': 165, '1': 22, '2': 165})
    check('READY bit is present on both relay sides', ready['ready_values_bus0'] == [1] and ready['selected_counts']['0x51E/8'] == {'0': 9, '1': 0, '2': 9})

    print('\n== relay-correct moving route ==')
    drive = art['drive']
    check('route retains nine segments / 1.65M incoming frames', drive['segment_count'] == 9 and drive['frame_count'] == 1656656)
    check('B6 absent at every DLC on every incoming bus', drive['b6_any_bus_any_length_count'] == 0 and drive['b6_examples'] == [])
    for seg in drive['segments']:
        p = seg['protected_counts']
        check(f'seg{seg["segment"]} keeps protected sync/D7 but no B6', p['0x00F/8']['0'] > 0 and p['0x00F/8']['2'] > 0 and p['0x0D7/32']['0'] > 0 and p['0x0D7/32']['2'] > 0 and sum(p['0x0B6/32'].values()) == 0)
    check('segments 4-6 are continuously moving', all(drive['segments'][i]['speed_kph']['moving_over_2kph_fraction'] == 1.0 for i in (4, 5, 6)))
    check('segment 5 is D-state and 32.66..42.88 kph', drive['segments'][5]['gear_raw_counts'] == {'3': 3662} and drive['segments'][5]['speed_kph']['min'] == 32.66 and drive['segments'][5]['speed_kph']['max'] == 42.88)
    switches = drive['validated_cruise_switch_events']
    check('same-car 0x0FE join sees MAIN toggles in segments 4/5', len(switches['MAIN']['4']) == 2 and len(switches['MAIN']['5']) == 2)
    check('same-car 0x0FE join sees SET- interaction in segment 5', switches['SET_MINUS']['5'] == [
        {'end_s': 19.64854, 'frames': 5, 'start_s': 19.526293},
        {'end_s': 20.159219, 'frames': 3, 'start_s': 20.097979},
    ])
    check('0x08A is retained only as structural corroboration', set(drive['structural_0x08A_transitions']) == {'4', '5'} and 'machine-prove' in drive['interpretation'])
    check('zero-B6 conclusion remains bounded', 'bounded negative' in art['conclusion']['b6'] and 'synchronize' in art['conclusion']['next_observation'])

    print('\n== deliberate confirmation drive ==')
    confirm = art['confirmation_drive']
    check('confirmation route retains ten segments / 1.918M incoming frames', confirm['segment_count'] == 10 and confirm['frame_count'] == 1918047)
    check('confirmation route repeats zero B6 at every DLC/bus', confirm['b6_any_bus_any_length_count'] == 0 and confirm['b6_examples'] == [])
    for seg in confirm['segments']:
        pcounts = seg['protected_counts']
        check(f'confirmation seg{seg["segment"]} keeps protected sync/D7 but no B6', pcounts['0x00F/8']['0'] > 0 and pcounts['0x00F/8']['2'] > 0 and pcounts['0x0D7/32']['0'] > 0 and pcounts['0x0D7/32']['2'] > 0 and sum(pcounts['0x0B6/32'].values()) == 0)
    segs = {x['segment']: x for x in confirm['segments']}
    check('confirmation contains sustained road-speed operation', all(segs[i]['speed_kph']['moving_over_2kph_fraction'] == 1.0 for i in (18, 20, 21, 22)) and segs[20]['speed_kph']['min'] == 65.31 and segs[20]['speed_kph']['max'] == 72.493)
    check('confirmation sees repeated same-car MAIN interactions', set(confirm['validated_cruise_switch_events']['MAIN']) == {'16', '18', '19', '20'})
    check('confirmation 0x08A stays structural only', set(confirm['structural_0x08A_transitions']) == {'18', '19', '20', '21'} and 'machine-proves' in confirm['interpretation'])
    combined = art['combined_route_evidence']
    check('two drives total 19 segments / 3.574M incoming frames / zero B6', combined == {'b6_any_bus_any_length_count': 0, 'frame_count': 3574703, 'segment_count': 19})
    check('operator report is retained as unsynchronized evidence only', 'not synchronized' in art['capture_boundary']['operator_report_boundary'])

    print('\n== documentation ==')
    doc = (REPO / 'docs/variants/camry-2026-live-baseline.md').read_text()
    for token in ('relay-correct', '1,656,656', '1,918,047', '3,574,703', 'zero `0x0B6`', '0x0FE', 'CHECKSUM_ERROR'):
        check(f'Camry report preserves relay result {token}', token in doc)
_section_camry_2026_relay_correct_capture()
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
    REPO = Path(__file__).resolve().parents[1]
    RAW = REPO / 'targets/camry-2026/raw-20260826'
    ART = REPO / 'data/generated/camry_2026_tsk_baseline.json'
    BUILD = REPO / 'tools/analyze_camry_2026_baseline.py'

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
    check('schema is v1', art['schema'] == 'camry-2026-tsk-baseline-v1')
    check('vehicle attribution stays external to wire facts', art['vehicle_attribution']['vehicle'] == '2026 Toyota Camry' and 'operator context' in art['vehicle_attribution']['boundary'])
    print('\n== exact identity and route ==')
    ident = art['identity']
    check('exact two-record F181', ident['f181_records'] == ['8965F3307000', '8A3113303100'])
    check('exact ECU serial', ident['ecu_serial'] == '8965033K9011J2740743')
    check('normal-harness bus1 7A1/7A9 route', ident['route'] == {'elm327_param': 1, 'eps_bus': 1, 'eps_rx': '0x7a9', 'eps_rx_bus': 1, 'eps_tx': '0x7a1', 'semantic_path': 'normal-harness'})
    check('F181 is new to prior corpus', ident['exact_f181_known_in_prior_repo_corpus'] is False)
    print('\n== programming and XCP boundary ==')
    prog = art['programming']
    check('PROGRAMMING handoff entered and route preserved', prog['status'] == 'entered' and prog['handoff_switched'] and prog['route_preserved'])
    check('boot F181 is two bang placeholders', prog['bootloader_f181_is_two_bang_placeholders'] and bytes.fromhex(prog['bootloader_f181_hex']) == b'\x02' + b'!' * 32)
    check('RAM-exec transfer remains unclaimed', all((x in prog['boundary'] for x in ('not established', 'must not be inferred'))))
    xcp = art['xcp']
    check('tested XCP route is negative', xcp['status'] == 'unreachable' and xcp['request_id'] == '0x7f7' and (xcp['response_id'] == '0x7f8') and (xcp['connect_response'] == ''))
    check('XCP negative remains route/session bounded', 'not a universal physical absence proof' in xcp['boundary'])
    print('\n== TSS3 CAN topology ==')
    can = art['can_capture']
    check('capture is approximately one minute', 59.98 < can['duration_s'] < 60.01)
    check('bus stream census is exact', can['stream_count_by_bus'] == {'0': 22, '1': 179, '2': 22})
    check('bus0/bus2 share exact 22-ID/DLC set', can['bus0_bus2_same_id_dlc_set'] and can['bus0_bus2_stream_count'] == 22)
    check('only 189 payload sequence differs across bus0/bus2', can['bus0_bus2_payload_sequence_unequal'] == ['0x189/64'])
    check('classic 131/2E4 steering is absent', can['legacy_steering_commands_absent'] and can['legacy_steering_counts'] == {'0x131/8': 0, '0x2E4/8': 0})
    check('B6 absent only in non-LTA segment', can['b6_absent_in_stationary_ready_segment'] and 'stock-LTA' in can['b6_absence_boundary'] and ('segment-level negative' in can['b6_absence_boundary']))
    streams = can['selected_streams']
    for key, expected_count in (('0x00F/8', 619), ('0x025/32', 6188), ('0x030/32', 6188), ('0x090/32', 6187), ('0x0D7/32', 3094), ('0x0AA/8', 6187), ('0x101/8', 3095), ('0x116/8', 2627), ('0x127/8', 3777), ('0x176/8', 1949), ('0x51E/8', 61)):
        check(f'{key} retained count', streams[key]['count'] == expected_count and streams[key]['bus'] == 1)
    check('H/F auxiliary Tx set absent in this segment', all((streams[x]['count'] == 0 for x in ('0x351/4', '0x394/3', '0x4A3/8', '0x4C8/8'))))
    print('\n== H/F wire-format transfer ==')
    hf = art['hf_transfer_observations']
    check('classification does not overclaim Camry firmware equivalence', 'wire-format transfer' in hf['classification'] and 'unproved without CodeFlash' in hf['classification'])
    f030 = hf['0x030']
    check('030 additive rule matches every frame', f030['frame_count'] == f030['additive_rule_matches'] == 6188 and '+ 0x38' in f030['additive_rule'])
    check('030 torque is dynamic/plausible', f030['steering_wheel_torque_nm'] == {'count': 6188, 'max': 1.8, 'min': -1.75, 'unique_count': 143})
    check('030 candidate fault/inhibit bit stays clear', f030['b6_status_values']['b6_bit2'] == [0])
    check('030 invalid candidate clears early', f030['b6_status_transitions']['b6_bit0'][:2] == [{'seconds': 0.01764, 'value': 1}, {'seconds': 0.201959, 'value': 0}])
    f025 = hf['0x025']
    check('025 steering layout decodes coherent dynamic values', f025['steering_angle_deg']['min'] == -12.0 and f025['steering_angle_deg']['max'] == 19.5 and (f025['steering_rate_raw_or_prior_art_deg_s']['min'] == -80) and (f025['steering_rate_raw_or_prior_art_deg_s']['max'] == 70))
    for addr, count in (('0x101', 3095), ('0x127', 3777), ('0x176', 1949)):
        c = hf['legacy_checksum_carriers'][addr]
        check(f'{addr} Toyota checksum all valid', c['frames'] == c['checksum_matches'] == count)
    check('127 raw0 P candidate is bounded', hf['0x127']['gear_raw_values'] == [0] and 'prior-art-compatible with P' in hf['0x127']['interpretation'] and ('transition validation remains required' in hf['0x127']['interpretation']))
    ready = hf['0x51E']
    check('51E Ready wire exercises 0->1', ready['ready_values'] == [0, 1] and [x['value'] for x in ready['transition_timeline'][:2]] == [0, 1])
    check('51E Ready transition timing is exact', ready['transition_timeline'][0] == {'payload': '0000610000000000', 'seconds': 0.01764, 'value': 0} and ready['transition_timeline'][1] == {'payload': '8000610000000000', 'seconds': 0.994317, 'value': 1})
    check('Ready interpretation retains causal boundary', 'strongly corroborating' in ready['interpretation'] and 'not independently recorded' in ready['interpretation'])
    print('\n== documentation ==')
    doc = (REPO / 'docs/variants/camry-2026-live-baseline.md').read_text()
    for token in ('8965F3307000', '8A3113303100', '0x7A1', '0x7A9', '0x030', '0x51E', '0x0B6', 'Ready Status'):
        check(f'variant report preserves {token}', token in doc)
    check('report preserves firmware-transfer boundary', 'not a Camry CodeFlash analysis' in doc and 'Production output remains disabled' in doc)
_section_camry_2026_tsk_baseline()
print()

print(f"\n== RESULT: {passed} passed, {failed} failed ==")
raise SystemExit(1 if failed else 0)
