#!/usr/bin/env python3
"""Execute stock and patched F33 Gate-2 firmware at real CodeFlash addresses."""

from __future__ import annotations

import hashlib
import struct
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from exploit.patcher.build_payload import simulate_apply
from exploit.patcher.patch_config import config_from_manifest
from tools.security.build_secoc_patch_manifest import crc32
from tools.targets.camry.builders import (
    build_camry_f33_gate2_root_result_patch as builder,
)

SCENARIO = ROOT / "tests/fixtures/rh850/camry_f33_gate2_codeflash_sim.json"
CRC_START = 0x18000
CRC_FIXUP = 0xFFDEC
CRC_END = 0xFFDF0


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def run_image(directory: Path, name: str, image: bytes, expected: str) -> None:
    image_path = directory / f"{name}.bin"
    image_path.write_bytes(image)
    proc = subprocess.run(
        [
            str(ROOT / "tools/rh850"),
            "codeflash-sim",
            str(image_path),
            "--spec",
            str(SCENARIO),
            "--expect",
            expected,
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    output = proc.stdout + proc.stderr
    if proc.returncode != 0:
        raise AssertionError(f"{name} simulation failed\n{output}")
    if expected not in output or "codeflash-sim: PASS" not in output:
        raise AssertionError(f"{name} simulation omitted its behavioral result\n{output}")
    print(f"PASS {name}: {expected}")


def main() -> int:
    stock = builder.STOCK_IMAGE.read_bytes()
    if sha256(stock) != builder.EXPECTED_STOCK_SHA256:
        raise AssertionError("stock image identity drift")

    root_only = bytearray(stock)
    root_only[builder.ROOT_RESULT_VA:builder.ROOT_RESULT_VA + 4] = builder.ROOT_RESULT_REPLACEMENT
    root_only_fixup = crc32(bytes(root_only[CRC_START:CRC_FIXUP])) ^ 0xFFFFFFFF
    struct.pack_into("<I", root_only, CRC_FIXUP, root_only_fixup)
    root_only_image = bytes(root_only)
    if crc32(root_only_image[CRC_START:CRC_END]) != 0xFFFFFFFF:
        raise AssertionError("root-only image CRC repair failed")

    stage2, stage2_manifest = builder.reconstruct_stage2(stock)
    stage3_manifest = builder.build_stage3_manifest(stage2, stage2_manifest)
    stage3_config = config_from_manifest(stage3_manifest, mode="apply")
    stage3, _, stage3_residue = simulate_apply(stage2, stage3_config)
    if sha256(stage3) != builder.EXPECTED_FINAL_SHA256 or stage3_residue != 0xFFFFFFFF:
        raise AssertionError("stage-3 image construction drift")

    tmp_root = ROOT / "build/tmp"
    tmp_root.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="gate2-codeflash-sim-", dir=tmp_root) as td:
        directory = Path(td)
        run_image(
            directory,
            "stock",
            stock,
            "GATE2_RESULT=0x222 FRESHNESS_ARG=1 ROOT_BOOL=1",
        )
        run_image(
            directory,
            "root-only",
            root_only_image,
            "GATE2_RESULT=0x333 FRESHNESS_ARG=0 ROOT_BOOL=0",
        )
        run_image(
            directory,
            "stage2",
            stage2,
            "GATE2_RESULT=0x333 FRESHNESS_ARG=0 ROOT_BOOL=1",
        )
        run_image(
            directory,
            "stage3",
            stage3,
            "GATE2_RESULT=0x333 FRESHNESS_ARG=0 ROOT_BOOL=0",
        )

    print("PASS real-address Gate-2 CodeFlash differential")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
