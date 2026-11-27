#!/usr/bin/env python3
"""Benchmark Ghidra's plain and JIT p-code engines on a firmware RAM-clear loop."""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import tempfile
from pathlib import Path
from typing import Any

from tools import REPO_ROOT

WORKLOAD = "clear_application_ram_4k@0x632b2; lp=entry"


def _run_headless(
    project_dir: Path, project_name: str, stage: str, log_path: Path, arguments: list[str],
) -> None:
    label = f"pcode-jit-{stage}"
    result = subprocess.run(
        [
            str(REPO_ROOT / "tools/project/run_headless"),
            "--project-dir", str(project_dir),
            "--project", project_name,
            "--label", label,
            "--log", str(log_path),
            "--quiet", "--",
            *arguments,
        ],
        cwd=REPO_ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(f"{label} failed ({result.returncode}):\n{result.stdout}")

def run_engine(
    project_dir: Path,
    project_name: str,
    program_name: str,
    engine: str,
    instructions: int,
    warmup: int,
    image_size: int,
    output_dir: Path,
) -> dict[str, Any]:
    result_path = output_dir / f"{engine}.json"
    _run_headless(
        project_dir, project_name, engine, output_dir / f"{engine}.log",
        [
            "-process", program_name,
            "-noanalysis",
            "-readOnly",
            "-postScript", "BenchmarkPcodeJit.java",
            engine,
            str(instructions),
            str(warmup),
            str(image_size),
            str(result_path),
        ],
    )
    result = json.loads(result_path.read_text(encoding="utf-8"))
    if (
        result["engine"] != engine
        or result["instructions"] != instructions
        or result["warmup_instructions"] != warmup
        or not 0 <= result["compiled_instructions"] <= instructions
        or not 0 <= result["warmup_compiled_instructions"] <= warmup
        or result["compiled_instructions"] + result["interpreted_instructions"] != instructions
        or result["warmup_compiled_instructions"] + result["warmup_interpreted_instructions"]
        != warmup
    ):
        raise RuntimeError(f"{engine} reported inconsistent execution counts: {result}")
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", type=Path)
    parser.add_argument("instructions", type=int, help="positive measured instruction count")
    parser.add_argument("--warmup-instructions", type=int, default=0)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.instructions <= 0:
        parser.error("instruction count must be positive")
    if args.warmup_instructions < 0:
        parser.error("warm-up instruction count must be nonnegative")

    image = args.image.resolve()
    if not image.is_file():
        parser.error(f"image is not a file: {image}")
    image_size = image.stat().st_size
    with image.open("rb") as stream:
        image_sha256 = hashlib.file_digest(stream, "sha256").hexdigest()

    temporary_root = REPO_ROOT / "build/tmp"
    temporary_root.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="pcode-jit-benchmark-", dir=temporary_root) as temp:
        root = Path(temp)
        project_dir = root / "project"
        output_dir = root / "results"
        project_name = "pcode_jit_benchmark"
        _run_headless(
            project_dir, project_name, "import", root / "import.log",
            [
                "-import",
                str(image),
                "-processor",
                "v850e3:LE:32:default",
                "-cspec",
                "default",
                "-loader",
                "BinaryLoader",
                "-loader-baseAddr",
                "0x0",
                "-noanalysis",
            ],
        )

        plain = run_engine(
            project_dir, project_name, image.name, "plain", args.instructions,
            args.warmup_instructions, image_size, output_dir,
        )
        jit = run_engine(
            project_dir, project_name, image.name, "jit", args.instructions,
            args.warmup_instructions, image_size, output_dir,
        )
        snapshots_match = {
            phase: plain[f"{phase}_snapshot"] == jit[f"{phase}_snapshot"]
            for phase in ("initial", "final")
        }
        report = {
            "image": str(image),
            "image_sha256": image_sha256,
            "workload": WORKLOAD,
            "instructions": args.instructions,
            "warmup_instructions": args.warmup_instructions,
            "snapshot_matches": snapshots_match,
            "plain": plain,
            "jit": jit,
        }
        if args.output is not None:
            destination = args.output.resolve()
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    print(f"workload: {WORKLOAD}")
    print(f"instructions: {args.instructions:,} after {args.warmup_instructions:,} warm-up")
    for result in (plain, jit):
        elapsed = result["wall_nanoseconds"]
        rate = f", {args.instructions * 1e9 / elapsed:,.0f} instructions/s" if elapsed > 0 else ""
        print(
            f"{result['engine']}: {elapsed:,} ns{rate}; "
            f"{result['compiled_instructions']:,} compiled, "
            f"{result['interpreted_instructions']:,} interpreted"
        )
    for phase, matches in snapshots_match.items():
        print(f"{phase}_snapshot_matches: {str(matches).lower()}")
        if not matches:
            for field, value in plain[f"{phase}_snapshot"].items():
                other = jit[f"{phase}_snapshot"][field]
                if value != other:
                    print(f"  {field}: plain={value} jit={other}")
    return 0 if all(snapshots_match.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
