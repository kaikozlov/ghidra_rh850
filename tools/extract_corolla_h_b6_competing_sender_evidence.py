#!/usr/bin/env python3
"""Promote exact-H decompiler evidence for competing protected-B6 receiver arbitration."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from corolla_h_constants import CODEFLASH as H_CODEFLASH

from decompiler_evidence import bind_entries, load_function_corpus, sha256_bytes

REPO = Path(__file__).resolve().parents[1]
GENERATOR = Path(__file__).resolve()
IMAGE = H_CODEFLASH
OUT = REPO / "data/generated/corolla_8965H1202000_b6_competing_sender_decompiler_evidence.json"

# These functions close the generic one-slot queue/coalescing behavior and the
# post-verification application arbitration that were deliberately outside the
# earlier byte-complete SecOC-envelope artifact.
ENTRIES = {
    0x00076A3C: "com_rx_indication_single_shadow_copy",
    0x00087B72: "secoc_queue_geometry_lookup",
    0x00087C22: "secoc_queue_slot_storage_lookup",
    0x00087CD6: "secoc_queue_first_insert",
    0x00087DB0: "secoc_queue_existing_slot_update",
    0x00087E2C: "secoc_queue_payload_getter",
    0x00087E8E: "secoc_queue_remove_and_clear",
    0x0008865A: "secoc_secured_pdu_ingress",
    0x00088702: "secoc_pending_or_retry_to_verify",
    0x000CB246: "b6_application_sequence_delta",
    0x000CB4F4: "b6_sequence_scaled_target_plausibility",
    0x000CBE6E: "b6_target_lateral_id_decoder",
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
        "schema": "corolla-h-b6-competing-sender-decompiler-evidence-v1",
        "software_id": "8965H1202000",
        "generator": {"path": rel(GENERATOR), "sha256": sha(GENERATOR.read_bytes())},
        "image": {"path": rel(args.image), "size": len(image), "sha256": sha(image)},
        "source_corpus": {"path": rel(args.corpus), "sha256": sha(args.corpus.read_bytes())},
        "function_count": len(functions),
        "functions": functions,
        "boundary": (
            "Exact-H disposable-project decompilations for protected-B6 queue ingress/coalescing, "
            "successful COM shadow delivery, application sequence handling, target-plausibility use, "
            "and Target Lateral ID decode. Every body is raw-byte-bound to 8965H1202000. The companion "
            "tracked SecOC-verification artifact remains authoritative for freshness reconstruction, CMAC, "
            "commit ordering, and key/profile selection."
        ),
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    print(f"wrote {args.out}: {len(functions)} functions")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
