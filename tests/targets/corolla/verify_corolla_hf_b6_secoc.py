#!/usr/bin/env python3
"""Portable Corolla H/F protected-command pins: direct canary, competing-sender arbitration, and 00F freshness bridge.

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
print()
print('== corolla hf direct canary ==')

def _section_corolla_hf_direct_canary():
    import hashlib
    import json
    ROOT = REPO_ROOT
    from exploit.common.ram_exec import explicit_route
    from exploit.ephemeral_runtime.corolla_hf_direct_canary import ALBINO_APP_F181, BOOT_F181, CANARY_SHA256, DIRECT_PAYLOAD_SHA256, DID_201, DID_202, DID_203, FF00_REQUEST, HEARTBEAT_ADDR, HEARTBEAT_MAGIC, REQUEST_DOWNLOAD, VERIFY_10F0, _attest_once, _upload_and_trigger, build_payload, build_plan

    class FakeUds:

        class SESSION_TYPE:
            DEFAULT = 1
            EXTENDED_DIAGNOSTIC = 3
            PROGRAMMING = 2

        class ACCESS_TYPE:
            REQUEST_SEED = 1
            SEND_KEY = 2

        class SERVICE_TYPE:
            REQUEST_DOWNLOAD = 52
            READ_MEMORY_BY_ADDRESS = 35

        class ROUTINE_CONTROL_TYPE:
            START = 1

        class DATA_IDENTIFIER_TYPE:
            APPLICATION_SOFTWARE_IDENTIFICATION = 61825

    class FakeClient:

        def __init__(self, f181: bytes=BOOT_F181) -> None:
            self.events: list[tuple] = []
            self.f181 = f181

        def diagnostic_session_control(self, session):
            self.events.append(('session', session))
            return b''

        def read_data_by_identifier(self, did):
            self.events.append(('rdbi', did))
            return self.f181

        def security_access(self, access, data_record=None, security_key=None):
            data = data_record if data_record is not None else security_key
            self.events.append(('security', access, bytes(data or b'')))
            if access == FakeUds.ACCESS_TYPE.REQUEST_SEED:
                return bytes.fromhex('ef309a63a0572b7a147b7062aa1073a3')
            return b''

        def write_data_by_identifier(self, did, data):
            self.events.append(('wdbi', did, bytes(data)))
            return b''

        def _uds_request(self, service, data):
            self.events.append(('request', service, bytes(data)))
            return b' \x04\x02' if service == FakeUds.SERVICE_TYPE.REQUEST_DOWNLOAD else b''

        def transfer_data(self, block, data):
            self.events.append(('transfer', block, bytes(data)))
            return b''

        def request_transfer_exit(self):
            self.events.append(('exit',))
            return b''

        def routine_control(self, control, rid, data=b''):
            self.events.append(('routine', control, rid, bytes(data)))
            return b''
    print('== deterministic direct package ==')
    payload, meta = build_payload()
    plan = build_plan()
    canary_source = ROOT / 'exploit/ephemeral_runtime/corolla_hf_canary.c'
    canary_audit = json.loads((ROOT / 'exploit/ephemeral_runtime/audited_corolla_hf_canary_build.json').read_text())
    canary_source_bytes = canary_source.read_bytes()
    check('heartbeat semantics are source/audit bound', canary_audit['source']['path'] == 'exploit/ephemeral_runtime/corolla_hf_canary.c' and canary_audit['source']['sha256'] == hashlib.sha256(canary_source_bytes).hexdigest() and (canary_audit['runtime_contract']['canary_heartbeat'] == f'0x{HEARTBEAT_ADDR:08X}') and (b'0x45504843u' in canary_source_bytes))
    check('audited canary identity', meta['shellcode_size'] == 298 and meta['shellcode_sha256'] == CANARY_SHA256)
    check('direct package identity', len(payload) == 4096 and meta['payload_sha256'] == DIRECT_PAYLOAD_SHA256)
    check('package callback and descriptor are FEBF0000', meta['callback_address'] == '0xFEBF0000' and meta['crc_descriptor_address'] == '0xFEBF0000')
    check('package authenticates and has terminal CRC residue', meta['cmac_valid'] is True and meta['crc_residue'] == '0xFFFFFFFF')
    check('plan reproduces telescope zero DID setup', plan['field_proven_bootstrap']['did_0203'] == DID_203.hex() and plan['field_proven_bootstrap']['did_0201'] == DID_201.hex() and (plan['field_proven_bootstrap']['did_0202'] == DID_202.hex()))
    check('plan reproduces exact RequestDownload', plan['field_proven_bootstrap']['request_download'] == REQUEST_DOWNLOAD.hex() == '01460100febf000000001000')
    check('plan reproduces exact 10F0 option', plan['field_proven_bootstrap']['verify_option'] == VERIFY_10F0.hex() == '4500febf000000001000')
    check('plan reproduces exact old-stack FF00 request', plan['field_proven_bootstrap']['ff00_request'] == FF00_REQUEST.hex() == '3101ff004500000e000000008000')
    check('direct package eliminates post-auth substitution', plan['field_proven_bootstrap']['post_10f0_ram_substitution_required'] is False)
    check('command5 remains gated off', plan['success_gate']['command5_proxy_authorized_by_this_plan'] is False)
    check('exact application identity is pinned', plan['target']['required_application_f181_hex'] == ALBINO_APP_F181.hex())
    check('exact boot placeholder identity is pinned', plan['target']['required_boot_f181_hex'] == BOOT_F181.hex())
    print('\n== mocked field-proven upload choreography ==')
    client = FakeClient()
    route = explicit_route(bus=0, elm327_param=0, uds_variant='old', cpu_index=0)
    sent: list[tuple] = []
    sleeps: list[float] = []
    stats = _upload_and_trigger(object(), client, FakeUds, route, payload=payload, security_secret=bytes.fromhex('f05f36b7d78c03e24ab4faef2a57d044'), isotp_send_fn=lambda panda, data, addr, *, bus: sent.append((bytes(data), addr, bus)), sleep_fn=lambda seconds: sleeps.append(seconds))
    e = client.events
    check('one old-stack identity ladder is explicit', e[:3] == [('session', 1), ('session', 3), ('session', 2)], repr(e[:3]))
    check('session settle timing mirrors telescope', sleeps == [0.5, 0.7, 1.0], repr(sleeps))
    check('boot F181 is verified before SA', e[3] == ('rdbi', 61825))
    check('SecurityAccess requests zero data record', e[4] == ('security', 1, bytes(16)))
    check('SecurityAccess sends a 16-byte response', e[5][0:2] == ('security', 2) and len(e[5][2]) == 16)
    check('DID writes exactly reproduce telescope 0203/0201/0202', e[6:9] == [('wdbi', 515, bytes(5)), ('wdbi', 513, bytes(16)), ('wdbi', 514, bytes(16))])
    check('RequestDownload record is exact', e[9] == ('request', 52, REQUEST_DOWNLOAD))
    check('payload transfers in four exact 0x400 blocks', [row[1] for row in e[10:14]] == [1, 2, 3, 4] and all((row[0] == 'transfer' and len(row[2]) == 1024 for row in e[10:14])))
    check('TransferExit precedes 10F0', e[14] == ('exit',) and e[15] == ('routine', 1, 4336, VERIFY_10F0))
    check('FF00 sent only after successful 10F0 call', sent == [(FF00_REQUEST, 1953, 0)])
    check('install stats retain boot identity and successful gates', stats['boot_f181_hex'] == BOOT_F181.hex() and stats['rid_10f0_accepted'] and stats['ff00_sent'])
    empty_download = FakeClient()
    empty_download._uds_request = lambda service, data: empty_download.events.append(('request', service, bytes(data))) or b''
    try:
        _upload_and_trigger(object(), empty_download, FakeUds, route, payload=payload, security_secret=bytes.fromhex('f05f36b7d78c03e24ab4faef2a57d044'), isotp_send_fn=lambda *args, **kwargs: None, sleep_fn=lambda _: None)
    except Exception as exc:
        empty_download_rejected = 'RequestDownload returned an empty' in str(exc)
    else:
        empty_download_rejected = False
    check('empty RequestDownload positive payload fails closed before transfer', empty_download_rejected and (not any((row[0] == 'transfer' for row in empty_download.events))))
    try:
        _upload_and_trigger(object(), FakeClient(), FakeUds, explicit_route(bus=0, elm327_param=0, uds_variant='new', cpu_index=0), payload=payload, security_secret=bytes(16), isotp_send_fn=lambda *args, **kwargs: None, sleep_fn=lambda _: None)
    except Exception as exc:
        new_stack_rejected = 'old-stack' in str(exc)
    else:
        new_stack_rejected = False
    check('unobserved new-stack variant fails closed', new_stack_rejected)
    bad = FakeClient(f181=b'bad')
    try:
        _upload_and_trigger(object(), bad, FakeUds, route, payload=payload, security_secret=bytes(16), isotp_send_fn=lambda *args, **kwargs: None, sleep_fn=lambda _: None)
    except Exception as exc:
        boot_identity_rejected = 'boot F181 mismatch' in str(exc)
    else:
        boot_identity_rejected = False
    check('wrong boot identity fails before SecurityAccess/upload', boot_identity_rejected and (not any((row[0] == 'security' for row in bad.events))))
    print('\n== application-context canary attestation ==')
    app = FakeClient(f181=ALBINO_APP_F181)
    reads = iter((bytes.fromhex('50485045'), bytes.fromhex('51485045')))
    attest = _attest_once(app, FakeUds, heartbeat_interval=0.05, read_memory_fn=lambda client, uds, mem, addr, size: next(reads), sleep_fn=lambda _: None)
    check('post-FF00 application F181 must reappear', attest['application_f181_hex'] == ALBINO_APP_F181.hex())
    check('attestation enters extended session', ('session', 3) in app.events)
    check('attestation reads target-native heartbeat address', attest['heartbeat_address'] == f'0x{HEARTBEAT_ADDR:08X}')
    check('heartbeat signature and progression are required', attest['heartbeat_magic_le'] == HEARTBEAT_MAGIC and attest['heartbeat_start_delta'] == 13 and (attest['heartbeat_step'] == 1) and (attest['heartbeat_advanced'] is True))
    try:
        _attest_once(FakeClient(f181=ALBINO_APP_F181), FakeUds, heartbeat_interval=0.05, read_memory_fn=lambda client, uds, mem, addr, size: bytes.fromhex('50485045'), sleep_fn=lambda _: None)
    except Exception as exc:
        static_rejected = 'progression is implausible' in str(exc)
    else:
        static_rejected = False
    check('static heartbeat cannot pass', static_rejected)
    foreign_reads = iter((bytes.fromhex('01020304'), bytes.fromhex('02020304')))
    try:
        _attest_once(FakeClient(f181=ALBINO_APP_F181), FakeUds, heartbeat_interval=0.05, read_memory_fn=lambda client, uds, mem, addr, size: next(foreign_reads), sleep_fn=lambda _: None)
    except Exception as exc:
        foreign_rejected = 'canary signature' in str(exc)
    else:
        foreign_rejected = False
    check('unrelated changing RAM cannot masquerade as canary heartbeat', foreign_rejected)
    try:
        _attest_once(FakeClient(f181=b'wrong'), FakeUds, heartbeat_interval=0.05, read_memory_fn=lambda *args: bytes(4), sleep_fn=lambda _: None)
    except Exception as exc:
        wrong_app_rejected = 'application F181 mismatch' in str(exc)
    else:
        wrong_app_rejected = False
    check('wrong application identity cannot pass', wrong_app_rejected)
    source = (ROOT / 'exploit/ephemeral_runtime/corolla_hf_direct_canary.py').read_text(encoding='utf-8')
    check('live mode is double-gated', '--execute requires --bench-isolated' in source)
    check('tool cannot expose command5 proxy', 'corolla_hf_command5_proxy.bin' not in source and 'command5_proxy_authorized_by_this_plan' in source)
    check('no flash write primitive is imported', all((token not in source for token in ('flash_erase', 'flash_program', 'erase_codeflash', 'write_codeflash', 'exploit.patcher'))))
_section_corolla_hf_direct_canary()
print()
print('== corolla hf b6 competing sender arbitration ==')

def _section_corolla_hf_b6_competing_sender_arbitration():
    import hashlib
    import json
    ROOT = REPO_ROOT
    ART = ROOT / 'data/generated/corolla_hf_b6_competing_sender_arbitration.json'
    EVID = ROOT / 'data/generated/corolla_8965H1202000_b6_competing_sender_decompiler_evidence.json'
    BUILDER = ROOT / 'tools/targets/corolla/builders/build_corolla_hf_b6_competing_sender_arbitration.py'
    H = ROOT / 'community/albinoelephant/normalized/8965H1202000_CodeFlash.bin'

    def sha(data: bytes) -> str:
        return hashlib.sha256(data).hexdigest()
    a = json.loads(ART.read_text())
    ev = json.loads(EVID.read_text())
    h = H.read_bytes()
    check('exact H/F scope', a['applies_to'] == ['8965H1202000', '8965F1208000'] and a['cross_variant']['h_f_application_byte_identical'])
    check('non-enabling boundary', not a['suppression_conclusion']['parallel_injection_safe'] and (not a['suppression_conclusion']['freshness_preemption_is_safe_coexistence']))
    print('\n== promoted target-native evidence ==')
    check('H image hash pinned', ev['image']['sha256'] == sha(h))
    body_ok = True
    for row in ev['functions']:
        entry = int(row['entry'], 16)
        size = row['body_size']
        body_ok &= sha(h[entry:entry + size]) == row['body_sha256']
    check('all promoted raw H bodies pinned', body_ok)
    roles = {r['role'] for r in ev['functions']}
    check('queue/delivery/sequence/request roles all promoted', {'secoc_secured_pdu_ingress', 'secoc_queue_first_insert', 'secoc_queue_existing_slot_update', 'secoc_pending_or_retry_to_verify', 'com_rx_indication_single_shadow_copy', 'b6_application_sequence_delta', 'b6_sequence_scaled_target_plausibility', 'b6_target_lateral_id_decoder'}.issubset(roles))
    print('\n== receiver/source identity ==')
    r = a['receiver_identity']
    check('one B6 identity', r['can_id'] == '0x0B6' and r['application_pdu_id'] == 42 and (r['authenticated_data_id'] == '0x00B6'))
    check('one ordinary freshness identity', r['freshness_id'] == 2 and r['normal_freshness_slot'] == 1)
    check('slot4 shared crypto selection', r['crypto_slot'] == 4)
    check('no source ID in recovered authenticated input', not r['separate_source_identifier_in_authenticated_input'])
    check('no source-specific acceptance recovered', not r['source_specific_acceptance_recovered'])
    print('\n== one-slot SecOC queue arbitration ==')
    q = a['single_profile_queue']
    check('single B6 queue multiplicity', q['queue_multiplicity'] == 1 and q['not_a_source_priority_queue'])
    check('idle first arrival inserts', 'E1->D2' in q['idle_E1'] and '0x87CD6' in q['idle_E1'])
    check('pending stage is last-arrival-wins', 'last B6 arrival' in q['pending_arbitration'])
    check('inflight C3/B4 arrivals not admitted', 'ignored' in q['inflight_arbitration'] and 'C3' in q['verify_C3_or_retry_B4'] and ('B4' in q['verify_C3_or_retry_B4']))
    print('\n== freshness arbitration ==')
    fresh = a['freshness_arbitration']
    check('single shared committed B6 freshness', fresh['committed_state_is_shared_per_b6_profile'])
    check('freshness commits before normal verified COM delivery', fresh['commit_before_normal_verified_application_delivery'])
    check('same low2 after committed10 reconstructs 14', fresh['same_low2_reference_examples']['committed10_received_low2_2'] == 14)
    check('next low2 after committed10 reconstructs 11', fresh['same_low2_reference_examples']['committed10_received_low2_3'] == 11)
    check('same-full-freshness replay cannot reuse committed freshness', 'next congruent' in fresh['same_full_freshness_replay_after_commit'] and 'fails verification' in fresh['same_full_freshness_replay_after_commit'])
    check('same-freshness verification failure has bounded delivery exception', 'failure forwarding grace/global-override' in fresh['same_full_freshness_replay_after_commit'] and 'without committing freshness' in fresh['same_full_freshness_replay_after_commit'])
    ffd = fresh['verification_failure_forwarding_exception']
    check('failure-forward grace geometry joined', ffd['grace_limit'] == 204 and ffd['b6_profile_plus_0x09'] == 0)
    check('future valid freshness has no source lock', 'no source lock' in fresh['future_freshness_from_another_capable_sender'])
    check('capable senders race shared freshness', 'race one shared freshness' in fresh['consequence'])
    print('\n== application sequence is not sender arbitration ==')
    s = a['application_sequence_arbitration']
    check('signal261 modulo64/gap8', s['signal_id'] == 261 and s['modulus'] == 64 and ('min(delta,8)' in s['effective_gap']))
    check('strict +1 not required by EPS', not s['strict_plus_one_required_by_eps'])
    check('duplicate app sequence not rejected', not s['duplicate_sequence_rejected'] and s['examples']['same_application_sequence'] == {'raw_delta': 0, 'effective_gap': 1})
    check('strict +1 and gap4 examples', s['examples']['strict_plus_one'] == {'raw_delta': 1, 'effective_gap': 1} and s['examples']['gap_four'] == {'raw_delta': 4, 'effective_gap': 4})
    check('large app gap capped8', s['examples']['large_gap_capped'] == {'raw_delta': 19, 'effective_gap': 8})
    check('sequence feeds target plausibility', '0xCB4F4' in s['plausibility_use'] and '78 raw' in s['plausibility_use'])
    print('\n== request ID and application shadow ==')
    req = a['request_id_arbitration']
    check('accepted request dictionary exact', req['accepted_active_ids'] == {'1': 'PCS', '4': 'LDA', '10': 'Hands Off LTA', '11': 'LTA/LCA', '19': 'PDA'})
    check('no request priority order recovered', req['priority_order_recovered'] is None and 'no competing-request history' in req['behavior'])
    check('later delivered request can replace profile', 'later successfully delivered B6' in req['conclusion'])
    d = a['application_delivery']
    check('single PDU42 shadow', d['shared_shadow_pdu'] == 42 and d['entry'] == '0x00076A3C')
    check('sequential accepted B6 overwrites current shadow', 'overwrites' in d['sequential_valid_frames'])
    check('last successful delivery is current command', 'last successfully delivered' in d['effective_policy'])
    print('\n== hypothesis resolution / suppression policy ==')
    hyp = a['hypothesis_resolution']
    check('newest application sequence winner disproved', hyp['newest_application_sequence_wins'].startswith('disproved'))
    check('source-specific arbitration not recovered', hyp['source_specific_acceptance'].startswith('not recovered'))
    check('frame winner is stage-dependent', hyp['first_or_last_frame_wins'].startswith('stage-dependent'))
    check('request priority disproved', hyp['request_id_priority'].startswith('disproved'))
    check('freshness is source-agnostic', 'not source-specific' in hyp['freshness_rejects_competing_sender'])
    policy = a['suppression_conclusion']
    check('EPS does not require named stock identity', not policy['eps_protocol_requires_named_stock_source'])
    check('deterministic lateral requires exclusive B6 authority', policy['deterministic_lateral_authority_requires_exclusive_b6_control'])
    check('production policy requires stock suppression or proved quiescence', 'Suppress/isolate' in policy['production_policy'] and 'quiescent' in policy['production_policy'])
    print('\n== builder reproducibility ==')
_section_corolla_hf_b6_competing_sender_arbitration()
print()
print('== corolla hf secoc 00f freshness bridge ==')

def _section_corolla_hf_secoc_00f_freshness_bridge():
    import hashlib
    import json
    REPO = REPO_ROOT
    ART = json.loads((REPO / 'data/generated/corolla_hf_secoc_00f_freshness_bridge.json').read_text())
    H = json.loads((REPO / 'data/generated/corolla_8965H1202000_b6_secoc_verification.json').read_text())
    DECOMP = json.loads((REPO / 'data/generated/corolla_8965H1202000_b6_secoc_verification_decompiler_evidence.json').read_text())
    COMP = json.loads((REPO / 'data/generated/corolla_h_sienna_secoc_structural_comparison.json').read_text())
    ALBINO = REPO / 'community/albinoelephant/can_oracle.ndjson'
    print('== exact H/F synchronization profile and wire layout ==')
    prof = COMP['profile_tables']['corolla_h_f']['records'][0]
    static = ART['static_h_f_receiver']
    wire = static['wire_layout']
    check('H/F application identity applies', static['applies_to']['corolla_h_f_application_identical'] is True)
    check('H/F sync profile is DataID 0x00F freshness ID0', prof['data_id'] == '0x00F' and prof['freshness_id'] == 0)
    check('H/F sync profile record address exact', prof['address'] == '0x0002572C')
    check('sync PDU is exactly eight bytes', prof['secured_pdu_length'] == prof['input_buffer_length'] == 8)
    check('sync freshness is full/transmitted FV36', prof['full_freshness_bits'] == prof['transmitted_freshness_bits'] == 36)
    check('sync CMAC is 128 -> MSB28', prof['full_cmac_bits'] == 128 and prof['transmitted_cmac_bits'] == 28)
    check('sync has no auth or CryptoIf-busy retry', prof['authentication_retry_limit'] == prof['cryptoif_busy_retry_limit'] == 0)
    check('artifact profile is independently pinned to raw profile', static['profile_record']['record_sha256'] == prof['record_sha256'])
    check('sync has no application payload', wire['application_payload_bytes'] == 0)
    check('sync trip occupies B0:B1', wire['B0_B1'] == 'trip16, big-endian')
    check('sync reset occupies B2:B4 high nibble', wire['B2_B3_B4_7_4'] == 'reset20, big-endian')
    check('sync MAC28 occupies B4 low nibble through B7', wire['B4_3_0_B5_B6_B7'] == 'CMAC_MSB28')
    check('sync FV36 is trip16||reset20', wire['freshness36'] == 'trip16 || reset20')
    check('sync CMAC input is seven bytes', wire['authenticated_input'] == '00 0F || trip16 || reset20 || 0000b' and wire['authenticated_input_bytes'] == 7)
    print('\n== target-native H receiver functions ==')
    funcs = {f['entry']: f for f in DECOMP['functions']}
    bind = static['decompiler_bindings']
    for role, entry in {'authenticated_input_build': '0x00087FC2', 'sync_pack': '0x000899B4', 'sync_parse': '0x00089B46', 'sync_reconstruct': '0x00089F6E', 'sync_commit': '0x0008A130', 'normal_reset_search': '0x00089CDA', 'normal_window': '0x00089D58'}.items():
        check(f'{role} entry/hash bound to target-native decompiler', bind[role]['entry'] == entry and bind[role]['body_sha256'] == funcs[entry]['body_sha256'])
    check('sync parser decodes B0:B1 trip', 'CONCAT11(*param_1,param_1[1])' in funcs['0x00089B46']['decompiled_c'])
    check('sync parser decodes B2:B4 reset', 'param_1[4] >> 4' in funcs['0x00089B46']['decompiled_c'])
    check('sync packer writes five freshness bytes', 'param_2[4] = (char)(param_1[1] << 4)' in funcs['0x000899B4']['decompiled_c'])
    check('global 00F state addresses remain exact', static['ram_state']['current_state'] == ['0xFEBE54AC', '0xFEBE54B0'])
    check('sync commit is authentication-gated', static['ram_state']['commit_only_after_authentication_success'] is True)
    check('trip wrap threshold remains 15', static['sync_acceptance']['trip_wrap_threshold'] == 15)
    check('authenticated trip wrap clears B6/D7 state', static['sync_acceptance']['trip_wrap_clears_b6_and_d7'] is True)
    print('\n== ordinary D7/B6 freshness relationship ==')
    ordf = static['ordinary_freshness']
    check('D7 and B6 have distinct ordinary freshness IDs', ordf['d7_freshness_id'] == 1 and ordf['b6_freshness_id'] == 2)
    check('ordinary D7/B6 slots are independent', ordf['independent_ordinary_slots'] is True)
    check('FV4 split is message-low2 then reset-low2', ordf['wire_fv4']['decode'] == {'message_low2': 'B28[7:6]', 'reset_low2': 'B28[5:4]'})
    check('ordinary full freshness is exact', ordf['full_freshness'] == 'trip16 || reset20 || message8 || reset_low2 || 00b')
    check('reset search exact order', ordf['reset_candidate_search']['ordered_trials'] == ['current', 'current-1', 'current+1', 'current-2', 'current+2'])
    check('same-epoch window is strict-forward +1..+4', ordf['same_epoch_message_rule']['strictly_forward'] is True and ordf['same_epoch_message_rule']['ordinary_forward_delta'] == [1, 4])
    check('new epoch seeds message from received low2', ordf['new_epoch_message_rule'] == 'received_message_low2 (0..3)')
    print('\n== Albino same-investigation sync oracle ==')
    alb = ART['captures']['albino_2023_tskm_sync_oracle']
    check('Albino raw oracle SHA pinned', hashlib.sha256(ALBINO.read_bytes()).hexdigest() == alb['source']['sha256'] == '8863398a98875a853e722a6ba83fc10563d5764cea33719c8af34225efa189a3')
    check('Albino oracle has 1232 sync rows split 616/616', alb['rows'] == 1232 and alb['rows_per_bus'] == {'0': 616, '2': 616})
    check('Albino bus0/bus2 sync payload sequences identical', alb['bus0_bus2_payload_sequences_identical'] is True)
    check('Albino trip is exactly 0x0D0D', alb['trip_values_hex'] == ['0x0D0D'])
    check('Albino has 206 unique sync states', alb['unique_states'] == 206)
    check('Albino reset states mostly advance +1', alb['reset_transition_deltas'] == {'1': 204, '115': 1})
    check('Albino state copies are byte-identical', alb['all_repeated_state_payloads_byte_identical'] is True)
    check('Albino normal reset cadence median is ~300ms', 295000000 <= alb['state_transition_period_ns_median'] <= 305000000)
    check('Albino collection gap remains explicitly bounded', alb['initial_collection_gap']['observed_reset_delta'] == 115)
    print('\n== Span moving-rlog dynamic replay ==')
    span = ART['captures']['span_2025_discord']
    ss = span['sync_00f']
    sd = span['d7_receiver_model_replay']
    st = span['transition_ordering']
    check('Span has 600 00F and 3000 D7 frames', span['wire_counts']['0x00F'] == 600 and span['wire_counts']['0x0D7'] == 3000)
    check('Span trip is 0x162D and constant', ss['trip_values_hex'] == ['0x162D'])
    check('Span reset advances 1037->1237', ss['reset_first'] == 1037 and ss['reset_last'] == 1237)
    check('Span 00F wire cadence ~100ms', 99000000 <= ss['frame_period_ns_median'] <= 101000000)
    check('Span reset epoch cadence ~300ms', 299000000 <= ss['state_transition_period_ns_median'] <= 301000000)
    check('Span all 199 inter-transition intervals near 300ms', ss['state_transition_intervals_280_to_320ms'] == ss['state_transition_interval_count'] == 199)
    check('Span reset transition is +1 exactly 200 times', ss['reset_transition_deltas_same_trip'] == {'1': 200})
    check('Span duplicate sync states are byte/MAC identical', ss['all_repeated_state_payloads_byte_identical'] is True and ss['all_repeated_state_mac28_identical'] is True)
    check('Span has one unique MAC28 per sync state', ss['unique_mac28_count'] == ss['unique_states'] == 201)
    check('H reset search maps every post-sync Span D7', sd['unmapped_after_first_sync'] == 0 and span['wire_counts']['mapped_0x0D7_after_first_00F'] == 2997)
    check('Span live reset candidates are current/current-1 only', sd['candidate_delta_counts'] == {'-1': 200, '0': 2797})
    check('Span same-epoch reconstructed message8 always +1', sd['same_epoch_message8_delta_counts'] == {'1': 2796})
    check('Span has 199 complete 15-frame D7 epochs', sd['complete_15_frame_epochs'] == 199)
    check('every complete Span epoch is message8 1..15', sd['complete_epochs_exact_message8_1_through_15'] == 199)
    check('all non-initial Span epochs begin message-low2=1', sd['non_initial_epoch_first_message_low2'] == {'1': 200})
    check('all Span sync transitions record one same-timestamp old-reset D7 after the new 00F', st['d7_same_timestamp_after_sync_using_previous_reset_low2'] == st['sync_state_transitions'] == 200)
    check('no same-timestamp old-reset Span D7 precedes the new 00F in logged array order', st['d7_same_timestamp_before_sync_using_previous_reset_low2'] == 0)
    check('all after-sync old-reset D7 frames end at message-low2=3', st['those_after_sync_previous_reset_frames_with_message_low2_3'] == 200)
    check('new-reset D7 follows ~20ms later', 19000000 <= st['first_d7_new_reset_delay_ns_min'] <= st['first_d7_new_reset_delay_ns_median'] <= st['first_d7_new_reset_delay_ns_max'] <= 21000000)
    check('all first new-reset Span D7 frames start low2=1', st['first_d7_new_reset_message_low2'] == {'1': 200})
    check('cross-capture conclusion binds Span current-1 overlap to logged order', ART['cross_capture_conclusions']['span_logged_order_exercises_current_minus_1_overlap'] is True)
    print('\n== independent public-route replay ==')
    pub = ART['captures']['public_2023']
    ps = pub['sync_00f']
    pd = pub['d7_receiver_model_replay']
    check('public route has 588 00F and 2943 D7 frames', pub['wire_counts']['0x00F'] == 588 and pub['wire_counts']['0x0D7'] == 2943)
    check('public trip is 0x0CE9 and constant', ps['trip_values_hex'] == ['0x0CE9'])
    check('public reset states 224->428', ps['reset_first'] == 224 and ps['reset_last'] == 428)
    check('public sync cadence ~100ms', 99000000 <= ps['frame_period_ns_median'] <= 101000000)
    check('public reset cadence median ~300ms', 295000000 <= ps['state_transition_period_ns_median'] <= 305000000)
    check('public capture has 194/196 near-300ms transition intervals', ps['state_transition_intervals_280_to_320ms'] == 194 and ps['state_transition_interval_count'] == 196)
    check('H reset search maps every post-sync public D7', pd['unmapped_after_first_sync'] == 0 and pub['wire_counts']['mapped_0x0D7_after_first_00F'] == 2940)
    check('public live reset candidates are current/current-1 only', pd['candidate_delta_counts'] == {'-1': 196, '0': 2744})
    check('public same-epoch reconstructed message8 always +1', pd['same_epoch_message8_delta_counts'] == {'1': 2742})
    check('all 194 complete public epochs are message8 1..15', pd['complete_15_frame_epochs'] == pd['complete_epochs_exact_message8_1_through_15'] == 194)
    print('\n== B6 sender consequence and boundary ==')
    imp = ART['b6_sender_implication']
    check('00F exposes 36/46 meaningful B6 freshness bits', imp['what_00f_reveals'].startswith('36/46'))
    check('B6 message8 explicitly remains local', 'B6-local' in imp['what_remains_per_b6'] and 'must not be copied' in imp['what_remains_per_b6'])
    check('new authenticated epoch removes dependence on old B6 message8', 'does not require knowledge of the previous B6 message8' in imp['new_epoch_reanchor'])
    check('same-epoch sender still needs full message state', 'still needs the reconstructed full message8' in imp['same_epoch_boundary'])
    check('transition overlap is explicitly handled', 'current-1' in imp['transition_race'] and 'new 0x00F' in imp['transition_race'])
    check('slot4 secret remains unresolved', any(('slot-4 secret' in x for x in imp['still_blocking'])))
    check('live B6 sender policy remains unresolved', any(('live B6' in x for x in imp['still_blocking'])))
    check('capture identity boundary remains explicit', 'not exact H/F firmware-identity joins' in ART['evidence_boundary'])
    check('D7 message counter is not transferred to B6', 'No D7 message counter is transferred to B6' in ART['evidence_boundary'])
_section_corolla_hf_secoc_00f_freshness_bridge()
print()
print(f'\n== RESULT: {passed} passed, {failed} failed ==')
raise SystemExit(1 if failed else 0)
