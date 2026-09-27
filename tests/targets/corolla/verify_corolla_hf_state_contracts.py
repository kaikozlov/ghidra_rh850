#!/usr/bin/env python3
"""Portable Corolla H/F state pins: non-steering engagement state, fault state contract, and remaining status contract.

Domain split; assertions and helpers are carried over verbatim.
"""
from __future__ import annotations
from tools import REPO_ROOT
ROOT = REPO = REPO_ROOT
passed = failed = 0

def check(name, cond, detail=''):
    global passed, failed
    ok = bool(cond)
    passed += int(ok)
    failed += int(not ok)
    suffix = f' ({detail})' if detail else ''
    print(f"[{('PASS' if ok else 'FAIL')}] {name}{suffix}")
print()
print('== corolla hf nonsteering engagement state ==')

def _section_corolla_hf_nonsteering_engagement_state():
    import hashlib
    import json
    REPO = REPO_ROOT
    ART = REPO / 'data/generated/corolla_hf_nonsteering_engagement_state.json'
    BUILD = REPO / 'tools/targets/corolla/builders/build_corolla_hf_nonsteering_engagement_state.py'
    IMAGE = REPO / 'community/albinoelephant/normalized/8965H1202000_CodeFlash.bin'
    ENG = REPO / 'data/generated/corolla_8965H1202000_nonsteering_engagement_decompiler_evidence.json'
    TECH = REPO / 'data/generated/techstream_v18/tss3_cruise_engagement_semantics.json'

    def sha(data: bytes) -> str:
        return hashlib.sha256(data).hexdigest()
    art = json.loads(ART.read_text())
    eng = json.loads(ENG.read_text())
    tech = json.loads(TECH.read_text())
    image = IMAGE.read_bytes()
    print('== deterministic synthesis ==')
    check('H/F application identity retained', art['software_family'] == {'h': '8965H1202000', 'f': '8965F1208000', 'application_byte_identical': True})
    for row in eng['functions']:
        start = int(row['entry'], 16)
        check(f"raw H body {row['entry']}", sha(image[start:start + row['body_size']]) == row['body_sha256'])
    check('compact H engagement evidence is image-bound', eng['image']['sha256'] == sha(image))
    print('\n== exact Ready Status wire join ==')
    ready = art['ready_status']
    check('Ready Status carrier is exact H 0x51E B0[7]', ready['classification'] == 'wire field closed' and ready['can_id'] == '0x51E' and (ready['length'] == 8) and (ready['h_rx_descriptor_index'] == 24) and (ready['h_signal_id'] == 154) and (ready['wire'] == 'B0[7]'))
    check('Ready Status exact source chain reaches DID1033', ready['source_chain'] == ['0x51E B0[7]', '0xFEBE7D1B', '0xFEBEF052', '0xFEBEB5A8', '0xFEBEE811', 'DID 0x1033'] and ready['techstream'] == {'name': 'Ready Status', 'did': '0x1033', 'boolean_domain': [0, 1]})
    check('Ready Status copy provenance does not claim an exclusive writer', ready['operational_copy_sites'] == ['0x000BAB58', '0x000BAC16'])
    check('public route corroborates Ready=1', ready['route_corroboration']['public_2023'] == {'frames': 59, 'values': [1], 'payloads': ['8000004500000000']})
    check('Span route corroborates Ready=1', ready['route_corroboration']['span_2025'] == {'frames': 60, 'values': [1], 'payloads': ['86001a0000000000']})
    print('\n== generation-native gear state ==')
    gear = art['gear']
    h127 = gear['exact_h_0x127']
    check('exact H retains 0x127/8 as Rx PDU20', h127['can_id'] == '0x127' and h127['length'] == 8 and h127['h_rx_descriptor_index'] == 20)
    check('exact H generated signal ownership is 123..132', h127['h_signal_ids'] == list(range(123, 133)))
    check('exact H scalar extraction positions are regenerated', h127['h_scalar_extractions'] == [{'signal_id': 123, 'wire': 'B0[7:2]', 'length': 6}, {'signal_id': 125, 'wire': 'B1[3]', 'length': 1}, {'signal_id': 129, 'wire': 'B3/B4 signed11 domain', 'length': 11}])
    span127 = gear['span_0x127']
    check('Span 0x127 raw3 is independently D-corroborated', span127['frames'] == span127['checksum_valid'] == 3662 and span127['raw_values'] == [3] and span127['decoded_values'] == ['D'] and all(x in span127['decode_basis'] for x in ('0x3BF', '0x10', 'D')))
    g3 = gear['generation_native_0x3bf']
    check('public route directly closes 0x3BF P/R/D', g3['public_2023']['direct_observed_labels'] == {'0x10': 'D', '0x40': 'R', '0x80': 'P'} and [x['raw'] for x in g3['public_2023']['transitions']] == [128, 64, 16])
    check('Span repeats 0x3BF D on moving 2025 Corolla', g3['span_2025']['raw_values'] == [16] and g3['span_2025']['direct_decoded_values'] == ['D'])
    check('0x3BF N boundary is one-hot plus GTS corroboration', g3['enum'] == {'0x10': 'D', '0x20': 'N', '0x40': 'R', '0x80': 'P'})
    check('0x2A1 independently corroborates route P/R/D transitions', gear['corroborating_0x2a1']['direct_observed_labels'] == {'0x01': 'P', '0x02': 'R', '0x04': 'D'} and [x['raw'] for x in gear['corroborating_0x2a1']['transitions']] == [1, 2, 4])
    check('GTS+ P5 hybrid preserves P/R/N/D/B ordering', gear['gts_p5_hybrid_ordering'] == {'source': 'HV_P5.ddb', 'name': 'Shift Position', 'pattern_display': {'0': 'P', '2': 'R', '4': 'N', '6': 'D', '8': 'B'}})

    print('\n== generation-native cruise state ==')
    cruise = art['cruise']
    c176 = cruise['retained_wire_prior_art']['0x176']
    check('0x176 survives both captures with valid checksum', c176['public_2023_frames'] == 1855 and c176['span_2025_frames'] == 1890 and c176['checksums_all_valid'] is True)
    check('old 0x176 active/state is explicitly rejected', c176['legacy_cruise_active_values'] == [False] and c176['legacy_cruise_state_values'] == [0])
    c24d = cruise['retained_wire_prior_art']['0x24D']
    check('0x24D survives but old switch fields remain inactive', c24d['public_2023_frames'] == 59 and c24d['span_2025_frames'] == 60 and all(v == [0] for v in c24d['legacy_button_fields'].values()))
    check('old cruise replacement IDs absent in both captures', cruise['legacy_ids_absent_in_both_captures'] == ['0x177', '0x1A2', '0x1D3', '0x399'])
    native = cruise['native_wire_mapping']
    check('0x08A native available/enabled mapping is closed', 'ACC_STATE' in native['available'] and 'B22 bit0x10' in native['enabled'] and native['span_0x08a']['acc_engaged_frames'] == 37 and native['span_0x08a']['acc_disengaged_frames'] == 2363)
    check('core cruise fields are closed while optional fields remain open', cruise['wire_mapping_status']['cruise_available'].startswith('closed') and cruise['wire_mapping_status']['cruise_enabled'].startswith('closed') and cruise['wire_mapping_status']['cruise_standstill'].startswith('closed') and cruise['wire_mapping_status']['set_speed'].startswith('closed') and cruise['wire_mapping_status']['follow_distance'].startswith('optional/open'))

    print('\n== Toyota P5 engagement diagnostic oracles ==')
    rows = {x['name']: x for x in cruise['techstream_p5_frc_oracles']}
    for name, data_id, bits in (('Cruise Control Permission Flag', '0x1905', [8, 8]), ('Main Switch Recognition Flag', '0x1906', [8, 8]), ('ACC Not Available Icon Lighting Request Flag', '0x1906', [40, 40]), ('ACC Control in Operation Flag', '0x1914', [8, 8]), ('Set Vehicle Interval Time', '0x1912', [0, 7]), ('Current Vehicle Speed', '0x1901', [0, 31]), ('Memory Vehicle Speed', '0x1901', [32, 63])):
        check(f'FRC oracle {name}', rows[name]['primary_data_id'] == data_id and rows[name]['bit_range'] == bits)
    check('permission dictionary exact', rows['Cruise Control Permission Flag']['pattern_values'] == {'0': 'Cruise Control Not Allowed', '1': 'Cruise Control Allowed'})
    check('ACC-operation dictionary exact', rows['ACC Control in Operation Flag']['pattern_values'] == {'0': 'Cruise Control Not in Operation', '1': 'Cruise Control in Operation'})
    check('set-speed oracle is physical km/h', rows['Memory Vehicle Speed']['conversion']['unit'] == 'km/h' and rows['Memory Vehicle Speed']['conversion']['mul'] == rows['Memory Vehicle Speed']['conversion']['div'] == 1)
    check('follow-distance dictionary exact', rows['Set Vehicle Interval Time']['pattern_values'] == {'1': 'Set Vehicle Interval Time4', '2': 'Set Vehicle Interval Time3', '3': 'Set Vehicle Interval Time2', '4': 'Set Vehicle Interval Time1'})

    print('\n== implementation boundary ==')
    safe = art['implementation_consequence']['safe_now']
    unsafe = art['implementation_consequence']['not_safe_yet']
    check('Ready input is safe for inspection', any('0x51E B0[7]' in x for x in safe))
    check('gear carriers are safe for production CarState', any('0x127 GEAR_PACKET_HYBRID' in x and '0x3BF' in x for x in safe))
    check('native cruise available/enabled/standstill is safe', any('0x08A ACC_STATE/B22' in x and 'standstill' in x for x in safe))
    check('retained set speed is safe with native floor', any('0x251 B2' in x and '19-mph' in x for x in safe))
    check('fault-policy overreach remains prohibited', any('temporary/permanent' in x and 'fault' in x for x in unsafe))

_section_corolla_hf_nonsteering_engagement_state()
print()
print('== corolla hf fault state contract ==')

def _section_corolla_hf_fault_state_contract():
    import json
    REPO = REPO_ROOT
    ART = REPO / 'data/generated/corolla_hf_fault_state_contract.json'
    TOOL = REPO / 'tools/targets/corolla/builders/build_corolla_hf_fault_state_contract.py'
    d = json.loads(ART.read_text())
    check('exact H/F software family', d['software_ids'] == ['8965H1202000', '8965F1208000'])
    check('0x394 geometry exact', d['wire']['can_id'] == '0x394' and d['wire']['length'] == 3 and (len(d['wire']['state_table_rows']) == 17))
    check('complete DEM class census exact', d['dem']['class_counts'] == {'0x01': 8, '0x02': 34, '0x04': 1, '0x08': 1, '0x0F': 1, '0x10': 173, '0x20': 16, '0x40': 1, '0x80': 7} and sum(d['dem']['class_counts'].values()) == 242)
    ct = d['dem']['class_to_state']
    check('class2/4 paired-state mapping exact', ct['0x02']['states'] == [6, 7] and ct['0x04']['states'] == [8, 9])
    check('direct class branches exact', ct['0x10']['states'] == [10] and ct['0x20']['states'] == [11] and (ct['0x40']['states'] == [12]) and (ct['0x08']['states'] == [13]) and (ct['0x0F']['states'] == [14]))
    check('class80 is bounded general fallback', ct['0x80']['states'] == [16])
    check('classF0 supported but absent in event table', '0xF0' not in d['dem']['class_counts'])
    check('class01 populated but not accumulator-consumed', ct['0x01']['states'] == [])
    a = d['aging']
    check('paired-state aging constants exact', a['class2_primary_age'] == 200 and a['class4_primary_age'] == 200 and (a['class2_class4_secondary_age'] == 600) and (a['primary_clear_enable_age'] == 17736))
    n = d['named_dtc_families']
    check('named DTC family cardinalities exact', len(n['class_0x01_no_direct_394_accumulator_effect']) == 6 and len(n['class_0x02_states_6_7']) == 11 and (len(n['class_0x10_state_10']) == 50) and (len(n['class_0x20_state_11']) == 6))
    check('class10 includes Brake missing-message DTC', any((x['code'] == 'U012987' and x['failure'] == 'Missing Message' for x in n['class_0x10_state_10'])))
    check('class20 includes steering-angle comm incompatibility family', any((x['code'] == 'U012687' for x in n['class_0x20_state_11'])) and any((x['code'] == 'U032857' for x in n['class_0x20_state_11'])))
_section_corolla_hf_fault_state_contract()
print()
print('== corolla hf remaining status contract ==')

def _section_corolla_hf_remaining_status_contract():
    import hashlib, json
    REPO = REPO_ROOT
    ART = REPO / 'data/generated/corolla_hf_remaining_status_contract.json'
    EVID = REPO / 'data/generated/corolla_8965H1202000_remaining_status_decompiler_evidence.json'
    TOOL = REPO / 'tools/targets/corolla/builders/build_corolla_hf_remaining_status_contract.py'
    IMAGE = REPO / 'community/albinoelephant/normalized/8965H1202000_CodeFlash.bin'
    d = json.loads(ART.read_text())
    e = json.loads(EVID.read_text())
    image = IMAGE.read_bytes()
    check('exact H/F software family', d['software_ids'] == ['8965H1202000', '8965F1208000'])
    check('all promoted bodies match exact H bytes', all((hashlib.sha256(image[int(x['entry'], 16):int(x['entry'], 16) + x['body_size']]).hexdigest() == x['body_sha256'] for x in e['functions'])))
    b = d['can_0x030_b6_bit1']
    check('B6[1] source is Q-axis actual current', b['wire'] == '0x030 B6[1]' and b['chain'][0] == 'FEBE6BAE Motor Actual Current (Q Axis)')
    check('B6[1] full threshold/debounce chain retained', all((x in ' '.join(b['chain']) for x in ('FEBEEC0C', 'FEBEAFC4', 'FEBEB64D', 'FEBEB64C', 'FEBEE848', 'FEBE7DB3'))))
    check('exact-H detector calibration exact', b['calibration']['feature_flag'] == 90 and b['calibration']['threshold_a'] == 5120 and (b['calibration']['threshold_b'] == 2560) and (b['calibration']['debounce_count'] == 0))
    check('Span is kept cross-specimen only', b['span_observation']['values'] == [0, 1])
    f = d['can_0x351_force7']
    check('force7 condition exact', f['condition'] == '(FEBE65E4 & 0x0003) != 0 AND FEBE7E13 != 0')
    check('force7 status-bitmap bits exact', f['status_bitmap_side']['bits_used'] == [0, 1] and 'FEBE6FB4' in ' '.join(f['status_bitmap_side']['chain']))
    check('force7 24-record aggregate bit exact', f['record_aggregate_side']['record_count'] == 24 and f['record_aggregate_side']['bit_used'] == 15)
    check('force7 remains semantically bounded', 'does not assign Toyota names' in f['status_bitmap_side']['boundary'] and 'not recovered' in f['record_aggregate_side']['boundary'])
_section_corolla_hf_remaining_status_contract()
print()
print(f'\n== RESULT: {passed} passed, {failed} failed ==')
raise SystemExit(1 if failed else 0)
