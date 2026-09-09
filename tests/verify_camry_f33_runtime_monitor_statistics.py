#!/usr/bin/env python3
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data/generated/camry_f33_runtime_monitor_statistics.json"
subprocess.run(["python3", str(ROOT / "tools/analyze_camry_f33_runtime_monitor_statistics.py")], check=True)
d = json.loads(OUT.read_text())
i = d["retained_idle_control"]
assert d["target"] == "8965F3307000"
assert i["host_b6_tx_echoes"] == 0
assert i["host_reads"] == 26
assert i["distinct_resident_snapshots"] == 6
assert i["route44_generation_u8_distinct_samples"] == [121, 243, 249, 107, 119, 121]
assert i["route44_generation_mod256_deltas"] == [122, 6, 114, 12, 2]
assert i["route44_minimum_publications_between_first_last_distinct_snapshot"] == 256
assert 96.9 < i["route44_minimum_publication_rate_hz"] < 97.1
assert i["distinct_trailer_values"] == 6
assert i["application_sequence_mod64_distinct_samples"] == [53, 38, 40, 22, 27, 28]
assert i["all_sampled_target_lateral_ids_zero"] is True
assert i["actual_host_read_rate_hz"] < 9
assert i["resident_sample_generation_rate_hz"] < 25
assert i["nominal_foreground_rate_hz_from_static_timer"] == 200.0
assert d["short_window_rate_reaudit"]["segments"][2]["route44_generation_residue_mod256"] == 128
assert d["short_window_rate_reaudit"]["segments"][2]["compatible_event_counts"] == "128 + 256*k, k>=0"
assert d["decision"]["vehicle_needed_now"] is False
print("PASS camry F33 runtime monitor statistics audit")
