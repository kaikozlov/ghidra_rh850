#!/usr/bin/env python3
"""Generate the machine-readable semantic record for Vance candidate-f05.

The executable facts are locked to the decrypted RH850 body hashes and exact
instruction windows. Human-readable interpretation lives in the canonical
report; this generator makes byte/authentication drift fail closed.
"""
from __future__ import annotations

import argparse
import binascii
import hashlib
import json
import struct
from pathlib import Path

from Crypto.Cipher import AES
from Crypto.Hash import CMAC


ROOT = Path(__file__).resolve().parents[1]
CODEFLASH = ROOT / "firmware/RH850_P1M-E_CodeFlash.bin"
STANDARD = ROOT / "tests/fixtures/payloads/dataflash_dump_payload.bin"
CANDIDATE = ROOT / "tests/fixtures/payloads/candidate_f05_dataflash_payload.bin"
DEFAULT_OUTPUT = ROOT / "data/generated/candidate_f05_payload.json"

ZERO = bytes(16)
PAYLOAD_SIZE = 0x1000
CRC_BLOCK_END = 0xFF0
CALLBACK_OFFSET = 0xFD0
CANDIDATE_BODY_END = 0x1B2
STANDARD_BODY_END = 0x18A


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def decrypt(ciphertext: bytes, secret: bytes) -> tuple[bytes, bytes]:
    derived = AES.new(secret, AES.MODE_ECB).encrypt(ZERO)
    plaintext = AES.new(derived, AES.MODE_CBC, ZERO).decrypt(ciphertext)
    return plaintext, derived


def authenticate(plaintext: bytes, derived: bytes) -> dict[str, object]:
    cmac = CMAC.new(derived, ciphermod=AES)
    cmac.update(ZERO + plaintext[:CRC_BLOCK_END])
    return {
        "crc32_residue": f"0x{binascii.crc32(plaintext[:CRC_BLOCK_END]) & 0xffffffff:08x}",
        "crc_valid": (binascii.crc32(plaintext[:CRC_BLOCK_END]) & 0xFFFFFFFF) == 0xFFFFFFFF,
        "cmac": cmac.hexdigest().lower(),
        "cmac_valid": cmac.digest() == plaintext[CRC_BLOCK_END:],
    }


def require(condition: object, message: str) -> None:
    if not condition:
        raise ValueError(message)


def build_report() -> dict[str, object]:
    codeflash = CODEFLASH.read_bytes()
    standard_cipher = STANDARD.read_bytes()
    candidate_cipher = CANDIDATE.read_bytes()
    require(len(standard_cipher) == PAYLOAD_SIZE, "standard payload size changed")
    require(len(candidate_cipher) == PAYLOAD_SIZE, "candidate payload size changed")

    payload_secret = codeflash[0xBFD8:0xBFE8]
    security_access_secret = codeflash[0xBFE8:0xBFF8]
    standard_plain, standard_derived = decrypt(standard_cipher, payload_secret)
    candidate_plain, candidate_derived = decrypt(candidate_cipher, security_access_secret)
    candidate_wrong_plain, candidate_wrong_derived = decrypt(candidate_cipher, payload_secret)

    require(
        sha256(standard_cipher) == "d48988366b5e6d2ddd7438caca5e6f6f02daba9b650263c323a2ffd770a06e34",
        "standard ciphertext hash changed",
    )
    require(
        sha256(candidate_cipher) == "296d87d2e89b9c7e800122e4c7f6d3b9c876362e52586530cdd53c86ba1116f5",
        "candidate ciphertext hash changed",
    )
    require(
        sha256(standard_plain) == "ec332718e01a3e346939fedf21833500b0fecd8ff08c5b9f218ba5724a4d3a10",
        "standard plaintext hash changed",
    )
    require(
        sha256(candidate_plain) == "ec39ef6c4a19c3687ee59183e2526bdea9e6d4886f11fbe4ab1f5382c484e1c0",
        "candidate plaintext hash changed",
    )
    require(
        sha256(standard_plain[:STANDARD_BODY_END]) == "a23f686a7f31d3fad9d5fc72464065bd38e517b5ea8e3a0e6410ca51cfedc597",
        "standard code body changed",
    )
    require(
        sha256(candidate_plain[:CANDIDATE_BODY_END]) == "5551b5aaecaeb361b21777d2f91d7cdf7b2dfe6b2ec0d1356d544cdbdf3416d1",
        "candidate code body changed",
    )
    require(not any(candidate_plain[CANDIDATE_BODY_END:CALLBACK_OFFSET]), "candidate padding is nonzero")
    require(not any(standard_plain[STANDARD_BODY_END:CALLBACK_OFFSET]), "standard padding is nonzero")

    standard_auth = authenticate(standard_plain, standard_derived)
    candidate_auth = authenticate(candidate_plain, candidate_derived)
    wrong_auth = authenticate(candidate_wrong_plain, candidate_wrong_derived)
    require(standard_auth["crc_valid"] and standard_auth["cmac_valid"], "standard authentication failed")
    require(candidate_auth["crc_valid"] and candidate_auth["cmac_valid"], "candidate authentication failed")
    require(not wrong_auth["crc_valid"] and not wrong_auth["cmac_valid"], "candidate unexpectedly accepts normal secret")

    callback = struct.unpack_from("<I", candidate_plain, CALLBACK_OFFSET)[0]
    crc_address, crc_length = struct.unpack_from("<II", candidate_plain, 0xFE0)
    require(callback == 0xFEBF0000, "candidate callback changed")
    require((crc_address, crc_length) == (0xFEBF0000, 0xFF0), "candidate CRC descriptor changed")

    differing = [i for i, pair in enumerate(zip(standard_plain, candidate_plain)) if pair[0] != pair[1]]
    code_differing = [i for i in differing if i < CALLBACK_OFFSET]
    trailer_differing = [i for i in differing if i >= 0xFEC]
    require(len(differing) == 380, "total plaintext diff count changed")
    require(len(code_differing) == 360, "pre-callback diff count changed")
    require(len(trailer_differing) == 20, "CRC/CMAC diff count changed")

    return {
        "schema_version": 1,
        "scope": "Vance 20260531 v3 deployment-bundle payloads",
        "load_address": "0xfebf0000",
        "inputs": {
            "standard_ciphertext_sha256": sha256(standard_cipher),
            "candidate_ciphertext_sha256": sha256(candidate_cipher),
            "payload_build_secret_source": "CodeFlash 0x0000bfd8",
            "security_access_secret_source": "CodeFlash 0x0000bfe8",
        },
        "standard": {
            "plaintext_sha256": sha256(standard_plain),
            "body_range": ["0xfebf0000", "0xfebf0189"],
            "body_sha256": sha256(standard_plain[:STANDARD_BODY_END]),
            "derived_key_sha256": sha256(standard_derived),
            "authentication": standard_auth,
            "terminal_behavior": "infinite branch at 0xfebf0188",
        },
        "candidate_f05": {
            "plaintext_sha256": sha256(candidate_plain),
            "body_range": ["0xfebf0000", "0xfebf01b1"],
            "body_sha256": sha256(candidate_plain[:CANDIDATE_BODY_END]),
            "derived_key_sha256": sha256(candidate_derived),
            "authentication": candidate_auth,
            "wrong_payload_secret_authentication": wrong_auth,
            "callback": f"0x{callback:08x}",
            "crc_descriptor": {"address": f"0x{crc_address:08x}", "length": f"0x{crc_length:x}"},
            "functions": [
                {"entry": "0xfebf0000", "end": "0xfebf019b", "role": "dataflash_dump"},
                {"entry": "0xfebf019c", "end": "0xfebf019f", "role": "indirect_call_trampoline"},
                {"entry": "0xfebf01a0", "end": "0xfebf01b1", "role": "return_epilogue"},
            ],
            "basic_blocks": [
                {"start": "0xfebf0000", "end": "0xfebf0073", "role": "prologue_and_pointer_setup"},
                {"start": "0xfebf0074", "end": "0xfebf0097", "role": "tx_slot_ready_gate"},
                {"start": "0xfebf0098", "end": "0xfebf012b", "role": "frame_build_and_submit"},
                {"start": "0xfebf012c", "end": "0xfebf0145", "role": "tx_completion_poll"},
                {"start": "0xfebf0146", "end": "0xfebf0177", "role": "clear_status_and_advance_word"},
                {"start": "0xfebf0178", "end": "0xfebf018b", "role": "range_loop_test"},
                {"start": "0xfebf018c", "end": "0xfebf019b", "role": "boot_reset_call_setup"},
                {"start": "0xfebf019c", "end": "0xfebf019f", "role": "indirect_call_trampoline"},
                {"start": "0xfebf01a0", "end": "0xfebf01b1", "role": "return_epilogue"},
            ],
            "memory_read": {
                "start": "0xff200000",
                "end_exclusive": "0xff208000",
                "stride": 4,
                "words": 8192,
                "region": "DataFlash",
            },
            "output": {
                "transport": "RSCFD classic CAN transmit slot 16",
                "can_id": "0x7a9",
                "frames": 8192,
                "data_layout": "07 || address_low24_le || memory_word_le32",
            },
            "sfr_references": [
                "0xffd20260", "0xffd202e0", "0xffd24200", "0xffd24204",
                "0xffd24208", "0xffd2420c", "0xffd24210",
            ],
            "reset_target": "0x0000157e",
            "special_references_absent": [
                "ICU-S 0xffc5dxxx",
                "object-15 RAM 0xfebf02e8",
                "object-15 DataFlash special-case 0xff206e14",
                "CPU-visible key-slot scan",
            ],
        },
        "semantic_diff": {
            "plaintext_bytes_changed": len(differing),
            "pre_callback_bytes_changed": len(code_differing),
            "crc_cmac_bytes_changed": len(trailer_differing),
            "unchanged": [
                "DataFlash range", "CAN ID", "frame format", "RSCFD slot",
                "ready/completion polling", "four-byte stride",
            ],
            "changed": [
                "payload authentication secret",
                "compiler stack/call frame and relocated loop body",
                "terminal infinite-loop replaced by boot reset call",
                "CRC32 adjustment and CMAC",
            ],
            "classification": "alternate full DataFlash dump, not an oracle or key-slot probe",
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    rendered = json.dumps(build_report(), indent=2, sort_keys=True) + "\n"
    if args.check:
        if not args.output.is_file() or args.output.read_text(encoding="utf-8") != rendered:
            raise SystemExit(f"generated candidate-f05 artifact is stale: {args.output}")
        print(f"[PASS] candidate-f05 generated artifact is current: {args.output}")
        return 0
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(rendered, encoding="utf-8")
    print(f"wrote {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
