#!/usr/bin/env python3
"""Verify exact H/F remaining 0x030/0x351 status closure."""
from __future__ import annotations
import hashlib, json, subprocess, sys, tempfile
from pathlib import Path
REPO=Path(__file__).resolve().parents[1]
ART=REPO/'data/generated/corolla_hf_remaining_status_contract.json'
EVID=REPO/'data/generated/corolla_8965H1202000_remaining_status_decompiler_evidence.json'
TOOL=REPO/'tools/build_corolla_hf_remaining_status_contract.py'
IMAGE=REPO/'community/albinoelephant/normalized/8965H1202000_CodeFlash.bin'
passed=failed=0
def check(name,cond):
 global passed,failed
 ok=bool(cond);passed+=int(ok);failed+=int(not ok);print(f"[{'PASS' if ok else 'FAIL'}][raw_bytes] {name}")
with tempfile.TemporaryDirectory() as td:
 out=Path(td)/'status.json'; p=subprocess.run([sys.executable,str(TOOL),'--out',str(out)],cwd=REPO)
 check('builder exits cleanly',p.returncode==0); check('status artifact regenerates exactly',out.exists() and out.read_bytes()==ART.read_bytes())
d=json.loads(ART.read_text()); e=json.loads(EVID.read_text()); image=IMAGE.read_bytes()
check('schema/software family exact',d['schema']=='corolla-hf-remaining-status-contract-v1' and d['software_ids']==['8965H1202000','8965F1208000'])
check('18 exact-H functions promoted',e['function_count']==18)
check('all promoted bodies match exact H bytes',all(hashlib.sha256(image[int(x['entry'],16):int(x['entry'],16)+x['body_size']]).hexdigest()==x['body_sha256'] for x in e['functions']))
b=d['can_0x030_b6_bit1']
check('B6[1] source is Q-axis actual current',b['wire']=='0x030 B6[1]' and b['chain'][0]=='FEBE6BAE Motor Actual Current (Q Axis)')
check('B6[1] full threshold/debounce chain retained',all(x in ' '.join(b['chain']) for x in ('FEBEEC0C','FEBEAFC4','FEBEB64D','FEBEB64C','FEBEE848','FEBE7DB3')))
check('exact-H detector calibration exact',b['calibration']['feature_flag']==0x5A and b['calibration']['threshold_a']==5120 and b['calibration']['threshold_b']==2560 and b['calibration']['debounce_count']==0)
check('exact-H detector is calibration-disabled','disabled' in b['classification'] and 'unreachable' in b['exact_h_calibration_effect'])
check('Span is kept cross-specimen only',b['span_observation']['values']==[0,1] and 'not exact-F181-joined' in b['span_observation']['boundary'])
f=d['can_0x351_force7']
check('force7 condition exact',f['condition']=='(FEBE65E4 & 0x0003) != 0 AND FEBE7E13 != 0')
check('force7 status-bitmap bits exact',f['status_bitmap_side']['bits_used']==[0,1] and 'FEBE6FB4' in ' '.join(f['status_bitmap_side']['chain']))
check('force7 24-record aggregate bit exact',f['record_aggregate_side']['record_count']==24 and f['record_aggregate_side']['bit_used']==15)
check('force7 remains semantically bounded','does not assign Toyota names' in f['status_bitmap_side']['boundary'] and 'not recovered' in f['record_aggregate_side']['boundary'])
check('force7 separated from C159B49','distinct from the C159B49' in f['classification'])
doc=(REPO/'docs/variants/corolla-h-f-openpilot-state-bridge.md').read_text(); findings=(REPO/'docs/status/FINDINGS.md').read_text()
check('canonical doc records B6[1]/force7 closures','### 6.8' in doc and 'Q-axis-current-derived' in doc and '24' in doc and 'bit **15**' in doc)
check('TMS-059 integrated','| TMS-059 |' in findings and 'corolla_hf_remaining_status_contract.json' in findings)
print(f'\nResults: {passed} passed, {failed} failed')
raise SystemExit(1 if failed else 0)
