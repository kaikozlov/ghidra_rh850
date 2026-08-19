#!/usr/bin/env python3
"""Verify Corolla H storage/NvM role recovery and persistence boundary."""
from __future__ import annotations
import hashlib,json,struct,subprocess,sys,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
ART=ROOT/'data/generated/corolla_8965H1202000_storage_nvm.json';EV=ROOT/'data/generated/corolla_8965H1202000_storage_nvm_decompiler_evidence.json';BUILD=ROOT/'tools/build_corolla_h_storage_nvm.py';DF=ROOT/'data/generated/corolla_2023_albino_dataflash_analysis.json'
HRAW=ROOT/'community/albinoelephant/raw-20260818/albinoelephant-corolla-2023.20260814-0023/dump_codeflash_00000000_00200000_20260814-025814.bin';SI=ROOT/'firmware/RH850_P1M-E_CodeFlash.bin'
p=f=0
def sha(b):return hashlib.sha256(b).hexdigest()
def ck(n,c,d=''):
 global p,f
 ok=bool(c);p+=ok;f+=not ok;print(f"[{'PASS' if ok else 'FAIL'}][raw_bytes] {n}"+(f' ({d})' if d else ''))
a=json.loads(ART.read_text());e=json.loads(EV.read_text());df=json.loads(DF.read_text());H=HRAW.read_bytes()[:0x100000];S=SI.read_bytes();by={int(x['entry'],16):x for x in e['functions']}
print('== deterministic artifact ==')
with tempfile.TemporaryDirectory() as td:
 out=Path(td)/'x.json';r=subprocess.run([sys.executable,str(BUILD),'--out',str(out)],cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
 ck('builder exits',r.returncode==0,r.stdout[-400:] if r.returncode else '');ck('report regenerates exactly',r.returncode==0 and out.read_bytes()==ART.read_bytes())
print('\n== compact evidence ==')
ck('H codeflash hash pinned',sha(H)==e['image']['codeflash_sha256']==a['images']['h_sha256']);ck('three H functions compacted',e['function_count']==3==len(e['functions']))
ck('all raw H bodies validate',all(sha(H[int(x['entry'],16):int(x['entry'],16)+x['body_size']])==x['body_sha256'] for x in e['functions']))
ck('all H decompiler hashes validate',all(sha(x['decompiled_c'].encode())==x['decompiled_c_sha256'] for x in e['functions']))
print('\n== three role mappings ==')
exp={'0x0004EAD8':'0x0004A534','0x00065C84':'0x0005FFBC','0x00066DB2':'0x000610EA'}
ck('all three storage/NvM roles recovered',a['storage_nvm_role_closure_count']==3 and {x['reference_entry']:x['target_entry'] for x in a['storage_nvm_role_closure']}==exp)
ck('all three retain exact canonical body sizes',[x['reference_body_size'] for x in a['storage_nvm_role_closure']]==[68,84,150] and all(x['reference_body_size']==x['target_body_size'] for x in a['storage_nvm_role_closure']))
print('\n== DataFlash range protection ==')
rng=a['dataflash_range_filter'];ck('protected range tables are identical',rng['tables_identical'] and [struct.unpack_from('<I',H,0x28EFC+i*4)[0] for i in range(4)]==[0xFF207800,0xFF207FFF,0xFF206C00,0xFF206EFF])
ck('range filter returns 0x5A accept marker',rng['h_accept_marker']==0x5A and '= 0x5a' in by[0x4A534]['decompiled_c'])
ck('object-15 key-field geometry lies inside second protected range',rng['object15_geometry_inside_second_range'])
ck('H range function scans exactly two exclusion entries','while (uVar2 < 2)' in by[0x4A534]['decompiled_c'])
print('\n== generic NvM restore ==')
rr=a['restore_request'];ck('H and Sienna expose 16 restore objects',rr['h_object_count']==rr['sienna_object_count']==16)
ck('namespace 0x100 dispatches to H restore queue',rr['namespace_dispatch']['0x100']=='0x000610EA' and rr['namespace_0x100_is_restore'])
ck('restore request keeps 0/100/200 namespaces',all(t in by[0x5FFBC]['decompiled_c'] for t in ('uVar3 == 0','uVar3 == 0x100','uVar3 == 0x200')))
q=a['queue_restore'];ck('restore queue writes state 0x11',q['queue_state']==0x11 and q['has_0x11_state_write'])
ck('queue restore accepts object index below 16','DAT_0002a972 <= uVar5' in by[0x610EA]['decompiled_c'] and struct.unpack_from('<H',H,0x2A972)[0]==16)
ck('request-side namespace 0x100 directly calls queue restore',q['request_calls_queue_restore'])
ck('queue restore invokes three-copy worker',q['copies_requested']==3 and q['h_three_copy_worker']=='0x00069D1A' and 'FUN_00069d1a(0x20' in by[0x610EA]['decompiled_c'])
print('\n== supplied object-15 snapshot boundary ==')
o=a['object15_snapshot'];src=next(x for x in df['triplicate_objects'] if x['object']==15)
ck('DataFlash snapshot hash pinned',a['images']['dataflash_sha256']==df['dump_sha256'])
ck('object 15 has three invalid copies',o['object']==15 and o['valid_copy_count']==0 and o['copy_validity']==[False,False,False] and src['valid_copy_count']==0)
ck('object-15 copy roots are FF206E00/D00/C00',o['copy_addresses']==['0xFF206E00','0xFF206D00','0xFF206C00'])
ck('known key fields are FF206E14/D14/C14',[o['known_key_field_geometry'][k] for k in ('raw','xor55','xoraa')]==['0xFF206E14','0xFF206D14','0xFF206C14'])
ck('runtime key equivalence remains explicitly unproven',o['known_key_field_geometry']['runtime_key_equivalence']=='unproven')
ck('generic restore does not collapse into command-8 provisioning',a['static_conclusion']['command8_provisioning_remains_separate'] and not a['static_conclusion']['runtime_slot4_key_from_valid_object15_in_supplied_snapshot'])
print(f'\nResults: {p} passed, {f} failed');raise SystemExit(1 if f else 0)
