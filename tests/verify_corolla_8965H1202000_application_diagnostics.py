#!/usr/bin/env python3
"""Verify the target-native 8965H1202000 application diagnostics comparison."""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
ARTIFACT = REPO / "data/generated/corolla_8965H1202000_application_diagnostics_diff.json"
EVIDENCE = REPO / "data/generated/corolla_8965H1202000_application_diagnostic_decompiler_evidence.json"
TOOL = REPO / "tools/compare_variant_application_diagnostics.py"

passed = failed = 0


def check(name: str, cond: object, detail: str = "") -> None:
    global passed, failed
    ok = bool(cond)
    passed += int(ok)
    failed += int(not ok)
    suffix = f" ({detail})" if detail else ""
    print(f"[{'PASS' if ok else 'FAIL'}][raw_bytes] {name}{suffix}")


print("== deterministic application-diagnostics diff ==")
with tempfile.TemporaryDirectory() as td:
    out = Path(td) / "diagnostics.json"
    subprocess.run(
        [sys.executable, str(TOOL), "--out", str(out)],
        cwd=REPO,
        check=True,
        stdout=subprocess.DEVNULL,
    )
    check("tracked diagnostics artifact regenerates exactly", out.read_bytes() == ARTIFACT.read_bytes())

d = json.loads(ARTIFACT.read_text())
e = json.loads(EVIDENCE.read_text())

print("\n== service and RDBI generation ==")
svc = d["application_service_objects"]
check("H 17-SID service table relocates to 0x25B38", svc["corolla_h_base"] == "0x25B38")
check("service-object semantic policy shape is unchanged", svc["semantic_policy_shape_same"])
check("all 17 primary service security counts remain zero", all(row["security_count"] == 0 for row in svc["corolla_h"]))

r = d["readable_dids"]
check("readable DID count shrinks 242 -> 226", (r["sienna_count"], r["corolla_h_count"]) == (242, 226))
check("H DID table is 0x28F34", r["corolla_h_base"] == "0x28F34")
check("exact 16-DID 1CF4..1D03 block is removed",
      r["removed"] == [f"0x{x:04X}" for x in range(0x1CF4, 0x1D04)])
check("H adds no readable DIDs", r["added"] == [])
check("F181 is the only declared-width change and grows 17 -> 33",
      r["declared_length_changes"] == [{"did": "0xF181", "sienna": 17, "corolla_h": 33}])
check("H F181 target-native evidence is the two-record response",
      r["f181"]["corolla_h_declared_length"] == 33 and "two 16-byte software-ID records" in r["f181"]["corolla_h_semantics"])

print("\n== exhaustive H RDBI emitted-write audit ==")
audit = r["corolla_h_rdbi_output_audit"]
check("all 180 unique H RDBI producers are classified", audit["unique_producer_count"] == 180)
check("no non-stub H RDBI producer underwrites", audit["nonstub_underwrite_producer_count"] == 0)
check("no H RDBI producer overruns", audit["overrun_producer_count"] == 0)
check("H has exactly 32 stale-response DIDs", audit["stale_response_did_count"] == 32)
check("all H stale DIDs are explained by exact success stubs",
      all(row["classification"] == "success_stub" for row in audit["producers"] if row["write_relation"] == "underwrite"))
comparison = r["stale_response_comparison"]
check("19 Sienna stale DIDs remain stale on H", len(comparison["shared"]) == 19)
check("29 Sienna stale DIDs are fixed or removed on H", len(comparison["sienna_stale_fixed_or_removed_on_h"]) == 29)
check("13 H stale DIDs are new relative to Sienna", len(comparison["new_h_stale_vs_sienna"]) == 13)

print("\n== RoutineControl configuration and target behavior ==")
rc = d["routine_control"]
check("H keeps the exact 19-RID sequence", len(rc["rid_sequence"]) == 19 and rc["rid_sequence"][0] == "0x1000" and rc["rid_sequence"][-1] == "0x110D")
check("decoded policy/session/control-type/width configuration is identical", rc["decoded_policy_support_and_widths_identical"])
check("H 110A/110C/110D are exact no-op precondition+action pairs",
      rc["corolla_h_noop_precondition_and_action_rids"] == ["0x110A", "0x110C", "0x110D"])
check("H 110B is documented as newly active lifecycle state", "FEBEB32C" in rc["material_semantic_differences"]["0x110B"] and "0x1C" in rc["material_semantic_differences"]["0x110B"])
check("H 1009 action change is pinned", "directly starts" in rc["material_semantic_differences"]["0x1009"])
check("H 1106 lower lifecycle family remains active", "structurally matched" in rc["material_semantic_differences"]["0x1106"])

print("\n== compact target-native evidence binding ==")
check("evidence is bound to H software ID", e["software_id"] == "8965H1202000")
check("evidence selects all 180 RDBI producer functions", e["selection"]["rdbi_producer_count"] == 180)
check("evidence selects all 35 nonzero RoutineControl callbacks", e["selection"]["routine_control_callback_count"] == 35)
check("evidence set stays compact", e["selection"]["function_count"] == 240)

print(f"\nResults: {passed} passed, {failed} failed")
raise SystemExit(1 if failed else 0)
