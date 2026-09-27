#!/usr/bin/env python3
"""Tracked 2026 Camry relay-correct drive capture pins and FRC LTA synchronized capture tooling.

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

print("== camry 2026 relay-correct capture ==")
def _section_camry_2026_relay_correct_capture():
    import hashlib
    import json
    import subprocess
    import sys
    import tempfile
    from pathlib import Path
    REPO = REPO_ROOT
    RAW = REPO / 'targets/camry-2026/raw-20260827'
    ART = REPO / 'data/generated/camry_2026_relay_correct_capture.json'
    GTS_TOPOLOGY = REPO / 'data/generated/gtsplus_2026/camry_8965F3307000_emps_semantics.json'
    BUILD = REPO / 'tools/targets/camry/analysis/analyze_camry_2026_relay_capture.py'

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

    print('\n== deterministic artifact ==')
    with tempfile.TemporaryDirectory() as td:
        out = Path(td) / 'relay.json'
        proc = subprocess.run([sys.executable, str(BUILD), '--out', str(out)], cwd=REPO, capture_output=True, text=True, check=False)
        check('relay analyzer succeeds', proc.returncode == 0, proc.stderr[-300:])
        check('relay artifact regenerates exactly', proc.returncode == 0 and out.read_bytes() == ART.read_bytes())
    art = json.loads(ART.read_text())

    print('\n== physical repin topology ==')
    nrtd = art['post_repin_nrtd']
    check('NRTD bus0/bus2 exact duplicated sequence', nrtd['bus0_bus2_sequence_identical'] is True and nrtd['frames_by_bus'] == {'0': 13910, '1': 3938, '2': 13910})
    check('NRTD repin census is 153/22/153', nrtd['id_dlc_count_by_bus'] == {'0': 153, '1': 22, '2': 153})
    for addr, expected_count in (('0x00F/8', 100), ('0x025/32', 1000), ('0x030/32', 1000), ('0x0D7/32', 500)):
        check(f'{addr} moved to relay pair', nrtd['selected_counts'][addr] == {'0': expected_count, '1': 0, '2': expected_count})
    ready = art['post_repin_ready']
    check('READY keeps same 0/2-vs-1 topology', ready['id_dlc_count_by_bus'] == {'0': 165, '1': 22, '2': 165})
    check('READY bit is present on both relay sides', ready['ready_values_bus0'] == [1] and ready['selected_counts']['0x51E/8'] == {'0': 9, '1': 0, '2': 9})

    print('\n== current-GTS+ physical-network join ==')
    gt = json.loads(GTS_TOPOLOGY.read_text())['current_camry_can_topology']
    crit = gt['critical_placement']
    check('Toyota current Camry topology separates camera Bus1 from Brake/EPS Bus4',
          crit['front_camera_module']['bus_name'] == 'Bus 1' and
          crit['skid_control_abs_vsc_trac']['bus_name'] == 'Bus 4' and
          crit['power_steering_eps']['bus_name'] == 'Bus 4')
    check('exact F33 030/B6 share the single normal application CAN controller surface',
          gt['exact_f33_channel_join']['canif_controller_count_byte']['value'] == 1 and
          gt['exact_f33_channel_join']['normal_tx_ids'][0] == '0x030' and
          gt['exact_f33_channel_join']['b6_rule_can_id'] == '0x0B6')
    check('repinned CAN0/CAN2 carries the Toyota Bus4 EPS surface',
          nrtd['selected_counts']['0x030/32'] == {'0':1000,'1':0,'2':1000} and
          nrtd['selected_counts']['0x0D7/32'] == {'0':500,'1':0,'2':500} and
          nrtd['selected_counts']['0x025/32'] == {'0':1000,'1':0,'2':1000} and
          gt['component_placements_identical_across_variants'] is True)

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
    availability = drive['cruise_main_availability_lifecycle']
    check('0x251 B1[4] has exactly one retained rise and no fall in the relay drive',
          availability['rising_edges'] == [{'from': 0, 'seconds': 21.147887, 'segment': 4, 'to': 1}] and
          availability['falling_edges'] == [])
    check('0x251 B1[4] stays high through the later MAIN-off lifecycle',
          availability['segments']['4']['last'] == 1 and availability['segments']['5']['first'] == 1 and
          availability['segments']['5']['last'] == 1)
    op_edges = availability['main_operation_edges']
    check('validated MAIN pulses exercise two operation-latch activations and two deactivations',
          [(x['segment'], x['operation_from'], x['operation_to']) for x in op_edges] ==
          [(4, 0, 1), (4, 1, 0), (5, 0, 1), (5, 1, 0)])
    check('0x251 availability remains high at both true MAIN deactivation edges',
          all(x['availability_at_or_before_operation_edge'] == 1 for x in op_edges if x['operation_from'] == 1 and x['operation_to'] == 0))
    check('same-car 0x0FE join sees SET- interaction in segment 5', switches['SET_MINUS']['5'] == [
        {'end_s': 19.64854, 'frames': 5, 'start_s': 19.526293},
        {'end_s': 20.159219, 'frames': 3, 'start_s': 20.097979},
    ])
    check('raw relay artifact retains structural 0x08A transition segments', set(drive['structural_0x08A_transitions']) == {'4', '5'})

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
    check('raw confirmation artifact preserves 0x08A transition segments', set(confirm['structural_0x08A_transitions']) == {'18', '19', '20', '21'})
    combined = art['combined_route_evidence']
    check('two drives total 19 segments / 3.574M incoming frames / zero B6', combined == {'b6_any_bus_any_length_count': 0, 'frame_count': 3574703, 'segment_count': 19})

_section_camry_2026_relay_correct_capture()
print()


print("== camry FRC LTA synchronized capture tooling ==")
def _section_camry_frc_lta_capture_tool():
    import io
    import json
    import tempfile
    from pathlib import Path
    from types import SimpleNamespace

    import tools.targets.camry.analysis.analyze_camry_frc_lta_capture as analyze
    import tools.targets.camry.live.camry_frc_lta_capture as cap
    import tools.targets.camry.extract.extract_camry_frc_lta_rlog as rlog_extract

    p = cap.plan()
    check('FRC LTA tool is read-only and pins exact 1601 request',
          p['tx'] == '0x792' and p['rx'] == '0x79A' and p['did'] == '0x1601' and
          p['request_frame'] == '0322160100000000' and p['companion_did'] == '0x1914' and
          p['companion_request_frame'] == '0322191400000000' and p['vehicle_control_tx'] is False and
          p['flash_write'] is False and p['security_access'] is False and p['routine_control'] is False)
    parsed = cap.parse_1601_frame(bytes.fromhex('0762160101020304'))
    check('FRC 1601 positive response maps exact four GTS+ condition bytes', parsed == {
        'status': 'positive', 'raw': '01020304', 'lta_switch_condition': 1,
        'lta_control_condition': 2, 'hands_off_customize_condition': 3,
        'hands_off_control_condition': 4, 'lta_switch_label': 'ON',
        'lta_control_label': None, 'hands_off_customize_label': None,
        'hands_off_control_label': None, 'lta_enabled_oracle': False,
    })
    check('FRC 1601 negative response is retained without decoding state',
          cap.parse_1601_frame(bytes.fromhex('037f223100000000')) == {
              'status': 'negative', 'nrc': 0x31, 'raw_frame': '037f223100000000'})
    check('FRC 1914 response maps exact ACC-in-operation bit and OEM label',
          cap.parse_1914_frame(bytes.fromhex('0562191480010000')) == {
              'status': 'positive', 'raw': '8001', 'acc_control_in_operation': 1,
              'acc_control_label': 'Cruise Control in Operation', 'acc_in_operation_oracle': True})
    buf = io.BytesIO()
    cap.write_canbin_header(buf)
    cap.write_canbin_record(buf, 123, 0, 0x0B6, bytes(range(32)))
    cap.write_canbin_record(buf, 456, 1, 0x18A, bytes(range(64)))
    buf.seek(0)
    check('compact CAN capture format round-trips classic/FD records', list(cap.iter_canbin_records(buf)) == [
        (123, 0, 0x0B6, bytes(range(32))),
        (456, 1, 0x18A, bytes(range(64))),
    ])
    check('direct-Panda fallback pins the already-proved FRC bus-0 route', p['diag_bus'] == 0)
    with tempfile.TemporaryDirectory() as td:
        capture = Path(td)
        (capture / 'metadata.json').write_text(json.dumps({
            'schema': 'camry-frc-lta-capture-v1', 'diag_bus': 0, 'duration_s': 1.0,
            'files': {'can': 'can.bin', 'oracle': 'oracle.ndjson'},
        }))
        oracle_rows = [
            {'type':'response','status':'positive','did':'0x1601','t_ns':1_000_000_000,'raw':'01000000',
             'lta_switch_condition':1,'lta_control_condition':0,'hands_off_customize_condition':0,
             'hands_off_control_condition':0,'lta_switch_label':'ON','lta_control_label':'LTA Enabled',
             'hands_off_customize_label':'OFF','hands_off_control_label':'Hands-Off Enabled','lta_enabled_oracle':True},
            {'type':'response','status':'positive','did':'0x1914','t_ns':1_010_000_000,'raw':'8001',
             'acc_control_in_operation':1,'acc_control_label':'Cruise Control in Operation','acc_in_operation_oracle':True},
            {'type':'response','status':'positive','did':'0x1601','t_ns':1_100_000_000,'raw':'01000000',
             'lta_switch_condition':1,'lta_control_condition':0,'hands_off_customize_condition':0,
             'hands_off_control_condition':0,'lta_switch_label':'ON','lta_control_label':'LTA Enabled',
             'hands_off_customize_label':'OFF','hands_off_control_label':'Hands-Off Enabled','lta_enabled_oracle':True},
            {'type':'response','status':'positive','did':'0x1914','t_ns':1_110_000_000,'raw':'8001',
             'acc_control_in_operation':1,'acc_control_label':'Cruise Control in Operation','acc_in_operation_oracle':True},
            {'type':'response','status':'positive','did':'0x1601','t_ns':1_200_000_000,'raw':'01010000',
             'lta_switch_condition':1,'lta_control_condition':1,'hands_off_customize_condition':0,
             'hands_off_control_condition':0,'lta_switch_label':'ON','lta_control_label':'LTA Disabled',
             'hands_off_customize_label':'OFF','hands_off_control_label':'Hands-Off Enabled','lta_enabled_oracle':False},
        ]
        oracle_rows.insert(1, oracle_rows[0] | {'bus': 2})
        oracle_rows.insert(3, oracle_rows[2] | {'bus': 2})
        (capture / 'oracle.ndjson').write_text(''.join(json.dumps(row) + '\n' for row in oracle_rows))
        with (capture / 'can.bin').open('wb') as stream:
            cap.write_canbin_header(stream)
            cap.write_canbin_record(stream, 1_020_000_000, 0, 0x00F, bytes(8))
            cap.write_canbin_record(stream, 1_030_000_000, 0, 0x0D7, bytes(32))
            cap.write_canbin_record(stream, 1_040_000_000, 0, 0x0AA, bytes.fromhex('1e571e571e571e57'))
            cap.write_canbin_record(stream, 1_050_000_000, 0, 0x030, bytes(32))
            cap.write_canbin_record(stream, 1_070_000_000, 1, 0x18A, bytes(64))
        summary = analyze.analyze(capture)
        check('offline analyzer intersects stable LTA-enabled + ACC-operating oracle intervals',
              summary['oracle']['lta_0x1601']['positive_sample_count'] == 3 and
              summary['oracle']['acc_0x1914']['positive_sample_count'] == 2 and
              summary['oracle']['lta_0x1601']['stable_lta_enabled_duration_s'] == 0.1 and
              abs(summary['oracle']['combined_operating_context']['stable_lta_enabled_plus_acc_operating_duration_s'] - 0.09) < 1e-9 and
              summary['can']['operating_context_selected_counts']['operational']['bus0:0x030/32'] == 1 and
              summary['can']['operating_context_selected_counts']['operational']['bus0:0x0D7/32'] == 1 and
              summary['can']['b6_during_stable_lta_enabled_plus_acc_operating'] == 0 and
              summary['can']['wheel_speed_kph_during_operating_context']['moving_over_2kph_sample_count'] == 1 and
              summary['discriminator']['strong_zero_b6_operating_context'] is True)

    class FakeEvent:
        def __init__(self, kind, t_ns, frames):
            self._kind = kind
            self.logMonoTime = t_ns
            self.can = frames if kind == 'can' else []
            self.sendcan = frames if kind == 'sendcan' else []
        def which(self):
            return self._kind

    def frame(bus, addr, data):
        return SimpleNamespace(src=bus, address=addr, dat=data)

    with tempfile.TemporaryDirectory() as td:
        reduced = Path(td) / 'reduced'
        events = [
            (26, FakeEvent('sendcan', 1_000_000_000, [frame(0, 0x792, cap.UDS_RDBI_REQUEST)])),
            (26, FakeEvent('can', 1_005_000_000, [frame(0, 0x79A, bytes.fromhex('0762160101000000'))])),
            (26, FakeEvent('sendcan', 1_010_000_000, [frame(0, 0x792, cap.ACC_OPERATION_RDBI_REQUEST)])),
            (26, FakeEvent('can', 1_015_000_000, [frame(0, 0x79A, bytes.fromhex('0562191480010000'))])),
            (26, FakeEvent('can', 1_030_000_000, [
                frame(0, 0x00F, bytes(8)),
                frame(0, 0x0D7, bytes(32)),
                frame(0, 0x0AA, bytes.fromhex('1e571e571e571e57')),
                frame(0, 0x030, bytes(32)),
                frame(1, 0x18A, bytes(64)),
            ])),
            (26, FakeEvent('sendcan', 1_100_000_000, [frame(0, 0x792, cap.UDS_RDBI_REQUEST)])),
            (26, FakeEvent('can', 1_105_000_000, [frame(0, 0x79A, bytes.fromhex('0762160101000000'))])),
            (26, FakeEvent('sendcan', 1_110_000_000, [frame(0, 0x792, cap.ACC_OPERATION_RDBI_REQUEST)])),
            (26, FakeEvent('can', 1_115_000_000, [frame(0, 0x79A, bytes.fromhex('0562191480010000'))])),
        ]
        meta = rlog_extract.reduce_events(
            events, reduced, sources=[{'segment': 26, 'size': 123, 'sha256': 'a' * 64}],
        )
        reduced_summary = analyze.analyze(reduced)
        check('loggerd reducer preserves only fixed FRC queries plus incoming CAN in analyzer-compatible shape',
              meta['diag_bus'] == 0 and
              meta['oracle_query_by_did'] == {'0x1601': 2, '0x1914': 2} and
              meta['oracle_positive_by_did'] == {'0x1601': 2, '0x1914': 2} and
              meta['b6_by_bus'] == {'0': 0, '1': 0, '2': 0} and
              reduced_summary['discriminator']['strong_zero_b6_operating_context'] is True)
    check('pandad process guard recognizes manager Python module and native process forms',
          cap.cmdline_is_pandad('/usr/bin/python3 -m openpilot.selfdrive.pandad.pandad') and
          cap.cmdline_is_pandad('/data/openpilot/openpilot/selfdrive/pandad/pandad') and
          not cap.cmdline_is_pandad('/usr/bin/python3 tools/targets/camry/live/camry_frc_lta_capture.py'))
_section_camry_frc_lta_capture_tool()
print()

print(f"\n== RESULT: {passed} passed, {failed} failed ==")
raise SystemExit(1 if failed else 0)
