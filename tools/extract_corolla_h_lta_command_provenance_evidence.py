#!/usr/bin/env python3
"""Extract compact H-native evidence for Corolla H lateral-command provenance.

This deliberately does not rename the foreign Ghidra project.  It binds the
already-generated target-native decompiler corpus to the exact 8965H1202000
CodeFlash bytes so the semantic provenance report can remain deterministic.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
DEFAULT_CORPUS = REPO / "build/h_8965H1202000_decompilations.corrected-context.raw.jsonl"
DEFAULT_IMAGE = REPO / "build/community-normalized/8965H1202000_CodeFlash.bin"
DEFAULT_OUT = REPO / "data/generated/corolla_8965H1202000_lta_command_provenance_decompiler_evidence.json"

# Initialization / retained LTA command path / final command composition / COM APIs.
ENTRIES = [
    0x4636A,  # shared CAN025 steering-sensor unpacker
    0x46A10,  # H 0B6 scalar unpacker
    0x5262C,  # generated COM staging publication including F126/F127...
    0x7643A,  # scalar Com_ReceiveSignal-like helper
    0x7636C,  # full-PDU copy helper
    0x77A3A,  # block/group signal copy helper
    0xB8EEC,  # generated staging -> steering snapshot copier
    0xC2176,  # CAN025 coarse angle + fraction reconstruction
    0xC584A,  # local assist contributor initialization
    0xC5932,  # local assist contribution BD0E
    0xC97A8,  # retained LTA state initialization
    0xC9C16,  # retained LTA magnitude vote/rate-limit
    0xC9CD2,  # retained LTA wrapper
    0xCB07C,  # C26D-derived enable status
    0xCB1C8,  # retained LTA mode-source initialization
    0xCB2E0,  # CAN025 steering-rate magnitude threshold logic
    0xCB670,  # retained LTA decoded-mode initialization
    0xCB68A,  # cyclic decoded-mode wrapper
    0xCB696,  # retained LTA command-state initialization
    0xCB6CA,  # retained LTA command-state reset
    0xCB8BA,  # retained LTA command select
    0xCB9B6,  # retained LTA command slew/gain/limit -> C2A8
    0xCBA40,  # retained LTA command wrapper
    0xCBE6E,  # decoded LTA mode selector
    0xCBD7E,  # CAN025 angle/rate plausibility consumer
    0xCCE8C,  # H-local assist contribution C358
    0xCD1E8,  # H-local assist precursor C392
    0xCD3CC,  # secondary/final command composition
    0xCD440,  # final command gain/clip
    0xCD496,  # final command slew stage
    0xCD53E,  # final command bound
    0xCD55A,  # internal command-torque precursor composition
    0xCD5DC,  # torque/current gate and limit
    0xCE974,  # active steering pipeline owner
    0xCEB8E,  # steering-state initialization owner
    0xCEDAE,  # steering supervisor owner
]


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load_corpus(path: Path) -> dict[int, dict]:
    out: dict[int, dict] = {}
    with path.open() as f:
        for line in f:
            row = json.loads(line)
            if row.get("record") == "function":
                out[int(row["entry_addr"], 16)] = row
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--corpus", type=Path, default=DEFAULT_CORPUS)
    ap.add_argument("--image", type=Path, default=DEFAULT_IMAGE)
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = ap.parse_args()

    corpus = load_corpus(args.corpus)
    image = args.image.read_bytes()
    funcs = []
    for entry in ENTRIES:
        row = corpus.get(entry)
        if row is None:
            raise SystemExit(f"missing 0x{entry:08X} in {args.corpus}")
        if not row.get("decompile_completed"):
            raise SystemExit(f"decompile incomplete at 0x{entry:08X}")
        size = int(row["body_size"])
        body = image[entry:entry + size]
        if len(body) != size:
            raise SystemExit(f"body outside image at 0x{entry:08X}")
        c = row["decompiled_c"]
        funcs.append({
            "entry": f"0x{entry:08X}",
            "body_size": size,
            "body_sha256": sha(body),
            "decompiled_c_sha256": sha(c.encode()),
            "decompiled_c": c,
        })

    out = {
        "schema": "corolla-h-lta-command-provenance-decompiler-evidence-v1",
        "software_id": "8965H1202000",
        "image": {
            "path": str(args.image.relative_to(REPO)),
            "size": len(image),
            "sha256": sha(image),
        },
        "corpus": str(args.corpus.relative_to(REPO)),
        "function_count": len(funcs),
        "functions": funcs,
        "evidence_boundary": (
            "Target-native decompiler observations are raw-body SHA-bound to exact H CodeFlash. "
            "Direct-reference negatives cover the tracked corpus plus explicit raw literal-pointer/API-call scans; "
            "they do not prove absence of arbitrary computed aliases or undocumented hardware/DMA writers."
        ),
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"out": str(args.out), "functions": len(funcs)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
