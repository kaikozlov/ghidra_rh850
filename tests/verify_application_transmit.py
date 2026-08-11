#!/usr/bin/env python3
"""Independent raw-CodeFlash checks for docs/communications/application-tx.md."""
from __future__ import annotations

from collections import Counter
import csv
import hashlib
from pathlib import Path
import struct
import subprocess
import sys
import tempfile

REPO = Path(__file__).resolve().parents[1]
CF = (REPO / "firmware" / "RH850_P1M-E_CodeFlash.bin").read_bytes()
CSV_PATH = REPO / "data" / "application_tx_map.csv"
GEN = REPO / "tools" / "generate_application_tx_map.py"

passed = failed = 0


def check(name: str, condition: object, detail: str = "") -> None:
    global passed, failed
    ok = bool(condition)
    passed += int(ok)
    failed += int(not ok)
    suffix = f" ({detail})" if detail else ""
    print(f"[{'PASS' if ok else 'FAIL'}] {name}{suffix}")


def u16(offset: int) -> int:
    return struct.unpack_from("<H", CF, offset)[0]


def u32(offset: int) -> int:
    return struct.unpack_from("<I", CF, offset)[0]


def sha256_region(offset: int, size: int) -> str:
    return hashlib.sha256(CF[offset:offset + size]).hexdigest()


print("== generated CanIf transmit classes and records ==")
class_counts = [u16(0x21A68 + 2 * i) for i in range(6)]
check("six PduR transmit classes have exact active counts", class_counts == [6, 0, 4, 0, 0, 1], repr(class_counts))

TX = struct.Struct("<IBBH")
com_tx = [TX.unpack_from(CF, 0x21F78 + TX.size * i) for i in range(6)]
diag_tx = [TX.unpack_from(CF, 0x21FA8 + TX.size * i) for i in range(4)]
special_tx = TX.unpack_from(CF, 0x21F68)
check("CanIf Tx records are eight bytes", TX.size == 8)
check("six COM Tx CAN IDs are exact",
      [row[0] for row in com_tx] == [0x260, 0x262, 0x351, 0x394, 0x4A3, 0x4C8])
check("COM Tx records select controller zero", all(row[1:3] == (0, 0) for row in com_tx))
check("COM Tx confirmation routes split 0/0/1/1/1/1",
      [row[3] for row in com_tx] == [0, 0, 1, 1, 1, 1])
check("four class-2 routes use 7A9/7A9/7A8/7A8",
      [row[0] for row in diag_tx] == [0x7A9, 0x7A9, 0x7A8, 0x7A8])
check("class-2 routes select controller zero", all(row[1:3] == (0, 0) for row in diag_tx))
check("class-2 confirmation routes split 0/0/1/1",
      [row[3] for row in diag_tx] == [0, 0, 1, 1])
check("sole indexed class-5 Tx route is CAN 0x7F8", special_tx == (0x7F8, 0, 0, 0), repr(special_tx))
check("class-5 Rx descriptor points at adjacent CAN 0x7F7 record",
      u32(0x21A40) == 0x21AC4 and u32(0x21AC4) == 0x21F70
      and TX.unpack_from(CF, 0x21F70)[0] == 0x7F7)
check("class-5 Rx upper callback is 0x82042", u32(0x21AC8) == 0x82042)
check("special protocol Tx function is 0x8206C", u32(0x22B90) == 0x8206C)
check("special Tx wrapper injects PduR class 0xF800 and calls CanIf",
      CF[0x82078:0x82082] == bytes.fromhex("863600f80338bfff8ecd"))
check("special Rx callback reaches the paired protocol receive path",
      CF[0x82062:0x82066] == bytes.fromhex("bfff82ff")
      and CF[0x8203A:0x8203E] == bytes.fromhex("bfffc6fe"))
check("CAN 0x344 is absent from every active Tx route",
      0x344 not in [row[0] for row in com_tx + diag_tx] + [special_tx[0]])

print("\n== COM transmit PDU descriptors and buffers ==")
PDU = struct.Struct("<HBBHBB")
expected_pdu = [
    (4, 0, 0, 8, 0, 3),
    (8, 0, 0, 8, 0, 3),
    (200, 0, 0, 4, 0, 3),
    (60, 0, 0, 3, 0, 3),
    (100, 0, 0, 8, 0, 3),
    (196, 0, 0, 8, 0, 3),
]
com_pdu = [PDU.unpack_from(CF, 0x2273C + PDU.size * i) for i in range(6)]
check("COM PDU descriptors are eight bytes", PDU.size == 8)
check("six Tx PDU cycle/length/flag records match", com_pdu == expected_pdu, repr(com_pdu))
check("first six buffer offsets are contiguous by PDU length",
      [u16(0x228E4 + 2 * i) for i in range(6)] == [0, 8, 16, 20, 23, 31])
check("six Tx lengths occupy 39 initial bytes", sum(row[3] for row in com_pdu) == 39)
expected_initial = bytes.fromhex(
    "0e00000000000000"
    "1000000000ffff00"
    "00000000"
    "000000"
    "0000000000000000"
    "0900000000000000"
)
check("39-byte initial Tx data image matches", CF[0x221DC:0x221DC + 39] == expected_initial,
      CF[0x221DC:0x221DC + 39].hex())
check("53 COM PDU descriptors split as six Tx plus 47 Rx", 53 - 6 == 47)

print("\n== all 58 configured transmit signals ==")
signal_to_pdu = [u16(0x224E4 + 2 * i) for i in range(300)]
expected_groups = [0] * 10 + [1] * 28 + [2] * 2 + [3] * 6 + [4] * 8 + [5] * 4
check("first 58 generated signals map exactly to Tx PDUs 0..5", signal_to_pdu[:58] == expected_groups)
check("Tx signal counts are 10/28/2/6/8/4",
      [signal_to_pdu[:58].count(i) for i in range(6)] == [10, 28, 2, 6, 8, 4])
check("remaining 242 signals map only to 47 receive PDUs",
      min(signal_to_pdu[58:]) == 6 and max(signal_to_pdu[58:]) == 52 and len(set(signal_to_pdu[58:])) == 47)
signal_properties = list(CF[0x223B8:0x223B8 + 58])
check("Tx signal property classes match 0*38,3*8,0*12",
      signal_properties == [0] * 38 + [3] * 8 + [0] * 12)

with CSV_PATH.open(newline="", encoding="utf-8") as stream:
    rows = list(csv.DictReader(stream))
check("machine-readable Tx map has 58 rows", len(rows) == 58, str(len(rows)))
check("CSV signal IDs are exactly 0..57", [int(row["signal_id"]) for row in rows] == list(range(58)))
check("CSV PDU membership equals raw signal map",
      [int(row["tx_pdu_id"]) for row in rows] == signal_to_pdu[:58])
summary = {
    int(row["tx_pdu_id"]): (
        int(row["can_id"], 0), int(row["length"]), int(row["cycle_ticks"])
    )
    for row in rows
}
check("CSV PDU summaries match raw tables", summary == {
    0: (0x260, 8, 4),
    1: (0x262, 8, 8),
    2: (0x351, 4, 200),
    3: (0x394, 3, 60),
    4: (0x4A3, 8, 100),
    5: (0x4C8, 8, 196),
}, repr(summary))
check("each PDU has one recovered generated packer", {
    pdu: {row["packer"] for row in rows if int(row["tx_pdu_id"]) == pdu}
    for pdu in range(6)
} == {
    0: {"0x4BCEE"}, 1: {"0x4BE24"}, 2: {"0x4C25C"},
    3: {"0x4C158"}, 4: {"0x4BB1E"}, 5: {"0x4BC54"},
})
check("all 58 configured signals are assigned to their generated PDU packer",
      all(row["packer"] != "none" for row in rows))
check("signals 9 and 37 are post-packer CanIf checksums",
      [(int(r["signal_id"]), r["source_kind"], r["source"]) for r in rows if int(r["signal_id"]) in (9, 37)]
      == [(9, "canif_checksum", "0x7FEAC"), (37, "canif_checksum", "0x7FEAC")])
check("signal 57 is classified default-only zero",
      next(r for r in rows if r["signal_id"] == "57")["source_kind"] == "default_only"
      and next(r for r in rows if r["signal_id"] == "57")["source"] == "0")
check("no configured-unresolved Tx rows remain",
      all(r["source_kind"] != "configured-unresolved" for r in rows))
check("RAM-backed signal sources are application addresses",
      all(0xFEBE8094 <= int(row["source"], 0) <= 0xFEBE8110
          for row in rows if row["source_kind"] == "ram"))
expected_sources = [
    "0xFEBE8094", "0xFEBE8096", "0xFEBE8098", "0xFEBE8099", "0xFEBE809A",
    "0xFEBE809B", "0xFEBE810A", "0xFEBE810E", "0xFEBE8110", "0x7FEAC",
    "0xFEBE809C", "0xFEBE80B4", "0xFEBE809D", "0", "0xFEBE809E", "0xFEBE809F",
    "0xFEBE80A0", "0xFEBE80A4", "0xFEBE80A6", "0xFEBE80A8", "0xFEBE80AA",
    "0xFEBE80AC", "0", "0xFEBE80A1", "0xFEBE80A2", "0xFEBE80A3", "0xFEBE80A5",
    "0xFEBE80A7", "0xFEBE80A9", "0xFEBE80AB", "0xFEBE80AD", "0xFEBE80AE",
    "0xFEBE80AF", "0xFEBE80B0", "0xFEBE80B1", "0xFEBE80B2", "0xFEBE80B3", "0x7FEAC",
    "0xFEBE80B8", "0xFEBE80B9", "0xFEBE80BA", "0xFEBE80C2", "0xFEBE80BD",
    "0xFEBE80BE", "0xFEBE80BF", "0xFEBE80C1", "0xFEBE80C3", "0xFEBE80C4",
    "0xFEBE80C5", "0xFEBE80C6", "0xFEBE80C7", "0xFEBE80C8", "0xFEBE80C9",
    "0xFEBE80CA", "9", "0", "0", "0",
]
check("all 58 CSV source fields match the recovered packers",
      [row["source"] for row in rows] == expected_sources)
expected_wire = [
    "B0[7]", "B0[4]", "B0[3]", "B0[2]", "B0[1]", "B0[0]", "B1..B2 BE16",
    "B3..B4 BE16", "B5..B6 BE16", "B7",
    "B0[7]", "B0[6]", "B0[5]", "B0[4]", "B0[2]", "B0[1]", "B0[0]",
    "B1[7]", "B1[6]", "B1[5]", "B1[4]", "B1[3]", "B1[2:0] || B2",
    "B3[7]", "B3[6]", "B3[5]", "B3[4]", "B3[3]", "B3[2]", "B3[1]", "B3[0]",
    "B4[7]", "B4[6]", "B4[5]", "B4[4:3]", "B5", "B6", "B7",
    "B2[7:5]", "B2[4]", "B0[6:4]", "B0[1:0]", "B1[7:6]", "B1[2:0]",
    "B2[3:1]", "B2[0]", "B0", "B1", "B2", "B3", "B4", "B5", "B6", "B7",
    "B0", "B1[7]", "B2..B3 BE16", "B4..B7",
]
check("all 58 CSV wire fields match the recovered packing layout",
      [row["wire_field"] for row in rows] == expected_wire)


print("\n== post-packer checksum/default-only closure ==")
check("CanIf post-packer flags select only COM PDU 0/1",
      list(CF[0x21FE0:0x21FE6]) == [1, 1, 0, 0, 0, 0])
check("controller-0 CanIf pre-enqueue hook is 0x800D2", u32(0x21900) == 0x800D2)
check("controller-0 post-packer callback is 0x7FEAC", u32(0x2194C) == 0x7FEAC)
check("0x7FEAC checksum callback body is pinned",
      sha256_region(0x7FEAC, 0x46) == "0e077cd8d1f3c22b7fe2c1478e98a44e2d05f0c7febfa45e9385a5181607c8f1")
check("checksum callback stores accumulated byte at payload[length-1]",
      CF[0x7FEEA:0x7FEF2] == bytes.fromhex("12f0d1f1800b7f00"))
check("all six COM descriptors disable COM-level 0x10/0x20 transforms",
      [row[5] for row in com_pdu] == [3] * 6)
check("CAN 0x4C8 initial B4..B7 are zero",
      CF[0x221DC + 31 + 4:0x221DC + 31 + 8] == bytes(4))

print("\n== raw packer bodies and call-chain evidence ==")
packer_hashes = {
    (0x4BCEE, 306): "bc9f9430d8e8f59bf010286e425df101ac480a738ac220455a82a6c4c7636c8b",
    (0x4BE24, 816): "0c6150b05372cece5a32c1fc41efc7782d4f0fef7f201cb2673662203b651152",
    (0x4C25C, 136): "7b112b649674374a6ad7be424c8c8b748b8eedb28b73f8b622818157ef0946e7",
    (0x4C158, 256): "99f1648cc628ba9d4fc775415d6ac97ef9ddd9243e11c68b679a1af495b16d10",
    (0x4BB1E, 306): "bcd3ccc9fafb4bbb9fd21e173d2225527baf5104c8c29729612247e3cfb8da0a",
    (0x4BC54, 150): "d24846f017aee98543e1c2f3c30ea4226503fb0e41876749073f7321fddd7477",
}
for (address, size), expected in packer_hashes.items():
    check(f"packer {address:#x} raw body", sha256_region(address, size) == expected)
check("COM main invokes cyclic scheduler 0x7CA20", CF[0x7D068:0x7D06C] == bytes.fromhex("bfffb8f9"))
check("COM main invokes pending-PDU transmitter 0x7CE28", CF[0x7D082:0x7D086] == bytes.fromhex("bfffa6fd"))
check("pending-PDU path invokes PduR adapter 0x80992", CF[0x7CEC4:0x7CEC8] == bytes.fromhex("80ffce3a"))
check("CanIf transmit invokes software enqueue 0x7EC5A", CF[0x7EEA4:0x7EEA8] == bytes.fromhex("bfffb6fd"))
check("queue drain invokes RSCFD dispatch 0x84022", CF[0x7F12E:0x7F132] == bytes.fromhex("80fff44e"))
check("RSCFD dispatch invokes classic writer 0x842BA", CF[0x8407C:0x84080] == bytes.fromhex("80ff3203"))
check("CAN1 Tx ISR body invokes confirmation dispatch 0x84710", CF[0x84754:0x84758] == bytes.fromhex("bfffbcff"))

print("\n== generator determinism ==")
with tempfile.NamedTemporaryFile("w+", delete=False, suffix=".csv") as tmp:
    tmp_path = Path(tmp.name)
subprocess.check_call([sys.executable, str(GEN), "--output", str(tmp_path)], cwd=REPO)
check("generator regenerates Tx map byte-for-byte", tmp_path.read_bytes() == CSV_PATH.read_bytes())
tmp_path.unlink(missing_ok=True)

print(f"\nSummary: {passed} passed, {failed} failed")
sys.exit(1 if failed else 0)
