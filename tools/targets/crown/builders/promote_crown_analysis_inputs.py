#!/usr/bin/env python3
"""Materialize canonical physical CodeFlash/DataFlash for the mruno Crown EPS target."""
from __future__ import annotations

import argparse
import hashlib
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
RAW_CODEFLASH = REPO / "community/mruno/partial_codeflash_00000000_00200000_20260913-220010_2075572of2097152.bin"
RAW_DATAFLASH = REPO / "community/mruno/crown-eps-dataflash-dump-20260913.bin"
OUT_DIR = REPO / "firmware/crown-8965F3012000"
OUT_CODEFLASH = OUT_DIR / "CodeFlash.bin"
OUT_DATAFLASH = OUT_DIR / "DataFlash.bin"

RAW_CODEFLASH_SHA = "d4952d5aeb385709d6705750b59bbce46b06cc56790c09e361a7c83e746f6560"
RAW_DATAFLASH_SHA = "0c7b027900d4ac12a4e665e17c0575d44efb0ccfbcb6239416a40c8260c50872"
CODEFLASH_SHA = "5b89fdbc69edc2f66ef8a557f88b08c758e3146bd4e90067320d7966812b1273"
DATAFLASH_SHA = RAW_DATAFLASH_SHA
RECEIVED_BYTES = 2_075_572
PHYSICAL_CODEFLASH_SIZE = 0x100000
HOST_RANGE_SIZE = 0x200000


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def build() -> tuple[bytes, bytes]:
    raw = RAW_CODEFLASH.read_bytes()
    if len(raw) != HOST_RANGE_SIZE or sha256(raw) != RAW_CODEFLASH_SHA:
        raise SystemExit("mruno Crown CodeFlash source identity drift")
    # The collector saved a fixed 2-MiB host buffer after receiving 2,075,572 bytes.
    # The populated physical CodeFlash is the complete lower 1 MiB. The received
    # upper-host-range bytes are erased 0xFF; only the unreceived trailing interval
    # is zero-filled collector state and must never become canonical firmware.
    if set(raw[PHYSICAL_CODEFLASH_SIZE:RECEIVED_BYTES]) != {0xFF}:
        raise SystemExit("unexpected non-FF data in received upper CodeFlash host range")
    if set(raw[RECEIVED_BYTES:]) != {0x00}:
        raise SystemExit("unexpected bytes in unreceived CodeFlash host-buffer tail")
    codeflash = raw[:PHYSICAL_CODEFLASH_SIZE]
    if sha256(codeflash) != CODEFLASH_SHA:
        raise SystemExit("normalized Crown CodeFlash identity drift")

    dataflash = RAW_DATAFLASH.read_bytes()
    if len(dataflash) != 0x8000 or sha256(dataflash) != RAW_DATAFLASH_SHA:
        raise SystemExit("mruno Crown DataFlash source identity drift")
    return codeflash, dataflash


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()
    codeflash, dataflash = build()
    outputs = ((OUT_CODEFLASH, codeflash, CODEFLASH_SHA), (OUT_DATAFLASH, dataflash, DATAFLASH_SHA))
    for path, data, digest in outputs:
        assert sha256(data) == digest
        if args.check:
            if not path.is_file() or path.read_bytes() != data:
                raise SystemExit(f"canonical target input drift: {path.relative_to(REPO)}")
            print(f"checked {path.relative_to(REPO)} ({len(data)} bytes)")
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
            print(f"wrote {path.relative_to(REPO)} ({len(data)} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
