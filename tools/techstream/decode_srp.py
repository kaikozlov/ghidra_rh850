#!/usr/bin/env python3
"""Decode Techstream V18 UtilityNeo .srp files.

The pinned IT3UtilityNeoNK/EntranceDLL wrapper encrypts SRP bodies with
AES-256-ECB under a fixed 32-byte key.  Decrypted files carry a four-byte
wrapper followed by UTF-16 XML.
"""
from __future__ import annotations

import argparse
from pathlib import Path

from Crypto.Cipher import AES

SRP_AES_KEY = b"bCVaAQnA3fNdDgdls2Cjar5er8iwP4Xz"
SRP_WRAPPER = b"H\x02H\x02"


def decrypt_srp_bytes(ciphertext: bytes) -> str:
    if not ciphertext or len(ciphertext) % AES.block_size:
        raise ValueError("SRP ciphertext must be a non-empty AES-block multiple")
    plaintext = AES.new(SRP_AES_KEY, AES.MODE_ECB).decrypt(ciphertext)
    padding = plaintext[-1]
    if padding == 0 or padding > AES.block_size or plaintext[-padding:] != bytes([padding]) * padding:
        raise ValueError("SRP plaintext has invalid PKCS#7 padding")
    plaintext = plaintext[:-padding]
    if not plaintext.startswith(SRP_WRAPPER):
        raise ValueError("SRP plaintext has unexpected wrapper")
    body = plaintext[len(SRP_WRAPPER):]
    if not body.startswith((b"\xff\xfe", b"\xfe\xff")):
        raise ValueError("SRP body is not BOM-marked UTF-16")
    return body.decode("utf-16")


def decrypt_srp(path: Path) -> str:
    return decrypt_srp_bytes(path.read_bytes())


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("srp", type=Path, help="encrypted .srp file")
    parser.add_argument("-o", "--output", type=Path, help="write decoded XML instead of stdout")
    args = parser.parse_args()
    text = decrypt_srp(args.srp)
    if args.output:
        args.output.write_text(text, encoding="utf-8")
    else:
        print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
