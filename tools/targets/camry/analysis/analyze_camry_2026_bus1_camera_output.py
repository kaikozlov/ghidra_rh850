#!/usr/bin/env python3
"""Decode retained Toyota Bus-1 camera/radar output with GTS+ vocabulary.

GTS+ is DID/FFD keyed, not a CAN DBC. This joins the sniffed panda-bus-1
0x180 family to recovered FRC Data List / Operation-FFD scales, and tests
whether FRC's TSS request object (5282 ID||pinion||assist) is on that native
bus. It does not invent a 64-byte OEM field map where the corpus has none.
"""
from __future__ import annotations

import argparse
import binascii
import gzip
import hashlib
import json
import math
import statistics
import subprocess
from collections import Counter, defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
RAW = REPO / "targets/camry-2026/raw-20260827"
DRIVES = {
    "drive_a": RAW / "camry_relay_route_can_20260827.ndjson.gz",
    "drive_b": RAW / "camry_relay_lta_confirm_route_can_20260827.ndjson.gz",
}
PCS = REPO / "data/generated/gtsplus_2026/pcs_data_viewer_tss3_managed_semantics.json"

EMPTY7 = bytes.fromhex("fff8000000ffff")
SLOT_N = 8
SLOT_LEN = 7
HEADER_LEN = 4
TRAILER_LEN = 4
FAMILY = range(0x180, 0x18D)
DIST_LSB_M = 0.005  # independent vision/range anchor, not the FFD encoding
LAT_LSB_M = 0.04  # independent calibrated-gyro and vision anchors, left-positive
REL_SPEED_LSB_M_S = 0.025  # independent vision/ego-speed anchors; low14 word
DIST_MAX_M = 500.0
# FFD 5282 consecutive layout: byte1 ID, bytes2-3 s16be pinion, byte4 assist.
JOIN_WINDOW_NS = 25_000_000
JOIN_MIN_ABS = 20
JOIN_MAX_SAMPLES = 200


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def summarize(xs: list[float]) -> dict | None:
    if not xs:
        return None
    xs = sorted(xs)
    n = len(xs)
    return {
        "n": n,
        "min": round(xs[0], 3),
        "p05": round(xs[n // 20], 3),
        "median": round(xs[n // 2], 3),
        "p95": round(xs[19 * n // 20], 3),
        "max": round(xs[-1], 3),
    }


def signed(value: int, bits: int) -> int:
    sign = 1 << (bits - 1)
    return value - (1 << bits) if value & sign else value


def decode_object_geometry(slot: bytes) -> tuple[float, float]:
    """Recover the first 7-byte record: u16 range + s12 lateral geometry."""
    if len(slot) != SLOT_LEN:
        raise ValueError("object slot must be exactly 7 bytes")
    distance_m = int.from_bytes(slot[0:2], "big") * DIST_LSB_M
    lateral_raw = (slot[2] << 4) | (slot[3] >> 4)
    lateral_m = signed(lateral_raw, 12) * LAT_LSB_M
    return distance_m, lateral_m


def decode_object_relative_speed(slot: bytes) -> float:
    """Decode the low14 velocity word; B1[7:6] are independent flags."""
    if len(slot) != SLOT_LEN:
        raise ValueError("object slot must be exactly 7 bytes")
    raw = ((slot[1] & 0x3F) << 8) | slot[2]
    return signed(raw, 14) * REL_SPEED_LSB_M_S


def pearson(xs: list[float], ys: list[float]) -> float:
    if len(xs) != len(ys) or len(xs) < 2:
        return float("nan")
    mx = statistics.fmean(xs)
    my = statistics.fmean(ys)
    dx = [x - mx for x in xs]
    dy = [y - my for y in ys]
    den = math.sqrt(sum(x * x for x in dx) * sum(y * y for y in dy))
    return sum(x * y for x, y in zip(dx, dy, strict=True)) / den if den else float("nan")


def joined_object_family(bursts: dict[tuple[int, int, int], dict[int, tuple[int, bytes]]]) -> dict:
    """Join 0x180..0x18B into three banks x four records x eight object slots."""
    decoded: list[tuple[int, int, int, float, float, float]] = []
    # seg, timestamp, object index, distance, lateral, relative speed
    complete = 0
    empty = 0
    occupied = 0
    for (seg, _counter, bank), records in sorted(bursts.items(), key=lambda item: min(v[0] for v in item[1].values())):
        if set(records) != {0, 1, 2, 3}:
            continue
        complete += 1
        timestamp = min(v[0] for v in records.values())
        payloads = [records[group][1] for group in range(4)]
        for slot_idx in range(SLOT_N):
            slots = [p[HEADER_LEN + slot_idx * SLOT_LEN:HEADER_LEN + (slot_idx + 1) * SLOT_LEN] for p in payloads]
            if slots[0] == EMPTY7:
                empty += 1
                continue
            occupied += 1
            distance_m, lateral_m = decode_object_geometry(slots[0])
            relative_speed_m_s = decode_object_relative_speed(slots[1])
            decoded.append((seg, timestamp, bank * SLOT_N + slot_idx, distance_m, lateral_m, relative_speed_m_s))

    # Kinematic validation: same slot, same segment, short 20 Hz step, continuous
    # range/lateral geometry. Large discontinuities are excluded, but silent
    # same-slot reassignment is not proved absent by this filter.
    prev: dict[tuple[int, int], tuple[int, float, float]] = {}
    range_rate: list[float] = []
    encoded_vrel: list[float] = []
    for seg, timestamp, obj, distance_m, lateral_m, relative_speed_m_s in decoded:
        key = (seg, obj)
        if key in prev:
            pt, pd, py = prev[key]
            dt = (timestamp - pt) * 1e-9
            if 0.035 <= dt <= 0.065 and abs(distance_m - pd) < 2.5 and abs(lateral_m - py) < 1.0:
                drdt = (distance_m - pd) / dt
                if abs(drdt) <= 50:
                    range_rate.append(drdt)
                    encoded_vrel.append(relative_speed_m_s)
        prev[key] = (timestamp, distance_m, lateral_m)

    diffs = [a - b for a, b in zip(range_rate, encoded_vrel, strict=True)]
    corr = pearson(range_rate, encoded_vrel)
    slope = intercept = float("nan")
    if len(range_rate) >= 2:
        mx = statistics.fmean(encoded_vrel)
        my = statistics.fmean(range_rate)
        denom = sum((x - mx) ** 2 for x in encoded_vrel)
        if denom:
            slope = sum((x - mx) * (y - my) for x, y in zip(encoded_vrel, range_rate, strict=True)) / denom
            intercept = my - slope * mx
    return {
        "bank_layout": {
            "bank0": ["0x180", "0x183", "0x186", "0x189"],
            "bank1": ["0x181", "0x184", "0x187", "0x18A"],
            "bank2": ["0x182", "0x185", "0x188", "0x18B"],
            "object_slots_per_bank": SLOT_N,
            "record_bytes_per_object": SLOT_LEN * 4,
        },
        "complete_bursts": complete,
        "empty_objects": empty,
        "occupied_objects": occupied,
        "distance_m": summarize([row[3] for row in decoded]),
        "lateral_m_s12_lsb_0_04": summarize([row[4] for row in decoded]),
        "relative_speed_m_s_s14_lsb_0_025": summarize([row[5] for row in decoded]),
        "kinematic_validation": {
            "n": len(diffs),
            "pearson_r": round(corr, 6),
            "median_abs_error_m_s": round(statistics.median(abs(x) for x in diffs), 6) if diffs else None,
            "rmse_m_s": round(math.sqrt(statistics.fmean(x * x for x in diffs)), 6) if diffs else None,
            "fit_range_rate_from_encoded_vrel": {
                "slope": round(slope, 6),
                "intercept_m_s": round(intercept, 6),
            },
            "continuity_filter": "35..65 ms, |delta range|<2.5 m, |delta lateral|<1.0 m, |range rate|<=50 m/s",
        },
        "wire_fields": {
            "record0_distance": "B0:B1 u16be * 0.005 m",
            "record0_lateral": "B2:B3[7:4] signed12be * 0.04 m, left-positive",
            "record1_relative_speed": "B1[5:0]||B2[7:0] signed14be * 0.025 m/s",
        },
    }


def gts_vocabulary() -> dict:
    """OEM names/scales from tracked FFD tables plus live FRC Data List."""
    pcs = json.loads(PCS.read_text())
    rows = pcs["operation_ffd"]["detail_rows"]
    wanted = {
        "5A22": "vertical/longitudinal distance u16 LSB 0.01 m",
        "5A24": "lateral position s16 LSB 0.01 m",
        "5A26": "relative speed s16 LSB 0.05 m/s",
        "590C": "ACC control-target floats (distance/lateral/rel-speed Type f)",
        "5A30": "left lane boundary offset/yaw Type f",
        "5A33": "right lane boundary offset/yaw Type f",
        "5737": "control-target lateral corners s11 LSB 0.05 m",
        "5738": "control-target longitudinal corners u11 LSB 0.05 m",
        "573C": "relative speed for control target s10 LSB 0.1 m/s",
        "573D": "control-target object number u5",
        "573E": "target object number u5",
        "573F": "control-target object type u3",
        "57BA": "camera-target lateral position s12 LSB 0.05 m",
    }
    ffd = {}
    for row in rows:
        did = str(row.get("DataID"))
        if did not in wanted:
            continue
        ffd.setdefault(did, {"role": wanted[did], "fields": []})
        ffd[did]["fields"].append({
            "name": row["DataName"],
            "byte": row["BytePosition"],
            "bit": row["BitPosition"],
            "length": row["BitLength"],
            "type": row["Type"],
            "lsb": row["Lsb"],
            "data_size": row["DataSize"],
        })

    proc = subprocess.run(
        [str(REPO / "tools/gts"), "did", "FRC_P5", "--json", "--limit", "5000"],
        cwd=REPO,
        capture_output=True,
        text=True,
        check=True,
    )
    frc_rows = json.loads(proc.stdout)
    frc_want = {0x1804, 0x1805, 0x1806, 0x1909, 0x190A}
    frc = []
    for row in frc_rows:
        if row["primary_did"] not in frc_want:
            continue
        si = row.get("signal_info") or {}
        frc.append({
            "did": f"0x{row['primary_did']:04X}",
            "name": row["name"],
            "bit_start": row["bit_start"],
            "bit_end": row["bit_end"],
            "mul": si.get("mul"),
            "div": si.get("div"),
            "offset": si.get("offset"),
            "signed": si.get("signed"),
            "bit_width": si.get("bit_width"),
            "decimal_point_count": si.get("decimal_point_count"),
            "unit": si.get("unit"),
        })
    return {
        "boundary": (
            "GTS+ names quantities and diagnostic/FFD bit layouts. It does not "
            "emit BO_ 0x180. Wire packing and units need independent CAN/physics "
            "anchors; diagnostic scales do not transfer automatically."
        ),
        "frc_p5_geometry_dids": frc,
        "operation_ffd_object_layouts": ffd,
        "joined_distance_scale": {
            "lsb_m": DIST_LSB_M,
            "sources": [
                "independent retained model lead / wheel-speed / calibrated-gyro anchors",
                "data/generated/camry_2026_radar_anchors.json (FFD 5A22 is NOT a direct scale source)",
            ],
        },
    }


def sample_id11(id11: list[tuple[int, bytes, int, int]]) -> list[tuple[int, bytes, int, int]]:
    if not id11:
        return []
    step = max(1, len(id11) // JOIN_MAX_SAMPLES)
    return id11[::step][:JOIN_MAX_SAMPLES]


def join_5282_on_bus1(path: Path, id11: list[tuple[int, bytes, int, int]]) -> dict:
    """Test whether FRC's consecutive 5282 request layout is on native Bus 1."""
    samples = sample_id11(id11)
    empty = {
        "layout": "5282 byte1 Target Lateral ID || bytes2-3 pinion s16be || byte4 assist",
        "id11_min_abs_pinion": JOIN_MIN_ABS,
        "id11_qualifying": len(id11),
        "sampled": 0,
        "window_ns": JOIN_WINDOW_NS,
        "layout_hits_in_window": 0,
        "layout_hits_global_bus1": 0,
        "exact_pinion_2byte_in_window": 0,
        "exact_pinion_top": [],
    }
    if not samples:
        return empty
    buckets: dict[int, list[int]] = defaultdict(list)
    for i, (t, *_rest) in enumerate(samples):
        buckets[t // JOIN_WINDOW_NS].append(i)
    pats = {bytes([b21]) + angb + bytes([b24]) for _t, angb, b21, b24 in samples}
    per_exact = [False] * len(samples)
    per_layout = [False] * len(samples)
    exact_by: Counter[tuple[int, int]] = Counter()
    global_layout = 0
    with gzip.open(path, "rt") as f:
        for line in f:
            _seg, t, src, addr, hx = json.loads(line)
            if src != 1:
                continue
            d = bytes.fromhex(hx)
            for pat in pats:
                if pat in d:
                    global_layout += 1
                    break
            keys = {
                t // JOIN_WINDOW_NS,
                t // JOIN_WINDOW_NS - 1,
                t // JOIN_WINDOW_NS + 1,
            }
            idxs: list[int] = []
            for k in keys:
                idxs.extend(buckets.get(k, []))
            if not idxs:
                continue
            for i in idxs:
                tt, angb, b21, b24 = samples[i]
                if abs(t - tt) > JOIN_WINDOW_NS:
                    continue
                if angb in d:
                    per_exact[i] = True
                    exact_by[(addr, d.find(angb))] += 1
                if (bytes([b21]) + angb + bytes([b24])) in d:
                    per_layout[i] = True
    top = [
        {"can_id": f"0x{addr:03X}", "offset": off, "n": n}
        for (addr, off), n in sorted(
            exact_by.items(), key=lambda kv: (-kv[1], kv[0][0], kv[0][1])
        )[:8]
    ]
    return {
        **empty,
        "sampled": len(samples),
        "layout_hits_in_window": int(sum(per_layout)),
        "layout_hits_global_bus1": global_layout,
        "exact_pinion_2byte_in_window": int(sum(per_exact)),
        "exact_pinion_top": top,
    }


def collect_drive(path: Path) -> dict:
    streams: dict[tuple[int, int], int] = defaultdict(int)
    last4: dict[int, set[bytes]] = defaultdict(set)
    n_00f = 0
    occupied_dist: list[float] = []
    occupied_lat_hyp: list[float] = []
    occupied_rel_hyp: list[float] = []
    empty_slots = 0
    occupied_slots = 0
    occupied_dist_in_range = 0
    family_samples: dict[str, str] = {}
    n_180 = 0
    id11: list[tuple[int, bytes, int, int]] = []
    object_bursts: dict[tuple[int, int, int], dict[int, tuple[int, bytes]]] = defaultdict(dict)
    object_cycle: tuple[int, int, int] | None = None
    object_epoch = 0
    object_crc_valid = object_crc_invalid = 0
    pending_bursts = {}
    burst_serial = 0
    expired_bursts = 0
    with gzip.open(path, "rt") as f:
        for line in f:
            seg, t, src, addr, hx = json.loads(line)
            if src == 0 and addr == 0x08A:
                d08 = bytes.fromhex(hx)
                if len(d08) >= 25 and d08[21] == 11:
                    ang = int.from_bytes(d08[18:20], "big", signed=True)
                    if abs(ang) >= JOIN_MIN_ABS:
                        id11.append((t, bytes(d08[18:20]), d08[21], d08[24]))
            if src != 1:
                continue
            d = bytes.fromhex(hx)
            streams[(addr, len(d))] += 1
            if addr == 0x00F:
                n_00f += 1
            if addr in FAMILY and len(d) >= 4:
                last4[addr].add(d[-4:])
            if 0x180 <= addr <= 0x18B and len(d) == 64:
                bank = (addr - 0x180) % 3
                record_group = (addr - 0x180) // 3
                # P05 has an 8-bit B2 counter, not a monotonic B2:B3 u16.
                # B3 also repeats after 256 cycles. An occurrence ordinal keeps
                # every wrap in a segment instead of overwriting earlier data.
                cycle = (seg, d[2], d[3])
                if cycle != object_cycle:
                    object_epoch += 1
                    object_cycle = cycle
                valid = int.from_bytes(d[:2], "little") == binascii.crc_hqx(
                    d[2:] + addr.to_bytes(2, "little"), 0xFFFF,
                )
                object_crc_valid += valid
                object_crc_invalid += not valid
                if valid:
                    key = (seg, d[2], d[3], bank)
                    if key in pending_bursts and t - pending_bursts[key][1] > 50_000_000:
                        del pending_bursts[key]
                        expired_bursts += 1
                    if key not in pending_bursts:
                        burst_serial += 1
                        pending_bursts[key] = (burst_serial, t, {})
                    serial, _start, records = pending_bursts[key]
                    records[record_group] = (t, d)
                    if len(records) == 4:
                        object_bursts[(seg, serial, bank)] = records
                        del pending_bursts[key]
            if addr == 0x180:
                n_180 += 1
            if 0x180 <= addr <= 0x182 and len(d) == 64:
                body = d[HEADER_LEN: HEADER_LEN + SLOT_N * SLOT_LEN]
                for i in range(SLOT_N):
                    slot = body[i * SLOT_LEN:(i + 1) * SLOT_LEN]
                    if slot == EMPTY7:
                        empty_slots += 1
                        continue
                    occupied_slots += 1
                    dist_m = int.from_bytes(slot[0:2], "big", signed=False) * DIST_LSB_M
                    occupied_dist.append(dist_m)
                    if 0 < dist_m <= DIST_MAX_M:
                        occupied_dist_in_range += 1
                    occupied_lat_hyp.append(
                        int.from_bytes(slot[2:4], "big", signed=True) * 0.01
                    )
                    occupied_rel_hyp.append(
                        int.from_bytes(slot[4:6], "big", signed=True) * 0.05
                    )
            key = f"0x{addr:03X}/{len(d)}"
            if key not in family_samples and addr in FAMILY:
                family_samples[key] = d.hex()

    stream_rows = [
        {
            "can_id": f"0x{addr:03X}",
            "dlc": dlc,
            "n": n,
            "unique_last4": len(last4[addr]) if addr in last4 else None,
        }
        for (addr, dlc), n in sorted(streams.items(), key=lambda kv: kv[0][0])
        if n >= 50
    ]
    in_range_frac = (
        round(occupied_dist_in_range / occupied_slots, 6) if occupied_slots else None
    )
    lat = summarize(occupied_lat_hyp)
    rel = summarize(occupied_rel_hyp)
    return {
        "source": str(path.relative_to(REPO)),
        "source_sha256": sha256(path),
        "0x00F_count": n_00f,
        "periodic_streams": stream_rows,
        "0x180_n": n_180,
        "0x180_unique_last4": len(last4[0x180]),
        "object_cycle_integrity": {
            "crc_valid_frames": object_crc_valid,
            "crc_invalid_frames": object_crc_invalid,
            "chronological_cycle_occurrences": object_epoch,
            "counter_width_bits": 8,
            "join_key": "segment + counter bytes + bank, bounded to 50ms and consumed after completion",
            "incomplete_bursts": expired_bursts + len(pending_bursts),
        },
        "object_slots_0x180_0x182": {
            "header_bytes": HEADER_LEN,
            "slot_bytes": SLOT_LEN,
            "slots_per_pdu": SLOT_N,
            "trailer_bytes": TRAILER_LEN,
            "empty_sentinel": EMPTY7.hex(),
            "empty_slots": empty_slots,
            "occupied_slots": occupied_slots,
            "longitudinal_m_u16be_lsb_0_005": summarize(occupied_dist),
            "occupied_distance_in_range_frac": in_range_frac,
            "rejected_direct_ffd_5A24_lateral_s16_0_01": {
                "reason": (
                    "s16be at slot bytes 2-3 at FFD 5A24 LSB 0.01 m spans hundreds "
                    "of metres; not a 1:1 overlay"
                ),
                "span_m": lat,
            },
            "rejected_direct_ffd_5A26_relspeed_s16_0_05": {
                "reason": (
                    "s16be at slot bytes 4-5 at FFD 5A26 LSB 0.05 m/s is physically "
                    "impossible as relative speed"
                ),
                "span_m_s": rel,
            },
        },
        "family_first_samples": {k: family_samples[k] for k in sorted(family_samples)},
        "joined_object_family_0x180_0x18B": joined_object_family(object_bursts),
        "request_object_on_bus1": join_5282_on_bus1(path, id11),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        type=Path,
        default=REPO / "data/generated/camry_2026_bus1_camera_output.json",
    )
    args = parser.parse_args()
    drives = {name: collect_drive(path) for name, path in DRIVES.items()}
    artifact = {
        "schema": "camry-2026-bus1-camera-output-v5",
        "gts_vocabulary": gts_vocabulary(),
        "drives": drives,
        "classification": {
            "bus": (
                "Panda bus 1 is Toyota Bus 1 after the CAN0/CAN1 repin. GTS+ canbus "
                "12984 places Front Camera Module, Front Radar, and other ADAS nodes "
                "on that bus. Exact F33 does not accept 0x180..0x18C."
            ),
            "framing": (
                "0x180..0x18B/64: B0-B1 unique per frame (checksum/CRC), B2 is an 8-bit alive counter; B3 is a "
                "separate synchronized cycle byte, last-4 constant 00000000 (not a MAC). "
                "0x18C is the same header/trailer with DLC 48."
            ),
            "object_family_0x180_0x182": (
                "Eight 7-byte slots after the 4-byte header. Empty slot is exactly "
                "fff8000000ffff (0xFFF8/0xFFFF invalid-style sentinels). Occupied slot "
                "bytes 0-1 unsigned big-endian * 0.005 m is the independently "
                "vision-anchored longitudinal range; FRC DID/FFD distance encodings "
                "are diagnostic vocabulary, not a wire-scale proof."
            ),
            "not_08A": (
                "The 28-byte 0x08A application blob is absent. This family is perception "
                "output, not the truncated TSS request 5282."
            ),
            "middle_hop": (
                "FRC builds FFD 5282/5631 in camera RAM (ID + milliradian pinion + "
                "assist + damping) from vision objects plus plant observers (including "
                "SAS 0x025 and EPS torque 0x030; 0x160 remains unassigned after CORR-138). "
                "The consecutive 5282 "
                "layout ID||pinion||assist is absent from sniffed Bus-1 CAN. A Bus-4 "
                "origin truncates damping, packs ID/pinion/assist as 0x08A B21/B18/B24, "
                "and SecOC-wraps it. Measured angle on the camera bus is inbound plant "
                "echo, not a command to EPS. Requested pinion is not an F33 COM input."
            ),
            "not_tss2_8byte_radar_dbc": (
                "Old comma 8-byte 0x180..0x19F radar-track geometry does not transfer."
            ),
            "0x160": (
                "0x160/32 remains a roughly 40 Hz camera/radar-domain stream. CORR-138 "
                "rejects the former standing 0x025 steering-angle-echo identity: the high "
                "0x160[22] correlation was Class-L-window-restricted, while full-drive "
                "correlation collapses to r=+0.086104/-0.091204. No per-ID FRC-versus-radar "
                "transmitter or standing field identity is assigned."
            ),
            "joined_object_records": (
                "The repeated B2/B3 cycle bytes join 0x180..0x18B as three banks of "
                "eight objects with four 7-byte records per object: bank0 180/183/186/189, "
                "bank1 181/184/187/18A, bank2 182/185/188/18B. Empty geometry in the first "
                "record coincides with zero companion records. In record0, B0:B1 is u16be "
                "range *0.005 m and B2:B3[7:4] is signed12 lateral *0.04 m, left-positive. "
                "In record1, B1[5:0]||B2 is a signed14 velocity word *0.025 m/s. "
                "Independent vision, ego-speed, and gyro anchors supersede the former "
                "direct FFD 57BA/573C scale transfer. Range-rate agreement by itself "
                "cannot identify a common scale. 0x18C/48 remains the VAR-068 status PDU."
            ),
            "remainder": (
                "The three core RadarPoint quantities (range, lateral position, relative "
                "speed) are recovered. Remaining companion bits include object identity/type/"
                "reliability/classification metadata; GTS provides matching u5/u3 vocabulary "
                "but exact CAN packing is not yet assigned. Which Bus-1 node transmits the "
                "family (FRC vs Front Radar vs fusion) is likewise not named by GTS+ CAN-ID."
            ),
        },
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(artifact, indent=1) + "\n")
    print(f"wrote {args.out} ({args.out.stat().st_size} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
