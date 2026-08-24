#!/usr/bin/env python3
"""Verify the Corolla pre-TSS3 openpilot-to-H/F message migration report."""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
REPORT = REPO / "data/generated/corolla_pre_tss3_opendbc_message_comparison.json"
CONTRACT = REPO / "data/external/opendbc/toyota_corolla_pre_tss3_contract.json"
LOCK = REPO / "external-references.lock.json"
DOC = REPO / "docs/variants/corolla-pre-tss3-openpilot-message-comparison.md"

passed = failed = 0

def check(name: str, condition: object, detail: str = "") -> None:
    global passed, failed
    ok = bool(condition)
    passed += int(ok); failed += int(not ok)
    suffix = f" ({detail})" if detail else ""
    print(f"[{'PASS' if ok else 'FAIL'}][raw_bytes] {name}{suffix}")

print("== generated report reproducibility ==")
report=json.loads(REPORT.read_text())
contract=json.loads(CONTRACT.read_text())
lock=json.loads(LOCK.read_text())
check("comparison schema is v1", report["schema"] == "corolla-pre-tss3-opendbc-message-comparison-v1")
check("Corolla prior-art schema is v1", contract["schema"] == "opendbc-toyota-corolla-pre-tss3-contract-v1")
check("canonical upstream revision matches repository lock", contract["canonical_commit"] == lock["repositories"]["opendbc"]["commit"])
check("current upstream revision was explicitly checked", contract["current_upstream_commit"] == "7343a66d46213d5f73528afc6c6db713ebd88a9d")
with tempfile.TemporaryDirectory(prefix="corolla-pre-tss3-") as td:
    out=Path(td)/"comparison.json"
    proc=subprocess.run([sys.executable,str(REPO/"tools/build_corolla_pre_tss3_message_comparison.py"),"--output",str(out)],cwd=REPO,capture_output=True,text=True)
    check("comparison regenerates successfully", proc.returncode == 0, proc.stderr.strip()[:200])
    if out.exists():
        check("tracked comparison is generator-drift free", json.loads(out.read_text()) == report)

print("\n== exact H/F application identity ==")
fw=report["firmware"]
check("albino image is exact H application", fw["corolla_2023_albino"]["software_id"] == "8965H1202000" and fw["corolla_2023_albino"]["sha256"] == "0b47bdc1217835c839e3543e52eab40eb793650a9c159e46f6a9b365ea41a67f")
check("span image is exact normalized F acquisition", fw["corolla_2025_span"]["software_id"] == "8965F1208000" and fw["corolla_2025_span"]["sha256"] == "fdb35b76891cf84a8b89e0a05c9c7c5cfcd27994cf85ccc01ff32828f53091f6")
app=fw["application_region"]
check("H/F application is byte-identical", app["byte_identical"] and app["start"] == "0x00020000" and app["end_exclusive"] == "0x00100000")
check("H/F application hash is pinned", app["sha256"] == "2ccb79cda1e8689ec91c389d3d7e3921c010ddc9c9d917f23c1705916a0e0d7f")

rx={r["can_id"]:r for r in fw["normal_rx"]["descriptors"]}
tx={r["can_id"]:r for r in fw["tx"]["descriptors"]}
check("normal Rx table is exact 40-row table", fw["normal_rx"]["table_start"] == "0x00021F94" and fw["normal_rx"]["descriptor_count"] == 40)
check("newer EPS still receives 0x025 as 32-byte FD", rx["0x025"]["can_fd"] and rx["0x025"]["length"] == 32)
check("newer EPS still receives 0x0AA as classic 8-byte", not rx["0x0AA"]["can_fd"] and rx["0x0AA"]["length"] == 8)
for cid in ("0x2E4","0x191","0x343","0x412"):
    check(f"newer EPS active Rx has no {cid}", cid not in rx)
check("newer EPS Tx table is exact five-message set", list(tx) == ["0x030","0x351","0x394","0x4A3","0x4C8"])
check("newer EPS transmits FD030", tx["0x030"]["can_fd"] and fw["tx"]["fd030_pdu"]["length"] == 32)
check("newer EPS no longer transmits 0x260/0x262", "0x260" not in tx and "0x262" not in tx)

print("\n== Corolla-specific upstream baseline ==")
profiles=contract["profiles"]
old=profiles["corolla_2017_2019"]
tss2=profiles["corolla_tss2_2020_2022"]
check("both pre-TSS3 Corolla profiles are torque control", old["steer_control"] == tss2["steer_control"] == "torque")
check("neither pre-TSS3 Corolla profile is SecOC", not old["secoc"] and not tss2["secoc"])
check("old Corolla uses 88 EPS scale and TSS2 uses 73", old["eps_scale"] == 88 and tss2["eps_scale"] == 73)
check("TSS2 Corolla camera owns stock longitudinal", "camera" in tss2["stock_longitudinal_source"] and tss2["openpilot_longitudinal"])
old_tx={r["id"]:r for r in old["transmit"]}
tss2_tx={r["id"]:r for r in tss2["transmit"]}
check("both Corolla generations actively command 0x2E4/5", old_tx["0x2E4"]["length"] == tss2_tx["0x2E4"]["length"] == 5 and old_tx["0x2E4"]["cadence_hz"] == tss2_tx["0x2E4"]["cadence_hz"] == 100)
check("only TSS2 Corolla emits 0x191", "0x191" not in old_tx and tss2_tx["0x191"]["cadence_hz"] == 50)
check("TSS2 Corolla 0x191 is explicitly neutral", "neutral" in tss2_tx["0x191"]["role"] and "STEER_REQUEST=false" in tss2_tx["0x191"]["neutral_contract"])
check("old Corolla 0x343 is cancel-only", old_tx["0x343"]["cadence"] == "cancel-event only when stock longitudinal")
check("TSS2 Corolla 0x343 is active longitudinal", abs(tss2_tx["0x343"]["cadence_hz"] - 100/3) < 1e-9 and "active longitudinal" in tss2_tx["0x343"]["role"])
check("both Corolla profiles replace 0x412 HUD", old_tx["0x412"]["cadence_hz"] == tss2_tx["0x412"]["cadence_hz"] == 5)
check("0x131/0x183 are explicitly outside Corolla baseline", {r["id"] for r in contract["explicit_non_corolla_secoc_messages"]} == {"0x131","0x183"})

print("\n== role migration conclusions ==")
roles={r["role"]:r for r in report["message_role_comparison"]}
check("0x025 migration preserves semantic role but changes wire shape", roles["steering_angle_and_rate_input"]["classification"] == "same_id_role_continuity_wire_migrated_to_can_fd")
check("0x0AA continuity is not overclaimed", roles["wheel_speed_input"]["classification"] == "same_id_same_length_configured_continuity_semantics_not_reproved_here")
check("0x260 feedback migration points to FD030", roles["driver_eps_torque_and_accurate_angle_feedback"]["corolla_h_f"]["replacement_candidate"]["id"] == "0x030")
check("0x262 status migration points to FD030", roles["eps_lka_readiness_and_fault_feedback"]["corolla_h_f"]["replacement_candidate"]["id"] == "0x030")
check("old 0x2E4 command is classified removed with no EPS-local setpoint replacement", roles["active_lateral_torque_command"]["classification"] == "old_command_removed_no_eps_local_replacement_setpoint_recovered")
check("TSS2 0x191 disappearance is not treated as lost active actuation", roles["tss2_lta_coexistence_frame"]["classification"] == "old_neutral_tss2_replacement_removed")
check("0x343 absence remains whole-vehicle/non-diagnostic", roles["longitudinal_command_and_stock_source_replacement"]["classification"] == "not_eps_local_absence_non_diagnostic")
check("0x412 absence remains whole-vehicle/non-diagnostic", roles["lkas_hud_and_lane_ui_replacement"]["classification"] == "not_eps_local_absence_non_diagnostic")

print("\n== documentation integration ==")
doc=DOC.read_text()
for token in ("0x2E4", "0x025", "0x0AA", "0x030", "0x260", "0x262", "0x191", "0x343", "0x412", "0x131", "0x183", "byte-identical"):
    check(f"report preserves {token}", token in doc)
findings=(REPO/"docs/status/FINDINGS.md").read_text()
check("COM-008 records the comparison", "| COM-008 |" in findings and "corolla-pre-tss3-openpilot-message-comparison.md" in findings)
priorities=(REPO/"docs/status/PRIORITIES.md").read_text()
check("Corolla command-provenance priority consumes comparison", "corolla-pre-tss3-openpilot-message-comparison.md" in priorities)

print(f"\n== RESULT: {passed} passed, {failed} failed ==")
raise SystemExit(1 if failed else 0)
