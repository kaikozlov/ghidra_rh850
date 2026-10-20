"""Camry reconstruction tree, identity image, and evidence loaders."""
from __future__ import annotations

from pathlib import Path
from tools import REPO_ROOT
import hashlib
import json
from tools.project.analysis_target import target as resolve_target
from tools.project.build_paths import for_repo

TARGET = "camry-8965F3307000"
ROOT = REPO_ROOT / resolve_target(TARGET)[1]["decomp_root"]
COMMON_HEADER = ROOT / "include" / "common.h"
OUTPUT = for_repo(REPO_ROOT).out / "targets" / TARGET / "decomp"
CANDIDATES = OUTPUT / "candidates"


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


def image_summary(symbols: list[dict]) -> dict:
    """Validate registered CodeFlash and report symbol-range coverage."""
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
    ranges = function_ranges(symbols)
    covered = 0
    outside = 0
    for start, end, name in ranges:
        if start >= len(image):
            outside += 1
            continue
        if end >= len(image):
            raise SystemExit(f"{name}: range {start:#x}..{end:#x} crosses the end of CodeFlash")
        covered += end - start + 1
    return {
        "target": TARGET,
        "codeflash_sha256": digest,
        "image_bytes": len(image),
        "functions": len(symbols),
        "function_bytes": covered,
        "gap_bytes": len(image) - covered,
        "ranges_outside_codeflash": outside,
    }


# RH850G3M register banks: v850_common.sinc selector 0 and v850e3.sinc
# selectors 1/2. PSW and PMR have their existing dedicated host globals.
SYSTEM_REGISTERS = {
    "EIPC": (0, 0), "EIPSW": (0, 1), "FEPC": (0, 2), "FEPSW": (0, 3),
    "FEIC": (0, 14),
    "FPEC": (0, 11), "EIIC": (0, 13), "CTPC": (0, 16), "CTPSW": (0, 17),
    "EIWR": (0, 0x1c), "FEWR": (0, 0x1d),
    "RBASE": (1, 2), "EBASE": (1, 3), "INTBP": (1, 4), "MCTL": (1, 5), "FPIPR": (1, 7),
    "ISPR": (2, 10), "ICSR": (2, 12), "INTCFG": (2, 13),
    **{f"MPAT{index}": (6 + index // 8, 2 + 4 * (index % 8)) for index in range(16)},
}


def _machine_registers() -> dict[str, dict]:
    payload = json.loads(
        (REPO_ROOT / "data" / "generated" / "p1me_machine.json").read_text(encoding="utf-8")
    )
    found: dict[str, dict] = {}
    for value in payload.values():
        if isinstance(value, dict):
            for row in value.get("registers") or []:
                if isinstance(row, dict) and "name" in row and "address" in row:
                    found[row["name"]] = row
    return found
_CHECKED_STATUS = {"equivalent", "byte-matched"}


def load_oracles() -> list[dict]:
    return _load_jsonl(ROOT / "oracles.jsonl")
