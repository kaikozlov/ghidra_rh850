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
import runpy
import zipfile
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[4]
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
DIRECT_CANARY = REPO / "exploit/ephemeral_runtime/corolla_hf_direct_canary.py"
DIRECT_COMMAND5 = REPO / "exploit/ephemeral_runtime/corolla_hf_direct_command5.py"
H_RUNTIME = REPO / "data/generated/ephemeral_runtime_target_manifest_8965H1202000.json"
SPAN_ZIP = REPO / "community/spanconstant/spanconstant_tsk.zip"
SPAN_MEMBER = "tsk/uds-sweep/ready_capture.ndjson"
SPAN_RLOG = REPO / "data/generated/corolla_2025_span_discord_rlog_opendbc_evidence.json"
ENGAGEMENT = REPO / "data/generated/corolla_hf_nonsteering_engagement_state.json"
POWER_GATE = REPO / "data/generated/corolla_8965H1202000_power_supply_monitor_gate.json"
AUTH_WIRE = REPO / "data/generated/corolla_hf_cooperative_authority_wire_visibility.json"
FAULT_STATE = REPO / "data/generated/corolla_hf_fault_state_contract.json"
REMAINING_STATUS = REPO / "data/generated/corolla_hf_remaining_status_contract.json"
ALBINO_ARCH = REPO / "community/albinoelephant/albinoelephant_discord_PORT_ARCHITECTURE.md"
GTS_REGISTRY = REPO / "data/generated/gtsplus_2026/toyota_diag_registry_camry_2026.json"


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


def find_gts_shift_position(registry: dict[str, Any], source: str, name: str) -> dict[str, Any]:
    """Return one exact GTS+ signal record without depending on catalog numbering."""
    stack: list[Any] = [registry]
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
    direct_canary_ns = runpy.run_path(str(DIRECT_CANARY))
    direct_canary = direct_canary_ns["build_plan"]()
    direct_command5_ns = runpy.run_path(str(DIRECT_COMMAND5))
    direct_command5 = direct_command5_ns["build_plan"]()
    h_runtime = json.loads(H_RUNTIME.read_text())
    span = span_capture()
    span_rlog = json.loads(SPAN_RLOG.read_text())
    engagement = json.loads(ENGAGEMENT.read_text())
    fault_state = json.loads(FAULT_STATE.read_text())
    remaining_status = json.loads(REMAINING_STATUS.read_text())
    power_gate = json.loads(POWER_GATE.read_text())
    auth_wire = json.loads(AUTH_WIRE.read_text())
    albino_arch = ALBINO_ARCH.read_text()
    gts_registry = json.loads(GTS_REGISTRY.read_text())
    gts_hv_gear = find_gts_shift_position(gts_registry, "HV_P5.ddb", "Shift Position")
    expected_gts_gear = {"0": "P", "2": "R", "4": "N", "6": "D", "8": "B"}
    if gts_hv_gear["signal_info"]["pattern_display"] != expected_gts_gear:
        raise ValueError("GTS+ P5 hybrid shift-position semantics drift")
    for marker in (
        "0x160 is protected by a keyless CRC",
        "modify-and-forward",
        "Longitudinal (follow, speed, stop-and-go to 0 + hold, resume): VALIDATED on car",
        "Lateral: IN PROGRESS",
    ):
        if marker not in albino_arch:
            raise ValueError(f"retained Albino architecture boundary drift: {marker}")
    if carrier["schema"] != "corolla-hf-command5-runtime-carrier-v1" or not carrier["boundary"]["static_target_native_carrier_candidate_closed"]:
        raise ValueError("H/F command5 carrier contract drift")
    if carrier["boundary"]["live_retention_closed"] or carrier["boundary"]["live_slot4_permission_closed"]:
        raise ValueError("static carrier artifact must not claim live closure")
    if direct_canary["schema"] != "corolla-hf-direct-canary-v1" or direct_canary["mode"] != "plan":
        raise ValueError("H/F direct-canary plan schema drift")
    if direct_canary["package"]["payload_sha256"] != "313d1bb70fe6147c179e4b5a35e4556e536f062a80d53d85af3d4292b0b29d84":
        raise ValueError("H/F direct-canary package drift")
    if direct_canary["success_gate"]["command5_proxy_authorized_by_this_plan"] is not False:
        raise ValueError("H/F direct-canary must not authorize command5")
    if direct_command5["schema"] != "corolla-hf-direct-command5-v1" or direct_command5["mode"] != "plan":
        raise ValueError("H/F direct-command5 plan schema drift")
    if direct_command5["package"]["payload_sha256"] != "a94979704010758dd09acc0e137977c8eed5003822eababa39eb8a7e5e9d5a58":
        raise ValueError("H/F direct-command5 package drift")
    if not direct_command5["live_guards"]["successful_canary_result_required"] or not direct_command5["live_guards"]["reset_to_stock_confirmation_required"]:
        raise ValueError("H/F direct-command5 must remain gated behind canary/reset proof")
    if engagement["schema"] != "corolla-hf-nonsteering-engagement-state-v1":
        raise ValueError("non-steering engagement contract schema drift")
    if fault_state["schema"] != "corolla-hf-0x394-fault-state-contract-v1" or remaining_status["schema"] != "corolla-hf-remaining-status-contract-v1":
        raise ValueError("remaining H/F static-state contract drift")
    if not (engagement["ready_status"]["can_id"] == "0x51E" and engagement["ready_status"]["wire"] == "B0[7]"):
        raise ValueError("Ready Status engagement-contract drift")
    if power_gate["schema"] != "corolla-8965H1202000-power-supply-monitor-gate-v1":
        raise ValueError("power-supply gate artifact drift")
    if auth_wire["schema"] != "corolla-hf-cooperative-authority-wire-visibility-v1":
        raise ValueError("cooperative-authority wire artifact drift")
    if power_gate["classification"]["distinct_from_b6_loss"] != "B6 missing-message loss remains the separate FEBEADB9 -> FEBEC26D path.":
        raise ValueError("power gate/B6-loss separation drift")
    if auth_wire["static_conclusion"]["exact_wire_visible_cooperative_authority_bit_recovered"] is not False:
        raise ValueError("cooperative authority wire boundary drift")

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
            "generation_native_can_closed",
            "Older Toyota uses 0x176 PCM_CRUISE.CRUISE_ACTIVE/CRUISE_STATE",
            "0x176 is explicitly rejected as the TSS3 engagement source: its old active/state fields stay inactive and B0[3] tracks accelerator-release/brake context. Span's retained 2025 rlog directly closes 0x08A B22 bit 0x10 instead: 2,363 clear frames are all ACC_STATE=0x12 and 37 asserted frames are all ACC_STATE=0x5D. Albino's validated longitudinal implementation independently uses the same 0x08A engaged bit for host and Panda gating.",
            "Span moving rlog + retained Albino on-car longitudinal implementation",
            "No core CarState engagement-field blocker remains; exact-target replay remains the normal final validation step.",
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
            "0x262 is absent from the TSS3 routes. Exact H closes 0x030 B6[2] as a live selected steering fault/inhibit status aggregate (nominal-clear 6000/6000; not exhaustive), and now closes B6[1] to a Motor Actual Current (Q Axis)-derived threshold/debounce chain whose exact-H detector is calibration-disabled. 0x351 is a mixed carrier with a C159B49-linked base path plus a separate force-7 override now traced to status-bitmap bits0/1 AND bit15 of a 24-record aggregate. 0x394 is a 17-state projection whose 242 populated-class DEM events are exhaustively partitioned: class 0x02 -> states 6/7, class 0x04 -> 8/9, class 0x10 -> 10, class 0x20/F0-compatible aggregate -> 11, class 0x40 -> 12, class 0x08 -> 13, class 0x0F -> 14, with exact 200/600-count latch-aging structure; named Toyota DTC families are joined where H carries a DTC index. State 0 remains the deepest clear/normal path, not a Ready boolean. Incoming 0x51E B0[7] is DID 0x1033 Ready Status; retained operational routes show Ready=1, while Ready=0 remains uncaptured. Separately, FEBE7C58->FEBEF000->FEBEACBD is a graded power-supply receive-validity/freeze gate, distinct from B6 loss, and the related 0x030 B6[3]/B10[3]/B13[4] path carries only a coarse raw-mode<2 aggregate that cannot represent exact cooperative authority.",
            "exact H state bridge + non-steering engagement contract + Techstream DTC/DID joins + Span moving-rlog 0x030 polarity",
            "Static class/DTC/source mapping is now closed; remaining work is operational policy. Capture 0x351/0x394 plus a 0x51E Ready 1->0->1 transition during recoverable versus latched faults and stock-LTA disable/recovery to decide openpilot temporary/permanent policy. Old numeric fault enums are not portable.",
        ),
        row(
            "gear",
            "generation_native_carstate_closed",
            "Current SecOC Toyota CarState uses 0x127 GEAR_PACKET_HYBRID; older non-SecOC profiles use 0x3BC",
            "The public 2023 Corolla route directly observes 0x3BF byte0 transitions 0x80=P -> 0x40=R -> 0x10=D, with independent 0x2A1 byte4 transitions 1=P -> 2=R -> 4=D at the same boundaries. Span's moving 2025 segment independently carries 0x3BF=0x10 while driving and 3,662 checksum-valid 0x127 frames at raw3. N=0x20 completes the 0x3BF one-hot domain and Toyota GTS+ HV_P5 independently preserves the P/R/N/D/B ordinal ordering. Production CarState can therefore use 0x127 on the retained hybrid shape and 0x3BF as the generation-native fallback.",
            "2023 public route direct transitions + Span moving rlog + GTS+ HV_P5 Shift Position",
            "No core gear-state blocker remains; unexercised 0x127 P/R/N/B values retain Toyota's established enum rather than a new TSS3 inference.",
        ),
        row(
            "cruise availability / set speed / ACC faults / follow distance",
            "core_carstate_closed_optional_acc_ui_open",
            "0x1D3 PCM_CRUISE_2 and 0x399 PCM_CRUISE_SM supply main availability, set speed, fault, lockout, distance and cluster set speed",
            "The old 0x1D3/0x399 family is absent. Core TSS3 CarState is instead generation-native: 0x08A ACC_STATE is nonzero in retained idle/engaged states, B22 bit0x10 is the direct engaged gate, and contributor live drives identify ACC_STATE bit0x20/0x67 as standstill hold. Retained contributor evidence identifies 0x251 byte2 as the dash set speed in mph and the validated on-car port reports a 19-mph set-speed floor. GTS+ FRC_P5 independently provides the diagnostic semantic oracles 0x1901/0x1905/0x1906/0x1912/0x1914. Follow-distance and detailed ACC-unavailable UI state remain optional unmapped fields, not base-control blockers.",
            "Span moving rlog + retained Albino live-drive evidence + GTS+ FRC_P5 semantics",
            "Optional follow-distance and detailed ACC-unavailable UI mapping remain open; they are not required for base engagement, set speed, standstill, or actuation.",
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
            "optional_parser_not_required_for_base_port",
            "Older Toyota radar parser expects 0x123/7 status plus TSS2 0x180..0x19F/8 object halves",
            "Public TSS3 route has 0x123/16 and a 22-ID CAN-FD baseline including 0x180..0x18B/64 and 0x18C/48. Both the older Span UDS-sweep capture and Span's moving Discord rlog repeat exactly the same 22 ID/DLC set on buses 0/2; the moving rlog also has byte-identical bus0/bus2 payload sequences.",
            "2023 public route + Span static capture + Span moving rlog",
            "The base port should keep radarUnavailable/model-lead operation. Recover this namespace only if a native TSS3 RadarInterface is desired; CAN ID reuse is not semantic continuity.",
        ),
        row(
            "longitudinal command / stock ACC ownership",
            "stock_owned_shared_08a_request_plane_source_ownership_open",
            "Older TSS2 uses 0x343; Toyota's TSS3 vehicle-movement architecture instead separates application request, selected/result, and controller-target planes",
            "The old 0x343 wire contract does not transfer, and the retained contributor 0x160 modify-and-forward result no longer establishes command ingress. Cross-generation TSS3 recovery identifies 0x08A as the shared application-request plane: its two packed longitudinal request-ID/allocation bytes accompany two signed16 acceleration requests at 0.001 m/s²/count while the same PDU carries the lateral request tuple. Span's 37 retained ACC-engaged frames are request A ID17/allocation3 plus request B ID23/allocation1; their two acceleration slots are equal frame-for-frame and sweep 15 values from -0.387 to +0.082 m/s². Native 0x160 remains useful FRC-origin Profile-5 state/evidence but is not qualified as a writable longitudinal actuator contract.",
            "retained Corolla 0x08A road traffic + cross-generation Camry/Toyota request-result architecture + historical Albino 0x160 field experiment",
            "Keep Toyota stock longitudinal authoritative. A native-long port first needs a qualified 0x08A source-suppression/sole-emitter boundary or equivalent pre-signing handoff on the unsplit Toyota-B network, then Brake/PCS/AEB coexistence and result-plane validation. Do not revive the 0x160 encoder from the historical field experiment.",
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
                "native_acc_gate": span_rlog["direct_reuse_evidence"]["0x08A_acc"],
                "gear_0x3bf": span_rlog["direct_reuse_evidence"]["0x3BF"],
            },
            "public_route_gear": {
                "0x3BF": public["direct_reuse_evidence"]["0x3BF"],
                "0x2A1": public["direct_reuse_evidence"]["0x2A1"],
            },
            "gts_p5_hybrid_shift_position": {
                "source": gts_hv_gear["source"],
                "name": gts_hv_gear["name"],
                "pattern_display": gts_hv_gear["signal_info"]["pattern_display"],
            },
            "retained_albino_longitudinal": {
                "path": str(ALBINO_ARCH.relative_to(REPO)),
                "sha256": sha256_file(ALBINO_ARCH),
                "validated_status": "Longitudinal (follow, speed, stop-and-go to 0 + hold, resume): VALIDATED on car",
                "boundary": "Use the retained contributor architecture as historical evidence for the reported on-car longitudinal behavior plus 0x160 topology/E2E observations. The September-16 cross-system request-plane recovery supersedes the inference that 0x160 itself is authoritative longitudinal command ingress. Its own status also says lateral remained IN PROGRESS, so it is not evidence for any later 0x160/0x1A0 steering claim.",
            },
            "command5_runtime_carrier": {
                "static_candidate": carrier["carrier_geometry"],
                "canary": carrier["runtime_candidates"]["inert_canary"],
                "proxy": carrier["runtime_candidates"]["fixed_b6_command5_proxy"],
                "direct_canary": {
                    "tool": str(DIRECT_CANARY.relative_to(REPO)),
                    "target": direct_canary["target"],
                    "package": direct_canary["package"],
                    "field_proven_bootstrap": direct_canary["field_proven_bootstrap"],
                    "success_gate": direct_canary["success_gate"],
                    "boundary": direct_canary["boundary"],
                },
                "direct_command5": {
                    "tool": str(DIRECT_COMMAND5.relative_to(REPO)),
                    "target": direct_command5["target"],
                    "package": direct_command5["package"],
                    "probe": direct_command5["probe"],
                    "live_guards": direct_command5["live_guards"],
                },
                "boundary": carrier["boundary"],
            },
            "nonsteering_engagement_contract": {
                "ready_status": engagement["ready_status"],
                "gear": engagement["gear"],
                "cruise_wire_mapping_status": engagement["cruise"]["wire_mapping_status"],
                "cruise_diagnostic_transport_boundary": engagement["cruise"]["diagnostic_transport_boundary"],
            },
            "power_supply_cooperative_gate": {
                "state_chain": power_gate["state_chain"],
                "classification": power_gate["classification"],
            },
            "cooperative_authority_wire_visibility": {
                "positive_coarse_mode_wire_path": auth_wire["positive_coarse_mode_wire_path"],
                "exact_authority_negative": auth_wire["exact_authority_negative"],
                "five_pdu_boundary": auth_wire["five_pdu_boundary"],
            },
            "fault_state_contract": {
                "class_counts": fault_state["dem"]["class_counts"],
                "class_to_state": fault_state["dem"]["class_to_state"],
                "aging": fault_state["aging"],
                "openpilot_boundary": fault_state["openpilot_boundary"],
            },
            "remaining_status_contract": {
                "can_0x030_b6_bit1": remaining_status["can_0x030_b6_bit1"],
                "can_0x351_force7": remaining_status["can_0x351_force7"],
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
            "implemented_from_retained_evidence": [
                "Generation-specific TSS3 platform selection, Toyota-B bus placement, and exact Corolla EPS firmware matching.",
                "0x025/32 steering angle/rate, 0x030 driver torque/validity, 0x0AA wheel speed, 0x101 brake, 0x116 gas, 0x51E Ready Status, and generation-native Corolla gear parsing (0x127 hybrid shape with 0x3BF fallback).",
                "0x08A native ACC available/enabled/standstill state and 0x251 retained set-speed decode, with the native 19-mph set-speed floor and manual resume from stock hold.",
                "Shared 0x08A longitudinal request geometry and native ACC state are decoded; historical 0x160 modify-and-forward remains evidence only. Runtime keeps Toyota stock longitudinal authoritative and does not synthesize or suppress 0x160.",
                "Exact H/F B6 lateral receiver contract, target-angle scaling, request profile, freshness reconstruction, native angle limits, bounded host sideband, and Panda angle safety for the EPS-resident signer design.",
                "Model-lead/radarUnavailable base operation; a native TSS3 radar parser is optional rather than a Corolla port prerequisite.",
            ],
            "blocks_production_lateral": [
                "Live same-car validation of the retained EPS-resident signer/helper: confirm command-5 carrier retention/slot-4 signing, native B6 output, and steering response on the exact Corolla H/F family before treating host-side completion as production actuation proof.",
                "Relay-correct stock-LTA off -> active -> off capture to close the physical stock B6 producer/suppression point and confirm the minimal secondary-field template under real cooperative steering.",
                "Conservative Panda/openpilot driver-override dynamic validation and final Ready/fault recovery policy. Exact target-angle, receiver freshness, steering limits, driver-torque telemetry, 0x394 DEM classes, and 0x351 source topology are already statically closed.",
            ],
            "blocks_normal_carstate": [
                "Operational steering-fault/readiness policy only: capture Ready=0 and recoverable-versus-latched fault transitions before mapping TSS3 native states into openpilot temporary/permanent fault classes.",
                "Optional body/UI fields that were static in retained routes should remain unmapped or prior-art-only until exercised; they are not actuation blockers.",
            ],
            "blocks_radar": [
                "Only a future native RadarInterface is blocked on 0x123/16 and 0x180-family FD semantics. The base Corolla port intentionally uses radarUnavailable/model leads.",
            ],
            "blocks_longitudinal": [
                "Recover a clean 0x08A source-ownership boundary on stock Toyota-B (source suppression/sole emitter or an equivalent pre-signing handoff), then validate selected/result behavior and PCS/AEB priority before enabling native longitudinal. The historical 0x160 modify-and-forward path is not a production candidate.",
            ],
        },
        "highest_value_next_evidence": [
            "On the isolated exact H/F specimen, run exploit/ephemeral_runtime/corolla_hf_direct_canary.py first, then the guarded selector-4 command-5 probe after reset-to-stock confirmation; this is the remaining live prerequisite for the EPS-resident B6 signer used by the openpilot branch.",
            "On the vehicle, preserve F181 and capture the relay-correct stock-LTA off -> active -> off transition, then validate that the resident helper emits native authenticated B6 and that EPS response follows openpilot's bounded target-angle sideband.",
            "Recover the physical Corolla 0x08A producer/pre-signing path and establish how openpilot could become the sole qualified request source without competing on the unsplit network; only then stage native-long and PCS/AEB coexistence validation.",
            "Capture Ready=0 plus recoverable and latched steering faults to finish openpilot temporary/permanent fault policy. Gear, core cruise state, set speed, driver torque, and longitudinal request semantics are no longer evidence blockers; request-source ownership remains open.",
            "Recover the 0x123/0x180-family radar FD semantics only if a native TSS3 RadarInterface is desired; model-lead operation does not depend on it.",
        ],
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
