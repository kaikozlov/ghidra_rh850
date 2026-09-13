#!/usr/bin/env python3
"""Pin exact F33 read-only identity distinctions used in recovery assessment.

This checks the retained firmware, not live reachability or permission to flash.
No network, vehicle, Ghidra, proprietary host distribution or build/ input.
"""
from __future__ import annotations

import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IMAGE = ROOT / "firmware/camry-8965F3307000/CodeFlash.bin"


def main() -> int:
    image = IMAGE.read_bytes()
    assert len(image) == 0x100000

    app_dids = {}
    for index in range(241):
        address = 0x2928C + 16 * index
        did, width, callback = struct.unpack_from("<HHI", image, address)
        assert did not in app_dids
        app_dids[did] = (width, callback)
    assert app_dids[0xF181] == (33, 0x4FA26)
    assert app_dids[0xF186] == (1, 0x4FA7C)

    # Complete application F181 producer: count 2; status-selected 16-byte
    # records, or two sixteen-byte literal-0x21 loops. All opcodes are checked,
    # including both stores and the loop bound; this is not a text-name test.
    producer = bytes.fromhex(
        "8007610006e8020a460f000081ffe633000ae051ca15"
        "409e020001f0c199ddf1939f6108819b409e0100c199"
        "939fc17d410a0106f0ff919bf6edb50d01f0ddf1209e"
        "2100410a819b0106f0ff919bf6f5005240067f00"
    )
    assert image[0x4FA26:0x4FA7C] == producer
    assert image[0x62E18:0x62E1E] == bytes.fromhex("84576d4e7f00")
    normal_body = bytes([2]) + image[0x20860:0x20870] + image[0x17DC0:0x17DD0]
    assert normal_body == bytes([2]) + b"8965F3307000".ljust(16, b"\0") + b"8A3113303100".ljust(16, b"\0")
    app_failure_body = bytes([2]) + bytes([0x21]) * 16 * 2

    # Boot service 22's descriptor pointer, table bound and read-access test.
    assert image[0x8E84:0x8E8C] == bytes.fromhex("22020000b85f0000")
    boot = [struct.unpack_from("<IHHBBBB", image, 0x8F14 + 12 * i) for i in range(4)]
    assert [row[2] for row in boot] == [0xF181, 0x0201, 0x0202, 0x0203]
    assert [row[2] for row in boot if row[3] & 1] == [0xF181]
    assert image[0x6004:0x6010] == bytes.fromhex("7398f3518a25dec70800d21d")
    assert image[0x6048:0x604E] == bytes.fromhex("41326432f6d5")
    assert image[0x6066:0x6070] == bytes.fromhex("e0e9c20520363100c5f5")
    assert image[0x5F4C:0x5F56] == bytes.fromhex("209e21005e9f6e93410a")
    _, width, _, _, _, prefix, _ = boot[0]
    boot_body = bytes([prefix]) + bytes([0x21]) * width
    assert boot_body == app_failure_body
    assert len(boot_body) == 33
    assert normal_body != boot_body

    # F186 is an ordinary application current-session producer, not a write
    # or reset. Boot's four-entry readable table does not contain that DID.
    assert image[0x4FA7C:0x4FA8A] == bytes.fromhex("8007210084ff7420005240063f00")
    assert image[0x924FC:0x92518] == bytes.fromhex(
        "8007610006e880ffd867840f5da15d0f000080ffd867005240067f00"
    )
    assert 0xF186 not in [row[2] for row in boot if row[3] & 1]
    print("F33 recovery identity: PASS (placeholder is not boot-exclusive; F186 is an independent read-only distinction)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
