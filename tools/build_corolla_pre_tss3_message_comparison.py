#!/usr/bin/env python3
"""Compare pre-TSS3 Corolla openpilot roles with the tracked 2023/2025 EPS images.

The upstream Corolla contract is a tracked, externally-corroborated snapshot.
Firmware conclusions are rebuilt from exact CodeFlash bytes plus existing
H-target semantic evidence. Absence of whole-vehicle messages from an EPS image
is explicitly non-diagnostic unless the old role was EPS-local.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import struct
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from tools.build_ephemeral_runtime_manifest import load_codeflash  # noqa: E402
from tools.compare_variant_application_rx import find_normal_rx_descriptor_table  # noqa: E402

SCHEMA = "corolla-pre-tss3-opendbc-message-comparison-v5"
TX = struct.Struct("<IBBH")
PDU = struct.Struct("<HBBHBB")

DEFAULT_H = REPO / "community/albinoelephant/normalized/8965H1202000_CodeFlash.bin"
DEFAULT_F = REPO / "community/spanconstant/raw-20260821/span-corolla-2025.20260821-1511/dump_codeflash_00000000_00200000_20260821-152033.bin"
DEFAULT_CONTRACT = REPO / "data/external/opendbc/toyota_corolla_pre_tss3_contract.json"
DEFAULT_FD = REPO / "data/generated/corolla_8965H1202000_fd_control_interface.json"
DEFAULT_LTA = REPO / "data/generated/corolla_8965H1202000_lta_command_provenance.json"
DEFAULT_EQ = REPO / "data/generated/corolla_8965F1208000_vs_8965H1202000_codeflash_equivalence.json"
DEFAULT_BRIDGE = REPO / "data/generated/corolla_8965H1202000_openpilot_state_bridge.json"
DEFAULT_OUT = REPO / "data/generated/corolla_pre_tss3_opendbc_message_comparison.json"


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def rx_rows(image: bytes) -> tuple[int, list[dict]]:
    start, records = find_normal_rx_descriptor_table(image)
    rows = []
    for i, (software_id, length) in enumerate(records):
        rows.append({
            "index": i,
            "can_id": f"0x{software_id & 0x7FF:03X}",
            "length": length,
            "can_fd": bool(software_id & 0x40000000),
            "software_id": f"0x{software_id:08X}",
        })
    return start, rows


def tx_rows(image: bytes) -> list[dict]:
    raw = [TX.unpack_from(image, 0x21F04 + i * TX.size)[0] for i in range(5)]
    return [
        {"can_id": f"0x{x & 0x7FF:03X}", "can_fd": bool(x & 0x40000000), "software_id": f"0x{x:08X}"}
        for x in raw
    ]


def by_id(rows: list[dict]) -> dict[str, dict]:
    return {row["can_id"]: row for row in rows}


def role_row(*, role: str, old: dict, new: dict, classification: str, consequence: str, scope: str = "eps-local") -> dict:
    return {
        "role": role,
        "scope": scope,
        "pre_tss3": old,
        "corolla_h_f": new,
        "classification": classification,
        "porting_consequence": consequence,
    }


def build(args: argparse.Namespace) -> dict:
    h, h_source = load_codeflash(args.h_image)
    f, f_source = load_codeflash(args.f_image)
    contract = json.loads(args.contract.read_text())
    fd = json.loads(args.fd_control.read_text())
    lta = json.loads(args.lta_provenance.read_text())
    eq = json.loads(args.equivalence.read_text())
    bridge = json.loads(args.state_bridge.read_text())
    if bridge["schema"] != "corolla-8965H1202000-openpilot-state-bridge-v6":
        raise ValueError("openpilot state/command bridge schema drift")

    if len(h) != 0x100000 or len(f) != 0x100000:
        raise ValueError("normalized CodeFlash must be 1 MiB")
    app_slice = slice(0x20000, 0x100000)
    if h[app_slice] != f[app_slice]:
        raise ValueError("2023 H and 2025 F application regions are not byte-identical")
    if eq["application_equivalence"]["different_bytes"] != 0:
        raise ValueError("tracked equivalence artifact disagrees with raw application equality")

    h_rx_start, h_rx = rx_rows(h)
    f_rx_start, f_rx = rx_rows(f)
    if h_rx != f_rx or h_rx_start != f_rx_start:
        raise ValueError("H/F application Rx configuration diverges despite equal application bytes")
    h_tx = tx_rows(h)
    f_tx = tx_rows(f)
    if h_tx != f_tx:
        raise ValueError("H/F application Tx configuration diverges despite equal application bytes")
    if h_tx != [
        {"can_id": "0x030", "can_fd": True, "software_id": "0x40000030"},
        {"can_id": "0x351", "can_fd": False, "software_id": "0x00000351"},
        {"can_id": "0x394", "can_fd": False, "software_id": "0x00000394"},
        {"can_id": "0x4A3", "can_fd": False, "software_id": "0x000004A3"},
        {"can_id": "0x4C8", "can_fd": False, "software_id": "0x000004C8"},
    ]:
        raise ValueError(f"unexpected H/F Tx table: {h_tx}")
    pdu0 = PDU.unpack_from(h, 0x22620)
    if pdu0 != (2, 0, 0, 32, 0, 3):
        raise ValueError(f"unexpected FD030 PDU descriptor: {pdu0}")

    rx = by_id(h_rx)
    tx = by_id(h_tx)
    def rx_fact(can_id: str) -> dict | None:
        row = rx.get(can_id)
        return None if row is None else {"direction": "rx", "length": row["length"], "can_fd": row["can_fd"], "descriptor_index": row["index"]}
    def tx_fact(can_id: str) -> dict | None:
        row = tx.get(can_id)
        if row is None: return None
        out = {"direction": "tx", "can_fd": row["can_fd"]}
        if can_id == "0x030": out["length"] = pdu0[3]
        return out

    profiles = contract["profiles"]
    old_025 = {"id": "0x025", "name": "STEER_ANGLE_SENSOR", "length": 8, "profiles": list(profiles)}
    old_0aa = {"id": "0x0AA", "name": "WHEEL_SPEEDS", "length": 8, "profiles": list(profiles)}
    old_260 = {"id": "0x260", "name": "STEER_TORQUE_SENSOR", "length": 8, "profiles": list(profiles)}
    old_262 = {"id": "0x262", "name": "EPS_STATUS", "length_by_profile": {"corolla_2017_2019": 5, "corolla_tss2_2020_2022": 8}}
    old_2e4 = {"id": "0x2E4", "name": "STEERING_LKA", "length": 5, "profiles": list(profiles), "role": "active torque steering command", "cadence_hz": 100}
    old_191 = {"id": "0x191", "name": "STEERING_LTA", "length": 8, "profiles": ["corolla_tss2_2020_2022"], "role": "neutral/inactive replacement under Corolla torque control", "cadence_hz": 50}

    shared_025 = lta["shared_can025_sensor_ingress"]
    if shared_025["can_id"] != "0x025" or shared_025["classification"] != "shared-command-sized-ingress-is-steering-angle-sensor-state":
        raise ValueError("0x025 semantic evidence drifted")
    fd030 = fd["fd_0x030_transmit"]
    if fd030["corolla_h_tx_ids"][0] != "0x030" or fd030["pdu0_descriptor"]["length"] != 32:
        raise ValueError("FD030 evidence drifted")

    roles = [
        role_row(
            role="steering_angle_and_rate_input",
            old=old_025,
            new={**rx_fact("0x025"), "id": "0x025", "target_native_semantics": "signed-12 coarse angle + signed-4 fraction + signed-12 rate; H recombines angle/fraction and independently consumes rate magnitude"},
            classification="same_id_role_continuity_wire_migrated_to_can_fd",
            consequence="Keep 0x025 as a high-confidence semantic anchor, but build a generation-specific 32-byte CAN-FD definition; do not reuse the old 8-byte bit layout blindly.",
        ),
        role_row(
            role="wheel_speed_input",
            old=old_0aa,
            new={**rx_fact("0x0AA"), "id": "0x0AA"},
            classification="same_id_same_length_configured_continuity_semantics_not_reproved_here",
            consequence="0x0AA is a strong capture/DBC starting point because ID and 8-byte classic descriptor survive, but exact old field offsets remain a separate target-native validation task.",
        ),
        role_row(
            role="driver_eps_torque_and_accurate_angle_feedback",
            old=old_260,
            new={
                "old_id_present_in_tx": tx_fact("0x260") is not None,
                "generation_native_carriers": ["0x4A3", "0x030"],
                "0x4A3": bridge["state_bridge"]["0x4A3"],
                "0x030_classification": bridge["state_bridge"]["0x030"]["classification"],
            },
            classification="old_eps_tx_removed_roles_split_across_newer_state_carriers",
            consequence="Use 0x4A3 as the clearest H/F angle, driver-torque-source, and motor-response bridge, then decode only the remaining 0x030 validity/state needed for CarState/Panda safety. Do not assume old 0x260 torque scaling.",
        ),
        role_row(
            role="eps_lka_readiness_and_fault_feedback",
            old=old_262,
            new={
                "old_id_present_in_tx": tx_fact("0x262") is not None,
                "generation_native_candidates": ["0x351", "0x394", "0x030"],
                "0x351": bridge["state_bridge"]["0x351"],
                "0x394": bridge["state_bridge"]["0x394"],
            },
            classification="old_eps_status_tx_removed_status_roles_split_across_newer_carriers",
            consequence="Correlate 0x351/0x394 against normal, active, inhibit, and fault transitions; use 0x030 only for remaining validity holes. Old numeric LKA_STATE values are not portable.",
        ),
        role_row(
            role="active_lateral_steering_command",
            old=old_2e4,
            new={
                "old_id_active_rx": rx_fact("0x2E4"),
                "secured_profiles": ["0x00F", "0x0D7", "0x0B6"],
                "replacement": bridge["command_ingress_closure"]["b6_target_angle"],
                "static_conclusion": bridge["command_ingress_closure"]["static_conclusion"],
            },
            classification="old_torque_command_replaced_by_protected_b6_target_angle_control",
            consequence="Do not extend/sign classic 0x2E4. H/F instead consume protected FD 0x0B6 signal255 as a target steering-angle command, with signal254 selecting cooperative-control profiles. The controller-equivalent signal255 scale is 1024/17870 deg/count (~1.000121519 mrad/count), and Techstream Target Lateral ID closes profiles 1/4/10/11/19 as PCS/LDA/Hands Off LTA/LTA-LCA/PDA. Receiver-side request selection, the 7-tick loss cutoff, and modulo-64 sequence rules are closed; recover the exact OEM signal255 unit, wall-clock sender cadence, SecOC freshness/key behavior, and stock-source suppression before injection.",
        ),
        role_row(
            role="tss2_lta_coexistence_frame",
            old=old_191,
            new={"old_id_active_rx": rx_fact("0x191")},
            classification="old_neutral_tss2_replacement_removed",
            consequence="0x191 was not Corolla TSS2's active steering actuator path in openpilot; its disappearance is not evidence for a missing angle-command replacement.",
        ),
        role_row(
            role="longitudinal_command_and_stock_source_replacement",
            old={"id": "0x343", "name": "ACC_CONTROL", "tss2":"active 33.3 Hz openpilot longitudinal replacement of camera source", "pre_tss2":"cancel-only"},
            new={"eps_rx": rx_fact("0x343"), "eps_tx": tx_fact("0x343")},
            classification="not_eps_local_absence_non_diagnostic",
            consequence="The EPS dump cannot answer the TSS3 longitudinal question. Analyze/capture the FRC/radar/brake/gateway ownership path separately.",
            scope="whole-vehicle",
        ),
        role_row(
            role="lkas_hud_and_lane_ui_replacement",
            old={"id": "0x412", "name": "LKAS_HUD", "length": 8, "cadence_hz": 5, "source_state":"camera bus 2"},
            new={"eps_rx": rx_fact("0x412"), "eps_tx": tx_fact("0x412")},
            classification="not_eps_local_absence_non_diagnostic",
            consequence="Recover TSS3 camera/cluster UI separately; no conclusion follows from 0x412 being absent from EPS application tables.",
            scope="whole-vehicle",
        ),
    ]

    old_core_ids = ["0x025","0x0AA","0x224","0x226","0x260","0x262","0x2E4","0x191","0x343","0x412"]
    inventory = []
    for cid in old_core_ids:
        inventory.append({"can_id": cid, "h_f_rx": rx_fact(cid), "h_f_tx": tx_fact(cid)})

    return {
        "schema": SCHEMA,
        "evidence_boundary": (
            "The 2023 H and 2025 F conclusions are exact application CodeFlash facts plus target-native fixed-map/dataflow proofs. "
            "Whole-vehicle openpilot messages may legitimately be absent from an EPS image; only EPS-local command/feedback migrations are treated as architectural evidence. B6 controller-equivalent physical scaling, signal254 feature/request selection, the 7-tick receiver loss cutoff, and modulo-64 sequence handling are closed; the exact OEM signal255 unit, wall-clock sender cadence, exact secondary-field names, and upstream producer/authentication remain open."
        ),
        "upstream": {
            "contract": str(args.contract.relative_to(REPO)),
            "canonical_commit": contract["canonical_commit"],
            "current_upstream_commit": contract["current_upstream_commit"],
            "current_upstream_checked": contract["current_upstream_checked"],
            "corolla_profiles": list(profiles),
            "secoc_exclusion": contract["boundary"],
        },
        "firmware": {
            "corolla_2023_albino": {"software_id":"8965H1202000", "image":str(args.h_image.relative_to(REPO)), "sha256":sha(h), "source":h_source},
            "corolla_2025_span": {"software_id":"8965F1208000", "image":str(args.f_image.relative_to(REPO)), "sha256":sha(f), "source":f_source},
            "application_region": {"start":"0x00020000", "end_exclusive":"0x00100000", "sha256":sha(h[app_slice]), "byte_identical":True},
            "normal_rx": {"table_start":f"0x{h_rx_start:08X}", "descriptor_count":len(h_rx), "descriptors":h_rx},
            "tx": {"table_start":"0x00021F04", "descriptor_count":len(h_tx), "descriptors":h_tx, "fd030_pdu":{"descriptor":"0x00022620", "length":pdu0[3], "cycle_or_timeout":pdu0[0], "flags":pdu0[5]}},
        },
        "message_role_comparison": roles,
        "old_core_id_inventory": inventory,
        "explicit_non_corolla_prior_art": contract["explicit_non_corolla_secoc_messages"],
        "conclusion": {
            "survives_with_semantic_proof":"0x025 steering angle/rate",
            "survives_as_configuration_lead":"0x0AA wheel speeds",
            "feedback_generation_change":"0x260 + 0x262 disappear; roles split across classic 0x4A3/0x351/0x394 plus mixed 32-byte FD 0x030",
            "command_generation_change":"classic 5-byte torque 0x2E4 disappears; protected FD 0x0B6 signal255 is the H/F target-steering-angle command and signal254 selects cooperative modes",
            "tss2_lta_note":"0x191 was only a neutral coexistence/replacement frame on Corolla TSS2 torque control, not its active steering command",
            "longitudinal_ui_boundary":"0x343 and 0x412 are whole-vehicle camera/ACC/UI contracts; EPS-table absence does not answer their TSS3 replacements",
            "secoc_boundary":"0x131 and 0x183 are not pre-TSS3 Corolla messages and must not be included in the Corolla migration baseline",
        },
    }


def main() -> int:
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--h-image',type=Path,default=DEFAULT_H)
    ap.add_argument('--f-image',type=Path,default=DEFAULT_F)
    ap.add_argument('--contract',type=Path,default=DEFAULT_CONTRACT)
    ap.add_argument('--fd-control',type=Path,default=DEFAULT_FD)
    ap.add_argument('--lta-provenance',type=Path,default=DEFAULT_LTA)
    ap.add_argument('--equivalence',type=Path,default=DEFAULT_EQ)
    ap.add_argument('--state-bridge',type=Path,default=DEFAULT_BRIDGE)
    ap.add_argument('--output',type=Path,default=DEFAULT_OUT)
    args=ap.parse_args()
    report=build(args)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
    print(json.dumps({'output':str(args.output),'roles':len(report['message_role_comparison']),'rx':report['firmware']['normal_rx']['descriptor_count']},indent=2))
    return 0

if __name__=='__main__':
    raise SystemExit(main())
