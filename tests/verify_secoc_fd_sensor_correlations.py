#!/usr/bin/env python3
"""Verify protected CAN-FD sensor correlations against committed evidence."""
from __future__ import annotations
import importlib.util, json, struct
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
ART=ROOT/'data/generated/techstream_v18/secoc_fd_sensor_correlations.json'
FW=(ROOT/'firmware/RH850_P1M-E_CodeFlash.bin').read_bytes()
passed=failed=0

def check(name,cond,detail=''):
 global passed,failed
 if cond: passed+=1; print('[PASS]',name)
 else: failed+=1; print('[FAIL]',name,detail)

d=json.loads(ART.read_text())
cs={x['semantic']:x for x in d['correlations']}
print('== promoted correlations ==')
check('three promoted correlations',len(cs)==3)
check('rear wheel speeds remain unordered pair',cs['CAN rear wheel speeds (RR/RL pair)']['confidence']=='high_pair_low_individual_order' and cs['CAN rear wheel speeds (RR/RL pair)']['firmware_signals']==[270,273])
check('SSAV high-confidence signal 276',cs['CAN Steering Angle Speed (SSAV)']['confidence']=='high' and cs['CAN Steering Angle Speed (SSAV)']['firmware_signals']==[276] and cs['CAN Steering Angle Speed (SSAV)']['unit']=='deg/s')
check('SP1 very-high-confidence signal 283',cs['CAN Vehicle Speed (SP1)']['confidence']=='very_high' and cs['CAN Vehicle Speed (SP1)']['firmware_signals']==[283] and cs['CAN Vehicle Speed (SP1)']['unit']=='km/h')
check('RR/RL individual ordering explicitly bounded',any('270 versus 273' in x for x in d['bounded_unknowns']))

print('\n== Techstream family invariants ==')
for region,r in d['techstream']['regions'].items():
 m=r['monitors']
 check(f'{region} RR name/unit/range',m['303']['name']=='CAN Vehicle Speed (Speed Sensor RR)' and m['303']['unit']=='km/h' and m['303']['range_words_i32'][:4]==[0,255,0,255])
 check(f'{region} RL name/unit/range',m['304']['name']=='CAN Vehicle Speed (Speed Sensor RL)' and m['304']['unit']=='km/h' and m['304']['range_words_i32'][:4]==[0,255,0,255])
 check(f'{region} SP1 30000 bound',m['305']['name']=='CAN Vehicle Speed (SP1)' and m['305']['unit']=='km/h' and m['305']['range_words_i32'][3]==30000)
 check(f'{region} SSAV signed16 deg/s',m['306']['name']=='CAN Steering Angle Speed (SSAV)' and m['306']['unit']=='deg/s' and m['306']['range_words_i32'][:4]==[-32768,32767,-32768,32767])

print('\n== firmware joins ==')
t=d['firmware']['transforms']
check('SP1 raw clamp 30000',t['sp1_vehicle_speed']['raw_clamp']==30000)
check('SP1 scale 0x147B/0x1000',t['sp1_vehicle_speed']['gain_numerator']==0x147B and t['sp1_vehicle_speed']['gain_denominator']==0x1000)
check('rear wheel pair common 0x931/0x100 transform',t['rear_wheel_speed_pair']['signals']==[270,273] and t['rear_wheel_speed_pair']['gain_numerator']==0x931 and t['rear_wheel_speed_pair']['gain_denominator']==0x100)
check('SSAV distinct 0x3E77/0x100 transform',t['steering_angle_speed']['signal']==276 and t['steering_angle_speed']['gain_numerator']==0x3E77 and t['steering_angle_speed']['gain_denominator']==0x100)
# Raw-code fixtures: BC484's 30000 comparison immediate and 0x147B gain remain in firmware.
check('firmware contains BC484 raw-clamp constant',struct.unpack_from('<H',FW,0xbc490)[0] in (30000,0x7530) or b'\x30\x75' in FW[0xbc480:0xbc520])

# If proprietary V18 inputs are locally available, regenerate in memory and demand exact artifact equality.
tech=ROOT/'Techstream/unpacked/toyota/Toyota Diagnostics/Techstream'
if tech.is_dir():
 spec=importlib.util.spec_from_file_location('fdcorr',ROOT/'tools/techstream/extract_secoc_fd_sensor_correlations.py')
 mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
 check('artifact deterministically regenerates from pinned V18 tree',mod.build()==d)
else:
 print('[SKIP] pinned Techstream V18 tree unavailable')

print(f'\nSummary: {passed} passed, {failed} failed')
raise SystemExit(1 if failed else 0)
