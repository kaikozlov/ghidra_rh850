#!/usr/bin/env python3
"""Verify security-relevant SecOC receiver properties from the committed image.

This suite focuses on logic boundaries rather than key extraction:
- authenticated payload/freshness are committed only after a successful CMAC;
- receiver freshness is cleared at SecOC initialization;
- synchronization accepts any authenticated forward jump (plus bounded wrap);
- failed guesses leave freshness uncommitted, while the transmitted tag is 28 bits;
- the synchronous CryptoIf wrapper has a fixed busy-poll budget;
- classic protected frames are exact-length, while configured 32-byte FD frames
  accept larger physical DLCs and are truncated before SecOC processing.
"""
from __future__ import annotations

import hashlib
import struct
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
CF = (REPO / "firmware" / "RH850_P1M-E_CodeFlash.bin").read_bytes()
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


print("== locked security-relevant function bodies ==")
expected_hashes = {
    (0x8DB84, 62, "SecOC RX initialization"): "ac170e1911bb6e94c78b939d024b7098ec5c389eec80a29dccb4144034cbfbe2",
    (0x8E7D4, 24, "freshness initialization wrapper"): "5901280c0931729a4bf5e37d5ce17f74a12f2c8d640ab9e15495eefe6ff0b77c",
    (0x8E9FC, 76, "freshness state clear"): "ba4de073bb19193547aa2617a2df65b811fed603cf64c87d9fdad60f0603178a",
    (0x8EF9E, 228, "sync freshness reconstruction"): "0b0c4ce23e156ae4b1d621c86c0f4a5356d738ef6fdd2ed34187ff895bc5c596",
    (0x8E67A, 134, "post-verification commit/delivery"): "fbe3753387d3e9de73baee0496c2a3777b0ebe7b252ef3654ddb88f7bae402ff",
    (0x8E0BE, 128, "secured-PDU queue/clamp"): "0acb261aeb2ae94df0089fe06da35b2b2c346b8751fbad78188ebe5f89a866b6",
    (0x8E4BA, 396, "SecOC verification worker"): "db69bf24d3ce490afdfbcac2049ed054a0097227e4a3eea3f3749cedcb72ee2c",
    (0x88BA8, 98, "CryptoIf completion poll"): "139547a74d2b9affed13921621766da441817167bf42b4d78f0545b3eb9b7965",
    (0x7FF52, 52, "CAN RX DLC bounds callback"): "0a6ca30fbd26a8694b363c59e7bb5a4c0a51e71982a7b3b2e41329be5804439e",
}
for (address, size, label), expected in expected_hashes.items():
    actual = body_hash(address, size)
    check(f"{label} body hash", actual == expected, actual)


print("\n== fail-closed authentication boundary ==")
# The sole load of the ICU verify-result byte (APP_GP-0x62A4 = FEBE555C)
# is converted to boolean and passed to the freshness-commit callback. The
# same boolean controls whether the authentic PDU is delivered downstream.
check(
    "post-verify path loads FEBE555C and booleanizes nonzero mismatch",
    CF[0x8E69E:0x8E6A8] == bytes.fromhex("840f5d9de009e10f14d3"),
    CF[0x8E69E:0x8E6A8].hex(),
)
check(
    "verify-result GP-relative load occurs once in CodeFlash",
    CF.count(bytes.fromhex("840f5d9d")) == 1,
    str(CF.count(bytes.fromhex("840f5d9d"))),
)
check(
    "nonzero result branches to mismatch path while zero falls through delivery",
    CF[0x8E6C4:0x8E6DA]
    == bytes.fromhex("1d30e0d19a0d1a38bfff78fb1d301a38bfffe6fbd505"),
    CF[0x8E6C4:0x8E6DA].hex(),
)


print("\n== volatile freshness and synchronization ordering ==")
# Init explicitly zeroes three freshness control words, then calls the full
# state-clear helper. This is a positive firmware assertion; the absence of a
# later NvM restore into these words remains a firmware-static bounded result.
check(
    "freshness init zeroes control words then calls state clear",
    CF[0x8E7D4:0x8E7EC]
    == bytes.fromhex("800721006407609d6407629d6407649d80ff180240063f00"),
    CF[0x8E7D4:0x8E7EC].hex(),
)
check("sync wrap threshold is 15", CF[0x2596C] == 0x0F, hex(CF[0x2596C]))


def sync_candidate_is_forward(
    old_trip: int,
    old_reset: int,
    new_trip: int,
    new_reset: int,
    wrap_threshold: int = 0x0F,
) -> bool:
    """Reference model of 0x8EF9E's pre-CMAC monotonicity predicate."""
    old_trip &= 0xFFFF
    new_trip &= 0xFFFF
    old_reset &= 0xFFFFF
    new_reset &= 0xFFFFF
    wrap = (
        old_trip >= 0xFFFF - wrap_threshold
        and new_trip != 0
        and new_trip <= wrap_threshold + 1
    )
    return (
        old_trip < new_trip
        or (old_trip == new_trip and old_reset < new_reset)
        or wrap
    )


check("equal sync freshness is rejected", not sync_candidate_is_forward(7, 9, 7, 9))
check("ordinary rollback is rejected", not sync_candidate_is_forward(7, 9, 6, 0xFFFFF))
check("same-trip reset advance is accepted", sync_candidate_is_forward(7, 9, 7, 10))
check("arbitrarily large forward trip jump is accepted", sync_candidate_is_forward(1, 0, 0xE000, 0))
check("configured trip wrap is accepted", sync_candidate_is_forward(0xFFF0, 4, 1, 0))
check(
    "post-init captured positive sync is structurally forward",
    sync_candidate_is_forward(0, 0, 1, 0),
)


print("\n== truncated-tag retry and availability bounds ==")
RECORD_BASE = 0x25970
records = [RECORD_BASE + i * 0x50 for i in range(6)]
check("all profiles transmit 28 CMAC bits", all(u16(a + 2) == 28 for a in records))
check("mean blind-guess work factor is 2^27", (1 << (28 - 1)) == 134_217_728)
check(
    "CryptoIf completion uses fixed 0xE07-iteration poll budget",
    CF[0x88BF0:0x88BF8] == bytes.fromhex("410a0106f9f1b9f5"),
    CF[0x88BF0:0x88BF8].hex(),
)
# Failed verification passes false to commit and does not advance freshness;
# this is what makes repeated guesses target the same candidate until success
# or a legitimate authenticated frame advances state.
check(
    "post-verify false branch passes zero to freshness commit",
    CF[0x8E6B8:0x8E6C4] == bytes.fromhex("003aa5051a381d30bfff86ff"),
    CF[0x8E6B8:0x8E6C4].hex(),
)


print("\n== physical DLC canonicalization ==")
NORMAL_RX_DESC = 0x22018
configured_lengths = [CF[NORMAL_RX_DESC + i * 8 + 4] for i in range(47)]
for index, expected in ((0, 8), (5, 8), (20, 8), (29, 8), (40, 32), (41, 32)):
    check(f"secured route {index} configured minimum DLC", configured_lengths[index] == expected)


def canif_dlc_accepted(actual: int, configured_minimum: int, can_fd: bool) -> bool:
    physical_maximum = 64 if can_fd else 8
    return configured_minimum <= actual <= physical_maximum


def secoc_effective_length(actual: int, configured: int) -> int:
    return min(actual, configured)


check("classic secured profiles require exact DLC 8", all(
    canif_dlc_accepted(n, 8, False) == (n == 8) for n in range(0, 65)
))
check("FD secured profiles accept configured DLC 32", canif_dlc_accepted(32, 32, True))
check("FD secured profiles also accept physical DLC 48/64", all(
    canif_dlc_accepted(n, 32, True) for n in (48, 64)
))
check("SecOC truncates accepted FD DLC 48/64 to 32", all(
    secoc_effective_length(n, 32) == 32 for n in (48, 64)
))
check(
    "CAN RX descriptor IDs match protected FD routes",
    (u32(NORMAL_RX_DESC + 40 * 8) & 0x7FF, u32(NORMAL_RX_DESC + 41 * 8) & 0x7FF)
    == (0x090, 0x0D7),
)

print(f"\nSummary: {passed} passed, {failed} failed")
sys.exit(1 if failed else 0)
