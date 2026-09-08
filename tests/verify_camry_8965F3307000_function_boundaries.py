#!/usr/bin/env python3
"""Regression-check the corrected exact-F33 canonical function boundaries (CORR-181)."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CORPUS = ROOT / "data/generated/camry-8965F3307000/decompilations.jsonl"
INVENTORY = ROOT / "data/targets/camry-8965F3307000/ghidra_project_inventory.baseline.jsonl"
SEEDS = ROOT / "data/targets/camry-8965F3307000/function_seeds.csv"
CONE = ROOT / "data/generated/camry_8965F3307000_command_cone_ingress.json"
HIDDEN = ROOT / "data/generated/camry_8965F3307000_hidden_ingress_residuals.json"
COMPOSITION = ROOT / "data/generated/camry_f33_b6_command_composition.json"
EXPECTED_INVENTORY_SHA = "423f5e584548f984bc5b447d9975ac378fdcba4a3a00b3a4c6d0c33660320f99"

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
check("canonical metadata denominator is 6062",
      metadata is not None and metadata["function_count"] == 6062
      and metadata["inventory_function_count"] == 6062 and len(rows) == 6062)
check("corrected normalized inventory identity is pinned",
      hashlib.sha256(INVENTORY.read_bytes()).hexdigest() == EXPECTED_INVENTORY_SHA
      and metadata["project_inventory_sha256"] == EXPECTED_INVENTORY_SHA)
check("real parent starts have the complete bodies",
      all(entry in rows and rows[entry]["body_size"] == size for entry, size in real.items()))
check("false +4 child functions are absent", not (false & set(rows)))

seed_text = SEEDS.read_text()
check("seed list contains only the real starts",
      all(f"0x{entry:08X}," in seed_text for entry in real)
      and all(f"0x{entry:08X}," not in seed_text for entry in false))

# Independent textual call-target check: the parent entries are real call targets;
# none of the former child labels appears as a call target in the corrected corpus.
callers: dict[int, list[int]] = {}
for target in real:
  token = f"FUN_{target:08x}("
  callers[target] = sorted(entry for entry, rec in rows.items()
                           if entry != target and token in rec.get("decompiled_c", ""))
check("real parent starts have the expected callers",
      callers == {0xBCD62: [0xC214C, 0xC26A4], 0xCCFB2: [0xCD032], 0xCEE7C: [0xCEF0E]}, str(callers))
check("former child labels have no callsite spelling",
      all(f"FUN_{target:08x}(" not in rec.get("decompiled_c", "")
          for target in false for rec in rows.values()))

cone = json.loads(CONE.read_text())
check("snapshot/stage denominators reflect the collapsed boundary",
      cone["target"]["corpus_function_count"] == 6062
      and cone["pipeline"]["L3_stage_reader_census"]["total"] == 51
      and cone["pipeline"]["L3_stage_reader_census"]["in_cluster"] == 15
      and cone["pipeline"]["L4_snapshot_copiers"] == {
        "0xBC96A": {"exact_pairs": 1},
        "0xBCA08": {"exact_pairs": 13},
        "0xBCAA6": {"exact_pairs": 1},
        "0xBCBD8": {"exact_pairs": 46},
        "0xBCD62": {"exact_pairs": 245},
      }
      and cone["pipeline"]["L4_unique_snapshot_destinations"] == 306)

hidden = json.loads(HIDDEN.read_text())
e1 = hidden["e1_register_arithmetic_store_targets"]["census"]
e2 = hidden["e2_dmac_destination_reprogramming"]["computed_store_census"]
check("HighFunction denominator changed without changing E1/E2 candidates",
      e1 == {"candidateFunctions": 46, "candidates": 100, "functions": 6062,
             "knownRangeStores": 4701, "stores": 13183}
      and e2 == {"candidateFunctions": 3, "candidates": 5, "functions": 6062,
                 "knownRangeStores": 4701, "stores": 13183})

composition = json.loads(COMPOSITION.read_text())
sel = composition["selector_census"]
check("CB00 denominator and exhaustive semantic partition are corrected",
      sel["CB00_decompiled_function_count"] == 49
      and sel["CB00_semantic_partition_counts"] == {
        "bank_selection": 2,
        "controller_calibration_supervision": 28,
        "gain_output_shaping": 3,
        "mode_mirror_status": 9,
        "readiness_fault_supervision": 7,
      }
      and sum(sel["CB00_semantic_partition_counts"].values()) == 49)

print(f"\nResults: {passed} passed, {failed} failed")
raise SystemExit(1 if failed else 0)
