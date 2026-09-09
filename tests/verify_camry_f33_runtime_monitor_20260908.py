#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools.analyze_camry_f33_runtime_monitor_20260908 import build

TRACKED = ROOT / "data/generated/camry_f33_runtime_monitor_20260908.json"

expected = json.loads(TRACKED.read_text(encoding="utf-8"))
actual = build()
assert actual == expected, "2026-09-08 runtime-monitor reduction drift"

assert actual["controlled_route44_activity"]["idle_segments_quiescent"] is True
assert actual["controlled_route44_activity"]["bus0_and_bus2_injection_associated_with_generation"] is True
assert actual["controlled_route44_activity"]["bus1_injection_not_associated_with_generation"] is True
assert actual["current_shape_phase_a"]["sent_target_lateral_id"] == 11
assert actual["current_shape_phase_a"]["sent_contribution_pct_1"] == 100
assert actual["current_shape_phase_a"]["sent_contribution_pct_2"] == 100
assert actual["current_shape_phase_a"]["raw_route44_post"]["target_lateral_id"] == 0
assert actual["current_shape_phase_a"]["raw_route44_post"]["contribution_pct_1"] == 0
assert actual["full_raw_phase_k_post"]["contribution_pct_2"] == 0
assert actual["downstream_post"]["generated_target_lateral_id"] == 0
assert actual["downstream_post"]["adb0"] == 0
assert actual["downstream_post"]["acbd"] == 0
assert actual["downstream_post"]["caff"] == 1
assert actual["id63_marker"]["all_sampled_raw_generated_snapshot_ids_remained_zero"] is True
assert actual["preaggregate_phase_p"]["tx_count"] == actual["preaggregate_phase_p"]["tx_echo_delta"] == 188
assert actual["preaggregate_phase_p"]["preaggregate_verdict"] == "no_profile2_queue_hit_latched"
assert actual["preaggregate_phase_p"]["queue_length_at_latched_sample"] == 0
assert "0x8F746" in actual["exact_scheduler_correction"]["aggregate_contains_secoc_consumer_chain"]
assert "inter-tick" in actual["boundary"]["next"]

print("camry F33 2026-09-08 runtime-monitor evidence: PASS")
