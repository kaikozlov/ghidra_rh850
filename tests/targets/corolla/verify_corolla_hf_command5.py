#!/usr/bin/env python3
"""Portable Corolla H/F command5 pins: resident runtime carrier, direct command5, and portability.

Domain split; assertions and helpers are carried over verbatim.
"""
from __future__ import annotations
from tools import REPO_ROOT
ROOT = REPO = REPO_ROOT
passed = failed = 0

def check(name, cond, detail=''):
    global passed, failed
    ok = bool(cond)
    passed += int(ok)
    failed += int(not ok)
    suffix = f' ({detail})' if detail else ''
    print(f"[{('PASS' if ok else 'FAIL')}] {name}{suffix}")
print('== corolla hf command5 runtime carrier ==')

def _section_corolla_hf_command5_runtime_carrier():
    import hashlib
    import json
    ROOT = REPO_ROOT
    ART = ROOT / 'data/generated/corolla_hf_command5_runtime_carrier.json'
    EVID = ROOT / 'data/generated/corolla_hf_command5_runtime_carrier_evidence.json'
    BUILDER = ROOT / 'tools/targets/corolla/builders/build_corolla_hf_command5_runtime_carrier.py'
    RUNTIME_BUILDER = ROOT / 'exploit/ephemeral_runtime/build_corolla_hf_command5_carrier.py'
    PROXY_SOURCE = ROOT / 'exploit/ephemeral_runtime/corolla_hf_command5_proxy.c'
    CANARY_SOURCE = ROOT / 'exploit/ephemeral_runtime/corolla_hf_canary.c'
    PROXY_AUDIT = ROOT / 'exploit/ephemeral_runtime/audited_corolla_hf_command5_proxy_build.json'
    CANARY_AUDIT = ROOT / 'exploit/ephemeral_runtime/audited_corolla_hf_canary_build.json'
    PROXY_BIN = ROOT / 'exploit/ephemeral_runtime/audited/corolla_hf_command5_proxy.bin'
    CANARY_BIN = ROOT / 'exploit/ephemeral_runtime/audited/corolla_hf_runtime_canary.bin'
    H = ROOT / 'community/albinoelephant/normalized/8965H1202000_CodeFlash.bin'
    F = ROOT / 'community/spanconstant/raw-20260821/span-corolla-2025.20260821-1511/dump_codeflash_00000000_00200000_20260821-152033.bin'
    RAMREQ = ROOT / 'data/variant_ram_exec_requirements.json'

    def sha(data: bytes) -> str:
        return hashlib.sha256(data).hexdigest()
    a = json.loads(ART.read_text())
    ev = json.loads(EVID.read_text())
    h = H.read_bytes()
    fraw = F.read_bytes()
    proxy_audit = json.loads(PROXY_AUDIT.read_text())
    canary_audit = json.loads(CANARY_AUDIT.read_text())
    print('== promoted static evidence ==')
    check('carrier plan applies to exact H/F images', a['applies_to'] == ['8965H1202000', '8965F1208000'])
    check('exact H normalized image pinned', ev['sources']['h_normalized_codeflash']['sha256'] == sha(h) == '0b47bdc1217835c839e3543e52eab40eb793650a9c159e46f6a9b365ea41a67f')
    check('exact F source range dump pinned', ev['sources']['f_source_range_dump']['sha256'] == sha(fraw) == 'b8fa3d951f59fb75c190ce1b2c73164adb952f871650cfcd3b7656f08a9c448d')
    check('F normalized first MiB identity distinct/pinned', ev['sources']['f_normalized_first_mib']['sha256'] == sha(fraw[:1048576]) == 'fdb35b76891cf84a8b89e0a05c9c7c5cfcd27994cf85ccc01ff32828f53091f6')
    check('listed H/F prerequisites byte-identical', ev['h_f_exact_transfer']['all_ranges_byte_equal'] and all((r['byte_equal'] for r in ev['h_f_exact_transfer']['ranges'])))
    print('\n== carrier pocket / MPU ==')
    g = a['carrier_geometry']
    check('candidate is exact 464-byte lower-page pocket', g['base'] == '0xFEBF0000' and g['end_inclusive'] == '0xFEBF01CF' and (g['end_exclusive'] == '0xFEBF01D0') and (g['size'] == 464))
    check('first normalized direct reference starts exactly after pocket', g['first_recovered_normalized_reference'] == '0xFEBF01D0' and g['normalized_direct_reference_count_inside'] == 0)
    check('candidate resides in exact H MPU region5', g['mpu_region_index'] == 5 and g['mpu_bounds'] == ['0xFEBEF400', '0xFEBF33FC'])
    check('candidate MPAT is B8 in both contexts', g['mpat_contexts'] == ['0x000000B8', '0x000000B8'] and 'read-write-execute' in g['permissions'])
    print('\n== mailbox ==')
    m = a['mailbox_geometry']
    check('mailbox geometry exact', m['base'] == '0xFEBFFB80' and m['end_exclusive'] == '0xFEBFFBBC' and (m['size'] == 60))
    check('mailbox has zero recovered normalized direct refs', m['normalized_direct_reference_count_inside'] == 0)
    check('mailbox stays in H XCP shadow and above startup copy', m['xcp_shadow_window'] == ['0xFEBF7C00', '0xFEBFFBFF'] and m['startup_shadow_copy_end_inclusive'] == '0xFEBFF9EF')
    check('proxy self-initializes request byte before interrupts', all((x in m['request_state_initialization'] for x in ('proxy initializes', 'request_state', '0', 'before enabling interrupts', 'sampled once per foreground tick'))))
    check('proxy mirrors driver status into host-readable mailbox', m['result_status_offset'] == 1 and all((x in m['result_status_protocol'] for x in ('FEBF1280/FEBF1281', 'mailbox byte +1', 'request_state=0', 'immediate non-busy'))))
    print('\n== audited executable candidates ==')
    canary = a['runtime_candidates']['inert_canary']
    proxy = a['runtime_candidates']['fixed_b6_command5_proxy']
    check('canary exact audited bytes', canary['size'] == CANARY_BIN.stat().st_size == 298 and canary['headroom'] == 166 and (canary['sha256'] == sha(CANARY_BIN.read_bytes()) == 'ec4a31160b877c9067361fe3296f151c5a5ca38835ee8f8f22aa9a6fe3fca2df'))
    check('proxy exact audited bytes', proxy['size'] == PROXY_BIN.stat().st_size == 424 and proxy['headroom'] == 40 and (proxy['sha256'] == sha(PROXY_BIN.read_bytes()) == '62e4880eaa1bb7dd79fb1f47f4ce44033d1201550a20812a6a103ace00dde183'))
    check('both executables entry0/no relocations', canary['entry_offset'] == proxy['entry_offset'] == 0 and canary['relocations'] == proxy['relocations'] == 0)
    check('proxy exact B6 command5 contract', proxy['input_length'] == 36 and proxy['driver_record'] == 0 and (proxy['key_selector'] == 4) and (proxy['dispatcher'] == '0x00082750') and (proxy['done_flag'] == '0xFEBF1280') and (proxy['status_flag'] == '0xFEBF1281'))
    check('proxy shared-driver busy retry semantics', 'busy result 2' in proxy['busy_behavior'] and 'retries' in proxy['busy_behavior'] and ('no command-7 abort' in proxy['busy_behavior']))
    check('proxy source fixes input length at 36', '(void *)m->input' in PROXY_SOURCE.read_text() and '36u' in PROXY_SOURCE.read_text())
    check('proxy source leaves busy request pending', 'else if (rc != 2)' in PROXY_SOURCE.read_text())
    check('proxy source self-initializes mailbox after startup before interrupts', 'm->request_state = 0u;\n  __asm__ volatile("ei");' in PROXY_SOURCE.read_text())
    check('proxy caches host request state once per foreground tick', 'unsigned char request_state = m->request_state;' in PROXY_SOURCE.read_text() and 'else if (request_state == 1u)' in PROXY_SOURCE.read_text())
    check('proxy atomically samples adjacent done/status and mirrors both completion paths', 'volatile unsigned short *completion' in PROXY_SOURCE.read_text() and 'unsigned short completion_state = *completion;' in PROXY_SOURCE.read_text() and ('m->result_status = (unsigned char)(completion_state >> 8);' in PROXY_SOURCE.read_text()) and ('m->result_status = (unsigned char)rc;' in PROXY_SOURCE.read_text()))
    check('H completion callback raw body is pinned before halfword sampling', H.read_bytes()[536412:536412 + 14].hex() == '4437815a010a440f805a00527f00')
    check('canary source is inert wrt command5', 'TARGET_COMMAND5_DISPATCH' not in CANARY_SOURCE.read_text() and 'TARGET_CANARY_HEARTBEAT' in CANARY_SOURCE.read_text())
    print('\n== audit/toolchain trust ==')
    for label, audit, source in (('proxy', proxy_audit, PROXY_SOURCE), ('canary', canary_audit, CANARY_SOURCE)):
        check(f'{label} audit source hash', audit['source']['sha256'] == sha(source.read_bytes()))
        check(f'{label} static-only review grade', audit['review_status'] == 'static-carrier-candidate-not-live-validated')
    check('artifact binds one pinned compiler image', a['toolchain_reproducibility']['proxy_and_canary_use_same_pinned_image'] and a['toolchain_reproducibility']['backend'] == 'tools/rh850')
    print('\n== dynamic boundary ==')
    b = a['boundary']
    check('static carrier candidate is closed', b['static_target_native_carrier_candidate_closed'] is True)
    check('verified RAM requirement intentionally not promoted', b['verified_variant_ram_exec_requirement_promoted'] is False)
    check('live retention/permission/latency remain open', not b['live_retention_closed'] and (not b['live_slot4_permission_closed']) and (not b['command5_latency_jitter_closed']))
    check('production signer and actuation remain disabled', not b['production_b6_signer_closed'] and (not b['vehicle_actuation_authorized']))
    variants = {row['id'] for row in json.loads(RAMREQ.read_text())['variants']}
    check('H/F absent from verified variant RAM geometry', 'corolla-8965h1202000' not in variants and 'corolla-8965f1208000' not in variants)
    stages = a['validation_sequence']
    check('canary is mandatory first live stage', [r['stage'] for r in stages] == [1, 2, 3, 4] and stages[0]['name'] == 'inert carrier canary' and ('before exposing command-5' in stages[0]['purpose']))
    check('slot4 permission precedes timing', stages[1]['name'] == 'known-input slot4 command5 permission' and stages[3]['name'] == 'latency and contention characterization')
    print('\n== deterministic artifact builder ==')
_section_corolla_hf_command5_runtime_carrier()
print()
print('== corolla hf direct command5 ==')

def _section_corolla_hf_direct_command5():
    import json
    import subprocess
    import sys
    import tempfile
    from pathlib import Path
    ROOT = REPO_ROOT
    TOOL = ROOT / 'exploit/ephemeral_runtime/corolla_hf_direct_command5.py'
    PROXY = ROOT / 'exploit/ephemeral_runtime/audited/corolla_hf_command5_proxy.bin'
    SOURCE = ROOT / 'exploit/ephemeral_runtime/corolla_hf_command5_proxy.c'
    import exploit.ephemeral_runtime.corolla_hf_direct_command5 as mod
    plan = mod.build_plan()
    check('audited proxy identity exact', PROXY.stat().st_size == 424 and plan['package']['shellcode_sha256'] == '62e4880eaa1bb7dd79fb1f47f4ce44033d1201550a20812a6a103ace00dde183')
    check('direct proxy package identity exact', plan['package']['payload_sha256'] == 'a81b367febb819f4016a0880c707b82fb7f46f1bad5ec59119e43aec0140bfc5' and plan['package']['payload_size'] == 4096)
    check('package validates CRC and CMAC', plan['package']['crc_residue'] == '0xFFFFFFFF' and plan['package']['cmac_valid'] is True)
    check('field-proven zero-DID old-stack path retained', plan['field_proven_bootstrap']['did_0203'] == '0000000000' and plan['field_proven_bootstrap']['did_0201'] == '00' * 16 and (plan['field_proven_bootstrap']['did_0202'] == '00' * 16) and (plan['field_proven_bootstrap']['post_10f0_ram_substitution_required'] is False))
    probe = plan['probe']
    check('fixed selector4 B6-sized contract', probe['command5']['driver_record'] == 0 and probe['command5']['key_selector'] == 4 and (probe['command5']['input_length'] == 36) and (probe['command5']['expected_output_length'] == 16))
    check('mailbox contract exact', probe['mailbox'] == {'address': '0xFEBFFB80', 'size': 60, 'request_state_offset': 0, 'result_status_offset': 1, 'output_length_offset': 4, 'input_offset': 8, 'output_offset': 44})
    check('host uses sentinels and commits request state last', probe['host_commit_order'][-1] == 'write request_state=1 last' and '0xFE' in probe['host_commit_order'][2] and ('a5' in probe['host_commit_order'][1]))
    check('live stage requires canary plus reset confirmation', plan['live_guards']['successful_canary_result_required'] and plan['live_guards']['reset_to_stock_confirmation_required'] and plan['live_guards']['execute_and_bench_isolated_required'])
    check('no flash/steering transmission is part of probe', plan['live_guards']['flash_write_used'] is False and plan['live_guards']['steering_can_transmit_used'] is False)
    check('proxy source self-initializes before interrupts', 'm->request_state = 0u;\n  __asm__ volatile("ei");' in SOURCE.read_text())
    check('proxy mirrors completion status into mailbox', 'm->result_status = (unsigned char)(completion_state >> 8);' in SOURCE.read_text() and 'm->result_status = (unsigned char)rc;' in SOURCE.read_text())
    check('proxy samples adjacent completion bytes as halfword', 'volatile unsigned short *completion' in SOURCE.read_text() and '*completion = 0xff00u;' in SOURCE.read_text())
    with tempfile.TemporaryDirectory() as td:
        good = Path(td) / 'good.json'
        good.write_text(json.dumps({'schema': 'corolla-hf-direct-canary-v1', 'mode': 'live', 'created_at': 'test', 'live': {'attestation': {'attested': True, 'heartbeat_advanced': True, 'application_f181_hex': mod.ALBINO_APP_F181.hex(), 'heartbeat_first_hex': '43485045', 'heartbeat_second_hex': '44485045'}, 'panda_safety_tx_blocked_delta': 0, 'package': {'payload_sha256': 'b6d4b261ef6fb614ef0c9f8cd72bc7e7fb7608a793f9094ec76fe226bd884367'}, 'reset_to_stock_checked': False}}))
        gate = mod.validate_canary_result(good)
        check('successful exact canary result is accepted', gate['application_f181_hex'] == mod.ALBINO_APP_F181.hex() and gate['panda_safety_tx_blocked_delta'] == 0)
        bad = Path(td) / 'bad.json'
        bad.write_text(json.dumps({'schema': 'corolla-hf-direct-canary-v1', 'mode': 'live', 'live': {'attestation': {'attested': False}}}))
        try:
            mod.validate_canary_result(bad)
            bad_rejected = False
        except mod.DirectCommand5Error:
            bad_rejected = True
        check('failed canary result is rejected', bad_rejected)
    originals = (mod._exchange, mod.parse_positive_response, mod._read_xcp, mod._write_xcp, mod.time.sleep)
    try:
        mem = bytearray(60)
        phases = {'poll': 0}
        writes = []
        output = bytes.fromhex('00112233445566778899aabbccddeeff')

        def fake_exchange(*args, **kwargs):
            return b'\xff'

        def fake_positive(*args, **kwargs):
            return None

        def fake_write(_panda, *, bus, timeout, address, data):
            off = address - mod.MAILBOX
            mem[off:off + len(data)] = data
            writes.append((address, bytes(data)))
            return 1

        def fake_read(_panda, *, bus, timeout, address, length):
            off = address - mod.MAILBOX
            if address == mod.MAILBOX and length == 2 and (mem[0] == 1):
                phases['poll'] += 1
                if phases['poll'] == 1:
                    return bytes((2, mod.RESULT_SENTINEL))
                mem[0] = 0
                mem[1] = 0
                mem[4:8] = 16 .to_bytes(4, 'little')
                mem[44:60] = output
            return bytes(mem[off:off + length])
        mod._exchange, mod.parse_positive_response = (fake_exchange, fake_positive)
        mod._write_xcp, mod._read_xcp, mod.time.sleep = (fake_write, fake_read, lambda _x: None)
        observed, meta = mod._execute_probe(object(), bus=1, timeout=0.1, completion_timeout=1, message=mod.DEFAULT_VECTOR)
        check('host state machine accepts queued then status-zero completion', observed == output and meta['result_status'] == 0 and meta['queued_state_observed'] and (meta['state_transitions_observed'] == [2, 0]))
        check('request_state commit is final host write', writes[-1] == (mod.MAILBOX, b'\x01'))
        check('output sentinel is replaced before success', observed != mod.OUTPUT_SENTINEL)
    finally:
        mod._exchange, mod.parse_positive_response, mod._read_xcp, mod._write_xcp, mod.time.sleep = originals
    proc = subprocess.run([sys.executable, str(TOOL)], cwd=ROOT, capture_output=True, text=True)
    check('plan-only CLI succeeds without hardware', proc.returncode == 0)
    if proc.returncode == 0:
        cli = json.loads(proc.stdout)
        check('plan-only CLI cannot claim live result', cli['mode'] == 'plan' and cli['live'] is None)
    proc = subprocess.run([sys.executable, str(TOOL), '--execute', '--bench-isolated', '--reset-to-stock-confirmed'], cwd=ROOT, capture_output=True, text=True)
    check('live CLI refuses missing canary result before hardware', proc.returncode != 0 and '--canary-result' in proc.stderr)
_section_corolla_hf_direct_command5()
print()
print('== corolla hf command5 portability ==')

def _section_corolla_hf_command5_portability():
    import hashlib, json
    REPO = REPO_ROOT
    ART = REPO / 'data/generated/corolla_hf_command5_portability.json'
    BUILDER = REPO / 'tools/targets/corolla/builders/build_corolla_hf_command5_portability.py'
    H = REPO / 'community/albinoelephant/normalized/8965H1202000_CodeFlash.bin'

    def sha(b):
        return hashlib.sha256(b).hexdigest()
    art = json.loads(ART.read_text())
    h = H.read_bytes()
    check('applies to H/F only', art['applies_to'] == ['8965H1202000', '8965F1208000'])
    core = art['command5_core']
    fields = core['record_fields']
    check('record0 raw bytes exact', core['driver_record_address'] == '0x00027C88' and core['driver_record_raw_hex'] == h[162952:162984].hex())
    check('record0 completion callback exact', fields['completion_callback'] == '0x00082F5C')
    check('record0 adapter exact', fields['adapter_callback'] == '0x000820CC')
    check('record0 worker exact', fields['worker_callback'] == '0x000821D0')
    check('record0 config pointer exact', fields['config_pointer'] == '0x00027C84' and core['config_type_word'] == 1)
    check('serialized command5 dispatcher exact', core['serialized_dispatcher'] == '0x00082750' and core['record_lookup'] == '0x00082702')
    check('variable length command5 input supports B6 36 bytes', core['variable_length_prepare'] == '0x00081E94' and core['maximum_input_bytes'] == 80 and (core['b6_authenticated_input_bytes'] == 36) and core['b6_authenticated_input_fits'])
    check('lower ICU-S command5 engine exact', core['lower_icus_engine'] == '0x00083A30' and core['command_word_formula'] == '(key_selector << 16) | 5')
    check('record0 completion state exact', core['synchronous_wrapper'] == '0x00082ED2' and core['done_flag'] == '0xFEBF1280' and (core['status_flag'] == '0xFEBF1281'))
    check('H/F application command5 path byte-identical', core['h_f_application_byte_identical'] is True)
    rb = art['resident_runtime_boundary']
    check('Sienna resident geometry explicitly does not transfer', rb['sienna_single_stage_geometry_transfers'] is False and rb['h_f_verified_ram_exec_requirement_entry_present'] is False)
    check('H startup clear ranges exact', rb['h_startup_clear_ranges_inclusive'] == [['0xFEBF05CC', '0xFEBF09CB'], ['0xFEBF0B4C', '0xFEBF0F4B']])
    check('naive FEBF0000 Sienna proxy rejected', 'does not authorize the Sienna 546-byte proxy' in rb['interpretation'] and 'TMS-054' in rb['interpretation'])
    two = art['two_stage_candidate']
    check('TMS053 two-stage shadow idea retained as historical bounded hypothesis', two['status'].startswith('historical-tms053') and two['xcp_write_shadow_bounds'] == ['0xFEBF7C00', '0xFEBFFBFF'] and ('TMS-054' in two['interpretation']) and ('Neither artifact proves' in two['interpretation']))
    con = art['static_conclusion']
    check('software machinery transfer closed', con['h_f_command5_software_machinery_transfers'] and con['b6_36_byte_input_supported'])
    check('resident signer and live policy remain open', not con['h_f_resident_signer_runtime_closed'] and (not con['slot4_live_permission_closed']) and (not con['signing_latency_closed']))
    check('evidence boundary rejects working-oracle overclaim', 'working H/F' in art['evidence_boundary'] and 'still requires live carrier retention' in art['evidence_boundary'])
_section_corolla_hf_command5_portability()
print()
print(f'\n== RESULT: {passed} passed, {failed} failed ==')
raise SystemExit(1 if failed else 0)
