#!/usr/bin/env python3
"""Synthetic boundary tests for the shared gear/READY all-source census accumulator.

Exercises the receive/echo/sendcan channel split, raw source/DLC retention,
per-source coverage denominators, and the sufficient-DLC gate for selected-field
value counts without requiring any external rlog or openpilot checkout.
"""
from __future__ import annotations

from tools.toyota_support.toyota_route_opendbc_common import GEAR_READY_CENSUS_IDS, GearReadyCensus

passed = failed = 0


def check(name: str, condition: object, detail: str = "") -> None:
    global passed, failed
    ok = bool(condition)
    passed += int(ok)
    failed += int(not ok)
    suffix = f" ({detail})" if detail else ""
    print(f"[{'PASS' if ok else 'FAIL'}][synthetic_census_check] {name}{suffix}")


def feed(census: GearReadyCensus) -> None:
    # Received vehicle traffic on logical buses 0/1/2 plus non-census filler so
    # per-source totals carry a coverage denominator independent of the IDs.
    for raw in (0x80, 0x40, 0x10):
        census.add_can(1, 0x3BF, bytes([raw, 0, 0, 1, 0, 0x74, 0xDE, 0x47]))
    census.add_can(1, 0x0AA, bytes(8))
    census.add_can(1, 0x127, bytes.fromhex("000000000030"))  # dlc 6: gear nibble sufficient
    census.add_can(1, 0x127, bytes.fromhex("0000000000"))  # dlc 5: insufficient, DLC count only
    census.add_can(0, 0x1A2, bytes(8))
    census.add_can(2, 0x0AA, bytes(8))
    census.add_can(2, 0x3BF, bytes(32))  # FD-length DLC on a census ID is retained unfiltered
    census.add_can(2, 0x2A1, bytes.fromhex("0000000004000000"))  # dlc 8: byte 4 sufficient
    census.add_can(2, 0x2A1, bytes.fromhex("000000000400"))  # dlc 6 >= min 5: sufficient
    census.add_can(2, 0x2A1, bytes.fromhex("00000000"))  # dlc 4: insufficient, DLC count only
    census.add_can(1, 0x51E, b"\x80")  # dlc 1 is sufficient for B0[7]
    census.add_can(1, 0x51E, b"\x00")
    # Panda echo channels and sendcan stay distinct from received traffic.
    census.add_can(129, 0x3BF, bytes.fromhex("100001005fc18f5f"))  # returned Tx echo (bus 1)
    census.add_can(193, 0x3BF, bytes.fromhex("100001005fc18f5f"))  # rejected Tx echo (bus 1)
    census.add_can(200, 0x0AA, bytes(8))  # rejected echo of a non-census ID
    census.add_sendcan(1, 0x127, bytes.fromhex("000000000030"))  # attempted Tx of the same payload


census = GearReadyCensus()
feed(census)
doc = census.result("ab" * 32, 1234)
rx = doc["channels"]["received_can"]


print("\n== received channel and DLC boundaries ==")
g3bf = rx["ids"]["0x3BF"]
check("received 0x3BF retains every recorded source/DLC",
      g3bf["source_dlc_counts"] == {"src=1 dlc=8": 3, "src=2 dlc=32": 1} and g3bf["frame_count"] == 4)
check("received 0x3BF raw byte0 values counted for every sufficient DLC",
      g3bf["selected_field_value_counts"] == {"0": 1, "16": 1, "64": 1, "128": 1})
g127 = rx["ids"]["0x127"]
check("received 0x127 selected field gated on min DLC 6",
      g127["frame_count"] == 2 and
      g127["source_dlc_counts"] == {"src=1 dlc=5": 1, "src=1 dlc=6": 1} and
      g127["selected_field_value_counts"] == {"3": 1})
g2a1 = rx["ids"]["0x2A1"]
check("received 0x2A1 counts byte4 only from DLC >= 5",
      g2a1["source_dlc_counts"] == {"src=2 dlc=4": 1, "src=2 dlc=6": 1, "src=2 dlc=8": 1} and
      g2a1["frame_count"] == 3 and g2a1["selected_field_value_counts"] == {"4": 2})
g51e = rx["ids"]["0x51E"]
check("received 0x51E B0[7] decodes at minimal DLC 1",
      g51e["source_dlc_counts"] == {"src=1 dlc=1": 2} and
      g51e["selected_field_value_counts"] == {"0": 1, "1": 1})
check("received per-source totals give the coverage denominator across all IDs",
      rx["source_totals"] == {"0": 1, "1": 8, "2": 5} and rx["record_count"] == 14)

print("\n== echo and sendcan channel boundaries ==")
check("returned Tx echoes are separated from received traffic",
      doc["channels"]["returned_can_echo"]["source_totals"] == {"129": 1} and
      doc["channels"]["returned_can_echo"]["ids"]["0x3BF"]["selected_field_value_counts"] == {"16": 1} and
      all("129" not in s for s in rx["source_totals"]))
check("rejected Tx echoes are separated from returned echoes",
      doc["channels"]["rejected_can_echo"]["source_totals"] == {"193": 1, "200": 1} and
      doc["channels"]["rejected_can_echo"]["record_count"] == 2)
tx = doc["channels"]["sendcan"]
check("sendcan records stay distinct from both received and echo channels",
      tx["source_totals"] == {"1": 1} and
      tx["ids"]["0x127"]["selected_field_value_counts"] == {"3": 1} and
      g127["frame_count"] == 2)

print("\n== absence-claim shape and determinism ==")
empty = GearReadyCensus()
empty.add_can(1, 0x0AA, bytes(8))
empty_doc = empty.result("cd" * 32, 7)
check("zero-count IDs still carry per-source coverage denominators",
      all(empty_doc["channels"]["received_can"]["ids"][f"0x{a:03X}"]["frame_count"] == 0
          for a in GEAR_READY_CENSUS_IDS) and
      empty_doc["channels"]["received_can"]["source_totals"] == {"1": 1})

print(f"\n== RESULT: {passed} passed, {failed} failed ==")
raise SystemExit(1 if failed else 0)
