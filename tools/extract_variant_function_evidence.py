#!/usr/bin/env python3
"""Extract compact image-bound target-native Ghidra function evidence.

This is a provenance/compaction helper, not a semantic classifier. It copies the
selected target-native decompilations into a tracked JSON artifact and binds each
record to the exact raw CodeFlash body with SHA-256. Downstream deterministic
analysis may therefore consume the small evidence set without committing a full
disposable Ghidra corpus.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def parse_int(value: str) -> int:
    return int(value, 0)


def display_path(path: Path, root: Path) -> str:
    resolved = path.resolve()
    try:
        return str(resolved.relative_to(root.resolve()))
    except ValueError:
        return str(path)


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--image", type=Path, required=True)
    p.add_argument("--corpus", type=Path, required=True)
    p.add_argument("--software-id", required=True)
    p.add_argument("--address", type=parse_int, action="append", default=[])
    p.add_argument("--out", type=Path, required=True)
    args = p.parse_args()

    root = Path(__file__).resolve().parents[1]
    image = args.image.read_bytes()
    if len(image) != 0x100000:
        raise SystemExit(f"expected 1 MiB CodeFlash, got {len(image):#x}")
    wanted = set(args.address)
    if not wanted:
        raise SystemExit("at least one --address is required")

    selected: dict[int, dict] = {}
    for line in args.corpus.read_text(encoding="utf-8").splitlines():
        record = json.loads(line)
        raw_entry = record.get("entry_addr")
        if raw_entry is None:
            continue
        entry = int(raw_entry, 16)
        if entry in wanted:
            selected[entry] = record

    missing = sorted(wanted - selected.keys())
    if missing:
        raise SystemExit("missing selected functions: " + ", ".join(f"0x{x:X}" for x in missing))

    functions = []
    for entry in sorted(wanted):
        record = selected[entry]
        size = int(record["body_size"])
        code = record.get("decompiled_c", "")
        if not record.get("decompile_completed", False) or not code:
            raise SystemExit(f"incomplete target-native decompilation at {entry:#x}")
        body = image[entry : entry + size]
        if len(body) != size:
            raise SystemExit(f"function outside CodeFlash: {entry:#x}+{size:#x}")
        functions.append({
            "entry": f"0x{entry:08X}",
            "body_size": size,
            "body_sha256": sha256(body),
            "decompiled_c_sha256": sha256(code.encode("utf-8")),
            "decompiled_c": code,
        })

    payload = {
        "schema": "rh850-variant-function-decompiler-evidence-v1",
        "software_id": args.software_id,
        "image": {
            "path": display_path(args.image, root),
            "size": len(image),
            "sha256": sha256(image),
        },
        "source_corpus": {
            "path": display_path(args.corpus, root),
            "sha256": sha256(args.corpus.read_bytes()),
            "note": "Disposable target-native Ghidra corpus; provenance only. Downstream checks use the compact image-bound records.",
        },
        "function_count": len(functions),
        "functions": functions,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"wrote {args.out}: {len(functions)} functions")


if __name__ == "__main__":
    main()
