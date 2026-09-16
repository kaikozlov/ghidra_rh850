#!/usr/bin/env python3
"""Recover the exact-Camry meaning and topology role of Toyota's ``EBU`` token.

The evidence is deliberately split into what current GTS+ says literally and what
can only be inferred.  In particular, ``EBU`` is a junction/attachment label in
the CAN Bus Check topology; it is not promoted into an installed ECU component.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import struct
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "tools/techstream"))

from ddb_semantics import extract_monitor_records, records
from ddb_strings import load_string_db
from parse_ddb import DDBParser
from techstream_paths import GTSPLUS_EXTERNAL_ROOT, resolve_gts_root

DEFAULT_OUT = ROOT / "data/generated/camry_2026_ebu_topology.json"
CAMRY_VEHICLE_TYPES = (12704, 12862, 12984)
CAMRY_CAN_BUS_CAR_ID = 0x00A7D910


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def u16(data: bytes, off: int) -> int:
    return struct.unpack_from("<H", data, off)[0]


def u32(data: bytes, off: int) -> int:
    return struct.unpack_from("<I", data, off)[0]


def need(ok: object, msg: str) -> None:
    if not ok:
        raise RuntimeError(msg)


def monitor_names(parser: DDBParser, db_path: Path, strings) -> list[dict[str, Any]]:
    db = parser.parse_ecu_db(db_path)
    out = []
    for rec in extract_monitor_records(db.sections[62]):
        name = strings.get_string(rec.name_string_index) or ""
        if "EBU node" not in name:
            continue
        out.append({
            "name": name,
            "primary_did": f"0x{rec.primary_did:04X}",
            "alternate_did": f"0x{rec.alternate_did:04X}" if rec.alternate_did else "0x0000",
            "bit_range": [rec.bit_start, rec.bit_end],
        })
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--gtsplus-root", type=Path, default=resolve_gts_root(GTSPLUS_EXTERNAL_ROOT))
    ap.add_argument("--output", type=Path, default=DEFAULT_OUT)
    ap.add_argument("--check", action="store_true")
    ns = ap.parse_args()

    gts = resolve_gts_root(ns.gtsplus_root)
    dbroot = gts / "NA/DB/Gen"
    sources = {
        "master": dbroot / "Toyota.ddb",
        "strings": dbroot / "M_English.ddb",
        "abs_p5": dbroot / "ABS_P5.ddb",
        "brake_booster_p5": dbroot / "Brk_Bst_P5.ddb",
        "epb_p5": dbroot / "EPB_P5.ddb",
        "bscm_a_p6": dbroot / "BSCM_A_P6.ddb",
        "bscm_b_p6": dbroot / "BSCM_B_P6.ddb",
    }
    for key, path in sources.items():
        need(path.is_file(), f"missing {key}: {path}")

    parser = DDBParser()
    master = parser.parse_master_db(sources["master"])
    strings = load_string_db(parser, sources["strings"])

    # Vehicle name and exact Camry topology denominator.
    vehicle_names = {u32(raw, 4): strings.get_string(u32(raw, 0)) for raw in records(master.sections[43])}
    car_rows = [raw for raw in records(master.sections[75]) if u32(raw, 4) in CAMRY_VEHICLE_TYPES]
    need(len(car_rows) == 3, f"Camry CanBusCarId row count drift: {len(car_rows)}")
    need({u32(raw, 0) for raw in car_rows} == {CAMRY_CAN_BUS_CAR_ID}, "Camry topology key drift")
    need({u32(raw, 4) for raw in car_rows} == set(CAMRY_VEHICLE_TYPES), "Camry vehicle-type drift")

    option_rows = [raw for raw in records(master.sections[77]) if u32(raw, 0) == CAMRY_CAN_BUS_CAR_ID]
    need(len(option_rows) == 18, f"Camry option count drift: {len(option_rows)}")
    option_groups = [u32(raw, 44) for raw in option_rows]
    need(len(set(option_groups)) == 18, "Camry component-set keys no longer unique")

    subbus_names = {u32(raw, 0): strings.get_string(u32(raw, 4)) or "" for raw in records(master.sections[76])}
    bus_names = {u32(raw, 8): strings.get_string(u32(raw, 4)) or "" for raw in records(master.sections[79])}
    gateways: dict[int, set[str]] = defaultdict(set)
    for raw in records(master.sections[55]):
        value = strings.get_string(u32(raw, 4)) or ""
        if value:
            gateways[u16(raw, 8)].add(value)

    by_group: dict[int, list[bytes]] = defaultdict(list)
    for raw in records(master.sections[78]):
        by_group[u32(raw, 0)].append(raw)

    variants: list[list[dict[str, Any]]] = []
    for group in option_groups:
        rows = by_group[group]
        need(len(rows) == 31, f"Camry component-set 0x{group:08X} count drift: {len(rows)}")
        placement = []
        for raw in sorted(rows, key=lambda r: (u16(r, 8), r[14])):
            component = raw[14]
            bus_index = u16(raw, 8)
            placement.append({
                "component_index": f"0x{component:02X}",
                "ecu_domain": subbus_names.get(component + 1, ""),
                "bus_index": bus_index,
                "bus_name": bus_names.get(bus_index, ""),
                "gateway_names": sorted(gateways.get(bus_index, set())),
                # This is literally the string-valued +4 field in
                # CDbCanBusComponentTable.  Keep the neutral name used by the
                # recovered API rather than treating it as another ECU.
                "junction_name": strings.get_string(u32(raw, 4)) or "",
                "raw_hex": raw.hex(),
            })
        variants.append(placement)
    # Option variants change a few physical junction labels (radar/FCM/body), but
    # not logical component-to-bus membership.  Preserve both denominators: one
    # logical network shape and the exact junction-label variation.
    membership_shapes = {
        tuple((r["component_index"], r["ecu_domain"], r["bus_index"], r["bus_name"]) for r in v)
        for v in variants
    }
    junction_shapes = {
        tuple((r["component_index"], r["bus_index"], r["junction_name"]) for r in v)
        for v in variants
    }
    need(len(membership_shapes) == 1, "Camry logical component-to-bus topology differs across option variants")

    # The brake/EPS attachment facts relevant here are invariant in all 18 options.
    critical_by_variant = []
    for v in variants:
        critical = {r["component_index"]: r for r in v if r["component_index"] in {"0x28", "0x29", "0x32"}}
        need(set(critical) == {"0x28", "0x29", "0x32"}, f"critical Bus-4 component drift: {critical}")
        critical_by_variant.append({k: critical[k]["junction_name"] for k in sorted(critical)})
    need(all(row == {
        "0x28": "No. 2 Global CAN Junction Connector",
        "0x29": "No. 2 Global CAN Junction Connector",
        "0x32": "EBU",
    } for row in critical_by_variant), f"critical Brake/EPS junction drift: {critical_by_variant}")

    placement = variants[0]
    bus4 = [r for r in placement if r["bus_name"] == "Bus 4"]
    ebu_rows = [r for r in placement if r["junction_name"] == "EBU"]
    need(len(ebu_rows) == 1 and ebu_rows[0]["component_index"] == "0x32", f"Camry EBU rows drift: {ebu_rows}")
    need(not any(r["ecu_domain"] == "EBU" for r in placement), "EBU unexpectedly became ECU-domain name")
    need(not any(r["component_index"] == "0x65" for r in placement), "Camry unexpectedly gained component 0x65")

    # Current Toyota English GTS does not spell the acronym out.  Preserve that
    # exact negative so the expansion can be separately sourced to Toyota-authored
    # material rather than invented from an acronym dictionary.
    expansion_hits = {
        term: [text for _, text in strings.search(term, limit=32)]
        for term in ("Electronic Brake Unit", "Electric Brake Unit", "Electronic Brake Module")
    }
    need(not any(expansion_hits.values()), f"GTS now contains an EBU expansion: {expansion_hits}")

    ebu_node = {
        key: monitor_names(parser, sources[key], strings)
        for key in ("abs_p5", "brake_booster_p5", "epb_p5", "bscm_a_p6", "bscm_b_p6")
    }

    def named_monitors(key: str, names: set[str]) -> list[dict[str, Any]]:
        db = parser.parse_ecu_db(sources[key])
        rows = []
        for rec in extract_monitor_records(db.sections[62]):
            name = strings.get_string(rec.name_string_index) or ""
            if name in names:
                rows.append({"name": name, "primary_did": f"0x{rec.primary_did:04X}"})
        return rows

    p6_ebu_identity_probe = {
        "bscm_a_native": named_monitors("bscm_a_p6", {"FR Wheel Speed", "Lateral G"}),
        "bscm_b_ebu_mirror": named_monitors("bscm_b_p6", {"FR Wheel Speed (EBU node)", "Lateral G (EBU node)"}),
    }
    need(all(ebu_node[k] for k in ("abs_p5", "brake_booster_p5", "epb_p5", "bscm_b_p6")),
         "expected brake-domain EBU-node vocabulary missing")
    need(not ebu_node["bscm_a_p6"], "BSCM_A_P6 unexpectedly carries EBU-node monitor names")
    need({row["name"] for row in p6_ebu_identity_probe["bscm_a_native"]} == {"FR Wheel Speed", "Lateral G"},
         f"BSCM_A native dynamics drift: {p6_ebu_identity_probe}")
    need(any(row["name"] == "FR Wheel Speed (EBU node)" for row in p6_ebu_identity_probe["bscm_b_ebu_mirror"]),
         f"BSCM_B EBU mirror drift: {p6_ebu_identity_probe}")

    abs_db = parser.parse_ecu_db(sources["abs_p5"])
    dtc_rows = {}
    for entry in parser.extract_dtc_failure_entries(abs_db.sections[65]):
        if entry.code in {"U013187", "U11B187"}:
            dtc_rows[entry.code] = {
                "description": strings.get_string(entry.description_string_index) or "",
                "failure": strings.get_string(entry.failure_string_index) or "",
                "enabled": entry.tail_word != 0,
            }
    need(set(dtc_rows) == {"U013187", "U11B187"}, f"ABS_P5 EPS communication DTC vocabulary drift: {dtc_rows}")
    need("Power Steering" in dtc_rows["U013187"]["description"]
         and "(ch2)" in dtc_rows["U11B187"]["description"],
         f"ABS_P5 EPS channel names drift: {dtc_rows}")
    eps_comm_open = []
    for rec in extract_monitor_records(abs_db.sections[62]):
        name = strings.get_string(rec.name_string_index) or ""
        if name == "EPS/Steering Control Actuator ECU Communication Open":
            eps_comm_open.append({
                "name": name,
                "primary_did": f"0x{rec.primary_did:04X}",
                "alternate_did": f"0x{rec.alternate_did:04X}" if rec.alternate_did else "0x0000",
                "bit_range": [rec.bit_start, rec.bit_end],
            })
    need(eps_comm_open and {row["primary_did"] for row in eps_comm_open} == {"0x102F"},
         f"ABS_P5 EPS communication-open monitor drift: {eps_comm_open}")

    # P6 category names are a clean successor naming control: A is Brake/EPB;
    # B is Brake Booster.  This is useful context for the EBU-node vocabulary,
    # not backward-transfer proof of exact Camry physical ownership.
    cats = {e.category_id: e for e in parser.extract_master_ecu_categories(master.sections[16])}
    cat_names = {cid: strings.get_string(cats[cid].ecu_name_string_index) or "" for cid in (6004, 6005)}
    need(cats[6004].database_name == "BSCM_A_P6.ddb" and cat_names[6004] == "Brake/EPB", "P6 BSCM_A identity drift")
    need(cats[6005].database_name == "BSCM_B_P6.ddb" and cat_names[6005] == "Brake Booster", "P6 BSCM_B identity drift")

    result = {
        "schema": "camry-2026-ebu-topology-v1",
        "title": "2026 Camry GTS EBU attachment and brake-domain topology boundary",
        "sources": {k: {"path": str(v.relative_to(ROOT)), "sha256": sha(v)} for k, v in sources.items()},
        "exact_camry": {
            "vehicle_types": [{"id": v, "name": vehicle_names[v]} for v in CAMRY_VEHICLE_TYPES],
            "can_bus_car_id": f"0x{CAMRY_CAN_BUS_CAR_ID:08X}",
            "option_count": len(option_rows),
            "network_membership_variant_count": len(membership_shapes),
            "junction_attachment_variant_count": len(junction_shapes),
            "critical_brake_eps_junctions_invariant_across_all_options": True,
            "component_count": len(placement),
            "bus4_placements": bus4,
            "ebu_junction_rows": ebu_rows,
            "ebu_ecu_component_present": False,
            "component_0x65_present": False,
            "literal_table_fact": (
                "In current GTS+ CDbCanBusComponentTable, EBU is the string-valued junction/attachment field "
                "on the exact Camry EPS component row. It is not an installed ECU-domain/component row."
            ),
        },
        "gts_vocabulary": {
            "literal_ebu_expansion_present": False,
            "expansion_search_hits": expansion_hits,
            "ebu_node_monitor_rows": ebu_node,
            "p6_ebu_identity_probe": {
                **p6_ebu_identity_probe,
                "interpretation": (
                    "Successor BSCM_A=Brake/EPB exposes the native wheel/G quantities while BSCM_B=Brake Booster exposes an EBU-node copy. "
                    "This strongly favors EBU as the Brake/EPB/skid-control-side node rather than a third ECU, but it is successor contextual evidence, not an exact-P5 Camry wiring proof."
                ),
            },
            "brake_to_eps_channel_vocabulary": {
                "abs_p5_dtc_rows": dtc_rows,
                "eps_communication_open_monitor": eps_comm_open,
                "interpretation_boundary": (
                    "ABS_P5 explicitly distinguishes ordinary Power Steering communication from a Power Steering Control Module A (ch2) missing-message code and exposes an EPS/Steering Control Actuator ECU Communication Open bit. This supports a brake-domain secondary/local EPS communication path, but static DDB capability does not prove which channel exact Camry uses for B6."
                ),
            },
            "p6_successor_category_control": {
                "6004": {"database": cats[6004].database_name, "name": cat_names[6004]},
                "6005": {"database": cats[6005].database_name, "name": cat_names[6005]},
                "boundary": "Successor naming is context for the brake-domain split, not an exact-P5 Camry ownership transfer.",
            },
        },
        "interpretation": {
            "discrete_ebu_filter_ecu_supported_by_exact_camry_topology": False,
            "one_eps_controller_compatible_with_upstream_segmentation": True,
            "leading_physical_model": (
                "The exact topology supports an EPS attachment through an EBU-labelled brake-domain node/branch, not a second "
                "installed EBU ECU. Combined with the one-controller F33 receiver and direct-B6 pre-admission loss, the leading "
                "model is an upstream Brake/Skid request-generation/routing boundary feeding the EPS over its single local CAN path. "
                "The P6 A/B split strongly favors the EBU node as the Brake/EPB/skid-control side, and ABS_P5's explicit Power-Steering ch2/missing-message vocabulary is consistent with that two-sided brake-domain topology."
            ),
            "unresolved": (
                "Current GTS does not identify the exact electrical bridge, whether the EBU-labelled attachment is internal to the "
                "brake actuator assembly, or the concrete B6 filter/forwarder/signing routine. Exact category-435 F152633K0000 "
                "firmware or physical wiring/trace evidence is required for that promotion."
            ),
        },
    }

    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if ns.check:
        need(ns.output.is_file(), f"missing artifact {ns.output}")
        need(ns.output.read_text() == text, "generated EBU topology artifact stale")
    else:
        ns.output.parent.mkdir(parents=True, exist_ok=True)
        ns.output.write_text(text)
        print(f"wrote {ns.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
