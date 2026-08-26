#!/usr/bin/env python3
"""Build the exact Corolla H protected-B6 target-angle ingress proof."""
from __future__ import annotations
import argparse, hashlib, json, math, struct
from pathlib import Path

REPO=Path(__file__).resolve().parents[1]
IMAGE=REPO/'community/albinoelephant/normalized/8965H1202000_CodeFlash.bin'
EVID=REPO/'data/generated/corolla_8965H1202000_b6_target_angle_decompiler_evidence.json'
TECH=REPO/'data/generated/corolla_8965H1202000_techstream_correlations.json'
P5=REPO/'data/generated/techstream_v18/p5_lateral_control_semantics.json'
RECEIVER=REPO/'data/generated/corolla_8965H1202000_b6_receiver_contract.json'
OUT=REPO/'data/generated/corolla_8965H1202000_b6_target_angle_ingress.json'

def sha(b:bytes)->str:return hashlib.sha256(b).hexdigest()
def need(s:str,*xs:str)->bool:
    if not all(x in s for x in xs): raise ValueError('missing decompiler token(s): '+', '.join(x for x in xs if x not in s))
    return True

def main()->int:
    ap=argparse.ArgumentParser(description=__doc__); ap.add_argument('--image',type=Path,default=IMAGE); ap.add_argument('--evidence',type=Path,default=EVID); ap.add_argument('--out',type=Path,default=OUT); a=ap.parse_args()
    h=a.image.read_bytes(); e=json.loads(a.evidence.read_text()); tech=json.loads(TECH.read_text()); p5=json.loads(P5.read_text()); receiver=json.loads(RECEIVER.read_text())
    if len(h)!=0x100000 or sha(h)!=e['image']['sha256']: raise ValueError('H identity drift')
    if receiver['schema']!='corolla-8965H1202000-b6-receiver-contract-v1' or receiver['static_conclusion']['primary_loss_cutout_ticks']!=7 or receiver['static_conclusion']['sequence_modulus']!=64: raise ValueError('B6 receiver contract drift')
    funcs={int(x['entry'],16):x['decompiled_c'] for x in e['functions']}
    if e['function_count']!=41: raise ValueError('target-angle evidence count drift')
    # Raw generated COM geometry.
    sig254_pdu=struct.unpack_from('<H',h,0x223FC+254*2)[0]
    sig255_pdu=struct.unpack_from('<H',h,0x223FC+255*2)[0]
    b6_off=struct.unpack_from('<H',h,0x22788+42*2)[0]
    if sig254_pdu!=42 or sig255_pdu!=42 or b6_off!=0x1A7: raise ValueError('B6 signal/PDU geometry drift')
    need(funcs[0x46A10], 'FUN_0007643a(0xfe,0x1aa,6,0,0,0xfebe7d96);', 'FUN_0007643a(0xff,0x1ab,0x10,0,1,', '-0x3a6c')
    need(funcs[0x5262C], 'uRamfebef127 = uRamfebe7d96;', 'uRamfebef1cc = uRamfebe7d94;', 'uRamfebef182 = uRamfebe7d34;', 'uRamfebef06f = uRamfebe7d3b;')
    need(funcs[0xB8EEC], '*(code *)(iVar15 + -0xa50) = FUN_00003926[iVar15 + 1];', '*(undefined2 *)(iVar15 + -0x97e) = *(undefined2 *)(&DAT_000039cc + iVar15);', '*(undefined2 *)(iVar15 + -0xa10) = *(undefined2 *)(iVar15 + 0x3982);', '*(undefined1 *)(iVar15 + -0xb3b) = *(undefined1 *)(iVar15 + 0x386f);')
    # GP is hardcoded by these functions as FEBEB800; resolve the hidden copy exactly.
    gp=0xFEBEB800
    if gp+0x3927!=0xFEBEF127 or gp-0xA50!=0xFEBEADB0 or gp+0x39CC!=0xFEBEF1CC or gp-0x97E!=0xFEBEAE82: raise AssertionError('GP arithmetic')
    # FD025 measured-angle wire representation and independent physical-unit closure.
    need(funcs[0x4636A], 'FUN_0007643a(0xb8,0x11f,0xc,0,1,0xfebe7d34);', 'FUN_0007643a(0xb9,0x123,4,4,1,')
    need(funcs[0x42676], 'FUN_000638aa((int)sRamfebe7d34,auStack_e);', 'iVar5 + -0x3dba')
    need(funcs[0x638AA], 'param_1 + 0x7fff', 'param_1 + -0x7fff', '*param_2 = uVar1;')
    need(funcs[0xB24D0], 'sRamfebeb140 = sRamfebef182 * 0xf + (short)cRamfebef06f;')
    need(funcs[0xB23A2], '((int)sRamfebeb140 << 0x10) / 0xe10')
    # B6 signal254 is the target/control ID that selects H steering modes.
    need(funcs[0xCBE6E], "cRamfebeacbd == '\\0'", "cRamfebec26d == '\\x01'", "cRamfebeadb0 == '\\x01'", "cRamfebeadb0 == '\\x04'", "cRamfebeadb0 == '\\n'", "cRamfebeadb0 == '\\v'", "cRamfebeadb0 == '\\x13'", 'iVar2 + 0xa72', 'iVar2 + 0xa73', 'iVar2 + 0xa6e', 'iVar2 + 0xa6f', 'iVar2 + 0xa70', 'iVar2 + 0xa71')
    need(funcs[0xC825A], "cRamfebeadb0 != '\\x19'", "cRamfebeadb0 != '\\x1b'", "cRamfebeadb0 == '\\x19'", "cRamfebeadb0 == '\\x1b'")
    # Target branch.
    need(funcs[0xC9DB0], 'iVar1 = sRamfebeae82 * 2;', 'sRamfebec14c = (short)iVar2;', 'iRamfebec094 = (int)sRamfebec14c;', 'iRamfebec0fc = iRamfebec094;', 'iRamfebec11c = iRamfebec094;')
    need(funcs[0xC9E54], 'uRamfebec098 = uVar4;', 'uRamfebec100 = uRamfebec098;', 'uRamfebec120 = uRamfebec098;', "if (cRamfebec272 == '\\x01')")
    need(funcs[0xC9ED0], 'FUN_000c9cea();','FUN_000c9db0();','FUN_000c9e54();')
    # Measured angle path from 0x025 snapshots.
    need(funcs[0xCBD7E], 'cRamfebeacc5 + sRamfebeadf0 * 0xf','* 0x6fb) / 0x200','sRamfebeae14','iVar6 + 0xa30','iVar6 + 0xa34','iVar6 + 0xa38')
    need(funcs[0xCB096], 'iRamfebec230','iRamfebec234','iRamfebec238','uRamfebec23c','uRamfebec23e','uRamfebec240')
    # Exact target-minus-measured comparator: same gain on both domains.
    need(funcs[0xCA138], 'iRamfebec098','iRamfebec100','iRamfebec120','sRamfebec23c','sRamfebec23e','sRamfebec240','iVar1 = (iVar1 * 0xb76) / 0x400;','iRamfebec0bc = (iVar2 * 0xb76) / 0x400;','iRamfebec0c0 = iVar1 - iRamfebec0bc;')
    # Downstream controller and torque composition.
    need(funcs[0xCAC24], 'FUN_000ca052();','FUN_000ca138();','FUN_000ca940();')
    need(funcs[0xCA940], 'FUN_000ca614();','FUN_000cbeee();','FUN_000ca83a();')
    need(funcs[0xCAD1C], "if (cRamfebec272 == '\\x01')", 'FUN_000cac24();','FUN_000cbfce();','FUN_000cc18e();')
    need(funcs[0xCC18E], 'iVar14 + 0x9ac','iVar14 + 0x9c4','iVar14 + 0x9d0')
    need(funcs[0xCC2EC], 'iVar10 + 0x9f8','iVar10 + 0x9fc','iVar10 + 0xa06')
    need(funcs[0xCAD62], 'iVar2 + 0x97c','iVar2 + 0x97e','iVar2 + 0x984')
    need(funcs[0xC9C16], 'sRamfebec17c','sRamfebec17e','sRamfebec184','uRamfebec1e0','uRamfebec200','uRamfebec20a')
    need(funcs[0xCB8BA], 'iRamfebec278','sRamfebec1e0',"cRamfebec272 == '\\x01'")
    need(funcs[0xCB9B6], 'iRamfebec278','uRamfebec290','sRamfebec2a8 =')
    need(funcs[0xCD3CC], 'sRamfebec2a8','iRamfebec3b8')
    need(funcs[0xCD440], 'puRamfebec3b8', 'sRamfebec3bc')
    need(funcs[0xCD496], 'sRamfebec3be = sRamfebec3bc;', 'iRamfebec3ac = (int)sRamfebec3be;')
    need(funcs[0xCD53E], 'sRamfebec3be', 'sRamfebec3d0')
    need(funcs[0xCD55A], 'iVar3 + 0xbd0', 'iVar3 + 0xbc0')
    need(funcs[0xCD5DC], 'sRamfebec3c0', 'sRamfebec3d2', 'uRamfebeac5a', '/ 0x400')
    need(funcs[0xCE928], 'uRamfebeac56 = uRamfebec3d2')
    need(funcs[0xCE974], 'FUN_000cd3cc();','FUN_000cd440();','FUN_000cd496();','FUN_000cd53e();','FUN_000cd55a();','FUN_000cd5dc();','FUN_000ce928();')
    # Independent target plausibility/safety consumer.
    need(funcs[0xCB4F4], 'sVar4 = *(short *)(iVar13 + -0x97e);','*(undefined1 *)(iVar13 + 0xa69) = uVar16;')
    # Techstream corroboration: immediate monitored sender + family target-angle vocabulary.
    cm=tech['communication_monitor_dtc']; b6row=next(x for x in cm['rows'] if x['can_id']=='0x0B6')
    if b6row['pdu_id']!=42 or b6row['dtc']['techstream_code']!='U012987' or b6row['dtc']['techstream_description']!='Lost Communication with Brake System Control Module': raise ValueError('B6 Techstream sender join drift')
    modern=tech['modern_angle_domain']; names={x['monitor_key']:x['name'] for x in modern['rows']}
    if names.get(2071)!='Target Steering Angle After Output Compensation' or names.get(2072)!='Advanced Drive Target Steering Angle': raise ValueError('P5 target-angle vocabulary drift')
    cvt=tech['command_value_torque']; qbridge=tech['motor_current_bridge']
    if cvt['techstream']['primary_data_id']!='0x1C02' or cvt['techstream']['name']!='Command Value Torque' or cvt['techstream']['unit']!='Nm' or not all(x['recovered'] for x in cvt['target_native_producer_chain']): raise ValueError('1C02 command-torque bridge drift')
    if qbridge['techstream_monitors']['252']['primary_data_id']!='0x1152' or qbridge['techstream_monitors']['252']['name']!='Command Value Current (Q Axis)' or not all(x['recovered'] for x in qbridge['q_axis_command_chain']): raise ValueError('Q-current bridge drift')
    corolla_sets=p5['corolla_model_install_sets']['rows']
    if not any(x['model_name']=='Corolla' and 405 in x['categories'] and 435 in x['categories'] and 498 in x['categories'] for x in corolla_sets): raise ValueError('Corolla P5 topology drift')
    conv=p5['power_steering']['emps_angle_conversion']; steer_conv=conv['steering_angle']
    if not (steer_conv['name']=='Steering Angle' and steer_conv['physical_data_key']==3 and steer_conv['mul']==15 and steer_conv['div']==1 and steer_conv['offset']==0 and steer_conv['signed'] is True and steer_conv['decimal_point_count']==1 and steer_conv['unit']=='deg' and steer_conv['data_range']==[-2048,2047] and steer_conv['graph_range']==[-30720,30705]): raise ValueError('P5 steering-angle conversion drift')
    if 'raw * mul / div + offset' not in conv['formula'] or '0.0..300.0 km/h' not in conv['direction_witness']: raise ValueError('P5 conversion-direction proof drift')
    target_id=p5['power_steering']['target_lateral_id_semantics']
    target_id_values={int(k):v for k,v in target_id['value_dictionary'].items()}
    profile_labels={1:'PCS',4:'LDA',10:'Hands Off LTA',11:'LTA/LCA',19:'PDA'}
    if target_id['oem_name']!='Target Lateral ID' or any(target_id_values.get(k)!=v for k,v in profile_labels.items()): raise ValueError('P5 Target Lateral ID profile dictionary drift')
    if target_id_values.get(25)!='AP' or target_id_values.get(27)!='Remote Parking': raise ValueError('P5 Target Lateral ID AP/Remote Parking dictionary drift')
    did1037=next(x for x in tech['ddb_overlap']['emps_p5']['monitor_rows'] if x['monitor_key']==17)
    if did1037['name']!='Steering Angle' or did1037['primary_data_id']!='0x1037' or did1037['h_callback']!='0x488A8': raise ValueError('H DID1037 join drift')
    controller_deg_num=1024; controller_deg_den=17870
    controller_deg_per_count=controller_deg_num/controller_deg_den
    controller_mrad_per_count=controller_deg_per_count*math.pi/180*1000
    out={
      'schema':'corolla-8965H1202000-b6-target-angle-ingress-v4','software_id':'8965H1202000',
      'sources':{
        'codeflash':{'path':str(a.image.relative_to(REPO)),'sha256':sha(h)},
        'decompiler_evidence':{'path':str(a.evidence.relative_to(REPO)),'sha256':sha(a.evidence.read_bytes()),'function_count':e['function_count']},
        'techstream_correlations':{'path':str(TECH.relative_to(REPO)),'sha256':sha(TECH.read_bytes())},
        'p5_lateral_semantics':{'path':str(P5.relative_to(REPO)),'sha256':sha(P5.read_bytes())},
        'b6_receiver_contract':{'path':str(RECEIVER.relative_to(REPO)),'sha256':sha(RECEIVER.read_bytes())},
      },
      'mode_ingress':{
        'signal_id':254,'wire_byte':3,'bit_length':6,'signed':False,
        'raw_destination':'0xFEBE7D96','staging_destination':'0xFEBEF127','snapshot_destination':'0xFEBEADB0',
        'classification':'target-lateral/control-id-mode-selector',
        'decoder':'0x000CBE6E','required_gates':['FEBEACBD==0','FEBEC26D==1'],
        'decoded_values':{'1':['C272','C273'],'4':['C272','C26E'],'10':['C272','C270'],'11':['C272','C26F'],'19':['C272','C271']},
        'profile_semantics':{
          'common_active_flag':'C272 is asserted for every accepted value',
          'mutually_exclusive_profile_flags':{'1':'C273','4':'C26E','10':'C270','11':'C26F','19':'C271'},
          'oem_feature_labels':{str(k):v for k,v in profile_labels.items()},
          'oem_dictionary_name':'Target Lateral ID',
          'calibration_selection':'C9CEA/C9FAE/CB72A/CB900 and later controller helpers select distinct calibration banks from these five profile flags',
          'additional_raw_id_use':'C825A separately treats raw IDs 25 (0x19) and 27 (0x1B); Techstream Target Lateral ID identifies them as AP and Remote Parking respectively. Only 25/AP is one of CBE6E steering-controller accepted profiles.',
          'join_proof':'H CBE6E accepts exactly IDs 1/4/10/11/19 and C825A separately recognizes 25/27. Techstream P5 EMPS Target Lateral ID uses the same numeric dictionary: 1 PCS, 4 LDA, 10 Hands Off LTA, 11 LTA/LCA, 19 PDA, 25 AP, 27 Remote Parking. The dictionary is identical in EMPS_P5/EMPS2_P5 across NA/EU/JP.',
        },
        'boundary':'Target-native H proves a 6-bit cooperative-control profile ID, five accepted steering-controller profiles, and distinct per-profile calibration banks. Techstream closes the OEM feature labels for all five accepted values through the exact Target Lateral ID numeric dictionary. The literal on-wire field name is not exposed by H firmware itself.'
      },
      'wire_ingress':{
        'can_id':'0x0B6','can_fd':True,'secured':True,'pdu_id':42,'pdu_buffer_offset':'0x01A7',
        'signal_id':255,'wire_byte':4,'bit_length':16,'signed':True,
        'raw_destination':'0xFEBE7D94','staging_destination':'0xFEBEF1CC','snapshot_destination':'0xFEBEAE82',
        'unpacker':'0x00046A10','staging_copy':'0x0005262C','gp_relative_snapshot_copy':'0x000B8EEC',
        'classification':'authenticated-signed16-target-steering-angle-command',
      },
      'target_angle_pipeline':[
        {'entry':'0x000C9DB0','relation':'AE82 * 2 -> saturated C14C -> C094, then target interpolation/history C0FC/C11C'},
        {'entry':'0x000C9E54','relation':'C094 with mode-dependent delta/rate limits -> replicated target C098/C100/C120'},
        {'entry':'0x000CA138','relation':'median(C098/C100/C120) and median(C23C/C23E/C240) receive identical 0xB76/0x400 gain; C0C0 = scaled_target - scaled_measured'},
        {'entry':'0x000CAC24/0x000CA940','relation':'target-angle error enters active steering controller/filter/gain pipeline'},
        {'entry':'0x000CAD1C','relation':'decoded cooperative mode C272 selects active controller path; controller output feeds CC18E'},
        {'entry':'0x000CC18E -> 0x000CC2EC -> 0x000CAD62','relation':'controller/local state becomes replicated C17C/C17E/C184 magnitude'},
        {'entry':'0x000C9C16 -> 0x000CB8BA -> 0x000CB9B6','relation':'replicated magnitude is voted/rate-limited into C2A8'},
        {'entry':'0x000CD3CC','relation':'C2A8 contributes to general EPS torque-command composition C3B8'},
      ],
      'final_command_bridge':{
        'local_chain':'C2A8 -> CD3CC:C3B8 -> CD440:C3BC -> CD496:C3BE -> CD53E:C3D0 -> CD55A:C3C0 -> CD5DC:C3D2 -> CE928:AC56',
        'techstream_command_torque':{'did':'0x1C02','name':'Command Value Torque','unit':'Nm'},
        'q_axis_command':{'did':'0x1152','name':'Command Value Current (Q Axis)','unit':'A'},
        'recovered':True,
        'boundary':'Signal255 is one conditional contributor to the general EPS command composition; the final torque/current chain also contains local assist/control terms and gating.'
      },
      'measured_angle_feedback':{
        'source_can_id':'0x025','source_signals':[184,185,186],
        'wire_representation':{
          'signal184':{'bits':12,'signed':True,'role':'coarse steering angle','techstream_did':'0x1037','techstream_name':'Steering Angle','physical_scale_deg_per_count':1.5},
          'signal185':{'bits':4,'signed':True,'role':'signed fractional steering angle','physical_scale_deg_per_count':0.1},
          'combined':'15 * signal184 + signal185','combined_unit':'0.1 deg','full_turn_counts':3600,
          'proof':'4636A unpacks signed12 signal184 and signed4 signal185; 42676 copies signal184 without scale into DID1037 source; P5 CDbPhyData key3 defines 1.5 deg/count; B24D0 recombines 15*coarse+fraction and B23A2 divides that combined count by 3600 for a revolution/phase conversion.'
        },
        'snapshots':{'184':'0xFEBEADF0','185':'0xFEBEACC5','186':'0xFEBEAE14'},
        'reconstruction':'0xCBD7E: (fraction + coarse*15) * 0x6FB / 0x200; 0xCB096 algebraically republishes the valid measured-angle domain as C23C/C23E/C240',
        'comparison':'0xCA138 applies the same 0xB76/0x400 gain to the B6-derived target and 0x025-derived measured angle, then subtracts measured from target',
        'classification':'independent-target-versus-measured-steering-angle-control-loop',
      },
      'independent_safety_consumer':{'entry':'0x000CB4F4','source':'0xFEBEAE82','role':'absolute target magnitude / threshold / validity supervision','boundary':'algorithmic safety/plausibility role; OEM monitor name not assigned'},
      'scaling':{
        'exact_internal_relation':'target_internal_pre_controller = saturate(2 * signed16(B6 B4:B5)); measured_internal = trunc((FD025_fraction + 15*FD025_coarse) * 1787 / 512) before matched comparator gain',
        'measured_wire_physical_relation':'FD025 signal184 = 1.5 deg/count from H DID1037 + Techstream CDbPhyData key3; signed4 signal185 supplies 0.1-deg fraction, so 15*signal184+signal185 is tenths of a degree',
        'controller_equivalent_fraction_deg_per_b6_count':{'numerator':controller_deg_num,'denominator':controller_deg_den},
        'controller_equivalent_deg_per_b6_count':controller_deg_per_count,
        'controller_equivalent_mrad_per_b6_count':controller_mrad_per_count,
        'difference_from_exact_1_mrad_percent':(controller_mrad_per_count-1.0)*100,
        'physical_degree_scale_closed':True,
        'oem_wire_unit_name_closed':False,
        'interpretation':'In the matched target-vs-measured controller domain, one B6 signal255 count is equivalent to 1024/17870 deg (~0.057302742 deg), or ~1.000121519 mrad. The 0.0122% offset from exactly 1 mrad is consistent with the firmware fixed-point 1787/512 degree-to-internal approximation, but static evidence does not directly name the B6 engineering unit as milliradians.',
        'quantization_boundary':'The measured path uses integer truncation and the target path saturates after x2, so controller equality is quantized; the fraction above is the exact linearized conversion implied by the two fixed-point gains, not a claim that every individual integer target code has a unique exact degree value.'
      },
      'techstream':{
        'immediate_sender_monitor':{'dtc':b6row['dtc']['techstream_code'],'description':b6row['dtc']['techstream_description'],'failure':b6row['dtc']['techstream_failure']},
        'corolla_p5_topology':{'required_categories':[405,435,498],'names':{'405':'EMPS','435':'Brake/EPB','498':'Front Recognition Camera 2'},'interpretation':'Corolla P5 install sets contain EMPS + Brake/EPB + FRC_P5; B6 is monitored by EPS as Brake System Control Module traffic. This proves the immediate module relationship, not the upstream FRC-to-Brake wire route.'},
        'family_angle_vocabulary':[{'monitor_key':2071,'name':names[2071],'primary_data_id':'0x1CEE'},{'monitor_key':2072,'name':names[2072],'primary_data_id':'0x1CEE'}],
        'target_lateral_id_dictionary':{'name':target_id['oem_name'],'accepted_h_profile_labels':{str(k):v for k,v in profile_labels.items()},'special_h_ids':{'25':target_id_values[25],'27':target_id_values[27]},'pattern_display_key':39},
        'steering_angle_conversion':{'did':'0x1037','name':'Steering Angle','h_callback':'0x488A8','raw_scale':'1.5 deg/count','physical_data_key':3,'conversion_plugin':'GetDatMonSignalInfoP5_DT.dll'},
        'vocabulary_boundary':'EMPS_P5 family vocabulary corroborates the target-angle interpretation. The Target Lateral ID numeric dictionary exactly labels every H-observed signal254 profile/special ID, while exact H lacks DID 0x1CEE and the OEM engineering-unit name for B6 signal255 remains unjoined.'
      },
      'migration':{
        'pre_tss3_corolla':'classic 0x2E4 5-byte torque command',
        'sienna_secoc_prior_art':'protected 0x131 signed16 STEER_ANGLE_CMD uses a different wire position/path',
        'corolla_h_f':'protected FD 0x0B6 signed16 B4:B5 target-angle command through a new target-vs-measured controller architecture',
        'wire_compatibility':'none claimed; H/F scaling, request/mode fields, freshness and authentication are generation-specific'
      },
      'static_conclusion':{
        'external_autonomous_lateral_ingress_identified':True,
        'ingress':'protected CAN-FD 0x0B6 signal255 signed16 B4:B5',
        'mode_ingress':'protected CAN-FD 0x0B6 signal254 6-bit B3',
        'command_domain':'target steering angle',
        'torque_command':False,
        'reaches_command_value_torque_and_q_current':True,
        'immediate_sender_relationship':'Brake System Control Module',
        'upstream_feature_producer_identified':False,
        'physical_scale_identified':True,
        'controller_equivalent_deg_per_count':controller_deg_per_count,
        'oem_wire_unit_name_identified':False,
        'signal254_feature_labels_identified':True,
        'signal254_profile_labels':{str(k):v for k,v in profile_labels.items()},
        'request_selection_identified':receiver['static_conclusion']['request_selection_closed'],
        'receiver_loss_cutout_ticks':receiver['static_conclusion']['primary_loss_cutout_ticks'],
        'wall_clock_timeout_identified':receiver['static_conclusion']['wall_clock_timeout_closed'],
        'sequence_counter_identified':receiver['static_conclusion']['sequence_counter_closed'],
        'sequence_modulus':receiver['static_conclusion']['sequence_modulus'],
        'sequence_gap_cap':receiver['static_conclusion']['sequence_gap_cap'],
        'next_static_target':'recover upstream FRC_P5 -> Brake/EPB producer/transport, stock B6 cadence/secondary-field template, and a production signing/suppression path; replacement freshness re-anchoring and the EPS scheduler timeout are already closed'
      },
      'evidence_boundary':'The H target-angle role and controller-equivalent physical scale are firmware-primary: B6 signed16 becomes target state, is compared against independently reconstructed 0x025 measured steering angle with matched gain, and enters the steering controller. Techstream closes the 0x025 coarse-angle physical scale through DID1037 and the byte-anchored P5 conversion plugin, independently names B6 loss as Brake System Control Module loss, and closes H signal254 feature labels through the exact Target Lateral ID numeric dictionary. The dedicated receiver contract additionally closes signal254 request selection, the seven-foreground-tick / nominal-35-ms primary loss cutout, and modulo-64 sequence handling with gap cap 8. The OEM engineering-unit label for B6 signal255, Toyota stock B6 transmit cadence/template, exact secondary-field names, and the upstream FRC/Brake producer route remain unresolved; exclusive replacement freshness progression is closed separately.'
    }
    a.out.parent.mkdir(parents=True,exist_ok=True); a.out.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n'); print(json.dumps({'out':str(a.out),'classification':out['wire_ingress']['classification']},indent=2)); return 0
if __name__=='__main__': raise SystemExit(main())
