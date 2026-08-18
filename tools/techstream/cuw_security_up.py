#!/usr/bin/env python3
"""Reproduce Techstream V18 CUW SecurityUp key handling.

The modern CUW prepare-writer path does not use the ECU-family SecurityAccess
root directly.  TCUWCanCommonPrepareWriter.dll unwraps the 16-byte
ServiceAuthKey with its selector-0 AES wrapping key, then encrypts the 16-byte
ECU seed with that working key.

CUW text fields are ordinary hex strings.  Cuw.exe's calibration parser creates
CBytes from the full string but copies exactly the first 16 decoded bytes into
the fixed-size calibration structure fields used by the writers.
"""
from __future__ import annotations

import argparse

from Crypto.Cipher import AES

SECURITY_UP_WRAP_KEY = bytes.fromhex("B45B26D6344FD60E80BC01D63C7584A0")
BLOCK_SIZE = 16


def decode_cuw_block(value: str) -> bytes:
    """Decode a CUW hex field exactly as consumed by the V18 fixed-size fields."""
    try:
        raw = bytes.fromhex(value)
    except ValueError as exc:
        raise ValueError("CUW field must contain hexadecimal bytes") from exc
    if len(raw) < BLOCK_SIZE:
        raise ValueError(f"CUW field must decode to at least {BLOCK_SIZE} bytes")
    return raw[:BLOCK_SIZE]


def unwrap_service_auth_key(service_auth: bytes) -> bytes:
    if len(service_auth) != BLOCK_SIZE:
        raise ValueError("ServiceAuthKey must be exactly 16 bytes after CUW parsing")
    return AES.new(SECURITY_UP_WRAP_KEY, AES.MODE_ECB).decrypt(service_auth)


def calculate_security_up_response(ecu_seed: bytes, service_auth: bytes) -> bytes:
    if len(ecu_seed) != BLOCK_SIZE:
        raise ValueError("ECU seed must be exactly 16 bytes")
    working_key = unwrap_service_auth_key(service_auth)
    return AES.new(working_key, AES.MODE_ECB).encrypt(ecu_seed)


def firmware_security_access_working_key(family_secret: bytes, ecu_auth_key: bytes) -> bytes:
    """Reference the recovered RH850 firmware-side first SA stage."""
    if len(family_secret) != BLOCK_SIZE or len(ecu_auth_key) != BLOCK_SIZE:
        raise ValueError("firmware SA secret and ECUAuthKey must be 16 bytes")
    return AES.new(family_secret, AES.MODE_ECB).decrypt(ecu_auth_key)


def payload_key(payload_build_secret: bytes, seed_key: bytes) -> bytes:
    """Reference the recovered RH850 payload-key derivation."""
    if len(payload_build_secret) != BLOCK_SIZE or len(seed_key) != BLOCK_SIZE:
        raise ValueError("payload build secret and SeedKey must be 16 bytes")
    return AES.new(payload_build_secret, AES.MODE_ECB).encrypt(seed_key)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--service-auth", required=True, help="CUW ServiceAuthKey hex field")
    parser.add_argument("--ecu-seed", help="16-byte ECU seed hex; calculate the 27 02 response")
    parser.add_argument("--ecu-auth", help="CUW ECUAuthKey hex field; show the effective first 16 bytes")
    parser.add_argument("--seed-key", help="CUW SeedKey hex field; show the effective DID 0x0201 bytes")
    parser.add_argument("--nonce", help="CUW Nonce hex field; show the effective DID 0x0202 bytes")
    args = parser.parse_args()

    service_auth = decode_cuw_block(args.service_auth)
    working_key = unwrap_service_auth_key(service_auth)
    print(f"service_auth: {service_auth.hex()}")
    print(f"working_key: {working_key.hex()}")

    for name, value in (("ecu_auth", args.ecu_auth), ("seed_key", args.seed_key), ("nonce", args.nonce)):
        if value:
            print(f"{name}: {decode_cuw_block(value).hex()}")

    if args.ecu_seed:
        ecu_seed = bytes.fromhex(args.ecu_seed)
        response = calculate_security_up_response(ecu_seed, service_auth)
        print(f"ecu_seed: {ecu_seed.hex()}")
        print(f"security_up_response: {response.hex()}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
