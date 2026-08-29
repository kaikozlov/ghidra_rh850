#!/usr/bin/env python3
"""Verify the deterministic Camry LTA-state cross-domain reconciliation."""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
ART = REPO / "data/generated/camry_2026_lta_state_reconciliation.json"
BUILD = REPO / "tools/analyze_camry_2026_lta_state_reconciliation.py"

passed = failed = 0


def check(name, condition, detail=""):
  global passed, failed
  ok = bool(condition)
  passed += int(ok)
  failed += int(not ok)
  print(f"[{'PASS' if ok else 'FAIL'}] {name}" + (f" ({detail})" if detail else ""))


def confusion(rows, names):
  return {tuple(row[name] for name in names): row["count"] for row in rows}


art = json.loads(ART.read_text())

print("== deterministic regeneration and raw identities ==")
with tempfile.TemporaryDirectory() as td:
  out = Path(td) / ART.name
  proc = subprocess.run(
    [sys.executable, str(BUILD), "--out", str(out)], cwd=REPO,
    capture_output=True, text=True, check=False)
  check("offline analyzer succeeds", proc.returncode == 0, proc.stderr[-300:])
  check("generated artifact regenerates byte-identically", proc.returncode == 0 and out.read_bytes() == ART.read_bytes())
check("schema is v1", art["schema"] == "camry-2026-lta-state-reconciliation-v1")

a = art["drives"]["drive_a"]
b = art["drives"]["drive_b"]
expected_sources = {
  "drive_a": (
    "be0c02946818fafc48b7d3e2be5d2fde31d796e057ab29d8bf59a879c7553db5",
    "91ee1c9babead2ced001ca62fb6729dbd3f051d3335afe8d3093a2b3569e506a", 1656656),
  "drive_b": (
    "641eee57eaffc579002708185178ea08c189155527354712dd43a1f0e309bb3a",
    "4bdf3d493595c6d76baa4f454b0443a6c15324c098c4872c0229f773fc7a0c65", 1918047),
}
for name, drive in art["drives"].items():
  compressed, uncompressed, frames = expected_sources[name]
  source = drive["source"]
  check(f"{name} exact compressed/uncompressed identities and frame count",
        (source["compressed_sha256"], source["uncompressed_sha256"], source["frame_count"]) ==
        (compressed, uncompressed, frames))

print("\n== 0x08A state and 0x081 mirror ==")
for name, drive, counts in (
    ("drive_a", a, {"0": 18868, "11": 646, "18": 1101}),
    ("drive_b", b, {"0": 20914, "11": 2288, "18": 797})):
  state = drive["0x08A_b21"]
  check(f"{name} B21 value set and counts exact", state["value_set"] == [0, 11, 18] and state["value_counts"] == counts)
  cond = state["conditions"]
  check(f"{name} B21=11 is cruise-active/B24=100 only", cond["b21_11_only_cruise_active_b24_100"] is True)
  check(f"{name} B21=18 is cruise-off/B24=50 and B23=0x20",
        cond["b21_18_only_cruise_off_b24_50"] is True and
        cond["b21_18_b23_0x20_count"] == cond["b21_18_count"])

expected_joint_a = {
  (0, 0, 0, 0): 9541, (0, 0, 0, 50): 7321, (0, 0, 0, 100): 818,
  (0, 18, 32, 50): 1101, (8, 0, 0, 0): 1166, (8, 0, 0, 100): 22,
  (8, 11, 0, 100): 270, (8, 11, 32, 100): 376,
}
expected_joint_b = {
  (0, 0, 0, 50): 18594, (0, 0, 0, 100): 82, (0, 18, 32, 50): 797,
  (8, 0, 0, 50): 2238, (8, 11, 0, 100): 2059, (8, 11, 32, 100): 229,
}
for name, drive, expected in (("drive_a", a, expected_joint_a), ("drive_b", b, expected_joint_b)):
  actual = confusion(drive["0x08A_b21"]["joint_b3_b21_b23_b24_counts"], ("b3", "b21", "b23", "b24"))
  check(f"{name} complete B3/B21/B23/B24 tuple census exact", actual == expected)

expected_mirror_a = {
  (0, 0): 18698, (0, 11): 1, (0, 18): 1, (0, 128): 32,
  (11, 11): 645, (11, 18): 1, (18, 0): 2, (18, 18): 1099,
}
expected_mirror_b = {
  (0, 0): 20910, (0, 11): 1, (0, 18): 3, (11, 0): 1,
  (11, 11): 2287, (18, 0): 3, (18, 18): 794,
}
for name, drive, paired, missed, matched, expected in (
    ("drive_a", a, 20479, 136, 20442, expected_mirror_a),
    ("drive_b", b, 23999, 0, 23991, expected_mirror_b)):
  mirror = drive["0x081_b13_mirror"]
  actual = confusion(mirror["confusion"], ("0x08A_b21", "0x081_b13"))
  check(f"{name} 0x081 B13 nearest-frame confusion exact",
        (mirror["paired_count"], mirror["unpaired_0x08A_count"], mirror["matching_count"], actual) ==
        (paired, missed, matched, expected))
  check(f"{name} 0x081 B13 mirrors B21 above 99.8%", mirror["matching_fraction"] > 0.998)

print("\n== exact 0x412/0x371 three-state carrier ==")
canonical = [
  {"0x412_b0": 16, "0x371_b9": 16, "0x371_b20_low2": 0},
  {"0x412_b0": 18, "0x371_b9": 32, "0x371_b20_low2": 1},
  {"0x412_b0": 20, "0x371_b9": 48, "0x371_b20_low2": 3},
]
check("three-state numeric map exact in both drives",
      a["three_state_carrier"]["canonical_states"] == canonical == b["three_state_carrier"]["canonical_states"])
expected_carrier_a = {
  (0, 0, 0): 2, (0, 32, 1): 1, (2, 32, 1): 3, (16, 16, 0): 5,
  (16, 32, 1): 2, (18, 32, 1): 496, (20, 32, 3): 1, (20, 48, 3): 17,
}
expected_carrier_b = {
  (16, 16, 0): 216, (18, 32, 1): 357, (20, 32, 1): 1, (20, 48, 3): 57,
}
for name, drive, paired, joined, matched, expected in (
    ("drive_a", a, 527, 520, 518, expected_carrier_a),
    ("drive_b", b, 631, 631, 630, expected_carrier_b)):
  carrier = drive["three_state_carrier"]
  actual = confusion(carrier["confusion"], ("0x412_b0", "0x371_b9", "0x371_b20_low2"))
  check(f"{name} complete 0x412/0x371 confusion exact",
        (carrier["paired_count"], carrier["canonical_joined_count"], carrier["canonical_matching_count"], actual) ==
        (paired, joined, matched, expected))

expected_412_a = [(0, 0.733751, 0), (0, 1.235853, 2), (0, 2.985451, 18),
                  (5, 1.426071, 16), (5, 4.852482, 18), (5, 16.944992, 20),
                  (5, 33.476303, 16), (5, 33.978766, 18)]
expected_412_b = [(16, 0.794611, 18), (17, 0.260357, 16), (20, 13.239624, 18),
                  (20, 13.339979, 20), (21, 10.435632, 18)]
expected_371_a = [(0, 0.66328, [0, 0]), (0, 1.215797, [32, 1]), (5, 1.456081, [16, 0]),
                  (5, 4.852482, [32, 1]), (5, 17.014128, [48, 3]),
                  (5, 33.014397, [32, 3]), (5, 33.174135, [32, 1])]
expected_371_b = [(16, 0.123395, [32, 1]), (17, 0.28353, [16, 0]),
                  (20, 13.280048, [32, 1]), (20, 13.440058, [48, 3]),
                  (21, 10.505968, [32, 1])]
for name, drive, expected_412, expected_371 in (
    ("drive_a", a, expected_412_a, expected_371_a),
    ("drive_b", b, expected_412_b, expected_371_b)):
  carrier = drive["three_state_carrier"]
  timeline_412 = [(row["segment"], row["segment_s"], row["value"]) for row in carrier["0x412_transition_timeline"]]
  timeline_371 = [(row["segment"], row["segment_s"], row["value"]) for row in carrier["0x371_transition_timeline"]]
  check(f"{name} exact 0x412 transition timeline", timeline_412 == expected_412)
  check(f"{name} exact 0x371 transition timeline", timeline_371 == expected_371)

print("\n== Class-L timing, cruise distinction, CANCEL, and B6 ==")
a_int = a["0x08A_b21"]["b21_11_intervals"][0]
b_int = b["0x08A_b21"]["b21_11_intervals"][0]
check("one exact B21=11 interval in each drive",
      (a_int["start"]["segment"], a_int["start"]["segment_s"], a_int["duration_s"], a_int["a8_frame_count"]) == (5, 16.834568, 16.119256, 646) and
      (b_int["start"]["segment"], b_int["start"]["segment_s"], b_int["duration_s"], b_int["a8_frame_count"]) == (20, 13.239624, 57.184128, 2288))
check("active three-state carrier follows B21=11 by exact 0.1-0.2 s lags",
      (a_int["carrier_activation"]["0x412_b0_0x14"]["lag_from_b21_11_s"],
       a_int["carrier_activation"]["0x371_b9_0x30_b20_low2_3"]["lag_from_b21_11_s"],
       b_int["carrier_activation"]["0x412_b0_0x14"]["lag_from_b21_11_s"],
       b_int["carrier_activation"]["0x371_b9_0x30_b20_low2_3"]["lag_from_b21_11_s"]) ==
      (0.110424, 0.17956, 0.100354, 0.200434))
check("drive B cruise precedes B21=11 by 11.693298 s", b_int["cruise_active_before_b21_11_s"] == 11.693298)
cancel = b["segment21_cancel_clear"]
check("segment21 CANCEL clears cruise+B21 and 0x412 together",
      cancel["cancel"]["segment_s"] == 10.406004 and cancel["cancel"]["frames"] == 5 and
      cancel["0x08A_cruise_and_b21_clear"]["lag_s"] == 0.029628 and
      (cancel["0x08A_cruise_and_b21_clear"]["b3"], cancel["0x08A_cruise_and_b21_clear"]["b21"]) == (0, 0) and
      cancel["0x412_b0_clear"]["b0"] == 18 and cancel["0x412_b0_clear"]["lag_s"] == 0.029628)
check("segment21 CANCEL clears 0x371 active carrier within 0.1 s",
      (cancel["0x371_active_clear"]["b9"], cancel["0x371_active_clear"]["b20_low2"], cancel["0x371_active_clear"]["lag_s"]) == (32, 1, 0.099964))
combined = art["combined"]
check("combined Class-L interval duration/frame census exact",
      combined["b21_11_duration_s"] == 73.303384 and combined["b21_11_incoming_frame_count_all_buses"] == 237097)
check("B6 remains zero on every bus/DLC throughout both complete Class-L intervals",
      combined["b6_during_entire_b21_11_intervals_all_buses_any_dlc"] == 0 and
      a_int["b6_count_all_buses_any_dlc"] == b_int["b6_count_all_buses_any_dlc"] == 0)

print("\n== 0x08A upstream target-steering-angle field ==")
target = combined["0x08A_target_angle"]
check("manual B18:B19 fit reproduces exact F33 B6 scale in both drives",
      target["wire"] == "B18:B19 signed big-endian" and
      target["exact_f33_b6_deg_per_count"] == 0.05730274202574147 and
      target["manual_fit_scale_error_percent_by_drive"] == {"drive_a": 0.017046, "drive_b": 0.026993})
manual_a = target["manual_state_fit_by_drive"]["drive_a"]
manual_b = target["manual_state_fit_by_drive"]["drive_b"]
check("manual ID0 B18:B19 is a 25-ms-lagging measured-angle-scale echo",
      (manual_a["best_lag_ms"], manual_a["pearson_r"], manual_a["fit_deg_per_raw_count"]) ==
      (-25, 0.9987, 0.05731251) and
      (manual_b["best_lag_ms"], manual_b["pearson_r"], manual_b["fit_deg_per_raw_count"]) ==
      (-25, 1.0, 0.05731821))
lta_a = target["lta_lca_state_fit_by_drive"]["drive_a"]
lta_b = target["lta_lca_state_fit_by_drive"]["drive_b"]
check("LTA/LCA ID11 changes B18:B19 into a leading angle quantity in both drives",
      (lta_a["best_lag_ms"], lta_a["pearson_r"], lta_a["raw_range"]) == (50, 0.8755, [-367, 63]) and
      (lta_b["best_lag_ms"], lta_b["pearson_r"], lta_b["raw_range"]) == (225, 0.4467, [-1, 56]))

print("\n== current GTS+ and exact-F33 boundaries ==")
gts = art["current_gtsplus_join"]
check("current registry identity and exact EMPS source DDB pinned",
      gts["source"]["sha256"] == "44053e3892e1f489cf8382eba1705735824a804f5952348224ce987438904611" and
      gts["target_lateral_id"]["source_ddb_sha256"] == "fb7933228bc2f1c5788d1f896c008c5c590ede45ec2e650c07123f94764e329e")
check("Target Lateral ID exact 0/11/18 dictionary",
      gts["target_lateral_id"]["selected_dictionary"] == {
        "0": "No Request (Manual Operation)", "11": "LTA/LCA", "18": "SDG"})
check("GTS+ supplies the matching target-angle output-compensation vocabulary",
      gts["target_steering_angle_after_output_compensation"] == {
        "did": "0x1CEE",
        "monitor_key": 2071,
        "bit_start": 16,
        "bit_end": 31,
        "name": "Target Steering Angle After Output Compensation",
        "source_ddb_sha256": "fb7933228bc2f1c5788d1f896c008c5c590ede45ec2e650c07123f94764e329e",
      })
indicator = gts["frc_lta_indicator_1"]
check("LTA Indicator 1 retained only as fixed FRC routine/display concept",
      (indicator["service"], indicator["routine_id"], indicator["start_static"], indicator["execution"]) ==
      (49, 5507, "31011583", "plan_only") and "not a synchronized live-state oracle" in indicator["boundary"])

expected_rx = [
  "0x3B0", "0x63B", "0x624", "0x63D", "0x00F", "0x013", "0x014", "0x015", "0x016", "0x017",
  "0x018", "0x019", "0x01A", "0x01B", "0x01C", "0x01D", "0x01E", "0x01F", "0x0D0", "0x3BF",
  "0x127", "0x115", "0x116", "0x1C5", "0x294", "0x51E", "0x611", "0x2D1", "0x675", "0x2E8",
  "0x025", "0x0AA", "0x101", "0x0D5", "0x13B", "0x090", "0x0D7", "0x0D8", "0x64F", "0x0B6",
  "0x403", "0x490", "0x1DA",
]
f33 = art["exact_f33_receive_boundary"]
check("exact-F33 accepted-Rx list remains exact", f33["descriptor_count"] == 43 and f33["accepted_can_ids"] == expected_rx)
check("0x08A/0x371/0x412 are absent from exact-F33 ingress",
      f33["state_carriers_absent"] == {"0x08A": True, "0x371": True, "0x412": True})

interpretation = art["interpretation"]
check("conclusion identifies upstream angle while keeping route/authentication open",
      "B18:B19 is the upstream target-steering-angle quantity" in interpretation["identification"] and
      "camera-side upstream command/state carrier" in interpretation["route_boundary"] and
      "authentication/trailer" in interpretation["proof_boundary"])
check("historical layouts and physical LTA button remain untransferred",
      "corroboration only" in interpretation["historical_labels"] and
      "No physical LTA-button carrier is recovered" in interpretation["button_boundary"] and
      art["interpretation"]["production_output_authorized"] is False)

print(f"\n{passed} passed, {failed} failed")
raise SystemExit(1 if failed else 0)
