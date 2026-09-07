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
              index["schema"] == "toyota-diagnostics-bundle-v1"
              and index["profile"] == "toyota-current"
              and index["release"] == "2026.03.002.02"
              and set(index["regions"]) == {"NA", "EU", "JP"})
        check("bundle contains one index plus 439 lazy current-P5 category catalogs",
              len(names) == 440 and sum(name.startswith("catalogs/") for name in names) == 439)

        expected_counts = {
            "NA": (2864, 135, 179, 133),
            "EU": (6057, 161, 179, 150),
            "JP": (1868, 143, 179, 143),
        }
        for region, expected in expected_counts.items():
            counts = index["regions"][region]["counts"]
            actual = (
                counts["vehicle_count"], counts["supported_p5_category_count"],
                counts["p5_plugin_category_count"], counts["route_count"],
            )
            check(f"{region} universal vehicle/P5/route counts are stable", actual == expected)

        for region in ("NA", "EU", "JP"):
            categories = index["regions"][region]["categories"]
            check(f"{region} P6 Engine is not projected into the P5 runtime family",
                  categories["6000"]["database"] == "Engine_CM_P6.ddb"
                  and categories["6000"]["current_p5_supported"] is False
                  and "catalog_member" not in categories["6000"])
            for category_id in index["regions"][region]["supported_p5_category_ids"]:
                catalog = json.loads(archive.read(f"catalogs/{region}/{category_id}.json"))
                plugins = {row["dll"] for row in catalog["plugins"]}
                if "GetSupportP5_DT.dll" not in plugins:
                    check(f"{region} category {category_id} is backed by Toyota GetSupportP5_DT", False)
                    break
            else:
                check(f"{region} every shipped P5 catalog is backed by Toyota GetSupportP5_DT", True)

        na_session = index["regions"]["NA"]["session_control"]["per_category"]
        eu_session = index["regions"]["EU"]["session_control"]["per_category"]
        jp_session = index["regions"]["JP"]["session_control"]["per_category"]
        check("current P5 lifecycle keeps Toyota's category-local F186 session-poll family",
              na_session["372"]["keepalive"]["request"] == "22f186"
              and eu_session["372"]["keepalive"]["request"] == "22f186"
              and jp_session["372"]["keepalive"]["request"] == "22f186")
        check("Mitsubishi-family P5 categories use their recovered D100 DID poll rather than Camry F186",
              na_session["851"]["keepalive"] == {
                  "kind": "did_poll", "did": "0xD100", "request": "22d100",
                  "positive_prefix": "62d100", "interval_s": 2.0,
              }
              and eu_session["851"]["keepalive"]["request"] == "22d100")
        check("EU/JP preserve the category-local 1003 extended-session refresh family",
              eu_session["471"]["keepalive"] == {
                  "kind": "extended_session_refresh", "request": "1003", "interval_s": 2.0,
              }
              and jp_session["471"]["keepalive"]["request"] == "1003")

        na = index["regions"]["NA"]
        check("current P5 session generation dispatch is Phase5-only",
              index["p5_session_generation_low5"] == [20, 21])
        check("class-0x10D stores legislated physical request IDs",
              na["routes"]["372:18"]["legislated_request_address"] == 0x7E0
              and "legislated_response_address" not in na["routes"]["372:18"])
        camry = na["vehicles"]["12704"]
        check("Camry HV remains one Toyota DB vehicle, not the bundle profile",
              camry["name"] == "Camry HV"
              and camry["install_set_ids"] == [8119, 8120, 8121, 27706])
        four_runner = na["vehicles"]["12757"]
        check("non-Camry current-P5 vehicle is represented by the same resolver",
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
        check("Camry resolver has 34 logical candidates with 33 implemented P5 routes",
              len(camry_candidates) == 34
              and sum(row.get("route_key") is not None for row in camry_candidates) == 33)
        check("4Runner resolves independently to 35 implemented P5 routes",
              len(four_runner_candidates) == 35
              and all(row.get("route_key") is not None for row in four_runner_candidates))

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
