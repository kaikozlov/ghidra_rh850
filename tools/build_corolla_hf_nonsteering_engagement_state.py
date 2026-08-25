#!/usr/bin/env python3
"""Build the bounded H/F Corolla non-steering engagement-state contract."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import struct
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
IMAGE = REPO / "community/albinoelephant/normalized/8965H1202000_CodeFlash.bin"
RX_DIFF = REPO / "data/generated/corolla_8965H1202000_application_rx_diff.json"
ENG_EVID = REPO / "data/generated/corolla_8965H1202000_nonsteering_engagement_decompiler_evidence.json"
STATE = REPO / "data/generated/corolla_8965H1202000_openpilot_state_bridge.json"
TECH_READY = REPO / "data/generated/corolla_8965H1202000_techstream_correlations.json"
TECH_CRUISE = REPO / "data/generated/techstream_v18/tss3_cruise_engagement_semantics.json"
PUBLIC = REPO / "data/generated/corolla_2023_public_route_opendbc_evidence.json"
SPAN = REPO / "data/generated/corolla_2025_span_discord_rlog_opendbc_evidence.json"
EQ = REPO / "data/generated/corolla_8965F1208000_vs_8965H1202000_codeflash_equivalence.json"
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
    public = load(PUBLIC)
    span = load(SPAN)
    eq = load(EQ)

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
    if not all(x in frc_boundary for x in ("primary Data IDs", "not automatically UDS ReadDataByIdentifier DIDs", "diagnostic transport service")):
        raise ValueError("FRC P5 Data-ID/UDS transport boundary drift")
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
    if not (gear["frame_count"] == gear["checksum_valid"] == 3662 and gear["gear_raw_values"] == [3] and gear["prior_art_decoded_values"] == ["D"]):
        raise ValueError("Span 0x127 raw3/prior-art-D evidence drift")

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
            "classification": "carrier/layout retained; raw 3 observed and prior-art-compatible with D; target-native enum semantics not independently validated",
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
            "h_static_boundary": "Exact H retains 0x127 and three scalar fields at the same wire positions as the older SecOC Toyota family, but its generated scalar unpacker does not consume the legacy B5[3:0] gear nibble. The EPS therefore cannot statically validate P/R/N/B enum semantics.",
            "span_dynamic": {"frames": gear["frame_count"], "checksum_valid": gear["checksum_valid"], "raw_values": gear["gear_raw_values"], "prior_art_decoded_values": gear["prior_art_decoded_values"], "decode_basis": gear["decode_basis"]},
            "production_boundary": "Raw value 3 is operationally observed and compatible with the retained Toyota prior-art D enum, but the MOCK rlog provides no independent gear-state oracle. Treat target-native D semantics as bounded until an independent gear oracle or explicit transition confirms them; P/R/N/B still require live transitions.",
        },
        "cruise": {
            "classification": "diagnostic semantics narrowed; live CAN mapping not closed",
            "retained_wire_prior_art": {
                "0x176": {
                    "public_2023_frames": pub176["frame_count"],
                    "span_2025_frames": span176["frame_count"],
                    "checksums_all_valid": True,
                    "legacy_cruise_active_values": [False],
                    "legacy_cruise_state_values": [0],
                    "b0_bit3_values": [0, 1],
                    "b0_bit3_interpretation": "Strongly tracks accelerator-release/driver-input context in both captures. Without an independent cruise-state oracle this does not disprove every possible cruise-related meaning, but it is insufficient evidence to promote B0[3] as TSS3 main/active cruise state.",
                    "public_2023_b0_bit3_context": pub176["b0_bit3_context"],
                    "span_2025_b0_bit3_context": span176["b0_bit3_context"],
                },
                "0x24D": {
                    "public_2023_frames": pub24d["frame_count"],
                    "span_2025_frames": span24d["frame_count"],
                    "legacy_button_fields": {k: [0] for k in pub24d["prior_art_button_values"]},
                    "boundary": "The carrier survives, but neither segment exercises a cruise-switch transition, so old button semantics remain a prior-art lead only.",
                },
            },
            "legacy_ids_absent_in_both_captures": old_cruise_ids,
            "techstream_p5_frc_oracles": tech_cruise["frc_p5"]["monitors"],
            "openpilot_oracle_mapping": tech_cruise["frc_p5"]["openpilot_oracle_mapping"],
            "supporting_p5_oracles": tech_cruise["supporting_p5"],
            "wire_mapping_status": {
                "cruise_available": "open: diagnose against Main Switch Recognition Flag and Cruise Control Permission Flag",
                "cruise_enabled": "open: diagnose against ACC Control in Operation Flag",
                "set_speed": "open: diagnose against Memory Vehicle Speed; Current Vehicle Speed is an independent reference",
                "acc_not_available_or_fault": "open: diagnose against ACC Not Available Icon Lighting Request Flag and permission state",
                "follow_distance": "open: diagnose against Set Vehicle Interval Time",
            },
            "capture_recipe": [
                "Use Techstream/GTS+ FRC_P5 Data ID 0x1905 (Cruise Control Permission Flag) while toggling cruise main and engagement.",
                "Use Techstream/GTS+ FRC_P5 Data ID 0x1906 (Main Switch Recognition Flag, Set Cancel Switch Condition, ACC Not Available Icon Lighting Request Flag) synchronized with all-bus CAN.",
                "Use Techstream/GTS+ FRC_P5 Data ID 0x1914 (ACC Control in Operation Flag) through disengaged -> engaged -> cancelled transitions.",
                "Use Techstream/GTS+ FRC_P5 Data ID 0x1901 (Current Vehicle Speed, Memory Vehicle Speed) while changing set speed.",
                "Use Techstream/GTS+ FRC_P5 Data ID 0x1912 (Set Vehicle Interval Time) while cycling following distance.",
            ],
            "diagnostic_transport_boundary": "The 0x19xx values above are P5 diagnostic Data IDs from FRC_P5, not automatically UDS ReadDataByIdentifier DIDs. Use Techstream/GTS+ data-monitor access unless a separate FRC service mapping proves direct 0x22 support.",
            "boundary": "Neither retained route supplies an independent cruise-main/engagement oracle. Exact Toyota diagnostics now define what each missing semantic must correlate with, but no CAN field may be promoted to available/enabled/set-speed/fault until a wire-to-oracle transition is observed or statically recovered from the producer firmware.",
        },
        "implementation_consequence": {
            "safe_now": [
                "Add/inspect 0x51E B0[7] as target-native Ready Status input.",
                "The current read-only parser may retain prior-art raw3->D decoding as an observation aid, but do not call D target-native validated; preserve P/R/N/B as unvalidated prior-art enums.",
                "Keep TSS3 cruiseState.available/enabled/set-speed neutral in production CarState.",
                "Use the exact FRC P5 Data-ID oracle set through Techstream/GTS+ for the next synchronized capture instead of guessing replacement CAN bits.",
            ],
            "not_safe_yet": [
                "Treat 0x176 B0[3] as cruise main/active state.",
                "Assume surviving 0x24D button bit semantics without a button transition.",
                "Map diagnostic permission/main/active/fault/set-speed semantics to CAN without a producer/static or synchronized live join.",
                "Promote P/R/N/B gear enums without live transitions.",
            ],
        },
        "evidence_sources": {
            "h_decompiler": {"path": str(ENG_EVID.relative_to(REPO)), "sha256": sha(ENG_EVID.read_bytes())},
            "h_rx_diff": {"path": str(RX_DIFF.relative_to(REPO)), "sha256": sha(RX_DIFF.read_bytes())},
            "state_bridge": {"path": str(STATE.relative_to(REPO)), "sha256": sha(STATE.read_bytes())},
            "techstream_ready": {"path": str(TECH_READY.relative_to(REPO)), "sha256": sha(TECH_READY.read_bytes())},
            "techstream_cruise": {"path": str(TECH_CRUISE.relative_to(REPO)), "sha256": sha(TECH_CRUISE.read_bytes())},
            "public_route": {"path": str(PUBLIC.relative_to(REPO)), "sha256": sha(PUBLIC.read_bytes())},
            "span_route": {"path": str(SPAN.relative_to(REPO)), "sha256": sha(SPAN.read_bytes())},
        },
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    print(args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
