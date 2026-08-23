#!/usr/bin/env python3
"""Compact target-native H system/orchestration decompilation evidence.

Application function boundaries come from the clean disposable H corpus.  The
reset decision at 0x1F2 is deliberately kept separate because Ghidra models its
body as non-contiguous; it is bound to fixed raw windows rather than a bogus
contiguous body hash.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
H_RAW = ROOT / "community/albinoelephant/raw-20260818/albinoelephant-corolla-2023.20260814-0023/dump_codeflash_00000000_00200000_20260814-025814.bin"
APP_CORPUS = ROOT / "build/work/corpora/h_8965H1202000_rdbihelper2_decompilations.jsonl"
BOOT_CORPUS = ROOT / "build/work/corpora/h_8965H1202000_boot1f2_decompilations.jsonl"
OUT = ROOT / "data/generated/corolla_8965H1202000_system_orchestration_decompiler_evidence.json"

APP_FUNCS = [
    0x524B8, 0x52CE6, 0x52CFA, 0x52E4C, 0x52EEE, 0x52FEC,
    0x5316C, 0x5389C, 0x56970, 0x5701E, 0x5722E, 0x58450,
    0x5886A, 0x589A8, 0x58B3C, 0x5CAAC,
    0xB05D0, 0xB2692, 0xB8EE4, 0xBBA48, 0xBBFE6, 0xBD954,
    0xBDE28, 0xFDC14, 0xFDD40,
]
BOOT_WINDOWS = [
    (0x01F2, 0x60, "reset prologue/system synchronization"),
    (0x0320, 0xC0, "flash-controller status/consistency decision"),
    (0x03D8, 0x70, "FCU command/key sequence"),
    (0x0694, 0x98, "reset-marker validation and terminal decision"),
]


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load_corpus(path: Path) -> dict[int, dict]:
    out: dict[int, dict] = {}
    for line in path.read_text().splitlines():
        row = json.loads(line)
        if row.get("entry_addr"):
            out[int(row["entry_addr"], 16)] = row
    return out


def main() -> None:
    raw = H_RAW.read_bytes()
    if len(raw) < 0x100000:
        raise SystemExit(f"H dump too small: {len(raw):#x}")
    image = raw[:0x100000]
    app = load_corpus(APP_CORPUS)
    boot = load_corpus(BOOT_CORPUS)

    functions = []
    for entry in APP_FUNCS:
        row = app.get(entry)
        if row is None:
            raise SystemExit(f"missing app function {entry:#x}")
        if not row.get("decompile_completed") or not row.get("decompiled_c"):
            raise SystemExit(f"incomplete app decompilation {entry:#x}")
        size = int(row["body_size"])
        body = image[entry:entry + size]
        if len(body) != size:
            raise SystemExit(f"function outside image {entry:#x}+{size:#x}")
        code = row["decompiled_c"]
        functions.append({
            "entry": f"0x{entry:08X}",
            "name": row.get("name", f"FUN_{entry:08x}"),
            "body_size": size,
            "body_sha256": sha(body),
            "decompiled_c_sha256": sha(code.encode()),
            "decompiled_c": code,
        })

    reset = boot.get(0x1F2)
    if reset is None or not reset.get("decompile_completed") or not reset.get("decompiled_c"):
        raise SystemExit("missing forced H reset decision 0x1F2")
    reset_code = reset["decompiled_c"]
    windows = []
    for start, size, role in BOOT_WINDOWS:
        data = image[start:start + size]
        windows.append({
            "start": f"0x{start:08X}",
            "size": size,
            "sha256": sha(data),
            "role": role,
        })

    payload = {
        "schema": "corolla-h-system-orchestration-decompiler-evidence-v1",
        "software_id": "8965H1202000",
        "image": {
            "path": str(H_RAW.relative_to(ROOT)),
            "source_size": len(raw),
            "codeflash_size": len(image),
            "codeflash_sha256": sha(image),
        },
        "source_corpora": {
            "application": {
                "path": str(APP_CORPUS.relative_to(ROOT)),
                "sha256": sha(APP_CORPUS.read_bytes()),
                "boundary": "clean disposable H application corpus; used for application function boundaries",
            },
            "forced_reset": {
                "path": str(BOOT_CORPUS.relative_to(ROOT)),
                "sha256": sha(BOOT_CORPUS.read_bytes()),
                "boundary": "disposable corpus after forcing 0x1F2; used only for the non-contiguous reset-decision decompilation",
            },
        },
        "functions": functions,
        "function_count": len(functions),
        "reset_0x1f2": {
            "entry": "0x000001F2",
            "ghidra_reported_body_size": int(reset["body_size"]),
            "body_boundary": "non-contiguous; do not interpret reported body_size as a contiguous firmware range",
            "decompiled_c_sha256": sha(reset_code.encode()),
            "decompiled_c": reset_code,
            "raw_windows": windows,
        },
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(f"wrote {OUT}: {len(functions)} contiguous functions + reset 0x1F2")


if __name__ == "__main__":
    main()
