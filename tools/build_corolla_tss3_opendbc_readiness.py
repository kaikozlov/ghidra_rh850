#!/usr/bin/env python3
"""Build the Corolla TSS3 -> opendbc implementation-readiness artifact.

The builder intentionally joins different evidence classes without conflating
specimens:
- current upstream Toyota/openpilot prior art (role requirements),
- an externally attributed 2023 Corolla whole-vehicle public route,
- exact H/F EPS firmware analysis,
- the retained Span 2025 source-ZIP CAN capture, and
- Span's separately supplied moving/driving Discord rlog.

TSS generation and SecOC/TSK are modeled as orthogonal axes throughout.
"""
from __future__ import annotations

import argparse
import collections
import hashlib
import json
import zipfile
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[1]
DEFAULT_OUT = REPO / "data/generated/corolla_tss3_opendbc_readiness.json"
PUBLIC = REPO / "data/generated/corolla_2023_public_route_opendbc_evidence.json"
PRIOR = REPO / "data/external/opendbc/toyota_porting_contract.json"
COROLLA_PRIOR = REPO / "data/external/opendbc/toyota_corolla_pre_tss3_contract.json"
STATE = REPO / "data/generated/corolla_8965H1202000_openpilot_state_bridge.json"
B6 = REPO / "data/generated/corolla_8965H1202000_b6_receiver_contract.json"
B6_SECOC = REPO / "data/generated/corolla_8965H1202000_b6_secoc_verification.json"
LIMITS = REPO / "data/generated/corolla_hf_steering_limits.json"
CMD5 = REPO / "data/generated/corolla_hf_command5_portability.json"
CARRIER = REPO / "data/generated/corolla_hf_command5_runtime_carrier.json"
H_RUNTIME = REPO / "data/generated/ephemeral_runtime_target_manifest_8965H1202000.json"
SPAN_ZIP = REPO / "community/spanconstant/spanconstant_tsk.zip"
SPAN_MEMBER = "tsk/uds-sweep/ready_capture.ndjson"
SPAN_RLOG = REPO / "data/generated/corolla_2025_span_discord_rlog_opendbc_evidence.json"
ENGAGEMENT = REPO / "data/generated/corolla_hf_nonsteering_engagement_state.json"


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def rate(rows: list[tuple[float, str]]) -> float | None:
    if len(rows) < 2:
        return None
    span = rows[-1][0] - rows[0][0]
    return (len(rows) - 1) / span if span > 0 else None


def span_capture() -> dict[str, Any]:
    with zipfile.ZipFile(SPAN_ZIP) as zf:
        raw = zf.read(SPAN_MEMBER)
    by_key: dict[tuple[int, int, int], list[tuple[float, str]]] = collections.defaultdict(list)
    for line in raw.splitlines():
        if not line:
            continue
        row = json.loads(line)
        dat = row["data"]
        by_key[(int(row["bus"]), int(row["addr"]), len(bytes.fromhex(dat)))].append((float(row["t"]), dat))

    buses: dict[str, list[dict[str, Any]]] = {}
    for bus in sorted({k[0] for k in by_key}):
        rows = []
        for (b, addr, dlc), vals in sorted(by_key.items()):
            if b != bus:
                continue
            rows.append({
                "can_id": f"0x{addr:03X}",
                "dlc": dlc,
                "count": len(vals),
                "rate_hz": rate(vals),
                "first_payload": vals[0][1],
            })
        buses[str(bus)] = rows

    set0 = {(r["can_id"], r["dlc"]) for r in buses.get("0", [])}
    set2 = {(r["can_id"], r["dlc"]) for r in buses.get("2", [])}
    sequence_equal = True
    equality_by_id = []
    for can_id, dlc in sorted(set0 | set2):
        addr = int(can_id, 16)
        a = [x[1] for x in by_key.get((0, addr, dlc), [])]
        b = [x[1] for x in by_key.get((2, addr, dlc), [])]
        same = a == b
        sequence_equal &= same
        equality_by_id.append({"can_id": can_id, "dlc": dlc, "payload_sequence_equal": same})

    return {
        "source_zip": {
            "path": str(SPAN_ZIP.relative_to(REPO)),
            "sha256": sha256_file(SPAN_ZIP),
        },
        "member": {
            "path": SPAN_MEMBER,
            "sha256": sha256_bytes(raw),
            "size": len(raw),
            "line_count": len(raw.splitlines()),
        },
        "capture_mode_boundary": "The source investigation later concluded this file was probably captured Not Ready to Drive despite its ready_capture filename. Use it for static ID/DLC/cadence/topology structure only, not active-LTA or READY-state semantics.",
        "buses": buses,
        "bus0_bus2_same_id_dlc_set": set0 == set2,
        "bus0_bus2_payload_sequences_equal": sequence_equal,
        "bus0_bus2_equality_by_id": equality_by_id,
    }


def expand_hex_range(spec: str) -> set[int]:
    lo, hi = spec.split("..", 1)
    return set(range(int(lo, 16), int(hi, 16) + 1))


def row(role: str, status: str, old: str, tss3: str, evidence: str, blocker: str = "") -> dict[str, str]:
    return {
        "role": role,
        "status": status,
        "older_toyota_contract": old,
        "tss3_corolla_evidence": tss3,
        "evidence": evidence,
        "remaining_blocker": blocker,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", type=Path, default=DEFAULT_OUT)
    args = ap.parse_args()

    public = json.loads(PUBLIC.read_text())
    prior = json.loads(PRIOR.read_text())
    corolla_prior = json.loads(COROLLA_PRIOR.read_text())
    state = json.loads(STATE.read_text())
    b6 = json.loads(B6.read_text())
    b6_secoc = json.loads(B6_SECOC.read_text())
    limits = json.loads(LIMITS.read_text())
    cmd5 = json.loads(CMD5.read_text())
    carrier = json.loads(CARRIER.read_text())
    h_runtime = json.loads(H_RUNTIME.read_text())
    span = span_capture()
    span_rlog = json.loads(SPAN_RLOG.read_text())
    engagement = json.loads(ENGAGEMENT.read_text())
    if carrier["schema"] != "corolla-hf-command5-runtime-carrier-v1" or not carrier["boundary"]["static_target_native_carrier_candidate_closed"]:
        raise ValueError("H/F command5 carrier contract drift")
    if carrier["boundary"]["live_retention_closed"] or carrier["boundary"]["live_slot4_permission_closed"]:
        raise ValueError("static carrier artifact must not claim live closure")
    if engagement["schema"] != "corolla-hf-nonsteering-engagement-state-v1":
        raise ValueError("non-steering engagement contract schema drift")
    if not (engagement["ready_status"]["can_id"] == "0x51E" and engagement["ready_status"]["wire"] == "B0[7]"):
        raise ValueError("Ready Status engagement-contract drift")

    pub_set = {(r["can_id"], r["dlc"]) for r in public["bus0_canfd_baseline"]}
    span0_set = {(r["can_id"], r["dlc"]) for r in span["buses"]["0"]}
    span2_set = {(r["can_id"], r["dlc"]) for r in span["buses"]["2"]}
    span_rlog0_set = {(r["can_id"], r["dlc"]) for r in span_rlog["tss3_fd_network"]["bus0"]}
    span_rlog2_set = {(r["can_id"], r["dlc"]) for r in span_rlog["tss3_fd_network"]["bus2"]}
    old_tss2_radar_ids = set().union(*(expand_hex_range(x) for x in prior["radar_generation"]["tss2_track_id_ranges"]))
    pub_bus0_by_id = {int(r["can_id"], 16): r for r in public["bus0_canfd_baseline"]}
    radar_namespace_overlap = [pub_bus0_by_id[x] for x in sorted(set(pub_bus0_by_id) & old_tss2_radar_ids)]

    old_temp = prior["control_roles"]["steering_feedback"]["fault_contract"]["temporary_states"]
    old_perm = prior["control_roles"]["steering_feedback"]["fault_contract"]["permanent_states"]
    h_tx = [(x["can_id"], x["length"]) for x in state["h_tx_pdu_descriptors"]]
    h_secoc_rx = [(f"0x{int(x['can_id'], 16):03X}", x["secured_length"]) for x in h_runtime["secoc_records"]["records"]]
    route_h_visibility = public["route_vs_exact_h_f_visibility"]
    b6_request = b6["request_contract"]

    readiness = [
        row(
            "SecOC synchronization",
            "reusable_security_plumbing",
            "0x00F trip/reset/authenticator synchronization for Toyota SecOC profiles",
            "Public 2023 route carries 0x00F/8 on logical bus 1 at ~9.6 Hz; exact H/F SecOC queue contains 0x00F/8, 0x0D7/32 and 0x0B6/32. The route also exposes 0x0D7/32 but no 0x0B6 sample, without an exact H/F identity join.",
            "public route + exact H/F firmware",
            "Protected slot-4 signing access/key and upstream stock ownership remain open. The EPS receiver plus authenticated 0x00F now close a deterministic exclusive replacement-sender message8/re-anchor state machine, so Toyota's stock B6 counter policy is no longer required for receiver-valid freshness. SecOC presence says nothing about TSS generation.",
        ),
        row(
            "vehicle speed / wheel validity",
            "strong_reuse_candidate",
            "0x0AA WHEEL_SPEEDS and four wheel-fault bits feed CarState and Panda safety",
            "Public route has 0x0AA/8 at ~96 Hz; the old four wheel-speed fields decode coherently with all four fault bits zero. Span's moving Discord rlog independently carries 6,000 frames and the same four old fields track 0..~24 km/h with all fault bits zero. Exact H/F normal Rx also retains classic 0x0AA/8.",
            "public route + Span moving rlog raw decoding + exact H/F Rx descriptor",
            "Choose the physical safety bus and retain generation-specific validation rather than copying the whole old DBC.",
        ),
        row(
            "brake pressed",
            "strong_reuse_candidate",
            "SecOC Toyota uses 0x101 BRAKE_MODULE.BRAKE_PRESSED in CarState/Panda",
            "Public route has 0x101/8 at ~48 Hz and the old brake bit toggles 0/1. Span's moving rlog independently has 3,000/3,000 checksum-valid 0x101 frames with the same bit toggling. Exact H/F normal Rx retains 0x101/8.",
            "public route + Span moving rlog + exact H/F Rx descriptor",
            "Bus/relay placement remains a production-topology question, not a signal-layout blocker.",
        ),
        row(
            "gas pressed",
            "strong_reuse_candidate",
            "SecOC Toyota uses 0x116 GAS_PEDAL_USER",
            "Public route has protected 0x116/8 at ~41 Hz; the old GAS_PEDAL_USER field varies coherently. Span's moving rlog independently exercises the same old field from 0.00 to 0.73 across 2,548 frames.",
            "public route + Span moving rlog raw decoding",
            "This is whole-vehicle state and is not an EPS-local requirement; retain generation-specific validation.",
        ),
        row(
            "cruise engaged",
            "wire_reuse_dynamic_semantics_open",
            "SecOC Toyota Panda/CarState uses 0x176 PCM_CRUISE.CRUISE_ACTIVE/CRUISE_STATE",
            "Public route has 0x176/8 at ~30 Hz and all 1,855 frames pass the existing Toyota additive checksum. Span's moving rlog independently has 1,890/1,890 checksum-valid frames. Cruise remains inactive in both segments. 0x176 B0[3] is specifically rejected as a cruise replacement because it tracks accelerator-release/brake context in both captures.",
            "public route + Span moving rlog raw checksum + non-steering engagement contract",
            "Capture cruise main/engage/standstill transitions on a firmware-identified target before treating active/state values as production-ready.",
        ),
        row(
            "steering angle / rate",
            "reusable_signal_layout_new_fd_pdu",
            "Older Toyota uses 0x025/8 STEER_ANGLE/FRACTION/RATE",
            "TSS3 route uses 0x025/32 at ~96 Hz. Exact H firmware proves the legacy signed12 coarse, signed4 fraction and signed12 rate positions survive inside the 32-byte FD PDU; both the public route and Span's moving rlog decode dynamically under those positions.",
            "public route + Span moving rlog + exact H firmware + Techstream physical scale",
            "Define a TSS3 32-byte DBC message; do not use the old 8-byte message size.",
        ),
        row(
            "driver steering torque / actuator response",
            "driver_torque_closed_actuator_response_static",
            "Older Toyota uses 0x260 for driver torque, EPS torque, accurate angle and initialization; Panda torque safety samples it at 50 Hz",
            "0x260 is absent from the TSS3 routes. Exact H plus Techstream close live physical Steering Wheel Torque on 0x030 signals10+31; Span exercises 6000 frames and 536 values from -8.23 to +2.85 N.m. Exact H also closes 0x4A3 B5 as a 0.1 N.m/count alternate torque carrier and B6:B7 as -0.01 A/count Motor Actual Current (Q Axis), but current routes do not carry 0x4A3.",
            "exact H state bridge + Techstream physical conversion + Span moving-rlog 0x030 decode",
            "The expanded exact-H physical-torque census finds no driver-torque comparator in the target-to-motor control cone; choose a conservative Panda/openpilot driver-override policy and validate it dynamically. Capture 0x4A3 Q-current response under assist/control before finalizing any separate actuator-response policy.",
        ),
        row(
            "EPS readiness / steering faults",
            "generation_native_replacement_open_dynamic_join",
            f"Older Toyota uses 0x262 LKA/LTA states; temporary={old_temp}, permanent={old_perm}",
            "0x262 is absent from the TSS3 routes. Exact H closes 0x030 B6[2] as a live selected steering fault/inhibit status aggregate (nominal-clear 6000/6000; not an exhaustive EPS-fault state), 0x351 as a mixed status carrier with a C159B49-linked motor-B electrical-monitor base path plus a separate force-7 override, and 0x394 as a lossy 17-state fault/status projection whose state 0 is the deepest recovered clear/normal classifier path, not a proved Ready boolean. Exact H now also closes incoming 0x51E B0[7] as DID 0x1033 Ready Status; both retained operational routes show Ready=1, while Ready=0 remains uncaptured.",
            "exact H state bridge + non-steering engagement contract + Techstream DTC/DID joins + Span moving-rlog 0x030 polarity",
            "Correlate both 0x351 paths (C159B49-linked base status and force-7 override), 0x394, and a 0x51E Ready 1->0->1 transition against standby, stock LTA active, message loss, temporary fault and latched fault. Old numeric fault enums and temporary/permanent classes are not portable.",
        ),
        row(
            "gear",
            "strong_reuse_candidate_partial_dynamic",
            "Current SecOC Toyota CarState uses 0x127 GEAR_PACKET_HYBRID; older non-SecOC profiles use 0x3BC",
            "The public 2023 route lacks 0x127, but Span's moving Discord rlog carries 3,662 0x127/8 frames; all 3,662 pass the existing Toyota additive checksum and raw value 3 maps to D only through the retained Toyota prior-art GEAR enum. Embedded carParams is MOCK, so there is no independent gear-state oracle. Exact H retains 0x127/8 and its generated receive layout, but its scalar unpacker does not consume the legacy B5[3:0] gear nibble.",
            "Span moving rlog raw bytes + exact H receive layout + current opendbc prior art",
            "Obtain an independent gear-state oracle or explicit D transition, validate P/R/N/B transitions, and bind the capture to exact target firmware before declaring any target-native gear enum production-ready.",
        ),
        row(
            "cruise availability / set speed / ACC faults / follow distance",
            "diagnostic_oracles_closed_wire_mapping_open",
            "0x1D3 PCM_CRUISE_2 and 0x399 PCM_CRUISE_SM supply main availability, set speed, fault, lockout, distance and cluster set speed",
            "0x1D3/0x399 are absent from both retained routes; 0x177/0x1A2 are also absent. Techstream FRC_P5 supplies exact P5 Data-ID oracles: 0x1905 Cruise Control Permission, 0x1906 Main Switch Recognition / Set-Cancel / ACC Not Available icon, 0x1914 ACC Control in Operation, 0x1901 Current/Memory Vehicle Speed, and 0x1912 Set Vehicle Interval Time. These Data IDs are not automatically direct UDS RDBI DIDs.",
            "public route + Span moving rlog + exact Techstream FRC_P5 Data-ID semantics",
            "Synchronize all-bus CAN with Techstream/GTS+ FRC data-monitor transitions to identify generation-native CAN fields for available/enabled/set speed/fault/follow distance.",
        ),
        row(
            "brake hold / stability state",
            "same_id_layout_lead",
            "0x3B7 ESP_CONTROL supplies brake hold and TC-disabled state",
            "0x3B7/8 is present on the public route, but all old decoded state bits are static zero in this segment.",
            "public route",
            "Exercise brake hold/TC state before promoting field compatibility.",
        ),
        row(
            "AEB / FCW coexistence",
            "partially_visible_role_open",
            "Older Toyota observes PRE_COLLISION and PCS_HUD depending architecture",
            "0x283 PRE_COLLISION is absent; 0x411/8 PCS_HUD remains present at ~1 Hz but is static in the segment.",
            "public route",
            "Recover TSS3 AEB ownership/state and verify 0x411 semantics before longitudinal integration.",
        ),
        row(
            "lane / driver UI",
            "same_id_layout_lead",
            "0x412 LKAS_HUD is preserved/replaced by older Toyota CarController",
            "0x412/8 remains present at ~1 Hz with plausible old-layout fields, but no LTA/LDA/UI transition is exercised and ownership is not established.",
            "public route",
            "Capture stock LTA/LDA state and determine whether TSS3 openpilot must replace, mirror, or leave this producer intact.",
        ),
        row(
            "body / units / blinkers / doors / light stalk",
            "partial_reuse_only",
            "0x610/0x614/0x620/0x622 supply units, indicators, doors/belt/parking brake, and auto-high-beam state",
            "All four IDs/8-byte shapes remain present. 0x614 decodes left/none and 0x620 parking brake toggles, but 0x610 old UNITS decodes value 7 outside its old 1..4 domain and many other fields are static.",
            "public route",
            "Carry over only independently validated fields; do not reuse the whole old body DBC by ID.",
        ),
        row(
            "lateral command",
            "eps_receiver_replacement_freshness_and_static_carrier_closed_live_signer_open",
            "Pre-TSS3 Corolla uses 0x2E4 torque; secure Sienna prior art provides 0x2E4/0x131 protected command examples",
            f"Exact H/F replace them with protected FD 0x0B6: signal254 Target Lateral ID, signal255 signed target angle, signal261 modulo-64 sequence. Accepted active request IDs are {b6_request['accepted_active_requests']}; receiver loss cuts out after 7 foreground ticks / nominal 35 ms. An EPS-consumer minimal ID11 companion candidate and authenticated-0x00F replacement freshness state machine are now statically closed.",
            "exact H/F firmware + Techstream + audited static H/F command-5 carrier",
            "Still required for production: validate the minimal/stock B6 secondary-field template and cross-ECU effects, obtain a slot-4 signing primitive/key or live-validate the audited H/F command-5 carrier (inert canary first, then selector-4 permission/latency), establish stock sender cadence/physical route, and suppress the stock source on the relay-correct topology. Receiver-valid replacement freshness and H/F-native numeric limits are no longer static blockers. The public 2023 route is not an exact H/F join. Span's moving rlog sees 0x00F/0x0D7 but no B6; B6 absence remains only a no-stock-LTA-transition segment-level negative.",
        ),
        row(
            "radar / object state",
            "new_tss3_parser_required",
            "Older Toyota radar parser expects 0x123/7 status plus TSS2 0x180..0x19F/8 object halves",
            "Public TSS3 route has 0x123/16 and a 22-ID CAN-FD baseline including 0x180..0x18B/64 and 0x18C/48. Both the older Span UDS-sweep capture and Span's moving Discord rlog repeat exactly the same 22 ID/DLC set on buses 0/2; the moving rlog also has byte-identical bus0/bus2 payload sequences.",
            "2023 public route + Span static capture + Span moving rlog",
            "Recover field semantics and producer ownership before implementing a TSS3 RadarInterface. CAN ID reuse is not semantic continuity.",
        ),
        row(
            "longitudinal command / stock ACC ownership",
            "open_separate_architecture",
            "Older TSS2 uses 0x343; known SecOC profiles can move signed acceleration into 0x183/8 while preserving 0x343 coordination",
            "Public TSS3 route has no 0x343 and carries 0x183 as 64-byte CAN-FD in the 20-Hz FD family; this directly disproves old wire-shape transfer.",
            "public route + upstream prior art",
            "Identify TSS3 ACC producer, command fields/cadence, AEB/brake arbitration, authentication and stock-source suppression. This remains OQ-052.",
        ),
    ]

    tss3_fd = {
        "public_2023_bus0": public["bus0_canfd_baseline"],
        "span_2025_static": span,
        "span_2025_moving_discord_rlog": span_rlog["tss3_fd_network"],
        "cross_year_same_bus0_id_dlc_set": pub_set == span0_set,
        "cross_year_public_bus0_equals_span_bus2_id_dlc_set": pub_set == span2_set,
        "moving_span_matches_public_bus0_id_dlc_set": pub_set == span_rlog0_set,
        "moving_span_bus0_bus2_same_id_dlc_set": span_rlog0_set == span_rlog2_set,
        "cross_year_id_dlc_set": [
            {"can_id": can_id, "dlc": dlc}
            for can_id, dlc in sorted(pub_set & span0_set)
        ],
        "interpretation": "The same 22-ID/DLC FD network geometry appears in the public 2023 route, the older Span capture, and Span's independently supplied moving/driving rlog. The moving rlog upgrades persistence of this geometry beyond NRtD/static conditions, but still does not assign field semantics, producer ownership, or command roles.",
        "tss2_radar_track_namespace_overlap": {
            "upstream_ranges": prior["radar_generation"]["tss2_track_id_ranges"],
            "matching_tss3_bus0_pdus": radar_namespace_overlap,
            "matching_count": len(radar_namespace_overlap),
            "boundary": "These TSS3 FD arbitration IDs occupy comma's older TSS2 radar-track numeric namespace, but their DLC/packing is generation-broken. This is a radar/object-family search prior, not a semantic assignment or proof of producer ownership.",
        },
        "0x18A_disposition": "0x18A is one 64-byte ~20-Hz member of the broader 0x180..0x18B family and lies inside comma's older TSS2 radar-track namespace. That makes radar/object semantics a concrete competing prior to the community lateral-control label; neither interpretation is promoted until producer/field/authentication dataflow is independently joined.",
    }

    out = {
        "schema": "corolla-tss3-opendbc-readiness-v1",
        "axes": {
            "adas_control_generation": "TSS/TSS2/TSS3 describes ADAS/control ownership, messages and semantics.",
            "security_architecture": "SecOC/TSK describes the security/authentication architecture: message authentication, freshness, keying, and diagnostic/reprogramming security.",
            "orthogonality": "These axes are independent. All three tracked firmware dump families are SecOC/TSK evidence; that fact alone does not establish their TSS generation.",
        },
        "upstream_prior_art": {
            "canonical_commit": prior["repository"]["commit"],
            "current_upstream_checked_commit": corolla_prior["current_upstream_commit"],
            "current_upstream_checked": corolla_prior["current_upstream_checked"],
            "current_upstream_equivalence": corolla_prior["contract_equivalence"],
        },
        "specimen_boundaries": {
            "public_2023_route": public["source"]["identity_note"],
            "exact_h": state["images"]["corolla_h"],
            "exact_f": state["images"]["corolla_f"],
            "h_f_application_contract_same": state["images"]["corolla_f"]["application_byte_identical_to_h"],
            "exact_h_tx_pdus": h_tx,
            "exact_h_secoc_rx_pdus": h_secoc_rx,
            "public_route_vs_exact_h_f_visibility": route_h_visibility,
            "public_route_0x030_exact_h_f_rule_join": public["direct_reuse_evidence"]["0x030"],
            "span_moving_rlog": {
                "source": span_rlog["source"],
                "identity_boundary": span_rlog["source"]["identity_boundary"],
                "harness_observation_boundary": span_rlog["harness_observation_boundary"],
                "exact_h_f_visibility": span_rlog["exact_h_f_visibility"],
            },
            "command5_runtime_carrier": {
                "static_candidate": carrier["carrier_geometry"],
                "canary": carrier["runtime_candidates"]["inert_canary"],
                "proxy": carrier["runtime_candidates"]["fixed_b6_command5_proxy"],
                "boundary": carrier["boundary"],
            },
            "nonsteering_engagement_contract": {
                "ready_status": engagement["ready_status"],
                "gear": engagement["gear"],
                "cruise_wire_mapping_status": engagement["cruise"]["wire_mapping_status"],
                "cruise_diagnostic_transport_boundary": engagement["cruise"]["diagnostic_transport_boundary"],
            },
            "critical_warning": "Do not attribute exact H/F Tx/Rx state carriers to the public 2023 route: that route has no carFw, exposes 0x00F/0x0D7 but not B6 from H/F's three-PDU SecOC Rx set, and contains only 0x030 from H/F's five-PDU Tx set. It is not evidence of a complete exact-H/F EPS-bus mirror.",
        },
        "role_readiness": readiness,
        "tss3_fd_network": tss3_fd,
        "bus_and_suppression_boundary": {
            "current_toyota_safety_assumption": "Current Toyota Panda safety consumes its checked vehicle-state inputs on logical bus 0.",
            "public_route_observation": "The directly reusable 0x00F/0x025/0x0AA/0x101/0x116/0x176 state evidence in the public TSS3 route is on logical bus 1. That bus also exposes exact-H/F search-vocabulary 0x0D7 and 0x030, but not B6 or H/F's 0x351/0x394/0x4A3/0x4C8 Tx set.",
            "span_moving_observation": span_rlog["harness_observation_boundary"],
            "toyota_b_harness_fact": "Official Toyota-B hardware uses CAN0/CAN2 as the intercept-relay pair and CAN1 as a separate unsplit network. Panda harnessStatus=flipped is cable orientation, not a physical Toyota-B CAN0/CAN1 repin.",
            "diagnostic_vs_interception": "ELM327 param=1 + logical bus 1 attaches FDCAN2 to the normal harness CAN1 wires and is sufficient for direct/passive observation. A physical CAN0/CAN1 repin is still required to move that network onto the CAN0/CAN2 relay pair for normal comma interception, stock-source suppression, and side-of-relay producer attribution.",
            "consequence": "Span's missing physical repin explains why its rlog cannot establish production suppression topology; it does not by itself erase stock-CAN1 traffic from logical bus 1. B6's segment-level absence therefore remains a bounded observation, while its producer side and suppression point remain open until a relay-correct LTA transition capture is obtained.",
        },
        "forced_old_profile": public["forced_old_profile_result"],
        "implementation_readiness": {
            "can_scaffold_now": [
                "Add an explicit TSS3 control-generation axis independent of the existing SECOC security flag.",
                "Define a TSS3 0x025/32 DBC PDU carrying the firmware-proved steering angle/fraction/rate fields.",
                "Decode live 0x030 physical Steering Wheel Torque and its raw fault/validity gates without importing the legacy override threshold or 0x262 fault classes.",
                "Carry forward 0x0AA/0x101/0x116/0x176 only behind generation-specific validation; do not copy the entire old DBC, and do not relabel 0x176 B0[3] as cruise state.",
                "Expose incoming 0x51E B0[7] as target-native Ready Status for read-only observation without yet mapping Ready=0 to an openpilot fault/engagement policy.",
                "Scaffold 0x127 GEAR_PACKET_HYBRID only as a read-only reuse candidate: carrier/checksum/raw3 are observed and raw3 is prior-art-compatible with D, while target-native gear semantics remain gated on an independent oracle/transitions.",
                "Model exact H/F B6 signal254/255/261 receiver requirements, nominal 35-ms loss cutout, the EPS-consumer minimal ID11 companion candidate, and the authenticated-0x00F replacement freshness state machine without enabling live actuation.",
                "Create a new TSS3 radar/CAN-FD namespace rather than extending the old 8-byte TSS2 radar DBC by ID.",
            ],
            "blocks_production_lateral": [
                "Firmware-identified H/F-family capture with the Toyota-B CAN0/CAN1 network physically relay-correct and stock LTA exercised off -> active -> off.",
                "B6 stock/minimal secondary-field cross-ECU validation, stock sender cadence/physical route, and a working slot-4 signing path: key or the audited 462-byte H/F command-5 proxy after the 332-byte inert carrier canary proves live retention and selector-4 permission/latency is measured.",
                "Stock-source suppression/interception point on Toyota-B topology.",
                "Conservative Panda/openpilot driver-override policy dynamic validation, Q-current actuator-response policy if desired, Ready/fault transition mapping, and final relay-correct actuator validation. No Toyota EPS physical-driver-torque comparator remains to recover under the promoted static census.",
            ],
            "blocks_normal_carstate": [
                "Validate P/R/N/B transitions on the retained 0x127 GEAR_PACKET_HYBRID carrier and bind them to the exact target.",
                "Cruise CAN-field mapping for available/enabled/set speed/follow distance/ACC not-available state; exact FRC_P5 Data-ID oracles are already recovered and should be synchronized through Techstream/GTS+.",
                "Generation-native steering fault/readiness mapping; driver-torque physical scaling is already closed.",
                "Dynamic validation of retained body/UI fields used by openpilot.",
            ],
            "blocks_radar": [
                "TSS3 0x123/16 and 0x180-family FD field semantics, validity/status and object association.",
            ],
            "blocks_longitudinal": [
                "TSS3 ACC producer/ownership, command+feedback payload, cadence, integrity/authentication, AEB/brake coexistence and safe stock suppression (OQ-052).",
            ],
        },
        "highest_value_next_evidence": [
            "On an isolated exact-H/F bench target, run the audited 332-byte inert carrier canary first and require FEBFFB80 heartbeat progression before exposing the 462-byte fixed-36-byte command-5 proxy; then test live slot-4 permission and latency without vehicle actuation.",
            "Capture an exact H/F-family vehicle with carFw/F181 preserved, the Toyota-B CAN0/CAN1 network physically repinned onto the CAN0/CAN2 relay pair, and all buses logged during stock LTA off->active->off, steering input, cruise main/engage, brake/gas and P/R/N/D transitions; simultaneously record 0x51E Ready and the exact FRC_P5 Data-ID oracles through Techstream/GTS+.",
            "Acquire matched category-435 07B0 Brake/EPB firmware and 0792 FRC_P5 firmware; join planner state -> upstream FD traffic -> protected B6 -> EPS response and signer/freshness ownership.",
            "Use that firmware-identified relay-correct capture to choose TSS3 CarState/Panda input buses, validate 0x127 gear enums, and recover the missing 0x1D3/0x399/0x260/0x262 roles before implementing production safety.",
            "Treat longitudinal as a separate architecture and close OQ-052 rather than inferring it from lateral/FRC progress.",
        ],
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
