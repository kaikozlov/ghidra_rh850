#!/usr/bin/env python3
"""Build two CRC-valid exact-F33 stages for the normal-boot C7/B6 signer."""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))

from exploit.common.payload_package import package_shellcode  # noqa: E402
from exploit.common.ram_exec import TOYOTA_P1ME_PAYLOAD_BUILD_SECRET  # noqa: E402
from exploit.ephemeral_runtime import build_camry_f33_b6_persistent_signer as signer_build  # noqa: E402
from exploit.patcher.build_payload import (  # noqa: E402
    build_configured_payload,
    config_from_manifest,
    simulate_apply,
)
from tools.security.build_secoc_patch_manifest import crc32  # noqa: E402
from tools.targets.camry.builders import build_camry_f33_crypto_result_patch as stage5  # noqa: E402

SIGNER_BUILDER = ROOT / "exploit/ephemeral_runtime/build_camry_f33_b6_persistent_signer.py"
FIXED_BLOB_SOURCE = ROOT / "exploit/patcher/fixed_blob.c"
DEFAULT_OUT = ROOT / "build/out/f33-persistent-b6-signer"
FLASH_SIZE = 0x100000
CRC_FIXUP_VA = 0xFFDEC
CRC_END = 0xFFDF0
PERSISTENT_SEGMENTS = signer_build.PERSISTENT_SEGMENTS
HOOK_VA = 0x7A272
HOOK_BLOCK = 0x78000
HOOK_ORIGINAL = bytes.fromhex("80ffee1c")
STAGE5_REQUIRED = bytes.fromhex("e001")
STAGE5_REQUIRED_VA = 0x8F890
EXPECTED_F181_HEX = stage5.EXPECTED_F181_HEX
EXPECTED_BOOT_F181_HEX = stage5.EXPECTED_BOOT_F181_HEX


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def apply_uncovered_segments(image: bytes, *, expected: list[bytes], replacement: list[bytes],
                             crc_start: int, crc_end: int) -> bytes:
    if len(image) != FLASH_SIZE or len(expected) != len(PERSISTENT_SEGMENTS) or len(replacement) != len(expected):
        raise ValueError("uncovered fixed-segment geometry drift")
    result = bytearray(image)
    for before, after, (_, _, address, limit) in zip(expected, replacement, PERSISTENT_SEGMENTS, strict=True):
        if len(before) != len(after) or len(after) > limit - address:
            raise ValueError("uncovered fixed-segment size drift")
        if not (address + len(before) <= crc_start or address >= crc_end):
            raise ValueError("uncovered fixed segment overlaps application CRC range")
        if image[address:address + len(before)] != before:
            raise ValueError(f"uncovered fixed-segment preimage drift at 0x{address:X}")
        result[address:address + len(after)] = after
    return bytes(result)


def reconstruct_stage5() -> tuple[bytes, dict[str, Any]]:
    stock = stage5.STOCK_IMAGE.read_bytes()
    source, stage4_manifest = stage5.reconstruct_stage4(stock)
    manifest = stage5.build_stage5_manifest(source, stage4_manifest)
    image, fixup, residue = simulate_apply(source, config_from_manifest(manifest, mode="apply"))
    if sha256(image) != stage5.EXPECTED_FINAL_SHA256 or fixup != stage5.EXPECTED_STAGE5_FIXUP or residue != 0xFFFFFFFF:
        raise ValueError("reconstructed stage-5 image drift")
    return image, manifest


def _blob_assembly(expected: list[bytes], replacement: list[bytes]) -> str:
    rows = [".section .text.fixed_blob,\"ax\""]
    for index, blob in enumerate(expected):
        rows.extend((f".global _fixed_blob_expected{index}", f"_fixed_blob_expected{index}:"))
        for offset in range(0, len(blob), 16):
            rows.append("    .byte " + ",".join(f"0x{x:02x}" for x in blob[offset:offset + 16]))
    for index, blob in enumerate(replacement):
        rows.extend((f".global _fixed_blob_replacement{index}", f"_fixed_blob_replacement{index}:"))
        for offset in range(0, len(blob), 16):
            rows.append("    .byte " + ",".join(f"0x{x:02x}" for x in blob[offset:offset + 16]))
    return "\n".join(rows) + "\n"


def compile_fixed_blob_shellcode(*, docker_image: str, expected: list[bytes], replacement: list[bytes],
                                 source_fixup: int, write: bool, work: Path,
                                 stem: str) -> tuple[bytes, dict[str, Any]]:
    blob_source = work / f"{stem}-blob.S"
    blob_source.write_text(_blob_assembly(expected, replacement), encoding="utf-8")
    elf = work / f"{stem}.elf"
    raw = work / f"{stem}.bin"
    definitions = [
        f"-DFIXED_BLOB_SOURCE_FIXUP=0x{source_fixup:08X}u",
    ]
    for index, (before, after, (_, _, address, _)) in enumerate(
        zip(expected, replacement, PERSISTENT_SEGMENTS, strict=True)
    ):
        if len(before) != len(after):
            raise ValueError("fixed-blob expected/replacement size mismatch")
        definitions.extend((
            f"-DFIXED_BLOB_TARGET{index}=0x{address:X}u",
            f"-DFIXED_BLOB_SIZE{index}={len(before)}u",
        ))
    if write:
        definitions.append("-DFIXED_BLOB_WRITE=1")
    compile_cmd = [
        "v850-elf-gcc", "-mv850e3v5", "-mno-app-regs", "-fPIC", "-ffreestanding",
        "-fno-toplevel-reorder", "-fno-builtin", "-flto", "-Os", "-nostdlib",
        "-Wl,-Ttext=0xFEBF0000", "-Wl,-e,_exploit", "-Wl,--build-id=none",
        *definitions, "/src/exploit/patcher/fixed_blob.c", f"/out/{blob_source.name}",
        "-o", f"/out/{elf.name}",
    ]
    base = [
        "docker", "run", "--rm", "-v", f"{ROOT}:/src:ro", "-v", f"{work}:/out",
        "-w", "/src", docker_image,
    ]
    compiled = subprocess.run(base + compile_cmd, check=False, capture_output=True, text=True)
    if compiled.returncode != 0:
        raise ValueError(f"fixed-blob shellcode compile failed: {compiled.stderr.strip()}")
    subprocess.run(base + [
        "v850-elf-objcopy", "-O", "binary", "-j", ".text", f"/out/{elf.name}", f"/out/{raw.name}",
    ], check=True, capture_output=True, text=True)
    nm = subprocess.run(base + ["v850-elf-nm", "-n", f"/out/{elf.name}"], check=True, capture_output=True, text=True).stdout
    relocs = subprocess.run(base + ["v850-elf-readelf", "-r", f"/out/{elf.name}"], check=True, capture_output=True, text=True).stdout
    shellcode = raw.read_bytes()
    symbols: dict[str, int] = {}
    for line in nm.splitlines():
        parts = line.split()
        if len(parts) >= 3 and (parts[-1] == "_exploit" or parts[-1].startswith("_fixed_blob_")):
            symbols[parts[-1]] = int(parts[0], 16)
    if symbols.get("_exploit") != 0xFEBF0000:
        raise ValueError(f"fixed-blob shellcode entry drift: {symbols.get('_exploit')!r}")
    blob_offsets: dict[str, int] = {}
    for kind, blobs in (("expected", expected), ("replacement", replacement)):
        for index, blob in enumerate(blobs):
            symbol = f"_fixed_blob_{kind}{index}"
            blob_va = symbols.get(symbol)
            if blob_va is None:
                raise ValueError(f"fixed blob symbol missing: {symbol}")
            blob_off = blob_va - 0xFEBF0000
            if shellcode[blob_off:blob_off + len(blob)] != blob:
                raise ValueError(f"fixed blob was not preserved byte-exact: {symbol}")
            blob_offsets[symbol] = blob_off
    if "There are no relocations" not in relocs:
        raise ValueError("fixed-blob shellcode contains relocations")
    if len(shellcode) > 0xFF0:
        raise ValueError(f"fixed-blob shellcode exceeds authenticated region: {len(shellcode)}")
    return shellcode, {
        "sha256": sha256(shellcode), "size": len(shellcode),
        "entry": "0xFEBF0000", "blob_offsets": blob_offsets, "relocations": 0,
        "write": write,
        "source_fixup": f"0x{source_fixup:08X}",
    }


def make_stage7_manifest(stage6: bytes, stage6_fixup: int, hook: bytes,
                         inherited: dict[str, Any]) -> dict[str, Any]:
    if stage6[HOOK_VA:HOOK_VA + 4] != HOOK_ORIGINAL or len(hook) != 4:
        raise ValueError("stage-7 hook geometry/preimage drift")
    manifest = copy.deepcopy(inherited)
    source_sha = sha256(stage6)
    manifest["image"] = {
        "base": "0x0", "path": "CodeFlash.stage6-resident.bin",
        "sha256": source_sha, "size": len(stage6),
    }
    manifest["patch"] = {
        "address": f"0x{HOOK_VA:X}", "block_base": f"0x{HOOK_BLOCK:X}",
        "block_size": 0x8000, "original": HOOK_ORIGINAL.hex(),
        "replacement": hook.hex(), "preimage_verified": True,
    }
    crc = manifest["boot_crc"]
    crc.update({
        "stock_expected_fixup": f"0x{stage6_fixup:08X}",
        "stored_fixup": f"0x{stage6_fixup:08X}",
        "stock_prefix_crc": f"0x{crc32(stage6[:CRC_FIXUP_VA]):08X}",
        "stock_residue": "0xFFFFFFFF", "stock_region_valid": True,
        "live_policy": "require exact CRC-valid stage-6 resident image, then patch only displaced foreground JARL",
    })
    manifest["semantic_resolution"] = {
        "schema": "camry-f33-persistent-signer-hook-v1", "resolution": "unique", "candidate_count": 1,
        "program_sha256": source_sha,
        "function": {"entry": "0x0007a254", "name": "FUN_0007a254"},
        "patch": {
            "address": f"0x{HOOK_VA:08x}", "operation": "replace one stock JARL with signer wrapper JARL",
            "original": HOOK_ORIGINAL.hex(), "replacement": hook.hex(),
            "displaced_call_replayed_by_wrapper": "0x0007BF60",
        },
        "invariants": [
            "stage-6 source is CRC-valid and contains an inert signer blob",
            "one same-width JARL changes", "wrapper replays the displaced stock call",
            "no-control and every signer failure leave native B6 untouched",
        ],
    }
    manifest["safety"] = {"fail_closed": True, "requirements": [
        "exact stage-6 source SHA/fixup/residue", "exact four-byte displaced-call preimage",
        "NRTD/Park/stationary for programming", "stage-7 restore before stage-6 blob removal",
    ]}
    manifest["development_stage"] = {
        "name": "f33-persistent-b6-signer-hook-stage7", "source_image_sha256": source_sha,
        "source_fixup": f"0x{stage6_fixup:08X}",
    }
    return manifest


def build(out: Path, *, docker_image: str = "v850-gcc-scratch") -> dict[str, Any]:
    if shutil.which("docker") is None:
        raise ValueError("Docker is required")
    out.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="camry-f33-persistent-patch-") as td:
        work = Path(td)
        signer_out = work / "signer"
        subprocess.run([
            sys.executable, str(SIGNER_BUILDER), "--docker-image", docker_image,
            "--output-dir", str(signer_out),
        ], cwd=ROOT, check=True, capture_output=True, text=True)
        signer_segments = [
            (signer_out / f"camry_f33_b6_persistent_signer_{name}.bin").read_bytes()
            for name, _, _, _ in PERSISTENT_SEGMENTS
        ]
        hook = (signer_out / "camry_f33_b6_persistent_hook.bin").read_bytes()
        signer_meta = json.loads((signer_out / "camry_f33_b6_persistent_signer.json").read_text())

        stage5_image, inherited_manifest = reconstruct_stage5()
        erased_segments = [b"\xFF" * len(blob) for blob in signer_segments]
        for erased, (_, _, address, _) in zip(erased_segments, PERSISTENT_SEGMENTS, strict=True):
            if stage5_image[address:address + len(erased)] != erased:
                raise ValueError(f"stage-5 persistent tail is not erased at 0x{address:08X}")
        if stage5_image[STAGE5_REQUIRED_VA:STAGE5_REQUIRED_VA + 2] != STAGE5_REQUIRED:
            raise ValueError("stage-5 ICU-S result patch missing")
        crc_start = int(inherited_manifest["boot_crc"]["start"], 0)
        crc_end = int(inherited_manifest["boot_crc"]["end"], 0)
        stage6 = apply_uncovered_segments(
            stage5_image, expected=erased_segments, replacement=signer_segments,
            crc_start=crc_start, crc_end=crc_end,
        )
        stage6_fixup = int.from_bytes(stage6[CRC_FIXUP_VA:CRC_FIXUP_VA + 4], "little")
        restored5 = apply_uncovered_segments(
            stage6, expected=signer_segments, replacement=erased_segments,
            crc_start=crc_start, crc_end=crc_end,
        )
        if restored5 != stage5_image or stage6_fixup != stage5.EXPECTED_STAGE5_FIXUP:
            raise ValueError("stage-6 offline removal does not restore exact stage 5")
        stage7_manifest = make_stage7_manifest(stage6, stage6_fixup, hook, inherited_manifest)
        stage7_cfg = config_from_manifest(stage7_manifest, mode="apply")
        stage7, stage7_fixup, stage7_residue = simulate_apply(stage6, stage7_cfg)
        if stage7_residue != 0xFFFFFFFF:
            raise ValueError("stage-7 CRC residue drift")

        image5 = out / "CodeFlash.stage5.bin"
        image6 = out / "CodeFlash.stage6-resident.bin"
        image7 = out / "CodeFlash.stage7-persistent-signer.bin"
        image5.write_bytes(stage5_image)
        image6.write_bytes(stage6)
        image7.write_bytes(stage7)
        for blob, (name, _, _, _) in zip(signer_segments, PERSISTENT_SEGMENTS, strict=True):
            (out / f"camry_f33_b6_persistent_signer_{name}.bin").write_bytes(blob)
        (out / "camry_f33_b6_persistent_hook.bin").write_bytes(hook)
        (out / "camry_f33_b6_persistent_signer.json").write_text(
            json.dumps(signer_meta, indent=2, sort_keys=True) + "\n", encoding="utf-8",
        )

        fixed_payloads: dict[str, Any] = {}
        for name, expected, replacement, write, source_fixup in (
            ("stage6-preflight", erased_segments, signer_segments, False, stage5.EXPECTED_STAGE5_FIXUP),
            ("stage6-apply", erased_segments, signer_segments, True, stage5.EXPECTED_STAGE5_FIXUP),
            ("stage6-restore-preflight", signer_segments, erased_segments, False, stage6_fixup),
            ("stage6-restore", signer_segments, erased_segments, True, stage6_fixup),
        ):
            shellcode, shell_meta = compile_fixed_blob_shellcode(
                docker_image=docker_image, expected=expected, replacement=replacement,
                source_fixup=source_fixup, write=write, work=work, stem=name,
            )
            payload = package_shellcode(shellcode, secret=TOYOTA_P1ME_PAYLOAD_BUILD_SECRET)
            shell_path = out / f"{name}-shellcode.bin"
            payload_path = out / f"{name}-payload.bin"
            shell_path.write_bytes(shellcode)
            payload_path.write_bytes(payload)
            fixed_payloads[name] = {
                "shellcode": {"path": shell_path.name, **shell_meta},
                "payload": {"path": payload_path.name, "sha256": sha256(payload), "size": len(payload)},
            }

        manifest_path = out / "stage7-hook-manifest.json"
        manifest_path.write_text(json.dumps(stage7_manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        template_path = stage5.materialize_template(out)
        preflight7 = build_configured_payload(
            image_path=image6, manifest_path=manifest_path, template_path=template_path,
            mode="validate-only", output_path=out / "stage7-preflight-payload.bin",
            payload_secret=TOYOTA_P1ME_PAYLOAD_BUILD_SECRET,
        )
        apply7 = build_configured_payload(
            image_path=image6, manifest_path=manifest_path, template_path=template_path,
            mode="apply", output_path=out / "stage7-apply-payload.bin",
            payload_secret=TOYOTA_P1ME_PAYLOAD_BUILD_SECRET, restore_dir=out / "stage7-restore",
        )

    result = {
        "schema": "camry-f33-persistent-b6-signer-patch-v1",
        "target": {
            "software_id": "8965F3307000", "f181_hex": EXPECTED_F181_HEX,
            "boot_f181_hex": EXPECTED_BOOT_F181_HEX,
        },
        "stage5_source": {"path": image5.name, "sha256": sha256(stage5_image), "fixup": f"0x{stage5.EXPECTED_STAGE5_FIXUP:08X}"},
        "stage6_resident": {
            "path": image6.name, "sha256": sha256(stage6), "fixup": f"0x{stage6_fixup:08X}",
            "segments": [
                {"address": f"0x{address:08X}", "size": len(blob), "sha256": sha256(blob)}
                for blob, (_, _, address, _) in zip(signer_segments, PERSISTENT_SEGMENTS, strict=True)
            ],
            "behavior_before_stage7": "inert; no stock control-flow reference enters the blob",
            "payloads": fixed_payloads,
        },
        "stage7_hook": {
            "path": image7.name, "sha256": sha256(stage7), "fixup": f"0x{stage7_fixup:08X}",
            "hook_address": f"0x{HOOK_VA:08X}", "hook_original": HOOK_ORIGINAL.hex(),
            "hook_replacement": hook.hex(), "manifest": manifest_path.name,
            "preflight_payload_sha256": preflight7["payload"]["sha256"],
            "apply_payload_sha256": apply7["payload"]["sha256"],
            "restore_artifact": str(Path("stage7-restore") / "restore.json"),
        },
        "signer": signer_meta,
        "ordering": {
            "install": ["stage6-preflight", "stage6-apply", "power-cycle", "stage7-preflight", "stage7-apply", "power-cycle"],
            "remove": ["stage7 restore", "power-cycle", "stage6-restore-preflight", "stage6-restore", "power-cycle"],
            "never_remove_blob_while_hook_active": True,
        },
        "boundaries": {
            "development_only": True, "stock_08a_modified": False,
            "stock_081_modified": False, "longitudinal_0ca_modified": False,
            "requires_programming_session_only_during_install_or_remove": True,
            "normal_boot_requires_programming_session": False,
        },
    }
    (out / "package.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return result


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT)
    ap.add_argument("--docker-image", default="v850-gcc-scratch")
    args = ap.parse_args()
    print(json.dumps(build(args.out, docker_image=args.docker_image), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
