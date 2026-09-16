#!/usr/bin/env python3
"""Reduce existing Camry captures for the port audit, without accessing a vehicle.

The September 10 routes used the temporary repin; September 11 used stock
Toyota-B and a non-publishing EPS. Keep these source populations separate.
"""
from __future__ import annotations

import argparse
import binascii
from collections import Counter
import gzip
import hashlib
import json
from pathlib import Path
import statistics
import sys

ROOT = Path(__file__).resolve().parents[4]
DEFAULT_LOGS = ROOT.parents[1] / "logs/camry-2026"
DEFAULT_OPENPILOT = ROOT.parent / "kai-openpilot"
IDS = {0x025, 0x030, 0x08A, 0x0AA, 0x0FE, 0x101, 0x116, 0x127, 0x160,
       0x180, 0x183, 0x185, 0x251, 0x3B7, 0x3F6, 0x412, 0x51E, 0x610, 0x614, 0x620, 0x622}
ROUTES = (
    ("working_repin", "2026-09-10/0000008d--a9f348691a", (2, 3, 6)),
    ("working_repin_corroboration", "2026-09-10/00000093--4066e7ae51", (3,)),
    ("stock_harness_eps_absent", "2026-09-11/000000d1--ad906be282", (3, 9)),
    ("stock_harness_combined_long", "2026-09-11/000000d4--327b2c4bb8", (3,)),
)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def signed(value: int, bits: int) -> int:
    return value - (1 << bits) if value & (1 << (bits - 1)) else value


def stock_longitudinal_bounds(path: Path) -> dict:
    n = bad_crc = outside = high_bit = 0
    examples = []
    with gzip.open(path, "rt") as f:
        for line in f:
            segment, timestamp, bus, address, text = json.loads(line)
            if bus != 1 or address != 0x160:
                continue
            d = bytes.fromhex(text)
            fine = signed(int.from_bytes(d[4:6], "big") & 0x7FFF, 15)
            coarse = -100 * signed(d[12] & 0x7F, 7)
            crc_valid = int.from_bytes(d[:2], "little") == binascii.crc_hqx(d[2:] + b"\x60\x01", 0xFFFF)
            bad_crc += not crc_valid
            high_bit += bool(d[12] & 0x80)
            n += 1
            exceeds = not (-1500 <= fine <= 1300 and -1500 <= coarse <= 1300)
            outside += exceeds
            if exceeds and len(examples) < 3:
                examples.append({"segment": segment, "timestamp_ns": timestamp, "data": text,
                                 "fine_raw": fine, "coarse_scaled_100": coarse})
    return {"source": str(path.relative_to(ROOT)), "sha256": sha256(path), "frames": n,
            "bad_crc": bad_crc, "outside_host_command_bounds": outside, "b12_high_bit_set": high_bit,
            "examples": examples,
            "boundary": "Native copies must not be clipped to host request limits; quantity names/causal Camry command mapping are not proved by this census."}


def summarize(values: list[float]) -> dict | None:
    return {"n": len(values), "min": min(values), "median": statistics.median(values),
            "max": max(values), "distinct": len(set(values))} if values else None


def reduce_log(path: Path, logs_root: Path, LogReader) -> dict:
    counts = Counter()
    examples = {}
    modes = Counter()
    lateral_modes = Counter()
    cp_values = None
    stiffness, steer_ratio, delays = [], [], []
    delay_states = Counter()
    p05 = Counter()
    for e in LogReader(str(path)):
        w = e.which()
        if w == "can":
            for m in e.can:
                if m.src >= 3 or m.address not in IDS:
                    continue
                key = (m.address, m.src, len(m.dat))
                counts[key] += 1
                examples.setdefault(key, {"timestamp_ns": e.logMonoTime, "data": bytes(m.dat).hex()})
                if m.address == 0x251 and len(m.dat) == 8:
                    modes[(m.src, m.dat[0])] += 1
                if m.address == 0x08A and len(m.dat) == 32:
                    lateral_modes[(m.src, m.dat[21] & 0x3F)] += 1
                if m.address in (0x160, 0x180, 0x183, 0x185) and len(m.dat) in (32, 64):
                    valid = int.from_bytes(m.dat[:2], "little") == binascii.crc_hqx(m.dat[2:] + m.address.to_bytes(2, "little"), 0xFFFF)
                    p05[(m.address, valid)] += 1
        elif w == "carParams":
            cp = e.carParams
            cp_values = {"steerRatio": cp.steerRatio, "tireStiffnessFactor": cp.tireStiffnessFactor,
                         "tireStiffnessFront": cp.tireStiffnessFront, "tireStiffnessRear": cp.tireStiffnessRear,
                         "steerActuatorDelay": cp.steerActuatorDelay}
        elif w == "vehicleParameters":
            stiffness.append(e.vehicleParameters.stiffnessFactor)
            steer_ratio.append(e.vehicleParameters.steerRatio)
        elif w == "lateralDelay":
            d = e.lateralDelay
            delays.append(d.lateralDelayEstimate)
            delay_states[(str(d.status), d.validBlocks)] += 1
    return {
        "source": str(path.relative_to(logs_root)), "sha256": sha256(path), "bytes": path.stat().st_size,
        "native_can": [{"address": f"0x{a:03X}", "bus": b, "length": length, "n": n, **examples[(a, b, length)]}
                       for (a, b, length), n in sorted(counts.items())],
        "cruise_mode_b0": [{"bus": bus, "value": f"0x{value:02X}", "n": n} for (bus, value), n in sorted(modes.items())],
        "upstream_lateral_id": [{"bus": bus, "id": value, "n": n} for (bus, value), n in sorted(lateral_modes.items())],
        "p05": [{"address": f"0x{a:03X}", "valid": valid, "n": n} for (a, valid), n in sorted(p05.items())],
        "recorded_car_params": cp_values, "learned_stiffness_multiplier": summarize(stiffness),
        "learned_steer_ratio": summarize(steer_ratio), "lag_estimates": summarize(delays),
        "lag_status": [{"status": status, "valid_blocks": blocks, "n": n} for (status, blocks), n in sorted(delay_states.items())],
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--logs-root", type=Path, default=DEFAULT_LOGS)
    ap.add_argument("--openpilot-root", type=Path, default=DEFAULT_OPENPILOT)
    ap.add_argument("--out", type=Path, default=ROOT / "data/generated/camry_20260915_port_evidence_audit.json")
    args = ap.parse_args()
    sys.path.insert(0, str(args.openpilot_root))
    from openpilot.tools.lib.logreader import LogReader
    result = {
        "schema": "camry-port-evidence-audit-v1",
        "vehicle_access": False,
        "scope": "seven source-pinned rlog segments plus both complete August-27 CAN captures; not a full-fleet qualification",
        "route_groups": {name: [reduce_log(args.logs_root / route / f"rlog-{segment}.zst", args.logs_root, LogReader)
                                for segment in segments] for name, route, segments in ROUTES},
        "native_longitudinal_handoff": [stock_longitudinal_bounds(ROOT / "targets/camry-2026/raw-20260827" / filename)
                                       for filename in ("camry_relay_route_can_20260827.ndjson.gz", "camry_relay_lta_confirm_route_can_20260827.ndjson.gz")],
        "boundaries": [
            "Stock-harness samples have an absent EPS and cannot qualify healthy-stock-harness steering.",
            "The working steering samples use conventional cruise, not a demonstrated adaptive-cruise lifecycle.",
            "Repeated cached lag estimates are not fresh independent lag measurements.",
            "GTS meanings for Control Mode/Permission/ACC Not Available remain diagnostic fields, not CAN overlays.",
        ],
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
