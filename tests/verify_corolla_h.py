#!/usr/bin/env python3
"""Portable Corolla H artifact pins. Builder regen lives in verify_corolla_h_regen.py."""
from __future__ import annotations

import hashlib
import json
import struct
from pathlib import Path

ROOT = REPO = Path(__file__).resolve().parents[1]
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
    import hashlib,json
    from pathlib import Path
    ROOT=Path(__file__).resolve().parents[1];ART=ROOT/'data/generated/corolla_8965H1202000_application_callback_tables.json';TOOL=ROOT/'tools/build_corolla_h_application_callback_tables.py';SRAW=ROOT/'firmware/RH850_P1M-E_CodeFlash.bin';HRAW=ROOT/'community/albinoelephant/raw-20260818/albinoelephant-corolla-2023.20260814-0023/dump_codeflash_00000000_00200000_20260814-025814.bin'
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
    check('missing-row boundary explicit','does not prove' in d['static_conclusion']['boundary'])


def _section_application_diagnostics():
    print('== application diagnostics ==')
    """Verify the target-native 8965H1202000 application diagnostics comparison."""

    import json
    from pathlib import Path

    REPO = Path(__file__).resolve().parents[1]
    ARTIFACT = REPO / "data/generated/corolla_8965H1202000_application_diagnostics_diff.json"
    EVIDENCE = REPO / "data/generated/corolla_8965H1202000_application_diagnostic_decompiler_evidence.json"
    TOOL = REPO / "tools/compare_variant_application_diagnostics.py"



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
    check("evidence set stays compact", e["selection"]["function_count"] == 240)


def _section_application_interrupt_bodies():
    print('== application interrupt bodies ==')
    import hashlib,json
    from pathlib import Path
    ROOT=Path(__file__).resolve().parents[1];ART=ROOT/'data/generated/corolla_8965H1202000_application_interrupt_bodies.json';TOOL=ROOT/'tools/build_corolla_h_application_interrupt_bodies.py';EVID=ROOT/'data/generated/corolla_8965H1202000_application_interrupt_body_decompiler_evidence.json';HRAW=ROOT/'community/albinoelephant/raw-20260818/albinoelephant-corolla-2023.20260814-0023/dump_codeflash_00000000_00200000_20260814-025814.bin';p=f=0
    d=json.loads(ART.read_text());e=json.loads(EVID.read_text());h=HRAW.read_bytes()[:0x100000]
    check('seven evidence bodies raw-bound',len(e['functions'])==7 and all(sha(h[int(r['entry'],16):int(r['entry'],16)+r['body_size']])==r['body_sha256'] for r in e['functions']))
    exp={'application_tauj0_ch0_body':'0x0005F258','application_tauj0_ch1_body':'0x0005F294','application_tauj0_ch2_body':'0x0005F2D0','application_can1_rx_interrupt_body':'0x0007D240','application_can1_tx_interrupt_body':'0x0007EB4E'}
    check('five body roles exact',{x['reference_name']:x['target_entry'] for x in d['role_closure']}==exp)
    chains={x['reference_name']:x['chain'] for x in d['rows']}
    check('TAUJ bodies are direct wrapper children',chains['application_tauj0_ch0_body']==['0x0006A6C0','0x0005F258'] and chains['application_tauj0_ch1_body']==['0x0006A76A','0x0005F294'] and chains['application_tauj0_ch2_body']==['0x0006A816','0x0005F2D0'])
    check('CAN1 bodies use one-hop thunks',chains['application_can1_rx_interrupt_body']==['0x0005F3AA','0x0005FB1E','0x0007D240'] and chains['application_can1_tx_interrupt_body']==['0x0005F368','0x0005FB12','0x0007EB4E'])
    check('semantic boundary explicit','Deeper timer/ADC semantics are not transferred' in d['static_conclusion']['boundary'])


def _section_application_interrupt_vectors():
    print('== application interrupt vectors ==')
    import json
    from pathlib import Path
    ROOT=Path(__file__).resolve().parents[1];ART=ROOT/'data/generated/corolla_8965H1202000_application_interrupt_vectors.json';TOOL=ROOT/'tools/build_corolla_h_application_interrupt_vectors.py';p=f=0
    d=json.loads(ART.read_text());check('EIINT table is 384 entries at 20200',d['table']['base']=='0x00020200' and d['table']['count']==384)
    exp={8:'0x0006ADF4',133:'0x0006A6C0',134:'0x0006A76A',135:'0x0006A816',187:'0x0005F3AA',188:'0x0005F368',379:'0x0005F470'}
    check('seven channel targets exact',{x['channel']:x['h_target'] for x in d['rows']}==exp)
    check('all seven roles recovered',d['role_closure_count']==7 and d['static_conclusion']['seven_unresolved_wrappers_recovered'])
    check('target evidence is exactly vector entries',set(d['target_evidence_entries'])==set(exp.values()))
    check('internal semantic boundary explicit','internals' in d['static_conclusion']['boundary'])


def _section_application_transport_residue():
    print('== application transport residue ==')
    import hashlib,json
    from pathlib import Path
    ROOT=Path(__file__).resolve().parents[1];ART=ROOT/'data/generated/corolla_8965H1202000_application_transport_residue.json';TOOL=ROOT/'tools/build_corolla_h_application_transport_residue.py';HRAW=ROOT/'community/albinoelephant/raw-20260818/albinoelephant-corolla-2023.20260814-0023/dump_codeflash_00000000_00200000_20260814-025814.bin';HEV=ROOT/'data/generated/corolla_8965H1202000_application_transport_decompiler_evidence.json'
    d=json.loads(ART.read_text());h=HRAW.read_bytes()[:0x100000];ev=json.loads(HEV.read_text())
    check('H evidence image hash pinned',ev['image']['codeflash_sha256']==sha(h))
    check('five H evidence bodies raw-bound',all(sha(h[int(r['entry'],16):int(r['entry'],16)+r['body_size']])==r['body_sha256'] and sha(r['decompiled_c'].encode())==r['decompiled_c_sha256'] for r in ev['functions']))
    check('normal Rx table shrinks 47 to 40',d['rx_configuration']['sienna_count']==47 and d['rx_configuration']['h_count']==40)
    check('2E4 Rx descriptor removed',d['rx_configuration']['can_2e4_removed'])
    check('Tx IDs change exactly',d['tx_configuration']['sienna_ids']==['0x260','0x262','0x351','0x394','0x4A3','0x4C8'] and d['tx_configuration']['h_ids']==['0x030','0x351','0x394','0x4A3','0x4C8'])
    check('260/262 removed',d['tx_configuration']['removed']==['0x260','0x262'])
    check('H 394 remains PDU index 2',d['tx_configuration']['h_394_index']==2 and d['tx_configuration']['h_394_packer']['entry']=='0x00047ADA')
    check('H 394 packer has four direct pack calls and submits index 2',d['tx_configuration']['h_394_packer']['direct_pack_call_count']==4 and d['tx_configuration']['h_394_packer']['submits_pdu_index_2'])
    expected={'application_can_special_rx_demux':'0x0007A382','application_can_normal_rx_demux':'0x0007A402','application_pdu_transmit_router':'0x0007ADC2','application_pdu_rx_router':'0x0007B040','application_pack_can_394':'0x00047ADA'}
    check('five transport roles exact', {x['reference_name']:x['target_entry'] for x in d['role_closure']}==expected)
    check('three generated PDU roles recensused', {x['reference_name'] for x in d['surface_recensus']}=={'application_unpack_can_2e4','application_pack_can_260','application_pack_can_262'})
    check('target-specific field boundary explicit','field identity is not transferred' in d['static_conclusion']['boundary'])


def _section_b6_full_receiver_contract():
    print('== b6 full receiver contract ==')
    """Verify the byte/bit-complete H/F protected-0x0B6 receiver contract."""

    import hashlib
    import json
    import struct
    from pathlib import Path

    REPO = Path(__file__).resolve().parents[1]
    ART = REPO / "data/generated/corolla_8965H1202000_b6_full_receiver_contract.json"
    EVID = REPO / "data/generated/corolla_8965H1202000_b6_full_receiver_decompiler_evidence.json"
    H = REPO / "community/albinoelephant/normalized/8965H1202000_CodeFlash.bin"
    F_RAW = REPO / "community/spanconstant/raw-20260821/span-corolla-2025.20260821-1511/dump_codeflash_00000000_00200000_20260821-152033.bin"
    LTA = REPO / "data/generated/corolla_8965H1202000_lta_command_provenance.json"
    KEYS = REPO / "data/generated/corolla_8965H1202000_secoc_key_provenance.json"
    TOOL = REPO / "tools/build_corolla_h_b6_full_receiver_contract.py"
    EXTRACTOR = REPO / "tools/extract_corolla_h_b6_full_receiver_evidence.py"


    art = json.loads(ART.read_text())
    ev = json.loads(EVID.read_text())
    h = H.read_bytes()
    f = F_RAW.read_bytes()
    lta = json.loads(LTA.read_text())
    keys = json.loads(KEYS.read_text())
    funcs = {int(row["entry"], 16): row for row in ev["functions"]}

    print("\n== exact source and H/F binding ==")
    check("schema exact", art["schema"] == "corolla-8965H1202000-b6-full-receiver-contract-v1")
    check("H image pinned", len(h) == 0x100000 and sha(h) == "0b47bdc1217835c839e3543e52eab40eb793650a9c159e46f6a9b365ea41a67f")
    check("15 promoted SecOC/delivery functions", ev["function_count"] == len(funcs) == 15)
    check("evidence generator source-bound",
          ev["generator"] == {"path": "tools/extract_corolla_h_b6_full_receiver_evidence.py", "sha256": sha(EXTRACTOR.read_bytes())})
    check("whole application corpus source identity pinned",
          ev["source_corpus"]["sha256"] == "5cc79174e8ea917356b9d4758d086df1209c85c9665f122782cff7d88261c387")
    check("all promoted functions raw-bound",
          all(sha(h[a:a + row["body_size"]]) == row["body_sha256"] for a, row in funcs.items()))
    check("H/F application bytes identical", h[0x20000:0x100000] == f[0x20000:0x100000])
    check("H/F contract explicitly shared", art["applies_to"] == ["8965H1202000", "8965F1208000"] and art["cross_variant"]["receiver_contract_byte_identical"] is True)
    check("cross-variant boundary retains low-region calibration caveat", "Low-region" in art["cross_variant"]["boundary"])

    print("\n== raw B6 SecOC profile ==")
    record = h[0x257CC:0x2581C]
    check("B6 record raw exact", len(record) == 0x50 and art["wire_envelope"]["profile_record"]["raw_hex"] == record.hex())
    check("CMAC width is 128/full and 28/transmitted", struct.unpack_from("<H", record, 0)[0] == 128 and struct.unpack_from("<H", record, 2)[0] == 28)
    check("trailer is four bytes", struct.unpack_from("<H", record, 6)[0] == 4)
    check("normal profile and Data ID B6 exact", record[9] == 0 and struct.unpack_from("<H", record, 0xA)[0] == 0xB6)
    check("freshness profile id2, FV46/FV4 exact", struct.unpack_from("<H", record, 0x12)[0] == 2 and record[0x14] == 46 and record[0x15] == 4)
    check("secured lengths all 32", struct.unpack_from("<I", record, 0x24)[0] == struct.unpack_from("<I", record, 0x3C)[0] == struct.unpack_from("<I", record, 0x44)[0] == 32)
    check("application and route PDU both 42", struct.unpack_from("<H", record, 0x34)[0] == struct.unpack_from("<H", record, 0x36)[0] == 42)
    check("freshness callbacks exact", struct.unpack_from("<I", record, 0x30)[0] == 0x89758 and struct.unpack_from("<I", record, 0x48)[0] == 0x896B0)
    check("profile partitions frame 28+4", art["wire_envelope"]["authenticated_application_region"] == {"first_byte": 0, "last_byte": 27, "bytes": 28} and art["wire_envelope"]["security_trailer_region"] == {"first_byte": 28, "last_byte": 31, "bytes": 4})

    print("\n== trailer and freshness arithmetic ==")
    # Synthetic trailer: high B28 nibble is FV4; remaining 28 wire bits are CMAC_MSB28.
    b28, b29, b30, b31 = 0xDA, 0x12, 0x34, 0x56
    fv4 = b28 >> 4
    cmac28 = ((b28 & 0xF) << 24) | (b29 << 16) | (b30 << 8) | b31
    shifted = bytes([((b28 << 4) | (b29 >> 4)) & 0xFF,
                     ((b29 << 4) | (b30 >> 4)) & 0xFF,
                     ((b30 << 4) | (b31 >> 4)) & 0xFF,
                     (b31 << 4) & 0xFF])
    check("B28 high nibble is FV4", fv4 == 0xD)
    check("B28 low nibble plus B29..31 is CMAC28", cmac28 == 0x0A123456)
    check("receiver left-shift reconstructs top-aligned CMAC28", shifted.hex() == "a1234560")
    # Independent reference pack for trip16/reset20/message8/reset-low2/00.
    trip, reset, message = 0x1234, 0x56789, 0xAB
    freshness = struct.pack(">HI", trip, ((reset & 0xFFFFF) << 12) | (message << 4) | ((reset & 3) << 2))
    check("full freshness is six bytes", len(freshness) == 6 and freshness.hex() == "123456789ab4")
    check("46-bit full freshness leaves low two pad bits zero", freshness[-1] & 3 == 0)
    check("transmitted FV4 is message-low2 then reset-low2", ((message & 3) << 2 | (reset & 3)) == 0xD)
    check("artifact pins exact full-freshness packing", art["wire_envelope"]["full_freshness"]["packing"] == "trip16 || reset20 || message8 || reset_low2 || 00b")

    print("\n== authenticated input and slot selection ==")
    auth = art["wire_envelope"]["authenticated_input"]
    check("authenticated input is exactly 36 bytes", auth["bytes"] == 36 and auth["application_bytes"] == 28 and auth["freshness_storage_bytes"] == 6)
    check("authenticated input exact shape", auth["packing"] == "DataID_be16(0x00B6) || B0..B27 || reconstructed_freshness48" and auth["data_id_bytes"] == "00b6")
    check("CMAC compare is MSB28", "MSB28" in auth["algorithm"])
    sel = keys["shared_crypto_selection"]
    check("B6 selects generated config0/job0/ICU-S slot4", sel["secoc_crypto_config_id"] == 0 and sel["cryptoif_job_handle"] == 0 and sel["icus_slot_selector"] == 4)
    check("slot4 key value remains CPU-opaque", art["wire_envelope"]["profile"]["key_value_cpu_visible"] is False and art["static_conclusion"]["receiver_key_value_closed"] is False)

    print("\n== verified upper delivery ==")
    delivery = art["verified_delivery"]
    check("verified route resolves to COM PDU42", delivery["route_id"] == 42 and delivery["resolved_upper_callback"] == "0x00076A3C" and "COM RxIndication" in delivery["upper_callback_role"])
    check("delivery chain exact", delivery["queue_ingress"] == "0x0008865A" and delivery["verify_worker"] == "0x00088A56" and delivery["upper_wrapper"] == "0x00088856 -> 0x00089514 -> 0x0007AFB6")
    check("no trailer-stripping overclaim", "does not prove" in delivery["length_boundary"] and "application-consumer census" in delivery["length_boundary"])

    print("\n== application-consumer closure ==")
    app = art["application_consumption"]
    check("configured B6 IDs are exactly 252..267", app["configured_signal_ids"] == list(range(252, 268)))
    check("scalar B6 IDs are exactly 254..265", app["scalar_extracted_signal_ids"] == list(range(254, 266)))
    check("nonscalar configured IDs exact", app["configured_without_scalar_receive"] == [252, 253, 266, 267])
    check("semantic scalar IDs exact", app["application_semantic_signal_ids"] == [254, 255, 258, 260, 261, 262, 263, 264, 265])
    check("extracted/no-downstream IDs exact", app["extracted_no_recovered_downstream_consumer_signal_ids"] == [256, 257, 259])
    escape = app["generic_escape_census"]
    check("no B6 nonscalar block/group consumer", escape["non_scalar_ids_used_by_block_group_api"] == [])
    check("no B6 full-PDU copy", escape["b6_full_pdu_copy_present"] is False and 42 not in escape["all_literal_full_pdu_ids"])
    check("no raw absolute B6 COM-buffer pointer", escape["raw_u32_buffer_pointer_hits"] == [])
    direct_region = escape["direct_com_region_reference_census"]
    check("no direct named/simple-GP-alias B6 COM-window reference in application corpus",
          direct_region["hit_count"] == 0 and direct_region["direct_hits"] == []
          and direct_region["first_byte"] == "0xFEBE4AF4" and direct_region["last_byte"] == "0xFEBE4B13"
          and direct_region["application_first"] == "0x00020000"
          and direct_region["application_end_exclusive"] == "0x00100000"
          and direct_region["scanned_application_function_count"] == 5138)
    check("direct-region negative states its remaining alias boundary",
          "simple GP aliases/constants/copies" in direct_region["boundary"]
          and "computed-base/value-set aliases" in direct_region["boundary"])
    check("bounded escape wording preserved", "computed-base aliases" in escape["boundary"] and "hardware/DMA" in escape["boundary"])

    print("\n== complete 256-bit partition ==")
    counts = app["bit_category_counts"]
    check("all 256 wire bits partitioned once", sum(counts.values()) == 256)
    check("51 bits have recovered application semantics", counts["application_semantic"] == 51)
    check("6 bits extracted but have no recovered downstream consumer", counts["extracted_no_recovered_downstream_consumer"] == 6)
    check("167 authenticated app bits have no recovered app consumer", counts["authenticated_application_no_recovered_consumer"] == 167)
    check("security trailer partitions 4 FV + 28 MAC bits", counts["secoc_transmitted_freshness"] == 4 and counts["secoc_transmitted_authenticator"] == 28)
    byte_map = app["byte_map"]
    check("byte map covers B0..B31", [row["byte"] for row in byte_map] == list(range(32)))
    check("B0..B2 are authenticated/no-consumer", all(set(byte_map[i]["bit_categories_lsb_to_msb"]) == {"authenticated_application_no_recovered_consumer"} for i in range(3)))
    check("B3 includes Target Lateral ID and two no-consumer bits", {f["signal_id"] for f in byte_map[3]["scalar_fields"]} == {254} and byte_map[3]["bit_categories_lsb_to_msb"].count("application_semantic") == 6)
    check("B4/B5 are entirely target-angle semantics", all(set(byte_map[i]["bit_categories_lsb_to_msb"]) == {"application_semantic"} for i in (4, 5)))
    check("B6 partitions snapshot/gate/staged and one unconsumed bit", byte_map[6]["bit_categories_lsb_to_msb"].count("application_semantic") == 1 and byte_map[6]["bit_categories_lsb_to_msb"].count("extracted_no_recovered_downstream_consumer") == 6 and byte_map[6]["bit_categories_lsb_to_msb"].count("authenticated_application_no_recovered_consumer") == 1)
    check("B7/B8/B9 are entirely recovered application semantics", all(set(byte_map[i]["bit_categories_lsb_to_msb"]) == {"application_semantic"} for i in (7, 8, 9)))
    check("B10 has four semantic and four no-consumer bits", byte_map[10]["bit_categories_lsb_to_msb"].count("application_semantic") == 4 and byte_map[10]["bit_categories_lsb_to_msb"].count("authenticated_application_no_recovered_consumer") == 4)
    check("B11..B27 are authenticated/no-consumer", all(set(byte_map[i]["bit_categories_lsb_to_msb"]) == {"authenticated_application_no_recovered_consumer"} for i in range(11, 28)))
    check("B28 splits CMAC/FV nibble", byte_map[28]["bit_categories_lsb_to_msb"] == ["secoc_transmitted_authenticator"] * 4 + ["secoc_transmitted_freshness"] * 4)
    check("B29..B31 are all transmitted authenticator", all(set(byte_map[i]["bit_categories_lsb_to_msb"]) == {"secoc_transmitted_authenticator"} for i in range(29, 32)))

    print("\n== sender/application boundary ==")
    check("receiver semantics explicitly concentrated B3..B10", "B3..B10" in app["receiver_semantic_concentration"])
    check("unconsumed application bytes still authenticated", "all B0..B27 are inside the CMAC input" in app["sender_boundary"])
    conclusion = art["static_conclusion"]
    check("full receiver partition and SecOC envelope closed", conclusion["full_32_byte_receiver_partition_closed"] is True and conclusion["receiver_secoc_envelope_closed"] is True and conclusion["receiver_authenticated_input_closed"] is True)
    check("receiver freshness/trailer closed", conclusion["receiver_freshness_layout_closed"] is True and conclusion["receiver_transmitted_trailer_layout_closed"] is True)
    check("receiver app generic consumption closed", conclusion["receiver_application_generic_consumption_closed"] is True)
    check("sender cadence/ownership still open", conclusion["sender_wall_clock_cadence_closed"] is False and conclusion["sender_freshness_state_ownership_closed"] is False and conclusion["upstream_producer_closed"] is False)
    check("evidence boundary rejects sender/key overclaim", "does not recover the ICU-S slot-4 secret value" in art["evidence_boundary"] and "sender cadence" in art["evidence_boundary"])


def _section_b6_receiver_contract():
    print('== b6 receiver contract ==')
    """Verify the H protected-B6 request/validity/loss receiver contract."""
    import hashlib, json, struct, subprocess, sys, tempfile
    from pathlib import Path

    REPO = Path(__file__).resolve().parents[1]
    ART = REPO / "data/generated/corolla_8965H1202000_b6_receiver_contract.json"
    EVID = REPO / "data/generated/corolla_8965H1202000_b6_receiver_contract_decompiler_evidence.json"
    FOLLOWUP = REPO / "data/generated/corolla_8965H1202000_tms053_followup_decompiler_evidence.json"
    CAN_EVID = REPO / "data/generated/corolla_8965H1202000_can_com_decompiler_evidence.json"
    RAW = REPO / "community/albinoelephant/normalized/8965H1202000_CodeFlash.bin"
    TOOL = REPO / "tools/build_corolla_h_b6_receiver_contract.py"

    art = json.loads(ART.read_text())
    ev = json.loads(EVID.read_text())
    followup = json.loads(FOLLOWUP.read_text())
    can_ev = json.loads(CAN_EVID.read_text())
    raw = RAW.read_bytes()

    print("\n== exact source binding ==")
    check("schema v1", art["schema"] == "corolla-8965H1202000-b6-receiver-contract-v1")
    check("H image exact", len(raw) == 0x100000 and art["sources"]["codeflash"]["sha256"] == sha(raw) == "0b47bdc1217835c839e3543e52eab40eb793650a9c159e46f6a9b365ea41a67f")
    check("33 historical compact receiver functions preserved", ev["function_count"] == art["sources"]["decompiler_evidence"]["function_count"] == 33)
    check("29 TMS-053 follow-up functions are raw-bound", followup["function_count"] == art["sources"]["tms053_followup_decompiler_evidence"]["function_count"] == 29 and all(sha(raw[int(x["entry"], 16):int(x["entry"], 16) + x["body_size"]]) == x["body_sha256"] for x in followup["functions"]))
    check("all compact receiver bodies raw-bound", all(sha(raw[int(x["entry"], 16):int(x["entry"], 16) + x["body_size"]]) == x["body_sha256"] for x in ev["functions"]))
    rx = next(x for x in can_ev["functions"] if x["entry"] == "0x00076A3C")
    check("CAN COM receive indication raw-bound", sha(raw[0x76A3C:0x76A3C + rx["body_size"]]) == rx["body_sha256"])

    print("\n== request selection ==")
    req = art["request_contract"]
    check("signal254 request geometry", req["signal_id"] == 254 and req["wire_byte"] == 3 and req["bit_length"] == 6 and req["snapshot"] == "0xFEBEADB0")
    check("OEM request dictionary exact", req["oem_dictionary"] == "Target Lateral ID" and req["no_request"] == {"value": 0, "label": "No Request (Manual Operation)"})
    check("five H active request IDs exact", req["accepted_active_requests"] == {"1":"PCS","4":"LDA","10":"Hands Off LTA","11":"LTA/LCA","19":"PDA"})
    check("request decoder/gates exact", req["decoder"] == "0x000CBE6E" and req["common_active_flag"] == "0xFEBEC272" and req["receiver_gates"] == ["0xFEBEACBD == 0", "0xFEBEC26D == 1"])
    check("signal254 classified as request ID", req["classification"] == "supported-target-lateral-request-id" and "unsupported/No-Request" in req["boundary"])

    print("\n== lower COM deadline and loss cutout ==")
    com = art["communication_supervision"]
    pdu_raw = raw[0x22770:0x22778]
    check("PDU42 raw descriptor exact", pdu_raw.hex() == "060000002000000c" and struct.unpack("<HBBHBB", pdu_raw) == (6,0,0,32,0,12))
    pdu = com["pdu_descriptor"]
    check("PDU42 contract decodes deadline/length/flags", pdu == {"address":"0x00022770","raw_hex":"060000002000000c","deadline_value_ticks":6,"successful_rx_reload_ticks":7,"length":32,"flags":12,"activity_tracking_enabled":True})
    check("successful Rx reload and activity clear", com["successful_receive"]["entry"] == "0x00076A3C" and any("769F6" in x for x in com["successful_receive"]["actions"]) and any("87A82" in x for x in com["successful_receive"]["actions"]))
    loss = com["deadline_expiry"]
    check("primary cutout is seven foreground ticks", loss["primary_cutout_after_foreground_ticks"] == 7 and loss["countdown"] == "0x0007683C" and "87AA0" in loss["expiry_action"])
    check("wall-clock timeout closed at nominal 35 ms", loss["absolute_time_supported"] is True and loss["nominal_primary_cutout_ms"] == 35.0 and "5.1 ms" in loss["absolute_time_boundary"])

    print("\n== receive-status propagation ==")
    status_raw = raw[0x28D8C:0x28D94]
    check("slot18 status config exact", status_raw.hex() == "2a00000bb8010200" and status_raw[0] == 42 and struct.unpack_from("<H", status_raw, 4)[0] == 440)
    qual = com["status_qualifier"]
    check("extended qualifier records 440 threshold", qual["config_address"] == "0x00028D8C" and qual["configured_extended_threshold_ticks"] == 440 and qual["primary_cutout_precedes_extended_state"] is True)
    flow = com["status_dataflow"]
    check("status slot18 chain exact", flow["slot_accessor"] == "0x44744(0x18)" and flow["raw"] == "0xFEBE7DA0" and flow["staging"] == "0xFEBEF132" and flow["snapshot"] == "0xFEBEADB9")
    check("receive status convention exact", flow["initial_value"] == 1 and flow["healthy_value"] == 0 and "nonzero immediately" in flow["loss_value"])
    gate = com["steering_enable_gate"]
    check("C26D steering-health gate exact", gate["entry"] == "0x000CC7F8" and gate["output"] == "0xFEBEC26D" and gate["health_slots"] == ["0x10 (CAN 0x025)", "0x18 (CAN 0x0B6)"] and "0xFEBEADB9 == 0" in gate["condition"])
    check("loss disables cooperative profile selection", "cannot assert any cooperative profile" in gate["effect"])
    mode_gate = com["cooperative_system_mode_gate"]
    check("FEBEACBD normalization exact", mode_gate["source_state"] == "0xFEBEF000" and mode_gate["normalized_output"] == "0xFEBEACBD" and mode_gate["normalization"] == {"0": 0, "2": 2, "3": 4, "other_nonzero": 1})
    check("cooperative acceptance requires ACBD0 and C26D1", "FEBEACBD == 0 AND FEBEC26D == 1" in mode_gate["cooperative_acceptance"])
    check("ACBD is distinct from B6 communication loss", "not a synonym" in mode_gate["classification"] and "FEBEADB9 -> FEBEC26D" in mode_gate["b6_loss_path_is_separate"])
    check("no direct H Tx packer reads ACBD under promoted census", mode_gate["direct_reference_count"] == 21 and mode_gate["direct_tx_packer_refs"] == [] and "no native wire-visible" in mode_gate["wire_feedback_boundary"])

    print("\n== scheduler domain ==")
    sched = com["scheduler"]
    check("foreground tick source exact", sched["foreground_loop"] == "0x0005F30C" and "TAUJ0 CH3" in sched["tick_source"] and "0xFFFFB111" in sched["tick_source"])
    check("deadline and status run in same tick domain", sched["same_tick_domain"] is True and sched["lower_deadline_chain"] == "5F30C -> 5FAF2 -> 73564 -> 7683C" and "58BBC transition | 59574 steady" in sched["status_chain"])
    timing = sched["tauj0_config"]
    check("TAUJ0 CH3 startup/steady count geometry exact", timing["init_entry"] == "0x0005F660" and timing["steady_reload_entry"] == "0x0005F812" and timing["tps"] == timing["brs"] == timing["cmor3"] == 0 and timing["ch3_initial_cdr"] == 407999 and timing["ch3_steady_cdr"] == 399999 and timing["ch3_initial_counts"] == 408000 and timing["ch3_steady_counts"] == 400000)
    check("steady foreground tick is nominal 5 ms with one 5.1 ms startup interval", timing["nominal_steady_tick_ms"] == 5.0 and abs(timing["nominal_initial_interval_ms"] - 5.1) < 1e-12)
    dyn = sched["dynamic_corroboration"]
    check("Span 0x030 dynamically corroborates two ticks at ~10 ms", dyn["frames"] == 6000 and dyn["descriptor_cycle_ticks"] == 2 and abs(dyn["mean_interval_ms"] - 10.00001211468578) < 1e-9 and abs(dyn["derived_foreground_tick_ms"] - 5.00000605734289) < 1e-9)
    check("Techstream missing-message join exact", com["techstream"] == {"dtc":"U012987","description":"Lost Communication with Brake System Control Module","failure":"Missing Message","dem_event":"0x0143"})

    print("\n== companion control fields ==")
    cf = art["companion_fields"]
    unpacker = next(x["decompiled_c"] for x in ev["functions"] if x["entry"] == "0x00046A10")
    check("signals258/260/261/264/265 exact unpacker geometries", all(token in unpacker for token in (
        "FUN_0007643a(0x102,0x1ad,1,2,0,unaff_gp + -0x3a68);",
        "FUN_0007643a(0x104,0x1ae,2,6,0,unaff_gp + -0x3a66);",
        "FUN_0007643a(0x105,0x1ae,6,0,0,unaff_gp + -0x3a65);",
        "FUN_0007643a(0x108,0x1b1,1,7,0,unaff_gp + -0x3a62);",
        "FUN_0007643a(0x109,0x1b1,3,0,0,unaff_gp + -0x3a5f);",
    )))
    check("signal258 corrected as additive-term suppressor", cf["258"]["wire"] == "B6 bit2" and cf["258"]["snapshot"] == "0xFEBEADBB" and cf["258"]["consumer"] == "0x000CBEEE" and "signal258 == 1 suppresses" in cf["258"]["semantics"] and cf["258"]["candidate_id11_value"] == 1 and cf["258"]["oem_name_identified"] is False)
    check("signal258 OEM name is not overclaimed", cf["258"]["family_vocabulary_candidate"] == "Cooperative Control in Progress Flag" and "does not prove" in cf["258"]["boundary"])
    check("signal260 0/3 recovered-equivalence is bounded", cf["260"]["wire"] == "B7 bits7:6" and cf["260"]["snapshot"] == "0xFEBEADC2" and cf["260"]["consumers"] == ["0x000C89D2","0x000C8D42"] and "values 0 and 3" in cf["260"]["semantics"] and cf["260"]["candidate_id11_value"] == 0 and "not asserted globally equivalent" in cf["260"]["candidate_boundary"])
    seq = cf["261"]
    check("signal261 is exact six-bit rolling sequence counter", seq["wire"] == "B7 bits5:0" and seq["snapshot"] == "0xFEBEADBC" and seq["classification"] == "rolling-sequence-counter" and seq["counter_bits"] == 6 and seq["wrap_max"] == 63 and seq["modulus"] == 64)
    check("sequence constants raw exact", struct.unpack_from("<H", raw, 0xAFCE8)[0] == 63 and struct.unpack_from("<H", raw, 0xAFCEA)[0] == 8 and seq["gap_cap"] == 8)
    check("sequence gap behavior exact", seq["delta_formula"] == "delta = (current - previous) mod 64" and seq["effective_gap_formula"] == "effective_gap = 1 when delta <= 1, otherwise min(delta, 8)" and seq["strict_plus_one_required"] is False)
    check("sequence gap reaches plausibility supervision", "CB4F4" in seq["downstream"] and "GP+0xA4C" in seq["downstream"])
    check("signals262/263 zero remove recovered percentage contributions", cf["262"]["wire"] == "B8" and cf["262"]["snapshot"] == "0xFEBEADBD" and cf["262"]["consumer"] == "0x000CC442" and cf["262"]["candidate_id11_value"] == 0 and cf["263"]["wire"] == "B9" and cf["263"]["snapshot"] == "0xFEBEADBE" and cf["263"]["consumer"] == "0x000CBFCE" and cf["263"]["candidate_id11_value"] == 0)
    check("signal264 special validity/inhibit remains scoped", cf["264"]["wire"] == "B10 bit7" and cf["264"]["snapshot"] == "0xFEBEADC1" and "zero is required" in cf["264"]["semantics"] and cf["264"]["candidate_id11_value"] == 0 and "AP/Remote Parking" in cf["264"]["scope_boundary"])
    check("signal265 is valid-gated status with zero default", cf["265"]["wire"] == "B10 bits2:0" and cf["265"]["snapshot"] == "0xFEBEADD9" and cf["265"]["consumer"] == "0x000CCF58" and cf["265"]["downstream_consumer"] == "0x000CCF8C" and cf["265"]["initial_default_value"] == cf["265"]["candidate_id11_value"] == 0 and "healthy" in cf["265"]["semantics"])

    print("\n== static conclusion ==")
    c = art["static_conclusion"]
    check("receiver request selection closed", c["request_selection_closed"] is True)
    check("loss cutout closed in ticks and nominal wall clock", c["primary_loss_cutout_closed_in_ticks"] is True and c["primary_loss_cutout_ticks"] == 7 and c["wall_clock_timeout_closed"] is True and c["foreground_tick_nominal_ms"] == 5.0 and c["primary_loss_cutout_nominal_ms"] == 35.0)
    check("rolling sequence contract closed", c["sequence_counter_closed"] is True and c["sequence_modulus"] == 64 and c["sequence_gap_cap"] == 8)
    check("secondary names and upstream producer remain bounded", c["secondary_field_names_closed"] is False and c["upstream_producer_closed"] is False and c["minimal_id11_companion_candidate_closed_for_eps_consumers"] is True and "FRC_P5/Brake stock template" in c["next_static_target"])
    check("evidence boundary keeps stock cadence/cross-ECU neutrality bounded", "35.0 ms" in art["evidence_boundary"] and "stock B6 transmit cadence" in art["evidence_boundary"] and "cross-ECU neutrality" in art["evidence_boundary"])


def _section_b6_secoc_verification():
    print('== b6 secoc verification ==')
    """Verify the complete H/F protected-0x0B6 receiver SecOC state machine."""

    import hashlib
    import json
    import struct
    from pathlib import Path

    REPO = Path(__file__).resolve().parents[1]
    ART = REPO / "data/generated/corolla_8965H1202000_b6_secoc_verification.json"
    EVID = REPO / "data/generated/corolla_8965H1202000_b6_secoc_verification_decompiler_evidence.json"
    H = REPO / "community/albinoelephant/normalized/8965H1202000_CodeFlash.bin"
    F_RAW = REPO / "community/spanconstant/raw-20260821/span-corolla-2025.20260821-1511/dump_codeflash_00000000_00200000_20260821-152033.bin"
    FULL = REPO / "data/generated/corolla_8965H1202000_b6_full_receiver_contract.json"
    BASE = REPO / "data/generated/corolla_8965H1202000_b6_receiver_contract.json"
    KEYS = REPO / "data/generated/corolla_8965H1202000_secoc_key_provenance.json"
    TOOL = REPO / "tools/build_corolla_h_b6_secoc_verification.py"
    EXTRACTOR = REPO / "tools/extract_corolla_h_b6_secoc_verification_evidence.py"


    def reset_trials(current: int) -> list[tuple[int, int]]:
        rows = [(0, current)]
        if current > 0:
            rows.append((1, current - 1))
        if current < 0xFFFFF:
            rows.append((2, current + 1))
        if current > 1:
            rows.append((3, current - 2))
        if current < 0xFFFFE:
            rows.append((4, current + 2))
        return rows


    def reset_candidate(current: int, rx_low2: int, attempt: int) -> tuple[int, int] | None:
        rows = [(trial, value) for trial, value in reset_trials(current) if value & 3 == rx_low2]
        return rows[attempt] if attempt < len(rows) else None


    def next_message(committed: int, rx_low2: int) -> tuple[int, bool]:
        candidate = (committed & ~3) | rx_low2
        if rx_low2 <= (committed & 3):
            candidate += 4
        if candidate <= 0xFF:
            return candidate, False
        return 0xFF, True


    art = json.loads(ART.read_text())
    ev = json.loads(EVID.read_text())
    h = H.read_bytes()
    f = F_RAW.read_bytes()
    full = json.loads(FULL.read_text())
    base = json.loads(BASE.read_text())
    keys = json.loads(KEYS.read_text())
    funcs = {int(row["entry"], 16): row for row in ev["functions"]}

    print("\n== exact source and cross-variant binding ==")
    check("schema exact", art["schema"] == "corolla-8965H1202000-b6-secoc-verification-v1")
    check("H image exact", len(h) == 0x100000 and sha(h) == "0b47bdc1217835c839e3543e52eab40eb793650a9c159e46f6a9b365ea41a67f")
    check("44 target-native functions promoted", ev["function_count"] == len(funcs) == 44)
    check("extractor source pinned", ev["generator"] == {"path": "tools/extract_corolla_h_b6_secoc_verification_evidence.py", "sha256": sha(EXTRACTOR.read_bytes())})
    check("whole forced H source corpus pinned", ev["source_corpus"]["sha256"] == "5cc79174e8ea917356b9d4758d086df1209c85c9665f122782cff7d88261c387")
    check("all promoted H bodies raw-bound",
          all(sha(h[a:a + row["body_size"]]) == row["body_sha256"] for a, row in funcs.items()))
    check("H/F application bytes are identical", h[0x20000:0x100000] == f[0x20000:0x100000])
    check("verification contract explicitly shared with F", art["applies_to"] == ["8965H1202000", "8965F1208000"] and art["cross_variant"]["b6_secoc_verification_contract_byte_identical"] is True)
    check("cross-variant caveat retained", "low-region calibration" in art["cross_variant"]["boundary"])

    print("\n== exact B6 profile / identifiers ==")
    r = h[0x257CC:0x2581C]
    check("B6 profile record exact location/size", len(r) == 0x50 and art["identifiers"]["secoc_record_address"] == "0x000257CC")
    check("B6 DataID and PDU42 exact", struct.unpack_from("<H", r, 0xA)[0] == 0xB6 and struct.unpack_from("<H", r, 0x34)[0] == 42)
    check("B6 freshness ID2 normal slot1", r[9] == 0 and struct.unpack_from("<H", r, 0x12)[0] == 2 and art["identifiers"]["normal_freshness_slot"] == 1)
    check("B6 FV46/FV4 exact", r[0x14] == 46 and r[0x15] == 4)
    check("B6 get/commit callbacks exact", struct.unpack_from("<I", r, 0x48)[0] == 0x896B0 and struct.unpack_from("<I", r, 0x30)[0] == 0x89758)
    check("B6 two retry budgets exact", struct.unpack_from("<H", r, 0x10)[0] == 1 and struct.unpack_from("<H", r, 0x2E)[0] == 2)
    check("B6 internal linkage field +0x04 is zero", struct.unpack_from("<H", r, 4)[0] == 0 and art["identifiers"]["normal_linkage_field_plus_0x04"] == 0)
    check("no invented extra source identifier", art["identifiers"]["separate_source_identifier_in_cmac_input"] is False and "DataID" in art["identifiers"]["boundary"])

    print("\n== exact RAM state geometry ==")
    ram = art["ram_state"]
    check("retry/result cells exact", ram["crypto_submit_retry_counter"] == "0xFEBE5404" and ram["authentication_candidate_retry_counter"] == "0xFEBE5406" and ram["cmac_verify_result_byte"] == "0xFEBE5450")
    check("authenticated sync current cells exact", ram["global_sync_current_trip"] == "0xFEBE54AC" and ram["global_sync_current_reset"] == "0xFEBE54B0")
    check("authenticated sync pending cells exact", ram["global_sync_pending_trip"] == "0xFEBE54B4" and ram["global_sync_pending_reset"] == "0xFEBE54B8")
    check("B6 committed/pending slots exact", ram["b6_committed_slot"]["address"] == "0xFEBE54D4" and ram["b6_pending_slot"]["address"] == "0xFEBE54EC")
    check("B6 freshness slot shape exact", ram["b6_committed_slot"]["fields"] == {"trip_u32": 0, "reset_u32": 4, "message_u16": 8} and ram["b6_committed_slot"]["bytes"] == 12)
    check("init boundary does not overclaim persistence", "does not by itself claim" in ram["initialization"]["persistence_boundary"])

    print("\n== transmitted freshness and reference candidate arithmetic ==")
    tf = art["transmitted_freshness"]
    check("FV4 split exact", tf["wire"] == "B28[7:4]" and tf["decode"] == {"message_low2": "B28[7:6]", "reset_low2": "B28[5:4]"})
    check("full freshness format exact", tf["full_bits"] == 46 and tf["full_freshness"] == "trip16 || reset20 || message8 || reset_low2 || 00b")
    fa = art["freshness_acceptance"]
    rc = fa["reset_candidate_search"]
    check("reset candidate order exact", rc["ordered_trials"] == ["current", "current-1", "current+1", "current-2", "current+2"])
    check("reset domain exact", rc["domain"] == [0, 0xFFFFF])
    check("reset search is anchored to authenticated global reset", "uVar1 = *(uint *)(unaff_gp + -0x6350);" in funcs[0x89CDA]["decompiled_c"])
    check("reset low2 filter exact", rc["filter"] == "candidate_reset & 3 == transmitted reset_low2" and "*(byte *)(param_2 + 10)" in funcs[0x89CDA]["decompiled_c"])
    check("independent reset model nominal", reset_candidate(100, 0, 0) == (0, 100) and reset_candidate(100, 3, 0) == (1, 99) and reset_candidate(100, 1, 0) == (2, 101))
    check("independent reset model ±2 ambiguity", reset_candidate(100, 2, 0) == (3, 98) and reset_candidate(100, 2, 1) == (4, 102))
    check("B6 retry1 exactly resolves ±2 ambiguity", rc["ordinary_b6_retry_limit"] == 1 and "-2" in rc["important_ambiguity"] and "+2" in rc["important_ambiguity"])
    mc = fa["message_reconstruction_same_epoch"]
    check("same-epoch formula exact", mc["formula"] == "candidate=(committed_message & ~3)|received_message_low2; if received_low2 <= (committed_message & 3), candidate += 4")
    check("message truncation width is exactly two bits", "uStack_24 = 2" in funcs[0x89E2C]["decompiled_c"] and "uVar6 = *param_3;" in funcs[0x89D58]["decompiled_c"] and "uVar7 = 1 << uVar6;" in funcs[0x89D58]["decompiled_c"])
    check("message low2 comes from B28[7:6] and committed slot +8", "*(ushort *)(param_2 + 8) <=" in funcs[0x89E2C]["decompiled_c"] and "unaff_gp + -0x6330" in funcs[0x89E2C]["decompiled_c"] and (0xFEBEB800 - 0x6330 + 0xC) == 0xFEBE54DC)
    check("message reconstruction masks then advances by four", "uVar4 = *(ushort *)(param_2 + 8) | ~((short)uVar7 - 1U) & uVar2;" in funcs[0x89D58]["decompiled_c"] and "uVar6 = uVar5 + uVar2;" in funcs[0x89D58]["decompiled_c"])
    check("independent message model forward 1..4", next_message(10, 3) == (11, False) and next_message(10, 2) == (14, False) and mc["ordinary_forward_delta"] == [1, 4])
    check("message boundary model exact", next_message(254, 3) == (255, False) and next_message(253, 0) == (255, True))
    check("new epoch forward rule exact", fa["epoch_transition"]["strictly_newer_rule"] == "global_trip > committed_trip OR (global_trip == committed_trip AND candidate_reset > committed_reset)")
    check("new epoch starts message from received low2", fa["epoch_transition"]["new_epoch_message"] == "received_message_low2 (0..3)")
    check("staging happens before CMAC", "pending slot" in fa["epoch_transition"]["staging"] and "before CMAC" in fa["epoch_transition"]["staging"])

    print("\n== special boundary and authenticated sync wrap ==")
    s24 = fa["special_status_0x24"]
    check("0x24 is not hard freshness reject", s24["hard_reject"] is False)
    check("0x24 still executes CMAC", s24["cmac_still_runs"] is True and "common C3 path" in s24["reason"])
    wrap = fa["trip_wrap"]
    check("sync trip-wrap threshold raw exact", h[0x25728] == 0x0F and wrap["sync_threshold"] == 15)
    check("sync wrap window exact", "0xFFFF-15" in wrap["wrap_acceptance"] and "<=16" in wrap["wrap_acceptance"])
    check("authenticated trip wrap clears B6 freshness slots", wrap["b6_state_cleared_on_authenticated_trip_wrap"] is True and "0x8A0AE(0)" in wrap["post_verified_sync_action"] and "B6" in wrap["post_verified_sync_action"])
    check("global sync only commits after auth success", fa["global_epoch_source"]["commit_only_after_authentication_success"] is True)

    print("\n== CMAC construction, command7, key selector ==")
    env = art["authenticated_envelope"]
    check("CMAC input exact 36-byte shape", env["authenticated_input_bytes"] == 36 and env["cmac_input"] == "00 B6 || B0..B27 || reconstructed_freshness[6]")
    check("CMAC/tag exact", env["cmac_algorithm"] == "AES-CMAC-128" and env["received_tag_bits"] == 28 and env["transmitted_tag"] == "MSB28")
    check("command7 path exact", "0x88A56" in env["submit_path"] and "0x822D0" in env["submit_path"] and "0x83BF4" in env["submit_path"])
    check("config0/job0/slot4 exact", art["identifiers"]["secoc_crypto_config_id"] == 0 and art["identifiers"]["cryptoif_job_handle"] == 0 and art["identifiers"]["icus_slot_selector"] == 4)
    check("ICU-S command word exact", env["icus_command_word"].endswith("0x00040007"))
    check("raw config type1/selector4 exact", h[0x2570C:0x25720].hex() == "0100000004000000000000000000000000000000")
    check("slot4 key remains opaque", env["key_value_cpu_visible"] is False and keys["static_storage_derivation_conclusion"]["cpu_visible_raw_slot4_key"] is False)
    check("result zero means CMAC match", "0 means verified/match" in env["result_polarity"] and "disabled" in env["result_evidence"])

    print("\n== queue / retry / acceptance state machine ==")
    sm = art["acceptance_state_machine"]
    check("queue states exact", sm["queue_states"] == {"idle": "E1", "new": "D2", "verify": "C3", "retry": "B4", "freshness_failure": "A5", "generic_failure": "96"})
    check("fresh PDU resets both retry counters", "D2->C3" in sm["new_pdu_transition"] and "resets" in sm["new_pdu_transition"])
    check("B4 re-entry itself adds no counter reset", "B4->C3" in sm["same_pdu_retry_transition"] and "without an additional reset" in sm["same_pdu_retry_transition"])
    rb = sm["retry_budgets"]
    check("auth candidate/MAC retry budget1 exact", rb["authentication_candidate_or_mac_mismatch"]["limit"] == 1 and rb["authentication_candidate_or_mac_mismatch"]["record_offset"] == "0x10" and rb["authentication_candidate_or_mac_mismatch"]["scope"] == "current queued PDU")
    check("auth retry resets CryptoIf busy counter", "unaff_gp + -0x63fc) = 0;" in funcs[0x8891E]["decompiled_c"] and "resets the CryptoIf-submit counter" in rb["authentication_candidate_or_mac_mismatch"]["interaction"])
    check("CryptoIf busy retry budget2 is per auth attempt", rb["cryptoif_submit_busy"]["limit"] == 2 and rb["cryptoif_submit_busy"]["record_offset"] == "0x2E" and "current authentication candidate" in rb["cryptoif_submit_busy"]["scope"])
    check("CryptoIf result2 increments busy counter without clearing auth counter", "unaff_gp + -0x63fc" in funcs[0x889C2]["decompiled_c"] and "unaff_gp + -0x63fa" not in funcs[0x889C2]["decompiled_c"])
    fr = sm["freshness_results"]
    check("freshness 0x22 hard fails before command7", "hard freshness failure" in fr["0x22"] and "no command7" in fr["0x22"])
    check("freshness 0x22 records conditional failure-forwarding", "0x888A6" in fr["0x22"] and "grace counter" in fr["0x22"])
    check("freshness 0x23 retries candidate", "candidate retry" in fr["0x23"] and "C3->B4" in fr["0x23"])
    check("freshness 0x24 stays verify and continues command7", "state remains C3" in fr["0x24"] and "command7 still executes" in fr["0x24"])
    check("Gate1 requires verify-worker zero", "only when 0x88A56 returns 0" in sm["gate1"])
    g2 = sm["gate2"]
    check("Gate2 result cell exact", g2["result_cell"] == "0xFEBE5450")
    check("success commits before delivery", g2["commit_before_delivery"] is True and "pending slot commits" in g2["success"] and "then PDU42 routes" in g2["success"])
    check("mismatch never commits freshness", "does not commit" in g2["mismatch"])
    check("exhausted mismatch records conditional failure-forwarding", "retry budget is exhausted" in g2["mismatch"] and "0x888A6" in g2["mismatch"])
    fc = sm["freshness_commit"]
    check("normal commit copies pending only on success", "copy pending" in fc["success_action"] and "no copy" in fc["failure_action"] and "unchanged" in fc["failure_action"])
    fd = sm["verification_failure_delivery_policy"]
    check("B6 failure-forward grace policy exact", fd["b6_profile_plus_0x09"] == 0 and fd["grace_limit_raw"] == 204 and fd["grace_counter"] == "0xFEBE5408")
    check("failure grace raw config exact", struct.unpack_from("<H", h, 0x25726)[0] == 204)
    check("failure grace lifecycle promoted", all(a in funcs for a in (0x88288, 0x88308, 0x8857C, 0x886DA, 0x886FC)))
    check("failure delivery handler promoted", all(a in funcs for a in (0x88512, 0x88856, 0x888A6)))
    check("hard freshness fail can conditionally reach COM", "0x88A56 sets A5" in fd["freshness_0x22_path"] and "still reach COM" in fd["freshness_0x22_path"])
    check("exhausted CMAC mismatch can conditionally reach COM", "retry is exhausted" in fd["cmac_mismatch_path"] and "0x888A6" in fd["cmac_mismatch_path"])
    check("failure forwarding never commits freshness", "not authenticated successes" in fd["authentication_boundary"] and "do not commit" in fd["authentication_boundary"])
    check("post-grace normal failure route closed", "grace_counter >= 204" in fd["steady_state_boundary"] and "does not route" in fd["steady_state_boundary"])
    check("verified upper route remains COM PDU42", sm["verified_delivery"]["route_id"] == 42 and sm["verified_delivery"]["resolved_upper_callback"] == "0x00076A3C")

    print("\n== application signal261 is independent from SecOC freshness ==")
    seq = art["application_sequence_relation"]
    check("signal261 wire geometry exact", seq["signal_id"] == 261 and seq["wire"] == "B7[5:0]" and seq["application_counter_bits"] == 6)
    check("signal261 modulo64/gap8 exact", seq["application_modulus"] == 64 and seq["application_gap_cap"] == 8 and seq["application_consumer"]["modulus"] == 64)
    check("SecOC message counter distinct 8-bit state", seq["secoc_message_counter_bits"] == 8 and seq["secoc_transmitted_message_bits"] == 2)
    check("two counters explicitly independent", seq["independent_counters"] is True and "does not select the SecOC freshness candidate" in seq["relationship"])
    check("sender must maintain both counters", "Maintain both counters" in seq["sender_requirement"])

    print("\n== Sienna prior art and remaining sender boundary ==")
    prior = art["sienna_prior_art"]
    check("seven Sienna upper-engine role anchors", len(prior["rows"]) == 7)
    check("Sienna comparison uses consistent +0x5A64 role relocation", all(row["entry_delta"] == "0x5A64" for row in prior["rows"]))
    check("H/Sienna upper engine not falsely byte-identical", all(row["different_byte_count"] > 0 for row in prior["rows"]) and "not claimed byte-identical" in prior["boundary"])
    recipe = art["sender_recipe"]
    check("receiver-required sender envelope enumerated", len(recipe["receiver_required_steps"]) == 7 and "AES-CMAC-128" in recipe["receiver_required_steps"][4] and "authenticated/committed 0x00F" in recipe["receiver_required_steps"][0])
    check("slot4 secret remains true cryptographic blocker", "slot-4 secret value remains opaque" in recipe["cryptographic_blocker"])
    replacement = recipe["replacement_sender_state_machine"]
    check("replacement sender re-anchors on authenticated newer 0x00F epoch", "strictly newer authenticated 0x00F" in replacement["startup"] and "seeds full message8" in replacement["new_epoch"])
    check("same-epoch replacement progression matches receiver +1..+4 window", "+1 is simplest" in replacement["same_epoch"] and "+1..+4" in replacement["same_epoch"])
    check("sender restart waits for next epoch instead of guessing message8", "do not guess/replay" in replacement["sender_restart_mid_epoch"] and "next authenticated reset/trip advance" in replacement["sender_restart_mid_epoch"])
    check("replacement sender needs no cross-power message8 persistence", "No sender-side message8 persistence is required" in replacement["power_cycle_persistence"])
    check("replacement sender keeps signal261 separate", "separately modulo 64" in replacement["application_sequence261"] and replacement["state_to_persist_while_running"] == ["trip16", "reset20", "message8", "signal261"])
    check("replacement re-anchor delay stays outside acyclic receiver artifact", "separate freshness-bridge artifact" in replacement["reanchor_delay_boundary"] and "remains acyclic" in replacement["reanchor_delay_boundary"])
    check("replacement freshness no longer requires stock counter discovery", replacement["requires_stock_sender_counter_discovery"] is False and replacement["requires_exclusive_b6_authority"] is True and "no longer required" in recipe["runtime_state_blocker"])
    con = art["static_conclusion"]
    check("all receiver verification dimensions closed", all(con[k] is True for k in (
        "b6_freshness_extraction_closed", "b6_freshness_window_closed", "b6_mac_input_closed",
        "b6_key_slot_selection_closed", "b6_profile_identifiers_closed", "b6_sequence_relation_closed",
        "b6_accept_reject_state_machine_closed", "b6_commit_timing_closed", "b6_verification_failure_delivery_policy_closed", "b6_h_f_receiver_verification_identical")))
    check("replacement sender freshness state machine is closed", con["replacement_sender_freshness_state_machine_closed"] is True and con["replacement_sender_requires_stock_counter_discovery"] is False)
    check("true stock sender/key boundaries remain open", con["slot4_secret_value_closed"] is False and con["stock_sender_freshness_state_ownership_closed"] is False and con["sender_wall_clock_cadence_closed"] is False and con["upstream_producer_closed"] is False)
    check("evidence boundary rejects stock sender/key overclaim but closes replacement re-anchor", "does not recover the protected slot-4 secret" in art["evidence_boundary"] and "upstream FRC/Brake" in art["evidence_boundary"] and "exclusive replacement sender" in art["evidence_boundary"])


def _section_b6_target_angle_ingress():
    print('== b6 target angle ingress ==')
    """Verify the H protected-B6 target-angle ingress proof."""
    import hashlib,json
    from pathlib import Path
    REPO=Path(__file__).resolve().parents[1]
    ART=REPO/'data/generated/corolla_8965H1202000_b6_target_angle_ingress.json'
    EVID=REPO/'data/generated/corolla_8965H1202000_b6_target_angle_decompiler_evidence.json'
    TOOL=REPO/'tools/build_corolla_h_b6_target_angle_ingress.py'
    RAW=REPO/'community/albinoelephant/normalized/8965H1202000_CodeFlash.bin'
    d=json.loads(ART.read_text()); e=json.loads(EVID.read_text()); raw=RAW.read_bytes()
    print('\n== source identity ==')
    check('schema v4',d['schema']=='corolla-8965H1202000-b6-target-angle-ingress-v4')
    check('H hash exact',d['sources']['codeflash']['sha256']==sha(raw)=='0b47bdc1217835c839e3543e52eab40eb793650a9c159e46f6a9b365ea41a67f')
    check('41 compact H functions',e['function_count']==d['sources']['decompiler_evidence']['function_count']==41)
    check('all compact raw bodies validate',all(sha(raw[int(x['entry'],16):int(x['entry'],16)+x['body_size']])==x['body_sha256'] for x in e['functions']))
    print('\n== exact protected B6 ingress ==')
    mode=d['mode_ingress']; w=d['wire_ingress']
    check('signal254 is 6-bit B3 mode ID',mode['signal_id']==254 and mode['wire_byte']==3 and mode['bit_length']==6 and not mode['signed'])
    check('signal254 fixed-map snapshot exact',mode['raw_destination']=='0xFEBE7D96' and mode['staging_destination']=='0xFEBEF127' and mode['snapshot_destination']=='0xFEBEADB0')
    check('signal254 decoder exact values',mode['decoded_values']=={'1':['C272','C273'],'4':['C272','C26E'],'10':['C272','C270'],'11':['C272','C26F'],'19':['C272','C271']})
    profiles=mode['profile_semantics']
    check('signal254 accepted profiles share common active flag',profiles['common_active_flag']=='C272 is asserted for every accepted value')
    check('signal254 profile flags are mutually exclusive',profiles['mutually_exclusive_profile_flags']=={'1':'C273','4':'C26E','10':'C270','11':'C26F','19':'C271'})
    check('signal254 profiles select separate calibration banks','distinct calibration banks' in profiles['calibration_selection'])
    check('signal254 exact OEM feature labels close',profiles['oem_dictionary_name']=='Target Lateral ID' and profiles['oem_feature_labels']=={'1':'PCS','4':'LDA','10':'Hands Off LTA','11':'LTA/LCA','19':'PDA'})
    check('raw 25/27 special pair gets OEM labels','raw IDs 25 (0x19) and 27 (0x1B)' in profiles['additional_raw_id_use'] and 'AP and Remote Parking' in profiles['additional_raw_id_use'] and 'Only 25/AP' in profiles['additional_raw_id_use'])
    check('signal254 OEM join proof exact','1 PCS, 4 LDA, 10 Hands Off LTA, 11 LTA/LCA, 19 PDA, 25 AP, 27 Remote Parking' in profiles['join_proof'] and 'NA/EU/JP' in profiles['join_proof'])
    check('signal254 literal wire-name boundary retained','literal on-wire field name' in mode['boundary'] and 'feature labels' in mode['boundary'])
    check('B6 is protected FD PDU42',w['can_id']=='0x0B6' and w['can_fd'] and w['secured'] and w['pdu_id']==42 and w['pdu_buffer_offset']=='0x01A7')
    check('signal255 is signed16 B4:B5',w['signal_id']==255 and w['wire_byte']==4 and w['bit_length']==16 and w['signed'])
    check('wire->raw->stage->snapshot exact',w['raw_destination']=='0xFEBE7D94' and w['staging_destination']=='0xFEBEF1CC' and w['snapshot_destination']=='0xFEBEAE82')
    check('three ingress functions exact',w['unpacker']=='0x00046A10' and w['staging_copy']=='0x0005262C' and w['gp_relative_snapshot_copy']=='0x000B8EEC')
    check('wire classification is target steering angle',w['classification']=='authenticated-signed16-target-steering-angle-command')
    print('\n== target vs measured control proof ==')
    t=d['target_angle_pipeline']; m=d['measured_angle_feedback']
    check('target starts at C9DB0',t[0]['entry']=='0x000C9DB0' and 'AE82 * 2' in t[0]['relation'])
    check('target replication/rate-limit at C9E54',t[1]['entry']=='0x000C9E54' and 'C098/C100/C120' in t[1]['relation'])
    check('matched target-vs-measured comparator at CA138',t[2]['entry']=='0x000CA138' and 'scaled_target - scaled_measured' in t[2]['relation'])
    check('actual feedback is FD025 184/185/186',m['source_can_id']=='0x025' and m['source_signals']==[184,185,186])
    check('actual snapshots exact',m['snapshots']=={'184':'0xFEBEADF0','185':'0xFEBEACC5','186':'0xFEBEAE14'})
    check('actual reconstruction exact constants', '0x6FB / 0x200' in m['reconstruction'] and 'fraction + coarse*15' in m['reconstruction'])
    wr=m['wire_representation']
    check('FD025 signal184 exact coarse-angle scale',wr['signal184']=={'bits':12,'signed':True,'role':'coarse steering angle','techstream_did':'0x1037','techstream_name':'Steering Angle','physical_scale_deg_per_count':1.5})
    check('FD025 signal185 exact signed fraction scale',wr['signal185']=={'bits':4,'signed':True,'role':'signed fractional steering angle','physical_scale_deg_per_count':0.1})
    check('FD025 combined angle is tenths of degree',wr['combined']=='15 * signal184 + signal185' and wr['combined_unit']=='0.1 deg' and wr['full_turn_counts']==3600 and 'divides that combined count by 3600' in wr['proof'])
    check('same comparator gain recorded', 'same 0xB76/0x400 gain' in m['comparison'])
    check('independent target-vs-measured loop asserted',m['classification']=='independent-target-versus-measured-steering-angle-control-loop')
    check('active controller follows comparator',t[3]['entry']=='0x000CAC24/0x000CA940')
    check('decoded cooperative mode gates controller',t[4]['entry']=='0x000CAD1C' and 'C272' in t[4]['relation'])
    check('controller reaches replicated magnitude',t[5]['entry']=='0x000CC18E -> 0x000CC2EC -> 0x000CAD62')
    check('replicated magnitude reaches C2A8',t[6]['entry']=='0x000C9C16 -> 0x000CB8BA -> 0x000CB9B6' and 'C2A8' in t[6]['relation'])
    check('C2A8 reaches general torque composition',t[7]['entry']=='0x000CD3CC' and 'C3B8' in t[7]['relation'])
    fb=d['final_command_bridge']
    check('target contribution reaches 1C02 bridge','C2A8' in fb['local_chain'] and 'C3D2' in fb['local_chain'] and fb['recovered'])
    check('final observer is Command Value Torque',fb['techstream_command_torque']=={'did':'0x1C02','name':'Command Value Torque','unit':'Nm'})
    check('final q-current observer is 1152',fb['q_axis_command']=={'did':'0x1152','name':'Command Value Current (Q Axis)','unit':'A'})
    check('general-command boundary retained','one conditional contributor' in fb['boundary'])
    check('independent AE82 safety/plausibility consumer',d['independent_safety_consumer']['entry']=='0x000CB4F4' and d['independent_safety_consumer']['source']=='0xFEBEAE82')
    print('\n== scaling boundary ==')
    s=d['scaling']
    check('internal target x2 relation exact','2 * signed16(B6 B4:B5)' in s['exact_internal_relation'])
    check('internal measured relation exact','15*FD025_coarse' in s['exact_internal_relation'] and '1787 / 512' in s['exact_internal_relation'])
    check('physical degree scale closed',s['physical_degree_scale_closed'] is True and s['controller_equivalent_fraction_deg_per_b6_count']=={'numerator':1024,'denominator':17870})
    check('controller-equivalent degree value exact enough',abs(s['controller_equivalent_deg_per_b6_count']-(1024/17870))<1e-15)
    check('controller-equivalent scale is ~1 mrad/count',abs(s['controller_equivalent_mrad_per_b6_count']-1.0001215187701138)<1e-12 and abs(s['difference_from_exact_1_mrad_percent']-0.01215187701137932)<1e-12)
    check('OEM B6 engineering-unit name remains open',s['oem_wire_unit_name_closed'] is False and 'does not directly name' in s['interpretation'])
    check('scale keeps integer quantization boundary','integer truncation' in s['quantization_boundary'] and 'exact linearized conversion' in s['quantization_boundary'])
    print('\n== independent Techstream context ==')
    ts=d['techstream']
    check('B6 sender DTC is U012987',ts['immediate_sender_monitor']['dtc']=='U012987')
    check('B6 sender is Brake System Control Module',ts['immediate_sender_monitor']['description']=='Lost Communication with Brake System Control Module' and ts['immediate_sender_monitor']['failure']=='Missing Message')
    check('Corolla P5 topology includes EMPS Brake/EPB FRC',ts['corolla_p5_topology']['required_categories']==[405,435,498] and ts['corolla_p5_topology']['names']=={'405':'EMPS','435':'Brake/EPB','498':'Front Recognition Camera 2'})
    check('P5 target-angle names corroborate domain',[x['name'] for x in ts['family_angle_vocabulary']]==['Target Steering Angle After Output Compensation','Advanced Drive Target Steering Angle'])
    check('P5 target-angle family uses 1CEE',all(x['primary_data_id']=='0x1CEE' for x in ts['family_angle_vocabulary']))
    check('Target Lateral ID dictionary joins H signal254',ts['target_lateral_id_dictionary']=={'name':'Target Lateral ID','accepted_h_profile_labels':{'1':'PCS','4':'LDA','10':'Hands Off LTA','11':'LTA/LCA','19':'PDA'},'special_h_ids':{'25':'AP','27':'Remote Parking'},'pattern_display_key':39})
    check('DID1037 conversion joins H measured angle',ts['steering_angle_conversion']=={'did':'0x1037','name':'Steering Angle','h_callback':'0x488A8','raw_scale':'1.5 deg/count','physical_data_key':3,'conversion_plugin':'GetDatMonSignalInfoP5_DT.dll'})
    check('exact H target observer name not overclaimed','exact H lacks DID 0x1CEE' in ts['vocabulary_boundary'] and 'OEM engineering-unit name' in ts['vocabulary_boundary'])
    print('\n== generation migration ==')
    mig=d['migration']
    check('older Corolla was torque command','0x2E4' in mig['pre_tss3_corolla'] and 'torque' in mig['pre_tss3_corolla'])
    check('Sienna angle prior art kept separate','0x131' in mig['sienna_secoc_prior_art'] and 'different wire' in mig['sienna_secoc_prior_art'])
    check('H/F migration is B6 target angle','0x0B6' in mig['corolla_h_f'] and 'target-angle' in mig['corolla_h_f'])
    check('no wire compatibility overclaim','none claimed' in mig['wire_compatibility'])
    print('\n== static conclusion ==')
    c=d['static_conclusion']
    check('external lateral ingress identified',c['external_autonomous_lateral_ingress_identified'] is True)
    check('ingress exact B6 signal255',c['ingress']=='protected CAN-FD 0x0B6 signal255 signed16 B4:B5')
    check('command domain angle not torque',c['command_domain']=='target steering angle' and c['torque_command'] is False)
    check('mode ingress exact B6 signal254',c['mode_ingress']=='protected CAN-FD 0x0B6 signal254 6-bit B3')
    check('wire target reaches torque/current chain',c['reaches_command_value_torque_and_q_current'] is True)
    check('immediate sender relationship brake',c['immediate_sender_relationship']=='Brake System Control Module')
    check('upstream feature producer still open',c['upstream_feature_producer_identified'] is False)
    check('physical controller-equivalent scale identified',c['physical_scale_identified'] is True and abs(c['controller_equivalent_deg_per_count']-(1024/17870))<1e-15)
    check('OEM wire unit name remains open',c['oem_wire_unit_name_identified'] is False)
    check('signal254 feature labels are identified',c['signal254_feature_labels_identified'] is True and c['signal254_profile_labels']=={'1':'PCS','4':'LDA','10':'Hands Off LTA','11':'LTA/LCA','19':'PDA'})
    check('receiver request/loss/sequence contract promoted',c['request_selection_identified'] is True and c['receiver_loss_cutout_ticks']==7 and c['wall_clock_timeout_identified'] is True and c['sequence_counter_identified'] is True and c['sequence_modulus']==64 and c['sequence_gap_cap']==8)
    check('next target is upstream producer, stock template and signing path','FRC_P5 -> Brake/EPB' in c['next_static_target'] and 'stock B6 cadence' in c['next_static_target'] and 'production signing/suppression path' in c['next_static_target'] and 'replacement freshness' in c['next_static_target'])


def _section_can_com():
    print('== can com ==')
    """Verify Corolla H changed CAN/COM role recovery and configured routing."""
    import hashlib,json,struct
    from pathlib import Path
    ROOT=Path(__file__).resolve().parents[1]
    ART=ROOT/'data/generated/corolla_8965H1202000_can_com.json';EV=ROOT/'data/generated/corolla_8965H1202000_can_com_decompiler_evidence.json';BUILD=ROOT/'tools/build_corolla_h_can_com.py'
    HRAW=ROOT/'community/albinoelephant/raw-20260818/albinoelephant-corolla-2023.20260814-0023/dump_codeflash_00000000_00200000_20260814-025814.bin';SIMG=ROOT/'firmware/RH850_P1M-E_CodeFlash.bin'
    a=json.loads(ART.read_text());e=json.loads(EV.read_text());H=HRAW.read_bytes()[:0x100000];S=SIMG.read_bytes()
    print('== deterministic artifact ==')
    print('\n== compact evidence ==')
    check('H image hash pinned',sha(H)==e['image']['codeflash_sha256']==a['images']['h_sha256']);check('19 H functions compacted',e['function_count']==19==len(e['functions']))
    check('all raw H bodies validate',all(sha(H[int(x['entry'],16):int(x['entry'],16)+x['body_size']])==x['body_sha256'] for x in e['functions']))
    check('all H decompiler hashes validate',all(sha(x['decompiled_c'].encode())==x['decompiled_c_sha256'] for x in e['functions']))
    print('\n== nine role mappings ==')
    exp={'0x0005D3CE':'0x00058450','0x0005DB6E':'0x00058BBC','0x00069DEC':'0x0006418C','0x0007C640':'0x00076A3C','0x0007E30C':'0x00078708','0x0007E5F2':'0x000789EE','0x0007F002':'0x000793FE','0x00080992':'0x0007AD8E','0x00084710':'0x0007EB10'}
    check('all nine changed can_com roles recovered',a['can_com_role_closure_count']==9 and {x['reference_entry']:x['target_entry'] for x in a['can_com_role_closure']}==exp)
    g=a['rx_dispatch_groups'];check('group B guard schedule is identical 29/29',g['group_b']['sienna_guard_count']==g['group_b']['h_guard_count']==29 and g['group_b']['guard_diff']==[])
    check('group A is 97->96 with one nested guard deletion',g['group_a']['sienna_guard_count']==97 and g['group_a']['h_guard_count']==96 and len(g['group_a']['guard_diff'])==1 and g['group_a']['guard_diff'][0]['sienna']==['if (uVar != 0) {'] and g['group_a']['guard_diff'][0]['h']==[])
    d=a['deadline_monitor_c'];check('deadline monitor body is exact at active H 6418C',d['exact_body_equal'] and H[0x6418C:0x6462A]==S[0x69DEC:0x6A28A])
    check('deadline body ambiguity is explicit',d['h_exact_body_occurrences']==['0x0006418C','0x000CF27E'])
    check('active H monitor caller disambiguates 6418C',d['active_h_caller']=='0x0003E118' and d['active_h_caller_invokes_6418c'])
    print('\n== configured transport table proofs ==')
    for row in a['configuration_pointer_proofs']:
     sa=int(row['sienna_pointer_at'],16);ha=int(row['h_pointer_at'],16)
     check('table '+row['role'],struct.unpack_from('<I',S,sa)[0]==int(row['sienna_target'],16) and struct.unpack_from('<I',H,ha)[0]==int(row['h_target'],16))
    by={int(x['entry'],16):x for x in e['functions']}
    check('H COM RxIndication retains full 212-byte copy/filter/timeout body',by[0x76A3C]['body_size']==212 and all(t in by[0x76A3C]['decompiled_c'] for t in ('& 0x10','& 8','& 4','*pbVar1 = *pbVar1 & 0xdc','FUN_00087a82(param_1)')))
    check('H PduR COM transmit wrapper remains 26 bytes',by[0x7AD8E]['body_size']==26 and 'PTR_LAB_00021c70' in by[0x7AD8E]['decompiled_c'])
    check('H CanIf Tx-ID class decoder retains six classes',all(t in by[0x789EE]['decompiled_c'] for t in ('0x6000','0x800','0xb800','0xc000','0xf800')))
    check('H CanIf Tx confirmation retains six class dispatch',all(t in by[0x793FE]['decompiled_c'] for t in ('0x6000','0x800','0xb800','0xc000','0xf800')))
    check('H RSCFD confirmation is called by Tx interrupt body', 'FUN_0007eb10' in by[0x7EB4E]['decompiled_c'])
    check('H normal Rx demux terminates at PduR route adapter', 'FUN_0007b026' in by[0x7A402]['decompiled_c'] and struct.unpack_from('<I',H,0x21C90)[0]==0x7B040)
    check('report keeps PDU membership in separate topology owner','individual PDU membership' in a['static_conclusion']['boundary'])


def _section_crypto_residue():
    print('== crypto residue ==')
    """Verify target-native recovery of the final seven H crypto roles."""
    import hashlib,json
    from pathlib import Path
    ROOT=Path(__file__).resolve().parents[1]
    ART=ROOT/'data/generated/corolla_8965H1202000_crypto_residue.json';EV=ROOT/'data/generated/corolla_8965H1202000_crypto_residue_decompiler_evidence.json';BUILD=ROOT/'tools/build_corolla_h_crypto_residue.py';HRAW=ROOT/'community/albinoelephant/raw-20260818/albinoelephant-corolla-2023.20260814-0023/dump_codeflash_00000000_00200000_20260814-025814.bin'
    a=json.loads(ART.read_text());e=json.loads(EV.read_text());H=HRAW.read_bytes()[:0x100000];by={int(x['target_entry'],16):x for x in e['functions']}
    check('H image hash pinned',sha(H)==e['image']['codeflash_sha256']==a['images']['h_sha256']);check('seven crypto roles compacted',e['function_count']==7==len(e['functions'])==a['crypto_role_closure_count']);check('all raw H bodies validate',all(sha(H[int(x['target_entry'],16):int(x['target_entry'],16)+x['target_reported_body_size']])==x['body_sha256'] for x in e['functions']));check('all decompiler hashes validate',all(sha(x['decompiled_c'].encode())==x['decompiled_c_sha256'] for x in e['functions']))
    exp={'0x000070FC':'0x000070E0','0x00068F0C':'0x00063244','0x00068F92':'0x000632CA','0x00068FC2':'0x000632FA','0x00069018':'0x00063350','0x00088302':'0x00082702','0x00088508':'0x00082908'};check('all seven role mappings exact', {x['reference_entry']:x['target_entry'] for x in a['crypto_role_closure']}==exp)
    pf=a['payload_crypto_finalize'];check('payload finalize is exact 12-byte relocated wrapper',pf['exact_body_equal'] and pf['body_size']==12 and pf['h']=='0x000070E0');check('payload finalize is role-bound by relocated clear call',pf['h_calls_clear'] and pf['clear_delta']==-0x1c and 'FUN_000070c8' in by[0x70e0]['decompiled_c'])
    b=a['crypto_test_banks'];check('bank0 preserves eight-counter snapshot',b['bank0']['snapshot']['h_counter_indices']==list(range(10,18)) and b['bank0']['snapshot']['sienna_counter_indices']==list(range(12,20)));check('bank1 preserves five-counter snapshot',b['bank1']['snapshot']['h_counter_indices']==list(range(18,23)) and b['bank1']['snapshot']['sienna_counter_indices']==list(range(20,25)));check('both H counter cohorts shift by -2',b['bank0']['index_shift']==[-2]*8 and b['bank1']['index_shift']==[-2]*5);check('bank0 activation keeps active/state 0x11 lifecycle',all(t in by[0x632ca]['decompiled_c'] for t in ('cRamfebe4f82','uRamfebe4f83 = 0x11','FUN_00062214','FUN_0006224c(1)','direct_call_target_00063244')));check('bank1 activation keeps active/state 0x11 lifecycle',all(t in by[0x63350]['decompiled_c'] for t in ('cRamfebe4f87','uRamfebe4f88 = 0x11','FUN_00062282','direct_call_target_000632fa')));check('counter-number transfer is explicitly rejected','do not transfer Sienna counter numbers' in b['interpretation'])
    dr=a['driver_record_lookup'];check('generate driver lookup is two records stride 0x20',dr['generate']['h']=='0x00082702' and dr['generate']['record_count']==2 and dr['generate']['record_stride']==0x20 and '0x27c88' in by[0x82702]['decompiled_c']);check('generic driver lookup is two records stride 0x20',dr['verify_generic']['h']=='0x00082908' and dr['verify_generic']['record_count']==2 and dr['verify_generic']['record_stride']==0x20 and '0x27ccc' in by[0x82908]['decompiled_c']);check('driver lookup pair remains -0x5C00',dr['delta']==-0x5c00)
    sc=a['static_conclusion'];check('all seven crypto residual roles closed',sc['all_7_crypto_residual_roles_recovered'] and sc['crypto_named_residue_closed']);check('target-specific generated-state boundary remains explicit','target-specific' in sc['boundary'])


def _section_deadline_monitor_surface():
    print('== deadline monitor surface ==')
    """Verify complete target-surface closure of Corolla-H deadline-monitor callbacks."""
    import hashlib,json
    from pathlib import Path
    ROOT=Path(__file__).resolve().parents[1];ART=ROOT/'data/generated/corolla_8965H1202000_deadline_monitor_surface.json';EV=ROOT/'data/generated/corolla_8965H1202000_deadline_monitor_surface_decompiler_evidence.json';TOOL=ROOT/'tools/build_corolla_h_deadline_monitor_surface.py';RAW=ROOT/'community/albinoelephant/raw-20260818/albinoelephant-corolla-2023.20260814-0023/dump_codeflash_00000000_00200000_20260814-025814.bin'
    d=json.loads(ART.read_text());e=json.loads(EV.read_text());raw=RAW.read_bytes()[:0x100000]
    check('H image hash pinned',sha(raw)==e['image']['codeflash_sha256'])
    check('91 H functions compacted: 88 callbacks + 3 support',e['function_count']==91 and e['callback_count']==88 and e['support_count']==3)
    check('all raw H bodies validate',all(sha(raw[int(r['entry'],16):int(r['entry'],16)+r['body_size']])==r['body_sha256'] for r in e['functions']))
    check('all decompiler hashes validate',all(sha(r['decompiled_c'].encode())==r['decompiled_c_sha256'] for r in e['functions']))
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
    check('no one-to-one callback naming is claimed','not assigned Sienna callback names one-to-one' in d['summary']['boundary'])


def _section_diagnostic_residue():
    print('== diagnostic residue ==')
    """Verify closure of the remaining Corolla-H named diagnostic residue."""
    import hashlib,json
    from pathlib import Path
    ROOT=Path(__file__).resolve().parents[1];ART=ROOT/'data/generated/corolla_8965H1202000_diagnostic_residue.json';EV=ROOT/'data/generated/corolla_8965H1202000_diagnostic_residue_decompiler_evidence.json';TOOL=ROOT/'tools/build_corolla_h_diagnostic_residue.py';RAW=ROOT/'community/albinoelephant/raw-20260818/albinoelephant-corolla-2023.20260814-0023/dump_codeflash_00000000_00200000_20260814-025814.bin'
    d=json.loads(ART.read_text());e=json.loads(EV.read_text());raw=RAW.read_bytes()[:0x100000];by={int(r['entry'],16):r for r in e['functions']}
    check('H image hash pinned',sha(raw)==e['image']['codeflash_sha256'])
    check('53 target-native functions compacted',e['function_count']==53==len(e['functions']))
    check('all raw H bodies validate',all(sha(raw[int(r['entry'],16):int(r['entry'],16)+r['body_size']])==r['body_sha256'] for r in e['functions']))
    check('all decompiler hashes validate',all(sha(r['decompiled_c'].encode())==r['decompiled_c_sha256'] for r in e['functions']))
    check('27 diagnostic roles recovered',d['diagnostic_role_closure_count']==27)
    check('32 canonical rows closed by complete recensus',d['diagnostic_surface_recensus_count']==32)
    check('all 59 residual names accounted once',d['diagnostic_role_closure_count']+d['diagnostic_surface_recensus_count']==59)
    w=d['wdbi'];check('S WDBI has 13 entries',w['sienna_table']['count']==13);check('H WDBI has 12 entries',w['h_table']['count']==12)
    check('H removes only DID 200D',w['removed_dids']==['0x200D'] and not w['added_dids'])
    check('H WDBI table base is 25530',w['h_table']['base']=='0x00025530' and w['start_lookup']['h_table_base']=='0x00025530')
    check('H lookup bound is 12 in both phases',w['start_lookup']['h_count']==12==w['result_lookup']['h_count'])
    check('2013 and 2014 are disabled on H',w['disabled_on_h']==['0x2013','0x2014'])
    for did,start,result in [('0x2013',0x4A8B8,0x4A8BC),('0x2014',0x4A8C0,0x4A8C4)]:
     check(f'{did} start returns 5', 'return 5;' in by[start]['decompiled_c'])
     check(f'{did} result is no-op success', 'return 0;' in by[result]['decompiled_c'] and by[result]['body_size']==4)
    check('2012 remains unconditional-start',w['h_2012_unconditional_start'] and by[0x4A89A]['body_size']==4)
    check('2012 result still reaches target lifecycle helper','thunk_FUN_000b2b6e' in by[0x4A89E]['decompiled_c'])
    check('0204 maintains pending 2E10 behavior','0x2e10' in by[0x4A686]['decompiled_c'])
    check('WDBI request start maps to exact-size H 8EB7C',by[0x8EB7C]['body_size']==136)
    check('WDBI callback maps to exact-size H 8EC88',by[0x8EC88]['body_size']==36)
    check('session policy preserves session-2 speed gate',d['session']['policy']['requested_session_2_speed_gate'])
    check('session request family maps all four lifecycle roles',len(d['session']['request_family'])==4)
    check('RoutineControl generic helpers map all four roles',len(d['routine_control']['helpers'])==4)
    check('request-start retains H RID count source',d['routine_control']['h_rid_count_source']=='DAT_00026376')
    check('all 59 diagnostic residuals closed',d['static_conclusion']['all_59_diagnostic_residuals_closed'])
    check('fake WDBI homologs explicitly rejected','fake homologs' in d['static_conclusion']['boundary'])


def _section_direct_call_surface():
    print('== direct call surface ==')
    import csv,hashlib,json,subprocess,sys,tempfile
    from pathlib import Path
    ROOT=Path(__file__).resolve().parents[1];EVID=ROOT/'data/generated/corolla_8965H1202000_direct_call_surface_evidence.json';ART=ROOT/'data/generated/corolla_8965H1202000_direct_call_surface.json';TOOL=ROOT/'tools/build_corolla_h_direct_call_surface.py';HRAW=ROOT/'community/albinoelephant/raw-20260818/albinoelephant-corolla-2023.20260814-0023/dump_codeflash_00000000_00200000_20260814-025814.bin';LEDGER=ROOT/'data/semantic_coverage_ledger.csv';p=f=0
    e=json.loads(EVID.read_text());d=json.loads(ART.read_text());h=HRAW.read_bytes()[:0x100000]
    check('evidence image hash pinned',e['image']['codeflash_sha256']==sha(h))
    check('clean H corpus cardinality pinned',e['summary']['function_count']==5425 and e['summary']['instruction_count']==159192)
    check('all 5425 raw contiguous bodies validate',all(sha(h[int(r['entry'],16):int(r['entry'],16)+r['body_size']])==r['body_sha256'] for r in e['functions']))
    entries={int(r['entry'],16) for r in e['functions']};edges=[int(t,16) for r in e['functions'] for t in r['direct_call_targets']]
    check('literal-call edge/target counts pinned',len(edges)==9509 and len(set(edges))==5151)
    check('all in-image literal call targets resolve to clean H function entries',all(t>0xfffff or t in entries for t in edges) and e['summary']['missing_in_image_literal_call_targets']==[] and e['summary']['closed'])
    rows=list(csv.DictReader(LEDGER.open()));seeds=[r for r in rows if r['name'].startswith('direct_call_target_') and r['discovery_source']=='direct-call seed' and r['discovery_provenance']=='SeedDirectCallTargets.java']
    check('canonical direct-call-seed provenance cohort is exactly 153',len(seeds)==153 and d['canonical_direct_call_seed_count']==153)
    check('recensus covers exactly the canonical generic seed names',{x['reference_name'] for x in d['surface_recensus']}=={r['name'] for r in seeds})
    check('provenance-only boundary explicit','not semantic identity' in d['static_conclusion']['boundary'] and 'no one-to-one behavior' in d['static_conclusion']['boundary'])


def _section_fd_control():
    print('== fd control ==')
    """Verify the 8965H1202000 FD/control-interface comparison."""

    import json
    from pathlib import Path

    REPO = Path(__file__).resolve().parents[1]
    ART = REPO / "data/generated/corolla_8965H1202000_fd_control_interface.json"
    EVIDENCE = REPO / "data/generated/corolla_8965H1202000_fd_control_decompiler_evidence.json"
    REFS = REPO / "data/generated/corolla_8965H1202000_fd_control_reference_census.json"
    STATE_EVIDENCE = REPO / "data/generated/corolla_8965H1202000_openpilot_state_bridge_decompiler_evidence.json"
    TOOL = REPO / "tools/build_corolla_h_fd_control_interface.py"


    d = json.loads(ART.read_text())
    check("FD/control schema v2", d["schema"] == "corolla-8965H1202000-fd-control-interface-v2")
    print("\n== FD receive generation ==")
    fd = d["fd_receive_generation"]
    check("Sienna FD Rx set is 025/090/D7", [x["can_id"] for x in fd["sienna_fd_rx"]] == ["0x025", "0x090", "0x0D7"])
    check("H FD Rx set adds only B6", [x["can_id"] for x in fd["corolla_h_fd_rx"]] == ["0x025", "0x090", "0x0D7", "0x0B6"])
    check("025 is explicitly classified as shared rather than H replacement",
          fd["shared_0x025_boundary"]["classification"] == "shared-preexisting-fd-interface-not-h-replacement")
    check("025 unpacker/producer/4A3 packer all have unique complete-shape transfers",
          len(fd["shared_0x025_boundary"]["unique_instruction_shape_pairs"]) == 3)
    check("H 025 signed12 field is still mirrored into 4A3 B1/B2",
          fd["shared_0x025_boundary"]["corolla_h_signed12_signal_184"]["directly_repacked_to_can_0x4A3_bytes"] == [1, 2])

    print("\n== secured FD B6 field roles ==")
    b6 = d["secured_fd_0x0b6"]
    check("B6 has 16 configured IDs but 12 scalar extracts",
          (len(b6["configured_signal_ids"]), len(b6["scalar_extracted_signal_ids"])) == (16, 12))
    check("B6 configured non-scalar IDs are 252/253/266/267",
          b6["configured_without_recovered_scalar_extract"] == [252, 253, 266, 267])
    by = {row["signal_id"]: row for row in b6["fields"]}
    check("B6 signal254 is 6-bit B3 mode/control ID", not by[254]["signed"] and by[254]["bit_length"] == 6 and by[254]["wire_byte"] == 3 and by[254]["snapshot_destination"] == "0xFEBEADB0" and by[254]["role"] == "target-lateral-control-id-mode-selector" and by[254]["direct_consumers"] == ["0xCBE6E"])
    check("B6 signal255 is signed16 at wire byte4", by[255]["signed"] and by[255]["bit_length"] == 16 and by[255]["wire_byte"] == 4)
    check("B6 signed16 field reaches AE82 target-angle snapshot",
          by[255]["role"] == "signed16-target-steering-angle-command" and by[255]["snapshot_destination"] == "0xFEBEAE82")
    check("B6 signed16 target-angle consumers are explicit", by[255]["direct_consumers"] == ["0xC86E8","0xC87FC","0xC9DB0","0xCB4F4"])
    check("B6 signed16 canonical result is target angle not torque", b6["signed16_target_angle_command"]["classification"] == "authenticated target-steering-angle command; not torque" and b6["signed16_target_angle_command"]["physical_scale_closed"] is True)
    check("B6 signed16 controller-equivalent scale is promoted", abs(b6["signed16_target_angle_command"]["controller_equivalent_deg_per_count"]-(1024/17870))<1e-15 and abs(b6["signed16_target_angle_command"]["controller_equivalent_mrad_per_count"]-1.0001215187701138)<1e-12 and b6["signed16_target_angle_command"]["oem_wire_unit_name_closed"] is False)
    check("B6 signal259 remains staging-only", by[259]["snapshot_destination"] is None)
    check("B6 signals256/257 reach snapshots but no recovered runtime consumer",
          all(by[x]["role"] == "snapshot-only-direct-xref-negative" for x in (256, 257)))
    check("B6 signal260 selects/ramp-controls mode tables", by[260]["role"] == "mode-table-selector" and "0xC89D2" in by[260]["direct_consumers"])
    check("B6 signal261 is a modulo/sequence delta input", by[261]["role"] == "modulo-sequence-delta" and by[261]["direct_consumers"] == ["0xCB246"])
    check("B6 8-bit signals262/263 are percentage-scaling inputs", by[262]["role"] == by[263]["role"] == "percentage-scaling")
    check("B6 signal264 is a validity/reset gate", by[264]["role"] == "validity-reset-gate")
    check("B6 signal265 is validity-gated mode/status", by[265]["role"] == "validity-gated-mode-status")
    check("active B6 consumers have target-native CEDAE paths where expected",
          all(by[x]["paths_from_0xCEDAE"][next(iter(by[x]["paths_from_0xCEDAE"]))] is not None for x in (258, 261, 262, 263, 264, 265)))
    check("B6 target-angle canonical proof linked", b6["signed16_target_angle_command"]["canonical_proof"] == "data/generated/corolla_8965H1202000_b6_target_angle_ingress.json" and b6["signed16_target_angle_command"]["physical_scale_closed"] is True)

    print("\n== Sienna-shaped steering-branch corrections ==")
    corr = d["sienna_shaped_branch_corrections"]
    check("AE20 is classified as internal-fed monitor/status branch", "monitor/status" in corr["old_2e4_monitor_branch"]["classification"])
    clamp = corr["retained_torque_clamp_branch"]
    check("retained H clamp input is AE12", clamp["input"] == "0xFEBEAE12")
    check("H clamp staging source is F166", clamp["upstream_staging"] == "0xFEBEF166")
    check("both recovered direct writers zero the clamp staging cell", len(clamp["direct_writer_census"]) == 2 and all("writes zero" in x for x in clamp["direct_writer_census"]))
    check("clamp branch is bounded as zero-source retained framework", "zero source" in clamp["classification"])

    print("\n== FD030 transmit generation ==")
    tx = d["fd_0x030_transmit"]
    check("H Tx replaces 260/262 with FD030", tx["sienna_tx_ids"][:2] == ["0x260", "0x262"] and tx["corolla_h_tx_ids"][0] == "0x030")
    check("FD030 is 32-byte cycle/tick 2", tx["pdu0_descriptor"] == {"cycle_or_timeout": 2, "flags": 3, "length": 32})
    check("FD030 owns configured signal IDs 0..36", tx["configured_signal_ids"] == list(range(37)))
    check("packer directly writes only signals 0..34", tx["direct_packer_signal_ids"] == list(range(35)))
    check("configured signals35/36 have no recovered direct pack call", tx["configured_without_recovered_direct_pack_call"] == [35, 36])
    check("signal9 is exact first-seven-byte additive field plus 0x38",
          tx["checksum_like_signal_9"]["formula"] == "sum(payload_bytes_0_through_6) + 0x38, low byte")
    classes = {row["writer_class"] for row in tx["fields"]}
    check("FD030 writer census distinguishes direct, GP-relative, constant-zero and computed fields",
          {"runtime-produced", "runtime-produced-gp-relative", "runtime-constant-zero-direct-writer-census", "computed-first-seven-byte-additive-field-plus-0x38"} <= classes)
    check("FD030 no longer has false default-init-only fields", "default-init-only-direct-writer-census" not in classes)
    gp = tx["gp_relative_writer_correction"]
    expected_gp = [0, 1, 10, 14, 16, 17, 18, 27, 28, 31, 34]
    check("FD030 GP-relative correction covers exact eleven signals", gp["affected_signal_ids"] == expected_gp)
    rows = {row["signal_id"]: row for row in tx["fields"]}
    check("all corrected signals have exact runtime GP-relative writers", all(rows[x]["writer_class"] == "runtime-produced-gp-relative" for x in expected_gp))
    check("signals 0/10/31 are the recovered driver-torque encoding family", all("driver-steering-torque" in rows[x]["recovered_semantic"] for x in (0, 10, 31)))
    check("signal34 is Q-current-derived", "Motor Actual Current (Q Axis)" in rows[34]["recovered_semantic"] and "calibration-dependent" in rows[34]["recovered_semantic"])
    print("\n== compact evidence binding ==")
    e = json.loads(EVIDENCE.read_text()); r = json.loads(REFS.read_text()); se = json.loads(STATE_EVIDENCE.read_text())
    check("FD/control evidence is exact H image-bound", e["software_id"] == "8965H1202000" and e["image"]["sha256"] == d["images"]["corolla_h_sha256"])
    check("compact function evidence contains 56 target-native functions", e["function_count"] == 56)
    check("GP-relative writer evidence is exact H-bound steering evidence", se["schema"] == "corolla-h-openpilot-state-bridge-decompiler-evidence-v2" and se["function_count"] == 26 and {"0x00047188", "0x00047430"} <= {x["entry"] for x in se["functions"]})
    check("FD report pins steering evidence hash/count", d["evidence"]["state_bridge_function_count"] == 26)
    check("GP correction preserves arbitrary-computed-pointer boundary", "does not upgrade" in gp["boundary"] and "computed-pointer" in r["evidence_boundary"])
    check("direct-reference census records its computed-pointer boundary", "computed-pointer" in r["evidence_boundary"])
    check("reference census covers at least 70 explicit terms", len(r["terms"]) >= 70)


def _section_final_named_residue():
    print('== final named residue ==')
    import hashlib,json
    from pathlib import Path
    ROOT=Path(__file__).resolve().parents[1]
    ART=ROOT/'data/generated/corolla_8965H1202000_final_named_residue.json'
    EVID=ROOT/'data/generated/corolla_8965H1202000_final_named_residue_evidence.json'
    TOOL=ROOT/'tools/build_corolla_h_final_named_residue.py'
    SRAW=ROOT/'firmware/RH850_P1M-E_CodeFlash.bin'
    HRAW=ROOT/'community/albinoelephant/raw-20260818/albinoelephant-corolla-2023.20260814-0023/dump_codeflash_00000000_00200000_20260814-025814.bin'
    d=json.loads(ART.read_text());e=json.loads(EVID.read_text());s=SRAW.read_bytes();h=HRAW.read_bytes()[:0x100000]
    check('image hashes pinned',d['images']['sienna_sha256']==sha(s) and d['images']['h_sha256']==sha(h) and e['images']==d['images'])
    check('compact evidence raw-bound',all(sha((s if k=='sienna_fingerprints' else h)[int(r['entry'],16):int(r['entry'],16)+r['body_size']])==r['body_sha256'] for k in ('sienna_fingerprints','h_fingerprints') for r in e[k]))
    check('33 roles + one recensus close final 34',d['role_closure_count']==33 and d['surface_recensus_count']==1 and d['static_conclusion']['all_34_prior_unresolved_names_closed'])
    check('boot dispatcher transferred at -0x1C',d['claims']['boot_eiint']['dispatcher_target']=='0x0000072C' and d['claims']['boot_eiint']['dispatcher_shift']==-0x1c and s[0x730:0x770]==h[0x714:0x754])
    check('H boot EIINT table shrinks to 10BC/10C0/10C1/default',[x[0] for x in d['claims']['boot_eiint']['h_rows']]==['0x000010BC','0x000010C0','0x000010C1','0xFFFFFFFF'])
    check('boot TAUJ0 CH2 is removed, not remapped',d['surface_recensus']==[{'reason':'H complete boot EIINT table removes code 0x1087; H 0x1E5E belongs to code 0x10BC and must not be misidentified as TAUJ0 CH2','reference_entry':'0x00001E44','reference_name':'boot_tauj0_ch2_isr'}])
    check('boot exception handlers exact at -0x1C',s[0x1e1e:0x1e26]==h[0x1e02:0x1e0a] and s[0x1e2a:0x1e36]==h[0x1e0e:0x1e1a])
    roles={x['reference_name']:x['target_entry'] for x in d['role_closure']}
    check('CRC trio exact',roles['memory_crc_verify_result']=='0x000047C2' and roles['memory_crc_verify_busy']=='0x000047C8' and roles['crc32_hardware_compute']=='0x000047CE')
    check('application entry remains 20880',roles['application_entry']=='0x00020880')
    check('RAM policy maps to 4A4D4',roles['application_ram_range_allowed']=='0x0004A4D4' and d['claims']['ram_policy']['h_table']=='0x00028F0C')
    check('event-query cone exact',{n:roles[n] for n in ['application_event_record_query','application_event_active_id_list','application_event_state_query','application_event_detail_query']}=={'application_event_record_query':'0x0004AF74','application_event_active_id_list':'0x0004FE70','application_event_state_query':'0x0004FFD8','application_event_detail_query':'0x0005031A'})
    check('RMBA start/poll exact',roles['application_read_memory_by_address_request_start']=='0x0008F7C0' and roles['application_read_memory_by_address_request_poll']=='0x0008F720')
    check('proprietary AB workers exact',roles['application_proprietary_ab_selector_worker']=='0x0009193E' and roles['application_proprietary_ab_event_worker']=='0x00087384')
    check('RTE copy trio exact',[roles[x] for x in ['rte_input_staging_copy_c','rte_input_staging_copy_b','rte_input_staging_copy_a']]==['0x00056BAC','0x0005722E','0x0005778E'])
    check('application exception vectors exact',roles['application_default_exception_handler']=='0x0005C0F2' and roles['application_vector_0x90_handler']=='0x0005EE7E')
    check('changed generated successors pinned',roles['application_timer_peripheral_reload']=='0x0005F812' and roles['tauj0_ch0_sample_snapshot']=='0x0005FB30' and roles['fd0d7_status_fault_monitor']=='0x000B5EA4' and roles['application_input_snapshot_update']=='0x000BBA48')
    check('system/scheduler successors pinned',roles['application_rx_signal_consumer_56fc2']=='0x0005262C' and roles['application_ram_default_init']=='0x0005316C' and roles['application_substate_machine']=='0x000CF27E')
    check('shutdown/programming/timer targets pinned',roles['boot_shutdown_reset_path']=='0x0006A93E' and roles['application_programming_lower_request_stub']=='0x0008441C' and roles['application_programming_reset_marker_clear']=='0x000482AE' and roles['timer_expiry_07_callback']=='0x0008FBAC' and roles['system_programming_shutdown_mode_entry']=='0x000B1F68')
    check('zero-residue boundary does not overclaim','does not promote structural-only candidates' in d['static_conclusion']['boundary'])


def _section_lta_command_provenance():
    print('== lta command provenance ==')
    """Verify the exact-image Corolla H autonomous-lateral command provenance."""

    import hashlib
    import json
    from pathlib import Path

    REPO = Path(__file__).resolve().parents[1]
    ART = REPO / "data/generated/corolla_8965H1202000_lta_command_provenance.json"
    EVID = REPO / "data/generated/corolla_8965H1202000_lta_command_provenance_decompiler_evidence.json"
    TOOL = REPO / "tools/build_corolla_h_lta_command_provenance.py"
    IMAGE = REPO / "community/albinoelephant/normalized/8965H1202000_CodeFlash.bin"


    d = json.loads(ART.read_text())
    e = json.loads(EVID.read_text())
    image = IMAGE.read_bytes()

    print("\n== evidence identity ==")
    check("report is exact H image-bound", d["software_id"] == "8965H1202000" and d["images"]["corolla_h"]["sha256"] == hashlib.sha256(image).hexdigest())
    check("50 target-native functions support direct+computed provenance closure", e["function_count"] == 50)
    check("LTA report consumes tracked compact whole-corpus census", d["schema"] == "corolla-8965H1202000-lta-command-provenance-v8" and d["whole_corpus_census"]["path"] == "data/generated/corolla_8965H1202000_lta_command_provenance_census.json" and d["whole_corpus_census"]["source_function_count"] > 5000)
    for row in e["functions"]:
        start = int(row["entry"], 16); size = row["body_size"]
        check(f"raw body hash {row['entry']}", hashlib.sha256(image[start:start+size]).hexdigest() == row["body_sha256"])

    print("\n== retained Sienna-homolog branch: computed-writer correction ==")
    r = d["retained_lta_branch"]
    for addr in ("0xFEBEC17C", "0xFEBEC17E", "0xFEBEC184", "0xFEBEC26D"):
        cell = r["direct_symbol_observations"][addr]
        check(f"{addr} direct-symbol census retained as bounded observation", cell["direct_symbol_lhs_writes"] and cell["raw_u32_literal_pointer_hits"] == [])

    corr = r["computed_writer_correction"]
    check("direct-symbol-only census is explicitly marked incomplete", corr["direct_symbol_census_was_incomplete"] is True)
    mode = corr["mode_enable_0xFEBEC26D"]
    check("CC7F8 recovers GP-relative C26D writer", mode["writer"] == "0x000CC7F8" and mode["recovered"] and mode["selector_recovered"] and mode["health_aggregate_recovered"])
    check("health selectors 0x10/0x18 both use class2", mode["selector_slots"]["0x10"]["health_class"] == 2 and mode["selector_slots"]["0x18"]["health_class"] == 2)
    check("raw selector rows pinned", mode["selector_slots"]["0x10"]["raw_hex"] == "025a2300000bb801" and mode["selector_slots"]["0x18"]["raw_hex"] == "02002b00000bffff")
    mag = corr["replicated_magnitude_0xFEBEC17C_17E_184"]
    check("CC2EC->CAD62 recovers GP-relative magnitude triplet writers", mag["writer"] == "0x000CAD62" and mag["upstream_conditioner"] == "0x000CC2EC" and mag["recovered"])
    mods = {x["signal_id"]: x for x in corr["b6_modulators"]}
    check("B6 signal262 is 8-bit byte8 ADBD modifier", mods[262]["wire_byte"] == 8 and mods[262]["bit_length"] == 8 and mods[262]["snapshot"] == "0xFEBEADBD" and mods[262]["consumer"] == "0x000CC442" and mods[262]["recovered"])
    check("B6 signal263 is 8-bit byte9 ADBE modifier", mods[263]["wire_byte"] == 9 and mods[263]["bit_length"] == 8 and mods[263]["snapshot"] == "0xFEBEADBE" and mods[263]["consumer"] == "0x000CBFCE" and mods[263]["recovered"])
    check("base magnitude synthesis is target-native local state", corr["local_base_synthesis"]["entry"] == "0x000CC18E" and corr["local_base_synthesis"]["recovered"])
    check("C9C16 still recovers three-word magnitude vote/rate-limit", r["magnitude_vote_and_rate_limit"]["recovered"])
    check("mode decoder explicitly requires C26D==1", r["mode_enable"]["decoder_requires_one"])
    check("mode decoder initializes all outputs zero before gate", r["mode_enable"]["decoder_zeroes_all_outputs_when_gate_false"])
    check("retained command conditioning chain is recovered", all(x["recovered"] for x in r["command_conditioning"]))
    check("retained branch classification records live local B6-modulated path", r["classification"] == "retained-sienna-homolog-conditioner-live-b6-target-angle-driven-and-b6-modulated")

    print("\n== D7 hidden-payload census ==")
    d7 = d["d7_hidden_payload_census"]
    check("D7 SecOC profile is 32 bytes with 28-bit MAC and 4-bit transmitted freshness", d7["secured_length"] == 32 and d7["profile"]["authenticator_bits"] == 28 and d7["profile"]["transmitted_freshness_bits"] == 4)
    check("D7 carries 28 authenticated application bytes", d7["profile"]["security_trailer_bytes"] == 4 and d7["profile"]["authenticated_application_bytes"] == 28)
    check("D7 configured signal IDs are exactly 240..247", d7["com"]["configured_signal_ids"] == list(range(240,248)))
    check("D7 scalar receive IDs are exactly 240/243/246", d7["com"]["scalar_receive_ids"] == [240,243,246])
    check("D7 configured nonscalar IDs are 241/242/244/245/247", d7["com"]["configured_without_scalar_receive"] == [241,242,244,245,247])
    check("no D7 nonscalar ID is consumed by block/group API", d7["com"]["non_scalar_ids_used_by_block_group_api"] == [])
    check("full-PDU copy does not use D7/PDU40", d7["com"]["all_literal_full_pdu_ids"] == [0] and d7["com"]["d7_full_pdu_copy_present"] is False)
    check("D7 COM buffer has no raw absolute pointer literal", d7["com"]["buffer_address"] == "0xFEBE4ACC" and d7["com"]["raw_u32_buffer_pointer_hits"] == [])

    print("\n== B6 hidden-payload census ==")
    b = d["b6_hidden_payload_census"]
    check("B6 SecOC profile is 32 bytes with 28-bit MAC and 4-bit transmitted freshness", b["secured_length"] == 32 and b["profile"]["authenticator_bits"] == 28 and b["profile"]["transmitted_freshness_bits"] == 4)
    check("B6 therefore carries 28 authenticated application bytes", b["profile"]["security_trailer_bytes"] == 4 and b["profile"]["authenticated_application_bytes"] == 28)
    check("B6 configured signal IDs are exactly 252..267", b["com"]["configured_signal_ids"] == list(range(252,268)))
    check("B6 scalar receive IDs are exactly 254..265", b["com"]["scalar_receive_ids"] == list(range(254,266)))
    check("B6 configured nonscalar IDs are 252/253/266/267", b["com"]["configured_without_scalar_receive"] == [252,253,266,267])
    check("block/group receive calls resolve only unrelated IDs", b["com"]["all_literal_block_group_receive_ids"] == list(range(89,97)) + list(range(99,103)))
    check("no B6 nonscalar ID is consumed by block/group API", b["com"]["non_scalar_ids_used_by_block_group_api"] == [])
    check("full-PDU copy surface only uses PDU0", b["com"]["all_literal_full_pdu_ids"] == [0] and b["com"]["b6_full_pdu_copy_present"] is False)
    check("B6 COM buffer has no raw absolute pointer literal", b["com"]["buffer_address"] == "0xFEBE4AF4" and b["com"]["raw_u32_buffer_pointer_hits"] == [])
    check("Sienna 2E4 control also has nonscalar configured rows", b["sienna_2e4_control"]["configured_signal_ids"] == list(range(58,66)) and b["sienna_2e4_control"]["configured_without_scalar_receive"] == [64,65])

    print("\n== adversarial shared-large-field closure ==")
    sh = d["shared_can025_sensor_ingress"]
    support = d["supporting_inputs"]
    sup_path = REPO / support["supervisor_external_ingress_census"]["path"]
    check("supervisor external-ingress census identity is bound", hashlib.sha256(sup_path.read_bytes()).hexdigest() == support["supervisor_external_ingress_census"]["sha256"])
    dbc_path = REPO / sh["dbc"]["path"]
    check("pinned Toyota DBC identity is bound", hashlib.sha256(dbc_path.read_bytes()).hexdigest() == sh["dbc"]["sha256"])
    check("CAN025 is pinned as STEER_ANGLE_SENSOR", sh["can_id"] == "0x025" and sh["dbc"]["message"] == "STEER_ANGLE_SENSOR" and sh["dbc"]["message_id_decimal"] == 37)
    check("DBC coarse steering angle is signed12", sh["dbc"]["signals"]["STEER_ANGLE"] == {"start_bit_motorola":3,"bit_length":12,"signed":True})
    check("DBC steering fraction is signed4", sh["dbc"]["signals"]["STEER_FRACTION"] == {"start_bit_motorola":39,"bit_length":4,"signed":True})
    check("DBC steering rate is signed12", sh["dbc"]["signals"]["STEER_RATE"] == {"start_bit_motorola":35,"bit_length":12,"signed":True})
    for sig, bits, byte, bitoff, addr, sref in [
        (184,12,0,0,"0xFEBEADF0",221),
        (185,4,4,4,"0xFEBEACC5",222),
        (186,12,4,0,"0xFEBEAE14",223),
    ]:
        row = sh["h_signals"][str(sig)]
        check(f"H signal{sig} has exact shared CAN025 shape", row["can_id"] == "0x025" and row["bit_length"] == bits and row["signed"] and row["wire_byte"] == byte and row["bit_offset_in_byte"] == bitoff and row["snapshot_address"] == addr and row["source_unpackers"] == ["0x0004636A"] and row["sienna_same_shape_signals"] == [sref])
    check("CAN025 unpacker recovers all three field shapes", all(sh["unpacker"][k] for k in ("signal184_shape_recovered","signal185_shape_recovered","signal186_shape_recovered")))
    check("H reconstructs angle from coarse+fraction", sh["target_native_semantics"]["angle_plus_fraction"]["recovered"])
    check("H treats signal186 snapshot as rate magnitude", sh["target_native_semantics"]["steering_rate_magnitude"]["recovered"])
    check("H jointly plausibility-checks angle and rate", sh["target_native_semantics"]["joint_plausibility"]["recovered"])
    check("shared command-sized ingress is classified sensor state", sh["classification"] == "shared-command-sized-ingress-is-steering-angle-sensor-state")

    print("\n== final internal torque-command composition ==")
    f = d["final_command_composition"]
    check("BD0E is recovered from local ABB0+BCF8 chain", f["bd0e_local_chain"]["recovered"])
    check("C358 is recovered from local C392+C2D4 chain", f["c358_local_chain"]["recovered"] and f["c358_local_chain"]["c392_recovered_local_state"])
    writers = f["computed_writer_audit"]
    expected = {
        "0xFEBEBE04":"0x000C68F4", "0xFEBEBD90":"0x000C6146", "0xFEBEB678":"0x000BE25A",
        "0xFEBEBEC6":"0x000C76FA", "0xFEBEC39C":"0x000CD31A",
    }
    check("all promoted GP-relative final-command writers recover", f["all_promoted_computed_writers_recovered"] and all(writers[a]["writer"] == e and writers[a]["recovered"] for a,e in expected.items()))

    print("\n== B6 signed16 target-angle ingress ==")
    ta=d["b6_signed16_target_angle_ingress"]
    check("B6 signed16 snapshot is AE82", ta["wire_ingress"]["signal_id"] == 255 and ta["wire_ingress"]["snapshot_destination"] == "0xFEBEAE82")
    check("B6 signed16 domain is target angle", ta["wire_ingress"]["classification"] == "authenticated-signed16-target-steering-angle-command")
    check("target-vs-measured loop is independently recovered", ta["measured_angle_feedback"]["classification"] == "independent-target-versus-measured-steering-angle-control-loop")
    check("physical B6 controller-equivalent scale is closed", ta["scaling"]["physical_degree_scale_closed"] is True and ta["scaling"]["controller_equivalent_fraction_deg_per_b6_count"] == {"numerator":1024,"denominator":17870} and abs(ta["scaling"]["controller_equivalent_mrad_per_b6_count"]-1.0001215187701138)<1e-12)
    check("B6 OEM wire-unit label remains open", ta["scaling"]["oem_wire_unit_name_closed"] is False)
    check("Techstream identifies B6 immediate sender as brake", ta["techstream"]["immediate_sender_monitor"]["description"] == "Lost Communication with Brake System Control Module")

    print("\n== corrected bounded static conclusion ==")
    s = d["static_conclusion"]
    check("earlier direct-write inactive conclusion is superseded", s["earlier_direct_write_inactive_conclusion_superseded"] is True)
    check("retained magnitude computed writer is recovered", s["retained_sienna_lta_magnitude_computed_writer_recovered"] is True)
    check("retained enable computed writer is recovered", s["retained_sienna_lta_enable_computed_writer_recovered"] is True)
    check("retained branch is not statically dead", s["retained_sienna_lta_branch_statically_dead"] is False)
    check("B6 percentage modifiers reach retained branch", s["b6_percentage_modulates_retained_branch"] is True)
    check("B6 signed16 target-angle command is recovered", s["b6_signed16_target_angle_command_recovered"] is True)
    check("no hidden D7 group/full-PDU command is recovered", s["hidden_d7_group_or_full_pdu_command_recovered"] is False)
    check("no hidden B6 group/full-PDU command is recovered", s["hidden_b6_group_or_full_pdu_command_recovered"] is False)
    check("all shared command-sized ingress is sensor state", s["shared_command_sized_ingress_classified_as_sensor_state"])
    check("H-only command-sized scalar is now recovered", s["h_only_or_wire_changed_command_sized_scalar_recovered"] is True)
    check("named retained-branch computed alias audit is closed", s["named_retained_branch_computed_alias_audit_closed"] is True)
    check("Command Value Torque is not classified LTA-only", s["command_value_torque_is_lta_only"] is False)
    check("external autonomous lateral ingress is identified", s["external_autonomous_lateral_ingress_identified"] is True and "0x0B6 signal255" in s["external_autonomous_lateral_ingress"])
    check("immediate sender relationship is Brake System Control Module", s["immediate_sender_relationship"] == "Brake System Control Module")
    check("upstream feature producer remains open", s["upstream_feature_producer_identified"] is False)
    check("physical B6 scale is promoted", s["physical_scale_identified"] is True and abs(s["controller_equivalent_deg_per_count"]-(1024/17870))<1e-15)
    check("OEM B6 wire-unit label remains open", s["oem_wire_unit_name_identified"] is False)
    check("signal254 accepted profiles and OEM labels recovered", s["signal254_profile_values_recovered"] == [1,4,10,11,19] and s["signal254_exact_feature_labels_identified"] is True and s["signal254_profile_labels"] == {'1':'PCS','4':'LDA','10':'Hands Off LTA','11':'LTA/LCA','19':'PDA'})
    check("B6 receiver request/loss/sequence contract promoted", s["request_selection_identified"] is True and s["receiver_loss_cutout_ticks"] == 7 and s["wall_clock_timeout_identified"] is True and s["sequence_counter_identified"] is True and s["sequence_modulus"] == 64 and s["sequence_gap_cap"] == 8)
    check("broad static search remains closed", s["broad_static_search_closed"] is True)

    print("\n== correction/documentation integration ==")
    corrections=(REPO / "docs/status/CORRECTIONS.md").read_text()
    findings=(REPO / "docs/status/FINDINGS.md").read_text()
    variant=(REPO / "docs/variants/corolla-2023-us-public-route.md").read_text()
    priorities=(REPO / "docs/status/PRIORITIES.md").read_text()
    check("CORR-107 records GP-relative target-angle correction", "### CORR-107" in corrections and "CC7F8" in corrections and "CAD62" in corrections and "signal255" in corrections and "signals262/263" in corrections and "FEBEAE82" in corrections)
    check("CORR-078 is explicitly superseded", "**Superseded:** CORR-107" in corrections)
    check("VAR-036 current finding is corrected", "| VAR-036 | **Correction" in findings and "CC2EC -> CAD62" in findings)
    check("canonical Corolla report carries corrected B6 target-angle branch", "protected B6 carries target steering angle" in variant and "FEBEF1CC -> FEBEAE82" in variant and "CA138" in variant and "CAD62" in variant)
    check("priority promotes recovered B6 target-angle command", "B6 signal255" in priorities and "target-minus-measured" in priorities and "1024/17870" in priorities and "signed16 scalar is staged-only" not in priorities)


def _section_motor_control():
    print('== motor control ==')
    """Verify target-native Corolla-H motor-control role recovery."""
    import hashlib,json
    from pathlib import Path
    ROOT=Path(__file__).resolve().parents[1]
    ART=ROOT/'data/generated/corolla_8965H1202000_motor_control.json';EV=ROOT/'data/generated/corolla_8965H1202000_motor_control_decompiler_evidence.json';BUILD=ROOT/'tools/build_corolla_h_motor_control.py';HRAW=ROOT/'community/albinoelephant/raw-20260818/albinoelephant-corolla-2023.20260814-0023/dump_codeflash_00000000_00200000_20260814-025814.bin'
    a=json.loads(ART.read_text());e=json.loads(EV.read_text());H=HRAW.read_bytes()[:0x100000];by={int(x['entry'],16):x for x in e['functions']}
    print('== deterministic artifact ==')
    print('\n== compact evidence ==')
    check('H image hash pinned',sha(H)==e['image']['codeflash_sha256']==a['images']['h_sha256']);check('13 H motor functions compacted',e['function_count']==13==len(e['functions']));check('all raw H bodies validate',all(sha(H[int(x['entry'],16):int(x['entry'],16)+x['body_size']])==x['body_sha256'] for x in e['functions']));check('all H decompiler hashes validate',all(sha(x['decompiled_c'].encode())==x['decompiled_c_sha256'] for x in e['functions']))
    print('\n== five changed motor roles ==')
    exp={'0x00032B80':'0x0002E780','0x00036A44':'0x00032616','0x00038464':'0x00033C70','0x00038554':'0x00033D60','0x0005D18C':'0x00058226'}
    check('all five unresolved motor roles recovered',a['motor_role_closure_count']==5 and {x['reference_entry']:x['target_entry'] for x in a['motor_role_closure']}==exp)
    print('\n== calibration state machine ==')
    c=a['calibration_state_machine'];check('S/H calibration state machines are both 1004 bytes',c['sienna_body_size']==c['h_body_size']==1004);check('state 0x33 calls recovered H main handler',c['sienna_has_state_33_call'] and c['h_has_state_33_call'] and c['h_state_0x33_handler']=='0x0002E780');check('H main calibration handler grows 1560->1638 bytes',c['sienna_handler_size']==1560 and c['h_handler_size']==1638);check('H calibration phases publish 0x22 then 0x44',c['h_completion_states']=={'preceding':0x22,'main':0x44} and '= 0x22' in by[0x2E44C]['decompiled_c'] and '= 0x44' in by[0x2E780]['decompiled_c']);check('0x512 and 0x600 domains still dispatch calibration machine',c['version_dispatch']['domains']==[0x512,0x600] and all(t in by[0x57CEA]['decompiled_c'] for t in ('param_2 == 0x512','param_2 == 0x600','FUN_0002ede6')) and all(t in by[0x57EEE]['decompiled_c'] for t in ('param_2 == 0x512','param_2 == 0x600','FUN_0002ede6')))
    print('\n== PI current loops ==')
    pi=a['current_pi_pair'];check('axis A remains exact-size 304-byte analogue',pi['axis_a_body_sizes']==[304,304]);check('axis B is simplified 404->280 bytes',pi['axis_b_body_sizes']==[404,280]);check('steady worker preserves B-before-A order',pi['order_preserved'] and pi['sienna_worker_indices']==[15,16] and pi['h_worker_indices']==[11,12]);check('H A/B share reset and saturation gates',pi['h_shared_reset_gate']);check('H axis B uses ref-feedback 6BBC-6BAC',all(t.lower().replace('0x','') in by[0x32616]['decompiled_c'].lower() for t in pi['h_axis_b_reference_feedback']));check('H axis A uses ref-feedback 6BBE-6BB0',all(t.lower().replace('0x','') in by[0x324D4]['decompiled_c'].lower() for t in pi['h_axis_a_reference_feedback']));check('H gain blocks split A/B at 2D5A4/2D5B4',all(t in by[0x324D4]['decompiled_c'] for t in ('DAT_0002d5a4','DAT_0002d5b0')) and all(t in by[0x32616]['decompiled_c'] for t in ('DAT_0002d5b4','PTR_LAB_0002d5bc')));check('axis-B internal-state transfer is explicitly bounded','do not transfer Sienna axis-B internal state semantics wholesale' in pi['axis_b_boundary'])
    print('\n== inverse rotating-frame pair ==')
    inv=a['inverse_rotating_frame'];check('H inverse transforms are twin 226-byte functions',inv['body_sizes']==[226,226]);check('inverse formula constants are preserved',inv['formula_tokens_present'] and inv['formula_tokens']==['0x6eda','0x6883','0x8000','0x2000','0x7fff','0x8001']);check('inverse-transform order is preserved',inv['order_preserved'] and inv['h_worker_indices']==[20,21]);check('motor0 H inputs/angle/output banks pinned',inv['h_inputs'][0]==['0xFEBE6A80','0xFEBE6A82'] and inv['h_angle_pairs'][0]==['0xFEBE7A54','0xFEBE7A56'] and inv['h_outputs'][0]==['0xFEBE6C78','0xFEBE6C7A','0xFEBE6C7C']);check('motor1 H inputs/angle/output banks pinned',inv['h_inputs'][1]==['0xFEBE6A84','0xFEBE6A86'] and inv['h_angle_pairs'][1]==['0xFEBE7A60','0xFEBE7A62'] and inv['h_outputs'][1]==['0xFEBE6C80','0xFEBE6C82','0xFEBE6C84'])
    print('\n== CH0 orchestration ==')
    w=a['ch0_worker'];check('CH0 worker maps 216->192 bytes',w['sienna_body_size']==216 and w['h_body_size']==192);check('CH0 wrappers are both 146 bytes',w['wrapper_body_sizes']==[146,146]);check('H wrapper directly invokes transition and steady workers',all(t in by[0x52DBA]['decompiled_c'] for t in ('FUN_00057fc8(2,uVar4,uVar1)','FUN_00058226(2,uVar2)')));check('H steady worker uses >0x1FF motor gate and >0x100 duty gate','0x1ff < param_2' in by[0x58226]['decompiled_c'] and '0x100 < param_2' in by[0x58226]['decompiled_c']);check('H anchor call order is PI-B, PI-A, inverse0, inverse1',all(by[0x58226]['decompiled_c'].index(x+'()') < by[0x58226]['decompiled_c'].index(y+'()') for x,y in zip(w['h_anchor_call_order'],w['h_anchor_call_order'][1:])));check('transition dispatcher contains same motor anchors',all(x+'()' in by[0x57FC8]['decompiled_c'] for x in w['h_anchor_call_order']))
    check('report closes changed motor residue without flattening target-specific internals',a['static_conclusion']['motor_control_residue_closed'] and 'target-specific' in a['static_conclusion']['boundary'])


def _section_openpilot_state_bridge():
    print('== openpilot state bridge ==')
    """Verify the H/F Corolla openpilot state-interface bridge."""

    import hashlib
    import json
    from pathlib import Path

    REPO = Path(__file__).resolve().parents[1]
    ART = REPO / "data/generated/corolla_8965H1202000_openpilot_state_bridge.json"
    EVID = REPO / "data/generated/corolla_8965H1202000_openpilot_state_bridge_decompiler_evidence.json"
    FD = REPO / "data/generated/corolla_8965H1202000_fd_control_interface.json"
    BUILD = REPO / "tools/build_corolla_h_openpilot_state_bridge.py"
    IMAGE = REPO / "community/albinoelephant/normalized/8965H1202000_CodeFlash.bin"
    DOC = REPO / "docs/variants/corolla-h-f-openpilot-state-bridge.md"


    art = json.loads(ART.read_text())
    evid = json.loads(EVID.read_text())
    fd = json.loads(FD.read_text())
    image = IMAGE.read_bytes()

    print("== deterministic artifacts ==")
    check("bridge schema v8", art["schema"] == "corolla-8965H1202000-openpilot-state-bridge-v8")
    check("compact evidence schema v2", evid["schema"] == "corolla-h-openpilot-state-bridge-decompiler-evidence-v2")
    check("exact H image identity", len(image) == 0x100000 and sha(image) == art["images"]["corolla_h"]["sha256"] == evid["image"]["sha256"])
    check("H/F application identity carried forward", art["images"]["corolla_f"]["application_byte_identical_to_h"])
    check("promoted corpus identity exact", evid["source_corpus"]["sha256"] == "c3411eec57b9d55c004b0b0f328394bb152577c3398084dccc729dab5da54656" and evid["source_corpus"]["function_count"] == 5478)
    check("26 compact state functions promoted", evid["function_count"] == 26)
    for row in evid["functions"]:
        start = int(row["entry"], 16)
        check(f"raw body {row['entry']}", sha(image[start:start + row["body_size"]]) == row["body_sha256"])

    print("\n== exact H Tx carriers ==")
    pdus = {x["can_id"]: x for x in art["h_tx_pdu_descriptors"]}
    check("new H Tx family exact", list(pdus) == ["0x030", "0x351", "0x394", "0x4A3", "0x4C8"])
    check("0x030 is 32-byte PDU0", pdus["0x030"]["pdu"] == 0 and pdus["0x030"]["length"] == 32)
    check("0x351 is 4-byte PDU1", pdus["0x351"]["pdu"] == 1 and pdus["0x351"]["length"] == 4)
    check("0x394 is 3-byte PDU2", pdus["0x394"]["pdu"] == 2 and pdus["0x394"]["length"] == 3)
    check("0x4A3 is 8-byte PDU3", pdus["0x4A3"]["pdu"] == 3 and pdus["0x4A3"]["length"] == 8)

    print("\n== 0x4A3 physical state bridge ==")
    b = art["state_bridge"]["0x4A3"]
    fields = {x["wire"]: x for x in b["fields"]}
    check("4A3 driver torque has official physical scale", fields["B5"]["semantic"] == "Steering Wheel Torque" and fields["B5"]["techstream_did"] == "0x1035" and fields["B5"]["unit"] == "Nm" and fields["B5"]["packet_scale"] == 0.1)
    check("4A3 Q-current is sign-inverted physical feedback", fields["B6:B7"]["semantic"] == "Motor Actual Current (Q Axis)" and fields["B6:B7"]["techstream_did"] == "0x1151" and fields["B6:B7"]["packet_scale"] == -0.01)
    check("4A3 carries selected steering fault/inhibit duplicate", fields["B0[0]"]["semantic"].startswith("selected steering fault/inhibit status") and "not an exhaustive EPS-fault state" in fields["B0[0]"]["semantic"])
    check("4A3 remains route-availability bounded", "zero 0x4A3 frames" in b["dynamic_boundary"])

    print("\n== 0x351 mixed status bridge ==")
    s351 = art["state_bridge"]["0x351"]
    check("351 is mixed status, not generic readiness", "mixed EPS status" in s351["classification"] and "C159B49-linked" in s351["classification"] and "not a generic LKA/EPS-ready state" in s351["boundary"] and "no unique Toyota/DTC display names" in s351["boundary"])
    check("351 force7 topology is fully source-bounded", s351["force7_static_contract"]["condition"] == "(FEBE65E4 & 0x0003) != 0 AND FEBE7E13 != 0" and s351["force7_static_contract"]["record_aggregate_side"]["record_count"] == 24 and s351["force7_static_contract"]["record_aggregate_side"]["bit_used"] == 15)
    check("351 exact C159B49 diagnostic join", s351["diagnostic_join"]["techstream_code"] == "C159B49" and s351["diagnostic_join"]["h_dtc_index"] == 54 and s351["diagnostic_join"]["enabled_word"] == 1)
    check("351 exact seven-count transition state", any("seven-count transition state" in x and "0x2B930 = 7" in x for x in s351["producer_chain"]))
    check("351 force-7 override is separate and exact", "separately forces code 7" in s351["wire_fields"][0]["semantic"] and "exact force-7 indicator" in s351["wire_fields"][1]["semantic"] and "(FEBE65E4 & 3) != 0" in s351["wire_fields"][1]["semantic"] and "FEBE7E13 != 0" in s351["wire_fields"][1]["semantic"] and any("force-writes code 7 plus FEBE7DD1=1" in x for x in s351["producer_chain"]))
    check("351 packet availability remains bounded", "zero 0x351 frames" in s351["dynamic_boundary"])

    print("\n== 0x394 classifier ==")
    s394 = art["state_bridge"]["0x394"]
    check("394 has exact 17-row classifier table", len(s394["state_table_rows"]) == 17 and s394["state_table_rows"][0] == [0, 0, 0, 0, 0])
    check("394 homolog table is byte-identical in Sienna", s394["sienna_table_byte_identical"] is True)
    check("394 state0 is deepest clear/normal path, not Ready", s394["classifier_states"]["0"]["role"] == "deepest clear/normal classifier path" and s394["openpilot_fault_mapping"]["classifier_deepest_clear_normal_state"] == 0 and "not sufficient to authorize actuation" in s394["openpilot_fault_mapping"]["conservative_clear_state_candidate"])
    cfg = s394["state0_final_branch_window"]
    check("394 state0 final gating is raw-instruction pinned", cfg["start"] == "0x0004BB16" and cfg["end_exclusive"] == "0x0004BB50" and cfg["sha256"] == "d3838fae94f6a5bdcf953ccabda64142bddeffd2470e4935af3c4a7374ba50c6" and "0x4BB48" in cfg["control_flow"] and "state 16" in cfg["control_flow"] and "not assign OEM names" in cfg["boundary"])
    check("394 special state15 remains bounded", s394["classifier_states"]["15"]["role"] == "special operating state" and "not safely nameable" in s394["classifier_states"]["15"]["boundary"])
    check("394 temp/permanent fault mapping is deliberately unresolved", s394["openpilot_fault_mapping"]["steerFaultTemporary"] == s394["openpilot_fault_mapping"]["steerFaultPermanent"] == "unresolved")
    check("394 complete DEM class partition is embedded", sum(s394["fault_state_contract"]["dem"]["class_counts"].values()) == 242 and s394["classifier_states"]["6"]["role"].startswith("class-0x02") and s394["classifier_states"]["10"]["role"].startswith("class-0x10") and s394["fault_state_contract"]["aging"]["class2_class4_secondary_age"] == 600)
    check("394 packet availability remains bounded", "zero 0x394 frames" in s394["dynamic_boundary"])

    print("\n== live 0x030 state and torque ==")
    s030 = art["state_bridge"]["0x030"]
    check("030 configured signal set 0..36", s030["configured_signals"] == list(range(37)))
    check("030 direct packed signals 0..34", s030["direct_packed_signals"] == list(range(35)))
    check("030 additive byte7 exact formula", s030["additive_field"]["wire_byte"] == 7 and "sum(payload_bytes_0_through_6) + 0x38" in s030["additive_field"]["formula"])
    state_fields = {x["signal_id"]: x for x in s030["steering_state_fields"]}
    check("030 selected steering fault/inhibit status nominal polarity observed", state_fields[6]["wire"] == "B6[2]" and state_fields[6]["span_values"] == [0] and state_fields[6]["span_clear_frames"] == 6000)
    check("030 torque-validity gate nominal polarity observed", state_fields[8]["wire"] == "B6[0]" and state_fields[8]["span_values"] == [0] and state_fields[8]["span_clear_frames"] == 6000)
    check("030 neighboring status bit is live", state_fields[7]["span_values"] == [0, 1])
    check("030 B6[1] source/calibration is statically closed", "Q-axis actual-current-derived" in state_fields[7]["semantic"] and state_fields[7]["static_contract"]["calibration"]["feature_flag"] == 0x5A and "calibration-disabled" in state_fields[7]["static_contract"]["classification"])
    torque = s030["driver_torque_encoding_family"]
    check("030 torque exact physical reconstruction promoted", torque["signal_ids"] == [0, 10, 31] and torque["physical_reconstruction"].startswith("Steering Wheel Torque [N.m] = signal10_signed * 0.1"))
    check("030 torque live dynamic range observed", torque["span_torque_nm"]["count"] == 6000 and torque["span_torque_nm"]["min"] < -8.0 and torque["span_torque_nm"]["max"] > 2.8 and torque["span_torque_nm"]["unique_count"] > 500)
    check("030 coarse rounding behavior exact", torque["coarse_rounding_delta_values"] == [-1, 0, 1])
    check("030 eleven GP-relative false negatives corrected", [x["signal_id"] for x in s030["gp_relative_runtime_fields"]] == [0, 1, 10, 14, 16, 17, 18, 27, 28, 31, 34])
    check("underlying FD artifact carries the GP correction", fd["schema"] == "corolla-8965H1202000-fd-control-interface-v2" and fd["fd_0x030_transmit"]["gp_relative_writer_correction"]["affected_signal_ids"] == [0, 1, 10, 14, 16, 17, 18, 27, 28, 31, 34])
    check("030 Q-current derivative remains scale-bounded", s030["q_current_derived_field"]["signal_id"] == 34 and "calibration-dependent" in s030["q_current_derived_field"]["classification"])

    print("\n== Ready Status input wire join ==")
    ready = art["state_bridge"]["ready_status_input_0x51E"]
    check("Ready Status exact input wire and DID", ready["can_id"] == "0x51E" and ready["wire"] == "B0[7]" and ready["firmware_signal_id"] == 154 and ready["did"] == "0x1033" and ready["name"] == "Ready Status")
    check("Ready Status exact source chain", ready["source_chain"] == ["0x51E B0[7]", "0xFEBE7D1B", "0xFEBEF052", "0xFEBEB5A8", "0xFEBEE811", "DID 0x1033"] and ready["firmware_chain_verified"] is True)
    check("Ready Status operational value1 is observed but value0 remains bounded", ready["span_operational_frames"] == 60 and ready["span_values"] == [1] and "value 0" in ready["boundary"] and "does not imply" in ready["boundary"])
    check("Ready Status is explicitly an input, not invented as EPS Tx field", "can be parsed as the target-native Ready Status input" in ready["openpilot_consequence"] and "distinct from 0x030/0x351/0x394" in ready["openpilot_consequence"])

    print("\n== CarState/Panda closure ==")
    closure = art["carstate_and_panda_input_closure"]
    check("driver torque is now live on 030", "closed and live on 0x030" in closure["driver_steering_torque"])
    check("motor response remains static 4A3", "0x4A3 B6:B7" in closure["motor_actuator_response"] and "current routes do not carry 0x4A3" in closure["motor_actuator_response"])
    check("fault gates are live but temp/permanent remains open", "live 0x030 B6[2]" in closure["steering_fault_inhibit_status"] and closure["temporary_vs_permanent_fault"].startswith("not closed"))
    check("production safety remains blocked", "do not authorize actuation" in closure["production_safety_boundary"])

    print("\n== command ingress continuity ==")
    c = art["command_ingress_closure"]
    check("large ingress includes B6 target plus 025 sensors", c["supervisor_reaching_ge12bit_fields"] == [{"can_id": "0x025", "signal_id": 184, "bits": 12}, {"can_id": "0x025", "signal_id": 186, "bits": 12}, {"can_id": "0x0B6", "signal_id": 255, "bits": 16}])
    check("B6 target-angle command remains exact", c["b6_target_angle"]["signal_id"] == 255 and c["b6_target_angle"]["wire_byte"] == 4 and c["b6_target_angle"]["signed"] and c["b6_target_angle"]["snapshot"] == "0xFEBEAE82")
    check("B6 receiver contract retained", c["b6_target_angle"]["request_selection_closed"] is True and c["b6_target_angle"]["receiver_loss_cutout_ticks"] == 7 and c["b6_target_angle"]["sequence_modulus"] == 64 and c["b6_target_angle"]["sequence_gap_cap"] == 8)

    print("\n== documentation integration ==")
    doc = DOC.read_text() if DOC.exists() else ""
    for token in ("0x4A3", "0x351", "0x394", "0x030", "0x1035", "0x1037", "0x1151", "0x0B6", "Target Steering Angle", "FRC_P5"):
        check(f"doc preserves {token}", token in doc)
    findings = (REPO / "docs/status/FINDINGS.md").read_text()
    priorities = (REPO / "docs/status/PRIORITIES.md").read_text()
    check("COM-009 integrated", "| COM-009 |" in findings and "corolla-h-f-openpilot-state-bridge.md" in findings)
    check("priority consumes state bridge", "corolla-h-f-openpilot-state-bridge.md" in priorities)


def _section_plausibility_monitor():
    print('== plausibility monitor ==')
    """Verify the target-native nine-channel plausibility-monitor mapping."""
    import hashlib,json
    from pathlib import Path
    ROOT=Path(__file__).resolve().parents[1];ART=ROOT/'data/generated/corolla_8965H1202000_plausibility_monitor.json';EV=ROOT/'data/generated/corolla_8965H1202000_plausibility_monitor_decompiler_evidence.json';TOOL=ROOT/'tools/build_corolla_h_plausibility_monitor.py';RAW=ROOT/'community/albinoelephant/raw-20260818/albinoelephant-corolla-2023.20260814-0023/dump_codeflash_00000000_00200000_20260814-025814.bin'
    d=json.loads(ART.read_text());e=json.loads(EV.read_text());raw=RAW.read_bytes()[:0x100000];by={int(r['entry'],16):r for r in e['functions']}
    check('H image hash pinned',sha(raw)==e['image']['codeflash_sha256'])
    check('12 H functions compacted',e['function_count']==12)
    check('all raw H bodies validate',all(sha(raw[int(r['entry'],16):int(r['entry'],16)+r['body_size']])==r['body_sha256'] for r in e['functions']))
    check('all H decompiler hashes validate',all(sha(r['decompiled_c'].encode())==r['decompiled_c_sha256'] for r in e['functions']))
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
    check('target-specific boundary explicit','remain target-specific' in d['static_conclusion']['boundary'])


def _section_power_supply_monitor_gate():
    print('== power supply monitor gate ==')
    """Verify the exact H/F FEBE7C58 -> FEBEF000 -> FEBEACBD monitor contract."""

    import hashlib
    import json
    from pathlib import Path

    REPO = Path(__file__).resolve().parents[1]
    RAW = REPO / "community/albinoelephant/normalized/8965H1202000_CodeFlash.bin"
    EVID = REPO / "data/generated/corolla_8965H1202000_power_supply_monitor_decompiler_evidence.json"
    ART = REPO / "data/generated/corolla_8965H1202000_power_supply_monitor_gate.json"
    TOOL = REPO / "tools/build_corolla_h_power_supply_monitor_gate.py"


    raw = RAW.read_bytes()
    ev = json.loads(EVID.read_text())
    art = json.loads(ART.read_text())

    print("\n== source binding ==")
    check("schema exact", art["schema"] == "corolla-8965H1202000-power-supply-monitor-gate-v1")
    check("exact H image", len(raw) == 0x100000 and sha(raw) == art["sources"]["codeflash"]["sha256"] == "0b47bdc1217835c839e3543e52eab40eb793650a9c159e46f6a9b365ea41a67f")
    check("14 compact functions", ev["function_count"] == art["sources"]["decompiler_evidence"]["function_count"] == 14)
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
    check("unlabeled control inputs remain unnamed", all(token in join["boundary"] for token in ("FEBE63A4", "FEBE65E4", "FEBE7C5F")))
    classification = art["classification"]
    check("state classified as graded receive-validity/freeze gate", "power-supply receive-validity/freeze state" in classification["recovered"] and "scheduler snapshot" in classification["recovered"] and "normalized downstream gate" in classification["recovered"])
    check("B6 loss remains separate", classification["distinct_from_b6_loss"] == "B6 missing-message loss remains the separate FEBEADB9 -> FEBEC26D path.")
    check("confidence boundary explicit", classification["not_established"] == ["literal OEM name for any of the three state bytes", "physical units of the raw supply cells", "wall-clock debounce durations", "a wire-visible FEBEACBD feedback field", "arbitrary computed-pointer aliases outside the census"])


    print("\n== documentation/status integration ==")
    state_doc = (REPO / "docs/variants/corolla-h-f-openpilot-state-bridge.md").read_text()
    findings = (REPO / "docs/status/FINDINGS.md").read_text()
    check("canonical report records power-supply gate semantics", all(x in state_doc for x in ("### 6.5", "FEBE7C58", "FEBEF000", "FEBEACBD", "power-supply receive-validity/freeze state", "FEBEADB9 -> FEBEC26D")))
    check("TMS-055 integrated", "| TMS-055 |" in findings and "power_supply_monitor_gate.json" in findings)


def _section_secoc_key_provenance():
    print('== secoc key provenance ==')
    """Verify Corolla 8965H1202000 SecOC key-selector/provisioning provenance."""

    import hashlib
    import json
    from pathlib import Path

    REPO = Path(__file__).resolve().parents[1]
    ART = REPO / "data/generated/corolla_8965H1202000_secoc_key_provenance.json"
    EVIDENCE = REPO / "data/generated/corolla_8965H1202000_secoc_key_provenance_decompiler_evidence.json"
    BUILDER = REPO / "tools/build_corolla_h_secoc_key_provenance.py"
    HRAW = REPO / "community/albinoelephant/raw-20260818/albinoelephant-corolla-2023.20260814-0023/dump_codeflash_00000000_00200000_20260814-025814.bin"
    SIMG = REPO / "firmware/RH850_P1M-E_CodeFlash.bin"
    DF = REPO / "data/generated/corolla_2023_albino_dataflash_analysis.json"


    hraw = HRAW.read_bytes()
    h = hraw[:0x100000]
    s = SIMG.read_bytes()
    d = json.loads(ART.read_text())
    ev = json.loads(EVIDENCE.read_text())
    df = json.loads(DF.read_text())

    print("== deterministic generator ==")
    print("\n== image/evidence binding ==")
    check("H image hash is pinned", sha(h) == d["images"]["corolla_h_sha256"] == ev["image"]["sha256"])
    check("Sienna image hash is pinned", sha(s) == d["images"]["sienna_sha256"])
    check("decompiler evidence contains 22 functions", ev["function_count"] == 22 == len(ev["functions"]))
    all_bodies = True
    all_c = True
    for row in ev["functions"]:
        entry = int(row["entry"], 16)
        all_bodies &= sha(h[entry:entry + row["body_size"]]) == row["body_sha256"]
        all_c &= sha(row["decompiled_c"].encode()) == row["decompiled_c_sha256"]
    check("all cited H raw function bodies validate", all_bodies)
    check("all cited decompiler records validate", all_c)

    print("\n== queue records and shared selector ==")
    check("exact H protected queue IDs", [r["can_id"] for r in d["secoc_records"]] == ["0x00F", "0x0D7", "0x0B6"])
    check("all queue records use SecOC config ID 0", all(r["secoc_crypto_config_id"] == 0 for r in d["secoc_records"]))
    check("all queue records use CryptoIf job handle 0", all(r["cryptoif_job_handle"] == 0 for r in d["secoc_records"]))
    check("config object is exact type1/slot4", d["shared_crypto_selection"]["config_bytes"] == "0100000004000000000000000000000000000000")
    check("config object selects ICU-S slot 4", d["shared_crypto_selection"]["config_type"] == 1 and d["shared_crypto_selection"]["icus_slot_selector"] == 4)
    check("H and Sienna use the same slot-4 config bytes", d["shared_crypto_selection"]["same_bytes_as_sienna"])
    check("raw H config bytes agree", h[0x2570C:0x25720].hex() == d["shared_crypto_selection"]["config_bytes"])
    check("raw Sienna config bytes agree", s[0x25950:0x25964].hex() == d["shared_crypto_selection"]["config_bytes"])

    print("\n== command-7 CPU/ICU boundary ==")
    path = d["command7_cpu_to_icus_path"]
    check("command-7 path retains no raw key bytes", path["raw_key_bytes_in_cpu_command_descriptor"] is False)
    check("command-7 prepare is pinned", path["icus_command7_prepare"] == "0x822D0")
    check("command-7 driver is pinned", path["icus_command7"] == "0x83BF4")
    check("selector flow ends in ICUSCMD command 7", "writes (word4 << 16) | 7 to ICUSCMD" in path["selector_flow"][-1])
    check("disabled H KAT uses same config", d["slot4_kat"]["config_bytes"] == d["shared_crypto_selection"]["config_bytes"])
    check("disabled H KAT gate is zero", d["slot4_kat"]["compile_gate_address"] == "0x2CA9F" and h[0x2CA9F] == 0 and not d["slot4_kat"]["enabled"])

    print("\n== authenticated key update boundary ==")
    ku = d["command8_key_update"]
    check("key update accepts exact 64-byte package", ku["request_length"] == 64 and ku["staging_shape"] == [16, 32, 16])
    check("key update returns 48-byte proof/result", ku["success_output_length"] == 48)
    check("key update submits literal ICU command 8", ku["icus_command"] == 8 and ku["driver"] == "0x83D7A")
    check("CPU descriptor has no fixed target slot", ku["fixed_cpu_side_target_slot_selector"] is None)

    print("\n== DataFlash evidence boundary ==")
    neg = d["dataflash_raw_key_negative"]
    check("tracked DataFlash hash is pinned", neg["snapshot_sha256"] == df["dump_sha256"])
    check("raw-window scan denominator is 23,277", neg["candidates_tested"] == df["key_domain_scan"]["candidates_tested"] == 23277)
    check("raw-window scan found no candidate match", neg["matches"] == df["key_domain_scan"]["matches"] == [])
    check("report preserves cross-epoch/derivation caveat", "not proven same-runtime-epoch" in neg["boundary"] and "does not exclude transformed/derived" in neg["boundary"])

    print("\n== final static model ==")
    model = d["static_storage_derivation_conclusion"]
    check("slot selector is CPU-visible", model["cpu_visible_slot4_selector"] is True)
    check("raw slot-4 key is not CPU-visible on mapped verify path", model["cpu_visible_raw_slot4_key"] is False)
    check("mapped SecOC init has no recovered raw-key load", model["mapped_secoc_init_raw_key_load_found"] is False)
    check("mapped SecOC init has no recovered key derivation", model["mapped_secoc_init_key_derivation_found"] is False)
    check("authenticated provisioning interface is recovered", model["provisioning_interface_found"] is True)


def _section_secoc_surface():
    print('== secoc surface ==')
    """Verify target-native Corolla H SecOC/ICU-S residual role recovery."""
    import hashlib,json
    from pathlib import Path
    ROOT=Path(__file__).resolve().parents[1]
    ART=ROOT/'data/generated/corolla_8965H1202000_secoc_surface.json';EV=ROOT/'data/generated/corolla_8965H1202000_secoc_surface_decompiler_evidence.json';BUILD=ROOT/'tools/build_corolla_h_secoc_surface.py';HRAW=ROOT/'community/albinoelephant/raw-20260818/albinoelephant-corolla-2023.20260814-0023/dump_codeflash_00000000_00200000_20260814-025814.bin'
    a=json.loads(ART.read_text());e=json.loads(EV.read_text());H=HRAW.read_bytes()[:0x100000];byh={int(x['target_entry'],16):x for x in e['functions']}
    print('== deterministic artifact ==')
    print('\n== compact evidence ==')
    check('H image hash pinned',sha(H)==e['image']['codeflash_sha256']==a['images']['h_sha256']);check('42 residual role records are compacted',e['function_count']==42==len(e['functions'])==a['secoc_role_closure_count']);check('all raw canonical-size target windows validate',all(sha(H[int(x['target_entry'],16):int(x['target_entry'],16)+x['raw_window_size']])==x['raw_window_sha256'] for x in e['functions']));check('all target-native decompiler hashes validate',all(sha(x['decompiled_c'].encode())==x['decompiled_c_sha256'] for x in e['functions']))
    print('\n== ICU-S / CryptoIf core ==')
    c=a['icus_cryptoif_core'];check('25 lower core roles recover at one -0x5C00 island',c['role_count']==25 and c['all_at_single_delta'] and c['delta']==-0x5c00);check('all 25 core reported body sizes match canonical roles',c['all_reported_body_sizes_match']);check('command8 adapter calls command8 prepare','FUN_00081262' in byh[0x814a8]['decompiled_c']);check('command5 adapter calls MAC-generation prepare','FUN_00081e94' in byh[0x820cc]['decompiled_c']);check('command7 verify adapter calls CMAC-verify prepare','FUN_000822d0' in byh[0x824dc]['decompiled_c']);check('CryptoIf begin/update preserve generic job chain',byh[0x82f6a]['target_reported_body_size']==50 and byh[0x82f9c]['target_reported_body_size']==12);check('FIFO/finalizer trio is exact-size relocated family',[byh[x]['target_reported_body_size'] for x in (0x83848,0x838be,0x83910)]==[82,82,60])
    print('\n== RX front-end and profile population ==')
    r=a['rx_frontend'];check('H init and ingress roles recovered',r['init']['h']=='0x00088024' and r['indication']['h']=='0x0008818C');check('H init installs generated slot-4 crypto config',r['init']['installs_slot4_config']);check('H ingress calls record lookup then secured queue',r['indication']['calls_record_lookup'] and r['indication']['calls_secured_queue'] and r['indication']['body_size']==62);check('H has exactly three SecOC RX profiles',r['profile_count']==3 and [x['can_id'] for x in r['profiles']]==[0x00f,0x0d7,0x0b6]);check('H profile PDU IDs are 9/40/42',[x['pdu_id'] for x in r['profiles']]==[9,40,42]);check('all H profiles share crypto config/job 0',all(x['crypto_config_id']==0 and x['cryptoif_handle']==0 for x in r['profiles']))
    print('\n== freshness architecture ==')
    fr=a['freshness'];check('configured get callback is H 896B0',fr['configured_get_callback_set']==[0x896b0]);check('configured commit callback is H 89758',fr['configured_commit_callback_set']==[0x89758]);check('get callback dispatches profile lookup + normal/sync reconstruction',fr['get_dispatches_normal_sync']);check('commit callback dispatches profile lookup + normal/sync commit',fr['commit_dispatches_normal_sync']);check('normal freshness reconstruct maps to H 89E9A',fr['reconstruct_normal']['h']=='0x00089E9A' and byh[0x89e9a]['target_reported_body_size']==212);check('sync freshness reconstruct maps to H 89F6E',fr['reconstruct_sync']['h']=='0x00089F6E' and byh[0x89f6e]['target_reported_body_size']==228);check('normal/sync commits retain 52/78-byte roles',[byh[x]['target_reported_body_size'] for x in (0x8a07a,0x8a130)]==[52,78])
    print('\n== application ICU interrupts and test callbacks ==')
    i=a['application_icus_isrs'];check('ICU ISR pair remains 66-byte wrappers',i['same_reported_size']);check('CH292 ISR calls H interrupt dispatcher','FUN_00081a10' in byh[0x5f3ec]['decompiled_c']);check('CH293 ISR calls H interrupt dispatcher','FUN_00081a36' in byh[0x5f42e]['decompiled_c']);tc=a['crypto_test_callbacks'];cmpc=byh[0x633a0]['decompiled_c'];check('command5 result comparator still compares 16 bytes and returns 44/33',tc['result_compare']['compare_length']==16 and '0x10' in cmpc and '0x44' in cmpc and '0x33' in cmpc);check('key-update completion retains 44/66 terminal states','0x66' in byh[0x63542]['decompiled_c'] and '0x44' in byh[0x63542]['decompiled_c']);check('command5 completion calls result comparator on success','000633a0' in byh[0x635a2]['decompiled_c'].lower());check('fragmented callback boundary caveat is explicit','fragmented' in tc['boundary'])
    print('\n== protected D7 generated unpacker ==')
    d=a['d7_unpacker'];check('H D7 SecOC record routes to PDU 40',d['h_secoc_record_pdu_id']==40);check('PDU 40 owns configured signals 240..247',d['h_pdu40_signal_ids']==list(range(240,248)));check('H D7 scalar unpacker is 468FA and reads 240/243/246',d['h']=='0x000468FA' and sorted(d['h_scalar_receive_signal_ids'])==[240,243,246]);check('H D7 unpacker is regenerated 194->140 bytes',d['sienna_body_size']==194 and d['h_reported_body_size']==140);check('D7 role transfer does not transfer Sienna signal IDs','regenerates the signal population' in d['interpretation'])
    print('\n== conclusion boundary ==')
    sc=a['static_conclusion'];check('all 42 SecOC/ICU-S residual roles are closed',sc['all_42_secoc_icus_residual_roles_recovered']);check('profile population difference remains explicit',sc['h_profile_population_changed']);check('target-specific key/profile boundary remains explicit','protected key contents remain H-specific' in sc['boundary'])


def _section_small_adapters():
    print('== small adapters ==')
    """Verify generated bounded-API, packet-selector, and record-operation adapter mappings."""
    import hashlib,json
    from pathlib import Path
    ROOT=Path(__file__).resolve().parents[1];ART=ROOT/'data/generated/corolla_8965H1202000_small_adapters.json';EV=ROOT/'data/generated/corolla_8965H1202000_small_adapter_decompiler_evidence.json';TOOL=ROOT/'tools/build_corolla_h_small_adapters.py';RAW=ROOT/'community/albinoelephant/raw-20260818/albinoelephant-corolla-2023.20260814-0023/dump_codeflash_00000000_00200000_20260814-025814.bin'
    d=json.loads(ART.read_text());e=json.loads(EV.read_text());raw=RAW.read_bytes()[:0x100000];by={int(r['entry'],16):r for r in e['functions']}
    check('H image hash pinned',sha(raw)==e['image']['codeflash_sha256'])
    check('18 H adapter functions compacted',e['function_count']==18)
    check('all raw H bodies validate',all(sha(raw[int(r['entry'],16):int(r['entry'],16)+r['body_size']])==r['body_sha256'] for r in e['functions']))
    check('all H decompiler hashes validate',all(sha(r['decompiled_c'].encode())==r['decompiled_c_sha256'] for r in e['functions']))
    check('all 18 roles recovered',d['role_closure_count']==18 and d['static_conclusion']['all_18_roles_recovered'])
    b=d['bounded_api'];check('six bounded wrappers relocate by -0x5C60',b['delta']==-0x5C60 and b['same_wrapper_sizes'])
    check('H bounded pointer table is 21838',b['h_pointer_table']['base']=='0x00021838' and len(b['h_pointer_table']['values'])==6)
    check('all six bounded target slots preserve -0x4FDA relocation',all(int(h,16)-int(s,16)==-0x4FDA for s,h in zip(b['sienna_pointer_table']['values'],b['h_pointer_table']['values'])))
    pkt=d['packet_selector'];check('packet table has same 21 configured selector indices',pkt['configured_selectors_h']==pkt['configured_selectors_sienna'] and len(pkt['configured_selectors_h'])==21)
    check('packet table maps to H 269FC',pkt['h_table_base']=='0x000269FC' and pkt['table_count']==44)
    check('seven residual packet selector targets exact',pkt['mapped_target_checks'] and sorted(pkt['mapped_selectors'])==[6,15,16,22,38,39,43])
    rec=d['record_operation'];check('record table maps 5x0x1C at H 25F28',rec['h_table_base']=='0x00025F28' and rec['record_count']==5 and rec['stride']==28)
    check('five record callback words exact',rec['mapped_target_checks'] and rec['all_h_callbacks_48_bytes'])
    check('target-specific payload boundary explicit','remain H-specific' in d['static_conclusion']['boundary'])


def _section_static_coverage():
    print('== static coverage ==')
    """Verify the evidence-graded named-function coverage denominator."""
    import json
    from pathlib import Path
    REPO=Path(__file__).resolve().parents[1]
    ART=REPO/'data/generated/corolla_8965H1202000_static_coverage_matrix.json'
    TOOL=REPO/'tools/build_corolla_h_static_coverage_matrix.py'
    d=json.loads(ART.read_text());s=d['summary'];rows=d['functions']
    print('\n== denominator ==')
    check('matrix covers all 1113 named canonical functions',s['named_function_count']==1113==len(rows))
    check('coverage counts sum to denominator',sum(s['coverage_counts'].values())==1113)
    check('all 288 exact named transfers remain verified exact',s['coverage_counts']['verified-exact-body-transfer']==288)
    check('some changed/structural entries are promoted only by later evidence',s['coverage_counts'].get('target-native-inspected-unique-shape',0)>0 and s['coverage_counts'].get('target-native-role-recovered',0)>0 and s['coverage_counts'].get('target-surface-recensused',0)>0)
    check('canonical named denominator has zero genuinely unresolved rows',s['genuinely_unresolved_count']==0)
    check('all former structural-only candidates now have target-native inspection evidence',s['structural_candidate_only_count']==0)
    print('\n== promotion evidence discipline ==')
    check('target-native-inspected rows always name evidence files',all(r['target_native_evidence_files'] for r in rows if r['coverage']=='target-native-inspected-unique-shape'))
    check('target-native role-recovered rows always carry explicit role records and evidence',all(r['role_recovery'] and r['target_native_evidence_files'] for r in rows if r['coverage']=='target-native-role-recovered'))
    check('all eight scheduler-system changed roles remain target-native recovered',s['tag_coverage_counts']['scheduler_system'].get('target-native-role-recovered')==8 and s['tag_coverage_counts']['scheduler_system'].get('genuinely-unresolved',0)==0)
    check('all nine CAN/COM changed roles are target-native recovered',s['tag_coverage_counts']['can_com'].get('target-native-role-recovered')==9 and s['tag_coverage_counts']['can_com'].get('genuinely-unresolved',0)==0)
    check('all three storage/NvM changed roles are target-native recovered',s['tag_coverage_counts']['storage_nvm'].get('target-native-role-recovered')==3 and s['tag_coverage_counts']['storage_nvm'].get('genuinely-unresolved',0)==0)
    check('all four XCP changed roles are target-native recovered',s['tag_coverage_counts']['xcp'].get('target-native-role-recovered')==4 and s['tag_coverage_counts']['xcp'].get('genuinely-unresolved',0)==0)
    check('all five newly mapped motor-control roles are target-native recovered',all(any(r['reference_name']==name and r['coverage']=='target-native-role-recovered' for r in rows) for name in ('motor_coord_transform_calib_handler','dq_current_pi_axis_b','motor0_inverse_rotating_frame_transform','motor1_inverse_rotating_frame_transform','tauj0_ch0_motor_control_worker')) and s['tag_coverage_counts']['motor_control'].get('genuinely-unresolved',0)==0)
    check('axis-A motor PI structural candidate is promoted by target-native evidence',any(r['reference_name']=='dq_current_pi_axis_a' and r['coverage']=='target-native-inspected-unique-shape' for r in rows))
    check('all 42 remaining SecOC/ICU-S roles are target-native recovered',s['tag_coverage_counts']['secoc_icus'].get('genuinely-unresolved',0)==0 and s['tag_coverage_counts']['secoc_icus'].get('target-native-role-recovered')==44)
    check('all seven remaining crypto roles are target-native recovered',s['tag_coverage_counts']['crypto'].get('genuinely-unresolved',0)==0 and s['tag_coverage_counts']['crypto'].get('target-native-role-recovered')==14)
    check('remaining steering residue is fully closed without fake latch homologs',s['tag_coverage_counts']['steering'].get('genuinely-unresolved',0)==0 and s['tag_coverage_counts']['steering'].get('target-native-role-recovered')==6 and s['tag_coverage_counts']['steering'].get('target-surface-recensused')==6)
    check('remaining diagnostics residue is fully closed',s['tag_coverage_counts']['diagnostics'].get('genuinely-unresolved',0)==0 and s['tag_coverage_counts']['diagnostics'].get('target-native-role-recovered')==27)
    check('all 11 plausibility-monitor roles are target-native recovered',sum(1 for r in rows if r['reference_name'].startswith('plausibility_monitor_') and r['coverage']=='target-native-role-recovered')==11)
    check('all 18 packet/record/bounded adapter roles are target-native recovered',sum(1 for r in rows if (r['reference_name'].startswith('packet_low_selector_') or r['reference_name'].startswith('record_operation_') or r['reference_name'].startswith('bounded_api_wrapper_')) and r['coverage']=='target-native-role-recovered')==18)
    check('all 12 preserved veneer-derived roles are target-native recovered',sum(1 for r in rows if r.get('role_recovery') and r['role_recovery'].get('report')=='data/generated/corolla_8965H1202000_veneer_bank.json')==12)
    check('all 10 deleted veneer-derived roles are surface-recensused',sum(1 for r in rows if 'high-page-veneer-bank-complete-recensus' in r.get('surface_recensus',[]))==10)
    check('all 33 configured application callback roles are target-native recovered',sum(1 for r in rows if r.get('role_recovery') and r['role_recovery'].get('report')=='data/generated/corolla_8965H1202000_application_callback_tables.json')==33)
    check('all four removed async-operation callback roles are surface-recensused',sum(1 for r in rows if 'application-async-operation-complete-table-recensus' in r.get('surface_recensus',[]))==4)
    check('all 33 final named-residue successors are target-native recovered',sum(1 for r in rows if r.get('role_recovery') and r['role_recovery'].get('report')=='data/generated/corolla_8965H1202000_final_named_residue.json')==33)
    check('all three keyless event-formatter roles are target-native recovered',sum(1 for r in rows if r.get('role_recovery') and r['role_recovery'].get('report')=='data/generated/corolla_8965H1202000_keyless_event_formatter.json')==3)
    check('removed boot TAUJ0 CH2 role is recensused, not falsely mapped',sum(1 for r in rows if 'boot-eiint-complete-table-recensus' in r.get('surface_recensus',[]))==1 and any(r['reference_name']=='boot_tauj0_ch2_isr' and r['coverage']=='target-surface-recensused' for r in rows))
    check('238 total roles are target-native recovered',s['coverage_counts'].get('target-native-role-recovered')==238)
    check('all 88 deadline callbacks are closed by complete target recensus',sum(1 for r in rows if r['reference_name'].startswith('deadline_') and r['coverage']=='target-surface-recensused')==88)
    check('global genuinely-unresolved denominator is zero',s['genuinely_unresolved_count']==0)
    check('all 96 former structural-only rows retain target-native structural-residue evidence',sum(1 for r in rows if r['coverage']=='target-native-inspected-unique-shape' and 'data/generated/corolla_8965H1202000_structural_residue_decompiler_evidence.json' in r.get('target_native_evidence_files', []))==96)
    check('final evidence-class distribution is pinned',s['coverage_counts']=={'verified-exact-body-transfer':288,'target-native-role-recovered':238,'target-surface-recensused':461,'target-native-inspected-unique-shape':126})
    check('surface-recensused rows always name an explicit complete recensus',all(r['surface_recensus'] for r in rows if r['coverage']=='target-surface-recensused'))
    check('no structural-only rows remain',not any(r['coverage']=='structural-candidate-only' for r in rows))
    check('genuinely unresolved rows have neither target-native evidence nor surface recensus',all(not r['target_native_evidence_files'] and not r['surface_recensus'] for r in rows if r['coverage']=='genuinely-unresolved'))
    check('H-native inspected additions without unique S pair are counted separately',s['h_native_evidence_functions_without_unique_sienna_pair']>0)


def _section_steering_nested():
    print('== steering nested ==')
    """Verify closure of the nine remaining named Corolla-H steering roles."""
    import hashlib,json
    from pathlib import Path
    ROOT=Path(__file__).resolve().parents[1]
    ART=ROOT/'data/generated/corolla_8965H1202000_steering_nested.json'; EV=ROOT/'data/generated/corolla_8965H1202000_steering_nested_decompiler_evidence.json'; TOOL=ROOT/'tools/build_corolla_h_steering_nested.py'; RAW=ROOT/'community/albinoelephant/raw-20260818/albinoelephant-corolla-2023.20260814-0023/dump_codeflash_00000000_00200000_20260814-025814.bin'
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


def _section_steering_supervisor():
    print('== steering supervisor ==')
    """Verify the 8965H1202000 steering-supervisor stage ledger."""
    import json
    from pathlib import Path
    REPO=Path(__file__).resolve().parents[1]
    ART=REPO/'data/generated/corolla_8965H1202000_steering_supervisor_stage_ledger.json'
    TOOL=REPO/'tools/build_corolla_h_steering_supervisor_stage_ledger.py'
    d=json.loads(ART.read_text());r=d['roots'];s=d['summary']
    print('\n== stage denominator ==')
    check('Sienna root is CB86E / 424 bytes',r['sienna']=='0xCB86E' and r['sienna_body_size']==424)
    check('H root is CEDAE / 534 bytes',r['corolla_h']=='0xCEDAE' and r['corolla_h_body_size']==534)
    check('direct stage counts are 94 -> 123',(r['sienna_direct_stage_count'],r['corolla_h_direct_stage_count'])==(94,123))
    check('83 stages are order-paired',s['paired']==83)
    check('33 pairs are unique exact instruction-shape transfers',s['paired_unique_exact_shape']==33)
    check('40 H stages are order-unpaired',s['h_order_unpaired']==40)
    check('11 Sienna stages are order-unpaired',s['sienna_order_unpaired']==11)
    check('every H-unpaired stage has a bounded role class',len(d['h_order_unpaired'])==40 and all(x['role_class'] and x['bounded_description'] for x in d['h_order_unpaired']))
    print('\n== command-specific transfer boundary ==')
    def pair(sa,ha):
     return next((x for x in d['stages'] if x.get('sienna_entry')==sa and x.get('h_entry')==ha),None)
    check('S clamp/gain -> H C91B6 is exact-shape',pair('0xC853A','0xC91B6')['pair_evidence']=='unique-exact-instruction-shape')
    check('S rate-limit -> H C9232 is exact-shape',pair('0xC85B6','0xC9232')['pair_evidence']=='unique-exact-instruction-shape')
    removed={x['sienna_entry']:x for x in d['sienna_order_unpaired']}
    check('authenticated 131 smoothing C8DE0 is order-unpaired',removed['0xC8DE0']['role_class']=='sienna_lta_angle_command')
    replacement=d['explicit_command_mode_boundary']['replacement_command']
    check('replacement command is protected B6 target angle','0x0B6 signal255' in replacement and 'signal254' in replacement)
    check('replacement command carries current closed B6 semantics','1024/17870 deg/count' in replacement and 'PCS/LDA/Hands Off LTA/LTA-LCA/PDA' in replacement and '7-foreground-tick' in replacement and 'modulo-64' in replacement)
    check('replacement command preserves remaining boundaries','literal OEM signal255 unit' in replacement and 'stock wall-clock sender cadence/template' in replacement and 'upstream producer/SecOC signing contract remain bounded' in replacement and 'exclusive replacement freshness progression is closed separately' in replacement and 'Physical scale and exact OEM mode names remain open' not in replacement)
    check('replacement command proof linked',d['explicit_command_mode_boundary']['canonical_proof']=='data/generated/corolla_8965H1202000_b6_target_angle_ingress.json')
    print('\n== H expansion classification ==')
    roles=s['h_unpaired_role_counts']
    check('H expansion includes B6 mode/validity/status stages',roles['b6_mode_table']==roles['b6_validity_gate']==roles['b6_status_export']==1)
    check('H expansion has eight dual-channel plausibility stages',roles['h_dual_channel_plausibility']==8)
    check('H expansion has three motion-state estimator stages',roles['h_motion_state_estimator']==3)
    check('H expansion has two geometry-estimator stages',roles['h_geometry_estimation']==2)
    check('H expansion has three supervisor fault monitors',roles['supervisor_fault_monitor']==3)
    check('all 40 H-unpaired roles are counted',sum(roles.values())==40)


def _section_storage_nvm():
    print('== storage nvm ==')
    """Verify Corolla H storage/NvM role recovery and persistence boundary."""
    import hashlib,json,struct
    from pathlib import Path
    ROOT=Path(__file__).resolve().parents[1]
    ART=ROOT/'data/generated/corolla_8965H1202000_storage_nvm.json';EV=ROOT/'data/generated/corolla_8965H1202000_storage_nvm_decompiler_evidence.json';BUILD=ROOT/'tools/build_corolla_h_storage_nvm.py';DF=ROOT/'data/generated/corolla_2023_albino_dataflash_analysis.json'
    HRAW=ROOT/'community/albinoelephant/raw-20260818/albinoelephant-corolla-2023.20260814-0023/dump_codeflash_00000000_00200000_20260814-025814.bin';SI=ROOT/'firmware/RH850_P1M-E_CodeFlash.bin'
    a=json.loads(ART.read_text());e=json.loads(EV.read_text());df=json.loads(DF.read_text());H=HRAW.read_bytes()[:0x100000];S=SI.read_bytes();by={int(x['entry'],16):x for x in e['functions']}
    print('== deterministic artifact ==')
    print('\n== compact evidence ==')
    check('H codeflash hash pinned',sha(H)==e['image']['codeflash_sha256']==a['images']['h_sha256']);check('three H functions compacted',e['function_count']==3==len(e['functions']))
    check('all raw H bodies validate',all(sha(H[int(x['entry'],16):int(x['entry'],16)+x['body_size']])==x['body_sha256'] for x in e['functions']))
    check('all H decompiler hashes validate',all(sha(x['decompiled_c'].encode())==x['decompiled_c_sha256'] for x in e['functions']))
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


def _section_structural_residue_inspection():
    print('== structural residue inspection ==')
    import hashlib,json
    from pathlib import Path
    ROOT=Path(__file__).resolve().parents[1]
    ART=ROOT/'data/generated/corolla_8965H1202000_structural_residue_decompiler_evidence.json'
    STRUCT=ROOT/'data/generated/corolla_8965H1202000_structural_function_transfer.json'
    HRAW=ROOT/'community/albinoelephant/raw-20260818/albinoelephant-corolla-2023.20260814-0023/dump_codeflash_00000000_00200000_20260814-025814.bin'
    d=json.loads(ART.read_text());st=json.loads(STRUCT.read_text());h=HRAW.read_bytes()[:0x100000]
    check('software/image identity pinned',d['software_id']=='8965H1202000' and d['image']['codeflash_sha256']==sha(h))
    check('exactly 96 inspected candidates',d['function_count']==96 and len(d['functions'])==96)
    check('reference and target entries are each unique',len({x['reference_entry'] for x in d['functions']})==96 and len({x['entry'] for x in d['functions']})==96)
    check('all H bodies raw-bound',all(sha(h[int(x['entry'],16):int(x['entry'],16)+x['body_size']])==x['body_sha256'] for x in d['functions']))
    check('all decompiler payloads hash-bind',all(sha(x['decompiled_c'].encode())==x['decompiled_c_sha256'] and x['decompiled_c'] for x in d['functions']))
    sm={int(x['reference_entry'],16):x for x in st['matches']}
    check('every inspected pair is the structural artifact target',all(int(x['reference_entry'],16) in sm and int(x['entry'],16)==int(sm[int(x['reference_entry'],16)]['target_entry'],16) for x in d['functions']))
    check('every inspected pair is unique-exact-shape',all(sm[int(x['reference_entry'],16)]['classification']=='unique-exact-shape' for x in d['functions']))
    check('all structural body sizes agree with target evidence',all(int(sm[int(x['reference_entry'],16)]['body_size_target'])==x['body_size'] for x in d['functions']))
    check('inspection boundary explicitly avoids semantic homology','does not assert semantic-role' in d['static_conclusion']['boundary'])


def _section_supervisor_external_ingress():
    print('== supervisor external ingress ==')
    """Verify the H generated-COM -> steering-supervisor ingress census."""
    import hashlib,json
    from pathlib import Path
    REPO=Path(__file__).resolve().parents[1]
    ART=REPO/'data/generated/corolla_8965H1202000_supervisor_external_ingress_census.json'
    HRAW=REPO/'community/albinoelephant/raw-20260818/albinoelephant-corolla-2023.20260814-0023/dump_codeflash_00000000_00200000_20260814-025814.bin'
    SIMG=REPO/'firmware/RH850_P1M-E_CodeFlash.bin'
    hsrc=HRAW.read_bytes();h=hsrc[:0x100000];s=SIMG.read_bytes();d=json.loads(ART.read_text())
    print('== image/corpus evidence boundary ==')
    check('H normalized image hash is pinned',sha(h)==d['images']['corolla_h_sha256'])
    check('Sienna image hash is pinned',sha(s)==d['images']['sienna_sha256'])
    check('census uses corrected fixed-map model','fixed-map-snapshot' in d['evidence_boundary'] and 'corrected-context' in d['evidence_boundary'])
    check('schema v2',d['schema']=='corolla-8965H1202000-supervisor-external-ingress-census-v2')
    check('H COM data-offset table is recovered',d['summary']['h_offset_table']=='0x22788')
    check('S COM data-offset table is uniquely recovered in generated-data region',0x22000 <= int(d['summary']['s_offset_table'],16) < 0x23000)
    print('\n== exact consumer binding ==')
    check('census contains external supervisor references',len(d['external_refs'])>0)
    all_hash=True
    all_unpack=True
    for row in d['external_refs']:
     entry=row['consumer']; size=row['consumer_body_size']
     all_hash &= sha(h[entry:entry+size])==row['consumer_body_sha256']
     for u in row['source_unpackers']:
      all_unpack &= sha(h[u['entry']:u['entry']+u['body_size']])==u['body_sha256']
    check('every cited consumer raw-body hash validates',all_hash)
    check('every cited source-unpacker raw-body hash validates',all_unpack)
    print('\n== replacement-command closure ==')
    changed=[x for x in d['external_refs'] if x['wire_class']!='shared_wire_field']
    check('all H-only/wire-changed supervisor fields are from B6',bool(changed) and all(x['can']==0xB6 for x in changed))
    check('no non-B6 changed wire field reaches mapped supervisor cone',not [x for x in changed if x['can']!=0xB6])
    large=d['potential_changed_large_fields']
    check('only changed >=12-bit ingress is B6 signal255',bool(large) and {(x['can'],x['signal'],x['bits'],x['signed'],x['wire_byte']) for x in large}=={(0xB6,255,16,1,4)})
    positive=d['positive_changed_large_field']
    check('positive B6 signal255 fixed-map path exact',positive['raw']=='0xFEBE7D94' and positive['stage']=='0xFEBEF1CC' and positive['snapshot']=='0xFEBEAE82')
    check('positive B6 signal255 reaches steering cone',positive['consumer_entries']==['0x000C86E8','0x000C87FC','0x000C9DB0'])
    active_b6={x['signal'] for x in changed if x['can']==0xB6}
    check('exact fixed-map B6 supervisor field set is pinned',active_b6 == {254,255,258,260,261,262,263,264})
    check('all changed B6 fields except signal255 are sub-12-bit',all(x['bits']<12 for x in changed if x['signal']!=255))
    print('\n== shared-CAN boundary ==')
    shared_nonb6=[x for x in d['external_refs'] if x['can']!=0xB6]
    check('non-B6 external supervisor refs are same-wire fields on Sienna',bool(shared_nonb6) and all(x['wire_class']=='shared_wire_field' for x in shared_nonb6))
    check('shared FD025 cannot become an H-only wire-field source',all(x['wire_class']=='shared_wire_field' for x in d['external_refs'] if x['can']==0x25))
    check('census walks a nontrivial H supervisor call cone',d['summary']['h_cone_functions']>100)
    check('census tracks nontrivial generated COM staging/snapshot state',d['summary']['h_com_stage_cells']>20 and d['summary']['h_com_snapshot_cells']>20)


def _section_system_orchestration():
    print('== system orchestration ==')
    """Verify target-native Corolla 8965H1202000 system/orchestration recovery."""

    import hashlib
    import json
    from pathlib import Path

    ROOT = Path(__file__).resolve().parents[1]
    ART = ROOT / "data/generated/corolla_8965H1202000_system_orchestration.json"
    EVIDENCE = ROOT / "data/generated/corolla_8965H1202000_system_orchestration_decompiler_evidence.json"
    BUILDER = ROOT / "tools/build_corolla_h_system_orchestration.py"
    HRAW = ROOT / "community/albinoelephant/raw-20260818/albinoelephant-corolla-2023.20260814-0023/dump_codeflash_00000000_00200000_20260814-025814.bin"


    art = json.loads(ART.read_text())
    ev = json.loads(EVIDENCE.read_text())
    h = HRAW.read_bytes()[:0x100000]

    print("== deterministic artifact ==")
    print("\n== evidence binding ==")
    check("H image hash is pinned", sha(h) == ev["image"]["codeflash_sha256"] == art["images"]["corolla_h_sha256"])
    check("25 contiguous H functions are compacted", ev["function_count"] == 25 == len(ev["functions"]))
    check("all contiguous H body hashes validate",
          all(sha(h[int(r["entry"],16):int(r["entry"],16)+r["body_size"]]) == r["body_sha256"] for r in ev["functions"]))
    check("all compacted H decompilation hashes validate",
          all(sha(r["decompiled_c"].encode()) == r["decompiled_c_sha256"] for r in ev["functions"]))
    reset = ev["reset_0x1f2"]
    check("reset 0x1F2 is explicitly non-contiguous", reset["entry"] == "0x000001F2" and "non-contiguous" in reset["body_boundary"])
    check("all reset raw windows validate",
          all(sha(h[int(w["start"],16):int(w["start"],16)+w["size"]]) == w["sha256"] for w in reset["raw_windows"]))

    print("\n== scheduler/system closure ==")
    closure = art["scheduler_system_closure"]
    expected = {
        "0x000001F2":"0x000001F2", "0x00058404":"0x0005389C", "0x00062758":"0x0005CAAC",
        "0x000B0518":"0x000B05D0", "0x000B28AC":"0x000B2692", "0x000BA43A":"0x000B8EE4",
        "0x000BD10E":"0x000BBFE6", "0x000BEC4C":"0x000BD954",
    }
    check("all eight scheduler/system residual roles are mapped", art["scheduler_system_closure_count"] == 8 and
          {r["reference_entry"]:r["target_entry"] for r in closure} == expected)
    by_ref = {r["reference_entry"]:r for r in closure}
    check("H periodic generated task remains flat/no-branch", by_ref["0x00058404"]["target_metrics"]["if_count"] == 0 and
          by_ref["0x00058404"]["target_metrics"]["switch_count"] == 0 and
          by_ref["0x00058404"]["target_metrics"]["unique_direct_call_count"] == 333)
    check("H one-shot subsystem init remains no-branch", by_ref["0x000BD10E"]["target_metrics"]["if_count"] == 0 and
          by_ref["0x000BD10E"]["target_metrics"]["unique_direct_call_count"] == 94)
    check("H telemetry snapshot body is target-native 2654 bytes", by_ref["0x000BA43A"]["target_metrics"]["body_size"] == 2654)
    check("H transition phase initializer retains 26-byte/one-call shape", by_ref["0x000B28AC"]["target_metrics"] == {
        "body_size":26,"direct_call_count":1,"unique_direct_call_count":1,"if_count":0,"switch_count":0,"loop_count":0})
    markers = by_ref["0x000001F2"]["target_evidence"]["static_markers"]
    check("H reset decision retains FCU/marker constants and terminal loop", all(markers.values()))

    print("\n== mode coordinator ==")
    mode = art["mode_coordinator"]
    expected_query = [0,9,5,0,1,9,3,0,1,9,6,12,0,1,9,6,11,7,0,1,9,4,7,2,0,9,10,7,14,15,9,2,7,0,13,8,1,9]
    expected_clear = [0,0,1,9,0,1,9,12,0,1,9,6,0,1,9,2,0,9,7,2,15,0,8,1]
    check("mode event-query sequence is exactly preserved", mode["query_sequences_identical"] and mode["event_query_sequence"] == expected_query)
    check("mode event-clear sequence is exactly preserved", mode["clear_sequences_identical"] and mode["event_clear_sequence"] == expected_clear)
    check("mode coordinator keeps 47 branch tests", mode["sienna_metrics"]["if_count"] == mode["h_metrics"]["if_count"] == 47)
    check("mode coordinator body size remains near-identical", mode["sienna_metrics"]["body_size"] == 1014 and mode["h_metrics"]["body_size"] == 1016)

    print("\n== per-tick wiring delta ==")
    tick = art["per_tick_dispatch"]
    check("guard denominator is 74 -> 64", tick["sienna_guard_count"] == 74 and tick["h_guard_count"] == 64)
    check("guard diff is one contiguous 10-guard deletion", len(tick["guard_diff"]) == 1 and
          tick["guard_diff"][0]["opcode"] == "delete" and len(tick["guard_diff"][0]["sienna_guards"]) == 10 and
          tick["guard_diff"][0]["h_guards"] == [])
    check("deleted guard region includes both Sienna 0x520 branches",
          tick["guard_diff"][0]["sienna_guards"].count("if (param_2 == 0x520) {") == 2)
    check("H full dispatcher has no 0x520 guard", tick["sienna_has_0x520_guard"] and not tick["h_has_0x520_guard"])
    check("deleted block includes known Sienna B763C helper", "FUN_000b763c" in tick["sienna_only_post_coordinator_calls"])
    check("H full dispatcher preserves telemetry -> coordinator -> snapshot order",
          tick["h_major_call_order"] == ["FUN_000b8ee4","FUN_000b05d0","FUN_000bba48"] and
          tick["h_major_call_positions"]["FUN_000b8ee4"] <
          tick["h_major_call_positions"]["FUN_000b05d0"] <
          tick["h_major_call_positions"]["FUN_000bba48"])
    reduced = art["reduced_per_tick_companion"]
    check("H reduced/current-mode dispatcher keeps same major trio", reduced["h_calls"] == ["FUN_000b8ee4","FUN_000b05d0","FUN_000bba48"])
    check("reduced dispatcher shrinks 504 -> 460 bytes", reduced["sienna_metrics"]["body_size"] == 504 and reduced["h_metrics"]["body_size"] == 460)

    print("\n== startup / wrappers / regenerated copy surface ==")
    start = art["startup_and_wrappers"]
    check("H startup coordinator enables IRQ", start["startup"]["enables_irq"])
    check("H startup coordinator tail is foreground loop call", start["startup"]["last_explicit_fun_call"] == "FUN_0005f30c")
    check("subsystem-init veneer targets BBFE6", "FUN_000bbfe6();" in start["subsystem_init_wrapper"]["wrapper_code"])
    check("per-tick veneer forwards three args to BD954", "FUN_000bd954(param_1,param_2,param_3);" in start["per_tick_wrapper"]["wrapper_code"])
    check("transition phase init writes shifted FEBEB160-162 state", all(x in start["transition_phase_init"]["code"] for x in ("0xfebeb162","0xfebeb160","0xfebeb161")))
    rte = art["regenerated_com_rte_surface"]
    check("H shared Rx consumer fragment has five recovered generated callers", rte["consumer_fragment_callers_within_evidence"] ==
          ["0x0005389C","0x00058450","0x0005886A","0x000589A8","0x00058B3C"])
    check("H RTE copy banks are split across three pinned wrappers", rte["rte_copy_banks"] == [
        {"target":"0x00056970","wrapper":"0x00052E4C"},
        {"target":"0x0005701E","wrapper":"0x00052EEE"},
        {"target":"0x0005722E","wrapper":"0x00052FEC"},
    ])
    check("report preserves non-1:1 COM/RTE boundary", "do not infer canonical one-to-one" in rte["boundary"])
    check("static conclusion closes scheduler residue without claiming all COM helpers", art["static_conclusion"]["scheduler_system_residue_closed"] and
          "not every generated COM helper" in art["static_conclusion"]["remaining_boundary"])


def _section_techstream_correlations():
    print('== techstream correlations ==')
    """Verify the Techstream ↔ Corolla 8965H1202000 steering correlation."""

    import hashlib
    import json
    from pathlib import Path

    REPO = Path(__file__).resolve().parents[1]
    ART = REPO / "data/generated/corolla_8965H1202000_techstream_correlations.json"
    EVID = REPO / "data/generated/corolla_8965H1202000_techstream_steering_decompiler_evidence.json"
    TOOL = REPO / "tools/build_corolla_h_techstream_correlations.py"
    RAW = REPO / "community/albinoelephant/raw-20260818/albinoelephant-corolla-2023.20260814-0023/dump_codeflash_00000000_00200000_20260814-025814.bin"
    TECHROOT = REPO / "software/Techstream/v18/unpacked/toyota/Toyota Diagnostics/Techstream"


    d = json.loads(ART.read_text())
    e = json.loads(EVID.read_text())
    raw = RAW.read_bytes()

    print("\n== source identity ==")
    check("tracked raw Corolla dump is 2 MiB", len(raw) == 0x200000)
    check("report binds raw Corolla dump", sha(raw) == d["sources"]["corolla_codeflash"]["sha256"])
    for key, rel in (("na_emps_p5", "NA/DB/EMPS_P5.ddb"), ("na_emps2_p5", "NA/DB/EMPS2_P5.ddb")):
        src = TECHROOT / rel
        check(f"{rel} hash matches pinned semantics", sha(src.read_bytes()) == d["sources"][key]["sha256"])

    print("\n== compact target-native evidence ==")
    check("40 H functions support the Techstream steering/current/DTC joins", e["function_count"] == 40)
    for row in e["functions"]:
        start = int(row["entry"], 16); size = row["body_size"]
        check(f"raw body hash {row['entry']}", sha(raw[start:start+size]) == row["body_sha256"])

    print("\n== recovered P5 data-ID layout ==")
    for name in ("emps_p5", "emps2_p5"):
        x = d["data_id_layout_recovery"][name]
        check(f"{name} primary data-ID words resolve except sentinel",
              x["primary_nonzero_count"] == x["primary_resolves_in_type61_or_fffe"])
        check(f"{name} alternate data-ID words all resolve",
              x["alternate_nonzero_count"] == x["alternate_resolves_in_type61"])
    check("P5 list host uses support-ID filtering", "CheckSupportPid" in d["data_id_layout_recovery"]["host_consumer"])

    print("\n== Corolla vocabulary fit ==")
    ov = d["ddb_overlap"]
    check("H has 226 readable RDBI DIDs", ov["h_readable_did_count"] == 226)
    check("EMPS_P5 overlaps 124 H DIDs", ov["emps_p5"]["h_type61_overlap_count"] == 124)
    check("EMPS_P5 yields 137 H-supported named monitor rows", ov["emps_p5"]["h_supported_monitor_rows"] == 137)
    check("EMPS2_P5 overlap is smaller", ov["emps2_p5"]["h_type61_overlap_count"] == 112)

    print("\n== Command Value Torque exact join ==")
    t = d["command_value_torque"]
    check("monitor 402 is Command Value Torque in Nm",
          t["techstream"]["monitor_key"] == 402 and t["techstream"]["name"] == "Command Value Torque" and t["techstream"]["unit"] == "Nm")
    check("monitor 402 primary/alternate IDs are 1C02/3C02",
          t["techstream"]["primary_data_id"] == "0x1C02" and t["techstream"]["alternate_data_id"] == "0x3C02")
    check("H DID 1C02 is a live 2-byte callback", t["corolla_h_rdbi"]["callback"] == "0x000495A0" and t["corolla_h_rdbi"]["callback_classification"] == "direct_fixed" and t["corolla_h_rdbi"]["declared_length"] == 2)
    check("H DID 1C02 formula is recovered", t["corolla_h_rdbi"]["formula_recovered"])
    check("all target-native producer-chain relations are recovered", all(x["recovered"] for x in t["target_native_producer_chain"]))
    check("active pipeline order is CD55A -> CD5DC -> CE928",
          t["target_native_producer_chain"][-1]["relation"].endswith("CD55A -> CD5DC -> CE928 in order"))

    print("\n== motor-current bridge ==")
    b = d["motor_current_bridge"]
    mon = b["techstream_monitors"]
    check("Q actual/command and D actual/command monitors are 16-bit amperes",
          all(mon[str(k)]["bit_width"] == 16 and mon[str(k)]["unit"] == "A" for k in (251, 252, 253, 254)))
    check("Q current command is DID 1152", mon["252"]["primary_data_id"] == "0x1152" and mon["252"]["name"] == "Command Value Current (Q Axis)")
    check("D current command is DID 1154", mon["254"]["primary_data_id"] == "0x1154" and mon["254"]["name"] == "Command Value Current 2 (D Axis)")
    check("final Q current limit is DID 1156", mon["256"]["primary_data_id"] == "0x1156" and mon["256"]["name"] == "Final Motor Current Limited (Q Axis)" and mon["256"]["unit"] == "A")
    check("internal command torque has complete static Q-current bridge", all(x["recovered"] for x in b["q_axis_command_chain"]))
    check("Q-current bridge reaches compensated-command minus raw-feedback error stage",
          any(x["entry"] == "0x00032934" and "FEBE6BB8" in x["relation"] and "FEBE6BB4" in x["relation"] for x in b["q_axis_command_chain"]))
    check("Q-current bridge reaches dedicated PI stage",
          any(x["entry"] == "0x000329A0" and "PI" in x["relation"] for x in b["q_axis_command_chain"]))
    check("actual q/d current observers have complete target-native chain", all(x["recovered"] for x in b["q_axis_actual_chain"]))
    check("D-axis current command is recovered as separate motor-internal path", all(x["recovered"] for x in b["d_axis_command_chain"]))
    check("Q-axis current-limit observer chain is complete", all(x["recovered"] for x in b["q_axis_limit_chain"]))
    check("Q command chain explicitly passes through C3D2 -> C3D6 -> C3D4",
          b["q_axis_command_chain"][0]["entry"] == "0x000CD5DC" and b["q_axis_command_chain"][1]["entry"] == "0x000CD644")

    print("\n== steering-state diagnostic bridge ==")
    sb = d["steering_state_bridge_diagnostics"]
    tq = sb["steering_wheel_torque"]
    check("Steering Wheel Torque DID 1035 is signed Nm/3 decimals", tq["primary_data_id"] == "0x1035" and tq["name"] == "Steering Wheel Torque" and tq["signed"] and tq["unit"] == "Nm" and tq["decimal_point_count"] == 3 and tq["mul"] == tq["div"] == 1)
    ready = sb["ready_status_oracle"]
    check("Ready Status DID 1033 is exact boolean diagnostic oracle", ready["primary_data_id"] == "0x1033" and ready["name"] == "Ready Status" and ready["source_chain"] == ["0xFEBE7D1B", "0xFEBEF052", "0xFEBEB5A8", "0xFEBEE811", "DID 0x1033"] and ready["conversion"]["data_range"] == [0, 1])
    elec = sb["0x351_motor_b_terminal_voltage_monitor"]
    check("0x351 electrical monitor joins exact enabled C159B49", elec["dem_event"] == 4 and elec["dtc"]["h_dtc_index"] == 54 and elec["dtc"]["enabled_word"] == 1 and elec["dtc"]["techstream_code"] == "C159B49")
    check("C159B49 carries exact Toyota description/failure", elec["dtc"]["techstream_description"] == 'Power Steering Motor "B" Terminal Voltage Detect Circuit' and elec["dtc"]["techstream_failure"] == "Internal Electronic Failure")
    check("C159B49 path does not name whole 0x351 packet", "does not name the whole packet" in elec["interpretation"] and "force-7 override" in elec["interpretation"])
    qactual = b["techstream_monitors"]["251"]
    check("Q actual current conversion is signed A/2 decimals", qactual["primary_data_id"] == "0x1151" and qactual["signed"] and qactual["unit"] == "A" and qactual["decimal_point_count"] == 2 and qactual["mul"] == qactual["div"] == 1)

    print("\n== Techstream surface selection ==")
    ts = d["techstream_surface"]
    check("EMPS_P5 master route is category405 generation20", ts["na_master_category_id"] == 405 and ts["na_master_generation"] == 20)
    check("EMPS_P5 is master-routed in NA/EU/JP while EMPS2_P5 is not", ts["emps_p5_master_routed_regions"] == ["NA","EU","JP"] and ts["emps2_p5_master_route_count"] == 0)
    check("EMPS_P5 parsed section set is P5 monitor/behavior only", ts["section_types"] == [61,62,63,80,87,88,90,91])
    check("no classic type11/12 Active Test table is present", ts["classic_active_test_section_types_present"] == [])
    check("category405 routes no Active Test or Routine-named DLL", ts["active_test_named_dlls"] == [] and ts["routine_named_dlls"] == [])
    check("Cooperation Control State DID106A is a success stub", ts["cooperation_control_state"]["primary_data_id"] == "0x106A" and ts["cooperation_control_state"]["h_callback_classification"] == "success_stub")

    print("\n== communication-monitor DTC join ==")
    cm = d["communication_monitor_dtc"]
    check("communication monitor is a six-row target-native family", cm["row_count"] == 6 and all(cm["target_native_checks"].values()))
    check("six monitor rows resolve to 025/D7/D0/3B0/D5/B6", [x["can_id"] for x in cm["rows"]] == ["0x025","0x0D7","0x0D0","0x3B0","0x0D5","0x0B6"])
    check("D7/D5/B6 share Brake System Control Module missing-message DTC", cm["brake_missing_message_can_ids"] == ["0x0D7","0x0D5","0x0B6"])
    b6 = next(x for x in cm["rows"] if x["can_id"] == "0x0B6")
    check("B6 monitor is row5 slot18 PDU42", b6["row_index"] == 5 and b6["status_slot"] == "0x18" and b6["pdu_id"] == 42)
    check("B6 maps event0143 to H DTC index82 C12987", b6["dem_event"] == "0x0143" and b6["dtc"]["h_dtc_index"] == 82 and b6["dtc"]["packed_dtc"] == "0xC12987")
    check("Techstream names B6 source as brake-system missing message", b6["dtc"]["techstream_code"] == "U012987" and b6["dtc"]["techstream_description"] == "Lost Communication with Brake System Control Module" and b6["dtc"]["techstream_failure"] == "Missing Message")

    print("\n== complete H DEM event-class/DTC catalog ==")
    fc = d["fault_event_class_catalog"]
    check("242 populated-class DEM events are exhaustively classified", sum(fc["class_counts"].values()) == 242 and fc["event_count_scanned"] == 0x180)
    check("exact class histogram is pinned", fc["class_counts"] == {"0x01":8,"0x02":34,"0x04":1,"0x08":1,"0x0F":1,"0x10":173,"0x20":16,"0x40":1,"0x80":7})
    check("class 0x02 mostly carries named DTCs", fc["classes"]["0x02"]["dtc_indexed_count"] == 32)
    check("class 0x10 is the dominant named fault family", fc["classes"]["0x10"]["dtc_indexed_count"] == 169)
    check("class 0x20 has six named DTC events", fc["classes"]["0x20"]["dtc_indexed_count"] == 6)
    check("internal-only classes retain zero-DTC boundary", all(fc["classes"][x]["dtc_indexed_count"] == 0 for x in ("0x04","0x08","0x0F","0x40","0x80")))
    check("fault catalog does not invent openpilot policy", "do not by themselves define openpilot" in fc["boundary"])

    print("\n== protected brake-profile field semantics ==")
    pb = d["protected_brake_profile_semantics"]
    check("D7 configured/scalar split is 240..247 versus 240/243/246", pb["d7"]["configured_signal_ids"] == list(range(240,248)) and [x["signal_id"] for x in pb["d7"]["scalar_calls"]] == [240,243,246])
    check("D7 only 16-bit scalar is signal243", [x for x in pb["d7"]["scalar_calls"] if x["bit_length"] == 16] == [{"bit_length":16,"bit_offset_in_byte":0,"packed_bit_offset":384,"signal_id":243}])
    check("D7 signal243 is exact DID1185 CAN Vehicle Speed SP1", pb["d7"]["sp1_vehicle_speed"]["signal_id"] == 243 and pb["d7"]["sp1_vehicle_speed"]["primary_data_id"] == "0x1185" and pb["d7"]["sp1_vehicle_speed"]["name"] == "CAN Vehicle Speed (SP1)" and pb["d7"]["sp1_vehicle_speed"]["callback_recovered"])
    check("B6 signal255 role is deferred beyond direct-xref Techstream join", pb["b6"]["largest_scalar_signal_id"] == 255 and pb["b6"]["largest_scalar_role"] == "target-native-role-deferred-to-computed-ingress-provenance")

    print("\n== disabled camera/IPM-A diagnostic residue ==")
    ipm = d["camera_ipm_a_residue"]
    check("H retains U023A87 IPM-A DTC at index93 but disables it", ipm["h_dtc_index"] == 93 and ipm["packed_dtc"] == "0xC23A87" and ipm["techstream_code"] == "U023A87" and ipm["h_enabled_word"] == 0)
    check("Techstream names disabled H residue as Image Processing Module A missing message", ipm["techstream_description"] == 'Lost Communication with Image Processing Module "A"' and ipm["techstream_failure"] == "Missing Message")
    check("removed Sienna IPM monitor set is 2E4/131/191/2FD", ipm["removed_sienna_can_ids"] == ["0x131","0x191","0x2E4","0x2FD"])
    check("all four Sienna IPM rows are absent from H active monitor table", len(ipm["sienna_active_ipm_rows"]) == 4 and all(x["sienna_row_event_matches"] and x["corolla_h_event_dtc_index"] == 93 and not x["corolla_h_active_monitor_row_present"] for x in ipm["sienna_active_ipm_rows"]))
    check("legacy B3 event is disconnected from DTC93 in H", ipm["h_event_b3"]["dtc_index"] == 0)

    print("\n== angle-domain negative ==")
    a = d["modern_angle_domain"]
    check("target-angle monitor family is grouped under 1CEE/1CEF", a["primary_data_ids"] == ["0x1CEE", "0x1CEF"])
    check("H supports none of the 2069..2076 target-angle family", not a["corolla_h_supports_any"] and all(not x["corolla_h_rdbi_supported"] for x in a["rows"]))

    print("\n== interpretation boundary ==")
    c = d["static_conclusion"]
    check("exact H Command Value Torque DID join is asserted", c["command_value_torque_exact_did_join"])
    check("live internal H producer pipeline is asserted", c["command_value_torque_live_internal_pipeline"])
    check("command-torque to Q-current static bridge is asserted", c["command_torque_to_q_current_static_bridge"])
    check("q/d actual current observer closure is asserted", c["q_d_actual_current_observers_recovered"])
    check("D-axis command path is asserted separate", c["d_axis_command_path_separate"])
    check("Q-axis limit observer closure is asserted", c["q_axis_limit_observer_recovered"])
    check("classic Active Test surface remains absent", c["classic_active_test_surface_present"] is False)
    check("live Cooperation Control State monitor remains absent", c["live_cooperation_control_state_monitor"] is False)
    check("B6 brake-system DTC join is asserted", c["b6_brake_system_missing_message_dtc_join"])
    check("D7 command-sized scalar is exact vehicle speed", c["d7_command_sized_scalar_is_vehicle_speed"])
    check("B6 signal255 semantics are deferred to target-native provenance", c["b6_signal255_semantics_deferred_to_target_native_provenance"])
    check("camera/IPM-A DTC is asserted disabled", c["camera_ipm_a_dtc_disabled"])
    check("Sienna active IPM-A monitor rows are asserted removed", c["sienna_ipm_a_monitor_rows_removed_in_h"])
    check("external CAN-field equivalence remains false", c["external_can_field_equivalence"] is False)


def _section_veneer_bank():
    print('== veneer bank ==')
    import hashlib,json
    from pathlib import Path
    ROOT=Path(__file__).resolve().parents[1]; ART=ROOT/'data/generated/corolla_8965H1202000_veneer_bank.json'; TOOL=ROOT/'tools/build_corolla_h_veneer_bank.py'; SRAW=ROOT/'firmware/RH850_P1M-E_CodeFlash.bin'; HRAW=ROOT/'community/albinoelephant/raw-20260818/albinoelephant-corolla-2023.20260814-0023/dump_codeflash_00000000_00200000_20260814-025814.bin'
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
    check('removed low-role boundary is explicit','does not prove' in d['static_conclusion']['boundary'])


def _section_xcp():
    print('== xcp ==')
    """Verify target-native H XCP command residuals."""
    import hashlib,json,struct
    from pathlib import Path
    ROOT=Path(__file__).resolve().parents[1];ART=ROOT/'data/generated/corolla_8965H1202000_xcp.json';EV=ROOT/'data/generated/corolla_8965H1202000_xcp_decompiler_evidence.json';BUILD=ROOT/'tools/build_corolla_h_xcp.py';HRAW=ROOT/'community/albinoelephant/raw-20260818/albinoelephant-corolla-2023.20260814-0023/dump_codeflash_00000000_00200000_20260814-025814.bin'
    a=json.loads(ART.read_text());e=json.loads(EV.read_text());H=HRAW.read_bytes()[:0x100000];by={int(x['entry'],16):x for x in e['functions']}
    check('H hash pinned',sha(H)==e['image']['codeflash_sha256']==a['images']['h_sha256']);check('11 H XCP functions compacted',e['function_count']==11==len(e['functions']));check('all raw bodies validate',all(sha(H[int(x['entry'],16):int(x['entry'],16)+x['body_size']])==x['body_sha256'] for x in e['functions']));check('all decompiler hashes validate',all(sha(x['decompiled_c'].encode())==x['decompiled_c_sha256'] for x in e['functions']))
    exp={'0x000972FA':'0x0009232A','0x00097432':'0x00092462','0x000975EE':'0x0009261E','0x00097668':'0x00092698'};check('four XCP residual roles recovered',a['xcp_role_closure_count']==4 and {x['reference_entry']:x['target_entry'] for x in a['xcp_role_closure']}==exp)
    check('custom selector sequence is unchanged',a['custom_command_table']['selectors']==[0xFB,0xFA,0xF5,0xF3,0xEB,0xEA,0xE4]);check('H command table points at all four recovered handlers',a['custom_command_table']['h_handlers'][1:6:1][0]=='0x0009232A' and a['custom_command_table']['h_handlers'][2]=='0x00092462' and a['custom_command_table']['h_handlers'][4]=='0x0009261E' and a['custom_command_table']['h_handlers'][5]=='0x00092698')
    fa=a['fa_indexed_identifier'];check('FA keeps index<5 behavior',fa['index_limit']==5 and '< 5' in by[0x9232A]['decompiled_c']);f5=a['f5_upload'];check('F5 accepts only lengths 1..7',f5['byte_count_min']==1 and f5['byte_count_max']==7 and all(t in by[0x92462]['decompiled_c'] for t in ('bVar3 == 0','7 < bVar3')));check('F5 range helper covers LocalRAM outer range','0xfebdffff < param_1' in by[0x9238A]['decompiled_c'] and '0xfec00000' in by[0x9238A]['decompiled_c']);check('F5 has five H-specific exclusion ranges',f5['exclusion_count']==5 and len(f5['h_exclusion_ranges'])==5);check('F5 retains special CodeFlash 0x10000..17DEF rule',f5['special_codeflash_copy_check']['length']==0x7DEC and '0x7dec' in by[0x9238A]['decompiled_c'] and 'DAT_00017df0' in by[0x9238A]['decompiled_c']);check('F5 copy helper advances MTA', 'FUN_0007c390' in by[0x92436]['decompiled_c'])
    ps=a['page_state'];check('EB writer and EA reader share H state cells',all(cell.lower().replace('0x','') in (by[0x9261E]['decompiled_c']+by[0x92698]['decompiled_c']).lower() for cell in ps['state_cells']));check('EB writer preserves flag mask and value<2 checks','bVar4 & 3' in by[0x9261E]['decompiled_c'] and 'bVar3 < 2' in by[0x9261E]['decompiled_c']);check('EA reader preserves selectors 1/2',"== '\\x01'" in by[0x92698]['decompiled_c'] and "== '\\x02'" in by[0x92698]['decompiled_c']);check('E4 remains in same custom command table',a['e4_support']['remains_in_same_custom_table'] and a['custom_command_table']['h_handlers'][-1]=='0x00092724');check('application-side F5 primitive explicitly preserved',a['static_conclusion']['application_side_f5_read_primitive_preserved']);check('external reachability remains bounded','external gateway reachability' in a['static_conclusion']['boundary'])


_section_application_callback_tables()
_section_application_diagnostics()
_section_application_interrupt_bodies()
_section_application_interrupt_vectors()
_section_application_transport_residue()
_section_b6_full_receiver_contract()
_section_b6_receiver_contract()
_section_b6_secoc_verification()
_section_b6_target_angle_ingress()
_section_can_com()
_section_crypto_residue()
_section_deadline_monitor_surface()
_section_diagnostic_residue()
_section_direct_call_surface()
_section_fd_control()
_section_final_named_residue()
_section_lta_command_provenance()
_section_motor_control()
_section_openpilot_state_bridge()
_section_plausibility_monitor()
_section_power_supply_monitor_gate()
_section_secoc_key_provenance()
_section_secoc_surface()
_section_small_adapters()
_section_static_coverage()
_section_steering_nested()
_section_steering_supervisor()
_section_storage_nvm()
_section_structural_residue_inspection()
_section_supervisor_external_ingress()
_section_system_orchestration()
_section_techstream_correlations()
_section_veneer_bank()
_section_xcp()
print(f'\nResults: {passed} passed, {failed} failed')
raise SystemExit(1 if failed else 0)
