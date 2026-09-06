#!/usr/bin/env python3
"""Verify the full retained-road Camry Target-Lateral-ID family census."""
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
r = json.loads((REPO / "data/generated/camry_2026_lateral_family_census.json").read_text())


def check(name: str, cond: bool) -> None:
  if not cond:
    raise AssertionError(name)
  print(f"[PASS] {name}")


check("artifact schema", r["schema"] == "camry-2026-lateral-family-census-v1")
check("full selected road corpus is 12 routes / 513 retained rlog segments",
      r["corpus"]["route_count"] == 12 and r["corpus"]["segment_count"] == 513)
check("all selected routes present",
      set(r["routes"]) == {"1c", "27", "29", "2a", "2c", "2d", "37", "3b", "3c", "3d", "3e", "3f"})

agg = r["aggregate"]
check("complete 0x08A Target-Lateral-ID population exact",
      agg["native_08a_target_lateral_id_counts"] == {
        "0": 512847, "4": 298, "11": 653586, "18": 52853,
      })
check("road-observed steering profiles are exactly LDA/LTA-SDG family 4/11/18",
      agg["observed_target_lateral_ids"] == [0, 4, 11, 18] and
      agg["observed_nonzero_ids"] == [4, 11, 18])
check("exact-F33 profiles PCS/Hands-Off-LTA/PDA are not road-observed",
      agg["unobserved_exact_f33_profiles"] == [1, 10, 19])
check("all nonzero request episodes retained",
      agg["nonzero_episode_counts_by_id"] == {"4": 6, "11": 165, "18": 81})

# Aggregate the richer per-ID fields independently from the route summaries.
by_id: dict[int, dict] = {}
transitions: Counter[str] = Counter()
for route in r["routes"].values():
  transitions.update(route["id_transition_counts"])
  for lid_s, row in route["target_lateral_ids"].items():
    lid = int(lid_s)
    a = by_id.setdefault(lid, {
      "frames": 0, "level": Counter(), "cruise": Counter(), "b23": Counter(),
    })
    a["frames"] += row["frames"]
    a["level"].update({int(k): v for k, v in row["request_level_counts"].items()})
    a["cruise"].update({int(k): v for k, v in row["cruise_latch_counts"].items()})
    a["b23"].update(row["b23_counts"])

check("ID11 is uniformly 100-percent request level with FRC cruise latch set",
      by_id[11]["frames"] == 653586 and by_id[11]["level"] == Counter({100: 653586}) and
      by_id[11]["cruise"] == Counter({1: 653586}))
check("ID18 is uniformly cruise-off/B23=0x20 and uses 25/50-percent request levels",
      by_id[18]["frames"] == 52853 and by_id[18]["cruise"] == Counter({0: 52853}) and
      by_id[18]["b23"] == Counter({"0x20": 52853}) and
      by_id[18]["level"] == Counter({50: 27837, 25: 25016}))
check("ID4 LDA is a 100-percent request and occurs both cruise-off and cruise-on",
      by_id[4]["frames"] == 298 and by_id[4]["level"] == Counter({100: 298}) and
      by_id[4]["cruise"] == Counter({1: 152, 0: 146}))
check("request family directly switches between nonzero profiles without an ID0 publication",
      transitions["18->11"] == 28 and transitions["18->4"] == 1 and
      transitions["11->4"] == 2 and transitions["4->11"] == 2)

# 0x081 is the protected chassis-side returned/reference state.  Pair only to a
# fresh latest 0x08A within 100 ms; mismatches are concentrated at transitions.
check("0x081 returned-state Target-Lateral-ID population exact",
      agg["native_081_target_lateral_id_counts"] == {
        "0": 427400, "4": 248, "11": 544673, "18": 44045,
      })
pair = agg["native_081_latest_08a_pairing"]
check("over one million fresh 0x081/0x08A state pairs retained",
      pair["eligible"] == 1016141 and pair["match"] == 1015978)
check("0x081 mirrors latest 0x08A Target Lateral ID above 99.98 percent",
      agg["native_081_latest_08a_match_fraction"] > 0.9998)
check("0x081 also mirrors the newly observed ID4 family",
      pair["11->4"] == 1 and pair["4->11"] == 2 and pair["0->4"] == 1 and pair["4->0"] == 1)

# Route 27 predates the final relay topology and records each accepted injected
# B6 twice in the same CAN event: src128 Panda TX echo plus an exact src2 copy.
# Do not misclassify that copy as stock/native B6.
check("raw low-source B6 population is exactly the route27 TX-echo duplicate population",
      agg["b6_src_0_1_2_id_counts_raw"] == {"0": 60722, "11": 46078} and
      agg["b6_same_event_tx_echo_duplicate_id_counts"] == {"0": 60722, "11": 46078})
check("no unmatched stock/native B6 candidate exists in selected road corpus",
      agg["unmatched_native_b6_candidate_id_counts"] == {})
r27 = r["routes"]["27"]["b6"]
check("route27 exact src2/TX-echo duplicate proof retained",
      r27["can_src_counts"].get("2") == 106800 and r27["can_src_counts"].get("128") == 106800 and
      r27["src_0_1_2_id_counts_raw"] == r27["same_event_tx_echo_duplicate_id_counts"] ==
      r27["panda_tx_echo_id_counts"])

# Exact F33 profile-selection semantics and secondary-field consumer closure.
f33 = r["exact_f33"]
check("exact-F33 profile selector is CEFFC and defaults every invocation",
      f33["selector_entry"] == "0x000CEFFC" and f33["selector_resets_to_default_each_invocation"])
check("exact-F33 selector uses only validity plus current Target Lateral ID",
      f33["selector_direct_inputs"] == ["FEBEACBD", "FEBECAFF", "FEBEADB0(Target Lateral ID snapshot)"] and
      f33["selector_requires"] == {"FEBEACBD": 0, "FEBECAFF": 1})
check("all six exact-F33 B6 steering profiles map directly to common banks",
      f33["selector_bank_map"] == {"1": 0, "4": 1, "10": 3, "11": 2, "18": 5, "19": 4})
check("runtime selector has no previous-ID comparison",
      not f33["unpacker_has_previous_target_id_comparison"] and
      f33["selector_writer_entries_complete_decompilation_corpus"] == ["0x000CEFF4", "0x000CEFFC"])
check("FRC/cruise state carriers are absent from exact-F33 normal Rx",
      f33["known_frc_state_carriers_absent_from_exact_rx"] ==
      ["0x081", "0x08A", "0x0FE", "0x251", "0x371", "0x412"] and
      f33["exact_normal_rx_descriptor_count"] == 43)
check("35-ms B6 loss timeout remains communication supervision, not profile ownership",
      f33["communication_timeout"] == {
        "pdu": 44, "nominal_ms": 35, "basis": "seven exact-F33 foreground ticks at 5 ms",
      })
check("profile-indexed persistence supervisor is distinct from selector lock",
      f33["profile_supervision"]["thresholds_by_bank"]["2_LTA_LCA"] ==
      {"abs_signal_threshold": 1280, "persistence_cycles": 96} and
      f33["profile_supervision"]["thresholds_by_bank"]["5_SDG"] ==
      {"abs_signal_threshold": 2048, "persistence_cycles": 96} and
      f33["profile_supervision"]["ce7fe_recomputes_common_readiness"])

sec = f33["secondary_application_fields"]
check("secondary-field reader census closes unused direct companions",
      sec["264"]["direct_reader_entries"] == [] and sec["266"]["snapshot"] is None and
      sec["267"]["direct_reader_entries"] == [] and sec["271"]["direct_reader_entries"] == [] and
      sec["272"]["direct_reader_entries"] == [])
check("signal263 is scoped to Self-Propelled Transport state, not ordinary profile enable",
      sec["263"]["wire"] == "B6[7]" and sec["263"]["direct_reader_entries"] == ["0x000CB664"] and
      "Self-Propelled Transport" in sec["263"]["role"])
check("signal265/268/269/270 retain recovered controller roles",
      sec["265"]["direct_reader_entries"] == ["0x000CDA20"] and
      sec["268"]["direct_reader_entries"] == ["0x000CEC8A"] and
      sec["269"]["direct_reader_entries"] == ["0x000CE3AA"] and
      sec["270"]["direct_reader_entries"] == ["0x000CDFF8"])
check("signal273 is a separate status/mode path, not CEFFC authorization",
      sec["273"]["wire"] == "B10[2:0]" and sec["273"]["direct_reader_entries"] == ["0x000CFDA0"] and
      "not a profile-selector input" in sec["273"]["role"])
check("no generic secondary B6 command-enable bit is recovered",
      not f33["secondary_field_authorization_boundary"]["generic_command_enable_recovered"] and
      f33["secondary_field_authorization_boundary"]["cefa4_communication_validity_shape"])
