#!/usr/bin/env python3
"""Verify the recovered Camry TSS3 0x08A request / 0x081 result layout."""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
ART = REPO / "data/generated/camry_2026_longitudinal_request_plane.json"
BUILD = REPO / "tools/targets/camry/analysis/analyze_camry_2026_longitudinal_request_plane.py"

passed = failed = 0


def check(name: str, cond, detail: str = "") -> None:
  global passed, failed
  ok = bool(cond)
  passed += int(ok)
  failed += int(not ok)
  print(f"[{'PASS' if ok else 'FAIL'}] {name}" + (f" ({detail})" if detail else ""))


def approx(a: float, b: float, eps: float = 1e-9) -> bool:
  return abs(a - b) <= eps


art = json.loads(ART.read_text())
check("schema", art["schema"] == "camry-2026-longitudinal-request-plane-v4")

print("== deterministic regeneration ==")
with tempfile.TemporaryDirectory() as td:
  out = Path(td) / ART.name
  proc = subprocess.run([sys.executable, str(BUILD), "--output", str(out)], cwd=REPO,
                        capture_output=True, text=True, check=False)
  check("analyzer succeeds", proc.returncode == 0, proc.stderr[-300:])
  check("artifact regenerates byte-exact", proc.returncode == 0 and out.read_bytes() == ART.read_bytes())

expected = {
  "drive_a": {
    "sha": "be0c02946818fafc48b7d3e2be5d2fde31d796e057ab29d8bf59a879c7553db5",
    "request_frames": 20618, "raw_range": [-1146, 995], "pair_n": 17073,
    "result_ids": {"11": 1529, "63": 15544}, "r": 0.941674118,
    "id63_delta": 0.0, "id11_delta": -0.181, "lat_match": 0.999941428,
  },
  "drive_b": {
    "sha": "641eee57eaffc579002708185178ea08c189155527354712dd43a1f0e309bb3a",
    "request_frames": 23999, "raw_range": [-1102, 1070], "pair_n": 19999,
    "result_ids": {"11": 3281, "63": 16718}, "r": 0.836883952,
    "id63_delta": 0.0, "id11_delta": -0.435, "lat_match": 0.99979999,
  },
}

for label, e in expected.items():
  d = art["drives"][label]
  request = d["request_0x08A"]
  result = d["result_0x081"]
  words = request["longitudinal_acceleration_words"]
  result_id = result["longitudinal_result_id_candidate"]
  result_acc = result["longitudinal_result_acceleration_candidate"]
  print(f"== {label} ==")
  check(f"{label}: raw capture identity", d["source"]["sha256"] == e["sha"])
  check(f"{label}: duplicated 0x08A acceleration words are exact",
        request["frame_count"] == e["request_frames"] and words["equal_frames"] == e["request_frames"]
        and words["equal_fraction"] == 1.0 and words["B8_B9"]["signed16_raw_range"] == e["raw_range"]
        and words["B11_B12"]["signed16_raw_range"] == e["raw_range"])
  check(f"{label}: request scale matches Toyota 5280/5281 geometry",
        words["B8_B9"]["scale_mps2_per_count"] == .001 and words["B11_B12"]["scale_mps2_per_count"] == .001)
  check(f"{label}: 0x081 selected longitudinal-ID alphabet",
        result["paired_to_preceding_0x08A"] == e["pair_n"] and result_id["value_counts"] == e["result_ids"])
  packed = request["longitudinal_id_allocation_packing"]
  check(f"{label}: 0x08A B6/B7 use Toyota's 6-bit ID + 2-bit allocation geometry",
        set(packed["candidate_A"]["allocation_method_counts"]).issubset({"0", "1", "2", "3"})
        and set(packed["candidate_B"]["allocation_method_counts"]).issubset({"0", "1", "2", "3"})
        and "11" in packed["candidate_A"]["request_id_counts"]
        and "17" in packed["candidate_B"]["request_id_counts"])
  relation = result_id["relation_to_request_ids"]
  check(f"{label}: selected ID11 names request candidate A and ID63 is outside the TSS application slots",
        relation["selected_ID11_equals_candidate_A_frames"] >= relation["selected_ID11_frames"] - 5
        and relation["selected_equals_candidate_B_frames"] == 0
        and relation["selected_63_absent_from_A_B_frames"] == e["result_ids"]["63"])
  check(f"{label}: 0x081 B20:B21 is strongly request-related result acceleration",
        approx(result_acc["request_vs_result"]["pearson_r"], e["r"]))
  check(f"{label}: ID63 pass-through and ID11 arbitration divergence",
        approx(result_acc["conditional_by_result_id"]["63"]["result_minus_request"]["median_mps2"], e["id63_delta"])
        and approx(result_acc["conditional_by_result_id"]["11"]["result_minus_request"]["median_mps2"], e["id11_delta"])
        and abs(result_acc["conditional_by_result_id"]["11"]["result_minus_request"]["median_mps2"]) > .15)
  check(f"{label}: lateral selected ID remains the 0x081 positive control",
        approx(result["lateral_result"]["latest_request_id_match_fraction"], e["lat_match"]))
  old = d["0x0CA_supersession_check"]["0x081_result_accel_vs_0x0CA_words"]
  check(f"{label}: old 0x0CA result triplet does not reproduce the cleaner 0x081 result",
        all(abs(row["pearson_r"]) < .6 for row in old.values()))

print("== GTS recorder and mapping boundaries ==")
layout = art["layout"]
check("5280/5281 packed ID/allocation bytes and acceleration pair are mapped without inventing upper/lower order",
      layout["5280_lower_longitudinal_request"]["acceleration"]["status"].startswith("mapped")
      and layout["5281_upper_longitudinal_request"]["acceleration"]["status"].startswith("mapped")
      and layout["5280_lower_longitudinal_request"]["request_id"]["status"].startswith("strong structural")
      and layout["5281_upper_longitudinal_request"]["force_distribution"]["status"].startswith("strong structural"))
check("5282 lateral tuple is recovered in 0x08A",
      layout["5282_lateral_request"]["lateral_id"]["wire"] == "0x08A B21[5:0]"
      and layout["5282_lateral_request"]["pinion_angle"]["wire"].startswith("0x08A B18:B19"))
check("5284/57DB longitudinal result candidates live in Brake-owned 0x081",
      layout["5284_longitudinal_result_id"]["wire"] == "0x081 B6[5:0]"
      and layout["57DB_result_acceleration"]["wire"].startswith("0x081 B20:B21"))
check("57D3 remains explicitly unresolved", layout["57D3_acceleration_valid"]["status"] == "unresolved")
check("GTS preserves TSS request versus Vehicle Motion Control target boundary",
      art["gts_vehicle_motion_control_surface"]["dids"]["0x10A1"]["name"] == "Request Acceleration of Upper Limit from Toyota Safety Sense"
      and art["gts_vehicle_motion_control_surface"]["dids"]["0x10A5"]["name"] == "Target Acceleration of Upper Limit from Vehicle Motion Control"
      and art["gts_vehicle_motion_control_surface"]["dids"]["0x10A7"]["name"] == "Target Acceleration and Deceleration ID of Upper Limit from Vehicle Motion Control"
      and art["gts_vehicle_motion_control_surface"]["dids"]["0x10A9"]["name"] == "Target Driving Force of Upper Limit from Vehicle Motion Control")
check("FFD result/state vocabulary matches vehicle-movement result packet",
      art["gts_recorder_schema"]["rows"]["5253"][0]["DataName"] == "Estimated vehicle acceleration"
      and art["gts_recorder_schema"]["rows"]["525E"][0]["DataName"] == "Stop holding status"
      and any(x["DataName"] == "Current shift range" for x in art["gts_recorder_schema"]["rows"]["526A"]))
hold = art["hold_request_semantics"]
check("raw ACC hold states decompose into request IDs and allocation methods",
      hold["hold_episode_frames"] == 198
      and hold["decoded_states"]["ordinary_active"]["request_id_B"] == 17
      and hold["decoded_states"]["ordinary_active"]["allocation_B"] == 3
      and hold["decoded_states"]["delayed_hold"]["request_id_B"] == 25
      and hold["decoded_states"]["delayed_hold"]["allocation_B"] == 3
      and hold["decoded_states"]["delayed_hold_accelerator_override"]["allocation_A"] == 0
      and hold["decoded_states"]["delayed_hold_accelerator_override"]["allocation_B"] == 2)
check("B4[5] is the exact Camry delayed-hold structural state",
      hold["structural_hold_state"]["wire"] == "0x08A B4[5]"
      and hold["structural_hold_state"]["set_frames_with_cruise_latch"] == 198
      and hold["structural_hold_state"]["xor_violations_vs_retained_delayed_hold"] == 0)
check("moving ID25 counterexample proves hold needs allocation state too",
      hold["decoded_states"]["moving_ID25_counterexample"]["request_id_B"] == 25
      and hold["decoded_states"]["moving_ID25_counterexample"]["allocation_B"] == 1)
check("0x08A is unified request envelope but not full 5280/5281 byte map",
      "unified observed continuous TSS request-side envelope" in art["conclusion"]["request_plane"]
      and "NOT yet byte-named" in art["conclusion"]["not_fully_mapped"])
check("0x0CA old triplet interpretation is superseded", "Supersede" in art["conclusion"]["0x0CA"])

namespace = art["requester_id_namespace"]
working = namespace["working_table"]
check("longitudinal IDs are modeled as application identities rather than priorities",
      "not an ordinal priority" in namespace["model"]["id_is_not_priority"]
      and "identifiers of applications" in namespace["model"]["application_id_semantics"])
check("P5 longitudinal/vertical namespace names driver operation ID63",
      namespace["authoritative_sparse_names"]["p5_frc_isa_vertical_id"]["patterns"] == {"0": "No Request", "63": "Driver Operation"})
check("cross-generation sparse long anchors include ISA9 and MaaS41/45",
      namespace["authoritative_sparse_names"]["cross_generation_examples"]["Speed Limiter Requesting Vertical ID (Upper Limit)"]["patterns"] == {"0": "No Request", "9": "ISA"}
      and namespace["authoritative_sparse_names"]["cross_generation_examples"]["MaaS Longitudinal Request ID of Lower Limit From IFU"]["patterns"] == {"0": "No Request of MaaS Autonomous Driving System", "41": "Request 1 of MaaS Autonomous Driving System", "45": "Request 2 of MaaS Autonomous Driving System"})
check("ID11 shared-axis hypothesis is explicit but not promoted to an OEM longitudinal name",
      working["11"]["lateral"] == "LTA/LCA"
      and "ordinary DRCC" in working["11"]["longitudinal"]
      and "hypothesis" in working["11"]["grade"])
check("ID25 remains an unresolved shared-application clue rather than an axis-namespace disproof",
      working["25"]["lateral"] == "AP"
      and "delayed ACC hold" in working["25"]["longitudinal"]
      and "unresolved" in working["25"]["grade"])
check("Camry startup ID36 is bounded and not active authority",
      namespace["camry_observed"]["id36_startup_frames"] == 33
      and "not observed as active cruise authority" in namespace["camry_observed"]["id36_boundary"])
check("retained Corolla independently exercises active requester IDs 17 and 23 with result63",
      namespace["corolla_cross_platform"]["request_candidate_A_counts"] == {"0": 2363, "17": 37}
      and namespace["corolla_cross_platform"]["request_candidate_B_counts"] == {"4": 2363, "23": 37}
      and namespace["corolla_cross_platform"]["result_id_counts"] == {"63": 2000})
check("feature-specific recorder IDs expose more longitudinal requester surfaces without enums",
      {(row["data_id"], row["name"]) for row in namespace["feature_specific_recorder_id_fields_without_enum"]} >= {
        ("5271", "IFU request vertical ID (lower limit)"),
        ("5280", "TSS required longitudinal ID (lower limit)"),
        ("5281", "TSS request longitudinal ID (upper limit)"),
        ("5284", "Arbitration result_longitudinal ID"),
        ("5A04", "PDA(OAA) Request Vertical ID"),
        ("5B07", "Longitudinal Request ID of Lower Limit from PDA(DA)"),
      })

print(f"Summary: {passed} passed, {failed} failed")
raise SystemExit(1 if failed else 0)
