#!/usr/bin/env python3
"""Promote exact-F33 0x394 DEM/classifier decompiler evidence."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
IMAGE = REPO / "community/kai/camry-2026/normalized/8965F3307000_CodeFlash.bin"
OUT = REPO / "data/generated/camry_8965F3307000_fault_status_decompiler_evidence.json"
IMAGE_SHA256 = "42dce8efc42f6ae31718e7713fa2d26bb9191b4a82439778aee4d7afded9b0e7"
ENTRIES = [
    0x50FC8,  # DEM class accumulator
    0x510B6,  # class-2 additional injection
    0x510E0,  # classifier operational helper
    0x5110A,  # primary-latch aging helper
    0x5116C,  # secondary-latch aging helper
    0x511B6,  # latch-aging coordinator
    0x51208,  # invalid/unavailable classifier predicate
    0x51266,  # state-11 additional aggregate source
    0x512E4,  # 17-state classifier + table projection
    0x51592,  # DEM/classifier initialization
]


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--corpus", type=Path, required=True)
    ap.add_argument("--out", type=Path, default=OUT)
    args = ap.parse_args()

    image = IMAGE.read_bytes()
    if len(image) != 0x100000 or sha(image) != IMAGE_SHA256:
        raise SystemExit("exact F33 image identity drift")

    rows: dict[int, dict] = {}
    total = 0
    for line in args.corpus.open(encoding="utf-8"):
        row = json.loads(line)
        if row.get("record") == "function":
            total += 1
            rows[int(row["entry_addr"], 16)] = row

    functions = []
    for entry in ENTRIES:
        row = rows.get(entry)
        if not row or not row.get("decompile_completed") or not row.get("decompiled_c"):
            raise SystemExit(f"missing complete decompile 0x{entry:08X}")
        size = int(row["body_size"])
        text = row["decompiled_c"]
        functions.append({
            "entry": f"0x{entry:08X}",
            "body_size": size,
            "body_sha256": sha(image[entry:entry + size]),
            "decompiled_c_sha256": sha(text.encode()),
            "decompiled_c": text,
        })

    obj = {
        "schema": "camry-8965f3307000-fault-status-decompiler-evidence-v1",
        "software_id": "8965F3307000",
        "image": {
            "path": str(IMAGE.relative_to(REPO)),
            "size": len(image),
            "sha256": IMAGE_SHA256,
        },
        "source_corpus": {
            "path": str(args.corpus),
            "sha256": sha(args.corpus.read_bytes()),
            "function_count": total,
            "boundary": (
                "Disposable exact-F33 Ghidra corpus. Promoted functions are independently raw-body-hash-bound "
                "to the normalized 8965F3307000 image; the disposable project/corpus is not required at verification time."
            ),
        },
        "function_count": len(functions),
        "functions": functions,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"wrote {args.out}: {len(functions)} functions from {total}-function corpus")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
