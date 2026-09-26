#!/usr/bin/env python3
"""Execute the exact F33 RAM canary with stock CodeFlash in one address space."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BUILDER = ROOT / "exploit/ephemeral_runtime/build_camry_f33_command5_carrier.py"
IMAGE = ROOT / "firmware/camry-8965F3307000/CodeFlash.bin"
SCENARIO = ROOT / "tests/fixtures/rh850/camry_f33_runtime_canary_sim.json"
EXPECTED = (
    "RAM_HEARTBEAT=0x45504844 TICK=1 FLAG=0x0 "
    "CONTEXT=0x43545831 STARTUP=0x53544152 "
    "FOREGROUND=0x46475231 STOCK_ZERO=0x0"
)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


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
    with tempfile.TemporaryDirectory(prefix="f33-canary-codeflash-sim-", dir=tmp_root) as td:
        work = Path(td)
        build_dir = work / "build"
        sim_dir = work / "simulation"
        run([
            sys.executable,
            str(BUILDER),
            "--output-dir",
            str(build_dir),
        ])

        resident = build_dir / "camry_f33_runtime_canary.bin"
        metadata = json.loads(
            (build_dir / "camry_f33_runtime_canary.json").read_text(encoding="utf-8")
        )
        blob = resident.read_bytes()
        if metadata["compile_contract"]["candidate_base"] != "0xFEBF0000":
            raise AssertionError("resident base drift")
        if metadata["shellcode"] != {
            "headroom": 776 - len(blob),
            "sha256": sha256(blob),
            "size": len(blob),
        }:
            raise AssertionError("resident metadata does not bind the generated binary")

        proc = run([
            str(ROOT / "tools/rh850"),
            "codeflash-sim",
            str(IMAGE),
            "--spec",
            str(SCENARIO),
            "--load",
            f"0xFEBF0000={resident}",
            "--output-dir",
            str(sim_dir),
            "--expect",
            EXPECTED,
        ])
        output = proc.stdout + proc.stderr
        if EXPECTED not in output or "codeflash-sim: PASS" not in output:
            raise AssertionError(f"co-simulation omitted expected result\n{output}")

        result = json.loads((sim_dir / "simulation.json").read_text(encoding="utf-8"))
        if result["loads"] != [{
            "address": "0xFEBF0000",
            "path": str(resident.resolve()),
            "sha256": sha256(blob),
            "size": len(blob),
        }]:
            raise AssertionError("simulation audit does not bind the RAM resident")
        if len(result["overlays"]) != 33:
            raise AssertionError("simulation boundary-model inventory drift")

    print(f"PASS {EXPECTED}")
    print("PASS exact RAM resident executed with real-address stock CodeFlash")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
