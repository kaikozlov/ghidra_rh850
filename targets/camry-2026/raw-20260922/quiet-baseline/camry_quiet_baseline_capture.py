#!/usr/bin/env python3
"""Capture an exact-Camry deep-sleep CAN baseline without transmitting CAN.

This tool is intended to run while the caller owns the cooperative direct-Panda
lease. It deliberately opens Panda with configure=False so connecting does not
reset CAN communications or rewrite speeds/modes. The only board-state change
is temporarily disabling Panda power-save so all receive transceivers/IRQs are
available. Safety must already be NOOUTPUT; the tool refuses to change it.

No CAN frame is ever submitted. USB heartbeats keep the existing Panda safety
state alive while the native pandad child is leased away.
"""

from __future__ import annotations

import argparse
import gzip
import json
import time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

from panda import Panda

NOOUTPUT_SAFETY_MODE = 19


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def health_snapshot(panda: Panda) -> dict[str, object]:
    return {
        "health": panda.health(),
        "can_health": [panda.can_health(i) for i in range(3)],
    }


def counter_deltas(before: dict[str, object], after: dict[str, object]) -> list[dict[str, int]]:
    fields = (
        "total_rx_cnt",
        "total_tx_cnt",
        "total_fwd_cnt",
        "total_error_cnt",
        "total_rx_lost_cnt",
        "total_tx_lost_cnt",
        "total_tx_checksum_error_cnt",
        "bus_off_cnt",
        "can_core_reset_count",
    )
    out: list[dict[str, int]] = []
    bstates = before["can_health"]
    astates = after["can_health"]
    assert isinstance(bstates, list) and isinstance(astates, list)
    for bus, (b, a) in enumerate(zip(bstates, astates, strict=True)):
        assert isinstance(b, dict) and isinstance(a, dict)
        row = {"controller": bus}
        row.update({field: int(a[field]) - int(b[field]) for field in fields})
        out.append(row)
    return out


def capture(duration: float, output: Path) -> dict[str, object]:
    serials = Panda.list()
    if len(serials) != 1:
        raise RuntimeError(f"expected exactly one Panda, found {serials}")

    panda = Panda(serials[0], cli=False, configure=False, disable_checks=False)
    power_save_restored = False
    try:
        initial = health_snapshot(panda)
        ih = initial["health"]
        assert isinstance(ih, dict)
        if bool(ih["ignition_line"]) or bool(ih["ignition_can"]):
            raise RuntimeError(f"vehicle is not in quiet ignition-off state: {ih}")
        if int(ih["safety_mode"]) not in (0, NOOUTPUT_SAFETY_MODE):
            raise RuntimeError(
                f"refusing unexpected Panda safety state; expected SILENT(0) or NOOUTPUT(19), got {ih['safety_mode']}"
            )

        # The native child may fall to SILENT during cooperative handoff once its
        # heartbeat stops. SILENT and NOOUTPUT both keep the intercept relay
        # closed; select NOOUTPUT so the observer remains ACK-capable if a
        # sleeping vehicle node begins transmitting. This submits no CAN data
        # frames.
        if int(ih["safety_mode"]) == 0:
            panda.set_safety_mode(NOOUTPUT_SAFETY_MODE, 0)
            time.sleep(0.02)

        # The stock offroad pandad policy intentionally puts Panda in power-save.
        # Disable only that receiver-side state so all CAN transceivers/IRQs can
        # observe a genuinely quiet vehicle.
        panda.set_power_save(False)
        time.sleep(0.05)
        enabled = health_snapshot(panda)
        eh = enabled["health"]
        assert isinstance(eh, dict)
        if bool(eh["power_save_enabled"]):
            raise RuntimeError("Panda power-save did not disable")
        if int(eh["safety_mode"]) != NOOUTPUT_SAFETY_MODE:
            raise RuntimeError(f"Panda safety changed unexpectedly after receiver wake: {eh}")

        start_ns = time.monotonic_ns()
        start_wall = utc_now()
        frames: list[dict[str, object]] = []
        heartbeat_deadline = 0.0
        while (time.monotonic_ns() - start_ns) / 1e9 < duration:
            now = time.monotonic()
            if now >= heartbeat_deadline:
                panda.send_heartbeat(False)
                heartbeat_deadline = now + 0.5
            batch = panda.can_recv() or []
            batch_ns = time.monotonic_ns()
            for address, data, raw_bus in batch:
                raw_bus_i = int(raw_bus)
                frames.append(
                    {
                        "t_ns": batch_ns - start_ns,
                        "address": int(address),
                        "raw_bus": raw_bus_i,
                        "bus": raw_bus_i & 0x7F,
                        "returned": bool(raw_bus_i & 0x80),
                        "data": bytes(data).hex(),
                    }
                )
            time.sleep(0.001)
        end_wall = utc_now()
        active_end = health_snapshot(panda)

        panda.set_power_save(True)
        power_save_restored = True
        time.sleep(0.05)
        restored = health_snapshot(panda)

        census = Counter((int(row["bus"]), int(row["address"]), len(bytes.fromhex(str(row["data"])))) for row in frames)
        result: dict[str, object] = {
            "schema": "camry-quiet-baseline-direct-panda-v1",
            "capture_method": (
                "cooperative direct-Panda lease; Panda(configure=False); SILENT/NOOUTPUT entry asserted; "
                "NOOUTPUT selected only if handoff heartbeat had fallen to SILENT, preserving closed relay and ACK capability; "
                "Panda power-save temporarily disabled to enable receive transceivers; can_recv only; "
                "USB heartbeat only; zero CAN data-frame submissions; no diagnostics"
            ),
            "duration_s": (time.monotonic_ns() - start_ns) / 1e9,
            "requested_duration_s": duration,
            "start_wall_utc": start_wall,
            "end_wall_utc": end_wall,
            "initial_power_save_snapshot": initial,
            "receiver_enabled_snapshot": enabled,
            "active_end_snapshot": active_end,
            "power_save_restored_snapshot": restored,
            "active_counter_deltas": counter_deltas(enabled, active_end),
            "frames": frames,
            "traffic_census": [
                {"bus": bus, "address": f"0x{address:03X}", "dlc": dlc, "count": count}
                for (bus, address, dlc), count in sorted(census.items())
            ],
            "frame_count": len(frames),
        }
        output.parent.mkdir(parents=True, exist_ok=True)
        payload = json.dumps(result, sort_keys=True, separators=(",", ":")).encode()
        with output.open("wb") as raw:
            with gzip.GzipFile(fileobj=raw, mode="wb", mtime=0) as gz:
                gz.write(payload)
        return result
    finally:
        if not power_save_restored:
            try:
                panda.set_power_save(True)
            except Exception:
                pass
        panda.close()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--duration", type=float, default=60.0)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = capture(args.duration, args.output)
    print(
        json.dumps(
            {
                "output": str(args.output),
                "duration_s": result["duration_s"],
                "frame_count": result["frame_count"],
                "traffic_census": result["traffic_census"],
                "active_counter_deltas": result["active_counter_deltas"],
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
