#!/usr/bin/env python3
"""Verify the configuration-dependent bounds of the unchecked event snapshot formatter."""
from __future__ import annotations
import hashlib,json,struct,subprocess,sys,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
S=(ROOT/'firmware/RH850_P1M-E_CodeFlash.bin').read_bytes()
H=(ROOT/'community/albinoelephant/raw-20260818/albinoelephant-corolla-2023.20260814-0023/dump_codeflash_00000000_00200000_20260814-025814.bin').read_bytes()[:0x100000]
F=(ROOT/'community/spanconstant/raw-20260821/span-corolla-2025.20260821-1511/dump_codeflash_00000000_00200000_20260821-152033.bin').read_bytes()[:0x100000]
EVP=ROOT/'data/generated/corolla_8965H1202000_keyless_event_formatter_decompiler_evidence.json'
EV=json.loads(EVP.read_text())
ARTP=ROOT/'data/generated/corolla_8965H1202000_keyless_event_formatter.json'
ART=json.loads(ARTP.read_text())
BUILD=ROOT/'tools/build_corolla_h_keyless_event_formatter.py'
SC={}
for line in (ROOT/'data/generated/decompilations.jsonl').read_text().splitlines():
 r=json.loads(line)
 if r.get('entry_addr'):SC[int(r['entry_addr'],16)]=r
HE={int(x['entry'],16):x for x in EV['functions']}
p=f=0
def sha(b):return hashlib.sha256(b).hexdigest()
def ck(n,c,d=''):
 global p,f
 ok=bool(c);p+=ok;f+=not ok;print(f"[{'PASS' if ok else 'FAIL'}][cfg_dataflow] {n}"+(f' ({d})' if d else ''))
def bounds(img,desc_base,count,event_base):
 rows=[]
 for i in range(count):
  a=desc_base+i*0x18; rows.append((struct.unpack_from('<H',img,a+0x14)[0],img[a+0x16]))
 vals=[]
 for i in range(0x40):
  a=event_base+i*8; eid=struct.unpack_from('<h',img,a)[0]; mask=struct.unpack_from('<H',img,a+2)[0]
  if not mask: continue
  selected=[ln for m,ln in rows if m & mask]
  vals.append((3+sum(3+ln for ln in selected),eid,mask,len(selected),sum(selected)))
 return rows,vals
print('== deterministic report regeneration ==')
with tempfile.TemporaryDirectory() as td:
 out=Path(td)/'event.json'
 r=subprocess.run([sys.executable,str(BUILD),'--out',str(out)],cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
 ck('event-formatter builder exits',r.returncode==0,r.stdout[-500:] if r.returncode else '')
 ck('event-formatter report regenerates exactly',r.returncode==0 and out.read_bytes()==ARTP.read_bytes())
ck('three target-native role mappings are explicit',ART['role_closure_count']==3 and {(x['reference_entry'],x['target_entry']) for x in ART['role_closure']}=={('0x00054910','0x00050038'),('0x000549FA','0x00050122'),('0x00054A7E','0x000501A6')})

print('== target-native H evidence ==')
ck('six H functions are compacted',EV['function_count']==6==len(HE))
ck('H image hash pinned',EV['image']['codeflash_sha256']==sha(H))
ck('all H raw bodies validate',all(sha(H[a:a+x['body_size']])==x['body_sha256'] for a,x in HE.items()))
ck('all H decompiler hashes validate',all(sha(x['decompiled_c'].encode())==x['decompiled_c_sha256'] for x in HE.values()))
inner_s=SC[0x54910]['decompiled_c']; wrap_s=SC[0x549FA]['decompiled_c']; sib_s=SC[0x54A7E]['decompiled_c']; worker_s=SC[0x8CF84]['decompiled_c']
inner_h=HE[0x50038]['decompiled_c']; wrap_h=HE[0x50122]['decompiled_c']; sib_h=HE[0x501A6]['decompiled_c']; worker_h=HE[0x87384]['decompiled_c']; helper_h=HE[0x50D10]['decompiled_c']
print('\n== unchecked formatter structure ==')
for tag,c in [('Sienna',inner_s),('Corolla H',inner_h)]:
 ck(f'{tag} formatter advances output by descriptor length without capacity operand','iVar9 = iVar9 + 3 + (uint)*(byte *)(iVar1 + 0x16);' in c and 'param_4 & 0xffff' not in c)
for tag,c in [('Sienna',wrap_s),('Corolla H',wrap_h)]:
 ck(f'{tag} wrapper can append both snapshot banks',c.count('param_1,param_2')>=2 and c.count('param_3')>=2)
 ck(f'{tag} wrapper checks total against capacity only after formatter calls',c.rfind('param_4 & 0xffff') > c.rfind('param_1,param_2'))
for tag,c in [('Sienna',sib_s),('Corolla H',sib_h)]:
 ck(f'{tag} sibling formatter has an in-loop capacity check','param_4 & 0xffff' in c and '+ uVar7 + 3' in c)
print('\n== configured reachable output bounds ==')
srows,svals=bounds(S,0x2A504,0x4B,0x2AD10); hrows,hvals=bounds(H,0x29F1C,0x4E,0x2A770); frows,fvals=bounds(F,0x29F1C,0x4E,0x2A770)
ck('Sienna helper count is 75','*param_1 = 0x4b;' in SC[0x555E8]['decompiled_c'])
ck('H helper count is 78 and table is 0x29F1C','*param_1 = 0x4e;' in helper_h and 'PTR_DAT_00029f1c' in helper_h)
ck('H/F descriptor tables are byte-identical',H[0x29F1C:0x29F1C+0x4E*0x18]==F[0x29F1C:0x29F1C+0x4E*0x18])
ck('H/F event maps are byte-identical',H[0x2A770:0x2A970]==F[0x2A770:0x2A970])
ck('Sienna reachable one-bank maximum is 207',max(x[0] for x in svals)==207,str(sorted(svals,reverse=True)[:1]))
ck('H reachable one-bank maximum is 202',max(x[0] for x in hvals)==202,str(sorted(hvals,reverse=True)[:1]))
ck('F reachable one-bank maximum is also 202',max(x[0] for x in fvals)==202)
ck('Sienna two-bank conservative maximum is 414',2*max(x[0] for x in svals)==414)
ck('H/F two-bank conservative maximum is 404',2*max(x[0] for x in hvals)==404==2*max(x[0] for x in fvals))
print('\n== staging capacity and portability ==')
ck('Sienna AB worker resets staging capacity to 0x300','DAT_febf45d6 = 0x300;' in worker_s)
ck('H AB worker resets staging capacity to 0x300','_DAT_febf45d6 = 0x300;' in worker_h)
ck('Sienna configured headroom is 354 bytes',0x300-2*max(x[0] for x in svals)==354)
ck('H/F configured headroom is 364 bytes',0x300-2*max(x[0] for x in hvals)==364)
ck('F carries H formatter/wrapper/worker bytes exactly',F[0x50038:0x50038+234]==H[0x50038:0x50038+234] and F[0x50122:0x50122+90]==H[0x50122:0x50122+90] and F[0x87384:0x87384+364]==H[0x87384:0x87384+364])
ck('tracked configurations stay below staging capacity',414<0x300 and 404<0x300)
ck('generated report publishes exact S/H/F maxima',ART['bounds']['sienna']['conservative_two_bank_max']==414 and ART['bounds']['corolla_h']['conservative_two_bank_max']==404 and ART['bounds']['corolla_f']['conservative_two_bank_max']==404)
ck('generated report preserves configuration-dependent safety boundary',ART['static_conclusion']['configuration_dependent_safety'] and not ART['static_conclusion']['tracked_images_overflow'] and 'not a global static-attack absence claim' in ART['static_conclusion']['boundary'])
print(f'\nResults: {p} passed, {f} failed'); raise SystemExit(1 if f else 0)
