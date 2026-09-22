#!/usr/bin/env python3
"""Passive key-proximity wake probe for the exact 2026 Camry.

Run only while holding the cooperative direct-Panda lease. The tool enables
Panda receive hardware, verifies a zero-traffic baseline, then arms. It sends no
CAN data frames and no diagnostics. A USB heartbeat only keeps Panda alive.
"""

from __future__ import annotations

import argparse
import gzip
import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path

from panda import Panda

NOOUTPUT = 19
SILENT = 0


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def snap(p: Panda) -> dict:
    return {"health": p.health(), "can_health": [p.can_health(i) for i in range(3)]}


def atomic_json(path: Path, obj: dict) -> None:
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n")
    os.replace(tmp, path)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", type=Path, required=True)
    ap.add_argument("--status", type=Path, required=True)
    ap.add_argument("--stop-file", type=Path, required=True)
    ap.add_argument("--baseline", type=float, default=5.0)
    ap.add_argument("--max-duration", type=float, default=600.0)
    ap.add_argument("--tail-after-first", type=float, default=30.0)
    args = ap.parse_args()

    args.status.unlink(missing_ok=True)
    args.stop_file.unlink(missing_ok=True)

    serials = Panda.list()
    if len(serials) != 1:
        raise RuntimeError(f"expected one Panda, got {serials}")
    p = Panda(serials[0], cli=False, configure=False, disable_checks=False)
    restored = False
    frames: list[dict] = []
    try:
        initial = snap(p)
        h = initial["health"]
        if h["ignition_line"] or h["ignition_can"]:
            raise RuntimeError("ignition is already active")
        if h["safety_mode"] not in (SILENT, NOOUTPUT):
            raise RuntimeError(f"unexpected safety mode {h['safety_mode']}")

        # During the cooperative handoff the native pandad child is gone, so its
        # heartbeat stops. Disable the board-side heartbeat watchdog while in a
        # non-car safety mode; normal pandad's next heartbeat re-enables it.
        p.set_heartbeat_disabled()
        if h["safety_mode"] == SILENT:
            p.set_safety_mode(NOOUTPUT, 0)
            time.sleep(0.02)

        p.set_power_save(False)
        time.sleep(0.05)
        enabled = snap(p)
        if enabled["health"]["power_save_enabled"]:
            raise RuntimeError("power-save did not disable")
        if enabled["health"]["safety_mode"] != NOOUTPUT:
            raise RuntimeError("NOOUTPUT not active")

        # Flush any USB-side buffered rows, then prove a quiet interval.
        p.can_recv()
        base_start_ns = time.monotonic_ns()
        baseline_frames: list[dict] = []
        while (time.monotonic_ns() - base_start_ns) / 1e9 < args.baseline:
            for a, d, b in p.can_recv() or []:
                baseline_frames.append({"address": int(a), "raw_bus": int(b), "data": bytes(d).hex()})
            time.sleep(0.001)
        if baseline_frames:
            atomic_json(args.status, {
                "state": "baseline_not_quiet",
                "wall_utc": utc_now(),
                "frame_count": len(baseline_frames),
                "sample": baseline_frames[:20],
            })
            raise RuntimeError(f"baseline was not quiet: {len(baseline_frames)} frames")

        armed_ns = time.monotonic_ns()
        armed_wall = utc_now()
        enabled_at_arm = snap(p)
        atomic_json(args.status, {
            "state": "armed",
            "armed_wall_utc": armed_wall,
            "baseline_s": args.baseline,
            "frame_count": 0,
            "first_frame": None,
        })
        print(f"ARMED {armed_wall}", flush=True)

        first_frame_ns: int | None = None
        last_status = 0.0
        reason = "max_duration"
        while True:
            now_ns = time.monotonic_ns()
            elapsed = (now_ns - armed_ns) / 1e9
            if args.stop_file.exists():
                reason = "operator_stop"
                break
            if elapsed >= args.max_duration:
                break
            if first_frame_ns is not None and (now_ns - first_frame_ns) / 1e9 >= args.tail_after_first:
                reason = "first_frame_plus_tail"
                break

            now = time.monotonic()

            for address, data, raw_bus in p.can_recv() or []:
                rx_ns = time.monotonic_ns()
                if first_frame_ns is None:
                    first_frame_ns = rx_ns
                rb = int(raw_bus)
                frames.append({
                    "t_ns": rx_ns - armed_ns,
                    "address": int(address),
                    "raw_bus": rb,
                    "bus": rb & 0x7F,
                    "returned": bool(rb & 0x80),
                    "data": bytes(data).hex(),
                })

            if now - last_status >= 0.25:
                first = frames[0] if frames else None
                atomic_json(args.status, {
                    "state": "capturing",
                    "armed_wall_utc": armed_wall,
                    "elapsed_s": elapsed,
                    "frame_count": len(frames),
                    "first_frame": first,
                })
                last_status = now
            time.sleep(0.001)

        end_wall = utc_now()
        active_end = snap(p)
        p.set_power_save(True)
        restored = True
        time.sleep(0.05)
        restored_snap = snap(p)

        out = {
            "schema": "camry-key-proximity-probe-v1",
            "armed_wall_utc": armed_wall,
            "end_wall_utc": end_wall,
            "baseline_s": args.baseline,
            "end_reason": reason,
            "frames": frames,
            "frame_count": len(frames),
            "first_frame": frames[0] if frames else None,
            "initial": initial,
            "receiver_enabled_at_arm": enabled_at_arm,
            "active_end": active_end,
            "power_save_restored": restored_snap,
            "capture_method": "cooperative direct-Panda lease; configure=False; board heartbeat watchdog disabled only while leased; NOOUTPUT; power-save disabled for RX; can_recv only; zero CAN data submissions; no diagnostics",
        }
        args.output.parent.mkdir(parents=True, exist_ok=True)
        raw = json.dumps(out, sort_keys=True, separators=(",", ":")).encode()
        with args.output.open("wb") as fh:
            with gzip.GzipFile(fileobj=fh, mode="wb", mtime=0) as gz:
                gz.write(raw)
        atomic_json(args.status, {
            "state": "complete",
            "armed_wall_utc": armed_wall,
            "end_wall_utc": end_wall,
            "end_reason": reason,
            "frame_count": len(frames),
            "first_frame": frames[0] if frames else None,
            "output": str(args.output),
        })
        return 0
    finally:
        if not restored:
            try:
                p.set_power_save(True)
            except Exception:
                pass
        p.close()


if __name__ == "__main__":
    raise SystemExit(main())
