#!/usr/bin/env python3
"""Promote exact F33 boot flash-control decompiler evidence."""
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
IMAGE = REPO / "community/kai/camry-2026/normalized/8965F3307000_CodeFlash.bin"
OUT = REPO / "data/generated/camry_8965F3307000_flash_backend_evidence.json"
ENTRIES = [0x78BFA, 0x78C30, 0x78CE6, 0x78E2A, 0x79026]


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--image', type=Path, default=IMAGE)
    ap.add_argument('--corpus', type=Path, required=True)
    ap.add_argument('--out', type=Path, default=OUT)
    a = ap.parse_args()
    image = a.image.read_bytes()
    if len(image) != 0x100000:
        raise SystemExit(f'expected 1 MiB CodeFlash, got {len(image):#x}')
    rows = {}
    for line in a.corpus.open(encoding='utf-8'):
        row = json.loads(line)
        if row.get('record') == 'function':
            rows[int(row['entry_addr'], 16)] = row
    funcs = []
    for entry in ENTRIES:
        row = rows.get(entry)
        if not row or not row.get('decompile_completed') or not row.get('decompiled_c'):
            raise SystemExit(f'missing complete decompile 0x{entry:X}')
        size = int(row['body_size'])
        body = image[entry:entry + size]
        if len(body) != size:
            raise SystemExit(f'function outside image 0x{entry:X}')
        text = row['decompiled_c']
        funcs.append({
            'entry': f'0x{entry:08X}',
            'body_size': size,
            'body_sha256': sha(body),
            'decompiled_c_sha256': sha(text.encode()),
            'decompiled_c': text,
        })
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
