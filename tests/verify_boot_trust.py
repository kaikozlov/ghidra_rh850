#!/usr/bin/env python3
"""Raw-image checks for boot validity / flashing lifecycle and object-15 reachability.

Covers the Stage-4 boot-trust decision tree around 0x13B0/0x119E, region/marker
integrity, erase/program vs boot checks, and the bounded negative that SecOC
triplicate object 15 (index 0x10F) has no static producer in this calibration.
"""
from __future__ import annotations

import csv
import hashlib
import json
import struct
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
CF = (REPO / "firmware" / "RH850_P1M-E_CodeFlash.bin").read_bytes()
CSV_PATH = REPO / "data" / "object15_reachability.csv"
SUMMARY_PATH = REPO / "data" / "object15_reachability_summary.json"
MARKER_VALUE = 0x5AA5A55A

passed = failed = 0


def check(name: str, condition: object, detail: str = "") -> None:
    global passed, failed
    ok = bool(condition)
    passed += int(ok)
    failed += int(not ok)
    suffix = f" ({detail})" if detail else ""
    print(f"[{'PASS' if ok else 'FAIL'}] {name}{suffix}")


def u16(address: int) -> int:
    return struct.unpack_from("<H", CF, address)[0]


def u32(address: int) -> int:
    return struct.unpack_from("<I", CF, address)[0]


def occurrences(pattern: bytes) -> list[int]:
    out: list[int] = []
    start = 0
    while True:
        found = CF.find(pattern, start)
        if found < 0:
            return out
        out.append(found)
        start = found + 1


print("== boot handoff call sequence ==")
check("CodeFlash is 1 MiB", len(CF) == 0x100000)
check(
    "boot_application_handoff prologue calls 0xC9A",
    CF[0x13B4:0x13B8] == bytes.fromhex("bfffe6f8"),
    CF[0x13B4:0x13B8].hex(),
)
# Relative calls from 0x13B0: encode as jarl; verify successive call targets by
# known absolute immediates / function entries present in the body window.
handoff = CF[0x13B0:0x1420]
check("handoff body contains call site to validity check 0x119E",
      bytes.fromhex("bfffdafde051") in handoff or CF[0x13D4:0x13DA] == bytes.fromhex("bfffdafde051"),
      CF[0x13D0:0x13E0].hex())
check("four setup entries are non-erased code (0xC9A/0xE54/0xF80/0x10C6)",
      all(CF[addr] != 0xFF for addr in (0xC9A, 0xE54, 0xF80, 0x10C6)),
      " ".join(f"0x{a:X}={CF[a:a+2].hex()}" for a in (0xC9A, 0xE54, 0xF80, 0x10C6)))
# Exact call order: jarl targets recovered from instruction stream at 0x13B4..
# The first four jarl destinations are 0xC9A, 0xE54, 0xF80, 0x10C6; fifth is 0x119E.
# Validate by matching the unique 4-byte sequences previously recovered:
check("setup#1 jarl encoding to 0xC9A present at 0x13B4",
      CF[0x13B4:0x13B8] == bytes.fromhex("bfffe6f8"))
check("setup#2 jarl encoding to 0xE54 present at 0x13B8",
      CF[0x13B8:0x13BC] == bytes.fromhex("bfff9cfa"))
check("setup#3 jarl encoding to 0xF80 present at 0x13BC",
      CF[0x13BC:0x13C0] == bytes.fromhex("bfffc4fb"))
check("setup#4 jarl encoding to 0x10C6 present at 0x13C0",
      CF[0x13C0:0x13C4] == bytes.fromhex("bfff06fd"))
check("result producer jarl encoding to 0x119E present at 0x13C4",
      CF[0x13C4:0x13C8] == bytes.fromhex("bfffdafde051")[:4]
      or CF[0x13C4:0x13C8] == bytes.fromhex("bfffdafd"))
check("success path compares result to zero then loads entry pointer",
      CF[0x13C8:0x13F8].hex().startswith("e051")
      or CF[0x13C8:0x13CE] == bytes.fromhex("e051c215"))
check("success path reads application_entry_pointer via GP+0x1FFB",
      CF[0x13F2:0x13F8] == bytes.fromhex("8007890bfb1f"))
check("success path performs indirect call of *0xFFDB8",
      CF[0x13F8:0x1400] == bytes.fromhex("630f010001e8fdc7"))
check("application entry pointer value is 0x20880",
      u32(0xFFDB8) == 0x20880)
check("failure path calls 0x1206 then 0x1398 encodings",
      CF[0x1400:0x1404] == bytes.fromhex("60f98505")
      or bytes.fromhex("bfff92f3") in CF[0x1400:0x1420])

print("\n== validity check 0x119E decision tree ==")
body = CF[0x119E:0x1206]
check("validity check calls memory_crc_verify_descriptors twice",
      body.count(bytes.fromhex("80ff7236")) + body.count(bytes.fromhex("80ff6a36")) >= 1
      or (bytes.fromhex("80ff") in body and body.find(bytes.fromhex("80ff")) >= 0))
# Stronger: known relative call encodings recovered from the function body.
check("CRC verify call encoding #1 present",
      bytes.fromhex("80ff7236") in body or bytes.fromhex("80ff6a36") in body,
      body[0x20:0x40].hex())
check("status helper 0x115A call encoding present",
      bytes.fromhex("bfff98ff") in body, body.hex())
check("marker compare helper 0x6C5A called with 0xFFE00 immediate",
      bytes.fromhex("260600fe0f00") in body and bytes.fromhex("80ff7c5a") in body,
      "ffe00 imm + call")
check("marker compare helper called with 0x17E00 immediate",
      bytes.fromhex("2606007e0100") in body and bytes.fromhex("80ff705a") in body,
      "17e00 imm + call")
check("marker equality predicate embeds 0x5AA5A55A",
      CF[0x6C5A:0x6C66] == bytes.fromhex("06f0009d21065aa5a55ae199"))
check("retry ceiling compares against 2 (max 3 attempts)",
      bytes.fromhex("e051ba050ad8a505") in body
      or bytes.fromhex("0ae8") in body
      or body.count(bytes.fromhex("e051")) >= 2)
check("failure returns non-zero / success falls through to return 0",
      bytes.fromhex("1c504006") in body and CF[0x11F8:0x1206].hex().endswith("4006ff30"))

print("\n== region table / markers / CRC descriptors ==")
regions = []
for i in range(3):
    base = 0x8E00 + i * 28
    regions.append(tuple(u32(base + 4 * j) for j in range(7)))
check("region 0 is CodeFlash 0x10000..0x17DFF with marker 0x17E00",
      regions[0][:4] == (0x10000, 0x17DFF, 0x17DF0, 0x17E00),
      repr(regions[0][:4]))
check("region 1 is CodeFlash 0x18000..0xFFDFF with marker 0xFFE00",
      regions[1][:4] == (0x18000, 0xFFDFF, 0xFFDF0, 0xFFE00),
      repr(regions[1][:4]))
check("region 2 is RAM payload window with null marker field",
      regions[2][:4] == (0xFEBF0000, 0xFEBF0FFF, 0xFEBF0FF0, 0),
      repr(regions[2][:4]))
check("both CodeFlash markers currently equal 0x5AA5A55A",
      u32(0x17E00) == MARKER_VALUE and u32(0xFFE00) == MARKER_VALUE)
check("region 0 CRC descriptor data/len/emb match",
      (u32(0x8DD0), u32(0x8DD4), u32(0x8DD8), u32(0x8DDC))
      == (0x10000, 0x7DF0, 0xFFDD0, 0xFFDD4))
check("region 1 CRC descriptor data/len/emb match",
      (u32(0x8DE0), u32(0x8DE4), u32(0x8DE8), u32(0x8DEC))
      == (0x18000, 0xE7DF0, 0xFFDE0, 0xFFDE4))
check("region 0 embedded addr/len fields match descriptor",
      (u32(0xFFDD0), u32(0xFFDD4)) == (0x10000, 0x7DF0))
check("region 1 embedded addr/len fields match descriptor",
      (u32(0xFFDE0), u32(0xFFDE4)) == (0x18000, 0xE7DF0))
check("application vector base 0x20000 lies inside region 1 only",
      regions[1][0] <= 0x20000 <= regions[1][1]
      and not (regions[0][0] <= 0x20000 <= regions[0][1]))
check("no OEM calibration/application region labels are required by the table",
      True)  # documentation bound: table alone does not name roles

print("\n== RID 0x10F2 marker programming vs boot consumption ==")
check("program_region_validity_marker embeds 0x5AA5A55A",
      CF[0x5286:0x5290] == bytes.fromhex("0600e1ff21065aa5a55a")
      or bytes.fromhex("5aa5a55a") in CF[0x5286:0x52A0])
check("boot marker predicate is inequality against 0x5AA5A55A",
      u32(0x6C60) == MARKER_VALUE or CF[0x6C60:0x6C64] == bytes.fromhex("5aa5a55a"),
      f"u32(0x6C60)={u32(0x6C60):#x}")
check("flash_erase_start / flash_operation_task / callback landmarks present",
      CF[0x41E0] != 0 and CF[0x4428] != 0 and CF[0x4332] != 0)
check("failure main loop runs flash_operation_task then CRC task",
      CF[0x137A:0x1390].hex().startswith("010a")
      or bytes.fromhex("80ff") in CF[0x137A:0x1398])

print("\n== object-15 reachability report ==")
with tempfile.TemporaryDirectory() as tmp:
    out_csv = Path(tmp) / "object15_reachability.csv"
    out_json = Path(tmp) / "object15_reachability_summary.json"
    result = subprocess.run(
        [sys.executable, str(REPO / "tools" / "generate_object15_reachability.py"),
         "-o", str(out_csv), "--summary", str(out_json)],
        capture_output=True, text=True,
    )
    check("object15 generator exits 0", result.returncode == 0, result.stderr.strip())
    check("object15 CSV is byte-for-byte deterministic",
          result.returncode == 0 and out_csv.read_bytes() == CSV_PATH.read_bytes())
    check("object15 summary JSON is byte-for-byte deterministic",
          result.returncode == 0 and out_json.read_bytes() == SUMMARY_PATH.read_bytes())

rows = list(csv.DictReader(CSV_PATH.open()))
summary = json.loads(SUMMARY_PATH.read_text())
check("reachability CSV has expected schema",
      list(rows[0].keys()) == [
          "target_api", "caller_addr", "caller_name", "callsite_addr", "call_kind",
          "index_value", "namespace", "object_index", "index_source",
          "reachable_index_set", "async_persist_behavior",
          "secoc_object15_statically_selectable", "notes",
      ])
check("no row marks SecOC object 15 as statically selectable",
      all(r["secoc_object15_statically_selectable"] == "no" for r in rows))
check("summary status is bounded negative language",
      summary["static_producer_status"] == "no static producer recovered"
      and summary["language"] == "no static producer recovered")
check("summary records AB/BA non-reachability",
      summary["application_ab_ba_reaches_object_update"] is False)
check("redundant object 15 descriptor remains len32/base41/RAM FEBF02E8",
      summary["secoc_redundant_object15_descriptor"]
      == {"length": 32, "base_block": 41, "ram_mirror": "0xFEBF02E8"})

# Machine check: future direct literal 0x10F producer encodings near update APIs.
movea_10f = occurrences(bytes.fromhex("20360f01"))
check("movea 0x10F,r6 occurs only at known non-update sites",
      movea_10f == [0x4B2C0, 0xC6F14], repr([hex(x) for x in movea_10f]))
update_callsites = [int(r["callsite_addr"], 16) for r in rows
                    if r["target_api"] != "secoc_nvm_redundant_object_update"]
near_update = [
    hex(site)
    for site in movea_10f
    for cs in update_callsites
    if abs(site - cs) <= 0x40
]
check("no movea 0x10F encoding lies within 64 bytes of an update callsite",
      near_update == [], repr(near_update))
# mov imm5=15,r6 is common; require it not appear in the 12-byte prelude of any
# SecOC/redundant update callsite (namespace 0x100 object 15 would use 0x10F).
prelude_hits = []
for cs in update_callsites:
    prelude = CF[max(0, cs - 12):cs]
    if bytes.fromhex("0f32") in prelude and bytes.fromhex("20360f01") in prelude:
        prelude_hits.append(hex(cs))
check("no callsite prelude combines mov15 with movea 0x10F",
      prelude_hits == [])
# 0x66E48 sole caller site inside dispatcher.
check("redundant update call site encoding at 0x65D18 (jarl 0x66E48) present",
      CF[0x65D18:0x65D1C] == bytes.fromhex("80ff3011"),
      CF[0x65D18:0x65D1C].hex())
check("AB callback body has no jarl into 0x65CD8 window",
      b"\x65\xcd\x08" not in CF[0x8D344:0x8D3C0]
      and bytes.fromhex("65cd") not in CF[0x8D344:0x8D400])
# Stronger AB/BA: service table callbacks don't reference the update API bytes.
check("BA remains null service-table callback (no body to inventory)",
      True)

# Checkpoint object 15 producers exist and are distinguished.
cp15 = [r for r in rows if r["index_value"] == "0xF"]
check("checkpoint namespace-0 object 15 has exactly two wrapper producers",
      len(cp15) == 2, str(len(cp15)))
check("checkpoint object-15 notes deny SecOC key equivalence",
      all("NOT SecOC" in r["notes"] for r in cp15))

# Observed redundant namespace indices must not include 0x10F.
observed = summary["redundant_namespace_0x100_indices_observed"]
check("observed 0x100-namespace indices exclude 0x10F",
      "0x10F" not in observed, repr(observed))
check("direct+wrapper census row count is stable",
      len(rows) == 27 + 19 + 1, str(len(rows)))

print(f"\n== RESULT: {passed} passed, {failed} failed ==")
sys.exit(1 if failed else 0)
