#!/usr/bin/env python3
"""Triage the blurbdust/yc SecOC patch target in an RH850 CodeFlash image.

This is a raw-byte first pass for future 8965F3/8965F4 firmware acquisitions.
It does not assume that the 8-byte egg is semantically a SecOC verifier. It
reports every occurrence, context bytes, and the exact overwrite performed by
the community patcher. It deliberately does **not** infer callers from raw
halfwords: instruction boundaries/code-vs-data ownership belong to Ghidra.
Semantic ownership must then be established with the companion Ghidra script
``ghidra/scripts/investigate/AnalyzeCommunityPatchTarget.java``.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

EGG = bytes.fromhex("88000152000ae50d")
PATCH = bytes.fromhex("01527f00")
PATCH_SEMANTICS = "mov 1,r10; jmp [lp] (immediate return with r10=1)"
REPO = Path(__file__).resolve().parents[1]
KNOWN_SIENNA_SHA256 = "21140bbd65e530a9e518a3e84e20e5d85679675bc09cc724cb177bb7c76bafde"
KNOWN_SIENNA_EGG_VA = 0x3485A
KNOWN_SIENNA_SECOC_WORKER = 0x8E4BA


def find_all(blob: bytes, needle: bytes) -> list[int]:
    matches: list[int] = []
    start = 0
    while True:
        offset = blob.find(needle, start)
        if offset < 0:
            return matches
        matches.append(offset)
        start = offset + 1


def context_hex(blob: bytes, offset: int, radius: int = 32) -> dict[str, object]:
    start = max(0, offset - radius)
    end = min(len(blob), offset + len(EGG) + radius)
    return {
        "start_offset": start,
        "end_offset": end,
        "hex": blob[start:end].hex(),
    }


def analyze(path: Path, *, image_base: int = 0, context_radius: int = 32) -> dict[str, object]:
    blob = path.read_bytes()
    digest = hashlib.sha256(blob).hexdigest()
    matches = []
    for offset in find_all(blob, EGG):
        matches.append({
            "file_offset": offset,
            "virtual_address": image_base + offset,
            "context": context_hex(blob, offset, context_radius),
            "patched_first_4_bytes": PATCH.hex(),
            "patch_semantics": PATCH_SEMANTICS,
        })

    known_sienna = digest == KNOWN_SIENNA_SHA256
    try:
        display_path = str(path.resolve().relative_to(REPO.resolve()))
    except ValueError:
        display_path = str(path.resolve())

    output: dict[str, object] = {
        "file": display_path,
        "sha256": digest,
        "size": len(blob),
        "image_base": image_base,
        "egg": EGG.hex(),
        "patch": PATCH.hex(),
        "patch_semantics": PATCH_SEMANTICS,
        "egg_match_count": len(matches),
        "matches": matches,
        "semantic_warning": (
            "An egg match is only a patch-location candidate. It does not establish "
            "that the containing function performs MAC verification; recover the "
            "containing function, callers, and SecOC/ICU data flow independently."
        ),
        "next_step": "Run AnalyzeCommunityPatchTarget.java in the imported image's Ghidra project.",
    }
    if known_sienna:
        output["known_image"] = {
            "name": "8965B4512000",
            "expected_false_positive_va": KNOWN_SIENNA_EGG_VA,
            "actual_secoc_rx_verify_worker": KNOWN_SIENNA_SECOC_WORKER,
            "classification": "known false positive: proprietary 0xAB event-token comparator",
        }
    return output


def parse_int(value: str) -> int:
    return int(value, 0)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", type=Path)
    parser.add_argument("--image-base", type=parse_int, default=0)
    parser.add_argument("--context-radius", type=int, default=32)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    result = analyze(args.image, image_base=args.image_base, context_radius=args.context_radius)
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(text, encoding="utf-8")
    else:
        print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
