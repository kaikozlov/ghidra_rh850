#!/usr/bin/env python3
"""Decode a reassembled Camry TSS3 Operation-FFD EB13 response.

Input is the diagnostic PDU after ISO-TP reassembly, beginning with EB 13.
This tool is offline only; it does not contact the vehicle.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from tools.techstream import tss3_operation_ffd as recorder


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--hex", help="reassembled EB13 PDU as hexadecimal")
    source.add_argument("--file", type=Path, help="file containing raw bytes or ASCII hex")
    parser.add_argument("--only", action="append", type=lambda value: int(value, 16),
                        help="decode only this hexadecimal recorder DID (repeatable)")
    parser.add_argument("--out", type=Path, help="write JSON here instead of stdout")
    args = parser.parse_args()

    if args.hex is not None:
        pdu = bytes.fromhex(args.hex)
    else:
        raw = args.file.read_bytes()
        try:
            pdu = bytes.fromhex(raw.decode().strip())
        except (UnicodeDecodeError, ValueError):
            pdu = raw

    result = recorder.decode_eb13(pdu, only=set(args.only) if args.only else None)
    rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(rendered)
    else:
        print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
