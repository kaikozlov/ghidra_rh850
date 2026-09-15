#!/usr/bin/env python3
"""Anchor TSS3 radar units to retained vision, wheel speed, and calibrated gyro.

Default reduction uses a compact, raw-object-byte fixture. --extract recreates
that fixture from the specified original rlogs; it never accesses a vehicle.
Diagnostic FFD encodings are NOT treated as CAN wire layouts.
"""
from __future__ import annotations
import argparse
import gzip
import hashlib
import io
import json
import sys
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[4]
FIXTURE = ROOT / "tests/fixtures/camry_2026_radar_anchors.jsonl.gz"
OUTPUT = ROOT / "data/generated/camry_2026_radar_anchors.json"
LOG_ROOT = Path("/Users/kai/dev/inspect/logs/camry-2026")
OPENPILOT = Path("/Users/kai/dev/inspect/repos/kai-openpilot")
ROUTE3B = "0000003b--62262eb7a1"
ROUTE8D = "0000008d--a9f348691a"
ROUTE93 = "00000093--4066e7ae51"
VISION_SEGMENTS = list(range(0, 109, 9))
POSE_SEGMENTS = {ROUTE3B: [54, 72, 81, 90], ROUTE8D: [2, 4, 6], ROUTE93: [3]}
EMPTY = bytes.fromhex("fff8000000ffff")


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def signed(value: int, bits: int) -> int:
    return value - (1 << bits) if value & (1 << (bits - 1)) else value


def decode(geometry: bytes, motion: bytes) -> tuple[float, float, float]:
    return (int.from_bytes(geometry[:2], "big") * 0.005,
            signed(int.from_bytes(geometry[2:4], "big") >> 4, 12) * 0.04,
            signed(int.from_bytes(motion[1:3], "big") & 0x3FFF, 14) * 0.025)


def stats(values) -> dict:
    x = np.asarray(values, dtype=float)
    return {"n": len(x), "p05_median_p95": np.quantile(x, [0.05, 0.5, 0.95]).round(8).tolist()} if len(x) else {"n": 0}


def fit(x, y) -> dict:
    x, y = np.asarray(x, dtype=float), np.asarray(y, dtype=float)
    if len(x) < 4 or np.std(x) == 0:
        return {"n": len(x)}
    slope, offset = np.polyfit(x, y, 1)
    return {"n": len(x), "pearson_r": round(float(np.corrcoef(x, y)[0, 1]), 8),
            "slope": round(float(slope), 8), "intercept": round(float(offset), 8),
            "absolute_error": stats(abs(x - y))}


def extract(fixture: Path, log_root: Path, openpilot: Path) -> None:
    sys.path.insert(0, str(openpilot))
    from openpilot.tools.lib.logreader import LogReader
    from openpilot.selfdrive.locationd.helpers import Pose, PoseCalibrator
    source_rows, observations = [], []
    for route in (ROUTE3B, ROUTE8D, ROUTE93):
        segments = sorted(set(POSE_SEGMENTS[route] + (VISION_SEGMENTS if route == ROUTE3B else [])))
        for segment in segments:
            date = "2026-09-04" if route == ROUTE3B else "2026-09-10"
            path = log_root / date / route / f"rlog-{segment}.zst"
            source_index = len(source_rows)
            source_rows.append({"path": str(path.relative_to(log_root)), "sha256": digest(path)})
            cal = PoseCalibrator()
            speed, yaw, objects = [], [], []
            packets, last_pair = {}, {}
            current_speed = 0.0
            model_samples = 0
            for event in LogReader(str(path)):
                t, which = event.logMonoTime, event.which()
                if which == "extrinsicsCalibration":
                    cal.feed_extrinsics_calibration(event.extrinsicsCalibration)
                elif which == "carState":
                    current_speed = float(event.carState.vEgo)
                    speed.append((t, current_speed))
                elif which == "deviceMotion" and cal.calib_valid and event.deviceMotion.angularVelocityDevice.valid:
                    pose = cal.build_calibrated_pose(Pose.from_device_motion(event.deviceMotion))
                    yaw.append((t, -float(pose.angular_velocity.z)))  # paramsd left-positive convention
                elif which == "can":
                    for frame in event.can:
                        # These specified routes used the historical repin. Bus 1
                        # here is ADAS, not the final stock-Toyota-B parser bus.
                        if frame.src != 1 or not 0x180 <= frame.address <= 0x185 or len(frame.dat) != 64:
                            continue
                        packets[frame.address] = (t, bytes(frame.dat))
                        bank = (frame.address - 0x180) % 3
                        if 0x180 + bank not in packets or 0x183 + bank not in packets:
                            continue
                        ta, a = packets[0x180 + bank]
                        tb, b = packets[0x183 + bank]
                        if a[2:4] != b[2:4] or abs(ta - tb) > 50_000_000 or last_pair.get(bank) == (ta, tb):
                            continue
                        last_pair[bank] = (ta, tb)
                        for slot in range(8):
                            off = 4 + 7 * slot
                            objects.append((ta, bank * 8 + slot, a[off:off+7], b[off:off+7]))
                elif which == "modelV2" and route == ROUTE3B and segment in VISION_SEGMENTS:
                    if not event.modelV2.leadsV3:
                        continue
                    lead = event.modelV2.leadsV3[0]
                    if lead.prob < 0.9 or not lead.x:
                        continue
                    model_samples += 1
                    if model_samples % 3:  # deterministic decimation, before looking at candidate matches
                        continue
                    candidates = []
                    for bank in range(3):
                        if 0x180 + bank not in packets or 0x183 + bank not in packets:
                            continue
                        ta, a = packets[0x180 + bank]
                        tb, b = packets[0x183 + bank]
                        if t - ta > 100_000_000 or t - tb > 100_000_000 or a[2:4] != b[2:4]:
                            continue
                        for slot in range(8):
                            off = 4 + 7 * slot
                            raw_a, raw_b = a[off:off+7], b[off:off+7]
                            if raw_a != EMPTY:
                                candidates.append([raw_a.hex(), raw_b.hex()])
                    # Selection/rejection runs later from raw bytes and does not
                    # use lateral position: lateral is the held-out observable.
                    observations.append(["vision", source_index, t, float(lead.x[0]) - 1.52,
                                         -float(lead.y[0]), float(lead.v[0]) - current_speed, current_speed, candidates])
            if segment in POSE_SEGMENTS[route] and yaw and speed:
                yaw, speed = np.asarray(yaw), np.asarray(speed)
                previous = {}
                for t, slot, a, b in sorted(objects):
                    if a == EMPTY:
                        previous.pop(slot, None)
                        continue
                    x, y, vr = decode(a, b)
                    v = float(np.interp(t, speed[:, 0], speed[:, 1]))
                    w = float(np.interp(t, yaw[:, 0], yaw[:, 1]))
                    if slot in previous:
                        pt, pa, pb, pv, pw = previous[slot]
                        px, py, pvr = decode(pa, pb)
                        dt = (t - pt) * 1e-9
                        # Inferred stationary, continuity-qualified cohort. This
                        # is NOT an OEM object-class/track-validity claim.
                        if (.035 <= dt <= .065 and abs((x-px)/dt - (vr+pvr)/2) < 1.5
                                and abs(vr-pvr) < 2 and abs(vr+v) < 1.5 and abs(pvr+pv) < 1.5
                                and v > 3 and abs(w) > .01 and abs(w*x) > .3 and abs(y-py) < 1.6):
                            observations.append(["motion", source_index, pt, t, slot,
                                                 pa.hex(), pb.hex(), a.hex(), b.hex(), pv, v, pw, w])
                    previous[slot] = (t, a, b, v, w)
            print(f"extracted {route}/{segment}", flush=True)
    header = {"schema": "camry-radar-independent-anchor-fixture-v1", "sources": source_rows,
              "source_bus": 1, "source_topology": "historical physical CAN0/CAN1 repin",
              "gyro_anchor": "negative calibrated angularVelocityDevice.z (paramsd left-positive)",
              "vision_anchor": "leadsV3[0], probability>=0.9, x-1.52m, -y, v-carState.vEgo; every third eligible sample"}
    fixture.parent.mkdir(parents=True, exist_ok=True)
    with fixture.open("wb") as raw:
        with gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=0) as gz:
            with io.TextIOWrapper(gz, encoding="utf-8") as text:
                for row in [header, *observations]:
                    text.write(json.dumps(row, separators=(",", ":")) + "\n")


def reduce(fixture: Path) -> dict:
    motion, vision, widths = [], [], {str(bits): 0 for bits in (10, 11, 12, 13, 14, 15)}
    with gzip.open(fixture, "rt") as f:
        header = json.loads(next(f))
        for line in f:
            row = json.loads(line)
            if row[0] == "vision":
                _, source, t, lx, ly, lv, ego, candidates = row
                matches = []
                for a, b in candidates:
                    a, b = bytes.fromhex(a), bytes.fromhex(b)
                    x, y, vr = decode(a, b)
                    word = int.from_bytes(b[1:3], "big")
                    for bits in (10, 11, 12, 13, 14, 15):
                        widths[str(bits)] += signed(word & ((1 << bits)-1), bits) != signed(word & ((1 << (bits+1))-1), bits+1)
                    matches.append((abs(x-lx)+2*abs(vr-lv), x, y, vr))
                matches.sort()
                if not matches:
                    continue
                score, x, y, vr = matches[0]
                if abs(x-lx) > max(2., .1*lx) or abs(vr-lv) > 2 or (len(matches)>1 and matches[1][0]-score < 2):
                    continue
                vision.append((lx, x, ly, y, lv, vr, source))
            else:
                _, source, pt, t, slot, pa, pb, a, b, pv, v, pw, w = row
                px, py, _ = decode(bytes.fromhex(pa), bytes.fromhex(pb))
                x, y, _ = decode(bytes.fromhex(a), bytes.fromhex(b))
                dt = (t-pt)*1e-9
                predicted = -.5*(pw*px+w*x)
                measured = (y-py)/dt
                motion.append((predicted, measured, source))
    m, v = np.asarray(motion), np.asarray(vision)
    offcenter = abs(v[:, 2]) > .5
    yaw_fit = fit(m[:, 0], m[:, 1])
    return {
        "schema": "camry-radar-independent-anchors-v1",
        "fixture": {"path": str(fixture.relative_to(ROOT)), "sha256": digest(fixture), "sources": header["sources"]},
        "wire_decode": {"distance_m_per_word": .005, "lateral_m_per_signed12": .04,
                        "lateral_positive": "left", "relative_speed_m_s_per_signed14": .025,
                        "speed_width_boundary": "at least 13 bits required; signed13 and signed14 agree in retained data; B1[7:6] independently vary"},
        "vision_selection": "range/velocity only, score=abs(range error)+2*abs(velocity error); gap>=2 to runner-up; range error<=max(2m,10%); velocity error<=2m/s",
        "vision_range": fit(v[:, 0], v[:, 1]),
        "vision_relative_speed": fit(v[:, 4], v[:, 5]),
        "vision_lateral_offcenter": fit(v[offcenter, 2], v[offcenter, 3]),
        "vision_lateral_inverted_error": stats(abs(v[offcenter, 2]+v[offcenter, 3])),
        "gyro_lateral_derivative": yaw_fit,
        "gyro_implied_lateral_lsb": round(.04 / yaw_fit["slope"], 8),
        "gyro_inverted_sign_error": stats(abs(m[:, 0]+m[:, 1])),
        "narrow_velocity_wrap_disagreements": widths,
        "boundaries": ["range and range-rate agreement alone cannot determine their common scale",
                       "stationary-object membership is inferred from continuity and velocity, not an OEM validity bit",
                       "OEM object validity, confidence, and silent slot reassignment remain unresolved; no production radar-enable decision follows automatically",
                       "cached lagd outputs are not independent fresh identifications"],
    }


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--extract", action="store_true")
    ap.add_argument("--fixture", type=Path, default=FIXTURE)
    ap.add_argument("--out", type=Path, default=OUTPUT)
    ap.add_argument("--log-root", type=Path, default=LOG_ROOT)
    ap.add_argument("--openpilot-root", type=Path, default=OPENPILOT)
    args = ap.parse_args()
    if args.extract:
        extract(args.fixture, args.log_root, args.openpilot_root)
    result = reduce(args.fixture)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(args.out)


if __name__ == "__main__":
    main()
