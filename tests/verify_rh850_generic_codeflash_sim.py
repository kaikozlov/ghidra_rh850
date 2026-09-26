#!/usr/bin/env python3
"""Execute a synthetic RAM resident against a non-target-specific CodeFlash image."""

from __future__ import annotations

import hashlib
import json
import struct
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IMAGE_SIZE = 0x60000
CODEFLASH_VALUE = 0x200
RAM_LOAD = 0xFEBF0200
ENTRY = RAM_LOAD
RESULT = 0xFEBF0100
VALUE = 0x13579BDF


def run(command: list[str]) -> subprocess.CompletedProcess[str]:
    proc = subprocess.run(
        command,
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if proc.returncode != 0:
        raise AssertionError(
            f"command failed ({proc.returncode}): {' '.join(command)}\n"
            f"{proc.stdout}{proc.stderr}"
        )
    return proc


def main() -> int:
    tmp_root = ROOT / "build/tmp"
    tmp_root.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="generic-codeflash-sim-", dir=tmp_root) as td:
        work = Path(td)
        source = work / "program.S"
        source.write_text(
            "    .section .text,\"ax\"\n"
            f"    mov 0x{CODEFLASH_VALUE:x}, r12\n"
            "    ld.w 0[r12], r10\n"
            "    mov 0xfebf0100, r11\n"
            "    st.w r10, 0[r11]\n"
            "stop:\n"
            "    br stop\n",
            encoding="utf-8",
        )
        run([
            str(ROOT / "tools/rh850"), "exec", "--work-dir", str(work),
            "v850-elf-gcc", "-mv850e3v5", "-mno-app-regs", "-ffreestanding",
            "-nostdlib", "-Wa,-mv850e3v5,-mextension", "-c", "/out/program.S",
            "-o", "/out/program.o",
        ])
        run([
            str(ROOT / "tools/rh850"), "exec", "--work-dir", str(work),
            "v850-elf-objcopy", "--dump-section", ".text=/out/program.bin",
            "/out/program.o",
        ])
        program = (work / "program.bin").read_bytes()

        image = bytearray(b"\xFF" * IMAGE_SIZE)
        struct.pack_into("<I", image, CODEFLASH_VALUE, VALUE)
        image_path = work / "new-target-CodeFlash.bin"
        image_path.write_bytes(image)
        ram_path = work / "resident.bin"
        ram_path.write_bytes(program)
        output_dir = work / "simulation"
        expected = f"GENERIC_RESULT=0x{VALUE:x}"

        proc = run([
            str(ROOT / "tools/rh850"), "codeflash-sim", str(image_path),
            "--entry", f"0x{ENTRY:X}",
            "--load", f"0x{RAM_LOAD:X}={ram_path}",
            "--memory-region", "0xFEBF0000,0x1000",
            "-ex", f"break *0x{ENTRY + len(program) - 2:X}",
            "-ex", "run",
            "-ex", f'printf "GENERIC_RESULT=0x%x\\n", *(unsigned int *)0x{RESULT:X}',
            "--output-dir", str(output_dir),
            "--expect", expected,
        ])
        output = proc.stdout + proc.stderr
        if (
            expected not in output
            or "codeflash-sim: PASS" not in output
            or "hardware UNVERIFIED" not in output
        ):
            raise AssertionError(f"generic execution omitted expected output\n{output}")

        audit = json.loads((output_dir / "simulation.json").read_text(encoding="utf-8"))
        if audit["schema"] != "rh850-raw-codeflash-sim-result-v1":
            raise AssertionError("generic result schema drift")
        if audit["input"] != {
            "base": "0x00000000",
            "entry": f"0x{ENTRY:08X}",
            "path": str(image_path.resolve()),
            "sha256": hashlib.sha256(image).hexdigest(),
            "size": IMAGE_SIZE,
        }:
            raise AssertionError("generic image audit drift")
        if audit["loads"] != [{
            "address": f"0x{RAM_LOAD:08X}",
            "path": str(ram_path.resolve()),
            "sha256": hashlib.sha256(ram_path.read_bytes()).hexdigest(),
            "size": len(program),
        }]:
            raise AssertionError("generic RAM-load audit drift")
        if audit["proof_boundary"]["hardware_validated"] is not False:
            raise AssertionError("simulation audit overclaims hardware validation")

    print(f"PASS {expected}")
    print("PASS arbitrary-size, arbitrary-hash CodeFlash image and RAM entry executed without a spec")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
