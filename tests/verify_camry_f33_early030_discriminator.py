#!/usr/bin/env python3
from __future__ import annotations
import json, subprocess, sys, tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from exploit.common.payload_package import inspect_payload
from exploit.common.ram_exec import TOYOTA_P1ME_PAYLOAD_BUILD_SECRET
BUILDER=ROOT/'exploit/ephemeral_runtime/build_camry_f33_early030_discriminator.py'
passed=failed=0
def check(name,cond,detail=''):
 global passed,failed
 if cond:
  passed+=1; print('[PASS]',name,detail)
 else:
  failed+=1; print('[FAIL]',name,detail)
with tempfile.TemporaryDirectory(prefix='early030-test-') as td:
 p=subprocess.run([sys.executable,str(BUILDER),'--output-dir',td],cwd=ROOT,check=True,capture_output=True,text=True)
 m=json.loads(p.stdout)
 rb=(Path(td)/m['resident']['path']).read_bytes(); payload=(Path(td)/m['authenticated_payload']['path']).read_bytes()
 check('resident fits retained high tail with headroom', len(rb)==m['resident']['size']==488 and m['resident']['headroom']==36)
 check('authenticated payload exact 4KiB', len(payload)==0x1000)
 ins=inspect_payload(payload,secret=TOYOTA_P1ME_PAYLOAD_BUILD_SECRET)
 check('authenticated payload CRC/CMAC/callback valid', ins.crc_residue==0xffffffff and ins.cmac_valid and ins.callback_address==0xFEBF0000)
 e=m['early_030']
 check('exact early030 contract', e['freshness_callback']=='0x000903F6' and e['freshness_id']==3 and e['selector']==4 and e['lower_pdu_id']==0 and e['wire_can_id']=='0x030' and e['command5_pre_ei_completion_service']=='0x00088700' and e['command5_done_flag']=='0xFEBF13BC' and e['command5_status_flag']=='0xFEBF13BD')
 tele=e['telemetry']; tele_addr=int(tele['address'],16); resident_base=int(m['resident']['base'],16)
 check('self-attestation is wholly outside executable resident', tele['outside_resident'] is True and tele['size']==4 and resident_base+len(rb) <= tele_addr and tele_addr+tele['size'] <= resident_base+m['resident']['limit'])
 mut=m['mutation_boundary']
 check('mutation boundary is one 0x030, no steering/flash', mut['can_transmit']==['one protected 0x030 before stock foreground'] and not mut['b6_transmit'] and not mut['steering_actuation'] and not mut['codeflash_write'])
print(f'\nSummary: {passed} passed, {failed} failed')
raise SystemExit(1 if failed else 0)
