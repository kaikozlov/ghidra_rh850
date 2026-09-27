#!/usr/bin/env python3
"""Tracked 2026 Camry engagement-state captures: NRTD/P5 bring-up, READY/gear baseline, and cruise/LTA edge census.

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

print("== camry 2026 nrtd p5 ==")
def _section_camry_2026_nrtd_p5():
    import hashlib
    import json
    import subprocess
    import sys
    import tempfile
    from pathlib import Path
    REPO = REPO_ROOT
    RAW = REPO / 'targets/camry-2026/raw-20260826'
    ART = REPO / 'data/generated/camry_2026_nrtd_p5.json'
    BUILD = REPO / 'tools/targets/camry/analysis/analyze_camry_2026_nrtd_p5.py'

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
    print('\n== deterministic generated artifact ==')
    with tempfile.TemporaryDirectory() as td:
        out = Path(td) / 'camry_nrtd.json'
        proc = subprocess.run([sys.executable, str(BUILD), '--out', str(out)], cwd=REPO, capture_output=True, text=True, check=False)
        check('NRTD analyzer succeeds', proc.returncode == 0, proc.stderr[-300:])
        check('NRTD artifact regenerates exactly', proc.returncode == 0 and out.read_bytes() == ART.read_bytes())
    print('\n== exact P5 module identities ==')
    mods = art['module_identity']
    frc = mods['FRC_P5']
    brake = mods['Brake_EPB_category_435']
    check('normal-harness ELM param1 retained', mods['elm327_param'] == 1)
    check('FRC route and exact F181', frc['bus'] == 1 and frc['tx'] == '0x792' and (frc['rx'] == '0x79A') and (frc['f181'] == '8646F3315000'))
    check('FRC exact supporting identities', frc['f18c_serial'] == 'TN69400026030404235J' and frc['ecu_part_0105'] == '8646C06091' and (frc['swin_1fff'] == '06000000000000000000'))
    check('Brake/EPB route and exact F181', brake['bus'] == 1 and brake['tx'] == '0x7B0' and (brake['rx'] == '0x7B8') and (brake['f181'] == 'F152633K0000'))
    check('Brake exact supporting identities', brake['f18c_serial'] == '8954147040CFC1800985' and brake['ecu_part_0105'] == '8954147040')
    print('\n== read-only Techstream-oracle transfer ==')
    fo = art['frc_read_only_oracles']
    expected_oracles = {'0X1202': ('febcf6d2', 4), '0X1901': ('0000000000000000', 8), '0X1905': ('8080', 2), '0X1906': ('e080e0008000', 6), '0X1912': ('02', 1), '0X1914': ('8000', 2), '0X1918': ('8000', 2), '0X1928': ('c0c0', 2)}
    check('all selected FRC P5 oracles answer', all((fo[k]['status'] == 'positive' and (fo[k]['hex'], fo[k]['length']) == v for k, v in expected_oracles.items())))
    bo = art['brake_read_only_oracles']
    check('Brake 0x102F answers', bo['0x102F'] == {'hex': 'f700fd007c00a9000000', 'length': 10, 'status': 'positive'})
    check('Brake 0x107E rejected in default', bo['0x107E_default']['status'] == 'negative_or_timeout')
    check('Brake 0x107E rejected in extended and ECU returned default', bo['0x107E_extended']['extended_session'] == 'positive' and bo['0x107E_extended']['status'] == 'negative_or_timeout' and (bo['0x107E_extended']['returned_default'] is True))
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
    dist = sync['distance_state']
    check('distance DID 1912 validated twice', dist['isolated_transition'] == '03->04' and dist['synchronized_transition'] == '04->01' and (dist['frc_did'] == '0x1912'))
    c251 = dist['candidate_can_carriers']['0x251/8']
    c5af = dist['candidate_can_carriers']['0x5AF/32']
    check('0x251 distance candidate exact', c251['bus'] == 1 and c251['byte_index'] == 5 and (c251['before'] == 136) and (c251['after'] == 40) and (c251['payload_before'] == 'a00000488088a080') and (c251['payload_after'] == 'a00000488028a080') and (0 < c251['latency_from_1912_change_ms'] < 20))
    check('0x5AF distance candidate exact', c5af['bus'] == 1 and c5af['byte_index'] == 24 and (c5af['before'] == 240) and (c5af['after'] == 228) and (c5af['xor'] == 20) and (0 < c5af['latency_from_1912_change_ms'] < 20))
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
    REPO = REPO_ROOT
    RAW = REPO / 'targets/camry-2026/raw-20260826'
    ART = REPO / 'data/generated/camry_2026_ready_gear.json'
    BUILD = REPO / 'tools/targets/camry/analysis/analyze_camry_2026_ready_gear.py'

    def sha(path: Path) -> str:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    art = json.loads(ART.read_text())
    print('== source provenance ==')
    expected = {'camry_ready_gear_capture.py': (774, 'b79857ffa38f7ad94030313a5c5609cbd3e35178c31f8d72fa72a912c20740fb'), 'camry_ready_gear_20260826.json.gz': (1660906, '379ec28fba65191d2898ebb156fe83e2e8e59c38bbf5fcfb7166ec9ff32c3889'), 'camry_b_capture.py': (755, '2d72ec4ace3ab01ecae440d8d4f8324e3d7166a15f9bdd868d6a5c2d2a2ae153'), 'camry_ready_b_20260826.json.gz': (715102, '7bae994dea1caff06d8f31f58558f67d646da38bd9531557875858eb33fa4db3')}
    for name, (size, digest) in expected.items():
        p = RAW / name
        check(f'{name} exact tracked identity', p.stat().st_size == size and sha(p) == digest)
    for name, raw_size, raw_sha in (('camry_ready_gear_20260826.json.gz', 16814179, 'c03524036e531c22d60646be65c57b85fb1e9fb0c8b5d2c50e4b3055dbecef52'), ('camry_ready_b_20260826.json.gz', 7278095, '733b7a6fe9aa2f12401077489d662657a5abd20588c1d53a600ffbeec41b40f2')):
        raw = gzip.decompress((RAW / name).read_bytes())
        check(f'{name} uncompressed identity', len(raw) == raw_size and hashlib.sha256(raw).hexdigest() == raw_sha)
    print('\n== deterministic artifact ==')
    with tempfile.TemporaryDirectory() as td:
        out = Path(td) / 'camry-ready-gear.json'
        proc = subprocess.run([sys.executable, str(BUILD), '--out', str(out)], cwd=REPO, capture_output=True, text=True, check=False)
        check('READY/gear analyzer succeeds', proc.returncode == 0, proc.stderr[-300:])
        check('READY/gear artifact regenerates exactly', proc.returncode == 0 and out.read_bytes() == ART.read_bytes())
    print('\n== controlled Ready transition ==')
    ready = art['ready_status']
    check('51E Ready sequence is 0->1', ready['first_run_sequence'] == [0, 1])
    check('51E transition bytes/timing exact', ready['transition'] == [{'payload': '0000640000000000', 'seconds': 0.070314, 'value': 0}, {'payload': '80006e0000000000', 'seconds': 5.213083, 'value': 1}])
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
    print('\n== stationary corroboration ==')
    for name, count in (('nrtd_to_ready_gear', 6187), ('ready_b', 2677)):
        wheels = art['captures'][name]['0x0AA_stationary_corroboration']
        check(f'{name} stationary wheel carrier exact', wheels['frame_count'] == count and wheels['unique_payloads'] == ['1a6f1a6f1a6f1a6f'])
_section_camry_2026_ready_gear()
print()

print("== camry 2026 cruise/lateral edge census ==")
def _section_camry_2026_cruise_lta_edges():
    import json
    import subprocess
    import sys
    import tempfile
    from pathlib import Path
    REPO = REPO_ROOT
    ART = REPO / 'data/generated/camry_2026_cruise_lta_edge_census.json'
    BUILD = REPO / 'tools/targets/camry/analysis/analyze_camry_2026_cruise_lta_edges.py'

    with tempfile.TemporaryDirectory() as td:
        out = Path(td) / 'edges.json'
        proc = subprocess.run([sys.executable, str(BUILD), '--out', str(out)], cwd=REPO,
                              capture_output=True, text=True, check=False)
        check('cruise/lateral edge analyzer succeeds', proc.returncode == 0, proc.stderr[-300:])
        check('cruise/lateral edge artifact regenerates exactly', proc.returncode == 0 and out.read_bytes() == ART.read_bytes())

    art = json.loads(ART.read_text())
    combined = art['combined']
    check('existing logs machine-recover sustained cruise operation',
          combined['cruise_rising_edge_count'] == 6 and combined['cruise_rises_with_recent_main'] == 6 and
          combined['cruise_active_duration_s'] > 150 and combined['cruise_active_incoming_frame_count_all_buses'] > 500000)
    check('0x08A byte10 independently joins set speed to wheel speed',
          combined['max_abs_set_speed_vs_wheel_kph_at_cruise_rise'] <= 1.4)
    check('B6 remains zero throughout recovered cruise-active intervals', combined['b6_during_cruise_active_all_buses'] == 0)

    a = art['drives']['drive_a']
    b = art['drives']['drive_b']
    a_edges = [e for e in a['cruise_active']['control_edges'] if e['button'] == 'SET_MINUS']
    b_res = [e for e in b['cruise_active']['control_edges'] if e['button'] == 'RES_PLUS']
    b_cancel = [e for e in b['cruise_active']['control_edges'] if e['button'] == 'CANCEL' and e['a8_after_b3'] == 0]
    check('SET- decrements 0x08A set-speed byte in first drive',
          [(e['a8_before_b10'], e['a8_after_b10']) for e in a_edges] == [(42, 40), (40, 39)])
    check('RES+ increments 0x08A set-speed byte in confirmation drive',
          [(e['a8_before_b10'], e['a8_after_b10']) for e in b_res] == [(66, 67), (67, 68), (68, 70)])
    check('CANCEL clears recovered cruise state', len(b_cancel) >= 2 and all(e['a8_after_b10'] == 0 for e in b_cancel))

    lat = art['combined']
    check('existing logs contain long structurally distinct lateral/HUD candidate intervals',
          lat['lateral_hud_candidate_duration_s'] > 70 and lat['lateral_hud_candidate_incoming_frame_count_all_buses'] > 230000)
    check('B6 also remains zero throughout lateral/HUD candidate intervals',
          lat['b6_during_lateral_hud_candidate_all_buses'] == 0)
    latch = combined['eps_latch_inputs']
    check('exact-F33 moving-mode gate 0x0D5 s211 is set throughout cruise AND lateral/HUD strata in both drives',
          latch['d5_s211_set_fraction_cruise_min'] == 1.0 and latch['d5_s211_set_fraction_lateral_min'] == 1.0)
    check('exact-F33 moving-mode clear gate 0x0D7 s243 is never set in either drive',
          latch['d7_s243_set_fraction_max'] == 0)
    check('0x0D5 s213 (FEBEC5FC/FEBEC5EC magnitude source) is identically zero in both drives',
          latch['d5_s213_abs_max'] == 0)
    for drv in (a, b):
        li = drv['eps_latch_inputs']['0x0D5']
        check(f"{drv['source']['file'].split('/')[-1]}: s212 stays far below the FEBEC602 monitor threshold inside every stratum",
              max(abs(li[s]['s212_min']) for s in ('all', 'cruise_active', 'lateral_hud_candidate')) <= 5 and
              max(abs(li[s]['s212_max']) for s in ('all', 'cruise_active', 'lateral_hud_candidate')) <= 11)
    a_lat = a['lateral_hud_candidate']['intervals']
    b_lat = b['lateral_hud_candidate']['intervals']
    check('lateral/HUD state is mirrored on 0x081 and dominated by one 0x412 payload',
          len(a_lat) == len(b_lat) == 1 and
          a_lat[0]['id081_b13_match_fraction'] > 0.998 and b_lat[0]['id081_b13_match_fraction'] > 0.999 and
              a_lat[0]['hud_0x412_modal_payload'] == b_lat[0]['hud_0x412_modal_payload'] == '1400004401ee9307' and
              a_lat[0]['hud_0x412_modal_fraction'] > 0.94 and b_lat[0]['hud_0x412_modal_fraction'] > 0.98)
_section_camry_2026_cruise_lta_edges()
print()

print(f"\n== RESULT: {passed} passed, {failed} failed ==")
raise SystemExit(1 if failed else 0)
