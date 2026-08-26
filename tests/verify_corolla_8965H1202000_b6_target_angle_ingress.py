#!/usr/bin/env python3
"""Verify the H protected-B6 target-angle ingress proof."""
from __future__ import annotations
import hashlib,json,subprocess,sys,tempfile
from pathlib import Path
REPO=Path(__file__).resolve().parents[1]
ART=REPO/'data/generated/corolla_8965H1202000_b6_target_angle_ingress.json'
EVID=REPO/'data/generated/corolla_8965H1202000_b6_target_angle_decompiler_evidence.json'
TOOL=REPO/'tools/build_corolla_h_b6_target_angle_ingress.py'
RAW=REPO/'community/albinoelephant/normalized/8965H1202000_CodeFlash.bin'
p=f=0
def sha(b):return hashlib.sha256(b).hexdigest()
def check(n,c,d=''):
 global p,f
 ok=bool(c);p+=ok;f+=not ok;print(f"[{'PASS' if ok else 'FAIL'}][raw_bytes] {n}"+(f' ({d})' if d else ''))
with tempfile.TemporaryDirectory() as td:
 out=Path(td)/'x.json'; r=subprocess.run([sys.executable,str(TOOL),'--out',str(out)],cwd=REPO,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
 check('builder exits',r.returncode==0,r.stdout[-400:] if r.returncode else '')
 check('target-angle artifact regenerates exactly',r.returncode==0 and out.read_bytes()==ART.read_bytes())
d=json.loads(ART.read_text()); e=json.loads(EVID.read_text()); raw=RAW.read_bytes()
print('\n== source identity ==')
check('schema v4',d['schema']=='corolla-8965H1202000-b6-target-angle-ingress-v4')
check('H hash exact',d['sources']['codeflash']['sha256']==sha(raw)=='0b47bdc1217835c839e3543e52eab40eb793650a9c159e46f6a9b365ea41a67f')
check('41 compact H functions',e['function_count']==d['sources']['decompiler_evidence']['function_count']==41)
check('all compact raw bodies validate',all(sha(raw[int(x['entry'],16):int(x['entry'],16)+x['body_size']])==x['body_sha256'] for x in e['functions']))
print('\n== exact protected B6 ingress ==')
mode=d['mode_ingress']; w=d['wire_ingress']
check('signal254 is 6-bit B3 mode ID',mode['signal_id']==254 and mode['wire_byte']==3 and mode['bit_length']==6 and not mode['signed'])
check('signal254 fixed-map snapshot exact',mode['raw_destination']=='0xFEBE7D96' and mode['staging_destination']=='0xFEBEF127' and mode['snapshot_destination']=='0xFEBEADB0')
check('signal254 decoder exact values',mode['decoded_values']=={'1':['C272','C273'],'4':['C272','C26E'],'10':['C272','C270'],'11':['C272','C26F'],'19':['C272','C271']})
profiles=mode['profile_semantics']
check('signal254 accepted profiles share common active flag',profiles['common_active_flag']=='C272 is asserted for every accepted value')
check('signal254 profile flags are mutually exclusive',profiles['mutually_exclusive_profile_flags']=={'1':'C273','4':'C26E','10':'C270','11':'C26F','19':'C271'})
check('signal254 profiles select separate calibration banks','distinct calibration banks' in profiles['calibration_selection'])
check('signal254 exact OEM feature labels close',profiles['oem_dictionary_name']=='Target Lateral ID' and profiles['oem_feature_labels']=={'1':'PCS','4':'LDA','10':'Hands Off LTA','11':'LTA/LCA','19':'PDA'})
check('raw 25/27 special pair gets OEM labels','raw IDs 25 (0x19) and 27 (0x1B)' in profiles['additional_raw_id_use'] and 'AP and Remote Parking' in profiles['additional_raw_id_use'] and 'Only 25/AP' in profiles['additional_raw_id_use'])
check('signal254 OEM join proof exact','1 PCS, 4 LDA, 10 Hands Off LTA, 11 LTA/LCA, 19 PDA, 25 AP, 27 Remote Parking' in profiles['join_proof'] and 'NA/EU/JP' in profiles['join_proof'])
check('signal254 literal wire-name boundary retained','literal on-wire field name' in mode['boundary'] and 'feature labels' in mode['boundary'])
check('B6 is protected FD PDU42',w['can_id']=='0x0B6' and w['can_fd'] and w['secured'] and w['pdu_id']==42 and w['pdu_buffer_offset']=='0x01A7')
check('signal255 is signed16 B4:B5',w['signal_id']==255 and w['wire_byte']==4 and w['bit_length']==16 and w['signed'])
check('wire->raw->stage->snapshot exact',w['raw_destination']=='0xFEBE7D94' and w['staging_destination']=='0xFEBEF1CC' and w['snapshot_destination']=='0xFEBEAE82')
check('three ingress functions exact',w['unpacker']=='0x00046A10' and w['staging_copy']=='0x0005262C' and w['gp_relative_snapshot_copy']=='0x000B8EEC')
check('wire classification is target steering angle',w['classification']=='authenticated-signed16-target-steering-angle-command')
print('\n== target vs measured control proof ==')
t=d['target_angle_pipeline']; m=d['measured_angle_feedback']
check('target starts at C9DB0',t[0]['entry']=='0x000C9DB0' and 'AE82 * 2' in t[0]['relation'])
check('target replication/rate-limit at C9E54',t[1]['entry']=='0x000C9E54' and 'C098/C100/C120' in t[1]['relation'])
check('matched target-vs-measured comparator at CA138',t[2]['entry']=='0x000CA138' and 'scaled_target - scaled_measured' in t[2]['relation'])
check('actual feedback is FD025 184/185/186',m['source_can_id']=='0x025' and m['source_signals']==[184,185,186])
check('actual snapshots exact',m['snapshots']=={'184':'0xFEBEADF0','185':'0xFEBEACC5','186':'0xFEBEAE14'})
check('actual reconstruction exact constants', '0x6FB / 0x200' in m['reconstruction'] and 'fraction + coarse*15' in m['reconstruction'])
wr=m['wire_representation']
check('FD025 signal184 exact coarse-angle scale',wr['signal184']=={'bits':12,'signed':True,'role':'coarse steering angle','techstream_did':'0x1037','techstream_name':'Steering Angle','physical_scale_deg_per_count':1.5})
check('FD025 signal185 exact signed fraction scale',wr['signal185']=={'bits':4,'signed':True,'role':'signed fractional steering angle','physical_scale_deg_per_count':0.1})
check('FD025 combined angle is tenths of degree',wr['combined']=='15 * signal184 + signal185' and wr['combined_unit']=='0.1 deg' and wr['full_turn_counts']==3600 and 'divides that combined count by 3600' in wr['proof'])
check('same comparator gain recorded', 'same 0xB76/0x400 gain' in m['comparison'])
check('independent target-vs-measured loop asserted',m['classification']=='independent-target-versus-measured-steering-angle-control-loop')
check('active controller follows comparator',t[3]['entry']=='0x000CAC24/0x000CA940')
check('decoded cooperative mode gates controller',t[4]['entry']=='0x000CAD1C' and 'C272' in t[4]['relation'])
check('controller reaches replicated magnitude',t[5]['entry']=='0x000CC18E -> 0x000CC2EC -> 0x000CAD62')
check('replicated magnitude reaches C2A8',t[6]['entry']=='0x000C9C16 -> 0x000CB8BA -> 0x000CB9B6' and 'C2A8' in t[6]['relation'])
check('C2A8 reaches general torque composition',t[7]['entry']=='0x000CD3CC' and 'C3B8' in t[7]['relation'])
fb=d['final_command_bridge']
check('target contribution reaches 1C02 bridge','C2A8' in fb['local_chain'] and 'C3D2' in fb['local_chain'] and fb['recovered'])
check('final observer is Command Value Torque',fb['techstream_command_torque']=={'did':'0x1C02','name':'Command Value Torque','unit':'Nm'})
check('final q-current observer is 1152',fb['q_axis_command']=={'did':'0x1152','name':'Command Value Current (Q Axis)','unit':'A'})
check('general-command boundary retained','one conditional contributor' in fb['boundary'])
check('independent AE82 safety/plausibility consumer',d['independent_safety_consumer']['entry']=='0x000CB4F4' and d['independent_safety_consumer']['source']=='0xFEBEAE82')
print('\n== scaling boundary ==')
s=d['scaling']
check('internal target x2 relation exact','2 * signed16(B6 B4:B5)' in s['exact_internal_relation'])
check('internal measured relation exact','15*FD025_coarse' in s['exact_internal_relation'] and '1787 / 512' in s['exact_internal_relation'])
check('physical degree scale closed',s['physical_degree_scale_closed'] is True and s['controller_equivalent_fraction_deg_per_b6_count']=={'numerator':1024,'denominator':17870})
check('controller-equivalent degree value exact enough',abs(s['controller_equivalent_deg_per_b6_count']-(1024/17870))<1e-15)
check('controller-equivalent scale is ~1 mrad/count',abs(s['controller_equivalent_mrad_per_b6_count']-1.0001215187701138)<1e-12 and abs(s['difference_from_exact_1_mrad_percent']-0.01215187701137932)<1e-12)
check('OEM B6 engineering-unit name remains open',s['oem_wire_unit_name_closed'] is False and 'does not directly name' in s['interpretation'])
check('scale keeps integer quantization boundary','integer truncation' in s['quantization_boundary'] and 'exact linearized conversion' in s['quantization_boundary'])
print('\n== independent Techstream context ==')
ts=d['techstream']
check('B6 sender DTC is U012987',ts['immediate_sender_monitor']['dtc']=='U012987')
check('B6 sender is Brake System Control Module',ts['immediate_sender_monitor']['description']=='Lost Communication with Brake System Control Module' and ts['immediate_sender_monitor']['failure']=='Missing Message')
check('Corolla P5 topology includes EMPS Brake/EPB FRC',ts['corolla_p5_topology']['required_categories']==[405,435,498] and ts['corolla_p5_topology']['names']=={'405':'EMPS','435':'Brake/EPB','498':'Front Recognition Camera 2'})
check('P5 target-angle names corroborate domain',[x['name'] for x in ts['family_angle_vocabulary']]==['Target Steering Angle After Output Compensation','Advanced Drive Target Steering Angle'])
check('P5 target-angle family uses 1CEE',all(x['primary_data_id']=='0x1CEE' for x in ts['family_angle_vocabulary']))
check('Target Lateral ID dictionary joins H signal254',ts['target_lateral_id_dictionary']=={'name':'Target Lateral ID','accepted_h_profile_labels':{'1':'PCS','4':'LDA','10':'Hands Off LTA','11':'LTA/LCA','19':'PDA'},'special_h_ids':{'25':'AP','27':'Remote Parking'},'pattern_display_key':39})
check('DID1037 conversion joins H measured angle',ts['steering_angle_conversion']=={'did':'0x1037','name':'Steering Angle','h_callback':'0x488A8','raw_scale':'1.5 deg/count','physical_data_key':3,'conversion_plugin':'GetDatMonSignalInfoP5_DT.dll'})
check('exact H target observer name not overclaimed','exact H lacks DID 0x1CEE' in ts['vocabulary_boundary'] and 'OEM engineering-unit name' in ts['vocabulary_boundary'])
print('\n== generation migration ==')
mig=d['migration']
check('older Corolla was torque command','0x2E4' in mig['pre_tss3_corolla'] and 'torque' in mig['pre_tss3_corolla'])
check('Sienna angle prior art kept separate','0x131' in mig['sienna_secoc_prior_art'] and 'different wire' in mig['sienna_secoc_prior_art'])
check('H/F migration is B6 target angle','0x0B6' in mig['corolla_h_f'] and 'target-angle' in mig['corolla_h_f'])
check('no wire compatibility overclaim','none claimed' in mig['wire_compatibility'])
print('\n== static conclusion ==')
c=d['static_conclusion']
check('external lateral ingress identified',c['external_autonomous_lateral_ingress_identified'] is True)
check('ingress exact B6 signal255',c['ingress']=='protected CAN-FD 0x0B6 signal255 signed16 B4:B5')
check('command domain angle not torque',c['command_domain']=='target steering angle' and c['torque_command'] is False)
check('mode ingress exact B6 signal254',c['mode_ingress']=='protected CAN-FD 0x0B6 signal254 6-bit B3')
check('wire target reaches torque/current chain',c['reaches_command_value_torque_and_q_current'] is True)
check('immediate sender relationship brake',c['immediate_sender_relationship']=='Brake System Control Module')
check('upstream feature producer still open',c['upstream_feature_producer_identified'] is False)
check('physical controller-equivalent scale identified',c['physical_scale_identified'] is True and abs(c['controller_equivalent_deg_per_count']-(1024/17870))<1e-15)
check('OEM wire unit name remains open',c['oem_wire_unit_name_identified'] is False)
check('signal254 feature labels are identified',c['signal254_feature_labels_identified'] is True and c['signal254_profile_labels']=={'1':'PCS','4':'LDA','10':'Hands Off LTA','11':'LTA/LCA','19':'PDA'})
check('receiver request/loss/sequence contract promoted',c['request_selection_identified'] is True and c['receiver_loss_cutout_ticks']==7 and c['wall_clock_timeout_identified'] is True and c['sequence_counter_identified'] is True and c['sequence_modulus']==64 and c['sequence_gap_cap']==8)
check('next target is upstream producer, stock template and signing path','FRC_P5 -> Brake/EPB' in c['next_static_target'] and 'stock B6 cadence' in c['next_static_target'] and 'production signing/suppression path' in c['next_static_target'] and 'replacement freshness' in c['next_static_target'])
print(f'\nResults: {p} passed, {f} failed');raise SystemExit(1 if f else 0)
