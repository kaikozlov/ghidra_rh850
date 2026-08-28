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
check("final Toyota-named command torque remains recommended context",
      art["recommended_passive_oracles"][1]["data_id"] == "0x1C02"
      and "Toyota-named final Command Value Torque" in art["recommended_passive_oracles"][1]["reason"])
check("production output remains unauthorized", art["production_output_authorized"] is False)
print(f"\nResults: {passed} passed, {failed} failed")
sys.exit(1 if failed else 0)
