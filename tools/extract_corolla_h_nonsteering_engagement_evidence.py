#!/usr/bin/env python3
"""Promote exact-H decompiler evidence for non-steering engagement-state ingress."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from corolla_h_constants import CODEFLASH as H_CODEFLASH

from decompiler_evidence import bind_entries, load_function_corpus, sha256_bytes

REPO = Path(__file__).resolve().parents[1]
GENERATOR = Path(__file__).resolve()
IMAGE = H_CODEFLASH
OUT = REPO / "data/generated/corolla_8965H1202000_nonsteering_engagement_decompiler_evidence.json"

# Exact-H target-native functions needed to close 0x51E Ready Status and the
# conserved 0x127 receive layout.  The source corpus is disposable; this compact
# artifact is raw-byte-bound and tracked.
ENTRIES = {
    0x00045EDE: "gear_packet_hybrid_scalar_unpacker",
    0x00046144: "ready_status_0x51e_scalar_unpacker",
    0x0005262C: "rte_input_staging_copy",
    0x000BAB58: "ready_status_secondary_operational_copy",
    0x000BAC16: "ready_status_primary_operational_copy",
    0x000BBA48: "ready_status_snapshot_publish",
}


def sha(data: bytes) -> str:
    return sha256_bytes(data)


def rel(path: Path) -> str:
    resolved = path.resolve()
    try:
        return str(resolved.relative_to(REPO.resolve()))
    except ValueError:
        return str(resolved)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--image", type=Path, default=IMAGE)
    ap.add_argument("--corpus", type=Path, required=True,
                    help="disposable exact-H whole-application decompiler corpus")
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

    out = {
        "schema": "corolla-h-nonsteering-engagement-decompiler-evidence-v1",
        "software_id": "8965H1202000",
        "generator": {"path": rel(GENERATOR), "sha256": sha(GENERATOR.read_bytes())},
        "image": {"path": rel(args.image), "size": len(image), "sha256": sha(image)},
        "source_corpus": {"path": rel(args.corpus), "sha256": sha(args.corpus.read_bytes())},
        "function_count": len(functions),
        "functions": functions,
        "boundary": (
            "Exact-H target-native decompilations for the retained 0x127 receive layout and the "
            "0x51E B0[7] Ready Status path. Every promoted function body is raw-byte-bound to "
            "8965H1202000. FEBEF052 reaches FEBEB5A8 through two operational copy sites; the "
            "dataflow chain is proved without claiming exclusive-writer provenance. Cruise semantics "
            "are not inferred from these EPS-local functions."
        ),
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    print(f"wrote {args.out}: {len(functions)} functions")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
