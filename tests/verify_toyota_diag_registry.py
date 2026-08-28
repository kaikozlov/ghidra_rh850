"""Verify the clean derived Toyota diagnostics registry for the maintainer Camry."""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "tools/techstream"))

import gts_cli

ART = REPO / "data/generated/gtsplus_2026/toyota_diag_registry_camry_2026.json"

passed = failed = 0


def check(name: str, condition: object) -> None:
    global passed, failed
    ok = bool(condition)
    passed += int(ok)
    failed += int(not ok)
    print(f"[{'PASS' if ok else 'FAIL'}][generated_self_check] {name}")


def main() -> int:
    check("registry artifact exists", ART.is_file())
    actual = json.loads(ART.read_text())
    gts = gts_cli._resolve_gts_root(os.environ.get("GTSPLUS_ROOT"))
    regenerated = gts_cli.build_toyota_diag_registry(gts)
    check("registry regenerates exactly from current GTS+ and pinned live evidence", actual == regenerated)

    profile = actual["profile"]
    check("schema and exact Camry profile are pinned",
          actual["schema"] == "toyota-diagnostics-registry-v1"
          and profile["profile"] == "camry-2026-f33"
          and profile["panda_bus"] == 0)
    check("exact F33 EPS identity guard is pinned",
          profile["identity_guard"] == {
              "ecu": "eps", "did": 0xF181, "contains_ascii": "8965F3307000",
          })
    check("post-repin DTC sweep retains the exact 17 validated addresses",
          [row["address"] for row in profile["ecus"]] == [
              0x700, 0x701, 0x724, 0x7D2, 0x747, 0x745, 0x707, 0x703, 0x7A1,
              0x7B0, 0x750, 0x7B3, 0x7C4, 0x7D1, 0x7D0, 0x792, 0x7A2,
          ])
    functional = profile["dtc_clear"]["functional_obd"]
    check("functional OBD Mode 04 route matches the live-validated Camry clear",
          functional == {
              "request_id": 0x7DF,
              "mode04_request": "0104000000000000",
              "positive_prefix": "0144",
              "expected_responders": [0x7E8, 0x7EA, 0x7EB, 0x7ED, 0x7EE],
          })
    check("core current P5 catalogs are present",
          profile["catalog_category_ids"] == [372, 395, 397, 398, 405, 435, 450, 498])

    eps_angle = actual["catalogs"]["405"]["dids"]["0x1037"]
    check("EPS steering-angle DID retains exact current scaling",
          len(eps_angle) == 1
          and eps_angle[0]["name"] == "Steering Angle"
          and (eps_angle[0]["bit_start"], eps_angle[0]["bit_end"]) == (0, 15)
          and eps_angle[0]["mul"] == 15
          and eps_angle[0]["signed"] is True
          and eps_angle[0]["unit"] == "deg")

    frc_lta = actual["catalogs"]["498"]["dids"]["0x1601"]
    check("FRC 0x1601 carries the current LTA and Hands-Off state vocabulary",
          [row["name"] for row in frc_lta] == [
              "LTA Switch Condition Flag", "LTA Control Condition",
              "Hands-Off Customize Condition Flag", "Hands-Off Control Condition",
          ]
          and frc_lta[1]["patterns"] == {"0": "LTA Enabled", "1": "LTA Disabled"})

    for category in (397, 435, 450, 498):
        dtc = actual["catalogs"][str(category)]["dtcs"].get("C13187", [])
        check(f"category {category} resolves live U0131-87 as missing EPS message",
              len(dtc) == 1 and dtc[0]["code"] == "U013187" and dtc[0]["failure"] == "Missing Message")

    hv_test = next(row for row in actual["catalogs"]["397"]["active_tests"] if row["id"] == 1)
    check("Hybrid Active Test 1 is a closed plan-only 0x2F executor",
          hv_test["name"] == "Activate the Inverter Water Pump"
          and hv_test["service"] == 0x2F
          and hv_test["did"] == 0x2801
          and hv_test["start_prefix"] == "2f280103"
          and hv_test["stop_prefix"] == "2f280100"
          and hv_test["execution"] == "plan_only")

    frc_test = next(row for row in actual["catalogs"]["498"]["active_tests"] if row["id"] == 0xA429)
    check("FRC LTA Steering Vibration is exact fixed RID 0x1588 plan-only RoutineControl",
          frc_test["name"] == "LTA Steering Vibration"
          and frc_test["routine_id"] == 0x1588
          and frc_test["fixed_request"] is True
          and frc_test["start_static"] == "31011588"
          and frc_test["stop_static"] == "31021588"
          and frc_test["result_static"] == "31031588"
          and frc_test["execution"] == "plan_only")

    active = [row for catalog in actual["catalogs"].values() for row in catalog["active_tests"]]
    check("closed and ambiguous Active Tests are both represented without guessing",
          sum(row["execution"] == "plan_only" for row in active) == 402
          and sum(row["execution"] == "unresolved_static_plan" for row in active) == 26)
    check("registry contains derived metadata only and forbids execution authorization",
          "no Toyota binaries" in actual["boundary"]
          and "Active Tests are static plans only" in actual["boundary"])

    print(f"\n== RESULT: {passed} passed, {failed} failed ==")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
