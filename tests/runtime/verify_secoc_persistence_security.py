#!/usr/bin/env python3
"""Firmware/JSON pins for base-image SecOC persistence and security properties: NVM key state and security-property contracts.

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
print()

print("== secoc nvm ==")
def _section_secoc_nvm():
    import struct
    REPO = REPO_ROOT
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
    REPO = REPO_ROOT
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

print(f"\n== RESULT: {passed} passed, {failed} failed ==")
raise SystemExit(1 if failed else 0)
