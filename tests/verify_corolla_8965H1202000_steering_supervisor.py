#!/usr/bin/env python3
"""Verify the 8965H1202000 steering-supervisor stage ledger."""
from __future__ import annotations
import json, subprocess, sys, tempfile
from pathlib import Path
REPO=Path(__file__).resolve().parents[1]
ART=REPO/'data/generated/corolla_8965H1202000_steering_supervisor_stage_ledger.json'
TOOL=REPO/'tools/build_corolla_h_steering_supervisor_stage_ledger.py'
passed=failed=0
def check(name,cond,detail=''):
 global passed,failed
 ok=bool(cond);passed+=int(ok);failed+=int(not ok);s=f' ({detail})' if detail else ''
 print(f"[{'PASS' if ok else 'FAIL'}][raw_bytes] {name}{s}")
with tempfile.TemporaryDirectory() as td:
 out=Path(td)/'ledger.json';subprocess.run([sys.executable,str(TOOL),'--out',str(out)],cwd=REPO,check=True,stdout=subprocess.DEVNULL)
 check('tracked stage ledger regenerates exactly',out.read_bytes()==ART.read_bytes())
d=json.loads(ART.read_text());r=d['roots'];s=d['summary']
print('\n== stage denominator ==')
check('Sienna root is CB86E / 424 bytes',r['sienna']=='0xCB86E' and r['sienna_body_size']==424)
check('H root is CEDAE / 534 bytes',r['corolla_h']=='0xCEDAE' and r['corolla_h_body_size']==534)
check('direct stage counts are 94 -> 123',(r['sienna_direct_stage_count'],r['corolla_h_direct_stage_count'])==(94,123))
check('83 stages are order-paired',s['paired']==83)
check('33 pairs are unique exact instruction-shape transfers',s['paired_unique_exact_shape']==33)
check('40 H stages are order-unpaired',s['h_order_unpaired']==40)
check('11 Sienna stages are order-unpaired',s['sienna_order_unpaired']==11)
check('every H-unpaired stage has a bounded role class',len(d['h_order_unpaired'])==40 and all(x['role_class'] and x['bounded_description'] for x in d['h_order_unpaired']))
print('\n== command-specific transfer boundary ==')
def pair(sa,ha):
 return next((x for x in d['stages'] if x.get('sienna_entry')==sa and x.get('h_entry')==ha),None)
check('S clamp/gain -> H C91B6 is exact-shape',pair('0xC853A','0xC91B6')['pair_evidence']=='unique-exact-instruction-shape')
check('S rate-limit -> H C9232 is exact-shape',pair('0xC85B6','0xC9232')['pair_evidence']=='unique-exact-instruction-shape')
removed={x['sienna_entry']:x for x in d['sienna_order_unpaired']}
check('authenticated 131 smoothing C8DE0 is order-unpaired',removed['0xC8DE0']['role_class']=='sienna_lta_angle_command')
check('replacement command remains deliberately unassigned','no direct replacement is assigned' in d['explicit_command_mode_boundary']['replacement_command'])
print('\n== H expansion classification ==')
roles=s['h_unpaired_role_counts']
check('H expansion includes B6 mode/validity/status stages',roles['b6_mode_table']==roles['b6_validity_gate']==roles['b6_status_export']==1)
check('H expansion has eight dual-channel plausibility stages',roles['h_dual_channel_plausibility']==8)
check('H expansion has three motion-state estimator stages',roles['h_motion_state_estimator']==3)
check('H expansion has two geometry-estimator stages',roles['h_geometry_estimation']==2)
check('H expansion has three supervisor fault monitors',roles['supervisor_fault_monitor']==3)
check('all 40 H-unpaired roles are counted',sum(roles.values())==40)
print(f'\nResults: {passed} passed, {failed} failed')
raise SystemExit(1 if failed else 0)
