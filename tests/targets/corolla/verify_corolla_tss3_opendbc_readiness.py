#!/usr/bin/env python3
"""Verify the generated Corolla TSS3/opendbc implementation-readiness model."""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

from tools import REPO_ROOT
REPO = REPO_ROOT
ART_PATH = REPO / "data/generated/corolla_tss3_opendbc_readiness.json"
ART = json.loads(ART_PATH.read_text())

passed = failed = 0

def check(name: str, condition: object, detail: str = "") -> None:
    global passed, failed
    ok = bool(condition); passed += int(ok); failed += int(not ok)
    suffix = f" ({detail})" if detail else ""
    print(f"[{'PASS' if ok else 'FAIL'}][generated_self_check] {name}{suffix}")

print("== reproducibility ==")
with tempfile.TemporaryDirectory(prefix="tss3-opendbc-") as td:
    out = Path(td) / "readiness.json"
    proc = subprocess.run([sys.executable, str(REPO / "tools/targets/corolla/builders/build_corolla_tss3_opendbc_readiness.py"), "--output", str(out)], cwd=REPO, capture_output=True, text=True, check=False)
    check("builder succeeds", proc.returncode == 0, proc.stderr.strip()[:200])
    if out.exists():
        check("tracked artifact is generator-drift free", json.loads(out.read_text()) == ART)

print("\n== upstream prior art ==")
check("current upstream Toyota prior art was checked", ART["upstream_prior_art"]["current_upstream_checked_commit"] == "7343a66d46213d5f73528afc6c6db713ebd88a9d")

print("\n== specimen discipline ==")
spec = ART["specimen_boundaries"]
check("exact H Tx set is pinned", spec["exact_h_tx_pdus"] == [["0x030", 32], ["0x351", 4], ["0x394", 3], ["0x4A3", 8], ["0x4C8", 8]])
check("exact H SecOC Rx set is pinned", spec["exact_h_secoc_rx_pdus"] == [["0x00F", 8], ["0x0D7", 32], ["0x0B6", 32]])
vis = spec["public_route_vs_exact_h_f_visibility"]
check("route sees sync/D7 but not B6", vis["secoc_rx_observed_counts"] == {"0x00F/8": 588, "0x0B6/32": 0, "0x0D7/32": 2943})
check("route sees only 0x030 of H/F exact Tx set", vis["tx_observed_counts"] == {"0x030/32": 5888, "0x351/4": 0, "0x394/3": 0, "0x4A3/8": 0, "0x4C8/8": 0})
join30 = spec["public_route_0x030_exact_h_f_rule_join"]
check("route 0x030 matches exact H/F additive rule on all frames", join30["frame_count"] == join30["rule_matches"] == 5888 and join30["exact_h_f_additive_rule"]["wire_byte"] == 7)
span_spec = spec["span_moving_rlog"]
check("Span moving rlog has no usable F181 join", span_spec["identity_boundary"]["rlog_has_no_usable_f181_join"] is True and span_spec["identity_boundary"]["same_dongle"] is False)
check("Span moving rlog is unswapped ELM327 observation", span_spec["harness_observation_boundary"]["all_samples_elm327_param1"] is True)
native_acc = span_spec["native_acc_gate"]
check("Span retained rlog closes native 0x08A ACC gate", native_acc["acc_engaged_frames"] == 37 and native_acc["acc_disengaged_frames"] == 2363 and native_acc["state_when_engaged"] == [93] and native_acc["state_when_disengaged"] == [18])
public_gear = spec["public_route_gear"]
check("public route closes 0x3BF P/R/D transitions", public_gear["0x3BF"]["direct_observed_labels"] == {"0x10": "D", "0x40": "R", "0x80": "P"} and [x["raw"] for x in public_gear["0x3BF"]["transitions"]] == [128, 64, 16])
check("public 0x2A1 independently corroborates P/R/D", public_gear["0x2A1"]["direct_observed_labels"] == {"0x01": "P", "0x02": "R", "0x04": "D"} and [x["raw"] for x in public_gear["0x2A1"]["transitions"]] == [1, 2, 4])
check("GTS+ P5 hybrid preserves P/R/N/D/B ordering", spec["gts_p5_hybrid_shift_position"] == {"source": "HV_P5.ddb", "name": "Shift Position", "pattern_display": {"0": "P", "2": "R", "4": "N", "6": "D", "8": "B"}})

print("\n== cross-year TSS3 FD network ==")
fd = ART["tss3_fd_network"]
span = fd["span_2025_static"]
span_move = fd["span_2025_moving_discord_rlog"]
check("Span source ZIP is exact tracked archive", span["source_zip"]["sha256"] == "a5744b4c4627d3e5c20d590bb882d25b9b40c0679cbc3e9660140c7f2ef5262b")
check("Span capture member identity is pinned", span["member"] == {"line_count": 75192, "path": "tsk/uds-sweep/ready_capture.ndjson", "sha256": "182ae388d292d38edea892ce02565f51ac1c36453aae5c302d8e32c1abcd0ae9", "size": 11981966})
check("Span static bus0/bus2 ID/DLC sets are equal", span["bus0_bus2_same_id_dlc_set"] is True)
check("Span static bus0/bus2 payload sequences are byte-identical", span["bus0_bus2_payload_sequences_equal"] is True and all(x["payload_sequence_equal"] for x in span["bus0_bus2_equality_by_id"]))
check("2023 and static Span share exact 22-ID/DLC baseline", fd["cross_year_same_bus0_id_dlc_set"] is True and fd["cross_year_public_bus0_equals_span_bus2_id_dlc_set"] is True and len(fd["cross_year_id_dlc_set"]) == 22)
check("moving Span independently preserves exact 22-ID/DLC baseline", fd["moving_span_matches_public_bus0_id_dlc_set"] is True and fd["moving_span_bus0_bus2_same_id_dlc_set"] is True and span_move["bus0_bus2_same_id_dlc_set"] is True and span_move["bus0_bus2_payload_sequences_equal"] is True)
overlap = fd["tss2_radar_track_namespace_overlap"]
check("13 TSS3 FD PDUs overlap older TSS2 radar-track namespace", overlap["upstream_ranges"] == ["0x180..0x18F", "0x190..0x19F"] and overlap["matching_count"] == 13 and [x["can_id"] for x in overlap["matching_tss3_bus0_pdus"]] == [f"0x{x:03X}" for x in range(0x180, 0x18D)])

print("\n== Span moving-rlog harness measurements ==")
bus = ART["bus_and_suppression_boundary"]
span_bus = bus["span_moving_observation"]
check("Span rlog stayed direct normal-harness observation", span_bus["panda_state_samples"] == 599 and span_bus["all_samples_elm327_param1"] is True and span_bus["all_samples_harness_status_flipped"] is True)

print("\n== retained contracts ==")
check("readiness carries 242-event 0x394 fault contract", sum(ART["specimen_boundaries"]["fault_state_contract"]["class_counts"].values()) == 242 and ART["specimen_boundaries"]["fault_state_contract"]["class_to_state"]["0x02"]["states"] == [6,7] and ART["specimen_boundaries"]["fault_state_contract"]["aging"]["class2_class4_secondary_age"] == 600)
check("readiness carries force7 source contract", ART["specimen_boundaries"]["remaining_status_contract"]["can_0x351_force7"]["condition"] == "(FEBE65E4 & 0x0003) != 0 AND FEBE7E13 != 0")
carrier = ART["specimen_boundaries"]["command5_runtime_carrier"]
check("readiness carries static H/F carrier candidate sizes", carrier["static_candidate"]["size"] == 464 and carrier["proxy"]["size"] == 424 and carrier["canary"]["size"] == 298)
direct = carrier["direct_canary"]
check("readiness operationalizes exact same-car direct canary", direct["tool"] == "exploit/ephemeral_runtime/corolla_hf_direct_canary.py" and direct["package"]["payload_sha256"] == "b6d4b261ef6fb614ef0c9f8cd72bc7e7fb7608a793f9094ec76fe226bd884367" and direct["field_proven_bootstrap"]["did_0203"] == "0000000000" and direct["field_proven_bootstrap"]["post_10f0_ram_substitution_required"] is False and direct["success_gate"]["heartbeat_address"] == "0xFEBFFB80" and direct["success_gate"]["command5_proxy_authorized_by_this_plan"] is False)
direct_cmd5 = carrier["direct_command5"]
check("readiness operationalizes guarded exact-H/F command5 second stage", direct_cmd5["tool"] == "exploit/ephemeral_runtime/corolla_hf_direct_command5.py" and direct_cmd5["package"]["payload_sha256"] == "a81b367febb819f4016a0880c707b82fb7f46f1bad5ec59119e43aec0140bfc5" and direct_cmd5["probe"]["command5"]["input_length"] == 36 and direct_cmd5["live_guards"]["successful_canary_result_required"] and direct_cmd5["live_guards"]["reset_to_stock_confirmation_required"] and direct_cmd5["live_guards"]["steering_can_transmit_used"] is False)

print(f"\n== RESULT: {passed} passed, {failed} failed ==")
raise SystemExit(1 if failed else 0)
