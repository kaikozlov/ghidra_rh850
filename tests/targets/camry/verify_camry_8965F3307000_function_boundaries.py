#!/usr/bin/env python3
"""Regression-check the corrected exact-F33 canonical function boundaries (CORR-181)."""
from __future__ import annotations

import hashlib
import json

from tools import REPO_ROOT
ROOT = REPO_ROOT
CORPUS = ROOT / "data/generated/camry-8965F3307000/decompilations.jsonl"
INVENTORY = ROOT / "data/targets/camry-8965F3307000/ghidra_project_inventory.baseline.jsonl"

passed = failed = 0


def check(name: str, cond: object, detail: str = "") -> None:
  global passed, failed
  ok = bool(cond)
  passed += int(ok)
  failed += int(not ok)
  print(f"[{'PASS' if ok else 'FAIL'}][f33_boundaries] {name}" + (f" ({detail})" if detail else ""))


rows: dict[int, dict] = {}
metadata = None
for line in CORPUS.read_text().splitlines():
  rec = json.loads(line)
  if rec.get("record") == "metadata":
    metadata = rec
  elif rec.get("record") == "function":
    rows[int(rec["entry_addr"], 16)] = rec

real = {0xBCD62: 2748, 0xCCFB2: 128, 0xCEE7C: 146}
false = {0xBCD66, 0xCCFB6, 0xCEE80}
recovered = {0x71508: 170, 0x7D72C: 212, 0x810F2: 204}
check("canonical corpus is complete and bound to the current inventory",
      metadata is not None
      and metadata["function_count"] == metadata["inventory_function_count"] == len(rows)
      and metadata["decompiled_count"] == len(rows)
      and metadata["failed_count"] == 0
      and metadata["project_inventory_sha256"] == hashlib.sha256(INVENTORY.read_bytes()).hexdigest())
check("real parent starts have the complete bodies",
      all(entry in rows and rows[entry]["body_size"] == size for entry, size in real.items()))
check("false +4 child functions are absent", not (false & set(rows)))
check("omitted B6 receive-path entries are recovered with complete bodies",
      all(entry in rows and rows[entry]["body_size"] == size
          for entry, size in recovered.items()))

print(f"\nResults: {passed} passed, {failed} failed")
raise SystemExit(1 if failed else 0)
