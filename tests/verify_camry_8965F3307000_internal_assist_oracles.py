#!/usr/bin/env python3
"""Verify exact-F33 passive RDBI observability for internal baseline-assist state."""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
ART = REPO / "data/generated/camry_8965F3307000_internal_assist_oracles.json"
BUILD = REPO / "tools/build_camry_8965F3307000_internal_assist_oracles.py"
passed = failed = 0


def check(name: str, cond: object) -> None:
    global passed, failed
    ok = bool(cond); passed += int(ok); failed += int(not ok)
    print(f"[{'PASS' if ok else 'FAIL'}][generated_self_check] {name}")

with tempfile.TemporaryDirectory() as td:
    out = Path(td) / "oracles.json"
    p = subprocess.run([sys.executable, str(BUILD), "--out", str(out)], cwd=REPO,
                       capture_output=True, text=True, check=False)
    check("builder exits clean", p.returncode == 0)
    check("artifact regenerates byte-exact", p.returncode == 0 and out.read_bytes() == ART.read_bytes())

art = json.loads(ART.read_text())
check("schema/target exact", art["schema"] == "camry-8965f3307000-internal-assist-oracles-v1"
      and art["target"]["software_id"] == "8965F3307000" and art["target"]["corpus_function_count"] == 6065)
check("exact RDBI table denominator pinned", art["exact_rdbi_table"] == {"offset":"0x2928C", "record_count":241})
sel = art["selector_state_direct_rdbi"]
check("selector cells have no direct exact-F33 RDBI callback", sel["cells"] == {"FEBEC156":[], "FEBEC158":[]}
      and "direct-reference negative" in sel["classification"])
check("selector diagnostic negative denominator is explicit and intersection-free",
      sel["denominator"] == {
          "rdbi_records":241, "unique_callbacks":195, "distinct_direct_ram_read_cells_ge_FEBE0000":136,
          "selector_direct_reader_functions":34, "selector_reader_write_targets_intersecting_rdbi_read_cells":0,
      } and "Pointer/indexed" in sel["classification"])
rows = {r["data_id"]: r for r in art["d0218_term_proxies"]}
check("proxy DID set exact", set(rows) == {"0x1C38","0x1C3E","0x1C4A","0x1C50"})
check("1C3E is exact C5EE scaled/clamped proxy", rows["0x1C3E"]["source_term"] == "FEBEC5EE"
      and rows["0x1C3E"]["scaled_intermediate"] == "FEBEAE12"
      and rows["0x1C3E"]["diagnostic_cell"] == "FEBEE8B6"
      and rows["0x1C3E"]["callback"] == "0x0004EA90")
check("1C38/1C4A/1C50 share exact CB38 proxy cell", all(rows[d]["source_term"] == "FEBECB38"
      and rows[d]["scaled_intermediate"] == "FEBEAE6E" and rows[d]["diagnostic_cell"] == "FEBEE8C2"
      for d in ("0x1C38","0x1C4A","0x1C50")))
check("proxy callbacks preserve common *100/0x80 post-scale", all("* 100) / 0x80" in r["rdbi_transform"] for r in rows.values()))
check("current target-native GTS+ leaves all four proxy DIDs unnamed", set(art["current_gtsplus_boundary"]["unnamed_exact_f33_proxy_dids"]) == {"0x1C38","0x1C3E","0x1C4A","0x1C50"}
      and all(r["current_gtsplus_emps_p5_name"] is None for r in rows.values()))
eff = art["normal_selector_effect_closure"]
check("C28FC healthy selector1 is the sole distinct normal calibration bank",
      eff["base_pointer_table_0xB144C"] == {"AC3C_0_integrity_fallback":"0x18100","AC3C_1_healthy":"0x10100"}
      and eff["healthy_equivalence"] == "selector 0 == selector 2 == selector 3 byte-for-byte; selector 1 differs"
      and eff["healthy_selector0_vs_1_diff_bytes"] == 215)
check("C28FC fallback and C58B8 selector records alias across all selector values",
      len(set(eff["fallback_block_sha256"])) == 1
      and all(len(set(v)) == 1 for v in eff["C58B8_C1A4_C1A6_selector_records"].values()))
check("route-zero sig160 can choose only equivalent normal C2B64 banks",
      "FEBEC156 0 or 2" in eff["zero_sig160_state_reduction"]
      and "normal blocks are identical" in eff["zero_sig160_state_reduction"]
      and "no effective C2B64 calibration effect" in eff["classification"]
      and "0x55/0x11" in eff["remaining_special_modes"])
inf = art["selector_influence_observability"]
check("1C3E C5EE selector indexing aliases away in exact F33 calibration",
      "PTR_DAT_000D39DC[FEBEC156&3]" in inf["FEBEC5EE_via_0x1C3E"]
      and "all four selector entries alias 0xB018A" in inf["FEBEC5EE_via_0x1C3E"]
      and inf["exact_alias_tables"]["C5EE_D39DC"] == ["0xB018A"] * 4)
check("C4C0 selector-indexed maps also alias and have no direct term DID",
      "PTR_LAB_000D3630[FEBEC156&3]" in inf["FEBEC4C0_no_direct_term_did"]
      and inf["exact_alias_tables"]["C4C0_D3630"] == ["0xB1208"] * 4
      and inf["exact_alias_tables"]["C4C0_D3670_family"] == ["0xB1248","0xB121C"] * 4
      and "exact F33 RDBI callback directly reads FEBEC4C0" in inf["FEBEC4C0_no_direct_term_did"])
check("selector-state discriminator remains internal after exact calibration aliasing",
      "selector-state discriminator" in inf["classification"] and "C28FC/C2B64" in inf["classification"])
check("passive oracle ranking favors unresolved CB38 then named final command torque",
      [(x["rank"],x["data_id"]) for x in art["recommended_passive_oracles"]] == [(1,"0x1C38"),(2,"0x1C02"),(3,"0x1C3E")])
check("Toyota-named 1C02 is preserved as the pre-slew diagnostic mirror of a physical-funnel value",
      art["recommended_passive_oracles"][1]["data_id"] == "0x1C02"
      and "verified CC66/CC64 physical actuation funnel" in art["recommended_passive_oracles"][1]["reason"])
terms = art["d0218_term_semantic_closure"]
check("all eight B6-inactive D0218 value terms retain structural provenance classes",
      {r["cell"] for r in terms["terms"]} == {"FEBEC43C","FEBEC4C0","FEBEC3BA","FEBECC2C","FEBEBF3C","FEBECB38","FEBEC5EE","FEBECBE8"}
      and "no term is an independently recovered external lane-target magnitude" in terms["classification"])
obs = art["command_value_torque_observable_branch"]
check("1C02 pre-slew observable branch is pinned separately from the motor-driving sibling",
      obs["FEBECC62_canonical_direct_readers"] == ["0x000C4F04","0x000D0AAE"]
      and obs["FEBE6772_direct_readers"] == ["0x0004E7D6"]
      and obs["mirror_tail"]["FEBE6AF6_direct_readers"] == ["0x000387CE"]
      and obs["mirror_tail"]["FEBE6E22_direct_readers"] == ["0x00059448","0x0005CA3A","0x0005D12C"]
      and "diagnostic/model mirror" in obs["classification"])
funnel = art["physical_actuation_funnel"]
check("physical actuation funnel crosses post-slew CC64 through AC54/EE40C into 6AF4/6E0A",
      "FEBECC62 -> D042C/FEBECC66 -> D047C/FEBECC64" in funnel["chain"]
      and "D0AAE/FEBEAC54 -> BF33E/FEBEE40C" in funnel["chain"]
      and "35C4C/FEBE6AF4 -> 387BA/FEBE6E0A" in funnel["chain"]
      and "38502/FEBE6DEC -> 3835E/FEBE6DC8 + 384D8/FEBE6DD6" in funnel["chain"])
check("physical funnel writer sets remain exact for the command/current cells",
      funnel["writer_sets"]["FEBECC64"] == ["0x000D01B4","0x000D047C"]
      and funnel["writer_sets"]["FEBEAC54"] == ["0x000BF97A","0x000D0AAE"]
      and funnel["writer_sets"]["FEBEE40C"] == ["0x000BF33E","0x000BF97A"]
      and funnel["writer_sets"]["FEBE6AF4"] == ["0x00035C4C","0x00059448"]
      and funnel["writer_sets"]["FEBE6E0A"] == ["0x000387BA","0x00059448"]
      and funnel["writer_sets"]["FEBE6DEC"] == ["0x00038502","0x00059448"]
      and funnel["writer_sets"]["FEBE6DC8"] == ["0x0003835E","0x00059448"]
      and funnel["writer_sets"]["FEBE6DD6"] == ["0x000384D8","0x00059448"])
check("6D84/6D86 are downstream diagnostic mirrors of 6DD6/6DC8, not the upstream command source",
      funnel["downstream_current_diagnostic_mirror"]["cells"] == ["FEBE6D84","FEBE6D86"]
      and funnel["downstream_current_diagnostic_mirror"]["direct_writers"]["FEBE6D84"] == ["0x00037F16","0x00059448"]
      and funnel["downstream_current_diagnostic_mirror"]["direct_writers"]["FEBE6D86"] == ["0x00037F16","0x00059448"]
      and "CC62 is a real pre-slew stage" in funnel["classification"]
      and "remaining stock-LTA contradiction is upstream" in funnel["classification"])
check("production output remains unauthorized", art["production_output_authorized"] is False)
print(f"\nResults: {passed} passed, {failed} failed")
sys.exit(1 if failed else 0)
