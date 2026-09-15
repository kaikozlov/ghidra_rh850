#!/usr/bin/env python3
"""Build the bounded H/F Corolla non-steering engagement-state contract."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import struct
import zipfile
from pathlib import Path
from tools.targets.corolla.support.corolla_h_constants import CODEFLASH as H_CODEFLASH

REPO = Path(__file__).resolve().parents[4]
IMAGE = H_CODEFLASH
RX_DIFF = REPO / "data/generated/corolla_8965H1202000_application_rx_diff.json"
ENG_EVID = REPO / "data/generated/corolla_8965H1202000_nonsteering_engagement_decompiler_evidence.json"
STATE = REPO / "data/generated/corolla_8965H1202000_openpilot_state_bridge.json"
TECH_READY = REPO / "data/generated/corolla_8965H1202000_techstream_correlations.json"
TECH_CRUISE = REPO / "data/generated/techstream_v18/tss3_cruise_engagement_semantics.json"
TECH_CRUISE_TRANSPORT = REPO / "data/generated/techstream_v18/tss3_cruise_live_transport.json"
PUBLIC = REPO / "data/generated/corolla_2023_public_route_opendbc_evidence.json"
SPAN = REPO / "data/generated/corolla_2025_span_discord_rlog_opendbc_evidence.json"
EQ = REPO / "data/generated/corolla_8965F1208000_vs_8965H1202000_codeflash_equivalence.json"
ALBINO_ARCH = REPO / "community/albinoelephant/albinoelephant_discord_PORT_ARCHITECTURE.md"
ALBINO_PORT = REPO / "community/albinoelephant/Corolla_Fingerprint_v1.zip"
ALBINO_DBC_MEMBER = r"Corolla_Fingerprint\port\files\opendbc_repo\opendbc\dbc\toyota_corolla_tss3_pt.dbc"
GTS_REGISTRY = REPO / "data/generated/gtsplus_2026/toyota_diag_registry_camry_2026.json"
OUT = REPO / "data/generated/corolla_hf_nonsteering_engagement_state.json"


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load(path: Path) -> dict:
    return json.loads(path.read_text())


def fns(e: dict) -> dict[int, dict]:
    return {int(x["entry"], 16): x for x in e["functions"]}


def need(text: str, *tokens: str) -> None:
    for token in tokens:
        if token not in text:
            raise ValueError(f"missing target-native token: {token}")


def route_inventory(route: dict) -> dict[str, dict]:
    rows = route.get("incoming_state_inventory", route.get("role_inventory"))
    return {x["can_id"]: x for x in rows}


def find_gts_signal(registry: dict, source: str, name: str) -> dict:
    stack = [registry]
    while stack:
        item = stack.pop()
        if isinstance(item, dict):
            if item.get("source") == source and item.get("name") == name and "signal_info" in item:
                return item
            stack.extend(item.values())
        elif isinstance(item, list):
            stack.extend(item)
    raise ValueError(f"missing GTS+ signal {source}:{name}")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", type=Path, default=OUT)
    args = ap.parse_args()

    image = IMAGE.read_bytes()
    rx = load(RX_DIFF)
    eng = load(ENG_EVID)
    state = load(STATE)
    tech_ready = load(TECH_READY)
    tech_cruise = load(TECH_CRUISE)
    tech_cruise_transport = load(TECH_CRUISE_TRANSPORT)
    public = load(PUBLIC)
    span = load(SPAN)
    eq = load(EQ)
    albino_arch = ALBINO_ARCH.read_text()
    with zipfile.ZipFile(ALBINO_PORT) as zf:
        albino_dbc = zf.read(ALBINO_DBC_MEMBER).decode("utf-8", "replace")
    gts_registry = load(GTS_REGISTRY)
    gts_hv_gear = find_gts_signal(gts_registry, "HV_P5.ddb", "Shift Position")
    if gts_hv_gear["signal_info"]["pattern_display"] != {"0": "P", "2": "R", "4": "N", "6": "D", "8": "B"}:
        raise ValueError("GTS+ P5 hybrid shift-position semantics drift")
    for marker in (
        "Longitudinal (follow, speed, stop-and-go to 0 + hold, resume): VALIDATED on car",
        "acc_main_on = msg->data[7] != 0U",
        "Lateral: IN PROGRESS",
    ):
        if marker not in albino_arch:
            raise ValueError(f"Albino retained architecture drift: {marker}")
    for marker in (
        'CM_ SG_ 138 ACC_STATE "byte 7. DECODED FROM REAL DRIVES',
        'CM_ SG_ 138 ACC_STANDSTILL "byte 7 mask 0x20.',
        'CM_ SG_ 593 SET_SPEED "byte 2, mph, factor 1.0',
    ):
        if marker not in albino_dbc:
            raise ValueError(f"Albino retained live-drive note drift: {marker}")

    if len(image) != 0x100000 or sha(image) != eng["image"]["sha256"]:
        raise ValueError("exact-H image/evidence identity drift")
    if eq["application_equivalence"]["different_bytes"] != 0:
        raise ValueError("H/F application equivalence drift")

    target_desc = {x["can_id"]: x for x in rx["target"]["descriptors"]}
    if (target_desc["0x127"]["index"], target_desc["0x127"]["length"]) != (20, 8):
        raise ValueError("H 0x127 descriptor drift")
    if (target_desc["0x51E"]["index"], target_desc["0x51E"]["length"]) != (24, 8):
        raise ValueError("H 0x51E descriptor drift")

    signal_to_pdu = [struct.unpack_from("<H", image, 0x223FC + 2 * i)[0] for i in range(274)]
    pdu25_signals = [i for i, pdu in enumerate(signal_to_pdu) if pdu == 25]
    pdu29_signals = [i for i, pdu in enumerate(signal_to_pdu) if pdu == 29]
    if pdu25_signals != list(range(123, 133)) or pdu29_signals != list(range(154, 164)):
        raise ValueError("H 0x127/0x51E signal-to-PDU ownership drift")

    ef = fns(eng)
    for row in eng["functions"]:
        start = int(row["entry"], 16)
        if sha(image[start:start + row["body_size"]]) != row["body_sha256"]:
            raise ValueError(f"H raw body drift {row['entry']}")
        if sha(row["decompiled_c"].encode()) != row["decompiled_c_sha256"]:
            raise ValueError(f"H decompile digest drift {row['entry']}")

    gear_c = ef[0x45EDE]["decompiled_c"]
    ready_c = ef[0x46144]["decompiled_c"]
    stage_c = ef[0x5262C]["decompiled_c"]
    secondary_copy_c = ef[0xBAB58]["decompiled_c"]
    primary_copy_c = ef[0xBAC16]["decompiled_c"]
    publish_c = ef[0xBBA48]["decompiled_c"]
    need(gear_c,
         "FUN_0007643a(0x7b,0xd7,6,2,0,",
         "FUN_0007643a(0x7d,0xd8,1,3,0,",
         "FUN_0007643a(0x81,0xda,0xb,0,1,0xfebe7cfc);")
    scalar_calls = re.findall(r"FUN_0007643a\((0x[0-9a-f]+|\d+),([^;]+)\);", gear_c, re.I)
    if [int(x[0], 0) for x in scalar_calls] != [129, 123, 125]:
        raise ValueError(f"H 0x127 scalar call set drift: {scalar_calls}")
    need(ready_c, "FUN_0007643a(0x9a,0xf7,1,7,0,0xfebe7d1b);")
    need(stage_c, "uRamfebef052 = uRamfebe7d1b;")
    need(secondary_copy_c, "uVar1 = uRamfebef052;", "*(undefined1 *)(iVar3 + -600) = uVar1;")
    need(primary_copy_c, "cRamfebeb5a8 = cRamfebef052;")
    need(publish_c, "uRamfebee811 = uRamfebeb5a8;")

    ready = tech_ready["steering_state_bridge_diagnostics"]["ready_status_oracle"]
    if not (ready["name"] == "Ready Status" and ready["primary_data_id"] == "0x1033" and
            ready["source_chain"] == ["0xFEBE7D1B", "0xFEBEF052", "0xFEBEB5A8", "0xFEBEE811", "DID 0x1033"]):
        raise ValueError("Techstream/H Ready Status diagnostic join drift")
    state_ready = state["state_bridge"]["ready_status_input_0x51E"]
    if not (state_ready["can_id"] == "0x51E" and state_ready["wire"] == "B0[7]" and state_ready["did"] == "0x1033"):
        raise ValueError("state-bridge Ready Status wire join drift")

    frc_boundary = tech_cruise["frc_p5"]["boundary"]
    if not all(x in frc_boundary for x in ("DDB rows alone", "current-GTS+ host evidence", "SID 0x22 ReadDataByIdentifier")):
        raise ValueError("FRC P5 Data-ID/UDS transport boundary drift")
    transport_rows = {x["data_id"]: x for x in tech_cruise_transport["selected_cruise_oracles"]}
    if set(transport_rows) != {"0x1901", "0x1905", "0x1906", "0x1912", "0x1914"}:
        raise ValueError("FRC live-transport selected Data-ID set drift")
    for did, row in transport_rows.items():
        if row["request"] != "22" + did[2:] or row["strict_capture_positive_prefix"] != "62" + did[2:]:
            raise ValueError(f"FRC live-transport request/response drift: {did}")
    frc_rows = {x["name"]: x for x in tech_cruise["frc_p5"]["monitors"]}
    required_oracles = {
        "Cruise Control Permission Flag": ("0x1905", [8, 8]),
        "Main Switch Recognition Flag": ("0x1906", [8, 8]),
        "ACC Not Available Icon Lighting Request Flag": ("0x1906", [40, 40]),
        "ACC Control in Operation Flag": ("0x1914", [8, 8]),
        "Set Vehicle Interval Time": ("0x1912", [0, 7]),
        "Current Vehicle Speed": ("0x1901", [0, 31]),
        "Memory Vehicle Speed": ("0x1901", [32, 63]),
    }
    for name, (data_id, bits) in required_oracles.items():
        row = frc_rows[name]
        if row["primary_data_id"] != data_id or row["bit_range"] != bits:
            raise ValueError(f"FRC P5 engagement oracle drift: {name}")

    pub_inv = route_inventory(public)
    span_inv = route_inventory(span)
    old_cruise_ids = ["0x177", "0x1A2", "0x1D3", "0x399"]
    if any(pub_inv[x]["instances"] or span_inv[x]["instances"] for x in old_cruise_ids):
        raise ValueError("legacy cruise replacement-negative drift")

    pub176 = public["direct_reuse_evidence"]["0x176"]
    span176 = span["direct_reuse_evidence"]["0x176"]
    pub24d = public["direct_reuse_evidence"]["0x24D"]
    span24d = span["direct_reuse_evidence"]["0x24D"]
    pub51e = public["direct_reuse_evidence"]["0x51E"]
    span51e = span["direct_reuse_evidence"]["0x51E"]
    if not (pub176["checksum_valid"] == pub176["frame_count"] == 1855 and span176["checksum_valid"] == span176["frame_count"] == 1890):
        raise ValueError("0x176 checksum/frame-count drift")
    if pub176["cruise_active_values"] != [False] or pub176["cruise_state_values"] != [0] or span176["cruise_active_values"] != [False] or span176["cruise_state_values"] != [0]:
        raise ValueError("0x176 inactive prior-art field drift")
    if not (pub176["b0_bit3_context"]["1"]["gas_positive_fraction"] == 0.0 and
            pub176["b0_bit3_context"]["0"]["gas_positive_fraction"] > 0.99 and
            span176["b0_bit3_context"]["1"]["gas_positive_fraction"] < 0.01 and
            span176["b0_bit3_context"]["0"]["gas_positive_fraction"] > 0.97):
        raise ValueError("0x176 B0[3] accelerator-context drift")
    if any(v != [0] for r in (pub24d, span24d) for v in r["prior_art_button_values"].values()):
        raise ValueError("0x24D inactive cruise-switch prior-art drift")
    if not (pub51e["frame_count"] == 59 and pub51e["ready_status_values"] == [1] and
            span51e["frame_count"] == 60 and span51e["ready_status_values"] == [1]):
        raise ValueError("0x51E route Ready Status corroboration drift")

    gear = span["direct_reuse_evidence"]["0x127"]
    span_3bf = span["direct_reuse_evidence"]["0x3BF"]
    public_3bf = public["direct_reuse_evidence"]["0x3BF"]
    public_2a1 = public["direct_reuse_evidence"]["0x2A1"]
    span_acc = span["direct_reuse_evidence"]["0x08A_acc"]
    span_set_speed = span["direct_reuse_evidence"]["0x251"]
    if not (gear["frame_count"] == gear["checksum_valid"] == 3662 and gear["gear_raw_values"] == [3] and gear["prior_art_decoded_values"] == ["D"]):
        raise ValueError("Span 0x127 raw3/prior-art-D evidence drift")
    if not (span_3bf["raw_values"] == [0x10] and public_3bf["direct_observed_labels"] == {"0x10": "D", "0x40": "R", "0x80": "P"} and
            [x["raw"] for x in public_3bf["transitions"]] == [0x80, 0x40, 0x10] and
            [x["raw"] for x in public_2a1["transitions"]] == [1, 2, 4]):
        raise ValueError("generation-native Corolla gear transition evidence drift")
    if not (span_acc["acc_engaged_frames"] == 37 and span_acc["acc_disengaged_frames"] == 2363 and
            span_acc["state_when_engaged"] == [0x5D] and span_acc["state_when_disengaged"] == [0x12]):
        raise ValueError("Span native 0x08A ACC-state evidence drift")

    out = {
        "schema": "corolla-hf-nonsteering-engagement-state-v1",
        "software_family": {
            "h": "8965H1202000",
            "f": "8965F1208000",
            "application_byte_identical": True,
        },
        "ready_status": {
            "classification": "wire field closed",
            "can_id": "0x51E",
            "length": 8,
            "h_rx_descriptor_index": 24,
            "h_signal_id": 154,
            "wire": "B0[7]",
            "source_chain": ["0x51E B0[7]", "0xFEBE7D1B", "0xFEBEF052", "0xFEBEB5A8", "0xFEBEE811", "DID 0x1033"],
            "operational_copy_sites": ["0x000BAB58", "0x000BAC16"],
            "writer_boundary": "FEBEF052 reaches FEBEB5A8 through two operational copy sites and the RAM nodes also have initialization/reset writers. The Ready Status dataflow is proved; exclusive-writer provenance is not claimed.",
            "techstream": {
                "name": "Ready Status",
                "did": "0x1033",
                "boolean_domain": [0, 1],
            },
            "route_corroboration": {
                "public_2023": {"frames": pub51e["frame_count"], "values": pub51e["ready_status_values"], "payloads": pub51e["unique_payloads"]},
                "span_2025": {"frames": span51e["frame_count"], "values": span51e["ready_status_values"], "payloads": span51e["unique_payloads"]},
            },
            "boundary": "Both operational captures show only value 1; value 0 and a Ready transition remain uncaptured. This is an incoming Ready Status field, not proof that an EPS Tx PDU republishes the same boolean.",
        },
        "gear": {
            "classification": "core CarState gear semantics closed from generation-native route transitions plus Toyota ordering",
            "preferred_carriers": {
                "retained_hybrid_shape": "0x127 GEAR_PACKET_HYBRID",
                "generation_native_fallback": "0x3BF byte0 one-hot",
            },
            "exact_h_0x127": {
                "can_id": "0x127",
                "length": 8,
                "h_rx_descriptor_index": 20,
                "h_signal_ids": pdu25_signals,
                "h_scalar_extractions": [
                    {"signal_id": 123, "wire": "B0[7:2]", "length": 6},
                    {"signal_id": 125, "wire": "B1[3]", "length": 1},
                    {"signal_id": 129, "wire": "B3/B4 signed11 domain", "length": 11},
                ],
                "legacy_gear_field": {"wire": "B5[3:0]", "prior_art_values": {"0": "P", "1": "R", "2": "N", "3": "D", "4": "B"}},
                "static_boundary": "Exact H retains 0x127, but its EPS scalar unpacker does not consume the legacy B5[3:0] gear nibble; whole-vehicle route/GTS evidence therefore owns CarState gear semantics.",
            },
            "span_0x127": {
                "frames": gear["frame_count"],
                "checksum_valid": gear["checksum_valid"],
                "raw_values": gear["gear_raw_values"],
                "decoded_values": gear["prior_art_decoded_values"],
                "decode_basis": gear["decode_basis"],
            },
            "generation_native_0x3bf": {
                "public_2023": public_3bf,
                "span_2025": span_3bf,
                "enum": {"0x80": "P", "0x40": "R", "0x20": "N", "0x10": "D"},
                "boundary": "P/R/D are directly observed on the retained public route and D is independently repeated in Span's moving 2025 segment. N=0x20 is the remaining one-hot value and preserves Toyota's P/R/N/D ordering; it is corroborated by GTS+ rather than a retained N transition.",
            },
            "corroborating_0x2a1": public_2a1,
            "gts_p5_hybrid_ordering": {
                "source": gts_hv_gear["source"],
                "name": gts_hv_gear["name"],
                "pattern_display": gts_hv_gear["signal_info"]["pattern_display"],
            },
            "production_boundary": "The base port no longer needs a gear-discovery experiment. Use 0x127 where the retained hybrid carrier is present and 0x3BF otherwise; preserve the stated N/0x127-unexercised-value evidence boundaries rather than inventing new enums.",
        },
        "cruise": {
            "classification": "core generation-native CarState mapping closed; optional detailed ACC UI/follow fields remain open",
            "retained_wire_prior_art": {
                "0x176": {
                    "public_2023_frames": pub176["frame_count"],
                    "span_2025_frames": span176["frame_count"],
                    "checksums_all_valid": True,
                    "legacy_cruise_active_values": [False],
                    "legacy_cruise_state_values": [0],
                    "b0_bit3_values": [0, 1],
                    "b0_bit3_interpretation": "Rejected as the TSS3 active/main source: B0[3] tracks accelerator-release/brake context while the old CRUISE_ACTIVE/STATE fields stay inactive.",
                    "public_2023_b0_bit3_context": pub176["b0_bit3_context"],
                    "span_2025_b0_bit3_context": span176["b0_bit3_context"],
                },
                "0x24D": {
                    "public_2023_frames": pub24d["frame_count"],
                    "span_2025_frames": span24d["frame_count"],
                    "legacy_button_fields": {k: [0] for k in pub24d["prior_art_button_values"]},
                    "boundary": "The carrier survives, but neither retained segment exercises a cruise-switch transition; old button semantics remain prior-art only.",
                },
            },
            "native_wire_mapping": {
                "available": "0x08A ACC_STATE (B7) != 0; retained states 0x12 idle and 0x5D engaged, and the validated contributor Panda path uses B7!=0 as acc_main_on",
                "enabled": "0x08A B22 bit0x10; Span directly observes 2,363 clear / 37 asserted frames with exact 0x12/0x5D state separation",
                "standstill": "0x08A ACC_STATE B7 bit0x20; contributor live-drive evidence records 0x67 engaged+standstill hold and validates stop-and-go hold/resume",
                "set_speed": "0x251 B2, mph factor 1.0; contributor live-drive evidence records one-mph +/- changes and a 19-mph floor",
                "span_0x08a": span_acc,
                "span_0x251": span_set_speed,
            },
            "legacy_ids_absent_in_both_captures": old_cruise_ids,
            "techstream_p5_frc_oracles": tech_cruise["frc_p5"]["monitors"],
            "openpilot_oracle_mapping": tech_cruise["frc_p5"]["openpilot_oracle_mapping"],
            "supporting_p5_oracles": tech_cruise["supporting_p5"],
            "wire_mapping_status": {
                "cruise_available": "closed on generation-native 0x08A ACC_STATE presence",
                "cruise_enabled": "closed on generation-native 0x08A B22 bit0x10",
                "cruise_standstill": "closed from contributor live-drive 0x08A B7 bit0x20 / state0x67",
                "set_speed": "closed from contributor live-drive 0x251 B2 mph",
                "acc_not_available_or_fault": "optional/open: exact FRC_P5 diagnostic oracle exists, but no base-control CAN mapping is required",
                "follow_distance": "optional/open: exact FRC_P5 Set Vehicle Interval Time oracle exists",
            },
            "capture_recipe": [
                "Use FRC_P5 0x1905/0x1906/0x1914 only to extend optional permission/fault UI semantics; core available/enabled no longer requires a diagnostic discovery pass.",
                "Use FRC_P5 0x1912 only if exposing following-distance state is desired.",
                "Retain 0x1901 Current/Memory Vehicle Speed as a diagnostic cross-check for 0x251 set speed rather than a required runtime input.",
            ],
            "diagnostic_transport_boundary": "Current GTS+ proves selected FRC_P5 0x1901/0x1905/0x1906/0x1912/0x1914 Data IDs are ordinary SID 0x22 ReadDataByIdentifier requests. They are now optional semantic oracles, not prerequisites for core CarState.",
            "retained_contributor_boundary": "The retained contributor architecture explicitly says longitudinal follow/speed/stop-and-go-to-0/hold/resume was VALIDATED on car while lateral remained IN PROGRESS. Only the longitudinal/state observations are used here.",
            "boundary": "Core openpilot cruise state is closed from retained generation-native CAN plus validated contributor live-drive evidence. Detailed ACC-not-available UI and follow-distance remain optional unmapped state.",
        },
        "implementation_consequence": {
            "safe_now": [
                "Use 0x51E B0[7] as target-native Ready Status input; keep Ready=0 fault policy dynamic until exercised.",
                "Use 0x127 GEAR_PACKET_HYBRID on the retained hybrid shape and generation-native 0x3BF one-hot gear otherwise.",
                "Use 0x08A ACC_STATE/B22 for cruise available/enabled and the contributor-validated B7 bit0x20 standstill state.",
                "Use retained 0x251 B2 as set speed in mph; preserve the native 19-mph set-speed floor and manual resume from hold.",
                "Keep optional follow-distance and detailed ACC-unavailable UI unmapped until needed; their FRC_P5 diagnostic oracles are already known.",
            ],
            "not_safe_yet": [
                "Treat 0x176 B0[3] as cruise main/active state.",
                "Assume surviving 0x24D button bit semantics without a button transition.",
                "Map Ready=0 or native steering fault states to temporary/permanent openpilot faults without an exercised recovery/latched transition.",
            ],
        },
        "evidence_sources": {
            "h_decompiler": {"path": str(ENG_EVID.relative_to(REPO)), "sha256": sha(ENG_EVID.read_bytes())},
            "h_rx_diff": {"path": str(RX_DIFF.relative_to(REPO)), "sha256": sha(RX_DIFF.read_bytes())},
            "state_bridge": {"path": str(STATE.relative_to(REPO)), "sha256": sha(STATE.read_bytes())},
            "techstream_ready": {"path": str(TECH_READY.relative_to(REPO)), "sha256": sha(TECH_READY.read_bytes())},
            "techstream_cruise": {"path": str(TECH_CRUISE.relative_to(REPO)), "sha256": sha(TECH_CRUISE.read_bytes())},
            "techstream_cruise_live_transport": {"path": str(TECH_CRUISE_TRANSPORT.relative_to(REPO)), "sha256": sha(TECH_CRUISE_TRANSPORT.read_bytes())},
            "public_route": {"path": str(PUBLIC.relative_to(REPO)), "sha256": sha(PUBLIC.read_bytes())},
            "span_route": {"path": str(SPAN.relative_to(REPO)), "sha256": sha(SPAN.read_bytes())},
            "albino_architecture": {"path": str(ALBINO_ARCH.relative_to(REPO)), "sha256": sha(ALBINO_ARCH.read_bytes())},
            "albino_port_package": {"path": str(ALBINO_PORT.relative_to(REPO)), "sha256": sha(ALBINO_PORT.read_bytes()), "dbc_member": ALBINO_DBC_MEMBER},
            "gts_registry": {"path": str(GTS_REGISTRY.relative_to(REPO)), "sha256": sha(GTS_REGISTRY.read_bytes())},
        },
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    print(args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
