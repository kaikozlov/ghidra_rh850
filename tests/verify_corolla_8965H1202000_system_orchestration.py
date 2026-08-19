#!/usr/bin/env python3
"""Verify target-native Corolla 8965H1202000 system/orchestration recovery."""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / "data/generated/corolla_8965H1202000_system_orchestration.json"
EVIDENCE = ROOT / "data/generated/corolla_8965H1202000_system_orchestration_decompiler_evidence.json"
BUILDER = ROOT / "tools/build_corolla_h_system_orchestration.py"
HRAW = ROOT / "community/albinoelephant/raw-20260818/albinoelephant-corolla-2023.20260814-0023/dump_codeflash_00000000_00200000_20260814-025814.bin"

passed = failed = 0

def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def check(name: str, cond: object, detail: str = "") -> None:
    global passed, failed
    ok = bool(cond)
    passed += int(ok); failed += int(not ok)
    suffix = f" ({detail})" if detail else ""
    print(f"[{'PASS' if ok else 'FAIL'}][raw_bytes] {name}{suffix}")

art = json.loads(ART.read_text())
ev = json.loads(EVIDENCE.read_text())
h = HRAW.read_bytes()[:0x100000]

print("== deterministic artifact ==")
with tempfile.TemporaryDirectory() as td:
    out = Path(td) / "orchestration.json"
    cp = subprocess.run([sys.executable, str(BUILDER), "--out", str(out)], cwd=ROOT,
                        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    check("builder exits successfully", cp.returncode == 0, cp.stdout[-600:] if cp.returncode else "")
    check("tracked report regenerates exactly", cp.returncode == 0 and out.read_bytes() == ART.read_bytes())

print("\n== evidence binding ==")
check("H image hash is pinned", sha(h) == ev["image"]["codeflash_sha256"] == art["images"]["corolla_h_sha256"])
check("25 contiguous H functions are compacted", ev["function_count"] == 25 == len(ev["functions"]))
check("all contiguous H body hashes validate",
      all(sha(h[int(r["entry"],16):int(r["entry"],16)+r["body_size"]]) == r["body_sha256"] for r in ev["functions"]))
check("all compacted H decompilation hashes validate",
      all(sha(r["decompiled_c"].encode()) == r["decompiled_c_sha256"] for r in ev["functions"]))
reset = ev["reset_0x1f2"]
check("reset 0x1F2 is explicitly non-contiguous", reset["entry"] == "0x000001F2" and "non-contiguous" in reset["body_boundary"])
check("all reset raw windows validate",
      all(sha(h[int(w["start"],16):int(w["start"],16)+w["size"]]) == w["sha256"] for w in reset["raw_windows"]))

print("\n== scheduler/system closure ==")
closure = art["scheduler_system_closure"]
expected = {
    "0x000001F2":"0x000001F2", "0x00058404":"0x0005389C", "0x00062758":"0x0005CAAC",
    "0x000B0518":"0x000B05D0", "0x000B28AC":"0x000B2692", "0x000BA43A":"0x000B8EE4",
    "0x000BD10E":"0x000BBFE6", "0x000BEC4C":"0x000BD954",
}
check("all eight scheduler/system residual roles are mapped", art["scheduler_system_closure_count"] == 8 and
      {r["reference_entry"]:r["target_entry"] for r in closure} == expected)
by_ref = {r["reference_entry"]:r for r in closure}
check("H periodic generated task remains flat/no-branch", by_ref["0x00058404"]["target_metrics"]["if_count"] == 0 and
      by_ref["0x00058404"]["target_metrics"]["switch_count"] == 0 and
      by_ref["0x00058404"]["target_metrics"]["unique_direct_call_count"] == 333)
check("H one-shot subsystem init remains no-branch", by_ref["0x000BD10E"]["target_metrics"]["if_count"] == 0 and
      by_ref["0x000BD10E"]["target_metrics"]["unique_direct_call_count"] == 94)
check("H telemetry snapshot body is target-native 2654 bytes", by_ref["0x000BA43A"]["target_metrics"]["body_size"] == 2654)
check("H transition phase initializer retains 26-byte/one-call shape", by_ref["0x000B28AC"]["target_metrics"] == {
    "body_size":26,"direct_call_count":1,"unique_direct_call_count":1,"if_count":0,"switch_count":0,"loop_count":0})
markers = by_ref["0x000001F2"]["target_evidence"]["static_markers"]
check("H reset decision retains FCU/marker constants and terminal loop", all(markers.values()))

print("\n== mode coordinator ==")
mode = art["mode_coordinator"]
expected_query = [0,9,5,0,1,9,3,0,1,9,6,12,0,1,9,6,11,7,0,1,9,4,7,2,0,9,10,7,14,15,9,2,7,0,13,8,1,9]
expected_clear = [0,0,1,9,0,1,9,12,0,1,9,6,0,1,9,2,0,9,7,2,15,0,8,1]
check("mode event-query sequence is exactly preserved", mode["query_sequences_identical"] and mode["event_query_sequence"] == expected_query)
check("mode event-clear sequence is exactly preserved", mode["clear_sequences_identical"] and mode["event_clear_sequence"] == expected_clear)
check("mode coordinator keeps 47 branch tests", mode["sienna_metrics"]["if_count"] == mode["h_metrics"]["if_count"] == 47)
check("mode coordinator body size remains near-identical", mode["sienna_metrics"]["body_size"] == 1014 and mode["h_metrics"]["body_size"] == 1016)

print("\n== per-tick wiring delta ==")
tick = art["per_tick_dispatch"]
check("guard denominator is 74 -> 64", tick["sienna_guard_count"] == 74 and tick["h_guard_count"] == 64)
check("guard diff is one contiguous 10-guard deletion", len(tick["guard_diff"]) == 1 and
      tick["guard_diff"][0]["opcode"] == "delete" and len(tick["guard_diff"][0]["sienna_guards"]) == 10 and
      tick["guard_diff"][0]["h_guards"] == [])
check("deleted guard region includes both Sienna 0x520 branches",
      tick["guard_diff"][0]["sienna_guards"].count("if (param_2 == 0x520) {") == 2)
check("H full dispatcher has no 0x520 guard", tick["sienna_has_0x520_guard"] and not tick["h_has_0x520_guard"])
check("deleted block includes known Sienna B763C helper", "FUN_000b763c" in tick["sienna_only_post_coordinator_calls"])
check("H full dispatcher preserves telemetry -> coordinator -> snapshot order",
      tick["h_major_call_order"] == ["FUN_000b8ee4","FUN_000b05d0","FUN_000bba48"] and
      tick["h_major_call_positions"]["FUN_000b8ee4"] <
      tick["h_major_call_positions"]["FUN_000b05d0"] <
      tick["h_major_call_positions"]["FUN_000bba48"])
reduced = art["reduced_per_tick_companion"]
check("H reduced/current-mode dispatcher keeps same major trio", reduced["h_calls"] == ["FUN_000b8ee4","FUN_000b05d0","FUN_000bba48"])
check("reduced dispatcher shrinks 504 -> 460 bytes", reduced["sienna_metrics"]["body_size"] == 504 and reduced["h_metrics"]["body_size"] == 460)

print("\n== startup / wrappers / regenerated copy surface ==")
start = art["startup_and_wrappers"]
check("H startup coordinator enables IRQ", start["startup"]["enables_irq"])
check("H startup coordinator tail is foreground loop call", start["startup"]["last_explicit_fun_call"] == "FUN_0005f30c")
check("subsystem-init veneer targets BBFE6", "FUN_000bbfe6();" in start["subsystem_init_wrapper"]["wrapper_code"])
check("per-tick veneer forwards three args to BD954", "FUN_000bd954(param_1,param_2,param_3);" in start["per_tick_wrapper"]["wrapper_code"])
check("transition phase init writes shifted FEBEB160-162 state", all(x in start["transition_phase_init"]["code"] for x in ("0xfebeb162","0xfebeb160","0xfebeb161")))
rte = art["regenerated_com_rte_surface"]
check("H shared Rx consumer fragment has five recovered generated callers", rte["consumer_fragment_callers_within_evidence"] ==
      ["0x0005389C","0x00058450","0x0005886A","0x000589A8","0x00058B3C"])
check("H RTE copy banks are split across three pinned wrappers", rte["rte_copy_banks"] == [
    {"target":"0x00056970","wrapper":"0x00052E4C"},
    {"target":"0x0005701E","wrapper":"0x00052EEE"},
    {"target":"0x0005722E","wrapper":"0x00052FEC"},
])
check("report preserves non-1:1 COM/RTE boundary", "do not infer canonical one-to-one" in rte["boundary"])
check("static conclusion closes scheduler residue without claiming all COM helpers", art["static_conclusion"]["scheduler_system_residue_closed"] and
      "not every generated COM helper" in art["static_conclusion"]["remaining_boundary"])

print(f"\nResults: {passed} passed, {failed} failed")
raise SystemExit(1 if failed else 0)
