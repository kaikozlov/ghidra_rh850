#!/usr/bin/env python3
"""Decode retained Toyota Bus-1 camera/radar output with GTS+ vocabulary.

GTS+ is DID/FFD keyed, not a CAN DBC. This joins the sniffed panda-bus-1
0x180 family to recovered FRC Data List / Operation-FFD scales, and tests
whether FRC's TSS request object (5282 ID||pinion||assist) is on that native
bus. It does not invent a 64-byte OEM field map where the corpus has none.
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import statistics
import subprocess
from collections import Counter, defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
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
DIST_LSB_M = 0.01  # FFD 5A22 / FRC 0x190A
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
            "emit BO_ 0x180. Wire packing is recovered from sniffed Bus-1 frames "
            "joined to those scales."
        ),
        "frc_p5_geometry_dids": frc,
        "operation_ffd_object_layouts": ffd,
        "joined_distance_scale": {
            "lsb_m": DIST_LSB_M,
            "sources": [
                "FRC_P5 DID 0x190A Forward Vehicle Distance (mul=100, 2 decimal places, m)",
                "FFD 5A22 vertical distance (unsigned, LSB 0.01 m)",
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
    with gzip.open(path, "rt") as f:
        for line in f:
            _seg, t, src, addr, hx = json.loads(line)
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
        "object_slots_0x180_0x182": {
            "header_bytes": HEADER_LEN,
            "slot_bytes": SLOT_LEN,
            "slots_per_pdu": SLOT_N,
            "trailer_bytes": TRAILER_LEN,
            "empty_sentinel": EMPTY7.hex(),
            "empty_slots": empty_slots,
            "occupied_slots": occupied_slots,
            "longitudinal_m_u16be_lsb_0_01": summarize(occupied_dist),
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
        "schema": "camry-2026-bus1-camera-output-v2",
        "gts_vocabulary": gts_vocabulary(),
        "drives": drives,
        "classification": {
            "bus": (
                "Panda bus 1 is Toyota Bus 1 after the CAN0/CAN1 repin. GTS+ canbus "
                "12984 places Front Camera Module, Front Radar, and other ADAS nodes "
                "on that bus. Exact F33 does not accept 0x180..0x18C."
            ),
            "framing": (
                "0x180..0x18B/64: B0-B1 unique per frame (checksum/CRC), B2-B3 shared "
                "rolling counter across the burst, last-4 constant 00000000 (not a MAC). "
                "0x18C is the same header/trailer with DLC 48."
            ),
            "object_family_0x180_0x182": (
                "Eight 7-byte slots after the 4-byte header. Empty slot is exactly "
                "fff8000000ffff (0xFFF8/0xFFFF invalid-style sentinels). Occupied slot "
                "bytes 0-1 unsigned big-endian * 0.01 m is longitudinal/vertical range "
                "at the FRC 0x190A / FFD 5A22 scale (median tens of metres, tail to "
                "a few hundred metres on occupied slots)."
            ),
            "not_08A": (
                "The 28-byte 0x08A application blob is absent. This family is perception "
                "output, not the truncated TSS request 5282."
            ),
            "middle_hop": (
                "FRC builds FFD 5282/5631 in camera RAM (ID + milliradian pinion + "
                "assist + damping) from vision objects plus plant observers (SAS "
                "0x025 / 0x160 echo inbound, EPS torque 0x030). The consecutive 5282 "
                "layout ID||pinion||assist is absent from sniffed Bus-1 CAN. A Bus-4 "
                "origin truncates damping, packs ID/pinion/assist as 0x08A B21/B18/B24, "
                "and SecOC-wraps it. Measured angle on the camera bus is inbound plant "
                "echo, not a command to EPS. Requested pinion is not an F33 COM input."
            ),
            "not_tss2_8byte_radar_dbc": (
                "Old comma 8-byte 0x180..0x19F radar-track geometry does not transfer."
            ),
            "0x160": (
                "0x160/32 is delayed 0x025 steering-angle echo at byte 22 (VAR-074): "
                "plant measured pinion onto the ADAS bus so FRC can see the wheel. "
                "Direction is SAS -> FRC, not FRC -> EPS."
            ),
            "0x183_0x18C": (
                "Different schemas: 0x183/0x184 carry typed records with float-shaped "
                "words (FFD Type-f / 32-bit FRC geometry vocabulary) but are not a 1:1 "
                "copy of FFD 590C. 0x185/0x188/0x18B are often idle zeros. 0x186/0x189/"
                "0x18A are structured and still unpacking. 0x18C/48 is the VAR-068 "
                "staircase/status PDU."
            ),
            "remainder": (
                "Object-slot bytes 2-6 are not FFD 5A24/5A26 16-bit overlays. Which "
                "Bus-1 node transmits which ID (FRC vs Front Radar vs fusion) is not "
                "named by GTS+ CAN-ID. No output authorized."
            ),
        },
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(artifact, indent=1) + "\n")
    print(f"wrote {args.out} ({args.out.stat().st_size} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
