#!/usr/bin/env python3
"""Materialize canonical physical CodeFlash/DataFlash inputs for Corolla targets."""
from __future__ import annotations

import argparse
import hashlib
from dataclasses import dataclass
from pathlib import Path


REPO = Path(__file__).resolve().parents[4]


@dataclass(frozen=True)
class Input:
    source: str
    source_sha256: str
    source_size: int
    output: str
    output_sha256: str
    output_size: int
    require_ff_suffix: bool = False


INPUTS = (
    Input(
        "community/albinoelephant/normalized/8965H1202000_CodeFlash.bin",
        "0b47bdc1217835c839e3543e52eab40eb793650a9c159e46f6a9b365ea41a67f",
        0x100000,
        "firmware/corolla-8965H1202000/CodeFlash.bin",
        "0b47bdc1217835c839e3543e52eab40eb793650a9c159e46f6a9b365ea41a67f",
        0x100000,
    ),
    Input(
        "community/albinoelephant/dump_ff200000_ff208000.bin",
        "8ac2a6beecb4ca2e6caf695eebffe440478171b4e093a1b2a36ab4e4ff313299",
        0x8000,
        "firmware/corolla-8965H1202000/DataFlash.bin",
        "8ac2a6beecb4ca2e6caf695eebffe440478171b4e093a1b2a36ab4e4ff313299",
        0x8000,
    ),
    Input(
        "community/spanconstant/raw-20260821/span-corolla-2025.20260821-1511/"
        "dump_codeflash_00000000_00200000_20260821-152033.bin",
        "b8fa3d951f59fb75c190ce1b2c73164adb952f871650cfcd3b7656f08a9c448d",
        0x200000,
        "firmware/corolla-8965F1208000/CodeFlash.bin",
        "fdb35b76891cf84a8b89e0a05c9c7c5cfcd27994cf85ccc01ff32828f53091f6",
        0x100000,
        True,
    ),
    Input(
        "community/spanconstant/raw-20260821/span-corolla-2025.20260821-1511/"
        "dump_dataflash_ff200000_ff210000_20260821-151200.bin",
        "85d76a96436e99e246b0695938e2dd046b8878e7d0e68f2ba7cd79f285f468a2",
        0x10000,
        "firmware/corolla-8965F1208000/DataFlash.bin",
        "7d339a531b911b97a1d3d0bbeb45938aa996dcc856a0951f6c74ed42c67c1d58",
        0x8000,
    ),
)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def materialize(spec: Input, check: bool) -> None:
    source = REPO / spec.source
    raw = source.read_bytes()
    if len(raw) != spec.source_size or sha256(raw) != spec.source_sha256:
        raise SystemExit(f"source identity drift: {spec.source}")
    if spec.require_ff_suffix and set(raw[spec.output_size:]) != {0xFF}:
        raise SystemExit(f"non-FF data outside physical CodeFlash: {spec.source}")
    normalized = raw[:spec.output_size]
    if sha256(normalized) != spec.output_sha256:
        raise SystemExit(f"normalized identity drift: {spec.output}")
    output = REPO / spec.output
    if check:
        if not output.is_file() or output.read_bytes() != normalized:
            raise SystemExit(f"canonical target input drift: {spec.output}")
    else:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_bytes(normalized)
    print(f"{'checked' if check else 'wrote'} {spec.output} ({len(normalized)} bytes)")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    for spec in INPUTS:
        materialize(spec, args.check)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
