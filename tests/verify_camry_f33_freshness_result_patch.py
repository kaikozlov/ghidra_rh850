#!/usr/bin/env python3
from __future__ import annotations
import importlib.util, json, struct, sys, tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
P=ROOT/'tools/build_camry_f33_freshness_result_patch.py'
s=importlib.util.spec_from_file_location('stage4',P); assert s and s.loader
b=importlib.util.module_from_spec(s); sys.modules[s.name]=b; s.loader.exec_module(b)
from exploit.patcher.build_payload import simulate_apply
from exploit.patcher.patch_config import config_from_manifest
from tools.build_secoc_patch_manifest import crc32
passed=failed=0
def check(n,c):
 global passed,failed
 ok=bool(c); passed+=ok; failed+=not ok; print(f"[{'PASS' if ok else 'FAIL'}] {n}")
stock=b.STOCK_IMAGE.read_bytes(); s3,s3m=b.reconstruct_stage3(stock)
check('stage3 source sha exact', b.sha256(s3)==b.EXPECTED_STAGE3_SHA256)
check('stage3 source crc exact', crc32(s3[0x18000:0xFFDF0])==0xffffffff and struct.unpack_from('<I',s3,0xFFDEC)[0]==b.EXPECTED_STAGE3_FIXUP)
check('freshness result preimage exact', s3[0x8F7E6:0x8F7E8]==bytes.fromhex('0ad8'))
check('forced zero encoding exact via known instruction', s3[0x90C6E:0x90C70]==bytes.fromhex('00da'))
check('freshness dispatch context exact', s3[0x8F7E0:0x8F812]==bytes.fromhex('1400f8c760f90ad81b06deffba0d200ea5ff20ce00015a0f00001c30bfff9afdb51d1b06dcffea05fd371300bfffecfdb515'))
with tempfile.TemporaryDirectory() as td:
 out=Path(td)/'s4'; pkg=b.build(out,build_payloads=True); man=json.loads((out/pkg['manifest']['path']).read_text()); cfg=config_from_manifest(man,mode='apply'); src=(out/pkg['source_image']['path']).read_bytes(); final,fix,res=simulate_apply(src,cfg)
 check('patch target exact', cfg.patch_va==0x8F7E6 and cfg.original==bytes.fromhex('0ad8') and cfg.replacement==bytes.fromhex('00da'))
 check('final cumulative sites exact', final[0x8F7E6:0x8F7E8]==bytes.fromhex('00da') and final[0x8F930:0x8F934]==bytes.fromhex('e00714d3') and final[0x8F948:0x8F94A]==bytes.fromhex('003a') and final[0x8F952:0x8F954]==bytes.fromhex('e001'))
 check('stage4 prefix exact', crc32(final[0x18000:0xFFDEC])==b.EXPECTED_STAGE4_PREFIX)
 check('stage4 fixup residue exact', fix==b.EXPECTED_STAGE4_FIXUP and res==0xffffffff and struct.unpack_from('<I',final,0xFFDEC)[0]==b.EXPECTED_STAGE4_FIXUP)
 check('stage4 final sha exact', b.sha256(final)==b.EXPECTED_FINAL_SHA256)
 sem=man['semantic_resolution']; check('callback remains and result only overridden', sem['native_success_equivalence']['freshness_callback_still_runs'] is True and sem['patch']['address']=='0x0008f7e6')
 check('preflight payload pinned', pkg['payloads']['preflight']['sha256']=='b97e34ec7b796d4c525bccfa12abc3152ac1b1fc3f80baa96d54d69826cbef4f')
 check('apply payload pinned', pkg['payloads']['apply']['sha256']=='920631b8725b7520c8f04d895b4f76f9d5c1de87c8baa901678512ba2d59c4d7')
 check('post payload pinned', pkg['payloads']['post_apply']['payload_sha256']=='82f569c121215ad8dd7516af183067c81548a21c195c5f48c9d9923bfd41acdb')
 r=json.loads((out/'restore/restore.json').read_text()); check('restore reverses stage4 only', r['restore_config']['expected_live_preimage']=='00da' and r['restore_config']['replacement']=='0ad8' and r['validation']['target_bytes_restored'] is True)
 check('restore returns exact stage3 crc', r['validation']['restore_simulated_fixup']=='0xEC525C33' and r['validation']['restore_simulated_residue']=='0xFFFFFFFF')
 check('no standalone secrets', not any('secret' in p.name.lower() for p in out.rglob('*')))
print(f'Results: {passed} passed, {failed} failed'); raise SystemExit(1 if failed else 0)
