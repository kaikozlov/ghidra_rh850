#!/usr/bin/env python3
"""Build exact-target static evidence for the maintainer 2026 Camry EPS."""
from __future__ import annotations
import argparse, hashlib, json, math, struct, sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))
from tools.compare_variant_application_rx import compare as compare_rx  # noqa: E402
from tools.camry_f33_corpus import body_bytes  # noqa: E402

RAW_DIR = REPO / 'targets/camry-2026/raw-20260826/codeflash'
RAW = RAW_DIR / 'camry_8965F3307000_codeflash_20260826T213719Z.bin'
RUN = RAW_DIR / 'camry_8965F3307000_codeflash_20260826T213719Z.run.json'
COVERAGE = RAW_DIR / 'camry_8965F3307000_codeflash_20260826T213719Z.coverage.bin'
NORMALIZED = REPO / 'firmware/camry-8965F3307000/CodeFlash.bin'
PAYLOAD = REPO / 'targets/camry-2026/raw-20260826/calvin_payload_codeflash_00000000_00200000.bin'
EVIDENCE = REPO / 'data/generated/camry_8965F3307000_decompiler_evidence.json'
P5 = REPO / 'data/generated/techstream_v18/p5_lateral_control_semantics.json'
H = REPO / 'community/albinoelephant/normalized/8965H1202000_CodeFlash.bin'
SIENNA = REPO / 'firmware/RH850_P1M-E_CodeFlash.bin'
OUT = REPO / 'data/generated/camry_8965F3307000_codeflash.json'

PROFILE_BASE = 0x25848
PROFILE_SIZE = 0x50
KEY_CONFIG = 0x25828
TP = 0x23DFC
SIGNAL_TO_PDU = TP - 0x1974
PDU_TABLE = TP - 0x173C
PDU_COUNT = 48
PDU_BUFFER_OFFSETS = PDU_TABLE + PDU_COUNT * 8


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()

def u16(b: bytes, o: int) -> int:
    return struct.unpack_from('<H', b, o)[0]

def u32(b: bytes, o: int) -> int:
    return struct.unpack_from('<I', b, o)[0]

def profile(b: bytes, index: int) -> dict:
    a = PROFILE_BASE + index * PROFILE_SIZE
    full_mac = u16(b, a)
    tx_mac = u16(b, a + 2)
    tx_fv = b[a + 0x15]
    trailer = math.ceil((tx_mac + tx_fv) / 8)
    secured_len = u32(b, a + 0x24)
    return {
        'index': index,
        'address': f'0x{a:08X}',
        'data_id': f'0x{u16(b, a + 0x0A):03X}',
        'full_cmac_bits': full_mac,
        'transmitted_cmac_bits': tx_mac,
        'sync_linkage': u16(b, a + 4),
        'trailer_bytes_configured': u16(b, a + 6),
        'is_sync': bool(b[a + 9]),
        'freshness_id': u16(b, a + 0x12),
        'full_freshness_bits': b[a + 0x14],
        'transmitted_freshness_bits': tx_fv,
        'cryptoif_handle': u32(b, a + 0x20),
        'secured_pdu_length': secured_len,
        'application_bytes': secured_len - trailer,
        'commit_callback': f'0x{u32(b, a + 0x30):08X}',
        'application_pdu_id': u16(b, a + 0x34),
        'upper_route_id': u16(b, a + 0x36),
        'secured_buffer_length': u32(b, a + 0x3C),
        'input_buffer_length': u32(b, a + 0x44),
        'get_freshness_callback': f'0x{u32(b, a + 0x48):08X}',
        'upper_callback': f'0x{u32(b, a + 0x4C):08X}',
        'record_sha256': sha(b[a:a + PROFILE_SIZE]),
    }

def need(text: str, *tokens: str) -> None:
    missing = [token for token in tokens if token not in text]
    if missing:
        raise ValueError(f'missing target-native decompiler tokens: {missing}')

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--out', type=Path, default=OUT)
    args = ap.parse_args()

    raw = RAW.read_bytes(); image = NORMALIZED.read_bytes(); coverage = COVERAGE.read_bytes(); payload = PAYLOAD.read_bytes()
    run = json.loads(RUN.read_text())
    evid = json.loads(EVIDENCE.read_text())
    p5 = json.loads(P5.read_text())
    h = H.read_bytes(); sienna = SIENNA.read_bytes()
    if len(raw) != 0x200000 or len(image) != 0x100000 or raw[:0x100000] != image or raw[0x100000:] != b'\xff' * 0x100000:
        raise ValueError('Camry CodeFlash normalization drift')
    if len(coverage) != 0x80000 or coverage != b'\x01' * len(coverage):
        raise ValueError('CodeFlash coverage is no longer complete')
    if image[0x180:0x1A8] != b'BOOT INFO AREA  R7F701381       72116350':
        raise ValueError('Camry BOOT INFO AREA / MCU identity drift')
    if run['result']['status'] != 'complete' or run['result']['unique_words'] != 0x80000 or run['result']['conflicts'] != 0 or run['result']['spi_errors'] != 0:
        raise ValueError('live CodeFlash acquisition completeness drift')
    if run['result']['sha256'] != sha(raw) or run['payload']['sha256'] != sha(payload):
        raise ValueError('live acquisition provenance hash drift')
    if evid['image']['sha256'] != sha(image) or evid['function_count'] != 27:
        raise ValueError('target-native decompiler evidence identity drift')
    funcs = {int(row['entry'], 16): row for row in evid['functions']}
    for entry, row in funcs.items():
        body = body_bytes(image, row)
        if sha(body) != row['body_sha256']:
            raise ValueError(f'decompiler body hash drift 0x{entry:X}')

    steering_conv = p5['power_steering']['emps_angle_conversion']['steering_angle']
    target_lateral = p5['power_steering']['target_lateral_id_semantics']
    target_lateral_values = {int(k): v for k, v in target_lateral['value_dictionary'].items()}
    if not (steering_conv['name'] == 'Steering Angle' and steering_conv['mul'] == 15 and
            steering_conv['div'] == 1 and steering_conv['decimal_point_count'] == 1 and
            steering_conv['unit'] == 'deg' and steering_conv['signed'] is True):
        raise ValueError('Techstream P5 Steering Angle conversion drift')
    expected_lateral = {1: 'PCS', 4: 'LDA', 10: 'Hands Off LTA', 11: 'LTA/LCA', 18: 'SDG', 19: 'PDA', 49: 'Self-Propelled Transport'}
    if target_lateral['oem_name'] != 'Target Lateral ID' or any(target_lateral_values.get(k) != v for k, v in expected_lateral.items()):
        raise ValueError('Techstream Target Lateral ID dictionary drift')

    # Target-native application Rx table comparison.
    vs_h = compare_rx(h, image, reference_id='8965H1202000', target_id='8965F3307000')
    vs_s = compare_rx(sienna, image, reference_id='8965B4512000', target_id='8965F3307000')

    # Exact three-profile SecOC configuration and shared slot selector.
    profiles = [profile(image, i) for i in range(3)]
    if [p['data_id'] for p in profiles] != ['0x00F', '0x0D7', '0x0B6']:
        raise ValueError('Camry SecOC profile IDs drift')
    key_cfg = image[KEY_CONFIG:KEY_CONFIG + 20]
    if u32(image, KEY_CONFIG) != 1 or u32(image, KEY_CONFIG + 4) != 4:
        raise ValueError('Camry ICU-S selector config drift')
    b6 = profiles[2]
    if not (b6['application_pdu_id'] == b6['upper_route_id'] == 44 and b6['secured_pdu_length'] == 32 and
            b6['application_bytes'] == 28 and b6['full_cmac_bits'] == 128 and b6['transmitted_cmac_bits'] == 28 and
            b6['full_freshness_bits'] == 46 and b6['transmitted_freshness_bits'] == 4 and b6['cryptoif_handle'] == 0):
        raise ValueError('Camry protected B6 profile geometry drift')

    # COM geometry: the target-native context resolves TP-0x1974 to absolute
    # CodeFlash 0x22488.  Prefer the canonical Ghidra data-reference graph over
    # decompiler-local `unaff_tp` spelling, which disappears once TP is seeded.
    scalar_row = funcs[0x7D12A]
    scalar = scalar_row['decompiled_c']
    scalar_refs = {int(r['to_addr'], 16) for r in scalar_row.get('data_references', [])}
    if 0x22488 not in scalar_refs:
        raise ValueError('Camry signal-to-PDU table reference drift')
    need(scalar, 'param_3 - 1', '*(short *)param_6')
    signal_count = (PDU_TABLE - SIGNAL_TO_PDU) // 2
    signal_to_pdu = [u16(image, SIGNAL_TO_PDU + i * 2) for i in range(signal_count)]
    pdu44_signals = [i for i, pdu_id in enumerate(signal_to_pdu) if pdu_id == 44]
    pdu44_desc = image[PDU_TABLE + 44 * 8:PDU_TABLE + 45 * 8]
    pdu44_buf = u16(image, PDU_BUFFER_OFFSETS + 44 * 2)
    if signal_count != 284 or pdu44_signals != list(range(259, 276)) or pdu44_desc != bytes.fromhex('060000002000000c') or pdu44_buf != 0x1B7:
        raise ValueError('Camry PDU44 COM geometry drift')

    # B6 generated unpacker and exact wire layout.
    unpack = funcs[0x4BD46]['decompiled_c']
    extracts = [
        (261, 0x1BA, 6, 0, False, 'gp-0x3744'),
        (262, 0x1BB, 16, 0, True, 'gp-0x3748'),
        (263, 0x1BD, 1, 7, False, 'gp-0x3735'),
        (264, 0x1BD, 3, 4, False, 'gp-0x3742'),
        (265, 0x1BD, 1, 2, False, 'gp-0x3740'),
        (266, 0x1BD, 2, 0, False, 'gp-0x373f'),
        (267, 0x1BE, 2, 6, False, 'gp-0x373e'),
        (268, 0x1BE, 6, 0, False, 'gp-0x373d'),
        (269, 0x1BF, 8, 0, False, 'gp-0x373c'),
        (270, 0x1C0, 8, 0, False, 'gp-0x373b'),
        (271, 0x1C1, 1, 7, False, 'gp-0x373a'),
        (272, 0x1C1, 1, 5, False, 'gp-0x3734'),
        (273, 0x1C1, 3, 0, False, 'gp-0x3736'),
    ]
    for sid, off, bits, start, signed, _ in extracts:
        token = f'FUN_0007d12a(0x{sid:x},0x{off:x},'
        need(unpack, token)
    unpack_refs = {int(r['to_addr'], 16) for r in funcs[0x4BD46].get('data_references', [])}
    if not {0xFEBE80BC, 0xFEBE80B8}.issubset(unpack_refs):
        raise ValueError('Camry B6 signal 261/262 destination reference drift')

    # Raw -> staging -> snapshot -> target-conditioning/plausibility consumers.
    stage = funcs[0x58074]['decompiled_c']; snap = funcs[0xBCD66]['decompiled_c']
    preprocess = funcs[0xCCF0E]['decompiled_c']; clamp = funcs[0xCCFB6]['decompiled_c']; plaus = funcs[0xCEE80]['decompiled_c']
    selector_decode = funcs[0xCEFFC]['decompiled_c']; selector_aux = funcs[0xCB73A]['decompiled_c']
    need(stage, 'DAT_febef130 = DAT_febe80bc;', 'DAT_febef1fa = DAT_febe80b8;')
    need(snap, '*(undefined2 *)(puVar15 + -0x970) = *(undefined2 *)(puVar15 + 0x39fa);',
         'puVar15[-0xa50] = puVar15[0x3930];')
    need(preprocess, 'iVar1 = DAT_febeae90 * 2;', '0x7fff', '-0x7fff', 'DAT_febec8b4')
    need(clamp, 'DAT_febec8b4', 'DAT_febec9fe', 'DAT_febeca00', 'DAT_febec8b8')
    need(plaus, 'sVar3 = *(short *)(puVar11 + -0x970);', 'FUN_000d0970((int)sVar3)')
    need(selector_decode, "DAT_febeadb0 == '\\x01'", "DAT_febeadb0 == '\\x04'", "DAT_febeadb0 == '\\n'", "DAT_febeadb0 == '\\v'", "DAT_febeadb0 == '\\x12'", "DAT_febeadb0 == '\\x13'")
    need(selector_aux, "DAT_febeadb0 == '1'")

    # Target-native 0x025 measured steering-angle feedback and exact target-vs-measured comparator.
    pdu35_signals = [i for i, pdu_id in enumerate(signal_to_pdu) if pdu_id == 35]
    pdu35_desc = image[PDU_TABLE + 35 * 8:PDU_TABLE + 36 * 8]
    pdu35_buf = u16(image, PDU_BUFFER_OFFSETS + 35 * 2)
    rx_025_soft, rx_025_len = struct.unpack_from('<II', image, 0x21FE8 + 30 * 8)
    if not (pdu35_signals == list(range(184, 194)) and pdu35_desc == bytes.fromhex('060000002000000c') and
            pdu35_buf == 0x127 and (rx_025_soft & 0x7FF) == 0x025 and bool(rx_025_soft & 0x40000000) and rx_025_len == 32):
        raise ValueError('Camry 0x025/PDU35 geometry drift')
    measured_unpack = funcs[0x4B59E]['decompiled_c']; measured_stage = funcs[0x47AE0]['decompiled_c']
    did1037 = funcs[0x4DBF8]['decompiled_c']; measured_combine = funcs[0xB3B06]['decompiled_c']
    measured_condition = funcs[0xCE9EA]['decompiled_c']; measured_vote = funcs[0xCEADA]['decompiled_c']
    comparator = funcs[0xCD128]['decompiled_c']
    need(measured_unpack,
         'FUN_0007d12a(0xbb,0x127,0xc,0,1,&DAT_febe8048);',
         'FUN_0007d12a(0xbc,299,4,4,1,puVar2 + -0x37b1);')
    need(measured_stage, 'FUN_0006a5fa((int)DAT_febe8048,auStack_e);',
         '*(undefined2 *)(puVar5 + -0x3aba) = auStack_e[0];')
    did1037_row = image[0x293AC:0x293BC]
    if did1037_row != bytes.fromhex('37100200f8db04000000000000000000'):
        raise ValueError('Camry DID1037 row drift')
    need(did1037, 'asStack_a[0] = DAT_febe7d46;', 'FUN_00070110', 'FUN_0006a5ac')
    need(stage, 'DAT_febef1a0 = DAT_febe8048;', 'DAT_febef06f = DAT_febe804f;')
    need(snap,
         '*(undefined2 *)(puVar15 + -0xa02) = *(undefined2 *)(puVar15 + 0x39a0);',
         'puVar15[-0xb3b] = puVar15[0x386f];')
    need(measured_combine, 'DAT_febeb16c = DAT_febef1a0 * 0xf + (short)DAT_febef06f;')
    need(measured_condition, '((int)DAT_febeacc5 + DAT_febeadfe * 0xf) * 0x6fb) / 0x200;',
         'iVar13 = iVar12 * 2 - iVar1;')
    need(measured_vote, 'iVar2 = DAT_febeae5e * 2 - iVar2;', 'DAT_febecad2', 'DAT_febecad4', 'DAT_febecad6')
    need(comparator,
         'DAT_febec8b8', 'DAT_febec9a0', 'DAT_febec9cc',
         'DAT_febecad2', 'DAT_febecad4', 'DAT_febecad6',
         'iVar1 = (iVar1 * 0xb76) / 0x400;', 'DAT_febec8dc = (iVar2 * 0xb76) / 0x400;',
         'DAT_febec8e0 = iVar1 - DAT_febec8dc;')
    # B6 raw target and 0x025 measured feedback share the comparator domain.  The
    # measured coarse field is Techstream's 1.5-deg Steering Angle and the signed
    # nibble supplies the 0.1-deg fraction used by the 15*coarse+fraction reconstruction.
    controller_deg_per_b6_count = 1024 / 17870
    controller_mrad_per_b6_count = controller_deg_per_b6_count * math.pi / 180 * 1000

    # Target-native SecOC worker chain and command-7 ICU job programming.
    rx_ind = funcs[0x8EE7C]['decompiled_c']; lookup = funcs[0x8F2B0]['decompiled_c']; verify = funcs[0x8F746]['decompiled_c']; cmd7 = funcs[0x8A8E4]['decompiled_c']
    need(rx_ind, 'FUN_0008f2b0', 'FUN_0008f34a')
    need(lookup, '(&DAT_0002587c)[(short)uVar1 * 0x28]', 'if (2 < uVar1)', 'uVar1 < 3')
    need(verify, 'FUN_0008f434', 'FUN_0008ecb2', 'FUN_0008f676', '*(undefined4 *)(puVar1 + -0x62d8) = 0x24;')
    need(cmd7, 'DAT_ffc5d000 = puVar2[4] << 0x10 | 7;')

    stages = {row['name']: row for row in run['stages']}
    out = {
        'schema': 'camry-8965f3307000-codeflash-static-v1',
        'target': {
            'vehicle': '2026 Toyota Camry',
            'application_f181': ['8965F3307000', '8A3113303100'],
            'normalized_codeflash_sha256': sha(image),
            'raw_transport_dump_sha256': sha(raw),
            'raw_transport_dump_size': len(raw),
            'populated_codeflash_size': len(image),
            'upper_transport_half_erased_ff': True,
            'mcu': 'Renesas RH850/P1M-E R7F701381',
            'boot_info_area': {'address': '0x00000180', 'raw_ascii': 'BOOT INFO AREA  R7F701381       72116350'},
        },
        'acquisition': {
            'schema': run['schema'],
            'route': run['target'],
            'nrt_ready_values': stages['NRTD Ready-status guard']['ready_values'],
            'boot_f181_hex': stages['boot identity']['observed_hex'],
            'boot_read_memory_by_address': {'status': stages['boot SID 0x23 codeflash probe']['status'], 'nrc': stages['boot SID 0x23 codeflash probe']['nrc']},
            'uds_variant': run['uds_variant'],
            'did_0203': stages['UDS variant / DID 0x0203']['value'],
            'did_0201_0202': stages['DID 0x0201/0x0202']['value'],
            'request_download': stages['RequestDownload']['data_hex'],
            'verify_10f0': stages['RoutineControl 0x10F0']['data_hex'],
            'callback_ff00': stages['RoutineControl 0xFF00 callback trigger']['data_hex'],
            'payload': run['payload'],
            'result': run['result'],
            'boundary': 'The recovered artifact is read-only CodeFlash output, but acquisition uses the authenticated boot-RAM payload path and an FF00 callback trigger; it is not a stock UDS memory-read service.',
        },
        'application_rx': {
            'camry_table_start': vs_h['target']['table_start'],
            'camry_descriptor_count': vs_h['target']['descriptor_count'],
            'vs_corolla_h': vs_h['summary'],
            'vs_sienna_b4512000': vs_s['summary'],
            'interpretation': 'All 40 Corolla-H normal application Rx descriptors are present on Camry; Camry adds 0x116/8, 0x0D8/8, and 0x1DA/8. This is target-native configuration continuity, not a blanket semantic-equivalence claim.',
        },
        'secoc_receive': {
            'key_config_address': f'0x{KEY_CONFIG:08X}',
            'key_config_raw_hex': key_cfg.hex(),
            'selector_type': u32(image, KEY_CONFIG),
            'selector': u32(image, KEY_CONFIG + 4),
            'profile_base': f'0x{PROFILE_BASE:08X}',
            'profile_count': 3,
            'profiles': profiles,
            'command7_function': '0x0008A8E4',
            'worker_chain': ['0x0008EE7C RxIndication', '0x0008F2B0 3-record lookup', '0x0008F34A secured-PDU queue', '0x0008F746 verify worker', '0x0008F434 freshness split', '0x0008ECB2 auth-input builder', '0x0008F676 CMAC submit'],
            'interpretation': 'Camry protects exactly 0x00F, 0x0D7, and 0x0B6 in the recovered three-record receive table. B6 is PDU44 with 28 application bytes + FV4/MAC28 trailer and selects crypto handle 0; the shared key config selects ICU-S slot 4 and target-native code programs command 7.',
        },
        'b6_com': {
            'tp': f'0x{TP:08X}',
            'signal_to_pdu_table': f'0x{SIGNAL_TO_PDU:08X}',
            'signal_count': signal_count,
            'pdu_table': f'0x{PDU_TABLE:08X}',
            'pdu_count': PDU_COUNT,
            'pdu_buffer_offset_table': f'0x{PDU_BUFFER_OFFSETS:08X}',
            'pdu44_descriptor_hex': pdu44_desc.hex(),
            'pdu44_buffer_offset': f'0x{pdu44_buf:03X}',
            'pdu44_signal_ids': pdu44_signals,
            'scalar_signal_ids': [x[0] for x in extracts],
            'non_scalar_bookends': [259, 260, 274, 275],
            'wire_fields': [
                {'signal_id': sid, 'byte_offset': off - pdu44_buf, 'absolute_buffer_offset': f'0x{off:03X}', 'bit_length': bits, 'bit_start': start, 'signed': signed, 'raw_destination': dest}
                for sid, off, bits, start, signed, dest in extracts
            ],
            'deadline_descriptor': {'configured_value': 6, 'successful_receive_reload_ticks': 7, 'tick_period_ms': None},
            'boundary': 'Seven foreground ticks are target-native; this pass does not transfer Corolla H\'s 5 ms tick period to Camry without a Camry timer proof.',
        },
        'b6_steering_command': {
            'selector_signal': {
                'signal_id': 261, 'wire': 'B3[5:0]', 'raw': 'gp-0x3744', 'staged': 'gp+0x3930', 'snapshot': 'gp-0xA50',
                'oem_name': target_lateral['oem_name'],
                'target_native_decoder': '0x000CEFFC',
                'accepted_controller_values': {str(k): target_lateral_values[k] for k in (1, 4, 10, 11, 18, 19)},
                'additional_target_native_value': {'49': target_lateral_values[49]},
                'join_proof': 'Camry 0xCEFFC consumes the protected B3 snapshot and recognizes exactly 1/4/10/11/18/19; Toyota P5 Target Lateral ID assigns those values PCS/LDA/Hands Off LTA/LTA-LCA/SDG/PDA. Camry 0xCB73A separately recognizes raw 49, matching Self-Propelled Transport.'
            },
            'signed_target_signal': {
                'signal_id': 262, 'wire': 'B4:B5 signed16', 'raw': 'gp-0x3748', 'staged': 'gp+0x39FA', 'snapshot': 'gp-0x970',
                'classification': 'target steering angle command',
            },
            'preprocessor': {'entry': '0x000CCF0E', 'operation': 'saturate(2 * signed16(B4:B5)) followed by interpolation/history'},
            'clamp': {'entry': '0x000CCFB6', 'role': 'mode-dependent delta/absolute clamp of the preprocessed target-angle domain'},
            'independent_plausibility_consumer': {'entry': '0x000CEE80', 'source': 'gp-0x970', 'role': 'target-angle magnitude/threshold plausibility path'},
            'measured_steering_angle_feedback': {
                'can_id': '0x025', 'pdu_id': 35, 'buffer_offset': '0x127',
                'coarse_signal': {'signal_id': 187, 'wire': 'B0..B1 signed12', 'raw': 'gp-0x37B8', 'techstream_did': '0x1037', 'techstream_name': steering_conv['name'], 'scale_deg_per_count': 1.5},
                'fraction_signal': {'signal_id': 188, 'wire': 'B2[7:4] signed4', 'raw': 'gp-0x37B1', 'scale_deg_per_count': 0.1},
                'did1037_row': {'address': '0x000293AC', 'callback': '0x0004DBF8', 'raw_hex': did1037_row.hex()},
                'reconstruction': '0xB3B06: 15*coarse + signed_fraction; 0xCE9EA: reconstructed_tenths_deg * 0x6FB / 0x200; 0xCEADA republishes the valid measured-angle domain into a voted triple.',
            },
            'target_minus_measured_comparator': {
                'entry': '0x000CD128',
                'target_inputs': ['DAT_000010B8', 'DAT_000011A0', 'DAT_000011CC'],
                'measured_inputs': ['DAT_000012D2', 'DAT_000012D4', 'DAT_000012D6'],
                'gain': '0xB76/0x400 applied identically to target and measured domains before subtraction',
                'relation': 'scaled_target - scaled_measured',
            },
            'controller_equivalent_scale': {
                'fraction_deg_per_b6_count': {'numerator': 1024, 'denominator': 17870},
                'deg_per_b6_count': controller_deg_per_b6_count,
                'mrad_per_b6_count': controller_mrad_per_b6_count,
                'difference_from_exact_1_mrad_percent': (controller_mrad_per_b6_count - 1.0) * 100,
                'boundary': 'This is the exact linearized controller-equivalent relation implied by target-native integer gains plus the Techstream 0x1037 Steering Angle scale. Integer truncation/saturation apply, and firmware does not literally name the B6 wire engineering unit as milliradians.'
            },
            'classification': 'target-native protected B6 Target Lateral ID plus signed16 target steering angle command, closed by the Camry 0x025/DID1037 measured-angle feedback and same-gain target-minus-measured comparator.',
        },
        'decompiler_evidence': {
            'path': str(EVIDENCE.relative_to(REPO)),
            'sha256': sha(EVIDENCE.read_bytes()),
            'function_count': evid['function_count'],
        },
        'cross_variant_boundary': 'The exact Camry image now replaces prior H/F inference for Rx/SecOC/B6 wire, Target Lateral ID, target steering-angle ingress, and measured-angle feedback/comparator facts. Corolla-only wall-clock timing, steering limits, fault thresholds, and final motor-control constants must still be revalidated target-natively before production actuation.',
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(out, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    print(f'wrote {args.out}')
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
