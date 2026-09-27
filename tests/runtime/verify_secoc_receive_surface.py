#!/usr/bin/env python3
"""Firmware/JSON pins for the base-image SecOC receive chain: application path, Rx control surface, freshness trials, and FD sensor correlations.

Domain split; assertions and helpers are carried over verbatim.
"""
from __future__ import annotations


from tools import REPO_ROOT
ROOT = REPO = REPO_ROOT

passed = failed = 0


def check(name, cond, detail=""):
    global passed, failed
    ok = bool(cond)
    passed += int(ok)
    failed += int(not ok)
    suffix = f" ({detail})" if detail else ""
    print(f"[{'PASS' if ok else 'FAIL'}] {name}{suffix}")

print("== secoc application ==")
def _section_secoc_application():
    import math
    import struct
    from collections import Counter
    from Crypto.Cipher import AES
    from Crypto.Hash import CMAC
    REPO = REPO_ROOT
    CF = (REPO / 'firmware' / 'RH850_P1M-E_CodeFlash.bin').read_bytes()
    DF = (REPO / 'firmware' / 'RH850_P1M-E_DataFlash.bin').read_bytes()

    def u16(a: int) -> int:
        return struct.unpack_from('<H', CF, a)[0]

    def u32(a: int) -> int:
        return struct.unpack_from('<I', CF, a)[0]
    print('== generated SecOC receive records ==')
    TP = 147172
    RECORD_BASE = TP + 6796
    RECORD_SIZE = 80
    records = [RECORD_BASE + i * RECORD_SIZE for i in range(6)]
    expected_ids = [15, 740, 305, 306, 144, 215]
    expected_pdu = [11, 6, 26, 35, 46, 47]
    expected_secured_len = [8, 8, 8, 8, 32, 32]
    expected_trailer_len = [8, 4, 4, 4, 4, 4]
    expected_full_fv = [36, 46, 46, 46, 46, 46]
    expected_trunc_fv = [36, 4, 4, 4, 4, 4]
    expected_handles = [0, 0, 0, 0, 0, 0]
    expected_crypto_buffer_lengths = [8, 8, 8, 8, 32, 32]
    expected_freshness_ids = [0, 1, 2, 4, 5, 6]
    check('record table resolves to 0x25970', RECORD_BASE == 153968)
    check('six records have exact Data/CAN IDs', [u16(a + 10) for a in records] == expected_ids)
    check('records have exact application RX PDU IDs', [u16(a + 52) for a in records] == expected_pdu)
    check('records have exact secured PDU lengths', [u32(a + 60) for a in records] == expected_secured_len)
    check('records duplicate exact buffer lengths', [u32(a + 68) for a in records] == expected_secured_len)
    check('sync/normal trailer lengths are 8/4', [u16(a + 6) for a in records] == expected_trailer_len)
    check('all records configure 128-bit full CMAC', all((u16(a) == 128 for a in records)))
    check('all records configure 28-bit transmitted CMAC', all((u16(a + 2) == 28 for a in records)))
    check('full freshness widths are 36/46 bits', [CF[a + 20] for a in records] == expected_full_fv)
    check('transmitted freshness widths are 36/4 bits', [CF[a + 21] for a in records] == expected_trunc_fv)
    check('freshness IDs match exact sequence', [u16(a + 18) for a in records] == expected_freshness_ids)
    check('all SecOC profiles use CSM/CryptoIf handle 0', [u32(a + 32) for a in records] == expected_handles)
    check('classic/FD crypto buffer lengths are 8/32', [u32(a + 36) for a in records] == expected_crypto_buffer_lengths)
    check('all profiles use freshness callback 0x8E8E6', all((u32(a + 72) == 583910 for a in records)))
    check('all profiles use freshness commit callback 0x8E942', all((u32(a + 48) == 584002 for a in records)))
    check('all profiles use application state callback 0x69182', all((u32(a + 76) == 430466 for a in records)))
    payload_lengths = [total - trailer for total, trailer in zip(expected_secured_len, expected_trailer_len)]
    full_fv_bytes = [(bits + 7) // 8 for bits in expected_full_fv]
    authenticated_lengths = [2 + payload + fv for payload, fv in zip(payload_lengths, full_fv_bytes)]
    check('sync has no authentic payload', payload_lengths[0] == 0)
    check('classic protected payloads are four bytes', payload_lengths[1:4] == [4, 4, 4])
    check('CAN-FD protected payloads are 28 bytes', payload_lengths[4:] == [28, 28])
    check('classic protected authenticated input is 96 bits', authenticated_lengths[1:4] == [12, 12, 12])
    check('CAN-FD authenticated input is 36 bytes', authenticated_lengths[4:] == [36, 36])
    check('sync authenticated input is ID16 + freshness36', authenticated_lengths[0] == 7)
    check('ordinary trailer is exactly FV4 + CMAC28', expected_trunc_fv[1] + 28 == 32)
    check('sync trailer is exactly FV36 + CMAC28', expected_trunc_fv[0] + 28 == 64)
    print('\n== CAN acceptance to SecOC PDU routing ==')
    normal_ids = [u32(139288 + i * 8) & 2047 for i in range(47)]
    acceptance_ids = [u32(143776 + i * 16) for i in range(51)]
    expected_routes = {740: (0, 6), 15: (5, 11), 305: (20, 26), 306: (29, 35), 144: (40, 46), 215: (41, 47)}
    for can_id, (index, pdu_id) in expected_routes.items():
        check(f'CAN {can_id:#05x} acceptance index', acceptance_ids[index] == can_id)
        check(f'CAN {can_id:#05x} maps to SecOC PDU {pdu_id}', 6 + index == pdu_id)
    check('normal RX descriptors mirror all six SecOC CAN IDs', all((normal_ids[index] == can_id for can_id, (index, _) in expected_routes.items())))
    check('0x344 has no application acceptance rule', 836 not in acceptance_ids)
    check('0x344 has no SecOC receive record', 836 not in [u16(a + 10) for a in records])
    check('0x344 has no aligned 32-bit CodeFlash literal', all((u32(a) != 836 for a in range(0, len(CF) - 3, 4))))
    print('\n== ICU-S slot-4 configuration and disabled known-answer vector ==')
    secoc_key_cfg = CF[153936:153956]
    kat_message = CF[136676:136692]
    kat_tag = CF[136692:136708]
    kat_cfg = CF[136708:136728]
    check('SecOC crypto config type is 1', struct.unpack_from('<I', secoc_key_cfg)[0] == 1)
    check('SecOC crypto config selects slot 4', secoc_key_cfg[4] == 4 and secoc_key_cfg[5:] == bytes(15))
    check('known-answer config matches type 1 / slot 4', kat_cfg == secoc_key_cfg)
    check('known-answer input is 16 zero bytes', kat_message == bytes(16))
    check('known-answer tag is exact embedded value', kat_tag.hex() == 'b290fa2ea7b6b52eb124134522a6e540')
    kat = CMAC.new(bytes([255]) * 16, ciphermod=AES)
    kat.update(bytes(16))
    check('known-answer tag is AES-CMAC under erased FF*16 key', kat.digest() == kat_tag)
    zero_kat = CMAC.new(bytes(16), ciphermod=AES)
    zero_kat.update(bytes(16))
    check('known-answer tag is not the zero-key vector', zero_kat.digest() != kat_tag)
    check('known-answer compile-time gate byte is zero', CF[200435] == 0)
    check('synchronous known-answer body requires gate byte 0x5A', CF[426242:426256] == bytes.fromhex('400e0300a10ff30e0106a6ffda2d'))
    check('asynchronous known-answer body requires the same gate byte 0x5A', CF[426672:426686] == bytes.fromhex('400e0300a10ff30e0106a6ffaa1d'))
    check('ICU request loads key selector from config+4', CF[556912:556918] == bytes.fromhex('9b0f05000d0d'))
    check('ICU command encodes key slot <<16 OR command 7', CF[563462:563468] == bytes.fromhex('d08a910e0700'))
    check('ICU command writes FFC5D000', CF[563468:563474] == bytes.fromhex('80070f08a08b'))
    check('CMAC verify command state is literal 7', CF[563406:563412] == bytes.fromhex('070a640f295b'))
    print('\n== ICU-S command-5 MAC-generation family ==')
    generate_records = [163704, 163736]
    verify_records = [163772, 163804]
    check('command-5 lower table has IDs 0 and 1', [u16(a) for a in generate_records] == [0, 1])
    check('command-5 records use the same adapter and completion worker', all((u32(a + 20) == 556236 and u32(a + 24) == 556496 for a in generate_records)))
    check('command-5 records use synchronous/asynchronous callbacks', [u32(a + 4) for a in generate_records] == [559964, 430698])
    check('command-7 records use the seeded verification completion worker', all((u32(a + 24) == 557532 for a in verify_records)))
    check('command-5 prepare loads key selector from config+4', CF[555822:555826] == bytes.fromhex('9a0f0500'))
    check('command-5 engine records literal operation 5', CF[562908:562914] == bytes.fromhex('050a640f295b'))
    check('command-5 command encodes selector <<16 OR 5 and writes ICUSCMD', CF[562996:563008] == bytes.fromhex('d092920e050080070f08a08b'))
    check('command-5 completion clamps caller output length to 16 bytes', CF[555902:555920] == bytes.fromhex('e0e9ca0d00450806efffb905204610000145'))
    check('command-5 application harness compares all 16 generated bytes', CF[430184:430222] == bytes.fromhex('20563300000a01f0c4f19e9fab999e978b99f391c205205644007f00410a0106f0ffa9f57f00'))
    check('only configured command-5 dispatch call is the application crypto-test harness', CF.count(bytes.fromhex('81ffa4f7')) == 1 and CF[428972:428976] == bytes.fromhex('81ffa4f7'))
    check('command-5 harness obtains selector from RAM rather than hard-coding slot 4', CF[428930:428946] == bytes.fromhex('03f0070d840f9998204e1000644f6198'))
    check('command-5 engine accepts every software selector from 0 through 14', CF[562774:562812] == bytes.fromhex('0495407eff0001980180c89ad8824f99109901808882d08600ff13810198989a10996e92ab0d'))
    print('\n== dormant CAN-controlled command-5 test harness ==')
    check('normal receive descriptors 14..18 are CAN 0x01B..0x01F', normal_ids[14:19] == [27, 28, 29, 30, 31])
    check('crypto-test bank uses COM update-counter indices 20..24', [u16(153848 + i * 2) for i in range(5)] == [20, 21, 22, 23, 24])
    check('crypto-test bank uses signal IDs 95..100', [u16(153874 + i * 2) for i in range(6)] == [95, 96, 97, 98, 99, 100])
    check('bank-1 activator initializes active/state and snapshots counters', CF[430104:430146] == bytes.fromhex('80072100a40f8f98e009ea0d010a440f8f9864077a98200e1100440f9098bfff14efbfff88ff40063f00'))
    check('bank-1 activator has no CodeFlash function-pointer entry', struct.pack('<I', 430104) not in CF)
    check('command-5 upper dispatcher has no CodeFlash function-pointer entry', struct.pack('<I', 557904) not in CF)
    check('command-5 interrupt callback is a distinct recovered function', CF[556052:556144] == bytes.fromhex('80072100840f915901064cffea2580fffe216152aa0d1f0a640f995964079559200ec3ff0032d515e051f2150a06eeffc215640795591f0a640f995980ffaa22645785590032bfff92f1200ee1ff0132440f9059bfff52ff40063f00'))
    check('command-7 has its paired interrupt callback', CF[557096:557184] == bytes.fromhex('840f915901064cffea2580ffee1d6152aa0d1f0a640f995964079559200ec3ff0032d515e051f2150a06eeffc215640795591f0a640f995980ff9a1e645785590032bfff82ed200ee1ff0132440f9059bfff52ff40063f00'))
    print('\n== authenticated-input and freshness packing code ==')
    check('authenticated-input builder stores big-endian Data ID', CF[580432:580444] == bytes.fromhex('880a470f00006808470f0100'))
    check('freshness parser has explicit four-bit profile branch', CF[584642:584650] == bytes.fromhex('08f0643aba0d0105'))
    check('full-freshness packer has explicit 46-bit profile branch', CF[584268:584286] == bytes.fromhex('06f06b08889f0100f309eb350106d2ffba25'))

    def pack_freshness(trip: int, reset: int, message: int) -> bytes:
        return struct.pack('>HI', trip & 65535, (reset & 1048575) << 12 | (message & 255) << 4 | (reset & 3) << 2)
    sample = pack_freshness(4660, 354185, 171)
    check('freshness reference packing is six bytes', len(sample) == 6)
    check('freshness leaves two low pad bits clear', sample[-1] & 3 == 0)
    transmitted_flag = (171 & 3) << 2 | 354185 & 3
    check('transmitted nibble combines message-low2/reset-low2', transmitted_flag == 13)
    check('full freshness retains message-low4 in its high final nibble', sample[-1] >> 4 == 171 & 15)
    print('\n== object-15 separation and corrected work buffers ==')
    obj15 = struct.unpack_from('<HHI', CF, 176300 + 15 * 8)
    check('object 15 remains len32/base41/RAM FEBF02E8', obj15 == (32, 41, 4273930984))
    check('FEBF02F8 has no direct CodeFlash pointer literal', struct.pack('<I', 4273931000) not in CF)
    check('FEBF02E8 appears only in the object-15 descriptor', CF.find(struct.pack('<I', 4273930984)) == 176424 and CF.find(struct.pack('<I', 4273930984), 176425) == -1)
    APP_GP = 4273911808
    work_root = APP_GP + 21256
    obj15_group = work_root + (15 & 3) * 96
    check('correct triplicate work root is FEBF0B08', work_root == 4273933064)
    check('object-15 work buffers are FEBF0C28/48/68', (obj15_group, obj15_group + 32, obj15_group + 64) == (4273933352, 4273933384, 4273933416))
    check('restore code uses GP displacement 0x5308', CF[423354:423358] == bytes.fromhex('24e60853'))
    check('persistence buffers are FEBF06A8/6C8/6E8', tuple((APP_GP + 20136 + x for x in (0, 32, 64))) == (4273931944, 4273931976, 4273932008))
    copy_data = []
    copy_valid = []
    for page, mask, storage_index in [(440, 0, 40), (436, 85, 44), (432, 170, 48)]:
        rec = DF[page * 64:(page + 1) * 64]
        copy_valid.append(struct.unpack_from('<H', rec)[0] == storage_index and rec[-4:] == b'\xaa' * 4)
        copy_data.append(bytes((b ^ mask for b in rec[4:36])))
    check('all three object-15 records are invalid', copy_valid == [False, False, False], str(copy_valid))
    check('invalid object-15 copies do not decode to consensus', len(set(copy_data)) == 3)
    for obj, pages in {12: (443, 439, 435), 13: (442, 438, 434), 14: (441, 437, 433)}.items():
        valid = []
        for page, storage_index in zip(pages, (40 - (15 - obj), 44 - (15 - obj), 48 - (15 - obj))):
            rec = DF[page * 64:(page + 1) * 64]
            valid.append(struct.unpack_from('<H', rec)[0] == storage_index and rec[-4:] == b'\xaa' * 4)
        check(f'object {obj} optional-bank copies are also invalid', valid == [False, False, False], str(valid))
    raw_field = DF[28180:28196]
    entropy = -sum((n / 16 * math.log2(n / 16) for n in Counter(raw_field).values()))
    check('raw object-15 field is exact low-entropy snapshot value', raw_field.hex() == '00000000040000808202000000000000' and entropy < 1.4)
    print('\n== SecOC lower-job lookup ==')
    lower_records = verify_records
    lower_ids = [u16(a) for a in lower_records]
    check('lower CryptoIf table has only IDs 0 and 1', lower_ids == [0, 1])
    check('both lower records target ICU verify adapter 0x880DC', all((u32(a + 20) == 557276 for a in lower_records)))
    check('SecOC handle 0 resolves to lower ICU driver record 0', set(expected_handles) == {0} and 0 in lower_ids)
    check('SecOC worker loads handle from record+0x20', CF[583160:583168] == bytes.fromhex('fd372100233e1c00'))

_section_secoc_application()
print()

print("== secoc rx control surface ==")
def _section_secoc_rx_control_surface():
    import csv
    import struct
    ROOT = REPO_ROOT
    CF = (ROOT / 'firmware' / 'RH850_P1M-E_CodeFlash.bin').read_bytes()
    SURFACE = ROOT / 'data' / 'secoc_rx_control_surface.csv'
    RXMAP = ROOT / 'data' / 'application_rx_map.csv'

    def u16(off: int) -> int:
        return struct.unpack_from('<H', CF, off)[0]

    def u32(off: int) -> int:
        return struct.unpack_from('<I', CF, off)[0]
    with SURFACE.open(newline='', encoding='utf-8') as f:
        rows = list(csv.DictReader(f))
    by_id = {int(r['can_id'], 0): r for r in rows}
    expected_ids = [15, 740, 305, 306, 144, 215]
    expected_pdu = [11, 6, 26, 35, 46, 47]
    expected_len = [8, 8, 8, 8, 32, 32]
    print('== profile census ==')
    check('surface has exactly six rows', len(rows) == 6)
    check('surface CAN IDs are exact', list(by_id) == expected_ids, repr(list(by_id)))
    check('exact role classes', [by_id[i]['role_class'] for i in expected_ids] == ['synchronization', 'steering_command', 'steering_command', 'protected_snapshot', 'rear_wheel_speed_and_steering_angle_speed_validity', 'sp1_vehicle_speed_validity'])
    check('only 0x2E4 and 0x131 select command modes', {i for i, r in by_id.items() if r['command_mode'] != 'none'} == {740, 305})
    check('0x132 remains bounded snapshot negative', by_id[306]['evidence_grade'] == 'bounded')
    print('\n== firmware SecOC records ==')
    records = [153968 + i * 80 for i in range(6)]
    check('record IDs match ledger', [u16(a + 10) for a in records] == expected_ids)
    check('record PDU IDs match ledger', [u16(a + 52) for a in records] == expected_pdu)
    check('record secured lengths match ledger', [u32(a + 60) for a in records] == expected_len)
    check('ledger PDU IDs match firmware', [int(by_id[i]['rx_pdu_id']) for i in expected_ids] == expected_pdu)
    check('ledger formats match firmware lengths', [by_id[i]['can_format'] for i in expected_ids] == ['classic'] * 4 + ['fd', 'fd'])
    check('all profiles transmit 28 CMAC bits', all((u16(a + 2) == 28 for a in records)))
    with RXMAP.open(newline='', encoding='utf-8') as f:
        rx_rows = list(csv.DictReader(f))
    by_signal = {int(r['signal_id']): r for r in rx_rows}
    with (ROOT / 'data' / 'application_rx_signal_evidence.csv').open(newline='', encoding='utf-8') as f:
        evidence_rows = list(csv.DictReader(f))
    by_evidence_signal = {int(r['signal_id']): r for r in evidence_rows}
    print('\n== protected steering commands ==')
    check('0x2E4 request destination is FEBE7F98', int(by_signal[60]['dest'], 0) == 4273897368)
    check('0x2E4 torque destination is FEBE7F94', int(by_signal[61]['dest'], 0) == 4273897364)
    check('0x131 request2 destination is FEBE7FC5', int(by_signal[112]['dest'], 0) == 4273897413)
    check('0x131 signed angle destination is FEBE7FBE', int(by_signal[114]['dest'], 0) == 4273897406)
    check('0x131 angle ledger reaches C0D6/C144', 'C0D6' in by_id[305]['derived_control_state'] and 'FEBEC144' in by_id[305]['derived_control_state'])
    print('\n== protected 0x090 measurement/validity domain ==')
    check('0x090 three 10-bit raw signals are exact', [(int(by_signal[s]['dest'], 0), int(by_signal[s]['bit_length'])) for s in (270, 273, 276)] == [(4273897562, 10), (4273897564, 10), (4273897566, 10)])
    check('0x090 ledger pins normalized steering-cycle states', all((t in by_id[144]['derived_control_state'] for t in ('FEBEB6AA', 'FEBEB714', 'FEBEAE02', 'FEBEAF00'))))
    check('0x090 ledger distinguishes prerequisite from command selection', 'never selects C13A/C13D' in by_id[144]['downstream_effect'])
    print('\n== protected 0x0D7 speed/status domain ==')
    check('signal 283 is unsigned16 at FEBE8070', int(by_signal[283]['dest'], 0) == 4273897584 and int(by_signal[283]['bit_length']) == 16 and (int(by_signal[283]['signed']) == 0))
    check('signal 280 corrected destination is FEBE8076', int(by_signal[280]['dest'], 0) == 4273897590)
    check('signal 284 independently owns FEBE8072', int(by_signal[284]['dest'], 0) == 4273897586)
    check('signal 280 evidence marks generated stack persistence', 'stack temporary' in by_evidence_signal[280]['classification_basis'])
    check('signal 280 stack destination setup bytes', CF[308226:308234] == bytes.fromhex('03f0230e0b000105'))
    check('signal 280 persists stack byte to FEBE8076', CF[308304:308320] == bytes.fromhex('a30f0b0020361c0044ef7ac8440f76c8'))
    check('0x0D7 ledger reaches named vehicle-speed state', 'application_vehicle_speed_raw' in by_id[215]['derived_control_state'])
    check('0x0D7 ledger records status/fault path', 'B6396' in by_id[215]['derived_control_state'])
_section_secoc_rx_control_surface()
print()

print("== secoc freshness trials ==")
def _section_secoc_freshness_trials():
    import subprocess
    import sys
    import tempfile
    from pathlib import Path
    REPO = REPO_ROOT
    from exploit.followups.secoc_freshness_trials import FreshnessTrialError, TAG_MASK, build_fd_suffix_alias, build_future_sync, build_reset_replay, build_tag_guesses, parse_protected_frame, parse_sync_frame, replace_tag, sync_candidate_is_forward
    from tools.toyota_support.toyota_secoc_signer import sign_classic_frame, sign_sync_frame
    KEY = bytes(range(16))

    def rejects(fn) -> bool:
        try:
            fn()
        except FreshnessTrialError:
            return True
        return False
    print('== synchronization parsing and firmware ordering model ==')
    sync = sign_sync_frame(KEY, 4660, 354185)
    parsed_sync = parse_sync_frame(sync)
    check('sync parser recovers trip/reset', (parsed_sync.trip, parsed_sync.reset) == (4660, 354185))
    check('sync parser preserves exact tag28', parsed_sync.tag28 == int.from_bytes(sync, 'big') & TAG_MASK)
    check('equal sync rejected', not sync_candidate_is_forward(7, 9, 7, 9))
    check('rollback sync rejected', not sync_candidate_is_forward(7, 9, 6, 1048575))
    check('same-trip reset advance accepted', sync_candidate_is_forward(7, 9, 7, 10))
    check('large forward trip jump accepted', sync_candidate_is_forward(1, 0, 57344, 0))
    check('configured wrap accepted', sync_candidate_is_forward(65520, 4, 1, 0))
    print('\n== reset replay artifact ==')
    protected = sign_classic_frame(KEY, 740, bytes.fromhex('01020304'), 4660, 354185, 171)
    replay = build_reset_replay(sync, [(740, protected)])
    check('reset replay binds SECOC-012', replay['finding_ids'] == ['SECOC-012'])
    check('captured positive sync is forward from zero', replay['captured_sync']['structurally_forward_from_post_init_zero'] is True)
    check('reset replay preserves signed sync bytes unchanged', replay['captured_sync']['frame'] == sync.hex())
    check('reset replay preserves protected bytes unchanged', replay['protected_replays'][0]['frame'] == protected.hex())
    check('reset replay exposes startup suppression as dynamic unknown', any(('startup' in item for item in replay['dynamic_unknowns'])))
    check('zero sync cannot masquerade as replay candidate', rejects(lambda: build_reset_replay(bytes(8), [(740, protected)])))
    print('\n== future synchronization artifact ==')
    current = sign_sync_frame(KEY, 10, 20)
    future = sign_sync_frame(KEY, 57344, 1)
    future_plan = build_future_sync(current, future)
    check('future-sync binds SECOC-012', future_plan['finding_ids'] == ['SECOC-012'])
    check('future sync is structurally forward', future_plan['candidate_sync']['structurally_forward'] is True)
    check('future-sync requires independently valid MAC', 'valid MAC' in future_plan['cryptographic_precondition'])
    backward = sign_sync_frame(KEY, 9, 1048575)
    check('backward candidate is rejected offline', rejects(lambda: build_future_sync(current, backward)))
    print('\n== FD ignored-suffix alias artifact ==')
    base32 = bytes(range(32))
    alias48 = build_fd_suffix_alias(base32, bytes.fromhex('aa' * 16))
    alias64 = build_fd_suffix_alias(base32, bytes.fromhex('55' * 32))
    check('FD alias binds SECOC-014', alias48['finding_ids'] == ['SECOC-014'])
    check('DLC48 alias preserves exact first 32 bytes', bytes.fromhex(alias48['physical_frame'])[:32] == base32 and alias48['physical_dlc'] == 48)
    check('DLC64 alias preserves exact first 32 bytes', bytes.fromhex(alias64['physical_frame'])[:32] == base32 and alias64['physical_dlc'] == 64)
    check('FD alias declares EPS effective length 32', alias48['eps_secoc_effective_length'] == 32 and alias48['eps_authenticated_view_unchanged'] is True)
    check('invalid FD suffix width rejected', rejects(lambda: build_fd_suffix_alias(base32, bytes(8))))
    print('\n== bounded tag-guess artifact ==')
    parsed = parse_protected_frame(protected)
    mutated = replace_tag(protected, 1193046)
    mutated_parsed = parse_protected_frame(mutated)
    check('tag replacement preserves authentic payload', mutated_parsed.payload == parsed.payload)
    check('tag replacement preserves transmitted freshness nibble', mutated_parsed.transmitted_freshness == parsed.transmitted_freshness)
    check('tag replacement changes only requested tag28', mutated_parsed.tag28 == 1193046)
    summary, rows = build_tag_guesses(740, protected, 256, 4)
    check('tag-guess artifact binds SECOC-013', summary['finding_ids'] == ['SECOC-013'])
    check('tag-guess mean work factor is 2^27', summary['mean_blind_work_factor'] == 134217728)
    check('tag-guess preserves failure-freshness/no-lockout static facts', summary['firmware_static_properties']['failed_mac_advances_freshness'] is False and summary['firmware_static_properties']['recovered_per_source_failure_lockout'] is False)
    check('candidate tags advance deterministically', [row['tag28'] for row in rows] == ['0x0000100', '0x0000101', '0x0000102', '0x0000103'])
    check('candidate frames all preserve payload/freshness', all((parse_protected_frame(bytes.fromhex(row['frame'])).payload == parsed.payload and parse_protected_frame(bytes.fromhex(row['frame'])).transmitted_freshness == parsed.transmitted_freshness for row in rows)))
    check('tag range overflow rejected', rejects(lambda: build_tag_guesses(740, protected, TAG_MASK, 2)))
    check('unbounded artifact generation rejected', rejects(lambda: build_tag_guesses(740, protected, 0, 65537)))
    print('\n== CLI remains offline only ==')
    probe = REPO / 'exploit/followups/secoc_freshness_trials.py'
    source = probe.read_text(encoding='utf-8')
    check('freshness trial source has no Panda import', 'from panda import' not in source and 'import panda' not in source)
    check('freshness trial source has no execute flag', '--execute' not in source)
    cli = subprocess.run([sys.executable, str(probe), 'reset-replay', '--sync-frame', sync.hex(), '--protected', f'0x2e4:{protected.hex()}'], cwd=REPO, capture_output=True, text=True, check=False)
    check('reset-replay CLI emits offline plan', cli.returncode == 0 and '"operation": "reset_window_replay"' in cli.stdout and ('"can_transmit_implemented": false' in cli.stdout))
    alias_cli = subprocess.run([sys.executable, str(probe), 'fd-suffix-alias', '--base32', base32.hex(), '--suffix', (b'\xaa' * 16).hex()], cwd=REPO, capture_output=True, text=True, check=False)
    check('FD alias CLI emits offline SECOC-014 plan', alias_cli.returncode == 0 and '"SECOC-014"' in alias_cli.stdout and ('"physical_dlc": 48' in alias_cli.stdout))
    with tempfile.TemporaryDirectory() as directory:
        candidates = Path(directory) / 'guesses.ndjson'
        guess_cli = subprocess.run([sys.executable, str(probe), 'tag-guesses', '--can-id', '0x2e4', '--frame', protected.hex(), '--start', '0x20', '--count', '3', '--candidates-output', str(candidates)], cwd=REPO, capture_output=True, text=True, check=False)
        check('tag CLI writes exactly bounded candidate rows', guess_cli.returncode == 0 and len(candidates.read_text().splitlines()) == 3)
_section_secoc_freshness_trials()
print()

print("== secoc fd sensor correlations ==")
def _section_secoc_fd_sensor_correlations():
    import json, os, struct
    ROOT = REPO_ROOT
    ART = ROOT / 'data/generated/techstream_v18/secoc_fd_sensor_correlations.json'
    FW = (ROOT / 'firmware/RH850_P1M-E_CodeFlash.bin').read_bytes()
    d = json.loads(ART.read_text())
    cs = {x['semantic']: x for x in d['correlations']}
    print('== promoted correlations ==')
    check('three promoted correlations', len(cs) == 3)
    check('rear wheel speeds remain unordered pair', cs['CAN rear wheel speeds (RR/RL pair)']['confidence'] == 'high_pair_low_individual_order' and cs['CAN rear wheel speeds (RR/RL pair)']['firmware_signals'] == [270, 273])
    check('SSAV high-confidence signal 276', cs['CAN Steering Angle Speed (SSAV)']['confidence'] == 'high' and cs['CAN Steering Angle Speed (SSAV)']['firmware_signals'] == [276] and (cs['CAN Steering Angle Speed (SSAV)']['unit'] == 'deg/s'))
    check('SP1 very-high-confidence signal 283', cs['CAN Vehicle Speed (SP1)']['confidence'] == 'very_high' and cs['CAN Vehicle Speed (SP1)']['firmware_signals'] == [283] and (cs['CAN Vehicle Speed (SP1)']['unit'] == 'km/h'))
    check('RR/RL individual ordering explicitly bounded', any(('270 versus 273' in x for x in d['bounded_unknowns'])))
    print('\n== Techstream family invariants ==')
    for region, r in d['techstream']['regions'].items():
        m = r['monitors']
        check(f'{region} RR name/unit/range', m['303']['name'] == 'CAN Vehicle Speed (Speed Sensor RR)' and m['303']['unit'] == 'km/h' and (m['303']['range_words_i32'][:4] == [0, 255, 0, 255]))
        check(f'{region} RL name/unit/range', m['304']['name'] == 'CAN Vehicle Speed (Speed Sensor RL)' and m['304']['unit'] == 'km/h' and (m['304']['range_words_i32'][:4] == [0, 255, 0, 255]))
        check(f'{region} SP1 30000 bound', m['305']['name'] == 'CAN Vehicle Speed (SP1)' and m['305']['unit'] == 'km/h' and (m['305']['range_words_i32'][3] == 30000))
        check(f'{region} SSAV signed16 deg/s', m['306']['name'] == 'CAN Steering Angle Speed (SSAV)' and m['306']['unit'] == 'deg/s' and (m['306']['range_words_i32'][:4] == [-32768, 32767, -32768, 32767]))
    print('\n== firmware joins ==')
    t = d['firmware']['transforms']
    check('SP1 raw clamp 30000', t['sp1_vehicle_speed']['raw_clamp'] == 30000)
    check('SP1 scale 0x147B/0x1000', t['sp1_vehicle_speed']['gain_numerator'] == 5243 and t['sp1_vehicle_speed']['gain_denominator'] == 4096)
    check('rear wheel pair common 0x931/0x100 transform', t['rear_wheel_speed_pair']['signals'] == [270, 273] and t['rear_wheel_speed_pair']['gain_numerator'] == 2353 and (t['rear_wheel_speed_pair']['gain_denominator'] == 256))
    check('SSAV distinct 0x3E77/0x100 transform', t['steering_angle_speed']['signal'] == 276 and t['steering_angle_speed']['gain_numerator'] == 15991 and (t['steering_angle_speed']['gain_denominator'] == 256))
    check('firmware contains BC484 raw-clamp constant', struct.unpack_from('<H', FW, 771216)[0] in (30000, 30000) or b'0u' in FW[771200:771360])
    tech = ROOT / 'software/Techstream/v18/unpacked/toyota/Toyota Diagnostics/Techstream'
    if os.environ.get('RH850_VERIFY_EXTERNAL') == '1' and tech.is_dir():
        import tools.techstream.extract_secoc_fd_sensor_correlations as mod
        check('artifact deterministically regenerates from pinned V18 tree', mod.build() == d)
    else:
        print('[SKIP] optional pinned Techstream V18 regeneration disabled or unavailable')
_section_secoc_fd_sensor_correlations()
print()

print(f"\n== RESULT: {passed} passed, {failed} failed ==")
raise SystemExit(1 if failed else 0)
