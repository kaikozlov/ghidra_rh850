#!/usr/bin/env python3
"""Verify foreign-Corolla facts that bound the Toyota-B programming pin-swap anomaly."""
from __future__ import annotations

import hashlib
import struct
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
S = (REPO / "firmware/RH850_P1M-E_CodeFlash.bin").read_bytes()
H_RANGE = (REPO / "community/albinoelephant/raw-20260818/albinoelephant-corolla-2023.20260814-0023/dump_codeflash_00000000_00200000_20260814-025814.bin").read_bytes()
H = H_RANGE[:0x100000]

passed = failed = 0

def check(name: str, condition: object, detail: str = "") -> None:
    global passed, failed
    ok = bool(condition)
    passed += int(ok)
    failed += int(not ok)
    print(f"[{'PASS' if ok else 'FAIL'}] {name}" + (f" ({detail})" if detail else ""))


def u32(buf: bytes, off: int) -> int:
    return struct.unpack_from("<I", buf, off)[0]


print("== foreign image identity ==")
check("range dump is 2 MiB", len(H_RANGE) == 0x200000, hex(len(H_RANGE)))
check("upper 1 MiB is outside-part filler", H_RANGE[0x100000:] == b"\xff" * 0x100000)
check("normalized CodeFlash is 1 MiB", len(H) == 0x100000)
check(
    "normalized CodeFlash SHA-256 is pinned 8965H1202000 image",
    hashlib.sha256(H).hexdigest() == "0b47bdc1217835c839e3543e52eab40eb793650a9c159e46f6a9b365ea41a67f",
)
check("live application software ID is 8965H1202000", H[0x17D80:0x17D8C] == b"8965H1202000")

print("\n== boot diagnostic controller/routing ==")
# Foreign TP is 0x867c. These are the same CanIf/RSCFD roots recovered for the
# Sienna image, shifted by the variant's boot layout.
rx_ids = [u32(H, 0x8900 + i * 12 + 4) for i in range(2)]
tx_count = u32(H, 0x8924)
tx_id = u32(H, 0x892C)
tx_hth = struct.unpack_from("<H", H, 0x8932)[0]
check("boot Rx IDs are physical 0x7A1 and functional 0x777", rx_ids == [0x7A1, 0x777], repr(rx_ids))
check("boot has one Tx PDU", tx_count == 1, str(tx_count))
check("boot Tx ID is 0x7A9", tx_id == 0x7A9, hex(tx_id))
check("boot diagnostic Tx HTH is channel-1 object 0x13", tx_hth == 0x13, hex(tx_hth))
channel_records = [H[0x8958 + i * 6:0x8958 + (i + 1) * 6] for i in range(3)]
check("only boot RSCFD channel 1 is enabled", channel_records == [bytes(6), bytes.fromhex("008003000800"), bytes(6)], repr([x.hex() for x in channel_records]))

hrh_routes = [struct.unpack_from("<IHBB", H, 0x896C + i * 8) for i in range(0x30)]
filter0_hrhs = [i for i, (_cb, first, count, _flags) in enumerate(hrh_routes) if count and first == 0]
check("0x7A1 is exposed only through channel-1 HRHs 0x10/0x13", filter0_hrhs == [0x10, 0x13], repr(filter0_hrhs))
check("boot channels 0 and 2 expose no active receive filters", all(r[2] == 0 for r in hrh_routes[:0x10] + hrh_routes[0x20:]))

print("\n== application controller continuity ==")
def vector(irq: int) -> int:
    return u32(H, 0x20200 + irq * 4)
app = {irq: vector(irq) for irq in (184, 185, 187, 188, 192, 193)}
check("application CAN1 RX/TX vectors are live", app[187] == 0x5F3AA and app[188] == 0x5F368, repr(app))
check("application CAN0/CAN2 vectors remain default", len({app[i] for i in (184,185,192,193)}) == 1 and app[184] == 0x5C0F2, repr(app))
check("application CAN1 RX body hard-codes channel 1", H[0x7D240:0x7D246] == bytes.fromhex("800721000132"))
check("application CAN1 TX body hard-codes channel 1", H[0x7EB4E:0x7EB54] == bytes.fromhex("800721000132"))
check(
    "complete three-channel application RSCFD register map transfers byte-identically",
    H[0x22E18:0x22E18 + 3 * 0x74] == S[0x22FE0:0x22FE0 + 3 * 0x74],
)
check(
    "complete three-channel application RSCFD driver config transfers byte-identically",
    H[0x232A8:0x232A8 + 3 * 0x34] == S[0x234E0:0x234E0 + 3 * 0x34],
)

print("\n== boot stack implementation transfer ==")
check("boot peripheral init is byte-identical", H[0xC7E:0xC7E + 442] == S[0xC9A:0xC9A + 442])
# The transport/driver body is the same code shifted by 0x1c, with only three
# relocation bytes changing because variant-local table addresses moved.
s_driver = S[0x3400:0x4700]
h_driver = H[0x33E4:0x46E4]
diffs = [(i, a, b) for i, (a, b) in enumerate(zip(s_driver, h_driver)) if a != b]
check("boot CAN/CanIf transport region differs only at three relocation bytes", [(i,a,b) for i,a,b in diffs] == [(0x1F4,0x70,0x50),(0x6B4,0x0C,0x0A),(0x6D0,0xF0,0xEE)], repr(diffs))

print("\n== programming-session handoff semantics ==")
s_sessions = S[0x262F6:0x262F6 + 5 * 10]
h_sessions = H[0x26006:0x26006 + 5 * 10]
check("five session runtime records transfer byte-identically", h_sessions == s_sessions)
check("PROGRAMMING session record is async kind 2", h_sessions[10:20] == bytes.fromhex("020232008813d007f401"), h_sessions[10:20].hex())
check("foreign programming speed threshold is 0x0180", struct.unpack_from("<H", H, 0x2D454)[0] == 0x180)
check("foreign programming supply threshold is 0x0A00", struct.unpack_from("<H", H, 0x2D456)[0] == 0xA00)
check("foreign lower handoff operation is a zero-return stub", H[0x8441C:0x84424] == bytes.fromhex("00527f0000527f00"))
check("foreign token helper contains the same 0x5A success return", H[0x87934:0x8793A] == bytes.fromhex("20565a007f00"))
check("foreign prepare path references operation selector 0x08000200", bytes.fromhex("02000813") in H[0x844C2:0x84572])
check("foreign commit path references operation selector 0x08000201", bytes.fromhex("010002d2") in H[0x84572:0x84644])
check("foreign reset-request path contains the 0x5A transition marker", bytes.fromhex("200e5a00") in H[0x482B4:0x48304])

print("\n== RESULT ==")
print(f"{passed} passed, {failed} failed")
sys.exit(1 if failed else 0)
