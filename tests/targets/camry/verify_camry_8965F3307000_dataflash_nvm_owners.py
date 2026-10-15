#!/usr/bin/env python3
"""Exercise NvM descriptor boundaries, record markers and artifact regeneration."""
from __future__ import annotations

import struct
import subprocess
import sys
import tempfile
from pathlib import Path

from tools import REPO_ROOT
from tools.targets.camry.analysis import (
    analyze_camry_8965F3307000_dataflash_nvm_owners as owner,
)

ROOT = REPO_ROOT
ART = ROOT / "data/generated/camry_8965F3307000_dataflash_nvm_owners.json"
TOOL = ROOT / "tools/targets/camry/analysis/analyze_camry_8965F3307000_dataflash_nvm_owners.py"
failures = []


def check(name, cond, detail=""):
    if cond:
        print(f"PASS {name}")
    else:
        print(f"FAIL {name}: {detail}")
        failures.append(name)


# A short table with deliberately distinct page/length fields catches the old
# one-descriptor shift and hard-coded 48-row traversal. The zero descriptor is
# a sentinel, not a physical page. Nonzero option overhead makes record2 span
# two pages even though its payload is shorter than one page.
code = bytearray(owner.JOB_COUNT + 2)
struct.pack_into("<H", code, owner.JOB_COUNT, 3)
for index, fields in enumerate(((0xFFFF, 32, 0, 0), (7, 16, 0, 0), (2, 48, 1, 0))):
    struct.pack_into("<HHBB", code, owner.JOB_TABLE + index * owner.JOB_STRIDE, *fields)
jobs = owner.decode_job_table(bytes(code))
check("descriptor bound and field alignment",
      [(job["handle"], job["page"], job["payload_len"], job["allocation_pages"])
       for job in jobs] == [(0, 0xFFFF, 32, 1), (1, 7, 16, 1), (2, 2, 48, 2)])

dump = bytearray(b"\xff" * (9 * 64))
struct.pack_into("<H", dump, 7 * 64, 1)
struct.pack_into("<I", dump, 8 * 64 - 4, 0xAAAAAAAA)
struct.pack_into("<H", dump, 2 * 64, 2)
struct.pack_into("<I", dump, 3 * 64 - 4, 0xAAAAAAAA)
records = {record["handle"]: record for record in owner.decode_dataflash_records(bytes(dump), jobs)}
check("sentinel descriptor is not read as DataFlash", set(records) == {1, 2})
check("single-page header and trailer match", records[1]["markers_match"])
check("first-page trailer cannot commit a multi-page allocation",
      records[2]["header_matches_handle"] and not records[2]["commit_marker_present"])

struct.pack_into("<I", dump, 4 * 64 - 4, 0xAAAAAAAA)
records = {record["handle"]: record for record in owner.decode_dataflash_records(bytes(dump), jobs)}
check("final-allocation trailer is recognized", records[2]["markers_match"])
struct.pack_into("<H", dump, 2 * 64, 480 - 2)
records = {record["handle"]: record for record in owner.decode_dataflash_records(bytes(dump), jobs)}
check("header must match handle, not descending page ordinal",
      records[2]["commit_marker_present"] and not records[2]["header_matches_handle"]
      and not records[2]["markers_match"])

try:
    owner.decode_dataflash_records(bytes(dump[:4 * 64 - 1]), jobs[2:])
except ValueError:
    check("truncated allocation rejected", True)
else:
    check("truncated allocation rejected", False)

with tempfile.TemporaryDirectory() as td:
    regen = Path(td) / "nvm_owners.json"
    subprocess.run([sys.executable, str(TOOL), "--output", str(regen)], cwd=ROOT, check=True,
                   stdout=subprocess.DEVNULL)
    check("artifact regenerates byte-identically", regen.read_bytes() == ART.read_bytes())

if failures:
    raise SystemExit(f"{len(failures)} failed checks: {', '.join(failures)}")
print("all checks passed")
