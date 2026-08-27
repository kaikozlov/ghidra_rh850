#!/usr/bin/env python3
"""Promote compact H decompiler evidence for the openpilot state-interface bridge.

The source corpus is disposable workspace state.  The tracked output binds each
recovered pseudocode observation to exact 8965H1202000 CodeFlash bytes so portable
verification can use the firmware body hashes without depending on disposable workspace state.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from corolla_h_constants import CODEFLASH as H_CODEFLASH

REPO = Path(__file__).resolve().parents[1]
DEFAULT_IMAGE = H_CODEFLASH
DEFAULT_OUT = REPO / "data/generated/corolla_8965H1202000_openpilot_state_bridge_decompiler_evidence.json"

ENTRIES = [
    0x3738C,  # system fault-bit dispatcher feeding the 0x351 electrical monitor gate
    0x46C4C,  # torque/current plus 0x030/0x4A3 fault and validity source preparation
    0x46D9A,  # 0x4A3 staging producer
    0x46E0C,  # 0x351 seven-count debounce/hold helper
    0x46E62,  # 0x351 status/flag staging producer
    0x46E96,  # 0x394 table projection
    0x47188,  # GP-relative 0x030 driver-torque/status/Q-current staging producer
    0x472E0,  # writes the 0x351 electrical-monitor enable marker
    0x47430,  # GP-relative 0x030 status-code staging producer
    0x4749A,  # 0x4A3 packer
    0x47ADA,  # 0x394 packer
    0x47BA2,  # 0x351 packer
    0x4B692,  # Dem event-class aggregator consumed by the 0x394 classifier
    0x4B780,  # 0x394 classifier event-latch updater
    0x4B7AA,  # 0x394 classifier operational helper
    0x4B7D4,  # 0x394 event-latch aging helper
    0x4B836,  # 0x394 secondary latch aging helper
    0x4B880,  # 0x394 latch-aging coordinator
    0x4B8D2,  # 0x394 internal-validity helper
    0x4B930,  # 0x394 fault-input latch helper
    0x4B9AE,  # actual 17-state 0x394 fault/status classifier
    0x5262C,  # snapshot copy proving DID 0x1033 starts from FEBE7D1B
    0x6387C,  # signed byte saturation helper used by 0x4A3 B5
    0xB87E8,  # 0x351 upstream electrical-fault debounce and Dem event-4 reporter
    0xBAC16,  # DID 0x1033 Ready Status intermediate snapshot
    0xBBA48,  # DID 0x1033 Ready Status diagnostic snapshot publication
]


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load_corpus(path: Path) -> dict[int, dict]:
    rows: dict[int, dict] = {}
    with path.open() as f:
        for line in f:
            row = json.loads(line)
            if row.get("record") == "function":
                rows[int(row["entry_addr"], 16)] = row
    return rows


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--corpus", type=Path, required=True,
                    help="disposable corrected-context H decompiler corpus JSONL")
    ap.add_argument("--image", type=Path, default=DEFAULT_IMAGE)
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = ap.parse_args()
    corpus_path = args.corpus.resolve()
    image_path = args.image.resolve()

    corpus = load_corpus(corpus_path)
    image = image_path.read_bytes()
    if len(image) != 0x100000:
        raise SystemExit(f"expected 1 MiB normalized image, got {len(image):#x}")

    functions = []
    for entry in ENTRIES:
        row = corpus.get(entry)
        if row is None or not row.get("decompile_completed"):
            raise SystemExit(f"missing completed decompilation for 0x{entry:08X}")
        size = int(row["body_size"])
        body = image[entry:entry + size]
        text = row["decompiled_c"]
        if len(body) != size:
            raise SystemExit(f"function body outside image: 0x{entry:08X}")
        functions.append({
            "entry": f"0x{entry:08X}",
            "body_size": size,
            "body_sha256": sha(body),
            "decompiled_c_sha256": sha(text.encode()),
            "decompiled_c": text,
        })

    payload = {
        "schema": "corolla-h-openpilot-state-bridge-decompiler-evidence-v2",
        "software_id": "8965H1202000",
        "image": {
            "path": str(image_path.relative_to(REPO)) if image_path.is_relative_to(REPO) else str(image_path),
            "sha256": sha(image),
            "size": len(image),
        },
        "source_corpus": {
            "path": str(corpus_path.relative_to(REPO)) if corpus_path.is_relative_to(REPO) else str(corpus_path),
            "sha256": sha(corpus_path.read_bytes()),
            "function_count": len(corpus),
        },
        "functions": functions,
        "function_count": len(functions),
        "boundary": (
            "Target-native decompiler evidence for H 0x030/0x4A3/0x351/0x394 state-message recovery and the DID 0x1033 Ready Status oracle. "
            "Raw body hashes are the firmware identity authority; structural Sienna matches are only corroboration."
        ),
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
