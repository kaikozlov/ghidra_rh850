#!/usr/bin/env python3
"""Portable Corolla H storage and adapter pins: storage/NVM, small adapters, and veneer bank.

Domain split; assertions and helpers are carried over verbatim.
"""
from __future__ import annotations

import hashlib

from tools import REPO_ROOT
ROOT = REPO = REPO_ROOT
passed = failed = 0

def sha(data):
    return hashlib.sha256(data).hexdigest()

def check(name, cond, detail=''):
    global passed, failed
    ok = bool(cond)
    passed += int(ok)
    failed += int(not ok)
    suffix = f' ({detail})' if detail else ''
    print(f"[{'PASS' if ok else 'FAIL'}][raw_bytes] {name}{suffix}")


def _section_storage_nvm():
    print('== storage nvm ==')
    """Verify Corolla H storage/NvM role recovery and persistence boundary."""
    import json,struct
    ROOT=REPO_ROOT
    ART=ROOT/'data/generated/corolla_8965H1202000_storage_nvm.json';EV=ROOT/'data/generated/corolla_8965H1202000_storage_nvm_decompiler_evidence.json';DF=ROOT/'data/generated/corolla_2023_albino_dataflash_analysis.json'
    HRAW=ROOT/'community/albinoelephant/raw-20260818/albinoelephant-corolla-2023.20260814-0023/dump_codeflash_00000000_00200000_20260814-025814.bin';SI=ROOT/'firmware/RH850_P1M-E_CodeFlash.bin'
    a=json.loads(ART.read_text());e=json.loads(EV.read_text());df=json.loads(DF.read_text());H=HRAW.read_bytes()[:0x100000];S=SI.read_bytes();by={int(x['entry'],16):x for x in e['functions']}
    print('== deterministic artifact ==')
    print('\n== compact evidence ==')
    check('H codeflash hash pinned',sha(H)==e['image']['codeflash_sha256']==a['images']['h_sha256'])
    check('all raw H bodies validate',all(sha(H[int(x['entry'],16):int(x['entry'],16)+x['body_size']])==x['body_sha256'] for x in e['functions']))
    print('\n== three role mappings ==')
    exp={'0x0004EAD8':'0x0004A534','0x00065C84':'0x0005FFBC','0x00066DB2':'0x000610EA'}
    check('all three storage/NvM roles recovered',a['storage_nvm_role_closure_count']==3 and {x['reference_entry']:x['target_entry'] for x in a['storage_nvm_role_closure']}==exp)
    check('all three retain exact canonical body sizes',[x['reference_body_size'] for x in a['storage_nvm_role_closure']]==[68,84,150] and all(x['reference_body_size']==x['target_body_size'] for x in a['storage_nvm_role_closure']))
    print('\n== DataFlash range protection ==')
    rng=a['dataflash_range_filter'];check('protected range tables are identical',rng['tables_identical'] and [struct.unpack_from('<I',H,0x28EFC+i*4)[0] for i in range(4)]==[0xFF207800,0xFF207FFF,0xFF206C00,0xFF206EFF])
    check('range filter returns 0x5A accept marker',rng['h_accept_marker']==0x5A and '= 0x5a' in by[0x4A534]['decompiled_c'])
    check('object-15 key-field geometry lies inside second protected range',rng['object15_geometry_inside_second_range'])
    check('H range function scans exactly two exclusion entries','while (uVar2 < 2)' in by[0x4A534]['decompiled_c'])
    print('\n== generic NvM restore ==')
    rr=a['restore_request'];check('H and Sienna expose 16 restore objects',rr['h_object_count']==rr['sienna_object_count']==16)
    check('namespace 0x100 dispatches to H restore queue',rr['namespace_dispatch']['0x100']=='0x000610EA' and rr['namespace_0x100_is_restore'])
    check('restore request keeps 0/100/200 namespaces',all(t in by[0x5FFBC]['decompiled_c'] for t in ('uVar3 == 0','uVar3 == 0x100','uVar3 == 0x200')))
    q=a['queue_restore'];check('restore queue writes state 0x11',q['queue_state']==0x11 and q['has_0x11_state_write'])
    check('queue restore accepts object index below 16','DAT_0002a972 <= uVar5' in by[0x610EA]['decompiled_c'] and struct.unpack_from('<H',H,0x2A972)[0]==16)
    check('request-side namespace 0x100 directly calls queue restore',q['request_calls_queue_restore'])
    check('queue restore invokes three-copy worker',q['copies_requested']==3 and q['h_three_copy_worker']=='0x00069D1A' and 'FUN_00069d1a(0x20' in by[0x610EA]['decompiled_c'])
    print('\n== supplied object-15 snapshot boundary ==')
    o=a['object15_snapshot'];src=next(x for x in df['triplicate_objects'] if x['object']==15)
    check('DataFlash snapshot hash pinned',a['images']['dataflash_sha256']==df['dump_sha256'])
    check('object 15 has three invalid copies',o['object']==15 and o['valid_copy_count']==0 and o['copy_validity']==[False,False,False] and src['valid_copy_count']==0)
    check('object-15 copy roots are FF206E00/D00/C00',o['copy_addresses']==['0xFF206E00','0xFF206D00','0xFF206C00'])
    check('known key fields are FF206E14/D14/C14',[o['known_key_field_geometry'][k] for k in ('raw','xor55','xoraa')]==['0xFF206E14','0xFF206D14','0xFF206C14'])
    check('runtime key equivalence remains explicitly unproven',o['known_key_field_geometry']['runtime_key_equivalence']=='unproven')
    check('generic restore does not collapse into command-8 provisioning',a['static_conclusion']['command8_provisioning_remains_separate'] and not a['static_conclusion']['runtime_slot4_key_from_valid_object15_in_supplied_snapshot'])


def _section_small_adapters():
    print('== small adapters ==')
    """Verify generated bounded-API, packet-selector, and record-operation adapter mappings."""
    import json
    ROOT=REPO_ROOT;ART=ROOT/'data/generated/corolla_8965H1202000_small_adapters.json';EV=ROOT/'data/generated/corolla_8965H1202000_small_adapter_decompiler_evidence.json';RAW=ROOT/'community/albinoelephant/raw-20260818/albinoelephant-corolla-2023.20260814-0023/dump_codeflash_00000000_00200000_20260814-025814.bin'
    d=json.loads(ART.read_text());e=json.loads(EV.read_text());raw=RAW.read_bytes()[:0x100000];by={int(r['entry'],16):r for r in e['functions']}
    check('H image hash pinned',sha(raw)==e['image']['codeflash_sha256'])
    check('all raw H bodies validate',all(sha(raw[int(r['entry'],16):int(r['entry'],16)+r['body_size']])==r['body_sha256'] for r in e['functions']))
    check('all 18 roles recovered',d['role_closure_count']==18 and d['static_conclusion']['all_18_roles_recovered'])
    b=d['bounded_api'];check('six bounded wrappers relocate by -0x5C60',b['delta']==-0x5C60 and b['same_wrapper_sizes'])
    check('H bounded pointer table is 21838',b['h_pointer_table']['base']=='0x00021838' and len(b['h_pointer_table']['values'])==6)
    check('all six bounded target slots preserve -0x4FDA relocation',all(int(h,16)-int(s,16)==-0x4FDA for s,h in zip(b['sienna_pointer_table']['values'],b['h_pointer_table']['values'])))
    pkt=d['packet_selector'];check('packet table has same 21 configured selector indices',pkt['configured_selectors_h']==pkt['configured_selectors_sienna'] and len(pkt['configured_selectors_h'])==21)
    check('packet table maps to H 269FC',pkt['h_table_base']=='0x000269FC' and pkt['table_count']==44)
    check('seven residual packet selector targets exact',pkt['mapped_target_checks'] and sorted(pkt['mapped_selectors'])==[6,15,16,22,38,39,43])
    rec=d['record_operation'];check('record table maps 5x0x1C at H 25F28',rec['h_table_base']=='0x00025F28' and rec['record_count']==5 and rec['stride']==28)
    check('five record callback words exact',rec['mapped_target_checks'] and rec['all_h_callbacks_48_bytes'])


def _section_veneer_bank():
    print('== veneer bank ==')
    import json
    ROOT=REPO_ROOT; ART=ROOT/'data/generated/corolla_8965H1202000_veneer_bank.json'; SRAW=ROOT/'firmware/RH850_P1M-E_CodeFlash.bin'; HRAW=ROOT/'community/albinoelephant/raw-20260818/albinoelephant-corolla-2023.20260814-0023/dump_codeflash_00000000_00200000_20260814-025814.bin'
    d=json.loads(ART.read_text());S=SRAW.read_bytes();H=HRAW.read_bytes()[:0x100000]
    check('image hashes pinned',d['images']['sienna_sha256']==sha(S) and d['images']['h_sha256']==sha(H))
    b=d['bank'];check('fixed bank is 60 slots at 0x14 stride',b['slot_count']==60 and b['stride']==0x14 and b['start']=='0x000FDE08' and b['end']=='0x000FE2A4')
    check('veneer cardinality is 44 S / 38 H / 36 common',b['sienna_veneer_count']==44 and b['h_veneer_count']==38 and b['common_veneer_slots']==36)
    check('full-bank removal set pinned',b['removed_slots']==['0x000FE164','0x000FE1B4','0x000FE1C8','0x000FE1F0','0x000FE204','0x000FE218','0x000FE22C','0x000FE2A4'])
    check('full-bank addition set pinned',b['added_slots']==['0x000FE178','0x000FE18C'])
    check('all recorded veneer raw bytes have call/return signature',all((x[side]['kind']!='veneer' or (bytes.fromhex(x[side]['raw8'])[:2]==b'\x2c\x06' and bytes.fromhex(x[side]['raw8'])[6:8]==b'\x6c\x00')) for x in b['slots'] for side in ('sienna','h')))
    pairs=d['unresolved_pair_census'];check('11 canonical unresolved veneer pairs censused',len(pairs)==11)
    check('six preserved and five removed unresolved pairs',d['static_conclusion']['preserved_unresolved_pairs']==6 and d['static_conclusion']['removed_unresolved_pairs']==5)
    check('preserved H target set pinned',[(x['slot'],x['h_target']) for x in pairs if x['status']=='preserved-slot']==[('0x000FDEA8','0x000B6556'),('0x000FE074','0x000B4882'),('0x000FE088','0x000B4886'),('0x000FE0B0','0x000B5364'),('0x000FE1A0','0x000B1F4A'),('0x000FE1DC','0x000B1F5A')])
    check('removed unresolved slots are literal fill',all(bytes.fromhex(x['h_raw8'])==bytes.fromhex('4000400040004000') for x in pairs if x['status']=='removed-slot'))
    check('12 direct roles + 10 recensus rows close 22 names',d['role_closure_count']==12 and d['surface_recensus_count']==10 and d['role_closure_count']+d['surface_recensus_count']==22)
    check('role targets are represented by raw veneer evidence',set(x['target_entry'] for x in d['role_closure']) <= set(d['target_evidence_entries']))
_section_storage_nvm()
_section_small_adapters()
_section_veneer_bank()
print(f'\nResults: {passed} passed, {failed} failed')
raise SystemExit(1 if failed else 0)
