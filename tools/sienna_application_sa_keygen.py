#!/usr/bin/env python3
"""
Standalone key generator for the Sienna EPS application SecurityAccess (27 03/04).

Algorithm (recovered from static analysis of 8965B4512000, RH850/P1M-E):

    K_inter = AES-128-ECB-DEC(APPLICATION_SA_SECRET, data_record)
    key     = AES-128-ECB-ENC(K_inter, seed)

The secret is at CodeFlash 0x20840. The data_record is tester-controlled:
it is the 16 bytes at PDU_buffer[2:18] during the 27 03 seed request.
Send "27 03" + 16 bytes of chosen data to set a known data_record.
For a bare "27 03" as the first request after reset, data_record = zeros.

Usage:
    python3 sienna_application_sa_keygen.py <seed_hex> [data_record_hex]

    seed_hex        16-byte seed received from 27 03 response (hex)
    data_record_hex 16-byte data record (hex, default = all zeros)

Examples:
    # Bare 27 03 (first request after reset, data_record = zeros):
    python3 sienna_application_sa_keygen.py 00112233445566778899aabbccddeeff

    # Chosen data record (attacker-controlled):
    python3 sienna_application_sa_keygen.py 00112233445566778899aabbccddeeff deadbeef000000000000000000000000

Requirements:
    pip install pycryptodome
"""
import sys

try:
    from Crypto.Cipher import AES
except ImportError:
    sys.stderr.write("pycryptodome required: pip install pycryptodome\n")
    sys.exit(1)

APPLICATION_LEVEL2_SA_SECRET = bytes.fromhex(
    "893e08418c741ffa2a9c044bffa55813"
)

ZERO_RECORD = bytes(16)


def derive_application_sa_key(seed: bytes, data_record: bytes = ZERO_RECORD) -> bytes:
    if len(seed) != 16:
        raise ValueError(f"seed must be exactly 16 bytes, got {len(seed)}")
    if len(data_record) != 16:
        raise ValueError(f"data_record must be exactly 16 bytes, got {len(data_record)}")

    intermediate = AES.new(APPLICATION_LEVEL2_SA_SECRET, AES.MODE_ECB).decrypt(data_record)
    return AES.new(intermediate, AES.MODE_ECB).encrypt(seed)


def main():
    if len(sys.argv) < 2:
        sys.stderr.write(__doc__ or "")
        sys.exit(1)

    seed = bytes.fromhex(sys.argv[1])
    data_record = bytes.fromhex(sys.argv[2]) if len(sys.argv) > 2 else ZERO_RECORD

    key = derive_application_sa_key(seed, data_record)

    print(f"secret:       {APPLICATION_LEVEL2_SA_SECRET.hex()}")
    print(f"data_record:  {data_record.hex()}")
    print(f"seed:         {seed.hex()}")
    print(f"key:          {key.hex()}")


if __name__ == "__main__":
    main()
