#!/usr/bin/env python3
"""Verify exact-F33 protected-B6 end-to-end software-gate closure."""
from __future__ import annotations

import hashlib
import json
import struct
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / "data/generated/camry_f33_b6_end_to_end.json"
TOOL = ROOT / "tools/targets/camry/analysis/analyze_camry_f33_b6_end_to_end.py"
IMAGE = ROOT / "firmware/camry-8965F3307000/CodeFlash.bin"
CORPUS = ROOT / "data/generated/camry-8965F3307000/decompilations.jsonl"
EXPECTED_SHA = "42dce8efc42f6ae31718e7713fa2d26bb9191b4a82439778aee4d7afded9b0e7"

passed = failed = 0


def check(name: str, cond: object, detail: str = "") -> None:
  global passed, failed
  ok = bool(cond)
  passed += int(ok)
  failed += int(not ok)
  print(f"[{'PASS' if ok else 'FAIL'}][b6_end_to_end] {name}" + (f" ({detail})" if detail else ""))


def load_corpus() -> dict[int, dict]:
  out = {}
  with CORPUS.open(encoding="utf-8") as fh:
    for line in fh:
      rec = json.loads(line)
      if rec.get("record") == "function":
        out[int(rec["entry_addr"], 16)] = rec
  return out


def refs(corpus: dict[int, dict], target: int, ref_type: str) -> list[int]:
  out = set()
  for entry, rec in corpus.items():
    for ref in rec.get("data_references", []):
      try:
        to_addr = int(ref["to_addr"], 16)
      except (KeyError, ValueError):
        continue
      if to_addr == target and ref.get("ref_type") == ref_type:
        out.add(entry)
  return sorted(out)


with tempfile.TemporaryDirectory() as td:
  out = Path(td) / "b6_e2e.json"
  p = subprocess.run([sys.executable, str(TOOL), "--out", str(out)], capture_output=True, text=True, check=False)
  check("reducer exits clean", p.returncode == 0, p.stderr[-400:] if p.returncode else "")
  check("artifact regenerates byte-exact", out.exists() and out.read_bytes() == ART.read_bytes())

image = IMAGE.read_bytes()
corpus = load_corpus()
j = json.loads(ART.read_text())
check("exact firmware and complete canonical corpus pinned",
      hashlib.sha256(image).hexdigest() == EXPECTED_SHA
      and j["target"] == {"software_id": "8965F3307000", "codeflash_sha256": EXPECTED_SHA, "canonical_function_count": 6065}
      and len(corpus) == 6065)

# Independently decode the two raw configuration records used before any decompiler semantics.
canif = 0x21FE8 + 39 * 8
route = 0x226C0 + 44 * 8
check("CanIf descriptor39 is exact B6/32-byte descriptor",
      struct.unpack_from("<I", image, canif)[0] == 0x400000B6
      and struct.unpack_from("<H", image, canif + 4)[0] == 32)
check("PduR route44 is exact 32-byte configured route",
      image[route:route + 8].hex() == "060000002000000c"
      and struct.unpack_from("<H", image, 0x22840 + 44 * 2)[0] == 0x1B7)
check("B6 SecOC ingress geometry is exact",
      struct.unpack_from("<H", image, 0x258EE)[0] == 4
      and struct.unpack_from("<H", image, 0x258FE)[0] == 0
      and j["exact_config"]["secoc_queue_record"] == "0xFEBE547A"
      and j["exact_config"]["secoc_secured_buffer"] == "0xFEBE54D4")

profile_base = 0x23DFC + 0x1A40
profile = []
slot = 0
for index in range(3):
  rec = profile_base + index * 0x50
  special = image[rec + 0x15]
  fid = struct.unpack_from("<H", image, rec + 0x1E)[0]
  ordinary_slot = None if special == 1 else slot
  if special != 1:
    slot += 1
  profile.append((special, fid, ordinary_slot))
check("freshness table independently resolves B6 FreshnessId2 to ordinary slot1",
      profile == [(1, 0, None), (0, 1, 0), (0, 2, 1)] and j["b6_freshness_slot"] == 1)

checks = j["semantic_checks"]
check("every exact semantic predicate passes", checks and all(checks.values()))
for name in (
  "sig263_is_special_0x31_transient_condition_not_id11_gate",
  "sig265_one_suppresses_controller_term",
  "app_sequence_is_independent_modulo_counter",
  "sig269_scales_supervisor",
  "sig270_scales_supervisor",
  "ordinary_sum_adds_b6_term_only_in_normal_branch",
  "ac5a_is_internal_ramped_scale",
  "common_actuator_gate_can_zero_command",
  "internal_override_trigger_and_replacement_are_exact",
  "motor_side_can_substitute_internal_bounded_source",
):
  check(f"critical semantic gate closed: {name}", checks[name])

# Independent direct-writer closure over every state transition from B6 contribution to current model.
expected_writers = {
  0xFEBECB00: [0xCEFF4, 0xCEFFC],
  0xFEBECB20: [0xCF056, 0xCF148],
  0xFEBECB38: [0xCF056, 0xCF2B2],
  0xFEBECC48: [0xD01B4, 0xD0218],
  0xFEBECC4C: [0xD01B4, 0xD0284],
  0xFEBECC4E: [0xD01B4, 0xD02DA],
  0xFEBECC60: [0xD01B4, 0xD0382],
  0xFEBECC50: [0xD01B4, 0xD039E],
  0xFEBECC62: [0xD01B4, 0xD042C],
  0xFEBECC66: [0xD01B4, 0xD042C],
  0xFEBECC64: [0xD01B4, 0xD047C],
  0xFEBEAC54: [0xBF97A, 0xD0AAE],
  0xFEBEE40C: [0xBF33E, 0xBF97A],
  0xFEBE6AF4: [0x35C4C, 0x59448],
  0xFEBE6E0A: [0x387BA, 0x59448],
  0xFEBE6DEC: [0x38502, 0x59448],
  0xFEBE6DC8: [0x3835E, 0x59448],
  0xFEBE6DD6: [0x384D8, 0x59448],
}
check("all recovered B6-to-current writer sets independently close",
      all(refs(corpus, cell, "WRITE") == writers for cell, writers in expected_writers.items()))

check("AC2B diagnostic branch source has no hidden runtime writer",
      refs(corpus, 0xFEBEAC2B, "WRITE") == [0xBCBD8, 0xBF97A]
      and refs(corpus, 0xFEBEB112, "WRITE") == [0xB3314, 0xB338C, 0xBF97A])
check("AC5A output-scale source has no hidden runtime writer",
      refs(corpus, 0xFEBEAC5A, "WRITE") == [0xBCBD8, 0xBF97A]
      and refs(corpus, 0xFEBEB1F8, "WRITE") == [0xB4B6C, 0xB4EF4, 0xBF97A])
check("hard actuator gate source closes through one status snapshot",
      refs(corpus, 0xFEBE8B28, "WRITE") == [0x572E6, 0x59448]
      and refs(corpus, 0xFEBEEF90, "WRITE") == [0xFCC00]
      and refs(corpus, 0xFEBEAC29, "WRITE") == [0xBCAA6, 0xBF97A]
      and refs(corpus, 0xFEBEAC2A, "WRITE") == [0xBCAA6, 0xBF97A])
check("post-gate override writer family is exact",
      refs(corpus, 0xFEBECC98, "WRITE") == [0xD04F0, 0xD0528, 0xD0674]
      and refs(corpus, 0xFEBECC94, "WRITE") == [0xD0674])

# Application-field closure: distinguish live companions from staged-but-dead bits.
rows = {row["signal"]: row for row in j["raw_stage_snapshot_census"]}
check("all thirteen B6 application scalars are explicitly tracked", set(rows) == set(range(261, 274)))
check("signal266 dies at staging exactly",
      rows[266]["snapshot"] is None and rows[266]["stage"]["readers"] == [])
for signal in (264, 267, 271, 272):
  check(f"signal{signal} snapshots but has no runtime reader", rows[signal]["snapshot"]["readers"] == [])
check("signal263 only feeds the special-0x31 transient qualifier",
      rows[263]["snapshot"]["readers"] == ["0x0CB664"]
      and refs(corpus, 0xFEBEC7B4, "READ") == [0xCB664, 0xCB73A]
      and refs(corpus, 0xFEBEC7B4, "WRITE") == [0xCB548, 0xCB664])
check("command-relevant normal-ID11 companion consumers are exact",
      rows[265]["snapshot"]["readers"] == ["0x0CDA20"]
      and rows[268]["snapshot"]["readers"] == ["0x0CEC8A"]
      and rows[269]["snapshot"]["readers"] == ["0x0CE3AA"]
      and rows[270]["snapshot"]["readers"] == ["0x0CDFF8"]
      and rows[273]["snapshot"]["readers"] == ["0x0CFDA0"])

matrix = j["gate_matrix"]
ladder = j["live_witness_ladder"]
check("full software gate matrix is ordered and contiguous", len(matrix) == 18 and [g["order"] for g in matrix] == list(range(1, 19)))
check("runtime ladder is ordered and contiguous", len(ladder) == 17 and [r["n"] for r in ladder] == list(range(1, 18)))
check("only freshness/auth result layers are marked stage5-bypassed",
      [g["order"] for g in matrix if g["stage5_bypasses"]] == [3, 4])

phases = j["stationary_monitor_phases"]
check("seven stationary monitor phases fit the generic eight-slot ABI",
      [p["phase"] for p in phases] == list("ABCDEFG")
      and all(1 <= len(p["watch_windows"]) <= 8 for p in phases)
      and all(int(w["address"], 16) % 4 == 0 for p in phases for w in p["watch_windows"])
      and all(0xFEBE0000 <= int(w["address"], 16) <= 0xFEBFFFFC for p in phases for w in p["watch_windows"]))
check("phase boundaries deliberately overlap adjacent rungs",
      {w["address"] for w in phases[0]["watch_windows"]} & {w["address"] for w in phases[1]["watch_windows"]} == {"0xFEBE5364"}
      and {w["address"] for w in phases[1]["watch_windows"]} & {w["address"] for w in phases[2]["watch_windows"]} == {"0xFEBEF1F8"}
      and {w["address"] for w in phases[2]["watch_windows"]} & {w["address"] for w in phases[3]["watch_windows"]} == {"0xFEBECAFC"}
      and {w["address"] for w in phases[3]["watch_windows"]} & {w["address"] for w in phases[4]["watch_windows"]} == {"0xFEBECB38"}
      and {w["address"] for w in phases[4]["watch_windows"]} & {w["address"] for w in phases[5]["watch_windows"]} == {"0xFEBEAC28", "0xFEBECC60"}
      and {w["address"] for w in phases[5]["watch_windows"]} & {w["address"] for w in phases[6]["watch_windows"]} == {"0xFEBEE40C"})

obj = j["objective_conclusions"]
check("stage5 scope is bounded to auth/freshness results",
      obj["stage5_removes_recovered_freshness_and_auth_result_rejection_after_valid_secoc_ingress"] is True
      and obj["stage5_forces_noncrypto_queue_pdur_com_or_controller_gates"] is False)
check("ID11 acceptance does not imply authority or nonzero motor command",
      obj["accepted_id11_guarantees_nonzero_cb38"] is False
      and obj["nonzero_cb38_guarantees_nonzero_motor_command"] is False
      and obj["accepted_id11_is_exclusive_eps_authority"] is False
      and obj["accepted_id11_is_a_co_modulated_input"] is True)
check("proof boundary does not overclaim ICU/PWM closure",
      obj["final_hardware_pwm_commit_recovered_exact_f33_here"] is False
      and "ICU-S silicon internals" in obj["proof_boundary"]
      and "final hardware PWM commit" in obj["proof_boundary"])

print(f"\nResults: {passed} passed, {failed} failed")
raise SystemExit(1 if failed else 0)
