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
    from opendbc.car.common.filter_simple import FirstOrderFilter
    from opendbc.car.lateral import apply_steer_angle_limits_vm
    from opendbc.car.toyota.carcontroller import get_safety_CP
    from opendbc.car.toyota.values import CarControllerParams
    from opendbc.car.vehicle_model import VehicleModel
    return LogReader, FirstOrderFilter, apply_steer_angle_limits_vm, get_safety_CP, CarControllerParams, VehicleModel


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


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--log-root", default=DEFAULT_LOG_ROOT)
    parser.add_argument("--openpilot-root", default=DEFAULT_OPENPILOT_ROOT)
    parser.add_argument("--output", default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    (
        LogReader,
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
