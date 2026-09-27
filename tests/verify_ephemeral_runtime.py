#!/usr/bin/env python3
"""Verify the callback-free ephemeral SecOC scheduler bridge against firmware truth."""
from __future__ import annotations

import csv
import json
import struct
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
CF = (REPO / "firmware" / "RH850_P1M-E_CodeFlash.bin").read_bytes()
SOURCE = REPO / "exploit" / "ephemeral_runtime" / "main.c"
CANARY_SOURCE = REPO / "exploit" / "ephemeral_runtime" / "canary.c"
SUBSTITUTION_PLANNER = REPO / "exploit" / "ephemeral_runtime" / "build_substitution_plan.py"
CORPUS = REPO / "data" / "generated" / "decompilations.jsonl"
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
check("runtime source contains no CodeFlash/FACI programming primitive",
      all(token not in source.lower() for token in ("faci_", "flash_block_rmw", "program_page", "codeflash_write")))
installer_source = (REPO / "exploit" / "ephemeral_runtime" / "live_installer.py").read_text(encoding="utf-8")
check("live installer is isolated-bench gated and defaults to plan-only",
      "--bench-isolated" in installer_source and "--execute" in installer_source and
      "--execute requires --bench-isolated" in installer_source)
check("live installer retains initial boot SecurityAccess boundary",
      "initial_authentication_bypassed" in installer_source and "load_security_secret" in installer_source and
      "load_payload_secret" not in installer_source)

print("\n== inert scheduler canary ==")
canary_source = CANARY_SOURCE.read_text(encoding="utf-8")
check("canary preserves the manifest-resolved stock aggregate and contains no COM/SecOC bridge",
      "TARGET_FG_AGGREGATE" in canary_source and
      "application_com_rx" not in canary_source.lower() and "MAC28" not in canary_source)
# Heartbeat is beyond startup CodeFlash shadow copy and remains XCP-readable.
heartbeat = 0xFEBFFBF0
exclusion_count = u32(0x2B3B8)
exclusions = [struct.unpack_from("<II", CF, 0x293F4 + i * 8) for i in range(exclusion_count)]
check("heartbeat is above startup shadow-copy end and inside XCP shadow window",
      heartbeat > 0xFEBFF9EF and 0xFEBF7C00 <= heartbeat <= 0xFEBFFBFF)
check("heartbeat lies outside all five XCP/RMBA RAM exclusions",
      all(not (lo <= heartbeat <= hi) for lo, hi in exclusions))
heartbeat_refs = []
for line in CORPUS.read_text(encoding="utf-8").splitlines():
    obj = json.loads(line)
    if obj.get("record") != "function":
        continue
    for ref in obj.get("data_references", []):
        if int(ref["to_addr"], 16) == heartbeat:
            heartbeat_refs.append(ref)
check("heartbeat has no canonical application direct reference", not heartbeat_refs, repr(heartbeat_refs))

print("\n== post-auth substitution / execution ordering ==")
planner = SUBSTITUTION_PLANNER.read_text(encoding="utf-8")
check("planner explicitly requires prior successful 10F0 authentication",
      "selected target-accepted encrypted bootstrap fixture has been uploaded and passed RID 0x10F0" in planner and
      '"initial_authentication_bypassed": False' in planner)
check("flash_erase_start stages operation type 2 rather than invoking payload callback",
      CF[0x4244:0x424A] == bytes.fromhex("020a440f9c91"))
check("operation-type-2 worker reaches flash_driver_call_block_operation",
      jarl22_target(0x4538) == 0x4332)
check("block-operation helper loads FEBF0FD0 and indirect-calls it",
      CF[0x434C:0x4362] == bytes.fromhex("40eebffe3defd10f0ad81c380142234e0300fdc760f9"))

print(f"\nResults: {passed} passed, {failed} failed")
if failed:
    raise SystemExit(1)
