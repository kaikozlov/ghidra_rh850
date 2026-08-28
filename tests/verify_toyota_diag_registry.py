"""Verify the clean derived Toyota diagnostics registry for the maintainer Camry."""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "tools/techstream"))

import gts_cli
from ddb_semantics import decode_p5_signal, extract_msb0, format_p5_decimal, convert_p5_physical

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
          actual["schema"] == "toyota-diagnostics-registry-v2"
          and profile["profile"] == "camry-2026-f33"
          and profile["panda_bus"] == 0)
    decoder = actual["decoders"]["p5-linear-msb0-v1"]
    check("registry carries the closed current-P5 value decoder contract",
          decoder["payload_origin"] == "UDS DID value bytes (positive SID/DID echo excluded)"
          and decoder["bit_numbering"] == "msb0"
          and decoder["byte_order"] == "big-endian"
          and decoder["integer_formula"] == "trunc_toward_zero(signed_raw * mul / div) + offset"
          and decoder["pattern_lookup"] == "match converted_integer before decimal rendering")
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
          and eps_angle[0]["decoder"] == "p5-linear-msb0-v1"
          and eps_angle[0]["name"] == "Steering Angle"
          and (eps_angle[0]["bit_start"], eps_angle[0]["bit_end"]) == (0, 15)
          and eps_angle[0]["mul"] == 15
          and eps_angle[0]["signed"] is True
          and eps_angle[0]["unit"] == "deg")
    signal_rows = [
        signal
        for catalog in actual["catalogs"].values()
        for signals in catalog["dids"].values()
        for signal in signals
    ]
    check("every shipped current-P5 DID signal explicitly selects the closed decoder",
          signal_rows and all(row["decoder"] == "p5-linear-msb0-v1" for row in signal_rows))
    check("MSB0 extraction crosses bytes exactly",
          extract_msb0(bytes.fromhex("a53c"), 4, 11) == 0x53)
    check("signed conversion truncates division toward zero rather than Python floor",
          convert_p5_physical(0xFF, bit_width=8, signed=True, mul=5, div=2, offset=0) == -2)
    check("decimal presentation retains exact DDB precision",
          format_p5_decimal(-15, 1) == "-1.5" and format_p5_decimal(15, 3) == "0.015")
    eps_decoded = decode_p5_signal(
        bytes.fromhex("0001"),
        bit_start=eps_angle[0]["bit_start"], bit_end=eps_angle[0]["bit_end"],
        mul=eps_angle[0]["mul"], div=eps_angle[0]["div"], offset=eps_angle[0]["offset"],
        signed=eps_angle[0]["signed"], decimal_point_count=eps_angle[0]["decimal_point_count"],
    )
    check("Steering Angle raw 1 deterministically renders as 1.5 deg",
          eps_decoded == {"raw": 1, "converted_integer": 15, "value": "1.5", "pattern": None})

    frc_lta = actual["catalogs"]["498"]["dids"]["0x1601"]
    check("FRC 0x1601 carries the current LTA and Hands-Off state vocabulary",
          [row["name"] for row in frc_lta] == [
              "LTA Switch Condition Flag", "LTA Control Condition",
              "Hands-Off Customize Condition Flag", "Hands-Off Control Condition",
          ]
          and frc_lta[1]["patterns"] == {"0": "LTA Enabled", "1": "LTA Disabled"})
    frc_condition = frc_lta[1]
    frc_decoded = decode_p5_signal(
        bytes.fromhex("00010000"),
        bit_start=frc_condition["bit_start"], bit_end=frc_condition["bit_end"],
        mul=frc_condition["mul"], div=frc_condition["div"], offset=frc_condition["offset"],
        signed=frc_condition["signed"], decimal_point_count=frc_condition["decimal_point_count"],
        patterns={int(key): value for key, value in frc_condition["patterns"].items()},
    )
    check("FRC 0x1601 pattern display matches the converted integer",
          frc_decoded["raw"] == 1 and frc_decoded["converted_integer"] == 1
          and frc_decoded["pattern"] == "LTA Disabled")

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
