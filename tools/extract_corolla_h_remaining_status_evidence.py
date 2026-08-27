#!/usr/bin/env python3
"""Extract compact exact-H evidence for the remaining 0x030/0x351 status paths."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from corolla_h_constants import CODEFLASH as H_CODEFLASH

from decompiler_evidence import bind_entries, load_function_corpus, sha256_bytes

REPO = Path(__file__).resolve().parents[1]
IMAGE = H_CODEFLASH
OUT = REPO / "data/generated/corolla_8965H1202000_remaining_status_decompiler_evidence.json"
ENTRIES = (
    0x36AAA, 0x36B9E, 0x36BBE, 0x36CEC, 0x3738C,
    0x46E62, 0x46EE0, 0x472E0, 0x5258A, 0x5778E,
    0xBB8F6, 0xBB942, 0xBB98E, 0xBBA48, 0xBBF8A, 0xBBFE6, 0xBD50C, 0xCF070,
)


def sha(data: bytes) -> str:
    return sha256_bytes(data)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--image", type=Path, default=IMAGE)
    ap.add_argument("--corpus", type=Path, required=True)
    ap.add_argument("--out", type=Path, default=OUT)
    args = ap.parse_args()
    image = args.image.read_bytes()
    if len(image) != 0x100000:
        raise SystemExit(f"expected 1 MiB H CodeFlash, got {len(image):#x}")
    rows, _ = load_function_corpus(args.corpus)
    functions = bind_entries(
        image, rows, ENTRIES, include_data_references=False,
        include_body_ranges=False, honor_body_ranges=False,
    )

    payload = {
        "schema": "corolla-h-remaining-status-decompiler-evidence-v1",
        "software_id": "8965H1202000",
        "image": {"path": str(args.image.resolve().relative_to(REPO.resolve())), "size": len(image), "sha256": sha(image)},
        "source_corpus": {"path": str(args.corpus.resolve().relative_to(REPO.resolve())), "sha256": sha(args.corpus.read_bytes()), "function_count": len(rows)},
        "function_count": len(functions),
        "functions": functions,
        "boundary": (
            "Exact-H raw-body-bound decompilations for the remaining 0x030 B6[1] Q-current-derived status chain and "
            "the 0x351 force-7 source topology. OEM display names are not inferred from internal status words."
        ),
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(f"wrote {args.out}: {len(functions)} functions")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
