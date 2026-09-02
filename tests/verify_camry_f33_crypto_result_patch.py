#!/usr/bin/env python3
from __future__ import annotations
import hashlib, importlib.util, json, struct, sys, tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
P=ROOT/'tools/build_camry_f33_crypto_result_patch.py'
s=importlib.util.spec_from_file_location('stage5',P); assert s and s.loader
b=importlib.util.module_from_spec(s); sys.modules[s.name]=b; s.loader.exec_module(b)
from exploit.patcher.patch_config import config_from_manifest
from exploit.patcher.build_payload import simulate_apply
from tools.build_secoc_patch_manifest import crc32

passed=failed=0
def check(n,c):
  global passed,failed
  ok=bool(c); passed+=ok; failed+=not ok; print(f"[{'PASS' if ok else 'FAIL'}] {n}")

stock=b.STOCK_IMAGE.read_bytes(); s4,m4=b.reconstruct_stage4(stock)
check('stage4 source sha exact', b.sha256(s4)==b.EXPECTED_STAGE4_SHA256)
check('stage4 source crc exact', crc32(s4[0x18000:0xFFDF0])==0xffffffff and struct.unpack_from('<I',s4,0xFFDEC)[0]==b.EXPECTED_STAGE4_FIXUP)
ctx=bytes.fromhex('fd372100233e1c00bfffeafde051a2151c306252fa05203e0202bfff14fe0ac8950d200e96ff20ce01015a0f0000bfffe4fc')
check('crypto result dispatch context exact', s4[0x8F884:0x8F8B6]==ctx)
check('actual ICU-S result compare exact', s4[0x8F890:0x8F892]==bytes.fromhex('e051'))
hw=int.from_bytes(s4[0x8F890:0x8F892],'little'); left=hw&31; neutral=((hw&2047)|(left<<11)).to_bytes(2,'little')
check('same-register CMP neutralizes to e001', neutral==bytes.fromhex('e001'))
with tempfile.TemporaryDirectory() as td:
  out=Path(td)/'s5'; pkg=b.build(out, build_payloads=True); man=json.loads((out/pkg['manifest']['path']).read_text()); cfg=config_from_manifest(man,mode='apply'); src=(out/pkg['source_image']['path']).read_bytes(); final,fix,res=simulate_apply(src,cfg)
  check('patch target exact', cfg.patch_va==0x8F890 and cfg.original==bytes.fromhex('e051') and cfg.replacement==bytes.fromhex('e001'))
  check('source is installed stage4 image identity', b.sha256(src)==b.EXPECTED_STAGE4_SHA256)
  check('final patch byte exact', final[0x8F890:0x8F892]==bytes.fromhex('e001'))
  check('stage4 freshness patch retained', final[0x8F7E6:0x8F7E8]==bytes.fromhex('00da'))
  check('stage3 root result patch retained', final[0x8F930:0x8F934]==bytes.fromhex('e00714d3'))
  check('stage2 callback patch retained', final[0x8F948:0x8F94A]==bytes.fromhex('003a'))
  check('stage1 tail patch retained', final[0x8F952:0x8F954]==bytes.fromhex('e001'))
  check('stage5 prefix exact', crc32(final[0x18000:0xFFDEC])==b.EXPECTED_STAGE5_PREFIX)
  check('stage5 fixup/residue exact', fix==b.EXPECTED_STAGE5_FIXUP and res==0xffffffff and struct.unpack_from('<I',final,0xFFDEC)[0]==b.EXPECTED_STAGE5_FIXUP)
  check('stage5 final sha exact', b.sha256(final)==b.EXPECTED_FINAL_SHA256)
  sem=man['semantic_resolution']['exact_control_flow']
  check('manifest identifies pre-8F906 ordinary failure', 'FUN_0008F906 is not called' in sem['ordinary_failure'])
  check('preflight payload pinned', pkg['payloads']['preflight']['sha256']=='274eb7eaea0e41c77a8f3d1fabfe82a0fffc8a0c085be7957790f93147483f53')
  check('apply payload pinned', pkg['payloads']['apply']['sha256']=='a5d9b3eaf8670160c371fa2756d65db73d8ad3f1644313c277ac52e5f4091917')
  check('post payload pinned', pkg['payloads']['post_apply']['payload_sha256']=='98c6042021de65e6a0da8038e6198de5caa0764a5725a8fd0c0a0e66a12bed85')
  r=json.loads((out/'restore/restore.json').read_text())
  check('restore reverses stage5 only', r['restore_config']['expected_live_preimage']=='e001' and r['restore_config']['replacement']=='e051')
  check('restore returns stage4 CRC', r['validation']['restore_simulated_fixup']=='0x8FD65A07' and r['validation']['restore_simulated_residue']=='0xFFFFFFFF')
  check('no standalone secrets', not any('secret' in p.name.lower() for p in out.rglob('*')))
print(f'Results: {passed} passed, {failed} failed')
raise SystemExit(1 if failed else 0)
