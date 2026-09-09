#!/usr/bin/env python3
"""Promote exact-F33 TSS3 transmit/status packer decompiler evidence."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from camry_f33_corpus import CORPUS, IMAGE, IMAGE_SHA256, body_bytes, display_path
from decompiler_evidence import bind_entries, bind_function, load_function_corpus, require_function, sha256_bytes

REPO = Path(__file__).resolve().parents[1]
OUT = REPO / "data/generated/camry_8965F3307000_tss3_tx_decompiler_evidence.json"
ENTRIES = [
    0x37E48,  # dual-channel actual-current aggregation; Q-axis sum feeds DID1151
    0x38678,  # nonlinear current/assist-feedback map
    0x3879E,  # publish mapped feedback to GP-0x4A00
    0x4C000,  # 0x4A3 source preparation
    0x4C14E,  # 0x4A3 staging
    0x4C1C0,  # 0x351 debounce/state preparation
    0x4C216,  # 0x351 force/status producer
    0x4C24A,  # 0x394 state projection
    0x4C490,  # 0x030 torque/current source preparation
    0x4C7AA,  # 0x4A3 packer / PDU3
    0x4C97A,  # 0x030 packer / PDU0
    0x4CE08,  # 0x394 packer / PDU2
    0x4CED0,  # 0x351 packer / PDU1
    0x7D0EA,  # generic Tx PDU status helper
    0x7D1DC,  # generic Tx scalar packer
    0x7D31E,  # generic Tx raw pack helper
]


def sha(data: bytes) -> str:
    return sha256_bytes(data)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--corpus", type=Path, default=CORPUS)
    ap.add_argument("--out", type=Path, default=OUT)
    args = ap.parse_args()

    image = IMAGE.read_bytes()
    if len(image) != 0x100000 or sha(image) != IMAGE_SHA256:
        raise SystemExit("exact F33 image identity drift")

    rows, total = load_function_corpus(args.corpus)
    functions = bind_entries(image, rows, ENTRIES)

    def refs(address: int) -> list[dict]:
        found = []
        for entry, row in rows.items():
            matched = [ref for ref in row.get("data_references", []) if int(ref["to_addr"], 16) == address]
            if matched:
                size = int(row["body_size"])
                found.append({
                    "entry": f"0x{entry:08X}",
                    "body_size": size,
                    "body_ranges": row.get("body_ranges", []),
                    "body_sha256": sha(body_bytes(image, row)),
                    "reference_types": sorted({ref["ref_type"] for ref in matched}),
                    "reference_sites": [ref["from_addr"] for ref in matched],
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
            "path": display_path(args.corpus),
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
            "driver_torque_source_gp_minus_0x5158": refs(0xFEBE66A8),
            "alternate_4a3_current_source_gp_minus_0x50e8": refs(0xFEBE6718),
            "did1151_q_current_source_gp_minus_0x50f2": refs(0xFEBE670E),
            "did1151_q_current_upstream_gp_minus_0x4a8e": refs(0xFEBE6D72),
            "mapped_current_feedback_gp_minus_0x4a00": refs(0xFEBE6E00),
            "tx030_current_scale_gp_plus_0x30d8": refs(0xFEBEE8D8),
            "boundary": (
                "Whole 6,065-function canonical Ghidra data-reference census to exact GP-resolved RAM addresses. Computed aliases "
                "without a Ghidra data reference, value-set pointer recovery, DMA, and unrecovered code remain outside the negative proof."
            ),
        },
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"wrote {args.out}: {len(functions)} functions, corpus={total}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
