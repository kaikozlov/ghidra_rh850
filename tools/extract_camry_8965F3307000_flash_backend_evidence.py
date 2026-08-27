#!/usr/bin/env python3
"""Promote exact F33 boot flash-control decompiler evidence."""
from __future__ import annotations
import argparse, json
from pathlib import Path
from camry_f33_corpus import CORPUS, IMAGE, IMAGE_SHA256, body_bytes, display_path
from decompiler_evidence import bind_entries, bind_function, load_function_corpus, require_function, sha256_bytes

REPO = Path(__file__).resolve().parents[1]
OUT = REPO / "data/generated/camry_8965F3307000_flash_backend_evidence.json"
ENTRIES = [0x78BFA, 0x78C30, 0x78CE6, 0x78E2A, 0x79026]


def sha(b: bytes) -> str:
    return sha256_bytes(b)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--image', type=Path, default=IMAGE)
    ap.add_argument('--corpus', type=Path, default=CORPUS)
    ap.add_argument('--out', type=Path, default=OUT)
    a = ap.parse_args()
    image = a.image.read_bytes()
    if len(image) != 0x100000:
        raise SystemExit(f'expected 1 MiB CodeFlash, got {len(image):#x}')
    rows, _ = load_function_corpus(a.corpus)
    funcs = bind_entries(image, rows, ENTRIES)
    out = {
        'schema': 'camry-8965f3307000-flash-backend-evidence-v1',
        'software_id': '8965F3307000',
        'image': {'path': str(a.image.relative_to(REPO)), 'size': len(image), 'sha256': sha(image)},
        'source_corpus_sha256': sha(a.corpus.read_bytes()),
        'functions': funcs,
        'boundary': 'Exact F33 boot flash-control functions. Raw body hashes bind the decompiler observations to 8965F3307000; function names remain structural.',
    }
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(out, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    print(f'wrote {a.out}: {len(funcs)} functions')
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
