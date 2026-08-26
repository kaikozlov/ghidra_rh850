#!/usr/bin/env python3
"""Extract compact exact-H evidence for the FEBE7C58 receive-validity monitor."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
IMAGE = REPO / "community/albinoelephant/normalized/8965H1202000_CodeFlash.bin"
OUT = REPO / "data/generated/corolla_8965H1202000_power_supply_monitor_decompiler_evidence.json"
ENTRIES = (
    0x44D84, 0x44EC2, 0x44FC4, 0x450FC,
    0x4516A, 0x451C4, 0x45212,
    0x45260, 0x45268, 0x45272, 0x4527A, 0x4528A, 0x4529A,
    # The corpus retains the overlapping 0xB8EE4 prologue and 0xB8EEC body
    # as separate functions.  Existing TMS-053 evidence carries the prologue;
    # this body pins the actual source-normalization/store instructions.
    0xB8EEC,
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
        functions.append({
            "entry": f"0x{entry:08X}",
            "body_size": size,
            "body_sha256": sha(image[entry:entry + size]),
            "decompiled_c_sha256": sha(row["decompiled_c"].encode()),
            "decompiled_c": row["decompiled_c"],
            "data_references": row.get("data_references", []),
        })

    census_specs = {
        "native_state": ("0xFEBE7C58", ("febe7c58", "-0x3ba8")),
        "snapshot_state": ("0xFEBEF000", ("febef000", "+ 0x3800")),
        "normalized_state": ("0xFEBEACBD", ("febeacbd", "-0xb43")),
    }
    census = {}
    for name, (address, terms) in census_specs.items():
        matches = []
        for entry, row in sorted(rows.items()):
            text = row.get("decompiled_c", "")
            lines = [line.strip() for line in text.splitlines()
                     if any(term.lower() in line.lower() for term in terms)]
            if lines:
                size = int(row["body_size"])
                matches.append({
                    "entry": f"0x{entry:08X}",
                    "body_size": size,
                    "body_sha256": sha(image[entry:entry + size]),
                    "matching_lines": lines,
                })
        census[name] = {
            "address": address,
            "terms": list(terms),
            "match_count": len(matches),
            "matches": matches,
        }

    rel_image = str(args.image.resolve().relative_to(REPO.resolve()))
    rel_corpus = str(args.corpus.resolve().relative_to(REPO.resolve()))
    out = {
        "schema": "corolla-h-power-supply-monitor-decompiler-evidence-v1",
        "software_id": "8965H1202000",
        "image": {"path": rel_image, "size": len(image), "sha256": sha(image)},
        "source_corpus": {"path": rel_corpus, "sha256": sha(args.corpus.read_bytes())},
        "function_count": len(functions),
        "functions": functions,
        "direct_text_reference_census": census,
        "boundary": (
            "Exact-H raw-body-bound decompilations plus a complete-corpus textual census for named and simple fixed-GP "
            "spellings. The census does not exclude arbitrary computed-pointer aliases. Diagnostic names are joined "
            "separately and do not name FEBE63A4, FEBE65E4, or FEBE7C5F."
        ),
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    print(f"wrote {args.out}: {len(functions)} functions")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
