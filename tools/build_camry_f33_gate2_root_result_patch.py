#!/usr/bin/env python3
"""Build the exact-F33 Gate-2 root-result development patch package.

Stage 3 starts from the live-proven CRC-valid stage-2 image and changes only the
boolean materialization at 0x8F930.  Stock `cmovne 1,r1,r26` turns the ICU-S
result byte at FEBE5564 into `r26 = (result != 0)`; the replacement
`cmovne 0,r0,r26` forces that one root boolean to zero without changing
instruction width or control flow.  With r26=0 the existing stage-1/stage-2 tail
edits are semantically inert and the whole FUN_0008F906 tail follows its native
verified-success behavior.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import shutil
import struct
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from exploit.patcher.build_payload import (
    build_authenticated_payload,
    build_configured_payload,
    inject_config,
    sha256_bytes,
    simulate_apply,
)
from exploit.patcher.patch_config import PatchConfigV1, config_from_manifest
from exploit.patcher.post_apply_verify import build_post_apply_validate_config
from tools import build_camry_f33_gate2_semantic_patch as stage2
from tools.build_secoc_patch_manifest import crc32

STOCK_IMAGE = stage2.STOCK_IMAGE
EXPECTED_STOCK_SHA256 = stage2.EXPECTED_STOCK_SHA256
EXPECTED_STAGE2_SHA256 = stage2.EXPECTED_FINAL_SHA256
EXPECTED_STAGE2_FIXUP = stage2.EXPECTED_STAGE2_FIXUP
EXPECTED_STAGE3_PREFIX = 0x13ADA3CC
EXPECTED_STAGE3_FIXUP = 0xEC525C33
EXPECTED_FINAL_SHA256 = "67f4aaa803f9f3df3e5b2bf31d2c8950ebbb3870fa3f5d439f585caae3a8313c"
EXPECTED_TEMPLATE_SHA256 = stage2.EXPECTED_TEMPLATE_SHA256

ROOT_RESULT_VA = 0x8F930
ROOT_RESULT_ORIGINAL = bytes.fromhex("e10f14d3")  # cmovne 1,r1,r26
ROOT_RESULT_REPLACEMENT = bytes.fromhex("e00714d3")  # cmovne 0,r0,r26
PATCH_BLOCK_BASE = 0x88000
STAGE2_CALLBACK_VA = stage2.STAGE2_VA
STAGE2_CALLBACK_BYTES = stage2.STAGE2_REPLACEMENT
STAGE1_GATE_VA = stage2.STAGE1_VA
STAGE1_GATE_BYTES = stage2.STAGE1_REPLACEMENT
BOOT_SECRET_OFF = stage2.BOOT_SECRET_OFF
PAYLOAD_SECRET_OFF = stage2.PAYLOAD_SECRET_OFF
SECRET_LEN = stage2.SECRET_LEN
EXPECTED_F181_HEX = stage2.EXPECTED_F181_HEX
EXPECTED_BOOT_F181_HEX = stage2.EXPECTED_BOOT_F181_HEX
RAM_LOAD_ADDR = stage2.RAM_LOAD_ADDR


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _hex32(value: int) -> str:
    return f"0x{value:08X}"


def enc_cmov_imm(cc: int, imm5: int, r2: int, r3: int) -> bytes:
    """Encode RH850 CMOV cccc, imm5, reg2, reg3 (32-bit form)."""
    word0 = ((r2 & 0x1F) << 11) | (0x3F << 5) | (imm5 & 0x1F)
    word1 = ((r3 & 0x1F) << 11) | (0x18 << 5) | ((cc & 0xF) << 1)
    return struct.pack("<HH", word0, word1)


def reconstruct_stage2(stock: bytes) -> tuple[bytes, dict[str, Any]]:
    if sha256(stock) != EXPECTED_STOCK_SHA256:
        raise ValueError("exact F33 stock CodeFlash SHA-256 mismatch")
    stage1_image, stage1_manifest = stage2.reconstruct_stage1(stock)
    stage2_manifest = stage2.build_stage2_manifest(stage1_image, stage1_manifest)
    cfg = config_from_manifest(stage2_manifest, mode="apply")
    stage2_image, fixup, residue = simulate_apply(stage1_image, cfg)
    if sha256(stage2_image) != EXPECTED_STAGE2_SHA256:
        raise ValueError("stage-2 reconstructed image SHA-256 drift")
    if fixup != EXPECTED_STAGE2_FIXUP or residue != 0xFFFFFFFF:
        raise ValueError("stage-2 reconstructed CRC/fixup drift")
    if stage2_image[STAGE2_CALLBACK_VA:STAGE2_CALLBACK_VA + 2] != STAGE2_CALLBACK_BYTES:
        raise ValueError("stage-2 callback patch missing")
    if stage2_image[STAGE1_GATE_VA:STAGE1_GATE_VA + 2] != STAGE1_GATE_BYTES:
        raise ValueError("stage-1 final-gate patch missing")
    return stage2_image, stage2_manifest


def build_stage3_manifest(stage2_image: bytes, stage2_manifest: dict[str, Any]) -> dict[str, Any]:
    if enc_cmov_imm(0xA, 1, 1, 26) != ROOT_RESULT_ORIGINAL:
        raise ValueError("RH850 CMOV immediate encoder no longer reconstructs stock 8F930")
    if enc_cmov_imm(0xA, 0, 0, 26) != ROOT_RESULT_REPLACEMENT:
        raise ValueError("RH850 CMOV immediate forced-zero encoding drift")
    if stage2_image[ROOT_RESULT_VA:ROOT_RESULT_VA + 4] != ROOT_RESULT_ORIGINAL:
        raise ValueError("stage-3 root-result preimage drift")
    # Exact local dataflow: load FEBE5564, zero-test, materialize bool into r26.
    if stage2_image[0x8F92A:0x8F934] != bytes.fromhex("840f659de009e10f14d3"):
        raise ValueError("stage-3 root-result machine context drift")
    # Existing experimental tail must match the live-proven stage-2 source.
    if stage2_image[0x8F944:0x8F964] != bytes.fromhex(
        "003aa505003a1d30bfff86ff1d30e0019a0d1a38bfff78fb1d301a38bfffe6fb"
    ):
        raise ValueError("stage-3 downstream Gate-2 tail drift")

    manifest = copy.deepcopy(stage2_manifest)
    image_sha = sha256(stage2_image)
    manifest["image"] = {
        "base": "0x0",
        "path": "CodeFlash.gate2-stage2.bin",
        "sha256": image_sha,
        "size": len(stage2_image),
    }
    manifest["patch"] = {
        "address": f"0x{ROOT_RESULT_VA:X}",
        "block_base": f"0x{PATCH_BLOCK_BASE:X}",
        "block_size": 0x8000,
        "original": ROOT_RESULT_ORIGINAL.hex(),
        "preimage_verified": True,
        "replacement": ROOT_RESULT_REPLACEMENT.hex(),
    }

    crc = manifest["boot_crc"]
    start = int(crc["start"], 0)
    end = int(crc["end"], 0)
    fixup_va = int(crc["fixup_va"], 0)
    source_prefix = crc32(stage2_image[start:fixup_va])
    source_fixup = int.from_bytes(stage2_image[fixup_va:fixup_va + 4], "little")
    source_residue = crc32(stage2_image[start:end])
    candidate = bytearray(stage2_image)
    candidate[ROOT_RESULT_VA:ROOT_RESULT_VA + 4] = ROOT_RESULT_REPLACEMENT
    patched_prefix = crc32(candidate[start:fixup_va])
    patched_fixup = patched_prefix ^ 0xFFFFFFFF
    struct.pack_into("<I", candidate, fixup_va, patched_fixup)
    patched_residue = crc32(candidate[start:end])

    if source_fixup != EXPECTED_STAGE2_FIXUP or source_residue != 0xFFFFFFFF:
        raise ValueError("stage-3 source CRC is not the live-proven stage-2 CRC-valid image")
    if patched_prefix != EXPECTED_STAGE3_PREFIX:
        raise ValueError("stage-3 prefix CRC drift")
    if patched_fixup != EXPECTED_STAGE3_FIXUP or patched_residue != 0xFFFFFFFF:
        raise ValueError("stage-3 cumulative CRC repair drift")
    if sha256(bytes(candidate)) != EXPECTED_FINAL_SHA256:
        raise ValueError("stage-3 final image SHA-256 drift")

    crc.update({
        "stock_expected_fixup": _hex32(source_fixup),
        "stock_prefix_crc": _hex32(source_prefix),
        "stock_region_valid": True,
        "stock_residue": _hex32(source_residue),
        "stored_fixup": _hex32(source_fixup),
        "patched_prefix_crc_for_supplied_image": _hex32(patched_prefix),
        "patched_fixup_for_supplied_image": _hex32(patched_fixup),
        "patched_residue_for_supplied_image": _hex32(patched_residue),
        "live_policy": "recompute prefix CRC from live CodeFlash containing stages 1+2 after root-result target-block RMW; write complement at discovered fixup VA; require final residue 0xFFFFFFFF",
    })
    manifest["semantic_resolution"] = {
        "schema": "toyota-secoc-semantic-target-v3",
        "resolution": "unique",
        "candidate_count": 1,
        "program_sha256": image_sha,
        "function": {"entry": "0x0008f906", "name": "FUN_0008f906"},
        "verify_result_polarity": "FEBE5564 zero means ICU-S verify success; nonzero is failure/timeout normalized to true",
        "producer_chain": [
            "FUN_0008F676 passes FEBE5564 as result storage to FUN_00089C98",
            "FUN_00089C98 delegates command/result handling to FUN_00089646 and normalizes return/result to 0/1/2",
            "FUN_0008F906 loads FEBE5564 at 0x8F92A and materializes bool(result!=0) into r26 at 0x8F930",
        ],
        "patch": {
            "address": f"0x{ROOT_RESULT_VA:08x}",
            "operation": "force-root-secoc-result-boolean-zero",
            "original": ROOT_RESULT_ORIGINAL.hex(),
            "replacement": ROOT_RESULT_REPLACEMENT.hex(),
            "stock_instruction": "cmovne 1,r1,r26",
            "replacement_instruction": "cmovne 0,r0,r26",
            "instruction_width_preserved": True,
        },
        "native_success_equivalence": {
            "r26": 0,
            "freshness_callback": "FUN_0008F8D2 receives zero through the existing success-compatible argument path",
            "failure_arm": "0x8F966 FUN_0008F60E(id,0x200) is not taken",
            "success_bookkeeping": "FUN_0008F4D0(id,0) is taken",
            "pdu_delivery": "FUN_0008F546(id,0) is taken and continues through FUN_0008EB1C -> FUN_00090204 -> FUN_00081CA6",
            "cleanup": "existing state cleanup/return flow is unchanged",
        },
        "existing_experimental_tail": [
            {"address": "0x0008f948", "bytes": STAGE2_CALLBACK_BYTES.hex(), "effect_with_r26_zero": "same callback argument as stock success"},
            {"address": "0x0008f952", "bytes": STAGE1_GATE_BYTES.hex(), "effect_with_r26_zero": "same branch outcome as stock cmp r0,r26"},
        ],
        "invariants": [
            "stage-3-source-is-exact-live-proven-stage-2-crc-valid-image",
            "root-result-load-and-zero-test-bytes-match-exactly",
            "replacement-is-same-width-rh850-cmov-immediate-form",
            "r26-is-the-single-bool-used-by-callback-and-success/failure-tail",
            "native-success-callees-and-their-zero-arguments-remain-unchanged",
            "crc-repair-covers-all-three-persistent-development-edits",
        ],
    }
    manifest["safety"] = {
        "fail_closed": True,
        "requirements": [
            "exact stock F33 SHA-256 matches",
            "stage-2 source reconstructs through the pinned stage-1 and stage-2 manifests",
            "stage-2 source SHA/fixup/residue match the reboot-verified live image contract",
            "8F930 root-result preimage and neighboring load/compare bytes match exactly",
            "existing 8F948 and 8F952 development bytes match the live stage-2 source",
            "live patcher recomputes CRC over the cumulative image and requires final residue 0xFFFFFFFF",
            "programming-session operations are performed only in NRTD/Park/stationary state",
        ],
    }
    manifest["development_stage"] = {
        "name": "f33-gate2-root-result-stage3",
        "source_stage": "live-proven-stage2-callback-plus-final-gate-image",
        "source_image_sha256": EXPECTED_STAGE2_SHA256,
        "source_fixup": _hex32(EXPECTED_STAGE2_FIXUP),
        "final_image_sha256": EXPECTED_FINAL_SHA256,
        "final_prefix_crc": _hex32(EXPECTED_STAGE3_PREFIX),
        "final_fixup": _hex32(EXPECTED_STAGE3_FIXUP),
        "cumulative_patch_sites": [
            {"address": "0x8F930", "bytes": ROOT_RESULT_REPLACEMENT.hex()},
            {"address": "0x8F948", "bytes": STAGE2_CALLBACK_BYTES.hex()},
            {"address": "0x8F952", "bytes": STAGE1_GATE_BYTES.hex()},
        ],
        "consolidation_note": "after live admission proof, stages 1+2 can be restored to stock because r26=0 makes their outcomes redundant; stage 3 intentionally changes only one new site for the next discriminator",
    }
    return manifest


def materialize_template(out: Path) -> Path:
    path = stage2.materialize_template(out)
    meta = {
        "schema": "camry-f33-gate2-stage3-template-v1",
        "sha256": EXPECTED_TEMPLATE_SHA256,
        "source": "exploit/patcher/shellcode.c",
        "config_offset": 0xF70,
        "size": path.stat().st_size,
    }
    path.with_suffix(path.suffix + ".json").write_text(json.dumps(meta, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


def build_post_apply_payload(*, source_image: bytes, manifest: dict[str, Any], template: bytes, payload_secret: bytes, out: Path) -> dict[str, Any]:
    apply_cfg = config_from_manifest(manifest, mode="apply")
    final_image, expected_fixup, expected_residue = simulate_apply(source_image, apply_cfg)
    verify_cfg = PatchConfigV1.from_bytes(build_post_apply_validate_config(apply_cfg, final_image).to_bytes())
    shellcode = inject_config(template, verify_cfg)
    payload = build_authenticated_payload(shellcode, payload_secret, ram_load_addr=RAM_LOAD_ADDR)
    d = out / "post-apply"
    d.mkdir(parents=True, exist_ok=True)
    (d / "config-validate.bin").write_bytes(verify_cfg.to_bytes())
    (d / "shellcode-validate-only.bin").write_bytes(shellcode)
    (d / "payload-validate-only.bin").write_bytes(payload)
    start, end, fixup_va = apply_cfg.crc_start, apply_cfg.crc_end, apply_cfg.crc_fixup_va
    expected = {
        "patch_observed": int.from_bytes(final_image[ROOT_RESULT_VA:ROOT_RESULT_VA + 4], "little"),
        "fixup_stored": int.from_bytes(final_image[fixup_va:fixup_va + 4], "little"),
        "crc_prefix": crc32(final_image[start:fixup_va]),
        "crc_residue": crc32(final_image[start:end]),
    }
    meta = {
        "schema": "camry-f33-gate2-stage3-post-apply-v1",
        "final_image_sha256": sha256(final_image),
        "expected_fixup": _hex32(expected_fixup),
        "expected_residue": _hex32(expected_residue),
        "expected_preflight": {k: _hex32(v) for k, v in expected.items()},
        "config_sha256": sha256_bytes(verify_cfg.to_bytes()),
        "shellcode_sha256": sha256_bytes(shellcode),
        "payload_sha256": sha256_bytes(payload),
    }
    (d / "manifest.json").write_text(json.dumps(meta, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return meta


def build(out: Path, *, build_payloads: bool = True) -> dict[str, Any]:
    out.mkdir(parents=True, exist_ok=True)
    stock = STOCK_IMAGE.read_bytes()
    source, stage2_manifest = reconstruct_stage2(stock)
    source_path = out / "CodeFlash.gate2-stage2.bin"
    source_path.write_bytes(source)
    manifest = build_stage3_manifest(source, stage2_manifest)
    manifest_path = out / "secoc_patch_manifest_f33_root_result.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    result: dict[str, Any] = {
        "schema": "camry-f33-gate2-root-result-patch-package-v1",
        "source_image": {"path": source_path.name, "sha256": sha256(source), "size": len(source)},
        "manifest": {"path": manifest_path.name, "sha256": sha256(manifest_path.read_bytes())},
        "stage1": {"address": "0x8F952", "bytes": STAGE1_GATE_BYTES.hex()},
        "stage2": {"address": "0x8F948", "bytes": STAGE2_CALLBACK_BYTES.hex(), "fixup": _hex32(EXPECTED_STAGE2_FIXUP)},
        "stage3": {"address": "0x8F930", "bytes": ROOT_RESULT_REPLACEMENT.hex(), "fixup": _hex32(EXPECTED_STAGE3_FIXUP)},
        "final_image_sha256": EXPECTED_FINAL_SHA256,
        "expected_f181_hex": EXPECTED_F181_HEX,
        "expected_boot_f181_hex": EXPECTED_BOOT_F181_HEX,
        "payloads_built": build_payloads,
    }

    if build_payloads:
        template_path = materialize_template(out)
        template = template_path.read_bytes()
        payload_secret = stock[PAYLOAD_SECRET_OFF:PAYLOAD_SECRET_OFF + SECRET_LEN]
        if len(payload_secret) != SECRET_LEN:
            raise ValueError("payload-build secret range truncated")
        preflight_path = out / "payload-validate-only.bin"
        preflight_meta = build_configured_payload(
            image_path=source_path,
            manifest_path=manifest_path,
            template_path=template_path,
            mode="validate-only",
            output_path=preflight_path,
            payload_secret=payload_secret,
            software_id="8965F3307000",
            ram_load_addr=RAM_LOAD_ADDR,
        )
        apply_path = out / "payload-apply.bin"
        apply_meta = build_configured_payload(
            image_path=source_path,
            manifest_path=manifest_path,
            template_path=template_path,
            mode="apply",
            output_path=apply_path,
            payload_secret=payload_secret,
            restore_dir=out / "restore",
            software_id="8965F3307000",
            ram_load_addr=RAM_LOAD_ADDR,
        )
        post_meta = build_post_apply_payload(
            source_image=source,
            manifest=manifest,
            template=template,
            payload_secret=payload_secret,
            out=out,
        )
        result["template"] = {"path": template_path.name, "sha256": EXPECTED_TEMPLATE_SHA256}
        result["payloads"] = {
            "preflight": preflight_meta["payload"],
            "apply": apply_meta["payload"],
            "restore": apply_meta["restore_artifact"],
            "post_apply": post_meta,
        }
        result["security_access"] = {
            "source": "exact F33 CodeFlash source image",
            "offset": f"0x{BOOT_SECRET_OFF:X}",
            "length": SECRET_LEN,
            "secret_value_recorded": False,
        }

    package_path = out / "package.json"
    package_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return result


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--out", type=Path, default=ROOT / "build/out/f33-gate2-root-result")
    p.add_argument("--no-payloads", action="store_true")
    args = p.parse_args()
    result = build(args.out, build_payloads=not args.no_payloads)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
