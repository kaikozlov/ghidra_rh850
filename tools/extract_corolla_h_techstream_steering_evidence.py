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
DEFAULT_CORPUS = REPO / "build/work/corpora/h_8965H1202000_rdbihelper2_decompilations.jsonl"
DEFAULT_IMAGE = REPO / "community/albinoelephant/normalized/8965H1202000_CodeFlash.bin"
DEFAULT_OUT = REPO / "data/generated/corolla_8965H1202000_techstream_steering_decompiler_evidence.json"

ENTRIES = [
    0x312F0,  # published steering state -> motor-reference staging
    0x378CC,  # six-row communication-monitor failure dispatcher
    0x379A2,  # communication monitor scheduler / slot selector
    0x44744,  # generated receive-status slot reader
    0x45C8E,  # receive-status slot 0 unpacker
    0x45E34,  # receive-status slot 5 unpacker
    0x4636A,  # receive-status slot 0x10 unpacker
    0x46606,  # receive-status slot 0x13 unpacker
    0x468FA,  # receive-status slot 0x16 unpacker (D7)
    0x46A10,  # receive-status slot 0x18 unpacker (B6)
    0x4C338,  # communication monitor Dem event failure reporter
    0x4C9B6,  # Dem event -> DTC table consumer
    0x32934,  # compensated Q command minus raw Q feedback
    0x32958,  # Q-current PI sign/gating helper
    0x329A0,  # Q-current PI stage
    0x33160,  # d/q feedback combine
    0x3322E,  # d/q current-reference publication
    0x335EE,  # D-axis/current auxiliary update
    0x33622,  # D-axis/current auxiliary limiter
    0x3364E,  # D-axis/current command source update
    0x336EE,  # Q-axis command source publication
    0x4915E,  # RDBI 1151 Motor Actual Current Q
    0x4919A,  # RDBI 1152 Command Value Current Q
    0x491D6,  # RDBI 1153 Motor Actual Current D
    0x49372,  # RDBI 1185 CAN Vehicle Speed (SP1) from protected D7
    0x49212,  # RDBI 1154 Command Value Current D
    0x4924E,  # RDBI 1155 Motor Rotation Angle
    0x49298,  # RDBI 1156 Final Motor Current Limited Q
    0x495A0,  # RDBI DID 1C02 Command Value Torque
    0x56892,  # diagnostic snapshot bank A
    0x5722E,  # motor diagnostic snapshot bank
    0x57692,  # diagnostic snapshot bank B
    0xBB9E8,  # steering state -> diagnostic snapshot
    0xC84F2,  # coefficient selector A
    0xC850C,  # coefficient selector B
    0xCD55A,  # commanded-torque precursor composition
    0xCD5DC,  # commanded-torque scale/limit stage
    0xCD644,  # gated command state -> motor-reference state
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
        "schema": "corolla-h-techstream-steering-decompiler-evidence-v2",
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
            "Target-native evidence for the Techstream command-torque/current control join. "
            "Names are not promoted into the Ghidra snapshot; raw-body hashes bind each "
            "recovered pseudocode observation to 8965H1202000."
        ),
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
