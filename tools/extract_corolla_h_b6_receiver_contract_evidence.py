#!/usr/bin/env python3
"""Promote exact H decompiler evidence for the protected-B6 receiver contract."""
from __future__ import annotations
import argparse, json
from pathlib import Path
from corolla_h_constants import CODEFLASH as H_CODEFLASH

from decompiler_evidence import bind_entries, load_function_corpus, sha256_bytes

REPO = Path(__file__).resolve().parents[1]
IMAGE = H_CODEFLASH
OUT = REPO / "data/generated/corolla_8965H1202000_b6_receiver_contract_decompiler_evidence.json"
ENTRIES = [
    0x44538, 0x4456C, 0x445C0, 0x4460C, 0x44640, 0x44658, 0x446EC, 0x44744,
    0x46A10, 0x5262C, 0x53030, 0x58BBC, 0x59574, 0x5F30C, 0x5FAF2,
    0x73564, 0x7683C, 0x769F6,
    0x87A5E, 0x87A82, 0x87AA0,
    0xB8EE4, 0xBA090,
    0xC819E, 0xC825A, 0xC89D2, 0xC8D42,
    0xCB246, 0xCB4F4, 0xCBEEE, 0xCBE6E, 0xCC7F8, 0xCCF58,
]

def sha(data: bytes) -> str:
    return sha256_bytes(data)

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--image", type=Path, default=IMAGE)
    ap.add_argument("--corpus", type=Path, required=True, help="disposable corrected-context H decompiler corpus JSONL")
    ap.add_argument("--out", type=Path, default=OUT)
    args = ap.parse_args()
    image = args.image.read_bytes()
    if len(image) != 0x100000:
        raise SystemExit(f"expected 1 MiB H CodeFlash, got {len(image):#x}")
    rows, _ = load_function_corpus(args.corpus)
    funcs = bind_entries(
        image, rows, ENTRIES, include_data_references=False,
        include_body_ranges=False, honor_body_ranges=False,
    )

    rel_image = str(args.image.resolve().relative_to(REPO.resolve())) if args.image.resolve().is_relative_to(REPO.resolve()) else str(args.image)
    rel_corpus = str(args.corpus.resolve().relative_to(REPO.resolve())) if args.corpus.resolve().is_relative_to(REPO.resolve()) else str(args.corpus)
    out = {
        "schema": "corolla-h-b6-receiver-contract-decompiler-evidence-v1",
        "software_id": "8965H1202000",
        "image": {"path": rel_image, "size": len(image), "sha256": sha(image)},
        "source_corpus": {"path": rel_corpus, "sha256": sha(args.corpus.read_bytes())},
        "function_count": len(funcs),
        "functions": funcs,
        "boundary": (
            "Target-native H decompiler observations for protected-B6 request selection, COM deadline/activity supervision, "
            "receive-status propagation, companion control fields, and rolling sequence handling. Every promoted pseudocode "
            "body is bound to exact 8965H1202000 raw bytes; wall-clock scheduler timing and upstream producer behavior are not inferred."
        ),
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    print(f"wrote {args.out}: {len(funcs)} functions")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
