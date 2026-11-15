#!/usr/bin/env python3
"""Offline bakeoff for low-speed TSS3 steering-request smoothing.

This analysis uses maintainer Camry rlogs external to the repository. It replays
recorded carControl requests at the recorded CAN-loop cadence, applies the
current opendbc TSS3 vehicle-model limiter, and compares a small retained set of
candidate request shapers. It also scans the source corpus for native FRC ID11
0x08A low-speed request texture.

Usage:
  /path/to/kai-openpilot/.venv/bin/python \
    tools/targets/camry/analysis/analyze_camry_20261114_low_speed_steering_filter.py \
    --log-root /Users/kai/dev/inspect/logs/camry-2026 \
    --openpilot-root /Users/kai/dev/inspect/repos/kai-openpilot
"""
from __future__ import annotations

import argparse
import bisect
import json
import math
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np

DEFAULT_LOG_ROOT = "/Users/kai/dev/inspect/logs/camry-2026"
DEFAULT_OPENPILOT_ROOT = "/Users/kai/dev/inspect/repos/kai-openpilot"
DEFAULT_OUTPUT = "data/generated/camry_20261114_low_speed_steering_filter.json"

SCAN_DATES = (
    "2026-09-06", "2026-09-07", "2026-09-10",
    "2026-09-11", "2026-09-18", "2026-11-12",
)

CORPUS = (
    "2026-09-18/0000010c--506d7277c7/rlog-18.zst",
    "2026-09-07/00000048--709f22277b/00000048--709f22277b--1/rlog.zst",
    "2026-09-07/00000048--709f22277b/00000048--709f22277b--0/rlog.zst",
    "2026-09-18/0000010c--506d7277c7/rlog-17.zst",
    "2026-11-12/00000126--a98b6dd040--0/rlog.zst",
    "2026-09-06/0000003f--36e72f5fdc/0000003f--36e72f5fdc--22/rlog.zst",
    "2026-09-10/0000008d--a9f348691a/rlog-6.zst",
    "2026-11-12/00000126--a98b6dd040--1/rlog.zst",
    "2026-09-18/0000010c--506d7277c7/rlog-5.zst",
    "2026-09-07/00000045--805b7ca6ab/00000045--805b7ca6ab--9/rlog.zst",
    "2026-09-10/0000008d--a9f348691a/rlog-7.zst",
)

VARIANTS = (
    "baseline",
    "yc",
    "rc15",
    "rc20",
    "rc25",
    "shape30_8_8",
)


def load_stack(openpilot_root: str):
    root = Path(openpilot_root).resolve()
    for p in (root / "opendbc_repo", root):
        if str(p) not in sys.path:
            sys.path.insert(0, str(p))

    from openpilot.tools.lib.logreader import LogReader
    from openpilot.selfdrive.controls.lib.drive_helpers import get_curvature_from_plan
    from opendbc.car.common.filter_simple import FirstOrderFilter
    from opendbc.car.lateral import apply_steer_angle_limits_vm
    from opendbc.car.toyota.carcontroller import get_safety_CP
    from opendbc.car.toyota.values import CarControllerParams
    from opendbc.car.vehicle_model import VehicleModel
    return LogReader, get_curvature_from_plan, FirstOrderFilter, apply_steer_angle_limits_vm, get_safety_CP, CarControllerParams, VehicleModel


@dataclass
class Sample:
    t: float
    speed: float
    measured: float
    steering_rate: float
    offset: float
    desired: float
    enabled: bool
    active: bool


def load_can_loop_samples(LogReader, path: Path) -> list[Sample]:
    msgs = list(LogReader(str(path), only_union_types=True))
    if not msgs:
        return []
    t0 = msgs[0].logMonoTime

    states: list[tuple[float, float, float, float, float]] = []
    controls: list[tuple[float, float, bool, bool]] = []
    ticks: list[float] = []

    for msg in msgs:
        t = (msg.logMonoTime - t0) * 1e-9
        which = msg.which()
        if which == "carState":
            cs = msg.carState
            states.append((
                t,
                float(cs.vEgoRaw),
                float(cs.steeringAngleDeg),
                float(cs.steeringRateDeg),
                float(cs.steeringAngleOffsetDeg),
            ))
        elif which == "carControl":
            cc = msg.carControl
            controls.append((
                t,
                float(cc.actuators.steeringAngleDeg),
                bool(cc.enabled),
                bool(cc.latActive),
            ))
        elif which == "can":
            ticks.append(t)

    if not states or not controls:
        return []

    state_times = [x[0] for x in states]
    control_times = [x[0] for x in controls]
    out: list[Sample] = []
    for t in ticks:
        si = bisect.bisect_right(state_times, t) - 1
        ci = bisect.bisect_right(control_times, t) - 1
        if si < 0 or ci < 0:
            continue
        _, speed, angle, rate, offset = states[si]
        _, desired, enabled, active = controls[ci]
        out.append(Sample(
            t=t,
            speed=speed,
            measured=angle + offset,
            steering_rate=rate,
            offset=offset,
            desired=desired,
            enabled=enabled,
            active=active,
        ))
    return out


class RequestSimulator:
    def __init__(
        self,
        variant: str,
        *,
        FirstOrderFilter,
        apply_steer_angle_limits_vm,
        get_safety_CP,
        CarControllerParams,
        VehicleModel,
    ):
        self.variant = variant
        safety_cp = get_safety_CP()
        self.params = CarControllerParams(safety_cp)
        self.vm = VehicleModel(safety_cp)
        self.apply_limits = apply_steer_angle_limits_vm
        self.scale = CarControllerParams.TSS3_TARGET_ANGLE_SCALE_DEG
        self.filter = FirstOrderFilter(0.0, 0.0, 0.01, initialized=False)

        self.last_angle = 0.0
        self.initialized = False
        self.last_t: float | None = None

        self.yc_pos = 0.0
        self.yc_vel = 0.0

    def _reset(self, sample: Sample) -> None:
        self.last_angle = sample.measured
        self.filter.x = sample.measured
        self.filter.initialized = True
        self.yc_pos = sample.measured
        self.yc_vel = 0.0
        self.initialized = True

    def step(self, sample: Sample) -> float:
        reset = (
            not self.initialized
            or self.last_t is None
            or sample.t - self.last_t > 0.1
            or not sample.enabled
        )
        if reset:
            self._reset(sample)

        active = (
            sample.enabled
            and sample.active
            and abs(sample.measured) < self.params.ANGLE_LIMITS.STEER_ANGLE_MAX
        )
        target = sample.desired + sample.offset

        if self.variant == "yc":
            if not active or self.last_t is None:
                self.yc_pos = sample.measured
                self.yc_vel = 0.0
            elif sample.speed < 9.0:
                dt = float(np.clip(sample.t - self.last_t, 0.005, 0.05))
                wn = min(float(np.interp(sample.speed, [2.0, 9.0], [6.0, 15.0])), 0.3 / dt)
                kp = wn * wn
                kd = 2.0 * wn
                max_accel = float(np.interp(sample.speed, [2.0, 9.0], [180.0, 900.0]))
                max_rate = float(np.interp(
                    sample.speed,
                    [2.0, 9.0],
                    [90.0, self.params.ANGLE_LIMITS.MAX_ANGLE_RATE / dt],
                ))
                if (
                    self.yc_pos < sample.measured < target
                    or target < sample.measured < self.yc_pos
                ):
                    self.yc_pos = sample.measured
                    self.yc_vel = float(np.clip(sample.steering_rate, -max_rate, max_rate))
                accel = float(np.clip(
                    kp * (target - self.yc_pos) - kd * self.yc_vel,
                    -max_accel,
                    max_accel,
                ))
                self.yc_vel = float(np.clip(
                    self.yc_vel + accel * dt,
                    -max_rate,
                    max_rate,
                ))
                self.yc_pos += self.yc_vel * dt
                target = self.yc_pos
            else:
                self.yc_pos = target
                self.yc_vel = 0.0

        elif self.variant.startswith("rc") or self.variant == "shape30_8_8":
            if not active or not self.filter.initialized:
                self.filter.x = sample.measured
                self.filter.initialized = True

            if active:
                if self.variant == "shape30_8_8":
                    rc = float(np.interp(
                        sample.speed,
                        [0.0, 5.0, 9.0, 12.0],
                        [0.030, 0.008, 0.008, 0.0],
                    ))
                else:
                    rc0 = int(self.variant.removeprefix("rc")) / 1000.0
                    rc = float(np.interp(
                        sample.speed,
                        [0.0, 9.0, 12.0],
                        [rc0, rc0 * 0.35, 0.0],
                    ))
                dt = 0.01 if self.last_t is None else float(np.clip(sample.t - self.last_t, 0.005, 0.05))
                self.filter.update_dt(dt)
                self.filter.update_alpha(rc)
                target = self.filter.update(target)

        self.last_angle = self.apply_limits(
            target,
            self.last_angle,
            sample.speed,
            sample.measured,
            active,
            self.params,
            self.vm,
        )
        if self.variant.startswith("rc") or self.variant == "shape30_8_8":
            self.filter.x = self.last_angle

        self.last_t = sample.t
        return round(self.last_angle / self.scale) * self.scale


def contiguous_runs(samples: list[Sample]) -> list[list[int]]:
    runs: list[list[int]] = []
    current: list[int] = []
    prev = -2
    for i, sample in enumerate(samples):
        valid = sample.enabled and sample.active and 1.0 <= sample.speed < 9.0
        if not valid:
            if len(current) >= 3:
                runs.append(current)
            current = []
            prev = -2
            continue
        if not current or (i == prev + 1 and sample.t - samples[prev].t < 0.03):
            current.append(i)
        else:
            if len(current) >= 3:
                runs.append(current)
            current = [i]
        prev = i
    if len(current) >= 3:
        runs.append(current)
    return runs


def variant_metrics(samples: list[Sample], baseline: np.ndarray, values: np.ndarray) -> dict[str, Any] | None:
    runs = contiguous_runs(samples)
    if not runs:
        return None

    indices: list[int] = []
    steps: list[float] = []
    second: list[float] = []
    duration = 0.0
    reversals = 0
    reversal_energy = 0.0
    lags: list[int] = []
    lag_weights: list[int] = []

    for run in runs:
        indices.extend(run)
        x = values[run]
        b = baseline[run]
        t = np.asarray([samples[i].t for i in run])
        d = np.diff(x)
        steps.extend(d)
        second.extend(np.diff(x, 2))
        duration += t[-1] - t[0]

        nz = np.where(np.abs(d) >= 0.057302742)[0]
        if len(nz) > 1:
            signs = np.sign(d[nz])
            flips = np.where(np.diff(signs) != 0)[0]
            reversals += len(flips)
            for flip in flips:
                reversal_energy += min(abs(d[nz[flip]]), abs(d[nz[flip + 1]]))

        if len(run) >= 40:
            rms: list[float] = []
            for lag in range(0, min(21, len(run) // 4)):
                err = b - x if lag == 0 else b[:-lag] - x[lag:]
                rms.append(float(np.sqrt(np.mean(err * err))))
            lags.append(int(np.argmin(rms)))
            lag_weights.append(len(run))

    if not steps:
        return None

    idx = np.asarray(indices, dtype=int)
    step_arr = np.asarray(steps)
    second_arr = np.asarray(second)
    dev = np.abs(values[idx] - baseline[idx])
    abs_step = np.abs(step_arr)

    return {
        "frames": int(len(idx)),
        "seconds": duration,
        "step_rms_deg": float(np.sqrt(np.mean(step_arr * step_arr))),
        "step_p95_deg": float(np.percentile(abs_step, 95)),
        "second_difference_rms_deg": float(np.sqrt(np.mean(second_arr * second_arr))) if len(second_arr) else 0.0,
        "total_variation_per_s_deg": float(np.sum(abs_step) / duration),
        "reversal_energy_per_s_deg": float(reversal_energy / duration),
        "reversals_per_s": float(reversals / duration),
        "mean_abs_deviation_deg": float(np.mean(dev)),
        "p95_abs_deviation_deg": float(np.percentile(dev, 95)),
        "max_abs_deviation_deg": float(np.max(dev)),
        "best_fit_lag_frames": float(np.average(lags, weights=lag_weights)) if lags else 0.0,
    }


def pool_metrics(per_segment: dict[str, list[dict[str, Any]]]) -> dict[str, dict[str, Any]]:
    pooled: dict[str, dict[str, Any]] = {}
    for variant, rows in per_segment.items():
        frames = sum(r["frames"] for r in rows)
        seconds = sum(r["seconds"] for r in rows)

        def frame_mean(key: str) -> float:
            return sum(r[key] * r["frames"] for r in rows) / frames

        def second_mean(key: str) -> float:
            return math.sqrt(sum((r[key] ** 2) * r["frames"] for r in rows) / frames)

        def time_mean(key: str) -> float:
            return sum(r[key] * r["seconds"] for r in rows) / seconds

        pooled[variant] = {
            "segments": len(rows),
            "frames": frames,
            "seconds": seconds,
            "step_rms_deg": second_mean("step_rms_deg"),
            "step_p95_deg": frame_mean("step_p95_deg"),
            "second_difference_rms_deg": second_mean("second_difference_rms_deg"),
            "total_variation_per_s_deg": time_mean("total_variation_per_s_deg"),
            "reversal_energy_per_s_deg": time_mean("reversal_energy_per_s_deg"),
            "reversals_per_s": time_mean("reversals_per_s"),
            "mean_abs_deviation_deg": frame_mean("mean_abs_deviation_deg"),
            "p95_abs_deviation_deg": frame_mean("p95_abs_deviation_deg"),
            "max_abs_deviation_deg": max(r["max_abs_deviation_deg"] for r in rows),
            "best_fit_lag_frames": frame_mean("best_fit_lag_frames"),
        }
    return pooled


def request_update_structure(samples_by_file: list[list[Sample]]) -> dict[str, Any]:
    deltas: list[float] = []
    update_intervals: list[float] = []
    for samples in samples_by_file:
        prev: Sample | None = None
        last_update_t: float | None = None
        for sample in samples:
            if not (sample.enabled and sample.active and 1.0 <= sample.speed < 9.0):
                prev = None
                last_update_t = None
                continue
            if prev is not None:
                delta = sample.desired - prev.desired
                deltas.append(delta)
                if abs(delta) >= 0.02:
                    if last_update_t is not None:
                        update_intervals.append(sample.t - last_update_t)
                    last_update_t = sample.t
            prev = sample

    abs_delta = np.abs(np.asarray(deltas))
    intervals = np.asarray(update_intervals)
    return {
        "pairs": len(deltas),
        "fraction_abs_delta_le_0_01": float(np.mean(abs_delta <= 0.01)),
        "fraction_abs_delta_le_0_05": float(np.mean(abs_delta <= 0.05)),
        "fraction_abs_delta_gt_0_1": float(np.mean(abs_delta > 0.1)),
        "fraction_abs_delta_gt_0_3": float(np.mean(abs_delta > 0.3)),
        "fraction_abs_delta_gt_0_5": float(np.mean(abs_delta > 0.5)),
        "fraction_abs_delta_gt_1_0": float(np.mean(abs_delta > 1.0)),
        "significant_update_interval_median_ms": float(np.median(intervals) * 1000.0),
        "fraction_significant_intervals_40_to_60_ms": float(np.mean((intervals >= 0.04) & (intervals <= 0.06))),
    }


def stock_request_scan(LogReader, root: Path) -> dict[str, Any]:
    scale = 1024 / 17870
    steps: list[float] = []
    source_files: list[dict[str, Any]] = []
    total_seconds = 0.0
    reversals = 0
    reversal_energy = 0.0

    paths: list[Path] = []
    for date in SCAN_DATES:
        paths.extend((root / date).glob("**/rlog.zst"))
        paths.extend((root / date).glob("**/rlog-*.zst"))

    for path in sorted(set(paths)):
        speed = 0.0
        previous: tuple[float, int, int] | None = None
        previous_step = 0.0
        local_steps: list[float] = []
        local_seconds = 0.0
        local_reversals = 0
        local_reversal_energy = 0.0

        for msg in LogReader(str(path), only_union_types=True):
            which = msg.which()
            if which == "carState":
                speed = float(msg.carState.vEgoRaw)
                continue
            if which != "can":
                continue

            t = msg.logMonoTime * 1e-9
            for frame in msg.can:
                if frame.address != 0x08A or len(frame.dat) != 32 or int(frame.src) != 2:
                    continue
                dat = bytes(frame.dat)
                request_id = dat[21] & 0x3F
                if request_id != 11 or not (1.0 <= speed < 9.0):
                    previous = None
                    previous_step = 0.0
                    continue

                raw = int.from_bytes(dat[18:20], "big", signed=True)
                seq = dat[26] & 0x3F
                if previous is not None:
                    pt, praw, pseq = previous
                    if t - pt < 0.03 and ((seq - pseq) & 0x3F) == 1:
                        step = (raw - praw) * scale
                        local_steps.append(step)
                        local_seconds += t - pt
                        if (
                            abs(step) >= scale
                            and abs(previous_step) >= scale
                            and np.sign(step) != np.sign(previous_step)
                        ):
                            local_reversals += 1
                            local_reversal_energy += min(abs(step), abs(previous_step))
                        if abs(step) >= scale:
                            previous_step = step
                    else:
                        previous_step = 0.0
                previous = (t, raw, seq)

        if local_steps:
            arr = np.asarray(local_steps)
            source_files.append({
                "path": str(path.relative_to(root)),
                "steps": len(arr),
                "seconds": local_seconds,
                "step_rms_deg": float(np.sqrt(np.mean(arr * arr))),
                "step_p95_deg": float(np.percentile(np.abs(arr), 95)),
            })
            steps.extend(local_steps)
            total_seconds += local_seconds
            reversals += local_reversals
            reversal_energy += local_reversal_energy

    arr = np.asarray(steps)
    return {
        "files_scanned": len(set(paths)),
        "files_with_native_id11_low_speed": len(source_files),
        "source_files": source_files,
        "steps": len(arr),
        "seconds": total_seconds,
        "step_rms_deg": float(np.sqrt(np.mean(arr * arr))) if len(arr) else None,
        "step_p95_deg": float(np.percentile(np.abs(arr), 95)) if len(arr) else None,
        "step_p99_deg": float(np.percentile(np.abs(arr), 99)) if len(arr) else None,
        "fraction_abs_step_ge_0_3": float(np.mean(np.abs(arr) >= 0.3)) if len(arr) else None,
        "reversals_per_s": reversals / total_seconds if total_seconds else None,
        "reversal_energy_per_s_deg": reversal_energy / total_seconds if total_seconds else None,
    }



def root_layer_diagnostics(LogReader, get_curvature_from_plan, root: Path) -> dict[str, Any]:
    """Trace the low-speed staircase to model updates and the action->curvature conversion."""
    november = (
        root / "2026-11-12/00000126--a98b6dd040--0/rlog.zst",
        root / "2026-11-12/00000126--a98b6dd040--1/rlog.zst",
    )

    update_ages_ms: list[float] = []
    plan_diffs: list[float] = []
    action_bins: dict[int, list[float]] = {b: [] for b in range(1, 9)}
    lat_action_bins: dict[int, list[float]] = {b: [] for b in range(1, 9)}

    for path in november:
        v_ego = 0.0
        v_ego_raw = 0.0
        lateral_delay = 0.3
        last_model_t: float | None = None
        previous_angle: float | None = None
        active = False

        for msg in LogReader(str(path), only_union_types=True):
            t = msg.logMonoTime * 1e-9
            which = msg.which()
            if which == "carState":
                v_ego = float(msg.carState.vEgo)
                v_ego_raw = float(msg.carState.vEgoRaw)
            elif which == "lateralDelay":
                lateral_delay = float(msg.lateralDelay.lateralDelay)
            elif which == "modelV2":
                last_model_t = t
                if active and 1.0 <= v_ego_raw < 9.0:
                    model = msg.modelV2
                    tids = np.asarray(list(model.orientation.t), dtype=float)
                    yaws = np.asarray(list(model.orientation.z), dtype=float)
                    yaw_rates = np.asarray(list(model.orientationRate.z), dtype=float)
                    plan_curvature = get_curvature_from_plan(
                        yaws,
                        yaw_rates,
                        tids,
                        v_ego,
                        lateral_delay + 0.075,
                    )
                    plan_diffs.append(plan_curvature - float(model.action.desiredCurvature))
            elif which == "carControl":
                cc = msg.carControl
                active = bool(cc.enabled and cc.latActive)
                if not (active and 1.0 <= v_ego_raw < 9.0):
                    previous_angle = None
                    continue
                angle = float(cc.actuators.steeringAngleDeg)
                if previous_angle is not None and abs(angle - previous_angle) > 0.05 and last_model_t is not None:
                    update_ages_ms.append((t - last_model_t) * 1000.0)
                previous_angle = angle

    for rel in CORPUS:
        path = root / rel
        v_ego = 0.0
        v_ego_raw = 0.0
        active = False
        previous_curvature: float | None = None
        previous_lat_action: float | None = None

        for msg in LogReader(str(path), only_union_types=True):
            which = msg.which()
            if which == "carState":
                v_ego = float(msg.carState.vEgo)
                v_ego_raw = float(msg.carState.vEgoRaw)
            elif which == "carControl":
                active = bool(msg.carControl.enabled and msg.carControl.latActive)
                if not active:
                    previous_curvature = None
                    previous_lat_action = None
            elif which == "modelV2":
                if not (active and 1.0 <= v_ego_raw < 9.0):
                    previous_curvature = None
                    previous_lat_action = None
                    continue
                curvature = float(msg.modelV2.action.desiredCurvature)
                lat_action = curvature * max(2.5, v_ego) ** 2
                if previous_curvature is not None and previous_lat_action is not None:
                    speed_bin = int(v_ego_raw)
                    action_bins[speed_bin].append(curvature - previous_curvature)
                    lat_action_bins[speed_bin].append(lat_action - previous_lat_action)
                previous_curvature = curvature
                previous_lat_action = lat_action

    ages = np.asarray(update_ages_ms, dtype=float)
    pdiff = np.asarray(plan_diffs, dtype=float)
    by_speed: dict[str, Any] = {}
    for speed_bin in range(1, 9):
        curv = np.asarray(action_bins[speed_bin], dtype=float)
        lat = np.asarray(lat_action_bins[speed_bin], dtype=float)
        if not len(curv):
            continue
        by_speed[f"{speed_bin}-{speed_bin + 1}"] = {
            "samples": len(curv),
            "curvature_delta_rms": float(np.sqrt(np.mean(curv * curv))),
            "curvature_delta_p95": float(np.percentile(np.abs(curv), 95)),
            "decoded_lateral_action_delta_rms": float(np.sqrt(np.mean(lat * lat))),
            "decoded_lateral_action_delta_p95": float(np.percentile(np.abs(lat), 95)),
        }

    return {
        "november_significant_angle_update_alignment": {
            "count": len(ages),
            "model_update_age_median_ms": float(np.median(ages)) if len(ages) else None,
            "model_update_age_p90_ms": float(np.percentile(ages, 90)) if len(ages) else None,
            "fraction_within_15_ms": float(np.mean(ages <= 15.0)) if len(ages) else None,
            "fraction_within_20_ms": float(np.mean(ages <= 20.0)) if len(ages) else None,
        },
        "november_action_vs_plan_at_action_horizon": {
            "samples": len(pdiff),
            "mean_abs_curvature_difference": float(np.mean(np.abs(pdiff))) if len(pdiff) else None,
            "p95_abs_curvature_difference": float(np.percentile(np.abs(pdiff), 95)) if len(pdiff) else None,
            "rms_curvature_difference": float(np.sqrt(np.mean(pdiff * pdiff))) if len(pdiff) else None,
        },
        "model_action_deltas_by_speed_mps": by_speed,
    }



GENERIC_REFERENCE_RCS = {
    "curvature_ref_mdl4": 0.0125,
    "curvature_ref_mdl3": 1.0 / 60.0,
}


def generic_reference_bakeoff(
    LogReader,
    FirstOrderFilter,
    apply_steer_angle_limits_vm,
    get_safety_CP,
    CarControllerParams,
    VehicleModel,
    root: Path,
) -> dict[str, Any]:
    """Compare a 100-Hz generic curvature reference against the recorded angle path."""

    variants = ("baseline", *GENERIC_REFERENCE_RCS.keys())
    per_variant: dict[str, list[dict[str, Any]]] = {variant: [] for variant in variants}

    for rel in CORPUS:
        path = root / rel
        msgs = list(LogReader(str(path), only_union_types=True))
        if not msgs:
            continue
        t0 = msgs[0].logMonoTime
        cp = next(msg.carParams for msg in msgs if msg.which() == "carParams")

        states: list[tuple[float, float, float, float, float]] = []
        params_rows: list[tuple[float, float, float, float, float]] = []
        model_times: list[float] = []
        controls: list[tuple[float, float, bool, bool]] = []

        for msg in msgs:
            t = (msg.logMonoTime - t0) * 1e-9
            which = msg.which()
            if which == "carState":
                cs = msg.carState
                states.append((
                    t,
                    float(cs.vEgo),
                    float(cs.vEgoRaw),
                    float(cs.steeringAngleDeg),
                    float(cs.steeringAngleOffsetDeg),
                ))
            elif which == "vehicleParameters":
                vp = msg.vehicleParameters
                params_rows.append((
                    t,
                    float(vp.stiffnessFactor),
                    float(vp.steerRatio),
                    float(vp.roll),
                    float(vp.angleOffsetDeg),
                ))
            elif which == "modelV2":
                model_times.append(t)
            elif which == "carControl":
                cc = msg.carControl
                controls.append((
                    t,
                    float(cc.actuators.steeringAngleDeg),
                    bool(cc.enabled),
                    bool(cc.latActive),
                ))

        if not states or not params_rows or not model_times or not controls:
            continue

        state_times = [row[0] for row in states]
        params_times = [row[0] for row in params_rows]
        vm = VehicleModel(cp)
        controller_params = CarControllerParams(get_safety_CP())
        filters = {
            name: FirstOrderFilter(0.0, rc, 0.01, initialized=False)
            for name, rc in GENERIC_REFERENCE_RCS.items()
        }
        last_vmc = {variant: 0.0 for variant in variants}
        vmc_initialized = {variant: False for variant in variants}
        output: dict[str, list[tuple[float, bool, float, int, float, float, float, float, float]]] = {
            variant: [] for variant in variants
        }
        last_t: float | None = None

        for t, raw_angle, enabled, lat_active in controls:
            si = bisect.bisect_right(state_times, t) - 1
            pi = bisect.bisect_right(params_times, t) - 1
            mi = bisect.bisect_right(model_times, t) - 1
            if min(si, pi, mi) < 0:
                continue

            _, v_ego, v_ego_raw, measured_angle, carstate_offset = states[si]
            _, stiffness_factor, steer_ratio, roll, angle_offset = params_rows[pi]
            vm.update_params(max(stiffness_factor, 0.1), max(steer_ratio, 0.1))
            raw_curvature = -vm.calc_curvature(math.radians(raw_angle - angle_offset), v_ego, roll)
            active = enabled and lat_active
            dt = 0.01 if last_t is None else float(np.clip(t - last_t, 0.005, 0.03))

            reference: dict[str, tuple[float, float]] = {
                "baseline": (raw_angle, raw_curvature),
            }
            for name, filt in filters.items():
                if not active or not filt.initialized:
                    filt.x = raw_curvature
                    filt.initialized = True
                filt.update_dt(dt)
                filtered_curvature = filt.update(raw_curvature) if active else raw_curvature
                filtered_angle = math.degrees(
                    vm.get_steer_from_curvature(-filtered_curvature, v_ego, roll)
                ) + angle_offset
                reference[name] = (filtered_angle, filtered_curvature)

            measured_for_vmc = measured_angle + carstate_offset
            for name, (angle, curvature) in reference.items():
                if not vmc_initialized[name] or not active:
                    last_vmc[name] = measured_for_vmc
                    vmc_initialized[name] = True
                target = angle + carstate_offset
                last_vmc[name] = apply_steer_angle_limits_vm(
                    target,
                    last_vmc[name],
                    v_ego_raw,
                    measured_for_vmc,
                    active,
                    controller_params,
                    vm,
                )
                output[name].append((
                    t,
                    active,
                    v_ego_raw,
                    mi,
                    angle,
                    curvature,
                    curvature * v_ego * v_ego,
                    curvature * max(2.5, v_ego) ** 2,
                    last_vmc[name],
                ))
            last_t = t

        baseline = np.asarray(output["baseline"], dtype=float)
        if not len(baseline):
            continue

        for name in variants:
            values = np.asarray(output[name], dtype=float)
            active_idx = np.where(
                (values[:, 1] > 0.5) & (values[:, 2] >= 1.0) & (values[:, 2] < 9.0)
            )[0]
            pair_idx = np.asarray([
                i for i in active_idx
                if i > 0
                and values[i - 1, 1] > 0.5
                and values[i, 0] - values[i - 1, 0] < 0.03
            ], dtype=int)
            if not len(pair_idx):
                continue
            model_update_idx = np.asarray([
                i for i in pair_idx if int(values[i, 3]) != int(values[i - 1, 3])
            ], dtype=int)
            intersample_idx = np.asarray([
                i for i in pair_idx if int(values[i, 3]) == int(values[i - 1, 3])
            ], dtype=int)

            def signal_metrics(col: int) -> dict[str, float]:
                steps = values[pair_idx, col] - values[pair_idx - 1, col]
                second = np.diff(values[active_idx, col], 2)
                update_steps = (
                    values[model_update_idx, col] - values[model_update_idx - 1, col]
                    if len(model_update_idx) else np.asarray([], dtype=float)
                )
                intersample_steps = (
                    values[intersample_idx, col] - values[intersample_idx - 1, col]
                    if len(intersample_idx) else np.asarray([], dtype=float)
                )
                return {
                    "step_rms": float(np.sqrt(np.mean(steps * steps))),
                    "step_p95": float(np.percentile(np.abs(steps), 95)),
                    "second_difference_rms": float(np.sqrt(np.mean(second * second))) if len(second) else 0.0,
                    "model_update_step_rms": float(np.sqrt(np.mean(update_steps * update_steps))) if len(update_steps) else 0.0,
                    "intersample_step_rms": float(np.sqrt(np.mean(intersample_steps * intersample_steps))) if len(intersample_steps) else 0.0,
                }

            angle_dev = np.abs(values[active_idx, 4] - baseline[active_idx, 4])
            vmc_dev = np.abs(values[active_idx, 8] - baseline[active_idx, 8])
            per_variant[name].append({
                "frames": int(len(active_idx)),
                "angle": signal_metrics(4),
                "lateral_accel": signal_metrics(6),
                "model_lateral_action": signal_metrics(7),
                "vmc_angle": signal_metrics(8),
                "angle_mean_abs_deviation_deg": float(np.mean(angle_dev)),
                "angle_p95_abs_deviation_deg": float(np.percentile(angle_dev, 95)),
                "angle_max_abs_deviation_deg": float(np.max(angle_dev)),
                "vmc_mean_abs_deviation_deg": float(np.mean(vmc_dev)),
                "vmc_p95_abs_deviation_deg": float(np.percentile(vmc_dev, 95)),
                "vmc_max_abs_deviation_deg": float(np.max(vmc_dev)),
            })

    pooled: dict[str, Any] = {}
    for name, rows in per_variant.items():
        frames = sum(row["frames"] for row in rows)
        if not frames:
            continue

        def weighted_mean(key: str) -> float:
            return sum(row[key] * row["frames"] for row in rows) / frames

        def pooled_rms(group: str, key: str) -> float:
            return math.sqrt(sum(
                row[group][key] ** 2 * row["frames"] for row in rows
            ) / frames)

        pooled[name] = {
            "segments": len(rows),
            "frames": frames,
            "angle": {
                key: pooled_rms("angle", key)
                for key in ("step_rms", "second_difference_rms", "model_update_step_rms", "intersample_step_rms")
            },
            "lateral_accel": {
                key: pooled_rms("lateral_accel", key)
                for key in ("step_rms", "second_difference_rms", "model_update_step_rms", "intersample_step_rms")
            },
            "model_lateral_action": {
                key: pooled_rms("model_lateral_action", key)
                for key in ("step_rms", "second_difference_rms", "model_update_step_rms", "intersample_step_rms")
            },
            "vmc_angle": {
                key: pooled_rms("vmc_angle", key)
                for key in ("step_rms", "second_difference_rms", "model_update_step_rms", "intersample_step_rms")
            },
            "angle_mean_abs_deviation_deg": weighted_mean("angle_mean_abs_deviation_deg"),
            "angle_p95_abs_deviation_deg": weighted_mean("angle_p95_abs_deviation_deg"),
            "angle_max_abs_deviation_deg": max(row["angle_max_abs_deviation_deg"] for row in rows),
            "vmc_mean_abs_deviation_deg": weighted_mean("vmc_mean_abs_deviation_deg"),
            "vmc_p95_abs_deviation_deg": weighted_mean("vmc_p95_abs_deviation_deg"),
            "vmc_max_abs_deviation_deg": max(row["vmc_max_abs_deviation_deg"] for row in rows),
        }

    dt = 0.01
    for name, rc in GENERIC_REFERENCE_RCS.items():
        alpha = dt / (rc + dt)
        pooled[name]["filter"] = {
            "rc_seconds": rc,
            "alpha_at_100hz": alpha,
            "fraction_remaining_after_one_model_period": (1.0 - alpha) ** 5,
        }
    return pooled


ANGLE_RATE_CONTROLLER_TUNE = {
    "kp": 1.0,
    "ki": 0.0,
    "kd": 2.8,
}


def angle_rate_controller_diagnostics(LogReader, VehicleModel, root: Path) -> dict[str, Any]:
    """Identify the low-speed angle plant and score the rate-domain controller prototype."""

    sequences: list[np.ndarray] = []
    lateral_delays: list[float] = []
    for rel in CORPUS:
        msgs = list(LogReader(str(root / rel), only_union_types=True))
        if not msgs:
            continue
        t0 = msgs[0].logMonoTime
        cp = next(msg.carParams for msg in msgs if msg.which() == "carParams")
        vm = VehicleModel(cp)

        states: list[tuple[float, float, float, float]] = []
        params_rows: list[tuple[float, float, float, float, float]] = []
        controls: list[tuple[float, float, bool, bool]] = []
        outputs: list[tuple[float, float]] = []

        for msg in msgs:
            t = (msg.logMonoTime - t0) * 1e-9
            which = msg.which()
            if which == "carState":
                cs = msg.carState
                states.append((
                    t,
                    float(cs.vEgo),
                    float(cs.vEgoRaw),
                    float(cs.steeringAngleDeg + cs.steeringAngleOffsetDeg),
                ))
            elif which == "vehicleParameters":
                vp = msg.vehicleParameters
                params_rows.append((
                    t,
                    float(vp.stiffnessFactor),
                    float(vp.steerRatio),
                    float(vp.roll),
                    float(vp.angleOffsetDeg),
                ))
            elif which == "carControl":
                cc = msg.carControl
                controls.append((
                    t,
                    float(cc.actuators.steeringAngleDeg),
                    bool(cc.enabled),
                    bool(cc.latActive),
                ))
            elif which == "carOutput":
                outputs.append((t, float(msg.carOutput.actuatorsOutput.steeringAngleDeg)))
            elif which == "lateralDelay":
                lateral_delays.append(float(msg.lateralDelay.lateralDelay))

        if not states or not params_rows or not controls or not outputs:
            continue

        params_times = [row[0] for row in params_rows]
        control_times = [row[0] for row in controls]
        output_times = [row[0] for row in outputs]
        rows: list[tuple[float, float, float, float, float, bool]] = []

        for t, v_ego, v_ego_raw, measured_angle in states:
            pi = bisect.bisect_right(params_times, t) - 1
            ci = bisect.bisect_right(control_times, t) - 1
            oi = bisect.bisect_right(output_times, t) - 1
            if min(pi, ci, oi) < 0:
                continue

            _, stiffness_factor, steer_ratio, roll, angle_offset = params_rows[pi]
            vm.update_params(max(stiffness_factor, 0.1), max(steer_ratio, 0.1))
            measured_curvature = -vm.calc_curvature(
                math.radians(measured_angle - angle_offset), v_ego, roll
            )
            output_curvature = -vm.calc_curvature(
                math.radians(outputs[oi][1] - angle_offset), v_ego, roll
            )
            desired_curvature = -vm.calc_curvature(
                math.radians(controls[ci][1] - angle_offset), v_ego, roll
            )
            active = controls[ci][2] and controls[ci][3] and 1.0 <= v_ego_raw < 9.0
            rows.append((
                t,
                v_ego_raw,
                measured_curvature,
                output_curvature,
                desired_curvature,
                active,
            ))

        current: list[tuple[float, float, float, float, float, bool]] = []
        for row in rows:
            if row[5] and (not current or row[0] - current[-1][0] < 0.025):
                current.append(row)
            else:
                if len(current) >= 80:
                    sequences.append(np.asarray(current, dtype=float))
                current = []
        if len(current) >= 80:
            sequences.append(np.asarray(current, dtype=float))

    if not sequences:
        return {}

    # First-order ARX plant: y[k+1] = a*y[k] + b*u[k-d] + c.
    train = [seq for i, seq in enumerate(sequences) if i % 3 != 0]
    test = [seq for i, seq in enumerate(sequences) if i % 3 == 0]
    best_global: tuple[float, int, np.ndarray, int, int] | None = None
    for delay in range(31):
        x_rows: list[list[float]] = []
        y_rows: list[float] = []
        for seq in train:
            for k in range(delay, len(seq) - 1):
                x_rows.append([seq[k, 2], seq[k - delay, 3], 1.0])
                y_rows.append(seq[k + 1, 2])
        if not x_rows:
            continue
        x = np.asarray(x_rows)
        y = np.asarray(y_rows)
        coef = np.linalg.lstsq(x, y, rcond=None)[0]

        errors: list[float] = []
        for seq in test:
            for k in range(delay, len(seq) - 1):
                errors.append(
                    float(np.dot([seq[k, 2], seq[k - delay, 3], 1.0], coef) - seq[k + 1, 2])
                )
        if not errors:
            continue
        rmse = float(np.sqrt(np.mean(np.square(errors))))
        candidate = (rmse, delay, coef, len(y_rows), len(errors))
        if best_global is None or rmse < best_global[0]:
            best_global = candidate

    if best_global is None:
        return {}

    test_rmse, plant_delay, plant_coef, train_samples, test_samples = best_global
    plant_a, plant_b, plant_c = (float(x) for x in plant_coef)
    dc_gain = plant_b / (1.0 - plant_a)

    local_models: list[tuple[int, float, int, float, float, float, float]] = []
    for seq_i, seq in enumerate(sequences):
        best_local: tuple[float, int, float, float, float, float] | None = None
        for delay in range(31):
            x_rows = []
            y_rows = []
            for k in range(delay, len(seq) - 1):
                x_rows.append([seq[k, 2], seq[k - delay, 3], 1.0])
                y_rows.append(seq[k + 1, 2])
            if len(x_rows) < 60:
                continue
            x = np.asarray(x_rows)
            y = np.asarray(y_rows)
            coef = np.linalg.lstsq(x, y, rcond=None)[0]
            a, b, c = (float(v) for v in coef)
            gain = b / (1.0 - a) if abs(1.0 - a) > 1e-9 else math.inf
            if not (0.90 < a < 0.9999 and b > 0.0 and 0.2 < gain < 2.0):
                continue
            rmse = float(np.sqrt(np.mean(np.square(x @ coef - y))))
            candidate = (rmse, delay, a, b, c, gain)
            if best_local is None or rmse < best_local[0]:
                best_local = candidate
        if best_local is not None:
            local_models.append((seq_i, *best_local))

    dt = 0.01
    feedback_delay = float(np.median(lateral_delays)) if lateral_delays else 0.38

    def simulate_direct(seq: np.ndarray, model) -> tuple[np.ndarray, np.ndarray]:
        _, _, delay, a, b, c, _ = model
        ref = seq[:, 4]
        y = np.zeros(len(seq))
        y[0] = seq[0, 2]
        for k in range(len(seq) - 1):
            y[k + 1] = a * y[k] + b * ref[max(0, k - delay)] + c
        return y, ref.copy()

    def simulate_rc20(seq: np.ndarray, model) -> tuple[np.ndarray, np.ndarray]:
        _, _, delay, a, b, c, _ = model
        ref = seq[:, 4]
        y = np.zeros(len(seq))
        u = np.zeros(len(seq))
        y[0] = seq[0, 2]
        u[0] = ref[0]
        alpha = dt / (0.020 + dt)
        for k in range(len(seq) - 1):
            u[k] = ref[k] if k == 0 else alpha * ref[k] + (1.0 - alpha) * u[k - 1]
            y[k + 1] = a * y[k] + b * u[max(0, k - delay)] + c
        if len(seq) > 1:
            u[-1] = u[-2]
        return y, u

    def simulate_rate_controller(seq: np.ndarray, model) -> tuple[np.ndarray, np.ndarray]:
        _, _, delay, a, b, c, _ = model
        ref = seq[:, 4]
        y = np.zeros(len(seq))
        u = np.zeros(len(seq))
        y[0] = seq[0, 2]
        u[0] = y[0]
        previous_y = y[0]
        integral = 0.0
        kp = ANGLE_RATE_CONTROLLER_TUNE["kp"]
        ki = ANGLE_RATE_CONTROLLER_TUNE["ki"]
        kd = ANGLE_RATE_CONTROLLER_TUNE["kd"]
        for k in range(len(seq) - 1):
            error = ref[k] - y[k]
            rate_error = error / max(feedback_delay, dt)
            measured_rate = (y[k] - previous_y) / dt if k else 0.0
            previous_y = y[k]
            integral += ki * dt * rate_error
            rate_command = kp * rate_error - kd * measured_rate + integral
            u[k] = float(np.clip(
                (u[k - 1] if k else y[k]) + rate_command * dt,
                -0.2,
                0.2,
            ))
            y[k + 1] = a * y[k] + b * u[max(0, k - delay)] + c
        if len(seq) > 1:
            u[-1] = u[-2]
        return y, u

    def robust_metrics(simulator) -> dict[str, float]:
        response_ratios: list[float] = []
        step_rms: list[float] = []
        second_rms: list[float] = []
        for model in local_models:
            seq = sequences[model[0]]
            baseline_y, _ = simulate_direct(seq, model)
            candidate_y, candidate_u = simulator(seq, model)
            ref = seq[:, 4]
            start = 50
            baseline_error = float(np.sqrt(np.mean(np.square(baseline_y[start:] - ref[start:]))))
            candidate_error = float(np.sqrt(np.mean(np.square(candidate_y[start:] - ref[start:]))))
            if baseline_error > 0.0:
                response_ratios.append(candidate_error / baseline_error)
            step_rms.append(float(np.sqrt(np.mean(np.square(np.diff(candidate_u)[start:])))))
            second_rms.append(float(np.sqrt(np.mean(np.square(np.diff(candidate_u, 2)[start - 1:])))))
        return {
            "tracking_error_ratio_median": float(np.median(response_ratios)),
            "tracking_error_ratio_worst": float(np.max(response_ratios)),
            "command_step_rms_median": float(np.median(step_rms)),
            "command_step_rms_worst": float(np.max(step_rms)),
            "command_second_difference_rms_median": float(np.median(second_rms)),
            "command_second_difference_rms_worst": float(np.max(second_rms)),
        }

    def global_step_response(kind: str) -> dict[str, float]:
        samples = 900
        step_start = 100
        target = 0.02
        ref = np.zeros(samples)
        ref[step_start:] = target
        y = np.zeros(samples)
        u = np.zeros(samples)
        input_history = [0.0] * (plant_delay + 1)
        previous_y = 0.0
        integral = 0.0
        alpha = dt / (0.020 + dt)

        for k in range(samples - 1):
            if kind == "direct":
                u[k] = ref[k]
            elif kind == "rc20":
                u[k] = ref[k] if k == 0 else alpha * ref[k] + (1.0 - alpha) * u[k - 1]
            else:
                error = ref[k] - y[k]
                rate_error = error / max(feedback_delay, dt)
                measured_rate = (y[k] - previous_y) / dt if k else 0.0
                previous_y = y[k]
                integral += ANGLE_RATE_CONTROLLER_TUNE["ki"] * dt * rate_error
                rate_command = (
                    ANGLE_RATE_CONTROLLER_TUNE["kp"] * rate_error
                    - ANGLE_RATE_CONTROLLER_TUNE["kd"] * measured_rate
                    + integral
                )
                u[k] = float(np.clip(
                    (u[k - 1] if k else y[k]) + rate_command * dt,
                    -0.2,
                    0.2,
                ))
            input_history.append(u[k])
            y[k + 1] = (
                plant_a * y[k]
                + plant_b * input_history[-plant_delay - 1]
                + plant_c
            )

        if samples > 1:
            u[-1] = u[-2]
        baseline = float(np.mean(y[70:95]))
        final = float(np.mean(y[-100:]))
        amplitude = final - baseline

        def crossing_time(fraction: float) -> float | None:
            threshold = baseline + fraction * amplitude
            hits = np.where(y[step_start:] >= threshold)[0]
            return float(hits[0] * dt) if len(hits) else None

        overshoot = (float(np.max(y[step_start:])) - final) / abs(amplitude)
        return {
            "target_curvature": target,
            "t50_seconds": crossing_time(0.5),
            "t90_seconds": crossing_time(0.9),
            "overshoot_fraction": overshoot,
            "peak_command_to_target_ratio": float(np.max(u) / target),
            "command_second_difference_rms": float(np.sqrt(np.mean(np.square(np.diff(u, 2)[99:299])))),
        }

    return {
        "scope": {
            "sequences": len(sequences),
            "samples": int(sum(len(seq) for seq in sequences)),
            "local_models": len(local_models),
            "sample_period_seconds": dt,
            "feedback_delay_median_seconds": feedback_delay,
        },
        "identified_plant": {
            "form": "y[k+1] = a*y[k] + b*u[k-delay] + c",
            "delay_samples": plant_delay,
            "delay_seconds": plant_delay * dt,
            "a": plant_a,
            "b": plant_b,
            "c": plant_c,
            "dc_gain": dc_gain,
            "held_out_rmse_curvature": test_rmse,
            "train_samples": train_samples,
            "test_samples": test_samples,
        },
        "prototype": {
            "form": "u_dot = kp*(desired_curvature-actual_curvature)/lateral_delay - kd*actual_curvature_rate + ki*integral(rate_error)",
            **ANGLE_RATE_CONTROLLER_TUNE,
        },
        "global_step_response": {
            "direct": global_step_response("direct"),
            "rc20": global_step_response("rc20"),
            "rate_controller": global_step_response("rate"),
        },
        "local_model_robustness": {
            "rc20": robust_metrics(simulate_rc20),
            "rate_controller": robust_metrics(simulate_rate_controller),
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--log-root", default=DEFAULT_LOG_ROOT)
    parser.add_argument("--openpilot-root", default=DEFAULT_OPENPILOT_ROOT)
    parser.add_argument("--output", default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    (
        LogReader,
        get_curvature_from_plan,
        FirstOrderFilter,
        apply_steer_angle_limits_vm,
        get_safety_CP,
        CarControllerParams,
        VehicleModel,
    ) = load_stack(args.openpilot_root)

    log_root = Path(args.log_root).resolve()
    samples_by_file: list[list[Sample]] = []
    per_segment: dict[str, list[dict[str, Any]]] = {variant: [] for variant in VARIANTS}
    segment_rows: list[dict[str, Any]] = []

    for rel in CORPUS:
        path = log_root / rel
        samples = load_can_loop_samples(LogReader, path)
        samples_by_file.append(samples)

        values: dict[str, np.ndarray] = {}
        for variant in VARIANTS:
            sim = RequestSimulator(
                variant,
                FirstOrderFilter=FirstOrderFilter,
                apply_steer_angle_limits_vm=apply_steer_angle_limits_vm,
                get_safety_CP=get_safety_CP,
                CarControllerParams=CarControllerParams,
                VehicleModel=VehicleModel,
            )
            values[variant] = np.asarray([sim.step(sample) for sample in samples])

        baseline = values["baseline"]
        row: dict[str, Any] = {"path": rel, "variants": {}}
        for variant in VARIANTS:
            metrics = variant_metrics(samples, baseline, values[variant])
            if metrics is not None:
                per_segment[variant].append(metrics)
                row["variants"][variant] = metrics
        segment_rows.append(row)

    pooled = pool_metrics(per_segment)
    baseline_rms = pooled["baseline"]["step_rms_deg"]
    for variant in VARIANTS:
        pooled[variant]["step_rms_reduction_fraction"] = 1.0 - pooled[variant]["step_rms_deg"] / baseline_rms

    report = {
        "scope": {
            "log_root": str(log_root),
            "openpilot_root": str(Path(args.openpilot_root).resolve()),
            "corpus": list(CORPUS),
            "scan_dates": list(SCAN_DATES),
            "speed_range_mps": [1.0, 9.0],
            "request_angle_scale_deg_per_count": 1024 / 17870,
        },
        "request_update_structure": request_update_structure(samples_by_file),
        "root_layer_diagnostics": root_layer_diagnostics(LogReader, get_curvature_from_plan, log_root),
        "generic_reference_bakeoff": generic_reference_bakeoff(
            LogReader,
            FirstOrderFilter,
            apply_steer_angle_limits_vm,
            get_safety_CP,
            CarControllerParams,
            VehicleModel,
            log_root,
        ),
        "angle_rate_controller_diagnostics": angle_rate_controller_diagnostics(LogReader, VehicleModel, log_root),
        "pooled": pooled,
        "segments": segment_rows,
        "native_stock": stock_request_scan(LogReader, log_root),
    }

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps({
        "output": str(output),
        "corpus_segments": len(CORPUS),
        "pooled": pooled,
        "native_stock": report["native_stock"],
    }, indent=2))


if __name__ == "__main__":
    main()
