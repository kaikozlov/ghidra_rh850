#!/usr/bin/env python3
"""Pin semantics for functions promoted from the reproducible semantic sweep."""
from __future__ import annotations

import hashlib
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CF = (ROOT / "firmware" / "RH850_P1M-E_CodeFlash.bin").read_bytes()
passed = failed = 0


def check(name: str, condition: bool, detail: str = "") -> None:
    global passed, failed
    if condition:
        passed += 1
    else:
        failed += 1
    suffix = f" ({detail})" if detail else ""
    print(f"[{'PASS' if condition else 'FAIL'}] {name}{suffix}")


def body_hash(address: int, size: int) -> str:
    return hashlib.sha256(CF[address : address + size]).hexdigest()


def u32(address: int) -> int:
    return struct.unpack_from("<I", CF, address)[0]


def decode_long_branch(address: int) -> tuple[str, int] | None:
    w0, w1 = struct.unpack_from("<HH", CF, address)
    if ((w0 >> 6) & 0x1F) != 0x1E or (w1 & 1):
        return None
    reg2 = (w0 >> 11) & 0x1F
    high = w0 & 0x3F
    if high & 0x20:
        high -= 0x40
    return ("jarl" if reg2 else "jr"), address + (high << 16) + w1


print("== boot RequestTransferExit ==")
services = {
    sid: handler
    for sid, _mask, _reserved, handler in (
        struct.unpack_from("<BBHI", CF, 0x8E54 + i * 8) for i in range(20)
    )
}
check("SID 0x37 dispatches to 0x5C92", services.get(0x37) == 0x5C92)
check(
    "TransferExit body pinned",
    body_hash(0x5C92, 152) == "b7e3789a7ec481d6b2274115c808bedaf2cb7d062d3a27e39795ffe2bc55c3da",
)
check("TransferExit finalizes payload crypto on active path", decode_long_branch(0x5CE6) == ("jarl", 0x6BD2))
check("TransferExit finalizes payload crypto on terminal cleanup path", decode_long_branch(0x5D0E) == ("jarl", 0x6BD2))
check(
    "TransferExit clears transfer authorization/address/length/state",
    CF[0x5D12:0x5D22] == bytes.fromhex("44071793640701936407059344071393"),
)
check("TransferExit returns through response helper", decode_long_branch(0x5D22) == ("jarl", 0x5C76))

print("\n== ICU command-5 lower adapter ==")
check(
    "command-5 adapter body pinned",
    body_hash(0x87CCC, 260) == "2a5c7f1c4bed7543f8143a21e3d78319c8c3f1298f96ca2b87a5b7a244e9b729",
)
check("both command-5 lower records own adapter", [u32(0x27F8C), u32(0x27FAC)] == [0x87CCC, 0x87CCC])
check("command-5 adapter prepares on both state paths",
      decode_long_branch(0x87D06) == ("jarl", 0x87A94)
      and decode_long_branch(0x87D72) == ("jarl", 0x87A94))
check("command-5 adapter installs start callback 0x87C70", CF[0x87D1A:0x87D20] == bytes.fromhex("2106707c0800"))
check("command-5 adapter installs finish callback 0x87BBA", CF[0x87D2A:0x87D30] == bytes.fromhex("2106ba7b0800"))
check("command-5 adapter starts ICU command 5", decode_long_branch(0x87D96) == ("jarl", 0x87C70))

print("\n== ICU command-7 CMAC-verify lower adapter ==")
check(
    "CMAC-verify adapter body pinned",
    body_hash(0x880DC, 256) == "6b5d22eb5fb7b899d83f105cf5f00ed1cc87ac9e7a8e2b7b9d22ccaa94ece6ec",
)
check("both command-7 lower records own adapter", [u32(0x27FD0), u32(0x27FF0)] == [0x880DC, 0x880DC])
check("CMAC-verify adapter prepares on both state paths",
      decode_long_branch(0x88114) == ("jarl", 0x87ED0)
      and decode_long_branch(0x8817E) == ("jarl", 0x87ED0))
check("CMAC-verify adapter installs start callback 0x88080", CF[0x88128:0x8812E] == bytes.fromhex("210680800800"))
check("CMAC-verify adapter installs finish callback 0x87FCA", CF[0x88138:0x8813E] == bytes.fromhex("2106ca7f0800"))
check("CMAC-verify adapter starts ICU command 7", decode_long_branch(0x881A2) == ("jarl", 0x88080))

print(f"\n== RESULT: {passed} passed, {failed} failed ==")
sys.exit(1 if failed else 0)
