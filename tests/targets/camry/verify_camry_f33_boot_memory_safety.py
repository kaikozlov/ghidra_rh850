#!/usr/bin/env python3
"""Verify exact-Camry bootloader memory-safety findings and live primitives."""

from __future__ import annotations

import hashlib
import tempfile
from pathlib import Path
from typing import cast

from tools import REPO_ROOT
from tools.rh850_codeflash import run_elf
from tools.security.memory_safety_semantics import analyze
from tools.targets.camry.research import fuzz_camry_f33_dcm_handlers as dcm
from tools.targets.camry.research import fuzz_camry_f33_stateful_coverage as fuzz

IMAGE = REPO_ROOT / "firmware/camry-8965F3307000/CodeFlash.bin"
IMAGE_SHA256 = "42dce8efc42f6ae31718e7713fa2d26bb9191b4a82439778aee4d7afded9b0e7"
BOOT_GP = 0xFEBF9800
SOURCE = 0xFEBE7000
DESTINATION = 0xFEBE7100


def write_ram(image: bytearray, address: int, data: bytes) -> None:
    offset = address - dcm.RAM_BASE
    image[offset : offset + len(data)] = data


def execute_and_dump(
    elf: Path,
    work: Path,
    name: str,
    entry: int,
    image: bytes,
) -> bytes:
    initial = elf.parent / f"{name}-initial.bin"
    dumped = elf.parent / f"{name}-dump.bin"
    initial.write_bytes(image)
    marker = f"BOOT_MEMORY_SAFETY_{name.upper()}"
    run_elf(
        root=REPO_ROOT,
        elf_path=elf,
        stop=f"{dcm.SENTINEL:#x}",
        memory_regions=dcm.SIM_MEMORY_REGIONS,
        gdb_commands=(
            f"break *{dcm.SENTINEL:#x}",
            f"restore /out/{initial.name} binary {dcm.RAM_BASE:#x}",
            f"set $r4={BOOT_GP:#x}",
            f"set $r3={dcm.STACK_TOP:#x}",
            f"set $r31={dcm.SENTINEL:#x}",
            f"set $pc={entry:#x}",
            "continue",
            (
                f"dump binary memory /out/{dumped.name} "
                f"{dcm.RAM_BASE:#x} {dcm.RAM_BASE + dcm.RAM_SIZE:#x}"
            ),
            f'printf "{marker}\\n"',
        ),
        expected_output=[marker],
        timeout=30,
        output_path=work / f"{name}.txt",
    )
    result = dumped.read_bytes()
    assert len(result) == dcm.RAM_SIZE
    return result


def ram_slice(image: bytes, address: int, size: int) -> bytes:
    offset = address - dcm.RAM_BASE
    return image[offset : offset + size]


def verify_static_propositions() -> None:
    print("== exact Camry bootloader propositions ==")
    image = IMAGE.read_bytes()
    assert hashlib.sha256(image).hexdigest() == IMAGE_SHA256
    result = analyze(image)
    claims = cast("dict[str, bool]", result["claims"])
    propositions = cast("dict[str, dict[str, bool]]", result["propositions"])
    for claim in ("MEM-SAFE-001", "MEM-SAFE-002", "MEM-SAFE-003"):
        assert claims[claim] is True
        failed = [name for name, passed in propositions[claim].items() if not passed]
        assert failed == []
        print(f"{claim}: {len(propositions[claim])} propositions passed")


def verify_short_block_and_raw_copy(work: Path) -> None:
    print("== exact Camry short-block execution ==")
    elf, _model = fuzz.prepare_elf(work, 30)
    payload = bytes.fromhex("deadc0de112233445566778899aabb")

    progress = bytearray(dcm.RAM_SIZE)
    write_ram(progress, SOURCE, payload)
    write_ram(progress, DESTINATION, b"\xa5" * 16)
    write_ram(progress, BOOT_GP - 0x6C2C, SOURCE.to_bytes(4, "little"))
    write_ram(progress, BOOT_GP - 0x6C28, DESTINATION.to_bytes(4, "little"))
    write_ram(progress, BOOT_GP - 0x6C24, len(payload).to_bytes(2, "little"))
    write_ram(progress, BOOT_GP - 0x6C22, b"\x01")
    after_progress = execute_and_dump(
        elf,
        work,
        "short_progress",
        0x6BDE,
        bytes(progress),
    )
    assert ram_slice(after_progress, BOOT_GP - 0x6C24, 2) == b"\x00\x00"
    assert ram_slice(after_progress, BOOT_GP - 0x6C22, 1) == b"\x00"
    assert (
        int.from_bytes(ram_slice(after_progress, BOOT_GP - 0x6C2C, 4), "little")
        == SOURCE
    )
    assert (
        int.from_bytes(ram_slice(after_progress, BOOT_GP - 0x6C28, 4), "little")
        == DESTINATION
    )
    assert ram_slice(after_progress, DESTINATION, 16) == b"\xa5" * 16

    descriptor = BOOT_GP - 0x6D48
    raw_copy = bytearray(dcm.RAM_SIZE)
    write_ram(raw_copy, SOURCE, payload)
    write_ram(raw_copy, DESTINATION, b"\xa5" * len(payload))
    write_ram(raw_copy, BOOT_GP - 0x6CE9, b"\x01")
    write_ram(raw_copy, BOOT_GP - 0x6D35, b"\x01")
    write_ram(raw_copy, BOOT_GP - 0x6D36, b"\x01")
    write_ram(raw_copy, descriptor, DESTINATION.to_bytes(4, "little"))
    write_ram(raw_copy, descriptor + 8, SOURCE.to_bytes(4, "little"))
    write_ram(raw_copy, descriptor + 0xC, len(payload).to_bytes(2, "little"))
    after_copy = execute_and_dump(
        elf,
        work,
        "raw_copy",
        0x4F50,
        bytes(raw_copy),
    )
    assert ram_slice(after_copy, DESTINATION, len(payload)) == payload
    assert int.from_bytes(ram_slice(after_copy, descriptor, 4), "little") == (
        DESTINATION + len(payload)
    )
    assert ram_slice(after_copy, BOOT_GP - 0x6D35, 1) == b"\x00"


def main() -> int:
    verify_static_propositions()
    out_root = REPO_ROOT / "build/out"
    out_root.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(
        prefix="verify-f33-boot-memory-", dir=out_root
    ) as td:
        verify_short_block_and_raw_copy(Path(td))
    print("Camry F33 bootloader memory-safety verification passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
