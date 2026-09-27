#!/usr/bin/env python3
"""Verify the exact-F33 static command-5 runtime carrier and audited candidates.

Standalone section of the exact-F33 portable family; assertions are carried over verbatim.
"""
from __future__ import annotations

from tools import REPO_ROOT
def section_command5_runtime_carrier() -> int:
    """Verify the exact-F33 static command-5 runtime carrier and audited candidates."""
    import hashlib, json, struct, subprocess, sys, tempfile
    from pathlib import Path
    ROOT=REPO_ROOT
    ART=ROOT/'data/generated/camry_8965F3307000_command5_runtime_carrier.json'
    BUILD=ROOT/'tools/targets/camry/builders/build_camry_8965F3307000_command5_runtime_carrier.py'
    IMAGE=ROOT/'firmware/camry-8965F3307000/CodeFlash.bin'
    RUNTIME_BUILDER=ROOT/'exploit/ephemeral_runtime/build_camry_f33_command5_carrier.py'
    PROXY_AUDIT=ROOT/'exploit/ephemeral_runtime/audited_camry_f33_command5_proxy_build.json'
    CANARY_AUDIT=ROOT/'exploit/ephemeral_runtime/audited_camry_f33_runtime_canary_build.json'
    PROXY_BIN=ROOT/'exploit/ephemeral_runtime/audited/camry_f33_command5_proxy.bin'
    CANARY_BIN=ROOT/'exploit/ephemeral_runtime/audited/camry_f33_runtime_canary.bin'
    PROXY_SOURCE=ROOT/'exploit/ephemeral_runtime/corolla_hf_command5_proxy.c'
    CANARY_SOURCE=ROOT/'exploit/ephemeral_runtime/camry_f33_runtime_canary.c'
    p=f=0
    def sha(b:bytes)->str:return hashlib.sha256(b).hexdigest()
    def check(name:str,cond:object)->None:
     nonlocal p, f; ok=bool(cond); p+=int(ok); f+=int(not ok); print(f"[{'PASS' if ok else 'FAIL'}] {name}")
    a=json.loads(ART.read_text()); img=IMAGE.read_bytes(); pa=json.loads(PROXY_AUDIT.read_text()); ca=json.loads(CANARY_AUDIT.read_text())
    print('== deterministic target binding ==')
    check('exact image pinned',a['sources']['codeflash']['sha256']==sha(img)=='42dce8efc42f6ae31718e7713fa2d26bb9191b4a82439778aee4d7afded9b0e7')
    check('identity/route exact',a['identity']['application_records']==['8965F3307000','8A3113303100'] and a['identity']['route']=={'tx':'0x7A1','rx':'0x7A9','bus':1,'elm327_param':1,'uds_variant':'old','cpu_index':0})
    with tempfile.TemporaryDirectory(prefix='f33-runtime-') as td:
     out=Path(td)/'a.json'; r=subprocess.run([sys.executable,str(BUILD),'--out',str(out)],cwd=ROOT,capture_output=True,text=True)
     check('builder exits cleanly',r.returncode==0)
     check('builder reproduces artifact byte-exact',out.exists() and out.read_bytes()==ART.read_bytes())
    for name,row in a['sources']['raw_function_ranges'].items():
     off=int(row['address'],16); n=row['size']; check(f'{name} raw range hash',sha(img[off:off+n])==row['sha256'])
    print('\n== bootstrap / startup / scheduler ==')
    b=a['bootstrap_contract']; s=a['scheduler_transfer']
    check('bootstrap stays RAM-only old-stack',b['download_base']==b['callback_base']=='0xFEBF0000' and b['download_size']==0x1000 and b['verify_routine']=='0x10F0' and b['callback_routine']=='0xFF00' and b['did_0203']=='0000000000' and b['did_0201']==b['did_0202']=='00'*16)
    check('boot transition exact',s['boot_transition_calls']==['0x00000C9A','0x00000E54','0x00000F80','0x000010C6'] and s['boot_validity_check']=='0x0000119E')
    check('context/startup exact',s['application_context_init']=='0x000715B4' and s['startup_jarl_first']=='0x000637F6' and s['startup_jarl_after']=='0x0006384A' and s['startup_jarl_count']==21 and s['startup_final_init']=='0x000701EA')
    check('foreground exact',s['foreground_loop']=='0x00066062' and s['tick_poll']=={'address':'0xFFFFB111','bit':4,'clear_mask':'0xEF'} and s['foreground_tick_counter']=='0xFEBE39DB')
    check('foreground context wrappers exact',s['foreground_calls']==['0x00065442','0x00071378','0x00066FF2','0x00071398','0x000667E6','0x00071378','0x00066CF6','0x00071398'])
    print('\n== static-low versus verified-high carrier geometry ==')
    g=a['static_low_carrier_geometry']; h=a['verified_high_tail_carrier']; m=a['mailbox_geometry']
    check('historical low pocket stays exact but is explicitly disproved live',g['base']=='0xFEBF0000' and g['end_inclusive']=='0xFEBF0307' and g['end_exclusive']=='0xFEBF0308' and g['size']==776 and g['first_recovered_normalized_direct_or_simple_gp_reference']=='0xFEBF0308')
    check('low pocket region5 static MPU geometry remains exact',g['mpu_region_index']==5 and g['mpu_bounds']==['0xFEBEF400','0xFEBF33FC'] and g['ctx0_mpat']==g['ctx1_mpat']=='0x000000B8')
    check('high tail is live retained/executable exact 524-byte carrier',h['base']=='0xFEBFF9F0' and h['end_inclusive']=='0xFEBFFBFB' and h['end_exclusive']=='0xFEBFFBFC' and h['size']==524 and h['retained_sha256']=='89ffed31c24e746a57171e6f3e22f99d1e78d57b63bccb8778c7fe715d18800c' and h['live_exact_after_stock_startup'] and h['live_execution_proven'] and h['stock_application_reappeared'] and h['safety_tx_blocked_delta']==0)
    check('high tail region1 MPU geometry exact',h['mpu_region_index']==1 and h['mpu_bounds']==['0xFEBF7C00','0xFEBFFBFC'] and h['ctx0_mpat']=='0x000000B8' and h['ctx1_mpat']=='0x000000A8')
    check('historical mailbox exact 60-byte span',m['base']=='0xFEBFFB80' and m['end_inclusive']=='0xFEBFFBBB' and m['end_exclusive']=='0xFEBFFBBC' and m['size']==60 and m['normalized_direct_or_simple_gp_reference_count']==0)
    check('mailbox region1 ctx0 writable / ctx1 nonwrite',m['mpu_region_index']==1 and m['mpu_bounds']==['0xFEBF7C00','0xFEBFFBFC'] and m['ctx0_mpat']=='0x000000B8' and m['ctx1_mpat']=='0x000000A8' and 'ctx0' in m['intended_write_context'] and '0x71398' in m['intended_write_context'])
    words=struct.unpack_from('<64I',img,0x31688)
    check('raw MPU table exact region1/5', (words[2],words[3],words[10],words[11])==(0xFEBF7C00,0xFEBFFBFC,0xFEBEF400,0xFEBF33FC) and words[33]==0xB8 and words[49]==0xA8 and words[37]==words[53]==0xB8)
    print('\n== command5 route ==')
    c=a['command5_contract']
    check('record0 adapter/worker/callback exact',c['driver_record_table']=='0x00027DA4' and c['driver_record']==0 and c['adapter']=='0x00088DBC' and c['worker']=='0x00088EC0' and c['completion_callback']=='0x00089C4C')
    check('dispatcher/lower exact',c['dispatcher']=='0x00089440' and c['lower_engine']=='0x0008A720' and c['key_selector']==4 and c['fixed_input_length']==36 and c['output_length']==16)
    check('completion cells exact',c['done_flag']=='0xFEBF13BC' and c['status_flag']=='0xFEBF13BD' and c['serialized_with_command7'] is True)
    check('raw driver record exact',struct.unpack_from('<8I',img,0x27DA4)==(0xFFFF0000,0x89C4C,0,0,0,0x88DBC,0x88EC0,0x27DA0))
    print('\n== audited executable candidates ==')
    can=a['runtime_candidates']['inert_canary']; prox=a['runtime_candidates']['fixed_36_command5_proxy']
    check('canary exact audited build',can['size']==CANARY_BIN.stat().st_size==302 and can['headroom']==474 and can['sha256']==sha(CANARY_BIN.read_bytes())=='81c7a45487a5ae8647b3526567b884011dba0adad606fd345e34ec97137949be' and can['entry_offset']==can['relocations']==0 and can['command5_calls'] is False)
    check('proxy exact audited build',prox['size']==PROXY_BIN.stat().st_size==428 and prox['headroom']==348 and prox['sha256']==sha(PROXY_BIN.read_bytes())=='513dc3cc5edf992b401c6b88ab054b78073df2e634ca52c61a72bed90dff1c09' and prox['entry_offset']==prox['relocations']==0 and prox['input_length']==36 and prox['key_selector']==4)
    for label,audit,source,binary in [('proxy',pa,PROXY_SOURCE,PROXY_BIN),('canary',ca,CANARY_SOURCE,CANARY_BIN)]:
     check(f'{label} audit source bound',audit['source']['sha256']==sha(source.read_bytes()))
     check(f'{label} audit binary bound',audit['shellcode']['sha256']==sha(binary.read_bytes()) and audit['compile_contract']['entry_offset']==0 and audit['compile_contract']['relocations']==0)
    print(f'\nResults: {p} passed, {f} failed')
    return 1 if f else 0


if __name__ == "__main__":
    raise SystemExit(section_command5_runtime_carrier())
