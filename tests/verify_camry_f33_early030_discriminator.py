#!/usr/bin/env python3
from __future__ import annotations
import json, subprocess, sys, tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from exploit.common.payload_package import inspect_payload
from exploit.common.ram_exec import TOYOTA_P1ME_PAYLOAD_BUILD_SECRET
SRC=ROOT/'exploit/ephemeral_runtime/camry_f33_early030_discriminator_resident.S'
BUILDER=ROOT/'exploit/ephemeral_runtime/build_camry_f33_early030_discriminator.py'
HOST=ROOT/'exploit/ephemeral_runtime/camry_f33_early030_bootstrap_probe.py'
SEED=ROOT/'ghidra/scripts/seed/SeedCamryF33TxFreshness.java'
passed=failed=0
def check(name,cond,detail=''):
 global passed,failed
 if cond:
  passed+=1; print('[PASS]',name,detail)
 else:
  failed+=1; print('[FAIL]',name,detail)
s=SRC.read_text()
check('exact insertion is startup18 -> early030 -> startup19', s.index('jarl32 startup_18, lp') < s.index('jarl32 early_030_once, lp') < s.index('jarl32 startup_19, lp'))
check('one-shot uses recovered native primitives', all(x in s for x in ('jarl32 tx_freshness, lp','jarl32 command5_sync, lp','jarl32 lower_pdu_tx, lp','mov 0x3000, r1')))
check('one-shot returns to stock startup/foreground', 'jarl32 app_startup_final_init, lp' in s and 'jarl32 stock_foreground, lp' in s)
check('no B6 steering path in discriminator', '0x0b6' not in s.lower())
h=HOST.read_text()
check('host requires healthy FRC and independent stale bridge', '_healthy_frc_drcc_baseline' in h and '_Process030Bridge' in h)
check('bridge uses separate process and SPI flock boundary', 'multiprocessing.get_context("spawn")' in h and 'transport": "separate-process-spi-flock"' in h)
check('main SPI receive path yields between polls', 'SPI_RECV_YIELD_SECONDS = 0.0015' in h and 'class _YieldingPandaTap' in h)
check('host classifies first non-replay 0x030 after trigger', '_poll_first_changed_030' in h and 'ms_after_trigger_send' in h)
check('invalid cadence preserves partial evidence instead of throwing it away', 'invalid_bridge_continuity' in h and 'validity_errors' in h)
check('Ghidra seed pins 0x903F6 callback body', '0x000903F6L' in SEED.read_text() and '0x00090429L' in SEED.read_text())
with tempfile.TemporaryDirectory(prefix='early030-test-') as td:
 p=subprocess.run([sys.executable,str(BUILDER),'--output-dir',td],cwd=ROOT,check=True,capture_output=True,text=True)
 m=json.loads(p.stdout)
 rb=(Path(td)/m['resident']['path']).read_bytes(); payload=(Path(td)/m['authenticated_payload']['path']).read_bytes()
 check('resident fits retained high tail with headroom', len(rb)==m['resident']['size']==432 and m['resident']['headroom']==92)
 check('authenticated payload exact 4KiB', len(payload)==0x1000)
 ins=inspect_payload(payload,secret=TOYOTA_P1ME_PAYLOAD_BUILD_SECRET)
 check('authenticated payload CRC/CMAC/callback valid', ins.crc_residue==0xffffffff and ins.cmac_valid and ins.callback_address==0xFEBF0000)
 e=m['early_030']
 check('exact early030 contract', e['freshness_callback']=='0x000903F6' and e['freshness_id']==3 and e['selector']==4 and e['lower_pdu_id']==0 and e['wire_can_id']=='0x030')
 mut=m['mutation_boundary']
 check('mutation boundary is one 0x030, no steering/flash', mut['can_transmit']==['one protected 0x030 before stock foreground'] and not mut['b6_transmit'] and not mut['steering_actuation'] and not mut['codeflash_write'])
print(f'\nSummary: {passed} passed, {failed} failed')
raise SystemExit(1 if failed else 0)
