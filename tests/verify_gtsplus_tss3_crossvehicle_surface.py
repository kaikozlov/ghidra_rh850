#!/usr/bin/env python3
"""Verify the current-GTS+ cross-vehicle TSS3/architecture/topology census artifact."""
from __future__ import annotations

import csv
import json
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "tools/techstream"))

from extract_gtsplus_tss3_crossvehicle_surface import (
    REGIONS,
    SELECTED_CATEGORY_IDS,
    build,
    decode_bus_clusters,
    write_install_set_csv,
    write_topology_csv,
)

ART = REPO / "data/generated/gtsplus_2026/tss3_crossvehicle_surface.json"
INSTALL_CSV = REPO / "data/generated/gtsplus_2026/tss3_crossvehicle_fleet_install_sets.csv"
TOPOLOGY_CSV = REPO / "data/generated/gtsplus_2026/tss3_crossvehicle_canbus_placements.csv"


def check(label: str, condition: bool) -> None:
    if not condition:
        raise AssertionError(label)
    print(f"[OK] {label}")


def csv_rows(path: Path) -> list[list[str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.reader(handle))


def shape_component_buses(shape: dict) -> dict[str, int]:
    return {
        component_hex: bus_index
        for bus_index, components in decode_bus_clusters(shape)
        for component_hex, _ in components
    }


def shape_component_count(shape: dict) -> int:
    return sum(len(components) for _, components in decode_bus_clusters(shape))


def main() -> int:
    stored = json.loads(ART.read_text(encoding="utf-8"))
    current = build()
    check("artifact regenerates byte-semantically from pinned current GTS+", stored == current)
    check(
        "schema/version pinned",
        stored["schema"] == "gtsplus-tss3-crossvehicle-surface-v2" and stored["gtsplus_version"] == "2026.03.002.02",
    )

    fleet = stored["fleet_category_498_architecture"]
    expected = {
        "NA": (256, 51, 5),
        "EU": (460, 93, 9),
        "JP": (213, 70, 9),
    }
    for region, (rows, names, architectures) in expected.items():
        got = fleet[region]
        check(
            f"{region} FRC_P5 fleet breadth",
            (got["frc_p5_install_row_count"], got["frc_p5_model_name_count"], got["architecture_count"])
            == (rows, names, architectures),
        )
        check(
            f"{region} Steering Actuator is minority of FRC_P5 rows",
            got["selected_category_cooccurrence_counts"]["499"] < got["frc_p5_install_row_count"],
        )
        for cid in (427, 428, 429, 431, 432):
            check(
                f"{region} category {cid} is not joined to FRC_P5 by current install sets",
                got["selected_category_cooccurrence_counts"][str(cid)] == 0,
            )

    na_arch = {tuple(row["selected_category_ids"]): row for row in fleet["NA"]["architectures"]}
    check("NA dominant FRC+EMPS+Brake+Booster architecture", na_arch[(405, 435, 466, 498)]["install_row_count"] == 117)
    check("NA FRC+EMPS+Brake architecture", na_arch[(405, 435, 498)]["install_row_count"] == 98)
    check("NA FRC+EMPS architecture", na_arch[(405, 498)]["install_row_count"] == 36)
    check(
        "NA 498+499 cooccurrence is only four MAC rows",
        na_arch[(405, 418, 430, 435, 466, 476, 477, 498, 499)]["install_row_count"] == 4,
    )

    # ── per-model/install-set classification ────────────────────────────────
    expected_rows = {"NA": 256, "EU": 460, "JP": 213}
    for region, count in expected_rows.items():
        rows = fleet[region]["install_rows"]
        check(f"{region} install rows enumerated per model/install set", len(rows) == count)
        check(
            f"{region} every install row carries FRC_P5 498 and a region-local install_set_id",
            all(
                498 in row["selected_category_ids"] and isinstance(row["install_set_id"], int)
                for row in rows
            ),
        )
        check(
            f"{region} install rows are uniquely keyed by (vehicle_id, install_set_id)",
            len({(row["vehicle_id"], row["install_set_id"]) for row in rows}) == len(rows),
        )
    na_labels = {row["architecture_label"]: row["install_row_count"] for row in fleet["NA"]["architectures"]}
    check(
        "NA architecture labels classify the three production clusters",
        (na_labels["EMPS+ABS+BRKBST+FRC"], na_labels["EMPS+ABS+FRC"], na_labels["EMPS+FRC"]) == (117, 98, 36),
    )
    check(
        "NA 498+499 cluster label is the MAC placeholder architecture",
        na_labels["EMPS+LDA+FRCAM+ABS+BRKBST+ADS+ADeU+FRC+EMPS2"] == 4
        and {row["vehicle_name"] for row in fleet["NA"]["install_rows"] if 499 in row["selected_category_ids"]}
        == {"MAC"},
    )

    # ── category identities + families ──────────────────────────────────────
    identities = stored["category_identities"]
    check("selected category identities are identical across regions", identities["identical_across_regions"])
    for region in REGIONS:
        rows = identities["regions"][region]
        check(
            f"{region} identity rows cover the selection with family and address joins",
            sorted(int(cid) for cid in rows) == sorted(SELECTED_CATEGORY_IDS)
            and all(row["family"] for row in rows.values()),
        )
    families = stored["category_families"]
    check(
        "family zero-cooccurrence boundary is exactly the pre-498 P5 PCS set",
        sorted(int(cid) for cid in families["zero_cooccurrence_with_498_all_regions"]) == [427, 428, 429, 431, 432],
    )
    check(
        "legacy P4 EPS co-occurs with 498 only in EU",
        families["region_only_cooccurrence_with_498"]["142"] == {"EU": 3, "JP": 0, "NA": 0},
    )
    check(
        "Electric Parking Brake co-occurs with 498 only in JP",
        families["region_only_cooccurrence_with_498"]["485"] == {"EU": 0, "JP": 2, "NA": 0},
    )
    check(
        "Steering Actuator 499 cooccurrence stays region-local (NA 4 / EU 9 / JP 12)",
        [fleet[r]["selected_category_cooccurrence_counts"]["499"] for r in REGIONS] == [4, 9, 12],
    )

    # ── diagnostic address join ─────────────────────────────────────────────
    addresses = stored["diagnostic_addresses"]["regions"]
    check(
        "v18 ECU_Setting address census sizes",
        [addresses[r]["matched_ecu_count"] for r in REGIONS] == [26, 24, 26],
    )
    for region in REGIONS:
        by_ecu = {row["ecu_no"]: row for row in addresses[region]["rows"]}
        check(
            f"{region} pinned diagnostic request addresses for EPS/skid/FRC",
            (by_ecu[405]["address"], by_ecu[435]["address"], by_ecu[498]["address"]) == ("7A1", "7B0", "792")
            and by_ecu[372]["address"] == "700",
        )
        unaddressed = sorted(
            int(cid) for cid in identities["regions"][region]
            if identities["regions"][region][cid]["diagnostic_request_address"] is None
        )
        check(
            f"{region} only EPS/skid/FRC of the selection carry ECU_Setting addresses",
            unaddressed == sorted(cid for cid in SELECTED_CATEGORY_IDS if cid not in (405, 435, 498)),
        )
        check(
            f"{region} identity rows join the same addresses as the ECU_Setting census",
            all(
                identities["regions"][region][cid]["diagnostic_request_address"]
                == (by_ecu[int(cid)]["address"] if int(cid) in by_ecu else None)
                for cid in identities["regions"][region]
            ),
        )

    # ── CAN Bus Check topology join ─────────────────────────────────────────
    topology = stored["can_bus_check_topology"]
    check(
        "topology section pins the Toyota (non-panda) identity namespace",
        topology["identity_namespace"] == "toyota-gtsplus-can-bus-check"
        and "not comma panda bus numbers" in topology["identity_note"],
    )
    expected_topology = {
        "NA": (256, 251, 122, 114),
        "EU": (460, 454, 391, 356),
        "JP": (213, 207, 108, 107),
    }
    for region, (vehicles, car_rows, groups, shapes) in expected_topology.items():
        got = topology["regions"][region]
        check(
            f"{region} topology join breadth (vehicles/car rows/groups/shapes)",
            (
                got["frc_p5_vehicle_type_count"],
                got["can_bus_car_row_count"],
                got["topology_group_count"],
                got["placement_shape_count"],
            )
            == (vehicles, car_rows, groups, shapes),
        )
        check(
            f"{region} every referenced bus identity carries a Toyota bus name and gateway names",
            all(
                identity["bus_name"] and identity["gateway_names"]
                for identity in got["bus_identities"].values()
            )
            and all(
                component_hex in got["component_domains"]
                for shape in got["placement_shapes"]
                for _, components in decode_bus_clusters(shape)
                for component_hex, _ in components
            ),
        )
        invariants = got["placement_invariants"]
        check(
            f"{region} EPS+Skid colocated and camera separated in every shape carrying both",
            invariants["eps_skid_colocated_same_bus"] == invariants["shapes_with_eps_and_skid"]
            and invariants["camera_on_different_bus_than_eps"] == invariants["shapes_with_eps_and_skid"],
        )
    check(
        "fleet-wide EPS+Skid colocation totals pinned (NA/EU/JP)",
        [topology["regions"][r]["placement_invariants"]["shapes_with_eps_and_skid"] for r in REGIONS]
        == [114, 328, 99],
    )
    na_without = {row["vehicle_name"] for row in topology["regions"]["NA"]["vehicle_types_without_topology_row"]}
    check(
        "NA vehicles without topology rows are exactly the TEST/MAC placeholders",
        na_without == {"TEST", "MAC"} and len(topology["regions"]["NA"]["vehicle_types_without_topology_row"]) == 5,
    )
    check(
        "JP placeholder ZZZ4_P5C also lacks a topology row",
        any(row["vehicle_name"] == "ZZZ4_P5C" for row in topology["regions"]["JP"]["vehicle_types_without_topology_row"]),
    )

    # Camry oracle independently pinned by docs/variants/camry-2026-live-baseline.md
    camry = {
        row["vehicle_type"]: row
        for row in topology["regions"]["NA"]["vehicle_topology"]
        if row["vehicle_type"] in (12704, 12862, 12984)
    }
    check(
        "Camry HV vehicle types joined to one shared CAN topology car row",
        len(camry) == 3
        and all(
            row["vehicle_name"] == "Camry HV"
            and [car["can_bus_car_id"] for car in row["can_bus_car_rows"]] == ["0x00A7D910"]
            for row in camry.values()
        ),
    )
    na_topology = topology["regions"]["NA"]
    group_shape = {
        key: shape["shape_sha256"]
        for shape in na_topology["placement_shapes"]
        for key in shape["topology_group_keys"]
    }
    camry_digest = group_shape[camry[12704]["can_bus_car_rows"][0]["topology_group_keys"][0]]
    camry_shape = next(s for s in na_topology["placement_shapes"] if s["shape_sha256"] == camry_digest)
    component_bus = shape_component_buses(camry_shape)

    def bus_identity(bus_index: int) -> dict:
        return na_topology["bus_identities"][str(bus_index)]

    check(
        "Camry topology places Front Camera Module on Central-Gateway Bus 1",
        na_topology["component_domains"]["0x6D"] == "Front Camera Module"
        and component_bus["0x6D"] == 29
        and bus_identity(29)["bus_name"] == "Bus 1"
        and bus_identity(29)["gateway_names"] == ["Central Gateway"],
    )
    check(
        "Camry topology places Skid Control and EPS together on Central-Gateway Bus 4",
        na_topology["component_domains"]["0x29"] == "Skid Control (ABS/VSC/TRAC)"
        and na_topology["component_domains"]["0x32"] == "Power Steering (EPS)"
        and component_bus["0x29"] == component_bus["0x32"] == 32
        and bus_identity(32)["bus_name"] == "Bus 4"
        and bus_identity(32)["gateway_names"] == ["Central Gateway"],
    )

    # ── region-local install-set namespace proof ────────────────────────────
    collisions = {
        tuple(row["regions"]): row
        for row in stored["region_local_boundaries"]["install_set_id_namespaces"]["collisions"]
    }
    check(
        "NA/JP share install-set ids with different full category sets",
        collisions[("NA", "JP")]["shared_install_set_id_count"] == 91
        and collisions[("NA", "JP")]["different_full_category_set_count"] == 90,
    )
    check(
        "NA/EU and EU/JP 498-carrying install-set id spaces are disjoint",
        collisions[("NA", "EU")]["shared_install_set_id_count"] == 0
        and collisions[("EU", "JP")]["shared_install_set_id_count"] == 0,
    )

    # ── generated CSV surfaces ──────────────────────────────────────────────
    install_csv = csv_rows(INSTALL_CSV)
    check(
        "install-set CSV header and row count match the JSON census",
        install_csv[0]
        == [
            "region",
            "vehicle_id",
            "vehicle_name",
            "install_set_id",
            "install_set_id_hex",
            "architecture_label",
            "selected_category_ids",
        ]
        and len(install_csv) - 1 == sum(expected_rows.values()),
    )
    topology_csv = csv_rows(TOPOLOGY_CSV)
    expected_placement_rows = sum(
        shape_component_count(shape) * len(shape["topology_group_keys"])
        for region in REGIONS
        for shape in topology["regions"][region]["placement_shapes"]
    )
    check(
        "topology CSV row count matches group x placement dedup join",
        len(topology_csv) - 1 == expected_placement_rows,
    )
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        install_tmp = tmp_path / "install.csv"
        topology_tmp = tmp_path / "topology.csv"
        write_install_set_csv(stored, install_tmp)
        write_topology_csv(stored, topology_tmp)
        check(
            "CSVs regenerate byte-identically from the stored artifact",
            install_tmp.read_bytes() == INSTALL_CSV.read_bytes()
            and topology_tmp.read_bytes() == TOPOLOGY_CSV.read_bytes(),
        )

    pcs = stored["pcs_data_viewer"]
    check("PCS Data Viewer version pinned", pcs["version"] == "12.00.005")
    check(
        "PCS Data Viewer has large explicit TSS3 recorder dictionary",
        pcs["tss3_resource_key_counts"]
        == {
            "FFD_TSS3_ID_": 1131,
            "FFD_TSS3_TRIGGER_ID_": 49,
            "IMGFFD_TSS3_ID_": 13,
            "IMGFFD_TSS3_TRIGGER_ID_": 18,
            "INFO_FCMIMGFFD_TSS3_": 14,
            "INFO_TSS3FFD_": 19,
        },
    )
    check("PCS viewer names lateral target report", "get_REPORT_LATERAL_POSITION_FOR_CONTROL_TARGET" in pcs["report_accessors"])
    check("PCS resources name target steering angle", "Advanced Drive Control Target Steering Angle Order Value [rad]" in pcs["english_text_witnesses"])

    tse = stored["tse_converter"]
    check("TSE converter version pinned", tse["version"] == "01.02.002")
    check("TSE converter exposes ring-buffer signal parser", "GetRingBuffData_SignalDataList" in tse["converter_symbols"] and "ParseRingBuffer" in tse["ring_buffer_symbols"])
    check("all three TSE templates retained", len(tse["sources"]["templates"]) == 3)
    check("TSE templates name PCS time-series FFD", "PCS時系列作動時FFD" in tse["template_section_translations"])

    p6 = stored["adcu_p6_successor_surface"]
    check("ADCU_P6 successor identity", p6["category"] == {"category_id": 6037, "database": "ADCU_P6.ddb", "generation": 22, "name": "ADAS Domain Controller", "short_name": ""})
    check("ADCU_P6 monitor/RoB/DDR scale", p6["selected_table_census"]["62"]["record_count"] == 1647 and p6["selected_table_census"]["164"]["record_count"] == 717 and p6["selected_table_census"]["167"]["record_count"] == 1797)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
