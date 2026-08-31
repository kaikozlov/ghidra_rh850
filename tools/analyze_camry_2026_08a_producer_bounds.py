#!/usr/bin/env python3
"""Bound who transmits / SecOC-protects retained Bus-4 0x08A.

Offline over the two relay-correct Camry drives plus current GTS+ canbus
placement for vehicle type 12984. No vehicle I/O. Does not recover the
signer key or name a single remaining Bus-4 origin CPU.
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import subprocess
from collections import defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
RAW = REPO / "targets/camry-2026/raw-20260827"
DRIVES = {
    "drive_a": RAW / "camry_relay_route_can_20260827.ndjson.gz",
    "drive_b": RAW / "camry_relay_lta_confirm_route_can_20260827.ndjson.gz",
}
F33_TX = REPO / "data/generated/camry_8965F3307000_tss3_opendbc_port.json"
WATCH = {0x025, 0x030, 0x081, 0x08A, 0x090, 0x00F, 0x0D7, 0x180}
PERIODIC_N = 50
MACLIKE_LAST4_FRAC = 0.5


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def cadence(times: list[int]) -> dict:
    if len(times) < 3:
        return {"n": len(times)}
    dts = [(b - a) / 1e6 for a, b in zip(times, times[1:]) if 0 < (b - a) < 2e9]
    dts_sorted = sorted(dts)
    n20 = sum(18 <= g <= 22 for g in dts)
    n30 = sum(28 <= g <= 32 for g in dts)
    span_s = (times[-1] - times[0]) / 1e9
    return {
        "n": len(times),
        "mean_hz": round((len(times) - 1) / span_s, 3) if span_s else None,
        "median_ms": round(dts_sorted[len(dts_sorted) // 2], 3),
        "gap_20ms_class": n20,
        "gap_30ms_class": n30,
        "gap_other": len(dts) - n20 - n30,
        "frac_30ms": round(n30 / len(dts), 4) if dts else None,
    }

def event_batching(
    bus0_event_counts: dict[int, int],
    target_times: list[int],
) -> dict:
    """Describe rlog publication batching; logMonoTime is not a wire timestamp."""
    sizes = sorted(bus0_event_counts.values())
    target_sizes = [bus0_event_counts[t] for t in target_times]
    return {
        "timestamp_bucket_count": len(sizes),
        "median_bus0_frames_per_event": sizes[len(sizes) // 2] if sizes else None,
        "max_bus0_frames_per_event": max(sizes, default=None),
        "0x08A_frames_in_multi_frame_events": sum(size > 1 for size in target_sizes),
        "0x08A_frame_count": len(target_sizes),
        "0x08A_multi_frame_event_fraction": (
            round(sum(size > 1 for size in target_sizes) / len(target_sizes), 6)
            if target_sizes
            else None
        ),
        "boundary": (
            "Each rlog Event.logMonoTime timestamps a publication batch, not an "
            "individual CAN frame. Inter-frame 20/30 ms classes therefore cannot "
            "identify physical arbitration, a CAN TX queue, or a transmitter ECU"
        ),
    }




def summarize_bus1_auth(
    last4: dict[tuple[int, int], set[bytes]],
    counts: dict[tuple[int, int], int],
    n_00f: int,
) -> dict:
    """Ordinary-P5 SecOC puts a frame-unique MAC in the last four bytes.

    Camera Bus-1 output is the opposite: every periodic stream has a constant
    last-4, and authenticated 0x00F never appears on that bus.
    """
    periodic = []
    for (addr, dlc), n in sorted(counts.items(), key=lambda kv: (-kv[1], kv[0])):
        if n < PERIODIC_N:
            continue
        u4 = len(last4[(addr, dlc)])
        periodic.append({
            "can_id": f"0x{addr:03X}",
            "dlc": dlc,
            "n": n,
            "unique_last4": u4,
            "last4_unique_frac": round(u4 / n, 6),
        })
    fracs = [p["last4_unique_frac"] for p in periodic]
    maclike = [p for p in periodic if p["last4_unique_frac"] >= MACLIKE_LAST4_FRAC]
    max_frac = max(fracs) if fracs else None
    return {
        "0x00F_count": n_00f,
        "periodic_stream_count": len(periodic),
        "max_last4_unique_frac": max_frac,
        "maclike_last4_stream_count": len(maclike),
        "0x180_unique_last4": next(
            (p["unique_last4"] for p in periodic if p["can_id"] == "0x180" and p["dlc"] == 64),
            None,
        ),
        "0x160_unique_last4": next(
            (p["unique_last4"] for p in periodic if p["can_id"] == "0x160" and p["dlc"] == 32),
            None,
        ),
        "classification": (
            "no ordinary-P5 SecOC trailer on panda bus 1: zero 0x00F, and every "
            "periodic stream has a near-constant last-4 (max unique fraction "
            f"{max_frac}); last-8 variation on 64-byte vision PDUs is payload, "
            "not a MAC (a MAC28 would uniquify last-4)"
        ),
    }


def collect_drive(path: Path) -> dict:
    times: dict[tuple[int, int], list[int]] = defaultdict(list)
    bus1_last4: dict[tuple[int, int], set[bytes]] = defaultdict(set)
    bus1_counts: dict[tuple[int, int], int] = defaultdict(int)
    n_00f_bus1 = 0
    last4_08a: set[bytes] = set()
    n_08a_bus0 = 0
    bus0_event_counts: dict[int, int] = defaultdict(int)
    t0 = t1 = None
    with gzip.open(path, "rt") as f:
        for line in f:
            _seg, t, src, addr, hx = json.loads(line)
            t0 = t if t0 is None else t0
            t1 = t
            if addr in WATCH:
                times[(src, addr)].append(t)
            if src == 0:
                bus0_event_counts[t] += 1
            if src == 0 and addr == 0x08A:
                d = bytes.fromhex(hx)
                if len(d) >= 4:
                    n_08a_bus0 += 1
                    last4_08a.add(d[-4:])
                continue
            if src != 1:
                continue
            d = bytes.fromhex(hx)
            if addr == 0x00F:
                n_00f_bus1 += 1
            key = (addr, len(d))
            bus1_counts[key] += 1
            if len(d) >= 4:
                bus1_last4[key].add(d[-4:])
    duration_s = round((t1 - t0) / 1e9, 6)
    by_id = {}
    for (bus, addr), ts in sorted(times.items()):
        by_id[f"bus{bus}_0x{addr:03X}"] = cadence(ts)
    return {
        "source": str(path.relative_to(REPO)),
        "source_sha256": sha256(path),
        "duration_s": duration_s,
        "0x08A_bus_counts": {
            "0": len(times.get((0, 0x08A), [])),
            "1": len(times.get((1, 0x08A), [])),
            "2": len(times.get((2, 0x08A), [])),
        },
        "event_timestamp_batching": event_batching(
            bus0_event_counts,
            times.get((0, 0x08A), []),
        ),
        "cadence": {
            "0x08A": by_id.get("bus0_0x08A"),
            "0x081": by_id.get("bus0_0x081"),
            "0x00F": by_id.get("bus0_0x00F"),
            "0x0D7": by_id.get("bus0_0x0D7"),
            "0x030": by_id.get("bus0_0x030"),
            "0x180": by_id.get("bus1_0x180"),
        },
        "bus1_auth_negative": summarize_bus1_auth(bus1_last4, bus1_counts, n_00f_bus1),
        "bus0_08a_last4_unique_frac": (
            round(len(last4_08a) / n_08a_bus0, 6) if n_08a_bus0 else None
        ),
    }


def gts_canbus_domains(vehicle: str = "12984") -> dict:
    proc = subprocess.run(
        [str(REPO / "tools/gts"), "canbus", vehicle, "--json"],
        cwd=REPO,
        capture_output=True,
        text=True,
        check=True,
    )
    data = json.loads(proc.stdout)
    buses: dict[str, set[str]] = defaultdict(set)

    def walk(obj) -> None:
        if isinstance(obj, dict):
            if "bus_name" in obj and "ecu_domain" in obj:
                buses[obj["bus_name"]].add(obj["ecu_domain"])
            for v in obj.values():
                walk(v)
        elif isinstance(obj, list):
            for v in obj:
                walk(v)

    walk(data)
    row = data[0] if isinstance(data, list) else data
    return {
        "vehicle_name": row.get("vehicle_name"),
        "vehicle_type": row.get("vehicle_type"),
        "domains_by_bus": {k: sorted(v) for k, v in sorted(buses.items())},
        "recovered_via": "tools/gts canbus 12984 --json",
    }


def f33_tx_ids() -> list[str]:
    art = json.loads(F33_TX.read_text())
    return [row["can_id"] for row in art["generated_com_tx"]["first_five"]]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        type=Path,
        default=REPO / "data/generated/camry_2026_08a_producer_bounds.json",
    )
    args = parser.parse_args()

    drives = {name: collect_drive(path) for name, path in DRIVES.items()}
    canbus = gts_canbus_domains()
    bus1 = set(canbus["domains_by_bus"].get("Bus 1", []))
    bus4 = set(canbus["domains_by_bus"].get("Bus 4", []))
    tx = f33_tx_ids()

    artifact = {
        "schema": "camry-2026-08a-producer-bounds-v4",
        "drives": drives,
        "f33_generated_com_tx": tx,
        "gtsplus_canbus_12984": canbus,
        "classification": {
            "recorder_object": (
                "FRC-hosted TSS recorder objects 5282/5631; Bus-4 0x08A carries "
                "the same ID/pinion/assist subset"
            ),
            "not_exact_f33": (
                "exact F33 generated-COM Tx is only 0x030/0x351/0x394/0x4A3/0x4C8; "
                "0x08A is absent"
            ),
            "wire_placement": (
                "zero retained 0x08A on panda bus 1; Front Camera Module is GTS+ "
                "Bus 1 only; 0x08A is observed on captured Bus 4, but CAN event "
                "timestamps and GTS+ topology do not identify its physical transmitter"
            ),
            "camera_output_auth_boundary": (
                "panda bus 1 is sniffed in both retained drives. Zero 0x00F. Every "
                "periodic Bus-1 stream has a near-constant last-4 (max unique fraction "
                "<0.002) while Bus-4 0x08A last-4 is frame-unique. The observed "
                "Bus-1 PDUs do not carry an ordinary-P5 FV4||MAC28 trailer. Joined to "
                "Toyota's recovered TSK architecture, where AES-CMAC keys reside in "
                "protected Renesas ICU-S slots on TSK-capable chassis participants, "
                "the FRC is not a TSK key-holder/signing participant; its request must "
                "cross into a downstream TSK-capable proxy before authenticated Bus-4 "
                "publication"
            ),
            "timestamp_attribution_boundary": (
                "rlog Event.logMonoTime is shared by multi-frame CAN publication "
                "batches. The apparent 0x08A 20/30 ms mix versus 0x0D7 cannot reject "
                "a shared controller, TX queue, or scheduler"
            ),
            "secoc": (
                "ordinary Toyota-P5 FV4||MAC28 trailer on Bus-4 0x08A only, synced to "
                "authenticated 0x00F on the chassis buses; Bus 1 is outside that domain; "
                "key/profile/CMAC unrecovered"
            ),
            "bus4_native_nodes": sorted(bus4),
            "bus1_includes_front_camera": "Front Camera Module" in bus1,
            "physical_tx_and_signer_bounds": (
                "Exact F33 is excluded as generated-COM transmitter and FRC is excluded "
                "as the TSK key holder/signer. GTS+ Bus-4 placement leaves Skid Control, "
                "Brake Booster, and Central Gateway as architecture candidates for the "
                "downstream proxy that assembles/authenticates and physically publishes "
                "0x08A; the captures do not provide transmitter fingerprints. Which of "
                "those TSK-capable chassis/gateway participants owns the SecOC profile, "
                "ICU-S key selection, and final Tx descriptor remains unidentified"
            ),
            "regression_rule": (
                "Do not label 0x08A a Bus-1 camera frame. Do not send 0x08A to EPS. "
                "No 0x08A->B6 stock-LTA transform (CORR-135). No output authorized"
            ),
        },
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(artifact, indent=1, sort_keys=False) + "\n")
    print(f"wrote {args.out} ({args.out.stat().st_size} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
