#!/usr/bin/env python3
"""Triage RH850 reprogramming/SecurityAccess secrets in foreign firmware.

This is an offline candidate-key verifier. It intentionally does not talk to a
vehicle or ECU. It supports the three recovered Toyota/Denso P1M-E EPS roots:

* payload-build root
* boot/programming SecurityAccess root
* application SecurityAccess root

Use the scan command on arbitrary firmware, sa-response to compute the expected
16-byte key for a known candidate root/data-record/seed tuple, and payload-key
to derive the image key for a candidate payload root.
"""
from __future__ import annotations

import argparse
import json
import re
from collections.abc import Iterable
from pathlib import Path

from Crypto.Cipher import AES
from Crypto.Hash import CMAC

BLOCK = 16

KNOWN_SECRETS = {
    "payload": bytes.fromhex("ba052435f8843f985fd1329d2b6117b0"),
    "boot": bytes.fromhex("f05f36b7d78c03e24ab4faef2a57d044"),
    "application": bytes.fromhex("893e08418c741ffa2a9c044bffa55813"),
}

BOOT_INFO_RE = re.compile(rb"BOOT INFO AREA[ -~]{0,64}")
RH850_PART_RE = re.compile(rb"R7F70[0-9A-Z]{4,10}")


def _parse_block(value: str, *, what: str) -> bytes:
    try:
        raw = bytes.fromhex(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(f"{what} must be hexadecimal bytes") from exc
    if len(raw) != BLOCK:
        raise argparse.ArgumentTypeError(
            f"{what} must be exactly {BLOCK} bytes, got {len(raw)}"
        )
    return raw


def _resolve_secret(value: str) -> bytes:
    key = value.lower()
    if key in KNOWN_SECRETS:
        return KNOWN_SECRETS[key]
    return _parse_block(value, what="secret")


def _storage_variants(secret: bytes) -> dict[str, bytes]:
    """Common byte layouts for a 128-bit constant in little-endian firmware."""
    words = [secret[i : i + 4] for i in range(0, BLOCK, 4)]
    variants = {
        "raw": secret,
        "reverse_all": secret[::-1],
        "reverse_each_u32": b"".join(word[::-1] for word in words),
        "reverse_u32_order": b"".join(reversed(words)),
    }
    out: dict[str, bytes] = {}
    seen: set[bytes] = set()
    for name, encoded in variants.items():
        if encoded not in seen:
            out[name] = encoded
            seen.add(encoded)
    return out


def _all_offsets(blob: bytes, needle: bytes) -> list[int]:
    out: list[int] = []
    start = 0
    while True:
        offset = blob.find(needle, start)
        if offset < 0:
            return out
        out.append(offset)
        start = offset + 1


def security_access_working_key(secret: bytes, data_record: bytes) -> bytes:
    """Recovered Toyota P1M-E first stage: AES-DEC(root, data_record)."""
    if len(secret) != BLOCK or len(data_record) != BLOCK:
        raise ValueError("secret and data_record must be 16 bytes")
    return AES.new(secret, AES.MODE_ECB).decrypt(data_record)


def security_access_response(secret: bytes, data_record: bytes, seed: bytes) -> bytes:
    """Recovered Toyota P1M-E second stage: AES-ENC(Kwork, seed)."""
    if len(seed) != BLOCK:
        raise ValueError("seed must be 16 bytes")
    working_key = security_access_working_key(secret, data_record)
    return AES.new(working_key, AES.MODE_ECB).encrypt(seed)


def payload_key(secret: bytes, seed_key: bytes) -> bytes:
    """Recovered Toyota P1M-E payload KDF: AES-ENC(payload_root, SeedKey)."""
    if len(secret) != BLOCK or len(seed_key) != BLOCK:
        raise ValueError("secret and SeedKey must be 16 bytes")
    return AES.new(secret, AES.MODE_ECB).encrypt(seed_key)


def _cmac(key: bytes, message: bytes) -> bytes:
    ctx = CMAC.new(key, ciphermod=AES)
    ctx.update(message)
    return ctx.digest()


def gm_security_access_response(secret: bytes, subfunction: int, seed: bytes) -> bytes:
    """Snipesy Global-B example: CMAC(root, subfn||seed), then CMAC(FF*16)[:12]."""
    if len(secret) != BLOCK:
        raise ValueError("secret must be 16 bytes")
    if not 0 <= subfunction <= 0xFF:
        raise ValueError("subfunction must fit in one byte")
    if len(seed) != 31:
        raise ValueError("GM seed must be exactly 31 bytes")
    intermediate = _cmac(secret, bytes([subfunction]) + seed)
    return _cmac(intermediate, bytes([0xFF]) * BLOCK)[:12]


def _ascii_matches(pattern: re.Pattern[bytes], blob: bytes) -> list[dict[str, object]]:
    out: list[dict[str, object]] = []
    seen: set[tuple[int, bytes]] = set()
    for match in pattern.finditer(blob):
        value = match.group(0).rstrip(b" \xff")
        item = (match.start(), value)
        if item in seen:
            continue
        seen.add(item)
        out.append(
            {
                "offset": f"0x{match.start():X}",
                "ascii": value.decode("ascii", errors="replace"),
            }
        )
    return out


def scan_image(path: Path) -> dict[str, object]:
    blob = path.read_bytes()
    hits = {
        name: {
            layout: [f"0x{x:X}" for x in _all_offsets(blob, encoded)]
            for layout, encoded in _storage_variants(secret).items()
        }
        for name, secret in KNOWN_SECRETS.items()
    }

    payload_boot_pair = KNOWN_SECRETS["payload"] + KNOWN_SECRETS["boot"]

    return {
        "path": str(path),
        "size": len(blob),
        "known_secret_hits": hits,
        "payload_boot_pair_hits": [
            f"0x{x:X}" for x in _all_offsets(blob, payload_boot_pair)
        ],
        "boot_info": _ascii_matches(BOOT_INFO_RE, blob),
        "rh850_part_strings": _ascii_matches(RH850_PART_RE, blob),
    }


def _print_scan(result: dict[str, object]) -> None:
    print(f"{result['path']} ({result['size']:#x} bytes)")
    hits = result["known_secret_hits"]
    assert isinstance(hits, dict)
    for name in ("payload", "boot", "application"):
        layouts = hits[name]
        raw = layouts["raw"]
        print(f"  {name:11}: {', '.join(raw) if raw else '-'}")
        for layout, offsets in layouts.items():
            if layout != "raw" and offsets:
                print(f"    {layout:17}: {', '.join(offsets)}")
    pair_hits = result["payload_boot_pair_hits"]
    print(f"  payload+boot pair: {', '.join(pair_hits) if pair_hits else '-'}")
    for item in result["boot_info"]:
        print(f"  boot-info       : {item['offset']}  {item['ascii']}")
    if not result["boot_info"]:
        for item in result["rh850_part_strings"]:
            print(f"  RH850 part      : {item['offset']}  {item['ascii']}")


def _cmd_scan(args: argparse.Namespace) -> int:
    results = [scan_image(Path(value)) for value in args.images]
    if args.json:
        print(json.dumps(results, indent=2, sort_keys=True))
    else:
        for index, result in enumerate(results):
            if index:
                print()
            _print_scan(result)
    return 0


def _cmd_sa_response(args: argparse.Namespace) -> int:
    secret = _resolve_secret(args.secret)
    data_record = _parse_block(args.data_record, what="data record")
    seed = _parse_block(args.seed, what="seed")
    working_key = security_access_working_key(secret, data_record)
    response = AES.new(working_key, AES.MODE_ECB).encrypt(seed)

    out = {
        "secret": secret.hex(),
        "data_record": data_record.hex(),
        "seed": seed.hex(),
        "working_key": working_key.hex(),
        "response": response.hex(),
    }
    if args.observed_key is not None:
        observed = _parse_block(args.observed_key, what="observed key")
        out["observed_key"] = observed.hex()
        out["matches_observed_key"] = observed == response

    if args.json:
        print(json.dumps(out, indent=2, sort_keys=True))
    else:
        for key, value in out.items():
            print(f"{key:20} {value}")
    return 0


def _cmd_gm_sa_response(args: argparse.Namespace) -> int:
    secret = _resolve_secret(args.secret)
    try:
        seed = bytes.fromhex(args.seed)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("GM seed must be hexadecimal bytes") from exc
    if len(seed) != 31:
        raise argparse.ArgumentTypeError(
            f"GM seed must be exactly 31 bytes, got {len(seed)}"
        )
    response = gm_security_access_response(secret, args.subfunction, seed)
    out: dict[str, object] = {
        "secret": secret.hex(),
        "subfunction": f"0x{args.subfunction:02x}",
        "seed": seed.hex(),
        "response": response.hex(),
    }
    if args.observed_key is not None:
        try:
            observed = bytes.fromhex(args.observed_key)
        except ValueError as exc:
            raise argparse.ArgumentTypeError(
                "observed GM key must be hexadecimal bytes"
            ) from exc
        if len(observed) != 12:
            raise argparse.ArgumentTypeError(
                f"observed GM key must be exactly 12 bytes, got {len(observed)}"
            )
        out["observed_key"] = observed.hex()
        out["matches_observed_key"] = observed == response

    if args.json:
        print(json.dumps(out, indent=2, sort_keys=True))
    else:
        for key, value in out.items():
            print(f"{key:20} {value}")
    return 0


def _cmd_payload_key(args: argparse.Namespace) -> int:
    secret = _resolve_secret(args.secret)
    seed_key = _parse_block(args.seed_key, what="SeedKey")
    derived = payload_key(secret, seed_key)
    out = {
        "secret": secret.hex(),
        "seed_key": seed_key.hex(),
        "payload_key": derived.hex(),
    }
    if args.json:
        print(json.dumps(out, indent=2, sort_keys=True))
    else:
        for key, value in out.items():
            print(f"{key:20} {value}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    scan = sub.add_parser("scan", help="scan arbitrary firmware for the known roots")
    scan.add_argument("images", nargs="+", help="firmware image(s) to scan")
    scan.add_argument("--json", action="store_true")
    scan.set_defaults(func=_cmd_scan)

    sa = sub.add_parser(
        "sa-response",
        help="compute/verify a candidate 16-byte two-stage AES SecurityAccess key",
    )
    sa.add_argument(
        "--secret",
        required=True,
        help="boot, application, payload, or an arbitrary 16-byte root in hex",
    )
    sa.add_argument("--data-record", required=True, help="16-byte request data in hex")
    sa.add_argument("--seed", required=True, help="16-byte ECU seed in hex")
    sa.add_argument(
        "--observed-key",
        help="optional 16-byte tester key from a transcript; reports exact match",
    )
    sa.add_argument("--json", action="store_true")
    sa.set_defaults(func=_cmd_sa_response)

    gm_sa = sub.add_parser(
        "gm-sa-response",
        help="test a candidate 16-byte root against the published GM Global-B 31-byte-seed algorithm",
    )
    gm_sa.add_argument(
        "--secret",
        required=True,
        help="boot, application, payload, or an arbitrary 16-byte root in hex",
    )
    gm_sa.add_argument(
        "--subfunction", type=lambda x: int(x, 0), default=1, help="requestSeed subfunction (default: 1)"
    )
    gm_sa.add_argument("--seed", required=True, help="31-byte seed from 67 01 in hex")
    gm_sa.add_argument(
        "--observed-key", help="optional accepted 12-byte 27 02 payload; reports exact match"
    )
    gm_sa.add_argument("--json", action="store_true")
    gm_sa.set_defaults(func=_cmd_gm_sa_response)

    payload = sub.add_parser(
        "payload-key",
        help="derive an image key from a candidate payload root and 16-byte SeedKey",
    )
    payload.add_argument(
        "--secret",
        default="payload",
        help="payload or an arbitrary 16-byte root in hex (default: payload)",
    )
    payload.add_argument("--seed-key", required=True, help="16-byte SeedKey in hex")
    payload.add_argument("--json", action="store_true")
    payload.set_defaults(func=_cmd_payload_key)

    return parser


def main(argv: Iterable[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(list(argv) if argv is not None else None)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
