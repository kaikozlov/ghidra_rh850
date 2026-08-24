#!/usr/bin/env python3
"""Verify the H/F Corolla openpilot state-interface bridge."""
from __future__ import annotations

import hashlib,json,subprocess,sys,tempfile
from pathlib import Path

REPO=Path(__file__).resolve().parents[1]
ART=REPO/'data/generated/corolla_8965H1202000_openpilot_state_bridge.json'
EVID=REPO/'data/generated/corolla_8965H1202000_openpilot_state_bridge_decompiler_evidence.json'
BUILD=REPO/'tools/build_corolla_h_openpilot_state_bridge.py'
IMAGE=REPO/'community/albinoelephant/normalized/8965H1202000_CodeFlash.bin'
DOC=REPO/'docs/variants/corolla-h-f-openpilot-state-bridge.md'
passed=failed=0

def sha(b:bytes)->str:return hashlib.sha256(b).hexdigest()
def check(name:str,cond:object,detail:str='')->None:
 global passed,failed
 ok=bool(cond); passed+=int(ok);failed+=int(not ok)
 print(f"[{'PASS' if ok else 'FAIL'}][raw_bytes] {name}"+(f' ({detail})' if detail else ''))

art=json.loads(ART.read_text()); evid=json.loads(EVID.read_text()); image=IMAGE.read_bytes()
print('== deterministic artifacts ==')
with tempfile.TemporaryDirectory() as td:
 out=Path(td)/'bridge.json'
 r=subprocess.run([sys.executable,str(BUILD),'--out',str(out)],cwd=REPO,capture_output=True,text=True)
 check('bridge builder succeeds',r.returncode==0,r.stderr[-300:])
 check('bridge artifact regenerates exactly',r.returncode==0 and out.read_bytes()==ART.read_bytes())
check('bridge schema v3',art['schema']=='corolla-8965H1202000-openpilot-state-bridge-v3')
check('compact evidence schema v1',evid['schema']=='corolla-h-openpilot-state-bridge-decompiler-evidence-v1')
check('exact H image identity',len(image)==0x100000 and sha(image)==art['images']['corolla_h']['sha256']==evid['image']['sha256'])
check('H/F application identity carried forward',art['images']['corolla_f']['application_byte_identical_to_h'])
check('promoted corpus identity exact',evid['source_corpus']['sha256']=='c3411eec57b9d55c004b0b0f328394bb152577c3398084dccc729dab5da54656' and evid['source_corpus']['function_count']==5478)
check('nine compact functions promoted',evid['function_count']==9)
for row in evid['functions']:
 a=int(row['entry'],16); n=row['body_size']; check(f"raw body {row['entry']}",sha(image[a:a+n])==row['body_sha256'])

print('\n== exact H Tx carriers ==')
pdus={x['can_id']:x for x in art['h_tx_pdu_descriptors']}
check('new H Tx family exact',list(pdus)==['0x030','0x351','0x394','0x4A3','0x4C8'])
check('0x030 is 32-byte PDU0',pdus['0x030']['pdu']==0 and pdus['0x030']['length']==32)
check('0x351 is 4-byte PDU1',pdus['0x351']['pdu']==1 and pdus['0x351']['length']==4)
check('0x394 is 3-byte PDU2',pdus['0x394']['pdu']==2 and pdus['0x394']['length']==3)
check('0x4A3 is 8-byte PDU3',pdus['0x4A3']['pdu']==3 and pdus['0x4A3']['length']==8)

print('\n== 0x4A3 state bridge ==')
b=art['state_bridge']['0x4A3']; fields={x['wire']:x for x in b['fields']}
check('0x4A3 high-confidence classification','high-confidence' in b['classification'])
check('B1:B2 mirrors FD025 angle','0x025 signal184' in fields['B1:B2']['source'])
check('B3:B4 exact Techstream Steering Angle join','0x1037 Steering Angle' in fields['B3:B4']['semantic'] and fields['B3:B4']['source']=='FEBE7A46')
check('B5 exact Steering Wheel Torque source join','0x1035 Steering Wheel Torque' in fields['B5']['semantic'] and 'FEBE6554' in fields['B5']['source'])
check('B5 physical scaling remains bounded','exact physical B5 scaling not yet promoted' in fields['B5']['semantic'])
check('B6:B7 is target-native Q-current response','0x1151 Motor Actual Current (Q Axis)' in fields['B6:B7']['semantic'] and 'not assumed old STEER_TORQUE_EPS' in fields['B6:B7']['semantic'])

print('\n== 0x351 / 0x394 status families ==')
s351=art['state_bridge']['0x351']; s394=art['state_bridge']['0x394']
check('351 exact status/flag wire location',s351['wire']=='B2[7:5] = FEBE7DD0; B2[4] = FEBE7DD1')
check('351 preserves seven-count architecture','seven-count' in s351['producer'])
check('351 semantic transfer is bounded','not given an old OEM semantic name' in s351['boundary'])
check('394 exact four packed status fields',s394['wire']=='B1[7:6]=7DD5; B1[5:3]=7DD6; B2[3:1]=7DD7; B2[0]=7DD9')
check('394 internal state source is explicit','FEBE7F58' in s394['producer'])
check('old LKA_STATE codes explicitly non-portable','old 0x262 LKA_STATE numeric values are unresolved/non-portable' in s394['boundary'])

print('\n== 0x030 reframed ==')
s030=art['state_bridge']['0x030']
check('030 stays mixed rather than monolithic','mixed 32-byte FD' in s030['classification'])
check('030 configured signal set 0..36',s030['configured_signals']==list(range(37)))
check('030 direct packed signals 0..34',s030['direct_packed_signals']==list(range(35)))
check('030 additive byte7 exact formula',s030['additive_field']['wire_byte']==7 and 'sum(payload_bytes_0_through_6) + 0x38' in s030['additive_field']['formula'])

print('\n== command ingress closure ==')
c=art['command_ingress_closure']
check('complete scalar generated-COM census is 101',c['generated_scalar_rx_calls']==101)
check('twenty-two external signals enter supervisor cone',c['supervisor_external_signals']==22)
check('large ingress includes B6 target plus 025 sensors',c['supervisor_reaching_ge12bit_fields']==[{'can_id':'0x025','signal_id':184,'bits':12},{'can_id':'0x025','signal_id':186,'bits':12},{'can_id':'0x0B6','signal_id':255,'bits':16}])
check('fixed-map correction recovered B6 target',c['fixed_map_correction_recovered_b6_target'] is True)
check('D7 16-bit field is SP1 vehicle speed','CAN Vehicle Speed (SP1)' in c['protected_0x0D7'])
check('Techstream B6 semantics defer to target-native proof','defers signal255 control semantics' in c['protected_0x0B6_techstream_boundary'])
check('B6 target-angle command exact',c['b6_target_angle']['signal_id']==255 and c['b6_target_angle']['wire_byte']==4 and c['b6_target_angle']['bit_length']==16 and c['b6_target_angle']['signed'] and c['b6_target_angle']['snapshot']=='0xFEBEAE82')
check('B6 mode/control ID exact',c['b6_target_angle']['mode_signal_id']==254 and c['b6_target_angle']['mode_wire_byte']==3 and set(c['b6_target_angle']['decoded_mode_values'])=={'1','4','10','11','19'})
check('B6 target-vs-measured loop recovered','target-versus-measured-steering-angle' in c['b6_target_angle']['target_vs_measured_loop'] or 'target-vs-measured-steering-angle' in c['b6_target_angle']['target_vs_measured_loop'])
check('B6 physical scale stays open',c['b6_target_angle']['physical_scale_closed'] is False)
check('classic camera/IPM-A interface removal retained',all(x in c['old_camera_interface_removed'] for x in ('0x2E4','0x131','0x191','0x2FD','disabled/removed')))
cr=c['computed_retained_branch']
check('computed retained branch is live, not statically dead',cr['statically_dead'] is False and 'live' in cr['classification'])
check('computed retained magnitude writer recovered',cr['magnitude_writer']=='0x000CAD62')
check('computed retained mode-enable writer recovered',cr['mode_enable_writer']=='0x000CC7F8')
check('B6 signals 262/263 are recovered modifiers',cr['b6_modulator_signal_ids']==[262,263])
check('command-sized replacement wire scalar is recovered',cr['command_sized_wire_scalar_recovered'] is True and '0x0B6 signal255' in c['static_conclusion'])

print('\n== openpilot integration contract ==')
r=art['pre_tss3_openpilot_requirements']
check('old 260 roles retained',r['steer_torque_sensor_0x260_roles']==['driver steering torque','EPS steering torque','accurate steering angle','angle initialization'])
check('old 262 readiness role retained',r['eps_status_0x262_roles']==['LKA readiness/fault state'])
check('old fault codes explicitly marked nonportable',r['old_fault_states_are_not_portable']['temporary']==[0,9,11,21,25])
check('three concrete next discriminators',len(art['next_discriminators'])==3 and 'FRC_P5' in art['next_discriminators'][1])

print('\n== documentation integration ==')
doc=DOC.read_text() if DOC.exists() else ''
for token in ('0x4A3','0x351','0x394','0x030','0x1035','0x1037','0x1151','101','0x2E4','0x0B6','262','263','0xCC7F8','0xCAD62','signal 255','0xFEBEAE82','Target Steering Angle','FRC_P5'):
 check(f'doc preserves {token}',token in doc)
findings=(REPO/'docs/status/FINDINGS.md').read_text(); priorities=(REPO/'docs/status/PRIORITIES.md').read_text()
check('COM-009 integrated','| COM-009 |' in findings and 'corolla-h-f-openpilot-state-bridge.md' in findings)
check('priority consumes state bridge','corolla-h-f-openpilot-state-bridge.md' in priorities)
print(f'\nResults: {passed} passed, {failed} failed'); raise SystemExit(1 if failed else 0)
