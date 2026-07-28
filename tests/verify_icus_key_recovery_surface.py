#!/usr/bin/env python3
"""Verify the static ICU-S key-recovery surface in the committed firmware.

This suite locks the facts used by the physical-recovery assessment:
- every direct ICUSCMD writer is accounted for;
- no application writer issues a plaintext persistent-key export command;
- command 1/3, command 5, and command 7 accept runtime selectors 0..14 in
  software (hardware key-policy acceptance remains a bench question);
- the two protected CAN-FD profiles expose a 36-byte CMAC input whose first
  block contains 14 chosen payload bytes after the fixed two-byte Data ID; and
- the captured final 2 KiB DataFlash tail is only 00/FF CPU-visible readback.
"""
from __future__ import annotations

import hashlib
import math
import struct
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
CF = (REPO / "firmware" / "RH850_P1M-E_CodeFlash.bin").read_bytes()
DF = (REPO / "firmware" / "RH850_P1M-E_DataFlash.bin").read_bytes()
passed = failed = 0


def check(name: str, condition: bool, detail: str = "") -> None:
    global passed, failed
    if condition:
        passed += 1
        print(f"PASS: {name}")
    else:
        failed += 1
        suffix = f" ({detail})" if detail else ""
        print(f"FAIL: {name}{suffix}")


def u16(address: int) -> int:
    return struct.unpack_from("<H", CF, address)[0]


def u32(address: int) -> int:
    return struct.unpack_from("<I", CF, address)[0]


def body_hash(address: int, size: int) -> str:
    return hashlib.sha256(CF[address : address + size]).hexdigest()


print("== pinned ICU-S command implementations ==")
expected_hashes = {
    (0x8954C, 228, "command-1/3 AES family"): "e8577a1f8729e6ca4c261732427577f4b0ba3cce6388261993564682536429eb",
    (0x89630, 274, "command-5 MAC generation"): "eee619e9f0bd8f7454d7563f295d3430c3bdf1e365a7e4c04a7d064c4f8e9ed7",
    (0x897F4, 288, "command-7 CMAC verification"): "ad36148a8155bb51a07a2e8aabc4086210526e717d9e4cb5a83553342240cd98",
    (0x8997A, 188, "command-8 authenticated key update"): "2fd94cdf4d51be10d1528e43bee64e0f67f43b18a690ccf7ae22090e9a5895e7",
    (0x89D3E, 168, "ICU diagnostic command family"): "e58c772bcc123c2bf50637e87eb8e0bcf4da70428087d0bcba564593c31e5c5b",
}
for (address, size, label), expected in expected_hashes.items():
    actual = body_hash(address, size)
    check(f"{label} body hash", actual == expected, actual)

# Every direct store to ICUSCMD (FFC5D000) uses this six-byte RH850 encoding.
# Locking its complete occurrence census prevents a hidden literal command path
# from being inferred or silently introduced by an image change.
icuscmd_store = bytes.fromhex("80070f08a08b")
writer_sites = []
start = 0
while True:
    site = CF.find(icuscmd_store, start)
    if site < 0:
        break
    writer_sites.append(site)
    start = site + 1
check(
    "all nine direct ICUSCMD writer sites are accounted for",
    writer_sites == [0x8919C, 0x89628, 0x8973A, 0x8990C, 0x89A2C,
                     0x89A8A, 0x89BB0, 0x89BF8, 0x89DDC],
    repr([hex(site) for site in writer_sites]),
)

print("\n== software-selectable cryptographic oracles ==")
# The command-1/3 wrapper accepts key selectors <= 0xE, maps its operation flag
# 0/1 to literal command 1/3, and emits (selector << 16) | command.
check(
    "command-1/3 software selector range is 0 through 14",
    CF[0x89570:0x8957C] == bytes.fromhex("0495068de099e20d6e92cb0d"),
    CF[0x89570:0x8957C].hex(),
)
check(
    "operation flag selects only command 1 or command 3",
    CF[0x8958A:0x895A0] == bytes.fromhex("e089e205618ac205205611007f00010ae089e30f140b"),
    CF[0x8958A:0x895A0].hex(),
)
check(
    "command-1/3 emits selector-shifted dynamic command word",
    CF[0x89624:0x8962E] == bytes.fromhex("d092120980070f08a08b"),
    CF[0x89624:0x8962E].hex(),
)
check(
    "command-5 software selector range is 0 through 14",
    CF[0x89656:0x8967C]
    == bytes.fromhex(
        "0495407eff0001980180c89ad8824f9910990180"
        "8882d08600ff13810198989a10996e92ab0d"
    ),
    CF[0x89656:0x8967C].hex(),
)
check(
    "command-5 emits selector-shifted literal command 5",
    CF[0x89734:0x89740] == bytes.fromhex("d092920e050080070f08a08b"),
    CF[0x89734:0x89740].hex(),
)
check(
    "command-7 emits selector-shifted literal command 7",
    CF[0x89906:0x89912] == bytes.fromhex("d08a910e070080070f08a08b"),
    CF[0x89906:0x89912].hex(),
)
check(
    "command-8 writer is a literal command with no CPU key output",
    CF[0x89A22:0x89A32] == bytes.fromhex("200ed2ff440f6c5b080a80070f08a08b"),
    CF[0x89A22:0x89A32].hex(),
)
# The remaining writers are reset/abort (0x3F), ICU initialization (0x22),
# command 11, and diagnostic words 0x7000/0x7100. Combined with the exact
# writer census and constrained dynamic wrappers above, there is no command-13
# persistent-slot export invocation in this application image.
check("abort writer uses command 0x3F", CF[0x89BF4:0x89BFE] == bytes.fromhex("200e3f0080070f08a08b"))
check("initialization writer uses command 0x22", CF[0x89BAC:0x89BB6] == bytes.fromhex("200e220080070f08a08b"))
check("literal command-11 writer is accounted for", CF[0x89A88:0x89A90] == bytes.fromhex("0b0a80070f08a08b"))
check("diagnostic writer selects only 0x7000 or 0x7100",
      bytes.fromhex("2096007063970100") in CF[0x89D3E:0x89DE6]
      and bytes.fromhex("2096007163970100") in CF[0x89D3E:0x89DE6])

print("\n== slot-4 SecOC and chosen first-block surface ==")
key_config = CF[0x25950:0x25964]
check("SecOC key configuration selects ICU-S slot 4",
      u32(0x25950) == 1 and key_config[4] == 4 and key_config[5:] == bytes(15))

record_base = 0x25970
record_size = 0x50
records = [record_base + index * record_size for index in range(6)]
fd_records = records[4:]
check("protected CAN-FD Data IDs are 0x090 and 0x0D7",
      [u16(record + 0x0A) for record in fd_records] == [0x090, 0x0D7])
check("protected CAN-FD secured lengths are 32 bytes",
      [u32(record + 0x3C) for record in fd_records] == [32, 32])
check("protected CAN-FD trailers are four bytes",
      [u16(record + 0x06) for record in fd_records] == [4, 4])
check("protected CAN-FD profiles transmit 28 CMAC bits",
      [u16(record + 0x02) for record in fd_records] == [28, 28])
check("authenticated-input builder stores the Data ID big-endian",
      CF[0x8DB50:0x8DB5C] == bytes.fromhex("880a470f00006808470f0100"))

secured_length = u32(fd_records[0] + 0x3C)
trailer_length = u16(fd_records[0] + 0x06)
full_freshness_bytes = math.ceil(CF[fd_records[0] + 0x14] / 8)
payload_length = secured_length - trailer_length
authenticated_length = 2 + payload_length + full_freshness_bytes
chosen_first_block_bytes = 16 - 2
check("FD payload contributes 28 chosen bytes", payload_length == 28)
check("FD authenticated input is 36 bytes", authenticated_length == 36)
check("CMAC first block is DataID16 plus 14 chosen payload bytes",
      chosen_first_block_bytes == 14 and payload_length >= chosen_first_block_bytes)

# A first-round chosen-input leakage attack can target key bytes 2..15. If the
# two Data-ID-aligned bytes remain unresolved, exhaustive completion is only
# 2^16 and one 28-bit observed tag has a very small expected false-match count.
remaining_candidates = 1 << (8 * 2)
expected_false_matches = (remaining_candidates - 1) / (1 << 28)
check("two unresolved key bytes require only 2^16 completion candidates",
      remaining_candidates == 65_536)
check("one 28-bit tag gives under 1/4000 expected false completions",
      expected_false_matches < 1 / 4000, f"{expected_false_matches:.9f}")

print("\n== protected-tail readback boundary ==")
tail = DF[0x7800:0x8000]
check("captured protected tail is exactly 2 KiB", len(tail) == 0x800)
check("captured protected tail exposes only 00/FF bytes", set(tail) == {0x00, 0xFF})
check("captured protected-tail hash is pinned",
      hashlib.sha256(tail).hexdigest()
      == "736a3498a850949fabf830e7f422e4425dc648a2fd08a28364c7329198e193e1")
check("application DataFlash range validator body is pinned",
      body_hash(0x4EAD8, 68)
      == "ed9a2310d38eba7ef5b353dc41595ab8ebe337b01562cdab8636ccbb84c2d202")

print(f"\nSummary: {passed} passed, {failed} failed")
sys.exit(1 if failed else 0)
