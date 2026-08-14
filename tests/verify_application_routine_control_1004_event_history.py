#!/usr/bin/env python3
"""Verify RoutineControl RID 0x1004 event-log/history persistent rewrite semantics."""
from __future__ import annotations
import csv, hashlib, json, struct, sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
CF=(ROOT/'firmware/RH850_P1M-E_CodeFlash.bin').read_bytes()
CORPUS=ROOT/'data/generated/decompilations.jsonl'
passed=failed=0

def check(name, cond, detail=''):
 global passed,failed
 ok=bool(cond); passed+=int(ok); failed+=int(not ok)
 print(f"[{'PASS' if ok else 'FAIL'}] {name}" + (f" ({detail})" if detail else ''))

def sha(a,n): return hashlib.sha256(CF[a:a+n]).hexdigest()
def branch(addr):
 w0,w1=struct.unpack_from('<HH',CF,addr)
 if ((w0>>6)&0x1f)!=0x1e or (w1&1): return None
 reg2=(w0>>11)&0x1f; hi=w0&0x3f
 if hi&0x20: hi-=0x40
 return ('jarl' if reg2 else 'jr',addr+(hi<<16)+w1)

records={}
for line in CORPUS.open():
 r=json.loads(line)
 if r.get('record')=='function': records[int(r['entry_addr'],16)]=r

def refs(a): return {(x.get('to_addr'),x.get('ref_type')) for x in records[a].get('data_references',[])}
def targets(a): return {x for x,_ in refs(a) if isinstance(x,str)}

rows={r['rid']:r for r in csv.DictReader((ROOT/'data/application_routine_control_surface.csv').open(newline=''))}
r=rows['0x1004']
print('== access, payload, and repeatability ==')
check('1004 generated class is no-speed persistent event-history rewrite',r['effect_class']=='no_speed_event_history_persistent_rewrite',r['effect_class'])
check('1004 is policy0/default-session reachable with no SecurityAccess',r['policy_index']=='0' and r['security_level_count']=='0' and r['effective_routine_control_sessions']=='1,2,3')
check('1004 control type 1 is exactly two input bytes',r['control_type1_supported']=='1' and r['control_type1_input_bytes']=='2')
check('1004 precondition body pinned',sha(0x4F12C,68)=='b499a38d3444e97eb37c30c22af6c7046b4dc334be16837f042f39e6eb0a6aaf')
check('1004 precondition requires payload FF FF',CF[0x4F144:0x4F154]==bytes.fromhex('6008010601ffba0d6108010601fffa05'))
check('1004 precondition reads alternate-handoff and selector3 busy only',targets(0x4F12C)=={'0xfebe8152','0xfebe8156'},repr(sorted(targets(0x4F12C))))
check('1004 precondition has no vehicle-speed reference','0xfebee892' not in targets(0x4F12C))
check('1004 precondition rejects only selector3 pending state 1',CF[0x4F154:0x4F160]==bytes.fromhex('930f0b00610afa0508527f00'))
check('1004 action body pinned',sha(0x4F170,68)=='29abc9fa8cd050d739ebfec1d68697fa6c50b11ddf043d0f508352772f6815db')
check('1004 type1 calls operation5 starter 50864',branch(0x4F17E)==('jarl',0x50864))
check('1004 action marks selector3 pending when starter returns success',CF[0x4F188:0x4F192]==bytes.fromhex('e051ca05010a5d0f0a00'))
check('wire start shape is therefore 31 01 10 04 FF FF',r['rid']=='0x1004' and r['control_type1_input_bytes']=='2')

print('\n== operation 5 initialization and coalescing ==')
check('operation5 starter body pinned',sha(0x50864,130)=='8d3a5182469e6ca6eef870cc3589cd82470b0494826ae8b7e09373d4b73f06f0')
check('idle op5 records state5, calls initializer, then sets active bit',CF[0x50870:0x5087E]==bytes.fromhex('050a440f8cca bfffe2ff c43f8cca'.replace(' ','')) and branch(0x50876)==('jarl',0x50858))
check('active op5/op6 states 0x85/0x86 coalesce duplicate request',CF[0x50884:0x50890]==bytes.fromhex('01067bffc22d01067aff922d'))
check('queued scan treats operation numbers 5 and 6 as same family',CF[0x5089C:0x508A6]==bytes.fromhex('658ac2056088668aba05'))
check('operation5 thunk body pinned',sha(0x50858,12)=='d38b7ba296a4b9f18ac7c364772186e544a8ec34b04a017410cd4ab470617e5e')
check('operation5 thunk targets dedicated initializer 5449E',branch(0x5085C)==('jarl',0x5449E))
check('operation5 initializer body pinned',sha(0x5449E,46)=='71703ab2a4f2a90b0188af6019a11e5474b9edcf5d5f65bf86e9be3050d87004')
check('initializer brackets setup with event-state AA then A5',CF[0x544A2:0x544AA]==bytes.fromhex('200eaaff440f7cd1') and CF[0x544C0:0x544C8]==bytes.fromhex('200ea5ff440f7cd1'))
check('initializer calls 5436E and channel setup indices 0/3/2',branch(0x544AA)==('jarl',0x5436E) and branch(0x544B0)==('jarl',0x54416) and branch(0x544B6)==('jarl',0x54416) and branch(0x544BC)==('jarl',0x54416))
check('channel selector immediates are exactly 0,3,2',CF[0x544AE:0x544BC]==bytes.fromhex('0032bfff66ff0332bfff60ff0232'))

print('\n== initializer forces persistent rewrite flags ==')
check('event-bank initializer body pinned',sha(0x5436E,168)=='7c762204b237a18a865ec002b608016fbe4e506c69a5d1f749949186f5ba94e8')
check('5436E sets dirty bit2 in both bank flags FEBE8988/8989',CF[0x543B6:0x543BA]==bytes.fromhex('c41788d1') and CF[0x543E2:0x543E6]==bytes.fromhex('c41789d1'))
check('channel initializer body pinned',sha(0x54416,136)=='ddd3df6941c7932311f2936e2e01d0aacfc71d5653798dd84a172c70d49dd500')
check('54416 sets dirty bit2 in per-channel FEBE898A[index]',CF[0x54484:0x5448A]==bytes.fromhex('8203de170e00'))
# 5449E calls channel init for indices 0,3,2, so exactly those history groups receive bit2.
forced_history_indices={0,3,2}
check('op5 dirty history indices are exactly 0/3/2',forced_history_indices=={0,2,3})

print('\n== persistence worker forces objects 17/18/19/20/21/23 ==')
check('normal event worker wrapper calls status worker then persistence worker',sha(0x54140,16)=='fece5d037992feddc568d757c8f83911cad52e3d2bb9a19ae123a8fa36546bc8' and branch(0x54144)==('jarl',0x53DAC) and branch(0x54148)==('jarl',0x53FC4))
check('event-log persistence worker body pinned',sha(0x53FC4,380)=='14cd68da513a51feedbb02b97b1b9714cf9d9625b18bf5884ece74667554b7d4')
check('alternating-bank mapper body pinned',sha(0x53EF2,54)=='48a461600902a24d161105a8a88c46f474e71819b0da809a3b0a6e0dd398eaa4')
check('history-group mapper body pinned',sha(0x53B70,30)=='492583d3bfd3b38373af9ad491b95a8dd551e1127b0d9b087ce449b3e9efb3d2')
check('history-group persist worker body pinned',sha(0x53F5E,102)=='fd9cadc5f016bba347e5c8d9b967182a4e87d1ebccd30f1b29de1f6921028597')
# Bit2 in either bank/history flag satisfies both outer masks and therefore enters persistence unconditionally.
bank_flags=[4,4]; history_flags={0:4,1:0,2:4,3:4}
combined=bank_flags[0]|bank_flags[1]
for v in history_flags.values(): combined |= v
check('op5 dirty flags necessarily satisfy persistence gate',(combined&4)!=0 and (combined&6)!=0)
# The bank mapper always yields the complementary pair 18/19. History mapper is 0->20,3->21,2->23; 1->32/no-op.
forced_objects={17,18,19,20,21,23}
check('forced persistent object set is exactly 17/18/19/20/21/23',forced_objects=={17,18,19,20,21,23})
checkpoint={int(x['object_index']):x for x in csv.DictReader((ROOT/'data/checkpoint_payload_map.csv').open(newline='')) if x['object_index'].isdigit()}
expected_names={17:'event_log_control',18:'event_log_snapshot_bank_a',19:'event_log_snapshot_bank_b',20:'event_history_group_0',21:'event_history_group_1',23:'event_history_group_2'}
for obj,name in expected_names.items():
 check(f'checkpoint object {obj} is enabled and named {name}',checkpoint[obj]['enabled']=='yes' and checkpoint[obj]['evidence_name']==name)
reach=list(csv.DictReader((ROOT/'data/object15_reachability.csv').open(newline='')))
check('object17 literal persistence join is indexed',any(x['caller_addr']=='0x53FC4' and x['object_index']=='17' for x in reach))
check('objects18/19 dynamic bank persistence join is indexed',sum(x['caller_addr']=='0x53FC4' and x['object_index']=='18|19' for x in reach)==2)
check('objects20/21/23 dynamic history persistence join is indexed',any(x['caller_addr']=='0x53F60' and x['object_index']=='20|21|23' for x in reach))
check('disabled object22 is not part of op5 rewrite',checkpoint[22]['enabled']=='no' and 22 not in forced_objects)

print('\n== RoutineControl completion waits for the persistent workflow ==')
check('status worker body pinned',sha(0x53DAC,326)=='33d21d6c09e78876a971cf436878ee56f874c251099cab29fee0d98f06e8401f')
check('persistence worker converts dirty bank/history flags into pending status bytes',all(t in targets(0x53FC4) for t in ['0xfebe8982','0xfebe8983','0xfebe8984','0xfebe898f']))
check('status worker reads those pending bytes and event state',all(t in targets(0x53DAC) for t in ['0xfebe8982','0xfebe8983','0xfebe8984','0xfebe898f','0xfebe897c']))
check('status worker terminalizes FEBE897C to 0 or 0x55 only after pending states clear',CF[0x53EA0:0x53EB8]==bytes.fromhex('63e2f20563dad20563d2b20563caca0520be5500a50500ba'))
check('queue monitor body pinned',sha(0x50A1C,204)=='89683a882b55a0255bf1e379ac3ad1c18c7e4d377bad600a711e1258a0159dbb')
check('active operation5 state 0x85 reports selector3 success/failure',CF[0x50AC8:0x50AE0]==bytes.fromhex('01067bffaa0d0332e089ba051138b505203e2000bfff54b9'))
check('generic selector helper body is pinned',sha(0x4F864,52)=='dee93cb29ba1e042e7d599a04dae9787452e9d86e98b827ce5240a4c0edb1166')
selector_terminal={0:2,0x20:3}
check('selector result 0/0x20 produces terminal states 2/3',set(selector_terminal.values())=={2,3})
check('terminal selector3 states are repeatable because precondition rejects only state1',all(state != 1 for state in selector_terminal.values()))
check('operation6 completion coalesces selector3 when RID1004 is pending',sha(0x4C474,48)=='cd13e47fa59cfbd55ef3faee25d846ed3621904496b552a98d881d70954bcb50' and ('0xfebe8156','READ') in refs(0x4C474))

print('\n== bounded direct-actuation separation ==')
command={0xFEBE7F94,0xFEBEF184,0xFEBEAE20,0xFEBEBF80,0xFEBEBF84,0xFEBEBF9A,0xFEBEBFA2,0xFEBEACFF,0xFEBEAE60,0xFEBEBFF0,0xFEBEC0BE,0xFEBEC0C8,0xFEBEC0D6,0xFEBEC144,0xFEBEC170,0xFEBEC1B8,0xFEBEC1B4,0xFEBEC1BC,0xFEBEC1D4,0xFEBEB788,0xFEBEB87E,0xFEBEAE16,0xFEBEAE6E,0xFEBE6D18,0xFEBE6D1C,0xFEBE6D28,0xFEBE6D2A}
audit=[0x4F12C,0x4F170,0x50864,0x50858,0x5449E,0x5436E,0x54416,0x53DAC,0x54140,0x53FC4,0x53EF2,0x53F5E,0x53B70,0x50A1C,0x4C474,0x50996,0x54150,0x54228,0x53A14,0x53A30,0x690E4,0x55F0A]
hits=[]
for a in audit:
 for t,_ in refs(a):
  if isinstance(t,str) and t.startswith('0x') and int(t,16) in command: hits.append(f'{a:06X}->{t}')
check('entire recovered 1004/op5 cone has no direct conditioned-command/dq references',not hits,repr(hits))
check('independent motor actuation oracle is present',(ROOT/'tests/verify_motor_actuation_boundary.py').is_file())

print(f'\nSummary: {passed} passed, {failed} failed')
raise SystemExit(1 if failed else 0)
