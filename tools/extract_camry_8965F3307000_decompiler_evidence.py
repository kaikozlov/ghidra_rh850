#!/usr/bin/env python3
"""Promote exact 8965F3307000 target-native decompiler evidence."""
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
IMAGE = REPO / "community/kai/camry-2026/normalized/8965F3307000_CodeFlash.bin"
OUT = REPO / "data/generated/camry_8965F3307000_decompiler_evidence.json"
ENTRIES = [
    # Target-native COM/diagnostic steering-angle ingress.
    0x47AE0, 0x4B59E, 0x4BD46, 0x4DBF8, 0x58074, 0x6A5FA, 0x7D12A,
    # Target-native SecOC receive/ICU-S verify path.
    0x8A8E4, 0x8ECB2, 0x8ED14, 0x8EE7C, 0x8F2B0, 0x8F34A, 0x8F434, 0x8F676, 0x8F746,
    # Measured-angle reconstruction, B6 staging, target conditioner/comparator.
    0xB39D8, 0xB3B06, 0xBCD66, 0xCB73A, 0xCCF0E, 0xCCFB6, 0xCD128, 0xCE9EA, 0xCEADA, 0xCEE80, 0xCEFFC,
]

def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--image', type=Path, default=IMAGE)
    ap.add_argument('--corpus', type=Path, required=True, help='disposable target-native Ghidra decompiler corpus JSONL')
    ap.add_argument('--out', type=Path, default=OUT)
    a = ap.parse_args()
    image = a.image.read_bytes()
    if len(image) != 0x100000:
        raise SystemExit(f'expected 1 MiB normalized CodeFlash, got {len(image):#x}')
    rows = {}
    for line in a.corpus.open(encoding='utf-8'):
        r = json.loads(line)
        if r.get('record') == 'function':
            rows[int(r['entry_addr'], 16)] = r
    funcs = []
    for entry in ENTRIES:
        r = rows.get(entry)
        if not r or not r.get('decompile_completed') or not r.get('decompiled_c'):
            raise SystemExit(f'missing complete decompile 0x{entry:X}')
        size = int(r['body_size'])
        body = image[entry:entry + size]
        text = r['decompiled_c']
        if len(body) != size:
            raise SystemExit(f'body outside image 0x{entry:X}')
        funcs.append({
            'entry': f'0x{entry:08X}',
            'body_size': size,
            'body_sha256': sha(body),
            'decompiled_c_sha256': sha(text.encode()),
            'decompiled_c': text,
        })
    out = {
        'schema': 'camry-8965f3307000-decompiler-evidence-v1',
        'software_id': '8965F3307000',
        'image': {
            'path': str(a.image.resolve().relative_to(REPO.resolve())) if a.image.resolve().is_relative_to(REPO.resolve()) else str(a.image),
            'size': len(image),
            'sha256': sha(image),
        },
        'source_corpus': {
            'path': str(a.corpus.resolve().relative_to(REPO.resolve())) if a.corpus.resolve().is_relative_to(REPO.resolve()) else str(a.corpus),
            'sha256': sha(a.corpus.read_bytes()),
        },
        'function_count': len(funcs),
        'functions': funcs,
        'boundary': (
            'Target-native Camry decompiler observations for protected 00F/D7/B6 receive verification, '
            'B6 COM extraction/staging, target-native 0x025/DID1037 measured steering-angle feedback, and the signed B4:B5 target-angle controller chain. '
            'Raw body hashes bind every pseudocode row to exact 8965F3307000 bytes; OEM signal names are '
            'assigned only where the target-native consumer semantics close them.'
        ),
    }
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(out, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    print(f'wrote {a.out}: {len(funcs)} functions')
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
