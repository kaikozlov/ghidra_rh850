#!/usr/bin/env python3
"""Compact target-native H functions needed for the Techstream steering join.

This is a promotion helper for the disposable 8965H1202000 corpus.  The output
pins both raw function bodies and the decompiler text used to recover the
Command Value Torque producer chain; consumers should treat the raw CodeFlash as
the authoritative identity and the pseudocode as recovered semantic evidence.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
DEFAULT_CORPUS = REPO / "build/h_8965H1202000_rdbihelper2_decompilations.jsonl"
DEFAULT_IMAGE = REPO / "build/community-normalized/8965H1202000_CodeFlash.bin"
DEFAULT_OUT = REPO / "data/generated/corolla_8965H1202000_techstream_steering_decompiler_evidence.json"

ENTRIES = [
    0x495A0,  # RDBI DID 1C02 producer
    0x56892,  # diagnostic snapshot bank A
    0x57692,  # diagnostic snapshot bank B
    0xBB9E8,  # steering state -> diagnostic snapshot
    0xC84F2,  # coefficient selector A
    0xC850C,  # coefficient selector B
    0xCD55A,  # commanded-torque precursor composition
    0xCD5DC,  # commanded-torque scale/limit stage
    0xCE928,  # steering state publication
    0xCE974,  # active steering pipeline owner
]


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load_corpus(path: Path) -> dict[int, dict]:
    out: dict[int, dict] = {}
    with path.open() as f:
        for line in f:
            row = json.loads(line)
            if row.get("record") != "function":
                continue
            out[int(row["entry_addr"], 16)] = row
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--corpus", type=Path, default=DEFAULT_CORPUS)
    ap.add_argument("--image", type=Path, default=DEFAULT_IMAGE)
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = ap.parse_args()

    corpus = load_corpus(args.corpus)
    image = args.image.read_bytes()
    rows = []
    for entry in ENTRIES:
        row = corpus.get(entry)
        if row is None:
            raise SystemExit(f"missing target function 0x{entry:08X} in {args.corpus}")
        if not row.get("decompile_completed"):
            raise SystemExit(f"decompilation failed for 0x{entry:08X}: {row.get('decompile_error')}")
        size = int(row["body_size"])
        body = image[entry:entry + size]
        if len(body) != size:
            raise SystemExit(f"body outside image: 0x{entry:08X}+0x{size:X}")
        text = row["decompiled_c"]
        rows.append({
            "entry": f"0x{entry:08X}",
            "body_size": size,
            "body_sha256": sha(body),
            "decompiled_c_sha256": sha(text.encode()),
            "decompiled_c": text,
        })

    payload = {
        "schema": "corolla-h-techstream-steering-decompiler-evidence-v1",
        "software_id": "8965H1202000",
        "image": {
            "path": str(args.image.relative_to(REPO)) if args.image.is_relative_to(REPO) else str(args.image),
            "sha256": sha(image),
            "size": len(image),
        },
        "source_corpus": {
            "path": str(args.corpus.relative_to(REPO)) if args.corpus.is_relative_to(REPO) else str(args.corpus),
            "sha256": sha(args.corpus.read_bytes()),
        },
        "functions": rows,
        "function_count": len(rows),
        "boundary": (
            "Target-native evidence for the Techstream Command Value Torque join only. "
            "Names are not promoted into the Ghidra snapshot; raw-body hashes bind each "
            "recovered pseudocode observation to 8965H1202000."
        ),
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
