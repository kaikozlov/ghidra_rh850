#!/usr/bin/env python3
"""Verify exact-F33 normal-COM lateral-ingress closure against retained live CAN."""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
ART = REPO / "data/generated/camry_8965F3307000_external_lateral_ingress.json"
BUILD = REPO / "tools/build_camry_8965F3307000_external_lateral_ingress.py"
CLASS_ART = REPO / "data/generated/camry_2026_class_l_upstream_correlation.json"
CLASS_BUILD = REPO / "tools/analyze_camry_2026_class_l_upstream.py"

passed = failed = 0

def check(name: str, cond: object, detail: str = "") -> None:
    global passed, failed
    ok = bool(cond); passed += int(ok); failed += int(not ok)
    print(f"[{'PASS' if ok else 'FAIL'}][dynamic_trace] {name}" + (f" ({detail})" if detail else ""))

with tempfile.TemporaryDirectory() as td:
    out = Path(td) / "ingress.json"
    p = subprocess.run([sys.executable, str(BUILD), "--out", str(out)], cwd=REPO, capture_output=True, text=True)
    check("generator succeeds", p.returncode == 0, p.stderr[-300:])
    check("artifact regenerates byte-exact", p.returncode == 0 and out.read_bytes() == ART.read_bytes())
    class_out = Path(td) / "class-l.json"
    p = subprocess.run([sys.executable, str(CLASS_BUILD), "--out", str(class_out)], cwd=REPO, capture_output=True, text=True)
    check("Class-L/upstream analyzer succeeds", p.returncode == 0, p.stderr[-300:])
    check("Class-L/upstream artifact regenerates byte-exact", p.returncode == 0 and class_out.read_bytes() == CLASS_ART.read_bytes())

art = json.loads(ART.read_text())
check("schema/target exact", art["schema"] == "camry-8965f3307000-external-lateral-ingress-v1" and art["target"]["software_id"] == "8965F3307000" and art["target"]["corpus_function_count"] == 6065)
check("normal Rx/scalar census exact", art["normal_rx"]["descriptor_count"] == 43 and art["normal_rx"]["scalar_receive_call_count"] == 116)
ctrl = art["controller1_acceptance"]
check("controller1 acceptance span is exhausted", ctrl["count"] == 47 and ctrl["normal_rule_indices"] == [0,42] and ctrl["normal_rules_equal_descriptor_order"] is True)
check("only diagnostic/XCP rules follow normal COM", [(x.get("can_id"), x["role"]) for x in ctrl["special_tail"]] == [("0x7A1","physical UDS"),("0x777","functional UDS"),("0x7A0","secondary diagnostics"),("0x7F7","application XCP")])
src = art["b6_receiver_source_expectation"]
check("F33 communication monitor maps slot1A to PDU44/B6", src["communication_monitor"]["row_index"] == 5 and src["communication_monitor"]["status_slot"] == "0x1A" and src["communication_monitor"]["monitored_pdu"] == 44 and src["communication_monitor"]["can_id"] == "0x0B6")
check("F33 B6 loss is Brake System Control Module missing-message", src["communication_monitor"]["dem_event"] == "0x0143" and src["communication_monitor"]["dtc_index"] == 82 and src["techstream_dtc"] == {"code":"U012987","description":"Lost Communication with Brake System Control Module","failure":"Missing Message"})

cands = {(x["can_id"], x["signal"]): x for x in art["normal_rx"]["signed_12plus_candidates"]}
check("signed >=12-bit ingress set exact", set(cands) == {(0x025,187),(0x025,189),(0x0B6,262),(0x0D5,212),(0x0D5,213),(0x115,134),(0x1C5,141),(0x64F,255),(0x64F,257)})
check("025 large fields are measured feedback", cands[(0x025,187)]["classification"] == cands[(0x025,189)]["classification"] == "measured-feedback")
check("B6 signed16 remains external lateral command", cands[(0x0B6,262)]["classification"] == "external-lateral-command" and cands[(0x0B6,262)]["byte_offset"] == 4)
check("D5 signed16s are monitor paths", cands[(0x0D5,212)]["classification"] == cands[(0x0D5,213)]["classification"] == "monitor/plausibility")
check("115 signed16 is engine-domain", cands[(0x115,134)]["classification"] == "engine-domain" and art["special_paths"]["0x115"]["gtsplus_name"] == "Engine Revolution")
check("1C5/64F command-sized fields are not observed", all(cands[k]["classification"] == "not-observed" for k in ((0x1C5,141),(0x64F,255),(0x64F,257))))

cone = art["scalar_command_cone_census"]
cone_ids = {261,262,263,265,268,269,270,273,186,187,188,189,211,212,213,243,223,130,141}
check("corrected scalar command-cone census is exactly 19/116", cone["scalar_receive_call_count"] == 116 and cone["nonempty_count"] == 19 and cone["empty_count"] == 97 and set(cone["nonempty_signal_ids"]) == cone_ids and len(cone["empty_signal_ids"]) == 97)
chains = {row["signal"]: row for row in cone["chains"]}
expected_chain_addresses = {
    130:("0xFEBE800E","0xFEBEF192","0xFEBEAE0A"), 141:("0xFEBE801E","0xFEBEF196","0xFEBEAE08"),
    186:("0xFEBE804E","0xFEBEF06B","0xFEBEACC4"), 187:("0xFEBE8048","0xFEBEF1A0","0xFEBEADFE"),
    188:("0xFEBE804F","0xFEBEF06F","0xFEBEACC5"), 189:("0xFEBE804A","0xFEBEF19E","0xFEBEAE22"),
    211:("0xFEBE8076","0xFEBEF097","0xFEBEACCE"), 212:("0xFEBE8072","0xFEBEF1BC","0xFEBEAE04"),
    213:("0xFEBE8074","0xFEBEF1BE","0xFEBEAE06"), 223:("0xFEBE807F","0xFEBEF091","0xFEBEACD6"),
    243:("0xFEBE80A0","0xFEBEF094","0xFEBEACCD"), 261:("0xFEBE80BC","0xFEBEF130","0xFEBEADB0"),
    262:("0xFEBE80B8","0xFEBEF1FA","0xFEBEAE90"), 263:("0xFEBE80CB","0xFEBEF155","0xFEBEADDD"),
    265:("0xFEBE80C0","0xFEBEF134","0xFEBEADBB"), 268:("0xFEBE80C3","0xFEBEF137","0xFEBEADBC"),
    269:("0xFEBE80C4","0xFEBEF138","0xFEBEADBD"), 270:("0xFEBE80C5","0xFEBEF139","0xFEBEADBE"),
    273:("0xFEBE80CA","0xFEBEF14D","0xFEBEADD9"),
}
check("all 19 raw/stage/snapshot chains are exact", {sid:(row["raw"],row["stage"],row["snapshot"]) for sid,row in chains.items()} == expected_chain_addresses)
check("signal243 stack-RMW chain is pinned", chains[243]["unpacker"] == "0x0004BB62" and chains[243]["destination_expression"] == "auStack_9" and chains[243]["raw_copy"] == "0x0004BB62 stack-RMW auStack_9[0]" and [chains[243][k] for k in ("raw","stage","snapshot")] == ["0xFEBE80A0","0xFEBEF094","0xFEBEACCD"])
check("B6 has sole selector and magnitude", chains[261]["classification"] == "sole-mode-selector" and chains[262]["classification"] == "sole-command-magnitude" and all(row["classification"] not in {"sole-mode-selector","sole-command-magnitude"} for row in cone["chains"] if row["can_id"] != "0x0B6"))
check("non-B6 cone is feedback/monitor/gate only", cone["semantics"]["non_b6"].startswith("non-B6 cone members are feedback"))

identity = art["same_image_software_compatibility_identity"]
check("8A311 record is same-image compatibility identity", identity["f181_callback"] == "0x0004FA26" and identity["f181_count"] == 2 and identity["f181_records"] == ["8965F3307000 @ 0x00020860","8A3113303100 @ 0x00017DC0"] and identity["startup_chain"] == ["0x000637EE","0x00062D5E"])
check("startup mismatch behavior and DID2032 are distinct", identity["mismatch_behavior"]["jb1ba101_mismatch"] == "additionally writes 0x5A to FEBF066C" and "does not set" in identity["mismatch_behavior"]["8a311_prefix_mismatch"] and identity["did2032"].startswith("0x0004F9DE separately"))

live = art["live_intersection"]
check("two drives total 3.574M frames", live["combined_incoming_frames"] == 3574703)
check("B6 absent on every bus", live["selected_counts"]["0x0B6/32"] == {"0":0,"1":0,"2":0})
check("D5 first signed16 stays tiny", live["d5_signed16_b1_b2"] == {"count":55793,"min":-5,"max":11,"unique":17})
check("D5 second signed16 is identically zero", live["d5_signed16_b3_b4"] == {"count":55793,"min":0,"max":0,"unique":1})
check("115 engine-revolution field is dynamically populated", live["id115_signed16_b0_b1"]["count"] == 47384 and live["id115_signed16_b0_b1"]["max"] == 2884 and live["id115_signed16_b0_b1"]["unique"] > 1000)
check("generic group receive surface is absent live", art["special_paths"]["generic_group_receive"]["can_ids"] == [f"0x{x:03X}" for x in range(0x13,0x20)] and art["special_paths"]["generic_group_receive"]["live_total"] == 0)
check("B6 reaches Toyota-named command torque", art["b6_to_command_torque"]["gtsplus_terminal"] == "0x1C02 Command Value Torque")
check("normal-COM conclusion is bounded", "No observed ordinary EPS-CAN field besides B6" in art["conclusion"]["normal_com"] and "does not prove" in art["boundary"][1])
check("production output remains disabled", art["conclusion"]["production_output_authorized"] is False)

class_art = json.loads(CLASS_ART.read_text())
check("Class-L intervals preserve cross-segment B", class_art["drives"]["drive_a"]["class_l"]["intervals"][0]["duration_s"] == 16.119256 and class_art["drives"]["drive_b"]["class_l"]["intervals"][0] == {"start_segment":20,"end_segment":21,"start_ns":1267881231677,"end_ns":1325065360088,"duration_s":57.184128})
check("persistent accepted/EPS edge result is negative", class_art["combined"]["common_accepted_rise_flip_bits_across_drives"] == [] and class_art["combined"]["eps_0x030_persistent_flip_total"] == 0 and all(d["eps_0x030_stability"]["persistence_threshold"] == 0.95 for d in class_art["drives"].values()))
check("matched 0x18A result is negative", class_art["combined"]["matched_upstream_0x18a_rise_flip_bits_across_drives"] == [] and class_art["combined"]["matched_upstream_0x18a_class_l_step_detected"] is False)
check("0x18C staircase record count stays three", all(edge["record_counts"] == {"3":edge["frames"]} for d in class_art["drives"].values() for edge in d["upstream_0x18c_record_counts"]))
check("0x181 signed-LE lag result is pinned", [(d["upstream_0x181_lag_field"]["wire"], d["upstream_0x181_lag_field"]["peak_dt_ms"], d["upstream_0x181_lag_field"]["peak_r"]) for d in class_art["drives"].values()] == [("bytes[35:37] signed LE i16",-200,-0.7192),("bytes[35:37] signed LE i16",-240,-0.7287)])
check("0x090 exploratory composite retired with reproduction intact", [(d["eps_metrics_inside_class_l"]["exploratory_0x090_reproduction"]["best_field"], d["eps_metrics_inside_class_l"]["exploratory_0x090_reproduction"]["best_r"], d["eps_metrics_inside_class_l"]["exploratory_0x090_reproduction"]["peak_lag_ms"]) for d in class_art["drives"].values()] == [("B12[3:0]+B13",0.9931,-60),("B12[3:0]+B13",0.7615,-70)] and all(d["eps_metrics_inside_class_l"]["exploratory_0x090_reproduction"]["classification"].startswith("resolved: synthetic cross-signal composite outside the exact-F33 0x090 receive surface") for d in class_art["drives"].values()))
fw_a = class_art["drives"]["drive_a"]["eps_metrics_inside_class_l"]["firmware_exact_0x090"]
fw_b = class_art["drives"]["drive_b"]["eps_metrics_inside_class_l"]["firmware_exact_0x090"]
check("0x090 firmware-exact geometry and lead/lag pinned",
      [fw_a["signals"][s]["wire"] for s in ("sig229","sig232","sig235")] == ["B0[1:0]+B1","B2[1:0]+B3","B4[1:0]+B5"]
      and [(fw_a["signals"][s]["r_vs_0x025_angle"], fw_a["signals"][s]["peak_lag_ms"], fw_a["signals"][s]["slope_counts_per_deg_at_peak"]) for s in ("sig229","sig232","sig235")] == [(0.1831,120,0.1097),(0.8934,-40,1.3163),(0.9924,-60,0.9569)]
      and [(fw_b["signals"][s]["r_vs_0x025_angle"], fw_b["signals"][s]["peak_lag_ms"], fw_b["signals"][s]["slope_counts_per_deg_at_peak"]) for s in ("sig229","sig232","sig235")] == [(0.4115,-120,8.8637),(0.3331,10,1.9853),(0.7428,-70,1.1976)])
check("0x090 strong motor correlations do not reproduce as leads",
      not any(abs(fw_a["signals"][s]["r_vs_0x030_motor_proxy"]) >= 0.25
                  and abs(fw_b["signals"][s]["r_vs_0x030_motor_proxy"]) >= 0.25
                  and fw_a["signals"][s]["motor_peak_lag_ms"] > 0
                  and fw_b["signals"][s]["motor_peak_lag_ms"] > 0
                  for s in ("sig229","sig232","sig235")))
check("0x090 synthetic winners sit outside the consumed surface",
      all(fw["duplication"]["b12b13_equals_b14b15_frames"] == fw["duplication"]["frames"] == fw["duplication"]["b4_le3_frames"] for fw in (fw_a, fw_b))
      and fw_a["flags_all_zero_inside_class_l"] is True and fw_b["flags_all_zero_inside_class_l"] is True
      and fw_a["receive_surface"]["sig241_wire"] == "B28[7:4]"
      and "B6..B27 are not touched" in fw_a["receive_surface"]["defined_bytes"]
      and "sig232" in fw_a["receiver_chain"]["combination"] and "FEBEAE0C" in fw_a["receiver_chain"]["integrator"])
check("Class-L analyzer preserves exact DBC formulas", class_art["dbc_formulas"] == {"0x030_steering_wheel_torque_nm":"signed_be(71|8) * 0.1 + signed_be(139|4) * 0.01","0x025_steering_angle_deg":"signed_be(3|12) * 1.5 + signed_be(39|4) * 0.1","0x025_steering_rate_raw":"signed_be(35|12)"})

print(f"\nResults: {passed} passed, {failed} failed")
raise SystemExit(1 if failed else 0)
