#!/usr/bin/env python3
"""Reproduce tracked T-0035 FACI evidence from the pinned external CUW."""
from __future__ import annotations
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from tools.techstream.analyze_t0035_faci_backend import (  # noqa:E402
    PAYLOAD_BUILD_ROOT_OFFSET, build, decrypt_region, deobfuscate_16, parse_ini,
    parse_streams, stream_regions,
)

CUW=ROOT/'software/Techstream/cuw/T-0035-22.cuw'
REF=ROOT/'firmware/RH850_P1M-E_CodeFlash.bin'
TRACKED=ROOT/'data/generated/techstream_v18/t0035_faci_backend_evidence.json'
passed=failed=0
def check(name,cond,detail=''):
 global passed,failed
 ok=bool(cond);passed+=ok;failed+=not ok
 print(f"[{'PASS' if ok else 'FAIL'}][independent_external_artifact] {name}"+(f' ({detail})' if detail else ''))

check('pinned T-0035 CUW is present',CUW.is_file())
if not CUW.is_file():
 print(f'\n{passed} passed, {failed} failed'); raise SystemExit(1)
actual=build(CUW,REF)
tracked=json.loads(TRACKED.read_text())
check('external T-0035 extraction exactly reproduces tracked secret-free evidence',actual==tracked)
check('both plaintext erase payload CMACs validate',all(x['erase']['cmac_valid'] for x in actual['cpus']))

# Reproduce the persisted CPU11 application firmware byte-for-byte. The CUW
# plaintext carries a final 16-byte authentication trailer; firmware/ stores
# only the actual application payload mapped at 0x00018000.
ini=parse_ini(CUW.read_bytes())
streams=parse_streams(CUW.read_bytes())
build_root=REF.read_bytes()[PAYLOAD_BUILD_ROOT_OFFSET:PAYLOAD_BUILD_ROOT_OFFSET+16]
persisted=ROOT/'firmware/tundra-8965F3401200/Application.bin'
cpu11=ini['CPU11']
did201=deobfuscate_16(cpu11['SeedKey']); did202=deobfuscate_16(cpu11['Nonce'])
body_addr=int(ini['CPUImage11']['01_StartAddress'],16)
body_plain=None
for addr,ciphertext in stream_regions(streams[0]):
    if addr==body_addr:
        body_plain,cmac_ok=decrypt_region(ciphertext,build_root,did201,did202)
        check('persisted Tundra CPU11 source body CMAC validates',cmac_ok)
        break
check('persisted Tundra CPU11 application is reproduced byte-exact',
      body_plain is not None and persisted.is_file() and persisted.read_bytes()==body_plain[:-16])
expected_program_hashes={
 '8965F3401200':'f55822835a6e20340b58b3cea46ad52c29f4fcf5c0bffdbcb971b0069df63aa8',
 '8965F3402200':'3e031dfa78e0b89343594b07c1e4900b45bd9f4f8b64fceb7b60fe7899d2608a',
}
check('manufacturer program-function raw hashes are independently pinned',all(x['functions']['program_256b']['body_sha256']==expected_program_hashes[x['cid']] for x in actual['cpus']))
check('manufacturer shared FRDY/error/erase bodies are byte-identical across CPUs',
      len({x['functions']['frdy']['body_sha256'] for x in actual['cpus']})==1 and
      len({x['functions']['fstatr_error']['body_sha256'] for x in actual['cpus']})==1 and
      len({x['functions']['erase_block']['body_sha256'] for x in actual['cpus']})==1)
check('no secret values are persisted',actual['crypto_provenance']['secret_values_recorded'] is False and all(k not in json.dumps(actual).lower() for k in ('seedkey','nonce','derived_key')))
print(f'\n{passed} passed, {failed} failed')
raise SystemExit(1 if failed else 0)
