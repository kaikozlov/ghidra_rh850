#!/usr/bin/env python3
"""Verify closure of the nine remaining named Corolla-H steering roles."""
from __future__ import annotations
import hashlib,json,subprocess,sys,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
ART=ROOT/'data/generated/corolla_8965H1202000_steering_nested.json'; EV=ROOT/'data/generated/corolla_8965H1202000_steering_nested_decompiler_evidence.json'; TOOL=ROOT/'tools/build_corolla_h_steering_nested.py'; RAW=ROOT/'community/albinoelephant/raw-20260818/albinoelephant-corolla-2023.20260814-0023/dump_codeflash_00000000_00200000_20260814-025814.bin'
p=f=0
def check(n,c):
 global p,f
 ok=bool(c);p+=ok;f+=not ok;print(f"[{'PASS' if ok else 'FAIL'}][raw_bytes] {n}")
def sha(b):return hashlib.sha256(b).hexdigest()
with tempfile.TemporaryDirectory() as td:
 out=Path(td)/'x.json';subprocess.run([sys.executable,str(TOOL),'--out',str(out)],cwd=ROOT,check=True,stdout=subprocess.DEVNULL);check('report regenerates exactly',out.read_bytes()==ART.read_bytes())
d=json.loads(ART.read_text());e=json.loads(EV.read_text());raw=RAW.read_bytes()[:0x100000]
check('H image hash pinned',sha(raw)==e['image']['codeflash_sha256'])
check('14 target-native functions compacted',e['function_count']==14==len(e['functions']))
check('all raw bodies validate',all(sha(raw[int(r['entry'],16):int(r['entry'],16)+r['body_size']])==r['body_sha256'] for r in e['functions']))
check('all decompiler hashes validate',all(sha(r['decompiled_c'].encode())==r['decompiled_c_sha256'] for r in e['functions']))
by={int(r['entry'],16):r for r in e['functions']}
check('six one-to-one steering roles recovered',d['steering_role_closure_count']==6)
check('three classic command roles closed by recensus',d['classic_command_surface_recensus_count']==3)
check('pipeline maps to H CEDAE',d['pipeline']['h']=='0x000CEDAE' and d['pipeline']['h_wrapper_calls_pipeline'])
check('wrapper maps to H CF028',d['pipeline']['wrapper_h']=='0x000CF028')
check('LTA limiter is terminal fourth call in paired wrapper',d['lta_rate_limit']['h_is_fourth_wrapper_call'] and d['lta_rate_limit']['h_wrapper_call_count']==4)
check('H LTA limiter writes regenerated output bank',all(x.lower().replace('0x','') in by[0xC9C16]['decompiled_c'].lower().replace('0x','') for x in ['FEBEC1E0','FEBEC200','FEBEC20A']))
pri=d['primary_command_conditioning']
check('primary command wrapper keeps six stages',pri['wrapper_call_count_sienna']==6==pri['wrapper_call_count_h'])
check('mode select and slew targets are ordered',pri['ordered_targets'][3:6]==['0x000CB8BA','0x000CB900','0x000CB9B6'])
check('H mode select uses local supervisor mode and selected command',all(s in by[0xCB8BA]['decompiled_c'] for s in ['cRamfebec272','iRamfebec278','cRamfebec2a6']))
check('H slew stage consumes selected command and emits conditioned output',all(s in by[0xCB9B6]['decompiled_c'] for s in ['iRamfebec278','sRamfebec2a8']))
rep=d['classic_command_mode_replacement']
check('classic 2E4/131 command inputs stay absent',not rep['classic_2e4_rx_present'] and not rep['classic_131_rx_present'])
check('replacement decoder is H CBE6E behind CB68A',rep['h_decoder']=='0x000CBE6E' and rep['h_decoder_wrapper']=='0x000CB68A' and 'FUN_000cbe6e' in by[0xCB68A]['decompiled_c'])
check('replacement decoder reads H-specific mode state',all(s in by[0xCBE6E]['decompiled_c'] for s in ['cRamfebeacbd','cRamfebec26d','cRamfebeadb0']))
sec=d['secondary_command_conditioning']
check('secondary parent chain maps BA3DA/CBA42/CB49C to B8E84/CEFF8/CE974',sec['h_parent_chain']==['0x000B8E84','0x000CEFF8','0x000CE974'])
check('secondary select maps to H CD3CC',sec['select']['h']=='0x000CD3CC' and 'iRamfebec3b8' in by[0xCD3CC]['decompiled_c'])
check('following gain clip remains H CD440 anchor',sec['following_gain_clip_anchor']['h']=='0x000CD440' and by[0xCD440]['body_size']==86)
check('all nine named steering residuals closed',d['static_conclusion']['all_9_named_steering_residuals_closed'])
check('replacement boundary is explicit','not reintroduced' in d['static_conclusion']['boundary'])
print(f'\nResults: {p} passed, {f} failed');raise SystemExit(1 if f else 0)
