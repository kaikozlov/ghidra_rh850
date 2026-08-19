#!/usr/bin/env python3
"""Verify the evidence-graded named-function coverage denominator."""
from __future__ import annotations
import json, subprocess, sys, tempfile
from pathlib import Path
REPO=Path(__file__).resolve().parents[1]
ART=REPO/'data/generated/corolla_8965H1202000_static_coverage_matrix.json'
TOOL=REPO/'tools/build_corolla_h_static_coverage_matrix.py'
passed=failed=0
def check(name,cond,detail=''):
 global passed,failed
 ok=bool(cond);passed+=int(ok);failed+=int(not ok);s=f' ({detail})' if detail else ''
 print(f"[{'PASS' if ok else 'FAIL'}][raw_bytes] {name}{s}")
with tempfile.TemporaryDirectory() as td:
 out=Path(td)/'coverage.json';subprocess.run([sys.executable,str(TOOL),'--out',str(out)],cwd=REPO,check=True,stdout=subprocess.DEVNULL)
 check('tracked coverage matrix regenerates exactly',out.read_bytes()==ART.read_bytes())
d=json.loads(ART.read_text());s=d['summary'];rows=d['functions']
print('\n== denominator ==')
check('matrix covers all 1113 named canonical functions',s['named_function_count']==1113==len(rows))
check('coverage counts sum to denominator',sum(s['coverage_counts'].values())==1113)
check('all 288 exact named transfers remain verified exact',s['coverage_counts']['verified-exact-body-transfer']==288)
check('some changed/structural entries are promoted only by later evidence',s['coverage_counts'].get('target-native-inspected-unique-shape',0)>0 and s['coverage_counts'].get('target-native-role-recovered',0)>0 and s['coverage_counts'].get('target-surface-recensused',0)>0)
check('matrix retains a genuine unresolved residue',0<s['genuinely_unresolved_count']<689)
check('matrix retains structural-only candidates rather than auto-promoting them',s['structural_candidate_only_count']>0)
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
check('111 total roles are target-native recovered',s['coverage_counts'].get('target-native-role-recovered')==111)
check('all 88 deadline callbacks are closed by complete target recensus',sum(1 for r in rows if r['reference_name'].startswith('deadline_') and r['coverage']=='target-surface-recensused')==88)
check('global unresolved denominator is now 228',s['genuinely_unresolved_count']==228)
check('surface-recensused rows always name an explicit complete recensus',all(r['surface_recensus'] for r in rows if r['coverage']=='target-surface-recensused'))
check('structural-only rows have no target-native evidence',all(not r['target_native_evidence_files'] for r in rows if r['coverage']=='structural-candidate-only'))
check('genuinely unresolved rows have neither target-native evidence nor surface recensus',all(not r['target_native_evidence_files'] and not r['surface_recensus'] for r in rows if r['coverage']=='genuinely-unresolved'))
check('H-native inspected additions without unique S pair are counted separately',s['h_native_evidence_functions_without_unique_sienna_pair']>0)
print(f'\nResults: {passed} passed, {failed} failed')
raise SystemExit(1 if failed else 0)
