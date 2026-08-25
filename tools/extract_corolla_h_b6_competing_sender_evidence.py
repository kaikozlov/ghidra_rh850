#!/usr/bin/env python3
"""Promote exact-H decompiler evidence for competing protected-B6 receiver arbitration."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
GENERATOR = Path(__file__).resolve()
IMAGE = REPO / "community/albinoelephant/normalized/8965H1202000_CodeFlash.bin"
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
    return hashlib.sha256(data).hexdigest()


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

    rows: dict[int, dict] = {}
    for line in args.corpus.open():
        row = json.loads(line)
        if row.get("record") == "function":
            rows[int(row["entry_addr"], 16)] = row

    functions = []
    for entry, role in ENTRIES.items():
        row = rows.get(entry)
        if not row or not row.get("decompile_completed") or not row.get("decompiled_c"):
            raise SystemExit(f"missing complete decompile 0x{entry:X}")
        size = int(row["body_size"])
        body = image[entry:entry + size]
        if len(body) != size:
            raise SystemExit(f"function body outside image 0x{entry:X}")
        text = row["decompiled_c"]
        functions.append({
            "entry": f"0x{entry:08X}",
            "role": role,
            "body_size": size,
            "body_sha256": sha(body),
            "decompiled_c_sha256": sha(text.encode()),
            "decompiled_c": text,
        })

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
