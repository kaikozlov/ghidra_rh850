#!/usr/bin/env python3
"""Verify the exact-Camry EBU topology interpretation against current GTS+."""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / "data/generated/camry_2026_ebu_topology.json"
GEN = ROOT / "tools/targets/camry/analysis/analyze_camry_2026_ebu_topology.py"

passed = failed = 0


def check(name: str, value: object) -> None:
    global passed, failed
    ok = bool(value)
    passed += int(ok)
    failed += int(not ok)
    print(f"[{'PASS' if ok else 'FAIL'}][camry_ebu] {name}")


with tempfile.TemporaryDirectory() as td:
    out = Path(td) / "ebu.json"
    proc = subprocess.run([sys.executable, str(GEN), "--output", str(out)], cwd=ROOT,
                          capture_output=True, text=True, check=False)
    check("generator exits cleanly", proc.returncode == 0)
    check("artifact regenerates byte-exact", proc.returncode == 0 and out.read_bytes() == ART.read_bytes())

art = json.loads(ART.read_text())
exact = art["exact_camry"]
check("exact Camry denominator is three current vehicle types and 18 options",
      [x["id"] for x in exact["vehicle_types"]] == [12704, 12862, 12984]
      and exact["can_bus_car_id"] == "0x00A7D910" and exact["option_count"] == 18)
check("logical membership is invariant while physical junction labels can vary",
      exact["network_membership_variant_count"] == 1 and exact["junction_attachment_variant_count"] == 12)

bus4 = {row["component_index"]: row for row in exact["bus4_placements"]}
check("Brake Booster and Skid share No.2 Global CAN Junction",
      bus4["0x28"]["junction_name"] == "No. 2 Global CAN Junction Connector"
      and bus4["0x29"]["junction_name"] == "No. 2 Global CAN Junction Connector")
check("EPS is Bus4 via literal EBU attachment in every option",
      bus4["0x32"]["ecu_domain"] == "Power Steering (EPS)"
      and bus4["0x32"]["junction_name"] == "EBU"
      and exact["critical_brake_eps_junctions_invariant_across_all_options"] is True)
check("EBU is not an installed exact-Camry ECU component",
      exact["ebu_ecu_component_present"] is False and exact["component_0x65_present"] is False
      and len(exact["ebu_junction_rows"]) == 1)

vocab = art["gts_vocabulary"]
check("current GTS English corpus does not spell out EBU acronym",
      vocab["literal_ebu_expansion_present"] is False
      and not any(vocab["expansion_search_hits"].values()))
rows = vocab["ebu_node_monitor_rows"]
check("P5 brake databases explicitly contain EBU-node telemetry",
      all(len(rows[key]) >= 8 for key in ("abs_p5", "brake_booster_p5", "epb_p5")))
check("P6 successor keeps EBU-node telemetry on BSCM_B but not BSCM_A",
      len(rows["bscm_b_p6"]) >= 8 and rows["bscm_a_p6"] == []
      and vocab["p6_successor_category_control"]["6004"] == {"database": "BSCM_A_P6.ddb", "name": "Brake/EPB"}
      and vocab["p6_successor_category_control"]["6005"] == {"database": "BSCM_B_P6.ddb", "name": "Brake Booster"})
probe = vocab["p6_ebu_identity_probe"]
check("P6 A/B split favors EBU as Brake/EPB-side node",
      {x["name"] for x in probe["bscm_a_native"]} == {"FR Wheel Speed", "Lateral G"}
      and any(x["name"] == "FR Wheel Speed (EBU node)" for x in probe["bscm_b_ebu_mirror"]))
check("ABS_P5 exposes ordinary and ch2 power-steering communication vocabulary",
      vocab["brake_to_eps_channel_vocabulary"]["abs_p5_dtc_rows"]["U013187"]["description"] == "Lost Communication with Power Steering Control Module"
      and "(ch2)" in vocab["brake_to_eps_channel_vocabulary"]["abs_p5_dtc_rows"]["U11B187"]["description"]
      and vocab["brake_to_eps_channel_vocabulary"]["eps_communication_open_monitor"][0]["primary_did"] == "0x102F")
check("interpretation does not invent a discrete EBU filter ECU",
      art["interpretation"]["discrete_ebu_filter_ecu_supported_by_exact_camry_topology"] is False
      and art["interpretation"]["one_eps_controller_compatible_with_upstream_segmentation"] is True)

print(f"\nResults: {passed} passed, {failed} failed")
raise SystemExit(1 if failed else 0)
