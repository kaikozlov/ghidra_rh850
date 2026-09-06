#!/usr/bin/env python3
"""Verify the Camry TSS3 PDA/SDG attribution artifact."""
from __future__ import annotations

import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
r = json.loads((REPO / "data/generated/camry_2026_pda_sdg_attribution.json").read_text())


def check(name: str, cond: bool) -> None:
  if not cond:
    raise AssertionError(name)
  print(f"[PASS] {name}")


check("artifact schema", r["schema"] == "camry-2026-pda-sdg-attribution-v1")
f33 = r["exact_f33"]
check("exact F33 accepts both SDG and PDA profiles",
      f33["accepted_controller_values"]["18"] == "SDG" and
      f33["accepted_controller_values"]["19"] == "PDA")
check("SDG and PDA select distinct common-controller banks",
      f33["controller_bank_map"]["18"] == 5 and f33["controller_bank_map"]["19"] == 4)
check("ID19 has no separate direct snapshot consumer outside CEFFC",
      f33["id19_direct_snapshot_consumers"] == ["0x000ceffc"])
check("common profile selector has broad downstream use", f33["common_cb00_reader_function_count"] >= 40)
check("separate special consumer is ID49 Self-Propelled Transport",
      f33["separate_special_snapshot_consumer"]["raw_value"] == 49 and
      f33["separate_special_snapshot_consumer"]["oem_label"] == "Self-Propelled Transport")

gts = r["gts_tss3"]
check("Toyota recorder classifies PDA-SA RoB as SDG",
      gts["pda_sa"]["rob_code"] == "22B4" and
      gts["pda_sa"]["rob_system_type"] == 6 and
      gts["pda_sa"]["rob_system_name"] == "SDG" and
      "PDA(SA)" in gts["pda_sa"]["rob_name"])
check("PDA-OAA exposes lateral request ID, pinion and gains",
      gts["pda_oaa_request"]["data_ids"] == ["5A09", "5A0A", "5A0D"] and
      "PDA(OAA) request pinion angle" in gts["pda_oaa_request"]["field_names"] and
      "PDA(OAA) Gain for steering support" in gts["pda_oaa_request"]["field_names"] and
      "PDA(OAA) Damping control gain" in gts["pda_oaa_request"]["field_names"])

routes = r["routes"]
check("3b carries substantial ID18 SDG", routes["3b"]["target_lateral_id_counts"]["18"] > 30000)
check("3b PDA-SA-regime proxy is majority ID18",
      routes["3b"]["pda_sa_regime_proxy"]["target_lateral_id_counts"]["18"] > 30000 and
      routes["3b"]["pda_sa_regime_proxy"]["target_lateral_id_counts"]["18"] >
      routes["3b"]["pda_sa_regime_proxy"]["target_lateral_id_counts"]["0"])
for short in ("3c", "3d", "3e", "3f"):
  proxy = routes[short]["pda_sa_regime_proxy"]
  check(f"{short} has substantial eligible-regime control population", proxy["frames"] > 30000)
  check(f"{short} has zero ID18 in eligible-regime proxy", proxy["target_lateral_id_counts"].get("18", 0) == 0)
  check(f"{short} has zero observed ID19", routes[short]["target_lateral_id_counts"].get("19", 0) == 0)
check("3b also has zero observed ID19", routes["3b"]["target_lateral_id_counts"].get("19", 0) == 0)

archive = r["supplemental_archive_scan"]
check("older archive adds 186934 native 08A frames", archive["native_08a_frames"] == 186934)
check("older archive contains substantial ID18 but zero ID19",
      archive["aggregate_target_lateral_id_counts"]["18"] == 16876 and archive["id19_frames"] == 0)
