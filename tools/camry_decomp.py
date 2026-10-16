#!/usr/bin/env python3
"""Link the Camry CodeFlash image from its symbol map and report decomp status."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from tools import REPO_ROOT
from tools.project.analysis_target import target as resolve_target

TARGET = "camry-8965F3307000"
ROOT = REPO_ROOT / "decomp" / TARGET


def _load_jsonl(path: Path) -> list[dict]:
    rows: list[dict] = []
    with path.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, 1):
            text = line.strip()
            if not text:
                continue
            try:
                row = json.loads(text)
            except json.JSONDecodeError as exc:
                raise SystemExit(f"{path}:{line_number}: {exc}") from exc
            if not isinstance(row, dict):
                raise SystemExit(f"{path}:{line_number}: expected an object")
            rows.append(row)
    return rows


def load_symbols() -> list[dict]:
    return _load_jsonl(ROOT / "symbols.jsonl")


def load_matched() -> list[dict]:
    return _load_jsonl(ROOT / "matched.jsonl")


def _address(value: str) -> int:
    return int(value, 16)


def function_ranges(symbols: list[dict]) -> list[tuple[int, int, str]]:
    ranges: list[tuple[int, int, str]] = []
    for row in symbols:
        name = row["name"]
        for start, end in row["ranges"]:
            if end < start:
                raise SystemExit(f"{name}: range end {end:#x} precedes start {start:#x}")
            ranges.append((start, end, name))
    ranges.sort()
    previous_end = -1
    previous_name = ""
    for start, end, name in ranges:
        if start <= previous_end:
            raise SystemExit(
                f"overlapping function bytes: {previous_name} through {previous_end:#x} "
                f"and {name} at {start:#x}"
            )
        previous_end = end
        previous_name = name
    return ranges


def identity_image(symbols: list[dict] | None = None) -> tuple[bytes, dict]:
    """Rebuild CodeFlash by placing each symbol's original bytes back at its address."""
    metadata = resolve_target(TARGET)[1]
    image_path = REPO_ROOT / metadata["codeflash"]
    image = image_path.read_bytes()
    digest = hashlib.sha256(image).hexdigest()
    if digest != metadata["codeflash_sha256"]:
        raise SystemExit(f"CodeFlash hash drift: {digest}")
    if len(image) != metadata["codeflash_size"]:
        raise SystemExit(
            f"CodeFlash size {len(image)} != registered {metadata['codeflash_size']}"
        )
    ranges = function_ranges(symbols if symbols is not None else load_symbols())
    rebuilt = bytearray(image)
    covered = 0
    outside = 0
    for start, end, name in ranges:
        if start >= len(image):
            outside += 1
            continue
        if end >= len(image):
            raise SystemExit(f"{name}: range {start:#x}..{end:#x} crosses the end of CodeFlash")
        rebuilt[start : end + 1] = image[start : end + 1]
        covered += end - start + 1
    if bytes(rebuilt) != image:
        raise SystemExit("identity link diverged from CodeFlash")
    report = {
        "target": TARGET,
        "codeflash_sha256": digest,
        "image_bytes": len(image),
        "functions": len(symbols if symbols is not None else load_symbols()),
        "function_bytes": covered,
        "gap_bytes": len(image) - covered,
        "ranges_outside_codeflash": outside,
        "matched": [
            {"addr": row["addr"], "name": row["name"], "status": row["status"]}
            for row in load_matched()
        ],
    }
    return bytes(rebuilt), report


def cmd_identity(args: argparse.Namespace) -> int:
    image, report = identity_image()
    if args.output:
        destination = Path(args.output)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(image)
        report["output"] = str(destination)
    print(json.dumps(report, indent=2))
    return 0


def cmd_status(_args: argparse.Namespace) -> int:
    _, report = identity_image()
    named = sum(1 for row in load_symbols() if not row["name"].startswith("FUN_"))
    report["named_functions"] = named
    report["equivalent_functions"] = sum(
        1 for row in report["matched"] if row["status"] == "equivalent"
    )
    report["byte_matched_functions"] = sum(
        1 for row in report["matched"] if row["status"] == "byte-matched"
    )
    print(json.dumps(report, indent=2))
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    identity = sub.add_parser("identity", help="link an image identical to CodeFlash")
    identity.add_argument("--output", help="write the linked image here")
    identity.set_defaults(func=cmd_identity)
    status = sub.add_parser("status", help="print image and matched-function counts")
    status.set_defaults(func=cmd_status)
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
