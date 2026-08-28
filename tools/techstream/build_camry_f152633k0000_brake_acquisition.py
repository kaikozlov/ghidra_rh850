#!/usr/bin/env python3
"""Build the exact-Camry Brake/EPB producer acquisition assessment.

This is an integration artifact, not a firmware decoder.  It joins the exact
read-only Camry identity to the raw local CUW descriptor census and the already
verified Toyota/TIS host acquisition contract.  If a matching 07B0 package
appears, generation stops so the package can be decoded and promoted as a real
analysis target instead of silently preserving a stale blocker.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import struct
import subprocess
import sys
import zlib
from collections import Counter
from pathlib import Path
from typing import Any

from techstream_paths import CUW_CORPUS_ROOT

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))

from cuw_attach import parse_attach_bytes  # noqa: E402

LIVE = REPO / "data/generated/camry_2026_nrtd_p5.json"
CORPUS = REPO / "data/generated/techstream_v18/cuw_frc_corpus.json"
SENDER = REPO / "data/generated/techstream_v18/tss3_b6_sender_attribution.json"
CAMPAIGNS = REPO / "data/external/toyota_corolla_2023_calibration_campaigns.json"
DEFAULT_OUT = REPO / "data/generated/gtsplus_2026/camry_f152633k0000_brake_acquisition.json"

EXACT_F181 = "F152633K0000"
EXACT_ECU_PART = "8954147040"
TARGET_DIAG_ID = "07B0"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def raw_descriptor(path: Path) -> dict[str, dict[str, str]]:
    """Read and CRC-check the first CUW member (attach.att) only."""
    with path.open("rb") as f:
        header = f.read(24)
        if len(header) != 24:
            raise ValueError(f"truncated CUW header: {path.name}")
        name_len = struct.unpack_from(">H", header, 22)[0]
        name = f.read(name_len)
        meta = f.read(8)
        if len(name) != name_len or len(meta) != 8:
            raise ValueError(f"truncated first CUW member: {path.name}")
        payload_len, payload_crc = struct.unpack(">II", meta)
        payload = f.read(payload_len)
    if name != b"attach.att" or len(payload) != payload_len:
        raise ValueError(f"invalid first CUW member: {path.name}")
    if zlib.crc32(payload) & 0xFFFFFFFF != payload_crc:
        raise ValueError(f"attach payload CRC drift: {path.name}")
    return parse_attach_bytes(payload)


def all_values(desc: dict[str, dict[str, str]]) -> set[str]:
    return {value for section in desc.values() for value in section.values()}


def gts_json(*args: str) -> Any:
    proc = subprocess.run(
        [str(REPO / "tools/gts"), *args, "--json"],
        cwd=REPO,
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        raise RuntimeError(f"tools/gts {' '.join(args)} failed: {proc.stderr[-500:]}")
    return json.loads(proc.stdout)


def build() -> dict[str, Any]:
    live = load(LIVE)
    corpus = load(CORPUS)
    sender = load(SENDER)
    campaigns = load(CAMPAIGNS)

    brake = live["module_identity"]["Brake_EPB_category_435"]
    expected_brake = {
        "bus": 1,
        "tx": "0x7B0",
        "rx": "0x7B8",
        "f181": EXACT_F181,
        "f18c_serial": "8954147040CFC1800985",
        "ecu_part_0105": EXACT_ECU_PART,
        "bus0_bus2_f181_timeout": True,
    }
    if brake != expected_brake:
        raise ValueError(f"exact Camry Brake identity drift: {brake}")

    raw_paths = sorted(CUW_CORPUS_ROOT.glob("*.cuw"), key=lambda path: path.name)
    if len(raw_paths) != 26:
        raise ValueError(f"expected pinned 26-CUW corpus, found {len(raw_paths)}")

    diag_counts: Counter[str] = Counter()
    exact_value_matches: list[dict[str, Any]] = []
    diag_matches: list[str] = []
    camry_packages: list[dict[str, Any]] = []
    for path in raw_paths:
        desc = raw_descriptor(path)
        node = desc.get("Node01", {})
        vehicle = desc.get("Vehicle", {})
        block = desc.get("LogicalBlock101", {})
        diag_id = node.get("DiagID", "")
        diag_counts[diag_id] += 1
        values = all_values(desc)
        hits = sorted({EXACT_F181, EXACT_ECU_PART} & values)
        if hits:
            exact_value_matches.append({"filename": path.name, "values": hits})
        if diag_id == TARGET_DIAG_ID:
            diag_matches.append(path.name)
        if vehicle.get("VehicleName", "").upper() == "CAMRY":
            camry_packages.append({
                "filename": path.name,
                "sha256": sha256_file(path),
                "size": path.stat().st_size,
                "vehicle_name": vehicle.get("VehicleName", ""),
                "vehicle_type": vehicle.get("VehicleType", ""),
                "model_year": vehicle.get("ModelYear", ""),
                "engine_type": vehicle.get("EngineType", ""),
                "date_of_issue": vehicle.get("DateOfIssue", ""),
                "contact_type": vehicle.get("ContactType", ""),
                "diag_id": diag_id,
                "source_calibration": block.get("01_TargetCalibration", ""),
                "new_cid": block.get("NewCID", ""),
            })

    expected_counts = corpus["reference_inventory"]["diag_id_counts"]
    if dict(sorted(diag_counts.items())) != expected_counts:
        raise ValueError("raw CUW DiagID census drifted from the tracked corpus artifact")
    if diag_matches or exact_value_matches:
        raise ValueError(
            "exact/07B0 producer candidate is now local; decode and register it instead of regenerating this blocker"
        )
    if len(camry_packages) != 1 or camry_packages[0]["filename"] != "T-0051-26.cuw":
        raise ValueError(f"current local Camry package census drift: {camry_packages}")
    if camry_packages[0]["diag_id"] != "0724":
        raise ValueError("the local Camry contrast package is no longer the 0724 Engine/MG package")

    category = gts_json("category", "435")["category"]
    if category != {
        "category_id": 435,
        "database": "ABS_P5.ddb",
        "generation": 20,
        "name": "Brake/EPB",
        "short_name": "",
    }:
        raise ValueError(f"current GTS+ category-435 identity drift: {category}")
    routes = gts_json("route", "P5-Unified", "--limit", "50")
    exact_routes = [route for route in routes if route["contact_type"] == "P5-Unified"]
    if len(exact_routes) != 1:
        raise ValueError(f"current GTS+ P5-Unified route cardinality drift: {len(exact_routes)}")
    route = exact_routes[0]

    related_brake = campaigns["campaigns"]["24TC01_brake_epb"]
    related_cids = sorted({
        cid
        for transition in related_brake["published_transitions"]
        for cid in (transition["current_calibration_id"], transition["new_calibration_id"])
    })
    if EXACT_F181 in related_cids:
        raise ValueError("related Corolla campaign unexpectedly became an exact Camry match")

    axes = {
        "tx_0x0b6_32_descriptor": "blocked_missing_decoded_brake_application",
        "secoc_generation_profile_freshness": "blocked_missing_decoded_brake_application",
        "upstream_frc_inputs": "blocked_missing_decoded_brake_application",
        "enable_arming_conditions": "blocked_missing_decoded_brake_application",
    }

    return {
        "schema": "camry-f152633k0000-brake-acquisition-v1",
        "title": "Exact 2026 Camry Brake/EPB producer acquisition blocker and route",
        "sources": {
            str(path.relative_to(REPO)): {"sha256": sha256_file(path)}
            for path in (LIVE, CORPUS, SENDER, CAMPAIGNS)
        },
        "exact_target": {
            "vehicle": "maintainer 2026 Toyota Camry Hybrid",
            "ecu_domain": "Brake/EPB",
            "category_id": 435,
            "database": category["database"],
            "physical_request": brake["tx"],
            "physical_response": brake["rx"],
            "f181_software_part": brake["f181"],
            "f181_record_count": 1,
            "ecu_part_0105": brake["ecu_part_0105"],
            "f18c_serial": brake["f18c_serial"],
            "identity_source": "tracked read-only NRTD response",
        },
        "local_corpus": {
            "package_count": len(raw_paths),
            "diag_id_counts": dict(sorted(diag_counts.items())),
            "diag_07b0_matches": diag_matches,
            "exact_descriptor_value_matches": exact_value_matches,
            "producer_firmware_available": False,
            "decoded_producer_application_available": False,
            "camry_packages": camry_packages,
            "camry_package_rejection": (
                "T-0051-26 is a validated 2025-26 AXVH85 CAMRY P5-Unified package, but Node01/DiagID=0724 "
                "and its 8A28/8A29/8A2A calibration family identify the Engine/MG package, not Brake/EPB 07B0."
            ),
            "boundary": (
                "This is an exhaustive raw attach.att descriptor census of the pinned local 26-CUW corpus. "
                "It proves local absence only, not absence from Toyota/TIS or from an unretained package."
            ),
        },
        "requested_producer_searches": {
            "status_by_axis": axes,
            "search_performed": False,
            "why": (
                "No decoded category-435 07B0 producer application is available. Searching opaque or unrelated "
                "payloads for executable Tx/SecOC constants would not be firmware evidence."
            ),
            "sender_domain_already_known": sender["static_conclusion"]["architectural_immediate_sender_domain"],
            "ownership_still_unknown": {
                "b6_signing_implementation": True,
                "b6_freshness_generation": True,
                "frc_to_brake_payload_transform": True,
                "enable_arming_logic": True,
            },
        },
        "highest_confidence_acquisition_route": {
            "route_kind": "Toyota/TIS ECU-supply-change search",
            "selection": "category-435 Brake/EPB at physical 0x7B0 for the exact vehicle VIN",
            "search_inputs": {
                "vin": "required at authenticated query time; not stored in this artifact",
                "ecuAssyNo_from_did_0105": EXACT_ECU_PART,
                "baseSwNoLst_from_counted_did_f181": [EXACT_F181],
            },
            "host_dataflow_verification": "TMS-049 / tests/verify_techstream_tis_calibration_acquisition.py",
            "result_selection_verification": "TMS-050 / tests/verify_techstream_tis_calibration_selection.py",
            "server_package_availability_proven": False,
            "calibration_url": None,
            "url_policy": (
                "Do not synthesize /t3Portal/calibration/F152633K0000 or any other URL. The exact F181 is a "
                "search input/current software identity, not a proved downloadable target CID."
            ),
            "accepted_package_checks": [
                "Toyota/TIS result is returned for the exact VIN + ecuAssyNo + baseSwNo query",
                "CUW attach descriptor identifies Node01/DiagID=07B0",
                "container/member CRCs and package provenance are pinned before decoding",
                "decoded representation is executable firmware before Ghidra target registration",
            ],
            "current_gtsplus_writer_route": {
                "contact_type": route["contact_type"],
                "parameter_file": route["parameter_file"],
                "cid_getter": route["cid_getter"],
                "prepare_writer": route["prepare_writer"],
                "flash_writer": route["flash_writer"],
                "can_id_source": route["get_can_id_flash"],
                "boundary": (
                    "P5-Unified is a current host route, not proof that an unavailable exact Brake package uses it; "
                    "the acquired CUW descriptor must select the contact type."
                ),
            },
        },
        "campaign_metadata": {
            "exact_camry_brake_campaign_found_tracked": False,
            "related_only": {
                "campaign": related_brake["campaign"],
                "vehicle": related_brake["applicability"],
                "published_cids": related_cids,
            },
            "boundary": (
                "The tracked 24TC01 Brake campaign is Corolla-only and shares only broad F1526-family vocabulary. "
                "It is not an exact Camry package route and none of its CIDs may be transferred to F152633K0000."
            ),
        },
        "next_step_after_acquisition": {
            "register_only_if_plaintext_runtime_code_is_recovered": True,
            "search_order": [
                "Tx 0x0B6 / DLC 32 descriptor and packer",
                "SecOC authenticator submission, profile/key selector, freshness extraction and commit",
                "upstream FRC/ADS request inputs and byte-level transform",
                "enable, arming, suppression, timeout and recovery gates",
            ],
            "vehicle_io_required": False,
        },
        "static_conclusion": {
            "exact_producer_firmware_locally_available": False,
            "producer_analysis_completed": False,
            "acquisition_blocker_deterministic": True,
            "exact_identity_search_route_identified": True,
            "package_url_identified": False,
            "no_live_vehicle_action_performed": True,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()
    obj = build()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"Wrote {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
