#!/usr/bin/env python3
"""Decode UtilityNeo encrypted scripts and the separate ASCII registry.

Scripts have a four-byte wrapper and BOM-marked UTF-16 text. The registry
has four ASCII CSV columns and a terminal 0,0,0,0 row. Both use AES-256-ECB.
Offline decoding strictly validates PKCS#7; the current native wrapper instead
zeros the final-byte count without checking the preceding padding bytes.
"""
from __future__ import annotations

import argparse
import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path

from Crypto.Cipher import AES

SRP_AES_KEY = b"bCVaAQnA3fNdDgdls2Cjar5er8iwP4Xz"
SRP_WRAPPER = b"H\x02H\x02"
SRP_REGISTRY_SENTINEL = "0,0,0,0\r\n"
_REGISTRY_ROW = re.compile(r"([0-9]+),([\x20-\x2b\x2d-\x7e]+),([0-9]+),([01])\r\n", re.ASCII)


@dataclass(frozen=True)
class SRPRegistration:
    """Source fields: column3 selects decryption; column4 is parsed but unused."""

    function_id: int
    script_stem: str
    column3: int
    column4: int


@dataclass(frozen=True)
class SRPRegistry:
    """All registrations, the explicit sentinel, and lossless decoded text."""

    registrations: tuple[SRPRegistration, ...]
    sentinel: SRPRegistration
    text: str


def _decrypt_payload(ciphertext: bytes) -> bytes:
    if not ciphertext or len(ciphertext) % AES.block_size:
        raise ValueError("SRP ciphertext must be a non-empty AES-block multiple")
    plaintext = AES.new(SRP_AES_KEY, AES.MODE_ECB).decrypt(ciphertext)
    padding = plaintext[-1]
    if padding == 0 or padding > AES.block_size or plaintext[-padding:] != bytes([padding]) * padding:
        raise ValueError("SRP plaintext has invalid PKCS#7 padding")
    plaintext = plaintext[:-padding]
    return plaintext


def decrypt_srp_bytes(ciphertext: bytes) -> str:
    """Decode only a wrapped, BOM-marked script; never auto-detect a registry."""
    plaintext = _decrypt_payload(ciphertext)
    if not plaintext.startswith(SRP_WRAPPER):
        raise ValueError("SRP plaintext has unexpected wrapper")
    body = plaintext[len(SRP_WRAPPER):]
    if not body.startswith((b"\xff\xfe", b"\xfe\xff")):
        raise ValueError("SRP body is not BOM-marked UTF-16")
    return body.decode("utf-16")


def decrypt_srp(path: Path) -> str:
    return decrypt_srp_bytes(path.read_bytes())


def decrypt_srp_registry_bytes(ciphertext: bytes) -> SRPRegistry:
    """Decode the distinct ASCII/CRLF registry with a required final sentinel.

    This strict offline grammar requires exactly four comma-separated fields:
    decimal FunctionID, nonempty printable ASCII stem, decimal column3, bit column4.
    The native scanf/tokenizer is more permissive about whitespace and integers.
    No script parsing or execution is performed.
    """
    text = _decrypt_payload(ciphertext).decode("ascii")
    if not text.endswith(SRP_REGISTRY_SENTINEL):
        raise ValueError("SRP registry has no terminal 0,0,0,0 sentinel")
    registrations = []
    offset = 0
    while offset < len(text):
        match = _REGISTRY_ROW.match(text, offset)
        if match is None:
            raise ValueError("SRP registry row must contain four ASCII CSV fields and CRLF")
        function_id, script_stem, column3, column4 = match.groups()
        row = SRPRegistration(int(function_id), script_stem, int(column3), int(column4))
        offset = match.end()
        if row.function_id == 0:
            if match.group() != SRP_REGISTRY_SENTINEL or offset != len(text):
                raise ValueError("SRP registry sentinel must be the last and exact 0,0,0,0 row")
            return SRPRegistry(tuple(registrations), row, text)
        registrations.append(row)
    raise ValueError("SRP registry has no sentinel")


def decrypt_srp_registry(path: Path) -> SRPRegistry:
    return decrypt_srp_registry_bytes(path.read_bytes())


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("srp", type=Path, help="encrypted .srp script or UtilityNeo.srplst registry")
    parser.add_argument("--format", choices=("script", "registry"), default="script",
                        help="explicit plaintext format (default: strict script)")
    parser.add_argument("-o", "--output", type=Path, help="write decoded XML or registry JSON instead of stdout")
    args = parser.parse_args()
    if args.format == "registry":
        text = json.dumps(asdict(decrypt_srp_registry(args.srp)), indent=2) + "\n"
    else:
        text = decrypt_srp(args.srp)
    if args.output:
        args.output.write_text(text, encoding="utf-8")
    else:
        print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
