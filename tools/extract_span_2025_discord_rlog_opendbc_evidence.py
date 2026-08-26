#!/usr/bin/env python3
"""Extract opendbc-porting evidence from Span's tracked 2025 Corolla Discord rlog.

The rlog is tracked and hash-pinned, but LogReader/cereal comes from a compatible
openpilot checkout supplied via --openpilot-root.  All Toyota signal/checksum
interpretation used below is local and explicitly bounded to pinned prior art or
exact H/F firmware-derived rules.
"""
from __future__ import annotations

import argparse
from bisect import bisect_right
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
    0x177: "PCM_CRUISE_3",
    0x1A2: "CRUISE_RELATED",
    0x1D3: "PCM_CRUISE_2",
    0x24D: "PCM_CRUISE_4 / cruise-switch SecOC prior art",
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
    0x51E: "exact-H Ready Status input carrier (target-native join)",
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


def signed_n(value: int, bits: int) -> int:
    sign = 1 << (bits - 1)
    return value - (1 << bits) if value & sign else value


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
    from openpilot.tools.lib.logreader import (
        LogReader,  # type: ignore[import-not-found]
    )

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
    cruise_b0_bit3 = [(dat[0] >> 3) & 1 for _, dat in cruise]
    cruise_switch = rows(0x24D, 8)
    cruise_switch_prior_art = {
        "distance": [be_raw(dat, 2, 1) for _, dat in cruise_switch],
        "cancel": [be_raw(dat, 4, 1) for _, dat in cruise_switch],
        "decrease": [be_raw(dat, 5, 1) for _, dat in cruise_switch],
        "enable": [be_raw(dat, 6, 1) for _, dat in cruise_switch],
        "increase": [be_raw(dat, 7, 1) for _, dat in cruise_switch],
    }
    ready = rows(0x51E, 8)
    ready_bit = [be_raw(dat, 7, 1) for _, dat in ready]

    def preceding(series: list[tuple[int, bytes]], t: int) -> bytes | None:
        if not series:
            return None
        times = [x[0] for x in series]
        idx = bisect_right(times, t) - 1
        return series[idx][1] if idx >= 0 else None

    cruise_bit3_context: dict[str, dict[str, Any]] = {}
    for bit in (0, 1):
        speeds: list[float] = []
        brakes: list[int] = []
        gases: list[float] = []
        for t, dat in cruise:
            if ((dat[0] >> 3) & 1) != bit:
                continue
            wd = preceding(wheel, t)
            bd = preceding(brake, t)
            gd = preceding(gas, t)
            if wd is not None:
                speeds.append(sum(be_raw(wd, start, 15) * 0.01 - 67.67 for start in (6, 22, 38, 54)) / 4)
            if bd is not None:
                brakes.append(be_raw(bd, 3, 1))
            if gd is not None:
                gases.append(be_raw(gd, 15, 8) * 0.005)
        cruise_bit3_context[str(bit)] = {
            "frame_count": sum(x == bit for x in cruise_b0_bit3),
            "speed_kph": stats(speeds) if speeds else None,
            "brake_pressed_fraction": (sum(brakes) / len(brakes)) if brakes else None,
            "gas_pedal_user": stats(gases) if gases else None,
            "gas_positive_fraction": (sum(x > 0 for x in gases) / len(gases)) if gases else None,
        }

    fd30 = rows(0x030, 32)
    # Exact H/F firmware maps four single-bit steering-state fields into byte 6
    # of the 0x030 EPS Tx PDU. Keep these direct masks separate from the generic
    # Motorola decoder: these byte/bit positions are firmware-proved.
    fd30_b6_bit3 = [((dat[6] >> 3) & 1) for _, dat in fd30]
    fd30_steering_fault_inhibit_status = [((dat[6] >> 2) & 1) for _, dat in fd30]
    fd30_b6_bit1 = [((dat[6] >> 1) & 1) for _, dat in fd30]
    fd30_driver_torque_invalid = [(dat[6] & 1) for _, dat in fd30]
    # 0x47188 proves signals 0/10/31 are three views of the same native
    # Steering Wheel Torque intermediate. Signal0 is truncation-toward-zero at
    # 0.1 N.m/count; signal10 is the rounded coarse component paired with the
    # signed hundredths remainder in signal31 for exact reconstruction.
    fd30_torque_coarse_dup = [signed_n(dat[0], 8) for _, dat in fd30]
    fd30_torque_coarse = [signed_n(dat[8], 8) for _, dat in fd30]
    fd30_torque_fine = [signed_n(dat[17] & 0xF, 4) for _, dat in fd30]
    fd30_torque_nm = [coarse * 0.1 + fine * 0.01 for coarse, fine in zip(fd30_torque_coarse, fd30_torque_fine)]
    fd30_byte16 = [dat[16] for _, dat in fd30]
    fd30_rule_matches = sum(
        dat[h030_rule["wire_byte"]] == ((sum(dat[: h030_last_data_byte + 1]) + h030_addend) & 0xFF)
        for _, dat in fd30
    )
    fd30_intervals_ms = [(b[0] - a[0]) / 1e6 for a, b in zip(fd30, fd30[1:])]
    fd30_mean_interval_ms = (
        (fd30[-1][0] - fd30[0][0]) / 1e6 / (len(fd30) - 1)
        if len(fd30) > 1 else None
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
                "cadence": {
                    "interval_count": len(fd30_intervals_ms),
                    "mean_interval_ms": fd30_mean_interval_ms,
                    "min_interval_ms": min(fd30_intervals_ms) if fd30_intervals_ms else None,
                    "max_interval_ms": max(fd30_intervals_ms) if fd30_intervals_ms else None,
                    "descriptor_cycle_ticks": next(x["cycle_or_timeout_raw"] for x in h_state["h_tx_pdu_descriptors"] if x["can_id"] == "0x030"),
                    "derived_foreground_tick_ms": (fd30_mean_interval_ms / 2) if fd30_mean_interval_ms is not None else None,
                    "boundary": "Observed 0x030 cadence corroborates the exact-H/F descriptor's two-foreground-tick period; it does not identify stock B6 sender cadence.",
                },
                "steering_state_bridge": {
                    "b6_bit3": {
                        "firmware_signal_id": 5,
                        "firmware_source": "0xFEBE7E09",
                        "wire": "B6[3]",
                        "values": unique(fd30_b6_bit3),
                        "classification": "runtime-produced status bit; exact steering semantic unresolved",
                    },
                    "steering_fault_inhibit_status": {
                        "firmware_signal_id": 6,
                        "firmware_source": "0xFEBE7DAE",
                        "wire": "B6[2]",
                        "values": unique(fd30_steering_fault_inhibit_status),
                        "clear_frames": sum(x == 0 for x in fd30_steering_fault_inhibit_status),
                        "classification": "H firmware selected steering fault/inhibit status aggregate duplicated into 0x4A3 B0[0]; not an exhaustive EPS-fault bitmap",
                    },
                    "b6_bit1": {
                        "firmware_signal_id": 7,
                        "firmware_source": "0xFEBE7DB3",
                        "wire": "B6[1]",
                        "values": unique(fd30_b6_bit1),
                        "classification": "runtime-produced status bit; exact steering semantic unresolved",
                    },
                    "driver_torque_invalid": {
                        "firmware_signal_id": 8,
                        "firmware_source": "0xFEBE7DB2",
                        "wire": "B6[0]",
                        "values": unique(fd30_driver_torque_invalid),
                        "clear_frames": sum(x == 0 for x in fd30_driver_torque_invalid),
                        "classification": "H firmware driver-torque validity/inhibit gate; asserted state forces the native driver-torque intermediate to zero",
                    },
                    "steering_wheel_torque": {
                        "firmware_signal_ids": [0, 10, 31],
                        "wire": ["B0 signed8", "B8 signed8", "B17[3:0] signed4"],
                        "coarse_duplicate_values": unique(fd30_torque_coarse_dup),
                        "coarse_values": unique(fd30_torque_coarse),
                        "fine_values": unique(fd30_torque_fine),
                        "coarse_rounding_delta_values": unique([b - a for a, b in zip(fd30_torque_coarse_dup, fd30_torque_coarse)]),
                        "coarse_rounding_delta_nonzero_frames": sum(a != b for a, b in zip(fd30_torque_coarse_dup, fd30_torque_coarse)),
                        "reconstruction": "Steering Wheel Torque [N.m] = B8_signed * 0.1 + B17_low_signed4 * 0.01 exactly for the firmware intermediate; B0_signed is the independently saturated truncation-toward-zero 0.1 N.m view and can differ from B8 by one count due to rounding",
                        "torque_nm": stats(fd30_torque_nm),
                        "classification": "exact firmware/Techstream physical decode of live 0x030 driver steering torque; current capture supplies dynamic range but no independent torque transducer",
                    },
                    "byte16_values": unique(fd30_byte16),
                    "boundary": "This nominal moving segment exercises only the clear state for B6[2] and B6[0]. It dynamically corroborates their normal-state polarity and 0x030 availability, but does not replace firmware-static asserted-state semantics or prove openpilot temporary/permanent fault classification.",
                },
                "boundary": "Every Span-rlog 0x030 frame matches the exact-H/F firmware-derived additive-byte rule; the firmware-proved selected steering fault/inhibit status and driver-torque-invalid bits are clear for all 6,000 frames. This strengthens format/producer-family continuity and nominal-state polarity without creating an exact firmware identity join or an induced-fault transition.",
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
                "prior_art_decoded_values": unique([GEAR_PRIOR_ART.get(x, f"UNKNOWN_{x}") for x in gear_values]),
                "decode_basis": "The D label comes only from the retained Toyota prior-art GEAR_PACKET_HYBRID enum; embedded carParams is MOCK and supplies no independent gear-state oracle.",
                "checksum_valid": sum(toyota_checksum(0x127, dat) == dat[-1] for _, dat in gear),
                "frame_count": len(gear),
                "boundary": "This forward-driving capture exercises only raw value 3. Carrier, bit position, checksum, and compatibility with the prior-art D enum are supported; target-native D semantics are not independently validated, and P/R/N/B transitions still require live validation.",
            },
            "0x176": {
                "wire": "classic 8-byte PCM_CRUISE with Toyota additive checksum",
                "checksum_valid": sum(toyota_checksum(0x176, dat) == dat[-1] for _, dat in cruise),
                "frame_count": len(cruise),
                "cruise_active_values": unique(cruise_active),
                "cruise_state_values": unique(cruise_state),
                "b0_bit3_values": unique(cruise_b0_bit3),
                "b0_bit3_context": cruise_bit3_context,
                "dynamic_boundary": "Vehicle motion is exercised, but this capture has no independent cruise-main/engagement oracle. The older CRUISE_ACTIVE/CRUISE_STATE positions stay 0 while B0[3] toggles strongly with accelerator/brake context, so B0[3] is not justified as a TSS3 cruise-main/engaged replacement from this capture.",
            },
            "0x24D": {
                "wire": "classic 8-byte PCM_CRUISE_4 / SecOC cruise-switch prior-art carrier",
                "frame_count": len(cruise_switch),
                "prior_art_button_values": {k: unique(v) for k, v in cruise_switch_prior_art.items()},
                "boundary": "All legacy cruise-switch bits are inactive in this segment; ID/DLC survival is evidence for a retained carrier, not proof that the old button semantics are unchanged on TSS3.",
            },
            "0x51E": {
                "wire": "classic 8-byte target-native H/F Ready Status input carrier",
                "frame_count": len(ready),
                "ready_status_values": unique(ready_bit),
                "unique_payloads": unique([dat.hex() for _, dat in ready]),
                "boundary": "Exact H firmware independently joins B0[7] to Techstream DID 0x1033 Ready Status. Span's moving capture corroborates Ready Status=1 operationally, but carParams is MOCK and the rlog is not an exact F181-to-firmware identity join; Ready Status=0 is not exercised.",
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
