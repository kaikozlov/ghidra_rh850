#!/usr/bin/env python3
"""Verify Stage-7 ICU-S software-path closure from the pinned CodeFlash image."""
from __future__ import annotations

import hashlib
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CF = (ROOT / "firmware" / "RH850_P1M-E_CodeFlash.bin").read_bytes()
SOFTWARE_REPORT = ROOT / "docs/security/secoc/software-path-assessment.md"
SENDER_REPORT = ROOT / "docs/security/secoc/sender-implementation.md"
CANDIDATE_REPORT = ROOT / "docs/security/secoc/candidate-f05-payload.md"
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


def decode_long_branch(addr: int) -> tuple[str, int] | None:
    if addr + 4 > len(CF):
        return None
    w0 = struct.unpack_from("<H", CF, addr)[0]
    if (w0 >> 6) & 0x1F != 0x1E:
        return None
    w1 = struct.unpack_from("<H", CF, addr + 2)[0]
    if w1 & 1:
        return None
    reg2 = (w0 >> 11) & 0x1F
    high = w0 & 0x3F
    if high & 0x20:
        high -= 0x40
    return ("jarl" if reg2 else "jr"), addr + (high << 16) + w1


print("== ICU result/FIFO software boundary ==")
for address, size, digest, label in (
    (0x87712, 116, "14082d1a1766778b49f733b879814da7a5c7a937db81f59410cf67f06e2fded5", "command 1/3 result wrapper"),
    (0x87B46, 116, "c62fc5e48366ad9f56eb73694bfa1481eaba9045f09d36dc751fc264e54f4be2", "command 5 result wrapper"),
    (0x87F7C, 78, "4f0358e66b4cd5597a6c7b48c220c6a5eddb2e386ab1d9967c7a8641732b8a63", "command 7 result wrapper"),
    (0x86EE8, 174, "c0ef9476d61b07555280b94dde170741b70e659c51e96fefc2dacb65df683ba4", "command 8 result wrapper"),
    (0x89510, 60, "257f509c57eb21caf89ce16e38597174b39a68d08c0b763caf8b20813c089836", "common finalizer"),
    (0x89DE6, 58, "814595c10b759f6dc32d1f9d36ed81bcd9c65b82048babfaea8857e77194c775", "tracked-command check"),
    (0x89E20, 218, "10c1395a6908962ce76597b92a8dd1a7ce89fe613b1a2534f33806d216da7948", "interrupt dispatcher"),
    (0x89BB8, 110, "bc1917e47be55473bf3833b894be2438303a9a30a141c1333ac9458796550683", "abort replacement"),
    (0x89360, 88, "c0dc4279962e2eb690c071414bf0342481493bdb4eccb621098ad390bbe24d4d", "driver state initializer"),
    (0x87DD0, 186, "ed65ceae78ed91987a3b27847dffaba9118143e0f94734ffc9aedca5fc9c45f9", "command 5 completion worker"),
    (0x881DC, 186, "a5df00bb4c1d63efb0870828b647b2c51d902372b3aecfb15081d1db5f2faba9", "command 7 completion worker"),
    (0x871A0, 186, "4d7f9856c658073e5551822f50bd0fb59ff081bca8bbd6a7cb14e64b867f19f9", "command 8 completion worker"),
):
    check(f"{label} body pinned", body_hash(address, size) == digest)

# Fixed lower-driver output geometries: cmd5=1 block, cmd7=1 word-result block,
# cmd8=3 blocks. Command 1/3 sets output count equal to its 16-byte input block count.
check("command 5 fixes one 16-byte output block", CF[0x896BE:0x896C6].find(bytes.fromhex("010a640f355b")) >= 0)
check("command 7 fixes one output block", CF[0x89894:0x898A2].find(bytes.fromhex("010a640f355b")) >= 0)
check("command 8 fixes four input and three output blocks", CF[0x899C2:0x899CC] == bytes.fromhex("040a640f2d5b030a640f"))
check("command 8 clears caller output on failure", decode_long_branch(0x86F54) == ("jarl", 0x89044))
check("command 8 clears 64-byte input staging",
      CF[0x86F5C:0x86F68] == bytes.fromhex("203e40001d36080080ffe020"))
check("command 8 clears 48-byte result staging",
      CF[0x86F68:0x86F74] == bytes.fromhex("1d364800203e300080ffd420"))

# Abort/replacement command 0x3f nulls both FIFO callbacks before replacing the
# tracked command. Body hash above pins the exact ordering; these literal zeros
# additionally make the intended boundary explicit.
check("abort replacement clears input/output callbacks", CF[0x89BEC:0x89BF4] == bytes.fromhex("6407215b64071d5b"))
check("abort/replacement submits command 0x3f", bytes.fromhex("3f") in CF[0x89BE0:0x89C10])

# No caller-controlled output length reaches the lower FIFO count: wrapper-side
# contracts are 16 / 16 / one result byte / 48 bytes respectively.
for token in ("status-zero gated", "16 bytes", "48 bytes", "command replacement", "hardware sequencing"):
    check(f"software-path report records {token}", token.lower() in SOFTWARE_REPORT.read_text(encoding="utf-8").lower())

print("\n== crypto-test activator reachability closure ==")
ACT_START, ACT_END = 0x69018, 0x69042
check("activator body remains pinned", body_hash(ACT_START, ACT_END - ACT_START) == "12088375d109e4753b8e88ffeb0edef82691229791ab8505f4ffab62e106f1fd")
# The RoutineControl action table does not point directly to 0x69018; RID 0x100F points
# to wrapper 0x8A782, whose literal call reaches the stock activator. This
# one-hop indirection is why the earlier direct-pointer census missed it.
ROUTINE_100F_ACTION_PTR = 0x25804 + 8 * 12 + 8
check("RoutineControl RID 0x100F action pointer selects wrapper 0x8A782",
      struct.unpack_from("<I", CF, ROUTINE_100F_ACTION_PTR)[0] == 0x8A782)
check("RoutineControl RID 0x100F wrapper directly calls bank-1 activator",
      decode_long_branch(0x8A786) == ("jarl", 0x69018))
# Exhaustive raw 32-bit pointer scan remains useful, but it proves only that no
# table points straight into the activator body; it is not a reachability proof.
pointer_hits: list[tuple[int, int]] = []
for off in range(len(CF) - 3):
    value = struct.unpack_from("<I", CF, off)[0]
    if ACT_START <= value < ACT_END:
        pointer_hits.append((off, value))
check("no raw CodeFlash pointer directly targets activator entry/interior", not pointer_hits, repr(pointer_hits[:8]))
# Direct code/data references, including the RoutineControl wrapper call, are locked by
# AssertIcusStage7Static.java.
check("startup path clears activation byte", CF[0x68006:0x6800A] == bytes.fromhex("44078f98"))
check("activator uniquely has explicit set-to-one store", CF[0x69024:0x6902A] == bytes.fromhex("010a440f8f98"))
check("finalizer writes terminal -1 state, not activation 1", CF[0x68D2C:0x68D36] == bytes.fromhex("1f9a44979798449f8f98"))

print("\n== statically justified signing-proxy landmarks ==")
for address, size, digest, label in (
    (0x68B42, 128, "2b7634bb6d42aa8173c53a5f43b8a88dcc12dedd89b9ceba35a728c8ad509b58", "stock crypto-test submit shape"),
    (0x88350, 150, "dca5252efba4bfee3cc2a509050d088b280771ce58b1d4134d3ead290545d4e4", "serialized generation dispatcher"),
    (0x64FCC, 92, "fd0f3a0bee88aae6eb48ba7bde2ae99e35d7ddd9fbd5fbac919fa498d112914a", "foreground cyclic loop"),
    (0x65750, 32, "dc700a7d2687bc725b522d4272aa73114933774c5dabd985cb3bd09de505fbdf", "foreground crypto-test slot"),
    (0x7EE0C, 160, "a1939f554721d183047141e2a78c1b15d19d4532b87f25614f36afa3b9f0445d", "CanIf transmit primitive"),
    (0x8206C, 26, "b1fbada7c360bba014061c255d1d1198328ff5f9ab13e48cdc60b153505db347", "special-class Tx wrapper"),
):
    check(f"{label} body pinned", body_hash(address, size) == digest)
check("stock harness requests 16-byte command-5 result", CF[0x68B8A:0x68B92] == bytes.fromhex("204e1000644f6198"))
check("stock harness dispatches generation driver", decode_long_branch(0x68BAC) == ("jarl", 0x88350))
check("foreground slot calls dormant step and finalize pair",
      decode_long_branch(0x65754) == ("jarl", 0x68C0C) and decode_long_branch(0x65760) == ("jarl", 0x68DE6))
for token in ("selector 4", "0x68b42", "0x65750", "0x7f8", "command-7 contention", "teardown"):
    check(f"sender design records {token}", token.lower() in SENDER_REPORT.read_text(encoding="utf-8").lower())

print("\n== candidate-f05 provenance boundary ==")
for token in (
    "97ba3d1d9e77a6e047887da04767538fe81fc674",
    "2026-05-31 20:26:27 +0800",
    "296d87d2e89b9c7e800122e4c7f6d3b9c876362e52586530cdd53c86ba1116f5",
    "db453752beeb7cdd024a1a9c38c6711c981e75ad",
    "2026-07-11",
    "cannot establish",
):
    check(f"candidate provenance records {token}", token.lower() in CANDIDATE_REPORT.read_text(encoding="utf-8").lower())

print(f"\nSummary: {passed} passed, {failed} failed")
sys.exit(1 if failed else 0)
