#!/usr/bin/env python3
"""Promote exact-H decompiler evidence for cooperative-authority wire visibility."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]
IMAGE = REPO / "community/albinoelephant/normalized/8965H1202000_CodeFlash.bin"
OUT = REPO / "data/generated/corolla_8965H1202000_cooperative_authority_wire_decompiler_evidence.json"
ENTRIES = [
    0x470C6,  # aggregate-mode status -> three 0x030 source cells
    0x4749A,  # 0x4A3 packer
    0x475D0,  # 0x4C8 constant packer
    0x4766A,  # 0x030 packer
    0x47ADA,  # 0x394 packer
    0x47BA2,  # 0x351 packer
    0x5262C,  # raw mode -> FEBEF000 staging
    0xB23A2,  # raw-mode-containing aggregate -> FEBEB118
    0xB8EEC,  # raw mode -> normalized FEBEACBD gate body (B8EE4 is overlapping prologue)
    0xBBA48,  # fixed-map FEBEB118 -> FEBEE887 copy
    0xC5156,  # first table-driven profile-gain family
    0xC51EA,  # first table-driven gain consumer
    0xC6D16,  # second table-driven profile-gain family
    0xC6DAA,  # second table-driven gain consumer
    0xCAF84,  # indirect dereference of profile flag pointer
    0xCBE6E,  # exact cooperative acceptance gate/derived flags
]


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def relative(path: Path) -> str:
    resolved = path.resolve()
    return str(resolved.relative_to(REPO.resolve())) if resolved.is_relative_to(REPO.resolve()) else str(resolved)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--image", type=Path, default=IMAGE)
    ap.add_argument("--corpus", type=Path, required=True,
                    help="disposable corrected-context H decompiler corpus JSONL")
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
        body = image[entry:entry + size]
        text = row["decompiled_c"]
        if len(body) != size:
            raise SystemExit(f"function body outside image 0x{entry:X}")
        functions.append({
            "entry": f"0x{entry:08X}",
            "body_size": size,
            "body_sha256": sha(body),
            "decompiled_c_sha256": sha(text.encode()),
            "decompiled_c": text,
        })

    payload = {
        "schema": "corolla-h-cooperative-authority-wire-decompiler-evidence-v1",
        "software_id": "8965H1202000",
        "image": {"path": relative(args.image), "size": len(image), "sha256": sha(image)},
        "source_corpus": {
            "path": relative(args.corpus),
            "sha256": sha(args.corpus.read_bytes()),
            "function_count": len(rows),
        },
        "function_count": len(functions),
        "functions": functions,
        "boundary": (
            "Target-native exact-H decompiler evidence for the normalized cooperative gate, the only recovered raw-mode-to-wire alias, "
            "the two CodeFlash-table/fixed-GP profile-gain consumers, and all five normal Tx packers. Raw body hashes bind every promoted "
            "pseudocode body to exact 8965H1202000 bytes. Mutable runtime pointers, DMA/peripheral mutation, and physical actuator response "
            "are not negative-proof targets."
        ),
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(f"wrote {args.out}: {len(functions)} functions")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
