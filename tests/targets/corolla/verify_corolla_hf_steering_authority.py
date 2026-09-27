#!/usr/bin/env python3
"""Portable Corolla H/F steering-authority pins: steering limits, cooperative authority wire visibility, and Panda lateral safety contract.

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
print('== corolla hf steering limits ==')

def _section_corolla_hf_steering_limits():
    import json
    ROOT = REPO_ROOT
    ART = ROOT / 'data/generated/corolla_hf_steering_limits.json'
    BUILDER = ROOT / 'tools/targets/corolla/builders/build_corolla_hf_steering_limits.py'
    PANDA = ROOT / 'data/generated/corolla_hf_panda_lateral_safety_contract.json'
    d = json.loads(ART.read_text())
    check('applies to exact H/F pair', d['applies_to'] == ['8965H1202000', '8965F1208000'])
    check('artifact is non-enabling', not d['status']['production_enable_authorized'] and (not d['static_conclusion']['production_enable_authorized']))
    check('promoted functions transfer exactly H/F', d['cross_variant']['all_promoted_function_bodies_h_f_identical'])
    check('promoted calibration bytes transfer exactly H/F', d['cross_variant']['all_promoted_calibration_bytes_h_f_identical'])
    check('runtime selected bank is low vehicle', '0x12960' in d['cross_variant']['runtime_selected_bank'] and 'selector 1' in d['cross_variant']['runtime_selected_bank'])
    check('compiled default bank is high', '0x1A960' in d['cross_variant']['compiled_default_bank'])
    c = d['command_limits']
    check('hard LTA absolute raw limit', c['b6_lta_absolute']['raw'] == 1745 and c['b6_lta_absolute']['bank_invariant'])
    check('hard LTA absolute physical limit', 99.99 < c['b6_lta_absolute']['deg'] < 100.0)
    check('target delta exact', c['b6_lta_delta']['raw_per_effective_sequence_gap'] == 78)
    check('target delta physical', 4.46 < c['b6_lta_delta']['deg_per_effective_sequence_gap'] < 4.48)
    check('target low-angle deadband exact', c['b6_lta_delta']['low_angle_deadband_raw'] == 87)
    check('low selected per-task slew exact', c['internal_lta_slew']['selected_low_doubled_domain_per_steering_task'] == 7 and c['internal_lta_slew']['selected_low_b6_counts_per_task'] == 3.5)
    check('high default per-task slew exact', c['internal_lta_slew']['high_default_doubled_domain_per_steering_task'] == 4 and c['internal_lta_slew']['high_default_b6_counts_per_task'] == 2.0)
    check('foreground tick now attached to per-task slew', c['internal_lta_slew']['foreground_tick_nominal_ms'] == 5.0 and c['internal_lta_slew']['wall_clock_rate_unconditional'] is False)
    check('conditional once-per-foreground slew rates are explicit', 40.0 < c['internal_lta_slew']['selected_low_deg_per_second_if_called_each_foreground_tick'] < 40.2 and 22.8 < c['internal_lta_slew']['high_default_deg_per_second_if_called_each_foreground_tick'] < 23.0)
    check('doubled target clamp equals B6 envelope', c['doubled_domain_absolute_clamp']['raw_internal'] == 3490 and c['doubled_domain_absolute_clamp']['equivalent_b6_raw'] == 1745.0)
    check('measured rate violation is strictly above 100', c['measured_steering_rate']['raw_abs_threshold'] == 100 and c['measured_steering_rate']['violation_relation'] == 'abs(rate_raw) > 100')
    check('rate persistence bank split', c['measured_steering_rate']['selected_low_persistence_cycles'] == 79 and c['measured_steering_rate']['high_default_persistence_cycles'] == 63)
    m = d['indexed_compensation']
    check('CBFCE map input remains physically unnamed', m['index_input'] == 'FEBEADF4' and m['index_physical_identity'] is None)
    check('four profile compensation maps recovered', len(m['maps']) == 4 and [x['offset'] for x in m['maps']] == ['0x768', '0x798', '0x7C8', '0x7F8'])
    check('selected vehicle compensation maps all zero at real points', all((x['selected_low_all_real_values_zero'] for x in m['maps'])))
    check('high default maps become nonzero at axis 7680', all((x['high_default_first_nonzero_axis'] == 7680 for x in m['maps'])))
    check('speed-dependent hard angle reduction not claimed', not d['static_conclusion']['speed_dependent_hard_angle_reduction_recovered'] and 'not a max-angle curve' in m['safety_conclusion'])
    p = d['internal_plausibility_and_fault_thresholds']
    check('tracking consistency raw window', p['tracking_consistency']['half_window_internal'] == 524 and p['tracking_consistency']['full_comparison_window_internal'] == 1048 and (p['tracking_consistency']['persistence_cycles'] == 40))
    check('tracking physical units bounded', p['tracking_consistency']['physical_units'] is None)
    check('instant internal-command threshold', p['internal_command_instant_monitor']['lta_threshold_raw'] == 512)
    check('instant internal-command persistence split', p['internal_command_instant_monitor']['selected_low_persistence_cycles'] == 79 and p['internal_command_instant_monitor']['high_default_persistence_cycles'] == 59)
    check('instant monitor explicitly not Q current', p['internal_command_instant_monitor']['not_measured_q_current'])
    check('persistent internal-command threshold', p['internal_command_persistent_inhibit']['lta_threshold_raw'] == 1280 and p['internal_command_persistent_inhibit']['persistence_cycles'] == 96)
    check('persistent monitor explicitly not Q current', p['internal_command_persistent_inhibit']['not_measured_q_current'])
    check('reconstruction validity bounds exact', p['reconstruction_validity_bounds']['raw_bounds'] == [80, 90, 512] and p['reconstruction_validity_bounds']['physical_units'] is None)
    check('extended inhibit counter exact', p['extended_inhibit_counter']['threshold'] == 15 and p['extended_inhibit_counter']['wall_clock_duration'] is None)
    check('controller error is saturation not Panda rejection', p['controller_error_saturation']['raw_internal'] == 18000)
    check('torque sensor fault constants retained raw', p['torque_sensor_fault_calibration']['raw_constants'] == {'0x0002B538': 2655, '0x0002B53C': 4233, '0x0002B546': 4091, '0x0002B548': 3341, '0x0002B54C': 1764})
    check('torque sensor fault constants not promoted to override', not p['torque_sensor_fault_calibration']['physical_driver_override_semantics'])
    t = d['driver_torque']
    check('driver torque acquisition clamp exact', t['acquisition_clamp_raw'] == 2109 and t['acquisition_raw_units_per_nm'] == 256)
    check('driver torque acquisition clamp physical', abs(t['acquisition_clamp_abs_nm'] - 8.23828125) < 1e-09)
    check('driver torque telemetry saturation exact', t['telemetry_saturation_abs_centi_nm'] == 1000 and t['telemetry_saturation_abs_nm'] == 10.0)
    check('driver torque override remains unset as Panda policy', t['override_abs_threshold_nm'] is None and (not t['supervisor_numeric_override_comparator_recovered']) and (not t['target_to_motor_physical_torque_comparator_recovered']) and ('Panda/openpilot' in t['policy_classification']))
    check('expanded physical torque census has zero C8xxx-CExxx consumers', len(t['direct_source_snapshot_reference_entries']) == 13 and t['direct_source_snapshot_refs_inside_c8xxx_cexxx_control_cone'] == [])
    q = d['motor_q_current']
    check('Q current physical observable closed', 'Motor Actual Current (Q Axis)' in q['observable'] and '-0.01 A/count' in q['observable'])
    check('Q direct-reference census exact', q['direct_reference_matches'] == ['0x00046C4C', '0x0005722E'])
    check('no cooperative Q-current response threshold invented', q['cooperative_supervisor_numeric_response_threshold'] is None and (not q['cooperative_supervisor_measured_q_comparator_recovered']))
    check('internal command monitors not Q current', not q['internal_monitors_are_q_current'])
    r = d['remaining_policy']
    check('remaining driver override is deliberate Panda policy', r['driver_override_abs_nm'] is None and 'Panda/openpilot policy' in r['driver_override_source'] and ('no recovered Toyota EPS' in r['driver_override_source']))
    check('temporary/permanent fault mapping open', r['temporary_vs_permanent_fault_mapping'] is None)
    check('actuator response now deliberate policy, not fake OEM threshold', 'no OEM measured-Q comparator recovered' in r['actuator_response_policy'])
    s = d['static_conclusion']
    check('core steering limits closed', s['absolute_angle_limit_closed'] and s['per_frame_delta_limit_closed'] and s['measured_rate_limit_closed'])
    check('slew/tick distinction explicit', s['per_task_slew_closed'] and s['foreground_tick_wall_clock_closed'] and s['slew_deg_per_second_only_conditional_on_once_per_foreground_call'])
    check('driver torque policy reclassified from OEM recovery blocker', s['driver_torque_observable_closed'] and s['physical_driver_torque_comparator_absent_under_promoted_census_boundary'] and s['driver_override_is_panda_policy_not_static_eps_recovery_blocker'])
    check('Q observable/threshold boundary preserved', s['measured_q_observable_closed_oem_response_threshold_not_recovered'])
    if PANDA.exists():
        pd = json.loads(PANDA.read_text())
        check('Panda remains non-enabling', not pd['status']['panda_safety_enable_authorized'])
        check('Panda hard target agrees', pd['eps_hard_envelope']['lta_target_abs_max_raw'] == c['b6_lta_absolute']['raw'])
        check('Panda driver override still null', pd['unresolved_safety_parameters']['driver_override_abs_nm']['value'] is None)
    else:
        check('Panda artifact exists', False)
_section_corolla_hf_steering_limits()
print()
print('== corolla hf cooperative authority wire visibility ==')

def _section_corolla_hf_cooperative_authority_wire_visibility():
    import hashlib
    import json
    import struct
    ROOT = REPO_ROOT
    ART = ROOT / 'data/generated/corolla_hf_cooperative_authority_wire_visibility.json'
    EVID = ROOT / 'data/generated/corolla_8965H1202000_cooperative_authority_wire_decompiler_evidence.json'
    BUILDER = ROOT / 'tools/targets/corolla/builders/build_corolla_hf_cooperative_authority_wire_visibility.py'
    H = ROOT / 'community/albinoelephant/normalized/8965H1202000_CodeFlash.bin'
    H_RAW = ROOT / 'community/albinoelephant/raw-20260818/albinoelephant-corolla-2023.20260814-0023/dump_codeflash_00000000_00200000_20260814-025814.bin'
    F_RAW = ROOT / 'community/spanconstant/raw-20260821/span-corolla-2025.20260821-1511/dump_codeflash_00000000_00200000_20260821-152033.bin'

    def sha(data: bytes) -> str:
        return hashlib.sha256(data).hexdigest()
    artifact = json.loads(ART.read_text())
    evidence = json.loads(EVID.read_text())
    h = H.read_bytes()
    check('exact variants only', artifact['software_ids'] == ['8965H1202000', '8965F1208000'])
    check('exact H image identity', len(h) == 1048576 and sha(h) == '0b47bdc1217835c839e3543e52eab40eb793650a9c159e46f6a9b365ea41a67f')
    body_ok = True
    for row in evidence['functions']:
        entry = int(row['entry'], 16)
        body_ok &= sha(h[entry:entry + row['body_size']]) == row['body_sha256']
    check('all 16 promoted functions raw/text bound', body_ok)
    gate = artifact['exact_cooperative_gate']
    check('raw stage and normalizer exact', gate['raw_mode_source'] == '0xFEBE7C58' and gate['raw_mode_stage'] == '0xFEBEF000' and (gate['stage_copy'] == '0x0005262C') and (gate['normalizer'] == '0x000B8EEC'))
    check('normalization distinguishes raw modes 0 and 1', gate['normalization']['0'] == 0 and gate['normalization']['1'] == 1)
    check('exact acceptance condition', gate['acceptance_decoder'] == '0x000CBE6E' and gate['acceptance_condition'] == 'FEBEACBD == 0 AND FEBEC26D == 1')
    coarse = artifact['positive_coarse_mode_wire_path']
    check('coarse path endpoints', coarse['path'][0] == 'FEBE7C58' and coarse['path'][-1] == 'CAN 0x030')
    check('fixed-GP/computed chain exact', all((x in coarse['path'] for x in ['FEBEF000', '0x000B23A2', 'FEBEB118', '0x000BBA48', 'FEBEE887', '0x000470C6', '0x0004766A'])))
    check('coarse predicate exact', coarse['raw_mode_predicate'] == 'FEBEF000 < 2' and 'larger aggregate' in coarse['predicate_role'])
    check('three exact 0x030 wire bits', coarse['wire_bits'] == [{'signal_id': 5, 'source': '0xFEBE7E09', 'wire': 'B6[3]'}, {'signal_id': 12, 'source': '0xFEBE7E0B', 'wire': 'B10[3]'}, {'signal_id': 15, 'source': '0xFEBE7E0D', 'wire': 'B13[4]'}])
    negative = artifact['exact_authority_negative']
    check('mode-0/mode-1 counterexample retained', 'FEBEACBD=0' in negative['distinguishing_pair']['raw_mode_0'] and 'FEBEACBD=1' in negative['distinguishing_pair']['raw_mode_1'])
    check('exact authority negative', negative['exact_wire_visible_cooperative_authority_bit_recovered'] is False and 'opposite exact-gate outcomes' in negative['proof'])
    pdus = artifact['five_pdu_boundary']
    check('five normal Tx PDUs exact', [row['can_id'] for row in pdus] == ['0x030', '0x351', '0x394', '0x4A3', '0x4C8'])
    check('five packers exact', [row['packer'] for row in pdus] == ['0x0004766A', '0x00047BA2', '0x00047ADA', '0x0004749A', '0x000475D0'])
    check('five direct exact-root sets empty', all((row['direct_cooperative_root_references'] == [] for row in pdus)))
    check('five exact authority results negative', all((row['exact_wire_visible_cooperative_authority_bit_recovered'] is False for row in pdus)))
    occ = artifact['indirect_profile_flag_consumers']['absolute_pointer_occurrences']
    expected_offsets = {4273914478: [855588, 855648, 856356, 856416], 4273914479: [855600, 855660, 856368, 856428], 4273914480: [855612, 855672, 856380, 856440], 4273914481: [855624, 855684, 856392, 856452]}
    raw_occ_ok = True
    for address, expected in expected_offsets.items():
        needle = struct.pack('<I', address)
        actual = [offset for offset in range(len(h)) if h.startswith(needle, offset)]
        raw_occ_ok &= actual == expected
    check('profile absolute-pointer occurrence census exact', raw_occ_ok)
    check('non-profile exact/chain roots have zero pointer literals', all((occ[name] == [] for name in ['raw_mode', 'normalized_mode', 'health_gate', 'common_active', 'profile_1_mirror', 'aggregate_stage', 'aggregate_snapshot', 'wire_source_signal_5', 'wire_source_signal_12', 'wire_source_signal_15'])))
    table_ok = True
    for base in (855576, 856344):
        for bank in range(2):
            flags = [struct.unpack_from('<I', h, base + bank * 60 + row * 12)[0] for row in range(5)]
            table_ok &= flags == [0, 4273914478, 4273914479, 4273914480, 4273914481]
    check('both two-bank computed profile tables exact', table_ok)
    check('indirect profile consumers are internal gains', artifact['indirect_profile_flag_consumers']['classification'].endswith('internal gain selectors, not discrete Tx fields'))
    h_raw = H_RAW.read_bytes()
    f_raw = F_RAW.read_bytes()
    check('raw range dumps normalize to exact identities', len(h_raw) == len(f_raw) == 2097152 and h_raw[:1048576] == h and (sha(f_raw[:1048576]) == 'fdb35b76891cf84a8b89e0a05c9c7c5cfcd27994cf85ccc01ff32828f53091f6'))
    check('H/F application bytes independently identical', h_raw[131072:1048576] == f_raw[131072:1048576] and sha(h_raw[131072:1048576]) == '2ccb79cda1e8689ec91c389d3d7e3921c010ddc9c9d917f23c1705916a0e0d7f')
    conclusion = artifact['static_conclusion']
    check('positive and negative both explicit', conclusion['coarse_mode_aggregate_bits_recovered'] is True and conclusion['coarse_mode_wire_can_id'] == '0x030' and (conclusion['exact_wire_visible_cooperative_authority_bit_recovered'] is False))

_section_corolla_hf_cooperative_authority_wire_visibility()
print()
print('== corolla hf panda lateral safety contract ==')

def _section_corolla_hf_panda_lateral_safety_contract():
    import json
    ROOT = REPO_ROOT
    ART = ROOT / 'data/generated/corolla_hf_panda_lateral_safety_contract.json'
    BUILDER = ROOT / 'tools/targets/corolla/builders/build_corolla_hf_panda_lateral_safety_contract.py'

    def candidate_tx_ok(*, controls_allowed: bool, request_id: int, target_raw: int, seq: int, previous_target: int | None, previous_seq: int | None, steer_rate_raw: int, driver_torque_invalid: int=0, fault_inhibit: int=0, driver_torque_nm: float=0.0, driver_override_abs_nm: float | None=None) -> bool:
        """Reference implementation of the deliberately strict policy encoded by the artifact."""
        if driver_torque_invalid != 0 or fault_inhibit != 0:
            return False
        if driver_override_abs_nm is not None and abs(driver_torque_nm) > driver_override_abs_nm:
            return False
        if controls_allowed:
            if request_id != 11 or abs(target_raw) > 1745 or abs(steer_rate_raw) > 100:
                return False
            if previous_seq is not None and seq != previous_seq + 1 & 63:
                return False
            if previous_target is not None and abs(target_raw - previous_target) > 78:
                return False
            return True
        return request_id == 0 and target_raw == 0
    d = json.loads(ART.read_text())
    check('candidate remains explicitly non-enabling', d['status']['classification'] == 'candidate-non-enabling' and (not d['status']['panda_safety_enable_authorized']))
    check('production enable remains false', not d['static_conclusion']['production_enable_authorized'])
    check('H/F exact software IDs', d['cross_variant']['software_ids'] == ['8965H1202000', '8965F1208000'])
    check('all cited H/F safety functions byte-identical', d['cross_variant']['all_safety_function_windows_byte_identical'] and len(d['cross_variant']['function_windows']) == 15)
    check('all cited H/F safety calibration bytes byte-identical', d['cross_variant']['all_cited_safety_calibration_bytes_byte_identical'])
    check('critical LTA limits bank-invariant', d['cross_variant']['critical_lta_abs_and_delta_limits_bank_invariant'])
    wire = d['wire_command']
    check('B6 wire geometry', wire['can_id'] == '0x0B6' and wire['dlc'] == 32 and wire['secured'])
    check('Target Lateral ID geometry', wire['target_lateral_id'] == {'signal': 254, 'wire': 'B3[5:0]'})
    check('target-angle signal geometry', wire['target_angle']['signal'] == 255 and wire['target_angle']['wire'] == 'B4:B5 signed16')
    check('target-angle exact scale', wire['target_angle']['exact_scale_fraction_deg'] == {'numerator': 1024, 'denominator': 17870})
    check('application sequence geometry', wire['application_sequence'] == {'signal': 261, 'wire': 'B7[5:0]', 'modulus': 64})
    e = d['eps_hard_envelope']
    check('EPS accepted request IDs exact', e['accepted_active_target_lateral_ids'] == {'1': 'PCS', '4': 'LDA', '10': 'Hands Off LTA', '11': 'LTA/LCA', '19': 'PDA'})
    check('manual/no-request ID is zero', e['inactive_target_lateral_id'] == 0 and e['lta_lca_request_id'] == 11)
    check('LTA absolute raw target limit', e['lta_target_abs_max_raw'] == 1745)
    check('LTA absolute physical target is approximately 100 deg', 99.99 < e['lta_target_abs_max_deg'] < 100.0)
    check('target delta deadband exact', e['target_delta_deadband_raw'] == 87)
    check('target delta threshold exact', e['lta_target_delta_max_raw_per_effective_gap'] == 78)
    check('target delta physical threshold approximately 4.47 deg', 4.46 < e['lta_target_delta_max_deg_per_effective_gap'] < 4.48)
    check('EPS sequence gap formula and cap', e['sequence']['effective_gap_min'] == 1 and e['sequence']['effective_gap_max'] == 8 and (not e['sequence']['strict_plus_one_required_by_eps']))
    check('seven-tick B6 receiver cutout', e['communication_loss']['successful_receive_reload_ticks'] == 7 and e['communication_loss']['primary_cutout_after_foreground_ticks'] == 7)
    check('seven-tick wall clock closed at nominal 35 ms', e['communication_loss']['wall_clock_duration_known'] and e['communication_loss']['nominal_wall_clock_ms'] == 35.0)
    check('LTA measured steering-rate raw threshold', e['measured_steering_rate_monitor']['lta_raw_abs_threshold'] == 100)
    check('measured-rate persistent debounce remains bank-specific', e['measured_steering_rate_monitor']['persistent_eps_debounce_cycles_low_bank'] == 79 and e['measured_steering_rate_monitor']['persistent_eps_debounce_cycles_high_bank'] == 63)
    check('per-task target slew retained with conditional 5ms rate', e['internal_target_conditioning']['runtime_low_bank_lta_slew_doubled_domain_per_steering_task'] == 7 and e['internal_target_conditioning']['default_high_bank_lta_slew_doubled_domain_per_steering_task'] == 4 and (e['internal_target_conditioning']['foreground_tick_nominal_ms'] == 5.0) and (not e['internal_target_conditioning']['wall_clock_rate_unconditional']) and (40.0 < e['internal_target_conditioning']['runtime_low_bank_deg_per_second_if_once_per_foreground_tick'] < 40.2))
    check('internal target/response inhibit aggregation exact', 'FEBEC269' in e['internal_inhibit_chain']['aggregate'] and 'FEBEC26B' in e['internal_inhibit_chain']['aggregate'] and ('FEBEC26A' in e['internal_inhibit_chain']['aggregate']))
    check('additional C245 cooperative gate retained', 'FEBEC245' in e['internal_inhibit_chain']['additional_gate'])
    check('controller error saturation not promoted as rejection', e['controller_error_clamp']['classification'] == 'controller error saturation, not promoted to a Panda rejection threshold')
    m = d['measured_inputs']
    check('measured angle comes from 0x025 coarse+fraction', m['steering_angle']['can_id'] == '0x025' and m['steering_angle']['coarse_signal'] == 184 and (m['steering_angle']['fraction_signal'] == 185))
    check('measured angle scales exact', m['steering_angle']['coarse_deg_per_count'] == 1.5 and m['steering_angle']['fraction_deg_per_count'] == 0.1)
    check('measured rate is signal186', m['steering_rate']['signal'] == 186 and m['steering_rate']['signed_bits'] == 12)
    check('driver torque source physical and live', m['driver_torque']['can_id'] == '0x030' and m['driver_torque']['live_span_range_nm']['count'] == 6000)
    check('driver torque invalid gate is required clear', 'must be 0' in m['driver_torque']['invalid_gate'])
    check('driver override numeric threshold deliberately open as Panda policy', m['driver_torque']['override_abs_threshold_nm'] is None and 'Panda/openpilot' in m['driver_torque']['override_policy_source'])
    check('driver torque acquisition clamp is not override', abs(m['driver_torque']['acquisition_clamp_abs_nm'] - 8.23828125) < 1e-09)
    check('driver torque telemetry saturation is not override', m['driver_torque']['telemetry_saturation_abs_nm'] == 10.0)
    check('selected fault/inhibit is immediate cutout candidate', m['steering_fault_inhibit']['nominal_clear_value'] == 0 and 'immediate controls cutout' in m['steering_fault_inhibit']['candidate_action'])
    p = d['candidate_panda_subset']
    check('candidate Panda subset still disabled', not p['enabled'])
    check('candidate restricts active request to LTA/LCA', any(('ID 11' in x for x in p['tx_requirements'])))
    check('candidate rejects other EPS request profiles', any(('Reject all other' in x for x in p['tx_requirements'])))
    check('candidate requires strict +1 sequence', any(('exactly +1 modulo 64' in x for x in p['tx_requirements'])))
    check('candidate applies single-step 78-count delta', any(('<= 78 raw counts' in x for x in p['tx_requirements'])))
    check('candidate inactive command is ID0/target0', any(('ID 0 and target angle 0' in x for x in p['tx_requirements'])))
    check('sender lapse now records nominal 35 ms EPS cutout', p['sender_lapse']['milliseconds'] == 35.0)
    u = d['unresolved_safety_parameters']
    check('only three bounded safety-policy parameter classes remain', set(u) == {'driver_override_abs_nm', 'extended_fault_policy', 'actuator_response_fault_threshold'})
    check('driver override parameter is intentionally unset policy not OEM recovery', u['driver_override_abs_nm']['value'] is None and u['driver_override_abs_nm']['classification'] == 'deliberate-panda-policy-not-unrecovered-oem-comparator' and ('no Toyota EPS' in u['driver_override_abs_nm']['missing_evidence']))
    check('extended fault policy is intentionally unset with immediate gate known', u['extended_fault_policy']['value'] is None and 'disable' in u['extended_fault_policy']['known_immediate_gate'])
    check('actuator response threshold intentionally unset', u['actuator_response_fault_threshold']['value'] is None)
    check('actuator response is reclassified as no recovered OEM measured-Q threshold', u['actuator_response_fault_threshold']['classification'] == 'no-recovered-oem-measured-q-current-threshold' and 'FEBEAE16' in u['actuator_response_fault_threshold']['static_firmware_result'])
    check('deployment blockers remain outside safety math', len(d['deployment_integration_blockers']) == 4 and any(('repin' in x for x in d['deployment_integration_blockers'])))
    check('reference policy accepts nominal first active LTA', candidate_tx_ok(controls_allowed=True, request_id=11, target_raw=100, seq=7, previous_target=None, previous_seq=None, steer_rate_raw=20))
    check('reference policy accepts wrap +1', candidate_tx_ok(controls_allowed=True, request_id=11, target_raw=110, seq=0, previous_target=100, previous_seq=63, steer_rate_raw=20))
    check('reference policy accepts exact max angle', candidate_tx_ok(controls_allowed=True, request_id=11, target_raw=1745, seq=2, previous_target=1700, previous_seq=1, steer_rate_raw=100))
    check('reference policy rejects above max angle', not candidate_tx_ok(controls_allowed=True, request_id=11, target_raw=1746, seq=2, previous_target=1700, previous_seq=1, steer_rate_raw=20))
    check('reference policy rejects non-LTA request', not candidate_tx_ok(controls_allowed=True, request_id=4, target_raw=100, seq=2, previous_target=90, previous_seq=1, steer_rate_raw=20))
    check('reference policy rejects sequence gap tolerated by EPS', not candidate_tx_ok(controls_allowed=True, request_id=11, target_raw=110, seq=3, previous_target=100, previous_seq=1, steer_rate_raw=20))
    check('reference policy accepts 78-count delta', candidate_tx_ok(controls_allowed=True, request_id=11, target_raw=178, seq=2, previous_target=100, previous_seq=1, steer_rate_raw=20))
    check('reference policy rejects 79-count delta', not candidate_tx_ok(controls_allowed=True, request_id=11, target_raw=179, seq=2, previous_target=100, previous_seq=1, steer_rate_raw=20))
    check('reference policy rejects measured rate 101', not candidate_tx_ok(controls_allowed=True, request_id=11, target_raw=100, seq=2, previous_target=90, previous_seq=1, steer_rate_raw=101))
    check('reference policy rejects torque-invalid gate', not candidate_tx_ok(controls_allowed=True, request_id=11, target_raw=100, seq=2, previous_target=90, previous_seq=1, steer_rate_raw=20, driver_torque_invalid=1))
    check('reference policy rejects selected fault gate', not candidate_tx_ok(controls_allowed=True, request_id=11, target_raw=100, seq=2, previous_target=90, previous_seq=1, steer_rate_raw=20, fault_inhibit=1))
    check('reference policy supports future driver threshold parameter', not candidate_tx_ok(controls_allowed=True, request_id=11, target_raw=100, seq=2, previous_target=90, previous_seq=1, steer_rate_raw=20, driver_torque_nm=3.1, driver_override_abs_nm=3.0))
    check('reference policy permits exact future driver threshold', candidate_tx_ok(controls_allowed=True, request_id=11, target_raw=100, seq=2, previous_target=90, previous_seq=1, steer_rate_raw=20, driver_torque_nm=-3.0, driver_override_abs_nm=3.0))
    check('inactive candidate accepts only zero request/target', candidate_tx_ok(controls_allowed=False, request_id=0, target_raw=0, seq=0, previous_target=None, previous_seq=None, steer_rate_raw=0))
    check('inactive candidate rejects stale target', not candidate_tx_ok(controls_allowed=False, request_id=0, target_raw=1, seq=0, previous_target=None, previous_seq=None, steer_rate_raw=0))
    check('steering-limit ledger is a tracked Panda input', 'steering_limits' in d['sources'] and d['sources']['steering_limits']['path'] == 'data/generated/corolla_hf_steering_limits.json')
    check('static conclusion keeps Q-current OEM threshold negative', d['static_conclusion']['measured_q_current_observable_closed_but_oem_response_threshold_not_recovered'])
    check('static conclusion keeps speed-dependent hard reduction negative', d['static_conclusion']['speed_dependent_hard_angle_reduction_not_recovered'])
    check('static conclusion closes nominal 35ms loss cutout', d['static_conclusion']['eps_loss_cutout_nominal_wall_clock_ms'] == 35.0)
    check('static conclusion reclassifies driver override as Panda policy', d['static_conclusion']['driver_torque_signal_closed'] and d['static_conclusion']['driver_override_is_panda_policy_not_eps_static_recovery_blocker'])
    check('static conclusion separates stock cadence from replacement freshness', d['static_conclusion']['wall_clock_sender_cadence_open'] and d['static_conclusion']['replacement_sender_freshness_policy_closed_independently_of_stock_cadence'])
_section_corolla_hf_panda_lateral_safety_contract()
print()
print(f'\n== RESULT: {passed} passed, {failed} failed ==')
raise SystemExit(1 if failed else 0)
