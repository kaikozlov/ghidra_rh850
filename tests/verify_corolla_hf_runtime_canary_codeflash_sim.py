#!/usr/bin/env python3
"""Execute the corrected Corolla H/F RAM canary against both tracked images."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BUILDER = ROOT / "exploit/ephemeral_runtime/build_corolla_hf_command5_carrier.py"
SPEC = ROOT / "tests/fixtures/rh850/corolla_hf_runtime_canary_sim.json"
IMAGES = (
    ROOT / "firmware/corolla-8965H1202000/CodeFlash.bin",
    ROOT / "firmware/corolla-8965F1208000/CodeFlash.bin",
)
EXPECTED = (
    "COROLLA_RAM_HEARTBEAT=0x45504844 TICK=1 "
    "CONTEXT=0x43545848 STARTUP=0x53544152 FOREGROUND=0x46475248"
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
    with tempfile.TemporaryDirectory(prefix="corolla-hf-codeflash-sim-", dir=tmp_root) as td:
        work = Path(td)
        build_dir = work / "build"
        run([sys.executable, str(BUILDER), "--output-dir", str(build_dir)])

        resident = build_dir / "corolla_hf_runtime_canary.bin"
        metadata = json.loads(
            (build_dir / "corolla_hf_runtime_canary.json").read_text(encoding="utf-8")
        )
        blob = resident.read_bytes()
        if metadata["compile_contract"]["candidate_base"] != "0xFEBF0000":
            raise AssertionError("resident base drift")
        if metadata["compile_contract"]["relocations"] != 0:
            raise AssertionError("resident contains relocations")
        if metadata["shellcode"] != {
            "headroom": 464 - len(blob),
            "sha256": sha256(blob),
            "size": len(blob),
        }:
            raise AssertionError("resident metadata does not bind the generated binary")

        for image in IMAGES:
            simulation_dir = work / image.parent.name
            proc = run([
                str(ROOT / "tools/rh850"),
                "codeflash-sim",
                str(image),
                "--spec",
                str(SPEC),
                "--load",
                f"0xFEBF0000={resident}",
                "--output-dir",
                str(simulation_dir),
                "--expect",
                EXPECTED,
            ])
            output = proc.stdout + proc.stderr
            if (
                EXPECTED not in output
                or "codeflash-sim: PASS" not in output
                or "hardware UNVERIFIED" not in output
            ):
                raise AssertionError(
                    f"{image.parent.name} simulation omitted expected result\n{output}"
                )

    print(f"PASS {EXPECTED}")
    print("PASS corrected RAM resident executed against both Corolla H/F CodeFlash images")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
