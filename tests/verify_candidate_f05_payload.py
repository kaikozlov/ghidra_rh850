#!/usr/bin/env python3
"""Deterministically verify Vance candidate-f05 payload semantics."""
from __future__ import annotations

import hashlib
import json
import struct
import sys
from pathlib import Path

from Crypto.Cipher import AES


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from generate_candidate_f05_semantics import build_report  # noqa: E402


passed = failed = 0


def check(name: str, condition: object, detail: str = "") -> None:
    global passed, failed
    ok = bool(condition)
    passed += int(ok)
    failed += int(not ok)
    suffix = f" ({detail})" if detail else ""
    print(f"[{'PASS' if ok else 'FAIL'}] {name}{suffix}")


report = build_report()
artifact_path = ROOT / "data/generated/candidate_f05_payload.json"
artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
check("generated semantic artifact matches generator", artifact == report)

candidate_cipher = (ROOT / "tests/fixtures/payloads/candidate_f05_dataflash_payload.bin").read_bytes()
standard_cipher = (ROOT / "tests/fixtures/payloads/dataflash_dump_payload.bin").read_bytes()
codeflash = (ROOT / "firmware/RH850_P1M-E_CodeFlash.bin").read_bytes()
zero = bytes(16)

payload_secret = codeflash[0xBFD8:0xBFE8]
sa_secret = codeflash[0xBFE8:0xBFF8]
payload_key = AES.new(payload_secret, AES.MODE_ECB).encrypt(zero)
candidate_key = AES.new(sa_secret, AES.MODE_ECB).encrypt(zero)
standard = AES.new(payload_key, AES.MODE_CBC, zero).decrypt(standard_cipher)
candidate = AES.new(candidate_key, AES.MODE_CBC, zero).decrypt(candidate_cipher)

print("\n== authentication and immutable bodies ==")
check("candidate fixture ciphertext hash", hashlib.sha256(candidate_cipher).hexdigest() == report["inputs"]["candidate_ciphertext_sha256"])
check("candidate plaintext hash", hashlib.sha256(candidate).hexdigest() == report["candidate_f05"]["plaintext_sha256"])
check("candidate RH850 body hash", hashlib.sha256(candidate[:0x1B2]).hexdigest() == report["candidate_f05"]["body_sha256"])
check("candidate code is followed by zero padding", candidate[0x1B2:0xFD0] == bytes(0xFD0 - 0x1B2))
check("candidate callback is payload base", struct.unpack_from("<I", candidate, 0xFD0)[0] == 0xFEBF0000)
check("candidate CRC descriptor", struct.unpack_from("<II", candidate, 0xFE0) == (0xFEBF0000, 0xFF0))
check("candidate accepts SecurityAccess secret as build secret", report["candidate_f05"]["authentication"]["crc_valid"] and report["candidate_f05"]["authentication"]["cmac_valid"])
check("candidate rejects normal payload-build secret", not report["candidate_f05"]["wrong_payload_secret_authentication"]["crc_valid"] and not report["candidate_f05"]["wrong_payload_secret_authentication"]["cmac_valid"])

print("\n== semantic diff ==")
differing = [i for i, pair in enumerate(zip(standard, candidate)) if pair[0] != pair[1]]
check("exact plaintext difference count", len(differing) == 380)
check("exact pre-callback difference count", sum(i < 0xFD0 for i in differing) == 360)
check("only 20 changed bytes after code metadata", sum(i >= 0xFEC for i in differing) == 20)
check("standard body is the pinned 394-byte dump body", hashlib.sha256(standard[:0x18A]).hexdigest() == "a23f686a7f31d3fad9d5fc72464065bd38e517b5ea8e3a0e6410ca51cfedc597")
check("standard terminates in a self-branch", standard[0x188:0x18A] == bytes.fromhex("8505"))
check("candidate replaces self-branch with reset-call sequence", candidate[0x18C:0x1A0] == bytes.fromhex("20567e157d5721003d57210080ff040044fa6a00"))
check("candidate has a complete return epilogue", candidate[0x1A0:0x1B2] == bytes.fromhex("00001d1823ff2d0023ef2900031e30007f00"))

print("\n== RH850 memory and transport semantics ==")
pointer_setup = {
    0x10: "4056d2ff2a56d002",  # FFD202D0
    0x1C: "4056d2ff2a560040",  # FFD24000
    0x28: "4056d2ff2a560c40",  # FFD2400C
    0x34: "4056d2ff2a561040",  # FFD24010
    0x40: "4056d2ff2a560440",  # FFD24004
    0x4C: "4056d2ff2a560840",  # FFD24008
    0x58: "4056d2ff2a565002",  # FFD20250
}
for offset, expected in pointer_setup.items():
    check(f"RSCFD pointer setup at {offset:#x}", candidate[offset:offset + 8] == bytes.fromhex(expected))
check("interrupts disabled", candidate[0x64:0x68] == bytes.fromhex("e0076001"))
check("DataFlash start is 0xFF200000", candidate[0x68:0x6C] == bytes.fromhex("405620ff"))
check("DataFlash inclusive upper word is 0xFF207FFC", candidate[0x17C:0x184] == bytes.fromhex("405620ff2a56ff7f"))
check("transmit slot index is 16", candidate[0x74:0x78] == bytes.fromhex("20561000"))
check("classic eight-byte frame pointer field", candidate[0xA4:0xAC] == bytes.fromhex("405e00806a5f0100"))
check("CAN arbitration ID is 0x7A9", candidate[0xB8:0xC0] == bytes.fromhex("205ea9076a5f0100"))
check("DF0 encodes address shifted by 8 with marker 0x07", candidate[0xC0:0xDC] == bytes.fromhex("3d572500c8528a6607003d5f11003d571d00c552cb510c586a5f0100"))
check("DF1 reads one source word and stores it", candidate[0xDC:0xF6] == bytes.fromhex("3d5725002a6701003d5f0d003d571d00c552cb510c586a5f0100"))
check("frame-control word is cleared", candidate[0xF6:0x106] == bytes.fromhex("3d5f05003d571d00c552cb516a070100"))
check("transmit request sets bit 0", candidate[0x106:0x12A].endswith(bytes.fromhex("8b5e0100cb5eff004a5f0000")))
check("source advances by one 32-bit word", candidate[0x16E:0x178] == bytes.fromhex("3d57250044527d572500"))
check("bootloader reset target is 0x157E", candidate[0x18C:0x190] == bytes.fromhex("20567e15"))

print("\n== bounded negatives ==")
check("no SecurityAccess secret embedded in plaintext", sa_secret not in candidate)
check("no derived build key embedded in plaintext", candidate_key not in candidate)
check("no ASCII f05 signature in plaintext", b"f05" not in candidate.lower())
check("classification is full DataFlash dump", report["semantic_diff"]["classification"].startswith("alternate full DataFlash dump"))
check("object-15 is not specially addressed", "object-15 DataFlash special-case 0xff206e14" in report["candidate_f05"]["special_references_absent"])
check("ICU-S register family is absent", "ICU-S 0xffc5dxxx" in report["candidate_f05"]["special_references_absent"])
check("output protocol is unchanged", report["semantic_diff"]["unchanged"] == ["DataFlash range", "CAN ID", "frame format", "RSCFD slot", "ready/completion polling", "four-byte stride"])

print(f"\n== RESULT: {passed} passed, {failed} failed ==")
raise SystemExit(1 if failed else 0)
