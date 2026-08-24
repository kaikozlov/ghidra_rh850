#!/usr/bin/env python3
"""Extract opendbc-porting evidence from Span's tracked 2025 Corolla Discord rlog.

The rlog is tracked and hash-pinned, but LogReader/cereal comes from a compatible
openpilot checkout supplied via --openpilot-root.  All Toyota signal/checksum
interpretation used below is local and explicitly bounded to pinned prior art or
exact H/F firmware-derived rules.
"""
from __future__ import annotations

import argparse
import collections
import json
import re
import sys
from pathlib import Path
from typing import Any

from toyota_route_opendbc_common import be_raw, rate_hz, sha256, stats, toyota_checksum

REPO = Path(__file__).resolve().parents[1]
LOCK = REPO / "external-references.lock.json"
RLOG_REL = "community/spanconstant/span_67fd5b833889fedf_00000010--17084916da--3--rlog.zst"
DEFAULT_RLOG = REPO / RLOG_REL
DEFAULT_OUT = REPO / "data/generated/corolla_2025_span_discord_rlog_opendbc_evidence.json"
H_STATE = REPO / "data/generated/corolla_8965H1202000_openpilot_state_bridge.json"
H_RUNTIME = REPO / "data/generated/ephemeral_runtime_target_manifest_8965H1202000.json"
SPAN_PREFLIGHT = REPO / "community/spanconstant/raw-20260821/span-corolla-2025.20260821-1511/preflight_8965012N50E12H030731_20260821-151149.json"

ROLE_IDS = {
    0x00F: "SECOC_SYNCHRONIZATION",
    0x025: "STEER_ANGLE_SENSOR",
    0x030: "generation-native EPS FD telemetry",
    0x0AA: "WHEEL_SPEEDS",
    0x0B6: "exact-H/F protected lateral command (visibility check)",
    0x0D7: "exact-H/F protected vehicle-speed carrier (visibility check)",
    0x101: "BRAKE_MODULE",
    0x116: "GAS_PEDAL",
    0x127: "GEAR_PACKET_HYBRID",
    0x176: "PCM_CRUISE",
    0x1D3: "PCM_CRUISE_2",
    0x260: "STEER_TORQUE_SENSOR",
    0x262: "EPS_STATUS",
    0x283: "PRE_COLLISION",
    0x320: "VSC1S07",
    0x343: "ACC_CONTROL",
    0x351: "exact-H/F EPS Tx plausibility/debounce carrier (visibility check)",
    0x394: "exact-H/F EPS Tx fault/status carrier (visibility check)",
    0x399: "PCM_CRUISE_SM",
    0x3B7: "ESP_CONTROL",
    0x3BC: "GEAR_PACKET",
    0x3F6: "BSM",
    0x411: "PCS_HUD",
    0x412: "LKAS_HUD",
    0x4A3: "exact-H/F EPS Tx state bridge (visibility check)",
    0x4C8: "exact-H/F EPS Tx carrier (visibility check)",
    0x610: "BODY_CONTROL_STATE_2",
    0x614: "BLINKERS_STATE",
    0x620: "BODY_CONTROL_STATE",
    0x622: "LIGHT_STALK",
}

GEAR_PRIOR_ART = {0: "P", 1: "R", 2: "N", 3: "D", 4: "B"}


def expected_source() -> dict[str, Any]:
    lock = json.loads(LOCK.read_text())
    row = next(x for x in lock["community_artifacts"] if x["path"] == RLOG_REL)
    return {
        "source": row["source"],
        "provenance": row["provenance"],
        "notes": row["notes"],
        "sha256": row["sha256"],
        "size": row["size"],
    }


def unique(xs: list[Any]) -> list[Any]:
    return sorted(set(xs))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--rlog", type=Path, default=DEFAULT_RLOG)
    ap.add_argument("--openpilot-root", type=Path, required=True)
    ap.add_argument("--output", type=Path, default=DEFAULT_OUT)
    args = ap.parse_args()

    expected = expected_source()
    if not args.rlog.is_file():
        raise SystemExit(f"missing rlog: {args.rlog}")
    actual = {"sha256": sha256(args.rlog), "size": args.rlog.stat().st_size}
    if actual != {"sha256": expected["sha256"], "size": expected["size"]}:
        raise SystemExit(f"rlog identity mismatch: expected {expected}, got {actual}")

    h_state = json.loads(H_STATE.read_text())
    h_runtime = json.loads(H_RUNTIME.read_text())
    exact_h_tx = [(int(x["can_id"], 16), int(x["length"])) for x in h_state["h_tx_pdu_descriptors"]]
    exact_h_secoc_rx = [(int(x["can_id"], 16), int(x["secured_length"])) for x in h_runtime["secoc_records"]["records"]]
    h030_rule = h_state["state_bridge"]["0x030"]["additive_field"]
    m030 = re.fullmatch(r"sum\(payload_bytes_0_through_(\d+)\) \+ 0x([0-9A-Fa-f]+), low byte", h030_rule["formula"])
    if not m030 or h030_rule["wire_byte"] != int(m030.group(1)) + 1:
        raise SystemExit(f"unsupported exact-H 0x030 additive rule: {h030_rule}")
    h030_last_data_byte = int(m030.group(1))
    h030_addend = int(m030.group(2), 16)

    sys.path.insert(0, str(args.openpilot_root.resolve()))
    from openpilot.tools.lib.logreader import LogReader  # type: ignore[import-not-found]

    frames: dict[tuple[int, int, int], list[tuple[int, bytes]]] = collections.defaultdict(list)
    returned: collections.Counter[tuple[int, int, int]] = collections.Counter()
    carstate: dict[str, list[Any]] = collections.defaultdict(list)
    first_can_t: int | None = None
    last_can_t: int | None = None
    init: dict[str, Any] | None = None
    car_params: dict[str, Any] | None = None
    panda_state: dict[str, Any] | None = None
    panda_states: list[dict[str, Any]] = []
    selfdrive_states: list[str] = []
    lat_active: list[bool] = []
    long_active: list[bool] = []
    radar_tracks_nonempty = 0
    radar_tracks_samples = 0

    for ev in LogReader(str(args.rlog), sort_by_time=True):
        which = ev.which()
        if which == "can":
            t = int(ev.logMonoTime)
            first_can_t = t if first_can_t is None else min(first_can_t, t)
            last_can_t = t if last_can_t is None else max(last_can_t, t)
            for c in ev.can:
                bus = int(c.src)
                dat = bytes(c.dat)
                key = (bus % 128, int(c.address), len(dat))
                if bus < 128:
                    frames[key].append((t, dat))
                else:
                    returned[(bus, int(c.address), len(dat))] += 1
        elif which == "initData" and init is None:
            x = ev.initData
            init = {
                "version": str(x.version),
                "git_commit": str(x.gitCommit),
                "git_branch": str(x.gitBranch),
                "git_remote": str(x.gitRemote),
                "device_type": str(x.deviceType),
                "dongle_id": str(x.dongleId),
            }
        elif which == "carParams" and car_params is None:
            x = ev.carParams
            car_params = {
                "car_fingerprint": str(x.carFingerprint),
                "brand": str(x.brand),
                "safety_configs": [
                    {"model": str(s.safetyModel), "param": int(s.safetyParam)}
                    for s in x.safetyConfigs
                ],
                "car_fw": [
                    {"ecu": str(fw.ecu), "address": int(fw.address), "fw_version_hex": bytes(fw.fwVersion).hex()}
                    for fw in x.carFw
                ],
            }
        elif which == "pandaStates" and len(ev.pandaStates):
            for x in ev.pandaStates:
                state_row = {
                    "panda_type": str(x.pandaType),
                    "safety_model": str(x.safetyModel),
                    "safety_param": int(x.safetyParam),
                    "controls_allowed": bool(x.controlsAllowed),
                    "harness_status": str(x.harnessStatus),
                }
                panda_states.append(state_row)
                if panda_state is None:
                    panda_state = state_row
        elif which == "carState":
            x = ev.carState
            carstate["vEgo"].append(float(x.vEgo))
            carstate["steeringAngleDeg"].append(float(x.steeringAngleDeg))
            carstate["steeringTorque"].append(float(x.steeringTorque))
            carstate["gearShifter"].append(str(x.gearShifter))
            carstate["canValid"].append(bool(x.canValid))
        elif which == "selfdriveState":
            selfdrive_states.append(str(ev.selfdriveState.state))
        elif which == "carControl":
            lat_active.append(bool(ev.carControl.latActive))
            long_active.append(bool(ev.carControl.longActive))
        elif which == "radarTracks":
            radar_tracks_samples += 1
            d = ev.radarTracks.to_dict()
            # Current schema puts parsed point content outside the always-present
            # deprecated/errors objects.  This Span log contains no such content.
            if any(k not in {"deprecated", "errors"} for k in d):
                radar_tracks_nonempty += 1

    if not init or not car_params or not panda_state or first_can_t is None or last_can_t is None:
        raise SystemExit("rlog is missing required init/carParams/panda/CAN metadata")

    def rows(addr: int, dlc: int, bus: int = 1) -> list[tuple[int, bytes]]:
        return frames.get((bus, addr, dlc), [])

    fd25 = rows(0x025, 32)
    angle = [be_raw(dat, 3, 12, True) * 1.5 for _, dat in fd25]
    fraction = [be_raw(dat, 39, 4, True) * 0.1 for _, dat in fd25]
    steer_rate = [be_raw(dat, 35, 12, True) for _, dat in fd25]

    wheel = rows(0x0AA, 8)
    wheel_speeds: dict[str, list[float]] = {x: [] for x in ("FR", "FL", "RR", "RL")}
    wheel_faults: dict[str, list[int]] = {x: [] for x in wheel_speeds}
    wheel_starts = {"FR": (7, 6), "FL": (23, 22), "RR": (39, 38), "RL": (55, 54)}
    for _, dat in wheel:
        for whl, (fault_bit, speed_start) in wheel_starts.items():
            wheel_faults[whl].append(be_raw(dat, fault_bit, 1))
            wheel_speeds[whl].append(be_raw(dat, speed_start, 15) * 0.01 - 67.67)

    brake = rows(0x101, 8)
    brake_pressed = [be_raw(dat, 3, 1) for _, dat in brake]
    gas = rows(0x116, 8)
    gas_user = [be_raw(dat, 15, 8) * 0.005 for _, dat in gas]
    gear = rows(0x127, 8)
    gear_values = [be_raw(dat, 47, 4) for _, dat in gear]
    cruise = rows(0x176, 8)
    cruise_active = [bool((dat[0] >> 5) & 1) for _, dat in cruise]
    cruise_state = [be_raw(dat, 31, 4) for _, dat in cruise]
    fd30 = rows(0x030, 32)
    fd30_rule_matches = sum(
        dat[h030_rule["wire_byte"]] == ((sum(dat[: h030_last_data_byte + 1]) + h030_addend) & 0xFF)
        for _, dat in fd30
    )

    role_inventory = []
    for addr, name in ROLE_IDS.items():
        instances = []
        for (bus, a, dlc), vals in sorted(frames.items()):
            if a != addr:
                continue
            instances.append({
                "bus": bus,
                "dlc": dlc,
                "count": len(vals),
                "rate_hz": rate_hz(vals),
                "first_payload": vals[0][1].hex(),
            })
        role_inventory.append({"can_id": f"0x{addr:03X}", "role": name, "instances": instances})

    def bus_shapes(bus: int) -> list[dict[str, Any]]:
        out = []
        for (b, addr, dlc), vals in sorted(frames.items()):
            if b != bus:
                continue
            out.append({
                "can_id": f"0x{addr:03X}",
                "dlc": dlc,
                "count": len(vals),
                "rate_hz": rate_hz(vals),
                "first_payload": vals[0][1].hex(),
            })
        return out

    bus0 = bus_shapes(0)
    bus2 = bus_shapes(2)
    bus0_set = {(x["can_id"], x["dlc"]) for x in bus0}
    bus2_set = {(x["can_id"], x["dlc"]) for x in bus2}
    equality = []
    for can_id, dlc in sorted(bus0_set | bus2_set):
        addr = int(can_id, 16)
        a = [dat for _, dat in frames.get((0, addr, dlc), [])]
        b = [dat for _, dat in frames.get((2, addr, dlc), [])]
        equality.append({
            "can_id": can_id,
            "dlc": dlc,
            "count_bus0": len(a),
            "count_bus2": len(b),
            "payload_sequence_equal": a == b,
        })

    h_rx_counts = {
        f"0x{addr:03X}/{dlc}": sum(len(vals) for (bus, a, d), vals in frames.items() if a == addr and d == dlc)
        for addr, dlc in exact_h_secoc_rx
    }
    h_tx_counts = {
        f"0x{addr:03X}/{dlc}": sum(len(vals) for (bus, a, d), vals in frames.items() if a == addr and d == dlc)
        for addr, dlc in exact_h_tx
    }

    preflight = json.loads(SPAN_PREFLIGHT.read_text())
    preflight_dongle = preflight["panda"]["dongle"]

    out = {
        "schema": "corolla-2025-span-discord-rlog-opendbc-evidence-v1",
        "source": {
            "path": RLOG_REL,
            **actual,
            "attribution": expected["source"],
            "provenance": expected["provenance"],
            "notes": expected["notes"],
            "can_window_s": (last_can_t - first_can_t) * 1e-9,
            "init_data": init,
            "car_params": car_params,
            "panda_state": panda_state,
            "panda_state_samples": len(panda_states),
            "panda_state_unique": [dict(items) for items in sorted({tuple(sorted(x.items())) for x in panda_states})],
            "can_source_filter": "Only src<128 records are treated as incoming vehicle traffic; Panda returned/Tx and rejected echoes are excluded from every inventory and baseline.",
            "identity_boundary": {
                "rlog_car_params_is_mock": car_params["car_fingerprint"] == "MOCK",
                "rlog_has_no_usable_f181_join": True,
                "rlog_dongle_id": init["dongle_id"],
                "firmware_dump_preflight_dongle_id": preflight_dongle,
                "same_dongle": init["dongle_id"] == preflight_dongle,
                "interpretation": "Discord attribution ties this dynamic rlog to Span's reported 2025 Corolla investigation, but embedded carParams is MOCK and the logging dongle differs from the later TSKM dump preflight. Treat this as Span-attributed vehicle-level evidence, not an exact 8965F1208000 firmware-to-route join.",
            },
        },
        "runtime_boundary": {
            "selfdrive_state_values": unique(selfdrive_states),
            "lat_active_values": unique(lat_active),
            "long_active_values": unique(long_active),
            "controls_allowed": panda_state["controls_allowed"],
            "interpretation": "Openpilot control was disabled and Panda controlsAllowed was false. Raw src<128 CAN is used as vehicle evidence; logged MOCK CarState is not used for physical-state semantics.",
            "mock_carstate": {k: unique(v) for k, v in carstate.items()},
        },
        "moving_vehicle_evidence": {
            "wheel_speed_max_kph": max(max(v) for v in wheel_speeds.values()),
            "wheel_speed_min_kph": min(min(v) for v in wheel_speeds.values()),
            "brake_pressed_values": unique(brake_pressed),
            "gas_pedal_user": stats(gas_user),
            "steering_angle_deg": stats(angle),
            "steering_rate_deg_s": stats(steer_rate),
            "interpretation": "Raw vehicle signals are dynamic and wheel speed exceeds zero, so this is a moving/driving CAN capture even though the embedded MOCK CarState remains zeroed. Motion does not by itself prove that stock LTA was active or exercise every READY-state subsystem contract.",
        },
        "role_inventory": role_inventory,
        "direct_reuse_evidence": {
            "0x025": {
                "wire": "32-byte CAN-FD; exact H firmware independently proves the older steering angle/fraction/rate positions survive",
                "steer_angle_deg": stats(angle),
                "steer_fraction_deg": stats(fraction),
                "steer_rate_deg_s": stats(steer_rate),
            },
            "0x030": {
                "wire": "32-byte generation-native EPS telemetry/status PDU",
                "exact_h_f_additive_rule": h030_rule,
                "frame_count": len(fd30),
                "rule_matches": fd30_rule_matches,
                "boundary": "Every Span-rlog 0x030 frame matches the exact-H/F firmware-derived additive-byte rule; this strengthens format/producer-family continuity without creating an exact firmware identity join.",
            },
            "0x0AA": {
                "wire": "classic 8-byte WHEEL_SPEEDS",
                "speeds_kph": {k: stats(v) for k, v in wheel_speeds.items()},
                "fault_values": {k: unique(v) for k, v in wheel_faults.items()},
            },
            "0x101": {
                "wire": "classic 8-byte BRAKE_MODULE",
                "brake_pressed_values": unique(brake_pressed),
                "checksum_valid": sum(toyota_checksum(0x101, dat) == dat[-1] for _, dat in brake),
                "frame_count": len(brake),
            },
            "0x116": {
                "wire": "classic 8-byte GAS_PEDAL with Toyota classic SecOC trailer",
                "gas_pedal_user": stats(gas_user),
            },
            "0x127": {
                "wire": "classic 8-byte GEAR_PACKET_HYBRID",
                "gear_raw_values": unique(gear_values),
                "prior_art_value_map": {str(k): v for k, v in GEAR_PRIOR_ART.items()},
                "decoded_values": unique([GEAR_PRIOR_ART.get(x, f"UNKNOWN_{x}") for x in gear_values]),
                "checksum_valid": sum(toyota_checksum(0x127, dat) == dat[-1] for _, dat in gear),
                "frame_count": len(gear),
                "boundary": "This capture exercises only D (raw value 3). Carrier, bit position, checksum, and D enum compatibility are directly supported; P/R/N/B transitions still require dynamic validation.",
            },
            "0x176": {
                "wire": "classic 8-byte PCM_CRUISE with Toyota additive checksum",
                "checksum_valid": sum(toyota_checksum(0x176, dat) == dat[-1] for _, dat in cruise),
                "frame_count": len(cruise),
                "cruise_active_values": unique(cruise_active),
                "cruise_state_values": unique(cruise_state),
                "dynamic_boundary": "Vehicle motion is exercised, but cruise never engages in this segment; active-state semantics remain untested.",
            },
        },
        "harness_observation_boundary": {
            "panda_state_samples": len(panda_states),
            "all_samples_elm327_param1": all(x["safety_model"] == "elm327" and x["safety_param"] == 1 for x in panda_states),
            "all_samples_harness_status_flipped": all(x["harness_status"] == "flipped" for x in panda_states),
            "all_samples_controls_disallowed": all(not x["controls_allowed"] for x in panda_states),
            "field_context": "The maintainer reports Span had not physically swapped the Toyota-B CAN0/CAN1 pairs for this log.",
            "interpretation": "Panda harnessStatus=flipped is USB-C harness orientation, not the Toyota-B physical CAN0/CAN1 repin. ELM327 param=1 keeps logical bus 1/FDCAN2 on the normal harness CAN1 wires, so an unmodified harness can passively observe that unsplit network. The missing physical repin prevents CAN0/CAN2 relay interception and camera-side-vs-car-side producer attribution; it does not by itself make stock CAN1 traffic invisible to logical bus 1.",
        },
        "exact_h_f_visibility": {
            "secoc_rx_expected": [f"0x{addr:03X}/{dlc}" for addr, dlc in exact_h_secoc_rx],
            "secoc_rx_observed_counts": h_rx_counts,
            "tx_expected": [f"0x{addr:03X}/{dlc}" for addr, dlc in exact_h_tx],
            "tx_observed_counts": h_tx_counts,
            "boundary": "The moving Span rlog exposes 0x00F/0x0D7 but no B6, and only 0x030 from the exact-H/F five-PDU Tx set. Because all Panda-state samples are ELM327 param=1, logical bus 1 was attached to the normal harness CAN1 wires throughout; lack of the physical CAN0/CAN1 repin therefore blocks interception/side attribution rather than passive CAN1 observation. B6 absence is still only a segment-level negative: no stock-LTA off->active->off transition or exact F181 join is present, so feature/request gating and specimen/segment differences remain open.",
        },
        "tss3_fd_network": {
            "bus0": bus0,
            "bus2": bus2,
            "bus0_bus2_same_id_dlc_set": bus0_set == bus2_set,
            "bus0_bus2_payload_sequences_equal": all(x["payload_sequence_equal"] for x in equality),
            "equality_by_id": equality,
            "interpretation": "The full moving capture carries the same 22 incoming CAN-FD ID/DLC shapes on buses 0 and 2 with byte-identical payload sequences. This upgrades the prior Span NRtD structure result to a dynamic/moving topology invariant; it still does not assign field semantics or physical producer ownership.",
        },
        "radar_parser_boundary": {
            "radar_tracks_samples": radar_tracks_samples,
            "nonempty_parsed_track_samples": radar_tracks_nonempty,
            "interpretation": "Span's tskdash log contains radarTracks/radarState services, but radarTracks carries no parsed points and radarState model leads have radar=false. The source branch therefore supplies no hidden TSS3 radar decoder for the 0x180-family.",
        },
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
