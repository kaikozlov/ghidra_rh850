#!/usr/bin/env python3
"""Verify exact-F33 VAR-084 E1/E2 hidden-ingress residual closure."""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
ART = REPO / "data/generated/camry_8965F3307000_hidden_ingress_residuals.json"
BUILD = REPO / "tools/build_camry_8965F3307000_hidden_ingress_residuals.py"
E1 = REPO / "data/generated/camry_8965F3307000_computed_store_target_census.json"
E2 = REPO / "data/generated/camry_8965F3307000_dmac_destination_computed_store_census.json"
passed = failed = 0


def check(name: str, cond: object) -> None:
    global passed, failed
    ok = bool(cond); passed += int(ok); failed += int(not ok)
    print(f"[{'PASS' if ok else 'FAIL'}][hidden_ingress_residuals] {name}")


with tempfile.TemporaryDirectory() as td:
    out = Path(td) / "hidden.json"
    p = subprocess.run([sys.executable, str(BUILD), "--out", str(out)], cwd=REPO,
                       capture_output=True, text=True, check=False)
    check("builder exits clean", p.returncode == 0)
    check("closure artifact regenerates byte-exact", p.returncode == 0 and out.read_bytes() == ART.read_bytes())

art = json.loads(ART.read_text())
e1 = json.loads(E1.read_text())
e2 = json.loads(E2.read_text())
check("schema and exact target pinned",
      art["schema"] == "camry-8965f3307000-hidden-ingress-residuals-v1"
      and art["target"]["software_id"] == "8965F3307000"
      and art["target"]["corpus_function_count"] == 6065)
check("E1 promoted target-native denominator pinned",
      art["e1_register_arithmetic_store_targets"]["census"] == {
          "candidateFunctions":46,"candidates":100,"functions":6065,"knownRangeStores":5011,"stores":13493,
      }
      and e1["summary"] == art["e1_register_arithmetic_store_targets"]["census"])
check("E1 exact candidate-function denominator pinned",
      art["e1_register_arithmetic_store_targets"]["candidate_function_count"] == 46
      and len(art["e1_register_arithmetic_store_targets"]["candidate_functions"]) == 46)
groups = {x["name"]: x for x in art["e1_register_arithmetic_store_targets"]["closure_groups"]}
check("E1 71F2 arithmetic aliases close by exact lane/index bounds",
      "0..7" in groups["71f2_status_arrays"]["bound"] and "<0x18" in groups["71f2_status_arrays"]["bound"])
check("E1 generated-COM aliases close below steering cells",
      "0xFEBE48xx..0xFEBE4Fxx" in groups["generated_com_bookkeeping"]["bound"]
      and "FEBE3DF8..FEBE3EA0" in groups["generated_com_bookkeeping"]["bound"])
check("E1 XCP/CAN manager aliases close below steering cells",
      "FEBE493E..FEBE503A" in groups["xcp_can_manager_state"]["bound"])
check("E1 diagnostic/event aliases close below steering cells",
      "three node IDs" in groups["diagnostic_event_state"]["bound"]
      and "FEBE5527" in groups["diagnostic_event_state"]["bound"])
check("E1 logical-block aliases have exact three-buffer domain",
      all(x in groups["logical_block_state"]["bound"] for x in ("FEBE5651","FEBE5751","FEBE5851")))
check("E1 five-channel and CBxx aliases are explicitly bounded",
      "0..4" in groups["five_channel_snapshot_state"]["bound"]
      and "<3" in groups["cbxx_diagnostic_state"]["bound"])
check("E1 closes register-arithmetic false-negative class without overclaiming arbitrary pointers",
      art["e1_register_arithmetic_store_targets"]["status"] == "closed_within_known_range_store_arithmetic"
      and "unknown/unbounded pointer" in art["e1_register_arithmetic_store_targets"]["boundary"])

em = art["e2_dmac_destination_reprogramming"]
check("E2 destination-register geometry pinned",
      em["destination_registers"] == {"channel_base":"0xFFFF8400","channel_stride":64,"offsets":["0x04","0x14"],"channels":16})
check("E2 target-native computed STORE denominator pinned",
      em["computed_store_census"] == {"candidateFunctions":3,"candidates":5,"functions":6065,"knownRangeStores":5011,"stores":13493}
      and e2["summary"] == em["computed_store_census"])
check("E2 computed candidates are control-register false positives",
      em["computed_false_positive_functions"] == ["0x000607FE","0x0006080E","0x000609B0"]
      and em["computed_false_positive_offsets_mod_0x40"] == [32,44,56])
check("E2 recovered destination writer sets exact",
      em["direct_writers"] == {
          "destination_0x04":["0x0006082C"],
          "destination_0x14":["0x0006082C","0x00060A6A"],
          "read_only_0x04_accessor":"0x0006091E",
      })
check("E2 sole runtime updater caller set exact",
      em["runtime_updater"] == "0x00060A6A"
      and em["runtime_updater_callers"] == ["0x00060462","0x00060C20","0x00061B90","0x000628B2"])
check("E2 fixed descriptor denominator exact",
      len(em["fixed_descriptor_tables"]) == 7
      and sum(x["count"] for x in em["fixed_descriptor_tables"]) == 22
      and em["destination_field_count"] == 44
      and em["distinct_destination_count"] == 22)
check("E2 fixed and runtime-refreshable destinations never enter LocalRAM",
      em["localram_destination_hits"] == []
      and all(not (0xFEBE0000 <= int(r[k],16) <= 0xFEBFFFFF)
                  for t in em["fixed_descriptor_tables"] for r in t["rows"]
                  for k in ("destination_1","destination_2")))
check("E2 closure remains bounded to recovered application dataflow",
      em["status"] == "closed_within_recovered_application_dataflow"
      and "unknown-pointer" in em["boundary"])
check("combined result leaves stock-LTA authority unresolved upstream",
      "E1 and E2 are closed" in art["combined_classification"]
      and "upstream of CC50/CC62" in art["combined_classification"])
check("production output remains unauthorized", art["production_output_authorized"] is False)
check("all promoted evidence functions are exact body/decompile bound",
      len(art["evidence_functions"]) >= 60
      and all(len(x["body_sha256"]) == 64 and len(x["decompiled_c_sha256"]) == 64 for x in art["evidence_functions"]))

print(f"\nResults: {passed} passed, {failed} failed")
sys.exit(1 if failed else 0)
