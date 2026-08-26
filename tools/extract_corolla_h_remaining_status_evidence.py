#!/usr/bin/env python3
"""Extract compact exact-H evidence for the remaining 0x030/0x351 status paths."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
IMAGE = REPO / "community/albinoelephant/normalized/8965H1202000_CodeFlash.bin"
OUT = REPO / "data/generated/corolla_8965H1202000_remaining_status_decompiler_evidence.json"
ENTRIES = (
    0x36AAA, 0x36B9E, 0x36BBE, 0x36CEC, 0x3738C,
    0x46E62, 0x46EE0, 0x472E0, 0x5258A, 0x5778E,
    0xBB8F6, 0xBB942, 0xBB98E, 0xBBA48, 0xBBF8A, 0xBBFE6, 0xBD50C, 0xCF070,
)


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--image", type=Path, default=IMAGE)
    ap.add_argument("--corpus", type=Path, required=True)
    ap.add_argument("--out", type=Path, default=OUT)
    args = ap.parse_args()
    image = args.image.read_bytes()
    if len(image) != 0x100000:
        raise SystemExit(f"expected 1 MiB H CodeFlash, got {len(image):#x}")
    rows: dict[int, dict] = {}
    for line in args.corpus.open():
        row = json.loads(line)
        if row.get("record") == "function":
            rows[int(row["entry_addr"], 16)] = row
    functions = []
    for entry in ENTRIES:
        row = rows.get(entry)
        if not row or not row.get("decompile_completed") or not row.get("decompiled_c"):
            raise SystemExit(f"missing complete decompile 0x{entry:X}")
        size = int(row["body_size"])
        text = row["decompiled_c"]
        functions.append({
            "entry": f"0x{entry:08X}",
            "body_size": size,
            "body_sha256": sha(image[entry:entry + size]),
            "decompiled_c_sha256": sha(text.encode()),
            "decompiled_c": text,
        })
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
