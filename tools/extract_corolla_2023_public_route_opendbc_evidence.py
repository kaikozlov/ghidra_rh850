#!/usr/bin/env python3
"""Extract opendbc-porting evidence from the pinned 2023 Corolla public rlog.

This is an external-source regeneration helper, not a core verifier. The raw rlog is
intentionally untracked. Point --openpilot-root at a checkout that can import
openpilot.tools.lib.logreader; all Toyota signal/checksum decoding used here is
implemented locally so the result does not depend on that checkout's Toyota DBC.
"""
from __future__ import annotations

import argparse
from bisect import bisect_right
import collections
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
LOCK = REPO / "external-references.lock.json"
H_STATE = REPO / "data/generated/corolla_8965H1202000_openpilot_state_bridge.json"
H_RUNTIME = REPO / "data/generated/ephemeral_runtime_target_manifest_8965H1202000.json"
DEFAULT_OUT = REPO / "data/generated/corolla_2023_public_route_opendbc_evidence.json"
ROUTE = "a74eba85c97eaf67|00000004--555953f500"

STATE_IDS = {
    0x00F: "SECOC_SYNCHRONIZATION",
    0x025: "STEER_ANGLE_SENSOR",
    0x030: "generation-native EPS FD telemetry",
    0x0AA: "WHEEL_SPEEDS",
    0x0B6: "exact-H/F protected lateral-command carrier (cross-specimen visibility check)",
    0x0D7: "exact-H/F protected vehicle-speed carrier (cross-specimen visibility check)",
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
    0x351: "exact-H/F EPS Tx plausibility/debounce carrier (cross-specimen visibility check)",
    0x394: "exact-H/F EPS Tx fault/status carrier (cross-specimen visibility check)",
    0x399: "PCM_CRUISE_SM",
    0x3B7: "ESP_CONTROL",
    0x3BC: "GEAR_PACKET",
    0x3F6: "BSM",
    0x411: "PCS_HUD",
    0x412: "LKAS_HUD",
    0x4A3: "exact-H/F EPS Tx state bridge (cross-specimen visibility check)",
    0x4C8: "exact-H/F EPS Tx carrier (cross-specimen visibility check)",
    0x51E: "exact-H Ready Status input carrier (target-native join)",
    0x610: "BODY_CONTROL_STATE_2",
    0x614: "BLINKERS_STATE",
    0x620: "BODY_CONTROL_STATE",
    0x622: "LIGHT_STALK",
}

# Current older-Toyota CarState/Panda roles. This is role vocabulary only; the
# classification below is derived from this exact TSS3 route and target-native H facts.
OLD_REQUIRED_IDS = {
    0x025, 0x0AA, 0x101, 0x116, 0x127, 0x176, 0x1D3, 0x260, 0x262,
    0x283, 0x320, 0x343, 0x399, 0x3B7, 0x3BC, 0x3F6, 0x411, 0x412,
    0x610, 0x614, 0x620, 0x622,
}


from toyota_route_opendbc_common import be_raw, rate_hz, sha256, stats, toyota_checksum


def expected_source() -> dict[str, object]:
    lock = json.loads(LOCK.read_text())
    row = next(r for r in lock["public_routes"] if r["route"] == ROUTE)
    sample = next(x for x in row["rlog_samples"] if x["segment"] == 0)
    return {"sha256": sample["sha256"], "size": sample["size"]}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--rlog", type=Path, required=True)
    ap.add_argument("--openpilot-root", type=Path, required=True)
    ap.add_argument("--output", type=Path, default=DEFAULT_OUT)
    args = ap.parse_args()

    src = expected_source()
    if not args.rlog.is_file():
        raise SystemExit(f"missing rlog: {args.rlog}")
    actual = {"sha256": sha256(args.rlog), "size": args.rlog.stat().st_size}
    if actual != src:
        raise SystemExit(f"rlog identity mismatch: expected {src}, got {actual}")

    sys.path.insert(0, str(args.openpilot_root.resolve()))
    from openpilot.tools.lib.logreader import LogReader  # type: ignore[import-not-found]

    frames: dict[tuple[int, int, int], list[tuple[int, bytes]]] = collections.defaultdict(list)
    carstate: dict[str, list[Any]] = collections.defaultdict(list)
    first_t: int | None = None
    last_t: int | None = None

    for ev in LogReader(str(args.rlog), sort_by_time=True):
        which = ev.which()
        if which == "can":
            t = int(ev.logMonoTime)
            first_t = t if first_t is None else min(first_t, t)
            last_t = t if last_t is None else max(last_t, t)
            for c in ev.can:
                if c.src < 128:
                    dat = bytes(c.dat)
                    frames[(int(c.src), int(c.address), len(dat))].append((t, dat))
        elif which == "carState":
            cs = ev.carState
            for name in (
                "canValid", "vEgo", "steeringAngleDeg", "steeringRateDeg",
                "steeringTorque", "steeringTorqueEps", "steerFaultTemporary",
                "steerFaultPermanent", "brakePressed", "gasPressed",
            ):
                carstate[name].append(getattr(cs, name))
            carstate["cruiseAvailable"].append(cs.cruiseState.available)
            carstate["cruiseEnabled"].append(cs.cruiseState.enabled)

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

    incoming_by_addr: dict[int, list[tuple[int, int, int]]] = collections.defaultdict(list)
    for (bus, addr, dlc), rows in frames.items():
        incoming_by_addr[addr].append((bus, dlc, len(rows)))

    state_rows = []
    for addr, name in STATE_IDS.items():
        instances = []
        for (bus, a, dlc), rows in sorted(frames.items()):
            if a != addr:
                continue
            instances.append({
                "bus": bus,
                "dlc": dlc,
                "count": len(rows),
                "rate_hz": rate_hz(rows),
                "first_payload": rows[0][1].hex(),
            })
        state_rows.append({
            "can_id": f"0x{addr:03X}",
            "older_toyota_role": name,
            "required_by_older_toyota_contract": addr in OLD_REQUIRED_IDS,
            "instances": instances,
        })

    # Exact H firmware independently proves that its 32-byte 0x025 keeps these
    # three older Toyota signal positions. Decode the route at those positions.
    fd25 = frames.get((1, 0x025, 32), [])
    angle = [be_raw(dat, 3, 12, True) * 1.5 for _, dat in fd25]
    fraction = [be_raw(dat, 39, 4, True) * 0.1 for _, dat in fd25]
    rate = [be_raw(dat, 35, 12, True) * 1.0 for _, dat in fd25]

    cruise = frames.get((1, 0x176, 8), [])
    cruise_checksums = sum(toyota_checksum(0x176, dat) == dat[-1] for _, dat in cruise)
    cruise_active = [bool((dat[0] >> 5) & 1) for _, dat in cruise]
    cruise_state = [be_raw(dat, 31, 4) for _, dat in cruise]
    cruise_b0_bit3 = [(dat[0] >> 3) & 1 for _, dat in cruise]
    cruise_switch = frames.get((1, 0x24D, 8), [])
    cruise_switch_prior_art = {
        "distance": [be_raw(dat, 2, 1) for _, dat in cruise_switch],
        "cancel": [be_raw(dat, 4, 1) for _, dat in cruise_switch],
        "decrease": [be_raw(dat, 5, 1) for _, dat in cruise_switch],
        "enable": [be_raw(dat, 6, 1) for _, dat in cruise_switch],
        "increase": [be_raw(dat, 7, 1) for _, dat in cruise_switch],
    }
    ready = frames.get((1, 0x51E, 8), [])
    ready_bit = [be_raw(dat, 7, 1) for _, dat in ready]

    wheel = frames.get((1, 0x0AA, 8), [])
    wheel_speeds: dict[str, list[float]] = {x: [] for x in ("FR", "FL", "RR", "RL")}
    wheel_faults: dict[str, list[int]] = {x: [] for x in wheel_speeds}
    wheel_starts = {"FR": (7, 6), "FL": (23, 22), "RR": (39, 38), "RL": (55, 54)}
    for _, dat in wheel:
        for whl, (fault_bit, speed_start) in wheel_starts.items():
            wheel_faults[whl].append(be_raw(dat, fault_bit, 1))
            wheel_speeds[whl].append(be_raw(dat, speed_start, 15) * 0.01 - 67.67)

    brake = frames.get((1, 0x101, 8), [])
    brake_pressed = [be_raw(dat, 3, 1) for _, dat in brake]
    gas = frames.get((1, 0x116, 8), [])
    gas_user = [be_raw(dat, 15, 8) * 0.005 for _, dat in gas]

    def preceding(rows: list[tuple[int, bytes]], t: int) -> bytes | None:
        if not rows:
            return None
        times = [x[0] for x in rows]
        idx = bisect_right(times, t) - 1
        return rows[idx][1] if idx >= 0 else None

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

    fd30 = frames.get((1, 0x030, 32), [])
    fd30_rule_matches = sum(
        dat[h030_rule["wire_byte"]] == ((sum(dat[: h030_last_data_byte + 1]) + h030_addend) & 0xFF)
        for _, dat in fd30
    )

    bus0 = []
    for (bus, addr, dlc), rows in sorted(frames.items()):
        if bus == 0:
            bus0.append({
                "can_id": f"0x{addr:03X}",
                "dlc": dlc,
                "count": len(rows),
                "rate_hz": rate_hz(rows),
                "first_payload": rows[0][1].hex(),
            })

    def unique(xs: list[Any]) -> list[Any]:
        return sorted(set(xs))

    out = {
        "schema": "corolla-2023-public-route-opendbc-evidence-v1",
        "source": {
            "route": ROUTE,
            "segment": 0,
            **actual,
            "duration_s": ((last_t - first_t) * 1e-9) if first_t is not None and last_t is not None else None,
            "identity_note": "Route carParams was forced TOYOTA_COROLLA_TSS2 and contains no carFw; this is a TSS3 Corolla whole-vehicle route oracle, not an exact H/F firmware-to-route join.",
            "can_source_filter": "Only CAN records with src<128 are treated as incoming vehicle traffic. Panda returned/Tx echoes (src=bus+128) and rejected echoes (src=bus+192) are excluded from every inventory and baseline in this artifact.",
        },
        "axis_boundary": "TSS generation describes ADAS/control architecture. SecOC/TSK describes security/authentication. Presence of 0x00F or authenticated messages does not classify TSS generation.",
        "incoming_state_inventory": state_rows,
        "direct_reuse_evidence": {
            "0x030": {
                "wire": "32-byte CAN-FD generation-native EPS telemetry/status PDU",
                "exact_h_f_additive_rule": h030_rule,
                "frame_count": len(fd30),
                "rule_matches": fd30_rule_matches,
                "boundary": "All route 0x030 frames matching the exact-H/F firmware-derived additive-byte rule is a strong format/producer-family continuity join, not an exact firmware/vehicle identity join.",
            },
            "0x025": {
                "wire": "32-byte CAN-FD; exact H firmware independently proves legacy STEER_ANGLE/STEER_FRACTION/STEER_RATE bit positions survive inside the new PDU",
                "steer_angle_deg": stats(angle),
                "steer_fraction_deg": stats(fraction),
                "steer_rate_deg_s": stats(rate),
            },
            "0x0AA": {
                "wire": "classic 8-byte WHEEL_SPEEDS",
                "speeds_kph": {k: stats(v) for k, v in wheel_speeds.items()},
                "fault_values": {k: unique(v) for k, v in wheel_faults.items()},
            },
            "0x101": {
                "wire": "classic 8-byte BRAKE_MODULE",
                "brake_pressed_values": unique(brake_pressed),
            },
            "0x116": {
                "wire": "classic 8-byte GAS_PEDAL with Toyota classic SecOC trailer",
                "gas_pedal_user": stats(gas_user),
            },
            "0x176": {
                "wire": "classic 8-byte PCM_CRUISE with Toyota additive checksum",
                "checksum_valid": cruise_checksums,
                "frame_count": len(cruise),
                "cruise_active_values": unique(cruise_active),
                "cruise_state_values": unique(cruise_state),
                "b0_bit3_values": unique(cruise_b0_bit3),
                "b0_bit3_context": cruise_bit3_context,
                "dynamic_boundary": "This segment has no independent cruise-main/engagement oracle. The older CRUISE_ACTIVE/CRUISE_STATE positions stay 0 while B0[3] toggles strongly with accelerator/brake context, so B0[3] is not justified as a TSS3 cruise-main/engaged replacement from this route.",
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
                "boundary": "Exact H firmware independently joins B0[7] to Techstream DID 0x1033 Ready Status. This route supplies operational-state corroboration only because it has no carFw/F181 identity join and does not exercise Ready Status=0.",
            },
        },
        "forced_old_profile_result": {
            "sample_count": len(carstate.get("canValid", [])),
            "fields": {k: unique(v) for k, v in carstate.items()},
            "interpretation": "The forced TOYOTA_COROLLA_TSS2 parser remained canValid=false and reported zero vehicle speed/steering despite coherent TSS3 traffic. This proves a new generation-specific bus/DBC parser is required; it does not invalidate individual compatible signal layouts recovered directly from raw frames.",
        },
        "bus0_canfd_baseline": bus0,
        "route_vs_exact_h_f_visibility": {
            "exact_h_f_secoc_rx_search_vocabulary": [f"0x{addr:03X}/{dlc}" for addr, dlc in exact_h_secoc_rx],
            "secoc_rx_observed_counts": {
                f"0x{addr:03X}/{dlc}": sum(len(rows) for (bus, a, d), rows in frames.items() if a == addr and d == dlc)
                for addr, dlc in exact_h_secoc_rx
            },
            "exact_h_f_tx_search_vocabulary": [f"0x{addr:03X}/{dlc}" for addr, dlc in exact_h_tx],
            "tx_observed_counts": {
                f"0x{addr:03X}/{dlc}": sum(len(rows) for (bus, a, d), rows in frames.items() if a == addr and d == dlc)
                for addr, dlc in exact_h_tx
            },
            "boundary": "The public route exposes 0x00F and 0x0D7 but no 0x0B6, and only 0x030 from the exact-H/F five-PDU Tx set. Because the route has no carFw/F181 join, this cannot prove B6 is feature-gated or absent on an exact H/F EPS bus; it instead proves the route is not evidence of a complete exact-H/F EPS-bus mirror.",
        },
        "boundaries": [
            "No exact carFw/F181 inventory exists in the route metadata, so exact H/F firmware state carriers must not be attributed to this route.",
            "Same CAN ID does not imply same semantics; 0x025 changes DLC and 0x123/0x180-family geometry differs from older Toyota radar definitions.",
            "A retained ID with static values is only a reuse lead unless signal meaning is independently recovered or dynamically exercised.",
            "Panda logical bus numbering is not physical producer ownership; Toyota-B relay topology must be solved separately before stock-source suppression is designed.",
        ],
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
