#!/usr/bin/env python3
"""Verify exact H/F 0x394 DEM class/state/DTC closure."""
from __future__ import annotations
import json, subprocess, sys, tempfile
from pathlib import Path
REPO=Path(__file__).resolve().parents[1]
ART=REPO/'data/generated/corolla_hf_fault_state_contract.json'
TOOL=REPO/'tools/build_corolla_hf_fault_state_contract.py'
passed=failed=0
def check(name,cond):
 global passed,failed
 ok=bool(cond);passed+=int(ok);failed+=int(not ok);print(f"[{'PASS' if ok else 'FAIL'}][generated_self_check] {name}")
with tempfile.TemporaryDirectory() as td:
 out=Path(td)/'fault.json'; p=subprocess.run([sys.executable,str(TOOL),'--out',str(out)],cwd=REPO)
 check('builder exits cleanly',p.returncode==0)
 check('tracked artifact regenerates exactly',out.exists() and out.read_bytes()==ART.read_bytes())
d=json.loads(ART.read_text())
check('schema/software family exact',d['schema']=='corolla-hf-0x394-fault-state-contract-v1' and d['software_ids']==['8965H1202000','8965F1208000'])
check('0x394 geometry exact',d['wire']['can_id']=='0x394' and d['wire']['length']==3 and len(d['wire']['state_table_rows'])==17)
check('complete DEM class census exact',d['dem']['class_counts']=={'0x01':8,'0x02':34,'0x04':1,'0x08':1,'0x0F':1,'0x10':173,'0x20':16,'0x40':1,'0x80':7} and sum(d['dem']['class_counts'].values())==242)
ct=d['dem']['class_to_state']
check('class2/4 paired-state mapping exact',ct['0x02']['states']==[6,7] and ct['0x04']['states']==[8,9])
check('direct class branches exact',ct['0x10']['states']==[10] and ct['0x20']['states']==[11] and ct['0x40']['states']==[12] and ct['0x08']['states']==[13] and ct['0x0F']['states']==[14])
check('class80 is bounded general fallback',ct['0x80']['states']==[16] and 'not unique' in ct['0x80']['selection'])
check('classF0 supported but absent in event table','no exact-H event-table row' in ct['0xF0']['selection'] and '0xF0' not in d['dem']['class_counts'])
check('class01 populated but not accumulator-consumed',ct['0x01']['states']==[] and 'not consumed' in ct['0x01']['selection'])
a=d['aging']
check('paired-state aging constants exact',a['class2_primary_age']==200 and a['class4_primary_age']==200 and a['class2_class4_secondary_age']==600 and a['primary_clear_enable_age']==17736)
n=d['named_dtc_families']
check('named DTC family cardinalities exact',len(n['class_0x01_no_direct_394_accumulator_effect'])==6 and len(n['class_0x02_states_6_7'])==11 and len(n['class_0x10_state_10'])==50 and len(n['class_0x20_state_11'])==6)
check('class10 includes Brake missing-message DTC',any(x['code']=='U012987' and x['failure']=='Missing Message' for x in n['class_0x10_state_10']))
check('class20 includes steering-angle comm incompatibility family',any(x['code']=='U012687' for x in n['class_0x20_state_11']) and any(x['code']=='U032857' for x in n['class_0x20_state_11']))
check('openpilot temporary/permanent remains bounded',d['openpilot_boundary']['steerFaultTemporary']=='unresolved policy mapping' and d['openpilot_boundary']['steerFaultPermanent']=='unresolved policy mapping')
doc=(REPO/'docs/variants/corolla-h-f-openpilot-state-bridge.md').read_text(); findings=(REPO/'docs/status/FINDINGS.md').read_text()
check('canonical doc records 242-event class closure','### 6.7' in doc and '242' in doc and '200' in doc and '600' in doc)
check('TMS-058 integrated','| TMS-058 |' in findings and 'corolla_hf_fault_state_contract.json' in findings)
print(f'\nResults: {passed} passed, {failed} failed')
raise SystemExit(1 if failed else 0)
