#!/usr/bin/env python3
"""Portable Corolla H static-residue and coverage pins: crypto, diagnostic, and final named residue, static coverage, structural residue inspection, CAN comms, and XCP surface.

Domain split; assertions and helpers are carried over verbatim.
"""
from __future__ import annotations

import hashlib

from tools import REPO_ROOT
ROOT = REPO = REPO_ROOT
passed = failed = 0

def sha(data):
    return hashlib.sha256(data).hexdigest()

def check(name, cond, detail=''):
    global passed, failed
    ok = bool(cond)
    passed += int(ok)
    failed += int(not ok)
    suffix = f' ({detail})' if detail else ''
    print(f"[{'PASS' if ok else 'FAIL'}][raw_bytes] {name}{suffix}")


def _section_crypto_residue():
    print('== crypto residue ==')
    """Verify target-native recovery of the final seven H crypto roles."""
    import json
    ROOT=REPO_ROOT
    ART=ROOT/'data/generated/corolla_8965H1202000_crypto_residue.json';EV=ROOT/'data/generated/corolla_8965H1202000_crypto_residue_decompiler_evidence.json';HRAW=ROOT/'community/albinoelephant/raw-20260818/albinoelephant-corolla-2023.20260814-0023/dump_codeflash_00000000_00200000_20260814-025814.bin'
    a=json.loads(ART.read_text());e=json.loads(EV.read_text());H=HRAW.read_bytes()[:0x100000];by={int(x['target_entry'],16):x for x in e['functions']}
    check('H image hash pinned',sha(H)==e['image']['codeflash_sha256']==a['images']['h_sha256']);check('all raw H bodies validate',all(sha(H[int(x['target_entry'],16):int(x['target_entry'],16)+x['target_reported_body_size']])==x['body_sha256'] for x in e['functions']))
    exp={'0x000070FC':'0x000070E0','0x00068F0C':'0x00063244','0x00068F92':'0x000632CA','0x00068FC2':'0x000632FA','0x00069018':'0x00063350','0x00088302':'0x00082702','0x00088508':'0x00082908'};check('all seven role mappings exact', {x['reference_entry']:x['target_entry'] for x in a['crypto_role_closure']}==exp)
    pf=a['payload_crypto_finalize'];check('payload finalize is exact 12-byte relocated wrapper',pf['exact_body_equal'] and pf['body_size']==12 and pf['h']=='0x000070E0');check('payload finalize is role-bound by relocated clear call',pf['h_calls_clear'] and pf['clear_delta']==-0x1c and 'FUN_000070c8' in by[0x70e0]['decompiled_c'])
    b=a['crypto_test_banks'];check('bank0 preserves eight-counter snapshot',b['bank0']['snapshot']['h_counter_indices']==list(range(10,18)) and b['bank0']['snapshot']['sienna_counter_indices']==list(range(12,20)));check('bank1 preserves five-counter snapshot',b['bank1']['snapshot']['h_counter_indices']==list(range(18,23)) and b['bank1']['snapshot']['sienna_counter_indices']==list(range(20,25)));check('both H counter cohorts shift by -2',b['bank0']['index_shift']==[-2]*8 and b['bank1']['index_shift']==[-2]*5);check('bank0 activation keeps active/state 0x11 lifecycle',all(t in by[0x632ca]['decompiled_c'] for t in ('cRamfebe4f82','uRamfebe4f83 = 0x11','FUN_00062214','FUN_0006224c(1)','direct_call_target_00063244')));check('bank1 activation keeps active/state 0x11 lifecycle',all(t in by[0x63350]['decompiled_c'] for t in ('cRamfebe4f87','uRamfebe4f88 = 0x11','FUN_00062282','direct_call_target_000632fa')));check('counter-number transfer is explicitly rejected','do not transfer Sienna counter numbers' in b['interpretation'])
    dr=a['driver_record_lookup'];check('generate driver lookup is two records stride 0x20',dr['generate']['h']=='0x00082702' and dr['generate']['record_count']==2 and dr['generate']['record_stride']==0x20 and '0x27c88' in by[0x82702]['decompiled_c']);check('generic driver lookup is two records stride 0x20',dr['verify_generic']['h']=='0x00082908' and dr['verify_generic']['record_count']==2 and dr['verify_generic']['record_stride']==0x20 and '0x27ccc' in by[0x82908]['decompiled_c']);check('driver lookup pair remains -0x5C00',dr['delta']==-0x5c00)
    sc=a['static_conclusion'];check('all seven crypto residual roles closed',sc['all_7_crypto_residual_roles_recovered'] and sc['crypto_named_residue_closed']);


def _section_diagnostic_residue():
    print('== diagnostic residue ==')
    """Verify closure of the remaining Corolla-H named diagnostic residue."""
    import json
    ROOT=REPO_ROOT;ART=ROOT/'data/generated/corolla_8965H1202000_diagnostic_residue.json';EV=ROOT/'data/generated/corolla_8965H1202000_diagnostic_residue_decompiler_evidence.json';RAW=ROOT/'community/albinoelephant/raw-20260818/albinoelephant-corolla-2023.20260814-0023/dump_codeflash_00000000_00200000_20260814-025814.bin'
    d=json.loads(ART.read_text());e=json.loads(EV.read_text());raw=RAW.read_bytes()[:0x100000];by={int(r['entry'],16):r for r in e['functions']}
    check('H image hash pinned',sha(raw)==e['image']['codeflash_sha256'])
    check('all raw H bodies validate',all(sha(raw[int(r['entry'],16):int(r['entry'],16)+r['body_size']])==r['body_sha256'] for r in e['functions']))
    check('27 diagnostic roles recovered',d['diagnostic_role_closure_count']==27)
    check('32 canonical rows closed by complete recensus',d['diagnostic_surface_recensus_count']==32)
    check('all 59 residual names accounted once',d['diagnostic_role_closure_count']+d['diagnostic_surface_recensus_count']==59)
    w=d['wdbi'];check('S WDBI has 13 entries',w['sienna_table']['count']==13);check('H WDBI has 12 entries',w['h_table']['count']==12)
    check('H removes only DID 200D',w['removed_dids']==['0x200D'] and not w['added_dids'])
    check('H WDBI table base is 25530',w['h_table']['base']=='0x00025530' and w['start_lookup']['h_table_base']=='0x00025530')
    check('H lookup bound is 12 in both phases',w['start_lookup']['h_count']==12==w['result_lookup']['h_count'])
    check('2013 and 2014 are disabled on H',w['disabled_on_h']==['0x2013','0x2014'])
    for did,start,result in [('0x2013',0x4A8B8,0x4A8BC),('0x2014',0x4A8C0,0x4A8C4)]:
     check(f'{did} start returns 5', 'return 5;' in by[start]['decompiled_c'])
     check(f'{did} result is no-op success', 'return 0;' in by[result]['decompiled_c'] and by[result]['body_size']==4)
    check('2012 remains unconditional-start',w['h_2012_unconditional_start'] and by[0x4A89A]['body_size']==4)
    check('2012 result still reaches target lifecycle helper','thunk_FUN_000b2b6e' in by[0x4A89E]['decompiled_c'])
    check('0204 maintains pending 2E10 behavior','0x2e10' in by[0x4A686]['decompiled_c'])
    check('WDBI request start maps to exact-size H 8EB7C',by[0x8EB7C]['body_size']==136)
    check('WDBI callback maps to exact-size H 8EC88',by[0x8EC88]['body_size']==36)
    check('session policy preserves session-2 speed gate',d['session']['policy']['requested_session_2_speed_gate'])
    check('session request family maps all four lifecycle roles',len(d['session']['request_family'])==4)
    check('RoutineControl generic helpers map all four roles',len(d['routine_control']['helpers'])==4)
    check('request-start retains H RID count source',d['routine_control']['h_rid_count_source']=='DAT_00026376')
    check('all 59 diagnostic residuals closed',d['static_conclusion']['all_59_diagnostic_residuals_closed'])


def _section_final_named_residue():
    print('== final named residue ==')
    import json
    ROOT=REPO_ROOT
    ART=ROOT/'data/generated/corolla_8965H1202000_final_named_residue.json'
    EVID=ROOT/'data/generated/corolla_8965H1202000_final_named_residue_evidence.json'
    SRAW=ROOT/'firmware/RH850_P1M-E_CodeFlash.bin'
    HRAW=ROOT/'community/albinoelephant/raw-20260818/albinoelephant-corolla-2023.20260814-0023/dump_codeflash_00000000_00200000_20260814-025814.bin'
    d=json.loads(ART.read_text());e=json.loads(EVID.read_text());s=SRAW.read_bytes();h=HRAW.read_bytes()[:0x100000]
    check('image hashes pinned',d['images']['sienna_sha256']==sha(s) and d['images']['h_sha256']==sha(h) and e['images']==d['images'])
    check('compact evidence raw-bound',all(sha((s if k=='sienna_fingerprints' else h)[int(r['entry'],16):int(r['entry'],16)+r['body_size']])==r['body_sha256'] for k in ('sienna_fingerprints','h_fingerprints') for r in e[k]))
    check('33 roles + one recensus close final 34',d['role_closure_count']==33 and d['surface_recensus_count']==1 and d['static_conclusion']['all_34_prior_unresolved_names_closed'])
    check('boot dispatcher transferred at -0x1C',d['claims']['boot_eiint']['dispatcher_target']=='0x0000072C' and d['claims']['boot_eiint']['dispatcher_shift']==-0x1c and s[0x730:0x770]==h[0x714:0x754])
    check('H boot EIINT table shrinks to 10BC/10C0/10C1/default',[x[0] for x in d['claims']['boot_eiint']['h_rows']]==['0x000010BC','0x000010C0','0x000010C1','0xFFFFFFFF'])
    check('boot TAUJ0 CH2 is removed, not remapped',d['surface_recensus']==[{'reason':'H complete boot EIINT table removes code 0x1087; H 0x1E5E belongs to code 0x10BC and must not be misidentified as TAUJ0 CH2','reference_entry':'0x00001E44','reference_name':'boot_tauj0_ch2_isr'}])
    check('boot exception handlers exact at -0x1C',s[0x1e1e:0x1e26]==h[0x1e02:0x1e0a] and s[0x1e2a:0x1e36]==h[0x1e0e:0x1e1a])
    roles={x['reference_name']:x['target_entry'] for x in d['role_closure']}
    check('CRC trio exact',roles['memory_crc_verify_result']=='0x000047C2' and roles['memory_crc_verify_busy']=='0x000047C8' and roles['crc32_hardware_compute']=='0x000047CE')
    check('application entry remains 20880',roles['application_entry']=='0x00020880')
    check('RAM policy maps to 4A4D4',roles['application_ram_range_allowed']=='0x0004A4D4' and d['claims']['ram_policy']['h_table']=='0x00028F0C')
    check('event-query cone exact',{n:roles[n] for n in ['application_event_record_query','application_event_active_id_list','application_event_state_query','application_event_detail_query']}=={'application_event_record_query':'0x0004AF74','application_event_active_id_list':'0x0004FE70','application_event_state_query':'0x0004FFD8','application_event_detail_query':'0x0005031A'})
    check('RMBA start/poll exact',roles['application_read_memory_by_address_request_start']=='0x0008F7C0' and roles['application_read_memory_by_address_request_poll']=='0x0008F720')
    check('proprietary AB workers exact',roles['application_proprietary_ab_selector_worker']=='0x0009193E' and roles['application_proprietary_ab_event_worker']=='0x00087384')
    check('RTE copy trio exact',[roles[x] for x in ['rte_input_staging_copy_c','rte_input_staging_copy_b','rte_input_staging_copy_a']]==['0x00056BAC','0x0005722E','0x0005778E'])
    check('application exception vectors exact',roles['application_default_exception_handler']=='0x0005C0F2' and roles['application_vector_0x90_handler']=='0x0005EE7E')
    check('changed generated successors pinned',roles['application_timer_peripheral_reload']=='0x0005F812' and roles['tauj0_ch0_sample_snapshot']=='0x0005FB30' and roles['fd0d7_status_fault_monitor']=='0x000B5EA4' and roles['application_input_snapshot_update']=='0x000BBA48')
    check('system/scheduler successors pinned',roles['application_rx_signal_consumer_56fc2']=='0x0005262C' and roles['application_ram_default_init']=='0x0005316C' and roles['application_substate_machine']=='0x000CF27E')
    check('shutdown/programming/timer targets pinned',roles['boot_shutdown_reset_path']=='0x0006A93E' and roles['application_programming_lower_request_stub']=='0x0008441C' and roles['application_programming_reset_marker_clear']=='0x000482AE' and roles['timer_expiry_07_callback']=='0x0008FBAC' and roles['system_programming_shutdown_mode_entry']=='0x000B1F68')


def _section_static_coverage():
    print('== static coverage ==')
    """Verify the evidence-graded named-function coverage denominator."""
    import json
    REPO=REPO_ROOT
    ART=REPO/'data/generated/corolla_8965H1202000_static_coverage_matrix.json'
    d=json.loads(ART.read_text());s=d['summary'];rows=d['functions']
    print('\n== denominator ==')
    check('coverage counts sum to denominator',sum(s['coverage_counts'].values())==1113)
    check('all 288 exact named transfers remain verified exact',s['coverage_counts']['verified-exact-body-transfer']==288)
    check('some changed/structural entries are promoted only by later evidence',s['coverage_counts'].get('target-native-inspected-unique-shape',0)>0 and s['coverage_counts'].get('target-native-role-recovered',0)>0 and s['coverage_counts'].get('target-surface-recensused',0)>0)
    check('canonical named denominator has zero genuinely unresolved rows',s['genuinely_unresolved_count']==0)
    check('all former structural-only candidates now have target-native inspection evidence',s['structural_candidate_only_count']==0)
    print('\n== promotion evidence discipline ==')
    check('target-native-inspected rows always name evidence files',all(r['target_native_evidence_files'] for r in rows if r['coverage']=='target-native-inspected-unique-shape'))
    check('target-native role-recovered rows always carry explicit role records and evidence',all(r['role_recovery'] and r['target_native_evidence_files'] for r in rows if r['coverage']=='target-native-role-recovered'))
    check('all eight scheduler-system changed roles remain target-native recovered',s['tag_coverage_counts']['scheduler_system'].get('target-native-role-recovered')==8 and s['tag_coverage_counts']['scheduler_system'].get('genuinely-unresolved',0)==0)
    check('all nine CAN/COM changed roles are target-native recovered',s['tag_coverage_counts']['can_com'].get('target-native-role-recovered')==9 and s['tag_coverage_counts']['can_com'].get('genuinely-unresolved',0)==0)
    check('all three storage/NvM changed roles are target-native recovered',s['tag_coverage_counts']['storage_nvm'].get('target-native-role-recovered')==3 and s['tag_coverage_counts']['storage_nvm'].get('genuinely-unresolved',0)==0)
    check('all four XCP changed roles are target-native recovered',s['tag_coverage_counts']['xcp'].get('target-native-role-recovered')==4 and s['tag_coverage_counts']['xcp'].get('genuinely-unresolved',0)==0)
    check('all five newly mapped motor-control roles are target-native recovered',all(any(r['reference_name']==name and r['coverage']=='target-native-role-recovered' for r in rows) for name in ('motor_coord_transform_calib_handler','dq_current_pi_axis_b','motor0_inverse_rotating_frame_transform','motor1_inverse_rotating_frame_transform','tauj0_ch0_motor_control_worker')) and s['tag_coverage_counts']['motor_control'].get('genuinely-unresolved',0)==0)
    check('axis-A motor PI structural candidate is promoted by target-native evidence',any(r['reference_name']=='dq_current_pi_axis_a' and r['coverage']=='target-native-inspected-unique-shape' for r in rows))
    check('all 42 remaining SecOC/ICU-S roles are target-native recovered',s['tag_coverage_counts']['secoc_icus'].get('genuinely-unresolved',0)==0 and s['tag_coverage_counts']['secoc_icus'].get('target-native-role-recovered')==44)
    check('all seven remaining crypto roles are target-native recovered',s['tag_coverage_counts']['crypto'].get('genuinely-unresolved',0)==0 and s['tag_coverage_counts']['crypto'].get('target-native-role-recovered')==14)
    check('remaining steering residue is fully closed without fake latch homologs',s['tag_coverage_counts']['steering'].get('genuinely-unresolved',0)==0 and s['tag_coverage_counts']['steering'].get('target-native-role-recovered')==6 and s['tag_coverage_counts']['steering'].get('target-surface-recensused')==6)
    check('remaining diagnostics residue is fully closed',s['tag_coverage_counts']['diagnostics'].get('genuinely-unresolved',0)==0 and s['tag_coverage_counts']['diagnostics'].get('target-native-role-recovered')==27)
    check('all 11 plausibility-monitor roles are target-native recovered',sum(1 for r in rows if r['reference_name'].startswith('plausibility_monitor_') and r['coverage']=='target-native-role-recovered')==11)
    check('all 18 packet/record/bounded adapter roles are target-native recovered',sum(1 for r in rows if (r['reference_name'].startswith('packet_low_selector_') or r['reference_name'].startswith('record_operation_') or r['reference_name'].startswith('bounded_api_wrapper_')) and r['coverage']=='target-native-role-recovered')==18)
    check('all 12 preserved veneer-derived roles are target-native recovered',sum(1 for r in rows if r.get('role_recovery') and r['role_recovery'].get('report')=='data/generated/corolla_8965H1202000_veneer_bank.json')==12)
    check('all 10 deleted veneer-derived roles are surface-recensused',sum(1 for r in rows if 'high-page-veneer-bank-complete-recensus' in r.get('surface_recensus',[]))==10)
    check('all 33 configured application callback roles are target-native recovered',sum(1 for r in rows if r.get('role_recovery') and r['role_recovery'].get('report')=='data/generated/corolla_8965H1202000_application_callback_tables.json')==33)
    check('all four removed async-operation callback roles are surface-recensused',sum(1 for r in rows if 'application-async-operation-complete-table-recensus' in r.get('surface_recensus',[]))==4)
    check('all 33 final named-residue successors are target-native recovered',sum(1 for r in rows if r.get('role_recovery') and r['role_recovery'].get('report')=='data/generated/corolla_8965H1202000_final_named_residue.json')==33)
    check('all three keyless event-formatter roles are target-native recovered',sum(1 for r in rows if r.get('role_recovery') and r['role_recovery'].get('report')=='data/generated/corolla_8965H1202000_keyless_event_formatter.json')==3)
    check('removed boot TAUJ0 CH2 role is recensused, not falsely mapped',sum(1 for r in rows if 'boot-eiint-complete-table-recensus' in r.get('surface_recensus',[]))==1 and any(r['reference_name']=='boot_tauj0_ch2_isr' and r['coverage']=='target-surface-recensused' for r in rows))
    check('238 total roles are target-native recovered',s['coverage_counts'].get('target-native-role-recovered')==238)
    check('all 88 deadline callbacks are closed by complete target recensus',sum(1 for r in rows if r['reference_name'].startswith('deadline_') and r['coverage']=='target-surface-recensused')==88)
    check('global genuinely-unresolved denominator is zero',s['genuinely_unresolved_count']==0)
    check('all 96 former structural-only rows retain target-native structural-residue evidence',sum(1 for r in rows if r['coverage']=='target-native-inspected-unique-shape' and 'data/generated/corolla_8965H1202000_structural_residue_decompiler_evidence.json' in r.get('target_native_evidence_files', []))==96)
    check('final evidence-class distribution is pinned',s['coverage_counts']=={'verified-exact-body-transfer':288,'target-native-role-recovered':238,'target-surface-recensused':461,'target-native-inspected-unique-shape':126})
    check('surface-recensused rows always name an explicit complete recensus',all(r['surface_recensus'] for r in rows if r['coverage']=='target-surface-recensused'))
    check('no structural-only rows remain',not any(r['coverage']=='structural-candidate-only' for r in rows))
    check('genuinely unresolved rows have neither target-native evidence nor surface recensus',all(not r['target_native_evidence_files'] and not r['surface_recensus'] for r in rows if r['coverage']=='genuinely-unresolved'))
    check('H-native inspected additions without unique S pair are counted separately',s['h_native_evidence_functions_without_unique_sienna_pair']>0)


def _section_structural_residue_inspection():
    print('== structural residue inspection ==')
    import json
    ROOT=REPO_ROOT
    ART=ROOT/'data/generated/corolla_8965H1202000_structural_residue_decompiler_evidence.json'
    STRUCT=ROOT/'data/generated/corolla_8965H1202000_structural_function_transfer.json'
    HRAW=ROOT/'community/albinoelephant/raw-20260818/albinoelephant-corolla-2023.20260814-0023/dump_codeflash_00000000_00200000_20260814-025814.bin'
    d=json.loads(ART.read_text());st=json.loads(STRUCT.read_text());h=HRAW.read_bytes()[:0x100000]
    check('software/image identity pinned',d['software_id']=='8965H1202000' and d['image']['codeflash_sha256']==sha(h))
    check('reference and target entries are each unique',len({x['reference_entry'] for x in d['functions']})==96 and len({x['entry'] for x in d['functions']})==96)
    check('all H bodies raw-bound',all(sha(h[int(x['entry'],16):int(x['entry'],16)+x['body_size']])==x['body_sha256'] for x in d['functions']))
    sm={int(x['reference_entry'],16):x for x in st['matches']}
    check('every inspected pair is the structural artifact target',all(int(x['reference_entry'],16) in sm and int(x['entry'],16)==int(sm[int(x['reference_entry'],16)]['target_entry'],16) for x in d['functions']))
    check('every inspected pair is unique-exact-shape',all(sm[int(x['reference_entry'],16)]['classification']=='unique-exact-shape' for x in d['functions']))
    check('all structural body sizes agree with target evidence',all(int(sm[int(x['reference_entry'],16)]['body_size_target'])==x['body_size'] for x in d['functions']))


def _section_can_com():
    print('== can com ==')
    """Verify Corolla H changed CAN/COM role recovery and configured routing."""
    import json,struct
    ROOT=REPO_ROOT
    ART=ROOT/'data/generated/corolla_8965H1202000_can_com.json';EV=ROOT/'data/generated/corolla_8965H1202000_can_com_decompiler_evidence.json'
    HRAW=ROOT/'community/albinoelephant/raw-20260818/albinoelephant-corolla-2023.20260814-0023/dump_codeflash_00000000_00200000_20260814-025814.bin';SIMG=ROOT/'firmware/RH850_P1M-E_CodeFlash.bin'
    a=json.loads(ART.read_text());e=json.loads(EV.read_text());H=HRAW.read_bytes()[:0x100000];S=SIMG.read_bytes()
    print('== deterministic artifact ==')
    print('\n== compact evidence ==')
    check('H image hash pinned',sha(H)==e['image']['codeflash_sha256']==a['images']['h_sha256'])
    check('all raw H bodies validate',all(sha(H[int(x['entry'],16):int(x['entry'],16)+x['body_size']])==x['body_sha256'] for x in e['functions']))
    print('\n== nine role mappings ==')
    exp={'0x0005D3CE':'0x00058450','0x0005DB6E':'0x00058BBC','0x00069DEC':'0x0006418C','0x0007C640':'0x00076A3C','0x0007E30C':'0x00078708','0x0007E5F2':'0x000789EE','0x0007F002':'0x000793FE','0x00080992':'0x0007AD8E','0x00084710':'0x0007EB10'}
    check('all nine changed can_com roles recovered',a['can_com_role_closure_count']==9 and {x['reference_entry']:x['target_entry'] for x in a['can_com_role_closure']}==exp)
    g=a['rx_dispatch_groups'];check('group B guard schedule is identical 29/29',g['group_b']['sienna_guard_count']==g['group_b']['h_guard_count']==29 and g['group_b']['guard_diff']==[])
    check('group A is 97->96 with one nested guard deletion',g['group_a']['sienna_guard_count']==97 and g['group_a']['h_guard_count']==96 and len(g['group_a']['guard_diff'])==1 and g['group_a']['guard_diff'][0]['sienna']==['if (uVar != 0) {'] and g['group_a']['guard_diff'][0]['h']==[])
    d=a['deadline_monitor_c'];check('deadline monitor body is exact at active H 6418C',d['exact_body_equal'] and H[0x6418C:0x6462A]==S[0x69DEC:0x6A28A])
    check('deadline body ambiguity is explicit',d['h_exact_body_occurrences']==['0x0006418C','0x000CF27E'])
    check('active H monitor caller disambiguates 6418C',d['active_h_caller']=='0x0003E118' and d['active_h_caller_invokes_6418c'])
    print('\n== configured transport table proofs ==')
    for row in a['configuration_pointer_proofs']:
     sa=int(row['sienna_pointer_at'],16);ha=int(row['h_pointer_at'],16)
     check('table '+row['role'],struct.unpack_from('<I',S,sa)[0]==int(row['sienna_target'],16) and struct.unpack_from('<I',H,ha)[0]==int(row['h_target'],16))
    by={int(x['entry'],16):x for x in e['functions']}
    check('H COM RxIndication retains full 212-byte copy/filter/timeout body',by[0x76A3C]['body_size']==212 and all(t in by[0x76A3C]['decompiled_c'] for t in ('& 0x10','& 8','& 4','*pbVar1 = *pbVar1 & 0xdc','FUN_00087a82(param_1)')))
    check('H PduR COM transmit wrapper remains 26 bytes',by[0x7AD8E]['body_size']==26 and 'PTR_LAB_00021c70' in by[0x7AD8E]['decompiled_c'])
    check('H CanIf Tx-ID class decoder retains six classes',all(t in by[0x789EE]['decompiled_c'] for t in ('0x6000','0x800','0xb800','0xc000','0xf800')))
    check('H CanIf Tx confirmation retains six class dispatch',all(t in by[0x793FE]['decompiled_c'] for t in ('0x6000','0x800','0xb800','0xc000','0xf800')))
    check('H RSCFD confirmation is called by Tx interrupt body', 'FUN_0007eb10' in by[0x7EB4E]['decompiled_c'])
    check('H normal Rx demux terminates at PduR route adapter', 'FUN_0007b026' in by[0x7A402]['decompiled_c'] and struct.unpack_from('<I',H,0x21C90)[0]==0x7B040)


def _section_xcp():
    print('== xcp ==')
    """Verify target-native H XCP command residuals."""
    import json
    ROOT=REPO_ROOT;ART=ROOT/'data/generated/corolla_8965H1202000_xcp.json';EV=ROOT/'data/generated/corolla_8965H1202000_xcp_decompiler_evidence.json';HRAW=ROOT/'community/albinoelephant/raw-20260818/albinoelephant-corolla-2023.20260814-0023/dump_codeflash_00000000_00200000_20260814-025814.bin'
    a=json.loads(ART.read_text());e=json.loads(EV.read_text());H=HRAW.read_bytes()[:0x100000];by={int(x['entry'],16):x for x in e['functions']}
    check('H hash pinned',sha(H)==e['image']['codeflash_sha256']==a['images']['h_sha256']);check('all raw bodies validate',all(sha(H[int(x['entry'],16):int(x['entry'],16)+x['body_size']])==x['body_sha256'] for x in e['functions']))
    exp={'0x000972FA':'0x0009232A','0x00097432':'0x00092462','0x000975EE':'0x0009261E','0x00097668':'0x00092698'};check('four XCP residual roles recovered',a['xcp_role_closure_count']==4 and {x['reference_entry']:x['target_entry'] for x in a['xcp_role_closure']}==exp)
    check('custom selector sequence is unchanged',a['custom_command_table']['selectors']==[0xFB,0xFA,0xF5,0xF3,0xEB,0xEA,0xE4]);check('H command table points at all four recovered handlers',a['custom_command_table']['h_handlers'][1:6:1][0]=='0x0009232A' and a['custom_command_table']['h_handlers'][2]=='0x00092462' and a['custom_command_table']['h_handlers'][4]=='0x0009261E' and a['custom_command_table']['h_handlers'][5]=='0x00092698')
    fa=a['fa_indexed_identifier'];check('FA keeps index<5 behavior',fa['index_limit']==5 and '< 5' in by[0x9232A]['decompiled_c']);f5=a['f5_upload'];check('F5 accepts only lengths 1..7',f5['byte_count_min']==1 and f5['byte_count_max']==7 and all(t in by[0x92462]['decompiled_c'] for t in ('bVar3 == 0','7 < bVar3')));check('F5 range helper covers LocalRAM outer range','0xfebdffff < param_1' in by[0x9238A]['decompiled_c'] and '0xfec00000' in by[0x9238A]['decompiled_c']);check('F5 has five H-specific exclusion ranges',f5['exclusion_count']==5 and len(f5['h_exclusion_ranges'])==5);check('F5 retains special CodeFlash 0x10000..17DEF rule',f5['special_codeflash_copy_check']['length']==0x7DEC and '0x7dec' in by[0x9238A]['decompiled_c'] and 'DAT_00017df0' in by[0x9238A]['decompiled_c']);check('F5 copy helper advances MTA', 'FUN_0007c390' in by[0x92436]['decompiled_c'])
    ps=a['page_state'];check('EB writer and EA reader share H state cells',all(cell.lower().replace('0x','') in (by[0x9261E]['decompiled_c']+by[0x92698]['decompiled_c']).lower() for cell in ps['state_cells']));check('EB writer preserves flag mask and value<2 checks','bVar4 & 3' in by[0x9261E]['decompiled_c'] and 'bVar3 < 2' in by[0x9261E]['decompiled_c']);check('EA reader preserves selectors 1/2',"== '\\x01'" in by[0x92698]['decompiled_c'] and "== '\\x02'" in by[0x92698]['decompiled_c']);check('E4 remains in same custom command table',a['e4_support']['remains_in_same_custom_table'] and a['custom_command_table']['h_handlers'][-1]=='0x00092724');check('application-side F5 primitive explicitly preserved',a['static_conclusion']['application_side_f5_read_primitive_preserved']);check('external reachability remains bounded','external gateway reachability' in a['static_conclusion']['boundary'])


_section_crypto_residue()
_section_diagnostic_residue()
_section_final_named_residue()
_section_static_coverage()
_section_structural_residue_inspection()
_section_can_com()
_section_xcp()
print(f'\nResults: {passed} passed, {failed} failed')
raise SystemExit(1 if failed else 0)
