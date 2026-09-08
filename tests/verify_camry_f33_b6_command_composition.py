#!/usr/bin/env python3
"""Verify exact-F33 B6 ID11 command composition/exclusivity closure."""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / "data/generated/camry_f33_b6_command_composition.json"
TOOL = ROOT / "tools/analyze_camry_f33_b6_command_composition.py"

passed = failed = 0

def check(name: str, cond: object, detail: str = "") -> None:
  global passed, failed
  ok = bool(cond)
  passed += int(ok)
  failed += int(not ok)
  print(f"[{'PASS' if ok else 'FAIL'}][b6_composition] {name}" + (f" ({detail})" if detail else ""))

with tempfile.TemporaryDirectory() as td:
  out = Path(td) / "composition.json"
  p = subprocess.run([sys.executable, str(TOOL), "--out", str(out)], capture_output=True, text=True, check=False)
  check("reducer exits clean", p.returncode == 0, p.stderr[-300:] if p.returncode else "")
  check("artifact regenerates byte-exact", out.exists() and out.read_bytes() == ART.read_bytes())

j = json.loads(ART.read_text())
check("schema and exact firmware are pinned",
      j["schema"] == "camry-f33-b6-command-composition-v1"
      and j["target"] == {
        "software_id": "8965F3307000",
        "codeflash_sha256": "42dce8efc42f6ae31718e7713fa2d26bb9191b4a82439778aee4d7afded9b0e7",
        "corpus_function_count": 6062,
      })

sel = j["selector_census"]
check("all CB00-aware functions are exhausted",
      sel["CB00_decompiled_function_count"] == 49
      and len(sel["CB00_decompiled_functions"]) == 49
      and sel["CB00_final_funnel_direct_references"] == {})
check("all 49 CB00-aware functions have one non-overlapping semantic category",
      sel["CB00_semantic_partition_counts"] == {
        "mode_mirror_status": 9,
        "controller_calibration_supervision": 28,
        "readiness_fault_supervision": 7,
        "bank_selection": 2,
        "gain_output_shaping": 3,
      }
      and set().union(*(set(v) for v in sel["CB00_semantic_partition"].values())) == set(sel["CB00_decompiled_functions"])
      and sum(len(v) for v in sel["CB00_semantic_partition"].values()) == 49)
check("ADB0 has only the two semantic runtime readers",
      sel["ADB0_decompiled_functions"] == ["0x0CB73A", "0x0CEFFC"]
      and sorted({r["function"] for r in sel["ADB0_direct_references"] if r["type"] == "READ"})
          == ["0x0CB73A", "0x0CEFFC"])
check("B6 target snapshot AE90 feeds the recovered control family",
      {r["function"] for r in sel["AE90_direct_references"] if r["type"] == "READ"}
      >= {"0x0CBA80", "0x0CBB66", "0x0CCF0E"})

checks = j["semantic_checks"]
check("every exact semantic predicate is true", checks and all(checks.values()))
check("ID11 maps to bank2 and not the 0x31 transient",
      checks["id11_maps_to_bank2"] and checks["id11_does_not_arm_special_transient"]
      and j["special_transient"] == {
        "gate_function": "0x0CB73A",
        "required_ADB0_literal": "0x31",
        "id11_literal": "0x0B",
        "same": False,
        "consequence": "the C7BF special transient that can change the ordinary sum is not the ID11 B6 path",
      })
check("B6 target controller reaches CB38 inside D0218",
      checks["b6_angle_enters_supervisor"]
      and checks["b6_supervisor_reaches_cb38"]
      and checks["d0218_adds_cb38_to_ordinary_terms"])
check("same command coordinator/funnel remains active",
      checks["shared_command_coordinator_always_calls_same_funnel"]
      and checks["d039e_retains_shared_base_and_local_addend"]
      and checks["post_slew_override_is_internal_not_b6_selected"])

writers = j["shared_funnel_writer_census"]
check("shared funnel has one runtime writer per stage plus reset/init writers",
      writers == {
        "CC48": ["0x0D01B4", "0x0D0218"],
        "CC4C": ["0x0D01B4", "0x0D0284"],
        "CC4E": ["0x0D01B4", "0x0D02DA"],
        "CC60": ["0x0D01B4", "0x0D0382"],
        "CC50": ["0x0D01B4", "0x0D039E"],
        "CC62": ["0x0D01B4", "0x0D042C"],
        "CC64": ["0x0D01B4", "0x0D047C"],
        "AC54": ["0x0BF97A", "0x0D0AAE"],
        "EE40C": ["0x0BF33E", "0x0BF97A"],
      })

proof = j["proof"]
check("exclusive-authority answer is objectively NO",
      proof["accepted_id11_selects_exclusive_b6_motor_path"] is False
      and proof["accepted_id11_replaces_shared_command_funnel"] is False)
check("co-modulation answer is objectively YES",
      proof["accepted_id11_contributes_via_cb38_inside_ordinary_d0218_sum"] is True
      and proof["ordinary_eps_terms_remain_in_id11_composition"] is True
      and proof["later_id11_specific_final_command_override_recovered"] is False)
check("0x08A/0x081 are explicitly outside this EPS-side proof",
      "receives neither 0x08A nor 0x081" in proof["stock_request_plane_boundary"])

print(f"\nResults: {passed} passed, {failed} failed")
raise SystemExit(1 if failed else 0)
