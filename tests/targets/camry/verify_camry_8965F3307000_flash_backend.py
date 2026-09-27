#!/usr/bin/env python3
"""Verify exact-F33 plus Toyota T-0035 FACI behavior used by the patch backend.

Standalone section of the exact-F33 portable family; assertions are carried over verbatim.
"""
from __future__ import annotations

from tools import REPO_ROOT
def section_flash_backend() -> int:
    """Verify exact-F33 plus Toyota T-0035 FACI behavior used by the patch backend."""
    import hashlib, json

    ROOT = REPO_ROOT
    IMAGE = ROOT / 'firmware/camry-8965F3307000/CodeFlash.bin'
    F33 = ROOT / 'data/generated/camry_8965F3307000_flash_backend_evidence.json'
    T0035 = ROOT / 'data/generated/techstream_v18/t0035_faci_backend_evidence.json'
    CUW = ROOT / 'software/Techstream/cuw/T-0035-22.cuw'

    passed=failed=0
    def check(name, cond, detail=''):
        nonlocal passed, failed
        ok=bool(cond); passed+=ok; failed+=not ok
        print(f"[{'PASS' if ok else 'FAIL'}][raw_bytes] {name}" + (f' ({detail})' if detail else ''))

    def funcs(obj):
        return {int(x['entry'],16):x for x in obj['functions']}

    image=IMAGE.read_bytes(); f33=json.loads(F33.read_text()); t=json.loads(T0035.read_text())

    print('== exact F33 boot flash-control evidence ==')
    check('F33 flash evidence is exact-image bound', f33['software_id']=='8965F3307000' and f33['image']['sha256']==hashlib.sha256(image).hexdigest())
    F=funcs(f33)
    for entry,row in F.items():
        size=row['body_size']; check(f'F33 function 0x{entry:X} raw body hash', hashlib.sha256(image[entry:entry+size]).hexdigest()==row['body_sha256'])
    check('F33 ready helper uses FSTATR bit15', '& 0x8000' in F[0x78BFA]['decompiled_c'])
    status=F[0x78C30]['decompiled_c']
    check('F33 status-clear helper uses FSTATR error bit and FASTAT command-lock family', all(x in status for x in ('& 0x4000','0xffa10010','0x10','0xffa20000,0x50')))
    forced=F[0x78CE6]['decompiled_c']
    check('F33 forced-stop helper emits B3 and waits on ready', '0xffa20000,0xb3' in forced and '0x8000,0x8000' in forced)
    program=F[0x78E2A]['decompiled_c']
    write='FUN_00078aec(0xffa20000,local_20[uVar5]);'; dbfull='if ((uVar2 & 0x400) != 0)'
    check('F33 native program routine checks DBFULL bit10 after each halfword write', write in program and dbfull in program and program.index(write)<program.index(dbfull))
    check('F33 native program routine uses E8 and terminal D0', '0xffa20000,0xe8' in program and '0xffa20000,0xd0' in program)
    check('F33 native final status mask remains 0x24068', '& 0x24068' in F[0x79026]['decompiled_c'])

    print('\n== exact Toyota T-0035 manufacturer evidence ==')
    CUW = ROOT / 'software/Techstream/cuw/T-0035-22.cuw'
    check('T-0035 artifact source is exact corpus member', t['source']['filename']=='T-0035-22.cuw' and t['source']['sha256']==hashlib.sha256(CUW.read_bytes()).hexdigest() and t['source']['size']==5725237==CUW.stat().st_size)
    check('T-0035 is exact P5-Unified EPS/Tundra 07A1 package', t['package']['contact_type']=='P5-Unified' and t['package']['diag_id']=='07A1' and t['package']['vehicle']=='TUNDRA')
    check('both manufacturer CPU erase payloads are 4KiB at FEBF0000 and CMAC-valid', len(t['cpus'])==2 and all(x['erase']['load_address']=='0xFEBF0000' and x['erase']['size']==0x1000 and x['erase']['cmac_valid'] for x in t['cpus']))
    check('manufacturer program semantics use post-write DBFULL bit10', '0x00000400 (DBFULL)' in t['recovered_faci_semantics']['program_sequence'])
    check('manufacturer error/command-lock families are exact', t['recovered_faci_semantics']['fstatr_error_mask']=='0x00007040' and t['recovered_faci_semantics']['command_lock_mask']=='FASTAT 0x10')
    check('manufacturer erase and P/E entry sequences are recovered', t['recovered_faci_semantics']['erase_sequence']=='FPSADDR=1; FSADDR; 0x20; D0' and 'FENTRYR=AA01' in t['recovered_faci_semantics']['pe_entry'] and 'FPROTR=5501' in t['recovered_faci_semantics']['pe_entry'])

    print(f'\n{passed} passed, {failed} failed')
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(section_flash_backend())
