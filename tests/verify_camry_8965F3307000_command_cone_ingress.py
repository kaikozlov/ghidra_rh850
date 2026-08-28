#!/usr/bin/env python3
"""Verify exact-F33 command-cone ingress census (pipeline + composition provenance)."""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
ART = REPO / "data/generated/camry_8965F3307000_command_cone_ingress.json"
BUILD = REPO / "tools/build_camry_8965F3307000_command_cone_ingress.py"
PRIOR = REPO / "data/generated/camry_8965F3307000_external_lateral_ingress.json"

passed = failed = 0


def check(name: str, cond: object, detail: str = "") -> None:
    global passed, failed
    ok = bool(cond)
    passed += int(ok)
    failed += int(not ok)
    print(f"[{'PASS' if ok else 'FAIL'}][command_cone] {name}" + (f" ({detail})" if detail else ""))


with tempfile.TemporaryDirectory() as td:
    out = Path(td) / "cone.json"
    p = subprocess.run([sys.executable, str(BUILD), "--out", str(out)], capture_output=True, text=True, check=False)
    check("builder exits clean", p.returncode == 0, p.stderr[-200:] if p.returncode else "")
    check("artifact regenerates byte-exact", out.exists() and out.read_bytes() == ART.read_bytes())

art = json.loads(ART.read_text())
check("schema/target exact",
      art["schema"] == "camry-8965f3307000-command-cone-ingress-v2"
      and art["target"]["software_id"] == "8965F3307000"
      and art["target"]["corpus_function_count"] == 6065)

den = art["ingress_denominator"]
check("extract denominator is 116 literal + 14 table-driven",
      den["literal_scalar_extracts"] == 116 and den["table_driven_extracts"] == 14)
check("table-driven extracts resolve to the 0x013..0x01F family",
      {x["can_id"] for x in den["table_driven"]} == set(range(0x13, 0x20))
      and [x["signal"] for x in den["table_driven"]] == list(range(90, 104)))
check("extract API geometry is pinned",
      den["extract_api_geometry"]["frame_block_base"] == "0xFEBE4A48"
      and den["extract_api_geometry"]["pdu_status_base"] == "0xFEBE493E")
check("0x090 10-bit transforms are the only transform helper family",
      den["transform_helpers"][0]["form"] == "s16(raw10 - 0x200)"
      and den["transform_helpers"][0]["signals"] == {"229": "0xFEBE808A", "232": "0xFEBE808C", "235": "0xFEBE808E"})

pipe = art["pipeline"]
check("L1 raw census is 116 with stack-RMW signal243",
      pipe["L1_raw_cells"]["count"] == 116 and "0x4BB62" in pipe["L1_raw_cells"]["signal243_path"])
check("L2 stages 98 raw cells over 105 edges",
      pipe["L2_stage"]["raw_cells_staged"] == 98 and pipe["L2_stage"]["edges"] == 105)
check("L2 unstaged raw cells are consumer-free",
      pipe["L2_unstaged_raw_closure"]["unstaged_count"] == 18
      and "no consumer exists" in pipe["L2_unstaged_raw_closure"]["evidence"])
census = pipe["L3_stage_reader_census"]
check("stage-reader census is 52 readers, 15 in-cluster",
      census["total"] == 52 and census["in_cluster"] == 15 and census["max_reader"] == "0xBF0EC"
      and len(census["readers"]) == 52)
check("no C/D-family compute reads stages directly",
      all(int(r, 16) <= 0xBF0EC for r in census["readers"])
      and "consume the L4 snapshot bank instead" in census["structural_claim"])
check("group API callers are exactly the two qualifiers",
      pipe["group_api_callers"] == ["0x693FE", "0x697F4"])
check("L2 init-only stage cells have no runtime writer",
      pipe["L2_stage"]["init_only_stage_cells"] == {
          "0xFEBEF098": 0, "0xFEBEF099": 0, "0xFEBEF09C": 1, "0xFEBEF0AA": 0, "0xFEBEF1C0": 0})
check("L4 has six snapshot copiers totalling 306 destinations",
      pipe["L4_unique_snapshot_destinations"] == 306
      and pipe["L4_snapshot_copiers"] == {"0xBC96A": {"exact_pairs": 1}, "0xBCA08": {"exact_pairs": 13},
                                          "0xBCAA6": {"exact_pairs": 1}, "0xBCBD8": {"exact_pairs": 46},
                                          "0xBCD62": {"exact_pairs": 245}, "0xBCD66": {"exact_pairs": 245}})

blk = art["command_block_map"]
check("command block writer is 0xBF33E with 17 statement-mapped bytes",
      blk["writer"] == "0x000BF33E" and len(blk["bytes"]) == 17)
check("command-torque byte FEBEE40A comes from FEBEAC56 (FEBECC62 path)",
      blk["bytes"]["FEBEE40A"] == ["0xFEBEAC56"] and blk["via_D0AAE"]["FEBEAC56"] == "FEBECC62 (command torque)")
check("peripheral-fed byte and constants are pinned",
      blk["bytes"]["FEBEE408"] == ["0xFEBEAC58"] and blk["bytes"]["FEBEE401"] == []
      and blk["bytes"]["FEBEE402"] == [] and blk["bytes"]["FEBEE404"] == [])

comp = art["composition_provenance"]["FEBECC50/FEBECC62 (command torque composition)"]
check("generated-COM composition value inputs are B6-only",
      "only COM-derived VALUE inputs are B6 sig261" in comp["classification"]
      and "FEBEAE90" in comp["FEBEC81A"] and "FEBE71F2" in comp["FEBECC60"])

gain = art["gain_selector_machinery"]
check("gain install writes guarded pairs",
      gain["install"].startswith("0x000CB516") and "FEBEC7AA = complements" in gain["install"].replace("-1 - ", "complements"))
check("assist activation is B6-sig261-gated",
      "FEBEADB0=='1' (B6 sig261 snapshot)" in gain["activation"]
      and "FEBEAE02 (sig246-derived speed class)" in gain["activation"])
check("gain adaptation cannot activate without B6 sig261",
      "cannot activate while B6 sig261 is absent" in gain["effect_on_command"])

pos = {x["can_id"]: x for x in art["positive_non_b6_cluster_inputs"]}
check("positive non-B6 set is exactly 0x090/0x0D7/0x675/0x13B",
      set(pos) == {"0x090", "0x0D7", "0x675", "0x13B"})
check("0x090 geometry is the 3x(flag+10-bit)+byte28 family",
      [g["signal"] for g in pos["0x090"]["geometry"]] == [227, 228, 229, 230, 231, 232, 233, 234, 235, 241]
      and [(g["signal"], g["byte"]) for g in pos["0x090"]["geometry"] if g["signal"] in (229,232,235,241)]
          == [(229,0),(232,2),(235,4),(241,28)]
      and pos["0x090"]["geometry"][2]["transform"] == "s16(x-0x200) -> FEBE808A")
check("0x090 classification is observer/plausibility with no magnitude",
      pos["0x090"]["classification"].startswith("observer/plausibility")
      and "never reach FEBECC50/FEBECC62/FEBEE400..418 as magnitudes" in pos["0x090"]["classification"])
check("0x090 integrator chain reaches plausibility flags",
      any("FEBEBFA0 = FEBEBF58*0x400/ROM_0AF564" in c for c in pos["0x090"]["chains"])
      and any("FEBEBFB1" in c for c in pos["0x090"]["chains"]))
check("0x0D7 sig246 geometry is B1:B2 u16",
      pos["0x0D7"]["geometry"][1] == {"signal": 246, "byte": 1, "bits": 16, "bit": 0, "signed": False})
check("0x0D7 sig246 snapshot FEBEAE02 feeds 13 cluster consumers",
      "CDFF8" in pos["0x0D7"]["chains"][1] and "CB664" in pos["0x0D7"]["chains"][1])
check("0x0D7 sig244 selects a handler pointer, not a magnitude",
      "FEBEAF40 stores a pointer, not a magnitude" in pos["0x0D7"]["classification"])
check("0x13B qualifier branch is B6-sig243-gated",
      "invalidated by B6 sig243 != 0" in pos["0x13B"]["chains"][1])
check("0x675 config cells are diagnostics/telemetry class",
      "no composition magnitude path recovered" in pos["0x675"]["classification"])

base = art["baseline_internal_assist_path"]
check("D0218 baseline path is explicit and B6-independent",
      "FEBECC48 baseline sum" in base["D0218_sum"]
      and "C43C + C4C0 + C3BA + CC2C + BF3C" in base["D0218_sum"]
      and base["C7BF_gate"].endswith("B6 sig261 snapshot FEBEADB0=='1'"))
check("D0382 uses AC52 as a limit on dynamic CC4E, not as command magnitude",
      base["D0382_limit"] == "FEBECC60 = clamp(FEBECC4E, +/-FEBEAC52); AC52 is a limit, not the source magnitude"
      and "0x3BDC6 selects the minimum active entry" in base["FEBEAC52_limit_provenance"]
      and set(base["limit_table"]) == {"0x2B4D", "0x3A75", "0x569A"})
check("D0284 scale is internal calibration-derived, not another external value ingress",
      base["D0284_scale_provenance"] == {
          "snapshot": "FEBEAC64 <- FEBEB140 via BCBD8",
          "calibration_u16_at_0x000AEF4C": "0x5571",
          "runtime_derivation": "FEBEB140 = floor(0x2774564E / 0x5571) = 0x7636 in B3866/B389C/B38D2",
          "reset_default": "BF97A writes FEBEB140=0x7637",
          "writer_census": ["0xB3866", "0xB389C", "0xB38D2", "0xBF97A"],
          "classification": "internal ROM/calibration-derived scale; no generated-COM/CAN value source",
      })
check("D0218 direct internal value cells and runtime writers are pinned",
      base["direct_D0218_value_cells"] == ["FEBECB38", "FEBEC5EE", "FEBEC43C", "FEBEC4C0",
                                                "FEBEC3BA", "FEBECC2C", "FEBEBF3C", "FEBECBE8"]
      and base["direct_value_runtime_writers"] == {
          "FEBECB38":"0xCF2B2", "FEBEC5EE":"0xC9A84", "FEBEC43C":"0xC7E36", "FEBEC4C0":"0xC8678",
          "FEBEC3BA":"0xC74AC", "FEBECC2C":"0xD0162", "FEBEBF3C":"0xC2B64", "FEBECBE8":"0xCFCD4"}
      and base["classification"].startswith("B6-independent EPS-internal baseline-assist magnitude path"))
check("AC2B is an internal diagnostic gate, not a CAN target",
      "FEBEB112" in base["AC2B_gate"] and "B338C sets 0x5A" in base["AC2B_gate"])

mir = art["non_com_internal_mirrors"]
check("FEBE71F2 mirror terminates at the D0382 saturation limit",
      mir["0x000FCC00"]["FEBEEF8E"] == "FEBE71F2" and mir["0x00057F00"]["FEBEEE02"] == "FEBE686C"
      and "D0382 saturation limit on dynamic FEBECC4E" in mir["into_cone"])
check("old peripheral-magnitude interpretation is gone",
      "limit, not command magnitude" in mir["classification"] and "non_com_peripheral_inputs" not in art)

cl = art["class_l_relevance"]
check("0x090 live correlation now has a bounded firmware path",
      "no 0x090 value is a command magnitude" in cl["0x090"])
check("no non-B6 COM signal can raise assist-active",
      "B6-sig261-gated at 0xCB73A" in cl["mode_without_b6"])

sup = art["census_supersession"]
check("VAR-065 census framing superseded but headline preserved",
      sup["prior"].startswith("VAR-065 pinned copy-edge census: 19/116")
      and "306 unique snapshot destinations" in sup["finding"]
      and "B6 sig261 (mode) and B6 sig262 (magnitude)" in sup["preserved"])

live = art["live_context"]
check("B6 remains absent in retained drives (re-read, no new I/O)",
      live["b6_frames_in_retained_drives"] == 0 and "no new vehicle I/O" in live["note"])

prior = json.loads(PRIOR.read_text())
check("prior VAR-065 artifact chain for signal243 stays consistent",
      {c["signal"] for c in prior["scalar_command_cone_census"]["chains"]} >= {243, 261, 262})

print(f"\nResults: {passed} passed, {failed} failed")
raise SystemExit(1 if failed else 0)
