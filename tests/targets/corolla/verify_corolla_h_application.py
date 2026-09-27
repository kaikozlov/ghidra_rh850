#!/usr/bin/env python3
"""Portable Corolla H application-surface pins: callback tables, diagnostics diff, interrupt bodies/vectors, transport residue. Builder regen lives in verify_corolla_h_regen.py.

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

def _section_application_callback_tables():
    print('== application callback tables ==')
    import json
    ROOT=REPO_ROOT;ART=ROOT/'data/generated/corolla_8965H1202000_application_callback_tables.json';SRAW=ROOT/'firmware/RH850_P1M-E_CodeFlash.bin';HRAW=ROOT/'community/albinoelephant/raw-20260818/albinoelephant-corolla-2023.20260814-0023/dump_codeflash_00000000_00200000_20260814-025814.bin'
    d=json.loads(ART.read_text());S=SRAW.read_bytes();H=HRAW.read_bytes()[:0x100000]
    check('image hashes pinned',d['images']['sienna_sha256']==sha(S) and d['images']['h_sha256']==sha(H))
    c=d['command_table'];check('command tables are 18 entries',c['count']==18 and len(c['rows'])==18)
    check('command-0 target anchor is unique raw pointer at H table base',c['anchor']['target']=='0x0007BD6C' and c['anchor']['h_pointer_occurrences']==['0x00022A74'])
    check('H command table exact targets pinned',[r['h_target'] for r in c['rows']]==['0x0007BD6C','0x0007BD7E','0x0007BDDE','0x0007BDB2','0x0007BF72','0x0007BE2A','0x0007B30E','0x0007B3D4','0x0007BB90','0x0007B7C8','0x0007B820','0x0007B926','0x0007B9E6','0x0007BAC4','0x0007BC6C','0x0007BCAA','0x0007BC20','0x0007BCDE'])
    check('17 named command IDs recovered',d['static_conclusion']['command_roles_recovered']==17 and sum('application_command_' in x['reference_name'] for x in d['role_closure'])==17)
    o=d['async_operation_table'];check('canonical operation discriminators F3..FB',o['canonical_discriminators']==[f'0x{x:04X}' for x in range(0x6F3,0x6FC)])
    check('H removes exactly F4/F5',o['removed_discriminators']==['0x06F4','0x06F5'] and o['h_discriminators']==['0x06F3','0x06F6','0x06F7','0x06F8','0x06F9','0x06FA','0x06FB'])
    check('operation H callback pairs pinned',[(x['discriminator'],x['h']['start'],x['h']['completion']) for x in o['rows'] if x['status']=='preserved']==[('0x06F3','0x000307C2','0x000307E8'),('0x06F6','0x000307F6','0x00030842'),('0x06F7','0x0003089E','0x00030934'),('0x06F8','0x00030994','0x00030A52'),('0x06F9','0x00030AA6','0x00030ADC'),('0x06FA','0x00030AEE','0x00030B14'),('0x06FB','0x00030B22','0x00030B54'),('special-op9','0x00030B64','0x00030B7E')])
    check('16 operation roles recovered and four removed',d['static_conclusion']['operation_roles_recovered']==16 and d['surface_recensus_count']==4)
    check('33 direct roles + 4 recensuses close 37 names',d['role_closure_count']==33 and d['surface_recensus_count']==4)
    check('all direct role targets are raw-config evidence',set(x['target_entry'] for x in d['role_closure'])<=set(d['target_evidence_entries']))


def _section_application_diagnostics():
    print('== application diagnostics ==')
    """Verify the target-native 8965H1202000 application diagnostics comparison."""

    import json

    REPO = REPO_ROOT
    ARTIFACT = REPO / "data/generated/corolla_8965H1202000_application_diagnostics_diff.json"
    EVIDENCE = REPO / "data/generated/corolla_8965H1202000_application_diagnostic_decompiler_evidence.json"



    print("== deterministic application-diagnostics diff ==")
    d = json.loads(ARTIFACT.read_text())
    e = json.loads(EVIDENCE.read_text())

    print("\n== service and RDBI generation ==")
    svc = d["application_service_objects"]
    check("H 17-SID service table relocates to 0x25B38", svc["corolla_h_base"] == "0x25B38")
    check("service-object semantic policy shape is unchanged", svc["semantic_policy_shape_same"])
    check("all 17 primary service security counts remain zero", all(row["security_count"] == 0 for row in svc["corolla_h"]))

    r = d["readable_dids"]
    check("readable DID count shrinks 242 -> 226", (r["sienna_count"], r["corolla_h_count"]) == (242, 226))
    check("H DID table is 0x28F34", r["corolla_h_base"] == "0x28F34")
    check("exact 16-DID 1CF4..1D03 block is removed",
          r["removed"] == [f"0x{x:04X}" for x in range(0x1CF4, 0x1D04)])
    check("H adds no readable DIDs", r["added"] == [])
    check("F181 is the only declared-width change and grows 17 -> 33",
          r["declared_length_changes"] == [{"did": "0xF181", "sienna": 17, "corolla_h": 33}])
    check("H F181 target-native evidence is the two-record response",
          r["f181"]["corolla_h_declared_length"] == 33 and "two 16-byte software-ID records" in r["f181"]["corolla_h_semantics"])

    print("\n== exhaustive H RDBI emitted-write audit ==")
    audit = r["corolla_h_rdbi_output_audit"]
    check("all 180 unique H RDBI producers are classified", audit["unique_producer_count"] == 180)
    check("no non-stub H RDBI producer underwrites", audit["nonstub_underwrite_producer_count"] == 0)
    check("no H RDBI producer overruns", audit["overrun_producer_count"] == 0)
    check("H has exactly 32 stale-response DIDs", audit["stale_response_did_count"] == 32)
    check("all H stale DIDs are explained by exact success stubs",
          all(row["classification"] == "success_stub" for row in audit["producers"] if row["write_relation"] == "underwrite"))
    comparison = r["stale_response_comparison"]
    check("19 Sienna stale DIDs remain stale on H", len(comparison["shared"]) == 19)
    check("29 Sienna stale DIDs are fixed or removed on H", len(comparison["sienna_stale_fixed_or_removed_on_h"]) == 29)
    check("13 H stale DIDs are new relative to Sienna", len(comparison["new_h_stale_vs_sienna"]) == 13)

    print("\n== RoutineControl configuration and target behavior ==")
    rc = d["routine_control"]
    check("H keeps the exact 19-RID sequence", len(rc["rid_sequence"]) == 19 and rc["rid_sequence"][0] == "0x1000" and rc["rid_sequence"][-1] == "0x110D")
    check("decoded policy/session/control-type/width configuration is identical", rc["decoded_policy_support_and_widths_identical"])
    check("H 110A/110C/110D are exact no-op precondition+action pairs",
          rc["corolla_h_noop_precondition_and_action_rids"] == ["0x110A", "0x110C", "0x110D"])
    check("H 110B is documented as newly active lifecycle state", "FEBEB32C" in rc["material_semantic_differences"]["0x110B"] and "0x1C" in rc["material_semantic_differences"]["0x110B"])
    check("H 1009 action change is pinned", "directly starts" in rc["material_semantic_differences"]["0x1009"])
    check("H 1106 lower lifecycle family remains active", "structurally matched" in rc["material_semantic_differences"]["0x1106"])

    print("\n== compact target-native evidence binding ==")
    check("evidence is bound to H software ID", e["software_id"] == "8965H1202000")
    check("evidence selects all 180 RDBI producer functions", e["selection"]["rdbi_producer_count"] == 180)
    check("evidence selects all 35 nonzero RoutineControl callbacks", e["selection"]["routine_control_callback_count"] == 35)


def _section_application_interrupt_bodies():
    print('== application interrupt bodies ==')
    import json
    ROOT=REPO_ROOT;ART=ROOT/'data/generated/corolla_8965H1202000_application_interrupt_bodies.json';EVID=ROOT/'data/generated/corolla_8965H1202000_application_interrupt_body_decompiler_evidence.json';HRAW=ROOT/'community/albinoelephant/raw-20260818/albinoelephant-corolla-2023.20260814-0023/dump_codeflash_00000000_00200000_20260814-025814.bin';p=f=0
    d=json.loads(ART.read_text());e=json.loads(EVID.read_text());h=HRAW.read_bytes()[:0x100000]
    check('seven evidence bodies raw-bound',len(e['functions'])==7 and all(sha(h[int(r['entry'],16):int(r['entry'],16)+r['body_size']])==r['body_sha256'] for r in e['functions']))
    exp={'application_tauj0_ch0_body':'0x0005F258','application_tauj0_ch1_body':'0x0005F294','application_tauj0_ch2_body':'0x0005F2D0','application_can1_rx_interrupt_body':'0x0007D240','application_can1_tx_interrupt_body':'0x0007EB4E'}
    check('five body roles exact',{x['reference_name']:x['target_entry'] for x in d['role_closure']}==exp)
    chains={x['reference_name']:x['chain'] for x in d['rows']}
    check('TAUJ bodies are direct wrapper children',chains['application_tauj0_ch0_body']==['0x0006A6C0','0x0005F258'] and chains['application_tauj0_ch1_body']==['0x0006A76A','0x0005F294'] and chains['application_tauj0_ch2_body']==['0x0006A816','0x0005F2D0'])
    check('CAN1 bodies use one-hop thunks',chains['application_can1_rx_interrupt_body']==['0x0005F3AA','0x0005FB1E','0x0007D240'] and chains['application_can1_tx_interrupt_body']==['0x0005F368','0x0005FB12','0x0007EB4E'])


def _section_application_interrupt_vectors():
    print('== application interrupt vectors ==')
    import json
    ROOT=REPO_ROOT;ART=ROOT/'data/generated/corolla_8965H1202000_application_interrupt_vectors.json';p=f=0
    d=json.loads(ART.read_text());check('EIINT table is 384 entries at 20200',d['table']['base']=='0x00020200' and d['table']['count']==384)
    exp={8:'0x0006ADF4',133:'0x0006A6C0',134:'0x0006A76A',135:'0x0006A816',187:'0x0005F3AA',188:'0x0005F368',379:'0x0005F470'}
    check('seven channel targets exact',{x['channel']:x['h_target'] for x in d['rows']}==exp)
    check('all seven roles recovered',d['role_closure_count']==7 and d['static_conclusion']['seven_unresolved_wrappers_recovered'])
    check('target evidence is exactly vector entries',set(d['target_evidence_entries'])==set(exp.values()))


def _section_application_transport_residue():
    print('== application transport residue ==')
    import json
    ROOT=REPO_ROOT;ART=ROOT/'data/generated/corolla_8965H1202000_application_transport_residue.json';HRAW=ROOT/'community/albinoelephant/raw-20260818/albinoelephant-corolla-2023.20260814-0023/dump_codeflash_00000000_00200000_20260814-025814.bin';HEV=ROOT/'data/generated/corolla_8965H1202000_application_transport_decompiler_evidence.json'
    d=json.loads(ART.read_text());h=HRAW.read_bytes()[:0x100000];ev=json.loads(HEV.read_text())
    check('H evidence image hash pinned',ev['image']['codeflash_sha256']==sha(h))
    check('five H evidence bodies raw-bound',all(sha(h[int(r['entry'],16):int(r['entry'],16)+r['body_size']])==r['body_sha256'] for r in ev['functions']))
    check('normal Rx table shrinks 47 to 40',d['rx_configuration']['sienna_count']==47 and d['rx_configuration']['h_count']==40)
    check('2E4 Rx descriptor removed',d['rx_configuration']['can_2e4_removed'])
    check('Tx IDs change exactly',d['tx_configuration']['sienna_ids']==['0x260','0x262','0x351','0x394','0x4A3','0x4C8'] and d['tx_configuration']['h_ids']==['0x030','0x351','0x394','0x4A3','0x4C8'])
    check('260/262 removed',d['tx_configuration']['removed']==['0x260','0x262'])
    check('H 394 remains PDU index 2',d['tx_configuration']['h_394_index']==2 and d['tx_configuration']['h_394_packer']['entry']=='0x00047ADA')
    check('H 394 packer has four direct pack calls and submits index 2',d['tx_configuration']['h_394_packer']['direct_pack_call_count']==4 and d['tx_configuration']['h_394_packer']['submits_pdu_index_2'])
    expected={'application_can_special_rx_demux':'0x0007A382','application_can_normal_rx_demux':'0x0007A402','application_pdu_transmit_router':'0x0007ADC2','application_pdu_rx_router':'0x0007B040','application_pack_can_394':'0x00047ADA'}
    check('five transport roles exact', {x['reference_name']:x['target_entry'] for x in d['role_closure']}==expected)
    check('three generated PDU roles recensused', {x['reference_name'] for x in d['surface_recensus']}=={'application_unpack_can_2e4','application_pack_can_260','application_pack_can_262'})
_section_application_callback_tables()
_section_application_diagnostics()
_section_application_interrupt_bodies()
_section_application_interrupt_vectors()
_section_application_transport_residue()
print(f'\nResults: {passed} passed, {failed} failed')
raise SystemExit(1 if failed else 0)
