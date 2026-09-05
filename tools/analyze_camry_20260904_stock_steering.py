#!/usr/bin/env python3
"""Reproducible passive reducer for the 2026-09-04 Camry stock-steering corpus.

Work package 1 of the Camry openpilot completion plan (REFERENCE/
CAMRY_OPENPILOT_COMPLETION_PLAN.md). This tool re-derives, from the original
loggerd rlogs, the published September observations recorded as VAR-124
(transport census subset) and VAR-129 (native request census, 0x081/0x08A
reference relationship, native ID4 episodes, and the route-3c segment-43
divergent-request witness) without relying on any retained ``build/``
artifact.

Design boundaries:

- Streaming: events are consumed one at a time per segment; no route-level
  frame retention. Per-segment state is bounded (counters, last-observed
  signal trackers, a 20-Hz sample grid, and retained rows only for configured
  witness windows).
- Provenance: every source file is hashed (compressed bytes; an unreadable
  file aborts the run) and inventoried with event counts, first/last
  live-event timestamps, and input-quality flags
  (missing/duplicate/out-of-order).
- Separation: native vehicle frames (Panda ``src`` 0..2), Panda TX-loopback
  echoes (``src`` 128..191), rejected TX (``src`` 192..255), and openpilot
  ``sendcan`` are counted independently. Forwarding echoes are never counted
  as native producers.
- Time base: segment-relative seconds are measured from the first *live*
  event (can/sendcan/carState/controlsState/pandaState) in the segment.
  Repeated startup metadata never resets the origin. Joins never cross
  routes, and each segment's grid is independent (segment boundaries are
  temporal discontinuities).
- Decode geometry is implemented locally from the pinned evidence
  (byte-aligned Motorola bit numbering; see DECODE_PROVENANCE) and does not
  depend on any DBC parser. Missing, stale (age > MAX_AGE_NS), invalid, and
  numeric zero stay distinguishable: every sample row carries per-signal
  ages and raw words.

Inputs are external to this repository (maintainer driving logs); full-corpus
regeneration requires them. Portable tests use small JSONL excerpts produced
by ``--emit-fixtures``; expected values there are pinned from independent
hand/publication derivations, never from this decoder.

Usage (analysis repo root, openpilot environment providing LogReader)::

  tools/analyze_camry_20260904_stock_steering.py \
    --input-root /Users/kai/dev/inspect/logs/camry-2026/2026-09-04 \
    --openpilot-root /path/to/kai-openpilot
"""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
import subprocess
import sys
from collections import Counter
from collections.abc import Iterable, Iterator
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

DEFAULT_INPUT_ROOT = "/Users/kai/dev/inspect/logs/camry-2026/2026-09-04"
DEFAULT_OPENPILOT_ROOT = "/Users/kai/dev/inspect/repos/kai-openpilot"
DEFAULT_ROUTES = (
    "0000003b--62262eb7a1",
    "0000003c--97b9e7a69a",
    "0000003d--0e812cecba",
)
ROUTE_SHORT = {r: r[6:8] for r in DEFAULT_ROUTES}

OUT_MANIFEST = "data/generated/camry_20260904_stock_steering_manifest.json"
OUT_REPORT = "data/generated/camry_20260904_stock_steering_report.json"

# --- Wire geometry (pinned evidence; do not adjust to make checks pass) ----

ADDR_STEER_ANGLE = 0x025   # measured steering angle/fraction/rate (bus 0)
ADDR_EPS_TELEM = 0x030     # driver torque + status + motor-feedback proxy (bus 0)
ADDR_REFERENCE = 0x081     # steering-reference word B16:B17 (bus 0)
ADDR_LATERAL_REQ = 0x08A   # stock lateral request (bus 2, camera side)
ADDR_LATERAL_CTRL = 0x0B6  # openpilot B6 candidate (sendcan; never native here)
ANALYSIS_ADDRESSES = (ADDR_STEER_ANGLE, ADDR_EPS_TELEM, ADDR_REFERENCE,
                      ADDR_LATERAL_REQ, ADDR_LATERAL_CTRL)
ADDRS_ABSENT_NATIVE = (0x0B6, 0x131, 0x2E4)
# Shortest frame the fixed-offset decoders index into, per analysis address
# (0x025 needs d4; 0x030 needs d17/B22:B23; 0x081 needs B16:B17; 0x08A needs
# B24; the 32-byte B6 shape reads d28..d31). Shorter frames are counted, not
# decoded, so one malformed frame cannot abort a whole-route run.
DECODE_MIN_LEN = {
    ADDR_STEER_ANGLE: 5, ADDR_EPS_TELEM: 24, ADDR_REFERENCE: 18,
    ADDR_LATERAL_REQ: 25, ADDR_LATERAL_CTRL: 32,
}

# 0x025: STEER_ANGLE = signed12 @bit3 * 1.5 deg; STEER_FRACTION = signed4
# @bit39 * 0.1 deg (live-baseline §4.2; exact F33 §1.4 uses the same
# nibble:byte coarse layout on 0x4A3).
ANGLE_COARSE_SCALE = 1.5
ANGLE_FRACTION_SCALE = 0.1
# 0x030: torque = signed8(B8)*0.1 + signed4(B17 low nibble)*0.01 N.m; B6[0] is
# DRIVER_TORQUE_INVALID (opendbc toyota_tss3_pt TSS3_EPS_TELEMETRY 48|1).
TORQUE_COARSE_SCALE = 0.1
TORQUE_FINE_SCALE = 0.01
DRIVER_TORQUE_INVALID_MASK = 0x01
# 0x030 B22:B23 signed BE16: mapped motor-feedback proxy (NOT amperes or
# commanded torque; port report §1.3).
# 0x08A: B21 request/target-lateral ID (full byte retained; dictionary values
# 0/1/4/10/11/18/19...; upper two bits zero in retained frames), B18:B19
# signed BE16 request angle, B24 request level.
# 0x081: B16:B17 signed BE16 steering-reference word.
# 0x0B6 (sendcan only): B3[5:0] target lateral ID, B4:B5 signed BE16 target
# angle (opendbc toyota_tss3_pt TSS3_LATERAL_CONTROL).
REQUEST_SCALE_DEG_PER_COUNT = 1024.0 / 17870.0  # ~0.05730274202574147

DECODE_PROVENANCE = {
    "0x025": ("live-baseline §4.2 H/F-transferred geometry; exact-F33 §1.4 "
              "corroborates the nibble:byte coarse layout"),
    "0x030": ("exact-F33 §1.3 packer recovery (B8 coarse, B17[3:0] fine, "
              "B6[0] invalid, B22:B23 motor-feedback proxy)"),
    "0x08A/0x081": "VAR-091/CORR-134/CORR-135 word geometry; 1024/17870 deg/count",
    "0x0B6": ("opendbc toyota_tss3_pt_generated TSS3_LATERAL_CONTROL "
              "(B3[5:0] ID, B4:B5 signed BE16)"),
}

# --- VAR-129 sampling method (exact reproduction) --------------------------

SAMPLE_HZ = 20
GRID_STEP_NS = 1_000_000_000 // SAMPLE_HZ
MAX_AGE_NS = 75_000_000          # maximum signal age at a grid point
SPEED_MIN_MPS = 10.0             # strictly above
TORQUE_MAX_NM = 0.5              # absolute raw-decoded driver torque strictly below
NATIVE_ID_ACTIVE = 11            # B21 == 11 (LTA/LCA request state)
DIVERGENCE_DEG = 2.5             # |openpilot - native| >= for the divergent set
ID4_BYTE = 4                     # B21 == 4 episodes
ID4_EPISODE_GAP_NS = 500_000_000  # > 0.5 s gap separates ID4 episodes
OP_LAG_NS_FOR_ID4 = 150_000_000   # sendcan age bound when labeling ID4 rows

WITNESS_ROUTE = "0000003c--97b9e7a69a"
WITNESS_SEGMENT = 43
# selection window; the published 34.46-35.26 window is the rounded span of the
# 17 qualified samples (first 34.458562, last 35.258562 in the original grid)
WITNESS_WINDOW_S = (34.40, 35.30)
WITNESS_PUBLISHED_SPAN_S = (34.458562074, 35.258562074)

LIVE_EVENT_TYPES = frozenset({"can", "sendcan", "carState", "controlsState", "pandaState"})


# --- Decode primitives ------------------------------------------------------


def be_signal(data: bytes, start_bit: int, size: int) -> int:
    """Motorola bit numbering, MSB-first within each byte.

    Matches the pinned repo helper semantics and the exact-F33 packer
    geometry (empirically r=0.9999 against the logged carState decodes).
    """
    be_bits = [j + i * 8 for i in range(len(data)) for j in range(7, -1, -1)]
    idx = be_bits.index(start_bit)
    value = 0
    for b in be_bits[idx:idx + size]:
        value = (value << 1) | ((data[b // 8] >> (b % 8)) & 1)
    if value >= (1 << (size - 1)):
        value -= 1 << size
    return value


def signed_be16(data: bytes, off: int) -> int:
    return int.from_bytes(data[off:off + 2], "big", signed=True)


def torque_nm(dat: bytes) -> float:
    return round(be_signal(dat, 71, 8) * TORQUE_COARSE_SCALE
                 + be_signal(dat, 139, 4) * TORQUE_FINE_SCALE, 3)


def torque_invalid(dat: bytes) -> bool:
    return bool(dat[6] & DRIVER_TORQUE_INVALID_MASK)


def steering_angle_deg(dat: bytes) -> float:
    return round(be_signal(dat, 3, 12) * ANGLE_COARSE_SCALE
                 + be_signal(dat, 39, 4) * ANGLE_FRACTION_SCALE, 3)


def motor_feedback_proxy(dat: bytes) -> int:
    return signed_be16(dat, 22)


# --- Event records -----------------------------------------------------------
#
# Ingestion adapters yield tuples:
#   ("can"|"sendcan", t_ns, src, addr, dat_hex)
#   ("carState", t_ns, vEgo, left_blinker, right_blinker, steering_torque,
#    steering_pressed, steering_angle_deg)
#   ("pandaState", t_ns, safety_tx_blocked)
#   ("controlsState", t_ns)
# Only these cross the ingestion boundary, so fixtures and rlogs share one
# reducer implementation.


@dataclass
class Obs:
    """Last-observed tracker for one signal."""

    t: int = -1
    value: Any = None

    def update(self, t: int, value: Any) -> None:
        if t >= self.t:  # equal-timestamp updates keep the later arrival
            self.t, self.value = t, value


@dataclass
class SampleRow:
    grid_ns: int
    seg_s: float
    measured_deg: float | None
    torque_nm: float | None
    torque_valid: bool | None
    motor_proxy: int | None
    native_id: int | None
    native_req_deg: float | None
    native_req_raw: int | None
    native_level: int | None
    reference_raw: int | None
    reference_deg: float | None
    op_id: int | None
    op_target_deg: float | None
    op_target_raw: int | None
    v_ego: float | None
    blinker: bool | None
    ages_ns: dict[str, int]

@dataclass
class SegmentResult:
    route: str
    segment: int
    source: dict[str, Any]
    event_counts: dict[str, int]
    out_of_order_events: int
    first_live_ns: int | None
    last_live_ns: int | None
    census: dict[str, Any]
    grid_samples: int
    exclusions: dict[str, int]
    native_id_counts_fresh: dict[str, int]
    qualified: list[SampleRow] = field(default_factory=list)
    id4_rows: list[dict[str, Any]] = field(default_factory=list)
    witness_rows: list[SampleRow] = field(default_factory=list)


class SegmentReducer:
    """Streaming reduction of one rlog segment (ingestion-agnostic).

    Events must arrive in nondecreasing time order (callers stable-sort).
    Grid points at ``first_live + k*step`` are sampled just before the first
    event strictly after them arrives, so every sample reflects the last
    observation at or before the grid time.
    """

    def __init__(self, route: str, segment: int, *, keep_qualified: bool = False,
                 witness: bool = False, witness_window_s: tuple[float, float] | None = None,
                 anchor_ns: int | None = None) -> None:
        # anchor_ns overrides the segment-relative origin and grid phase (used
        # by fixture replay so excerpt grids match the full-segment run).
        self.anchor_ns = anchor_ns
        self.route = route
        self.segment = segment
        self.keep_qualified = keep_qualified
        self.witness = witness
        self.witness_window_s = witness_window_s
        self.event_counts: Counter[str] = Counter()
        self.out_of_order = 0
        self.last_t: int | None = None
        self.first_live: int | None = None
        self.last_live: int | None = None
        # census
        self.native_by_bus: Counter[str] = Counter({str(b): 0 for b in range(3)})
        self.native_absent: Counter[str] = Counter({f"0x{a:03X}": 0 for a in ADDRS_ABSENT_NATIVE})
        self.returned_by_bus: Counter[str] = Counter()
        self.rejected_by_bus: Counter[str] = Counter()
        self.returned_by_addr: Counter[str] = Counter()
        self.rejected_by_addr: Counter[str] = Counter()
        self.sendcan_by_addr: Counter[str] = Counter()
        self.b6_shapes: Counter[str] = Counter()
        self.unexpected_src: Counter[str] = Counter()
        self.short_frames = 0
        self.safety_tx_blocked: list[tuple[int, int]] = []
        # signal trackers
        self.obs: dict[str, Obs] = {
            "measured": Obs(), "torque": Obs(), "torque_invalid": Obs(),
            "motor": Obs(), "native": Obs(), "reference": Obs(),
            "op": Obs(), "v_ego": Obs(), "blinker": Obs(),
        }
        # grid state
        self._seg0: int | None = None
        self._next_grid: int | None = None
        self.grid_samples = 0
        self.exclusions: Counter[str] = Counter()
        self.native_id_counts_fresh: Counter[str] = Counter()
        self.qualified: list[SampleRow] = []
        self.id4_rows: list[dict[str, Any]] = []

    # -- ingestion -----------------------------------------------------------

    def feed(self, rec: tuple) -> None:
        kind = rec[0]
        t = int(rec[1])
        self.event_counts[kind] += 1
        if self.last_t is not None and t < self.last_t:
            self.out_of_order += 1
        self.last_t = t
        if kind in LIVE_EVENT_TYPES:
            if self.first_live is None:
                self.first_live = t
                origin = self.anchor_ns if self.anchor_ns is not None else t
                self._seg0 = origin
                # first grid point at or before t; the excerpt skips earlier
                # grid points exactly like a full-segment run would sample them
                self._next_grid = origin + max((t - origin) // GRID_STEP_NS, 0) * GRID_STEP_NS
            self.last_live = t
        # advance the grid past everything strictly before t
        if self._next_grid is not None:
            while self._next_grid < t:
                self._sample(self._next_grid)
                self.grid_samples += 1
                self._next_grid += GRID_STEP_NS
        if kind in ("can", "sendcan"):
            self._frame(kind, t, int(rec[2]), int(rec[3]), bytes.fromhex(rec[4]))
        elif kind == "carState":
            self._car_state(t, float(rec[2]), bool(rec[3]), bool(rec[4]))
        elif kind == "pandaState":
            self._panda_state(t, int(rec[2]))
        # controlsState and non-live metadata (initData etc.) count toward the
        # live origin but carry no reducer fields and never reset it.

    def _frame(self, kind: str, t: int, src: int, addr: int, dat: bytes) -> None:
        min_len = DECODE_MIN_LEN.get(addr)
        if min_len is not None and len(dat) < min_len:
            self.short_frames += 1
            return
        if kind == "sendcan":
            self.sendcan_by_addr[f"0x{addr:03X}"] += 1
            if addr == ADDR_LATERAL_CTRL:
                self._observe(t, "op", (dat[3] & 0x3F, signed_be16(dat, 4)))
                shape = (dat[3] & 0x3F, dat[6], dat[8], dat[9],
                         int.from_bytes(dat[28:32], "big"))
                self.b6_shapes[repr(shape)] += 1
            return
        if 0 <= src <= 2:
            self.native_by_bus[str(src)] += 1
            if addr in ADDRS_ABSENT_NATIVE:
                self.native_absent[f"0x{addr:03X}"] += 1
            if src == 0 and addr == ADDR_STEER_ANGLE:
                self._observe(t, "measured", steering_angle_deg(dat))
            elif src == 0 and addr == ADDR_EPS_TELEM:
                self._observe(t, "torque", torque_nm(dat))
                self._observe(t, "torque_invalid", torque_invalid(dat))
                self._observe(t, "motor", motor_feedback_proxy(dat))
            elif src == 0 and addr == ADDR_REFERENCE:
                self._observe(t, "reference", signed_be16(dat, 16))
            elif src == 2 and addr == ADDR_LATERAL_REQ:
                b21 = dat[21]
                self._observe(t, "native", (b21, signed_be16(dat, 18), dat[24]))
                if b21 == ID4_BYTE:
                    self._id4(t, dat)
        elif 128 <= src <= 191:
            self.returned_by_bus[str(src - 128)] += 1
            self.returned_by_addr[f"0x{addr:03X}"] += 1
        elif 192 <= src:
            self.rejected_by_bus[str(src - 192)] += 1
            self.rejected_by_addr[f"0x{addr:03X}"] += 1
        else:
            # Panda emits src 0..2 (native), 128..191 (returned TX), 192+
            # (rejected TX). Anything else is a misrouted/foreign frame:
            # count it instead of silently dropping it from every census.
            self.unexpected_src[str(src)] += 1

    def _car_state(self, t: int, v_ego: float, left: bool, right: bool) -> None:
        self._observe(t, "v_ego", v_ego)
        self._observe(t, "blinker", bool(left or right))

    def _panda_state(self, t: int, safety_tx_blocked: int) -> None:
        self.safety_tx_blocked.append((t, safety_tx_blocked))

    def _observe(self, t: int, name: str, value: Any) -> None:
        self.obs[name].update(t, value)

    def _id4(self, t: int, dat: bytes) -> None:
        op = self.obs["op"]
        op_id: int | None = None
        if op.value is not None and 0 <= t - op.t <= OP_LAG_NS_FOR_ID4:
            op_id = op.value[0]
        seg_s = None if self._seg0 is None else round((t - self._seg0) / 1e9, 9)
        self.id4_rows.append({
            "time_ns": t,
            "byte21": dat[21],
            "angle_word_hex": f"{signed_be16(dat, 18) & 0xFFFF:04x}",
            "request_level": dat[24],
            "segment_s": seg_s,
            "latActive": op_id == NATIVE_ID_ACTIVE,
        })

    def finish(self) -> SegmentResult:
        if self._next_grid is not None and self.last_live is not None:
            while self._next_grid <= self.last_live:
                self._sample(self._next_grid)
                self.grid_samples += 1
                self._next_grid += GRID_STEP_NS
        return SegmentResult(
            route=self.route,
            segment=self.segment,
            source={},
            event_counts=dict(sorted(self.event_counts.items())),
            out_of_order_events=self.out_of_order,
            first_live_ns=self.first_live,
            last_live_ns=self.last_live,
            census=self._census(),
            grid_samples=self.grid_samples,
            exclusions=dict(sorted(self.exclusions.items())),
            native_id_counts_fresh=dict(sorted(self.native_id_counts_fresh.items())),
            qualified=self.qualified,
            id4_rows=self.id4_rows,
            witness_rows=self._witness_rows(),
        )

    def _census(self) -> dict[str, Any]:
        stx = self.safety_tx_blocked
        if stx:
            safety = {"samples": len(stx), "first": stx[0][1], "last": stx[-1][1],
                      "delta": stx[-1][1] - stx[0][1]}
        else:
            safety = {"samples": 0, "first": None, "last": None, "delta": None}
        return {
            "native_by_bus": dict(self.native_by_bus),
            "native_total": sum(self.native_by_bus.values()),
            "native_absent_addresses": dict(self.native_absent),
            "returned_echo_by_bus": dict(sorted(self.returned_by_bus.items())),
            "returned_echo_total": sum(self.returned_by_bus.values()),
            "returned_b6": self.returned_by_addr.get("0x0B6", 0),
            "rejected_by_bus": dict(sorted(self.rejected_by_bus.items())),
            "rejected_b6": self.rejected_by_addr.get("0x0B6", 0),
            "sendcan_by_addr": dict(sorted(self.sendcan_by_addr.items())),
            "b6_send_shapes": dict(sorted(self.b6_shapes.items())),
            "unexpected_src": dict(sorted(self.unexpected_src.items())),
            "short_frames": self.short_frames,
            "safety_tx_blocked": safety,
        }

    def _witness_rows(self) -> list[SampleRow]:
        if not self.witness or not self.witness_window_s or self._seg0 is None:
            return []
        lo, hi = self.witness_window_s
        return [r for r in self.qualified
                if lo <= r.seg_s <= hi
                and r.native_id == NATIVE_ID_ACTIVE and r.op_id == NATIVE_ID_ACTIVE]

    # -- grid machinery --------------------------------------------------------

    def _snapshot(self, t: int, name: str) -> tuple[Any, int]:
        o = self.obs[name]
        if o.value is None or o.t < 0 or o.t > t or t - o.t > MAX_AGE_NS:
            return None, -1
        return o.value, t - o.t

    def _sample(self, t: int) -> None:
        seg_s = round((t - (self._seg0 if self._seg0 is not None else t)) / 1e9, 9)
        measured, a_m = self._snapshot(t, "measured")
        torque, a_t = self._snapshot(t, "torque")
        tinv, _a_ti = self._snapshot(t, "torque_invalid")
        motor, _a_mo = self._snapshot(t, "motor")
        native, a_n = self._snapshot(t, "native")
        reference, a_r = self._snapshot(t, "reference")
        op, a_o = self._snapshot(t, "op")
        v_ego, a_v = self._snapshot(t, "v_ego")
        blinker, _a_b = self._snapshot(t, "blinker")
        ages = {k: v for k, v in (("measured", a_m), ("torque", a_t), ("native", a_n),
                                  ("reference", a_r), ("op", a_o), ("v_ego", a_v)) if v >= 0}
        native_id = native[0] if native is not None else None
        if native is not None:
            self.native_id_counts_fresh[str(native_id)] += 1
        row = SampleRow(
            grid_ns=t, seg_s=seg_s,
            measured_deg=measured, torque_nm=torque,
            torque_valid=(not tinv) if tinv is not None else None,
            motor_proxy=motor,
            native_id=native_id,
            native_req_raw=native[1] if native is not None else None,
            native_req_deg=(round(native[1] * REQUEST_SCALE_DEG_PER_COUNT, 9)
                            if native is not None else None),
            native_level=native[2] if native is not None else None,
            reference_raw=reference,
            reference_deg=(round(reference * REQUEST_SCALE_DEG_PER_COUNT, 9)
                           if reference is not None else None),
            op_id=op[0] if op is not None else None,
            op_target_raw=op[1] if op is not None else None,
            op_target_deg=(round(op[1] * REQUEST_SCALE_DEG_PER_COUNT, 9)
                           if op is not None else None),
            v_ego=v_ego, blinker=blinker, ages_ns=ages,
        )
        # exclusion accounting (a sample may fail several; each is counted)
        if v_ego is None:
            self.exclusions["speed_stale"] += 1
        elif not v_ego > SPEED_MIN_MPS:
            self.exclusions["speed_le_10mps"] += 1
        if torque is None:
            self.exclusions["torque_stale"] += 1
        elif abs(torque) >= TORQUE_MAX_NM:
            self.exclusions["torque_ge_0p5nm"] += 1
        if tinv is None:
            self.exclusions["torque_validity_stale"] += 1
        elif tinv:
            self.exclusions["torque_invalid"] += 1
        if blinker is None:
            self.exclusions["blinker_stale"] += 1
        elif blinker:
            self.exclusions["blinker_active"] += 1
        if native is None:
            self.exclusions["native_request_stale"] += 1
        elif native_id != NATIVE_ID_ACTIVE:
            self.exclusions[f"native_id_not_{NATIVE_ID_ACTIVE}"] += 1
        if reference is None:
            self.exclusions["reference_stale"] += 1
        if measured is None:
            self.exclusions["measured_stale"] += 1
        if op is None:
            self.exclusions["openpilot_stale"] += 1
        # Base qualification keeps every native request ID (0/4/11/18/...);
        # the published quadrant subsets (manual ID0, stock ID11, dual-active,
        # divergent) are predicates over these rows, never re-filtered here.
        clean = (
            v_ego is not None and v_ego > SPEED_MIN_MPS
            and torque is not None and abs(torque) < TORQUE_MAX_NM
            and tinv is not None and not tinv
            and blinker is not None and not blinker
            and native is not None and reference is not None and measured is not None
            and op is not None
        )
        if clean and self.keep_qualified:
            self.qualified.append(row)


# --- Statistics ---------------------------------------------------------------


def pearson(xs: list[float], ys: list[float]) -> float | None:
    n = len(xs)
    if n < 2:
        return None
    mx = sum(xs) / n
    my = sum(ys) / n
    cov = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    vx = sum((x - mx) ** 2 for x in xs)
    vy = sum((y - my) ** 2 for y in ys)
    if vx == 0 or vy == 0:
        return None
    return round(cov / math.sqrt(vx * vy), 6)


def percentile(values: list[float], q: float) -> float | None:
    if not values:
        return None
    s = sorted(values)
    if len(s) == 1:
        return round(s[0], 6)
    pos = q * (len(s) - 1)
    lo = math.floor(pos)
    hi = math.ceil(pos)
    v = s[lo] + (s[hi] - s[lo]) * (pos - lo)
    return round(v, 6)


def median(values: list[float]) -> float | None:
    return percentile(values, 0.5)


def pair_stats(pairs: list[tuple[float, float]]) -> dict[str, Any]:
    if not pairs:
        return {"samples": 0}
    diffs = [abs(a - b) for a, b in pairs]
    xs = [a for a, _ in pairs]
    ys = [b for _, b in pairs]
    rmse = math.sqrt(sum(d * d for d in diffs) / len(diffs))
    return {
        "samples": len(pairs),
        "median_absolute": median(diffs),
        "p90_absolute": percentile(diffs, 0.9),
        "rmse": round(rmse, 6),
        "correlation": pearson(xs, ys),
    }


def _f(x: float | None) -> float:
    if x is None:
        raise ValueError("required signal missing in qualified row")
    return float(x)


# --- Route aggregation ---------------------------------------------------------


def _subset_stats(rows: list[SampleRow], pred) -> dict[str, Any]:
    sub = [r for r in rows if pred(r)]
    return {
        "reference081_vs_stock_raw": pair_stats(
            [(_f(r.reference_raw), _f(r.native_req_raw)) for r in sub]),
        "stock_vs_measured": pair_stats([(_f(r.native_req_deg), _f(r.measured_deg)) for r in sub]),
        "reference081_vs_measured": pair_stats([(_f(r.reference_deg), _f(r.measured_deg)) for r in sub]),
        "openpilot_vs_measured": pair_stats([(_f(r.op_target_deg), _f(r.measured_deg)) for r in sub]),
    }


def _sum_maps(maps: Iterable[dict[str, int]]) -> dict[str, int]:
    out: Counter[str] = Counter()
    for m in maps:
        out.update(m)
    return dict(sorted(out.items()))


def aggregate_route(route: str, segments: list[SegmentResult]) -> dict[str, Any]:
    segs = sorted(segments, key=lambda s: s.segment)
    samples = sum(s.grid_samples for s in segs)
    duration_ns = sum((s.last_live_ns - s.first_live_ns)
                      for s in segs if s.first_live_ns is not None and s.last_live_ns is not None)
    exclusions: Counter[str] = Counter()
    id_fresh: Counter[str] = Counter()
    for s in segs:
        exclusions.update(s.exclusions)
        id_fresh.update(s.native_id_counts_fresh)
    clean = [r for s in segs for r in s.qualified]
    any_stx = any(s.census["safety_tx_blocked"]["samples"] for s in segs)
    census = {
        "native_by_bus": {b: sum(s.census["native_by_bus"].get(b, 0) for s in segs)
                          for b in ("0", "1", "2")},
        "native_total": sum(s.census["native_total"] for s in segs),
        "native_absent_addresses": _sum_maps([s.census["native_absent_addresses"] for s in segs]),
        "returned_echo_total": sum(s.census["returned_echo_total"] for s in segs),
        "returned_b6": sum(s.census["returned_b6"] for s in segs),
        "rejected_by_bus": {b: sum(s.census["rejected_by_bus"].get(b, 0) for s in segs)
                            for b in ("0", "1", "2")},
        "rejected_b6": sum(s.census["rejected_b6"] for s in segs),
        "sendcan_b6_total": sum(s.census["sendcan_by_addr"].get("0x0B6", 0) for s in segs),
        "sendcan_by_addr": _sum_maps([s.census["sendcan_by_addr"] for s in segs]),
        "b6_send_shapes": _sum_maps([s.census["b6_send_shapes"] for s in segs]),
        "unexpected_src": _sum_maps([s.census["unexpected_src"] for s in segs]),
        "short_frames": sum(s.census["short_frames"] for s in segs),
        "safety_tx_blocked_delta": (sum(s.census["safety_tx_blocked"]["delta"] or 0 for s in segs)
                                    if any_stx else None),
        "safety_tx_blocked_samples": sum(s.census["safety_tx_blocked"]["samples"] for s in segs),
    }
    return {
        "route": route,
        "route_short": ROUTE_SHORT.get(route, route),
        "segments": [s.segment for s in segs],
        "segment_count": len(segs),
        "duration_s": round(duration_ns / 1e9, 2),
        "samples": samples,
        "exclusions": dict(sorted(exclusions.items())),
        "native_08a_id_counts_fresh": dict(sorted(id_fresh.items())),
        "comparison": {
            "manual_id0": _subset_stats(clean, lambda r: r.native_id == 0),
            "stock_id11": _subset_stats(clean, lambda r: r.native_id == NATIVE_ID_ACTIVE),
            "dual_active": _subset_stats(clean, lambda r: r.native_id == NATIVE_ID_ACTIVE
                                         and r.op_id == NATIVE_ID_ACTIVE),
            "divergent": _subset_stats(
                clean, lambda r: r.native_id == NATIVE_ID_ACTIVE and r.op_id == NATIVE_ID_ACTIVE
                and abs(_f(r.op_target_deg) - _f(r.native_req_deg)) >= DIVERGENCE_DEG),
        },
        "census": census,
    }


def id4_episodes(segments: list[SegmentResult]) -> list[dict[str, Any]]:
    """Group retained native bus-2 0x08A B21==4 frames into episodes."""
    episodes: list[dict[str, Any]] = []
    for s in sorted(segments, key=lambda x: x.segment):
        rows = sorted(s.id4_rows, key=lambda r: r["time_ns"])
        run: list[dict[str, Any]] = []
        for row in rows:
            if run and row["time_ns"] - run[-1]["time_ns"] > ID4_EPISODE_GAP_NS:
                episodes.append(_episode(s.route, s.segment, run))
                run = []
            run.append(row)
        if run:
            episodes.append(_episode(s.route, s.segment, run))
    return episodes


def _episode(route: str, segment: int, run: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "route": route,
        "route_short": ROUTE_SHORT.get(route, route),
        "segment": segment,
        "first_segment_s": run[0]["segment_s"],
        "last_segment_s": run[-1]["segment_s"],
        "first_time_ns": run[0]["time_ns"],
        "last_time_ns": run[-1]["time_ns"],
        "frames": len(run),
        "request_level_values": sorted({r["request_level"] for r in run}),
        "openpilot_lateral_active": any(r["latActive"] for r in run),
        "rows": run,
    }


# --- Ingestion adapters ---------------------------------------------------------

FIXTURE_SCHEMA = "camry-20260904-fixture-v1"


def iter_fixture_events(path: Path) -> Iterator[tuple]:
    """Yield event tuples from a JSONL fixture (stdlib-only)."""
    with path.open("r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            kind = rec["type"]
            if kind == "provenance":
                continue
            if kind in ("can", "sendcan"):
                yield (kind, rec["t"], rec["src"], rec["addr"], rec["dat"])
            elif kind == "carState":
                yield (kind, rec["t"], rec["vEgo"], rec["leftBlinker"], rec["rightBlinker"],
                       rec.get("steeringTorque"), rec.get("steeringPressed"),
                       rec.get("steeringAngleDeg"))
            elif kind == "pandaState":
                yield (kind, rec["t"], rec["safetyTxBlocked"])
            elif kind == "controlsState":
                yield (kind, rec["t"])


def _witness_summary(rows: list[SampleRow]) -> dict[str, Any]:
    if not rows:
        return {"samples": 0}
    return {
        "route": WITNESS_ROUTE,
        "segment": WITNESS_SEGMENT,
        "selection_window_s": list(WITNESS_WINDOW_S),
        "published_span_s": list(WITNESS_PUBLISHED_SPAN_S),
        "first_sample_s": rows[0].seg_s,
        "last_sample_s": rows[-1].seg_s,
        "samples": len(rows),
        "median_measured_deg": median([_f(r.measured_deg) for r in rows]),
        "median_native_08a_request_deg": median([_f(r.native_req_deg) for r in rows]),
        "median_native_081_reference_deg": median([_f(r.reference_deg) for r in rows]),
        "median_openpilot_target_deg": median([_f(r.op_target_deg) for r in rows]),
        "max_abs_driver_torque_nm": round(max(abs(_f(r.torque_nm)) for r in rows), 3),
        "median_speed_mps": median([_f(r.v_ego) for r in rows]),
    }


def load_fixture(path: Path) -> tuple[dict[str, Any], list[tuple]]:
    """Return (provenance, events) from a JSONL fixture."""
    prov: dict[str, Any] | None = None
    events = list(iter_fixture_events(path))
    with path.open("r") as f:
        for line in f:
            line = line.strip()
            if line:
                obj = json.loads(line)
                if obj.get("type") == "provenance":
                    prov = obj
                    break
    if prov is None:
        raise ValueError(f"fixture {path} has no provenance header")
    return prov, events
def reduce_fixture(path: Path, *, keep_qualified: bool = True,
                   witness: bool = False,
                   witness_window_s: tuple[float, float] | None = None) -> SegmentResult:
    prov, events = load_fixture(path)
    red = SegmentReducer(prov["route"], int(prov["segment"]), keep_qualified=keep_qualified,
                         witness=witness, witness_window_s=witness_window_s,
                         anchor_ns=int(prov["first_live_ns"]))
    for rec in sorted(events, key=lambda r: int(r[1])):
        red.feed(rec)
    return red.finish()


def load_logreader(openpilot_root: str):
    root = Path(openpilot_root).resolve()
    for cand in (root, root / "openpilot"):
        if (cand / "tools" / "lib" / "logreader.py").exists():
            # In a nested-submodule fork `cand` is itself the openpilot package,
            # so `from openpilot...` needs cand's parent importable, not cand.
            base = cand.parent if (cand / "__init__.py").exists() else cand
            if str(base) not in sys.path:
                sys.path.insert(0, str(base))
            break
    from openpilot.tools.lib.logreader import (
        LogReader,  # type: ignore[import-not-found]
    )
    return LogReader


def iter_rlog_events(LogReader, path: Path) -> Iterator[tuple]:
    """Yield normalized event tuples from one rlog (file order; caller sorts)."""
    for ev in LogReader(str(path), sort_by_time=False):
        which = ev.which()
        if which in ("can", "sendcan"):
            frames = ev.can if which == "can" else ev.sendcan
            for fr in frames:
                yield (which, int(ev.logMonoTime), int(fr.src), int(fr.address),
                       bytes(fr.dat).hex())
        elif which == "carState":
            cs = ev.carState
            yield ("carState", int(ev.logMonoTime), float(cs.vEgo), bool(cs.leftBlinker),
                   bool(cs.rightBlinker), float(cs.steeringTorque), bool(cs.steeringPressed),
                   float(cs.steeringAngleDeg))
        elif which == "pandaState":
            health = ev.pandaState.health
            if health is not None:
                yield ("pandaState", int(ev.logMonoTime), int(health.safetyTxBlocked))
        elif which == "controlsState":
            yield ("controlsState", int(ev.logMonoTime))


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def git_head(path: str) -> str | None:
    try:
        proc = subprocess.run(["git", "-C", path, "rev-parse", "HEAD"],
                              capture_output=True, text=True, timeout=15, check=False)
    except (OSError, subprocess.SubprocessError):
        return None
    return proc.stdout.strip() if proc.returncode == 0 else None


# --- Driver -----------------------------------------------------------------------


def discover_segments(input_root: Path, routes: list[str]) -> dict[str, list[Path]]:
    out: dict[str, list[Path]] = {}
    for route in routes:
        rdir = input_root / route
        segs: list[tuple[int, Path]] = []
        if rdir.is_dir():
            for p in rdir.iterdir():
                name = p.name
                if name.startswith("rlog-") and name.endswith(".zst"):
                    try:
                        segs.append((int(name[5:-4]), p))
                    except ValueError:
                        continue
        segs.sort()
        out[route] = [p for _, p in segs]
    return out


def segment_number(path: Path) -> int:
    return int(path.name[5:-4])


def reduce_segment(route: str, path: Path, events: Iterable[tuple], *, keep_qualified: bool,
                   witness: bool = False,
                   witness_window_s: tuple[float, float] | None = None) -> SegmentResult:
    red = SegmentReducer(route, segment_number(path), keep_qualified=keep_qualified,
                         witness=witness, witness_window_s=witness_window_s)
    ordered = sorted(events, key=lambda r: int(r[1]))  # stable; mirrors LogReader sort_by_time
    for rec in ordered:
        red.feed(rec)
    return red.finish()


def emit_fixture(path: Path, route: str, segment: int, events: list[tuple], *,
                 source_file: Path, source_sha: str, source_bytes: int,
                 window_s: tuple[float, float], first_live_ns: int) -> dict[str, Any]:
    lo_ns = first_live_ns + int(window_s[0] * 1e9)
    hi_ns = first_live_ns + int(window_s[1] * 1e9)
    prov = {
        "type": "provenance",
        "schema": FIXTURE_SCHEMA,
        "route": route,
        "segment": segment,
        "source_file": str(source_file),
        "source_sha256": source_sha,
        "source_bytes": source_bytes,
        "first_live_ns": first_live_ns,
        "window_s": list(window_s),
        "selection": ("live events with first_live_ns + window_s[0]*1e9 <= t < "
                      "window_s[1]*1e9; can/sendcan frames filtered to the analysis "
                      "address set; no GPS/video/other loggerd services"),
        "addresses_kept": sorted(f"0x{a:03X}" for a in ANALYSIS_ADDRESSES),
    }
    kept: list[tuple] = []
    for rec in events:
        t = int(rec[1])
        if not (lo_ns <= t < hi_ns):
            continue
        if rec[0] in ("can", "sendcan") and int(rec[3]) not in ANALYSIS_ADDRESSES:
            continue
        kept.append(rec)
    kept.sort(key=lambda r: int(r[1]))
    with path.open("w") as f:
        f.write(json.dumps(prov, sort_keys=True) + "\n")
        for rec in kept:
            kind = rec[0]
            if kind in ("can", "sendcan"):
                obj: dict[str, Any] = {"type": kind, "t": int(rec[1]), "src": int(rec[2]),
                                       "addr": int(rec[3]), "dat": rec[4]}
            elif kind == "carState":
                obj = {"type": kind, "t": int(rec[1]), "vEgo": rec[2], "leftBlinker": rec[3],
                       "rightBlinker": rec[4], "steeringTorque": rec[5],
                       "steeringPressed": rec[6], "steeringAngleDeg": rec[7]}
            elif kind == "controlsState":
                obj = {"type": kind, "t": int(rec[1])}
            elif kind == "pandaState":
                obj = {"type": kind, "t": int(rec[1]), "safetyTxBlocked": rec[2]}
            else:
                raise ValueError(f"emit_fixture: unknown event kind {kind!r}")
            f.write(json.dumps(obj, sort_keys=True) + "\n")
    return {"fixture": str(path), "events": len(kept), "source_sha256": source_sha,
            "window_s": list(window_s)}


def _segment_gaps(segments: list[int]) -> list[list[int]]:
    return [[a, b] for a, b in itertools.pairwise(segments) if b != a + 1]



def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--input-root", default=DEFAULT_INPUT_ROOT,
                    help=f"caller-supplied corpus root (default {DEFAULT_INPUT_ROOT})")
    ap.add_argument("--openpilot-root", default=DEFAULT_OPENPILOT_ROOT,
                    help="openpilot checkout providing LogReader")
    ap.add_argument("--routes", default=",".join(DEFAULT_ROUTES))
    ap.add_argument("--manifest", default=OUT_MANIFEST)
    ap.add_argument("--report", default=OUT_REPORT)
    ap.add_argument("--out-root", default="build/out/camry-20260904-stock-steering",
                    help="review-aid output directory (reports, CSV, SVG)")
    ap.add_argument("--emit-fixtures", metavar="DIR",
                    help="write compact JSONL fixtures for the witness/ID4 segments")
    args = ap.parse_args(argv)

    input_root = Path(args.input_root)
    routes = [r.strip() for r in args.routes.split(",") if r.strip()]
    LogReader = load_logreader(args.openpilot_root)
    parser_identity = {
        "logreader": "openpilot.tools.lib.logreader.LogReader",
        "openpilot_root": str(Path(args.openpilot_root).resolve()),
        "openpilot_head": git_head(args.openpilot_root),
        "sort": "python stable sort by logMonoTime (mirrors LogReader sort_by_time)",
    }

    discovered = discover_segments(input_root, routes)
    manifest_routes: list[dict[str, Any]] = []
    seg_results: list[SegmentResult] = []
    fixture_infos: list[dict[str, Any]] = []
    seen_hashes: dict[str, str] = {}
    duplicates: list[str] = []

    for route in routes:
        for path in discovered.get(route, []):
            entry: dict[str, Any] = {
                "route": route, "segment": segment_number(path), "file": str(path),
                "bytes": path.stat().st_size,
            }
            sha = sha256_file(path)
            entry["sha256"] = sha
            if sha in seen_hashes:
                duplicates.append(f"{path} duplicates {seen_hashes[sha]}")
            else:
                seen_hashes[sha] = str(path)
            is_witness = route == WITNESS_ROUTE and segment_number(path) == WITNESS_SEGMENT
            events = list(iter_rlog_events(LogReader, path))
            entry["events_total"] = len(events)
            res = reduce_segment(route, path, events, keep_qualified=True,
                                 witness=is_witness,
                                 witness_window_s=WITNESS_WINDOW_S if is_witness else None)
            res.source = entry
            entry["event_counts"] = res.event_counts
            entry["out_of_order_events"] = res.out_of_order_events
            entry["first_live_ns"] = res.first_live_ns
            entry["last_live_ns"] = res.last_live_ns
            entry["duration_s"] = (round((res.last_live_ns - res.first_live_ns) / 1e9, 3)
                                   if res.first_live_ns is not None
                                   and res.last_live_ns is not None else None)
            manifest_routes.append(entry)
            seg_results.append(res)
            if args.emit_fixtures and res.first_live_ns is not None and (is_witness or res.id4_rows):
                fdir = Path(args.emit_fixtures)
                fdir.mkdir(parents=True, exist_ok=True)
                fname = f"{ROUTE_SHORT.get(route, route[:6])}-seg{segment_number(path)}.jsonl"
                if is_witness:
                    window = WITNESS_WINDOW_S
                else:
                    seg_s_vals = [r["segment_s"] for r in res.id4_rows if r["segment_s"] is not None]
                    window = (max(0.0, min(seg_s_vals) - 2.0), max(seg_s_vals) + 2.0)
                info = emit_fixture(fdir / fname, route, segment_number(path), events,
                                    source_file=path, source_sha=sha, source_bytes=entry["bytes"],
                                    window_s=window, first_live_ns=res.first_live_ns)
                fixture_infos.append(info)

    by_route: dict[str, list[SegmentResult]] = {}
    for res in seg_results:
        by_route.setdefault(res.route, []).append(res)

    route_reports = [aggregate_route(route, by_route.get(route, [])) for route in routes]
    episodes = id4_episodes(seg_results)
    witness_rows = next((s.witness_rows for s in seg_results
                         if s.route == WITNESS_ROUTE and s.segment == WITNESS_SEGMENT), [])

    manifest = {
        "schema": "camry-20260904-stock-steering-manifest-v1",
        "input_root": str(input_root),
        "parser": parser_identity,
        "routes": manifest_routes,
        "input_quality": {
            "missing_route_dirs": [r for r in routes if not (input_root / r).is_dir()],
            "segment_gaps": {
                route: _segment_gaps([e["segment"] for e in manifest_routes if e["route"] == route])
            },
            "duplicates": duplicates,
            "out_of_order_segments": [
                {"route": e["route"], "segment": e["segment"], "events": e["out_of_order_events"]}
                for e in manifest_routes if e["out_of_order_events"]
            ],
        },
        "fixtures": fixture_infos,
    }

    stx_any = any(rr["census"]["safety_tx_blocked_delta"] is not None for rr in route_reports)
    report = {
        "schema": "camry-20260904-stock-steering-report-v1",
        "sampling": {
            "rate_hz": SAMPLE_HZ, "max_age_ns": MAX_AGE_NS,
            "speed_min_mps": SPEED_MIN_MPS, "torque_max_nm": TORQUE_MAX_NM,
            "native_active_id": NATIVE_ID_ACTIVE, "divergence_deg": DIVERGENCE_DEG,
            "method": ("per-segment 20 Hz grid anchored at first live event; last-observed "
                       "values at or before each grid time; per-signal ages retained"),
        },
        "decode_provenance": DECODE_PROVENANCE,
        "request_scale_deg_per_count": REQUEST_SCALE_DEG_PER_COUNT,
        "totals": {
            "segments": sum(rr["segment_count"] for rr in route_reports),
            "native_can_records_buses_012": sum(rr["census"]["native_total"] for rr in route_reports),
            "sendcan_b6": sum(rr["census"]["sendcan_b6_total"] for rr in route_reports),
            "returned_echoes": sum(rr["census"]["returned_echo_total"] for rr in route_reports),
            "returned_b6": sum(rr["census"]["returned_b6"] for rr in route_reports),
            "rejected_b6": sum(rr["census"]["rejected_b6"] for rr in route_reports),
            "native_absent_addresses": _sum_maps(
                [rr["census"]["native_absent_addresses"] for rr in route_reports]),
            "safety_tx_blocked_delta": (sum(rr["census"]["safety_tx_blocked_delta"] or 0
                                            for rr in route_reports) if stx_any else None),
        },
        "routes": route_reports,
        "id4_episodes": [{k: v for k, v in ep.items() if k != "rows"} for ep in episodes],
        "id4_total_frames": sum(ep["frames"] for ep in episodes),
        "witness": _witness_summary(witness_rows),
    }

    for rel, obj in ((args.manifest, manifest), (args.report, report)):
        target = REPO / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n")

    _write_review_aids(Path(args.out_root), report, episodes, witness_rows)
    print(json.dumps({"manifest": args.manifest, "report": args.report,
                      "segments": report["totals"]["segments"],
                      "native_total": report["totals"]["native_can_records_buses_012"],
                      "id4_frames": report["id4_total_frames"]}, indent=2))
    return 0


def _write_review_aids(out_root: Path, report: dict, episodes: list[dict[str, Any]],
                       witness_rows: list[SampleRow]) -> None:
    out_root.mkdir(parents=True, exist_ok=True)
    csv_path = out_root / "route3c-segment43-witness.csv"
    with csv_path.open("w") as f:
        f.write("segment_s,measured_deg,native_request_deg,native_reference_deg,openpilot_transmitted_deg,"
                "driver_torque_nm,speed_mps\n")
        for r in witness_rows:
            f.write(f"{r.seg_s:.9f},{r.measured_deg},{r.native_req_deg},{r.reference_deg},"
                    f"{r.op_target_deg},{r.torque_nm},{r.v_ego}\n")
    _write_svg(out_root / "route3c-segment43-witness.svg", witness_rows)
    ep_path = out_root / "id4-episodes.csv"
    with ep_path.open("w") as f:
        f.write("route,segment,first_segment_s,last_segment_s,frames,levels,latActive\n")
        for ep in episodes:
            f.write(f"{ep['route_short']},{ep['segment']},{ep['first_segment_s']:.6f},"
                    f"{ep['last_segment_s']:.6f},{ep['frames']},{ep['request_level_values']},"
                    f"{ep['openpilot_lateral_active']}\n")
    md = [
        "# 2026-09-04 Camry stock-steering passive reduction",
        "",
        (f"Segments: {report['totals']['segments']}; native bus-0/1/2 records: "
         f"{report['totals']['native_can_records_buses_012']}; "
         f"native B6/0x131/0x2E4: {report['totals']['native_absent_addresses']}."),
        "",
    ]
    for rr in report["routes"]:
        c = rr["comparison"]["stock_id11"]["reference081_vs_stock_raw"]
        md.append(f"- route `{rr['route_short']}`: samples {rr['samples']}, duration "
                  f"{rr['duration_s']} s, clean native-ID11 {c['samples']}, "
                  f"r(081,08A)={c['correlation']}, median|d|={c['median_absolute']} raw, "
                  f"p90={c['p90_absolute']} raw")
    w = report["witness"]
    if w.get("samples"):
        md += [
            "",
            (f"Witness (route 3c seg {w['segment']}): {w['samples']} samples; medians "
             f"measured {w['median_measured_deg']} deg, 0x08A {w['median_native_08a_request_deg']} deg, "
             f"0x081 {w['median_native_081_reference_deg']} deg, "
             f"openpilot {w['median_openpilot_target_deg']} deg."),
        ]
    md += [
        "",
        (f"ID4 episodes: {report['id4_total_frames']} frames across "
         f"{len(report['id4_episodes'])} episodes."),
    ]
    (out_root / "report.md").write_text("\n".join(md) + "\n")


def _write_svg(path: Path, rows: list[SampleRow]) -> None:
    if not rows:
        path.write_text("<svg xmlns='http://www.w3.org/2000/svg'/>\n")
        return
    series = (("measured", [r.measured_deg for r in rows]),
              ("native_08A", [r.native_req_deg for r in rows]),
              ("native_081", [r.reference_deg for r in rows]),
              ("openpilot_B6", [r.op_target_deg for r in rows]))
    w, h, pad = 960, 480, 48
    lo = min(min(v for v in vals if v is not None) for _, vals in series)
    hi = max(max(v for v in vals if v is not None) for _, vals in series)
    span = (hi - lo) or 1.0
    t0, t1 = rows[0].seg_s, rows[-1].seg_s
    tsp = (t1 - t0) or 1.0
    colors = {"measured": "#111", "native_08A": "#0a7", "native_081": "#77c", "openpilot_B6": "#d33"}
    parts = [f"<svg xmlns='http://www.w3.org/2000/svg' width='{w}' height='{h}' viewBox='0 0 {w} {h}'>",
             "<rect width='100%' height='100%' fill='white'/>"]
    for name, vals in series:
        pts = []
        for r, v in zip(rows, vals):
            if v is None:
                continue
            x = pad + (r.seg_s - t0) / tsp * (w - 2 * pad)
            y = h - pad - (v - lo) / span * (h - 2 * pad)
            pts.append(f"{x:.1f},{y:.1f}")
        parts.append(f"<polyline fill='none' stroke='{colors[name]}' stroke-width='1.6' "
                     f"points='{' '.join(pts)}'/>")
    parts.append(f"<text x='{pad}' y='24' font-family='monospace' font-size='13'>"
                 f"route 3c segment 43 witness {t0:.2f}..{t1:.2f} s, deg [{lo:.2f},{hi:.2f}]</text>")
    for i, (name, _vals) in enumerate(series):
        parts.append(f"<text x='{pad + i * 170}' y='42' font-family='monospace' font-size='12' "
                     f"fill='{colors[name]}'>{name}</text>")
    parts.append("</svg>")
    path.write_text("\n".join(parts) + "\n")


if __name__ == "__main__":
    raise SystemExit(main())
