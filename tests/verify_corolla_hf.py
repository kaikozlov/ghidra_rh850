#!/usr/bin/env python3
"""Portable Corolla H/F contract pins against committed artifacts.

Merged portable family module.
"""
from __future__ import annotations
import sys
from pathlib import Path
ROOT = REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
passed = failed = 0

def check(name, cond, detail=''):
    global passed, failed
    ok = bool(cond)
    passed += int(ok)
    failed += int(not ok)
    suffix = f' ({detail})' if detail else ''
    print(f"[{('PASS' if ok else 'FAIL')}] {name}{suffix}")
print('== corolla hf command5 runtime carrier ==')

def _section_corolla_hf_command5_runtime_carrier():
    import hashlib
    import json
    import subprocess
    import sys
    import tempfile
    from pathlib import Path
    ROOT = Path(__file__).resolve().parents[1]
    ART = ROOT / 'data/generated/corolla_hf_command5_runtime_carrier.json'
    EVID = ROOT / 'data/generated/corolla_hf_command5_runtime_carrier_evidence.json'
    EXTRACTOR = ROOT / 'tools/extract_corolla_hf_command5_runtime_carrier_evidence.py'
    BUILDER = ROOT / 'tools/build_corolla_hf_command5_runtime_carrier.py'
    RUNTIME_BUILDER = ROOT / 'exploit/ephemeral_runtime/build_corolla_hf_command5_carrier.py'
    PROXY_SOURCE = ROOT / 'exploit/ephemeral_runtime/corolla_hf_command5_proxy.c'
    CANARY_SOURCE = ROOT / 'exploit/ephemeral_runtime/corolla_hf_canary.c'
    PROXY_AUDIT = ROOT / 'exploit/ephemeral_runtime/audited_corolla_hf_command5_proxy_build.json'
    CANARY_AUDIT = ROOT / 'exploit/ephemeral_runtime/audited_corolla_hf_canary_build.json'
    PROXY_BIN = ROOT / 'exploit/ephemeral_runtime/audited/corolla_hf_command5_proxy.bin'
    CANARY_BIN = ROOT / 'exploit/ephemeral_runtime/audited/corolla_hf_runtime_canary.bin'
    H = ROOT / 'community/albinoelephant/normalized/8965H1202000_CodeFlash.bin'
    F = ROOT / 'community/spanconstant/raw-20260821/span-corolla-2025.20260821-1511/dump_codeflash_00000000_00200000_20260821-152033.bin'
    RAMREQ = ROOT / 'data/variant_ram_exec_requirements.json'
    DOC = ROOT / 'docs/variants/corolla-h-f-openpilot-state-bridge.md'
    FINDINGS = ROOT / 'docs/status/FINDINGS.md'
    PRIORITIES = ROOT / 'docs/status/PRIORITIES.md'
    OPEN = ROOT / 'docs/status/OPEN_QUESTIONS.md'
    SENDER = ROOT / 'docs/security/secoc/sender-implementation.md'

    def sha(data: bytes) -> str:
        return hashlib.sha256(data).hexdigest()
    a = json.loads(ART.read_text())
    ev = json.loads(EVID.read_text())
    h = H.read_bytes()
    fraw = F.read_bytes()
    proxy_audit = json.loads(PROXY_AUDIT.read_text())
    canary_audit = json.loads(CANARY_AUDIT.read_text())
    print('== promoted static evidence ==')
    check('artifact schema/scope', a['schema'] == 'corolla-hf-command5-runtime-carrier-v1' and a['applies_to'] == ['8965H1202000', '8965F1208000'])
    check('evidence schema', ev['schema'] == 'corolla-hf-command5-runtime-carrier-evidence-v1')
    check('evidence extractor hash pinned', ev['generator']['sha256'] == sha(EXTRACTOR.read_bytes()))
    check('exact H normalized image pinned', ev['sources']['h_normalized_codeflash']['sha256'] == sha(h) == '0b47bdc1217835c839e3543e52eab40eb793650a9c159e46f6a9b365ea41a67f')
    check('exact F source range dump pinned', ev['sources']['f_source_range_dump']['sha256'] == sha(fraw) == 'b8fa3d951f59fb75c190ce1b2c73164adb952f871650cfcd3b7656f08a9c448d')
    check('F normalized first MiB identity distinct/pinned', ev['sources']['f_normalized_first_mib']['sha256'] == sha(fraw[:1048576]) == 'fdb35b76891cf84a8b89e0a05c9c7c5cfcd27994cf85ccc01ff32828f53091f6')
    check('listed H/F prerequisites byte-identical', ev['h_f_exact_transfer']['all_ranges_byte_equal'] and all((r['byte_equal'] for r in ev['h_f_exact_transfer']['ranges'])))
    print('\n== carrier pocket / MPU ==')
    g = a['carrier_geometry']
    check('candidate is exact 464-byte lower-page pocket', g['base'] == '0xFEBF0000' and g['end_inclusive'] == '0xFEBF01CF' and (g['end_exclusive'] == '0xFEBF01D0') and (g['size'] == 464))
    check('first normalized direct reference starts exactly after pocket', g['first_recovered_normalized_reference'] == '0xFEBF01D0' and g['normalized_direct_reference_count_inside'] == 0)
    check('negative proof boundary is explicit', 'computed aliases' in g['static_negative_boundary'] and 'DMA' in g['static_negative_boundary'] and ('live canary' in g['static_negative_boundary']))
    check('candidate resides in exact H MPU region5', g['mpu_region_index'] == 5 and g['mpu_bounds'] == ['0xFEBEF400', '0xFEBF33FC'])
    check('candidate MPAT is B8 in both contexts', g['mpat_contexts'] == ['0x000000B8', '0x000000B8'] and 'read-write-execute' in g['permissions'])
    print('\n== mailbox ==')
    m = a['mailbox_geometry']
    check('mailbox geometry exact', m['base'] == '0xFEBFFB80' and m['end_exclusive'] == '0xFEBFFBBC' and (m['size'] == 60))
    check('mailbox has zero recovered normalized direct refs', m['normalized_direct_reference_count_inside'] == 0)
    check('mailbox stays in H XCP shadow and above startup copy', m['xcp_shadow_window'] == ['0xFEBF7C00', '0xFEBFFBFF'] and m['startup_shadow_copy_end_inclusive'] == '0xFEBFF9EF')
    check('proxy self-initializes request byte before interrupts', all((x in m['request_state_initialization'] for x in ('proxy initializes', 'request_state', '0', 'before enabling interrupts', 'sampled once per foreground tick'))))
    check('proxy mirrors driver status into host-readable mailbox', m['result_status_offset'] == 1 and all((x in m['result_status_protocol'] for x in ('FEBF1280/FEBF1281', 'mailbox byte +1', 'request_state=0', 'immediate non-busy'))))
    print('\n== audited executable candidates ==')
    canary = a['runtime_candidates']['inert_canary']
    proxy = a['runtime_candidates']['fixed_b6_command5_proxy']
    check('canary exact audited bytes', canary['size'] == CANARY_BIN.stat().st_size == 332 and canary['headroom'] == 132 and (canary['sha256'] == sha(CANARY_BIN.read_bytes()) == 'a32baf46dd8e0599021b5c174763887513b3ba903d40ebe284f19d31c97424f4'))
    check('proxy exact audited bytes', proxy['size'] == PROXY_BIN.stat().st_size == 462 and proxy['headroom'] == 2 and (proxy['sha256'] == sha(PROXY_BIN.read_bytes()) == '3bb96eefae06005c99a0ac52b7f0c64cc5d52e2b0b1fcbb73e0b4ec69609f8d3'))
    check('both executables entry0/no relocations', canary['entry_offset'] == proxy['entry_offset'] == 0 and canary['relocations'] == proxy['relocations'] == 0)
    check('proxy exact B6 command5 contract', proxy['input_length'] == 36 and proxy['driver_record'] == 0 and (proxy['key_selector'] == 4) and (proxy['dispatcher'] == '0x00082750') and (proxy['done_flag'] == '0xFEBF1280') and (proxy['status_flag'] == '0xFEBF1281'))
    check('proxy shared-driver busy retry semantics', 'busy result 2' in proxy['busy_behavior'] and 'retries' in proxy['busy_behavior'] and ('no command-7 abort' in proxy['busy_behavior']))
    check('proxy source fixes input length at 36', '(void *)m->input' in PROXY_SOURCE.read_text() and '36u' in PROXY_SOURCE.read_text())
    check('proxy source leaves busy request pending', 'else if (rc != 2)' in PROXY_SOURCE.read_text())
    check('proxy source self-initializes mailbox after startup before interrupts', 'm->request_state = 0u;\n  __asm__ volatile("ei");' in PROXY_SOURCE.read_text())
    check('proxy caches host request state once per foreground tick', 'unsigned char request_state = m->request_state;' in PROXY_SOURCE.read_text() and 'else if (request_state == 1u)' in PROXY_SOURCE.read_text())
    check('proxy atomically samples adjacent done/status and mirrors both completion paths', 'volatile unsigned short *completion' in PROXY_SOURCE.read_text() and 'unsigned short completion_state = *completion;' in PROXY_SOURCE.read_text() and ('m->result_status = (unsigned char)(completion_state >> 8);' in PROXY_SOURCE.read_text()) and ('m->result_status = (unsigned char)rc;' in PROXY_SOURCE.read_text()))
    check('H completion callback raw body is pinned before halfword sampling', H.read_bytes()[536412:536412 + 14].hex() == '4437815a010a440f805a00527f00')
    check('canary source is inert wrt command5', 'TARGET_COMMAND5_DISPATCH' not in CANARY_SOURCE.read_text() and 'TARGET_CANARY_HEARTBEAT' in CANARY_SOURCE.read_text())
    print('\n== audit/toolchain trust ==')
    for label, audit, source in (('proxy', proxy_audit, PROXY_SOURCE), ('canary', canary_audit, CANARY_SOURCE)):
        check(f'{label} audit source hash', audit['source']['sha256'] == sha(source.read_bytes()))
        check(f'{label} audit builder hash', audit['builder']['sha256'] == sha(RUNTIME_BUILDER.read_bytes()))
        check(f'{label} compiler equivalence', audit['toolchain']['reproduced_byte_exact'] is True and audit['toolchain']['reference_sha256'] == '273202dc591810b2f587ab8fac044599b57b4e07a24ff61d36b7131b97c00660')
        check(f'{label} static-only review grade', audit['review_status'] == 'static-carrier-candidate-not-live-validated')
    check('artifact records compiler-equivalence rule', a['toolchain_reproducibility']['selected_build_reproduced_canonical_reference'] and 'byte-exact' in a['toolchain_reproducibility']['noncanonical_image_acceptance_rule'])
    print('\n== dynamic boundary ==')
    b = a['boundary']
    check('static carrier candidate is closed', b['static_target_native_carrier_candidate_closed'] is True)
    check('verified RAM requirement intentionally not promoted', b['verified_variant_ram_exec_requirement_promoted'] is False)
    check('live retention/permission/latency remain open', not b['live_retention_closed'] and (not b['live_slot4_permission_closed']) and (not b['command5_latency_jitter_closed']))
    check('production signer and actuation remain disabled', not b['production_b6_signer_closed'] and (not b['vehicle_actuation_authorized']))
    variants = {row['id'] for row in json.loads(RAMREQ.read_text())['variants']}
    check('H/F absent from verified variant RAM geometry', 'corolla-8965h1202000' not in variants and 'corolla-8965f1208000' not in variants)
    stages = a['validation_sequence']
    check('canary is mandatory first live stage', [r['stage'] for r in stages] == [1, 2, 3, 4] and stages[0]['name'] == 'inert carrier canary' and ('before exposing command-5' in stages[0]['purpose']))
    check('slot4 permission precedes timing', stages[1]['name'] == 'known-input slot4 command5 permission' and stages[3]['name'] == 'latency and contention characterization')
    print('\n== canonical documentation ==')
    doc = DOC.read_text()
    findings = FINDINGS.read_text()
    priorities = PRIORITIES.read_text()
    oq = OPEN.read_text()
    sender = SENDER.read_text()
    check('canonical report records target-native pocket', 'FEBF0000..FEBF01CF' in doc and '462-byte' in doc and ('332-byte' in doc))
    check('canonical report preserves live-canary boundary', 'required first live payload' in doc.lower() and 'canary' in doc.lower() and ('2 bytes' in doc))
    check('TMS-054 registered', '| TMS-054 |' in findings and '462 bytes' in findings and ('332-byte' in findings))
    check('priority now asks for canary before command5', 'inert H/F carrier canary' in priorities and 'FEBFFB80' in priorities)
    check('OQ-021 reflects static carrier closure', '462-byte' in oq and '332-byte' in oq and ('live retention' in oq.lower()))
    check('sender design separates H/F static carrier from Sienna live runtime', 'Corolla H/F target-native carrier candidate' in sender and 'not verified RAM geometry' in sender and ('live_installer.py' in sender))
    print('\n== deterministic artifact builder ==')
_section_corolla_hf_command5_runtime_carrier()
print()
print('== corolla hf steering limits ==')

def _section_corolla_hf_steering_limits():
    import json
    import subprocess
    import sys
    import tempfile
    from pathlib import Path
    ROOT = Path(__file__).resolve().parents[1]
    ART = ROOT / 'data/generated/corolla_hf_steering_limits.json'
    BUILDER = ROOT / 'tools/build_corolla_hf_steering_limits.py'
    PANDA = ROOT / 'data/generated/corolla_hf_panda_lateral_safety_contract.json'
    d = json.loads(ART.read_text())
    check('schema', d['schema'] == 'corolla-hf-steering-limits-v1')
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
    check('conditional once-per-foreground slew rates are explicit', 40.0 < c['internal_lta_slew']['selected_low_deg_per_second_if_called_each_foreground_tick'] < 40.2 and 22.8 < c['internal_lta_slew']['high_default_deg_per_second_if_called_each_foreground_tick'] < 23.0 and ('conditional' in c['internal_lta_slew']['boundary']))
    check('doubled target clamp equals B6 envelope', c['doubled_domain_absolute_clamp']['raw_internal'] == 3490 and c['doubled_domain_absolute_clamp']['equivalent_b6_raw'] == 1745.0)
    check('measured rate violation is strictly above 100', c['measured_steering_rate']['raw_abs_threshold'] == 100 and c['measured_steering_rate']['violation_relation'] == 'abs(rate_raw) > 100')
    check('rate persistence bank split', c['measured_steering_rate']['selected_low_persistence_cycles'] == 79 and c['measured_steering_rate']['high_default_persistence_cycles'] == 63)
    m = d['indexed_compensation']
    check('CBFCE map input remains physically unnamed', m['index_input'] == 'FEBEADF4' and m['index_physical_identity'] is None)
    check('four profile compensation maps recovered', len(m['maps']) == 4 and [x['offset'] for x in m['maps']] == ['0x768', '0x798', '0x7C8', '0x7F8'])
    check('selected vehicle compensation maps all zero at real points', all((x['selected_low_all_real_values_zero'] for x in m['maps'])))
    check('high default maps become nonzero at axis 7680', all((x['high_default_first_nonzero_axis'] == 7680 for x in m['maps'])))
    check('speed-dependent hard angle reduction not claimed', not d['static_conclusion']['speed_dependent_hard_angle_reduction_recovered'] and 'not a max-angle curve' in m['safety_conclusion'])
    check('ADF4 is not mislabeled SP1', 'does not claim FEBEADF4 is SP1' in m['boundary'])
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
    check('controller error is saturation not Panda rejection', p['controller_error_saturation']['raw_internal'] == 18000 and 'not Panda' in p['controller_error_saturation']['classification'])
    check('torque sensor fault constants retained raw', p['torque_sensor_fault_calibration']['raw_constants'] == {'0x0002B538': 2655, '0x0002B53C': 4233, '0x0002B546': 4091, '0x0002B548': 3341, '0x0002B54C': 1764})
    check('torque sensor fault constants not promoted to override', not p['torque_sensor_fault_calibration']['physical_driver_override_semantics'])
    t = d['driver_torque']
    check('driver torque acquisition clamp exact', t['acquisition_clamp_raw'] == 2109 and t['acquisition_raw_units_per_nm'] == 256)
    check('driver torque acquisition clamp physical', abs(t['acquisition_clamp_abs_nm'] - 8.23828125) < 1e-09)
    check('driver torque telemetry saturation exact', t['telemetry_saturation_abs_centi_nm'] == 1000 and t['telemetry_saturation_abs_nm'] == 10.0)
    check('driver torque override remains unset as Panda policy', t['override_abs_threshold_nm'] is None and (not t['supervisor_numeric_override_comparator_recovered']) and (not t['target_to_motor_physical_torque_comparator_recovered']) and ('Panda/openpilot' in t['policy_classification']))
    check('expanded physical torque census has zero C8xxx-CExxx consumers', len(t['direct_source_snapshot_reference_entries']) == 13 and t['direct_source_snapshot_refs_inside_c8xxx_cexxx_control_cone'] == [] and ('fixed-GP' in t['census_boundary']))
    check('torque clamps explicitly not override', 'not driver-override thresholds' in t['safety_boundary'] and 'removes an OEM override comparator' in t['safety_boundary'])
    q = d['motor_q_current']
    check('Q current physical observable closed', 'Motor Actual Current (Q Axis)' in q['observable'] and '-0.01 A/count' in q['observable'])
    check('Q direct-reference census exact', q['direct_reference_matches'] == ['0x00046C4C', '0x0005722E'])
    check('no cooperative Q-current response threshold invented', q['cooperative_supervisor_numeric_response_threshold'] is None and (not q['cooperative_supervisor_measured_q_comparator_recovered']))
    check('internal command monitors not Q current', not q['internal_monitors_are_q_current'] and 'FEBEAE16' in q['safety_boundary'])
    check('Q negative remains census-bounded', 'exact-substring census' in q['census_boundary'] and 'computed-pointer' in q['census_boundary'])
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
print('== corolla hf nonsteering engagement state ==')

def _section_corolla_hf_nonsteering_engagement_state():
    import hashlib
    import json
    import subprocess
    import sys
    import tempfile
    from pathlib import Path
    REPO = Path(__file__).resolve().parents[1]
    ART = REPO / 'data/generated/corolla_hf_nonsteering_engagement_state.json'
    BUILD = REPO / 'tools/build_corolla_hf_nonsteering_engagement_state.py'
    IMAGE = REPO / 'community/albinoelephant/normalized/8965H1202000_CodeFlash.bin'
    ENG = REPO / 'data/generated/corolla_8965H1202000_nonsteering_engagement_decompiler_evidence.json'
    TECH = REPO / 'data/generated/techstream_v18/tss3_cruise_engagement_semantics.json'
    DOC = REPO / 'docs/architecture/toyota-openpilot-porting-contract.md'
    STATE_DOC = REPO / 'docs/variants/corolla-h-f-openpilot-state-bridge.md'

    def sha(data: bytes) -> str:
        return hashlib.sha256(data).hexdigest()
    art = json.loads(ART.read_text())
    eng = json.loads(ENG.read_text())
    tech = json.loads(TECH.read_text())
    image = IMAGE.read_bytes()
    print('== deterministic synthesis ==')
    check('schema exact', art['schema'] == 'corolla-hf-nonsteering-engagement-state-v1')
    check('H/F application identity retained', art['software_family'] == {'h': '8965H1202000', 'f': '8965F1208000', 'application_byte_identical': True})
    check('compact H engagement evidence is raw-byte-bound', eng['schema'] == 'corolla-h-nonsteering-engagement-decompiler-evidence-v1' and eng['function_count'] == 6 and (eng['image']['sha256'] == sha(image)))
    for row in eng['functions']:
        start = int(row['entry'], 16)
        check(f"raw H body {row['entry']}", sha(image[start:start + row['body_size']]) == row['body_sha256'])
    print('\n== exact Ready Status wire join ==')
    ready = art['ready_status']
    check('Ready Status carrier is exact H 0x51E B0[7]', ready['classification'] == 'wire field closed' and ready['can_id'] == '0x51E' and (ready['length'] == 8) and (ready['h_rx_descriptor_index'] == 24) and (ready['h_signal_id'] == 154) and (ready['wire'] == 'B0[7]'))
    check('Ready Status exact source chain reaches DID1033', ready['source_chain'] == ['0x51E B0[7]', '0xFEBE7D1B', '0xFEBEF052', '0xFEBEB5A8', '0xFEBEE811', 'DID 0x1033'] and ready['techstream'] == {'name': 'Ready Status', 'did': '0x1033', 'boolean_domain': [0, 1]})
    check('Ready Status copy provenance does not claim an exclusive writer', ready['operational_copy_sites'] == ['0x000BAB58', '0x000BAC16'] and all((x in ready['writer_boundary'] for x in ('two operational copy sites', 'initialization/reset', 'exclusive-writer'))))
    check('public route corroborates Ready=1', ready['route_corroboration']['public_2023'] == {'frames': 59, 'values': [1], 'payloads': ['8000004500000000']})
    check('Span route corroborates Ready=1', ready['route_corroboration']['span_2025'] == {'frames': 60, 'values': [1], 'payloads': ['86001a0000000000']})
    check('Ready=0 remains bounded', all((x in ready['boundary'] for x in ('value 0', 'uncaptured', 'incoming', 'not proof'))))
    print('\n== 0x127 gear carrier ==')
    gear = art['gear']
    check('exact H retains 0x127/8 as Rx PDU20', gear['can_id'] == '0x127' and gear['length'] == 8 and (gear['h_rx_descriptor_index'] == 20))
    check('exact H generated signal ownership is 123..132', gear['h_signal_ids'] == list(range(123, 133)))
    check('exact H scalar extraction positions are regenerated', gear['h_scalar_extractions'] == [{'signal_id': 123, 'wire': 'B0[7:2]', 'length': 6}, {'signal_id': 125, 'wire': 'B1[3]', 'length': 1}, {'signal_id': 129, 'wire': 'B3/B4 signed11 domain', 'length': 11}])
    check('legacy B5 gear nibble is not statically consumed by exact H scalar unpacker', 'does not consume' in gear['h_static_boundary'] and gear['legacy_gear_field']['wire'] == 'B5[3:0]')
    check('Span observes raw3 with prior-art D compatibility only', gear['span_dynamic']['frames'] == gear['span_dynamic']['checksum_valid'] == 3662 and gear['span_dynamic']['raw_values'] == [3] and (gear['span_dynamic']['prior_art_decoded_values'] == ['D']) and ('MOCK' in gear['span_dynamic']['decode_basis']))
    check('gear target-native validation remains bounded', all((x in gear['production_boundary'] for x in ('no independent gear-state oracle', 'target-native D semantics', 'P/R/N/B', 'live transitions'))))
    print('\n== retained cruise prior art and false-positive rejection ==')
    cruise = art['cruise']
    c176 = cruise['retained_wire_prior_art']['0x176']
    check('0x176 survives both captures with valid checksum', c176['public_2023_frames'] == 1855 and c176['span_2025_frames'] == 1890 and (c176['checksums_all_valid'] is True))
    check('old 0x176 cruise-active/state fields stay inactive', c176['legacy_cruise_active_values'] == [False] and c176['legacy_cruise_state_values'] == [0])
    check('0x176 B0[3] is not justified as cruise replacement', c176['b0_bit3_values'] == [0, 1] and 'accelerator-release' in c176['b0_bit3_interpretation'] and ('does not disprove every possible cruise-related meaning' in c176['b0_bit3_interpretation']) and (c176['public_2023_b0_bit3_context']['0']['gas_positive_fraction'] > 0.99) and (c176['public_2023_b0_bit3_context']['1']['gas_positive_fraction'] == 0.0) and (c176['span_2025_b0_bit3_context']['0']['gas_positive_fraction'] > 0.97) and (c176['span_2025_b0_bit3_context']['1']['gas_positive_fraction'] < 0.01))
    c24d = cruise['retained_wire_prior_art']['0x24D']
    check('0x24D survives but old switch fields remain inactive', c24d['public_2023_frames'] == 59 and c24d['span_2025_frames'] == 60 and all((v == [0] for v in c24d['legacy_button_fields'].values())))
    check('old cruise replacement IDs absent in both captures', cruise['legacy_ids_absent_in_both_captures'] == ['0x177', '0x1A2', '0x1D3', '0x399'])
    print('\n== Toyota P5 engagement diagnostic oracles ==')
    rows = {x['name']: x for x in cruise['techstream_p5_frc_oracles']}
    for name, data_id, bits in (('Cruise Control Permission Flag', '0x1905', [8, 8]), ('Main Switch Recognition Flag', '0x1906', [8, 8]), ('ACC Not Available Icon Lighting Request Flag', '0x1906', [40, 40]), ('ACC Control in Operation Flag', '0x1914', [8, 8]), ('Set Vehicle Interval Time', '0x1912', [0, 7]), ('Current Vehicle Speed', '0x1901', [0, 31]), ('Memory Vehicle Speed', '0x1901', [32, 63])):
        check(f'FRC oracle {name}', rows[name]['primary_data_id'] == data_id and rows[name]['bit_range'] == bits)
    check('permission dictionary exact', rows['Cruise Control Permission Flag']['pattern_values'] == {'0': 'Cruise Control Not Allowed', '1': 'Cruise Control Allowed'})
    check('ACC-operation dictionary exact', rows['ACC Control in Operation Flag']['pattern_values'] == {'0': 'Cruise Control Not in Operation', '1': 'Cruise Control in Operation'})
    check('set-speed oracle is physical km/h', rows['Memory Vehicle Speed']['conversion']['unit'] == 'km/h' and rows['Memory Vehicle Speed']['conversion']['mul'] == rows['Memory Vehicle Speed']['conversion']['div'] == 1)
    check('follow-distance dictionary exact', rows['Set Vehicle Interval Time']['pattern_values'] == {'1': 'Set Vehicle Interval Time4', '2': 'Set Vehicle Interval Time3', '3': 'Set Vehicle Interval Time2', '4': 'Set Vehicle Interval Time1'})
    check('diagnostic semantics remain wire-unmapped', cruise['classification'] == 'diagnostic semantics narrowed; live CAN mapping not closed' and 'no CAN field may be promoted' in cruise['boundary'])
    print('\n== implementation boundary ==')
    safe = art['implementation_consequence']['safe_now']
    unsafe = art['implementation_consequence']['not_safe_yet']
    check('Ready input is safe for inspection', any(('0x51E B0[7]' in x for x in safe)))
    check('production cruise remains neutral', any(('cruiseState.available/enabled/set-speed neutral' in x for x in safe)))
    check('B0[3] promotion explicitly prohibited', any(('0x176 B0[3]' in x for x in unsafe)))
    check('P/R/N/B promotion explicitly prohibited', any(('P/R/N/B' in x for x in unsafe)))
    check('capture recipe is concrete and directly pollable', all((any((data_id in x for x in cruise['capture_recipe'])) for data_id in ('0x1905', '0x1906', '0x1914', '0x1901', '0x1912'))) and all(('UDS 22' in x and 'require 62' in x for x in cruise['capture_recipe'])))
    check('P5 selected Data IDs are proved as direct UDS RDBI', all((x in cruise['diagnostic_transport_boundary'] for x in ('ordinary SID 0x22 ReadDataByIdentifier', 'matching 0x62', 'outer DiagnosticSessionControl', 'not statically proved'))))
    print('\n== documentation/status integration ==')
    doc = DOC.read_text() if DOC.exists() else ''
    state_doc = STATE_DOC.read_text() if STATE_DOC.exists() else ''
    findings = (REPO / 'docs/status/FINDINGS.md').read_text()
    priorities = (REPO / 'docs/status/PRIORITIES.md').read_text()
    for token in ('0x51E', 'Ready Status', '0x1905', '0x1906', '0x1914', '0x24D'):
        check(f'porting doc preserves {token}', token in doc)
    check('porting doc preserves Memory Vehicle Speed oracle', 'Memory' in doc and 'Vehicle Speed' in doc and ('Data ID `0x1901`' in doc))
    check('state-bridge doc closes 0x51E Ready input', all((x in state_doc for x in ('0x51E', 'B0[7]', 'Ready Status', 'DID `0x1033`'))))
    check('COM-017 integrated', '| COM-017 |' in findings and 'nonsteering_engagement_state' in findings)
    check('priority consumes engagement-state contract', 'corolla_hf_nonsteering_engagement_state.json' in priorities)
_section_corolla_hf_nonsteering_engagement_state()
print()
print('== corolla hf direct canary ==')

def _section_corolla_hf_direct_canary():
    import hashlib
    import json
    import sys
    from pathlib import Path
    ROOT = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(ROOT))
    from exploit.common.ram_exec import explicit_route
    from exploit.ephemeral_runtime.corolla_hf_direct_canary import ALBINO_APP_F181, BOOT_F181, CANARY_SHA256, DIRECT_PAYLOAD_SHA256, DID_201, DID_202, DID_203, FF00_REQUEST, HEARTBEAT_ADDR, HEARTBEAT_MAGIC, REQUEST_DOWNLOAD, VERIFY_10F0, _attest_once, _upload_and_trigger, build_payload, build_plan

    class FakeUds:

        class SESSION_TYPE:
            DEFAULT = 1
            EXTENDED_DIAGNOSTIC = 3
            PROGRAMMING = 2

        class ACCESS_TYPE:
            REQUEST_SEED = 1
            SEND_KEY = 2

        class SERVICE_TYPE:
            REQUEST_DOWNLOAD = 52
            READ_MEMORY_BY_ADDRESS = 35

        class ROUTINE_CONTROL_TYPE:
            START = 1

        class DATA_IDENTIFIER_TYPE:
            APPLICATION_SOFTWARE_IDENTIFICATION = 61825

    class FakeClient:

        def __init__(self, f181: bytes=BOOT_F181) -> None:
            self.events: list[tuple] = []
            self.f181 = f181

        def diagnostic_session_control(self, session):
            self.events.append(('session', session))
            return b''

        def read_data_by_identifier(self, did):
            self.events.append(('rdbi', did))
            return self.f181

        def security_access(self, access, data_record=None, security_key=None):
            data = data_record if data_record is not None else security_key
            self.events.append(('security', access, bytes(data or b'')))
            if access == FakeUds.ACCESS_TYPE.REQUEST_SEED:
                return bytes.fromhex('ef309a63a0572b7a147b7062aa1073a3')
            return b''

        def write_data_by_identifier(self, did, data):
            self.events.append(('wdbi', did, bytes(data)))
            return b''

        def _uds_request(self, service, data):
            self.events.append(('request', service, bytes(data)))
            return b' \x04\x02' if service == FakeUds.SERVICE_TYPE.REQUEST_DOWNLOAD else b''

        def transfer_data(self, block, data):
            self.events.append(('transfer', block, bytes(data)))
            return b''

        def request_transfer_exit(self):
            self.events.append(('exit',))
            return b''

        def routine_control(self, control, rid, data=b''):
            self.events.append(('routine', control, rid, bytes(data)))
            return b''
    print('== deterministic direct package ==')
    payload, meta = build_payload()
    plan = build_plan()
    canary_source = ROOT / 'exploit/ephemeral_runtime/corolla_hf_canary.c'
    canary_audit = json.loads((ROOT / 'exploit/ephemeral_runtime/audited_corolla_hf_canary_build.json').read_text())
    canary_source_bytes = canary_source.read_bytes()
    check('heartbeat semantics are source/audit bound', canary_audit['source']['path'] == 'exploit/ephemeral_runtime/corolla_hf_canary.c' and canary_audit['source']['sha256'] == hashlib.sha256(canary_source_bytes).hexdigest() and (canary_audit['runtime_contract']['canary_heartbeat'] == f'0x{HEARTBEAT_ADDR:08X}') and (b'0x45504843u' in canary_source_bytes))
    check('audited canary identity', meta['shellcode_size'] == 332 and meta['shellcode_sha256'] == CANARY_SHA256)
    check('direct package identity', len(payload) == 4096 and meta['payload_sha256'] == DIRECT_PAYLOAD_SHA256)
    check('package callback and descriptor are FEBF0000', meta['callback_address'] == '0xFEBF0000' and meta['crc_descriptor_address'] == '0xFEBF0000')
    check('package authenticates and has terminal CRC residue', meta['cmac_valid'] is True and meta['crc_residue'] == '0xFFFFFFFF')
    check('plan reproduces telescope zero DID setup', plan['field_proven_bootstrap']['did_0203'] == DID_203.hex() and plan['field_proven_bootstrap']['did_0201'] == DID_201.hex() and (plan['field_proven_bootstrap']['did_0202'] == DID_202.hex()))
    check('plan reproduces exact RequestDownload', plan['field_proven_bootstrap']['request_download'] == REQUEST_DOWNLOAD.hex() == '01460100febf000000001000')
    check('plan reproduces exact 10F0 option', plan['field_proven_bootstrap']['verify_option'] == VERIFY_10F0.hex() == '4500febf000000001000')
    check('plan reproduces exact old-stack FF00 request', plan['field_proven_bootstrap']['ff00_request'] == FF00_REQUEST.hex() == '3101ff004500000e000000008000')
    check('direct package eliminates post-auth substitution', plan['field_proven_bootstrap']['post_10f0_ram_substitution_required'] is False)
    check('command5 remains gated off', plan['success_gate']['command5_proxy_authorized_by_this_plan'] is False)
    check('exact application identity is pinned', plan['target']['required_application_f181_hex'] == ALBINO_APP_F181.hex())
    check('exact boot placeholder identity is pinned', plan['target']['required_boot_f181_hex'] == BOOT_F181.hex())
    print('\n== mocked field-proven upload choreography ==')
    client = FakeClient()
    route = explicit_route(bus=0, elm327_param=0, uds_variant='old', cpu_index=0)
    sent: list[tuple] = []
    sleeps: list[float] = []
    stats = _upload_and_trigger(object(), client, FakeUds, route, payload=payload, security_secret=bytes.fromhex('f05f36b7d78c03e24ab4faef2a57d044'), isotp_send_fn=lambda panda, data, addr, *, bus: sent.append((bytes(data), addr, bus)), sleep_fn=lambda seconds: sleeps.append(seconds))
    e = client.events
    check('one old-stack identity ladder is explicit', e[:3] == [('session', 1), ('session', 3), ('session', 2)], repr(e[:3]))
    check('session settle timing mirrors telescope', sleeps == [0.5, 0.7, 1.0], repr(sleeps))
    check('boot F181 is verified before SA', e[3] == ('rdbi', 61825))
    check('SecurityAccess requests zero data record', e[4] == ('security', 1, bytes(16)))
    check('SecurityAccess sends a 16-byte response', e[5][0:2] == ('security', 2) and len(e[5][2]) == 16)
    check('DID writes exactly reproduce telescope 0203/0201/0202', e[6:9] == [('wdbi', 515, bytes(5)), ('wdbi', 513, bytes(16)), ('wdbi', 514, bytes(16))])
    check('RequestDownload record is exact', e[9] == ('request', 52, REQUEST_DOWNLOAD))
    check('payload transfers in four exact 0x400 blocks', [row[1] for row in e[10:14]] == [1, 2, 3, 4] and all((row[0] == 'transfer' and len(row[2]) == 1024 for row in e[10:14])))
    check('TransferExit precedes 10F0', e[14] == ('exit',) and e[15] == ('routine', 1, 4336, VERIFY_10F0))
    check('FF00 sent only after successful 10F0 call', sent == [(FF00_REQUEST, 1953, 0)])
    check('install stats retain boot identity and successful gates', stats['boot_f181_hex'] == BOOT_F181.hex() and stats['rid_10f0_accepted'] and stats['ff00_sent'])
    empty_download = FakeClient()
    empty_download._uds_request = lambda service, data: empty_download.events.append(('request', service, bytes(data))) or b''
    try:
        _upload_and_trigger(object(), empty_download, FakeUds, route, payload=payload, security_secret=bytes.fromhex('f05f36b7d78c03e24ab4faef2a57d044'), isotp_send_fn=lambda *args, **kwargs: None, sleep_fn=lambda _: None)
    except Exception as exc:
        empty_download_rejected = 'RequestDownload returned an empty' in str(exc)
    else:
        empty_download_rejected = False
    check('empty RequestDownload positive payload fails closed before transfer', empty_download_rejected and (not any((row[0] == 'transfer' for row in empty_download.events))))
    try:
        _upload_and_trigger(object(), FakeClient(), FakeUds, explicit_route(bus=0, elm327_param=0, uds_variant='new', cpu_index=0), payload=payload, security_secret=bytes(16), isotp_send_fn=lambda *args, **kwargs: None, sleep_fn=lambda _: None)
    except Exception as exc:
        new_stack_rejected = 'old-stack' in str(exc)
    else:
        new_stack_rejected = False
    check('unobserved new-stack variant fails closed', new_stack_rejected)
    bad = FakeClient(f181=b'bad')
    try:
        _upload_and_trigger(object(), bad, FakeUds, route, payload=payload, security_secret=bytes(16), isotp_send_fn=lambda *args, **kwargs: None, sleep_fn=lambda _: None)
    except Exception as exc:
        boot_identity_rejected = 'boot F181 mismatch' in str(exc)
    else:
        boot_identity_rejected = False
    check('wrong boot identity fails before SecurityAccess/upload', boot_identity_rejected and (not any((row[0] == 'security' for row in bad.events))))
    print('\n== application-context canary attestation ==')
    app = FakeClient(f181=ALBINO_APP_F181)
    reads = iter((bytes.fromhex('50485045'), bytes.fromhex('51485045')))
    attest = _attest_once(app, FakeUds, heartbeat_interval=0.05, read_memory_fn=lambda client, uds, mem, addr, size: next(reads), sleep_fn=lambda _: None)
    check('post-FF00 application F181 must reappear', attest['application_f181_hex'] == ALBINO_APP_F181.hex())
    check('attestation enters extended session', ('session', 3) in app.events)
    check('attestation reads target-native heartbeat address', attest['heartbeat_address'] == f'0x{HEARTBEAT_ADDR:08X}')
    check('heartbeat signature and progression are required', attest['heartbeat_magic_le'] == HEARTBEAT_MAGIC and attest['heartbeat_start_delta'] == 13 and (attest['heartbeat_step'] == 1) and (attest['heartbeat_advanced'] is True))
    try:
        _attest_once(FakeClient(f181=ALBINO_APP_F181), FakeUds, heartbeat_interval=0.05, read_memory_fn=lambda client, uds, mem, addr, size: bytes.fromhex('50485045'), sleep_fn=lambda _: None)
    except Exception as exc:
        static_rejected = 'progression is implausible' in str(exc)
    else:
        static_rejected = False
    check('static heartbeat cannot pass', static_rejected)
    foreign_reads = iter((bytes.fromhex('01020304'), bytes.fromhex('02020304')))
    try:
        _attest_once(FakeClient(f181=ALBINO_APP_F181), FakeUds, heartbeat_interval=0.05, read_memory_fn=lambda client, uds, mem, addr, size: next(foreign_reads), sleep_fn=lambda _: None)
    except Exception as exc:
        foreign_rejected = 'canary signature' in str(exc)
    else:
        foreign_rejected = False
    check('unrelated changing RAM cannot masquerade as canary heartbeat', foreign_rejected)
    try:
        _attest_once(FakeClient(f181=b'wrong'), FakeUds, heartbeat_interval=0.05, read_memory_fn=lambda *args: bytes(4), sleep_fn=lambda _: None)
    except Exception as exc:
        wrong_app_rejected = 'application F181 mismatch' in str(exc)
    else:
        wrong_app_rejected = False
    check('wrong application identity cannot pass', wrong_app_rejected)
    source = (ROOT / 'exploit/ephemeral_runtime/corolla_hf_direct_canary.py').read_text(encoding='utf-8')
    check('live mode is double-gated', '--execute requires --bench-isolated' in source)
    check('tool cannot expose command5 proxy', 'corolla_hf_command5_proxy.bin' not in source and 'command5_proxy_authorized_by_this_plan' in source)
    check('no flash write primitive is imported', all((token not in source for token in ('flash_erase', 'flash_program', 'erase_codeflash', 'write_codeflash', 'exploit.patcher'))))
_section_corolla_hf_direct_canary()
print()
print('== corolla hf cooperative authority wire visibility ==')

def _section_corolla_hf_cooperative_authority_wire_visibility():
    import hashlib
    import json
    import struct
    import subprocess
    import sys
    import tempfile
    from pathlib import Path
    ROOT = Path(__file__).resolve().parents[1]
    ART = ROOT / 'data/generated/corolla_hf_cooperative_authority_wire_visibility.json'
    EVID = ROOT / 'data/generated/corolla_8965H1202000_cooperative_authority_wire_decompiler_evidence.json'
    BUILDER = ROOT / 'tools/build_corolla_hf_cooperative_authority_wire_visibility.py'
    H = ROOT / 'community/albinoelephant/normalized/8965H1202000_CodeFlash.bin'
    H_RAW = ROOT / 'community/albinoelephant/raw-20260818/albinoelephant-corolla-2023.20260814-0023/dump_codeflash_00000000_00200000_20260814-025814.bin'
    F_RAW = ROOT / 'community/spanconstant/raw-20260821/span-corolla-2025.20260821-1511/dump_codeflash_00000000_00200000_20260821-152033.bin'

    def sha(data: bytes) -> str:
        return hashlib.sha256(data).hexdigest()
    artifact = json.loads(ART.read_text())
    evidence = json.loads(EVID.read_text())
    h = H.read_bytes()
    check('schema exact', artifact['schema'] == 'corolla-hf-cooperative-authority-wire-visibility-v1')
    check('exact variants only', artifact['software_ids'] == ['8965H1202000', '8965F1208000'])
    check('exact H image identity', len(h) == 1048576 and sha(h) == '0b47bdc1217835c839e3543e52eab40eb793650a9c159e46f6a9b365ea41a67f')
    check('promoted evidence count', evidence['function_count'] == 16 and artifact['sources']['decompiler_evidence']['function_count'] == 16)
    body_ok = True
    for row in evidence['functions']:
        entry = int(row['entry'], 16)
        body_ok &= sha(h[entry:entry + row['body_size']]) == row['body_sha256']
        body_ok &= sha(row['decompiled_c'].encode()) == row['decompiled_c_sha256']
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
    check('0x030 alone carries recovered coarse path', 'three duplicated coarse' in pdus[0]['classification'] and all(('coarse' not in row['classification'] for row in pdus[1:])))
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
    check('negative boundary names excluded mechanisms', all((term in artifact['evidence_boundary'] for term in ['mutable runtime pointers', 'DMA/peripheral', 'physical actuator', 'No live authority transition'])))
    print('\n== documentation/status integration ==')
    state_doc = (ROOT / 'docs/variants/corolla-h-f-openpilot-state-bridge.md').read_text()
    findings = (ROOT / 'docs/status/FINDINGS.md').read_text()
    check('canonical report records coarse-not-exact authority boundary', all((x in state_doc for x in ('### 6.6', 'FEBEF000 < 2', 'B6[3]', 'B10[3]', 'B13[4]', 'cannot be used as an exact cooperative-authority signal'))))
    check('TMS-056 integrated', '| TMS-056 |' in findings and 'cooperative_authority_wire_visibility.json' in findings)
_section_corolla_hf_cooperative_authority_wire_visibility()
print()
print('== corolla hf b6 competing sender arbitration ==')

def _section_corolla_hf_b6_competing_sender_arbitration():
    import hashlib
    import json
    import subprocess
    import sys
    import tempfile
    from pathlib import Path
    ROOT = Path(__file__).resolve().parents[1]
    ART = ROOT / 'data/generated/corolla_hf_b6_competing_sender_arbitration.json'
    EVID = ROOT / 'data/generated/corolla_8965H1202000_b6_competing_sender_decompiler_evidence.json'
    EXTRACTOR = ROOT / 'tools/extract_corolla_h_b6_competing_sender_evidence.py'
    BUILDER = ROOT / 'tools/build_corolla_hf_b6_competing_sender_arbitration.py'
    H = ROOT / 'community/albinoelephant/normalized/8965H1202000_CodeFlash.bin'
    DOC = ROOT / 'docs/variants/corolla-h-f-openpilot-state-bridge.md'
    FINDINGS = ROOT / 'docs/status/FINDINGS.md'
    CORRECTIONS = ROOT / 'docs/status/CORRECTIONS.md'

    def sha(data: bytes) -> str:
        return hashlib.sha256(data).hexdigest()
    a = json.loads(ART.read_text())
    ev = json.loads(EVID.read_text())
    h = H.read_bytes()
    check('schema', a['schema'] == 'corolla-hf-b6-competing-sender-arbitration-v1')
    check('exact H/F scope', a['applies_to'] == ['8965H1202000', '8965F1208000'] and a['cross_variant']['h_f_application_byte_identical'])
    check('non-enabling boundary', not a['suppression_conclusion']['parallel_injection_safe'] and (not a['suppression_conclusion']['freshness_preemption_is_safe_coexistence']))
    print('\n== promoted target-native evidence ==')
    check('evidence schema/count', ev['schema'] == 'corolla-h-b6-competing-sender-decompiler-evidence-v1' and ev['function_count'] == 12)
    check('extractor hash pinned', ev['generator']['sha256'] == sha(EXTRACTOR.read_bytes()))
    check('H image hash pinned', ev['image']['sha256'] == sha(h))
    body_ok = True
    for row in ev['functions']:
        entry = int(row['entry'], 16)
        size = row['body_size']
        body_ok &= sha(h[entry:entry + size]) == row['body_sha256']
    check('all promoted raw H bodies pinned', body_ok)
    roles = {r['role'] for r in ev['functions']}
    check('queue/delivery/sequence/request roles all promoted', {'secoc_secured_pdu_ingress', 'secoc_queue_first_insert', 'secoc_queue_existing_slot_update', 'secoc_pending_or_retry_to_verify', 'com_rx_indication_single_shadow_copy', 'b6_application_sequence_delta', 'b6_sequence_scaled_target_plausibility', 'b6_target_lateral_id_decoder'}.issubset(roles))
    print('\n== receiver/source identity ==')
    r = a['receiver_identity']
    check('one B6 identity', r['can_id'] == '0x0B6' and r['application_pdu_id'] == 42 and (r['authenticated_data_id'] == '0x00B6'))
    check('one ordinary freshness identity', r['freshness_id'] == 2 and r['normal_freshness_slot'] == 1)
    check('slot4 shared crypto selection', r['crypto_slot'] == 4)
    check('no source ID in recovered authenticated input', not r['separate_source_identifier_in_authenticated_input'])
    check('no source-specific acceptance recovered', not r['source_specific_acceptance_recovered'])
    print('\n== one-slot SecOC queue arbitration ==')
    q = a['single_profile_queue']
    check('single B6 queue multiplicity', q['queue_multiplicity'] == 1 and q['not_a_source_priority_queue'])
    check('idle first arrival inserts', 'E1->D2' in q['idle_E1'] and '0x87CD6' in q['idle_E1'])
    check('pending arrival coalesces into existing slot', '0x87DB0' in q['pending_D2'] and 'does not create a second' in q['pending_D2'])
    check('pending stage is last-arrival-wins', 'last B6 arrival' in q['pending_arbitration'])
    check('inflight C3/B4 arrivals not admitted', 'ignored' in q['inflight_arbitration'] and 'C3' in q['verify_C3_or_retry_B4'] and ('B4' in q['verify_C3_or_retry_B4']))
    print('\n== freshness arbitration ==')
    fresh = a['freshness_arbitration']
    check('single shared committed B6 freshness', fresh['committed_state_is_shared_per_b6_profile'])
    check('freshness commits before normal verified COM delivery', fresh['commit_before_normal_verified_application_delivery'])
    check('same low2 after committed10 reconstructs 14', fresh['same_low2_reference_examples']['committed10_received_low2_2'] == 14)
    check('next low2 after committed10 reconstructs 11', fresh['same_low2_reference_examples']['committed10_received_low2_3'] == 11)
    check('same-full-freshness replay cannot reuse committed freshness', 'next congruent' in fresh['same_full_freshness_replay_after_commit'] and 'fails verification' in fresh['same_full_freshness_replay_after_commit'])
    check('same-freshness verification failure has bounded delivery exception', 'failure forwarding grace/global-override' in fresh['same_full_freshness_replay_after_commit'] and 'without committing freshness' in fresh['same_full_freshness_replay_after_commit'])
    ffd = fresh['verification_failure_forwarding_exception']
    check('failure-forward grace geometry joined', ffd['grace_limit'] == 204 and ffd['b6_profile_plus_0x09'] == 0)
    check('failure-forward never authenticates/commits', 'never commits freshness' in ffd['behavior'] and 'does not turn' in ffd['arbitration_effect'])
    check('future valid freshness has no source lock', 'no source lock' in fresh['future_freshness_from_another_capable_sender'])
    check('capable senders race shared freshness', 'race one shared freshness' in fresh['consequence'])
    print('\n== application sequence is not sender arbitration ==')
    s = a['application_sequence_arbitration']
    check('signal261 modulo64/gap8', s['signal_id'] == 261 and s['modulus'] == 64 and ('min(delta,8)' in s['effective_gap']))
    check('strict +1 not required by EPS', not s['strict_plus_one_required_by_eps'])
    check('duplicate app sequence not rejected', not s['duplicate_sequence_rejected'] and s['examples']['same_application_sequence'] == {'raw_delta': 0, 'effective_gap': 1})
    check('strict +1 and gap4 examples', s['examples']['strict_plus_one'] == {'raw_delta': 1, 'effective_gap': 1} and s['examples']['gap_four'] == {'raw_delta': 4, 'effective_gap': 4})
    check('large app gap capped8', s['examples']['large_gap_capped'] == {'raw_delta': 19, 'effective_gap': 8})
    check('sequence feeds target plausibility', '0xCB4F4' in s['plausibility_use'] and '78 raw' in s['plausibility_use'])
    print('\n== request ID and application shadow ==')
    req = a['request_id_arbitration']
    check('accepted request dictionary exact', req['accepted_active_ids'] == {'1': 'PCS', '4': 'LDA', '10': 'Hands Off LTA', '11': 'LTA/LCA', '19': 'PDA'})
    check('no request priority order recovered', req['priority_order_recovered'] is None and 'no competing-request history' in req['behavior'])
    check('later delivered request can replace profile', 'later successfully delivered B6' in req['conclusion'])
    d = a['application_delivery']
    check('single PDU42 shadow', d['shared_shadow_pdu'] == 42 and d['entry'] == '0x00076A3C')
    check('sequential accepted B6 overwrites current shadow', 'overwrites' in d['sequential_valid_frames'])
    check('last successful delivery is current command', 'last successfully delivered' in d['effective_policy'])
    print('\n== hypothesis resolution / suppression policy ==')
    hyp = a['hypothesis_resolution']
    check('newest application sequence winner disproved', hyp['newest_application_sequence_wins'].startswith('disproved'))
    check('source-specific arbitration not recovered', hyp['source_specific_acceptance'].startswith('not recovered'))
    check('frame winner is stage-dependent', hyp['first_or_last_frame_wins'].startswith('stage-dependent'))
    check('request priority disproved', hyp['request_id_priority'].startswith('disproved'))
    check('freshness is source-agnostic', 'not source-specific' in hyp['freshness_rejects_competing_sender'])
    policy = a['suppression_conclusion']
    check('EPS does not require named stock identity', not policy['eps_protocol_requires_named_stock_source'])
    check('deterministic lateral requires exclusive B6 authority', policy['deterministic_lateral_authority_requires_exclusive_b6_control'])
    check('production policy requires stock suppression or proved quiescence', 'Suppress/isolate' in policy['production_policy'] and 'quiescent' in policy['production_policy'])
    check('freshness racing explicitly forbidden as coexistence', 'Do not use freshness racing' in policy['production_policy'])
    check('physical relay-side identity remains dynamic', 'Static receiver logic cannot identify' in policy['physical_topology_boundary'])
    print('\n== canonical documentation ==')
    doc = DOC.read_text()
    findings = FINDINGS.read_text()
    corrections = CORRECTIONS.read_text()
    check('canonical report records competing-sender arbitration', 'Competing valid B6 senders: receiver arbitration and suppression requirement' in doc)
    check('canonical report forbids freshness racing', 'Freshness racing or' in doc and 'not a safe coexistence/fallback mechanism' in doc)
    check('canonical report keeps physical suppression point dynamic', 'Static receiver logic cannot identify which physical relay side' in doc)
    check('COM-016 finding registered', '| COM-016 |' in findings and 'competing-sender arbitration is source-agnostic' in findings)
    check('CORR-111 failure-forward correction registered', '### CORR-111' in corrections and 'not universally non-delivering' in corrections)
    print('\n== builder reproducibility ==')
_section_corolla_hf_b6_competing_sender_arbitration()
print()
print('== corolla hf fault state contract ==')

def _section_corolla_hf_fault_state_contract():
    import json, subprocess, sys, tempfile
    from pathlib import Path
    REPO = Path(__file__).resolve().parents[1]
    ART = REPO / 'data/generated/corolla_hf_fault_state_contract.json'
    TOOL = REPO / 'tools/build_corolla_hf_fault_state_contract.py'
    d = json.loads(ART.read_text())
    check('schema/software family exact', d['schema'] == 'corolla-hf-0x394-fault-state-contract-v1' and d['software_ids'] == ['8965H1202000', '8965F1208000'])
    check('0x394 geometry exact', d['wire']['can_id'] == '0x394' and d['wire']['length'] == 3 and (len(d['wire']['state_table_rows']) == 17))
    check('complete DEM class census exact', d['dem']['class_counts'] == {'0x01': 8, '0x02': 34, '0x04': 1, '0x08': 1, '0x0F': 1, '0x10': 173, '0x20': 16, '0x40': 1, '0x80': 7} and sum(d['dem']['class_counts'].values()) == 242)
    ct = d['dem']['class_to_state']
    check('class2/4 paired-state mapping exact', ct['0x02']['states'] == [6, 7] and ct['0x04']['states'] == [8, 9])
    check('direct class branches exact', ct['0x10']['states'] == [10] and ct['0x20']['states'] == [11] and (ct['0x40']['states'] == [12]) and (ct['0x08']['states'] == [13]) and (ct['0x0F']['states'] == [14]))
    check('class80 is bounded general fallback', ct['0x80']['states'] == [16] and 'not unique' in ct['0x80']['selection'])
    check('classF0 supported but absent in event table', 'no exact-H event-table row' in ct['0xF0']['selection'] and '0xF0' not in d['dem']['class_counts'])
    check('class01 populated but not accumulator-consumed', ct['0x01']['states'] == [] and 'not consumed' in ct['0x01']['selection'])
    a = d['aging']
    check('paired-state aging constants exact', a['class2_primary_age'] == 200 and a['class4_primary_age'] == 200 and (a['class2_class4_secondary_age'] == 600) and (a['primary_clear_enable_age'] == 17736))
    n = d['named_dtc_families']
    check('named DTC family cardinalities exact', len(n['class_0x01_no_direct_394_accumulator_effect']) == 6 and len(n['class_0x02_states_6_7']) == 11 and (len(n['class_0x10_state_10']) == 50) and (len(n['class_0x20_state_11']) == 6))
    check('class10 includes Brake missing-message DTC', any((x['code'] == 'U012987' and x['failure'] == 'Missing Message' for x in n['class_0x10_state_10'])))
    check('class20 includes steering-angle comm incompatibility family', any((x['code'] == 'U012687' for x in n['class_0x20_state_11'])) and any((x['code'] == 'U032857' for x in n['class_0x20_state_11'])))
    check('openpilot temporary/permanent remains bounded', d['openpilot_boundary']['steerFaultTemporary'] == 'unresolved policy mapping' and d['openpilot_boundary']['steerFaultPermanent'] == 'unresolved policy mapping')
    doc = (REPO / 'docs/variants/corolla-h-f-openpilot-state-bridge.md').read_text()
    findings = (REPO / 'docs/status/FINDINGS.md').read_text()
    check('canonical doc records 242-event class closure', '### 6.7' in doc and '242' in doc and ('200' in doc) and ('600' in doc))
    check('TMS-058 integrated', '| TMS-058 |' in findings and 'corolla_hf_fault_state_contract.json' in findings)
_section_corolla_hf_fault_state_contract()
print()
print('== corolla hf panda lateral safety contract ==')

def _section_corolla_hf_panda_lateral_safety_contract():
    import json
    import subprocess
    import sys
    import tempfile
    from pathlib import Path
    ROOT = Path(__file__).resolve().parents[1]
    ART = ROOT / 'data/generated/corolla_hf_panda_lateral_safety_contract.json'
    BUILDER = ROOT / 'tools/build_corolla_hf_panda_lateral_safety_contract.py'

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
    check('application sequence explicitly separate from SecOC', 'not SecOC message8' in wire['secoc_boundary'])
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
    check('driver torque acquisition clamp is not override', abs(m['driver_torque']['acquisition_clamp_abs_nm'] - 8.23828125) < 1e-09 and 'not driver-override thresholds' in m['driver_torque']['override_boundary'])
    check('driver torque telemetry saturation is not override', m['driver_torque']['telemetry_saturation_abs_nm'] == 10.0 and 'not driver-override thresholds' in m['driver_torque']['override_boundary'])
    check('selected fault/inhibit is immediate cutout candidate', m['steering_fault_inhibit']['nominal_clear_value'] == 0 and 'immediate controls cutout' in m['steering_fault_inhibit']['candidate_action'])
    p = d['candidate_panda_subset']
    check('candidate Panda subset still disabled', not p['enabled'])
    check('candidate restricts active request to LTA/LCA', any(('ID 11' in x for x in p['tx_requirements'])))
    check('candidate rejects other EPS request profiles', any(('Reject all other' in x for x in p['tx_requirements'])))
    check('candidate requires strict +1 sequence', any(('exactly +1 modulo 64' in x for x in p['tx_requirements'])))
    check('candidate applies single-step 78-count delta', any(('<= 78 raw counts' in x for x in p['tx_requirements'])))
    check('candidate inactive command is ID0/target0', any(('ID 0 and target angle 0' in x for x in p['tx_requirements'])))
    check('secondary B6 values have bounded minimal candidate but still require validation', p['secondary_b6_fields']['policy'] == 'not an unresolved Panda threshold' and '258=1' in p['secondary_b6_fields']['boundary'] and ('cross-ECU' in p['secondary_b6_fields']['boundary']) and ('whitelist' in p['secondary_b6_fields']['boundary']))
    check('sender lapse now records nominal 35 ms EPS cutout', p['sender_lapse']['milliseconds'] == 35.0)
    u = d['unresolved_safety_parameters']
    check('only three bounded safety-policy parameter classes remain', set(u) == {'driver_override_abs_nm', 'extended_fault_policy', 'actuator_response_fault_threshold'})
    check('driver override parameter is intentionally unset policy not OEM recovery', u['driver_override_abs_nm']['value'] is None and u['driver_override_abs_nm']['classification'] == 'deliberate-panda-policy-not-unrecovered-oem-comparator' and ('no Toyota EPS' in u['driver_override_abs_nm']['missing_evidence']))
    check('extended fault policy is intentionally unset with immediate gate known', u['extended_fault_policy']['value'] is None and 'disable' in u['extended_fault_policy']['known_immediate_gate'])
    check('actuator response threshold intentionally unset', u['actuator_response_fault_threshold']['value'] is None)
    check('actuator response is reclassified as no recovered OEM measured-Q threshold', u['actuator_response_fault_threshold']['classification'] == 'no-recovered-oem-measured-q-current-threshold' and 'FEBEAE16' in u['actuator_response_fault_threshold']['static_firmware_result'])
    check('future actuator response remains deliberate Panda/sender policy', 'separate safety policy' in u['actuator_response_fault_threshold']['policy_boundary'])
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
    check('Panda does not transplant TSS2 speed-angle/current limits', 'speed-angle curves' in d['not_promoted_as_safety_limits']['legacy_toyota_lta_limits'] and 'measured_q_current' in d['not_promoted_as_safety_limits'])
    check('static conclusion keeps Q-current OEM threshold negative', d['static_conclusion']['measured_q_current_observable_closed_but_oem_response_threshold_not_recovered'])
    check('static conclusion keeps speed-dependent hard reduction negative', d['static_conclusion']['speed_dependent_hard_angle_reduction_not_recovered'])
    check('static conclusion closes nominal 35ms loss cutout', d['static_conclusion']['eps_loss_cutout_nominal_wall_clock_ms'] == 35.0)
    check('static conclusion reclassifies driver override as Panda policy', d['static_conclusion']['driver_torque_signal_closed'] and d['static_conclusion']['driver_override_is_panda_policy_not_eps_static_recovery_blocker'])
    check('static conclusion separates stock cadence from replacement freshness', d['static_conclusion']['wall_clock_sender_cadence_open'] and d['static_conclusion']['replacement_sender_freshness_policy_closed_independently_of_stock_cadence'])
_section_corolla_hf_panda_lateral_safety_contract()
print()
print('== corolla hf secoc 00f freshness bridge ==')

def _section_corolla_hf_secoc_00f_freshness_bridge():
    import hashlib
    import json
    from pathlib import Path
    REPO = Path(__file__).resolve().parents[1]
    ART = json.loads((REPO / 'data/generated/corolla_hf_secoc_00f_freshness_bridge.json').read_text())
    H = json.loads((REPO / 'data/generated/corolla_8965H1202000_b6_secoc_verification.json').read_text())
    DECOMP = json.loads((REPO / 'data/generated/corolla_8965H1202000_b6_secoc_verification_decompiler_evidence.json').read_text())
    COMP = json.loads((REPO / 'data/generated/corolla_h_sienna_secoc_structural_comparison.json').read_text())
    ALBINO = REPO / 'community/albinoelephant/can_oracle.ndjson'
    print('== exact H/F synchronization profile and wire layout ==')
    prof = COMP['profile_tables']['corolla_h_f']['records'][0]
    static = ART['static_h_f_receiver']
    wire = static['wire_layout']
    check('artifact schema/title pinned', ART['schema'] == 1 and '0x00F' in ART['title'])
    check('H/F application identity applies', static['applies_to']['corolla_h_f_application_identical'] is True)
    check('H/F sync profile is DataID 0x00F freshness ID0', prof['data_id'] == '0x00F' and prof['freshness_id'] == 0)
    check('H/F sync profile record address exact', prof['address'] == '0x0002572C')
    check('sync PDU is exactly eight bytes', prof['secured_pdu_length'] == prof['input_buffer_length'] == 8)
    check('sync freshness is full/transmitted FV36', prof['full_freshness_bits'] == prof['transmitted_freshness_bits'] == 36)
    check('sync CMAC is 128 -> MSB28', prof['full_cmac_bits'] == 128 and prof['transmitted_cmac_bits'] == 28)
    check('sync has no auth or CryptoIf-busy retry', prof['authentication_retry_limit'] == prof['cryptoif_busy_retry_limit'] == 0)
    check('artifact profile is independently pinned to raw profile', static['profile_record']['record_sha256'] == prof['record_sha256'])
    check('sync has no application payload', wire['application_payload_bytes'] == 0)
    check('sync trip occupies B0:B1', wire['B0_B1'] == 'trip16, big-endian')
    check('sync reset occupies B2:B4 high nibble', wire['B2_B3_B4_7_4'] == 'reset20, big-endian')
    check('sync MAC28 occupies B4 low nibble through B7', wire['B4_3_0_B5_B6_B7'] == 'CMAC_MSB28')
    check('sync FV36 is trip16||reset20', wire['freshness36'] == 'trip16 || reset20')
    check('sync CMAC input is seven bytes', wire['authenticated_input'] == '00 0F || trip16 || reset20 || 0000b' and wire['authenticated_input_bytes'] == 7)
    print('\n== target-native H receiver functions ==')
    funcs = {f['entry']: f for f in DECOMP['functions']}
    bind = static['decompiler_bindings']
    for role, entry in {'authenticated_input_build': '0x00087FC2', 'sync_pack': '0x000899B4', 'sync_parse': '0x00089B46', 'sync_reconstruct': '0x00089F6E', 'sync_commit': '0x0008A130', 'normal_reset_search': '0x00089CDA', 'normal_window': '0x00089D58'}.items():
        check(f'{role} entry/hash bound to target-native decompiler', bind[role]['entry'] == entry and bind[role]['body_sha256'] == funcs[entry]['body_sha256'])
    check('sync parser decodes B0:B1 trip', 'CONCAT11(*param_1,param_1[1])' in funcs['0x00089B46']['decompiled_c'])
    check('sync parser decodes B2:B4 reset', 'param_1[4] >> 4' in funcs['0x00089B46']['decompiled_c'])
    check('sync packer writes five freshness bytes', 'param_2[4] = (char)(param_1[1] << 4)' in funcs['0x000899B4']['decompiled_c'])
    check('global 00F state addresses remain exact', static['ram_state']['current_state'] == ['0xFEBE54AC', '0xFEBE54B0'])
    check('sync commit is authentication-gated', static['ram_state']['commit_only_after_authentication_success'] is True)
    check('trip wrap threshold remains 15', static['sync_acceptance']['trip_wrap_threshold'] == 15)
    check('authenticated trip wrap clears B6/D7 state', static['sync_acceptance']['trip_wrap_clears_b6_and_d7'] is True)
    print('\n== ordinary D7/B6 freshness relationship ==')
    ordf = static['ordinary_freshness']
    check('D7 and B6 have distinct ordinary freshness IDs', ordf['d7_freshness_id'] == 1 and ordf['b6_freshness_id'] == 2)
    check('ordinary D7/B6 slots are independent', ordf['independent_ordinary_slots'] is True)
    check('FV4 split is message-low2 then reset-low2', ordf['wire_fv4']['decode'] == {'message_low2': 'B28[7:6]', 'reset_low2': 'B28[5:4]'})
    check('ordinary full freshness is exact', ordf['full_freshness'] == 'trip16 || reset20 || message8 || reset_low2 || 00b')
    check('reset search exact order', ordf['reset_candidate_search']['ordered_trials'] == ['current', 'current-1', 'current+1', 'current-2', 'current+2'])
    check('same-epoch window is strict-forward +1..+4', ordf['same_epoch_message_rule']['strictly_forward'] is True and ordf['same_epoch_message_rule']['ordinary_forward_delta'] == [1, 4])
    check('new epoch seeds message from received low2', ordf['new_epoch_message_rule'] == 'received_message_low2 (0..3)')
    print('\n== Albino same-investigation sync oracle ==')
    alb = ART['captures']['albino_2023_tskm_sync_oracle']
    check('Albino raw oracle SHA pinned', hashlib.sha256(ALBINO.read_bytes()).hexdigest() == alb['source']['sha256'] == '8863398a98875a853e722a6ba83fc10563d5764cea33719c8af34225efa189a3')
    check('Albino oracle has 1232 sync rows split 616/616', alb['rows'] == 1232 and alb['rows_per_bus'] == {'0': 616, '2': 616})
    check('Albino bus0/bus2 sync payload sequences identical', alb['bus0_bus2_payload_sequences_identical'] is True)
    check('Albino trip is exactly 0x0D0D', alb['trip_values_hex'] == ['0x0D0D'])
    check('Albino has 206 unique sync states', alb['unique_states'] == 206)
    check('Albino reset states mostly advance +1', alb['reset_transition_deltas'] == {'1': 204, '115': 1})
    check('Albino state copies are byte-identical', alb['all_repeated_state_payloads_byte_identical'] is True)
    check('Albino normal reset cadence median is ~300ms', 295000000 <= alb['state_transition_period_ns_median'] <= 305000000)
    check('Albino collection gap remains explicitly bounded', alb['initial_collection_gap']['observed_reset_delta'] == 115 and 'collection artifact' in alb['initial_collection_gap']['interpretation'])
    print('\n== Span moving-rlog dynamic replay ==')
    span = ART['captures']['span_2025_discord']
    ss = span['sync_00f']
    sd = span['d7_receiver_model_replay']
    st = span['transition_ordering']
    check('Span has 600 00F and 3000 D7 frames', span['wire_counts']['0x00F'] == 600 and span['wire_counts']['0x0D7'] == 3000)
    check('Span trip is 0x162D and constant', ss['trip_values_hex'] == ['0x162D'])
    check('Span reset advances 1037->1237', ss['reset_first'] == 1037 and ss['reset_last'] == 1237)
    check('Span 00F wire cadence ~100ms', 99000000 <= ss['frame_period_ns_median'] <= 101000000)
    check('Span reset epoch cadence ~300ms', 299000000 <= ss['state_transition_period_ns_median'] <= 301000000)
    check('Span all 199 inter-transition intervals near 300ms', ss['state_transition_intervals_280_to_320ms'] == ss['state_transition_interval_count'] == 199)
    check('Span reset transition is +1 exactly 200 times', ss['reset_transition_deltas_same_trip'] == {'1': 200})
    check('Span duplicate sync states are byte/MAC identical', ss['all_repeated_state_payloads_byte_identical'] is True and ss['all_repeated_state_mac28_identical'] is True)
    check('Span has one unique MAC28 per sync state', ss['unique_mac28_count'] == ss['unique_states'] == 201)
    check('H reset search maps every post-sync Span D7', sd['unmapped_after_first_sync'] == 0 and span['wire_counts']['mapped_0x0D7_after_first_00F'] == 2997)
    check('Span live reset candidates are current/current-1 only', sd['candidate_delta_counts'] == {'-1': 200, '0': 2797})
    check('Span same-epoch reconstructed message8 always +1', sd['same_epoch_message8_delta_counts'] == {'1': 2796})
    check('Span has 199 complete 15-frame D7 epochs', sd['complete_15_frame_epochs'] == 199)
    check('every complete Span epoch is message8 1..15', sd['complete_epochs_exact_message8_1_through_15'] == 199)
    check('all non-initial Span epochs begin message-low2=1', sd['non_initial_epoch_first_message_low2'] == {'1': 200})
    check('all Span sync transitions record one same-timestamp old-reset D7 after the new 00F', st['d7_same_timestamp_after_sync_using_previous_reset_low2'] == st['sync_state_transitions'] == 200)
    check('no same-timestamp old-reset Span D7 precedes the new 00F in logged array order', st['d7_same_timestamp_before_sync_using_previous_reset_low2'] == 0)
    check('all after-sync old-reset D7 frames end at message-low2=3', st['those_after_sync_previous_reset_frames_with_message_low2_3'] == 200)
    check('new-reset D7 follows ~20ms later', 19000000 <= st['first_d7_new_reset_delay_ns_min'] <= st['first_d7_new_reset_delay_ns_median'] <= st['first_d7_new_reset_delay_ns_max'] <= 21000000)
    check('all first new-reset Span D7 frames start low2=1', st['first_d7_new_reset_message_low2'] == {'1': 200})
    check('cross-capture conclusion binds Span current-1 overlap to logged order', ART['cross_capture_conclusions']['span_logged_order_exercises_current_minus_1_overlap'] is True)
    print('\n== independent public-route replay ==')
    pub = ART['captures']['public_2023']
    ps = pub['sync_00f']
    pd = pub['d7_receiver_model_replay']
    check('public route has 588 00F and 2943 D7 frames', pub['wire_counts']['0x00F'] == 588 and pub['wire_counts']['0x0D7'] == 2943)
    check('public trip is 0x0CE9 and constant', ps['trip_values_hex'] == ['0x0CE9'])
    check('public reset states 224->428', ps['reset_first'] == 224 and ps['reset_last'] == 428)
    check('public sync cadence ~100ms', 99000000 <= ps['frame_period_ns_median'] <= 101000000)
    check('public reset cadence median ~300ms', 295000000 <= ps['state_transition_period_ns_median'] <= 305000000)
    check('public capture has 194/196 near-300ms transition intervals', ps['state_transition_intervals_280_to_320ms'] == 194 and ps['state_transition_interval_count'] == 196)
    check('H reset search maps every post-sync public D7', pd['unmapped_after_first_sync'] == 0 and pub['wire_counts']['mapped_0x0D7_after_first_00F'] == 2940)
    check('public live reset candidates are current/current-1 only', pd['candidate_delta_counts'] == {'-1': 196, '0': 2744})
    check('public same-epoch reconstructed message8 always +1', pd['same_epoch_message8_delta_counts'] == {'1': 2742})
    check('all 194 complete public epochs are message8 1..15', pd['complete_15_frame_epochs'] == pd['complete_epochs_exact_message8_1_through_15'] == 194)
    print('\n== B6 sender consequence and boundary ==')
    imp = ART['b6_sender_implication']
    check('00F exposes 36/46 meaningful B6 freshness bits', imp['what_00f_reveals'].startswith('36/46'))
    check('B6 message8 explicitly remains local', 'B6-local' in imp['what_remains_per_b6'] and 'must not be copied' in imp['what_remains_per_b6'])
    check('new authenticated epoch removes dependence on old B6 message8', 'does not require knowledge of the previous B6 message8' in imp['new_epoch_reanchor'])
    check('same-epoch sender still needs full message state', 'still needs the reconstructed full message8' in imp['same_epoch_boundary'])
    check('transition overlap is explicitly handled', 'current-1' in imp['transition_race'] and 'new 0x00F' in imp['transition_race'])
    check('slot4 secret remains unresolved', any(('slot-4 secret' in x for x in imp['still_blocking'])))
    check('live B6 sender policy remains unresolved', any(('live B6' in x for x in imp['still_blocking'])))
    check('capture identity boundary remains explicit', 'not exact H/F firmware-identity joins' in ART['evidence_boundary'])
    check('D7 message counter is not transferred to B6', 'No D7 message counter is transferred to B6' in ART['evidence_boundary'])
_section_corolla_hf_secoc_00f_freshness_bridge()
print()
print('== corolla hf direct command5 ==')

def _section_corolla_hf_direct_command5():
    import importlib.util
    import json
    import subprocess
    import sys
    import tempfile
    from pathlib import Path
    ROOT = Path(__file__).resolve().parents[1]
    TOOL = ROOT / 'exploit/ephemeral_runtime/corolla_hf_direct_command5.py'
    PROXY = ROOT / 'exploit/ephemeral_runtime/audited/corolla_hf_command5_proxy.bin'
    SOURCE = ROOT / 'exploit/ephemeral_runtime/corolla_hf_command5_proxy.c'
    spec = importlib.util.spec_from_file_location('hf_cmd5', TOOL)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    plan = mod.build_plan()
    check('schema exact', plan['schema'] == 'corolla-hf-direct-command5-v1')
    check('audited proxy identity exact', PROXY.stat().st_size == 462 and plan['package']['shellcode_sha256'] == '3bb96eefae06005c99a0ac52b7f0c64cc5d52e2b0b1fcbb73e0b4ec69609f8d3')
    check('direct proxy package identity exact', plan['package']['payload_sha256'] == 'a94979704010758dd09acc0e137977c8eed5003822eababa39eb8a7e5e9d5a58' and plan['package']['payload_size'] == 4096)
    check('package validates CRC and CMAC', plan['package']['crc_residue'] == '0xFFFFFFFF' and plan['package']['cmac_valid'] is True)
    check('field-proven zero-DID old-stack path retained', plan['field_proven_bootstrap']['did_0203'] == '0000000000' and plan['field_proven_bootstrap']['did_0201'] == '00' * 16 and (plan['field_proven_bootstrap']['did_0202'] == '00' * 16) and (plan['field_proven_bootstrap']['post_10f0_ram_substitution_required'] is False))
    probe = plan['probe']
    check('fixed selector4 B6-sized contract', probe['command5']['driver_record'] == 0 and probe['command5']['key_selector'] == 4 and (probe['command5']['input_length'] == 36) and (probe['command5']['expected_output_length'] == 16))
    check('mailbox contract exact', probe['mailbox'] == {'address': '0xFEBFFB80', 'size': 60, 'request_state_offset': 0, 'result_status_offset': 1, 'output_length_offset': 4, 'input_offset': 8, 'output_offset': 44})
    check('host uses sentinels and commits request state last', probe['host_commit_order'][-1] == 'write request_state=1 last' and '0xFE' in probe['host_commit_order'][2] and ('a5' in probe['host_commit_order'][1]))
    check('live stage requires canary plus reset confirmation', plan['live_guards']['successful_canary_result_required'] and plan['live_guards']['reset_to_stock_confirmation_required'] and plan['live_guards']['execute_and_bench_isolated_required'])
    check('no flash/steering transmission is part of probe', plan['live_guards']['flash_write_used'] is False and plan['live_guards']['steering_can_transmit_used'] is False)
    check('proxy source self-initializes before interrupts', 'm->request_state = 0u;\n  __asm__ volatile("ei");' in SOURCE.read_text())
    check('proxy mirrors completion status into mailbox', 'm->result_status = (unsigned char)(completion_state >> 8);' in SOURCE.read_text() and 'm->result_status = (unsigned char)rc;' in SOURCE.read_text())
    check('proxy samples adjacent completion bytes as halfword', 'volatile unsigned short *completion' in SOURCE.read_text() and '*completion = 0xff00u;' in SOURCE.read_text())
    with tempfile.TemporaryDirectory() as td:
        good = Path(td) / 'good.json'
        good.write_text(json.dumps({'schema': 'corolla-hf-direct-canary-v1', 'mode': 'live', 'created_at': 'test', 'live': {'attestation': {'attested': True, 'heartbeat_advanced': True, 'application_f181_hex': mod.ALBINO_APP_F181.hex(), 'heartbeat_first_hex': '43485045', 'heartbeat_second_hex': '44485045'}, 'panda_safety_tx_blocked_delta': 0, 'package': {'payload_sha256': '313d1bb70fe6147c179e4b5a35e4556e536f062a80d53d85af3d4292b0b29d84'}, 'reset_to_stock_checked': False}}))
        gate = mod.validate_canary_result(good)
        check('successful exact canary result is accepted', gate['application_f181_hex'] == mod.ALBINO_APP_F181.hex() and gate['panda_safety_tx_blocked_delta'] == 0)
        bad = Path(td) / 'bad.json'
        bad.write_text(json.dumps({'schema': 'corolla-hf-direct-canary-v1', 'mode': 'live', 'live': {'attestation': {'attested': False}}}))
        try:
            mod.validate_canary_result(bad)
            bad_rejected = False
        except mod.DirectCommand5Error:
            bad_rejected = True
        check('failed canary result is rejected', bad_rejected)
    originals = (mod._exchange, mod.parse_positive_response, mod._read_xcp, mod._write_xcp, mod.time.sleep)
    try:
        mem = bytearray(60)
        phases = {'poll': 0}
        writes = []
        output = bytes.fromhex('00112233445566778899aabbccddeeff')

        def fake_exchange(*args, **kwargs):
            return b'\xff'

        def fake_positive(*args, **kwargs):
            return None

        def fake_write(_panda, *, bus, timeout, address, data):
            off = address - mod.MAILBOX
            mem[off:off + len(data)] = data
            writes.append((address, bytes(data)))
            return 1

        def fake_read(_panda, *, bus, timeout, address, length):
            off = address - mod.MAILBOX
            if address == mod.MAILBOX and length == 2 and (mem[0] == 1):
                phases['poll'] += 1
                if phases['poll'] == 1:
                    return bytes((2, mod.RESULT_SENTINEL))
                mem[0] = 0
                mem[1] = 0
                mem[4:8] = 16 .to_bytes(4, 'little')
                mem[44:60] = output
            return bytes(mem[off:off + length])
        mod._exchange, mod.parse_positive_response = (fake_exchange, fake_positive)
        mod._write_xcp, mod._read_xcp, mod.time.sleep = (fake_write, fake_read, lambda _x: None)
        observed, meta = mod._execute_probe(object(), bus=1, timeout=0.1, completion_timeout=1, message=mod.DEFAULT_VECTOR)
        check('host state machine accepts queued then status-zero completion', observed == output and meta['result_status'] == 0 and meta['queued_state_observed'] and (meta['state_transitions_observed'] == [2, 0]))
        check('request_state commit is final host write', writes[-1] == (mod.MAILBOX, b'\x01'))
        check('output sentinel is replaced before success', observed != mod.OUTPUT_SENTINEL)
    finally:
        mod._exchange, mod.parse_positive_response, mod._read_xcp, mod._write_xcp, mod.time.sleep = originals
    proc = subprocess.run([sys.executable, str(TOOL)], cwd=ROOT, capture_output=True, text=True)
    check('plan-only CLI succeeds without hardware', proc.returncode == 0)
    if proc.returncode == 0:
        cli = json.loads(proc.stdout)
        check('plan-only CLI cannot claim live result', cli['mode'] == 'plan' and cli['live'] is None)
    proc = subprocess.run([sys.executable, str(TOOL), '--execute', '--bench-isolated', '--reset-to-stock-confirmed'], cwd=ROOT, capture_output=True, text=True)
    check('live CLI refuses missing canary result before hardware', proc.returncode != 0 and '--canary-result' in proc.stderr)
_section_corolla_hf_direct_command5()
print()
print('== corolla hf remaining status contract ==')

def _section_corolla_hf_remaining_status_contract():
    import hashlib, json, subprocess, sys, tempfile
    from pathlib import Path
    REPO = Path(__file__).resolve().parents[1]
    ART = REPO / 'data/generated/corolla_hf_remaining_status_contract.json'
    EVID = REPO / 'data/generated/corolla_8965H1202000_remaining_status_decompiler_evidence.json'
    TOOL = REPO / 'tools/build_corolla_hf_remaining_status_contract.py'
    IMAGE = REPO / 'community/albinoelephant/normalized/8965H1202000_CodeFlash.bin'
    d = json.loads(ART.read_text())
    e = json.loads(EVID.read_text())
    image = IMAGE.read_bytes()
    check('schema/software family exact', d['schema'] == 'corolla-hf-remaining-status-contract-v1' and d['software_ids'] == ['8965H1202000', '8965F1208000'])
    check('18 exact-H functions promoted', e['function_count'] == 18)
    check('all promoted bodies match exact H bytes', all((hashlib.sha256(image[int(x['entry'], 16):int(x['entry'], 16) + x['body_size']]).hexdigest() == x['body_sha256'] for x in e['functions'])))
    b = d['can_0x030_b6_bit1']
    check('B6[1] source is Q-axis actual current', b['wire'] == '0x030 B6[1]' and b['chain'][0] == 'FEBE6BAE Motor Actual Current (Q Axis)')
    check('B6[1] full threshold/debounce chain retained', all((x in ' '.join(b['chain']) for x in ('FEBEEC0C', 'FEBEAFC4', 'FEBEB64D', 'FEBEB64C', 'FEBEE848', 'FEBE7DB3'))))
    check('exact-H detector calibration exact', b['calibration']['feature_flag'] == 90 and b['calibration']['threshold_a'] == 5120 and (b['calibration']['threshold_b'] == 2560) and (b['calibration']['debounce_count'] == 0))
    check('exact-H detector is calibration-disabled', 'disabled' in b['classification'] and 'unreachable' in b['exact_h_calibration_effect'])
    check('Span is kept cross-specimen only', b['span_observation']['values'] == [0, 1] and 'not exact-F181-joined' in b['span_observation']['boundary'])
    f = d['can_0x351_force7']
    check('force7 condition exact', f['condition'] == '(FEBE65E4 & 0x0003) != 0 AND FEBE7E13 != 0')
    check('force7 status-bitmap bits exact', f['status_bitmap_side']['bits_used'] == [0, 1] and 'FEBE6FB4' in ' '.join(f['status_bitmap_side']['chain']))
    check('force7 24-record aggregate bit exact', f['record_aggregate_side']['record_count'] == 24 and f['record_aggregate_side']['bit_used'] == 15)
    check('force7 remains semantically bounded', 'does not assign Toyota names' in f['status_bitmap_side']['boundary'] and 'not recovered' in f['record_aggregate_side']['boundary'])
    check('force7 separated from C159B49', 'distinct from the C159B49' in f['classification'])
    doc = (REPO / 'docs/variants/corolla-h-f-openpilot-state-bridge.md').read_text()
    findings = (REPO / 'docs/status/FINDINGS.md').read_text()
    check('canonical doc records B6[1]/force7 closures', '### 6.8' in doc and 'Q-axis-current-derived' in doc and ('24' in doc) and ('bit **15**' in doc))
    check('TMS-059 integrated', '| TMS-059 |' in findings and 'corolla_hf_remaining_status_contract.json' in findings)
_section_corolla_hf_remaining_status_contract()
print()
print('== corolla hf command5 portability ==')

def _section_corolla_hf_command5_portability():
    import hashlib, json, subprocess, sys, tempfile
    from pathlib import Path
    REPO = Path(__file__).resolve().parents[1]
    ART = REPO / 'data/generated/corolla_hf_command5_portability.json'
    BUILDER = REPO / 'tools/build_corolla_hf_command5_portability.py'
    H = REPO / 'community/albinoelephant/normalized/8965H1202000_CodeFlash.bin'

    def sha(b):
        return hashlib.sha256(b).hexdigest()
    art = json.loads(ART.read_text())
    h = H.read_bytes()
    check('schema exact', art['schema'] == 'corolla-hf-command5-portability-v1')
    check('applies to H/F only', art['applies_to'] == ['8965H1202000', '8965F1208000'])
    core = art['command5_core']
    fields = core['record_fields']
    check('record0 raw bytes exact', core['driver_record_address'] == '0x00027C88' and core['driver_record_raw_hex'] == h[162952:162984].hex())
    check('record0 completion callback exact', fields['completion_callback'] == '0x00082F5C')
    check('record0 adapter exact', fields['adapter_callback'] == '0x000820CC')
    check('record0 worker exact', fields['worker_callback'] == '0x000821D0')
    check('record0 config pointer exact', fields['config_pointer'] == '0x00027C84' and core['config_type_word'] == 1)
    check('serialized command5 dispatcher exact', core['serialized_dispatcher'] == '0x00082750' and core['record_lookup'] == '0x00082702')
    check('variable length command5 input supports B6 36 bytes', core['variable_length_prepare'] == '0x00081E94' and core['maximum_input_bytes'] == 80 and (core['b6_authenticated_input_bytes'] == 36) and core['b6_authenticated_input_fits'])
    check('lower ICU-S command5 engine exact', core['lower_icus_engine'] == '0x00083A30' and core['command_word_formula'] == '(key_selector << 16) | 5')
    check('record0 completion state exact', core['synchronous_wrapper'] == '0x00082ED2' and core['done_flag'] == '0xFEBF1280' and (core['status_flag'] == '0xFEBF1281'))
    check('H/F application command5 path byte-identical', core['h_f_application_byte_identical'] is True)
    rb = art['resident_runtime_boundary']
    check('Sienna resident geometry explicitly does not transfer', rb['sienna_single_stage_geometry_transfers'] is False and rb['h_f_verified_ram_exec_requirement_entry_present'] is False)
    check('H startup clear ranges exact', rb['h_startup_clear_ranges_inclusive'] == [['0xFEBF05CC', '0xFEBF09CB'], ['0xFEBF0B4C', '0xFEBF0F4B']])
    check('naive FEBF0000 Sienna proxy rejected', 'does not authorize the Sienna 546-byte proxy' in rb['interpretation'] and 'TMS-054' in rb['interpretation'])
    two = art['two_stage_candidate']
    check('TMS053 two-stage shadow idea retained as historical bounded hypothesis', two['status'].startswith('historical-tms053') and two['xcp_write_shadow_bounds'] == ['0xFEBF7C00', '0xFEBFFBFF'] and ('TMS-054' in two['interpretation']) and ('Neither artifact proves' in two['interpretation']))
    con = art['static_conclusion']
    check('software machinery transfer closed', con['h_f_command5_software_machinery_transfers'] and con['b6_36_byte_input_supported'])
    check('resident signer and live policy remain open', not con['h_f_resident_signer_runtime_closed'] and (not con['slot4_live_permission_closed']) and (not con['signing_latency_closed']))
    check('evidence boundary rejects working-oracle overclaim', 'working H/F' in art['evidence_boundary'] and 'still requires live carrier retention' in art['evidence_boundary'])
_section_corolla_hf_command5_portability()
print()
print(f'\n== RESULT: {passed} passed, {failed} failed ==')
raise SystemExit(1 if failed else 0)
