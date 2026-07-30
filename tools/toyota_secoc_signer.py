#!/usr/bin/env python3
"""Build Toyota classic-CAN SecOC frames for the profile in 8965B4512000.

This is an independent implementation of the firmware-derived receive format:

    authenticated input = DataID_be16 || payload4 || freshness48
    freshness48         = trip16 || reset20 || message8 || reset_low2 || 00b
    wire trailer        = message_low2 || reset_low2 || CMAC_msb28

The synchronization frame uses:

    authenticated input = DataID_be16 || trip16 || reset20 || 0000b
    wire frame           = trip16 || reset20 || CMAC_msb28

The tool only constructs bytes; it does not recover keys or transmit CAN frames.
Use only a legitimately obtained 16-byte AES-128 key.

Examples:
    export TOYOTA_SECOC_KEY=000102030405060708090a0b0c0d0e0f
    uv run --locked python tools/toyota_secoc_signer.py sign \
        --can-id 0x2e4 --payload 00000000 --trip 1 --reset 2 --message 0
    uv run --locked python tools/toyota_secoc_signer.py sync \
        --trip 1 --reset 2
"""

from __future__ import annotations

import argparse
import os

from Crypto.Cipher import AES
from Crypto.Hash import CMAC

SYNC_CAN_ID = 0x00F
AES_128_KEY_BYTES = 16
CLASSIC_AUTHENTIC_PAYLOAD_BYTES = 4


def _require_uint(name: str, value: int, bits: int) -> None:
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"{name} must be an integer")
    maximum = (1 << bits) - 1
    if not 0 <= value <= maximum:
        raise ValueError(f"{name} must fit in {bits} bits (0..{maximum:#x}), got {value:#x}")


def _require_key(key: bytes) -> None:
    if not isinstance(key, bytes):
        raise TypeError("key must be bytes")
    if len(key) != AES_128_KEY_BYTES:
        raise ValueError(f"key must be exactly {AES_128_KEY_BYTES} bytes, got {len(key)}")


def _require_classic_can_id(can_id: int) -> None:
    _require_uint("can_id", can_id, 11)


def _cmac_msb28(key: bytes, authenticated_input: bytes) -> int:
    _require_key(key)
    cmac = CMAC.new(key, ciphermod=AES)
    cmac.update(authenticated_input)
    return int.from_bytes(cmac.digest()[:4], "big") >> 4


def pack_normal_freshness(
    trip_counter: int,
    reset_counter: int,
    message_counter: int,
) -> bytes:
    """Pack 46 meaningful freshness bits and two low padding bits."""
    _require_uint("trip_counter", trip_counter, 16)
    _require_uint("reset_counter", reset_counter, 20)
    _require_uint("message_counter", message_counter, 8)

    tail = (
        (reset_counter << 12)
        | (message_counter << 4)
        | ((reset_counter & 0x3) << 2)
    )
    return trip_counter.to_bytes(2, "big") + tail.to_bytes(4, "big")


def build_normal_authenticated_input(
    can_id: int,
    payload: bytes,
    trip_counter: int,
    reset_counter: int,
    message_counter: int,
) -> bytes:
    """Build DataID_be16 || payload4 || freshness48 for a classic frame."""
    _require_classic_can_id(can_id)
    if not isinstance(payload, bytes):
        raise TypeError("payload must be bytes")
    if len(payload) != CLASSIC_AUTHENTIC_PAYLOAD_BYTES:
        raise ValueError(
            "payload must be exactly four authentic bytes; "
            f"got {len(payload)}"
        )
    return (
        can_id.to_bytes(2, "big")
        + payload
        + pack_normal_freshness(trip_counter, reset_counter, message_counter)
    )


def sign_classic_frame(
    key: bytes,
    can_id: int,
    payload: bytes,
    trip_counter: int,
    reset_counter: int,
    message_counter: int,
) -> bytes:
    """Return an eight-byte classic-CAN payload with a Toyota SecOC trailer."""
    authenticated_input = build_normal_authenticated_input(
        can_id,
        payload,
        trip_counter,
        reset_counter,
        message_counter,
    )
    tag = _cmac_msb28(key, authenticated_input)
    transmitted_freshness = (
        ((message_counter & 0x3) << 2) | (reset_counter & 0x3)
    )
    trailer = (transmitted_freshness << 28) | tag
    return payload + trailer.to_bytes(4, "big")


def build_sync_authenticated_input(
    trip_counter: int,
    reset_counter: int,
    can_id: int = SYNC_CAN_ID,
) -> bytes:
    """Build DataID_be16 || trip16 || reset20 || 0000b for synchronization."""
    _require_classic_can_id(can_id)
    _require_uint("trip_counter", trip_counter, 16)
    _require_uint("reset_counter", reset_counter, 20)
    sync_freshness_left_aligned = (
        ((trip_counter << 20) | reset_counter) << 4
    ).to_bytes(5, "big")
    return can_id.to_bytes(2, "big") + sync_freshness_left_aligned


def sign_sync_frame(
    key: bytes,
    trip_counter: int,
    reset_counter: int,
    can_id: int = SYNC_CAN_ID,
) -> bytes:
    """Return an eight-byte synchronization frame: trip16 || reset20 || tag28."""
    authenticated_input = build_sync_authenticated_input(
        trip_counter,
        reset_counter,
        can_id,
    )
    tag = _cmac_msb28(key, authenticated_input)
    frame = (((trip_counter << 20) | reset_counter) << 28) | tag
    return frame.to_bytes(8, "big")


def _parse_int(value: str) -> int:
    try:
        return int(value, 0)
    except ValueError as error:
        raise argparse.ArgumentTypeError(f"invalid integer: {value}") from error


def _parse_hex(value: str, name: str, expected_bytes: int) -> bytes:
    try:
        parsed = bytes.fromhex(value)
    except ValueError as error:
        raise ValueError(f"{name} must be hexadecimal") from error
    if len(parsed) != expected_bytes:
        raise ValueError(
            f"{name} must encode exactly {expected_bytes} bytes, got {len(parsed)}"
        )
    return parsed


def _add_common_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--key",
        default=os.environ.get("TOYOTA_SECOC_KEY"),
        help="16-byte AES key as hex; defaults to TOYOTA_SECOC_KEY",
    )
    parser.add_argument("--trip", required=True, type=_parse_int, help="16-bit trip counter")
    parser.add_argument("--reset", required=True, type=_parse_int, help="20-bit reset counter")


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    sign_parser = subparsers.add_parser("sign", help="build a protected classic-CAN frame")
    _add_common_arguments(sign_parser)
    sign_parser.add_argument("--can-id", required=True, type=_parse_int, help="standard CAN ID")
    sign_parser.add_argument("--payload", required=True, help="four authentic payload bytes as hex")
    sign_parser.add_argument("--message", required=True, type=_parse_int, help="8-bit message counter")

    sync_parser = subparsers.add_parser("sync", help="build a synchronization frame")
    _add_common_arguments(sync_parser)
    sync_parser.add_argument(
        "--can-id",
        default=SYNC_CAN_ID,
        type=_parse_int,
        help=f"standard CAN ID (default: {SYNC_CAN_ID:#x})",
    )
    return parser


def main() -> int:
    parser = build_argument_parser()
    args = parser.parse_args()
    if args.key is None:
        parser.error("--key or TOYOTA_SECOC_KEY is required")

    try:
        key = _parse_hex(args.key, "key", AES_128_KEY_BYTES)
        if args.command == "sign":
            payload = _parse_hex(
                args.payload,
                "payload",
                CLASSIC_AUTHENTIC_PAYLOAD_BYTES,
            )
            frame = sign_classic_frame(
                key,
                args.can_id,
                payload,
                args.trip,
                args.reset,
                args.message,
            )
            can_id = args.can_id
        else:
            frame = sign_sync_frame(key, args.trip, args.reset, args.can_id)
            can_id = args.can_id
    except (TypeError, ValueError) as error:
        parser.error(str(error))

    print(f"{can_id:03X}#{frame.hex().upper()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
