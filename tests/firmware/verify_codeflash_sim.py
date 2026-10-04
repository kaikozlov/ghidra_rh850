#!/usr/bin/env python3
"""One gate for generic CodeFlash execution, F33 Gate-2 differential,
registered RAM canaries, and the dump-generated universal signer model."""

from __future__ import annotations

import hashlib
import json
import struct
import subprocess
import sys
import tempfile
from pathlib import Path

from exploit.ephemeral_runtime import build_tss3_request_signer as signer_builder
from exploit.patcher.build_payload import simulate_apply
from exploit.patcher.patch_config import config_from_manifest
from exploit.ram_runtime.target_profiles import supported_targets, target_spec
from tools import REPO_ROOT
from tools.security.build_secoc_patch_manifest import crc32
from tools.targets.camry.builders import (
    build_camry_f33_gate2_root_result_patch as gate2_builder,
)
from tools.targets.tss3.onboard_ram_signer import simulate_candidate

ROOT = REPO_ROOT

GATE2_SPEC = ROOT / "tests/fixtures/rh850/camry_f33_gate2_codeflash_sim.json"
F33_SPEC = ROOT / "tests/fixtures/rh850/camry_f33_runtime_canary_sim.json"
COROLLA_SPEC = ROOT / "tests/fixtures/rh850/corolla_hf_runtime_canary_sim.json"
CRC_START = 0x18000
CRC_FIXUP = 0xFFDEC
CRC_END = 0xFFDF0


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def run(command: list[str]) -> subprocess.CompletedProcess[str]:
    proc = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, check=False)
    if proc.returncode != 0:
        raise AssertionError(f"command failed: {command}\n{proc.stdout}{proc.stderr}")
    return proc


def simulate(image: Path, expected: str, *, spec: Path | None = None, load: str | None = None,
             entry: str | None = None, memory_region: str | None = None,
             script: tuple[str, ...] = ()) -> None:
    command = [str(ROOT / "tools/rh850"), "codeflash-sim", str(image), "--expect", expected]
    if spec is not None:
        command += ["--spec", str(spec)]
    if entry is not None:
        command += ["--entry", entry]
    if load is not None:
        command += ["--load", load]
    if memory_region is not None:
        command += ["--memory-region", memory_region]
    for gdb_command in script:
        command += ["-ex", gdb_command]
    output = run(command).stdout
    if expected not in output:
        raise AssertionError(f"simulation omitted {expected!r}\n{output}")


def check_generic(work: Path) -> None:
    """A synthetic resident against a synthetic image: no spec, no target knowledge."""
    source = work / "program.S"
    source.write_text(
        "    .section .text\n"
        "    .global _start\n"
        "_start:\n"
        "    ld.w 0x200[r0], r10\n"
        "    mov 0xfebf0100, r11\n"
        "    st.w r10, 0[r11]\n"
        "    jr _start\n"
    )
    rel_source = source.relative_to(ROOT)
    rel_object = (work / "program.o").relative_to(ROOT)
    run([
        str(ROOT / "tools/rh850"), "exec",
        "v850-elf-gcc", "-mv850e3v5", "-mno-app-regs", "-ffreestanding",
        "-fno-builtin", "-Os", "-nostdlib", "-Wa,-mv850e3v5,-mextension",
        "-c", str(rel_source), "-o", str(rel_object),
    ])
    run([
        str(ROOT / "tools/rh850"), "exec",
        "v850-elf-objcopy", "-O", "binary",
        str(rel_object), str((work / "program.bin").relative_to(ROOT)),
    ])

    image = bytearray(b"\xFF" * 0x60000)
    struct.pack_into("<I", image, 0x200, 0x13579BDF)
    image_path = work / "new-target-CodeFlash.bin"
    image_path.write_bytes(image)

    simulate(
        image_path,
        "GENERIC_RESULT=0x13579bdf",
        entry="0xFEBF0200",
        load=f"0xFEBF0200={work / 'program.bin'}",
        memory_region="0xFEBF0000,0x1000",
        script=(
            f"break *0x{0xFEBF0200 + (work / 'program.bin').stat().st_size - 2:X}",
            "run",
            'printf "GENERIC_RESULT=0x%x\\n", *(unsigned int *)0xFEBF0100',
        ),
    )
    print("PASS generic resident on synthetic image (spec-less + -ex script)")


def check_gate2(work: Path) -> None:
    """Stock, root-only, stage-2, and stage-3 Gate-2 images differ behaviorally."""
    stock = gate2_builder.STOCK_IMAGE.read_bytes()
    if sha256(stock) != gate2_builder.EXPECTED_STOCK_SHA256:
        raise AssertionError("stock image identity drift")

    root_only = bytearray(stock)
    root_only[gate2_builder.ROOT_RESULT_VA:gate2_builder.ROOT_RESULT_VA + 4] = (
        gate2_builder.ROOT_RESULT_REPLACEMENT
    )
    struct.pack_into("<I", root_only, CRC_FIXUP, crc32(bytes(root_only[CRC_START:CRC_FIXUP])) ^ 0xFFFFFFFF)
    if crc32(bytes(root_only[CRC_START:CRC_END])) != 0xFFFFFFFF:
        raise AssertionError("root-only image CRC repair failed")

    stage2, stage2_manifest = gate2_builder.reconstruct_stage2(stock)
    stage3_manifest = gate2_builder.build_stage3_manifest(stage2, stage2_manifest)
    stage3, _, stage3_residue = simulate_apply(stage2, config_from_manifest(stage3_manifest, mode="apply"))
    if sha256(stage3) != gate2_builder.EXPECTED_FINAL_SHA256 or stage3_residue != 0xFFFFFFFF:
        raise AssertionError("stage-3 image construction drift")

    for name, image, expected in (
        ("stock", stock, "GATE2_RESULT=0x222 FRESHNESS_ARG=1 ROOT_BOOL=1"),
        ("root-only", bytes(root_only), "GATE2_RESULT=0x333 FRESHNESS_ARG=0 ROOT_BOOL=0"),
        ("stage2", stage2, "GATE2_RESULT=0x333 FRESHNESS_ARG=0 ROOT_BOOL=1"),
        ("stage3", stage3, "GATE2_RESULT=0x333 FRESHNESS_ARG=0 ROOT_BOOL=0"),
    ):
        image_path = work / f"gate2-{name}.bin"
        image_path.write_bytes(image)
        simulate(image_path, expected, spec=GATE2_SPEC)
        print(f"PASS gate2 {name}: {expected}")


def check_built_resident(work: Path, *, builder: Path, binary_name: str, pocket: int,
                         spec: Path, images: tuple[Path, ...], expected: str) -> None:
    """Build the audited resident, bind it to its build metadata, execute it."""
    build_dir = work / binary_name
    run([sys.executable, str(builder), "--output-dir", str(build_dir)])
    resident = build_dir / f"{binary_name}.bin"
    metadata = json.loads((build_dir / f"{binary_name}.json").read_text(encoding="utf-8"))
    blob = resident.read_bytes()
    if metadata["compile_contract"]["candidate_base"] != "0xFEBF0000":
        raise AssertionError("resident base drift")
    if metadata["compile_contract"]["relocations"] != 0:
        raise AssertionError("resident contains relocations")
    if metadata["shellcode"] != {"headroom": pocket - len(blob), "sha256": sha256(blob), "size": len(blob)}:
        raise AssertionError("resident metadata does not bind the generated binary")

    for image in images:
        simulate(image, expected, spec=spec, load=f"0xFEBF0000={resident}")
    print(f"PASS {binary_name}: {expected} ({len(images)} image(s))")

def check_request_signer(work: Path) -> None:
    build_dir = work / "tss3-request-signer"
    metadata = signer_builder.build_request_signer(
        target="camry-8965F3307000", output_dir=build_dir,
    )
    staging = build_dir / metadata["staging"]["path"]

    for target in supported_targets():
        spec = target_spec(target)
        simulate_candidate(
            image_path=spec["image"],
            contract=spec["contract"],
            metadata=metadata,
            staging_path=staging,
            output_dir=work / "request-signer-sim" / target,
        )
        print(f"PASS universal request signer {target}")


def main() -> int:
    tmp_root = ROOT / "build/tmp"
    tmp_root.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="codeflash-sim-", dir=tmp_root) as td:
        work = Path(td)
        check_generic(work)
        check_gate2(work)
        check_built_resident(
            work,
            builder=ROOT / "exploit/ephemeral_runtime/build_camry_f33_command5_carrier.py",
            binary_name="camry_f33_runtime_canary",
            pocket=776,
            spec=F33_SPEC,
            images=(ROOT / "firmware/camry-8965F3307000/CodeFlash.bin",),
            expected=(
                "RAM_HEARTBEAT=0x45504844 TICK=1 FLAG=0x0 "
                "CONTEXT=0x43545831 STARTUP=0x53544152 "
                "FOREGROUND=0x46475231 STOCK_ZERO=0x0"
            ),
        )
        check_built_resident(
            work,
            builder=ROOT / "exploit/ephemeral_runtime/build_corolla_hf_command5_carrier.py",
            binary_name="corolla_hf_runtime_canary",
            pocket=464,
            spec=COROLLA_SPEC,
            images=(
                ROOT / "firmware/corolla-8965H1202000/CodeFlash.bin",
                ROOT / "firmware/corolla-8965F1208000/CodeFlash.bin",
            ),
            expected=(
                "COROLLA_RAM_HEARTBEAT=0x45504844 TICK=1 "
                "CONTEXT=0x43545848 STARTUP=0x53544152 FOREGROUND=0x46475248"
            ),
        )
        check_request_signer(work)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
