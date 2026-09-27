#!/usr/bin/env python3
"""Raw-firmware keyless application-surface pins: event formatter, boot variant residuals, diagnostic transport, and PC surfaces.

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

print("== keyless application event formatter ==")
def _section_keyless_application_event_formatter():
    import hashlib, json, struct, subprocess, sys, tempfile
    from pathlib import Path
    ROOT = REPO_ROOT
    S = (ROOT / 'firmware/RH850_P1M-E_CodeFlash.bin').read_bytes()
    H = (ROOT / 'community/albinoelephant/raw-20260818/albinoelephant-corolla-2023.20260814-0023/dump_codeflash_00000000_00200000_20260814-025814.bin').read_bytes()[:1048576]
    F = (ROOT / 'community/spanconstant/raw-20260821/span-corolla-2025.20260821-1511/dump_codeflash_00000000_00200000_20260821-152033.bin').read_bytes()[:1048576]
    EVP = ROOT / 'data/generated/corolla_8965H1202000_keyless_event_formatter_decompiler_evidence.json'
    EV = json.loads(EVP.read_text())
    ARTP = ROOT / 'data/generated/corolla_8965H1202000_keyless_event_formatter.json'
    ART = json.loads(ARTP.read_text())
    BUILD = ROOT / 'tools/targets/corolla/builders/build_corolla_h_keyless_event_formatter.py'
    SC = {}
    for line in (ROOT / 'data/generated/decompilations.jsonl').read_text().splitlines():
        r = json.loads(line)
        if r.get('entry_addr'):
            SC[int(r['entry_addr'], 16)] = r
    HE = {int(x['entry'], 16): x for x in EV['functions']}

    def sha(b):
        return hashlib.sha256(b).hexdigest()

    def bounds(img, desc_base, count, event_base):
        rows = []
        for i in range(count):
            a = desc_base + i * 24
            rows.append((struct.unpack_from('<H', img, a + 20)[0], img[a + 22]))
        vals = []
        for i in range(64):
            a = event_base + i * 8
            eid = struct.unpack_from('<h', img, a)[0]
            mask = struct.unpack_from('<H', img, a + 2)[0]
            if not mask:
                continue
            selected = [ln for m, ln in rows if m & mask]
            vals.append((3 + sum((3 + ln for ln in selected)), eid, mask, len(selected), sum(selected)))
        return (rows, vals)
    print('== deterministic report regeneration ==')
    with tempfile.TemporaryDirectory() as td:
        out = Path(td) / 'event.json'
        r = subprocess.run([sys.executable, str(BUILD), '--out', str(out)], cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        check('event-formatter builder exits', r.returncode == 0, r.stdout[-500:] if r.returncode else '')
        check('event-formatter report regenerates exactly', r.returncode == 0 and out.read_bytes() == ARTP.read_bytes())
    check('three target-native role mappings are explicit', ART['role_closure_count'] == 3 and {(x['reference_entry'], x['target_entry']) for x in ART['role_closure']} == {('0x00054910', '0x00050038'), ('0x000549FA', '0x00050122'), ('0x00054A7E', '0x000501A6')})
    print('== target-native H evidence ==')
    check('six H functions are compacted', EV['function_count'] == 6 == len(HE))
    check('H image hash pinned', EV['image']['codeflash_sha256'] == sha(H))
    check('all H raw bodies validate', all((sha(H[a:a + x['body_size']]) == x['body_sha256'] for a, x in HE.items())))
    check('all H decompiler hashes validate', all((sha(x['decompiled_c'].encode()) == x['decompiled_c_sha256'] for x in HE.values())))
    inner_s = SC[346384]['decompiled_c']
    wrap_s = SC[346618]['decompiled_c']
    sib_s = SC[346750]['decompiled_c']
    worker_s = SC[577412]['decompiled_c']
    inner_h = HE[327736]['decompiled_c']
    wrap_h = HE[327970]['decompiled_c']
    sib_h = HE[328102]['decompiled_c']
    worker_h = HE[553860]['decompiled_c']
    helper_h = HE[331024]['decompiled_c']
    print('\n== unchecked formatter structure ==')
    for tag, c in [('Sienna', inner_s), ('Corolla H', inner_h)]:
        check(f'{tag} formatter advances output by descriptor length without capacity operand', 'iVar9 = iVar9 + 3 + (uint)*(byte *)(iVar1 + 0x16);' in c and 'param_4 & 0xffff' not in c)
    for tag, c in [('Sienna', wrap_s), ('Corolla H', wrap_h)]:
        check(f'{tag} wrapper can append both snapshot banks', c.count('param_1,param_2') >= 2 and c.count('param_3') >= 2)
        check(f'{tag} wrapper checks total against capacity only after formatter calls', c.rfind('param_4 & 0xffff') > c.rfind('param_1,param_2'))
    for tag, c in [('Sienna', sib_s), ('Corolla H', sib_h)]:
        check(f'{tag} sibling formatter has an in-loop capacity check', 'param_4 & 0xffff' in c and '+ uVar7 + 3' in c)
    print('\n== configured reachable output bounds ==')
    srows, svals = bounds(S, 173316, 75, 175376)
    hrows, hvals = bounds(H, 171804, 78, 173936)
    frows, fvals = bounds(F, 171804, 78, 173936)
    check('Sienna helper count is 75', '*param_1 = 0x4b;' in SC[349672]['decompiled_c'])
    check('H helper count is 78 and table is 0x29F1C', '*param_1 = 0x4e;' in helper_h and 'PTR_DAT_00029f1c' in helper_h)
    check('H/F descriptor tables are byte-identical', H[171804:171804 + 78 * 24] == F[171804:171804 + 78 * 24])
    check('H/F event maps are byte-identical', H[173936:174448] == F[173936:174448])
    check('Sienna reachable one-bank maximum is 207', max((x[0] for x in svals)) == 207, str(sorted(svals, reverse=True)[:1]))
    check('H reachable one-bank maximum is 202', max((x[0] for x in hvals)) == 202, str(sorted(hvals, reverse=True)[:1]))
    check('F reachable one-bank maximum is also 202', max((x[0] for x in fvals)) == 202)
    check('Sienna two-bank conservative maximum is 414', 2 * max((x[0] for x in svals)) == 414)
    check('H/F two-bank conservative maximum is 404', 2 * max((x[0] for x in hvals)) == 404 == 2 * max((x[0] for x in fvals)))
    print('\n== staging capacity and portability ==')
    check('Sienna AB worker resets staging capacity to 0x300', 'DAT_febf45d6 = 0x300;' in worker_s)
    check('H AB worker resets staging capacity to 0x300', '_DAT_febf45d6 = 0x300;' in worker_h)
    check('Sienna configured headroom is 354 bytes', 768 - 2 * max((x[0] for x in svals)) == 354)
    check('H/F configured headroom is 364 bytes', 768 - 2 * max((x[0] for x in hvals)) == 364)
    check('F carries H formatter/wrapper/worker bytes exactly', F[327736:327736 + 234] == H[327736:327736 + 234] and F[327970:327970 + 90] == H[327970:327970 + 90] and (F[553860:553860 + 364] == H[553860:553860 + 364]))
    check('tracked configurations stay below staging capacity', 414 < 768 and 404 < 768)
    check('generated report publishes exact S/H/F maxima', ART['bounds']['sienna']['conservative_two_bank_max'] == 414 and ART['bounds']['corolla_h']['conservative_two_bank_max'] == 404 and (ART['bounds']['corolla_f']['conservative_two_bank_max'] == 404))
    check('generated report preserves configuration-dependent safety boundary', ART['static_conclusion']['configuration_dependent_safety'] and (not ART['static_conclusion']['tracked_images_overflow']) and ('not a global static-attack absence claim' in ART['static_conclusion']['boundary']))
_section_keyless_application_event_formatter()
print()

print("== keyless boot variant residuals ==")
def _section_keyless_boot_variant_residuals():
    ROOT = REPO_ROOT
    S = (ROOT / 'firmware/RH850_P1M-E_CodeFlash.bin').read_bytes()
    H = (ROOT / 'community/albinoelephant/raw-20260818/albinoelephant-corolla-2023.20260814-0023/dump_codeflash_00000000_00200000_20260814-025814.bin').read_bytes()
    F = (ROOT / 'community/spanconstant/raw-20260821/span-corolla-2025.20260821-1511/dump_codeflash_00000000_00200000_20260821-152033.bin').read_bytes()
    check('Corolla H/F boot bytes are identical through 0xA003', H[:40964] == F[:40964])
    EXACT = [('warm reset', 432, 432, 66), ('EIC init', 6088, 6058, 1014), ('TAUJ0 init', 7200, 7170, 64), ('TAUJ1 init', 7264, 7234, 64), ('TAUJ sequencer', 7328, 7298, 72)]
    for name, sa, ha, size in EXACT:
        check(f'{name} body is byte-exact at residual placement', S[sa:sa + size] == H[ha:ha + size])
    check('default exception thunk target relinks 0x1E1E -> 0x1E02', S[48:60] == bytes.fromhex('1f00e0061e1e000000000000') and H[48:60] == bytes.fromhex('1f00e006021e000000000000'))
    check('old/new default-exception targets carry the same 12-byte stub', S[7710:7722] == H[7682:7694])
    check('cold-start TP immediate moves 0x869C -> 0x867C', S[504:510] == bytes.fromhex('25069c860000') and H[504:510] == bytes.fromhex('25067c860000'))
    for off in (510, 528, 546):
        check(f'cold-start PSW-family immediate at 0x{off:X} clears CU0', S[off:off + 6] == bytes.fromhex('2a0620800100') and H[off:off + 6] == bytes.fromhex('2a0620800000'))
    check('FPIPR changes from r10=0x10 to r0', S[1166:1176] == bytes.fromhex('20561000ea3f20081c00') and H[1166:1172] == bytes.fromhex('e03f20081c00'))
    check('H cold-start body is exactly 28 bytes shorter before dominant relocation', S[1668:1858] == H[1640:1830])
    check('CSIH TX base remaps by 0x2000', S[5672:5676] == bytes.fromhex('490840b0') and H[5644:5648] == bytes.fromhex('490800b0'))
    check('CSIH init saves two bytes with movhi FFD8', H[5862:5866] == bytes.fromhex('40f6d8ff'))
    check('-0x1E island closes with one zero pad before dominant -0x1C resumes', H[7382:7384] == b'\x00\x00' and S[7410:7412] != b'\x00\x00')
    for name, sa, ha in (('runtime init', 4920, 4892), ('CSIH TX', 5670, 5642), ('CSIH RX', 5788, 5760), ('CSIH init', 5874, 5846), ('EIC mask helper', 7102, 7072), ('timer trampoline', 7400, 7370), ('TAUJ ISR', 7748, 7720), ('RAM table copier', 13796, 13768), ('EIC helper A', 15006, 14978), ('EIC helper B', 15034, 15006)):
        check(f'{name} retains expected instruction-family prologue', S[sa:sa + 4] == H[ha:ha + 4])
    check('RAM table copier source table relocates 0x8370 -> 0x8350 with identical 0x32C bytes', S[33648:34460] == H[33616:34428])
    check('0x9F00 handoff stays at the same VA and same fixed-state prefix', S[40704:40738] == H[40704:40738])
    check('0x9F00 handoff PSW clears CU0 on H/F', S[40738:40744] == bytes.fromhex('2a0620800100') and H[40738:40744] == bytes.fromhex('2a0620800000'))
    check('0x9F00 handoff TP moves 0x869C -> 0x867C', S[40784:40790] == bytes.fromhex('25069c860000') and H[40784:40790] == bytes.fromhex('25067c860000'))
    check('0x9F00 direct call relinks 0x148E -> 0x1472', S[40798:40802] == bytes.fromhex('bfff3075') and H[40798:40802] == bytes.fromhex('bfff1475'))
_section_keyless_boot_variant_residuals()
print()

print("== keyless application diagnostic transport ==")
def _section_keyless_application_diagnostic_transport():
    import json, struct
    ROOT = REPO_ROOT
    FW = (ROOT / 'firmware/RH850_P1M-E_CodeFlash.bin').read_bytes()
    CORP = ROOT / 'data/generated/decompilations.jsonl'
    WANTED = {499174, 499674, 590760, 590908, 592150, 592316, 598226, 598936}
    by = {}
    for line in CORP.read_text().splitlines():
        r = json.loads(line)
        if r.get('entry_addr'):
            a = int(r['entry_addr'], 16)
            if a in WANTED:
                by[a] = r

    def u16(a):
        return struct.unpack_from('<H', FW, a)[0]

    def u32(a):
        return struct.unpack_from('<I', FW, a)[0]
    print('== CanTp framing and PduR routing ==')
    check('all required canonical functions are in the decompiler corpus', set(by) == WANTED, str(sorted(WANTED - set(by))))
    check('CanTp first-frame protocol ceiling is 0xFFF', u16(142624) == 4095, hex(u16(142624)))
    tp_ids = [u16(142526 + i * 32 + 8) for i in range(3)]
    check('three diagnostic CanTp connections route PDU IDs 0x802/803/804', tp_ids == [2050, 2051, 2052], str([hex(x) for x in tp_ids]))
    callbacks = [u32(137356 + 4 * i) for i in range(6)]
    check('PduR callback vector is exact', callbacks == [590760, 590908, 592316, 591036, 592672, 592944], str([hex(x) for x in callbacks]))
    check('generic 0x90916 copy belongs to CopyTxData, not receive reassembly', 'FUN_00090916' in by[592316]['decompiled_c'] and callbacks[2] == 592316)
    print('\n== DCM receive allocation ==')
    slots = [(u16(155748 + i * 8), u32(155748 + i * 8 + 4)) for i in range(3)]
    check('DCM has three fixed 256-byte request buffers', slots == [(256, 4273886761), (256, 4273887017), (256, 4273887273)], str([(hex(a), hex(b)) for a, b in slots]))
    check('DCM local PDU IDs are exactly 2/3/4', [u16(155846 + i * 12) for i in range(3)] == [2, 3, 4])
    sor = by[590760]['decompiled_c']
    check('StartOfReception rejects total length above configured slot capacity', '(param_3 & 0xffff) <=' in sor and 'return 3;' in sor)
    check('StartOfReception recognizes exactly three slots', 'if (2 < uVar4)' in sor)
    print('\n== segmented-copy bounds ==')
    copyrx = by[590908]['decompiled_c']
    copy = by[598226]['decompiled_c']
    rem = by[598936]['decompiled_c']
    cf = by[499674]['decompiled_c']
    ff = by[499174]['decompiled_c']
    check('CopyRxData obtains remaining capacity before copying', 'FUN_00092398' in copyrx and 'FUN_000920d2' in copyrx and (copyrx.index('FUN_00092398') < copyrx.index('FUN_000920d2')))
    check('CopyRxData requires chunk length <= remaining capacity', '*(ushort *)(param_2 + 4) <= uVar4' in copyrx)
    check('remaining-capacity getter reads the per-slot remaining field', 'DAT_febe59d0' in rem)
    check('copy helper advances destination pointer one byte per copied byte', '*(undefined1 *)*piVar1 = uVar3;' in copy and '*piVar1 = *piVar1 + 1;' in copy)
    check('copy helper decrements remaining capacity by copied length', 'DAT_febe59d0' in copy and '= sVar2 - sVar4;' in copy)
    check('CanTp CF path clips payload chunk to remaining TP length', 'if (uVar6 < uVar9)' in cf and 'uStack_24 = uVar6;' in cf and ('uVar9 = uVar9 - uStack_24;' in cf))
    check('CanTp FF parser enforces 0x22D20 configured ceiling', 'DAT_00022d20 < uVar2' in ff)
    check('protocol max is larger than each DCM allocation, making DCM check material', 4095 > 256)
_section_keyless_application_diagnostic_transport()
print()

print("== keyless application pc surfaces ==")
def _section_keyless_application_pc_surfaces():
    import json
    import struct
    ROOT = REPO_ROOT
    CF = (ROOT / 'firmware/RH850_P1M-E_CodeFlash.bin').read_bytes()
    CORPUS = ROOT / 'data/generated/decompilations.jsonl'
    XCP_LO, XCP_HI = (4273961984, 4273994751)

    def u32(off: int) -> int:
        return struct.unpack_from('<I', CF, off)[0]
    funcs: dict[int, dict] = {}
    with CORPUS.open() as f:
        for line in f:
            rec = json.loads(line)
            if rec.get('record') == 'function' and rec.get('entry_addr'):
                funcs[int(rec['entry_addr'], 16)] = rec

    def refs(entry: int) -> set[tuple[int, str, int]]:
        out = set()
        for r in funcs[entry].get('data_references') or []:
            try:
                out.add((int(r['from_addr'], 16), str(r['ref_type']), int(r['to_addr'], 16)))
            except (KeyError, TypeError, ValueError):
                pass
        return out
    print('== exception-return and saved-PC surfaces ==')
    return_sites = {131346: bytes.fromhex('e0074801'), 412618: bytes.fromhex('e0074a01'), 459490: bytes.fromhex('e0074801'), 459718: bytes.fromhex('e0074801'), 459890: bytes.fromhex('e0074801'), 460062: bytes.fromhex('e0074801'), 461312: bytes.fromhex('e0074801'), 461744: bytes.fromhex('e0074801')}
    for off, op in return_sites.items():
        check(f'exception return opcode pinned at 0x{off:X}', CF[off:off + 4] == op)
    check('return census has seven EIRET and one FERET', list(return_sites.values()).count(bytes.fromhex('e0074801')) == 7 and list(return_sites.values()).count(bytes.fromhex('e0074a01')) == 1)
    check('common restore reloads EIPC from RAM frame', CF[459474:459494] == bytes.fromhex('0a650c6de16f2000ec072000ed0f2000266d2465100d0ef53fff0000df1923ff0100441ae0074801')[-20:])
    for name, entry, stack_imm in (('TAUJ0', 459552, bytes.fromhex('4036befe261e0008')), ('TAUJ1', 459722, bytes.fromhex('4036befe261e0010')), ('TAUJ2', 459894, bytes.fromhex('4036befe261e0018'))):
        body = CF[entry:entry + 172]
        check(f'{name} saves EIPC at frame+0x14', bytes.fromhex('e057400063571500') in body)
        check(f'{name} work-stack switch is fixed FEBE address', stack_imm in body)
    check('application foreground SP is fixed FEBE2000', CF[460104:460110] == bytes.fromhex('23060020befe'))
    check('fast-exception handler saves FEPC into its RAM frame', CF[412486:412498] == bytes.fromhex('e25740000a56040063570d00'))
    check('fast-exception handler restores FEPC before FERET', CF[412602:412622] == bytes.fromhex('23570d00ea17200023571100031e1400e0074a01'))
    check('known fixed application stack anchors lie below XCP window', all((v < XCP_LO for v in (4273866752, 4273868800, 4273870848, 4273872896))))
    check('canonical function entries do not lie in XCP window', not any((XCP_LO <= a <= XCP_HI for a in funcs)))
    print('\n== near-window callback FEBF7704 ==')
    cb = 4273960708
    check('callback cell is exactly 0x4FC below XCP lower bound', XCP_LO - cb == 1276)
    cb_refs = {(e, fr, typ, to) for e in funcs for fr, typ, to in refs(e) if to == cb}
    check('callback cell has exactly one canonical read and one write globally', cb_refs == {(470602, 470610, 'READ', cb), (470622, 470642, 'WRITE', cb)}, repr(sorted(cb_refs)))
    check('callback setter embeds both fixed targets', (470642, 'DATA', 480868) in refs(470622) and (470642, 'DATA', 481114) in refs(470622))
    check('callback consumer performs computed JARL after loading FEBF7704', CF[470602:470618] == bytes.fromhex('8007610040eebffe3def0577fdc760f9'))
    check('setter selects only fixed 75664/7575A targets', CF[470622:470646] == bytes.fromhex('21065a570700d832ca05210664560700405ebffe6b0f0577'))
    print('\n== MPU selector provenance ==')
    check('MPU context selector bytes are only 0/1', CF[202764:202772] == bytes.fromhex('0000000001000000'))
    check('MPU loader table base is fixed 0x31894', CF[411886:411900] == bytes.fromhex('06f09e00c6f22a0694180300caf1'))
    expected_selector_refs = {395434: 202770, 411604: 202767, 459496: 202768, 459528: 202767, 413736: 202769, 413802: 202769, 413868: 202771, 413934: 202771, 459552: 202764, 459722: 202765, 459894: 202766}
    mpu_callers = {e for e, r in funcs.items() if e != 411886 and 'FUN_000648ee(' in (r.get('decompiled_c') or '')}
    check('MPU loader has exactly the 11 recovered canonical callers', mpu_callers == set(expected_selector_refs), repr(sorted(mpu_callers)))
    for entry, target in expected_selector_refs.items():
        check(f'MPU caller 0x{entry:X} reads fixed selector byte 0x{target:X}', any((r[1] == 'READ' and r[2] == target for r in refs(entry))), repr(refs(entry)))
    check('all recovered MPU selector bytes decode to context 0 or 1', {CF[t] for t in expected_selector_refs.values()} <= {0, 1})
    print('\n== architectural alias geometry ==')
    PE1_BASE, SELF_BASE, SIZE = (4273864704, 4275961856, 131072)
    check('self LocalRAM view is same-offset +0x200000 alias', SELF_BASE - PE1_BASE == 2097152)
    check('XCP shadow aliases to FEDF7C00, not a lower FEBE control object', XCP_LO + (SELF_BASE - PE1_BASE) == 4276059136)
    for control in (4273866752, 4273868800, 4273870848, 4273872896, 4273960708):
        check(f'control object 0x{control:X} physical offset differs from XCP start', (control - PE1_BASE) % SIZE != (XCP_LO - PE1_BASE) % SIZE)
_section_keyless_application_pc_surfaces()
print()

print(f"\n== RESULT: {passed} passed, {failed} failed ==")
raise SystemExit(1 if failed else 0)
