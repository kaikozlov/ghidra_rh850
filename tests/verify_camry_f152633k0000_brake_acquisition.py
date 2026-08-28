#!/usr/bin/env python3
"""Verify the exact-Camry Brake/EPB acquisition blocker and route."""
from __future__ import annotations

import importlib.util
import json
import struct
import sys
import zlib
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
ARTIFACT = REPO / "data/generated/gtsplus_2026/camry_f152633k0000_brake_acquisition.json"
BUILDER = REPO / "tools/techstream/build_camry_f152633k0000_brake_acquisition.py"
CUW_ROOT = REPO / "software/Techstream/cuw"
sys.path.insert(0, str(REPO / "tools/techstream"))

from cuw_attach import parse_attach_bytes  # noqa: E402

passed = failed = 0
oracle = "generated_self_check+independent_external_artifact+raw_bytes"


def check(name: str, condition: object, detail: str = "") -> None:
    global passed, failed
    ok = bool(condition)
    passed += int(ok)
    failed += int(not ok)
    print(f"[{'PASS' if ok else 'FAIL'}][{oracle}] {name}" + (f" ({detail})" if detail else ""))


def descriptor(path: Path) -> dict[str, dict[str, str]]:
    with path.open("rb") as f:
        header = f.read(24)
        name_len = struct.unpack_from(">H", header, 22)[0]
        name = f.read(name_len)
        payload_len, payload_crc = struct.unpack(">II", f.read(8))
        payload = f.read(payload_len)
    if name != b"attach.att" or len(payload) != payload_len:
        raise ValueError(f"invalid first member: {path.name}")
    if zlib.crc32(payload) & 0xFFFFFFFF != payload_crc:
        raise ValueError(f"attach CRC drift: {path.name}")
    return parse_attach_bytes(payload)


if not CUW_ROOT.is_dir():
    print("[SKIP] Toyota CUW reference corpus unavailable")
    raise SystemExit(77)

spec = importlib.util.spec_from_file_location("camry_brake_acquisition_builder", BUILDER)
assert spec and spec.loader
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
art = json.loads(ARTIFACT.read_text(encoding="utf-8"))

check("artifact regenerates exactly", art == mod.build())
check("schema exact", art["schema"] == "camry-f152633k0000-brake-acquisition-v1")

target = art["exact_target"]
check(
    "exact Brake identity and physical route",
    target["category_id"] == 435
    and target["database"] == "ABS_P5.ddb"
    and target["physical_request"] == "0x7B0"
    and target["physical_response"] == "0x7B8"
    and target["f181_software_part"] == "F152633K0000"
    and target["f181_record_count"] == 1
    and target["ecu_part_0105"] == "8954147040",
)

raw_paths = sorted(CUW_ROOT.glob("*.cuw"), key=lambda path: path.name)
check("raw local corpus has exactly 26 packages", len(raw_paths) == 26)
diag_counts: Counter[str] = Counter()
diag_matches: list[str] = []
exact_matches: list[str] = []
camry: list[tuple[str, str, str, str]] = []
for path in raw_paths:
    desc = descriptor(path)
    diag = desc.get("Node01", {}).get("DiagID", "")
    diag_counts[diag] += 1
    values = {value for section in desc.values() for value in section.values()}
    if diag == "07B0":
        diag_matches.append(path.name)
    if {"F152633K0000", "8954147040"} & values:
        exact_matches.append(path.name)
    vehicle = desc.get("Vehicle", {})
    if vehicle.get("VehicleName", "").upper() == "CAMRY":
        camry.append((
            path.name,
            diag,
            desc.get("LogicalBlock101", {}).get("01_TargetCalibration", ""),
            desc.get("LogicalBlock101", {}).get("NewCID", ""),
        ))

local = art["local_corpus"]
check("raw DiagID census matches artifact", dict(sorted(diag_counts.items())) == local["diag_id_counts"])
check("no raw descriptor has Brake DiagID 07B0", diag_matches == [] and local["diag_07b0_matches"] == [])
check("no raw descriptor has exact Camry Brake identities", exact_matches == [] and local["exact_descriptor_value_matches"] == [])
check(
    "sole local Camry package is non-Brake 0724 contrast",
    camry == [("T-0051-26.cuw", "0724", "8A2810602000", "8A2810602100")]
    and "Engine/MG" in local["camry_package_rejection"],
)
check(
    "producer runtime bytes are unavailable",
    local["producer_firmware_available"] is False
    and local["decoded_producer_application_available"] is False,
)

requested = art["requested_producer_searches"]
check(
    "all requested producer axes are deterministically blocked",
    requested["search_performed"] is False
    and set(requested["status_by_axis"]) == {
        "tx_0x0b6_32_descriptor",
        "secoc_generation_profile_freshness",
        "upstream_frc_inputs",
        "enable_arming_conditions",
    }
    and set(requested["status_by_axis"].values()) == {"blocked_missing_decoded_brake_application"},
)
check(
    "known sender domain is retained without ownership inflation",
    requested["sender_domain_already_known"] == "Brake System Control Module / Corolla category-435 Brake/EPB family"
    and all(requested["ownership_still_unknown"].values()),
)

route = art["highest_confidence_acquisition_route"]
check(
    "exact TIS search inputs use live F181 and 0105",
    route["search_inputs"]["ecuAssyNo_from_did_0105"] == "8954147040"
    and route["search_inputs"]["baseSwNoLst_from_counted_did_f181"] == ["F152633K0000"]
    and "VIN" in route["selection"],
)
check(
    "no calibration URL or package availability is invented",
    route["server_package_availability_proven"] is False
    and route["calibration_url"] is None
    and "Do not synthesize" in route["url_policy"],
)
writer = route["current_gtsplus_writer_route"]
check(
    "current GTS+ P5-Unified route recorded with package-selection boundary",
    writer["contact_type"] == "P5-Unified"
    and writer["parameter_file"] == "P5-Unified.ini"
    and writer["cid_getter"] == "TCUWCanUnifiedCIDGetter.dll"
    and writer["prepare_writer"] == "TCUWCanUnifiedPrepareWriter.dll"
    and writer["flash_writer"] == "TCUWCanUnifiedFlashWriter.dll"
    and "not proof" in writer["boundary"],
)

campaign = art["campaign_metadata"]
check(
    "tracked Corolla campaign is explicitly not transferred to Camry",
    campaign["exact_camry_brake_campaign_found_tracked"] is False
    and campaign["related_only"]["campaign"] == "24TC01"
    and "Corolla-only" in campaign["boundary"]
    and "F152633K0000" not in campaign["related_only"]["published_cids"],
)
conclusion = art["static_conclusion"]
check(
    "final boundary is acquisition-only and no-live-I/O",
    conclusion == {
        "acquisition_blocker_deterministic": True,
        "exact_identity_search_route_identified": True,
        "exact_producer_firmware_locally_available": False,
        "no_live_vehicle_action_performed": True,
        "package_url_identified": False,
        "producer_analysis_completed": False,
    },
)

print(f"\nRESULT: {passed} passed, {failed} failed")
raise SystemExit(1 if failed else 0)
