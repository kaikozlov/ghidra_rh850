#!/usr/bin/env python3
"""Close the remaining application RoutineControl query/lifecycle/persistence controls."""
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

def refs(a):
 return {(x.get('to_addr'),x.get('ref_type')) for x in records[a].get('data_references',[])}
def targets(a): return {x for x,_ in refs(a) if isinstance(x,str)}

rows={r['rid']:r for r in csv.DictReader((ROOT/'data/application_routine_control_surface.csv').open(newline=''))}
print('== generated classifications and access boundary ==')
expected={
 '0x1001':('capability_bitmap_query','0x4EFFE','0x4F00A'),
 '0x1002':('speed_gated_lifecycle_reinit','0x4F0AE','0x4F0EA'),
 '0x1103':('gated_mode1_service_control','0x4F37C','0x4F3C0'),
 '0x1106':('speed_gated_multigroup_reinit','0x4F400','0x4F43E'),
 '0x1108':('no_speed_persistent_checkpoint_reset','0x4F48E','0x4F4BC'),
 '0x1109':('speed_state_gated_redundant_object0_update','0x4F500','0x4F570'),
}
for rid,(effect,pre,act) in expected.items():
 r=rows[rid]
 check(f'{rid} generated class is exact',r['effect_class']==effect,r['effect_class'])
 check(f'{rid} uses policy0 sessions 1/2/3 without SecurityAccess',r['policy_index']=='0' and r['security_level_count']=='0' and r['effective_routine_control_sessions']=='1,2,3')
 check(f'{rid} callback pair is pinned',r['precondition_callback']==pre and r['action_callback']==act)

print('\n== RID 1001 is a read/query bitmap ==')
check('1001 precondition is immediate policy body',sha(0x4EFFE,12)=='84a8f2ef0650e0289b731957f14db0272156864b6f95f08ea606cb36e067ec1a')
check('1001 action body is pinned',sha(0x4F00A,74)=='8632e9331a905cb16b7014c0ef51d1eba9c5167335944327b5f7c63b6f97adb1')
check('1001 builder body is pinned',sha(0x4C5AE,86)=='3ab6859c16db64592ab7417cf2f39463c0320dd38e906fe8b7c167a6d48e9709')
check('1001 type1 calls support-bitmap builder with 0x20-byte output',branch(0x4F01C)==('jarl',0x4C5AE) and CF[0x4F018:0x4F01C]==bytes.fromhex('203e2000'))
check('1001 type1 marks selector-1 status complete directly',CF[0x4F02A:0x4F030]==bytes.fromhex('020a440f54c9'))
check('1001 output width is 32 bytes',rows['0x1001']['control_type1_output_bytes']=='32')

print('\n== RID 1002 speed-gated lifecycle normalization/reinit ==')
check('1002 precondition body pinned',sha(0x4F0AE,60)=='4066aeaa40016233deac2b002e9cbe825d79f59b3d149ac9e5290b80831fd360')
check('1002 precondition reads vehicle-speed state', '0xfebee892' in targets(0x4F0AE),repr(sorted(targets(0x4F0AE))))
check('1002 action body pinned',sha(0x4F0EA,66)=='65afb32b1420788d13b905d142e0c894437dfba0f363cf3f3189608bad8e0dfe')
check('1002 type1 calls 35582 then requests 0x44 through FDE08',branch(0x4F0F4)==('jarl',0x35582) and branch(0x4F0FC)==('jarl',0xFDE08) and CF[0x4F0F8:0x4F0FC]==bytes.fromhex('20364400'))
check('1002 writes pending status FEBE8155=1',('0xfebe8155','WRITE') in refs(0x4F0EA))
check('1002 application worker body pinned',sha(0xB7E6E,182)=='bf7950266f1d10f78fc58f7fee440f858576f5a366843d7b40ab5706d0940dc1')
check('0x44 branch calls B79F8(1) then B7A36(1)',branch(0xB7EBC)==('jarl',0xB79F8) and branch(0xB7EC8)==('jarl',0xB7A36))
check('1002 lifecycle helpers pinned',sha(0xB79F8,62)=='cc7d98099d539e15a75d7bc4b0dc469e5c5dd0e263a5f7ff8d39d123bffc9d6c' and sha(0xB7A36,120)=='9eaec849349c3a159a1c2b70071fe315cb083cfb92fdad969144af6f1c590209')

print('\n== RID 1103 gated internal-mode-1 service request ==')
check('1103 precondition/action bodies pinned',sha(0x4F37C,68)=='c5700bc9cfda343f2d3aeb618f0e5c38a0d5a0d8ed98f200cf103beb3006b63a' and sha(0x4F3C0,64)=='49721caad6060683c707dc89efa6c59c4d57be8ec6ac8cc917d67bc4cf6beb5c')
check('1103 eligibility helper pinned',sha(0x354E6,98)=='a1c1bcaf237887806b3e102bcee0948f8f66a731fa2e27ca803f41f1a6d78d1a')
check('1103 eligibility helper includes vehicle-speed state', '0xfebee892' in targets(0x354E6),repr(sorted(targets(0x354E6))))
check('1103 action calls 35576 and maps return-2 to pending',branch(0x4F3CE)==('jarl',0x35576) and CF[0x4F3D2:0x4F3DC]==bytes.fromhex('6252da05010a00525d0f'))
check('35576 fixed body sets FEBE6ABA=0x11 and returns 2',sha(0x35576,12)=='c0002b54c1393dc65b0d50a6b1942f16bb1b99c6f439a25f2a8f9028989e56a8' and ('0xfebe6aba','WRITE') in refs(0x35576))
check('per-tick 352A0 body pinned',sha(0x352A0,138)=='efc214561f31964449976ed52b1f249e410797a88cb354e2394e6908f6120c5e')
check('1103 path requests internal mode 1 through FE038',CF[0x352DE:0x352E4]==bytes.fromhex('01328cff588d') and branch(0x352E0)==('jarl',0xFE038))
check('mode arbiter and selector-8 completion bodies pinned',sha(0xB1F34,188)=='a74de522bc3d1f13747959c168eb1aac75c787fcca4cef1d309f48b564768a01' and sha(0xB1CFE,48)=='88a8e79dff7d99d3ae834cd340ec1c938f54335236706daba1e151ed9ae5fe00')

print('\n== RID 1106 speed-gated three-group lifecycle reinit ==')
check('1106 precondition/action bodies pinned',sha(0x4F400,62)=='facfa0d92b28416e68eafc6119759c54b695c7ae3046bee2da5ab1ded58f3812' and sha(0x4F43E,80)=='c8a7663283cb38f42511935130ab2d617acf5ef8dd903d473baf95ef5cef6ae6')
check('1106 precondition reads vehicle speed', '0xfebee892' in targets(0x4F400),repr(sorted(targets(0x4F400))))
check('1106 action starts reinit only when FEBEE958 is zero',('0xfebee958','READ') in refs(0x4F43E) and branch(0x4F454)==('jarl',0xFDE6C))
check('B3974 body pinned',sha(0xB3974,28)=='964531c41537b4c397e7de7714b98f17f8e4084f8ab4d8f47390ea191bb8b087')
check('B3974 starts two state machines and marker group',all(branch(a)==('jarl',t) for a,t in [(0xB3978,0xB47D2),(0xB397C,0xB5CF4),(0xB3980,0xB7C04)]))
check('1106 completion worker body pinned',sha(0xB38C0,116)=='59c3c991a2670aae8e552a60055370842c2cfc057cafb3ec0131bff166de6280')
check('1106 completion worker reads 25A/325/48D',all((t,'READ') in refs(0xB38C0) for t in ['0xfebeb25a','0xfebeb325','0xfebeb48d']))
check('1106 reports selector 9 success/failure through C430 thunk',branch(0xB38F0)==('jarl',0xFEC00) and branch(0xB3924)==('jarl',0xFEC00) and CF[0xB38EC:0xB38F0]==bytes.fromhex('0932003a'))

print('\n== RID 1108 no-speed persistent checkpoint reset ==')
check('1108 precondition/action bodies pinned',sha(0x4F48E,46)=='93fd433860e024580a90d79627ff0a6c3f59a0e022a688a34cbca19215c7e170' and sha(0x4F4BC,68)=='99a19dd2c333663e0a8a2483efa784f86cc7bb7a949196a064b935ca19de1af2')
check('1108 precondition has alternate/busy state but no vehicle-speed reference','0xfebe8152' in targets(0x4F48E) and '0xfebe815d' in targets(0x4F48E) and '0xfebee892' not in targets(0x4F48E),repr(sorted(targets(0x4F48E))))
check('1108 action directly starts/queues operation 2',branch(0x4F4CA)==('jarl',0x50760))
check('1108 action sets status FEBE815D pending after 50760 return 0',('0xfebe815d','WRITE') in refs(0x4F4BC))
check('operation-2 starter and initializer bodies pinned',sha(0x50760,138)=='a25cabafa8560267791181e7444f2b8e420553a6a26a321c63e73242cbde9d9d' and sha(0x5070C,84)=='0342dc36eabb4aaab753c81af0647f632f21b91489067ff8fc26926c625b82e6')
check('idle operation-2 path writes state 2, calls initializer, sets active bit',CF[0x5076C:0x5077A]==bytes.fromhex('020a440f8cca bfff9aff c43f8cca'.replace(' ','')) and branch(0x50772)==('jarl',0x5070C))
expected_op2_calls=[0xFDFE8,0x539A8,0x390E6,0x453A2,0xFDDF4,0xFDDE0,0x545DC]
actual_op2_calls=[branch(a)[1] if branch(a) else None for a in [0x50714,0x50718,0x5071C,0x50720,0x50724,0x50728,0x5072C]]
check('operation-2 unconditional initializer fan-out is exact',actual_op2_calls==expected_op2_calls,repr([hex(x) for x in actual_op2_calls]))
persist_rows=list(csv.DictReader((ROOT/'data/object15_reachability.csv').open(newline='')))
def persisted(caller,obj): return any(r['caller_addr']==caller and r['object_index']==str(obj) and r['async_persist_behavior']=='checkpoint_persist' for r in persist_rows)
for caller,obj in [('0xBAFB2',9),('0xBB3C6',11),('0x453A2',12),('0x539A8',14),('0xBB5EC',15)]:
 check(f'operation-2 reset fan-out persists checkpoint object {obj}',persisted(caller,obj))
check('operation monitor body pinned',sha(0x50A1C,204)=='89683a882b55a0255bf1e379ac3ad1c18c7e4d377bad600a711e1258a0159dbb')
check('active op2 state 0x82 reports selector 10 result 0/0x20',CF[0x50AA8:0x50AC8]==bytes.fromhex('01067effea0de099aa0de0918a0de081ea05e089ca050a321038d50d0a32950d'))
check('operation6 completion coalesces pending selectors 3 and 10',sha(0x4C474,48)=='cd13e47fa59cfbd55ef3faee25d846ed3621904496b552a98d881d70954bcb50' and ('0xfebe815d','READ') in refs(0x4C474))

print('\n== RID 1109 speed/state-gated redundant object-0 persistence ==')
check('1109 precondition/action bodies pinned',sha(0x4F500,112)=='3cb3f97102af2e60e00264f3745ba5b12b2e08be6287961111bfde500404a545' and sha(0x4F570,84)=='99a3b8e5f84ab4b622909b27918b06dffbc7310d351cd32aa48cc1828c56d7b9')
check('1109 precondition includes vehicle-speed and state gates','0xfebee892' in targets(0x4F500) and '0xfebe815e' in targets(0x4F500),repr(sorted(targets(0x4F500))))
check('1109 action calls B7D26 thunk with mode 0x22 and phase bit 1',CF[0x4F57E:0x4F588]==bytes.fromhex('20362200013a8afface8') and branch(0x4F584)==('jarl',0xFDE30))
check('B7D26 body pinned',sha(0xB7D26,194)=='639ed5a0f9aa8fe3f0a8c6c03b8de84fb83ea3cd32c920e41a358cab72746d6d')
check('object0 update helper body pinned',sha(0x3547E,56)=='98b8f54819101ba03bd5abaf82cbcf74d2ca80c705f2eae0ae389c2ec13100ac')
check('3547E submits literal namespace-0x100 object 0 through secoc NVM dispatcher',CF[0x3549C:0x354AE].startswith(bytes.fromhex('20360001')) and branch(0x354AA)==('jarl',0x65CD8))
check('1109 accepts no tester payload bytes',rows['0x1109']['control_type1_input_bytes']=='0')
check('redundant object0 descriptor is 16 bytes at FEBEF468 with base NvM block 2',struct.unpack_from('<HHI',CF,0x2B0AC)==(16,2,0xFEBEF468),repr(struct.unpack_from('<HHI',CF,0x2B0AC)))
check('3547E persists fixed reset/default representation: marker 0, four 0x800 halfwords, zero tail',
      CF[0x3548E:0x354AA]==bytes.fromhex('03f001050705200e0008850c840c20360001830c0338820c20ee1100'))
check('valid object0 writer uses A55A5AA5 marker and staged four-channel offsets',
      sha(0x35260,64)=='cc7a43bda4ec1523073e94482a1076353173f5704432ba549887c336669b3712'
      and CF[0x35288:0x35290]==bytes.fromhex('2106a55a5aa5010d'))
check('object0 restore copies four persisted halfwords into staged offset bank',
      sha(0x350D6,74)=='1f4731d4b18caa293fdd29158c406b208c36979c248e0c865e2beef91a5435ff'
      and all((t,'WRITE') in refs(0x350D6) for t in ['0xfebe6abe','0xfebe6ac0','0xfebe6ac2','0xfebe6ac4']))
check('staged offsets copy into active four-channel offset bank',
      sha(0x35048,30)=='c763d66277c97e591ade510a90dc5f2d493c8194b3b8619cfb3320f8be39032d'
      and all((t,'WRITE') in refs(0x35048) for t in ['0xfebe6aaa','0xfebe6aac','0xfebe6aae','0xfebe6ab0']))
check('neutral/default helper sets all four active offsets to 0x800',
      sha(0x35066,18)=='e28bccbbdc75db223d8c0f5ec2516987d42ab863fbfd9413dc777b7b3167e775')
check('live signal-conditioning transform reads raw quartet and active offset quartet',
      sha(0x47A5C,396)=='b216623036f56554fe8c48595a35a0b4843b8ad71ec525efb2e258037f887c04'
      and all((t,'READ') in refs(0x47A5C) for t in ['0xfebe819e','0xfebe81a0','0xfebe81a2','0xfebe81a4','0xfebe6aaa','0xfebe6aac','0xfebe6aae','0xfebe6ab0']))
check('signal-conditioning transform subtracts offsets before four scale/divide-by-0x800 paths',
      CF[0x47A94:0x47AA0]==bytes.fromhex('b3097498b2997590b1917688') and CF[0x47AB0:0x47AD0].count(bytes.fromhex('fc02'))==4)
check('1109 completion state machines pinned',sha(0xB7CC6,96)=='c45a552c8d30b2028495022c78efe029dfc7db4b007a61cbda51f1fb9c6ef221' and sha(0xB7C4A,124)=='f39c8cccd6d98fe61861ff045ddf158c2adbe3fc73ed693bb260391b0716499a')
check('B7C4A reports selector 11 through C430 thunk',CF[0xB7C98:0xB7CA0]==bytes.fromhex('1a380b3284ff646f') and branch(0xB7C9C)==('jarl',0xFEC00))

print('\n== bounded separation from direct current/PWM actuation ==')
command={0xFEBE7F94,0xFEBEF184,0xFEBEAE20,0xFEBEBF80,0xFEBEBF84,0xFEBEBF9A,0xFEBEBFA2,0xFEBEACFF,0xFEBEAE60,0xFEBEBFF0,0xFEBEC0BE,0xFEBEC0C8,0xFEBEC0D6,0xFEBEC144,0xFEBEC170,0xFEBEC1B8,0xFEBEC1B4,0xFEBEC1BC,0xFEBEC1D4,0xFEBEB788,0xFEBEB87E,0xFEBEAE16,0xFEBEAE6E,0xFEBE6D18,0xFEBE6D1C,0xFEBE6D28,0xFEBE6D2A}
audit=[0x4C5AE,0x4F0EA,0xB7E6E,0xB7A36,0x354E6,0x35576,0x352A0,0xB1F34,0xB1CFE,0xB3974,0xB38C0,0x50760,0x5070C,0x50A1C,0x4C474,0xB7D26,0x3547E,0xB7CC6,0xB7C4A]
hits=[]
for a in audit:
 for t,_ in refs(a):
  if isinstance(t,str) and t.startswith('0x') and int(t,16) in command: hits.append(f'{a:06X}->{t}')
check('remaining RoutineControl cohort has no direct conditioned-command/dq state references',not hits,repr(hits))
check('independent motor actuation oracle remains present',(ROOT/'tests/verify_motor_actuation_boundary.py').is_file())

print(f'\nSummary: {passed} passed, {failed} failed')
raise SystemExit(1 if failed else 0)
