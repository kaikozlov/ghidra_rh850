#!/usr/bin/env python3
"""Portable Corolla H monitor pins: COM deadline-monitor dispatch surface, plausibility monitor, and power-supply monitor gate.

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


def _section_deadline_monitor_surface():
    print('== deadline monitor surface ==')
    """Verify complete target-surface closure of Corolla-H deadline-monitor callbacks."""
    import json
    ROOT=REPO_ROOT;ART=ROOT/'data/generated/corolla_8965H1202000_deadline_monitor_surface.json';EV=ROOT/'data/generated/corolla_8965H1202000_deadline_monitor_surface_decompiler_evidence.json';RAW=ROOT/'community/albinoelephant/raw-20260818/albinoelephant-corolla-2023.20260814-0023/dump_codeflash_00000000_00200000_20260814-025814.bin'
    d=json.loads(ART.read_text());e=json.loads(EV.read_text());raw=RAW.read_bytes()[:0x100000]
    check('H image hash pinned',sha(raw)==e['image']['codeflash_sha256'])
    check('all raw H bodies validate',all(sha(raw[int(r['entry'],16):int(r['entry'],16)+r['body_size']])==r['body_sha256'] for r in e['functions']))
    check('simple dispatcher maps 6962A->639CA at 138 bytes',d['dispatchers']['simple']=={'sienna':'0x0006962A','h':'0x000639CA','body_size':138,'unique_exact_instruction_shape':True})
    check('variant-D dispatcher maps 6A28A->6462A at 1208 bytes',d['dispatchers']['variant_d']=={'sienna':'0x0006A28A','h':'0x0006462A','body_size':1208,'unique_exact_instruction_shape':True})
    check('simple setup maps to H 387E4 and table 280E8',d['dispatchers']['simple_setup']['h']=='0x000387E4' and d['dispatchers']['simple_setup']['h_table']=='0x000280E8')
    ht={x['name']:x for x in d['h_tables']};st={x['name']:x for x in d['sienna_tables']}
    check('H variant-D A table base 280B4',ht['variant_d_a']['base']=='0x000280B4')
    check('H simple table base 280E8',ht['simple']['base']=='0x000280E8')
    check('H variant-D B table base 28260',ht['variant_d_b']['base']=='0x00028260')
    check('S/H table row/stride shapes are identical',d['summary']['same_table_shapes'])
    check('S/H per-table unique callback counts are 3/82/3',d['summary']['same_per_table_unique_counts'] and [ht[x]['unique_callbacks'] for x in ('variant_d_a','simple','variant_d_b')]==[3,82,3])
    check('H simple table has 83 nonzero slots / 82 unique',ht['simple']['nonzero_slots']==83 and ht['simple']['unique_callbacks']==82)
    check('H variant A has 3 nonzero / 3 unique',ht['variant_d_a']['nonzero_slots']==3 and ht['variant_d_a']['unique_callbacks']==3)
    check('H variant B has 4 nonzero / 3 unique',ht['variant_d_b']['nonzero_slots']==4 and ht['variant_d_b']['unique_callbacks']==3)
    check('both images have 88-callback union',d['summary']['sienna_unique_callback_union']==88==d['summary']['h_unique_callback_union'])
    check('simple final row preserves duplicate-start/null-third shape',ht['simple']['rows'][-1][0]==ht['simple']['rows'][-1][1] and ht['simple']['rows'][-1][2] is None)
    check('all 88 canonical deadline names are recensused',d['surface_recensus_count']==88 and d['summary']['all_88_named_deadline_residuals_closed'])



def _section_plausibility_monitor():
    print('== plausibility monitor ==')
    """Verify the target-native nine-channel plausibility-monitor mapping."""
    import json
    ROOT=REPO_ROOT;ART=ROOT/'data/generated/corolla_8965H1202000_plausibility_monitor.json';EV=ROOT/'data/generated/corolla_8965H1202000_plausibility_monitor_decompiler_evidence.json';RAW=ROOT/'community/albinoelephant/raw-20260818/albinoelephant-corolla-2023.20260814-0023/dump_codeflash_00000000_00200000_20260814-025814.bin'
    d=json.loads(ART.read_text());e=json.loads(EV.read_text());raw=RAW.read_bytes()[:0x100000];by={int(r['entry'],16):r for r in e['functions']}
    check('H image hash pinned',sha(raw)==e['image']['codeflash_sha256'])
    check('all raw H bodies validate',all(sha(raw[int(r['entry'],16):int(r['entry'],16)+r['body_size']])==r['body_sha256'] for r in e['functions']))
    check('all 11 named roles recovered',d['role_closure_count']==11 and d['static_conclusion']['all_11_roles_recovered'])
    check('nine channels mapped',len(d['channels'])==9)
    check('all channel tables shift by -0x470',d['static_conclusion']['all_channel_table_deltas_minus_0x470'] and all(c['table_delta']==-0x470 for c in d['channels']))
    check('status permutation preserved',d['status_index_order']==[7,8,3,4,0,1,2,5,6] and d['static_conclusion']['status_index_permutation_preserved'])
    check('each H channel calls common status publisher',all('FUN_0003eccc' in by[int(c['h'],16)]['decompiled_c'] for c in d['channels']))
    check('publisher maps to H 3ECCC',d['publisher']['h']=='0x0003ECCC' and d['publisher']['both_body_size_18'] and d['publisher']['h_bound']==9)
    check('H publisher vector base is FEBE76EC','febe76ec' in by[0x3ECCC]['decompiled_c'].lower())
    check('aggregate maps 436->484',d['aggregate']['size_change']==[436,484] and d['aggregate']['h']=='0x0003EAE8')
    check('H aggregate adds status publication',d['aggregate']['h_adds_status_publication'] and 'FUN_00047484(1,' in by[0x3EAE8]['decompiled_c'])
    check('owner group-B ordering preserved',d['owner_dispatch']['h']=='0x00058450' and d['owner_dispatch']['channel_call_order_h']==['0x0003E5DC','0x0003E7CC','0x0003E87A','0x0003E27C','0x0003E42C','0x0003E928','0x0003EA16','0x0003E118','0x0003E1CA','0x0003EAE8'])



def _section_power_supply_monitor_gate():
    print('== power supply monitor gate ==')
    """Verify the exact H/F FEBE7C58 -> FEBEF000 -> FEBEACBD monitor contract."""

    import json

    REPO = REPO_ROOT
    RAW = REPO / "community/albinoelephant/normalized/8965H1202000_CodeFlash.bin"
    EVID = REPO / "data/generated/corolla_8965H1202000_power_supply_monitor_decompiler_evidence.json"
    ART = REPO / "data/generated/corolla_8965H1202000_power_supply_monitor_gate.json"


    raw = RAW.read_bytes()
    ev = json.loads(EVID.read_text())
    art = json.loads(ART.read_text())

    print("\n== source binding ==")
    check("exact H image", len(raw) == 0x100000 and sha(raw) == art["sources"]["codeflash"]["sha256"] == "0b47bdc1217835c839e3543e52eab40eb793650a9c159e46f6a9b365ea41a67f")
    check("all compact function bodies raw-bound", all(sha(raw[int(row["entry"], 16):int(row["entry"], 16) + row["body_size"]]) == row["body_sha256"] for row in ev["functions"]))
    check("H/F application transfer exact", art["applies_to"] == ["8965H1202000", "8965F1208000"] and art["sources"]["hf_application_equivalence"]["region"]["identical"] is True and art["sources"]["hf_application_equivalence"]["region"]["different_bytes"] == 0)

    print("\n== exact state chain ==")
    chain = art["state_chain"]
    check("native to scheduler snapshot exact", chain["native_state"] == "0xFEBE7C58" and chain["snapshot_copy"] == {"entry": "0x0005262C", "destination": "0xFEBEF000"})
    check("B8EE4 normalization body exact", chain["normalizer"] == {"entry": "0x000B8EE4", "tracked_body_continuation": "0x000B8EEC"} and chain["normalized_output"] == "0xFEBEACBD")
    check("normalization mapping exact", chain["mapping"] == {"0": 0, "2": 2, "3": 4, "other_nonzero": 1})
    check("fixed-GP arithmetic exact", chain["exact_fixed_gp_arithmetic"] == {"gp": "0xFEBEB800", "native": "GP-0x3BA8", "snapshot": "GP+0x3800", "normalized": "GP-0x0B43"})
    check("direct census counts pinned", {key: value["match_count"] for key, value in chain["direct_text_reference_census"].items()} == {"native_state": 47, "normalized_state": 21, "snapshot_state": 31})

    print("\n== three power-supply monitors ==")
    dispatch = art["monitor_dispatch"]
    check("three configured channels active", dispatch["entry"] == "0x000450FC" and dispatch["feature_bytes"]["address"] == "0x0002B864" and dispatch["feature_bytes"]["raw_hex"] == raw[0x2B864:0x2B867].hex() == "000000")
    check("three monitor/classifier pairs exact", [(row["monitor"], row["classifier"]) for row in dispatch["channels"]] == [("0x00044D84", "0x0004516A"), ("0x00044EC2", "0x000451C4"), ("0x00044FC4", "0x00045212")])
    check("combined, A6, and A8 input sets exact", [row["supply_inputs"] for row in dispatch["channels"]] == [["0xFEBE63B0", "0xFEBE63A6", "0xFEBE63A8"], ["0xFEBE63B0", "0xFEBE63A6"], ["0xFEBE63B0", "0xFEBE63A8"]])
    check("shared state writers exact", dispatch["shared_state_writes"] == {"0": "0x00045268", "1": "0x00045260", "2": "0x00045272", "3": ["0x0004527A", "0x0004528A", "0x0004529A"]})
    check("raw calibration bytes exact", dispatch["calibration"]["address"] == "0x0002B69A" and dispatch["calibration"]["raw_hex"] == raw[0x2B69A:0x2B6B6].hex() == "00100009001000090500c8000000c8000500c80000000500c8000000")

    print("\n== diagnostic join and boundaries ==")
    join = art["diagnostic_input_join"]
    check("IG supply cell exact", join["0xFEBE63B0"]["producer"] == "0x000488E6" and {x["name"] for x in join["0xFEBE63B0"]["rows"]} == {"IG Power Supply", "IG Power Supply (System 2)"})
    check("A6 retains both supported OEM labels", join["0xFEBE63A6"]["producers"] == ["0x00048918", "0x00048CFC"] and {x["name"] for x in join["0xFEBE63A6"]["rows"]} == {"PIG Power Supply", "PIG Power Supply (System 2)", "Motor 1 Power Supply"})
    check("A8 motor-2 supply cell exact", join["0xFEBE63A8"]["producer"] == "0x00048E90" and join["0xFEBE63A8"]["rows"] == [{"did": "0x10FA", "name": "Motor 2 Power Supply"}])
    classification = art["classification"]
    check("state classified as graded receive-validity/freeze gate", "power-supply receive-validity/freeze state" in classification["recovered"] and "scheduler snapshot" in classification["recovered"] and "normalized downstream gate" in classification["recovered"])
    check("B6 loss remains separate", classification["distinct_from_b6_loss"] == "B6 missing-message loss remains the separate FEBEADB9 -> FEBEC26D path.")
_section_deadline_monitor_surface()
_section_plausibility_monitor()
_section_power_supply_monitor_gate()
print(f'\nResults: {passed} passed, {failed} failed')
raise SystemExit(1 if failed else 0)
