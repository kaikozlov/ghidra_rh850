#!/usr/bin/env python3
"""Build the 2023 Corolla FRC/Brake calibration-acquisition correlation.

The public Toyota campaign tables are curated external corroboration.  Package
presence and identity are derived from the pinned local CUW corpus.  The output
intentionally distinguishes a model/year-generation match from an exact vehicle
or ECU identity join.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import struct
import zlib
from pathlib import Path
from typing import Any

from inspect_cuw_legacy import parse_attach_bytes

REPO = Path(__file__).resolve().parents[2]
CAMPAIGNS = REPO / "data/external/toyota_corolla_2023_calibration_campaigns.json"
FRC_CORPUS = REPO / "data/generated/techstream_v18/cuw_frc_corpus.json"
DEFAULT_OUT = REPO / "data/generated/techstream_v18/corolla_2023_calibration_acquisition.json"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def raw_descriptor(path: Path) -> dict[str, dict[str, str]]:
    """Read and CRC-check only the first CUW member (`attach.att`)."""
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
    if len(payload) != payload_len:
        raise ValueError(f"truncated attach payload: {path.name}")
    if zlib.crc32(payload) & 0xFFFFFFFF != payload_crc:
        raise ValueError(f"attach payload CRC drift: {path.name}")
    if name != b"attach.att":
        raise ValueError(f"unexpected first CUW member {name!r}: {path.name}")
    return parse_attach_bytes(payload)


def descriptor_values(desc: dict[str, dict[str, str]]) -> set[str]:
    return {value for section in desc.values() for value in section.values()}


def build() -> dict[str, Any]:
    ext = load(CAMPAIGNS)
    corpus = load(FRC_CORPUS)
    frc_campaign = ext["campaigns"]["23TC01_front_recognition_camera"]
    brake_campaign = ext["campaigns"]["24TC01_brake_epb"]

    transitions = {
        (r["current_calibration_id"], r["new_calibration_id"])
        for r in frc_campaign["published_transitions"]
    }
    local_matches: list[dict[str, Any]] = []
    for pkg in corpus["packages"]:
        d = pkg["descriptor"]
        edge = (d["source_target_calibration_1"], d["new_cid"])
        if edge not in transitions:
            continue
        raw_path = REPO / "REFERENCE/cuw" / pkg["filename"]
        if not raw_path.is_file():
            raise FileNotFoundError(f"required pinned CUW unavailable: {raw_path}")
        if raw_path.stat().st_size != pkg["size"] or sha256_file(raw_path) != pkg["sha256"]:
            raise ValueError(f"raw CUW identity drift: {pkg['filename']}")
        local_matches.append({
            "filename": pkg["filename"],
            "size": pkg["size"],
            "sha256": pkg["sha256"],
            "diag_id": d["diag_id"],
            "contact_type": d["contact_type"],
            "vehicle_name": d["vehicle_name"],
            "vehicle_type": d["vehicle_type"],
            "engine_type": d["engine_type"],
            "model_year": d["model_year"],
            "date_of_issue": d["date_of_issue"],
            "source_calibration_id": d["source_target_calibration_1"],
            "new_calibration_id": d["new_cid"],
            "repro_method": d["repro_method"],
            "required_spec_repro_ver": d["required_spec_repro_ver"],
            "whole_image_sha256": pkg["whole_repro"]["decoded_image_sha256"],
            "whole_image_length": pkg["whole_repro"]["decoded_image_length"],
            "whole_image_entropy_bits_per_byte": pkg["whole_repro"]["decoded_image_entropy_bits"],
            "routine_decoded_sha256": pkg["routine_member"]["decoded_sha256"],
        })
    local_matches.sort(key=lambda r: r["source_calibration_id"])

    if [(r["source_calibration_id"], r["new_calibration_id"]) for r in local_matches] != sorted(transitions):
        raise ValueError("local Corolla FRC package set no longer exactly covers the published 23TC01 Corolla transitions")
    if not all(
        r["diag_id"] == "0792"
        and r["contact_type"] == "P5-Unified"
        and r["vehicle_name"] == "COROLLA Series"
        and r["repro_method"] == "07"
        for r in local_matches
    ):
        raise ValueError("published Corolla FRC transition matched a package outside the expected 0792/P5-Unified/ReproMethod07 family")
    if len({r["whole_image_sha256"] for r in local_matches}) != 1:
        raise ValueError("23TC01 Corolla source packages no longer converge on one target image")

    brake_ids = {
        x
        for r in brake_campaign["published_transitions"]
        for x in (r["current_calibration_id"], r["new_calibration_id"])
    }
    raw_paths = sorted((REPO / "REFERENCE/cuw").glob("*.cuw"), key=lambda path: path.name)
    local_07b0_matches: list[str] = []
    local_brake_cid_matches: list[dict[str, Any]] = []
    for raw_path in raw_paths:
        desc = raw_descriptor(raw_path)
        if desc.get("Node01", {}).get("DiagID") == "07B0":
            local_07b0_matches.append(raw_path.name)
        hits = sorted(brake_ids & descriptor_values(desc))
        if hits:
            local_brake_cid_matches.append({"filename": raw_path.name, "calibration_ids": hits})
    if local_07b0_matches or local_brake_cid_matches:
        raise ValueError("local corpus now contains a Brake acquisition candidate; rerun and promote producer analysis")

    return {
        "schema_version": 1,
        "title": "2023 Corolla FRC/Brake calibration acquisition correlation",
        "sources": {
            str(CAMPAIGNS.relative_to(REPO)): {"sha256": sha256_file(CAMPAIGNS)},
            str(FRC_CORPUS.relative_to(REPO)): {"sha256": sha256_file(FRC_CORPUS)},
        },
        "front_recognition_camera": {
            "campaign": frc_campaign,
            "local_campaign_transition_matches": local_matches,
            "local_match_count": len(local_matches),
            "target_image_shared": True,
            "target_image_sha256": local_matches[0]["whole_image_sha256"],
            "generation_model_match_identified": True,
            "exact_target_vehicle_identity_joined": False,
            "runtime_application_plaintext_available": False,
            "boundary": (
                "T-0058-23 and T-0060-23 are raw-package matches to Toyota's published 23TC01 Corolla "
                "FRC transitions, so a 2023 Corolla P5 FRC update family is already present locally. "
                "This is not a VIN-level join to the albinoelephant or Span cars, and the 85,458,944-byte "
                "target representation remains high-entropy/opaque rather than decoded application code."
            ),
        },
        "brake_epb": {
            "campaign": brake_campaign,
            "target_diag_id": "07B0",
            "local_reference_package_count": len(raw_paths),
            "local_target_diag_id_count": len(local_07b0_matches),
            "local_target_diag_id_matches": local_07b0_matches,
            "published_calibration_ids": sorted(brake_ids),
            "local_published_cid_matches": local_brake_cid_matches,
            "generation_model_acquisition_family_identified": True,
            "exact_target_vehicle_identity_joined": False,
            "package_bytes_available": False,
            "boundary": (
                "24TC01 independently publishes a concrete 2023 Corolla Brake/EPB CID family. No package "
                "descriptor has DiagID 07B0 or any published Brake CID in the pinned 26-CUW local corpus. "
                "The campaign family is therefore an acquisition key set, not proof of the exact target Brake F181."
            ),
        },
        "acquisition_plan": {
            "primary_static_target": "category-435 Brake/EPB DiagID 07B0 application",
            "candidate_new_brake_cid": "F152612A5400",
            "candidate_techinfo_url": brake_campaign["techinfo_acquisition_probe"]["candidate_url"],
            "package_availability_proven": brake_campaign["techinfo_acquisition_probe"]["package_availability_proven"],
            "live_identity_reads": [
                "Brake/EPB physical 0x7B0 DID F181 software-part list",
                "Brake/EPB physical 0x7B0 DID 0x0105 ECU part number",
                "FRC software identity/SWIN sufficient to choose between the local 23TC01 family and any later update family",
            ],
            "what_is_already_owned": (
                "Two raw 0792/P5-Unified CUWs exactly cover Toyota's published 23TC01 Corolla FRC source transitions "
                "to 8646F1204500; another generic 'find a 2023 Corolla FRC CUW' pass is unnecessary."
            ),
            "remaining_code_level_blocker": (
                "Acquire/decode the 07B0 Brake application and either decode the already-owned 0792 FRC target "
                "representation or pair both modules with synchronized stock-LTA traffic."
            ),
        },
        "static_conclusion": {
            "model_year_frc_package_family_already_present": True,
            "model_year_brake_calibration_family_publicly_identified": True,
            "brake_package_present_locally": False,
            "exact_albino_or_span_brake_cid_identified": False,
            "exact_albino_or_span_frc_cid_identified": False,
            "tms051_sender_attribution_retracted": False,
            "priority_refinement": (
                "The next acquisition target is specifically the 07B0 Brake/EPB application or exact live Brake "
                "identity, not an unspecified matched FRC package. The 2023 Corolla 0792 generation package family "
                "is already local but remains encoded."
            ),
        },
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", type=Path, default=DEFAULT_OUT)
    args = ap.parse_args()
    obj = build()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"Wrote {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
