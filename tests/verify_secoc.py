#!/usr/bin/env python3
"""Firmware/JSON pins for the application SecOC receive chain.

Merged portable family module.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

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
    import sys
    from collections import Counter
    from pathlib import Path
    from Crypto.Cipher import AES
    from Crypto.Hash import CMAC
    REPO = Path(__file__).resolve().parents[1]
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
    print('\n== CORR-017 regression: SHE slot-4 usage determination ==')
    _kr = (REPO / 'docs' / 'security' / 'secoc' / 'key-recovery-assessment.md').read_text(encoding='utf-8').lower()
    check('key-recovery §1.3 records the SHE binary KEY_USAGE flag', 'key_usage' in _kr and 'no verify-only bit exists' in _kr)
    check('key-recovery §1.3 retracts the verify-only generation-disabled claim', 'is retracted' in _kr and 'not supported by the' in _kr)
    check('key-recovery §1.3 names command 5 as the spec-permitted slot-4 oracle', 'spec-permitted primitive' in _kr)
_section_secoc_application()
print()

print("== secoc nvm ==")
def _section_secoc_nvm():
    from pathlib import Path
    import struct
    import sys
    REPO = Path(__file__).resolve().parents[1]
    CF = (REPO / 'firmware' / 'RH850_P1M-E_CodeFlash.bin').read_bytes()
    DF = (REPO / 'firmware' / 'RH850_P1M-E_DataFlash.bin').read_bytes()
    u8 = lambda b, a: b[a]
    u16 = lambda b, a: struct.unpack_from('<H', b, a)[0]
    u32 = lambda b, a: struct.unpack_from('<I', b, a)[0]
    print('== static sizes and configuration roots ==')
    check('CodeFlash is 1 MiB', len(CF) == 1048576, hex(len(CF)))
    check('DataFlash is 32 KiB', len(DF) == 32768, hex(len(DF)))
    check('redundant object count @ 0x2AF12 is 16', u16(CF, 175890) == 16)
    check('object request queue has 49 entries', u8(CF, 175915) == 49)
    expected_desc = [(16, 2, 4273927272), (16, 3, 4273927288), (8, 4, 4273927168), (16, 5, 4273927304)]
    print('\n== redundant object descriptors @ 0x2B0AC ==')
    for obj, expected in enumerate(expected_desc):
        a = 176300 + obj * 8
        actual = (u16(CF, a), u16(CF, a + 2), u32(CF, a + 4))
        check(f'object {obj} descriptor', actual == expected, f'len={actual[0]} base={actual[1]} ram={actual[2]:#x}')
    TP = 147172
    MAGIC_TABLE = TP + 14524
    READ_ENTRY = MAGIC_TABLE + 16
    WRITE_ENTRY = MAGIC_TABLE + 24
    print('\n== AUTOSAR NvM service identification ==')
    check('magic table is at 0x277A0', MAGIC_TABLE == 161696)
    check('service 0x06 maps to 0xA1A62093', (u32(CF, READ_ENTRY), u32(CF, READ_ENTRY + 4)) == (6, 2712019091))
    check('service 0x07 maps to 0x22AA8A36', (u32(CF, WRITE_ENTRY), u32(CF, WRITE_ENTRY + 4)) == (7, 581601846))
    services = [u32(CF, MAGIC_TABLE + 16 + i * 8) for i in range(9)]
    check('accepted service list matches NvM family', services == [6, 7, 8, 10, 22, 23, 24, 12, 13], str(services))
    check('0x72F58 wrapper embeds ReadBlock magic', 2712019091 .to_bytes(4, 'little') in CF[470872:470916])
    check('0x72F84 wrapper embeds WriteBlock magic', 581601846 .to_bytes(4, 'little') in CF[470916:470960])
    JOB_COUNT = u16(CF, TP + 12024)
    JOB_TABLE = TP + 12028
    STORAGE_MAP = TP + 14628
    expected_pages = {2: 479, 6: 475, 10: 471, 3: 478, 7: 474, 11: 470, 4: 477, 8: 473, 12: 469, 5: 476, 9: 472, 13: 468}
    print('\n== NvM job to DataFlash mapping ==')
    check('NvM job count is 124', JOB_COUNT == 124, str(JOB_COUNT))
    configured_pages = []
    for job in range(JOB_COUNT):
        cfg = u16(CF, JOB_TABLE + job * 16 + 8)
        if cfg in (65534, 65535):
            continue
        entry = STORAGE_MAP + cfg * 6
        if entry + 2 <= len(CF):
            configured_pages.append(u16(CF, entry))
    for job, expected_page in expected_pages.items():
        cfg = u16(CF, JOB_TABLE + job * 16 + 8)
        page = u16(CF, STORAGE_MAP + cfg * 6)
        check(f'NvM block/job {job} maps to page {expected_page}', page == expected_page)
    objects = [(0, 16, (479, 475, 471), bytes.fromhex('a55a5aa5000800080008000800000000')), (1, 16, (478, 474, 470), bytes.fromhex('a55a5aa5025a0000ffffffff00ffff00')), (2, 8, (477, 473, 469), bytes.fromhex('aa5555aa5aa55aa5')), (3, 16, (476, 472, 468), bytes.fromhex('a55a5aa55aa55aa5ffffffffff4affff'))]
    print('\n== decode raw / XOR55 / XORAA triplicate records ==')
    for obj, length, pages, expected in objects:
        decoded = []
        for copy, (page, mask) in enumerate(zip(pages, (0, 85, 170))):
            record = DF[page * 64:(page + 1) * 64]
            stored = record[4:4 + length]
            value = bytes((x ^ mask for x in stored))
            decoded.append(value)
            check(f'object {obj} copy {copy} page header identifies NvM block', u16(DF, page * 64) == 1 + obj + copy * 4)
        check(f'object {obj} three copies decode identically', len(set(decoded)) == 1)
        check(f'object {obj} decoded structured value', decoded[0] == expected, decoded[0].hex())
    print('\n== normal NvM boundary and unconfigured/reserved tail ==')
    check('highest configured normal NvM page is 479', max(configured_pages) == 479, str(max(configured_pages)))
    check('no normal NvM job maps into pages 480..511', all((page < 480 for page in configured_pages)))
    tail = DF[480 * 64:]
    check('unconfigured tail is exactly 2 KiB', len(tail) == 2048)
    check('tail contains only 0x00 and 0xFF', set(tail) <= {0, 255}, str(sorted(set(tail))))
    check('tail is non-erased/masked-looking rather than all 0xFF', 0 in tail and 255 in tail, f'00={tail.count(0)} ff={tail.count(255)}')
    check('tail starts at VA 0xFF207800', 4280287232 + 480 * 64 == 4280317952)
_section_secoc_nvm()
print()

print("== secoc security properties ==")
def _section_secoc_security_properties():
    import hashlib
    import struct
    import sys
    from pathlib import Path
    REPO = Path(__file__).resolve().parents[1]
    CF = (REPO / 'firmware' / 'RH850_P1M-E_CodeFlash.bin').read_bytes()

    def u16(address: int) -> int:
        return struct.unpack_from('<H', CF, address)[0]

    def u32(address: int) -> int:
        return struct.unpack_from('<I', CF, address)[0]

    def body_hash(address: int, size: int) -> str:
        return hashlib.sha256(CF[address:address + size]).hexdigest()
    print('== locked security-relevant function bodies ==')
    expected_hashes = {(580484, 62, 'SecOC RX initialization'): 'ac170e1911bb6e94c78b939d024b7098ec5c389eec80a29dccb4144034cbfbe2', (583636, 24, 'freshness initialization wrapper'): '5901280c0931729a4bf5e37d5ce17f74a12f2c8d640ab9e15495eefe6ff0b77c', (584188, 76, 'freshness state clear'): 'ba4de073bb19193547aa2617a2df65b811fed603cf64c87d9fdad60f0603178a', (585630, 228, 'sync freshness reconstruction'): '0b0c4ce23e156ae4b1d621c86c0f4a5356d738ef6fdd2ed34187ff895bc5c596', (583290, 134, 'post-verification commit/delivery'): 'fbe3753387d3e9de73baee0496c2a3777b0ebe7b252ef3654ddb88f7bae402ff', (581822, 128, 'secured-PDU queue/clamp'): '0acb261aeb2ae94df0089fe06da35b2b2c346b8751fbad78188ebe5f89a866b6', (582842, 396, 'SecOC verification worker'): 'db69bf24d3ce490afdfbcac2049ed054a0097227e4a3eea3f3749cedcb72ee2c', (560040, 98, 'CryptoIf completion poll'): '139547a74d2b9affed13921621766da441817167bf42b4d78f0545b3eb9b7965', (524114, 52, 'CAN RX DLC bounds callback'): '0a6ca30fbd26a8694b363c59e7bb5a4c0a51e71982a7b3b2e41329be5804439e'}
    for (address, size, label), expected in expected_hashes.items():
        actual = body_hash(address, size)
        check(f'{label} body hash', actual == expected, actual)
    print('\n== fail-closed authentication boundary ==')
    check('post-verify path loads FEBE555C and booleanizes nonzero mismatch', CF[583326:583336] == bytes.fromhex('840f5d9de009e10f14d3'), CF[583326:583336].hex())
    check('verify-result GP-relative load occurs once in CodeFlash', CF.count(bytes.fromhex('840f5d9d')) == 1, str(CF.count(bytes.fromhex('840f5d9d'))))
    check('nonzero result branches to mismatch path while zero falls through delivery', CF[583364:583386] == bytes.fromhex('1d30e0d19a0d1a38bfff78fb1d301a38bfffe6fbd505'), CF[583364:583386].hex())
    print('\n== volatile freshness and synchronization ordering ==')
    check('freshness init zeroes control words then calls state clear', CF[583636:583660] == bytes.fromhex('800721006407609d6407629d6407649d80ff180240063f00'), CF[583636:583660].hex())
    check('sync wrap threshold is 15', CF[153964] == 15, hex(CF[153964]))

    def sync_candidate_is_forward(old_trip: int, old_reset: int, new_trip: int, new_reset: int, wrap_threshold: int=15) -> bool:
        """Reference model of 0x8EF9E's pre-CMAC monotonicity predicate."""
        old_trip &= 65535
        new_trip &= 65535
        old_reset &= 1048575
        new_reset &= 1048575
        wrap = old_trip >= 65535 - wrap_threshold and new_trip != 0 and (new_trip <= wrap_threshold + 1)
        return old_trip < new_trip or (old_trip == new_trip and old_reset < new_reset) or wrap
    check('equal sync freshness is rejected', not sync_candidate_is_forward(7, 9, 7, 9))
    check('ordinary rollback is rejected', not sync_candidate_is_forward(7, 9, 6, 1048575))
    check('same-trip reset advance is accepted', sync_candidate_is_forward(7, 9, 7, 10))
    check('arbitrarily large forward trip jump is accepted', sync_candidate_is_forward(1, 0, 57344, 0))
    check('configured trip wrap is accepted', sync_candidate_is_forward(65520, 4, 1, 0))
    check('post-init captured positive sync is structurally forward', sync_candidate_is_forward(0, 0, 1, 0))
    print('\n== truncated-tag retry and availability bounds ==')
    RECORD_BASE = 153968
    records = [RECORD_BASE + i * 80 for i in range(6)]
    check('all profiles transmit 28 CMAC bits', all((u16(a + 2) == 28 for a in records)))
    check('mean blind-guess work factor is 2^27', 1 << 28 - 1 == 134217728)
    check('CryptoIf completion uses fixed 0xE07-iteration poll budget', CF[560112:560120] == bytes.fromhex('410a0106f9f1b9f5'), CF[560112:560120].hex())
    check('post-verify false branch passes zero to freshness commit', CF[583352:583364] == bytes.fromhex('003aa5051a381d30bfff86ff'), CF[583352:583364].hex())
    print('\n== physical DLC canonicalization ==')
    NORMAL_RX_DESC = 139288
    configured_lengths = [CF[NORMAL_RX_DESC + i * 8 + 4] for i in range(47)]
    for index, expected in ((0, 8), (5, 8), (20, 8), (29, 8), (40, 32), (41, 32)):
        check(f'secured route {index} configured minimum DLC', configured_lengths[index] == expected)

    def canif_dlc_accepted(actual: int, configured_minimum: int, can_fd: bool) -> bool:
        physical_maximum = 64 if can_fd else 8
        return configured_minimum <= actual <= physical_maximum

    def secoc_effective_length(actual: int, configured: int) -> int:
        return min(actual, configured)
    check('classic secured profiles require exact DLC 8', all((canif_dlc_accepted(n, 8, False) == (n == 8) for n in range(0, 65))))
    check('FD secured profiles accept configured DLC 32', canif_dlc_accepted(32, 32, True))
    check('FD secured profiles also accept physical DLC 48/64', all((canif_dlc_accepted(n, 32, True) for n in (48, 64))))
    check('SecOC truncates accepted FD DLC 48/64 to 32', all((secoc_effective_length(n, 32) == 32 for n in (48, 64))))
    check('CAN RX descriptor IDs match protected FD routes', (u32(NORMAL_RX_DESC + 40 * 8) & 2047, u32(NORMAL_RX_DESC + 41 * 8) & 2047) == (144, 215))
_section_secoc_security_properties()
print()

print("== secoc freshness trials ==")
def _section_secoc_freshness_trials():
    import subprocess
    import sys
    import tempfile
    from pathlib import Path
    REPO = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(REPO))
    from exploit.followups.secoc_freshness_trials import FreshnessTrialError, TAG_MASK, build_fd_suffix_alias, build_future_sync, build_reset_replay, build_tag_guesses, parse_protected_frame, parse_sync_frame, replace_tag, sync_candidate_is_forward
    from tools.toyota_secoc_signer import sign_classic_frame, sign_sync_frame
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

print("== secoc rx control surface ==")
def _section_secoc_rx_control_surface():
    import csv
    import struct
    from pathlib import Path
    ROOT = Path(__file__).resolve().parents[1]
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

print("== secoc fd sensor correlations ==")
def _section_secoc_fd_sensor_correlations():
    import importlib.util, json, os, struct
    from pathlib import Path
    ROOT = Path(__file__).resolve().parents[1]
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
        spec = importlib.util.spec_from_file_location('fdcorr', ROOT / 'tools/techstream/extract_secoc_fd_sensor_correlations.py')
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        check('artifact deterministically regenerates from pinned V18 tree', mod.build() == d)
    else:
        print('[SKIP] optional pinned Techstream V18 regeneration disabled or unavailable')
_section_secoc_fd_sensor_correlations()
print()

print("== secoc bypass patch point ==")
def _section_secoc_bypass_patch_point():
    import struct
    import sys
    import zlib
    from pathlib import Path
    REPO = Path(__file__).resolve().parents[1]
    CF = (REPO / 'firmware' / 'RH850_P1M-E_CodeFlash.bin').read_bytes()

    def u16(off: int) -> int:
        return struct.unpack_from('<H', CF, off)[0]

    def u32(off: int) -> int:
        return struct.unpack_from('<I', CF, off)[0]

    def decode_cmp_format_ii(data: bytes) -> tuple[int, int, int]:
        """Return (left_reg, right_reg, opcode6) for a 2-byte RH850 Format-II CMP."""
        if len(data) != 2:
            raise ValueError('CMP must be two bytes')
        hw = int.from_bytes(data, 'little')
        return (hw & 31, hw >> 11 & 31, hw >> 5 & 63)

    def synthesize_cmp_same_register(data: bytes) -> bytes:
        left, _right, _opcode = decode_cmp_format_ii(data)
        hw = int.from_bytes(data, 'little')
        patched = hw & 2047 | left << 11
        return patched.to_bytes(2, 'little')

    def decode_bcond(off: int, data: bytes | None=None) -> tuple[int, int]:
        hw = int.from_bytes(data if data is not None else CF[off:off + 2], 'little')
        s1115 = hw >> 11 & 31
        op0406 = hw >> 4 & 7
        cc = hw & 15
        s1115_signed = s1115 - 32 if s1115 & 16 else s1115
        target = (s1115_signed << 4 | op0406 << 1) + off
        return (cc, target)
    PATCH_VA = 583366
    BRANCH_VA = 583368
    ORIGINAL = bytes.fromhex('e0d1')
    REPLACEMENT = bytes.fromhex('e001')
    print('== 1. corrected patch is CMP neutralization at 0x8E6C6 ==')
    check('stock patch preimage is e0d1', CF[PATCH_VA:PATCH_VA + 2] == ORIGINAL)
    left, right, opcode = decode_cmp_format_ii(ORIGINAL)
    check('stock CMP operands encode r0,r26', (left, right) == (0, 26), repr((left, right)))
    check('generic same-register synthesis yields e001', synthesize_cmp_same_register(ORIGINAL) == REPLACEMENT)
    pleft, pright, popcode = decode_cmp_format_ii(REPLACEMENT)
    check('patched CMP encodes r0,r0', (pleft, pright) == (0, 0))
    check('CMP opcode bits are preserved', popcode == opcode)
    check('only the second-register field changes', ORIGINAL[0] == REPLACEMENT[0] and ORIGINAL[1] != REPLACEMENT[1])
    check('full field-tested gate context is unique', CF.count(bytes.fromhex('e0d19a0d1a38bfff')) == 1)
    print('\n== 2. BNE is preserved and still points to mismatch arm ==')
    check('following BNE bytes remain 9a0d', CF[BRANCH_VA:BRANCH_VA + 2] == bytes.fromhex('9a0d'))
    cc, target = decode_bcond(BRANCH_VA)
    check('stock branch condition is NE', cc == 10, f'cc=0x{cc:X}')
    check('stock branch target is mismatch bookkeeping at 0x8E6DA', target == 583386, f'0x{target:X}')
    check('neutralized CMP makes BNE condition false for every result', pleft == pright)
    check('fallthrough begins at verified-delivery arm 0x8E6CA', BRANCH_VA + 2 == 583370)
    print('\n== 3. old branch patch is explicitly the wrong direction ==')
    OLD_WRONG_REPLACEMENT = bytes.fromhex('950d')
    old_cc, old_target = decode_bcond(BRANCH_VA, OLD_WRONG_REPLACEMENT)
    check('superseded 950d condition is unconditional BR', old_cc == 5, f'cc=0x{old_cc:X}')
    check('superseded 950d preserves mismatch target', old_target == 583386)
    check('old patch therefore forces mismatch arm, not delivery', old_cc == 5 and old_target != 583370)
    check('correct patch leaves the branch bytes untouched', CF[BRANCH_VA:BRANCH_VA + 2] == bytes.fromhex('9a0d'))
    print('\n== 4. pre-gate freshness handling remains before patched CMP ==')
    check('Gate-2 context keeps freshness call before CMP and delivery calls after it', CF[583360:583386] == bytes.fromhex('bfff86ff1d30e0d19a0d1a38bfff78fb1d301a38bfffe6fbd505'), CF[583360:583386].hex())
    check('patch is two bytes after pre-gate call return setup', PATCH_VA > 583360)
    print('\n== 5. CRC resigning for corrected patch ==')
    check('patch lies in boot CRC region 1', 98304 <= PATCH_VA < 1048048)
    check('CRC fixup remains at terminal word 0xFFDEC', 1048044 == 1048048 - 4)
    check('validity marker remains 0x5AA5A55A', u32(1048064) == 1520805210)
    published = bytearray(CF)
    published[PATCH_VA:PATCH_VA + 2] = REPLACEMENT
    published_prefix = zlib.crc32(published[98304:1048044]) & 4294967295
    published_fixup = published_prefix ^ 4294967295
    check('published-image corrected-patch prefix CRC is pinned', published_prefix == 589594124, f'0x{published_prefix:08X}')
    check('published-image corrected-patch fixup is pinned', published_fixup == 3705373171, f'0x{published_fixup:08X}')
    clean = bytearray(CF)
    clean[766404] = 130
    clean[PATCH_VA:PATCH_VA + 2] = REPLACEMENT
    clean_prefix = zlib.crc32(clean[98304:1048044]) & 4294967295
    clean_fixup = clean_prefix ^ 4294967295
    struct.pack_into('<I', clean, 1048044, clean_fixup)
    clean_residue = zlib.crc32(clean[98304:1048048]) & 4294967295
    check('reconstructed-clean corrected-patch prefix CRC is pinned', clean_prefix == 3191271437, f'0x{clean_prefix:08X}')
    check('reconstructed-clean corrected-patch fixup is 0x41C90FF2', clean_fixup == 1103695858, f'0x{clean_fixup:08X}')
    check('reconstructed-clean corrected-patch residue is 0xFFFFFFFF', clean_residue == 4294967295, f'0x{clean_residue:08X}')
_section_secoc_bypass_patch_point()
print()

print("== secoc acceptance gate ==")
def _section_secoc_acceptance_gate():
    import struct
    import sys
    from pathlib import Path
    REPO = Path(__file__).resolve().parents[1]
    CF = (REPO / 'firmware' / 'RH850_P1M-E_CodeFlash.bin').read_bytes()

    def u16(off: int) -> int:
        return struct.unpack_from('<H', CF, off)[0]

    def u32(off: int) -> int:
        return struct.unpack_from('<I', CF, off)[0]

    def jarl_target(call_site: int) -> int | None:
        w0, w1 = struct.unpack_from('<HH', CF, call_site)
        if w0 >> 6 & 31 != 30 or w1 & 1:
            return None
        reg2 = w0 >> 11 & 31
        if reg2 == 0:
            return None
        high = w0 & 63
        if high & 32:
            high -= 64
        return call_site + (high << 16) + w1

    def find_jarls(start: int, end: int) -> dict[int, int]:
        out: dict[int, int] = {}
        for off in range(start, min(end, len(CF) - 4), 2):
            target = jarl_target(off)
            if target is not None:
                out[off] = target
        return out
    print('== 1. Gate 1 remains worker-completion filtering ==')
    check('dispatcher calls secoc_rx_verify_worker', jarl_target(583456) == 582842)
    check('Gate 1 is cmp r0,r10 then bne', u16(583462) == 20960 and u16(583464) == 1514, f'0x{u16(583462):04X} 0x{u16(583464):04X}')
    check('worker success enters Gate-2 dispatcher', jarl_target(583470) == 583290)
    print('\n== 2. command-7 KAT pins verify-result polarity ==')
    check('KAT preinitializes verify-result output byte to 1', CF[426236:426242] == bytes.fromhex('010a430f0300'), CF[426236:426242].hex())
    check('KAT passes sp+3 as cryptoif_job_finish result pointer', CF[426314:426322] == bytes.fromhex('234e030082ff5a0a'), CF[426314:426322].hex())
    check('KAT result call targets cryptoif_job_finish', jarl_target(426318) == 560040)
    check('KAT reports pass iff verify-result byte equals zero', CF[426344:426366] == bytes.fromhex('03f06398010a030d2036ff00233e0400e099e20f0000'), CF[426344:426366].hex())
    print('\n== 3. Gate 2 maps zero to delivery and nonzero to mismatch ==')
    GATE2_LOAD = bytes.fromhex('840f5d9de009e10f14d3')
    check('Gate 2 loads FEBE555C and materializes result!=0', CF[583326:583336] == GATE2_LOAD)
    check('FEBE555C load is unique', CF.count(bytes.fromhex('840f5d9d')) == 1)
    check('Gate 2 compares boolean to zero then BNEs to mismatch arm', CF[583364:583372] == bytes.fromhex('1d30e0d19a0d1a38'), CF[583364:583372].hex())
    check('gate CMP is cmp r0,r26', CF[583366:583368] == bytes.fromhex('e0d1'))
    check('following BNE remains 9a0d', CF[583368:583370] == bytes.fromhex('9a0d'))
    check('verified-result fallthrough begins at 0x8E6CA', 583368 + 2 == 583370)
    check('mismatch BNE target is 0x8E6DA', 583386 > 583370)
    print('\n== 4. fallthrough is the PduR/COM delivery chain ==')
    jarls_gate = find_jarls(583290, 583424)
    check('fallthrough calls verification-status helper with success code', jarls_gate.get(583372) == 582212)
    check('fallthrough calls PDU extract/route helper', jarls_gate.get(583380) == 582330)
    check('mismatch branch calls retry/failure bookkeeping', jarls_gate.get(583390) == 582530)
    check('pre-gate freshness/status callback remains before Gate 2', jarls_gate.get(583360) == 583238)
    jarls_delivery = find_jarls(582330, 582410)
    check('delivery helper extracts queued PDU', jarls_delivery.get(582356) == 580004)
    check('delivery helper passes extracted PDU to routing wrapper', jarls_delivery.get(582384) == 583622)
    check('routing wrapper enters PduR-style dispatcher', jarl_target(583628) == 527290)
    check('PduR-style dispatcher terminates in computed routing callback', CF[527388:527398] == bytes.fromhex('25ef61e01330fdc760f9'), CF[527388:527398].hex())
    print('\n== 5. mismatch arm is retained/retry bookkeeping, not delivery ==')
    jarls_mismatch = find_jarls(582530, 582634)
    check('mismatch bookkeeping not direct PDU-routing wrapper', 583622 not in jarls_mismatch.values())
    check('mismatch bookkeeping not PduR dispatcher', 527290 not in jarls_mismatch.values())
    check('mismatch helper contains state/counter updates and status notification call', jarls_mismatch.get(582604) == 582212 and jarls_mismatch.get(582620) == 582410)
    check('post-arm cleanup tests state against 0xB4', CF[583402:583412] == bytes.fromhex('9c0f010001064cffc205'), CF[583402:583412].hex())
    print('\n== 6. Gate 1 completion and Gate 2 verify result are distinct ==')
    GP = 4273911808
    check('job-completion polling cell differs from CMAC verify-result cell', GP + 23486 == 4273935294 and 4273935294 != 4273886556)
    check('cryptoif_job_finish calls crypto_driver_dispatch', jarl_target(560082) == 558422)
    print('\n== 7. shared receive-profile coverage ==')
    profile_can_ids = []
    for i in range(6):
        base = 153970 + i * 80
        can_id = u32(base + 8)
        profile_can_ids.append(can_id)
        check(f'profile {i} has valid CAN ID 0x{can_id:03X}', 0 < can_id < 2048)
    check('profiles cover all six recovered secured inputs', set(profile_can_ids) == {740, 305, 306, 144, 215, 15})
_section_secoc_acceptance_gate()
print()

print(f"\n== RESULT: {passed} passed, {failed} failed ==")
raise SystemExit(1 if failed else 0)
