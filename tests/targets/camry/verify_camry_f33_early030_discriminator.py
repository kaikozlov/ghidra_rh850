#!/usr/bin/env python3
from __future__ import annotations
import json, subprocess, sys, tempfile
from pathlib import Path
from tools import REPO_ROOT
ROOT=REPO_ROOT
from tsk.common.payload_package import inspect_payload
from tsk.common.ram_exec import TOYOTA_P1ME_PAYLOAD_BUILD_SECRET
BUILDER=ROOT/'tools/targets/camry/research/ram_runtime/bootstrap/build_camry_f33_early030_discriminator.py'
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
 check('resident fits retained high tail', len(rb) <= m['resident']['limit'] == 524)
 check('authenticated payload exact 4KiB', len(payload)==0x1000)
 ins=inspect_payload(payload,secret=TOYOTA_P1ME_PAYLOAD_BUILD_SECRET)
 check('authenticated payload CRC/CMAC/callback valid', ins.crc_residue==0xffffffff and ins.cmac_valid and ins.callback_address==0xFEBF0000)
 tele=m['early_030']['telemetry']; tele_addr=int(tele['address'],16); resident_base=int(m['resident']['base'],16)
 check('self-attestation is wholly outside executable resident', resident_base+len(rb) <= tele_addr and tele_addr+tele['size'] <= resident_base+m['resident']['limit'])
print(f'\nSummary: {passed} passed, {failed} failed')
raise SystemExit(1 if failed else 0)
