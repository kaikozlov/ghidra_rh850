#!/usr/bin/env python3
"""Join exact Techstream EMPS_P5 Data IDs to Sienna 8965B4512000 RDBI producers."""
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path

REPO=Path(__file__).resolve().parents[2]
FW=REPO/'firmware/RH850_P1M-E_CodeFlash.bin'
H_JOIN=REPO/'data/generated/corolla_8965H1202000_techstream_correlations.json'
OUT=REPO/'data/generated/sienna_8965B4512000_techstream_did_semantics.json'

DIDS={
0x1151:{'callback':0x4D71C,'size':60,'observer_cell':'0xFEBE66E6','source_chain':['0xFEBE66E6','0xFEBE6D1A'],'semantic':'Motor Actual Current (Q Axis)','unit':'A','monitor_key':251,'role':'actual_q_current'},
0x1152:{'callback':0x4D758,'size':60,'observer_cell':'0xFEBE66FC','source_chain':['0xFEBE66FC','0xFEBE6D2C','0xFEBE6D7E'],'semantic':'Command Value Current (Q Axis)','unit':'A','monitor_key':252,'role':'command_q_current'},
0x1153:{'callback':0x4D794,'size':60,'observer_cell':'0xFEBE66E4','source_chain':['0xFEBE66E4','0xFEBE6D18'],'semantic':'Motor Actual Current 2 (D Axis)','unit':'A','monitor_key':253,'role':'actual_d_current'},
0x1154:{'callback':0x4D7D0,'size':60,'observer_cell':'0xFEBE66FE','source_chain':['0xFEBE66FE','0xFEBE6D2E','0xFEBE6D70'],'semantic':'Command Value Current 2 (D Axis)','unit':'A','monitor_key':254,'role':'command_d_current'},
0x1155:{'callback':0x4D80C,'size':74,'observer_cell':'0xFEBE665C','source_chain':['0xFEBE665C','0xFEBE7D14','0xFEBE7D34'],'semantic':'Motor Rotation Angle','unit':'deg','monitor_key':255,'role':'motor_rotation_angle'},
0x1156:{'callback':0x4D856,'size':58,'observer_cell':'0xFEBE6764','source_chain':['0xFEBE6764','0xFEBEE608','0xFEBEAF40'],'semantic':'Final Motor Current Limited (Q Axis)','unit':'A','monitor_key':256,'role':'final_q_current_limit'},
0x1185:{'callback':0x4D930,'size':42,'observer_cell':'0xFEBE8070','source_chain':['0xFEBE8070'],'semantic':'CAN Vehicle Speed (SP1)','unit':'km/h','monitor_key':None,'role':'vehicle_speed_sp1'},
0x1C02:{'callback':0x4DB5E,'size':72,'observer_cell':'0xFEBE674A','source_chain':['0xFEBE674A','0xFEBEE40A','0xFEBEAC56','0xFEBEC1D2'],'semantic':'Command Value Torque','unit':'Nm','monitor_key':402,'role':'internal_command_value_torque'},
}

FUNCTIONS={
0x37644:(202,'dual_motor_dq_feedback_combine'),0x37712:(120,'dual_motor_dq_current_reference'),0x472A6:(38,'motor_rotation_wrap'),
0x5B662:(222,'rte_snapshot_copy'),0x5C0B6:(1204,'rte_input_staging_copy_b'),0x5C56A:(252,'rte_snapshot_copy_2'),
0xB8ED0:(128,'q_limit_publish'),0xBCA88:(66,'q_limit_rte_publish'),0xBCACE:(104,'command_torque_rte_publish'),0xCB454:(72,'command_torque_state_publish'),
}

def digest(fw,a,n): return hashlib.sha256(fw[a:a+n]).hexdigest()

def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--output',type=Path,default=OUT); a=ap.parse_args()
 fw=FW.read_bytes(); h=json.loads(H_JOIN.read_text()); monitors=h['motor_current_bridge']['techstream_monitors']
 # Monitor 402 is outside motor_current_bridge; recover its exact DDB row from overlap.
 rows=h['ddb_overlap']['emps_p5']['monitor_rows']; m402=next(x for x in rows if x['monitor_key']==402)
 # Vehicle speed 1185 is a separately proved exact DID name in the same artifact.
 m1185=next(x for x in rows if x['primary_data_id'].lower()=='0x1185')
 out=[]
 for did,row in DIDS.items():
  if row['monitor_key'] in monitors: src=monitors[str(row['monitor_key'])] if str(row['monitor_key']) in monitors else monitors[row['monitor_key']]
  elif row['monitor_key']==402: src=m402
  elif did==0x1185: src=m1185
  else: src={}
  entry=dict(row); entry.update({'did':f'0x{did:04X}','callback':f"0x{row['callback']:08X}",'callback_sha256':digest(fw,row['callback'],row['size']),
    'techstream_record_sha256':src.get('ddb_record_sha256'),'techstream_name':src.get('name',row['semantic']),'techstream_primary_data_id':src.get('primary_data_id',f'0x{did:04X}'),
    'techstream_alternate_data_id':src.get('alternate_data_id'),'confidence':'exact DID vocabulary + target-native producer/dataflow'})
  out.append(entry)
 functions=[{'address':f'0x{x:08X}','size':sz,'role':role,'sha256':digest(fw,x,sz)} for x,(sz,role) in FUNCTIONS.items()]
 obj={'schema_version':1,'software_id':'8965B4512000','image_sha256':hashlib.sha256(fw).hexdigest(),'dids':out,'supporting_functions':functions,
 'observer_priority':['0x1C02','0x1152','0x1151','0x1153','0x1156','0x1154','0x1185','0x1155'],
 'boundary':'Techstream names are carried by exact primary Data ID identity plus Sienna target-native callback/dataflow. 1C02 names a general internal command-value torque observable; it is not intrinsically a specific external steering-CAN field.'}
 a.output.parent.mkdir(parents=True,exist_ok=True); a.output.write_text(json.dumps(obj,indent=2,sort_keys=True)+'\n')
 return 0
if __name__=='__main__': raise SystemExit(main())
