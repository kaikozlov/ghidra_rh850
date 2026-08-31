#!/usr/bin/env python3
"""Recover the observable E2E integrity/freshness shape of Camry Toyota Bus 1.

This is deliberately wire-only. It tests whether the first two bytes of the
native Bus-1 periodic family behave as a cryptographic authenticator or as an
affine-linear integrity code, and characterizes the visible rolling counter.
It does not claim receiver acceptance-window semantics from sender traces.
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import statistics
from collections import Counter, defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
RAW = REPO / "targets/camry-2026/raw-20260827"
DRIVES = {
    "drive_a": RAW / "camry_relay_route_can_20260827.ndjson.gz",
    "drive_b": RAW / "camry_relay_lta_confirm_route_can_20260827.ndjson.gz",
}
MIN_STREAM = 50


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load_drive(path: Path) -> dict[tuple[int, int], list[tuple[int, int, bytes]]]:
    out: dict[tuple[int, int], list[tuple[int, int, bytes]]] = defaultdict(list)
    with gzip.open(path, "rt") as f:
        for line in f:
            seg, t, src, addr, hx = json.loads(line)
            if src != 1:
                continue
            d = bytes.fromhex(hx)
            out[(addr, len(d))].append((seg, t, d))
    return out


def xy(d: bytes) -> tuple[int, int]:
    return int.from_bytes(d[2:], "big"), int.from_bytes(d[:2], "big")


def build_basis(frames: list[bytes]) -> tuple[bytes, dict[int, tuple[int, int]], int]:
    base = frames[0]
    x0, y0 = xy(base)
    basis: dict[int, tuple[int, int]] = {}
    conflicts = 0
    for d in frames[1:]:
        x, y = xy(d)
        x ^= x0
        y ^= y0
        while x:
            p = x.bit_length() - 1
            if p in basis:
                bx, by = basis[p]
                x ^= bx
                y ^= by
            else:
                basis[p] = (x, y)
                break
        if x == 0 and y != 0:
            conflicts += 1
    return base, basis, conflicts


def reduce_vector(basis: dict[int, tuple[int, int]], x: int) -> tuple[bool, int]:
    y = 0
    while x:
        p = x.bit_length() - 1
        if p not in basis:
            return False, y
        bx, by = basis[p]
        x ^= bx
        y ^= by
    return True, y


def bit_contribution(base: bytes, basis: dict[int, tuple[int, int]], byte_idx: int, bit: int) -> int | None:
    z = bytearray(len(base) - 2)
    z[byte_idx - 2] = 1 << bit
    ok, y = reduce_vector(basis, int.from_bytes(z, "big"))
    return y if ok else None


def suffix_determinism(frames: list[bytes]) -> dict:
    by_suffix: dict[bytes, set[bytes]] = defaultdict(set)
    for d in frames:
        by_suffix[d[2:]].add(d[:2])
    return {
        "frames": len(frames),
        "unique_suffixes": len(by_suffix),
        "suffixes_with_multiple_headers": sum(len(v) > 1 for v in by_suffix.values()),
        "max_headers_per_suffix": max(map(len, by_suffix.values())),
    }


def heldout_affine(frames: list[bytes], stride: int = 5) -> dict:
    base = frames[0]
    x0, y0 = xy(base)
    train = frames[::stride]
    holdout = [d for i, d in enumerate(frames) if i % stride]
    _base, basis, train_conflicts = build_basis(train)
    # build_basis used train[0], which is frames[0].
    covered = correct = 0
    for d in holdout:
        x, y = xy(d)
        ok, pred_delta = reduce_vector(basis, x ^ x0)
        if not ok:
            continue
        covered += 1
        correct += ((pred_delta ^ y0) == y)
    return {
        "stride": stride,
        "train_frames": len(train),
        "train_rank": len(basis),
        "train_conflicts": train_conflicts,
        "holdout_frames": len(holdout),
        "covered": covered,
        "correct": correct,
    }


def counter_stats(rows: list[tuple[int, int, bytes]]) -> dict:
    total = plus1 = 0
    gaps_ms: list[float] = []
    non_plus1: list[dict] = []
    for (s0, t0, a), (s1, t1, b) in zip(rows, rows[1:]):
        if s0 != s1:
            continue
        total += 1
        delta = (b[2] - a[2]) & 0xFF
        dt_ms = (t1 - t0) / 1e6
        gaps_ms.append(dt_ms)
        plus1 += delta == 1
        if delta != 1 and len(non_plus1) < 16:
            non_plus1.append({"gap_ms": round(dt_ms, 6), "from": a[2], "to": b[2], "delta": delta})
    return {
        "pairs": total,
        "plus1": plus1,
        "plus1_fraction": round(plus1 / total, 9) if total else None,
        "gap_ms_median": round(statistics.median(gaps_ms), 6) if gaps_ms else None,
        "non_plus1_examples": non_plus1,
    }


def affine_020(rows: list[tuple[int, int, bytes]]) -> dict:
    mapping: dict[int, int] = {}
    for _seg, _t, d in rows:
        if len(d) != 12 or d[2] != d[3] or any(d[4:]):
            continue
        mapping[d[2]] = int.from_bytes(d[:2], "big")
    violations = 0
    if len(mapping) == 256:
        f0 = mapping[0]
        for a in range(256):
            for b in range(256):
                violations += mapping[a ^ b] != (mapping[a] ^ mapping[b] ^ f0)

    by_seg_frame: dict[tuple[int, bytes], int] = {}
    recurrence_s: list[float] = []
    for seg, t, d in rows:
        key = (seg, d)
        if key in by_seg_frame:
            recurrence_s.append((t - by_seg_frame[key]) / 1e9)
        by_seg_frame[key] = t
    return {
        "counter_values": len(mapping),
        "affine_pair_tests": 256 * 256 if len(mapping) == 256 else 0,
        "affine_pair_violations": violations,
        "unique_full_frames": len({d for _s, _t, d in rows}),
        "exact_frame_recurrence_s_median": round(statistics.median(recurrence_s), 9) if recurrence_s else None,
        "exact_frame_recurrence_count": len(recurrence_s),
    }


def cross_id_same_suffix(streams: dict[tuple[int, int], list[tuple[int, int, bytes]]], a: int, b: int, dlc: int) -> dict:
    ma = {d[2:]: int.from_bytes(d[:2], "big") for _s, _t, d in streams[(a, dlc)]}
    mb = {d[2:]: int.from_bytes(d[:2], "big") for _s, _t, d in streams[(b, dlc)]}
    overlap = sorted(set(ma) & set(mb))
    xs = Counter(ma[k] ^ mb[k] for k in overlap)
    return {
        "ids": [f"0x{a:03X}", f"0x{b:03X}"],
        "dlc": dlc,
        "overlapping_suffixes": len(overlap),
        "header_xor_histogram": {f"0x{k:04X}": v for k, v in sorted(xs.items())},
    }


def stream_summary(rows: list[tuple[int, int, bytes]]) -> dict:
    frames = [d for _s, _t, d in rows]
    base, basis, conflicts = build_basis(frames)
    return {
        "n": len(frames),
        "affine_rank": len(basis),
        "affine_conflicts": conflicts,
        "suffix_determinism": suffix_determinism(frames),
        "last4_histogram": {k.hex(): v for k, v in Counter(d[-4:] for d in frames).items()},
        "B2_unique": len({d[2] for d in frames}),
        "B3_histogram": {str(k): v for k, v in sorted(Counter(d[3] for d in frames).items())},
        "base": base.hex(),
    }


def fmt_contrib(vals: list[int | None]) -> list[str | None]:
    return [None if x is None else f"0x{x:04X}" for x in vals]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=REPO / "data/generated/camry_2026_bus1_e2e.json")
    args = ap.parse_args()

    drives = {name: load_drive(path) for name, path in DRIVES.items()}
    drive_out = {}
    for name, streams in drives.items():
        periodic = {}
        for (addr, dlc), rows in sorted(streams.items()):
            if len(rows) < MIN_STREAM:
                continue
            periodic[f"0x{addr:03X}/{dlc}"] = stream_summary(rows)
        x160 = streams[(0x160, 32)]
        drive_out[name] = {
            "source": str(DRIVES[name].relative_to(REPO)),
            "source_sha256": sha256(DRIVES[name]),
            "periodic_streams": periodic,
            "0x160_counter": counter_stats(x160),
            "0x020_control": affine_020(streams[(0x020, 12)]),
        }

    combined_160_rows = drives["drive_a"][(0x160, 32)] + drives["drive_b"][(0x160, 32)]
    combined_160 = [d for _s, _t, d in combined_160_rows]
    base160, basis160, conflicts160 = build_basis(combined_160)
    b2 = fmt_contrib([bit_contribution(base160, basis160, 2, b) for b in range(8)])
    b12 = fmt_contrib([bit_contribution(base160, basis160, 12, b) for b in range(8)])

    # Same-DLC common-code witnesses from the richer drive-B capture.
    s_b = drives["drive_b"]
    same_dlc_b2 = {}
    for addr in (0x160, 0x440, 0x450):
        frames = [d for _s, _t, d in s_b[(addr, 32)]]
        base, basis, _ = build_basis(frames)
        same_dlc_b2[f"0x{addr:03X}"] = fmt_contrib([bit_contribution(base, basis, 2, b) for b in range(8)])

    artifact = {
        "schema": "camry-2026-bus1-e2e-v1",
        "drives": drive_out,
        "combined_0x160": {
            "frames": len(combined_160),
            "affine_rank": len(basis160),
            "affine_conflicts": conflicts160,
            "heldout_prediction": heldout_affine(combined_160, 5),
            "B2_checksum_xor_contribution_by_bit0_to_7": b2,
            "B12_checksum_xor_contribution_by_bit0_to_7": b12,
            "B12_used_bits": [0, 1, 2, 3, 4, 5, 6],
            "patch_rule": (
                "For an observed 0x160 frame, changing only B12 old->new can preserve the observed linear integrity word as "
                "new_B0B1 = old_B0B1 XOR XOR(contribution[bit] for bit set in old XOR new). "
                "The retained corpus spans and solves every used B12 bit 0..6; B7 is never used."
            ),
        },
        "common_code_witnesses": {
            "dlc32_B2_contributions": same_dlc_b2,
            "same_suffix_id_bit0": [
                cross_id_same_suffix(s_b, 0x184, 0x185, 64),
                cross_id_same_suffix(s_b, 0x18A, 0x18B, 64),
            ],
        },
        "interpretation": {
            "integrity": (
                "B0:B1 is an affine-linear 16-bit integrity code over the visible PDU state, with a common length-dependent "
                "transform and an ID/Data-ID contribution. This is incompatible with treating B0:B1 as a cryptographic MAC "
                "on the observed interface. The exact OEM polynomial/implementation name remains unrecovered."
            ),
            "freshness": (
                "0x160 B2 is an 8-bit alive/rolling counter. It advances +1 on every retained drive-B same-segment pair; "
                "drive-A non-+1 observations coincide with capture gaps/missed cycles. Sender traces do not prove the receiver's "
                "accepted counter window or timeout policy."
            ),
            "replay_boundary": (
                "There is no observed long-lived epoch/nonce on this Bus-1 framing. Constant 0x020 has only 256 complete wire "
                "images and repeats byte-for-byte after the 8-bit counter wraps (about 12.8 s at its ~20 Hz cadence). Immediate "
                "replay can still be rejected by receiver-side counter state; post-wrap anti-replay beyond that state is not on wire."
            ),
            "security_boundary": (
                "The retained native Bus-1 family therefore exposes E2E integrity/freshness rather than ordinary P5 SecOC. "
                "This does not identify which node transmits 0x160 or prove receiver acceptance of synthetically modified frames."
            ),
        },
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(artifact, indent=2, sort_keys=True) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
