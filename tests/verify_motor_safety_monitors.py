#!/usr/bin/env python3
"""Verify the recovered nine-channel plausibility/deadline monitor family."""
from __future__ import annotations

import csv
import hashlib
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CF = (ROOT / "firmware" / "RH850_P1M-E_CodeFlash.bin").read_bytes()
CSV_PATH = ROOT / "data" / "motor_safety_monitors.csv"
REPORT = ROOT / "docs" / "architecture" / "control-partition.md"

passed = failed = 0

def check(name: str, cond: object, detail: str = "") -> None:
    global passed, failed
    ok = bool(cond)
    passed += int(ok); failed += int(not ok)
    print(f"[{'PASS' if ok else 'FAIL'}] {name}" + (f" ({detail})" if detail else ""))

def u32(off: int) -> int:
    return struct.unpack_from("<I", CF, off)[0]

def sha(off: int, size: int) -> str:
    return hashlib.sha256(CF[off:off+size]).hexdigest()

print("== nine-channel monitor artifact ==")
with CSV_PATH.open(newline="", encoding="utf-8") as fh:
    rows = list(csv.DictReader(fh))
check("artifact has exactly nine channels", len(rows) == 9, str(len(rows)))
check("channel IDs are 0..8", [int(r["channel"]) for r in rows] == list(range(9)))
check("status vector covers FEBE797C..7984 exactly",
      {int(r["status_ram"], 0) for r in rows} == set(range(0xFEBE797C, 0xFEBE7985)))
check("status indices form 0..8",
      {int(r["status_index"]) for r in rows} == set(range(9)))
check("all rows feed aggregate 0x43F28", {r["aggregate_addr"] for r in rows} == {"0x43F28"})

for r in rows:
    ch = int(r["channel"])
    setup = int(r["setup_addr"], 0); size = int(r["setup_size"])
    table = int(r["callback_table"], 0); cb = int(r["primary_callback"], 0)
    threshold = int(r["threshold_record"], 0)
    check(f"channel {ch} setup body hash", sha(setup, size) == r["setup_sha256"])
    check(f"channel {ch} callback table duplicates primary callback in slots 0/1",
          u32(table) == cb and u32(table+4) == cb)
    # The setup embeds threshold/table addresses as 32-bit immediates in the
    # bounded function body. This proves each CSV row belongs to that setup.
    body = CF[setup:setup+size]
    check(f"channel {ch} setup embeds threshold record",
          threshold.to_bytes(4, "little") in body)
    check(f"channel {ch} setup embeds callback table",
          table.to_bytes(4, "little") in body)

print("\n== formerly 'isolated interlocks' ==")
# The three old candidates are called from callbacks stored in the tables.
check("0x43784 wrapper calls 0x43716", bytes.fromhex("bfff38ff") in CF[0x43784:0x4382A])
check("0x43934 wrapper calls 0x438C6", bytes.fromhex("bfff38ff") in CF[0x43934:0x439DA])
check("0x43B16 wrapper calls 0x43A78 twice", CF[0x43B16:0x43BB8].count(bytes.fromhex("bffffafe")) == 1
      and CF[0x43B16:0x43BB8].count(bytes.fromhex("bffff0fe")) == 1)
# Return-domain correction: 43716/438C6 are 0/5A predicate helpers, while
# 43A78 participates in the 11/22/33 lifecycle vocabulary.
check("0x43716/0x438C6 contain 0x5A success return",
      bytes.fromhex("20565a00") in CF[0x43716:0x43784]
      and bytes.fromhex("20565a00") in CF[0x438C6:0x43934])
check("0x43A78 contains 0x11/0x22/0x33 lifecycle returns",
      all(v in CF[0x43A78:0x43B16] for v in
          (bytes.fromhex("20561100"), bytes.fromhex("20562200"), bytes.fromhex("20563300"))))

print("\n== aggregate and downstream boundary ==")
check("aggregate monitor body pinned",
      sha(0x43F28, 436) == "e32a6f11a9466703c09d6e21372bb840a4db4c4be924114dae330ad652bf4f86")
check("downstream debounced monitor body pinned",
      sha(0xB9D36, 350) == "6d76dfa8813337b8d7e8ed038f5e9543b2a72b842460d2f5afbcec90caa4ad72")
# 43F28 uses shared diagnostic/event helpers rather than the motor d/q/PWM
# functions. Pin representative calls to the selector-bitmask and status vector.
check("0x43F28 calls shared selector/event aggregator 0x3BFD8",
      bytes.fromhex("bfff7680") in CF[0x43F28:0x440DC])
# No direct calls from 43F28 or B9D36 into the proved motor-control cluster.
def branch_target(addr: int) -> int | None:
    if addr + 4 > len(CF): return None
    w0, w1 = struct.unpack_from("<HH", CF, addr)
    if ((w0 >> 6) & 0x1F) != 0x1E or (w1 & 1): return None
    hi = w0 & 0x3F
    if hi & 0x20: hi -= 0x40
    return addr + (hi << 16) + w1
motor = {0x37712,0x36902,0x36A44,0x38464,0x38554,0x3875A,0x60BFA,0x60DDC}
for start,end,name in [(0x43F28,0x440DC,"aggregate"),(0xB9D36,0xB9E94,"downstream")]:
    targets={t for a in range(start,end,2) if (t:=branch_target(a)) is not None}
    check(f"{name} has no direct call/jump to proved motor d/q/PWM stages", not (targets & motor),
          repr(sorted(hex(x) for x in targets & motor)))

text = REPORT.read_text(encoding="utf-8") if REPORT.exists() else ""
for token in ("nine-channel", "0x289EC", "0x43F28", "0xB9D36", "data/motor_safety_monitors.csv"):
    check(f"canonical report contains {token}", token.lower() in text.lower())

print(f"\nSummary: {passed} passed, {failed} failed")
sys.exit(1 if failed else 0)
