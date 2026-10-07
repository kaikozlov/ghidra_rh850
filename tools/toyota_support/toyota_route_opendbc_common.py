#!/usr/bin/env python3
"""Shared raw-CAN helpers for Toyota route -> opendbc evidence extractors."""
from __future__ import annotations

import collections
import hashlib
from bisect import bisect_left, bisect_right
from pathlib import Path
from typing import Any


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def be_raw(dat: bytes, start_bit: int, size: int, signed: bool = False) -> int:
    """Decode one Motorola DBC signal using opendbc's bit-numbering convention."""
    be_bits = [j + i * 8 for i in range(len(dat)) for j in range(7, -1, -1)]
    idx = be_bits.index(start_bit)
    bits = be_bits[idx:idx + size]
    if len(bits) != size:
        raise ValueError(f"signal {start_bit}|{size} exceeds payload")
    value = 0
    for bit in bits:
        byte_i, bit_i = divmod(bit, 8)
        value = (value << 1) | ((dat[byte_i] >> bit_i) & 1)
    if signed and value & (1 << (size - 1)):
        value -= 1 << size
    return value


def be_signal(dat: bytes, start_bit: int, size: int, *, is_signed: bool = False) -> int:
    """Compatibility spelling used by capture analyzers."""
    return be_raw(dat, start_bit, size, signed=is_signed)


def decode_wheel_speed_kph(dat: bytes) -> float:
    """Existing Camry/Corolla H/F 0x0AA four-wheel speed geometry."""
    vals = [be_raw(dat, s, 15) * 0.01 - 67.67 for s in (6, 22, 38, 54)]
    return sum(vals) / 4


def toyota_checksum(addr: int, dat: bytes) -> int:
    return (addr + (addr >> 8) + len(dat) + sum(dat[:-1])) & 0xFF


def rate_hz(rows: list[tuple[int, bytes]]) -> float | None:
    if len(rows) < 2:
        return None
    span_s = (rows[-1][0] - rows[0][0]) * 1e-9
    return (len(rows) - 1) / span_s if span_s > 0 else None


def stats(values: list[float]) -> dict[str, Any]:
    return {
        "count": len(values),
        "unique_count": len(set(values)),
        "min": min(values),
        "max": max(values),
    }


def _corr(xs: list[float], ys: list[float]) -> float | None:
    if len(xs) < 2 or len(xs) != len(ys):
        return None
    mx = sum(xs) / len(xs)
    my = sum(ys) / len(ys)
    sx = sum((x - mx) ** 2 for x in xs)
    sy = sum((y - my) ** 2 for y in ys)
    if sx == 0 or sy == 0:
        return None
    return sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / (sx * sy) ** 0.5


def lateral_reference_family(
    request_rows: list[tuple[int, bytes]],
    return_rows: list[tuple[int, bytes]],
    angle_rows: list[tuple[int, bytes]],
) -> dict[str, Any]:
    """Reduce the TSS3 0x08A/0x081 lateral request/reference family.

    The field geometry is the currently recovered generation-20 Toyota layout:
    0x08A B21[5:0] Target Lateral ID, B18:B19 reference word, B24 request
    level; 0x081 B13[5:0] returned Target Lateral ID and B16:B17 reference
    word.  Pairing uses loggerd publication timestamps only and therefore does
    not claim physical wire ordering/latency.
    """
    req_ids = collections.Counter((dat[21] & 0x3F) for _, dat in request_rows)
    ret_ids = collections.Counter((dat[13] & 0x3F) for _, dat in return_rows)
    req_levels = collections.Counter(dat[24] for _, dat in request_rows)
    req_b23 = collections.Counter(dat[23] for _, dat in request_rows)
    req_words = [int.from_bytes(dat[18:20], "big", signed=True) for _, dat in request_rows]
    ret_words = [int.from_bytes(dat[16:18], "big", signed=True) for _, dat in return_rows]

    # Join request/reference word to the nearest 0x025 measured steering-angle
    # publication.  The exact H/F/Camry controller-equivalent factor is kept as
    # an explicit comparison, not promoted to an OEM unit name for 0x08A.
    angle_times = [t for t, _ in angle_rows]
    fit_x: list[float] = []
    fit_y: list[float] = []
    for t, dat in request_rows:
        if not angle_times:
            break
        i = bisect_left(angle_times, t)
        candidates = [j for j in (i - 1, i) if 0 <= j < len(angle_rows)]
        if not candidates:
            continue
        j = min(candidates, key=lambda j: abs(angle_rows[j][0] - t))
        if abs(angle_rows[j][0] - t) > 50_000_000:
            continue
        measured = angle_rows[j][1]
        fit_x.append(float(int.from_bytes(dat[18:20], "big", signed=True)))
        fit_y.append(be_raw(measured, 3, 12, True) * 1.5 + be_raw(measured, 39, 4, True) * 0.1)

    slope = intercept = None
    if len(fit_x) >= 2:
        mx = sum(fit_x) / len(fit_x)
        my = sum(fit_y) / len(fit_y)
        den = sum((x - mx) ** 2 for x in fit_x)
        if den:
            slope = sum((x - mx) * (y - my) for x, y in zip(fit_x, fit_y)) / den
            intercept = my - slope * mx

    # Pair each 0x081 with the latest 0x08A no older than 100 ms.  This is a
    # state/reference consistency join only; rlog batching is not a latency oracle.
    req_times = [t for t, _ in request_rows]
    paired = id_match = word_equal = 0
    abs_word_delta: list[int] = []
    for t, dat in return_rows:
        i = bisect_right(req_times, t) - 1
        if i < 0 or t - req_times[i] > 100_000_000:
            continue
        req = request_rows[i][1]
        paired += 1
        id_match += int((dat[13] & 0x3F) == (req[21] & 0x3F))
        rw = int.from_bytes(dat[16:18], "big", signed=True)
        qw = int.from_bytes(req[18:20], "big", signed=True)
        word_equal += int(rw == qw)
        abs_word_delta.append(abs(rw - qw))

    exact_scale = 1024 / 17870
    return {
        "request_0x08A": {
            "frame_count": len(request_rows),
            "target_lateral_id_counts": {str(k): v for k, v in sorted(req_ids.items())},
            "request_level_counts": {str(k): v for k, v in sorted(req_levels.items())},
            "b23_counts": {f"0x{k:02X}": v for k, v in sorted(req_b23.items())},
            "reference_word_raw": stats([float(x) for x in req_words]) if req_words else None,
        },
        "return_0x081": {
            "frame_count": len(return_rows),
            "target_lateral_id_counts": {str(k): v for k, v in sorted(ret_ids.items())},
            "reference_word_raw": stats([float(x) for x in ret_words]) if ret_words else None,
        },
        "request_angle_join": {
            "pair_count": len(fit_x),
            "pearson_r": _corr(fit_x, fit_y),
            "fitted_deg_per_count": slope,
            "fitted_intercept_deg": intercept,
            "exact_h_f_camry_controller_equivalent_deg_per_count": exact_scale,
            "scale_error_percent": ((slope / exact_scale) - 1) * 100 if slope is not None else None,
            "boundary": "Nearest rlog-publication join only; high correlation/scale agreement supports common reference geometry but does not establish producer identity or physical command latency.",
        },
        "return_latest_request_join": {
            "pair_count": paired,
            "target_lateral_id_match_count": id_match,
            "reference_word_exact_match_count": word_equal,
            "median_abs_reference_word_delta": sorted(abs_word_delta)[len(abs_word_delta) // 2] if abs_word_delta else None,
            "boundary": "Latest <=100-ms rlog-publication state join; loggerd batch timestamps are not wire-order timestamps.",
        },
    }


# Gear/READY evidence IDs that every route reducer must census across all
# recorded channels: hybrid gear packet, Corolla gear corroboration,
# generation-native gear packet, Ready Status input.
GEAR_READY_CENSUS_IDS = (0x127, 0x2A1, 0x3BF, 0x51E)

# Raw selected-field geometry per census ID as (start_bit, size) in the same
# Motorola numbering as be_raw().  Values stay raw counts; the census asserts
# no gear/READY label semantics.
_GEAR_READY_CENSUS_FIELDS: dict[int, tuple[int, int]] = {
    0x127: (47, 4),
    0x2A1: (39, 8),
    0x3BF: (7, 8),
    0x51E: (7, 1),
}


def _motorola_min_dlc(start_bit: int, size: int) -> int:
    wrap = max(0, size - 1 - (start_bit % 8))
    return start_bit // 8 + (1 if wrap else 0) + 1


class GearReadyCensus:
    """All-source record census for the gear/READY evidence IDs.

    Counts every recorded record per raw source/DLC across four distinct
    channels -- received can (src<128), panda returned Tx echoes (128<=src<192),
    panda rejected echoes (src>=192), and sendcan service records -- plus
    per-source totals over ALL addresses, so a zero count for one ID still has
    a coverage denominator.  Sources are never normalized to a physical bus
    topology and no DLC is filtered.
    """

    RECEIVED = "received_can"
    RETURNED = "returned_can_echo"
    REJECTED = "rejected_can_echo"
    SENDCAN = "sendcan"
    _CHANNELS = (RECEIVED, RETURNED, REJECTED, SENDCAN)

    def __init__(self) -> None:
        self._source_totals: dict[str, dict[int, int]] = {c: collections.Counter() for c in self._CHANNELS}
        self._id_counts: dict[str, dict[int, dict[tuple[int, int], int]]] = {
            c: {a: collections.Counter() for a in GEAR_READY_CENSUS_IDS} for c in self._CHANNELS
        }
        self._id_field_values: dict[str, dict[int, dict[int, int]]] = {
            c: {a: collections.Counter() for a in GEAR_READY_CENSUS_IDS} for c in self._CHANNELS
        }

    def add_can(self, src: int, address: int, dat: bytes) -> None:
        """Feed one `can` service record; src>=128 are panda echoes, not vehicle traffic."""
        channel = self.RECEIVED if src < 128 else (self.RETURNED if src < 192 else self.REJECTED)
        self._add(channel, src, address, dat)

    def add_sendcan(self, src: int, address: int, dat: bytes) -> None:
        """Feed one `sendcan` service record (queued/attempted openpilot Tx)."""
        self._add(self.SENDCAN, src, address, dat)

    def _add(self, channel: str, src: int, address: int, dat: bytes) -> None:
        self._source_totals[channel][src] += 1
        counts = self._id_counts[channel].get(address)
        if counts is None:
            return
        counts[(src, len(dat))] += 1
        start_bit, size = _GEAR_READY_CENSUS_FIELDS[address]
        if len(dat) >= _motorola_min_dlc(start_bit, size):
            self._id_field_values[channel][address][be_raw(dat, start_bit, size)] += 1

    def result(self, input_sha256: str, input_size: int) -> dict[str, Any]:
        channels: dict[str, Any] = {}
        for channel in self._CHANNELS:
            ids: dict[str, Any] = {}
            for address in GEAR_READY_CENSUS_IDS:
                start_bit, size = _GEAR_READY_CENSUS_FIELDS[address]
                ids[f"0x{address:03X}"] = {
                    "frame_count": sum(self._id_counts[channel][address].values()),
                    "source_dlc_counts": {
                        f"src={src} dlc={dlc}": n
                        for (src, dlc), n in sorted(self._id_counts[channel][address].items())
                    },
                    "selected_field": {
                        "decoder": "be_raw",
                        "start_bit": start_bit,
                        "size": size,
                        "min_dlc": _motorola_min_dlc(start_bit, size),
                    },
                    "selected_field_value_counts": {
                        str(value): n for value, n in sorted(self._id_field_values[channel][address].items())
                    },
                }
            channels[channel] = {
                "record_count": sum(self._source_totals[channel].values()),
                "source_totals": {str(src): n for src, n in sorted(self._source_totals[channel].items())},
                "ids": ids,
            }
        return {
            "census_schema": "toyota-gear-ready-all-source-census-v1",
            "input_sha256": input_sha256,
            "input_size": input_size,
            "ids": [f"0x{a:03X}" for a in GEAR_READY_CENSUS_IDS],
            "channel_definitions": {
                self.RECEIVED: "can service records with src<128 (incoming vehicle traffic)",
                self.RETURNED: "can service records with 128<=src<192 (panda returned Tx echo; src-128 = logical bus)",
                self.REJECTED: "can service records with src>=192 (panda rejected Tx echo; src-192 = logical bus)",
                self.SENDCAN: "sendcan service records (openpilot queued/attempted Tx; raw src)",
            },
            "channels": channels,
            "boundary": "Raw per-source/per-DLC counts over every recorded channel, source and DLC; sources are never normalized to a physical bus topology and no DLC is filtered. A zero count proves only that this pinned input contains no such record, not that the vehicle never sends the ID. Selected-field value counts are raw decodes gated on sufficient DLC and assert no gear/READY label semantics.",
        }
