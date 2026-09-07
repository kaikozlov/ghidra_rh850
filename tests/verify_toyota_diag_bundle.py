"""Verify the universal clean Toyota diagnostic bundle derived from current GTS+."""
from __future__ import annotations

import hashlib
import json
import os
import sys
import tempfile
import zipfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "tools/techstream"))

import gts_cli

ART = REPO / "data/generated/gtsplus_2026/toyota_diag_bundle_current.zip"

passed = failed = 0


def check(name: str, condition: object) -> None:
    global passed, failed
    ok = bool(condition)
    passed += int(ok)
    failed += int(not ok)
    print(f"[{'PASS' if ok else 'FAIL'}][generated_self_check] {name}")


def main() -> int:
    check("universal Toyota diagnostic bundle exists", ART.is_file())
    if not ART.is_file():
        return 1

    with zipfile.ZipFile(ART) as archive:
        check("bundle ZIP has no corrupt members", archive.testzip() is None)
        names = archive.namelist()
        index = json.loads(archive.read("index.json"))

        check("bundle schema/release and all three regional masters are pinned",
              index["schema"] == "toyota-diagnostics-bundle-v2"
              and index["profile"] == "toyota-current"
              and index["release"] == "2026.03.002.02"
              and set(index["regions"]) == {"NA", "EU", "JP"})
        check("bundle keeps lazy decoded catalogs separate from resolver metadata",
              len(names) == 440 and sum(name.startswith("catalogs/") for name in names) == 439)
        check("universal Toyota bundle does not project a Panda wiring default",
              "default_panda_bus" not in index)
        p5_contract = index["support_contracts"]["p5"]
        p6_contract = index["support_contracts"]["p6"]
        check("P5 and P6 support contracts are independent Toyota families",
              set(index["support_contracts"]) == {"p5", "p6"}
              and p5_contract["did_root"]["request"] == "220101"
              and p6_contract["did_root"]["request"] == "22a100")
        check("ordinary Toyota P5 preserves root IDs and skips Toyota-reserved group queries",
              p5_contract["standard_did"]["root_ids_remain_supported"] is True
              and p5_contract["standard_did"]["selector_excluded"] == ["0xF300", "0xFD00"]
              and p5_contract["standard_did"]["member_offset"] == 1
              and p5_contract["standard_did"]["implementation"]["CreateEnableDataIdList"] == "0x10063890")
        check("P6 DID/RID support hierarchy is byte-exact and independently pinned",
              p6_contract["did_root"]["root_base"] == "0xA100"
              and p6_contract["did_root"]["root_shift"] == 0
              and p6_contract["did_root"]["selector_excluded"] == ["0xA1FD", "0xA1FE"]
              and p6_contract["did_root"]["selector_ids_remain_supported"] is True
              and p6_contract["routine_root"]["root_base"] == "0xD100"
              and p6_contract["routine_root"]["selector_excluded"] == ["0xD1F0", "0xD1FE"]
              and p6_contract["implementation"]["AnalyzeFrameData"] == "0x100678D0"
              and p6_contract["implementation"]["CreateEnableDataIdList"] == "0x100679A0"
              and p6_contract["implementation"]["CreateEnableRIdList"] == "0x10067CF0")

        expected_counts = {
            "NA": (2864, 8372, 2136, 135, 82761, 2402, 1869, 479),
            "EU": (6057, 17656, 2136, 161, 180592, 4621, 938, 554),
            "JP": (1868, 5583, 2136, 143, 61095, 414, 653, 589),
        }
        for region, expected in expected_counts.items():
            counts = index["regions"][region]["counts"]
            actual = tuple(counts[key] for key in (
                "vehicle_count", "install_set_count", "category_count", "catalog_count", "install_row_count",
                "vin_decision_row_count", "vehicle_decision_row_count", "route_count",
            ))
            check(f"{region} universal resolver counts are stable", actual == expected)
            check(f"{region} support-family dispatch covers every Toyota category",
                  counts["support_family_counts"] == {"p3": 1, "p4": 1859, "p5": 172, "p6": 104}
                  and sum(counts["support_family_counts"].values()) == counts["category_count"])
            check(f"{region} P5 family-local support modes remain distinct",
                  counts["support_mode_counts"] == {
                      "p3": 1, "p4": 1859, "p5-hino": 3, "p5-mazda": 11, "p5-standard": 114,
                      "p5-subaru": 24, "p5-suzuki": 20, "p6-standard": 104,
                  })

        for region in ("NA", "EU", "JP"):
            regional = index["regions"][region]
            categories = regional["categories"]
            check(f"{region} resolver keeps every master category independent of catalog availability",
                  len(categories) == 2136)
            check(f"{region} P6 Engine is classified by Toyota plugin dispatch, not projected into P5",
                  categories["6000"]["database"] == "Engine_CM_P6.ddb"
                  and categories["6000"]["support_family"] == "p6"
                  and categories["6000"]["support_mode"] == "p6-standard"
                  and categories["6000"]["catalog_available"] is False)
            check(f"{region} representative current TSS3 categories bind literal ordinary-Toyota P5 mode",
                  all(categories[str(cid)]["support_family"] == "p5"
                      and categories[str(cid)]["support_mode"] == "p5-standard"
                      and categories[str(cid)]["support_plugin_single"]["dll"] == "GetSupportP5_DT.dll"
                      for cid in (372, 397, 405, 435, 498)))
            check(f"{region} P5 shared-plugin partner/Hino modes are not collapsed into ordinary Toyota",
                  categories["722"]["support_mode"] == "p5-subaru"
                  and categories["8500"]["support_mode"] == "p5-suzuki"
                  and categories["851"]["support_mode"] == "p5-mazda"
                  and categories["5033"]["support_mode"] == "p5-hino")
            routes = regional["routes"]
            p5_route = routes["498:18"]
            p6_route = routes["6000:24"]
            check(f"{region} P5 route remains Toyota Phase5 ISO15765 CAN",
                  p5_route["transport_kind"] == "iso15765-phase-family"
                  and p5_route["controller"].startswith("CCommCtrlISO15765")
                  and p5_route["physical_request_address"] == 0x792)
            check(f"{region} P6 phase 0x18 selects Toyota 29-bit ISO15765 normal-fixed",
                  p6_route["transport_kind"] == "iso15765-29bit-normal-fixed"
                  and p6_route["controller"] == "CCommCtrlISO15765_29BitCan"
                  and p6_route["request_address_field"] == 0x00
                  and p6_route["physical_request_address"] == 0x18DA00F1
                  and p6_route["physical_response_address"] == 0x18DAF100
                  and p6_route["functional_request_address"] == 0x18DB33F1)

            dispatch = regional["vehicle_resolver_dispatch"]
            check(f"{region} VIN10 generation dispatch is exact and 5..19 are an unresolved alternate path, not unsupported",
                  dispatch["vin10_generation_low5"] == {
                      "3": "phase3", "4": "phase4", "20": "phase5", "21": "phase5", "22": "phase6",
                  }
                  and dispatch["vin10_rejected_generation_low5"] == list(range(5, 20))
                  and dispatch["roles"]["0x45"]["semantic"] == "legacy_select_vehicle"
                  and dispatch["roles"]["0x45"]["binary_present_in_current_gtsplus"] is False
                  and dispatch["roles"]["0x7D"]["binary_present_in_current_gtsplus"] is True)

            session = regional["session_control"]
            check(f"{region} session metadata has no generation/category permission allowlist",
                  session["kind"] == "toyota-per-category-selector-lifecycle"
                  and "eligible_generation_low5" not in session
                  and "wire_proven_categories" not in session)
            for cid in (372, 397, 405, 435, 498):
                row = session["per_category"][str(cid)]
                if not (row["session_executor_supported"] is True
                        and row["default_session_value"] == 1
                        and row["extended_session_value"] == 3):
                    check(f"{region} TSS3 category-local D1/D2 session executor is recovered", False)
                    break
            else:
                check(f"{region} TSS3 category-local D1/D2 session executor is recovered", True)

        na = index["regions"]["NA"]
        camry = na["vehicles"]["12704"]
        check("Camry HV remains one Toyota DB vehicle, not the bundle profile",
              camry["name"] == "Camry HV"
              and camry["install_set_ids"] == [8119, 8120, 8121, 27706])
        four_runner = na["vehicles"]["12757"]
        check("non-Camry vehicle is represented by the same resolver",
              four_runner["name"] == "4Runner" and bool(four_runner["install_set_ids"]))

        def vehicle_candidates(vehicle: dict[str, object]) -> list[dict[str, object]]:
            rows: list[dict[str, object]] = []
            seen: set[tuple[int, int, str | None]] = set()
            for install_set_id in vehicle["install_set_ids"]:
                for row in na["install_sets"].get(str(install_set_id), []):
                    identity = (int(row["category_id"]), int(row["connection_phase_type"]), row.get("route_key"))
                    if identity not in seen:
                        seen.add(identity)
                        rows.append(row)
            return rows

        camry_candidates = vehicle_candidates(camry)
        four_runner_candidates = vehicle_candidates(four_runner)
        check("Camry resolver preserves all 34 logical candidates and routes",
              len(camry_candidates) == 34
              and all(row.get("route_key") is not None for row in camry_candidates))
        check("4Runner resolves independently to all 35 routes",
              len(four_runner_candidates) == 35
              and all(row.get("route_key") is not None for row in four_runner_candidates))

        p4 = na["vehicle_decision"]["probe_program"]["phase4"]
        p4_programs = list(p4["programs_by_k1"].values())
        check("P4 vehicle decision exports Toyota's complete 0x28..0x39 special-master program",
              bool(p4_programs)
              and all(sorted(step["selector"] for step in program["steps"]) == list(range(0x28, 0x3A))
                      for program in p4_programs))

    actual_sha = hashlib.sha256(ART.read_bytes()).hexdigest()
    with tempfile.TemporaryDirectory() as tmp:
        regenerated_path = Path(tmp) / "toyota_diag_bundle_current.zip"
        gts = gts_cli._resolve_gts_root(os.environ.get("GTSPLUS_ROOT"))
        gts_cli.write_toyota_diag_bundle(gts, regenerated_path)
        regenerated_sha = hashlib.sha256(regenerated_path.read_bytes()).hexdigest()
        check("universal bundle regenerates byte-for-byte deterministically", actual_sha == regenerated_sha)

    print(f"\n{passed} passed, {failed} failed")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
