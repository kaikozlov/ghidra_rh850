#!/usr/bin/env python3
"""Extract a compact direct-text reference census from a target-native corpus.

The result is deliberately a *bounded direct-reference* evidence layer. It
records every decompiled function whose C contains one of the requested exact
substrings, plus the matching lines and raw function-body SHA-256. It does not
claim to detect computed-pointer/alias-only accesses.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def display_path(path: Path, root: Path) -> str:
    try:
        return str(path.resolve().relative_to(root.resolve()))
    except ValueError:
        return str(path)


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--image", type=Path, required=True)
    p.add_argument("--corpus", type=Path, required=True)
    p.add_argument("--software-id", required=True)
    p.add_argument("--term", action="append", default=[], metavar="NAME=SUBSTRING")
    p.add_argument("--out", type=Path, required=True)
    args = p.parse_args()
    root = Path(__file__).resolve().parents[1]
    image = args.image.read_bytes()
    if len(image) != 0x100000:
        raise SystemExit(f"expected 1 MiB CodeFlash, got {len(image):#x}")
    terms: dict[str, str] = {}
    for item in args.term:
        if "=" not in item:
            raise SystemExit(f"bad --term {item!r}; expected NAME=SUBSTRING")
        name, value = item.split("=", 1)
        if not name or not value or name in terms:
            raise SystemExit(f"bad/duplicate --term {item!r}")
        terms[name] = value.lower()
    if not terms:
        raise SystemExit("at least one --term is required")

    matches = {name: [] for name in terms}
    for line in args.corpus.read_text(encoding="utf-8").splitlines():
        record = json.loads(line)
        entry_raw = record.get("entry_addr")
        code = record.get("decompiled_c", "")
        if entry_raw is None or not code:
            continue
        entry = int(entry_raw, 16)
        size = int(record["body_size"])
        body = image[entry : entry + size]
        if len(body) != size:
            raise SystemExit(f"function body outside image: {entry:#x}+{size:#x}")
        code_lines = code.splitlines()
        for name, needle in terms.items():
            hit_lines = [text.strip() for text in code_lines if needle in text.lower()]
            if hit_lines:
                matches[name].append({
                    "entry": f"0x{entry:08X}",
                    "body_size": size,
                    "body_sha256": sha256(body),
                    "matching_lines": hit_lines,
                })

    payload = {
        "schema": "rh850-variant-decompiler-direct-reference-census-v1",
        "evidence_boundary": "Complete exact-substring census over the supplied target-native decompiler corpus; bounded to direct textual references and does not exclude computed-pointer or alias-only accesses.",
        "software_id": args.software_id,
        "image": {
            "path": display_path(args.image, root),
            "size": len(image),
            "sha256": sha256(image),
        },
        "source_corpus": {
            "path": display_path(args.corpus, root),
            "sha256": sha256(args.corpus.read_bytes()),
        },
        "terms": {
            name: {"substring": value, "match_count": len(matches[name]), "matches": matches[name]}
            for name, value in terms.items()
        },
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"wrote {args.out}: {len(terms)} terms")
    for name in terms:
        print(f"  {name}: {len(matches[name])} functions")


if __name__ == "__main__":
    main()
