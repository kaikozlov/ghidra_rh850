#!/usr/bin/env python3
"""Verify the callback-free ephemeral SecOC scheduler bridge against firmware truth."""
from __future__ import annotations

import csv
import hashlib
import json
import struct
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
CF = (REPO / "firmware" / "RH850_P1M-E_CodeFlash.bin").read_bytes()
SOURCE = REPO / "exploit" / "ephemeral_runtime" / "main.c"
BUILDER = REPO / "exploit" / "ephemeral_runtime" / "build_shellcode.py"
AUDIT = REPO / "exploit" / "ephemeral_runtime" / "audited_build.json"
passed = failed = 0


def check(name: str, condition: object, detail: str = "") -> None:
    global passed, failed
    ok = bool(condition)
    passed += int(ok)
    failed += int(not ok)
    suffix = f" ({detail})" if detail else ""
    print(f"[{'PASS' if ok else 'FAIL'}][raw_bytes] {name}{suffix}")


def u16(a: int) -> int:
    return struct.unpack_from("<H", CF, a)[0]


def u32(a: int) -> int:
    return struct.unpack_from("<I", CF, a)[0]


def jarl22_target(a: int) -> int:
    ins = u32(a)
    high6 = ins & 0x3F
    if high6 & 0x20:
        high6 -= 0x40
    disp = (high6 << 16) + (ins >> 16)
    return (a + disp) & 0xFFFFFFFF


print("== stock boot/application transition ==")
check("boot handoff calls four stock transition initializers",
      [jarl22_target(a) for a in (0x13B4, 0x13B8, 0x13BC, 0x13C0)] ==
      [0x0C9A, 0x0E54, 0x0F80, 0x10C6])
check("boot handoff calls validity gate", jarl22_target(0x13C4) == 0x119E)
check("boot handoff tests validity result against zero",
      CF[0x13C8:0x13CC] == bytes.fromhex("e051c215"))
check("application context installs INTBP 0x20200", CF[0x70524:0x7052A] == bytes.fromhex("2b0600020200"))
check("application context installs EBASE 0x20000", CF[0x70530:0x70536] == bytes.fromhex("2b0600000200"))
check("application context installs GP FEBEB800", CF[0x7053C:0x70542] == bytes.fromhex("240600b8befe"))
check("application context installs TP 0x23EE4", CF[0x70542:0x70548] == bytes.fromhex("2506e43e0200"))
check("application context installs SP FEBE2000 and returns through LP",
      CF[0x70548:0x70550] == bytes.fromhex("23060020befe7f00"))

print("\n== stock startup sequence is machine-decodable ==")
startup_sites = list(range(0x62760, 0x627B4, 4))
expected_startup = [
    0x6221C, 0x62232, 0x62252, 0x5FDA8, 0x60026, 0x601CA, 0x622A2,
    0x61B18, 0x6257E, 0x5FC78, 0x61DD4, 0x6263E, 0x62662, 0x62682,
    0x627C6, 0x70550, 0x626A2, 0x61CC8, 0x65626, 0x626F6, 0x6555C,
]
check("startup coordinator contains exactly 21 consecutive direct JARL slots", len(startup_sites) == 21)
check("JARL disp22 decoder reproduces exact stock startup targets",
      [jarl22_target(a) for a in startup_sites] == expected_startup)
check("stock startup then calls final init 0x6F15A with r6=0",
      CF[0x627B4:0x627BA] == bytes.fromhex("003280ffa4c9") and jarl22_target(0x627B6) == 0x6F15A)
check("stock startup enables interrupts then enters foreground loop",
      CF[0x627BA:0x627BE] == bytes.fromhex("e0876001") and jarl22_target(0x627BE) == 0x64FCC)

print("\n== foreground splice point preserves stock order ==")
stock_foreground_calls = [
    jarl22_target(a) for a in
    (0x64FF2, 0x64FF6, 0x64FFA, 0x64FFE, 0x65002, 0x65006, 0x6500A, 0x6500E)
]
check("stock foreground top-level call order is pinned",
      stock_foreground_calls == [0x643AC, 0x702E8, 0x65F5C, 0x70308, 0x65750, 0x702E8, 0x65C60, 0x70308])
check("stock TAUJ0 CH3 poll/clear is TST1+CLR1",
      CF[0x64FD0:0x64FDA] == bytes.fromhex("c0e711b1e2fdc0a711b1"))
check("0x65750 six-call order places comm/SecOC before system-mode/control",
      [jarl22_target(a) for a in range(0x65754, 0x6576C, 4)] ==
      [0x68C0C, 0x791C4, 0x96BAC, 0x68DE6, 0x57AC2, 0x6547C])
check("0x791C4 reaches SecOC main wrapper before returning",
      jarl22_target(0x79224) == 0x69380)
check("SecOC wrapper chain reaches generated receive worker",
      jarl22_target(0x69384) == 0x8DD78 and
      jarl22_target(0x8DDA4) == 0x8DD38 and
      jarl22_target(0x8DD4E) == 0x8E700)
check("generated receive worker invokes verify then Gate-2",
      jarl22_target(0x8E720) == 0x8E4BA and jarl22_target(0x8E72E) == 0x8E67A)

print("\n== pre-verification secured-record geometry ==")
records = [0x25970 + i * 0x50 for i in range(6)]
check("SecOC record order is sync,2E4,131,132,090,0D7",
      [u16(a + 0x0A) for a in records] == [0x00F, 0x2E4, 0x131, 0x132, 0x090, 0x0D7])
check("2E4/131 records map to application PDU 6/26",
      [u16(records[i] + 0x34) for i in (1, 2)] == [6, 26])
check("2E4/131 secured buffers are exactly eight bytes",
      [u32(records[i] + 0x3C) for i in (1, 2)] == [8, 8])
check("2E4/131 raw-buffer offsets are 8/16 from FEBE5488",
      [u32(records[i] + 0x28) for i in (1, 2)] == [8, 16])
check("SecOC storage backend exposes descriptor base FEBE5452",
      CF[0x8D754:0x8D75A] == bytes.fromhex("240e529c010d"))
check("SecOC storage backend exposes queue-head base FEBE544C",
      CF[0x8D75C:0x8D762] == bytes.fromhex("240e4c9c030d"))
check("SecOC storage backend exposes raw-buffer base FEBE5488",
      CF[0x8D762:0x8D768] == bytes.fromhex("240e889c050d"))

print("\n== stock COM destination joins ==")
with (REPO / "data" / "application_rx_map.csv").open(newline="", encoding="utf-8") as f:
    rows = list(csv.DictReader(f))
by_can = {}
for row in rows:
    by_can.setdefault(row["can_id"], row)
check("generated receive map pins 2E4 COM buffer/counter",
      by_can["0x2E4"]["com_buf_ram"] == "0xFEBE4A70" and by_can["0x2E4"]["update_counter_ram"] == "0xFEBE5332")
check("generated receive map pins 131 COM buffer/counter",
      by_can["0x131"]["com_buf_ram"] == "0xFEBE4B10" and by_can["0x131"]["update_counter_ram"] == "0xFEBE5346")
check("2E4 request/torque unpack destinations remain stock",
      any(r["can_id"] == "0x2E4" and r["signal_id"] == "60" and r["dest"] == "0xFEBE7F98" for r in rows) and
      any(r["can_id"] == "0x2E4" and r["signal_id"] == "61" and r["dest"] == "0xFEBE7F94" for r in rows))

print("\n== tracked resident runtime contract ==")
source = SOURCE.read_text(encoding="utf-8")
builder = BUILDER.read_text(encoding="utf-8")
audit = json.loads(AUDIT.read_text(encoding="utf-8"))
source_hash = hashlib.sha256(SOURCE.read_bytes()).hexdigest()
builder_hash = hashlib.sha256(BUILDER.read_bytes()).hexdigest()
bindings = {item["path"]: item["sha256"] for item in audit["sources"]}
check("runtime source is bound by audited build", bindings["exploit/ephemeral_runtime/main.c"] == source_hash)
check("runtime builder is bound by audited build", bindings["exploit/ephemeral_runtime/build_shellcode.py"] == builder_hash)
check("audited resident image fits 0x308-byte pocket with 72-byte headroom",
      audit["shellcode"]["size"] == 704 and audit["shellcode"]["headroom"] == 72 and audit["compile_contract"]["retained_limit"] == 776)
check("audited resident image has exact executable SHA",
      audit["shellcode"]["sha256"] == "8f486d36ae38d233165563ad2cc4a71d006cf5c8cf9a876345a3b6ab72f10495")
check("audited build pins zero relocations and entry offset zero",
      audit["compile_contract"]["relocations"] == 0 and audit["shellcode"]["entry_offset"] == 0)
check("audited build is explicitly not bench-validated",
      audit["review_status"] == "audited-static-not-bench-validated")
check("builder pins exact Docker image content identity",
      "2d5e4c27e490302fbcd05e896e31bf36109a2c5aab899b500eecbebd3fec8c24" in builder)
check("runtime reuses stock startup JARL stream instead of duplicating a target table",
      "APP_STARTUP_FIRST_JARL" in source and "APP_STARTUP_AFTER_JARLS" in source and "signed_high6" in source)
check("runtime bridge is limited to two steering profiles and MAC28-zero marker",
      "BRIDGE_PROFILE_COUNT       2u" in source and "MAC28_ZERO_MASK            0xFFFFFF0Fu" in source)
check("runtime calls stock COM RxIndication before stock system-mode dispatcher",
      source.index("call0(COM_AND_SECOC_MAIN)") < source.index("((com_rx_t)APPLICATION_COM_RX)") < source.index("call0(SYSTEM_MODE_DISPATCH)"))
check("runtime source contains no CodeFlash/FACI programming primitive",
      all(token not in source.lower() for token in ("faci_", "flash_block_rmw", "program_page", "codeflash_write")))
check("workstream contains no live deploy wrapper",
      not any(p.name.startswith(("deploy", "flash", "run_live")) for p in (REPO / "exploit" / "ephemeral_runtime").iterdir()))

print(f"\nResults: {passed} passed, {failed} failed")
if failed:
    raise SystemExit(1)
