#!/usr/bin/env python3
"""Promote exact-F33 TSS3 transmit/status packer decompiler evidence."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
IMAGE = REPO / "community/kai/camry-2026/normalized/8965F3307000_CodeFlash.bin"
OUT = REPO / "data/generated/camry_8965F3307000_tss3_tx_decompiler_evidence.json"
IMAGE_SHA256 = "42dce8efc42f6ae31718e7713fa2d26bb9191b4a82439778aee4d7afded9b0e7"
ENTRIES = [
    0x4C000,  # 0x4A3 source preparation
    0x4C14E,  # 0x4A3 staging
    0x4C1C0,  # 0x351 debounce/state preparation
    0x4C216,  # 0x351 force/status producer
    0x4C24A,  # 0x394 state projection
    0x4C7AA,  # 0x4A3 packer / PDU3
    0x4CE08,  # 0x394 packer / PDU2
    0x4CED0,  # 0x351 packer / PDU1
    0x7D0EA,  # generic Tx PDU status helper
    0x7D1DC,  # generic Tx scalar packer
    0x7D31E,  # generic Tx raw pack helper
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

    def refs(token: str) -> list[dict]:
        found = []
        for entry, row in rows.items():
            text = row.get("decompiled_c", "")
            if token in text:
                size = int(row["body_size"])
                found.append({
                    "entry": f"0x{entry:08X}",
                    "body_size": size,
                    "body_sha256": sha(image[entry:entry + size]),
                })
        return sorted(found, key=lambda item: item["entry"])

    obj = {
        "schema": "camry-8965f3307000-tss3-tx-decompiler-evidence-v1",
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
                "Disposable Ghidra corpus used only to recover the selected functions and a bounded direct/fixed-GP "
                "reference census. Every promoted row is independently body-hash-bound to the exact normalized F33 image."
            ),
        },
        "function_count": len(functions),
        "functions": functions,
        "fixed_gp_census": {
            "driver_torque_source_gp_minus_0x5158": refs("-0x5158"),
            "alternate_4a3_current_source_gp_minus_0x50e8": refs("-0x50e8"),
            "did1151_q_current_source_gp_minus_0x50f2": refs("-0x50f2"),
            "boundary": (
                "Whole recovered-function-corpus textual census of direct/fixed-GP references only. Computed aliases, "
                "value-set pointer recovery, DMA, and functions not recovered in this corpus are outside the negative proof."
            ),
        },
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"wrote {args.out}: {len(functions)} functions, corpus={total}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
