#!/usr/bin/env python3
"""Promote the exact F33 callback used by the current GTS+ ASIC-state join."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from camry_f33_corpus import CORPUS, IMAGE, IMAGE_SHA256, body_bytes, display_path
from decompiler_evidence import bind_entries, bind_function, load_function_corpus, require_function, sha256_bytes

REPO = Path(__file__).resolve().parents[1]
OUT = REPO / "data/generated/camry_8965F3307000_gtsplus_decompiler_evidence.json"
IMAGE_SHA = IMAGE_SHA256
ENTRY = 0x4E848


def sha(data: bytes) -> str:
    return sha256_bytes(data)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--corpus", type=Path, default=CORPUS)
    ap.add_argument("--out", type=Path, default=OUT)
    args = ap.parse_args()

    image = IMAGE.read_bytes()
    if len(image) != 0x100000 or sha(image) != IMAGE_SHA:
        raise SystemExit("exact F33 image identity drift")

    rows, total = load_function_corpus(args.corpus)
    try:
        row = require_function(rows, ENTRY)
    except ValueError as exc:
        raise SystemExit(str(exc)) from exc
    callback = bind_function(image, row)
    body_size = callback["body_size"]
    body = body_bytes(image, row)
    text = row["decompiled_c"]
    refs = {int(ref["to_addr"], 16) for ref in row.get("data_references", [])}
    if not {0xFEBE8298, 0xFEBE829C} <= refs or "param_1 + 4" not in text:
        raise SystemExit("0x4E848 callback canonical-reference contract drift")

    out = {
        "schema": "camry-8965f3307000-gtsplus-decompiler-evidence-v1",
        "software_id": "8965F3307000",
        "image": {
            "path": str(IMAGE.relative_to(REPO)),
            "size": len(image),
            "sha256": IMAGE_SHA,
        },
        "source_corpus": {
            "path": display_path(args.corpus),
            "sha256": sha(args.corpus.read_bytes()),
            "function_count": total,
            "boundary": "Tracked first-class exact-F33 Ghidra corpus; promoted function body and canonical data references remain independently image-bound.",
        },
        "callback": {
            "entry": "0x0004E848",
            "body_size": body_size,
            "body_ranges": row.get("body_ranges", []),
            "data_references": row.get("data_references", []),
            "body_sha256": sha(body),
            "decompiled_c_sha256": sha(text.encode()),
            "decompiled_c": text,
            "fixed_gp_offsets": ["-0x3568", "-0x3564"],
            "gp_value_from_exact_f33_runtime_model": "0xFEBEB800",
            "resolved_sources": ["0xFEBE8298", "0xFEBE829C"],
            "output_bytes": 8,
        },
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    print(f"wrote {args.out}: callback 0x{ENTRY:X}, corpus={total}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
