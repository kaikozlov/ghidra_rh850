#!/usr/bin/env python3
"""Extract the strongest current GTS+ static TSS3 control-ownership boundaries.

This joins three previously separate surfaces:

* master type-19 bindings prove which ECU category hosts Toyota's current TSS3
  Operation/Image FFD recorder plugins;
* ordinary Data Monitor rows expose the longitudinal request source/sink model
  around FRC_P5 and the brake domain; and
* the pinned distribution/repository specimen census records whether a real
  Toyota-generated TSE/GTSE capture is available for end-to-end validation.

It deliberately does *not* infer the vehicle-network frame, SecOC signer, copy
order, or arbitration executor from diagnostic/recorder hosting.
"""
from __future__ import annotations

import argparse
import json
import struct
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

from ddb_semantics import monitor_rows, records
from extract_gtsplus_p5_adas_p6_migration import rob_data_ids
from ddb_strings import load_string_db
from parse_ddb import DDBParser
from techstream_paths import gts_db_root, resolve_gts_root

REPO = Path(__file__).resolve().parents[2]
DEFAULT_OUT = REPO / "data/generated/gtsplus_2026/tss3_control_ownership_surface.json"
REGIONS = ("NA", "EU", "JP")

TSS3_RECORDER_BINDINGS = (
    (498, 233, "GetTSS3ImageFFDP5_DT.dll"),
    (498, 234, "GetTSS3OperationFFDP5_DT.dll"),
)
FRC_REQUEST_DIDS = (0x1B03, 0x1B04, 0x1B05, 0x1B06, 0x1B07)
BRAKE_TSS_REQUEST_DIDS = (0x10A1, 0x10A2, 0x10A3, 0x10A4)
BRAKE_DID_SERVING_CATEGORIES = {
    435: "ABS_P5.ddb",
    466: "Brk_Bst_P5.ddb",
    485: "EPB_P5.ddb",
    6004: "BSCM_A_P6.ddb",
}
# BSCM_B_P6 is part of the brake domain but does not expose 0x10A1..0x10A4.
BRAKE_DOMAIN_CATEGORIES = tuple(sorted((*BRAKE_DID_SERVING_CATEGORIES, 6005)))

RECORDER_LONGITUDINAL_DIDS = ("5280", "5281", "5284", "57D3", "57DB")
PCS_SEMANTICS = REPO / "data/generated/gtsplus_2026/pcs_data_viewer_tss3_managed_semantics.json"
CROSSVEHICLE = REPO / "data/generated/gtsplus_2026/tss3_crossvehicle_surface.json"
B6_SENDER_ATTRIBUTION = REPO / "data/generated/techstream_v18/tss3_b6_sender_attribution.json"
CAMRY_BRAKE_ACQUISITION = REPO / "data/generated/gtsplus_2026/camry_f152633k0000_brake_acquisition.json"
CAMRY_BRAKE_OBSERVERS = REPO / "data/generated/gtsplus_2026/camry_brake_observer_vocabulary.json"


def _u16(raw: bytes, off: int) -> int:
    return struct.unpack_from("<H", raw, off)[0]


def _u32(raw: bytes, off: int) -> int:
    return struct.unpack_from("<I", raw, off)[0]


def _compact_monitor(row: dict[str, Any]) -> dict[str, Any]:
    signal = row.get("signal_info") or {}
    return {
        "name": row["name"],
        "primary_did": f"0x{int(row['primary_did']):04X}",
        "alternate_did": f"0x{int(row['alternate_did']):04X}" if row["alternate_did"] else None,
        "bit_start": int(row["bit_start"]),
        "bit_end": int(row["bit_end"]),
        "bit_width": int(row["bit_end"] - row["bit_start"] + 1),
        "signed": signal.get("signed"),
        "mul": signal.get("mul"),
        "div": signal.get("div"),
        "offset": signal.get("offset"),
        "decimal_point_count": signal.get("decimal_point_count"),
        "unit": signal.get("unit"),
        "patterns": {str(k): v for k, v in signal.get("pattern_display", {}).items()},
    }


def _db_monitor_rows(parser: DDBParser, root: Path, region: str, database: str) -> list[dict[str, Any]]:
    db_root = gts_db_root(root, region, "Gen")
    db = parser.parse_ecu_db(db_root / database)
    strings = load_string_db(parser, db_root / "M_English.ddb")
    return monitor_rows(db, strings, database, include_signal_info=True)


def _selected_dids(rows: list[dict[str, Any]], dids: tuple[int, ...]) -> dict[str, list[dict[str, Any]]]:
    out = {}
    for did in dids:
        matched = [_compact_monitor(row) for row in rows if int(row["primary_did"]) == did]
        if not matched:
            raise ValueError(f"missing expected DID 0x{did:04X}")
        out[f"0x{did:04X}"] = matched
    return out


def recorder_hosting(parser: DDBParser, root: Path) -> dict[str, Any]:
    per_region = {}
    for region in REGIONS:
        db_root = gts_db_root(root, region, "Gen")
        master = parser.parse_master_db(db_root / "Toyota.ddb")
        strings = load_string_db(parser, db_root / "M_English.ddb")
        categories = {row.category_id: row for row in parser.extract_master_ecu_categories(master.sections[16])}
        bindings = [
            (row.category_id, row.dll_role_id, row.dll_name)
            for row in parser.extract_master_dlls(master.sections[19])
            if "TSS3" in row.dll_name
        ]
        if tuple(bindings) != TSS3_RECORDER_BINDINGS:
            raise ValueError(f"{region} TSS3 recorder bindings changed: {bindings!r}")
        category = categories[498]
        per_region[region] = {
            "category_id": 498,
            "database": category.database_name,
            "generation": category.generation,
            "name": strings.get_string(category.ecu_name_string_index),
            "bindings": [
                {"role": role, "role_hex": f"0x{role:02X}", "dll": dll}
                for _, role, dll in bindings
            ],
        }
    if any(per_region[r] != per_region[REGIONS[0]] for r in REGIONS[1:]):
        raise ValueError("TSS3 recorder host binding differs by region")

    cross = json.loads(CROSSVEHICLE.read_text(encoding="utf-8"))
    addresses = {
        region: cross["category_identities"]["regions"][region]["498"]["diagnostic_request_address"]
        for region in REGIONS
    }
    if set(addresses.values()) != {"792"}:
        raise ValueError(f"unexpected FRC diagnostic address join: {addresses}")
    return {
        "identical_across_regions": True,
        "host": per_region[REGIONS[0]],
        "diagnostic_request_address_by_region": addresses,
        "proof": (
            "Current master CDbDllTable binds both TSS3 Operation/Image FFD plugins only to category 498, "
            "FRC_P5 / Front Recognition Camera 2. Therefore Toyota's current TSS3 recorder is hosted and "
            "served at the FRC diagnostic endpoint; this does not identify the arbitration executor or "
            "vehicle-network transmitter."
        ),
    }


def lateral_ownership_boundary() -> dict[str, Any]:
    prior = json.loads(B6_SENDER_ATTRIBUTION.read_text(encoding="utf-8"))
    immediate = prior["immediate_b6_sender_domain"]
    auth = prior["authenticated_source_family"]
    static = prior["static_conclusion"]
    recipe = prior["sender_recipe_boundary"]
    if not (
        immediate["identified"]
        and immediate["domain"] == "Brake System Control Module"
        and immediate["eps_receive_can_id"] == "0x0B6"
        and immediate["corolla_p5_category"]["category_id"] == 435
        and static["current_corpus_static_search_exhausted"]
    ):
        raise ValueError("tracked B6 sender-attribution boundary changed")
    return {
        "eps_receiver": {
            "can_id": immediate["eps_receive_can_id"],
            "pdu_id": immediate["eps_receive_pdu_id"],
            "monitored_source_domain": immediate["domain"],
            "techstream_dtc": immediate["techstream_dtc"],
        },
        "brake_domain": {
            "category": immediate["corolla_p5_category"],
            "authenticated_source_family_supported": static["authenticated_brake_source_family_supported"],
            "shared_protected_profiles": auth["h_protected_profiles"],
            "icus_slot_selector": auth["shared_icus_slot_selector"],
        },
        "eps_is_not_producer_evidence": {
            "role": "SecOC receiver/verifier for protected B6",
            "verifier_envelope_known": recipe["eps_verifier_envelope_known"],
            "slot4_secret_cpu_visible": auth["slot4_key_value_cpu_visible"],
        },
        "unique_originator_identified": static["unique_upstream_originator_identified"],
        "signing_owner_identified": static["b6_secoc_signing_implementation_owner_identified"],
        "freshness_owner_identified": static["b6_sender_freshness_owner_identified"],
        "frc_to_brake_transform_identified": static["byte_level_frc_to_brake_transform_identified"],
        "static_search_exhausted": static["current_corpus_static_search_exhausted"],
        "interpretation": (
            "Exact EPS firmware/DTC evidence attributes protected B6 to the Brake System Control Module domain and "
            "the EPS is the receiving/verifying endpoint. Current GTS+ separately proves FRC hosts the TSS3 "
            "request/arbitration recorder. Together these exclude EPS as the producer and make Brake the only "
            "positively attributed immediate source domain, but they do not uniquely distinguish FRC-originated "
            "commands forwarded by Brake from Brake-computed commands, nor identify the CMAC/freshness implementation owner."
        ),
        "next_evidence": static["next_evidence"],
    }


def longitudinal_request_surface(parser: DDBParser, root: Path) -> dict[str, Any]:
    # FRC output-side vocabulary is required to be identical across the three regional DDBs.
    frc_regions = {
        region: _selected_dids(_db_monitor_rows(parser, root, region, "FRC_P5.ddb"), FRC_REQUEST_DIDS)
        for region in REGIONS
    }
    if any(frc_regions[r] != frc_regions[REGIONS[0]] for r in REGIONS[1:]):
        raise ValueError("FRC longitudinal request monitor surface differs by region")

    # The generation-20 brake sink is independently region invariant.
    abs_regions = {
        region: _selected_dids(_db_monitor_rows(parser, root, region, "ABS_P5.ddb"), BRAKE_TSS_REQUEST_DIDS)
        for region in REGIONS
    }
    if any(abs_regions[r] != abs_regions[REGIONS[0]] for r in REGIONS[1:]):
        raise ValueError("ABS TSS request monitor surface differs by region")

    # Additional brake-family consumers that carry the same exact ordinary RDBI surface.
    brake_consumers = {}
    for category_id, database in BRAKE_DID_SERVING_CATEGORIES.items():
        rows = _db_monitor_rows(parser, root, "NA" if category_id != 485 else "JP", database)
        brake_consumers[str(category_id)] = {
            "database": database,
            "request_dids": _selected_dids(rows, BRAKE_TSS_REQUEST_DIDS),
        }

    # PCS Data Viewer independently names lower/upper request and arbitration-result records.
    pcs = json.loads(PCS_SEMANTICS.read_text(encoding="utf-8"))
    all_rows = pcs["operation_ffd"]["detail_rows"]
    recorder = {}
    for did in RECORDER_LONGITUDINAL_DIDS:
        rows = [row for row in all_rows if row["DataID"] == did]
        if not rows:
            raise ValueError(f"PCS semantics lost recorder DID {did}")
        recorder[did] = [{
            "name": row["DataName"],
            "byte_position": row["BytePosition"],
            "bit_position": row["BitPosition"],
            "bit_length": row["BitLength"],
            "type": row["Type"],
            "lsb": row["Lsb"],
            "offset": row["Offset"],
            "point": row["Point"],
        } for row in rows]

    return {
        "frc_output_vocabulary": {
            "database": "FRC_P5.ddb",
            "identical_across_regions": True,
            "dids": frc_regions[REGIONS[0]],
            "boundary": (
                "The ordinary FRC Data List exposes only the upper-limit ISA request half. "
                "Lower-limit TSS request fields are present in the PCS recorder and brake receive surface but are "
                "not exposed as FRC_P5 ordinary Data Monitor DIDs."
            ),
        },
        "brake_receive_vocabulary": {
            "abs_identical_across_regions": True,
            "dids": abs_regions[REGIONS[0]],
            "consumers": brake_consumers,
            "meaning": (
                "Toyota labels 0x10A1..0x10A4 as upper/lower acceleration magnitudes and request IDs 'from Toyota "
                "Safety Sense'. They are ordinary read-only Data Monitor observations in the brake domain, not "
                "proof of the underlying vehicle-network frame or authentication owner."
            ),
        },
        "pcs_recorder_vocabulary": recorder,
        "static_join": (
            "FRC_P5 contains the upper-limit requester/acceleration/allocation/permission source vocabulary; "
            "brake-domain ECUs expose upper/lower acceleration and requester IDs explicitly named 'from Toyota "
            "Safety Sense'; and the FRC-hosted PCS recorder contains both request halves plus arbitration-result "
            "longitudinal ID/acceleration. This closes the diagnostic source->brake-sink architecture, but not "
            "copy direction, wire encoding, SecOC ownership, or arbitration execution."
        ),
    }


def fleet_brake_sink_census(parser: DDBParser, root: Path) -> dict[str, Any]:
    out = {}
    serving = set(BRAKE_DID_SERVING_CATEGORIES)
    for region in REGIONS:
        db_root = gts_db_root(root, region, "Gen")
        master = parser.parse_master_db(db_root / "Toyota.ddb")
        strings = load_string_db(parser, db_root / "M_English.ddb")
        vehicle_names = {
            _u32(raw, 0x04): strings.get_string(_u32(raw, 0x00))
            for raw in records(master.sections[43])
        }
        vehicle_sets: dict[int, set[int]] = defaultdict(set)
        for raw in records(master.sections[5]):
            vehicle_sets[_u16(raw, 0x04)].add(_u16(raw, 0x06))
        set_categories: dict[int, set[int]] = defaultdict(set)
        for raw in records(master.sections[44]):
            set_categories[_u16(raw, 0x04)].add(_u16(raw, 0x06))

        frc_rows = []
        for vehicle_id, install_sets in vehicle_sets.items():
            for install_set in install_sets:
                categories = set_categories[install_set]
                if 498 not in categories:
                    continue
                frc_rows.append((vehicle_id, install_set, categories))
        covered = [row for row in frc_rows if row[2] & serving]
        missing = [row for row in frc_rows if not row[2] & serving]
        category_counts = Counter(cid for _, _, cats in frc_rows for cid in cats if cid in serving)
        out[region] = {
            "frc_install_row_count": len(frc_rows),
            "rows_with_tss_request_observable_brake_sink": len(covered),
            "serving_category_counts": {str(cid): category_counts[cid] for cid in sorted(serving)},
            "rows_without_sink": [{
                "vehicle_id": vehicle_id,
                "vehicle_name": vehicle_names.get(vehicle_id),
                "install_set_id": install_set,
                "category_ids": sorted(categories),
            } for vehicle_id, install_set, categories in missing],
        }
    return {
        "did_serving_brake_categories": {str(k): v for k, v in BRAKE_DID_SERVING_CATEGORIES.items()},
        "regions": out,
        "interpretation": (
            "Every EU/JP FRC_P5 install row and every NA row except one explicit TEST placeholder includes at "
            "least one brake ECU whose current DDB exposes 0x10A1..0x10A4. This establishes a fleet-wide "
            "diagnostic observation sink, not guaranteed runtime PID support on every physical vehicle."
        ),
    }


def brake_rob_boundary(parser: DDBParser, root: Path) -> dict[str, Any]:
    db_root = gts_db_root(root, "NA", "Gen")
    strings = load_string_db(parser, db_root / "M_English.ddb")
    databases = {}
    forbidden_terms = (
        "arbitration",
        "toyota safety sense",
        "request acceleration",
        "requesting vertical",
        "lateral control request",
        "tss request",
        "steering assist gain",
        "damping control gain",
    )
    for database in ("FRC_P5.ddb", "ABS_P5.ddb", "Brk_Bst_P5.ddb"):
        db = parser.parse_ecu_db(db_root / database)
        raw_rows = rob_data_ids(db, strings)
        unique: dict[tuple[str, str | None], dict[str, Any]] = {}
        for row in raw_rows:
            key = (row["data_id"], row.get("record_name"))
            unique.setdefault(key, {
                "data_id": row["data_id"],
                "record_name": row.get("record_name"),
                "tables": [],
            })["tables"].append(row["table"])
        rows = sorted(unique.values(), key=lambda row: (row["data_id"], row["record_name"] or ""))
        request_or_arbitration = [
            row for row in rows
            if any(term in (row.get("record_name") or "").casefold() for term in forbidden_terms)
        ]
        pinion = [row for row in rows if "pinion" in (row.get("record_name") or "").casefold()]
        databases[database] = {
            "unique_data_id_count": len(rows),
            "request_or_arbitration_name_hits": request_or_arbitration,
            "pinion_name_hits": pinion,
        }
    if databases["FRC_P5.ddb"]["request_or_arbitration_name_hits"]:
        raise ValueError("ordinary FRC RoB unexpectedly gained a request/arbitration field")
    if databases["ABS_P5.ddb"]["request_or_arbitration_name_hits"]:
        raise ValueError("ordinary ABS RoB unexpectedly gained a request/arbitration field")
    expected_observer = [{
        "data_id": "0x507E",
        "record_name": "ADS Control EPS Pinion Angle2",
        "tables": [90, 151],
    }]
    if databases["ABS_P5.ddb"]["pinion_name_hits"] != expected_observer:
        raise ValueError(f"ABS RoB pinion surface changed: {databases['ABS_P5.ddb']['pinion_name_hits']!r}")
    if databases["Brk_Bst_P5.ddb"]["pinion_name_hits"] != expected_observer:
        raise ValueError("Brake Booster RoB pinion surface changed")
    return {
        "region": "NA",
        "databases": databases,
        "interpretation": (
            "The ordinary P5 FRC/Brake Record-on-Behavior tables contain no named TSS request or arbitration-result "
            "field that resolves the remaining producer/executor question. ABS_P5 and Brk_Bst_P5 do persist one "
            "pinion-named observer, RoB DID 0x507E 'ADS Control EPS Pinion Angle2' (mirrored in tables 90/151), "
            "which corroborates brake-domain observation of steering state but does not name a target/request/winner."
        ),
        "boundary": (
            "This closes the remaining obvious brake-RoB static-table lead. The specialized FRC-hosted PCS "
            "Operation FFD remains the only current P5 host surface here that explicitly names request and arbitration results."
        ),
    }


def ordinary_arbitration_census(parser: DDBParser, root: Path) -> dict[str, Any]:
    db_root = gts_db_root(root, "NA", "Gen")
    master = parser.parse_master_db(db_root / "Toyota.ddb")
    strings = load_string_db(parser, db_root / "M_English.ddb")
    hits = []
    seen_db = set()
    for category in parser.extract_master_ecu_categories(master.sections[16]):
        database = category.database_name
        if not database or database in seen_db or not (db_root / database).is_file():
            continue
        seen_db.add(database)
        try:
            rows = _db_monitor_rows(parser, root, "NA", database)
        except (ValueError, KeyError):
            continue
        for row in rows:
            name = row.get("name") or ""
            folded = name.casefold()
            if "arbitration" not in folded:
                continue
            if not any(token in folded for token in ("lateral", "longitudinal", "acceleration", "pinion", "steer")):
                continue
            hits.append({
                "category_id": category.category_id,
                "generation": category.generation,
                "database": database,
                **_compact_monitor(row),
            })
    generation20 = [row for row in hits if row["generation"] == 20]
    return {
        "region": "NA",
        "control_related_hits": hits,
        "generation20_hit_count": len(generation20),
        "generation20_hits": generation20,
        "boundary": (
            "The current ordinary P5 Data Monitor surface exposes no control-related arbitration-result signal. "
            "P6 arbitration rows are successor terminology only; the P5 winner remains available through the "
            "FRC-hosted PCS recorder rather than an ordinary RDBI oracle."
        ),
    }


def exact_camry_blocker() -> dict[str, Any]:
    acquisition = json.loads(CAMRY_BRAKE_ACQUISITION.read_text(encoding="utf-8"))
    observers = json.loads(CAMRY_BRAKE_OBSERVERS.read_text(encoding="utf-8"))
    target = acquisition["exact_target"]
    local = acquisition["local_corpus"]
    route = acquisition["highest_confidence_acquisition_route"]
    obs = observers["exact_camry_boundary"]
    if not (
        target["f181_software_part"] == "F152633K0000"
        and target["ecu_part_0105"] == "8954147040"
        and target["physical_request"] == "0x7B0"
        and local["producer_firmware_available"] is False
        and local["diag_07b0_matches"] == []
    ):
        raise ValueError("exact Camry Brake acquisition boundary changed")
    return {
        "identity": {
            "vehicle": target["vehicle"],
            "category_id": target["category_id"],
            "request": target["physical_request"],
            "response": target["physical_response"],
            "f181": target["f181_software_part"],
            "ecu_part_0105": target["ecu_part_0105"],
            "f18c_serial": target["f18c_serial"],
        },
        "producer_firmware": {
            "locally_available": local["producer_firmware_available"],
            "local_cuw_count": local["package_count"],
            "diag_07b0_matches": local["diag_07b0_matches"],
            "t2_tis_package_availability_proven": route["server_package_availability_proven"],
            "acquisition_route": route["route_kind"],
            "search_inputs": route["search_inputs"],
            "url_policy": route["url_policy"],
        },
        "already_tested_observers": {
            "did_107e_default": obs["did_107e_default"],
            "did_107e_extended": obs["did_107e_extended"],
            "did_10af_live_support": obs["did_10af_live_support"],
        },
        "new_longitudinal_observers_10a1_10a4_live_support": "not_measured",
        "interpretation": (
            "The exact Camry Brake ECU is identity-bound, but its decoded producer firmware is absent from the "
            "pinned CUW corpus and Toyota/TIS has not returned a package in retained evidence. The older 0x107E "
            "steering observer is already live-rejected in default and extended sessions, so it is not a Camry "
            "runtime oracle. The newly identified 0x10A1..0x10A4 longitudinal TSS receive observers remain the "
            "next read-only live support/correlation probe; static DDB presence alone does not claim they answer."
        ),
    }


def specimen_census(root: Path) -> dict[str, Any]:
    diagnostics = root.parent
    bundled = sorted(
        str(path.relative_to(diagnostics)).replace("\\", "/")
        for path in diagnostics.rglob("*")
        if path.is_file() and path.suffix.casefold() in {".tse", ".gtse"}
    )
    repository_roots = [REPO / name for name in ("REFERENCE", "community", "targets")]
    repo_specimens = sorted(
        str(path.relative_to(REPO)).replace("\\", "/")
        for base in repository_roots if base.exists()
        for path in base.rglob("*")
        if path.is_file() and path.suffix.casefold() in {".tse", ".gtse"}
    )
    return {
        "bundled_toyota_diagnostics_tse_gtse_count": len(bundled),
        "bundled_toyota_diagnostics_tse_gtse_paths": bundled,
        "repository_reference_tse_gtse_count": len(repo_specimens),
        "repository_reference_tse_gtse_paths": repo_specimens,
        "boundary": (
            "The pinned Toyota Diagnostics distribution and tracked REFERENCE/community/targets corpora contain "
            "no real TSE/GTSE specimen. Host traversal is recovered, but end-to-end real-section validation "
            "requires an externally acquired Toyota-generated raw TSE; preserve it before GTSE conversion because "
            "the current converter skip policy omits PCS Operation/Image FFD sections."
        ),
    }


def build() -> dict[str, Any]:
    root = resolve_gts_root()
    parser = DDBParser()
    return {
        "schema": "gtsplus-tss3-control-ownership-surface-v1",
        "title": "Current GTS+ TSS3 recorder hosting and longitudinal request ownership surface",
        "recorder_hosting": recorder_hosting(parser, root),
        "lateral_ownership_boundary": lateral_ownership_boundary(),
        "longitudinal_request_surface": longitudinal_request_surface(parser, root),
        "fleet_brake_sink_census": fleet_brake_sink_census(parser, root),
        "brake_rob_boundary": brake_rob_boundary(parser, root),
        "ordinary_arbitration_census": ordinary_arbitration_census(parser, root),
        "exact_camry_blocker": exact_camry_blocker(),
        "specimen_census": specimen_census(root),
        "remaining_boundary": (
            "Static GTS+ now identifies the TSS3 recorder host (FRC) and the longitudinal diagnostic request "
            "source/sink architecture (FRC/TSS vocabulary observed at the brake domain). It still cannot prove "
            "the vehicle-network command frame, copy/forwarding transform, SecOC signer/freshness owner, or the "
            "ECU/function that executes final arbitration. Those require target firmware or synchronized live "
            "recorder + CAN observations."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()
    payload = build()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"wrote {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
