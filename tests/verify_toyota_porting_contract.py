#!/usr/bin/env python3
"""Verify the tracked Toyota/openpilot prior-art porting contract.

This is a repository-internal integrity check. External source hashes are checked
against the pinned checkout by verify_external_corroboration.py.
"""
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
CONTRACT = REPO / "data/external/opendbc/toyota_porting_contract.json"
REPORT = REPO / "docs/architecture/toyota-openpilot-porting-contract.md"
LOCK = REPO / "external-references.lock.json"
MATRIX = REPO / "data/toyota_eps_variant_matrix.csv"
FINDINGS = REPO / "docs/status/FINDINGS.md"
PRIORITIES = REPO / "docs/status/PRIORITIES.md"

passed = failed = 0


def check(name: str, condition: object, detail: str = "") -> None:
    global passed, failed
    ok = bool(condition)
    passed += int(ok)
    failed += int(not ok)
    suffix = f" ({detail})" if detail else ""
    print(f"[{'PASS' if ok else 'FAIL'}][documentation_lint] {name}{suffix}")


print("== Toyota/openpilot porting contract ==")
check("machine-readable contract exists", CONTRACT.is_file())
check("canonical report exists", REPORT.is_file())

contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
lock = json.loads(LOCK.read_text(encoding="utf-8"))
report = REPORT.read_text(encoding="utf-8")
findings = FINDINGS.read_text(encoding="utf-8")
priorities = PRIORITIES.read_text(encoding="utf-8")

check("contract schema is v1", contract["schema"] == "opendbc-toyota-porting-contract-v1")
check(
    "contract uses canonical pinned opendbc commit",
    contract["repository"]["commit"] == lock["repositories"]["opendbc"]["commit"],
    contract["repository"]["commit"],
)
check(
    "boundary forbids direct TSS3 wire transfer",
    all(token in contract["boundary"] for token in ("not evidence", "TSS3", "Target firmware")),
)

required_sources = {
    "interface", "carstate", "radar_interface", "carcontroller", "toyotacan", "values", "secoc", "safety",
    "toyota_2017", "toyota_adas_standard", "toyota_nodsu", "toyota_secoc",
}
check("contract pins all implementation layers", required_sources == set(contract["sources"]))
check(
    "all source records are path/hash bound",
    all(v.get("path") and len(v.get("sha256", "")) == 64 for v in contract["sources"].values()),
)

platform = contract["platform_model"]
check("TSS2 platform records TSS2/NO_DSU", platform["tss2"]["flags"] == ["TSS2", "NO_DSU"])
check(
    "SecOC platform is layered on TSS2/NO_DSU",
    platform["secoc_tss2"]["flags"] == ["TSS2", "NO_DSU", "SECOC"],
)
check("RADAR_ACC remains an orthogonal architecture flag", "RADAR_ACC" in platform["orthogonal_flags"])
check("ANGLE_CONTROL remains an orthogonal architecture flag", "ANGLE_CONTROL" in platform["orthogonal_flags"])

identity = contract["platform_identity"]
check("platform identity binds camera/radar/EPS generations", identity["platform_code_ecus"] == ["fwdCamera", "fwdRadar", "eps"])
check("EPS firmware is recorded as a lateral-API discriminator", "lateral API changes" in identity["eps_role"] and "reject" in identity["eps_role"])
radar = contract["radar_generation"]
check("TSS2 and pre-TSS2 radar ranges remain generation-specific", radar["tss2_track_id_ranges"] == ["0x180..0x18F", "0x190..0x19F"] and radar["pre_tss2_track_id_ranges"] == ["0x210..0x21F", "0x220..0x22F"])

roles = contract["control_roles"]
torque = roles["lateral_torque_command"]
angle = roles["lateral_angle_command"]
longitudinal = roles["longitudinal_command"]
feedback = roles["steering_feedback"]
ui = roles["driver_ui"]

check("classic STEERING_LKA is 0x2E4/5", torque["classic"] == {"can_id_hex": "0x2E4", "length": 5, "source": "toyota_adas_standard"})
check("SecOC STEERING_LKA is 0x2E4/8", torque["secoc"] == {"can_id_hex": "0x2E4", "length": 8, "source": "toyota_secoc"})
check("torque command requires request and signed-torque roles", torque["command_signals"][:2] == ["STEER_REQUEST", "STEER_TORQUE_CMD"])
check("LTA primary is 0x191", angle["primary_message"]["can_id_hex"] == "0x191")
check("SecOC LTA companion is 0x131", angle["secoc_companion"]["can_id_hex"] == "0x131")
check("ACC primary is 0x343", longitudinal["primary_message"]["can_id_hex"] == "0x343")
check("SecOC ACC command is 0x183", longitudinal["secoc_command"]["can_id_hex"] == "0x183")
check("longitudinal ownership explicitly distinguishes TSS2 camera and radar", all(x in longitudinal["ownership"] for x in ("TSS2 camera", "RADAR_ACC", "radar")))
check("UI role records LKAS_HUD 0x412", ui["message"]["name"] == "LKAS_HUD" and ui["message"]["can_id_hex"] == "0x412")

feedback_by_name = {m["name"]: m for m in feedback["messages"]}
check("feedback contract includes angle sensor 0x025", feedback_by_name["STEER_ANGLE_SENSOR"]["can_id_hex"] == "0x025")
check("feedback contract includes torque sensor 0x260", feedback_by_name["STEER_TORQUE_SENSOR"]["can_id_hex"] == "0x260")
check("feedback contract includes EPS status 0x262", feedback_by_name["EPS_STATUS"]["can_id_hex"] == "0x262")
check("temporary steering states are pinned", feedback["fault_contract"]["temporary_states"] == [0, 9, 11, 21, 25])
check("permanent steering states are pinned", feedback["fault_contract"]["permanent_states"] == [3, 17])

secoc = contract["secoc_layer"]
check("SecOC has three independent semantic outputs", secoc["authenticated_outputs"] == ["STEERING_LKA", "STEERING_LTA_2", "ACC_CONTROL_2"])
check("SecOC synchronization remains 0x00F", secoc["sync_can_id_hex"] == "0x00F")
check("SecOC authenticator is 28 bits", secoc["authenticator_bits"] == 28)

history = {row["commit"]: row for row in contract["history"]}
for commit in ("e1ce3619", "fb4ac268", "0ebc4cb4", "4d93a559", "5e71fde2", "e76c2cf5"):
    check(f"history contains {commit}", commit in history)

limits = contract["actuation_and_safety_contract"]
check("older steer max is preserved as prior art", limits["steer_max"] == 1500)
check("older high-rate threshold is preserved as prior art", limits["max_steer_rate_deg_s"] == 100)
check("limits explicitly forbid blind transplant", "not values to transplant" in limits["note"])
check("pinned SecOC LTA2 actuation is safety-blocked", "rejects any STEERING_LTA_2 actuation" in limits["secoc_lta2_actuation_policy"])

with MATRIX.open(newline="", encoding="utf-8") as fh:
    rows = list(csv.DictReader(fh))
corolla_h = next(r for r in rows if r["application_software_id"] == "8965H1202000")
check("tracked Corolla H remains a direct old-steering-ID counterexample", "no 0x2E4/0x131" in corolla_h["secured_can_ids"])
check("variant matrix separates ADAS and security axes", all(k in corolla_h for k in ("adas_generation", "security_architecture")) and "SecOC/TSK" in corolla_h["security_architecture"])
check("report explicitly separates TSS generation from SecOC/TSK", all(x in report for x in ("Two orthogonal axes", "TSS generation", "SecOC/TSK")))

for token in (
    "control contract",
    "FRC_P5",
    "0x18A",
    "64-byte CAN-FD",
    "stock producer safely suppressed",
    "When the target command is SecOC-protected, SecOC makes that command deliverable",
):
    check(f"report preserves roadmap token {token}", token in report)

check("ARCH-016 points at the contract report", "| ARCH-016 |" in findings and "toyota-openpilot-porting-contract.md" in findings)
open_questions = (REPO / "docs/status/OPEN_QUESTIONS.md").read_text(encoding="utf-8")
check("TSS3 longitudinal ownership is independently tracked", "OQ-052" in open_questions and "True-TSS3 longitudinal producer/control contract" in open_questions)
check("priority queue links the porting contract", "toyota-openpilot-porting-contract.md" in priorities)
check("priority queue preserves separate longitudinal work", "OQ-052" in priorities)

print(f"\n== RESULT: {passed} passed, {failed} failed ==")
raise SystemExit(1 if failed else 0)
