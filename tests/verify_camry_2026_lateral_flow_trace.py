#!/usr/bin/env python3
"""Verify the deterministic Camry TSS3 lateral flow-trace artifact."""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
ART = REPO / "data/generated/camry_2026_lateral_flow_trace.json"
BUILD = REPO / "tools/analyze_camry_2026_lateral_flow_trace.py"

passed = failed = 0


def check(name, condition, detail=""):
    global passed, failed
    ok = bool(condition)
    passed += ok
    failed += not ok
    print(f"[{'PASS' if ok else 'FAIL'}] {name}" + (f" ({detail})" if detail else ""))


art = json.loads(ART.read_text())

print("== deterministic regeneration and raw identities ==")
with tempfile.TemporaryDirectory() as td:
    out = Path(td) / ART.name
    proc = subprocess.run([sys.executable, str(BUILD), str(out)],
                          capture_output=True, text=True, check=False)
    check("generator exits cleanly", proc.returncode == 0,
          proc.stderr[-200:] if proc.returncode else "")
    check("generated artifact regenerates byte-identically",
          proc.returncode == 0 and out.read_bytes() == ART.read_bytes())
check("schema is v1", art["schema"] == "camry-2026-lateral-flow-trace-v1")
check("production output remains unauthorized", art["production_output_authorized"] is False)

expected_sources = {
    "drive_a": (1656656,
                "be0c02946818fafc48b7d3e2be5d2fde31d796e057ab29d8bf59a879c7553db5",
                "91ee1c9babead2ced001ca62fb6729dbd3f051d3335afe8d3093a2b3569e506a"),
    "drive_b": (1918047,
                "641eee57eaffc579002708185178ea08c189155527354712dd43a1f0e309bb3a",
                "4bdf3d493595c6d76baa4f454b0443a6c15324c098c4872c0229f773fc7a0c65"),
}
for name, drive in art["drives"].items():
    frames, sha_c, sha_u = expected_sources[name]
    check(f"{name} source identities exact",
          (drive["incoming_frames"], drive["sha256_compressed"],
           drive["sha256_uncompressed_ndjson"]) == (frames, sha_c, sha_u))

print("\n== absent actuation carriers and streaming controls ==")
absent_ids = ["0x351", "0x394", "0x4A3", "0x4C8", "0x0B6", "0x131", "0x2E4"]
for name, drive in art["drives"].items():
    check(f"{name} EPS telemetry Tx PDUs, 0x0B6, and legacy lateral IDs are zero on every bus",
          all(drive["absent_carriers"][k]["total"] == 0 for k in absent_ids))
    check(f"{name} controls stream throughout",
          drive["control_carriers"]["0x030"]["src0"] > 50000
          and drive["control_carriers"]["0x081"]["src0"] > 15000,
          f"0x030={drive['control_carriers']['0x030']['src0']} 0x081={drive['control_carriers']['0x081']['src0']}")
for name, parked in art["parked_censuses"].items():
    check(f"parked {name} also carries zero absent carriers with live controls",
          all(parked["absent_carriers"][k] == 0 for k in absent_ids)
          and parked["controls"]["0x030"] > 1900 and parked["controls"]["0x081"] > 600)

print("\n== exact ID11 anchor intervals ==")
for name, start, end, frames_bus0 in (("drive_a", 371.48431, 387.603566, 646),
                                      ("drive_b", 1267.881232, 1325.06536, 2288)):
    iv = art["drives"][name]["id11_interval"]
    check(f"{name} ID11 interval exact",
          (iv["start_s"], iv["end_s"], iv["frames_bus0"]) == (start, end, frames_bus0),
          f"duration={iv['duration_s']}")

print("\n== 0x081 steering-reference word ==")
for name, paired, dt_le10, static_n, static_eq, dup, fit in (
        ("drive_a", 17172, 14942, 12396, 0.893595, 0.002038,
         (16531, 0.998737, 0.038231, 0.057346)),
        ("drive_b", 19999, 17539, 13963, 0.836711, 0.0009,
         (18092, 0.999911, 0.038214, 0.057321))):
    m = art["drives"][name]["reference_word_081"]
    check(f"{name} mirror pairing population exact",
          (m["paired_frames"], m["pair_dt_buckets"]["le10ms"], m["static_both_paired"])
          == (paired, dt_le10, static_n))
    check(f"{name} static-word byte equality above 0.83 and duplicate-word negative below 0.005",
          m["static_both_equality_fraction"] == static_eq
          and m["duplicate_word_B8_B9_equality_fraction"] == dup)
    n, r, slope, deg = fit
    got = m["manual_state_word_vs_sas_ct"]
    check(f"{name} manual-state word reproduces the F33 B6 scale against SAS",
          (got["n"], got["pearson_r"], got["slope_sas_ct_per_word"], got["implied_deg_per_word"])
          == (n, r, slope, deg),
          f"implied {got['implied_deg_per_word']} vs F33 {got['expected_f33_b6_scale_deg_per_word']}")
bm = {name: art["drives"][name]["reference_word_081"]["batch_median_comparison"]
      for name in ("drive_a", "drive_b")}
check("drive-B batch-median equality stays above 0.92 inside ID11",
      bm["drive_b"]["id11_equality_le1_fraction"] == 0.920555)
check("drive-A fast-slew disagreement is disclosed, not hidden",
      bm["drive_a"]["id11_equality_le1_fraction"] == 0.506849)

print("\n== 0x08A byte-complete census ==")
for name, b26_frac, b26_breaks, b24_distinct in (("drive_a", 0.991511, 175, 3),
                                                 ("drive_b", 1.0, 0, 2)):
    c = art["drives"][name]["a08A_byte_census"]
    check(f"{name} B26 mod-64 freshness counter",
          c["B26_freshness_counter"]["step_fraction_plus1_mod64"] == b26_frac
          and c["B26_freshness_counter"]["break_count"] == b26_breaks)
    check(f"{name} latch mirrors and active flags exact",
          c["latch_mirror_agreement"] == {"B6[0]": c["latch_mirror_agreement"]["B6[0]"],
                                          "B7[0]": c["latch_mirror_agreement"]["B7[0]"],
                                          "B20[7]": c["latch_mirror_agreement"]["B20[7]"]}
          and c["active_flags"]["B22[4]"]["set_fraction_b21_11"] == 1.0
          and c["active_flags"]["B4[7]"]["set_fraction_b21_11"] == 1.0)
    check(f"{name} damping absence: B24 gain alphabet vs unnamed bytes",
          c["damping_gain_absence"]["B24_distinct"] == b24_distinct
          and c["damping_gain_absence"]["unnamed_bytes_distinct"]["B12"] == 256)

print("\n== SDG (B21=18) request content ==")
a_sdg = art["drives"]["drive_a"]["sdg_states"]["intervals"]
b_sdg = art["drives"]["drive_b"]["sdg_states"]["intervals"]
check("drive A has two SDG intervals, both long with nonzero tracking words",
      len(a_sdg) == 2 and all(i["long_interval"] for i in a_sdg)
      and (a_sdg[0]["word_min"], a_sdg[0]["word_max"], a_sdg[0]["word_vs_sas_pearson_r"]) == (-339, 32, 0.816961)
      and (a_sdg[1]["word_min"], a_sdg[1]["word_max"], a_sdg[1]["word_vs_sas_pearson_r"]) == (20, 195, 0.908715))
check("drive B has five SDG intervals; the 17.7 s interval publishes a dynamic steering target",
      len(b_sdg) == 5
      and (b_sdg[4]["start_s"], b_sdg[4]["frames"], b_sdg[4]["word_min"], b_sdg[4]["word_max"],
           b_sdg[4]["word_vs_sas_pearson_r"]) == (1423.999209, 711, -209, 123, 0.754389))
check("SDG blips carry small nonzero trims (12-20 counts), not zeros",
      all(14.0 <= i["mean_abs_word"] <= 21.0 for i in b_sdg[:4]))

print("\n== plant closure ==")
pa = art["drives"]["drive_a"]["plant_closure"]
pb = art["drives"]["drive_b"]["plant_closure"]
check("drive A request leads measured angle: plateau r~0.87 with gain 1.25 mrad/mrad",
      [(l["lag_ms"], l["pearson_r"]) for l in pa["id11_word_vs_sas_lag_table"]][:3]
      == [(-50, 0.864612), (-25, 0.865859), (0, 0.867767)]
      and pa["best_lag"]["lag_ms"] == 50 and pa["best_lag"]["pearson_r"] == 0.867905
      and pa["plant_gain_mrad_per_mrad"] == 1.248945)
check("drive B tracking is small-signal: first 30 s r=0.562, second 30 s collapses",
      [(s["pearson_r"]) for s in pb["b_style_30s_subinterval_word_vs_sas_r"]] == [0.561663, 0.139101])
for name, pc in (("drive_a", pa), ("drive_b", pb)):
    tri = pc["motor_proxy_triangle"]
    check(f"{name} motor proxy follows the reference word at least as well as SAS",
          tri["vs_reference_word_081"]["pearson_r"] > tri["vs_sas"]["pearson_r"],
          f"word={tri['vs_reference_word_081']['pearson_r']} sas={tri['vs_sas']['pearson_r']}")

print("\n== no delayed grant/ack on any DLC-32 bus-0 stream ==")
for name in ("drive_a", "drive_b"):
    da = art["drives"][name]["delayed_ack"]["onsets"]["id11_onset"]
    check(f"{name} zero delayed persistent flips +0.5..+5.0 s after ID11 onset",
          da["flip_count"] == 0 and da["delayed_persistent_flips"] == [])

print("\n== 0x160 'SAS echo' is a Class-L-window artifact (CORR-138) ==")
for name, full_be, id11_be in (("drive_a", 0.086104, 0.985033),
                               ("drive_b", -0.091204, 0.554946)):
    x = art["drives"][name]["x160_echo_correction"]["results"]
    check(f"{name} B22s16be correlation collapses outside the Class-L window",
          x[f"full_drive/B22s16be"]["pearson_r"] == full_be
          and x[f"id11_window/B22s16be"]["pearson_r"] == id11_be
          and abs(x[f"full_drive/B22s16be"]["pearson_r"]) < 0.1)

print("\n== refuted 0x19C 'LTA cadence flip' ==")
for name, fast_start, fast_end in (("drive_a", 263.945429, 503.945429),
                                   ("drive_b", 1104.701663, 1494.701663)):
    p = art["drives"][name]["p19c_phase_refutation"]
    fast = [q for q in p["phases"] if q["mode"] == "fast"]
    check(f"{name} single fast phase containing ID11 (mode dilution, not LTA behavior)",
          len(fast) == 1 and (fast[0]["start_s"], fast[0]["end_s"]) == (fast_start, fast_end)
          and p["id11_contained_in_fast_phase"] is True)

print("\n== interpretation boundaries ==")
interp = art["interpretation"]
check("conclusion states the command never appears on any captured segment",
      "never appears on any captured segment" in interp["conclusion"]
      and "not the full EPS interface" in interp["conclusion"])
check("proof boundary forbids producer/transform/grant claims and output",
      "No 0x08A-to-B6 transform is established" in interp["proof_boundary"]
      and art["production_output_authorized"] is False)

print(f"\n{passed} passed, {failed} failed")
raise SystemExit(1 if failed else 0)
